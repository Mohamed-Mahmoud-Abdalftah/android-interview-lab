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

:app aggregates modules, wires Hilt DI, and builds the final APK. :feature holds UI screens, ViewModels, and state. :domain contains pure JVM business logic and repository interfaces. :data implements repositories via Room and Retrofit. :core provides low-level infrastructure (network, analytics). :designsystem provides reusable design tokens, typography, and UI widgets without business logic.

## Interview answer — structured

A disciplined taxonomy assigns distinct responsibilities and strict dependency rules across module categories:

1. **`:app`**: The composition root. It applies `com.android.application`, aggregates all feature and data modules, configures the Hilt root component, registers global navigation, and generates the final APK/AAB. It contains zero business logic.
2. **`:feature:*`**: User-facing vertical slices (`:feature:login`, `:feature:feed`). Contains UI composables, ViewModels, navigation routes, and presentation state. Features must never depend directly on sibling feature implementation modules.
3. **`:domain:*`**: Pure Kotlin/JVM modules without Android framework imports. Houses domain entities, Use Cases, and abstract repository interfaces. It represents the most stable layer of the architecture.
4. **`:data:*`**: Implements domain repository contracts using local databases and remote network APIs, encapsulating caching and network resilience.
5. **`:core:*`**: Horizontal infrastructure libraries (`:core:network`, `:core:analytics`, `:core:database`) reusable across any feature.
6. **`:core:designsystem`**: Houses shared theme tokens (colors, typography, shapes) and stateless reusable UI components (buttons, headers, empty states). It must remain strictly agnostic of business domains.

## Interview answer — deep senior

When enforcing module boundaries in enterprise codebases, architects use **dependency analysis tools (like Dependency Analysis Gradle Plugin)** and custom lint checks to enforce directional contracts:

- **Rule 1 (The Gravity Rule)**: Dependencies only flow downward toward higher stability. A low-level module like `:core:designsystem` or `:core:network` must **NEVER** import a `:feature` module. Doing so inverts the architecture and causes instant cyclic dependency locks.
- **Rule 2 (Domain Purity)**: The `:domain` module should use the standard `kotlin("jvm")` plugin rather than `com.android.library`. This guarantees that Android framework dependencies (like `android.content.Context` or `android.os.Bundle`) cannot compile inside domain logic, keeping business rules testable on local JVMs in single-digit milliseconds.
- **Rule 3 (Data Encapsulation)**: DAOs, Retrofit interfaces, and Room entities are `internal` to the `:data` module. Features only see domain repository interfaces.

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
