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

## Concept and technical explanation

StateFlow and SharedFlow are specialized "hot" stream primitives in Kotlin coroutines whose execution and lifecycle exist independently of the presence or number of active collectors. Unlike cold flows, a hot stream begins executing and holds values in memory as soon as it is allocated in a CoroutineScope, broadcasting emissions to multiple concurrent subscribers simultaneously (multicast). StateFlow is a state-holder hot stream that always stores and exposes a current value, requires an initial value upon instantiation, conflates sequential updates, and replays exactly its latest state to newly arriving subscribers. SharedFlow is a highly configurable, general-purpose hot event bus that supports custom replay cache sizes, extra buffer capacities, and configurable BufferOverflow drop strategies. They are classified as "hot" because their upstream producers emit regardless of whether downstream collectors are actively listening, and emissions not captured within configured buffers are dropped.

## Practical walkthrough (English)

Contrasting StateFlow state retention with SharedFlow event broadcasting:
```kotlin
class NewsFeedViewModel : ViewModel() {
    // 1. StateFlow: Holds current state, requires initial value, always replays 1 to new collectors
    private val _uiState = MutableStateFlow<NewsUiState>(NewsUiState.Loading)
    val uiState: StateFlow<NewsUiState> = _uiState.asStateFlow()

    // 2. SharedFlow: Broadcasts transient events, zero replay by default, drops if uncollected
    private val _userEvents = MutableSharedFlow<UserMessage>(
        replay = 0,
        extraBufferCapacity = 1,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )
    val userEvents: SharedFlow<UserMessage> = _userEvents.asSharedFlow()

    fun onRefresh() {
        viewModelScope.launch {
            _uiState.value = NewsUiState.Success(fetchNews())
            _userEvents.emit(UserMessage.ShowToast("Feed updated successfully!"))
        }
    }
}
```

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

StateFlow and SharedFlow are hot streams because they exist and emit independently of collectors, multicasting values to multiple subscribers. StateFlow is a state holder that always retains a current value, requires an initial state, and conflates updates. SharedFlow is a configurable event stream with customizable replay cache, buffer capacity, and overflow policies.

## Interview answer — structured

StateFlow and SharedFlow represent hot streams whose lifecycles operate independently of downstream collectors.

The definition of a "hot" stream is that it produces and retains values in memory regardless of whether any subscriber is actively listening. When values are emitted, they are broadcast simultaneously to all active collectors using a multicast distribution model.

In production, we choose between them based on state persistence versus event transmission. StateFlow is designed specifically for UI state management. It requires an initial value, exposes a synchronous value getter, replays exactly its current state to new subscribers, and automatically conflates identical consecutive values.

SharedFlow serves as an event stream. It does not require an initial value and allows engineers to customize replay capacity, buffer size, and overflow behavior, making it the preferred primitive for broadcasting one-off events, system notifications, or shared domain messages across multiple application components.


## Interview answer — deep senior

At the lower plumbing layer of kotlinx.coroutines, StateFlow and SharedFlow are built on top of AbstractSharedFlow, a thread-safe allocation-free synchronization structure. Unlike cold flows that execute via sequential continuation passes, hot flows maintain an internal array of active subscriber slots (StateFlowSlot and SharedFlowSlot). When emit is invoked, the hot stream acquires an internal mutex, iterates over its active slot table, and wakes up suspended collector continuations directly.
StateFlow is mathematically equivalent to a specialized SharedFlow configured with replay = 1 and onBufferOverflow = BufferOverflow.DROP_OLDEST, coupled with strict Any.equals conflation. When MutableStateFlow.value is updated, it performs an equality check: if the new value equals the existing value, the emission is discarded immediately without waking collector slots, preventing redundant recompositions in Jetpack Compose and frame drops.
SharedFlow provides fine-grained backpressure tuning through three constructor parameters: replay determines how many previous emissions are cached for new subscribers; extraBufferCapacity provides headroom for emissions when collectors are slow; and onBufferOverflow dictates whether emit suspends (SUSPEND), drops the oldest buffered value (DROP_OLDEST), or drops the newly emitted value (DROP_LATEST).
Staff engineers enforce strict guidelines: UI screens must observe state via StateFlow to guarantee that rotated screens instantly render the current state; transient one-off events must either use SharedFlow with replay = 0 or be modeled directly as consumed fields within the single immutable StateFlow to prevent event loss or double execution.

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
