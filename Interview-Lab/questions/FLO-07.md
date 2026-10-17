---
id: "FLO-07"
question: "How do you expose read-only state via asStateFlow()?"
topic: "Flow, StateFlow, SharedFlow & Channels"
code: "FLO"
group: "A"
phase: 1
priority: "P1"
order: 120
editorial_status: "reviewed"
---

# FLO-07

## Original interview question

How do you expose read-only state via asStateFlow()?

## What the interviewer evaluates

Explain read-only exposure without claiming it makes underlying objects immutable.

## Concept and technical explanation

Exposing read-only state via asStateFlow() is the foundational encapsulation and unidirectional data flow (UDF) pattern in modern Android architecture. In the presentation layer, a ViewModel manages a private, mutable backing property (MutableStateFlow) to mutate internal screen state in response to user actions or domain responses. However, exposing MutableStateFlow publicly violates object-oriented encapsulation and architectural boundaries by allowing external classes—such as Activities, Fragments, Composables, or peer components—to directly mutate the state from the outside. The asStateFlow() extension function solves this by wrapping the mutable instance inside a ReadonlyStateFlow proxy. This read-only abstraction enforces at compile time that only the owning ViewModel holds write privileges, while public consumers can only observe emissions or read the synchronous value property.

## Practical walkthrough (English)

Encapsulating state within an Android ViewModel:
```kotlin
class CheckoutViewModel(private val repository: CheckoutRepository) : ViewModel() {
    // 1. Private mutable state: Only this ViewModel can mutate the backing state
    private val _uiState = MutableStateFlow<CheckoutUiState>(CheckoutUiState.Initial)

    // 2. Public read-only projection: Downstream UI layers can only observe
    val uiState: StateFlow<CheckoutUiState> = _uiState.asStateFlow()

    fun completePurchase() {
        viewModelScope.launch {
            _uiState.value = CheckoutUiState.Processing
            val result = repository.submitOrder()
            _uiState.value = result.fold(
                onSuccess = { CheckoutUiState.Success(it.orderId) },
                onFailure = { CheckoutUiState.Error(it.message ?: "Failed") }
            )
        }
    }
}

// In the UI Layer (Activity / Composable):
// viewModel.uiState.value = CheckoutUiState.Success("fake") // COMPILE ERROR! Read-only.
```

## Explanation in Arabic

نمط الكبسولة (Encapsulation Pattern) باستخدام `asStateFlow()` هو القاعدة الذهبية في تصميم الـ ViewModels في أندرويد:

1. المشكلة التي يحلها:
   - في الـ ViewModel، نحتاج أن نكون قادرين على تعديل الحالة (`_uiState.value = ...` أو `_uiState.update { }`).
   - ولكن **الـ View (Activity/Fragment/Composable) يجب ألا تكون قادرة على تعديل الحالة إطلاقاً!**
   - لو تم كشف `MutableStateFlow` مباشرة للـ UI، يمكن لأي زر أو كود في الـ UI أن يكتب `viewModel.uiState.value = BadState`، مما يكسر مبدأ **UDF (Unidirectional Data Flow)** ويجعل تتبع الأخطاء كابوساً.

2. ما الذي تفعله دالة `asStateFlow()`؟
   - تقوم بإنشاء **Read-Only View Wrapper** (`ReadOnlyStateFlow`) حول الـ `MutableStateFlow`.
   - تمنع أي شخص من عمل Cast خبيث أو غير مقصود: حتى لو حاول المطور كتابة `(uiState as MutableStateFlow).value = ...`، الـ Wrapper الداخلي يمنع ذلك ويرمي `ClassCastException` في وقت التشغيل!

3. النمط القياسي للتنفيذ:
   - متغير خاص للتعديل: `private val _uiState = MutableStateFlow(...)`
   - متغير عام للقراءة فقط: `val uiState: StateFlow<T> = _uiState.asStateFlow()`

## Practical walkthrough

الكود القياسي في الـ ViewModel:
```kotlin
class CheckoutViewModel : ViewModel() {
    // 1. Mutable خاص بالـ ViewModel فقط:
    private val _uiState = MutableStateFlow(CheckoutUiState.Initial)
    
    // 2. Read-only مكشوف للـ UI:
    val uiState: StateFlow<CheckoutUiState> = _uiState.asStateFlow()
    
    fun onPromoCodeEntered(code: String) {
        // التعديل محصور حصرياً داخل دوال الـ ViewModel:
        _uiState.update { it.copy(promoCode = code) }
    }
}
```
في الـ Composable: الشاشة تقرأ فقط `val state by viewModel.uiState.collectAsStateWithLifecycle()`، وأي محاولة لتعديل الحالة تتم بإرسال حدث للـ ViewModel.

## Why it matters and how it works

`asStateFlow()` returns a read-only view of the same hot state source; it does not copy data. Use immutable state classes/lists and atomic `update` when concurrent writers may modify state. Keep mutation functions small and domain-specific.

## Worked example

JVM example uses `kotlinx-coroutines-core`; immutable data class state and an atomic transformation.

```kotlin
import kotlinx.coroutines.flow.*

data class CounterState(val value: Int)
class CounterViewModelState {
    private val mutable = MutableStateFlow(CounterState(0))
    val state: StateFlow<CounterState> = mutable.asStateFlow()
    fun increment() { mutable.update { it.copy(value = it.value + 1) } }
}
```

## Trade-offs and decision criteria

Read-only exposure prevents arbitrary callers from assigning state but is not authorization/security isolation. An interface property is also possible; `asStateFlow()` makes the intent explicit. Immutable snapshots and a single source of truth remain important.

## Failure modes

Exposing `MutableStateFlow` lets UI code write values that bypass validation. Returning a read-only StateFlow containing a mutable list still allows in-place list mutation and equality bugs. A non-atomic `state.value = state.value.copy(...)` can race with another writer.

## Production perspective

A checkout ViewModel exposes a read-only price state and methods for quantity changes. Validation and total calculation stay inside the owner; the UI cannot publish arbitrary totals. Business authority still belongs to the backend.

## Interview answer — short

asStateFlow() wraps a private MutableStateFlow into a read-only StateFlow, preventing external layers from mutating ViewModel state. This enforces unidirectional data flow (UDF) and encapsulation, ensuring that the ViewModel remains the single source of truth and the only component with write privileges.

## Interview answer — structured

Exposing state via asStateFlow() enforces encapsulation and unidirectional data flow.

The ViewModel must maintain exclusive ownership over its state transitions. By declaring MutableStateFlow as a private backing property and exposing a public read-only StateFlow using asStateFlow(), we establish a compile-time boundary preventing external components from modifying state.

In production, allowing UI layers or testing utilities to mutate state directly creates chaotic multi-directional mutations, introduces race conditions, and complicates state debugging. When state mutates strictly through ViewModel member functions, business logic remains centralized, testable, and auditable.

AsStateFlow() returns a ReadonlyStateFlow instance that intercepts casting attempts. Merely declaring val uiState: StateFlow = _uiState without asStateFlow() allows malicious or erroneous code to downcast the reference back to MutableStateFlow at runtime, whereas asStateFlow() guarantees immutable encapsulation.


## Interview answer — deep senior

At the compiler and runtime API boundary level, the difference between a direct upcast and asStateFlow() represents a vital defense against reflection and unsafe type casting. In naive implementations, developers write: val uiState: StateFlow<T> get() = _uiState. Because MutableStateFlow implements the StateFlow interface directly, the runtime instance remains an instance of MutableStateFlowImpl. A consumer can write (viewModel.uiState as MutableStateFlow).value = newState, successfully bypassing encapsulation and mutating state externally.
The asStateFlow() extension function specifically mitigates this by wrapping the mutable instance in an internal ReadonlyStateFlow wrapper. ReadonlyStateFlow implements StateFlow and CancellableFlow, delegating collect and value calls to the wrapped instance while concealing the MutableStateFlow interface entirely. An unsafe downcast to MutableStateFlow throws a runtime ClassCastException, closing the vulnerability.
Furthermore, this pattern guarantees the Unidirectional Data Flow (UDF) lifecycle contract: State flows down from the ViewModel to the UI, and Events flow up from the UI to the ViewModel. If the UI could mutate the state directly, state consistency models would shatter, making automated UI testing and bug reproduction nearly impossible.
This discipline ensures that testing harnesses and UI previews interact strictly with predictable read contracts, while mutations remain isolated to explicit, testable ViewModel intent handlers.
Staff engineers enforce this via Detekt and Android Lint rules: flagging any public MutableStateFlow or MutableSharedFlow property as an architectural violation across all repository, use case, and presentation layers.

## How to answer in the interview

- **Why:** only the owner should enforce state transitions.
- **How:** private mutable flow, public read-only view, named events.
- **Trade-off:** API boundary does not freeze mutable nested objects.
- **Failure case:** exposing `_state` or mutating a list in place.
- **Production solution:** immutable models and atomic update tests.

## Deep-dive talking points

Contrast API immutability, value immutability and server authority.

## Follow-up questions

- **Interviewer:** "Why not use a custom getter `val uiState get() = _uiState`?"
  **Answer:** "A custom getter returns the raw `_uiState` reference on every property access, which permits unsafe runtime casting to `MutableStateFlow`. `asStateFlow()` creates the protective wrapper once."

- **Interviewer:** "What is the equivalent function for SharedFlow?"
  **Answer:** "For `MutableSharedFlow`, the equivalent function is `asSharedFlow()`, which wraps the instance in a read-only `ReadOnlySharedFlow`."

- **Interviewer:** "How does Jetpack Compose interact with `asStateFlow()`?"
  **Answer:** "Compose consumes it via `collectAsStateWithLifecycle()`, which observes the read-only StateFlow and converts it into a Compose `State<T>`, triggering recomposition only when new distinct states are emitted."

## Self-check rubric

Can I encapsulate mutation, explain shared underlying stream, publish immutable values and handle concurrent updates?

## References and reviewed-on date

- [Kotlin StateFlow API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-state-flow/) — `asStateFlow` and `update`.

Technically reviewed against primary documentation on 2026-10-13.
