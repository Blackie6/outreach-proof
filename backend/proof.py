"""Build Proof of Outreach dict from lead + verification root. PRD §5.4."""
from backend.models import EventType, LeadRecord


def build_proof(lead: LeadRecord, verification_root: str) -> dict:
    """Return Proof of Outreach: lead id, touchpoints, date range, outcome, events table, statement."""
    events_sorted = sorted(lead.events, key=lambda e: e.timestamp)
    calls = [e for e in lead.events if e.type in (EventType.call_completed, EventType.call_failed)]
    whatsapp = [e for e in lead.events if e.type in (EventType.whatsapp_sent, EventType.whatsapp_reply)]
    timestamps = [e.timestamp for e in lead.events]
    date_min = min(timestamps) if timestamps else None
    date_max = max(timestamps) if timestamps else None
    final_outcome = events_sorted[-1].outcome.value if events_sorted else None

    events_table = [
        {
            "event_id": e.event_id,
            "type": e.type.value,
            "timestamp": e.timestamp,
            "outcome": e.outcome.value,
            "agent": e.agent,
            "storage_tx_id": e.storage_tx_id or verification_root,
        }
        for e in events_sorted
    ]

    return {
        "lead_id": lead.lead_id,
        "phone_hash": lead.phone_hash,
        "total_touchpoints": len(lead.events),
        "calls_count": len(calls),
        "whatsapp_count": len(whatsapp),
        "date_range": {"first": date_min, "last": date_max},
        "final_outcome": final_outcome,
        "events": events_table,
        "verification_root": verification_root,
        "verification_statement": "All records verifiable on 0G Storage Network",
    }
