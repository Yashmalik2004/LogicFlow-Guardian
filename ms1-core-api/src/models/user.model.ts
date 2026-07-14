import { pool } from '../config/database';

export interface User {
  user_id?: number;
  name: string;
  email: string;
  password_hash: string;
  created_at?: Date;
}

export class UserModel {
  /**
   * Insert a new user into the User table.
   */
  static async create(user: Omit<User, 'user_id' | 'created_at'>): Promise<User> {
    const query = `
      INSERT INTO "User" (name, email, password_hash)
      VALUES ($1, $2, $3)
      RETURNING user_id, name, email, password_hash, created_at;
    `;
    const values = [user.name, user.email, user.password_hash];
    const { rows } = await pool.query(query, values);
    return rows[0];
  }

  /**
   * Find a user by email.
   */
  static async findByEmail(email: string): Promise<User | null> {
    const query = `
      SELECT user_id, name, email, password_hash, created_at
      FROM "User"
      WHERE email = $1;
    `;
    const { rows } = await pool.query(query, [email]);
    return rows.length ? rows[0] : null;
  }

  /**
   * Find a user by user_id.
   */
  static async findById(userId: number): Promise<User | null> {
    const query = `
      SELECT user_id, name, email, password_hash, created_at
      FROM "User"
      WHERE user_id = $1;
    `;
    const { rows } = await pool.query(query, [userId]);
    return rows.length ? rows[0] : null;
  }
}
