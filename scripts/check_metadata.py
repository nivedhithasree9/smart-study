from __future__ import annotations

from pathlib import Path

REQUIRED_FILES = [
    "README.md",
    "LICENSE",
    "CONTRIBUTING.md",
    "CHANGELOG.md",
    "pyproject.toml",
    ".gitlab-ci.yml",
    ".pre-commit-config.yaml",
    "docs/issues.md",
    "docs/work-division.md",
    "specs/001-offline-smart-study-assistant/spec.md",
]


def main() -> None:
    missing = [path for path in REQUIRED_FILES if not Path(path).exists()]
    if missing:
        raise SystemExit(f"Missing required metadata files: {', '.join(missing)}")

    readme = Path("README.md").read_text(encoding="utf-8")
    license_text = Path("LICENSE").read_text(encoding="utf-8")
    required_readme_phrases = ["CPU-first", "offline", "AGPL-3.0-or-later", "llama.cpp", "SQLite"]
    missing_phrases = [phrase for phrase in required_readme_phrases if phrase not in readme]
    if missing_phrases:
        raise SystemExit(f"README missing required phrases: {', '.join(missing_phrases)}")
    if "AGPL-3.0-or-later" not in license_text:
        raise SystemExit("LICENSE must declare AGPL-3.0-or-later")


if __name__ == "__main__":
    main()
