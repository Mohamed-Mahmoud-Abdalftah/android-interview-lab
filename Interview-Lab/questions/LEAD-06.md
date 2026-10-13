---
id: "LEAD-06"
question: "How do you write an RFC/ADR for a major architecture change?"
topic: "Senior Ownership, Communication & Technical Leadership"
code: "LEAD"
group: "B"
phase: 5
priority: "P2"
order: 461
editorial_status: "reviewed"
---

# LEAD-06

## Original interview question

How do you write an RFC/ADR for a major architecture change?

## What the interviewer evaluates

- ADR/RFC structure, decision status and implementation consequences.
- Review/revisit trigger rather than a document that merely declares preference.

## Explanation in Arabic

RFC للمناقشة قبل القرار، وADR يسجل قرار اتاخد وسياقه. اكتب المشكلة والconstraints، الخيارات، evidence، القرار، consequences، rollout/migration، security/testing، وامتى نراجعه. خلّي ownership واضح واطلب feedback من mobile/backend/QA/security لو interfaces هتتأثر. القرار مش “نستخدم MVI” فقط؛ لازم يحدد state/events وحدود الـAPI.

### Practical walkthrough in Egyptian Arabic

RFC/ADR لتغيير architecture لازم يربط القرار بمشكلة قابلة للفحص. مثال نقل data layer لـoffline-first: اكتب current failures، constraints، options، لماذا اخترت strategy، migration slice، data compatibility، rollback، وmetrics. اذكر ما ليس في scope، ومن يملك backend/API/testing. ADR يسجل قرارًا وسببًا وتاريخًا، ويمكن استبداله بقرار لاحق؛ ما تخليش المستند إعلانًا أن pattern “أفضل” بلا trade-offs أو خطة تنفيذ.

## Why it matters and how it works

An RFC invites alternatives and unresolved questions; an ADR records accepted decision and why. Both should be concise enough to review, linked to measurable outcomes and versioned with code. Superseding an ADR preserves history.

## Worked example

For offline-first checkout, RFC compares in-memory retry, WorkManager-only and Room outbox plus backend idempotency. ADR chooses outbox, names process-death/duplicate-send tests, server contract and rollback compatibility.

## Trade-offs and decision criteria

Too much documentation delays delivery; too little hides trade-offs. Scale depth to risk and cross-team impact. A one-page ADR may be enough for a localized choice, while a payment protocol change needs more detailed sequence/failure analysis.

## Failure modes

An ADR lacks rejected alternatives, so future team repeats debate; or says “exactly once via WorkManager,” an inaccurate guarantee. Review against implementation and update when assumptions change.

## Production perspective

Keep decision index, owner and review trigger. During rollout compare predicted metrics with actual unknown-payment age and incident rate; supersede decision if evidence changes.

## Interview answer — short

“An RFC explores a significant change; an ADR records the chosen option, context, alternatives, consequences and revisit conditions. I tie it to tests and rollout.”

## Interview answer — structured

“I write the problem and non-negotiable constraints first, then compare feasible options against criteria such as durability, team complexity, latency and security. I record the selected design, rejected alternatives, failure handling, migration, tests, owner and measurable success condition. An RFC gathers feedback before commitment; an ADR preserves the accepted rationale and can later be superseded. For cross-team API changes I ask backend, QA and security to review the contract. Superseding an ADR preserves history.”

## Interview answer — deep senior

“I write an RFC or ADR so future maintainers can recover the decision, not merely the chosen library name. For an offline-first migration I state the current failure, user impact and constraints: existing Room schema, backend consistency model, process restoration and release cadence. I compare viable options, including the smallest change, and make trade-offs explicit around complexity, testing and rollback. The decision section says why one option fits now, which assumptions it depends on and who owns each cross-team contract. I include a migration sequence that keeps old and new data compatible during rollout, tests at each boundary, observability and a rollback trigger. An ADR is intentionally concise and can later be superseded when evidence changes. The failure mode is a document that promises ‘clean architecture’ without describing data flow or what happens after a crash. I seek review from the teams that must support the system and record dissent or unresolved risk honestly.”

## How to answer in the interview

- **Why:** decisions outlive their authors.
- **How:** record context, options, choice and migration.
- **Trade-off:** document cost versus future clarity.
- **Failure case:** pattern name replaces failure analysis.
- **Production solution:** owner, test evidence and rollback trigger.

## Deep-dive talking points

Prompt for RFC versus ADR, alternative evidence, failure table, cross-team signoff and supersession.

## Follow-up questions

- [LEAD-01](../lead-01/): How explain trade-off? **Answer:** compare options against explicit constraints and revisit trigger.
- [LEAD-07](../lead-07/): Who reviews API contract? **Answer:** mobile, backend, QA and security owners.

## Self-check rubric

Write context, options, decision, consequences and rollback triggers for one architecture ADR; identify stakeholders and evidence that would justify revisiting the decision.

## References and reviewed-on date

- [Android architecture guide](https://developer.android.com/topic/architecture) — architectural boundaries.
- [Android offline-first](https://developer.android.com/topic/architecture/data-layer/offline-first) — durable decision example.

Technically reviewed against the cited primary documentation on 2026-10-13; automated technical review only, not human review.
