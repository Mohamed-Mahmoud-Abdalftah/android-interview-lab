---
id: "COR-10"
question: "What is cooperative cancellation? What are cancellation points?"
topic: "Kotlin Coroutines & Concurrency"
code: "COR"
group: "A"
phase: 1
priority: "P1"
order: 91
editorial_status: "reviewed"
---

# COR-10

## Original interview question

What is cooperative cancellation? What are cancellation points?

## What the interviewer evaluates

Whether the candidate can locate cancellation checks and explain that cancellation is cooperative, not forced thread interruption.

## Explanation in Arabic

الإلغاء في coroutines تعاوني: `cancel` بيغيّر حالة الـJob، والـcoroutine تلاحظ ده عند suspending functions قابلة للإلغاء زي `delay` أو عند `ensureActive`/`yield` في loop طويل. لو الكود CPU loop من غير checks، أو driver synchronous مش بيدعم cancel، هيفضل شغال لحد ما يرجع. لازم ننقل cleanup إلى `finally` وما نبلعش `CancellationException`.

## Practical walkthrough

تخيّل معالجة 100 ألف record على `Default`. لو المستخدم خرج، `cancel` يعلّم الـJob ملغية لكنه مش يوقف loop tight وحده. افحص `ensureActive()` كل chunk أو استخدم `yield()` لو محتاج تدي فرصة لشغل تاني، وحط تحرير الموارد في `finally`. لو catch عام أو `runCatching` بلع `CancellationException`، الـloop ممكن يبان إنه خلص بنجاح وهو المفروض اتلغى.

## Why it matters and how it works

A cancelled Job makes cancellable suspension throw `CancellationException`. `ensureActive()` explicitly checks and throws; `yield()` checks and gives other coroutines a scheduling opportunity. `finally` runs for cleanup, but suspending cleanup needs `withContext(NonCancellable)` only for a small bounded critical cleanup when required.

## Worked example

JVM example uses `kotlinx-coroutines-core`; `items` is in-memory and `inspect` is CPU work, so the loop checks cancellation periodically.

```kotlin
import kotlinx.coroutines.currentCoroutineContext
import kotlinx.coroutines.ensureActive

suspend fun scan(items: List<String>, inspect: (String) -> Unit) {
    for ((index, item) in items.withIndex()) {
        if (index % 256 == 0) currentCoroutineContext().ensureActive()
        inspect(item)
    }
}
```

## Trade-offs and decision criteria

Checking every iteration may add cost; choose a frequency that keeps response time acceptable. `yield` also offers fairness, while `ensureActive` only checks. For blocking libraries use their explicit cancel/close API or isolate and bound them; coroutine cancellation alone cannot guarantee prompt interruption.

## Failure modes

`runCatching { suspendingCall() }` catches `CancellationException` because it catches Throwable, potentially converting cancellation to a normal failure result. A broad `catch (Exception)` that logs and continues has the same risk. Rethrow cancellation before handling domain errors.

## Production perspective

A ViewModel starts a large local search over cached products. New query input cancels the previous Job; the scan checks `ensureActive` to stop quickly. Telemetry distinguishes user cancellation from genuine error, and tests measure cancellation latency under a large dataset.

## Interview answer — short

“Cancellation is cooperative. `cancel` marks the Job, and cancellable suspension or explicit checks such as `ensureActive` observe it. A CPU loop or blocking SDK may ignore it. I rethrow `CancellationException` and use `finally` for cleanup.”

## Interview answer — structured

“A coroutine is not forcibly killed when its Job is cancelled. Suspending functions such as `delay` usually check cancellation and throw `CancellationException`. For CPU-heavy loops I add periodic `ensureActive` or `yield`, trading a little overhead for responsiveness. A synchronous SDK call may not stop until it returns, so I use the SDK’s cancellation facility if one exists. I keep cleanup in `finally` and do not convert cancellation into an ordinary error state.”

## Interview answer — deep senior

“I distinguish three layers: the coroutine Job, the code currently executing, and any external operation already started. Cancelling the Job signals intent; cooperative suspension and explicit checks make the coroutine stop. For a tight CPU loop I check often enough to meet user-visible cancellation latency. For a legacy blocking SDK I cannot promise interruption unless its own API supports it; I may close a resource or cancel a transport call, and I bound the concurrency and timeout. In `finally`, short non-suspending cleanup can run normally; a necessary suspending cleanup can use a tightly bounded `NonCancellable` region. I never swallow `CancellationException`, because that breaks parent cancellation and can publish stale UI or retry cancelled work. Rethrow cancellation before handling domain errors. I would test cancellation in three places: while suspended, during a CPU chunk, and while an external SDK call is in progress. `ensureActive` makes a tight loop notice the Job; `yield` also lets peer tasks run. Neither interrupts arbitrary native code. Cleanup belongs in `finally`, and any broad error mapper must rethrow `CancellationException`. My target is bounded cancellation latency with no stale UI update or leaked resource.”

## How to answer in the interview

- **Why:** cancellation latency affects stale work and resource use.
- **How:** suspend points and explicit ensureActive checks observe a cancelled Job; yield also gives peers a turn.
- **Trade-off:** checking every item adds overhead, so tune the chunk.
- **Failure case:** runCatching turns cancellation into a Result failure or a blocking driver ignores it.
- **Production solution:** rethrow cancellation and test cleanup.

## Deep-dive talking points

Discuss cancellation at `delay`, a CPU loop and a blocking call; distinguish `ensureActive`, `yield` and `NonCancellable` cleanup.

## Follow-up questions

- [COR-16](../cor-16/): How handle cancellation in catch blocks? **Answer:** rethrow `CancellationException` before domain error handling.
- [COR-22](../cor-22/): When add `yield`? **Answer:** for cooperative cancellation and fairness during long CPU work.

## Self-check rubric

Can I identify a cancellation point, fix a tight loop, explain a blocking limitation, and preserve cancellation through error handling?

## References and reviewed-on date

- [Kotlin coroutines basics](https://kotlinlang.org/docs/coroutines-basics.html) — Job and cancellation.
- [Coroutine exceptions](https://kotlinlang.org/docs/exception-handling.html) — cancellation exception semantics.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-13; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
