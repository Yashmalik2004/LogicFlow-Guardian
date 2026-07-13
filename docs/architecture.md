# System Architecture

## Overview

LogicFlow Guardian is an Agentic AI-powered Business Logic Security Testing Platform that analyzes application source code, infers business rules, generates intelligent security test cases, executes them automatically, and produces explainable vulnerability reports.

The platform follows a **microservice architecture** consisting of two independent backend services.

- **ms1 (Express.js)** – Core application service responsible for authentication, project management, report management, user interactions, and persistent application data.
- **ms2 (FastAPI)** – Dedicated AI service responsible for repository parsing, knowledge graph construction, LangGraph execution, business rule inference, security test generation, execution, reflection, and report generation.

The frontend communicates **only with ms1**. Whenever repository analysis is requested, ms1 delegates the analysis to ms2 through internal REST communication.

Each microservice owns its own persistence layer, ensuring clear separation of responsibilities and minimizing coupling between business logic and AI workflows.

---

# High-Level System Architecture

The following diagram illustrates the complete system architecture and communication between all major components.

![High Level Architecture](assets/architecture-imgs/hld/HLD.png)

---

# Component Responsibilities

The application is divided into independent components, each responsible for a well-defined domain.

| Component | Responsibility |
|-----------|----------------|
| React Frontend | User interface, authentication screens, repository submission, analysis progress, knowledge graph visualization, report viewing, and analysis history |
| ms1 – Express.js | Authentication, authorization, project management, repository management, report storage, API gateway, and communication with ms2 |
| ms2 – FastAPI | Repository parsing, LangGraph execution, AI reasoning, business rule extraction, knowledge graph generation, reflection, and report generation |
| PostgreSQL (ms1) | Stores users, projects, repositories, analysis jobs, reports, findings, and application metadata |
| PostgreSQL (ms2) | Stores analysis sessions, LangGraph execution state, reflection history, execution logs, and AI metadata |
| Neo4j (ms2) | Stores repository knowledge graphs and relationships between routes, controllers, middleware, services, models, and business rules |
| Docker | Containerization of all services |
| NGINX | Reverse proxy, HTTPS termination, and request routing |

---

# Database Ownership

LogicFlow Guardian follows the **Database-per-Service** microservice pattern.

Rather than sharing one database across multiple services, each microservice owns the data required for its own responsibilities.

---

## ms1 Database

The Express.js service owns all persistent application data.

Tables include:

- Users
- Projects
- Repository Metadata
- Analysis Jobs
- Reports
- Findings
- Authentication Sessions

These tables are accessed only through ms1.

---

## ms2 Databases

The FastAPI service owns all AI-specific information.

### Neo4j

Stores:

- Repository Knowledge Graph
- Route Relationships
- Controller Dependencies
- Middleware Flow
- Service Relationships
- Business Rules

### PostgreSQL

Stores:

- Analysis Sessions
- LangGraph State
- Planner Outputs
- Reflection History
- Execution Logs
- Temporary AI Metadata

These databases are private to ms2 and are never accessed directly by ms1.

---

# System Workflow

The overall application workflow begins when a user submits a repository for analysis and ends with the generation of an explainable security report.

![Stage 1: User Onboarding](assets/architecture-imgs/system%20workflow/workflow_stage1_user_onboarding.png)

![Stage 2: Repository Ingestion & Parsing](assets/architecture-imgs/system%20workflow/workflow_stage2_ingestion_parsing.png)

![Stage 3: Knowledge Graph & Agent Execution](assets/architecture-imgs/system%20workflow/workflow_stage3_agent_loop.png)

![Stage 4: Reflection & Report Delivery](assets/architecture-imgs/system%20workflow/workflow_stage4_reflection_delivery.png)

---

# Agent Architecture

The AI service consists of multiple specialized agents working together to understand the uploaded repository and generate intelligent business logic security tests.

Each agent performs one well-defined responsibility.

The pipeline consists of:

- Repository Parser
- Knowledge Graph Builder
- Planner Agent
- Test Executor
- Response Analyzer
- Reflection Agent
- Report Generator

The agents communicate through a shared LangGraph state object, enabling modular execution and reflection-based iteration.

![Part 1: Repository Ingestion & Planning](assets/architecture-imgs/agent%20worflow/agent_pipeline_part1_ingestion_planning.png)

![Part 2: Execution, Reflection & Reporting](assets/architecture-imgs/agent%20worflow/agent_pipeline_part2_execution_reporting.png)

---

# LangGraph Workflow

The AI workflow is implemented using LangGraph.

Each node performs one logical task before transferring control to the next node.

Unlike a traditional pipeline, LangGraph supports cyclic execution. If the Reflection Agent determines that additional test coverage is required, execution returns to the Planner Agent and continues until sufficient coverage has been achieved.

![Part 1: Planning Phase](assets/architecture-imgs/langGraph%20workflow/coverage_loop_part1_setup.png)

![Part 2: Reflection Loop](assets/architecture-imgs/langGraph%20workflow/coverage_loop_part2_decision.png)

---

# Repository Analysis Lifecycle

Every uploaded repository follows the same processing lifecycle.

The repository is cloned, parsed, transformed into a knowledge graph, analyzed by the AI agents, and finally converted into a structured vulnerability report.

![Repository Intake](assets/architecture-imgs/repo%20lifecycle/codebase_pipeline_part1_intake.png)

![Metadata Extraction & Test Planning](assets/architecture-imgs/repo%20lifecycle/codebase_pipeline_part2_extraction.png)

![Execution & Report Generation](assets/architecture-imgs/repo%20lifecycle/codebase_pipeline_part3_execution.png)

---

# Request Lifecycle

The frontend communicates exclusively with the Express.js API.

Express validates the request, creates an analysis job, and forwards the repository to the FastAPI AI service.

FastAPI performs the repository analysis, executes the LangGraph workflow, generates the security report, and returns the final findings to Express.

Express permanently stores the generated report inside its application database before returning the analysis status to the frontend.

Historical reports are therefore retrieved directly from ms1 without requiring the AI service to execute again.

![Part 1: Request Path](assets/architecture-imgs/request%20lifecycle/request_cycle_part1_request_path.png)

![Part 2: Processing & Response](assets/architecture-imgs/request%20lifecycle/request_cycle_part2_processing_response.png)

---

# Deployment Architecture

The platform is designed to run as containerized services on AWS EC2.

Each service executes inside its own Docker container.

NGINX serves as the reverse proxy, terminating HTTPS requests and routing traffic to the appropriate backend service.

The deployment architecture allows every component to scale independently while maintaining clear separation between business logic, AI processing, and data storage.

![Part 1: Ingress Layer](assets/architecture-imgs/deployment%20workflow/deployment_topology_part1_ingress.png)

![Part 2: Service & Data Layer](assets/architecture-imgs/deployment%20workflow/deployment_topology_part2_data_tier.png)

---

# Scalability

The architecture has been designed to support future enhancements without major structural changes.

Planned extensions include:

- Multi-language repository support
- Additional AI testing agents
- Runtime instrumentation
- Distributed task execution
- Kubernetes deployment
- Multi-tenant organizations
- Vector databases for GraphRAG
- Plugin-based vulnerability analyzers

---

# Architectural Principles

The following architectural principles guide the design of LogicFlow Guardian.

- Microservice architecture
- Database-per-Service design
- Separation of business logic and AI reasoning
- Stateless backend services
- Modular LangGraph nodes
- Explainable AI-generated findings
- Independent service scalability
- Containerized infrastructure
- Secure internal service communication
- Extensible agent pipeline
- Production-ready cloud deployment