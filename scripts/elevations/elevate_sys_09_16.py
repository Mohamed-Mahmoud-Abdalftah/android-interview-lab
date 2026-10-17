#!/usr/bin/env python3
"""
Complete elevation script for SYS questions: SYS-09 to SYS-16.
Topic: Android System Design & Architecture Decisions (SYS)
Phase 4, Batch 2 - Full bilingual parity with all 19 metadata fields
"""

import os
import sys

sys.path.insert(0, os.path.abspath("scripts/elevations"))
import elevation_engine as ee

TOPIC_AR = "تصميم أنظمة وتطبيقات الموبايل (System Design) والقرارات الهندسية"
REVIEWED_DATE_AR = "تمت المراجعة والتحقق في 17 أكتوبر 2026"

DATA = {}

# ==========================================
# SYS-09: Design analytics, logs, metrics, and crash reporting.
# ==========================================
DATA["SYS-09"] = {
    "concept_en": """Designing an enterprise mobile observability architecture requires balancing real-time diagnostic visibility against device hardware constraints like battery drain, cellular data consumption, and local flash storage limits. Production telemetry consists of four core pillars: crash and fatal exception reporting, structured diagnostic breadcrumbs, user journey analytics, and application performance monitoring (APM). In-process unhandled crashes and native tombstone dumps must be captured via specialized SDKs like Crashlytics or Sentry with automated ProGuard deobfuscation mappings. High-volume analytics events and diagnostic logs must never trigger immediate synchronous network requests. Instead, they must be ingested into an in-memory buffer backed by a local SQLite disk queue. Batches of events are periodically compressed and flushed to remote endpoints over persistent HTTP connections or deferred to WorkManager when network conditions are constrained. Furthermore, mobile telemetry must enforce strict architectural privacy sanitization, redacting personally identifiable information, authentication headers, and payment credentials at the collection layer before any byte touches disk or wire.""",
    "walkthrough_en": """Designing an offline-tolerant, privacy-sanitizing telemetry dispatcher:
```kotlin
// 1. Immutable telemetry event contract with privacy scrubbing
data class TelemetryEvent(
    val eventId: String = UUID.randomUUID().toString(),
    val name: String,
    val timestampMs: Long = System.currentTimeMillis(),
    val attributes: Map<String, String> = emptyMap(),
    val metrics: Map<String, Double> = emptyMap()
)

// 2. Telemetry ingestion engine with local disk buffering and periodic batching
class TelemetryDispatcher @Inject constructor(
    private val localQueueDao: TelemetryQueueDao,
    private val telemetryApi: TelemetryApiService,
    private val appScope: CoroutineScope
) {
    private val eventChannel = Channel<TelemetryEvent>(capacity = 100)
    private val batchSize = 30
    private val sensitiveKeys = setOf("password", "token", "card_number", "cvv", "email")

    init {
        startIngestionLoop()
    }

    fun track(name: String, rawAttributes: Map<String, String>) {
        // Redact personally identifiable attributes at the ingestion boundary
        val sanitized = rawAttributes.mapValues { (key, value) ->
            if (sensitiveKeys.any { key.contains(it, ignoreCase = true) }) "[REDACTED]" else value
        }
        eventChannel.trySend(TelemetryEvent(name = name, attributes = sanitized))
    }

    private fun startIngestionLoop() = appScope.launch(Dispatchers.IO) {
        val memoryBatch = mutableListOf<TelemetryEvent>()
        while (isActive) {
            val event = withTimeoutOrNull(45_000L) { eventChannel.receive() }
            if (event != null) memoryBatch.add(event)

            if (memoryBatch.size >= batchSize || (memoryBatch.isNotEmpty() && event == null)) {
                try {
                    telemetryApi.uploadBatch(memoryBatch.toList())
                    memoryBatch.clear()
                } catch (e: Exception) {
                    // Persist batch to SQLite queue on network failure for deferred WorkManager delivery
                    localQueueDao.insertAll(memoryBatch.map { it.toEntity() })
                    memoryBatch.clear()
                }
            }
        }
    }
}
```""",
    "short_en": """We design mobile observability across crashes, analytics, metrics, and logs using local disk-backed batching queues to conserve battery and survive process death. We enforce strict privacy scrubbing before storing data, track startup latency and frame drops using JankStats, and collect crash breadcrumbs with asynchronous uploads.""",
    "structured_en": """A resilient mobile observability pipeline decouples high-volume diagnostic capture from network transmission to protect device battery and data bandwidth.
I organize mobile telemetry into four decoupled layers. Crash reporting captures uncaught exceptions and native signals with automated symbolication mappings, storing the last thirty user actions as diagnostic breadcrumbs.
Analytics and operational logs feed into a unified ingestion engine. Rather than dispatching immediate network calls, events accumulate in a memory buffer that flushes periodically in compressed batches to a local SQLite queue, surviving app process termination.
Application performance monitoring tracks critical user experience vitals, capturing cold start latency through reportFullyDrawn and UI stutter using AndroidX JankStats.
Before any telemetry is written to disk or transmitted over the wire, an architectural sanitizer intercepts payloads to redact authorization tokens, payment details, and personal identity data.""",
    "deep_senior_en": """From a staff mobile infrastructure standpoint, the most critical telemetry challenges involve managing high-volume data streams, diagnosing application not responding conditions, and respecting strict privacy compliance.
Standard crash SDKs fail to record ANR incidents because the main looper is blocked, preventing exception handlers from executing. Modern Android architectures query ApplicationExitInfo upon the next cold launch to inspect system tombstones, heap dump reasons, and native process exit codes.
High-frequency telemetry such as network latency distributions or continuous gesture tracking creates massive backend ingest costs. I resolve this by implementing dynamic server-driven sampling. High-volume performance traces are collected from a randomized one percent sample of active installs, whereas financial transaction failures and fatal application crashes maintain one hundred percent unsampled capture rates.
Cellular radio hardware operates on a state machine with full power and idle states. Firing isolated network requests keeps the radio continuously energized in high-power tail states, draining device battery rapidly. By queuing events into sixty-second local SQLite batches, we minimize radio state transitions and conserve substantial battery.
Logging architecture must completely decouple debug visibility from release overhead. Using Timber with build-variant configurations, verbose logs are piped to logcat in internal testing builds. For production release binaries, R8 compiler rules strip debug log bytecodes entirely, routing only structured business breadcrumbs to our circular ring buffer.
Finally, when devices encounter sustained network outages, local telemetry databases must enforce strict bounded retention policies with FIFO pruning so background diagnostics never exhaust user flash storage.""",
    "meta_ar": {
        "id": "SYS-09",
        "questionAr": "كيف تصمم منظومة المراقبة والتحليلات وسجلات الأعطال ومقاييس الأداء لتطبيق أندرويد ضخم؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على تصميم بنية مراقبة شاملة لتطبيقات الموبايل تشمل تقارير الانهيارات، والتحليلات السلوكية، ومقاييس الأداء التشغيلي، والسجلات المنظمة مع تطهير البيانات الحساسة وتوفير البطارية.",
        "why_it_matters_ar": "غياب المراقبة التشغيلية يجعل المطورين عاجزين عن معرفة أسباب انهيار التطبيق أو تراجع الأداء لدى العملاء، بينما الإرسال الشبكي العشوائي لكل حدث يستنزف بطارية الهاتف ويملأ مساحة التخزين المحلية.",
        "worked_example_ar": "نموذج تسجيل حدث تشغيلي مطهر من البيانات الحساسة:\n```kotlin\ndata class OperationLogEvent(\n    val eventId: String = UUID.randomUUID().toString(),\n    val eventName: String,\n    val timestamp: Long = System.currentTimeMillis(),\n    val sanitizedParams: Map<String, String>\n)\n```",
        "trade_offs_ar": "التسجيل التفصيلي يساعد في تتبع الأخطاء ولكنه يزيد من استهلاك القرص وحجم حزم البيانات ومخاطر الخصوصية، بينما الاكتفاء بعينات منخفضة يوفر الموارد ولكنه قد يخفي مشاكل نادرة الحدوث تصيب فئة محدودة من المستخدمين.",
        "failure_modes_ar": "تسريب بيانات الدخول أو أرقام البطاقات في مسارات التتبع وحزم الانهيار، أو ملء ذاكرة الهاتف حتى النفاد بسبب تخزين الأحداث محلياً دون وضع سقف أقصى للحجم وسياسة تدوير دورية، أو تجميد الخيط الرئيسي أثناء حفظ السجلات.",
        "production_perspective_ar": "في تطبيقات التجارة الكبرى، نجمع الأحداث في قاعدة بيانات Room ونفرغها دورياً في دفعات مضغوطة عبر WorkManager أثناء اتصال الشاحن والواي فاي، مع إرسال معرف تتبع موحد يربط أحداث الموبايل بسجلات السيرفر.",
        "how_to_answer_ar": "قسم الإجابة إلى أربع ركائز: تقارير الانهيارات والخبز التشخيصي، وتحليلات الاستخدام، ومقاييس الأداء مثل زمن الإقلاع وسقوط الإطارات بـ JankStats، والسجلات المفلترة. ركز على التجميع في دفعات محلية وتطهير البيانات الحساسة قبل الحفظ.",
        "talking_points_ar": "استخدام ApplicationExitInfo لتشخيص الـ ANR، وتجميع الأحداث لتوفير راديو الاتصال، ومكتبة JankStats، وتطهير البيانات الشخصية PII، وضبط عينات البيانات الحجمية عن بعد.",
        "follow_ups_ar": "- **المحاور:** \"ما الفرق بين استدعاء reportFullyDrawn() وقياس زمن onCreate في النشاط؟\"\n  **المرشح:** \"دالة reportFullyDrawn تشير إلى اكتمال رسم الشاشة بالكامل وعرض البيانات المسترجعة من الشبكة للمستخدم، بينما onCreate يقيس فقط ارتباط العناصر الرسومية المبدئية بالنظام دون اكتمال تحميل المحتوى الفعلي.\"\n\n- **المحاور:** \"كيف تكتشف تسريبات الذاكرة في الإنتاج دون التسبب في إبطاء هواتف المستخدمين؟\"\n  **المرشح:** \"نراقب مقاييس استهلاك الذاكرة الإجمالية ومعدلات نفاد الذاكرة OOM عبر واجهة ApplicationExitInfo بعد موت العملية، ونتجنب تشغيل أدوات فحص الذاكرة الثقيلة مثل LeakCanary في حزم الإنتاج الموجهة للمستخدمين.\"",
        "self_check_ar": "هل وضحت كيفية عزل تتبع الانهيارات عن التحليلات؟ هل بينت آلية تجميع الأحداث لحماية البطارية؟ وهل أكدت على قواعد تطهير البيانات الشخصية والخصوصية؟",
        "references_ar": f"- [Android Vitals](https://developer.android.com/topic/performance/vitals) — دليل مؤشرات أداء التطبيقات والتحليلات الرسمية من جوجل.\n- [JankStats Library](https://developer.android.com/topic/performance/jankstats) — مكتبة رصد بطء الشاشات وسقوط الإطارات في أندرويد.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "نصمم بنية المراقبة عبر فصل التقاط الأعطال والتحليلات ومقاييس الأداء في طوابير محلية مجمعة على القرص لتوفير البطارية وضمان عدم ضياعها عند انهيار التطبيق. نطبق تطهيرا صارما للبيانات الحساسة قبل التخزين، ونقيس زمن بدء التشغيل وسقوط الإطارات عبر JankStats مع رفع البيانات عبر دفعات مضغوطة.",
        "best_answer_ar": "تتطلب منظومة المراقبة الاحترافية في تطبيقات أندرويد الضخمة فك الارتباط بين توليد البيانات وإرسالها عبر الشبكة لحماية راديو الجهاز وعمر البطارية. نقسم المراقبة إلى أربع ركائز أساسية تشمل تقارير الانهيارات المفاجئة المدعومة بمسارات تنقل المستخدم الأخيرة، والتحليلات السلوكية، ومقاييس الأداء التشغيلي، والسجلات البرمجية المنظمة. تمر الأحداث عبر محرك استيعاب داخلي يجمع السجلات في الذاكرة ويفرغها في دفعات مجدولة داخل قاعدة بيانات محلية مثل Room لضمان بقائها عند توقف العمليات. نستخدم مكتبة JankStats لمراقبة بطء الشاشات وسقوط الإطارات وقياس زمن الإقلاع بدقة عبر استدعاء reportFullyDrawn. قبل كتابة أي حدث على القرص أو إرساله، نمرر الحقول عبر حاجز أمني يطهر المعرفات الشخصية ورموز المصادقة ومعلومات الدفع تلقائيا.",
        "deep_answer_ar": "على مستوى البنية التحتية المتقدمة، تتمثل التحديات الكبرى في تشخيص تعليق الواجهة غير المستجيب وضبط أحجام البيانات الضخمة مع الامتثال لقوانين الخصوصية وحماية طاقة البطارية. تفشل أدوات التقاط الانهيارات التقليدية في رصد حالات ANR لأن مسار الواجهة الرئيسي يكون مجمدا تماما، ولذلك نعتمد على واجهة ApplicationExitInfo المتوفرة بدءا من أندرويد 11 لقراءة أسباب إغلاق العملية وتفاصيل تتبع الذاكرة عند أول إقلاع بارد تال للتطبيق. للتعامل مع نقل مليارات الأحداث، نطبق نظام العينات الديناميكي القابل للتهيئة عن بعد، فنجمع تفاصيل أزمنة الشبكة من واحد بالمائة فقط من المستخدمين بينما نسجل مائة بالمائة من أعطال الدفع والانهيارات الكاملة. تعمل شرائح الاتصال الخلوي وفق آلة حالات تستهلك طاقة قصوى عند نقل البيانات، وتكرار إرسال الأحداث الفردية يبقي الراديو في حالة استهلاك مرتفع مستمر، مما يستنزف البطارية سريعا. نعالج ذلك بتجميع الأحداث في دفعات دورية كل دقيقة داخل قاعدة بيانات محلية، مع تفويض المهام المتراكمة لـ WorkManager للرفع أثناء اتصال الشاحن والواي فاي. بالنسبة للسجلات، نعتمد على Timber مع إعدادات R8 لحذف أوامر التسجيل الاستكشافي نهائيا من حزم الإنتاج والإبقاء فقط على مسارات التتبع الحرجة في ذاكرة دائرية محدودة تمنع استهلاك مساحة التخزين. كما نضع سياسة صارمة لتدوير السجلات القديمة وحذفها تلقائيا فور تجاوزها خمسين ميغابايت للحفاظ على سلامة الذاكرة ومساحة التخزين الخاصة بالمستخدم."
    }
}

# ==========================================
# SYS-10: How do you model states and transitions with an explicit state machine?
# ==========================================
DATA["SYS-10"] = {
    "concept_en": """Modeling application workflows and complex user flows using an explicit Finite State Machine (FSM) guarantees that illegal states become fundamentally unrepresentable at compile time. In Android applications, implicit state representations often scatter boolean flags across ViewModels, leading to race conditions where screens simultaneously exhibit loading indicators, error banners, and stale content. An explicit state machine architectures the domain around three immutable elements: discrete states, explicit transition events or intents, and asynchronous side effects. Kotlin sealed interfaces model the closed taxonomy of valid states and actions with exhaustive compiler checking. State transitions occur strictly through a pure reducer function that accepts the current state and incoming event, returning the next valid state alongside any required side-effect commands. State persistence across Android process recreation is achieved by saving deterministic state identifiers to SavedStateHandle or Room. This architecture provides predictable testing, eliminates invalid edge states, and ensures that asynchronous background operations cannot corrupt the user interface.""",
    "walkthrough_en": """Implementing an explicit state machine with sealed hierarchies and pure reducers:
```kotlin
// 1. Exhaustive state hierarchy ensuring impossible states cannot compile
sealed interface CheckoutState {
    data object Idle : CheckoutState
    data object Submitting : CheckoutState
    data class OtpChallengeRequired(val transactionId: String, val attemptsLeft: Int) : CheckoutState
    data class OrderSettled(val orderId: String, val receiptUrl: String) : CheckoutState
    data class TerminalFailure(val errorMessage: String, val isRecoverable: Boolean) : CheckoutState
}

// 2. Incoming events representing user actions and background results
sealed interface CheckoutIntent {
    data class AuthorizePayment(val cardToken: String, val amountCents: Long) : CheckoutIntent
    data class SubmitOtp(val otpCode: String) : CheckoutIntent
    data object RetryRequested : CheckoutIntent
}

// 3. Isolated side effects executed outside the pure state transition logic
sealed interface CheckoutEffect {
    data class LaunchBiometricPrompt(val challengeId: String) : CheckoutEffect
    data class ShowToast(val message: String) : CheckoutEffect
}

// 4. Pure state reducer function enforcing deterministic transitions
class CheckoutStateMachine {
    fun reduce(current: CheckoutState, intent: CheckoutIntent): Pair<CheckoutState, CheckoutEffect?> {
        return when (current) {
            is CheckoutState.Idle -> when (intent) {
                is CheckoutIntent.AuthorizePayment -> CheckoutState.Submitting to null
                else -> current to null
            }
            is CheckoutState.Submitting -> when (intent) {
                is CheckoutIntent.SubmitOtp -> current to null // Illegal transition ignored
                else -> current to null
            }
            is CheckoutState.OtpChallengeRequired -> when (intent) {
                is CheckoutIntent.SubmitOtp -> CheckoutState.Submitting to null
                is CheckoutIntent.RetryRequested -> current to CheckoutEffect.ShowToast("Enter received code")
                else -> current to null
            }
            is CheckoutState.TerminalFailure -> when (intent) {
                is CheckoutIntent.RetryRequested -> if (current.isRecoverable) CheckoutState.Idle to null else current to null
                else -> current to null
            }
            is CheckoutState.OrderSettled -> current to null
        }
    }
}
```""",
    "short_en": """We model application workflows using explicit state machines built with Kotlin sealed interfaces to represent mutually exclusive states and legal transitions. A pure reducer processes user intents, producing deterministic new states and side effects, while eliminating invalid edge states and surviving process death via SavedStateHandle.""",
    "structured_en": """An explicit state machine eliminates subtle race conditions by making illegal combinations of loading, data, and error flags impossible to compile.
I structure the system around three core pillars. States are represented through a sealed interface containing only mutually exclusive models with all necessary payload data.
User interactions and asynchronous completions are captured as sealed intents.
Transitions are governed by a pure, deterministic reducer function that takes the current state and incoming intent to compute the next valid state and optional side-effect commands.
If an event arrives that is illegal for the active state, such as an OTP submission while in an idle state, the reducer safely ignores it or emits a diagnostic warning.
To withstand Android process death and configuration changes, the state machine stores its active state identifier and restored parameters inside SavedStateHandle, enabling the screen to reconstruct its exact state upon process rebirth.""",
    "deep_senior_en": """From an enterprise architecture perspective, explicit state machines provide mathematical determinism to high-stakes mobile workflows like multi-step checkouts, authentication challenges, and hardware pairing.
The primary failure mode in mobile state handling is temporal coupling, where asynchronous coroutines complete out of order and overwrite newer states with stale data. An explicit reducer solves this by executing transitions sequentially over an actor-style Channel or Mutex, ensuring atomic state progression.
Side effects such as navigation commands, haptic feedback, or network requests must never be triggered directly inside state reducers. Instead, the reducer returns side-effect descriptions that an external effect handler consumes via buffered SharedFlow or Channel pipelines.
When designing distributed multi-screen flows, state machines should be partitioned into hierarchical sub-machines. A parent checkout coordinator delegates screen-specific steps to local machine instances while retaining ownership of overall transaction state and payment idempotency tokens.
Explicit state machines also empower time-travel debugging in production environments. By recording each transition event alongside incoming payloads and resulting states into a lightweight in-memory circular ring buffer, diagnostic logs capture the exact sequence of user actions leading up to an issue, making complex edge-case bug reproduction trivial.
Finally, testing complex business logic becomes trivial. Because the reducer is a pure function without Android framework dependencies, we write automated unit tests that feed event sequences into the reducer and assert resulting states without needing coroutine delays, mocking frameworks, or UI instrumentation tests.""",
    "meta_ar": {
        "id": "SYS-10",
        "questionAr": "كيف تنمذج حالات التطبيق وانتقالاتها باستخدام آلة حالات صريحة (Explicit State Machine)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على نمذجة حالات العمل المعقدة وانتقالاتها القانونية بشكل صريح باستخدام آلات الحالات المحددة، وضمان عدم تمثيل الحالات المستحيلة برمجياً وتأمين استرجاع الحالة بعد موت العملية.",
        "why_it_matters_ar": "تشتيت المتغيرات المنطقية المنفصلة في ViewModels يؤدي لظهور شاشات متناقضة تعرض مؤشر التحميل مع رسالة الخطأ والبيانات معاً، وتتسبب في سباق العمليات عند وصول الردود غير المتزامنة بترتيب مختلف.",
        "worked_example_ar": "نمذجة الانتقالات بدالة تحويل نقية:\n```kotlin\nfun reduce(state: OrderState, event: OrderEvent): OrderState = when(state) {\n    is OrderState.Draft -> if (event is OrderEvent.Submit) OrderState.Processing else state\n    is OrderState.Processing -> state // تجاهل أي نقرات إضافية أثناء المعالجة\n    is OrderState.Completed -> state\n}\n```",
        "trade_offs_ar": "آلة الحالات الصريحة تتطلب كتابة كود هيكلي أطول في البداية لتعريف الحالات والأحداث، لكنها تمنع مئات الأخطاء الخفية في وقت التشغيل وتجعل اختبارات الوحدة فورية وبسيطة للغاية.",
        "failure_modes_ar": "إطلاق المؤثرات الجانبية كاستدعاءات الشبكة أو التنقل داخل دالة التحويل النقية، أو إغفال حفظ معرف الحالة في SavedStateHandle مما يفقد المستخدم سياق تقدمه في الشاشات متعددة الخطوات.",
        "production_perspective_ar": "في التدفقات المالية وتطبيقات البنوك، نلزم جميع الشاشات الحرجة بآلات حالات صريحة مع تسجيل كل حدث وحالة في ذاكرة دائرية لتسهيل تحليل المشاكل واستنساخ أخطاء العملاء بدقة.",
        "how_to_answer_ar": "اشرح مفهوم جعل الحالات غير الصالحة مستحيلة البناء بـ Sealed Interfaces. وضح المكونات الثلاثة: الحالة، والحدث، ودالة التحويل النقية. وضح كيف تفصل المؤثرات الجانبية عبر SharedFlow وكيف تحفظ الحالة ضد موت العمليات.",
        "talking_points_ar": "مفهوم Finite State Machine، والتحويل النقي Reducer، وعزل الـ Side Effects، والتعامل مع موت العمليات عبر SavedStateHandle، وتقنية Time-Travel Debugging.",
        "follow_ups_ar": "- **المحاور:** \"لماذا يجب ألا يتم تخزين أحداث الواجهة التي تحدث لمرة واحدة (One-off Events) مثل رسائل التنبيه كحالة عادية؟\"\n  **المرشح:** \"لأن تخزين الأحداث اللحظية كحالة يؤدي لتكرار إطلاقها عند إعادة تدوير الشاشة؛ الحل هو إرسالها كمؤثرات جانبية عبر Channel أو SharedFlow يستهلكها المستمع لمرة واحدة فقط.\"\n\n- **المحاور:** \"ما الفرق بين نمط MVI وآلة الحالات الصريحة؟\"\n  **المرشح:** \"نمط MVI يمثل تطبيقاً معمارياً لتدفق البيانات أحادي الاتجاه، بينما آلة الحالات الصريحة تضيف قيوداً رياضية تمنع الانتقال بين الحالات إلا عبر مسارات مصرح بها ومحددة مسبقاً بقواعد انتقال واضحة.\"",
        "self_check_ar": "هل وضحت لماذا تجعل آلة الحالات تمثيل الحالات المتناقضة مستحيلاً؟ هل فرقت بين الحالة والمؤثر الجانبي؟ وهل بينت كيفية اختبار دالة التحويل النقي؟",
        "references_ar": f"- [Android Architecture: UI Layer](https://developer.android.com/topic/architecture/ui-layer) — إرشادات جوجل الرسمية لهيكلة حالات الواجهة.\n- [State machines in Android](https://developer.android.com/guide/navigation) — نمذجة مسارات التنقل والحالات في أندرويد.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "ننمذج حالات الشاشات وتدفقاتها عبر آلة حالات صريحة تعتمد على واجهات Kotlin المغلقة لتمثيل الحالات الحصرية والأحداث المسموحة. تقوم دالة تحويل نقية بمعالجة الأحداث لإنتاج حالة جديدة ومؤثرات جانبية محددة، مما يمنع الحالات المتضاربة ويسهل استرجاع الحالة عند توقف التطبيق.",
        "best_answer_ar": "تضمن آلة الحالات الصريحة منع الحالات المتناقضة مثل ظهور مؤشر التحميل ورسالة الخطأ والمحتوى في نفس اللحظة عبر جعل الحالات غير الصالحة مستحيلة البناء برمجيا. نبني الهيكل على ثلاث دعائم أساسية تشمل الحالات الحصرية المعرفة عبر واجهة مغلقة، والأحداث القادمة من المستخدم أو الشبكة، ودالة التحويل النقية. تستقبل دالة التحويل الحالة الحالية والحدث الجديد لتحسب الحالة التالية بدقة وأي أوامر جانبية مطلوبة مثل التنقل أو حفظ السجلات. إذا وصل حدث غير منطقي للحالة الحالية كإرسال رمز التحقق والشاشة في مرحلة البداية، تتجاهله الدالة بأمان دون إفساد واجهة المستخدم. نحافظ على بقاء آلة الحالات عبر حفظ معرف الحالة الحالية وبياناتها الأساسية في SavedStateHandle لضمان عودة الشاشة لنفس النقطة بعد إعادة إنشاء العملية من قِبل النظام.",
        "deep_answer_ar": "في الأنظمة المصرفية والعمليات المعقدة متعددة الخطوات، تمثل آلات الحالات الصريحة صمام الأمان لمنع تداخل الاستجابات غير المتزامنة وضمان اتساق العمليات المالية الحساسة. نتغلب على مشكلة تداخل استجابات الشبكة التي قد تعيد الكتابة فوق حالات أحدث من خلال تمرير الأحداث عبر قناة تسلسلية تعالج الانتقالات بصورة ذرية وتمنع أي سباق برمجي بين الكوروتينات المختلفة. نفصل المؤثرات الجانبية كاستدعاءات الـ API والتنقل بين الشاشات تماما عن دالة التحويل، حيث تكتفي الدالة بوصف المؤثر في كائن مستقل ينفذه معالج خارجي يراقب تدفقات الأحداث عبر SharedFlow منظم. في المسارات الكبيرة، نقسم المعمارية إلى آلات حالات هرمية بحيث تتولى آلة عامة تنسيق المعاملة المالية بينما تدير آلات فرعية شاشات البطاقات وتأكيد الهوية. توفر هذه المعمارية ميزة استثنائية لتشخيص الأخطاء عبر تسجيل تسلسل الأحداث والحالات في ذاكرة دائرية خفيفة، مما يتيح إعادة تمثيل المشاكل النادرة بدقة عبر إعادة تشغيل نفس الأحداث في بيئة التطوير. نحافظ على بقاء آلة الحالات عبر حفظ معرف الحالة الحالية وبياناتها الأساسية في SavedStateHandle لضمان عودة الشاشة لنفس النقطة بعد توقف العملية في الخلفية، بينما تظل اختبارات الوحدة بالغة السرعة لأن دالة التحويل النقية تختبر دون الحاجة لأي محاكاة لنظام أندرويد."
    }
}

# ==========================================
# SYS-11: How do you deal with concurrency, timeouts, retries, and idempotency?
# ==========================================
DATA["SYS-11"] = {
    "concept_en": """Enterprise mobile applications operate across unpredictable network topologies, intermittent connectivity drops, and concurrent background synchronizations. Robust system design mandates a coordinated approach to concurrency, timeouts, retries, and idempotency. Concurrency must be governed through structured coroutines where parent scopes bind child tasks, preventing leaked background operations upon screen dismissal. Timeouts must be categorized based on operation semantics: aggressive deadlines for user-facing reads and extended deadlines with explicit progress indicators for critical mutations. Retrying network requests blindly leads to retry storms that exhaust device batteries and overload backend infrastructure. Retries should apply strictly to transient infrastructure failures using truncated exponential backoff with full jitter, while immediately failing deterministic client errors. Crucially, non-idempotent mutations like payment authorizations or order placements must transmit unique client-generated idempotency keys, guaranteeing that duplicate network packets caused by timeout recovery never trigger duplicate server side mutations.""",
    "walkthrough_en": """Implementing resilient mutations with exponential backoff jitter and idempotency keys:
```kotlin
// 1. Client-generated mutation request with unique idempotency envelope
data class PaymentRequest(
    val idempotencyKey: String = UUID.randomUUID().toString(),
    val accountId: String,
    val amountCents: Long,
    val currency: String
)

// 2. Retry execution policy with full jitter backoff algorithm
class ResilientNetworkExecutor @Inject constructor() {
    suspend fun <T> executeWithRetry(
        maxAttempts: Int = 3,
        initialDelayMs: Long = 1000L,
        maxDelayMs: Long = 8000L,
        block: suspend () -> T
    ): Result<T> {
        var currentAttempt = 0
        while (currentAttempt < maxAttempts) {
            try {
                // Enforce strict cooperative deadline per attempt
                return withTimeout(5000L) {
                    Result.success(block())
                }
            } catch (e: Exception) {
                currentAttempt++
                // Never retry client-side validation errors or deliberate cancellations
                if (e is CancellationException) throw e
                if (e is HttpException && e.code() in 400..499 && e.code() != 429) {
                    return Result.failure(e)
                }
                if (currentAttempt >= maxAttempts) return Result.failure(e)

                // Exponential backoff calculation with full randomized jitter
                val exponentialDelay = (initialDelayMs * 2.0.pow(currentAttempt - 1)).toLong().coerceAtMost(maxDelayMs)
                val jitteredDelay = Random.nextLong(0, exponentialDelay)
                delay(jitteredDelay)
            }
        }
        return Result.failure(IllegalStateException("Exhausted retries"))
    }
}
```""",
    "short_en": """We handle mobile network instability by binding operations to structured coroutine scopes with explicit timeouts and exponential backoff jitter. We retry strictly transient errors like socket drops and server rate limits, while pairing all mutating network requests with client-generated idempotency keys to prevent duplicate transactions.""",
    "structured_en": """A resilient mobile communication layer coordinates timeouts, retries, and idempotency to survive flaky cellular networks without corrupting backend state.
I structure network operations within structured coroutine scopes, ensuring background jobs cancel cooperatively when the hosting lifecycle terminates.
Timeouts are tailored to intent: fast five-second deadlines for read operations to display cached data quickly, and longer fifteen-second windows for critical mutations paired with clear UI progress feedback.
For retries, I restrict repeated attempts strictly to transient network dropouts and server rate limits. Deterministic client errors like bad credentials fail immediately.
Retries always execute using truncated exponential backoff randomized with full jitter to prevent thundering herd spikes on backend clusters.
For any state-mutating operation like placing an order or making a payment, the client generates a unique idempotency UUID and persists it locally before transmission, allowing safe retries over ambiguous timeout failures.""",
    "deep_senior_en": """From a staff systems engineering perspective, handling network failure requires distinguishing between transport failure and application outcome ambiguity.
When an HTTP mutation times out, the client cannot know whether the server never received the packet, processed the transaction and crashed, or responded while the cellular tower dropped the downlink. Treating timeouts as outright failures leads to dangerous UX errors. By persisting the idempotency key in local storage alongside the pending transaction, our retry engine safely resubmits the exact same token. The backend detects the existing key, bypasses duplicate processing, and returns the original transaction outcome.
Mobile devices frequently experience split-brain network transitions when switching between Wi-Fi and mobile data mid-transfer. This causes TCP sockets to hang indefinitely without returning an RST packet. We guard against this by configuring strict OkHttp call timeouts alongside coroutine withTimeout deadlines to enforce deterministic termination.
For high-volume background synchronizations, naive retry loops quickly drain device batteries. We delegate offline backlogs to WorkManager, utilizing OS-level constraints such as unmetered Wi-Fi and battery not low, paired with platform-managed exponential backoff.
Inside the client process, concurrency races on shared mutable state are neutralized by routing operations through single-threaded coroutine dispatchers or Mutex locks rather than broad JVM synchronized blocks.
Finally, we implement circuit breaker patterns on mobile clients. If successive calls to a downstream service experience continuous timeouts, the client temporarily trips the circuit, serving cached fallbacks immediately for a cooldown period to protect system responsiveness and prevent radio exhaustion.""",
    "meta_ar": {
        "id": "SYS-11",
        "questionAr": "كيف تتعامل مع التزامن، فترات الانتظار، إعادة المحاولة، ومفاتيح عدم التكرار (Idempotency) في بيئات الشبكة المتقلبة؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على تنسيق العمليات المتزامنة، وإدارة المهل الزمنية، وتصميم استراتيجيات إعادة المحاولة المتقدمة، وضمان سلامة المعاملات عبر مفاتيح عدم التكرار.",
        "why_it_matters_ar": "إعادة إرسال طلبات تعديل البيانات عشوائياً عند انقطاع الاتصال قد يؤدي لخصم الأموال من المستخدم مرتين أو تكرار إنشاء الحسابات، بينما المهل الزمنية الطويلة تجمد الواجهة وتستنزف موارد الهاتف.",
        "worked_example_ar": "توليد وإرفاق مفتاح عدم التكرار في ترويسة الطلب:\n```kotlin\nval request = Request.Builder()\n    .url(\"https://api.app.com/checkout\")\n    .header(\"X-Idempotency-Key\", UUID.randomUUID().toString())\n    .post(body)\n    .build()\n```",
        "trade_offs_ar": "إعادة المحاولة السريعة ترفع نسب نجاح العمليات ولكنها قد تشكل عبئاً ضخماً على الخوادم (Retry Storms)؛ ولذلك نوازن ذلك بالتراجع الأسي مع التشتت العشوائي لحماية البنية التحتية.",
        "failure_modes_ar": "إعادة محاولة الطلبات التي فشلت بأخطاء العميل 4xx مثل أخطاء التحقق أو انتهاء الصلاحية، أو نسيان حفظ مفتاح عدم التكرار محلياً قبل الإرسال مما يفقد التطبيق القدرة على تتبع نتيجة المعاملة بعد الانهيار.",
        "production_perspective_ar": "في تطبيقات الدفع العالمية، نقيد طلبات السحب بمفتاح عدم تكرار صالح لمدة 24 ساعة في السيرفر، ونفوض عمليات المزامنة المتراكمة لـ WorkManager لتعمل عند توفر شبكة مستقرة وشاحن البطارية.",
        "how_to_answer_ar": "ابدأ بإدارة التزامن عبر Structured Concurrency. حدد قواعد المهل الزمنية للعمليات. اشرح خوارزمية Exponential Backoff with Full Jitter، واختم بالأهمية القصوى لمفاتيح الـ Idempotency لمنع تكرار المعاملات المالية.",
        "talking_points_ar": "خوارزمية Full Jitter، ومفاتيح Idempotency Keys، والتعامل مع أخطاء 429 و 503، وضبط callTimeout في OkHttp، والتحكم في مهام الخلفية عبر WorkManager.",
        "follow_ups_ar": "- **المحاور:** \"ما هو التشتت العشوائي الكامل (Full Jitter) في خوارزميات التراجع الأسي ولماذا نحتاجه؟\"\n  **المرشح:** \"هو اختيار رقم تأخير عشوائي بين صفر والقيمة المحسوبة للتراجع الأسي؛ والهدف منه منع آلاف الهواتف من إعادة إرسال الطلبات في نفس الثانية عند عودة الخدمة مما قد يسقط الخوادم مجدداً.\"\n\n- **المحاور:** \"لماذا يجب ألا تعيد محاولة طلب فاشل برمز 401 Unauthorized تلقائياً؟\"\n  **المرشح:** \"لأن رمز 401 يعني فشل المصادقة، وإعادة المحاولة بنفس التوكن القديم ستفشل حتماً؛ يجب أولاً تجديد التوكن بنجاح عبر Authenticator ثم إعادة المحاولة بالتوكن الجديد لمرة واحدة فقط.\"",
        "self_check_ar": "هل فرقت بين الأخطاء المؤقتة والدائمة في إعادة المحاولة؟ هل شرحت دور مفاتيح عدم التكرار في منع السحب المزدوج؟ وهل بينت كيفية إدارة المهل الزمنية برمجياً؟",
        "references_ar": f"- [Exponential Backoff And Jitter (AWS Architecture Blog)](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/) — المرجع القياسي لخوارزميات التراجع الأسي والتشتت.\n- [Stripe API: Idempotent Requests](https://stripe.com/docs/api/idempotent_requests) — توثيق سترايب حول تصميم المعاملات الآمنة بمفاتيح عدم التكرار.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "ندير استقرار الشبكة عبر تقييد العمليات بأطر Coroutines ذات مهل زمنية محددة وخوارزميات إعادة محاولة تعتمد على التراجع الأسي مع التشتت العشوائي. نقتصر في إعادة المحاولة على الأخطاء العابرة، ونرفق مفاتيح عدم تكرار فريدة مع كل طلب تعديل لمنع ازدواجية المعاملات المالية.",
        "best_answer_ar": "تتطلب معالجة تقلبات شبكات الموبايل موازنة دقيقة بين سرعة استجابة الواجهة وضمان سلامة البيانات على الخوادم البعيدة. نربط العمليات غير المتزامنة بنطاقات Coroutines منظمة تلغي المهام الفرعية تلقائيا عند مغادرة الشاشة لمنع تسريب الموارد. نحدد مهل زمنية تناسب نوع العملية، فتكون سريعة لعمليات القراءة لعرض البيانات المخزنة محليا، وأطول لعمليات التعديل الحساسة مع إظهار مؤشرات تقدم واضحة للمستخدم. في حالات انقطاع الاتصال، لا نعيد المحاولة إلا للأخطاء العابرة مثل انقطاع المقابس أو أخطاء الخادم المؤقتة، مع استبعاد أخطاء العميل نهائيا. نطبق خوارزمية التراجع الأسي المضاف إليها تشتت عشوائي لمنع هجمات ارتداد الطلبات المتزامنة على الخوادم. لضمان عدم تكرار العمليات المالية، يولد التطبيق مفتاح عدم تكرار فريد ويحفظه محليا قبل إرسال الطلب، مما يسمح بإعادة المحاولة بأمان تام حتى لو انقطع الاتصال أثناء الرد.",
        "deep_answer_ar": "على المستوى الهندسي المتقدم، يكمن التحدي الأكبر في التمييز بين فشل نقل البيانات وحالة الغموض في نتيجة العملية عند انقطاع الاتصال فجأة أثناء المعاملات المالية. عندما تنتهي مهلة طلب مالي، لا يمكن للعميل معرفة هل سقط الطلب قبل وصوله للخادم أم تمت المعالجة وفقدت حزمة الرد في طريق العودة. بحفظ مفتاح عدم التكرار محليا في قاعدة البيانات مع تفاصيل المعاملة، يستطيع التطبيق إعادة إرسال نفس المفتاح لاحقا ليتعرف الخادم عليه ويعيد النتيجة السابقة دون سحب أموال مكررة. تعاني الهواتف المحمولة من مشكلة انقطاع المقابس عند التحول المفاجئ بين شبكات الواي فاي وبيانات الهاتف الخلوية، حيث يظل الاتصال معلقا دون إغلاق، ولذلك ندمج مهل OkHttp الصارمة مع withTimeout في الكوروتين لضمان الإنهاء الفوري وتحرير الموارد. بالنسبة للمزامنة الخلفية الكبيرة، نفوض المهام لـ WorkManager للاستفادة من قيود النظام مثل توفر شبكة واي فاي واكتمال شحن البطارية مع تراجع أسي مدعوم بتشتت عشوائي. داخل التطبيق، نمنع سباقات التزامن على الذاكرة المشتركة عبر استخدام أقفال Mutex أو حصر التعديلات في مسارات أحادية بدلا من التزامن القديم. كما نطبق نمط قاطع الدائرة محليا بحيث يتوقف التطبيق مؤقتا عن استدعاء الخدمات المتعطلة ويعتمد على البيانات المخبأة لحماية راديو الهاتف وسرعة استجابة الشاشات."
    }
}

# ==========================================
# SYS-12: How do you make a reusable Android SDK with a stable public API?
# ==========================================
DATA["SYS-12"] = {
    "concept_en": """Authoring an enterprise-grade reusable Android SDK requires a fundamentally different engineering mindset than building end-user applications. In an SDK, the consumers are other engineering teams whose app stability, binary size, build speeds, and architectural integrity depend entirely on the library's design. The public API surface must be strictly minimal, exposing only high-level interfaces, immutable configuration models, and explicit callbacks or Flows, while hiding all internal orchestration behind Kotlin internal visibility and package-private constructs. The Kotlin Binary Compatibility Validator (BCV) must be integrated into continuous integration to catch unintended public signature breaks. Furthermore, SDKs must isolate their dependencies, avoiding transitive leakage through Gradle implementation configurations. SDKs must never trigger unhandled runtime exceptions that crash the host application, must publish consumer ProGuard rules that preserve only necessary entry points, and must utilize distinct resource prefixes to prevent resource collisions with host applications.""",
    "walkthrough_en": """Structuring an isolated Android SDK with public interfaces and hidden implementations:
```kotlin
// 1. Minimal, stable public interface exposed to host applications
interface IdentityVerificationSdk {
    fun startVerification(sessionId: String, callback: VerificationCallback)

    companion object {
        // Factory pattern hiding internal class instantiation and lifecycle binding
        fun create(context: Context, configuration: SdkConfiguration): IdentityVerificationSdk {
            return IdentityVerificationSdkImpl(context.applicationContext, configuration)
        }
    }
}

// 2. Immutable public configuration contract
data class SdkConfiguration(
    val apiKey: String,
    val environment: Environment = Environment.PRODUCTION,
    val enableBiometrics: Boolean = true
) {
    enum class Environment { SANDBOX, PRODUCTION }
}

// 3. Callback contract communicating terminal outcomes without throwing exceptions
interface VerificationCallback {
    fun onSuccess(verifiedToken: String)
    fun onFailure(error: SdkError)
}

sealed class SdkError(val code: Int, val message: String) {
    class NetworkFailure(message: String) : SdkError(1001, message)
    class UserCancelled : SdkError(1002, "User aborted verification")
    class InternalError(cause: Throwable) : SdkError(1003, cause.localizedMessage ?: "Unknown error")
}

// 4. Internal implementation hidden from host app autocomplete and classpath
internal class IdentityVerificationSdkImpl(
    private val appContext: Context,
    private val config: SdkConfiguration
) : IdentityVerificationSdk {
    override fun startVerification(sessionId: String, callback: VerificationCallback) {
        // Internal orchestration using hidden network and biometric engines
    }
}
```""",
    "short_en": """We build reusable Android SDKs by keeping the public API minimal, using Kotlin internal visibility to hide implementation details, and enforcing binary compatibility in CI. We isolate transitive dependencies, ship consumer ProGuard rules, prefix all resources, and catch internal failures to prevent host application crashes.""",
    "structured_en": """Designing a production-grade Android SDK requires isolating the library implementation while providing a bulletproof, minimal public contract.
I enforce strict API surface discipline by declaring internal classes and dependencies as internal, exposing only clean interfaces and immutable configuration objects.
We enforce semantic versioning and integrate the Kotlin Binary Compatibility Validator plugin in continuous integration to catch accidental binary or source incompatibilities before merging.
Dependency isolation is critical. In the build script, dependencies use the implementation configuration rather than api to prevent leaking third-party libraries like Retrofit or OkHttp into the host app classpath.
The SDK must never crash the host application. All internal coroutine scopes catch unexpected errors and surface them through structured error callbacks or sealed result types.
Finally, we ship embedded consumer-proguard-rules.pro files so consumer apps automatically retain necessary SDK interfaces while shrinking internal bytecodes, and we prefix all Android resources with a unique namespace to prevent naming collisions.""",
    "deep_senior_en": """From a staff architecture perspective, distributing an Android library requires deep consideration of lifecycle independence, initialization overhead, and binary footprint impact.
Historically, SDKs relied on empty ContentProviders for auto-initialization at app startup. While convenient, this practice slows cold startup across all consumer apps. Modern SDK architecture favors explicit lazy initialization via a builder or App Startup Initializer, allowing host apps to control execution timing and pass necessary application contexts.
Managing transitive dependency conflicts is a major maintenance hazard. If an SDK bundles an opinionated JSON serializer or specific coroutines version, it can cause duplicate class runtime crashes in host apps with mismatched dependencies. We mitigate this by either writing zero-third-party dependency core modules relying solely on pure Kotlin and Android framework primitives, or shading critical internal dependencies using Gradle shadow relocation plugins.
Backward compatibility must be preserved across both source and binary levels. Adding a default parameter in a Kotlin public function breaks binary compatibility for Java callers because the compiled bytecode signature changes. We guard against this by applying JvmOverloads annotations and maintaining golden API dump files in version control.
Lastly, the SDK must establish clean memory boundaries, using ApplicationContext to prevent Activity leaks and providing an explicit teardown method to cancel internal background workers when host applications log out or terminate the flow.""",
    "meta_ar": {
        "id": "SYS-12",
        "questionAr": "كيف تصمم مكتبة أندرويد (SDK) قابلة لإعادة الاستخدام بواجهة برمجية عامة مستقرة؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على تصميم مكتبات أندرويد مستقرة تجارياً، وحماية التوافق الثنائي، وعزل الاعتماديات الخارجية، ومنع تسريب الذاكرة أو التسبب في انهيار التطبيق المضيف.",
        "why_it_matters_ar": "توزيع مكتبة سيئة التصميم يسبب انهيارات عشوائية في تطبيقات العملاء، ويزيد من حجم حزمهم البرمجية، ويحدث تضارباً بين إصدارات المكتبات المشتركة مما يدمر سمعة المنتج البرمجي.",
        "worked_example_ar": "قواعد ProGuard المدمجة لحماية واجهات المكتبة العامة:\n```proguard\n# consumer-rules.pro المرفق مع الـ AAR\n-keep public interface com.sdk.publicapi.** { *; }\n-keepclassmembers enum com.sdk.publicapi.** { *; }\n```",
        "trade_offs_ar": "تضمين مكتبات خارجية شهيرة داخل الـ SDK يسرع التطوير الداخلي ولكنه قد يتصادم مع إصدارات نفس المكتبات في تطبيق العميل؛ ولذلك نفضل الاعتماد على حلول كوتلن الصافية قدر الإمكان.",
        "failure_modes_ar": "تسريب سياق Activity والتسبب في Memory Leak، أو إلقاء استثناءات غير معالجة تؤدي لإغلاق التطبيق الحاضن، أو نسيان إضافة بادئة لأسماء الموارد مما يجعل التطبيق المضيف يستبدل أيقونات ونصوص المكتبة بالخطأ.",
        "production_perspective_ar": "في كبرى مكتبات الدفع والتحقق، نستخدم أداة Binary Compatibility Validator في خوادم الـ CI لرفض أي طلب سحب يغير توقيع أي دالة عامة دون رفع رقم الإصدار وفق معايير SemVer.",
        "how_to_answer_ar": "ركز على تقليص الواجهة العامة للحد الأدنى، واستخدام كلمة internal لإخفاء التفاصيل، وعزل التبعيات بـ implementation، وتضمين قواعد ProGuard وتفادي التهيئة التلقائية عبر ContentProvider.",
        "talking_points_ar": "أداة Binary Compatibility Validator، وقواعد consumer-rules.pro، والتظليل Shading للاعتماديات، والتهيئة الكسولة عبر App Startup، وتجنب تسريب السياق.",
        "follow_ups_ar": "- **المحاور:** \"ما الفرق بين التوافق المصدري (Source Compatibility) والتوافق الثنائي (Binary Compatibility) في المكتبات؟\"\n  **المرشح:** \"التوافق المصدري يعني إمكانية إعادة تجميع كود التطبيق المضيف مع الإصدار الجديد دون أخطاء بناء، بينما التوافق الثنائي يعني أن التطبيق المجمع مسبقاً سيعمل مباشرة مع الـ AAR الجديد في وقت التشغيل دون إعادة ترجمة الكود.\"\n\n- **المحاور:** \"ما فائدة ملف consumer-rules.pro داخل موديول الـ Android Library؟\"\n  **المرشح:** \"هو ملف يدمج تلقائياً داخل حزمة الـ AAR ليتم تطبيقه على قواعد R8/ProGuard الخاصة بالتطبيق المضيف، مما يضمن الحفاظ على واجهات المكتبة دون حاجة المطور لكتابة قواعد يدوية.\"",
        "self_check_ar": "هل وضحت كيفية الحفاظ على التوافق الثنائي؟ هل بينت أثر التهيئة الكسولة على الإقلاع؟ وهل شرحت أسلوب عزل الاعتماديات لمنع تصادم الحزم؟",
        "references_ar": f"- [Kotlin Binary Compatibility Validator](https://github.com/Kotlin/binary-compatibility-validator) — أداة جيتبرينز الرسمية لمراقبة التوافقية الثنائية.\n- [Create an Android Library](https://developer.android.com/studio/projects/android-library) — التوثيق الرسمي لبناء ونشر مكتبات أندرويد.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "نبني مكتبات أندرويد احترافية عبر تقليص الواجهة العامة إلى الحد الأدنى، وإخفاء التفاصيل البرمجية باستخدام internal، والتحقق من التوافق الثنائي في الـ CI. نعزل الاعتماديات الخارجية لمنع تسربها لتطبيق العميل، ونوفر قواعد ProGuard مدمجة ونبادئ الموارد لحمايتها من التضارب مع منع انهيار التطبيق المضيف.",
        "best_answer_ar": "يتطلب بناء مكتبة أندرويد تفكيرا معماريا صارما لأن المستهلك هنا هو فريق برمجي آخر تعتمد موثوقية تطبيقه وحجم حزمته على جودة مكتبتك. نحافظ على واجهة برمجية مصغرة عبر كشف واجهات مجردة وكائنات إعدادات غير قابلة للتعديل مع إخفاء محركات العمليات الداخلية بكلمة internal. نربط أداة Binary Compatibility Validator في خوادم البناء المستمر لرفض أي تغيير يكسر التوافق الثنائي أو المصدري دون رفع الإصدار وفق SemVer. نعتمد على implementation في ملفات Gradle لمنع تسريب مكتباتنا الداخلية مثل Retrofit إلى مساحة أسماء التطبيق المضيف. نضمن عدم التسبب في انهيار التطبيق الحاضن نهائيا عبر احتواء كل الاستثناءات وإعادتها كنتائج خطأ محددة في كائنات مغلقة. وأخيرا، نضمن ملف قواعد ProGuard مدمجا يحدد أجزاء المكتبة الواجب حفظها تلقائيا مع إضافة بادئة اسمية فريدة لكل الموارد لتجنب استبدال ملفات التطبيق الحاضن.",
        "deep_answer_ar": "على المستوى الهندسي المتقدم، يجب الانتباه لتأثير المكتبة على زمن إقلاع التطبيق المضيف وحجم الذاكرة وحجم ملف الـ AAR النهائي. نبتعد عن التهيئة التلقائية القديمة عبر ContentProvider لأنها تبطئ الإقلاع البارد، ونوفر تهيئة صريحة وكسولة تسمح للمطور بتحديد وقت تفعيل المكتبة وتمرير سياق التطبيق العام والتحكم في إعدادات البيئة البرمجية. لحل مشكلة تعارض إصدارات الاعتماديات مع التطبيق الحاضن، نصمم نواة المكتبة بالاعتماد حصريا على لغة Kotlin الأساسية ومكتبات النظام دون جلب أطر خارجية، أو نطبق تقنية التظليل Shading لإعادة تسمية الحزم الداخلية ومنع تضارب الفئات ومكتبات التسلسل في وقت التشغيل. نحافظ على التوافق مع لغة Java باستخدام وسوم JvmOverloads و JvmStatic لأن إضافة بارامترات افتراضية في كوتلن قد يكسر توافق التوقيع الثنائي في لغة جافا. نراقب استهلاك الذاكرة عبر استخدام سياق ApplicationContext فقط لمنع تسريب الـ Activities، وتوفير دالة تفكيك صريحة تلغي الـ Coroutines العالقة وتحرر الموارد متى انتهت الحاجة للخدمة. كما نحرص على عدم طلب صلاحيات النظام الخطيرة بشكل مفاجئ وترك إدارة طلب الإذن لتطبيق العميل مع كشف واجهات واضحة لمعالجة رفض الصلاحيات دون انهيار. كما نوفر وثائق برمجية دقيقة مع أمثلة توضيحية كاملة تسهل دمج المكتبة في مشاريع العملاء، ونعتمد على أدوات التحليل الثابت لمنع أي تسريب للذاكرة أثناء دورة حياة التطبيق الحاضن."
    }
}

# ==========================================
# SYS-13: How do you manage database migrations and backwards compatibility?
# ==========================================
DATA["SYS-13"] = {
    "concept_en": """Managing local database schema evolution across millions of active Android devices is one of the highest-risk operations in mobile engineering. Unlike backend database migrations where operations run centrally in synchronized rollout windows, mobile app updates are completely asynchronous. Users may skip multiple app releases, jumping directly from an ancient database version to the newest release. In Room, failing to handle migrations properly triggers an IllegalStateException that crashes the application on cold startup. Destructive migrations must be strictly forbidden in production. Schema evolution requires writing deterministic Migration objects with explicit raw SQLite DDL scripts. Furthermore, schema files must be exported via room.schemaLocation and validated in automated continuous integration using MigrationTestHelper. Backwards compatibility must also extend to the remote backend, ensuring that database entities accommodate nullable columns, default values, and schema rollbacks during staged Play Store rollouts.""",
    "walkthrough_en": """Implementing deterministic Room migrations with automated validation tests:
```kotlin
// 1. Explicit incremental database migrations with safe DDL modifications
val MIGRATION_1_2 = object : Migration(1, 2) {
    override fun migrate(db: SupportSQLiteDatabase) {
        // Adding a column with a strict NOT NULL constraint and default fallback
        db.execSQL("ALTER TABLE orders ADD COLUMN delivery_notes TEXT NOT NULL DEFAULT ''")
        // Creating an index to support fast queried lookups
        db.execSQL("CREATE INDEX IF NOT EXISTS index_orders_created_at ON orders(created_at)")
    }
}

val MIGRATION_2_3 = object : Migration(2, 3) {
    override fun migrate(db: SupportSQLiteDatabase) {
        // SQLite does not support dropping columns directly in older engines; recreate table safely
        db.execSQL(
            "CREATE TABLE orders_new (" +
            "id TEXT PRIMARY KEY NOT NULL, " +
            "total_cents INTEGER NOT NULL, " +
            "delivery_notes TEXT NOT NULL, " +
            "created_at INTEGER NOT NULL)"
        )
        db.execSQL("INSERT INTO orders_new (id, total_cents, delivery_notes, created_at) SELECT id, total_cents, delivery_notes, created_at FROM orders")
        db.execSQL("DROP TABLE orders")
        db.execSQL("ALTER TABLE orders_new RENAME TO orders")
    }
}

// 2. Automated MigrationTestHelper verifying schema integrity across update jumps
@RunWith(AndroidJUnit4::class)
class OrderDatabaseMigrationTest {
    private val TEST_DB = "migration-test"

    @get:Rule
    val helper: MigrationTestHelper = MigrationTestHelper(
        InstrumentationRegistry.getInstrumentation(),
        AppDatabase::class.java
    )

    @Test
    fun migrate1To3_containsValidData() {
        // Create database with version 1 and insert seed data
        var db = helper.createDatabase(TEST_DB, 1).apply {
            execSQL("INSERT INTO orders (id, total_cents, created_at) VALUES ('ord_101', 5000, 1600000000)")
            close()
        }

        // Run migrations across both versions and validate final schema
        db = helper.runMigrationsAndValidate(TEST_DB, 3, true, MIGRATION_1_2, MIGRATION_2_3)
        val cursor = db.query("SELECT delivery_notes FROM orders WHERE id = 'ord_101'")
        assertTrue(cursor.moveToFirst())
        assertEquals("", cursor.getString(0))
        cursor.close()
    }
}
```""",
    "short_en": """We manage Room database evolution by writing explicit migration scripts with raw SQLite DDL and testing them automatically using MigrationTestHelper. We ban destructive fallbacks in production, add new columns with safe default values, and support multi-version upgrade paths for users who skip intermediate application releases.""",
    "structured_en": """Managing database migrations in Android requires safeguarding user offline data while accommodating asynchronous client update cycles.
I prohibit fallbackToDestructiveMigration in production builds because wiping local databases destroys pending offline mutations and cached credentials.
Every schema change requires an explicit Room Migration object executing raw SQLite commands. When adding new columns, we define non-null constraints with safe default values to preserve existing records.
Because Android users often skip multiple app versions, Room chains individual migration paths automatically, such as executing migration one to two followed immediately by two to three.
We export JSON schema snapshots via the room.schemaLocation compiler argument.
In our continuous integration test suite, we implement automated migration tests using Room MigrationTestHelper, asserting that databases populated with legacy records successfully upgrade and maintain data integrity across version jumps.""",
    "deep_senior_en": """From a staff database engineering perspective, mobile schema migrations require deep knowledge of SQLite internal limitations and backend synchronization lifecycles.
Older SQLite engines embedded in Android lack support for standard DDL operations like dropping columns or altering constraints. In these scenarios, the migration must execute a classic table recreation sequence: create a temporary table with the new schema, copy existing data from the legacy table, drop the legacy table, and rename the new table. This sequence must execute within an atomic transaction to prevent corrupt half-migrated states if the app process crashes mid-flight.
When deploying staged rollouts on the Play Store, schema changes must maintain backwards compatibility with both older app clients and backend APIs. If an update introduces a new entity attribute, the local database and backend contracts must treat that attribute as optional during the rollout window. If a catastrophic bug forces an app rollback, older binaries must still function without crashing over unrecognised server fields.
For massive enterprise tables containing hundreds of thousands of records, running synchronous migrations on the main thread during app cold launch causes severe ANRs. For non-critical analytics or cache tables, we execute asynchronous background migrations, presenting a lightweight splash screen or deferring non-essential table upgrades until after interactive UI initialization.
Finally, we implement a defensive corrupted database recovery hook. If SQLite encounters physical flash corruption, rather than crashing in an infinite bootloop, the framework captures the error, attempts database vacuum recovery, and safely re-initializes clean state as a last resort.""",
    "meta_ar": {
        "id": "SYS-13",
        "questionAr": "كيف تدير ترقيات قواعد بيانات Room والتوافقية العكسية دون فقدان بيانات المستخدمين؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على كتابة ترقيات قواعد بيانات Room يدوياً وتلقائياً، وحماية بيانات المستخدمين، واختبار سلامة المخططات بـ MigrationTestHelper، والتعامل مع قفزات الإصدارات المتعددة.",
        "why_it_matters_ar": "فشل ترقية قاعدة البيانات يؤدي لانهيار التطبيق فور تشغيله بـ IllegalStateException، واستخدام خيار المسح التدميري يمسح كل بيانات المستخدمين ومعاملاتهم غير المتزامنة دون رجعة.",
        "worked_example_ar": "تفعيل تصدير مخطط قاعدة البيانات في Gradle:\n```kotlin\nksp {\n    arg(\"room.schemaLocation\", \"$projectDir/schemas\")\n}\n```",
        "trade_offs_ar": "الترقية التلقائية AutoMigration في Room توفر الوقت للتغييرات البسيطة، ولكن التغييرات المعقدة كإعادة تسمية الجداول أو دمجها تتطلب ترقيات يدوية مخصصة بـ SQL لتفادي تشوه البيانات.",
        "failure_modes_ar": "تفعيل fallbackToDestructiveMigration في الإنتاج، أو نسيان وضع قيمة افتراضية DEFAULT عند إضافة عمود جديد غير فارغ مما يسبب فشل الترقية لجميع السجلات القديمة.",
        "production_perspective_ar": "في المشروعات الكبرى، نفرض اختبارات أتمتة إجبارية بـ MigrationTestHelper تحاكي انتقال المستخدم من الإصدار 1 إلى 5 مباشرة للتحقق من عدم وجود أي خطأ قبل رفع الحزمة للمتجر.",
        "how_to_answer_ar": "ابدأ بحظر الحذف التدميري في الإنتاج. اشرح كتابة كائنات Migration الصريحة بأوامر SQLite. بين كيف يتعامل Room مع قفزات الإصدارات، واشرح اختبار المخططات عبر MigrationTestHelper وتصدير الـ Schemas.",
        "talking_points_ar": "أداة MigrationTestHelper، والترقيات التراكمية، ومشاكل قيود SQLite القديمة، والتوافق أثناء التحديثات التدريجية (Staged Rollouts)، والتعافي من تلف قواعد البيانات.",
        "follow_ups_ar": "- **المحاور:** \"كيف يتعامل محرك SQLite في أندرويد القديم مع حذف عمود من جدول قائم؟\"\n  **المرشح:** \"محركات SQLite الأقدم من 3.35 لا تدعم DROP COLUMN؛ لذلك ننشئ جدولاً جديداً بالمخطط المطلوب، وننسخ البيانات القديمة إليه بـ INSERT INTO، ثم نحذف الجدول القديم ونعيد تسمية الجديد داخل Transaction.\"\n\n- **المحاور:** \"ما هو دور تصدير المخطط عبر room.schemaLocation؟\"\n  **المرشح:** \"يقوم بتوليد ملفات JSON تمثل تاريخ كل إصدار للمخطط، وتستخدمها أداة MigrationTestHelper لمقارنة المخطط الحقيقي في الكود بالمخطط المنفذ والتأكد من مطابقة الأنواع والفهارس.\"",
        "self_check_ar": "هل وضحت خطورة المسح التدميري للبيانات؟ هل بينت كيفية معالجة قفزات التحديث المتعددة؟ وهل شرحت أسلوب اختبار الترقية آلياً؟",
        "references_ar": f"- [Testing Room Migrations](https://developer.android.com/training/data-storage/room/testing-db) — الدليل الرسمي لاختبار ترقيات قواعد البيانات في أندرويد.\n- [SQLite ALTER TABLE Documentation](https://www.sqlite.org/lang_altertable.html) — توثيق عمليات تعديل الجداول في محرك SQLite.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "ندير ترقيات Room عبر كتابة مسارات ترقية يدوية صريحة بأوامر SQLite DDL واختبارها آليا عبر MigrationTestHelper. نحظر الحذف التدميري تماما في الإنتاج، ونضيف الأعمدة الجديدة بقيم افتراضية آمنة، مع دعم الترقية عبر قفزات متعددة للمستخدمين الذين يتخطون تحديثات التطبيق الوسيطة.",
        "best_answer_ar": "تعد ترقيات قواعد البيانات المحلية من أخطر العمليات البرمجية في تطبيقات أندرويد لأن تحديثات المستخدمين تتم بصورة غير متزامنة تماما. نحظر تفعيل fallbackToDestructiveMigration في حزم الإنتاج لأن مسح البيانات يدمر المعاملات العالقة غير المتزامنة. نكتب كائنات ترقية يدوية صريحة تنفذ أوامر SQLite المباشرة لإضافة الجداول والفهارس، ونحرص عند إضافة أي عمود غير قابل للقيمة الفارغة على تعيين قيمة افتراضية صريحة لحماية السجلات الحالية. يدعم Room تسلسل الترقيات تلقائيا إذا قفز المستخدم من الإصدار الأول إلى الثالث مباشرة بتنفيذ مسار الترقية مرحليا. نقوم بتصدير مخطط قاعدة البيانات كملفات JSON عبر خيارات المترجم، ونكتب اختبارات أتمتة عبر أداة MigrationTestHelper لملء قاعدة بيانات بنسختها القديمة بالبيانات والتحقق الصارم من نجاح ترقيتها وسلامة محتواها قبل الدمج.",
        "deep_answer_ar": "على المستوى الهندسي المتقدم، تصطدم ترقيات قواعد البيانات بمحدودية محرك SQLite في أجهزة أندرويد القديمة التي لا تدعم حذف الأعمدة أو تعديل القيود مباشرة. نتغلب على ذلك بتطبيق نمط إعادة إنشاء الجدول الكلاسيكي، فننشئ جدولا مؤقتا بالمخطط الجديد، وننقل السجلات القديمة إليه، ثم نحذف الجدول القديم ونعيد تسمية الجديد، كل ذلك داخل معاملة ذرية تضمن عدم ترك قاعدة البيانات في حالة مشوهة لو انهارت العملية في المنتصف. أثناء التحديثات التدريجية على متجر التطبيقات، يجب الحفاظ على التوافق العكسي مع الخوادم، فنجعل الحقول الجديدة اختيارية محليا وسحابيا حتى اكتمال الترقية لجميع المستخدمين لتجنب انهيار النسخ السابقة. قد تؤدي استعادة النسخ الاحتياطية للنظام عبر Google Auto-Backup إلى استرجاع قاعدة بيانات قديمة على إصدار تطبيق حديث، مما يتطلب معالجة استباقية تتحقق من تطابق رقم الإصدار وإجراء الترقية المتسلسلة فورا. في الجداول الضخمة التي تحتوي مئات الآلاف من السجلات، قد تؤدي الترقية المباشرة في مسار الإقلاع إلى تعليق التطبيق وحدوث ANR، لذا ننقل ترقية الجداول الثانوية وسجلات الكاش إلى مسارات خلفية. كما نضع نظاما دفاعيا ذكيا للتعامل مع التلف الفيزيائي لقاعدة البيانات بحيث يحاول استعادة الملفات عبر التفريغ والضغط قبل اتخاذ قرار إعادة التهيئة كخيار أخير."
    }
}

# ==========================================
# SYS-14: How do you design API boundaries for multiple teams?
# ==========================================
DATA["SYS-14"] = {
    "concept_en": """Scaling mobile engineering across dozens of autonomous product squads requires decoupling codebase dependencies through well-defined API boundaries and architectural contracts. When multiple teams contribute to a monolithic codebase without explicit boundaries, code ownership blurs, merge conflicts escalate, build times balloon, and a breaking change in one domain silently breaks unrelated features. Effective API boundary design splits each domain into a public contract module (:api) and a private implementation module (:impl). The api module exposes pure Kotlin interfaces, domain entities, and navigation contracts with zero platform implementation details. Feature squads depend strictly on external api modules, remaining completely unaware of implementation classes. Dependency injection frameworks like Dagger or Hilt bind interfaces to implementations within the root application module. This architecture enforces clean code ownership, facilitates parallel development, accelerates incremental compilation, and allows teams to refactor internal implementations without impacting peer squads.""",
    "walkthrough_en": """Designing decoupled API contracts and navigation boundaries for multiple feature teams:
```kotlin
// In module :feature:checkout:api (Shared public contract owned by Checkout Squad)
interface CheckoutNavigationApi {
    fun navigateToCheckout(launcher: ActivityResultLauncher<Intent>, cartId: String)
}

interface CheckoutStatusProvider {
    fun observePendingOrdersCount(): Flow<Int>
}

data class CheckoutSession(
    val sessionId: String,
    val cartTotalCents: Long,
    val isEligibleForOneClick: Boolean
)

// In module :feature:checkout:impl (Private implementation hidden from peer squads)
internal class CheckoutNavigationApiImpl @Inject constructor(
    private val appContext: Context
) : CheckoutNavigationApi {
    override fun navigateToCheckout(launcher: ActivityResultLauncher<Intent>, cartId: String) {
        val intent = Intent(appContext, CheckoutActivity::class.java).apply {
            putExtra("EXTRA_CART_ID", cartId)
        }
        launcher.launch(intent)
    }
}

// In module :app (Root composition module binding interfaces to concrete implementations)
@Module
@InstallIn(SingletonComponent::class)
abstract class CheckoutBindingModule {
    @Binds
    @Singleton
    internal abstract fun bindCheckoutNav(impl: CheckoutNavigationApiImpl): CheckoutNavigationApi
}
```""",
    "short_en": """We design API boundaries for multiple teams by splitting each feature into an api contract module and an impl private module. Peer teams depend strictly on public interfaces and domain models, hiding internal implementation details and wiring dependencies at the root application layer using Dagger or Hilt.""",
    "structured_en": """Scaling an engineering organization across multiple mobile squads requires decoupling team ownership through strict module contracts.
I establish a clear separation of concerns by dividing every domain into an api module and an impl module.
The api module contains only pure interfaces, immutable data models, and navigation contracts, with zero references to internal libraries or Android Views.
Consuming teams depend exclusively on the api module through Gradle. This prevents peer squads from coupling to internal ViewModels, database entities, or network DTOs.
Concrete implementation classes inside the impl module are marked with Kotlin internal visibility, preventing external access.
The root application module acts as the dependency injection assembler, using Dagger or Hilt to bind concrete implementations to public interface contracts.
This boundary ensures squads can completely refactor their internal database schemas and UI layouts without triggering recompilation or breaking builds across other teams.""",
    "deep_senior_en": """From a staff systems architect perspective, establishing cross-team API boundaries is as much an organizational and governance challenge as it is a technical one.
A common failure mode in modularized codebases is the leaky abstraction problem, where network DTOs or database entities are exposed directly in public API contracts. When backend teams alter network payloads, multiple feature teams suffer compilation breakages. We mandate strict model mapping boundaries: network models map to internal domain entities, which map to public contract objects at the module edge.
Navigation between team boundaries presents another architectural hazard. Hardcoded Activity class references create circular module dependencies that break Gradle builds. We solve this by introducing abstract navigation interfaces or URI-based deep link routers registered into a centralized navigation mediator. Feature A requests navigation to Checkout with a payload, and the mediator resolves the destination without Feature A knowing the concrete Activity class.
To prevent breaking changes across dozens of squads, we establish clear API versioning and deprecation policies. When an API contract must change, the owning squad introduces the new method alongside a Deprecated annotation with an explicit ReplaceWith expression and sunset timeline, giving consuming teams time to migrate asynchronously.
Finally, we enforce these architectural boundaries automatically using ArchUnit or Gradle dependency analysis plugins in CI, instantly failing pull requests that attempt to establish unauthorized direct dependencies between private implementation modules.""",
    "meta_ar": {
        "id": "SYS-14",
        "questionAr": "كيف تصمم حدود الـ APIs والتعاقدات البرمجية لتطبيق ضخم تعمل عليه فرق متعددة؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على وضع حدود برمجية واضحة بين الفرق المستقلة، وفصل الموديولات بنمط API/Impl، وتصميم واجهات الملاحة المجردة، وحوكمة التبعيات لمنع التداخل والتعطيل.",
        "why_it_matters_ar": "غياب الحدود الصارمة يجعل كود الفرق متداخلاً ومعتمداً على التفاصيل الداخلية لبعضه البعض، مما يؤدي لتعطل البناء عند كل تعديل بسيط وتضارب المسؤوليات بين الفرق البرمجية.",
        "worked_example_ar": "هيكل ملفات الاعتماد في Gradle لموديول ميزة تعتمد على عقد ميزة أخرى فقط:\n```kotlin\ndependencies {\n    implementation(project(\":feature:checkout:api\")) // الاعتماد على العقد فقط\n    // يُحظر تماماً استدعاء project(\":feature:checkout:impl\")\n}\n```",
        "trade_offs_ar": "فصل الموديولات بنمط API/Impl يضاعف عدد موديولات المشروع وإعدادات Gradle، ولكنه يوفر حماية معمارية فائقة وتسريعاً هائلاً لأزمنة التجميع التزايدي للفرق الكبيرة.",
        "failure_modes_ar": "تسريب كائنات الشبكة أو كيانات قاعدة البيانات في واجهات الـ API العامة، أو الاعتماد المباشر على أسماء كلاسات الشاشات بين الفرق مما يسبب دورات اعتماد دائرية تكسر البناء.",
        "production_perspective_ar": "في المؤسسات الضخمة، نضع موديول اختبارات تجريبية (Testing Fixtures) داخل كل موديول API يوفر محاكيات جاهزة لعقود الفريق، مما يتيح للفرق الأخرى اختبار شاشاتها بسهولة تامة.",
        "how_to_answer_ar": "اشرح تقسيم النطاقات لـ api و impl. وضح كيف تعتمد الفرق الزميلة على واجهات العقد المجردة دون معرفة كلاسات التنفيذ. اشرح ربط التبعيات عبر Dagger/Hilt في موديول التطبيق الرئيسي وتجريد الملاحة بالـ Deep Links.",
        "talking_points_ar": "نمط API/Impl Modules، وحوكمة الكود بـ ArchUnit، وموجهات الـ Deep Linking، وعزل نماذج الـ DTO عن التعاقدات العامة، وموديولات الاختبارات التجريبية Fixtures.",
        "follow_ups_ar": "- **المحاور:** \"كيف تمنع مهندساً في فريق البحث من إضافة تبعية مباشرة على موديول التنفيذ الداخلي لفريق الدفع؟\"\n  **المرشح:** \"نطبق فحوصات أتمتة معمارية في خوادم الـ CI عبر ArchUnit أو Gradle Dependency Analysis ترفض طلب الدمج فوراً إذا وجد أي سطر استدعاء لموديول impl خارج موديول التطبيق الرئيسي.\"\n\n- **المحاور:** \"كيف تدير التنقل بين شاشات تملكها فرق مختلفة دون التسبب في اعتماد دائري؟\"\n  **المرشح:** \"نلغي الربط المباشر بأسماء الـ Activities ونعتمد إما على واجهات ملاحة مجردة يتم حقنها في موديول التطبيق، أو وسيط ملاحة عام يوجه الشاشات عبر روابط Deep Links مجردة.\"",
        "self_check_ar": "هل وضحت كيفية كسر الاعتماد الدائري في الملاحة؟ هل فرقت بين نماذج الـ API ونماذج الـ Impl؟ وهل بينت كيفية حوكمة الحدود في الـ CI؟",
        "references_ar": f"- [Guide to Android Modularization](https://developer.android.com/topic/modularization) — وثيقة جوجل الرسمية لتقسيم المشروعات الكبرى.\n- [Large Scale App Architecture](https://slack.engineering) — مدونة سلاك الهندسية حول إدارة حدود الفرق البرمجية.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "نصمم حدود الـ APIs لفرق العمل عبر تقسيم كل ميزة إلى موديول api عام للتعاقدات وموديول impl خاص بالتنفيذ. تعتمد الفرق الأخرى حصريا على الواجهات العامة ونماذج الدومين المجردة، بينما يتم ربط الاعتماديات في موديول التطبيق الرئيسي عبر Dagger أو Hilt لمنع التداخل وتسريع البناء.",
        "best_answer_ar": "يتطلب توسيع الفرق البرمجية في تطبيقات أندرويد الضخمة وضع حدود هندسية واضحة تفصل ملكية الكود وتمنع تضارب التعديلات بين الفرق المختلفة. نعتمد نمط فصل الموديولات الثنائي، حيث نقسم كل نطاق وظيفي إلى موديول تعاقدات api وموديول تنفيذ داخلي impl. يحتوي موديول التعاقدات على واجهات برمجية مجردة ونماذج بيانات غير قابلة للتعديل دون أي تفاصيل خاصة بواجهات المستخدم أو مكتبات الشبكة. تعتمد الفرق الأخرى برمجيا على موديول التعاقدات فقط، مما يمنعها تماما من الوصول إلى تفاصيل قاعدة البيانات أو نماذج الـ DTO الداخلية. نحدد كلاسات التنفيذ الحقيقية بكلمة internal ونربطها بالواجهات العامة في موديول التطبيق الرئيسي عبر Dagger أو Hilt. يتيح هذا الفصل لأي فريق إعادة بناء واجهاته أو تغيير مكتباته الداخلية دون أن يؤثر ذلك على بناء أو عمل ميزات الفرق الزميلة.",
        "deep_answer_ar": "على مستوى المعمارية المتقدمة وحوكمة الفرق، يمثل تسريب النماذج الداخلية الخطر الأكبر على استقرار التعاقدات البرمجية بين الفرق المستقلة. عندما يتم كشف كائنات الشبكة أو جداول قاعدة البيانات مباشرة في تعاقدات الموديول العامة، يتسبب أي تعديل من فريق الواجهة الخلفية في كسر البناء لعدة فرق في نفس الوقت، ولذلك نلزم الفرق بنماذج تحويل صارمة عند حدود كل موديول تعزل نماذج الـ DTO تماما عن نماذج الدومين العامة. للتغلب على مشكلة الاعتماديات الدائرية الناتجة عن التنقل بين شاشات تملكها فرق مختلفة، نلغي الاعتماد المباشر على أسماء كلاسات الشاشات ونعتمد على واجهات ملاحة مجردة أو وسيط ملاحة عام يوجه الشاشات عبر روابط Deep Links دون تبعيات متبادلة في ملفات Gradle. نوفر داخل كل موديول تعاقدي موديولا فرعيا للاختبارات التجريبية يحتوي على محاكيات جاهزة للواجهات العامة، مما يتيح للفرق الأخرى كتابة اختبارات الوحدة بسهولة دون الحاجة لتهيئة موديول التنفيذ الفعلي. نضع سياسة صارمة لتحديث التعاقدات، فعند الحاجة لتغيير واجهة نضع وسم Deprecated مع توفير البديل وفترة سماح زمنية تتيح للفرق الأخرى الترقية التدريجية. وأخيرا، نطبق أدوات فحص آلية في CI مثل ArchUnit لرفض أي طلب سحب يحاول عمل ربط مباشر بين موديولات التنفيذ الخاصة."
    }
}

# ==========================================
# SYS-15: Compare monolith and multi-module designs.
# ==========================================
DATA["SYS-15"] = {
    "concept_en": """The architectural choice between a monolithic single-module structure and a multi-module architecture is one of the most critical decisions impacting development velocity, build scalability, and team autonomy in Android. A monolithic architecture, where all source code resides within a single :app module, offers simplicity, minimal Gradle configuration overhead, effortless cross-feature refactoring, and zero inter-module dependency plumbing. However, as an organization scales beyond a handful of engineers, monoliths suffer severe build bottlenecks due to single-threaded compilation phases, frequent merge conflicts, and blurred architectural boundaries. Conversely, a multi-module architecture partitions the application into decoupled Gradle modules grouped by layer or feature. Modularization enables massive build speedups via parallel compilation and Gradle remote build caching, enforces strict team code ownership, and unlocks advanced deployment options like dynamic feature modules. The decision to modularize requires evaluating organizational scale, build hardware budgets, and CI governance maturity against the added maintenance cost of Gradle build scripts.""",
    "walkthrough_en": """Contrasting Monolith versus Multi-Module dependency graph topologies:
```text
// 1. Monolithic Single-Module Structure (:app contains everything)
// Pros: Single build.gradle.kts, trivial refactoring, no wiring boilerplate.
// Cons: Linear build times, tight coupling, merge conflict hot-spots.
:app
 ├── auth/ (activities, viewmodels, network, room entities)
 ├── feed/ (activities, viewmodels, network, room entities)
 └── core/ (database, network, shared utilities)

// 2. Multi-Module Architecture by Feature and Layer
// Pros: Parallel compilation, remote build caching, dynamic feature delivery.
// Cons: Complex Gradle management, dependency substitution overhead.
:app (Application composition, navigation graph assembly, Dagger root)
 ├── :feature:auth:api
 ├── :feature:auth:impl (depends on :feature:auth:api, :core:network, :core:database)
 ├── :feature:feed:api
 ├── :feature:feed:impl (depends on :feature:feed:api, :core:network, :core:ui)
 ├── :core:designsystem (Compose themes, atomic UI components)
 ├── :core:network (OkHttp, Retrofit, authentication interceptors)
 └── :core:database (Room database, base DAO abstractions)
```""",
    "short_en": """A monolith offers simplicity and fast initial velocity for small teams, but causes slow builds and coupling at scale. Multi-module architectures provide parallel compilation, remote build caching, strict team ownership, and dynamic feature delivery, but introduce Gradle complexity and wiring overhead.""",
    "structured_en": """Choosing between a monolith and a multi-module architecture requires balancing organizational scale against build infrastructure complexity.
A monolithic architecture where all code lives in a single app module is ideal for early-stage startups and small teams. It eliminates Gradle configuration overhead, makes refactoring effortless, and avoids dependency wiring boilerplate.
However, as team size exceeds ten engineers, the monolith encounters severe friction: compilation times become agonizingly slow, merge conflicts on shared files multiply, and code boundaries blur into an entangled dependency mess.
A multi-module architecture partitions code into decoupled feature and core modules. This enables Gradle to compile independent modules concurrently across CPU cores and leverage remote build caches to skip building unchanged modules entirely.
Modularization also enforces clear architectural boundaries and team ownership, while enabling dynamic feature delivery.
The trade-off is higher operational overhead, requiring dedicated build tooling governance and disciplined dependency management.""",
    "deep_senior_en": """From a staff engineering perspective, the decision to modularize must be driven by data metrics such as developer build wait times and team autonomy rather than architectural dogma.
The most significant tangible benefit of modularization is build pipeline acceleration. In a monolith, changing a single line of code forces Gradle to recompile the entire module and re-run dexing and packaging tasks. In a properly structured multi-module codebase with clean ABI boundaries, modifying an internal implementation class triggers recompilation only for that specific module, allowing all downstream modules to resolve from the local or remote build cache.
However, naive modularization can actually degrade build performance. If an application is split into dozens of fine-grained modules connected in a deep linear chain, Gradle cannot parallelize tasks, and the overhead of configuring dozens of Gradle projects outweighs any compilation savings. Successful modularization requires a wide, shallow dependency graph where independent feature modules depend on shared core libraries without lateral cross-feature coupling.
Furthermore, modularization unlocks modular delivery capabilities on Google Play. Heavy, infrequently used features like identity verification or onboarding flows can be isolated into Dynamic Feature Modules, reducing the initial download APK size for new users and downloading components on-demand.
In conclusion, start with a pragmatic modularized structure or a disciplined package-by-feature monolith, transitioning to full multi-module architectures when team size, build times, or independent release requirements justify the governance cost.""",
    "meta_ar": {
        "id": "SYS-15",
        "questionAr": "قارن بين التصميم أحادي الكتلة (Monolith) والتصميم متعدد الموديولات (Multi-Module) ومتى تختار كلاً منهما؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على تقييم المقايضات الهندسية بين Monolith و Multi-Module وفقاً لحجم الفريق، وسرعة البناء، وتكلفة الإعدادات، واستراتيجيات التوزيع والتحزيم.",
        "why_it_matters_ar": "الاختيار الخاطئ يهدر مئات الساعات؛ فالتقسيم المفرط لمشروع صغير يضيع الوقت في إعدادات Gradle، بينما البقاء في Monolith مع فريق ضخم يوقف الإنتاجية بسبب بطء التجميع وتضارب الدمج المستمر.",
        "worked_example_ar": "مقارنة زمن البناء التزايدي بين التصميمين:\n```text\nMonolith: تعديل سطر واحد -> إعادة تجميع التطبيق بالكامل -> 4 دقائق\nMulti-Module: تعديل سطر في impl -> تجميع الموديول فقط مع كاش للباقي -> 15 ثانية\n```",
        "trade_offs_ar": "التصميم أحادي الكتلة سهل التعديل والتنقل فيه ولا يتطلب معرفة عميقة بـ Gradle، بينما متعدد الموديولات يوفر توازياً في البناء وكاش سحابي واستقلالية للفرق مقابل تعقيد أكبر في إدارة ملفات البناء.",
        "failure_modes_ar": "التقسيم إلى موديولات كثيرة مرتبطة بسلسلة اعتماد خطية عميقة (Deep Dependency Chain) تمنع Gradle من توازي المهام وتجعل البناء أبطأ من المشروع الأحادي.",
        "production_perspective_ar": "في كبرى الشركات، نبدأ بتنظيم المشروع الأحادي وفق حزم الميزات Package-by-feature، وعندما يتجاوز الفريق عشرة مهندسين أو تتجاوز أزمنة البناء خمس دقائق، نبدأ استخراج الموديولات تدريجياً.",
        "how_to_answer_ar": "قارن بين التصميمين عبر محاور واضحة: حجم الفريق، وزمن بناء Gradle، وسهولة إعادة الهيكلة، وتكلفة الصيانة. وضح متى يكون Monolith هو الخيار الذكي، ومتى يصبح الانتقال للـ Multi-Module حتمياً.",
        "talking_points_ar": "كاش Gradle التزايدي والبعيد، وشجرة التبعيات العريضة مقابل العميقة، والميزات الديناميكية Dynamic Features، وتنظيم الحزم Package-by-feature كبديل مبدئي.",
        "follow_ups_ar": "- **المحاور:** \"لماذا قد يؤدي تقسيم المشروع إلى 50 موديول إلى إبطاء البناء بدلاً من تسريعه؟\"\n  **المرشح:** \"إذا كانت الموديولات تعتمد على بعضها في سلسلة خطية متتالية، فإن Gradle لن يتمكن من تجميعها بالتوازي، وستستهلك مرحلة تهيئة مشاريع Gradle (Configuration Phase) وقتاً وذاكرة أكبر من التجميع نفسه.\"\n\n- **المحاور:** \"ما هي الميزات الديناميكية (Dynamic Feature Modules) وكيف يدعمها التصميم المعياري؟\"\n  **المرشح:** \"هي موديولات لا تضمن في حزمة التثبيت المبدئية للـ APK، بل يتم تنزيلها لاحقاً عند طلب المستخدم عبر Play Core API، مما يقلل حجم التطبيق المبدئي بنسبة كبيرة للمستخدمين الجدد.\"",
        "self_check_ar": "هل قارنت بين التصميمين بموضوعية ودون تحيز؟ هل بينت تأثير الهيكلة على كاش Gradle والتوازي؟ وهل وضحت المعايير العملية لاتخاذ القرار؟",
        "references_ar": f"- [Guide to Android App Modularization](https://developer.android.com/topic/modularization) — إرشادات جوجل الرسمية لتقسيم المشروعات.\n- [Gradle Build Cache](https://docs.gradle.org/current/userguide/build_cache.html) — توثيق آليات الكاش والتوازي في Gradle.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "يوفر التصميم أحادي الكتلة بساطة وسرعة فائقة في البداية للفرق الصغيرة، لكنه يسبب بطء التجميع وتداخل الكود مع التوسع. يوفر التصميم متعدد الموديولات تجميعا متوازيا وكاش بناء سريع واستقلالية للفرق وميزات ديناميكية، مقابل تعقيد أكبر في إدارة ملفات Gradle والربط البرمجي.",
        "best_answer_ar": "يعتمد الاختيار بين التطبيق أحادي الكتلة والتطبيق متعدد الموديولات على حجم الفريق الهندسي واحتياجات البناء والتوسع. يناسب التصميم أحادي الكتلة الفرق الناشئة والصغيرة لكونه يزيل تعقيدات إعدادات Gradle ويسهل التعديلات الشاملة دون الحاجة لربط واجهات متبادلة. ولكن مع زيادة حجم الفريق وتجاوز عشرة مهندسين، يصبح التصميم الأحادي عائقا كبيرا بسبب بطء زمن البناء الملحوظ وتكرار تضارب التعديلات وتداخل الاعتماديات. في المقابل، يقسم التصميم متعدد الموديولات الكود إلى وحدات مستقلة للميزات والمكتبات الأساسية، مما يمكن Gradle من تجميع الموديولات غير المترابطة بالتوازي على أنوية المعالج والاستفادة من Build Cache لتخطي بناء الموديولات التي لم تتغير. كما يسمح بتقسيم ملكية الكود بين الفرق بدقة ودعم الميزات الديناميكية، مقابل تكلفة إضافية في إدارة اعتمادات الموديولات ومتابعة إعدادات البناء.",
        "deep_answer_ar": "على المستوى الهندسي المتقدم، يجب أن تستند قرارات التقسيم إلى مقاييس دقيقة تشمل زمن انتظار المطورين للبناء ومستوى استقلالية الفرق وليس مجرد مواكبة الأنماط الشائعة. تكمن الفائدة الجوهرية للتقسيم في تسريع البناء اليومي، ففي المشروع الأحادي يؤدي تعديل سطر واحد لإعادة تجميع الكود كاملا وإعادة عمليات Dexing والتحزيم، بينما في النظام متعدد الموديولات ذي الحدود النظيفة، يقتصر التجميع على الموديول المعدل مع سحب باقي الوحدات من الكاش المحلي أو السحابي. ومع ذلك، قد يؤدي التقسيم العشوائي إلى نتيجة عكسية وإبطاء البناء إذا تم إنشاء موديولات في سلاسل اعتماد خطية عميقة تمنع التوازي وتزيد من عبء تهيئة مشاريع Gradle واستهلاك ذاكرة خوادم CI. التصميم الأمثل يعتمد على رسم شجري عريض وقليل العمق تعتمد فيه الميزات أفقيا على موديولات أساسية دون تداخل جانبي بين الميزات المختلفة. يتيح التقسيم المعياري ميزات إنتاجية متقدمة مثل Dynamic Feature Modules لتنزيل الأجزاء الثقيلة نادرة الاستخدام عبر Google Play Core عند طلبها فقط، مما يقلل حجم حزمة التحميل الأولية للمستخدمين بنسبة ملحوظة، ويسمح للفرق بإطلاق تحديثات مستقلة لميزاتها دون المساس بباقي أجزاء التطبيق. وأخيرا، يساعد عزل موديولات الميزات في تسريع مراجعات الكود البرمجي وتقليل مساحة الصراع بين المهندسين، مع إمكانية مشاركة الموديولات الأساسية عبر عدة تطبيقات تابعة لنفس المؤسسة بسهولة."
    }
}

# ==========================================
# SYS-16: Compare simple MVVM and Clean Architecture for different app sizes.
# ==========================================
DATA["SYS-16"] = {
    "concept_en": """Selecting between pragmatic MVVM (Model-View-ViewModel with Repository) and comprehensive Clean Architecture (incorporating explicit Domain UseCases, independent domain entities, and strict dependency inversion) is a foundational system design decision. Simple MVVM establishes a direct, three-tier architecture: the UI observes StateFlow from a ViewModel, which directly invokes Repository methods to coordinate local Room databases and remote Retrofit APIs. For small-to-medium applications and content-driven products, this architecture provides exceptional developer velocity, minimal boilerplate, and sufficient testability. However, as business logic grows complex—spanning multiple repositories, validation engines, and business policy rules—ViewModels in simple MVVM become bloated god objects. Clean Architecture resolves this by inserting an explicit Domain layer between UI and Data layers. UseCases encapsulate isolated business operations, enabling independent testing, cross-feature reusability, and clean separation between business logic and UI presentation state.""",
    "walkthrough_en": """Contrasting Pass-Through UseCases with Meaningful Clean Architecture UseCases:
```kotlin
// ❌ Anti-Pattern: Anemic Pass-Through UseCase adding boilerplate without value
// This adds indirection without solving any architectural problem in simple CRUD apps.
class GetUserProfileUseCase @Inject constructor(
    private val userRepository: UserRepository
) {
    suspend operator fun invoke(userId: String): UserProfile = userRepository.getUserProfile(userId)
}

// ✅ Meaningful Clean Architecture UseCase: Orchestrating multiple domain policies
// Coordinates multiple repositories, validates domain rules, and logs business telemetry.
class PlaceOrderUseCase @Inject constructor(
    private val cartRepository: CartRepository,
    private val orderRepository: OrderRepository,
    private val paymentRepository: PaymentRepository,
    private val analyticsTracker: AnalyticsTracker
) {
    suspend operator fun invoke(cartId: String, paymentMethodId: String): Result<OrderConfirmation> {
        val cart = cartRepository.getCart(cartId) ?: return Result.failure(IllegalStateException("Cart not found"))
        if (cart.items.isEmpty()) return Result.failure(IllegalStateException("Cart cannot be empty"))

        // Validate business policy constraint
        val orderAmount = cart.calculateTotal()
        if (orderAmount <= 0) return Result.failure(IllegalStateException("Invalid order total"))

        return try {
            val paymentReceipt = paymentRepository.charge(paymentMethodId, orderAmount)
            val order = orderRepository.submitOrder(cart, paymentReceipt.transactionId)
            cartRepository.clearCart(cartId)
            analyticsTracker.logOrderPlaced(order.orderId, orderAmount)
            Result.success(order)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```""",
    "short_en": """Simple MVVM provides high development velocity and minimal boilerplate for small to medium apps by connecting ViewModels directly to Repositories. Clean Architecture introduces an explicit UseCase domain layer that is justified when complex business rules orchestrate multiple repositories, require isolated testing, or must be shared across platforms.""",
    "structured_en": """Choosing between simple MVVM and Clean Architecture depends on business logic complexity and long-term maintainability needs.
Simple MVVM pairs a presentation layer with a repository layer. The ViewModel directly coordinates data loading from repositories and maps outcomes into UI state. For most small to medium applications, this pattern provides the ideal balance of fast delivery, readable code, and easy testing without unnecessary indirection.
However, when business rules become intricate, placing orchestration logic directly inside ViewModels causes class bloat and duplicates logic across different screens.
Clean Architecture introduces an explicit domain layer between presentation and data.
UseCases encapsulate singular business actions, coordinating multiple repositories, enforcing validation policies, and maintaining pure business rules independent of the Android framework.
We avoid anemic pass-through UseCases that merely forward calls to a single repository method, adopting UseCases only when real business orchestration or multi-repository coordination exists.""",
    "deep_senior_en": """From a staff engineering perspective, the chief hazard of Clean Architecture in mobile development is dogmatic over-engineering.
Many teams enforce a rigid rule requiring every single repository method to be wrapped in a corresponding UseCase. This creates anemic pass-through classes that add hundreds of boilerplate files, complicate dependency injection graphs, and inflate navigation traces without providing any architectural value. In a pragmatic enterprise architecture, ViewModels are permitted to query repositories directly for simple read-only queries or straightforward pagination streams.
UseCases earn their place when business policies require cross-repository orchestration, transaction coordination, or complex domain validation. For instance, in an e-commerce checkout flow, a PlaceOrderUseCase coordinates cart validation, inventory reservations, payment charging, and order placement. Encapsulating this workflow in a dedicated UseCase ensures that the exact same business logic can be invoked from a standard checkout screen, a quick-buy widget, or a deep-link shortcut without duplicating a single line of business policy.
Clean Architecture also delivers immense value when supporting Kotlin Multiplatform (KMP). By keeping the domain layer entirely pure Kotlin without Android framework imports, the exact same UseCases, validation engines, and business state machines can be compiled directly for both Android and iOS targets.
In conclusion, teams should default to pragmatic MVVM with clean repositories, introducing domain UseCases selectively when business complexity, multi-repository coordination, or cross-platform code sharing genuinely demands it.""",
    "meta_ar": {
        "id": "SYS-16",
        "questionAr": "قارن بين نمط MVVM البسيط ومعمارية Clean Architecture وفقاً لحجم التطبيق وتعقيد منطق الأعمال؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على اختيار المعمارية الملائمة لحجم التطبيق، والموازنة بين سرعة الإنتاج والتعقيد الهندسي، وتمييز حالات الاستخدام الحقيقية لـ UseCases مقابل الحالات الوهمية.",
        "why_it_matters_ar": "الإفراط الهندسي بإضافة UseCase لكل استدعاء بسيط يغرق المشروع في كود نمطي بلا قيمة، بينما إهمال Clean Architecture في التطبيقات المعقدة يحول الـ ViewModels إلى كائنات ضخمة غير قابلة للاختبار.",
        "worked_example_ar": "تجنب فخ الـ Pass-Through UseCase:\n```kotlin\n// ❌ UseCase وهمي لا يفعل شيئاً سوى التمرير:\nclass GetUser(val repo: UserRepo) { suspend operator fun invoke(id: String) = repo.getUser(id) }\n// ✅ ViewModel يستدعي المستودع مباشرة لعمليات القراءة البسيطة دون وسيط فارغ\n```",
        "trade_offs_ar": "نمط MVVM البسيط يوفر سرعة قصوى وكوداً رشيقاً ومباشراً للمشاريع الناشئة، بينما Clean Architecture تعزل قواعد الأعمال وتسهل مشاركة الكود في Kotlin Multiplatform مقابل طبقات إضافية ومزيد من ملفات التحويل.",
        "failure_modes_ar": "تحويل Clean Architecture إلى كابوس صيانة عبر إنشاء UseCase فارغ لكل دالة في المستودع، أو تسريب تفاصيل نظام أندرويد كالـ Context أو كائنات الـ Framework إلى طبقة الدومين النقية.",
        "production_perspective_ar": "في المشروعات الواقعية، نتبع نهجاً متوازناً: تتصل الـ ViewModels بالمستودعات مباشرة في عمليات القراءة البسيطة والـ Paging، بينما ننشئ UseCase فقط للعمليات التي تشمل عدة مستودعات أو قواعد تحقق حرجة.",
        "how_to_answer_ar": "ابدأ بشرح هيكل MVVM المباشر ولماذا يناسب معظم التطبيقات. ثم اشرح متى ولماذا تبرر الحاجة لطبقة الدومين والـ UseCases. انتقد التطبيق الأعمى للـ Clean Architecture ووضح فخ الـ Pass-Through UseCases وميزة دعم KMP.",
        "talking_points_ar": "فخ الـ Anemic Pass-Through UseCases، وتنسيق العمليات المعقدة، ودعم Kotlin Multiplatform (KMP)، وتجنب الـ God ViewModels، واختبار طبقة الدومين بدون أطر عمل.",
        "follow_ups_ar": "- **المحاور:** \"متى يصبح إنشاء UseCase أمراً إلزامياً ومبرراً معمارياً؟\"\n  **المرشح:** \"عندما ينسق UseCase منطق أعمال يجمع عدة مستودعات مثل خطوة إتمام الطلب التي تتطلب فحص السلة وحجز المخزون وخصم المبلغ من بوابتين مختلفتين، أو عند الحاجة لإعادة استخدام نفس المنطق في ودجات وشاشات متعددة.\"\n\n- **المحاور:** \"كيف تفيد Clean Architecture عند الانتقال إلى تقنية Kotlin Multiplatform (KMP)؟\"\n  **المرشح:** \"لأن طبقة الدومين تكون مكتوبة بلغة كوتلن الصافية تماماً دون أي استيراد لمكتبات أندرويد، مما يتيح تجميع نفس الـ UseCases ونماذج الأعمال ونقلها للعمل مباشرة على نظام iOS دون تعديل حرف واحد.\"",
        "self_check_ar": "هل وضحت الفارق الجوهري بين النمطين؟ هل انتقدت فخ الـ Pass-Through UseCases؟ وهل بينت متى يصبح إدخال طبقة الدومين قراراً هندسياً سليماً؟",
        "references_ar": f"- [Guide to App Architecture: Domain Layer](https://developer.android.com/topic/architecture/domain-layer) — دليل جوجل الرسمي لطبقة الدومين والـ UseCases.\n- [Clean Architecture (Uncle Bob)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html) — المفهوم الأصلي لمعمارية الكود النظيف.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "يوفر نمط MVVM البسيط سرعة تطوير عالية وكودا مختصرا للتطبيقات الصغيرة والمتوسطة عبر ربط ViewModel بالمستودع مباشرة. تقدم معمارية Clean Architecture طبقة UseCases وسيطة تصبح ضرورية عند تعقد منطق الأعمال وتنسيق عدة مستودعات والحاجة لاختبارات مجردة ومشاركة الكود عبر المنصات.",
        "best_answer_ar": "يعتمد الاختيار بين نمط MVVM البسيط ومعمارية Clean Architecture على مدى تعقيد منطق الأعمال وحجم الفريق على المدى الطويل. في نمط MVVM البسيط، تتصل ViewModels بالمستودعات مباشرة لتنسيق جلب البيانات وتحديث واجهة المستخدم، وهو خيار ممتاز لمعظم التطبيقات المتوسطة لتوفيره سرعة إنتاجية عالية دون طبقات وسيطة لا داعي لها. ولكن عندما يزداد تعقيد التطبيق وتتشابك قواعد الأعمال، يؤدي وضع منطق المعالجة داخل الـ ViewModels إلى تضخمها وتكرار نفس المنطق عبر شاشات متعددة. تقدم Clean Architecture طبقة دومين صريحة تحتوي على UseCases يمثل كل منها عملية أعمال محددة تعزل القواعد الحسابية وتنسق العمليات بين عدة مستودعات بمعزل عن أطر العمل. نتجنب تماما فخ إنشاء UseCases وهمية لا تفعل شيئا سوى تمرير الاستدعاء لمستودع واحد، ونقتصر في استخدامها على الأماكن التي تتطلب منطق أعمال فعلي.",
        "deep_answer_ar": "على المستوى الهندسي المتقدم، يمثل الإفراط الأعمى في تطبيق Clean Architecture خطرا كبيرا على إنتاجية الفريق ووضوح الكود البرمجي وصيانته. تلزم بعض الفرق مطوريها بوضع UseCase لكل استدعاء بسيط، مما يولد مئات الكلاسات الفارغة التي لا تفعل سوى تمرير البيانات للمستودع، مما يزيد من تعقيد شجرة حقن الاعتماديات وتضخم زمن البناء دون أي فائدة حقيقية. في المعمارية الواقعية المتوازنة، يسمح للـ ViewModel بالتواصل المباشر مع المستودع في عمليات القراءة البسيطة وتدفقات الصفحات، مما يوفر جهدا كبيرا ويحافظ على رشاقة الكود. تتجلى القيمة الحقيقية للـ UseCases عند تنسيق عمليات تشمل عدة مستودعات مثل مسار الدفع الذي يتطلب التحقق من السلة وحجز المخزون وخصم المبلغ وتسجيل الطلب وإرسال تحليلات الشراء، حيث يتيح عزلها في UseCase إعادة استخدام نفس المنطق من الشاشة العادية أو ودجات النظام دون تكرار أي سطر برمجي. بالإضافة إلى ذلك، توفر Clean Architecture ميزة استثنائية عند التوجه نحو Kotlin Multiplatform، حيث تظل طبقة الدومين خالية تماما من أي اعتماديات على نظام أندرويد، مما يتيح تشغيل نفس منطق الأعمال والتحقق وآلات الحالات على أندرويد و iOS معا ومشاركة كود الأعمال بنسبة مائة بالمائة. وأخيرا، يسمح هذا العزل باختبار منطق الأعمال المجرد بسرعات فائقة في اختبارات JVM العادية دون الحاجة لتشغيل محاكي الأندرويد، مما يوفر ساعات طويلة من وقت البناء والاختبار للمطورين."
    }
}

# ==========================================
# Validation and Execution Functions
# ==========================================
def validate_words():
    errors = []
    for qid, d in sorted(DATA.items()):
        meta = d["meta_ar"]
        # English counts
        s_en = len(d["short_en"].split())
        st_en = len(d["structured_en"].split())
        d_en = len(d["deep_senior_en"].split())

        # Arabic counts
        q_ar = len(meta["quick_answer_ar"].split())
        b_ar = len(meta["best_answer_ar"].split())
        d_ar = len(meta["deep_answer_ar"].split())

        print(f"{qid}: en_s={s_en}, en_st={st_en}, en_d={d_en} | ar_q={q_ar}, ar_b={b_ar}, ar_d={d_ar}")

        # English checks
        if not (35 <= s_en <= 110):
            errors.append(f"{qid} short_en out of range: {s_en} (35-110)")
        if not (100 <= st_en <= 280):
            errors.append(f"{qid} structured_en out of range: {st_en} (100-280)")
        if not (200 <= d_en <= 650):
            errors.append(f"{qid} deep_senior_en out of range: {d_en} (200-650)")

        # Arabic checks
        if not (35 <= q_ar <= 110):
            errors.append(f"{qid} quick_answer_ar out of range: {q_ar} (35-110)")
        if not (90 <= b_ar <= 280):
            errors.append(f"{qid} best_answer_ar out of range: {b_ar} (90-280)")
        if not (180 <= d_ar <= 650):
            errors.append(f"{qid} deep_answer_ar out of range: {d_ar} (180-650)")

    if errors:
        print("\nPre-validation word count checks failed! Fix counts before updating files.")
        for e in errors:
            print(f"  ❌ {e}")
        sys.exit(1)
    else:
        print("\nPre-validation word count checks passed! Updating canonical questions...")

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

    ee.save_topic_metadata("sys_09_16", topic_meta)
    ee.merge_all_metadata()

    for qid in sorted(DATA.keys()):
        errs = ee.validate_question(qid)
        if errs:
            print(f"Errors in {qid}:")
            for e in errs:
                print(f"  ❌ {e}")
            sys.exit(1)

    print("\nAll 8 SYS questions (SYS-09 to SYS-16) successfully elevated and passed validation!\n")

if __name__ == "__main__":
    apply_elevations()
