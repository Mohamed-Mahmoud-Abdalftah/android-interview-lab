---
id: "MOD-19"
question: "Two feature teams need the same business logic. Where should it live?"
topic: "Gradle Modularization & Dependency Boundaries"
code: "MOD"
group: "C"
phase: 4
priority: "P1"
order: 372
editorial_status: "reviewed"
---

# MOD-19

## Original interview question

Two feature teams need the same business logic. Where should it live?

## What the interviewer evaluates

- Identify one authoritative business-rule owner.
- Separate stable shared policy from UI convenience code.
- Account for versioning, tests and cross-team governance.

## Explanation in Arabic

لو logic هي rule حقيقية مثل حساب أهلية خصم أو رسوم، اجعل لها owner واحد في domain/use-case module أو capability service يرى الفريقان عقدها؛ لا تنسخها فتختلف النتائج. لكن “نفس” تنسيق text أو UI behavior قد لا يكون نفس semantics، فلا ترفع كل تشابه إلى core. اكتب invariants والأمثلة وحدد inputs/outputs بعيدًا عن Android UI، ثم اختبار مشترك وconsumer integration. الفريقان يتفقان على ownership وAPI evolution، والتطبيق يربط implementation. لو اختلاف المتطلبات قريب، صمم extension واضح بدل `if (featureA)` داخل common.

## Why it matters and how it works

A shared business rule needs consistent decisions across user flows. A stable domain contract lets both features depend in one direction on an owned policy. Changes to shared logic then fan out deliberately, which is appropriate for correctness even if it adds coordination. Similar-looking code is not always the same rule; premature extraction can force unrelated teams into one release cycle.

## Worked example

Cart and Checkout both display discount eligibility. A `DiscountPolicy.evaluate(cart, customer)` use case owns the calculation and returns a reasoned result; both features render it differently. Tests cover boundaries, expired offers and currency precision. A change to policy updates one implementation and both UI integration tests, rather than letting Cart show a discount Checkout later rejects.

## Trade-offs and decision criteria

Central policy avoids drift but its public API and release process need an owner. Duplicating small presentation formatting may be fine; duplicating financial rules is risky. A remote backend may be authoritative for final eligibility, with local policy only a preview, so the contract should state that distinction.

## Failure modes

Each team copies the formula and rounding differs. A shared module takes direct dependencies on both feature UIs. A policy API returns screen-specific models. Local eligibility is treated as final even though the server can reject it. A common module grows many feature flags rather than stable concepts.

## Production perspective

Assign codeowners and versioned contract review, build a boundary test matrix, and compare app/server results where backend authority applies. Monitor disagreements as product defects, not merely UI inconsistencies.

## Interview answer — short

“One owner should hold a genuinely shared business rule behind a small domain contract; each feature renders the result, and backend authority stays explicit.”

## Interview answer — structured

“I first verify the two teams mean the same business rule. If Cart and Checkout both calculate discount eligibility, I put the policy in an owned domain capability with clear inputs, outputs and boundary tests, then let each feature present it differently. I keep the final server decision authoritative if applicable. I would not extract two coincidentally similar formatting functions into common before their semantics are shared.”

## Interview answer — deep senior

“I classify the shared code by semantics. If two teams need one financial eligibility rule, duplicating it invites drift, so I give the policy one owner and expose a small contract independent of either screen. Cart and Checkout can both call `DiscountPolicy.evaluate`, get an eligibility result with reason, and render it in their own UI. The policy tests cover rounding, currency, expiry, account tier and concurrency or stale input as relevant. I also state whether the client calculation is a preview while a server makes the final decision; otherwise the two features may present certainty they cannot guarantee. Shared ownership has a cost: policy changes affect both teams, so codeowners, API review and a rollout plan matter. If the common code is only a short date label with subtly different product meaning, premature extraction can be worse than local duplication. I avoid a core module that imports both feature implementations or contains switches for team names. The shared layer should represent a stable business concept, with integration tests proving both consumers handle its outcomes.”

## Deep-dive talking points

Discuss semantic sharing, one policy owner, backend authority, API governance and integration tests.

## Follow-up questions

- Is every duplicate function a shared domain rule? **Answer:** no; similar code may have different semantics.
- Who owns the final discount decision? **Answer:** often the backend; client logic should state whether it is only a preview.
- Why test both consumers? **Answer:** they may render or handle the shared result differently.

## Self-check rubric

Identify the invariant, owner and authority, then test rule boundaries and feature integration.

## References and reviewed-on date

- [Android modularization guide](https://developer.android.com/topic/modularization) — reusable modules.
- [Domain layer guidance](https://developer.android.com/topic/architecture/domain-layer) — shared business logic.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. Discount authority is product-specific.
Two feature teams need the same business logic. Where should it live?
