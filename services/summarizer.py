"""Local extractive summarization helpers."""

from __future__ import annotations

from services.text_processing import sentences


def summarize(text: str) -> tuple[str, str, str, list[str]]:
    source = sentences(text)
    if not source:
        fallback = text[:500] or "No readable study text was found."
        return fallback[:220], fallback[:650], fallback, []

    key_points = source[:8]
    short = " ".join(source[:2])
    medium = " ".join(source[:5])
    detailed = " ".join(source[:10])
    return short, medium, detailed, key_points
