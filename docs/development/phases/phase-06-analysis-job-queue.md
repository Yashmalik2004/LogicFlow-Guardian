# Phase 06 — Analysis Job Queue

## Objective

Introduce asynchronous job processing into LogicFlow Guardian using Redis and BullMQ.

This phase establishes the queue infrastructure required for scalable repository analysis.

Repository analysis must no longer execute synchronously.

Instead, analysis requests are converted into background jobs.

MS2 is NOT involved in this phase.

No AI analysis is performed.

---

# Purpose

Business logic analysis can take several minutes.

The frontend should receive an immediate response instead of waiting.

Future workflow

Client

↓

MS1

↓

Create Analysis

↓

Redis Queue

↓

Immediate Response

↓

Background Worker

↓

Completed

This phase only builds the queue foundation.

---

# Scope

Implement only:

- Redis connection
- BullMQ configuration
- Analysis queue
- Background worker
- Analysis database table
- Analysis APIs
- Queue status updates

Do NOT implement:

- MS2 communication
- Repository parsing
- Git cloning
- Repository storage
- LangGraph
- Docker
- WebSockets
- Webhooks
- Report generation

---

# Dependencies

Install only

- redis
- bullmq
- ioredis

No additional libraries.

---

# Folder Scope

Only modify

ms1-core-api/

- config
- controllers
- services
- routes
- models
- utils

Database migrations

Do NOT modify

frontend/

ms2-agent/

infra/

---

# Database

Create a new table

ANALYSIS

Suggested fields

| Column | Description |
|----------|-------------|
| id | Primary Key |
| project_id | FK → PROJECT |
| user_id | FK → USER |
| bull_job_id | Queue Job Identifier |
| status | Current Analysis Status |
| queue_position | Optional Queue Position |
| started_at | Nullable |
| completed_at | Nullable |
| created_at | Timestamp |
| updated_at | Timestamp |

---

# Status Values

Allowed values

- QUEUED
- PROCESSING
- COMPLETED
- FAILED

Future phases may introduce

- PARSING
- GRAPH_BUILDING
- PLANNING
- EXECUTING
- REFLECTING
- REPORT_GENERATION

Do NOT implement these now.

---

# Queue

Create a BullMQ queue

AnalysisQueue

Each queued job should contain

```json
{
  "analysisId": 42,
  "projectId": 17,
  "userId": 3
}
```

Notice

The queue never owns the application's identity.

The BullMQ Job ID is stored separately.

---

# Queue Worker

Implement one worker.

Worker behaviour

Receive Job

↓

Update database

PROCESSING

↓

Print

Starting Analysis...

↓

Wait 5 seconds

↓

Update database

COMPLETED

↓

Print

Analysis Completed

No AI.

No Parser.

No Docker.

No MS2.

---

# REST APIs

## Start Analysis

POST

/api/analysis/start

Body

```json
{
  "projectId": 17
}
```

Flow

Validate JWT

↓

Validate project ownership

↓

Create ANALYSIS record

↓

Create BullMQ Job

↓

Store Bull Job ID

↓

Return immediately

Example Response

```json
{
  "analysisId": 42,
  "status": "QUEUED"
}
```

Never return the BullMQ Job ID.

The frontend should only know about analysisId.

---

## Get Analysis Status

GET

/api/analysis/:analysisId/status

Example Response

```json
{
  "analysisId": 42,
  "status": "PROCESSING"
}
```

The API reads only from PostgreSQL.

It never queries BullMQ directly.

---

# Business Rules

Every analysis belongs to one project.

Every project belongs to one user.

Users may only start analyses on their own projects.

Creating an analysis

DOES

- Create database record
- Create queue job

DOES NOT

- Contact MS2
- Clone repositories
- Parse code
- Execute AI
- Generate reports

---

# Error Handling

Redis unavailable

↓

503 Service Unavailable

Queue creation failure

↓

Update Analysis

FAILED

↓

500 Internal Server Error

Invalid project

↓

404 Not Found

Unauthorized user

↓

401 Unauthorized

Forbidden project

↓

403 Forbidden

---

# Logging

Log

Analysis Created

↓

Queue Job Created

↓

Worker Started

↓

Worker Completed

↓

Worker Failed

Do not implement OpenTelemetry yet.

---

# Architecture Notes

BullMQ is considered an internal infrastructure component.

The application's business entity is

Analysis

The mapping is

Analysis

↓

BullMQ Job

↓

Worker

↓

Status Updates

The frontend communicates only through analysisId.

This allows BullMQ to be replaced by

- RabbitMQ
- Kafka
- AWS SQS

without changing frontend APIs or database design.

---

# Testing Checklist

✓ Redis connection established

✓ BullMQ queue created

✓ Worker starts successfully

✓ Analysis record created

✓ Queue job created

✓ Bull Job ID stored

✓ Worker updates status

✓ Completed status stored

✓ Unauthorized requests rejected

✓ Invalid projects rejected

✓ Existing project APIs continue working

---

# Success Criteria

Workflow

Login

↓

Create Project

↓

Start Analysis

↓

Analysis record created

↓

BullMQ Job created

↓

Worker receives job

↓

Status becomes PROCESSING

↓

Status becomes COMPLETED

↓

Client retrieves status

No communication with MS2 occurs.

---

# Completion Checklist

- Redis configured
- BullMQ configured
- Analysis table implemented
- Queue created
- Worker created
- Analysis APIs implemented
- Database updates working
- Logging implemented
- Error handling complete
- Existing functionality still works
- memory.md updated

Stop immediately after completion.

Do not continue to Phase 07.