# Phase 07 — MS1 ↔ MS2 Job Communication

## Objective

Establish secure internal communication between MS1 and MS2.

MS1 should dispatch queued analysis jobs to MS2.

MS2 should acknowledge receipt of the job.

This phase verifies that the two microservices can communicate reliably before introducing repository analysis.

---

# Purpose

The AI service should never be invoked directly by frontend requests.

Instead:

Client

↓

MS1

↓

BullMQ Worker

↓

MS2

↓

Acknowledgement

↓

Worker Finished

No analysis occurs.

---

# Scope

Implement only:

- Internal REST communication
- Analysis dispatch service
- MS2 analysis endpoint
- Request validation
- Retry handling
- Timeout handling
- Logging

Do NOT implement:

- Repository download
- Git cloning
- Repository storage
- Parser
- Neo4j
- LangGraph
- Docker
- Report generation

---

# Folder Scope

Modify

ms1-core-api/

- services
- config
- utils

ms2-agent/

- app
- schemas

Do not modify

frontend/

infra/

---

# Internal API

MS2 exposes

POST

/internal/analysis/start

This endpoint is NOT public.

Only MS1 may call it.

---

## Request

```json
{
    "analysisId": 42,
    "projectId": 17,
    "userId": 5
}
```

---

## Response

```json
{
    "accepted": true,
    "message": "Analysis job received."
}
```

MS2 does not process the job.

It only validates the payload and acknowledges receipt.

---

# Worker Behaviour

BullMQ Worker

↓

Receives Job

↓

Calls MS2

↓

Receives ACK

↓

Updates ANALYSIS

Status

DISPATCHED

↓

Worker Completed

No AI execution.

---

# Database

Extend ANALYSIS status values.

Current

- QUEUED
- PROCESSING
- COMPLETED
- FAILED

Add

- DISPATCHED

Meaning

The job has been successfully transferred to MS2.

---

# Configuration

Store MS2 base URL inside environment variables.

Example

MS2_BASE_URL=http://localhost:8000

Never hardcode service URLs.

---

# Timeout Rules

Maximum request timeout

30 seconds

If timeout occurs

↓

Retry

Maximum retries

3

If retries fail

↓

Update Analysis

FAILED

↓

Log error

---

# Validation

MS2 validates

analysisId

projectId

userId

Missing fields

↓

400 Bad Request

---

# Error Handling

MS2 unavailable

↓

Retry

↓

FAILED

Invalid payload

↓

400

Unexpected exception

↓

500

---

# Logging

Log

Dispatch Started

↓

Request Sent

↓

Acknowledgement Received

↓

Dispatch Completed

↓

Dispatch Failed

---

# Architecture Notes

Communication remains synchronous only for the acknowledgement.

Long-running analysis is intentionally NOT performed during the request.

Future phases will move AI execution into a dedicated worker inside MS2.

---

# Testing Checklist

✓ MS1 reaches MS2

✓ Payload transmitted correctly

✓ ACK returned

✓ Analysis status updated to DISPATCHED

✓ Retry mechanism works

✓ Timeout handled

✓ Invalid payload rejected

✓ Existing queue continues working

---

# Success Criteria

Workflow

Login

↓

Create Project

↓

Start Analysis

↓

BullMQ Queue

↓

Worker

↓

POST /internal/analysis/start

↓

MS2 returns ACK

↓

Analysis status

DISPATCHED

↓

Worker exits

No repository processing occurs.

---

# Completion Checklist

- Internal REST endpoint created
- Dispatch service implemented
- Environment configuration completed
- Retry logic implemented
- Timeout handling implemented
- Logging completed
- Existing queue still works
- memory.md updated

Stop immediately after completion.

Do not continue to Phase 08.