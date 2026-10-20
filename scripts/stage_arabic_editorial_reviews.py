#!/usr/bin/env python3
"""Stage individually reviewed questions for integration validation.

This command records agent review evidence but never marks a question complete.
Only the release reviewer may promote staged rows after the repository gates pass.
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from audit_arabic_editorial import (
    ARABIC_FIELDS, REVIEW_CHECKS, ROOT, RUBRIC_MINIMUMS, digest, metadata_digest,
)

METADATA = ROOT / "scripts/elevations/data/arabic_lab_metadata.json"
CHECKPOINT = ROOT / "reports/arabic-editorial-checkpoint.json"
EVIDENCE = ROOT / "reports/arabic-editorial-review-evidence.json"


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def nonempty(value: object) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return bool(value) and all(nonempty(item) for item in value)
    if isinstance(value, dict):
        return bool(value) and all(nonempty(item) for item in value.values())
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pair", nargs=2, metavar=("METADATA_DELTA", "REVIEW_EVIDENCE"),
                        action="append", required=True)
    args = parser.parse_args()
    metadata = read(METADATA)
    checkpoint = read(CHECKPOINT)
    evidence = read(EVIDENCE) if EVIDENCE.exists() else {}
    staged: set[str] = set()
    for metadata_path, review_path in args.pair:
        delta = read(Path(metadata_path))
        reviews = read(Path(review_path))
        if set(delta) != set(reviews):
            raise ValueError(f"ID mismatch between {metadata_path} and {review_path}")
        for qid, record in delta.items():
            if qid in staged or qid not in metadata or qid not in checkpoint["questions"]:
                raise ValueError(f"Duplicate or unknown ID: {qid}")
            if checkpoint["questions"][qid]["status"] == "complete":
                raise ValueError(f"Refusing to overwrite completed review: {qid}")
            if record.get("id", qid) != qid or set(record) - {"id"} != set(ARABIC_FIELDS):
                raise ValueError(f"Wrong metadata fields: {qid}")
            if any(not isinstance(record[field], str) or not record[field].strip()
                   for field in ARABIC_FIELDS):
                raise ValueError(f"Empty Arabic field: {qid}")
            review = reviews[qid]
            for key in ("technicalFindings", "editorialChanges", "secondPassNotes",
                        "scoreEvidence", "sources", "limitations"):
                if not nonempty(review.get(key)):
                    raise ValueError(f"Missing {key}: {qid}")
            for name, minimum in RUBRIC_MINIMUMS.items():
                score = review.get("scores", {}).get(name)
                if not isinstance(score, int) or not minimum <= score <= 5:
                    raise ValueError(f"Invalid {name} score: {qid}")
            source_path = ROOT / "Interview-Lab/questions" / f"{qid}.md"
            if not source_path.exists():
                raise ValueError(f"Missing canonical source: {qid}")
            source = source_path.read_text(encoding="utf-8")
            metadata[qid] = {"id": qid, **{field: record[field] for field in ARABIC_FIELDS}}
            row = checkpoint["questions"][qid]
            row.update({
                "status": "verification_pending",
                "reviewedOn": date.today().isoformat(),
                "secondPassOn": date.today().isoformat(),
                "reviewedFields": list(ARABIC_FIELDS),
                "metadataSha256": metadata_digest(metadata[qid]),
                "sourceSha256": digest(source),
                "checks": dict.fromkeys(REVIEW_CHECKS, True),
                "validationOutcome": "pending",
                "validationEvidence": [],
                "remainingIssues": [],
                "humanReviewed": False,
                "reviewKind": "agent_editorial_review",
                "scores": review["scores"],
                "scoreEvidence": review["scoreEvidence"] if isinstance(review["scoreEvidence"], str)
                else "; ".join(f"{name}: {note}" for name, note in review["scoreEvidence"].items()),
            })
            evidence[qid] = review
            staged.add(qid)
    write(METADATA, metadata)
    write(CHECKPOINT, checkpoint)
    write(EVIDENCE, dict(sorted(evidence.items())))
    print(f"Staged {len(staged)} question reviews for validation: {', '.join(sorted(staged))}")


if __name__ == "__main__":
    main()
