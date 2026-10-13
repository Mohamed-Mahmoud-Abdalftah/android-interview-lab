---
id: "FLO-30"
question: "A SharedFlow event has no active subscribers. What guarantees do replay and buffering actually give?"
topic: "Flow, StateFlow, SharedFlow & Channels"
code: "FLO"
group: "C"
phase: 1
priority: "P1"
order: 143
editorial_status: "reviewed"
---

# FLO-30

## Original interview question

A SharedFlow event has no active subscribers. What guarantees do replay and buffering actually give?

## What the interviewer evaluates

State precise absent-subscriber SharedFlow replay/buffer guarantees.

## Explanation in Arabic

لو `SharedFlow` أصدرت event ومفيش subscriber، اللي يتخزن للوافدين الجدد هو آخر `replay` قيم فقط. `extraBufferCapacity` مخصص للـsubscribers البطيئين الموجودين، مش backlog وقت الغياب؛ `BufferOverflow` ما يشتغلش أصلًا في حالة مفيش subscribers. `tryEmit` ممكن يرجع success رغم إن محدش استلم. ولو process اتقفل، replay in-memory تضيع.

### Practical walkthrough in Egyptian Arabic

`SharedFlow(replay=0, extraBufferCapacity=64)` ومعاها zero subscribers مش معناها 64 event مستنيين UI؛ من غير subscribers اللي يفضل هو replay cache فقط، وهنا صفر. حتى `emit` الناجحة لا تعني navigation اتنفذت. لو حدث لازم يوصل بعد ما التطبيق يرجع، خزّنه في state/durable store مع ID وack؛ replay=1 قد تعيد حدث قديم وتكرر action.

## Why it matters and how it works

With replay zero, no-subscriber emissions are lost. With replay n, a new subscriber receives up to n latest values, which can be correct for history or duplicate an imperative effect. Emission acknowledgement cannot be inferred from SharedFlow buffering; a durable queue needs persisted IDs and consumer acknowledgement.

## Worked example

JVM illustration shows two distinct contracts, not a durable event system.

```kotlin
import kotlinx.coroutines.flow.MutableSharedFlow

val disposable = MutableSharedFlow<String>(replay = 0, extraBufferCapacity = 8)
val latestNotice = MutableSharedFlow<String>(replay = 1)
// With no collectors: disposable retains nothing; latestNotice retains one.
```

## Trade-offs and decision criteria

Choose replay only if late subscribers should see past values. More replay increases duplication risk and memory. Extra capacity helps an active slow subscriber, while durable events require Room/server state plus acknowledgement.

## Failure modes

A navigation effect with replay zero can vanish while Activity is stopped. Replay one can navigate again after rotation. A buffered emission returning true is not proof that `collect` processed it.

## Production perspective

A payment status update is written to local database; UI observes StateFlow derived from it. A cosmetic snackbar uses replay zero and accepts loss while screen is absent. Tests explicitly emit before subscription and assert each contract.

## Interview answer — short

“Without subscribers, SharedFlow retains only replay values; extra buffer capacity and overflow do not queue events for later. `tryEmit` success is not delivery confirmation. Required events need persistence and acknowledgement.”

## Interview answer — structured

“I distinguish a replay cache from an active-subscriber buffer. If replay is zero, an emission during a no-subscriber window is lost, even if extraBufferCapacity is positive. If replay is one, a new subscriber receives the last value, which may repeat navigation after rotation. Overflow settings matter when subscribers lag, not when there are none. No setting survives process death or proves handling, so a business event is persisted with an ID and acknowledged.”

## Interview answer — deep senior

“A SharedFlow is a broadcast primitive with precise memory semantics. Replay holds recent values for new subscribers. Extra buffer capacity absorbs lag from subscribers already collecting; absent subscribers do not create a backlog beyond replay. `tryEmit` returning true only describes acceptance by the flow under its rules, not that a UI action completed. These distinctions matter most across STOP/START and rotation: replay zero may lose a toast, replay one may repeat a navigation command. I document which is acceptable, test no-subscriber emissions and late joins, and use a durable operation record plus acknowledgement if the event represents a payment or other required effect. I would test the absent-subscriber case explicitly. SharedFlow is hot, but with no active subscriber it retains only the configured replay cache; extra buffer capacity does not become an offline mailbox. With replay zero, an emitted event can disappear even if `emit` returns normally, and a successful `tryEmit` is not proof of UI consumption. With replay one, a new collector gets the last event, which can be useful for a latest signal but dangerous for navigation because it may fire again after rotation. Buffer overflow settings matter when subscribers are present and slow. For a required action, I use a recoverable state or durable command with an ID and acknowledgment and test no-subscriber, slow-subscriber, and restart paths.”

## How to answer in the interview

- **Why:** no-subscriber semantics are easy to misread.
- **How:** distinguish replay cache from extra buffer.
- **Trade-off:** replay recovery versus duplicate action.
- **Failure case:** tryEmit success mistaken for handling.
- **Production solution:** no-subscriber tests and durable commands when required.

## Deep-dive talking points

Trace tryEmit, replay cache, active lag and process death separately.

## Follow-up questions

- [FLO-19](../flo-19/): What is extraBufferCapacity for? **Answer:** lagging active subscribers.
- [FLO-20](../flo-20/): Would Channel fix process death? **Answer:** no; an in-memory channel is also lost.

## Self-check rubric

Can I predict replay zero/one while absent and explain why success is not acknowledgement?

## References and reviewed-on date

- [Kotlin SharedFlow API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-shared-flow/) — absent-subscriber rules.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
