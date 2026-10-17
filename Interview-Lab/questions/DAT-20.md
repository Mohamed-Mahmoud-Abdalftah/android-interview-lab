---
id: "DAT-20"
question: "The server accepted a payment but the response was lost. How do you recover safely?"
topic: "Networking, Room, DataStore & Offline-First"
code: "DAT"
group: "C"
phase: 3
priority: "P1"
order: 277
editorial_status: "reviewed"
---

# DAT-20

## Original interview question

The server accepted a payment but the response was lost. How do you recover safely?

## What the interviewer evaluates

Recover a server-accepted payment whose response was lost, without duplicate charge.

## Concept and technical explanation

Safe recovery from lost payment responses addresses the classic Two Generals' network partition problem using idempotency protocols and deterministic state reconciliation:
- The Failure Scenario: The client sends a payment POST request. The payment gateway charges the customer and persists the record. Before the 200 OK HTTP response reaches the mobile device, the cellular signal drops or the connection times out. The Android client catches a SocketTimeoutException. Blindly retrying the transaction without an idempotency key triggers a duplicate charge, while reporting failure induces user panic.
- Client-Generated Idempotency Keys: Before transmitting the payment request, the client generates a unique cryptographically random UUID (Idempotency-Key HTTP header) and saves the payment record locally in Room with status PENDING_CONFIRMATION.
- Server Idempotency Contract: The backend stores idempotency keys in Redis or a relational database with strict unique constraints. When a duplicate request with the identical key arrives, the backend does not re-execute the charge; it returns the cached receipt from the initial successful execution.
- Safe Recovery Protocol:
  1. Intercept network failure (SocketTimeoutException or IOException).
  2. Do not report payment failure or show an error toast. Transition UI to a 'Verifying Transaction' state.
  3. Query a dedicated idempotency status endpoint (GET /api/v1/payments/status/{idempotencyKey}).
  4. If network recovery fails, schedule an immediate non-destructive WorkManager task with Exponential Backoff to reconcile the payment status in the background.

## Practical walkthrough (English)

Safe payment execution with client-generated idempotency key and status recovery:
```kotlin
@Entity(tableName = "payments")
data class PaymentRecord(
    @PrimaryKey val idempotencyKey: String,
    val orderId: String,
    val amount: Double,
    val status: PaymentStatus // PENDING, CONFIRMED, FAILED
)

class PaymentRecoveryManager(
    private val paymentDao: PaymentDao,
    private val paymentApi: PaymentApiService
) {
    suspend fun executePayment(orderId: String, amount: Double): PaymentResult {
        val key = UUID.randomUUID().toString()
        paymentDao.insert(PaymentRecord(key, orderId, amount, PaymentStatus.PENDING))

        return try {
            val response = paymentApi.charge(idempotencyKey = key, orderId = orderId, amount = amount)
            paymentDao.updateStatus(key, PaymentStatus.CONFIRMED)
            PaymentResult.Success(response.receiptId)
        } catch (e: IOException) {
            // Network failed: do NOT treat as failed charge; initiate recovery
            recoverPaymentState(key)
        }
    }

    private suspend fun recoverPaymentState(key: String): PaymentResult {
        // Poll status endpoint using the same idempotency key
        return runCatching {
            val status = paymentApi.checkStatus(key)
            paymentDao.updateStatus(key, status.toRecordStatus())
            if (status.isSuccess) PaymentResult.Success(status.receiptId)
            else PaymentResult.PendingConfirmation(key)
        }.getOrElse {
            PaymentResult.PendingConfirmation(key)
        }
    }
}
```

## Explanation in Arabic

قبل السيرفر عملية دفع مالي (Payment Accepted) لكن الاستجابة ضاعت في شبكة الهاتف (Lost Network Response). كيف تتعافى بأمان تام دون خصم العميل مرتين؟

1. فهم طبيعة الفشل (The Distributed Systems Dilemma):
   - أرسل العميل طلب `POST /orders/123/pay`.
   - قام السيرفر بالخصم من بطاقة الائتمان وأصدر إيصالاً بنجاح.
   - في نفس اللحظة، دخل الهاتف في نفق وانقطعت الشبكة، فاستقبل التطبيق `SocketTimeoutException`.
   - **من منظور الهاتف**: النتيجة مجهولة (Unknown Outcome)، وليست فشلاً! السيرفر قد يكون خصم المبلغ بنجاح.
   - **الخطأ الكارثي**: أن يعرض التطبيق رسالة 'فشلت العملية' ويطلب من المستخدم الضغط على زر 'ادفع الآن' مرة أخرى بمفتاح جديد، مما يؤدي إلى خصم المبلغ مرتين!

2. بروتوكول التعافي الآمن (Safe Recovery Protocol):
   - **المرحلة 1: توليد وحفظ Idempotency Key مسبقاً في Room**:
     * قبل إرسال أول طلب للسيرفر، يتم حفظ المعاملة محلياً في Room بحالة `PAYMENT_PENDING` مع معرف فريد ثابت (UUID) ومفتاح تكرار محدد: `idempotencyKey = "pay_ord_123"`.
   - **المرحلة 2: إظهار حالة غير مؤكدة للـ UI (Pending Reconciliation)**:
     * عند وقوع مهلة الاتصال، لا تعرض 'فشل' ولا تعرض 'نجاح'؛ اعرض: 'جارِ التحقق من حالة الدفع مع البنك'.
   - **المرحلة 3: استعلام استقصائي (Reconciliation Query)**:
     * يتم إرسال طلب استعلام آمن `GET /orders/123/payment-status` مستخدماً نفس المفتاح.
     * إذا وجد السيرفر المعاملة قد تمت، يعيد الإيصال ويتم تحديث الـ UI إلى `SUCCESS`.
     * إذا لم يجد السيرفر أي أثر، يتم إلغاء المعاملة بأمان.

## Practical walkthrough

تنفيذ بروتوكول استرداد الدفع المفقود باستخدام Idempotency Key والاستعلام الاستقصائي:
```kotlin
class PaymentRecoveryRepositoryImpl @Inject constructor(
    private val paymentApi: PaymentApiService,
    private val paymentDao: PaymentDao
) : PaymentRepository {

    override suspend fun executePayment(orderId: String, amountCents: Long): PaymentResult {
        // 1. توليد وتثبيت مفتاح التكرار محلياً قبل أي اتصال شبكي:
        val idempotencyKey = "idemp_${orderId}_$amountCents"
        paymentDao.recordIntent(orderId, idempotencyKey, PaymentStatus.PENDING)

        return try {
            // 2. إرسال الطلب:
            val receipt = paymentApi.chargeOrder(idempotencyKey, ChargeRequest(orderId, amountCents))
            paymentDao.updateStatus(orderId, PaymentStatus.CONFIRMED, receipt.receiptUrl)
            PaymentResult.Success(receipt)
        } catch (e: IOException) {
            // 3. انقطعت الشبكة بعد الإرسال! النتيجة غير مؤكدة:
            reconcileLostPayment(orderId, idempotencyKey)
        }
    }

    private suspend fun reconcileLostPayment(orderId: String, idempotencyKey: String): PaymentResult {
        // استعلام استقصائي باستخدام نفس المفتاح:
        return try {
            val statusResponse = paymentApi.getPaymentStatus(orderId, idempotencyKey)
            if (statusResponse.isPaid) {
                paymentDao.updateStatus(orderId, PaymentStatus.CONFIRMED, statusResponse.receiptUrl)
                PaymentResult.Success(statusResponse.toReceipt())
            } else {
                paymentDao.updateStatus(orderId, PaymentStatus.FAILED, null)
                PaymentResult.Failed("Payment was not processed by server. Please try again.")
            }
        } catch (e: Exception) {
            // لا زالت الشبكة مقطوعة: نعرض حالة انتظار التحقق للـ UI:
            PaymentResult.PendingVerification(orderId)
        }
    }
}
```

## Why it matters and how it works

A client-side timeout cannot reverse a server transaction. Stable operation identity plus server deduplication allows safe logical retries within the backend contract, but not exactly-once network execution. Persist pending/acknowledged states transactionally and audit transitions. If status endpoint lags, keep pending with bounded retry and support escalation.

## Worked example

Conceptual suspend workflow; Gateway status is authoritative and Store persists operation state. Never treat unknown as a failed charge.

```kotlin
sealed interface ChargeStatus { data object Pending: ChargeStatus
    data object Settled: ChargeStatus; data object Rejected: ChargeStatus }
interface Gateway {
    suspend fun status(operationId: String): ChargeStatus
    suspend fun charge(operationId: String, key: String): ChargeStatus
}
suspend fun recover(id: String, gateway: Gateway): ChargeStatus = gateway.status(id)
```

## Trade-offs and decision criteria

Immediate retry improves responsiveness only when server idempotency is documented and status is reconciled. Waiting for status reduces duplicate risk but can leave Pending UX longer. A support/audit path is essential for unresolved financial operations.

## Failure modes

A naive retry with a new key can create a second charge. A local Success write may fail after server success, so the next launch must query server rather than assume absence of local record means no charge. An idempotency key retention window may expire.

## Production perspective

A checkout backend stores a ledger operation keyed by client operation ID and exposes status. Android persists Pending before request, uses WorkManager for reconciliation after process death, and shows Pending/Settled/Rejected. Tests crash after server commit but before client acknowledgement.

## Interview answer — short

Recovering from lost payment responses requires client-generated Idempotency Keys persisted in Room before dispatching network calls. Upon experiencing timeouts, the client avoids blind retries to prevent duplicate charges, transitions the UI to a verification state, polls a status endpoint using the existing key, and delegates persistent background reconciliation to WorkManager.

## Interview answer — structured

Safely recovering when a payment response is dropped after server processing requires client-driven idempotency and defensive verification protocols.
First, generate an Idempotency-Key prior to network transmission. The client generates a unique UUID, persists it in Room with the pending payment details, and attaches it as an HTTP header.
Second, establish server idempotency semantics. If a network drop occurs and the same request is replayed, the backend recognizes the idempotency key and returns the original transaction receipt without charging the customer a second time.
Third, implement safe recovery instead of blind failure reporting. When encountering network timeouts, never display a generic payment failed error. Transition the UI to a pending verification state, query a dedicated payment status endpoint using the idempotency key, and enqueue a WorkManager job to reconcile the transaction reliably in the background.

## Interview answer — deep senior

In financial mobile engineering, dropped payment responses represent the classic distributed systems Two Generals' problem.
When a POST payment request succeeds on the banking gateway but the connection drops before the HTTP 200 payload returns to the phone, the Android client receives a SocketTimeoutException.
Rookie engineers often make two critical errors: either reporting an immediate payment failure which induces user panic, or automatically retrying the raw payment call which charges the customer's credit card twice.
To guarantee mathematical safety, we enforce a strict idempotency architecture.
Before any network bytes leave the device, our repository generates a cryptographically random UUID as an Idempotency-Key and commits the transaction into Room with status PENDING.
This key is injected into the HTTP request headers.
If OkHttp throws a SocketTimeoutException or network partition error, our recovery flow intercepts the exception.
The UI immediately transitions into an informational 'Verifying Payment Status' state with clear messaging.
The repository then queries a lightweight, side-effect-free status endpoint passing the idempotency key.
If the status check returns confirmed, we update Room and transition the UI to success.
If the device remains completely offline, we enqueue a dedicated WorkManager worker configured with Exponential Backoff and network constraints to resolve the payment status in the background, notifying the user via a system notification once confirmation is finalized.

## How to answer in the interview

- **Why:** Lost response creates an unknown outcome, not proven failure.
- **How:** Persist attempt identity, submit, then reconcile by status endpoint.
- **Trade-offs:** Retry only under provider key/payload/retention rules.
- **Failure cases:** New-key duplicate charge or premature “failed” UI.
- **Production solution:** PendingVerification state, worker recovery and lost-reply tests.

## Deep-dive talking points

Trace pre-send persistence, server commit, lost response and process restart.

## Follow-up questions

- **Interviewer:** "What is the danger of generating a new Idempotency Key on retry?"
  **Answer:** "Generating a new key treats the retry as an entirely new transaction, causing the server to process a second independent charge."

- **Interviewer:** "What HTTP status code should the server return on duplicate idempotent requests?"
  **Answer:** "HTTP 200 OK or 201 Created returning the original saved receipt, often accompanied by an `Idempotent-Replayed: true` header."

## Self-check rubric

Can I hold Pending, query authority, reuse key and test the commit/ack crash window?

## References and reviewed-on date

- [Kotlin withTimeout API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/with-timeout.html) — local deadline limitations.
- [Android offline-first guidance](https://developer.android.com/topic/architecture/data-layer/offline-first) — durable write synchronization.

Technically reviewed against primary documentation on 2026-10-13.
