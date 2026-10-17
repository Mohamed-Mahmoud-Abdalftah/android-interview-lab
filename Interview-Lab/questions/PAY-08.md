---
id: "PAY-08"
question: "How do you avoid duplicate payment requests after UI timeout?"
topic: "Bonus: Payment/POS & Security Scenarios"
code: "PAY"
group: "B"
phase: 5
priority: "P2"
order: 478
editorial_status: "reviewed"
---

# PAY-08

## Original interview question

How do you avoid duplicate payment requests after UI timeout?

## What the interviewer evaluates

- Timeout as unknown, not declined.
- Stable operation ID, authoritative lookup and guarded user retry.

## Concept and technical explanation

Preventing duplicate payment requests following a user interface (UI) timeout requires strict architectural separation between UI presentation timeouts and underlying network transaction lifecycles:
- The UI Timeout vs Network Timeout Fallacy:
  - When a payment spinner reaches a UI timeout limit (e.g., 15 seconds), developers often pop the screen or re-enable the "Pay Now" button.
  - If the background network socket is still alive or pending at the bank gateway, the user taps "Pay Now" a second time, triggering an immediate duplicate charge.
- Key Prevention Mechanisms:
  1. Transactional State Gatekeeping via Local Database:
     - The UI must observe a single source of truth from Room (e.g., `StateFlow<PaymentStatus>`) rather than transient ViewModel or Coroutine states.
     - While a transaction is `INITIATED` or `PROCESSING`, the database enforces an in-flight lock. Any attempt to start a new payment for the same order is rejected with `PaymentInProgressException`.
  2. UI Hard-Disable and Monotonic State Rendering:
     - When the UI timeout fires, the "Pay Now" button remains permanently disabled.
     - The UI transitions to an ambiguous inquiry screen ("Verifying payment status with bank...").
  3. Status Inquiry Instead of Re-Authorizing:
     - Rather than initiating a new charge, retry buttons after a timeout must route strictly to a Status Polling Endpoint (`GET /v1/payments/{orderId}/status?idempotencyKey=...`).
     - If the status inquiry returns `PENDING`, the app waits; if `APPROVED`, it displays the receipt; if `NOT_FOUND` after a grace period, it triggers the reversal and allows safe re-entry.

## Practical walkthrough (English)

Decoupling UI timeout from transaction lifecycle and routing retries to status polling in Kotlin:
```kotlin
class PaymentViewModel(
    private val paymentRepository: PaymentRepository,
    private val orderId: String
) : ViewModel() {

    private val _uiState = MutableStateFlow<PaymentUiState>(PaymentUiState.Idle)
    val uiState: StateFlow<PaymentUiState> = _uiState.asStateFlow()

    fun onPayClicked(amount: Long) {
        viewModelScope.launch {
            _uiState.value = PaymentUiState.Processing

            try {
                // UI enforce a 15-second visual timeout without killing background transaction
                withTimeout(15_000L) {
                    val result = paymentRepository.executePayment(orderId, amount)
                    _uiState.value = PaymentUiState.Success(result.authCode)
                }
            } catch (e: TimeoutCancellationException) {
                // UI TIMEOUT FIRED: Never re-enable Pay button! Transition to Status Inquiry
                _uiState.value = PaymentUiState.InDoubtCheckStatus
            }
        }
    }

    // Retries strictly query gateway status rather than re-charging!
    fun onCheckStatusClicked() {
        viewModelScope.launch {
            _uiState.value = PaymentUiState.Processing
            val status = paymentRepository.queryPaymentStatus(orderId)
            _uiState.value = when (status) {
                is StatusResult.Approved -> PaymentUiState.Success(status.authCode)
                is StatusResult.NotFound -> PaymentUiState.SafeToRetry
                is StatusResult.Pending -> PaymentUiState.InDoubtCheckStatus
            }
        }
    }
}
```

## Explanation in Arabic

كيف تمنع طلبات الدفع المكررة (Duplicate Payment Requests) الناتجة عن نفاد وقت واجهة المستخدم (UI Timeout) أو نقر العميل المتكرر؟

1. سيناريوهات التكرار الشائعة في واجهة المستخدم (UI Hazards):
   - **1. النقر المزدوج المتسارع (Double-Tapping / Rapid Clicks)**: ينقر المستخدم على زر "تأكيد الدفع" مرتين بسرعة قبل أن يتم تعطيل الزر (Disable).
   - **2. نفاد وقت الواجهة (UI Timeout)**: تستغرق استجابة البنك 25 ثانية، بينما شاشة التطبيق مضبوطة على إظهار رسالة خطأ بعد 15 ثانية! يرى المستخدم رسالة فشل، فيضغط الزر مرة ثانية بينما الطلب الأول ما زال قيد المعالجة في البنك!
   - **3. استدارة الشاشة (Configuration Changes)**: تدوير الشاشة يعيد إنشاء الـ Activity فيقوم بكود البدء مرة أخرى إذا لم تكن المعمارية سليمة.

2. آليات المنع متعددة الطبقات (Multi-Layer Defense):
   - **الطبقة 1: واجهة المستخدم (UI Layer - Debounce & State)**:
     * تعطيل زر الدفع فوراً عند أول نقرة (`enabled = false`) وإظهار مؤشر تحميل (Loading Spinner).
     * استخدام `throttleFirst(1000ms)` في تدفقات Compose أو Coroutines لمنع النقرات المتتالية.
   - **الطبقة 2: طبقة إدارة الحالة (ViewModel & State Machine)**:
     * استخدام كائن حالة أحادي (`PaymentUiState.Processing`)؛ إذا كان الـ ViewModel في حالة `Processing`، يتجاهل أي حدث دفع جديد فوراً.
   - **الطبقة 3: طبقة النطاق والبيانات (Repository & Mutex)**:
     * استخدام **Kotlin `Mutex`** لمنع إطلاق دالتين للدفع بالتوازي لنفس الـ Session.
   - **الطبقة 4: طبقة الشبكة (Network - Idempotency Key)**:
     * ربط الطلب بـ Idempotency-Key محفوظ في Room، بحيث يرفض الخادم أي طلب مكرر لنفس المعاملة.

## Practical walkthrough

تنفيذ هندسي متكامل لمنع تكرار طلبات الدفع عبر الطبقات الثلاث:
```kotlin
// 1. في الـ ViewModel: حماية عبر Mutex وحالة المعالجة الأحادية:
class CheckoutViewModel(private val repository: PaymentRepository) : ViewModel() {
    private val paymentMutex = Mutex()
    private val _uiState = MutableStateFlow<CheckoutUiState>(CheckoutUiState.Idle)
    val uiState: StateFlow<CheckoutUiState> = _uiState.asStateFlow()

    fun onPayClicked(orderId: String, amount: Long) {
        viewModelScope.launch {
            // حماية Mutex: إذا كان هناك دفع جاري، يتم تجاهل النقرة فوراً:
            if (!paymentMutex.tryLock()) return@launch
            try {
                _uiState.value = CheckoutUiState.Processing
                val result = repository.executePayment(orderId, amount)
                _uiState.value = CheckoutUiState.Success(result)
            } catch (e: Exception) {
                _uiState.value = CheckoutUiState.Error(e.message ?: "Payment failed")
            } finally {
                paymentMutex.unlock()
            }
        }
    }
}

// 2. في واجهة Compose: زر معطل ومحمي ضد النقر المتكرر:
@Composable
fun CheckoutScreen(viewModel: CheckoutViewModel) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()
    val isProcessing = state is CheckoutUiState.Processing

    Button(
        onClick = { viewModel.onPayClicked("ord_123", 5000) },
        enabled = !isProcessing // تعطيل الزر فورياً عند بدء الدفع
    ) {
        if (isProcessing) {
            CircularProgressIndicator(modifier = Modifier.size(24.dp))
        } else {
            Text("Pay $50.00")
        }
    }
}
```

## Why it matters and how it works

HTTP transport timeout gives no knowledge of remote commit. The app persists the intent before sending and observes a backend-owned state. The backend atomically deduplicates retries and exposes status lookup; provider retention windows and request-parameter rules vary.

## Worked example

A customer taps Pay, then the app times out. UI displays “Checking payment” with an opaque reference and allows safe resume after process death. The repository calls `lookup(operationId)`; if still unknown, it schedules reconciliation and keeps checkout locked to that intent rather than starting a new payment.

## Trade-offs and decision criteria

A conservative pending state adds user friction but avoids double charges. An immediate retry can be safe only when the same server/provider operation identity is honored. A cancel button may mean “stop waiting,” not “reverse approved payment.”

## Failure modes

Creating a new UUID on each button tap can double-charge. Marking timeout as declined can prompt the same mistake. Test response lost after server success and duplicate taps from two devices.

## Production perspective

Backend/terminal metrics track unresolved age and duplicate attempts. Customer support can query by operation ID without card data. Long-running unknown states have a reconciliation and escalation path.

## Interview answer — short

Avoid duplicate payment requests after a UI timeout by keeping the Pay button disabled and never dispatching a new charge. Instead, transition the screen to an in-doubt verification state that routes retries exclusively to a status inquiry endpoint, checking whether the backend captured the transaction before allowing any safe re-payment.

## Interview answer — structured

Preventing duplicate payment requests after a UI timeout requires decoupling the user interface presentation from the underlying financial transaction lifecycle.
When a loading spinner exceeds a UI timeout threshold, applications must never simply dismiss the screen or restore the Pay button to an active state. If the bank is still processing the initial request, tapping the button again submits a duplicate charge instruction.
To prevent this, the payment lifecycle must be governed by a local database state machine rather than transient UI coroutines. When a UI timeout occurs, the button remains strictly disabled. The UI displays an in-doubt message informing the user that the payment status is being verified.
Furthermore, any user-facing retry action must be rerouted to a status inquiry endpoint rather than an authorization endpoint. The client queries the gateway using the original idempotency key. Only if the gateway authoritatively confirms that no charge was ever recorded does the app safely permit the user to initiate a new checkout.

## Interview answer — deep senior

From a distributed state coordination and UX resilience perspective, managing UI timeouts in payment workflows addresses a dangerous disconnect between visual perception and network reality.
Network calls on mobile devices frequently endure high latency due to cellular handshakes, DNS resolution, and multi-datacenter bank routing. If an app imposes an arbitrary fifteen-second UI coroutine timeout, cancelling the coroutine scope only aborts the local client socket; the HTTP packet may have already reached the payment gateway and initiated the authorization hold. If the UI then returns to the cart screen and re-enables the checkout button, the user instinctively taps it again, creating a race condition that results in a duplicate financial charge.
The architectural remedy enforces a strict unidirectional state machine backed by persistent storage. When the user taps Pay, the transaction moves to PROCESSING in the local database, locking the order ID. The UI binds directly to this state.
If the UI timer expires, the presentation layer transitions to an In-Doubt reconciliation state while maintaining the checkout button in an immutable disabled state.
Any retry mechanism is strictly bound to an inquiry contract. Instead of invoking the POST charge endpoint, the retry button triggers a GET status check passing the original correlation ID and idempotency key. If the gateway confirms that authorization succeeded, the app navigates directly to the receipt screen. If the transaction is confirmed absent, the app closes the stranded order and allows a clean retry. This guarantees that user frustration never translates into duplicate debits.

## How to answer in the interview

- **Why:** timeout describes missing response, not failed authorization.
- **How:** persist the attempt, lock that intent, and query status before another charge.
- **Trade-off:** the user may wait while a genuine unknown is resolved.
- **Failure case:** new ID on retry causes duplicate charge.
- **Production solution:** stable-key server dedupe, recovery UI, and escalation for long unknowns.

## Deep-dive talking points

Prompt for lost response, same-key retry, parameter immutability, process death and long-unknown escalation.

## Follow-up questions

- **Interviewer:** "Why should client UI timeouts always be longer than backend payment gateway timeouts?"
  **Answer:** "To prevent premature client failure dialogs while the backend is still actively and legitimately capturing funds."

- **Interviewer:** "How does `Mutex.tryLock()` prevent duplicate payment executions in Kotlin Coroutines?"
  **Answer:** "It atomically attempts to acquire the lock without suspending; if already held by an in-flight payment, it returns false and exits immediately."

## Self-check rubric

Can I explain timeout ambiguity, durable identity, status lookup and safe UI behavior?

## References and reviewed-on date

- [Stripe idempotent requests](https://docs.stripe.com/api/idempotent_requests) — one provider’s retry semantics.
- [Android offline-first data layer](https://developer.android.com/topic/architecture/data-layer/offline-first) — persistent state recovery.

Technically reviewed against primary documentation on 2026-10-13.
