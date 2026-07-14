# LogicFlow Guardian - Development Memory

## Purpose

This document records the implementation history of the project.

It serves as persistent context for developers and AI assistants.

Every completed phase must update this document.

---

# Current Project State

Current Milestone

Milestone 2

Current Phase

Phase 05 — Project & Repository Management

---

# Completed Phases

- Phase 01 — MS1 Foundation ✅
- Phase 02 — MS2 Foundation ✅
- Phase 03 — Authentication ✅
- Phase 04 — Frontend Authentication ✅
- Phase 05 — Project & Repository Management ✅

---

# Architectural Decisions

## Microservices

Express.js (ms1)

- Authentication
- Project Management
- Report Management
- PostgreSQL (Application Database)

FastAPI (ms2)

- AI Analysis
- Repository Parsing
- LangGraph
- Neo4j
- PostgreSQL (AI Metadata)

---

## Database Ownership

MS1 owns

- User
- Project
- Report

MS2 owns

- Analysis
- Endpoint
- Finding
- TestCase

Neo4j stores

- Knowledge Graph

---

## API Ownership

Frontend

↓

Express only

Express

↓

FastAPI only

FastAPI

↓

Neo4j / PostgreSQL

---

# Development Log

## Phase 01

Status

Completed ✅

Files Created

- ms1-core-api/tsconfig.json
- ms1-core-api/src/app.ts
- ms1-core-api/src/server.ts
- ms1-core-api/src/config/env.ts
- ms1-core-api/src/config/database.ts
- ms1-core-api/src/controllers/health.controller.ts
- ms1-core-api/src/routes/health.routes.ts
- ms1-core-api/src/utils/logger.ts
- ms1-core-api/.env.example
- ms1-core-api/.gitignore

Files Modified

- ms1-core-api/package.json (added scripts, dependencies)

Commit

feat(ms1): initialize express backend foundation

Notes

- TypeScript 5.x pinned (TypeScript 7 is incompatible with ts-node-dev 2.x)
- PostgreSQL connection uses Supabase connection string from .env
- GET /health returns HTTP 200 with { "status": "OK", "service": "ms1-core-api" }
- Server tested locally — connection and health endpoint verified

---

## Phase 02

Status

Completed ✅

Files Created

- ms2-agent/main.py
- ms2-agent/app/app.py
- ms2-agent/app/config/env.py
- ms2-agent/app/config/__init__.py
- ms2-agent/agents/__init__.py
- ms2-agent/graphs/__init__.py
- ms2-agent/memory/__init__.py
- ms2-agent/parser/__init__.py
- ms2-agent/prompts/__init__.py
- ms2-agent/reflection/__init__.py
- ms2-agent/schemas/__init__.py
- ms2-agent/tools/__init__.py
- ms2-agent/.env.example

Files Modified

- ms2-agent/app/config/postgres.py (implemented SQLAlchemy connection)
- ms2-agent/app/config/neo4j.py (implemented Neo4j driver connection)
- ms2-agent/requirements.txt (added SQLAlchemy, psycopg2-binary, neo4j, python-dotenv)
- ms2-agent/.env (added PYTHON_ENV=development, changed URI scheme to neo4j+ssc:// for dev SSL workaround)
- ms2-agent/.gitignore (ignored venv/ and IDE config directories)

Commit

feat(ms2): initialize fastapi foundation

Notes

- Successfully established connections to PostgreSQL and Neo4j on app startup.
- Handled SSL cert verification failure on local environments connecting to Neo4j AuraDB by utilizing `neo4j+ssc://` scheme.
- Internal health endpoint `GET /internal/health` successfully returns HTTP 200 OK and expected payload.

---

## Phase 03

Status

Completed ✅

Files Created

- ms1-core-api/src/models/user.model.ts
- ms1-core-api/src/services/auth.service.ts
- ms1-core-api/src/middleware/auth.middleware.ts
- ms1-core-api/src/controllers/auth.controller.ts
- ms1-core-api/src/routes/auth.routes.ts

Files Modified

- ms1-core-api/package.json (added dependencies: bcrypt, jsonwebtoken, express-validator and types)
- ms1-core-api/src/config/database.ts (added automatic creation of the "User" table on startup)
- ms1-core-api/src/app.ts (registered authRouter on /api/auth)

Commit

feat(auth): implement JWT authentication

Notes

- Installed bcrypt, jsonwebtoken, and express-validator with TypeScript declarations.
- Updated database connection initialization to run query ensuring "User" table exists. Wrap User table in quotes as it is a PostgreSQL reserved keyword.
- Built AuthService and UserModel for password encryption, comparison, and token creation.
- AuthMiddleware verifies incoming authorization tokens, supporting both Bearer format and raw tokens.
- Fully verified all endpoints (Register, Login, Me) using a Node.js test script verifying success/error response formats.

---

## Phase 04

Status

Completed ✅

Files Created

- frontend/app/services/authService.ts (axios API calls for register, login, getCurrentUser)
- frontend/app/contexts/AuthContext.tsx (React context for auth state, JWT, session restore)
- frontend/app/hooks/useAuth.ts (useAuth hook)
- frontend/app/pages/Login.tsx (login form page)
- frontend/app/pages/Register.tsx (register form page)
- frontend/app/pages/Dashboard.tsx (placeholder dashboard page)
- frontend/components/ProtectedRoute.tsx (guards /dashboard, redirects unauthenticated users)
- frontend/styles/auth.css (minimal vanilla CSS for auth forms and dashboard)
- frontend/.env.example (documents VITE_API_URL)

Files Modified

- frontend/src/App.tsx (replaced Vite boilerplate with React Router routes)
- frontend/src/main.tsx (wrapped root with BrowserRouter and AuthProvider)
- frontend/index.html (updated title to LogicFlow Guardian, added meta description)

Dependencies Installed

- react-router-dom (routing)
- axios (HTTP client)
- jwt-decode (optional, installed per phase spec)

Commit

feat(frontend): implement authentication flow

Notes

- JWT is stored in localStorage under key `authToken` per conventions.md.
- Authorization header format: `Bearer <token>` per api-contracts.md.
- Session is restored on page refresh via GET /api/auth/me on AuthContext mount.
- Unauthenticated access to /dashboard redirects to / (login).
- All API calls go through authService.ts, never directly inside components.
- TypeScript strict compile (tsc --noEmit) passes with zero errors.
- No UI libraries used (no Tailwind, no Material UI) per phase spec.

---

## Phase 05

Status

Completed ✅

Files Created

- ms1-core-api/src/models/project.model.ts (ProjectModel with CRUD + soft delete)
- ms1-core-api/src/services/project.service.ts (ProjectService with ownership enforcement)
- ms1-core-api/src/controllers/project.controller.ts (ProjectController with validation)
- ms1-core-api/src/routes/project.routes.ts (ProjectRoutes mounted at /api/projects)

Files Modified

- ms1-core-api/src/config/database.ts (added Project table CREATE TABLE IF NOT EXISTS)
- ms1-core-api/src/app.ts (registered projectRouter on /api/projects)

APIs Implemented

- POST /api/projects — Create project (JWT required)
- GET /api/projects — List user's own projects (JWT required)
- GET /api/projects/:id — Get single project (JWT required, 403 if not owner)
- PUT /api/projects/:id — Update project (JWT required, 403 if not owner)
- DELETE /api/projects/:id — Soft-delete project (JWT required, 403 if not owner)

Database Changes

- "Project" table created with fields: project_id, user_id (FK→User), repo_name, repo_url, branch, description, repository_type, status, created_at, updated_at
- Soft delete implemented via status = 'DELETED'
- Ownership enforced at service layer before any mutation

Commit

feat(project): implement project CRUD with JWT protection and ownership enforcement

Notes

- All APIs follow the standard { success, message, data } response format per conventions.md.
- Business logic lives entirely in ProjectService; ProjectController remains thin.
- express-validator used for request validation (reused from Phase 03, no new dependencies needed).
- GitHub URL validated with isURL() when provided; optional per phase spec.
- defaultBranch defaults to 'main' when not provided.
- Soft delete used (status='DELETED'); hard delete not used.
- TypeScript strict compile (tsc --noEmit) passes with zero errors.
- Server started, PostgreSQL connected, Project table created successfully.
- Existing auth endpoints (/api/auth/*) are fully intact.

---


None

---

# Pending Work

- Analysis Job Queue (Redis + BullMQ)
- MS1 ↔ MS2 Job Communication
- Repository Storage & Retrieval
- Repository Parser
- Knowledge Graph Builder (Neo4j)
- LangGraph Planner Agent
- Docker Runner Service
- Dynamic Test Executor
- Reflection Agent
- Report Generator
- Webhook & Real-Time Progress Updates
- Report Viewer & Knowledge Graph UI
- Logging, Metrics & Observability
- Deployment & CI/CD
- Production Hardening & Performance

---

# AI Reminder

Before implementing any code:

1. Read architecture.md
2. Read tech-stack.md
3. Read schema.md
4. Read conventions.md
5. Read api-contracts.md
6. Read roadmap.md
7. Read memory.md
8. Read current-phase.md

Then implement ONLY the active phase.

Never continue into the next phase automatically.