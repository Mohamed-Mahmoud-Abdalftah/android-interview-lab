---
id: "CIC-08"
question: "How do you configure PR checks for lint, static analysis, and tests?"
topic: "CI/CD, Git & Team Delivery"
code: "CIC"
group: "B"
phase: 4
priority: "P2"
order: 427
editorial_status: "reviewed"
---

# CIC-08

## Original interview question

How do you configure PR checks for lint, static analysis, and tests?

## What the interviewer evaluates

- Required PR checks and trust boundaries.
- Lint/static analysis/test coverage without an excessively slow gate.

## Concept and technical explanation

Pull Request verification gates enforce automated quality standards before code enters the shared mainline, operating on the fail-fast principle to maximize developer velocity:
- Tiered Quality Gate Strategy:
  - Formatting & Style Verification:
    - Executes deterministic linters like Spotless or ktlint. Confirms spacing, imports, and naming standards without semantic analysis overhead within seconds.
  - Static Code Analysis:
    - Runs Detekt to detect cyclomatic complexity, code smells, duplicate code, and custom architectural boundary rules (e.g., forbidding Android framework imports in domain modules).
  - Android Framework Linting:
    - Runs `./gradlew lintDebug`. Evaluates Android resource hygiene, security vulnerabilities, accessibility omissions, and API compatibility across minSdk and targetSdk versions.
  - Historical Debt Management via Baselines:
    - In mature codebases with legacy warnings, running Lint without baselines can produce hundreds of historical errors. Teams generate `lint-baseline.xml` and Detekt baseline files; the gate ignores preexisting issues but strictly breaks the build if a developer introduces even one net-new defect.
  - Host JVM Unit Testing:
    - Executes `./gradlew testDebugUnitTest` across affected modules, validating domain business logic, state machines, and repository contracts without emulator latency.
  - Unified Failure Reporting:
    - Pipelines execute checks with the `--continue` flag so all errors across modules are aggregated in a single run. Reports are ingested and published directly as SARIF annotations and inline PR comments.

## Practical walkthrough (English)

GitHub Actions workflow configuring fail-fast PR static analysis and unit testing:
```yaml
# .github/workflows/pr_checks.yml
name: PR Quality Verification

on:
  pull_request:
    branches: [ main, develop ]

concurrency:
  group: pr-${{ github.head_ref }}
  cancel-in-progress: true

jobs:
  static_analysis:
    name: Lint & Detekt
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: 'temurin', java-version: '17' }
      - uses: gradle/actions/setup-gradle@v3
        with: { cache-read-only: true }
      - name: Run Formatting & Static Analysis
        run: ./gradlew spotlessCheck detekt lintDebug --continue
      - name: Publish SARIF Lint Report
        if: always()
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: build/reports/detekt/detekt.sarif

  unit_tests:
    name: JVM Unit Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: 'temurin', java-version: '17' }
      - uses: gradle/actions/setup-gradle@v3
        with: { cache-read-only: true }
      - name: Run Host Unit Tests
        run: ./gradlew testDebugUnitTest --continue
      - name: Archive Test Results
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: unit-test-results
          path: '**/build/reports/tests/testDebugUnitTest/'
```

## Explanation in Arabic

كيف تقوم بإعداد وتأمين بوابات فحص الـ PRs (Pull Request Checks) للـ Lint والتحليل الساكن واختبارات الوحدة؟

1. استراتيجية بوابة الجودة للـ PR (PR Quality Gate):
   - الهدف الأساسي هو مبدأ **Fail-Fast**: إيقاف الكود المعيب في أسرع وقت ممكن (خلال دقيقة إلى 3 دقائق) قبل إهدار موارد السيرفر في بناء كامل أو اختبارات بطيئة.

2. المكونات الأساسية للبوابة:
   - **1. تنسيق الكود (Code Formatting)**: استخدام Spotless أو ktlint للتحقق من التزام الكود بمعايير Kotlin الرسمية (المسافات، الترتيب، الـ imports غير المستخدمة).
   - **2. التحليل الساكن (Static Analysis)**: تشغيل Detekt لكشف مشاكل تعقيد الكود (Cyclomatic Complexity)، والـ Code Smells، والـ Magic Numbers.
   - **3. أندرويد لنت (Android Lint)**: تشغيل `./gradlew lintDebug` للتحقق من مشاكل الـ Android SDK وموارد التطبيق والذاكرة واستخدام الـ APIs غير المتوافقة.
   - **4. اختبارات الوحدة السريعة**: تشغيل `./gradlew testDebugUnitTest` للتأكد من خلو منطق العمل من أي انحدار (Regressions).

3. إدارة الديون التقنية عبر الـ Baselines:
   - في المشاريع الكبيرة ذات الكود القديم، تشغيل Lint قد يُظهر 500 خطأ قديم! الحل ليس تجاهل Lint، بل توليد **Lint Baseline (`lint-baseline.xml`)** و **Detekt Baseline**؛ بحيث تتجاهل البوابة الأخطاء القديمة مؤقتاً، ولكن **ترفض الـ PR فوراً إذا أضاف المطور خطأً جديداً واحداً**.

## Practical walkthrough

إعداد Gradle وملف عمل GitHub Actions لتشغيل الفحوصات وإظهار التقارير مباشرة في الـ PR:
```yaml
# .github/workflows/pr_checks.yml
name: PR Static & Unit Checks
on:
  pull_request:
    branches: [ main, develop ]

jobs:
  quality_gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: 'temurin', java-version: '17' }
      - uses: gradle/actions/setup-gradle@v3

      # تشغيل الفحوصات مع استمرار التنفيذ لتجميع كل الأخطاء وتقديم تقرير موحد (--continue)
      - name: Run Linters and Tests
        run: ./gradlew spotlessCheck detekt lintDebug testDebugUnitTest --continue

      # رفع تقارير الفحص كـ Artifacts في حال فشل أي فحص لتسهيل الفحص
      - name: Upload Test and Lint Reports
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: pr-check-reports
          path: |
            **/build/reports/lint-results-debug.html
            **/build/reports/tests/testDebugUnitTest/
```

## Why it matters and how it works

Gradle tasks provide Android Lint/build/test outputs; CI status checks gate merge. Untrusted PR code should run with read-only tokens and no release secrets. Required checks should be deterministic and tied to a specific commit SHA.

## Worked example

PR modifies exported Activity: trigger manifest/security lint, unit tests and targeted instrumentation hostile-intent test. A formatting-only PR can skip hardware suite, while release candidate still runs broad device tests.

## Trade-offs and decision criteria

More checks improve coverage but can slow teams and increase flake noise. Stage fast checks first, parallelize, use affected-module selection with periodic full runs, and keep critical security gates mandatory.

## Failure modes

Allowing “green” from a previous commit while PR head changed is unsafe; require checks for current SHA. Blanket lint baseline can hide new findings. Separate existing debt from new regressions.

## Production perspective

CI publishes lint SARIF/report, test failures and changed-file context. Owners review suppressions, and release pipeline tests minified artifacts before signing.

## Interview answer — short

PR checks are configured as fail-fast parallel pipelines combining Spotless for formatting, Detekt for static complexity rules, Android Lint with baselines for SDK and resource hygiene, and testDebugUnitTest for business logic. Running with the continue flag aggregates all defects in a single pass, publishing inline PR annotations so developers receive comprehensive feedback within minutes.

## Interview answer — structured

Configuring Pull Request checks requires balancing thorough regression prevention against developer iteration velocity.
In high-performing engineering teams, we structure PR validation into parallel, fail-fast jobs. The first tier runs Spotless or ktlint to enforce code formatting instantly. Alongside it, Detekt executes static analysis rules enforcing cyclomatic complexity thresholds and preventing architectural layer violations.
For platform correctness, we run Android Lint on debug variants. To prevent historical warnings from blocking new feature work in mature codebases, we enforce baseline files like lint-baseline.xml; this ensures the pipeline only breaks when net-new violations are introduced. Concurrently, host JVM unit tests run across all modified modules using testDebugUnitTest.
By executing Gradle tasks with the continue flag and leveraging GitHub Actions concurrency cancellation, existing runs on outdated commits are terminated immediately when a developer pushes a new commit. Build summaries and SARIF annotations post failure reports directly into the pull request review interface, providing complete actionable feedback in under five minutes.

## Interview answer — deep senior

From a release engineering and developer productivity perspective, pull request checks are the foundational filter protecting mainline stability and reducing code review cycle time.
When designing an enterprise-scale PR verification pipeline, the primary architectural trap is attempting to run exhaustive test suites or full instrumentation emulators on every commit. This bloats queue times to half an hour and degrades team velocity. Instead, we divide verification into fast presubmit gates on PRs and exhaustive post-merge nightly runs. Presubmit checks focus exclusively on deterministic, low-overhead tasks: bytecode and source formatting with Spotless, static architecture governance with Detekt, platform resource verification with Android Lint, and JVM unit tests.
Managing technical debt in large legacy codebases requires disciplined baseline governance. Simply turning on Lint with fail-on-warning will paralyze development by surfacing thousands of legacy warnings. We establish baseline files that capture historical debt at a specific point in time, configuring CI to fail only on regression deltas. We then schedule automated recurring maintenance tasks to ratcheting down baselines incrementally over time.
To optimize CI infrastructure costs and runtimes, we combine Gradle configuration caching with affected-module detection tools. If a pull request touches only the profile feature module, our pipeline skips compiling unaffected payments and authentication modules entirely. Furthermore, we mandate pull request concurrency controls; pushing a new commit immediately cancels obsolete runner jobs, freeing up CI runners and ensuring that engineering feedback loops remain snappy, reliable, and friction-free.

## How to answer in the interview

- **Why:** review needs reliable failure signals.
- **How:** gate compile, lint, tests and risk-specific checks.
- **Trade-off:** CI latency versus scope of required checks.
- **Failure case:** flaky retry masks a real race.
- **Production solution:** protect branch and publish diagnostic artifacts.

## Deep-dive talking points

Prompt for head SHA, branch protection, baseline debt, affected tests and untrusted job permissions.

## Follow-up questions

- **Interviewer:** "What is the purpose of the `--continue` flag in Gradle CI commands?"
  **Answer:** "It instructs Gradle to execute every scheduled task even if an earlier task fails, aggregating all errors in a single CI run."

- **Interviewer:** "How do baseline files help manage tech debt in Android Lint?"
  **Answer:** "They record existing violations so CI only fails if a developer introduces new violations or modifies lines containing old ones."

## Self-check rubric

Specify required PR checks, branch protection and artifact identity; run lint/static analysis and focused tests before merge; explain where emulator and release-only tests fit without hiding failures.

## References and reviewed-on date

- [Android Lint](https://developer.android.com/studio/write/lint) — static checks.
- [Gradle command-line builds](https://docs.gradle.org/current/userguide/command_line_interface.html) — task execution.

Technically reviewed against primary documentation on 2026-10-13.
