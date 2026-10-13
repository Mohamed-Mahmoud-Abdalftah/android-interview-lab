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

JVM callback adapter. `SensorSource` represents an app-owned wrapper whose register/unregister methods accept the **same listener instance** and are safe if cancellation races with registration. The `kotlinx-coroutines-core` dependency is required.
```kotlin
import kotlinx.coroutines.channels.awaitClose
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.callbackFlow

interface SensorSource {
    fun register(listener: (Int) -> Unit)
    fun unregister(listener: (Int) -> Unit)
}

fun sensorEvents(source: SensorSource): Flow<Int> = callbackFlow {
    val listener: (Int) -> Unit = { value -> trySend(value) }
    source.register(listener)
    awaitClose { source.unregister(listener) }
}
```
Each cold collector registers separately. A ViewModel can share this Flow with a deliberate owner; UI must collect with lifecycle awareness. Decide how to handle buffer overflow or dropped events for the actual sensor contract.

## Practical walkthrough

callback observer من Android SDK ممكن يتحول لـ`callbackFlow`: سجّل listener لما Flow تتcollect، استخدم `trySend`، و`awaitClose` تفصل listener وقت cancellation. لو SDK callback بتشتغل بعد unregister، تحقق من late event handling. `StateFlow` hot وتحتفظ بآخر value وتعمل equality conflation؛ LiveData lifecycle-aware في UI، لكن لا تخلط semantics. Flow العادية cold وممكن كل collector يسجل listener منفصل؛ استخدم `shareIn/stateIn` في owner مناسب لو عايز مصدر واحد. في Fragment اجمع بـviewLifecycleOwner `repeatOnLifecycle` عشان view القديمة ما تستقبلش events. اختبر تعدد collectors وrotation والbackground.

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

Observer describes a relationship, while Flow and LiveData provide particular delivery and lifecycle semantics. A callback source can be wrapped in `callbackFlow`, registering on collection and unregistering in `awaitClose`; each cold collector may create a separate registration. StateFlow is hot, holds a current value, and conflates equal values, so it fits ongoing UI state rather than a guaranteed exactly-once event queue. LiveData has built-in lifecycle awareness for its observers; a Flow collected by UI needs lifecycle-aware collection such as `repeatOnLifecycle`. In a location feature I decide who owns the upstream listener and whether sharing is appropriate. I test rotation, simultaneous collectors, cancellation and late callbacks so the adapter does not leak a view or sensor.

## How to answer in the interview

- **Why:** Delivery semantics and lifecycle determine whether observer wiring is safe.
- **How:** Bridge callback with `callbackFlow`/`awaitClose`, then choose Flow/StateFlow/LiveData.
- **Trade-off:** Cold collectors can duplicate registration; sharing changes ownership.
- **Failure case:** Listener leak or false exactly-once event assumption.
- **Production solution:** View-lifecycle collection and multi-collector/cancellation tests.

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

Technically reviewed against the linked primary publisher/language/Android guidance on 2026-10-13. Conceptual examples are not device-tested.
