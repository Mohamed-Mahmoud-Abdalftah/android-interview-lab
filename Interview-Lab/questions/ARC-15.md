---
id: "ARC-15"
question: "When do you introduce interfaces, and when can concrete implementations be sufficient?"
topic: "Clean Architecture, MVVM, MVI & UDF"
code: "ARC"
group: "B"
phase: 2
priority: "P1"
order: 160
editorial_status: "reviewed"
---

# ARC-15

## Original interview question

When do you introduce interfaces, and when can concrete implementations be sufficient?

## What the interviewer evaluates

Choose interfaces for meaningful polymorphism, boundaries and tests, not one per class.

## Explanation in Arabic

Interface مفيدة لما consumer محتاج contract مستقل عن implementation: repository له offline/server adapters، payment provider strategies، أو module boundary محتاج fake. لكن `Foo` و`FooImpl` لكل class من غير alternative أو سبب تغيّر بيزود navigation وboilerplate. Concrete implementation ممكن تكون كفاية داخل feature صغير، وتقدر تختبرها بحقن dependencies بتاعتها. الأهم public types ما تسرّبش Retrofit/Room لو هدفك عزلها. DI tool يقدر يحقن concrete class؛ interface قرار design مش شرط Hilt.

## Practical walkthrough

Interface مفيدة عند boundary متغير أو له بديل اختبار/feature implementation؛ مثل `PaymentGateway` مع sandbox/vendor. لا تكتب `FooInterface` لكل class final لمجرد DI؛ Hilt يمكن يحقن concrete. ابدأ concrete داخل feature وextract contract عند الحاجة. اختبر behavior لا mock call order فقط؛ adapter الحقيقي يحتاج integration test.

## Why it matters and how it works

Abstractions are valuable when they protect independent change or express a stable consumer contract. Testability comes from substitutable dependencies and deterministic seams, not simply counting interfaces.

## Worked example

Example decision: `PaymentProcessor` interface with `CardProcessor` and `WalletProcessor` supports provider strategy and tests. A single `PriceFormatter` pure class with no planned variation can stay concrete. If its constructor accepts locale/format dependency, tests can still instantiate it.

## Trade-offs and decision criteria

Interfaces add indirection, API maintenance, and potential abstraction drift. Concrete dependencies can be simpler until a variation or module boundary emerges. Extracting an interface later is often cheaper than maintaining a premature one.

## Failure modes

An interface mirrors every method of one class, then both change together on each feature request. It is not an abstraction boundary. Conversely, a domain module importing `RetrofitPaymentClient` couples stable policy to volatile transport.

## Production perspective

A subscription app uses a narrow `EntitlementSource` contract consumed by policy code, with production and fake implementations. Inside one feature, a simple formatter remains concrete and tests call it directly.

## Interview answer — short

I introduce an interface when a consumer needs a stable contract across implementations, module boundaries, or tests. A single concrete class is sufficient when there is no meaningful variation. Interface count is not an architecture quality metric.

## Interview answer — structured

I start from the consumer. If it must remain independent of a payment provider or data source, a narrow interface expresses that need and supports a fake in tests. If I have a small internal formatter with one implementation and no volatile dependency, a concrete class is clearer. I can still test it directly and inject its own dependencies. I avoid `IThing`/`ThingImpl` pairs that move in lockstep without isolating change. This is especially relevant in Hilt projects: dependency injection can create a concrete class just fine. An interface should describe consumer needs, such as a narrow session source or payment processor, rather than copy a class’s full public API.

## Interview answer — deep senior

The question is where change happens. A repository contract consumed by a domain rule can isolate Room or network implementation details; a payment strategy interface can support multiple providers. Those interfaces should be narrow and use domain types. Creating one for every class adds cognitive load and makes refactors touch two declarations. Hilt can construct concrete classes, so DI does not force an interface. I also do not create interfaces solely to mock implementation details; tests can use fakes at meaningful boundaries and instantiate pure concrete collaborators. If a concrete dependency later starts changing independently, extracting a consumer-oriented contract is straightforward. I assess benefit by reduced change propagation, clearer behavior, and test isolation. I also inspect how tests are written. If every test mocks internal helpers, an interface explosion may be hiding over-coupling rather than solving it. A pure concrete class can be instantiated and tested directly; a repository seam can use a small fake. When a second implementation arrives, I can extract the exact common behavior then. The design goal is stable substitution where needed, not maximum indirection. I check public parameter types so a supposed abstraction does not still leak a DTO or framework class.

## How to answer in the interview

- **Why:** abstraction should isolate variability.
- **How:** introduce interface at meaningful boundary.
- **Trade-off:** testability versus interface sprawl.
- **Failure case:** fake hides broken real adapter.
- **Production solution:** pair fake policy test with integration.

## Deep-dive talking points

Compare a provider strategy with a pure formatter. Discuss consumer-owned contracts, fakes, DI and abstraction drift.

## Follow-up questions

- [ARC-26](../arc-26/): How to enforce boundaries without interface explosion? **Answer:** module visibility, dependency checks and narrow contracts at real seams.
- [SOL-13](../sol-13/): Why can an interface per class hurt? **Answer:** it doubles maintenance without providing variation or isolation.

## Self-check rubric

Name one interface worth extracting and one concrete class you would keep; justify both by change boundaries.

## References and reviewed-on date

- [Android architecture recommendations](https://developer.android.com/topic/architecture/recommendations) — dependency practices.
- [Android domain layer](https://developer.android.com/topic/architecture/domain-layer) — reuse and testability.

Technically reviewed against the linked official Android guidance on 2026-10-11. Conceptual examples are not device-tested.
