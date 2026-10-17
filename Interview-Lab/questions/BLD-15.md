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

## Concept and technical explanation

Diagnosing dependency conflicts and build performance regressions requires targeted profiling across Gradle's build lifecycle phases:
- Dependency Conflict Resolution Mechanics:
  1. Conflict Strategy: Gradle defaults to 'latest version wins'. If transitive dependencies pull disparate library revisions (e.g. OkHttp 4.9.0 vs 4.12.0), Gradle automatically upgrades to the highest version. This can introduce silent binary breaking changes or runtime NoSuchMethodError.
  2. Diagnostic Tooling:
     - ./gradlew :app:dependencies --configuration releaseRuntimeClasspath: Prints the comprehensive tree with upgrade notations (-> 4.12.0).
     - ./gradlew :app:dependencyInsight --dependency okhttp --configuration releaseRuntimeClasspath: Dissects exact incoming graph paths and explains selection reasons.
  3. Resolution Governance: Enforce consistency via Gradle Version Catalogs (libs.versions.toml) and strict rich constraints (strictly). Avoid blind resolutionStrategy.force() which silences compiler warnings but masks binary breakage.
- Build-Speed Regression Profiling:
  1. Lifecycle Phase Separation: Profile configuration phase (isolated via Gradle Configuration Cache), task execution phase, and compiler/annotation processing overhead.
  2. Gradle Build Scans: Execute ./gradlew assembleDebug --scan to generate deep diagnostics analyzing the critical path, task cache misses, non-incremental task inputs, and Garbage Collection pauses.
  3. Gradle Profiler: Use gradle-profiler for controlled statistical benchmarking across commits.

## Practical walkthrough (English)

Diagnostic CLI commands and conflict resolution configuration in build.gradle.kts:
```bash
# 1. Trace why a specific dependency version was selected and which modules requested it:
./gradlew :app:dependencyInsight --dependency okhttp --configuration releaseRuntimeClasspath

# 2. Profile build performance and cache misses with a Gradle Build Scan:
./gradlew :app:assembleRelease --scan
```

```kotlin
// 3. Enforce strict versioning and conflict detection in build.gradle.kts:
configurations.all {
    resolutionStrategy {
        // Fail the build immediately whenever two dependencies request divergent versions
        failOnVersionConflict()

        // Force a verified, audited library version across all transitive dependencies
        force("com.squareup.okhttp3:okhttp:4.12.0")
    }
}
```

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

Investigating dependency conflicts requires running Gradle dependencyInsight to inspect selection rationale and path origins across configurations, resolving discrepancies through Version Catalogs or strict constraints. For build speed regressions, we generate Gradle Build Scans to isolate configuration bottlenecks, identify cache-miss triggers in non-incremental tasks, and measure annotation processing overhead on the critical path.

## Interview answer — structured

When diagnosing dependency friction and compilation slowdowns, senior engineers follow a structured diagnostic pipeline.
To investigate dependency conflicts, we avoid blind version forcing. Running Gradle dependencyInsight for the affected runtime classpath prints the exact dependency graph path and selection rationale. Gradle defaults to selecting the highest version, which frequently introduces silent binary incompatibilities if a transitive upgrade introduces breaking API changes. We resolve these conflicts systematically using Gradle Version Catalogs and rich version constraints, or enable failOnVersionConflict in continuous integration to catch divergent transitive dependencies early.
To investigate build speed regressions, we never rely on subjective local observations. We generate a Gradle Build Scan to separate configuration overhead from task execution. The build timeline highlights tasks on the critical execution path, distinguishes incremental executions from full rebuilds, and pinpoints cache misses caused by non-hermetic task inputs. Furthermore, we audit annotation processing durations between KAPT and KSP, ensuring code generators run incrementally without invalidating downstream compilation caches.

## Interview answer — deep senior

From a platform engineering leadership perspective, maintaining dependency hygiene and compilation velocity requires continuous architectural guardrails rather than reactive troubleshooting.
When handling transitive dependency conflicts, using resolutionStrategy.force is a dangerous anti-pattern because it overrides the graph indiscriminately, masking underlying binary incompatibilities until runtime NoSuchMethodError crashes occur in production. Instead, we implement Gradle rich version constraints. Using strictly prevents any transitive dependency from upgrading a library beyond an audited release. Additionally, we integrate dependency analysis plugins in our pipeline to detect unused direct dependencies and transitive dependencies that leak across compilation boundaries.
When tackling build speed regressions, the most frequent culprits fall into three categories: configuration bloat, cache invalidation, and annotation processing. If developers execute arbitrary file operations, network calls, or dynamic Git queries during the configuration phase, every build incurs a heavy penalty regardless of task caching. We eliminate this by enabling the Gradle Configuration Cache and validating that all plugins conform to isolated configuration inputs.
For task execution regressions, a single task with unstable inputs breaks caching for all downstream dependents. Unstable inputs typically arise from un-annotated directory parameters, volatile timestamps in generated source headers, or absolute machine-specific file paths passed into compiler flags. By inspecting Build Scan task inputs and diffing cache keys between local and continuous integration environments, we isolate the exact input property invalidating the cache. Finally, migrating legacy KAPT processors to Kotlin Symbol Processing reduces annotation overhead significantly by generating code directly from Kotlin compiler AST without generating Java stubs.

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
