"""Offline flashcard generation."""

from __future__ import annotations

from services.text_processing import keywords, sentences


def generate_flashcards(text: str, limit: int = 8) -> list[dict[str, str]]:
    source_sentences = sentences(text)
    cards: list[dict[str, str]] = []
    for keyword in keywords(text, limit):
        match = next((s for s in source_sentences if keyword.lower() in s.lower()), "")
        answer = match or f"{keyword} is an important concept in this note."
        cards.append({"question": f"What is {keyword}?", "answer": answer})
    return cards[:limit]
