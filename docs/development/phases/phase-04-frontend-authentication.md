# Phase 04 — Frontend Authentication

---

# Phase Information

| Property | Value |
|----------|-------|
| Phase | 04 |
| Name | Frontend Authentication |
| Milestone | Milestone 2 |
| Owner | Sneha |
| Branch | feature/phase-04-frontend-authentication |
| Status | Not Started |
| Estimated Time | 3–4 Hours |

---

# Objective

Build the frontend authentication flow using React.

This phase connects the React frontend with the Express.js authentication APIs created in Phase 03.

Users should be able to register, login, remain authenticated using JWT, and access protected pages.

No project functionality should be implemented.

---

# Before Writing Code

Read the following documents in order.

1. docs/architecture.md
2. docs/tech-stack.md
3. docs/schema.md
4. docs/conventions.md
5. docs/api-contracts.md
6. docs/rules.md
7. docs/development/roadmap.md
8. docs/development/memory.md
9. docs/development/current-phase.md

Follow them exactly.

---

# Deliverables

Implement ONLY the following.

## Pages

Create

```
Login Page

Register Page
```

using the approved wireframes.

---

## Authentication

Implement

- Login form
- Register form
- JWT storage
- Logout
- Authentication context
- Protected routes

---

## API Integration

Connect only to

```
POST /api/auth/register

POST /api/auth/login

GET /api/auth/me
```

Do not call any other APIs.

---

## Routing

Implement

```
/

→ Login

/register

→ Register

/dashboard

→ Protected
```

Dashboard is only a placeholder page.

---

# Allowed Folders

Only modify

```
frontend/
```

Allowed folders

```
app/

components/

lib/

styles/
```

Do not modify

```
ms1-core-api

ms2-agent
```

---

# Allowed Libraries

Install only if required.

```
react-router-dom

axios

jwt-decode
```

No UI component libraries.

No Tailwind.

No Material UI.

Keep the UI simple.

---

# JWT Handling

After successful login

Store JWT

```
localStorage
```

Attach JWT to future requests using

```
Authorization: Bearer <token>
```

---

# Protected Routes

Unauthenticated users

↓

Redirect to

```
/login
```

Authenticated users

↓

Allow access

```
/dashboard
```

---

# Dashboard

Only display

```
Welcome

Logged in successfully.

Logout Button
```

No projects.

No upload.

No analysis.

---

# Validation

Validate

Email

- Required
- Valid email

Password

- Required

Display backend validation errors.

---

# Out Of Scope

Do NOT implement

- Repository Upload
- Project CRUD
- Analysis Dashboard
- Reports
- Knowledge Graph
- AI Workflow
- Progress Page
- Settings
- GitHub URL
- ZIP Upload
- Theme switching

Only authentication.

---

# Folder Structure

Suggested additions

```
frontend

app/

pages/

Login.jsx

Register.jsx

Dashboard.jsx

components/

AuthForm.jsx

ProtectedRoute.jsx

contexts/

AuthContext.jsx

services/

authService.js

hooks/

useAuth.js
```

Follow conventions.md.

---

# Success Criteria

The following must work.

✓ User registers.

✓ User logs in.

✓ JWT stored.

✓ Refresh keeps user logged in.

✓ Protected routes work.

✓ Logout clears JWT.

✓ Unauthorized users cannot access dashboard.

---

# Testing Checklist

Verify

- Register user.
- Login.
- JWT stored.
- Refresh page.
- Still logged in.
- Logout.
- Redirect to login.
- Access dashboard without JWT → Redirect.

---

# Expected Git Commit

Example

```
feat(frontend): implement authentication flow
```

---

# Completion Checklist

- [ ] Login page created
- [ ] Register page created
- [ ] Auth context created
- [ ] JWT storage implemented
- [ ] Protected routes implemented
- [ ] Logout implemented
- [ ] APIs integrated
- [ ] Authentication tested
- [ ] memory.md updated
- [ ] Commit created

---

# Stop Condition

Once every checklist item is complete

1. Stop coding immediately.
2. Do NOT begin Phase 05.
3. Update memory.md.
4. Mark Phase 04 complete in roadmap.md.
5. Update current-phase.md to Phase 05.
6. Commit changes.

Never continue automatically.