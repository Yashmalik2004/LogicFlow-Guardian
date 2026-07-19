import { AnalysisModel, Analysis } from '../models/analysis.model';
import { ProjectModel } from '../models/project.model';
import { getAnalysisQueue } from '../config/queue';
import { AnalysisJobData } from '../workers/analysis.worker';
import { logger } from '../utils/logger';

// ---------------------------------------------------------------------------
// Webhook payload shape sent from MS2 → POST /internal/webhook/analysis-status
// ---------------------------------------------------------------------------

export interface AnalysisStatusWebhookPayload {
  analysisId: number;
  status: string;
  // Optional metadata populated when status reaches READY_FOR_PARSING
  repositoryPath?: string | null;
  repositoryName?: string | null;
  language?: string | null;
  framework?: string | null;
  repositorySize?: number | null;
  errorMessage?: string | null;
}

export class AnalysisService {
  /**
   * Start an analysis for a project.
   *
   * Fetches all required project data from MS1's own database and places a
   * BullMQ job carrying the full payload so the worker can dispatch it to MS2
   * without MS2 ever needing to query MS1's database.
   *
   * Returns the created Analysis or 'not_found' / 'forbidden' sentinel values.
   */
  static async startAnalysis(
    projectId: number,
    userId: number
  ): Promise<Analysis | 'not_found' | 'forbidden'> {
    // Verify project exists and is owned by this user
    const project = await ProjectModel.findById(projectId);
    if (!project) return 'not_found';
    if (project.user_id !== userId) return 'forbidden';

    // Create the Analysis record in the database (status = QUEUED)
    const analysis = await AnalysisModel.create(projectId, userId);
    logger.info(`Analysis Created — analysisId=${analysis.analysis_id} projectId=${projectId}`);

    // Enqueue the BullMQ job
    let queue;
    try {
      queue = getAnalysisQueue();
    } catch (err) {
      logger.error('Failed to get analysis queue:', err);
      // Mark the analysis as FAILED if the queue is unavailable
      await AnalysisModel.updateStatus(analysis.analysis_id!, 'FAILED');
      throw new Error('SERVICE_UNAVAILABLE');
    }

    try {
      // Include full project metadata so the worker can pass it to MS2.
      // MS2 must never query MS1's database — all data travels in the job payload.
      const jobData: AnalysisJobData = {
        analysisId: analysis.analysis_id!,
        projectId,
        userId,
        repoUrl: project.repo_url ?? '',
        repoName: project.repo_name,
        branch: project.branch,
        repositoryType: project.repository_type,
      };

      const job = await queue.add('analyze', jobData, {
        attempts: 3,
        backoff: { type: 'exponential', delay: 2000 },
      });

      // Persist the BullMQ job ID against the analysis record
      await AnalysisModel.setBullJobId(analysis.analysis_id!, job.id!);
      logger.info(`Queue Job Created — jobId=${job.id} analysisId=${analysis.analysis_id}`);
    } catch (err) {
      logger.error('Failed to create queue job:', err);
      await AnalysisModel.updateStatus(analysis.analysis_id!, 'FAILED');
      throw new Error('QUEUE_FAILURE');
    }

    return analysis;
  }

  /**
   * Get the status of an analysis from PostgreSQL only (never from BullMQ).
   * Returns null if not found, 'forbidden' if the user doesn't own it.
   */
  static async getAnalysisStatus(
    analysisId: number,
    userId: number
  ): Promise<Analysis | null | 'forbidden'> {
    const analysis = await AnalysisModel.findById(analysisId);
    if (!analysis) return null;
    if (analysis.user_id !== userId) return 'forbidden';
    return analysis;
  }

  /**
   * Apply a status update received from MS2 via webhook.
   *
   * This is the ONLY way MS2 is allowed to update Analysis data in MS1's database.
   * MS2 POSTs to /internal/webhook/analysis-status; MS1 calls this method.
   *
   * Returns false if the analysis record is not found.
   */
  static async applyStatusUpdate(
    payload: AnalysisStatusWebhookPayload
  ): Promise<boolean> {
    const { analysisId, status } = payload;

    const analysis = await AnalysisModel.findById(analysisId);
    if (!analysis) {
      logger.warn(`[Webhook] applyStatusUpdate — analysisId=${analysisId} not found`);
      return false;
    }

    // Determine timestamps based on the incoming status
    const extras: { started_at?: Date; completed_at?: Date } = {};
    if (status === 'CLONING' && !analysis.started_at) {
      extras.started_at = new Date();
    }
    if (status === 'COMPLETED' || status === 'FAILED' || status === 'READY_FOR_PARSING') {
      // completed_at is set only on terminal states; READY_FOR_PARSING is not terminal
      // but COMPLETED and FAILED are
      if (status === 'COMPLETED' || status === 'FAILED') {
        extras.completed_at = new Date();
      }
    }

    await AnalysisModel.updateStatus(analysisId, status as any, extras);

    // If MS2 sent repository metadata, persist it alongside the status update
    if (
      payload.repositoryPath !== undefined ||
      payload.repositoryName !== undefined ||
      payload.language !== undefined ||
      payload.framework !== undefined ||
      payload.repositorySize !== undefined
    ) {
      await AnalysisModel.updateRepoMetadata(analysisId, {
        repository_path: payload.repositoryPath ?? null,
        repository_name: payload.repositoryName ?? null,
        language: payload.language ?? null,
        framework: payload.framework ?? null,
        repository_size: payload.repositorySize ?? null,
      });
    }

    logger.info(
      `[Webhook] Analysis ${analysisId} status updated to ${status} via MS2 webhook`
    );
    return true;
  }
}
