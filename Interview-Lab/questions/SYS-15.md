---
id: "SYS-15"
question: "Compare monolith and multi-module designs."
topic: "Android System Design & Architecture Decisions"
code: "SYS"
group: "B"
phase: 4
priority: "P1"
order: 344
editorial_status: "reviewed"
---

# SYS-15

## Original interview question

Compare monolith and multi-module designs.

## What the interviewer evaluates

Compare monolith and multi-module by team scale, build isolation and API cost.

## Concept and technical explanation

The architectural choice between a monolithic single-module structure and a multi-module architecture is one of the most critical decisions impacting development velocity, build scalability, and team autonomy in Android. A monolithic architecture, where all source code resides within a single :app module, offers simplicity, minimal Gradle configuration overhead, effortless cross-feature refactoring, and zero inter-module dependency plumbing. However, as an organization scales beyond a handful of engineers, monoliths suffer severe build bottlenecks due to single-threaded compilation phases, frequent merge conflicts, and blurred architectural boundaries. Conversely, a multi-module architecture partitions the application into decoupled Gradle modules grouped by layer or feature. Modularization enables massive build speedups via parallel compilation and Gradle remote build caching, enforces strict team code ownership, and unlocks advanced deployment options like dynamic feature modules. The decision to modularize requires evaluating organizational scale, build hardware budgets, and CI governance maturity against the added maintenance cost of Gradle build scripts.

## Practical walkthrough (English)

Contrasting Monolith versus Multi-Module dependency graph topologies:
```text
// 1. Monolithic Single-Module Structure (:app contains everything)
// Pros: Single build.gradle.kts, trivial refactoring, no wiring boilerplate.
// Cons: Linear build times, tight coupling, merge conflict hot-spots.
:app
 ├── auth/ (activities, viewmodels, network, room entities)
 ├── feed/ (activities, viewmodels, network, room entities)
 └── core/ (database, network, shared utilities)

// 2. Multi-Module Architecture by Feature and Layer
// Pros: Parallel compilation, remote build caching, dynamic feature delivery.
// Cons: Complex Gradle management, dependency substitution overhead.
:app (Application composition, navigation graph assembly, Dagger root)
 ├── :feature:auth:api
 ├── :feature:auth:impl (depends on :feature:auth:api, :core:network, :core:database)
 ├── :feature:feed:api
 ├── :feature:feed:impl (depends on :feature:feed:api, :core:network, :core:ui)
 ├── :core:designsystem (Compose themes, atomic UI components)
 ├── :core:network (OkHttp, Retrofit, authentication interceptors)
 └── :core:database (Room database, base DAO abstractions)
```

## Explanation in Arabic

قارن بين التصميم أحادي الكتلة (Monolith) والتصميم متعدد الموديولات (Multi-Module)، ومتى تختار كلاً منهما؟

1. العمارة الأحادية (Monolithic Architecture - Single `:app` Module):
   - **المزايا**: سرعة فائقة في بداية المشروع (MVP)، سهولة إعادة الهيكلة (Refactoring)، بساطة إعداد Dagger/Hilt، وبساطة التنقل (Navigation).
   - **العيوب عند التوسع**: بطء هائل في زمن التجميع (Clean build قد يتجاوز 25 دقيقة)، تداخل التبعيات والـ Spaghetti Code، نزاعات دمج مستمرة (Merge Conflicts)، واستحالة عزل الميزات لاختبارها المستقل.

2. العمارة متعددة الموديولات (Multi-Module Architecture):
   - **المزايا**: تجميع تزايدي سريع (Incremental Compilation)، استغلال Gradle Build Cache و Parallel Execution، وضوح ملكية الكود بين الفرق (Code Ownership)، وتطبيق مبدأ العزل الصارم (Encapsulation).
   - **العيوب**: تعقيد أولي في إعداد Gradle scripts، إدارة التبعيات المشتركة، صعوبة الـ Navigation غير المباشر، وتكلفة هندسية في بداية المشروع.

3. معايير الاختيار الواقعية (Decision Criteria):
   - **تطبيق صغير (1-3 مطورين، ميزات محدودة)**: الـ Monolith المنظم جيداً بالحزم (Package-by-Feature) هو الخيار الأذكى والأسرع.
   - **تطبيق متوسط/كبير (أكثر من 5 مطورين، ميزات متعددة)**: الانتقال التدريجي إلى موديولات Core و Feature لتسريع التجميع وعزل المسؤوليات.

## Practical walkthrough

المقارنة الهيكلية بين Monolith مقسم بحزم و Modular Architecture مقسم بـ Gradle Modules:
```text
// 1. هيكل Monolith (ملائم للفرق الصغيرة والمشاريع الناشئة):
:app
 ├── feature_auth/
 ├── feature_feed/
 ├── core_network/
 └── core_database/

// 2. هيكل Multi-Module احترافي (ملائم للفرق الكبيرة والتطبيقات الضخمة):
├── :app (تجميع الـ DI والـ Navigation العام فقط)
├── :feature:auth:api / :feature:auth:impl
├── :feature:feed:api / :feature:feed:impl
├── :core:designsystem (مكونات الواجهة المشتركة)
├── :core:network (OkHttp / Retrofit)
└── :core:database (Room Database)
```

## Why it matters and how it works

Modules are compilation/dependency boundaries, not automatically clean architecture. A poorly split project with giant shared API can be slower than a monolith. Measure clean/incremental build, affected module count, test isolation, merge conflicts and ownership before/after. Start with a few high-cohesion boundaries.

## Worked example

Conceptual graph; no code change is justified until coupling and build hotspot are measured.

```kotlin
// Monolith: :app contains catalog, checkout, account.
// Targeted split:
// :app -> :feature:catalog, :feature:checkout
// :feature:* -> :core:ui, narrow domain APIs
// Avoid :feature:catalog -> :feature:checkout implementation.
```

## Trade-offs and decision criteria

Monolith maximizes local simplicity for small teams; modularity adds up-front API/DI maintenance but can scale ownership. Dynamic delivery is a separate runtime packaging decision. Avoid splitting by every class or every layer when it creates boilerplate without isolation.

## Failure modes

A module cycle or all-features-depend-on-common graph prevents independent builds. Public API churn across 20 modules can increase recompilation. Teams may duplicate business logic if ownership is unclear.

## Production perspective

A startup with three engineers keeps one app module plus small data boundaries. At 20 teams, it extracts team-owned features and stable shared APIs incrementally, then tracks incremental build time and cross-team PR dependency.

## Interview answer — short

A monolith offers simplicity and fast initial velocity for small teams, but causes slow builds and coupling at scale. Multi-module architectures provide parallel compilation, remote build caching, strict team ownership, and dynamic feature delivery, but introduce Gradle complexity and wiring overhead.

## Interview answer — structured

Choosing between a monolith and a multi-module architecture requires balancing organizational scale against build infrastructure complexity.
A monolithic architecture where all code lives in a single app module is ideal for early-stage startups and small teams. It eliminates Gradle configuration overhead, makes refactoring effortless, and avoids dependency wiring boilerplate.
However, as team size exceeds ten engineers, the monolith encounters severe friction: compilation times become agonizingly slow, merge conflicts on shared files multiply, and code boundaries blur into an entangled dependency mess.
A multi-module architecture partitions code into decoupled feature and core modules. This enables Gradle to compile independent modules concurrently across CPU cores and leverage remote build caches to skip building unchanged modules entirely.
Modularization also enforces clear architectural boundaries and team ownership, while enabling dynamic feature delivery.
The trade-off is higher operational overhead, requiring dedicated build tooling governance and disciplined dependency management.

## Interview answer — deep senior

From a staff engineering perspective, the decision to modularize must be driven by data metrics such as developer build wait times and team autonomy rather than architectural dogma.
The most significant tangible benefit of modularization is build pipeline acceleration. In a monolith, changing a single line of code forces Gradle to recompile the entire module and re-run dexing and packaging tasks. In a properly structured multi-module codebase with clean ABI boundaries, modifying an internal implementation class triggers recompilation only for that specific module, allowing all downstream modules to resolve from the local or remote build cache.
However, naive modularization can actually degrade build performance. If an application is split into dozens of fine-grained modules connected in a deep linear chain, Gradle cannot parallelize tasks, and the overhead of configuring dozens of Gradle projects outweighs any compilation savings. Successful modularization requires a wide, shallow dependency graph where independent feature modules depend on shared core libraries without lateral cross-feature coupling.
Furthermore, modularization unlocks modular delivery capabilities on Google Play. Heavy, infrequently used features like identity verification or onboarding flows can be isolated into Dynamic Feature Modules, reducing the initial download APK size for new users and downloading components on-demand.
In conclusion, start with a pragmatic modularized structure or a disciplined package-by-feature monolith, transitioning to full multi-module architectures when team size, build times, or independent release requirements justify the governance cost.

## How to answer in the interview

- **Why:** module choice affects build speed and team coupling.
- **How:** measure dependency fan-out and split stable feature boundaries.
- **Trade-off:** more modules add wiring and maintenance overhead.
- **Failure case:** giant core and broad api edges still rebuild everything.
- **Production solution:** profile builds, enforce graph rules, and evolve incrementally.

## Deep-dive talking points

Defend one incremental split using measured build and ownership evidence.

## Follow-up questions

- **Interviewer:** "What is Gradle Configuration Cache?"
  **Answer:** "A Gradle feature that caches the output of the configuration phase and reuses it for subsequent builds, significantly speeding up multi-module build execution."

- **Interviewer:** "How do you handle dependency injection across feature modules?"
  **Answer:** "Feature modules expose interface dependencies via Dagger components or Hilt entry points; the root :app module compiles all implementations and injects them into the unified graph."

## Self-check rubric

Can I articulate both costs, draw acyclic target and specify metrics?

## References and reviewed-on date

- [Android modularization guide](https://developer.android.com/topic/modularization) — benefits and costs.
- [Android architecture guide](https://developer.android.com/topic/architecture) — separation of concerns.

Technically reviewed against primary documentation on 2026-10-13.
