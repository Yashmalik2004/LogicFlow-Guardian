import { Request, Response } from 'express';
import { env } from '../config/env';
import { AnalysisService, AnalysisStatusWebhookPayload } from '../services/analysis.service';
import { logger } from '../utils/logger';

export class WebhookController {
  /**
   * POST /internal/webhook/analysis-status
   *
   * Receives a status update callback from MS2 after each stage of the
   * repository intake pipeline. MS2 never writes to MS1's database directly —
   * all status transitions flow through this endpoint.
   *
   * Security: if MS2_WEBHOOK_SECRET is configured, the request must carry a
   * matching X-Webhook-Secret header. Requests without it are rejected 401.
   */
  static async receiveAnalysisStatus(req: Request, res: Response): Promise<void> {
    // Validate shared secret when it is configured
    if (env.MS2_WEBHOOK_SECRET) {
      const incomingSecret = req.headers['x-webhook-secret'];
      if (incomingSecret !== env.MS2_WEBHOOK_SECRET) {
        res.status(401).json({
          success: false,
          message: 'Unauthorized: invalid or missing webhook secret.',
          error: {},
        });
        return;
      }
    }

    const payload = req.body as AnalysisStatusWebhookPayload;

    // Basic validation
    if (!payload || typeof payload.analysisId !== 'number' || !payload.status) {
      res.status(400).json({
        success: false,
        message: 'Invalid webhook payload: analysisId and status are required.',
        error: {},
      });
      return;
    }

    logger.info(
      `[Webhook] Received status update — analysisId=${payload.analysisId} status=${payload.status}`
    );

    try {
      const updated = await AnalysisService.applyStatusUpdate(payload);

      if (!updated) {
        res.status(404).json({
          success: false,
          message: `Analysis ${payload.analysisId} not found.`,
          error: {},
        });
        return;
      }

      res.status(200).json({
        success: true,
        message: 'Status update applied.',
        data: {},
      });
    } catch (error) {
      logger.error('[Webhook] Failed to apply status update:', error);
      res.status(500).json({
        success: false,
        message: 'Internal server error while applying status update.',
        error: {},
      });
    }
  }
}
