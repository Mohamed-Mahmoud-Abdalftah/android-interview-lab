---
id: "TST-15"
question: "How do you reduce flaky UI tests and control scheduling?"
topic: "Testing, Quality & Reliability"
code: "TST"
group: "B"
phase: 4
priority: "P1"
order: 410
editorial_status: "reviewed"
---

# TST-15

## Original interview question

How do you reduce flaky UI tests and control scheduling?

## What the interviewer evaluates

- Root causes of flakiness rather than blanket retries.
- Scheduler, network, state isolation and device control.

## Explanation in Arabic

كيف تقضي على الاختبارات المتقلبة (Flaky UI Tests) وتتحكم في الجدولة الزمنية وتزامن العمليات غير المتزامنة؟

1. ما هو الـ Flaky Test ولماذا هو عدو الـ CI/CD الأول؟
   - هو الاختبار الذي ينجح أحياناً ويفشل أحياناً أخرى على نفس الكود بالضبط دون أي تغيير!
   - يدمر ثقة المطورين في الـ CI، ويؤخر دمج الـ PRs، ويخفي الأخطاء الحقيقية.

2. الأسباب الجذرية للـ Flakiness في اختبارات أندرويد:
   - **استخدام `Thread.sleep()`**: جريمة برمجية! إذا كان جهاز الـ CI بطيئاً، سينتهي الـ Sleep قبل اكتمال العملية ويفشل الاختبار.
   - **حركات الواجهة والـ Animations**: حركات التلاشي والانتقالات تؤخر ظهور العناصر. **الحل**: تعطيل جميع حركات النظام في المحاكي قبل بدء الاختبارات.
   - **التنافس الشبكي (Network Timing Races)**: الاتصال بسيرفرات حقيقية. **الحل**: استخدام MockWebServer محلي أو Fakes.

3. أدوات التحكم والمزامنة الحتمية:
   - **في Compose**: استخدام `composeTestRule.mainClock.autoAdvance = false` للتحكم في تقدم الإطارات يدوياً.
   - **في Espresso**: استخدام `CountingIdlingResource` أو تحويل الكود إلى Coroutines يتم التحكم بها عبر `StandardTestDispatcher`.
   - **Android Test Orchestrator**: تشغيل كل اختبار في Process مستقلة تماماً ومسح بيانات التطبيق بين الاختبارات لمنع تراكم الحالة.

## Practical walkthrough

تعطيل Animations النظام برمجياً عبر ADB واستخدام IdlingResource أو MainClock في Compose:
```bash
# 1. أوامر إجبارية في CI لتعطيل الـ Animations في المحاكي ومنع الـ Flakiness:
adb shell settings put global window_animation_scale 0
adb shell settings put global transition_animation_scale 0
adb shell settings put global animator_duration_scale 0
```

```kotlin
// 2. التحكم الحتمي في ساعة Compose لمنع سباقات التوقيت مع الأنيميشن:
@Test
fun testAnimatedBannerAppearsDeterministically() {
    // إيقاف التقدم التلقائي لساعة الـ Frame Clock:
    composeTestRule.mainClock.autoAdvance = false

    composeTestRule.setContent {
        AnimatedBannerScreen()
    }

    // التقدم بالساعة 500ms حتمياً لإكمال الأنيميشن بدقة:
    composeTestRule.mainClock.advanceTimeBy(500)

    composeTestRule.onNodeWithText("Welcome Back")
        .assertIsDisplayed()
}
```

## Why it matters and how it works

Android/Compose test frameworks can synchronize with UI work they know about, but custom background work and external I/O need explicit idling or controlled dependencies. Isolate test data and reset device state. Reproduce with repeated focused runs and capture timeline.

## Worked example

A checkout UI test fails once in 30 runs because network response arrives after fixed 500 ms sleep. Replace live backend with a controllable fake, wait for the Loading node then release result, and assert Approved or Unknown. Use Compose test clock for animation, not wall time.

## Trade-offs and decision criteria

Fakes improve determinism but may hide integration faults; keep separate contract/E2E coverage. Longer timeouts reduce false failures but slow detection. Quarantine only with owner, deadline and release-risk decision.

## Failure modes

Automatic rerun that turns red into green conceals a race in production code. Record original failure, investigate scheduler/thread traces and shared test order. Do not delete a flaky security/payment test without replacement.

## Production perspective

CI stores screenshots, logs and test seed/attempt IDs with redaction. Track flake rate by test and device, and address highest-cost or highest-risk cases first.

## Interview answer — short

Eliminate UI flakiness by banning Thread.sleep(), disabling system animations on test devices, mocking external network boundaries with MockWebServer, controlling Compose clocks deterministically via mainClock.autoAdvance = false, and running tests in isolated processes via Android Test Orchestrator.

## Interview answer — structured

Flaky UI tests degrade engineering trust and stall deployment pipelines. Eliminating flakiness requires controlling concurrency, animation timing, and environment isolation:

1. **Ban Arbitrary Sleeps**:
   - Never write `Thread.sleep(2000)`. Use synchronization hooks: in Espresso, register `CountingIdlingResource`; in Compose, rely on native auto-synchronization or manually advance `composeTestRule.mainClock`.

2. **Disable System Animations on CI Devices**:
   - UI tests click coordinates based on settled layout trees. If a window transition or fade animation is midway, clicks miss targets. Execute shell commands on CI emulators to disable all animation scales (`window_animation_scale 0`, `transition_animation_scale 0`, `animator_duration_scale 0`).

3. **Hermetic Test Environments**:
   - Flakiness often mirrors network flakiness. Mock external HTTP endpoints using `MockWebServer` running on `localhost`. Isolate storage by resetting test databases between tests.

4. **Android Test Orchestrator**:
   - Enable `execution 'ANDROIDX_TEST_ORCHESTRATOR'`. Orchestrator launches each test method in its own fresh `Instrumentation` process, clearing application memory, static singletons, and SQLite files between runs.

## Interview answer — deep senior

From an infrastructure resilience perspective, managing flaky tests at scale requires quarantine policies and sharding:

1. **Automated Quarantine Pipelines**: Implement CI tooling (e.g., Flank or Test Grid) that tracks test pass rates over 14 days. If a test fails intermittently without code changes, automatically flag it as `@FlakyTest`, quarantine it into a non-blocking diagnostic suite, and alert the owning team.

2. **Targeted Polling Matchers (`waitUntil`)**: When awaiting complex asynchronous conditions in Compose, use explicit condition timeouts:
   ```kotlin
   composeTestRule.waitUntil(timeoutMillis = 5000) {
       composeTestRule.onAllNodesWithText("Ready").fetchSemanticsNodes().isNotEmpty()
   }
   ```
   This polls at frame boundaries, proceeding immediately when the condition is satisfied rather than waiting for worst-case time ceilings.

3. **Device Matrix Sharding**: Shard instrumentation suites across 4–8 parallel emulators in CI. Sharding keeps individual runner sessions under 5 minutes, preventing emulator memory bloat and thermal throttling that cause late-suite test timeouts.

## How to answer in the interview

- **Why:** flaky green results undermine trust in the release gate.
- **How:** reproduce order/seed, replace sleeps with controlled fake and rerun original shard.
- **Trade-off:** quarantine can unblock work but leaves coverage debt.
- **Failure case:** retry masks an app race or shared singleton state.
- **Production solution:** owner, expiry, replacement gate and repeated verification.

## Deep-dive talking points

Prompt for first-failure evidence, synchronization, state isolation, bounded quarantine and app race.

## Follow-up questions

- **Interviewer:** "What does Android Test Orchestrator do?"
  **Answer:** "It runs each test in its own dedicated Android instrumentation process, ensuring zero state or static memory leaks between test executions."

- **Interviewer:** "How does composeTestRule.waitUntil() differ from Thread.sleep()?"
  **Answer:** "waitUntil polls a condition predicate on every frame clock tick and unblocks immediately when true, avoiding wasted time and race conditions."

## Self-check rubric

Reproduce the order-dependent or timing flake, remove wall-clock sleeps, control the fake response and Compose clock, and rerun the affected shard. Quarantine only with an owner, evidence and expiry.

## References and reviewed-on date

- [Android test reliability](https://developer.android.com/training/testing) — official testing practices.
- [Compose testing](https://developer.android.com/develop/ui/compose/testing) — clock/synchronization APIs.

Technically reviewed against primary documentation on 2026-10-13.
