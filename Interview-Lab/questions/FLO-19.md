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

replay sets how many historical items are cached and re-emitted to new subscribers; extraBufferCapacity adds buffer space beyond replay to absorb bursts; and onBufferOverflow dictates behavior when the buffer fills: SUSPEND (pauses emitter), DROP_OLDEST (drops oldest item), or DROP_LATEST (drops new item).

## Interview answer — structured

These three parameters configure the buffer mechanics and backpressure semantics of `MutableSharedFlow`:

**`replay`** defines the size of the replay cache. When a new collector subscribes, it immediately receives up to `replay` cached historical emissions. If set to 0, late subscribers receive nothing from the past. `StateFlow` is conceptually a SharedFlow with `replay = 1`.

**`extraBufferCapacity`** provides additional queue capacity beyond the replay cache. The total buffer size is `replay + extraBufferCapacity`. It allows fast producers to continue emitting without suspension when downstream collectors are busy.

**`onBufferOverflow`** configures backpressure behavior when the combined buffer is full. `BufferOverflow.SUSPEND` suspends `emit()` until downstream collectors catch up. `BufferOverflow.DROP_OLDEST` evicts the oldest buffered element to make room for the new one, enabling non-suspending `tryEmit()` to always succeed. `BufferOverflow.DROP_LATEST` discards the incoming item, preserving the existing buffer.

## Interview answer — deep senior

At the internal implementation level, `SharedFlowImpl` allocates a continuous array of slots representing the buffer. A critical engineering requirement involves `tryEmit()`. `tryEmit()` is a non-suspending method to post events. If `onBufferOverflow` is set to `BufferOverflow.SUSPEND` (the default) and there are slow collectors or the buffer is saturated, **`tryEmit()` will return `false` and drop the event silently**!

Therefore, in Android architecture, if you intend to dispatch events from synchronous callbacks using `tryEmit()` (such as view click listeners without launching a coroutine), you must configure `extraBufferCapacity >= 1` and `onBufferOverflow = BufferOverflow.DROP_OLDEST`. This guarantees that `tryEmit()` never fails and never drops events unexpectedly.

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
