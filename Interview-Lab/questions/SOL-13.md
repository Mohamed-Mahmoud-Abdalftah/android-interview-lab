---
id: "SOL-13"
question: "Why can creating an interface for every class make design worse?"
topic: "SOLID & Object-Oriented Design"
code: "SOL"
group: "B"
phase: 2
priority: "P1"
order: 184
editorial_status: "reviewed"
---

# SOL-13

## Original interview question

Why can creating an interface for every class make design worse?

## What the interviewer evaluates

Explain interface cost and distinguish useful polymorphism from ceremonial one-to-one pairs.

## Explanation in Arabic

Interface لكل class تخلي codebase فيها `Foo`/`FooImpl` حتى لو مفيش alternate implementation أو consumer محتاج abstraction. ده يضاعف navigation وDI bindings ويجمّد API قبل ما تفهم variation الحقيقية. tests تقدر تختبر pure concrete classes مباشرة؛ fake محتاجها عند boundary مهم مش كل helper. Interface مفيدة عند repository contract، provider strategies، أو module boundary له سبب مستقل للتغيير. اسأل: مين consumer؟ هل محتاج contract مختلف؟ هل signature domain-friendly؟ لو لا، خلّي class concrete واستخدم `internal`/constructor injection.

## Why it matters and how it works

Abstraction is a trade-off. It can decouple change and enable substitution, but every interface adds names, wiring and maintenance. A one-to-one mirror is not automatically a stable contract.

## Worked example

Example: `PriceFormatter(locale)` has one deterministic implementation and can be tested directly. `PaymentGateway` has two SDK adapters and a policy consumer, so an interface has a clear role. Hilt can inject either a concrete formatter or a bound gateway interface.

## Trade-offs and decision criteria

Premature abstraction can be revised later after a second implementation appears. Conversely, delaying a boundary when policy imports a volatile SDK can make testing and change costly. Use evidence from change patterns.

## Failure modes

A new field requires editing `ProfileFormatter`, `IProfileFormatter`, a binding module, fake, and dozens of mocks, with no behavior variation. The interface has created work without reducing coupling. Simplify and test public behavior.

## Production perspective

A feature team keeps concrete validators and formatters internal, with narrow interfaces for session state and payment providers. Architecture tests ensure DTOs do not leak across those meaningful contracts.

## Interview answer — short

An interface per class adds indirection and maintenance without necessarily isolating change. I use interfaces for real consumer contracts or multiple implementations, and keep simple cohesive helpers concrete.

## Interview answer — structured

A one-to-one interface and implementation often change together, so the interface may not be protecting anything. It adds navigation, bindings and fake boilerplate. For a pure formatter, I can inject and test the concrete class directly. For a payment gateway or domain-facing repository, a narrow contract may isolate a volatile adapter or support multiple providers. I decide from the consumer and change boundary, not from a rule that every class must have a mockable interface. A warning sign is when each small feature change edits both the interface and its only implementation, then updates a binding module and several mocks. That is usually not independent variation. I would collapse it until a real consumer boundary appears.

## Interview answer — deep senior

The cost of an abstraction is paid on every read and every refactor. If `Thing` and `ThingImpl` have identical APIs and no independent consumers or implementations, the pair may make a small feature harder to understand. It can even freeze a poor interface too early. I prefer to keep a pure helper concrete and test its behavior directly. When a high-level policy would otherwise import Retrofit or a vendor SDK, a consumer-oriented contract has a real job; provider strategies also justify one. I inspect module dependencies and signature types, because an interface returning `Response<Dto>` does not decouple business policy. Hilt can inject concrete classes, so DI framework use is not a reason to multiply interfaces. Tests also inform the choice. A pure class with injected primitive collaborators can be instantiated without a fake interface. A repository boundary consumed by several features may need a contract so tests can provide deterministic data and infrastructure can change independently. But mocking every internal helper can make tests brittle to refactoring rather than protective of behavior. I prefer fakes at meaningful seams, concrete classes within a feature, and a periodic audit of one-to-one pairs. The objective is readable change, not maximum theoretical replaceability.

## Deep-dive talking points

Compare one-to-one interface pair with provider contract; inspect client and change axis.

## Follow-up questions

- [ARC-15](../arc-15/): When is concrete sufficient? **Answer:** when no meaningful variation or boundary is protected.
- [SOL-06](../sol-06/): When is abstraction valuable? **Answer:** when it keeps policy independent of volatile details.

## Self-check rubric

Choose a formatter and a payment gateway; justify which one needs an interface and why.

## References and reviewed-on date

- [Android architecture recommendations](https://developer.android.com/topic/architecture/recommendations) — adaptable design guidance.
- [Android dependency injection](https://developer.android.com/training/dependency-injection) — constructor injection without mandatory interfaces.

Technically reviewed against the linked primary design/language/Android guidance on 2026-10-11. Conceptual examples are not device-tested.
