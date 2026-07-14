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

    // Create the "User" table if it doesn't exist
    await client.query(`
      CREATE TABLE IF NOT EXISTS "User" (
        user_id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
      );
    `);

    // Create the "Project" table if it doesn't exist
    await client.query(`
      CREATE TABLE IF NOT EXISTS "Project" (
        project_id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES "User"(user_id) ON DELETE CASCADE,
        repo_name VARCHAR(100) NOT NULL,
        repo_url VARCHAR(2048),
        branch VARCHAR(100) NOT NULL DEFAULT 'main',
        description VARCHAR(500),
        repository_type VARCHAR(10) NOT NULL CHECK (repository_type IN ('github', 'zip')),
        status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
      );
    `);

    // Create the "Analysis" table if it doesn't exist
    await client.query(`
      CREATE TABLE IF NOT EXISTS "Analysis" (
        analysis_id SERIAL PRIMARY KEY,
        project_id INTEGER NOT NULL REFERENCES "Project"(project_id) ON DELETE CASCADE,
        user_id INTEGER NOT NULL REFERENCES "User"(user_id) ON DELETE CASCADE,
        bull_job_id VARCHAR(255),
        status VARCHAR(30) NOT NULL DEFAULT 'QUEUED',
        queue_position INTEGER,
        started_at TIMESTAMP WITH TIME ZONE,
        completed_at TIMESTAMP WITH TIME ZONE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
      );
    `);

    logger.info('Database tables verified/created successfully.');
  } catch (error) {
    logger.error('Database initialization failed:', error);
    throw error;
  } finally {
    client.release();
  }
}
