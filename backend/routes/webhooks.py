"""POST /webhooks/retell: receive Retell call events, write call_completed/call_failed to 0G."""
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Request, Response

from backend.hashing import hash_content
from backend.models import EventType, Outcome
from backend.routes.events import append_event_to_lead

router = APIRouter()
logger = logging.getLogger(__name__)

# Terminal events we process (call ended or analyzed)
TERMINAL_EVENTS = {"call_ended", "call_analyzed"}

# Reasons that mean no contact -> call_failed, no_answer (call never connected)
NO_CONTACT_REASONS = {
    "no_answer", "dial_no_answer", "dial no answer", "failed", "not_connected",
    "unanswered", "voicemail",
}


def _get_lead_id(payload: dict) -> str | None:
    """Extract lead_id from call.retell_llm_dynamic_variables, call.metadata, or top-level."""
    if isinstance(payload.get("lead_id"), str) and payload["lead_id"].strip():
        return payload["lead_id"].strip()
    call = payload.get("call") or {}
    if not isinstance(call, dict):
        return None
    for key in ("retell_llm_dynamic_variables", "metadata"):
        vars_dict = call.get(key)
        if isinstance(vars_dict, dict) and vars_dict.get("lead_id"):
            return str(vars_dict["lead_id"]).strip()
    return None


def _is_no_contact(payload: dict) -> bool:
    """True if call never connected (no_answer, failed, etc.)."""
    call = payload.get("call") or {}
    event = (payload.get("event") or payload.get("event_type") or "").lower()
    reason = (
        (call.get("disconnection_reason") or call.get("end_reason") or call.get("endReason") or "")
    ).lower()
    status = (call.get("call_status") or call.get("session_status") or "").lower()
    analysis = call.get("call_analysis") or {}
    if isinstance(analysis, dict) and analysis.get("call_successful") is False:
        return True
    for r in (reason, status, event):
        if any(n in r for n in ("no_answer", "dial_no_answer", "dial no answer", "failed", "not_connected", "unanswered", "voicemail")):
            return True
    return False


def _get_duration(payload: dict) -> int | None:
    """Get call duration in seconds from payload."""
    call = payload.get("call") or {}
    if not isinstance(call, dict):
        return None
    d = call.get("duration") or call.get("call_duration")
    if d is not None:
        try:
            return int(d)
        except (TypeError, ValueError):
            pass
    return None


@router.post("/retell")
async def retell_webhook(request: Request):
    """
    Retell AI webhook. On call_ended/call_analyzed: read lead_id from metadata,
    map to call_completed or call_failed, append event to lead on 0G.
    """
    try:
        body = await request.json()
    except Exception as e:
        logger.warning("Retell webhook invalid JSON: %s", e)
        return Response(status_code=400)

    raw_event = body.get("event") or body.get("event_type") or ""
    event = (raw_event or "").strip().lower().replace(" ", "_")
    logger.info(
        "Retell webhook: received event=%r (raw=%r) keys=%s",
        event,
        raw_event,
        list(body.keys()) if isinstance(body, dict) else "not-dict",
    )
    if event not in TERMINAL_EVENTS:
        logger.info(
            "Retell webhook: ignoring non-terminal event=%r (we only process %s)",
            event,
            TERMINAL_EVENTS,
        )
        return Response(status_code=200)

    lead_id = _get_lead_id(body)
    if not lead_id:
        call = body.get("call") or {}
        logger.warning(
            "Retell webhook: no lead_id in metadata, skipping event=%s call_keys=%s llm_vars=%s",
            event,
            list(call.keys()) if isinstance(call, dict) else "n/a",
            call.get("retell_llm_dynamic_variables") if isinstance(call, dict) else "n/a",
        )
        return Response(status_code=200)

    no_contact = _is_no_contact(body)
    duration = _get_duration(body)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    call_id = (body.get("call") or {}).get("call_id") or ""
    placeholder_hash = hash_content(f"retell_call_{call_id}") if call_id else hash_content("retell_call")

    if no_contact:
        event_type = EventType.call_failed
        outcome = Outcome.no_answer
        content_hash = ""
    else:
        event_type = EventType.call_completed
        outcome = Outcome.pending
        content_hash = placeholder_hash

    try:
        append_event_to_lead(
            lead_id,
            event_type,
            outcome,
            "Lisa",
            duration_seconds=duration,
            content_hash=content_hash,
            timestamp=ts,
            metadata={"retell_call_id": call_id, "retell_event": event},
        )
        logger.info("Retell webhook: wrote event to lead_id=%s type=%s", lead_id, event_type.value)
    except ValueError as e:
        logger.warning("Retell webhook: lead not found lead_id=%s: %s", lead_id, e)
    except Exception as e:
        logger.exception("Retell webhook: failed to append event: %s", e)
        return Response(status_code=500)

    return Response(status_code=200)
