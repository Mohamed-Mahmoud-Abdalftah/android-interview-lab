---
id: "TST-21"
question: "A flaky test passes locally but fails on CI. Explain triage and mitigation."
topic: "Testing, Quality & Reliability"
code: "TST"
group: "C"
phase: 4
priority: "P1"
order: 416
editorial_status: "reviewed"
---

# TST-21

## Original interview question

A flaky test passes locally but fails on CI. Explain triage and mitigation.

## What the interviewer evaluates

- CI-only flake diagnosis with evidence before mitigation.
- Test order, sharding, emulator/resource and race hypotheses.

## Concept and technical explanation

Triaging and mitigating automated tests that pass consistently on local workstations but fail intermittently in Continuous Integration environments requires a disciplined root-cause diagnosis rather than superficial retry masking. CI runner nodes exhibit fundamentally different runtime characteristics than developer machines: virtualized headless CPU resource constraints, thread scheduling latency, lack of physical GPU rendering pipelines, unpredictable network socket jitter, randomized test class execution ordering, and dirty shared state between containerized jobs. Senior engineers isolate the root cause by gathering telemetry—inspecting failure stack traces, emulator video recordings, and Logcat dumps—before categorizing the issue into one of four primary failure modes: uncoordinated concurrency race conditions, shared static state pollution across test suites, missing Android UI idling synchronization, or aggressive CI runner CPU throttling. Mitigations enforce hermetic test sandboxing, deterministic dispatcher injection, and quarantine protocols.

## Practical walkthrough (English)

Diagnosing CI flakiness and enforcing hermetic isolation in Gradle and Kotlin:
```kotlin
// 1. Gradle configuration enforcing test sandboxing and animation disabling
android {
    testOptions {
        execution 'ANDROIDX_TEST_ORCHESTRATOR'
        animationsDisabled = true
        unitTests {
            isIncludeAndroidResources = true
            all {
                // Fail immediately on leaked background threads
                testLogging {
                    events "passed", "skipped", "failed", "standardError"
                }
                maxParallelForks = (Runtime.runtime.availableProcessors() / 2).coerceAtLeast(1)
            }
        }
    }
}

// 2. Hermetic test isolating shared preferences and coroutine dispatchers
@OptIn(ExperimentalCoroutinesApi::class)
class UserSessionManagerTest {
    private val testDispatcher = StandardTestDispatcher()
    private lateinit var sharedPreferences: SharedPreferences
    private lateinit var sessionManager: UserSessionManager

    @Before
    fun setUp() {
        // Enforce ephemeral sandbox: clear storage before EVERY test run
        val context = ApplicationProvider.getApplicationContext<Context>()
        sharedPreferences = context.getSharedPreferences("test_session", Context.MODE_PRIVATE)
        sharedPreferences.edit().clear().commit()

        Dispatchers.setMain(testDispatcher)
        sessionManager = UserSessionManager(sharedPreferences, testDispatcher)
    }

    @After
    fun tearDown() {
        // Prevent state bleed into neighboring tests
        sharedPreferences.edit().clear().commit()
        Dispatchers.resetMain()
    }

    @Test
    fun login_successfulToken_persistsSessionDeterministically() = runTest(testDispatcher) {
        sessionManager.saveToken("jwt_secret_token_123")
        advanceUntilIdle() // Eliminates async timing race conditions

        assertEquals("jwt_secret_token_123", sessionManager.getToken())
    }
}
```

## Explanation in Arabic

اختبار ينجح دائماً على جهازك المحلي (Local Machine) ولكنه يفشل بشكل متقطع على خوادم الـ CI (Flaky Test). اشرح منهجية التشخيص والحل الجذري؟

1. لماذا تفشل الاختبارات على الـ CI بينما تنجح محلياً؟
   - **اختلاف قوة المعالجة والـ Resources**: حاسوبك يملك 8-16 Core قوية، بينما خادم الـ CI يعمل على Virtual Machine بـ 2 Cores فقط وعليها ضغط عالي؛ أي عملية تعتمد على سباق توقيت أو تأخير بسيط ستفشل على الـ CI!
   - **اختلاف المنطقة الزمنية والـ Locale**: جهازك مضبوط على `GMT+2` بينما الـ CI مضبوط على `UTC`؛ إذا كان الكود يتعامل مع تواريخ ونصوص دون تحديد الـ Locale يدوياً، ستفشل الـ Assertions!
   - **تشغيل الاختبارات بالتوازي (Parallel Execution)**: الـ CI يشغل أكثر من Fork في نفس الوقت، مما يسبب تنافساً على الـ Ports أو قواعد البيانات المشتركة.

2. منهجية التشخيص خطوة بخطوة (Triage Protocol):
   - **الخطوة 1: إعادة إنتاج المشكلة محلياً عبر الضغط المكثف (Stress Testing)**: تشغيل الاختبار 100 مرة متتالية محلياً:
     `./gradlew test --tests MyFlakyTest --repeat 100`.
   - **الخطوة 2: فحص مخرجات الـ CI**: فحص صور الشاشة وسجلات الـ Logcat وملفات الـ HTML reports الناتجة عن الفشل.
   - **الخطوة 3: تحديد السبب الجذري**: هل هو بسبب `Thread.sleep`؟ هل هو بسبب `Dispatchers.Main`؟ هل هو بسبب الـ Timezone؟

3. الحل الجذري والوقاية:
   - استبدال أي انتظار عشوائي بـ `advanceUntilIdle()` أو Compose synchronization.
   - تثبيت الـ Locale والـ Timezone في الـ Test Setup (`Locale.setDefault(Locale.US)`).
   - عزل الاختبار فوراً في `@FlakyTest` لمنع تعطيل الـ PRs لحين إصلاحه.

## Practical walkthrough

تثبيت المنطقة الزمنية واللغة في اختبارات الـ JVM وإعادة إنتاج الاختبار المتقلب محلياً:
```bash
# 1. أمر تشغيل الاختبار المتكرر 50 مرة محلياً لاكتشاف أخطاء التزامن الخفية:
./gradlew testDebugUnitTest --tests "com.example.OrderHistoryTest" --rerun-tasks
```

```kotlin
// 2. ضبط إعدادات الـ Locale والـ Timezone برمجياً في Test Rule لمنع تباين الـ CI:
class DeterministicLocaleRule : TestWatcher() {
    private val originalLocale = Locale.getDefault()
    private val originalTimeZone = TimeZone.getDefault()

    override fun starting(description: Description) {
        Locale.setDefault(Locale.US)
        TimeZone.setDefault(TimeZone.getTimeZone("UTC"))
    }

    override fun finished(description: Description) {
        Locale.setDefault(originalLocale)
        TimeZone.setDefault(originalTimeZone)
    }
}
```

## Why it matters and how it works

CI differs in CPU contention, scheduling, filesystem, locale and emulator version. A deterministic test should synchronize on observable conditions, isolate fixtures and clean up global state. If repeated runs expose an app race, fix production code and add a lower-level regression test.

## Worked example

A Compose test fails only when run after logout tests. Rerun the pair in the same shard; discover a singleton fake retained session state. Reset DI/test DB per case and assert teardown. If the flake instead tracks low CPU, replace a fixed sleep with semantics wait or fake-clock control.

## Trade-offs and decision criteria

Retrying can keep a pipeline usable temporarily but increases cost and hides risk; quarantine needs owner, expiry and equivalent release coverage for high-risk flows. Longer timeouts may help legitimate slow operations but are not a race fix.

## Failure modes

Blindly increasing sleep from 1 to 5 seconds reduces one symptom while preserving an app concurrency bug. Preserve first-failure logs/screenshot and test ordering evidence; do not delete a payment gate.

## Production perspective

Track flake rate, affected branches/devices and time-to-fix. CI publishes first-attempt failure even when retry passes, enabling prioritization.

## Interview answer — short

We triage CI-only flaky tests by analyzing artifacts: video recordings, thread dumps, and Logcat. We reproduce the issue locally by running tests in randomized order with throttled CPU cores. To mitigate, we isolate shared state by clearing databases and preferences between runs, eliminate timing races with TestDispatchers and IdlingResources, disable animations via testOptions, and use Android Test Orchestrator to execute tests in clean processes.

## Interview answer — structured

When a test passes on a developer laptop but fails intermittently on CI, senior engineers treat it as an urgent diagnostic priority rather than re-running the build until it passes.
The triage workflow begins with evidence collection.
We examine the CI test failure report, download the emulator screen recording, and cross-reference Logcat logs with the failure timestamp to observe the exact UI state and background thread activity at the moment of failure.
Next, we formulate and verify hypotheses.
One frequent cause is test order dependency, where an earlier test modifies a shared singleton, in-memory database, or SharedPreferences file without cleaning up, polluting the environment for subsequent tests.
We reproduce this locally by running Gradle test suites with randomized execution order using testLogging and parallel fork flags.
Another primary cause is thread scheduling starvation on low-power CI virtual machines, where background coroutines or RxJava streams execute slower than assertions expect, leading to assertion race conditions.
Mitigation follows a three-step protocol.
First, we enforce hermetic isolation by clearing all persistent storage and resetting static state in teardown methods or running tests via Android Test Orchestrator.
Second, we replace arbitrary delays with deterministic TestDispatchers and Compose synchronization.
Third, if a test cannot be fixed immediately, we quarantine it from the blocking presubmit gate to maintain team velocity while investigating.

## Interview answer — deep senior

Under the hood, CI flakiness is primarily an entropy problem caused by architectural impedance mismatches between the host JVM, the Android OS thread scheduler, and the containerized virtual runner.
Developer workstations typically boast high clock speed multi-core processors where background threads finish almost instantaneously, masking missing synchronization bugs.
In containerized CI environments (such as Docker on Kubernetes or GitHub Actions), CPU resources are throttled, meaning background threads in Dispatchers.Default or IO may be preempted for tens of milliseconds.
If a test relies on arbitrary timing or uncoordinated coroutine execution, the assertion thread evaluates before the worker thread finishes writing memory, causing intermittent assertion errors.
To guarantee deterministic execution, tests must replace real dispatchers with StandardTestDispatcher, which virtualizes time and couples scheduler advancement to advanceUntilIdle().
For instrumented UI tests, flakiness often originates from the Android Choreographer and RenderThread missing frames due to CI virtualization lag.
Configuring testOptions { animationsDisabled = true } modifies the global system settings (window_animation_scale, transition_animation_scale, and animator_duration_scale) to 0.0, eliminating frame interpolation waits.
Finally, executing via Android Test Orchestrator isolates each test into its own freshly initialized instrumentation APK process (invoking am instrument for every method), guaranteeing zero static variable leakage or cached DexClassLoader contamination across the test suite.

## How to answer in the interview

- **Why:** CI-only flakes may reveal shared state or a real race.
- **How:** capture shard, seed and logs, reproduce in order and fix the causal boundary.
- **Trade-off:** temporary quarantine versus coverage loss.
- **Failure case:** longer sleep only lowers failure frequency.
- **Production solution:** repeated original-shard run with owned quarantine policy.

## Deep-dive talking points

Prompt for first-failure artifact, same shard/order reproduction, race versus harness, owned quarantine.

## Follow-up questions

- **Interviewer:** "Why does Date formatting frequently cause tests to fail on CI?"
  **Answer:** "Because default SimpleDateFormat formats use the machine's local TimeZone and Locale; CI machines configured to UTC mismatch developer local timezones."

- **Interviewer:** "What is test quarantining?"
  **Answer:** "Moving an intermittently failing test into a separate non-blocking suite so it does not block pull requests while engineers investigate the root cause."

## Self-check rubric

Reproduce the CI-only failure with its shard/order/environment, preserve logs and seed, isolate shared state or timing, then verify repeated green runs. State when a retry masks rather than fixes the defect.

## References and reviewed-on date

- [Android testing guidance](https://developer.android.com/training/testing) — test environment and reliability.
- [Compose testing](https://developer.android.com/develop/ui/compose/testing) — synchronization APIs.

Technically reviewed against primary documentation on 2026-10-13.
