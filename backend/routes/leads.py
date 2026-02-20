"""POST /leads, GET /leads/:lead_id, GET /leads/:lead_id/proof."""
import json
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from backend.hashing import hash_phone
from backend.models import CreateLeadRequest, CreateLeadResponse, LeadRecord
from backend.storage.index import get_root, list_lead_ids, set_lead_by_phone, set_root
from backend.storage.zerog import download_to_bytes, upload_bytes

router = APIRouter()


@router.get("")
def list_leads():
    """List all lead IDs. Use GET /leads/{lead_id} to fetch one."""
    return {"lead_ids": list_lead_ids()}


@router.post("", status_code=201, response_model=CreateLeadResponse)
def create_lead(body: CreateLeadRequest):
    """Create a new lead record; store on 0G and register root in index."""
    if body.phone_hash:
        phone_hash = body.phone_hash
    elif body.phone:
        phone_hash = hash_phone(body.phone)
    else:
        raise HTTPException(400, "Provide either phone or phone_hash")

    created_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    record = LeadRecord(
        lead_id=body.lead_id,
        phone_hash=phone_hash,
        created_at=created_at,
        events=[],
    )
    payload = json.dumps(record.model_dump(mode="json"), sort_keys=True).encode("utf-8")
    root_hash, tx_hash = upload_bytes(payload)
    set_root(body.lead_id, root_hash, tx_hash)
    set_lead_by_phone(phone_hash, body.lead_id)
    return CreateLeadResponse(lead_id=body.lead_id, storage_tx_id=root_hash)


def _load_lead(lead_id: str) -> tuple[LeadRecord, str]:
    """Return (lead, root_hash). Raises 404 if not found."""
    root_hash, _ = get_root(lead_id)
    if not root_hash:
        raise HTTPException(404, f"Lead not found: {lead_id}")
    raw = download_to_bytes(root_hash)
    data = json.loads(raw.decode("utf-8"))
    lead = LeadRecord.model_validate(data)
    return (lead, root_hash)


@router.get("/{lead_id}")
def get_lead(lead_id: str):
    """Return full lead (metadata + events) and timeline (ordered by timestamp)."""
    lead, root_hash = _load_lead(lead_id)
    events_sorted = sorted(lead.events, key=lambda e: e.timestamp)
    timeline = [
        {
            "event_id": e.event_id,
            "type": e.type.value,
            "timestamp": e.timestamp,
            "outcome": e.outcome.value,
            "agent": e.agent,
            "duration_seconds": e.duration_seconds,
            "storage_tx_id": e.storage_tx_id or root_hash,
        }
        for e in events_sorted
    ]
    return {
        "lead_id": lead.lead_id,
        "phone_hash": lead.phone_hash,
        "created_at": lead.created_at,
        "events": [e.model_dump(mode="json") for e in lead.events],
        "timeline": timeline,
        "verification_root": root_hash,
    }


@router.get("/{lead_id}/proof")
def get_lead_proof(lead_id: str):
    """Return Proof of Outreach JSON."""
    lead, root_hash = _load_lead(lead_id)
    from backend.proof import build_proof
    return build_proof(lead, root_hash)
