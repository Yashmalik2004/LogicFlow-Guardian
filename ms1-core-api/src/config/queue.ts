import { Queue, ConnectionOptions } from 'bullmq';
import { env } from './env';
import { logger } from '../utils/logger';

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

export const ANALYSIS_QUEUE_NAME = 'AnalysisQueue';

let analysisQueue: Queue | null = null;

export function getAnalysisQueue(): Queue {
  if (!analysisQueue) {
    analysisQueue = new Queue(ANALYSIS_QUEUE_NAME, { connection });
    logger.info(`BullMQ queue "${ANALYSIS_QUEUE_NAME}" initialized.`);
  }
  return analysisQueue;
}
