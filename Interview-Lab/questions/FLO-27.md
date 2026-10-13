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

This bug occurs when navigation events are improperly modeled as persistent state in StateFlow or SharedFlow with replay >= 1, causing the recreated UI to re-read and re-execute the cached event. Fix it by modeling one-off events using a buffered Channel.receiveAsFlow() or consuming and clearing the event from state immediately upon execution.

## Interview answer — structured

When a navigation event fires twice after screen rotation, it is almost always caused by modeling a transient event as durable state.

The root cause is storing navigation commands in a `StateFlow` or a `SharedFlow` configured with `replay >= 1`. When the device rotates, the Activity is destroyed and recreated. When the new Activity subscribes to the stream, the flow dutifully replays the cached navigation command from memory, triggering a duplicate navigation transaction.

To fix this, we change the event modeling to guarantee **single-time consumption**:

1. **Channel-based Events:** Use a private `Channel<NavTarget>(Channel.BUFFERED)` and expose `channel.receiveAsFlow()`. Channels are FIFO queues: once an event is consumed by the UI, it is dequeued. A recreated Activity on rotation will find the channel empty.

2. **State-driven Acknowledgment:** If kept in UI state (`data class UiState(val navRoute: NavRoute? = null)`), the UI must immediately notify the ViewModel upon navigation (`viewModel.onNavigated()`), which resets `navRoute = null` before any rotation can occur.

## Interview answer — deep senior

In code review investigations, I verify the event lifecycle across three audit checkpoints:

1. **Stream Type Inspection:** Check if the event flow is declared as `MutableStateFlow` or `MutableSharedFlow(replay = 1)`. If yes, replace it with `Channel(Channel.BUFFERED).receiveAsFlow()`.

2. **Collection Lifecycle Inspection:** In View-based code, verify that navigation events are collected inside `viewLifecycleOwner.lifecycleScope.launch { viewLifecycleOwner.repeatOnLifecycle(STARTED) { ... } }`. In Compose, verify it uses `LaunchedEffect(Unit)`.

3. **Queue Deduplication:** If using Channel, ensure the channel is buffered (`Channel.BUFFERED`) so events sent while the screen is in transit between lifecycles are retained until the new screen is ready, but consumed strictly once.

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
