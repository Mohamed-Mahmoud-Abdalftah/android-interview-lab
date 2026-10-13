---
id: "SYS-02"
question: "Design a scalable multi-feature Android application."
topic: "Android System Design & Architecture Decisions"
code: "SYS"
group: "A"
phase: 4
priority: "P1"
order: 331
editorial_status: "reviewed"
---

# SYS-02

## Original interview question

Design a scalable multi-feature Android application.

## What the interviewer evaluates

Design scalable multi-feature Android app with team boundaries, data ownership and build health.

## Explanation in Arabic

تطبيق كبير محتاج boundaries حسب features والملكية، مش مجرد 100 modules. نحدد `:app` composition، feature modules للواجهات، core صغيرة لقدرات مشتركة، data repositories تملك المصادر، وdomain layer فقط لو business logic مشتركة/معقدة. UI تستقبل immutable state وتبعث events، وdependencies تبقى acyclic. نستثمر في contracts, CI, build metrics وrelease ownership بين الفرق.

## Practical walkthrough

في تطبيق فيه catalog وcheckout وaccount، خَلّي `:app` يركب الـnavigation والـDI، وكل feature تملك UI وpublic contract صغير. الـrepository تملك local/remote data، وbackend يملك قرارات payment. لو عشر فرق بتعدل `:core` في كل feature، ده مش modularization ناجحة؛ اقسّم حسب ownership وحدود التغيير، وقس incremental build والـdependency graph قبل وبعد.

## Why it matters and how it works

Android architecture recommends UI/data layers and optional domain. Modularization can improve separation and parallel team work but adds configuration and API maintenance cost. Use stable public interfaces for cross-feature communication and navigation contracts. Local data source of truth and server APIs remain explicit.

## Worked example

Conceptual Gradle module graph, not executable code; arrows mean compile-time dependency.

```kotlin
// :app -> :feature:catalog, :feature:checkout
// :feature:checkout -> :core:payments-api, :core:ui
// :data:payments -> :core:payments-api, :core:network
// :app binds payments-api to data:payments in DI.
// No feature depends directly on another feature implementation.
```

## Trade-offs and decision criteria

A monolith is simpler for a small team; split when ownership, reuse or build isolation pays for added configuration. Avoid a giant core/common module that every change recompiles. Measure build time and coupling before/after split.

## Failure modes

Cross-feature concrete dependencies create cycles and block independent releases. Duplicated token/session ownership yields inconsistent logout. A feature owning server DTOs in UI makes backend version changes cascade through screens.

## Production perspective

A 20-team commerce app has team-owned feature APIs, central session/payment contracts, local Room data ownership and independent feature tests. CI measures dependency graph and incremental builds; release trains stage high-risk payment changes.

## Interview answer — short

“I start with clear UI/data ownership, optional domain logic and an acyclic module graph. Features own screens; small core APIs hold stable shared contracts; the app composes implementations. I measure build and team outcomes rather than modularizing by fashion.”

## Interview answer — structured

“For a large multi-feature app I define one source of truth per data type, ViewModel state holders for UI, repositories for data/business rules and domain use cases only when shared logic warrants them. Modules follow team/feature ownership with stable cross-feature interfaces and acyclic dependencies. The app composition root binds implementations. I keep core modules small, centralize session and network policy, and establish CI contracts, integration tests and build metrics. A small app can stay monolithic until the split solves a real problem.”

## Interview answer — deep senior

“Scalability has runtime and organizational dimensions. Runtime design uses persistent models, offline behavior, bounded concurrency and server-authoritative contracts. Team design uses feature ownership and a dependency graph that prevents implementation coupling: feature modules expose narrow APIs, data modules implement repositories, and the app wires them together. I avoid a giant core/common jar that becomes a recompilation and review bottleneck. I define navigation/deep-link contracts, DI boundaries, API compatibility checks and test fixtures that allow teams to work independently. I track clean/incremental build time, cycle violations, change lead time, crash/ANR metrics and ownership incidents; I split or merge modules based on those measurements. Duplicated token/session ownership yields inconsistent logout. I would validate the module graph with real change scenarios: how many modules recompile when checkout changes, who approves a payments API change, and whether a feature can be tested without the whole app. The app module composes implementations; feature modules consume contracts instead of importing each other's internals. Runtime scale still needs bounded requests, database design and backend capacity. A 100-module build with a giant shared core is organizationally expensive without delivering isolation.”

## How to answer in the interview

- **Why:** runtime and team scaling both depend on boundaries.
- **How:** define feature owners, narrow APIs, acyclic dependencies, and data authority.
- **Trade-off:** modules add Gradle and contract maintenance costs.
- **Failure case:** a giant shared core or feature-to-feature implementation dependency.
- **Production solution:** measure change impact and build time, then split at stable ownership seams.

## Deep-dive talking points

Draw acyclic graph with owners; defend where shared domain code lives and how CI measures benefit.

## Follow-up questions

- [MOD-07](../mod-07/): What module graph fits a large app? **Answer:** feature-owned nodes with narrow shared APIs and app composition.
- [SYS-19](../sys-19/): How address 25-minute builds? **Answer:** measure hotspots and shrink dependency/change impact.

## Self-check rubric

Can I assign data/team ownership, draw acyclic dependencies and identify runtime/build metrics?

## References and reviewed-on date

- [Android architecture guide](https://developer.android.com/topic/architecture) — UI/data layers and SSOT.
- [Android modularization guide](https://developer.android.com/topic/modularization) — module boundaries.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-13; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
