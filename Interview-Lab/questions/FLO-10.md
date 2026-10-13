---
id: "FLO-10"
question: "What is the difference between state and transient events?"
topic: "Flow, StateFlow, SharedFlow & Channels"
code: "FLO"
group: "A"
phase: 1
priority: "P1"
order: 123
editorial_status: "reviewed"
---

# FLO-10

## Original interview question

What is the difference between state and transient events?

## What the interviewer evaluates

Separate durable/current state from one-time UI effects and define delivery semantics.

## Explanation in Arabic

الفرق بين الحالة (State) والأحداث العابرة (Transient Events) هو من أهم النقاط المعمارية لتجنب تكرار الأحداث (Duplicate Events Bug) عند تدوير الشاشة:

1. ما هي الحالة (State)؟
   - تمثل **الوضع الحالي الدائم للواجهة (What the UI looks like right now)**.
   - خاصية: **Persistent across Re-renders / Rotations**.
   - مثال: قائمة المنتجات، نص البحث، هل الزر معطل أم مفعل، حالة التحميل `isLoading`.
   - التمثيل النموذجي: `StateFlow<UiState>`.

2. ما هي الأحداث العابرة (Transient Events)؟
   - تمثل **أفعال تحدث لمرة واحدة فقط (One-off Actions / Side Effects)**.
   - خاصية: **Must be consumed exactly once!** ولا يجب إعادة تنفيذها إذا تم تدوير الشاشة.
   - مثال: الانتقال لشاشة ثانية (Navigate to Details)، إظهار Snackbar أو Toast برسالة خطأ، أو إغلاق لوحة المفاتيح.

3. المشكلة الشائعة (The Bug):
   - لو تم تخزين حدث الانتقال `Navigate` داخل `StateFlow`: عند تدوير الشاشة، الشاشة الجديدة ستقرأ القيمة المخزنة في `StateFlow.value` وتعيد الانتقال مرة ثانية بالخطأ!
   - الحل: استخدام `Channel` أو `SharedFlow` (مع `replay = 0`)، أو نمط استهلاك الحدث في State وإرسال Intent للـ ViewModel بـ `onEventConsumed()`.

## Practical walkthrough

أفضل نمط معماري للتعامل مع الأحداث العابرة في Jetpack Compose و MVI:
```kotlin
// 1. تعريف الـ Event كـ Sealed Interface:
sealed interface LoginSideEffect {
    data object NavigateToHome : LoginSideEffect
    data class ShowToast(val message: String) : LoginSideEffect
}

class LoginViewModel : ViewModel() {
    // State عادي للواجهة:
    val uiState: StateFlow<LoginUiState> = ...
    
    // Channel للأحداث العابرة (One-off Events):
    private val _effectChannel = Channel<LoginSideEffect>(Channel.BUFFERED)
    val effects: Flow<LoginSideEffect> = _effectChannel.receiveAsFlow()
    
    fun onLoginSuccess() {
        viewModelScope.launch {
            _effectChannel.send(LoginSideEffect.NavigateToHome)
        }
    }
}
```
في الـ UI: نستمع لـ `effects` عبر `LaunchedEffect`؛ يتم استهلاك الحدث مرة واحدة، وتدوير الشاشة لن يكرر الانتقال إطلاقاً.

## Why it matters and how it works

StateFlow replays latest state and conflates equal values; that is ideal for rendering, not counting occurrences. SharedFlow/Channel have delivery and replay caveats, especially when no collector is active. Model business results as durable state, then use UI effects only for best-effort presentation or explicit consumption protocols.

## Worked example

Conceptual Kotlin model; navigation effect is best-effort while payment status is persistent repository state.

```kotlin
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.flow.asStateFlow

data class ScreenState(val paymentStatus: String, val receiptId: String? = null)
class PaymentPresenter {
    private val _state = MutableStateFlow(ScreenState("pending"))
    val state = _state.asStateFlow()
    private val _hints = MutableSharedFlow<String>(extraBufferCapacity = 1)
    val hints = _hints.asSharedFlow()
    fun markSaved(receiptId: String) { _state.value = ScreenState("saved", receiptId) }
    suspend fun showHint() { _hints.emit("Saved") }
}
// Receipt identity is recoverable state; UI handles navigation by ID with
// back-stack/acknowledgment rules. A decorative hint may be transient.
```

## Trade-offs and decision criteria

An event stream avoids storing a one-shot command as replayed state, but may lose events without subscribers. A consumed flag in state can coordinate UI acknowledgement but adds protocol complexity. Persist outcome first when loss is unacceptable.

## Failure modes

A `StateFlow<Boolean>` navigation flag stays true after rotation and navigates again. A replay-zero SharedFlow emitted while the UI is stopped can be missed. Treat neither as exactly-once durable delivery.

## Production perspective

A payment completion is recorded in Room/server status. UI observes Success and navigates only through a documented consumption or destination state; a snackbar may be best-effort. Tests rotate before/after completion and kill the process between persistence and display.

## Interview answer — short

State represents persistent screen conditions that survive rotation and should always be observable via StateFlow; transient events are one-off side effects (like navigation or snackbars) that must be consumed exactly once and never replayed on screen rotation, typically modeled using Channel or SharedFlow.

## Interview answer — structured

Distinguishing between persistent state and transient events is crucial for preventing duplicate navigation or repeated snackbars in Android.

**State** represents the durable condition of the UI at any given moment: the list of items, form input text, or loading indicators. State must be retained across configuration changes so that rotating the device immediately restores the exact same visual representation. We model state using `StateFlow`.

**Transient Events** (also called Side Effects) represent one-off occurrences that must happen exactly once: navigating to a details screen, showing a temporary error Toast, or requesting biometric authentication. If you store an event inside a StateFlow, the new Activity created after a rotation will observe that same StateFlow, re-reading the event and navigating a second time.

We model transient events either through a separate one-shot stream like `Channel.receiveAsFlow()` or by embedding an event in UI state paired with an explicit confirmation action (`onEventHandled()`).

## Interview answer — deep senior

Historically, developers addressed this issue using `SingleLiveEvent` or `Event<T>` wrappers containing an `isHandled` boolean flag. While functional, those patterns are considered workarounds that break reactive purity.

In modern Android architecture, Google's Architecture Guide recommends two clean approaches: 1. **Channel as Event Stream:** A ViewModel exposes `val sideEffects = effectChannel.receiveAsFlow()`. Channels guarantee single-receiver delivery (FIFO queue); once an event is received and handled by `LaunchedEffect` in Compose, it is dequeued and cannot be replayed on rotation. 2. **State-Driven Events:** Model the event directly inside the UI state with a unique ID: `data class UiState(val userMessage: UserMessage? = null)`. When the UI displays the message, it immediately dispatches an intent `viewModel.onMessageShown(message.id)`, and the ViewModel clears `userMessage = null`. This keeps everything in a single unidirectional state pipeline.

## How to answer in the interview

- **Why:** persistent state and one-time commands have different replay needs.
- **How:** classify Success versus navigation.
- **Trade-off:** replay can duplicate; no replay can lose.
- **Failure case:** repeated destination after rotation.
- **Production solution:** acknowledgment or recoverable destination state where required.

## Deep-dive talking points

Define replay, acknowledgement and process-death requirements before selecting a primitive.

## Follow-up questions

- **Interviewer:** "What is the danger of using `SharedFlow` with `replay = 0` for one-off events?"
  **Answer:** "If an event is emitted to a `SharedFlow` while the UI is between lifecycles (e.g., during rotation or before `LaunchedEffect` starts collecting), the event is dropped permanently and lost because there were zero active collectors."

- **Interviewer:** "Why does `Channel(Channel.BUFFERED)` solve that dropped event issue?"
  **Answer:** "A buffered Channel retains sent items in its internal queue until a collector connects. If an event is sent during rotation, the Channel holds it and delivers it as soon as the recreated screen begins collecting."

- **Interviewer:** "Can you use Jetpack Compose's `LaunchedEffect` to observe a Channel event flow?"
  **Answer:** "Yes. `LaunchedEffect(Unit) { viewModel.effects.collect { effect -> handleEffect(effect) } }` is the standard pattern for observing side-effect streams in Compose."

## Self-check rubric

Can I identify current facts versus occurrences, state acceptable loss, and design a durable business outcome?

## References and reviewed-on date

- [Kotlin StateFlow API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-state-flow/) — latest-state replay.
- [Kotlin SharedFlow API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-shared-flow/) — event replay/buffer behavior.

Technically reviewed against primary documentation on 2026-10-13.
