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

`StateFlow` و`SharedFlow` hot: الـinstance موجودة وبتستقبل updates حتى من غير collector، على عكس `flow {}` العادية. `StateFlow` عندها `value` ابتدائية وآخر state، وتمنع القيم المتساوية؛ `SharedFlow` broadcast قابل لضبط replay/buffer ومن غير قيمة ابتدائية مفروضة. ولا واحدة منهم queue مضمونة عبر process death.

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

“Both StateFlow and SharedFlow are hot. StateFlow has a current value and equality-based state behavior; SharedFlow is a configurable broadcast stream. I use the first for UI snapshots and define explicit delivery requirements before using the second for events.”

## Interview answer — structured

“Hot means the stream instance and its updates exist independently of a particular collector. StateFlow requires an initial value, exposes the latest state and suppresses equal updates. SharedFlow supports configurable replay and buffering and can broadcast to several subscribers. Neither guarantees an event survives process death. In Android I usually expose a read-only StateFlow for screen state and collect it with lifecycle awareness. For transient effects I define whether loss or replay is acceptable before choosing SharedFlow, Channel or persisted state. Use StateFlow for a current UI snapshot; SharedFlow when broadcast/replay semantics are deliberately specified. `extraBufferCapacity` helps slow subscribers, not a guaranteed no-subscriber queue. Durable commands require persistence and acknowledgement. A ViewModel exposes immutable screen state through StateFlow. Toast-like best-effort signals may use SharedFlow with documented loss tolerance.”

## Interview answer — deep senior

“The design question is the consumer contract. If a recreated UI must immediately render a current snapshot, StateFlow’s always-available value is appropriate; slow collectors can skip intermediate states. SharedFlow lets me set replay and buffering, but those settings have precise subscriber semantics and are not a durable message broker. A replay-zero emission with no subscribers may be lost, while replay can duplicate a one-shot effect after rotation. I keep mutable implementations private, scope producers to ViewModel/session ownership, and persist any business event whose acknowledgement matters. Tests cover subscribers joining late, rotation and no-subscriber windows. A `MutableStateFlow` retains current value and emits latest to new collectors; its collection does not complete normally. `MutableSharedFlow` retains configured replay values and can broadcast to active subscribers. The owner scope determines who publishes and for how long; Android UI collectors should still be lifecycle-aware. Using StateFlow for a one-time navigation flag can replay `true` after rotation. Using a replay-zero SharedFlow while no collector exists can lose a signal. A hot stream without a proper owner may retain state longer than intended. A ViewModel exposes immutable screen state through StateFlow. Toast-like best-effort signals may use SharedFlow with documented loss tolerance. Payment status is stored in Room and derived as state, so a process death cannot erase the business outcome.”

## Deep-dive talking points

Contrast hot producer lifetime, current value, replay cache, slow collector and process death.

## Follow-up questions

- [FLO-05](../flo-05/): Why initial state? **Answer:** StateFlow promises a readable current `value`.
- [FLO-19](../flo-19/): Does extra buffer persist without subscribers? **Answer:** no; only configured replay is retained then.

## Self-check rubric

Can I define hot, compare value/replay, select a UI use and describe loss after process death?

## References and reviewed-on date

- [Kotlin StateFlow API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-state-flow/) — current value and conflation.
- [Kotlin SharedFlow API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-shared-flow/) — replay/buffer semantics.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
