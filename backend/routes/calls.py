"""POST /calls/start: create lead, initiate Retell call."""
import json
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.config import retell_configured
from backend.hashing import hash_phone
from backend.models import LeadRecord
from backend.retell import initiate_call
from backend.storage.index import get_lead_id_by_phone, set_lead_by_phone, set_root
from backend.storage.zerog import upload_bytes

router = APIRouter()


class StartCallRequest(BaseModel):
    phone: str


@router.post("/start", status_code=201)
def start_call(body: StartCallRequest):
    """Create a lead for the phone number and start a Retell outbound call. Returns lead_id and call_id."""
    phone = (body.phone or "").strip()
    if not phone:
        raise HTTPException(400, "phone is required")
    if not retell_configured():
        raise HTTPException(503, "Retell is not configured (set RETELL_API_KEY, RETELL_AGENT_ID, RETELL_FROM_NUMBER)")

    phone_hash = hash_phone(phone)
    lead_id = get_lead_id_by_phone(phone_hash)
    if not lead_id:
        lead_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        record = LeadRecord(lead_id=lead_id, phone_hash=phone_hash, created_at=created_at, events=[])
        payload = json.dumps(record.model_dump(mode="json"), sort_keys=True).encode("utf-8")
        root_hash, tx_hash = upload_bytes(payload)
        set_root(lead_id, root_hash, tx_hash)
        set_lead_by_phone(phone_hash, lead_id)

    call_id = initiate_call(phone, metadata={"lead_id": lead_id, "phone": phone})
    if not call_id:
        raise HTTPException(502, "Could not start Retell call (check logs)")

    return {"lead_id": lead_id, "call_id": call_id}
