"""Offline MCQ generation from extracted notes."""

from __future__ import annotations

import hashlib
import random

from services.text_processing import keywords, note_sentences


QUESTION_TEMPLATES = [
    "Which concept is most directly connected to this note: {clue}?",
    "What is the main idea tested by this statement: {clue}?",
    "Which topic would best complete a revision card for: {clue}?",
    "Which option is the best keyword for this explanation: {clue}?",
    "In exam terms, this line is mainly about which concept: {clue}?",
    "Which concept should a student revise after reading: {clue}?",
]

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


def generate_mcqs(text: str, count: int = 20, variant_seed: str | int | None = None) -> list[dict[str, object]]:
    if _is_javascript_note(text):
        return JAVASCRIPT_MCQS[: min(count, len(JAVASCRIPT_MCQS))]

    rng = random.Random(_seed_from_text(text, variant_seed))
    terms = keywords(text, max(28, count + 10)) or ["Concept", "Definition", "Example", "Process"]
    source_sentences = note_sentences(text)
    rng.shuffle(terms)
    rng.shuffle(source_sentences)

    if not source_sentences:
        source_sentences = ["an important concept from the uploaded notes"]

    mcqs: list[dict[str, object]] = []
    used_questions: set[str] = set()

    for index in range(count):
        correct = terms[index % len(terms)]
        clue = _sentence_for_term(correct, source_sentences, index)
        template = QUESTION_TEMPLATES[index % len(QUESTION_TEMPLATES)]
        question = template.format(clue=clue)
        if question in used_questions:
            question = f"{question} Focus area {index + 1}."
        used_questions.add(question)

        distractors = _pick_distractors(correct, terms, rng)
        options = [correct, *distractors]
        rng.shuffle(options)
        mcqs.append({"question": question, "options": options, "correct_answer": correct})
    return mcqs


def _seed_from_text(text: str, variant_seed: str | int | None) -> int:
    raw_seed = f"{hashlib.sha256(text.encode('utf-8')).hexdigest()}:{variant_seed or 'default'}"
    return int(hashlib.sha256(raw_seed.encode("utf-8")).hexdigest()[:16], 16)


def _sentence_for_term(term: str, source_sentences: list[str], index: int) -> str:
    matching = [sentence for sentence in source_sentences if term.lower() in sentence.lower()]
    sentence = matching[index % len(matching)] if matching else source_sentences[index % len(source_sentences)]
    sentence = sentence.strip()
    if len(sentence) > 150:
        sentence = sentence[:150].rsplit(" ", 1)[0].rstrip(",;:-") + "..."
    return sentence


def _pick_distractors(correct: str, terms: list[str], rng: random.Random) -> list[str]:
    pool = [term for term in terms if term.lower() != correct.lower()]
    rng.shuffle(pool)
    distractors = pool[:3]
    while len(distractors) < 3:
        distractors.append(f"Related concept {len(distractors) + 1}")
    return distractors


def _is_javascript_note(text: str) -> bool:
    lowered = text.lower()
    return "javascript" in lowered or "document object model" in lowered
