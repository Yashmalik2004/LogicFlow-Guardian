# Phase 08 — Repository Intake & Storage

## Objective

Implement the complete repository intake pipeline.

MS2 should receive an analysis request, clone the GitHub repository into a dedicated workspace, validate the repository, detect its technology stack, and persist metadata required for future analysis.

This phase prepares repositories for parsing.

No AI analysis is performed.

---

# Purpose

Every analysis begins with obtaining a local copy of the repository.

Future phases will operate exclusively on this cloned workspace.

Workflow

Analysis Request

↓

GitHub Repository

↓

Clone Repository

↓

Validate Structure

↓

Detect Language & Framework

↓

Store Metadata

↓

Ready For Parsing

---

# Scope

Implement only

- Repository cloning
- Workspace management
- Repository validation
- Language detection
- Framework detection
- Repository metadata storage

Do NOT implement

- Repository parsing
- Knowledge graph
- Business rule extraction
- LangGraph
- Docker
- Dynamic execution
- Report generation

---

# Folder Scope

Modify

ms2-agent/

- app
- services
- tools
- parser (only repository discovery)
- schemas
- config

Database models

Do NOT modify

frontend/

infra/

---

# Repository Workspace

Create a workspace directory

```
/workspace/
```

Each analysis should create

```
workspace/

└── analysis-{analysisId}/
```

Example

```
workspace/

└── analysis-42/
```

The cloned repository should be stored here.

---

# Repository Cloning

Clone using the GitHub URL received from MS1.

Supported repositories

- Public GitHub repositories

Private repositories are out of scope.

Do not support ZIP uploads.

---

# Validation

After cloning

Verify

- Repository cloned successfully
- Git metadata exists
- Files are readable
- Repository is not empty

If validation fails

Update analysis status

FAILED

Return appropriate error.

---

# Repository Discovery

Detect

Programming Language

Examples

- JavaScript
- TypeScript
- Python
- Java
- Go

Framework

Examples

- Express
- FastAPI
- Spring Boot
- Django
- Flask

Detection should rely on common project files.

Examples

Node

package.json

Python

requirements.txt

pyproject.toml

Java

pom.xml

build.gradle

Go

go.mod

Do NOT parse source code.

Only inspect project metadata.

---

# Database

Extend ANALYSIS

Add nullable fields

- repository_path
- repository_name
- language
- framework
- repository_size

Store detected information.

---

# Repository Service

Create

RepositoryIntakeService

Responsibilities

- Clone repository
- Validate repository
- Detect language
- Detect framework
- Update database

Single responsibility only.

---

# Analysis Status

Extend status values

Current

- QUEUED
- PROCESSING
- DISPATCHED
- COMPLETED
- FAILED

Add

- CLONING
- VALIDATING
- READY_FOR_PARSING

Do not add parsing-related statuses yet.

---

# Logging

Log

Repository cloning started

↓

Repository cloned

↓

Validation successful

↓

Language detected

↓

Framework detected

↓

Repository ready

---

# Error Handling

Repository not found

↓

404

Invalid GitHub URL

↓

400

Git clone failure

↓

FAILED

Unsupported repository

↓

FAILED

Workspace creation failure

↓

500

---

# Business Rules

One analysis owns one cloned repository.

Each analysis has its own isolated workspace.

Repositories are never shared between analyses.

Existing workspaces should not be reused.

---

# Security

Clone only from GitHub.

Reject invalid URLs.

Never execute repository code.

Never install dependencies.

Never run scripts.

Only download files.

---

# Testing Checklist

✓ Public repository cloned successfully

✓ Workspace created

✓ Metadata stored

✓ Language detected

✓ Framework detected

✓ Invalid repository rejected

✓ Missing repository handled

✓ Analysis status updated correctly

✓ Existing queue and dispatch continue working

---

# Success Criteria

Workflow

User

↓

Start Analysis

↓

MS1 Queue

↓

MS2

↓

Clone Repository

↓

Validate Repository

↓

Detect Language

↓

Detect Framework

↓

Update Analysis

↓

READY_FOR_PARSING

No source code parsing occurs.

---

# Completion Checklist

- Workspace implemented
- Repository cloning implemented
- Validation completed
- Language detection implemented
- Framework detection implemented
- Metadata stored
- Logging completed
- Error handling completed
- Existing functionality still works
- memory.md updated

Stop immediately after completion.

Do not continue to Phase 09.