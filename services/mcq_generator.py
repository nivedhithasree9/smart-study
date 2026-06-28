"""Offline MCQ generation from extracted notes."""

from __future__ import annotations

from services.text_processing import keywords, note_sentences


JAVASCRIPT_MCQS = [
    {
        "question": "Which statement best describes JavaScript?",
        "options": [
            "A client-side scripting language used to create dynamic web pages",
            "A database language used only for storing records",
            "A markup language used to define page structure",
            "An operating system used to run web servers",
        ],
        "correct_answer": "A client-side scripting language used to create dynamic web pages",
    },
    {
        "question": "Which is an advantage of JavaScript validation in the browser?",
        "options": [
            "It can give immediate feedback before sending data to the server",
            "It permanently removes the need for HTML",
            "It prevents all network failures",
            "It converts every web page into a database",
        ],
        "correct_answer": "It can give immediate feedback before sending data to the server",
    },
    {
        "question": "Which control-flow statement is best for choosing one block from many possible cases?",
        "options": ["switch", "typeof", "push", "getElementById"],
        "correct_answer": "switch",
    },
    {
        "question": "Which loop executes its block at least once before checking the condition?",
        "options": ["do-while loop", "for-in loop", "while loop", "for loop"],
        "correct_answer": "do-while loop",
    },
    {
        "question": "What is the main purpose of a function in JavaScript?",
        "options": [
            "To group reusable code that performs a specific task",
            "To permanently delete HTML elements",
            "To replace CSS selectors",
            "To store only image files",
        ],
        "correct_answer": "To group reusable code that performs a specific task",
    },
    {
        "question": "What does an array store?",
        "options": [
            "Multiple values in a single variable",
            "Only one fixed number",
            "Only CSS rules",
            "Only browser history",
        ],
        "correct_answer": "Multiple values in a single variable",
    },
    {
        "question": "In JavaScript, what do object properties represent?",
        "options": [
            "Values or characteristics stored on an object",
            "Only page reload commands",
            "Only mathematical operators",
            "A list of browser tabs",
        ],
        "correct_answer": "Values or characteristics stored on an object",
    },
    {
        "question": "What does the DOM represent?",
        "options": [
            "The HTML document as a tree of elements that JavaScript can access",
            "A file compression format",
            "A JavaScript package manager",
            "A server-side database table",
        ],
        "correct_answer": "The HTML document as a tree of elements that JavaScript can access",
    },
    {
        "question": "Which method is commonly used to select an HTML element by its id?",
        "options": ["getElementById", "setTimeout", "parseInt", "toUpperCase"],
        "correct_answer": "getElementById",
    },
    {
        "question": "Which example is a JavaScript event?",
        "options": [
            "A user clicking a button",
            "A variable being named carefully",
            "A CSS color value being blue",
            "A PDF file being stored offline",
        ],
        "correct_answer": "A user clicking a button",
    },
]


def generate_mcqs(text: str, count: int = 10) -> list[dict[str, object]]:
    if _is_javascript_note(text):
        return JAVASCRIPT_MCQS[:count]

    terms = keywords(text, max(16, count + 4)) or ["Concept", "Definition", "Example", "Process"]
    source_sentences = note_sentences(text)
    mcqs: list[dict[str, object]] = []
    for index in range(count):
        correct = terms[index % len(terms)]
        distractors = [term for term in terms if term != correct][:3]
        while len(distractors) < 3:
            distractors.append(f"Related Topic {len(distractors) + 1}")
        clue = next((s for s in source_sentences if correct.lower() in s.lower()), "")
        question = f"Which option best matches this note: {clue[:140] or 'an important concept from the notes'}?"
        options = [correct, *distractors[:3]]
        mcqs.append({"question": question, "options": options, "correct_answer": correct})
    return mcqs


def _is_javascript_note(text: str) -> bool:
    lowered = text.lower()
    return "javascript" in lowered or "document object model" in lowered
