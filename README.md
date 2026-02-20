# Onchain Lead Journal

Append-only lead event ledger on **0G Storage**. Every AI touchpoint (call, WhatsApp) is written as an immutable record; the output is a **Proof of Outreach** report that any stakeholder can verify.

**Pitch:** *"Every AI sales call leaves a tamper-proof receipt on-chain. Your CRM can lie. The ledger can't."*

See [OnchainLeadJournal_PRD.md](OnchainLeadJournal_PRD.md) for full product spec.

## Quick start

1. **Prerequisites**
   - Python 3.8+
   - 0G testnet wallet with testnet 0G ([faucet.0g.ai](https://faucet.0g.ai))
   - `.env` with `BLOCKCHAIN_RPC`, `INDEXER_RPC`, `PRIVATE_KEY` (see [.env.example](.env.example))

2. **Install and run**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # or .venv\Scripts\activate on Windows
   pip install -r requirements.txt
   uvicorn backend.main:app --reload
   ```
   API: http://127.0.0.1:8000  
   Docs: http://127.0.0.1:8000/docs

3. **Demo**
   ```bash
   ./scripts/demo.sh
   ```
   Creates a lead, posts a mock call and WhatsApp event, then fetches the timeline and Proof of Outreach JSON.

## Success criteria (MVP)

- Mock call event and mock WhatsApp event written to 0G with real TX/root IDs
- Full lead timeline via `GET /leads/:id`
- Proof of Outreach JSON via `GET /leads/:id/proof`
- Demo script runs end-to-end

## Env vars

| Variable | Description |
|----------|-------------|
| `BLOCKCHAIN_RPC` | 0G chain RPC (testnet: `https://evmrpc-testnet.0g.ai`) |
| `INDEXER_RPC` | 0G Storage indexer (testnet: `https://indexer-storage-testnet-turbo.0g.ai`) |
| `PRIVATE_KEY` | Wallet private key (hex, with or without `0x`) for signing uploads |
| `LEAD_INDEX_DB_PATH` | Optional; default `./data/lead_index.db` |
| `RETELL_API_KEY` | Optional; Retell AI API key for "Make a call" |
| `RETELL_AGENT_ID` | Optional; Retell agent ID |
| `RETELL_FROM_NUMBER` | Optional; Caller ID (E.164) |
| `RETELL_BASE_URL` | Optional; default `https://api.retellai.com` |

## Retell webhook

For "Make a call", when a call ends Retell sends events to your app. Configure the **Retell webhook URL** in the Retell dashboard to:

`https://<your-host>/webhooks/retell`

The app must be **publicly reachable over HTTPS**. For local development use [ngrok](https://ngrok.com) or similar and set that URL in Retell.

**Troubleshooting: no events after a call**

- If the lead timeline stays empty after a call, Retell is likely not reaching your webhook. When running locally, Retell cannot POST to `localhost`. Use **ngrok** (e.g. `ngrok http 8001`) and set the Retell webhook URL to `https://<your-ngrok-host>/webhooks/retell`.
- Restart the app and watch the **server console** when a call ends. You should see logs like `Retell webhook: received event='call_ended'` or `Retell webhook: wrote event to lead_id=...`. If you see no webhook logs at all, the request is not reaching your server (check URL and firewall).
- If you see `no lead_id in metadata`, Retell may be sending a different payload shape; the logs will show the payload keys to adjust parsing.

## Notes

- Uploads can take a few minutes to propagate on 0G; if `GET /leads/:id` or `POST /events` (which downloads the current lead) fails right after creating the lead, wait 2–5 minutes and retry.
- PII (phone, message content) is hashed (SHA-256) before writing; raw values are never stored on-chain.

Built for 0G Hackathon 2025.
