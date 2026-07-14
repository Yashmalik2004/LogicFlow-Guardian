import dotenv from 'dotenv';

dotenv.config();

const requiredVars = ['PORT', 'DATABASE_URL', 'NODE_ENV'];

for (const key of requiredVars) {
  if (!process.env[key]) {
    throw new Error(`Missing required environment variable: ${key}`);
  }
}

export const env = {
  PORT: parseInt(process.env.PORT as string, 10),
  DATABASE_URL: process.env.DATABASE_URL as string,
  JWT_SECRET: process.env.JWT_SECRET as string,
  NODE_ENV: process.env.NODE_ENV as string,
  REDIS_URL: process.env.REDIS_URL || 'redis://localhost:6379',
};

