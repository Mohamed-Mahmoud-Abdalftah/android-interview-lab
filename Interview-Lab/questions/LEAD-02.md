---
id: "LEAD-02"
question: "How do you review code for correctness, security, readability, and testability?"
topic: "Senior Ownership, Communication & Technical Leadership"
code: "LEAD"
group: "A"
phase: 5
priority: "P2"
order: 457
editorial_status: "reviewed"
---

# LEAD-02

## Original interview question

How do you review code for correctness, security, readability, and testability?

## What the interviewer evaluates

- Risk-ranked code review with constructive, verifiable feedback.
- Correctness/security before style and testability.

## Explanation in Arabic

Code review تبدأ بالـbehavior والحدود: requirement اتحققت؟ هل في race، cancellation، auth bypass، data leak أو migration risk؟ بعدين API design، testability، readability وstyle. اكتب comment محدد بسبب وتأثير واقتراح أو سؤال؛ ما تحولش review لمنافسة preferences. في payment code لازم تشوف unknown outcome وidempotency قبل اسم variable.

## Why it matters and how it works

Review is a risk filter and a knowledge-sharing process. Check source of truth, lifecycle, concurrency, security boundary, performance and test evidence. Different findings have different severity; blocking comments should identify a real defect or unmet requirement.

## Worked example

On a PR that retries a charge after timeout, ask whether the same operation ID is persisted before send and enforced server-side. Request a lost-response test. A style issue on the same PR can be nonblocking if formatter handles it.

## Trade-offs and decision criteria

Deep reviews take time; risk-based sampling focuses attention. Automated lint handles routine formatting, freeing human review for logic and threat models. Excessive nitpicks can slow delivery and discourage discussion.

## Failure modes

Approving because tests pass misses untested trust boundaries. Blocking on personal naming taste wastes attention. Separate required change from suggestion and cite the concrete failure mode.

## Production perspective

Team review checklist includes release variant, data migration, API contract, telemetry redaction and rollback for risky code. Measure defect escapes and review latency, not comment count.

## Interview answer — short

“I review for behavior and risk first, then maintainability. I give actionable feedback with a failure case and test suggestion, and let automation handle style.”

## Interview answer — structured

“I read the requirement and trace data through the changed code: who owns state, what happens on cancellation or process death, where trust crosses to the backend, and what tests prove it. For a payment retry I look for stable identity and unknown-outcome reconciliation before discussing naming. I distinguish blocking defects from optional improvements, suggest a concrete reproduction or test, and ask clarifying questions when intent is unclear. Lint handles routine formatting, while review focuses on decisions that tests may miss.”

## Interview answer — deep senior

“My review starts with a change-risk map: user-visible invariant, security boundary, concurrency and lifecycle, persistence/migration, performance, and observability. I inspect only the relevant surrounding code and contract, then run or request targeted tests. Feedback names the precise line/behavior and why it matters—‘a response lost after provider approval can generate a second charge here’—plus a safe direction such as same-ID status lookup. I avoid presenting preferences as defects and explain trade-offs when there are alternatives. I also consider whether a rollback would strand persisted data. The process should teach and protect the product; I monitor escaped defects and review wait time to improve it. Request a lost-response test.”

## Deep-dive talking points

Prompt for severity, trust boundary, targeted test, respectful feedback and rollback.

## Follow-up questions

- [LEAD-03](../lead-03/): How prioritize review debt? **Answer:** by impact and frequency, not style annoyance.
- [TST-23](../tst-23/): What test evidence matters? **Answer:** threat-to-control mapping at real boundary.

## Self-check rubric

Can you state the decision, evidence, affected people, measurable result, risk and both follow-up answers without claiming unearned personal experience?

## References and reviewed-on date

- [Android architecture guide](https://developer.android.com/topic/architecture) — design boundaries.
- [Google code review guidance](https://google.github.io/eng-practices/review/reviewer/) — primary review process guidance.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
