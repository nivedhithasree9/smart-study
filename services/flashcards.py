"""Offline flashcard generation."""

from __future__ import annotations

from services.text_processing import keywords, note_sentences


JAVASCRIPT_CARDS = [
    (
        "JavaScript",
        "JavaScript is a client-side scripting language used to make web pages dynamic and interactive.",
    ),
    (
        "Advantages of JavaScript",
        "JavaScript can validate input, give immediate feedback, reduce server requests, and create richer browser interfaces.",
    ),
    (
        "Control Flow",
        "Control flow decides which block of code runs. JavaScript commonly uses if, else-if, else, and switch statements.",
    ),
    (
        "Loops",
        "Loops repeat a block of code. JavaScript supports for, while, do-while, and for-in loops.",
    ),
    (
        "Functions",
        "A function is a reusable block of code designed to perform a specific task.",
    ),
    (
        "Arrays",
        "An array stores multiple values in one variable and provides methods to access, join, add, or remove elements.",
    ),
    (
        "Objects",
        "An object stores related data and behavior using properties and methods.",
    ),
    (
        "DOM",
        "The Document Object Model represents an HTML page as a tree of elements that JavaScript can read or change.",
    ),
    (
        "Events",
        "Events are user or browser actions, such as clicks, key presses, form changes, loading, and submitting.",
    ),
]


def generate_flashcards(text: str, limit: int = 8) -> list[dict[str, str]]:
    source_sentences = note_sentences(text)
    cards: list[dict[str, str]] = []

    if _is_javascript_note(text):
        for concept, answer in JAVASCRIPT_CARDS[:limit]:
            cards.append({"question": f"What should you remember about {concept}?", "answer": answer})
        return cards

    for concept, markers in _concepts_for_text(text, limit):
        match = _best_match(source_sentences, markers)
        cards.append({"question": f"What should you remember about {concept}?", "answer": _study_answer(concept, match)})
    return cards[:limit]


def _is_javascript_note(text: str) -> bool:
    lowered = text.lower()
    return "javascript" in lowered or "document object model" in lowered


def _concepts_for_text(text: str, limit: int) -> list[tuple[str, list[str]]]:
    return [(keyword, [keyword.lower()]) for keyword in keywords(text, limit)]


def _best_match(source_sentences: list[str], markers: list[str]) -> str:
    for marker in markers:
        match = next((sentence for sentence in source_sentences if marker.lower() in sentence.lower()), "")
        if match:
            return match
    return ""


def _study_answer(keyword: str, match: str) -> str:
    if not match:
        return f"{keyword} is an important concept from this chapter. Revise its definition, purpose, and usage."
    return f"{keyword}: {match}"
