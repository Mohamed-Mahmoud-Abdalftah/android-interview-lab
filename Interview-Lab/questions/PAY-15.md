---
id: "PAY-15"
question: "The server is unreachable when a reversal is due. How do you guarantee eventual delivery without duplicates?"
topic: "Bonus: Payment/POS & Security Scenarios"
code: "PAY"
group: "C"
phase: 5
priority: "P2"
order: 485
editorial_status: "reviewed"
---

# PAY-15

## Original interview question

The server is unreachable when a reversal is due. How do you guarantee eventual delivery without duplicates?

## What the interviewer evaluates

- Eventual-delivery conditions and the impossibility of guaranteeing reconnect.
- Durable queue, duplicate-safe retries, status lookup and escalation.

## Concept and technical explanation

Guaranteeing eventual delivery of financial reversals during prolonged server outages without risking duplicate execution requires a persistent transactional outbox, idempotent protocol design, and exponential backoff:
- The Distributed Outage Dilemma:
  - When a transaction times out, a reversal must reach the banking switch to void the hold.
  - However, if the bank switch or cellular gateway remains unreachable for hours, volatile retries will fail and terminate upon device reboot or app closure.
- The Architectural Solution:
  1. Persistent Reversal Outbox:
     - The reversal intent is saved in a local SQLite table (`reversal_queue`) with Write-Ahead Logging and `PRAGMA synchronous = FULL`.
     - The record contains the original transaction's immutable parameters: `originalStan` (Systems Trace Audit Number), `originalRrn` (Retrieval Reference Number), `originalAmount`, and `correlationId`.
  2. Background Execution Engine (WorkManager):
     - A periodic and one-time `CoroutineWorker` is scheduled with `BackoffPolicy.EXPONENTIAL` and network constraints (`NetworkType.CONNECTED`).
     - Survives device reboots via `ExistingWorkPolicy.KEEP` and continues retrying over hours or days without battery drain.
  3. Strict Idempotent Banking Semantics:
     - ISO 8583 message 0400/0420 reversals are inherently idempotent by design when referencing the original transaction identifiers.
     - If the switch receives the same reversal multiple times due to unacknowledged delivery packets, it recognizes the original STAN/RRN, marks the hold as already reversed, and returns a success response (`00`) without creating duplicate balance credits.
  4. Poison-Pill Quarantine:
     - If the server responds with a definitive non-retryable response (e.g., `Invalid Card`, `Batch Already Settled`), the record is moved to an `orphaned_reversals` dead-letter table for end-of-day manual ledger reconciliation rather than retrying indefinitely.

## Practical walkthrough (English)

Implementing a resilient persistent reversal delivery worker in Kotlin:
```kotlin
class ResilientReversalWorker(
    appContext: Context,
    workerParams: WorkerParameters,
    private val reversalDao: ReversalQueueDao,
    private val paymentSwitchApi: PaymentSwitchApi
) : CoroutineWorker(appContext, workerParams) {

    override suspend fun doWork(): Result {
        val pending = reversalDao.getNextPendingReversal() ?: return Result.success()

        return try {
            // Reversals MUST use the exact original STAN and RRN to guarantee backend idempotency
            val response = paymentSwitchApi.sendIsoReversal(
                originalStan = pending.originalStan,
                originalRrn = pending.originalRrn,
                amountCents = pending.amountCents,
                correlationId = pending.correlationId
            )

            when (response.actionCode) {
                // 00 = Approved/Reversed successfully, 94 = Already Reversed (Idempotent Success)
                "00", "94" -> {
                    reversalDao.delete(pending.id)
                    Result.success()
                }
                // Terminal rejection codes: Quarantine to dead-letter queue for manual reconciliation
                "25", "12" -> {
                    reversalDao.markQuarantined(pending.id, response.actionCode)
                    Result.success()
                }
                else -> {
                    // Transient switch error: trigger exponential backoff retry
                    reversalDao.incrementAttempt(pending.id)
                    Result.retry()
                }
            }
        } catch (e: IOException) {
            // Network completely unreachable: WorkManager will back off and retry automatically
            reversalDao.incrementAttempt(pending.id)
            Result.retry()
        }
    }
}
```

## Explanation in Arabic

انقطع اتصال الإنترنت تماماً عندما حان وقت إرسال طلب العكس (Reversal) للبنك. كيف تضمن تسليم الطلب حتماً في المستقبل (Eventual Delivery) دون إرسال طلبات مكررة؟

1. معضلة انقطاع الشبكة أثناء العكس (Offline Reversals):
   - يحتاج التطبيق لإلغاء معاملة معلقة، ولكن الجهاز في وضع عدم الاتصال (Offline) أو في قبو بدون تغطية خلوية.
   - لا يجوز التراجع عن العكس أو نسيانه؛ لأن أموال العميل ستظل محجوزة لدى البنك للأبد!
   - ولا يجوز إرسال طلبات عكس عشوائية متكررة عند عودة الشبكة لأنها قد تربك نظام البنك وتعتبر معاملات مكررة (Duplicate Flood).

2. نمط التخزين والتمرير اللاحق (Store-and-Forward Pattern - SaF):
   - **1. الحفظ الدائم كـ Pending في SQLite**:
     * حفظ كائن الـ Reversal في جدول `reversal_queue` مع الـ `idempotency_key` الأصلي.
   - **2. آلية إعادة المحاولة مع التراجع الأسي (Exponential Backoff with Jitter)**:
     * استخدام Jetpack WorkManager الذي يتكفل بإعادة المحاولة تلقائياً بمجرد توفر الشبكة (`Constraints.NetworkType.CONNECTED`).
     * فترات الانتظار تتصاعد تدريجياً: 10 ثوانٍ، ثم 30 ثانية، ثم دقيقة، ثم 5 دقائق لمنع إغراق الخادم بالطلبات (Thundering Herd Problem).
   - **3. اللاتكرارية في خادم البنك (Server-Side Idempotency)**:
     * خادم الدفع مصمم ليكون Idempotent على معرف الـ Reversal (`reversal_id` + `original_tx_id`).
     * إذا استلم الخادم طلب العكس مرتين، ينفذ الأول ويعيد نجاحاً فورياً للطلب الثاني دون أي تكرار.
   - **4. الحذف الذري بعد التأكيد (Atomic Deletion upon 200 OK)**:
     * بمجرد استلام رد صريح بنجاح العكس من السيرفر، يتم حذف السجل من جدول الـ `reversal_queue` محلياً.

## Practical walkthrough

تنفيذ محرك Store-and-Forward للـ Reversals باستخدام WorkManager و Room:
```kotlin
// 1. Worker صامد يعتمد على Store-and-Forward لمعالجة الـ Reversals عند عودة الشبكة:
class StoreAndForwardReversalWorker(
    context: Context,
    params: WorkerParameters,
    private val paymentDao: PaymentDao,
    private val api: PaymentGatewayApi
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result = withContext(Dispatchers.IO) {
        val pendingReversals = paymentDao.getAllPendingReversals()
        if (pendingReversals.isEmpty()) return@withContext Result.success()

        for (reversal in pendingReversals) {
            try {
                // إرسال طلب العكس مع Idempotency Key الأصلي:
                val response = api.sendReversal(
                    idempotencyKey = reversal.idempotencyKey,
                    payload = reversal.payload
                )
                // تم التأكيد بنجاح -> حذفه فورياً من الطابور لمنع التكرار:
                if (response.isSuccess || response.isAlreadyReversed) {
                    paymentDao.deleteReversal(reversal.id)
                } else if (response.isTerminalRejection) {
                    // خطأ غير قابل للإعادة (مثل انتهاء الصلاحية) -> تحويله لتقرير التدقيق البشري:
                    paymentDao.markAuditRequired(reversal.id)
                }
            } catch (e: IOException) {
                // لا توجد شبكة -> مطالبة WorkManager بإعادة المحاولة لاحقاً مع Backoff:
                return@withContext Result.retry()
            }
        }
        Result.success()
    }
}
```

## Why it matters and how it works

A durable outbox preserves obligation through process death. WorkManager can retry under constraints but does not ensure execution while a device is off or disconnected. At-least-once send attempts plus provider/server idempotency and authoritative lookup aim for one business effect; retention windows and protocol rules must be explicit.

## Worked example

On `IOException`, leave `ReversalIntent(id=R1, original=P1, PENDING)` in Room and schedule constrained work with backoff. On restart, scan pending rows. If a send times out, query backend/provider for R1 before retrying; if still unknown, retry same identity under contract. Escalate aging entries.

### Kotlin/Android sketch

```kotlin
// Inside an injected CoroutineWorker: one durable row, same ID on retries.
override suspend fun doWork(): Result {
    val pending = dao.pendingReversals()
    for (intent in pending) {
        when (gateway.lookupOrSend(intent.reversalId, intent.originalId)) {
            ReversalStatus.Confirmed -> dao.markConfirmed(intent.reversalId)
            ReversalStatus.Unknown -> return Result.retry()
            ReversalStatus.Expired -> dao.markEscalated(intent.reversalId)
        }
    }
    return Result.success()
}
// App-defined gateway/status; server enforces deduplication and deadlines.
```

## Trade-offs and decision criteria

Aggressive retries reduce latency but may overload provider or exceed windows. Conservative backoff saves resources but delays reversal. Choose based on acquirer deadlines, network quality and operational SLA.

## Failure modes

Generating a fresh reversal ID after each timeout can create duplicate effects. Marking done when the request merely left the terminal loses unknown outcomes. Never delete a pending row solely because retry budget expired; move it to an escalated state.

## Production perspective

Backend reconciliation runs independently from terminal connectivity where possible. Dashboards page on queue age and mismatched ledgers. Test server outage, response loss, power removal, duplicate workers and expiry of provider deduplication window.

## Interview answer — short

Guarantee eventual delivery of reversals during server outages using a persistent SQLite Outbox table managed by WorkManager with exponential backoff and network constraints. Prevent duplicate credits by strictly reusing original transaction identifiers like STAN and RRN, ensuring the banking switch processes the reversal idempotently regardless of delivery attempts.

## Interview answer — structured

Guaranteeing eventual delivery of payment reversals when the server is unreachable requires combining local persistence with idempotent messaging protocols.
When a transaction times out and a reversal is required, relying on in-memory retries is insufficient because an extended network outage or terminal reboot will erase the task.
Instead, we implement the Transactional Outbox pattern. The reversal payload is durably written to a dedicated SQLite table using Room, preserving original identifiers like the Systems Trace Audit Number and Retrieval Reference Number.
A WorkManager worker configured with network connectivity constraints and exponential backoff polls this table. It operates persistently across device restarts and battery recharges, repeatedly attempting delivery once connectivity returns.
To guarantee that retrying never creates duplicate credits, the reversal request is designed to be strictly idempotent. By referencing the original transaction STAN and amount, the banking switch processes the first arrival and safely acknowledges any subsequent duplicate submissions with an idempotent success code, purging the local queue cleanly.

## Interview answer — deep senior

From an ISO 8583 protocol engineering, distributed ledger consistency, and store-and-forward architectural standpoint, delivering reversals across extended network partitions is a classic manifestation of the Guaranteed Delivery pattern.
In rural or mobile retail environments, an Android POS terminal can lose cellular connectivity for hours due to localized tower failures or tunnel transit. If a transaction enters an in-doubt state right before connectivity drops, failing to deliver the reversal leaves the cardholder's credit line tied up in a pending authorization hold, sparking customer outrage and merchant chargebacks.
The enterprise architectural solution deploys a hardened Store-and-Forward (SaF) engine backed by SQLite and WorkManager.
The reversal intent is recorded into a persistent queue table as an immutable record. Crucially, the payload must replicate the exact cryptographic and operational identifiers of the original authorization: the Systems Trace Audit Number (STAN), the Retrieval Reference Number (RRN), the local transaction timestamp, and the exact amount.
WorkManager orchestrates execution using a BackoffPolicy.EXPONENTIAL policy, ensuring that retries do not exhaust battery life or flood recovering network towers.
The ultimate safeguard against duplicate financial execution is backend protocol idempotency. Under ISO 8583 standards, message types 0400 and 0420 are intrinsically idempotent when anchored by the original STAN and RRN. When the server receives the first reversal packet, it voids the authorization and releases the cardholder funds. If network instability drops the server's ACK packet and the terminal retransmits the reversal ten minutes later, the switch detects that the referenced authorization has already been reversed, suppresses any secondary credit mutations, and returns a benign success response (Action Code 00 or 94).
Upon receiving this authoritative acknowledgement, the terminal purges the record from the queue, achieving absolute ledger parity across intermittent networks.

## How to answer in the interview

- **Why:** delivery requires connectivity and a live execution path.
- **How:** durable outbox, stable ID, status lookup, and retry after reconnection.
- **Trade-off:** fast retries versus provider limits and battery.
- **Failure case:** new IDs after each timeout or deleting an aged row.
- **Production solution:** independent backend reconciliation, retention-aware alerts, and human escalation.

## Deep-dive talking points

Prompt for safety versus liveness, same reversal ID, retention window, independent backend reconciliation and permanent-offline limit.

## Follow-up questions

- **Interviewer:** "What happens if a reversal request reaches the server after the daily batch settlement cutoff?"
  **Answer:** "The server rejects the reversal because the transaction has already cleared; the incident must be routed to back-office reconciliation for an automated refund."

- **Interviewer:** "Why is randomized jitter added to exponential backoff in payment retry engines?"
  **Answer:** "To prevent thousands of reconnected terminals from hitting the payment gateway simultaneously in a synchronized thundering herd wave."

## Self-check rubric

Can I state the conditional guarantee and explain duplicate-safe retries plus escalation?

## References and reviewed-on date

- [Android WorkManager overview](https://developer.android.com/topic/libraries/architecture/workmanager) — persistent scheduling constraints.
- [Stripe idempotent requests](https://docs.stripe.com/api/idempotent_requests) — provider-specific retry semantics.

Technically reviewed against primary documentation on 2026-10-13.
