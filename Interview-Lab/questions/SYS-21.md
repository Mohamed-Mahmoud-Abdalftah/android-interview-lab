---
id: "SYS-21"
question: "Design a Home screen that relies on 3 independent services with partial failure."
topic: "Android System Design & Architecture Decisions"
code: "SYS"
group: "C"
phase: 4
priority: "P1"
order: 350
editorial_status: "reviewed"
---

# SYS-21

## Original interview question

Design a Home screen that relies on 3 independent services with partial failure.

## What the interviewer evaluates

Design Home with three independent services and partial failures without swallowing cancellation.

## Explanation in Arabic

Home عندها ثلاثة cards مستقلة؛ لو واحد فشل، نخلي الاتنين الناجحين ظاهرين مع error/retry على card الفاشلة. `supervisorScope` تعزل فشل الإخوة، وكل child ترجع typed outcome جوهها؛ `CancellationException` تترمي تاني علشان خروج الشاشة يلغي الكل. cached values لازم تتوسم freshness، وmonitoring تعرف أي service متعطلة؛ لو card أساسية للقرار، نغير policy بدل partial success عمياء.

## Why it matters and how it works

Start calls concurrently under a ViewModel-owned suspend operation, capture domain failures inside each child and await all. Parent cancellation still cancels supervised children. State model has per-card Loading/Ready/Error/Stale, and retries target only failed dependencies. Bound fan-out/timeouts per service.

## Worked example

Kotlin/JVM conceptual aggregator; services return independent strings and shared `outcome` preserves cancellation.

```kotlin
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.async
import kotlinx.coroutines.supervisorScope

suspend fun <T> outcome(call: suspend () -> T): Result<T> =
    try { Result.success(call()) }
    catch (e: CancellationException) { throw e }
    catch (e: Exception) { Result.failure(e) }
suspend fun home(a: suspend () -> String, b: suspend () -> String,
                 c: suspend () -> String) = supervisorScope {
    listOf(a, b, c).map { call -> async { outcome(call) } }.map { it.await() }
}
```

## Trade-offs and decision criteria

Partial success improves resilience but increases UI/error complexity and can hide a dependency outage unless measured. All-or-nothing is better if cards jointly form one valid quote. Cached fallback needs freshness label, not silent stale success.

## Failure modes

Using ordinary coroutineScope may cancel all three on one child failure. Bare runCatching can swallow cancellation. A failed card retried with an unbounded loop can overload service. Returning a Home success flag conceals partial outage.

## Production perspective

A commerce Home loads offers, order status and support tips independently, each with its own state and targeted retry. A server correlation ID and per-card metrics identify outages; process death rebuilds from cached Room snapshots.

## Interview answer — short

“I supervise the three independent calls, capture each domain failure inside its child, await all outcomes and render per-card state. Parent cancellation still stops the group, so I rethrow CancellationException.”

## Interview answer — structured

“Because these Home services are independent, I do not discard two useful cards when the third fails. I use a supervised scope and run three child requests concurrently, converting each expected error to its own typed result. Cancellation is different: leaving the screen cancels all children and must propagate. The ViewModel exposes loading, ready, stale and error state per card; retry targets only the failed dependency. I set timeouts and measure per-service failures so partial UI does not hide an outage.”

## Interview answer — deep senior

“The product semantics determine supervision. If three services contribute independent cards, partial success is valid; if they form a financial total, it is not. I run each under a ViewModel-owned operation, supervise direct children and catch domain exceptions inside each child, always rethrowing CancellationException. I await every result, attach freshness metadata to cached fallback and set per-service timeout/retry policy with bounded fan-out. The UI presents individual retry affordances rather than one global success flag. Telemetry reports dependency latency/failure separately. Tests fail each service in turn, cancel the parent mid-flight and verify no stale result appears after navigation. Parent cancellation still cancels supervised children. Bare runCatching can swallow cancellation.”

## Deep-dive talking points

Compare independent card semantics with all-or-nothing quote and test cancellation.

## Follow-up questions

- [COR-26](../cor-26/): How preserve partial results? **Answer:** supervisorScope plus per-child typed outcome.
- [SYS-11](../sys-11/): How choose timeout/retry? **Answer:** per-service policy with bounded attempts and cancellation.

## Self-check rubric

Can I show three outcomes, preserve cancellation and avoid masking an outage?

## References and reviewed-on date

- [Kotlin exception handling](https://kotlinlang.org/docs/exception-handling.html) — supervision.
- [Android UI architecture](https://developer.android.com/topic/architecture/ui-layer) — state holders.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
