---
id: "FLO-29"
question: "A rapidly emitting upstream stream makes rendering slow. Which backpressure strategy fits?"
topic: "Flow, StateFlow, SharedFlow & Channels"
code: "FLO"
group: "C"
phase: 1
priority: "P1"
order: 142
editorial_status: "reviewed"
---

# FLO-29

## Original interview question

A rapidly emitting upstream stream makes rendering slow. Which backpressure strategy fits?

## What the interviewer evaluates

Choose backpressure strategy for a fast source and slow UI without dropping required records.

## Explanation in Arabic

لو upstream سريعة والرسم بطيء، نسأل الأول: كل emission مهمة ولا آخر snapshot بس؟ للـUI frame أو progress، `conflate` أو `collectLatest` ممكن يقلل شغل قديم؛ `buffer` يخلي المصدر يسبق ضمن capacity لكن ممكن يزيد latency. لو data لكل emission مهمة، نخزنها durable أو نعالجها بعقد backpressure، وما نسقطهاش عشان الرسم بطيء.

## Why it matters and how it works

Conflate drops intermediate values; collectLatest cancels previous processing; buffer queues within capacity and then applies backpressure. Throttle/sample can reduce render rate for telemetry, but their semantics differ and must be measured. Keep durable ingestion separate from lossy visualization.

## Worked example

JVM illustration; chart frames are replaceable snapshots. `draw` must cooperate with cancellation for collectLatest.

```kotlin
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.conflate
import kotlinx.coroutines.flow.collectLatest

suspend fun chart(frames: Flow<List<Float>>, draw: suspend (List<Float>) -> Unit) {
    frames.conflate().collectLatest { draw(it) }
}
```

## Trade-offs and decision criteria

Latest-only rendering improves responsiveness but skips intermediate visuals. Buffer preserves more data but costs memory and may show stale frames. A bounded sampling policy can cap CPU use; select it from UX and data-loss requirements.

## Failure modes

Applying conflate before persisting transaction events loses records. `collectLatest` may cancel local rendering but cannot undo a remote write. A huge buffer hides slowness until memory grows and the UI lags far behind.

## Production perspective

A real-time chart persists every sensor sample in a bounded ingestion pipeline, then exposes a separate latest-window Flow for UI drawing. Metrics record dropped visual frames, queue depth and render latency; tests use a fast fake producer.

## Interview answer — short

“I classify emissions first. For replaceable UI snapshots I may conflate or collectLatest; for values that must all be processed I use bounded buffering/backpressure or durable storage. I measure queue depth and latency.”

## Interview answer — structured

“A slow renderer should not dictate that business data is lost. If each value is a snapshot, `conflate` can skip intermediate emissions and `collectLatest` can cancel an old draw when a new frame arrives. `buffer` allows producer and consumer to overlap but still needs capacity and can increase display lag. If every record matters, I persist or process it with backpressure rather than dropping. I test a fast producer and slow collector and measure both frame freshness and dropped values.”

## Interview answer — deep senior

“I split data correctness from visualization. In a sensor app, raw samples may be legally or operationally important and go through a durable, bounded ingestion path. The chart is a derived latest-state view, so dropping intermediate frames is acceptable. `buffer` trades memory for throughput but can increase latency to what the user sees; `conflate` keeps the newest value; `collectLatest` cancels a running draw if it cooperates. I choose based on whether the render function has side effects, the maximum tolerable staleness and available memory. I instrument queue depth, render time and dropped-frame count, and test slow-device behavior rather than applying operators by habit.”

## Deep-dive talking points

Compare data ingestion with rendering; quantify stale latency, queue size and acceptable drops.

## Follow-up questions

- [FLO-16](../flo-16/): How does conflate differ from buffer? **Answer:** conflate drops intermediate values; buffer queues within capacity.
- [FLO-12](../flo-12/): What does collectLatest cancel? **Answer:** prior processing action.

## Self-check rubric

Can I classify emissions, choose an operator, protect required records and measure resource cost?

## References and reviewed-on date

- [Kotlin Flow API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-flow/) — buffering/conflation operators.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
