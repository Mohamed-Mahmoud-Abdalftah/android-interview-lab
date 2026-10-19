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

Can the candidate distinguish signalling a cancelled Job from stopping running code, locate a real cancellation check, handle blocking work, and preserve cancellation through error handling?

## Concept and technical explanation

Coroutine cancellation is cooperative. Cancelling a Job changes its state and cancels children and cancellable suspensions, but it does not forcibly stop instructions already running on a thread. Cancellable suspending functions such as `delay` and `yield` observe cancellation and throw `CancellationException`. Not every function marked `suspend` checks cancellation: a custom suspend function that only computes synchronously will keep running unless it checks the current Job or calls a cancellable operation.

In a CPU loop, `currentCoroutineContext().ensureActive()` throws when the current Job is inactive. `yield()` also checks cancellation and gives other coroutines a scheduling opportunity; it is not a synchronization primitive. `isActive` returns a Boolean for code that deliberately chooses its own exit path. Pick a check interval based on the work per item and acceptable cancellation latency. A blocking driver may need its own cancellation or close API; a coroutine check cannot interrupt a blocking call while it is stuck.

## Practical walkthrough (English)

An in-memory search scans a large cached catalog after each query. When a new query supersedes the old one, the owner cancels the previous Job. A scan that performs only CPU work cannot observe that signal until it checks the current context. It checks every 256 items; the current item may still finish, and a long `inspect` call may delay cancellation further. This is a response-time policy, not a guarantee of instant termination.

## Explanation in Arabic

الإلغاء في الـ Coroutines تعاوني: `job.cancel()` يسجل الإشارة، لكن كود CPU الجاري مش بيتوقف بالقوة. عملية قابلة للإلغاء مثل `delay` تلاحظ الإشارة، أما Loop حسابية فتحتاج `currentCoroutineContext().ensureActive()` كل فترة مناسبة. كلمة `suspend` وحدها مش ضمان إن الدالة بتفحص الإلغاء. لو في Driver بيعمل Blocking، لازم تستخدم عقد Cancel أو Close الخاص به؛ الفحص خارج الاستدعاء مش هيقطعه من جوه.

## Why it matters and how it works

Cancellation only becomes observable when the work reaches a cancellable operation or explicitly checks its current Job. A CPU scan must do that itself. The check interval bounds responsiveness only when each chunk is itself bounded. `ensureActive` throws and follows normal `finally` cleanup; `isActive` returns a Boolean when a deliberate alternative exit is needed. Use `join` or `await` for completion ordering rather than relying on `yield`.

## Worked example

Runnable Kotlin/JVM example using `kotlinx-coroutines-core`. The caller owns the Job and decides when an old scan becomes stale:

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

The check at index zero also rejects a Job cancelled before the scan starts. Cancellation during a chunk is observed at the next check; the callback itself must have its own policy if it can block.

## Trade-offs and decision criteria

Checking every item lowers worst-case response delay for cheap items but adds repeated work. Checking every 256 items is illustrative, not a universal setting: measure actual item cost and UI expectations. `yield` adds a scheduling opportunity, while `ensureActive` is only a state check. For a slow library call, use its cancellation/close contract, a timeout where appropriate, or isolate and bound it.

## Failure modes

A custom `suspend fun` with no cancellable operation can run through cancellation. `runCatching` and broad `catch (Exception)` also catch `CancellationException`; returning a normal fallback can allow subsequent code to run even though the Job remains cancelled. Catch specific domain errors or rethrow cancellation first. Avoid treating cancellation as a user-visible failure.

## Production perspective

For cached product search, measure how long stale scans remain active and whether a slow `inspect` callback dominates latency. Keep the Job owner clear, cancel superseded searches, and test that the old scan stops at a bounded check. Put synchronous close operations in `finally`; use a small `withContext(NonCancellable)` block only if essential cleanup itself must suspend. It does not make arbitrary network work safe or guaranteed.

## Interview answer — short

Coroutine cancellation is cooperative: `Job.cancel()` signals cancellation; it does not kill instructions running on a thread. Cancellable suspension, such as `delay`, observes it. In a CPU loop I add `ensureActive()` checks; for blocking I/O I need the library's cancellation contract. I let `CancellationException` propagate.

## Interview answer — structured

I first ask where the code can observe cancellation. A cancellable call like `delay` or `yield` throws `CancellationException` for a cancelled Job. A plain CPU loop, even inside a `suspend fun`, may have no such point, so I check `currentCoroutineContext().ensureActive()` periodically. `isActive` is useful if I intentionally want a Boolean exit; `yield` adds a chance for other coroutines to run but is not a way to wait for a particular result.

In a product search, a new query cancels the old scan; the old one may finish its current chunk before the next check. I choose the interval from measured work per item. If a call blocks inside a driver, checks outside it cannot interrupt it; I use the driver's own close or cancel API. Finally, I rethrow `CancellationException` before mapping ordinary errors.

## Interview answer — deep senior

The Job owns the cancellation state. When cancellation arrives during a cancellable suspension, that operation resumes with `CancellationException`. When execution is already in synchronous CPU code, the runtime does not preempt that code, so `ensureActive()` or another cancellable operation supplies the observation point. Not every `suspend` function is cancellable merely by its signature.

For a large scan I use `currentCoroutineContext().ensureActive()` at a deliberate interval. It checks the coroutine actually executing the scan, rather than an unrelated scope. If fairness on a constrained dispatcher matters, `yield()` checks cancellation and offers another coroutine a turn, but it cannot promise a particular interleaving. I would use `join` or `await` when I need completion ordering. The check interval limits response only if each chunk is bounded; a single blocking call still needs a separate cancellation contract.

Cancellation is a control signal, not an ordinary domain failure. `runCatching` catches `Throwable`, and broad catch blocks catch `CancellationException`; mapping it to a fallback may make the cancelled coroutine execute more code until its next check. It does not restore the Job to active. I rethrow cancellation, close synchronous resources in `finally`, and reserve `withContext(NonCancellable)` for short essential suspending cleanup.

In tests, I cancel the scan during an in-memory chunk and assert that it stops at the next explicit check. I separately test a blocking adapter through its own cancellation contract, because the coroutine check cannot interrupt an opaque call already in progress.

## How to answer in the interview

- Define the Job signal and the point where running code observes it.
- Give one cancellable suspension and one CPU loop that needs `ensureActive`.
- Explain check frequency and why blocking I/O needs its own contract.
- State that catching cancellation as an error does not reactivate the Job.

## Deep-dive talking points

`ensureActive` versus `isActive`; `yield` for responsiveness rather than synchronization; custom suspend functions; `runCatching`; bounded suspending cleanup.

## Follow-up questions

- **Interviewer:** “Does every `suspend fun` stop when its Job is cancelled?” **Answer:** “No. A custom suspend function that only computes synchronously can run on; it needs an explicit check or a cancellable operation.”
- **Interviewer:** “How do `ensureActive()` and `yield()` differ?” **Answer:** “Both observe cancellation. `yield` may also let other coroutines run; I do not use it to guarantee ordering.”
- **Interviewer:** “What if `runCatching` captures `CancellationException`?” **Answer:** “The Job stays cancelled, but a normal fallback may let code keep running until another check. I rethrow cancellation before mapping business errors.”

## Self-check rubric

Can I identify a real cancellation point, fix a CPU loop, explain the blocking-call limit, and preserve cancellation through error handling?

## References and reviewed-on date

- [Kotlin cancellation and timeouts](https://kotlinlang.org/docs/cancellation-and-timeouts.html) — cooperation, CPU loops, cleanup.
- [Kotlin `ensureActive` API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/ensure-active.html) — current-context checks.
- [Kotlin `yield` API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/yield.html) — cancellation and scheduling limitations.
- [Kotlin coroutine exception handling](https://kotlinlang.org/docs/exception-handling.html) — cancellation exception behavior.

Technically reviewed against primary documentation on 2026-10-19.
