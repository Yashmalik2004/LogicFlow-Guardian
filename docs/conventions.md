# LogicFlow Guardian - Project Conventions

## Purpose

This document defines the project-wide naming conventions, coding standards, folder structure, API standards, and development rules.

Every contributor and AI assistant must follow these conventions.

This document overrides AI assumptions.

---

# 1. General Naming Convention

Use **PascalCase** for:

- React Components
- TypeScript Classes
- Python Classes
- Database Models

Example

```
User
Project
Report
Analysis
Finding
```

---

Use **camelCase** for

- Variables
- Functions
- Object properties

Example

```
userId
projectId
createProject()
generateReport()
```

---

Use **UPPER_SNAKE_CASE** for

Environment Variables

```
PORT
DATABASE_URL
JWT_SECRET
OPENAI_API_KEY
NEO4J_URI
```

---

Use **kebab-case** for

Folders

```
ms1-core-api
ms2-agent
new-analysis
report-details
```

---

# 2. Folder Structure

Never rename these folders.

```
frontend/

ms1-core-api/

ms2-agent/

infra/

docs/
```

---

## Frontend

```
frontend

app/

components/

lib/

styles/

public/
```

---

## Express (ms1)

```
src/

config/

controllers/

middleware/

models/

routes/

services/

utils/
```

Business logic belongs ONLY inside Services.

Controllers must remain thin.

---

## FastAPI (ms2)

```
app/

agents/

graphs/

parser/

prompts/

reflection/

schemas/

tools/

memory/
```

Each folder has a single responsibility.

---

# 3. File Naming

Express

```
auth.controller.ts

auth.service.ts

auth.routes.ts

project.controller.ts

report.service.ts
```

Never use

```
AuthController.ts

loginController.ts

controller.js
```

---

FastAPI

```
planner_agent.py

executor_agent.py

reflection_agent.py

repository_parser.py

graph_builder.py
```

---

React

```
LoginPage.tsx

DashboardPage.tsx

NewAnalysisPage.tsx

AnalysisProgressPage.tsx

KnowledgeGraphPage.tsx

ReportPage.tsx
```

---

# 4. API Naming

Frontend ONLY communicates with

```
/api/*
```

Examples

```
POST /api/auth/register

POST /api/auth/login

GET /api/auth/me

POST /api/projects

GET /api/projects

GET /api/reports

POST /api/analysis/start
```

---

Internal APIs

Express ↔ FastAPI

```
POST /internal/analyze

GET /internal/status/{analysisId}

GET /internal/report/{analysisId}
```

Never expose internal APIs publicly.

---

# 5. Database Naming

Tables

Always singular.

```
User

Project

Report

Analysis

Endpoint

Finding

TestCase
```

Never

```
Users

Projects

Reports
```

---

Primary Keys

```
user_id

project_id

report_id

analysis_id

endpoint_id

finding_id

testcase_id
```

---

Foreign Keys

```
user_id

project_id

analysis_id

endpoint_id
```

Never use

```
uid

pid

rid
```

---

# 6. React Conventions

Each page

One component.

Reusable UI belongs inside

```
components/
```

API calls belong inside

```
lib/api/
```

Never call APIs directly inside components.

---

Protected routes require JWT.

Store JWT

```
localStorage
```

Key

```
authToken
```

---

# 7. Express Conventions

Routes

↓

Controllers

↓

Services

↓

Database

Never skip layers.

Controllers contain

- validation
- request parsing

Services contain

- business logic

Database access only through models/repositories.

---

# 8. FastAPI Conventions

Workflow

```
Repository

↓

Parser

↓

Knowledge Graph

↓

Planner Agent

↓

Executor Agent

↓

Reflection Agent

↓

Report Generator
```

Never place AI logic inside API routes.

Routes only receive requests.

---

# 9. LangGraph Naming

Nodes

```
RepositoryParserNode

KnowledgeGraphNode

PlannerNode

ExecutorNode

ReflectionNode

ReportGeneratorNode
```

State Object

```
AnalysisState
```

---

# 10. Neo4j Naming

Node Labels

```
Project

Endpoint

Controller

Middleware

Service

Model

BusinessRule

Finding

TestCase
```

Relationships

```
HAS_ENDPOINT

CALLS

USES

READS

WRITES

HAS_FINDING

MITIGATED_BY
```

Always uppercase.

---

# 11. Git Branches

Each developer works on their own branch.

```
main

yash

sneha

vansh
```

Never commit directly to

```
main
```

---

# 12. Commit Convention

Use Conventional Commits.

Examples

```
feat(auth): implement JWT login

feat(project): add project CRUD

feat(report): report endpoint

fix(auth): password validation

docs(schema): update relationships

refactor(ms2): simplify parser
```

---

# 13. Environment Variables

Express

```
PORT

DATABASE_URL

JWT_SECRET

NODE_ENV
```

FastAPI

```
FASTAPI_PORT

DATABASE_URL

NEO4J_URI

NEO4J_USERNAME

NEO4J_PASSWORD

OPENAI_API_KEY
```

Never hardcode values.

---

# 14. API Response Format

Success

```json
{
  "success": true,
  "message": "Project created successfully.",
  "data": {}
}
```

---

Error

```json
{
  "success": false,
  "message": "Unauthorized",
  "error": {}
}
```

All APIs must follow this format.

---

# 15. Logging

Never use

```
console.log()
```

inside production logic.

Use a centralized logger.

---

# 16. Documentation

Every completed phase must update

```
memory.md
```

Never modify

```
architecture.md

schema.md

tech-stack.md
```

unless architecture changes.

---

# 17. AI Development Rules

AI must never

- Rename folders
- Rename APIs
- Rename models
- Rename tables
- Introduce new architecture
- Implement future phases
- Install unnecessary dependencies

AI must only implement

```
current-phase.md
```

---

# 18. Project Ownership

Yash

Owns

```
ms1-core-api
```

Sneha

Owns

```
frontend
```

Vansh

Owns

```
ms2-agent
```

Shared ownership

```
docs/

infra/
```

Changes to shared folders require team agreement.

---

# 19. Code Quality

Before every commit verify

- Builds successfully
- No TypeScript errors
- No Python errors
- No unused imports
- No dead code
- Environment variables documented

---

# 20. Final Principle

When uncertain,

prefer consistency over creativity.

Never invent new naming patterns if one already exists.

Consistency is more valuable than cleverness.