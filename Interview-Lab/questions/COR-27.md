---
id: "COR-27"
question: "A payment timeout occurs after a request reaches the server. How do you avoid duplicate charges on retry?"
topic: "Kotlin Coroutines & Concurrency"
code: "COR"
group: "C"
phase: 1
priority: "P1"
order: 108
editorial_status: "reviewed"
---

# COR-27

## Original interview question

A payment timeout occurs after a request reaches the server. How do you avoid duplicate charges on retry?

## What the interviewer evaluates

Handle payment timeout as an ambiguous server outcome using durable keys and reconciliation.

## Explanation in Arabic

حدوث Timeout في عملية الدفع بعد وصول الطلب للسيرفر وكيفية تجنب الخصم المزدوج (Duplicate Charges) هو سؤال معماري كلاسيكي في تطبيقات الـ Fintech والتجارة الإلكترونية:

1. المشكلة (The Two Generals Problem in Payments):
   - العميل ضغط 'تأكيد الدفع' بمبلغ 1,000 جنيه.
   - التطبيق أرسل الطلب للسيرفر، والسيرفر خصم المبلغ بالفعل.
   - ولكن قبل أن تصل رسالة الـ Response للموبايل، شبكة الهاتف قطعت أو حدث Socket Timeout على الموبايل!
   - الموبايل يظن أن الطلب فشل! لو أعاد المحاولة ببساطة، سيتم خصم 1,000 جنيه إضافية من حساب العميل (Double Charge)!

2. الحل المعماري الإلزامي: مفتاح التكرار الفريد (Idempotency Key):
   - قبل إرسال أول طلب، التطبيق يولد **UUID فريد خاص بهذه المعاملة** (`idempotencyKey = UUID.randomUUID().toString()`).
   - يحفظ هذا المفتاح فوراً في قاعدة البيانات المحلية (Room DB) مع حالة المعاملة `PENDING`.
   - يرسل الـ Header في طلب الـ HTTP: `X-Idempotency-Key: <UUID>`.
   - السيرفر وبوابة الدفع (مثل Stripe) يحتفظان بالمفتاح في الـ Cache/Database. لو وصلهم نفس الـ Key مرة ثانية أثناء الـ Retry، **لن يقوموا بخصم المبلغ مرة أخرى**؛ بل سيعيدون نتيجة المعاملة الأولى فوراً!

## Practical walkthrough

تنفيذ دورة حياة عملية دفع آمنة ضد التكرار (Idempotent Payment):
```kotlin
suspend fun executePayment(orderId: String, amount: BigDecimal): PaymentResult {
    // 1. توليد أو استرجاع مفتاح التكرار المخزن محلياً لهذه المعاملة:
    val transaction = paymentDao.getOrCreateTransaction(orderId) {
        PaymentEntity(orderId = orderId, idempotencyKey = UUID.randomUUID().toString())
    }
    
    // 2. إرسال الطلب مع المفتاح وإعادة المحاولة بأمان:
    return try {
        val response = paymentApi.charge(
            idempotencyKey = transaction.idempotencyKey,
            request = ChargeRequest(orderId, amount)
        )
        paymentDao.markSuccess(transaction.id, response.receiptId)
        PaymentResult.Success(response.receiptId)
    } catch (e: SocketTimeoutException) {
        // 3. عند حدوث Timeout، لا نكرر الخصم عشوائياً؛ نستعلم عن حالة المعاملة أولاً:
        reconcilePaymentStatus(transaction.idempotencyKey)
    }
}
```

## Why it matters and how it works

Coroutine timeout cancels client waiting, not necessarily the HTTP transport or server transaction. A server-side idempotency contract can deduplicate retries with the same stable key, but it does not prove exactly-once network execution. Persist pending state and key transactionally before request; recover after process death and verify authoritative status before any repeat.

## Worked example

Conceptual Android repository skeleton; `gateway` must enforce one charge per stable key and document its retention and payload-matching contract. The store persists before network send. A pending operation is reconciled later by status lookup.

```kotlin
import java.net.SocketTimeoutException

data class PaymentOp(val id: String, val key: String)
sealed interface PaymentOutcome {
    data class Confirmed(val receipt: String) : PaymentOutcome
    data object Pending : PaymentOutcome
}
interface PaymentStore {
    suspend fun savePending(op: PaymentOp)
    suspend fun markConfirmed(id: String, receipt: String)
}
interface PaymentGateway {
    suspend fun charge(op: PaymentOp): String
    suspend fun status(id: String): String
}
suspend fun submit(
    op: PaymentOp, store: PaymentStore, gateway: PaymentGateway,
): PaymentOutcome {
    store.savePending(op)
    val receipt = try {
        gateway.charge(op) // retry only with the same key and payload
    } catch (e: SocketTimeoutException) {
        return PaymentOutcome.Pending // do not infer server rejection
    }
    store.markConfirmed(op.id, receipt)
    return PaymentOutcome.Confirmed(receipt)
}
```

## Trade-offs and decision criteria

A stable key helps only if the server enforces deduplication with defined retention and payload matching. Status lookup/reconciliation increases complexity but prevents false failure claims and duplicate financial effects. Do not convert every timeout to a new charge attempt.

## Failure modes

Client cancellation after server acceptance can leave a pending charge. Process death can occur after send but before local success write. A new key on retry may charge again; reusing a key outside its server retention window may also be unsafe. Log operation IDs, not payment credentials.

## Production perspective

A checkout creates a unique operation, stores it as Pending, submits with a stable key, and on timeout checks server status. WorkManager resumes reconciliation from durable state. The backend ledger decides success/failure; customer UI shows Pending while uncertain, and support tooling can inspect the correlation ID.

## Interview answer — short

Generate a unique client-side Idempotency Key (UUID) persisted locally before making the payment request, and pass it in the HTTP header (e.g., X-Idempotency-Key). On network timeout, retrying with the same idempotency key instructs the server and payment gateway to deduplicate the transaction and return the original receipt rather than charging twice.

## Interview answer — structured

A payment timeout is the classic distributed systems challenge: the client cannot distinguish whether the request timed out before reaching the server, while being processed, or while the response was returning over the air. Retrying blindly risks catastrophic duplicate charges.

The industry-standard solution is **Idempotency Keys** paired with local persistence:

1. Before dispatching the payment request, the Android app generates a cryptographically unique UUID as an idempotency key and persists it locally in Room alongside the order ID.
2. The app sends this key in the request header (e.g., `X-Idempotency-Key: <uuid>`).
3. The backend and payment gateway (like Stripe or Adyen) check their distributed transaction store. If a request with that key was already executed, they return the original processed receipt without re-executing the charge.
4. If a timeout occurs, the app doesn't immediately prompt the user to re-pay. It performs a status reconciliation query (`GET /payments/status?key=<uuid>`) to check if the transaction succeeded before triggering any retries.

## Interview answer — deep senior

From an architectural resiliency standpoint, payment flows must never rely solely on transient UI state or a simple `viewModelScope.launch` retry loop. If the user loses network connectivity or kills the application during a payment timeout, an in-memory retry mechanism is lost forever.

To make payments robust: 1. We model payments as a local state machine in Room: `CREATED -> SUBMITTED -> SETTLED | FAILED`. 2. Upon a timeout, we dispatch an idempotent status check using WorkManager with exponential backoff constraints. Even if the process dies or the device is rebooted, WorkManager queries the backend to determine if the charge succeeded, updating the local database when connectivity is restored.

Finally, UI UX must guard against double-clicks by immediately disabling the 'Pay' button and enforcing a single submission token, preventing the user from triggering two parallel payment coroutines.

## How to answer in the interview

- **Why:** client timeout cannot establish payment outcome.
- **How:** persist a stable operation identity before sending and reconcile status after ambiguity.
- **Trade-off:** idempotency contracts and pending UX add complexity.
- **Failure case:** generating a new key on retry produces a duplicate charge.
- **Production solution:** server-enforced deduplication, an authoritative ledger, and auditable Pending state.

## Deep-dive talking points

Walk through crash points and distinguish idempotent logical operation from exactly-once network execution.

## Follow-up questions

- **Interviewer:** "What if the backend does not support idempotency keys?"
  **Answer:** "You must implement a two-phase check: first, call a payment intent or reservation endpoint that issues a server-side transaction ID with an expiration window. All subsequent charge or query requests reference this reservation ID."

- **Interviewer:** "How does WorkManager help in payment recovery?"
  **Answer:** "WorkManager guarantees execution across process death and device reboots. If a payment request times out and the user closes the app, a periodic or one-time WorkManager task reconciles payment status with the server in the background and posts a notification when confirmed."

- **Interviewer:** "Why shouldn't you generate the Idempotency Key in-memory in the ViewModel?"
  **Answer:** "Because if the Android OS kills the process due to low memory while the request is in flight, recreating the ViewModel will generate a brand-new UUID. Retrying with a new UUID would defeat idempotency and charge the customer twice."

## Self-check rubric

Can I name every crash window, use a stable key, reconcile status and avoid declaring an uncertain charge failed?

## References and reviewed-on date

- [Kotlin withTimeout API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/with-timeout.html) — local deadline semantics.
- [Android offline-first guidance](https://developer.android.com/topic/architecture/data-layer/offline-first) — durable queued writes/reconciliation patterns.

Technically reviewed against primary documentation on 2026-10-13.
