---
id: "PAT-07"
question: "What does Dependency Injection as a pattern accomplish?"
topic: "Design Patterns"
code: "PAT"
group: "A"
phase: 2
priority: "P1"
order: 198
editorial_status: "reviewed"
---

# PAT-07

## Original interview question

What does Dependency Injection as a pattern accomplish?

## What the interviewer evaluates

Explain external construction, visible dependencies, replaceable collaborators, and scope ownership. Distinguish the DI pattern from Hilt and the Dependency Inversion Principle.

## Concept and technical explanation

Dependency Injection (DI) moves the choice and construction of a collaborator outside the object that uses it. A constructor parameter makes a required dependency visible; a composition root supplies the object. This can make behavior easier to reuse and test, but it does not require interfaces for every class or guarantee that the selected binding or lifetime is correct. DI is one way to apply Inversion of Control. The Dependency Inversion Principle is a separate rule about the direction of source-code dependencies.

## Practical walkthrough (English)

An order total calculator needs a promotion rule. If it constructs a concrete rule internally, a test cannot supply another rule through its public API. With constructor injection, app assembly supplies the live rule and a focused test supplies a fixed rule. For this small graph, manual wiring suffices. Hilt can help when Android entry points and scope management make wiring repetitive.

## Explanation in Arabic

Dependency Injection معناها إن الكلاس يعلن عن الـ collaborators اللي محتاجها، والـ composition root يختار ويكوّن التنفيذات ويمررها له. لو `OrderTotal` بتبني `PromotionPolicy` جواها، تغيير قاعدة الخصم أو اختبارها يبقى أصعب. لما تستقبل policy في الـ constructor، نفس الحساب يشتغل بقاعدة إنتاج أو Fake في Unit Test. دي طريقة لتطبيق Inversion of Control؛ لكنها مش هي Dependency Inversion Principle نفسها. تمرير Concrete SDK Client في constructor يظل DI، مع إن اعتماد الـ domain عليه مباشرة ممكن يبقى حد معماري ضعيف. الـ pattern ما بيختارش Scope أو Binding صح نيابة عنك.

## Practical walkthrough

في تطبيق طلبات، `OrderTotal` تستقبل `PromotionPolicy` وتحسب المطلوب دفعه. الـ app wiring يمرر قاعدة الخصم الحقيقية، والـ test يمرر policy ثابتة فيختبر حدود الخصم من غير API أو Android Context. لو الـ graph صغيرة، ركّبها يدويًا. لو عندك Android entry points وScopes كتير، Hilt تقلل كود التوصيل، لكن لازم تراجع أي Implementation بتتربط في كل Variant.

## Why it matters and how it works

The consumer declares a collaborator and app assembly chooses its implementation. A test can inject a deterministic fake; a build variant can choose another implementation. These benefits depend on a useful boundary. Hilt/Dagger can automate a larger graph and validate bindings they know about, but the pattern also works without any library.

## Worked example

This Kotlin/JVM example uses manual constructor injection.

```kotlin
interface PromotionPolicy { fun discountCents(subtotal: Int): Int }
class OrderTotal(private val policy: PromotionPolicy) {
    fun dueCents(subtotal: Int): Int {
        require(subtotal >= 0)
        val discount = policy.discountCents(subtotal)
        require(discount in 0..subtotal)
        return subtotal - discount
    }
}
class NoPromotion : PromotionPolicy {
    override fun discountCents(subtotal: Int) = 0
}
fun main() {
    check(OrderTotal(NoPromotion()).dueCents(1200) == 1200)
}
```

## Trade-offs and decision criteria

Manual DI keeps a small graph transparent but can require repetitive wiring across Android entry points. Hilt/Dagger add generated graph management and compile-time binding checks at the cost of build setup and scope decisions. Avoid interfaces for trivial helpers solely to satisfy a pattern. Review object ownership independently of graph construction.

## Failure modes

A graph compiles while the release variant receives a sandbox promotion policy: DI proves a binding exists, not that it expresses business intent. A singleton retaining an Activity can leak it. A service locator can hide dependencies and force tests to share mutable registry state. Test variants and lifetimes separately.

## Production perspective

Wire pricing policies at app composition and construct pure calculation logic directly in JVM tests. For framework-created Android entry points, Hilt can supply collaborators through its integration. Verify production bindings and lifetimes; a successful graph does not prove the selected policy is correct.

## Interview answer — short

Dependency Injection separates choosing and constructing a dependency from the class using it. `OrderTotal` can receive a `PromotionPolicy` through its constructor, so production supplies a real rule and tests supply a fixed one. The dependency is visible and replaceable. The pattern works with manual wiring; Hilt can help manage a larger Android graph.

## Interview answer — structured

As a pattern, DI changes who chooses collaborators. If an order calculator constructs a promotion rule internally, changing the rule changes the calculator and tests must work around its construction. With constructor injection, the calculator declares `PromotionPolicy`; app assembly supplies production behavior and a test supplies a deterministic fake.

That separates construction from calculation and makes the dependency visible. It does not automatically enforce the Dependency Inversion Principle: an injected concrete SDK client can still couple domain logic to infrastructure. A graph can compile while a release variant selects the wrong pricing policy.

For a small graph, manual wiring is clear. With many Android entry points, variants, and scopes, Hilt can reduce repetitive wiring. Either way, I would test the selected variant and lifetime: a singleton retaining Activity Context remains a bug when injection succeeds.

## Interview answer — deep senior

DI gives the consumer an explicit contract for required collaborators and moves their construction to a composition root. Constructor injection suits objects whose collaborators are required at creation. Android framework classes such as Activity and Fragment are created by the system, so their injection needs an integration mechanism such as Hilt field injection; ordinary collaborators can still use constructors.

For `OrderTotal`, an injected `PromotionPolicy` allows the same calculation to run with a production rule or a fake. A JVM unit test can cover discount boundaries without network or Android Context. That unit test cannot prove the production graph chose the right policy, so an integration test must inspect important build variants and account-specific selections.

DI is related to Inversion of Control but distinct from the Dependency Inversion Principle. Injecting a concrete SDK client is still DI, yet it may leave high-level policy coupled to infrastructure. Add an interface when it represents a real boundary, not for every helper. Manual composition is often readable for a few objects; Hilt/Dagger can generate larger graphs and catch missing bindings they compile. Neither chooses scope ownership automatically. An app-scoped object holding Activity Context or stale per-user state may outlive its owner. Define lifetimes and variants, then verify both graph construction and business behavior.

## How to answer in the interview

- **Pattern:** external construction and explicit collaborators.
- **Example:** inject `PromotionPolicy` into `OrderTotal`; supply a fake in a test.
- **Decision:** manual wiring for a small graph, Hilt when Android graph management grows.
- **Limit:** a binding or scope can still be wrong.

## Deep-dive talking points

Constructor injection versus platform-created entry points; DI versus Dependency Inversion; manual composition versus Hilt; variant bindings and lifetime checks.

## Follow-up questions

- **Interviewer:** "Does DI require Hilt or an interface for every dependency?"
  **Answer:** "No. A constructor supplied by app wiring is already DI. I add an interface for a useful boundary and Hilt when graph assembly needs automation."

- **Interviewer:** "What can compile-time graph validation miss?"
  **Answer:** "The release build might select a sandbox policy or a singleton might retain Activity state. Those require behavior and lifetime checks."

## Self-check rubric

Explain external construction, show a replaceable collaborator, distinguish DI from Dependency Inversion, and name a binding or scope mistake DI does not prevent.

## References and reviewed-on date

- [Android dependency injection](https://developer.android.com/training/dependency-injection) — pattern and manual wiring.
- [Hilt on Android](https://developer.android.com/training/dependency-injection/hilt-android) — framework entry points.
- [Hilt components](https://dagger.dev/hilt/components.html) — component scopes.

Technically reviewed against primary documentation on 2026-10-19.
