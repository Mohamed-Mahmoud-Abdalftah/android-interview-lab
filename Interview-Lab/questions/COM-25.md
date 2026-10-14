---
id: "COM-25"
question: "A user taps Save twice while a request is in flight. How do you make UI and domain behavior safe?"
topic: "Jetpack Compose"
code: "COM"
group: "C"
phase: 3
priority: "P1"
order: 254
editorial_status: "reviewed"
---

# COM-25

## Original interview question

A user taps Save twice while a request is in flight. How do you make UI and domain behavior safe?

## What the interviewer evaluates

- Address UI feedback and domain/server idempotency separately.
- Handle concurrency races, retry and process death.
- Define persisted result and unknown outcome reconciliation.

## Explanation in Arabic

عندما يضغط المستخدم على زر الحفظ (Save) مرتين بسرعة والطلب جارٍ: كيف تجعل سلوك الواجهة (UI) وسلوك النطاق (Domain) آمناً ومحمياً؟

1. طبقة واجهة المستخدم (UI Layer Protection):
   - **تعطيل الزر فورياً (Disable Button)**: بمجرد الضغط الأول، تتحول حالة `isSaving` في الـ `UiState` إلى `true`، مما يجعل `Button(enabled = !uiState.isSaving)` معطلاً فورياً.
   - **Click Debouncing**: استخدام Modifier نقر مخصص يفحص وقت الضغط الأخير ويتجاهل أي نقرة تحدث خلال 500ms.

2. طبقة الـ ViewModel (State Holder Protection):
   - **فحص الحالة الحالية (State Guarding)**: قبل إطلاق العملية، التحقق من: `if (_uiState.value.isSaving) return`.
   - **استخدام Mutex أو Concurrency Operators**: إما الاحتفاظ بمرجع للـ `Job` والتحقق من `if (saveJob?.isActive == true) return`، أو استخدام `Mutex` لمنع الدخول المتزامن.

3. طبقة الـ Domain والـ Backend (Idempotency):
   - حتى لو نجحت نقرتان في المرور، يجب أن تكون العملية **Idempotent**.
   - استخدام **Idempotency Key (UUID)** يُولد مرة واحدة لكل معاملة ويُرسل في ترويسة الطلب (`Idempotency-Key: uuid`)؛ حتى لو استلم السيرفر طلبين، ينفذ الأول ويرد بنفس النتيجة للثاني دون تكرار الخصم أو الحفظ.

## Practical walkthrough

تأمين زر الحفظ في الـ UI والـ ViewModel والـ Network Layer:
```kotlin
// 1. في ViewModel: حماية الطلب من التكرار عبر State Guarding ومفتاح Idempotency:
class CheckoutViewModel(private val orderRepository: OrderRepository) : ViewModel() {
    private val _uiState = MutableStateFlow(CheckoutUiState())
    val uiState: StateFlow<CheckoutUiState> = _uiState.asStateFlow()

    private var activeSaveJob: Job? = null

    fun saveOrder() {
        // منع التنفيذ إذا كان هناك طلب جارٍ بالفعل:
        if (activeSaveJob?.isActive == true || _uiState.value.isSaving) return

        activeSaveJob = viewModelScope.launch {
            _uiState.update { it.copy(isSaving = true) }
            try {
                val idempotencyKey = UUID.randomUUID().toString()
                orderRepository.submitOrder(idempotencyKey, _uiState.value.orderData)
                _uiState.update { it.copy(isSaving = false, isSuccess = true) }
            } catch (e: Exception) {
                _uiState.update { it.copy(isSaving = false, errorMessage = e.message) }
            }
        }
    }
}

// 2. في Compose: تعطيل الزر بصرياً وإظهار مؤشر تقدم:
@Composable
fun SaveButton(uiState: CheckoutUiState, onSaveClick: () -> Unit) {
    Button(
        onClick = onSaveClick,
        enabled = !uiState.isSaving // معطل فورياً بمجرد أول نقرة!
    ) {
        if (uiState.isSaving) {
            CircularProgressIndicator(modifier = Modifier.size(16.dp), strokeWidth = 2.dp)
        } else {
            Text("Save Order")
        }
    }
}
```

## Why it matters and how it works

Compose rendering can disable a control from state, but event delivery and network retries are independent of rendering. A mutex or atomic state transition protects one in-process owner, while server idempotency protects across devices, process restarts and retries. Distinguishing a new user intent from retry of the same intent determines whether to reuse the key.

## Worked example

A checkout screen submits an order with `clientOperationId`. The button enters `Submitting`, and the ViewModel ignores another tap for that ID. The backend stores idempotency key plus request fingerprint and returns the same order on retry. If connection drops after server commit, the app queries order status and shows Pending rather than creating a second order.

### Compose/Kotlin walkthrough

```kotlin
// Inside SaveViewModel: _ui is MutableStateFlow<SaveUiState>; Draft has a
// persisted operationId; repository/server honor that ID idempotently.
private val saveMutex = Mutex()
fun save(draft: Draft) = viewModelScope.launch {
    if (!saveMutex.tryLock()) return@launch
    try {
        _ui.update { it.copy(saving = true) }
        try {
            val id = repository.save(draft, operationId = draft.operationId)
            _ui.update { it.copy(saving = false, savedId = id) }
        } catch (e: CancellationException) {
            throw e
        } catch (e: Exception) {
            _ui.update { it.copy(saving = false, error = "Save status unknown") }
        }
    } finally { saveMutex.unlock() }
}
// Imports: kotlinx.coroutines.sync.Mutex, kotlinx.coroutines.flow.update,
// kotlinx.coroutines.CancellationException. Reconcile uncertain server status.
```

## Trade-offs and decision criteria

Disabling the button is simple UX but insufficient correctness. A local mutex prevents one process race but not post-crash duplicates. Server idempotency requires storage and expiry policy; high-value writes justify it. A generic `debounce` can drop a legitimate second intent, so define operation identity explicitly.

## Failure modes

Two rapid callbacks pass a non-atomic `if (!saving)` check. Timeout is treated as failure and a new key creates a duplicate charge. The UI shows success before server confirmation. An operation key is reused for a changed payload, causing incorrect deduplication.

## Production perspective

Test rapid double tap, retry after timeout, app restart, duplicate server delivery and mismatched payload. Log operation IDs without secrets and expose an explicit pending/reconciliation state. Make saved-state and backend contracts agree.

## Interview answer — short

Defend against rapid double-taps using defense-in-depth: disable the button in UI when `isSaving` is true, guard execution in the ViewModel by checking `if (saveJob?.isActive == true) return`, and ensure domain/backend idempotency by sending a unique client-generated Idempotency Key with the request.

## Interview answer — structured

Protecting against double-tap race conditions requires a defense-in-depth strategy across UI, ViewModel, and Domain/Backend boundaries.

First, an UI Layer Defense is the UI reflects saving state immediately. We set `Button(enabled = !uiState.isSaving)` and show an inline progress spinner. When disabled, Android skips touch event dispatching to that node. Additionally, click handlers can be wrapped in a single-click debounce modifier that rejects clicks within 400ms. Next, with ViewModel Concurrency Guard, because UI recomposition occurs on the next frame (leaving a fraction of a millisecond where a second tap could fire), the ViewModel must guard execution synchronously.
Maintain a reference to the active coroutine job: `if (saveJob?.isActive == true) return`. Atomically update state: `if (!_isProcessing.compareAndSet(false, true)) return`.
Finally, with Domain & Backend Idempotency, network operations must be structurally idempotent. The client generates a unique `Idempotency-Key` (UUID) attached to the network payload. Even if network latency causes duplicate packets, the backend processes the transaction once and returns the cached confirmation for subsequent calls.


## Interview answer — deep senior

Under the hood, relying solely on `enabled = false` in Compose has a micro-window vulnerability. Touch input dispatch occurs on the main looper. If a user taps twice with exceptional speed within the same frame interval before the snapshot state invalidation triggers a recomposition of the button's layout node, the second click event will invoke `onClick`.

This makes the ViewModel synchronous guard mandatory. By checking `saveJob?.isActive == true` at the very top of the function body on the main thread, the second invocation is discarded synchronously before any coroutine is scheduled or network request initiated.

In payment flows (Fintech), we also enforce transactional database flags: setting a local database status to `PENDING_SUBMISSION` within a local Room transaction before dispatching network calls, guaranteeing crash recovery and duplicate transaction avoidance.


## How to answer in the interview

- **Why:** disabling the button does not prevent duplicate domain work.
- **How:** guard in process and reuse an idempotency key across retries.
- **Trade-off:** key lifetime and request fingerprint need server agreement.
- **Failure case:** timeout after commit causes duplicate order.
- **Production solution:** query status and persist pending operation where needed.

## Deep-dive talking points

Discuss atomic single-flight, idempotency keys, payload fingerprints, unknown outcomes, and recovery.

## Follow-up questions

- **Interviewer:** "Why is disabling the button in UI insufficient on its own?"
  **Answer:** "Touch dispatch and recomposition are asynchronous. Two rapid taps within the same VSYNC frame will execute the click callback twice before Compose completes recomposing the button into a disabled state."

- **Interviewer:** "How does `compareAndSet` work for atomic gating in ViewModel?"
  **Answer:** "`AtomicBoolean.compareAndSet(false, true)` checks and updates a flag in a single atomic CPU instruction, guaranteeing that only the first thread or event passes while subsequent calls fail immediately."

## Self-check rubric

Name UI, in-process and server guards; explain timeout reconciliation and tests.

## References and reviewed-on date

- [Compose state architecture](https://developer.android.com/develop/ui/compose/architecture) — state-driven UI.
- [WorkManager persistent work](https://developer.android.com/topic/libraries/architecture/workmanager) — durable retries where applicable.
- [Stripe idempotent requests](https://docs.stripe.com/api/idempotent_requests) — provider-specific idempotency example.

Technically reviewed against primary documentation on 2026-10-13.
