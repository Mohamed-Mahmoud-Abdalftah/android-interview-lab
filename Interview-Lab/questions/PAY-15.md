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

Guarantee eventual reversal delivery without duplicates by implementing a persistent Store-and-Forward engine backed by SQLite and WorkManager. Enforce exponential backoff with network constraints, tie dispatches to the original persistent idempotency key for server-side deduplication, and purge local records only upon acknowledged receipt.

## Interview answer — structured

Guaranteeing eventual delivery of financial reversals during network blackouts relies on the Store-and-Forward (SaF) architecture:

1. **Store-and-Forward (SaF) Architecture**:
   - When an in-doubt transaction requires reversal while offline, the client durably writes the immutable reversal payload to a local SQLite `reversal_queue` table before acknowledging the failure to the UI.

2. **Resilient WorkManager Orchestration**:
   - Enqueue a unique WorkManager background task (`ExistingWorkPolicy.KEEP`) configured with a `NetworkType.CONNECTED` constraint and `BackoffPolicy.EXPONENTIAL`. WorkManager guarantees OS-level persistent execution attempts once connectivity is restored, surviving device reboots and app closures.

3. **Duplicate Prevention via Server Idempotency**:
   - The outbound reversal message carries the immutable `original_transaction_id` and a unique `reversal_id`. The acquiring gateway treats the reversal idempotently: if the reversal was already processed by a prior retry, the host returns an HTTP 200 / ISO 8583 Code 00 success response rather than flagging a duplicate error.

4. **Atomic Dequeue on Acknowledged Delivery**:
   - The local queue entry is deleted from SQLite only upon receiving an explicit confirmation (HTTP 200 / ISO approved) from the gateway. If a network drop occurs during response delivery, the subsequent retry safely dedupes on the server.

## Interview answer — deep senior

From an ISO 8583 financial interchange and settlement perspective, SaF engines must handle protocol edge cases:

1. **Reversal Expiration Windows (The 24-Hour Settlement Cutoff)**: If a POS terminal remains disconnected in an offline van for 4 days, issuing an ISO 8583 reversal against an authorization that was settled 3 days ago will be rejected with `Response Code 94: Duplicate or Expired`. High-reliability fintech apps implement time-to-live (TTL) checks: reversals older than the acquiring cutoff transition into a `DISPUTE_RECONCILIATION_REQUIRED` state for human back-office settlement.

2. **Jittered Backoff to Prevent Server DDOS**: When an airport or shopping mall Wi-Fi network reconnects after an outage, thousands of POS devices fire reversal retries simultaneously (the Thundering Herd Problem). WorkManager's exponential backoff applies randomized jitter to spread connection spikes smoothly over time.

3. **Terminal Pre-Flight Blocker**: As mandated in EMV certification, the terminal must prioritize flushing the offline reversal queue before permitting cashiers to initiate new customer sales, guaranteeing ledger synchronization.

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
