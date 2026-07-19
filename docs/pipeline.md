# LogicFlow Guardian — Orchestration & Analysis Pipeline Documentation

This document describes the orchestration of the analysis pipeline via **LangGraph**, details of each stage (Intake, Parser, Neo4j Graph Builder), and the flow of validation.

---

## Pipeline Orchestration

The pipeline is orchestrated as a directed execution graph using **LangGraph**. The workflow utilizes an execution-level context object `AnalysisState` to carry configuration, outputs, and status information from node to node.

### The AnalysisState Structure

```python
class AnalysisState(TypedDict, total=False):
    analysis_id: int               # Unique database run identifier
    project_id: int                # Project identifier from MS1
    payload: Dict[str, Any]        # Request details (repoUrl, branch, etc.)
    repository_path: str           # Local absolute path to the workspace
    repository_name: str           # Slugified repository name
    language: str                  # Detected programming language
    framework: str                 # Detected web framework
    status: str                    # Current status (CLONING, VALIDATING, GRAPH_BUILT, COMPLETED, FAILED)
    errors: List[str]              # Logs of any exceptions encountered
    metadata: Dict[str, Any]       # Sub-metadata metrics (file count, nodes count)
```

---

## Pipeline Stages

### 1. Repository Intake (`RepositoryIntakeNode`)
- **Responsibility**: Allocates workspace, fetches the target repository, and runs checks.
- **Workflow**:
  1. Checks if the `agent_run` record for `analysis_id` exists in the local database. If not, it inserts one. If yes, it resets it to allow idempotent re-runs.
  2. Submits webhook call back to MS1: `CLONING`.
  3. Checks if the workspace directory (`workspace/analysis-{id}`) exists. If not, creates the folder and invokes `git clone --depth 1`.
  4. Submits webhook call back to MS1: `VALIDATING`.
  5. Performs sanity checks (verifies `.git` presence, files are readable, non-empty).
  6. Inspects project root manifest files (e.g. `package.json`, `requirements.txt`) to extract primary programming language and framework metadata.
  7. Computes total repository size in bytes.
  8. Updates the local `agent_run` table and submits webhook to MS1: `READY_FOR_PARSING` with final metadata.
- **State Output**: Sets `repository_path`, `repository_name`, `language`, `framework`, `status="READY_FOR_PARSING"`.

### 2. Source Code Parser (`RepositoryParserNode`)
- **Responsibility**: Recursively scans files, runs AST analyses, and exports inventory metrics.
- **Workflow**:
  1. Checks state status; skips execution if status is `FAILED`.
  2. Recursively scans the workspace, ignoring blacklisted directories (`node_modules`, `.git`, `dist`, `build`, etc.) and binaries.
  3. Identifies supported source files (`.py`, `.js`, `.ts`, `.jsx`, `.tsx`).
  4. Parses Python files using Python's built-in `ast` module to extract classes, functions, member methods, FastAPI/Flask route decorators, imports, and decorators.
  5. Parses JavaScript/TypeScript files using a multi-pass regular expression parser to extract ES imports, CommonJS requirements, exports, classes, arrow functions, Express routes, and application middleware.
  6. Compiles a single normalized Intermediate Representation (IR) JSON document.
  7. Serializes the IR to `workspace/analysis-{id}/parser_output.json`.
- **State Output**: Sets `status="PARSED"`, sets `metadata.parser_supported_files`.

### 3. Knowledge Graph Builder (`KnowledgeGraphNode`)
- **Responsibility**: Resolves parsed elements into semantic graph models and loads them to Neo4j.
- **Workflow**:
  1. Checks state status; skips execution if status is `FAILED`.
  2. Parses the written `parser_output.json` file back into an IR object.
  3. Normalizes all IDs to prevent cross-run database collisions (`{analysis_id}::{label}::{name}`).
  4. Creates Neo4j uniqueness constraints and indexes if not present.
  5. Upserts node records (`Repository`, `Directory`, `File`, `Class`, `Function`, `Method`, `Route`, `Middleware`, `Import`, `Export`) in transactions of 500 records at a time using `UNWIND ... MERGE`.
  6. Builds dependency edges (`CONTAINS`, `DECLARES`, `IMPORTS`, `EXPORTS`, `EXTENDS`, `HAS_ROUTE`, `OWNS`) to build a complete semantic graph.
  7. Issues validation queries to verify that the Repository root node exists and counts the total ingested nodes and relationships.
- **State Output**: Sets `status="GRAPH_BUILT"`, sets `metadata.graph_nodes` and `metadata.graph_relationships`.

### 4. Future Pass-through Nodes
- The pipeline defines placeholder nodes (`PlannerNode`, `ExecutionNode`, `ReflectionNode`, `ReportNode`) in sequence.
- Currently, these print verification trace logs and pass state through unchanged.
- On final completion, the handler updates the local database state to `COMPLETED` and sends the final webhook notify to MS1.

---

## Pipeline Validation Flow

```
   [Run Intake Node]
           │
           ├─► Success: Go to Parser Node
           └─► Exception: Set status to FAILED, record errors, send Webhook, halt
                   │
                   ▼
           [Run Parser Node]
                   │
                   ├─► Success: Go to Knowledge Graph Node
                   └─► Exception: Set status to FAILED, record errors, send Webhook, halt
                           │
                           ▼
                   [Run Knowledge Graph Node]
                           │
                           ├─► Verify Repository Node exists in Neo4j
                           ├─► Success: Go to Planner Node
                           └─► Exception: Set status to FAILED, record errors, send Webhook, halt
                                   │
                                   ▼
                           [Run Placeholder Nodes]
                                   │
                                   ▼
                           [Update DB to COMPLETED]
                           [Send Webhook callback to MS1]
```
