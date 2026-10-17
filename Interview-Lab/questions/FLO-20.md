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

## Concept and technical explanation

The architectural distinction between Channel and SharedFlow centers on communication topology, delivery guarantees, and event-loss characteristics under lifecycle transitions.
Channel is a point-to-point (unicast), queue-based communication primitive. Every element sent to a Channel is delivered to and consumed by exactly one receiver; if multiple collectors listen to the same Channel, emissions are distributed competitively (fan-out worker queue) rather than broadcasted. Importantly, a buffered Channel retains elements in memory until consumed, guaranteeing that one-off events are not lost even if the UI is temporarily stopped.
SharedFlow is a broadcasting (multicast), hot reactive stream. Every element emitted is distributed simultaneously to all active collectors. However, SharedFlow requires active subscribers at emission time; if an event is emitted when zero subscribers are active (and replay cache is zero), the event is dropped permanently into the void, creating catastrophic event loss for navigation intents during lifecycle pauses.

## Practical walkthrough (English)

Contrasting Channel unicast delivery with SharedFlow multicasting:
```kotlin
class OrderProcessingViewModel : ViewModel() {
    // 1. Channel: Guarantees delivery to exactly ONE receiver, buffers during onStop
    private val _navigationChannel = Channel<OrderNavigationEvent>(Channel.BUFFERED)
    val navigationEvents = _navigationChannel.receiveAsFlow()

    // 2. SharedFlow: Broadcasts to ALL active screens, drops if no one is listening
    private val _orderUpdates = MutableSharedFlow<OrderBroadcast>(
        replay = 0,
        extraBufferCapacity = 16,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )
    val orderUpdates = _orderUpdates.asSharedFlow()

    fun onOrderApproved(orderId: String) {
        viewModelScope.launch {
            // Buffered until UI unpauses: Never lost!
            _navigationChannel.send(OrderNavigationEvent.OpenReceipt(orderId))

            // Multicast to all active observer screens:
            _orderUpdates.emit(OrderBroadcast.StatusChanged(orderId, "APPROVED"))
        }
    }
}
```

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

Channel is a unicast queue delivering each item to exactly one consumer, buffering events safely during UI pauses. SharedFlow is a multicast stream broadcasting to all active observers simultaneously, but drops emissions permanently if no subscribers exist at emission time unless replay or buffer is configured.

## Interview answer — structured

Channel and SharedFlow represent fundamentally distinct concurrency primitives serving opposing architectural topologies.

Channel implements queue semantics (unicast). Elements sent into a Channel remain in its buffer until a consumer dequeues them. When multiple collectors observe a Channel, each emission is consumed by only one worker, making Channel ideal for transactional work distribution.

In production, SharedFlow implements pub-sub broadcasting (multicast). Every emission is fanned out concurrently to all registered collectors, making it the premier choice for broadcasting state invalidation, user logout notifications, or global configuration updates across multiple screens.

The primary risk with SharedFlow is event loss. If an event is emitted while an Activity is in onStop and has detached its collector, a SharedFlow with replay = 0 discards the event completely. Conversely, a Channel buffers the message, delivering it reliably as soon as the UI enters onStart and resumes collection.


## Interview answer — deep senior

Under the hood in kotlinx.coroutines, Channel implements the SendChannel and ReceiveChannel interfaces, backed by low-level lock-free queues managing sender and receiver continuations. When send is invoked without an active receiver, the item sits in the channel buffer array. When receive or receiveAsFlow is invoked, the first waiting receiver extracts the element and dequeues it permanently.
Conversely, SharedFlow manages an array of SharedFlowSlots. When emit is invoked, it iterates through all registered slots, incrementing their read head pointers. If the slot array is empty (zero subscribers), the emit operation immediately returns. Unless replay is positive or extraBufferCapacity is configured with an uncollected buffer, the emission evaporates completely without trace.
However, Channel introduces its own architectural caveat: Single Consumer Queue semantics. If a developer uses receiveAsFlow() and collects it in two different Composables or Fragments, the collectors race to dequeue emissions. Collector A consumes event 1, and Collector B consumes event 2, resulting in split-brain event processing where neither UI screen observes the complete sequence.
During Android configuration changes, a buffered Channel safely queues one-shot navigation events while the Activity recreates, delivering the pending intent immediately upon reconnection without duplicating events across screen rotations.
Staff engineers apply strict architectural boundaries: Channel is reserved strictly for private 1:1 one-off UI events (like single-destination navigation), while SharedFlow is used strictly for 1:N multi-subscriber broadcasts with deliberate replay caching.

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
