#!/usr/bin/env python3
"""Elevation engine utility module for bilingual parity and conversational spoken answers."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
QUESTIONS_DIR = ROOT / "Interview-Lab" / "questions"
DATA_DIR = Path(__file__).resolve().parent / "data"
DOCS_EN = ROOT / "site" / "src" / "content" / "docs" / "lab" / "questions"
DOCS_AR = ROOT / "site" / "src" / "content" / "docs" / "ar" / "lab" / "questions"

ARABIC_CHAR_RE = re.compile(r"[؀-ۿ]")

TOPIC_AR_NAMES = {
    "KOT": "أساسيات لغة Kotlin ومفاهيمها المتقدمة",
    "AND": "أساسيات أندرويد ودورة الحياة والسياق (Context)",
    "MEM": "إدارة الذاكرة والـ ANR وتحسين الأداء",
    "COR": "الـ Coroutines والتزامن في Kotlin",
    "FLO": "الـ Flow و StateFlow و SharedFlow والـ Channels",
    "ARC": "العمارة النظيفة و MVVM و MVI و UDF",
    "SOL": "مبادئ SOLID والتصميم الكائني",
    "PAT": "أنماط التصميم البرمجية (Design Patterns)",
    "DI": "حقن التبعيات: Hilt و Dagger",
    "COM": "واجهات Jetpack Compose الحديثة",
    "DAT": "الشبكات وقواعد بيانات Room والـ DataStore والتخزين المحلي",
    "BG": "المهام الخلفية و WorkManager وقيود النظام",
    "SEC": "أمان أندرويد والتشفير والنمذجة الأمنية لتطبيقات التكنولوجيا المالية",
    "SYS": "تصميم أنظمة وتطبيقات الموبايل (System Design) والقرارات الهندسية",
    "MOD": "تقسيم المشروع لموديولات (Modularization) وحدود التبعيات",
    "BLD": "أنظمة البناء و Gradle و AGP و R8 والـ Signing وإصدار التطبيقات",
    "TST": "اختبار البرمجيات والجودة والموثوقية",
    "CIC": "الـ CI/CD والـ Git وتسليم المشاريع في الفرق الهندسية",
    "DSA": "هياكل البيانات والخوارزميات والـ Big O",
    "LEAD": "القيادة التقنية والتواصل وملكية المشاريع الهندسية",
    "PAY": "سيناريوهات الدفع ونقاط البيع (POS) وتأمين المعاملات المالية",
}


def parse_canonical_question(qid: str) -> tuple[dict, dict[str, str], str]:
    path = QUESTIONS_DIR / f"{qid.upper()}.md"
    if not path.exists():
        raise FileNotFoundError(f"Canonical file not found: {path}")
    raw = path.read_text(encoding="utf-8")
    fm_match = re.match(r"\A---\n(.*?)\n---\n(.*)\Z", raw, re.S)
    if not fm_match:
        raise ValueError(f"Invalid frontmatter in {path}")
    fm_str = fm_match.group(1)
    body = fm_match.group(2)

    meta = {}
    for line in fm_str.splitlines():
        k, sep, v = line.partition(": ")
        if sep:
            try:
                meta[k] = json.loads(v)
            except Exception:
                meta[k] = v.strip('"')

    secs = {
        m.group(1).strip(): m.group(2).strip()
        for m in re.finditer(r"^## (.+)\n([\s\S]*?)(?=^## |\Z)", body, re.M)
    }
    return meta, secs, fm_str


def update_canonical_question(
    qid: str,
    concept_en: str,
    walkthrough_en: str,
    structured_en: str,
    deep_senior_en: str,
    short_en: str | None = None,
) -> None:
    path = QUESTIONS_DIR / f"{qid.upper()}.md"
    meta, secs, fm_str = parse_canonical_question(qid)

    # Clean concept_en and walkthrough_en to guarantee ZERO Arabic chars
    concept_en = ARABIC_CHAR_RE.sub("", concept_en).strip()
    walkthrough_en = ARABIC_CHAR_RE.sub("", walkthrough_en).strip()

    # Clean English spoken answers: NO bullet points, NO numbered lists
    structured_en = re.sub(r"^\s*[-*•]\s*", "", structured_en, flags=re.MULTILINE)
    structured_en = re.sub(r"^\s*\d+[\.\)]\s*", "", structured_en, flags=re.MULTILINE).strip()
    deep_senior_en = re.sub(r"^\s*[-*•]\s*", "", deep_senior_en, flags=re.MULTILINE)
    deep_senior_en = re.sub(r"^\s*\d+[\.\)]\s*", "", deep_senior_en, flags=re.MULTILINE).strip()
    if short_en:
        short_en = re.sub(r"^\s*[-*•]\s*", "", short_en, flags=re.MULTILINE)
        short_en = re.sub(r"^\s*\d+[\.\)]\s*", "", short_en, flags=re.MULTILINE).strip()
    else:
        short_en = re.sub(r"^\s*[-*•]\s*", "", secs.get("Interview answer — short", ""), flags=re.MULTILINE).strip()

    orig_q = secs.get("Original interview question", meta.get("question", ""))
    evaluates_en = secs.get("What the interviewer evaluates", "")
    ar_expl = secs.get("Explanation in Arabic", "")
    ar_walk = secs.get("Practical walkthrough", "")
    why_en = secs.get("Why it matters and how it works", "")
    worked_en = secs.get("Worked example", "")
    trade_en = secs.get("Trade-offs and decision criteria", "")
    failure_en = secs.get("Failure modes", "")
    prod_en = secs.get("Production perspective", "")
    how_en = secs.get("How to answer in the interview", "")
    talking_en = secs.get("Deep-dive talking points", "")
    follow_en = secs.get("Follow-up questions", "")
    rubric_en = secs.get("Self-check rubric", "")
    refs_en = secs.get("References and reviewed-on date", "")

    updated_sections = [
        f"## Original interview question\n\n{orig_q}",
        f"## What the interviewer evaluates\n\n{evaluates_en}",
        f"## Concept and technical explanation\n\n{concept_en}",
        f"## Practical walkthrough (English)\n\n{walkthrough_en}",
        f"## Explanation in Arabic\n\n{ar_expl}",
        f"## Practical walkthrough\n\n{ar_walk}",
        f"## Why it matters and how it works\n\n{why_en}",
        f"## Worked example\n\n{worked_en}",
        f"## Trade-offs and decision criteria\n\n{trade_en}",
        f"## Failure modes\n\n{failure_en}",
        f"## Production perspective\n\n{prod_en}",
        f"## Interview answer — short\n\n{short_en}",
        f"## Interview answer — structured\n\n{structured_en}",
        f"## Interview answer — deep senior\n\n{deep_senior_en}",
        f"## How to answer in the interview\n\n{how_en}",
        f"## Deep-dive talking points\n\n{talking_en}",
        f"## Follow-up questions\n\n{follow_en}",
        f"## Self-check rubric\n\n{rubric_en}",
        f"## References and reviewed-on date\n\n{refs_en}",
    ]

    new_content = f"---\n{fm_str}\n---\n\n# {qid.upper()}\n\n" + "\n\n".join(updated_sections) + "\n"
    path.write_text(new_content, encoding="utf-8")


def save_topic_metadata(topic_code: str, items: dict[str, dict]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    out_file = DATA_DIR / f"metadata_{topic_code.lower()}.json"
    out_file.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def merge_all_metadata() -> None:
    main_meta_path = DATA_DIR / "arabic_lab_metadata.json"
    main_meta = {}
    if main_meta_path.exists():
        try:
            main_meta = json.loads(main_meta_path.read_text(encoding="utf-8"))
        except Exception:
            main_meta = {}

    for f in sorted(DATA_DIR.glob("metadata_*.json")):
        try:
            part = json.loads(f.read_text(encoding="utf-8"))
            for qid, qdata in part.items():
                main_meta[qid] = qdata
        except Exception as e:
            print(f"Error reading {f}: {e}", file=sys.stderr)

    main_meta_path.write_text(
        json.dumps(main_meta, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Merged metadata for {len(main_meta)} questions into {main_meta_path}")

def validate_question(qid: str) -> list[str]:
    """Validate single question against all bilingual parity and quality rules."""
    meta, secs, _ = parse_canonical_question(qid)
    errors = []

    # 1. English Concept & Walkthrough
    concept = secs.get("Concept and technical explanation", "")
    walkthrough = secs.get("Practical walkthrough (English)", "") or secs.get("Practical walkthrough & failure scenario", "")
    if not concept:
        errors.append(f"{qid}: Missing Concept and technical explanation")
    elif len(concept.strip()) < 30:
        errors.append(f"{qid}: Thin Concept and technical explanation")
    elif ARABIC_CHAR_RE.search(concept):
        errors.append(f"{qid}: Arabic characters in Concept and technical explanation")

    if not walkthrough:
        errors.append(f"{qid}: Missing Practical walkthrough (English)")
    elif len(walkthrough.strip()) < 30:
        errors.append(f"{qid}: Thin Practical walkthrough (English)")
    elif ARABIC_CHAR_RE.search(walkthrough):
        errors.append(f"{qid}: Arabic characters in Practical walkthrough (English)")

    # 2. English Spoken Answers
    short_en = secs.get("Interview answer — short", "")
    structured_en = secs.get("Interview answer — structured", "")
    deep_en = secs.get("Interview answer — deep senior", "")

    for name, ans, min_w, max_w in [
        ("short", short_en, 35, 110),
        ("structured", structured_en, 100, 280),
        ("deep senior", deep_en, 200, 650),
    ]:
        w = len(ans.split())
        if w < min_w or w > max_w:
            errors.append(f"{qid}: English {name} answer word count {w} not in [{min_w}, {max_w}]")
        if re.search(r"^\s*[-*•]\s*", ans, re.M):
            errors.append(f"{qid}: English {name} answer contains bullet points")
        if re.search(r"^\s*\d+[\.\)]\s*", ans, re.M):
            errors.append(f"{qid}: English {name} answer contains numbered list")

    if "First," in structured_en and "Next," in structured_en:
        errors.append(f"{qid}: English structured answer contains formulaic enumeration")

    # Copied sentences check
    def get_sentences(val: str) -> list[str]:
        val = re.sub(r"```[\s\S]*?```", "", val)
        return [p.strip().strip('"“”') for p in re.split(r"(?<=[.!?])\s+", val) if len(p.split()) >= 7]

    explanatory = " ".join(secs.get(n, "") for n in ("Why it matters and how it works", "Worked example", "Trade-offs and decision criteria", "Failure modes", "Production perspective"))
    orig_s = {re.sub(r"\s+", " ", p).casefold() for p in get_sentences(explanatory)}
    for depth, a in [("structured", structured_en), ("deep senior", deep_en)]:
        copied = [p for p in get_sentences(a) if re.sub(r"\s+", " ", p).casefold() in orig_s]
        if copied:
            errors.append(f"{qid}: Copied {len(copied)} long sentences into {depth}: {copied[0][:40]}...")

    # 3. Arabic Metadata
    meta_path = DATA_DIR / "arabic_lab_metadata.json"
    if meta_path.exists():
        all_meta = json.loads(meta_path.read_text(encoding="utf-8"))
        q_ar = all_meta.get(qid.upper())
        if not q_ar:
            errors.append(f"{qid}: Missing from arabic_lab_metadata.json")
        else:
            required_ar = [
                ("evaluates_ar", "ما يقيّمه المحاور", 30),
                ("why_it_matters_ar", "آلية العمل والتحليل الهندسي", 30),
                ("worked_example_ar", "مثال تطبيقي واختبار", 30),
                ("trade_offs_ar", "المفاضلات الهندسية ومعايير القرار", 30),
                ("failure_modes_ar", "أنماط الفشل ومصائد الأخطاء", 30),
                ("production_perspective_ar", "منظور بيئة العمل الفعلي", 30),
                ("how_to_answer_ar", "طريقة تقديم الإجابة في المقابلة", 30),
                ("talking_points_ar", "محاور النقاش المتقدم", 30),
                ("follow_ups_ar", "أسئلة المتابعة واعتراضات المحاور", 30),
                ("self_check_ar", "معايير التقييم الذاتي", 30),
                ("references_ar", "المراجع وتاريخ المراجعة الفنية", 30),
            ]
            for f_key, f_name, min_l in required_ar:
                val = q_ar.get(f_key, "")
                if not val or len(val.strip()) < min_l:
                    errors.append(f"{qid}: Arabic field {f_key} ({f_name}) missing or thin")
                else:
                    # check for untranslated english prose
                    clean = re.sub(r"```[\s\S]*?```", "", val)
                    clean = re.sub(r"`[^`]+`", "", clean)
                    for p in clean.split("\n\n"):
                        p_words = p.strip().split()
                        if len(p_words) >= 10 and not ARABIC_CHAR_RE.search(p):
                            errors.append(f"{qid}: Untranslated English paragraph in {f_key}: {p[:40]}...")

            quick_ar = q_ar.get("quick_answer_ar", "")
            best_ar = q_ar.get("best_answer_ar", "")
            deep_ar = q_ar.get("deep_answer_ar", "")

            for name, ans, min_w, max_w in [
                ("quick_ar", quick_ar, 35, 110),
                ("best_ar", best_ar, 90, 280),
                ("deep_ar", deep_ar, 180, 650),
            ]:
                w = len(ans.split())
                if w < min_w or w > max_w:
                    errors.append(f"{qid}: Arabic {name} answer word count {w} not in [{min_w}, {max_w}]")
                if re.search(r"^\s*[-*•]\s*", ans, re.M):
                    errors.append(f"{qid}: Arabic {name} answer contains bullet points")
                if re.search(r"^\s*\d+[\.\)]\s*", ans, re.M):
                    errors.append(f"{qid}: Arabic {name} answer contains numbered list")
                if "على الجانب الآخر، فيما يخص" in ans:
                    errors.append(f"{qid}: Arabic {name} answer contains banned cliché")

    return errors
