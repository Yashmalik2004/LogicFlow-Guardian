# Phase 02 — MS2 Foundation

---

## Phase Information

| Property | Value |
|----------|-------|
| Phase | 02 |
| Milestone | Milestone 2 |
| Owner | Vansh |
| Estimated Time | 2–3 Hours |
| Branch | feature/phase-02-ms2-foundation |
| Status | Not Started |

---

# Objective

Build the foundational AI microservice using FastAPI.

This phase establishes the base FastAPI application, configuration, database connectivity, Neo4j connectivity, and internal health endpoint.

No AI logic should be implemented.

No repository parsing should be implemented.

No LangGraph should be implemented.

---

# Before Writing Code

Read the following documents in order.

1. architecture.md
2. tech-stack.md
3. schema.md
4. conventions.md
5. api-contracts.md
6. rules.md
7. roadmap.md
8. memory.md

Do not skip this order.

---

# Deliverables

Implement only the following.

- FastAPI application
- Python virtual environment support
- Dependency management
- Project folder structure
- Environment variable loading
- PostgreSQL connection
- Neo4j connection
- Global configuration module
- Internal Health API

Nothing else.

---

# Allowed Folders

Only these folders may be modified.

```
ms2-agent/

app/

agents/

graphs/

memory/

parser/

prompts/

reflection/

schemas/

tools/
```

No frontend.

No Express.

---

# Allowed Dependencies

Only install dependencies required for this phase.

Example

```
fastapi

uvicorn

python-dotenv

sqlalchemy

psycopg2-binary

neo4j

pydantic

alembic (optional if using migrations)
```

Do not install LangChain.

Do not install LangGraph.

Do not install OpenAI SDK.

Those belong to later phases.

---

# Database

Allowed

- Configure PostgreSQL connection
- Configure Neo4j connection

Not Allowed

- Create tables
- Run migrations
- Seed data
- AI metadata
- Analysis models

---

# APIs To Implement

```
GET /internal/health
```

Expected Response

```json
{
    "status": "OK",
    "service": "ms2-agent"
}
```

---

# Environment Variables

Create support for

```
FASTAPI_PORT

DATABASE_URL

NEO4J_URI

NEO4J_USERNAME

NEO4J_PASSWORD

PYTHON_ENV
```

Do not hardcode values.

---

# Out Of Scope

Do NOT implement

- Parser
- Endpoint discovery
- LangGraph
- Planner
- Executor
- Reflection
- Repository cloning
- OpenAI
- Business rule extraction
- AI agents
- REST communication with Express
- Authentication
- Docker

If any of these are implemented, this phase has exceeded scope.

---

# Folder Structure

Ensure the following structure exists.

```
ms2-agent

app/

agents/

graphs/

memory/

parser/

prompts/

reflection/

schemas/

tools/
```

Each folder should contain placeholder files if necessary.

---

# Success Criteria

The following must work.

✓ FastAPI starts successfully.

✓ Environment variables load.

✓ PostgreSQL connection succeeds.

✓ Neo4j connection succeeds.

✓ GET /internal/health returns HTTP 200.

✓ Folder structure follows conventions.md.

---

# Testing Checklist

Verify

- FastAPI starts.
- PostgreSQL connects.
- Neo4j connects.
- No dependency errors.
- Health endpoint responds.

---

# Expected Git Commit

Example

```
feat(ms2): initialize fastapi foundation
```

---

# Files Expected

Typical files created.

```
main.py

app.py

config.py

database.py

neo4j.py

requirements.txt

.env.example
```

Naming must follow conventions.md.

---

# Completion Checklist

- [ ] FastAPI initialized
- [ ] Folder structure completed
- [ ] Environment variables configured
- [ ] PostgreSQL connected
- [ ] Neo4j connected
- [ ] Health endpoint implemented
- [ ] Server tested locally
- [ ] Commit created
- [ ] memory.md updated

---

# Stop Condition

Once every checklist item is complete

1. Stop coding.
2. Do NOT begin Authentication.
3. Update memory.md.
4. Mark Phase 02 complete inside roadmap.md.
5. Change current-phase.md to Phase 03.
6. Commit changes.

Never continue automatically into the next phase.