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

Whether the candidate uses boundaries to control change and testing, rather than treating three folders as architecture.

## Explanation in Arabic

Clean Architecture فكرة لتنظيم dependency والـbusiness rules بحيث تفاصيل زي Retrofit وRoom وCompose تتغير من غير ما تغيّر قواعد المنتج في كل مكان. الـinner policy المفروض تعرف abstractions وdomain concepts، والـouter adapters تترجم network/database/UI. مش شرط عدد layers ثابت؛ Android guidance نفسها بتعتبر domain layer اختيارية لما complexity أو reuse تبررها. المهم إن direction واضح، errors mapped، والـuse cases قابلة للاختبار. مجرد package اسمها domain مع models فارغة مش فائدة.

### Practical walkthrough in Egyptian Arabic

لو شاشة الطلبات بتكلم Retrofit مباشرة وتخلط loading مع parsing، تغيير API سيكسر UI والاختبارات. افصل policy مثل “هل يسمح بإعادة المحاولة؟” عن تفاصيل HTTP، وخلي الحدود تعتمد للداخل. مش لازم 30 interface من أول يوم؛ ابدأ بالحدود التي تختلف أو تحتاج اختبار. بعد refactor اثبت إن سلوك offline/process death ما اتغيرش.

## Why it matters and how it works

Dependencies point toward stable policies in the classic model; runtime control can flow outward through interfaces implemented by adapters. Android guidance uses UI and data layers, with an optional domain layer. Repositories own data access and source-of-truth decisions; UI produces display state. Boundaries isolate changing frameworks and make tests cheaper when the problem is large enough.

## Worked example

Conceptual module sketch: `:feature:checkout` depends on `:core:domain` contracts, while `:core:data` implements those contracts and depends on Retrofit/Room. DI at the app composition root supplies the implementation. A simple `CheckoutRepository` interface belongs where its consumer can depend on it; mapping DTOs to domain outcomes happens at the data boundary. This is architecture, not a runnable snippet.

## Trade-offs and decision criteria

Extra boundaries and model conversions cost code and build maintenance. For a tiny app, a clear UI/data split and one repository may suffice. Introduce a domain layer when shared rules, multiple data sources, or complex workflows justify it.

## Failure modes

Failure: a supposedly “domain” UseCase imports `android.content.Context` and Retrofit DTOs, so framework churn still reaches policy code. Another failure is creating interfaces for every one-line class with no alternative or test seam. Review actual dependency graph, not folder names.

## Production perspective

A banking app keeps transfer limits and eligibility in testable policy code, maps server replies in data, and renders state in UI. An uncertain transfer remains pending until server reconciliation; layer boundaries do not create transaction authority.

## Interview answer — short

Clean Architecture separates stable business policy from changing UI and data mechanisms through dependency boundaries. It helps teams test rules and change adapters without sweeping edits. I apply it in proportion to complexity, not by mandating a fixed number of layers.

## Interview answer — structured

I start with what changes independently. UI rendering, network transport, persistence, and business decisions have different reasons to change. Clean Architecture puts stable policy toward the center and makes outer adapters depend on it, often through interfaces. In Android I usually keep a UI layer and data layer, adding a domain layer when rules are complex or reused. The benefit is focused tests and less coupling to frameworks. The cost is more mapping and abstractions, so I would not impose every layer on a small CRUD screen. For a transfer feature, I would keep eligibility rules independent of the network client and persistence schema. A repository adapter can translate those details into domain values, while the UI maps outcomes to display state. I would judge the design by whether a change stays local and whether rule tests run without Android.

## Interview answer — deep senior

A successful boundary survives a concrete change: replacing Retrofit, changing Room schema, or rebuilding a screen should not rewrite transfer eligibility rules. I examine the compile-time dependency graph and the public types crossing each boundary. DTOs and entities are adapter models; domain inputs and outcomes should be stable enough for business tests. Runtime calls can still travel through a repository implementation supplied by DI even though source dependencies point inward. I avoid dogma: Android guidance calls its domain layer optional, and a small app can remain maintainable with UI plus data. The senior question is whether added indirection pays for itself in isolated change, testability, and team ownership. A common failure is to create `domain` packages while allowing their signatures to return Retrofit responses or Room entities. The dependency graph may appear layered while policy still changes with external schema. I would inspect imports and public types, then write one integration test at the adapter and focused tests for rules. I would also be willing to collapse an unnecessary layer when a feature has no independent business policy; architecture should reduce change cost rather than advertise terminology.

## How to answer in the interview

- **Why:** separation protects policy from framework changes.
- **How:** draw boundary from UI to domain to data.
- **Trade-off:** clarity versus boilerplate.
- **Failure case:** architecture becomes folders with same coupling.
- **Production solution:** test important seams and evolve gradually.

## Deep-dive talking points

Trace one business rule as Retrofit, Room, and Compose change. Verify dependency direction, adapter mapping, optional domain choice, and the maintenance cost of extra layers.

## Follow-up questions

- [ARC-03](../arc-03/): Which direction do source dependencies point? **Answer:** toward stable inner policy/contracts; adapters implement outward details.
- [ARC-13](../arc-13/): Is domain always mandatory? **Answer:** no; add it when complexity or reuse justifies it.

## Self-check rubric

Award one point each for: stating the change-isolation goal; drawing inner/outer dependencies; naming a real adapter boundary; explaining optional domain; identifying a small-app overengineering case.

## References and reviewed-on date

- [Android architecture guide](https://developer.android.com/topic/architecture) — UI/data structure and principles.
- [Robert C. Martin, The Dependency Rule](https://www.informit.com/articles/article.aspx?p=2832399) — original inward source-dependency rule.
- [Android domain layer](https://developer.android.com/topic/architecture/domain-layer) — optional use cases.

Technically reviewed against the linked official Android architecture guidance on 2026-10-11. Conceptual flows and snippets are not device-tested.
