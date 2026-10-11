---
id: "FLO-19"
question: "Explain replay, extraBufferCapacity, and BufferOverflow in SharedFlow."
topic: "Flow, StateFlow, SharedFlow & Channels"
code: "FLO"
group: "B"
phase: 1
priority: "P1"
order: 132
editorial_status: "reviewed"
---

# FLO-19

## Original interview question

Explain replay, extraBufferCapacity, and BufferOverflow in SharedFlow.

## What the interviewer evaluates

Explain replay, per-subscriber buffer capacity and overflow behavior including absent subscribers.

## Explanation in Arabic

`replay` عدد القيم القديمة اللي subscriber جديد يشوفها. `extraBufferCapacity` مساحة إضافية للتعامل مع subscriber بطيء، و`BufferOverflow` يحدد suspend أو إسقاط الأقدم/الأحدث لما buffer يتملي. نقطة مهمة: لو مفيش subscribers، SharedFlow تحتفظ بقيم replay فقط؛ extra buffer ما بيعملش queue لأحداث المستقبل. ولا إعداد يضمن بقاء event بعد process death.

## Why it matters and how it works

Replay cache is shared history for new subscribers. Extra capacity is relevant to lagging active subscribers. With no subscribers, overflow policy is not triggered and only last replay values are retained. `tryEmit` success does not prove any subscriber processed an event; acknowledgement is separate.

## Worked example

JVM snippet defines a lossy UI signal contract; it must not carry a required payment operation.

```kotlin
import kotlinx.coroutines.channels.BufferOverflow
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.asSharedFlow

class Signals {
    private val mutable = MutableSharedFlow<String>(
        replay = 0, extraBufferCapacity = 1,
        onBufferOverflow = BufferOverflow.DROP_OLDEST,
    )
    val events = mutable.asSharedFlow()
    fun announce(message: String) { mutable.tryEmit(message) }
}
```

## Trade-offs and decision criteria

`replay=1` helps late subscribers see a value but may duplicate one-shot effects. Extra capacity helps active slow subscribers but is not durability. `SUSPEND` backpressures emitters with subscribers; drop policies favor freshness at the cost of lost events.

## Failure modes

An event emitted at STOP with replay zero is absent when collection restarts. `tryEmit` may return true while no subscriber receives anything. A replayed navigation command may execute twice after rotation.

## Production perspective

A dashboard uses SharedFlow for best-effort snackbars where loss is acceptable. Order status changes are persisted in Room and derived as StateFlow, with IDs and acknowledgement if a UI action must occur once.

## Interview answer — short

“Replay supplies old values to new subscribers. Extra buffer capacity helps current slow subscribers; overflow policy decides suspend or drop when full. With no subscribers, only replay is retained, so this is not a durable queue.”

## Interview answer — structured

“I set SharedFlow parameters from a delivery contract. Replay controls what late subscribers see. Extra buffer capacity absorbs lag from active subscribers, and BufferOverflow defines whether an emitter suspends or old/new values drop when that capacity is exhausted. Without subscribers, only replay values are stored; extra capacity does not queue events for later. A successful `tryEmit` does not mean the UI handled the event. For a required business outcome I use durable state and explicit acknowledgement rather than tuning a SharedFlow buffer.”

## Interview answer — deep senior

“There are three distinct questions: what a new subscriber receives, how far an active subscriber may lag, and whether anything survives process death. Replay addresses the first; extraBufferCapacity and overflow address the second; none addresses the third. In the absence of subscribers, SharedFlow stores only replay and overflow settings do not turn it into a queue. This makes replay-zero suitable for disposable visual effects, but it may lose events while the Activity is stopped. Replay can cause a navigation effect to fire again after rotation. I test emissions before subscription, during a slow collector and after re-subscription, and I use persisted operation records for anything that must be handled reliably.”

## Deep-dive talking points

Walk through no subscriber, slow subscriber and new subscriber timelines.

## Follow-up questions

- [FLO-30](../flo-30/): Does extra capacity save absent-subscriber events? **Answer:** no, only replay cache does.
- [FLO-27](../flo-27/): Why duplicate navigation? **Answer:** replayed effect or unconsumed state can trigger it again.

## Self-check rubric

Can I predict values under each subscriber condition and distinguish buffer success from acknowledgement?

## References and reviewed-on date

- [Kotlin SharedFlow API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-shared-flow/) — replay, buffer and absent-subscriber behavior.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
