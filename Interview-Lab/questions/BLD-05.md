---
id: "BLD-05"
question: "What are build cache, configuration cache, and incremental compilation?"
topic: "Gradle, AGP, R8, Signing & Release Engineering"
code: "BLD"
group: "A"
phase: 4
priority: "P1"
order: 379
editorial_status: "reviewed"
---

# BLD-05

## Original interview question

What are build cache, configuration cache, and incremental compilation?

## What the interviewer evaluates

- Distinguish task-output reuse, configuration reuse and compiler-level changed work.
- Explain correct inputs/outputs and compatibility constraints.
- Measure clean versus warm builds and cache misses.

## Explanation in Arabic

Build cache تعيد استخدام outputs لمهمة إذا inputs المعلنة ونوع المهمة متطابقان، محليًا أو من remote cache. Configuration cache تحفظ نتيجة configuration/task graph لتتجنب إعادة تكوين build في invocation لاحقة عندما المدخلات المعنية لم تتغير. Incremental compilation تقلل ما يعيد compiler ترجمته بعد تغيير source/ABI. الثلاثة مستويات مختلفة وقد تفشل لأسباب مختلفة. Task تقرأ ملفًا غير معلن أو environment secret أثناء configuration قد تفسد reproducibility/compatibility؛ افحص Gradle reports وbuild scan، ولا تفترض أن تشغيل cache يجعل كل build سريعًا.

### Practical walkthrough in Egyptian Arabic

Build cache يعيد task outputs عند مطابقة inputs، configuration cache يعيد نتيجة configuration، incremental compilation يقلل إعادة compile عند تغير جزء من الكود. قس Build Scan قبل تفعيل toggles عشوائيًا؛ plugin غير متوافق قد يعطل cache، وtask لا يعلن input صحيحًا قد يعطي stale output. قارن cold/warm وCI runner ثابت، وراقب cache hit وcorrectness.

## Why it matters and how it works

Gradle computes task input fingerprints to decide up-to-date or cache reuse. Configuration cache serializes configured task state with compatibility requirements. Compiler incremental analysis tracks source dependencies and ABI changes within and across modules. A broad public API change can invalidate many compile units even if caches work correctly.

## Worked example

CI builds `:feature:orders` twice with no changes: configuration cache can skip reconfiguration and tasks can be UP-TO-DATE or loaded from build cache. Changing a private Kotlin function may recompile limited code; changing a public model used by many modules expands compilation. A custom codegen task missing a declared schema input can incorrectly reuse stale output and must be fixed before caching.

## Trade-offs and decision criteria

Remote cache can save team/CI time but needs secure trust and correct task declarations. Configuration cache requires plugins/tasks to avoid unsupported configuration-time behavior. Incremental compilation helps frequent edits but may not help clean builds. Diagnose cache hit rate and critical path rather than enabling flags blindly.

## Failure modes

A task reads an undeclared file and returns stale cached output. Secrets are captured in configuration-cache state. A plugin is incompatible and configuration cache is silently disabled. A public ABI change triggers broad recompilation despite successful task caching elsewhere.

## Production perspective

Pin toolchain, review task inputs/outputs, run cache correctness checks, and monitor configuration time, cache hit rate and incremental build wall time. Keep remote cache access controlled and investigate misses via reports.

## Interview answer — short

“Build cache reuses task outputs, configuration cache reuses configured build state, and incremental compilation limits compiler work after source changes.”

## Interview answer — structured

“These optimize different stages. The build cache retrieves a task result for matching declared inputs; configuration cache avoids repeating Gradle configuration when compatible; incremental compilation recompiles only affected code where the compiler can do so. A private edit may be cheap while a public ABI change fans out. I check input declarations and cache reports, measure clean and warm builds, and avoid capturing secrets during configuration.”

## Interview answer — deep senior

“I separate configuration time, task execution and compiler work. Gradle's build cache stores outputs of cacheable tasks by input fingerprint, so correct declared inputs are essential; a task reading an undeclared schema file can produce a fast but wrong build. Configuration cache serializes the configured task graph and related state so a later invocation can skip much of configuration, provided plugins and tasks follow its rules. Incremental compilation is a compiler-level strategy for changed sources and dependent ABI, independent of whether a task output is loaded from cache. In a multi-module Android build I inspect a representative warm edit: a private function change may affect one compiler task, while a public model or inline API change can fan out. I use build scans or Gradle reports to identify configuration cost, task cache misses and compile invalidation separately. Remote cache is useful only with controlled access and reproducible task inputs. I also avoid resolving sensitive credentials in configuration because cache state may capture them. I measure the critical path before enabling or refactoring build logic.”

## How to answer in the interview

- **Why:** build time has different phases.
- **How:** profile cache misses and configuration cost.
- **Trade-off:** speed versus reproducibility.
- **Failure case:** stale output from undeclared input.
- **Production solution:** measure and verify clean build parity.

## Deep-dive talking points

Discuss task fingerprints, configuration serialization, ABI invalidation, cache correctness, secrets and measurement.

## Follow-up questions

- Can a build cache fix an undeclared task input? **Answer:** no; it can reuse stale output unless the task declares inputs correctly.
- Does configuration cache store compiled classes? **Answer:** its main role is configured build state, not compiler artifacts.
- Why might a public model edit remain slow? **Answer:** ABI changes can invalidate many downstream compilations.

## Self-check rubric

Map three optimizations to stages, identify a stale-output risk, and define a build metric.

## References and reviewed-on date

- [Gradle build cache](https://docs.gradle.org/current/userguide/build_cache.html) — task-output reuse.
- [Gradle configuration cache](https://docs.gradle.org/current/userguide/configuration_cache.html) — configuration state.
- [Gradle incremental builds](https://docs.gradle.org/current/userguide/incremental_build.html) — changed inputs.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. Kotlin compiler incremental details vary by version.
