---
id: "MOD-20"
question: "How do you migrate a monolith to modules without blocking feature delivery?"
topic: "Gradle Modularization & Dependency Boundaries"
code: "MOD"
group: "C"
phase: 4
priority: "P1"
order: 373
editorial_status: "reviewed"
---

# MOD-20

## Original interview question

How do you migrate a monolith to modules without blocking feature delivery?

## What the interviewer evaluates

- Offer an incremental vertical-slice migration and measurable gates.
- Keep app behavior and tests stable during dual wiring.
- Handle dependency cycles, DI/navigation and rollback.

## Concept and technical explanation

Migrating an enterprise Android monolith to a multi-module architecture while shipping daily product features requires applying the Strangler Fig Pattern to incrementally dismantle the monolith without big-bang rewrites:
- Step 1: Foundational Bottom-Up Extraction: Extract stable, domain-agnostic leaf modules first (:core:designsystem, :core:network, :core:database). Because these have zero business logic dependencies, they stabilize quickly and establish convention plugins and version catalogs.
- Step 2: Vertical Leaf Feature Extraction: Identify self-contained, low-risk user journeys with minimal inward dependencies (e.g., Settings, About, Onboarding). Extract each into an independent :feature:<name> module using the API/Impl pattern, wiring navigation back to the monolith app module via contract interfaces.
- Step 3: Domain & Repository Decoupling: Extract core data and domain logic into independent modules, leaving backwards-compatible interface adapters in the legacy monolith so legacy screens continue functioning while new features build on modular foundations.
- Step 4: Governance & Enforcement: Introduce CI linters (Konsist) to forbid new code in the legacy monolith, shrinking it until :app becomes a pure composition root.

## Practical walkthrough (English)

Incremental migration using the Strangler Fig pattern and modular adapter bridges:
```text
Phase 1: Foundational Leaf Extraction
[Legacy Monolith :app] ──imports──> [:core:designsystem] & [:core:network]

Phase 2: Vertical Feature Extraction via API Contracts
[Legacy Monolith :app] ──wires──> [:feature:settings:impl] (Implements SettingsApi)
                      └──imports─> [:feature:settings:api]

Phase 3: The Monolith Becomes Pure Composition Root
[Root :app] (Pure DI & Navigation wiring)
  ├── imports :feature:onboarding:impl
  ├── imports :feature:checkout:impl
  └── imports :feature:settings:impl
```

## Explanation in Arabic

كيف تهاجر تطبيقاً متجانساً ضخماً (Monolith) إلى هيكل نمطي (Modularized Architecture) دون تعطيل تسليم الميزات الجديدة للفريق؟

1. الاستراتيجية المعمارية الأساسية: نمط شجرة التين الخانقة (Strangler Fig Pattern):
   - لا تقم أبداً بإيقاف تطوير الميزات لمدة 3 أشهر لإعادة كتابة التطبيق (وصفة للفشل المؤكد).
   - تتم الهجرة بشكل تزايدي وتدريجي شريحة بشريحة (Vertical Slices)، مع بقاء التطبيق القديم والجديد يعملان معاً في كل Release.

2. مراحل خطة الهجرة خطوة بخطوة:
   - **المرحلة 1: بناء الأساسات (Foundations & Build Infrastructure)**: إعداد Version Catalog و Convention Plugins في مجلد `build-logic` لتوحيد إعدادات Gradle.
   - **المرحلة 2: استخراج موديولات الـ Core من القاع (Bottom-Up Infrastructure Extraction)**:
     * استخراج `:core:designsystem` (الألوان والخطوط والمكونات العامة).
     * استخراج `:core:network` و `:core:database`.
   - **المرحلة 3: استخراج شريحة ميزة رأسية كاملة كـ Pilot Feature (Vertical Slice)**:
     * اختيار ميزة صغيرة ومحددة (مثل شاشة الإعدادات أو الملف الشخصي).
     * استخراجها في `:feature:profile` مع تطبيق نمط الـ DI و Navigation Contracts.
   - **المرحلة 4: تدريب الفريق وتوثيق المعايير (Documentation & Playbook)**: تحويل التجربة إلى دليل عمل للفريق لهجرة باقي الشاشات بالتوازي مع مهام السبرنت العادية.
   - **المرحلة 5: ضمور الموديول القديم**: يستمر موديول `:app` في فقدان الكلاسات تدريجياً حتى يتحول إلى مجرد موديول تجميع فارغ (Thin Composition Root).

## Practical walkthrough

خطة الهجرة التدريجية لشريحة رأسية (Vertical Slice Extraction):
```text
المرحلة 1: Monolith مع موديولات أساسية مستخرجة:
┌────────────────────────────────────────────────────────┐
│                         :app                           │
│ (Cart, Feed, Profile, Checkout, Auth كود مختلط بالداخل)│
└───────────┬────────────────────────────────┬───────────┘
            ▼                                ▼
    ┌───────────────┐                ┌───────────────┐
    │ :core:design  │                │ :core:network │
    └───────────────┘                └───────────────┘

المرحلة 2: استخراج أول ميزة مستقلة بنجاح (:feature:profile):
┌────────────────────────────────────────────────────────┐
│                         :app                           │
│        (فقط يجمع ويشغل Navigation و Hilt)             │
└───────┬────────────────────────────────────────┬───────┘
        ▼                                        ▼
┌─────────────────┐                     ┌─────────────────┐
│ :feature:profile│ (كود معزول جديد)    │ Monolith Legacy │ (القديم ينكمش)
└───────┬─────────┘                     └────────┬────────┘
        └────────────────┬───────────────────────┘
                         ▼
                 ┌───────────────┐
                 │ :core:*       │
                 └───────────────┘
```

## Why it matters and how it works

A monolith often contains implicit cross-package dependencies, so a big-bang split reveals many cycles at once. Extracting one vertical capability exposes a manageable contract and lets remaining code continue to ship. Adapter seams can preserve calls temporarily while new module boundaries are adopted. An explicit deletion condition prevents temporary bridges from becoming permanent architecture.

## Worked example

An app starts with Orders. First create a stable `OrderId`/repository API and move Orders UI, ViewModel and owned data behind it, while app registers its destination. Existing notification links still use a compatibility route mapped to the new entry. CI builds debug/release and tests a notification deep link. Next migrate callers and delete the old Orders package and adapter.

## Trade-offs and decision criteria

Incremental migration leaves temporary duplication and wiring, but limits product risk. Big-bang rewrite can reach a clean graph faster only with high capacity and stable requirements; it blocks delivery and widens regression risk. Choose a first feature with clear ownership and moderate complexity, not the most entangled payment flow.

## Failure modes

Files move without public API design, so every import becomes `api`. The old and new DI containers create different session instances. Redirect adapters persist indefinitely. CI tests only the extracted module while app variants fail. Metrics show worse build time but the team keeps splitting anyway.

## Production perspective

Track migration checklist, owner, old-caller count, graph rules, build metrics and rollback plan per slice. Run unit, integration and app assembly tests at each boundary; remove dead paths promptly.

## Interview answer — short

Migrating a monolith without blocking product delivery follows the Strangler Fig pattern. Teams extract horizontal core infrastructure modules first, then extract self-contained vertical feature modules using the API/Impl pattern. By wiring navigation through contract interfaces and freezing legacy monolith packages with CI lint rules, the monolith gradually shrinks into a pure composition root.

## Interview answer — structured

Migrating a monolithic Android codebase to a multi-module architecture requires a phased strategy that never halts product delivery.
Big-bang architectural rewrites are catastrophic because they block business features and generate impossible merge conflicts.
Instead, we apply the Strangler Fig pattern across four distinct phases.
In phase one, we extract stable, domain-agnostic foundational infrastructure from the bottom up, creating core:designsystem and core:network while setting up Version Catalogs and convention plugins.
In phase two, we extract vertical leaf features that have low coupling, such as Settings or Onboarding, splitting them into public api and private implementation modules.
The legacy monolith navigates to these new modules via abstract contracts.
In phase three, we migrate core data repositories into modular layers, providing bridge adapters so legacy monolithic code continues functioning.
In phase four, we establish CI lint rules that forbid adding new code to the legacy monolith, systematically shrinking it until the app module becomes a pure composition root.

## Interview answer — deep senior

In large-scale Android engineering, attempting a monolithic rewrite by pausing feature development is an organizational death sentence.
Product teams cannot freeze business roadmaps for six months while architects refactor the codebase.
Our proven methodology executes an incremental migration using the Strangler Fig pattern, ensuring that daily feature releases continue uninterrupted.
We begin with foundational leaf extraction.
We pull our visual styles, colors, and atomic Compose components into :core:designsystem, and our HTTP client configurations into :core:network.
Because infrastructure modules have zero business dependencies, this step creates zero regression risk while establishing our Gradle build-logic convention plugins and libs.versions.toml catalog.
Next, we execute vertical slice migrations starting with leaf features.
We identify an isolated, low-risk user flow—such as a Feedback or Profile Settings screen—and extract it completely into :feature:settings:api and :feature:settings:impl.
The legacy monolith in :app retains the navigation launcher, invoking SettingsNavigator wired via Hilt.
To prevent the monolith from regressing, we introduce architectural enforcement in CI using Konsist tests.
We freeze legacy monolithic packages: any pull request that adds new files to legacy app/src/main/java triggers an automated build failure with instructions to create a modular package.
New features are authored exclusively within modular subprojects, consuming the extracted core layers.
Over successive quarters, legacy activities are strangled one by one, until the monolithic :app module contains nothing more than the Application class, Hilt bindings, and top-level navigation graphs, successfully completing the transformation without a single day of blocked feature delivery.

## How to answer in the interview

- **Why:** modularization must preserve release cadence.
- **How:** extract one slice with tests and metrics.
- **Trade-off:** migration speed versus disruption.
- **Failure case:** big-bang move causes cycles and blocked teams.
- **Production solution:** ship reversible slices.

## Deep-dive talking points

Discuss baseline, first slice selection, compatibility adapters, DI identity, no-cycle rules, deletion and metrics.

## Follow-up questions

- **Interviewer:** "Why shouldn't you freeze feature development during modularization?"
  **Answer:** "Freezing feature development stalls business value for months, and merging back a massive refactoring branch inevitably causes catastrophic merge conflicts and regressions."

- **Interviewer:** "What defines a 'Thin Composition Root' in `:app`?"
  **Answer:** "An `:app` module that contains almost no Kotlin code except the `Application` class, top-level `NavHost` wiring, and root Hilt entry points."

## Self-check rubric

Give an incremental sequence, identify dual-wiring risk, define gate evidence and adapter removal.

## References and reviewed-on date

- [Android modularization guide](https://developer.android.com/topic/modularization) — phased boundaries.
- [Guide to app architecture](https://developer.android.com/topic/architecture) — ownership layers.

Technically reviewed against primary documentation on 2026-10-13.
