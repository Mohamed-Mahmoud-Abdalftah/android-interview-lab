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

Migrate a monolith incrementally using the Strangler Fig pattern. Establish Gradle convention plugins first, extract core horizontal foundations (:core:designsystem, :core:network) bottom-up, migrate one vertical feature slice as a pilot to validate the pattern, and gradually extract remaining features during regular sprints until :app becomes a thin assembly root.

## Interview answer — structured

Migrating an enterprise Android monolith to a multi-module architecture without halting feature velocity relies on the **Strangler Fig Pattern** executed in four controlled phases:

1. **Phase 1: Build Governance & Tooling**:
   - Introduce `libs.versions.toml` and custom Gradle convention plugins in `build-logic`.
   - Establish CI performance baselines for Gradle build times and memory consumption.

2. **Phase 2: Bottom-Up Foundation Extraction**:
   - Extract horizontal infrastructure that has zero feature dependencies: `:core:designsystem`, `:core:network`, and `:core:model`.
   - The legacy monolith consumes these modules immediately, proving they work in production.

3. **Phase 3: The Pilot Vertical Slice**:
   - Select an isolated, low-risk feature (e.g. `:feature:settings`).
   - Extract its UI, ViewModel, Domain logic, and Data layer into dedicated modules, establishing the navigation and DI patterns for the entire organization.

4. **Phase 4: Opportunistic Feature Migration**:
   - Create a 'Modularization Playbook'. Feature teams extract their own modules incrementally whenever embarking on a major feature redesign, until `:app` shrinks to a thin composition shell.

## Interview answer — deep senior

The greatest danger during a monolith migration is **The Entangled Dependency Knot** (where Class A in the feature imports 25 random utility and helper classes from the monolith).

If you try to extract everything Class A touches, you end up moving half the monolith into the new module. To break this knot in production:

1. **Invert the Seam with an Interface**: If the feature needs a monolith service (`LegacySessionManager`), define an interface inside the new feature module (`interface SessionProvider`). Have the legacy monolith implement this interface and inject it into the feature.

2. **Temporary Bidirectional Bridge**: The feature compiles against its own interface, completely isolated from monolith internals. Once the session logic itself is migrated to a core module later, you simply delete the bridge implementation in the monolith.

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
