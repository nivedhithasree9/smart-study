"""Keyword extraction wrapper."""

from __future__ import annotations

from services.text_processing import keywords


def extract_keywords(text: str, limit: int = 12) -> list[str]:
    return keywords(text, limit)
