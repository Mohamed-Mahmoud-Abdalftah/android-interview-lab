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

## Concept and technical explanation

Testing dependency injection substitutions and scoped dependencies ensures that production component graphs can be reconfigured cleanly for automated verification without state leaks or architecture violations. In pure JVM unit testing, dependency substitution is achieved seamlessly through constructor injection by supplying test doubles directly. In Hilt on-device or Robolectric testing, substitution operates at the Dagger dependency graph level using @HiltAndroidTest. Developers override production Dagger modules using @UninstallModules and provide test replacements via nested @TestInstallIn modules or @BindValue fields. Testing scoped dependencies (such as @Singleton, @ActivityRetainedScoped, or @ViewModelScoped) requires verifying that instances are reused within their active lifecycle scope and destroyed deterministically when the hosting scope terminates.

## Practical walkthrough (English)

Substituting Hilt modules and testing scoped dependencies using @TestInstallIn:
```kotlin
// 1. Production Module bound to SingletonComponent
@Module
@InstallIn(SingletonComponent::class)
abstract class AnalyticsModule {
    @Binds
    @Singleton
    abstract fun bindAnalytics(impl: FirebaseAnalyticsTracker): AnalyticsTracker
}

// 2. Test Module replacing production module across all tests in the test suite
@Module
@TestInstallIn(
    components = [SingletonComponent::class],
    replaces = [AnalyticsModule::class]
)
abstract class FakeAnalyticsModule {
    @Binds
    @Singleton
    abstract fun bindFakeAnalytics(fake: FakeAnalyticsTracker): AnalyticsTracker
}

// 3. Instrumented Hilt Test verifying scoped dependency substitution
@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class CheckoutActivityTest {
    @get:Rule(order = 0)
    val hiltRule = HiltAndroidRule(this)

    @Inject
    lateinit var analyticsTracker: AnalyticsTracker

    @Before
    fun setup() {
        hiltRule.inject() // Injects FakeAnalyticsTracker!
    }

    @Test
    fun checkout_logsPurchaseEvent_onFakeInstance() {
        val fake = analyticsTracker as FakeAnalyticsTracker
        assertEquals(0, fake.loggedEvents.size)

        launchActivity<CheckoutActivity>().use {
            onView(withId(R.id.btn_buy)).perform(click())
            assertEquals("purchase_completed", fake.loggedEvents.first())
        }
    }
}
```

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

We test DI substitutions differently across testing tiers. In JVM unit tests, we bypass DI frameworks entirely using constructor injection to pass test doubles directly. In Hilt instrumented or Robolectric tests, we use @HiltAndroidTest, replacing production modules with test doubles via @TestInstallIn or @UninstallModules and @BindValue. For scoped dependencies, we verify that instances remain identical within their lifecycle scope and recreate across process recreation.

## Interview answer — structured

Architecting dependency injection with testing in mind is one of the greatest advantages of using Hilt and Dagger in enterprise Android engineering.
At the local JVM unit testing tier, the most effective strategy is to avoid running the DI framework altogether.
Because classes rely on constructor injection, unit tests instantiate the class directly with standard Kotlin constructors, passing in lightweight fakes or mocks without Dagger reflection or annotation processing overhead.
At the instrumented and integration testing tiers, tests must execute against real or emulated dependency graphs.
Hilt provides first-class support for this via the @HiltAndroidTest annotation and HiltAndroidRule.
To substitute an external production service—such as swapping a live payment gateway or Firebase analytics with an in-memory fake—we annotate a test module with @TestInstallIn, explicitly declaring which production module it replaces across the SingletonComponent.
For localized single-test substitutions, developers use @UninstallModules alongside @BindValue, injecting an inline mock directly into the test class.
When validating scoped dependencies, tests assert instance equality (assertSame) across multiple injections within the same Activity or ViewModel lifecycle, and verify that rotating the screen or recreating the component cleans up the scoped instance, preventing cross-test state pollution.

## Interview answer — deep senior

Under the hood, Hilt dependency substitution orchestrates compile-time bytecode rewriting, custom annotation processing, and specialized test application class loading.
Standard production Hilt applications extend a generated Hilt_MyApplication that initializes the root SingletonComponent during onCreate().
When @HiltAndroidTest is executed, the Android test runner (such as HiltTestRunner) substitutes the application instance with HiltTestApplication before component binding starts.
Hilt's annotation processor scans the test classpath for all @TestInstallIn declarations and constructs a bespoke Dagger component graph specifically for the test suite execution.
Any module listed in replaces = [...] is stripped out of the generated Dagger component definition, ensuring that production bindings are never instantiated.
When @BindValue is used, Hilt generates a subcomponent binding that intercepts the injection graph at compile time, passing the exact instance initialized in the test class register.
Regarding scope lifecycles, Hilt scopes correspond to memoization entries stored in a thread-safe ScopeMap inside the generated Dagger subcomponent.
For example, @ActivityRetainedScoped instances are stored in an ActivityRetainedComponent holder that survives configuration changes by attaching to an internal headless ViewModelStore.
Testing these scopes requires simulating configuration changes using ActivityScenario.recreate() and asserting that the injected dependency retains its exact identity hash code, whereas calling ActivityScenario.close() disposes of the component and evicts all scoped references from memory, preventing memory leaks between test executions.

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
