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

## Concept and technical explanation

Designing a hardware-resilient payment reversal queue requires persistent queuing, boot-time reconciliation, and transactional gatekeeping:
- The Hardware Threat Model:
  - POS terminals operate in hostile physical environments where cashiers or drops cause instantaneous battery detachment, immediately halting the CPU without OS shutdown hooks.
  - In-flight memory queues, coroutine channels, or standard SharedPreferences are instantly lost or corrupted.
- Core Architectural Pillars:
  1. Durable Storage with Strict Synchronization:
     - The queue lives in SQLite using Room, configured with Write-Ahead Logging (WAL) and `PRAGMA synchronous = FULL` to ensure that every committed reversal record is physically synced to non-volatile NAND flash memory.
  2. Boot-Time and Network Recovery Workers:
     - A BroadcastReceiver listening for `android.intent.action.BOOT_COMPLETED` and `android.net.conn.CONNECTIVITY_CHANGE` initializes a dedicated persistent `CoroutineWorker` via WorkManager using `ExistingWorkPolicy.KEEP`.
  3. Gatekeeping the Transaction Terminal (Stop-the-World Rule):
     - In banking standards (APACS / ISO 8583 / EMVCo), a terminal that possesses an unresolved reversal in its persistent queue must block all subsequent sales until the reversal is either acknowledged by the acquirer or resolved via status inquiry.
  4. Exponential Backoff with Jitter:
     - Retry logic employs exponential backoff capped at 60 seconds with full randomized jitter to avoid thundering-herd spikes on bank switches after network outages.

## Practical walkthrough (English)

Implementing a persistent, crash-proof reversal worker and repository in Kotlin:
```kotlin
@Entity(tableName = "pending_reversals")
data class PendingReversalEntity(
    @PrimaryKey val transactionId: String,
    val correlationId: String,
    val stan: String,
    val rrn: String?,
    val amountCents: Long,
    val attempts: Int = 0,
    val lastAttemptEpoch: Long = 0L
)

class ReversalWorker(
    appContext: Context,
    workerParams: WorkerParameters,
    private val reversalDao: PendingReversalDao,
    private val paymentSwitchApi: PaymentSwitchApi
) : CoroutineWorker(appContext, workerParams) {

    override suspend fun doWork(): Result {
        val pending = reversalDao.getAllPending()
        if (pending.isEmpty()) return Result.success()

        for (reversal in pending) {
            try {
                // Dispatch ISO 8583 0400 Reversal Message
                val ack = paymentSwitchApi.sendReversal(
                    stan = reversal.stan,
                    amount = reversal.amountCents,
                    correlationId = reversal.correlationId
                )
                if (ack.isSuccess) {
                    reversalDao.delete(reversal.transactionId)
                } else {
                    reversalDao.incrementAttempts(reversal.transactionId, System.currentTimeMillis())
                }
            } catch (e: IOException) {
                // Transient network failure: retry on next scheduled interval
                return Result.retry()
            }
        }
        return Result.success()
    }
}
```

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

Design a battery-proof reversal queue using SQLite Room with Write-Ahead Logging and synchronous FULL flash syncing. Schedule dispatch via WorkManager triggered on boot and network reconnection with exponential backoff. Crucially, enforce terminal gatekeeping, blocking subsequent retail transactions until any pending reversal is acknowledged by the bank switch.

## Interview answer — structured

Building a payment reversal queue that survives instantaneous battery removal requires hardware-aware data persistence and strict terminal operational rules.
The queue is backed by an SQLite Room table rather than in-memory queues. We configure SQLite with Write-Ahead Logging and synchronous FULL mode to guarantee that transactions are flushed directly to non-volatile flash memory before execution continues.
To handle recovery, an Android BroadcastReceiver detects device boot and schedules a reliable WorkManager task. When connectivity restores, the worker reads the queue and dispatches ISO 8583 reversal messages to the bank switch using exponential backoff with randomized jitter.
The essential financial safeguard is terminal gatekeeping. Under certified payment standards, a POS device with an unresolved reversal in its queue must refuse to process new sales until the reversal is cleared. This prevents the terminal from accumulating un-reconciled transactions and forces immediate resolution of ambiguous ledger states.

## Interview answer — deep senior

From an embedded POS certification and EMVCo level 2/3 terminal engineering standpoint, building a battery-proof reversal engine requires designing for catastrophic power interruption as a normal operational condition.
Handheld payment terminals in supermarkets and delivery logistics are subjected to constant physical trauma. A battery pack can detach mid-swipe, abruptly depriving the processor of voltage without allowing Android to run clean-up callbacks or execute onTrimMemory routines.
Under these physical constraints, data integrity rests on the storage driver. We configure Room over SQLite with PRAGMA synchronous set to FULL or EXTRA. This forces the underlying Linux storage driver to issue hardware flush commands, ensuring that the reversal row is burned into NAND flash sectors before the thread unblocks.
When the terminal reboots after a battery replacement, a BOOT_COMPLETED receiver schedules a persistent WorkManager job configured with NetworkType.CONNECTED.
More importantly, the payment UI layer incorporates a hardware gatekeeper rule. Before the cashier can enter a new sale amount, the application checks whether any rows exist in the pending_reversals table. If an unresolved reversal is present, the app locks the transaction screen and displays a Reversal In Progress banner. The terminal executes the 0400 reversal message or queries the switch status endpoint. Only upon receiving a signed cryptographic acknowledgement from the acquirer does the terminal purge the record and unlock the sale interface. This strict architectural invariant guarantees that the merchant never operates with unbalanced local ledgers.

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
