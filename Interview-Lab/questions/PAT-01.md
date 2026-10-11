---
id: "PAT-01"
question: "What is a design pattern, and how is it different from architecture?"
topic: "Design Patterns"
code: "PAT"
group: "A"
phase: 2
priority: "P1"
order: 192
editorial_status: "reviewed"
---

# PAT-01

## Original interview question

What is a design pattern, and how is it different from architecture?

## What the interviewer evaluates

Define pattern as reusable local design idea and distinguish it from system-level architecture and implementation recipe.

## Explanation in Arabic

Design pattern وصف متكرر لحل مشكلة design داخل context معين مع trade-offs، مش library أو كود جاهز تنسخه. Strategy مثلًا تنظّم variation في algorithm، بينما architecture تحدد حدود system ومسؤوليات modules وتدفّق data؛ Repository أقرب architectural/data-access pattern من GoF class pattern. نفس app تقدر تستخدم MVVM كتنظيم presentation وAdapter عند SDK boundary وObserver لstate. اسم pattern يساعد الفريق يتفاهم، لكن مايثبتش إن الحل صحيح أو مناسب؛ ابدأ بالمشكلة وبالمتطلبات.

## Why it matters and how it works

Patterns provide shared vocabulary for object collaboration; architecture sets larger boundaries, data flow and quality attributes. A pattern is applied within a context and can be combined with other patterns. The implementation must still honor lifecycle, concurrency and failure contracts.

## Worked example

Example: a checkout app uses a repository boundary to coordinate Room/network, a Strategy for multiple payment providers, and Adapter wrappers for SDK callback differences. Its architecture also defines UI/data modules, server authority and process-death recovery. These are different scales of decision.

## Trade-offs and decision criteria

A named pattern can speed review when the team shares its meaning. Forcing pattern classes into a simple feature adds indirection. Kotlin language features such as `object`, lambdas and delegation can implement the intent with less boilerplate.

## Failure modes

A team calls a global `object ApiManager` “Singleton pattern” and stores Activity plus token state in it. The name hides lifecycle leak and process-death fragility. Review ownership and invariants, not labels.

## Production perspective

A finance app uses an SDK adapter at data boundary while the app architecture keeps payment policy and server verification separate. Contract tests show whether swapping SDKs preserves behavior.

## Interview answer — short

A design pattern is a reusable solution shape for a recurring local design problem. Architecture describes the larger system boundaries and data flow. I use patterns as vocabulary only when they clarify a real problem and trade-off.

## Interview answer — structured

I start with the problem: do I need to vary an algorithm, adapt an API, or notify observers? A pattern names a tested collaboration shape for that context, but it is not a drop-in implementation. Architecture is broader: it decides layers, modules, source of truth, lifecycle and deployment boundaries. A checkout system can have MVVM and repository architecture while using Strategy and Adapter inside it. I would evaluate behavior and maintenance cost rather than reward a diagram for containing pattern names.

## Interview answer — deep senior

The useful difference is scale and responsibility. A GoF pattern such as Adapter explains a collaboration among objects; application architecture decides which module owns transport, how state reaches UI, and where server authority resides. Some patterns like Repository sit closer to an architectural/data boundary and are not one of the original GoF catalog entries. Kotlin may implement a pattern without formal class hierarchies: lambdas can stand in for simple strategies, `object` can express a singleton, and delegation can forward behavior. None of those syntactic conveniences solves lifecycle or thread safety. I would show the team the problem, proposed seam, failure behavior and tests before choosing a pattern. A named pattern is valuable when it makes change local and expectations clear, not when it creates ceremonial classes.

## Deep-dive talking points

Compare object collaboration with module boundaries, and identify Kotlin shorthand plus lifecycle caveats.

## Follow-up questions

- [PAT-02](../pat-02/): What kinds of GoF patterns exist? **Answer:** creational, structural, and behavioral.
- [PAT-06](../pat-06/): Is Repository a GoF pattern? **Answer:** no; it is a data-access/architectural boundary pattern.

## Self-check rubric

Define pattern and architecture at different scales and give one Android example of each.

## References and reviewed-on date

- [GoF Design Patterns, publisher](https://www.pearson.com/en-us/subject-catalog/p/design-patterns-elements-of-reusable-object-oriented-software/P200000009480/9780321700698) — original pattern catalog and categories.
- [Android architecture guide](https://developer.android.com/topic/architecture) — app-level boundaries.

Technically reviewed against the linked primary publisher/language/Android guidance on 2026-10-11. Conceptual examples are not device-tested.
