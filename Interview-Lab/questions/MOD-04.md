---
id: "MOD-04"
question: "What is high cohesion and low coupling?"
topic: "Gradle Modularization & Dependency Boundaries"
code: "MOD"
group: "A"
phase: 4
priority: "P1"
order: 357
editorial_status: "reviewed"
---

# MOD-04

## Original interview question

What is high cohesion and low coupling?

## What the interviewer evaluates

- Define cohesion and coupling in terms of reasons to change.
- Apply the terms to module API and ownership rather than slogans.
- Admit trade-offs when extracting shared code.

## Explanation in Arabic

High cohesion تعني عناصر module تخدم مسؤولية/قدرة واضحة وتتغير غالبًا لنفس السبب. Low coupling تعني علاقتها بالآخرين عبر عقود صغيرة ومستقرة، فلا يحتاج feature معرفة تفاصيل implementation داخل غيره. مثلًا `:feature:checkout` يملك checkout UI/state/use cases المتصلة، لكنه لا يملك كل HTTP client للتطبيق. لو class واحدة مشتركة انتقلت إلى `:core:common` فذلك لا يقلل coupling تلقائيًا؛ قد يجعل عشرات modules تعتمد على API واسعة. قيّم أسباب التغيير واتجاه dependencies ووقت إعادة البناء.

## Why it matters and how it works

Modules with cohesive responsibilities have fewer unrelated internal reasons to change. Narrow public APIs reduce how much consumer code knows and must rebuild when internals evolve. Coupling is not zero—features must collaborate—but it should be intentional, directional and testable. A highly abstract API can itself create cognitive and maintenance cost.

## Worked example

Checkout contains cart validation, payment initiation UI and order confirmation coordination; catalog contains browsing and search. Both use a small `MoneyFormatter` or shared money value contract where semantically appropriate. If checkout imports catalog's internal Retrofit DTO merely to show a product name, they are coupled at the wrong boundary; pass a stable display or domain contract.

## Trade-offs and decision criteria

Sharing code prevents duplication but may force unrelated features into one dependency and release schedule. Duplicating a tiny UI helper can be cheaper than a premature common API. Cohesion can justify a larger feature module if all parts evolve together. Measure build fan-out and team ownership before extracting.

## Failure modes

A core module mixes payment rules, analytics UI and test helpers. A feature exposes every internal class as public. Two teams must coordinate for an internal change because their modules import each other's DTOs. A “decoupled” interface has one method per implementation detail and changes every sprint.

## Production perspective

Review module change history, API surface and dependency graph. Ask whether one product change touches one cohesive owner or several unrelated modules, and tighten boundaries where repeated cross-team edits occur.

## Interview answer — short

“High cohesion groups code with one reason to change; low coupling keeps collaboration through small stable contracts instead of implementation details.”

## Interview answer — structured

“I evaluate cohesion by asking whether classes in a module serve the same capability and evolve together. I evaluate coupling by checking what a consumer must import and know. Checkout should own its workflow and depend on a small product/payment contract, not catalog's internal DTOs. Extracting everything shared into common is not automatically good: the common API can become a high-fan-out bottleneck. I balance reuse, ownership and actual change patterns.”

## Interview answer — deep senior

“Cohesion is about why code changes together; coupling is about how much one unit must know about another. A checkout module containing cart validation, payment initiation and confirmation may be cohesive because those pieces support one user capability. It becomes tightly coupled if it reaches into catalog's database DTO or private UI state to obtain a product label. I would expose a narrow contract or share an appropriately owned domain value. I do not chase zero dependencies: a feature still needs other capabilities, but the direction and API should be intentional. I also avoid reflexively extracting every repeated function into `:core:common`. That can make a large number of modules depend on an unstable grab bag and broaden rebuilds. A small duplication may be cheaper until the semantics are truly shared. To assess the architecture, I inspect the graph, public API, change history and team workflow: does a simple internal change require edits across unrelated modules? Do consumers need implementation types? The goal is a boundary that makes expected product changes local while leaving integration explicit and testable.”

## Deep-dive talking points

Discuss reasons to change, public API size, semantic reuse, fan-out, duplication, and ownership history.

## Follow-up questions

- Does low coupling mean no dependencies? **Answer:** no; it means deliberate narrow dependencies on stable contracts.
- Is extracting all duplicate code good? **Answer:** no; semantic ownership and shared API cost matter.
- What evidence shows poor cohesion? **Answer:** unrelated product changes repeatedly modify one mixed module.

## Self-check rubric

Define both terms, diagnose one boundary violation, and weigh sharing versus duplication.

## References and reviewed-on date

- [Android modularization guide](https://developer.android.com/topic/modularization) — encapsulation and ownership.
- [Common modularization patterns](https://developer.android.com/topic/modularization/patterns) — practical boundaries.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. Design criteria are reasoned guidance.
What is high cohesion and low coupling?
