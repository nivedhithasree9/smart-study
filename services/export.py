"""Export utilities for generated study resources."""

from __future__ import annotations

import csv
from io import StringIO


def flashcards_to_csv(flashcards: list[dict[str, str]]) -> str:
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=["question", "answer"])
    writer.writeheader()
    writer.writerows(flashcards)
    return buffer.getvalue()


def summary_to_text(content: dict[str, object]) -> str:
    return "\n\n".join(
        [
            str(content.get("title", "Study Summary")),
            "Short Summary\n" + str(content.get("summary_short", "")),
            "Medium Summary\n" + str(content.get("summary_medium", "")),
            "Detailed Summary\n" + str(content.get("summary_detailed", "")),
        ]
    )
