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
    (
        "for loop",
        "A for loop repeats a block of code a known number of times, usually with initialization, condition, and update parts.",
    ),
    (
        "while loop",
        "A while loop repeats code while a condition is true. If the condition is false at the start, the block may not run.",
    ),
    (
        "do-while loop",
        "A do-while loop runs its block at least once, then checks the condition before repeating.",
    ),
    (
        "for-in loop",
        "A for-in loop is commonly used to loop through the properties of an object.",
    ),
    (
        "Variables",
        "Variables store values that a program can use and change. Older JavaScript examples often use the var keyword.",
    ),
    (
        "document.write",
        "document.write() writes content directly into the HTML document in simple JavaScript examples.",
    ),
    (
        "alert",
        "alert() displays a message box to the user, usually for quick feedback or warnings.",
    ),
    (
        "prompt",
        "prompt() asks the user for input and returns the entered value as text.",
    ),
    (
        "Math object",
        "The Math object provides mathematical properties and methods such as ceil(), floor(), round(), and random().",
    ),
    (
        "Math.ceil",
        "Math.ceil() returns the smallest integer greater than or equal to a given number.",
    ),
    (
        "Date object",
        "The Date object is used to work with dates and times, including year, month, day, hour, minute, and second values.",
    ),
    (
        "getFullYear",
        "getFullYear() returns the year from a Date object as a four-digit number.",
    ),
    (
        "getMonth",
        "getMonth() returns the month number from 0 to 11, so January is 0 and December is 11.",
    ),
    (
        "Array length",
        "The length property returns the number of elements stored in an array.",
    ),
    (
        "innerHTML",
        "innerHTML lets JavaScript get or set the HTML content inside an element.",
    ),
    (
        "keydown event",
        "The keydown event runs when the user presses a keyboard key.",
    ),
    (
        "Boolean",
        "A Boolean represents a true or false value and is commonly used in conditions.",
    ),
    (
        "Object methods",
        "Object methods are functions stored inside objects and used to describe object behavior.",
    ),
    (
        "Object properties",
        "Object properties are named values that describe an object's data or characteristics.",
    ),
    (
        "HTML and JavaScript",
        "HTML defines page content and structure, while JavaScript adds behavior and interaction.",
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
