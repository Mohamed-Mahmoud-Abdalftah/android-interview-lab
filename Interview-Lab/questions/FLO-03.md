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

`StateFlow` and `SharedFlow` are hot `Flow` implementations: their objects and stored values are independent of any individual collection. Collecting either does not start a fresh producer per collector. Hot does not mean a producer begins running merely because a `MutableSharedFlow` was allocated; code must assign or emit values, and an upstream shared through `shareIn` or `stateIn` follows its `SharingStarted` policy. `StateFlow` always exposes a current value, requires an initial value, replays the latest state, and conflates equal updates. `SharedFlow` has configurable replay and buffer/overflow behavior but no `.value` property. With replay zero, a late subscriber misses past emissions, while simultaneous subscribers can each receive one broadcast.

## Practical walkthrough (English)

A ViewModel can expose current UI state and a best-effort broadcast separately. The producer is the code that assigns or emits; construction alone does not start a periodic job.

```kotlin
class NewsFeedViewModel : ViewModel() {
    private val _uiState = MutableStateFlow<NewsUiState>(NewsUiState.Loading)
    val uiState: StateFlow<NewsUiState> = _uiState.asStateFlow()

    private val _refreshTicks = MutableSharedFlow<Unit>(replay = 0)
    val refreshTicks: SharedFlow<Unit> = _refreshTicks.asSharedFlow()

    fun refresh() = viewModelScope.launch {
        _uiState.value = NewsUiState.Success(fetchNews())
        _refreshTicks.emit(Unit) // late collectors will miss this tick
    }
}
```

## Explanation in Arabic

نسمي `StateFlow` و`SharedFlow` hot لأن **الكائن نفسه قائم مستقل عن الجمع**؛ الـ collector الجديد ما بيشغّلش نسخة جديدة من producer. لكن hot مش معناها إن فيه شغل أو إرسال مستمر من لحظة الإنشاء: `MutableSharedFlow()` وحده ساكت لحد ما حد ينادي `emit`، و`shareIn` ممكن يوقف upstream حسب `SharingStarted`.

`StateFlow` مناسب لقيمة حالية: يبدأ بـ initial value، تقدر تقرأ `.value` فورًا، والداخل الجديد يستلم آخر حالة. هو بيكتم القيم المتساوية وقد يتخطى حالات وسطية لو المستهلك بطيء.

`SharedFlow` بث لمشتركين متعددين. مافيش `.value` ولا قيمة ابتدائية لازمة؛ فيه `replay` وbuffer قابلين للضبط. مع `replay = 0`، اللي يدخل بعد event مش هيستلمه، واللي موجودين وقتها كلهم ممكن يستلموه. ده مش ضمان «مرة واحدة» ولا ضمان وصول عبر توقف الشاشة.

## Practical walkthrough

في ViewModel ممكن تميّز الحالة عن الإشارة:
```kotlin
private val _uiState = MutableStateFlow<LoginUiState>(LoginUiState.Idle)
val uiState: StateFlow<LoginUiState> = _uiState.asStateFlow()

private val _refreshTicks = MutableSharedFlow<Unit>(replay = 0)
val refreshTicks: SharedFlow<Unit> = _refreshTicks.asSharedFlow()
```
لو الشاشة رجعت بعد rotation، `uiState` يديها الحالة الحالية. لو `_refreshTicks.emit(Unit)` حصل وهي متوقفة، المشترك الجديد مش هياخد النبضة القديمة. ولو فيه مشتركين وقت الإرسال، الاتنين ممكن يستلموها. لو الإشارة مهمة لنتيجة عمل المستخدم، خزّن نتيجتها كحالة قابلة للاسترجاع بدل ما تعتمد على نبضة عابرة.

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

StateFlow and SharedFlow are hot because collecting them does not restart a producer for each subscriber. StateFlow holds a current value, requires an initial value, and conflates equal updates. SharedFlow broadcasts to active subscribers with configurable replay and buffering, but exposes no `.value`. A hot object need not emit continuously; its owner controls production.

## Interview answer — structured

Hot describes the relationship between a stream and its collectors: a new collector attaches to an existing StateFlow or SharedFlow rather than executing a new builder. It does not promise continuous production. A `MutableSharedFlow` without calls to `emit` remains quiet, and a flow shared with `shareIn` obeys `SharingStarted`.

Use StateFlow for a current UI snapshot. It has an initial value, synchronous `.value`, latest-value replay, equality suppression, and conflation for slow collectors. Use SharedFlow when a multicast contract needs explicit replay and buffering. At `replay = 0`, no-subscriber emissions are unavailable to later collectors; multiple active collectors can receive the same broadcast. Neither primitive alone provides durable, exactly-once business delivery across process death.

## Interview answer — deep senior

I first separate the hot stream object from its producer. A `MutableStateFlow` retains current state while referenced, and a `MutableSharedFlow` retains only its configured replay cache. Collecting these flows does not create one producer run per subscriber. But allocating a shared flow does not launch work: some owner must assign a state or emit an event. If a cold upstream was converted using `shareIn` or `stateIn`, `SharingStarted` controls when its sharing coroutine runs. `WhileSubscribed` may stop upstream during a subscriber gap and restart it later.

StateFlow is the state-holder contract: an initial value, synchronous `value`, latest snapshot for newcomers, equality-based suppression, and slow-collector conflation. SharedFlow instead offers replay count, extra buffer capacity, and overflow policy. It has `replayCache`, not `.value`. An extra buffer is headroom for existing slow subscribers, not a durable no-subscriber queue. With zero replay, an emission while no one collects is lost to future subscribers; with two active subscribers, both can observe the same emission.

The production decision depends on loss and replay tolerance. A periodic refresh tick can be best effort. A payment outcome or navigation consequence that must survive a lifecycle gap needs state or persistence with acknowledgement. I test a late collector, two concurrent collectors, a STOP/START gap, and process recreation instead of calling SharedFlow an exactly-once event channel.

## How to answer in the interview

- **Why:** state needs a current snapshot; events may not.
- **How:** compare initial value, replay, equality, and subscribers.
- **Trade-off:** hot streams need explicit owner and upstream policy.
- **Failure case:** replaying navigation as state after rotation.
- **Production solution:** test late collectors and lifecycle gaps.

## Deep-dive talking points

Contrast hot producer lifetime, current value, replay cache, slow collector and process death.

## Follow-up questions

- **Interviewer:** "Can a StateFlow collector miss intermediate states?"
  **Answer:** "Yes. A slow collector may move directly to the latest state; it is a snapshot, not a history log."
- **Interviewer:** "Does hot mean production starts at allocation?"
  **Answer:** "No. A mutable shared flow emits only when its owner calls `emit` or `tryEmit`; sharing operators obey their start policy."
- **Interviewer:** "What happens to a zero-replay SharedFlow emission with no subscribers?"
  **Answer:** "A later subscriber cannot receive it. It is not an exactly-once delivery mechanism."
- **Interviewer:** "Do two active collectors compete for one event?"
  **Answer:** "No. SharedFlow broadcasts to each active collector according to its buffering contract."

## Self-check rubric

Can I define hot, compare value/replay, select a UI use and describe loss after process death?

## References and reviewed-on date

- [Kotlin StateFlow API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-state-flow/) — current value and conflation.
- [Kotlin SharedFlow API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-shared-flow/) — replay/buffer semantics.

- [Android StateFlow and SharedFlow guide](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow) — owner and lifecycle examples.

Technically reviewed against primary documentation on 2026-10-19.
