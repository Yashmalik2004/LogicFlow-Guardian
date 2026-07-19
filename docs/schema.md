# LogicFlow Guardian - Database Schema

## Purpose

This document defines the logical database schema of LogicFlow Guardian.

It specifies:

- Database ownership
- Table ownership
- Entity relationships
- Primary keys
- Foreign keys
- Microservice responsibilities

This document is the single source of truth for the application's data model.

---

# Database Architecture

```
                    React Frontend
                           │
                           ▼
                    Express.js (MS1) ◄──────────────────┐
                           │                            │ (HTTP webhook callbacks)
                           ▼                            │
             PostgreSQL (Supabase MS1 DB)               │
           ┌────────────────────────────┐               │
           │ User                       │               │
           │ Project                    │               │
           │ Analysis                   │               │
           │ Report (future)            │               │
           └────────────────────────────┘               │
                           │                            │
             (Enqueues job via BullMQ/Redis)            │
                           │                            │
                           ▼                            │
                    Analysis Worker                     │
                           │                            │
             (POST /internal/analysis/start)            │
                           │                            │
                           ▼                            │
                     FastAPI (MS2) ─────────────────────┘
                           │
                           ▼
              PostgreSQL (Supabase MS2 DB)
              ┌────────────────────────┐
              │ agent_run              │
              └────────────────────────┘
                           │
                           ▼
                      Neo4j AuraDB
```

---

# Database Ownership

## MS1 PostgreSQL

MS1 owns all application-level and business data.

Tables

- User
- Project
- Analysis
- Report (future)

Only Express.js may modify these tables directly. Status updates on the Analysis table are triggered by MS2 via HTTP webhooks, and MS1 performs the updates.

---

## MS2 PostgreSQL

MS2 owns its own pipeline execution state and temporary runtime logs.

Tables

- AgentRun

Only FastAPI may read or write this database. MS2 must never connect to or modify MS1's PostgreSQL tables directly.

---

## Neo4j

Neo4j stores semantic relationships extracted during repository analysis.

It is owned exclusively by MS2.

---

# Entity Overview

```
[MS1 Database]
User
 │
 └───────────────┐
                 ▼
             Project
                 │
        ┌────────┴─────────┐
        ▼                  ▼
     Report            Analysis
 

[MS2 Database]
AgentRun (linked by analysis_id to Analysis, project_id to Project)
```


---

# MS1 Tables

---

## User

Stores registered users.

| Field | Type | Notes |
|--------|------|------|
| user_id | Integer | Primary Key |
| name | String | |
| email | String | Unique |
| password_hash | String | Encrypted password |
| created_at | Timestamp | |

---

## Project

Stores uploaded repositories.

| Field | Type | Notes |
|--------|------|------|
| project_id | Integer | Primary Key |
| user_id | Integer | FK → User |
| repo_name | String | |
| repo_url | String | |
| branch | String | |
| status | String | ACTIVE / DELETED |
| created_at | Timestamp | |
| updated_at | Timestamp | |

---

## Analysis

Represents one execution of the AI pipeline. Owned by MS1. Status updates and repository metadata are sent via webhooks from MS2 and saved here by MS1.

| Field | Type | Notes |
|--------|------|------|
| analysis_id | Integer | Primary Key |
| project_id | Integer | FK → Project |
| user_id | Integer | FK → User |
| bull_job_id | String | BullMQ job ID |
| status | String | QUEUED / PROCESSING / DISPATCHED / CLONING / VALIDATING / READY_FOR_PARSING / COMPLETED / FAILED |
| queue_position | Integer | |
| repository_path | String | Cloned repository path on MS2 |
| repository_name | String | Detected repository name |
| language | String | Detected language |
| framework | String | Detected framework |
| repository_size | BigInt | Repository size in bytes |
| started_at | Timestamp | |
| completed_at | Timestamp | |
| created_at | Timestamp | |
| updated_at | Timestamp | |

---

## Report

Stores generated reports (future).

| Field | Type | Notes |
|--------|------|------|
| report_id | Integer | Primary Key |
| project_id | Integer | FK → Project |
| file_path | String | PDF path |
| generated_at | Timestamp | |

---

# MS2 Tables

---

## AgentRun

Execution record for one analysis run managed by MS2, stored in MS2's separate database. Tracks MS2's local pipeline state.

| Field | Type | Notes |
|--------|------|------|
| id | Integer | Primary Key |
| analysis_id | Integer | Reference by value to MS1 Analysis ID (no foreign key) |
| project_id | Integer | Reference by value to MS1 Project ID |
| status | String | RECEIVED / CLONING / VALIDATING / READY_FOR_PARSING / COMPLETED / FAILED |
| repository_path | String | Local clone directory |
| repository_name | String | Detected repository name |
| language | String | Detected language |
| framework | String | Detected framework |
| repository_size | BigInt | Repository size in bytes |
| error_message | String | Error details if the run failed |
| started_at | Timestamp | |
| completed_at | Timestamp | |
| created_at | Timestamp | |
| updated_at | Timestamp | |


---

# Relationships

```
User (MS1)
  │
  ▼
Project (MS1)
  │
  ▼
Analysis (MS1) < - - - - Linked by analysis_id - - - - > AgentRun (MS2)
```

---

# Neo4j Knowledge Graph

## Node Labels

- Project
- Controller
- Endpoint
- Service
- Middleware
- Model
- BusinessRule
- Finding (future)
- TestCase (future)

---

## Relationships

```
(Project)-[:HAS_ENDPOINT]->(Endpoint)
(Endpoint)-[:CALLS]->(Controller)
(Controller)-[:USES]->(Service)
(Service)-[:READS]->(Model)
(Service)-[:WRITES]->(Model)
```

---

# Ownership Rules

## Express.js (MS1)

May access (read/write):

- User
- Project
- Analysis
- Report (future)

Must NOT access:

- AgentRun (MS2 Database)
- Neo4j Graph Database

---

## FastAPI (MS2)

May access (read/write):

- AgentRun
- Neo4j Graph Database

Must NOT access or query directly (forbidden from database configuration):

- User
- Project
- Analysis
- Report

---

# Communication Rules

```
Frontend
   │
   ▼
Express (MS1) ─── HTTP POST /internal/analysis/start ───► FastAPI (MS2)
      │                                                        │
      │                                                        │ (HTTP Webhook POST)
      ◄─── /internal/webhook/analysis-status ──────────────────┘
```

1. The frontend never communicates directly with FastAPI.
2. FastAPI never communicates directly with the frontend.
3. MS2 sends webhook callbacks to MS1 to report status changes.
4. MS1 updates its own Analysis table in response to webhooks.

---

# Final Principle

Each microservice owns its own data.

Cross-service communication occurs only through REST APIs and Webhook callbacks.

No microservice may directly read or modify another microservice's database tables.

---

# Shared Database Architecture Removal

Historically, MS1 and MS2 shared a single database connection. This led to coupling between service schemas, specifically with MS2 querying and mutating MS1-owned business tables (such as `Project` and `Analysis`).

The shared-database architecture was removed in favor of a strictly isolated **Database-per-Service** design:
1. **MS1 PostgreSQL Database**: Handles core business data (`User`, `Project`, `Analysis`, `Report`).
2. **MS2 PostgreSQL Database**: Handles local agent execution state (`agent_run`).
3. **No Direct Queries**: MS2 has no network visibility or configured credentials for MS1's database, and vice versa.
4. **Data Ingestion via API**: All project/analysis metadata required by MS2 is sent directly within the `POST /internal/analysis/start` request payload.
5. **Updates via Webhooks**: All state and metadata updates from MS2 to MS1 are communicated asynchronously via `POST /internal/webhook/analysis-status` authenticated with `X-Webhook-Secret`.

---

# Migration Process

The microservices utilize raw SQL migration scripts instead of an ORM migration manager (like Alembic).

### MS1 Database Migration
MS1 table schemas are defined in the MS1 core application repository. They must be executed against MS1's database host (from `DATABASE_URL`).

### MS2 Database Migration
MS2's database tables (specifically `agent_run`) must be initialized against MS2's own database host (from `MS2_DATABASE_URL`).

#### Initialization SQL
The migration is located at:
[001_create_agent_run.sql](file:///c:/Users/YASH/Desktop/LogicFlow-Guardian/ms2-agent/app/config/migrations/001_create_agent_run.sql)

To apply this migration manually:
1. Connect to the MS2 database instance using `psql`, pgAdmin, or any other PostgreSQL client:
   ```bash
   psql "postgresql://<user>:<password>@<host>:<port>/postgres_ms2"
   ```
2. Run the SQL script content to create the `agent_run` table and its indexes.

To apply this migration automatically:
1. Ensure `MS2_DATABASE_URL` in `.env` is pointing to the correct separate database (e.g. `postgres_ms2`).
2. Execute a Python migration runner or run the FastAPI app (which executes `Base.metadata.create_all(bind=_engine)` upon start, verifying and automatically initializing the `agent_run` table and its indexes).
