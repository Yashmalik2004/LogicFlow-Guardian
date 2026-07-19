import { Router } from 'express';
import { WebhookController } from '../controllers/webhook.controller';

const webhookRouter = Router();

/**
 * POST /internal/webhook/analysis-status
 *
 * Internal endpoint — NOT exposed publicly.
 * MS2 calls this to report Analysis status transitions back to MS1.
 * MS1 then updates its own Analysis table.
 *
 * Authentication: X-Webhook-Secret header (validated in WebhookController).
 */
webhookRouter.post('/analysis-status', WebhookController.receiveAnalysisStatus);

export default webhookRouter;
