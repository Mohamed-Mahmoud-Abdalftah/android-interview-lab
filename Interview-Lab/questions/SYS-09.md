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

Design observability across crashes, analytics, metrics, and logs using disk-backed batching queues to conserve battery and survive process death. Enforce strict PII scrubbing before storage, track cold start and frame-drop metrics via JankStats, and upload crash breadcrumbs and logs asynchronously.

## Interview answer — structured

A unified observability architecture balances real-time diagnostic visibility against device battery and network overhead.

First, **Crash Reporting & Diagnostic Breadcrumbs**. Next, integrate crash SDKs (Crashlytics/Sentry) configured with automated deobfuscation (`mapping.txt`).
Maintain a circular buffer of the last 30 user actions (screen views, network status transitions, critical user clicks) recorded as diagnostic breadcrumbs attached automatically to unhandled exceptions. **Disk-Backed Event Ingestion Pipeline**.
Dispatching network requests for individual analytics events drains battery radios rapidly. Ingest events into an in-memory queue that flushes to a local SQLite buffer. Batch-upload events periodically (e.g., every 30 events or 60 seconds) with GZIP compression, deferring large backlog flushes to Wi-Fi/charging via WorkManager.
**APM & User Experience Telemetry**. Measure application launch latency (Time to Initial Display & Time to Full Display via `reportFullyDrawn()`).
Instrument UI rendering using AndroidX `JankStats` to track jank percentages across critical scrollable surfaces. **PII Scrubbing Boundary**.
Finally, enforce an architectural sanitizer that intercepts all logs and analytics payloads, redacting PAN numbers, email addresses, and auth headers before persistence.


## Interview answer — deep senior

From a staff-level infrastructure perspective, mobile observability requires managing high-volume data streams and ANR detection.

First, with Application Not Responding (ANR) Forensics, standard crash handlers do not capture ANRs because the main thread is blocked. Modern architectures use `ApplicationExitInfo` (introduced in Android 11) to inspect system tombstone traces and exit reasons (`REASON_ANR`, `REASON_CRASH_NATIVE`, `REASON_LOW_MEMORY`) upon the subsequent app cold start. Next, with Adaptive Dynamic Sampling, high-volume telemetry (e.g., measuring individual HTTP call latencies) can overwhelm backend ingestion servers at scale. Implement server-configurable sampling rates via feature flags (e.g. Logging network performance traces for 1% of users, while capturing 100% of crashes and financial failure events).
Finally, with Zero-Overhead Debug vs. Release Logging, use Timber with separate tree implementations: a `DebugTree` logging verbose output in development, and a stripped release pipeline where R8 removes `Log.v` and `Log.d` bytecodes entirely, routing only critical error reports to the telemetry queue.


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
