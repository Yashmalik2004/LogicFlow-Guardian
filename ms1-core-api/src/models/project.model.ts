import { pool } from '../config/database';

export interface Project {
  project_id?: number;
  user_id: number;
  repo_name: string;
  repo_url: string | null;
  branch: string;
  description: string | null;
  repository_type: 'github' | 'zip';
  status: string;
  created_at?: Date;
  updated_at?: Date;
}

export interface CreateProjectInput {
  user_id: number;
  repo_name: string;
  repo_url?: string | null;
  branch?: string;
  description?: string | null;
  repository_type: 'github' | 'zip';
}

export interface UpdateProjectInput {
  repo_name?: string;
  description?: string | null;
  repo_url?: string | null;
  branch?: string;
}

export class ProjectModel {
  /**
   * Insert a new project into the Project table.
   */
  static async create(input: CreateProjectInput): Promise<Project> {
    const query = `
      INSERT INTO "Project" (user_id, repo_name, repo_url, branch, description, repository_type, status)
      VALUES ($1, $2, $3, $4, $5, $6, 'ACTIVE')
      RETURNING project_id, user_id, repo_name, repo_url, branch, description, repository_type, status, created_at, updated_at;
    `;
    const values = [
      input.user_id,
      input.repo_name,
      input.repo_url ?? null,
      input.branch ?? 'main',
      input.description ?? null,
      input.repository_type,
    ];
    const { rows } = await pool.query(query, values);
    return rows[0];
  }

  /**
   * Find all active projects owned by a user.
   */
  static async findAllByUser(userId: number): Promise<Project[]> {
    const query = `
      SELECT project_id, user_id, repo_name, repo_url, branch, description, repository_type, status, created_at, updated_at
      FROM "Project"
      WHERE user_id = $1 AND status != 'DELETED'
      ORDER BY created_at DESC;
    `;
    const { rows } = await pool.query(query, [userId]);
    return rows;
  }

  /**
   * Find a single project by project_id.
   */
  static async findById(projectId: number): Promise<Project | null> {
    const query = `
      SELECT project_id, user_id, repo_name, repo_url, branch, description, repository_type, status, created_at, updated_at
      FROM "Project"
      WHERE project_id = $1 AND status != 'DELETED';
    `;
    const { rows } = await pool.query(query, [projectId]);
    return rows.length ? rows[0] : null;
  }

  /**
   * Update a project's editable fields.
   */
  static async update(projectId: number, input: UpdateProjectInput): Promise<Project | null> {
    const fields: string[] = [];
    const values: (string | null | undefined)[] = [];
    let paramIndex = 1;

    if (input.repo_name !== undefined) {
      fields.push(`repo_name = $${paramIndex++}`);
      values.push(input.repo_name);
    }
    if (input.description !== undefined) {
      fields.push(`description = $${paramIndex++}`);
      values.push(input.description);
    }
    if (input.repo_url !== undefined) {
      fields.push(`repo_url = $${paramIndex++}`);
      values.push(input.repo_url);
    }
    if (input.branch !== undefined) {
      fields.push(`branch = $${paramIndex++}`);
      values.push(input.branch);
    }

    if (fields.length === 0) return null;

    fields.push(`updated_at = CURRENT_TIMESTAMP`);

    const query = `
      UPDATE "Project"
      SET ${fields.join(', ')}
      WHERE project_id = $${paramIndex}
      RETURNING project_id, user_id, repo_name, repo_url, branch, description, repository_type, status, created_at, updated_at;
    `;
    values.push(String(projectId));
    const { rows } = await pool.query(query, values);
    return rows.length ? rows[0] : null;
  }

  /**
   * Soft delete a project by setting status to 'DELETED'.
   */
  static async softDelete(projectId: number): Promise<boolean> {
    const query = `
      UPDATE "Project"
      SET status = 'DELETED', updated_at = CURRENT_TIMESTAMP
      WHERE project_id = $1 AND status != 'DELETED';
    `;
    const { rowCount } = await pool.query(query, [projectId]);
    return (rowCount ?? 0) > 0;
  }
}
