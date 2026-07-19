import { env } from '../config/env';
import { logger } from '../utils/logger';

/**
 * Full payload sent from MS1 to MS2 when dispatching an analysis job.
 * MS2 must operate solely on this payload — it must NEVER query MS1's database.
 */
export interface DispatchPayload {
  analysisId: number;
  projectId: number;
  userId: number;
  // Project data — MS2 uses these instead of querying MS1's database.
  repoUrl: string;
  repoName: string;
  branch: string;
  repositoryType: 'github' | 'zip';
}

export interface DispatchResult {
  accepted: boolean;
  message: string;
}

const MAX_RETRIES = 3;
const TIMEOUT_MS = 30_000; // 30 seconds

/**
 * Dispatch an analysis job to MS2 via POST /internal/analysis/start.
 *
 * The payload carries all project metadata needed by MS2 so that MS2
 * never has to query MS1's database directly.
 *
 * Implements retry with up to MAX_RETRIES attempts and exponential back-off.
 * Throws on all failure conditions so the caller can handle FAILED status.
 */
export async function dispatchAnalysisToMs2(
  payload: DispatchPayload
): Promise<DispatchResult> {
  const url = `${env.MS2_BASE_URL}/internal/analysis/start`;

  logger.info(
    `[Dispatch] Dispatch Started — analysisId=${payload.analysisId} projectId=${payload.projectId}`
  );

  let lastError: Error | null = null;

  for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
    try {
      logger.info(
        `[Dispatch] Request Sent — attempt=${attempt}/${MAX_RETRIES} url=${url}`
      );

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), TIMEOUT_MS);

      let response: Response;
      try {
        response = await fetch(url, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
          signal: controller.signal,
        });
      } finally {
        clearTimeout(timeoutId);
      }

      if (!response.ok) {
        const text = await response.text();
        throw new Error(
          `MS2 responded with HTTP ${response.status}: ${text}`
        );
      }

      let result: DispatchResult;
      try {
        result = (await response.json()) as DispatchResult;
      } catch (jsonErr) {
        throw new Error(`Failed to parse JSON response from MS2: ${(jsonErr as Error).message}`);
      }

      if (!result || result.accepted !== true) {
        throw new Error(
          `MS2 rejected the job: ${result?.message || 'No message provided'}`
        );
      }

      logger.info(
        `[Dispatch] ACK Received — analysisId=${payload.analysisId} accepted=${result.accepted}`
      );
      logger.info(
        `[Dispatch] Dispatch Completed — analysisId=${payload.analysisId}`
      );

      return result;
    } catch (err) {
      lastError = err as Error;

      logger.warn(
        `[Dispatch] Attempt ${attempt}/${MAX_RETRIES} failed — analysisId=${payload.analysisId} reason=${lastError.message}`
      );

      if (attempt === MAX_RETRIES) {
        break;
      }

      // Exponential back-off: 1s, 2s before retries
      const delayMs = 1000 * attempt;
      await new Promise((resolve) => setTimeout(resolve, delayMs));
    }
  }

  logger.error(
    `[Dispatch] Dispatch Failed — analysisId=${payload.analysisId} error=${lastError?.message}`
  );

  throw lastError ?? new Error('Dispatch failed after maximum retries.');
}
