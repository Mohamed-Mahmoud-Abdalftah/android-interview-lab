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

نضبط branch protection إن PR ما يندمجش إلا بعد compile، Android Lint، static analysis المختارة، JVM tests وcontract tests. Device tests حسب affected area أو release gate. كل check يطلع report واضح ويفشل عند threshold متفق عليه. مش نخلط warning جديد مع baseline debt؛ baseline مؤقتة لها owner وخطة تقليل.

## Practical walkthrough

PR checks لازم ترتبط بمخاطر التغيير: compile للـvariants الأساسية، Android Lint، static analysis، unit tests، contract tests، ومع feature حساس نفّذ release-like test أو emulator. Branch protection يمنع الدمج قبل required checks ومراجعة مستقلة. لا تجعل PR من fork يستخدم signing secrets. فرّق بين test فشل بسبب code وemulator تعطل؛ أظهر artifacts والlogs وخلي owner واضح. التغطية المئوية وحدها مش بوابة جودة.

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

“I require compile, lint/static checks, unit and contract tests on the current PR SHA, with targeted device checks for risky changes. Secrets stay out of untrusted PR jobs.”

## Interview answer — structured

“I configure branch protection around named, reliable status checks. Fast Gradle compile, Android Lint, static analysis, JVM and contract tests run on PRs; targeted instrumentation runs when platform behavior changes. Reports show actionable findings, and baselines for old debt do not excuse new issues. Untrusted fork code gets read-only permissions and no signing material. Broader device/hardware suites gate release. ”

## Interview answer — deep senior

“I make PR checks a contract rather than a list of green badges. The baseline compiles relevant variants, runs Android Lint/static analysis and fast JVM tests, and validates content or API contracts that can break other modules. I add targeted emulator tests when the change touches lifecycle, Room or UI semantics, and a minified release-like check for manifest, R8 or SDK integration risk. Branch protection requires those checks on the exact head or merge commit and prevents bypass except through an auditable process. A fork PR runs untrusted code with minimal token permissions and no signing secrets. To keep feedback useful, I parallelize independent checks, publish test reports and identify a check owner when flakes appear. A failure is not automatically waived because a retry passes; I investigate the race or environment and time-box quarantine. For payment logic, a low line coverage number is less important than an explicit duplicate-charge and unknown-outcome test that truly exercises the contract.”

## How to answer in the interview

- **Why:** review needs reliable failure signals.
- **How:** gate compile, lint, tests and risk-specific checks.
- **Trade-off:** CI latency versus scope of required checks.
- **Failure case:** flaky retry masks a real race.
- **Production solution:** protect branch and publish diagnostic artifacts.

## Deep-dive talking points

Prompt for head SHA, branch protection, baseline debt, affected tests and untrusted job permissions.

## Follow-up questions

- [CIC-18](../cic-18/): Why separate PR/release workflows? **Answer:** PR code must not read signing secrets.
- [TST-24](../tst-24/): How keep gate fast? **Answer:** cheap high-signal checks early and targeted slow tests.

## Self-check rubric

Specify required PR checks, branch protection and artifact identity; run lint/static analysis and focused tests before merge; explain where emulator and release-only tests fit without hiding failures.

## References and reviewed-on date

- [Android Lint](https://developer.android.com/studio/write/lint) — static checks.
- [Gradle command-line builds](https://docs.gradle.org/current/userguide/command_line_interface.html) — task execution.

Technically reviewed against the cited primary documentation on 2026-10-13; automated technical review only, not human review.
