---
id: "ARC-08"
question: "Compare MVC, MVP, MVVM, MVI, and UDF."
topic: "Clean Architecture, MVVM, MVI & UDF"
code: "ARC"
group: "A"
phase: 2
priority: "P1"
order: 153
editorial_status: "reviewed"
---

# ARC-08

## Original interview question

Compare MVC, MVP, MVVM, MVI, and UDF.

## What the interviewer evaluates

Compare responsibility for state and events across patterns without asserting one universal winner.

## Explanation in Arabic

MVC بيفصل model/view/controller لكن في Android القديم Activity كتير بقت controller ضخمة. MVP يخلي Presenter يتعامل مع View interface، يسهل بعض tests لكن wiring lifecycle يدوي. MVVM يستخدم ViewModel يعرض observable UI state والـView ترندر؛ Android lifecycle integration مناسب. MVI عادة intents/actions تدخل reducer لتولّد state موحدة وeffects واضحة، وUDF principle أوسع: events لأعلى وstate لأسفل. المصطلحات بتختلف بين الفرق؛ قيّم data flow، ownership، testability، وcomplexity بدل اختيار acronym.

### Practical walkthrough in Egyptian Arabic

MVC/MVP/MVVM/MVI/UDF أسماء لتنظيم ownership. في شاشة payment، الأهم state transitions وside effects وrecreation: هل Button tap ينتج event؟ هل Unknown محفوظ؟ هل UI تعمل request مباشرة؟ اختبر representative flow بدل تفضيل pattern بالاسم. MVVM مع immutable UiState قد يكفي، وreducer MVI يفيد transitions المعقدة بتكلفة ceremony.

## Why it matters and how it works

These patterns answer how presentation responsibilities and state transitions are organized. UDF is a directional principle that can be implemented within MVVM or MVI. Android guidance favors state holders and UDF, not a universal rigid MVI framework.

## Worked example

Conceptual comparison for Search: MVC Activity receives text, calls data and updates Views; MVP Presenter commands `SearchView`; MVVM ViewModel exposes `SearchUiState`; MVI reducer handles `QueryChanged` and emits a new state, with effects handled separately. In each, data access still belongs behind a repository.

## Trade-offs and decision criteria

MVI offers explicit transitions and time-travel-like testability for complex state but adds reducer/action boilerplate. MVVM is flexible and integrates naturally with Jetpack but can become ad hoc if state is scattered. MVP can isolate Views but requires manual view lifecycle handling.

## Failure modes

Calling an Activity “Controller” does not prevent a God Class. MVVM with multiple mutable booleans can permit impossible states. MVI with every keystroke as a heavyweight action can overcomplicate a simple form. Use explicit state and lifecycle-aware collection.

## Production perspective

A content feed may use MVVM with one immutable `FeedUiState`; checkout may use an explicit reducer/state machine for many transitions. Both follow UDF and keep payment authority on the server.

## Interview answer — short

MVC, MVP, MVVM, and MVI organize presentation responsibilities differently. UDF is the flow principle: events go toward the state holder and state returns to UI. I choose by state complexity and team cost, not acronym alone.

## Interview answer — structured

MVC often puts coordination in a controller, MVP uses a presenter and view contract, MVVM exposes observable state from a ViewModel, and MVI emphasizes intents, a reducer, and a single state model. UDF is broader and can exist in MVVM or MVI. On Android, ViewModel and lifecycle-aware state collection make MVVM practical. For a complex payment flow I may use an explicit reducer; for a simple feed a small ViewModel is enough. The key is predictable state ownership. For example, a feed with simple loading and content may need only one ViewModel and immutable state. A checkout with validation, submission, timeout and verification may benefit from reducer-style transitions. I would still keep data and business effects outside the reducer.

## Interview answer — deep senior

I compare these approaches by tracing one event through the system. Who receives it? Who applies business rules? Who owns current state? How does the UI render it after recreation? MVP makes View abstraction explicit but can require careful attach/detach behavior. MVVM gives a lifecycle-aware state holder but needs discipline to avoid scattered LiveData booleans. MVI or reducer-based UDF centralizes transitions and can make impossible states easier to detect, at the cost of more ceremony and effect handling. UDF itself simply asks for one-way event and state flow. I avoid claiming that a pattern name guarantees testability or correctness; I test actual transitions and separate durable business status from UI state. The names often overlap in practice, so I review the actual event and state flow. Does the UI render one source of state? Can a new event arrive while work is in flight? Is state restored after process death? MVP tests may fake a View contract, while MVVM tests can assert StateFlow and MVI tests can assert reducer transitions. None of these patterns automatically fixes stale cache, server authority or lifecycle leaks; those need explicit owners and tests.

## How to answer in the interview

- **Why:** pattern names do not prove correctness.
- **How:** compare ownership, state and effects.
- **Trade-off:** simple VM versus explicit reducer complexity.
- **Failure case:** pattern adopted but duplicate payment persists.
- **Production solution:** prototype difficult flow and measure.

## Deep-dive talking points

Trace a Search event through MVC, MVP, MVVM and reducer-style MVI. Separate UDF as a principle from a named framework; compare lifecycle and boilerplate costs.

## Follow-up questions

- [ARC-09](../arc-09/): Is UI state the domain state? **Answer:** no; UI state includes rendering and interaction details.
- [ARC-25](../arc-25/): When might MVI help payment flow? **Answer:** explicit transitions and exhaustive states can reduce scattered booleans.

## Self-check rubric

Explain who owns state in MVVM and MVI, how UDF flows, and why neither acronym alone guarantees testability.

## References and reviewed-on date

- [Android UI layer](https://developer.android.com/topic/architecture/ui-layer) — UDF and ViewModel.
- [Android state holders](https://developer.android.com/topic/architecture/ui-layer/stateholders) — UI state ownership.

Technically reviewed against the linked official Android architecture guidance on 2026-10-11. Conceptual flows and snippets are not device-tested.
