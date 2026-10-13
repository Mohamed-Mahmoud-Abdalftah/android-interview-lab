---
id: "TST-01"
question: "Compare unit, integration, instrumentation, UI, and end-to-end tests."
topic: "Testing, Quality & Reliability"
code: "TST"
group: "A"
phase: 4
priority: "P1"
order: 396
editorial_status: "reviewed"
---

# TST-01

## Original interview question

Compare unit, integration, instrumentation, UI, and end-to-end tests.

## What the interviewer evaluates

- Test boundary, speed and fidelity across five levels.
- Choosing the cheapest level that detects a specific risk.

## Explanation in Arabic

قارن بين اختبارات الوحدة (Unit)، والتكامل (Integration)، والأجهزة (Instrumentation)، والواجهة (UI)، والنهاية للنهاية (End-to-End)؟

1. طيف الاختبارات في أندرويد (The Android Testing Spectrum):
   - **Unit Tests (Local JVM Tests)**: تُنفذ على الـ JVM المحلي داخل الحاسوب دون الحاجة لمشغل أو محاكي أندرويد (`src/test/`). سريعة جداً (بضعة أجزاء من الثانية لكل اختبار)، وتختبر دالة أو كلاس واحد بمعزل عن النظام (ViewModels, UseCases, Mappers).
   - **Integration Tests**: تختبر تفاعل مكونين أو أكثر معاً للتأكد من صحة الاتصال (مثل اختبار Repository يتصل بـ Room Database محلية أو MockWebServer).
   - **Instrumentation Tests (On-Device Tests)**: تتطلب تشغيل جهاز أندرويد حقيقي أو محاكي (`src/androidTest/`). تختبر كوداً يعتمد على Android Framework الحقيقي (SQLite، SharedPreferences، الخدمات، ومدير الحزم).
   - **UI Tests (Compose / Espresso)**: تختبر الشاشات وتفاعل المستخدم (الضغط على الأزرار، التمرير، وظهور النصوص وقراءة Semantics شجرة الـ Compose).
   - **End-to-End Tests (E2E)**: تختبر تدفق المستخدم الكامل من البداية للنهاية (تسجيل دخول -> إضافة للسلة -> إتمام الدفع عبر بيئة Staging حقيقية).

2. المفاضلات الهندسية (Trade-offs):
   - كلما صعدت لأعلى (من Unit إلى E2E): تزداد الموثوقية وواقعية الاختبار، ولكن **تزداد التكلفة والبطء واحتمالية الاختبارات المتقلبة (Flakiness)**.

## Practical walkthrough

المقارنة بين Unit Test سريع على JVM و Instrumented Test يتطلب جهازاً حقيقياً في Room:
```kotlin
// 1. Unit Test سريع في src/test/ (ينفذ في 10ms على JVM بدون أندرويد):
class PriceCalculatorTest {
    @Test
    fun `calculateDiscount applies percentage correctly`() {
        val calculator = PriceCalculator()
        val finalPrice = calculator.applyDiscount(originalPrice = 100.0, discountPercent = 20)
        assertEquals(80.0, finalPrice, 0.001)
    }
}

// 2. Instrumented Integration Test في src/androidTest/ (يتطلب محاكي لفحص SQLite الحقيقي):
@RunWith(AndroidJUnit4::class)
class UserDaoTest {
    private lateinit var db: AppDatabase
    private lateinit var userDao: UserDao

    @Before
    fun createDb() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        db = Room.inMemoryDatabaseBuilder(context, AppDatabase::class.java).build()
        userDao = db.userDao()
    }

    @Test
    fun insertAndReadUser() = runTest {
        val user = UserEntity(id = "1", name = "Ahmed")
        userDao.insert(user)
        val byId = userDao.getUserById("1")
        assertEquals("Ahmed", byId?.name)
    }
}
```

## Why it matters and how it works

The levels vary in environment, not just file location. A pure JVM test cannot prove platform permission behavior, while an end-to-end payment test may detect cross-system contract failures but runs slower and is less deterministic. Contract tests sit between isolated unit logic and full E2E.

## Worked example

Test fee calculation as JVM unit; Room migration on an Android test device or suitable test database; Compose semantics with UI testing; a checkout sandbox flow end-to-end. Do not use a mocked repository to claim database durability was tested.

## Trade-offs and decision criteria

Fast tests give tight feedback; high-fidelity tests cover platform and system integration. Put deterministic logic low in the pyramid, then add a small number of device and E2E tests for risks only they can observe.

## Failure modes

A ViewModel unit test passes while a manifest permission or Room migration breaks on device. Conversely, thousands of UI tests make every PR slow and flaky. Map each production incident to the lowest effective test layer.

## Production perspective

CI runs JVM tests and static checks early, device tests on supported API/device matrix, and a limited critical-journey suite before release. Track failure detection value and runtime per layer.

## Interview answer — short

Unit tests run on the local JVM in milliseconds testing isolated logic. Integration tests verify interactions between components like repositories and databases. Instrumentation tests run on Android devices/emulators testing framework code. UI tests verify user interactions, and E2E tests validate complete user journeys across real backends.

## Interview answer — structured

The Android testing spectrum balances execution speed, maintenance costs, and production confidence:

1. **Local Unit Tests (`src/test/`)**:
   - Execute on the host machine's JVM without an emulator. Run in milliseconds. Ideal for ViewModels, pure domain UseCases, business algorithms, and data mappers.

2. **Integration Tests**:
   - Verify that multiple collaborating units interact correctly across module boundaries (e.g. testing Room DAOs against SQLite, or network parsers against OkHttp MockWebServer).

3. **Instrumentation Tests (`src/androidTest/`)**:
   - Execute inside an Android OS process on physical hardware or emulators. Used whenever real Android OS runtime primitives (ART, Binder IPC, Keystore, real SQLite drivers) must be validated.

4. **UI Tests (Compose Test / Espresso)**:
   - Programmatically interact with UI nodes: asserting text presence, triggering clicks, verifying recomposition stability and accessibility semantics.

5. **End-to-End (E2E) Tests**:
   - Exercise complete end-to-end user journeys (e.g., login, onboarding, checkout) against staging server infrastructure. Provide highest confidence, but carry highest execution duration and flake risks.

## Interview answer — deep senior

From an engineering management and CI governance perspective, test tiering dictates pipeline velocity:

1. **The Cost-Velocity Ratio**: 1,000 local unit tests run in 5 seconds on developer machines and cost zero cloud infrastructure. 20 UI instrumentation tests require booting an emulator, waiting for system initialization, and running for 5 minutes. High-performing engineering teams push 70–80% of test coverage into fast local JVM unit tests.

2. **Robolectric vs. Instrumentation**: Robolectric allows running Android framework tests (like inspecting Android Intent extras, Context resources, or Fragment lifecycles) directly on the local JVM by shadowing Android bytecode. It bridges the gap between speed and framework verification, though it does not replace real device verification for hardware-accelerated rendering or SQLite edge cases.

3. **Hermetic Test Environments**: Reliable CI pipelines mandate hermetic test boundaries. E2E tests that communicate with live external third-party services (e.g. live payment gateways) flake due to network latency; mock external boundaries using WireMock or controlled test stubs.

## How to answer in the interview

- **Why:** one test layer cannot see every boundary.
- **How:** map fee policy, Room, UI and sandbox checkout to the lowest layer that can observe each.
- **Trade-off:** fast isolated coverage versus slower integrated confidence.
- **Failure case:** a mocked DAO cannot prove migration or persistence.
- **Production solution:** risk-based matrix with a few complete release journeys.

## Deep-dive talking points

Prompt for overlap of labels, fidelity limits, payment invariants and CI runtime.

## Follow-up questions

- **Interviewer:** "What is Robolectric and when should you use it?"
  **Answer:** "A framework that provides simulated Android bytecode on the local JVM, allowing Android framework-dependent tests to run in seconds without an emulator."

- **Interviewer:** "Why are E2E tests often flaky in continuous integration pipelines?"
  **Answer:** "Due to external dependencies: network timeouts, test database state contamination, asynchronous UI animation delays, and backend server restarts."

## Self-check rubric

Score one point each for choosing a JVM unit test for pure policy, an integration test for real boundaries, an Android instrumented test for platform behavior, a UI test for user interaction, and a small end-to-end test for the full checkout path. State what each test cannot prove.

## References and reviewed-on date

- [Android testing fundamentals](https://developer.android.com/training/testing/fundamentals) — test types and environment.
- [Android test strategy](https://developer.android.com/training/testing) — official test guidance.

Technically reviewed against primary documentation on 2026-10-13.
