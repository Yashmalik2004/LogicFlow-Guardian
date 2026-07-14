# Phase 05B — Frontend Project Dashboard

## Objective

Implement the Project Dashboard UI using the existing Project Management APIs developed in Phase 05.

This phase transforms the backend CRUD APIs into a usable frontend experience.

No repository uploads or AI functionality are included.

---

# Scope

Build only the project management interface.

Users should be able to:

- View projects
- Create projects
- Edit projects
- Delete projects

Do NOT implement analysis.

Do NOT implement repository uploads.

Do NOT implement progress tracking.

---

# Pages

## Dashboard

Authenticated users land on the Dashboard after login.

The page displays:

- Welcome message
- Logged-in user
- Project list
- Create Project button
- Logout button

---

## Create Project Modal

Fields:

Project Name

Repository Type

- GitHub
- ZIP

GitHub URL

Default Branch

Description

Buttons

- Create
- Cancel

Validation errors should be displayed.

---

## Edit Project Modal

Allow editing:

- Project Name
- GitHub URL
- Default Branch
- Description

Repository Type cannot be changed.

---

## Delete Confirmation

Display confirmation dialog.

Example

Delete project

Bank API

This action cannot be undone.

Buttons

Cancel

Delete

---

# Components

Create reusable components.

Suggested structure

components/

ProjectCard.jsx

ProjectList.jsx

CreateProjectModal.jsx

EditProjectModal.jsx

DeleteProjectModal.jsx

DashboardHeader.jsx

EmptyState.jsx

LoadingSpinner.jsx

ErrorBanner.jsx

---

# Pages

Suggested structure

pages/

Dashboard.jsx

---

# Services

Create API layer.

lib/

projectService.js

Responsibilities

- getProjects()

- createProject()

- updateProject()

- deleteProject()

Never call fetch directly inside components.

---

# API Usage

GET

/api/projects

↓

Populate dashboard

---

POST

/api/projects

↓

Create project

↓

Refresh list

---

PUT

/api/projects/:id

↓

Update project

↓

Refresh list

---

DELETE

/api/projects/:id

↓

Delete project

↓

Refresh list

---

# State Management

Manage:

- Projects
- Loading
- Errors
- Modal state
- Selected project

React Context is optional.

Component state is acceptable.

Do not introduce Redux.

---

# UI Behaviour

Dashboard initially shows

Loading...

↓

Project list

If no projects exist

Display

"No projects found."

with

Create Project

button.

---

# Validation

Project Name

Required

Repository Type

Required

GitHub URL

Validate if Repository Type == GitHub

Description

Optional

Branch

Defaults to

main

---

# Navigation

After login

↓

Dashboard

Users remain on Dashboard after CRUD operations.

No navigation to analysis pages.

---

# Folder Scope

Modify only

frontend/

app/

components/

lib/

styles/

Do not modify

ms1-core-api/

ms2-agent/

infra/

---

# Testing Checklist

✓ Login redirects to Dashboard

✓ Dashboard loads projects

✓ Empty state works

✓ Create Project works

✓ Edit Project works

✓ Delete Project works

✓ Validation messages displayed

✓ Loading indicators displayed

✓ Error handling implemented

✓ Logout still works

---

# Success Criteria

The following workflow must succeed.

Login

↓

Dashboard

↓

Fetch Projects

↓

Create Project

↓

Display New Project

↓

Edit Project

↓

Update Dashboard

↓

Delete Project

↓

Project Removed

Everything communicates only with MS1.

No MS2 interaction occurs.

---

# Completion Checklist

- Dashboard created
- Project list implemented
- CRUD modals completed
- API service layer created
- Loading states implemented
- Empty state implemented
- Validation completed
- Existing authentication still works
- memory.md updated

Stop after completion.

Do not continue to Phase 06.