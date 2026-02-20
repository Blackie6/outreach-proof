"""POST /events - ingest event for a lead. Shared append_event_to_lead for webhook reuse."""
import json
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException

from backend.hashing import hash_content
from backend.models import (
    EVENT_TYPE_REQUIRED,
    Event,
    EventType,
    IngestEventRequest,
    IngestEventResponse,
    LeadRecord,
    Outcome,
)
from backend.storage.index import get_root, set_root
from backend.storage.zerog import download_to_bytes, upload_bytes

router = APIRouter()


def append_event_to_lead(
    lead_id: str,
    event_type: EventType,
    outcome: Outcome,
    agent: str,
    *,
    duration_seconds: int | None = None,
    content_hash: str = "",
    timestamp: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> tuple[str, str]:
    """
    Load lead by lead_id, append one event, upload to 0G, update index.
    Returns (event_id, storage_tx_id). Raises ValueError if lead not found.
    """
    ts = timestamp or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    event_id = str(uuid.uuid4())
    root_hash, _ = get_root(lead_id)
    if not root_hash:
        raise ValueError(f"Lead not found: {lead_id}")
    raw = download_to_bytes(root_hash)
    lead = LeadRecord.model_validate(json.loads(raw.decode("utf-8")))
    new_event = Event(
        event_id=event_id,
        type=event_type,
        timestamp=ts,
        content_hash=content_hash,
        outcome=outcome,
        agent=agent,
        duration_seconds=duration_seconds,
        storage_tx_id=None,
        metadata=metadata or {},
    )
    lead.events.append(new_event)
    payload = json.dumps(lead.model_dump(mode="json"), sort_keys=True).encode("utf-8")
    new_root, tx_hash = upload_bytes(payload)
    set_root(lead_id, new_root, tx_hash)
    return (event_id, new_root)


def _validate_event_payload(typ: EventType, body: IngestEventRequest) -> None:
    required = EVENT_TYPE_REQUIRED.get(typ, set())
    if "content_hash" in required:
        if body.content_hash is None and body.content is None:
            raise HTTPException(400, "content_hash or content required for this event type")
    if "timestamp" in required and body.timestamp is None:
        raise HTTPException(400, "timestamp required for this event type")
    if typ == EventType.call_completed and body.duration_seconds is None:
        raise HTTPException(400, "duration_seconds required for call_completed")


@router.post("", status_code=201, response_model=IngestEventResponse)
def ingest_event(body: IngestEventRequest):
    """Ingest a new event for a lead; append to lead record on 0G."""
    _validate_event_payload(body.type, body)

    timestamp = body.timestamp or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if body.content_hash:
        content_hash = body.content_hash
    elif body.content is not None:
        content_hash = hash_content(body.content)
    else:
        content_hash = ""

    try:
        event_id, storage_tx_id = append_event_to_lead(
            body.lead_id,
            body.type,
            body.outcome,
            body.agent,
            duration_seconds=body.duration_seconds,
            content_hash=content_hash,
            timestamp=timestamp,
            metadata=body.metadata,
        )
    except ValueError as e:
        raise HTTPException(404, str(e)) from e
    return IngestEventResponse(event_id=event_id, storage_tx_id=storage_tx_id)
