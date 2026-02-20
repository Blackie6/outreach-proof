"""Onchain Lead Journal API. FastAPI app and router wiring."""
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from backend.config import ensure_config

logging.basicConfig(level=logging.INFO)
logging.getLogger("backend").setLevel(logging.INFO)
from backend.routes import calls, events, leads, webhooks


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_config()
    yield


app = FastAPI(
    title="Onchain Lead Journal",
    description="Append-only lead event ledger on 0G Storage. Proof of Outreach.",
    lifespan=lifespan,
)

app.include_router(leads.router, prefix="/leads", tags=["leads"])
app.include_router(events.router, prefix="/events", tags=["events"])
app.include_router(calls.router, prefix="/calls", tags=["calls"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])


@app.get("/")
def root():
    return {
        "app": "Onchain Lead Journal",
        "docs": "/docs",
        "dashboard": "/dashboard",
        "health": "/health",
        "endpoints": {
            "GET /leads": "List all lead IDs",
            "POST /leads": "Create lead",
            "GET /leads/{lead_id}": "Get lead and timeline",
            "GET /leads/{lead_id}/proof": "Proof of Outreach JSON",
            "POST /events": "Ingest event for a lead",
            "POST /calls/start": "Create lead and start Retell call",
            "POST /webhooks/retell": "Retell AI webhook (call results -> 0G)",
        },
    }


@app.get("/wallet/balance")
def wallet_balance():
    """Return testnet wallet balance (0G) for the configured PRIVATE_KEY."""
    from eth_account import Account
    from web3 import Web3
    from backend.config import BLOCKCHAIN_RPC, PRIVATE_KEY
    key = (PRIVATE_KEY or "").strip()
    if not key.startswith("0x"):
        key = "0x" + key
    account = Account.from_key(key)
    w3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_RPC))
    balance_wei = w3.eth.get_balance(account.address)
    balance_og = balance_wei / 1e18
    return {
        "address": account.address,
        "balance_wei": str(balance_wei),
        "balance_og": round(balance_og, 6),
    }


@app.get("/dashboard")
def dashboard():
    """Simple dashboard with buttons to create lead, post events, get timeline and proof."""
    path = Path(__file__).parent / "static" / "dashboard.html"
    return FileResponse(path, media_type="text/html")


@app.get("/health")
def health():
    return {"status": "ok"}
