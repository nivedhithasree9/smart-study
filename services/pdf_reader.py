"""Local PDF text extraction."""

from __future__ import annotations

from pathlib import Path


def extract_pdf_text(path: str | Path) -> str:
    try:
        import fitz  # PyMuPDF
    except ImportError as exc:
        raise RuntimeError("PyMuPDF is not installed. Run: pip install PyMuPDF") from exc

    text_parts: list[str] = []
    with fitz.open(path) as document:
        for page in document:
            text_parts.append(page.get_text("text"))
    return "\n".join(text_parts).strip()
