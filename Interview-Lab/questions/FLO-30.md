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

ما هي الضمانات الحقيقية التي يقدمها `replay` و `buffering` في `SharedFlow` عند عدم وجود أي مستمع نشط (No active subscribers)؟

1. سلوك الـ `replay` عند عدم وجود مستمعين:
   - الـ `replay` **مضمون 100% ويتم حفظه في الذاكرة (Guaranteed in memory)**.
   - إذا كان `replay = 2` وتم إصدار 5 عناصر في غياب أي مستمع، سيحتفظ الـ SharedFlow بآخر عنصرين في ذاكرة التخزين المؤقت.
   - عندما يأتي أول مستمع مستقبلاً، سيستلم هذين العنصرين فوراً!

2. سلوك الـ `extraBufferCapacity` عند عدم وجود مستمعين:
   - **تحذير حرج جداً (The Critical Caveat):** الـ `extraBufferCapacity` **لا يعمل إطلاقاً في غياب المستمعين!**
   - الـ Buffer الإضافي مخصص فقط لتخفيف الضغط بين Producer سريع ومستمعين بطيئين متصلين حالياً. إذا كان عدد المستمعين **صفراً**، العناصر الزائدة عن `replay` **يتم إسقاطها فوراً وتضيع للأبد**، حتى لو كانت سعة الـ extra buffer = 1000!

3. النتيجة الإنتاجية:
   - لو أردت ضمان وصول أحداث لمستمعين قد يشتركون لاحقاً، يجب زيادة قيمة `replay` أو استخدام `Channel` بدلاً من SharedFlow.

## Practical walkthrough

إثبات عملي لسلوك الذاكرة في SharedFlow:
```kotlin
val sharedFlow = MutableSharedFlow<Int>(
    replay = 1,
    extraBufferCapacity = 10 // سعة إضافية 10
)

// لا يوجد أي مستمع حالياً (subscribers = 0):
sharedFlow.tryEmit(100)
sharedFlow.tryEmit(200)
sharedFlow.tryEmit(300)

// الآن يشترك أول مستمع:
sharedFlow.test { // باستخدام Turbine
    // سيستلم 300 فقط! (عنصر واحد فقط من replay = 1)
    assertEquals(300, awaitItem())
    // العناصر 100 و 200 ضاعت للأبد ولم يتم حفظها في extraBufferCapacity!
}
```

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

replay is guaranteed to retain up to N latest items in memory for future subscribers even when subscriber count is 0; however, extraBufferCapacity only buffers for active subscribers. With 0 subscribers, emissions exceeding the replay capacity are dropped immediately and cannot be queued in extra buffer space.

## Interview answer — structured

This is one of the most critical and frequently misunderstood memory guarantees in Kotlin Coroutines:

1. **`replay` guarantees retention:** The replay cache is permanent and memory-resident. If `replay = 2`, `SharedFlow` retains the last 2 emitted items in memory indefinitely, even if there are zero active subscribers. When a new collector subscribes in the future, it is guaranteed to receive those 2 replayed items immediately.

2. **`extraBufferCapacity` provides ZERO retention with 0 subscribers:** A common misconception is that an extra buffer of 10 will hold 10 items while waiting for subscribers. It does not. The extra buffer capacity exists solely to absorb backpressure for *active, currently connected* slow subscribers. If `subscriptionCount == 0`, emissions beyond the `replay` count are dropped immediately and permanently, regardless of how large `extraBufferCapacity` is configured.

If your architecture requires guaranteed delivery of queued events to future subscribers, you must use a buffered **Channel** (`Channel(Channel.BUFFERED)`), not a SharedFlow.

## Interview answer — deep senior

Under the hood, in `SharedFlowImpl`, the internal buffer consists of a `head` and `tail` pointer array representing replay slots and extra buffer slots. When `emit()` or `tryEmit()` is called, the implementation checks `if (nSubscribers == 0)`. If true, the code path strictly executes `updateReplayCache(value)` and returns immediately. It completely skips queuing items into the extra buffer indices.

This behavior is by design: `SharedFlow` models broadcast pub-sub, not a persistent task queue. If a SharedFlow preserved unconsumed items without subscribers, a ViewModel that emits analytics or telemetry while unobserved would grow memory without bound until a subscriber attached. For guaranteed queueing semantics across lifecycles, `Channel.send()` is the appropriate concurrency primitive.

## How to answer in the interview

- **Why:** no-subscriber semantics are easy to misread.
- **How:** distinguish replay cache from extra buffer.
- **Trade-off:** replay recovery versus duplicate action.
- **Failure case:** tryEmit success mistaken for handling.
- **Production solution:** no-subscriber tests and durable commands when required.

## Deep-dive talking points

Trace tryEmit, replay cache, active lag and process death separately.

## Follow-up questions

- **Interviewer:** "What happens if you call `emit()` with 0 subscribers and `onBufferOverflow = SUSPEND`?"
  **Answer:** "With 0 subscribers, `emit()` will NOT suspend. It updates the replay cache and returns immediately, dropping any non-replayed items."

- **Interviewer:** "Can a `SharedFlow` with `replay = 0` ever deliver an event to a subscriber that connects 1 millisecond after emission?"
  **Answer:** "No, never. With `replay = 0`, the emission is dropped the instant it occurs if there are no active collectors at that exact moment."

- **Interviewer:** "How does `StateFlow` behave with 0 subscribers?"
  **Answer:** "StateFlow is a SharedFlow with `replay = 1`. With 0 subscribers, it updates its `.value` slot. When a subscriber connects later, it receives that updated value immediately."

## Self-check rubric

Can I predict replay zero/one while absent and explain why success is not acknowledgement?

## References and reviewed-on date

- [Kotlin SharedFlow API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-shared-flow/) — absent-subscriber rules.

Technically reviewed against primary documentation on 2026-10-13.
