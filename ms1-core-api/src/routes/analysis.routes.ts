import { Router } from 'express';
import { authMiddleware } from '../middleware/auth.middleware';
import {
  AnalysisController,
  startAnalysisValidation,
  analysisIdParamValidation,
} from '../controllers/analysis.controller';

const analysisRouter = Router();

// All analysis routes require JWT authentication
analysisRouter.use(authMiddleware);

// POST /api/analysis/start — Start an analysis job
analysisRouter.post('/start', startAnalysisValidation, AnalysisController.startAnalysis);

// GET /api/analysis/:analysisId/status — Get analysis status from PostgreSQL
analysisRouter.get(
  '/:analysisId/status',
  analysisIdParamValidation,
  AnalysisController.getAnalysisStatus
);

export default analysisRouter;
