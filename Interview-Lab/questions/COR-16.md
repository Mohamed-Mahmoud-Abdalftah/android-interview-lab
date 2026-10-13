---
id: "COR-16"
question: "How do you propagate CancellationException correctly?"
topic: "Kotlin Coroutines & Concurrency"
code: "COR"
group: "B"
phase: 1
priority: "P1"
order: 97
editorial_status: "reviewed"
---

# COR-16

## Original interview question

How do you propagate CancellationException correctly?

## What the interviewer evaluates

Can the candidate preserve CancellationException through catch, Result and retry layers?

## Explanation in Arabic

`CancellationException` إشارة control flow إن الـJob اتلغى، مش network error نعرضه للمستخدم أو نعيد محاولته. لما `catch (Exception)` أو `runCatching` يلقطها، لازم نرميها تاني قبل تحويل باقي الأخطاء إلى `Result`. وإلا request قديم ممكن يكمل، أو retry loop تشتغل بعد ما المستخدم خرج من الشاشة.

## Practical walkthrough

في search request، خروج المستخدم يعمل cancel، والـHTTP suspend function غالبًا ترمي `CancellationException`. لو repository مسك `Exception` وحوّلها لـ`Result.failure`، ViewModel ممكن يعرض رسالة خطأ بعد الخروج أو يبدأ retry. حط catch للإلغاء أولًا وارمه تاني، وبعدها تعامل مع الأخطاء المتوقعة. نفس المشكلة تحصل مع `runCatching` لأنه يمسك `Throwable`.

## Why it matters and how it works

Cancelable suspending functions throw CancellationException when their Job is cancelled. It should flow up to the owner; cleanup belongs in `finally`. Kotlin `runCatching` catches Throwable, including cancellation, so a bare call around suspend work can accidentally turn cancellation into success-shaped data or a retryable failure.

## Worked example

JVM/Android repository pattern; `fetch` is a cancellable suspend API. The explicit catch order preserves owner cancellation.

```kotlin
import kotlinx.coroutines.CancellationException

suspend fun <T> fetchResult(fetch: suspend () -> T): Result<T> =
    try { Result.success(fetch()) }
    catch (e: CancellationException) { throw e }
    catch (e: Exception) { Result.failure(e) }
```

## Trade-offs and decision criteria

Use typed domain results for expected failures, but keep cancellation outside that domain. `finally` is right for resource release; only short essential suspending cleanup belongs in a bounded `NonCancellable` block. Avoid broad `Throwable` catches unless rethrowing fatal and cancellation signals correctly.

## Failure modes

If a search request catches cancellation as an ordinary failure, it may emit an error banner for a query the user no longer cares about. A retry wrapper that catches cancellation can schedule another request after ViewModel clearance. This can waste network and publish stale state.

## Production perspective

A search repository returns domain errors from API calls while propagating cancellation. ViewModel `flatMapLatest` cancels stale searches; tests assert the old request produces no UI error. Metrics count real transport failures separately from routine cancellation.

## Interview answer — short

“I rethrow `CancellationException` before handling ordinary exceptions. It signals coroutine cancellation, so swallowing it can keep obsolete work alive or misclassify it as a network failure. Cleanup can go in `finally`.”

## Interview answer — structured

“When a Job is cancelled, cancellable suspending calls commonly throw `CancellationException`. My repository can map HTTP or parsing failures into a typed result, but cancellation has to pass through. I write a specific catch before `catch (Exception)` and avoid bare `runCatching` around suspending operations because it catches Throwable. This matters in search and navigation: obsolete requests should stop rather than show an error or retry. I put resource cleanup in `finally`, keeping any non-cancellable suspending cleanup small and deliberate.”

## Interview answer — deep senior

“Cancellation is part of the concurrency contract between a caller and its children. If I turn it into `Result.failure`, the caller may think a task completed normally and launch retries, save stale data or render a wrong banner. Kotlin `runCatching` is especially easy to misuse because it catches Throwable. I normally use explicit try/catch with `CancellationException` rethrown, then catch only expected domain exceptions; I also avoid swallowing fatal JVM errors. A timeout uses a cancellation exception inside its scope, so I handle a specific timeout boundary where I need an explicit timeout outcome, while preserving outer cancellation. Tests should cancel during a delayed operation and verify no retry, no stale emission and prompt resource cleanup. I would distinguish caller cancellation from a server or network error in metrics. A cancelled search is not a failed search, and retrying it after navigation wastes bandwidth and risks stale state. `runCatching` catches `Throwable`, so a convenient wrapper can accidentally convert cancellation into a successful `Result` object. I would use a helper that rethrows cancellation first, test cancellation during refresh and backoff, and leave cleanup in `finally`.”

## How to answer in the interview

- **Why:** cancellation is control flow for ownership, not an ordinary domain failure.
- **How:** catch CancellationException first and rethrow it; map only expected exceptions afterward.
- **Trade-off:** Result is convenient but runCatching needs an explicit cancellation escape.
- **Failure case:** swallowed cancellation triggers retries or stale UI.
- **Production solution:** centralize a cancellation-safe outcome helper and test parent cancellation.

## Deep-dive talking points

Trace cancellation through nested try/catch, `runCatching`, a retry wrapper and a timeout boundary.

## Follow-up questions

- [FLO-32](../flo-32/): Why is `runCatching` risky in Flow? **Answer:** it can package cancellation as a value unless rethrown.
- [COR-18](../cor-18/): Should retry catch cancellation? **Answer:** no; cancellation stops the retry loop.

## Self-check rubric

Can I write catch order, explain `runCatching`, handle cleanup, and test stale-result prevention?

## References and reviewed-on date

- [Coroutine exceptions](https://kotlinlang.org/docs/exception-handling.html) — CancellationException control flow.
- [Kotlin coroutines basics](https://kotlinlang.org/docs/coroutines-basics.html) — Job cancellation.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-13; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
