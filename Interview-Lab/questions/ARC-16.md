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

Package-by-layer groups files by technical role (all ViewModels together, all Repositories together), causing scattered feature code and low cohesion. Package-by-feature groups files by business capability (all auth code together, all cart code together), providing high cohesion, encapsulation, and an easy path to Gradle modularization.

## Interview answer — structured

Packaging strategy determines cognitive load, code navigation speed, and modularization readiness in growing codebases.

1. **Package-by-Layer (Horizontal Partitioning)**:
   - Groups files strictly by their technical classification (`presentation`, `domain`, `data`).
   - *Drawbacks*: As the app grows beyond a few screens, packages balloon to hundreds of files. Feature cohesion is completely lost: developing a single feature requires jumping across multiple directories. Everything must be marked `public`, destroying encapsulation.

2. **Package-by-Feature (Vertical Partitioning)**:
   - Groups all artifacts required for a specific business capability into a single cohesive package (`auth`, `checkout`, `profile`).
   - *Benefits*: High cohesion. Deleting or modifying a feature touches files in a single self-contained directory. Allows leveraging Kotlin's `internal` visibility to hide feature-internal implementation details.

3. **Modern Hybrid Standard**:
   - In enterprise Android architecture, we package **by feature at the macro level** (often as separate Gradle modules), and **by layer at the micro level** within that feature (`:feature:checkout/ui`, `.../domain`, `.../data`).

## Interview answer — deep senior

The major architectural triumph of package-by-feature is enabling painless **Multi-Module Migration**. A project structured by layer is nearly impossible to modularize because circular dependencies between packages are rampant across features. In contrast, a project structured by feature can extract `auth/` or `checkout/` directly into an independent Gradle module `:feature:auth` within hours.

Encapsulation is another vital advantage. Under package-by-layer, a repository implementation class in `data` must be declared `public` so a use case in `domain` or a ViewModel in `ui` can access it. Under package-by-feature in separate modules, concrete implementation classes can be marked `internal`, exposing only a clean public interface or entry point.

Shared infrastructure (Network clients, Database drivers, Common UI Design Tokens) lives in dedicated core packages (`core:network`, `core:database`, `core:designsystem`).

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
