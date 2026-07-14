# LogicFlow Guardian - Development Roadmap

## Purpose

This roadmap defines the complete implementation plan for **Milestone 2**.

Each phase represents a self-contained feature that can be implemented, tested, committed, and merged independently.

Only one phase should be active at any given time.

---

# Milestone 2

## Objective

Implement complete interaction between:

React Frontend

↓

Express.js (ms1)

↓

FastAPI (ms2)

↓

Basic AI Workflow

The milestone is considered complete when a user can:

- Register/Login
- Create a project
- Upload a repository
- Start analysis
- Trigger ms2
- Receive a dummy report
- View the report

---

# Development Phases

| Phase | Status | Description |
|--------|--------|-------------|
| Phase 01 | ✅ Completed | MS1 Foundation |
| Phase 02 | ✅ Completed | MS2 Foundation |
| Phase 03 | ✅ Completed | Authentication |
| Phase 04 | ✅ Completed | Frontend Authentication |
| Phase 05 | ⬜ Not Started | Project Management |
| Phase 06 | ⬜ Not Started | Repository Upload |
| Phase 07 | ⬜ Not Started | MS1 ↔ MS2 Communication |
| Phase 08 | ⬜ Not Started | Basic Agent |
| Phase 09 | ⬜ Not Started | Analysis Workflow |
| Phase 10 | ⬜ Not Started | Dummy Report |

---

# Dependency Graph

```
Phase 01
      │
      ▼
Phase 03
      │
      ▼
Phase 05
      │
      ▼
Phase 06
      │
      ▼
Phase 07
      │
      ▼
Phase 09
      │
      ▼
Phase 10
```

```
Phase 02
      │
      ▼
Phase 07
      │
      ▼
Phase 08
      │
      ▼
Phase 09
```

```
Phase 04
      │
      ▼
Phase 09
```

---

# Team Ownership

| Member | Responsibility |
|----------|---------------|
| Yash | Express.js (ms1), PostgreSQL (ms1), Authentication, Projects, Reports |
| Sneha | React Frontend |
| Vansh | FastAPI (ms2), PostgreSQL (ms2), Neo4j, AI Workflow |

---

# Phase Completion Rule

A phase is considered complete only when:

- All deliverables are implemented.
- Code builds successfully.
- APIs behave according to `api-contracts.md`.
- Documentation (`memory.md`) is updated.
- Changes are committed.

Only then should `current-phase.md` move to the next phase.

---

# Final Principle

Never implement two phases simultaneously.

Finish one completely before starting the next.