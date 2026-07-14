import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import { env } from '../config/env';
import { UserModel, User } from '../models/user.model';

export interface LoginResult {
  token: string;
  user: {
    userId: number;
    name: string;
    email: string;
  };
}

export class AuthService {
  /**
   * Register a new user.
   */
  static async registerUser(name: string, email: string, password: string): Promise<User> {
    // Check if email already exists
    const existingUser = await UserModel.findByEmail(email);
    if (existingUser) {
      const error = new Error('Email already registered');
      (error as any).statusCode = 409;
      throw error;
    }

    // Hash password
    const passwordHash = await bcrypt.hash(password, 10);

    // Create user
    const newUser = await UserModel.create({
      name,
      email,
      password_hash: passwordHash,
    });

    return newUser;
  }

  /**
   * Log in an existing user.
   */
  static async loginUser(email: string, password: string): Promise<LoginResult> {
    // Find user by email
    const user = await UserModel.findByEmail(email);
    if (!user) {
      const error = new Error('Invalid email or password');
      (error as any).statusCode = 401;
      throw error;
    }

    // Validate password
    const isPasswordValid = await bcrypt.compare(password, user.password_hash);
    if (!isPasswordValid) {
      const error = new Error('Invalid email or password');
      (error as any).statusCode = 401;
      throw error;
    }

    // Generate JWT
    const token = jwt.sign(
      {
        userId: user.user_id,
        name: user.name,
        email: user.email,
      },
      env.JWT_SECRET,
      { expiresIn: '24h' }
    );

    return {
      token,
      user: {
        userId: user.user_id!,
        name: user.name,
        email: user.email,
      },
    };
  }
}
