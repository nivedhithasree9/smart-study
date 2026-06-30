"""Local CPU-only study content generation.

If a GGUF model is configured and llama-cpp-python is installed, this module asks
the model for strict JSON. Otherwise it uses deterministic local extraction so
the app remains fully offline and demoable on any laptop.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

from services.flashcards import generate_flashcards
from services.keyword_extractor import extract_keywords
from services.mcq_generator import generate_mcqs
from services.summarizer import summarize
from services.text_processing import estimate_reading_time, words

REQUIRED_KEYS = {
    "title",
    "subject",
    "chapter",
    "summary_short",
    "summary_medium",
    "summary_detailed",
    "keywords",
    "key_points",
    "flashcards",
    "mcqs",
    "short_questions",
    "difficulty",
    "estimated_study_time",
}


def generate_study_content(
    text: str,
    filename: str,
    model_path: str | None = None,
    threads: int = 4,
    context_window: int = 2048,
) -> dict[str, Any]:
    if model_path and Path(model_path).exists():
        try:
            content = _generate_with_llama(text, filename, model_path, threads, context_window)
            return _normalize_content(content, text, filename)
        except Exception:
            return _fallback_content(text, filename)
    return _fallback_content(text, filename)


def _generate_with_llama(
    text: str,
    filename: str,
    model_path: str,
    threads: int,
    context_window: int,
) -> dict[str, Any]:
    from llama_cpp import Llama

    prompt = f"""
Return only valid JSON with keys: {sorted(REQUIRED_KEYS)}.
Create study resources from this offline note named {filename}.
Need at least 20 flashcards and at least 20 MCQs with 4 options and one correct_answer.
TEXT:
{text[:7000]}
"""
    llm = Llama(model_path=model_path, n_ctx=context_window, n_threads=threads, n_gpu_layers=0, verbose=False)
    result = cast(Any, llm(prompt, max_tokens=1800, temperature=0.2, stop=["```"]))
    raw = result["choices"][0]["text"]
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("Model did not return JSON.")
    return json.loads(raw[start : end + 1])


def _fallback_content(text: str, filename: str) -> dict[str, Any]:
    short, medium, detailed, key_points = summarize(text)
    extracted_keywords = extract_keywords(text, 12)
    flashcards = generate_flashcards(text, 20)
    mcqs = generate_mcqs(text, 20)
    short_questions = [f"Explain the role of {kw} in this chapter." for kw in extracted_keywords[:6]]
    word_count = len(words(text))
    difficulty = "Easy" if word_count < 350 else "Medium" if word_count < 1000 else "Hard"
    title = Path(filename).stem.replace("_", " ").replace("-", " ").title() or "Study Notes"
    return {
        "title": title,
        "subject": _infer_subject(text),
        "chapter": title,
        "summary_short": short,
        "summary_medium": medium,
        "summary_detailed": detailed,
        "keywords": extracted_keywords,
        "key_points": key_points,
        "flashcards": flashcards,
        "mcqs": mcqs,
        "short_questions": short_questions,
        "difficulty": difficulty,
        "estimated_study_time": estimate_reading_time(text),
    }


def _normalize_content(content: dict[str, Any], text: str, filename: str) -> dict[str, Any]:
    fallback = _fallback_content(text, filename)
    normalized = {key: content.get(key, fallback[key]) for key in REQUIRED_KEYS}
    if len(normalized.get("mcqs", [])) < 20:
        normalized["mcqs"] = fallback["mcqs"]
    if len(normalized.get("flashcards", [])) < 20:
        normalized["flashcards"] = fallback["flashcards"]
    if normalized.get("difficulty") not in {"Easy", "Medium", "Hard"}:
        normalized["difficulty"] = fallback["difficulty"]
    return normalized


def _infer_subject(text: str) -> str:
    lower = text.lower()
    if any(term in lower for term in ["deadlock", "process", "operating system", "memory"]):
        return "Computer Science"
    if any(term in lower for term in ["cell", "organism", "photosynthesis"]):
        return "Biology"
    if any(term in lower for term in ["force", "energy", "motion"]):
        return "Physics"
    return "General Studies"
