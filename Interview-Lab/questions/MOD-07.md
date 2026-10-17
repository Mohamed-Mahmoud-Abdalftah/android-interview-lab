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

## Concept and technical explanation

Designing an enterprise multi-module architecture requires harmonizing horizontal architectural layers with vertical feature slices into a coherent Directed Acyclic Graph (DAG). An optimal structure establishes three primary tiers:
1. Root Tier (:app): Pure composition root that configures Hilt dependency injection, builds the application class, and packages release artifacts.
2. Feature Tier (:features:<name>): Subdivided into :api (public contracts, interfaces, and navigation destinations) and :impl (UI screens, ViewModels, and internal business logic). Cross-feature dependencies are strictly restricted to :api modules, completely preventing inter-feature implementation coupling.
3. Core Infrastructure Tier (:core:<name>): Highly cohesive, domain-agnostic platform modules including :core:network (Retrofit, OkHttp, cert pinning), :core:database (Room, encryption), :core:designsystem (Compose components, typography, theme), and :core:common (dispatchers, logging abstractions).
This taxonomy maximizes parallel build lanes, enforces clean code ownership, and prevents dependency spaghetti.

## Practical walkthrough (English)

Scalable enterprise multi-module directory and dependency structure:
```text
root/
├── app/                        (Composition root, builds APK)
├── core/
│   ├── designsystem/          (Compose theme, atomic UI components)
│   ├── network/               (Retrofit, OkHttp engine, token refresh)
│   ├── database/              (Room database, DAOs, migrations)
│   └── common/                (Coroutines dispatchers, extensions)
└── features/
    ├── checkout/
    │   ├── api/               (CheckoutNavigator, CheckoutResult contract)
    │   └── impl/              (CheckoutScreen, CheckoutViewModel, CheckoutRepository)
    └── catalog/
        ├── api/               (CatalogRoute contract)
        └── impl/              (CatalogScreen, depends on :features:checkout:api ONLY)
```

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

An enterprise multi-module structure organizes the codebase into a clean DAG: an app composition root at the top, vertical feature modules split into public api contracts and private implementation details, and horizontal core modules underneath covering networking, database, design-system, and platform utilities. Features communicate strictly through api interfaces, preventing direct coupling and maximizing build parallelism.

## Interview answer — structured

Designing a multi-module architecture for a large application requires balancing feature autonomy with centralized infrastructural consistency.
At the top level, the app module serves as the composition root, initializing application-level dependency injection and assembling features into the final binary without containing business logic.
Feature modules represent vertical domain slices such as checkout, search, or profile.
To prevent coupling, each feature is divided into a public api module and a private implementation module.
When one feature needs to trigger an action in another, it imports only the public api contract, keeping internal screens and ViewModels completely hidden.
Beneath the feature layer, horizontal core modules provide foundational capabilities.
These include core:designsystem for reusable UI components, core:network for authenticated HTTP clients, and core:database for local persistence.
This structure maintains an acyclic dependency graph where compilation tasks run concurrently across available CPU cores.

## Interview answer — deep senior

When architecting a multi-module codebase for an organization with multiple engineering squads, our primary objectives are optimizing build parallelism, isolating blast radiuses, and enforcing team autonomy.
A flat structure where features import one another degenerates into an unmaintainable web of dependencies.
Our architecture enforces a strict tripartite topology: the assembly layer, the feature layer, and the core platform layer.
The feature layer is structured around the API/Implementation pattern.
For example, :feature:payment contains two distinct Gradle subprojects: :feature:payment:api and :feature:payment:impl.
The api module contains solely pure interfaces, such as PaymentLauncher, and immutable navigation arguments, compiling in milliseconds because it has zero UI or data dependencies.
When :feature:cart requires payment functionality, it declares an implementation dependency strictly on :feature:payment:api.
The private implementation details in :feature:payment:impl—including payment gateways, Room database entities, and Compose payment dialogs—remain completely encapsulated behind Kotlin internal modifiers.
The root app module imports both implementations and binds them via Hilt at application start.
Horizontally, core modules are kept strictly domain-agnostic: :core:designsystem holds our visual design tokens, :core:network provides configured Retrofit builders, and :core:common distributes test dispatchers.
This strict structural governance preserves a pure Directed Acyclic Graph, guarantees predictable remote build caching, and allows multiple product squads to ship features in parallel without stepping on one another.

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
