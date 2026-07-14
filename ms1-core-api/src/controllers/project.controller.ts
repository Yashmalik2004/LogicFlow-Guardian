import { Response } from 'express';
import { body, param, validationResult } from 'express-validator';
import { AuthenticatedRequest } from '../middleware/auth.middleware';
import { ProjectService } from '../services/project.service';
import { logger } from '../utils/logger';

// ---------------------------------------------------------------------------
// Validation Rules
// ---------------------------------------------------------------------------

export const createProjectValidation = [
  body('repoName')
    .trim()
    .notEmpty()
    .withMessage('repoName is required.')
    .isLength({ max: 100 })
    .withMessage('repoName must not exceed 100 characters.'),
  body('repositoryType')
    .notEmpty()
    .withMessage('repositoryType is required.')
    .isIn(['github', 'zip'])
    .withMessage('repositoryType must be "github" or "zip".'),
  body('repoUrl')
    .optional({ nullable: true })
    .isURL()
    .withMessage('repoUrl must be a valid URL.'),
  body('branch')
    .optional({ nullable: true })
    .trim()
    .isLength({ max: 100 })
    .withMessage('branch must not exceed 100 characters.'),
  body('description')
    .optional({ nullable: true })
    .trim()
    .isLength({ max: 500 })
    .withMessage('description must not exceed 500 characters.'),
];

export const updateProjectValidation = [
  param('id').isInt({ min: 1 }).withMessage('Project ID must be a positive integer.'),
  body('repoName')
    .optional()
    .trim()
    .notEmpty()
    .withMessage('repoName must not be empty if provided.')
    .isLength({ max: 100 })
    .withMessage('repoName must not exceed 100 characters.'),
  body('repoUrl')
    .optional({ nullable: true })
    .isURL()
    .withMessage('repoUrl must be a valid URL.'),
  body('branch')
    .optional({ nullable: true })
    .trim()
    .isLength({ max: 100 })
    .withMessage('branch must not exceed 100 characters.'),
  body('description')
    .optional({ nullable: true })
    .trim()
    .isLength({ max: 500 })
    .withMessage('description must not exceed 500 characters.'),
];

export const projectIdParamValidation = [
  param('id').isInt({ min: 1 }).withMessage('Project ID must be a positive integer.'),
];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function handleValidationErrors(req: AuthenticatedRequest, res: Response): boolean {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    res.status(400).json({
      success: false,
      message: 'Validation failed.',
      error: { fields: errors.array() },
    });
    return true;
  }
  return false;
}

// ---------------------------------------------------------------------------
// Controller
// ---------------------------------------------------------------------------

export class ProjectController {
  /**
   * POST /api/projects
   * Create a new project for the authenticated user.
   */
  static async createProject(req: AuthenticatedRequest, res: Response): Promise<void> {
    if (handleValidationErrors(req, res)) return;

    try {
      const userId = req.user!.userId;
      const { repoName, repoUrl, branch, description, repositoryType } = req.body;

      const project = await ProjectService.createProject(userId, {
        repoName,
        repoUrl,
        branch,
        description,
        repositoryType,
      });

      res.status(201).json({
        success: true,
        message: 'Project created successfully.',
        data: {
          projectId: project.project_id,
        },
      });
    } catch (error) {
      logger.error('ProjectController.createProject error:', error);
      res.status(500).json({
        success: false,
        message: 'Internal server error.',
        error: {},
      });
    }
  }

  /**
   * GET /api/projects
   * List all projects for the authenticated user.
   */
  static async listProjects(req: AuthenticatedRequest, res: Response): Promise<void> {
    try {
      const userId = req.user!.userId;
      const projects = await ProjectService.listProjects(userId);

      res.status(200).json({
        success: true,
        data: projects.map((p) => ({
          projectId: p.project_id,
          repoName: p.repo_name,
          repoUrl: p.repo_url,
          branch: p.branch,
          description: p.description,
          repositoryType: p.repository_type,
          status: p.status,
          createdAt: p.created_at,
          updatedAt: p.updated_at,
        })),
      });
    } catch (error) {
      logger.error('ProjectController.listProjects error:', error);
      res.status(500).json({
        success: false,
        message: 'Internal server error.',
        error: {},
      });
    }
  }

  /**
   * GET /api/projects/:id
   * Get a single project. Users cannot access other users' projects.
   */
  static async getProject(req: AuthenticatedRequest, res: Response): Promise<void> {
    if (handleValidationErrors(req, res)) return;

    try {
      const userId = req.user!.userId;
      const projectId = parseInt(String(req.params.id), 10);

      const result = await ProjectService.getProject(projectId, userId);

      if (result === null) {
        res.status(404).json({
          success: false,
          message: 'Project not found.',
          error: {},
        });
        return;
      }

      if (result === 'forbidden') {
        res.status(403).json({
          success: false,
          message: 'Forbidden: You do not have access to this project.',
          error: {},
        });
        return;
      }

      res.status(200).json({
        success: true,
        data: {
          projectId: result.project_id,
          repoName: result.repo_name,
          repoUrl: result.repo_url,
          branch: result.branch,
          description: result.description,
          repositoryType: result.repository_type,
          status: result.status,
          createdAt: result.created_at,
          updatedAt: result.updated_at,
        },
      });
    } catch (error) {
      logger.error('ProjectController.getProject error:', error);
      res.status(500).json({
        success: false,
        message: 'Internal server error.',
        error: {},
      });
    }
  }

  /**
   * PUT /api/projects/:id
   * Update a project. Only the owner may update.
   */
  static async updateProject(req: AuthenticatedRequest, res: Response): Promise<void> {
    if (handleValidationErrors(req, res)) return;

    try {
      const userId = req.user!.userId;
      const projectId = parseInt(String(req.params.id), 10);
      const { repoName, repoUrl, branch, description } = req.body;

      const result = await ProjectService.updateProject(projectId, userId, {
        repo_name: repoName,
        repo_url: repoUrl,
        branch,
        description,
      });

      if (result === null) {
        res.status(404).json({
          success: false,
          message: 'Project not found.',
          error: {},
        });
        return;
      }

      if (result === 'forbidden') {
        res.status(403).json({
          success: false,
          message: 'Forbidden: You do not have access to this project.',
          error: {},
        });
        return;
      }

      res.status(200).json({
        success: true,
        message: 'Project updated successfully.',
        data: {
          projectId: result.project_id,
          repoName: result.repo_name,
          repoUrl: result.repo_url,
          branch: result.branch,
          description: result.description,
          repositoryType: result.repository_type,
          status: result.status,
          createdAt: result.created_at,
          updatedAt: result.updated_at,
        },
      });
    } catch (error) {
      logger.error('ProjectController.updateProject error:', error);
      res.status(500).json({
        success: false,
        message: 'Internal server error.',
        error: {},
      });
    }
  }

  /**
   * DELETE /api/projects/:id
   * Soft-delete a project. Only the owner may delete.
   */
  static async deleteProject(req: AuthenticatedRequest, res: Response): Promise<void> {
    if (handleValidationErrors(req, res)) return;

    try {
      const userId = req.user!.userId;
      const projectId = parseInt(String(req.params.id), 10);

      const result = await ProjectService.deleteProject(projectId, userId);

      if (result === false) {
        res.status(404).json({
          success: false,
          message: 'Project not found.',
          error: {},
        });
        return;
      }

      if (result === 'forbidden') {
        res.status(403).json({
          success: false,
          message: 'Forbidden: You do not have access to this project.',
          error: {},
        });
        return;
      }

      res.status(200).json({
        success: true,
        message: 'Project deleted successfully.',
        data: {},
      });
    } catch (error) {
      logger.error('ProjectController.deleteProject error:', error);
      res.status(500).json({
        success: false,
        message: 'Internal server error.',
        error: {},
      });
    }
  }
}
