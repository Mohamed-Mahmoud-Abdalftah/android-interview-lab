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

## Concept and technical explanation

A clean multi-module architecture draws strict boundaries between reusable, domain-agnostic infrastructure and domain-specific feature logic:
- :core:network: Contains foundational transport plumbing including configured OkHttpClient instances, Retrofit builders, token refresh authenticators, certificate pinning configs, and network connectivity observers. It strictly excludes business DTOs, endpoint interfaces, and feature-specific models.
- :core:database: Provides the underlying Room database engine, base DAOs, database encryption wrappers (SQLCipher), migration runners, and common type converters. Feature entities belong in feature data modules.
- :core:ui: Holds reusable Compose widgets, layout primitives, image loader bindings, and accessibility wrappers. Pure visual styling tokens, colors, and themes reside in :core:designsystem.
- Feature modules (:feature:<name>): Encapsulate domain use cases, ViewModels, Compose screens, UI state definitions, feature-specific repository implementations, and private API service interfaces.

## Practical walkthrough (English)

Separation of concerns between infrastructure core and feature modules:
```kotlin
// 1. :core:network provides configured Retrofit factory
class NetworkClientFactory @Inject constructor(private val okHttpClient: OkHttpClient) {
    fun createRetrofit(baseUrl: String): Retrofit = Retrofit.Builder()
        .baseUrl(baseUrl)
        .client(okHttpClient)
        .addConverterFactory(Json.asConverterFactory("application/json".toMediaType()))
        .build()
}

// 2. :feature:orders defines its OWN private API interface and DTOs
interface OrdersApiService {
    @GET("/v1/orders")
    suspend fun getOrders(): List<OrderDto>
}

// 3. DI in :feature:orders binds service via :core:network factory
@Provides
fun provideOrdersApi(factory: NetworkClientFactory): OrdersApiService =
    factory.createRetrofit("https://api.store.com").create()
```

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

Core modules provide domain-agnostic infrastructure: core:network handles HTTP transport and token refresh; core:database manages the Room engine and encryption; and core:ui supplies reusable layout widgets and atomic controls. Feature modules house all business logic, containing domain use cases, ViewModels, Compose screens, feature repositories, and specific API endpoints.

## Interview answer — structured

Designing a scalable modular architecture requires drawing clear boundaries between infrastructural platform modules and user-facing feature modules.
In the infrastructure tier, core:network provides preconfigured HTTP engines, certificate pinning, and authentication interceptors without containing feature API endpoints or business models.
Similarly, core:database manages the foundational Room database instance, encryption wrappers, and migration runners without defining specific feature tables.
The core:ui module supplies generic Compose modifiers, accessibility helpers, and custom layouts, while visual design tokens reside in core:designsystem.
Feature modules sit above this infrastructure tier.
Each feature module owns its entire business domain slice, including domain use cases, ViewModels, Compose screens, repository implementations, and private Retrofit service interfaces.
This separation ensures core modules remain stable, leaf-oriented dependencies that never require recompilation when product features change.

## Interview answer — deep senior

The defining hallmark of mature Android systems architecture is the ruthless exclusion of business knowledge from infrastructural core modules.
A frequent architectural failure occurs when teams place feature-specific endpoints or business models into :core:network, turning it into a bottleneck that forces full recompilation whenever a single API endpoint changes.
In our production standard, :core:network provides only transport-level mechanics.
It exports configured Retrofit builders, OkHttp interceptors for OAuth token renewal, certificate pinning definitions, and JSON serialization converters, but zero endpoint interfaces.
Each feature module declares its own private Retrofit interfaces and network DTOs within its internal data layer.
The same strict rule applies to :core:database: it exports the Room database builder, SQLCipher passphrase providers, and migration orchestrators, while individual feature entities and DAOs are registered modularly.
At the UI layer, :core:ui provides technical interaction wrappers such as keyboard insets listeners, pull-to-refresh containers, and image loading coil bindings, whereas :core:designsystem houses atomic tokens and buttons.
Feature modules encapsulate everything related to user flows, maintaining private domain models and state machines.
This strict structural hygiene ensures that core infrastructure changes infrequently, maximizing remote build cache hit rates across distributed development teams. We also configure automated linter rules to flag any PR that introduces domain-specific entity names or endpoint paths inside infrastructure modules, preserving platform purity.

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
