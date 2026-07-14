import { env } from './config/env';
import { connectDatabase } from './config/database';
import { logger } from './utils/logger';
import { startAnalysisWorker } from './workers/analysis.worker';
import app from './app';

async function startServer(): Promise<void> {
  try {
    await connectDatabase();

    // Start background worker for analysis queue
    startAnalysisWorker();

    app.listen(env.PORT, () => {
      logger.info(`ms1-core-api running on port ${env.PORT} [${env.NODE_ENV}]`);
    });
  } catch (error) {
    logger.error('Failed to start server.', error);
    process.exit(1);
  }
}

startServer();

