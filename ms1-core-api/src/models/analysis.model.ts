import { pool } from '../config/database';

export type AnalysisStatus = 'QUEUED' | 'PROCESSING' | 'DISPATCHED' | 'COMPLETED' | 'FAILED';

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
