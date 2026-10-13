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

ما هي الـ Build Cache، والـ Configuration Cache، والـ Incremental Compilation في Gradle، وكيف تضاعف سرعة البناء؟

1. الـ Incremental Compilation (التجميع التزايدي):
   - عند تعديل سطر واحد في كلاس، لا داعي لإعادة تجميع المشروع بأكمله!
   - المترجم يفحص ملفات الإدخال (Inputs)، ويعيد تجميع الكلاسات المعدلة والكلاسات التي تعتمد عليها مباشرة فقط (ABI changes)، متخطياً باقي الكلاسات.

2. الـ Build Cache (ذاكرة تخزين مخرجات المهام):
   - يقوم بحفظ مخرجات الـ Tasks في كاش محلي أو عن بُعد (Remote Cache) بناءً على بصمة تشفيرية (Hash) لمدخلات المهمة.
   - إذا طلبت من Gradle تشغيل مهمة (مثل `compileReleaseKotlin`) وكانت نفس المدخلات قد تم تجميعها سابقاً (على جهازك أو على سيرفر الـ CI)، يقوم Gradle بتخطي التنفيذ فوراً واستعادة المخرجات (`FROM-CACHE`) في أجزاء من الثانية!

3. الـ Configuration Cache (كاش مرحلة الإعداد):
   - مرحلة الـ Configuration في Gradle تقوم بقراءة كل ملفات `build.gradle.kts` وبناء الـ Task Graph، وهذا يستغرق 10-30 ثانية في المشاريع الضخمة حتى قبل بدء البناء!
   - الـ Configuration Cache يقوم بحفظ الـ Task Graph بالكامل على القرص؛ في المرات التالية، يتخطى Gradle مرحلة الـ Configuration ويبدأ تنفيذ المهام فوراً (`Configuration cache entry reused`).

## Practical walkthrough

تفعيل الـ Configuration Cache والـ Build Cache وتحسين أداء Gradle في gradle.properties:
```properties
# 1. تفعيل الـ Configuration Cache لتخطي مرحلة تقييم ملفات Gradle:
org.gradle.configuration-cache=true

# 2. تفعيل الـ Build Cache المحلي والمشترك:
org.gradle.caching=true

# 3. تفعيل المعالجة المتوازية للمشاريع المستقلة في وقت واحد:
org.gradle.parallel=true

# 4. زيادة حجم ذاكرة الـ JVM المخصصة لـ Gradle Daemon وتسريع جمع المهملات:
org.gradle.jvmargs=-Xmx6g -XX:+UseParallelGC -Dfile.encoding=UTF-8

# 5. تفعيل مراقبة نظام الملفات لتجنب إعادة فحص الملفات غير المعدلة:
org.gradle.vfs.watch=true
```

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

Incremental compilation recompiles only modified source files and their dependents. Build cache stores and reuses task outputs locally or across CI based on input hashes. Configuration cache serializes the Gradle task graph to disk, skipping the entire project configuration phase on subsequent builds.

## Interview answer — structured

Optimizing Gradle performance relies on understanding the distinct layers of build caching:

1. **Incremental Compilation**:
   - Operates within a single compiler task (e.g. `compileKotlin`). Analyzes source file change sets (diffs). If a private method body is modified without changing public ABI signatures, only that file recompiles, sparing dependent modules from recompilation.

2. **Build Cache (`org.gradle.caching=true`)**:
   - Caches the physical output artifacts of entire Gradle tasks. Generates a composite SHA-256 hash across task inputs (source files, compiler arguments, dependencies). If an identical hash is found in the local cache or remote CI cache, Gradle skips task execution entirely and displays `FROM-CACHE`.

3. **Configuration Cache (`org.gradle.configuration-cache=true`)**:
   - Caches the output of Gradle's Configuration phase. Evaluating dozens of `build.gradle.kts` files to construct the task execution graph often takes 15–30 seconds. Configuration caching serializes this execution graph to disk, executing directly on subsequent runs.

## Interview answer — deep senior

From an advanced build infrastructure engineering viewpoint, caching requires strict hygiene to avoid cache invalidation:

1. **Configuration Cache Invalidation Hazards**: Custom tasks or plugins that access the `Project` instance during the execution phase, read environment variables dynamically without `providers.environmentVariable()`, or inspect system timestamps break Configuration Caching. Audit builds with `./gradlew build --configuration-cache-problems=warn`.

2. **Cache Key Determinism & Non-Hermetic Builds**: Build caching fails if task inputs contain non-deterministic data. A common mistake is injecting current timestamps (`System.currentTimeMillis()`) into `BuildConfig.BUILD_TIME`. This changes input hashes on every execution, completely blowing up remote and local build caching.

3. **Remote Build Cache Strategy in CI**: Configure CI pipelines to populate a centralized HTTP build cache (e.g., Gradle Enterprise or self-hosted Docker cache) on every merged PR. Developers pulling the latest main branch download precompiled binaries, turning 15-minute builds into 45-second cache fetches.

## How to answer in the interview

- **Why:** build time has different phases.
- **How:** profile cache misses and configuration cost.
- **Trade-off:** speed versus reproducibility.
- **Failure case:** stale output from undeclared input.
- **Production solution:** measure and verify clean build parity.

## Deep-dive talking points

Discuss task fingerprints, configuration serialization, ABI invalidation, cache correctness, secrets and measurement.

## Follow-up questions

- **Interviewer:** "What is UP-TO-DATE vs FROM-CACHE in Gradle task execution?"
  **Answer:** "UP-TO-DATE means task inputs did not change since the last local run in the current workspace; FROM-CACHE means outputs were loaded from the local or remote build cache."

- **Interviewer:** "Why does injecting dynamic timestamps in BuildConfig break build caching?"
  **Answer:** "Because the timestamp alters the compiler input arguments on every run, changing the task input hash and forcing a full recompilation."

## Self-check rubric

Map three optimizations to stages, identify a stale-output risk, and define a build metric.

## References and reviewed-on date

- [Gradle build cache](https://docs.gradle.org/current/userguide/build_cache.html) — task-output reuse.
- [Gradle configuration cache](https://docs.gradle.org/current/userguide/configuration_cache.html) — configuration state.
- [Gradle incremental builds](https://docs.gradle.org/current/userguide/incremental_build.html) — changed inputs.

Technically reviewed against primary documentation on 2026-10-13.
