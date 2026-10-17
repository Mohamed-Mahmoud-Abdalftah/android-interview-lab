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

## Concept and technical explanation

A client-side timeout occurring after a payment request has been transmitted to a remote server represents the quintessential Two Generals Problem in distributed financial systems. When withTimeout or an underlying network socket timeout fires on a mobile client, it signifies lack of an acknowledgement, NOT failure of remote execution. The request payload may have reached the payment gateway, debited the user's funds, and persisted the transaction before the network connection dropped. Retrying the payment transaction naively with a new request risks catastrophic double charging. To guarantee financial safety and correctness, client architectures must enforce three foundational principles: client-generated idempotency keys, durable intent persistence, and post-timeout reconciliation. The mobile app must generate a cryptographically unique idempotency key (such as a UUID v4) and write the pending payment intent to local SQLite storage (Room) before making the network call. On timeout, the client transitions the local state to PENDING_RECONCILIATION and queries transaction status via a dedicated idempotency lookup endpoint before attempting any retry.

## Practical walkthrough (English)

Consider a robust Android payment repository workflow guarding against duplicate charges:
```kotlin
class PaymentRepository(
    private val paymentDao: PaymentDao,
    private val paymentApi: PaymentApi
) {
    suspend fun executePayment(orderId: String, amount: BigDecimal): PaymentResult {
        // 1. Generate and durably persist idempotency key BEFORE calling network:
        val idempotencyKey = UUID.randomUUID().toString()
        val intent = PaymentIntent(orderId, amount, idempotencyKey, status = Status.PENDING)
        paymentDao.insert(intent)

        return try {
            // 2. Call gateway with the idempotency key in the headers:
            val response = withTimeout(15_000L) {
                paymentApi.charge(idempotencyKey, ChargeRequest(orderId, amount))
            }
            paymentDao.updateStatus(idempotencyKey, Status.SUCCESS)
            PaymentResult.Success(response.transactionId)
        } catch (e: TimeoutCancellationException) {
            // 3. AMBIGUOUS OUTCOME: Never blindly retry! Enter reconciliation:
            paymentDao.updateStatus(idempotencyKey, Status.PENDING_RECONCILIATION)
            reconcilePaymentStatus(idempotencyKey)
        }
    }

    private suspend fun reconcilePaymentStatus(key: String): PaymentResult {
        // Query status endpoint using the identical idempotency key:
        return try {
            val status = paymentApi.queryStatus(idempotencyKey = key)
            if (status.isPaid) PaymentResult.Success(status.transactionId)
            else PaymentResult.Failed("Transaction aborted on gateway")
        } catch (e: Exception) {
            PaymentResult.RequiresManualReview(key)
        }
    }
}
```
If the network drops while processing, the identical idempotency key ensures the backend never executes a duplicate debit during reconciliation.

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

A payment timeout is an ambiguous state, not a confirmed failure; the server may have processed the charge. Blind retries cause duplicate charges. To avoid this, generate a unique idempotency key (UUID) and persist it locally before making the request. On timeout, never retry blindly: transition to a reconciliation state, query the payment status using the idempotency key, and retry only with the identical key.

## Interview answer — structured

Experiencing a timeout during a payment operation is an ambiguous outcome rather than a confirmed failure. The network request may have reached the backend and successfully charged the user's card right as the client-side socket dropped or timed out.

Performing an immediate, blind retry is a critical failure mode that causes duplicate financial deductions.

In production, resolving this distributed consensus hazard requires implementing the Idempotency Key pattern combined with local durable persistence. Before initiating the network request, the client generates a unique idempotency key—such as a UUID v4—and persists the payment intent in a local Room database. The network call transmits this key in the HTTP request headers. If the payment gateway receives repeated requests with the identical idempotency key, it guarantees that only one transaction is executed, returning the cached result for subsequent attempts.

When a timeout occurs, the client marks the transaction as pending reconciliation. Instead of re-charging, the application queries a transaction inquiry endpoint using the stored idempotency key to determine the true server state before deciding whether to retry or display a confirmation.


## Interview answer — deep senior

Under the hood, network timeouts represent an unresolvable partition in the CAP theorem. A client-side TimeoutCancellationException indicates solely that the local delay timer expired before bytes arrived on the TCP stream; it provides zero information regarding whether the server executed the SQL transaction. In enterprise financial mobile applications, handling this boundary requires a strict state machine implemented in local SQLite with write-ahead logging (WAL). The lifecycle transitions through Created, InFlight, Succeeded, Failed, and Ambiguous (PendingReconciliation). The idempotency key must be generated on the client, not by the server, because server generation requires a preliminary round-trip that itself can fail or time out. When the HTTP POST /charges executes with Header Idempotency-Key: <UUID>, the backend payment gateway (such as Stripe or Adyen) inserts the key into a distributed transaction table using unique constraints. If a timeout occurs, the mobile client must treat the outcome as indeterminate. It enters a reconciliation workflow: first, it attempts an idempotent status check via GET /charges/{idempotency_key}. If the status inquiry succeeds and confirms the charge, the local database transitions to Succeeded and the user is shown an order receipt. If the inquiry confirms that the charge was never created, the client can safely retry the POST using the exact same idempotency key. If the network remains completely partitioned or the app process is terminated by the OS Low Memory Killer during timeout handling, the pending state remains persisted in Room. Upon app relaunch, or via an injected Jetpack WorkManager PeriodicWorkRequest, the reconciliation worker runs in the background, resolving any lingering ambiguous transactions without requiring user intervention. This architecture completely eliminates double charges while maintaining full user confidence.

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
