---
id: "SYS-10"
question: "How do you model states and transitions with an explicit state machine?"
topic: "Android System Design & Architecture Decisions"
code: "SYS"
group: "B"
phase: 4
priority: "P1"
order: 339
editorial_status: "reviewed"
---

# SYS-10

## Original interview question

How do you model states and transitions with an explicit state machine?

## What the interviewer evaluates

Model business states and legal transitions explicitly, including persistence and idempotency.

## Explanation in Arabic

كيف تقوم بنمذجة حالات التطبيق وتدفقات الشاشات باستخدام آلة حالات صريحة (Explicit State Machine) لمنع الحالات غير الصالحة؟

1. مخاطر الـ State Modeling العشوائي (Boolean Hell):
   - كثير من المطورين يعرّفون الـ State بمجموعة من المتغيرات المنفصلة:
     `var isLoading: Boolean = false`, `var isError: Boolean = false`, `var data: List<Item>? = null`.
   - هذا يؤدي إلى **حالات متناقضة وغير منطقية مستحيلة هندسياً**! مثل: `isLoading = true` و `isError = true` في نفس الوقت، أو وجود بيانات مع خطأ فادح!

2. آلة الحالات الصريحة (Finite State Machine - FSM):
   - **Sealed Interfaces للحالات**: تمثيل كل حالة ممكنة بكلاس صريح ومغلق:
     `sealed interface UiState { object Loading; data class Success(val items); data class Error(val msg) }`.
   - **Sealed Interfaces للأحداث (User Actions & System Events)**: تمثيل كل حدث يغير الحالة:
     `sealed interface UiEvent { object Retry; data class SelectItem(val id); object Refresh }`.
   - **دالة التحويل النقية (State Reducer)**: دالة تأخذ الحالة الحالية والحدث وتعيد الحالة الجديدة فقط: `reduce(currentState, event): UiState`.

3. فصل الآثار الجانبية (Side-Effects Isolation):
   - العمليات غير النقية (Navigation, Showing Snackbars, Triggering Haptics) لا توضع داخل الـ State، بل تُعامل كـ `SharedFlow` أو `Channel` للأحداث الفردية (One-Off Side Effects) لمنع إعادة تنفيذها عند تدوير الشاشة.

## Practical walkthrough

تنفيذ State Machine صريحة ونقية مع MVI لتدفق دفع معقد ومنع الحالات المتضاربة:
```kotlin
// 1. نمذجة الحالات الممكنة حصرياً (Impossible States are Unrepresentable):
sealed interface CheckoutState {
    object Idle : CheckoutState
    object ProcessingPayment : CheckoutState
    data class AwaitingOtpVerification(val transactionId: String) : CheckoutState
    data class Completed(val receiptNumber: String) : CheckoutState
    data class Failed(val reason: String, val canRetry: Boolean) : CheckoutState
}

// 2. نمذجة الأحداث الصريحة:
sealed interface CheckoutEvent {
    data class SubmitPayment(val cardToken: String) : CheckoutEvent
    data class VerifyOtp(val code: String) : CheckoutEvent
    object Retry : CheckoutEvent
}

// 3. محرك الـ State Machine داخل ViewModel:
class CheckoutStateMachineViewModel @Inject constructor(
    private val paymentRepository: PaymentRepository
) : ViewModel() {
    private val _state = MutableStateFlow<CheckoutState>(CheckoutState.Idle)
    val state: StateFlow<CheckoutState> = _state.asStateFlow()

    fun onEvent(event: CheckoutEvent) {
        val currentState = _state.value
        viewModelScope.launch {
            when (event) {
                is CheckoutEvent.SubmitPayment -> {
                    if (currentState is CheckoutState.Idle || currentState is CheckoutState.Failed) {
                        _state.value = CheckoutState.ProcessingPayment
                        val result = paymentRepository.process(event.cardToken)
                        _state.value = when (result) {
                            is PaymentResult.RequiresOtp -> CheckoutState.AwaitingOtpVerification(result.txId)
                            is PaymentResult.Success -> CheckoutState.Completed(result.receipt)
                            is PaymentResult.Error -> CheckoutState.Failed(result.message, canRetry = true)
                        }
                    }
                }
                is CheckoutEvent.VerifyOtp -> {
                    if (currentState is CheckoutState.AwaitingOtpVerification) {
                        _state.value = CheckoutState.ProcessingPayment
                        // تنفيذ التحقق وتحديث الحالة
                    }
                }
                is CheckoutEvent.Retry -> {
                    if (currentState is CheckoutState.Failed && currentState.canRetry) {
                        _state.value = CheckoutState.Idle
                    }
                }
            }
        }
    }
}
```

## Why it matters and how it works

A reducer/transition function centralizes rules and can be pure for testability. Persistent state version or compare-and-set prevents concurrent workers overwriting newer results. External effects are issued through durable commands with stable IDs; completion events must be reconciled against authoritative source.

## Worked example

Kotlin conceptual pure transition function for a local upload; server business states need stronger authority.

```kotlin
sealed interface UploadState {
    data object Pending : UploadState
    data class Sending(val attempt: Int) : UploadState
    data class Complete(val receipt: String) : UploadState
}
sealed interface UploadEvent { data object Start : UploadEvent
    data class Acknowledged(val receipt: String) : UploadEvent }
fun reduce(state: UploadState, event: UploadEvent): UploadState = when {
    state is UploadState.Pending && event is UploadEvent.Start -> UploadState.Sending(1)
    state is UploadState.Sending && event is UploadEvent.Acknowledged -> UploadState.Complete(event.receipt)
    else -> state // production may reject/log illegal transitions explicitly
}
```

## Trade-offs and decision criteria

Explicit states add code but prevent impossible combinations like loading=true and settled=true. A permissive reducer that silently ignores illegal transitions can hide bugs; choose rejection/telemetry where appropriate. Distinguish UI transient state from durable business state.

## Failure modes

Two workers can race to mark Pending and Complete if updates lack version checks. A late network failure can overwrite a newer success. Treating timeout as final failure can trigger duplicate payment. Migration must preserve older state encodings.

## Production perspective

A payment repository stores operation state/version, applies server receipts transactionally and rejects stale updates. UI derives a screen from state; workers replay pending IDs after crash. Property tests enumerate legal/illegal transitions and race interleavings.

## Interview answer — short

Model states and transitions using an explicit finite state machine with Kotlin sealed interfaces to make invalid states unrepresentable. Enforce transitions through pure reducer functions driven by typed events, and isolate transient one-off side effects like navigation and snackbars from persistent view state.

## Interview answer — structured

Modeling complex UI and domain journeys using explicit State Machines eliminates the 'boolean flag explosion' where disparate variables create invalid state permutations:

1. **Making Invalid States Unrepresentable**:
   - Replace scattered variables (`var isLoading`, `var isError`, `var data`) with a single immutable sealed hierarchy (`Loading`, `Empty`, `Content`, `Error`). A screen cannot be simultaneously in `Loading` and `Error` because the type system strictly forbids it.

2. **Typed Events as Transition Triggers**:
   - Define a sealed interface representing all valid inputs (`UiEvent`). The UI emits intent events into the ViewModel without directly mutating data.

3. **Deterministic State Transitions (Reducers)**:
   - Transition logic follows a pure functional pattern: `f(State, Event) -> State`. Disallowed transitions are ignored or logged as violations, protecting flows like payments from duplicate executions during transitions.

4. **Isolating Side Effects**:
   - Decouple continuous UI state (rendered by Compose) from discrete one-off side effects (navigation commands, analytics triggers, toast messages). Channel side effects through a buffered `Channel<UiEffect>` consumed once via `LaunchedEffect`.

## Interview answer — deep senior

From an architectural rigor standpoint, finite state machines provide unparalleled testability and auditability:

1. **Exhaustive Unit Test Coverage**: Because state transitions are modeled as deterministic functions taking `(State, Event)`, unit testing requires zero mocking of Android framework components. You can assert that submitting `SubmitPayment` while in `ProcessingPayment` state is a no-op, preventing double-submission bugs with simple pure unit tests.

2. **State Restoration & Process Death**: Explicit state machines serialize seamlessly into Android `SavedStateHandle`. If the state machine is composed of parcelable primitives or identifiers, restoring the exact step of a multi-stage KYC or checkout flow post-process death requires deserializing a single state token.

3. **Hierarchical State Machines (Statecharts)**: For massive multi-step workflows (e.g., identity verification with camera capture, document review, and address confirmation), nest smaller child state machines within a parent coordinator state machine, ensuring sub-flow encapsulation.

## How to answer in the interview

- **Why:** explicit states make invariants reviewable.
- **How:** define events, preconditions, versions, and atomic transition persistence.
- **Trade-off:** more types and transitions require maintenance.
- **Failure case:** delayed callback overwrites a terminal state.
- **Production solution:** pure transition tests plus transactional compare-and-set on durable state.

## Deep-dive talking points

Draw state graph with duplicate/out-of-order events and version guard.

## Follow-up questions

- **Interviewer:** "Why should one-off UI events not be stored directly in StateFlow state?"
  **Answer:** "StateFlow retains its latest value; if an event like ShowSnackbar is stored in state, re-subscribing on screen rotation re-emits and displays the snackbar again."

- **Interviewer:** "What is the difference between MVI and traditional MVVM?"
  **Answer:** "MVI enforces a single immutable StateFlow and unidirectional event-driven reducers, whereas traditional MVVM often exposes multiple independent LiveData/StateFlow streams."

## Self-check rubric

Can I enumerate states, reject illegal transitions and protect against stale concurrent updates?

## References and reviewed-on date

- [Android architecture guide](https://developer.android.com/topic/architecture) — UDF and SSOT.
- [Android offline-first guidance](https://developer.android.com/topic/architecture/data-layer/offline-first) — durable operation states.

Technically reviewed against primary documentation on 2026-10-13.
