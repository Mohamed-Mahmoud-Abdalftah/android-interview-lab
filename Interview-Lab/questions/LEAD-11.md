---
id: "LEAD-11"
question: "A team disagrees about MVVM vs MVI. How do you lead a decision based on constraints?"
topic: "Senior Ownership, Communication & Technical Leadership"
code: "LEAD"
group: "C"
phase: 5
priority: "P2"
order: 466
editorial_status: "reviewed"
---

# LEAD-11

## Original interview question

A team disagrees about MVVM vs MVI. How do you lead a decision based on constraints?

## What the interviewer evaluates

- Decision facilitation from product constraints rather than framework preference.
- Small experiment and reversible ADR.

## Explanation in Arabic

خلاف MVVM/MVI ما يتحسمش بعدد المقالات. نحدد المشكلة: state معقدة؟ events؟ offline؟ حجم team؟ testability؟ ونقارن implementation صغير لنفس الشاشة، نقيس cognitive load، bugs وspeed. ممكن MVVM بStateFlow واحد يكفي؛ MVI يفيد لو transitions كثيرة وتحتاج reducer واضح لكنه يزيد ceremony. نوثق قرار قابل للمراجعة.

## Why it matters and how it works

MVVM is a broad separation pattern; MVI-style unidirectional state/reducer is a more specific state-management approach. They can overlap rather than be mutually exclusive. The team needs conventions for one-time effects, lifecycle collection and process death regardless of label.

## Worked example

Checkout screen with initiated/unknown/reversal states: prototype a reducer with explicit events and a ViewModel exposing StateFlow, then compare to current ViewModel methods. Test duplicate callback and rotation. Choose the simpler approach that makes illegal transitions visible.

## Trade-offs and decision criteria

Formal reducer improves traceability but adds boilerplate and may overcentralize simple screens. Ad hoc ViewModel methods are quick but can scatter state transitions. Pick by state complexity and team familiarity.

## Failure modes

Debate ends with “senior prefers MVI,” so adoption is inconsistent. Agree on decision criteria, sample code, migration scope and review trigger. Do not rewrite stable screens merely for consistency.

## Production perspective

Facilitator invites engineers with different views, records evidence and dissent, chooses limited pilot, and measures defects/onboarding impact. Document conventions in ADR.

## Interview answer — short

“I frame MVVM versus MVI around state complexity, team skills and failure modes, run a small pilot, then document a reversible decision rather than vote on labels.”

## Interview answer — structured

“I ask what pain we are solving: scattered state transitions, hard-to-test effects or just inconsistent style. MVVM and MVI are not exclusive; a ViewModel can expose a single immutable state and use reducer-like transitions. For a complex checkout I prototype both, test timeout and late callbacks, and compare readability, testability and migration cost. I choose a convention with a narrow rollout and a review date instead of mandating a rewrite across all screens.”

## Interview answer — deep senior

“I facilitate by making constraints explicit and separating facts from preferences. The team defines requirements such as process-death recovery, deterministic state transitions, one-time effects, accessibility and onboarding cost. We implement one representative high-risk flow with both approaches and inspect tests and code review friction. If MVI-style reducers make illegal payment transitions harder to express, that is evidence; if a simple screen gains only boilerplate, we avoid imposing it there. I record the decision, exceptions, migration strategy and metrics, then invite dissent before committing. The backend and durable repository remain authoritative regardless of UI pattern. Test duplicate callback and rotation. Document conventions in ADR.”

## Deep-dive talking points

Prompt for overlapping patterns, representative pilot, criteria, dissent and durable state boundary.

## Follow-up questions

- [LEAD-01](../lead-01/): How explain the choice? **Answer:** problem, constraints, options, evidence and revisit trigger.
- [LEAD-06](../lead-06/): What records it? **Answer:** an ADR with consequences and exceptions.

## Self-check rubric

Can you state the context, decision evidence, alternatives, affected people, measurable result and both follow-up answers?

## References and reviewed-on date

- [Android UI architecture](https://developer.android.com/topic/architecture/ui-layer) — UI state guidance.
- [Android architecture guide](https://developer.android.com/topic/architecture) — separation of concerns.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
