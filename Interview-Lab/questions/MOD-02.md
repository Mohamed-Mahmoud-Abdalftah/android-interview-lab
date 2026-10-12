---
id: "MOD-02"
question: "Compare app, feature, core, data, domain, and design-system modules."
topic: "Gradle Modularization & Dependency Boundaries"
code: "MOD"
group: "A"
phase: 4
priority: "P1"
order: 355
editorial_status: "reviewed"
---

# MOD-02

## Original interview question

Compare app, feature, core, data, domain, and design-system modules.

## What the interviewer evaluates

- Assign distinct responsibilities without a rigid universal taxonomy.
- Explain dependency direction and app composition.
- Prevent core/design system from absorbing feature-specific logic.

## Explanation in Arabic

`:app` هو composition/delivery entry point ويختار features وbindings وnavigation root. `:feature:*` يملك UI/use cases الخاصة بقدرة مثل checkout. `:data:*` يطبق repositories ويخاطب network/database. `:domain:*` اختياري لعقود وقواعد مستقلة عن Android إذا حجم النظام يبرره. `:core:*` لبنية مشتركة مستقرة مثل network client أو database setup، وليس مكانًا لكل كود لا يعرف صاحبه أين يضعه. `:designsystem` يوفر theme/components UI محايدة عن business. اتجاه dependencies من feature إلى contracts/core، وتطبيق implementation يركبه app؛ التفاصيل تختلف حسب الحجم.

## Why it matters and how it works

Module names encode ownership and intended dependency edges. App modules package final variants and serve as composition roots. Feature modules group user-facing behavior; data modules implement external access; domain modules can keep contracts/policies independent when reuse warrants them. Core and design-system modules expose cross-cutting primitives, and their APIs require careful governance because many consumers compile against them.

## Worked example

`:feature:orders` renders orders and depends on `:domain:orders` repository interface plus `:designsystem`. `:data:orders` implements it using `:core:network` and `:core:database`. `:app` includes the feature and implementation. The feature does not directly import Retrofit DTOs or a database DAO, and the design system accepts display values rather than an `Order` entity.

## Trade-offs and decision criteria

A separate domain module can clarify reusable policy but adds indirection if it holds only one interface. Shared core reduces duplication but can become a high-fan-out rebuild hotspot. Feature-local data may be simpler for a small isolated feature. Use names to express actual boundaries, not to enforce a fixed layered template.

## Failure modes

Every miscellaneous helper goes into `:core:common`. Design-system UI imports payment business types. A feature depends on data implementation, then data depends back on feature. The app contains all business logic while feature modules are empty shells.

## Production perspective

Publish a dependency rule with examples and check it in CI. Review public APIs and high-fan-out modules, and use app assembly plus feature tests to prove the composition remains valid.

## Interview answer — short

“App composes and packages; features own user capabilities; data implements access; domain can hold reusable policy/contracts; core and design system provide stable shared infrastructure and UI.”

## Interview answer — structured

“I use these names as ownership hints, not a mandated diagram. The app chooses variants, bindings and top-level navigation. A feature owns its screen behavior, data implements repository contracts with network/database, and a domain module holds independent rules when useful. Core supplies stable infrastructure; design system supplies theme and reusable UI primitives. I keep dependencies acyclic and avoid feature-specific objects in shared modules.”

## Interview answer — deep senior

“I would describe the modules by why another module is allowed to depend on them. The app is the final composition and packaging boundary: it selects features and their implementations. A feature groups a user capability and exposes only the API needed for navigation or integration. Data modules implement persistence and remote access, often behind interfaces a feature or domain layer can see. A domain module is useful when business rules or contracts are genuinely shared or need Android-independent tests; I would not create one just to house empty forwarding classes. Core network/database modules provide stable infrastructure, while a design system provides visual tokens and components without knowing orders or payments. In an orders example, feature UI depends on an orders contract and design system; data implements the contract using core clients; app assembles them. I watch high-fan-out shared modules because public changes there trigger widespread work. The exact partition is a design choice driven by ownership, reuse and build evidence, with an acyclic graph and integration tests as guardrails.”

## Deep-dive talking points

Explain ownership, dependency edges, app composition, optional domain, shared API fan-out, and UI neutrality.

## Follow-up questions

- Must every app have a domain module? **Answer:** no; add it when reusable policies or contracts justify the boundary.
- Should design system import an Order entity? **Answer:** no; it should accept UI-level values or state.
- Who selects the concrete repository? **Answer:** the app composition graph or an owned DI binding module.

## Self-check rubric

Assign six module roles, draw an acyclic orders path, and identify one over-shared module smell.

## References and reviewed-on date

- [Android modularization guide](https://developer.android.com/topic/modularization) — module ownership.
- [Common modularization patterns](https://developer.android.com/topic/modularization/patterns) — feature/data structures.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. Module names are conventions, not platform requirements.
