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

## Concept and technical explanation

Behavioral patterns govern dynamic algorithmic execution, responsibility distribution, and messaging protocols between collaborating objects, decoupling the invocation of an operation from its concrete execution. Observer establishes a one-to-many subscription model where state changes in a subject automatically notify registered observers reactively. Strategy encapsulates a family of interchangeable algorithms behind a common contract, allowing the algorithm to vary independently from consuming clients. State allows an object to alter its behavioral logic dynamically as its internal state changes, modeling state transitions cleanly without fragile conditional branching. Command encapsulates a request as a standalone object, enabling request parameterization, queueing, and undoable transactions. Chain of Responsibility decouples the sender of a request from its potential receivers by passing the request along a sequential handler pipeline until handled.

## Practical walkthrough (English)

Behavioral Pattern implementations across Android and Kotlin:
```kotlin
// 1. OBSERVER: Reactive emission via Flow
class CounterSubject {
    private val _count = MutableStateFlow(0)
    val count: StateFlow<Int> = _count.asStateFlow()
    fun increment() { _count.value += 1 }
}

// 2. STRATEGY: Interchangeable validation algorithms
interface ValidationStrategy { fun isValid(input: String): Boolean }
class EmailValidationStrategy : ValidationStrategy {
    override fun isValid(input: String) = android.util.Patterns.EMAIL_ADDRESS.matcher(input).matches()
}

// 3. STATE PATTERN: Clean state transition machine
sealed interface DownloadState {
    fun handlePause(context: DownloadContext)
}
object Downloading : DownloadState {
    override fun handlePause(context: DownloadContext) { context.state = Paused }
}
object Paused : DownloadState {
    override fun handlePause(context: DownloadContext) { /* Already paused */ }
}
class DownloadContext { var state: DownloadState = Downloading }

// 4. COMMAND: Encapsulated undoable user action
interface EditorCommand { fun execute(); fun undo() }
class InsertTextCommand(private val doc: Document, private val text: String) : EditorCommand {
    override fun execute() = doc.append(text)
    override fun undo() = doc.deleteLast(text.length)
}

// 5. CHAIN OF RESPONSIBILITY: Pipeline processing (OkHttp Interceptor model)
interface Interceptor {
    fun intercept(chain: Chain): Response
    interface Chain { fun proceed(request: Request): Response }
}
```

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

Observer notifies multiple subscribers reactively when subject state changes. Strategy encapsulates swappable algorithms behind a common interface. State dynamically alters an object's behavior based on internal state transitions. Command encapsulates a request as an object to support queuing, logging, and undo operations. Chain of Responsibility passes a request along a pipeline of sequential handlers until processed. Each behavioral pattern decouples execution mechanics from invoking components.

## Interview answer — structured

Behavioral patterns provide decoupled mechanisms for managing communication, state coordination, and algorithmic execution across application components.
The Observer pattern establishes a subscription model where state-holders notify dependents automatically when changes occur. In Android, Kotlin StateFlow, SharedFlow, and LiveData are canonical implementations, enabling reactive UI updates that respond to data stream emissions without tight coupling between presentation and domain layers.
The Strategy pattern defines a family of interchangeable algorithms, encapsulating each behind a shared interface. Consumers hold a reference to the strategy contract, allowing algorithmic policies such as sorting, caching, or discount calculations to be swapped dynamically at runtime or substituted during testing.
The State pattern allows an object to alter its behavior when its internal state changes. Instead of scattering complex, error-prone when or if-else ladders across methods, state-specific behavior is encapsulated inside dedicated state objects that manage their own transitions.
The Command pattern turns a request into a standalone object encapsulating the action, receiver, and execution parameters. This facilitates transactional queueing, offline action synchronization, and reversible operations like undo and redo.
The Chain of Responsibility pattern passes a request sequentially through a pipeline of handlers. Each handler inspects the request and chooses whether to process it, short-circuit execution, or pass it to the next link in the chain, as seen in OkHttp network interceptors and Android touch event dispatching.

## Interview answer — deep senior

Under the hood, behavioral patterns manage runtime message dispatch and decoupling, directly impacting call stack execution, thread safety, and memory retention.
In modern Android architecture, language evolutions in Kotlin have streamlined these classic patterns. The Observer pattern has evolved from error-prone callback interfaces with manual unsubscription to structured, lifecycle-aware Kotlin Coroutine Flows that automatically cancel upon coroutine scope teardown, completely eliminating listener memory leaks.
The Strategy pattern, which traditionally required creating dozens of boilerplate Java classes, is frequently replaced in Kotlin by first-class functions and lambdas (typealias DiscountStrategy = (Double) -> Double), maintaining clean decoupling with zero class overhead.
The State pattern has converged with modern Unidirectional Data Flow (UDF) paradigms. Rather than mutating state internally inside state objects, senior engineers leverage Kotlin sealed interfaces to model immutable state hierarchies emitted across StateFlow pipelines. ViewModels process user intents through pure functional reducers, achieving deterministic state transitions that are trivial to verify in unit tests.
Chain of Responsibility remains the premier architecture for pipeline processing. In OkHttp's RealInterceptorChain, handlers wrap each other recursively, allowing cross-cutting concerns like caching, authentication retry, and gzip compression to execute transparently before socket I/O.
Staff engineers leverage these behavioral patterns to maintain clean boundaries between event triggers and execution pipelines, ensuring high maintainability and testability.

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
