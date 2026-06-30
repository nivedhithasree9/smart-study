"""Offline MCQ generation from extracted notes."""

from __future__ import annotations

import hashlib
import random
from typing import TypedDict

from services.text_processing import keywords, note_sentences


class MCQ(TypedDict):
    question: str
    options: list[str]
    correct_answer: str


QUESTION_TEMPLATES = [
    "Which concept is most directly connected to this note: {clue}?",
    "What is the main idea tested by this statement: {clue}?",
    "Which topic would best complete a revision card for: {clue}?",
    "Which option is the best keyword for this explanation: {clue}?",
    "In exam terms, this line is mainly about which concept: {clue}?",
    "Which concept should a student revise after reading: {clue}?",
]

JAVASCRIPT_MCQS: list[MCQ] = [
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
    {
        "question": "Which statement correctly describes the for loop?",
        "options": [
            "It repeats a block of code a known number of times",
            "It stores many values in one variable",
            "It creates a new HTML document",
            "It converts text into an image",
        ],
        "correct_answer": "It repeats a block of code a known number of times",
    },
    {
        "question": "What is the purpose of a while loop?",
        "options": [
            "To repeat code while a condition remains true",
            "To define only object properties",
            "To load a CSS stylesheet",
            "To permanently close the browser",
        ],
        "correct_answer": "To repeat code while a condition remains true",
    },
    {
        "question": "What does a for-in loop commonly iterate over?",
        "options": [
            "The properties of an object",
            "Only image pixels",
            "Only database rows",
            "The operating system files",
        ],
        "correct_answer": "The properties of an object",
    },
    {
        "question": "Which keyword is used to declare a variable in older JavaScript examples?",
        "options": ["var", "echo", "select", "table"],
        "correct_answer": "var",
    },
    {
        "question": "What does document.write() do in basic JavaScript examples?",
        "options": [
            "Writes content into the web page document",
            "Creates a database backup",
            "Checks internet speed",
            "Encrypts all JavaScript files",
        ],
        "correct_answer": "Writes content into the web page document",
    },
    {
        "question": "What is the role of alert() in JavaScript?",
        "options": [
            "To display a message box to the user",
            "To sort an array permanently",
            "To style an element with CSS",
            "To create a server route",
        ],
        "correct_answer": "To display a message box to the user",
    },
    {
        "question": "What does prompt() usually collect?",
        "options": [
            "Input typed by the user",
            "The browser's installed fonts",
            "Only the current date",
            "A hidden database password",
        ],
        "correct_answer": "Input typed by the user",
    },
    {
        "question": "Which object provides mathematical methods such as ceil()?",
        "options": ["Math", "Document", "Array", "WindowHistory"],
        "correct_answer": "Math",
    },
    {
        "question": "What does Math.ceil() return?",
        "options": [
            "The smallest integer greater than or equal to a number",
            "The largest negative number in a script",
            "The current month name",
            "The length of a string",
        ],
        "correct_answer": "The smallest integer greater than or equal to a number",
    },
    {
        "question": "Which object is used in JavaScript to work with dates and times?",
        "options": ["Date", "Table", "Style", "Audio"],
        "correct_answer": "Date",
    },
    {
        "question": "What does getFullYear() return?",
        "options": [
            "The year as four digits",
            "The number of array elements",
            "The selected HTML tag name",
            "The user's keyboard layout",
        ],
        "correct_answer": "The year as four digits",
    },
    {
        "question": "What does getMonth() return in JavaScript Date objects?",
        "options": [
            "The month number from 0 to 11",
            "The day name as a string",
            "The total number of functions",
            "The browser zoom level",
        ],
        "correct_answer": "The month number from 0 to 11",
    },
    {
        "question": "What does the length property of an array return?",
        "options": [
            "The number of elements in the array",
            "The current screen width",
            "The file size of the script",
            "The number of web pages open",
        ],
        "correct_answer": "The number of elements in the array",
    },
    {
        "question": "Why are JavaScript events useful?",
        "options": [
            "They allow code to respond to user actions",
            "They remove the need for programming logic",
            "They convert JavaScript into HTML",
            "They make every condition true",
        ],
        "correct_answer": "They allow code to respond to user actions",
    },
    {
        "question": "What does innerHTML allow JavaScript to do?",
        "options": [
            "Get or set the HTML content inside an element",
            "Install a browser extension",
            "Compress a PDF file",
            "Change the computer's operating system",
        ],
        "correct_answer": "Get or set the HTML content inside an element",
    },
    {
        "question": "Which event can be used to react when a keyboard key is pressed?",
        "options": ["keydown", "ceil", "setMonth", "Boolean"],
        "correct_answer": "keydown",
    },
    {
        "question": "What is a Boolean value normally used to represent?",
        "options": [
            "A true or false condition",
            "Only a list of images",
            "A full HTML table",
            "The number of browser windows",
        ],
        "correct_answer": "A true or false condition",
    },
    {
        "question": "Why can JavaScript make web pages more interactive?",
        "options": [
            "It can react to user actions and update page content",
            "It disables all browser events",
            "It prevents pages from using HTML",
            "It works only after the server is restarted",
        ],
        "correct_answer": "It can react to user actions and update page content",
    },
    {
        "question": "Which pair is part of common web page structure and behavior?",
        "options": [
            "HTML defines content and JavaScript adds behavior",
            "JavaScript replaces all browsers and HTML stores databases",
            "CSS runs loops and JavaScript stores only colors",
            "Date objects define page headings and arrays open files",
        ],
        "correct_answer": "HTML defines content and JavaScript adds behavior",
    },
    {
        "question": "What is the best description of an object in JavaScript?",
        "options": [
            "A collection of related properties and methods",
            "Only a single plain number",
            "A type of internet cable",
            "A replacement for every loop",
        ],
        "correct_answer": "A collection of related properties and methods",
    },
]


def generate_mcqs(text: str, count: int = 20, variant_seed: str | int | None = None) -> list[MCQ]:
    if _is_javascript_note(text):
        js_mcqs = [item.copy() for item in JAVASCRIPT_MCQS]
        if variant_seed is not None:
            rng = random.Random(_seed_from_text(text, variant_seed))  # nosec B311
            rng.shuffle(js_mcqs)
        return js_mcqs[: min(count, len(js_mcqs))]

    rng = random.Random(_seed_from_text(text, variant_seed))  # nosec B311
    terms = keywords(text, max(28, count + 10)) or ["Concept", "Definition", "Example", "Process"]
    source_sentences = note_sentences(text)
    rng.shuffle(terms)
    rng.shuffle(source_sentences)

    if not source_sentences:
        source_sentences = ["an important concept from the uploaded notes"]

    mcqs: list[MCQ] = []
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
