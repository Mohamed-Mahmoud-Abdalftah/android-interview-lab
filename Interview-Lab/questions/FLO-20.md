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

المقارنة بين `Channel` و `SharedFlow` هي الفارق الجوهري بين طوابير المهام الفردية (Work Queues) والبث الجماعي (Broadcasting):

1. الـ `Channel` (Queue - 1:1 Delivery):
   - يعمل كـ **طابور مهام (Queue)** بين المنتجين والمستهلكين.
   - **العنصر الواحد يستهلكه مستمع واحد فقط (Single Consumer / Point-to-Point)!** لو عندك مستمعان (Collector A و B)، العنصر الأول سيذهب لـ A، والعنصر الثاني سيذهب لـ B بالتناوب.
   - يضمن عدم فقدان الأحداث (No event loss) لو تم استخدام `Channel.BUFFERED`، حيث تنتظر الأحداث في الطابور حتى يأتي مستهلك لقراءتها.
   - مثالي جداً لـ: **أحداث الـ Navigation و Side Effects لمرة واحدة (One-off events)**.

2. الـ `SharedFlow` (Broadcast - 1:N Multicast):
   - يعمل كـ **محطة إذاعة وراديو (Broadcast)**.
   - **العنصر الواحد يذهب لجميع المستمعين النشطين في نفس الوقت (Fan-out / Multicast)!**
   - **خطر فقدان الأحداث (Event Loss Caveat):** لو تم بث حدث ولا يوجد أي مستمع متصل حالياً (وكان `replay = 0`)، **الحدث يضيع في الفضاء للأبد**!
   - مثالي جداً لـ: مراقبة أحداث عامة مشتركة، إشعارات التطبيق، أو تحديثات حالة يشترك فيها عدة شاشات.

## Practical walkthrough

مقارنة عملية في التعامل مع حدث الانتقال (Navigation Event):
```kotlin
// ❌ فخ الـ SharedFlow مع الـ Navigation:
val navEvents = MutableSharedFlow<NavRoute>() // replay = 0
// إذا ضغط المستخدم الزر أثناء انتقال الشاشة وقبل أن يبدأ Composable الجديد بالاستماع:
navEvents.emit(NavRoute.Details) // ضاع الحدث للأبد! لن ينتقل التطبيق!

// ✅ الحل باستخدام Channel للأحداث الفردية:
private val _navChannel = Channel<NavRoute>(Channel.BUFFERED)
val navFlow = _navChannel.receiveAsFlow()

fun onNavigateClicked() {
    viewModelScope.launch {
        _navChannel.send(NavRoute.Details) // ينتظر بأمان في الـ Buffer حتى تفتح الشاشة وتستقبله!
    }
}
```

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

A Channel is a point-to-point FIFO queue where each element is consumed by exactly one receiver with zero event loss when buffered; SharedFlow is a broadcast multicaster where every emission fans out to all active subscribers, but drops events if no subscribers are listening when replay is 0.

## Interview answer — structured

The architectural distinction between `Channel` and `SharedFlow` lies in communication topology and event delivery guarantees.

A **Channel** is a point-to-point communication primitive (1-to-1). It models a queue: if multiple collectors read from a Channel, they compete for items, and each item is consumed by exactly one collector. Because it is buffered (`Channel.BUFFERED`), it guarantees zero event loss: an event sent while the UI is rotating or backgrounded waits safely in the queue until the UI recreates and consumes it. This makes Channels ideal for one-off side effects like navigation commands.

A **SharedFlow** is a broadcast multicaster (1-to-N). Every emitted item is delivered to all active subscribers simultaneously. However, its major caveat is event loss: if an emission occurs when zero collectors are subscribed and `replay = 0`, the event is dropped permanently. It is suited for telemetry and broadcast notifications where dropped transient events are acceptable.


## Interview answer — deep senior

Under the hood, `Channel` manages an explicit queue of elements and suspended continuations. When `send()` is invoked, if a receiver is waiting in `receive()`, the value is handed off directly between continuations without buffering. When converting a Channel to a Flow using `receiveAsFlow()`, you get a hot flow backed by that Channel. However, if multiple collectors collect from `receiveAsFlow()`, they will interleave item consumption rather than multicasting.

In contrast, `SharedFlow` maintains a ring buffer and an array of subscriber slot pointers. Each subscriber tracks its own index in the buffer. In Android architecture, this distinction dictates our pattern for ViewModel-to-UI communication: Use **StateFlow** for state (`UiState`); Use **Channel.receiveAsFlow()** for single-consumption events (`Navigation`, `Toast`); and Use **SharedFlow** only when multiple independent screens/subscribers must receive the exact same event.


## How to answer in the interview

- **Why:** event transport is not event consumption.
- **How:** compare one receiver versus broadcast and replay.
- **Trade-off:** queueing/replay can still duplicate or lose.
- **Failure case:** navigation event vanishes or repeats.
- **Production solution:** durable identity and acknowledgment for required transitions.

## Deep-dive talking points

Draw delivery windows before receiver, after receive/before action and across process death.

## Follow-up questions

- **Interviewer:** "What happens if a Channel is closed?"
  **Answer:** "Calling `channel.close()` signals that no more elements will be sent. Any buffered elements are delivered to receivers, and subsequent receive attempts return closed indicators or throw a ClosedReceiveChannelException."

- **Interviewer:** "Can you consume a Channel from multiple coroutines?"
  **Answer:** "Yes, this is known as the 'Fan-out' pattern. Multiple worker coroutines can listen to the same Channel, processing tasks concurrently where each task is picked up by the first available worker."

- **Interviewer:** "Why does Google recommend modeling events as UI State instead of Channels?"
  **Answer:** "Because modeling events as state (e.g., `data class UiState(val message: Message?)`) keeps everything in a single unidirectional data flow pipeline, is easier to test, and naturally survives process recreation with SavedStateHandle."

## Self-check rubric

Can I compare one-consumer/broadcast, explain rotation loss and specify an acknowledgement boundary?

## References and reviewed-on date

- [Kotlin SharedFlow API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-shared-flow/) — broadcast/replay semantics.
- [Kotlin Channel API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.channels/-channel/) — send/receive and close.

Technically reviewed against primary documentation on 2026-10-13.
