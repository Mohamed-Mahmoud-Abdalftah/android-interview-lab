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

Prevent duplicate payments by implementing multi-layered safeguards: immediately disable buttons and display loading spinners on the UI, protect ViewModel dispatch using a Kotlin Mutex or single-flight state guards, calibrate UI timeouts to exceed backend gateway SLAs, and anchor requests with persistent Idempotency Keys.

## Interview answer — structured

Preventing duplicate payment requests requires an end-to-end defense-in-depth architecture across UI, presentation, and data layers.

First, **Presentation & UI Layer Defenses**. Next, an Instant Click Debouncing & Button Disabling is the moment a user taps 'Pay', the button transitions to `enabled = false` and displays an explicit indeterminate progress spinner. Event handlers use `throttleFirst` to drop rapid taps.
Additionally, with ViewModel State Guards via Mutex, protect execution blocks using Kotlin `Mutex.tryLock()`. If a payment operation is currently active, subsequent invocations return immediately without launching duplicate coroutines. **Timeout SLA Alignment**.
A frequent architectural flaw is setting a 15-second client UI timeout when the payment gateway has a 30-second acquiring SLA. The UI prematurely times out and shows a retry button while the backend transaction is still processing. Client timeouts must exceed gateway read timeouts, and timeouts must transition to an 'In-Doubt Checking' screen rather than a generic failure screen. **Persistent Idempotency Layer**.
Finally, if the user manages to force-retry (e.g. By killing and restarting the app), the order entity retains the original `idempotency_key`. The subsequent network call presents the identical key to the payment gateway, which returns the original result rather than debiting the customer again.


## Interview answer — deep senior

From an Android lifecycle and process death perspective, state handling requires lifecycle-proof architecture.

First, with Configuration Changes & Process Recreation, if a user rotates the screen during payment processing, a naive Activity might re-invoke `onCreate` and trigger duplicate payment logic. Managing payment operations inside an injected Application-scoped or WorkManager-backed service unbinds transaction execution from transient UI component lifecycles. Next, with The 'In-Doubt' Loading Screen, when an inevitable client-side timeout occurs after 35 seconds, never display a simple 'Transaction Failed — Try Again' dialog. Display: 'Verifying payment with your bank... Please do not re-submit.' Query the transaction status endpoint before allowing the user to initiate a new checkout session.
Finally, with Backend Race Condition Mitigation, what if two duplicate requests arrive at the backend within 5 milliseconds due to multi-threaded glitches? Distributed Redis locks on `idempotency_key` ensure only one worker thread enters the payment processing block, returning an HTTP 409 Conflict to the concurrent duplicate.


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
