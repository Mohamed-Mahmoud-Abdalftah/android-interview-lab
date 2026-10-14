---
id: "FLO-03"
question: "What are StateFlow and SharedFlow? Why are they hot?"
topic: "Flow, StateFlow, SharedFlow & Channels"
code: "FLO"
group: "A"
phase: 1
priority: "P1"
order: 116
editorial_status: "reviewed"
---

# FLO-03

## Original interview question

What are StateFlow and SharedFlow? Why are they hot?

## What the interviewer evaluates

Explain hot StateFlow/SharedFlow lifetime, current state versus configurable broadcast.

## Explanation in Arabic

الـ `StateFlow` والـ `SharedFlow` هما الـ Hot Streams الأساسيان في Kotlin Coroutines، وفهم سبب كونهما 'Hot' هو جوهر إدارة الحالة والأحداث:

1. ما معنى أنهما 'Hot Streams'؟
   - الـ Hot Stream **موجود ونشط وينتج بيانات باستمرار في الذاكرة (Memory-resident)** بغض النظر عما إذا كان هناك مستمعين (Collectors) أم لا!
   - يشبه البث المباشر في الراديو أو التلفزيون: المذيع يتكلم حتى لو لا يوجد أحد يستمع؛ ومن يفتح الراديو يسمع ما يُبث في اللحظة الحالية فقط.

2. ما هو الـ `StateFlow`؟
   - مخصص لـ **إدارة الحالة (State Management)**.
   - يحمل دائماً **قيمة حالية في الذاكرة** يمكن قراءتها في أي وقت عبر `stateFlow.value` (Synchronous read).
   - يتطلب قيمة ابتدائية إلزامية (Initial Value).
   - لديه **Conflation مدمج:** لو الحالة لم تتغير (وفقاً للـ `equals()`)، فلن يرسل أي تحديث للمستمعين.

3. ما هو الـ `SharedFlow`؟
   - مخصص لـ **بث الأحداث والإشارات (Events & Multicasting)**.
   - لا يشترط وجود قيمة ابتدائية.
   - يمكن ضبطه بـ `replay = N` لتحديد عدد الأحداث السابقة التي يستلمها أي مستمع جديد.
   - مناسب جداً للأحداث العابرة (Navigation, Show Snackbar, Analytics).

## Practical walkthrough

في شاشة تسجيل الدخول (Login Screen):
- **إدارة الـ State باستخدام `StateFlow`:**
  `private val _uiState = MutableStateFlow<LoginUiState>(LoginUiState.Idle)`
  `val uiState: StateFlow<LoginUiState> = _uiState.asStateFlow()`
  الشاشة تعرض `uiState.value`؛ ولو دور المستخدم الشاشة، الشاشة الجديدة تقرأ القيمة الحالية فوراً بدون إعادة تحميل.
- **إدارة الـ Navigation Event باستخدام `SharedFlow`:**
  `private val _events = MutableSharedFlow<LoginEvent>()`
  `val events: SharedFlow<LoginEvent> = _events.asSharedFlow()`
  عند نجاح تسجيل الدخول، نرسل: `_events.emit(LoginEvent.NavigateToHome)`.
  الحدث يتم استهلاكه لمرة واحدة فقط؛ ولا يعاد تشغيله عند تدوير الشاشة.

## Why it matters and how it works

A `MutableStateFlow` retains current value and emits latest to new collectors; its collection does not complete normally. `MutableSharedFlow` retains configured replay values and can broadcast to active subscribers. The owner scope determines who publishes and for how long; Android UI collectors should still be lifecycle-aware.

## Worked example

JVM illustration with `kotlinx-coroutines-core`; state and event are exposed read-only.

```kotlin
import kotlinx.coroutines.flow.*

class FeedModel {
    private val _state = MutableStateFlow("idle")
    val state: StateFlow<String> = _state.asStateFlow()
    private val _signals = MutableSharedFlow<String>(extraBufferCapacity = 1)
    val signals: SharedFlow<String> = _signals.asSharedFlow()
    fun markLoaded() { _state.value = "loaded" }
    suspend fun announce() { _signals.emit("refreshed") }
}
```

## Trade-offs and decision criteria

Use StateFlow for a current UI snapshot; SharedFlow when broadcast/replay semantics are deliberately specified. `extraBufferCapacity` helps slow subscribers, not a guaranteed no-subscriber queue. Durable commands require persistence and acknowledgement.

## Failure modes

Using StateFlow for a one-time navigation flag can replay `true` after rotation. Using a replay-zero SharedFlow while no collector exists can lose a signal. A hot stream without a proper owner may retain state longer than intended.

## Production perspective

A ViewModel exposes immutable screen state through StateFlow. Toast-like best-effort signals may use SharedFlow with documented loss tolerance. Payment status is stored in Room and derived as state, so a process death cannot erase the business outcome.

## Interview answer — short

StateFlow and SharedFlow are hot streams because they exist and emit independently of collectors, residing in memory. StateFlow manages observable state, always retains a current value (.value), and suppresses duplicate emissions; SharedFlow broadcasts events to multiple collectors with configurable replay caches and buffer policies.

## Interview answer — structured

StateFlow and SharedFlow are 'hot' streams because their lifecycles are completely decoupled from subscribers. Unlike cold flows that only execute when collected, hot flows exist in memory, accept emissions, and retain state regardless of whether any collectors are active.

**StateFlow** is specialized for state management. It is a state machine that always holds an accessible current value via `.value`. It requires an initial value, retains exactly the latest emission, and features built-in conflation—meaning it uses `Any.equals()` to suppress emissions if the new state is identical to the current state.

**SharedFlow** is a general-purpose, highly configurable multicaster designed for broadcasting events to multiple collectors. It does not require an initial value, supports configurable replay buffer sizes (`replay = N`), and handles backpressure buffer overflow strategies (`BufferOverflow.DROP_OLDEST` or `SUSPEND`).


## Interview answer — deep senior

Under the hood, `StateFlow` is actually a specialized, optimized subtype of `SharedFlow`. Specifically, `StateFlow` behaves identically to a `SharedFlow` configured with `replay = 1` and `onBufferOverflow = BufferOverflow.DROP_OLDEST`, augmented with two critical characteristics.

First, **Synchronous Value Access:** You can read `stateFlow.value` at any time from any thread without launching a coroutine. Finally, **State Deduplication:** When you write `_stateFlow.value = newState`, it compares `newState == oldState`. If true, the update is a no-op; it skips notifying collectors and avoids triggering Jetpack Compose recompositions.

In contrast, `MutableSharedFlow` allows duplicate identical emissions. If you emit `SnackbarMessage("Error")` twice, collectors receive both events sequentially, which is why SharedFlow is chosen for discrete user actions and events.


## How to answer in the interview

- **Why:** state needs a current snapshot; events may not.
- **How:** compare initial value, replay, equality, and subscribers.
- **Trade-off:** hot streams need explicit owner and upstream policy.
- **Failure case:** replaying navigation as state after rotation.
- **Production solution:** test late collectors and lifecycle gaps.

## Deep-dive talking points

Contrast hot producer lifetime, current value, replay cache, slow collector and process death.

## Follow-up questions

- **Interviewer:** "Can a subscriber to a StateFlow miss intermediate values?"
  **Answer:** "Yes! Because StateFlow is conflated, if the producer emits values 1, 2, and 3 faster than a slow collector can process them, the collector may jump directly from 1 to 3, missing 2. StateFlow guarantees delivery of the most recent state, not historical delivery of every transition."

- **Interviewer:** "Why does StateFlow require an initial value while SharedFlow does not?"
  **Answer:** "Because StateFlow represents continuous state and exposes a synchronous `.value` property that must never return undefined or null unless explicitly typed as nullable (e.g., `StateFlow<User?>`)."

- **Interviewer:** "What happens when you emit to a `SharedFlow` with `replay = 0` when there are no collectors?"
  **Answer:** "The emission is dropped immediately and permanently lost. Any subscriber that connects a millisecond later will not receive that event."

## Self-check rubric

Can I define hot, compare value/replay, select a UI use and describe loss after process death?

## References and reviewed-on date

- [Kotlin StateFlow API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-state-flow/) — current value and conflation.
- [Kotlin SharedFlow API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-shared-flow/) — replay/buffer semantics.

Technically reviewed against primary documentation on 2026-10-13.
