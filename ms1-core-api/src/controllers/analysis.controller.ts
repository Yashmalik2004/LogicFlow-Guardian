import { Response } from 'express';
import { body, param, validationResult } from 'express-validator';
import { AuthenticatedRequest } from '../middleware/auth.middleware';
import { AnalysisService } from '../services/analysis.service';
import { logger } from '../utils/logger';

// ---------------------------------------------------------------------------
// Validation Rules
// ---------------------------------------------------------------------------

export const startAnalysisValidation = [
  body('projectId')
    .notEmpty()
    .withMessage('projectId is required.')
    .isInt({ min: 1 })
    .withMessage('projectId must be a positive integer.'),
];

export const analysisIdParamValidation = [
  param('analysisId')
    .isInt({ min: 1 })
    .withMessage('analysisId must be a positive integer.'),
];

// ---------------------------------------------------------------------------
// Helper
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

export class AnalysisController {
  /**
   * POST /api/analysis/start
   * Start an analysis for a project. Returns immediately with analysisId and status.
   */
  static async startAnalysis(req: AuthenticatedRequest, res: Response): Promise<void> {
    if (handleValidationErrors(req, res)) return;

    try {
      const userId = req.user!.userId;
      const projectId = parseInt(String(req.body.projectId), 10);

      const result = await AnalysisService.startAnalysis(projectId, userId);

      if (result === 'not_found') {
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

      res.status(201).json({
        success: true,
        message: 'Analysis started.',
        data: {
          analysisId: result.analysis_id,
          status: result.status,
        },
      });
    } catch (error) {
      const err = error as Error;
      if (err.message === 'SERVICE_UNAVAILABLE') {
        res.status(503).json({
          success: false,
          message: 'Analysis queue is currently unavailable. Please try again later.',
          error: {},
        });
        return;
      }
      if (err.message === 'QUEUE_FAILURE') {
        res.status(500).json({
          success: false,
          message: 'Failed to queue analysis job.',
          error: {},
        });
        return;
      }
      logger.error('AnalysisController.startAnalysis error:', error);
      res.status(500).json({
        success: false,
        message: 'Internal server error.',
        error: {},
      });
    }
  }

  /**
   * GET /api/analysis/:analysisId/status
   * Retrieve the current status of an analysis from PostgreSQL.
   */
  static async getAnalysisStatus(req: AuthenticatedRequest, res: Response): Promise<void> {
    if (handleValidationErrors(req, res)) return;

    try {
      const userId = req.user!.userId;
      const analysisId = parseInt(String(req.params.analysisId), 10);

      const result = await AnalysisService.getAnalysisStatus(analysisId, userId);

      if (result === null) {
        res.status(404).json({
          success: false,
          message: 'Analysis not found.',
          error: {},
        });
        return;
      }

      if (result === 'forbidden') {
        res.status(403).json({
          success: false,
          message: 'Forbidden: You do not have access to this analysis.',
          error: {},
        });
        return;
      }

      res.status(200).json({
        success: true,
        data: {
          analysisId: result.analysis_id,
          projectId: result.project_id,
          status: result.status,
          startedAt: result.started_at,
          completedAt: result.completed_at,
          createdAt: result.created_at,
        },
      });
    } catch (error) {
      logger.error('AnalysisController.getAnalysisStatus error:', error);
      res.status(500).json({
        success: false,
        message: 'Internal server error.',
        error: {},
      });
    }
  }
}
