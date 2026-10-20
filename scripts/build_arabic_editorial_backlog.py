#!/usr/bin/env python3
"""Build a deterministic, honest per-question editorial worklist."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

from audit_arabic_editorial import ARABIC_FIELDS, ROOT, digest, metadata_digest


KNOWN_REGRESSIONS = {
    "KOT-05": "data class immutability, shallow copy, object and companion semantics",
    "COM-02": "unsupported recomposition and 60fps performance guarantees",
    "DI-08": "qualifier binding keys and exaggerated @Named claims",
    "FLO-02": "cold Flow semantics and formal Arabic style",
    "AND-02": "lifecycle ordering, process death, multi-window and Fragment view owner",
}
REVIEW_LEADS = {
    "absolute_or_guarantee": re.compile(r"\b(?:always|never|guarantee[ds]?|100%)\b|(?:دائمًا|دائما|مستحيل|يضمن|مضمون)", re.I),
    "performance_number": re.compile(r"\b(?:60|120)\s*(?:fps|frames)\b|(?:صفر تسريبات|بدون أي تكلفة)", re.I),
    "process_or_lifecycle": re.compile(r"process death|process kill|onDestroy\(\)|موت العملية|قتل الـ?Process", re.I),
    "payment_or_retry": re.compile(r"\b(?:payment|settlement|reversal|retry|idempoten\w*)\b|(?:دفع|تسوية|عكس العملية)", re.I),
}


def main() -> None:
    questions = json.loads((ROOT / "reports/source-manifest.json").read_text())["questions"]
    metadata = json.loads((ROOT / "scripts/elevations/data/arabic_lab_metadata.json").read_text())
    checkpoint = json.loads((ROOT / "reports/arabic-editorial-checkpoint.json").read_text())["questions"]
    rows = []
    for item in sorted(questions, key=lambda q: q["id"]):
        qid = item["id"]
        review = checkpoint[qid]
        record = metadata[qid]
        source = (ROOT / "Interview-Lab/questions" / f"{qid}.md").read_text()
        claim_text = source + "\n" + "\n".join(str(record.get(field, "")) for field in ARABIC_FIELDS)
        status = review["status"]
        current = (review.get("sourceSha256") == digest(source)
                   and review.get("metadataSha256") == metadata_digest(record))
        checked = review.get("checks", {})
        reviewed_fields = set(review.get("reviewedFields", []))
        remaining = list(review.get("remainingIssues", []))
        if status != "complete" and not remaining:
            remaining.append("Individual technical, language, and second-pass review pending")
        if not current and status == "complete":
            remaining.append("Completed review hashes are stale")
        if qid in KNOWN_REGRESSIONS and status != "complete":
            remaining.append(KNOWN_REGRESSIONS[qid])
        rows.append({
            "id": qid,
            "topic": item["code"],
            "status": status,
            "technicalReview": bool(checked.get("technicalAccuracyReviewed")),
            "egyptianArabicReview": bool(checked.get("arabicQuestionReviewed")),
            "terminologyReview": bool(checked.get("technicalExplanationReviewed")),
            "fieldCoverage": {
                "present": sum(bool(record.get(field, "").strip()) for field in ARABIC_FIELDS),
                "reviewed": sum(field in reviewed_fields for field in ARABIC_FIELDS),
                "required": len(ARABIC_FIELDS),
            },
            "snippetValidation": "not_individually_recorded",
            "crossLanguageConsistency": bool(checked.get("technicalExplanationReviewed")
                                             and checked.get("technicalAccuracyReviewed")),
            "secondPassReview": bool(checked.get("secondEditorialPassCompleted")),
            "hashesCurrent": current if status == "complete" else None,
            "remainingDefects": remaining,
            "highRiskReviewLeads": [name for name, pattern in REVIEW_LEADS.items()
                                    if pattern.search(claim_text)],
        })
    output = {
        "schemaVersion": 1,
        "scope": {"questions": len(rows), "topics": len({row["topic"] for row in rows}),
                  "arabicFieldsPerQuestion": len(ARABIC_FIELDS)},
        "statusCounts": dict(sorted(Counter(row["status"] for row in rows).items())),
        "note": "Checklist values are checkpoint claims; they do not replace semantic review. Snippet compilation is not individually recorded.",
        "questions": rows,
    }
    path = ROOT / "reports/arabic-editorial-backlog.json"
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{path}: {len(rows)} questions")


if __name__ == "__main__":
    main()
