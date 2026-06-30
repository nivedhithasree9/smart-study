from __future__ import annotations

from pathlib import Path

FORBIDDEN_TERMS = [
    "api.openai.com",
    "generativelanguage.googleapis.com",
    "api.anthropic.com",
    "api.cohere.ai",
    "huggingface_hub.InferenceClient",
    "openai.ChatCompletion",
]

SCAN_SUFFIXES = {".py", ".md", ".txt", ".toml", ".yml", ".yaml"}
SKIP_DIRS = {".git", ".venv", "__pycache__", "database", "uploads", "models"}


def iter_files() -> list[Path]:
    files: list[Path] = []
    for path in Path(".").rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path == Path("scripts/check_no_cloud.py"):
            continue
        if path.is_file() and path.suffix.lower() in SCAN_SUFFIXES:
            files.append(path)
    return files


def main() -> None:
    violations: list[str] = []
    for path in iter_files():
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        for term in FORBIDDEN_TERMS:
            if term.lower() in text:
                violations.append(f"{path}: {term}")
    if violations:
        raise SystemExit("Cloud API references found:\n" + "\n".join(violations))


if __name__ == "__main__":
    main()
