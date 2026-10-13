---
id: "BLD-15"
question: "How do you investigate dependency version conflicts and build-speed regressions?"
topic: "Gradle, AGP, R8, Signing & Release Engineering"
code: "BLD"
group: "B"
phase: 4
priority: "P1"
order: 389
editorial_status: "reviewed"
---

# BLD-15

## Original interview question

How do you investigate dependency version conflicts and build-speed regressions?

## What the interviewer evaluates

- Use dependency graph/insight to identify selected version and requester.
- Measure configuration, resolution and task execution separately.
- Fix root cause with constraints or aligned upgrades, not arbitrary force.

## Explanation in Arabic

في version conflict، ابدأ بالـconfiguration والvariant المتأثرين؛ `dependencies` و`dependencyInsight --dependency ... --configuration ...` يبينان من طلب كل نسخة ولماذا اختار Gradle نسخة. راجع BOM/constraints وmetadata، وتحقق من runtime behavior لا compilation فقط. لبُطء build قارن baseline مع build scan/profile: configuration، dependency downloads، codegen، Kotlin compile، R8، tests. لا تفترض أن آخر library أضفتها هي السبب؛ جرّب تغييرًا مضبوطًا وحدد critical path/cache misses. تجنب `force` عشوائي يخفي binary incompatibility.

## Practical walkthrough

Dependency conflict قد يظهر duplicate class أو runtime `NoSuchMethodError`؛ افحص dependency graph والconstraints، لا تضف force version قبل معرفة من يطلبها. Build slowdown قد يأتي من plugin upgrade أو task invalidation؛ قس before/after بـBuild Scan. قفل النسخ والتحقق من dependencies يقلل surprise. اختبر release/minified variant بعد align لأنه قد يكشف native/R8 differences.

## Why it matters and how it works

Gradle resolves one selected component version per configuration under its rules and constraints. Different variants can have different graphs. Build wall time includes configuration and parallel task critical path, not just sum of tasks; a regression may be network resolution, ABI fan-out, annotation processing or cache invalidation. Evidence from task graphs and controlled runs makes optimization targeted.

## Worked example

`:app:prodReleaseRuntimeClasspath` selects a newer JSON library than a payment SDK expects. `dependencyInsight` shows direct app request plus SDK transitive request. The team checks compatible releases or an explicit tested constraint, then runs minified payment integration. Separately, a 40% build slowdown is traced to a new codegen task running every time because it declares an unstable input; fixing inputs restores cache hits.

## Trade-offs and decision criteria

Aligning to a BOM simplifies version coherence where one exists, but may require coordinated upgrades. A strict constraint prevents accidental drift yet can block necessary dependencies. Build scans may contain sensitive metadata and need appropriate access controls. Optimize local developer incremental flow and CI separately.

## Failure modes

`force` silences a conflict but creates runtime `NoSuchMethodError`. Engineers inspect debug graph while release differs. One clean build is compared to a warm cached build. An annotation processor adds broad invalidation but the team changes heap size instead. Dynamic versions make results hard to reproduce.

## Production perspective

Pin and verify dependencies, record selected versions by release variant, review constraints, and keep build performance baselines. Diagnose regressions with scans or task profiles and rerun compatibility tests after resolution changes.

## Interview answer — short

“I inspect the affected variant's dependency graph and `dependencyInsight`, then profile the build's critical path and cache misses before changing versions or build settings.”

## Interview answer — structured

“For a conflict I identify the exact configuration, selected version, request paths and selection reason with Gradle reports. I align compatible versions or add a justified constraint, then test the runtime path, especially minified release. For slow builds I compare controlled baseline runs and inspect configuration, downloads, codegen, compilation and R8 tasks. I fix the proven bottleneck rather than use a broad `force` or random JVM flags.”

## Interview answer — deep senior

“I separate correctness from speed but use the same evidence discipline. A dependency conflict is resolved per configuration, so I look at the failing release variant's compile or runtime classpath, run `dependencyInsight`, and trace every requester and the selected version. A forced version can make compilation green while an SDK later throws `NoSuchMethodError`, so I prefer compatible upgrades, a platform/BOM where applicable, or an explicit tested constraint. Then I exercise the affected runtime flow. For a build-speed regression I establish comparable warm and clean baselines with the same machine/toolchain and inspect a build scan or task profile. I locate configuration, dependency resolution, compiler/codegen, tests and R8 on the actual critical path. A new processor may invalidate many modules; a custom task with changing undeclared inputs may lose cache hits; neither is solved by blaming Gradle generally. I make one change, remeasure median/variance, and preserve a regression signal in CI. Dependency locks or verification can also prevent a later silent change.”

## How to answer in the interview

- **Why:** transitive changes affect behavior and speed.
- **How:** inspect graph and task profile.
- **Trade-off:** upgrade freshness versus compatibility.
- **Failure case:** forced version fixes compile but breaks runtime.
- **Production solution:** pin tested set and verify release.

## Deep-dive talking points

Discuss per-variant resolution, dependencyInsight, BOM/constraints, runtime linkage, build scan and critical path.

## Follow-up questions

- Can a forced version create runtime failure? **Answer:** yes; binary/API compatibility is not guaranteed by resolution success.
- Why inspect the release configuration? **Answer:** its graph may differ from debug and is the one shipped.
- Which build time matters? **Answer:** the measured critical path under a representative clean or incremental scenario.

## Self-check rubric

Trace a selected version, justify a fix, and profile one build regression with controlled evidence.

## References and reviewed-on date

- [Gradle dependency reports](https://docs.gradle.org/current/userguide/viewing_debugging_dependencies.html) — selection reasons.
- [Gradle build performance](https://docs.gradle.org/current/userguide/performance.html) — profiling and optimization.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. Example conflict is illustrative.
