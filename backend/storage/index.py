"""SQLite index: lead_id -> root hash; phone_hash -> lead_id for reuse."""
import sqlite3
from pathlib import Path


def _conn(db_path: str):
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS lead_index (
            lead_id TEXT PRIMARY KEY,
            root_hash TEXT NOT NULL,
            tx_hash TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS lead_by_phone (
            phone_hash TEXT PRIMARY KEY,
            lead_id TEXT NOT NULL
        )
        """
    )
    conn.commit()
    return conn


def get_root(lead_id: str, db_path: str | None = None) -> tuple[str | None, str | None]:
    """Return (root_hash, tx_hash) for lead_id, or (None, None) if not found."""
    from backend.config import LEAD_INDEX_DB_PATH
    path = db_path or LEAD_INDEX_DB_PATH
    conn = _conn(path)
    try:
        row = conn.execute(
            "SELECT root_hash, tx_hash FROM lead_index WHERE lead_id = ?",
            (lead_id,),
        ).fetchone()
        return (row[0], row[1]) if row else (None, None)
    finally:
        conn.close()


def list_lead_ids(db_path: str | None = None) -> list[str]:
    """Return all lead_id values in the index."""
    from backend.config import LEAD_INDEX_DB_PATH
    path = db_path or LEAD_INDEX_DB_PATH
    conn = _conn(path)
    try:
        rows = conn.execute("SELECT lead_id FROM lead_index ORDER BY lead_id").fetchall()
        return [r[0] for r in rows]
    finally:
        conn.close()


def set_root(lead_id: str, root_hash: str, tx_hash: str | None = None, db_path: str | None = None) -> None:
    """Store or update latest root (and tx) for lead_id."""
    from backend.config import LEAD_INDEX_DB_PATH
    path = db_path or LEAD_INDEX_DB_PATH
    conn = _conn(path)
    try:
        conn.execute(
            """
            INSERT INTO lead_index (lead_id, root_hash, tx_hash)
            VALUES (?, ?, ?)
            ON CONFLICT(lead_id) DO UPDATE SET root_hash = ?, tx_hash = ?
            """,
            (lead_id, root_hash, tx_hash or "", root_hash, tx_hash or ""),
        )
        conn.commit()
    finally:
        conn.close()


def get_lead_id_by_phone(phone_hash: str, db_path: str | None = None) -> str | None:
    """Return lead_id for phone_hash if known, else None."""
    from backend.config import LEAD_INDEX_DB_PATH
    path = db_path or LEAD_INDEX_DB_PATH
    conn = _conn(path)
    try:
        row = conn.execute(
            "SELECT lead_id FROM lead_by_phone WHERE phone_hash = ?",
            (phone_hash,),
        ).fetchone()
        return row[0] if row else None
    finally:
        conn.close()


def set_lead_by_phone(phone_hash: str, lead_id: str, db_path: str | None = None) -> None:
    """Map phone_hash to lead_id (for same-number reuse)."""
    from backend.config import LEAD_INDEX_DB_PATH
    path = db_path or LEAD_INDEX_DB_PATH
    conn = _conn(path)
    try:
        conn.execute(
            """
            INSERT INTO lead_by_phone (phone_hash, lead_id)
            VALUES (?, ?)
            ON CONFLICT(phone_hash) DO UPDATE SET lead_id = ?
            """,
            (phone_hash, lead_id, lead_id),
        )
        conn.commit()
    finally:
        conn.close()
