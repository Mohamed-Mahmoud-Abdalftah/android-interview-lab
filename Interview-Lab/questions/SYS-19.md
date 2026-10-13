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

تطبيق يعمل عليه 20 فريقاً برمجياً ويستغرق وقت البناء (Build Time) حوالي 25 دقيقة. كيف تعيد تصميم ملكية الكود والتبعيات لتسريع التطوير؟

1. تشخيص أسباب بطء البناء (Root Cause Analysis via Build Scans):
   - **تشغيل Gradle Build Scan (`--scan`)**: لتحديد المراحل والـ Tasks الأكثر استهلاكاً للوقت.
   - **المشاكل المعتادة**: موديول أحادي ضخم (`:app`)، تبعيات دائرية، تعطيل الـ Configuration Cache، كثرة كود الـ Annotation Processing (KAPT بدلاً من KSP)، وغياب الـ Remote Build Cache.

2. إعادة الهيكلة المعمارية (Modular Redesign & Dependency Decoupling):
   - **تفكيك الميزات إلى API و Implementation**:
     * `:feature:profile:api` (خفيف، كود عام فقط).
     * `:feature:profile:impl` (التنفيذ الفعلي، لا يعتمد عليه أحد).
   - **كسر التبعيات المباشرة بين الميزات**: منع أي موديول Feature من الاعتماد على موديول Feature آخر، وتمرير الاتصال عبر الـ DI والـ Core modules.
   - **إنشاء Sample Apps مستقلة لكل فريق**:
     * فريق الـ Profile يعمل داخل موديول تطبيقي صغير `:feature:profile:sample`. هذا التطبيق يُبنى ويشتغل في 10 ثوانٍ فقط، مما ينقذ إنتاجية الفريق اليومية!

3. تحسينات أدوات البناء والبنية التحتية (Build Infrastructure Optimization):
   - الانتقال من KAPT إلى **KSP (Kotlin Symbol Processing)** لتسريع معالجة الـ Annotations بنسبة 2x.
   - تفعيل **Gradle Configuration Cache** و **Build Cache** المشترك على شبكة الـ CI (Remote Build Cache).
   - تحديد ملف `CODEOWNERS` لفرض ملكية واضحة للموديولات ومنع التعديلات العشوائية.

## Practical walkthrough

هيكلة إعدادات Gradle باستخدام Convention Plugins و Sample Apps لتقليص زمن البناء:
```text
// هيكل الموديولات المصغر لفرق العمل المستقلة:
├── build-logic/ (Convention plugins لإدارة إعدادات Gradle مركزياً)
├── core/ (Modules منخفضة المستوى)
│    ├── network/
│    └── database/
├── features/
│    ├── checkout/
│    │    ├── api/    (العقود العامة فقط: تترجم في ثوانٍ)
│    │    ├── impl/   (التنفيذ الداخلي الخاص بالفريق)
│    │    └── sample/ (تطبيق مستقل مصغر لبناء واختبار الـ Checkout فقط في 8 ثوانٍ!)
└── app/ (التطبيق النهائي المجمع للإنتاج)
```

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

Redesign build performance by decoupling features into isolated :api and :impl modules, providing dedicated lightweight sample apps for each team, migrating from KAPT to KSP, enabling Gradle configuration and remote build caching, and enforcing architectural boundaries via automated linters and CODEOWNERS.

## Interview answer — structured

Addressing a 25-minute build across 20 feature teams requires both architectural modularization and build toolchain optimization:

1. **Architecture & Dependency Decoupling**:
   - Decouple feature interdependencies using the **API/Implementation pattern** (`:feature:x:api` and `:feature:x:impl`). Modifying implementation code in one feature will not invalidate the build cache of dependent features.
   - Eliminate the monolithic `:app` bottleneck. Provide each team with a dedicated, lightweight `:feature:x:sample` runner module. Feature engineers build and iterate within their sample app in under 10 seconds without compiling the remaining 19 domains.

2. **Toolchain Modernization**:
   - Replace legacy KAPT annotation processors with **KSP (Kotlin Symbol Processing)** for Room, Moshi, and Dagger/Hilt, reducing annotation processing overhead by 50%.
   - Enable Gradle's **Configuration Cache** (`org.gradle.configuration-cache=true`) to bypass project configuration evaluation on incremental builds.

3. **Distributed Remote Build Caching**:
   - Deploy a remote Gradle Build Cache server on the corporate network and CI. Outputs compiled on CI or colleagues' machines are pulled as precompiled binaries rather than re-executed locally.

4. **Organizational Governance**:
   - Enforce directory-level ownership using GitHub `CODEOWNERS`, and integrate Konsist or ArchUnit tests into CI to block PRs that introduce forbidden cross-feature dependencies.

## Interview answer — deep senior

From a staff platform engineering perspective, managing developer velocity at this scale requires continuous telemetry:

1. **Build Velocity Telemetry**: Instrument local developer and CI builds with Gradle Enterprise / Develocity. Monitor metrics across p50, p90, and p99 build times, task cache miss rates, and garbage collection pauses to identify pathological dependencies before they cascade.

2. **Binary Dependency Substitution (Focus Mode)**: For engineers working on specific verticals, implement an internal Gradle plugin that substitutes source module dependencies (`project(":core:network")`) with pre-compiled AAR binaries published to an internal Artifactory cache on every main-branch merge. Engineers compile only their 2 active modules from source.

3. **Non-Transitive R Classes**: Enable `android.nonTransitiveRClass=true` in `gradle.properties`. This ensures that each module's `R` class contains only its own resources rather than aggregating resource IDs from all upstream dependencies, preventing cascading recompilations when a string resource changes.

## How to answer in the interview

- **Why:** build time is a symptom of dependency and task behavior.
- **How:** profile representative edits, map fan-out, and assign module owners.
- **Trade-off:** fine modules may worsen configuration overhead.
- **Failure case:** splitting files without changing dependency edges.
- **Production solution:** build dashboards, graph rules, and incremental rollout with measured results.

## Deep-dive talking points

Analyze one build scan, one graph hotspot and a before/after measurement plan.

## Follow-up questions

- **Interviewer:** "What is the benefit of android.nonTransitiveRClass=true?"
  **Answer:** "It prevents Gradle from copying upstream resource IDs into downstream R classes, drastically reducing recompilations when resources change."

- **Interviewer:** "How does KSP achieve 2x faster performance than KAPT?"
  **Answer:** "KSP operates directly on Kotlin AST symbols without generating intermediate Java stubs, eliminating costly stub generation and javac execution."

## Self-check rubric

Can I profile first, shrink fan-out, measure real gains and keep release coverage?

## References and reviewed-on date

- [Android modularization guide](https://developer.android.com/topic/modularization) — module graph.
- [Gradle performance](https://docs.gradle.org/current/userguide/performance.html) — profiling/caches.

Technically reviewed against primary documentation on 2026-10-13.
