import { Worker, Job, ConnectionOptions } from 'bullmq';
import { env } from '../config/env';
import { ANALYSIS_QUEUE_NAME } from '../config/queue';
import { AnalysisModel } from '../models/analysis.model';
import { dispatchAnalysisToMs2 } from '../services/dispatch.service';
import { logger } from '../utils/logger';

/**
 * Full job data shape stored in BullMQ.
 *
 * Includes all project metadata required by MS2 so that MS2 never needs to
 * query MS1's database. MS1 fetches this data before enqueueing.
 */
export interface AnalysisJobData {
  analysisId: number;
  projectId: number;
  userId: number;
  // Project metadata — forwarded to MS2 in the dispatch payload
  repoUrl: string;
  repoName: string;
  branch: string;
  repositoryType: 'github' | 'zip';
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
  const { analysisId, projectId, userId, repoUrl, repoName, branch, repositoryType } = job.data;

  logger.info(
    `Worker Started — analysisId=${analysisId} projectId=${projectId} userId=${userId}`
  );

  // Mark as PROCESSING
  await AnalysisModel.updateStatus(analysisId, 'PROCESSING', {
    started_at: new Date(),
  });

  logger.info(`[Worker] Analysis ${analysisId} — Status: PROCESSING`);

  // Dispatch to MS2 — pass the full payload so MS2 never queries MS1's database.
  // Implements retry + timeout logic internally.
  await dispatchAnalysisToMs2({
    analysisId,
    projectId,
    userId,
    repoUrl,
    repoName,
    branch,
    repositoryType,
  });

  // Mark as DISPATCHED after successful ACK from MS2.
  // Further status updates (CLONING, VALIDATING, etc.) arrive via webhook from MS2.
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
