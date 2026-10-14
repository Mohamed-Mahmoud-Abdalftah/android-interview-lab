---
id: "PAY-06"
question: "How do you ensure atomic persistence of transaction status and reversal intent?"
topic: "Bonus: Payment/POS & Security Scenarios"
code: "PAY"
group: "B"
phase: 5
priority: "P2"
order: 476
editorial_status: "reviewed"
---

# PAY-06

## Original interview question

How do you ensure atomic persistence of transaction status and reversal intent?

## What the interviewer evaluates

- Atomic local transition pairing payment status with reversal intent.
- Limits of local atomicity across provider boundary.

## Explanation in Arabic

كيف تضمن التخزين الذري الحتمي (Atomic Persistence) لحالة المعاملة ونية العكس (Reversal Intent) في أندرويد؟

1. خطورة انعدام الذرية (Non-Atomic Persistence Hazard):
   - تخيل السيناريو التالي في كود الدفع:
     1. نقوم بتحديث حالة المعاملة إلى `FAILED`.
     2. في خطوة منفصلة، نقوم بإضافة طلب إلى جدول الـ `reversal_queue`.
   - إذا انطفأ الهاتف أو قُتلت العملية بين الخطوتين: أصبحت المعاملة معلمة كـ `FAILED`، ولكن **طلب الـ Reversal لم يُسجل أبداً**!
   - النتيجة: البنك يحتجز أموال العميل، والتطبيق يعتقد أن العملية فشلت، ولا يوجد أي كود في الخلفية يعرف أنه يجب إرسال Reversal!

2. مفهوم الذرية (Atomicity) في قواعد البيانات:
   - كل العمليات تنفذ معاً ككتلة واحدة غير قابلة للتجزئة: إما أن **تنجح جميعها بالكامل (Commit)**، أو **تفشل جميعها وتتراجع كأن شيئاً لم يكن (Rollback)**.

3. الحل الهندسي: معاملات Room/SQLite الذرية (`@Transaction`):
   - فتح معاملة ذرية واحدة تدمج:
     1. تحديث حالة المعاملة الأصلية إلى `IN_DOUBT_NEEDS_REVERSAL`.
     2. إدراج عنصر جديد في جدول `reversal_queue` يحتوي على كل بيانات الـ ISO 8583 payload.
     3. جدولة مهمة WorkManager فورية لتنفيذ العكس.
   - هذا يضمن 100% أن نية العكس محفوظة ومحمية على القرص مهما كانت ظروف تعطل الجهاز.

## Practical walkthrough

تطبيق المعاملات الذرية لحفظ نية العكس في Room باستخدام `@Transaction`:
```kotlin
@Dao
interface PaymentDao {
    @Query("UPDATE transactions SET status = :newStatus WHERE id = :txId")
    suspend fun updateTransactionStatus(txId: String, newStatus: String)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertReversalIntent(intent: ReversalIntentEntity)

    // ✅ المعاملة الذرية الصارمة: مستحيل تنفيذ خطوة دون الأخرى!
    @Transaction
    suspend fun markInDoubtAndEnqueueReversal(
        txId: String,
        intent: ReversalIntentEntity
    ) {
        updateTransactionStatus(txId, "UNKNOWN_AWAITING_REVERSAL")
        insertReversalIntent(intent)
    }
}

// الاستخدام داخل الـ Repository عند حدوث انقطاع في الشبكة:
suspend fun handleTimeoutFailure(txId: String, request: PaymentRequest) {
    val reversalIntent = ReversalIntentEntity(
        reversalId = UUID.randomUUID().toString(),
        originalTxId = txId,
        amountCents = request.amount,
        payload = request.toIso8583ReversalPayload(),
        status = "PENDING_DISPATCH"
    )
    // الذرية تضمن كتابة كلاهما للقرص معاً:
    paymentDao.markInDoubtAndEnqueueReversal(txId, reversalIntent)
    // إطلاق مهمة WorkManager لمعالجة الطابور:
    reversalWorkScheduler.scheduleReversalWorker()
}
```

## Why it matters and how it works

Room `withTransaction` can commit related local rows atomically. A transactional outbox record describes the required future side effect. A worker processes outbox rows with retries; completion is marked only after authoritative confirmation. The external call must occur outside the DB transaction and tolerate repeated delivery.

## Worked example

When a payment timeout requires reversal, one transaction updates `attempt.state=REVERSAL_PENDING` and inserts `ReversalIntent(originalOperationId, status=PENDING)`. WorkManager later sends it. If the app dies after send but before marking sent, it may send again; server/provider deduplicates by stable identity.

### Kotlin/Android sketch

```kotlin
// App DAO contract; @Transaction wraps both local SQL writes.
@Dao
interface PaymentDao {
    @Query("UPDATE attempts SET state = 'REVERSAL_PENDING' " +
           "WHERE id = :id AND state = 'UNKNOWN'")
    suspend fun markPending(id: String): Int
    @Insert(onConflict = OnConflictStrategy.ABORT)
    suspend fun insertIntent(intent: ReversalIntent)
    @Transaction
    suspend fun queueReversal(id: String, intent: ReversalIntent): Boolean {
        if (markPending(id) != 1) return false
        insertIntent(intent)
        return true
    }
}
// Imports: androidx.room.Dao/Query/Insert/Transaction/OnConflictStrategy.
// ReversalIntent has a unique original ID; a conflicting insert rolls back.
// The real DAO validates original references and provider-specific rules.
```

## Trade-offs and decision criteria

Local transaction adds consistency but cannot force exactly-once network delivery. Keeping the DB transaction open during an SDK call is unsafe and can block other work. Outbox processing is at-least-once with explicit idempotency.

## Failure modes

Two separate writes leave a crash gap. Marking reversal done after HTTP 200 without checking provider semantics may be wrong. Test crash before commit, after commit, after send and before acknowledgment.

## Production perspective

Production has unique constraints on original operation ID, a worker lease/claim strategy, retry backoff, observability of queue age and escalation after retention windows. A backend ledger remains authoritative.

## Interview answer — short

Ensure atomic persistence of transaction status and reversal intent by executing both operations inside a single database transaction (@Transaction in Room/SQLite). If a sudden power loss occurs, SQLite WAL guarantees that both the status update and the reversal queue insertion succeed together or rollback completely.

## Interview answer — structured

Atomic persistence prevents state divergence between payment status records and outbound reversal queues.

First, **The Dual-Write Vulnerability**. Next, when handling an ambiguous payment outcome (such as a gateway read timeout), two state mutations must occur: (1) transitioning the transaction status to `IN_DOUBT`, and (2) enqueuing a reversal payload in the pending dispatch queue. If performed as separate uncoordinated queries, a crash in between drops the reversal intent while recording a failed status, permanently leaking held customer funds.
**SQLite ACID Transaction Guarantees**. Wrap both operations in an atomic database transaction using Room's `@Transaction` annotation or `db.runInTransaction { ... }`. SQLite's Write-Ahead Log (WAL) ensures that either both mutations are durably committed to the database file or neither takes effect, preventing partial state writes.
**Deterministic WorkManager Triggering**. Finally, following the successful database transaction commit, schedule a persistent `OneTimeWorkRequest` with exponential backoff to dispatch the reversal. If the device powers off immediately after the commit, WorkManager inspects the pending table upon boot and resumes dispatch automatically.


## Interview answer — deep senior

From an ACID transaction isolation and POS hardware crash perspective, atomicity requires hardware-aware sequencing.

First, with Isolation Levels in Android SQLite, SQLite operates with `SERIALIZABLE` transaction isolation by default in WAL mode. This guarantees that background sync workers reading the `reversal_queue` cannot observe a half-written transaction state while the UI thread is committing an in-doubt payment. Next, with Immutable Reversal Enqueueing, store the exact raw cryptographic payload required for the reversal (e.g. Original STAN, terminal ID, card cryptogram, transaction amount) inside the `reversal_queue` table. Do not rely on recomputing the payload later, as volatile context variables will be lost if the process restarts.
Finally, with Battery-Removal Defense, on Android POS smart terminals, users frequently pull the battery pack to force-reset frozen screens. By executing `markInDoubtAndEnqueueReversal` before attempting any UI teardown or navigation, the reversal intent is guaranteed to survive the hard reset.


## How to answer in the interview

- **Why:** a status without its obligation can strand an approved transaction.
- **How:** change attempt and insert reversal intent in one database transaction.
- **Trade-off:** remote delivery remains at least once.
- **Failure case:** crash between two local writes or after send before ack.
- **Production solution:** durable outbox, deduplication, and authoritative confirmation.

## Deep-dive talking points

Prompt for Room transaction, outbox uniqueness, remote repeatability, crash matrix and provider contract.

## Follow-up questions

- **Interviewer:** "What catastrophic state occurs if transaction status and reversal queue insertion are not atomic?"
  **Answer:** "The app records the transaction as failed but loses the reversal intent, leaving the customer debited at the bank with no automated recovery."

- **Interviewer:** "Why should the reversal queue record store the complete pre-computed reversal payload?"
  **Answer:** "Because volatile memory context and ephemeral tokens are wiped if the process dies, making it impossible to reconstruct the payload later."

## Self-check rubric

Can I place the transaction boundary and describe the remaining distributed gap?

## References and reviewed-on date

- [Android Room transactions](https://developer.android.com/reference/kotlin/androidx/room/package-summary) — local atomicity.
- [Android WorkManager overview](https://developer.android.com/topic/libraries/architecture/workmanager) — persistent work.

Technically reviewed against primary documentation on 2026-10-13.
