---
id: "PAT-13"
question: "How do callback/lifecycle observers relate to Flow and LiveData?"
topic: "Design Patterns"
code: "PAT"
group: "B"
phase: 2
priority: "P1"
order: 204
editorial_status: "reviewed"
---

# PAT-13

## Original interview question

How do callback/lifecycle observers relate to Flow and LiveData?

## What the interviewer evaluates

Relate observer intent to callback APIs, Flow and LiveData while specifying lifecycle, replay and delivery.

## Explanation in Arabic

Observer pattern: source عندها subscribers وبتبلغهم بالتغيرات. Android callbacks شكل من ده، LiveData lifecycle-aware وتوقف notifications للinactive owners، وFlow cold عادة يبدأ producer لكل collector، بينما StateFlow hot وعندها latest value؛ مش كلهم نفس delivery contract. `callbackFlow` تقدر تلف listener وتعمل `awaitClose { removeListener }` عشان ما تسرّبش Activity. UI تجمع Flow بـlifecycle-aware APIs. لو event لازم ما يضيعش بعد process death، observer in-memory غير كافي؛ استخدم persisted state/acknowledgement.

## Why it matters and how it works

Observable APIs differ in lifecycle activation, hot/cold behavior, replay and backpressure. The pattern describes notification relationships, but the concrete stream contract decides correctness in Android.

## Worked example

Conceptual callback-to-Flow adapter requires `kotlinx.coroutines.flow.callbackFlow` and `awaitClose`: register listener on collection, `trySend` updates, unregister in `awaitClose`. A ViewModel can convert to `StateFlow`; Compose collects with lifecycle. Implementation must handle callback thread and close semantics.

## Trade-offs and decision criteria

LiveData integrates with Android Lifecycle but is Android-specific. Flow supports rich operators and explicit collection; StateFlow models current state. Use an event mechanism only after defining replay/loss requirements, not because “Observer” sounds suitable.

## Failure modes

A `callbackFlow` forgets `awaitClose`, leaving the vendor listener active after collection ends. Or UI collects a hot stream in an unowned scope, wasting work and leaking references. Test cancellation and rotation.

## Production perspective

A sensor screen wraps callback API into a Flow with unregister on cancellation, exposes throttled state, and collects only when visible. A critical safety event is persisted separately if it must survive process death.

## Interview answer — short

Callbacks, LiveData and Flow can all express observer-style updates, but their lifecycle, hot/cold and replay behavior differ. I choose the concrete API by state-versus-event needs and ensure listener cleanup.

## Interview answer — structured

Observer describes a source notifying interested consumers. Android LiveData implements lifecycle-aware observation; a Flow can model a callback source, but a cold Flow starts work per collector and StateFlow retains the latest state. When wrapping a listener, I register and unregister with `callbackFlow` and `awaitClose`. UI collects with its lifecycle to avoid work after the screen stops. For a business event that cannot be lost, I persist it; an in-memory observer stream is not a durable queue.

## Interview answer — deep senior

The design question is delivery, not merely whether an observer exists. A callback may invoke on an arbitrary thread and may outlive an Activity; a correct adapter owns registration and removal. `callbackFlow` bridges that lifecycle, but buffering and cancellation still need decisions. LiveData knows Android lifecycle; Flow is more general and needs a lifecycle-aware collection point for UI. StateFlow is hot and conflates current state, so it is appropriate for renderable snapshots but not an audit trail of every event. A critical action should be represented in persistent data and acknowledged, because process death can erase in-memory emissions. I test multiple collectors, rotation, cancellation and duplicate callbacks.

## Deep-dive talking points

Compare callback registration, LiveData active owners, cold Flow, hot StateFlow and durable events.

## Follow-up questions

- [PAT-05](../pat-05/): Is Observer a guarantee of delivery? **Answer:** no; concrete stream lifecycle and replay policy determine it.
- [FLO-06](../flo-06/): What does StateFlow conflate? **Answer:** intermediate equal/latest state updates, so it is not an event log.

## Self-check rubric

Explain three observable APIs, show listener cleanup, and identify one event that needs persistence.

## References and reviewed-on date

- [Android LiveData overview](https://developer.android.com/topic/libraries/architecture/livedata) — observer lifecycle.
- [Kotlin callbackFlow API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/callback-flow.html) — callback adaptation and `awaitClose`.

Technically reviewed against the linked primary publisher/language/Android guidance on 2026-10-11. Conceptual examples are not device-tested.
