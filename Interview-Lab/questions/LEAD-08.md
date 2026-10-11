---
id: "LEAD-08"
question: "What metrics tell you whether a refactor was successful?"
topic: "Senior Ownership, Communication & Technical Leadership"
code: "LEAD"
group: "B"
phase: 5
priority: "P2"
order: 463
editorial_status: "reviewed"
---

# LEAD-08

## Original interview question

What metrics tell you whether a refactor was successful?

## What the interviewer evaluates

- Outcome metrics of refactor, not lines moved or modules created.
- Baseline, guardrails and attribution.

## Explanation in Arabic

Refactor نجاحها يتقاس بهدفها: لو فصلنا data layer عشان bugs أقل، نقيس escaped defects ووقت إضافة feature واختبارات. لو الهدف build speed، نقيس cold/incremental p50/p95. لو UI، frame time وcrash/ANR. نحط baseline قبل التغيير وguardrails للأداء/الأمان، ونقارن cohorts؛ عدد files أو classes مش metric نجاح.

## Why it matters and how it works

A refactor preserves external behavior while changing structure. Metrics should include intended benefit, unintended regression and cost. Attribution is hard if releases change multiple things, so stage or compare before/after with context.

## Worked example

Extract a repository from 20 ViewModels. Baseline: checkout bugs per release, unit-test runtime, PR lead time and payment unknown age. After incremental migration, compare for several releases, and ensure crash/ANR and bundle size did not regress.

## Trade-offs and decision criteria

Engineering metrics can be noisy and gamed; combine quantitative trends with developer feedback and incident review. Short-term velocity may dip during migration while future change safety improves.

## Failure modes

Team declares success because there are more modules and 80% coverage, but build time doubled and bugs persisted. Revisit boundary design and whether tests assert behavior rather than implementation.

## Production perspective

Choose a small set of metrics with owners and observation windows, document confounders, and stop/rollback if guardrails fail. Share findings openly even if the hypothesis was wrong.

## Interview answer — short

“I define success before refactoring, capture a baseline, measure the target outcome and guardrails, and review whether the change improved real delivery or reliability.”

## Interview answer — structured

“For a refactor I name the problem first. If the goal is fewer data-layer bugs, I track escaped defects, PR lead time and testability before/after, while guarding build time, crash rate and performance. I migrate incrementally so I can attribute changes and roll back. Coverage or module count is supporting information, not success by itself. I also ask developers whether the new boundary makes changes easier and look for repeated review issues. The mechanics matter. A refactor preserves external behavior while changing structure. Metrics should include intended benefit, unintended regression and cost. Attribution is hard if releases change multiple things, so stage or compare before/after with context. The choice has a trade-off. Engineering metrics can be noisy and gamed; combine quantitative trends with developer feedback and incident review. Short-term velocity may dip during migration while future change safety improves.”

## Interview answer — deep senior

“I set an explicit hypothesis and observation window. For example, splitting a legacy repository should reduce duplicate cache logic and incidents without increasing cold build time beyond an agreed threshold. I collect baseline distributions, not one data point, and segment by affected flows and release version. I watch guardrails such as ANR, startup, APK size and security findings while tracking cycle time and defect escapes. If metrics do not improve, I examine whether the refactor moved complexity rather than removing it; I am willing to simplify or revert. I do not optimize for easy-to-game proxies like file count or nominal test coverage. Consider a concrete case. Extract a repository from 20 ViewModels. Baseline: checkout bugs per release, unit-test runtime, PR lead time and payment unknown age. After incremental migration, compare for several releases, and ensure crash/ANR and bundle size did not regress. A failure case illustrates the risk. Team declares success because there are more modules and 80% coverage, but build time doubled and bugs persisted. Revisit boundary design and whether tests assert behavior rather than implementation. In production, the response is concrete. Choose a small set of metrics with owners and observation windows, document confounders, and stop/rollback if guardrails fail. Share findings openly even if the hypothesis was wrong.”

## Deep-dive talking points

Prompt for hypothesis, baseline, target metric, guardrail, confounder and rollback.

## Follow-up questions

- [LEAD-03](../lead-03/): How prioritize debt repayment? **Answer:** link it to measurable future cost.
- [CIC-20](../cic-20/): How measure build refactor? **Answer:** critical-path p50/p95 and correctness.

## Self-check rubric

Can you state the context, decision evidence, alternatives, affected people, measurable result and both follow-up answers?

## References and reviewed-on date

- [Android app quality](https://developer.android.com/quality) — performance/reliability outcomes.
- [Gradle performance guide](https://docs.gradle.org/current/userguide/performance.html) — build measurement.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
