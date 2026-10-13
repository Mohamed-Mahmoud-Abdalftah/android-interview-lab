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

Test reactive flows using Turbine's flow.test { } DSL to assert sequential emissions via awaitItem() and awaitError(). For StateFlow, account for the immediate initial state emission and distinct-until-changed behavior. For SharedFlow, establish the collection block before triggering emissions to avoid dropped events.

## Interview answer — structured

Turbine provides a lightweight, deterministic testing harness for Kotlin asynchronous streams without manual collection coroutines:

1. **Testing Cold Flows**:
   - Cold flows execute on demand upon collection. Wrapping them in `flow.test { }` triggers collection, allowing assertions item-by-item (`awaitItem()`), followed by terminal assertions (`awaitComplete()` or `awaitError()`).

2. **Testing `StateFlow`**:
   - StateFlow is a confluent hot stream with conflation and replay size 1. The first invocation of `awaitItem()` **always** yields the initial state.
   - StateFlow enforces `distinctUntilChanged` equivalence; emitting identical sequential states emits only once, which Turbine verifies.

3. **Testing `SharedFlow`**:
   - SharedFlow does not retain past emissions unless configured with `replay > 0`. Because emissions before active collection are dropped, the test must enter the `sharedFlow.test { }` block **before** invoking the ViewModel method that emits the event.

4. **Asserting Absence of Events**:
   - `expectNoEvents()` ensures no unhandled or duplicate events are currently queued, guaranteeing stream purity.

## Interview answer — deep senior

From an advanced concurrency testing perspective, Turbine solves timing races with SharedFlow and WhileSubscribed streams:

1. **SharingStarted.WhileSubscribed(5000)**: In production ViewModels, flows are converted to state via `.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), Initial)`. Direct value reads (`uiState.value`) outside a collector return the initial state forever because upstream is cold. Turbine's `test { }` starts a real subscriber, advancing upstream collection deterministically.

2. **Turbine Timeouts & Cancellation**: Turbine enforces an internal timeout (default 1 second). If a flow fails to emit, Turbine fails fast with a descriptive `TimeoutCancellationException` rather than hanging the entire CI test suite.

3. **Cancel and Ignore Remaining Events**: When testing infinite flows (e.g. database change observers), use `cancelAndIgnoreRemainingEvents()` at the end of the test block to cleanly unsubscribe and cancel the underlying coroutine collector.

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
