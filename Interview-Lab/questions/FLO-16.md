---
id: "FLO-16"
question: "Compare merge, buffer, conflate, and collectLatest."
topic: "Flow, StateFlow, SharedFlow & Channels"
code: "FLO"
group: "B"
phase: 1
priority: "P1"
order: 129
editorial_status: "reviewed"
---

# FLO-16

## Original interview question

Compare merge, buffer, conflate, and collectLatest.

## What the interviewer evaluates

Distinguish fan-in, queued buffering, dropped intermediate values and cancellation of old processing.

## Explanation in Arabic

`merge` يجمع عدة flows في stream واحدة وemissions ممكن تتداخل. `buffer` يفصل producer عن collector بقناة buffer لكن لا يعني إسقاط القيم افتراضيًا. `conflate` يحتفظ بالأحدث لما المستهلك بطيء ويسقط intermediates. `collectLatest` يلغي شغل معالجة القيمة السابقة عند وصول أحدث. اختيار الإسقاط أو الإلغاء لازم يبقى آمن لنوع البيانات.

## Why it matters and how it works

Merge combines concurrent sources, while buffer, conflate and collectLatest address producer/consumer speed differently. Buffer allows upstream to get ahead within capacity; conflate skips intermediate elements; collectLatest cancels an in-progress collector action. None makes a blocking action cooperatively cancellable by itself.

## Worked example

JVM illustration; UI rendering is replaceable work, so latest-only processing is acceptable.

```kotlin
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.flow.conflate
import kotlinx.coroutines.flow.merge

suspend fun render(
    a: Flow<String>, b: Flow<String>, show: suspend (String) -> Unit,
) { merge(a, b).conflate().collectLatest { show(it) } }
```

## Trade-offs and decision criteria

Conflate and collectLatest reduce stale UI work but lose intermediate processing; unsafe for audit logs or payments. Buffer preserves more values at a memory/latency cost and can still backpressure when full. Merge loses global source order unless IDs/timestamps are carried.

## Failure modes

A payment event stream passed through conflate could silently drop a charge notification. `collectLatest` around a remote write may cancel observation while the write commits. An unbounded producer with buffer can still overload memory without capacity limits.

## Production perspective

A telemetry chart merges two sensor streams and shows only the latest visual frame; raw measurements are persisted separately. UI render path may conflate, while the durable ingestion path preserves every record with backpressure.

## Interview answer — short

“merge combines streams, buffer queues ahead, conflate skips intermediate values, and collectLatest cancels old processing. I use dropping only when the latest snapshot is sufficient, never for required business events.”

## Interview answer — structured

“These operators solve different problems. `merge` fans multiple sources into one concurrent stream. `buffer` decouples upstream and downstream within bounded capacity, typically preserving emitted values until capacity/backpressure applies. `conflate` lets a slow consumer skip intermediate values. `collectLatest` cancels its prior action when a new value arrives. For a UI progress graph, dropping stale frames is fine. For transaction or audit records it is not; those need durable ingestion and explicit acknowledgement.”

## Interview answer — deep senior

“I start by defining whether each emission is a state snapshot or an irreplaceable occurrence. Merge gives no single total order across sources, so I include source IDs and timestamps when order matters. Buffer can improve throughput by overlapping stages but needs a capacity/memory policy; it is not magical infinite storage. Conflate intentionally loses intermediate values, and collectLatest intentionally abandons prior processing if it cooperates. A blocking or remote side effect may still finish despite cancellation. In production I separate a durable event capture pipeline from a lossy UI render pipeline, measure queue depth and dropped-frame counts, and test a fast producer with a slow consumer to prove the selected behavior.”

## Deep-dive talking points

Draw a fast-producer/slow-consumer timeline and classify which emissions can be dropped.

## Follow-up questions

- [FLO-12](../flo-12/): What does collectLatest cancel? **Answer:** the previous collector action.
- [FLO-29](../flo-29/): Which strategy fits slow rendering? **Answer:** latest-only visual state, while durable data is preserved separately.

## Self-check rubric

Can I distinguish queue, drop and cancel; state when each is unsafe; and choose a bounded resource policy?

## References and reviewed-on date

- [Kotlin Flow API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-flow/) — buffer/conflate/merge behavior.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
