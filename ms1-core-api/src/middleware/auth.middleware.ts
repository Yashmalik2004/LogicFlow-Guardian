import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import { env } from '../config/env';

export interface AuthenticatedRequest extends Request {
  user?: {
    userId: number;
    name: string;
    email: string;
  };
}

export function authMiddleware(req: AuthenticatedRequest, res: Response, next: NextFunction) {
  const authHeader = req.headers.authorization;
  if (!authHeader) {
    return res.status(401).json({
      success: false,
      message: 'Unauthorized: No token provided.',
      error: {},
    });
  }

  // Handle "Bearer <token>" or raw "<token>"
  let token = authHeader;
  if (authHeader.startsWith('Bearer ')) {
    token = authHeader.substring(7);
  }

  try {
    const decoded = jwt.verify(token, env.JWT_SECRET) as {
      userId: number;
      name: string;
      email: string;
    };

    req.user = {
      userId: decoded.userId,
      name: decoded.name,
      email: decoded.email,
    };

    next();
  } catch (error) {
    return res.status(401).json({
      success: false,
      message: 'Unauthorized: Invalid or expired token.',
      error: {},
    });
  }
}
