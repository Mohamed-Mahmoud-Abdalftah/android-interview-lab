---
id: "MOD-19"
question: "Two feature teams need the same business logic. Where should it live?"
topic: "Gradle Modularization & Dependency Boundaries"
code: "MOD"
group: "C"
phase: 4
priority: "P1"
order: 372
editorial_status: "reviewed"
---

# MOD-19

## Original interview question

Two feature teams need the same business logic. Where should it live?

## What the interviewer evaluates

- Identify one authoritative business-rule owner.
- Separate stable shared policy from UI convenience code.
- Account for versioning, tests and cross-team governance.

## Concept and technical explanation

When two autonomous feature teams require identical business logic, resolving where that logic should live is a fundamental architectural dilemma with distinct trade-offs:
- Anti-Patterns to Avoid:
  1. Direct Feature Coupling: Having Feature B import Feature A breaks horizontal layer isolation, risks circular dependency loops, and compromises team release autonomy.
  2. The Common Garbage Dump: Shoving the logic into :core:common destroys cohesion and turns core into an uncontrolled monolith that invalidates the build cache project-wide.
- Architectural Solutions:
  1. Extract a Focused Shared Domain Module: If the capability represents a genuine, cohesive enterprise business concept (e.g., loan tax calculations, currency conversions), extract it into a leaf domain module: :domain:taxation or :core:domain:currency.
  2. API/Impl Feature Extraction: If one squad legitimately owns the domain (e.g., Identity squad owns biometric verification), they expose a contract in :feature:identity:api and house the logic in :feature:identity:impl for other features to consume.
  3. Controlled Code Duplication (AHA Programming): If the logic superficially appears similar but belongs to distinct bounded contexts with divergent lifecycles, duplicate the code rather than introducing premature, tightly coupled abstractions.

## Practical walkthrough (English)

Extracting shared business logic into an isolated leaf domain module:
```kotlin
// ❌ WRONG: :feature:cart imports :feature:checkout (Horizontal coupling!)
// ❌ WRONG: Logic dumped in :core:common (Cohesion destroyed!)

// ✅ CORRECT: Extract focused leaf domain module :domain:pricing
// domain/pricing/src/main/kotlin/CalculateDiscountUseCase.kt
class CalculateDiscountUseCase @Inject constructor() {
    operator fun invoke(cartTotal: BigDecimal, couponCode: String?): BigDecimal {
        // Pure Kotlin business calculation, zero Android dependencies
        return if (couponCode == "VIP") cartTotal.multiply(BigDecimal("0.80")) else cartTotal
    }
}

// Both :feature:cart and :feature:checkout depend on :domain:pricing
// Maintains clean DAG and enables sub-second JVM unit testing!
```

## Explanation in Arabic

فريقان لميزتين مختلفتين (Feature Teams) يحتاجان إلى نفس منطق الأعمال (Same Business Logic). أين يجب أن يعيش هذا المنطق معمارياً؟

1. الحلول الخاطئة الشائعة:
   - **الخطأ الأول**: جعل موديول Feature A يعتمد على موديول Feature B (`:feature:cart -> :feature:catalog`). هذا يكسر العزل، ويخلق اقتراناً شديداً، وقد يسبب تبعية دائرية مستحيلة.
   - **الخطأ الثاني**: رمي الكود في موديول عشوائي `:core:common` أو `:core:utils`، مما يجعله مزبلة للمنطق التجاري غير المترابط.

2. الحل المعماري النظيف (Single Authoritative Owner in Domain Layer):
   - **إنشاء موديول Domain مخصص**: استخراج منطق الأعمال إلى موديول نقي في طبقة الـ Domain، مثل `:domain:pricing` أو `:domain:tax`.
   - يحتوي هذا الموديول على الكيان النقي (Entity)، وقواعد الحساب، و UseCase محدد (مثل `CalculateOrderDiscountUseCase`).
   - **يعتمد كلا الفريقين على موديول الـ Domain للأسفل**: يعتمد كل من `:feature:cart` و `:feature:checkout` على `:domain:pricing`.
   - **وضوح الملكية (Code Ownership)**: يتم تعيين فريق محدد كمالك للموديول في ملف `CODEOWNERS` لضمان عدم إجراء أي تعديل دون مراجعة وتدقيق معتمدين.

## Practical walkthrough

استخراج منطق أعمال مشترك إلى موديول Domain مستقل:
```text
❌ قبل: اقتران غير مسموح بين موديولين ميزات:
:feature:cart ─────(illegal direct dependency)─────► :feature:catalog

✅ بعد: استخراج المنطق المشترك إلى موديول Domain مستقل يملكه مالك محدد:
      :feature:cart                   :feature:checkout
            │                                │
            │ (depends on)                   │ (depends on)
            ▼                                ▼
      ┌──────────────────────────────────────────────┐
      │             :domain:pricing                  │
      │ (DiscountCalculator, TaxPolicy, PricingRules)│
      └──────────────────────────────────────────────┘

// في :domain:pricing (Pure Kotlin JVM):
class CalculatePromotionalDiscountUseCase @Inject constructor() {
    fun execute(items: List<CartItem>, promoCode: String?): DiscountResult = ...
}
// كلا الفريقين يستوردان هذا الـ UseCase بأمان واستقرار تام!
```

## Why it matters and how it works

A shared business rule needs consistent decisions across user flows. A stable domain contract lets both features depend in one direction on an owned policy. Changes to shared logic then fan out deliberately, which is appropriate for correctness even if it adds coordination. Similar-looking code is not always the same rule; premature extraction can force unrelated teams into one release cycle.

## Worked example

Cart and Checkout both display discount eligibility. A `DiscountPolicy.evaluate(cart, customer)` use case owns the calculation and returns a reasoned result; both features render it differently. Tests cover boundaries, expired offers and currency precision. A change to policy updates one implementation and both UI integration tests, rather than letting Cart show a discount Checkout later rejects.

## Trade-offs and decision criteria

Central policy avoids drift but its public API and release process need an owner. Duplicating small presentation formatting may be fine; duplicating financial rules is risky. A remote backend may be authoritative for final eligibility, with local policy only a preview, so the contract should state that distinction.

## Failure modes

Each team copies the formula and rounding differs. A shared module takes direct dependencies on both feature UIs. A policy API returns screen-specific models. Local eligibility is treated as final even though the server can reject it. A common module grows many feature flags rather than stable concepts.

## Production perspective

Assign codeowners and versioned contract review, build a boundary test matrix, and compare app/server results where backend authority applies. Monitor disagreements as product defects, not merely UI inconsistencies.

## Interview answer — short

When two feature teams need the same business logic, never create a direct feature-to-feature dependency or dump it into core:common. Extract the logic into a focused, single-responsibility leaf domain module, or have the owning feature expose an api module. If the logic belongs to separate bounded contexts with different reasons to change, prefer controlled duplication over premature coupling.

## Interview answer — structured

Deciding where shared business logic should live requires balancing code reuse against architectural coupling.
We strictly avoid two common anti-patterns: allowing one feature module to import another directly, or dumping the logic into a monolithic core:common module.
Instead, we apply three structured options.
If the logic represents a distinct enterprise rule like currency exchange or tax calculation, we extract a dedicated leaf domain module like domain:pricing.
Both feature modules import this pure Kotlin module, preserving an acyclic dependency graph and enabling instantaneous JVM testing.
If one squad clearly owns the capability, such as identity verification, that team exposes an interface in an api module while retaining the implementation.
Finally, if the logic only appears similar coincidentally but belongs to different business domains with independent reasons to change, senior architects prefer controlled code duplication rather than coupling the teams with a premature shared abstraction.

## Interview answer — deep senior

In enterprise mobile architecture, sharing code across team boundaries is primarily an organizational governance decision rather than a simple refactoring exercise.
Engineers frequently suffer from dogmatic DRY (Don't Repeat Yourself) obsession, creating premature abstractions that tightly couple autonomous feature teams.
When two feature teams require shared business logic, we evaluate ownership, volatility, and domain alignment across three clear tiers.
First, if the capability represents an authentic, shared business policy—such as credit risk scoring or tax withholding calculations—we extract a dedicated, leaf-level pure Kotlin domain module, such as :domain:finance:tax.
Because this module has zero dependencies on Android frameworks, UI widgets, or sibling features, it compiles in milliseconds and can be unit-tested thoroughly on the JVM.
Both features declare an implementation dependency on this shared domain module, preserving a clean Directed Acyclic Graph.
Second, if the capability is a service owned by a specific squad—such as user identity verification—that team hosts the logic in its :feature:identity:impl module and publishes a clean interface in :feature:identity:api.
Other teams depend strictly on the :api contract, wiring the implementation via Hilt.
Third, we actively evaluate the AHA (Avoid Hasty Abstractions) principle.
If the shared logic is simply a five-line data transformation that happens to look identical today but serves different product goals—such as order sorting versus search result sorting—we intentionally allow controlled code duplication.
Duplicating a few lines of code is vastly cheaper than introducing an artificial shared module that requires cross-team synchronization and consensus for every future modification.

## How to answer in the interview

- **Why:** shared rules need stable ownership.
- **How:** extract true invariant, keep superficial duplication.
- **Trade-off:** reuse versus forced coupling.
- **Failure case:** one feature changes shared helper and breaks other.
- **Production solution:** contract tests and ownership.

## Deep-dive talking points

Discuss semantic sharing, one policy owner, backend authority, API governance and integration tests.

## Follow-up questions

- **Interviewer:** "What happens if a shared domain module requires network data?"
  **Answer:** "The domain module declares an abstract repository interface; the corresponding `:data:*` module implements it and handles networking."

- **Interviewer:** "Should shared business logic include UI formatting strings?"
  **Answer:** "No. Business logic returns raw domain types (e.g. `Money(amount = 12.50, currency = USD)`); UI formatting belongs in presentation layers."

## Self-check rubric

Identify the invariant, owner and authority, then test rule boundaries and feature integration.

## References and reviewed-on date

- [Android modularization guide](https://developer.android.com/topic/modularization) — reusable modules.
- [Domain layer guidance](https://developer.android.com/topic/architecture/domain-layer) — shared business logic.

Technically reviewed against primary documentation on 2026-10-13.
