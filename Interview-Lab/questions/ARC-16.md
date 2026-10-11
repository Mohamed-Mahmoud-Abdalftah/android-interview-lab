---
id: "ARC-16"
question: "Compare package-by-layer and package-by-feature."
topic: "Clean Architecture, MVVM, MVI & UDF"
code: "ARC"
group: "B"
phase: 2
priority: "P1"
order: 161
editorial_status: "reviewed"
---

# ARC-16

## Original interview question

Compare package-by-layer and package-by-feature.

## What the interviewer evaluates

Compare navigation, cohesion, ownership and Gradle module implications of two packaging strategies.

## Explanation in Arabic

Package-by-layer زي `ui/`, `domain/`, `data/` على مستوى app سهلة في البداية لكن feature واحدة بتتوزع على folders بعيدة. Package-by-feature زي `checkout/ui`, `checkout/data` تجمع الملفات اللي بتتغير مع بعض وتساعد ownership. في app كبيرة ممكن تعمل feature modules ومعاها shared core modules لعقود حقيقية؛ ما تعملش `core` garbage dump. تنظيم packages وحده ما يفرضش compile-time boundaries؛ Gradle module dependencies وvisibility/tests هي اللي تمنع imports غلط.

## Why it matters and how it works

Packaging improves discoverability and team ownership; modules can enforce dependency direction. Choose the shape that minimizes changes scattered across unrelated areas while preserving shared contracts.

## Worked example

Conceptual tree: `feature/checkout/{ui,data}` and `feature/profile/{ui,data}` with `core/model` for genuinely shared types. Compare with root `ui/checkout`, `data/checkout`, `domain/checkout`; both can work, but feature grouping keeps vertical work local.

## Trade-offs and decision criteria

Feature packages improve cohesion but can duplicate helpers until a real shared abstraction emerges. Layer packages make cross-cutting concerns visible but may scatter one feature. Do not split every package into a Gradle module without build/ownership benefit.

## Failure modes

A team creates `common/Utils.kt` used by all features, introducing hidden coupling and a huge rebuild hotspot. Another mistake is assuming package names stop UI from importing Room; enforce with modules or architecture checks.

## Production perspective

A marketplace organizes checkout, search and account by feature; shared payment domain contracts live in a small core module. Dependency checks prevent checkout UI from importing another feature’s data implementation.

## Interview answer — short

Package-by-layer groups technical roles; package-by-feature groups files that change together. For a growing app I often favor feature cohesion with explicit shared modules, but packages alone do not enforce boundaries.

## Interview answer — structured

A layer-first tree makes it easy to find all repositories or ViewModels, but working on checkout may require jumping across the whole tree. Feature-first grouping keeps a vertical slice together and clarifies ownership. In larger apps I combine feature modules with a few truly shared core contracts. I avoid turning `core` into a dumping ground. The important distinction is that a package layout is navigation, while Gradle modules and visibility can enforce dependency rules. If checkout changes usually touch its UI, data mapping and tests together, feature grouping makes reviews and ownership easier. A shared module should contain stable contracts used by several features, not every miscellaneous helper. I would reserve separate Gradle modules for meaningful isolation.

## Interview answer — deep senior

I choose organization based on team workflow and change coupling. If most commits touch UI, domain, and data for one feature, grouping those files improves discoverability and review. If a cross-cutting platform layer changes independently, a dedicated module can make sense. Feature modules can help parallel ownership and incremental builds, but too many tiny modules add configuration and build overhead. Package names are not a substitute for boundaries: Kotlin code can import across packages unless visibility or module dependencies prevent it. I would define allowed module edges, keep shared contracts small, and periodically audit the `common` area for accidental centralization. The design should make changes local without making simple code hard to find. There is a build-system dimension beyond file navigation. Gradle edges can prevent one feature from importing another feature’s implementation, while packages alone cannot. More modules may improve parallel build behavior in some codebases but add configuration and dependency management; I would measure. I keep `internal` visibility where possible and audit shared modules for becoming a dumping ground. The best layout helps a new engineer find a feature and lets a team change it without surprising cross-feature rebuilds.

## Deep-dive talking points

Draw a feature tree and layer tree for checkout; identify where module rules differ from mere packages.

## Follow-up questions

- [ARC-26](../arc-26/): What enforces boundaries? **Answer:** module graph, visibility and architecture checks rather than package names alone.
- [ARC-23](../arc-23/): Can modules overengineer a small app? **Answer:** yes, if configuration cost exceeds change isolation.

## Self-check rubric

Explain one benefit and cost of each layout, plus one mechanism that enforces dependency direction.

## References and reviewed-on date

- [Android modularization guide](https://developer.android.com/topic/modularization) — module organization and trade-offs.
- [Android architecture guide](https://developer.android.com/topic/architecture) — layer concerns.

Technically reviewed against the linked official Android guidance on 2026-10-11. Conceptual examples are not device-tested.
