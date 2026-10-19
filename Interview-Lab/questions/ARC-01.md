---
id: "ARC-01"
question: "What is Clean Architecture, and what problem does it solve?"
topic: "Clean Architecture, MVVM, MVI & UDF"
code: "ARC"
group: "A"
phase: 2
priority: "P1"
order: 146
editorial_status: "reviewed"
---

# ARC-01

## Original interview question

What is Clean Architecture, and what problem does it solve?

## What the interviewer evaluates

- Explain separation of business policy from UI, persistence, and network details.
- Explain the dependency rule rather than reciting a fixed number of layers.
- Show where an interface belongs when an inner policy must use an outer mechanism.
- Distinguish Clean Architecture from Android's recommended UI, data, and optional domain layers.
- Judge the cost of interfaces, mappings, and modules against the actual change and test risks.

## Concept and technical explanation

Clean Architecture protects important policies from changes in delivery mechanisms. Its dependency rule says source code dependencies point toward the inner policy. An inner rule can define the interface it needs, while an outer adapter implements it. A package name alone does not enforce this direction.

Android's official architecture guide recommends at least UI and data layers, with an optional domain layer for complex or reused logic. Its diagram allows a domain use case to depend on data layer classes. That is a pragmatic Android layering recommendation, not the same strict dependency direction as the original Clean Architecture model. Explain which boundary your project actually uses instead of claiming the two diagrams are identical.

The problem is coupling: a business decision tied to a ViewModel, Retrofit DTO, or Room entity becomes harder to change or test independently. A separate use case and domain owned interface help when that decision has its own policy. A simple read screen may work well with UI and a repository; a pass through use case would add little value.

## Practical walkthrough (English)

Consider a product quote. A `QuoteProduct` use case applies a stable discount rule to product data returned through `ProductRepository`. The domain owns the repository contract; an outer data adapter can fetch and map the network DTO. The ViewModel turns the quoted amount or an unavailable result into UI state. The unit test below uses an in memory fake, so it tests the rule without an Android runtime. The adapter still needs its own integration tests for mapping and errors.

## Explanation in Arabic

فكرة `Clean Architecture` إني أفصل قرار المنتج المهم عن تفاصيل الشاشة والشبكة والتخزين. في النموذج الأصلي، `Dependency Rule` معناها إن اعتماد الكود يبص ناحية القاعدة الداخلية. لو القاعدة محتاجة بيانات، هي تعرّف `Repository Interface` مناسب لها، والـ `Data Adapter` الخارجي ينفذه. اسم `domain` على Package مش كفاية لو جوّاها `Retrofit DTO` أو `Context`.

دليل Android الرسمي بيقترح `UI` و`Data` كحد أدنى، و`Domain Layer` اختيارية للمنطق المعقد أو المتكرر. الرسم بتاعه يسمح للـ `Domain` تعتمد على كلاسات من `Data`؛ ده تنظيم عملي ومش نفس قاعدة الاعتماد الصارمة في `Clean Architecture` الأصلية. في Interview أوضح أنا بتكلم عن أي تصميم وليه اخترته.

## Practical walkthrough

تخيل شاشة بتعرض سعر منتج بعد خصم له قاعدة مستقرة. `QuoteProduct` يطلب المنتج من `ProductRepository` Interface ويطبق القاعدة؛ `Data Adapter` تجيب `DTO` وتحولها، والـ `ViewModel` تعرض السعر أو حالة عدم التوفر. أختبر حساب الخصم بـ Fake Repository على JVM، وأختبر الـ Mapping وأخطاء الشبكة عند حد البيانات. لو الشاشة بتعرض قيمة جاية من Endpoint من غير قرار مستقل، ممكن `Use Case` زيادة ما تفيدنيش.

## Why it matters and how it works

The key is a dependency boundary around a meaningful policy. A domain interface lets a rule use data without importing the transport implementation. A pure Kotlin module can make some forbidden imports visible at compile time, but the actual module graph and API exposure still need review. Mapping at the boundary can isolate a stable product model from a changing wire format. These choices make unit tests simpler and contain some changes; they do not make every UI or backend change invisible.

## Worked example

This self contained JVM example shows the domain contract and an in memory test adapter. A real data adapter would implement the same contract and map its transport model.

```kotlin
data class Product(val id: String, val priceCents: Long)

interface ProductRepository {
    fun find(id: String): Product?
}

class QuoteProduct(private val products: ProductRepository) {
    fun quoteCents(id: String): Long? {
        val product = products.find(id) ?: return null
        require(product.priceCents >= 0)
        return product.priceCents * 90 / 100
    }
}

fun main() {
    val fake = object : ProductRepository {
        override fun find(id: String) =
            if (id == "p1") Product(id, 10_000) else null
    }
    val quote = QuoteProduct(fake)
    check(quote.quoteCents("p1") == 9_000L)
    check(quote.quoteCents("missing") == null)
}
```

The integer calculation is deliberately small; production money rules need a specified currency, rounding policy, overflow handling, and an authoritative backend price.

## Trade-offs and decision criteria

- Add a domain use case when it owns a decision, coordinates repositories, or serves more than one ViewModel.
- A separate model and mapper help when transport and product contracts change independently; they also increase maintenance work.
- A Gradle module can enforce a boundary but adds build and ownership overhead. Start with clear dependencies, then modularize when enforcement is worth that cost.
- A use case that only forwards a repository call can obscure a straightforward data path.

## Failure modes

- Declaring a `domain` package while its classes import `Context`, Retrofit DTOs, or Room entities and claiming the boundary is strict.
- Assuming Android's recommended optional domain layer requires domain owned repository interfaces in every app.
- Creating one interface and mapper per class without a policy or change boundary to protect.
- Testing only the domain fake while leaving data mapping, error semantics, and UI state untested.
- Treating a client side financial check as final approval; the server must decide against current authoritative state.

## Production perspective

First draw the source dependency graph and identify the rules that change for different reasons from UI or persistence. Put a strict rule in a pure Kotlin module when compile time separation helps. Keep transport conversion and error translation in a data adapter, and test that adapter separately. Decide the source of truth and behavior after process death for offline features. In regulated workflows, client checks improve feedback but do not authorize server side effects.

## Interview answer — short

Clean Architecture keeps important business decisions from depending on UI and data mechanisms. Its dependency rule points code inward: the rule defines the contract it needs, and an outer adapter implements it. On Android I use that boundary when a rule deserves independent tests or must survive framework changes. A simple screen may only need UI and data layers; extra use cases are not automatically useful.

## Interview answer — structured

I start with the problem: if a ViewModel mixes a pricing rule with Retrofit responses and UI state, a wire format change or screen redesign can disturb the rule. In strict Clean Architecture, the rule and its required interface sit inside; a data adapter depends on and implements that interface. The ViewModel asks the rule for a result and maps it to UI state.

For a product quote, I can test discount logic using a fake repository in a JVM test. Then I test the real adapter's DTO mapping and failure handling separately. That gives useful isolation without pretending the fake test covers networking.

I also distinguish this from Android's official guide. It recommends UI and data layers, with an optional domain layer, and its diagram has a different dependency direction. I choose a strict inner boundary when policy complexity or independent change makes it worthwhile. For a direct read screen, a pass through use case may just add files.

## Interview answer — deep senior

I would inspect actual imports and module dependencies before calling a design Clean Architecture. In the original model, source dependencies point toward high level policy. If the policy imports `Context`, Retrofit DTOs, or Room entities, that boundary has leaked. A domain owned repository interface plus an outer implementation can invert the compile time dependency; dependency injection wires the implementation at the app root. A pure Kotlin Gradle module can help enforce the boundary, but naming folders does not.

For a quote flow, the use case owns a price rule, the repository contract describes what product data it needs, and the data implementation maps HTTP or local records into that contract. The ViewModel maps the result to `UiState`. I would test the rule with a fake, the adapter with integration tests, and the screen state separately. I would define whether missing data, timeout, stale cache, and invalid input are distinct outcomes, because a generic failure type can hide a product decision.

Android's architecture guidance makes the domain layer optional and allows a domain use case to depend on data classes. That guidance is useful, but it is not the original strict dependency rule. I would be precise about which pattern the app follows. Interfaces, mappers, and modules cost review and build time, so I add them where they protect a meaningful policy or a likely change boundary. An offline feature additionally needs a clear source of truth and process death behavior. A client side eligibility check in a payment flow remains advisory; only the backend can authorize against current state.

## How to answer in the interview

Define the coupling problem, explain the dependency direction in the original model, show one useful rule and adapter, then give a case where another layer would be unnecessary. Name the difference from Android's optional domain recommendation if the interviewer asks about its diagram.

## Deep-dive talking points

- Source dependency direction versus runtime call direction.
- Domain owned interface and outer adapter wiring.
- Android optional domain guidance versus the original Clean Architecture rule.
- Module enforcement, mapping cost, and tests at each boundary.
- Source of truth and authoritative decisions in offline or financial flows.

## Follow-up questions

- **Interviewer:** "Does every button need a use case?" **Answer:** "No. I add one when it owns a decision or useful orchestration; forwarding a single repository call may add no value."
- **Interviewer:** "Can Android's domain layer depend on data?" **Answer:** "The official Android guide's diagram allows that. Strict Clean Architecture uses a different source dependency direction, so I name the pattern I am applying."
- **Interviewer:** "Where does a Retrofit response model go?" **Answer:** "In the data adapter. I map it before a strict domain rule if the wire format should not shape that rule."
- **Interviewer:** "Does a client side transfer check approve the transfer?" **Answer:** "No. The backend must validate current state and commit the decision atomically."

## Self-check rubric

Can I draw the compile time dependency arrows, name a rule worth isolating, explain Android's optional domain diagram, and say what the fake domain test does not cover?

## References and reviewed-on date

- [Android Guide to App Architecture](https://developer.android.com/topic/architecture) — recommended UI/data layers and optional domain.
- [Android Domain Layer](https://developer.android.com/topic/architecture/domain-layer) — use case guidance.
- [Robert C. Martin: The Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html) — original dependency rule.

Technically reviewed against the cited primary documentation on 2026-10-19; this is an agent editorial review, not a human review.
