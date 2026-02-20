"""SHA-256 hashing for PII. Phone (E.164) and content never stored raw on-chain."""
import hashlib
import re


def normalize_phone(phone: str) -> str:
    """Normalize to E.164-like form: digits only, optional leading +."""
    digits = re.sub(r"\D", "", phone.strip())
    if not digits.startswith("+"):
        digits = "+" + digits
    return digits if digits[0] == "+" else "+" + digits


def hash_phone(phone: str) -> str:
    """SHA-256 hex of normalized phone. Use for lead.phone_hash."""
    return hashlib.sha256(normalize_phone(phone).encode("utf-8")).hexdigest()


def hash_content(content: str) -> str:
    """SHA-256 hex of message/transcript content. Use for event.content_hash."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()
