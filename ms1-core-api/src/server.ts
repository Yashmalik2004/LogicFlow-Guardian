import { env } from './config/env';
import { connectDatabase } from './config/database';
import { logger } from './utils/logger';
import app from './app';

async function startServer(): Promise<void> {
  try {
    await connectDatabase();

    app.listen(env.PORT, () => {
      logger.info(`ms1-core-api running on port ${env.PORT} [${env.NODE_ENV}]`);
    });
  } catch (error) {
    logger.error('Failed to start server.', error);
    process.exit(1);
  }
}

startServer();
