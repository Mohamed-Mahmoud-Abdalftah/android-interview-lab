---
id: "SYS-05"
question: "Design a robust payment transaction lifecycle."
topic: "Android System Design & Architecture Decisions"
code: "SYS"
group: "A"
phase: 4
priority: "P1"
order: 334
editorial_status: "reviewed"
---

# SYS-05

## Original interview question

Design a robust payment transaction lifecycle.

## What the interviewer evaluates

Design payment lifecycle with idempotent backend, pending state and reconciliation.

## Explanation in Arabic

كيف تصمم دورة حياة معاملات دفع قوية ومرنة (Robust Payment Transaction Lifecycle) تمنع السحب المزدوج وتتحمل انقطاع الشبكة؟

1. التحديات القاتلة في مدفوعات الموبايل:
   - **مشكلة الانقطاع بعد الخصم (Payment in Flight Network Drop)**: المستخدم ضغط "ادفع الآن"، البنك خصم المبلغ، ولكن قبل أن تصل استجابة النجاح للهاتف انقطعت شبكة الإنترنت! إذا ضغط المستخدم "ادفع" مجدداً، قد يُخصم منه المبلغ مرتين!
   - **موت التطبيق أثناء معالجة البوابة (Process Death / Crash)**: إغلاق التطبيق أثناء انتظار تأكيد 3D Secure.

2. الركائز الهندسية لمعاملات الدفع:
   - **مفتاح عدم التكرار (Client-Side Idempotency Key)**: لكل عملية دفع يتم توليد `idempotencyKey = UUID()` فريد محلياً وتمريره في هيدر الطلب `Idempotency-Key: <uuid>`. إذا أعاد التطبيق إرسال نفس الطلب 10 مرات بسبب مشاكل الشبكة، يدرك السيرفر فوراً أنه نفس الطلب ويعيد نتيجة المعاملة الأولى دون تكرار الخصم!
   - **آلة حالات المعاملة الصريحة (Explicit State Machine)**:
     `INITIATED -> PROCESSING -> AUTHORIZED -> CAPTURED` أو `FAILED`.
   - **المطابقة التلقائية والاستعلام السيرفري (Polling / Reconciliation)**: عند انقطاع الاتصال أو إعادة فتح التطبيق بعد عطل، لا يعيد التطبيق محاولة الدفع، بل يستعلم عن حالة المعاملة الأصلية: `GET /payments/order/{orderId}` لمعرفة هل تم الخصم أم لا.
   - **Webhooks ومطابقة السيرفر**: السيرفر يعتمد على إشعارات Webhooks المباشرة من بوابة الدفع (Stripe/PayPal) كمصدر الحقيقة النهائي وليس استجابة تطبيق الموبايل.

## Practical walkthrough

تصميم نظام دفع قوي يعتمد على Idempotency Key ومطابقة الحالة عند الفشل وانقطاع الشبكة:
```kotlin
class PaymentTransactionCoordinator @Inject constructor(
    private val paymentApi: PaymentApiService,
    private val paymentDao: PaymentTransactionDao
) {
    suspend fun executePayment(orderId: String, amountCents: Long): PaymentResult {
        // 1. جلب أو إنشاء سجل المعاملة محلياً بمفتاح عدم تكرار فريد وثابت:
        val existingTx = paymentDao.getTransactionForOrder(orderId)
        val idempotencyKey = existingTx?.idempotencyKey ?: UUID.randomUUID().toString()

        if (existingTx == null) {
            paymentDao.insert(PaymentRecord(orderId, idempotencyKey, status = PaymentStatus.PENDING))
        }

        return try {
            // 2. إرسال طلب الدفع مع الـ Idempotency-Key في الهيدر
            val response = paymentApi.chargeOrder(
                idempotencyKey = idempotencyKey,
                request = ChargeRequest(orderId, amountCents)
            )

            paymentDao.updateStatus(orderId, PaymentStatus.COMPLETED)
            PaymentResult.Success(response.transactionId)
        } catch (e: IOException) {
            // 3. انقطاع الشبكة أثناء الدفع! لا تعيد المحاولة بالدفع؛ استعلم عن الحالة السيرفرية:
            reconcilePaymentStatus(orderId, idempotencyKey)
        }
    }

    private suspend fun reconcilePaymentStatus(orderId: String, idempotencyKey: String): PaymentResult {
        return try {
            val statusResponse = paymentApi.queryPaymentStatus(idempotencyKey)
            if (statusResponse.isPaid) {
                paymentDao.updateStatus(orderId, PaymentStatus.COMPLETED)
                PaymentResult.Success(statusResponse.transactionId)
            } else {
                PaymentResult.PendingResolution
            }
        } catch (e: Exception) {
            PaymentResult.NetworkErrorRequiresCheck
        }
    }
}
```

## Why it matters and how it works

Payment authorization and capture may be separate server operations with their own IDs and rules. Persist local intent and transition records; never trust device clock or balance as authority. Use bounded retry only with same key and status query. Reversal is a new linked operation, not deleting a row.

## Worked example

Conceptual Kotlin state representation; backend owns validation and ledger.

```kotlin
sealed interface PaymentState {
    data class Pending(val operationId: String) : PaymentState
    data class Authorized(val authId: String) : PaymentState
    data class Settled(val receiptId: String) : PaymentState
    data class Rejected(val reason: String) : PaymentState
    data class Unknown(val operationId: String) : PaymentState
}
```

## Trade-offs and decision criteria

Fast optimistic UI reduces perceived latency but is dangerous if it asserts success before server confirmation. Pending UX may be slower but honest. Server idempotency and status APIs cost engineering work; they are essential for safe retries.

## Failure modes

A timeout after server commit can be followed by a new key and double charge. A captured payment cannot be “rolled back” by deleting local state; it needs a server reversal/refund transition. Worker duplicate run must not duplicate ledger entries.

## Production perspective

A checkout persists operation ID/amount, submits through backend, shows Pending on timeout and schedules reconciliation. Server exposes ledger status and receipts; support monitors unresolved operations. Tests crash before send, after commit, before local acknowledgement and during reversal.

## Interview answer — short

Design a robust payment lifecycle by attaching a client-generated UUID idempotency key to each transaction, enforcing an explicit state machine, and never blindly retrying failed charges. If a network drop occurs in-flight, query the backend payment status using the idempotency key to reconcile transaction state without double-charging.

## Interview answer — structured

Payment flows require zero-tolerance for duplicate charges and resilient handling of network failures:

1. **Client-Generated Idempotency Keys**:
   - Before dispatching a charge request, generate a cryptographically unique `idempotencyKey = UUID()` and persist it locally in Room associated with the order ID.
   - Transmit this key in the HTTP header (`Idempotency-Key: <uuid>`). If network drops occur and the request is retried, payment gateways (e.g. Stripe, Adyen) recognize the key and return the original transaction receipt without re-executing charges.

2. **State Machine Modeling**:
   - Model the lifecycle with explicit states: `Created -> PaymentMethodAttached -> ActionRequired (3DS) -> Processing -> Succeeded / Failed`.

3. **In-Flight Network Disconnection Recovery (Reconciliation)**:
   - When an HTTP timeout occurs, the client does not know whether the charge succeeded on the gateway. **Never retry the charge mutation directly**. Instead, trigger a reconciliation query (`GET /payments/reconcile?key=<idempotencyKey>`) to retrieve the authoritative state.

4. **Server-to-Server Webhook Authority**:
   - The backend must not consider orders finalized solely because the mobile client returned success. Final order fulfillment is unlocked exclusively via authenticated server-side webhooks from the payment provider.

## Interview answer — deep senior

From a staff architecture perspective, payment systems require handling edge cases in client-side lifecycle and user interaction:

1. **UI Double-Tap & Concurrency Guards**: Prevent duplicate button clicks by disabling the UI immediately and using reactive StateFlow debounce mechanisms. The `executePayment()` method must be bounded by an in-memory Mutex to block concurrent triggers for the same order.

2. **3D Secure / Biometric Process Death**: When navigating to a 3DS webview or external banking app, the host Android OS may kill the main application under memory pressure. The app must persist order state and idempotency keys in persistent Room storage so that upon returning via Deep Link (`myapp://payment-return`), the activity reconstructs state and polls the backend for final status.

3. **Telemetry & PCI Auditing**: Mask PAN numbers (showing only first 6/last 4) in all UI logs, and completely eliminate CVV/CVC persistence from memory and storage post-tokenization.

## How to answer in the interview

- **Why:** client observations and financial state can diverge.
- **How:** persist operation identity, use backend ledger transitions, and reconcile ambiguous results.
- **Trade-off:** Pending UX is more complex than a simple success/failure toast.
- **Failure case:** retry with a new key after lost response.
- **Production solution:** server idempotency, authoritative status lookup, and auditable transitions.

## Deep-dive talking points

Draw payment states and justify how every crash window converges to authoritative status.

## Follow-up questions

- **Interviewer:** "What is the difference between authorization and capture in payments?"
  **Answer:** "Authorization holds the funds on the customer's card; Capture actually transfers the money to the merchant's account."

- **Interviewer:** "Why should the client never generate the charge amount directly?"
  **Answer:** "To prevent tampering; the client submits the order ID, and the server computes the authoritative amount from verified database inventory."

## Self-check rubric

Can I define states, preserve unknown outcomes and prevent duplicate charges?

## References and reviewed-on date

- [Android offline-first guidance](https://developer.android.com/topic/architecture/data-layer/offline-first) — durable pending operations.
- [Kotlin withTimeout API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/with-timeout.html) — timeout limits.

Technically reviewed against primary documentation on 2026-10-13.
