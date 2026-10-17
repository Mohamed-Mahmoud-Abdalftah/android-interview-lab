---
id: "MOD-02"
question: "Compare app, feature, core, data, domain, and design-system modules."
topic: "Gradle Modularization & Dependency Boundaries"
code: "MOD"
group: "A"
phase: 4
priority: "P1"
order: 355
editorial_status: "reviewed"
---

# MOD-02

## Original interview question

Compare app, feature, core, data, domain, and design-system modules.

## What the interviewer evaluates

- Assign distinct responsibilities without a rigid universal taxonomy.
- Explain dependency direction and app composition.
- Prevent core/design system from absorbing feature-specific logic.

## Concept and technical explanation

In a clean multi-module Android architecture, modules are classified by responsibility and layer into distinct categories:
- :app: The top-level assembly coordinator that compiles features and core into the installable APK/AAB and initializes global frameworks (Hilt application component, crash analytics).
- :feature: High-level business slices implementing user flows, Compose UI, and ViewModels (e.g., :feature:checkout). Features never depend on sibling features directly.
- :core: Low-level, non-business infrastructure utilities and platform wrappers (e.g., :core:network, :core:database).
- :data: Manages persistence, network data sources, and repository implementations.
- :domain: Pure Kotlin/Java business logic containing use cases, entities, and repository interfaces without Android framework coupling.
- :design-system: UI tokens, themes, typography, and reusable atomic Compose widgets. It maintains visual consistency without depending on business features or data layers.

## Practical walkthrough (English)

Layered dependency flow and separation of concerns across module types:
```kotlin
// 1. :core:designsystem (No feature dependencies)
@Composable
fun PrimaryFintechButton(text: String, onClick: () -> Unit) { /* ... */ }

// 2. :domain (Pure Kotlin, no Android imports)
data class UserProfile(val id: String, val balance: BigDecimal)
interface UserRepository {
    suspend fun fetchProfile(): Result<UserProfile>
}

// 3. :feature:profile (Depends on domain, core:ui, designsystem)
class ProfileViewModel @Inject constructor(
    private val getUserProfileUseCase: GetUserProfileUseCase
) : ViewModel() { /* ... */ }

// 4. :app (Root composition root)
// dependencies { implementation(project(":feature:profile")) }
```

## Explanation in Arabic

مقارنة معمارية شاملة بين أنواع موديولات أندرويد:
`:app`، و `:feature`، و `:core`، و `:data`، و `:domain`، و `:designsystem`:

1. `:app` (موديول التجميع النهائي والـ Composition):
   - الموديول التطبيقي الرئيسي (`com.android.application`).
   - **وظيفته**: تجميع كل موديولات الـ Features والـ Data، وبناء شجرة الـ Dependency Injection المركزية (Hilt Root)، وإعداد الـ Navigation Graph النهائي وتهيئة الـ Application class. لا يحتوي على أي منطق أعمال (Business Logic).

2. `:feature:*` (موديولات الميزات والشاشات):
   - موديولات مكتبية تمثل ميزة مستقلة من منظور المستخدم (مثل `:feature:cart`, `:feature:profile`).
   - تحتوي على شاشات Compose أو Views، والـ ViewModels، والـ UI State، ومنطق العرض. لا تعتمد ميزات على ميزات أخرى مباشرة.

3. `:domain:*` (موديول منطق الأعمال الصافي):
   - موديول Kotlin نقي (Pure JVM Library بدون أي تبعيات Android SDK).
   - يحتوي على الكيانات النقية (Entities)، ونماذج الأعمال، والـ UseCases، وواجهات الـ Repositories المجردة.

4. `:data:*` (موديول إدارة البيانات وتطبيق العقود):
   - يطبق واجهات الـ Repositories المعرفة في الـ Domain.
   - يتعامل مع مصادر البيانات المحلية (Room) والشبكية (Retrofit) ويحول الـ DTOs إلى Domain Models.

5. `:core:*` (موديولات البنية التحتية المشتركة):
   - مكتبات عامة تقدم خدمات منخفضة المستوى مستقلة عن أي ميزة تجارية محددة (مثل `:core:network`, `:core:database`, `:core:datastore`, `:core:analytics`).

6. `:designsystem` (نظام التصميم الموحد):
   - موديول يحتوي على مكونات الـ UI المشتركة القابلة لإعادة الاستخدام: الألوان، والخطوط، والـ Buttons، والـ Cards، والـ Dialogs الموحدة للتطبيق، بدون أي منطق أعمال أو ارتباط بـ API.

## Practical walkthrough

اتجاه التبعيات (Dependency Direction) المسموح به بين أنواع الموديولات:
```text
                     ┌───────────────┐
                     │     :app      │ (Application Assembly)
                     └───────┬───────┘
             ┌───────────────┴───────────────┐
             ▼                               ▼
   ┌───────────────────┐           ┌───────────────────┐
   │ :feature:checkout │           │  :feature:catalog │
   └─────────┬─────────┘           └─────────┬─────────┘
             │                               │
             ├───────────────┬───────────────┤
             ▼               ▼               ▼
     ┌──────────────┐ ┌──────────────┐ ┌───────────────┐
     │ :core:design │ │:domain:order │ │ :core:network │
     └──────────────┘ └──────▲───────┘ └───────▲───────┘
                             │                 │
                      ┌──────┴───────┐         │
                      │  :data:order ├─────────┘
                      └──────────────┘
```
قاعدة ذهبية: اتجاه الأسهم دائماً للأسفل باتجاه الاستقرار. لا يمكن لـ :core أو :designsystem أن يعتمد على أي :feature أبداً!

## Why it matters and how it works

Module names encode ownership and intended dependency edges. App modules package final variants and serve as composition roots. Feature modules group user-facing behavior; data modules implement external access; domain modules can keep contracts/policies independent when reuse warrants them. Core and design-system modules expose cross-cutting primitives, and their APIs require careful governance because many consumers compile against them.

## Worked example

`:feature:orders` renders orders and depends on `:domain:orders` repository interface plus `:designsystem`. `:data:orders` implements it using `:core:network` and `:core:database`. `:app` includes the feature and implementation. The feature does not directly import Retrofit DTOs or a database DAO, and the design system accepts display values rather than an `Order` entity.

## Trade-offs and decision criteria

A separate domain module can clarify reusable policy but adds indirection if it holds only one interface. Shared core reduces duplication but can become a high-fan-out rebuild hotspot. Feature-local data may be simpler for a small isolated feature. Use names to express actual boundaries, not to enforce a fixed layered template.

## Failure modes

Every miscellaneous helper goes into `:core:common`. Design-system UI imports payment business types. A feature depends on data implementation, then data depends back on feature. The app contains all business logic while feature modules are empty shells.

## Production perspective

Publish a dependency rule with examples and check it in CI. Review public APIs and high-fan-out modules, and use app assembly plus feature tests to prove the composition remains valid.

## Interview answer — short

Layered modular architecture divides responsibilities across module types: app acts as the root assembly coordinator; feature modules implement distinct user journeys; core provides shared platform infrastructure like networking; data encapsulates repositories and persistence; domain houses pure business use cases; and design-system centralizes reusable UI components and themes.

## Interview answer — structured

In a mature multi-module Android architecture, every module type has a distinct responsibility within the directed dependency graph.
The app module sits at the top as the composition root, wiring together features and initializing application-level dependency injection without holding business logic.
Feature modules encapsulate discrete user flows like login or checkout, containing screens, ViewModels, and UI state machines while remaining isolated from sibling features.
The domain module contains pure business logic, entities, and repository interfaces, remaining completely free of Android framework dependencies to enable fast unit testing.
The data module implements these repository interfaces, managing remote network clients and local database persistence.
Core modules provide foundational infrastructure such as networking, crypto utilities, and database drivers that any layer can consume.
The design-system module supplies shared UI components, colors, typography, and design tokens, ensuring visual consistency across all feature modules without importing domain models or business rules.

## Interview answer — deep senior

Architecting a scalable Android dependency graph requires categorizing modules into clear horizontal layers and vertical slices.
The root app module serves strictly as an assembly coordinator; it applies the Android application plugin, binds Hilt modules, configures navigation graphs, and bundles features into the final binary.
Feature modules represent vertical business slices that deliver user-facing value.
To maintain high cohesion, feature modules must never depend directly on sibling feature modules.
When cross-feature communication is required, it must route through dedicated public API modules or shared navigation contracts.
Horizontally, the domain layer represents the core business policy of the enterprise.
By maintaining domain as a pure Kotlin library free from Android framework dependencies, use cases execute instantaneously in JVM unit tests without needing Robolectric or device emulators.
The data module implements domain repository contracts, mapping network DTOs and Room entities into immutable domain models.
Underneath, core modules provide reusable platform capabilities such as :core:network for Retrofit instances and :core:database for SQLite drivers.
In the visual presentation layer, :core:designsystem acts as the single source of truth for the company's visual language, isolating Compose components and theme tokens from feature-specific logic.
Enforcing this strict layered flow ensures that the dependency graph remains acyclic, predictable, and resilient to refactoring. This separation empowers individual product squads to ship feature updates independently while maintaining rock-solid architectural cohesion across the entire mobile application.

## How to answer in the interview

- **Why:** module role clarifies ownership.
- **How:** assign app composition, feature behavior and narrow shared code.
- **Trade-off:** reuse versus generic core sprawl.
- **Failure case:** feature imports another feature internals.
- **Production solution:** contract and dependency graph review.

## Deep-dive talking points

Explain ownership, dependency edges, app composition, optional domain, shared API fan-out, and UI neutrality.

## Follow-up questions

- **Interviewer:** "Why should `:core:designsystem` never contain business models?"
  **Answer:** "Because it turns the design system into a coupled monolith. A user profile card in designsystem should accept primitive properties (`name: String`, `avatarUrl: String`), not a domain `User` entity."

- **Interviewer:** "Can a `:feature` module depend on multiple `:domain` modules?"
  **Answer:** "Yes. A feature (such as checkout) may need domain rules from `:domain:cart`, `:domain:payment`, and `:domain:user`."

## Self-check rubric

Assign six module roles, draw an acyclic orders path, and identify one over-shared module smell.

## References and reviewed-on date

- [Android modularization guide](https://developer.android.com/topic/modularization) — module ownership.
- [Common modularization patterns](https://developer.android.com/topic/modularization/patterns) — feature/data structures.

Technically reviewed against primary documentation on 2026-10-13.
