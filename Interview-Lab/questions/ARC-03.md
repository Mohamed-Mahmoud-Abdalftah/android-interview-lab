---
id: "ARC-03"
question: "What is the Dependency Rule, and in which direction should dependencies point?"
topic: "Clean Architecture, MVVM, MVI & UDF"
code: "ARC"
group: "A"
phase: 2
priority: "P1"
order: 148
editorial_status: "reviewed"
---

# ARC-03

## Original interview question

What is the Dependency Rule, and in which direction should dependencies point?

## What the interviewer evaluates

Explain compile-time source dependencies versus runtime control flow and where interfaces are placed.

## Explanation in Arabic

Dependency Rule في Clean Architecture بتقول source-code dependencies تتجه ناحية policies الأكثر ثباتًا، مش ناحية UI/framework details. Domain ما يستوردش Retrofit DTO ولا `Activity`. لو domain محتاج data، يعرف contract مناسب له، وdata implementation تنفّذه؛ DI في composition root تربطهم. وقت التشغيل call ممكن يمشي من UI إلى use case إلى repository implementation ثم network، وده مش تناقض: source dependency direction غير runtime call direction. Android official architecture بتعرّف domain اختيارية، وفي رسمها الـdomain تعتمد على data repositories؛ ده اصطلاح مختلف عن Clean Architecture الكلاسيكية اللي بتحط policy contract جوّه. وضّح أي model بتستخدمه بدل ما تخلط الرسمين.

## Why it matters and how it works

Compile-time dependencies determine what must change/rebuild when a component changes. Dependency inversion lets a stable policy depend on an abstraction rather than a volatile adapter. The adapter depends on the policy contract and is supplied at runtime.

## Worked example

Conceptual Kotlin contract: `interface AccountRepository { suspend fun balance(id: AccountId): Balance }` in a stable module; `RoomAccountRepository` in data implements it. `GetBalanceUseCase` depends only on the interface. The app DI composition root binds the implementation. `Balance` is a domain value, not a Room entity.

## Trade-offs and decision criteria

Inversion has a cost: interface placement and wiring. For a small internal feature, a UI state holder depending on a concrete repository can still be acceptable if the dependency does not leak volatile types. Use interfaces where they isolate meaningful variation, not for every class.

## Failure modes

A domain contract returns `Response<AccountDto>`; although the interface lives in domain, the boundary still depends on Retrofit and server schema. Define domain-friendly inputs/outputs and map in the adapter. Avoid circular Gradle module dependencies created by placing contracts in the wrong module.

## Production perspective

A payment eligibility rule depends on a `PaymentStatusSource` contract. One adapter reads a backend API; tests use a deterministic fake. The server remains authoritative, and a new provider adapter does not force rule rewrites.

## Interview answer — short

The Dependency Rule says source dependencies point toward stable business policy. An outer adapter implements an inner contract, and DI supplies it. Runtime calls may go outward through that contract; that does not reverse the compile-time dependency.

## Interview answer — structured

I distinguish import direction from execution direction. A use case should not import Retrofit or Room just to obtain account data. It can depend on a domain-facing repository contract, with a data implementation that knows the transport and database. The app graph wires them together. At runtime the call reaches the implementation, but source code in the policy stays independent of those details. I add this inversion where it protects a real boundary; I do not create interfaces mechanically. One concrete check is to compile the domain module without Android, Retrofit, or Room dependencies. If it cannot compile, I inspect what leaked. The runtime implementation still performs I/O; the rule concerns source references and the direction in which changes propagate.

## Interview answer — deep senior

To audit the rule, I inspect module dependencies and the types in public signatures. A domain module that compiles without Android, Retrofit, or Room is a strong signal, but the contract must also use stable domain concepts. Returning `Response<Dto>` through a domain interface defeats the purpose. The implementation can map DTO and entity models to domain values, while DI resolves the implementation at runtime. If the app is small, Android guidance allows a direct UI-to-data dependency and optional domain layer. The practical objective is to keep high-change details from infecting stable rules and tests. I watch for circular Gradle dependencies and for interfaces placed with the implementation rather than the consumer abstraction needs. The interface should reflect the consumer’s needs rather than mirror every endpoint of the provider. For example, `ObserveAccountStatus` may be a better domain contract than a generic `ApiService` with HTTP details. I would test the policy with a fake contract and the adapter with real payload mappings. If the app is small, direct UI-to-repository use can be acceptable; the dependency rule becomes most valuable where stable policies need insulation from volatile mechanisms.

## Deep-dive talking points

Draw compile-time module arrows separately from runtime calls. Inspect a repository contract for leaked `Response<Dto>` and show how DI binds an adapter.

## Follow-up questions

- [ARC-06](../arc-06/): Why keep DTOs out of domain contracts? **Answer:** they encode transport schema and couple policy to an adapter.
- [SOL-06](../sol-06/): How does DIP relate? **Answer:** high-level policy depends on abstractions, not low-level concrete details.

## Self-check rubric

State the source dependency direction, show a domain-facing contract, explain runtime calls, and detect one transport type leaked through the boundary.

## References and reviewed-on date

- [Android architecture guide](https://developer.android.com/topic/architecture) — layer dependency guidance.
- [Robert C. Martin, The Dependency Rule](https://www.informit.com/articles/article.aspx?p=2832399) — original inward source-dependency rule.
- [Android domain layer](https://developer.android.com/topic/architecture/domain-layer) — optional intermediate layer.

Technically reviewed against the linked official Android architecture guidance on 2026-10-11. Conceptual flows and snippets are not device-tested.
