#!/usr/bin/env python3
"""Validate canonical source fidelity and report true editorial coverage."""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

from import_interview_lab import ROOT, SOURCE, parse_source

REQUIRED = [
    "What the interviewer evaluates", "Explanation in Arabic", "Why it matters and how it works",
    "Worked example", "Trade-offs and decision criteria", "Failure modes",
    "Production perspective", "Interview answer — short", "Interview answer — structured",
    "Deep-dive talking points", "Follow-up questions", "Self-check rubric", "References and reviewed-on date",
]


def read_record(path: Path) -> tuple[dict, str]:
    raw = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n(.*)\Z", raw, re.S)
    if not match:
        raise ValueError(f"invalid frontmatter: {path}")
    metadata = {}
    for line in match.group(1).splitlines():
        key, separator, value = line.partition(": ")
        if not separator:
            raise ValueError(f"invalid metadata line: {path}: {line}")
        metadata[key] = json.loads(value)
    return metadata, match.group(2)


def validate() -> dict:
    source = parse_source(SOURCE.read_text(encoding="utf-8"))
    errors = []
    reviewed = []
    source_only = []
    files = sorted((ROOT / "Interview-Lab/questions").glob("*.md"))
    source_ids = {q["id"] for q in source}
    for extra in set(path.stem for path in files) - source_ids:
        errors.append(f"extra canonical record: {extra}")
    fingerprints = Counter()
    code_fingerprints = Counter()
    placeholder_count = 0
    for q in source:
        path = ROOT / "Interview-Lab/questions" / f"{q['id']}.md"
        if not path.exists():
            errors.append(f"missing record: {q['id']}")
            continue
        try:
            meta, body = read_record(path)
        except (ValueError, json.JSONDecodeError) as exc:
            errors.append(str(exc))
            continue
        for key in ("id", "question", "topic", "code", "group", "phase", "priority", "order"):
            if meta.get(key) != q[key]:
                errors.append(f"source mismatch {q['id']}: {key}")
        if f"## Original interview question\n\n{q['question']}" not in body:
            errors.append(f"verbatim question absent: {q['id']}")
        status = meta.get("editorial_status")
        if status == "source-only":
            source_only.append(q["id"])
        elif status == "reviewed":
            reviewed.append(q["id"])
            sections = {name: text.strip() for name, text in re.findall(r"^## (.+)\n([\s\S]*?)(?=^## |\Z)", body, re.M)}
            for section in REQUIRED:
                if section not in sections:
                    errors.append(f"missing {section}: {q['id']}")
                elif len(sections[section]) < 55:
                    errors.append(f"thin {section}: {q['id']}")
            if re.search(r"\b(?:TODO|TBD|lorem ipsum)\b", body, re.I):
                errors.append(f"placeholder content: {q['id']}")
                placeholder_count += 1
            if not re.search(r"[\u0600-\u06ff]", sections.get("Explanation in Arabic", "")):
                errors.append(f"Arabic explanation absent: {q['id']}")
            if not re.search(r"https://(?:developer\.android\.com|kotlinlang\.org|github\.com/Kotlin|docs\.gradle\.org|mas\.owasp\.org|docs\.stripe\.com)/", body):
                errors.append(f"no primary reference: {q['id']}")
            if not re.search(r"Technically reviewed.*\b\d{4}-\d{2}-\d{2}\b", sections.get("References and reviewed-on date", "")):
                errors.append(f"review date absent: {q['id']}")
            for related in re.findall(r"\[([A-Z]+-\d{2})\]", sections.get("Follow-up questions", "")):
                if related not in source_ids:
                    errors.append(f"invalid related ID {related}: {q['id']}")
            explanation = body.split('## Explanation in Arabic\n', 1)[-1].split('\n## ', 1)[0].strip()
            fingerprints[re.sub(r"\s+", " ", explanation)] += 1
            for code in re.findall(r"```kotlin\n([\s\S]*?)```", body):
                code_fingerprints[code.strip()] += 1
        else:
            errors.append(f"invalid editorial status: {q['id']}")
    for explanation, count in fingerprints.items():
        if explanation and count > 1:
            errors.append(f"duplicate Arabic explanation used {count} times")
    for code, count in code_fingerprints.items():
        if code and count > 1:
            errors.append(f"duplicate Kotlin example used {count} times")
    report = {
        "sourceIdsFound": len(source),
        "uniqueIds": len(source_ids),
        "topics": len({q["code"] for q in source}),
        "records": len(files),
        "reviewed": len(reviewed),
        "sourceOnly": len(source_only),
        "missing": len(source_ids - {path.stem for path in files}),
        "placeholderCount": placeholder_count,
        "errors": errors,
        "reviewedIds": reviewed,
    }
    (ROOT / "reports/content-coverage.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    report = validate()
    print(f"{report['sourceIdsFound']} source IDs; {report['records']} records; {report['reviewed']} reviewed; {report['sourceOnly']} source-only; {len(report['errors'])} errors")
    for error in report["errors"][:30]:
        print(f"- {error}")
    if "--require-complete" in sys.argv and report["reviewed"] != 485:
        print(f"release blocked: {485 - report['reviewed']} canonical answers are not fully reviewed")
        raise SystemExit(1)
    raise SystemExit(bool(report["errors"]))
