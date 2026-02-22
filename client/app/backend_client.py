"""
HTTP client for Brain Ball backend API (text-to-animal).
When backend URL is set, POSTs to /v1/text-to-animal; when unreachable, caller shows error + random animal.
"""
import logging
import os
import urllib.request
import urllib.error
import json

logger = logging.getLogger(__name__)


def get_backend_url() -> str | None:
    """Return backend base URL from env BRAIN_BALL_API_URL, or None if not set."""
    url = os.environ.get("BRAIN_BALL_API_URL", "").strip()
    return url or None


def get_animal(text: str) -> tuple[str | None, str | None]:
    """
    Call backend POST /v1/text-to-animal with {"text": text}.
    Returns (animal, error):
      - (animal, None) on success (animal is e.g. "bird")
      - (None, "unreachable") when backend is unreachable
      - (None, "invalid") on 400
      - (None, "unavailable") on 503
    If BRAIN_BALL_API_URL is not set, returns (None, None) (caller should use on-device path).
    """
    base = get_backend_url()
    if not base:
        return None, None
    url = f"{base.rstrip('/')}/v1/text-to-animal"
    data = json.dumps({"text": text}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=2) as resp:
            if resp.status != 200:
                return None, "unavailable"
            body = json.loads(resp.read().decode())
            animal = body.get("animal") or "bird"
            return animal, None
    except urllib.error.HTTPError as e:
        if e.code == 400:
            return None, "invalid"
        if e.code == 503:
            return None, "unavailable"
        return None, "unavailable"
    except (OSError, TimeoutError, json.JSONDecodeError) as e:
        logger.warning("Backend unreachable: %s", e)
        return None, "unreachable"
