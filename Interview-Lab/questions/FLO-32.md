---
id: "FLO-32"
question: "What is the danger of using runCatching around cancellable flow/coroutine work?"
topic: "Flow, StateFlow, SharedFlow & Channels"
code: "FLO"
group: "C"
phase: 1
priority: "P1"
order: 145
editorial_status: "reviewed"
---

# FLO-32

## Original interview question

What is the danger of using runCatching around cancellable flow/coroutine work?

## What the interviewer evaluates

Explain runCatching swallowing cancellation and how to preserve structured shutdown.

## Explanation in Arabic

`runCatching` في Kotlin بتمسك `Throwable`، وده يشمل `CancellationException`. لو لفّينا cancellable Flow/coroutine operation بيها من غير إعادة رمي الإلغاء، هنحوّل خروج الشاشة إلى `Result.failure` عادي؛ ممكن retry تشتغل أو UI تعرض error قديم. نستخدم `try/catch` واضح: نعيد رمي cancellation ونمسك expected domain exceptions فقط.

## Why it matters and how it works

CancellationException is control flow for a cancelled Job. `runCatching` is not coroutine-aware and catches it. A Flow `catch` operator has upstream placement rules and is transparent to downstream; custom wrappers still must avoid swallowing cancellation. Timeouts that use cancellation require narrow handling at their own boundary.

## Worked example

JVM/Android-compatible suspend wrapper; caller cancellation remains visible to its parent.

```kotlin
import kotlinx.coroutines.CancellationException

suspend fun <T> safeResult(call: suspend () -> T): Result<T> =
    try { Result.success(call()) }
    catch (e: CancellationException) { throw e }
    catch (e: Exception) { Result.failure(e) }
```

## Trade-offs and decision criteria

Typed Result can simplify expected error handling but should not absorb lifecycle cancellation or fatal errors. A narrow domain exception catch is preferable to a broad Throwable catch. For timeouts, choose whether a specific inner timeout becomes a domain result without catching outer cancellation.

## Failure modes

A flow search wrapped in bare `runCatching` may emit Error after a new query cancelled it. A retryWhen predicate that treats cancellation as transient may resubscribe an obsolete source. A catch block that logs and continues can retain work after logout.

## Production perspective

A search ViewModel cancels stale requests via flatMapLatest. Repository wrapper rethrows cancellation, so old request produces no Error state or retry. Unit tests cancel during delay and verify no further API calls or UI emissions.

## Interview answer — short

“Bare runCatching catches CancellationException, so it can turn cooperative cancellation into an ordinary Result. I rethrow cancellation before mapping domain errors and test that a cancelled stream neither retries nor renders stale error UI.”

## Interview answer — structured

“Kotlin `runCatching` catches Throwable without special knowledge of coroutine cancellation. A cancelled suspending call commonly throws CancellationException; packaging that exception as Result.failure can make the caller think the operation completed normally. In a search or lifecycle flow, this can trigger a retry or an obsolete error banner. I use explicit try/catch, rethrow CancellationException first, and catch only expected failures. I keep timeout mapping at a narrow boundary so an inner deadline is not confused with parent cancellation.”

## Interview answer — deep senior

“The failure is subtle because the code still type-checks and tests may pass on the happy path. Structured cancellation relies on the exception propagating from a cancellable suspension. Bare `runCatching` catches it as Throwable and can convert the cancelled branch into a value; downstream `map` or retry policy then continues as though the screen were active. I audit repository wrappers, Flow operators and `Result` adapters for that pattern. Explicit catch order rethrows cancellation, maps only expected I/O/domain errors, and lets fatal errors propagate. A timeout can be intentionally converted to a Timeout result at its own boundary, but outer Job cancellation must remain distinct. Deterministic tests cancel during a delayed API call and assert no retry, no stale UI emission and released resources.”

## Deep-dive talking points

Trace CancellationException through runCatching, retryWhen, catch and inner timeout mapping.

## Follow-up questions

- [COR-16](../cor-16/): What is the safe catch order? **Answer:** rethrow CancellationException before ordinary error mapping.
- [FLO-18](../flo-18/): Should retry resubscribe cancellation? **Answer:** no; cancellation stops the pipeline.

## Self-check rubric

Can I identify the caught Throwable, preserve parent cancellation and test no stale emission?

## References and reviewed-on date

- [Coroutine exceptions](https://kotlinlang.org/docs/exception-handling.html) — cancellation control flow.
- [Kotlin Result.runCatching API](https://kotlinlang.org/api/core/kotlin-stdlib/kotlin/run-catching.html) — catches Throwable.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
