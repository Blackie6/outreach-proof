"""Load configuration from environment. Fail fast if 0G vars missing."""
import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root (parent of backend/) so it works regardless of cwd
_project_root = Path(__file__).resolve().parent.parent
load_dotenv(_project_root / ".env")

BLOCKCHAIN_RPC = os.environ.get("BLOCKCHAIN_RPC")
INDEXER_RPC = os.environ.get("INDEXER_RPC")
PRIVATE_KEY = os.environ.get("PRIVATE_KEY")
LEAD_INDEX_DB_PATH = os.environ.get("LEAD_INDEX_DB_PATH") or str(
    Path(__file__).resolve().parent.parent / "data" / "lead_index.db"
)

# Retell AI (optional; required only for "Make a call")
def _env(key: str, default: str | None = None) -> str | None:
    v = os.environ.get(key) or default
    return v.strip() if isinstance(v, str) else v

RETELL_API_KEY = _env("RETELL_API_KEY")
RETELL_AGENT_ID = _env("RETELL_AGENT_ID")
RETELL_FROM_NUMBER = _env("RETELL_FROM_NUMBER")
RETELL_BASE_URL = _env("RETELL_BASE_URL") or "https://api.retellai.com"


def retell_configured() -> bool:
    """True if all Retell vars are set (for Make a call)."""
    return bool(RETELL_API_KEY and RETELL_AGENT_ID and RETELL_FROM_NUMBER and RETELL_BASE_URL)


def ensure_config() -> None:
    """Raise if required 0G config is missing."""
    if not BLOCKCHAIN_RPC:
        raise ValueError("BLOCKCHAIN_RPC is required")
    if not INDEXER_RPC:
        raise ValueError("INDEXER_RPC is required")
    if not PRIVATE_KEY:
        raise ValueError("PRIVATE_KEY is required")
