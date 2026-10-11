---
id: "FLO-21"
question: "What is callbackFlow? What does awaitClose do?"
topic: "Flow, StateFlow, SharedFlow & Channels"
code: "FLO"
group: "B"
phase: 1
priority: "P1"
order: 134
editorial_status: "reviewed"
---

# FLO-21

## Original interview question

What is callbackFlow? What does awaitClose do?

## What the interviewer evaluates

Adapt multi-shot callback APIs with callbackFlow, awaitClose and channel capacity decisions.

## Explanation in Arabic

`callbackFlow` بيحوّل listener بيطلع قيم متعددة إلى cold Flow. كل collector يسجّل callback، و`trySend` ينقل القيم إلى channel بتاعة الـFlow. `awaitClose` يخلي block عايشة ويعمل unregister عند cancel أو close؛ من غيره listener ممكن يتسرب أو الـFlow تقفل فورًا. لازم نختار buffer/overflow يناسب هل كل update مهم.

## Why it matters and how it works

`callbackFlow` is thread-safe for callbacks arriving on other threads and can be collected repeatedly, so registration must be per collector. `awaitClose` cleanup must be idempotent and safe if registration fails. For one-shot callbacks, `suspendCancellableCoroutine` is usually simpler. Slow collectors may fill the channel; check `trySend` results or configure backpressure.

## Worked example

Conceptual Android-style listener API; `SensorApi` is an application interface, and callbackFlow needs coroutines-core.

```kotlin
import kotlinx.coroutines.channels.awaitClose
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.callbackFlow

interface SensorApi {
    fun add(listener: (Int) -> Unit)
    fun remove(listener: (Int) -> Unit)
}
fun SensorApi.values(): Flow<Int> = callbackFlow {
    val listener: (Int) -> Unit = { value -> trySend(value).isSuccess }
    add(listener)
    awaitClose { remove(listener) }
}
```

## Trade-offs and decision criteria

callbackFlow makes listener ownership explicit but each cold collector can register separately; shareIn may be needed for one hardware subscription. Buffering can absorb bursts but may drop or delay values; decide whether state snapshots or every sample matters.

## Failure modes

Forgetting awaitClose leaks a sensor listener. Ignoring a failed trySend can silently lose important samples. Unregistering a different callback instance fails to detach. Sharing the flow in an overly broad scope can leave sensors active offscreen.

## Production perspective

A location repository wraps SDK callbacks, unregisters on screen cancellation, and shares only within a session when two screens need it. It tests immediate callback, cancellation, error close and slow collector behavior; battery metrics confirm listener stops.

## Interview answer — short

“callbackFlow bridges a repeated callback into Flow; awaitClose keeps the channel alive and unregisters the listener on cancellation. I check send failures and capacity, and I share the cold source only when multiple collectors should use one registration.”

## Interview answer — structured

“I use `callbackFlow` for multi-shot listener APIs. On collection I register one callback, use `trySend` for values from arbitrary callback threads, and call `awaitClose` to unregister when the collector cancels or the channel closes. The block is cold, so two collectors may register twice. If one hardware subscription is desired, I share it in a suitable scope. I decide whether a slow collector may drop intermediate sensor snapshots or whether every sample needs durable capture. callbackFlow makes listener ownership explicit but each cold collector can register separately; shareIn may be needed for one hardware subscription. Buffering can absorb bursts but may drop or delay values; decide whether state snapshots or every sample matters. A location repository wraps SDK callbacks, unregisters on screen cancellation, and shares only within a session when two screens need it.”

## Interview answer — deep senior

“A callback adapter has lifecycle and backpressure contracts. `callbackFlow` supplies a channel-backed bridge safe for callbacks from other threads, but registration occurs per collection and the callback may race with closure. I make unregister idempotent, preserve the exact callback identity, and inspect the result of `trySend` rather than assuming delivery. `awaitClose` is essential to hold the registration and clean it up. If the SDK emits a single terminal result, `suspendCancellableCoroutine` is simpler; if it emits a stream, callbackFlow is appropriate. In Android I align the collection owner with UI visibility or a shared session, test late callbacks after cancellation, and monitor battery/resource use. `callbackFlow` is thread-safe for callbacks arriving on other threads and can be collected repeatedly, so registration must be per collector. `awaitClose` cleanup must be idempotent and safe if registration fails. For one-shot callbacks, `suspendCancellableCoroutine` is usually simpler. Slow collectors may fill the channel; check `trySend` results or configure backpressure. Forgetting awaitClose leaks a sensor listener. Ignoring a failed trySend can silently lose important samples. Unregistering a different callback instance fails to detach. Sharing the flow in an overly broad scope can leave sensors active offscreen. A location repository wraps SDK callbacks, unregisters on screen cancellation, and shares only within a session when two screens need it.”

## Deep-dive talking points

Cover per-collector registration, callback identity, send failure and cleanup races.

## Follow-up questions

- [COR-23](../cor-23/): Which adapter for one result? **Answer:** `suspendCancellableCoroutine`.
- [FLO-08](../flo-08/): How avoid duplicate listener registrations? **Answer:** share one cold callbackFlow under a suitable scope.

## Self-check rubric

Can I register/unregister reliably, handle failed sends and choose one-shot versus multi-shot?

## References and reviewed-on date

- [Kotlin callbackFlow API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/callback-flow.html) — channel bridge and awaitClose.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
