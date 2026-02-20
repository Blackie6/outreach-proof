"""Minimal Retell AI client: initiate outbound call. Metadata is echoed in webhooks."""
import logging
from typing import Any

import requests

from backend.config import RETELL_AGENT_ID, RETELL_API_KEY, RETELL_BASE_URL, RETELL_FROM_NUMBER

logger = logging.getLogger(__name__)


def _stringify_metadata(metadata: dict[str, Any] | None) -> dict[str, str]:
    if not isinstance(metadata, dict):
        return {}
    return {k: str(v) for k, v in metadata.items() if v is not None}


def initiate_call(phone_number: str, metadata: dict[str, Any] | None = None) -> str | None:
    """
    Start an outbound call via Retell AI v2.
    Returns Retell call_id on success, None otherwise.
    """
    if not RETELL_API_KEY or not RETELL_AGENT_ID or not RETELL_FROM_NUMBER or not RETELL_BASE_URL:
        return None
    url = f"{RETELL_BASE_URL.rstrip('/')}/v2/create-phone-call"
    headers = {
        "Authorization": f"Bearer {RETELL_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "from_number": RETELL_FROM_NUMBER,
        "to_number": phone_number.strip(),
        "retell_llm_dynamic_variables": _stringify_metadata(metadata or {}),
        "override_agent_id": RETELL_AGENT_ID,
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        if resp.ok:
            data = resp.json()
            call_id = data.get("call_id")
            if call_id:
                logger.info("Retell call initiated: call_id=%s to_number=%s", call_id, phone_number)
                return call_id
        else:
            logger.warning("Retell create-phone-call failed: %s %s", resp.status_code, resp.text[:200])
    except Exception as e:
        logger.exception("Retell initiate_call error: %s", e)
    return None
