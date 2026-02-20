# Onchain Lead Journal API

Base URL: `http://127.0.0.1:8000` (default).

| Endpoint | Method | Description |
|----------|--------|-------------|
| `POST /leads` | POST | Create lead. Body: `lead_id`, `phone` or `phone_hash`. Returns `lead_id`, `storage_tx_id`. |
| `POST /events` | POST | Ingest event. Body: `lead_id`, `type`, `outcome`, `agent`, plus type-specific fields. Returns `event_id`, `storage_tx_id`. |
| `GET /leads/{lead_id}` | GET | Full lead + event chain + timeline. |
| `GET /leads/{lead_id}/proof` | GET | Proof of Outreach JSON. |
| `GET /health` | GET | Health check. |

Event types: `call_completed`, `call_failed`, `whatsapp_sent`, `whatsapp_reply`.  
Required fields per type: see PRD §5.2 (e.g. `call_completed` → `outcome`, `duration_seconds`, `content_hash`).
