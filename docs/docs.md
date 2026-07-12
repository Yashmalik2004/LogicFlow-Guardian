# 📚 LogicFlow Guardian Documentation

Welcome to the documentation directory for **LogicFlow Guardian**.

This folder contains all project design documents, architectural diagrams, wireframes, schemas, and planning artifacts created throughout the development lifecycle.

The documentation is intended to provide a complete understanding of the project's architecture, technology decisions, development roadmap, and system design before implementation.

---

# 📁 Documentation Structure

| Document | Description |
|-----------|-------------|
| `architecture.md` | High-level system architecture, workflows, agent design, deployment topology, and system interactions. |
| `tech-stack.md` | Complete technology stack used throughout the project with justification for each technology. |
| `milestones.md` | Development roadmap divided into five milestones from design to production deployment. |
| `schema.pdf` | Database schema and entity relationship diagrams used by the application. |
| `wireframes.md` | Low-fidelity application wireframes illustrating the planned user interface and navigation flow. |

---

# 🖼️ Assets

The **assets** directory contains all diagrams and visual documentation referenced throughout the project.

```
assets/
│
├── architecture-imgs/
└── wireframe-imgs/
```

---

# 🏗️ Architecture Diagrams

The `architecture-imgs` folder contains diagrams describing different aspects of the system architecture.

---

## High-Level Architecture

```
architecture-imgs/
└── hld/
```

Illustrates the overall software architecture including:

- React Frontend
- Express.js Core API (ms1)
- FastAPI AI Service (ms2)
- PostgreSQL
- Neo4j
- Service communication

---

## System Workflow

```
architecture-imgs/
└── system workflow/
```

Describes the complete end-to-end workflow from user login to report generation.

Includes:

- User interaction
- Repository ingestion
- AI execution
- Report delivery

---

## Agent Workflow

```
architecture-imgs/
└── agent workflow/
```

Illustrates how multiple AI agents collaborate during repository analysis.

Agents include:

- Repository Parser
- Knowledge Graph Builder
- Planner
- Test Executor
- Response Analyzer
- Reflection Agent
- Report Generator

---

## LangGraph Workflow

```
architecture-imgs/
└── langGraph workflow/
```

Shows the internal LangGraph state machine including:

- Planning
- Execution
- Reflection
- Coverage validation
- Report generation

---

## Repository Lifecycle

```
architecture-imgs/
└── repo lifecycle/
```

Explains the lifecycle of an uploaded repository from cloning through parsing, knowledge graph generation, testing, and report creation.

---

## Request Lifecycle

```
architecture-imgs/
└── request lifecycle/
```

Illustrates how requests move through the system:

```
React
    ↓
Express
    ↓
FastAPI
    ↓
Database
    ↓
Frontend
```

---

## Deployment Workflow

```
architecture-imgs/
└── deployment workflow/
```

Describes the production deployment architecture including:

- Docker
- NGINX
- AWS EC2
- PostgreSQL
- Neo4j

---

# 🎨 Wireframes

```
assets/
└── wireframe-imgs/
```

Contains the low-fidelity UI wireframes for the application.

Included screens:

- Login
- Dashboard
- New Analysis
- Analysis Progress
- Knowledge Graph
- Security Report

These wireframes represent the application's navigation flow and information hierarchy before frontend implementation.

---

# 📖 Reading Order

For someone exploring the project for the first time, the recommended reading order is:

1. **README.md** *(Project Overview)*
2. **milestones.md**
3. **tech-stack.md**
4. **architecture.md**
5. **schema.pdf**
6. **wireframes.md**

This sequence provides a gradual understanding of the project from high-level objectives to implementation details.

---

# 📌 Current Status

The documentation currently represents **Milestone 1 – Project Design & Architecture**.

Completed:

- Repository Structure
- Software Architecture
- Technology Stack
- Development Roadmap
- Database Schema
- UI Wireframes
- System Workflows
- Agent Design

Future milestones will progressively add implementation details, deployment documentation, testing reports, and production monitoring.

---

# 📄 Purpose

The documentation serves as the project's single source of truth and ensures that every team member follows a consistent architecture, technology stack, folder structure, and development workflow throughout the implementation lifecycle.