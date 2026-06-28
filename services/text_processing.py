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


PDF_NOISE_PATTERNS = [
    re.compile(r"^\s*\d{1,4}\s*/\s*\d{1,4}\s*$"),
    re.compile(r"\b\d{1,4}\s*/\s*\d{1,4}\b\s*$"),
    re.compile(r"^\s*(?:DSAI\s+)?WEB\s+ENABLED\s+TECHNOLOGY\b.*$", re.IGNORECASE),
    re.compile(r"^\s*March\s+\d{1,2},\s+\d{4}\s*$", re.IGNORECASE),
    re.compile(r"^\s*JAVA\s+SCRIPT\s*$", re.IGNORECASE),
]

INLINE_PDF_NOISE = [
    re.compile(
        r"\b\d{1,4}\s*/\s*\d{1,4}\s+DSAI\s+WEB\s+ENABLED\s+TECHNOLOGY\s+"
        r"March\s+\d{1,2},\s+\d{4}\s+JAVA\s+SCRIPT\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bDSAI\s+WEB\s+ENABLED\s+TECHNOLOGY\s+March\s+\d{1,2},\s+\d{4}\s+JAVA\s+SCRIPT\b",
        re.IGNORECASE,
    ),
    re.compile(r"\b\d{1,4}\s*/\s*\d{1,4}\b"),
]


def _looks_like_pdf_noise(line: str) -> bool:
    normalized = " ".join(line.split())
    if not normalized:
        return True
    return any(pattern.search(normalized) for pattern in PDF_NOISE_PATTERNS)


def _drop_repeated_short_lines(lines: list[str]) -> list[str]:
    counts: dict[str, int] = {}
    for line in lines:
        key = re.sub(r"\d+", "#", line.lower()).strip()
        if 4 <= len(key) <= 90:
            counts[key] = counts.get(key, 0) + 1

    cleaned: list[str] = []
    for line in lines:
        key = re.sub(r"\d+", "#", line.lower()).strip()
        if counts.get(key, 0) >= 3:
            continue
        cleaned.append(line)
    return cleaned


def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"-\s*\n\s*", "", text)
    lines = [" ".join(line.split()) for line in text.splitlines()]
    lines = [line for line in lines if not _looks_like_pdf_noise(line)]
    lines = _drop_repeated_short_lines(lines)
    text = " ".join(lines)
    for pattern in INLINE_PDF_NOISE:
        text = pattern.sub(" ", text)
    text = re.sub(r"\b([A-Za-z][A-Za-z0-9_-]{2,})\s+\1\b", r"\1", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def content_hash(text: str) -> str:
    normalized = clean_text(text).lower()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", clean_text(text))
    return [part.strip() for part in parts if len(part.strip()) > 25]


def note_sentences(text: str) -> list[str]:
    cleaned: list[str] = []
    for sentence in sentences(text):
        note = clean_note_sentence(sentence)
        if note and not is_code_heavy(note):
            cleaned.append(note)
    return _dedupe(cleaned)


def clean_note_sentence(sentence: str) -> str:
    sentence = sentence.replace("�", "'")
    sentence = re.sub(r"<[^>]+>", " ", sentence)
    sentence = re.sub(r"[{}]", " ", sentence)
    sentence = re.sub(r"\s+", " ", sentence).strip()
    sentence = sentence.strip(":- ")
    if len(sentence) > 260:
        sentence = sentence[:260].rsplit(" ", 1)[0].rstrip(",;:-") + "."
    return sentence


def is_code_heavy(sentence: str) -> bool:
    lowered = sentence.lower()
    code_markers = [
        "document.write",
        "document.writeln",
        "var ",
        "function(",
        "alert(",
        "prompt(",
        "console.",
        "});",
        "++",
        "==",
        "=>",
    ]
    if any(marker in lowered for marker in code_markers):
        return True
    symbol_count = sum(sentence.count(symbol) for symbol in [";", "=", "(", ")", "+", "{", "}", "<", ">"])
    return symbol_count > 8


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}", text.lower())


def keywords(text: str, limit: int = 12) -> list[str]:
    counts = Counter(word for word in words(text) if word not in STOPWORDS)
    return [word.title() for word, _ in counts.most_common(limit)]


def estimate_reading_time(text: str) -> str:
    minutes = max(1, round(len(words(text)) / 180))
    return f"{minutes} min"


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        key = item.lower()[:120]
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result
