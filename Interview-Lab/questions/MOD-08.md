---
id: "MOD-08"
question: "What belongs in :core:network, :core:database, :core:ui, and feature modules?"
topic: "Gradle Modularization & Dependency Boundaries"
code: "MOD"
group: "B"
phase: 4
priority: "P1"
order: 361
editorial_status: "reviewed"
---

# MOD-08

## Original interview question

What belongs in :core:network, :core:database, :core:ui, and feature modules?

## What the interviewer evaluates

- Distinguish infrastructure from feature policy and UI.
- Prevent giant core modules and domain leakage.
- Specify ownership of migrations, API clients and reusable UI.

## Explanation in Arabic

ما هي المسؤوليات الدقيقة التي تنتمي لكل من: `:core:network`، و `:core:database`، و `:core:ui`، و `:feature`؟ وكيف تمنع تسرب المنطق؟

1. `:core:network` (البنية التحتية للاتصال بالشبكة):
   - **ما ينتمي إليه**: إعدادات `OkHttpClient`, محولات `Retrofit`, إدارة شهادات الأمان و SSL Pinning, الـ Auth Interceptors لإرفاق الـ Bearer Tokens, ومتابعة جودة الاتصال وتحديث الـ Base URL.
   - **ما لا ينتمي إليه (خطر التسريب)**: نماذج بيانات خاصة بميزة تجارية معينة (مثل `CartResponse` أو `OrderDto`). هذه النماذج تنتمي لموديول بيانات الميزة نفسها (`:data:cart` أو `:data:order`).

2. `:core:database` (البنية التحتية لقاعدة البيانات المحلية):
   - **ما ينتمي إليه**: بناء كائن `RoomDatabase` الرئيسي، وإدارة الـ TypeConverters العامة، واستراتيجيات التشفير (SQLCipher)، وتنفيذ قواعد الترقية (Database Migrations).
   - **ما لا ينتمي إليه**: استعلامات الـ SQL الخاصة بشاشات معينة أو الـ DAOs المحددة للميزات.

3. `:core:ui` / `:core:designsystem` (مكونات الواجهة المشتركة):
   - **ما ينتمي إليه**: ألوان التطبيق (Color Palette), الخطوط (Typography), الأشكال (Shapes), وأزرار عامة وحقول إدخال ومكونات عرض خالية من المنطق التجاري.
   - **ما لا ينتمي إليه**: بطاقات عرض تعتمد على موديل تجاري (مثل بطاقة عرض المنتج `ProductCard` التي تعتمد على `ProductEntity`). يجب أن تأخذ المكونات بيانات بدائية (Primitives).

4. `:feature:*` (موديولات الميزات المستقلة):
   - **ما ينتمي إليه**: واجهات العرض (Composables/Screens), الـ ViewModels, الـ UI State, والـ Navigation Routes الخاصة بالميزة فقط.

## Practical walkthrough

تنظيم المسؤوليات ومنع تسريب منطق الميزات إلى موديولات الـ Core:
```kotlin
// ❌ تسريب خاطئ: وضع كود منتج تجاري داخل :core:ui:
// في موديول :core:ui:
@Composable
fun ProductCard(product: ProductDomainModel) { /* ... */ }
// خطأ! جعلت :core:ui يعتمد على موديل تجاري في :domain:product!

// ✅ التصميم النظيف: :core:ui يعتمد فقط على عناصر بدائية (Stateless Primitives):
// في موديول :core:ui:
@Composable
fun StandardMediaCard(
    title: String,
    subtitle: String,
    imageUrl: String,
    onClick: () -> Unit
) {
    Card(...) { /* رسم عام بدون أي اعتماد على أي موديل تجاري */ }
}

// 📁 في موديول :feature:catalog:
@Composable
fun CatalogProductItem(product: Product, onSelect: () -> Unit) {
    // الميزة هي التي تمرر البيانات للمكون العام في :core:ui:
    StandardMediaCard(
        title = product.name,
        subtitle = product.formattedPrice,
        imageUrl = product.imageUrl,
        onClick = onSelect
    )
}
```

## Why it matters and how it works

Core modules often have high fan-out, so changing their public API recompiles many consumers. Keeping infrastructure interfaces narrow protects that boundary. Feature modules remain cohesive when their UI and workflow policy live together. Database schema can be centralized physically yet ownership of feature migrations and tables should be explicit so teams do not edit one opaque shared module blindly.

## Worked example

Orders data uses a `NetworkClient` configured in core network but owns `OrdersApi` request/response mapping. Core database configures Room and the migration test harness; Orders data owns its `OrderEntity` schema and migration change review. Core UI provides an `AppButton` that accepts text/loading/click, while Orders feature formats the order-status message and decides when the button is enabled.

## Trade-offs and decision criteria

Central infrastructure reduces duplication but becomes a coordination hotspot. Feature-owned endpoint/DAO code keeps policy local, though cross-feature transactions require deliberate shared ownership. A separate UI core simplifies consistency but can over-generalize components. Choose a boundary that minimizes unstable public API and has a clear maintainer.

## Failure modes

Every feature-specific Retrofit interface is placed in core network, forcing core changes for all releases. Core UI accepts an `Order` domain object. Database migrations are added without the feature owner and break another variant. Multiple feature data modules configure incompatible HTTP clients accidentally.

## Production perspective

Publish module responsibilities and codeowners, track public API churn and affected builds, and test migrations and cross-feature integration. Review proposed core additions for genuine multi-feature reuse and stable semantics.

## Interview answer — short

:core:network owns network infrastructure (OkHttp, SSL, Retrofit engine, auth interceptors). :core:database owns the Room database container and migrations. :core:ui owns stateless design tokens and generic widgets. Feature modules own user-facing screens, ViewModels, and presentation state, ensuring zero business domain models leak into core foundations.

## Interview answer — structured

Clear architectural separation between infrastructure core modules and domain feature modules prevents the core from degrading into an unmaintainable monolith:

1. **`:core:network`**: Houses HTTP client engines (`OkHttpClient`), token refresh interceptors, SSL pinning configurations, and connectivity observers. It must **not** host feature-specific API endpoints (like `OrderApiService`); feature APIs belong in their respective `:data:*` modules.
2. **`:core:database`**: Manages the underlying database engine (`RoomDatabase`), encryption keys, and schema migration coordinators. Feature-specific DAOs and entities should be provided by data modules and aggregated by the database.
3. **`:core:ui` (Design System)**: Contains design tokens (theme colors, typography, elevations) and generic, stateless UI primitives (`AppButton`, `EmptyStateView`, `AppDialog`). It must remain strictly agnostic of business models, accepting only primitive parameters.
4. **`:feature:*`**: Contains end-to-end presentation logic for a user journey: composable screens, ViewModels, UI state machines, and local navigation routes.

## Interview answer — deep senior

A critical design challenge in multi-module database architecture is **Room Database Aggregation**.

Room requires its `@Database(entities = [...], version = ...)` annotation to enumerate all entity classes at compile time. If entities live inside feature modules, having `:core:database` declare the database directly creates an illegal circular dependency (core depending on features).

Senior engineers resolve this in one of two ways:
1. **Entity Delegation in `:core:database`**: Entities live in `:core:model` or dedicated `:data:*:model` modules that `:core:database` imports, keeping DAOs internal to their data modules.
2. **Single Database in `:app`**: The concrete `@Database` class is declared inside the `:app` module (where all feature data modules are already aggregated), while `:core:database` provides only the database builder infrastructure and migrations.

## How to answer in the interview

- **Why:** core should not absorb feature logic.
- **How:** define narrow infrastructure and feature ownership.
- **Trade-off:** reuse versus central bottleneck.
- **Failure case:** core imports feature DTO.
- **Production solution:** dependency direction and API audit.

## Deep-dive talking points

Discuss transport versus endpoint policy, physical database versus schema ownership, design-system neutrality and fan-out.

## Follow-up questions

- **Interviewer:** "Why shouldn't an Auth Token interceptor live in a feature module?"
  **Answer:** "Because all network requests across all feature modules need authentication; centralizing token refresh in `:core:network` avoids duplicate or conflicting token states."

- **Interviewer:** "Can a feature module have its own separate Room Database?"
  **Answer:** "Yes, if the feature's data is completely independent and offline-contained, a separate SQLite file is often cleaner than a single shared database."

## Self-check rubric

Place four concrete classes in modules, explain one shared exception, and identify a giant-core smell.

## References and reviewed-on date

- [Android modularization patterns](https://developer.android.com/topic/modularization/patterns) — feature and core roles.
- [Data layer guidance](https://developer.android.com/topic/architecture/data-layer) — repository ownership.

Technically reviewed against primary documentation on 2026-10-13.
