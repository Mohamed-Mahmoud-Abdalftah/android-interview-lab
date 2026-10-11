---
id: "FLO-01"
question: "What is Flow? Compare Flow and a single suspend function."
topic: "Flow, StateFlow, SharedFlow & Channels"
code: "FLO"
group: "A"
phase: 1
priority: "P1"
order: 114
editorial_status: "reviewed"
---

# FLO-01

## Original interview question

What is Flow? Compare Flow and a single suspend function.

## What the interviewer evaluates

Distinguish a stream of asynchronous values from a single suspend result, including collection lifetime.

## Explanation in Arabic

`Flow<T>` سلسلة قيم asynchronous بتطلع مع الوقت؛ `suspend fun ...: T` بترجع نتيجة واحدة أو error. Flow العادية غالبًا cold: الكود يبدأ مع `collect` وكل collector ممكن يشغّل المصدر من جديد. نستخدم suspend call لطلب profile واحد، وFlow لمتابعة تغييرات Room أو query مستمرة. الاتنين بيراعوا cancellation لكن stream يحتاج سياسة collection/lifecycle.

## Why it matters and how it works

Intermediate operators build a pipeline without starting a cold flow; a terminal operator such as `collect` or `first` starts it. Emission is sequential by default and completes or fails unless it is a hot never-ending subtype. A single suspending function can return a Flow, but its invocation alone need not start upstream work.

## Worked example

JVM example needs `kotlinx-coroutines-core`; it emits successive local snapshots, not a production database observer.

```kotlin
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow

suspend fun oneName(): String = "Mona"
fun names(): Flow<String> = flow {
    emit("Mona")
    emit("Mona Ali")
}
```

## Trade-offs and decision criteria

Use a suspend function for one response and Flow for values changing over time. A Flow adds collection lifetime and backpressure decisions; do not wrap one value in a stream solely for fashion. A hot StateFlow is useful when UI needs a current snapshot.

## Failure modes

Collecting a cold network Flow twice may make two network requests. Collecting indefinitely from UI without lifecycle awareness wastes work offscreen. A plain Flow is not automatically cached or shared.

## Production perspective

A repository exposes `suspend fun refresh()` to trigger one remote fetch and `Flow<List<Item>>` from Room for ongoing local truth. The ViewModel shares state appropriately; the UI collects only while active.

## Interview answer — short

“A suspend function returns one result; Flow represents a sequence of values over time. A cold Flow starts its upstream when collected, so multiple collectors can repeat work. I use it for changing data such as a Room table and collect with lifecycle awareness.”

## Interview answer — structured

“I pick the abstraction from the data contract. A one-shot API call is naturally a suspend function returning one value. A Flow can emit multiple snapshots and complete, or be shared as a hot state stream. Cold Flow intermediate operators are lazy; terminal collection starts work, and each collector may run upstream again. For an offline-first screen I expose Room rows as Flow and use a separate suspend refresh operation. I then share or collect it according to screen lifetime and avoid accidental duplicate network fetches.”

## Interview answer — deep senior

“Flow describes asynchronous stream behavior and context preservation, not automatic caching. Its ordinary cold pipeline executes on collection; map/filter are lazy and terminal operators trigger it. That gives a clean way to observe database changes and propagate cancellation, but two collectors can duplicate expensive upstream work unless `stateIn`/`shareIn` creates an explicitly scoped shared source. A suspend function is simpler for a single request/response. In Android I define whether the repository returns ongoing local state or a one-shot operation result, then choose ViewModel sharing and lifecycle-aware collection. I test repeated collectors, cancellation and upstream error handling rather than assuming Flow solves those choices.”

## Deep-dive talking points

Trace lazy operators, terminal collection, multiple collectors and the transition to a hot shared stream.

## Follow-up questions

- [FLO-02](../flo-02/): What does cold mean? **Answer:** each collector starts its own upstream execution unless shared.
- [FLO-08](../flo-08/): How share an expensive source? **Answer:** `stateIn` or `shareIn` with explicit scope and start policy.

## Self-check rubric

Can I choose single versus stream, identify a terminal operator, predict two collectors and name an Android lifecycle owner?

## References and reviewed-on date

- [Kotlin Flow API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-flow/) — cold pipelines and collection.
- [Android Flow guide](https://developer.android.com/kotlin/flow) — Android repository use.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
