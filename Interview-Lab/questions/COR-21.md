---
id: "COR-21"
question: "What is a semaphore? How do you limit parallelism?"
topic: "Kotlin Coroutines & Concurrency"
code: "COR"
group: "B"
phase: 1
priority: "P1"
order: 102
editorial_status: "reviewed"
---

# COR-21

## Original interview question

What is a semaphore? How do you limit parallelism?

## What the interviewer evaluates

Explain permit accounting and how to limit active operations separately from dispatcher choice.

## Explanation in Arabic

`Semaphore` عنده عدد permits؛ coroutine بتستنى permit قبل دخول عملية وتفرجها في `finally`/`withPermit`. ده بيحدّد عدد requests المتزامنة مثلًا، لكنه مش بيحدد thread بعينه. `Dispatchers.IO` ممكن يشغّل blocking calls كتير، لكن السيرفر والاتصالات والذاكرة عندهم حدود مختلفة؛ semaphore بتحمي الموارد دي.

## Why it matters and how it works

`withPermit` acquires cancellably and releases when the block exits, including failure. Scope the semaphore to the shared resource, not per request, or every call gets a fresh full quota. Use bounded queues and timeouts when callers can accumulate indefinitely.

## Worked example

JVM/Android-compatible snippet; all calls share one limiter instance and `fetch` is cancellable.

```kotlin
import kotlinx.coroutines.sync.Semaphore
import kotlinx.coroutines.sync.withPermit

class LimitedApi(private val fetch: suspend (String) -> String) {
    private val permits = Semaphore(3)
    suspend fun get(id: String): String = permits.withPermit { fetch(id) }
}
```

## Trade-offs and decision criteria

Use semaphore for a bounded number of in-flight operations; `limitedParallelism` can limit dispatcher execution but is not identical to an end-to-end API permit. Too few permits raise latency; too many overload dependencies. Observe queue wait and server responses.

## Failure modes

Constructing `Semaphore(3)` inside each `get` call limits nothing globally. Manually acquiring without `finally` can leak a permit after exception and stall all later requests. Permit limits alone do not prevent a huge waiting queue.

## Production perspective

A media repository limits concurrent thumbnail downloads to three per host while allowing UI cancellation. Metrics separate wait time, network time and server throttling. A bounded producer prevents thousands of queued offscreen requests.

## Interview answer — short

“A semaphore limits how many operations hold permits at once. I share it across calls and use `withPermit` so failure or cancellation releases the permit. It controls concurrency independently of which dispatcher runs the work.”

## Interview answer — structured

“Dispatchers provide execution resources; a semaphore protects a particular downstream limit. If an API allows three concurrent requests, I keep one semaphore in the repository and wrap each request with `withPermit`. Acquisition suspends rather than blocking a thread, and the helper releases the permit on all exit paths. I tune the number from connection and server limits, measure queueing, and cancel obsolete UI requests so they do not consume capacity. Observe queue wait and server responses.”

## Interview answer — deep senior

“I would define the capacity constraint first: sockets, database connections, CPU-intensive encoders or a partner API rate/parallelism rule. A shared Semaphore gives an in-flight permit bound and must outlive individual calls; per-call semaphores are ineffective. `withPermit` makes release exception-safe, while caller cancellation should remove queued work. It is distinct from a dispatcher, which schedules execution, and from rate limiting, which controls requests per time window. Under load I also bound the waiting queue, expose queue latency and reject or defer low-priority work. For a remote service, retries must obey the same limiter and server backoff policy.”

## Deep-dive talking points

Compare permit bound, thread bound, rate limit and queued backlog.

## Follow-up questions

- [COR-07](../cor-07/): Does IO bound requests to the server? **Answer:** no, dispatcher selection is not a service concurrency policy.
- [COR-18](../cor-18/): Should retries bypass permits? **Answer:** no, retries consume the same downstream capacity.

## Self-check rubric

Can I scope a shared semaphore, release permits safely, and distinguish active versus waiting work?

## References and reviewed-on date

- [Kotlin Semaphore API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.sync/-semaphore/) — permit semantics.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
