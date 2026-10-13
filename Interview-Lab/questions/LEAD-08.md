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

## Practical walkthrough

نجاح refactor يتقاس على الهدف لا على قلة الملفات. لو فصلت repository لأن tests صعبة، قس وقت إضافة use case، test flakiness، defect rate، build time وربما allocations للـUI بعده. خد baseline قبل التغيير، وراقب release metrics بعده. احذر metric مضللة: زيادة coverage مع tests سطحية، أو تقليل LOC على حساب state machine غامضة. لو التحسن محلي لكن release crashes زادت، القرار يحتاج مراجعة.

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

“For a refactor I name the problem first. If the goal is fewer data-layer bugs, I track escaped defects, PR lead time and testability before/after, while guarding build time, crash rate and performance. I migrate incrementally so I can attribute changes and roll back. Coverage or module count is supporting information, not success by itself. I also ask developers whether the new boundary makes changes easier and look for repeated review issues.”

## Interview answer — deep senior

“I define success before changing code. If the refactor aims to make an Android data layer safer, I take a baseline for escaped defects, time to implement a representative change, test setup/flake rate and, where relevant, startup or memory cost. I then ship in slices with behavior-preserving tests and compare the same measures after rollout. A higher coverage percentage can be misleading if tests only mirror implementation; fewer lines can hide a fragile state machine. I ask whether ownership became clearer: can the ViewModel be tested without a live database, while the repository still has integration tests for real transactions? I also watch production crashes and support signals because a locally clean design can introduce migration or lifecycle regressions. The trade-off is measurement effort versus confidence, so I choose a small set of metrics tied to the original problem. If there is no improvement or the operational cost rises, I am willing to stop or revise the refactor rather than defend it by aesthetics.”

## How to answer in the interview

- **Why:** refactor value must match original problem.
- **How:** baseline outcome and measure after rollout.
- **Trade-off:** measurement cost versus evidence.
- **Failure case:** coverage rises while failures remain.
- **Production solution:** slice release and compare user-facing metrics.

## Deep-dive talking points

Prompt for hypothesis, baseline, target metric, guardrail, confounder and rollback.

## Follow-up questions

- [LEAD-03](../lead-03/): How prioritize debt repayment? **Answer:** link it to measurable future cost.
- [CIC-20](../cic-20/): How measure build refactor? **Answer:** critical-path p50/p95 and correctness.

## Self-check rubric

Choose baseline and after metrics for correctness, delivery speed, crash rate or build time; control for release mix and explain when a refactor is not worth its migration cost.

## References and reviewed-on date

- [Android app quality](https://developer.android.com/quality) — performance/reliability outcomes.
- [Gradle performance guide](https://docs.gradle.org/current/userguide/performance.html) — build measurement.

Technically reviewed against the cited primary documentation on 2026-10-13; automated technical review only, not human review.
