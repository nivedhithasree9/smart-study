from services.flashcards import generate_flashcards
from services.mcq_generator import generate_mcqs
from services.summarizer import summarize

JAVASCRIPT_TEXT = """
JavaScript is a client-side scripting language used to create dynamic web pages.
The Document Object Model represents the HTML document as a tree of elements.
Functions are reusable blocks of code. Arrays store multiple values.
Events are user actions such as clicks and key presses.
"""


def test_javascript_flashcards_are_clear() -> None:
    cards = generate_flashcards(JAVASCRIPT_TEXT, 4)

    assert cards[0]["question"] == "What should you remember about JavaScript?"
    assert "client-side scripting language" in cards[0]["answer"]
    assert all("document.write" not in card["answer"] for card in cards)


def test_javascript_mcqs_are_real_questions() -> None:
    mcqs = generate_mcqs(JAVASCRIPT_TEXT, 10)

    assert len(mcqs) == 10
    assert all(len(mcq["options"]) == 4 for mcq in mcqs)
    assert mcqs[0]["correct_answer"] in mcqs[0]["options"]
    assert mcqs[0]["question"] == "Which statement best describes JavaScript?"


def test_summarizer_returns_study_notes() -> None:
    short, medium, detailed, key_points = summarize(JAVASCRIPT_TEXT)

    assert "### Quick Summary" in short
    assert "### Study Summary" in medium
    assert "### Complete Study Notes" in detailed
    assert key_points
