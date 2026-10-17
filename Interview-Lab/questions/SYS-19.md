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

## Concept and technical explanation

Scaling an enterprise Android application across twenty autonomous feature teams with a twenty-five-minute build time requires an aggressive restructuring of the dependency graph, build infrastructure, and architectural governance. In large organizations, build bottlenecks stem from monolithic module topologies, circular and deep linear dependency chains, excessive annotation processor passes (KAPT), non-cacheable Gradle tasks, and bloated root application packaging. Redesigning this architecture begins with empirical profiling using Gradle Build Scans to identify critical-path task execution times. Teams must adopt a modularized structure separating each feature into an api contract module, an impl private implementation module, and an independent sample harness app. Sample apps enable developers to compile and test their feature in isolation within seconds without building the entire application. In addition, migrating to Kotlin Symbol Processing (KSP), enabling remote build caching, and enforcing strict module boundaries via Gradle convention plugins restores rapid feedback loops.

## Practical walkthrough (English)

Structuring isolated feature modules and standalone sample apps for lightning-fast builds:
```text
// 1. Decoupled module hierarchy with isolated sample applications
├── build-logic/ (Convention plugins managing Gradle configurations centrally)
├── core/
│    ├── network/
│    └── database/
├── features/
│    ├── checkout/
│    │    ├── api/    (Exposes pure interfaces and models; compiles in 2 seconds)
│    │    ├── impl/   (Internal business logic, depends on checkout:api and core libraries)
│    │    └── sample/ (Standalone mini-app running Checkout flow in isolation in 8 seconds!)
│    ├── search/
│    │    ├── api/
│    │    ├── impl/
│    │    └── sample/
└── app/ (Final release composition wiring all 20 feature teams together)
```
```kotlin
// 2. Gradle convention plugin enforcing shared compiler and cache settings
class AndroidFeatureConventionPlugin : Plugin<Project> {
    override fun apply(target: Project) {
        with(target) {
            pluginManager.apply("com.android.library")
            pluginManager.apply("org.jetbrains.kotlin.android")
            pluginManager.apply("com.google.devtools.ksp") // Replace slow KAPT across all squads
            // Enforce unified JVM target, strict compilation flags, and build cacheability
        }
    }
}
```

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

We fix twenty-five-minute build bottlenecks by profiling Gradle tasks, migrating from KAPT to KSP, and restructuring code into decoupled api and impl modules. We provide standalone sample apps so squads build their features in seconds, while leveraging remote build caching and convention plugins for governance.

## Interview answer — structured

Resolving a twenty-five-minute build bottleneck across twenty squads requires restructuring both the dependency architecture and build pipelines.
I begin with data-driven profiling using Gradle Build Scans and Gradle Profiler to uncover task bottlenecks, non-cacheable steps, and critical compilation paths.
We reorganize the codebase into decoupled modules, splitting every feature into a lightweight api contract module and a private impl module.
Consuming squads depend strictly on api contracts, preventing downstream recompilation when private feature code changes.
We eliminate legacy KAPT annotation processing entirely, migrating to Kotlin Symbol Processing (KSP) to accelerate code generation by up to four hundred percent.
To give engineers immediate productivity, we author isolated sample testbed apps for every feature. Developers spend their day compiling only their feature sample app in under ten seconds rather than assembling the entire twenty-feature application.
Finally, we enable remote build caching in CI, allowing developers to pull precompiled module artifacts directly from cache.

## Interview answer — deep senior

From a staff developer productivity infrastructure perspective, scaling twenty teams requires treating build performance as a core product feature with dedicated SLOs and governance.
The most impactful technical shift is enabling remote build caching. When an engineer pulls the latest main branch, their local machine should not recompile nineteen untouched feature modules. By hosting a centralized remote build cache with strict input normalization, ninety percent of Gradle tasks resolve as FROM-CACHE, cutting incremental clean builds from twenty-five minutes down to under two minutes.
To prevent the dependency graph from regressing into an entangled monolith, we enforce strict dependency rules using Gradle convention plugins defined in build-logic. Feature modules are forbidden from depending on lateral feature implementation modules; they can only reference external api modules. We enforce these constraints automatically using Gradle dependency analysis plugins and ArchUnit tests in CI.
Furthermore, we optimize our continuous integration pipelines using predictive test selection and dynamic matrix builds. Rather than executing the entire sixty-minute test suite on every commit, CI inspects the git diff, determines affected modules through dependency graph traversal, and triggers tests only for the impacted subsystem and its immediate dependents.
Finally, code ownership is codified via CODEOWNERS files mapped to squad boundaries. Teams have autonomous merge rights within their impl modules, while modifications to core infrastructure and shared api contracts require formal architectural review, preventing uncontrolled dependency bloat.

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
