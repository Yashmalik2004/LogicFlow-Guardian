import { Router } from 'express';
import { authMiddleware } from '../middleware/auth.middleware';
import {
  ProjectController,
  createProjectValidation,
  updateProjectValidation,
  projectIdParamValidation,
} from '../controllers/project.controller';

const projectRouter = Router();

// All project routes require JWT authentication
projectRouter.use(authMiddleware);

// POST /api/projects — Create a new project
projectRouter.post('/', createProjectValidation, ProjectController.createProject);

// GET /api/projects — List authenticated user's projects
projectRouter.get('/', ProjectController.listProjects);

// GET /api/projects/:id — Get a single project
projectRouter.get('/:id', projectIdParamValidation, ProjectController.getProject);

// PUT /api/projects/:id — Update a project
projectRouter.put('/:id', updateProjectValidation, ProjectController.updateProject);

// DELETE /api/projects/:id — Soft-delete a project
projectRouter.delete('/:id', projectIdParamValidation, ProjectController.deleteProject);

export default projectRouter;
