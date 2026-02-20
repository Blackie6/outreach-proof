"""Pydantic schemas: Lead, Event, API request/response DTOs. Aligned with PRD §4."""
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class EventType(str, Enum):
    call_completed = "call_completed"
    call_failed = "call_failed"
    whatsapp_sent = "whatsapp_sent"
    whatsapp_reply = "whatsapp_reply"


class Outcome(str, Enum):
    interested = "interested"
    not_interested = "not_interested"
    callback = "callback"
    no_answer = "no_answer"
    pending = "pending"


class Event(BaseModel):
    event_id: str = Field(..., description="UUID v4")
    type: EventType
    timestamp: str = Field(..., description="ISO8601")
    content_hash: str = Field(..., description="SHA-256 hex of transcript or message")
    outcome: Outcome
    agent: str = Field(..., description="e.g. Lisa, WhatsApp-bot, human")
    duration_seconds: Optional[int] = None
    storage_tx_id: Optional[str] = Field(None, description="0G Storage root hash for this event")
    metadata: dict[str, Any] = Field(default_factory=dict)


class LeadRecord(BaseModel):
    """Lead record as stored in 0G (append-only)."""
    lead_id: str = Field(..., description="UUID v4")
    phone_hash: str = Field(..., description="SHA-256 hex of phone (E.164)")
    created_at: str = Field(..., description="ISO8601")
    events: list[Event] = Field(default_factory=list)


# --- API request/response ---


class CreateLeadRequest(BaseModel):
    lead_id: str = Field(..., description="UUID v4")
    phone: Optional[str] = Field(None, description="Raw phone (will be hashed); optional if phone_hash provided")
    phone_hash: Optional[str] = Field(None, description="Pre-hashed phone (SHA-256 hex)")


class CreateLeadResponse(BaseModel):
    lead_id: str
    storage_tx_id: str = Field(..., description="0G root hash")


class IngestEventRequest(BaseModel):
    lead_id: str
    type: EventType
    timestamp: Optional[str] = None  # default to now if omitted
    content_hash: Optional[str] = None  # can be computed from content if provided
    content: Optional[str] = None  # raw content; hashed if provided (never stored raw)
    outcome: Outcome
    agent: str
    duration_seconds: Optional[int] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class IngestEventResponse(BaseModel):
    event_id: str
    storage_tx_id: str


# Per PRD §5.2 required fields per event type
EVENT_TYPE_REQUIRED = {
    EventType.call_completed: {"outcome", "duration_seconds", "content_hash"},
    EventType.call_failed: {"outcome", "timestamp"},
    EventType.whatsapp_sent: {"content_hash", "agent"},
    EventType.whatsapp_reply: {"content_hash", "timestamp"},
}
