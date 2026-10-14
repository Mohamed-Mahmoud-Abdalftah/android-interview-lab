---
id: "PAT-05"
question: "Explain Observer, Strategy, State, Command, and Chain of Responsibility."
topic: "Design Patterns"
code: "PAT"
group: "A"
phase: 2
priority: "P1"
order: 196
editorial_status: "reviewed"
---

# PAT-05

## Original interview question

Explain Observer, Strategy, State, Command, and Chain of Responsibility.

## What the interviewer evaluates

Contrast notification, interchangeable algorithm, state-dependent behavior, action object and handler pipeline.

## Explanation in Arabic

شرح الأنماط السلوكية الأساسية: Observer و Strategy و State و Command و Chain of Responsibility في Android:

1. نمط المراقب (Observer Pattern):
   - **الهدف**: علاقة One-to-Many؛ عندما يتغير كائن (Subject)، يتم إشعار جميع المراقبين (Observers) المسجلين تلقائياً.
   - **في Android**: قلب البرمجة التفاعلية (`StateFlow`, `SharedFlow`, `LiveData`, و `SnapshotState` في Compose).

2. نمط الاستراتيجية (Strategy Pattern):
   - **الهدف**: تغليف مجموعة من الخوارزميات المتبادلة في كلاسات منفصلة، واختيار الخوارزمية في وقت التشغيل.
   - **في Android**: اختيار طريقة الدفع (Stripe vs PayPal)، أو اختيار طريقة ترتيب القائمة (حسب السعر vs التاريخ).

3. نمط الحالة (State Pattern):
   - **الهدف**: السماح لكائن بتغيير سلوكه بالكامل عندما تتغير حالته الداخلية (كأنه يغير كلاسه).
   - **في Android**: آلة حالات مشغل الوسائط (`IdleState`, `BufferingState`, `PlayingState`, `PausedState`)؛ ضغط زر التشغيل في `PlayingState` يوقف المشغل، بينما ضغطه في `PausedState` يستأنف التشغيل.

4. نمط الأمر (Command Pattern):
   - **الهدف**: تغليف الطلب بالكامل في كائن مستقل، مما يتيح تأجيل تنفيذه، وضعه في طابور (Queue)، أو التراجع عنه (Undo/Redo).
   - **في Android**: مهام `WorkManager` (WorkRequest) أو أحداث الـ MVI (`UiIntent`).

5. نمط سلسلة المسؤولية (Chain of Responsibility):
   - **الهدف**: تمرير الطلب عبر سلسلة من المعالجات (Handlers)؛ كل معالج يقرر معالجة الطلب أو تمريره لمن يليه.
   - **في Android**: `OkHttp Interceptors Chain`، وتمرير أحداث اللمس (Touch Event Dispatching في View Hierarchy من ViewGroup إلى View).

## Practical walkthrough

أمثلة تمثل الأنماط السلوكية الخمسة في كود Android:
```kotlin
// 1. OBSERVER: اشتراك تفاعلي في تدفق الحالة:
viewModel.uiState.onEach { render(it) }.launchIn(lifecycleScope)

// 2. STRATEGY: استراتيجية فرز قابلة للتبديل في وقت التشغيل:
val sortedList = list.sortedWith(if (sortByPrice) PriceComparator() else DateComparator())

// 3. STATE: مشغل وسائط يغير سلوكه حسب حالته الداخلية:
sealed interface PlayerState {
    fun onPlayClicked(player: MediaPlayerContext)
}
class PausedState : PlayerState {
    override fun onPlayClicked(player: MediaPlayerContext) { player.start(); player.setState(PlayingState()) }
}
class PlayingState : PlayerState {
    override fun onPlayClicked(player: MediaPlayerContext) { player.pause(); player.setState(PausedState()) }
}

// 4. COMMAND: تغليف عملية حفظ قابلة للوضع في طابور WorkManager:
val syncCommand = OneTimeWorkRequestBuilder<SyncWorker>().build()
WorkManager.getInstance(context).enqueue(syncCommand)

// 5. CHAIN OF RESPONSIBILITY: معالجة أحداث اللمس في Android:
override fun dispatchTouchEvent(ev: MotionEvent): Boolean {
    return if (onInterceptTouchEvent(ev)) onTouchEvent(ev) else child.dispatchTouchEvent(ev)
}
```

## Why it matters and how it works

Behavioral patterns organize communication and decision-making. Strategy varies policy selection; State varies behavior based on current state; Observer delivers updates; Command represents requests; a chain composes ordered handlers.

## Worked example

Example: checkout observes order Flow, chooses provider Strategy, transitions through `Pending/Confirmed` State, represents `SubmitPayment(requestId)` as a Command for durable handling, and validates request through an ordered chain of handlers. Each layer has explicit ownership and error semantics.

## Trade-offs and decision criteria

Patterns can clarify complex flows but add objects and indirection. A simple lambda may be enough for one strategy; a `when` may be enough for a small state machine. A chain can hide ordering and early-exit behavior if overused.

## Failure modes

A one-shot payment Command sits only in memory and is lost on process death; use persisted work plus server reconciliation. A Flow observer without lifecycle-aware collection can leak or do unnecessary work.

## Production perspective

A bank transfer flow uses explicit state transitions and persistent request IDs; UI observes status via a repository stream. Provider selection and validation handlers are tested independently.

## Interview answer — short

Observer handles reactive 1-to-N updates (`Flow`, Compose State). Strategy swaps interchangeable algorithms (payment methods). State alters object behavior based on its internal state machine (media player states). Command encapsulates executable requests (`WorkManager`). Chain of Responsibility passes requests through sequential handlers (`OkHttp Interceptors`, Touch Dispatch).

## Interview answer — structured

Behavioral patterns govern communication protocols, algorithms, and state transitions between decoupled objects.

First, an Observer defines a one-to-many dependency where state mutations in a subject broadcast notifications to subscribers. The foundation of modern reactive Android (`StateFlow`, `LiveData`, and Compose's `SnapshotMutationPolicy`). Next, a Strategy encapsulates a family of algorithms into interchangeable classes conforming to a common contract. Consumers delegate execution to the strategy instance injected at runtime (e.g. Routing between different payment gateways).
Additionally, with State, allows an object to alter its behavior when its internal state changes, behaving as if its underlying class transformed. Highly effective for complex state machines (e.g. `ExoPlayer` audio state transitions or Bluetooth connection sequences: `Disconnected`, `Scanning`, `Connecting`, `Connected`). A Command encapsulates a request as an object with its own execution context, enabling parameterization, queuing, scheduling, and undo/redo operations. Embodied by Jetpack `WorkManager` (`OneTimeWorkRequest`) and MVI `Intent` actions.
Finally, with Chain of Responsibility, decouples request senders from receivers by giving multiple handlers a chance to process the request sequentially along a pipeline. Embodied by **OkHttp Interceptor chains** and Android's **`dispatchTouchEvent()` hierarchy**.


## Interview answer — deep senior

Comparing **State vs Strategy** is a classic interview inquiry.

First, both share an identical UML class diagram (Context delegating to an Interface with multiple implementations). Next, *The difference is intent and state transitions*.
In **Strategy**, the client generally configures the strategy once (e.g. User chooses 'Pay with PayPal'), and strategies rarely know about other strategies. Finally, in **State**, the context changes states dynamically as events occur, and concrete state objects frequently trigger transitions to succeeding state objects (`PausedState` directly transitions context to `PlayingState`).

In modern Kotlin, the State pattern is often formalized using **Sealed Interfaces with Reducer Functions** (`MVI`), achieving mathematical state determinism.


## How to answer in the interview

- **Why:** These patterns address observation, variation, transitions, intent and handler order.
- **How:** Walk one checkout request through only the roles it actually needs.
- **Trade-off:** Prefer direct code when a chain or command queue adds no value.
- **Failure case:** Hidden handler order or replayed non-idempotent command.
- **Production solution:** Test state transitions, observer lifecycle and queued-operation identity.

## Deep-dive talking points

Compare Strategy/State, observer delivery, command persistence and chain ordering.

## Follow-up questions

- **Interviewer:** "What is the key difference between State and Strategy patterns?"
  **Answer:** "Strategy encapsulates interchangeable algorithms usually chosen once by the client. State encapsulates dynamic state machine transitions where the object actively changes its behavior and transitions to new states as events occur."

- **Interviewer:** "How does Android's Touch Event System implement Chain of Responsibility?"
  **Answer:** "A touch event starts at the Window, traverses down through nested `ViewGroup`s via `dispatchTouchEvent()` and `onInterceptTouchEvent()`, until a child view consumes it or passes it back up."

## Self-check rubric

Match five scenarios to patterns and identify one durability or lifecycle limitation.

## References and reviewed-on date

- [GoF Design Patterns, publisher](https://www.pearson.com/en-us/subject-catalog/p/design-patterns-elements-of-reusable-object-oriented-software/P200000009480/9780321700698) — behavioral patterns.
- [Android LiveData overview](https://developer.android.com/topic/libraries/architecture/livedata) — lifecycle-aware Observer example.

Technically reviewed against primary documentation on 2026-10-13.
