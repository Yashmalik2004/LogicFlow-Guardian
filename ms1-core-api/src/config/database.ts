import { Pool } from 'pg';
import { env } from './env';
import { logger } from '../utils/logger';

export const pool = new Pool({
  connectionString: env.DATABASE_URL,
});

export async function connectDatabase(): Promise<void> {
  const client = await pool.connect();
  try {
    await client.query('SELECT 1');
    logger.info('PostgreSQL connection established successfully.');
  } finally {
    client.release();
  }
}
