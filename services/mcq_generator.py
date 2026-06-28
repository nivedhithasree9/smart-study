"""Offline MCQ generation from extracted notes."""

from __future__ import annotations

from services.text_processing import keywords, sentences


def generate_mcqs(text: str, count: int = 10) -> list[dict[str, object]]:
    terms = keywords(text, max(16, count + 4)) or ["Concept", "Definition", "Example", "Process"]
    source_sentences = sentences(text)
    mcqs: list[dict[str, object]] = []
    for index in range(count):
        correct = terms[index % len(terms)]
        distractors = [term for term in terms if term != correct][:3]
        while len(distractors) < 3:
            distractors.append(f"Related Topic {len(distractors) + 1}")
        clue = next((s for s in source_sentences if correct.lower() in s.lower()), "")
        question = f"Which option best matches this idea: {clue[:120] or 'an important concept from the notes'}?"
        options = [correct, *distractors[:3]]
        mcqs.append({"question": question, "options": options, "correct_answer": correct})
    return mcqs
