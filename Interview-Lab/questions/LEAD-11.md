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

### Practical walkthrough in Egyptian Arabic

خلاف MVVM/MVI غالبًا خلاف على حدود state/event، مش اسم pattern. اختار شاشة واقعية فيها loading، user edits، retry وprocess death؛ ارسم event -> state -> side effect، وشوف أين يحدث duplication أو stale data. اعمل prototype صغير واختبارات، وقارن كلفة تعليم الفريق والتغيير والتشخيص. ممكن MVVM مع reducer واضح يحقق المطلوب بدون framework جديد، وممكن MVI يساعد لو state transitions معقدة. سجّل القرار وقواعد الاستثناء.

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

“I turn a pattern debate into a decision about state ownership and failure behavior. I pick a representative screen—perhaps a checkout with editable amount, loading, unknown payment outcome and process recreation—and ask each proposal to show where events enter, how state changes, who runs effects and what survives a kill. A small prototype and tests reveal more than arguing about names. MVVM can be clear with an immutable UI state and explicit reducer; an MVI-style unidirectional loop may be useful when transitions are complex, but it adds ceremony and learning cost. I compare debugging, testability, migration and team familiarity, then choose the smallest coherent model for this codebase. I write the decision and exceptions so future reviews are consistent. I do not claim a pattern alone fixes duplicate charges; durable identity and backend idempotency remain separate contracts. The trade-off is uniformity versus tailoring, so I seek enough consistency without forcing every simple screen into a complex framework.”

## How to answer in the interview

- **Why:** pattern conflict hides ownership questions.
- **How:** prototype one difficult screen and test transitions.
- **Trade-off:** consistency versus added ceremony.
- **Failure case:** pattern chosen but payment state remains transient.
- **Production solution:** document decision and exceptions.

## Deep-dive talking points

Prompt for overlapping patterns, representative pilot, criteria, dissent and durable state boundary.

## Follow-up questions

- [LEAD-01](../lead-01/): How explain the choice? **Answer:** problem, constraints, options, evidence and revisit trigger.
- [LEAD-06](../lead-06/): What records it? **Answer:** an ADR with consequences and exceptions.

## Self-check rubric

Turn MVVM/MVI disagreement into explicit state, event, team and testing criteria; run a small spike, record the decision and leave room for different screens to need different patterns.

## References and reviewed-on date

- [Android UI architecture](https://developer.android.com/topic/architecture/ui-layer) — UI state guidance.
- [Android architecture guide](https://developer.android.com/topic/architecture) — separation of concerns.

Technically reviewed against the cited primary documentation on 2026-10-13; automated technical review only, not human review.
