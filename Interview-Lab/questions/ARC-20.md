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

Test Domain independently using pure JVM unit tests with Fake Repositories to verify business rules. Test Data using Fake DataSources or MockWebServer for repositories, and In-Memory Room databases for DAOs. Test Presentation using Turbine and TestDispatchers for ViewModels, and `createComposeRule()` for UI composables.

## Interview answer — structured

Architectural layering enables independent, deterministic test suites without brittle end-to-end integration dependencies.

First, **Domain Layer Testing**. Next, with Environment, pure JVM tests running in milliseconds.
Additionally, with Methodology, instantiate Use Cases directly. Inject lightweight in-memory Fake Repositories. Assert business rule calculations, edge-case thresholds, and domain error flows without mock frameworks. **Data Layer Testing**.
With Repositories, tested via Fake Remote DataSources and Fake DAOs. Verify that repository logic correctly coordinates caching, writes network responses into the database, and maps DTOs into domain models. With DAOs, tested via `Room.inMemoryDatabaseBuilder()` in JVM tests (via Robolectric) or instrumented tests to verify SQL queries, table relations, and foreign key cascades.
**Presentation Layer Testing**. With ViewModels, tested via `runTest`, `StandardTestDispatcher`, and Cash App's **Turbine**. Assert that repository emissions produce the exact sequence of `UiState` snapshots.
Finally, with Composables, tested via `createComposeRule()` on pure stateless screen composables, asserting semantic trees and user interactions.


## Interview answer — deep senior

The overarching principle is preferring **Fakes over Mocks**. Mocking libraries (Mockito/MockK) record interactions (`verify { repo.call() }`), which tightly couples tests to implementation details and makes refactoring brittle. In contrast, a `FakeUserRepository` implements the `UserRepository` interface backed by a simple in-memory `MutableStateFlow` or `HashMap`. Tests verify visible outcomes (the state changes) rather than whether a specific method was invoked, dramatically increasing test resilience.

Furthermore, because Domain and ViewModel tests have zero Android Gradle plugin dependencies, an entire enterprise test suite of 3,000+ tests runs in under 15 seconds in CI, providing immediate developer feedback.


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
