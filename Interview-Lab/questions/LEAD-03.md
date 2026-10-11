---
id: "LEAD-03"
question: "What is technical debt, and how do you prioritize it?"
topic: "Senior Ownership, Communication & Technical Leadership"
code: "LEAD"
group: "A"
phase: 5
priority: "P2"
order: 458
editorial_status: "reviewed"
---

# LEAD-03

## Original interview question

What is technical debt, and how do you prioritize it?

## What the interviewer evaluates

- Debt as future-change cost caused by design shortcuts or obsolete assumptions.
- Priority by risk, change frequency and measurable return.

## Explanation in Arabic

Technical debt مش كل code قديم؛ هو قرار أو حالة بتخلّي التغيير القادم أغلى أو أخطر. نصنف debt: bug/security risk، build pain، architecture coupling، tests missing، migrations. الأولوية حسب impact واحتمال وقوع المشكلة وتكرار لمس الكود وتكلفة الإصلاح. Debt في payment retry أو secret handling أعلى من تنسيق file نادر.

## Why it matters and how it works

Debt can be deliberate with a repayment plan or accidental. A useful backlog item states evidence, consequence and a bounded intervention; vague “rewrite architecture” is hard to prioritize. Incident rate, lead time and defect escape can measure payoff.

## Worked example

Legacy screen directly calls Retrofit and Room. If it changes weekly and causes bugs, introduce repository seam around one flow and add tests before wider extraction. Do not rewrite all screens while a critical token leakage issue remains.

## Trade-offs and decision criteria

Repaying debt improves future velocity and reliability but consumes current feature capacity. A rewrite can introduce new defects; incremental strangler-style changes often reduce risk. Some harmless old code should remain.

## Failure modes

Team labels every disliked pattern “debt” and plans a six-month rewrite without baseline metrics. Instead tie each item to a customer/engineering cost and define completion criteria.

## Production perspective

Keep debt register with owner, impact, evidence and next touchpoint; reserve capacity for high-leverage repairs and revisit after incidents. Security debt may block release regardless of roadmap.

## Interview answer — short

“Technical debt is a design or maintenance cost that makes future change slower or riskier. I prioritize by impact, change frequency and repair payoff, then make incremental, measurable fixes.”

## Interview answer — structured

“I do not equate age with debt. I ask what future work is slowed or made unsafe and quantify it: repeated bugs, long build times, fragile migrations or security exposure. A hot payment path with no idempotency tests ranks above a rarely touched class with imperfect style. I choose a bounded repair, add tests around behavior, measure change lead time or incidents, and avoid a broad rewrite unless evidence shows incremental work cannot resolve the coupling. ”

## Interview answer — deep senior

“I maintain a portfolio of debt with risk and economic cost. For each item I record the constraint it creates, how often the area changes, customer impact if it fails, remediation size and expected metric. Critical security/payment correctness debt is addressed immediately or blocks rollout; medium debt can be paid when the feature area is touched; low-impact aesthetic debt may wait. I favor seams, test coverage and gradual migration because rewrites reset knowledge and introduce new failure modes. After a repair I compare escaped defects, cycle time, build time or on-call load; if no metric improves, I reassess rather than declare success.”

## Deep-dive talking points

Prompt for definition, impact/frequency scoring, incremental repair and measurable payoff.

## Follow-up questions

- [LEAD-08](../lead-08/): How measure refactor? **Answer:** compare defect, lead-time, performance and maintenance metrics.
- [LEAD-14](../lead-14/): What first in legacy app? **Answer:** inventory incidents and create safe seams before broad rewrite.

## Self-check rubric

Can you state the decision, evidence, affected people, measurable result, risk and both follow-up answers without claiming unearned personal experience?

## References and reviewed-on date

- [Android architecture guide](https://developer.android.com/topic/architecture) — maintainable separation.
- [Gradle performance guide](https://docs.gradle.org/current/userguide/performance.html) — build debt measurement.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
