---
id: "SYS-19"
question: "Your app has 20 feature teams and takes 25 minutes to build. How do you redesign team ownership and dependencies?"
topic: "Android System Design & Architecture Decisions"
code: "SYS"
group: "C"
phase: 4
priority: "P1"
order: 348
editorial_status: "reviewed"
---

# SYS-19

## Original interview question

Your app has 20 feature teams and takes 25 minutes to build. How do you redesign team ownership and dependencies?

## What the interviewer evaluates

Redesign ownership and dependency graph for 20 teams with 25-minute builds based on profiling.

## Explanation in Arabic

أولًا نقيس 25 دقيقة: configuration, dependency resolution, Kotlin compile, kapt/KSP, resources, tests ولا network؟ بعدها نرسم module graph وchange impact. نحدد feature ownership وstable API modules صغيرة، نمنع cycles وgiant core، ونستخدم `implementation` بدل `api` لما type مش public. convention plugins/version catalog تقلل اختلاف الإعدادات، وCI يعمل targeted tests مع full gates دوريًا. لا نَعِد بتحسن قبل benchmark.

## Practical walkthrough

25 دقيقة build مش معناها تلقائيًا نعمل modules أكثر. قس configuration وKotlin compile وKSP/resources/tests في clean/no-op/one-feature edit. لو `:core:model` عليها كل features، أي تغيير فيها يسبب fan-out؛ اقسم stable APIs وحدود ownership، وأصلح broad `api` edges. جرّب configuration cache وbuild cache حسب قياس، وقارن median وP95، مش أحسن run واحدة.

## Why it matters and how it works

Gradle build scans/profile, configuration cache and build cache diagnostics reveal hotspots. A module split can reduce incremental rebuild but increase configuration overhead; public API changes invalidate downstream compile. Team ownership needs contract versioning and app composition root, not just folder names.

## Worked example

Conceptual module dependency sketch; actual graph and timings must be measured in the repository.

```kotlin
// :app -> :feature:catalog, :feature:checkout, :feature:account
// :feature:checkout -> :core:payments-api, :core:ui
// :data:payments -> :core:payments-api, :core:network
// Keep implementation edges private; CI compares affected targets per change.
```

## Trade-offs and decision criteria

Build cache and configuration cache can help repeated work but require compatible deterministic tasks. Excess modules may worsen clean builds; too few cause broad recompilation. Targeted tests speed feedback but cannot replace end-to-end release gates.

## Failure modes

A shared model in giant core changes weekly and recompiles 20 features. Annotation processors with non-incremental tasks dominate builds. Parallel teams edit one app Gradle file and create merge bottlenecks. A cosmetic split without metrics can make all of these worse.

## Production perspective

A large retail org assigns feature owners, extracts stable contracts, replaces broad api dependencies, centralizes build conventions and measures clean/incremental builds by change type. CI keeps a full nightly/release gate plus fast affected-module feedback.

## Interview answer — short

“I profile the 25-minute build first, then shrink dependency and API change impact with cohesive team-owned modules, private implementation dependencies and shared conventions. I measure before and after; modularity alone is not a speed guarantee.”

## Interview answer — structured

“With 20 teams I separate build-system bottlenecks from architecture bottlenecks. I collect build scans for configuration, compilation, annotation processing, resources and tests; then inspect the dependency graph and which changes recompile which modules. I give teams cohesive feature ownership, narrow shared APIs and an acyclic app composition root. I use `implementation` when dependencies need not leak, version catalogs/convention plugins for consistent config, and targeted CI feedback alongside full release tests. I validate improvements against clean and incremental scenarios rather than promising a number.”

## Interview answer — deep senior

“A 25-minute build is a symptom, so I would first separate clean build, no-op build, and representative changes in one feature versus a shared model. A build scan can show configuration, KSP or kapt, resource processing, Kotlin compilation and test time. I would map the dependency graph and ask which edges cause a small change to recompile half the app. Then I would align modules with stable feature ownership, expose narrow API modules, keep `:app` as composition root, use `implementation` unless a type is part of a public signature, and prohibit cycles. I would pilot one split and compare median and P95 incremental builds, cache hits and integration-test time before expanding. The organizational side matters too: every public contract needs an owner, review policy and migration window, or teams simply move coupling into shared interfaces. CI can run affected tests quickly while retaining a full release gate. I would set a build-time budget and track regressions, because improving one local command at the expense of flaky integration or longer configuration time is not success.”

## How to answer in the interview

- **Why:** build time is a symptom of dependency and task behavior.
- **How:** profile representative edits, map fan-out, and assign module owners.
- **Trade-off:** fine modules may worsen configuration overhead.
- **Failure case:** splitting files without changing dependency edges.
- **Production solution:** build dashboards, graph rules, and incremental rollout with measured results.

## Deep-dive talking points

Analyze one build scan, one graph hotspot and a before/after measurement plan.

## Follow-up questions

- [MOD-18](../mod-18/): Why model change rebuilds many? **Answer:** public API exposure and dependency fan-out.
- [BLD-05](../bld-05/): Which caches help? **Answer:** configuration/build cache and incremental compilation when tasks are compatible.

## Self-check rubric

Can I profile first, shrink fan-out, measure real gains and keep release coverage?

## References and reviewed-on date

- [Android modularization guide](https://developer.android.com/topic/modularization) — module graph.
- [Gradle performance](https://docs.gradle.org/current/userguide/performance.html) — profiling/caches.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-13; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
