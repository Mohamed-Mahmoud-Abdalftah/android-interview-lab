---
id: "FLO-24"
question: "How do you test Flow/StateFlow with runTest and Turbine?"
topic: "Flow, StateFlow, SharedFlow & Channels"
code: "FLO"
group: "B"
phase: 1
priority: "P1"
order: 137
editorial_status: "reviewed"
---

# FLO-24

## Original interview question

How do you test Flow/StateFlow with runTest and Turbine?

## What the interviewer evaluates

Design deterministic runTest and Turbine assertions for emissions, cancellation and conflation.

## Explanation in Arabic

اختبار الـ Flow و StateFlow باستخدام `runTest` ومكتبة **Turbine** من CashApp هو المعيار الذهبي المعتمد عالمياً في اختبارات Kotlin:

1. المشكلة في اختبار الـ Flows بدون Turbine:
   - الـ Flow هو Asynchronous Stream. لو حاولت كتابة `flow.collect()` داخل الـ Test، الـ `collect()` دالة معلقة لا تنتهي أبداً، والاختبار سيتعلق ويتجمد!
   - ولو حاولت استخدام `toList()`، سيتعلق للأبد أيضاً لو كان الـ Flow لا نهائياً (زي StateFlow).

2. لماذا مكتبة Turbine هي الأفضل؟
   - توفر دالة `flow.test { ... }`.
   - تسمح لك باستهلاك العناصر عنصراً بعنصر بشكل متزامن وحتمي:
     * `awaitItem()`: تنتظر وتسترجع العنصر التالي وتتحقق من قيمته.
     * `awaitComplete()`: تتحقق من انتهاء التدفق بنجاح.
     * `awaitError()`: تتحقق من رمي الاستثناء المتوقع.
     * `expectNoEvents()`: تتأكد من عدم وجود أي انبعاثات جديدة.

3. التكامل مع `runTest`:
   - `runTest` تسرع الوقت الافتراضي وتتحكم في الـ `StandardTestDispatcher` لضمان اختبارات سريعة ومستقرة 100% بدون أي Flakiness.

## Practical walkthrough

كتابة Unit Test كامل لاختبار ViewModel StateFlow باستخدام Turbine:
```kotlin
@Test
fun `searchQuery updates uiState from Loading to Success`() = runTest {
    val fakeRepo = FakeRepository()
    val viewModel = SearchViewModel(fakeRepo)

    // نختبر تدفق الـ StateFlow باستخدام Turbine:
    viewModel.uiState.test {
        // 1. أول عنصر يجب أن يكون القيمة الابتدائية Loading:
        assertEquals(SearchUiState.Loading, awaitItem())

        // 2. تفعيل البحث:
        viewModel.onSearchQueryChanged("Kotlin")

        // 3. ننتظر العنصر الثاني ونتحقق من نتائج البحث:
        val successItem = awaitItem()
        assertTrue(successItem is SearchUiState.Success)
        assertEquals("Kotlin", (successItem as SearchUiState.Success).query)

        // 4. نلغي المراقبة بأمان:
        cancelAndIgnoreRemainingEvents()
    }
}
```

## Why it matters and how it works

Inject dispatchers so operators use the test scheduler; advance time and run queued tasks deliberately. Test both cold subscription counts and hot initial/replay behavior. Turbine is a separate test dependency; document version through the project catalog. Device lifecycle and real transport behavior require integration tests.

## Worked example

JVM test illustration assumes `kotlinx-coroutines-test`, `app.cash.turbine:turbine` and kotlin-test; it checks a simple cold flow.

```kotlin
import app.cash.turbine.test
import kotlinx.coroutines.flow.flowOf
import kotlinx.coroutines.test.runTest
import kotlin.test.Test
import kotlin.test.assertEquals

class StreamTest {
    @Test fun valuesInOrder() = runTest {
        flowOf(1, 2).test {
            assertEquals(1, awaitItem())
            assertEquals(2, awaitItem())
            awaitComplete()
        }
    }
}
```

## Trade-offs and decision criteria

Turbine improves readable stream assertions but does not fix an uncontrolled real dispatcher. Virtual time is fast and precise for coroutine scheduling, not a proof of Android process death or real network timing. Test semantics, not implementation details such as exact internal buffering.

## Failure modes

A test that never cancels a StateFlow turbine can hang because StateFlow never completes. Using `Thread.sleep` for debounce creates flaky timing. Expecting every rapid StateFlow assignment ignores equality/conflation behavior.

## Production perspective

A search ViewModel test advances 299 ms to assert no request, then the next millisecond to assert one query, delivers an old response after a new query and verifies it never renders. Separate instrumented tests drive START/STOP and rotation.

## Interview answer — short

Test flows deterministically using runTest paired with CashApp's Turbine library. Turbine's flow.test { } provides awaitItem(), awaitComplete(), and expectNoEvents() to assert on emissions sequentially without hanging on infinite streams like StateFlow.

## Interview answer — structured

Testing Kotlin Flows deterministically requires pairing `kotlinx-coroutines-test` (`runTest`) with Cash App's **Turbine** library.

Standard assertions fail on flows because terminal operators like `collect()` or `toList()` suspend indefinitely on infinite streams like `StateFlow`. Turbine solves this by providing the `flow.test { }` extension.

Inside the `test` block, Turbine exposes a sequential event-driven API.

First, with awaitItem(), suspends until the next emission arrives and returns it for assertion. Next, with awaitComplete(), asserts that the stream completed normally.
Additionally, with awaitError(), asserts that the stream terminated with an expected exception. With expectNoEvents(), verifies that no unexpected emissions occurred within the virtual time window.
Finally, with cancelAndIgnoreRemainingEvents(), cleans up subscriptions on infinite flows like StateFlow so tests finish without uncompleted coroutine errors.


## Interview answer — deep senior

Under the hood, Turbine wraps the flow inside an internal Channel that records emitted items, completion signals, and exceptions as typed `Event<T>` instances. Because it operates inside `runTest`, delays in operators like `debounce` or `WhileSubscribed` do not require real-time sleep: `testScheduler.advanceTimeBy()` triggers delayed emissions instantaneously.

When testing `StateFlow` created via `stateIn(viewModelScope, WhileSubscribed(5000), Initial)`: 1. Calling `stateFlow.test { }` subscribes to the flow, advancing `subscriptionCount` from 0 to 1 and triggering the upstream flow. 2. The first `awaitItem()` immediately yields the `initialValue`. 3. Advancing virtual time or completing fake repository coroutines triggers subsequent `awaitItem()` yields. 4. Finally, calling `cancelAndConsumeRemainingEvents()` drops `subscriptionCount` back to 0, ensuring full lifecycle test coverage.


## How to answer in the interview

- **Why:** timing bugs need controlled schedules.
- **How:** runTest virtual clock and Turbine item assertions.
- **Trade-off:** test dispatchers must reach the code under test.
- **Failure case:** hanging forever on hot Flow or missing initial state.
- **Production solution:** test subscribers, cancellation, and lifecycle-equivalent gaps.

## Deep-dive talking points

Test subscription count, initial value, late subscriber, virtual time and cancellation cleanup.

## Follow-up questions

- **Interviewer:** "Why does calling `stateFlow.toList()` cause a unit test to hang indefinitely?"
  **Answer:** "Because `toList()` collects until the flow terminates. `StateFlow` is an infinite stream that never completes on its own, so `toList()` will suspend forever until the test framework times out."

- **Interviewer:** "What is `turbineScope { }`?"
  **Answer:** "`turbineScope` allows testing multiple flows concurrently within the same test block (e.g., verifying that emitting on one flow triggers an expected update on another flow)."

- **Interviewer:** "How do you test a debounced flow with Turbine?"
  **Answer:** "Call `flow.test { ... }`, emit a query, assert with `expectNoEvents()`, call `advanceTimeBy(300L)`, and then assert the debounced query using `awaitItem()`."

## Self-check rubric

Can I write a terminal and endless-stream test, control time, close collectors and name a device test?

## References and reviewed-on date

- [Kotlin coroutines test API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/) — runTest and scheduler.
- [Turbine project](https://github.com/cashapp/turbine) — Flow testing assertions.

Technically reviewed against primary documentation on 2026-10-13.
