"""Upload file extraction entrypoint."""

from __future__ import annotations

from pathlib import Path

from services.ocr import extract_image_text
from services.pdf_reader import extract_pdf_text


SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".png", ".jpg", ".jpeg"}


def extract_text(path: str | Path, tesseract_cmd: str | None = None) -> str:
    file_path = Path(path)
    ext = file_path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}")
    if ext == ".pdf":
        return extract_pdf_text(file_path)
    if ext == ".txt":
        return file_path.read_text(encoding="utf-8", errors="ignore")
    return extract_image_text(file_path, tesseract_cmd)
