from __future__ import annotations

from collections import Counter
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
LESSON_FILES = sorted((ROOT / "modules").glob("module-*/lesson-*.md"))
REQUIRED = [
    "## Outcome",
    "## Direct answer",
    "## Best practice",
    "## Common failure",
    "## Independent application",
    "## Completion check",
]


def normalize_sentence(text: str) -> str:
    text = re.sub(r"[`*_>#\-]", " ", text.lower())
    text = re.sub(r"\s+", " ", text).strip()
    return text


def audit() -> list[str]:
    failures: list[str] = []
    titles: Counter[str] = Counter()
    substantial_sentences: dict[str, list[str]] = {}

    if len(LESSON_FILES) != 36:
        failures.append(f"expected 36 canonical lessons, found {len(LESSON_FILES)}")

    for path in LESSON_FILES:
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        if not lines or not lines[0].startswith("# Lesson "):
            failures.append(f"{path}: missing canonical lesson title")
        else:
            titles[lines[0]] += 1

        for heading in REQUIRED:
            if heading not in text:
                failures.append(f"{path}: missing {heading}")

        if len(text.split()) > 650:
            failures.append(f"{path}: exceeds 650-word simplicity ceiling")

        for sentence in re.split(r"(?<=[.!?])\s+", text):
            normalized = normalize_sentence(sentence)
            if 16 <= len(normalized.split()) <= 45:
                substantial_sentences.setdefault(normalized, []).append(str(path))

    for title, count in titles.items():
        if count > 1:
            failures.append(f"duplicate title ({count}): {title}")

    allowed_repeats = {
        normalize_sentence("You are ready to continue when"),
    }
    for sentence, paths in substantial_sentences.items():
        if len(set(paths)) > 1 and sentence not in allowed_repeats:
            failures.append(
                "possible repeated teaching sentence in "
                + ", ".join(sorted(set(paths)))
                + f": {sentence[:120]}"
            )

    return failures


if __name__ == "__main__":
    problems = audit()
    if problems:
        print("CONTENT AUDIT FAILED")
        for problem in problems:
            print(f"- {problem}")
        sys.exit(1)
    print(f"CONTENT AUDIT PASSED: {len(LESSON_FILES)} lessons checked")
