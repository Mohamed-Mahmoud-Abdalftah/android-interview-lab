---
id: "COR-26"
question: "Call 3 independent APIs concurrently. How do you preserve partial success without swallowing cancellation?"
topic: "Kotlin Coroutines & Concurrency"
code: "COR"
group: "C"
phase: 1
priority: "P1"
order: 107
editorial_status: "reviewed"
---

# COR-26

## Original interview question

Call 3 independent APIs concurrently. How do you preserve partial success without swallowing cancellation?

## What the interviewer evaluates

Design three independent API calls with typed partial outcomes while preserving parent cancellation.

## Explanation in Arabic

لو الثلاثة APIs مستقلين ووجود نتيجتين مفيد حتى لو التالتة فشلت، نستخدم `supervisorScope` مع outcome منفصلة لكل child. نمسك domain exceptions جوه كل child، لكن نعيد رمي `CancellationException` علشان خروج المستخدم يلغي الكل. UI تعرض نجاح الجزئيات ورسالة retry واضحة للفاشل، وما تسميش ده نجاح كامل.

## Why it matters and how it works

`supervisorScope` prevents one direct child failure from cancelling its siblings, but it does not automatically convert failures into values. Capture each result inside each `async` and await all three; parent cancellation still cancels the group. Record per-source timestamps if stale partial data is possible.

## Worked example

JVM example uses `kotlinx-coroutines-core`; independent APIs return strings and all are cancellable.

```kotlin
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.async
import kotlinx.coroutines.supervisorScope

suspend fun <T> outcome(call: suspend () -> T): Result<T> =
    try { Result.success(call()) }
    catch (e: CancellationException) { throw e }
    catch (e: Exception) { Result.failure(e) }

suspend fun cards(calls: List<suspend () -> String>): List<Result<String>> =
    supervisorScope { calls.map { call -> async { outcome(call) } }.map { it.await() } }
```

## Trade-offs and decision criteria

Partial success suits independent dashboard cards, not a payment total or single consistent transaction. Capturing all failures adds UI complexity and monitoring work. If one source is required, model required versus optional explicitly rather than treating every result equally.

## Failure modes

A broad `runCatching` can package cancellation into an ordinary `Result`, so a screen that disappears still waits or renders stale cards. A supervised `launch` without error handling can report uncaught failure. A partial response needs clear per-card error state and retry controls.

## Production perspective

An operations dashboard loads account alerts, offers and help independently. Each card exposes data/error/loading separately; stale cached data is labeled. Metrics report per-source failure and latency, and tests cancel the parent while two APIs are pending to verify all stop.

## Interview answer — short

“I use `supervisorScope` and capture each API’s domain failure inside its child, then await all outcomes. One failed call does not cancel useful siblings. Parent cancellation still cancels them all, so I rethrow `CancellationException`.”

## Interview answer — structured

“For independent cards, an all-or-nothing scope would discard useful data. I use `supervisorScope`, start each request with `async`, catch expected failures inside each child into a typed result, and await the full set. Cancellation is not a partial failure: I rethrow it so leaving the screen stops the group. The UI renders each result separately and offers targeted retry. If the outputs must form one consistent quote, I would instead use `coroutineScope` and one error state.”

## Interview answer — deep senior

“Supervision gives failure isolation at the coroutine level, but product semantics decide whether isolation is desirable. I define which data is required, which is optional, and whether cached values may be displayed. Each direct child returns an explicit outcome with source and freshness metadata; exceptions are mapped inside the child, with `CancellationException` rethrown. I await every Deferred before returning so no work is orphaned. Parent cancellation remains authoritative. I bound concurrency, avoid retries for permanent failures, and test one/two/three failures plus parent cancellation. Observability tracks each dependency separately so a page with two green cards does not hide a failing service.”

## Deep-dive talking points

Trace supervision, per-child catch placement, parent cancellation and data freshness.

## Follow-up questions

- [COR-25](../cor-25/): Why not partial checkout data? **Answer:** a quote requiring all components would be inconsistent.
- [COR-16](../cor-16/): Which exception must escape? **Answer:** `CancellationException`.

## Self-check rubric

Can I model separate outcomes, preserve cancellation, choose valid partial UX and test a failing dependency?

## References and reviewed-on date

- [Coroutine exceptions](https://kotlinlang.org/docs/exception-handling.html) — supervision and cancellation.
- [Kotlin coroutines basics](https://kotlinlang.org/docs/coroutines-basics.html) — async child ownership.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
