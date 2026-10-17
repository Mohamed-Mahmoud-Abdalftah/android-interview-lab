---
id: "ARC-20"
question: "How do you test Presentation, Domain, and Data independently?"
topic: "Clean Architecture, MVVM, MVI & UDF"
code: "ARC"
group: "B"
phase: 2
priority: "P1"
order: 165
editorial_status: "reviewed"
---

# ARC-20

## Original interview question

How do you test Presentation, Domain, and Data independently?

## What the interviewer evaluates

Define independent tests for UI transitions, business rules and data consistency, plus boundary integration checks.

## Concept and technical explanation

Testing Presentation, Domain, and Data layers independently requires establishing clear boundary seams and substituting adjacent dependencies with test doubles. The Domain layer comprises pure Kotlin business logic with zero Android dependencies; it is verified through blazingly fast JVM unit tests using lightweight in-memory Fake repositories. The Data layer is tested using Fake remote data sources or MockWebServer to assert network error handling, caching policies, and DTO-to-entity mapping, while Room DAOs are tested against in-memory SQLite instances to validate queries, migrations, and relational integrity. The Presentation layer is tested by driving ViewModels with runTest and TestDispatchers, utilizing Turbine to assert deterministic UiState emissions, and evaluating Compose screens with createComposeRule to verify rendering and semantics without booting device activities.

## Practical walkthrough (English)

Testing Domain, Data, and Presentation layers in complete isolation:
```kotlin
// 1. DOMAIN: Pure Kotlin unit test with in-memory Fake repository
class CalculateCartDiscountUseCaseTest {
    @Test
    fun appliesTenPercentDiscount_whenCartExceedsThreshold() {
        val fakeRepo = FakeCartRepository(initialTotal = 150.0)
        val useCase = CalculateCartDiscountUseCase(fakeRepo)
        val discountedTotal = useCase()
        assertEquals(135.0, discountedTotal, 0.01)
    }
}

// 2. DATA: Room DAO test using in-memory SQLite database
@RunWith(AndroidJUnit4::class)
class ProductDaoTest {
    private lateinit var db: AppDatabase
    private lateinit var dao: ProductDao

    @Before
    fun createDb() {
        db = Room.inMemoryDatabaseBuilder(ApplicationProvider.getApplicationContext(), AppDatabase::class.java).build()
        dao = db.productDao()
    }

    @After
    fun closeDb() = db.close()

    @Test
    fun insertAndObserveProducts() = runTest {
        dao.insert(ProductEntity("1", "Laptop", 1200))
        val products = dao.observeProducts().first()
        assertEquals(1, products.size)
    }
}

// 3. PRESENTATION: ViewModel test asserting state emissions via Turbine
class CheckoutViewModelTest {
    @Test
    fun submitPayment_transitionsFromLoadingToSuccess() = runTest {
        val fakeCheckoutRepo = FakeCheckoutRepository()
        val viewModel = CheckoutViewModel(fakeCheckoutRepo, StandardTestDispatcher(testScheduler))

        viewModel.uiState.test {
            assertEquals(CheckoutUiState.Idle, awaitItem())
            viewModel.onPayClicked()
            assertEquals(CheckoutUiState.Processing, awaitItem())
            assertEquals(CheckoutUiState.Success("txn_99"), awaitItem())
        }
    }
}
```

## Explanation in Arabic

كيف تختبر طبقات العرض (Presentation)، النطاق (Domain)، والبيانات (Data) بشكل مستقل ومعزول؟

1. اختبار طبقة النطاق (Domain Layer Testing):
   - **نوع الاختبار**: Pure JVM Unit Tests سريعة للغاية تعمل في أجزاء من الثانية دون أي محاكي.
   - **الاستراتيجية**: اختبار الـ UseCases بحقن Fake Repositories في الـ Constructor مباشرة.
   - **ما يتم التحقق منه**: قواعد البيزنس، العمليات الحسابية، استيفاء الشروط، واختبار المسارات البديلة (Happy path & Edge cases).

2. اختبار طبقة البيانات (Data Layer Testing):
   - **نوع الاختبار**: مزيج بين JVM Tests واختبارات تكامل (Integration Tests).
   - **الاستراتيجية**:
     * لاختبار الـ Repositories: حقن Fake DataSources أو استخدام MockWebServer لفحص استجابات الشبكة، واختبار قواعد المزامنة والـ Caching.
     * لاختبار Room DAOs: استخدام SQLite In-Memory Database (`Room.inMemoryDatabaseBuilder`) للتحقق من سلامة استعلامات SQL ومعاملات الـ Foreign Keys.

3. اختبار طبقة العرض (Presentation Layer Testing):
   - **نوع الاختبار**: Unit Tests للـ ViewModels و Compose UI Tests للواجهات.
   - **الاستراتيجية**:
     * الـ ViewModel: اختبار انبعاثات الـ `StateFlow` باستخدام مكتبة Turbine و `StandardTestDispatcher`.
     * الـ Composable: اختبار الشاشات الـ Stateless باستخدام `createComposeRule()` للتحقق من ظهور العناصر والنقر عليها.

## Practical walkthrough

استراتيجية الاختبار المعزول لكل طبقة من الطبقات الثلاث:
```kotlin
// 1. DOMAIN TEST: اختبار UseCase كود كوتلن نقي بدون أي أندرويد:
class CalculateCartTotalUseCaseTest {
    private val useCase = CalculateCartTotalUseCase()
    @Test
    fun whenCartHasTwoItems_calculatesTotalCorrectly() {
        val items = listOf(CartItem("1", 2, 1000L), CartItem("2", 1, 500L))
        assertEquals(2500L, useCase(items))
    }
}

// 2. DATA TEST: اختبار Repository باستخدام Fake DataSources:
class UserRepositoryTest = runTest {
    private val fakeDao = FakeUserDao()
    private val fakeApi = FakeUserApi()
    private val repo = UserRepositoryImpl(fakeDao, fakeApi)

    @Test
    fun whenNetworkSucceeds_writesToLocalDatabase() = runTest {
        fakeApi.stubUser = UserDto(id = "1", name = "Alice")
        repo.refreshUser("1")
        assertEquals("Alice", fakeDao.getUser("1")?.name)
    }
}

// 3. PRESENTATION TEST: اختبار ViewModel باستخدام Turbine:
class CartViewModelTest {
    @Test
    fun loadCart_emitsLoadingThenSuccess() = runTest {
        val fakeRepo = FakeCartRepository(initialItems = listOf(CartItem("1", 1, 100L)))
        val vm = CartViewModel(fakeRepo, CalculateCartTotalUseCase())
        vm.uiState.test {
            assertEquals(CartUiState.Loading, awaitItem())
            val success = awaitItem() as CartUiState.Success
            assertEquals(100L, success.total)
        }
    }
}
```

## Why it matters and how it works

Layered tests isolate logic and localize failures. Fakes at boundaries make state transitions deterministic; integration tests catch mapper and storage interactions that isolated tests miss. Android-specific behavior needs Android-capable tests.

## Worked example

Test plan for checkout: ViewModel fake use case emits `Pending` then `Accepted`, assert state and duplicate-tap behavior; domain fake repository checks amount limits and cancellation; data fake API plus Room validates request mapping, transaction and retry reconciliation. Device/UI test checks visible states and accessibility.

## Trade-offs and decision criteria

Unit tests are fast and precise but may miss wiring, database migrations and lifecycle. Integration/device tests cost more but cover real behavior. Use a small number of meaningful end-to-end flows instead of mirroring every implementation line.

## Failure modes

A test only verifies `repository.get()` was called, while ViewModel emits `Success` after a failure. Assert output state. Another failure is mocking Room DAO and claiming transaction behavior passed; use a real test database for that guarantee.

## Production perspective

CI runs JVM ViewModel/domain suites on each change, data integration tests for Room/network mapping, and selected instrumented Compose flows for loading/error/success and recreation. Reports distinguish simulated tests from device evidence.

## Interview answer — short

Test Domain independently using pure JVM unit tests with Fake repositories to verify business rules. Test Data by validating repository caching and mapping against Fake data sources, and verifying Room DAOs using in-memory SQLite databases. Test Presentation using Turbine and TestDispatchers for ViewModels to assert deterministic UiState transitions, and createComposeRule for testing composables in isolation.

## Interview answer — structured

Layered architecture allows each tier of an Android application to be tested in isolation using the fastest and most appropriate verification tools.
For the Domain layer, testing focuses entirely on pure business logic. Because use cases contain no Android SDK references, they execute as JVM unit tests in milliseconds. We inject lightweight in-memory Fake repositories through constructors, verifying calculations, business validations, and error pathways without relying on mock frameworks.
Within the Data layer, we separate repository testing from database verification. Repositories are tested on the JVM using Fake network data sources to ensure caching policies, entity mapping, and synchronization algorithms operate correctly. In contrast, Room DAOs are tested against in-memory SQLite databases to validate raw SQL queries, foreign key constraints, and database migrations under realistic relational behavior.
In the Presentation layer, ViewModel unit tests run on the JVM using runTest and StandardTestDispatcher. By pairing test dispatchers with Turbine, we observe StateFlow streams and assert the exact chronological sequence of UiState emissions. Finally, Compose UI elements are validated using createComposeRule, testing user interactions and visual semantics in isolation.

## Interview answer — deep senior

Under the hood, a resilient testing strategy across architectural boundaries hinges on favoring Fakes over Mocks. Mocking frameworks like Mockito or MockK encourage interaction testing, asserting that specific methods were invoked a certain number of times. This couples tests to private implementation details; refactoring internal method calls breaks the test suite even when user-visible behavior remains completely intact.
By creating lightweight Fake implementations of repositories and data sources backed by simple HashMaps or MutableStateFlows, tests verify observable state outcomes rather than mechanics. When a ViewModel triggers an action, the test asserts that the resulting UiState contains the expected models.
In the Presentation layer, testing asynchronous coroutines requires deterministic scheduling. Using runTest with a StandardTestDispatcher freezes virtual time. Suspending functions like delay do not stall test execution; developers advance the test scheduler explicitly using advanceUntilIdle to verify intermediate loading states and final emissions without introducing flaky Thread.sleep calls.
For Data layer verification, testing Room DAOs requires executing real SQLite operations because SQLite syntax and constraint violations cannot be simulated through JVM mocks. Using Room.inMemoryDatabaseBuilder allows these tests to run either via Robolectric on the local JVM or as fast instrumented tests, ensuring database schemas match entity definitions.
Staff engineers establish a pyramid where Domain and Presentation JVM tests constitute eighty percent of the suite, completing thousands of checks in seconds on CI, while integration tests validate database and network serialization boundaries.

## How to answer in the interview

- **Why:** different layers fail in different ways.
- **How:** test state, policy and real adapters separately.
- **Trade-off:** fast feedback versus integration cost.
- **Failure case:** fake passes while Room migration fails.
- **Production solution:** risk-based suite across boundaries.

## Deep-dive talking points

Specify one behavior assertion per layer, a real Room test boundary and an instrumented lifecycle/UI scenario.

## Follow-up questions

- **Interviewer:** "Why use In-Memory Room databases instead of mocking DAOs?"
  **Answer:** "Mocking DAOs tests your mock configuration, not your SQL. An In-Memory Room database executes real SQLite queries against the schema, verifying migrations, SQL syntax, and constraint violations accurately."

- **Interviewer:** "Why should tests prefer Fakes over Mocks?"
  **Answer:** "Fakes provide realistic in-memory behavior, withstand internal refactorings, avoid brittle interaction verifications, and run significantly faster than dynamic mock proxies."

## Self-check rubric

Design a three-layer test matrix for checkout and explain what each suite cannot prove.

## References and reviewed-on date

- [Android testing guide](https://developer.android.com/training/testing) — local and instrumented test roles.
- [Android architecture recommendations](https://developer.android.com/topic/architecture/recommendations) — testability.

Technically reviewed against primary documentation on 2026-10-13.
