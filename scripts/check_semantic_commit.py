from __future__ import annotations

import os
import re
import subprocess

SEMANTIC_COMMIT_PATTERN = re.compile(
    r"^(build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test)(\([a-z0-9._-]+\))?!?: .+"
)


def current_commit_title() -> str:
    title = os.environ.get("CI_COMMIT_TITLE", "").strip()
    if title:
        return title
    return subprocess.check_output(
        ["git", "log", "-1", "--pretty=%s"],
        text=True,
    ).strip()


def main() -> None:
    title = current_commit_title()
    if not SEMANTIC_COMMIT_PATTERN.match(title):
        raise SystemExit(
            "Commit title must follow Conventional Commits, "
            "for example: 'ci: group audit checks into six stages'. "
            f"Got: {title!r}"
        )


if __name__ == "__main__":
    main()
