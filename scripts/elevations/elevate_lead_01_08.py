#!/usr/bin/env python3
"""
Elevation script for LEAD questions: LEAD-01 to LEAD-08.
Topic: Senior Ownership, Communication & Technical Leadership (LEAD)
Phase 5, Batch 1
"""

import os
import sys

sys.path.insert(0, os.path.abspath("scripts/elevations"))
import elevation_engine as ee

TOPIC_AR = "القيادة التقنية والتواصل وملكية المشاريع الهندسية"
REVIEWED_DATE_AR = "تمت المراجعة والتحقق في 17 أكتوبر 2026"

DATA = {}

# ==========================================
# LEAD-01: How do you explain architectural trade-offs clearly in an interview?
# ==========================================
DATA["PAY-01"] = None  # placeholder
DATA["LEAD-01"] = {
    "concept_en": """Articulating architectural trade-offs in senior technical interviews requires demonstrating that engineering choices are never absolute solutions, but conscious compromises grounded in empirical constraints:
- The Senior Axiom: \"There are no solutions, only trade-offs\" (Thomas Sowell).
  - Junior engineers often seek a single \"ideal\" paradigm or dogmatically defend a favorite library or pattern.
  - Staff and Lead engineers evaluate choices through the lens of business constraints, team capabilities, codebase scale, and runtime costs.
- The 4-Stage Architectural Trade-off Framework:
  1. Context & Constraints Framing:
     - Clarify non-functional requirements: team velocity, time-to-market, team size, target device demographics (emerging markets vs flagship devices), and runtime memory/battery limits.
  2. Multi-Option Comparison:
     - Compare at least two viable alternatives honestly, presenting both advantages and tangible drawbacks (e.g., comparing MVI state predictability vs boilerplate object allocation churn).
  3. Context-Driven Rationale:
     - Explain precisely *why* the chosen pattern fits the current constraints, explicitly naming the accepted disadvantages and how their risks are mitigated.
  4. Evolution and Exit Strategy:
     - Define the conditions under which this architecture should be refactored or reversed if user scale, team size, or throughput increases tenfold.""",
    "walkthrough_en": """Framing architectural trade-offs systematically in Kotlin using a Dependency Injection evaluation matrix:
```kotlin
// Architectural Comparison Matrix: Hilt vs Koin vs Pure Manual DI
sealed interface DiArchitectureStrategy {
    val compileTimeSafety: Boolean
    val buildTimeImpactMs: Long
    val runtimeOverhead: String

    // Option A: Standard Google Recommendation
    object HiltDagger : DiArchitectureStrategy {
        override val compileTimeSafety = true // Zero runtime crash risk for missing dependencies
        override val buildTimeImpactMs = 45_000L // Heavy annotation processing overhead via KSP
        override val runtimeOverhead = "Negligible direct bytecode instantiation"
    }

    // Option B: Lightweight Service Locator
    object KoinServiceLocator : DiArchitectureStrategy {
        override val compileTimeSafety = false // Runtime resolution risks crash if definition missing
        override val buildTimeImpactMs = 1_000L // Blazing fast builds, zero code-generation
        override val runtimeOverhead = "Reflective dictionary lookups on application startup"
    }
}

// Verbal Formulation Pattern:
// "In our 40-developer team, we chose Hilt despite the 45-second build penalty.
// Our top constraint was eliminating runtime crashes in production releases.
// We mitigated the build overhead by modularizing our Gradle graph and isolating KSP tasks."
```""",
    "short_en": """Explain architectural trade-offs by framing decisions around constraints rather than dogma. Articulate the problem context, compare viable alternatives with their tangible drawbacks, justify the selection based on team and product constraints, and define an explicit reversal condition if scale or requirements change.""",
    "structured_en": """Articulating architectural trade-offs effectively in a senior engineering interview requires demonstrating pragmatic maturity over technical dogma.
Senior engineers understand that every architecture is a compromise. A compelling response follows a structured four-stage narrative.
First, establish the context and operational constraints, clarifying team size, delivery timelines, target device capabilities, and code maintainability.
Second, present viable alternatives fairly, evaluating their pros and cons. For instance, when comparing MVI to MVVM, contrast MVI\'s predictable unidirectional state flow with its higher allocation overhead and boilerplate.
Third, justify the chosen approach against the stated constraints, explicitly naming the trade-offs you chose to accept and explaining how you mitigated those downsides.
Finally, outline an evolution trigger, describing the exact metrics, such as team growth or throughput spikes, that would warrant revisiting the decision.""",
    "deep_senior_en": """From an engineering leadership and systems architecture perspective, communicating architectural trade-offs is the ultimate test of a candidate\'s technical discernment and stakeholder empathy.
Interviewers evaluate whether an engineer makes decisions driven by technological fashion or business value. Immature responses present a chosen tool as universally superior while dismissing alternatives. In contrast, senior leaders operate from first principles, acknowledging that every architectural pattern incurs a debt that must be managed.
When framing a decision, begin by anchoring the narrative in business and engineering reality. Describe the team composition, the release frequency, the target hardware spectrum, and performance SLAs.
Next, construct an objective trade-off matrix. When discussing asynchronous architectures, contrast Kotlin Coroutines against RxJava: Coroutines offer superior readability, native structured concurrency, and lower memory overhead, but RxJava historically offered richer specialized backpressure operators.
State the rationale decisively: explain why the team accepted Coroutines and how you resolved team knowledge gaps through internal tech talks and lint rules.
Conclude by presenting an evolution trigger and off-ramp strategy. Describe the operational thresholds, whether in crash rates, build duration, or latency percentiles, that would signal that the architecture has reached its scaling limits. This structured transparency proves that you design software systems capable of evolving gracefully under organizational growth.""",
    "meta_ar": {
        "id": "LEAD-01",
        "questionAr": "كيف تشرح المفاضلات المعمارية (Architectural Trade-offs) بوضوح واحترافية في المقابلة التقنية لمنصب Senior/Lead؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "النضج الهندسي وتجنب التعصب للأنماط (Dogmatism)، إطار عمل المفاضلات (Context, Options, Rationale, Evolution)، التبرير بناءً على القيود الواقعية، وتحديد شروط التراجع والتطوير.",
        "concept_ar": "يتطلب شرح المفاضلات المعمارية (Architectural Trade-offs) في المقابلات التقنية المتقدمة إثبات أن القرارات الهندسية ليست حلولاً مثالية بالمطلق، بل هي صفقات مقايضة واعية تحكمها القيود: فالمهندس المبتدئ يبحث عن 'الحل السحري الوحيد' ويدافع عن مكتبة معينة بتعصب؛ بينما يدرك المهندس القيادي (Lead Engineer) مقولة توماس سويل الشهيرة بأنه 'لا توجد حلول، بل توجد مفاضلات فقط'. وتعتمد صياغة الإجابة المقنعة على إطار من 4 مراحل: أولاً، تأطير السياق والقيود بتوضيح حجم الفريق وسرعة التسليم ومواصفات أجهزة المستخدمين؛ ثانياً، مقارنة البدائل المتاحة بنزاهة مع ذكر عيوب ومزايا كل خيار؛ ثالثاً، تبرير القرار باختيار الحل الذي يحقق أكبر مكسب بأقل تكلفة مع توضيح العيوب المقبولة وكيفية تحجيمها؛ رابعاً، وضع استراتيجية تطور وشروط واضحة للتراجع عن القرار إذا تغيرت المعطيات مستقبلاً.",
        "walkthrough_ar": """مصفوفة مفاضلة معمارية واقعية لاختيار مكتبة حقن التبعيات وصياغتها اللفظية في كوتلن:
```kotlin
// مصفوفة مقارنة معمارية لاختيار حقن التبعيات: Hilt مقابل Koin
sealed interface DiArchitectureStrategy {
    val compileTimeSafety: Boolean
    val buildTimeImpactMs: Long
    val runtimeOverhead: String

    // الخيار الأول: توصية جوجل الرسمية
    object HiltDagger : DiArchitectureStrategy {
        override val compileTimeSafety = true // أمان كامل أثناء التجميع ومنع كراشات الإنتاج
        override val buildTimeImpactMs = 45_000L // بطء في التجميع بسبب معالجة الرموز KSP
        override val runtimeOverhead = "استدعاء مباشر فائق السرعة عبر الكود المولد"
    }

    // الخيار الثاني: محدد الخدمات الخفيف
    object KoinServiceLocator : DiArchitectureStrategy {
        override val compileTimeSafety = false // خطورة حدوث كراش أثناء التشغيل إذا نُسي تعريف عنصر
        override val buildTimeImpactMs = 1_000L // سرعة بناء فائقة دون أي توليد للكود
        override val runtimeOverhead = "بحث بالانعكاس في القواميس عند بدء تشغيل التطبيق"
    }
}

// الصياغة اللفظية في المقابلة:
// "اخترنا Hilt في فريقنا المكون من 30 مطوراً رغم زيادة وقت البناء 45 ثانية؛
// لأن أولويتنا كانت منع كراشات الـ Missing Dependency في الإنتاج تماماً،
// وخففنا أثر بطء البناء بتقسيم المشروع لموديولات مستقلة."
```""",
        "why_it_matters_ar": "التعصب المعماري يورط الشركات في تقنيات معقدة لا تناسب احتياجاتها وتزيد تكاليف الصيانة وتبطئ سرعة وصول الميزات للمستخدمين.",
        "worked_example_ar": "في تطبيق تجاري، فضل الفريق استخدام MVVM البسيط بدلاً من MVI المعقد لأن الفريق كان يضم مطورين جدداً والموعد النهائي قريب، مما سرع الإطلاق بشهرين دون تعقيد الكود.",
        "trade_offs_ar": "الأنماط الصارمة تضمن أعلى درجات الأمان المعماري لكنها تزيد وقت البناء والـ Boilerplate؛ والتوازن يكمن في اختيار النمط الأنسب لحجم الفريق الحالي.",
        "failure_modes_ar": "أخطر الأخطاء هو الادعاء بأن الأداة المختارة ليس بها أي عيوب، أو إهانة الحلول البديلة وتجاهل سياق المشروع وتكلفة الصيانة.",
        "production_perspective_ar": "في المقابلات الكبرى، يبحث المحاورون عن القدرة على التراجع الذكي؛ متى تقول 'لو تضاعف حجم الفريق لغيرت هذا القرار فوراً'.",
        "how_to_answer_ar": "ابدأ برفض فكرة الحل المثالي، ثم طبق الخطوات الأربع: حدد سياق المشكلة والقيود، واطرح بديلين، وبرر اختيارك بذكر العيوب المقبولة، واختم ببيان متى تغير قرارك.",
        "talking_points_ar": "مبدأ المفاضلات Trade-offs، تأطير السياق والقيود، مقارنة البدائل بنزاهة، العيوب المقبولة، واستراتيجية التراجع والتطور عند التوسع.",
        "follow_ups_ar": "ما هي المؤشرات أو المقاييس التي تدفعك لإلغاء هذا القرار المعماري بعد ستة أشهر من إطلاقه في الإنتاج؟",
        "self_check_ar": "هل تجنبت التعصب للأدوات، وطرحت بديلاً منافساً، وذكرت العيوب التي قبلت التعايش معها، وحددت شروط التراجع؟",
        "references_ar": f"- [Martin Fowler: Architecture Trade-off Analysis](https://martinfowler.com/architecture/) — المرجع الهندسي الكلاسيكي لتحليل المفاضلات المعمارية واتخاذ القرارات البرمجية.\n- [Gregor Hohpe: The Software Architect Elevator](https://architectelevator.com/) — دليل القيادة المعمارية والتواصل الفعال بين فرق الهندسة وأصحاب القرار.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """نشرح المفاضلات المعمارية بتأطير القرار حول القيود لا التعصب، انطلاقاً من مبدأ أنه لا توجد حلول مثالية بل مقايضات مدروسة. نحدد سياق المشكلة وحجم الفريق، ونقارن بديلين بنزاهة مع توضيح عيوب ومزايا كل منهما، ونبرر اختيارنا بالعيوب التي قبلنا التعايش معها، ونحدد شروط التراجع وتطوير القرار مستقبلاً.""",
        "best_answer_ar": """يتطلب شرح المفاضلات المعمارية باحترافية في مقابلات القيادة التقنية إظهار النضج البرمجي وتجنب التعصب للأنماط والمكتبات.
يدرك المهندس الخبير أن كل قرار معماري يحمل ثمناً يجب إدارته، وتُبنى الإجابة المقنعة وفق إطار عمل محكم من أربع مراحل.
نبدأ أولاً بتأطير سياق المشكلة وقيودها المحددة؛ مثل حجم الفريق، والجدول الزمني للوصول للسوق، ومواصفات أجهزة المستخدمين المستهدفة.
ثم نطرح البدائل القابلة للتطبيق بموضوعية؛ فمثلاً عند مقارنة MVI وMVVM نبرز قابلية MVI العالية للتنبؤ مقابل تكلفة توليد الكائنات وتعقيد الصياغة.
بعد ذلك نبرر القرار بناءً على القيود القائمة، مع ذكر العيوب التي قبلنا التعايش معها وكيف قمنا بتحجيم مخاطرها التشغيلية.
وأخيراً نختم بتحديد استراتيجية التطور وشروط التراجع؛ موضحين المقاييس الدقيقة كنمو الفريق أو مضاعفة البيانات التي قد تدفعنا لإعادة النظر في القرار، مما يثبت التفكير الاستراتيجي المستدام.""",
        "deep_answer_ar": """من منظور القيادة الهندسية وتصميم النظم الموسعة، يمثل التواصل المعماري الفعال الاختبار الأهم لنضج المهندس وقدرته على موازنة الأهداف التقنية مع قيمة الأعمال.
في مقابلات المستويات العليا، لا يبحث الممتحن عن حفظ للمكتبات بل عن منهجية التفكير؛ فالإجابات السطحية تدعي دائماً أن النمط المفضل هو الأفضل مطلقاً. أما القائد التقني فينطلق من القواعد الأساسية معترفاً بأن كل خيار معماري هو مقايضة محسوبة تفرض كلفة صيانة مستقبلية.
وعند استعراض أي قرار، نؤسس السردية على واقع المشروع الفعلي: تركيبة الفريق، وتواتر الإطلاقات، ومواصفات المعالجات في هواتف المستخدمين.
ثم نبني مصفوفة مقارنة عادلة؛ فعند مناقشة المعمارية اللامركزية عبر Coroutines مقابل RxJava، نوضح تفوق Coroutines في الإلغاء الهيكلي وسهولة القراءة، في مقابل نضج مشغلات الـ Backpressure في النمط القديم.
ونوضح بعد ذلك مبررات الاختيار بحسم: كيف قبل الفريق بمنحنى تعلم تقنية معينة ووضع خطة لتأهيل المطورين عبر جلسات معرفية وأدوات فحص آلية.
ونختتم دائماً بمحفزات التراجع وشروط التوسع؛ محددين عتبات الأداء ومعدلات الأعطال التي تشير إلى وصول النمط لحدوده القصوى وتستوجب الانتقال لمستوى معماري جديد. هذا الطرح المتزن والشفاف يبرهن على بناء برمجيات قادرة على التطور مع نمو المؤسسة بكفاءة واقتدار، ويؤكد قدرة المهندس على قيادة التحولات التقنية المعقدة بثقة وهدوء."""
    }
}
del DATA["PAY-01"]

# ==========================================
# LEAD-02: How do you review code for correctness, security, readability, and testability?
# ==========================================
DATA["LEAD-02"] = {
    "concept_en": """A disciplined code review methodology elevates team engineering standards by automating mechanical checks and focusing human review on architectural invariants, security, and edge cases:
- The Senior Review Philosophy:
  - Automate the Trivial: Formatting, naming conventions, import ordering, and static linting must be enforced automatically in CI via ktlint, Detekt, and Android Lint. Human reviewers should never waste time debating indentation.
  - Review for Depth: Focus cognitive effort on system correctness, security vectors, concurrency hazards, lifecycle boundaries, and testability.
- The 4-Pillar Review Rubric:
  1. Correctness & Concurrency:
     - Are race conditions, deadlocks, or coroutine leaks possible? Is cancellation handled gracefully? Are state mutations atomic? Are edge cases (nulls, empty collections, boundary numbers) tested?
  2. Security & Compliance:
     - Is user input sanitized? Are credentials, tokens, or PII exposed to Logcat or SharedPreferences? Are Intent extras and exported components secured?
  3. Readability & Maintainability:
     - Does the code reveal its intent clearly? Are domain abstractions intuitive? Are public functions self-documenting without misleading comments?
  4. Testability & Modularity:
     - Is the logic decoupled from Android framework lifecycles? Can external dependencies be substituted with deterministic fakes? Are tests asserting behaviors rather than implementation details?
- The Empathetic Review Culture:
  - Frame critiques as collaborative questions (\"What happens if the network drops here?\" instead of \"You forgot timeout handling\").
  - Distinguish blocking blockers from non-blocking suggestions using explicit prefixes (e.g., `nit:`, `suggestion:`, `blocking:`).""",
    "walkthrough_en": """Structured Code Review checklist and PR feedback model in Kotlin:
```kotlin
// Example Pull Request under Review: User Profile Updater
class UserProfileViewModel(
    private val repository: UserRepository,
    private val analytics: AnalyticsTracker
) : ViewModel() {

    // CODE REVIEW DEFECT 1 (Correctness): Non-atomic state mutation and missing cancellation
    // CODE REVIEW DEFECT 2 (Security): Logging raw PII (email) into production analytics
    fun updateEmail(newEmail: String) {
        viewModelScope.launch {
            analytics.logEvent("email_change_attempt", mapOf("email" to newEmail)) // SECURITY HAZARD
            val result = repository.updateEmail(newEmail)
            // Lacks error handling or loading state management
        }
    }
}

// Senior Reviewer Constructive Feedback Format:
// [Blocking / Security]: Under GDPR and PCI rules, we cannot log cleartext email addresses.
//   Please mask the email or log an anonymized userId instead: `hashSha256(email)`.
// [Blocking / Correctness]: If the user navigates away or taps twice rapidly, duplicate requests fire.
//   Suggestion: Use an in-flight UI state check or throttle via flatMapLatest.
// [Nit / Readability]: Could we extract the validation regex into a domain value object `EmailAddress`?
```""",
    "short_en": """Review code by automating mechanical formatting via CI and focusing human review on correctness, security, readability, and testability. Verify concurrency safety, lifecycle boundaries, zero PII leakage, and test coverage using deterministic fakes. Communicate empathetically using explicit tags to distinguish blocking architectural defects from non-blocking suggestions.""",
    "structured_en": """A senior code review process balances rigorous technical scrutiny with a collaborative, empathetic engineering culture.
The foundation of effective code review is delegating mechanical checks like linting, code formatting, and syntax validation entirely to automated CI tools like ktlint and Detekt, freeing engineers to focus on substantive architecture.
Human review evaluates four essential dimensions.
Correctness examines concurrency hazards, race conditions, memory leaks, and boundary conditions.
Security verifies that sensitive data like PII and tokens are never logged or insecurely stored and ensures all external inputs and IPC boundaries are validated.
Readability assesses whether the code clearly expresses business intent and avoids unnecessary complexity.
Testability ensures that components are loosely coupled and that unit tests verify behavioral contracts rather than brittle internal implementation details.
Finally, senior reviewers communicate constructively, providing clear rationale and using explicit tags like blocking or nit to distinguish mandatory fixes from educational advice.""",
    "deep_senior_en": """From an engineering leadership and continuous delivery perspective, code review is the primary mechanism for knowledge distribution, architectural governance, and collective code ownership.
Ineffective code review cultures suffer from two common anti-patterns: shallow bikeshedding, where reviewers bicker over variable names and curly brace placement, and rubber-stamping, where large pull requests are approved without inspection. Senior leaders eliminate bikeshedding by mandating that any rule capable of being automated must be enforced via pre-commit hooks and CI gates like Detekt and Android Lint.
This elevates the review to architectural forensics. Reviewers inspect concurrency correctness: verifying that Coroutine dispatchers are injected rather than hardcoded, that shared mutable state is guarded by Mutex or atomic primitives, and that cancellation exceptions are never swallowed in catch-all blocks.
In the security domain, reviewers verify zero-trust data handling: validating that PII is masked, that sensitive flags prevent screenshot capture in banking flows via FLAG_SECURE, and that exported Android components enforce custom signature permissions.
For testability, reviewers check that ViewModels interact with domain interfaces, ensuring that test suites utilize fast, deterministic fakes rather than fragile mocks that mirror private methods.
Equally important is the human delivery. High-performing engineering teams adopt conventional comments, labeling feedback as blocking, suggestion, or praise. Reviewers explain the underlying mechanical rationale, transforming every pull request into an uplifting mentorship opportunity that levels up the entire team.""",
    "meta_ar": {
        "id": "LEAD-02",
        "questionAr": "كيف تراجع الشيفرة البرمجية (Code Review) لضمان الصحة البرمجية، والأمان، وقابلية القراءة والاختبار؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "منهجية مراجعة الكود الاحترافية، أتمتة الفحص الشكلي (ktlint/Detekt)، الركائز الأربع (الصحة، الأمان، المقروئية، وقابلية الاختبار)، وثقافة المراجعة البناءة والتعليقات الإيجابية.",
        "concept_ar": "ترتكز مراجعة الشيفرة البرمجية (Code Review) الاحترافية على أتمتة الفحوصات الشكلية وتكريس الجهد البشري لتقييم المعمارية وصحة المنطق والأمان وقابلية الاختبار: الخطوة الأولى هي تفويض التنسيق ومطابقة المعايير بالكامل لأدوات آلية في خطوط الـ CI مثل ktlint وDetekt وAndroid Lint؛ فلا يجوز للمراجع إضاعة وقته في مناقشة المسافات أو أسماء المتغيرات. وتركز المراجعة البشرية على 4 ركائز حاسمة: أولاً، الصحة البرمجية (Correctness) بفحص تسريب الذاكرة، وسباق الخيوط (Race Conditions)، وإلغاء الكوروتين، ومعالجة الحالات الحافة؛ ثانياً، الأمان (Security) بمنع تسجيل بيانات حساسة (PII) في السجلات، والتحقق من صحة المدخلات وتأمين الـ Intents؛ ثالثاً، المقروئية (Readability) بوضوح النية المعمارية وتجنب التعقيد؛ رابعاً، قابلية الاختبار (Testability) بحقن التبعيات وعدم الاعتماد على سياق أندرويد في منطق الأعمال. كما تتطلب المراجعة ثقافة تواصل بناءة عبر صياغة الملاحظات كأسئلة تشاركية واستخدام وسوم واضحة للتمييز بين التعليقات الإلزامية (Blocking) والاقتراحات الجانبية (Nit).",
        "walkthrough_ar": """نموذج مراجعة كود عملي يوضح رصد الثغرات وتقديم الملاحظات البناءة في كوتلن:
```kotlin
// كود معروض للمراجعة في Pull Request:
class UserProfileViewModel(
    private val repository: UserRepository,
    private val analytics: AnalyticsTracker
) : ViewModel() {

    // ملاحظة صحة وأمان: تسجيل البريد في السجلات خرق لمعايير الخصوصية، وتكرار النداء غير معالج
    fun updateEmail(newEmail: String) {
        viewModelScope.launch {
            analytics.logEvent("email_change_attempt", mapOf("email" to newEmail)) // خرق أمني!
            val result = repository.updateEmail(newEmail)
            // غياب معالجة الأخطاء وحالة التحميل
        }
    }
}

// أسلوب كتابة الملاحظات الاحترافي من مهندس Senior:
// [Blocking / Security]: وفقاً للوائح الخصوصية، يُحظر تسجيل البريد الإلكتروني كنص صريح.
//   يرجى تشفير البريد عبر Hash أو تسجيل معرّف المستخدم المشفر بدلاً منه.
// [Blocking / Correctness]: إذا نقر المستخدم مرتين بسرعة سيتم إرسال طلبين متزامنين.
//   اقتراح: تعطيل الزر أثناء المعالجة أو استخدام StateFlow لمنع التكرار.
// [Nit / Readability]: هل يمكن نقل التحقق من صيغة البريد إلى كائن قيمة Value Object مستقل؟
```""",
        "why_it_matters_ar": "المراجعة السطحية تسمح بتسريب ثغرات أمنية وكراشات للإنتاج، بينما المراجعة المتزمتة تعطل المطورين وتخلق بيئة عمل محبطة ومنفرة.",
        "worked_example_ar": "أوقف مراجع دمج كود كان يستدعي دالة حظر خيط الواجهة Thread.sleep؛ وشرح للمطور كيفية استبدالها بـ delay داخل الكوروتين مما حمى التطبيق من كراش ANR مؤكد.",
        "trade_offs_ar": "التدقيق العميق في كل PR يستغرق وقتاً إضافياً؛ لكنه يوفر أضعاف هذا الوقت الذي كان سيُهدر في معالجة كوارث الإنتاج بعد الإطلاق.",
        "failure_modes_ar": "أخطر الأخطاء هو الجدال حول التنسيق اليدوي وترك ثغرات السباق والتزامن، أو استخدام نبرة حادة وتهجمية على المطورين بدلاً من التوجيه المهني.",
        "production_perspective_ar": "في الشركات التقنية الكبرى، يُلزم الفريق باستخدام وسوم التعليقات مثل [Blocking] للمشاكل المعمارية و[Nit] للتحسينات التجميلية لسرعة دمج الكود.",
        "how_to_answer_ar": "ابدأ ببيان أتمتة الفحص الشكلي في CI، ثم اشرح الركائز الأربع (الصحة، الأمان، المقروئية، وقابلية الاختبار)، واختم بثقافة المراجعة واستخدام وسوم التعليقات البناءة.",
        "talking_points_ar": "أتمتة الفحص الشكلي Linting، الركائز الأربع لمراجعة الكود، سباق الخيوط Race Conditions، خصوصية البيانات PII، الوسوم التقليدية Conventional Comments، والتعليقات البناءة.",
        "follow_ups_ar": "كيف تتصرف إذا أصر مهندس على دمج كود يحتوي على عيب معماري وترفض التنازل عنه؟ وكيف تمنع تراكم الـ PRs الكبيرة؟",
        "self_check_ar": "هل أكدت على أتمتة التنسيق، وشرحت الركائز الأربع بالتفصيل، وأبرزت أهمية الأسلوب البناء في كتابة الملاحظات؟",
        "references_ar": f"- [Google Engineering Practices: Code Review Developer Guide](https://google.github.io/eng-practices/review/) — الدليل المرجعي العالمي المعتمد من شركة جوجل لأفضل ممارسات مراجعة الشيفرات البرمجية.\n- [Conventional Comments: Standardizing PR feedback](https://conventionalcomments.org/) — معيار التنسيق والتصنيف المعتمد لملاحظات مراجعة الأكواد البرمجية.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """نراجع الكود بأتمتة الفحص الشكلي والتنسيق بالكامل في الـ CI عبر أدوات مثل ktlint وDetekt، وتكريس الجهد البشري لأربع ركائز: صحة المنطق والتزامن، والأمان ومنع تسريب البيانات الحساسة، وقابلية القراءة ونقاء المعمارية، وقابلية الاختبار بفصل سياق أندرويد. ونقدم الملاحظات بأسلوب تشاركي واستخدام وسوم واضحة تميز الملاحظات الحرجة عن الاقتراحات الجانبية.""",
        "best_answer_ar": """ترتكز المنهجية الاحترافية لمراجعة الشيفرة البرمجية على موازنة التدقيق المعماري الصارم مع ثقافة التعاون الإيجابي والتطوير المستمر للفريق.
تبدأ المنهجية بقاعدة ذهبية تنص على تفويض الفحوصات الشكلية والتنسيقية لأدوات الفحص الآلي مثل ktlint وDetekt في خطوط البناء المؤتمت، لتفريغ طاقة المراجعين لتقييم عمق النظام.
وتفحص المراجعة البشرية أربع ركائز أساسية:
أولاً، الصحة البرمجية والتزامن بالتأكد من خلو الكود من سباق الخيوط وتسريب الذاكرة والتعامل السليم مع إلغاء مهام الكوروتين.
ثانياً، الأمان والامتثال بحظر تسجيل أي بيانات شخصية أو بنكية في السجلات وتأمين مكونات التطبيق.
ثالثاً، وضوح النية المعمارية والمقروئية وتفادي التعقيد البرمجي غير المبرر.
رابعاً، قابلية الاختبار بتجريد التبعيات الخارجية والتأكد من أن الاختبارات تفحص السلوك وليس تفاصيل التنفيذ الداخلي.
ويُتوج ذلك بأسلوب تواصل بناء؛ حيث تُصاغ الملاحظات كأسئلة محفزة للتفكير وتُستخدم وسوم صريحة للتمييز بين الأخطاء الإلزامية والاقتراحات التفضيلية.""",
        "deep_answer_ar": """من منظور القيادة الهندسية وتطوير ثقافة الجودة في المؤسسات التقنية، تمثل مراجعة الكود القناة الأهم لنقل المعرفة وترسيخ الملكية الجماعية لقاعدة الكود.
تعاني الفرق الهندسية غير الناضجة من فخين شهيرين: الانشغال بالجدال العقيم حول أسماء المتغيرات والأقواس، أو الموافقة العشوائية السريعة دون فحص حقيقي. ويقضي القادة التقنيون على الجدال السطحي بفرض فحص آلي صارم كشرط مسبق لفتح أي طلب دمج عبر بوابات الـ CI.
وهذا يرفع مستوى المراجعة لتصبح فحصاً جنائياً دقيقاً؛ فيدقق المراجع في سلامة التزامن البرمجي بالتأكد من حقن موزعات الكوروتين بدلاً من كتابتها يدوياً، وحماية الحالات المشتركة بأقفال ذرية، وعدم ابتلاع استثناءات الإلغاء في كتل الاستثناءات العامة.
وعلى الصعيد الأمني، نتحقق من مبدأ الثقة المعدومة؛ بالتأكد من تشفير السجلات وحظر تصوير الشاشات الحساسة بـ FLAG_SECURE والتحقق من مصادقة مدخلات الـ Deep Links.
أما في جانب الاختبارات، فنتأكد من اعتماد الشاشات على واجهات مجردة تتيح استخدام محاكيات برمجية سريعة وحتمية في الـ JVM.
والأهم هو البعد الإنساني؛ حيث نعتمد معايير Conventional Comments بتصنيف الملاحظات إلى إلزامي واقتراح وثناء، مع تقديم المبرر الهندسي وراء كل طلب، محولين كل طلب دمج إلى فرصة تدريبية ممتعة ترتقي بمستوى الفريق بأكمله، وتخلق بيئة هندسية تتسم بالإنتاجية العالية والاحترام المتبادل بين كافة المطورين."""
    }
}

# ==========================================
# LEAD-03: What is technical debt, and how do you prioritize it?
# ==========================================
DATA["LEAD-03"] = {
    "concept_en": """Technical debt is a financial metaphor coined by Ward Cunningham representing the implied future cost incurred when choosing an expedient shortcut over an architecturally sound solution:
- The Financial Metaphor Deconstructed:
  - Principal: The initial effort saved by taking a development shortcut to meet a pressing business deadline.
  - Interest: The continuous friction, slower feature velocity, increased defect rate, and onboarding overhead suffered on every subsequent release until the shortcut is refactored.
- Taxonomy of Technical Debt (Martin Fowler\'s Debt Quadrant):
  1. Deliberate & Prudent: Consciously shipping an MVP with simplified architecture to validate product-market fit, with a scheduled refactoring plan.
  2. Deliberate & Reckless: Taking shortcuts knowing they will cause catastrophic scaling failures, without team consensus or documentation.
  3. Inadvertent & Prudent: Architecture that was optimal at the time of design but becomes legacy as business scale, Android OS capabilities, or user concurrency grows.
  4. Inadvertent & Reckless: Blindly writing low-quality code due to ignorance of platform best practices.
- The 3-Dimensional Prioritization Framework:
  1. Impact on Feature Velocity (Developer Friction): How much does this debt slow down daily feature delivery?
  2. Blast Radius & Defect Density: Does this debt cause recurring production crashes, ANRs, or security vulnerabilities?
  3. Customer & Business Value: Does the debt directly degrade frame rates, app startup time, battery consumption, or conversion rates?
- Sustainable Management Models:
  - The 20% Rule: Dedicate 20% of engineering bandwidth per sprint to technical debt remediation.
  - The Boy Scout Rule: Always leave touched code cleaner than you found it.""",
    "walkthrough_en": """Visualizing technical debt risk scoring and scheduling in Kotlin:
```kotlin
data class TechDebtItem(
    val title: String,
    val velocityImpact: Int,  // 1 (low friction) to 5 (blocks sprint velocity)
    val defectRisk: Int,       // 1 (minor bug) to 5 (production crash / data loss)
    val remediationEffortDays: Int
) {
    // Priority Score = (Velocity Impact * Defect Risk) / Remediation Effort
    val priorityScore: Double
        get() = (velocityImpact * defectRisk).toDouble() / remediationEffortDays.coerceAtLeast(1)
}

// Technical Leadership Debt Registry
val backlog = listOf(
    TechDebtItem("Migrate God Activity to Modular ViewModels", velocityImpact = 5, defectRisk = 4, remediationEffortDays = 5), // Score: 4.0 (TOP PRIORITY)
    TechDebtItem("Replace Deprecated Handler with Coroutines", velocityImpact = 3, defectRisk = 2, remediationEffortDays = 1), // Score: 6.0 (QUICK WIN)
    TechDebtItem("Update Gradle build script to Kotlin DSL", velocityImpact = 2, defectRisk = 1, remediationEffortDays = 4)   // Score: 0.5 (DEFER)
)

// Verbal Framing for Business Stakeholders:
// "Refactoring the Checkout ViewModel will take 3 days, but it prevents the 2-second UI freeze
// and unblocks the next 3 quarterly payment features, recovering 15 developer days overall."
```""",
    "short_en": """Technical debt represents the compounding maintenance interest paid when taking short-term engineering shortcuts. Prioritize debt using a three-dimensional framework: impact on team velocity, defect blast radius, and customer experience. Allocate a dedicated 20% of sprint capacity to refactoring, translating technical debt into business metrics like crash rates and feature lead time.""",
    "structured_en": """Technical debt is the accrued engineering cost and friction resulting from expedient design shortcuts taken to meet short-term deadlines.
Like financial debt, taking on debt can be prudent to validate a product rapidly, but failing to repay the principal accumulates compounding interest in the form of sluggish velocity, frequent bugs, and developer fatigue.
To prioritize technical debt effectively without stalling product delivery, senior engineers evaluate three core dimensions.
First is developer velocity impact: how severely does the legacy component impede daily sprint delivery?
Second is blast radius and defect density: is this subsystem responsible for recurring production crashes or customer escalations?
Third is business customer impact: does the debt directly impair application startup latency or checkout conversion?
We manage debt sustainably by negotiating a continuous twenty percent engineering allocation per sprint and enforcing the Boy Scout Rule, pitching debt remediation to stakeholders in terms of risk mitigation and velocity acceleration.""",
    "deep_senior_en": """From an engineering strategy, capital allocation, and organizational scaling perspective, managing technical debt is fundamentally an exercise in risk governance and ROI optimization.
A naive engineering leader treats all technical debt as an existential crisis, demanding multi-month feature freezes to rewrite codebases from scratch—an approach that frequently destroys companies by severing business revenue. Conversely, a weak engineering leader surrenders entirely to product pressure, accumulating compounding technical liabilities until velocity grinds to zero and engineers resign in frustration.
Senior leaders adopt Ward Cunningham\'s original intent: debt can be a deliberate investment instrument. Shipping an MVP with monolithic architecture to secure market share is prudent, provided the debt is registered, tracked, and scheduled for repayment.
To prioritize remediation objectively, we employ a risk-weighted matrix evaluating velocity penalty, defect blast radius, and business impact. High-priority items are those where refactoring unlocks measurable business leverage: for instance, modularizing an unmaintainable checkout flow that accounts for forty percent of customer support tickets and doubles PR review cycles.
To communicate with executive stakeholders, technical jargon must be translated into business currency. Instead of asking to \"refactor Room queries,\" frame the proposal as \"reducing cold app startup from four seconds to one second to lift checkout conversion by three percent.\"
Operationally, we maintain a rolling twenty percent sprint capacity dedicated to debt liquidation and enforce the Boy Scout Rule, ensuring that continuous refactoring remains an intrinsic part of daily delivery.""",
    "meta_ar": {
        "id": "LEAD-03",
        "questionAr": "ما هو الدَّين التقني (Technical Debt) وكيف تحدد أولويات معالجته بفعالية دون تعطيل تسليم الميزات؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "مفهوم الدَّين التقني ومجاز وراد كانينغهام، التمييز بين الدَّين الحصيف والمتهور، مصفوفة تحديد الأولويات (الأثر على السرعة، نصف قطر الضرر، وقيمة الأعمال)، واستراتيجية تخصيص الـ 20% وقاعدة الكشافة.",
        "concept_ar": "يمثل الدَّين التقني (Technical Debt) استعارة مالية ابتكرها وارد كانينغهام لتوضيح الكلفة المستقبلية المتراكمة لاختيار حل برمجي سريع ومؤقت بدلاً من الحل المعماري الرصين: فكما في القروض المالية، يمثل 'الأصل' الوقت الذي وفرته للإطلاق السريع للمنتج، بينما تمثل 'الفائدة' التباطؤ المستمر في سرعة الفريق وتكرار الأعطال وصعوبة التطوير اللاحق حتى يتم سداد هذا الدَّين بإعادة الهيكلة (Refactoring). وينقسم الدَّين إلى متعمد حصيف (كالسرعة لإطلاق تجريبي مع خطة سداد واضحة) أو متهور ناتج عن غياب الكفاءة. وتحديد الأولويات يتطلب مصفوفة من 3 محاور: أولاً، الأثر على سرعة الفريق (Developer Velocity)؛ ثانياً، كثافة الأعطال ونصف قطر الضرر (Blast Radius) كالكراشات المتكررة؛ ثالثاً، الأثر المباشر على المستخدم وتجربة التطبيق (بطء الفتح واستهلاك البطارية). ولإدارته بنجاح، تخصص الفرق 20% من سعة كل دورة تطوير (Sprint) لسداد الدَّين، مع تطبيق قاعدة الكشافة (Boy Scout Rule) بترك الكود أنظف مما وجدته دائماً وترجمة الدَّين للغة الأرقام التجارية لإقناع مديري المنتجات.",
        "walkthrough_ar": """حساب أولوية سداد الديون التقنية وصياغتها الاستثمارية في كوتلن:
```kotlin
data class TechDebtItem(
    val title: String,
    val velocityImpact: Int,  // أثر التعطيل من 1 إلى 5
    val defectRisk: Int,       // خطورة الكراشات والأعطال من 1 إلى 5
    val remediationEffortDays: Int // الجهد المطلوب بالأيام
) {
    // معامل الأولوية = (أثر التعطيل * خطورة الأعطال) / أيام العمل المطلوبة
    val priorityScore: Double
        get() = (velocityImpact * defectRisk).toDouble() / remediationEffortDays.coerceAtLeast(1)
}

// سجل إدارة الديون التقنية
val debtRegistry = listOf(
    // 1. شاشة معقدة تعطل الفريق وتسبب كراشات: أولوية قصوى
    TechDebtItem("تفكيك Activity الدفع وتحويلها لموديولات", velocityImpact = 5, defectRisk = 4, remediationEffortDays = 5), // 4.0
    // 2. كود عفا عليه الزمن لكن حله سريع جداً: مكسب سريع (Quick Win)
    TechDebtItem("استبدال Handlers بالكوروتين في التنبيهات", velocityImpact = 3, defectRisk = 2, remediationEffortDays = 1), // 6.0
    // 3. تحسين شكلي قليل الأثر: يُؤجل
    TechDebtItem("تحويل إعدادات Gradle إلى Kotlin DSL", velocityImpact = 2, defectRisk = 1, remediationEffortDays = 4)   // 0.5
)

// الصياغة الاستثمارية لمدير المنتج:
// "إعادة بناء شاشة الدفع ستستغرق 3 أيام عمل، لكنها ستقلل زمن تجميد الشاشة بثانيتين
// وتسرع إطلاق ميزات الدفع القادمة بنسبة 40%، مما يوفر 15 يوم عمل للمطورين في الربع القادم."
```""",
        "why_it_matters_ar": "تجاهل الدَّين التقني يؤدي لتراكم الفوائد حتى تتجمد سرعة الفريق تماماً وتكثر الاستقالات وتفشل خطط إطلاق الميزات في مواعيدها.",
        "worked_example_ar": "كان الفريق يعاني من بطء إضافة أي وسيلة دفع جديدة بسبب كود قديم ضخم؛ خصصنا 20% من كل Sprint لمدة شهر لإعادة الهيكلة، مما قلل وقت إضافة أي وسيلة لاحقة من شهر كامل إلى 3 أيام فقط.",
        "trade_offs_ar": "إيقاف العمل على الميزات لسداد كل الديون يضر بنمو الشركة المالي؛ والحل الأمثل هو التقسيط المستمر بتخصيص 20% من كل دورة صيانة دورية.",
        "failure_modes_ar": "أخطر الأخطاء هو المطالبة بإيقاف تطوير الميزات لأشهر لإعادة كتابة التطبيق بالكامل (Rewrite)، أو الحديث بلغة تقنية بحتة تفشل في إقناع الإدارة.",
        "production_perspective_ar": "في الفرق الناضجة، يُربط الدَّين التقني بمؤشرات تجارية واضحة مثل معدل خلو الجلسات من الأعطال وزمن تشغيل التطبيق ومعدل تحويل المبيعات.",
        "how_to_answer_ar": "عرّف الدَّين التقني باستعارة الأصل والفائدة، وفرّق بين الدَّين الحصيف والمتهور، ثم اشرح مصفوفة الأولويات الثلاثية، واختم بنسبة الـ 20% وقاعدة الكشافة.",
        "talking_points_ar": "استعارة وارد كانينغهام، الأصل والفائدة المركبة، الدَّين الحصيف مقابل المتهور، مصفوفة تحديد الأولويات، نسبة الـ 20%، وقاعدة الكشافة Boy Scout Rule.",
        "follow_ups_ar": "كيف تقنع مدير المنتج المتصلب بتخصيص وقت لسداد الدَّين التقني بدلاً من إطلاق ميزات تجارية جديدة يطلبها العملاء؟",
        "self_check_ar": "هل شرحت مفهوم الفائدة والأصل، ووضحت مصفوفة الأولويات، وربطت الدَّين بإنتاجية الفريق وقيمة الأعمال؟",
        "references_ar": f"- [Ward Cunningham: The WyCash Portfolio Management System and Tech Debt Metaphor](http://c2.com/doc/oopsla92.html) — الورقة التاريخية الأصلية التي ابتكرت مجاز الدَّين التقني في هندسة البرمجيات.\n- [Martin Fowler: Technical Debt Quadrant](https://martinfowler.com/bliki/TechnicalDebtQuadrant.html) — المرجع الكلاسيكي لتصنيف الديون التقنية بين الحصيف والمتهور والمتعمد وغير المتعمد.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """الدَّين التقني هو استعارة مالية تمثل الكلفة المستقبلية والتعطيل الناتج عن اختيار حلول سريعة مؤقتة بدلاً من الحلول المعمارية الرصينة. نحدد أولوياته بمصفوفة ثلاثية تقيس الأثر على سرعة المطورين، ونصف قطر الضرر والكراشات، والأثر المباشر على المستخدم والأعمال. ونديره بتخصيص 20% من سعة كل دورة تطوير وتطبيق قاعدة الكشافة بترك الكود أنظف دائماً.""",
        "best_answer_ar": """يمثل الدَّين التقني استعارة مالية دقيقة تصف التكلفة المستقبلية وفقدان المرونة الناتج عن اتخاذ قرارات برمجية سريعة ومختصرة للوفاء بمواعيد الإطلاق.
وكما في القروض المالية، قد يكون الاقتراض قراراً حصيفاً للوصول السريع للسوق واختبار المنتج، لكن إهمال سداد أصل القرض يؤدي لتراكم فوائد مركبة تتمثل في بطء الإنتاجية وكثرة الكراشات وإحباط الفريق.
ولتحديد أولويات سداد الدَّين بفعالية دون تجميد تطوير الميزات، يعتمد القادة التقنيون على مصفوفة ثلاثية الأبعاد:
أولاً، الأثر على سرعة التطوير بتقدير حجم التعطيل اليومي الذي يفرضه هذا الكود على المهندسين.
ثانياً، خطورة الأعطال ونصف قطر الضرر برصد المكونات المسببة لأكبر نسبة من كراشات الإنتاج.
ثالثاً، أثر التجربة وقيمة الأعمال بربط الكود بتحسين زمن فتح التطبيق ومعدلات التحويل.
وتُترجم هذه الأولويات تشغيلياً بتخصيص نسبة مستمرة قدرها عشرون بالمئة من سعة كل Sprint لسداد الديون وتطبيق قاعدة الكشافة لتحسين الكود باستمرار.""",
        "deep_answer_ar": """من منظور الاستراتيجية الهندسية وحوكمة المخاطر المؤسسية، تعد إدارة الدَّين التقني تمريناً متقدماً في تخصيص الموارد وتعظيم العائد على الاستثمار.
فالمهندس غير الناضج يرى في كل دَين تقني كارثة تستوجب إيقاف العمل لشهور لإعادة كتابة النظام من الصفر، وهو قرار متهور غالباً ما يقود لتعطيل الإيرادات وانهيار الشركات. وبالمقابل، فإن الاستسلام الكامل لضغوط الأعمال يراكم الديون حتى تتجمد سرعة الإنجاز ويغادر الكفاءات الفريق.
وينطلق القائد الحقيقي من الفلسفة الأصلية لوارد كانينغهام: الدَّين قد يكون أداة استثمارية مشروعة؛ فإطلاق نموذج أولي بمعمارية بسيطة لاختبار السوق قرار ذكي شريطة تسجيل هذا الدَّين وجدولته للسداد.
ولتحديد الأولويات موضوعياً، نستخدم مصفوفة مرجحة بالمخاطر تركز على المكونات التي يحرر إصلاحها قفزات ملموسة في إنتاجية الفريق وسلامة التشغيل، مثل تفكيك مسار شراء معقد يستهلك أربعين بالمئة من وقت الصيانة وتسبب في نزاعات العملاء.
ولإقناع الإدارة التنفيذية، نترجم المصطلحات التقنية إلى أرقام مالية وتجارية واضحة؛ فنستبدل عبارة 'إعادة هيكلة قاعدة البيانات' بـ 'تقليص وقت استجابة الشاشة من أربع ثوانٍ إلى ثانية واحدة لرفع معدل إتمام الشراء بنسبة ثلاثة بالمئة'.
وعلى الصعيد التشغيلي، نثبت قاعدة تخصيص خمس سعة الفريق دائماً لتحسين البنية التحتية، مع ترسيخ قاعدة الكشافة في المراجعات اليومية لضمان بقاء قاعدة الكود مرنة وجاهزة للتوسع المستمر."""
    }
}

# ==========================================
# LEAD-04: How do you estimate an unfamiliar feature and communicate risk?
# ==========================================
DATA["LEAD-04"] = {
    "concept_en": """Estimating unfamiliar technical features under high uncertainty requires converting unknowns into knowns through timeboxed discovery and probabilistic communication:
- The Cone of Uncertainty:
  - In initial project stages, estimates can be off by up to 400% due to unknown third-party SDK quirks, OS platform quirks, or ambiguous requirements.
  - Senior engineers never give a single static date for an unfamiliar feature; committing to a single date transforms an educated guess into an adversarial deadline.
- Systematic 4-Step Estimation Framework:
  1. Timeboxed Discovery Spike (1-2 Days):
     - Allocate a hard-capped timebox to build a throwaway proof-of-concept (POC) exploring the core technical unknowns (e.g., verifying a Bluetooth or CameraX API).
     - The goal of a spike is not production code, but risk burning and uncertainty reduction.
  2. Granular Task Decomposition:
     - Break the feature down into sub-components no larger than 1 to 2 days of work: API contract, local storage schema, UI state modeling, error states, and testing.
  3. Three-Point Estimating (PERT):
     - Estimate three scenarios: Optimistic ($O$), Most Likely ($M$), and Pessimistic ($P$).
     - Calculate expected duration: $E = \frac{O + 4M + P}{6}$ with standard deviation $\\sigma = \\frac{P - O}{6}$.
  4. Probabilistic Risk Communication:
     - Communicate estimates as confidence intervals tied to assumptions: \"With 80% confidence, this will ship in 3 to 4 weeks, assuming the vendor SDK supports our target Android 15 devices without major NDK bugs.\"
     - Provide milestone delivery gates (Milestone 1: Core integration, Milestone 2: Edge cases, Milestone 3: Hardening).""",
    "walkthrough_en": """Estimating and communicating risk using structured discovery milestones in Kotlin:
```kotlin
// Discovery Spike Architecture: Throwaway verification harness
class BleHardwareDiscoverySpike {
    suspend fun verifyBluetoothThroughput(): SpikeOutcome {
        val startTime = System.currentTimeMillis()
        return try {
            // Test 1: Verify whether hardware supports LE 2M PHY
            val isSupported = checkLe2MPhySupport()
            // Test 2: Measure transfer latency for 10KB payload
            val transferTimeMs = measurePayloadTransfer()

            SpikeOutcome.Success(
                isFeasible = isSupported && transferTimeMs < 500L,
                findings = "Hardware meets latency requirement; BLE connection takes 320ms avg."
            )
        } catch (e: Exception) {
            SpikeOutcome.RiskIdentified("Vendor firmware disconnects on Android 14: ${e.message}")
        }
    }
}

// Stakeholder Communication Script:
// "Because Bluetooth Low Energy integration has unknown firmware variations across vendors,
// we are running a 2-day discovery spike first.
// If the spike succeeds, we estimate delivery in 3 weeks (+/- 4 days).
// If we encounter firmware incompatibilities, we will trigger our fallback plan:
// utilizing our cloud-assisted QR code pairing flow."
```""",
    "short_en": """Estimate unfamiliar features by running a timeboxed 1 to 2-day discovery spike to eliminate unknowns, breaking work into small modular tasks, and calculating three-point PERT ranges. Communicate confidence intervals tied to explicit assumptions, establishing phased delivery milestones and fallback strategies instead of promising misleading single-point dates.""",
    "structured_en": """Estimating an unfamiliar technical feature requires disciplined risk management and transparent stakeholder communication.
In the early stages of unfamiliar development, the Cone of Uncertainty means premature estimates carry high variance. Committing to a single date under these conditions creates severe delivery risk.
A senior engineer begins by proposing a timeboxed discovery spike of one to two days. During this spike, an engineer writes a disposable proof-of-concept to validate core technical assumptions, such as hardware APIs or third-party SDK behavior.
Once the spike burns down the largest unknowns, we decompose the remaining work into small, self-contained tasks of one to two days each.
We apply three-point estimation, considering optimistic, most likely, and pessimistic scenarios to derive a probabilistic range.
Finally, we communicate with product managers and business stakeholders using confidence intervals tied to explicit assumptions, defining incremental milestones and pre-agreed fallback plans if external dependencies fail.""",
    "deep_senior_en": """From an engineering leadership, project risk governance, and executive alignment perspective, estimation is fundamentally an exercise in risk reduction and decision support rather than deadline prophecy.
The most frequent failure in technical delivery occurs when an engineer is pressured into giving a quick estimate in a meeting. Without empirical data, the engineer guesses two weeks; the business commits to marketing campaigns; unforeseen native crashes emerge; the feature slips by a month; and executive trust dissolves.
Senior leaders counteract this dynamic by reshaping the conversation around the Cone of Uncertainty. When faced with an unfamiliar domain—such as integrating a custom biometric SDK or migrating to Compose multi-platform—we declare the uncertainty openly and mandate a Discovery Spike. A two-day spike dedicated exclusively to proving the riskiest architectural assumption burns down eighty percent of unknown variance.
Following the spike, we decompose the scope into granular functional slices. We employ the Program Evaluation and Review Technique, estimating optimistic, realistic, and pessimistic bounds. This accounts for regression risks and testing overhead.
When presenting estimates to leadership, we speak in probabilistic ranges: \"We have ninety percent confidence in delivering the core workflow within three to four weeks, contingent on third-party API availability.\"
We structure the rollout into progressive delivery gates: a functional prototype, followed by edge-case hardening, followed by a dark-launched canary release. By pairing estimates with pre-negotiated contingency plans, we safeguard engineering credibility and ensure predictable delivery.""",
    "meta_ar": {
        "id": "LEAD-04",
        "questionAr": "كيف تقدر الجهد الزمني لميزة برمجية غير مألوفة وتتواصل بوضوح بشأن المخاطر المحيطة بها؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "إدارة عدم اليقين الهندسي (Cone of Uncertainty)، استخدام مهام الاستكشاف المحددة زمنياً (Timeboxed Spikes)، التقدير ثلاثي النقاط (PERT)، والتواصل الاحتمالي مع مديري المنتجات عبر فترات الثقة.",
        "concept_ar": "يتطلب تقدير الجهد الزمني لميزة تقنية غير مألوفة تحت وطأة عدم اليقين تحويل المجهول إلى معلوم عبر الاستكشاف المنضبط والتواصل الاحتمالي الشفاف: فوفقاً لمنحنى عدم اليقين (Cone of Uncertainty)، يمكن أن تخطئ التقديرات الأولية بنسبة تصل إلى 400%؛ وإعطاء موعد محدد اعتباطي يعد مخاطرة كارثية. ويعتمد القائد التقني على منهجية من 4 خطوات: أولاً، تخصيص مهمة استكشاف محددة زمنياً (Discovery Spike) لمدة يوم أو يومين لبناء نموذج أولي سريع (POC) لفحص المعضلات التقنية كحزم العتاد أو واجهات البلوتوث وحرق المخاطر؛ ثانياً، تفكيك الميزة إلى مهام صغيرة لا يتجاوز حجم الواحدة منها يومين عمل؛ ثالثاً، تطبيق التقدير ثلاثي النقاط (PERT) بحساب السيناريو المتفائل والمتوقع والمتشائم واستخراج المدى الزمني الحسابي؛ رابعاً، التواصل مع مديري المنتجات بلغة فترات الثقة الاحتمالية بدلاً من التواريخ الثابتة المضللة (مثل: 'بثقة 80% سنطلق الميزة بين 3 و4 أسابيع بشرط استقرار حزمة المورد') مع وضع مراحل تسليم واضحة وخطة بديلة.",
        "walkthrough_ar": """تصميم مهمة استكشاف وحساب المدى الاحتمالي للتقدير الزمني في كوتلن:
```kotlin
// مهمة استكشاف محددة زمنياً (2-Day Discovery Spike) لحرق المخاطر
class BleHardwareDiscoverySpike {
    suspend fun verifyBluetoothThroughput(): SpikeOutcome {
        val startTime = System.currentTimeMillis()
        return try {
            // فحص الفرضيات التقنية الحرجة على أرض الواقع
            val isSupported = checkLe2MPhySupport()
            val transferTimeMs = measurePayloadTransfer()

            SpikeOutcome.Success(
                isFeasible = isSupported && transferTimeMs < 500L,
                findings = "العتاد متوافق وزمن النقل 320ms وهو ضمن الحدود المقبولة"
            )
        } catch (e: Exception) {
            SpikeOutcome.RiskIdentified("حزمة المورد تنهار على أندرويد 14: ${e.message}")
        }
    }
}

// صيغة التواصل الاحترافي مع أصحاب القرار:
// "نظراً لأن دمج تقنية البلوتوث الجديدة يحمل مخاطر برمجية في استقرار العتاد،
// سنبدأ بمهمة استكشاف لمدة يومين لبناء نموذج تجريبي.
// إذا نجح النموذج، نقدر التسليم خلال 3 إلى 4 أسابيع بنسبة ثقة 80%.
// وفي حال تعثر توافق العتاد، سنفعل فوراً خطتنا البديلة باستخدام مسار الربط عبر QR Code."
```""",
        "why_it_matters_ar": "إعطاء مواعيد عشوائية متفائلة لميزات غير مألوفة يورط الفريق في تأخيرات متكررة ويدمر ثقة الإدارة ويجبر المطورين على ضغط عمل مدمر.",
        "worked_example_ar": "طلب مدير المنتج دمج قارئ مستندات بالذكاء الاصطناعي على الجهاز؛ بدلاً من إعطاء موعد فوري، نفذنا Spike ليومين واكتشفنا بطء المعالجة في الأجهزة الاقتصادية، فعدلنا الخطة لمعالجة المستندات في السحابة ووفرنا شهراً من التطوير الضائع.",
        "trade_offs_ar": "أخذ يومين للاستكشاف يبدو كأنه يعطل بدء التطوير؛ لكنه يحرق 80% من المخاطر ويمنع إعادة كتابة الكود بعد أسابيع من التخبط.",
        "failure_modes_ar": "أخطر الأخطاء هو الرضوخ لضغط الاجتماعات وإعطاء موعد قاطع في التو، أو تحويل مهمة الـ Spike إلى كود إنتاج دائم مليء بالثغرات.",
        "production_perspective_ar": "في الشركات التقنية الناضجة، لا تُقبل التقديرات الفردية الثابتة، بل تُقسم الميزة إلى مراحل تسليم واضحة (Milestones) مرتبطة بمؤشرات إنجاز قابلة للقياس.",
        "how_to_answer_ar": "ابدأ ببيان منحنى عدم اليقين ورفض المواعيد الفردية، واشرح دور Discovery Spike في حرق المخاطر، ثم وضح معادلة PERT، واختم بكيفية التواصل الاحتمالي مع الإدارة.",
        "talking_points_ar": "منحنى عدم اليقين Cone of Uncertainty، مهمة الاستكشاف Discovery Spike، التقدير ثلاثي النقاط PERT، فترات الثقة الاحتمالية، مراحل التسليم Milestones، والخطط البديلة Fallback.",
        "follow_ups_ar": "ماذا تفعل إذا ضغطت عليك الإدارة لإلغاء يومي الـ Spike والبدء فوراً في كتابة كود الإنتاج؟",
        "self_check_ar": "هل أكدت على رفض إعطاء تاريخ ثابت فوري، وشرحت مهمة الـ Spike، واستخدمت فترات الثقة الاحتمالية مع الفرضيات؟",
        "references_ar": f"- [Steve McConnell: Software Estimation - Demystifying the Black Art](https://www.stevemcconnell.com/) — المرجع العالمي الكلاسيكي لتقدير المشاريع البرمجية ومنحنى عدم اليقين.\n- [Agile Alliance: Spikes in Agile Software Development](https://www.agilealliance.org/glossary/spike/) — الدليل الإرشادي المعتمد لتنفيذ مهام الاستكشاف التقنية وإدارة المخاطر.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """نقدر الميزات غير المألوفة بتنفيذ مهمة استكشاف Discovery Spike ليوم أو يومين لحرق المخاطر وبناء نموذج تجريبي، وتفكيك العمل إلى مهام صغيرة وتطبيق التقدير ثلاثي النقاط PERT. ونتواصل مع الإدارة بفترات ثقة احتمالية مرتبطة بفرضيات واضحة بدلاً من تاريخ ثابت مضلل، مع تحديد مراحل تسليم تدريجية وخطة بديلة.""",
        "best_answer_ar": """يتطلب تقدير الميزات البرمجية غير المألوفة منهجية علمية منضبطة لإدارة المخاطر والتواصل الشفاف مع أصحاب القرار.
ينطلق المهندس الخبير من حقيقة منحنى عدم اليقين؛ فالتقدير المبكر دون بيانات يحمل نسبة خطأ هائلة، وإعطاء تاريخ عشوائي يحول التخمين إلى موعد ملزم يضر بمصداقية الفريق.
لذا تبدأ المنهجية باقتراح مهمة استكشافية محددة زمنياً لمدة يوم أو يومين، يقوم فيها المطور ببناء نموذج أولي سريع لفحص الفرضيات التقنية الحرجة مثل توافق مكتبات العتاد أو استهلاك الذاكرة.
وبعد حرق المخاطر الكبرى في مرحلة الاستكشاف، نقوم بتفكيك الميزة إلى مهام تفصيلية صغيرة لا تتجاوز يومين عمل لكل منها، ونطبق أسلوب التقدير ثلاثي النقاط لحساب المدى الزمني المتوقع.
وأخيراً، نتواصل مع مديري المنتجات بلغة فترات الثقة الاحتمالية؛ فنحدد موعداً بمدى زمني مشروط بفرضيات تقنية صريحة، مع وضع مراحل تسليم تدريجية وخطة بديلة واضحة في حال تعثر أي عنصر خارجي.""",
        "deep_answer_ar": """من منظور القيادة الهندسية وحوكمة مخاطر المشروعات في بيئات التطوير السريعة، يعد التقدير الزمني أداة لدعم اتخاذ القرار وتوزيع الموارد وليس تنبؤاً بالغيب.
الخطأ الأكثر شيوعاً في بيئات العمل هو رضوخ المطور لضغوط الإدارة في الاجتماعات بطلب رقم فوري، فيخمن أسبوعين بينما يمتلئ المسار بثغرات غير مرئية في حزم العتاد أو قيود النظام؛ فتنكسر المواعيد وتضيع الثقة بين فرق العمل.
ويتصدى القائد التقني لهذا الخلل بنقل الحوار إلى مربع الحقائق؛ فيشرح وجود فجوة معرفية تستوجب إجراء مهمة استكشافية مركزة. تخصص هذه المهمة ليومين فقط لبناء نموذج مصغر لا يكتب كوداً للإنتاج بل يثبت صحة الفرضيات ويحرق ثمانين بالمئة من مساحة عدم اليقين.
وعقب انتهاء الاستكشاف، نجزئ الميزة إلى مكونات معمارية دقيقة تشمل طبقة الشبكة، وقاعدة البيانات، وحالات الخطأ، وواجهات العرض. ونستخدم معادلة PERT الإحصائية للموازنة بين التفاؤل والتحوط للأخطاء البرمجية.
وعند عرض التقدير على الإدارة التنفيذية، نتحدث بلغة الاحتمالات المعتمدة في هندسة النظم: 'نمتلك ثقة بنسبة تسعين بالمئة في إنجاز المسار الرئيسي خلال ثلاثة إلى أربعة أسابيع بشرط استقرار خدمات الطرف الثالث'.
كما نقسم الإطلاق إلى محطات واضحة؛ تبدأ بإطلاق تجريبي صامت، يليه استيعاب الحالات الحافة، ثم الإطلاق الكامل، مما يحفظ مصداقية الفريق الهندسي ويوفر رؤية استراتيجية واضحة للشركة."""
    }
}

# ==========================================
# LEAD-05: How do you mentor junior developers and improve team engineering practice?
# ==========================================
DATA["LEAD-05"] = {
    "concept_en": """Elevating junior developers and scaling team engineering standards requires deliberate mentorship, psychological safety, graduated autonomy, and systemic knowledge codification:
- The Socratic Mentorship Model:
  - Junior engineers often ask: \"How do I solve X?\"
  - Ineffective mentors dictate code or grab the keyboard.
  - Senior mentors practice the Socratic method: asking guiding questions that stimulate first-principles thinking: \"What happens to this flow when the screen rotates?\" or \"Where does the single source of truth live in this screen?\"
- The Graduated Autonomy Framework:
  1. Pairing (High Guidance): Pair-programming on complex architectural modules, thinking aloud to demonstrate problem decomposition and debugging workflows.
  2. Scaffolding (Medium Guidance): Assigning features with pre-designed architecture interfaces, allowing the junior engineer to implement business logic and tests independently.
  3. Autonomy (Low Guidance): Handing over end-to-end feature ownership with post-hoc PR review and design alignment.
- Systemic Team Uplift Mechanisms:
  - Blameless Postmortems: Treating production incidents as learning opportunities to improve linters and architectural guards rather than assigning personal fault.
  - Engineering Brown Bags: Bi-weekly lightning talks where team members share lessons learned, new Jetpack libraries, or internal tooling improvements.
  - Codifying Tribal Knowledge: Transforming oral traditions into automated static analysis rules (Detekt custom rules, Android Lint checks) and living Architecture Decision Records (ADRs).""",
    "walkthrough_en": """Structured mentoring framework and custom architectural lint rule in Kotlin:
```kotlin
// Codifying Team Best Practices into an Automated Lint Rule
// Example: Banning GlobalScope across the team to prevent background coroutine leaks
class GlobalScopeDetector : Detector(), SourceCodeScanner {
    companion object {
        val ISSUE = Issue.create(
            id = "BannedGlobalScope",
            briefDescription = "Prohibit GlobalScope usage",
            explanation = "GlobalScope bypasses structured concurrency. Use viewModelScope or injected CoroutineScope.",
            category = Category.CORRECTNESS,
            priority = 8,
            severity = Severity.ERROR,
            implementation = Implementation(GlobalScopeDetector::class.java, Scope.JAVA_FILE_SCOPE)
        )
    }

    override fun getApplicableUastTypes() = listOf(UReferenceExpression::class.java)

    override fun createUastHandler(context: JavaContext) = object : UElementHandler() {
        override fun visitReferenceExpression(node: UReferenceExpression) {
            if (node.asRenderString() == "GlobalScope") {
                context.report(
                    ISSUE,
                    node,
                    context.getLocation(node),
                    "Violates team standard: Inject an ApplicationScope or use viewModelScope instead."
                )
            }
        }
    }
}
```""",
    "short_en": """Mentor junior developers using Socratic inquiry and graduated autonomy, progressing from pair programming to independent feature ownership. Elevate team practice systemically through blameless postmortems, engineering brown-bags, and codifying tribal standards into automated Lint rules and living Architecture Decision Records.""",
    "structured_en": """Mentoring junior developers and improving team engineering maturity requires balancing individualized coaching with systemic architectural guardrails.
Individual mentorship thrives on the Socratic method. Rather than prescribing code solutions, senior mentors ask guiding questions that prompt engineers to reason through state lifecycles and edge cases independently.
We guide developers through graduated autonomy: beginning with pair programming on intricate features, moving to scaffolded tasks with pre-defined interfaces, and culminating in full feature ownership.
To improve team practice systemically, we establish a culture of psychological safety through blameless postmortems, analyzing incidents to strengthen systems rather than assign fault.
We organize regular engineering sharing sessions to cross-pollinate knowledge.
Crucially, we codify tribal knowledge into automated tooling by writing custom Detekt and Android Lint rules and maintaining living Architecture Decision Records, ensuring high standards scale effortlessly across the team.""",
    "deep_senior_en": """From an organizational culture, engineering leadership, and talent enablement perspective, a senior engineer\'s ultimate impact is measured not by individual code output, but by the elevated capability and velocity of the team.
Effective mentorship begins with establishing psychological safety. Junior engineers must feel entirely secure admitting confusion, asking fundamental questions, and proposing alternative designs without fear of condescension.
When guiding a junior colleague, resist the temptation to dictate implementations or hijack their keyboard. Practice Socratic inquiry: ask \"What failure modes occur if the network times out during this transition?\" or \"How would we write a deterministic unit test for this repository?\" This trains engineers to think in terms of edge cases, lifecycle boundaries, and architectural trade-offs.
Adopt a model of graduated responsibility: start with collaborative pairing, transition to scaffolded features with defined domain boundaries, and eventually delegate end-to-end technical ownership of a feature epic.
Beyond 1-on-1 coaching, senior leaders scale engineering excellence across the entire engineering organization.
Establish blameless postmortems after production incidents, framing outages as systemic design flaws that require better linting, canary rollouts, or circuit breakers.
Host bi-weekly brown-bag sessions where engineers present deep-dives on topics like Kotlin compiler plugins or memory profiling.
Most importantly, institutionalize standards by automating them. Transform recurring code review feedback into custom Android Lint checks, Detekt rules, and CI assertions. When team standards are enforced by automated compilers rather than subjective human debates, code reviews remain uplifting, educational, and focused on high-level architecture.""",
    "meta_ar": {
        "id": "LEAD-05",
        "questionAr": "كيف تدرب وتوجه المطورين الجدد (Mentorship) وترتقي بالممارسات الهندسية داخل الفريق؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "أسلوب التوجيه السقراطي (Socratic Method)، التدرج في منح الاستقلالية (Graduated Autonomy)، بناء الأمان النفسي، ثقافة المراجعة بعد الحوادث دون لوم (Blameless Postmortems)، وأتمتة المعايير في Lint وADRs.",
        "concept_ar": "يتطلب تدريب وتوجيه المطورين الجدد (Mentorship) والارتقاء بالممارسات الهندسية للفريق الجمع بين التدريب الفردي الفعال وبناء ثقافة الأمان النفسي وأتمتة المعايير المؤسسية: يعتمد التدريب الراقي على الأسلوب السقراطي؛ فعوضاً عن إملاء الكود الجاهز، يطرح القائد التقني أسئلة توجيهية تدرب المطور على التفكير من القواعد الأساسية مثل 'ماذا يحدث لهذا الكود عند تدوير الشاشة؟'. ويتدرج المطور عبر إطار الاستقلالية؛ بدءاً من البرمجة الزوجية (Pair Programming) لتفكيك المشكلات المعقدة، ثم تسليم مهام محددة الواجهات، وصولاً للملكية الكاملة للميزات. وعلى مستوى الفريق، تُبنى ثقافة التعلم من خلال جلسات تحليل الحوادث دون لوم شخصي (Blameless Postmortems) لتحويل الأخطاء إلى تحسينات في النظام، وعقد جلسات معرفية دورية (Brown Bags) لتبادل الخبرات. والأهم هو تحويل المعرفة الضمنية إلى قواعد برمجية مؤتمتة عبر كتابة فحوصات Detekt وAndroid Lint مخصصة وسجلات القرارات المعمارية (ADRs) لضمان التزام الفريق بالمعايير دون صدامات شخصية.",
        "walkthrough_ar": """تحويل معايير الفريق الهندسية إلى قاعدة فحص آلي في Android Lint بكوتلن:
```kotlin
// أتمتة المعايير الهندسية: منع استخدام GlobalScope في كامل المشروع
class GlobalScopeDetector : Detector(), SourceCodeScanner {
    companion object {
        val ISSUE = Issue.create(
            id = "BannedGlobalScope",
            briefDescription = "يحظر استخدام GlobalScope نهائياً",
            explanation = "يتسبب GlobalScope في تسريب الذاكرة وكسر التزامن الهيكلي. استخدم viewModelScope أو نطاقاً محقوناً.",
            category = Category.CORRECTNESS,
            priority = 8,
            severity = Severity.ERROR,
            implementation = Implementation(GlobalScopeDetector::class.java, Scope.JAVA_FILE_SCOPE)
        )
    }

    override fun getApplicableUastTypes() = listOf(UReferenceExpression::class.java)

    override fun createUastHandler(context: JavaContext) = object : UElementHandler() {
        override fun visitReferenceExpression(node: UReferenceExpression) {
            if (node.asRenderString() == "GlobalScope") {
                context.report(
                    ISSUE,
                    node,
                    context.getLocation(node),
                    "مخالفة لمعايير الفريق الهندسية: يرجى حقن ApplicationScope مخصص بدلاً من GlobalScope."
                )
            }
        }
    }
}
```""",
        "why_it_matters_ar": "غياب التوجيه يجعل المطورين الجدد يكررون أخطاء كارثية في الإنتاج، ويخلق بيئة محبطة تزيد من دوران الكفاءات وتدهور جودة البرمجيات.",
        "worked_example_ar": "بدلاً من حل مشكلة كراش للمطور الجديد بنفسي، وجهته عبر أسئلة حول دورة حياة الكوروتين؛ فاكتشف بنفسه سبب تسريب الذاكرة وكتب اختبار وحدة يؤكد حله بنجاح.",
        "trade_offs_ar": "التوجيه وطرح الأسئلة يستغرق وقتاً أطول من كتابة الحل مباشرة؛ لكنه يستثمر في بناء مهندس مستقل يرفع إنتاجية الفريق لعشرات الأضعاف لاحقاً.",
        "failure_modes_ar": "أخطر الأخطاء هو سحب لوحة المفاتيح وكتابة الكود بدلاً من المطور، أو السخرية من الأسئلة البديهية وتدمير الأمان النفسي للمبتدئين.",
        "production_perspective_ar": "في الشركات الكبرى، يُقاس أثر المهندس Senior بمدى نمو زملائه وترقيتهم، وليس فقط بعدد أسطر الكود أو الـ PRs المنجزة فردياً.",
        "how_to_answer_ar": "ابدأ ببيان أن أثر الـ Senior يقاس بنمو فريقه، واشرح أسلوب الأسئلة السقراطية، ثم بين مراحل الاستقلالية المتدرجة، واختم بتحليل الحوادث دون لوم وأتمتة المعايير في Lint.",
        "talking_points_ar": "الأسلوب السقراطي Socratic Method، الأمان النفسي Psychological Safety، الاستقلالية المتدرجة Graduated Autonomy، جلسات التحليل دون لوم Blameless Postmortems، وأتمتة المعايير بـ Lint.",
        "follow_ups_ar": "كيف تتعامل مع مطور جديد يكرر نفس الأخطاء المعمارية باستمرار رغم التوجيه المتكرر في مراجعات الكود؟",
        "self_check_ar": "هل ركزت على طرح الأسئلة بدلاً من إعطاء الحلول، ووضحت التدرج في منح المسؤولية، وأكدت على أتمتة المعايير في أدوات الفحص؟",
        "references_ar": f"- [Camille Fournier: The Manager's Path - A Guide for Tech Leaders](https://www.oreilly.com/library/view/the-managers-path/9781491973882/) — المرجع القيادي الشامل لبناء وتوجيه الفرق الهندسية وتطوير المهارات البرمجية.\n- [Google re:Work: Guide - Understand team effectiveness and Psychological Safety](https://rework.withgoogle.com/) — دراسة جوجل التاريخية حول أهمية الأمان النفسي في نجاح وتميز الفرق البرمجية.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """نوجه المطورين الجدد بالأسلوب السقراطي بطرح أسئلة محفزة للتفكير بدلاً من إملاء الحلول الجاهزة، والتدرج في منح الاستقلالية من البرمجة الزوجية إلى تسليم المهام الكاملة. ونرتقي بالممارسات الهندسية عبر ترسيخ الأمان النفسي في جلسات تحليل الحوادث دون لوم، وعقد لقاءات معرفية دورية، وأتمتة المعايير في فحوصات Lint وسجلات ADRs.""",
        "best_answer_ar": """يرتكز توجيه المطورين الجدد والارتقاء بالممارسات الهندسية للفريق على موازنة التدريب الفردي الملهم مع ترسيخ معايير برمجية مؤسسية مستدامة.
ينطلق التوجيه الفردي من الأسلوب السقراطي؛ فعندما يسأل المطور عن حل مشكلة، لا نسحب لوحة المفاتيح لكتابة الكود بدلاً منه، بل نطرح أسئلة توجيهية تدربه على التفكير في الحالات الحافة ودورات الحياة وكيفية كتابة اختبارات سلوكية مستقلة.
ونمنح المطور استقلالية متدرجة؛ تبدأ بالبرمجة الزوجية في الميزات المعقدة لمشاهدة كيفية تفكيك المشكلات وتتبع الأخطاء، ثم تسليمه مهام ذات واجهات محددة مسبقاً، وصولاً لإسناد الملكية الهندسية الكاملة للميزات.
وعلى صعيد الفريق، نبني بيئة تسودها الثقة والأمان النفسي من خلال مراجعات الحوادث دون لوم شخصي؛ حيث نركز على تحسين المنظومة وسد الثغرات.
كما نحرص على تحويل المعايير الشفهية إلى أدوات آلية عبر كتابة قواعد Lint مخصصة وسجلات قرارات معمارية تضمن الحفاظ على الجودة تلقائياً.""",
        "deep_answer_ar": """من منظور القيادة الهندسية وتنمية الكفاءات التقنية، يُقاس الأثر الحقيقي للمهندس القائد بمدى ارتفاع كفاءة الفريق ونضجه المعماري وليس بحجم إنجازه الفردي المنعزل.
تبدأ القيادة الفعالة بتأسيس بيئة عمل قائمة على الأمان النفسي؛ حيث يشعر المطور المبتدئ بالاطمئنان التام لطرح الأسئلة الاستكشافية والاعتراف بعدم المعرفة دون خوف من الاستنقاص.
وعند توجيه المطورين، نتجنب فرض الإجابات القاطعة؛ بل نعتمد على التحفيز السقراطي الذي يقود المهندس لاكتشاف عيوب التصميم بنفسه، كأن نسأله: 'ماذا سيحدث لموارد الهاتف إذا دخل هذا الطلب في حلقة مفرغة أثناء انقطاع الشبكة؟'.
ونعتمد إطار الاستقلالية المتدرجة؛ فنتشارك البرمجة الزوجية أولاً لشرح آليات تقسيم المشكلات الكبرى، ثم نمنحه مهاماً ذات حدود معمارية مؤطرة، حتى يصل لمرحلة قيادة الميزة بمفرده من التصميم حتى الإطلاق.
وعلى مستوى ثقافة الفريق، نحول الأخطاء البرمجية إلى مكاسب معرفية جماعية؛ فعند وقوع أي عطل في الإنتاج، نعقد جلسة مراجعة خالية تماماً من اللوم الشخصي، ونبحث في الأسباب الجذرية التي سمحت بمرور الخطأ.
والخطوة الأكثر نضجاً هي أتمتة هذه الدروس؛ فنحول الأخطاء المتكررة إلى قواعد فحص آلي في Android Lint وDetekt، ونوثق التوجهات في سجلات القرارات المعمارية ADRs. وبذلك تصبح المعايير الهندسية جزءاً أصيلاً من بيئة التطوير، مما يتيح للفريق التوسع بكفاءة واحترافية عالية."""
    }
}

# ==========================================
# LEAD-06: How do you write an RFC/ADR for a major architecture change?
# ==========================================
DATA["LEAD-06"] = {
    "concept_en": """Governing large-scale technical evolutions through Requests for Comments (RFCs) and Architecture Decision Records (ADRs) ensures asynchronous alignment, structured evaluation, and durable institutional memory:
- RFC vs ADR Distinction:
  - Request for Comments (RFC): A collaborative, exploratory document used *before* a decision is finalized to solicit feedback, explore alternatives, align cross-functional teams, and establish consensus.
  - Architecture Decision Record (ADR): An immutable, version-controlled document capturing a *finalized* architectural choice, recording the context, decision, consequences, and compliance requirements for future engineers.
- Anatomy of a Production-Grade RFC:
  1. Summary & Problem Statement: Clear, jargon-free explanation of the architectural bottleneck and business impact.
  2. Goals vs Non-Goals: Explicit boundary setting to prevent scope creep (e.g., \"Goal: Migrate network layer to Ktor; Non-Goal: Rewrite the UI in Compose\").
  3. Proposed Architecture & System Design: Class diagrams, data flow models, and concrete Kotlin API contracts.
  4. Alternatives Considered & Rejected: Objective analysis of competing options and explicit rationale for why they were dismissed.
  5. Migration, Rollout, and Rollback Plan: Phased rollout steps, feature-flag mechanics, deprecation schedules, and backout triggers.
  6. Security, Privacy, and Performance Impact: Metrics, memory implications, cold-start latency, and battery impact.
- The Michael Nygard ADR Schema:
  - Context -> Decision -> Status (Proposed, Accepted, Deprecated, Superseded) -> Consequences (Positive, Negative, Neutral).""",
    "walkthrough_en": """Standard Architecture Decision Record (ADR) template in Markdown:
```markdown
# ADR-007: Migration from Legacy XML View System to Jetpack Compose

## Status
Accepted (Date: 2026-10-17)

## Context
Our Android application currently uses a mixed View-binding and Data-binding XML architecture.
Fragment rendering benchmarks show high view-inflation latencies (averaging 42ms on budget devices).
Furthermore, maintaining duplicate UI state between custom views and ViewModels has caused 28% of our UI state synchronization bugs over the past two quarters.
Google has transitioned modern Android UI development to Jetpack Compose.

## Decision
We will adopt Jetpack Compose for all new feature development and migrate existing high-churn screens opportunistically during planned redesigns.
We strictly prohibit writing new XML layout files starting with Sprint 42.

## Consequences
### Positive
- Declarative unidirectional data flow directly consuming ViewModel StateFlow.
- Measured 35% reduction in UI boilerplate code.
- Eliminates fragment view-inflation overhead, reducing screen transition jank.

### Negative / Accepted Trade-offs
- Cold startup time increases slightly (~80ms) due to Compose runtime classloading; mitigated via Baseline Profiles.
- Team learning curve requires 3 internal training brown bags on recomposition optimization.

## Reversal / Exit Criteria
If Compose runtime regressions cause crash-free sessions to dip below 99.8% on low-end Android Go hardware and cannot be resolved within 30 days, new screen migration will pause and fall back to classic Views.
```""",
    "short_en": """Write an RFC before a decision to build consensus by defining goals, non-goals, proposed designs, rejected alternatives, and rollback plans. Once agreed, capture the outcome in an immutable ADR detailing context, status, consequences, and accepted trade-offs, preserving institutional memory in Git.""",
    "structured_en": """Driving major architectural changes successfully requires structured technical documentation through RFCs and ADRs.
An RFC, or Request for Comments, is authored before a decision is finalized. It frames the problem statement, defines explicit goals and non-goals to prevent scope creep, presents the proposed architecture with concrete Kotlin contracts, and thoroughly evaluates rejected alternatives. Crucially, it outlines a phased migration and rollback plan.
Once the engineering team reaches consensus, the decision is immortalized as an Architecture Decision Record, or ADR.
Following the Nygard template, an ADR is an immutable document committed to Git. It records the organizational context, the decision taken, its current status, and both positive and negative consequences.
This disciplined workflow transforms subjective architectural debates into collaborative engineering reviews while ensuring that future team members understand the mechanical rationale and trade-offs behind foundational decisions.""",
    "deep_senior_en": """From an engineering governance, distributed organization scaling, and technical strategy perspective, RFCs and ADRs are essential instruments for establishing architectural velocity and institutional memory.
In growing engineering teams, architectural decisions made in informal chats or private meetings create organizational misalignment, duplicate efforts, and toxic debates when new engineers join and wonder why a legacy choice was made. Senior leaders eliminate this dysfunction by institutionalizing asynchronous decision-making.
The process begins with an RFC. A well-crafted RFC is rigorous and concise. It leads with a sharp problem statement and draws strict boundaries via Goals and Non-Goals.
It provides comprehensive architectural diagrams and illustrative Kotlin code snippets, allowing reviewers to evaluate the ergonomic developer experience.
A vital section is Alternatives Considered: if you propose adopting Ktor, you must document why Retrofit, OkHttp, and gRPC were evaluated and rejected. The RFC must specify the migration strategy, demonstrating how the system will transition incrementally without breaking production releases, supported by feature flags and automated metric alarms.
Once the RFC review window concludes and stakeholders align, the outcome is recorded as an Architecture Decision Record in the repository docs/adr directory.
Using the classic Nygard structure, the ADR captures the immutable snapshot: context, decision, and balanced consequences, explicitly recording accepted liabilities such as build time penalties or training curves. This documentation serves as a permanent architectural lighthouse, preventing circular re-litigation of settled engineering choices.""",
    "meta_ar": {
        "id": "LEAD-06",
        "questionAr": "كيف تكتب وثيقة طلب التعليقات (RFC) أو سجل القرارات المعمارية (ADR) لتغيير معماري كبير؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "التوثيق المعماري والحوكمة التقنية، الفرق بين وثيقة الاستطلاع (RFC) وسجل القرار (ADR)، هيكل وثيقة RFC (الأهداف، ما يخرج عن النطاق، البدائل المرفوضة، وخطة التراجع)، وقالب نيجارد لـ ADRs.",
        "concept_ar": "يمثل استخدام وثائق طلب التعليقات (RFC) وسجلات القرارات المعمارية (ADR) الركيزة الأساسية للحوكمة التقنية واتخاذ القرارات المعمارية الكبرى وتوثيق الذاكرة المؤسسية للمشاريع: يكمن الفارق الجوهري في أن وثيقة RFC تُكتب *قبل* اتخاذ القرار لاستطلاع آراء الفرق، واستعراض البدائل، وبناء التوافق؛ بينما يُكتب سجل ADR *بعد* حسم القرار لتوثيقه بشكل دائم ومحدد داخل مستودع Git. وتتكون وثيقة الـ RFC الاحترافية من 6 عناصر أساسية: أولاً، توصيف المشكلة وسياقها التجاري؛ ثانياً، تحديد الأهداف وما يخرج عن النطاق (Non-Goals) لمنع تشتت المشروع؛ ثالثاً، التصميم المعماري المقترح ونماذج الكود؛ رابعاً، البدائل التي دُرست ورُفضت وأسباب رفضها؛ خامساً، خطة الهجرة التدريجية وآلية التراجع (Rollback Plan)؛ سادساً، الأثر على الأمان والأداء. أما الـ ADR فيتبع قالب مايكل نيجارد المعتمد: (السياق، القرار، الحالة، والتبعات الإيجابية والسلبية المقبولة)، مما يحمي الفريق من تكرار الجدال حول قرارات حُسمت مسبقاً.",
        "walkthrough_ar": """قالب سجل القرارات المعمارية (ADR) القياسي المعتمد لمشروع أندرويد بصيغة Markdown:
```markdown
# ADR-007: الانتقال من واجهات XML القديمة إلى Jetpack Compose

## الحالة (Status)
مقبول ومعتمد (Accepted - بتاريخ 17 أكتوبر 2026)

## السياق (Context)
يعتمد تطبيقنا حالياً على نظام واجهات XML مع Data-Binding وView-Binding؛
وتظهر مقاييس الأداء بطئاً في تضخيم الواجهات (متوسط 42ms على الهواتف الاقتصادية)،
كما تسببت ازدواجية إدارة الحالة بين الشاشات والـ ViewModel في 28% من أخطاء التزامن في الربعين الأخيرين.
وقد أعلنت جوجل اعتماد Compose كمعيار رسمي وحيد لمستقبل واجهات أندرويد.

## القرار (Decision)
سنعتمد Jetpack Compose حصرياً لبناء كافة الشاشات والميزات الجديدة،
مع تحويل الشاشات القديمة ذات التعديلات المستمرة تدريجياً أثناء دورات إعادة التصميم.
ويُحظر تماماً إنشاء أي ملفات XML جديدة بدءاً من دورة التطوير القادمة.

## التبعات (Consequences)
### التبعات الإيجابية (Positive)
- تدفق أحادي للبيانات يرتبط مباشرة بـ StateFlow في الـ ViewModel.
- انخفاض الشيفرة البرمجية المكررة للواجهات بنسبة 35%.
- القضاء على تهنيج الشاشات الناتج عن معالجة ملفات الـ XML.

### التبعات المقبولة والمحسوبة (Accepted Trade-offs)
- زيادة طفيفة في زمن الإقلاع الأولي للنسخة الباردة (~80ms) عولجت بتوليد Baseline Profiles.
- تخصيص 3 ورش عمل تقنية لتأهيل أعضاء الفريق على تحسين إعادة التركيب Recomposition.

## شروط التراجع (Reversal Criteria)
إذا تسبب الانتقال لـ Compose في هبوط معدل الجلسات الخالية من الكراشات عن 99.8% في أجهزة Android Go دون حل خلال 30 يوماً، سنوقف الهجرة فوراً ونعود لاستخدام Views التقليدية.
```""",
        "why_it_matters_ar": "القرارات المعمارية الشفهية تؤدي لفقدان الذاكرة المؤسسية وتكرار الجدال العقيم كلما انضم مهندس جديد وضياع الأسباب التي بنيت عليها القرارات.",
        "worked_example_ar": "أراد مهندس تغيير مكتبة الشبكة إلى Ktor؛ كتب RFC تضمن مقارنة بالأرقام مع Retrofit وخطة هجرة تدريجية عبر Feature Flags، مما نال موافقة سريعة من كافة الفرق دون خلافات.",
        "trade_offs_ar": "كتابة الـ RFC ومراجعته تستغرق عدة أيام قبل بدء البرمجة؛ لكنها تمنع كوارث التراجع المعماري بعد كتابة آلاف الأسطر في الاتجاه الخاطئ.",
        "failure_modes_ar": "أخطر الأخطاء هو اتخاذ قرارات كبرى في محادثات فردية، أو كتابة RFC دون تحديد ما يخرج عن النطاق Non-Goals مما يحول المشروع لمتاهة لا تنتهي.",
        "production_perspective_ar": "في الشركات التقنية العالمية، يُحفظ مجلد docs/adr في مستودع المشروع الرئيسي وتخضع ملفاته لنفس مراجعة الـ PR الصارمة قبل اعتمادها.",
        "how_to_answer_ar": "فرّق بوضوح بين RFC للاستطلاع والمناقشة وADR لتوثيق القرار النهائي، ثم اشرح بنية الـ RFC (الأهداف، البدائل المرفوضة، خطة التراجع)، واعرض قالب ADR المعتمد.",
        "talking_points_ar": "وثائق RFC الاستطلاعية، سجلات القرارات المعمارية ADRs، الذاكرة المؤسسية، ما يخرج عن النطاق Non-Goals، البدائل المرفوضة، وخطة التراجع Rollback.",
        "follow_ups_ar": "كيف تدير عملية مراجعة الـ RFC وتتخذ القرار النهائي إذا انقسم الفريق التقني بنسبة متساوية بين مؤيد ومعارض؟",
        "self_check_ar": "هل ميزت بين RFC وADR، وذكرت بند ما يخرج عن النطاق والبدائل المرفوضة، وشرحت قالب نيجارد والتبعات المقبولة؟",
        "references_ar": f"- [Michael Nygard: Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) — المقال التأسيسي الأصلي الذي ابتكر قالب سجلات القرارات المعمارية ADRs.\n- [IETF: Guidelines for Writing RFCs](https://www.ietf.org/) — التقاليد الهندسية العالمية لكتابة وثائق طلب التعليقات وتنسيق التوافق التقني.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """نكتب وثيقة RFC قبل اتخاذ القرار لبناء التوافق واستطلاع الآراء، موضحين فيها المشكلة والأهداف وما يخرج عن النطاق والبدائل المرفوضة وخطة التراجع. وبمجرد حسم القرار وتوافق الفريق، نوثق النتيجة في سجل ADR دائم في Git يتبع قالب نيجارد، موضحين السياق والقرار المتخذ وتبعاته الإيجابية والسلبية لحفظ الذاكرة المؤسسية.""",
        "best_answer_ar": """تمثل الحوكمة التقنية عبر وثائق RFC وسجلات ADRs الركيزة الأساسية لإدارة التغييرات المعمارية الكبرى وضمان الشفافية والذاكرة المؤسسية.
يبرز الفارق الجوهري في التوقيت والهدف؛ فوثيقة RFC هي مستند استطلاعي يُكتب قبل حسم القرار لدراسة البدائل ومناقشة التحديات وبناء التوافق عبر الفرق الهندسية.
وتتضمن الـ RFC الفعالة أهدافاً واضحة وما يخرج عن النطاق لتفادي تشتت المشروع، مع تقديم تصاميم برمجية دقيقة وتحليل البدائل المرفوضة بأسباب مقنعة، مع وضع خطة هجرة تدريجية ومسار تراجع واضح عند الطوارئ.
وعند الوصول للاتفاق، يُخلد القرار في سجل قرارات معمارية ADR غير قابل للتعديل داخل مستودع المشروع.
ويتبع الـ ADR قالب نيجارد الكلاسيكي الذي يسجل سياق القرار، والقرار المتخذ، وحالته، والتبعات المحاسبية والمقايضات المقبولة، مما يحمي الفريق من إعادة فتح نقاشات محسومة ويوضح للمهندسين الجدد أسباب بناء المعمارية بهذا الشكل.""",
        "deep_answer_ar": """من منظور الحوكمة الهندسية وتطوير المؤسسات البرمجية الموسعة، تشكل وثائق الاستطلاع RFCs وسجلات القرارات المعمارية ADRs أدوات لا غنى عنها لبناء توافق هادئ وتأصيل الذاكرة الهندسية المستدامة.
في الفرق البرمجية المتنامية، يؤدي اتخاذ القرارات المعمارية في محادثات جانبية عابرة إلى فوضى مؤسسية؛ حيث يتساءل المطورون الجدد عن مبررات اختيار نمط معين، ويعاد فتح الجدال ذاته دورياً وتضيع ساعات العمل في نقاشات دائرية عقيمة.
والقائد التقني يقضي على هذه العشوائية عبر مأسسة التوثيق غير المتزامن. تبدأ العملية بـ RFC رصين ينطلق من توصيف دقيق للمشكلة وعائدها الاستثماري، ويرسم حدوداً صارمة لما يخرج عن النطاق لمنع تضخم المتطلبات.
يقدم المستند نماذج بصرية ومخططات كوتلن واقعية تمكن المراجعين من تقييم التجربة البرمجية بوضوح. ومن الأبواب الحاسمة باب 'البدائل التي رُفضت'؛ فإذا اقترحت استبدال معمارية معينة، يجب توثيق أسباب استبعاد الخيارات الأخرى بنزاهة رقمية، مع وضع استراتيجية هجرة تدريجية تحمي الإنتاج عبر مفاتيح الميزات وقواطع الأعطال.
وعند اعتماد الوثيقة، يُثبت القرار في مستند ADR دائم في مسار docs داخل Git، مسجلاً السياق والقرار والتبعات المتوازنة، بما فيها الأثمان البرمجية المقبولة كزيادة زمن البناء أو التدريب.
هذا التوثيق المؤسسي الصارم يشكل منارة هندسية واضحة تمنع الجدال المتكرر وتضمن استمرار واستقرار البناء المعماري لعقود."""
    }
}

# ==========================================
# LEAD-07: How do you align mobile, backend, QA, and security teams on an API contract?
# ==========================================
DATA["LEAD-07"] = {
    "concept_en": """Aligning cross-functional engineering teams on robust API contracts requires schema-first design, consumer-driven contract testing, and cross-discipline governance:
- The Anti-Pattern of Backend-First Dictation:
  - Backend teams independently build database-centric endpoints and throw JSON documentation over the wall.
  - Mobile apps suffer from over-fetching, N+1 query waterfalls, battery drain, and sluggish rendering.
  - QA lacks mocks, while Security discovers unauthenticated endpoints days before release.
- The Schema-First Collaborative Lifecycle:
  1. Collaborative Contract Workshop:
     - Convene Mobile, Backend, QA, and Security engineers before writing a single line of implementation code.
     - Mobile advocates for screen-oriented, payload-sparse responses (or Backend-For-Frontend / BFF patterns) to conserve cellular data and battery.
     - Backend evaluates database indexing, pagination strategy (keyset/cursor vs offset), and caching headers (`ETag`, `Cache-Control`).
     - Security validates authentication scopes, OAuth2 PKCE flows, rate limiting, and zero cleartext PII.
     - QA validates testability, defining mock data generators and edge-case status codes.
  2. Single Source of Truth Specification:
     - The contract is committed as an OpenAPI (OAS 3.1) or Protocol Buffers (`.proto`) schema in a shared Git repository.
     - Client and server code generation tools auto-generate Kotlin data classes and Retrofit interfaces directly from the schema.
  3. Consumer-Driven Contract Testing (Pact):
     - CI builds enforce contract parity: backend PRs cannot merge if they introduce breaking schema changes that violate client contracts.""",
    "walkthrough_en": """Collaborative API Contract specification and Consumer-Driven Contract verification in Kotlin:
```kotlin
// Consumer-Driven Contract Test using Pact in Kotlin
class CheckoutApiContractTest {

    @Rule
    @JvmField
    val provider: PactProviderRule = PactProviderRule("CheckoutBackendService", this)

    @Pact(consumer = "AndroidMobileApp")
    fun createCheckoutPact(builder: PactDslWithProvider): RequestResponsePact {
        return builder
            .given("cart with id 1234 exists")
            .uponReceiving("a request to retrieve checkout summary")
            .path("/v1/checkout/1234")
            .method("GET")
            .willRespondWith()
            .status(200)
            .headers(mapOf("Content-Type" to "application/json"))
            // Pact verifies required schema shape: prevents backend from dropping mandatory fields
            .body(
                Dsl.newJsonObject()
                    .stringType("orderId", "ORD-998877")
                    .numberType("totalAmountCents", 5000L)
                    .stringMatcher("currency", "^[A-Z]{3}$", "USD")
                    .array("items")
                        .stringValue("Item name")
                    .closeArray()
                    .asBody()
            )
            .toPact()
    }
}
```""",
    "short_en": """Align cross-functional teams using a schema-first approach with OpenAPI or Protocol Buffers before writing code. Convene mobile, backend, QA, and security in contract design workshops to balance mobile payload efficiency with server performance, enforcing consumer-driven contract tests in CI pipelines to prevent breaking schema regressions.""",
    "structured_en": """Aligning mobile, backend, QA, and security teams on an API contract requires a collaborative, schema-first engineering process.
The primary failure mode in organizations is backend-driven API design, where servers expose database schemas without considering mobile constraints.
We solve this by establishing a contract-first lifecycle. Before implementation begins, leads from each discipline gather in a contract design workshop.
Mobile engineers advocate for compact, screen-oriented payloads and cursor pagination to minimize cellular radio activation. Backend engineers ensure database query feasibility and caching headers.
Security verifies authentication schemes, OAuth token scopes, and input sanitization, while QA defines synthetic edge cases and mock servers.
The agreed contract is codified as an OpenAPI or Protobuf schema in a central repository, auto-generating client models.
Finally, we integrate Consumer-Driven Contract Testing using tools like Pact into our CI pipelines, ensuring that backend changes never merge if they break client contracts.""",
    "deep_senior_en": """From an enterprise system integration, cross-functional engineering governance, and organizational topology perspective, API contracts represent the operational binding treaty between sovereign engineering teams.
When API definitions are treated as an afterthought, organizational friction explodes: mobile teams block on delayed backend endpoints, QA spends weeks writing manual stubs, and breaking changes slip into production, resulting in immediate mobile client crashes.
Senior leaders counteract this dysfunction through three core governance pillars: Schema-First Design, Contract Collaboration Workshops, and Consumer-Driven Verification.
The process begins with an OpenAPI 3.1 or Protocol Buffers specification authored in a dedicated contracts repository.
During the cross-functional workshop, mobile leads advocate for client performance: demanding Backend-For-Frontend (BFF) patterns or sparse fields to avoid transferring megabytes of JSON over spotty 4G connections.
Backend teams negotiate efficient cursor-based pagination to protect database clusters from expensive offset queries.
Security leads verify PCI and GDPR compliance, ensuring that sensitive PAN and PII are excluded from URL parameters and that request bodies enforce cryptographic signatures.
QA engineers leverage the schema immediately, spinning up Prism or WireMock servers to begin writing automated espresso tests on day one.
To guarantee enduring compatibility, we deploy Consumer-Driven Contract Testing via Pact into our continuous integration pipelines. Whenever a backend engineer opens a pull request, the CI runner validates the proposed changes against published mobile consumer pacts. If a field is renamed or its type changes from integer to string, the build fails automatically. This automated contract verification eliminates breaking changes and enables parallel team velocity across distributed organizations.""",
    "meta_ar": {
        "id": "LEAD-07",
        "questionAr": "كيف تنسق وتوحد الرؤى بين فرق تطبيقات الهاتف، والواجهات الخلفية، والجودة، والأمان حول عقود واجهات البرمجة (API Contracts)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "منهجية التصميم المعتمد على العقود أولاً (Schema-First Design)، ورش عمل التوافق المشترك بين الفرق، نمط BFF وحماية استهلاك باقة وبطارية الهاتف، واختبارات العقود الآلية في CI عبر Pact.",
        "concept_ar": "يتطلب توحيد الرؤى وتنسيق التعاون بين فرق تطبيقات الهاتف والواجهات الخلفية والجودة والأمان حول عقود واجهات البرمجة (API Contracts) اعتماد منهجية 'العقد أولاً' (Schema-First Design) واختبارات العقود المؤتمتة: يكمن الخلل الشائع في قيام فريق الـ Backend ببناء الواجهة من منظور قاعدة البيانات وفرضها على التطبيق، مما ينتج عنه حزم بيانات ضخمة (Over-fetching) تستنزف بطارية وباقة المستخدم. والحل القيادي يعتمد على 3 ركائز: أولاً، ورشة عمل مشتركة قبل كتابة أي كود؛ حيث يدافع فريق الهاتف عن كفاءة الشاشات وتصغير الحزم وتفضيل نمط Backend-For-Frontend (BFF) والترقيم بالمؤشرات (Cursor Pagination)، ويفحص فريق الأمان بروتوكولات التشفير والـ Scopes وحظر الـ PII، ويحدد فريق الـ QA نماذج المحاكاة وحالات الخطأ؛ ثانياً، اعتماد وثيقة OpenAPI أو Protobuf كمصدر وحيد للحقيقة في مستودع مشترك تُولد منه نماذج كوتلن تلقائياً؛ ثالثاً، تفعيل اختبارات العقود التي يقودها العميل (Consumer-Driven Contract Testing) عبر أدوات مثل Pact في خطوط الـ CI؛ بحيث يفشل دمج أي كود في الخادم إذا تضمن تغييراً يكسر توافق تطبيق الهاتف.",
        "walkthrough_ar": """تصميم اختبار عقود موجه من العميل (Consumer-Driven Contract) بأداة Pact في كوتلن:
```kotlin
// اختبار العقد البرمجي لتطبيق أندرويد لضمان عدم كسر الخادم للواجهة
class CheckoutApiContractTest {

    @Rule
    @JvmField
    val provider: PactProviderRule = PactProviderRule("خدمة_الواجهة_الخلفية", this)

    @Pact(consumer = "تطبيق_أندرويد")
    fun createCheckoutPact(builder: PactDslWithProvider): RequestResponsePact {
        return builder
            .given("السلة رقم 1234 موجودة بالفعل")
            .uponReceiving("طلب استرجاع ملخص الدفع")
            .path("/v1/checkout/1234")
            .method("GET")
            .willRespondWith()
            .status(200)
            .headers(mapOf("Content-Type" to "application/json"))
            // يفرض العقد وجود الحقول بالصيغ المحددة ويمنع الخادم من حذفها
            .body(
                Dsl.newJsonObject()
                    .stringType("orderId", "ORD-998877")
                    .numberType("totalAmountCents", 5000L)
                    .stringMatcher("currency", "^[A-Z]{3}$", "USD")
                    .array("items")
                        .stringValue("اسم المنتج")
                    .closeArray()
                    .asBody()
            )
            .toPact()
    }
}
```""",
        "why_it_matters_ar": "الخلافات حول الـ API تسبب تعطل المطورين لأسابيع وتفاجئ الفرق بتغييرات تكسر التطبيق في الإنتاج وتتسبب في انهيار التطبيق لدى المستخدمين.",
        "worked_example_ar": "قام فريق الـ Backend بتغيير اسم حقل user_id إلى id مما كاد يسقط التطبيق؛ أوقف اختبار Pact في خط الـ CI عملية الدمج تلقائياً وأجبر الخادم على دعم الاسمين لحين تحديث التطبيق.",
        "trade_offs_ar": "تنسيق العقود مسبقاً وتطبيق اختبارات Pact يتطلب يومين في بداية المشروع؛ لكنه يوفر شهوراً من التخبط ويسمح للفرق بالعمل المتوازي دون انتظار.",
        "failure_modes_ar": "أخطر الأخطاء هو بدء كتابة الكود قبل الاتفاق على العقد، أو إرسال تعديلات كاسرة (Breaking Changes) في الـ API دون دعم الإصدارات القديمة من التطبيق.",
        "production_perspective_ar": "في الشركات الكبرى، يُمنع فريق الخوادم من حذف أي حقل قديم من الـ API إلا بعد مرور عام كامل على تحديث التطبيق ومراقبة نسبة المستخدمين القدامى.",
        "how_to_answer_ar": "ابدأ برفض أسلوب فرض الـ API من الخادم، واشرح منهجية Schema-First، ثم فصّل أدوار الفرق في ورشة العمل (هاتف، خادم، جودة، أمان)، واختم باختبارات Pact في CI.",
        "talking_points_ar": "العقد أولاً Schema-First، مواصفات OpenAPI، نمط BFF، ورشة التوافق المشترك، اختبارات العقود Pact، ومنع التغييرات الكاسرة Breaking Changes.",
        "follow_ups_ar": "كيف تدير عملية ترقية إصدار الـ API (API Versioning) عندما تفرض ميزة جديدة تعديلاً جذرياً في بنية البيانات؟",
        "self_check_ar": "هل أكدت على الاتفاق قبل كتابة الكود، وذكرت احتياجات فرق الهاتف والأمان والجودة، وشرحت آلية الفحص الآلي في خط الـ CI؟",
        "references_ar": f"- [OpenAPI Initiative: OpenAPI Specification 3.1](https://www.openapis.org/) — المعيار القياسي الدولي المعتمد لتوثيق وتصميم عقود واجهات البرمجة.\n- [Pact Foundation: Consumer Driven Contracts](https://docs.pact.io/) — التوثيق الرسمي لنمط اختبارات العقود الموجهة من العميل لمنع التغييرات الكاسرة.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """نوحد رؤى الفرق بمنهجية 'العقد أولاً' بتعريف مواصفات OpenAPI في مستودع مركزي قبل كتابة الكود. ونعقد ورشة عمل يدافع فيها فريق الهاتف عن كفاءة الحزم والبطارية، ويحدد فريق الأمان المصادقة وحماية البيانات، ويبني فريق الجودة خوادم المحاكاة، ونلزم الـ CI باختبارات Pact لمنع أي تعديل كاسر في الخادم.""",
        "best_answer_ar": """يتطلب التنسيق الناجح بين فرق تطبيقات الهاتف والواجهات الخلفية والجودة والأمان اعتماد منهجية هندسية واضحة ترتكز على مبدأ 'العقد أولاً' قبل البدء في كتابة الشيفرة البرمجية.
نقضي على عشوائية التصاميم الفردية بعقد ورشة عمل مشتركة لتصميم العقد بصيغة OpenAPI أو Protocol Buffers في مستودع موحد.
خلال هذه الورشة، يدافع فريق الهاتف عن كفاءة البيانات وتقليل الحقول الزائدة واعتماد الترقيم بالمؤشرات لحماية البطارية، بينما يدرس فريق الخوادم كفاءة استعلامات قواعد البيانات والتخزين المؤقت.
ويتحقق فريق الأمان من أمان الترويسات ومصادقة الرموز وحظر البيانات الحساسة، في حين يستغل فريق الجودة المخطط لتوليد بيانات وهمية والبدء في كتابة الاختبارات فوراً.
ولضمان ديمومة هذا التوافق، نربط خطوط البناء المؤتمت باختبارات العقود التي يقودها العميل عبر أداة Pact؛ مما يمنع دمج أي تغيير في الخادم إذا كان يكسر التوافق مع إصدارات التطبيق الحالية.""",
        "deep_answer_ar": """من منظور حوكمة النظم الموسعة والتنسيق بين الفرق المتعددة، تمثل عقود واجهات البرمجة المعاهدة التشغيلية الحاكمة لاستقرار المنظومة البرمجية.
وعندما تُدار هذه العقود بعشوائية، تتفجر النزاعات المؤسسية؛ حيث ينتظر مطورو الهاتف اكتمال الخوادم، ويقضي مهندسو الجودة أسابيع في كتابة محاكيات يدوية، وتتسرب تعديلات كاسرة تحطم التطبيق في أيدي المستخدمين دون سابق إنذار.
ويقضي القادة التقنيون على هذا الارتباك عبر ثلاثة مرتكزات: التصميم المسبق للمخطط، وورش العمل التشاركية، والتحقق الآلي المستمر.
تبدأ العملية بصياغة مستند OpenAPI 3.1 في مستودع مستقل يمثل المصدر الوحيد للحقيقة. وفي ورشة العمل المتقاطعة، يفرض فريق الهاتف معايير كفاءة استهلاك الشبكة؛ مطالباً بنمط Backend-For-Frontend لتفادي استهلاك باقات الهواتف المحمولة في شبكات الجيل الرابع المتقطعة.
ويؤمّن فريق الأمان مسارات التحقق بتفعيل معايير OAuth2 وتشفير الرموز وحظر الحقول النصية الصريحة.
ويستفيد فريق الجودة من المخطط بتشغيل خوادم Prism لتشغيل اختبارات الأتمتة بالتوازي مع التطوير من اليوم الأول.
والضمانة الأكثر صلابة تكمن في أتمتة التحقق عبر Pact؛ حيث تُفحص كافة طلبات دمج كود الواجهة الخلفية مقابل عقود تطبيق الهاتف الحية، فإذا قام مطور الخادم بتغيير نوع حقل أو حذفه، تفشل عملية البناء فوراً في الـ CI. هذا التكامل الآلي يضمن سرعة إنجاز الفرق لمهامها دون خوف من المفاجآت الكارثية في الإنتاج."""
    }
}

# ==========================================
# LEAD-08: What metrics tell you whether a refactor was successful?
# ==========================================
DATA["LEAD-08"] = {
    "concept_en": """Validating whether an architectural refactor was truly successful requires a balanced scorecard evaluating technical stability, developer velocity, and business user experience:
- The Vanity Trap in Technical Refactoring:
  - Engineering teams often celebrate refactoring based purely on subjective feelings: \"the code looks cleaner\" or \"we are now using the latest library.\"
  - Without empirical baseline and post-migration telemetry, a refactor can introduce subtle regressions, increase startup latency, or balloon APK size without delivering measurable ROI.
- The 3-Tier Holistic Refactoring Evaluation Matrix:
  1. Technical Stability & Runtime Quality:
     - Crash-Free Sessions / Users: Must remain stable or improve (e.g., maintain > 99.85%).
     - ANR (Application Not Responding) Rate: Must decrease, especially across low-end devices.
     - Frame Drops & Jank: Percentage of frozen or slow frames (> 16ms / > 8ms) measured via Macrobenchmark and Android Vitals.
     - Cold App Startup Latency: Measured against physical baseline profiles (e.g., reduced from 2.8s to 1.2s).
     - Memory Churn & Heap Utilization: Reduction in GC pauses and Dalvik heap churn.
  2. Developer Velocity & Code Health (DORA Metrics):
     - Pull Request Cycle Time: Time elapsed from opening a PR to production merge.
     - Gradle Build Times: Measured reduction in clean and incremental build durations achieved through modularization.
     - Defect Density & Regression Rate: Number of bugs reported in the refactored subsystem drops significantly.
     - Test Execution Duration: Fast, deterministic unit test execution replacing slow end-to-end tests.
  3. Business & Conversion Impact:
     - Key Funnel Conversion: E.g., checkout completion rates increase due to elimination of UI freezes and responsiveness gains.""",
    "walkthrough_en": """Automating refactoring verification using Jetpack Macrobenchmark and Vitals telemetry in Kotlin:
```kotlin
// AndroidX Macrobenchmark: Quantifying startup and frame timing improvements post-refactor
@RunWith(AndroidJUnit4::class)
class RefactorVerificationBenchmark {
    @get:Rule
    val benchmarkRule = MacrobenchmarkRule()

    @Test
    fun verifyColdStartupPerformance() = benchmarkRule.measureRepeated(
        packageName = "com.enterprise.pos",
        metrics = listOf(StartupTimingMetric(), FrameTimingMetric()),
        iterations = 10,
        startupMode = StartupMode.COLD
    ) {
        pressHome()
        startActivityAndWait()

        // Measure frame rendering during complex list scrolling post-refactor
        val list = device.findObject(By.res("transaction_list"))
        list.setGestureMargin(device.displayWidth / 5)
        list.fling(Direction.DOWN)
        device.waitForIdle()
    }
}

// Executive Refactoring Success Scorecard:
// 1. App Startup Latency: Reduced by 48% (from 2.4s to 1.25s)
// 2. Frozen Frame Rate: Dropped from 3.2% to 0.4% in Google Play Vitals
// 3. PR Cycle Time: Dropped from 4.2 days to 1.6 days due to modularized Gradle builds
// 4. Crash-free Sessions: Improved from 99.72% to 99.94%
```""",
    "short_en": """Measure refactoring success across three objective dimensions: runtime quality, developer velocity, and business impact. Track Play Vitals for crash-free rates and reduced ANRs, verify startup and frame times using Jetpack Macrobenchmark, measure faster Gradle builds and PR cycle times, and confirm that user conversion funnels remained stable or improved.""",
    "structured_en": """Confirming the success of an architectural refactor requires measuring concrete telemetry before and after the migration rather than relying on subjective developer sentiment.
We evaluate refactoring across three objective tiers.
First is technical runtime stability. We examine Google Play Vitals and Crashlytics, asserting that crash-free user sessions remain above ninety-nine point nine percent and that ANR rates decrease. We run Jetpack Macrobenchmark suites on physical devices to prove that cold startup latency and UI jank dropped measurably.
Second is engineering velocity and code health. We track DORA metrics, confirming that modularization reduced incremental Gradle build times and shortened pull request review cycles. Furthermore, defect density in the refactored module should drop significantly.
Third is business and product impact. We verify that user retention, app store ratings, and funnel conversion rates, such as checkout completion, improved or held steady, proving tangible return on engineering investment.""",
    "deep_senior_en": """From an engineering economics, runtime performance auditing, and technical executive stewardship perspective, a refactor is an organizational capital investment that demands empirical proof of return on investment.
Too many development teams undertake expensive refactorings that fail to deliver tangible value. An architectural overhaul that introduces pristine design patterns but increases cold startup latency or causes a spike in production memory churn is, by objective business standards, an unmitigated failure.
Senior engineering leaders establish a quantitative baseline before touching a single line of production code. We configure Jetpack Macrobenchmark tests to record hard numbers for cold launch latency, TTID (Time to Initial Display), and frame-timing distributions across representative low-end Android hardware.
Following deployment, we monitor an integrated three-tier scorecard.
At the systems level, we verify that Play Console Vitals show zero regressions: ANR rates must remain well beneath the bad behavior threshold of zero point four seven percent, and memory allocations must reflect reduced garbage collection churn.
At the developer productivity level, we evaluate DORA metrics: modularization and dependency cleanup must produce measurable reductions in local and CI Gradle build times, while simplified domain abstractions should reduce pull request cycle time from days to hours.
Finally, we align with product managers to validate business metrics: analyzing analytics funnels to confirm that smoother screen transitions and zero ANRs translated into improved checkout conversion and higher customer retention. Presenting this comprehensive scorecard provides indisputable proof of architectural success and earns executive mandate for future technical investments.""",
    "meta_ar": {
        "id": "LEAD-08",
        "questionAr": "ما هي المقاييس والمؤشرات الدقيقة التي تؤكد لك نجاح عملية إعادة الهيكلة المعمارية (Refactoring)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "التحقق الموضوعي من نجاح إعادة الهيكلة (Refactoring ROI)، مقاييس جودة الأداء (Play Vitals, Macrobenchmark, ANRs)، مقاييس إنتاجية المطورين (DORA Metrics, Build Times)، ومؤشرات الأعمال وتجربة المستخدم.",
        "concept_ar": "يتطلب الحكم على نجاح عملية إعادة الهيكلة المعمارية (Refactoring) الاعتماد على مصفوفة متوازنة من المقاييس الرقمية الموثقة قبل وبعد التعديل، بدلاً من الانخداع بالانطباعات الشفهية المجردة مثل 'الكود أصبح أنظف': فإعادة الهيكلة التي تحسن شكل الكود لكنها تزيد من زمن فتح التطبيق أو ترفع استهلاك الذاكرة تعتبر فشلاً هندسياً! وتعتمد مصفوفة التقييم على 3 محاور موضوعية: أولاً، جودة الأداء واستقرار التشغيل برصد مؤشرات Play Vitals للتأكد من بقاء نسبة خلو الجلسات من الكراشات فوق 99.9%، وانخفاض معدل تجمد التطبيق (ANR)، وقياس تحسن زمن الفتح البارد (Cold Startup) وسلاسة الإطارات باستخدام مكتبة Jetpack Macrobenchmark؛ ثانياً، إنتاجية الفريق وسرعة التسليم بقياس مقاييس DORA مثل انخفاض وقت مراجعة ودمج الـ PRs، وتسريع وقت بناء المشروع في Gradle نتيجة تقسيم الموديولات، وانخفاض كثافة الأخطاء المكتشفة؛ ثالثاً، مؤشرات الأعمال برصد استقرار أو ارتفاع معدلات تحويل المستخدمين (Conversion Rates) وزيادة تقييمات التطبيق في المتجر، مما يثبت العائد الحقيقي على الاستثمار الهندسي.",
        "walkthrough_ar": """قياس أثر إعادة الهيكلة على سرعة الفتح وسلاسة الشاشة بأداة Macrobenchmark في كوتلن:
```kotlin
// اختبار مؤتمت لقياس زمن الإقلاع وسلاسة الإطارات ومقارنتها بالنسخة السابقة
@RunWith(AndroidJUnit4::class)
class RefactorVerificationBenchmark {
    @get:Rule
    val benchmarkRule = MacrobenchmarkRule()

    @Test
    fun verifyColdStartupPerformance() = benchmarkRule.measureRepeated(
        packageName = "com.enterprise.pos",
        metrics = listOf(StartupTimingMetric(), FrameTimingMetric()),
        iterations = 10,
        startupMode = StartupMode.COLD
    ) {
        pressHome()
        startActivityAndWait()

        // قياس كفاءة رسم الشاشة أثناء التمرير السريع بعد إعادة الهيكلة
        val list = device.findObject(By.res("transaction_list"))
        list.setGestureMargin(device.displayWidth / 5)
        list.fling(Direction.DOWN)
        device.waitForIdle()
    }
}

// تقرير نتائج إعادة الهيكلة المقدم للإدارة:
// 1. زمن فتح التطبيق: انخفض بنسبة 48% (من 2.4 ثانية إلى 1.25 ثانية).
// 2. نسبة الإطارات المجمدة: انخفضت من 3.2% إلى 0.4% في Google Play Vitals.
// 3. زمن تجميع Gradle: انخفض بنسبة 40% بفضل تقسيم الموديولات.
// 4. خلو الجلسات من الأعطال: ارتفع من 99.7% إلى 99.95%.
```""",
        "why_it_matters_ar": "الاعتماد على التخمين يجعل الفرق تهدر مئات الساعات في تعديلات لا طائل منها وقد تتسبب في بطء التطبيق وتراجع تقييماته في المتجر.",
        "worked_example_ar": "بعد إعادة هيكلة شاشة الدفع المعقدة، أثبتت مقاييس Macrobenchmark انخفاض وقت بدء الشاشة بنسبة 50%، مما قلل كراشات ANR بنسبة 80% ورفع نسبة إتمام عمليات الشراء بـ 2.5%.",
        "trade_offs_ar": "تسجيل المقاييس قبل البدء يستهلك يوماً إضافياً لإعداد الاختبارات؛ لكنه الدليل الحاسم الوحيد لتبرير الاستثمار الهندسي أمام الإدارة.",
        "failure_modes_ar": "أخطر الأخطاء هو بدء إعادة الهيكلة دون تسجيل خط الأساس (Baseline) مسبقاً، مما يجعل المقارنة بعد الانتهاء مستحيلة وعرضة للتشكيك.",
        "production_perspective_ar": "في الشركات التقنية الناضجة، لا يُعتبر أي PR لإعادة الهيكلة مكتملاً إلا إذا أرفق صاحبه نتائج قياس مقارنة تثبت عدم تراجع مؤشرات الأداء الأساسية.",
        "how_to_answer_ar": "ابدأ برفض التقييم الشفهي غير المقاس، ثم فصّل المحاور الثلاثة: استقرار وجودة التشغيل (Play Vitals وMacrobenchmark)، وسرعة المطورين (DORA ومقاييس البناء)، ومؤشرات الأعمال والتحويل.",
        "talking_points_ar": "خط الأساس Baseline، مقاييس Play Vitals، مكتبة Jetpack Macrobenchmark، معدلات ANRs، مقاييس DORA، زمن بناء Gradle، وعائد الاستثمار ROI.",
        "follow_ups_ar": "ماذا تفعل إذا أظهرت المقاييس تحسن مقروئية الكود وسرعة البناء ولكن زاد استهلاك الذاكرة وزمن الإقلاع البارد بشكل طفيف؟",
        "self_check_ar": "هل أكدت على القياس بالأرقام قبل وبعد، وذكرت أدوات أندرويد الرسمية، وشملت مقاييس المطورين ومؤشرات الأعمال؟",
        "references_ar": f"- [Android Developers: Measure app performance with Macrobenchmark](https://developer.android.com/topic/performance/benchmarking/macrobenchmark-overview) — الدليل الرسمي لقياس سرعة إقلاع التطبيق وسلاسة الإطارات بالأرقام.\n- [DORA: DevOps Research and Assessment Metrics](https://dora.dev/) — المعايير العالمية لقياس إنتاجية الفرق الهندسية وسرعة تسليم البرمجيات.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """نؤكد نجاح إعادة الهيكلة بمصفوفة قياس رقمية ثلاثية تقارن الوضع قبل وبعد التعديل: استقرار التشغيل بانخفاض معدل الكراشات وANRs وتسريع الإقلاع بـ Macrobenchmark، وإنتاجية المطورين بتسريع بناء Gradle وانخفاض وقت مراجعة الـ PRs ومقاييس DORA، ومؤشرات الأعمال باستقرار وارتفاع معدلات تحويل المستخدمين ورضاهم.""",
        "best_answer_ar": """يتطلب التأكد من نجاح عملية إعادة الهيكلة المعمارية الاعتماد على براهين رقمية ومقاييس موثقة قبل وبعد التعديل بدلاً من الاكتفاء بالانطباعات الذاتية.
نقيم نجاح العملية عبر ثلاثة أبعاد متكاملة:
أولاً، الجودة واستقرار التشغيل برصد مؤشرات Google Play Vitals لضمان بقاء الجلسات الخالية من الأعطال فوق 99.9% وانخفاض معدل تجمد الشاشة ANR، مع تشغيل اختبارات Jetpack Macrobenchmark لإثبات انخفاض زمن الإقلاع وسقوط الإطارات بالأرقام.
ثانياً، إنتاجية الفريق وصحة الكود بقياس مقاييس DORA العالمية؛ حيث نتحقق من تقليص زمن تجميع مشروع Gradle بفضل التقسيم الموديولي الرشيد، واختصار زمن مراجعة ودمج التعديلات، وانخفاض كثافة الأخطاء المكتشفة.
ثالثاً، أثر التجربة وقيمة الأعمال بالتحقق من استقرار مسارات الشراء وارتفاع معدلات إتمام العمليات وتحسن تقييمات المتجر، مما يقدم برهاناً ساطعاً على جدوى الاستثمار المعماري.""",
        "deep_answer_ar": """من منظور الاقتصاد الهندسي والتحليل المتقدم للأداء المؤسسي، تمثل إعادة الهيكلة استثماراً لرأس المال التقني يتطلب إثباتاً رقمياً قاطعاً على العائد الاستثماري.
فالفرق الهندسية غير الناضجة تقع كثيراً في فخ التباهي الشكلي؛ حيث تحتفل بتبني أحدث الأنماط المعمارية بينما تسببت التعديلات في زيادة زمن تشغيل التطبيق أو تفاقم استهلاك الذاكرة المؤقتة، وهو ما يُعد فشلاً هندسياً ذريعاً بمعايير الأعمال.
والقائد التقني يضع خط الأساس الرقمي الصارم قبل لمس سطر واحد من الكود؛ فيسجل زمن الإقلاع البارد، وسلاسة الإطارات، ومعدل استهلاك الذاكرة عبر اختبارات Macrobenchmark الدورية على هواتف حقيقية متفاوتة القدرات.
وعقب إطلاق التعديل في الإنتاج، نراقب لوحة مؤشرات ثلاثية الأبعاد:
على صعيد النظام، نتأكد من خلو مؤشرات Play Vitals من أي تراجع، وبقاء معدلات التعليق دون عتبة السلوك السيئ المحددة رسمياً من جوجل، مع انخفاض دورات تنظيف الذاكرة GC Churn.
وعلى صعيد إنتاجية المطورين، نتتبع مقاييس DORA للتأكد من أن تقسيم الموديولات قلص زمن البناء المحلي وفي خطوط الـ CI، واختصر دورة حياة الـ PR من أيام إلى ساعات.
وأخيراً، نتطابق مع مديري المنتجات للتأكد من أن القضاء على التهنيج انعكس إيجابياً على معدلات إتمام العمليات ونمو رضا المستخدمين، مما يوفر برهاناً لا يقبل الجدل على نجاح المعمارية الجديدة."""
    }
}

# ==========================================
# Validation & Runner logic
# ==========================================
def validate_words():
    print("Checking word counts and spoken style for LEAD-01 to LEAD-08...")
    for qid, d in sorted(DATA.items()):
        # Short answer (35 - 110)
        c_short = len(d["short_en"].split())
        assert 35 <= c_short <= 110, f"{qid}: short_en word count {c_short} out of range (35-110)"

        # Structured answer (100 - 280)
        c_struct = len(d["structured_en"].split())
        assert 100 <= c_struct <= 280, f"{qid}: structured_en word count {c_struct} out of range (100-280)"

        # Deep senior answer (200 - 650)
        c_deep = len(d["deep_senior_en"].split())
        assert 200 <= c_deep <= 650, f"{qid}: deep_senior_en word count {c_deep} out of range (200-650)"

        meta = d["meta_ar"]
        # Quick answer AR (35 - 110)
        c_qar = len(meta["quick_answer_ar"].split())
        assert 35 <= c_qar <= 110, f"{qid}: quick_answer_ar word count {c_qar} out of range (35-110)"

        # Best answer AR (90 - 280)
        c_bar = len(meta["best_answer_ar"].split())
        assert 90 <= c_bar <= 280, f"{qid}: best_answer_ar word count {c_bar} out of range (90-280)"

        # Deep answer AR (180 - 650)
        c_dar = len(meta["deep_answer_ar"].split())
        assert 180 <= c_dar <= 650, f"{qid}: deep_answer_ar word count {c_dar} out of range (180-650)"

        # Check spoken style (no bullets, no numbered lists)
        for field_name, text in [
            ("structured_en", d["structured_en"]),
            ("deep_senior_en", d["deep_senior_en"]),
            ("best_answer_ar", meta["best_answer_ar"]),
            ("deep_answer_ar", meta["deep_answer_ar"]),
        ]:
            assert not any(line.strip().startswith(("-", "*", "•")) for line in text.splitlines()), f"{qid}: {field_name} contains bullets"
            assert not any(line.strip() and line.strip()[0].isdigit() and line.strip()[1:3] in (". ", ") ") for line in text.splitlines()), f"{qid}: {field_name} contains numbered list"

        assert "على الجانب الآخر، فيما يخص" not in meta["best_answer_ar"], f"{qid}: best_answer_ar contains cliché"
        assert "على الجانب الآخر، فيما يخص" not in meta["deep_answer_ar"], f"{qid}: deep_answer_ar contains cliché"

    print("Pre-validation word count checks passed! Updating canonical questions...")

def apply_elevations():
    validate_words()

    topic_meta = {}
    for qid, d in sorted(DATA.items()):
        ee.update_canonical_question(
            qid=qid,
            concept_en=d["concept_en"],
            walkthrough_en=d["walkthrough_en"],
            structured_en=d["structured_en"],
            deep_senior_en=d["deep_senior_en"],
            short_en=d["short_en"],
        )
        topic_meta[qid] = d["meta_ar"]

    ee.save_topic_metadata("lead_01_08", topic_meta)
    ee.merge_all_metadata()

    for qid in sorted(DATA.keys()):
        errs = ee.validate_question(qid)
        if errs:
            print(f"Errors in {qid}:")
            for er in errs:
                print(f"  ❌ {er}")
            sys.exit(1)

    print(f"\nAll {len(DATA)} LEAD questions (LEAD-01 to LEAD-08) successfully elevated and passed validation!\n")

if __name__ == "__main__":
    apply_elevations()
