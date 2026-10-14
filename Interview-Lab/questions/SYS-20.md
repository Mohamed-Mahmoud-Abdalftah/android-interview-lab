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

Never retry timed-out payments blindly. Persist a client-generated UUID idempotency key before dispatching charges. On timeout or app restart, initiate a reconciliation query (GET /payments/reconcile?key=uuid) to verify whether the backend authorized the charge, transitioning to success if captured, or retrying safely with the same key if not found.

## Interview answer — structured

When a payment request times out, the client cannot distinguish between a failure during request delivery versus a failure during response delivery. Recovering gracefully requires a strict reconciliation workflow.

First, **Pre-Flight Local Persistence**. Next, before dispatching the payment request, insert an atomic transaction record into Room containing the order ID, a client-generated UUID `idempotencyKey`, and status `IN_FLIGHT`.
**Handling Timeouts Without Blind Retries**. If the network drops or the socket times out, **do not replay the charge mutation**. Re-invoking charge mutations without idempotency guarantees creates duplicate charges.
Transition local state to `PENDING_RECONCILIATION` and disable immediate retry buttons on the UI. **Idempotent Reconciliation Protocol**.
Dispatch a read-only reconciliation query (`GET /payments/status?idempotency_key=<key>`). If the backend returns `CAPTURED` or `AUTHORIZED`, update local storage to `SUCCESS` and navigate to the order confirmation screen.
If the backend returns `TRANSACTION_NOT_FOUND`, the original request never reached the payment gateway. The client can now safely retry the charge using the identical idempotency key. **Startup Reconciliation Hooks**.
Finally, if the app crashed or was killed during timeout, check for unresolved `PENDING_RECONCILIATION` records on next launch, reconciliate them in the background, and notify the user via a banner.


## Interview answer — deep senior

From a distributed systems and fintech compliance perspective, client reconciliation must interface with server webhooks.

First, a Server Webhook Authority is the payment processor (e.g. Stripe/Adyen) notifies your backend asynchronously via cryptographic webhooks (`payment_intent.succeeded`). Even if the mobile device stays offline for hours, the backend marks the order paid and sends a push notification. Next, with Polling Backoff & Timeout Windows, implement a polling state machine with exponential backoff for the reconciliation endpoint (polling at 2s, 4s, 8s intervals, capping at 30s). If reconciliation remains unresolved after 30 seconds, transition the UI to an asynchronous pending screen: 'Your payment is being verified with your bank. We will notify you shortly.'
Finally, with Customer Support Idempotency Traceability, display the idempotency key or a short human-readable transaction reference on the pending UI screen. If customer support is contacted, agents can query the payment gateway logs instantly using that exact key.


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
