#!/usr/bin/env python3
"""Remove exact explanatory sentence copies appended to interview answers.

This is a narrow editorial repair for the 2026-10-11 import. It never rewrites
an answer: a sentence is removed only when the same long sentence occurs in a
separate explanatory section of that question. Review the resulting diff.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from validate_interview_lab import ROOT, copied_long_sentences

EXPLANATORY = (
    "Why it matters and how it works", "Worked example",
    "Trade-offs and decision criteria", "Failure modes", "Production perspective",
)
GENERIC_FILLER = (
    "The mechanics matter.",
    "The choice has a trade-off.",
    "The decision has a trade-off.",
    "Consider a concrete case.",
    "A failure case illustrates the risk.",
    "In production, the response is concrete.",
)


def clean_record(raw: str) -> tuple[str, int]:
    sections = dict(re.findall(r"^## (.+)\n([\s\S]*?)(?=^## |\Z)", raw, re.M))
    source = " ".join(sections.get(name, "") for name in EXPLANATORY)
    removed = 0
    for name in ("Interview answer — short", "Interview answer — structured", "Interview answer — deep senior"):
        answer = sections.get(name)
        if answer is None:
            continue
        copies = copied_long_sentences(source, answer)
        replacement = answer
        for sentence in copies:
            if sentence not in replacement:
                raise ValueError(f"sentence could not be removed from {name}: {sentence}")
            replacement = replacement.replace(sentence, "", 1)
            removed += 1
        for sentence in GENERIC_FILLER:
            if sentence in replacement:
                replacement = replacement.replace(sentence, "")
                removed += 1
        if replacement == answer:
            continue
        replacement = re.sub(r" {2,}", " ", replacement)
        replacement = re.sub(r" +\n", "\n", replacement)
        before = f"## {name}\n{answer}"
        after = f"## {name}\n{replacement}"
        if raw.count(before) != 1:
            raise ValueError(f"answer section was not unique: {name}")
        raw = raw.replace(before, after, 1)
    return raw, removed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    files = 0
    sentences = 0
    for path in sorted((ROOT / "Interview-Lab/questions").glob("*.md")):
        old = path.read_text(encoding="utf-8")
        try:
            new, count = clean_record(old)
        except ValueError as exc:
            raise ValueError(f"{path}: {exc}") from exc
        if count:
            files += 1
            sentences += count
            if args.apply:
                path.write_text(new, encoding="utf-8")
    print(f"{files} records; {sentences} repeated sentences; applied={args.apply}")


if __name__ == "__main__":
    main()
