---
id: "PAY-07"
question: "How do you design a reversal queue that survives a battery removal?"
topic: "Bonus: Payment/POS & Security Scenarios"
code: "PAY"
group: "B"
phase: 5
priority: "P2"
order: 477
editorial_status: "reviewed"
---

# PAY-07

## Original interview question

How do you design a reversal queue that survives a battery removal?

## What the interviewer evaluates

- Reversal queue durability through process death and battery removal.
- Stable identity, at-least-once delivery and reconciliation.

## Explanation in Arabic

كيف تصمم طابوراً لمعالجة طلبات العكس (Reversal Queue) يصمد أمام نزع البطارية المفاجئ (Battery Pull Survival) في أجهزة الـ POS؟

1. سيناريو نزع البطارية في أجهزة نقاط البيع (The Battery Pull Scenario):
   - في محطات الوقود والمتاجر، إذا تجمدت الشاشة أو تأخرت الشبكة، يقوم الكاشير بنزع بطارية ماكينة الـ POS فجأة لإعادة تشغيلها قسراً!
   - أي بيانات كانت مخزنة في الـ RAM، أو في Coroutines عادية، أو في SharedPreferences غير محفوظة تنمحي تماماً في أجزاء من الألف من الثانية.

2. ركائز التصميم المعماري الصامد للصدمات (Battery-Proof Reversal Queue):
   - **1. قاعدة بيانات Room/SQLite محلية ومحصنة بـ WAL و Sync**:
     * كل طلب Reversal يتم تخزينه كصف في جدول `reversal_queue` يحتوي على: المعرف الأصلي، المبلغ، كود الـ ISO 8583، وعدد المحاولات السابقة.
   - **2. استخدام Jetpack WorkManager كجهة تنفيذ إجبارية**:
     * جدولة مهمة `PeriodicWorkRequest` أو `OneTimeWorkRequest` ذات قيود شبكة (`NetworkType.CONNECTED`).
     * ميزة WorkManager: يحفظ مهامه في قاعدة بيانات SQLite داخلية خاصة بنظام أندرويد، ويستمع لحدث إقلاع النظام (`BOOT_COMPLETED`)؛ بمجرد إعادة وضع البطارية وإقلاع الجهاز، يعمل الـ Worker تلقائياً في الخلفية!
   - **3. أسبقية طابور الـ Reversals على أي عملية جديدة (Pre-Flight Reversal Check)**:
     * **القاعدة الذهبية في الـ POS**: عند فتح التطبيق، أو قبل السماح بأي عملية دفع جديدة، يقوم النظام بفحص `reversal_queue` أولاً؛ وإذا وجد أي Reversal معلق، **يمنع أي عملية دفع جديدة حتى يتم إرسال الـ Reversal المعلق وتفريغ الطابور**!

## Practical walkthrough

تصميم نظام Reversal Queue متكامل يصمد أمام انقطاع الطاقة المفاجئ:
```kotlin
// 1. Worker صامد يعتمد على WorkManager لمعالجة طابور الـ Reversals:
class ReversalDispatchWorker(
    context: Context,
    params: WorkerParameters,
    private val paymentDao: PaymentDao,
    private val paymentApi: PaymentApi
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result = withContext(Dispatchers.IO) {
        val pendingReversals = paymentDao.getAllPendingReversals()
        for (reversal in pendingReversals) {
            try {
                val response = paymentApi.sendReversal(reversal.payload)
                if (response.isSuccess) {
                    paymentDao.deleteReversal(reversal.id)
                } else {
                    paymentDao.incrementRetryCount(reversal.id)
                }
            } catch (e: IOException) {
                // خطأ شبكة -> إعادة المحاولة التلقائية وفق Backoff Policy:
                return@withContext Result.retry()
            }
        }
        Result.success()
    }
}

// 2. فحص إلزامي يمنع إجراء أي معاملة جديدة إذا كان هناك Reversal معلق:
class PaymentOrchestrator(private val paymentDao: PaymentDao) {
    suspend fun canInitiateNewPayment(): Boolean {
        val pendingCount = paymentDao.countPendingReversals()
        // إذا نزع الكاشير البطارية وأعاد تشغيلها، نرفض أي دفع جديد حتى تصفية المعلقات:
        return pendingCount == 0
    }
}
```

## Why it matters and how it works

WorkManager persists scheduling intent but the application’s own DB should own financial state and queue identity. Worker execution can repeat or be interrupted; delivery is at-least-once unless server/provider deduplication and lookup close uncertain outcomes. Retry policy must respect provider windows and terminal power constraints.

## Worked example

A POS app atomically inserts `ReversalIntent(originalId, reversalId, PENDING)` with the payment’s pending status. On reboot, a worker scans pending rows, checks connectivity, calls backend with the stable reversal ID, and marks confirmed only after authoritative status. No PAN/PIN is persisted.

### Kotlin/Android sketch

```kotlin
// After DB commit, enqueue a worker; DB remains source of truth.
val request = OneTimeWorkRequestBuilder<ReversalWorker>()
    .setConstraints(Constraints.Builder()
        .setRequiredNetworkType(NetworkType.CONNECTED).build())
    .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 30, TimeUnit.SECONDS)
    .build()
workManager.enqueueUniqueWork("reversal-drain", ExistingWorkPolicy.KEEP, request)
// Worker scans pending rows and returns Result.retry() on transient failure.
// Imports: androidx.work.* and java.util.concurrent.TimeUnit.
```

## Trade-offs and decision criteria

Fast in-memory queues are simpler but disappear on battery removal. Durable queues cost storage and operational monitoring. WorkManager is suited to deferrable persistent work, while time-critical regulated payment flows may need a vendor-specific service/terminal process; both still need durable state.

## Failure modes

Worker sends reversal and crashes before DB update; next run repeats. Without provider deduplication, double side effects may occur. Reconcile first when outcome is unknown and enforce one reversal identity at the backend.

## Production perspective

Alert on queue age and repeated failures, run startup reconciliation and test forced power loss at every boundary. Escalate beyond retry window rather than silently discarding a financial obligation.

## Interview answer — short

Design a battery-pull-resilient reversal queue by persisting pre-computed reversal payloads into SQLite using synchronous transactions, binding dispatch execution to Jetpack WorkManager with BOOT_COMPLETED triggers, and enforcing a mandatory pre-flight gate that blocks new transactions until all pending reversals clear.

## Interview answer — structured

Engineering a reversal engine capable of surviving sudden physical battery removal requires a three-tiered architecture.

First, **Durable Storage with Synchronous Flash Flush**. Next, reversals must be committed to a dedicated SQLite `reversal_queue` table before any UI timeout resolution. Enforce `PRAGMA synchronous = NORMAL` or `FULL` to ensure kernel page buffers flush to physical flash memory before control flow returns.
**Resilient Execution via Jetpack WorkManager**. Enqueue reversal dispatches via `WorkManager.enqueueUniqueWork()` using an `ExistingWorkPolicy.APPEND_OR_REPLACE` policy with `Constraints(NetworkType.CONNECTED)`.
WorkManager registers system broadcast receivers (`ACTION_BOOT_COMPLETED`, `ACTION_MY_PACKAGE_REPLACED`). When the battery is re-inserted and Android boots up, WorkManager automatically resurrects the worker without user intervention. **The Pre-Flight Terminal Lockout Gate**.
Finally, financial certification (EMV/PCI) mandates that a terminal must clear historical reversals before accepting new card insertions. On app cold start or before launching a new transaction flow, the system queries the reversal queue. If entries exist, it halts new sales and flushes the queue first.


## Interview answer — deep senior

From an EMV L2 payment kernel and regulatory certification perspective, reversal queues follow strict protocol rules.

First, with Reversal Retry Limits and Poison Pill Mitigation, if a reversal request is rejected by the issuer host with a definitive non-retryable response (e.g. `ISO 8583 Response Code 12: Invalid Transaction` or `Code 94: Duplicate Transmission`), retrying forever locks the POS terminal indefinitely. The reversal worker must inspect response codes: definitive rejections transition the record to an `AUDIT_ALERT_FAILED` state, unblocking the terminal while alerting engineering telemetry. Next, with FIFO Queue Ordering, reversals must be dispatched in strict First-In-First-Out order. Discarding ordering risks reversing a subsequent authorization instead of the intended original transaction.
Finally, with Hardware Keystore Signature Durability, reversal payloads often contain encrypted EMV card cryptograms (ARQC / AAC) generated during the physical chip read. Because the physical chip is gone upon battery restart, this exact cryptogram must be safely encrypted in the persistent reversal queue record using the Android Keystore.


## How to answer in the interview

- **Why:** UI and scheduled job state are not the financial ledger.
- **How:** write outbox identity first, scan on restart, and retry under constraints.
- **Trade-off:** backoff delays delivery but protects provider/network.
- **Failure case:** assuming enqueue means confirmed reversal.
- **Production solution:** unique worker scheduling, status lookup, ageing alarms, and backend reconciliation.

## Deep-dive talking points

Prompt for durable outbox, scheduling repair, repeat delivery, provider retention and offline limit.

## Follow-up questions

- **Interviewer:** "Why must an Android POS terminal block new card transactions if a pending reversal exists in the queue?"
  **Answer:** "Payment certification rules require clearing in-doubt balance discrepancies with the host before creating new potential financial exposures."

- **Interviewer:** "How does WorkManager guarantee execution resumption after a physical battery removal?"
  **Answer:** "WorkManager persists tasks in internal SQLite storage and registers system `BOOT_COMPLETED` receivers to reschedule pending workers upon device reboot."

## Self-check rubric

Can I describe battery-removal recovery and avoid promising network delivery while permanently offline?

## References and reviewed-on date

- [Android WorkManager overview](https://developer.android.com/topic/libraries/architecture/workmanager) — persistent scheduling.
- [Android Room transactions](https://developer.android.com/reference/kotlin/androidx/room/package-summary) — local outbox commit.

Technically reviewed against primary documentation on 2026-10-13.
