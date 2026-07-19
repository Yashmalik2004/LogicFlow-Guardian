import express, { Application, Request, Response, NextFunction } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';

import healthRouter from './routes/health.routes';
import authRouter from './routes/auth.routes';
import projectRouter from './routes/project.routes';
import analysisRouter from './routes/analysis.routes';
import webhookRouter from './routes/webhook.routes';

const app: Application = express();

// Security middleware
app.use(helmet());

// CORS middleware
app.use(cors());

// HTTP request logger
app.use(morgan('dev'));

// JSON body parser
app.use(express.json());

// Public routes
app.use('/', healthRouter);
app.use('/api/auth', authRouter);
app.use('/api/projects', projectRouter);
app.use('/api/analysis', analysisRouter);

// Internal routes — not exposed publicly (should be firewalled in production)
// MS2 uses /internal/webhook/analysis-status to report status back to MS1
app.use('/internal/webhook', webhookRouter);

// 404 handler
app.use((req: Request, res: Response) => {
  res.status(404).json({
    success: false,
    message: 'Route not found.',
    error: {},
  });
});

// Global error handler
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  res.status(500).json({
    success: false,
    message: 'Internal server error.',
    error: { message: err.message },
  });
});

export default app;
