# LogicFlow Guardian - API Contracts

## Purpose

This document defines every REST API used throughout the project.

These contracts are frozen before implementation.

Frontend, Express (ms1), and FastAPI (ms2) must strictly follow these contracts.

---

# API Overview

```
React
   │
   ▼
Express (ms1)
   │
   ▼
FastAPI (ms2)
```

Frontend communicates ONLY with Express.

Express communicates ONLY with FastAPI.

FastAPI is never publicly accessible.

---

# Common Response Format

## Success

```json
{
  "success": true,
  "message": "Operation completed successfully.",
  "data": {}
}
```

---

## Error

```json
{
  "success": false,
  "message": "Something went wrong.",
  "error": {}
}
```

Every endpoint must follow this format.

---

# Authentication APIs

---

## Register User

### Endpoint

```
POST /api/auth/register
```

### Authentication

No

### Request

```json
{
  "name": "Yash Malik",
  "email": "yash@example.com",
  "password": "Password123"
}
```

### Response

```json
{
  "success": true,
  "message": "User registered successfully.",
  "data": {
    "userId": 1
  }
}
```

---

## Login

```
POST /api/auth/login
```

### Authentication

No

### Request

```json
{
  "email": "yash@example.com",
  "password": "Password123"
}
```

### Response

```json
{
  "success": true,
  "message": "Login successful.",
  "data": {
    "token": "jwt-token",
    "user": {
      "userId": 1,
      "name": "Yash Malik",
      "email": "yash@example.com"
    }
  }
}
```

---

## Current User

```
GET /api/auth/me
```

Authentication

JWT

Response

```json
{
  "success": true,
  "data": {
    "userId": 1,
    "name": "Yash Malik",
    "email": "yash@example.com"
  }
}
```

---

# Project APIs

---

## Create Project

```
POST /api/projects
```

Authentication

JWT

Request

```json
{
  "repoName": "Bank API",
  "repoUrl": "https://github.com/example/bank-api",
  "branch": "main"
}
```

Response

```json
{
  "success": true,
  "message": "Project created successfully.",
  "data": {
    "projectId": 101
  }
}
```

---

## Get Projects

```
GET /api/projects
```

Authentication

JWT

Response

```json
{
  "success": true,
  "data": [
    {
      "projectId": 101,
      "repoName": "Bank API",
      "status": "Completed"
    }
  ]
}
```

---

## Get Single Project

```
GET /api/projects/{projectId}
```

Authentication

JWT

---

## Delete Project

```
DELETE /api/projects/{projectId}
```

Authentication

JWT

---

# Repository Upload APIs

---

## Upload Repository

```
POST /api/projects/{projectId}/upload
```

Authentication

JWT

Content-Type

```
multipart/form-data
```

Accepted

- ZIP

or

GitHub URL

Request

```
repository.zip

or

repoUrl
```

Response

```json
{
  "success": true,
  "message": "Repository uploaded successfully."
}
```

---

# Analysis APIs

---

## Start Analysis

```
POST /api/analysis/start
```

Authentication

JWT

Request

```json
{
  "projectId": 101
}
```

Response

```json
{
  "success": true,
  "message": "Analysis started.",
  "data": {
    "analysisId": 5001
  }
}
```

---

## Analysis Status

```
GET /api/analysis/{analysisId}
```

Authentication

JWT

Response

```json
{
  "success": true,
  "data": {
    "status": "Running",
    "progress": 70,
    "currentStage": "Planner"
  }
}
```

---

## Cancel Analysis

```
POST /api/analysis/{analysisId}/cancel
```

Authentication

JWT

---

# Report APIs

---

## List Reports

```
GET /api/reports
```

Authentication

JWT

---

## Get Report

```
GET /api/reports/{reportId}
```

Authentication

JWT

---

## Download Report

```
GET /api/reports/{reportId}/download
```

Authentication

JWT

Returns

PDF

---

## Get Findings

```
GET /api/reports/{reportId}/findings
```

Authentication

JWT

---

# Knowledge Graph APIs

---

## Get Knowledge Graph

```
GET /api/projects/{projectId}/graph
```

Authentication

JWT

Response

Graph JSON

---

# Internal APIs (Express ↔ FastAPI)

These APIs are never exposed publicly.

---

## Health Check

```
GET /internal/health
```

Response

```json
{
  "status": "OK"
}
```

---

## Start AI Analysis

```
POST /internal/analyze
```

Request

```json
{
  "analysisId": 5001,
  "projectId": 101,
  "repoPath": "/uploads/project.zip"
}
```

Response

```json
{
  "status": "received"
}
```

---

## Analysis Progress

```
GET /internal/analysis/{analysisId}
```

Response

```json
{
  "analysisId": 5001,
  "status": "Running",
  "progress": 75,
  "currentStage": "Reflection"
}
```

---

## Submit Final Report

```
POST /internal/report
```

Request

```json
{
  "analysisId": 5001,
  "summary": {},
  "findings": []
}
```

Response

```json
{
  "status": "stored"
}
```

---

## Get Knowledge Graph

```
GET /internal/graph/{analysisId}
```

Returns

Knowledge Graph JSON

---

# HTTP Status Codes

| Status | Meaning |
|---------|----------|
| 200 | Success |
| 201 | Resource Created |
| 400 | Validation Error |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict |
| 422 | Invalid Request |
| 500 | Internal Server Error |

---

# Authentication Rules

Public APIs

- Register
- Login

Require JWT

- Projects
- Analysis
- Reports
- Knowledge Graph

Internal APIs

No JWT

Accessible only inside Docker network.

---

# Ownership

| Module | Owner |
|---------|--------|
| Authentication APIs | ms1 |
| Project APIs | ms1 |
| Report APIs | ms1 |
| Analysis APIs | ms1 |
| Internal AI APIs | ms2 |
| Knowledge Graph APIs | ms2 |

---

# API Version

Current Version

```
v1
```

Future versions

```
/api/v2
```

must not break existing contracts.

---

# Contract Rule

No developer or AI assistant may change an endpoint, request body, response body, or status code without updating this document first.

This document is the single source of truth for all REST communication.