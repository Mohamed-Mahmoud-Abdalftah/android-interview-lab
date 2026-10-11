---
id: "SOL-14"
question: "How does Hilt support dependency wiring without automatically guaranteeing DIP?"
topic: "SOLID & Object-Oriented Design"
code: "SOL"
group: "B"
phase: 2
priority: "P1"
order: 185
editorial_status: "reviewed"
---

# SOL-14

## Original interview question

How does Hilt support dependency wiring without automatically guaranteeing DIP?

## What the interviewer evaluates

Separate Hilt construction from dependency inversion and inspect actual injected types.

## Explanation in Arabic

Hilt بتعمل object graph، scopes، bindings، وبتحقن dependencies بدل manual wiring. ده يساعد DI، لكن مش ضمان DIP: `@Inject constructor(api: RetrofitApi)` داخل `TransferUseCase` لسه high-level policy عارفة low-level transport. لو عايز DIP classic، خلى use case تعتمد على domain-facing `TransferStatusSource` وHilt `@Binds` تربط data adapter. Hilt لا تختار contract صح بدل المهندس؛ حتى `@Binds` لinterface بترجع DTOs مش عزل حقيقي.

## Why it matters and how it works

A DI container resolves constructors and lifetimes. Dependency inversion concerns direction and semantics of source dependencies. Hilt can implement a good graph or a tightly coupled graph equally well.

## Worked example

Conceptual binding: `@Binds abstract fun bindStatus(impl: NetworkStatusSource): TransferStatusSource`. The useful part is that `TransferStatusSource` exposes domain status, not Retrofit `Response`. A manual composition root could bind the same types.

## Trade-offs and decision criteria

Hilt reduces wiring cost and supports test replacement but adds annotation processing and lifecycle scopes. Manual DI may be enough for a small project. DIP may justify an interface even if Hilt can inject concrete classes.

## Failure modes

Use case is annotated with `@Inject` yet imports `RetrofitService`, parses HTTP status and handles JSON fields. Moving construction to Hilt changed wiring only. Extract a data adapter and domain contract, then test policy without Retrofit.

## Production perspective

A lending app uses Hilt to wire an eligibility rule to a repository abstraction. Production adapter fetches and caches status; JVM tests provide a fake contract. Server enforces final approval.

## Interview answer — short

Hilt supplies dependencies; it does not automatically choose the right dependency direction. A use case can be Hilt-injected and still depend on Retrofit. DIP requires a stable, domain-facing contract at the boundary.

## Interview answer — structured

I can use `@Inject` everywhere and still have a use case import a concrete API service. That is DI but not useful dependency inversion. Hilt builds the graph and scopes instances; engineers decide which contracts high-level policy should reference. I would give the use case a domain-facing interface and bind a data adapter with Hilt. The interface should return domain outcomes, not DTOs. I can test the use case with a fake without starting Hilt. I would also ask whether the bound interface returns domain values or simply exposes Retrofit response wrappers. A `@Binds` annotation cannot turn a transport-shaped contract into a stable policy API. The abstraction must be designed before Hilt wires it.

## Interview answer — deep senior

I inspect the graph from the use case outward. If high-level policy has a constructor parameter of `RetrofitTransferApi`, Hilt has made construction cleaner but left policy coupled to transport and HTTP errors. A good DIP boundary has a contract named for what the policy needs, with domain types and documented behavior. A data adapter implements it, and Hilt binds that implementation at app composition. The framework also manages scopes, but scope correctness is a separate question: a singleton should not capture Activity context. I do not require an interface for every helper simply because Hilt can bind it. Manual DI could provide the same inverted contract in a small app. The outcome is local change and tests that run without vendor SDKs, not a high count of annotations. There are separate failure modes to review: type coupling, scope, and graph correctness. A use case that imports Retrofit violates the intended DIP boundary even if Hilt resolves it perfectly. A Singleton adapter capturing Activity context may leak even if the abstraction direction is sound. A missing binding fails graph compilation. I use Hilt to make construction and replacement manageable, then review each boundary’s semantic types and lifetime. In unit tests I can instantiate the use case with a fake interface without Hilt, while instrumented tests verify the actual generated graph. That gives evidence for both design and wiring.

## Deep-dive talking points

Review a Hilt graph for injected concrete SDKs, leaked DTOs, binding direction and scope errors.

## Follow-up questions

- [SOL-07](../sol-07/): How do DIP and DI differ? **Answer:** policy dependency direction versus object wiring.
- [DI-04](../di-04/): What does `@Binds` do? **Answer:** binds an implementation to an abstract contract in the Hilt graph.

## Self-check rubric

Show one Hilt-injected DIP violation and repair it with a domain-facing contract.

## References and reviewed-on date

- [Android Hilt guide](https://developer.android.com/training/dependency-injection/hilt-android) — graph and bindings.
- [Robert C. Martin, A Little Architecture](https://blog.cleancoder.com/uncle-bob/2016/01/04/ALittleArchitecture.html) — dependency inversion.

Technically reviewed against the linked primary design/language/Android guidance on 2026-10-11. Conceptual examples are not device-tested.
