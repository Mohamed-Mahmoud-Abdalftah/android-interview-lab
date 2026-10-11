---
id: "PAT-09"
question: "Compare State and Strategy with concrete examples."
topic: "Design Patterns"
code: "PAT"
group: "B"
phase: 2
priority: "P1"
order: 200
editorial_status: "reviewed"
---

# PAT-09

## Original interview question

Compare State and Strategy with concrete examples.

## What the interviewer evaluates

Contrast interchangeable algorithm selection with behavior governed by current state and transitions.

## Explanation in Arabic

Strategy بتختار behavior/algorithm مستقل بناءً على config أو context: card vs wallet provider، أو compression algorithm. State pattern بيغيّر behavior لأن object في state معينة وانتقالاتها: checkout `Idle -> Submitting -> PendingVerification -> Confirmed`. الاتنين ممكن يستخدموا interface وpolymorphism، لكن “ليه السلوك اتغيّر؟” هو الفرق. Strategy غالبًا caller يختارها، State يغيّرها transition داخل state machine. في payments provider strategy ما يقررّش إن transaction نجحت؛ server status يحرك state.

## Why it matters and how it works

Strategy encapsulates interchangeable policies; State encapsulates behavior that varies with an object’s lifecycle state. Similar class diagrams can hide distinct ownership and transition requirements.

## Worked example

Conceptual example: `PaymentStrategy.submit()` has card/wallet implementations. `CheckoutState` sealed cases determine whether Submit is legal and how timeout is represented. A reducer updates state; a selected strategy performs the provider request.

## Trade-offs and decision criteria

An explicit `when` can be simpler than either pattern for a few stable cases. A State pattern or reducer helps when transitions multiply. Strategy helps when independently replaceable algorithms exist. Avoid provider selection logic scattered through state classes.

## Failure modes

A timeout is handled by strategy as final failure and state immediately returns to Idle, allowing duplicate charge. Represent uncertainty as pending verification and reconcile with server; keep strategy result semantics consistent.

## Production perspective

A checkout ViewModel uses a reducer for state transitions and a gateway strategy for provider variation, with persisted request ID. Contract tests cover all providers and transition tests cover late confirmation.

## Interview answer — short

Strategy varies an algorithm or provider selected for a task; State varies behavior according to current lifecycle state and transitions. A payment provider strategy and checkout state machine can coexist.

## Interview answer — structured

I use Strategy when multiple implementations of one operation should be interchangeable, for example card and wallet SDK adapters. I use State when permitted behavior depends on where an object is in a lifecycle, such as Idle, Submitting or PendingVerification. Their class diagrams can look alike, but the reason for change differs. In checkout, a selected strategy performs the request; a state machine decides whether submit is legal and how results update UI. Server confirmation remains authoritative.

## Interview answer — deep senior

The distinguishing question is who selects the behavior and why. A Strategy is often supplied by configuration, DI or a router to perform one operation; it can usually be changed without implying an internal transition. State is tied to the object’s history and legal transitions. A checkout in `Submitting` rejects duplicate taps, while `PendingVerification` waits for server status after a timeout. One of several payment strategies may execute the request from that state. I test strategies for common outcome semantics and the state machine for transition legality, process-death restoration and late responses. If the flow has only two cases, a clear conditional may be easier than a hierarchy.

## Deep-dive talking points

Draw two axes—provider choice and checkout lifecycle—and test each independently.

## Follow-up questions

- [PAT-05](../pat-05/): Which family contains both? **Answer:** behavioral patterns with different intent.
- [ARC-25](../arc-25/): Why explicit payment state? **Answer:** it prevents invalid transitions and represents uncertainty.

## Self-check rubric

State who selects Strategy, what changes State, and model a timeout without declaring failure.

## References and reviewed-on date

- [GoF Design Patterns, publisher](https://www.pearson.com/en-us/subject-catalog/p/design-patterns-elements-of-reusable-object-oriented-software/P200000009480/9780321700698) — original Strategy and State patterns.
- [Android UI state guidance](https://developer.android.com/topic/architecture/ui-layer/stateholders) — screen state modeling.

Technically reviewed against the linked primary publisher/language/Android guidance on 2026-10-11. Conceptual examples are not device-tested.
