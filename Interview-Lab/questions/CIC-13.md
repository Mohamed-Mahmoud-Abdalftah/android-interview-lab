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

Manage flaky tests by addressing root causes (animations, unconfined coroutines, shared state), applying bounded retries in CI (max 1 retry) to prevent pipeline blockage, and enforcing a strict quarantine policy where flaky tests are moved out of blocking PR checks into non-blocking nightly suites until fixed.

## Interview answer — structured

Flaky tests undermine engineering trust and require an operational and technical mitigation policy.

First, **Root-Cause Remediation**. Next, replace asynchronous delays and `Thread.sleep` with Kotlin Coroutines' `runTest` and `advanceUntilIdle()`.
Enforce hermetic test environments: disable emulator animations via ADB, mock network layers with OkHttp MockWebServer, and use in-memory Room databases with strict `@Before`/`@After` teardowns. **Bounded Retries in CI**.
Implement the Gradle Test Retry plugin configured to retry failed tests at most once (`maxRetries = 1`). Retries act as a temporary velocity buffer to prevent blocking innocent PRs while logging telemetry. **Automated Quarantine Protocol**.
If a test passes only on retry, CI logs it as a flake metric. The test is immediately tagged (`@FlakyTest`) and quarantined from the blocking PR gate to a non-blocking scheduled suite. **SLA-Driven Resolution**.
Finally, a P1 technical debt ticket is automatically generated for the owning squad. If not resolved within a defined SLA (e.g. 5 days), the quarantined test is deleted to keep test suites lean and trustworthy.


## Interview answer — deep senior

From an engineering telemetry and cultural perspective, flaky test tracking must be automated.

First, with Flakiness Observability Dashboard, measure 'Flake Rate' across CI builds (total retries / total runs). If an organization's flake rate exceeds 1%, engineering leadership must treat test stabilization as a sprint blocker. Without visibility, engineers develop 'retry fatigue' where they blindly restart entire CI pipelines. Next, with De-flaking via Repeated Local Execution, when debugging a suspect test, run it 100 times in a loop locally using Gradle `--rerun-tasks`: `./gradlew test --tests 'com.app.SuspectTest' --repeat 100`. This reliably forces race conditions and coroutine leaks to surface.
Finally, with The Anti-Pattern of Infinite Retries, treating retries as a permanent fix rather than an alert mechanism creates dangerous compounding flakiness. Two flaky tests with 90% pass rates have an 81% combined pass rate; 10 such tests drop overall pipeline reliability below 35%, rendering CI useless.


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
