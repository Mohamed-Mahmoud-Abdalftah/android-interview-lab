---
id: "CIC-12"
question: "How do you reduce Gradle cold-build and CI execution times?"
topic: "CI/CD, Git & Team Delivery"
code: "CIC"
group: "B"
phase: 4
priority: "P2"
order: 431
editorial_status: "reviewed"
---

# CIC-12

## Original interview question

How do you reduce Gradle cold-build and CI execution times?

## What the interviewer evaluates

- Cold-build diagnosis versus configuration and execution improvements.
- Caching correctness and dependency graph.

## Explanation in Arabic

كيف تقوم بتقليل وقت التجميع الأولي البارد (Cold-Build) وتسريع تنفيذ خط أنابيب الـ CI في أندرويد؟

1. أسباب بطء بناء الـ CI (Bottlenecks):
   - سيرفرات الـ CI (مثل GitHub Actions runners) غالباً ما تكون بيئات عابرة (Ephemeral VMs) تبدأ من الصفر بدون أي كاش للمكتبات أو الـ Gradle Daemon.
   - إعادة تجميع كل الـ Modules والمكتبات مع كل PR تستهلك من 15 إلى 40 دقيقة.

2. استراتيجيات التسريع الجوهرية (Optimization Tactics):
   - **1. Remote Build Cache (كاش التجميع البعيد)**: أهم خطوة على الإطلاق! إعداد كاش سحابي (عبر Gradle Enterprise / Develocity أو سيرفر HTTP/S3) يسمح لسيرفرات الـ CI بمشاركة مخرجات المهام (Task Outputs). أي مهمة تم بناؤها مسبقاً بنفس المدخلات يتم تنزيل نتيجتها في أجزاء من الثانية (`FROM-CACHE`).
   - **2. استعادة كاش الـ Gradle والـ Dependencies**: استخدام `gradle/actions/setup-gradle` الذي يقوم بحفظ واستعادة مجلدات `~/.gradle/caches` ومجلد الـ wrapper تلقائياً.
   - **3. تفعيل خصائص Gradle المتقدمة**: تفعيل `org.gradle.parallel=true` لتجميع الوحدات المستقلة بالتوازي، وتفعيل `org.gradle.configuration-cache=true` لتخطي مرحلة التكوين (Configuration Phase).
   - **4. فحص الـ Modules المتأثرة فقط (Affected Module Detection)**: تشغيل الاختبارات والفحوصات فقط على الموديولات التي تغيرت في الـ Git Diff وما يعتمد عليها، بدلاً من فحص 100 موديول بالكامل.
   - **5. ضبط ذاكرة الـ JVM بدقة**: تخصيص ذاكرة كافية لـ Gradle في الـ CI (`-Xmx4g -XX:+UseParallelGC`) لتفادي توقف الـ Garbage Collector المتكرر.

## Practical walkthrough

إعداد ملف `gradle.properties` وتخصيص الـ CI لسرعة قياسية:
```properties
# gradle.properties مخصص لبيئة الـ CI:
org.gradle.jvmargs=-Xmx4096m -XX:+UseParallelGC -XX:MaxMetaspaceSize=1024m
org.gradle.parallel=true
org.gradle.caching=true
org.gradle.configuration-cache=true
kapt.incremental.apt=true
kotlin.incremental=false # Incremental compilation غير مجدية في الـ cold builds النظيفة بدون كاش محلي
```
وفي ملف `settings.gradle.kts` لتفعيل الـ Remote Build Cache:
```kotlin
buildCache {
    local {
        isEnabled = true
    }
    remote<HttpBuildCache> {
        url = uri("https://gradle-cache.company.internal/cache/")
        credentials {
            username = System.getenv("CACHE_USER")
            password = System.getenv("CACHE_PASSWORD")
        }
        isPush = System.getenv("IS_CI_MAIN_BRANCH") == "true" // سيرفر الـ main فقط يرفع للكاش
    }
}
```

## Why it matters and how it works

Gradle’s configuration cache reuses configuration state when plugins/tasks are compatible; build cache reuses task outputs when inputs are identical. Remote cache helps CI clean agents but must be trusted and correctly keyed. A module graph with unnecessary `api` edges increases recompilation.

## Worked example

A 12-minute cold CI build spends five minutes resolving artifacts and four in KAPT. Add dependency mirror/cache with verification, migrate a supported processor to KSP after measuring, then compare clean-build scans. Keep a no-cache control run to detect false wins.

## Trade-offs and decision criteria

Caches speed repeat builds but cold baseline may stay unchanged. Parallel workers can saturate memory and slow compilation. Modularization may improve selective builds but adds configuration overhead; measure total critical path.

## Failure modes

An invalid remote cache serves stale output or includes secret-bearing artifacts. Use Gradle’s input tracking and trusted cache permissions; never cache signing keystores. A “warm local” benchmark is not a cold CI result.

## Production perspective

Track cold and warm p50/p95, cache hit rate, configuration time and affected-module rebuilds. Roll changes back if correctness or memory use worsens.

## Interview answer — short

Slash Android CI build times by configuring Gradle Remote Build Cache (Develocity/HTTP cache) for task reuse, enabling Gradle configuration cache and parallel execution, caching Gradle dependencies via setup-gradle actions, using affected module detection to test only modified modules, and tuning JVM heap memory.

## Interview answer — structured

Accelerating cold and warm CI builds requires addressing Gradle's configuration and execution phases systematically.

First, **Remote Build Cache Infrastructure**. Next, ephemeral CI containers start without local cache. Enabling a remote HTTP build cache (e.g. Gradle Enterprise/Develocity or self-hosted HTTP cache) allows tasks that match input hashes to pull pre-compiled bytecode with `FROM-CACHE`, cutting build times by 50–70%.
**Gradle Execution Flags**. Enable `org.gradle.parallel=true` to process independent Gradle subprojects concurrently.
Enable `org.gradle.configuration-cache=true` to skip the configuration phase on subsequent invocations. Enable `org.gradle.caching=true`.
**Affected Module Detection**. In large multi-module repositories, use tools like Dropbox's `AffectedModuleDetector` or custom Git diff inspection. Run tests and static analysis exclusively on changed modules and their transitive downstream dependents rather than the entire project.
**JVM & Memory Tuning for CI Runners**. Finally, ephemeral runners typically suffer from memory thrashing. Configure `-Xmx4g` to `-Xmx6g` with `-XX:+UseParallelGC` to minimize garbage collection pauses during intensive compilation.


## Interview answer — deep senior

From an architectural systems engineering angle, cache hygiene and task avoidability drive performance.

First, with Task Cache Miss Hunting, if a single task includes absolute file paths or system timestamps in its `@Input`, Gradle invalidates the task's cache key on every runner, turning `FROM-CACHE` into expensive recompilations. Teams run Gradle Build Scans regularly to audit task inputs and enforce path sensitivity (`PathSensitivity.RELATIVE`). Next, with Push vs. Pull Cache Access Control, never allow every unverified PR to push to the remote build cache; a corrupted or poisoned cache entry on a feature branch can infect other builds. The main branch CI should be the only agent configured with `isPush = true` permissions, while PR builds have read-only (`isPush = false`) pull access.
Finally, with KSP vs. KAPT Migration, kAPT relies on Java stub generation which severely hampers build parallelization and cache performance. Migrating annotation processors to Kotlin Symbol Processing (KSP) delivers up to 2x faster compilation speed and native incremental processing.


## How to answer in the interview

- **Why:** slow feedback delays integration.
- **How:** profile queue, Gradle tasks, caches and devices.
- **Trade-off:** speed versus reliable risk coverage.
- **Failure case:** bad cache inputs reuse stale output.
- **Production solution:** measure before/after and retain critical gates.

## Deep-dive talking points

Prompt for cold/warm distinction, configuration versus task cache, processor cost, critical path.

## Follow-up questions

- **Interviewer:** "Why should feature PR builds have read-only access to the remote Gradle build cache?"
  **Answer:** "To prevent cache poisoning, ensuring that only trusted, validated builds from the main branch populate cache entries."

- **Interviewer:** "How does KSP improve build performance over KAPT in CI?"
  **Answer:** "KSP interacts directly with the Kotlin compiler AST without generating expensive intermediate Java stub files, reducing compilation time by up to 50%."

## Self-check rubric

Measure configuration, dependency resolution, compilation, tests and cache misses separately; pick the largest verified bottleneck and compare clean versus warm builds before changing the pipeline.

## References and reviewed-on date

- [Gradle performance guide](https://docs.gradle.org/current/userguide/performance.html) — profiling and optimization.
- [Gradle configuration cache](https://docs.gradle.org/current/userguide/configuration_cache.html) — compatibility and reuse.

Technically reviewed against primary documentation on 2026-10-13.
