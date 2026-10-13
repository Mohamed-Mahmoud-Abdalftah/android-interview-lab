---
id: "MOD-07"
question: "Design a multi-module structure for a large app."
topic: "Gradle Modularization & Dependency Boundaries"
code: "MOD"
group: "B"
phase: 4
priority: "P1"
order: 360
editorial_status: "reviewed"
---

# MOD-07

## Original interview question

Design a multi-module structure for a large app.

## What the interviewer evaluates

- Produce a plausible acyclic graph with ownership and app composition.
- Explain APIs, data implementation, navigation and DI.
- Specify build/test evidence and avoid module proliferation.

## Explanation in Arabic

كيف تصمم هيكل نمطي متكامل (Multi-Module Architecture) لتطبيق Android ضخم الحجم؟

1. المخطط المعماري الهرمي الموصى به (The Recommended Layered Graph):
   - **`:app` (Root Composition)**: موديول خفيف جداً يجمع شجرة الـ DI والـ Navigation والـ Application Class.
   - **`:features` (Vertical Slices)**: مقسمة بنمط API/Impl لكل ميزة:
     * `:feature:auth:api` (عقود، مسارات، واجهات فقط)
     * `:feature:auth:impl` (الشاشات، الـ ViewModels، والتنفيذ الفعلي)
     * `:feature:checkout:api` و `:feature:checkout:impl`
   - **`:core` (Horizontal Slices)**: خدمات البنية التحتية المشتركة:
     * `:core:designsystem` (الألوان، الخطوط، المكونات الرسومية)
     * `:core:network` (Retrofit, OkHttp, SSL Pinning)
     * `:core:database` (Room database, migrations)
     * `:core:analytics` (تتبع الأحداث)
     * `:core:model` (نماذج البيانات المشتركة النظيفة)

2. قواعد التحكم في شجرة التبعيات:
   - موديولات الـ Feature لا تعتمد على موديولات Feature أخرى إطلاقاً؛ بل تعتمد فقط على الـ `:api` موديول للميزة المطلوبة.
   - موديولات الـ `:core` لا تعتمد على أي موديول Feature في أي حال من الأحوال.
   - استخدام Version Catalogs (`libs.versions.toml`) و Convention Plugins لتوحيد إعدادات Gradle لجميع الموديولات.

## Practical walkthrough

الهيكل التنظيمي للموديولات في مشروع حقيقي واسع النطاق:
```text
MyEnterpriseApp/
├── app/                           // Final packaging, Hilt root, NavHost
├── build-logic/                   // Custom Gradle Convention Plugins
├── core/
│   ├── designsystem/              // Material3 tokens, Custom Buttons, Theme
│   ├── network/                   // OkHttp, Retrofit, Auth Interceptors
│   ├── database/                  // Room Database, DAOs
│   ├── model/                     // Immutable shared data classes (User, Money)
│   └── testing/                   // Test rules, Fake repositories
└── feature/
    ├── feed/
    │   ├── api/                   // FeedNavigationContract, FeedEntryRoute
    │   └── impl/                  // FeedScreen, FeedViewModel, FeedPagingSource
    └── cart/
        ├── api/                   // CartBadgeContract, AddToCartUseCase
        └── impl/                  // CartScreen, CartViewModel
```
كل ميزة مفصولة إلى API و Implementation، مما يضمن سرعة خرافية في الـ Incremental Compilation وعزل تام بين الفرق!

## Why it matters and how it works

Separate feature modules can encapsulate screen behavior and team work. Contracts direct dependencies toward stable abstractions; data implementations and app bindings complete the graph. Build performance depends on public ABI changes and Gradle configuration, so a new module must earn its maintenance cost. App-level navigation and DI composition prevent feature-to-feature cycles.

## Worked example

`:feature:checkout` depends on `:domain:checkout-api` and `:designsystem`; `:data:checkout` implements the repository using `:core:network` and `:core:database`. `:app` brings both in and maps a typed checkout destination to a feature entry point. Catalog exposes a product ID contract; checkout reloads needed price/availability from its own domain path, not catalog UI internals.

## Trade-offs and decision criteria

Vertical feature modules support ownership; horizontal core layers avoid infrastructure duplication. Too much separation creates configuration overhead, duplicate DTO mapping and difficult DI graph visibility. A small common capability can begin inside one owner and be extracted when multiple consumers need a stable contract.

## Failure modes

All features depend on one unstable `:core:common`. Feature modules import each other's screen classes. App contains most business logic while modules are only wrappers. Every dependency is `api`, broadening consumer classpaths. Independent feature tests pass while final variant assembly fails.

## Production perspective

Write allowed-edge rules, ownership documentation and a module graph check. Track clean/configuration and incremental build times, test feature-local logic and final app assembly, and review public APIs as carefully as external SDK APIs.

## Interview answer — short

Design a large-scale app using a layered DAG: an assembly :app module, feature modules split into :feature:x:api (contracts) and :feature:x:impl (screens/logic), horizontal :core infrastructure (network, database, designsystem), and centralized build-logic convention plugins with a Version Catalog.

## Interview answer — structured

A production-grade multi-module architecture for an enterprise Android app balances compilation speed, encapsulation, and team velocity:

1. **Layered Module Architecture**:
   - **`:app`**: Thin composition root. Assembles the final APK, provisions Hilt graph roots, and attaches top-level navigation graphs.
   - **`:feature:*:impl`**: Contains UI Composables, ViewModels, and internal presentation logic. Feature implementations never depend directly on sibling feature implementations.
   - **`:feature:*:api`**: Lightweight contract modules containing only navigation routes, shared events, and public interfaces. Features interact exclusively through peer API modules.
   - **`:core:*`**: Horizontal foundations (`:core:designsystem`, `:core:network`, `:core:database`, `:core:model`, `:core:analytics`).

2. **Standardized Build Governance**:
   - Centralized dependency coordinates via `libs.versions.toml`.
   - Custom Gradle Convention Plugins in `build-logic` (`android.library`, `android.feature`, `android.compose`) to eliminate 95% of boilerplate from individual `build.gradle.kts` files.

## Interview answer — deep senior

A critical pitfall in large-scale modularization is **Uncontrolled Micro-Modularization** (creating 300+ tiny modules for single classes).

Every Gradle module introduces overhead: configuration evaluation time, IDE indexing load, and task scheduling overhead. If modules are too granular, cold build times and Android Studio sync times explode.

To maintain an optimal balance:
- Extract a module only when there is a **real compile boundary** (independent team ownership, distinct release cycle, or high rebuild frequency).
- Use the `:api` / `:impl` split primarily for high-traffic features that multiple teams interact with, rather than dogmatically splitting every trivial screen.
- Implement continuous CI graph validation (enforcing no feature-to-feature direct implementation dependencies) to protect the DAG from accidental erosion.

## How to answer in the interview

- **Why:** large teams need independent boundaries.
- **How:** map owners and DAG before splitting.
- **Trade-off:** parallel work versus configuration overhead.
- **Failure case:** big-bang split blocks releases.
- **Production solution:** incremental extraction with build metrics.

## Deep-dive talking points

Draw feature/data/core/app edges, public API, navigation ownership, DI wiring and build measurement.

## Follow-up questions

- **Interviewer:** "What is the primary benefit of the `:api` vs `:impl` module split?"
  **Answer:** "It minimizes rebuild cascades: modifying code inside `:impl` does not recompile other modules that only depend on the stable `:api` contract."

- **Interviewer:** "How do feature modules navigate to each other without depending on `:impl`?"
  **Answer:** "They navigate using route contracts or destinations defined in peer `:api` modules, resolved at runtime by the root navigation graph in `:app`."

## Self-check rubric

Sketch an acyclic commerce graph, assign owners, and show integration and performance evidence.

## References and reviewed-on date

- [Android modularization guide](https://developer.android.com/topic/modularization) — graph design.
- [Common modularization patterns](https://developer.android.com/topic/modularization/patterns) — feature and core examples.

Technically reviewed against primary documentation on 2026-10-13.
