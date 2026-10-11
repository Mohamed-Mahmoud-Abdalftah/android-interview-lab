---
id: "MOD-15"
question: "How do api/implementation influence compilation boundaries and rebuilds?"
topic: "Gradle Modularization & Dependency Boundaries"
code: "MOD"
group: "B"
phase: 4
priority: "P1"
order: 368
editorial_status: "reviewed"
---

# MOD-15

## Original interview question

How do api/implementation influence compilation boundaries and rebuilds?

## What the interviewer evaluates

- Trace ABI exposure and consumer compile classpath.
- Explain incremental rebuild effects without absolute guarantees.
- Diagnose a concrete high-fan-out dependency change.

## Explanation in Arabic

`api` تصدر dependency للمستهلك على compile classpath؛ لو public ABI تعتمد على type منها، هذا لازم. `implementation` تخفي dependency كـتفصيل داخلي من compile classpath للمستهلك، ما قد يقلل recompilation عند تغيير implementation. لكن تأثير build ليس قانونًا ثابتًا: تغيير public ABI، annotation processors، Kotlin inline functions، resource/variant tasks أو configuration قد يوسع العمل. قِس Gradle task execution/build scan قبل وبعد، ولا تحول `api` إلى `implementation` إذا consumer يحتاج type في signature.

## Why it matters and how it works

Gradle computes compile inputs per module. API dependencies widen what consumers compile against; internal implementation dependencies need not. An ABI-stable private change can stay local, while modifying exported types invalidates downstream consumers. Android builds add resource and variant tasks, so a graph improvement may not dominate total wall time.

## Worked example

`:core:payments` publicly returns `ProviderResponse` from an SDK declared `api`, causing checkout and orders compile classpaths to include that SDK. Replace the public response with owned `PaymentResult` and declare SDK `implementation`. A private provider adapter update now need not force API consumers to compile against SDK types. Verify task graphs on a warm incremental build.

## Trade-offs and decision criteria

Hiding a dependency stabilizes architecture but adds mapping code. An `api` dependency is correct when public signatures genuinely expose its types. Fewer compile classpath entries can help builds, but module configuration and code generation may still dominate; optimize based on actual build scans.

## Failure modes

A public type remains exposed after switching to implementation and consumer compilation fails. An inline public function leaks an implementation detail. Teams benchmark clean builds only, missing incremental effects. An `api` edge is kept for convenience so consumers accidentally import internal SDK classes.

## Production perspective

Track ABI changes and affected compile tasks for high-fan-out modules, inspect dependency reports, and compare clean and incremental builds with controlled caches. Review `api` additions as contract changes.

## Interview answer — short

“`api` broadens consumer compile inputs; `implementation` hides internal dependencies. Narrow public ABI can reduce downstream rebuilds, but actual impact must be measured.”

## Interview answer — structured

“I follow the public signature. If a library returns an SDK type, consumers need that SDK on their compile classpath, so `api` is justified. If the SDK is hidden behind our result type, `implementation` narrows the boundary. Then a private SDK change may stay local, while an ABI change still recompiles consumers. I inspect build scans because Android resource, codegen and configuration work can dominate despite a cleaner dependency graph.”

## Interview answer — deep senior

“Gradle's `api` versus `implementation` choice changes who must compile against a dependency. `api` is part of the library's exported compile contract; `implementation` is internal, although needed runtime code remains available. Consider a high-fan-out payment module that returns a provider response directly: every consumer sees that SDK's types, and provider API changes may ripple widely. If I introduce a small owned `PaymentResult` contract, the provider SDK can become an implementation detail. That improves replacement freedom and can shrink downstream compile inputs. I still verify the ABI, including public generic types, supertypes and inline Kotlin behavior, before changing configuration. Incremental build results are not guaranteed by one keyword: annotation processing, Android resources, variant tasks, compiler settings and caches all affect what reruns. I compare controlled clean and warm incremental builds and inspect executed tasks in a build scan. The goal is a correct narrow API and measured build reduction, not blindly converting every `api` declaration.”

## Deep-dive talking points

Discuss ABI, compiler inputs, high fan-out, inline/codegen caveats, task graph and build measurement.

## Follow-up questions

- Can `implementation` hide a public SDK return type safely? **Answer:** no; consumers must compile against the exposed type.
- Does a private code change always rebuild only one module? **Answer:** not necessarily; build tooling and generated/resource tasks can expand work.
- Which build should you measure? **Answer:** both controlled clean and representative incremental builds.

## Self-check rubric

Trace a public type leak, propose an API boundary, and compare task graphs empirically.

## References and reviewed-on date

- [Gradle Java Library Plugin](https://docs.gradle.org/current/userguide/java_library_plugin.html) — API/implementation semantics.
- [Gradle performance guide](https://docs.gradle.org/current/userguide/performance.html) — measured build behavior.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. Kotlin/Android task behavior is toolchain-specific.
How do api/implementation influence compilation boundaries and rebuilds?
