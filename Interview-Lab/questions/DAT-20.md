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

Recover safely from lost payment responses by treating network drops on mutating requests as uncertain outcomes, never outright failures. Persist an Idempotency Key in Room prior to network dispatch. Upon timeout, query a dedicated status reconciliation endpoint using that key rather than issuing a fresh charge with a new ID.

## Interview answer — structured

In distributed mobile networking, a lost response after a mutating payment request represents an **Uncertain Outcome (the Two Generals' Problem)**. The server may have already committed the card charge. Retrying blindly or showing a failure screen causes double charges and furious customers.

A production recovery architecture operates in three phases:

1. **Pre-Flight Idempotency Persistence**: Prior to making the network call, persist the transaction intention in Room: `orderId`, `amount`, `status = PENDING`, and a deterministic `Idempotency-Key` (e.g. `UUID`).

2. **State Transition to Uncertain UI**: If the call fails with `SocketTimeoutException` or `IOException`, do **NOT** show a 'Payment Failed - Tap to Retry' button. Update local state to `PaymentStatus.PENDING_VERIFICATION` and inform the user: 'Verifying payment with your bank...'.

3. **Authoritative Reconciliation**: Query a dedicated reconciliation endpoint (`GET /orders/{id}/payment-status` or re-issue the `POST` with the *identical* Idempotency-Key). A compliant backend recognizes the key and returns the existing transaction status without charging again. If the server confirms payment, update local state to `SUCCESS`.

## Interview answer — deep senior

From an engineering telemetry and edge-case standpoint:

1. **Background Polling via WorkManager**: If the user closes the app while in `PENDING_VERIFICATION`, schedule a constrained `PaymentReconciliationWorker` in WorkManager. When connectivity returns, the worker polls the backend, resolves the payment receipt, and triggers a local notification: 'Your order #123 is confirmed!'.

2. **Backend Webhooks as Secondary Confirmation**: In robust payment flows (Stripe, Adyen, Apple Pay), mobile apps do not rely solely on client polling. The payment provider delivers an asynchronous server-to-server webhook directly to your backend. The backend updates the order status in the cloud database, which your app observes via WebSocket or a silent push notification upon relaunch.

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
