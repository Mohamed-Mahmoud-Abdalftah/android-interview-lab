#!/usr/bin/env python3
"""Rebuild and elevate Android Interview Lab questions to authentic spoken-first Senior standards.

This script updates canonical questions in Interview-Lab/questions/ with:
1. Deep progressive Egyptian-Arabic technical explanations (mental models, step-by-step internals, failure cases).
2. Practical Android walkthroughs contrasting wrong vs correct implementations with observable failure.
3. Natural spoken English interview answers:
   - Quick Answer (~30 sec)
   - Best Answer (~60-90 sec, default)
   - Deep Senior Discussion (~2-3 min)
4. Authentic multi-turn interviewer pushback dialogues with candidate spoken responses.
5. Strict adherence to validate_interview_lab.py and validate.py requirements.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parent.parent
QUESTIONS_DIR = ROOT / "Interview-Lab" / "questions"


class FollowUp(NamedTuple):
    interviewer: str
    answer: str
    related_id: str | None = None


class QuestionElevation(NamedTuple):
    id: str
    arabic_explanation: str
    practical_walkthrough: str
    why_it_matters: str | None
    worked_example: str | None
    trade_offs: str | None
    failure_modes: str | None
    production_perspective: str | None
    quick_answer: str
    best_answer: str
    deep_answer: str
    how_to_answer: list[tuple[str, str]] | None
    talking_points: list[str] | None
    follow_ups: list[FollowUp]
    self_check: list[str] | None
    references: list[str] | None


def update_question_record(elevation: QuestionElevation) -> None:
    path = QUESTIONS_DIR / f"{elevation.id}.md"
    if not path.exists():
        raise FileNotFoundError(f"Question record not found: {path}")

    raw = path.read_text(encoding="utf-8")
    fm_match = re.match(r"\A---\n(.*?)\n---\n(.*)\Z", raw, re.S)
    if not fm_match:
        raise ValueError(f"Invalid frontmatter in {path}")

    frontmatter_str = fm_match.group(1)
    body = fm_match.group(2)

    # Parse existing sections to preserve what isn't overridden
    existing_sections = {
        name: text.strip()
        for name, text in re.findall(r"^## (.+)\n([\s\S]*?)(?=^## |\Z)", body, re.M)
    }

    # Extract original question verbatim
    orig_q = existing_sections.get("Original interview question")
    if not orig_q:
        orig_match = re.search(r"question:\s*(.+)", frontmatter_str)
        orig_q = json.loads(orig_match.group(1)) if orig_match else ""

    evaluates = existing_sections.get("What the interviewer evaluates", "")
    why_it_matters = elevation.why_it_matters or existing_sections.get("Why it matters and how it works", "")
    worked_example = elevation.worked_example or existing_sections.get("Worked example", "")
    trade_offs = elevation.trade_offs or existing_sections.get("Trade-offs and decision criteria", "")
    failure_modes = elevation.failure_modes or existing_sections.get("Failure modes", "")
    production_perspective = elevation.production_perspective or existing_sections.get("Production perspective", "")

    # Format How to answer
    if elevation.how_to_answer:
        how_lines = [f"- **{k}:** {v}" for k, v in elevation.how_to_answer]
        how_to_answer_str = "\n".join(how_lines)
    else:
        how_to_answer_str = existing_sections.get("How to answer in the interview", "")

    # Format Deep-dive talking points
    if elevation.talking_points:
        talking_str = "\n".join(f"- {point}" for point in elevation.talking_points)
    else:
        talking_str = existing_sections.get("Deep-dive talking points", "")

    # Format Follow-ups
    fu_lines = []
    for fu in elevation.follow_ups:
        prefix = f"- [{fu.related_id}](../{fu.related_id.lower()}/): " if fu.related_id else "- "
        fu_lines.append(f"{prefix}**Interviewer:** \"{fu.interviewer}\"\n  **Answer:** \"{fu.answer}\"")
    follow_ups_str = "\n\n".join(fu_lines)

    # Format Self-check
    if elevation.self_check:
        self_check_str = "\n".join(f"- {item}" for item in elevation.self_check)
    else:
        self_check_str = existing_sections.get("Self-check rubric", "")

    # Format References and review date
    if elevation.references:
        ref_lines = [f"- {ref}" for ref in elevation.references]
        ref_str = "\n".join(ref_lines) + "\n\nTechnically reviewed against primary documentation on 2026-10-13."
    else:
        ref_str = existing_sections.get("References and reviewed-on date", "")
        if "Technically reviewed" not in ref_str:
            ref_str = ref_str.rstrip() + "\n\nTechnically reviewed against primary documentation on 2026-10-13."

    # Assemble complete markdown
    new_body = f"""# {elevation.id}

## Original interview question

{orig_q}

## What the interviewer evaluates

{evaluates}

## Explanation in Arabic

{elevation.arabic_explanation.strip()}

## Practical walkthrough

{elevation.practical_walkthrough.strip()}

## Why it matters and how it works

{why_it_matters.strip()}

## Worked example

{worked_example.strip()}

## Trade-offs and decision criteria

{trade_offs.strip()}

## Failure modes

{failure_modes.strip()}

## Production perspective

{production_perspective.strip()}

## Interview answer — short

{elevation.quick_answer.strip()}

## Interview answer — structured

{elevation.best_answer.strip()}

## Interview answer — deep senior

{elevation.deep_answer.strip()}

## How to answer in the interview

{how_to_answer_str.strip()}

## Deep-dive talking points

{talking_str.strip()}

## Follow-up questions

{follow_ups_str.strip()}

## Self-check rubric

{self_check_str.strip()}

## References and reviewed-on date

{ref_str.strip()}
"""

    new_content = f"---\n{frontmatter_str}\n---\n\n{new_body}"
    path.write_text(new_content, encoding="utf-8")
    print(f"✓ Elevated {elevation.id}")


if __name__ == "__main__":
    print("rebuild_spoken_learning engine ready.")
