#!/usr/bin/env python3
"""Report Arabic editorial review signals without treating them as approval."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
METADATA = ROOT / "scripts/elevations/data/arabic_lab_metadata.json"
MANIFEST = ROOT / "reports/source-manifest.json"
CHECKPOINT = ROOT / "reports/arabic-editorial-checkpoint.json"
OUTPUT = ROOT / "reports/arabic-editorial-audit.json"
ARABIC_FIELDS = (
    "questionAr", "topicAr", "evaluates_ar", "concept_ar", "walkthrough_ar",
    "why_it_matters_ar", "worked_example_ar", "trade_offs_ar", "failure_modes_ar",
    "production_perspective_ar", "quick_answer_ar", "best_answer_ar", "deep_answer_ar",
    "how_to_answer_ar", "talking_points_ar", "follow_ups_ar", "self_check_ar", "references_ar",
)
REVIEW_CHECKS = (
    "baselineAuditCompleted", "arabicQuestionReviewed", "technicalExplanationReviewed",
    "quickAnswerReviewed", "bestAnswerReviewed", "deepAnswerReviewed",
    "examplesReviewed", "followUpsReviewed", "technicalAccuracyReviewed",
    "secondEditorialPassCompleted",
)
RUBRIC_MINIMUMS = {
    "naturalEgyptianArabic": 4,
    "technicalTerminology": 5,
    "technicalAccuracy": 5,
    "explanationClarity": 4,
    "interviewUsefulness": 4,
    "answerDepthAndRelevance": 4,
}
TERM_SIGNALS = {
    "التزامن المهيكل": "Structured Concurrency",
    "الموزعات": "Dispatchers",
    "الدوال ذات الرتب العليا": "Higher-Order Functions",
    "التباين المشترك": "Covariance",
    "التباين المعاكس": "Contravariance",
    "اللاتباين": "Invariance",
    "آلة الحالات": "State Machine",
    "حقن التبعيات": "Dependency Injection",
    "شجرة المهام الهرمية": "Job Hierarchy",
    "التثبيت الذري": "Atomic Persistence",
    "مصائد الأخطاء": "Common Pitfalls",
    "المفاضلات الهندسية": "Trade-offs",
    "تجميع البيانات المتدفقة": "Flow Collection",
    "خيط التنفيذ": "Thread",
}
FORMAL_SIGNALS = (
    "يُعد جوهري", "يعتبر ركيزة أساسية", "يتعين على المطور", "حتمية التكرار",
    "تحقيق الاتساق المحكم", "في ضوء المعطيات السابقة", "بدقة متناهية",
)
ABSOLUTE_SIGNALS = (
    "يضمن بشكل كامل", "يمنع تمامًا", "مستحيل تمامًا", "بدون أي تكلفة",
    "صفر تسريبات", "100%", "بالضرورة", "حتمًا",
)
PLACEHOLDER = re.compile(r"\b(?:TODO|TBD|FIXME|lorem ipsum)\b", re.I)


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def metadata_digest(record: dict) -> str:
    return digest(json.dumps({key: record.get(key) for key in ARABIC_FIELDS},
                             ensure_ascii=False, sort_keys=True))


def main() -> int:
    metadata = json.loads(METADATA.read_text(encoding="utf-8"))
    questions = json.loads(MANIFEST.read_text(encoding="utf-8"))["questions"]
    checkpoint = json.loads(CHECKPOINT.read_text(encoding="utf-8"))
    ids = {q["id"] for q in questions}
    rows = checkpoint["questions"]
    structural = []
    if set(metadata) != ids:
        structural.append("metadata IDs differ from canonical source IDs")
    if set(rows) != ids:
        structural.append("checkpoint IDs differ from canonical source IDs")
    signals: dict[str, list[dict[str, str]]] = defaultdict(list)
    seen_answers: dict[tuple[str, str], str] = {}
    status_counts = Counter()
    topic_coverage: dict[str, Counter] = defaultdict(Counter)
    for q in questions:
        qid, topic = q["id"], q["code"]
        record, row = metadata[qid], rows[qid]
        status = row["status"]
        status_counts[status] += 1
        topic_coverage[topic]["total"] += 1
        topic_coverage[topic][status] += 1
        if row.get("topic") != topic:
            structural.append(f"{qid}: checkpoint topic differs from canonical source")
        if set(row.get("checks", {})) != set(REVIEW_CHECKS):
            structural.append(f"{qid}: incomplete checkpoint review checklist")
        if status in {"verification_pending", "complete"}:
            if not all(row["checks"].values()):
                structural.append(f"{qid}: scored review has unchecked steps")
            if set(row.get("reviewedFields", [])) != set(ARABIC_FIELDS):
                structural.append(f"{qid}: scored review does not cover all Arabic fields")
            for name, minimum in RUBRIC_MINIMUMS.items():
                score = row.get("scores", {}).get(name)
                if not isinstance(score, int) or not minimum <= score <= 5:
                    structural.append(f"{qid}: {name} score does not meet the minimum")
            if row.get("remainingIssues"):
                structural.append(f"{qid}: scored review still has unresolved issues")
        if status == "complete" and row.get("validationOutcome") != "passed":
            structural.append(f"{qid}: complete review lacks current validation evidence")
        for field in ARABIC_FIELDS:
            value = record.get(field, "")
            if not isinstance(value, str) or not value.strip():
                signals[qid].append({"field": field, "kind": "missing"})
                continue
            if PLACEHOLDER.search(value):
                signals[qid].append({"field": field, "kind": "placeholder"})
            if value.count("```") % 2:
                signals[qid].append({"field": field, "kind": "unclosed-code-fence"})
            for phrase in TERM_SIGNALS:
                if phrase in value:
                    signals[qid].append({"field": field, "kind": "terminology", "text": phrase})
            for phrase in FORMAL_SIGNALS:
                if phrase in value:
                    signals[qid].append({"field": field, "kind": "formal-style", "text": phrase})
            for phrase in ABSOLUTE_SIGNALS:
                if phrase in value:
                    signals[qid].append({"field": field, "kind": "absolute-claim", "text": phrase})
        for field, low, high in (("quick_answer_ar", 35, 110),
                                 ("best_answer_ar", 90, 280),
                                 ("deep_answer_ar", 180, 650)):
            words = len(record[field].split())
            if not low <= words <= high:
                signals[qid].append({"field": field, "kind": "answer-length", "text": str(words)})
            normalized = " ".join(record[field].casefold().split())
            answer_key = (field, normalized)
            if answer_key in seen_answers:
                signals[qid].append({"field": field, "kind": "duplicate-answer",
                                     "text": seen_answers[answer_key]})
            else:
                seen_answers[answer_key] = qid
        if status in {"first_pass_complete", "verification_pending", "complete"}:
            source = (ROOT / "Interview-Lab/questions" / f"{qid}.md").read_text(encoding="utf-8")
            if row.get("metadataSha256") != metadata_digest(record):
                structural.append(f"{qid}: completed metadata changed since manual review")
            if row.get("sourceSha256") != digest(source):
                structural.append(f"{qid}: completed source changed since manual review")
    report = {
        "scope": {"questions": len(ids), "topics": len(topic_coverage),
                  "arabicFieldsPerQuestion": len(ARABIC_FIELDS)},
        "editorialStatus": dict(status_counts),
        "topicCoverage": {topic: dict(counts) for topic, counts in sorted(topic_coverage.items())},
        "signalCounts": dict(Counter(s["kind"] for items in signals.values() for s in items)),
        "signals": dict(sorted(signals.items())),
        "structuralErrors": structural,
        "note": "Signals are review leads; absent signals do not prove technical or semantic quality.",
    }
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(ids)} questions; {len(topic_coverage)} topics; {status_counts['complete']} complete editorial reviews; "
          f"{sum(map(len, signals.values()))} review signals; {len(structural)} structural errors")
    return 1 if structural else 0


if __name__ == "__main__":
    raise SystemExit(main())
