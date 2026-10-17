---
id: "SOL-19"
question: "When should you deliberately accept a little duplication instead of introducing an abstraction?"
topic: "SOLID & Object-Oriented Design"
code: "SOL"
group: "C"
phase: 2
priority: "P1"
order: 190
editorial_status: "reviewed"
---

# SOL-19

## Original interview question

When should you deliberately accept a little duplication instead of introducing an abstraction?

## What the interviewer evaluates

Choose small duplication over premature shared abstraction when concepts only look alike.

## Concept and technical explanation

Deliberately accepting a little duplication instead of introducing a premature abstraction is a hallmark of mature software engineering, famously articulated by Sandi Metz: 'Duplication is far cheaper than the wrong abstraction.' While the Don't Repeat Yourself (DRY) principle cautions against duplicate knowledge, superficial code similarity frequently represents accidental duplication rather than shared domain concepts. In Android development, when two features exhibit similar UI layouts or data structures but evolve under different business stakeholders or change velocities, forcing them into a shared base class or generic abstraction couples their lifecycles, causing architectural rigidity and regression cascades.

## Practical walkthrough (English)

Contrasting the wrong abstraction against pragmatic, independent duplication:
```kotlin
// BAD ANTI-PATTERN: The Wrong Abstraction! (Forcing Auth and Checkout into a bloated shared form model)
open class GenericInputFormModel(
    val email: String,
    val isTermsAccepted: Boolean,
    val promoCode: String? = null, // Leaked from Checkout into Auth!
    val isSocialLogin: Boolean = false // Leaked from Auth into Checkout!
)

// ARCHITECTURAL BEST PRACTICE: Independent, cohesive models with accidental duplication
// 1. Auth Feature Model (Owned strictly by Auth Team / Login Stakeholders)
data class LoginCredentials(
    val email: String,
    val passwordHash: String
)

// 2. Checkout Feature Model (Owned strictly by Commerce Team / Billing Stakeholders)
data class CheckoutCustomerInfo(
    val email: String,
    val shippingAddress: String,
    val promotionalCode: String?
)
// Although both have 'email', their business reasons to change are 100% disconnected!
// Preserving independent models prevents cross-feature coupling!
```

## Explanation in Arabic

متى يجب عليك قبول قليل من التكرار (Duplication) عمداً بدلاً من التسرع في بناء تجريد غير ناضج (Premature Abstraction)؟

1. حكمة ساندي ميتز الشهيرة (Sandi Metz's Law):
   - **"التكرار المؤقت أرخص بكثير من التجريد الخاطئ (Duplication is far cheaper than the wrong abstraction)"**.
   - التسرع في دمج كودين يتشابهان شكلياً في كلاس تجريدي واحد (DRY Dogmatism) يؤدي إلى كوارث معمارية عندما يبدأ الكودان في التطور باتجاهات مختلفة.

2. التكرار العرضي (Accidental Duplication) مقابل التكرار الحقيقي (True Duplication):
   - **التكرار الحقيقي (True Duplication)**: كودان يمثلان نفس قاعدة البيزنس الحقيقية ويخدمان نفس الهدف (مثل دالة حساب ضريبة القيمة المضافة لطلبات الشراء)؛ هنا يجب توحيدهما فوراً.
   - **التكرار العرضي (Accidental Duplication)**: شاشتان (شاشة المنتجات وشاشة المستخدمين) تحتوي كل منهما على دالة لعرض بطاقة مستطيلة بداخلها صورة ونص؛ هذا مجرد تشابه بصري عارض (Accidental similarity) وليس بيزنس موحد! إذا قمت بدمجهما في كائن تجريدي واحد، فبمجرد أن يطلب مصمم الـ UI تعديل شاشة المستخدم، ستضطر لوضع شروط `if (isUser)` داخل التجريد، حتى يتحول إلى وحش مليء بالاستثناءات!

3. متى تقبل التكرار عمداً؟
   - في بداية بناء ميزة جديدة قبل وضوح اتجاه تطورها.
   - بين موديولات الـ Feature المستقلة لحمايتها من الاقتران غير المبرر (Loose Coupling between modules).
   - حتى تطبق قاعدة الثلاثة (Rule of Three): لا تجرد إلا عندما ترى التكرار لثالث مرة بوضوح تام.

## Practical walkthrough

المقارنة بين التجريد الخاطئ وقبول التكرار العرضي لسلامة الكود:
```kotlin
// ❌ تجريد خاطئ كارثي: دمج كارتين مختلفين في تجريد واحد بسبب تشابه عارض:
// شاشة الكتالوج وشاشة البروفايل كانتا متشابهتين، فقام المطور بدمجهما:
@Composable
fun FrankensteinGenericCard(item: Any, isUser: Boolean, showBadge: Boolean) {
    // 💥 كود مليء بشروط if/else ومقترن بكيانين لا علاقة لهما ببعض!
    if (isUser) UserSpecificLayout(item as User) else ProductLayout(item as Product)
}

// ✅ قبول قليل من التكرار العرضي للحفاظ على الاستقلالية التامة والتطور النظيف:
@Composable
fun ProductCard(product: Product) {
    // كارت منتج مستقل يتطور مع متطلبات التجارة الإلكترونية
    Text(product.name)
}

@Composable
fun UserAvatarCard(user: User) {
    // كارت بروفايل مستقل يتطور مع متطلبات الحسابات دون المساس بالمنتجات
    Text(user.displayName)
}
```

## Why it matters and how it works

A premature abstraction can couple independent changes and create configuration flags. Duplication has a visible local cost; a wrong shared model can make every change harder. Extract when the common behavior and invariant are proven.

## Worked example

Example: checkout address validation requires a verified billing postcode, while profile address edit permits an optional postcode. A shared `validateAddress(isCheckout: Boolean)` may grow flags. Two small validators can remain separate until a stable common primitive emerges.

## Trade-offs and decision criteria

Duplication risks drift and repeated bug fixes. A genuine shared policy should be centralized. Accept modest duplication only when the variation is unclear or change reasons differ; revisit with evidence.

## Failure modes

A “generic” form engine gains ten Boolean switches and a reflection registry, making a simple new field require edits in every feature. Unwind to explicit feature rules and extract only shared invariant pieces.

## Production perspective

A team allows two small UI mappers for different screens while sharing one authoritative tax calculation policy. They track divergent bugs and extract common behavior when stable.

## Interview answer — short

You should deliberately accept duplication when the similarity is accidental rather than conceptual, or when the requirements are still rapidly evolving. In Android, feature modules frequently have similar UI models or validation checks that serve different business actors. Forcing them into a premature shared abstraction creates tight coupling and makes future changes painful. As Sandi Metz observed, duplication is far cheaper than the wrong abstraction; wait until true domain commonality stabilizes.

## Interview answer — structured

Choosing pragmatic duplication over premature abstraction is an essential judgment call that separates dogmatic coders from senior architects.
The DRY (Don't Repeat Yourself) principle is frequently misinterpreted as an absolute ban on duplicate lines of code. However, DRY is fundamentally about avoiding the duplication of business knowledge and authority, not syntactic similarity.
There are three clear scenarios where accepting duplication is the superior architectural decision.
First, when code similarity is accidental rather than essential. If an e-commerce checkout screen and a user profile registration screen both collect an address and an email, their technical data structures look identical. However, marketing may change profile registration rules while payment gateways alter billing address rules. Coupling them to a single shared AddressModel forces one feature to inherit breaking changes meant for another.
Second, during early feature discovery and rapid prototyping. When requirements are fluid, the cost of guessing the wrong abstraction and continually adding boolean flags to accommodate edge cases is astronomically higher than maintaining two separate 20-line classes.
Third, across Gradle module boundaries. Forcing two independent feature modules to share a common utility module just for a minor helper function introduces unnecessary compilation coupling, slowing down builds.

## Interview answer — deep senior

Under the hood, the wrong abstraction is an architectural debt multiplier that actively dismantles modularity and increases cognitive load.
When developers prematurely merge two similar code paths into a shared class or generic UseCase, they create an artificial coupling point. As the two features inevitably diverge, the shared abstraction cannot adapt cleanly. Developers begin introducing conditional flags, nullable parameters, and boolean mode switches (like isCheckoutMode or skipValidation). The shared class mutates into a brittle state machine violating both SRP and OCP.
In multi-module Android architectures, premature abstractions create toxic dependency graphs. If :feature:auth and :feature:cart share a bloated :core:user-form model, both modules must recompile whenever either team modifies the form.
By deliberately accepting isolated duplication—allowing each feature module to define its own local DTO or UI state representation—modules compile in parallel without shared state locks.
Furthermore, memory locality and ART runtime optimizations favor simple, monomorphic concrete classes over heavily genericized, polymorphic wrapper abstractions that allocate boxed objects and trigger additional virtual method lookups.
Staff engineers follow the Rule of Three: tolerate duplication once, tolerate it twice, but when you encounter the exact same structural pattern a third time with identical change drivers, only then synthesize a deliberate, battle-tested abstraction. This disciplined restraint maintains rapid iteration cycles.

## How to answer in the interview

- **Why:** Use address-policy divergence.
- **How:** explain extraction trigger.
- **Trade-offs:** acknowledge drift cost.
- **Failure cases:** flag boolean-flag abstraction.
- **Production solutions:** finish with separate tests and review threshold..

## Deep-dive talking points

Compare syntactic duplication with semantic duplication; diagnose mode-flag growth and extraction timing.

## Follow-up questions

- **Interviewer:** "What is the difference between Accidental Duplication and Essential Duplication?"
  **Answer:** "Essential duplication occurs when multiple places implement the exact same business rule (e.g. tax formula) that must change together. Accidental duplication occurs when two components have similar syntax or layout purely by coincidence."

- **Interviewer:** "How does accepting slight duplication help multi-module compile times?"
  **Answer:** "It avoids creating unnecessary shared modules. When feature modules share no unnecessary common dependencies, Gradle can compile and test them concurrently in parallel."

## Self-check rubric

Give an example of safe temporary duplication and one shared policy that must be centralized.

## References and reviewed-on date

- [Android domain layer](https://developer.android.com/topic/architecture/domain-layer) — extracting reusable business logic when justified.
- [Robert C. Martin, SRP](https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html) — change reasons.
- [Robert C. Martin, OCP](https://blog.cleancoder.com/uncle-bob/2014/05/12/TheOpenClosedPrinciple.html) — strategic extension.

Technically reviewed against primary documentation on 2026-10-13.
