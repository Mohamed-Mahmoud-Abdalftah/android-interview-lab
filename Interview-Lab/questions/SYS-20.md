---
id: "SYS-20"
question: "A payment was authorized but the UI timed out. Design recovery and reconciliation."
topic: "Android System Design & Architecture Decisions"
code: "SYS"
group: "C"
phase: 4
priority: "P1"
order: 349
editorial_status: "reviewed"
---

# SYS-20

## Original interview question

A payment was authorized but the UI timed out. Design recovery and reconciliation.

## What the interviewer evaluates

Recover an authorized payment after UI timeout by querying ledger and preserving Pending.

## Concept and technical explanation

Handling ambiguous financial transactions where a payment authorization succeeds on the backend but the mobile user interface encounters a network timeout is one of the most critical challenges in mobile architecture. In distributed systems, a network timeout represents an unknown state, not a transaction failure. The payment packet may have been captured and processed by the payment gateway, but the confirmation response was dropped due to cellular tower switching. If the mobile app naively reports a failure and allows the user to re-tap the pay button, double-charging occurs. To prevent financial discrepancies, the transaction must be persisted locally in Room as PENDING alongside a client-generated UUID idempotency key before the network call is dispatched. Upon timeout recovery or screen re-entry, the application executes a reconciliation query using the existing idempotency key. The backend inspects its immutable ledger and returns the authoritative status, allowing the client to transition cleanly to success or failure.

## Practical walkthrough (English)

Implementing robust payment reconciliation using client idempotency keys and ledger verification:
```kotlin
// 1. Immutable local transaction record persisted before network transmission
@Entity(tableName = "payment_transactions")
data class PaymentRecordEntity(
    @PrimaryKey val orderId: String,
    val idempotencyKey: String = UUID.randomUUID().toString(),
    val amountCents: Long,
    val currency: String,
    val status: PaymentStatus = PaymentStatus.PENDING,
    val createdAtMs: Long = System.currentTimeMillis()
) {
    enum class PaymentStatus { PENDING, AUTHORIZED, FAILED }
}

// 2. Reconciliation coordinator resolving ambiguous transaction outcomes
class PaymentReconciliationCoordinator @Inject constructor(
    private val paymentDao: PaymentRecordDao,
    private val paymentApi: PaymentApiService
) {
    suspend fun resolveAmbiguousPayment(orderId: String): PaymentUiOutcome {
        val record = paymentDao.getByOrderId(orderId)
            ?: return PaymentUiOutcome.Failure("Transaction not found")

        return try {
            // Reconcile status against backend ledger using original idempotency key
            val statusResponse = paymentApi.getPaymentStatusByIdempotency(record.idempotencyKey)
            when (statusResponse.state) {
                "AUTHORIZED", "CAPTURED" -> {
                    paymentDao.updateStatus(orderId, PaymentRecordEntity.PaymentStatus.AUTHORIZED)
                    PaymentUiOutcome.Success(statusResponse.receiptId)
                }
                "FAILED", "REJECTED" -> {
                    paymentDao.updateStatus(orderId, PaymentRecordEntity.PaymentStatus.FAILED)
                    PaymentUiOutcome.Failure(statusResponse.failureReason ?: "Payment rejected")
                }
                else -> {
                    // Still processing on gateway; keep UI in pending reconciliation state
                    PaymentUiOutcome.StillPending
                }
            }
        } catch (e: Exception) {
            // Network remains unavailable; persist pending state for background WorkManager recovery
            PaymentUiOutcome.StillPending
        }
    }
}
```

## Explanation in Arabic

تم خصم وتفويض عملية دفع بنكية بنجاح، ولكن واجهة التطبيق واجهت انقطاعاً في الشبكة (Timeout) قبل استلام التأكيد. كيف تصمم آلية استعادة ومطابقة (Recovery & Reconciliation) تمنع السحب المزدوج؟

1. طبيعة المشكلة (The In-Flight Network Drop Problem):
   - المستخدم ضغط "ادفع الآن"، طلب الـ POST وصل للسيرفر، السيرفر خصم المبلغ من بطاقة المستخدم بنجاح، ولكن أثناء إرسال استجابة `200 OK` إلى الموبايل انقطعت شبكة الهاتف!
   - واجهة التطبيق أظهرت خطأ "انتهت مهلة الاتصال (Timeout)".
   - إذا ضغط المستخدم على زر الدفع مجدداً دون حماية، سيتم خصم المبلغ مرة ثانية!

2. خطوات الاستعادة والمطابقة التلقائية (Reconciliation Protocol):
   - **استخدام مفتاح عدم التكرار الثابت (Idempotency Key)**: كل معاملة ترتبط بـ UUID فريد يتم حفظه في قاعدة بيانات الهاتف المحلية (Room) قبل إرسال أول طلب.
   - **منع تكرار طلب الدفع المباشر**: عند حدوث Timeout، **يُمنع منعاً باتاً إعادة إرسال طلب الدفع الأصلي فوراً**.
   - **الاستعلام عن حالة المعاملة (Reconciliation Query)**: يقوم التطبيق بإرسال طلب استعلام آمن:
     `GET /payments/reconcile?idempotency_key=<uuid>`.
   - إذا كانت المعاملة قد تمت بنجاح على السيرفر، يعيد السيرفر تفاصيل الإيصال، فيقوم التطبيق بتحديث حالة الطلب إلى `SUCCESS` وعرض شاشة النجاح للمستخدم!
   - إذا لم تصل المعاملة للسيرفر أصلاً، يمكن للتطبيق إعادة المحاولة بأمان باستخدام نفس مفتاح الـ Idempotency دون أي خوف من التكرار.

3. المعالجة عند إعادة فتح التطبيق (App Restart Recovery):
   - عند فتح التطبيق، يفحص الـ Repository جدول المعاملات المعلقة (`PENDING_RECONCILIATION`) ويقوم بمطابقتها في الخلفية مع السيرفر وتحديث الواجهة تلقائياً.

## Practical walkthrough

تنفيذ دورة مطابقة المعاملات البنكية بعد الـ Timeout وحمايتها بمفتاح الـ Idempotency في Room:
```kotlin
class PaymentReconciliationManager @Inject constructor(
    private val paymentDao: PaymentTransactionDao,
    private val paymentApi: PaymentApiService
) {
    suspend fun resolveTimedOutPayment(orderId: String): PaymentUiState {
        val record = paymentDao.getTransaction(orderId) ?: return PaymentUiState.Error("Transaction not found")
        
        return try {
            // 1. الاستعلام الآمن عن حالة المعاملة عبر مفتاح عدم التكرار
            val reconciliationResponse = paymentApi.queryTransactionStatus(record.idempotencyKey)
            
            when (reconciliationResponse.status) {
                "AUTHORIZED", "CAPTURED" -> {
                    // تم الخصم بنجاح بالفعل على السيرفر! تحديث الحالة وعرض النجاح للمستخدم:
                    paymentDao.updateStatus(orderId, TransactionStatus.COMPLETED)
                    PaymentUiState.Success(reconciliationResponse.receiptId)
                }
                "FAILED" -> {
                    paymentDao.updateStatus(orderId, TransactionStatus.FAILED)
                    PaymentUiState.Failed(reconciliationResponse.errorMessage)
                }
                "NOT_FOUND" -> {
                    // الطلب لم يصل للسيرفر أصلاً؛ الآن فقط يمكن إعادة المحاولة بأمان
                    PaymentUiState.CanRetrySafely(record.idempotencyKey)
                }
                else -> PaymentUiState.Pending
            }
        } catch (e: Exception) {
            // في حال استمرار انقطاع الشبكة: تظل المعاملة معلقة للمطابقة في الخلفية
            PaymentUiState.NetworkUnavailable(canCheckLater = true)
        }
    }
}
```

## Why it matters and how it works

Authorization may expire or require later capture; status lookup and reconciliation must distinguish those states. A worker can resume after process death, using the same key for safe retry only under server contract. UI should disable duplicate submit and provide support correlation ID. Metrics track unresolved Unknown age.

## Worked example

Conceptual Kotlin recovery API; exact states belong to the payment backend contract.

```kotlin
interface PaymentGateway {
    suspend fun status(operationId: String): PaymentStatus
}
suspend fun resolveAfterTimeout(id: String, gateway: PaymentGateway): PaymentStatus =
    gateway.status(id)
// If status is temporarily unknown, retain Pending and retry reconciliation.
```

## Trade-offs and decision criteria

Pending UX can be frustrating but avoids false decline/duplicate charge. Status endpoints and durable workers add backend/client complexity. Automatic reversal may be appropriate only after backend-confirmed state and business policy, not merely UI timeout.

## Failure modes

A UI that shows Failed on timeout may invite the user to pay again and duplicate authorization. A cancellation exception cannot roll back an already accepted server operation. A stale cached status can miss a later capture; use authoritative version/receipt.

## Production perspective

A ticket app records one checkout ID, submits authorization, shows Pending after timeout and reconciles in WorkManager. Backend exposes ledger status and controls capture. Support can search correlation ID; tests lose the response after server acceptance.

## Interview answer — short

When a payment times out, we mark the transaction as pending in local persistence using a client-generated idempotency key rather than claiming failure. We run a reconciliation query using that key to fetch the authoritative ledger status, preventing double charges and updating the UI accordingly.

## Interview answer — structured

Handling a payment timeout requires treating network interruption as an ambiguous state rather than an immediate transaction failure.
Before dispatching any payment request, the client generates a unique UUID idempotency key and writes the transaction to a local Room database with a pending status.
If the network call times out or the connection drops mid-flight, the UI must never display a generic payment failed screen with an active retry button, as doing so leads directly to double charges.
Instead, the UI transitions to an order verification state while a reconciliation query polls the backend using the original idempotency key.
The backend queries its transaction ledger; if the payment was already captured, it returns the confirmed receipt, allowing the client to mark the local record as authorized and display success.
If the user closes the app during the timeout, a background WorkManager task resumes the reconciliation process automatically upon reconnecting.

## Interview answer — deep senior

From a staff financial systems perspective, client-side payment recovery requires absolute adherence to transaction idempotency and resilient distributed state machines.
The fundamental rule of payment UX is never allowing a user to re-execute a transaction without proving the fate of the previous attempt. If the UI displays an ambiguous pending state, we present clear messaging indicating that the payment is being confirmed with the financial institution and that the user's card will not be charged twice.
If the device loses connectivity entirely or the app process is killed by the Android system, recovery cannot rely on in-memory coroutines. We schedule an expedited WorkManager job backed by the local database. When network connectivity restores, WorkManager reads pending transactions, issues the reconciliation query against the backend status endpoint, and fires a high-priority local notification confirming the purchase or prompting safe recovery.
Backend payment services must be designed around strict ledger immutability. The idempotency key must be checked inside a distributed Redis lock or database unique constraint. If two identical requests hit the backend simultaneously due to aggressive client retries, the server processes the first and makes the second await the initial transaction outcome.
Finally, we implement telemetry on transaction resolution times. If the percentage of payments requiring reconciliation spikes, our monitoring triggers an alert to investigate cellular carrier issues or payment gateway webhook degradation.

## How to answer in the interview

- **Why:** a lost response does not undo authorization.
- **How:** persist identity, show Pending, and converge on authoritative status.
- **Trade-off:** waiting UX and support tooling are more complex.
- **Failure case:** second authorize with a new key duplicates effect.
- **Production solution:** ledger query, idempotency contract, durable recovery, and audit timeline.

## Deep-dive talking points

Trace authorization versus capture and show why timeout is not failure.

## Follow-up questions

- **Interviewer:** "Why is GET /payments/status safe to retry indefinitely?"
  **Answer:** "GET requests are inherently idempotent and read-only; polling status cannot alter server balances or duplicate charges."

- **Interviewer:** "What is the role of payment gateway webhooks in transaction reconciliation?"
  **Answer:** "Webhooks provide authoritative, out-of-band confirmation directly from payment processors to backend servers, independent of mobile network reliability."

## Self-check rubric

Can I preserve original key, represent Unknown and reconcile authorization/capture separately?

## References and reviewed-on date

- [Kotlin withTimeout API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/with-timeout.html) — timeout semantics.
- [Android task scheduling](https://developer.android.com/develop/background-work/background-tasks/persistent) — restartable reconciliation.

Technically reviewed against primary documentation on 2026-10-13.
