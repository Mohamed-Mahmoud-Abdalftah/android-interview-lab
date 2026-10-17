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

## Concept and technical explanation

Preventing duplicate submission when a user rapidly double-taps an action requires a coordinated defense across UI presentation, ViewModel concurrency, and domain idempotency. At the UI presentation layer, the interactive component must be immediately disabled using state (enabled = !state.isSubmitting) or visually replaced with a progress indicator to prevent further click gestures. At the ViewModel layer, coroutine concurrency must be guarded using Mutex locks, atomic boolean flags, or Flow operators like mapLatest or dropWhile. At the domain and backend layers, every submission must carry a unique idempotency key (such as a UUID) to guarantee that duplicate network transmissions execute as a safe no-op.

## Practical walkthrough (English)

Defending against rapid double-tap submissions across UI, ViewModel, and Network:
```kotlin
// 1. UI Layer: Disable button immediately when isSubmitting is true
@Composable
fun SaveTaskButton(
    isSubmitting: Boolean,
    onSaveClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Button(
        onClick = onSaveClick,
        enabled = !isSubmitting, // UI-level instant disablement!
        modifier = modifier
    ) {
        if (isSubmitting) {
            CircularProgressIndicator(modifier = Modifier.size(20.dp), strokeWidth = 2.dp)
        } else {
            Text("Save Task")
        }
    }
}

// 2. ViewModel & Domain Layer: Concurrency guard and Idempotency Key
@HiltViewModel
class TaskViewModel @Inject constructor(
    private val saveTaskUseCase: SaveTaskUseCase
) : ViewModel() {
    private val _uiState = MutableStateFlow(TaskUiState())
    val uiState = _uiState.asStateFlow()

    private var activeJob: Job? = null
    private val submitMutex = Mutex()

    fun submitTask(taskData: TaskData) {
        // Guard 1: Ignore call if already in-flight!
        if (activeJob?.isActive == true) return

        activeJob = viewModelScope.launch {
            if (!submitMutex.tryLock()) return@launch // Guard 2: Mutex prevents concurrent entry!

            try {
                _uiState.update { it.copy(isSubmitting = true) }
                // Guard 3: Pass idempotent UUID so backend processes duplicate requests safely
                val idempotencyKey = UUID.randomUUID().toString()
                saveTaskUseCase(taskData, idempotencyKey)
                _uiState.update { it.copy(isSubmitting = false, isSuccess = true) }
            } catch (e: Exception) {
                _uiState.update { it.copy(isSubmitting = false, errorMessage = e.message) }
            } finally {
                submitMutex.unlock()
            }
        }
    }
}
```

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

We defend against double-taps through a layered strategy. In the UI, we disable the button immediately using enabled = !state.isSubmitting and show a loading spinner. In the ViewModel, we guard against concurrent execution using activeJob.isActive checks or Mutex.tryLock() to reject duplicate calls while a request is in flight. At the domain and network layers, we pass a client-generated idempotency key (UUID) so the backend processes duplicated packets safely without duplicating transactions.

## Interview answer — structured

Handling rapid duplicate user taps is an essential resilience pattern tested in senior Android engineering interviews.
A user pressing Save twice in rapid succession can trigger duplicate database entries, double financial payments, or corrupted state.
A robust architecture implements a multi-layered defense.
Layer one is UI presentation deterrence.
The button's enabled parameter must bind to the reactive UI state (enabled = !uiState.isSubmitting).
The moment the first click registers, the UI updates its state, immediately disabling the button and ignoring subsequent click gestures.
However, UI disablement alone is insufficient because touch dispatch queues can fire two tap events within the same frame before recomposition finishes.
Layer two is ViewModel concurrency gating.
Inside the ViewModel, we guard the submission method against concurrent execution.
We check if the existing coroutine Job is active (if (job?.isActive == true) return) or utilize Mutex.tryLock() to ensure that only a single submission coroutine can execute at any given time.
Layer three is domain and network idempotency.
Every mutation request generates a client-side idempotency key (such as a UUID).
The backend uses this token to deduplicate requests, guaranteeing that even if a retry mechanism sends duplicate network packets, the transaction is processed exactly once.

## Interview answer — deep senior

Under the hood, addressing double-tap race conditions exposes the asynchronous latency between hardware touch event dispatch and Compose frame recomposition.
When a user double-taps rapidly, the platform hardware digitizer generates two MotionEvents spaced mere milliseconds apart.
Because Compose dispatches touch events through the PointerInputModifierNode pipeline during hit testing, both clicks can be processed and queued on the Main thread before the first click's state mutation can trigger Choreographer VSYNC, execute recomposition, and update the Button's enabled constraint.
Relying solely on enabled = false leaves a microscopic timing window where both clicks invoke the onClick callback.
To neutralize this window, senior engineers implement thread-safe concurrency guards inside the architecture ViewModel.
Using Kotlin Coroutines Mutex with tryLock() guarantees atomic entrance.
If thread execution enters while a lock is held, tryLock() returns false immediately without suspending, safely dropping the redundant second event.
Alternatively, engineers utilize AtomicBoolean.compareAndSet(false, true) for lock-free state synchronization.
At the network layer, integrating RFC-7231 or IETF draft Idempotency-Key headers in HTTP requests ensures distributed transaction safety across cloud microservices.
If network timeouts cause OkHttp to retry or if the user forces a resubmission, the backend caches the idempotency token in Redis, returning the original response without executing duplicate database inserts or processing duplicate financial debits.

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
