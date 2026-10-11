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

“I configure branch protection around named, reliable status checks. Fast Gradle compile, Android Lint, static analysis, JVM and contract tests run on PRs; targeted instrumentation runs when platform behavior changes. Reports show actionable findings, and baselines for old debt do not excuse new issues. Untrusted fork code gets read-only permissions and no signing material. Broader device/hardware suites gate release. The mechanics matter. Gradle tasks provide Android Lint/build/test outputs; CI status checks gate merge. Untrusted PR code should run with read-only tokens and no release secrets. Required checks should be deterministic and tied to a specific commit SHA. The choice has a trade-off. More checks improve coverage but can slow teams and increase flake noise. Stage fast checks first, parallelize, use affected-module selection with periodic full runs, and keep critical security gates mandatory.”

## Interview answer — deep senior

“A good PR gate is both trustworthy and fast. I pin checks to the exact head SHA, run independent jobs in parallel, cache deterministic inputs and measure flakiness. For a security-sensitive manifest change, an affected-area test must exercise exported components, not just lint. I prevent CI workflow changes in a PR from gaining privileged context, review suppressions and treat critical findings as blockers. Nightly/release suites cover the full graph so selective PR tests do not create blind spots. Consider a concrete case. PR modifies exported Activity: trigger manifest/security lint, unit tests and targeted instrumentation hostile-intent test. A formatting-only PR can skip hardware suite, while release candidate still runs broad device tests. A failure case illustrates the risk. Allowing “green” from a previous commit while PR head changed is unsafe; require checks for current SHA. Blanket lint baseline can hide new findings. Separate existing debt from new regressions. In production, the response is concrete. CI publishes lint SARIF/report, test failures and changed-file context. Owners review suppressions, and release pipeline tests minified artifacts before signing. The decision has a trade-off. More checks improve coverage but can slow teams and increase flake noise. Stage fast checks first, parallelize, use affected-module selection with periodic full runs, and keep critical security gates mandatory.”

## Deep-dive talking points

Prompt for head SHA, branch protection, baseline debt, affected tests and untrusted job permissions.

## Follow-up questions

- [CIC-18](../cic-18/): Why separate PR/release workflows? **Answer:** PR code must not read signing secrets.
- [TST-24](../tst-24/): How keep gate fast? **Answer:** cheap high-signal checks early and targeted slow tests.

## Self-check rubric

Can you explain this decision, apply the example, name a trade-off and failure, and answer both follow-ups without relying on a memorized slogan?

## References and reviewed-on date

- [Android Lint](https://developer.android.com/studio/write/lint) — static checks.
- [Gradle command-line builds](https://docs.gradle.org/current/userguide/command_line_interface.html) — task execution.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
