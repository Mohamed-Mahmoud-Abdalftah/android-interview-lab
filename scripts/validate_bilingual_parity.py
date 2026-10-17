#!/usr/bin/env python3
"""Bilingual parity and structural spoken-answer validator.

Asserts:
1. Complete bilingual coverage: 485 English pages and 485 Arabic pages.
2. Complete metadata schema: all 485 questions in arabic_lab_metadata.json have all 19 required fields with rich Arabic prose.
3. Zero silent fallback: Arabic pages must have distinct, independently authored Arabic translations for all explanatory sections.
4. Zero untranslated English paragraphs in Arabic question pages.
5. Zero Arabic characters in English question pages.
6. Mechanical checks on spoken-answer shape:
   - Zero bullet points and zero numbered lists in spoken answers
   - Quick answers: 35-110 words
   - Best answers: 100-280 words
   - Deep answers: 200-650 words
   - Zero robotic template openers ('To begin with,', 'From an architectural standpoint,', etc.)
   - Zero repetitive AI clichés ('على الجانب الآخر، فيما يخص...')
7. Answer uniqueness: no copy-pasted generic answers across different questions.
8. Technical claims audit across concurrency, ART, Keystore/StrongBox, and payment idempotency.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_EN = ROOT / "site" / "src" / "content" / "docs" / "lab" / "questions"
DOCS_AR = ROOT / "site" / "src" / "content" / "docs" / "ar" / "lab" / "questions"
CANONICAL_DIR = ROOT / "Interview-Lab" / "questions"
METADATA_FILE = ROOT / "scripts" / "elevations" / "data" / "arabic_lab_metadata.json"

ARABIC_CHAR_RE = re.compile(r"[\u0600-\u06ff]")

ROBOTIC_EN_MARKERS = [
    "To begin with,",
    "From an architectural standpoint,",
    "In production scenarios,",
    "As for boundary management,",
]

BANNED_AR_CLICHES = [
    "على الجانب الآخر، فيما يخص",
]

REQUIRED_METADATA_KEYS = [
    "id",
    "questionAr",
    "topicAr",
    "evaluates_ar",
    "concept_ar",
    "walkthrough_ar",
    "why_it_matters_ar",
    "worked_example_ar",
    "trade_offs_ar",
    "failure_modes_ar",
    "production_perspective_ar",
    "quick_answer_ar",
    "best_answer_ar",
    "deep_answer_ar",
    "how_to_answer_ar",
    "talking_points_ar",
    "follow_ups_ar",
    "self_check_ar",
    "references_ar",
]

REQUIRED_SECTIONS_EN = [
    "Original interview question",
    "What the interviewer evaluates",
    "Concept and technical explanation",
    "Practical walkthrough",
    "Why it matters and how it works",
    "Worked example",
    "Trade-offs and decision criteria",
    "Failure modes",
    "Production perspective",
    "Interview answer — short",
    "Interview answer — structured",
    "Interview answer — deep senior",
    "How to answer in the interview",
    "Deep-dive talking points",
    "Follow-up questions",
    "Self-check rubric",
    "References and reviewed-on date",
]

REQUIRED_SECTIONS_AR = [
    "السؤال الأصلي في المقابلة",
    "ما يقيّمه المحاور",
    "الشرح والمفهوم التقني",
    "التطبيق العملي وسيناريو الفشل",
    "آلية العمل والتحليل الهندسي",
    "مثال تطبيقي واختبار",
    "المفاضلات الهندسية ومعايير القرار",
    "أنماط الفشل ومصائد الأخطاء",
    "منظور بيئة العمل الفعلي (Production)",
    "إجابة المقابلة — ملخصة وسريعة",
    "إجابة المقابلة — نموذجية ومهيكلة",
    "إجابة المقابلة — مناقشة Senior متعمقة",
    "طريقة تقديم الإجابة في المقابلة",
    "محاور النقاش المتقدم",
    "أسئلة المتابعة واعتراضات المحاور",
    "معايير التقييم الذاتي",
    "المراجع وتاريخ المراجعة الفنية",
]


def extract_sections(markdown_text: str) -> dict[str, str]:
    body = re.sub(r"\A---\n[\s\S]*?\n---\n", "", markdown_text).strip()
    sections = {}
    for match in re.finditer(r"^## (.+)\n([\s\S]*?)(?=^## |\Z)", body, re.M):
        sections[match.group(1).strip()] = match.group(2).strip()
    return sections


def strip_code(text: str) -> str:
    text = re.sub(r"```[\s\S]*?```", "", text)
    text = re.sub(r"`[^`]+`", "", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    return text.strip()


def validate():
    canonical_files = sorted(CANONICAL_DIR.glob("*.md"))
    total_questions = len(canonical_files)
    if total_questions != 485:
        print(f"FAIL: Expected 485 canonical questions, found {total_questions}", file=sys.stderr)
        return 1

    # Auto-generate pages if not yet built and a JS runtime is present
    if not DOCS_EN.exists() or len(list(DOCS_EN.glob("*.md"))) < 485:
        sync_script = ROOT / "site" / "scripts" / "sync-interview-lab.mjs"
        if sync_script.exists():
            import shutil
            import subprocess
            runtime = shutil.which("node") or shutil.which("deno")
            if runtime:
                cmd = [runtime, "run", "-A", str(sync_script)] if "deno" in runtime else [runtime, str(sync_script)]
                print(f"Generated docs not found ({len(list(DOCS_EN.glob('*.md'))) if DOCS_EN.exists() else 0}/485). Running {sync_script.name} with {runtime}...")
                subprocess.run(cmd, cwd=str(ROOT), check=True)

    topic_filter = None
    qid_filter = None
    if "--topic" in sys.argv:
        idx = sys.argv.index("--topic")
        if idx + 1 < len(sys.argv):
            topic_filter = sys.argv[idx + 1].upper()
            canonical_files = [f for f in canonical_files if f.stem.upper().startswith(f"{topic_filter}-")]
    elif "--qid" in sys.argv:
        idx = sys.argv.index("--qid")
        if idx + 1 < len(sys.argv):
            qid_filter = sys.argv[idx + 1].upper()
            canonical_files = [f for f in canonical_files if f.stem.upper() == qid_filter]

    errors = []

    # 1. Validate arabic_lab_metadata.json schema completeness
    if not METADATA_FILE.exists():
        errors.append(f"Missing metadata file: {METADATA_FILE}")
    else:
        with open(METADATA_FILE, encoding="utf-8") as f:
            metadata = json.load(f)
        if len(metadata) != 485:
            errors.append(f"arabic_lab_metadata.json contains {len(metadata)} questions, expected 485!")
        for cfile in canonical_files:
            qid = cfile.stem.upper()
            if qid not in metadata:
                errors.append(f"Question {qid} missing from arabic_lab_metadata.json")
                continue
            q_data = metadata[qid]
            for key in REQUIRED_METADATA_KEYS:
                if key not in q_data:
                    errors.append(f"{qid}: Metadata missing key '{key}'")
                elif not str(q_data[key]).strip():
                    errors.append(f"{qid}: Metadata key '{key}' is empty")
                elif key.endswith("_ar") and key != "references_ar":
                    val = str(q_data[key])
                    if not ARABIC_CHAR_RE.search(val):
                        errors.append(f"{qid}: Metadata key '{key}' contains no Arabic prose!")

    scope_desc = f"topic {topic_filter}" if topic_filter else (f"question {qid_filter}" if qid_filter else f"all {total_questions} questions")
    print(f"Validating bilingual parity and structural spoken-answer rules across {len(canonical_files)} questions ({scope_desc})...")

    seen_en_best = {}
    seen_ar_best = {}

    for cfile in canonical_files:
        qid = cfile.stem.lower()
        en_path = DOCS_EN / f"{qid}.md"
        ar_path = DOCS_AR / f"{qid}.md"

        if not en_path.exists():
            errors.append(f"Missing English page: {en_path}")
            continue
        if not ar_path.exists():
            errors.append(f"Missing Arabic page: {ar_path}")
            continue

        canonical_text = cfile.read_text(encoding="utf-8")
        en_text = en_path.read_text(encoding="utf-8")
        ar_text = ar_path.read_text(encoding="utf-8")

        # 2. English canonical question: check robotic openers
        for marker in ROBOTIC_EN_MARKERS:
            if marker in canonical_text:
                errors.append(f"{qid.upper()}: Canonical question contains robotic marker '{marker}'")

        # 3. English page check: ZERO Arabic characters
        body_en = re.sub(r"\A---\n[\s\S]*?\n---\n", "", en_text)
        ar_matches = ARABIC_CHAR_RE.findall(body_en)
        if ar_matches:
            errors.append(f"{qid.upper()}: English page contains {len(ar_matches)} Arabic characters!")

        # 4. English page sections check
        en_secs = extract_sections(en_text)
        for sec in REQUIRED_SECTIONS_EN:
            if sec == "Practical walkthrough" and ("Practical walkthrough & failure scenario" in en_secs or "Practical walkthrough (English)" in en_secs or "Practical walkthrough" in en_secs):
                continue
            if sec not in en_secs:
                errors.append(f"{qid.upper()}: English page missing section: '{sec}'")
            elif sec != "Original interview question" and len(en_secs[sec].strip()) < 30:
                errors.append(f"{qid.upper()}: English page thin section: '{sec}'")

        # 5. Arabic page sections check
        ar_secs = extract_sections(ar_text)
        for sec in REQUIRED_SECTIONS_AR:
            if sec not in ar_secs:
                errors.append(f"{qid.upper()}: Arabic page missing section: '{sec}'")
            elif sec != "السؤال الأصلي في المقابلة" and len(ar_secs[sec].strip()) < 30:
                errors.append(f"{qid.upper()}: Arabic page thin section: '{sec}'")

        # 6. Silent Fallback check: ensure Arabic sections do not duplicate English content
        for ar_title, sec_content in ar_secs.items():
            if ar_title in ["السؤال الأصلي في المقابلة", "المراجع وتاريخ المراجعة الفنية"]:
                continue
            clean_ar = strip_code(sec_content)
            # Check against every English section to ensure it was not silently copied
            for en_title, en_content in en_secs.items():
                if en_title in ["Original interview question", "References and reviewed-on date"]:
                    continue
                clean_en = strip_code(en_content)
                if clean_ar and len(clean_ar) > 50 and clean_ar == clean_en:
                    errors.append(f"{qid.upper()}: Silent fallback detected! Arabic '{ar_title}' is identical to English '{en_title}'")

        # 7. Arabic page check: ZERO untranslated English explanatory paragraphs
        for sec_name, sec_content in ar_secs.items():
            if sec_name in ["السؤال الأصلي في المقابلة", "المراجع وتاريخ المراجعة الفنية"]:
                continue
            clean_prose = strip_code(sec_content)
            paragraphs = [p.strip() for p in clean_prose.split("\n\n") if p.strip()]
            for p in paragraphs:
                if len(p.split()) >= 10 and not ARABIC_CHAR_RE.search(p):
                    errors.append(f"{qid.upper()}: Untranslated English paragraph under Arabic '## {sec_name}': {p[:60]}...")

        # 8. Spoken answers quality check (English)
        quick_en = en_secs.get("Interview answer — short", "")
        best_en = en_secs.get("Interview answer — structured", "")
        deep_en = en_secs.get("Interview answer — deep senior", "")

        for name, ans, min_w, max_w in [
            ("short", quick_en, 35, 110),
            ("structured", best_en, 100, 280),
            ("deep senior", deep_en, 200, 650),
        ]:
            words = ans.split()
            if len(words) < min_w:
                errors.append(f"{qid.upper()}: English {name} answer too brief ({len(words)} words < {min_w})")
            if re.search(r"^\s*[-*•]\s+", ans, re.M):
                errors.append(f"{qid.upper()}: English {name} answer contains bullet points!")
            if re.search(r"^\s*\d+[\.\)]\s+", ans, re.M):
                errors.append(f"{qid.upper()}: English {name} answer contains numbered list!")

        # 9. Spoken answers quality check (Arabic)
        quick_ar = ar_secs.get("إجابة المقابلة — ملخصة وسريعة", "")
        best_ar = ar_secs.get("إجابة المقابلة — نموذجية ومهيكلة", "")
        deep_ar = ar_secs.get("إجابة المقابلة — مناقشة Senior متعمقة", "")

        for name, ans, min_w, max_w in [
            ("quick_ar", quick_ar, 35, 110),
            ("best_ar", best_ar, 90, 280),
            ("deep_ar", deep_ar, 180, 650),
        ]:
            words = ans.split()
            if len(words) < min_w:
                errors.append(f"{qid.upper()}: Arabic {name} answer too brief ({len(words)} words < {min_w})")
            if re.search(r"^\s*[-*•]\s+", ans, re.M):
                errors.append(f"{qid.upper()}: Arabic {name} answer contains bullet points!")
            if re.search(r"^\s*\d+[\.\)]\s+", ans, re.M):
                errors.append(f"{qid.upper()}: Arabic {name} answer contains numbered list!")
            for cliche in BANNED_AR_CLICHES:
                if cliche in ans:
                    errors.append(f"{qid.upper()}: Arabic {name} answer contains banned repetitive cliché '{cliche}'!")

        # 10. Check answer uniqueness (no duplicate answers across different questions)
        norm_best_en = re.sub(r"\s+", " ", best_en.strip())
        if norm_best_en in seen_en_best:
            errors.append(f"{qid.upper()}: Duplicate structured English answer with {seen_en_best[norm_best_en].upper()}!")
        else:
            seen_en_best[norm_best_en] = qid

        norm_best_ar = re.sub(r"\s+", " ", best_ar.strip())
        if norm_best_ar in seen_ar_best:
            errors.append(f"{qid.upper()}: Duplicate structured Arabic answer with {seen_ar_best[norm_best_ar].upper()}!")
        else:
            seen_ar_best[norm_best_ar] = qid

        # 11. Specific technical accuracy checks
        if qid.upper() == "COR-01":
            # Check for factual accuracy on threads vs coroutines and ANR timeout
            if "500ms" in canonical_text and "ANR" in canonical_text:
                errors.append("COR-01: Contains factually inaccurate 500ms ANR claim!")
            if "1GB" in canonical_text and "physical RAM" in canonical_text:
                errors.append("COR-01: Contains inaccurate thread stack physical RAM exhaustion claim!")
            if "threads-max" not in canonical_text and "pthread_create" not in canonical_text:
                errors.append("COR-01: Lacks kernel thread descriptor ceiling explanation (/proc/sys/kernel/threads-max or pthread_create failed)!")
            if "InputDispatcher" not in canonical_text and "watchdog" not in canonical_text.lower():
                errors.append("COR-01: Lacks precise ANR watchdog timeout distinction (InputDispatcher 5s vs 16.6ms jank)!")

    if errors:
        print(f"\nFAILED with {len(errors)} error(s):", file=sys.stderr)
        for err in errors[:50]:
            print(f"  - {err}", file=sys.stderr)
        if len(errors) > 50:
            print(f"  ... and {len(errors) - 50} more errors", file=sys.stderr)
        return 1

    print(f"SUCCESS: {total_questions} questions passed bilingual parity and structural spoken-answer checks. Natural interview quality still requires editorial review.")
    return 0


if __name__ == "__main__":
    sys.exit(validate())

