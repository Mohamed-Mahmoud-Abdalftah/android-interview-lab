---
id: "MOD-17"
question: "When is a new feature module justified, and when is it unnecessary complexity?"
topic: "Gradle Modularization & Dependency Boundaries"
code: "MOD"
group: "C"
phase: 4
priority: "P1"
order: 370
editorial_status: "reviewed"
---

# MOD-17

## Original interview question

When is a new feature module justified, and when is it unnecessary complexity?

## What the interviewer evaluates

- Demand a concrete ownership, build, reuse or delivery reason.
- Weigh module overhead and boundary stability.
- Propose measured incremental extraction.

## Explanation in Arabic

Feature module مبررة عندما قدرة لها owner واضح، public entry صغير، استقلال تطوير/اختبار مفيد، أو delivery/build impact مقاس. لو تطبيق صغير وفريق واحد، تقسيم شاشة واحدة إلى module مستقلة قد يزيد Gradle configuration وDI/navigation wiring دون فائدة. لا تعتمد على عدد classes وحده. اسأل: هل تغيراتها تتسبب في إعادة بناء أجزاء كثيرة؟ هل فرق تعمل بالتوازي؟ هل الميزة قابلة للتوصيل مستقلة؟ ابدأ بpackage boundary ثم استخرج module عند وجود seam مستقرة واختبارات تقيس أثرها.

## Why it matters and how it works

A Gradle module enforces compile visibility and can isolate changes, but every module adds configuration, dependencies, build variants and integration surface. A feature boundary that changes constantly may require frequent API edits, negating independence. Build improvements depend on the shape of the graph and tooling, not module count.

## Worked example

A marketplace's seller dashboard has its own team, flows and release risk; a `:feature:seller` module can hide its internals and expose a destination. A one-screen About page with no reusable contract and the same owner as settings likely remains in the settings module. Compare app assemble and incremental build traces after extracting seller.

## Trade-offs and decision criteria

Isolation can improve ownership and tests, while extra modules complicate setup and cross-feature integration. A module may be justified for dynamic delivery even if team ownership is shared, but download failure becomes a product concern. Start with cohesive boundaries and revise using change history.

## Failure modes

Every screen becomes a module and build configuration dominates. A module exposes all internals because no contract was designed. Teams split a tightly coupled workflow, then add event buses to reconstruct communication. A claimed build speedup is never measured.

## Production perspective

Record why each module exists, owner and public API. Track configuration time, incremental rebuild fan-out and integration failures. Merge or simplify modules when their boundary stops paying for itself.

## Interview answer — short

“I add a feature module when it buys real ownership, encapsulation, reuse, delivery or measured build isolation; otherwise I keep a cohesive feature together.”

## Interview answer — structured

“I do not split by line count alone. A seller dashboard with a separate team and stable entry point is a good module candidate; a tiny About screen inside Settings probably is not. I compare the benefit of visibility and incremental builds with Gradle configuration, DI/navigation wiring and contract maintenance. I can start with packages, extract a vertical slice when the seam is clear, then measure whether the split helped.”

## Interview answer — deep senior

“A new feature module is an investment in a boundary. I look for a coherent capability with a clear owner and a small public integration point. Independent teams, reuse across app variants, dynamic delivery or measured build fan-out can justify that investment. I also ask whether the boundary is stable enough: if two screens exchange internal state every week, splitting them may create ceremony and an opaque event bus rather than independence. A Gradle project adds configuration, plugin setup, DI visibility, navigation contracts and integration tests, so ‘more modules’ is not a success metric. I may begin with packages and access discipline, then extract a vertical slice after its dependencies are visible. For a seller dashboard I can expose a destination and keep its implementation private; for a static About screen I would probably keep it with Settings. I benchmark clean and incremental builds and inspect cross-team changes before and after. If a module stops serving a reason and only adds indirection, I am willing to merge it. Modularity should make routine product work safer at acceptable build and coordination cost.”

## Deep-dive talking points

Discuss ownership, stable API, build measurement, delivery, integration overhead and reversible extraction.

## Follow-up questions

- Does a large file count alone justify a module? **Answer:** no; a cohesive boundary and measured benefit matter.
- Can packages be a first step? **Answer:** yes, when a Gradle boundary is not yet justified.
- When should modules be merged? **Answer:** when artificial separation creates more coordination than isolation.

## Self-check rubric

Justify one extraction, reject one needless split, and define metrics and rollback criteria.

## References and reviewed-on date

- [Android modularization guide](https://developer.android.com/topic/modularization) — reasons and trade-offs.

Technically reviewed against this primary source on 2026-10-11 by automated editorial review. Extraction decision is context-specific.
