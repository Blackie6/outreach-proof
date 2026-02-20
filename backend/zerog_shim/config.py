# Shim for 0g-storage-sdk: package installs "core" at top level but core/file.py
# expects "from config import ...". We provide these constants (from SDK defaults).
from Crypto.Hash import keccak

DEFAULT_CHUNK_SIZE = 256
DEFAULT_SEGMENT_SIZE = 262144
DEFAULT_SEGMENT_MAX_CHUNKS = 1024
DEFAULT_BATCH_SIZE = 10

def _keccak256(data: bytes) -> str:
    k = keccak.new(digest_bits=256)
    k.update(data)
    return "0x" + k.hexdigest()

# Hash of a chunk of zeros (256 bytes) for padding
EMPTY_CHUNK_HASH = _keccak256(bytes(DEFAULT_CHUNK_SIZE))
ZERO_HASH = "0x" + "00" * 32
