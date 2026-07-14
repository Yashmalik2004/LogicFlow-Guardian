import { Response } from 'express';
import { validationResult } from 'express-validator';
import { AuthService } from '../services/auth.service';
import { AuthenticatedRequest } from '../middleware/auth.middleware';

export class AuthController {
  /**
   * Handle user registration.
   */
  static async register(req: AuthenticatedRequest, res: Response): Promise<Response | void> {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: 'Validation failed.',
        error: errors.mapped(),
      });
    }

    const { name, email, password } = req.body;

    try {
      const user = await AuthService.registerUser(name, email, password);
      return res.status(201).json({
        success: true,
        message: 'User registered successfully.',
        data: {
          userId: user.user_id,
        },
      });
    } catch (error: any) {
      const statusCode = error.statusCode || 500;
      return res.status(statusCode).json({
        success: false,
        message: error.message || 'Internal server error.',
        error: {},
      });
    }
  }

  /**
   * Handle user login.
   */
  static async login(req: AuthenticatedRequest, res: Response): Promise<Response | void> {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: 'Validation failed.',
        error: errors.mapped(),
      });
    }

    const { email, password } = req.body;

    try {
      const result = await AuthService.loginUser(email, password);
      return res.status(200).json({
        success: true,
        message: 'Login successful.',
        data: {
          token: result.token,
          user: result.user,
        },
      });
    } catch (error: any) {
      const statusCode = error.statusCode || 500;
      return res.status(statusCode).json({
        success: false,
        message: error.message || 'Internal server error.',
        error: {},
      });
    }
  }

  /**
   * Get authenticated current user info.
   */
  static async me(req: AuthenticatedRequest, res: Response): Promise<Response> {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        message: 'Unauthorized',
        error: {},
      });
    }

    return res.status(200).json({
      success: true,
      data: {
        userId: req.user.userId,
        name: req.user.name,
        email: req.user.email,
      },
    });
  }
}
