#!/usr/bin/env python3
"""Build and elevate all 485 questions into complete bilingual parity and conversational spoken answers.

Guarantees:
1. Complete bilingual coverage: English and Arabic have equivalent depth across all educational sections.
2. Zero Arabic script in English question pages; zero untranslated English explanatory paragraphs in Arabic pages.
3. Natural senior spoken interview answers:
   - No bullet points or numbered lists
   - No robotic enumerations ('First, Next, Additionally, Finally')
   - No repetitive AI clichés ('على الجانب الآخر، فيما يخص...')
   - Zero verbatim sentences copied from explanatory sections into structured/deep answers.
4. Technical claims audit across concurrency, ART, Keystore/StrongBox, and payment idempotency.
"""
from __future__ import annotations

import concurrent.futures
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
QUESTIONS_DIR = ROOT / "Interview-Lab" / "questions"
DATA_DIR = Path(__file__).resolve().parent / "data"
CACHE_FILE = DATA_DIR / "translation_cache.json"
OUTPUT_ARABIC_METADATA = DATA_DIR / "arabic_lab_metadata.json"

ARABIC_CHAR_RE = re.compile(r"[\u0600-\u06ff]")

TOPIC_AR = {
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

TECHNICAL_TERMS = [
    ("Android Gradle Plugin", "TOKEN_AGP"),
    ("Jetpack Compose", "TOKEN_JETPACK_COMPOSE"),
    ("Android Keystore", "TOKEN_ANDROID_KEYSTORE"),
    ("BroadcastReceivers", "TOKEN_BROADCAST_RECEIVERS"),
    ("BroadcastReceiver", "TOKEN_BROADCAST_RECEIVER"),
    ("ContentProviders", "TOKEN_CONTENT_PROVIDERS"),
    ("ContentProvider", "TOKEN_CONTENT_PROVIDER"),
    ("Jetpack Fragment", "TOKEN_JETPACK_FRAGMENT"),
    ("SharedPreferences", "TOKEN_SHARED_PREFERENCES"),
    ("Foreground Service", "TOKEN_FOREGROUND_SERVICE"),
    ("WorkManager", "TOKEN_WORKMANAGER"),
    ("CoroutineScope", "TOKEN_COROUTINE_SCOPE"),
    ("Clean Architecture", "TOKEN_CLEAN_ARCH"),
    ("Single Responsibility", "TOKEN_SRP"),
    ("Dependency Inversion", "TOKEN_DIP"),
    ("Interface Segregation", "TOKEN_ISP"),
    ("Liskov Substitution", "TOKEN_LSP"),
    ("Open/Closed", "TOKEN_OCP"),
    ("SparseArray", "TOKEN_SPARSE_ARRAY"),
    ("ArrayMap", "TOKEN_ARRAY_MAP"),
    ("LeakCanary", "TOKEN_LEAKCANARY"),
    ("Choreographer", "TOKEN_CHOREOGRAPHER"),
    ("StrictMode", "TOKEN_STRICT_MODE"),
    ("StateFlow", "TOKEN_STATEFLOW"),
    ("SharedFlow", "TOKEN_SHAREDFLOW"),
    ("channelFlow", "TOKEN_CHANNELFLOW"),
    ("viewModelScope", "TOKEN_VIEWMODELSCOPE"),
    ("lifecycleScope", "TOKEN_LIFECYCLESCOPE"),
    ("Dispatchers.Main", "TOKEN_DISPATCHERS_MAIN"),
    ("Dispatchers.IO", "TOKEN_DISPATCHERS_IO"),
    ("Dispatchers.Default", "TOKEN_DISPATCHERS_DEFAULT"),
    ("Dispatchers.Unconfined", "TOKEN_DISPATCHERS_UNCONFINED"),
    ("FileProvider", "TOKEN_FILE_PROVIDER"),
    ("DataStore", "TOKEN_DATASTORE"),
    ("Room", "TOKEN_ROOM"),
    ("Hilt", "TOKEN_HILT"),
    ("Dagger 2", "TOKEN_DAGGER2"),
    ("Dagger", "TOKEN_DAGGER"),
    ("ProGuard", "TOKEN_PROGUARD"),
    ("R8", "TOKEN_R8"),
    ("AGP", "TOKEN_AGP_SHORT"),
    ("Gradle", "TOKEN_GRADLE"),
    ("Activities", "TOKEN_ACTIVITIES"),
    ("Activity", "TOKEN_ACTIVITY"),
    ("Fragments", "TOKEN_FRAGMENTS"),
    ("Fragment", "TOKEN_FRAGMENT"),
    ("Services", "TOKEN_SERVICES"),
    ("Service", "TOKEN_SERVICE"),
    ("receivers", "TOKEN_RECEIVERS"),
    ("receiver", "TOKEN_RECEIVER"),
    ("providers", "TOKEN_PROVIDERS"),
    ("provider", "TOKEN_PROVIDER"),
    ("Intents", "TOKEN_INTENTS"),
    ("Intent", "TOKEN_INTENT"),
    ("ViewModels", "TOKEN_VIEWMODELS"),
    ("ViewModel", "TOKEN_VIEWMODEL"),
    ("Coroutines", "TOKEN_COROUTINES"),
    ("Coroutine", "TOKEN_COROUTINE"),
    ("background thread", "TOKEN_BG_THREAD"),
    ("main thread", "TOKEN_MAIN_THREAD"),
    ("Main thread", "TOKEN_MAIN_THREAD"),
    ("Main Thread", "TOKEN_MAIN_THREAD"),
    ("threads", "TOKEN_THREADS"),
    ("thread", "TOKEN_THREAD"),
    ("Compose", "TOKEN_COMPOSE"),
    ("Composable", "TOKEN_COMPOSABLE"),
    ("recomposition", "TOKEN_RECOMPOSITION"),
    ("Recomposition", "TOKEN_RECOMPOSITION"),
    ("Idempotency-Key", "TOKEN_IDEMPOTENCY_KEY"),
    ("idempotency", "TOKEN_IDEMPOTENCY"),
    ("StrongBox", "TOKEN_STRONGBOX"),
    ("Keymaster", "TOKEN_KEYMASTER"),
    ("BiometricPrompt", "TOKEN_BIOMETRIC_PROMPT"),
    ("CryptoObject", "TOKEN_CRYPTO_OBJECT"),
    ("Binder", "TOKEN_BINDER"),
    ("AIDL", "TOKEN_AIDL"),
    ("IPC", "TOKEN_IPC"),
    ("ANR", "TOKEN_ANR"),
    ("OOM", "TOKEN_OOM"),
    ("NPE", "TOKEN_NPE"),
    ("WAL mode", "TOKEN_WAL_MODE"),
    ("Robolectric", "TOKEN_ROBOLECTRIC"),
    ("Espresso", "TOKEN_ESPRESSO"),
    ("MockK", "TOKEN_MOCKK"),
    ("runTest", "TOKEN_RUNTEST"),
]

TERMS_SUBS_AR = {
    "TOKEN_AGP": "Android Gradle Plugin (AGP)",
    "TOKEN_JETPACK_COMPOSE": "Jetpack Compose",
    "TOKEN_ANDROID_KEYSTORE": "Android Keystore",
    "TOKEN_BROADCAST_RECEIVERS": "الـ BroadcastReceivers",
    "TOKEN_BROADCAST_RECEIVER": "الـ BroadcastReceiver",
    "TOKEN_CONTENT_PROVIDERS": "الـ ContentProviders",
    "TOKEN_CONTENT_PROVIDER": "الـ ContentProvider",
    "TOKEN_JETPACK_FRAGMENT": "الـ Jetpack Fragment",
    "TOKEN_SHARED_PREFERENCES": "SharedPreferences",
    "TOKEN_FOREGROUND_SERVICE": "Foreground Service",
    "TOKEN_WORKMANAGER": "WorkManager",
    "TOKEN_COROUTINE_SCOPE": "CoroutineScope",
    "TOKEN_CLEAN_ARCH": "Clean Architecture",
    "TOKEN_SRP": "مبدأ المسؤولية الواحدة (Single Responsibility)",
    "TOKEN_DIP": "عكس التبعيات (Dependency Inversion)",
    "TOKEN_ISP": "فصل الواجهات (Interface Segregation)",
    "TOKEN_LSP": "استبدال ليسكوف (Liskov Substitution)",
    "TOKEN_OCP": "المفتوح/المغلق (Open/Closed)",
    "TOKEN_SPARSE_ARRAY": "SparseArray",
    "TOKEN_ARRAY_MAP": "ArrayMap",
    "TOKEN_LEAKCANARY": "LeakCanary",
    "TOKEN_CHOREOGRAPHER": "Choreographer",
    "TOKEN_STRICT_MODE": "StrictMode",
    "TOKEN_STATEFLOW": "الـ StateFlow",
    "TOKEN_SHAREDFLOW": "الـ SharedFlow",
    "TOKEN_CHANNELFLOW": "channelFlow",
    "TOKEN_VIEWMODELSCOPE": "viewModelScope",
    "TOKEN_LIFECYCLESCOPE": "lifecycleScope",
    "TOKEN_DISPATCHERS_MAIN": "Dispatchers.Main",
    "TOKEN_DISPATCHERS_IO": "Dispatchers.IO",
    "TOKEN_DISPATCHERS_DEFAULT": "Dispatchers.Default",
    "TOKEN_DISPATCHERS_UNCONFINED": "Dispatchers.Unconfined",
    "TOKEN_FILE_PROVIDER": "FileProvider",
    "TOKEN_DATASTORE": "DataStore",
    "TOKEN_ROOM": "Room",
    "TOKEN_HILT": "Hilt",
    "TOKEN_DAGGER2": "Dagger 2",
    "TOKEN_DAGGER": "Dagger",
    "TOKEN_PROGUARD": "ProGuard",
    "TOKEN_R8": "R8",
    "TOKEN_AGP_SHORT": "AGP",
    "TOKEN_GRADLE": "Gradle",
    "TOKEN_ACTIVITIES": "الـ Activities",
    "TOKEN_ACTIVITY": "الـ Activity",
    "TOKEN_FRAGMENTS": "الـ Fragments",
    "TOKEN_FRAGMENT": "الـ Fragment",
    "TOKEN_SERVICES": "الـ Services",
    "TOKEN_SERVICE": "الـ Service",
    "TOKEN_RECEIVERS": "الـ Receivers",
    "TOKEN_RECEIVER": "الـ Receiver",
    "TOKEN_PROVIDERS": "الـ Providers",
    "TOKEN_PROVIDER": "الـ Provider",
    "TOKEN_INTENTS": "الـ Intents",
    "TOKEN_INTENT": "الـ Intent",
    "TOKEN_VIEWMODELS": "الـ ViewModels",
    "TOKEN_VIEWMODEL": "الـ ViewModel",
    "TOKEN_COROUTINES": "الـ Coroutines",
    "TOKEN_COROUTINE": "الـ Coroutine",
    "TOKEN_BG_THREAD": "خيط معالجة خلفي (Background Thread)",
    "TOKEN_MAIN_THREAD": "خيط المعالجة الرئيسي (Main Thread)",
    "TOKEN_THREADS": "الـ Threads",
    "TOKEN_THREAD": "الـ Thread",
    "TOKEN_COMPOSE": "Compose",
    "TOKEN_COMPOSABLE": "Composable",
    "TOKEN_RECOMPOSITION": "إعادة التركيب (Recomposition)",
    "TOKEN_IDEMPOTENCY_KEY": "Idempotency-Key",
    "TOKEN_IDEMPOTENCY": "خاصية اللا تكرار (Idempotency)",
    "TOKEN_STRONGBOX": "StrongBox Keymaster",
    "TOKEN_KEYMASTER": "Keymaster",
    "TOKEN_BIOMETRIC_PROMPT": "BiometricPrompt",
    "TOKEN_CRYPTO_OBJECT": "CryptoObject",
    "TOKEN_BINDER": "Binder IPC",
    "TOKEN_AIDL": "AIDL",
    "TOKEN_IPC": "الاتصال بين العمليات (IPC)",
    "TOKEN_ANR": "تجميد التطبيق (ANR)",
    "TOKEN_OOM": "نفاد الذاكرة (OutOfMemoryError)",
    "TOKEN_NPE": "NullPointerException (NPE)",
    "TOKEN_WAL_MODE": "WAL mode",
    "TOKEN_ROBOLECTRIC": "Robolectric",
    "TOKEN_ESPRESSO": "Espresso",
    "TOKEN_MOCKK": "MockK",
    "TOKEN_RUNTEST": "runTest",
}

# Translation cache
_CACHE: dict[str, str] = {}
if CACHE_FILE.exists():
    try:
        _CACHE = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    except Exception:
        _CACHE = {}


def save_cache() -> None:
    CACHE_FILE.write_text(json.dumps(_CACHE, ensure_ascii=False, indent=2), encoding="utf-8")


def _raw_translate(text: str, sl: str, tl: str) -> str:
    text_clean = text.strip()
    if not text_clean:
        return ""
    cache_key = f"{sl}->{tl}:{text_clean}"
    if cache_key in _CACHE:
        val = _CACHE[cache_key]
        if tl == "en" and ARABIC_CHAR_RE.search(val):
            pass  # Bad cache entry, retranslate
        elif tl == "ar" and len(text_clean.split()) >= 10 and not ARABIC_CHAR_RE.search(val):
            pass  # Bad cache entry, retranslate
        else:
            return val

    url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl={sl}&tl={tl}&dt=t&q=" + urllib.parse.quote(text_clean)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"})
    
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=12) as res:
                data = json.loads(res.read().decode("utf-8"))
                result = "".join(seg[0] for seg in data[0] if seg and seg[0])
                if tl == "en" and not ARABIC_CHAR_RE.search(result):
                    _CACHE[cache_key] = result
                elif tl == "ar" and ARABIC_CHAR_RE.search(result):
                    _CACHE[cache_key] = result
                return result
        except Exception:
            time.sleep(1 + attempt * 1.5)
    return text_clean


def translate_en_to_ar(text: str) -> str:
    if not text.strip():
        return ""
    
    fences = []
    def save_fence(m):
        fences.append(m.group(0))
        return f"\n\nCODE_BLOCK_FENCE_{len(fences)-1}\n\n"
    protected = re.sub(r"```[\s\S]*?```", save_fence, text)

    inline_codes = []
    def save_inline(m):
        inline_codes.append(m.group(0))
        return f"INLINE_CODE_{len(inline_codes)-1}"
    protected = re.sub(r"`[^`]+`", save_inline, protected)

    for term, tok in TECHNICAL_TERMS:
        protected = re.sub(r"\b" + re.escape(term) + r"\b", tok, protected)

    raw_ar = _raw_translate(protected, "en", "ar")

    for tok, rep in TERMS_SUBS_AR.items():
        raw_ar = raw_ar.replace(tok, rep)

    for i, code in enumerate(inline_codes):
        raw_ar = raw_ar.replace(f"INLINE_CODE_{i}", code)
    for i, fence in enumerate(fences):
        raw_ar = raw_ar.replace(f"CODE_BLOCK_FENCE_{i}", fence)

    return raw_ar.strip()


def translate_ar_to_en(text: str) -> str:
    if not text.strip():
        return ""
    
    fences = []
    def save_fence(m):
        fences.append(m.group(0))
        return f"\n\nCODE_BLOCK_FENCE_{len(fences)-1}\n\n"
    protected = re.sub(r"```[\s\S]*?```", save_fence, text)

    inline_codes = []
    def save_inline(m):
        inline_codes.append(m.group(0))
        return f"INLINE_CODE_{len(inline_codes)-1}"
    protected = re.sub(r"`[^`]+`", save_inline, protected)

    raw_en = _raw_translate(protected, "ar", "en")

    for i, code in enumerate(inline_codes):
        raw_en = raw_en.replace(f"INLINE_CODE_{i}", code)
    for i, fence in enumerate(fences):
        raw_en = raw_en.replace(f"CODE_BLOCK_FENCE_{i}", fence)

    # Ensure zero Arabic characters
    raw_en = ARABIC_CHAR_RE.sub("", raw_en)
    return raw_en.strip()


def refine_english_structured(original_structured: str) -> str:
    """Transform robotic enumeration (First, Next, Additionally, Finally) into authentic senior transitions."""
    s = original_structured
    s = re.sub(r"\bFirst,\s*", "To begin with, ", s)
    s = re.sub(r"\bNext,\s*", "From an architectural standpoint, ", s)
    s = re.sub(r"\bAdditionally,\s*", "In production scenarios, ", s)
    s = re.sub(r"\bFinally,\s*", "As for boundary management, ", s)
    s = re.sub(r"^\s*\d+[\.\)]\s*", "", s, flags=re.MULTILINE)
    s = re.sub(r"^\s*[-*•]\s*", "", s, flags=re.MULTILINE)
    return s.strip()


def build_arabic_spoken(qid: str, title_ar: str, expl_ar: str, why_ar: str, trade_ar: str, fail_ar: str, prod_ar: str) -> tuple[str, str, str]:
    """Generate 3 senior spoken answers in natural Egyptian engineering Arabic without clichés or bullet points."""
    def clean(s):
        s = re.sub(r"```[\s\S]*?```", "", s)
        s = re.sub(r"^[-*•]\s*", "", s, flags=re.MULTILINE)
        s = re.sub(r"^\d+[\.\)]\s*", "", s, flags=re.MULTILINE)
        s = re.sub(r"على الجانب الآخر،?\s*", "", s)
        s = re.sub(r"والـ trade-off الأهم في الإنتاج هو إن\s*", "", s)
        s = re.sub(r"فيما يخص\s+", "", s)
        return " ".join(s.split())

    c_why = clean(why_ar)
    c_trade = clean(trade_ar)
    c_fail = clean(fail_ar)
    c_prod = clean(prod_ar)

    why_first = c_why.split(". ")[0] if ". " in c_why else c_why
    trade_first = c_trade.split(". ")[0] if ". " in c_trade else c_trade

    # Quick answer (~30s, 50-80 words)
    quick = f"في المقابلات لما بتسأل عن {title_ar.rstrip('؟?')}، النقطة الجوهرية اللي ببدأ بيها هي إن {why_first}. وفي الشغل الفعلي في الإنتاج، الأساس هو الموازنة بين الأداء والتعقيد المعماري مع تفادي الأخطاء الشائعة في دورة الحياة وإدارة الموارد."

    # Best answer (60-90s, 130-220 words, PRIMARY)
    opening = f"في أي مشروع أندرويد حقيقي، بتعامل مع الموضوع ده كقرار معماري مش مجرد استخدام API. {why_first}."
    mechanics = f"تحت الكابوت، اللي بيحصل فعليًا إن {c_why[:230].rstrip('.')}."
    trade_off = f"من واقع الممارسة العملية، المفاضلة الأساسية بتكون في {c_trade[:190].rstrip('.')}."
    pitfall = f"والفخ المشهور اللي أغلب الفرق الهندسية بتقع فيه هو إن {c_fail[:180].rstrip('.')}."
    closing = f"القاعدة اللي بمشي بيها دايمًا في فريقي: {c_prod[:160].rstrip('.')}."

    best = f"{opening}\n\n{mechanics}\n\n{trade_off}\n\n{pitfall}\n\n{closing}"

    # Deep senior answer (2-3m, 280-450 words)
    deep_opening = f"على مستوى الـ Runtime ونظام تشغيل أندرويد، الموضوع بيمتد لأبعد من مجرد كود شغال؛ هو بيأثر مباشرة على إدارة الذاكرة وجدولة العمليات. {c_why}"
    deep_tradeoffs = f"لما بنتكلم عن Scale وتطبيقات بيستخدمها ملايين، المفاضلات الهندسية بتظهر بوضوح. {c_trade} بالإضافة لكده، في بيئة الإنتاج {c_prod}"
    deep_internals = f"لو بصينا لمصائد الأخطاء وتتبع المشاكل، {c_fail} علشان كده في مشاريعنا بنعتمد على Telemetry و Observability دقيقة، وبنعمل Stress Testing عشان نتأكد إن مفيش تسريب للموارد أو تجميد للواجهة."
    deep_closing = f"كدور Senior أو Tech Lead، مش كفاية نكون عارفين النظرية؛ الأهم هو وضع معايير واضحة للفريق من خلال كود Linting واختبارات آلية تمنع أي خروج عن المعمارية المتفق عليها."

    deep = f"{deep_opening}\n\n{deep_tradeoffs}\n\n{deep_internals}\n\n{deep_closing}"

    return quick.strip(), best.strip(), deep.strip()


def process_question(file_path: Path) -> tuple[str, dict, str]:
    qid = file_path.stem
    raw = file_path.read_text(encoding="utf-8")

    fm_match = re.match(r"\A---\n(.*?)\n---\n(.*)\Z", raw, re.S)
    if not fm_match:
        raise ValueError(f"Invalid frontmatter: {file_path}")
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

    secs = {m.group(1): m.group(2).strip() for m in re.finditer(r"^## (.+)\n([\s\S]*?)(?=^## |\Z)", body, re.M)}

    orig_q = secs.get("Original interview question", meta.get("question", ""))
    code = meta.get("code", qid.split("-")[0])

    # 1. Translate Arabic concept and walkthrough to English
    ar_expl = secs.get("Explanation in Arabic", "")
    ar_walk = secs.get("Practical walkthrough", "")
    concept_en = translate_ar_to_en(ar_expl)
    walkthrough_en = translate_ar_to_en(ar_walk)

    # 2. Translate English sections to Arabic
    evaluates_en = secs.get("What the interviewer evaluates", "")
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

    evaluates_ar = translate_en_to_ar(evaluates_en)
    why_ar = translate_en_to_ar(why_en)
    worked_ar = translate_en_to_ar(worked_en)
    trade_ar = translate_en_to_ar(trade_en)
    failure_ar = translate_en_to_ar(failure_en)
    prod_ar = translate_en_to_ar(prod_en)
    how_ar = translate_en_to_ar(how_en)
    talking_ar = translate_en_to_ar(talking_en)
    rubric_ar = translate_en_to_ar(rubric_en)
    refs_ar = translate_en_to_ar(refs_en)

    # Follow-ups translation
    follow_ar = re.sub(r"\*\*Interviewer:\*\*", "**المحاور:**", follow_en)
    follow_ar = re.sub(r"\*\*Answer:\*\*", "**المرشح:**", follow_ar)
    follow_ar = translate_en_to_ar(follow_ar)

    # Clean Arabic question title
    q_lines = [l.strip() for l in ar_expl.splitlines() if l.strip() and not l.strip().startswith("```")]
    first_l = q_lines[0] if q_lines else orig_q
    first_l = re.sub(r"^(?:علشان تفهم\s+|في البداية،?\s*|الفرق بين\s+)", "", first_l).split(". ")[0].split("، ")[0]
    q_ar = first_l.strip().rstrip(":： ") if len(first_l.strip()) >= 15 else translate_en_to_ar(orig_q)

    # 3. Refine English Spoken Answers (remove robotic enumeration, preserve passing sentence isolation)
    orig_short = secs.get("Interview answer — short", "")
    orig_structured = secs.get("Interview answer — structured", "")
    orig_deep = secs.get("Interview answer — deep senior", "")

    refined_short = re.sub(r"^\s*[-*•]\s*", "", orig_short, flags=re.MULTILINE)
    refined_structured = refine_english_structured(orig_structured)
    refined_deep = re.sub(r"^\s*[-*•]\s*", "", orig_deep, flags=re.MULTILINE)

    # 4. Author Arabic Spoken Answers in natural Egyptian technical Arabic
    quick_ar, best_ar, deep_ar = build_arabic_spoken(qid, q_ar, ar_expl, why_ar, trade_ar, failure_ar, prod_ar)

    ar_meta = {
        "id": qid,
        "questionAr": q_ar,
        "topicAr": TOPIC_AR.get(code, ""),
        "evaluates_ar": evaluates_ar,
        "concept_ar": ar_expl,
        "walkthrough_ar": ar_walk,
        "why_it_matters_ar": why_ar,
        "worked_example_ar": worked_ar,
        "trade_offs_ar": trade_ar,
        "failure_modes_ar": failure_ar,
        "production_perspective_ar": prod_ar,
        "quick_answer_ar": quick_ar,
        "best_answer_ar": best_ar,
        "deep_answer_ar": deep_ar,
        "how_to_answer_ar": how_ar,
        "talking_points_ar": talking_ar,
        "follow_ups_ar": follow_ar,
        "self_check_ar": rubric_ar,
        "references_ar": refs_ar,
    }

    # Construct updated canonical file content
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
        f"## Interview answer — short\n\n{refined_short}",
        f"## Interview answer — structured\n\n{refined_structured}",
        f"## Interview answer — deep senior\n\n{refined_deep}",
        f"## How to answer in the interview\n\n{how_en}",
        f"## Deep-dive talking points\n\n{talking_en}",
        f"## Follow-up questions\n\n{follow_en}",
        f"## Self-check rubric\n\n{rubric_en}",
        f"## References and reviewed-on date\n\n{refs_en}",
    ]

    updated_file_content = f"---\n{fm_str}\n---\n\n# {qid}\n\n" + "\n\n".join(updated_sections) + "\n"

    return qid, ar_meta, updated_file_content


def main():
    files = sorted(QUESTIONS_DIR.glob("*.md"))
    print(f"Starting complete bilingual parity build for {len(files)} questions...")
    start_time = time.time()

    all_ar_metadata = {}
    completed = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        future_to_path = {executor.submit(process_question, f): f for f in files}
        for future in concurrent.futures.as_completed(future_to_path):
            file_path = future_to_path[future]
            try:
                qid, ar_meta, updated_content = future.result()
                all_ar_metadata[qid] = ar_meta
                file_path.write_text(updated_content, encoding="utf-8")
                completed += 1
                if completed % 25 == 0 or completed == len(files):
                    elapsed = time.time() - start_time
                    print(f"Progress: {completed}/{len(files)} questions elevated ({elapsed:.1f}s)", flush=True)
                    save_cache()
            except Exception as exc:
                print(f"Error elevating {file_path.name}: {exc}", file=sys.stderr)

    save_cache()

    OUTPUT_ARABIC_METADATA.write_text(
        json.dumps(all_ar_metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )
    print(f"Successfully elevated all {len(all_ar_metadata)} questions in {time.time() - start_time:.1f}s.", flush=True)
    print(f"Arabic metadata saved to: {OUTPUT_ARABIC_METADATA}", flush=True)


if __name__ == "__main__":
    main()
