#!/usr/bin/env python3
"""Validate canonical source fidelity and report true editorial coverage."""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

from import_interview_lab import ROOT, SOURCE, parse_source

REQUIRED = [
    "What the interviewer evaluates", "Explanation in Arabic", "Why it matters and how it works",
    "Worked example", "Trade-offs and decision criteria", "Failure modes",
    "Production perspective", "Interview answer — short", "Interview answer — structured",
    "Interview answer — deep senior",
    "Deep-dive talking points", "Follow-up questions", "Self-check rubric", "References and reviewed-on date",
]


def copied_long_sentences(source: str, answer: str) -> list[str]:
    """Find substantive sentences copied into an interview response verbatim."""
    def sentences(value: str) -> list[str]:
        value = re.sub(r"```[\s\S]*?```", "", value)
        return [part.strip().strip('“”"') for part in re.split(r"(?<=[.!?])\s+", value)
                if len(part.split()) >= 7]

    originals = {re.sub(r"\s+", " ", part).casefold() for part in sentences(source)}
    return [part for part in sentences(answer)
            if re.sub(r"\s+", " ", part).casefold() in originals]


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


def review_footer_extra(section: str) -> str:
    """Return stray text following the final technical-review statement."""
    match = re.search(r"(?m)^Technically reviewed[^\n]*\n([\s\S]+)$", section)
    return match.group(1).strip() if match else ""


def validate() -> dict:
    source = parse_source(SOURCE.read_text(encoding="utf-8"))
    errors = []
    reviewed = []
    source_only = []
    question_status = {}
    topic_coverage = {code: {"total": 0, "reviewed": 0, "sourceOnly": 0, "qualityIssues": 0}
                      for code in sorted({q["code"] for q in source})}
    files = sorted((ROOT / "Interview-Lab/questions").glob("*.md"))
    source_ids = {q["id"] for q in source}
    for extra in set(path.stem for path in files) - source_ids:
        errors.append(f"extra canonical record: {extra}")
    fingerprints = Counter()
    code_fingerprints = Counter()
    rubric_ids = defaultdict(list)
    placeholder_count = 0
    for q in source:
        topic_coverage[q["code"]]["total"] += 1
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
        question_status[q["id"]] = {"topic": q["code"], "status": status,
                                     "automatedQuality": "not-authored", "hasKotlinCode": "```kotlin" in body}
        if status == "source-only":
            source_only.append(q["id"])
            topic_coverage[q["code"]]["sourceOnly"] += 1
        elif status == "reviewed":
            reviewed.append(q["id"])
            topic_coverage[q["code"]]["reviewed"] += 1
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
            if review_footer_extra(sections.get("References and reviewed-on date", "")):
                errors.append(f"stray text after review footer: {q['id']}")
            for related in re.findall(r"\[([A-Z]+-\d{2})\]", sections.get("Follow-up questions", "")):
                if related not in source_ids:
                    errors.append(f"invalid related ID {related}: {q['id']}")
            if sections.get("Follow-up questions", "").count("**Answer:**") < 2:
                errors.append(f"fewer than two answered follow-ups: {q['id']}")
            explanatory = " ".join(sections.get(name, "") for name in (
                "Why it matters and how it works", "Worked example",
                "Trade-offs and decision criteria", "Failure modes", "Production perspective"))
            for depth in ("structured", "deep senior"):
                copied = copied_long_sentences(explanatory, sections.get(f"Interview answer — {depth}", ""))
                if copied:
                    errors.append(f"copied {len(copied)} long sentences into {depth}: {q['id']}")
            explanation = body.split('## Explanation in Arabic\n', 1)[-1].split('\n## ', 1)[0].strip()
            fingerprints[re.sub(r"\s+", " ", explanation)] += 1
            rubric = re.sub(r"\s+", " ", sections.get("Self-check rubric", "")).strip().casefold()
            if rubric:
                rubric_ids[rubric].append(q["id"])
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
    for ids in rubric_ids.values():
        if len(ids) > 1:
            errors.extend(f"duplicate self-check rubric shared by {len(ids)} questions: {qid}" for qid in ids)
    for qid, item in question_status.items():
        if item["status"] == "reviewed":
            item["automatedQuality"] = "needs-fix" if any(error.endswith(f": {qid}") for error in errors) else "passes-checks"
            topic_coverage[item["topic"]]["qualityIssues"] += item["automatedQuality"] == "needs-fix"
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
        "sourceOnlyIds": source_only,
        "qualityPassing": sum(item["automatedQuality"] == "passes-checks" for item in question_status.values()),
        "questionStatus": question_status,
        "topicCoverage": topic_coverage,
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
