---
id: "FLO-27"
question: "A navigation event fires twice after rotation. How do you investigate event modeling and consumption?"
topic: "Flow, StateFlow, SharedFlow & Channels"
code: "FLO"
group: "C"
phase: 1
priority: "P1"
order: 140
editorial_status: "reviewed"
---

# FLO-27

## Original interview question

A navigation event fires twice after rotation. How do you investigate event modeling and consumption?

## What the interviewer evaluates

Investigate duplicate navigation through replay, collector duplication and consumption race.

## Concept and technical explanation

A navigation event firing repeatedly following device orientation changes represents the classic Android "Event Replay" anti-pattern, caused by mismodeling transient one-off side effects as persistent UI state.
When navigation destinations, snackbars, or toast messages are stored inside StateFlow or SharedFlow with positive replay cache (replay >= 1), the flow retains the navigation payload in memory. When device rotation triggers Activity destruction and recreation, the newly attached observer collects the flow and immediately receives the retained navigation event from the replay cache, re-triggering the navigation intent.
Investigating and resolving this failure mode involves evaluating event lifecycle ownership: transient side effects must not rely on sticky state caches or anti-patterns like EventWrapper / SingleLiveEvent. Senior Android engineering standards resolve this either by modeling navigation actions via single-consumer buffered Channels exposed as Flows, or by modeling events as explicit, state-driven UI models where the UI explicitly notifies the ViewModel upon consumption to acknowledge and clear the event.

## Practical walkthrough (English)

Investigating and fixing navigation event replay via state-driven consumption acknowledgement:
```kotlin
// 1. Model navigation as a nullable property within the UI State:
data class CheckoutUiState(
    val isLoading: Boolean = false,
    val navigationEvent: CheckoutNavigation? = null // Transient event
)

sealed interface CheckoutNavigation {
    data class NavigateToReceipt(val orderId: String) : CheckoutNavigation
}

class CheckoutViewModel : ViewModel() {
    private val _uiState = MutableStateFlow(CheckoutUiState())
    val uiState: StateFlow<CheckoutUiState> = _uiState.asStateFlow()

    fun onPaymentSuccess(orderId: String) {
        _uiState.update { it.copy(navigationEvent = CheckoutNavigation.NavigateToReceipt(orderId)) }
    }

    // Crucial: UI explicitly acknowledges consumption, clearing sticky state!
    fun onNavigationHandled() {
        _uiState.update { it.copy(navigationEvent = null) }
    }
}

// 2. In Jetpack Compose screen:
val state by viewModel.uiState.collectAsStateWithLifecycle()
LaunchedEffect(state.navigationEvent) {
    state.navigationEvent?.let { nav ->
        navController.navigate("receipt/${nav.orderId}")
        viewModel.onNavigationHandled() // Acknowledged! Rotation won't re-trigger!
    }
}
```

## Explanation in Arabic

تكرار حدث الانتقال مرتين بعد تدوير الشاشة (Navigation Event firing twice after rotation) هو أحد أشهر الـ Bugs الكلاسيكية في تطبيقات أندرويد:

1. كيف تحقق في هذا العطل وتكتشف سببه؟
   - **السبب رقم 1 (تخزين الحدث في StateFlow أو LiveData):** لو الـ ViewModel قام بتخزين أمر الانتقال في `StateFlow` (مثل `_uiState.value = NavigateToDetails`)، فالـ StateFlow بطبيعته يحتفظ بالقيمة الأخيرة في الذاكرة. عند تدوير الشاشة، الشاشة الجديدة تشترك في الـ StateFlow فتستلم نفس أمر الانتقال مجدداً وتنتقل مرتين!
   - **السبب رقم 2 (استخدام SharedFlow بـ replay >= 1):** لو تم ضبط `replay = 1`، المشترك الجديد بعد التدوير يستلم الحدث القديم من الـ Cache مجدداً.

2. الحلول المعمارية الصحيحة (The Architectural Fixes):
   - **الحل 1 (استخدام Channel للأحداث الفردية):** استخدام `Channel<NavigationEvent>(Channel.BUFFERED).receiveAsFlow()`. الـ Channel طابور يضمن تسليم العنصر لمرة واحدة فقط واستهلاكه فوراً، فلا يعاد بعد التدوير.
   - **الحل 2 (نمط استهلاك الحدث الصريح - Event Handled Pattern):** إذا كان الحدث داخل State، يتم إعطاؤه معرف فريد أو كائن `Event<T>`، وتطلب من الـ UI إرسال Intent للـ ViewModel فور استهلاكه (`viewModel.onNavigationHandled()`) ليقوم الـ ViewModel بتصفير الحالة إلى `null`.

## Practical walkthrough

إصلاح العطل في الـ ViewModel باستخدام Channel:
```kotlin
// ❌ الكود المسبب لتكرار الانتقال مرتين:
val navEvent = MutableStateFlow<NavRoute?>(null)
fun onCardClicked() { navEvent.value = NavRoute.Details } // عند التدوير سيعاد تنفيذه!

// ✅ الكود المصحح باستخدام Channel:
class MyViewModel : ViewModel() {
    private val _navEvents = Channel<NavRoute>(Channel.BUFFERED)
    val navEvents = _navEvents.receiveAsFlow()

    fun onCardClicked() {
        viewModelScope.launch {
            _navEvents.send(NavRoute.Details)
        }
    }
}
```
في Compose:
```kotlin
LaunchedEffect(Unit) {
    viewModel.navEvents.collect { route ->
        navController.navigate(route) // يتم استهلاكه وحذفه من الـ Channel؛ لن يتكرر أبداً!
    }
}
```

## Why it matters and how it works

Replayed state is correct for facts but can be wrong for imperative effects. A new collector may observe the last value, and duplicate collectors may both act. Channel receive can race with view destruction between dequeue and navigation. Instrument event IDs, producer calls and consumer lifecycle to locate duplication before changing primitive.

## Worked example

Conceptual Kotlin model uses a unique effect ID; UI must acknowledge after handling according to app navigation contract.

```kotlin
data class NavEffect(val id: Long, val route: String)
interface NavEffectStore {
    suspend fun pending(): NavEffect?
    suspend fun acknowledge(id: Long)
}
// UI reads pending, navigates under its lifecycle, then acknowledges;
// exact acknowledgement timing must be tested against rotation/process death.
```

## Trade-offs and decision criteria

For simple destination state, deriving navigation graph from authenticated state may be more robust than one-shot commands. An ID/ack protocol is more complex and must define when navigation counts as handled. SharedFlow replay zero avoids some duplicates but can lose offscreen emissions.

## Failure modes

Clearing a Boolean immediately after emission can race with collection and lose the effect; leaving it true replays it. A Channel may dequeue before the UI navigates and lose the action on rotation. Duplicated producer calls also need root-cause analysis.

## Production perspective

For sign-in, the authoritative session state drives the destination so a recreated UI lands correctly without issuing a repeated push. For a non-critical snackbar, best-effort loss is acceptable. Tests rotate before, during and after event consumption and record IDs in logs.

## Interview answer — short

Navigation fires twice because the event was stored in a sticky stream like StateFlow or SharedFlow with replay, replaying upon screen rotation. We fix this by modeling navigation as part of UI state with explicit consumption acknowledgement, or using a single-consumer buffered Channel.

## Interview answer — structured

Duplicate navigation upon screen rotation indicates that transient events were modeled using sticky state primitives.

StateFlow and SharedFlow with replay retain their latest emission in memory. When the Activity recreates upon rotation, the new UI collector subscribes and immediately receives the historical navigation payload, executing navigation a second time.

In production, legacy workarounds like EventWrapper or SingleLiveEvent introduced race conditions and anti-pattern flags that violated unidirectional data flow.
As for modern resolution, Google officially recommends modeling events directly inside the UI state class. The navigation payload resides as a nullable field within the state data class; as soon as the UI executes the navigation transition, it sends a consumption intent back to the ViewModel, which clears the event to null. Alternatively, a single-consumer buffered Channel guarantees exactly-once delivery without retention.


## Interview answer — deep senior

Under the hood, investigating duplicate emissions starts by inspecting the stream declaration inside the ViewModel. If the stream is declared as MutableStateFlow or MutableSharedFlow(replay = 1), the replay cache is the root cause. Upon recreation, repeatOnLifecycle enters STARTED and attaches a new subscriber slot. The hot flow traverses its circular buffer and immediately dispatches the cached item to the fresh subscriber before any user interaction occurs.
To eliminate this defect, two architectural patterns exist. The first pattern is the Single-Consumer Buffered Channel: Channel<NavEvent>(Channel.BUFFERED) exposed via receiveAsFlow(). A Channel enforces queue semantics where elements are consumed destructively; once the UI dequeues the navigation intent, it is permanently removed from memory, preventing replay across rotations.
The second pattern—recommended in modern Jetpack Compose architecture—is State-Driven Modeling with Explicit Consumption Acknowledgement. The UI state holds a nullable event object. In the Composable, a LaunchedEffect keyed to event executes the navigation command and immediately invokes viewModel.onEventConsumed(). The ViewModel atomically resets the state property to null via MutableStateFlow.update.
This pattern aligns with modern Unidirectional Data Flow guidelines: the UI never manages independent event state, but instead reflects the current state snapshot and dispatches user actions back to the ViewModel, eliminating navigation inconsistencies during configuration changes.
Staff engineers ban hacky solutions like reading and manually toggling boolean hasBeenHandled flags across multiple threads, enforcing deterministic state management across all navigation flows.

## How to answer in the interview

- **Why:** replay and consumption are separate concerns.
- **How:** reproduce duplicate, identify state/event owner, add acknowledgment.
- **Trade-off:** replay duplicates; no replay can lose.
- **Failure case:** clearing Boolean too early or late.
- **Production solution:** lifecycle-gap and process-death tests.

## Deep-dive talking points

Trace producer count, replay, two collectors and acknowledge-before/after-action windows.

## Follow-up questions

- **Interviewer:** "Why did `SingleLiveEvent` fall out of favor?"
  **Answer:** "Because `SingleLiveEvent` only supported a single observer. If multiple observers registered, only one received the event. Furthermore, it relied on an internal boolean atomic flag that violated reactive stream contracts."

- **Interviewer:** "What happens if a navigation event is sent while the app is in the background?"
  **Answer:** "With `Channel(Channel.BUFFERED)`, the event waits safely in the buffer. When the app returns to the foreground and collection resumes, the event is consumed and navigation proceeds safely."

- **Interviewer:** "Can you handle navigation directly from the ViewModel instead?"
  **Answer:** "In clean architecture, the ViewModel should not hold a reference to `NavController` or Android Views. It should only emit abstract routes (e.g., `NavRoute.Profile`), leaving the actual navigation mechanics to the UI layer."

## Self-check rubric

Can I diagnose root cause before changing type, define consumption and test rotation windows?

## References and reviewed-on date

- [Kotlin StateFlow API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-state-flow/) — replayed latest value.
- [Kotlin SharedFlow API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-shared-flow/) — replay behavior.

Technically reviewed against primary documentation on 2026-10-13.
