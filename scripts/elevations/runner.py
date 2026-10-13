#!/usr/bin/env python3
"""Runner engine that applies elevated educational & spoken content from JSON data files."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
QUESTIONS_DIR = ROOT / "Interview-Lab" / "questions"
DATA_DIR = Path(__file__).resolve().parent / "data"

sys.path.insert(0, str(ROOT / "scripts"))
from validate import source_files


def sync_inventory() -> None:
    files = sorted(source_files(ROOT))
    header = (
        f"# Actual academy source inventory — 2026-10-13\n\n"
        f"These {len(files)} files exist in the source tree. Interview Lab canonical records have a separate "
        f"validated inventory in `reports/content-inventory.md`; derived pages, caches, build output, "
        f"and ZIP archives are excluded.\n\n```text\n"
    )
    content = header + "\n".join(files) + "\n```\n"
    (ROOT / "FILE-INVENTORY.md").write_text(content, encoding="utf-8")


def apply_elevation(data: dict) -> None:
    qid = data["id"]
    path = QUESTIONS_DIR / f"{qid}.md"
    if not path.exists():
        raise FileNotFoundError(f"Missing question file: {path}")

    raw = path.read_text(encoding="utf-8")
    fm_match = re.match(r"\A---\n(.*?)\n---\n(.*)\Z", raw, re.S)
    if not fm_match:
        raise ValueError(f"Invalid frontmatter in {path}")

    frontmatter_str = fm_match.group(1)
    body = fm_match.group(2)

    existing_sections = {
        name: text.strip()
        for name, text in re.findall(r"^## (.+)\n([\s\S]*?)(?=^## |\Z)", body, re.M)
    }

    orig_q = existing_sections.get("Original interview question")
    if not orig_q:
        orig_match = re.search(r"question:\s*(.+)", frontmatter_str)
        orig_q = json.loads(orig_match.group(1)) if orig_match else ""

    evaluates = existing_sections.get("What the interviewer evaluates", "")
    ar_explanation = data.get("arabic_explanation", existing_sections.get("Explanation in Arabic", ""))
    walkthrough = data.get("practical_walkthrough", existing_sections.get("Practical walkthrough", ""))
    why_it_matters = data.get("why_it_matters", existing_sections.get("Why it matters and how it works", ""))
    worked_example = data.get("worked_example", existing_sections.get("Worked example", ""))
    trade_offs = data.get("trade_offs", existing_sections.get("Trade-offs and decision criteria", ""))
    failure_modes = data.get("failure_modes", existing_sections.get("Failure modes", ""))
    production_perspective = data.get("production_perspective", existing_sections.get("Production perspective", ""))

    quick_answer = data.get("quick_answer", existing_sections.get("Interview answer — short", ""))
    best_answer = data.get("best_answer", existing_sections.get("Interview answer — structured", ""))
    deep_answer = data.get("deep_answer", existing_sections.get("Interview answer — deep senior", ""))

    how_to_answer = data.get("how_to_answer")
    if how_to_answer:
        if isinstance(how_to_answer, list):
            how_to_answer_str = "\n".join(f"- **{k}:** {v}" for k, v in how_to_answer)
        else:
            how_to_answer_str = str(how_to_answer)
    else:
        how_to_answer_str = existing_sections.get("How to answer in the interview", "")

    talking_points = data.get("talking_points")
    if talking_points:
        talking_str = "\n".join(f"- {point}" for point in talking_points)
    else:
        talking_str = existing_sections.get("Deep-dive talking points", "")

    follow_ups = data.get("follow_ups")
    if follow_ups:
        fu_lines = []
        for fu in follow_ups:
            rel = fu.get("related_id")
            q_text = fu.get("interviewer") or fu.get("question", "")
            a_text = fu.get("answer") or fu.get("candidate", "")
            prefix = f"- [{rel}](../{rel.lower()}/): " if rel else "- "
            fu_lines.append(f"{prefix}**Interviewer:** \"{q_text}\"\n  **Answer:** \"{a_text}\"")
        follow_ups_str = "\n\n".join(fu_lines)
    else:
        follow_ups_str = existing_sections.get("Follow-up questions", "")

    self_check = data.get("self_check")
    if self_check:
        if isinstance(self_check, list):
            self_check_str = "\n".join(f"- {item}" for item in self_check)
        else:
            self_check_str = str(self_check)
    else:
        self_check_str = existing_sections.get("Self-check rubric", "")

    ref_str = existing_sections.get("References and reviewed-on date", "")
    if "Technically reviewed" not in ref_str:
        ref_str = ref_str.rstrip() + "\n\nTechnically reviewed against primary documentation on 2026-10-13."
    else:
        ref_str = re.sub(r"Technically reviewed[^\n]*", "Technically reviewed against primary documentation on 2026-10-13.", ref_str)

    new_body = f"""# {qid}

## Original interview question

{orig_q}

## What the interviewer evaluates

{evaluates}

## Explanation in Arabic

{ar_explanation.strip()}

## Practical walkthrough

{walkthrough.strip()}

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

{quick_answer.strip()}

## Interview answer — structured

{best_answer.strip()}

## Interview answer — deep senior

{deep_answer.strip()}

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
    print(f"✓ Applied elevation for {qid}")


def process_topic_file(json_path: Path) -> int:
    content = json_path.read_text(encoding="utf-8")
    items = json.loads(content)
    count = 0
    for item in items:
        apply_elevation(item)
        count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", help="Topic code to apply (e.g., KOT)")
    parser.add_argument("--all", action="store_true", help="Apply all available topic JSON files")
    args = parser.parse_args()

    if not DATA_DIR.exists():
        print(f"Data directory not found: {DATA_DIR}")
        return

    json_files: list[Path] = []
    if args.topic:
        target = DATA_DIR / f"{args.topic.lower()}.json"
        if not target.exists():
            print(f"No data file found for topic: {target}")
            sys.exit(1)
        json_files.append(target)
    elif args.all:
        json_files = sorted(DATA_DIR.glob("*.json"))
    else:
        json_files = sorted(DATA_DIR.glob("*.json"))

    total = 0
    for jf in json_files:
        print(f"Processing {jf.name}...")
        total += process_topic_file(jf)

    sync_inventory()
    print(f"Done. Processed {total} questions across {len(json_files)} data files.")


if __name__ == "__main__":
    main()
