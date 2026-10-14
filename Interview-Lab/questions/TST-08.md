---
id: "TST-08"
question: "How do you unit-test ViewModels, UseCases, and Repositories?"
topic: "Testing, Quality & Reliability"
code: "TST"
group: "B"
phase: 4
priority: "P1"
order: 403
editorial_status: "reviewed"
---

# TST-08

## Original interview question

How do you unit-test ViewModels, UseCases, and Repositories?

## What the interviewer evaluates

- Layer-specific assertions, not one giant mocked ViewModel test.
- Coroutine scheduling, state emissions and real adapter checks.

## Explanation in Arabic

كيف تقوم باختبار الـ ViewModels والـ UseCases والـ Repositories باحترافية وبشكل منعزل على الـ JVM؟

1. اختبار الـ UseCases (Domain Layer):
   - أسهل طبقة في الاختبار؛ لأنها كود Kotlin نقي وخالٍ من أي كود يخص أندرويد.
   - نمرر لها Fake Repositories، ونختبر منطق العمل وحسابات البيانات وحالات الخطأ مباشرة.

2. اختبار الـ ViewModels (Presentation Layer):
   - **التحدي**: `viewModelScope` يعتمد على `Dispatchers.Main` الذي لا يعمل على JVM بدون محاكي!
   - **الحل**: استبدال الـ Main Dispatcher بـ `StandardTestDispatcher` عبر `Dispatchers.setMain()`.
   - نقوم بإرسال أحداث (Events) للـ ViewModel ونفحص تدفق الـ `StateFlow` الناتج باستخدام مكتبة **Turbine** للتأكد من تسلسل الحالات.

3. اختبار الـ Repositories (Data Layer):
   - نختبر التنسيق بين الـ Local Data Source (قاعدة البيانات) والـ Remote Data Source (الشبكة).
   - نستخدم Fake DAO و MockWebServer للتأكد من أن البيانات تُجلب من الشبكة وتُحفظ في قاعدة البيانات المحلية بشكل سليم عند عمل Refresh.

## Practical walkthrough

تنفيذ اختبارات وحدة متكاملة لـ UseCase و ViewModel باستخدام MainDispatcherRule ومكتبة Turbine:
```kotlin
// 1. اختبار UseCase نقي مع Fake Repository:
class FormatOrderSummaryUseCaseTest {
    @Test
    fun `formatSummary calculates tax and returns domain model`() = runTest {
        val fakeCartRepo = FakeCartRepository(items = listOf(CartItem("item1", priceCents = 1000)))
        val useCase = FormatOrderSummaryUseCase(fakeCartRepo)

        val summary = useCase.execute()
        assertEquals("$10.00", summary.formattedSubtotal)
        assertEquals("$1.40", summary.formattedTax) // ضريبة 14%
    }
}

// 2. اختبار ViewModel مع استبدال Main Dispatcher واستخدام Turbine لفحص StateFlow:
class OrderViewModelTest {
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule() // يستبدل Dispatchers.Main بـ StandardTestDispatcher

    @Test
    fun `loadOrder emits Loading then Success state`() = runTest {
        val fakeRepo = FakeOrderRepository(order = Order(id = "123", total = 100))
        val viewModel = OrderViewModel(fakeRepo)

        // مراقبة الـ StateFlow باستخدام Turbine:
        viewModel.uiState.test {
            assertEquals(OrderUiState.Idle, awaitItem()) // الحالة الأولية

            viewModel.loadOrder("123")
            mainDispatcherRule.testDispatcher.scheduler.runCurrent()

            assertEquals(OrderUiState.Loading, awaitItem()) // حالة التحميل
            
            mainDispatcherRule.testDispatcher.scheduler.advanceUntilIdle()
            val successState = awaitItem() as OrderUiState.Success
            assertEquals("123", successState.order.id)
        }
    }
}
```

## Why it matters and how it works

Inject dependencies and dispatchers. Collect StateFlow under TestScope, trigger actions and advance scheduler deliberately. For repository tests, fake network/DAO for coordination logic and add integration tests for SQL, serialization and transaction behavior.

## Worked example

A ViewModel loads account summary. Fake repository emits Loading then an error; test asserts UI state and retry action. A use case test checks overdraft policy pure JVM. A Room repository integration test verifies that cache write and observation survive recreation.

## Trade-offs and decision criteria

Fast fakes improve diagnosis but may not model DB/HTTP contracts. Over-mocking every method call makes tests fragile; assert externally visible state and add real-adapter tests for persistence.

## Failure modes

A ViewModel launches on real Main and the test hangs; install a MainDispatcherRule and share testScheduler. A repository fake returns immediate success, hiding intermediate Loading; control emission timing.

## Production perspective

CI runs JVM layer tests on each PR, targeted DB/network integration tests, and a few UI flows. Production defects feed new tests at the responsible layer.

## Interview answer — short

Test UseCases on the JVM as pure functions using Fake repositories. Test ViewModels by swapping Dispatchers.Main with a TestDispatcher via a JUnit rule and asserting StateFlow transitions with Turbine. Test Repositories by verifying coordination between in-memory Room DAOs and MockWebServer network responses.

## Interview answer — structured

Unit testing across presentation, domain, and data layers requires tailored testing strategies per layer.

First, **Testing UseCases (Domain Layer)**. Next, useCases are pure Kotlin business orchestrators with zero framework dependencies. Test them synchronously or via `runTest`. Inject in-memory Fakes for repositories, verify business calculations, and assert that business boundary errors (e.g. Empty cart validations) throw typed domain exceptions.
**Testing ViewModels (Presentation Layer)**. With Main Dispatcher Replacement, replace `Dispatchers.Main` with `StandardTestDispatcher` using a reusable JUnit `@Rule` (`MainDispatcherRule`).
With Reactive StateFlow Verification with Turbine, collect the ViewModel's `StateFlow` inside a `turbine.test { }` block. Trigger user intent events, advance virtual time, and assert state emissions sequentially (`Idle -> Loading -> Success`). **Testing Repositories (Data Layer)**.
Finally, test caching and synchronization logic. Supply an in-memory SQLite DAO (or Fake DAO) and a `MockWebServer` network client. Verify that fetching data updates local storage, handles 500 network exceptions gracefully by returning cached data, and maps network DTOs into domain models accurately.


## Interview answer — deep senior

From an architectural rigor perspective, isolating tests prevents coupling to UI rendering lifecycles.

First, with Testing WhileSubscribed(5000) Flows, in production ViewModels, `stateIn` typically uses `SharingStarted.WhileSubscribed(5000)`. In unit tests without Turbine, collecting `uiState.value` directly returns the initial state because no UI collector is active! Using Turbine's `.test { }` creates an active subscription, ensuring the upstream cold flow executes and emits values. Next, with Testing Unhandled Coroutine Exceptions, when testing error scenarios in ViewModels, ensure exceptions inside `viewModelScope.launch` are caught inside `CoroutineExceptionHandler` or wrapped in `Result<T>`. Unhandled exceptions inside coroutine builders bubble up and fail the `runTest` scope with unhandled test failures.
Finally, with Repository Offline Sync Tests, when verifying offline-first repositories, write scenarios simulating network loss: insert a pending item locally, assert local emission, simulate network restoration with MockWebServer, trigger background sync, and assert that the item status flips to `SYNCED`.


## How to answer in the interview

- **Why:** ViewModel, UseCase and Repository own different invariants.
- **How:** test UI state with a fake, policy on JVM and storage with a real data source.
- **Trade-off:** isolation speeds feedback but cannot prove persistence.
- **Failure case:** asserting only collaborator calls misses a wrong displayed state.
- **Production solution:** layer-specific tests for one offline account journey.

## Deep-dive talking points

Prompt for layer contracts, test scheduler, fake drift, StateFlow sequence and process-death boundary.

## Follow-up questions

- **Interviewer:** "Why does uiState.value return initial state in tests when using SharingStarted.WhileSubscribed?"
  **Answer:** "Because WhileSubscribed only triggers upstream flow collection when an active subscriber is listening; without Turbine or a collector, upstream never starts."

- **Interviewer:** "What is the primary benefit of testing UseCases independently from ViewModels?"
  **Answer:** "It tests core business algorithms in complete isolation, allowing test reuse across multiple presentation screens and platforms (KMP)."

## Self-check rubric

Test a ViewModel state transition with a controlled fake and dispatcher, a UseCase invariant on the JVM, and a Repository persistence/observation contract against its real data source. Identify which mock-only assertion would be too weak.

## References and reviewed-on date

- [Android ViewModel testing](https://developer.android.com/topic/libraries/architecture/viewmodel) — ViewModel lifecycle and state.
- [Android coroutine testing](https://developer.android.com/kotlin/coroutines/test) — dispatcher/test-scope guidance.

Technically reviewed against primary documentation on 2026-10-13.
