---
id: "CIC-13"
question: "How do you deal with flaky tests, retries, and quarantine policies?"
topic: "CI/CD, Git & Team Delivery"
code: "CIC"
group: "B"
phase: 4
priority: "P2"
order: 432
editorial_status: "reviewed"
---

# CIC-13

## Original interview question

How do you deal with flaky tests, retries, and quarantine policies?

## What the interviewer evaluates

- Flake classification, visible retries and bounded quarantine.
- Maintaining release coverage for critical flows.

## Concept and technical explanation

Flaky tests—tests that exhibit non-deterministic pass/fail outcomes on identical commit SHAs—erode developer trust, block merge queues, and waste CI compute:
- Root Causes of Test Flakiness:
  - Timing and Asynchrony: Using arbitrary delays like `Thread.sleep()` instead of coroutine virtual time (`StandardTestDispatcher`, `runTest`, Turbine) or Espresso Idling Resources.
  - Shared State and Side Effects: Static singletons, in-memory databases, or preferences leaking state between independent test cases.
  - Main Thread Starvation: Resource contention on constrained CI runners causing animation or layout timeouts.
- Bounded Retries Architecture:
  - Using tools like the Gradle Test Retry Plugin (`org.gradle.test-retry`).
  - Strict Operational Rule: Retries must be bounded and monitored (e.g., `maxRetries = 1`, `maxFailures = 5`).
  - Retries prevent a single intermittent network blip or race condition from failing an entire build, but must NEVER be allowed to silently mask defects. CI logs must flag tests that passed only on retry.
- Test Quarantine Policy:
  - When a test is identified as flaky, it is immediately decorated with a `@FlakyTest` or `@Quarantined` annotation.
  - The primary pull request pipeline filters out quarantined tests, preventing them from blocking developer merges.
  - Quarantined tests are executed in scheduled non-blocking nightly observability pipelines to collect statistical flake rates.
- Flaky Test SLA & Engineering Budget:
  - A quarantined test is treated as a P1 bug assigned to the owning feature team.
  - Strict SLA: The test must be diagnosed and resolved with deterministic synchronization within one sprint, or permanently deleted if it provides insufficient signal. Indefinite quarantine is strictly forbidden.

## Practical walkthrough (English)

Gradle test retry plugin configuration and quarantine test filtering:
```kotlin
// app/build.gradle.kts
plugins {
    id("com.android.application")
    id("org.gradle.test-retry") version "1.5.8"
}

tasks.withType<Test>().configureEach {
    retry {
        // Only retry on CI runners
        val isCi = System.getenv("CI") == "true"
        maxRetries.set(if (isCi) 1 else 0)
        maxFailures.set(5) // Stop build if 5 tests fail to prevent retry runaway
        failOnPassedAfterRetry.set(false) // Allow build to pass, but record flake
    }

    // Filter out quarantined tests on PR builds
    useJUnitPlatform {
        if (project.hasProperty("excludeQuarantine")) {
            excludeTags("Quarantine")
        }
    }
}
```

```kotlin
// Example quarantined test file
@Tag("Quarantine")
@Test
fun testFlakyCheckoutAnimationFlow() = runTest {
    // Flagged for investigation due to CI race condition on runner VMs
}
```

```yaml
# .github/workflows/pr_checks.yml
- name: Run Unit Tests (Excluding Quarantined)
  run: ./gradlew testDebugUnitTest -PexcludeQuarantine
```

## Explanation in Arabic

كيف تتعامل مع الاختبارات المتقلبة (Flaky Tests)، وما هي سياسات إعادة المحاولة (Retries) والعزل (Quarantine) في الـ CI؟

1. ما هو الـ Flaky Test وما خطورته؟
   - هو اختبار يعطي نتائج متضاربة (ينجح أحياناً ويفشل أحياناً) لنفس الكود ونفس البيئة دون أي تغيير.
   - خطورته: يدمر ثقة المطورين في الـ CI، ويجعل الفريق يتجاهل فشل الاختبارات ("مجرد فليك، أعد تشغيل الـ Pipeline!")، مما يؤدي لتمرير كوارث حقيقية للإنتاج.

2. الأسباب التقنية للـ Flakiness في أندرويد:
   - الاعتماد على `Thread.sleep` أو أوقات انتظار غير محددة بدلاً من `IdlingResource` أو `advanceUntilIdle()` في الـ Coroutines.
   - الرسوم المتحركة (Animations) النشطة في المحاكي أثناء اختبارات الـ UI.
   - الاعتماد على شبكة إنترنت حقيقية أو خوادم خارجية غير مستقرة بدلاً من MockWebServer.
   - تسريب البيانات (State Leak) بين الاختبارات في قواعد بيانات Room المشتركة.

3. استراتيجية العزل وإعادة المحاولة (Quarantine & Retry Policy):
   - **إعادة المحاولة المحدودة (Bounded Retries)**: السماح لـ Gradle بإعادة تشغيل الاختبار الفاشل مرة أو مرتين كحد أقصى (`maxRetries = 1`) لمنع تعطيل الـ PRs العاجلة.
   - **سياسة العزل الفوري (Quarantine)**: أي اختبار يفشل بشكل متقلب يتم تمييزه بـ `@FlakyTest`، ونقله فوراً من مسار فحص الـ PRs إلى مسار ليلي منعزل (Non-blocking Nightly Suite).
   - **تذكرة عمل ذات أولوية (P1 Bug)**: فتح Issue فوري للفريق المسؤول، مع إعطاء مهلة محددة (SLA: مثلاً أسبوع) لإصلاحه أو حذفه نهائياً من المشروع.

## Practical walkthrough

إعداد Gradle Test Retry وعزل الاختبارات المشكوك فيها عبر JUnit Categories:
```kotlin
// app/build.gradle.kts
plugins {
    id("org.gradle.test-retry") version "1.5.8"
}

tasks.withType<Test>().configureEach {
    retry {
        // إعادة المحاولة فقط في بيئة الـ CI وبحد أقصى محاولة واحدة:
        maxRetries.set(if (System.getenv("CI") == "true") 1 else 0)
        maxFailures.set(5) // إذا كان هناك أكثر من 5 أخطاء، أوقف البناء ولا تعيد المحاولة (فشل حقيقي)
        failOnPassedAfterRetry.set(false) // يسمح بالنجاح المؤقت مع تسجيل الاختبار المتقلب
    }

    // استبعاد الاختبارات المعزولة (@Category(FlakyTest::class)) من فحص الـ PRs:
    if (project.hasProperty("excludeFlaky")) {
        useJUnit {
            excludeCategories("com.example.testing.FlakyTestCategory")
        }
    }
}
```

## Why it matters and how it works

CI retries can distinguish intermittent from deterministic failure but cannot identify cause alone. Quarantining removes a signal from required checks, so it needs risk assessment. Track flake rate per test, shard and device; preserve first-failure artifacts.

## Worked example

Compose test fails 2% on CI. Keep first screenshot/log, run on same emulator image and shard order, find a fixed sleep around network. Replace with fake response gate and semantics wait; remove retry after repeated clean runs.

## Trade-offs and decision criteria

Immediate quarantine may unblock work but increases escape risk. A small retry budget can reduce random infrastructure noise while adding latency. Critical financial invariants need lower-level deterministic tests during UI repair.

## Failure modes

A race in app code is mislabeled “test flake” and ignored. Analyze state traces and process timing before changing timeouts. Deleting the test without equivalent coverage is an unrecorded release risk.

## Production perspective

Weekly flake dashboard assigns owners; quarantine expiry fails or escalates. CI stores original failure even after retry success and trends test health.

## Interview answer — short

Address flaky tests by combining bounded retries via the Gradle Test Retry plugin, an immediate quarantine policy using custom test tags to unblock PR merges, and routing quarantined tests to nightly observability suites. Enforce a strict one-sprint SLA to fix async timing issues or delete non-viable tests to prevent eroding suite credibility.

## Interview answer — structured

Managing flaky tests requires balancing immediate developer productivity against long-term test suite reliability.
The primary causes of flakiness in Android are race conditions in asynchronous coroutines, animation timing mismatches, and shared static state. To protect developer momentum on pull requests, we configure the Gradle Test Retry plugin with bounded retries, allowing a maximum of one retry per failing test while capping total failures at five to prevent runaway build loops.
However, retries merely buy time; they do not solve flakiness. When a test flakes repeatedly, we apply a Quarantine annotation to immediately exclude it from the PR blocking gate. This unblocks the team while routing the test into a scheduled, non-blocking nightly pipeline that tracks pass-fail statistics.
Critically, we enforce a strict team SLA: quarantined tests are treated as high-priority bugs. The owning team has one sprint to refactor the test using deterministic tools like Turbine and virtual test dispatchers, or delete the test entirely if its value does not justify the maintenance burden.

## Interview answer — deep senior

From a quality engineering and team operations perspective, flaky tests are cancer to software delivery. When tests fail unpredictably on identical code, developers lose faith in the entire test suite, ignoring legitimate regression failures and resorting to blind retries.
To maintain high velocity without surrendering quality, we implement a three-tiered defense: bounded mitigation, quarantine isolation, and root-cause remediation. First, at the build level, we configure the Gradle Test Retry plugin. Crucially, retries must be strictly bounded to a single attempt. Unbounded retries turn CI pipelines into a game of roulette and dramatically inflate runner costs. Furthermore, every test that passes only after a retry is logged and reported to an observability dashboard as a flake event.
Second, tests exhibiting chronic flakiness are immediately quarantined using JUnit tags. Pull request pipelines pass a property excluding the Quarantine tag, instantly removing the blocker from developer queues. Quarantined tests do not disappear; they run in continuous nightly runs where they are subjected to stress loops of fifty consecutive executions to isolate race conditions.
Finally, quarantine governance requires an ironclad SLA. A quarantined test is an open technical debt ticket. We give feature teams a one-sprint deadline to either repair the test using deterministic virtual clocks, proper TestScope synchronization, and isolated state, or permanently remove it. Allowing tests to languish in quarantine indefinitely normalizes bad testing hygiene and undermines organizational discipline.

## How to answer in the interview

- **Why:** unreliable tests erode release confidence.
- **How:** capture first failure and classify race/environment.
- **Trade-off:** temporary retry versus trusted signal.
- **Failure case:** quarantine silently removes payment coverage.
- **Production solution:** owner, deadline and repeated verification.

## Deep-dive talking points

Prompt for first failure, same-environment reproduction, app race, quarantine owner.

## Follow-up questions

- **Interviewer:** "Why should tests that pass only after a retry still be flagged as failures in metrics?"
  **Answer:** "Because masked flakes degrade into persistent failures; recording them in metrics ensures visibility and accountability before they completely break the pipeline."

- **Interviewer:** "How do you reproduce a race condition in a suspected flaky test locally?"
  **Answer:** "Run the specific test repeatedly in a loop (e.g. 100 times) using test runner repeat flags to expose timing variations."

## Self-check rubric

Classify a flaky test by ordering, timing, shared state or environment; collect seed/log evidence, assign owner and expiry for quarantine, and explain why blind retries cannot prove a release safe.

## References and reviewed-on date

- [Android testing guidance](https://developer.android.com/training/testing) — reliable test practice.
- [Gradle test execution](https://docs.gradle.org/current/userguide/java_testing.html) — test reporting.

Technically reviewed against primary documentation on 2026-10-13.
