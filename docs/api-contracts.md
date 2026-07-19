# LogicFlow Guardian - API Contracts

## Purpose

This document defines every REST API used throughout the project.

These contracts are frozen before implementation.

Frontend, Express (ms1), and FastAPI (ms2) must strictly follow these contracts.

---

# API Overview

```
React
   │
   ▼
Express (ms1)
   │
   ▼
FastAPI (ms2)
```

Frontend communicates ONLY with Express.

Express communicates ONLY with FastAPI.

FastAPI is never publicly accessible.

---

# Common Response Format

## Success

```json
{
  "success": true,
  "message": "Operation completed successfully.",
  "data": {}
}
```

---

## Error

```json
{
  "success": false,
  "message": "Something went wrong.",
  "error": {}
}
```

Every endpoint must follow this format.

---

# Authentication APIs

---

## Register User

### Endpoint

```
POST /api/auth/register
```

### Authentication

No

### Request

```json
{
  "name": "Yash Malik",
  "email": "yash@example.com",
  "password": "Password123"
}
```

### Response

```json
{
  "success": true,
  "message": "User registered successfully.",
  "data": {
    "userId": 1
  }
}
```

---

## Login

```
POST /api/auth/login
```

### Authentication

No

### Request

```json
{
  "email": "yash@example.com",
  "password": "Password123"
}
```

### Response

```json
{
  "success": true,
  "message": "Login successful.",
  "data": {
    "token": "jwt-token",
    "user": {
      "userId": 1,
      "name": "Yash Malik",
      "email": "yash@example.com"
    }
  }
}
```

---

## Current User

```
GET /api/auth/me
```

Authentication

JWT

Response

```json
{
  "success": true,
  "data": {
    "userId": 1,
    "name": "Yash Malik",
    "email": "yash@example.com"
  }
}
```

---

# Project APIs

---

## Create Project

```
POST /api/projects
```

Authentication

JWT

Request

```json
{
  "repoName": "Bank API",
  "repoUrl": "https://github.com/example/bank-api",
  "branch": "main"
}
```

Response

```json
{
  "success": true,
  "message": "Project created successfully.",
  "data": {
    "projectId": 101
  }
}
```

---

## Get Projects

```
GET /api/projects
```

Authentication

JWT

Response

```json
{
  "success": true,
  "data": [
    {
      "projectId": 101,
      "repoName": "Bank API",
      "status": "Completed"
    }
  ]
}
```

---

## Get Single Project

```
GET /api/projects/{projectId}
```

Authentication

JWT

---

## Delete Project

```
DELETE /api/projects/{projectId}
```

Authentication

JWT

---

# Repository Upload APIs

---

## Upload Repository

```
POST /api/projects/{projectId}/upload
```

Authentication

JWT

Content-Type

```
multipart/form-data
```

Accepted

- ZIP

or

GitHub URL

Request

```
repository.zip

or

repoUrl
```

Response

```json
{
  "success": true,
  "message": "Repository uploaded successfully."
}
```

---

# Analysis APIs

---

## Start Analysis

```
POST /api/analysis/start
```

Authentication

JWT

Request

```json
{
  "projectId": 101
}
```

Response

```json
{
  "success": true,
  "message": "Analysis started.",
  "data": {
    "analysisId": 5001
  }
}
```

---

## Analysis Status

```
GET /api/analysis/{analysisId}
```

Authentication

JWT

Response

```json
{
  "success": true,
  "data": {
    "status": "Running",
    "progress": 70,
    "currentStage": "Planner"
  }
}
```

---

## Cancel Analysis

```
POST /api/analysis/{analysisId}/cancel
```

Authentication

JWT

---

# Report APIs

---

## List Reports

```
GET /api/reports
```

Authentication

JWT

---

## Get Report

```
GET /api/reports/{reportId}
```

Authentication

JWT

---

## Download Report

```
GET /api/reports/{reportId}/download
```

Authentication

JWT

Returns

PDF

---

## Get Findings

```
GET /api/reports/{reportId}/findings
```

Authentication

JWT

---

# Knowledge Graph APIs

---

## Get Knowledge Graph

```
GET /api/projects/{projectId}/graph
```

Authentication

JWT

Response

Graph JSON

---

# Internal APIs (Express ↔ FastAPI)

These APIs are never exposed publicly.

---

## Health Check

```
GET /internal/health
```

Response

```json
{
  "status": "OK"
}
```

---

## Start AI Analysis

```
POST /internal/analysis/start
```

Request

```json
{
  "analysisId": 5001,
  "projectId": 101,
  "userId": 1,
  "repoUrl": "https://github.com/example/bank-api",
  "repoName": "Bank API",
  "branch": "main",
  "repositoryType": "github"
}
```

Response

```json
{
  "accepted": true,
  "message": "Analysis job received. Repository intake started."
}
```

---

## Webhook: Analysis Status Update

```
POST /internal/webhook/analysis-status
```

Called by MS2 to report progress or execution state changes back to MS1. MS1 then updates the `"Analysis"` table.

### Headers
- `X-Webhook-Secret`: Optional shared secret string (must match `MS2_WEBHOOK_SECRET` configuration on both services).

### Request (Standard State Transition)

```json
{
  "analysisId": 5001,
  "status": "CLONING"
}
```

### Request (Intake Complete with Metadata)

```json
{
  "analysisId": 5001,
  "status": "READY_FOR_PARSING",
  "repositoryPath": "/workspace/analysis-5001",
  "repositoryName": "bank-api",
  "language": "TypeScript",
  "framework": "Express",
  "repositorySize": 123456
}
```

### Request (Failure Details)

```json
{
  "analysisId": 5001,
  "status": "FAILED",
  "errorMessage": "git clone failed: exit status 128"
}
```

### Response

```json
{
  "success": true,
  "message": "Status update applied.",
  "data": {}
}
```


---

## Get Knowledge Graph

```
GET /internal/graph/{analysisId}
```

Returns

Knowledge Graph JSON

---

# HTTP Status Codes

| Status | Meaning |
|---------|----------|
| 200 | Success |
| 201 | Resource Created |
| 400 | Validation Error |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict |
| 422 | Invalid Request |
| 500 | Internal Server Error |

---

# Authentication Rules

Public APIs

- Register
- Login

Require JWT

- Projects
- Analysis
- Reports
- Knowledge Graph

Internal APIs

No JWT

Accessible only inside Docker network.

---

# Ownership

| Module | Owner |
|---------|--------|
| Authentication APIs | ms1 |
| Project APIs | ms1 |
| Report APIs | ms1 |
| Analysis APIs | ms1 |
| Internal AI APIs | ms2 |
| Knowledge Graph APIs | ms2 |

---

# API Version

Current Version

```
v1
```

Future versions

```
/api/v2
```

must not break existing contracts.

---

# Contract Rule

No developer or AI assistant may change an endpoint, request body, response body, or status code without updating this document first.

This document is the single source of truth for all REST communication.

---

# Internal API Contract Freeze

This section formally freezes the internal API contract and communication rules between MS1 and MS2 to prevent future updates (Parser, Knowledge Graph, Planner, Docker Runner, Reflection, Reports, etc.) from introducing breaking changes.

## 1. MS1 → MS2 Request Contract

The payload structure for the internal analysis dispatch endpoint:
`POST /internal/analysis/start`
is frozen.

### Request Body Schema
```json
{
  "analysisId": 5001,
  "projectId": 101,
  "userId": 1,
  "repoUrl": "https://github.com/example/bank-api",
  "repoName": "Bank API",
  "branch": "main",
  "repositoryType": "github"
}
```

### Integration Rules
- **Business Data Ownership**: MS1 is responsible for gathering and supplying all business and repository metadata.
- **No Database Queries**: MS2 must never query MS1's database for additional project or job information.
- **Field Modification Restriction**: Existing field names must never be renamed or deleted.
- **Type Compatibility**: Existing field types must remain backwards compatible.
- **Payload Extension**: New optional fields may be appended to the payload in future phases.
- **Forward & Backward Compatibility**: Any future extension must remain backwards compatible.

---

## 2. MS2 → MS1 Webhook Contract

The payload structure for the internal status update webhook:
`POST /internal/webhook/analysis-status`
is frozen.

### Supported Fields
- `analysisId` (Integer, Required)
- `status` (String, Required)
- `repositoryPath` (String, Optional)
- `repositoryName` (String, Optional)
- `language` (String, Optional)
- `framework` (String, Optional)
- `repositorySize` (Integer/BigInt, Optional)
- `errorMessage` (String, Optional)

### Integration Rules
- **Field Deletion/Rename Restriction**: Existing webhook fields must never be renamed or removed.
- **Extension Policy**: Future stages in the pipeline may append additional optional fields to this payload.
- **Forward Compatibility**: MS1 must ignore any unknown properties in the webhook payload.
- **Required Fields**: MS2 must always include `analysisId` and `status` in every webhook request.

---

## 3. API Evolution Rules

To scale the LogicFlow Guardian architecture gracefully without breaking integration boundaries:
- **Append Only**: Always extend JSON payloads by adding new optional fields at the end.
- **No Breaking Changes**: Never change the type of existing fields or rename JSON properties.
- **URL Stability**: Never alter internal endpoint routes or request/response formats without first updating this specification document.
- **Backward Compatibility**: Ensure that all changes to API boundaries maintain backward compatibility.

---

## 4. Database Ownership Reminder

To ensure strict data coupling boundaries:
- **MS1 owns**: `User`, `Project`, `Analysis`, and `Report` (future).
- **MS2 owns**: Execution-state tables (currently `agent_run` table).
- **Neo4j owns**: The knowledge graph.
- **Zero Coupling**: Cross-database SQL queries are strictly forbidden.
- **Pure API Communication**: All interaction between MS1 and MS2 must occur exclusively through HTTP API calls and webhook callbacks.

---

## 5. Status Enum Documentation

The following analysis status values are officially supported across the pipeline:
- `QUEUED`: Job is created and waiting in BullMQ queue (MS1 state).
- `PROCESSING`: Job has been picked up by the Analysis Worker (MS1 state).
- `DISPATCHED`: Job has been forwarded to MS2 API (MS1 state).
- `RECEIVED`: MS2 has accepted the job and created the internal state record (MS2 state).
- `CLONING`: MS2 is cloning the target git repository (MS2 state).
- `VALIDATING`: MS2 is performing basic workspace validation checks (MS2 state).
- `READY_FOR_PARSING`: MS2 has completed the repository intake, extracted metadata, and is ready to parse (MS2 state).
- `COMPLETED`: The analysis run finished successfully (Final state).
- `FAILED`: An execution error occurred during the analysis run (Final state).

*Note: Future phases may introduce additional status values (e.g. for parsing, test generation, and docker runner stages), but existing status values must remain valid.*

---

## 6. Versioning Policy

- **Current Version**: The internal communication API is versioned at `v1`.
- **Incremental Expansion**: Future extensions (Parser, Knowledge Graph, Planner, Docker Runner, Reflection, and Report Generation) must extend the current contract rather than replacing it.
- **Breaking Changes**: Any breaking changes that cannot be implemented in a backwards-compatible manner require a new API version (e.g., `v2`).

---

# Appendix: Database Architecture & Ownership

To guarantee strict service separation, LogicFlow Guardian employs a **Database-per-Service** architecture. The shared database architecture has been completely removed.

### Service Databases
1. **MS1 PostgreSQL Database**: Handles core business data (`User`, `Project`, `Analysis`, `Report`).
2. **MS2 PostgreSQL Database**: Handles local agent execution state (`agent_run`).

### Table Ownership
- **MS1**: Owns `User`, `Project`, `Analysis`, `Report` tables.
- **MS2**: Owns `agent_run` table.
- **Neo4j Graph Database**: Owns the knowledge graph nodes/relationships (Controller, Endpoint, Service, Model, etc.) and is written to exclusively by MS2.

### Cross-Service Communication
- MS2 never queries or updates MS1 tables directly.
- MS1 passes all required project/analysis parameters inside the body of `POST /internal/analysis/start`.
- MS2 sends state updates and metadata back to MS1 via webhook callbacks (`POST /internal/webhook/analysis-status`).

### Migration Process
- **MS1 Database**: Table schemas are initialized via MS1-specific migration pathways on the MS1 DB host.
- **MS2 Database**: The database table structure is defined by the SQL migration file `ms2-agent/app/config/migrations/001_create_agent_run.sql`. This must be initialized on the MS2 DB host. It is automatically initialized on MS2 application startup (via SQLAlchemy `create_all()`) or can be run manually using a PostgreSQL client connection.
