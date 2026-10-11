---
id: "MOD-20"
question: "How do you migrate a monolith to modules without blocking feature delivery?"
topic: "Gradle Modularization & Dependency Boundaries"
code: "MOD"
group: "C"
phase: 4
priority: "P1"
order: 373
editorial_status: "reviewed"
---

# MOD-20

## Original interview question

How do you migrate a monolith to modules without blocking feature delivery?

## What the interviewer evaluates

- Offer an incremental vertical-slice migration and measurable gates.
- Keep app behavior and tests stable during dual wiring.
- Handle dependency cycles, DI/navigation and rollback.

## Explanation in Arabic

ابدأ audit للdependencies وbuild times وأماكن ownership. ضع module rules وأول seam مستقرة، ثم استخرج feature واحدة كاملة مع API صغيرة بدل نقل كل `utils` إلى core. أثناء النقل حافظ على public behavior، اختبارات/فakes وnavigation، واجعل app composition تدمج القديم والجديد. امنع cycle بإصلاح العقد لا بإخفائها، وشغّل full variant build. الفريق يواصل features عبر migration تدريجية وflag/adapter محدود العمر. قِس build/CI ووقت تعديل feature قبل وبعد، واحذف مسار قديم بعد انتقال كل callers.

## Why it matters and how it works

A monolith often contains implicit cross-package dependencies, so a big-bang split reveals many cycles at once. Extracting one vertical capability exposes a manageable contract and lets remaining code continue to ship. Adapter seams can preserve calls temporarily while new module boundaries are adopted. An explicit deletion condition prevents temporary bridges from becoming permanent architecture.

## Worked example

An app starts with Orders. First create a stable `OrderId`/repository API and move Orders UI, ViewModel and owned data behind it, while app registers its destination. Existing notification links still use a compatibility route mapped to the new entry. CI builds debug/release and tests a notification deep link. Next migrate callers and delete the old Orders package and adapter.

## Trade-offs and decision criteria

Incremental migration leaves temporary duplication and wiring, but limits product risk. Big-bang rewrite can reach a clean graph faster only with high capacity and stable requirements; it blocks delivery and widens regression risk. Choose a first feature with clear ownership and moderate complexity, not the most entangled payment flow.

## Failure modes

Files move without public API design, so every import becomes `api`. The old and new DI containers create different session instances. Redirect adapters persist indefinitely. CI tests only the extracted module while app variants fail. Metrics show worse build time but the team keeps splitting anyway.

## Production perspective

Track migration checklist, owner, old-caller count, graph rules, build metrics and rollback plan per slice. Run unit, integration and app assembly tests at each boundary; remove dead paths promptly.

## Interview answer — short

“I baseline the graph and builds, extract one cohesive vertical feature behind a small contract, keep compatibility while callers move, test the full app, then delete old wiring.”

## Interview answer — structured

“I would not pause all delivery for a full rewrite. I map dependencies and choose a bounded feature such as Orders, design its public API, move its UI and data ownership, and let app composition bridge existing routes. Tests and release variants continue to run during migration. I enforce no new reverse dependencies, measure compile and team impact, and retire temporary adapters after the last caller moves.”

## Interview answer — deep senior

“A monolith-to-modules migration is safest as a sequence of behavior-preserving boundary changes. I first collect a dependency graph, build-time baseline, ownership map and integration tests for critical flows. Then I select one cohesive, moderate-risk feature with a clear entry point and define the smallest API it should expose. I move a vertical slice—screen state, use case and owned data access—rather than scatter random utility files into core. The app composition root registers its navigation and DI bindings; a temporary adapter can keep old callers working while they migrate. I watch for duplicate shared state if both old and new containers construct a session service. Each slice has a full debug/release build and user-flow test, not only module tests, and a rollback path if release behavior changes. I prohibit new reverse imports so the graph improves rather than oscillates. Finally I delete old code once its caller count reaches zero, compare incremental build and delivery metrics, and adjust the next boundary. This lets feature teams ship while architecture changes in reviewable increments.”

## Deep-dive talking points

Discuss baseline, first slice selection, compatibility adapters, DI identity, no-cycle rules, deletion and metrics.

## Follow-up questions

- What makes a good first feature? **Answer:** clear ownership and moderate coupling/risk so the boundary can be proven.
- Why delete temporary adapters? **Answer:** they otherwise preserve old coupling and dual paths indefinitely.
- What test is essential beyond feature tests? **Answer:** full app variant assembly and an integrated user route.

## Self-check rubric

Give an incremental sequence, identify dual-wiring risk, define gate evidence and adapter removal.

## References and reviewed-on date

- [Android modularization guide](https://developer.android.com/topic/modularization) — phased boundaries.
- [Guide to app architecture](https://developer.android.com/topic/architecture) — ownership layers.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. Migration sequence is an engineering recommendation.
How do you migrate a monolith to modules without blocking feature delivery?
