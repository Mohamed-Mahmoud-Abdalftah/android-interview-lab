---
id: "AND-21"
question: "A payment screen is killed by Android mid-operation. What must be reconstructed, and what must not be repeated?"
topic: "Android Fundamentals, Lifecycle & Context"
code: "AND"
group: "C"
phase: 1
priority: "P1"
order: 51
editorial_status: "reviewed"
---

# AND-21

## Original interview question

A payment screen is killed by Android mid-operation. What must be reconstructed, and what must not be repeated?

## What the interviewer evaluates

- Treat a lost client response as an unknown outcome rather than proof of failure.
- Separate reconstructable UI state from durable transaction identity and server authority.
- Explain safe retry, idempotency, reconciliation, and process-death testing.

## Explanation in Arabic

مقتل شاشة الدفع بواسطة نظام أندرويد في منتصف العملية (Payment Screen killed mid-operation): ماذا يجب إعادة بنائه وما الذي يجب ألا يتكرر؟

1. ما الذي يجب ألا يتكرر إطلاقاً (MUST NOT BE REPEATED)?
   - **خصم الأموال من بطاقة العميل (The Financial Charge Call):**
     * لو كان طلب الدفع قد تم إرساله للسيرفر بالفعل، **ممنوع تماماً إعادة إرسال طلب خصم جديد (No duplicate charge)!**
     * لا تقم بتوليد `Idempotency Key` جديد؛ استخدم نفس المفتاح القديم.

2. ما الذي يجب إعادة بنائه واستعادته (MUST BE RECONSTRUCTED)?
   - **حالة الشاشة (UI State):** من خلال `SavedStateHandle`، استرجع: `orderId`, `amount`, و `idempotencyKey`.
   - **الاستعلام عن حالة العملية (Reconciliation Query):** بدلاً من الدفع مجدداً، أرسل استعلاماً للسيرفر: 'ما هي حالة المعاملة ذات المفتاح X؟' (`GET /orders/{id}/payment-status`).
     * لو السيرفر أكد نجاحها: انتقل فوراً لشاشة الإيصال (Receipt Screen).
     * لو لم تتم: اسمح للمستخدم بإعادة المحاولة يدوياً.

3. ضمانات الـ Backend و WorkManager:
   - إرسال طلبات الدفع الحيوية يفضل أن يكون عبر `WorkManager` حتى يضمن إكمال العملية حتى لو مات التطبيق بالكامل.

## Practical walkthrough

هندسة استعادة شاشة الدفع بعد Process Death في ViewModel:
```kotlin
class PaymentViewModel(
    private val savedStateHandle: SavedStateHandle,
    private val paymentRepository: PaymentRepository
) : ViewModel() {

    // 1. استعادة معرف العملية ومفتاح التكرار بعد مقتل الشاشة:
    private val orderId: String = checkNotNull(savedStateHandle["order_id"])
    private val idempotencyKey: String = checkNotNull(savedStateHandle["idempotency_key"])

    init {
        // 2. التحقق من الحالة الحقيقية أولاً بدون سحب أموال جديدة:
        reconcilePaymentStatus()
    }

    private fun reconcilePaymentStatus() = viewModelScope.launch {
        _uiState.value = PaymentUiState.VerifyingStatus
        when (val status = paymentRepository.queryPaymentStatus(idempotencyKey)) {
            is PaymentStatus.Completed -> _uiState.value = PaymentUiState.Success(status.receipt)
            is PaymentStatus.NotFound -> _uiState.value = PaymentUiState.ReadyToPay
            is PaymentStatus.Processing -> _uiState.value = PaymentUiState.Processing
        }
    }
}
```

## Why it matters and how it works

Process death destroys in-memory state and may occur after the server committed a payment but before the device received a response. The app therefore needs durable operation identity written before submission, an API contract that binds retries to the same idempotency key and unchanged parameters, and a status endpoint or webhook-backed backend record. On restoration, read the persisted attempt, authenticate the user, fetch authoritative status, then render succeeded, declined, pending, or unknown. Small saved UI state may restore the selected screen, but it is not the payment ledger.

## Worked example

Illustrative sequence with an app database and server contract: `transaction { insert(attemptId, orderId, idempotencyKey, PENDING) }`; submit the order through the backend; if the HTTP response is lost, persist `UNKNOWN` for this attempt rather than another new attempt; on screen recreation, fetch `GET /payment-attempts/{attemptId}`. A retry is permitted only when backend semantics explicitly accept the same key and payload. The pseudocode is architectural; the endpoint and atomicity guarantees must be provided by the actual backend.

## Trade-offs and decision criteria

Immediate screen reconciliation improves feedback but requires connectivity; scheduled recovery with WorkManager can continue after the UI leaves, subject to OS scheduling and network constraints. Server webhooks can establish eventual status but need authentication, replay defense, and duplicate handling. Local Room persistence helps the client remember identity, yet cannot make a charge exactly once. Provider idempotency is scoped to its documented retention and parameter rules; the backend should own the durable business transaction and avoid relying solely on a client-generated key.

## Failure modes

A naive `onCreate { charge() }` creates a second charge after recreation. A timeout handler that labels the payment failed might falsely encourage the user to pay again. A key reused with different amount or merchant data can be rejected or produce unsafe semantics. A local success flag can be stale or tampered with. Handle explicit declines, timeout/unknown, authentication expiry, and server status unavailability separately; alert operations on attempts stuck pending beyond a defined threshold.

## Production perspective

Persist attempt identity before submission, bind it to authenticated order and amount on the backend, and make status reads safe to repeat. The screen observes a repository that reconciles local state with server state. A unique WorkManager job may retry *status lookup* after restart; it should not initiate a new financial operation unless the server contract proves it safe. Tests inject process death before request, after server commit/before response, and during reconciliation, then assert one logical attempt and a recoverable UI. Log opaque attempt IDs rather than card data.

## Interview answer — short

Do NOT repeat the financial charge request or regenerate the idempotency key, preventing double billing. DO reconstruct the order details and original transaction idempotency key via SavedStateHandle, and execute an idempotent reconciliation query (GET /status) to verify whether the payment succeeded on the backend before offering a retry.

## Interview answer — structured

When a payment screen is killed by the OS mid-operation, the golden architectural rule is: **Separate state reconstruction from transactional execution**.

**What must NOT be repeated:**

- Never re-execute the financial charge API call automatically upon screen recreation.
- Never generate a new transaction ID or fresh idempotency key. Repeating a POST charge request will bill the customer twice if the backend already processed the initial request before the app was killed.

**What MUST be reconstructed:**

- Restore the transaction metadata (`orderId`, `amount`, and the existing `idempotencyKey`) from `SavedStateHandle`.
- Immediately execute an **Idempotent Status Reconciliation Query** (`GET /payments/status?key=<uuid>`). If the backend settled the charge during the process kill, restore the UI straight into `PaymentSuccess(receipt)`. If the backend confirms no transaction occurred, restore the UI to `ReadyToSubmit`, enabling the customer to retry safely.

## Interview answer — deep senior

From a mission-critical Fintech reliability perspective, payment dispatches should ideally not rely exclusively on in-memory ViewModel scopes. If the transaction submission was initiated via an application-level CoroutineScope or an expedited **WorkManager** worker, the background task might still be executing on the network thread while the UI is killed.

By maintaining a local transaction entity in Room:

```text
Order #1234 -> Status: SUBMITTING | Idempotency: 8a7f-43b2
```

When the recreated Activity and ViewModel spin up, they observe the Room entity. If the background worker finishes in Room with `Status: SUCCESS`, the UI updates automatically to the Success screen without any duplicate API calls, guaranteeing zero financial inconsistencies.

## How to answer in the interview

- **Why:** UI death does not roll back a server-side financial side effect.
- **How:** Persist attempt identity, then reconcile a pending outcome from the backend.
- **Trade-offs:** Retry only under a documented same-key idempotency contract.
- **Failure cases:** Explain a lost response and duplicate charge from a new request key.
- **Production solution:** Restore pending state, query status, and never store raw card/PIN data.

## Deep-dive talking points

Discuss write-before-send ordering, uncertain network outcomes, provider versus backend idempotency scope, status read versus charge retry, webhook reconciliation, process-death testing, and how to avoid logging sensitive payment material.

## Follow-up questions

- **Interviewer:** "Where should the idempotency key be generated?"
  **Answer:** "Locally on the device before the initial submission, persisted immediately in Room and SavedStateHandle so that it survives both configuration changes and process death."

- **Interviewer:** "What if the user clicks the 'Pay' button and rapidly presses Home?"
  **Answer:** "The payment request should be handed off to an application-scoped repository coroutine or WorkManager so that backgrounding the screen does not abort the in-flight payment request."

- **Interviewer:** "How do you prevent the user from clicking 'Pay' twice before the request leaves the device?"
  **Answer:** "Immediately disable the UI pay button upon the first tap, and guard the ViewModel submit function with a mutual exclusion lock (`Mutex`) or atomic state flag."

## Self-check rubric

Place the durable write before the network send; distinguish timeout from decline; identify the backend as status authority; describe one safe retry condition; and test at least three process-kill points without issuing a second logical payment.

## References and reviewed-on date

- [Android save UI states](https://developer.android.com/topic/libraries/architecture/saving-states) — process restoration and saved-state limits.
- [Android persistent work](https://developer.android.com/develop/background-work/background-tasks/persistent) — recovery scheduling limits.
- [Stripe idempotent requests](https://docs.stripe.com/api/idempotent_requests) — one provider's documented key and parameter semantics; other providers require their own contract review.

Technically reviewed against primary documentation on 2026-10-13.
