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

High cohesion means elements inside a module belong together and serve a single, unified purpose. Low coupling means modules maintain minimal dependencies on each other, interacting through stable abstract contracts. Together, they isolate changes, prevent ripple effects across features, and optimize build caching.

## Interview answer — structured

Cohesion and coupling are the twin pillars of sustainable software architecture, applied directly at the Gradle module level:

1. **High Cohesion (Inside the Module)**: All components within a module change for the same business reason and serve a tightly focused domain responsibility. For example, `:feature:search` contains only query processing, search results UI, and recent searches storage. If a module contains auth helpers, date formatters, and payment models, it suffers from low cohesion and becomes an unmaintainable junk drawer.

2. **Low Coupling (Between Modules)**: Modules minimize their knowledge of and dependencies on other modules. Instead of depending on concrete implementations or peer feature modules, they interact across clean boundaries using dependency inversion and API contracts.

Architecturally, high cohesion ensures that when a feature changes, developers only modify files within that single module. Low coupling ensures that changes made inside that module never trigger unexpected regressions or recompilations in other modules.

## Interview answer — deep senior

A common architectural trap in Android modularization is **False Cohesion through Over-sharing**.

Teams often create a `:core:common` module containing utility extension functions, custom views, and network DTOs. Developers assume this is 'high reuse'. In reality, `:core:common` exhibits **extremely low cohesion and catastrophic high coupling**—every feature module imports it. When an engineer modifies a string utility in `:core:common`, the ABI change invalidates the build cache for 100% of the downstream feature modules.

To achieve true high cohesion and low coupling:
- Break `:core:common` into hyper-focused modules: `:core:model`, `:core:network`, `:core:ui`.
- Tolerate minor duplication of trivial helper functions (e.g., 2 lines of string formatting) rather than introducing a global shared dependency that couples otherwise independent features.

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
