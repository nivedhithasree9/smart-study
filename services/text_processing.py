"""Text cleanup, hashing, and simple NLP helpers."""

from __future__ import annotations

import hashlib
import re
from collections import Counter

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has",
    "have", "in", "is", "it", "its", "of", "on", "or", "that", "the", "this",
    "to", "was", "were", "with", "can", "will", "which", "into", "their",
    "there", "these", "those", "when", "where", "while", "also", "than",
}


def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"-\s*\n\s*", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def content_hash(text: str) -> str:
    normalized = clean_text(text).lower()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", clean_text(text))
    return [part.strip() for part in parts if len(part.strip()) > 25]


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}", text.lower())


def keywords(text: str, limit: int = 12) -> list[str]:
    counts = Counter(word for word in words(text) if word not in STOPWORDS)
    return [word.title() for word, _ in counts.most_common(limit)]


def estimate_reading_time(text: str) -> str:
    minutes = max(1, round(len(words(text)) / 180))
    return f"{minutes} min"
