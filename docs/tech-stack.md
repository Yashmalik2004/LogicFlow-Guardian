# Technology Stack

## Overview

LogicFlow Guardian is built as a modern microservice-based web application with an agentic AI architecture. The system separates business logic, artificial intelligence, frontend, infrastructure, and deployment into independent components to improve scalability, maintainability, and modularity.

The project follows a monorepo architecture consisting of:

- React Frontend
- Express.js Core API (ms1)
- FastAPI AI Service (ms2)
- PostgreSQL
- Neo4j
- LangGraph
- Docker-based deployment

---

# Technology Overview

| Layer | Technology | Purpose |
|---------|------------|---------|
| Frontend | React.js | User Interface |
| Language | TypeScript | Type-safe frontend and backend development |
| Backend API | Express.js | Core application API |
| AI Service | FastAPI | AI Agent Service |
| AI Framework | LangGraph | Agent orchestration |
| LLM Framework | LangChain | Tool and LLM integration |
| Database | PostgreSQL | Primary relational database |
| Knowledge Graph | Neo4j | Repository relationship graph |
| Authentication | JWT | Secure authentication |
| Password Hashing | bcrypt | Password encryption |
| Reverse Proxy | NGINX | HTTPS and request routing |
| Containerization | Docker | Service isolation |
| Local Development | Docker Compose | Multi-container orchestration |
| Cloud Deployment | AWS EC2 | Hosting |
| CI/CD | GitHub Actions | Automated deployment |
| Monitoring | OpenTelemetry | Distributed tracing |
| Visualization | React Flow (Future) | Knowledge Graph visualization |

---

# Frontend

## React.js

### Purpose

React provides the complete user interface of LogicFlow Guardian.

### Responsibilities

- Authentication
- Dashboard
- Repository Upload
- Analysis Progress
- Knowledge Graph Visualization
- Security Report
- Report History

### Why React?

- Large ecosystem
- Component-based architecture
- Easy integration with REST APIs
- Excellent developer experience
- Strong community support

---

## TypeScript

### Purpose

Provides static typing for frontend and backend code.

### Why TypeScript?

- Compile-time error detection
- Better IDE support
- Safer refactoring
- Easier maintenance

---

# Backend

## Express.js (ms1)

### Purpose

Acts as the application's core API service.

### Responsibilities

- User Authentication
- JWT Management
- Project Management
- Repository Management
- Report Management
- Communication with FastAPI
- Database Operations

### Why Express?

- Lightweight
- Flexible routing
- Mature ecosystem
- Excellent TypeScript support
- Easy integration with PostgreSQL

---

## FastAPI (ms2)

### Purpose

Dedicated AI service.

### Responsibilities

- Repository Parsing
- LangGraph Execution
- Knowledge Graph Construction
- Security Test Planning
- Test Execution
- Reflection
- Report Generation

### Why FastAPI?

- High performance
- Native Python ecosystem
- Excellent LangGraph compatibility
- Automatic OpenAPI documentation
- Asynchronous processing

---

# Artificial Intelligence

## LangGraph

### Purpose

Coordinates the AI workflow as a deterministic graph.

### Responsibilities

- Agent orchestration
- State management
- Reflection loops
- Workflow execution

### Why LangGraph?

- Native support for agentic workflows
- Built-in state management
- Reflection support
- Cyclic execution
- Production-ready architecture

---

## LangChain

### Purpose

Provides tools for interacting with Large Language Models.

### Responsibilities

- Prompt execution
- Tool integration
- Document loading
- Embedding generation

---

# Database Layer

## PostgreSQL

### Purpose

Primary relational database.

### Stores

- Users
- Projects
- Repository Metadata
- Analysis Jobs
- Reports
- Findings
- Requirements

### Why PostgreSQL?

- ACID compliance
- Excellent performance
- JSON support
- Mature ecosystem

---

## Neo4j

### Purpose

Stores repository relationships as a graph.

### Stores

- Routes
- Controllers
- Services
- Middleware
- Models
- Business Rules
- Dependencies

### Why Neo4j?

Business logic vulnerabilities are relationship-based rather than purely relational. A graph database allows the AI agents to traverse dependencies and infer workflows more naturally.

---

# Authentication

## JWT

### Purpose

Stateless authentication.

### Responsibilities

- Login
- Session validation
- Protected routes

---

## bcrypt

### Purpose

Secure password hashing.

---

# Infrastructure

## Docker

### Purpose

Containerization of every service.

### Containers

- React
- Express
- FastAPI
- PostgreSQL
- Neo4j
- NGINX

---

## Docker Compose

### Purpose

Local development.

Runs every service using one command.

```bash
docker compose up
```

---

## NGINX

### Purpose

Reverse proxy.

### Responsibilities

- HTTPS
- Request routing
- Static file serving
- Load balancing (future)

---

# Cloud

## AWS EC2

### Purpose

Production deployment.

Hosts:

- React
- Express
- FastAPI
- PostgreSQL
- Neo4j

---

# CI/CD

## GitHub Actions

### Responsibilities

- Lint
- Build
- Testing
- Docker Image Build
- Deployment

Triggered on:

- Push to main
- Pull Requests

---

# Monitoring

## OpenTelemetry

### Responsibilities

Trace the entire analysis workflow.

```
Repository Upload
        ↓
Repository Parsing
        ↓
Knowledge Graph
        ↓
Planner
        ↓
Executor
        ↓
Reflection
        ↓
Report
```

Future integrations:

- Jaeger
- Grafana

---

# Development Tools

| Tool | Purpose |
|------|---------|
| Git | Version Control |
| GitHub | Source Code Hosting |
| VS Code | Development IDE |
| Postman | API Testing |
| Excalidraw | Architecture Diagrams |
| Figma | Wireframes |

---

# Future Technologies

The following technologies may be integrated in future versions.

- Redis (Job Queue / Cache)
- RabbitMQ (Distributed Tasks)
- Kubernetes
- Prometheus
- Grafana
- S3 Object Storage
- Elasticsearch
- Vector Database for RAG

---

# Final Stack Summary

| Category | Technology |
|-----------|------------|
| Frontend | React.js + TypeScript |
| Backend | Express.js + TypeScript |
| AI Service | FastAPI |
| Agent Framework | LangGraph |
| LLM Framework | LangChain |
| Database | PostgreSQL |
| Graph Database | Neo4j |
| Authentication | JWT + bcrypt |
| Containerization | Docker |
| Local Development | Docker Compose |
| Reverse Proxy | NGINX |
| Cloud | AWS EC2 |
| CI/CD | GitHub Actions |
| Monitoring | OpenTelemetry |