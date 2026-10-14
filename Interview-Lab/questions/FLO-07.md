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

Use asStateFlow() to expose a read-only StateFlow interface from a private MutableStateFlow backing property. This enforces Unidirectional Data Flow (UDF) by ensuring only the ViewModel can mutate state while UI components can only observe it, with a runtime wrapper that prevents unsafe downcasting.

## Interview answer — structured

Exposing state via `asStateFlow()` is the foundational encapsulation pattern in modern Android architecture for enforcing **Unidirectional Data Flow (UDF)**.

We declare a private mutable backing property:
`private val _uiState = MutableStateFlow(InitialState)`
And expose a public read-only property:
`val uiState: StateFlow<MyState> = _uiState.asStateFlow()`

This architectural separation guarantees that state mutations remain strictly confined to the ViewModel's business methods. The UI layer can observe emissions and read values, but it can never directly assign or mutate state.

Crucially, `asStateFlow()` does not perform a simple interface upcast; it wraps the mutable flow in a dedicated `ReadOnlyStateFlow` class. This provides defensive type-safety: if a consumer attempts to dangerously downcast `(uiState as MutableStateFlow).value = ...`, the JVM throws a `ClassCastException`, preventing state corruption.


## Interview answer — deep senior

Under the hood, why not simply write `val uiState: StateFlow<T> = _uiState` (a simple compiler upcast)?

A plain upcast only provides compile-time visibility restrictions. At runtime, the underlying JVM object remains an instance of `StateFlowImpl` (which implements `MutableStateFlow`). Any caller in Java, or any Kotlin developer using unsafe casting (`as MutableStateFlow`), could bypass your architectural boundary and mutate the internal state from the UI or test classes.

`asStateFlow()` wraps the instance in `ReadOnlyStateFlow`, an internal wrapper that only implements `StateFlow` and delegates read methods to the underlying instance without exposing mutation handles. In enterprise code reviews, we enforce this via lint rules: every public state exposed by a ViewModel must be a read-only `StateFlow` or `SharedFlow` derived via `asStateFlow()` or `stateIn()`.


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
