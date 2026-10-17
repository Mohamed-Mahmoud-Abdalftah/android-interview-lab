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

## Concept and technical explanation

Unit testing ViewModels, UseCases, and Repositories on the host JVM requires a layered isolation strategy that replaces heavy Android framework dependencies with test doubles, swaps the Android main thread dispatcher with a virtual TestDispatcher, and verifies reactive asynchronous streams using Turbine. UseCases are tested in pure isolation against fake or mocked repositories to assert domain business rules and edge conditions. Repositories are tested by coordinating fake network data sources and in-memory caches, validating offline-first policies, DTO mapping, and exception wrapping. ViewModels are tested using a custom JUnit TestRule (MainDispatcherRule) that replaces Dispatchers.Main with StandardTestDispatcher or UnconfinedTestDispatcher, capturing state emissions from StateFlow and SharedFlow to assert deterministic UI state transitions.

## Practical walkthrough (English)

Testing UseCases, Repositories, and ViewModels using MainDispatcherRule and Turbine:
```kotlin
// 1. Reusable JUnit Rule to replace Dispatchers.Main on JVM
class MainDispatcherRule(
    val testDispatcher: TestDispatcher = StandardTestDispatcher()
) : TestWatcher() {
    override fun starting(description: Description) = Dispatchers.setMain(testDispatcher)
    override fun finished(description: Description) = Dispatchers.resetMain()
}

// 2. Unit Testing ViewModel using MainDispatcherRule and Turbine
class UserProfileViewModelTest {
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private val getUserUseCase = mockk<GetUserUseCase>()
    private lateinit var viewModel: UserProfileViewModel

    @Before
    fun setup() {
        viewModel = UserProfileViewModel(getUserUseCase)
    }

    @Test
    fun loadUser_emitsLoadingThenSuccess_usingTurbine() = runTest {
        val user = User(id = "1", name = "Mohamed")
        coEvery { getUserUseCase("1") } returns Result.success(user)

        viewModel.uiState.test {
            // Initial state
            assertEquals(ProfileUiState.Idle, awaitItem())

            viewModel.loadProfile("1")

            // Intermediate Loading state
            assertEquals(ProfileUiState.Loading, awaitItem())

            // Final Success state
            assertEquals(ProfileUiState.Success(user), awaitItem())
        }
    }
}
```

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

We unit-test clean architecture layers in isolation on the JVM. UseCases are tested against fake repositories to verify business logic. Repositories are tested by mocking network and local sources to verify caching and error handling. ViewModels are tested by applying a MainDispatcherRule that replaces Dispatchers.Main with a TestDispatcher, using Turbine to collect and assert StateFlow emissions sequentially across loading, error, and success states.

## Interview answer — structured

Architecting robust unit tests across ViewModels, UseCases, and Repositories requires distinct testing strategies tailored to each architectural boundary.
At the domain layer, UseCases are the easiest to test because they contain zero Android framework dependencies.
We test them purely on the JVM, passing in fake or mocked repositories to verify business validation rules, authorization logic, and domain transformations across success and error permutations.
At the data layer, Repositories coordinate remote network datasources and local databases.
We test repositories by injecting mock network APIs and in-memory Room DAOs, asserting that the repository implements correct offline-first synchronization, handles network timeouts gracefully, maps raw DTOs into immutable domain entities, and catches low-level exceptions.
At the presentation layer, testing ViewModels introduces two unique concurrency challenges: Dispatchers.Main and reactive StateFlow emission streams.
Because the Android platform Main Looper does not exist on the desktop JVM, any call to Dispatchers.Main immediately crashes with an initialization exception.
To resolve this, we apply a reusable JUnit TestWatcher rule—MainDispatcherRule—that invokes Dispatchers.setMain(testDispatcher) before every test and resets it afterward.
We then employ the Turbine library to open a test collector on the ViewModel's uiState StateFlow, sequentially asserting that user intent triggers an immediate Loading state followed deterministically by a Success or Error state.

## Interview answer — deep senior

Under the hood, unit testing Clean Architecture layers on the JVM hinges on replacing platform dispatchers and handling hot coroutine stream lifecycles.
When testing ViewModels, viewModelScope defaults internally to Dispatchers.Main.immediate.
On the JVM, the kotlinx-coroutines-android artifact attempts to resolve the Main dispatcher via ServiceLoader, which queries Android's native android.os.Looper.
Because Looper.getMainLooper() returns null outside the Android ART runtime, attempting to launch a coroutine throws IllegalStateException('Module with the Main dispatcher had failed to initialize').
MainDispatcherRule bypasses this framework check by directly invoking Dispatchers.setMain(testDispatcher), injecting a virtualized TestDispatcher into the coroutine runtime's internal dispatcher registry.
When testing StateFlow emissions, standard collection via launch { viewModel.uiState.collect { ... } } is prone to deadlocks and race conditions because StateFlow is a hot, conflated stream that never completes naturally.
Turbine overcomes this by hooking into the StateFlow collector via a FlowTurbine channel.
Every time the ViewModel updates its state using _uiState.update { ... }, Turbine enqueues the state emission into an internal rendezvous channel.
When the test invokes awaitItem(), Turbine suspends until the next emission arrives or immediately pops the item if already enqueued, failing the test with a descriptive error if unexpected emissions occur or if the stream throws an unhandled exception.
Senior engineers combine MainDispatcherRule and Turbine to achieve 100% deterministic assertion coverage over complex reactive UI flows without a single flaky millisecond.

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
