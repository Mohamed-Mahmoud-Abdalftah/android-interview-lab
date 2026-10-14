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

Deliberately accept slight duplication when code looks syntactically similar but represents distinct business concepts evolving for different actors (accidental duplication), or across feature module boundaries to avoid tight coupling. Sandi Metz's rule applies: 'Duplication is far cheaper than the wrong abstraction.'

## Interview answer — structured

Software engineering maturity is recognizing that **premature abstraction is far more dangerous than temporary duplication**.

As phrased by Sandi Metz: *'Duplication is far cheaper than the wrong abstraction.'* When engineers dogmatically enforce DRY (Don't Repeat Yourself) at the syntax level, they frequently merge two pieces of code that look identical today but evolve for completely different reasons tomorrow.

**When to Deliberately Accept Duplication**.

First, with Accidental Duplication vs True Duplication, if two mapping routines in `:feature:catalog` and `:feature:profile` look identical, but one responds to catalog marketing needs and the other responds to user account settings, the duplication is accidental. Unifying them creates an artificial coupling between two unrelated business domains. Next, with Feature Module Boundaries, in multi-module architectures, forcing two independent feature modules to share an abstraction just to eliminate 15 lines of UI formatting creates a shared compile-time dependency, slowing builds and creating merge friction. Duplicating those 15 lines preserves independent module deployability.
Finally, with Early Stage / Exploratory Features, when a feature is brand-new, requirements mutate rapidly. Prematurely creating a rigid generic base class forces engineers to add boolean parameter flags (`isCaseB = true`) until the abstraction becomes an unmaintainable monster.


## Interview answer — deep senior

The life cycle of the **Wrong Abstraction** follows a predictable, destructive pattern.

First, developer A sees two similar routines and unifies them into `GenericHelper`. Next, feature requirements diverge. Developer B needs a slight difference, so they add an `if (flag)` parameter.
Developer C needs another variation, adding another flag. Finally, a year later, `GenericHelper` takes 8 boolean flags, has 20 conditional branches, and nobody dares touch it.

We adhere strictly to the **Rule of Three**: allow duplication to happen twice. Only when the exact same pattern recurs a third time across stable, mature requirements do we extract an abstraction, because by the third time, the true invariant shape of the abstraction is obvious.


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
