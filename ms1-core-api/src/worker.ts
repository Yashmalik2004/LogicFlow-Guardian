import { connectDatabase } from './config/database';
import { logger } from './utils/logger';
import { startAnalysisWorker } from './workers/analysis.worker';

async function startWorker(): Promise<void> {
  try {
    await connectDatabase();
    startAnalysisWorker();
    logger.info('Background worker process started.');
  } catch (error) {
    logger.error('Failed to start background worker.', error);
    process.exit(1);
  }
}

startWorker();
