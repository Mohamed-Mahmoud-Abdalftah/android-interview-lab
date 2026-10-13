---
id: "TST-04"
question: "What makes a class testable?"
topic: "Testing, Quality & Reliability"
code: "TST"
group: "A"
phase: 4
priority: "P1"
order: 399
editorial_status: "reviewed"
---

# TST-04

## Original interview question

What makes a class testable?

## What the interviewer evaluates

- Dependency boundaries, deterministic time and observable outputs.
- Why testability should follow clear ownership, not public-method proliferation.

## Explanation in Arabic

ما الذي يجعل الكلاس أو المكون البرمجي قابلاً للاختبار (Testable) في معمارية أندرويد الحديثة؟

1. الخصائص الهندسية للكود القابل للاختبار (Testability Attributes):
   - **حقن التبعيات الصريح (Constructor Dependency Injection)**: استقبال كل التبعيات عبر الـ Constructor بدلاً من إنشائها داخلياً (`val repo = UserRepositoryImpl()`) أو الاعتماد على Singletons عامة.
   - **الاعتماد على التجريد (Depend on Abstractions / Interfaces)**: جعل الكلاس يعتمد على Interface للـ Repository والـ Services يتيح استبدالها بـ Fakes في الاختبارات.
   - **حقن مشغلات الكوروتين (Coroutine Dispatcher Injection)**: عدم كتابة `Dispatchers.IO` صراحة داخل الكود! يجب تمرير الـ Dispatcher في الـ Constructor لاستبداله بـ `StandardTestDispatcher` في الاختبارات.
   - **دوال نقية وخالية من الآثار الجانبية (Pure Functions)**: دوال تأخذ مدخلات وتخرج نتائج محددة دون تعديل حالة عامة (State).

2. ما الذي يدمر قابلية الاختبار (Anti-Patterns)?:
   - الوصول المباشر لكائنات الـ Android Framework (مثل `Context.getString()`, `SharedPreferences`, `Log.*`) داخل دوال الـ Business Logic.
   - استخدام `System.currentTimeMillis()` مباشرة (يجعل الاختبار غير حتمي؛ يجب حقن كائن `Clock`).

## Practical walkthrough

المقارنة بين كلاس غير قابل للاختبار وكلاس مصمم بقابلية اختبار فائقة عبر حقن التبعيات والـ Dispatchers والـ Clock:
```kotlin
// ❌ كود سيئ يستحيل اختباره في Unit Test منعزل:
class BadUserManager(private val context: Context) {
    // إنشاء التبعيات داخلياً والاعتماد على Singletons و Dispatcher ثابت ووقت النظام:
    private val api = NetworkClient.instance.api
    private val prefs = context.getSharedPreferences("user_prefs", Context.MODE_PRIVATE)

    fun saveUserSession(token: String) {
        CoroutineScope(Dispatchers.IO).launch { // استخدام Dispatchers.IO و Scope غير مراقب!
            prefs.edit().putString("token", token).putLong("time", System.currentTimeMillis()).apply()
        }
    }
}

// ✅ كود مصمم باحترافية وقابل للاختبار الفوري على الـ JVM:
class TestableUserManager @Inject constructor(
    private val tokenStorage: TokenStorage,       // مفصول عبر Interface
    private val clock: Clock,                     // حقن الوقت لضمان الحتمية في الاختبارات
    private val ioDispatcher: CoroutineDispatcher // حقن الـ Dispatcher لاستبداله بـ TestDispatcher
) {
    suspend fun saveUserSession(token: String) = withContext(ioDispatcher) {
        tokenStorage.saveToken(token, timestamp = clock.millis())
    }
}
```

## Why it matters and how it works

Constructor-injected interfaces let tests substitute deterministic collaborators. Clock and coroutine dispatcher injection remove wall-time scheduling; immutable inputs and explicit outputs make behavior reproducible. The class should own one coherent responsibility with errors represented clearly.

## Worked example

A `SessionExpiryUseCase(clock: Clock, repository: SessionRepository)` can be tested at a fixed instant with a fake repository. A class that calls `System.currentTimeMillis()` and a global Retrofit singleton during its constructor forces slow, brittle integration tests.

## Trade-offs and decision criteria

Injecting every trivial value can overcomplicate code. Prefer seams at nondeterministic boundaries—time, network, disk, randomness—and keep pure functions simple. A real-adapter test remains necessary for integration semantics.

## Failure modes

A test fake passes because the class never checks database transaction behavior. Testability does not mean replacing every dependency in all tests; use focused integration tests. Static/global state leaking between tests causes order dependence.

## Production perspective

Code review checks constructor side effects, hidden globals and lifecycle ownership. Tests cover normal, error and cancellation paths through public behavior; performance-sensitive adapter details get separate integration checks.

## Interview answer — short

A class is testable when it receives all dependencies explicitly via its constructor, depends on interfaces rather than concrete singletons, injects CoroutineDispatchers rather than hardcoding Dispatchers.IO, avoids direct Android Context references, and injects Clock abstractions for time.

## Interview answer — structured

Testability is a direct reflection of architectural decoupling and inversion of control:

1. **Constructor Dependency Injection**:
   - Classes must never instantiate their own dependencies (`MyRepository()`) or reach out to global singleton state. Passing dependencies via constructors allows unit tests to inject fakes, mocks, or stubs effortlessly.

2. **Decoupling from the Android Framework**:
   - Domain and business logic classes should contain zero imports from `android.*`. Passing `Context` into domain calculators or repositories tethers code to the Android runtime, forcing slow emulator execution or complex mocking.

3. **Injected Coroutine Dispatchers**:
   - Never hardcode `Dispatchers.IO` or `Dispatchers.Default`. Inject dispatchers as constructor parameters (e.g. `@IoDispatcher ioDispatcher: CoroutineDispatcher`). Tests can inject a `StandardTestDispatcher` or `UnconfinedTestDispatcher` to control virtual time deterministically.

4. **Deterministic Time and Randomness**:
   - Never invoke `System.currentTimeMillis()` or `UUID.randomUUID()` directly in business rules. Inject a `Clock` or `IdGenerator` abstraction so tests can assert exact timestamp calculations and deterministic IDs.

## Interview answer — deep senior

From a software design principles viewpoint, testability directly enforces SOLID principles:

1. **Single Responsibility Principle (SRP)**: Classes with poor testability usually perform too many duties: fetching data, parsing JSON, formatting strings, and executing navigation. Splitting concerns creates small, cohesive classes whose single responsibility is verified in 3 concise unit tests.

2. **State Immutability & Observable Streams**: Classes exposing public mutable variables (`var user: User?`) invite race conditions and test state leaks. Testable ViewModels expose immutable `StateFlow<UiState>` streams driven by private unidirectional reducers, making state verification a matter of asserting stream emissions.

3. **Eliminating Global Static Singletons**: Static state (`object DatabaseHolder`) leaks state across independent unit tests, causing test order dependencies where test B passes if run alone but fails if run after test A. Inversion of control ensures every test creates fresh, isolated instances.

## How to answer in the interview

- **Why:** hidden time and I/O make behavior hard to reproduce.
- **How:** inject Clock and repository, then test fixed expiry boundaries.
- **Trade-off:** useful seams versus needless interfaces.
- **Failure case:** constructor network work and global state cause flaky tests.
- **Production solution:** isolate policy and separately test real adapters.

## Deep-dive talking points

Prompt for hidden inputs, clock/dispatcher injection, observable contract and integration limits.

## Follow-up questions

- **Interviewer:** "Why is hardcoding Dispatchers.IO bad for unit testing?"
  **Answer:** "Because tests cannot control thread scheduling or virtual time on real Dispatchers.IO, leading to race conditions, thread leaks, and flaky tests."

- **Interviewer:** "How do you test Android resource strings in a pure JVM ViewModel test?"
  **Answer:** "Expose typed StringResource wrappers or message IDs from the ViewModel; let the Composable layer resolve context.getString(id)."

## Self-check rubric

Identify hidden clock, network and dispatcher dependencies in an untestable class; inject them through a small contract; run a deterministic fixed-time case; and explain why constructor side effects make isolation difficult.

## References and reviewed-on date

- [Android app architecture](https://developer.android.com/topic/architecture) — separation of concerns and testability.
- [Android test doubles](https://developer.android.com/training/testing/fundamentals/test-doubles) — dependency substitutions.

Technically reviewed against primary documentation on 2026-10-13.
