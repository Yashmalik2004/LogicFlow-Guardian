# Phase 08 — Repository Intake & Storage

## Objective

Implement the repository intake layer.

This phase is responsible for obtaining the repository associated with an analysis request and storing it inside the platform's controlled workspace.

After this phase, every analysis should have a local repository path ready for future parsing.

No repository analysis should occur.

---

# Purpose

The AI cannot analyze code that does not exist locally.

This phase prepares repositories for later phases.

Workflow

Analysis Request

↓

Receive Repository Information

↓

Validate Repository Source

↓

Clone or Extract Repository

↓

Store Repository

↓

Update Database

↓

Ready For Parser

---

# Scope

Implement:

- GitHub repository cloning
- ZIP archive extraction
- Repository workspace creation
- Repository metadata updates
- Repository validation
- Cleanup on failure

Do NOT implement:

- Parser
- Knowledge Graph
- LangGraph
- AI
- Docker
- Dynamic execution

---

# Repository Sources

Support two repository types.

## GitHub

Clone using Git.

Store inside

workspace/

repositories/

<analysisId>/

---

## ZIP Upload

Accept uploaded ZIP archive.

Extract into

workspace/

repositories/

<analysisId>/

Delete ZIP after extraction.

---

# Repository Workspace

All repositories should be stored outside the application source code.

Example

workspace/

repositories/

42/

bank-api/

package.json

src/

README.md

Never clone into

ms1/

ms2/

frontend/

---

# Database

Extend ANALYSIS

Add

repository_path

repository_name

repository_type

repository_status

Suggested status values

PENDING

CLONING

READY

FAILED

---

# Repository Validation

For GitHub

Validate

Repository URL

↓

Reachable

↓

Clone succeeds

For ZIP

Validate

ZIP exists

↓

Extract succeeds

↓

Contains project files

Reject empty archives.

---

# GitHub Cloning

Use Git.

Do NOT execute shell commands directly from controllers.

Create

RepositoryService

Responsibilities

- Clone repository
- Validate repository
- Return local path

---

# ZIP Extraction

Create

ZipService

Responsibilities

- Validate archive
- Extract archive
- Delete temporary archive
- Return repository path

---

# Workspace Structure

Example

workspace/

repositories/

analysis-42/

repository/

package.json

src/

README.md

logs/

Temporary files should never remain after failure.

---

# Error Handling

Git clone failure

↓

repository_status

FAILED

↓

Analysis

FAILED

↓

Log error

Invalid ZIP

↓

Reject

↓

400 Bad Request

Workspace creation failure

↓

500 Internal Server Error

Cleanup partially created directories.

---

# Logging

Log

Repository Intake Started

↓

Workspace Created

↓

Repository Cloned

or

ZIP Extracted

↓

Repository Ready

↓

Database Updated

↓

Phase Complete

---

# Architecture Notes

Repository storage belongs entirely to MS2.

MS1 never accesses repository files.

MS1 only stores metadata.

Future phases receive

repository_path

from ANALYSIS.

---

# Security Rules

Reject

Private repositories without credentials.

Reject

Unsupported repository URLs.

Reject

Archives larger than configured limit.

Prevent

Zip Slip attacks.

Normalize extraction paths.

Never overwrite existing repositories.

---

# Folder Scope

Modify

ms2-agent/

app/

tools/

services/

config/

schemas/

workspace/

Database migrations

Do not modify

frontend/

infra/

---

# Testing Checklist

✓ GitHub repository cloned

✓ ZIP repository extracted

✓ Workspace created

✓ Repository path stored

✓ Repository status updated

✓ Invalid repositories rejected

✓ Cleanup works

✓ Existing MS1 ↔ MS2 communication still works

---

# Success Criteria

Workflow

User

↓

Create Analysis

↓

Queue

↓

MS2

↓

Clone Repository

or

Extract ZIP

↓

Store Repository

↓

Update ANALYSIS

repository_status

READY

↓

Ready for Parser

No repository parsing occurs.

---

# Completion Checklist

- Repository cloning implemented
- ZIP extraction implemented
- Workspace structure implemented
- Repository metadata stored
- Database updated
- Validation completed
- Error handling completed
- Logging completed
- Existing functionality still works
- memory.md updated

Stop immediately after completion.

Do not continue to Phase 09.