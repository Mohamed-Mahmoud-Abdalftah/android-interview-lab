---
id: "PAT-06"
question: "Where does Repository fit as an architectural/data-access pattern?"
topic: "Design Patterns"
code: "PAT"
group: "A"
phase: 2
priority: "P1"
order: 197
editorial_status: "reviewed"
---

# PAT-06

## Original interview question

Where does Repository fit as an architectural/data-access pattern?

## What the interviewer evaluates

Position Repository as data boundary, not a GoF catalog entry or a pure DAO alias.

## Explanation in Arabic

Repository pattern في Android data layer بتقدّم app data وتخفي sources: Room، network، cache. هي أقرب architectural/data-access pattern، مش واحدة من GoF 23. Repository ممكن تدير source of truth، sync، conflict، error mapping، وmain safety. مجرد class اسمها `UserRepository` تنادي `dao.getUser()` بنفس entity من غير contract ولا policy ممكن تكون wrapper بلا قيمة. ViewModel تعتمد على repository أو use case، مش DTO/DAO مباشرة. Offline-first DB تكون local source، لكن server يفضل authority لمعاملات حساسة.

## Why it matters and how it works

Repositories expose application data and centralize updates while abstracting data sources. They sit at a layer boundary and can contain data-centric business logic. Their value is consistent ownership, not merely a naming pattern.

## Worked example

Conceptual API: `observeOrders(): Flow<List<Order>>` reads Room; `refresh()` fetches and writes validated entities; `submit(requestId)` persists pending status and queries server outcome. UI observes the same local path. Room entity and Retrofit DTO stay internal.

## Trade-offs and decision criteria

A repository adds a boundary and testing seam; for tiny one-source features, a direct data-source wrapper may be enough but should still expose a stable app contract. Do not build one repository per method or hide unrelated workflows in one huge repository.

## Failure modes

One screen renders API DTOs while another reads Room entities, showing contradictory status. A repository should route both through a chosen source of truth. Another failure is treating a local `Paid` row as final server authorization.

## Production perspective

A delivery app uses a task repository to merge remote assignments into Room, preserve cached tasks offline, and expose freshness. Conflict rules and device tests cover reconnect.

## Interview answer — short

Repository is a data-access architecture pattern, not a GoF pattern. It exposes app data and coordinates sources, often including source-of-truth and refresh rules, so UI does not know Retrofit or Room details.

## Interview answer — structured

I use a repository when the app needs a stable way to obtain and update a kind of data. It may coordinate local database and network, map external models, and define how refresh affects observable state. Android guidance places repositories in the data layer. That is a broader data-boundary pattern than the GoF object patterns. I would not call a one-line DAO forwarder valuable merely because it is named Repository; its contract should hide actual data-source decisions or protect callers from schema churn.

## Interview answer — deep senior

The repository’s important responsibilities are consistency and ownership. For an offline-first feature I usually let a local database provide the observable stream, then write validated network refreshes into it so screens agree. The repository also reports refresh errors and staleness without discarding useful cached data. It maps DTOs and entities to app-facing models and makes expensive operations main-safe. This is not the same as a UseCase, which expresses a product action or reusable rule, nor is it a GoF pattern from the original catalog. A local cache remains only a display source for server-authoritative facts such as payment status; reconciliation is needed after uncertainty. I test races, process death and conflict policy rather than just DAO method forwarding.

## Deep-dive talking points

Distinguish repository from DAO and UseCase; explain local SSOT versus server authority.

## Follow-up questions

- [ARC-04](../arc-04/): Repository versus UseCase? **Answer:** data ownership/source coordination versus business action.
- [ARC-10](../arc-10/): What is SSOT? **Answer:** a defined authoritative owner for each app data type.

## Self-check rubric

Give two responsibilities beyond DAO forwarding and explain why Repository is not a GoF entry.

## References and reviewed-on date

- [Android data layer](https://developer.android.com/topic/architecture/data-layer) — repository responsibilities.
- [GoF pattern catalog](https://www.pearson.com/en-us/subject-catalog/p/design-patterns-elements-of-reusable-object-oriented-software/P200000009480/9780321700698) — original 23-pattern catalog.

Technically reviewed against the linked primary publisher/language/Android guidance on 2026-10-11. Conceptual examples are not device-tested.
