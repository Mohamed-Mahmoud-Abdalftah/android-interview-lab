#!/usr/bin/env python3
"""Elevate KOT-30 for bilingual parity and senior spoken answers."""
from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import elevation_engine as ee

DATA = {
    "KOT-30": {
        "concept_en": """Reviewing a Kotlin API or library interface requires balancing semantic readability, compile-time null safety, and memory allocation overhead. High-quality Kotlin APIs avoid primitive obsession by modeling domain primitives with compile-time inline value classes, enforce strict null contracts using sealed outcome hierarchies rather than ambiguous null returns, and eliminate accidental allocations caused by lambda capturing, excessive boxing, or eager collection transformations. Reviewers must guard against the double-bang operator (force-unwrap), restrict lateinit to dependency injection frameworks, and protect API ingress points from unannotated Java platform types. Readability requires idiomatic Kotlin patterns: exposing read-only interfaces rather than mutable collections, favoring immutability via val, and avoiding deeply nested scope functions that obscure variable ownership.""",
        "walkthrough_en": """Reviewing and refactoring an ambiguous API during pull request review:
```kotlin
// Suboptimal API: ambiguous nullability and unnecessary heap allocations
interface BadUserCatalog {
    fun fetchUsers(query: String?): List<String>? // Null vs empty ambiguity
}

class UserProcessor(private val catalog: BadUserCatalog) {
    fun process(query: String?) {
        val list = catalog.fetchUsers(query) ?: return
        // Eager collection chain creates two intermediate ArrayList instances:
        val activeIds = list.filter { it.isNotEmpty() }.map { it.uppercase() }
        activeIds.forEach { id ->
            // Non-inlined lambda capturing local variable:
            Analytics.track { logUser(id) }
        }
    }
}

// Senior refactoring: explicit domain models, zero-allocation sequence, compile-time safety
sealed interface CatalogResult {
    data class Success(val userIds: List<UserId>) : CatalogResult
    data object Empty : CatalogResult
    data class Error(val cause: Throwable) : CatalogResult
}

@JvmInline
value class UserId(val raw: String) {
    init { require(raw.isNotBlank()) { "User ID cannot be blank" } }
}

interface CleanUserCatalog {
    suspend fun fetchUsers(query: String): CatalogResult
}
```""",
        "short_en": """I review Kotlin APIs across three core architectural pillars: null safety, memory allocation cost, and idiomatic readability. I enforce strict null safety by eliminating force-unwraps and modeling outcomes with sealed interfaces. I audit allocation cost by avoiding unnecessary boxing and replacing intermediate collections with Sequences or direct iteration. Finally, I ensure readability through immutable read-only public contracts and clean domain-driven naming.""",
        "structured_en": """To begin with, evaluating a Kotlin API during code review is an essential engineering responsibility centered on semantic clarity, null contracts, and runtime cost.
From an architectural standpoint, my first priority is strict null safety and explicit outcome typing. I maintain a zero-tolerance policy for force-unwrap operators and inspect API boundaries where Java platform types enter the module to ensure they are immediately confined to explicit nullable or non-null types. Returning an ambiguous nullable collection is replaced with a sealed hierarchy that distinctly separates successful data, empty results, and domain failures.
In production scenarios, allocation cost represents the second critical evaluation pillar. I audit chained collection pipelines like chained map and filter calls that allocate intermediate collections on the heap, recommending Sequences for unbounded datasets. Furthermore, I ensure value classes are not inadvertently boxed into generic interfaces and verify that higher-order functions in performance-sensitive loops are properly inlined.
As for boundary management, readability requires idiomatic Kotlin design. Public interfaces must expose read-only collections rather than mutable instances, properties must favor immutability through val declarations, and convoluted chains of nested scope functions like let, also, and apply must be refactored into direct imperative code.""",
        "deep_senior_en": """At the staff-engineer level, API review transcends surface syntax to address binary compatibility, compiler stability, and memory efficiency under load. We automate mechanical checks using Detekt and Android Lint in CI pipelines to enforce baseline rules such as banning force-unwraps, restricting lateinit, and flagging unused return values, which frees senior reviewers to focus on architectural nuance.
When reviewing APIs consumed by Jetpack Compose, parameter stability is paramount. Data classes exposed to composables must use read-only val properties and replace standard mutable or runtime-indeterminate collections with persistent immutable collections like kotlinx.collections.immutable. This guarantees that the Compose compiler marks composable parameters as stable, unlocking recomposition skipping across high-frequency UI passes.
Regarding allocation overhead, reviewers must inspect decompiled JVM bytecode or ART DEX allocations using the Memory Profiler. Inlining functions with reified type parameters provides zero-cost abstractions, but over-inlining large function bodies bloats bytecode size and exhausts instruction caches. Similarly, while @JvmInline value classes eliminate heap allocation for domain identifiers, assigning them to generic type parameters or nullable wrappers forces the compiler to box them into heap-allocated objects, defeating the optimization.
Finally, for shared platform libraries, public binary compatibility is strictly guarded. We integrate the Jetpack Binary Compatibility Validator plugin to automatically detect breaking ABI shifts, such as altered default parameters or synthetic companion accessors, ensuring seamless multi-module consumer upgrades.""",
        "meta_ar": {
            "id": "KOT-30",
            "questionAr": "كيف تراجع كود Kotlin للتأكد من المقروءية والأمان من الـ Null وكفاءة الذاكرة؟",
            "topicAr": "أساسيات لغة Kotlin ومفاهيمها المتقدمة",
            "evaluates_ar": "- مراجعة عقود الأمان من الـ Null والتخلص من الـ Force-unwrap وإدارة Platform Types.\n- فحص تكلفة الذاكرة وحظر الـ Boxing غير المقصود وسلاسل التحويل الوسيطة في المجموعات.\n- تطبيق أنماط Kotlin القياسية وحماية التوافق الثنائي واستقرار Jetpack Compose.",
            "why_it_matters_ar": "الـ API البرمجي يُقرأ ويُستخدم مئات المرات مقارنة بوقت كتابته الأول. غياب الصرامة في مراجعة الأمان من الـ Null يؤدي إلى كراشات NullPointerException غير متوقعة عند التعامل مع مكتبات Java. والإفراط في إنشاء كائنات وسيطة داخل الـ Loops وسلاسل المجموعات يسبب ضغطاً هائلاً على مجمّع القمامة (GC Churn) وسقوط فريمات في الواجهة. المراجعة الهندسية تضمن كوداً نظيفاً، مستقراً، وموفراً للذاكرة.",
            "worked_example_ar": "إعادة صياغة API غامض إلى عقد هندسي صريح وموفر للذاكرة:\n```kotlin\n// كود يعاني من غموض الـ Null وتكلفة الذاكرة:\ninterface BadCatalog {\n    fun getUsers(): List<String>? // هل null تعني خطأ في الشبكة أم غياب مستخدمين؟\n}\n\n// التصميم الهندسي الصريح بعد المراجعة:\nsealed interface CatalogResult {\n    data class Success(val users: List<UserId>) : CatalogResult\n    data object Empty : CatalogResult\n    data class Failure(val cause: Throwable) : CatalogResult\n}\n\n@JvmInline\nvalue class UserId(val value: String)\n```\nهذا التصميم يفصل بوضوح بين حالات النجاح والغياب والأخطاء بدون أي غموض في الـ Null.",
            "trade_offs_ar": "إرجاع أنواع صريحة ومختومة (Sealed Interfaces) يزيد من عدد الملفات والتعريفات في المشروع، لكنه يقضي تماماً على تخمين المستدعي ويمنع أخطاء الإنتاج. استخدام Sequences يمنع إنشاء مصفوفات وسيطة في السلاسل الطويلة، ولكنه يضيف عبء كائنات الـ Iterator في المجموعات الصغيرة. التحسين الهندسي يبنى على القياس الفعلي بالأدوات وليس التخمين النظري.",
            "failure_modes_ar": "إرجاع قائمة قابلة للـ Null حيث يفسر المستدعي القيمة الفارغة على أنها غياب بيانات بينما هي عطل في الاتصال مما يخفي أعطال السيرفر. تمرير كائنات Java Platform Types بدون فحص صريح مما يفجر كراش NPE لاحقاً في مكان بعيد عن مصدر الخطأ. استخدام دوال Scope متداخلة بشكل معقد يخفي المتغير الحقيقي المقصود داخل الكتل.",
            "production_perspective_ar": "في الشركات الكبيرة، لا نعتمد فقط على المراجعة اليدوية؛ بل ندمج أدوات الفحص الآلي مثل Detekt و Android Lint في مسار الـ CI لمنع استخدام `!!` وحظر الدوال المعقدة تلقائياً. كما نستخدم إضافة Binary Compatibility Validator لضمان عدم كسر التوافق الثنائي للـ APIs المشتركة بين الفرق المختلفة.",
            "how_to_answer_ar": "- **البداية بالأعمدة الأساسية:** قسّم المراجعة إلى Null Safety، تكلفة الذاكرة، والمقروءية.\n- **محور الأمان:** بيّن حظر `!!` الصارم وكيفية التعامل مع Java Platform Types والـ Sealed Classes.\n- **محور الذاكرة:** وضح Sequences بدلاً من السلاسل الوسيطة، وحذر من الـ Boxing لكلاسات القيمة والـ Lambdas في الحلقات.\n- **محور المقروءية:** ركز على الـ Immutability، كشف List بدلاً من MutableList، وتجنب الـ Scope Functions المعقدة.\n- **منظور الـ Staff:** تحدث عن أتمتة القواعد في الـ CI واستقرار كلاسات Compose.",
            "talking_points_ar": "ناقش توافق الـ Bytecode، واستقرار بارامترات Jetpack Compose لتفادي إعادة الرسم غير الضرورية، وتكلفة الـ Inlining العشوائي على حجم ملف الـ DEX، واستخدام Value Classes بدون Boxing، ومراقبة الـ Allocations عبر Android Studio Profiler.",
            "follow_ups_ar": "- **المحاور:** \"كيف تكتشف الـ Boxing غير المقصود لـ Value Class أثناء الـ Code Review؟\"\n  **المرشح:** \"بفحص استخدام الـ Value Class؛ لو تم تمريرها لـ Generic Interface أو وضعها في `List<Any>` أو استخدامها كـ Nullable type، المترجم بيضطر يعمل ليها Boxing وينشئ كائن في الـ Heap، وده بيلغي ميزة التوفير. بنكشف ده بمراجعة الاستخدامات وتفقد الـ Bytecode إذا لزم الأمر.\"\n\n- **المحاور:** \"لماذا نمنع كشف MutableList في الـ Public APIs؟\"\n  **المرشح:** \"لأن كشف واجهة قابلة للتعديل يكسر مبدأ الـ Encapsulation ويسمح لأي كود خارجي بتعديل البيانات المشتركة بدون علم الكلاس، وده بيسبب سباق بيانات ConcurrentModificationException ويجعل تتبع الأخطاء شديد الصعوبة.\"",
            "self_check_ar": "هل غطيت محاور الأمان من الـ Null؟ هل بينت تكلفة الذاكرة وسلاسل المجموعات والـ Boxing؟ وهل وضحت معايير المقروءية وأتمتة الفحص في الـ CI؟",
            "references_ar": "- [Kotlin coding conventions](https://kotlinlang.org/docs/coding-conventions.html) — معايير كتابة وتصميم كود Kotlin النظيف.\n- [Jetpack Compose stability](https://developer.android.com/develop/ui/compose/performance/stability) — استقرار الكلاسات وتفادي إعادة الرسم غير الضرورية.\n\nتمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13.",
            "quick_answer_ar": "براجع كود Kotlin بالتركيز على تلات محاور رئيسية: أولاً أمان الـ Null بمنع الـ force-unwrap نهائياً واستخدام Sealed Interfaces لتوضيح النتائج وحماية حدود Java. ثانياً كفاءة الذاكرة بتفادي الـ intermediate allocations في سلاسل الـ Collections واستخدام Sequences للبيانات الكبيرة ومنع الـ boxing. ثالثاً المقروءية بفرض الـ Immutability وكشف واجهات القراءة فقط.",
            "best_answer_ar": "في مراجعة الكود، بنطلق من مبدأ إن الـ API بيتقرأ ويُستهلك أضعاف المرات اللي اتكتب فيها، علشان كده تركيزي بيكون على تلات ركائز أساسية.\n\nالركيزة الأولى هي الـ Null Safety؛ عندي رفض قاطع لأي استخدام للـ double-bang operator. بفحص حدود النظام اللي بتدخل منها بيانات من مكتبات Java وبتعامل معاها كـ Nullable فوراً، وبستبدل إرجاع القيم الـ Nullable الغامضة بـ Sealed Interface صريح بيعبر بوضوح عن النجاح أو غياب النتيجة أو حدوث خطأ مجالي.\n\nالركيزة التانية هي تكلفة الذاكرة والـ Allocations؛ بدقق في سلاسل التحويلات على الـ Collections زي filter و map ورا بعض لأن كل خطوة بتنشئ ArrayList وسيطة في الـ Heap، وبوجه لاستخدام Sequences لو البيانات كبيرة. وكمان بتأكد إن الـ Value Classes مبيحصلش ليها Boxing غير مقصود داخل Generic Collections.\n\nالركيزة التالتة هي الـ Idiomatic Readability؛ بمنع كشف MutableList في الـ Public APIs وبفرض استخدام List للقراءة فقط، وبمنع تشابك الـ Scope Functions زي let جوه also جوه apply اللي بتعقد مسار القراءة الذهني.",
            "deep_answer_ar": "على مستوى الـ Staff Engineer، المراجعة مش مجرد تفقد للشكل الجمالي للكود، دي حراسة معمارية للأداء والاستقرار على المدى الطويل.\n\nأولاً، بنفعل أدوات الفحص الآلي زي Detekt و Android Lint داخل الـ CI pipeline علشان تمنع ميكانيكياً أي مخالفات بديهية زي استخدام `!!` أو وجود `lateinit` غير مبرر، وده بيخلي المراجعين يركزوا على القرارات المعمارية العميقة.\n\nثانياً، لما الكود يكون مرتبط بـ Jetpack Compose، بدقق جداً في استقرار الـ Data Classes اللي بتتباصى للـ Composables. لازم الخصائص تكون val والـ Collections تكون معتمدة على Immutable Collections، علشان الـ Compose Compiler يعلم الكلاس كـ Stable ويقدر يعمل Recomposition Skipping ويوفر فريمات الشاشة.\n\nثالثاً، بنراقب الـ Allocations على مستوى الـ Bytecode؛ استخدام الدوال ذات الـ reified type parameters مع inline ممتاز وموفر، لكن الإفراط في الـ Inlining لدوال ضخمة بيضخم حجم ملف الـ DEX ويرهق الـ Instruction Cache في المعالج. وكمان التحقق من عدم عمل Boxing لكلاسات الـ @JvmInline value class وقت تمريرها لـ Generic Parameters.\n\nوأخيراً في المكتبات المشتركة، بنشغل Jetpack Binary Compatibility Validator لضمان إن أي تعديل في الـ Public API ميكسرش الـ ABI مع الموديولات المستهلكة بدون علم الفريق."
        }
    }
}

def run():
    qid = "KOT-30"
    data = DATA[qid]
    ee.update_canonical_question(
        qid=qid,
        concept_en=data["concept_en"],
        walkthrough_en=data["walkthrough_en"],
        structured_en=data["structured_en"],
        deep_senior_en=data["deep_senior_en"],
        short_en=data["short_en"],
    )
    print(f"Updated canonical question {qid}")

    meta_file = SCRIPT_DIR / "data" / "metadata_kot_30.json"
    meta_file.write_text(json.dumps({qid: data["meta_ar"]}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Saved Arabic metadata to {meta_file}")

    ee.merge_all_metadata()
    errs = ee.validate_question(qid)
    if errs:
        print(f"❌ {qid} validation failed with {len(errs)} errors:")
        for e in errs:
            print("  -", e)
        sys.exit(1)
    else:
        print(f"✅ {qid} passed validation with 0 errors!")

if __name__ == "__main__":
    run()
