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

## Concept and technical explanation

When a financial checkout or payment flow is abruptly killed by the operating system mid-operation (such as through background Low Memory Killer termination, configuration crashes, or battery death), the application enters an ambiguous state. In distributed systems, a lost client response must never be assumed to indicate that the remote transaction failed; the server may have successfully charged the customer's credit card and updated the ledger just as the client process died.
Engineering a resilient payment flow requires a strict division of responsibilities. What MUST NOT be repeated under any circumstance is the financial mutation call. Resubmitting an unverified payment charge blindly creates catastrophic duplicate billing, chargeback penalties, and severe customer distrust. What MUST be reconstructed is the user's transaction session, shopping cart summary, and durable transaction identifier. By generating a client-side UUID idempotency key before dispatching the payment and persisting it in local storage, the application can safely reconcile state with the backend upon process restoration by querying transaction status rather than issuing duplicate debits.

## Practical walkthrough (English)

Designing a resilient payment ViewModel backed by SavedStateHandle and durable repository synchronization:

```kotlin
class PaymentViewModel(
    private val savedStateHandle: SavedStateHandle,
    private val paymentRepository: PaymentRepository
) : ViewModel() {

    // Reconstructed securely from SavedStateHandle:
    private val orderId: String = checkNotNull(savedStateHandle["order_id"])
    private val idempotencyKey: String = savedStateHandle.get<String>("idempotency_key")
        ?: UUID.randomUUID().toString().also { savedStateHandle["idempotency_key"] = it }

    private val _uiState = MutableStateFlow<PaymentUiState>(PaymentUiState.Loading)
    val uiState: StateFlow<PaymentUiState> = _uiState.asStateFlow()

    fun resumePaymentFlow() {
        viewModelScope.launch {
            // NEVER charge again blindly! Reconcile status first:
            val status = paymentRepository.checkTransactionStatus(orderId, idempotencyKey)
            when (status) {
                is TransactionStatus.Success -> _uiState.value = PaymentUiState.Success(status.receipt)
                is TransactionStatus.Pending -> _uiState.value = PaymentUiState.Processing
                is TransactionStatus.NotFound -> {
                    // Safe to initiate payment because server has not seen this idempotency key
                    executeCharge(orderId, idempotencyKey)
                }
                is TransactionStatus.Failed -> _uiState.value = PaymentUiState.Failed(status.error)
            }
        }
    }

    private suspend fun executeCharge(orderId: String, key: String) {
        // Execute charge with idempotency key attached
    }
}
```

Failure scenario: An app dispatches a payment request without an idempotency key. The user switches to their authenticator app, causing the OS to kill the payment process. Upon returning, the app detects an incomplete order and automatically triggers a fresh payment call, charging the customer's credit card twice for the exact same order.

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

Never repeat the financial charge mutation blindly; an unreceived response does not prove payment failure. What must be reconstructed is the order ID, cart parameters, and a pre-generated client-side idempotency key preserved in SavedStateHandle and local database. Upon process restoration, query transaction status from the backend to reconcile state before allowing the user to retry.

## Interview answer — structured

In financial transactions, a terminated process or lost network response represents an indeterminate outcome, never a confirmed failure. The payment gateway may have committed the charge just as the client was reclaimed by the operating system, meaning we must never re-trigger the charge mutation automatically.

We enforce idempotency by generating a unique client-side UUID idempotency key before initiating the transaction. This key, along with the order ID and amount, is persisted immediately to durable local storage like Room and mirrored into SavedStateHandle.

In production, where the screen is recreated after process death, the ViewModel checks the transaction status against the backend using the order ID and idempotency key. If the server has already settled the charge, the UI transitions directly to the success confirmation screen. Only if the backend explicitly confirms the transaction was never received or failed safely do we enable a retry.

User interface state like selected payment methods and form inputs are reconstructed cleanly from SavedStateHandle, while sensitive card details and CVV codes are never persisted locally, ensuring strict compliance with PCI-DSS security standards.


## Interview answer — deep senior

From a distributed systems and fault-tolerance perspective, handling client death during payment processing is an instance of the Two Generals Problem. When a mobile client initiates an HTTP POST request to /api/v1/charge, several failure domains exist: the network may drop before reaching the server, the server may process the charge through payment processors like Stripe but fail before sending the response, or the Android Low Memory Killer (lmkd) may terminate the app process while the network connection is in flight. Assuming failure and re-executing the charge leads to duplicate card authorizations and chargeback disputes.
To build a bulletproof architecture, the client must generate an idempotency key before any network I/O occurs. This key is written synchronously to an encrypted local database table (Room with SQLCipher) alongside the order state marked as PENDING_AUTHORIZATION. The idempotency key is also injected into SavedStateHandle so that upon activity recreation, the ViewModelProvider restores the exact transaction context.
When the resurrected Activity initializes, the ViewModel enters a reconciliation state. It executes an idempotent status probe (such as GET /api/v1/orders/{orderId}/payment-status or passing the Idempotency-Key header). The backend payment service guarantees that identical idempotency keys yield identical responses without re-executing charges on payment rails. If the status returns SUCCEEDED, the client marks the local order as paid and navigates to the receipt screen. If the payment is still processing, the client subscribes to a WebSocket or polling mechanism with exponential backoff.
From a regulatory standpoint, PCI-DSS strictly prohibits persisting sensitive card verification values (CVV) or raw PANs in SavedStateHandle or local disk storage. Only tokenized payment tokens provided by the payment gateway SDK can be safely retained. By combining client-side idempotency, local transactional states, and server-driven reconciliation, the financial flow remains resilient against any unexpected process termination.

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
