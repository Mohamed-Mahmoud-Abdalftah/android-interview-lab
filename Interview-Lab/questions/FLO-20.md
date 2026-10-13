---
id: "FLO-20"
question: "Compare Channel and SharedFlow, including event-loss and delivery caveats."
topic: "Flow, StateFlow, SharedFlow & Channels"
code: "FLO"
group: "B"
phase: 1
priority: "P1"
order: 133
editorial_status: "reviewed"
---

# FLO-20

## Original interview question

Compare Channel and SharedFlow, including event-loss and delivery caveats.

## What the interviewer evaluates

Compare Channel queue/receive semantics with SharedFlow broadcast and acknowledge delivery limits.

## Explanation in Arabic

`Channel` بيوزع كل element عادة لمستقبل واحد من receivers متنافسين، و`SharedFlow` broadcast لكل subscribers النشطين حسب replay/buffer. Channel ممكن تحتفظ بعناصر في buffer أثناء غياب receiver داخل نفس process، لكن لو process مات ضاعت؛ و`receive` مش ضمان إن UI نفذت الفعل بعد ما استلمته. SharedFlow replay صفر ممكن يضيّع event بدون subscriber، وreplay موجب ممكن يعيدها.

### Practical walkthrough in Egyptian Arabic

`Channel` غالبًا point-to-point: كل element تروح لواحد من receivers، بينما `SharedFlow` broadcast للمشتركين الحاليين حسب replay. الاتنين في الذاكرة ومش ضمان إن UI نفذت navigation فعلًا؛ send ناجحة لقناة لا تعني handling تم قبل crash. لو لازم effect تعيش rotation/process death، خزّن event ID في state/durable layer واعمل acknowledgment.

## Why it matters and how it works

Channel has send/receive and close semantics; receiveAsFlow exposes one-consumer distribution among multiple collectors. SharedFlow is hot broadcast and never completes normally. Both require a lifecycle and delivery contract. For exactly-once business effects use durable IDs and acknowledgement at the source of truth.

## Worked example

JVM example with coroutines-core; buffered channel is explicitly in-process and the consumer owns lifecycle.

```kotlin
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.flow.receiveAsFlow

class EffectQueue {
    private val queue = Channel<String>(Channel.BUFFERED)
    val effects = queue.receiveAsFlow()
    suspend fun send(effect: String) { queue.send(effect) }
    fun close() { queue.close() }
}
```

## Trade-offs and decision criteria

Channel fits single-consumer handoff in one process; SharedFlow fits broadcast. A buffered Channel can accumulate while UI is absent, but size and process lifetime matter. Neither automatically gives durable exactly-once handling, and a Channel can deliver to an obsolete consumer.

## Failure modes

With two collectors of `receiveAsFlow`, each Channel element goes to one, not both. Rotation can race send/receive and handler execution; an event consumed just before destruction may never be acted on. A Channel buffer vanishes on process death.

## Production perspective

A snackbar may use a best-effort SharedFlow. A local in-process command dispatcher may use Channel with one owner. Payment completion is persisted as transaction state; UI effect consumption is recorded if it must be once per account.

## Interview answer — short

“Channel is a one-consumer queue with close semantics; SharedFlow broadcasts to active subscribers with chosen replay. Both are in-memory and have event-loss or duplication windows. I persist required business events and define acknowledgement.”

## Interview answer — structured

“I choose based on audience and delivery needs. Channel sends elements to receivers; if multiple collectors use `receiveAsFlow`, an element goes to one of them. SharedFlow broadcasts to active subscribers and can replay history. A buffered Channel may wait for an absent receiver in process, whereas replay-zero SharedFlow may drop that emission. But process death clears both, and receiving an event does not prove the UI performed its effect. For critical navigation or payment outcomes, I model durable state and a consumption protocol.”

## Interview answer — deep senior

“The word ‘event’ hides several contracts. Is it one receiver or several? Can it be lost while UI is stopped? Can it replay after rotation? Must it survive process death, and when is it acknowledged? Channel handles in-process handoff to one receiver and can buffer, but a receiver may remove an item just before its view is destroyed. SharedFlow broadcasts and its replay can help late subscribers, but can duplicate one-shot effects. Neither guarantees exactly-once business processing. I keep durable outcomes in Room/server state with stable IDs, use a lifecycle-aware UI consumer, and test the race between send, receive, rotation and acknowledgement. I would ask whether the event is work for one consumer or a broadcast to all active observers. Channel distributes elements among receivers and can queue according to capacity; SharedFlow broadcasts emissions and can replay some to late subscribers. Neither gives transactional exactly-once UI handling. A channel send can succeed and the process can die before the receiver navigates; a zero-replay SharedFlow can emit while no screen collects and lose the event. Conversely, replay can duplicate an action after rotation. For a truly important transition, such as opening a receipt after payment, I model the completed destination as recoverable state or a durable command with an ID and acknowledgment. Then I test lifecycle gaps, duplicate collectors, and process death.”

## How to answer in the interview

- **Why:** event transport is not event consumption.
- **How:** compare one receiver versus broadcast and replay.
- **Trade-off:** queueing/replay can still duplicate or lose.
- **Failure case:** navigation event vanishes or repeats.
- **Production solution:** durable identity and acknowledgment for required transitions.

## Deep-dive talking points

Draw delivery windows before receiver, after receive/before action and across process death.

## Follow-up questions

- [FLO-19](../flo-19/): What does SharedFlow retain without subscribers? **Answer:** only configured replay values.
- [FLO-10](../flo-10/): What is durable state? **Answer:** a current fact stored independently of transient UI collection.

## Self-check rubric

Can I compare one-consumer/broadcast, explain rotation loss and specify an acknowledgement boundary?

## References and reviewed-on date

- [Kotlin SharedFlow API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-shared-flow/) — broadcast/replay semantics.
- [Kotlin Channel API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.channels/-channel/) — send/receive and close.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
