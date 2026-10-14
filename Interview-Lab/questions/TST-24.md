---
id: "TST-24"
question: "How do you gate PRs without creating an unreasonably slow pipeline?"
topic: "Testing, Quality & Reliability"
code: "TST"
group: "C"
phase: 4
priority: "P1"
order: 419
editorial_status: "reviewed"
---

# TST-24

## Original interview question

How do you gate PRs without creating an unreasonably slow pipeline?

## What the interviewer evaluates

- Fast PR gates versus slower risk-specific release checks.
- Parallelism, caching, ownership and signal quality.

## Explanation in Arabic

كيف تفرض بوابات اختبار صارمة (Gate PRs) على طلبات الدمج دون التسبب في بطء مفرط وتعطيل خط الإنتاج في الـ CI/CD؟

1. معضلة سرعة الـ CI مقابل دقة الاختبارات:
   - إذا قمت بتشغيل كل اختبارات الـ Unit والاختبارات البصرية والـ End-to-End على كل PR، سيستغرق الـ CI أكثر من 40 دقيقة لكل Commit!
   - هذا يصيب المطورين بالإحباط ويعطل إنتاجية الفريق بالكامل.

2. استراتيجية البوابات متعددة المراحل (Tiered PR Gating Pipeline):
   - **المرحلة 1: بوابة الـ PR السريعة (Fast PR Gate - أقل من 5 دقائق)**:
     * فحص التنسيق والجودة الساكنة (ktlint, detekt, Android Lint للملفات المعدلة فقط).
     * **اختبار الموديولات المتأثرة فقط (Affected Module Testing)**: باستخدام أدوات مثل `affected-module-detector`؛ إذا عدل المطور كود في موديول `:feature:profile`، يقوم Gradle باختبار هذا الموديول فقط متخطياً باقي الـ 40 موديول في المشروع!
     * تشغيل اختبارات الـ Unit السريعة على الـ JVM المحلي فقط.
   - **المرحلة 2: بوابة الدمج النهائي (Merge Queue / Pre-Merge Gate - 10-15 دقيقة)**:
     * تُنفذ بعد موافقة الـ Reviewers وقبل دمج الكود في الـ Main branch مباشرة.
     * تشغيل اختبارات التكامل وفحص توافق الـ APIs.
   - **المرحلة 3: مسار الاختبارات الثقيلة الليلي (Nightly Builds / Post-Merge)**:
     * تشغيل اختبارات الـ UI على المحاكيات (Compose / Espresso)، واختبارات لقطات الشاشة (Screenshot Tests)، والـ Macrobenchmarks بشكل مجمع في الليل دون تعطيل عمل المطورين اليومي.

## Practical walkthrough

تكوين اختبار الموديولات المتأثرة واستخدام Gradle Build Cache في GitHub Actions للوصول لسرعة < 5 دقائق:
```yaml
# جزء من ملف .github/workflows/pr-gate.yml السريع:
name: Fast PR Gate
on: [pull_request]

jobs:
  fast-validation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0 # لجلب سجل التغييرات واكتشاف الموديولات المعدلة

      - name: Setup Java Toolchain
        uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'

      - name: Setup Gradle Cache
        uses: gradle/actions/setup-gradle@v3

      # 1. تشغيل الفحص والاختبارات للموديولات المتأثرة فقط بـ PR Diff:
      - name: Run Affected Unit Tests Only
        run: ./gradlew runAffectedUnitTests -Paffected_module_detector.enable
```

## Why it matters and how it works

A pipeline is a dependency graph with cost and detection value. Run cheap high-signal checks early, parallelize independent jobs, cache safely, and avoid repeating identical builds. Separate PR merge gate from release gate with explicit required status checks.

## Worked example

PR changing ViewModel runs module JVM tests, static checks and compile; nightly runs emulator matrix; release candidate runs migration, POS hardware and payment-lost-response tests. If PR touches transaction code, trigger targeted backend idempotency contract gate immediately.

## Trade-offs and decision criteria

Selective tests reduce PR time but can miss hidden dependencies. Use module graph plus a broad scheduled suite and monitor escape rate. Caches speed builds but must not reuse signing secrets or invalid artifacts.

## Failure modes

Making flaky UI tests optional forever erodes trust; quarantined tests need owner/deadline. Conversely, serializing all device tests blocks every small docs PR for 40 minutes. Profile and shard intelligently.

## Production perspective

Publish per-stage duration, queue time, flaky rate and defect escapes. Review gates after incidents, and prevent merge when critical source/contract tests fail.

## Interview answer — short

Gate PRs under 5 minutes by testing only modules impacted by the PR diff via affected-module-detector, executing fast local JVM unit tests, leveraging remote Gradle build caching, and offloading heavy on-device UI and Macrobenchmark tests to merge queues or nightly builds.

## Interview answer — structured

Maintaining rigorous quality gates without degrading developer velocity requires a tiered pipeline strategy.

First, **Affected Module Testing**. Next, in a multi-module codebase (e.g. 50+ modules), running every test suite on every PR is wasteful. Use tools like **Affected Module Detector** to analyze Git diffs. If a PR touches only `:feature:checkout`, Gradle compiles and executes tests strictly for `:feature:checkout` and its direct dependents, skipping the other 45 modules.
**Tier 1: Fast PR Feedback (< 5 Minutes)**. Target: Fast block/unblock signal for developers.
Executes: Incremental static analysis (ktlint, detekt, modified-file Android Lint) and affected JVM unit tests. Powered by **Remote Gradle Build Cache**, downloading pre-compiled binaries for unaffected modules.
**Tier 2: Merge Queue Gate (10–15 Minutes)**. Runs when a PR is approved and queued for merge.
Executes full project compilation, integration contract tests, and release APK assembly smoke tests. **Tier 3: Asynchronous Nightly Suite**.
Finally, executes heavy, slow, or resource-intensive suites: full emulator instrumentation tests, visual screenshot diffs, and Macrobenchmark performance profiles.


## Interview answer — deep senior

From an infrastructure optimization and developer productivity perspective, pipeline velocity relies on caching and sharding.

First, a Remote Build Cache Hit Rate Optimization is a well-tuned remote build cache achieves an 80%+ cache hit rate. Tasks like `compileKotlin` and `lint` pull outputs instantly from the shared cache. Measure and monitor cache hit rates; a drop in cache hits indicates non-deterministic task inputs. Next, with Parallel Test Worker Allocation, configure `gradle.properties` on CI runners with `org.gradle.parallel=true` and allocate optimal test workers (`maxParallelForks = Runtime.runtime.availableProcessors() / 2`). Running independent module tests across parallel workers reduces execution wall-clock time by 60%.
Finally, with Fail-Fast Configuration, configure test runners with `--fail-fast`. If an assertion fails on test 3 out of 100, Gradle terminates execution immediately, providing instant error feedback to the author rather than wasting 10 minutes completing remaining tests.


## How to answer in the interview

- **Why:** slow PR checks delay feedback, but missing gates leak serious defects.
- **How:** keep fast compile/static/JVM checks, trigger targeted device/backend gates by risk.
- **Trade-off:** feedback latency versus coverage and CI cost.
- **Failure case:** changed-module selection misses a shared API dependent.
- **Production solution:** profile pipeline and require critical release invariants.

## Deep-dive talking points

Prompt for critical path, risk-triggered checks, cache correctness, flake governance and release gates.

## Follow-up questions

- **Interviewer:** "What is Affected Module Testing?"
  **Answer:** "A build optimization that analyzes Git commit diffs to compile and test only the specific modules changed by the PR and their downstream dependents."

- **Interviewer:** "What is the benefit of the --fail-fast flag in Gradle tests?"
  **Answer:** "It stops test execution immediately upon encountering the first test failure, saving CI runner time and accelerating developer feedback."

## Self-check rubric

Name a fast PR gate for compilation, focused JVM tests and static checks; place device/hardware suites on risk triggers or later stages; define a hard release gate for payment invariants and measure feedback time.

## References and reviewed-on date

- [Android CI guidance](https://developer.android.com/studio/build/building-cmdline) — command-line builds.
- [Gradle performance](https://docs.gradle.org/current/userguide/performance.html) — build optimization.

Technically reviewed against primary documentation on 2026-10-13.
