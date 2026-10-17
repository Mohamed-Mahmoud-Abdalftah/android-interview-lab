---
id: "MOD-04"
question: "What is high cohesion and low coupling?"
topic: "Gradle Modularization & Dependency Boundaries"
code: "MOD"
group: "A"
phase: 4
priority: "P1"
order: 357
editorial_status: "reviewed"
---

# MOD-04

## Original interview question

What is high cohesion and low coupling?

## What the interviewer evaluates

- Define cohesion and coupling in terms of reasons to change.
- Apply the terms to module API and ownership rather than slogans.
- Admit trade-offs when extracting shared code.

## Concept and technical explanation

High cohesion and low coupling are fundamental software engineering principles that dictate the boundary design and health of modular systems:
- High Cohesion: Elements within a single module are strongly related in purpose, operate on a shared domain model, and change together for a unified business reason (following the Single Responsibility Principle at the module level). A cohesive module has a razor-sharp focus (e.g., :feature:authentication encapsulates only login, registration, and password recovery).
- Low Coupling: Modules maintain minimal, well-defined, and abstract surface areas with external modules. Changes to internal implementation details inside one module do not ripple into downstream consumers.
Violating these principles results in either a monolithic core module (low cohesion, high coupling) or fractured micro-modules that require distributed modifications across the codebase (shotgun surgery).

## Practical walkthrough (English)

Demonstrating high cohesion and low coupling via modular contract boundaries:
```kotlin
// ❌ LOW COHESION & HIGH COUPLING (:core:common dumps unrelated features)
// class CommonGodObject { fun formatCurrency(); fun openCamera(); fun parseJwt() }

// ✅ HIGH COHESION (:feature:scanner focuses strictly on barcode capture)
// feature/scanner/src/main/kotlin/BarcodeScannerManager.kt
class BarcodeScannerManager(private val cameraProvider: CameraProvider) {
    fun startScanning(onDetected: (String) -> Unit) { /* ... */ }
}

// ✅ LOW COUPLING (Consumer interacts via abstract interface, not camera internals)
interface ScannerContract {
    fun launchScanner(launcher: ActivityResultLauncher<Intent>)
}
```

## Explanation in Arabic

ما هو التماسك العالي (High Cohesion) والاقتران المنخفض (Low Coupling) في سياق معمارية موديولات Android؟

1. التماسك العالي (High Cohesion - الارتباط الوثيق داخلياً):
   - يعني أن جميع الكلاسات والدوال داخل الموديول الواحد تعمل معاً لخدمة **مسؤولية واحدة واضحة ومحددة (Single Cohesive Responsibility)**.
   - **مثال لموديول عالي التماسك**: `:core:network` يحتوي فقط على إعدادات الـ HttpClient، والـ Interceptors، والـ SSL Pinning، وإدارة الـ WebSockets. كل كود فيه يخدم الاتصال بالشبكة.
   - **مثال لموديول منخفض التماسك (Low Cohesion - كارثي)**: موديول يسمى `:core:utils` أو `:common` يحتوي على كود لتحميل الصور، وكود لحساب الضرائب، وكود لتنسيق التواريخ، ودوال للتعامل مع البلوتوث! الكلاسات داخله لا رابط منطقي بينها.

2. الاقتران المنخفض (Low Coupling - قلة الاعتمادية خارجياً):
   - يعني أن الموديول مستقل بذاته قدر الإمكان، ويعتمد على أقل عدد ممكن من الموديولات الخارجية، ويفصل تعاملاته عبر واجهات مجردة (Abstract Contracts).
   - إذا أردت تعديل أو إعادة كتابة كود موديول `:feature:auth`، يجب ألا يؤثر ذلك أو يتطلب أي تعديل في موديول `:feature:cart`.

3. القاعدة الهندسية:
   - **High Cohesion** يجعل الموديول سهل الفهم، والصيانة، والاختبار.
   - **Low Coupling** يجعل النظام مرناً، ويقلل من تسرب الأخطاء عند التعديل، ويسرع أوقات التجميع عبر تقليل تشابك شجرة التبعيات.

## Practical walkthrough

المقارنة بين تصميم منخفض التماسك ومقترن بشدة وتصميم متماسك عالي ومنخفض الاقتران:
```kotlin
// ❌ تصميم كارثي: Low Cohesion + High Coupling في موديول عشوائي (:core:common):
// يحتوي على كود ضرائب، وشاشات، وشبكة مخلطة في مكان واحد:
class CommonUtils {
    fun formatPrice(amount: Double): String = "$$amount"
    fun parseJwtToken(token: String): JwtClaims = ... // منطق أمان!
    fun calculateShipping(weight: Double, distance: Int): Double = ... // منطق مالي للشحن!
}
// أي موديول يستورد CommonUtils يرتبط تلقائياً بكل هذه التبعيات غير الضرورية!

// ✅ تصميم معماري راقٍ: High Cohesion + Low Coupling:
// 📁 في موديول :domain:pricing (High Cohesion: متخصص في التسعير فقط):
class PriceCalculator @Inject constructor(private val currencyFormatter: CurrencyFormatter) {
    fun calculateFinalTotal(items: List<CartItem>, taxRate: Double): Money = ...
}

// 📁 في موديول :core:auth (High Cohesion: متخصص في التحقق فقط):
class TokenParser @Inject constructor() {
    fun parse(rawToken: String): Result<AuthSession> = ...
}
// الموديولات لا تعتمد على بعضها إطلاقاً (Low Coupling)! كلاهما قابل لإعادة الاستخدام والاختبار في معزل.
```

## Why it matters and how it works

Modules with cohesive responsibilities have fewer unrelated internal reasons to change. Narrow public APIs reduce how much consumer code knows and must rebuild when internals evolve. Coupling is not zero—features must collaborate—but it should be intentional, directional and testable. A highly abstract API can itself create cognitive and maintenance cost.

## Worked example

Checkout contains cart validation, payment initiation UI and order confirmation coordination; catalog contains browsing and search. Both use a small `MoneyFormatter` or shared money value contract where semantically appropriate. If checkout imports catalog's internal Retrofit DTO merely to show a product name, they are coupled at the wrong boundary; pass a stable display or domain contract.

## Trade-offs and decision criteria

Sharing code prevents duplication but may force unrelated features into one dependency and release schedule. Duplicating a tiny UI helper can be cheaper than a premature common API. Cohesion can justify a larger feature module if all parts evolve together. Measure build fan-out and team ownership before extracting.

## Failure modes

A core module mixes payment rules, analytics UI and test helpers. A feature exposes every internal class as public. Two teams must coordinate for an internal change because their modules import each other's DTOs. A “decoupled” interface has one method per implementation detail and changes every sprint.

## Production perspective

Review module change history, API surface and dependency graph. Ask whether one product change touches one cohesive owner or several unrelated modules, and tighten boundaries where repeated cross-team edits occur.

## Interview answer — short

High cohesion means everything inside a module belongs together and serves a single focused purpose, changing for the same business reason. Low coupling means modules maintain minimal dependencies on each other and interact through stable, abstract interfaces. Together, they prevent cascading changes and ensure modules can evolve and compile independently.

## Interview answer — structured

High cohesion and low coupling represent the dual metrics of architectural quality in a multi-module system.
Cohesion measures how focused and unified the responsibilities are within a single module.
In a highly cohesive module, all classes, state models, and utilities work together toward a single business goal, such as user authentication or audio playback.
When business requirements for that capability change, edits remain localized within that specific module.
Coupling, on the other hand, measures the degree of interdependence between different modules.
Low coupling ensures that a module exposes only a minimal, stable public interface while hiding its internal implementation details.
Consumers depend on abstract contracts rather than concrete implementation classes.
If high cohesion is ignored, modules become chaotic dumping grounds for unrelated code.
If low coupling is ignored, a change in one module triggers cascading compilation failures and bugs across the entire application.

## Interview answer — deep senior

In enterprise Android system design, high cohesion and low coupling govern how we partition bounded contexts into Gradle subprojects.
Cohesion reflects the Single Responsibility Principle elevated to the architectural level: a module should have one, and only one, reason to change.
A feature module like :feature:checkout exhibits high cohesion when its payment form, cart review, and shipping address flows operate around a coherent checkout domain model.
Conversely, dumping payment utilities, image loaders, and date formatters into a single :core:common module destroys cohesion, creating a disguised monolith where unrelated feature teams constantly conflict over shared files.
Coupling dictates the blast radius of change across the dependency graph.
When modules are tightly coupled, modifying an internal database query or refactoring a ViewModel forces downstream consumers to modify their call sites, breaking the Gradle build cache and triggering full recompilations.
We enforce low coupling by applying the Dependency Inversion Principle and separating features into public :api and private :impl modules.
The :api module contains only lightweight interfaces and immutable data transfer objects, while :impl holds internal logic hidden behind Kotlin's internal visibility modifier.
Downstream features import solely the :api module.
This design guarantees that implementation refactors remain strictly contained within their private module boundaries, preserving build cache hits and decoupling feature release lifecycles.

## How to answer in the interview

- **Why:** change should stay near its owner.
- **How:** group related behavior and narrow imports.
- **Trade-off:** local cohesion versus duplicate utilities.
- **Failure case:** giant core becomes shared bottleneck.
- **Production solution:** measure affected modules per change.

## Deep-dive talking points

Discuss reasons to change, public API size, semantic reuse, fan-out, duplication, and ownership history.

## Follow-up questions

- **Interviewer:** "Is zero coupling achievable between two features?"
  **Answer:** "Yes, at compile time! Feature A and Feature B can communicate via deep link navigation URLs or event buses registered in the :app module without any compile-time dependency between them."

- **Interviewer:** "What is the danger of prioritizing DRY (Don't Repeat Yourself) over Low Coupling?"
  **Answer:** "Coupling unrelated modules to share a 3-line utility creates tight build and architectural coupling that costs far more in maintenance and build time than harmless code duplication."

## Self-check rubric

Define both terms, diagnose one boundary violation, and weigh sharing versus duplication.

## References and reviewed-on date

- [Android modularization guide](https://developer.android.com/topic/modularization) — encapsulation and ownership.
- [Common modularization patterns](https://developer.android.com/topic/modularization/patterns) — practical boundaries.

Technically reviewed against primary documentation on 2026-10-13.
