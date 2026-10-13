#!/usr/bin/env python3
"""Generator for SYS-09 through SYS-16 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "sys.json"

SYS_09_16 = [
    {
        "id": "SYS-09",
        "arabic_explanation": (
            "كيف تصمم بنية المراقبة التشغيلية (Analytics, Logs, Metrics, and Crash Reporting) لتطبيق ضخم دون التأثير على الأداء والبطارية؟\n\n"
            "1. الركائز الأربع للمراقبة التشغيلية (Observability Pillars):\n   - **Crash Reporting (Crashlytics / Sentry)**: التقاط الـ Uncaught Exceptions، وحفظ الـ Breadcrumbs (آخر 30 إجراء قام به المستخدم قبل السقوط)، وربط ملف الـ `mapping.txt` لفك التشفير.\n   - **Analytics Events**: تتبع سلوك المستخدم ومسارات التحويل (Funnels). يجب تجميعها (Batching) وإرسالها دورياً في الخلفية.\n   - **Application Performance Monitoring (APM)**: قياس زمن الـ Cold Start، ومعدل سقوط الإطارات (Jank / Slow Frames عبر مكتبة `androidx.metrics.performance:jankstats`)، ومعدل استجابة الشبكة.\n   - **Operational Logging**: تسجيل السجلات التشغيلية محلياً مع تطهير كامل من البيانات الحساسة (PII Scrubbing).\n\n"
            "2. تصميم محرك الـ Analytics الذاتي (Event Ingestion Engine):\n   - **التخزين المؤقت على القرص (Disk-Backed Queue)**: حفظ الأحداث في جدول SQLite أو ملفات محلية فور توليدها، لضمان عدم ضياعها في حال إغلاق التطبيق أو انقطاع الإنترنت.\n   - **الإرسال المجمع (Batching & Backoff)**: إرسال الأحداث في حزم (مثلاً كل 30 حدثاً أو كل دقيقتين) لتوفير راديو الشبكة والبطارية، مع تفويض الإرسال لـ WorkManager إذا كان التطبيق في الخلفية.\n\n"
            "3. الامتثال والخصوصية (Privacy & Compliance):\n   - حظر طباعة الـ PII (بطاقات ائتمانية، إيميلات، أرقام هواتف) وتطهير السجلات برمجياً قبل الإرسال."
        ),
        "practical_walkthrough": (
            "تصميم محرك Analytics مجمع مع طابور تخزين محلي وتطهير البيانات الحساسة:\n"
            "```kotlin\n"
            "class AnalyticsEventDispatcher @Inject constructor(\n"
            "    private val eventQueueDao: AnalyticsDao,\n"
            "    private val analyticsApi: AnalyticsApiService\n"
            ") {\n"
            "    private val eventChannel = Channel<AnalyticsEvent>(Channel.BUFFERED)\n"
            "    private val BATCH_SIZE = 25\n"
            "\n"
            "    init {\n"
            "        startBatchProcessor()\n"
            "    }\n"
            "\n"
            "    fun trackEvent(name: String, params: Map<String, Any> = emptyMap()) {\n"
            "        // 1. تطهير البيانات وحجب أي حقول حساسة:\n"
            "        val sanitizedParams = params.filterKeys { !it.contains(\"password\", true) && !it.contains(\"card\", true) }\n"
            "        val event = AnalyticsEvent(name = name, parameters = sanitizedParams, timestamp = System.currentTimeMillis())\n"
            "        eventChannel.trySend(event)\n"
            "    }\n"
            "\n"
            "    private fun startBatchProcessor() {\n"
            "        CoroutineScope(Dispatchers.IO).launch {\n"
            "            val buffer = mutableListOf<AnalyticsEvent>()\n"
            "            while (isActive) {\n"
            "                // 2. تجميع الأحداث حتى اكتمال الـ Batch أو انقضاء مهلة زمنية\n"
            "                val event = withTimeoutOrNull(30_000L) { eventChannel.receive() }\n"
            "                if (event != null) buffer.add(event)\n"
            "                \n"
            "                if (buffer.size >= BATCH_SIZE || (buffer.isNotEmpty() && event == null)) {\n"
            "                    try {\n"
            "                        analyticsApi.sendBatch(buffer.toList())\n"
            "                        buffer.clear()\n"
            "                    } catch (e: Exception) {\n"
            "                        // في حال فشل الشبكة: حفظ الأحداث في قاعدة البيانات المحلية لإرسالها لاحقاً\n"
            "                        eventQueueDao.insertAll(buffer.map { it.toEntity() })\n"
            "                        buffer.clear()\n"
            "                    }\n"
            "                }\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Design observability across crashes, analytics, metrics, and logs using disk-backed batching queues to conserve battery and survive process death. Enforce strict PII scrubbing before storage, track cold start and frame-drop metrics via JankStats, and upload crash breadcrumbs and logs asynchronously.",
        "best_answer": (
            "A unified observability architecture balances real-time diagnostic visibility against device battery and network overhead:\n\n"
            "1. **Crash Reporting & Diagnostic Breadcrumbs**:\n"
            "   - Integrate crash SDKs (Crashlytics/Sentry) configured with automated deobfuscation (`mapping.txt`).\n   - Maintain a circular buffer of the last 30 user actions (screen views, network status transitions, critical user clicks) recorded as diagnostic breadcrumbs attached automatically to unhandled exceptions.\n\n"
            "2. **Disk-Backed Event Ingestion Pipeline**:\n"
            "   - Dispatching network requests for individual analytics events drains battery radios rapidly. Ingest events into an in-memory queue that flushes to a local SQLite buffer.\n   - Batch-upload events periodically (e.g., every 30 events or 60 seconds) with GZIP compression, deferring large backlog flushes to Wi-Fi/charging via WorkManager.\n\n"
            "3. **APM & User Experience Telemetry**:\n"
            "   - Measure application launch latency (Time to Initial Display & Time to Full Display via `reportFullyDrawn()`).\n   - Instrument UI rendering using AndroidX `JankStats` to track jank percentages across critical scrollable surfaces.\n\n"
            "4. **PII Scrubbing Boundary**:\n"
            "   - Enforce an architectural sanitizer that intercepts all logs and analytics payloads, redacting PAN numbers, email addresses, and auth headers before persistence."
        ),
        "deep_answer": (
            "From a staff-level infrastructure perspective, mobile observability requires managing high-volume data streams and ANR detection:\n\n"
            "1. **Application Not Responding (ANR) Forensics**: Standard crash handlers do not capture ANRs because the main thread is blocked. Modern architectures use `ApplicationExitInfo` (introduced in Android 11) to inspect system tombstone traces and exit reasons (`REASON_ANR`, `REASON_CRASH_NATIVE`, `REASON_LOW_MEMORY`) upon the subsequent app cold start.\n\n"
            "2. **Adaptive Dynamic Sampling**: High-volume telemetry (e.g., measuring individual HTTP call latencies) can overwhelm backend ingestion servers at scale. Implement server-configurable sampling rates via feature flags (e.g. logging network performance traces for 1% of users, while capturing 100% of crashes and financial failure events).\n\n"
            "3. **Zero-Overhead Debug vs. Release Logging**: Use Timber with separate tree implementations: a `DebugTree` logging verbose output in development, and a stripped release pipeline where R8 removes `Log.v` and `Log.d` bytecodes entirely, routing only critical error reports to the telemetry queue."
        ),
        "follow_ups": [
            {
                "question": "What is reportFullyDrawn() and why is it preferred over Activity onCreate timing?",
                "answer": "reportFullyDrawn() indicates when the app is completely interactive with all async network data rendered, whereas onCreate only measures initial framework view attachment."
            },
            {
                "question": "How do you detect memory leaks in production without crashing user apps?",
                "answer": "Track aggregate heap metrics and OEM OOM exit rates via ApplicationExitInfo; avoid running heavy debug tools like LeakCanary in production builds."
            }
        ]
    },
    {
        "id": "SYS-10",
        "arabic_explanation": (
            "كيف تقوم بنمذجة حالات التطبيق وتدفقات الشاشات باستخدام آلة حالات صريحة (Explicit State Machine) لمنع الحالات غير الصالحة؟\n\n"
            "1. مخاطر الـ State Modeling العشوائي (Boolean Hell):\n   - كثير من المطورين يعرّفون الـ State بمجموعة من المتغيرات المنفصلة:\n     `var isLoading: Boolean = false`, `var isError: Boolean = false`, `var data: List<Item>? = null`.\n   - هذا يؤدي إلى **حالات متناقضة وغير منطقية مستحيلة هندسياً**! مثل: `isLoading = true` و `isError = true` في نفس الوقت، أو وجود بيانات مع خطأ فادح!\n\n"
            "2. آلة الحالات الصريحة (Finite State Machine - FSM):\n   - **Sealed Interfaces للحالات**: تمثيل كل حالة ممكنة بكلاس صريح ومغلق:\n     `sealed interface UiState { object Loading; data class Success(val items); data class Error(val msg) }`.\n   - **Sealed Interfaces للأحداث (User Actions & System Events)**: تمثيل كل حدث يغير الحالة:\n     `sealed interface UiEvent { object Retry; data class SelectItem(val id); object Refresh }`.\n   - **دالة التحويل النقية (State Reducer)**: دالة تأخذ الحالة الحالية والحدث وتعيد الحالة الجديدة فقط: `reduce(currentState, event): UiState`.\n\n"
            "3. فصل الآثار الجانبية (Side-Effects Isolation):\n   - العمليات غير النقية (Navigation, Showing Snackbars, Triggering Haptics) لا توضع داخل الـ State، بل تُعامل كـ `SharedFlow` أو `Channel` للأحداث الفردية (One-Off Side Effects) لمنع إعادة تنفيذها عند تدوير الشاشة."
        ),
        "practical_walkthrough": (
            "تنفيذ State Machine صريحة ونقية مع MVI لتدفق دفع معقد ومنع الحالات المتضاربة:\n"
            "```kotlin\n"
            "// 1. نمذجة الحالات الممكنة حصرياً (Impossible States are Unrepresentable):\n"
            "sealed interface CheckoutState {\n"
            "    object Idle : CheckoutState\n"
            "    object ProcessingPayment : CheckoutState\n"
            "    data class AwaitingOtpVerification(val transactionId: String) : CheckoutState\n"
            "    data class Completed(val receiptNumber: String) : CheckoutState\n"
            "    data class Failed(val reason: String, val canRetry: Boolean) : CheckoutState\n"
            "}\n"
            "\n"
            "// 2. نمذجة الأحداث الصريحة:\n"
            "sealed interface CheckoutEvent {\n"
            "    data class SubmitPayment(val cardToken: String) : CheckoutEvent\n"
            "    data class VerifyOtp(val code: String) : CheckoutEvent\n"
            "    object Retry : CheckoutEvent\n"
            "}\n"
            "\n"
            "// 3. محرك الـ State Machine داخل ViewModel:\n"
            "class CheckoutStateMachineViewModel @Inject constructor(\n"
            "    private val paymentRepository: PaymentRepository\n"
            ") : ViewModel() {\n"
            "    private val _state = MutableStateFlow<CheckoutState>(CheckoutState.Idle)\n"
            "    val state: StateFlow<CheckoutState> = _state.asStateFlow()\n"
            "\n"
            "    fun onEvent(event: CheckoutEvent) {\n"
            "        val currentState = _state.value\n"
            "        viewModelScope.launch {\n"
            "            when (event) {\n"
            "                is CheckoutEvent.SubmitPayment -> {\n"
            "                    if (currentState is CheckoutState.Idle || currentState is CheckoutState.Failed) {\n"
            "                        _state.value = CheckoutState.ProcessingPayment\n"
            "                        val result = paymentRepository.process(event.cardToken)\n"
            "                        _state.value = when (result) {\n"
            "                            is PaymentResult.RequiresOtp -> CheckoutState.AwaitingOtpVerification(result.txId)\n"
            "                            is PaymentResult.Success -> CheckoutState.Completed(result.receipt)\n"
            "                            is PaymentResult.Error -> CheckoutState.Failed(result.message, canRetry = true)\n"
            "                        }\n"
            "                    }\n"
            "                }\n"
            "                is CheckoutEvent.VerifyOtp -> {\n"
            "                    if (currentState is CheckoutState.AwaitingOtpVerification) {\n"
            "                        _state.value = CheckoutState.ProcessingPayment\n"
            "                        // تنفيذ التحقق وتحديث الحالة\n"
            "                    }\n"
            "                }\n"
            "                is CheckoutEvent.Retry -> {\n"
            "                    if (currentState is CheckoutState.Failed && currentState.canRetry) {\n"
            "                        _state.value = CheckoutState.Idle\n"
            "                    }\n"
            "                }\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Model states and transitions using an explicit finite state machine with Kotlin sealed interfaces to make invalid states unrepresentable. Enforce transitions through pure reducer functions driven by typed events, and isolate transient one-off side effects like navigation and snackbars from persistent view state.",
        "best_answer": (
            "Modeling complex UI and domain journeys using explicit State Machines eliminates the 'boolean flag explosion' where disparate variables create invalid state permutations:\n\n"
            "1. **Making Invalid States Unrepresentable**:\n"
            "   - Replace scattered variables (`var isLoading`, `var isError`, `var data`) with a single immutable sealed hierarchy (`Loading`, `Empty`, `Content`, `Error`). A screen cannot be simultaneously in `Loading` and `Error` because the type system strictly forbids it.\n\n"
            "2. **Typed Events as Transition Triggers**:\n"
            "   - Define a sealed interface representing all valid inputs (`UiEvent`). The UI emits intent events into the ViewModel without directly mutating data.\n\n"
            "3. **Deterministic State Transitions (Reducers)**:\n"
            "   - Transition logic follows a pure functional pattern: `f(State, Event) -> State`. Disallowed transitions are ignored or logged as violations, protecting flows like payments from duplicate executions during transitions.\n\n"
            "4. **Isolating Side Effects**:\n"
            "   - Decouple continuous UI state (rendered by Compose) from discrete one-off side effects (navigation commands, analytics triggers, toast messages). Channel side effects through a buffered `Channel<UiEffect>` consumed once via `LaunchedEffect`."
        ),
        "deep_answer": (
            "From an architectural rigor standpoint, finite state machines provide unparalleled testability and auditability:\n\n"
            "1. **Exhaustive Unit Test Coverage**: Because state transitions are modeled as deterministic functions taking `(State, Event)`, unit testing requires zero mocking of Android framework components. You can assert that submitting `SubmitPayment` while in `ProcessingPayment` state is a no-op, preventing double-submission bugs with simple pure unit tests.\n\n"
            "2. **State Restoration & Process Death**: Explicit state machines serialize seamlessly into Android `SavedStateHandle`. If the state machine is composed of parcelable primitives or identifiers, restoring the exact step of a multi-stage KYC or checkout flow post-process death requires deserializing a single state token.\n\n"
            "3. **Hierarchical State Machines (Statecharts)**: For massive multi-step workflows (e.g., identity verification with camera capture, document review, and address confirmation), nest smaller child state machines within a parent coordinator state machine, ensuring sub-flow encapsulation."
        ),
        "follow_ups": [
            {
                "question": "Why should one-off UI events not be stored directly in StateFlow state?",
                "answer": "StateFlow retains its latest value; if an event like ShowSnackbar is stored in state, re-subscribing on screen rotation re-emits and displays the snackbar again."
            },
            {
                "question": "What is the difference between MVI and traditional MVVM?",
                "answer": "MVI enforces a single immutable StateFlow and unidirectional event-driven reducers, whereas traditional MVVM often exposes multiple independent LiveData/StateFlow streams."
            }
        ]
    },
    {
        "id": "SYS-11",
        "arabic_explanation": (
            "كيف تتعامل مع التزامن (Concurrency)، فترات الانتظار (Timeouts)، إعادة المحاولة (Retries)، وعدم التكرار (Idempotency) في بيئات الموبايل؟\n\n"
            "1. إدارة التزامن (Concurrency Management via Coroutines):\n   - **تجنب الـ Shared Mutable State**: استخدام `StateFlow` و `SharedFlow` غير القابلة للتعديل خارج الـ ViewModel.\n   - **Mutex لحماية العمليات الحرجة**: منع تشغيل عمليتين حساستين معاً (مثل محاولة تجديد التوكن مرتين أو دفع فاتورة مرتين) باستخدام `kotlinx.coroutines.sync.Mutex`.\n   - **إلغاء العمليات السابقة (Canceling Stale Jobs)**: استخدام `collectLatest` أو إلغاء الـ `Job` السابق عند قيام المستخدم بالبحث المتكرر لمنع إهدار الموارد وعرض نتائج قديمة (Race Conditions).\n\n"
            "2. فترات الانتظار (Timeouts):\n   - تحديد فترات انتظار دقيقة ومخصصة على مستوى OkHttp: `connectTimeout` (10s), `readTimeout` (15s), `writeTimeout` (15s).\n   - استخدام `withTimeout(duration) { ... }` في Coroutines للعمليات التي تعتمد على معالجة محلية أو تدفقات بيانات غير منتهية.\n\n"
            "3. استراتيجية إعادة المحاولة الذكية (Exponential Backoff with Full Jitter):\n   - **الكارثة**: إعادة المحاولة فوراً وبشكل ثابت (مثل كل ثانية) يؤدي إلى هجوم حرمان خدمة ذاتي (Self-inflicted DDoS) على السيرفر عند تعافيه!\n   - **الحل الصحيح**: تأخير تضاعفي مع عشوائية كاملة:\n     `delay = min(maxDelay, baseDelay * (2 ^ attempt)) + Random(0, jitter)`.\n\n"
            "4. عدم التكرار (Idempotency):\n   - العمليات غير القابلة للتكرار بطبيعتها (مثل POST لإنشاء طلب أو تحويل أموال) يجب أن تُرفق بـ `Idempotency-Key` (UUID) منشأ في العميل لضمان معالجتها مرة واحدة فقط على السيرفر."
        ),
        "practical_walkthrough": (
            "تنفيذ دالة تنفيذ شبكي مرنة ومقاومة للأخطاء مع Exponential Backoff و Jitter ومعالجة الـ Idempotency:\n"
            "```kotlin\n"
            "suspend fun <T> executeWithRetry(\n"
            "    maxRetries: Int = 3,\n"
            "    baseDelayMs: Long = 1000L,\n"
            "    maxDelayMs: Long = 10000L,\n"
            "    block: suspend () -> T\n"
            "): Result<T> {\n"
            "    var currentAttempt = 0\n"
            "    while (currentAttempt < maxRetries) {\n"
            "        try {\n"
            "            return Result.success(block())\n"
            "        } catch (e: IOException) {\n"
            "            currentAttempt++\n"
            "            if (currentAttempt >= maxRetries) return Result.failure(e)\n"
            "            \n"
            "            // حساب Exponential Backoff مع Full Jitter لمنع الـ Thundering Herd:\n"
            "            val exponential = (baseDelayMs * (1 shl (currentAttempt - 1))).coerceAtMost(maxDelayMs)\n"
            "            val jitter = Random.nextLong(0, exponential)\n"
            "            delay(jitter)\n"
            "        } catch (e: Exception) {\n"
            "            // الأخطاء غير القابلة للتعافي (مثل 400 Bad Request أو 403 Forbidden) لا يُعاد محاولتها\n"
            "            return Result.failure(e)\n"
            "        }\n"
            "    }\n"
            "    return Result.failure(IllegalStateException(\"Exhausted retries\"))\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Manage concurrency via structured coroutines and Mutex locks, enforce fine-grained network and coroutine timeouts, apply exponential backoff with full jitter to avoid thundering-herd server spikes, and use client-generated UUID idempotency keys to guarantee at-most-once mutation semantics.",
        "best_answer": (
            "Building resilient network and data layers requires coordinating concurrency, time bounds, and retry semantics:\n\n"
            "1. **Structured Concurrency & Race Conditions**:\n"
            "   - Scope coroutines strictly to their lifecycle owners (`viewModelScope`, WorkManager). Avoid unstructured `GlobalScope`.\n   - Eliminate shared mutable state using atomic primitives or `Mutex`. For search autocomplete or rapid filter clicks, use `collectLatest` or cancel active jobs to drop obsolete responses.\n\n"
            "2. **Fine-Grained Timeouts**:\n"
            "   - Configure distinct OkHttp timeouts: short connect timeouts (10s) to detect dead networks rapidly, and appropriate read/write timeouts (15–30s) for payloads. Wrap sensitive domain operations in `withTimeoutOrNull` to guarantee UI unblocking.\n\n"
            "3. **Exponential Backoff with Full Jitter**:\n"
            "   - When an outage occurs, millions of mobile clients retrying at synchronized intervals will overwhelm recovered servers. Calculate delays using exponential backoff randomized with full jitter: `delay = Random(0, base * 2^attempt)`. Never retry non-idempotent 4xx client errors (e.g. 400, 401, 422).\n\n"
            "4. **Idempotency Keys**:\n"
            "   - For state-altering mutations (payments, order creation), attach a client-generated UUID `Idempotency-Key` header. If a network timeout prompts a retry, the backend processes the request safely without duplicating effects."
        ),
        "deep_answer": (
            "From a staff-level systems perspective, retry and concurrency policies must be designed end-to-end:\n\n"
            "1. **The Circuit Breaker Pattern on Mobile**: If network calls repeatedly fail with 503 Service Unavailable or consecutive timeouts, the mobile client should trip a local **Circuit Breaker**. For the next 60 seconds, fail requests immediately with cached error state without hitting the cellular radio, preserving device battery and giving the backend breathing room.\n\n"
            "2. **Safe Idempotent Methods vs. Unsafe Mutations**: RFC 7231 defines GET, PUT, and DELETE as inherently idempotent. Retrying GET or PUT is safe. Retrying POST is hazardous. Explicitly distinguish between safe retry policies (transparently retrying idempotent read queries) and guarded retry policies (requiring user confirmation or idempotency keys for mutations).\n\n"
            "3. **Coroutine Cancellation Cooperativeness**: Ensure custom background loops and heavy data parsing check `isActive` or invoke `ensureActive()`. If a coroutine does not yield, cancellation requests triggered by screen departures or timeouts will be ignored, resulting in leaked background compute."
        ),
        "follow_ups": [
            {
                "question": "What is Full Jitter in retry backoff algorithms?",
                "answer": "Selecting a random delay between 0 and the calculated exponential ceiling, spreading retries evenly across time to prevent clustered spikes."
            },
            {
                "question": "Why should you never retry an HTTP 401 response using a standard retry interceptor?",
                "answer": "401 indicates invalid authentication credentials; retrying without refreshing tokens will fail repeatedly and lock user accounts."
            }
        ]
    },
    {
        "id": "SYS-12",
        "arabic_explanation": (
            "كيف تصمم مكتبة أندرويد (Reusable Android SDK) بواجهة عامة مستقرة (Stable Public API) ومعايير أمان عالية للتوزيع؟\n\n"
            "1. تقليص مساحة السطح العام (Minimizing the Public API Surface):\n   - **قاعدة ذهبية**: كل كلاس أو دالة تجعلها `public` تصبح التزاماً للأبد! اجعل كل شيء `internal` أو `private` افتراضياً.\n   - **إخفاء كود الـ Implementation**: توفير Interfaces عامة فقط وكلاسات Factory أو Entrypoints محدودة (مثل `PaymentSdk.initialize()`).\n   - استخدام أداة **Binary Compatibility Validator (BCV)** في Gradle: تقوم بإنشاء ملف `.dump` بالـ Public API وتفشل الـ Build إذا قام مطور بتغيير أو كسر الـ Binary Compatibility دون زيادة رقم الـ Major Version.\n\n"
            "2. منع تسريب التبعيات الخارجية (No Transitive Dependency Leaks):\n   - **فخ شائع**: استخدام `api(\"com.squareup.retrofit2:retrofit:...\")` في ملف `build.gradle` الخاص بالـ SDK. هذا يسرب Retrofit لتطبيق العميل ويجبره على استخدام نفس الإصدار مما يسبب Dependency Hell وتعارض في الإصدارات!\n   - **الحل**: استخدام `implementation` دائماً للتبعيات الداخلية، وتجنب استخدام كائنات تابعة لمكتبات خارجية في دوال الـ Public API الخاصة بك.\n\n"
            "3. التهيئة السلسة (Frictionless Initialization):\n   - توفير تهيئة آلية خفيفة عبر AndroidX App Startup (`Initializer<T>`) إذا كان الـ SDK لا يتطلب إعدادات خاصة، مع إتاحة دالة تهيئة يدوية صريحة للتحكم في زمن التشغيل."
        ),
        "practical_walkthrough": (
            "تصميم واجهة عامة احترافية للـ SDK مع عزل التنفيذ الداخلي والتهيئة الآمنة:\n"
            "```kotlin\n"
            "// 1. الواجهة العامة المتاحة للمطورين فقط (Public API):\n"
            "interface PaymentSdk {\n"
            "    fun startCheckout(amountCents: Long, currency: String, callback: SdkCallback)\n"
            "    \n"
            "    companion object {\n"
            "        fun create(context: Context, apiKey: String): PaymentSdk {\n"
            "            // إخفاء كلاس التنفيذ الحقيقي تماماً ومنع استدعائه المباشر\n"
            "            return PaymentSdkInternal(context.applicationContext, apiKey)\n"
            "        }\n"
            "    }\n"
            "}\n"
            "\n"
            "interface SdkCallback {\n"
            "    fun onSuccess(transactionId: String)\n"
            "    fun onError(code: Int, message: String)\n"
            "}\n"
            "\n"
            "// 2. الكود الداخلي مغلق تماماً عبر internal لمنع الوصول إليه من خارج موديول الـ SDK:\n"
            "internal class PaymentSdkInternal(\n"
            "    private val context: Context,\n"
            "    private val apiKey: String\n"
            ") : PaymentSdk {\n"
            "    // استخدام OkHttp أو Room داخلياً بدون تسريبها لمستخدم الـ SDK\n"
            "    override fun startCheckout(amountCents: Long, currency: String, callback: SdkCallback) {\n"
            "        // منطق الدفع الداخلي\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Design a reusable SDK by strictly hiding implementation details behind internal modifiers and clean public interfaces, avoiding leaked transitive dependencies via implementation Gradle scopes, validating binary ABI compatibility in CI with BCV, and supporting graceful zero-friction initialization.",
        "best_answer": (
            "Architecting a distributed Android SDK requires strict discipline regarding backward compatibility, dependency isolation, and lifecycle consumption:\n\n"
            "1. **API Surface Minimization**:\n"
            "   - Expose the smallest viable public API surface. Mark all internal ViewModels, utilities, and models with Kotlin's `internal` visibility modifier.\n   - Hide concrete implementations behind stable interfaces instantiated via companion factory methods.\n\n"
            "2. **Preventing Dependency Hell**:\n"
            "   - Never leak internal dependencies into client builds. Use Gradle `implementation` instead of `api` for internal networking (Retrofit/OkHttp) or storage libraries.\n   - If third-party dependencies are required, consider shading/relocating package namespaces using the Shadow Jar plugin to prevent version collision with host apps.\n\n"
            "3. **Binary Compatibility (ABI) Enforcement**:\n"
            "   - Follow Semantic Versioning (SemVer). Integrate Jetpack's **Binary Compatibility Validator (BCV)** plugin into CI. Any breaking signature change (changing return types, adding non-default interface methods) alters the public `.dump` file and breaks CI, preventing accidental runtime crashes in consuming apps.\n\n"
            "4. **Non-Intrusive Lifecycle & Initialization**:\n"
            "   - Avoid heavy blocking work in `Application.onCreate`. Use AndroidX `Initializer` for zero-setup workflows, or provide an explicit `Sdk.initialize(config)` allowing the host app to defer initialization off the critical launch path."
        ),
        "deep_answer": (
            "From an enterprise SDK engineering perspective, public libraries must treat the host application as an unpredictable environment:\n\n"
            "1. **R8/ProGuard Consumer Rules**: Bundle optimized `consumer-rules.pro` files within the AAR. This automatically instructs the consuming app's R8 shrinker which public entry points and serialized DTOs must be retained, preventing host builds from stripping necessary SDK reflection classes.\n\n"
            "2. **Strict Manifest Merging Hygiene**: Audit the SDK's `AndroidManifest.xml`. Never declare aggressive permissions (e.g. `ACCESS_FINE_LOCATION`) inside an SDK manifest unless strictly optional, and avoid defining top-level single-instance activities that alter the host app's back stack.\n\n"
            "3. **Defensive Error Isolation**: Exceptions inside SDK background routines must be caught and returned through typed error callbacks rather than bubbling unhandled to crash the host app process."
        ),
        "follow_ups": [
            {
                "question": "What is the difference between source compatibility and binary compatibility in Kotlin?",
                "answer": "Source compatibility means existing source code recompiles without errors; binary compatibility means already-compiled binaries execute against the new library without NoSuchMethodError."
            },
            {
                "question": "What is the purpose of consumer-rules.pro in an Android library module?",
                "answer": "It bundles ProGuard/R8 rules into the exported AAR that are automatically applied to any application consuming the library."
            }
        ]
    },
    {
        "id": "SYS-13",
        "arabic_explanation": (
            "كيف تدير ترقيات قواعد البيانات (Database Migrations) والتوافقية العكسية (Backwards Compatibility) في Room دون فقدان بيانات المستخدمين؟\n\n"
            "1. كيف تعمل الـ Migrations في Room؟\n   - عند تعديل الـ Entity (إضافة عمود أو جدول جديد)، يجب زيادة رقم إصدار قاعدة البيانات (`version = 2`).\n   - إذا فتح المستخدم التطبيق بعد التحديث ولم يجد كود هجرة (Migration) صريح، سينهار التطبيق فوراً برمي استثناء `IllegalStateException: Room cannot verify the data integrity`!\n   - **كارثة ممنوعة في الإنتاج**: استخدام `fallbackToDestructiveMigration()`. هذا الأمر يقوم بمسح قاعدة البيانات بالكامل وتدمير كل بيانات المستخدم دون علمه!\n\n"
            "2. أنواع الـ Migrations المتاحة:\n   - **AutoMigration (AndroidX Room 2.4+)**: يتولى Room إنشاء كود الهجرة تلقائياً إذا كانت التغييرات بسيطة (إضافة عمود أو جدول جديد) باستخدام `@AutoMigration`.\n   - **Manual Migration**: كتابة استعلامات SQL صريحة عبر `Migration(from, to)` للعمليات المعقدة (إعادة تسمية أعمدة، تقسيم جداول، أو تحويل أنواع البيانات).\n\n"
            "3. الاختبار الآلي للهجرة (Automated Migration Testing):\n   - يجب عدم الوثوق بالـ SQL المكتوب يدوياً! نستخدم `MigrationTestHelper` في اختبارات الـ Instrumentation لاختبار الترقية من الإصدار 1 إلى الإصدار N باستخدام ملفات الـ Schema JSON الحقيقية والتأكد من بقاء البيانات سليمة."
        ),
        "practical_walkthrough": (
            "كتابة Migration يدوي واختباره والتأكد من سلامة البيانات في Room:\n"
            "```kotlin\n"
            "// 1. تعريف الـ Migration اليدوي من الإصدار 1 إلى 2:\n"
            "val MIGRATION_1_2 = object : Migration(1, 2) {\n"
            "    override fun migrate(db: SupportSQLiteDatabase) {\n"
            "        // إضافة عمود جديد مع قيمة افتراضية صريحة لمنع الـ NULL values\n"
            "        db.execSQL(\"ALTER TABLE users ADD COLUMN loyalty_points INTEGER NOT NULL DEFAULT 0\")\n"
            "        // إنشاء فهرس جديد لتسريع الاستعلامات\n"
            "        db.execSQL(\"CREATE INDEX IF NOT EXISTS index_users_loyalty_points ON users(loyalty_points)\")\n"
            "    }\n"
            "}\n"
            "\n"
            "// 2. ربط الـ Migration في Database Builder:\n"
            "@Database(entities = [UserEntity::class], version = 2, exportSchema = true)\n"
            "abstract class AppDatabase : RoomDatabase() {\n"
            "    companion object {\n"
            "        fun buildDatabase(context: Context): AppDatabase {\n"
            "            return Room.databaseBuilder(context, AppDatabase::class.java, \"app_data.db\")\n"
            "                .addMigrations(MIGRATION_1_2)\n"
            "                // ❌ ممنوع تماماً في الإنتاج:\n"
            "                // .fallbackToDestructiveMigration()\n"
            "                .build()\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Manage Room database migrations using explicit Migration classes or AutoMigrations, export schemas to JSON for version tracking, strictly avoid destructive fallbacks in production, and write automated instrumentation tests with MigrationTestHelper to verify schema upgrades against real databases.",
        "best_answer": (
            "Database migrations represent a high-stakes failure vector in mobile apps, as failed schema transitions crash the app upon startup:\n\n"
            "1. **Never Use Destructive Fallbacks in Production**:\n"
            "   - `fallbackToDestructiveMigration()` drops and recreates the SQLite database when a migration path is missing. This completely wipes offline user data, outbox queues, and cached credentials. It must be disabled in production releases.\n\n"
            "2. **Explicit Migration Architecture**:\n"
            "   - For straightforward changes (adding new tables or nullable columns), leverage Room's `@AutoMigration` with `exportSchema = true`.\n   - For non-trivial schema changes (renaming columns, changing primary keys, table splitting), write manual `Migration(from, to)` objects using explicit SQLite DDL statements.\n\n"
            "3. **Handling SQLite Limitations**:\n"
            "   - SQLite versions prior to 3.35.0 do not support `ALTER TABLE DROP COLUMN`. Complex migrations require creating a temporary table, copying data, dropping the old table, and renaming the temporary table.\n\n"
            "4. **Automated Migration Testing**:\n"
            "   - Use Room's `MigrationTestHelper` in Android instrumented tests. The test runner boots SQLite with the v1 schema JSON, inserts sample fixtures, executes the migration to v2, and validates that all records remain intact and match the new schema hash."
        ),
        "deep_answer": (
            "From a data resilience perspective, senior architects prepare for edge cases in database lifecycle and multi-version jumps:\n\n"
            "1. **Handling Multi-Version Hops (1 -> 5)**: Users do not update their apps on every release. A user jumping from version 1 directly to version 5 must traverse the migration chain (`1->2`, `2->3`, `3->4`, `4->5`). Room chains matching migrations automatically. Ensure every sequential migration path exists and is covered by automated integration test matrices.\n\n"
            "2. **Transaction Atomicity**: Room executes migration blocks inside a single SQLite transaction. If an error occurs midway, SQLite rolls back changes to prevent partial or corrupted database states. Ensure manual migrations do not attempt non-transactional SQLite operations.\n\n"
            "3. **Data Repair & Corruption Fallback**: If hardware flash corruption or unrecoverable disk faults corrupt the database file, catch `SQLiteDatabaseCorruptException`. Rather than crashing permanently in an infinite loop, gracefully back up corrupted remnants to a diagnostics dump, re-initialize the database cleanly, and trigger a fresh background synchronization from the server."
        ),
        "follow_ups": [
            {
                "question": "What does exportSchema = true do in Room?",
                "answer": "It exports the full database schema definition as a versioned JSON file at compile time, essential for Room to validate AutoMigrations and MigrationTestHelper."
            },
            {
                "question": "Can Room handle migrations across non-consecutive versions?",
                "answer": "Yes, either by chaining consecutive migrations (1->2->3) or by providing a custom shortcut migration directly from 1->3."
            }
        ]
    },
    {
        "id": "SYS-14",
        "arabic_explanation": (
            "كيف تصمم حدود الـ APIs والتعاقدات (API Boundaries and Contracts) لتطبيق كبير تعمل عليه فرق متعددة؟\n\n"
            "1. تحدي العمل عبر فرق متعددة (Multiple Teams & Distributed Ownership):\n   - عندما تعمل فرق متعددة (Mobile, Web, Backend, Payments, Search) دون تعاقدات واضحة، تتكرر المشاكل: تغييرات مفاجئة في الـ JSON، بطء التطوير لانتظار انتهاء الـ Backend، وتعارض في نماذج البيانات.\n\n"
            "2. المعمارية التعاقدية (Contract-First Design):\n   - **Contract-First قبل كتابة الكود**: الاتفاق على مواصفات الـ API (عبر OpenAPI/Swagger أو Protobuf) واعتمادها قبل أن يبدأ أي فريق في كتابة الكود.\n   - **توليد الـ Mocks التلقائية**: استخدام ملفات الـ Schema لتشغيل Mock Servers (مثل Prism أو WireMock) تتيح لفريق الموبايل تطوير واختبار الميزة بالكامل دون انتظار انتهاء الـ Backend.\n\n"
            "3. معمارية الـ BFF (Backend-for-Frontend):\n   - **مشكلة الـ Microservices في الموبايل**: استدعاء 5 خدمات منفصلة لعرض شاشة واحدة يستهلك شبكة الهاتف وبطاريته.\n   - **الحل**: طبقة BFF مخصصة للموبايل تقوم بتجميع البيانات وتفصيلها (Aggregating & Shaping) لتناسب الشاشات المحمولة تماماً، مما يقلل عدد الطلبات وحجم البايتات المنقولة.\n\n"
            "4. عزل النماذج داخل التطبيق (Data Layer Decoupling):\n   - لا تجعل كلاسات الـ DTO (الـ Network Models) تتسرب إلى الـ UI! لكل طبقة نماذجها الخاصة، ويتم استخدام Mappers صريحة لعزل الـ UI عن أي تغييرات تطرأ على الـ API."
        ),
        "practical_walkthrough": (
            "عزل نماذج الشبكة (DTOs) عن الـ Domain Entities واستخدام Mappers صريحة لحماية الواجهة من تقلبات الـ API:\n"
            "```kotlin\n"
            "// 1. نموذج الشبكة الخارجي المربوط بالـ API Contract (عرضة للتغيير من فرق الـ Backend):\n"
            "@JsonClass(generateAdapter = true)\n"
            "data class OrderNetworkDto(\n"
            "    @Json(name = \"order_id\") val id: String,\n"
            "    @Json(name = \"total_cents\") val totalAmount: Long,\n"
            "    @Json(name = \"status_code\") val statusCode: String,\n"
            "    @Json(name = \"created_at_epoch\") val timestamp: Long\n"
            ")\n"
            "\n"
            "// 2. نموذج الـ Domain المستقر والمعزول تماماً عن الـ Framework:\n"
            "data class Order(\n"
            "    val id: String,\n"
            "    val formattedTotal: String,\n"
            "    val status: OrderStatus,\n"
            "    val date: LocalDate\n"
            ")\n"
            "\n"
            "// 3. Mapper صريح يمتص التغييرات ويمنع كسر الـ UI:\n"
            "fun OrderNetworkDto.toDomain(): Order {\n"
            "    return Order(\n"
            "        id = this.id,\n"
            "        formattedTotal = \"$%.2f\".format(this.totalAmount / 100.0),\n"
            "        status = when (this.statusCode) {\n"
            "            \"PAID\" -> OrderStatus.CONFIRMED\n"
            "            \"SHIPPED\" -> OrderStatus.IN_TRANSIT\n"
            "            else -> OrderStatus.PENDING\n"
            "        },\n"
            "        date = Instant.ofEpochMilli(this.timestamp).atZone(ZoneId.systemDefault()).toLocalDate()\n"
            "    )\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Design cross-team API boundaries using contract-first schemas like OpenAPI or Protobuf, deploy a Backend-for-Frontend (BFF) layer to aggregate chatty microservices into mobile-optimized payloads, and decouple network DTOs from internal domain entities using explicit mapping boundaries.",
        "best_answer": (
            "Establishing clean API boundaries across distributed engineering teams prevents communication bottlenecks and contract drift:\n\n"
            "1. **Contract-First Design & Parallel Development**:\n"
            "   - Mobile and backend teams negotiate the API contract (OpenAPI 3.0 or Protocol Buffers) during sprint planning before implementation begins.\n   - CI generates type-safe client models and stubbed mock servers (e.g. WireMock, Prism), enabling mobile teams to build and verify features against accurate mocks without waiting for backend deployments.\n\n"
            "2. **The Backend-for-Frontend (BFF) Pattern**:\n"
            "   - Microservices architectures fragment data across domain services (User, Orders, Inventory, Recommendations). Direct client-to-microservice communication causes cellular radio drain, high latency, and fragile error handling.\n   - A mobile-specific BFF aggregates multiple microservices server-side, returning a single tailored response payload matching the client screen layout.\n\n"
            "3. **Strict Domain Layer Isolation**:\n"
            "   - Never leak API DTOs directly into UI Composables or ViewModels. Maintain explicit mapping layers (`NetworkDto -> DomainEntity -> UiState`). If the backend team renames a field, only the single mapping function requires modification; UI layers remain unaffected."
        ),
        "deep_answer": (
            "From an organizational scaling perspective, robust API boundaries require automated contract verification:\n\n"
            "1. **Consumer-Driven Contract Testing (Pact)**: Implement contract testing where the mobile client publishes its schema expectations to a central Pact broker. Before the backend team deploys an API change, their CI pipeline runs contract tests against the mobile schema to verify that no expected fields were broken or removed.\n\n"
            "2. **Tolerant Reader Pattern**: Mobile JSON parsers (Moshi / Kotlinx Serialization) must ignore unknown properties (`ignoreUnknownKeys = true`). If the backend adds new fields for other platforms, older mobile versions parse the payload without throwing deserialization exceptions.\n\n"
            "3. **Deprecation Strategy & Graceful Decommissioning**: Backends must never alter existing field data types. When deprecating fields, mark them `@Deprecated` in contracts, support them concurrently for at least 12 months, and monitor mobile version usage metrics before hard field removal."
        ),
        "follow_ups": [
            {
                "question": "What is the Tolerant Reader Pattern?",
                "answer": "A design practice where clients parse only the fields they care about and safely ignore unrecognized keys, allowing backends to evolve schemas without breaking older apps."
            },
            {
                "question": "Why is GraphQL or BFF preferred over direct REST calls in mobile architectures?",
                "answer": "It eliminates over-fetching and under-fetching by allowing the mobile client to request precisely the fields needed for the active viewport in a single HTTP round-trip."
            }
        ]
    },
    {
        "id": "SYS-15",
        "arabic_explanation": (
            "قارن بين التصميم أحادي الكتلة (Monolith) والتصميم متعدد الموديولات (Multi-Module)، ومتى تختار كلاً منهما؟\n\n"
            "1. العمارة الأحادية (Monolithic Architecture - Single `:app` Module):\n   - **المزايا**: سرعة فائقة في بداية المشروع (MVP)، سهولة إعادة الهيكلة (Refactoring)، بساطة إعداد Dagger/Hilt، وبساطة التنقل (Navigation).\n   - **العيوب عند التوسع**: بطء هائل في زمن التجميع (Clean build قد يتجاوز 25 دقيقة)، تداخل التبعيات والـ Spaghetti Code، نزاعات دمج مستمرة (Merge Conflicts)، واستحالة عزل الميزات لاختبارها المستقل.\n\n"
            "2. العمارة متعددة الموديولات (Multi-Module Architecture):\n   - **المزايا**: تجميع تزايدي سريع (Incremental Compilation)، استغلال Gradle Build Cache و Parallel Execution، وضوح ملكية الكود بين الفرق (Code Ownership)، وتطبيق مبدأ العزل الصارم (Encapsulation).\n   - **العيوب**: تعقيد أولي في إعداد Gradle scripts، إدارة التبعيات المشتركة، صعوبة الـ Navigation غير المباشر، وتكلفة هندسية في بداية المشروع.\n\n"
            "3. معايير الاختيار الواقعية (Decision Criteria):\n   - **تطبيق صغير (1-3 مطورين، ميزات محدودة)**: الـ Monolith المنظم جيداً بالحزم (Package-by-Feature) هو الخيار الأذكى والأسرع.\n   - **تطبيق متوسط/كبير (أكثر من 5 مطورين، ميزات متعددة)**: الانتقال التدريجي إلى موديولات Core و Feature لتسريع التجميع وعزل المسؤوليات."
        ),
        "practical_walkthrough": (
            "المقارنة الهيكلية بين Monolith مقسم بحزم و Modular Architecture مقسم بـ Gradle Modules:\n"
            "```text\n"
            "// 1. هيكل Monolith (ملائم للفرق الصغيرة والمشاريع الناشئة):\n"
            ":app\n"
            " ├── feature_auth/\n"
            " ├── feature_feed/\n"
            " ├── core_network/\n"
            " └── core_database/\n"
            "\n"
            "// 2. هيكل Multi-Module احترافي (ملائم للفرق الكبيرة والتطبيقات الضخمة):\n"
            "├── :app (تجميع الـ DI والـ Navigation العام فقط)\n"
            "├── :feature:auth:api / :feature:auth:impl\n"
            "├── :feature:feed:api / :feature:feed:impl\n"
            "├── :core:designsystem (مكونات الواجهة المشتركة)\n"
            "├── :core:network (OkHttp / Retrofit)\n"
            "└── :core:database (Room Database)\n"
            "```"
        ),
        "quick_answer": "Monoliths offer rapid initial prototyping and simple refactoring, but degrade into 20+ minute build times and team coupling at scale. Multi-module architectures provide parallel build caching, strict encapsulation, and team autonomy at the cost of Gradle configuration complexity. Choose monolith for MVPs and modularize as teams exceed 4–6 engineers.",
        "best_answer": (
            "Choosing between monolithic and multi-module architectures is an engineering trade-off governed by team size, build performance, and domain complexity:\n\n"
            "1. **Monolithic Architecture (`:app`)**:\n"
            "   - **Strengths**: Zero module configuration overhead, trivial dependency injection setups, effortless cross-cutting refactoring, and rapid early iteration velocity.\n   - **Failure Modes at Scale**: Long clean build times (20–40 minutes), frequent Git merge conflicts on shared manifests and navigation files, lack of enforcement boundaries leading to tight coupling between domains.\n\n"
            "2. **Multi-Module Architecture**:\n"
            "   - **Strengths**: Enables Gradle parallel execution, distributed build caching, and incremental compilation where modifying one feature only recompiles its isolated module. Provides strict encapsulation via Kotlin's `internal` modifier and defines clear team ownership.\n   - **Costs**: Increased Gradle maintenance, dependency version alignment overhead, and indirection in cross-feature navigation and dependency injection graphs.\n\n"
            "3. **Pragmatic Decision Threshold**:\n"
            "   - **1–4 Engineers**: Maintain a modular-ready monolith organized cleanly by package-by-feature.\n   - **5+ Engineers / Multi-Feature Products**: Modularize into `:core` and `:feature` boundaries to protect build velocity and establish autonomous team ownership."
        ),
        "deep_answer": (
            "From a staff platform architecture viewpoint, premature modularization can be just as damaging as an overgrown monolith:\n\n"
            "1. **The Cost of Granular Over-Modularization**: Splitting every screen into its own Gradle module creates dozens of small modules. Each module incurs Gradle configuration-time evaluation overhead. In large projects, configuring 150+ tiny modules can add 30 seconds to every build before compilation even begins. Modularize around bounded domain contexts, not individual UI screens.\n\n"
            "2. **Convention Plugins (build-logic)**: Manage multi-module build scripts cleanly by creating custom Gradle Convention Plugins in `build-logic`. Define shared conventions (`android-feature`, `android-library`, `android-compose`) in composite builds rather than duplicating Groovy/Kotlin script blocks across dozens of `build.gradle.kts` files.\n\n"
            "3. **Micro-Apps (Sample Apps) for Velocity**: The true superpower of modularization is sample app generation. An engineer working on `:feature:search:impl` runs a dedicated `:feature:search:sample` app, booting the local feature in an emulator in 4 seconds without compiling the rest of the application."
        ),
        "follow_ups": [
            {
                "question": "What is Gradle Configuration Cache?",
                "answer": "A Gradle feature that caches the output of the configuration phase and reuses it for subsequent builds, significantly speeding up multi-module build execution."
            },
            {
                "question": "How do you handle dependency injection across feature modules?",
                "answer": "Feature modules expose interface dependencies via Dagger components or Hilt entry points; the root :app module compiles all implementations and injects them into the unified graph."
            }
        ]
    },
    {
        "id": "SYS-16",
        "arabic_explanation": (
            "قارن بين نمط MVVM البسيط و Clean Architecture، ومتى تختار كلاً منهما وفقاً لحجم المشروع وتعقيد منطق الأعمال؟\n\n"
            "1. نمط MVVM البسيط (View -> ViewModel -> Repository):\n   - **الهيكل**: الـ Composable يستمع لـ StateFlow في ViewModel، والـ ViewModel يستدعي الـ Repository مباشرة لجلب البيانات وحفظها.\n   - **المزايا**: كود خفيف وبسيط، عدد ملفات قليل، سرعة تسليم عالية، ممتاز للتطبيقات القياسية التي تقوم بعمليات CRUD عادية (جلب بيانات وعرضها).\n   - **العيوب**: إذا كان التطبيق يحتوي على منطق أعمال معقد (Business Rules) تتكرر في أكثر من مكان، يبدأ الـ ViewModel في التضخم ويتحول إلى God-Class.\n\n"
            "2. نمط Clean Architecture (Presentation -> Domain -> Data):\n   - **الهيكل**: إضافة طبقة الـ Domain التي تحتوي على **UseCases / Interactors** المستقلة تماماً عن أي كود يخص أندرويد.\n   - **المزايا**: عزل كامل لقواعد العمل، إمكانية إعادة استخدام الـ UseCases عبر أكثر من ViewModel، سهولة كتابة Unit Tests نقية بدون أي Mocks تخص الـ Android Framework.\n   - **العيوب**: تكاثر هائل في عدد الملفات (Boilerplate File Proliferation)، والـ Pass-Through UseCases التي لا تفعل سوى استدعاء دالة الـ Repository مباشرة وتضيف تعقيداً بلا قيمة!\n\n"
            "3. متى تختار كل منهما؟\n   - **ابدأ بـ Pragmatic MVVM**: إذا كانت الـ UseCases مجرد سطر واحد يمرر الاستدعاء للـ Repository، فلا تكتبها!\n   - **أدخل الـ UseCases عند الحاجة فقط**: عندما تظهر قاعدة عمل معقدة تجمع بيانات من مستودعين (Repositories) مختلفين أو تتكرر في أكثر من شاشة."
        ),
        "practical_walkthrough": (
            "المقارنة بين استدعاء Repository مباشر في MVVM واستخدام UseCase مبرر في Clean Architecture:\n"
            "```kotlin\n"
            "// ❌ فخ الـ Pass-Through UseCase غير المفيد (Boilerplate بلا قيمة):\n"
            "class GetUserUseCase(private val repo: UserRepository) {\n"
            "    suspend operator fun invoke(id: String) = repo.getUser(id) // لا يفعل أي شيء سوى التمرير!\n"
            "}\n"
            "\n"
            "// ✅ استخدام سليم لـ UseCase في Clean Architecture يبرر وجوده بتنسيق منطق أعمال حقيقي:\n"
            "class CompleteCheckoutUseCase @Inject constructor(\n"
            "    private val cartRepository: CartRepository,\n"
            "    private val paymentRepository: PaymentRepository,\n"
            "    private val analyticsTracker: AnalyticsTracker\n"
            ") {\n"
            "    suspend operator fun invoke(cartId: String, paymentToken: String): CheckoutResult {\n"
            "        val cart = cartRepository.getCart(cartId) ?: return CheckoutResult.InvalidCart\n"
            "        if (cart.items.isEmpty()) return CheckoutResult.EmptyCart\n"
            "        \n"
            "        val payment = paymentRepository.charge(cart.totalCents, paymentToken)\n"
            "        return if (payment.isSuccess) {\n"
            "            cartRepository.clearCart(cartId)\n"
            "            analyticsTracker.trackPurchase(cart.totalCents)\n"
            "            CheckoutResult.Success(payment.transactionId)\n"
            "        } else {\n"
            "            CheckoutResult.PaymentFailed(payment.errorMessage)\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Simple MVVM is ideal for standard apps with minimal business logic, delivering high velocity with few layers. Clean Architecture introduces a Domain layer with UseCases to isolate complex business rules and cross-repository orchestration. Use Pragmatic MVVM by default, introducing UseCases only when real business orchestration justifies the indirection.",
        "best_answer": (
            "Comparing simple MVVM against Clean Architecture involves balancing rapid execution speed against decoupling and maintainability:\n\n"
            "1. **Simple MVVM (View -> ViewModel -> Repository)**:\n"
            "   - **Structure**: ViewModels interact directly with Repositories. Ideal for CRUD-heavy applications, data display, and feature teams prioritizing development velocity.\n   - **Trade-off**: As applications grow, ViewModels risk accumulating complex multi-repository business orchestration, resulting in bloated classes that are difficult to test in isolation.\n\n"
            "2. **Clean Architecture (Presentation -> Domain -> Data)**:\n"
            "   - **Structure**: Introduces a pure Kotlin Domain layer containing UseCases (Interactors) that orchestrate business rules independently of Android framework dependencies.\n   - **Trade-off**: High file overhead. Writing pass-through UseCases that simply delegate one line to a repository introduces unnecessary indirection without educational or architectural value.\n\n"
            "3. **Pragmatic Synthesis (Domain on Demand)**:\n"
            "   - Standard operations (e.g. fetching a profile, paginating articles) flow directly from ViewModel to Repository.\n   - Domain UseCases are introduced strictly when business logic requires orchestrating multiple repositories (e.g. checkout validating cart, charging payment, clearing cache, logging purchase) or is shared across multiple ViewModels."
        ),
        "deep_answer": (
            "From an architectural purity standpoint, the value of the Domain layer is its complete isolation from framework churn:\n\n"
            "1. **Zero Android Framework Dependencies**: The Domain layer should be a pure Kotlin library module containing zero imports from `android.*`. It does not know about Jetpack Compose, ViewModels, or SQLite. This guarantees that business logic can be tested instantly in pure JVM unit tests without Robolectric and can theoretically be shared via Kotlin Multiplatform (KMP).\n\n"
            "2. **Repository Boundary Enforcement**: In strict Clean Architecture, the domain layer defines the Repository interfaces, and the data layer implements them (Dependency Inversion Principle). In pragmatic Android MVVM, repository interfaces often live alongside the data layer. Inversion is valuable primarily when data layers swap out implementations (e.g. mocking in integration tests or swapping network drivers).\n\n"
            "3. **Architectural Cost-Benefit**: For an MVP or a small team, full Clean Architecture can reduce velocity by 30% due to continuous DTO-to-Domain-to-Ui mapping boilerplate. A senior architect chooses Clean Architecture when complex enterprise business rules demand long-term testability and cross-team boundary protection."
        ),
        "follow_ups": [
            {
                "question": "What is an anemic UseCase?",
                "answer": "A UseCase that contains no business logic and merely forwards a single method call to a repository, adding boilerplate without architectural benefit."
            },
            {
                "question": "Can a ViewModel call multiple Repositories directly in Pragmatic MVVM?",
                "answer": "Yes, if the coordination logic is specific to that screen; but if the coordination represents an enterprise business rule reused elsewhere, extract it into a UseCase."
            }
        ]
    }
]


def update_sys_data() -> None:
    data = []
    if DATA_FILE.exists():
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))

    existing_map = {item["id"]: item for item in data}
    for item in SYS_09_16:
        existing_map[item["id"]] = item

    updated = [existing_map[k] for k in sorted(existing_map.keys())]
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(updated, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {DATA_FILE} with questions SYS-09 to SYS-16. Total questions: {len(updated)}")


if __name__ == "__main__":
    update_sys_data()
