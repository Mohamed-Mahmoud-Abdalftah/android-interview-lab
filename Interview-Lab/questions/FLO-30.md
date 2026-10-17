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

## Concept and technical explanation

Understanding delivery guarantees and message persistence in MutableSharedFlow when zero active subscribers exist requires examining the interplay between replay cache, extraBufferCapacity, and buffer overflow policies.
SharedFlow is fundamentally a hot broadcast stream. Unlike cold Flows, which defer execution until a collector invokes collect, a hot SharedFlow executes and processes emissions independently of subscriber presence.
When an event is emitted into a MutableSharedFlow with zero active collectors: if the replay parameter is greater than zero (replay > 0), the emission is stored in the replay cache array up to the replay capacity and is instantly delivered to future subscribers upon attachment; if replay is zero (replay = 0), the emission bypasses subscriber dispatch. In this case, whether extraBufferCapacity can retain the event depends strictly on whether downstream collectors previously existed or buffer overflow rules apply; however, for new future subscribers, elements outside the replay cache are completely invisible and dropped permanently into the void.

## Practical walkthrough (English)

Demonstrating SharedFlow emission behavior and delivery guarantees with zero subscribers:
```kotlin
class SharedFlowGuaranteesDemo {
    // Scenario 1: Zero subscribers with default configuration
    // replay = 0, extraBufferCapacity = 0, onBufferOverflow = SUSPEND
    val defaultSharedFlow = MutableSharedFlow<String>()

    // Scenario 2: Replay cache configured
    // Retains last 2 emissions for ANY future subscriber
    val replaySharedFlow = MutableSharedFlow<String>(
        replay = 2,
        extraBufferCapacity = 0
    )

    suspend fun demonstrate() {
        // With 0 active subscribers:
        defaultSharedFlow.emit("Event 1") // Emitted, but NOT retained! Dropped!
        val tryEmitSuccess = defaultSharedFlow.tryEmit("Event 2") // Returns false!

        replaySharedFlow.emit("Replayed 1")
        replaySharedFlow.emit("Replayed 2")
        // Both saved in replay cache!

        // When a new subscriber attaches 5 seconds later:
        // defaultSharedFlow -> Receives NOTHING.
        // replaySharedFlow  -> Immediately receives "Replayed 1" and "Replayed 2".
    }
}
```

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

With zero active subscribers, only the replay cache guarantees retention for future collectors. If replay is zero, emitted events are permanently dropped for future subscribers regardless of extra buffer capacity, and synchronous tryEmit on default SharedFlow fails and returns false immediately.

## Interview answer — structured

SharedFlow is a hot broadcast stream that does not wait for collectors to start emitting.

Buffer guarantees differ drastically between replay cache and extraBufferCapacity when subscribers equal zero. The replay cache exists specifically to hold historical items for future subscribers. If replay = 1, the newest emitted item is guaranteed to be stored and delivered to subsequent subscribers.

In production, extraBufferCapacity is designed solely to cushion active, lagging subscribers. If replay = 0 and subscriber count is zero, extraBufferCapacity does not retain items for future observers; any emission without replay vanishes permanently into the void.
As for non-suspending emission, calling tryEmit on a default MutableSharedFlow with zero subscribers and zero buffer capacity fails immediately, returning false. To guarantee one-off delivery without subscribers, developers must utilize buffered Channels instead of SharedFlow.


## Interview answer — deep senior

Under the hood in SharedFlow.kt, emissions are tracked across an internal circular buffer array whose allocation size equals replay + extraBufferCapacity. Each active subscriber is tracked via a SharedFlowSlot. The runtime property nCollectors tracks active subscribers atomically.
When emit(value) is called, the implementation checks nCollectors. If nCollectors == 0, the method inspects replay. If replay > 0, the element is placed into the head of the replay buffer, updating the replay index. Any future subscriber that attaches will initialize its slot index to head minus replay, immediately reading the cached items upon subscription.
However, if replay == 0 and nCollectors == 0, the emitted item has nowhere to go. Because extraBufferCapacity is designed strictly to buffer elements between active subscribers and slow emitters, it is not an offline persistent queue. The emission evaluates as complete and is discarded from memory.
This creates a lethal production trap with tryEmit(). If a developer instantiates MutableSharedFlow() with default arguments (replay = 0, extraBufferCapacity = 0, SUSPEND), calling tryEmit() with zero active collectors returns false because the buffer cannot accept the item without suspending.
Staff engineers enforce clear architectural rules: never use SharedFlow with replay = 0 for one-off transactional events that must survive periods of subscriber absence; use buffered Channels for guaranteed single-consumer delivery.

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
