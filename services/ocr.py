"""Local OCR for image notes using Tesseract."""

from __future__ import annotations

from pathlib import Path


def extract_image_text(path: str | Path, tesseract_cmd: str | None = None) -> str:
    try:
        import pytesseract
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError("OCR needs pillow and pytesseract installed locally.") from exc

    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    try:
        return pytesseract.image_to_string(Image.open(path)).strip()
    except Exception as exc:  # Tesseract path errors vary by OS.
        raise RuntimeError(f"Tesseract OCR failed: {exc}") from exc
