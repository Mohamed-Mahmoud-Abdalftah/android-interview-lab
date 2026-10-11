---
id: "COR-22"
question: "When should you use ensureActive or yield during CPU-bound work?"
topic: "Kotlin Coroutines & Concurrency"
code: "COR"
group: "B"
phase: 1
priority: "P1"
order: 103
editorial_status: "reviewed"
---

# COR-22

## Original interview question

When should you use ensureActive or yield during CPU-bound work?

## What the interviewer evaluates

Explain cancellation responsiveness in CPU loops and the scheduling distinction between ensureActive and yield.

## Explanation in Arabic

لو coroutine بتعمل CPU loop طويل من غير suspension، إلغاء الـJob مش هيوقفها فورًا. `ensureActive()` بتفحص حالة الـJob وترمي `CancellationException` لو اتلغى؛ `yield()` بتفحص وبتدي فرصة لغيرها تتنفذ. نحط checks كل كمية عمل مناسبة بدل كل instruction، ونقيس latency الفعلية للإلغاء.

## Why it matters and how it works

Ordinary CPU code does not hit cancellable suspension automatically. `ensureActive` is a cheap explicit check; `yield` adds a scheduling point and fairness opportunity. Neither makes non-cooperative native calls cancellable. Avoid running the loop on Main; use an appropriate CPU dispatcher and bounded work.

## Worked example

JVM illustration assumes `kotlinx-coroutines-core`; chunk size is an example to tune by profiling.

```kotlin
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.currentCoroutineContext
import kotlinx.coroutines.ensureActive
import kotlinx.coroutines.withContext

suspend fun score(rows: List<Int>): Long = withContext(Dispatchers.Default) {
    var total = 0L
    rows.forEachIndexed { index, value ->
        if (index % 512 == 0) currentCoroutineContext().ensureActive()
        total += value.toLong() * value
    }
    total
}
```

## Trade-offs and decision criteria

`ensureActive` suits cancellation-only checks; `yield` may improve fairness when many tasks share a dispatcher but adds scheduling overhead. Offload CPU work from Main, but cap large parallel searches so they do not saturate every core and starve rendering-adjacent work.

## Failure modes

A tight image-processing loop on Main causes jank and ignores screen cancellation. Checking only after the whole batch is too late. Using `yield` every iteration can spend disproportionate time rescheduling.

## Production perspective

A gallery indexer processes images in chunks on Default and checks cancellation at chunk boundaries. When the user changes filters, old indexing stops promptly. Benchmarks track throughput and worst-case cancellation latency.

## Interview answer — short

“CPU loops need explicit cooperative cancellation checks. `ensureActive` throws when the Job is cancelled; `yield` also offers a scheduling opportunity. I check at measured chunk boundaries on a CPU dispatcher.”

## Interview answer — structured

“Suspending functions often observe cancellation, but a pure CPU loop may not suspend for a long time. I insert `ensureActive` periodically so a cancelled screen request stops, or `yield` when fairness with other coroutines matters. I run heavy work on Default rather than Main. The check frequency is a performance trade-off: too sparse gives slow cancellation, too frequent adds overhead. I test both throughput and cancellation latency with realistic input sizes.”

## Interview answer — deep senior

“I would choose an explicit cancellation budget. A CPU-bound parser can run millions of instructions without a suspension point, so cancelling its Job only sets state until it checks. `ensureActive` observes that state and throws; `yield` does that plus a dispatch opportunity, useful if one coroutine monopolizes a thread. I process bounded chunks on Default, check between chunks and avoid shared mutable state without synchronization. A native decoder or synchronous SDK may require its own stop mechanism; these helpers cannot interrupt arbitrary code inside it. In production I measure cancellation response under load and make sure a stale result is not published even if the last chunk completes near cancellation.”

## Deep-dive talking points

Contrast checks, fairness, dispatcher choice and uncooperative library calls.

## Follow-up questions

- [COR-10](../cor-10/): Why is cancellation cooperative? **Answer:** the running code must reach a cancellable suspension or explicit check.
- [COR-29](../cor-29/): Can `yield` cancel a blocking SDK call? **Answer:** no, it cannot execute until that call returns.

## Self-check rubric

Can I place a check, justify frequency, choose Default, and state the limitation for blocking native code?

## References and reviewed-on date

- [Kotlin cancellation guidance](https://kotlinlang.org/docs/cancellation-and-timeouts.html) — cooperative checks.
- [Kotlin coroutines basics](https://kotlinlang.org/docs/coroutines-basics.html) — dispatchers.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
