# LogicFlow Guardian - Development Roadmap

## Purpose

This roadmap defines the complete implementation plan for LogicFlow Guardian.

The project is divided into small, independent phases so that each feature can be designed, implemented, tested, committed, and reviewed separately.

Only one phase should be active at any given time.

---

# Final Product Goal

Build a production-ready AI-powered Business Logic Vulnerability Testing Platform capable of:

- User Authentication
- Repository Management
- GitHub & ZIP Upload
- AI-driven Static Analysis
- Knowledge Graph Generation
- Business Rule Extraction
- Intelligent Test Planning
- Secure Dynamic Test Execution
- Reflection & Self-Improvement
- Explainable Security Reports
- Real-time Progress Tracking
- Production Deployment
- Horizontal Scalability

---

# Development Phases

| Phase | Status | Description |
|--------|--------|-------------|
| Phase 01 | ✅ Completed | MS1 Foundation |
| Phase 02 | ✅ Completed | MS2 Foundation |
| Phase 03 | ✅ Completed | JWT Authentication |
| Phase 04 | ✅ Completed | React Authentication |
| Phase 05 | ⬜ Not Started | Project & Repository Management |
| Phase 06 | ⬜ Not Started | Analysis Job Queue (Redis + BullMQ) |
| Phase 07 | ⬜ Not Started | MS1 ↔ MS2 Job Communication |
| Phase 08 | ⬜ Not Started | Repository Storage & Retrieval |
| Phase 09 | ⬜ Not Started | Repository Parser |
| Phase 10 | ⬜ Not Started | Knowledge Graph Builder (Neo4j) |
| Phase 11 | ⬜ Not Started | LangGraph Planner Agent |
| Phase 12 | ⬜ Not Started | Docker Runner Service |
| Phase 13 | ⬜ Not Started | Dynamic Test Executor |
| Phase 14 | ⬜ Not Started | Reflection Agent |
| Phase 15 | ⬜ Not Started | Report Generator |
| Phase 16 | ⬜ Not Started | Webhook & Real-Time Progress Updates |
| Phase 17 | ⬜ Not Started | Report Viewer & Knowledge Graph UI |
| Phase 18 | ⬜ Not Started | Logging, Metrics & Observability |
| Phase 19 | ⬜ Not Started | Deployment & CI/CD |
| Phase 20 | ⬜ Not Started | Production Hardening & Performance |

---

# High-Level Dependency Graph

```
MS1 Foundation
        │
        ▼
Authentication
        │
        ▼
Frontend Authentication
        │
        ▼
Project & Repository Management
        │
        ▼
Analysis Queue
        │
        ▼
MS1 ↔ MS2 Communication
        │
        ▼
Repository Storage
        │
        ▼
Repository Parser
        │
        ▼
Knowledge Graph
        │
        ▼
Planner Agent
        │
        ▼
Docker Runner
        │
        ▼
Dynamic Test Execution
        │
        ▼
Reflection
        │
        ▼
Report Generation
        │
        ▼
Realtime Updates
        │
        ▼
Frontend Report Viewer
        │
        ▼
Observability
        │
        ▼
Deployment
        │
        ▼
Production Hardening
```

---

# Phase Categories

## Backend (MS1)

Responsible for:

- Authentication
- User Management
- Project Management
- Repository Metadata
- Analysis Jobs
- Report Management
- Queue Management
- Webhook Receiver

---

## AI Service (MS2)

Responsible for:

- Repository Parsing
- Static Analysis
- Knowledge Graph
- Planner Agent
- Docker Execution
- Reflection
- Report Generation

---

## Frontend

Responsible for:

- Authentication
- Dashboard
- Repository Upload
- Analysis Progress
- Knowledge Graph Viewer
- Report Viewer

---

## Infrastructure

Responsible for:

- Docker
- Redis
- PostgreSQL
- Neo4j
- NGINX
- HTTPS
- GitHub Actions
- OpenTelemetry
- AWS Deployment

---

# Team Ownership

| Member | Primary Responsibility |
|----------|------------------------|
| **Yash** | Express.js (MS1), PostgreSQL (MS1), Authentication, Projects, Reports, Queue APIs |
| **Sneha** | React Frontend, Authentication UI, Dashboard, Upload, Report Viewer, Progress UI |
| **Vansh** | FastAPI (MS2), PostgreSQL (MS2), Neo4j, LangGraph, AI Pipeline, Docker Execution |

---

# Development Rules

Each phase must:

- Have its own phase document.
- Define clear deliverables.
- Define allowed folders.
- Define allowed APIs.
- Define database changes.
- Define testing checklist.
- Define completion criteria.
- Define stop condition.

No implementation may continue into the next phase automatically.

---

# Completion Rule

A phase is considered complete only when:

- All deliverables are implemented.
- All APIs match `api-contracts.md`.
- Local testing passes.
- Existing functionality remains intact.
- `memory.md` is updated.
- `current-phase.md` points to the next phase.
- Changes are committed to Git.

---

# Branching Strategy

Every phase should be developed in its own Git branch.

Example

```
feature/phase-05-project-management

feature/phase-09-parser

feature/phase-13-dynamic-test-executor
```

Merge only after successful testing.

---

# AI Development Workflow

For every implementation session:

1. Read `architecture.md`
2. Read `tech-stack.md`
3. Read `schema.md`
4. Read `conventions.md`
5. Read `api-contracts.md`
6. Read `rules.md`
7. Read `memory.md`
8. Read `current-phase.md`
9. Open the referenced phase file.
10. Implement **only** the active phase.

Never implement future phases.

---

# Definition of Done

A phase is complete only when:

- Feature works end-to-end.
- Code follows project conventions.
- Documentation is updated.
- Tests pass.
- Git commit is created.
- Phase status is updated.
- AI stops automatically.

---

# Final Principle

**One phase. One responsibility. One commit.**

Small, isolated, testable phases produce a cleaner architecture, reduce merge conflicts, improve AI consistency, and make the project easier to maintain and scale.