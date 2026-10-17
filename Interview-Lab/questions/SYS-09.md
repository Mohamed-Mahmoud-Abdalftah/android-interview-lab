---
id: "SYS-09"
question: "Design analytics, logs, metrics, and crash reporting."
topic: "Android System Design & Architecture Decisions"
code: "SYS"
group: "A"
phase: 4
priority: "P1"
order: 338
editorial_status: "reviewed"
---

# SYS-09

## Original interview question

Design analytics, logs, metrics, and crash reporting.

## What the interviewer evaluates

Design privacy-aware analytics, structured logs, metrics and crash reporting.

## Concept and technical explanation

Designing an enterprise mobile observability architecture requires balancing real-time diagnostic visibility against device hardware constraints like battery drain, cellular data consumption, and local flash storage limits. Production telemetry consists of four core pillars: crash and fatal exception reporting, structured diagnostic breadcrumbs, user journey analytics, and application performance monitoring (APM). In-process unhandled crashes and native tombstone dumps must be captured via specialized SDKs like Crashlytics or Sentry with automated ProGuard deobfuscation mappings. High-volume analytics events and diagnostic logs must never trigger immediate synchronous network requests. Instead, they must be ingested into an in-memory buffer backed by a local SQLite disk queue. Batches of events are periodically compressed and flushed to remote endpoints over persistent HTTP connections or deferred to WorkManager when network conditions are constrained. Furthermore, mobile telemetry must enforce strict architectural privacy sanitization, redacting personally identifiable information, authentication headers, and payment credentials at the collection layer before any byte touches disk or wire.

## Practical walkthrough (English)

Designing an offline-tolerant, privacy-sanitizing telemetry dispatcher:
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
```

## Explanation in Arabic

كيف تصمم بنية المراقبة التشغيلية (Analytics, Logs, Metrics, and Crash Reporting) لتطبيق ضخم دون التأثير على الأداء والبطارية؟

1. الركائز الأربع للمراقبة التشغيلية (Observability Pillars):
   - **Crash Reporting (Crashlytics / Sentry)**: التقاط الـ Uncaught Exceptions، وحفظ الـ Breadcrumbs (آخر 30 إجراء قام به المستخدم قبل السقوط)، وربط ملف الـ `mapping.txt` لفك التشفير.
   - **Analytics Events**: تتبع سلوك المستخدم ومسارات التحويل (Funnels). يجب تجميعها (Batching) وإرسالها دورياً في الخلفية.
   - **Application Performance Monitoring (APM)**: قياس زمن الـ Cold Start، ومعدل سقوط الإطارات (Jank / Slow Frames عبر مكتبة `androidx.metrics.performance:jankstats`)، ومعدل استجابة الشبكة.
   - **Operational Logging**: تسجيل السجلات التشغيلية محلياً مع تطهير كامل من البيانات الحساسة (PII Scrubbing).

2. تصميم محرك الـ Analytics الذاتي (Event Ingestion Engine):
   - **التخزين المؤقت على القرص (Disk-Backed Queue)**: حفظ الأحداث في جدول SQLite أو ملفات محلية فور توليدها، لضمان عدم ضياعها في حال إغلاق التطبيق أو انقطاع الإنترنت.
   - **الإرسال المجمع (Batching & Backoff)**: إرسال الأحداث في حزم (مثلاً كل 30 حدثاً أو كل دقيقتين) لتوفير راديو الشبكة والبطارية، مع تفويض الإرسال لـ WorkManager إذا كان التطبيق في الخلفية.

3. الامتثال والخصوصية (Privacy & Compliance):
   - حظر طباعة الـ PII (بطاقات ائتمانية، إيميلات، أرقام هواتف) وتطهير السجلات برمجياً قبل الإرسال.

## Practical walkthrough

تصميم محرك Analytics مجمع مع طابور تخزين محلي وتطهير البيانات الحساسة:
```kotlin
class AnalyticsEventDispatcher @Inject constructor(
    private val eventQueueDao: AnalyticsDao,
    private val analyticsApi: AnalyticsApiService
) {
    private val eventChannel = Channel<AnalyticsEvent>(Channel.BUFFERED)
    private val BATCH_SIZE = 25

    init {
        startBatchProcessor()
    }

    fun trackEvent(name: String, params: Map<String, Any> = emptyMap()) {
        // 1. تطهير البيانات وحجب أي حقول حساسة:
        val sanitizedParams = params.filterKeys { !it.contains("password", true) && !it.contains("card", true) }
        val event = AnalyticsEvent(name = name, parameters = sanitizedParams, timestamp = System.currentTimeMillis())
        eventChannel.trySend(event)
    }

    private fun startBatchProcessor() {
        CoroutineScope(Dispatchers.IO).launch {
            val buffer = mutableListOf<AnalyticsEvent>()
            while (isActive) {
                // 2. تجميع الأحداث حتى اكتمال الـ Batch أو انقضاء مهلة زمنية
                val event = withTimeoutOrNull(30_000L) { eventChannel.receive() }
                if (event != null) buffer.add(event)
                
                if (buffer.size >= BATCH_SIZE || (buffer.isNotEmpty() && event == null)) {
                    try {
                        analyticsApi.sendBatch(buffer.toList())
                        buffer.clear()
                    } catch (e: Exception) {
                        // في حال فشل الشبكة: حفظ الأحداث في قاعدة البيانات المحلية لإرسالها لاحقاً
                        eventQueueDao.insertAll(buffer.map { it.toEntity() })
                        buffer.clear()
                    }
                }
            }
        }
    }
}
```

## Why it matters and how it works

Use structured events with sampling and retention limits. Offline telemetry can queue with bounded storage and WorkManager, respecting consent and network constraints. A server correlation ID helps trace one operation across retries. Crash reports need deobfuscation mapping for release and redaction of sensitive breadcrumbs.

## Worked example

Conceptual event contract; sink must enforce schema/redaction and consent.

```kotlin
data class OperationEvent(
    val name: String,
    val operationId: String,
    val stage: String,
    val durationMs: Long,
)
interface TelemetrySink { fun record(event: OperationEvent) }
// Never put access tokens, payment payloads or raw PII in event fields.
```

## Trade-offs and decision criteria

Detailed logs aid debugging but increase privacy/storage cost. Sampling reduces volume but can hide rare incidents; retain unsampled critical counters without sensitive payload. Client-only metrics miss server commit after lost response, so correlate both sides.

## Failure modes

Logging Authorization header leaks credentials. Treating a timed-out payment as failure metric hides Unknown outcomes. Analytics events with unstable names break dashboards. Storing endless offline telemetry can fill disk.

## Production perspective

A commerce app emits payment operation state transitions by opaque ID, records app crash/ANR vitals and sync backlog, and uses backend reconciliation metrics. Dashboards alert on increased Unknown age after staged rollout.

## Interview answer — short

We design mobile observability across crashes, analytics, metrics, and logs using local disk-backed batching queues to conserve battery and survive process death. We enforce strict privacy scrubbing before storing data, track startup latency and frame drops using JankStats, and collect crash breadcrumbs with asynchronous uploads.

## Interview answer — structured

A resilient mobile observability pipeline decouples high-volume diagnostic capture from network transmission to protect device battery and data bandwidth.
I organize mobile telemetry into four decoupled layers. Crash reporting captures uncaught exceptions and native signals with automated symbolication mappings, storing the last thirty user actions as diagnostic breadcrumbs.
Analytics and operational logs feed into a unified ingestion engine. Rather than dispatching immediate network calls, events accumulate in a memory buffer that flushes periodically in compressed batches to a local SQLite queue, surviving app process termination.
Application performance monitoring tracks critical user experience vitals, capturing cold start latency through reportFullyDrawn and UI stutter using AndroidX JankStats.
Before any telemetry is written to disk or transmitted over the wire, an architectural sanitizer intercepts payloads to redact authorization tokens, payment details, and personal identity data.

## Interview answer — deep senior

From a staff mobile infrastructure standpoint, the most critical telemetry challenges involve managing high-volume data streams, diagnosing application not responding conditions, and respecting strict privacy compliance.
Standard crash SDKs fail to record ANR incidents because the main looper is blocked, preventing exception handlers from executing. Modern Android architectures query ApplicationExitInfo upon the next cold launch to inspect system tombstones, heap dump reasons, and native process exit codes.
High-frequency telemetry such as network latency distributions or continuous gesture tracking creates massive backend ingest costs. I resolve this by implementing dynamic server-driven sampling. High-volume performance traces are collected from a randomized one percent sample of active installs, whereas financial transaction failures and fatal application crashes maintain one hundred percent unsampled capture rates.
Cellular radio hardware operates on a state machine with full power and idle states. Firing isolated network requests keeps the radio continuously energized in high-power tail states, draining device battery rapidly. By queuing events into sixty-second local SQLite batches, we minimize radio state transitions and conserve substantial battery.
Logging architecture must completely decouple debug visibility from release overhead. Using Timber with build-variant configurations, verbose logs are piped to logcat in internal testing builds. For production release binaries, R8 compiler rules strip debug log bytecodes entirely, routing only structured business breadcrumbs to our circular ring buffer.
Finally, when devices encounter sustained network outages, local telemetry databases must enforce strict bounded retention policies with FIFO pruning so background diagnostics never exhaust user flash storage.

## How to answer in the interview

- **Why:** observability must reveal broken promises without leaking data.
- **How:** define typed events, opaque correlation IDs, metrics, and privacy rules per sink.
- **Trade-off:** less raw logging requires better safe schemas.
- **Failure case:** token or card data enters crash attachments.
- **Production solution:** release leak tests, dashboard thresholds, and incident ownership.

## Deep-dive talking points

Choose SLOs and show how one opaque ID traces an ambiguous operation.

## Follow-up questions

- **Interviewer:** "What is reportFullyDrawn() and why is it preferred over Activity onCreate timing?"
  **Answer:** "reportFullyDrawn() indicates when the app is completely interactive with all async network data rendered, whereas onCreate only measures initial framework view attachment."

- **Interviewer:** "How do you detect memory leaks in production without crashing user apps?"
  **Answer:** "Track aggregate heap metrics and OEM OOM exit rates via ApplicationExitInfo; avoid running heavy debug tools like LeakCanary in production builds."

## Self-check rubric

Can I classify signals, redact data, bound offline storage and measure unknown outcomes?

## References and reviewed-on date

- [Android vitals](https://developer.android.com/google/play/vitals) — crash/ANR signals.
- [Android architecture guide](https://developer.android.com/topic/architecture) — data ownership.

Technically reviewed against primary documentation on 2026-10-13.
