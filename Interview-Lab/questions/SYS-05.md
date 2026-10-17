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

## Concept and technical explanation

Designing a robust mobile payment transaction lifecycle requires treating the mobile client as an untrusted, highly volatile coordinator. Mobile devices face abrupt network drops, socket timeouts, low-memory process termination, and unpredictable user abandonment during critical payment steps. Under no circumstances should the mobile client be the final authority on payment success or failure, nor should an ambiguous network timeout ever be interpreted as a failed transaction. A resilient architecture relies on client-generated idempotency keys, an explicit payment state machine (Draft, Processing, Pending Verification, Authorized, Settled, and Failed), durable transaction records in local persistence, and background reconciliation loops combining push notifications with exponential backoff polling to verify actual transaction state before permitting retries.

## Practical walkthrough (English)

Implementing a resilient payment state machine and reconciliation flow:
```kotlin
// 1. Explicit payment state machine representing all lifecycle stages
sealed interface PaymentTransactionState {
    data object Idle : PaymentTransactionState
    data class Processing(val idempotencyKey: String) : PaymentTransactionState
    data class PendingVerification(val idempotencyKey: String, val orderId: String) : PaymentTransactionState
    data class Succeeded(val transactionId: String, val orderId: String) : PaymentTransactionState
    data class Failed(val reason: String, val canRetrySafely: Boolean) : PaymentTransactionState
}

// 2. Payment repository orchestrating idempotency and status reconciliation
class PaymentRepositoryImpl @Inject constructor(
    private val paymentApi: PaymentApiService,
    private val paymentDao: PaymentDao
) : PaymentRepository {

    override suspend fun executePayment(orderId: String, amountCents: Long): PaymentTransactionState {
        val idempotencyKey = UUID.randomUUID().toString()

        // 1. Persist intent locally before initiating network request
        paymentDao.insert(
            PaymentEntity(orderId = orderId, idempotencyKey = idempotencyKey, state = "PROCESSING")
        )

        return try {
            val response = paymentApi.charge(
                idempotencyKey = idempotencyKey,
                request = ChargeRequest(orderId = orderId, amountCents = amountCents)
            )

            if (response.isSuccessful && response.body()?.status == "AUTHORIZED") {
                paymentDao.updateState(orderId, "SUCCEEDED")
                PaymentTransactionState.Succeeded(response.body()!!.transactionId, orderId)
            } else {
                paymentDao.updateState(orderId, "FAILED")
                PaymentTransactionState.Failed(response.errorBody()?.string() ?: "Declined", canRetrySafely = true)
            }
        } catch (e: IOException) {
            // CRITICAL: Network timeout is NOT a failure. Must reconcile to prevent double charge!
            paymentDao.updateState(orderId, "PENDING_VERIFICATION")
            PaymentTransactionState.PendingVerification(idempotencyKey, orderId)
        }
    }
}
```

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

We design payment lifecycles around idempotency and explicit state machines where the backend remains the ultimate authority. Every payment intent receives a client-generated UUID idempotency key. If a network timeout occurs during authorization, the client transitions into a pending verification state rather than failing. We poll the backend or await push notifications to reconcile the actual payment status before allowing any retry, preventing double charging.

## Interview answer — structured

Designing a robust payment transaction lifecycle requires handling network drops, process death, and payment gateway redirects without risking double charging.
The architecture centers on an explicit payment state machine with states like Draft, Processing, Pending Verification, Authorized, and Failed.
When a user taps to pay, we generate a unique idempotency key on the device and submit it with the payment intent.
The backend uses this key to ensure that duplicate HTTP submissions execute exactly once.
If the network drops or the HTTP socket times out while awaiting the gateway response, we strictly avoid marking the payment as failed.
Instead, we persist the transaction locally as Pending Verification and inform the user that payment confirmation is in progress.
The mobile client initiates exponential backoff polling against a dedicated transaction status endpoint, while also listening for Firebase Cloud Messaging push webhooks triggered by backend-to-gateway callbacks.
Only when the backend confirms final settlement does the state transition to Completed.
This eliminates duplicate charges and maintains financial integrity under worst-case mobile connectivity.

## Interview answer — deep senior

From a staff-level systems perspective, the most critical vulnerability in mobile payment design is the ambiguous network timeout.
When an HTTP POST request to execute a payment times out, the client cannot know whether the packet was lost on the outbound journey, processed successfully by the payment provider with a lost response, or rejected mid-flight.
Treating a timeout as a failure invites the user to tap pay again, causing an immediate double debit and severe customer dissatisfaction.
To solve this, our payment architecture decouples payment execution from payment reconciliation.
The initial submission creates a durable transaction record in local storage containing the idempotency key, amount, and order ID, locking the checkout UI against further interaction.
If the response drops, our background sync layer and UI polling mechanism query the backend using the same idempotency key to inspect the server's ledger.
If the backend has not received the transaction, it safely cancels the intent or permits a guarded retry.
If the payment succeeded at the gateway, the backend returns the settled order, and the client transitions seamlessly to the success confirmation screen.
Furthermore, we log comprehensive audit trail events across every lifecycle transition, enabling operational support teams to trace discrepancies between mobile telemetry, payment gateway logs, and core banking ledgers.

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
