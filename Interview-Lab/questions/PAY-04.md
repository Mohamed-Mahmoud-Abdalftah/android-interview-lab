---
id: "PAY-04"
question: "What risks arise when a local payment record is not durably committed?"
topic: "Bonus: Payment/POS & Security Scenarios"
code: "PAY"
group: "A"
phase: 5
priority: "P2"
order: 474
editorial_status: "reviewed"
---

# PAY-04

## Original interview question

What risks arise when a local payment record is not durably committed?

## What the interviewer evaluates

- Write-ahead intent before an external financial side effect.
- Crash windows, database durability and server reconciliation.

## Explanation in Arabic

ما هي المخاطر الكارثية التي تحدث عندما لا يتم حفظ سجل المعاملة المالية محلياً بشكل دائم ومؤكد (Durably Committed) في أندرويد؟

1. خطورة الاعتماد على ذاكرة التطبيق (In-Memory State):
   - إذا احتفظت ببيانات الدفع في كلاس Kotlin عادي، أو في `ViewModel`، أو في كاش مؤقت غير متزامن مع القرص.
   - نظام أندرويد يملك كامل الصلاحية لقتل الـ Process في أي جزء من الثانية (Low Memory Killer)، أو قد تنفد بطارية الهاتف فجأة، أو يغلق المستخدم التطبيق قسراً.

2. المخاطر المالية والتشغيلية المترتبة:
   - **1. المعاملات الشبحية وفقدان الأموال (Phantom / Stranded Transactions)**:
     * يرسل التطبيق طلب الدفع للبنك، ويوافق البنك ويخصم 500 دولار من العميل.
     * قبل أن يحفظ التطبيق الرد في قاعدة البيانات، تنفد البطارية وينطفئ الهاتف!
     * عند إعادة التشغيل: التطبيق لا يملك أي سجل عن العملية، والتاجر لم يسلم البضاعة للعميل، بينما العميل خُصم منه المبلغ بالفعل! هذه كارثة قانونية وشكاوى نزاع (Chargebacks).
   - **2. استحالة عمل Reversal أو إلغاء**:
     * بما أن السجل غير موجود محلياً، لا تستطيع الماكينة إرسال طلب إلغاء (Reversal) للبنك لأنها لا تملك الـ Transaction Reference.
   - **3. فشل المطابقة اليومية (Reconciliation Blindness)**:
     * عند مطابقة الحسابات في نهاية اليوم، ستظهر فجوة مالية بين كشف حساب البنك ودفاتر التاجر المحلية.

3. الحل الهندسي الإلزامي (Durable Persistence First):
   - **الحفظ المتزامن والمؤكد قبل كل خطوة (Write-Ahead Logging / WAL)**:
   - تسجيل المعاملة في Room/SQLite مع استدعاء `fsync` الحقيقي للقرص في حالة `Initiated` قبل فتح أي اتصال بالشبكة، وتحديث الحالة ذرياً مع كل خطوة.

## Practical walkthrough

كود Room يوضح الحفظ الدائم والمؤكد للمعاملة قبل بدء الاتصال بالشبكة:
```kotlin
@Entity(tableName = "payment_ledger")
data class PaymentRecordEntity(
    @PrimaryKey val transactionId: String,
    val amountCents: Long,
    val currency: String,
    val state: String, // INITIATED, PROCESSING, APPROVED, REVERSED
    val idempotencyKey: String,
    val createdAtTimestamp: Long,
    val authorizationCode: String? = null
)

// الإجراء الهندسي الصارم:
class PaymentRepository(private val db: AppDatabase, private val api: PaymentApi) {
    suspend fun processPayment(request: PaymentRequest): PaymentResult = withContext(Dispatchers.IO) {
        // 1. الحفظ الدائم أولاً على القرص (Durable Commit) قبل الشبكة:
        db.runInTransaction {
            db.paymentDao().insert(PaymentRecordEntity(
                transactionId = request.txId,
                amountCents = request.amount,
                currency = "USD",
                state = "INITIATED",
                idempotencyKey = request.idempotencyKey,
                createdAtTimestamp = System.currentTimeMillis()
            ))
        }

        // 2. الآن فقط يُسمح بفتح اتصال الشبكة بأمان:
        val response = api.charge(request)
        
        // 3. تحديث الحالة فوراً على القرص:
        db.paymentDao().updateState(request.txId, "APPROVED", response.authCode)
        PaymentResult.Success(response.authCode)
    }
}
```

## Why it matters and how it works

A database transaction protects related local rows, but cannot atomically commit with a remote payment provider. This is a distributed-systems gap. A write-ahead intent plus stable server operation ID narrows the gap; authoritative status lookup and reconciliation close unknown outcomes after crashes.

## Worked example

Before calling the SDK, Room writes `PaymentAttempt(id, amountMinor, state=READY)` and any required reversal obligation in one transaction. After sending, it records PROCESSING/UNKNOWN/FINAL. On startup, a worker scans nonfinal attempts and queries the backend using the same ID; it never blindly reissues a new charge.

### Kotlin/Android sketch

```kotlin
// Repository sketch: intent is committed before external I/O.
suspend fun authorize(intent: PaymentAttempt): PaymentState {
    attempts.insertIfAbsent(intent.copy(state = PaymentState.Initiated))
    val result = try { gateway.authorize(intent.operationId, intent.amountMinor) }
        catch (e: IOException) { GatewayResult.Unknown }
    return attempts.applyEvidence(intent.operationId, result)
}
// The DB write, gateway, and applyEvidence are separate steps;
// recovery scans nonfinal rows. Imports: java.io.IOException.
// App-owned PaymentAttempt/GatewayResult/DAOs; do not catch cancellation.
```

## Trade-offs and decision criteria

Synchronous durable writes may add latency; unsafe asynchronous writes reduce latency but risk lost evidence. Choose durability guarantees consciously and test power-loss behavior on representative hardware. Local DB corruption still needs backend recovery.

## Failure modes

Using `SharedPreferences.apply()` right before SDK call does not guarantee a durable commit before power loss. Even a Room transaction may not cover external provider effects. Persist before send and reconcile after any ambiguous window.

## Production perspective

Production defines write ordering, fsync/durability assumptions, backend transaction records, startup recovery, and support escalation for unresolvable IDs. Test forced process kill and battery removal at each state boundary.

## Interview answer — short

Failing to durably commit local payment records risks stranded transactions where customers are billed without receiving goods, leaves systems unable to execute auto-reversals after crashes, and causes unreconciled balance discrepancies between merchant terminals and acquiring banks.

## Interview answer — structured

In financial systems architecture, volatile in-memory transaction tracking violates foundational ACID guarantees.

First, **The Stranded Transaction Catastrophe**. Next, if transaction state exists merely in ViewModel memory or unflushed cache buffers, an abrupt Android OS process kill or physical battery detachment during payment processing destroys the record. If the payment gateway approved the transaction, the cardholder is debited, but the merchant app boots back up with zero knowledge of the purchase, producing furious customers and severe chargeback penalties.
**Inability to Reconcile or Reverse**. To issue an ISO 8583 reversal or query status, the terminal requires the original transaction identifiers (STAN, RRN, correlation ID, amount). Without durable disk persistence, the terminal has no metadata to issue a reversal, stranding customer funds in an indefinite authorization hold.
**Audit and Legal Non-Compliance**. Payment standards (PCI-DSS, EMVCo) mandate non-repudiation and immutable transaction audit trails. Failing to durably persist transactions violates payment terminal certification rules.
**The Write-Ahead Persistence Pattern**. Finally, strict financial architectures enforce Write-Ahead logging: records are durably committed to SQLite/Room using synchronous write transactions *before* emitting network bytes.


## Interview answer — deep senior

From an SQLite file-system and hardware storage architecture perspective, durability requires understanding flash storage semantics.

First, with The SQLite `fsync` and PRAGMA synchronous Guarantee, simply calling `db.insert()` does not guarantee the bits have hit physical NAND flash. Android's SQLite uses Write-Ahead Logging (WAL). If `PRAGMA synchronous = OFF` is set, data sits in Linux kernel page cache; a battery removal loses unwritten pages. High-reliability fintech apps mandate `PRAGMA synchronous = FULL` or `NORMAL` to ensure disk barriers flush. Next, with Atomic State Transition Ledgers, payment records should never be updated in-place via loose `UPDATE` statements. Use an append-only transaction ledger (`payment_events` table). Every state change (INITIATED -> PROCESSING -> APPROVED) is inserted as an immutable event row. This provides complete tamper-evident auditability for bank forensic audits.
**Storage Encryption (Encrypted Room)**. Finally, persistent payment ledgers containing transaction metadata must be encrypted on disk using SQLCipher backed by the Android Keystore to prevent physical flash extraction attacks on rooted POS hardware.


## How to answer in the interview

- **Why:** local loss destroys the reference needed for recovery.
- **How:** durably write identity and safe parameters before external I/O.
- **Trade-off:** local atomicity cannot cover a remote issuer.
- **Failure case:** power loss after remote approval but before local final write.
- **Production solution:** startup scan plus backend/acquirer reconciliation.

## Deep-dive talking points

Prompt for write-ahead record, distributed atomicity gap, startup scanner, safe metadata and power-loss tests.

## Follow-up questions

- **Interviewer:** "What is Write-Ahead Logging (WAL) in financial transaction persistence?"
  **Answer:** "Writing and flushing transaction intent to persistent storage before executing network or hardware actions, ensuring full recovery after sudden power failure."

- **Interviewer:** "Why is an append-only event ledger preferred over updating a single status column in payment databases?"
  **Answer:** "It preserves an immutable, chronological audit trail of every state transition, preventing state corruption and facilitating bank forensic audits."

## Self-check rubric

Can I identify the crash window and explain why a local transaction cannot cover a remote provider?

## References and reviewed-on date

- [Android Room transactions](https://developer.android.com/reference/kotlin/androidx/room/package-summary) — local atomic operations.
- [Android offline-first data layer](https://developer.android.com/topic/architecture/data-layer/offline-first) — durable source of truth concepts.

Technically reviewed against primary documentation on 2026-10-13.
