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

كيف تحقق في تعارض إصدارات التبعيات (Dependency Version Conflicts) وانحدار سرعة البناء (Build-Speed Regressions)؟

1. التحقيق في تعارض التبعيات (Dependency Conflicts):
   - **كيف يحل Gradle التعارض افتراضياً؟**: إذا طلبت مكتبة A إصدار `okhttp:4.9.0` وطلبت مكتبة B إصدار `okhttp:4.12.0`، يقوم Gradle باختيار **أحدث إصدار تلقائياً (Latest Version Wins)**. هذا قد يسبب مشاكل توافق إذا كان الإصدار الأحدث يحتوي على Breaking Changes!
   - **أدوات التشخيص الرسمية**:
     * `./gradlew :app:dependencies`: يطبع شجرة التبعيات بالكامل مع توضيح الترقيات التلقائية (`-> 4.12.0`).
     * `./gradlew :app:dependencyInsight --dependency okhttp --configuration releaseRuntimeClasspath`: يشرح بالضبط أي مكتبات طلبت OkHttp ولماذا اختار Gradle هذا الإصدار تحديداً.
   - **الحل الهندسي**: تثبيت الإصدارات عبر **Gradle Version Catalogs (`libs.versions.toml`)** أو استخدام `strictly` / `force` في `resolutionStrategy`.

2. التحقيق في انحدار سرعة البناء (Build-Speed Regressions):
   - **Gradle Build Scan (`./gradlew assembleDebug --scan`)**: الأداة الأقوى عالمياً؛ تحلل زمن كل Task، والـ Cache Misses، وزمن الـ Annotation Processing، والـ Garbage Collection pauses.
   - فحص الـ Non-Cacheable Tasks ومقارنة الـ Build Scans الحالية بسجلات سابقة لاكتشاف الـ Commit المتسبب في التراجع.

## Practical walkthrough

أوامر تشخيص التبعيات وفرض الإصدارات الصريحة في build.gradle.kts:
```bash
# 1. معرفة سبب اختيار إصدار معين والمسار الدقيق في شجرة التبعيات:
./gradlew :app:dependencyInsight --dependency okhttp --configuration releaseRuntimeClasspath

# 2. إنشاء تقرير Build Scan كامل لتحليل أسباب بطء البناء:
./gradlew :app:assembleRelease --scan
```

```kotlin
// 3. فرض إصدار معين وحظر الترقية التلقائية في build.gradle.kts:
configurations.all {
    resolutionStrategy {
        // إجبار المشروع بالكامل ومكتباته على استخدام إصدار موحد ومفحوص:
        force("com.squareup.okhttp3:okhttp:4.12.0")
        
        // أو إفشال الـ Build فوراً عند حدوث أي تعارض لإجبار المطورين على حله:
        failOnVersionConflict()
    }
}
```

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

Investigate dependency conflicts using Gradle's dependencyInsight task to trace conflict graphs, enforcing unified versions via Version Catalogs or resolutionStrategy.force(). Investigate build speed regressions using Gradle Build Scans (--scan) to identify slow tasks, cache misses, and annotation processing bottlenecks.

## Interview answer — structured

Diagnosing dependency friction and build performance regressions requires targeted Gradle diagnostic tooling:

1. **Dependency Conflict Investigation**:
   - By default, Gradle's conflict resolution selects the highest requested version (`latest version wins`). This can introduce silent binary incompatibilities if a transitive upgrade introduces breaking API changes.
   - Run `./gradlew :app:dependencyInsight --dependency <name> --configuration <classpath>`. Gradle prints the exact dependency graph path and selection rationale explaining why a specific version was resolved.
   - Enforce consistency across the codebase using Gradle Version Catalogs (`libs.versions.toml`) and `resolutionStrategy.force()`, or enable `failOnVersionConflict()` in CI to catch divergent transitive dependencies early.

2. **Build-Speed Regression Profiling**:
   - Generate a **Gradle Build Scan** using `./gradlew assembleDebug --scan`.
   - Inspect the Timeline view to identify non-parallel task bottlenecks, measure KAPT/KSP annotation processing durations, identify tasks failing incremental execution, and pinpoint cache misses across remote and local build caches.

## Interview answer — deep senior

From a staff platform architecture viewpoint, maintaining dependency and build velocity requires continuous guardrails:

1. **Rich Version Constraints (Strict vs. Require)**: Modern Gradle supports rich versioning. Specifying `strictly("1.5.0")` prevents any transitive dependency from bumping the version, causing a build failure if incompatible constraints are encountered.

2. **Task Cache Miss Forensics**: When a task fails to pull from the build cache, inspect Gradle's cache key inputs with `--info` or Build Scans. The most frequent culprit is non-hermetic tasks with volatile inputs, such as un-annotated directory inputs or hardcoded machine-specific absolute file paths in compiler arguments.

3. **Dependency Analysis Plugins**: Integrate AutonomousApps' `dependency-analysis-android-plugin` in CI. It automatically identifies unused direct dependencies, transitively used dependencies that should be declared directly, and dependencies leaking across `api` rather than `implementation` boundaries.

## How to answer in the interview

- **Why:** transitive changes affect behavior and speed.
- **How:** inspect graph and task profile.
- **Trade-off:** upgrade freshness versus compatibility.
- **Failure case:** forced version fixes compile but breaks runtime.
- **Production solution:** pin tested set and verify release.

## Deep-dive talking points

Discuss per-variant resolution, dependencyInsight, BOM/constraints, runtime linkage, build scan and critical path.

## Follow-up questions

- **Interviewer:** "What is the difference between implementation and api scope regarding dependency resolution?"
  **Answer:** "implementation hides the dependency from downstream consumers, preventing compilation leakage and rebuild cascading; api exposes the dependency transitively to all consumers."

- **Interviewer:** "What does failOnVersionConflict() do?"
  **Answer:** "It instructs Gradle to abort the build immediately whenever two dependencies request different versions of the same library, requiring explicit resolution."

## Self-check rubric

Trace a selected version, justify a fix, and profile one build regression with controlled evidence.

## References and reviewed-on date

- [Gradle dependency reports](https://docs.gradle.org/current/userguide/viewing_debugging_dependencies.html) — selection reasons.
- [Gradle build performance](https://docs.gradle.org/current/userguide/performance.html) — profiling and optimization.

Technically reviewed against primary documentation on 2026-10-13.
