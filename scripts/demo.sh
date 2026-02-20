#!/usr/bin/env bash
# Demo: create lead, post call + WhatsApp events, GET lead timeline, GET Proof of Outreach.
# Run with backend up: uvicorn backend.main:app --reload (from repo root).
set -e
BASE="${BASE_URL:-http://127.0.0.1:8000}"
LEAD_ID="${LEAD_ID:-$(uuidgen 2>/dev/null || python3 -c 'import uuid; print(uuid.uuid4())')}"

JQ=jq
command -v jq >/dev/null 2>&1 || JQ=cat
echo "Using BASE=$BASE LEAD_ID=$LEAD_ID"
echo "--- 1. Create lead ---"
curl -s -X POST "$BASE/leads" \
  -H "Content-Type: application/json" \
  -d "{\"lead_id\": \"$LEAD_ID\", \"phone\": \"+5215512345678\"}" | $JQ .

echo "--- 2. Post call_completed event ---"
curl -s -X POST "$BASE/events" \
  -H "Content-Type: application/json" \
  -d "{
    \"lead_id\": \"$LEAD_ID\",
    \"type\": \"call_completed\",
    \"outcome\": \"interested\",
    \"agent\": \"Lisa\",
    \"duration_seconds\": 142,
    \"content_hash\": \"$(echo -n 'Call transcript summary' | shasum -a 256 | cut -d' ' -f1)\"
  }" | $JQ .

echo "--- 3. Post whatsapp_sent event ---"
curl -s -X POST "$BASE/events" \
  -H "Content-Type: application/json" \
  -d "{
    \"lead_id\": \"$LEAD_ID\",
    \"type\": \"whatsapp_sent\",
    \"outcome\": \"pending\",
    \"agent\": \"WhatsApp-bot\",
    \"content_hash\": \"$(echo -n 'Hi, follow-up message' | shasum -a 256 | cut -d' ' -f1)\"
  }" | $JQ .

echo "--- 4. GET lead timeline ---"
curl -s "$BASE/leads/$LEAD_ID" | $JQ .

echo "--- 5. GET Proof of Outreach ---"
curl -s "$BASE/leads/$LEAD_ID/proof" | $JQ .

echo "Done."
