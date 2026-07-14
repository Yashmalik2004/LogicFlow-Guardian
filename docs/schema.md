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
                    Express.js (MS1)
                           │
                           ▼
              PostgreSQL (Supabase)
          ┌────────────────────────────┐
          │ User                       │
          │ Project                    │
          │ Report                     │
          └────────────────────────────┘
                           │
                    Internal REST API
                           │
                           ▼
                    FastAPI (MS2)
                    ┌───────────────┐
                    │ PostgreSQL    │
                    │ Analysis      │
                    │ Endpoint      │
                    │ Finding       │
                    │ TestCase      │
                    └───────────────┘
                           │
                           ▼
                     Neo4j AuraDB
```

---

# Database Ownership

## MS1 PostgreSQL

MS1 owns all application-level data.

Tables

- User
- Project
- Report

Only Express.js may modify these tables.

---

## MS2 PostgreSQL

MS2 owns all AI-analysis metadata.

Tables

- Analysis
- Endpoint
- Finding
- TestCase

Only FastAPI may modify these tables.

---

## Neo4j

Neo4j stores semantic relationships extracted during repository analysis.

It is owned exclusively by MS2.

---

# Entity Overview

```
User
 │
 └───────────────┐
                 ▼
             Project
                 │
        ┌────────┴─────────┐
        ▼                  ▼
     Report            Analysis
                            │
            ┌───────────────┼──────────────┐
            ▼               ▼              ▼
        Endpoint        Finding      TestCase
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
| status | String | Pending / Running / Completed |
| uploaded_at | Timestamp | |

---

## Report

Stores generated reports.

| Field | Type | Notes |
|--------|------|------|
| report_id | Integer | Primary Key |
| project_id | Integer | FK → Project |
| file_path | String | PDF path |
| generated_at | Timestamp | |

---

# MS2 Tables

---

## Analysis

Represents one execution of the AI pipeline.

| Field | Type | Notes |
|--------|------|------|
| analysis_id | Integer | Primary Key |
| project_id | Integer | Reference to Project |
| status | String | Running / Completed |
| started_at | Timestamp | |
| completed_at | Timestamp | |

---

## Endpoint

Discovered API endpoints.

| Field | Type | Notes |
|--------|------|------|
| endpoint_id | Integer | Primary Key |
| analysis_id | Integer | FK → Analysis |
| route | String | |
| method | String | |
| controller | String | |
| authentication | String | |

---

## Finding

Detected vulnerabilities.

| Field | Type | Notes |
|--------|------|------|
| finding_id | Integer | Primary Key |
| analysis_id | Integer | FK → Analysis |
| endpoint_id | Integer | FK → Endpoint |
| severity | String | Critical / High / Medium / Low |
| title | String | |
| description | Text | |
| recommendation | Text | |

---

## TestCase

Generated AI test cases.

| Field | Type | Notes |
|--------|------|------|
| testcase_id | Integer | Primary Key |
| analysis_id | Integer | FK → Analysis |
| endpoint_id | Integer | FK → Endpoint |
| title | String | |
| description | Text | |
| request_method | String | |
| status | String | Pending / Passed / Failed |

---

# Relationships

```
User

↓

Project

↓

Report

↓

Analysis

↓

Endpoint

↓

Finding

↓

TestCase
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
- Finding
- TestCase

---

## Relationships

```
(Project)-[:HAS_ENDPOINT]->(Endpoint)

(Endpoint)-[:CALLS]->(Controller)

(Controller)-[:USES]->(Service)

(Service)-[:READS]->(Model)

(Service)-[:WRITES]->(Model)

(Endpoint)-[:HAS_FINDING]->(Finding)

(Finding)-[:MITIGATED_BY]->(TestCase)

(Model)-[:RELATES_TO]->(Model)
```

---

# Ownership Rules

## Express.js

May access

- User
- Project
- Report

Must NOT access

- Analysis
- Endpoint
- Finding
- TestCase

---

## FastAPI

May access

- Analysis
- Endpoint
- Finding
- TestCase
- Neo4j

Must NOT modify

- User
- Project
- Report

---

# Communication Rules

Frontend

↓

Express

↓

PostgreSQL (MS1)

↓

REST API

↓

FastAPI

↓

PostgreSQL (MS2)

↓

Neo4j

The frontend never communicates directly with FastAPI.

FastAPI never communicates directly with the frontend.

---

# Future Extensions

Future versions may introduce:

- Organization
- Team
- AnalysisJob
- Notification
- AIModel
- PromptVersion

These are intentionally excluded from Milestone 2.

---

# Final Principle

Each microservice owns its own data.

Cross-service communication occurs only through REST APIs.

No microservice may directly modify another microservice's tables.