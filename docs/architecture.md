# System Architecture

## Overview

LogicFlow Guardian is an Agentic AI-powered Business Logic Security Testing Platform designed to analyze application source code, infer business rules, generate intelligent security tests, execute them, and produce explainable vulnerability reports.

The system follows a microservice architecture consisting of two backend services:

- **ms1 (Express.js)** – Handles authentication, project management, report management, and acts as the primary API consumed by the frontend.
- **ms2 (FastAPI)** – Dedicated AI service responsible for repository parsing, knowledge graph construction, LangGraph execution, business rule inference, security test generation, execution, reflection, and report generation.

The frontend communicates only with **ms1**, while **ms1** communicates internally with **ms2** whenever an analysis is requested.

---

# High-Level System Architecture

The overall architecture illustrates how each component communicates within the platform.

![High level design](assets/architecture-imgs/hld/HLD-architecture.png)

---

# Component Responsibilities

The platform is divided into independent components, each responsible for a specific part of the workflow.

| Component | Responsibility |
|-----------|----------------|
| React Frontend | User interface, authentication, repository submission, analysis progress, knowledge graph visualization, security reports |
| ms1 – Express.js | Authentication, project management, report management, database access, communication with ms2 |
| ms2 – FastAPI | AI workflow execution, repository parsing, LangGraph orchestration, report generation |
| PostgreSQL | Stores users, projects, analysis history, reports, findings, and application metadata |
| Neo4j | Stores repository knowledge graph and extracted relationships |
| Docker | Containerization of all services |
| NGINX | Reverse proxy, HTTPS termination, request routing |

---

# System Workflow

The system processes an uploaded repository through multiple stages before producing a vulnerability report.

![Stage 1: User onboarding](assets/architecture-imgs/system%20workflow/workflow_stage1_user_onboarding.png)
![Stage 2: Ingestion and parsing](assets/architecture-imgs/system%20workflow/workflow_stage2_ingestion_parsing.png)
![Stage 3: Knowledge graph and agent loop](assets/architecture-imgs/system%20workflow/workflow_stage3_agent_loop.png)
![Stage 4: Reflection and delivery](assets/architecture-imgs/system%20workflow/workflow_stage4_reflection_delivery.png)

---

# Agent Architecture

The AI service consists of multiple specialized agents that collaborate to understand the repository and generate meaningful security tests.

Each agent performs a single responsibility.

- Repository Parser
- Knowledge Graph Builder
- Planner Agent
- Test Executor
- Response Analyzer
- Reflection Agent
- Report Generator

These agents communicate through a shared LangGraph state, allowing the workflow to remain modular and extensible.

![Part 1: Ingestion and planning](assets/architecture-imgs/agent%20worflow/agent_pipeline_part1_ingestion_planning.png)
Once the plan is set, the remaining agents execute, analyze, reflect, and produce the final report.
Part 2: Execution and reporting
![Part 2: Execution and reporting](assets/architecture-imgs/agent%20worflow/agent_pipeline_part2_execution_reporting.png)

---

# LangGraph Workflow

The AI workflow is implemented using LangGraph as a deterministic state machine.

Each node performs one logical operation before passing execution to the next node.

Reflection may redirect execution back to the Planner whenever additional testing is required.

![Part 1: Setup through planning](assets/architecture-imgs/langGraph%20workflow/coverage_loop_part1_setup.png)
![Part 2: Execution, decision, and loop](assets/architecture-imgs/langGraph%20workflow/coverage_loop_part2_decision.png)

---

# Repository Analysis Lifecycle

Each repository uploaded by a user follows a fixed lifecycle.

The repository is cloned, parsed, transformed into a knowledge graph, analyzed using multiple AI agents, and finally converted into a structured security report.

![Part 1: Repository intake](assets/architecture-imgs/repo%20lifecycle/codebase_pipeline_part1_intake.png)
![Part 2: Extraction and test generation](assets/architecture-imgs/repo%20lifecycle/codebase_pipeline_part2_extraction.png)
![Part 3: Execution and reporting](assets/architecture-imgs/repo%20lifecycle/codebase_pipeline_part3_execution.png)

---

# Request Lifecycle

A repository analysis request travels through multiple services before returning the generated report to the user.

The frontend communicates only with the Express API, while AI operations remain isolated inside the FastAPI service.

![Part 1: Request path](assets/architecture-imgs/request%20lifecycle/request_cycle_part1_request_path.png)
![Part 2: Processing and response](assets/architecture-imgs/request%20lifecycle/request_cycle_part2_processing_response.png)

---

# Deployment Architecture

The platform is designed to run as independent Docker containers deployed on an AWS EC2 instance.

NGINX acts as the reverse proxy and HTTPS termination point, routing requests to the appropriate microservice.

![Part 1: Ingress and frontend](assets/architecture-imgs/deployment%20workflow/deployment_topology_part1_ingress.png)
![Part 2: AI service and data tier](assets/architecture-imgs/deployment%20workflow/deployment_topology_part2_data_tier.png)

---

# Scalability

The architecture has been designed to support future extensions without major structural changes.

Possible future enhancements include:

- Multi-language repository support
- Additional AI testing agents
- Kubernetes deployment
- Distributed task execution
- Multi-tenant organizations
- Runtime instrumentation
- Plugin-based vulnerability analyzers

---

# Architectural Principles

The following design principles are followed throughout the project.

- Separation of concerns using microservices
- AI isolated from business APIs
- Stateless backend services
- Modular LangGraph nodes
- Explainable AI-generated findings
- Extensible agent pipeline
- Production-ready deployment architecture
- Containerized infrastructure