---
id: "LEAD-05"
question: "How do you mentor junior developers and improve team engineering practice?"
topic: "Senior Ownership, Communication & Technical Leadership"
code: "LEAD"
group: "A"
phase: 5
priority: "P2"
order: 460
editorial_status: "reviewed"
---

# LEAD-05

## Original interview question

How do you mentor junior developers and improve team engineering practice?

## What the interviewer evaluates

- Mentoring through ownership, feedback and increasing independence.
- Team practice changes measured by outcomes, not activity counts.

## Explanation in Arabic

Mentoring junior مش مجرد review comments أو pair programming مرة. نعرف مستوى الشخص وهدفه، ندي مهمة بحدود واضحة ومساحة قرار، نعمل pair في نقطة صعبة، وfeedback محدد على reasoning/tests. نرفع المسؤولية تدريجيًا ونبني team practice زي design review، test examples، incident learning. ما نخليش mentoring يتحول لاعتماد دائم على senior.

## Why it matters and how it works

Effective mentoring creates safe feedback loops: explicit expectations, timely review, opportunity to explain decisions, and autonomy with guardrails. Knowledge sharing improves bus factor and consistency when institutionalized in docs/tests.

## Worked example

Junior يشتغل على Room migration صغيرة: senior يشرح data-loss risk، يتفقوا على fixture من schema قديمة، junior يكتب migration/test، ثم يراجعوا failure cases. في المهمة التالية junior يقود التصميم بنفسه مع review checkpoint.

## Trade-offs and decision criteria

Pairing speeds learning but costs immediate capacity; asynchronous review scales but may miss conceptual confusion. Use both based on task risk and learner needs. Protect psychological safety while holding quality bar.

## Failure modes

Giving only easy tickets slows growth; throwing a novice into payment reversal with no support risks users. Create graduated ownership and explicit escalation triggers.

## Production perspective

Measure progress via independent delivery, fewer repeated review findings, test quality and team resilience, not number of meetings. Rotate code ownership thoughtfully.

## Interview answer — short

“I mentor with clear goals, scoped ownership, concrete feedback and increasing independence. I improve team habits through examples, reviews and incident learning rather than making myself a bottleneck.”

## Interview answer — structured

“I start by understanding the developer’s goals and current strengths. We agree on a bounded task and quality criteria, pair on the unfamiliar part, and use review to discuss reasoning and tests rather than only edits. I then reduce support as confidence grows. For team practice, I document decisions, create good test examples and share incident lessons. I measure whether the person can own similar work independently and whether recurring defects decline.”

## Interview answer — deep senior

“I treat mentoring as capability building with product safety. A junior can own a Room migration if we provide historical schemas, a fixture plan and review checkpoints; they should make the decisions and explain trade-offs, while I protect the data-loss boundary. I give feedback promptly and privately where appropriate, distinguish preference from correctness, and invite reverse feedback. Over time I assign broader problems and let them lead review/design conversations. At team level I look for reduced single-person dependencies, more reliable PRs and improved onboarding time, not a high count of pairing sessions. For high-risk payments work, I keep explicit escalation and independent verification. Rotate code ownership thoughtfully.”

## Deep-dive talking points

Prompt for learner goal, graduated scope, concrete feedback, team metric and safety guardrail.

## Follow-up questions

- [LEAD-02](../lead-02/): What makes review educational? **Answer:** precise failure reasoning and actionable test suggestion.
- [LEAD-14](../lead-14/): How improve legacy team practice? **Answer:** safe seams and shared ownership, not a rewrite mandate.

## Self-check rubric

Can you state the decision, evidence, affected people, measurable result, risk and both follow-up answers without claiming unearned personal experience?

## References and reviewed-on date

- [Android architecture guide](https://developer.android.com/topic/architecture) — maintainable ownership boundaries.
- [Google code review guidance](https://google.github.io/eng-practices/review/reviewer/) — review communication.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
