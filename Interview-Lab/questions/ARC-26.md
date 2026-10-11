---
id: "ARC-26"
question: "How do you enforce boundaries without a huge number of boilerplate interfaces?"
topic: "Clean Architecture, MVVM, MVI & UDF"
code: "ARC"
group: "C"
phase: 2
priority: "P1"
order: 171
editorial_status: "reviewed"
---

# ARC-26

## Original interview question

How do you enforce boundaries without a huge number of boilerplate interfaces?

## What the interviewer evaluates

Enforce meaningful dependencies with modules, visibility and tests while minimizing ceremonial contracts.

## Explanation in Arabic

Boundary يعني قرار مين يعرف مين، مش عدد interfaces. في app متوسطة، Gradle modules تقدر تمنع `feature:ui` من استيراد Retrofit أو data implementation؛ `internal` يحدّ surface، وarchitecture tests/static checks تراقب imports. اعمل interfaces ضيقة عند seams حقيقية: domain policy محتاجة repository contract، أو provider متعدد. Concrete class داخل feature واحد ممكن يفضل concrete وتحقنه Hilt عادي. استخدم DTO/domain mapping لما contract مختلف، لكن ما تخلقش `FooApi/FooImpl/FooUseCase` لكل سطر. راجع dependency graph في CI وعالج violations بأمثلة حقيقية.

## Why it matters and how it works

Boundaries are compile-time dependency rules and stable API contracts. Gradle module edges, visibility, lint/architecture checks and review can enforce them. Interfaces are one tool, not the only enforcement mechanism.

## Worked example

Conceptual graph: `:feature:search` depends on `:core:model` and `:core:data-api`; `:data:search` implements the API and depends on Retrofit/Room; `:app` wires them. A pure `SearchFormatter` remains concrete and `internal` in its feature. CI checks that UI modules do not depend on Retrofit.

## Trade-offs and decision criteria

Modules and checks add build/configuration cost; too many tiny modules slow navigation. Package conventions are lightweight but not hard enforcement. Choose a few real boundaries, measure build and change locality, and expand only when leakage appears.

## Failure modes

A project has one interface per class but UI module still imports DTOs through those interfaces: boundary failed. Another has perfect packages but no module rules, so a new direct DAO call compiles. Test source dependencies and public types, not naming conventions.

## Production perspective

A growing marketplace keeps feature modules independent, core contracts small, and data adapters replaceable. Architecture tests catch forbidden imports, while reviews challenge new interfaces that have no consumer need.

## Interview answer — short

I enforce boundaries with module dependencies, visibility and architecture checks, and introduce narrow interfaces only at real variation or policy seams. Boilerplate interface count is not evidence of decoupling.

## Interview answer — structured

First I draw the allowed dependency graph. Gradle modules can prevent UI from importing data implementations, `internal` keeps helper APIs local, and automated architecture checks catch forbidden imports. I use a repository interface when domain policy needs a stable contract or there are multiple implementations. A small pure formatter can remain concrete and directly tested. I also inspect public types so a `Response<Dto>` does not leak through a supposedly clean boundary. For example, I can make a UI module unable to depend on Retrofit, keep data implementations `internal`, and expose one narrow repository contract. A simple formatter remains concrete and tested directly. That enforces a real boundary with fewer files than an interface-per-class rule.

## Interview answer — deep senior

A boundary must survive an implementation change and be enforced by the build, not just a package name. I use a small number of Gradle modules around features and volatile adapters, with explicit allowed edges and narrow shared contracts. Kotlin visibility limits accidental public API growth; lint or architecture tests catch prohibited dependencies such as Compose importing Retrofit DTOs. Interfaces are reserved for genuine consumer contracts, provider variation, or test substitution at important seams. A one-to-one interface per class adds navigation cost while leaving coupling untouched if types still leak. I periodically review build time, module graph, and change locality to see whether the structure pays for itself. For a small app, a documented UI/data split and a few checks may be enough; for a larger team, stronger module enforcement becomes valuable. I would audit the graph in CI, but also inspect the types that cross it. A domain-facing interface returning `Response<Dto>` is still coupled to transport even if Gradle edges look clean. I add contracts only where a consumer needs independent variation or a test seam, and I review whether shared modules are growing into catch-all dependencies. Architecture checks, visibility and focused tests give stronger evidence than naming conventions. As team and feature count change, I revisit module granularity and measure build and navigation cost.

## Deep-dive talking points

Audit module graph, exported types, `internal` helpers, interface necessity and CI architecture checks.

## Follow-up questions

- [ARC-03](../arc-03/): What should the dependency graph enforce? **Answer:** source dependencies toward stable contracts/policy.
- [ARC-15](../arc-15/): When is a concrete class enough? **Answer:** when no independent variation or stable boundary is needed.

## Self-check rubric

Design an allowed module graph and identify one meaningful interface and one avoidable interface.

## References and reviewed-on date

- [Android modularization guide](https://developer.android.com/topic/modularization) — module boundaries.
- [Android architecture recommendations](https://developer.android.com/topic/architecture/recommendations) — adaptable architecture practices.

Technically reviewed against the linked official Android guidance on 2026-10-11. Conceptual examples are not device-tested.
