---
id: "SOL-07"
question: "Compare DIP and Dependency Injection (DI)."
topic: "SOLID & Object-Oriented Design"
code: "SOL"
group: "A"
phase: 2
priority: "P1"
order: 178
editorial_status: "reviewed"
---

# SOL-07

## Original interview question

Compare DIP and Dependency Injection (DI).

## What the interviewer evaluates

Distinguish the direction of source-code dependencies (DIP) from external object construction (DI). Give a Hilt-based counterexample and explain how to repair the boundary without demanding an interface for every class.

## Concept and technical explanation

The Dependency Inversion Principle (DIP) concerns source-code dependency direction: high-level business policy should not import volatile low-level mechanisms; both meet at a suitable abstraction. Dependency Injection (DI) concerns object construction: a consumer receives collaborators from outside. Constructor injection can deliver a concrete HTTP client to a domain policy, so DI alone does not establish the desired boundary. Conversely, an app can manually wire a domain-facing contract without Hilt. An interface is useful when it expresses an architectural boundary; its mere presence does not help if it exposes transport DTOs.

## Practical walkthrough (English)

A checkout policy receives `HttpFeeClient` through Hilt and interprets HTTP status codes. Construction is external, but business policy still knows transport details. Replace that dependency with `FeeQuote`, a domain-facing contract returning a fee. The data adapter handles HTTP and mapping. The app composition root supplies the adapter manually or with a Hilt binding. Check actual Gradle imports to verify the intended module boundary.

## Explanation in Arabic

Dependency Inversion Principle أو DIP بتتكلم عن اتجاه اعتماد الكود: قواعد الـ business المهمة ما تعتمدش مباشرة على تفاصيل متغيرة زي HTTP أو Room؛ الاتنين يقابلوا Boundary أو Abstraction مناسبة. Dependency Injection أو DI بتتكلم عن إنشاء الـ collaborators وتوصيلها من خارج الكلاس. ممكن تحقن `HttpFeeClient` في `CheckoutPolicy` بـ Hilt؛ ده DI، لكن الـ policy لسه تعرف تفاصيل HTTP. ولو `CheckoutPolicy` تعتمد على `FeeQuote` وتوصل Implementation يدويًا، تقدر تحقق الحد المعماري من غير Hilt. وجود Interface وحده ما يكفيش لو العقد نفسه مليان DTOs أو HTTP status codes.

## Practical walkthrough

في Checkout، لو سياسة الرسوم بتقرأ `HttpFeeClient` وبتفسر Response Codes، الـ domain مرتبطة بالنقل حتى لو التبعية Injected. خلّيها تطلب `FeeQuote` ترجع قيمة business مفهومة، وخلي Data Adapter يتعامل مع HTTP وmapping. الـ app composition تقدر تمرر الـ adapter يدويًا أو تستخدم Hilt `@Binds`. راجع Dependencies بين Gradle modules فعلًا؛ اسم Interface لوحده مش بيمنع import غير مرغوب.

## Why it matters and how it works

DI makes a collaborator externally supplied. DIP keeps a high-level policy independent of volatile implementation details. They frequently work together, but neither proves the other. The abstraction must use domain-facing types, and the feature or domain module must not import the lower-level network implementation.

## Worked example

A domain-facing fee contract can be implemented by a network adapter in production and by a fixed fake in a JVM test. The following manual wiring is runnable.

```kotlin
interface FeeQuote { fun feeCents(orderCents: Int): Int }
class CheckoutFeePolicy(private val quote: FeeQuote) {
    fun totalCents(orderCents: Int): Int {
        require(orderCents >= 0)
        val fee = quote.feeCents(orderCents)
        require(fee >= 0)
        return Math.addExact(orderCents, fee)
    }
}
class FixedFeeQuote(private val feeCents: Int) : FeeQuote {
    override fun feeCents(orderCents: Int) = feeCents
}
fun main() {
    check(CheckoutFeePolicy(FixedFeeQuote(25)).totalCents(100) == 125)
}
```

## Trade-offs and decision criteria

Not every concrete dependency violates DIP: ask whether a high-level policy depends on a volatile detail across a meaningful boundary. Interfaces for trivial helpers add cost. Manual composition may be sufficient for a small graph; Hilt helps assemble larger Android graphs. Neither repairs a leaky contract automatically.

## Failure modes

A team moves `Retrofit.create()` into Hilt, but `CheckoutPolicy` still interprets HTTP 409 and response DTOs. The policy now has external construction but still depends on transport. Move mapping to the data adapter, define a business-facing contract, and verify module imports plus focused behavior tests.

## Production perspective

Let checkout policy depend on a `FeeQuote` contract and let a data adapter implement it. Compose the adapter in the app module manually or with Hilt. Test the policy with a fake and the adapter separately. Do not claim a build-time improvement without measuring the actual dependency graph.

## Interview answer — short

DIP is about the direction of source-code dependencies: high-level policy should not depend directly on volatile HTTP or database details. DI is about supplying objects from outside rather than constructing them inside a consumer. Hilt can inject `HttpFeeClient` into a policy, which is DI but may leave the wrong architectural boundary. DIP can also be applied with manual wiring.

## Interview answer — structured

DIP answers “what may this policy depend on?” DI answers “who constructs and passes its collaborators?” If a checkout policy receives `HttpFeeClient` from Hilt and interprets HTTP codes, constructor injection works, but the business rule still imports transport details.

Instead, the policy can depend on a `FeeQuote` contract using domain terms; a data adapter converts HTTP responses into that result. App assembly can pass the adapter manually or use Hilt `@Binds`. Hilt is not required for DIP, and an interface is not enough if it still exposes response DTOs.

I would inspect module imports and contract types, not just `@Inject`. I would not add interfaces for every internal helper. Then I would test fee policy with a fake and the HTTP adapter at its own boundary.

## Interview answer — deep senior

DIP governs source-code dependency direction. A high-level business policy should not import a volatile transport or storage mechanism; the mechanism should meet the policy at a suitable contract. DI governs runtime object assembly: a composition root supplies the collaborator instead of the policy creating it. The concepts work well together but are logically independent.

In checkout, Hilt may supply `HttpFeeClient` to `CheckoutPolicy`, which then interprets 409 and a response DTO. That is valid constructor injection yet a weak policy boundary. If the policy receives `FeeQuote` in domain terms and a data adapter handles HTTP mapping, the source dependency can point toward the stable rule. The app module can supply the adapter manually or through Hilt. Check that the feature or domain Gradle module does not import the network implementation.

Do not reduce DIP to “every concrete class is forbidden.” A stable internal helper might need no interface, while an interface returning `Response<FeeDto>` still leaks transport. Review API types and which details change independently. A fake `FeeQuote` gives focused JVM policy tests; the adapter needs separate mapping and network behavior tests. The DI framework checks known bindings, not contract quality or module boundaries. Any build or test speed claim requires measurement of the actual graph.

## How to answer in the interview

- **DIP:** direction of source-code dependencies.
- **DI:** external object construction and delivery.
- **Counterexample:** Hilt injects an HTTP client into business policy.
- **Repair:** domain-facing contract plus transport adapter; inspect module imports.
- **Caveat:** no interface is needed for every helper.

## Deep-dive talking points

Hilt without DIP; manual DI with DIP; contract types and DTO leakage; `@Binds` as assembly, not architecture; Gradle module dependency direction.

## Follow-up questions

- **Interviewer:** "Can DIP work without Hilt?"
  **Answer:** "Yes. Define a suitable contract, implement it in an adapter, and wire it manually at app composition. Hilt only automates assembly."

- **Interviewer:** "Does injecting any concrete class violate DIP?"
  **Answer:** "No. The question is whether high-level policy imports a volatile lower-level detail. A concrete internal helper can be fine, while an interface exposing HTTP DTOs still leaks transport."

## Self-check rubric

State the different questions DIP and DI answer, show DI with a leaky boundary, repair it, and explain why neither every concrete class nor every interface decides DIP compliance.

## References and reviewed-on date

- [Android dependency injection](https://developer.android.com/training/dependency-injection) — DI mechanics.
- [A Little Architecture](https://blog.cleancoder.com/uncle-bob/2016/01/04/ALittleArchitecture.html) — source dependency direction.
- [Android modularization patterns](https://developer.android.com/topic/modularization/patterns) — module boundaries.
- [Dagger `@Binds`](https://dagger.dev/api/latest/dagger/Binds.html) — binding contract to implementation.

Technically reviewed against primary documentation on 2026-10-19.
