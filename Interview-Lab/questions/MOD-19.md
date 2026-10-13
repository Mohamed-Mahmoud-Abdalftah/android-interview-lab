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

When two feature teams share business logic, never couple the features directly or dump code into :core:common. Extract the logic into a focused, single-responsibility domain module (e.g. :domain:pricing) containing pure Use Cases and business rules, with clear CODEOWNERS governance.

## Interview answer — structured

When two feature teams require identical business logic, resolving placement demands strict architectural governance:

1. **Never Create Feature-to-Feature Dependencies**: Permitting `:feature:cart` to depend on `:feature:checkout` violates the fundamental acyclic boundary rule and entangles two distinct user journeys.

2. **Extract to a Focused Domain Module**: Create a dedicated JVM module representing the specific business capability: e.g. `:domain:pricing` or `:domain:identity`. This module houses pure Kotlin business entities, invariants, and Use Cases (`CalculateTaxUseCase`). Both feature modules depend downward on this domain module.

3. **Establish Clear Code Ownership**: Designate a single team as the primary owner in `CODEOWNERS` (e.g. Payments team owns `:domain:pricing`). If the other team needs enhancements, they submit pull requests subject to the owning team's review and automated test suites.

## Interview answer — deep senior

Before extracting shared business logic into a common module, senior engineers evaluate **Semantic Equivalence vs. Accidental Coincidence**.

Often, two features appear to need the 'same' logic, but their underlying domain invariants are actually diverging. For example, calculating price in a product catalog may tolerate cached approximate tax estimations, whereas calculating price in final checkout requires strict real-time fiscal compliance.

If you force divergent requirements into a single shared function with boolean flags (`calculatePrice(isCheckout: Boolean)`), you introduce toxic coupling. If the business rules have fundamentally different lifecycles or reasons to change, it is better to maintain separate use cases. Only extract shared code when the underlying business invariant is mathematically or legally identical.

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
