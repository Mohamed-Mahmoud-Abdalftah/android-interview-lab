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

## Concept and technical explanation

Engineering a high-throughput Pull Request (PR) gating pipeline requires balancing rapid developer feedback loops (targeting sub-ten-minute validation) against comprehensive system quality assurances. Running exhaustive end-to-end emulator matrices and full UI regression suites on every commit introduces severe CI congestion, degrades developer velocity, and encourages premature merge bypasses. Senior engineering architectures resolve this tension by structuring validation into a multi-tiered testing pyramid: Tier 1 executes in fast PR presubmit gates, leveraging Git diffs and Gradle affected module detection to run only static analysis (ktlint, Detekt, Android Lint) and fast JVM unit/Robolectric tests against modified code. Expensive Tier 2 validations—including multi-device instrumented emulator suites, Macrobenchmark startup benchmarks, screenshot regression comparisons, and security vulnerability scans—are offloaded to asynchronous post-merge queues, nightly batches, or release-candidate triggers, accelerated via distributed remote build caching.

## Practical walkthrough (English)

Configuring fast affected module detection and Gradle remote build caching:
```kotlin
// 1. Enabling remote build caching and configuration caching in settings.gradle.kts
buildCache {
    local {
        isEnabled = true
        removeUnusedEntriesAfterDays = 7
    }
    remote<HttpBuildCache> {
        url = uri("https://gradle-cache.company.internal/cache/")
        isPush = System.getenv("CI_MASTER_BUILD") == "true"
        credentials {
            username = System.getenv("CACHE_USER")
            password = System.getenv("CACHE_PASSWORD")
        }
    }
}

// 2. Fast PR gating workflow command in CI pipeline
// Runs lint and JVM tests ONLY on modules affected by the current pull request branch
// ./gradlew checkAffected -PtargetBranch=origin/main --configuration-cache --parallel

// 3. GitHub Actions PR workflow tiered structure
/*
name: PR Fast Gate
on: [pull_request]

jobs:
  fast-checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'
      # Executes fast linting and unit tests on affected modules in parallel (~4-6 minutes)
      - name: Run Affected Module Tests
        run: ./gradlew testDebugUnitTest ktlintCheck --parallel --build-cache
*/
```

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

We gate PRs fast by structuring a multi-tiered validation pipeline. Presubmit PR gates run in under 8 minutes by executing only fast checks on affected modules: linting, ktlint, and JVM unit tests with Gradle build caching and configuration caching. Slow tests—such as instrumented emulator runs, screenshot tests, and Macrobenchmarks—are offloaded to async merge queues or nightly builds, ensuring developers get rapid feedback without sacrificing quality.

## Interview answer — structured

Designing an effective pull request gating pipeline is an optimization problem between feedback latency and release safety.
If a PR pipeline takes 45 minutes to run, developer productivity grinds to a halt, context switching skyrockets, and engineering teams are tempted to bypass checks.
The industry gold standard is a tiered gating pyramid.
In Tier 1 (the synchronous PR presubmit gate), the goal is strict sub-ten-minute execution.
We achieve this by testing only what changed.
Using Git change detection tools (like Dropbox's Focus or Slack's affected-module-detector), Gradle identifies the delta between the PR branch and main, executing tasks exclusively on modified modules and their direct dependents while skipping unaffected library modules.
Presubmit gates are strictly confined to fast static analysis (Android Lint, Detekt, ktlint) and in-memory JVM unit and Robolectric tests.
Heavy validations belong in Tier 2 and Tier 3.
Full-suite instrumented emulator tests, Roborazzi screenshot comparisons, and Macrobenchmark performance tests run asynchronously in a post-merge queue or nightly builds.
If a nightly build flags a regression, an automated revert bot or on-call engineer handles it immediately.
Underpinning this entire pipeline is infrastructure optimization: enabling Gradle's remote HTTP build cache, persistent configuration cache, and parallel test task workers across CI runner containers.

## Interview answer — deep senior

Under the hood, pipeline acceleration relies on Gradle's Directed Acyclic Graph (DAG) task execution engine, input/output hash fingerprinting, and distributed cache serialization.
When Gradle processes a task, it computes a composite SHA-256 fingerprint from the task inputs—source files, classpath dependencies, compiler versions, and environment variables.
With remote HTTP build caching enabled, Gradle queries the remote cache server; if a matching key exists, it downloads the pre-compiled class jars and test results, marking the task as FROM-CACHE and skipping compilation in milliseconds.
Configuration caching further accelerates runs by serializing the evaluated project model DAG to disk, bypassing the entire Groovy/Kotlin script evaluation phase on subsequent executions.
To isolate PR changes, affected module detection algorithms compute the reverse dependency tree: if a developer modifies a leaf feature module, only that feature's unit tests run; if a core shared module changes, the tool intelligently scales test coverage to all dependent consumers.
For instrumented tests that must run before merge, senior teams utilize emulator sharding (such as Flank or Marathon) across 20 concurrent cloud virtual devices, parallelizing a 60-minute test suite into 3 minutes.
Finally, predictive test selection algorithms monitor historical failure correlations, running only the top 10% of tests historically likely to catch bugs for a specific file diff, guaranteeing both peak developer velocity and rock-solid code health.

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
