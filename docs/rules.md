# LogicFlow Guardian AI Development Rules

## Purpose

This document defines how any AI assistant (ChatGPT, Claude, Gemini, Cursor, Windsurf, Copilot, etc.) must contribute to the LogicFlow Guardian codebase.

The goal is to ensure that all AI-generated code follows the same architecture, coding standards, and development workflow regardless of which AI model is used.

---

# Mandatory Reading Order

Before writing any code, ALWAYS read these documents in the following order:

1. architecture.md
2. tech-stack.md
3. schema.md (if database changes are involved)
4. milestones.md
5. current-phase.md
6. memory.md

Never skip this order.

---

# Primary Objective

Your objective is NOT to finish the entire project.

Your objective is ONLY to complete the currently active phase defined inside:

docs/current-phase.md

Nothing more.

---

# Scope Rules

Only implement the requirements explicitly listed in the current phase.

Never implement future milestones.

Never anticipate future features.

Never "helpfully" add functionality that has not been requested.

If authentication is scheduled for a later phase,
DO NOT create authentication code.

If Docker is scheduled later,
DO NOT create Docker configuration.

Stay strictly within the current scope.

---

# Stop Condition

Once every deliverable listed in current-phase.md has been completed:

1. Stop writing code.
2. Do not continue into the next phase.
3. Update memory.md.
4. Summarize your work.

Never continue automatically.

---

# Architecture Rules

Follow the architecture defined in architecture.md.

Never modify the system architecture unless explicitly instructed.

Maintain separation between:

- Frontend
- ms1 (Express)
- ms2 (FastAPI)
- Infrastructure

Never merge responsibilities between services.

---

# Coding Standards

## General

- Write clean production-quality code.
- Use meaningful names.
- Keep functions small.
- Avoid duplicated logic.
- Use descriptive variable names.
- Use consistent formatting.

---

## Express (ms1)

Use:

- Controllers
- Services
- Middleware
- Routes
- Config
- Utils

Business logic belongs inside Services.

Controllers should remain thin.

---

## FastAPI (ms2)

Organize code into:

- Agents
- Graphs
- Prompts
- Tools
- Schemas
- Parser
- Reflection
- Memory

Each module should have a single responsibility.

---

## React

Keep components:

- Small
- Reusable
- Typed

Avoid large monolithic components.

---

# Database Rules

Every database interaction must go through the application's data access layer.

Never execute raw queries inside controllers.

Never mix database logic with business logic.

---

# API Rules

Frontend communicates ONLY with ms1.

ms1 communicates with ms2.

Frontend must never directly call ms2.

---

# Git Rules

Generate code suitable for small commits.

Avoid modifying unrelated files.

Do not perform unnecessary refactoring.

Keep changes localized to the current phase.

---

# Documentation Rules

Whenever a phase is completed:

Update memory.md.

Include:

- Completed work
- Files created
- Files modified
- Architectural decisions
- Remaining tasks
- Known issues (if any)

Do not modify milestones.md unless explicitly instructed.

Do not modify architecture.md unless architecture changes.

---

# Error Handling

Never silently ignore errors.

Always:

- Validate inputs.
- Return meaningful errors.
- Log important failures.

---

# Dependencies

Only install dependencies required for the current phase.

Do not introduce libraries that are not immediately needed.

---

# Security Rules

Never:

- Hardcode secrets
- Hardcode API keys
- Commit credentials
- Disable security checks

Always use environment variables.

---

# Before Finishing

Before ending the session verify:

✓ All deliverables are complete.

✓ Project builds successfully.

✓ Existing functionality is not broken.

✓ memory.md has been updated.

✓ No future milestone has been implemented.

Then stop.

---

# Final Rule

When in doubt,

build LESS rather than MORE.

It is always preferable to stop early than to implement features from future phases.