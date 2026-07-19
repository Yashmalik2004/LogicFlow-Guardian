# LogicFlow Guardian - Current System Workflows

This document provides a technical overview of the system workflows as they are actually implemented in the codebase. It serves as a guide for developers to understand the current architecture, data flows, and active features.

---

## 1. Overall System Architecture & Request Flow

The system consists of three main components:
1. **Frontend (React + Vite)**: Handles user authentication UI and project management. Currently, it has no user interface or service methods for running or viewing analyses.
2. **MS1 Core API (Express.js + TypeScript)**: Exposes APIs for authentication and project management, handles the task queue (BullMQ), and manages business state in PostgreSQL.
3. **MS2 Agent Service (FastAPI + Python)**: Exposes internal APIs for executing the repository intake pipeline (cloning, validation, metadata extraction) and manages local execution state.

### Overall Workflow Diagram
```
  [Frontend (React/Vite)]
             │
             │ (HTTP REST: /api/auth/*, /api/projects/*)
             ▼
      [MS1 (Express.js)] ◄─── (Direct PostgreSQL updates) ──────┐
             │                                                  │
             │ (Enqueues Job)                                   │
             ▼                                                  │
       [Redis/BullMQ]                                           │
             │                                                  │
             │ (Worker Consumes)                                │
             ▼                                                  │
      [Analysis Worker]                                         │
             │                                                  │
             │ (POST /internal/analysis/start)                  │
             ▼                                                  │
       [MS2 (FastAPI)]                                          │
             │                                                  │
             │ (FastAPI BackgroundTasks)                        │
             ├──────────────────────────────────────────────────┤
             ▼                                                  ▼
     [AgentRun (MS2 DB)]                             [MS1 Webhook Endpoint]
   - Create AgentRun record                     (POST /internal/webhook/analysis-status)
   - Update AgentRun state
   - Save local repository metadata
```

---

## 2. Authentication Flow

Authentication is managed entirely by MS1 using JWT tokens and standard hashing.

### Registration Workflow
```
[Frontend (UI)] ── POST /api/auth/register ──► [AuthController.register]
                                                        │
                                                        ▼
                                             [AuthService.registerUser]
                                                        │
                                                        ├─► UserModel.findByEmail (Check duplicate)
                                                        ├─► Hash password via bcrypt (10 rounds)
                                                        ▼
[Frontend (UI)] ◄── 201 Created (userId) ─────── [UserModel.create]
```

- **Endpoints & Files Involved**:
  - `POST /api/auth/register` (Public)
  - **Routes**: [auth.routes.ts](file:///c:/Users/YASH/Desktop/LogicFlow-Guardian/ms1-core-api/src/routes/auth.routes.ts)
  - **Controller**: `AuthController.register` in [auth.controller.ts](file:///c:/Users/YASH/Desktop/LogicFlow-Guardian/ms1-core-api/src/controllers/auth.controller.ts)
  - **Service**: `AuthService.registerUser` in [auth.service.ts](file:///c:/Users/YASH/Desktop/LogicFlow-Guardian/ms1-core-api/src/services/auth.service.ts)
  - **Model**: `UserModel.create` in [user.model.ts](file:///c:/Users/YASH/Desktop/LogicFlow-Guardian/ms1-core-api/src/models/user.model.ts)

### Login Workflow
```
[Frontend (UI)] ── POST /api/auth/login ──► [AuthController.login]
                                                     │
                                                     ▼
                                            [AuthService.loginUser]
                                                     │
                                                     ├─► UserModel.findByEmail
                                                     ├─► Compare password via bcrypt.compare
                                                     ├─► Sign JWT (expires in 24h)
                                                     ▼
[Frontend (UI)] ◄── 200 OK (token, user metadata) ───┘
```

- **Endpoints & Files Involved**:
  - `POST /api/auth/login` (Public)
  - **Routes**: [auth.routes.ts](file:///c:/Users/YASH/Desktop/LogicFlow-Guardian/ms1-core-api/src/routes/auth.routes.ts)
  - **Controller**: `AuthController.login` in [auth.controller.ts](file:///c:/Users/YASH/Desktop/LogicFlow-Guardian/ms1-core-api/src/controllers/auth.controller.ts)
  - **Service**: `AuthService.loginUser` in [auth.service.ts](file:///c:/Users/YASH/Desktop/LogicFlow-Guardian/ms1-core-api/src/services/auth.service.ts)

### Token Verification
- **Middleware**: `authMiddleware` in [auth.middleware.ts](file:///c:/Users/YASH/Desktop/LogicFlow-Guardian/ms1-core-api/src/middleware/auth.middleware.ts)
- **Logic**: Intercepts requests, extracts JWT from the `Authorization` header (`Bearer <token>` or raw `<token>`), verifies it using `env.JWT_SECRET`, and attaches `{ userId, name, email }` to the Express request object (`req.user`).

---

## 3. Project Creation Flow

Allows users to define target codebases for analysis.

### Project Creation Workflow
```
[Frontend (Dashboard)] ── POST /api/projects ──► [ProjectController.createProject]
                                                            │
                                                            ▼
                                                [ProjectService.createProject]
                                                            │
                                                            ▼
                                                  [ProjectModel.create]
                                                            │
                                                            ▼
                                                 INSERT INTO "Project"
                                                            │
[Frontend (Dashboard)] ◄── 201 Created (projectId) ─────────┘
```

- **Endpoints & Files Involved**:
  - `POST /api/projects` (Requires JWT)
  - **Routes**: [project.routes.ts](file:///c:/Users/YASH/Desktop/LogicFlow-Guardian/ms1-core-api/src/routes/project.routes.ts)
  - **Controller**: `ProjectController.createProject` in [project.controller.ts](file:///c:/Users/YASH/Desktop/LogicFlow-Guardian/ms1-core-api/src/controllers/project.controller.ts)
  - **Service**: `ProjectService.createProject` in [project.service.ts](file:///c:/Users/YASH/Desktop/LogicFlow-Guardian/ms1-core-api/src/services/project.service.ts)
  - **Model**: `ProjectModel.create` in [project.model.ts](file:///c:/Users/YASH/Desktop/LogicFlow-Guardian/ms1-core-api/src/models/project.model.ts)

---

## 4. Analysis Creation & Job Queue Flow

Starts an analysis pipeline. (Note: Currently triggered via REST API endpoints directly, as no UI integration is implemented for starting analyses).

### Analysis Pipeline Workflow
```
[Client] ── POST /api/analysis/start ──► [AnalysisController.startAnalysis]
                                                      │
                                                      ▼
                                           [AnalysisService.startAnalysis]
                                                      │
                                                      ├─► ProjectModel.findById (verify owner)
                                                      ├─► AnalysisModel.create (inserts status 'QUEUED')
                                                      │
                                                      ▼
                                                [BullMQ Queue]
                                                      │
                            ┌─────────────────────────┴────────────────────────┐
                            ▼ (Success)                                        ▼ (Fail)
                  Set bull_job_id in DB                              Update status → 'FAILED'
                            │                                                  │
[Client] ◄── 201 Created (analysisId, status)                                  ▼
                                                                     Return status 500 / 503
```

- **Endpoints & Files Involved**:
  - `POST /api/analysis/start` (Requires JWT)
  - **Routes**: [analysis.routes.ts](file:///c:/Users/YASH/Desktop/LogicFlow-Guardian/ms1-core-api/src/routes/analysis.routes.ts)
  - **Controller**: `AnalysisController.startAnalysis` in [analysis.controller.ts](file:///c:/Users/YASH/Desktop/LogicFlow-Guardian/ms1-core-api/src/controllers/analysis.controller.ts)
  - **Service**: `AnalysisService.startAnalysis` in [analysis.service.ts](file:///c:/Users/YASH/Desktop/LogicFlow-Guardian/ms1-core-api/src/services/analysis.service.ts)
  - **Model**: `AnalysisModel` in [analysis.model.ts](file:///c:/Users/YASH/Desktop/LogicFlow-Guardian/ms1-core-api/src/models/analysis.model.ts)
- **Logic**:
  1. Validates request body for `projectId`.
  2. Verifies project exists and belongs to the user.
  3. Creates an `"Analysis"` record with status `'QUEUED'` in MS1's PostgreSQL database.
  4. Enqueues a job in `AnalysisQueue` containing the full project data payload:
     ```json
     {
       "analysisId": 5001,
       "projectId": 101,
       "userId": 1,
       "repoUrl": "https://github.com/...",
       "repoName": "repo",
       "branch": "main",
       "repositoryType": "github"
     }
     ```
  5. Stores the BullMQ job ID in the database and returns a success response. Upon failure, sets the status in PostgreSQL to `'FAILED'`.

---

## 5. BullMQ & Worker Architecture

The background job system is hosted entirely in MS1 and communicates asynchronously with MS2.

```
          [AnalysisQueue (Redis)]
                     │
                     ▼ (concurrency: 5)
          [AnalysisWorker]
                     │
                     ▼
          Update status → 'PROCESSING'
          Set started_at = current time
                     │
                     ▼
          [dispatchAnalysisToMs2]
                     │
                     ▼ (HTTP POST /internal/analysis/start)
                     │
         ┌───────────┴───────────┐
         ▼ (MS2 ACK)             ▼ (MS2 Fail / Timeout)
Update status → 'DISPATCHED'   Update status → 'FAILED'
```

- **Queue Location**: Located **before** MS2 (inside MS1, utilizing a local/remote Redis store). MS2 has no access to Redis or the BullMQ instance.
  - **Queue Name**: `AnalysisQueue`
  - **Configuration**: [queue.ts](file:///c:/Users/YASH/Desktop/LogicFlow-Guardian/ms1-core-api/src/config/queue.ts)
- **Producer**: `AnalysisService` (MS1 Core API) enqueues jobs.
- **Consumer**: `AnalysisWorker` (MS1 Core API background process).
  - **Worker Source**: [analysis.worker.ts](file:///c:/Users/YASH/Desktop/LogicFlow-Guardian/ms1-core-api/src/workers/analysis.worker.ts)
  - Started on server initialization in [server.ts](file:///c:/Users/YASH/Desktop/LogicFlow-Guardian/ms1-core-api/src/server.ts).
  - Concurrency is configured to `5`.
- **Inter-service Dispatcher**: `dispatchAnalysisToMs2` in [dispatch.service.ts](file:///c:/Users/YASH/Desktop/LogicFlow-Guardian/ms1-core-api/src/services/dispatch.service.ts).
  - Sends a POST request to MS2 (`/internal/analysis/start`).
  - Upon successful dispatch (MS2 response `{ accepted: true }`), updates PostgreSQL status of the analysis to `'DISPATCHED'`. Upon failure, updates PostgreSQL status to `'FAILED'`.

---

## 6. Repository Intake Pipeline & Webhook Callback Flow (MS2)

When MS2 receives an analysis job, it initiates the repository intake pipeline in a Python background thread and reports state transitions back to MS1 via HTTP webhooks.

```
[MS1 Worker (dispatchService)] ── POST /internal/analysis/start ──► [MS2 (FastAPI internal router)]
                                                                               │
                                                                               ├─► background_tasks.add_task(intake)
                                                                               ▼
[MS1 Worker (dispatchService)] ◄── HTTP 200 { accepted: true } ────────────────┘
```

- **Endpoint**: `/internal/analysis/start`
- **Route File**: [internal.py](file:///c:/Users/YASH/Desktop/LogicFlow-Guardian/ms2-agent/app/routers/internal.py)
- **Intake Pipeline Service**: `repository_intake_service.py` in [repository_intake_service.py](file:///c:/Users/YASH/Desktop/LogicFlow-Guardian/ms2-agent/app/services/repository_intake_service.py)
- **Execution Logic**:
  1. FastAPI receives `AnalysisStartRequest`, starts `repository_intake_service.run(...)` as a `BackgroundTasks` task, and immediately returns a response with `accepted=True` to MS1.
  2. In the background thread, the service performs the following synchronous pipeline stages:
     - **Create AgentRun**: Inserts a new execution record inside MS2's separate database with status `'RECEIVED'`.
     - **Cloning Webhook**: Sends a webhook POST request back to MS1 `/internal/webhook/analysis-status` with `status="CLONING"`. MS1 updates the `"Analysis"` table status.
     - **Create workspace**: Resolves `env.WORKSPACE_ROOT` and creates an isolated directory `analysis-{analysisId}` via [workspace_service.py](file:///c:/Users/YASH/Desktop/LogicFlow-Guardian/ms2-agent/app/services/workspace_service.py).
     - **Git clone**: Executes a shell subprocess `git clone --depth 1 <repo_url> <workspace_path>`.
     - **Validating Webhook**: Sends a webhook POST request to MS1 with `status="VALIDATING"`. MS1 updates the `"Analysis"` table status.
     - **Validate repository**: Checks that the clone directory exists, contains a `.git` metadata folder, contains non-git files, and is readable.
     - **Language/Framework detection**: Calls `detect_language_and_framework` in [repository_discovery.py](file:///c:/Users/YASH/Desktop/LogicFlow-Guardian/ms2-agent/parser/repository_discovery.py). This is a **metadata-only detection** inspecting root project files (e.g. `package.json`, `requirements.txt`, `pom.xml`, etc.). Source code files are *never* read or parsed.
     - **Compute repository size**: Traverses the directory structure and computes total size in bytes.
     - **Persist metadata (MS2)**: Updates MS2's own database `agent_run` table record with local repository path, size, language, and framework metadata.
     - **Ready Webhook**: Sends a webhook POST request to MS1 with `status="READY_FOR_PARSING"` and includes the metadata fields. MS1 updates the `"Analysis"` table status and saves the metadata.
     - **Subsequent Stages**: Skips all parser, knowledge graph builder, AI reasoning (LangGraph), or reporting stages.
  3. If any exception is thrown, the handler updates the local `agent_run` record status to `'FAILED'` and sends a webhook POST to MS1 with `status="FAILED"` and the error details.

---

## 7. Database Ownership & Schema Details

Under the Database per Service architecture, the services own separate PostgreSQL databases:

### MS1 PostgreSQL Database
- **`"User"`**: Stores registered users.
- **`"Project"`**: Stores project metadata owned by users.
- **`"Analysis"`**: Stores the execution logs status, queue details, and final repository metadata sent from MS2 via webhooks.

### MS2 PostgreSQL Database
- **`agent_run`**: Stores execution states, workspace directories, language/framework detection results, and error details for trace logging. MS2 never reads or writes to MS1 tables.

### Migration & Initialization Process
- **MS1**: Managed via application-specific schema setups.
- **MS2**: Uses a raw SQL migration script located at `app/config/migrations/001_create_agent_run.sql`. It is applied against the database specified in `MS2_DATABASE_URL` (connecting to `postgres_ms2` database).
- **Auto-Initialization**: When MS2 launches, the system runs startup connection verification and executes `Base.metadata.create_all` using SQLAlchemy ORM to verify or initialize the `agent_run` schema automatically.

---

## 8. Technology/Infrastructure Details

- **Redis**: Used by MS1 via `ioredis` to back the BullMQ job queue. MS2 does not connect to or utilize Redis.
- **WebSockets**: **None**. There is no WebSocket server or client implementation in the codebase.
- **Webhooks**: **Yes**. Webhooks are now fully implemented for status communication from MS2 to MS1. MS1 validates the request with a shared webhook secret header (`X-Webhook-Secret`).
- **Docker**: **None**. There is no Docker integration, containerization script, or Dockerode execution in the codebase (only a placeholder directory `infra/docker/` with a `.gitkeep` file).
- **AI / LangGraph**: **None**. There are no AI models, agent workflows, prompt templates, or LangGraph libraries implemented.

---

## 9. Codebase vs. Documentation Mismatches

Discrepancies that remain (future features):
- **Missing Tables**: Database documentation contains `Report`, `Endpoint`, `Finding`, and `TestCase` tables (`docs/schema.md`). These are future extensions and do not exist in the code yet.
- **WebSockets**: Real-time notifications are documented to occur via WebSockets (`docs/architecture.md`), which are not implemented in the codebase yet.
- **AI, LangGraph, & Neo4j**: System documentation details AI workflows, LangGraph nodes (Planner, Executor, Reporter, Reflector), and semantic graph writes to Neo4j. In the codebase, all these stages are currently hardcoded as skipped.
