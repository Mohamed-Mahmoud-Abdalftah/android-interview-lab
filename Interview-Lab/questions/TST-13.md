---
id: "TST-13"
question: "How do you test DI substitutions and scoped dependencies?"
topic: "Testing, Quality & Reliability"
code: "TST"
group: "B"
phase: 4
priority: "P1"
order: 408
editorial_status: "reviewed"
---

# TST-13

## Original interview question

How do you test DI substitutions and scoped dependencies?

## What the interviewer evaluates

- DI replacement scope and leak between tests.
- Production graph parity, Hilt test bindings and lifecycle.

## Explanation in Arabic

كيف تختبر استبدال التبعيات في الـ Dependency Injection (DI Substitutions) والتبعيات المربوطة بنطاقات (Scoped Dependencies)؟

1. استبدال التبعيات في اختبارات الوحدة (Local Unit Tests):
   - في الـ Unit Tests على JVM: **لا تستخدم Hilt أو Dagger إطلاقاً**!
   - اعتمد على حقن التبعيات عبر الـ Constructor يدوياً (Manual Constructor Injection). هذا يوفر سرعة فائقة في التنفيذ وتجنب أي تعقيد في معالجة الـ Code Generation.

2. استبدال التبعيات في اختبارات التكامل والأجهزة عبر Hilt (`@HiltAndroidTest`):
   - في اختبارات الـ UI والـ Integration Tests التي تتطلب تشغيل Hilt، نستخدم:
     * `@UninstallModules(ProductionNetworkModule::class)` لإلغاء الموديول الحقيقي الخاص بالإنتاج.
     * `@BindValue` لحقن كائن Fake أو Mock مباشرة داخل الـ Hilt Dependency Graph للاختبار الحالي.

3. اختبار التبعيات المربوطة بنطاقات (Scoped Dependencies):
   - **`@Singleton`**: يجب التأكد من عدم تسريب حالتها بين الاختبارات المستقلة (Test Leakage).
   - **`@ViewModelScoped` / `@ActivityScoped`**: التحقق من إعادة إنشاء التبعية عند تدمير وإعادة إنشاء الـ Scope المقترن بها.

## Practical walkthrough

استبدال موديول الإنتاج بـ Fake في اختبارات Hilt عبر @UninstallModules و @BindValue:
```kotlin
@HiltAndroidTest
@UninstallModules(AnalyticsModule::class) // 1. إلغاء موديول الإنتاج الحقيقي
@RunWith(AndroidJUnit4::class)
class CheckoutFlowIntegrationTest {

    @get:Rule(order = 0)
    val hiltRule = HiltAndroidRule(this)

    @get:Rule(order = 1)
    val composeTestRule = createAndroidComposeRule<MainActivity>()

    // 2. حقن كائن Fake بديل مباشرة داخل شجرة الـ DI الخاصة بـ Hilt:
    @BindValue
    val fakeAnalyticsTracker: AnalyticsTracker = FakeAnalyticsTracker()

    @Before
    fun init() {
        hiltRule.inject()
    }

    @Test
    fun checkoutScreen_triggersPurchaseEventOnFakeAnalytics() {
        composeTestRule.onNodeWithText("Complete Order").performClick()
        
        // التحقق من أن الـ Fake Analytics استقبل الحدث بنجاح:
        assertEquals(1, (fakeAnalyticsTracker as FakeAnalyticsTracker).capturedEvents.size)
    }
}
```

## Why it matters and how it works

Hilt generates a component graph with scopes and qualifiers; test replacement alters bindings, not the consumer contract. A local JVM use-case test can construct dependencies directly, while Android instrumentation can test graph construction and injected UI.

## Worked example

For a login screen test, replace `AuthRepository` with a controllable fake in a Hilt test component. Configure its response before launching Activity, then assert UI state. Separately instantiate the production graph in a smoke test to catch missing qualifiers.

## Trade-offs and decision criteria

Full Hilt tests are slower than constructor-injected JVM tests but validate wiring. Use direct construction for behavior and a few graph tests for scopes and qualifiers.

## Failure modes

A singleton fake retains a logged-in session from a previous test, causing order dependence. Reset state per test and avoid shared mutable test objects. A test binding that replaces only one flavor may leave another release graph broken.

## Production perspective

CI verifies unit behavior, instrumentation graph injection and each shipped flavor’s production graph. Test rules clean up components and Main dispatcher after each case.

## Interview answer — short

In local unit tests, substitute dependencies via direct constructor injection without DI frameworks. In Hilt instrumentation tests, use @HiltAndroidTest with @UninstallModules to remove production bindings, replacing them surgically with @BindValue or custom test modules to inject fakes into the active dependency graph.

## Interview answer — structured

Managing dependency injection substitutions in test suites requires separating fast JVM unit tests from full container integration tests.

First, **Local JVM Testing (Pure Constructor Injection)**. Next, bypassing Dagger/Hilt entirely in `src/test/` is an industry best practice. When classes follow constructor injection, tests simply pass instantiated Fakes (`MyViewModel(FakeUserRepository())`). This avoids annotation processing overhead and runs in milliseconds.
**Hilt Integration Testing (`@HiltAndroidTest`)**. When testing full Activity or Fragment flows requiring real dependency graphs.
Decorate test classes with `@HiltAndroidTest` and attach `HiltAndroidRule(this)`. Use `@UninstallModules(ProductionDataModule::class)` to decouple real network/storage bindings.
Use `@BindValue` on a field to automatically bind a Fake instance into the dependency container for that specific test run. **Verifying Scoped Lifecycles**.
Finally, verify that `@ActivityScoped` bindings produce distinct instances when transitioning between activities, while `@Singleton` bindings persist within the test process.


## Interview answer — deep senior

From an architectural systems perspective, managing test DI containers requires preventing cross-test state pollution.

First, with Singleton State Leaks Across Tests, if a Fake bound as a `@Singleton` maintains in-memory state (e.g. `FakeDatabase` holding user records), that state persists across consecutive `@Test` methods unless explicitly wiped in `@After` teardown hooks. Build explicit `clear()` methods on all stateful test fakes. Next, with Custom Test Application in Instrumentation, Hilt generates `HiltTestApplication` for instrumented tests. Ensure your `app/build.gradle.kts` sets `testInstrumentationRunner = "com.example.HiltTestRunner"`, which subclasses `AndroidJUnitRunner` and boots `HiltTestApplication` as the root application context.
Finally, with Dynamic Test Components, for feature-modular codebases, avoid a single monolithic test module. Create isolated test modules per feature (`:feature:checkout:testing`) exporting modular fakes, allowing feature tests to compose test graphs independently.


## How to answer in the interview

- **Why:** a replaceable test graph can hide a broken production graph.
- **How:** substitute AuthRepository before Activity launch and separately smoke-test real bindings.
- **Trade-off:** deterministic feature test versus realistic DI wiring.
- **Failure case:** missing qualifier or wrong scope survives fake-only tests.
- **Production solution:** test both user-visible state and release graph construction.

## Deep-dive talking points

Prompt for binding override, scope, setup-before-launch, flavor parity and fake cleanup.

## Follow-up questions

- **Interviewer:** "What does @BindValue do in Hilt testing?"
  **Answer:** "It binds a test class property into the Hilt dependency graph, replacing any existing binding of that type for the duration of the test."

- **Interviewer:** "Why must HiltAndroidRule have an order index of 0?"
  **Answer:** "Because Hilt must initialize the dependency injection container before other rules (like ActivityScenarioRule or ComposeRule) launch the UI components."

## Self-check rubric

Replace an AuthRepository in a test graph before Activity launch, assert the screen consumes the fake, and separately smoke-test production bindings. Explain scope and qualifier mistakes that a replaced graph can hide.

## References and reviewed-on date

- [Hilt testing](https://developer.android.com/training/dependency-injection/hilt-testing) — test bindings and components.
- [Android test doubles](https://developer.android.com/training/testing/fundamentals/test-doubles) — dependency replacement.

Technically reviewed against primary documentation on 2026-10-13.
