import { AnalysisModel, Analysis } from '../models/analysis.model';
import { ProjectModel } from '../models/project.model';
import { getAnalysisQueue } from '../config/queue';
import { AnalysisJobData } from '../workers/analysis.worker';
import { logger } from '../utils/logger';

export class AnalysisService {
  /**
   * Start an analysis for a project.
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
      const jobData: AnalysisJobData = {
        analysisId: analysis.analysis_id!,
        projectId,
        userId,
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
}
