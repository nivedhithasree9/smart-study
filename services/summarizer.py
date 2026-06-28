"""Local extractive summarization helpers."""

from __future__ import annotations

from services.text_processing import keywords, note_sentences


def summarize(text: str) -> tuple[str, str, str, list[str]]:
    source = note_sentences(text)
    if not source:
        fallback = text[:500] or "No readable study text was found."
        return fallback[:220], fallback[:650], fallback, []

    topics = _topic_notes(source)
    concept_bullets = _concept_bullets(topics, text)
    revision_bullets = _coverage_summary(source, text, 10)

    short = _short_notes(source, topics)
    medium = _medium_notes(source, topics, concept_bullets)
    detailed = _detailed_notes(source, topics, concept_bullets, revision_bullets)

    key_points = [item for items in topics.values() for item in items][:12]
    if len(key_points) < 8:
        key_points = _coverage_summary(source, text, 12)
    return short, medium, detailed, key_points


def _short_notes(source: list[str], topics: dict[str, list[str]]) -> str:
    covered = ", ".join(label for label, items in topics.items() if items)
    overview = " ".join(_coverage_summary(source, " ".join(source), 3))
    return (
        "### Quick Summary\n"
        f"{overview}\n\n"
        f"**Main areas covered:** {covered or 'core concepts and examples'}."
    )


def _medium_notes(source: list[str], topics: dict[str, list[str]], concept_bullets: list[str]) -> str:
    overview = " ".join(_coverage_summary(source, " ".join(source), 5))
    bullets = "\n".join(f"- {item}" for item in concept_bullets[:10])
    return (
        "### Study Summary\n"
        f"{overview}\n\n"
        "### Important Concepts\n"
        f"{bullets}"
    )


def _detailed_notes(
    source: list[str],
    topics: dict[str, list[str]],
    concept_bullets: list[str],
    revision_bullets: list[str],
) -> str:
    parts = [
        "### Complete Study Notes",
        "These notes are condensed from the full PDF and remove raw code-heavy examples so the content is easier to revise.",
        "",
        "### Overview",
        " ".join(_coverage_summary(source, " ".join(source), 6)),
        "",
        "### Topic-Wise Notes",
    ]

    for label, items in topics.items():
        if not items:
            continue
        parts.append(f"#### {label}")
        parts.extend(f"- {item}" for item in items[:6])
        parts.append("")

    parts.extend(
        [
            "### Key Concepts To Remember",
            *[f"- {item}" for item in concept_bullets[:14]],
            "",
            "### Revision Checklist",
            *[f"- {item}" for item in revision_bullets[:10]],
        ]
    )
    return "\n".join(parts).strip()


def _topic_notes(source: list[str]) -> dict[str, list[str]]:
    topic_rules = {
        "JavaScript Basics": ["javascript", "scripting", "dynamic web", "browser", "html", "css"],
        "Control Flow": ["if", "else", "switch", "loop", "for ", "while", "do/while"],
        "Functions": ["function", "parameter", "return", "block of code", "task"],
        "Objects And Arrays": ["object", "array", "property", "method", "constructor"],
        "Built-In Objects": ["date", "math", "boolean", "string", "number"],
        "DOM": ["document object model", "dom", "node", "element", "innerhtml", "getelementbyid"],
        "Events": ["event", "click", "mouse", "keyboard", "form", "submit", "change"],
    }
    topics = {label: [] for label in topic_rules}
    for sentence in source:
        lowered = sentence.lower()
        for label, markers in topic_rules.items():
            if any(marker in lowered for marker in markers) and len(topics[label]) < 8:
                topics[label].append(sentence)
                break
    return topics


def _concept_bullets(topics: dict[str, list[str]], text: str) -> list[str]:
    bullets: list[str] = []
    for label, items in topics.items():
        if not items:
            continue
        bullets.append(f"{label}: {items[0]}")
    if len(bullets) < 8:
        for keyword in keywords(text, 12):
            bullets.append(f"{keyword}: revise its definition, purpose, syntax, and common usage.")
    return _dedupe(bullets)


def _coverage_summary(source: list[str], text: str, limit: int) -> list[str]:
    """Pick useful sentences from across the whole document, not only page one."""
    if len(source) <= limit:
        return source

    important_words = {word.lower() for word in keywords(text, 20)}
    bucket_count = min(limit, max(1, len(source) // 8))
    buckets = _chunk(source, bucket_count)
    selected: list[str] = []

    for bucket in buckets:
        winner = max(bucket, key=lambda sentence: _score(sentence, important_words))
        selected.append(winner)

    remaining = [sentence for sentence in source if sentence not in selected]
    remaining.sort(key=lambda sentence: _score(sentence, important_words), reverse=True)
    selected.extend(remaining[: max(0, limit - len(selected))])

    selected = _dedupe(selected)
    selected.sort(key=source.index)
    return selected[:limit]


def _chunk(items: list[str], count: int) -> list[list[str]]:
    size = max(1, round(len(items) / count))
    return [items[index : index + size] for index in range(0, len(items), size)]


def _score(sentence: str, important_words: set[str]) -> tuple[int, int, int]:
    lowered = sentence.lower()
    keyword_hits = sum(1 for word in important_words if word in lowered)
    definition_hits = sum(
        marker in lowered
        for marker in [" is ", " are ", " used to ", " means ", " refers ", " example", " function", " object"]
    )
    length_penalty = -abs(len(sentence) - 180)
    return keyword_hits, definition_hits, length_penalty


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
