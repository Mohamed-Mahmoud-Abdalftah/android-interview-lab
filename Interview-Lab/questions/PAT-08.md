---
id: "PAT-08"
question: "Where do Singleton, Adapter, and Observer show up in Android?"
topic: "Design Patterns"
code: "PAT"
group: "B"
phase: 2
priority: "P1"
order: 199
editorial_status: "reviewed"
---

# PAT-08

## Original interview question

Where do Singleton, Adapter, and Observer show up in Android?

## What the interviewer evaluates

Identify Android examples while separating framework implementation details from pattern intent and lifecycle.

## Explanation in Arabic

Singleton مثالها Kotlin `object` أو Hilt `@Singleton` scope، لكن ده per running process/graph مش permanent state. Adapter يظهر لما تلف legacy callback SDK وتقدم suspend/domain API. Observer يظهر في LiveData وFlow-like streams للـUI state، لكن LiveData عندها lifecycle-aware observation وFlow لازم collection owner واضح. الثلاثة ممكن يشتغلوا معًا: singleton-scoped repository، adapter للخدمة، UI تلاحظ state. ما تخزنش Activity في singleton، وما تعتبرش observer event durable بعد process death.

## Why it matters and how it works

Android APIs often embody pattern intent but add lifecycle and process constraints. Recognizing the pattern helps choose a boundary, while the concrete API contract determines threading, replay, and lifetime.

## Worked example

Scenario: `object CurrencyFormatter` is stateless; `LegacyLocationAdapter` converts callback results; `ProfileViewModel.state: StateFlow<ProfileUiState>` is collected by a lifecycle-aware screen. The formatter is not a session store, and the state stream is not a payment event queue.

## Trade-offs and decision criteria

Using framework APIs can reduce custom pattern boilerplate. A hand-written singleton or observer registry may add leaks and concurrency hazards. Choose existing lifecycle-aware tools when they fit; still test delivery semantics.

## Failure modes

An Activity registers a custom observer on an application singleton and never unregisters, so old Activity remains reachable. Or a ViewModel collects a hot Flow beyond screen lifetime. Tie registration/collection to owner and test rotation.

## Production perspective

A delivery app wraps a vendor GPS callback API with an adapter, injects the repository at an appropriate scope, and exposes location state to UI with lifecycle-aware collection. It never treats cached location as authoritative delivery proof.

## Interview answer — short

Android uses singleton-like scoped objects, adapters for incompatible SDK APIs, and observer-style state APIs such as LiveData. I review lifecycle, process death and delivery semantics rather than assuming the pattern name guarantees safety.

## Interview answer — structured

A Kotlin `object` or Hilt singleton can hold one in-process instance, but it should not hold an Activity or be treated as durable storage. An Adapter can convert a callback SDK to a domain-facing interface. LiveData explicitly follows an observer pattern, and StateFlow can feed UI state with lifecycle-aware collection. Those are useful pattern examples, but Android adds recreation, cancellation and process death, so I choose the actual API and scope based on behavior.

## Interview answer — deep senior

In a production Android app, the three patterns often appear in one path. A data repository may be application-scoped for shared access, an adapter translates a vendor callback and normalizes errors, and a ViewModel exposes state observed by the screen. Each boundary has different lifetime. A singleton-like object is only one per process or DI graph, so it cannot be the sole store for a login session. A callback adapter must unregister or cancel with its owner, and UI observers should stop with the lifecycle. LiveData supplies lifecycle-aware observation; Flow/StateFlow need explicit collection strategy. I test rotation, process recreation, duplicate callbacks and stale results, rather than relying on GoF labels to imply those guarantees.

## Deep-dive talking points

Map object scope, SDK adaptation and observation; distinguish LiveData/Flow lifecycle behavior.

## Follow-up questions

- [PAT-17](../pat-17/): Why can a global singleton harm tests? **Answer:** shared mutable state survives between test cases in one process.
- [PAT-13](../pat-13/): How do observers relate to Flow? **Answer:** both propagate updates, but collection and lifecycle contracts differ.

## Self-check rubric

Give one Android example of each pattern and one lifecycle failure for Singleton or Observer.

## References and reviewed-on date

- [Kotlin object declarations](https://kotlinlang.org/docs/object-declarations.html) — object lifetime syntax.
- [Android LiveData overview](https://developer.android.com/topic/libraries/architecture/livedata) — observer behavior.

Technically reviewed against the linked primary publisher/language/Android guidance on 2026-10-11. Conceptual examples are not device-tested.
