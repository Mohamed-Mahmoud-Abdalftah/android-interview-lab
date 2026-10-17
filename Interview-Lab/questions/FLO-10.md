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

## Concept and technical explanation

In reactive Android architecture, distinguishing between persistent State and transient Events is fundamental to predictable UI rendering and avoiding duplicate side effects.
State represents an enduring, observable snapshot of the user interface at any given instant—such as a list of loaded products, a loading spinner visibility flag, or an error screen layout. State is persistent, non-destructive, supports immediate replay to newly attached observers, and conflates intermediate updates so that collectors always receive the freshest representation.
Transient Events represent momentary, one-off side effects that must be consumed exactly once—such as triggering screen navigation, showing a SnackBar notification, requesting biometric authentication, or playing an audio alert. Events must not persist in the UI state buffer; if an event is held in a regular state stream, configuration changes like screen rotations cause newly recreated UI observers to collect the cached event a second time, triggering repeated navigation loops or duplicate toast popups.

## Practical walkthrough (English)

Contrasting UI state with one-off transient events in an Android ViewModel:
```kotlin
// 1. UI State: Persistent snapshot of screen data
data class CheckoutUiState(
    val isProcessing: Boolean = false,
    val cartTotal: BigDecimal = BigDecimal.ZERO
)

// 2. Transient Events: One-off navigation or snackbar intents
sealed interface CheckoutUiEvent {
    data class NavigateToReceipt(val orderId: String) : CheckoutUiEvent
    data class ShowErrorSnackBar(val message: String) : CheckoutUiEvent
}

class CheckoutViewModel : ViewModel() {
    // State: Exposed via StateFlow with initial loading state
    private val _uiState = MutableStateFlow(CheckoutUiState())
    val uiState: StateFlow<CheckoutUiState> = _uiState.asStateFlow()

    // Events: Exposed via Channel or SharedFlow(replay = 0)
    private val _eventChannel = Channel<CheckoutUiEvent>(Channel.BUFFERED)
    val events = _eventChannel.receiveAsFlow()

    fun completeCheckout() {
        viewModelScope.launch {
            _uiState.update { it.copy(isProcessing = true) }
            val orderId = api.placeOrder()
            _uiState.update { it.copy(isProcessing = false) }
            // Transient event sent once:
            _eventChannel.send(CheckoutUiEvent.NavigateToReceipt(orderId))
        }
    }
}
```

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

State represents a continuous, persistent snapshot of the screen that survives rotation and supports replay. Transient events represent one-shot actions like navigation or toasts that must execute exactly once. Storing transient events in StateFlow causes duplicate execution upon rotation, requiring either Channel-backed event streams or consumed state flags.

## Interview answer — structured

The architectural dichotomy between state and transient events dictates how data streams are modeled and consumed.

State represents what the screen currently displays. It is persistent, stateful, and must replay immediately when an Activity recreates after rotation. We model UI state using StateFlow, conflating updates so the UI always reflects the latest snapshot.

In production, transient events represent fire-and-forget side effects like triggering navigation, displaying a toast, or vibrating the haptic engine. These actions must be delivered and processed exactly once.

Modeling one-off events inside a StateFlow is a frequent source of severe bugs. When the device rotates, newly registered collectors re-read the cached state, causing redundant navigation commands or re-showing dismissed SnackBars. We solve this by modeling events as Channel-backed streams or resetting state properties via explicit event consumption patterns.


## Interview answer — deep senior

At the system and lifecycle boundary level, handling transient events reliably in Android coroutines has undergone substantial architectural evolution. Naive historical patterns, such as SingleLiveEvent or wrapping events in an Event<T> wrapper with a getContentIfNotHandled() flag, suffered from race conditions and anti-pattern state mutability inside the presentation layer.
Modern reactive patterns utilize two primary production approaches. The first approach is Channel-based event streaming: creating a private Channel<Event>(Channel.BUFFERED) and exposing it downstream via channel.receiveAsFlow(). Because a Channel operates on queue semantics with individual message delivery, each emitted event is consumed by exactly one collector and immediately dequeued. However, if an event is emitted while the UI is between onStop and onStart, the Channel buffers the event in memory until the UI lifecycle resumes and collects it.
The second, increasingly recommended pattern from Google Android Architecture guidelines is Pure State Modeling: treating UI messages as part of the immutable UiState data class. In this pattern, the state includes a nullable message object with a unique identifier. Once the Composable or Fragment displays the SnackBar, it invokes an explicit callback on the ViewModel (such as onMessageDismissed(messageId)), which updates the StateFlow to nullify that specific event property.
Staff engineers select pure state modeling for user-facing visual notifications to guarantee state idempotency, while reserving Channels for critical single-shot operational commands like navigation transitions.

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
