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

Separate a design principle from object construction/wiring, with a counterexample using Hilt.

## Explanation in Arabic

DIP principle: high-level policy تعتمد على abstraction مش low-level detail. DI technique: dependency تيجي من برّه constructor/provider بدل class تنشئها بنفسها. ممكن تستخدم Hilt وتحقن `RetrofitService` في UseCase، يبقى DI موجودة لكن DIP مش متحققة. وممكن تحقق DIP بـmanual factory من غير Hilt. الـcontract لازم يستخدم domain types ومكانه يخلي policy مستقلة. DI بتحسن wiring/test replacement، لكن مش بتصمم interface ولا بتحدد boundary لوحدها.

## Why it matters and how it works

DI is a construction mechanism; DIP is source-level dependency design. They often work together but are logically independent. Constructor injection makes dependencies visible and replaceable, yet the injected type may still be an unwanted detail.

## Worked example

Counterexample: `class TransferRule @Inject constructor(private val api: RetrofitTransferApi)` uses DI but policy imports transport. Better: `TransferRule(private val status: TransferStatusSource)` with a data adapter bound in Hilt or a manual composition root.

## Trade-offs and decision criteria

Hilt reduces manual graph wiring but adds generated code and Android setup. Manual DI can be enough for a small app. Neither approach excuses a poorly chosen abstraction or hidden service locator.

## Failure modes

A team celebrates replacing `Retrofit.create()` with Hilt constructor injection, yet the use case still handles HTTP codes and DTOs. The change improves construction but not policy isolation. Move mapping to data and inject a domain-facing contract.

## Production perspective

A marketplace uses Hilt to bind a pricing repository contract to an API-backed adapter, while domain tests manually pass a fake. The design can survive an adapter change and still be tested without Hilt.

## Interview answer — short

DIP is about which types high-level code depends on; DI is how an object receives its dependencies. Hilt can implement DI without achieving DIP, and a manual factory can support DIP.

## Interview answer — structured

I can inject a concrete Retrofit service into a use case with Hilt. That is dependency injection, but the use case still depends on a low-level transport detail, so DIP has not been achieved. To invert that boundary, I define a contract in domain terms and let the adapter implement it; Hilt or manual wiring then supplies the implementation. DI makes dependencies explicit and replaceable. DIP determines whether those dependencies point to stable policy or volatile mechanism. For example, a manual factory can construct `TransferRule(FakeStatusSource())` in a unit test and `TransferRule(NetworkStatusSource())` in production. The architecture is still inverted if the rule knows only the status contract. Adding Hilt later changes construction, not the policy boundary.

## Interview answer — deep senior

The distinction matters because teams often confuse a tool with an architecture. DI is the act of providing collaborators from outside rather than constructing them internally. It can be constructor injection, a manual composition root, or Hilt. DIP asks whether high-level business decisions reference abstractions that are independent of low-level transport or persistence. A generated Hilt graph can still connect a use case directly to `RetrofitService`, leaking HTTP concerns into policy. Conversely, a small app can manually construct an adapter for a clean domain contract and satisfy DIP. I review imports, module edges, and types crossing the interface, then use DI to wire the chosen design. Test fakes should represent the contract’s behavior, not just the framework’s calls. Hilt is valuable for managing graphs and scopes in a growing Android app, but it cannot assess whether an interface represents a truthful domain need. I inspect a use case’s imports and constructor types, not just annotations. If it depends on `RetrofitResponse`, generated DI code will faithfully wire a coupled design. I also verify that a singleton-bound adapter does not retain Activity context, because lifetime correctness is separate from DIP. A clear composition root plus tests of the boundary gives stronger evidence than simply counting injected parameters.

## Deep-dive talking points

Construct a Hilt-but-not-DIP example and a manual-DI-with-DIP example; inspect public types.

## Follow-up questions

- [SOL-06](../sol-06/): What does DIP require? **Answer:** high-level policy relies on stable abstractions.
- [DI-01](../di-01/): What does DI do? **Answer:** supplies dependencies externally and makes construction/replaceability explicit.

## Self-check rubric

Give one counterexample proving DI and DIP are independent, then repair the boundary.

## References and reviewed-on date

- [Android dependency injection](https://developer.android.com/training/dependency-injection) — injection mechanisms.
- [Robert C. Martin, A Little Architecture](https://blog.cleancoder.com/uncle-bob/2016/01/04/ALittleArchitecture.html) — inversion.

Technically reviewed against the linked primary design/language/Android guidance on 2026-10-11. Conceptual examples are not device-tested.
