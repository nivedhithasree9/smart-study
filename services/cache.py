"""Cache helpers built on document content hashes."""

from __future__ import annotations

from services.text_processing import content_hash


def get_cache_key(text: str) -> str:
    return content_hash(text)
