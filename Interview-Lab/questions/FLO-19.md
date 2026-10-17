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

## Concept and technical explanation

Configuring MutableSharedFlow relies on three interrelated buffering parameters: replay, extraBufferCapacity, and onBufferOverflow, which govern backpressure mitigation, subscriber catch-up, and memory allocation.
replay designates the size of the replay cache—the exact number of previously emitted elements retained in memory and instantly delivered to newly attached subscribers.
extraBufferCapacity designates additional reserved buffer slots beyond the replay cache, providing temporary shock absorption when upstream producers generate emissions faster than downstream subscribers can consume them.
onBufferOverflow defines the precise eviction strategy executed when the total buffer capacity (the sum of replay plus extraBufferCapacity) is fully saturated. It supports three distinct strategies: BufferOverflow.SUSPEND (suspends the emitter until buffer space frees up), BufferOverflow.DROP_OLDEST (evicts the oldest buffered element to accommodate the incoming item without suspending), and BufferOverflow.DROP_LATEST (discards the newly arriving emission immediately, preserving existing buffer contents).

## Practical walkthrough (English)

Tuning SharedFlow buffer parameters for production workloads:
```kotlin
class LiveEventBus {
    // 1. Lossless event bus: Suspends emitter, guarantees zero event drops
    private val _criticalEvents = MutableSharedFlow<PaymentEvent>(
        replay = 0,
        extraBufferCapacity = 64,
        onBufferOverflow = BufferOverflow.SUSPEND
    )
    val criticalEvents = _criticalEvents.asSharedFlow()

    // 2. High-throughput sensor ticker: Never suspends, drops oldest ticks
    private val _sensorTicks = MutableSharedFlow<Float>(
        replay = 1, // Latest tick delivered to new screens
        extraBufferCapacity = 16,
        onBufferOverflow = BufferOverflow.DROP_OLDEST // Drops stale ticks under load
    )
    val sensorTicks = _sensorTicks.asSharedFlow()

    suspend fun postPayment(event: PaymentEvent) {
        _criticalEvents.emit(event) // Suspends if buffer fills up
    }

    fun postTick(value: Float) {
        _sensorTicks.tryEmit(value) // Always returns true with DROP_OLDEST
    }
}
```

## Explanation in Arabic

المعاملات الثلاثة لـ `MutableSharedFlow` (`replay`, `extraBufferCapacity`, `onBufferOverflow`) بتحدد سلوك الذاكرة وتوزيع الأحداث بدقة بالغة:

1. المعامل `replay` (ذاكرة الإعادة للمستمعين الجدد):
   - يحدد عدد العناصر السابقة (Past Items) التي يتم حفظها في الذاكرة لتسليمها فوراً لأي مستمع جديد يشترك مستقبلاً.
   - لو `replay = 0`: المستمع الجديد لن يستلم أي شيء من الماضي؛ يستلم فقط ما يصدر بعد لحظة اشتراكه.
   - لو `replay = 1`: المستمع الجديد يستلم أحدث عنصر فور اشتراكه (كما يفعل StateFlow).

2. المعامل `extraBufferCapacity` (سعة التخزين المؤقت الإضافية):
   - يحدد حجم الـ Buffer المتاح للـ Producer قبل أن يضطر للتعليق (Suspension) عند بطء المستمعين.
   - الحجم الكلي المتاح للذاكرة المؤقتة هو: `replay + extraBufferCapacity`.

3. المعامل `onBufferOverflow` (استراتيجية التصرف عند امتلاء الـ Buffer):
   - **`BufferOverflow.SUSPEND` (الافتراضي):** الـ Producer يتعلق في دالة `emit()` وينتظر حتى يفرغ المستمع مساحة في الـ Buffer.
   - **`BufferOverflow.DROP_OLDEST`:** يسقط أقدم عنصر في الـ Buffer لتوفير مساحة للعنصر الجديد بدون تعليق الـ Producer.
   - **`BufferOverflow.DROP_LATEST`:** يسقط العنصر الجديد الحالي ويحافظ على العناصر القديمة بدون تعليق.

## Practical walkthrough

تصميم SharedFlow للأحداث وسجل الإشعارات:
```kotlin
class NotificationCenter {
    // نحتفظ بآخر 3 إشعارات للمشتركين الجدد، مع سعة إضافية 10، وإسقاط الأقدم عند الامتلاء:
    val notifications = MutableSharedFlow<Notification>(
        replay = 3,
        extraBufferCapacity = 10,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )
    
    fun postNotification(notification: Notification) {
        // بفضل DROP_OLDEST، دالة tryEmit تنجح دائماً بدون الحاجة لكوروتين suspend:
        notifications.tryEmit(notification)
    }
}
```

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

replay sets how many past items are replayed to new subscribers; extraBufferCapacity adds buffer headroom beyond replay; and onBufferOverflow decides what happens when the buffer fills up: SUSPEND pauses the emitter, DROP_OLDEST evicts the oldest item, and DROP_LATEST drops the incoming item.

## Interview answer — structured

Configuring MutableSharedFlow requires balancing memory consumption against backpressure and subscriber guarantees.

Replay controls historical catch-up for newly attached observers. Setting replay = 1 mirrors StateFlow behavior, whereas replay = 0 ensures subscribers receive strictly future emissions, preventing stale event replays.

In production, extraBufferCapacity decouples producer velocity from consumer processing latency. When background tasks produce bursts of events, this extra cushion prevents immediate emitter suspension, smoothing out processing spikes.

OnBufferOverflow governs the saturation policy when total buffer capacity is exceeded. Using BufferOverflow.SUSPEND ensures zero data loss for transactional workloads like audit logs. In contrast, BufferOverflow.DROP_OLDEST is mandatory when using tryEmit from non-suspending contexts, guaranteeing that freshest sensor updates override stale pending data without blocking threads.


## Interview answer — deep senior

Under the hood in SharedFlow.kt, emissions are managed across an internal circular buffer array whose capacity equals replay + extraBufferCapacity. Each active subscriber is tracked via a SharedFlowSlot holding an index pointer into this circular array.
When an emitter invokes emit(value), the implementation checks whether any active subscriber is lagging behind. If the distance between the newest element index and a lagging subscriber's index exceeds the allocated total buffer capacity, a buffer overflow condition occurs.
If onBufferOverflow is configured as SUSPEND, the emitter creates a CancellableContinuation and enters a suspended state, enqueueing itself until the lagging subscriber advances its index pointer and frees buffer space. However, if onBufferOverflow is configured as DROP_OLDEST, the buffer simply advances the head pointer, dropping the oldest element and immediately resuming without suspending. This enables tryEmit(value) to succeed synchronously without suspending the caller. Conversely, DROP_LATEST drops the incoming item, leaving the buffer unaltered.
A critical architectural pitfall occurs when configuring replay = 0, extraBufferCapacity = 0, and default SUSPEND. Under this configuration, tryEmit always returns false if there are no active subscribers, dropping the event completely.
Staff engineers enforce clear rules: high-frequency real-time telemetry uses DROP_OLDEST to ensure tryEmit never blocks, while critical business commands use extraBufferCapacity with SUSPEND to guarantee lossless delivery.

## How to answer in the interview

- **Why:** replay and buffer serve different audiences.
- **How:** simulate absent and slow subscribers.
- **Trade-off:** suspension versus drops and memory.
- **Failure case:** relying on extraBufferCapacity as an offline queue.
- **Production solution:** test delivery gaps and persist important commands.

## Deep-dive talking points

Walk through no subscriber, slow subscriber and new subscriber timelines.

## Follow-up questions

- **Interviewer:** "Why does `tryEmit` fail on a default `MutableSharedFlow()`?"
  **Answer:** "Because a default `MutableSharedFlow()` has `replay = 0`, `extraBufferCapacity = 0`, and `onBufferOverflow = SUSPEND`. Without any buffer capacity, an emission can only be accepted if all subscribers are actively suspended in `collect`. If any subscriber is not immediately ready, `tryEmit()` returns false."

- **Interviewer:** "How does `StateFlow` configure these three parameters internally?"
  **Answer:** "`StateFlow` is conceptually configured with `replay = 1`, `extraBufferCapacity = 0`, and `onBufferOverflow = BufferOverflow.DROP_OLDEST`, plus state deduplication via `equals()`."

- **Interviewer:** "Can the replay cache be cleared dynamically?"
  **Answer:** "Yes. `MutableSharedFlow.resetReplayCache()` clears all currently stored values from the replay buffer, ensuring future collectors start with an empty cache."

## Self-check rubric

Can I predict values under each subscriber condition and distinguish buffer success from acknowledgement?

## References and reviewed-on date

- [Kotlin SharedFlow API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-shared-flow/) — replay, buffer and absent-subscriber behavior.

Technically reviewed against primary documentation on 2026-10-13.
