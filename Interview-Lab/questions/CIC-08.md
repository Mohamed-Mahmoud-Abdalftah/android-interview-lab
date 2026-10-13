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

Configure PR checks by chaining Spotless/ktlint for formatting, Detekt for static analysis, Android Lint with baseline files for framework checks, and testDebugUnitTest for local JVM unit tests. Run with the --continue flag in parallel jobs to fail fast while aggregating all errors into PR comments or build summaries.

## Interview answer — structured

A production PR quality gate is designed to enforce strict code standards without crippling developer velocity:

1. **Fail-Fast Pipeline Structure**:
   - Separate lightweight checks into parallel jobs: (a) formatting and static analysis (Spotless/ktlint, Detekt), and (b) local JVM unit tests (`testDebugUnitTest`). This provides feedback within 2–3 minutes.

2. **Baseline Management for Legacy Projects**:
   - Enforce zero-tolerance for new issues in legacy codebases by generating Lint and Detekt baselines (`lintOptions { baseline = file("lint-baseline.xml") }`). Existing issues are recorded and grandfathered in, while newly introduced violations fail the PR build immediately.

3. **Inline PR Feedback & Actionable Reporting**:
   - Integrate tools like Danger or reviewdog to parse Lint XML reports and publish inline GitHub PR comments directly on offending lines, eliminating the need for engineers to download raw CI log files.

4. **Execution Resilience**:
   - Use the `--continue` Gradle flag so the runner executes all static checks in a single pass, reporting formatting, lint, and unit test failures simultaneously rather than forcing repeated CI runs for sequential errors.

## Interview answer — deep senior

From an engineering governance and CI infrastructure standpoint, PR checks require careful caching and branch protection rules:

1. **Branch Protection Enforcement**: In GitHub or GitLab settings, mandate 'Require status checks to pass before merging' and 'Require branches to be up to date before merging'. This prevents race conditions where two PRs pass CI independently but break when merged together.

2. **Targeted Subproject Execution**: In a multi-module architecture of 80+ modules, running `./gradlew check` across the entire project on every 3-line PR wastes massive compute. Teams configure path filters or tools like Gradle's configuration-cache and affected-module-detector to run tests only on modules impacted by the PR's git diff.

3. **Remote Build Cache**: Enable Gradle's remote build cache (`org.gradle.caching=true`) backed by an S3/GCS or Develocity instance. If an engineer refactors a leaf module, upstream modules are retrieved from cache with `FROM-CACHE` status in seconds.

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
