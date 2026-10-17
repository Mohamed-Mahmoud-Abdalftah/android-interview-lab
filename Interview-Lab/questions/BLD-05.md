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

## Concept and technical explanation

Gradle accelerates multi-module build velocity through three distinct optimization tiers operating across different phases of the build lifecycle:
- Incremental Compilation: Operates within specific compilation tasks (such as compileKotlin or compileJava). Instead of recompiling all source files across a module, the compiler tracks source changes and re-processes only the modified files and their affected ABI consumers, drastically slashing iteration loops during local active development.
- Build Cache: Operates across the task execution phase. It maps immutable task inputs (source files, dependencies, compiler options, environment flags) to a cryptographic hash. If a task's hash matches an entry in the local or remote cache, Gradle skips task execution entirely and unpacks the pre-computed outputs directly into the build directory (FROM-CACHE). Remote Build Caching allows CI build results to be shared with local developer machines.
- Configuration Cache: Operates during Gradle's initial evaluation phase. It caches the resulting Directed Acyclic Graph (DAG) of tasks after evaluating settings.gradle.kts and build.gradle.kts files. On subsequent builds where build scripts remain untouched, Gradle bypasses project configuration entirely and proceeds straight to task execution, saving tens of seconds on multi-module codebases.

## Practical walkthrough (English)

Configuring build cache, configuration cache, and remote caching in Gradle:
```kotlin
// 1. gradle.properties: Enable modern caching optimizations
org.gradle.caching=true
org.gradle.configuration-cache=true
kotlin.incremental=true
org.gradle.parallel=true
org.gradle.jvmargs=-Xmx4g -XX:+UseParallelGC

// 2. settings.gradle.kts: Configure local and remote build caching
buildCache {
    local {
        isEnabled = true
        removeUnusedEntriesAfterDays = 7
    }
    remote<HttpBuildCache> {
        url = uri("https://cache.internal.company.com/cache/")
        isPush = System.getenv("CI") == "true" // Only CI pushes to remote cache
        credentials {
            username = System.getenv("CACHE_USER")
            password = System.getenv("CACHE_PASSWORD")
        }
    }
}
```

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

Incremental compilation recompiles only modified source files within a task. Build caching skips task execution entirely by reusing stored outputs matched by input hashes, shareable via remote CI caches. Configuration caching serializes the task graph, skipping build script evaluation when configuration has not changed to achieve instantaneous execution starts.

## Interview answer — structured

Optimizing Android build performance requires understanding how Gradle accelerates execution across distinct build phases.
First, incremental compilation operates within compiler tasks. The Kotlin compiler tracks changes and re-processes only edited classes and direct ABI dependents rather than recompiling entire modules.
Second, the build cache operates across task execution. By hashing task inputs including source code, dependencies, and build flags, Gradle matches pre-computed outputs from local disk or a shared remote cache, skipping execution completely with a FROM-CACHE status.
Third, the configuration cache optimizes Gradle's initial phase. Evaluating complex multi-module build scripts into a task graph consumes significant time; the configuration cache records this graph to disk, skipping build script evaluation entirely on subsequent runs whenever build configuration remains unchanged.

## Interview answer — deep senior

In large enterprise Android repositories spanning dozens or hundreds of Gradle modules, build times dictate developer velocity and engineering costs.
We treat build acceleration through a three-tier performance pyramid.
At the bottom tier sits incremental compilation.
Managed by the Kotlin Gradle Plugin, it observes source file modifications.
If an engineer modifies private implementation details inside a class without changing its public Abstract Binary Interface (ABI), kotlinc recompiles only that isolated file without invalidating downstream dependent modules.
In the middle tier sits Gradle's Build Cache.
While incremental compilation optimizes within a single task, build caching eliminates task execution altogether.
Gradle computes an SHA-256 fingerprint of all task inputs: source bytecodes, compiler flags, and classpath dependencies.
If an exact match exists, Gradle fetches the stored artifact, producing a FROM-CACHE outcome.
In our platform CI, we maintain a remote HTTP build cache: CI pipelines seed the cache with master branch artifacts, allowing developers pulling fresh branches to download pre-compiled DEX and class files instead of rebuilding locally.
At the top tier sits the Configuration Cache.
Evaluating hundreds of build.gradle.kts files to construct the task graph often consumes thirty to sixty seconds before any code compiles.
Configuration caching serializes the resolved task graph to disk; on subsequent invocations, Gradle bypasses script evaluation entirely, instantly beginning task execution.

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
