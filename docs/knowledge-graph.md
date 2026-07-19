# LogicFlow Guardian — Knowledge Graph Builder

**Phase 9B implementation.** Provides a modular, high-performance service to ingest the normalized Parser Intermediate Representation (IR) into a Neo4j Graph Database.

---

## Graph Schema Reference

The knowledge graph represents the structural hierarchy and code relationships of analyzed repositories.

### Node Labels

| Label | Description | Unique Key | Properties |
|---|---|---|---|
| `Repository` | The root project container node. Unique per analysis. | `repo_id` | `name`, `path`, `total_files`, `supported_files`, `analysis_id` |
| `Directory` | Folders in the repository structure. | `dir_id` | `name`, `relative_path`, `analysis_id` |
| `File` | Individual source code files (JS, TS, Python). | `file_id` | `name`, `relative_path`, `file_type`, `language`, `size_bytes`, `analysis_id` |
| `Class` | Class definitions. Can also have role labels. | `class_id` | `name`, `bases`, `extends`, `decorators`, `start_line`, `end_line`, `analysis_id`, `file_id` |
| `Controller` | Sub-label on `Class` representing HTTP routing logic. | `class_id` | Inherited from Class |
| `Service` | Sub-label on `Class` representing business/logic handlers. | `class_id` | Inherited from Class |
| `Model` | Sub-label on `Class` representing data transfer objects or database tables. | `class_id` | Inherited from Class |
| `Function` | Standalone function declarations. | `func_id` | `name`, `params`, `type`, `is_async`, `start_line`, `end_line`, `analysis_id`, `file_id` |
| `Method` | Functions declared inside classes. | `method_id` | `name`, `params`, `decorators`, `is_async`, `start_line`, `end_line`, `analysis_id`, `class_id` |
| `Route` | Web service endpoints mapping path + verb to handlers. | `route_id` | `path`, `http_method`, `handler`, `line`, `analysis_id`, `file_id` |
| `Middleware` | Express or FastAPI application-level middleware hooks. | `middleware_id` | `object`, `line`, `analysis_id`, `file_id` |
| `Import` | Declarations of dependency references. | `import_id` | `type`, `module`, `name`, `alias`, `line`, `analysis_id` |
| `Export` | Public symbols made available for reuse. | `export_id` | `type`, `name`, `line`, `analysis_id` |

### Relationships

| Name | Source Label | Target Label | Description | Properties |
|---|---|---|---|---|
| `CONTAINS` | `Repository` | `Directory` | Repository contains root directories | None |
| `CONTAINS` | `Directory` | `Directory` | Directory contains subdirectories | None |
| `CONTAINS` | `Directory` | `File` | Directory contains source files | None |
| `OWNS` | `Repository` | `File` | Direct ownership shortcut edge | None |
| `DECLARES` | `File` | `Class` | File contains class definition | None |
| `DECLARES` | `File` | `Function` | File contains standalone function | None |
| `DECLARES` | `Class` | `Method` | Class defines member method | None |
| `IMPORTS` | `File` | `Import` | File imports external/internal module | `line` |
| `EXPORTS` | `File` | `Export` | File exports a public symbol | None |
| `EXTENDS` | `Class` | `Class` | Class inherits from another class (even unresolved external classes) | `base_name` |
| `HAS_ROUTE` | `File` / `Class` | `Route` | Code defines web service route | None |
| `PROTECTED_BY`| `Route` | `Middleware` | Endpoint route is passed through middleware (future) | None |

---

## Services & Architecture

The knowledge graph ingestion process runs inside `ms2-agent` sequentially after the Parsing stage:

```
[Parser IR]
    │
    ▼
[IRNormalizer]  (graphrag/normalizer.py)
    │  - Normalizes IDs via: "{analysis_id}::{label}::{name}"
    │  - Runs role heuristics to classify Controllers, Services, Models
    │  - Generates flat lists of node and relationship dictionaries
    │
    ▼
[GraphBuilder]  (graphrag/graph_builder.py)
    │  - Runs Neo4j schema creation (Indexes & Unique constraints)
    │  - Dispatches batch MERGE calls to Neo4j
    │
    ▼
[Neo4j Database]
```

### Constraints & Indexes Setup

The graph builder initializes unique constraints to prevent entity collisions (especially useful across multiple analysis runs):

```cypher
CREATE CONSTRAINT repo_id IF NOT EXISTS FOR (n:Repository) REQUIRE n.repo_id IS UNIQUE;
CREATE CONSTRAINT file_id IF NOT EXISTS FOR (n:File) REQUIRE n.file_id IS UNIQUE;
CREATE CONSTRAINT dir_id IF NOT EXISTS FOR (n:Directory) REQUIRE n.dir_id IS UNIQUE;
CREATE CONSTRAINT class_id IF NOT EXISTS FOR (n:Class) REQUIRE n.class_id IS UNIQUE;
CREATE CONSTRAINT func_id IF NOT EXISTS FOR (n:Function) REQUIRE n.func_id IS UNIQUE;
CREATE CONSTRAINT method_id IF NOT EXISTS FOR (n:Method) REQUIRE n.method_id IS UNIQUE;
CREATE CONSTRAINT route_id IF NOT EXISTS FOR (n:Route) REQUIRE n.route_id IS UNIQUE;
```

---

## Key Cypher Queries

### Node Ingestion (Batching UNWIND)

Nodes are pushed into Neo4j in batches of 500 nodes per transaction for high memory efficiency. Example Cypher for Files:

```cypher
UNWIND $rows AS row
MERGE (f:File {file_id: row.file_id})
SET f.relative_path = row.relative_path,
    f.name          = row.name,
    f.file_type     = row.file_type,
    f.language      = row.language,
    f.size_bytes    = row.size_bytes,
    f.analysis_id   = row.analysis_id
```

### Relationship Ingestion (Indexed Matches)

Relationships match their endpoint nodes via unique keys and merge the relationship.

```cypher
UNWIND $rows AS row
MATCH (a:File {file_id: row.from_id})
MATCH (b:Class {class_id: row.to_id})
MERGE (a)-[r:DECLARES]->(b)
SET r += row.props
```

For inherits/extends relations where the base class may be an external library:

```cypher
UNWIND $rows AS row
MATCH (a:Class {class_id: row.from_id})
MERGE (b:Class {class_id: row.to_id})
ON CREATE SET b.name = row.props.base_name,
              b.is_unresolved = true,
              b.analysis_id = $analysis_id
MERGE (a)-[r:EXTENDS]->(b)
SET r += row.props
```

### Graph Validation Query

To confirm a successful import, the builder issues check queries:

```cypher
MATCH (n {analysis_id: $analysis_id})-[r]->()
RETURN count(r) AS cnt
```

---

## Integration with Repository Intake Pipeline

In `repository_intake_service.py`, after the `RepositoryParserEngine` output is written to disk, the graph is built synchronously:

```python
# ----------------------------------------------------------------
# STAGE: Knowledge Graph Construction
# ----------------------------------------------------------------
print("[INFO] Knowledge graph construction started...")
builder = GraphBuilder()
report = builder.build_graph(ir, repo_name)
if not report.get("success"):
    raise ValueError("Knowledge Graph validation failed: Repository node was not created.")
print(f"[INFO] Knowledge graph construction completed: {report}")
```
