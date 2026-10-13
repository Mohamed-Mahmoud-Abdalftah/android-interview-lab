---
id: "MOD-01"
question: "What is modularization, and what trade-offs does it introduce?"
topic: "Gradle Modularization & Dependency Boundaries"
code: "MOD"
group: "A"
phase: 4
priority: "P1"
order: 354
editorial_status: "reviewed"
---

# MOD-01

## Original interview question

What is modularization, and what trade-offs does it introduce?

## What the interviewer evaluates

- Define modules as build and ownership boundaries, not folders alone.
- Relate boundaries to encapsulation, team work and build graph.
- Explain configuration, API and integration costs.

## Explanation in Arabic

Modularization تقسيم التطبيق إلى Gradle modules لها dependencies وpublic APIs محددة، مثل app/features/core. الهدف عزل المسؤوليات، تسهيل ownership وإعادة الاستخدام، وربما تحسين incremental build حين تكون الحدود صحيحة. لكنه ليس مجانيًا: كل module تضيف Gradle configuration، API maintenance، DI/navigation wiring واختبارات تكامل. لو قسمت حسب كل class، ستخلق graph معقدة وبطء configuration بدون فائدة. قِس سبب التقسيم أولًا، واختَر حدودًا حول feature أو capability مستقرة.

### Practical walkthrough in Egyptian Arabic

Module تقسم ownership والبناء، لكن كل module جديدة تزيد Gradle configuration وAPI maintenance. لو فريق checkout وفريق catalog يغيروا نفس core باستمرار، التقسيم الحالي قد لا يحمي الاستقلالية. ابدأ boundary واضح لحاجة تتغير مستقلة وتملك tests، وقس build time وchange coupling بعد الفصل. لا تجعل عدد modules هدفًا بحد ذاته.

## Why it matters and how it works

Gradle compiles modules according to a dependency graph. An implementation change behind a stable API can avoid recompiling unrelated consumers, while an API change fans out. Visibility and compile dependencies make ownership enforceable beyond package conventions. The benefit depends on DAG quality, module size, Gradle configuration and test design, not merely module count.

## Worked example

A large commerce app separates checkout and catalog features, plus a shared payment contract and core network implementation. Catalog cannot import checkout internals; app composes both. A checkout API change is reviewed by its consumers, while a private screen refactor stays local. The team records configuration time and affected compile tasks before and after the split.

## Trade-offs and decision criteria

Modules help when a boundary supports independent ownership, visibility or build isolation. They cost wiring and public-surface design; a small app may be simpler as one module with package boundaries. Avoid moving unstable implementation details into a shared API solely to satisfy a module graph.

## Failure modes

A giant `:core:common` becomes a hidden monolith. Two features import each other's implementation and form a cycle. `api` exports too many libraries and broadens recompilation. Hundreds of tiny modules increase Gradle overhead and make navigation/DI debugging harder.

## Production perspective

Document a module DAG and ownership rules, enforce no cycles, track configuration and incremental build time, and maintain integration tests across boundaries. Revisit a split when its costs outweigh actual isolation gains.

## Interview answer — short

“Modularization creates explicit Gradle and API boundaries for ownership and reuse; it can improve isolation but adds graph, configuration and integration complexity.”

## Interview answer — structured

“I split around cohesive capabilities, not arbitrary file counts. A feature module exposes only the contract consumers need, and the app composes implementations through an acyclic graph. This can let teams change internals independently and reduce compile fan-out. I also account for more Gradle configuration, DI/navigation wiring and cross-module tests. I would measure build impact and start with a few meaningful boundaries rather than create dozens of tiny modules.”

## Interview answer — deep senior

“I treat a module as an enforceable ownership and compile boundary. A checkout feature can hide its screens and internal repositories, expose a small navigation or domain contract, and depend on stable lower-level APIs. That can reduce accidental coupling and make an internal refactor affect fewer compilers and teams. The graph must remain acyclic so there is a clear composition root. The trade-off is real: Gradle config time, duplicated convention setup if unmanaged, API version decisions, Hilt binding visibility, navigation contracts and more integration tests. A module per class may actually slow the build and make architecture harder to follow. I justify a new module with an ownership, reuse, delivery or measured build reason; for a small app I may use packages first. I track configuration and incremental build baselines, watch for a growing common module, and keep a test that assembles the actual app. The success criterion is easier, safer change at acceptable build cost, not the number of modules on a diagram.”

## How to answer in the interview

- **Why:** modules should reduce change coupling.
- **How:** split by ownership and dependency direction.
- **Trade-off:** isolation versus build/config cost.
- **Failure case:** many empty modules slow work.
- **Production solution:** measure build and cross-team changes.

## Deep-dive talking points

Discuss build boundary, public API, acyclic graph, ownership, config overhead and measurement.

## Follow-up questions

- Is a package the same as a Gradle module? **Answer:** no; package organization alone does not enforce compile dependency boundaries.
- Can more modules always speed builds? **Answer:** no; configuration and graph overhead can outweigh isolation gains.
- What is a warning sign of poor modularization? **Answer:** a giant common module or feature cycles that expose internals.

## Self-check rubric

State a concrete boundary, benefit, cost, cycle rule and build metric.

## References and reviewed-on date

- [Android modularization guide](https://developer.android.com/topic/modularization) — benefits and trade-offs.
- [Common modularization patterns](https://developer.android.com/topic/modularization/patterns) — module structures.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. Build impact must be measured in the target repo.
