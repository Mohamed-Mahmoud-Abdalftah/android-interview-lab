#!/usr/bin/env python3
"""Import the immutable 485-question bank without inventing educational answers."""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Senior_Android_Interview_Master_Bank.md"
OUT = ROOT / "Interview-Lab" / "questions"
REPORTS = ROOT / "reports"

EXPECTED = {
    "KOT": 30, "AND": 25, "MEM": 26, "COR": 32, "FLO": 32,
    "ARC": 26, "SOL": 20, "PAT": 18, "DI": 20, "COM": 28,
    "DAT": 22, "BG": 18, "SEC": 32, "SYS": 24, "MOD": 21,
    "BLD": 21, "TST": 24, "CIC": 20, "DSA": 16, "LEAD": 15,
    "PAY": 15,
}
TOPIC_RE = re.compile(r"^## (\d{2})\. (.+?)\s+—\s+`([A-Z]+)`\s+·\s+(P[12])")
QUESTION_RE = re.compile(r"^- \[[ x]\] \*\*([A-Z]+-\d{2})\*\* — (.+)$")
GROUP_RE = re.compile(r"^### ([ABC])\. ")


def parse_source(raw: str) -> list[dict]:
    questions = []
    topic = None
    group = None
    phase = None
    priority = None
    for line in raw.splitlines():
        match = TOPIC_RE.match(line)
        if match:
            _, topic, code, priority = match.groups()
            group = None
            if code != next((key for key in EXPECTED if key == code), None):
                raise ValueError(f"unknown topic code: {code}")
            continue
        if topic and (phase_match := re.match(r"^\*\*Phase (\d)\*\*", line)):
            phase = int(phase_match.group(1))
            continue
        if group_match := GROUP_RE.match(line):
            group = group_match.group(1)
            continue
        if question_match := QUESTION_RE.match(line):
            question_id, question = question_match.groups()
            code = question_id.split("-")[0]
            if not topic or not group or not phase or code not in EXPECTED:
                raise ValueError(f"question outside topic/group: {question_id}")
            questions.append({
                "id": question_id,
                "question": question,
                "topic": topic,
                "code": code,
                "group": group,
                "phase": phase,
                "priority": priority,
                "order": len(questions) + 1,
                "route": f"/lab/questions/{question_id.lower()}/",
            })
    counts = Counter(q["code"] for q in questions)
    ids = [q["id"] for q in questions]
    if len(ids) != 485 or len(set(ids)) != 485 or counts != EXPECTED:
        raise ValueError(f"source mismatch: total={len(ids)}, unique={len(set(ids))}, counts={dict(counts)}")
    return questions


def record_for(q: dict) -> str:
    meta = {key: q[key] for key in ("id", "question", "topic", "code", "group", "phase", "priority", "order")}
    meta["editorial_status"] = "source-only"
    frontmatter = "\n".join(f"{key}: {json.dumps(value, ensure_ascii=False)}" for key, value in meta.items())
    return f"---\n{frontmatter}\n---\n\n# {q['id']}\n\n## Original interview question\n\n{q['question']}\n"


def main() -> None:
    questions = parse_source(SOURCE.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    for q in questions:
        path = OUT / f"{q['id']}.md"
        if not path.exists():
            path.write_text(record_for(q), encoding="utf-8")
    (REPORTS / "source-manifest.json").write_text(json.dumps({"source": SOURCE.name, "questions": questions}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (REPORTS / "source-crosswalk.json").write_text(json.dumps({q["id"]: {"record": f"Interview-Lab/questions/{q['id']}.md", "route": q["route"]} for q in questions}, indent=2) + "\n", encoding="utf-8")
    counts = Counter(q["code"] for q in questions)
    inventory = "# Canonical source inventory\n\nGenerated from the supplied bank. Editorial review status is tracked separately.\n\n| Topic | Questions |\n|---|---:|\n"
    inventory += "".join(f"| {code} | {counts[code]} |\n" for code in EXPECTED)
    inventory += f"| **Total** | **{len(questions)}** |\n"
    (REPORTS / "content-inventory.md").write_text(inventory, encoding="utf-8")
    print(f"Parsed {len(questions)} source questions, {len(set(q['id'] for q in questions))} unique IDs, {len(counts)} topics")


if __name__ == "__main__":
    main()
