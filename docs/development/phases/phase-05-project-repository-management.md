# Phase 05 — Project & Repository Management

## Objective

Implement project management for authenticated users.

This phase establishes the application's primary resource: **Projects**.

Projects act as containers for future repository analyses.

Only metadata is managed during this phase.

Repository contents are NOT handled yet.

---

# Scope

Implement only CRUD operations for projects.

Every project belongs to exactly one authenticated user.

Projects must be stored in PostgreSQL (MS1).

Do NOT communicate with MS2.

Do NOT upload repositories.

Do NOT clone GitHub repositories.

---

# Deliverables

## Database

Create the PROJECT table.

Suggested fields:

- id
- user_id
- project_name
- repository_type
- github_url (nullable)
- default_branch
- description
- status
- created_at
- updated_at

Status should initially be:

ACTIVE

---

## Relationships

USER

↓

PROJECT

One user owns many projects.

One project belongs to one user.

---

# Backend

Implement the following modules.

Controllers

- ProjectController

Services

- ProjectService

Routes

- ProjectRoutes

Models

- ProjectModel

Validation

- Request validation

---

# REST APIs

## Create Project

POST

/api/projects

Body

```json
{
  "projectName": "Bank API",
  "repositoryType": "github",
  "githubUrl": "https://github.com/user/bank-api",
  "defaultBranch": "main",
  "description": "Business banking backend"
}
```

Response

201 Created

---

## List Projects

GET

/api/projects

Returns only projects owned by the authenticated user.

---

## Get Project

GET

/api/projects/:id

Returns a single project.

Users cannot access projects they do not own.

---

## Update Project

PUT

/api/projects/:id

Allow editing:

- projectName
- description
- githubUrl
- defaultBranch

Do not allow changing ownership.

---

## Delete Project

DELETE

/api/projects/:id

Soft delete preferred.

If soft delete is not implemented, hard delete is acceptable.

---

# Authentication

All endpoints require JWT.

Unauthenticated users receive:

401 Unauthorized

Attempting to access another user's project returns:

403 Forbidden

---

# Validation Rules

Project name

Required

Maximum length:

100 characters

Repository type

Allowed values

- github
- zip

GitHub URL

Optional

Must be valid if provided.

Default branch

Optional

Defaults to:

main

---

# Business Rules

A project exists independently of repository uploads.

Creating a project does NOT start analysis.

Creating a project does NOT contact MS2.

Creating a project does NOT clone repositories.

Projects are simply metadata containers.

---

# Folder Scope

Only modify:

ms1-core-api/

- controllers
- services
- routes
- models
- middleware (if required)
- config
- utils

Database migrations (if applicable)

Do NOT modify:

frontend/

ms2-agent/

infra/

---

# Testing Checklist

✓ Register a user

✓ Login successfully

✓ Obtain JWT

✓ Create project

✓ List own projects

✓ View single project

✓ Update project

✓ Delete project

✓ Unauthorized requests rejected

✓ Users cannot access other users' projects

✓ Validation errors handled correctly

---

# Success Criteria

The following workflow must succeed.

Register

↓

Login

↓

Receive JWT

↓

Create Project

↓

Store in PostgreSQL

↓

Retrieve Project

↓

Update Project

↓

Delete Project

All operations occur entirely within MS1.

MS2 is never contacted.

---

# Completion Checklist

- Project model implemented
- CRUD APIs completed
- JWT protection enabled
- Validation complete
- Ownership verification implemented
- API contract followed
- Database tested
- Existing authentication still works
- memory.md updated

Stop after completion.

Do not continue to Phase 06.