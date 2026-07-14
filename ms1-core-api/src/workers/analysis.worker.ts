import { Worker, Job, ConnectionOptions } from 'bullmq';
import { env } from '../config/env';
import { ANALYSIS_QUEUE_NAME } from '../config/queue';
import { AnalysisModel } from '../models/analysis.model';
import { dispatchAnalysisToMs2 } from '../services/dispatch.service';
import { logger } from '../utils/logger';

export interface AnalysisJobData {
  analysisId: number;
  projectId: number;
  userId: number;
}

const connection: ConnectionOptions = {
  host: (() => {
    try {
      return new URL(env.REDIS_URL).hostname;
    } catch {
      return 'localhost';
    }
  })(),
  port: (() => {
    try {
      return parseInt(new URL(env.REDIS_URL).port || '6379', 10);
    } catch {
      return 6379;
    }
  })(),
};

async function processAnalysisJob(job: Job<AnalysisJobData>): Promise<void> {
  const { analysisId, projectId, userId } = job.data;

  logger.info(
    `Worker Started — analysisId=${analysisId} projectId=${projectId} userId=${userId}`
  );

  // Mark as PROCESSING
  await AnalysisModel.updateStatus(analysisId, 'PROCESSING', {
    started_at: new Date(),
  });

  logger.info(`[Worker] Analysis ${analysisId} — Status: PROCESSING`);

  // Dispatch to MS2 — implements retry + timeout logic internally
  await dispatchAnalysisToMs2({ analysisId, projectId, userId });

  // Mark as DISPATCHED after successful ACK from MS2
  await AnalysisModel.updateStatus(analysisId, 'DISPATCHED');

  logger.info(`[Worker] Analysis ${analysisId} — Status: DISPATCHED`);
}

let worker: Worker | null = null;

export function startAnalysisWorker(): void {
  if (worker) return;

  worker = new Worker<AnalysisJobData>(
    ANALYSIS_QUEUE_NAME,
    processAnalysisJob,
    { connection, concurrency: 5 }
  );

  worker.on('completed', (job) => {
    logger.info(`[Worker] Job ${job.id} completed for analysisId=${job.data.analysisId}`);
  });

  worker.on('failed', async (job, err) => {
    if (job) {
      logger.error(`[Worker] Job ${job.id} failed for analysisId=${job.data.analysisId}:`, err);
      try {
        await AnalysisModel.updateStatus(job.data.analysisId, 'FAILED');
      } catch (dbErr) {
        logger.error('[Worker] Failed to update Analysis status to FAILED:', dbErr);
      }
    }
  });

  logger.info('[Worker] AnalysisWorker started and listening for jobs.');
}
