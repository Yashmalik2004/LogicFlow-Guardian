"""
Webhook service — sends analysis status updates from MS2 to MS1.

MS2 must NEVER write to MS1's database directly.
Instead, this service POSTs a JSON payload to MS1's internal webhook endpoint:

    POST {MS1_BASE_URL}/internal/webhook/analysis-status

MS1 then updates its own Analysis table.

Retries: up to 3 attempts with exponential back-off (1s, 2s).
Timeout: 15 seconds per attempt.
All failures are logged; a failed webhook does NOT raise so the intake
pipeline can continue (best-effort delivery).
"""
import time
import urllib.request
import urllib.error
import json

from app.config.env import env

_MAX_RETRIES = 3
_TIMEOUT_SECONDS = 15


def send_status_update(
    analysis_id: int,
    status: str,
    *,
    repository_path: str | None = None,
    repository_name: str | None = None,
    language: str | None = None,
    framework: str | None = None,
    repository_size: int | None = None,
    error_message: str | None = None,
) -> bool:
    """
    POST a status-update webhook to MS1.

    Parameters
    ----------
    analysis_id:      MS1 Analysis record ID
    status:           New status string (e.g. 'CLONING', 'READY_FOR_PARSING')
    repository_path:  Local workspace path (optional, sent when status is READY_FOR_PARSING)
    repository_name:  Detected repository name (optional)
    language:         Detected language (optional)
    framework:        Detected framework (optional)
    repository_size:  Total repo size in bytes (optional)
    error_message:    Error details when status is FAILED (optional)

    Returns True if MS1 acknowledged the webhook, False on all failures.
    """
    url = f"{env.MS1_BASE_URL}/internal/webhook/analysis-status"

    payload: dict = {"analysisId": analysis_id, "status": status}
    if repository_path is not None:
        payload["repositoryPath"] = repository_path
    if repository_name is not None:
        payload["repositoryName"] = repository_name
    if language is not None:
        payload["language"] = language
    if framework is not None:
        payload["framework"] = framework
    if repository_size is not None:
        payload["repositorySize"] = repository_size
    if error_message is not None:
        payload["errorMessage"] = error_message

    body = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if env.MS2_WEBHOOK_SECRET:
        headers["X-Webhook-Secret"] = env.MS2_WEBHOOK_SECRET

    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            req = urllib.request.Request(url, data=body, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=_TIMEOUT_SECONDS) as resp:
                if resp.status == 200:
                    print(
                        f"[INFO] [Webhook] Status update sent — "
                        f"analysis_id={analysis_id} status={status}"
                    )
                    return True
                else:
                    print(
                        f"[WARN] [Webhook] MS1 responded {resp.status} — "
                        f"attempt={attempt}/{_MAX_RETRIES}"
                    )
        except urllib.error.URLError as exc:
            print(
                f"[WARN] [Webhook] Request failed — "
                f"attempt={attempt}/{_MAX_RETRIES} error={exc}"
            )
        except Exception as exc:  # noqa: BLE001
            print(
                f"[WARN] [Webhook] Unexpected error — "
                f"attempt={attempt}/{_MAX_RETRIES} error={exc}"
            )

        if attempt < _MAX_RETRIES:
            time.sleep(attempt)  # 1s, 2s

    print(
        f"[ERROR] [Webhook] Failed to notify MS1 after {_MAX_RETRIES} attempts — "
        f"analysis_id={analysis_id} status={status}"
    )
    return False
