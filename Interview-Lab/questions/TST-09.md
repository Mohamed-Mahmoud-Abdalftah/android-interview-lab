---
id: "TST-09"
question: "How do you test Flow, StateFlow, and SharedFlow with Turbine?"
topic: "Testing, Quality & Reliability"
code: "TST"
group: "B"
phase: 4
priority: "P1"
order: 404
editorial_status: "reviewed"
---

# TST-09

## Original interview question

How do you test Flow, StateFlow, and SharedFlow with Turbine?

## What the interviewer evaluates

- Hot-flow subscription timing and replay/conflation semantics.
- Turbine assertions with deterministic scheduling.

## Concept and technical explanation

Testing Kotlin asynchronous reactive streams—cold Flow, StateFlow, and SharedFlow—requires tailored testing strategies driven by stream lifecycle and subscription semantics. Cold flows instantiate builders and execute emission pipelines on-demand whenever collected, allowing deterministic sequential assertions terminating in completion. StateFlow is a hot, conflated stream with replay of one that never completes naturally; it always holds an active initial value and skips rapid intermediate state mutations if new values arrive before the consumer reads the slot. SharedFlow is a configurable broadcast stream where emissions occurring prior to collector initialization are permanently dropped unless explicitly buffered via replay. CashApp's Turbine library provides a testing harness that connects a rendezvous channel to the stream, exposing synchronous assertion primitives like awaitItem(), expectNoEvents(), awaitComplete(), and awaitError().

## Practical walkthrough (English)

Testing cold Flows, StateFlow, and SharedFlow sequentially using Turbine:
```kotlin
class StreamTestingDemo {
    // 1. Cold Flow: Starts on collection and finishes with completion
    @Test
    fun coldFlow_emitsSequence_andCompletes() = runTest {
        val coldFlow = flow {
            emit("First")
            emit("Second")
        }

        coldFlow.test {
            assertEquals("First", awaitItem())
            assertEquals("Second", awaitItem())
            awaitComplete()
        }
    }

    // 2. StateFlow: Always yields initial state; never completes naturally
    @Test
    fun stateFlow_emitsInitialState_andUpdates() = runTest {
        val stateFlow = MutableStateFlow("Initial")

        stateFlow.test {
            assertEquals("Initial", awaitItem()) // Guaranteed initial value

            stateFlow.value = "Updated"
            assertEquals("Updated", awaitItem())

            cancelAndIgnoreRemainingEvents() // Must cancel hot infinite collector!
        }
    }

    // 3. SharedFlow: Subscription must be established BEFORE emitting!
    @Test
    fun sharedFlow_collectsEvents_whenSubscribedPriorToEmission() = runTest {
        val sharedFlow = MutableSharedFlow<String>()

        sharedFlow.test {
            // Collector is now active! Emit event:
            sharedFlow.emit("Alert")
            assertEquals("Alert", awaitItem())

            expectNoEvents()
            cancelAndIgnoreRemainingEvents()
        }
    }
}
```

## Explanation in Arabic

كيف تختبر الـ Flow، والـ StateFlow، والـ SharedFlow باحترافية باستخدام مكتبة Turbine؟

1. ما هي مكتبة Turbine ولماذا نحتاجها؟
   - في الكوتلن، الـ Flows عبارة عن تدفقات غير متزامنة (Asynchronous Streams). إذا حاولت اختبارها بجمع البيانات يدوياً في قائمة، قد تتجمد الاختبارات أو تحدث Race Conditions.
   - **Turbine** هي المكتبة الرسمية الموصى بها من CashApp/Square لاختبار الـ Flows بطريقة تسلسلية وحتمية: `flow.test { ... }`.

2. الفروق الجوهرية عند اختبار أنواع الـ Flows المختلفة:
   - **اختبار Cold Flow**: يبدأ في إصدار البيانات فقط عند استدعاء `test { }`. نستقبل العناصر عنصراً بعنصر عبر `awaitItem()`.
   - **اختبار `StateFlow` (Hot Stream)**: يملك قيمة أولية دائماً! أول استدعاء لـ `awaitItem()` سيعيد **القيمة الابتدائية (Initial State)**. كما أنه يطبق خاصية `distinctUntilChanged` تلقائياً؛ إذا أصدرت نفس القيمة مرتين فلن تظهر في الـ Flow.
   - **اختبار `SharedFlow` (Hot Event Stream)**: لا يحتفظ بالبيانات السابقة افتراضياً (إلا إذا كان له `replay > 0`). يجب بدء الاستماع له عبر `test { }` **قبل** استدعاء الدالة التي تصدر الحدث في كود الـ ViewModel، وإلا ستضيع الانبعاثات!

3. دوال Turbine الأساسية:
   - `awaitItem()`: ينتظر وصول العنصر التالي.
   - `awaitComplete()`: ينتظر اكتمال الـ Flow بنجاح.
   - `awaitError()`: ينتظر ويرجع الاستثناء إذا فشل الـ Flow.
   - `expectNoEvents()`: يتأكد من عدم حدوث أي انبعاثات جديدة.

## Practical walkthrough

اختبار StateFlow و SharedFlow باستخدام Turbine ومحاكاة انبعاثات الـ ViewModel:
```kotlin
class NotificationViewModel : ViewModel() {
    // StateFlow للحالة المستمرة
    private val _uiState = MutableStateFlow<String>("Initial")
    val uiState: StateFlow<String> = _uiState.asStateFlow()

    // SharedFlow للأحداث الفردية السريعة (One-off snackbar events)
    private val _events = MutableSharedFlow<String>()
    val events: SharedFlow<String> = _events.asSharedFlow()

    fun updateState(newValue: String) {
        _uiState.value = newValue
    }

    fun triggerAlert(message: String) {
        viewModelScope.launch {
            _events.emit(message)
        }
    }
}

class FlowTurbineTest {
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    @Test
    fun `test StateFlow emissions with Turbine`() = runTest {
        val viewModel = NotificationViewModel()

        viewModel.uiState.test {
            // 1. أول عنصر دائماً هو القيمة الابتدائية للـ StateFlow:
            assertEquals("Initial", awaitItem())

            viewModel.updateState("Updated")
            assertEquals("Updated", awaitItem())

            expectNoEvents()
        }
    }

    @Test
    fun `test SharedFlow requires collecting before emitting`() = runTest {
        val viewModel = NotificationViewModel()

        viewModel.events.test {
            // 2. يجب بدء الـ test block أولاً، ثم استدعاء دالة الإرسال:
            viewModel.triggerAlert("Error occurred")
            mainDispatcherRule.testDispatcher.scheduler.runCurrent()

            assertEquals("Error occurred", awaitItem())
            expectNoEvents()
        }
    }
}
```

## Why it matters and how it works

Turbine collects a Flow in a test scope. StateFlow may suppress equal updates and conflate fast changes, so a test must not demand every intermediate value unless scheduling ensures collection. SharedFlow with replay zero does not deliver past emissions to a late collector.

## Worked example

This small JVM test makes subscription and equality behavior explicit. It assumes JUnit 5, Turbine, and `kotlinx-coroutines-test` are test dependencies. The `test` block starts collecting before its assertions run; this matters for the replay-zero event.

```kotlin
import app.cash.turbine.test
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.flowOf
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

class FlowContractTest {
    @Test fun coldAndHotFlows() = runTest {
        flowOf("one", "two").test {
            assertEquals("one", awaitItem())
            assertEquals("two", awaitItem())
            awaitComplete()
        }

        val state = MutableStateFlow("Idle")
        state.test {
            assertEquals("Idle", awaitItem())
            state.value = "Loading"
            assertEquals("Loading", awaitItem())
            state.value = "Loading" // Equal value: no new StateFlow emission.
            expectNoEvents()
        }

        val events = MutableSharedFlow<String>(replay = 0)
        events.test {
            events.emit("Saved")
            assertEquals("Saved", awaitItem())
        }
    }
}
```

For a ViewModel Loading → Success test, keep the fake repository suspended until Loading is observed. A rapid pair of StateFlow writes may conflate, so do not assume this example proves every intermediate ViewModel state will always be delivered.

## Trade-offs and decision criteria

Turbine makes asynchronous assertions readable, but careless `advanceUntilIdle` can collapse intermediate StateFlow states. For one-shot UI events, design delivery and lifecycle explicitly rather than assuming SharedFlow is lossless.

## Failure modes

Emitting to SharedFlow before the test collector starts causes a missed event and apparent flake. Use subscription awareness or replay only if product semantics require it. Do not use replay solely to make the test pass if duplicate delivery is wrong.

## Production perspective

Test collector start, configuration recreation, lifecycle stop/start, equal-value updates and buffer overflow. Use stable fake sources and virtual time; integration UI tests verify actual collection behavior.

## Interview answer — short

We test reactive streams using Turbine by opening a test collector channel. Cold flows emit on collection and terminate with awaitComplete. StateFlow is hot and conflated, so its initial value is received immediately via awaitItem, requiring cancelAndIgnoreRemainingEvents to avoid hanging. SharedFlow drops unbuffered emissions, so the Turbine test block must be opened before emitting events. Turbine catches unhandled stream exceptions and prevents test deadlocks synchronously.

## Interview answer — structured

Testing asynchronous Kotlin flows reliably requires navigating the profound behavioral differences between cold and hot streams.
Standard collection approaches—such as calling toList() on a stream—frequently cause infinite test hangs because StateFlow and SharedFlow are hot streams that never complete.
CashApp's Turbine library solves this by providing a lightweight, structured testing scope.
When testing cold flows, Turbine initiates collection upon entering the test block.
Because cold flows follow structured completion, the test asserts items sequentially using awaitItem() and terminates with awaitComplete().
When testing StateFlow, developers must account for its hot, conflated nature.
Entering the test block immediately yields StateFlow's current value as the first item.
Subsequent state updates emitted by ViewModels are asserted sequentially, but because StateFlow never completes, the test block must conclude with cancelAndIgnoreRemainingEvents() to unregister the observer cleanly.
When testing SharedFlow, timing is paramount.
Because SharedFlow drops emissions when there are zero active subscribers unless replay is configured, the Turbine test block must be launched prior to calling emit().
Turbine provides expectNoEvents() to verify that quiescent streams do not leak phantom updates.

## Interview answer — deep senior

Under the hood, Turbine connects to Kotlin Coroutines by establishing a bridge between the Flow collector pipeline and an internal Channel.
When flow.test { ... } is invoked, Turbine launches an asynchronous consumer coroutine that invokes collect on the target Flow, routing every incoming value into an unbuffered rendezvous Channel.
When the test author invokes awaitItem(), Turbine suspends the test thread until the consumer coroutine offers an element into the channel, popping the value in O(1) time without thread sleeps.
If an unexpected exception is thrown inside the flow builder, Turbine catches the failure, surfaces it via awaitError(), and halts execution with a detailed failure diff.
Understanding stream mechanics separates junior tests from senior harnesses.
With StateFlow, rapid successive emissions can be conflated by the runtime; if the ViewModel executes _state.value = A followed immediately by _state.value = B within the same execution frame, StateFlow overwrites its internal state slot, and Turbine will only observe state B unless intermediate suspensions occur.
With SharedFlow, the buffer overflow policy dictates behavior.
If extraBufferCapacity is zero and BufferOverflow.SUSPEND is active, calling emit() from outside a coroutine can suspend indefinitely if no collector exists.
Turbine eliminates these hazards by ensuring the collector's Job is child-linked to the test's CoroutineScope, guaranteeing that canceling the test harness synchronously disposes of all underlying hot stream subscriptions without leaking coroutines on CI workers.

## How to answer in the interview

- **Why:** cold and hot flows deliver events under different timing rules.
- **How:** demonstrate Turbine assertions for cold completion, StateFlow current/equality and SharedFlow subscription.
- **Trade-off:** replay helps late collectors but can duplicate one-shot actions.
- **Failure case:** emission before replay-zero subscription is lost.
- **Production solution:** test Flow policy on JVM and lifecycle collection on device.

## Deep-dive talking points

Prompt for cold/hot collection, StateFlow equality, SharedFlow replay and collector startup.

## Follow-up questions

- **Interviewer:** "Why does StateFlow ignore duplicate identical values during testing?"
  **Answer:** "StateFlow internally implements Any.equals() equality checks on new values and suppresses emissions if the new value matches the current value."

- **Interviewer:** "What is the purpose of cancelAndIgnoreRemainingEvents() in Turbine?"
  **Answer:** "It unregisters the collector and halts the stream without failing the test if additional emissions remain pending in an infinite flow."

## Self-check rubric

Assert a cold Flow starts at collection, StateFlow exposes its current value and suppresses equal updates, and replay-zero SharedFlow requires an active collector. Use Turbine to consume or cancel all events and explain one lifecycle gap.

## References and reviewed-on date

- [Kotlin StateFlow/SharedFlow](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-state-flow/) — StateFlow semantics.
- [Turbine README](https://github.com/cashapp/turbine) — testing API.

Technically reviewed against primary documentation on 2026-10-13.
