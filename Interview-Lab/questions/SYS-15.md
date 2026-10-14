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

Monoliths offer rapid initial prototyping and simple refactoring, but degrade into 20+ minute build times and team coupling at scale. Multi-module architectures provide parallel build caching, strict encapsulation, and team autonomy at the cost of Gradle configuration complexity. Choose monolith for MVPs and modularize as teams exceed 4–6 engineers.

## Interview answer — structured

Choosing between monolithic and multi-module architectures is an engineering trade-off governed by team size, build performance, and domain complexity.

First, **Monolithic Architecture (`:app`)**. Next, with Strengths, zero module configuration overhead, trivial dependency injection setups, effortless cross-cutting refactoring, and rapid early iteration velocity.
Additionally, with Failure Modes at Scale, long clean build times (20–40 minutes), frequent Git merge conflicts on shared manifests and navigation files, lack of enforcement boundaries leading to tight coupling between domains. **Multi-Module Architecture**.
Strengths enables Gradle parallel execution, distributed build caching, and incremental compilation where modifying one feature only recompiles its isolated module. Provides strict encapsulation via Kotlin's `internal` modifier and defines clear team ownership. With Costs, increased Gradle maintenance, dependency version alignment overhead, and indirection in cross-feature navigation and dependency injection graphs.
**Pragmatic Decision Threshold**. With 1–4 Engineers, maintain a modular-ready monolith organized cleanly by package-by-feature.
Finally, with 5+ Engineers / Multi-Feature Products, modularize into `:core` and `:feature` boundaries to protect build velocity and establish autonomous team ownership.


## Interview answer — deep senior

From a staff platform architecture viewpoint, premature modularization can be just as damaging as an overgrown monolith.

First, with The Cost of Granular Over-Modularization, splitting every screen into its own Gradle module creates dozens of small modules. Each module incurs Gradle configuration-time evaluation overhead. In large projects, configuring 150+ tiny modules can add 30 seconds to every build before compilation even begins. Modularize around bounded domain contexts, not individual UI screens. Next, with Convention Plugins (build-logic), manage multi-module build scripts cleanly by creating custom Gradle Convention Plugins in `build-logic`. Define shared conventions (`android-feature`, `android-library`, `android-compose`) in composite builds rather than duplicating Groovy/Kotlin script blocks across dozens of `build.gradle.kts` files.
Finally, a Micro-Apps (Sample Apps) for Velocity is the true superpower of modularization is sample app generation. An engineer working on `:feature:search:impl` runs a dedicated `:feature:search:sample` app, booting the local feature in an emulator in 4 seconds without compiling the rest of the application.


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
