---
id: "PAT-10"
question: "Compare Factory and Abstract Factory."
topic: "Design Patterns"
code: "PAT"
group: "B"
phase: 2
priority: "P1"
order: 201
editorial_status: "reviewed"
---

# PAT-10

## Original interview question

Compare Factory and Abstract Factory.

## What the interviewer evaluates

Explain one product construction versus related product families and prevent mismatched configurations.

## Explanation in Arabic

Factory عادة تنشئ product أو تختار implementation واحد، مثل `createPaymentGateway(method)`. Abstract Factory تعرض مجموعة factories لمنتجات مرتبطة لازم تكون compatible: `EnvironmentFactory` تدي API client وserializer وauth config لنفس sandbox/production environment. ما تستخدمش Abstract Factory لمجرد عندك اتنين constructors؛ تعقيدها يستحقه لما family consistency مهمة. في Android DI graph ممكن توفر نفس family بالqualifiers/modules، لكن اختبر إن sandbox client ما يتوصلش production credentials.

## Why it matters and how it works

A regular factory encapsulates creation/selection of one product role. An abstract factory defines construction of a family of related products without clients naming concrete classes. The benefit is consistent combinations; the cost is another abstraction layer.

## Worked example

Conceptual Kotlin:
```kotlin
interface EnvironmentFactory {
    fun api(): PaymentsApi
    fun signer(): RequestSigner
}
interface PaymentsApi
interface RequestSigner
```
A sandbox factory returns both sandbox implementations; a production factory returns matching production ones. This contract alone is not credential storage.

## Practical walkthrough

Factory تنشئ نوع واحد حسب input/policy: `providerFor(method)` ترجع implementation للـpayment method أو error unsupported. Abstract Factory بتطلع family متوافقة: `environment.createApi()` و`createSigner()` للـsandbox أو production، فتقل احتمالية mixing endpoint production مع key sandbox. لو family مش موجودة، Abstract Factory زيادة طبقة بلا فايدة؛ function factory بسيطة تكفي. لا تخلّي factory تعمل network أو تمسك session mutable خفية؛ construction واضحة، وDI graph تملك lifetime. اختبر إن كل environment فيها زوج صحيح وإن unsupported method لا يقع في default unsafe.

## Trade-offs and decision criteria

A simple constructor or factory is easier if only one object varies. Abstract Factory helps when several products must change together, but adding a new product method can affect all factories. Hilt qualifiers may be clearer for a static Android graph.

## Failure modes

A test build accidentally combines sandbox API with production signer because clients independently create them. Factory family or DI validation prevents mismatch; secrets still belong in backend, not APK.

## Production perspective

A payment SDK wrapper has test and production client families with compatible endpoint/signature strategies. Integration tests verify environment pairing and no production charge from test configuration.

## Interview answer — short

A Factory creates or selects one product; an Abstract Factory supplies a compatible family of related products. I use the latter when environment or provider variants must stay matched, not for a single constructor.

## Interview answer — structured

If I only need to choose a card gateway implementation, a factory is enough. If switching an environment requires a matched API client, serializer and signer, an Abstract Factory can create that whole family through one contract. That reduces accidental mixed configurations. The extra interface has a cost: adding a new product affects each family implementation. In Android, Hilt qualifiers or modules can express a static family too, so I choose the simplest wiring that protects the invariant.

## Interview answer — deep senior

The difference is dimensional. A factory encapsulates how one kind of object is created, possibly selecting an implementation from input. An abstract factory creates several related roles that should vary together. The client asks for those roles without naming concrete sandbox or production classes. That is useful when a mismatch would be costly, such as test endpoint with production signing configuration. I still validate configuration and run integration tests; the pattern does not hide credentials securely or prevent a misconfigured composition root. If there is only one varying object, Abstract Factory adds needless indirection. If the product family is static and Hilt already has a clear qualifier scheme, I may use that instead of hand-written factories.

A Factory answers how to create one suitable product, for example selecting a payment provider adapter from a method. An Abstract Factory produces a coherent family of related products, such as API client and signer for one environment. That family is valuable when mixing a sandbox signer with a production endpoint would be a serious configuration error. I would keep constructors or a simple factory function when there is only one product and little variation. Factories should validate selection and make ownership visible, not perform hidden network work or become a god object. I test every supported environment pair and the unsupported-method path, and I let DI decide instance lifetime.

## How to answer in the interview

- **Why:** Prevent invalid construction and incompatible product families.
- **How:** Compare provider-for-method Factory with environment API+signer Abstract Factory.
- **Trade-off:** Use one function/constructor when no family exists.
- **Failure case:** Sandbox signer paired with production endpoint or god-factory growth.
- **Production solution:** Validate combinations and test unsupported routes.

## Deep-dive talking points

Distinguish product versus family, environment invariant, and DI qualifier alternative.

## Follow-up questions

- [PAT-03](../pat-03/): Where does Builder differ? **Answer:** staged configuration of one object rather than product-family selection.
- [DI-08](../di-08/): Can qualifiers select variants? **Answer:** yes, Hilt qualifiers distinguish bindings of the same type.

## Self-check rubric

Design a single gateway factory and a two-product environment family; justify which is necessary.

## References and reviewed-on date

- [Android Hilt guide](https://developer.android.com/training/dependency-injection/hilt-android) — qualifier/graph alternative for product-family wiring.
- [GoF Design Patterns, publisher](https://www.pearson.com/en-us/subject-catalog/p/design-patterns-elements-of-reusable-object-oriented-software/P200000009480/9780321700698) — Factory Method and Abstract Factory.

Technically reviewed against the linked primary publisher/language/Android guidance on 2026-10-13. Conceptual examples are not device-tested.
