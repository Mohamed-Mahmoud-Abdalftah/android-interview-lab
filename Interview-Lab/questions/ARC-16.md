---
id: "ARC-16"
question: "Compare package-by-layer and package-by-feature."
topic: "Clean Architecture, MVVM, MVI & UDF"
code: "ARC"
group: "B"
phase: 2
priority: "P1"
order: 161
editorial_status: "reviewed"
---

# ARC-16

## Original interview question

Compare package-by-layer and package-by-feature.

## What the interviewer evaluates

Compare navigation, cohesion, ownership and Gradle module implications of two packaging strategies.

## Concept and technical explanation

Code organization strategy governs codebase discoverability, coupling boundaries, and scalability. Package-by-layer groups code according to technical roles (e.g. presentation/, domain/, data/, adapters/), pooling all ViewModels, Repositories, and DAOs together. Package-by-feature organizes code into functional user-facing business verticals (e.g. feature/auth/, feature/checkout/, feature/profile/), where each package contains its own UI components, ViewModels, Use Cases, and internal models. While package-by-layer is common in tiny tutorials, it causes low cohesion, tight cross-layer coupling, high merge conflicts, and blocks modularization in enterprise teams. Package-by-feature delivers high cohesion, strict encapsulation, independent team ownership, and directly mirrors multi-module Gradle architectures.

## Practical walkthrough (English)

Contrasting Package-by-layer with Package-by-feature:
```text
// ❌ PACKAGE-BY-LAYER: Low cohesion, cross-cutting sprawl
com.example.app/
├── presentation/
│   ├── LoginFragment.kt, CheckoutFragment.kt, ProfileFragment.kt
│   └── LoginViewModel.kt, CheckoutViewModel.kt, ProfileViewModel.kt
├── domain/
│   └── LoginUseCase.kt, CheckoutUseCase.kt
└── data/
    └── UserRepository.kt, OrderRepository.kt

// ✅ PACKAGE-BY-FEATURE: High cohesion, natural Gradle module boundaries
com.example.app/
├── feature/auth/
│   ├── LoginScreen.kt, LoginViewModel.kt, AuthRepository.kt
├── feature/checkout/
│   ├── CheckoutScreen.kt, CheckoutViewModel.kt, CheckoutUseCase.kt
└── core/database/ (shared foundational infrastructure)
```

## Explanation in Arabic

المقارنة الهيكلية بين تنظيم الحزم حسب الطبقة (Package-by-Layer) وحسب الميزة (Package-by-Feature):

1. تنظيم الحزم حسب الطبقة (Package-by-Layer):
   - تقسيم الكود أفقياً بناءً على نوع المكون البرمجي:
     `com.example.app/`
       `├── presentation/` (كل الـ Activities, Composables, ViewModels)
       `├── domain/` (كل الـ UseCases, Entities)
       `├── data/` (كل الـ Repositories, DAOs, DTOs)
   - **المشكلة الكبرى**: مع نمو التطبيق (أكثر من 30 شاشة)، يصبح كل مجلد متضخماً بمئات الملفات غير المرتبطة ببعضها. كما أن التعديل في ميزة واحدة (مثل الدفع Payment) يجبرك على القفز بين 4 مجلدات مختلفة في أطراف المشروع!

2. تنظيم الحزم حسب الميزة (Package-by-Feature):
   - تقسيم الكود عمودياً بناءً على مجالات العمل وميزات المستخدم:
     `com.example.app/`
       `├── checkout/` (ViewModel, UI, UseCases, Repositories الخاصة بالـ Checkout)
       `├── auth/` (كل ما يخص تسجيل الدخول)
       `├── catalog/` (كل ما يخص تصفح المنتجات)
   - **المزايا الخارقة**: التماسك العالي (High Cohesion)، سهولة العثور على الملفات، واستخدام الـ Visibility Modifiers (`internal` في كوتلن) لحماية الكود الداخلي للميزة.

3. المعمارية الهجينة الحديثة في أندرويد (Feature Modules with Layers):
   - التطبيقات الكبرى تنظم الكود أولاً **حسب الميزة** (Modules per Feature)، وداخل كل ميزة يتم تنظيم الكود داخلياً **حسب الطبقات** (`presentation`, `domain`, `data`).

## Practical walkthrough

مقارنة هيكل المجلدات بين النمطين في مشروع حقيقي:
```text
// ❌ Package-by-Layer (ضعيف التماسك وصعب الصيانة في المشاريع الكبيرة):
com.example.app/
├── ui/
│   ├── LoginScreen.kt, HomeScreen.kt, CheckoutScreen.kt, ProfileScreen.kt...
├── viewmodel/
│   ├── LoginViewModel.kt, HomeViewModel.kt, CheckoutViewModel.kt...
├── repository/
│   ├── AuthRepository.kt, CartRepository.kt, ProfileRepository.kt...

// ✅ Package-by-Feature (عالي التماسك وسهل التوزيع والتحويل لـ Modules):
com.example.app/
├── auth/
│   ├── LoginScreen.kt
│   ├── LoginViewModel.kt
│   ├── AuthRepository.kt
│   └── AuthModels.kt
├── checkout/
│   ├── CheckoutScreen.kt
│   ├── CheckoutViewModel.kt
│   └── CartRepository.kt
└── core/
    ├── database/
    └── network/
```

## Why it matters and how it works

Packaging improves discoverability and team ownership; modules can enforce dependency direction. Choose the shape that minimizes changes scattered across unrelated areas while preserving shared contracts.

## Worked example

Conceptual tree: `feature/checkout/{ui,data}` and `feature/profile/{ui,data}` with `core/model` for genuinely shared types. Compare with root `ui/checkout`, `data/checkout`, `domain/checkout`; both can work, but feature grouping keeps vertical work local.

## Trade-offs and decision criteria

Feature packages improve cohesion but can duplicate helpers until a real shared abstraction emerges. Layer packages make cross-cutting concerns visible but may scatter one feature. Do not split every package into a Gradle module without build/ownership benefit.

## Failure modes

A team creates `common/Utils.kt` used by all features, introducing hidden coupling and a huge rebuild hotspot. Another mistake is assuming package names stop UI from importing Room; enforce with modules or architecture checks.

## Production perspective

A marketplace organizes checkout, search and account by feature; shared payment domain contracts live in a small core module. Dependency checks prevent checkout UI from importing another feature’s data implementation.

## Interview answer — short

Package-by-layer groups code by technical function (all ViewModels together, all Repositories together), causing low cohesion and tight coupling. Package-by-feature groups code by business verticals (authentication, checkout), maximizing cohesion, reducing cross-feature merge conflicts, and serving as the direct stepping stone to multi-module Gradle architectures.

## Interview answer — structured

Package organization directly impacts codebase scalability, developer velocity, and architectural modularity.

Package-by-layer groups classes according to technical categories: all activities in one package, all viewmodels in another, and all repositories in a third. This creates low cohesion because working on a single feature like user authentication requires navigating across four distinct root packages, making deletion or refactoring cumbersome.

In production, package-by-feature groups all components belonging to a specific user journey—such as checkout, onboarding, or search—into a dedicated package. Each feature contains its own Composables, ViewModels, and private helpers, keeping related code tightly localized.
As for enterprise growth, package-by-feature maps seamlessly to multi-module Gradle architectures. Teams can easily extract feature modules into isolated Gradle modules, enabling parallel compilation, fine-grained access control, and independent feature team ownership without cross-team merge conflicts.


## Interview answer — deep senior

Under the hood, the choice between package-by-layer and package-by-feature determines how cleanly code can be decoupled and compiled. In package-by-layer, classes within the same technical package have little semantic relationship—a CheckoutViewModel and an AuthViewModel share nothing except that they both extend the Android Jetpack ViewModel base class. Because dependencies crisscross horizontally between layers, developers easily introduce unintended circular couplings, and deleting a deprecated feature requires hunting down files across every layer folder.
Package-by-feature adheres to the Common Closure Principle: classes that change together should be packaged together. When modifying the checkout user experience, all relevant Composables, ViewModels, and state models reside in the same directory. Features can mark internal helpers with Kotlin's internal visibility modifier, protecting private implementation details from being accidentally imported by unrelated features.
In modern Android enterprise development, this structure directly mirrors the modularization strategy recommended by Google. Core shared functionality lives in core network, core database, and core designsystem, while feature verticals are packaged independently as feature cart, feature payments, and feature settings.
Staff engineers ensure that feature packages never depend on peer feature packages directly. Any cross-feature communication is handled via navigation deep links or core API interfaces, allowing Gradle to build feature modules in parallel and drastically reducing CI build times across large engineering departments.

## How to answer in the interview

- **Why:** structure should match change ownership.
- **How:** group by feature with explicit shared contracts.
- **Trade-off:** discoverability versus duplication.
- **Failure case:** packages move but dependencies still circular.
- **Production solution:** module boundaries and dependency checks.

## Deep-dive talking points

Draw a feature tree and layer tree for checkout; identify where module rules differ from mere packages.

## Follow-up questions

- **Interviewer:** "Where should shared cross-cutting code live in a package-by-feature setup?"
  **Answer:** "In dedicated foundation modules or packages prefixed with `core/` (e.g. `core/network`, `core/database`, `core/ui`), consumed by feature packages."

- **Interviewer:** "How does package-by-feature improve PR review velocity?"
  **Answer:** "Reviewers can review changes localized to a single directory rather than diffs scattered across presentation, domain, and data layers, speeding up comprehension and reducing merge conflicts."

## Self-check rubric

Explain one benefit and cost of each layout, plus one mechanism that enforces dependency direction.

## References and reviewed-on date

- [Android modularization guide](https://developer.android.com/topic/modularization) — module organization and trade-offs.
- [Android architecture guide](https://developer.android.com/topic/architecture) — layer concerns.

Technically reviewed against primary documentation on 2026-10-13.
