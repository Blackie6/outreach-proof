"""0G Storage wrapper: upload_bytes, download_to_bytes. Requires 0g-storage-sdk (run in venv)."""
import sys
import tempfile
from pathlib import Path

# 0g-storage-sdk installs "core" at top level but core expects "from config import ...".
# Inject our shim so config is found.
_shim = Path(__file__).resolve().parent.parent / "zerog_shim"
if _shim.exists() and str(_shim) not in sys.path:
    sys.path.insert(0, str(_shim))

from core.file import ZgFile
from core.indexer import Indexer
from eth_account import Account

from backend.config import BLOCKCHAIN_RPC, INDEXER_RPC, PRIVATE_KEY


def _indexer() -> Indexer:
    return Indexer(INDEXER_RPC)


def _account() -> Account:
    key = PRIVATE_KEY.strip()
    if not key.startswith("0x"):
        key = "0x" + key
    return Account.from_key(key)


def upload_bytes(data: bytes) -> tuple[str, str]:
    """Upload raw bytes to 0G Storage. Returns (root_hash, tx_hash)."""
    file = ZgFile.from_bytes(data)
    try:
        upload_opts = {
            "tags": b"\x00",
            "finalityRequired": True,
            "taskSize": 10,
            "expectedReplica": 1,
            "skipTx": False,
            "account": _account(),
        }
        result, err = _indexer().upload(file, BLOCKCHAIN_RPC, _account(), upload_opts)
        if err is not None:
            raise RuntimeError(f"0G upload failed: {err}") from err
        return (result["rootHash"], result.get("txHash") or "")
    finally:
        file.close()


def download_to_bytes(root_hash: str) -> bytes:
    """Download content by root hash; returns bytes. SDK requires output path that does not exist."""
    tmp = tempfile.mktemp(suffix=".bin")
    try:
        err = _indexer().download(root_hash, tmp, proof=False)
        if err is not None:
            raise RuntimeError(f"0G download failed: {err}") from err
        return Path(tmp).read_bytes()
    finally:
        Path(tmp).unlink(missing_ok=True)
