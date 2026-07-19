import { pool } from '../config/database';

// Extend status to include the intake stages reported back by MS2 via webhook
export type AnalysisStatus =
  | 'QUEUED'
  | 'PROCESSING'
  | 'DISPATCHED'
  | 'CLONING'
  | 'VALIDATING'
  | 'READY_FOR_PARSING'
  | 'COMPLETED'
  | 'FAILED';

export interface Analysis {
  analysis_id?: number;
  project_id: number;
  user_id: number;
  bull_job_id: string | null;
  status: AnalysisStatus;
  queue_position: number | null;
  started_at: Date | null;
  completed_at: Date | null;
  created_at?: Date;
  updated_at?: Date;
}

export interface RepoMetadata {
  repository_path: string | null;
  repository_name: string | null;
  language: string | null;
  framework: string | null;
  repository_size: number | null;
}

export class AnalysisModel {
  /**
   * Insert a new Analysis record with QUEUED status.
   */
  static async create(projectId: number, userId: number): Promise<Analysis> {
    const query = `
      INSERT INTO "Analysis" (project_id, user_id, status)
      VALUES ($1, $2, 'QUEUED')
      RETURNING analysis_id, project_id, user_id, bull_job_id, status,
                queue_position, started_at, completed_at, created_at, updated_at;
    `;
    const { rows } = await pool.query(query, [projectId, userId]);
    return rows[0];
  }

  /**
   * Update the bull_job_id after the BullMQ job has been created.
   */
  static async setBullJobId(analysisId: number, bullJobId: string): Promise<void> {
    const query = `
      UPDATE "Analysis"
      SET bull_job_id = $1, updated_at = CURRENT_TIMESTAMP
      WHERE analysis_id = $2;
    `;
    await pool.query(query, [bullJobId, analysisId]);
  }

  /**
   * Update the status of an Analysis record.
   * Used by MS1's own worker and by the webhook handler when MS2 reports progress.
   */
  static async updateStatus(
    analysisId: number,
    status: AnalysisStatus,
    extras?: { started_at?: Date; completed_at?: Date }
  ): Promise<void> {
    const fields: string[] = ['status = $1', 'updated_at = CURRENT_TIMESTAMP'];
    const values: (string | Date | number)[] = [status];
    let idx = 2;

    if (extras?.started_at) {
      fields.push(`started_at = $${idx++}`);
      values.push(extras.started_at);
    }
    if (extras?.completed_at) {
      fields.push(`completed_at = $${idx++}`);
      values.push(extras.completed_at);
    }

    values.push(analysisId);
    const query = `
      UPDATE "Analysis"
      SET ${fields.join(', ')}
      WHERE analysis_id = $${idx};
    `;
    await pool.query(query, values);
  }

  /**
   * Persist repository intake metadata onto the Analysis record.
   * Called by MS1's webhook handler when MS2 reports the completed intake.
   * MS2 no longer writes this data directly — it sends it via webhook payload.
   */
  static async updateRepoMetadata(
    analysisId: number,
    metadata: RepoMetadata
  ): Promise<void> {
    const query = `
      UPDATE "Analysis"
      SET repository_path = $1,
          repository_name = $2,
          language        = $3,
          framework       = $4,
          repository_size = $5,
          updated_at      = CURRENT_TIMESTAMP
      WHERE analysis_id = $6;
    `;
    await pool.query(query, [
      metadata.repository_path,
      metadata.repository_name,
      metadata.language,
      metadata.framework,
      metadata.repository_size,
      analysisId,
    ]);
  }

  /**
   * Find a single Analysis by analysis_id.
   */
  static async findById(analysisId: number): Promise<Analysis | null> {
    const query = `
      SELECT analysis_id, project_id, user_id, bull_job_id, status,
             queue_position, started_at, completed_at, created_at, updated_at
      FROM "Analysis"
      WHERE analysis_id = $1;
    `;
    const { rows } = await pool.query(query, [analysisId]);
    return rows.length ? rows[0] : null;
  }
}
