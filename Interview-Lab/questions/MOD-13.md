---
id: "MOD-13"
question: "When should a module depend on an interface versus a concrete type?"
topic: "Gradle Modularization & Dependency Boundaries"
code: "MOD"
group: "B"
phase: 4
priority: "P1"
order: 366
editorial_status: "reviewed"
---

# MOD-13

## Original interview question

When should a module depend on an interface versus a concrete type?

## What the interviewer evaluates

- Use abstraction where independent substitution/ownership is real.
- Avoid interface-per-class ceremony.
- Explain compile boundary, tests and dependency direction.

## Explanation in Arabic

اعتمد على interface عندما consumer يحتاج قدرة مستقرة وimplementation تختلف أو تعيش في module لا ينبغي استيرادها: `CheckoutRepository` عقد يراه checkout وتطبقه data module. هكذا app يختار implementation، والاختبار يمرر fake. لكن لو class محلية داخل feature، لا توجد بدائل ولا boundary، فـinterface لها طريقة واحدة وimplementation واحدة قد تكون عبئًا بلا قيمة. القرار عن ملكية العقد: من يحتاجه يحدد السلوك، ولا تجعل implementation تفرض تفاصيل Retrofit/Room في API.

### Practical walkthrough in Egyptian Arabic

Module تعتمد interface عند boundary متغيرة، مثل `PaymentGateway` يستبدل vendor، أو network client عبر data implementation. لو class بسيطة داخل feature ولا بديل واقعي، concrete dependency أوضح وأسهل. لا تنشئ `IUserMapper` لكل mapper. حدد لماذا interface موجودة، من يملكها، وهل test fake يثبت behavior أم يخفي adapter broken.

## Why it matters and how it works

An interface can invert compile dependency from policy to implementation: the consumer compiles against a contract and an outer composition root provides a concrete binding. This enables independent testing and replacement. The abstraction only reduces coupling when its methods express stable capability; a mirror interface that changes with every implementation edit preserves coupling under a new name.

## Worked example

Orders ViewModel depends on `OrderRepository` exposing `observeOrder(id)` and `submitOrder(command)`, with domain results. `:data:orders` implements it with Room and API clients. Tests inject a fake. In the same feature, a final `CurrencyLabelFormatter` used in one place may be passed concretely until a real module or behavior boundary emerges.

## Trade-offs and decision criteria

Interfaces cost design, DI binding and maintenance but can isolate high-volatility implementation. Concrete dependencies are simpler when code changes together and no external contract is needed. Testability alone is not an excuse to abstract every class; constructor injection can also test many concrete collaborators.

## Failure modes

A contract returns Retrofit `Response` and therefore still couples the feature to transport. An interface has one method per implementation detail and changes every sprint. A feature directly imports a data implementation to avoid one needed interface. An unnecessary interface forest makes navigation through code slow.

## Production perspective

Review dependency direction and contract change frequency. Keep public interfaces small and semantically owned, and use integration tests to ensure selected implementations satisfy critical behavior beyond fake tests.

## Interview answer — short

“Depend on an interface when it is a genuine stable boundary with independent implementation or substitution; use a concrete type for cohesive local code.”

## Interview answer — structured

“I ask who owns the policy and whether the implementation must vary independently. A feature repository contract lets its ViewModel avoid importing Room or network code, while app composition selects the data implementation and tests pass a fake. A local formatter with one owner may not need an interface. An abstraction helps only if it expresses domain behavior rather than exposing transport types or mirroring every implementation method.”

## Interview answer — deep senior

“An interface is useful when it changes the dependency direction in a meaningful way. The Checkout feature may need ‘submit an order and observe status,’ while data infrastructure decides how to use Room and a provider API. A contract in a feature-visible API lets Checkout compile without those implementation modules; the app graph binds the concrete class, and a fake supports focused tests. I design the methods around capability and domain outcomes, not around Retrofit Response or DAO entities, or I have merely disguised the coupling. Conversely, a small helper that is created and changed inside one feature may be clearer as a concrete constructor dependency. Creating an interface for every class adds DI bindings and navigation cost without independent ownership or a plausible alternative. I review the contract's stability and change history: if it changes on every implementation edit, the boundary is not buying much. I still add an integration test for the real implementation because a fake can satisfy the interface while missing transactional or network semantics.”

## How to answer in the interview

- **Why:** interfaces protect variability, not aesthetics.
- **How:** place contract with consumer or stable core.
- **Trade-off:** flexibility versus boilerplate.
- **Failure case:** mock passes while real SDK fails.
- **Production solution:** pair seam test with integration.

## Deep-dive talking points

Discuss inversion, contract owner, implementation leakage, test fake drift, and abstraction cost.

## Follow-up questions

- Does an interface automatically decouple modules? **Answer:** no; transport types and volatile methods can still leak implementation details.
- Can a concrete class be testable? **Answer:** yes, especially with constructor-injected collaborators and local ownership.
- Who binds the implementation? **Answer:** a composition root or DI module visible in the final app graph.

## Self-check rubric

Choose one interface and one concrete dependency, justify ownership, and identify API leakage.

## References and reviewed-on date

- [Android modularization guide](https://developer.android.com/topic/modularization) — boundaries and encapsulation.
- [Dependency injection on Android](https://developer.android.com/training/dependency-injection) — substitution and graph design.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. Interface selection is a design judgment.
