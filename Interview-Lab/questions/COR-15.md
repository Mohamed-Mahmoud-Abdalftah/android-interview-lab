---
id: "COR-15"
question: "How do launch exceptions differ from async exceptions?"
topic: "Kotlin Coroutines & Concurrency"
code: "COR"
group: "B"
phase: 1
priority: "P1"
order: 96
editorial_status: "reviewed"
---

# COR-15

## Original interview question

How do launch exceptions differ from async exceptions?

## What the interviewer evaluates

Can the candidate compare the observation of `launch` and `async` exceptions while preserving structured failure propagation?

## Explanation in Arabic

فشل `launch` من غير catch بيتعامل معاه كـuncaught exception عند boundary مناسبة؛ فشل `async` بيتخزن في `Deferred` ويتعاد رميه عند `await`. لكن تحت parent عادي الاتنين ممكن يلغوا الـparent والإخوة، فمش صحيح إن `async` آمنة لأن محدش عمل `await`. الاختلاف في طريقة أخذ النتيجة ومكان الملاحظة، مش تصريح بإهمال الفشل.

## Why it matters and how it works

Root `launch` reports an uncaught exception through a handler/default handling. Root `async` stores exception until awaited. Inside a normal structured parent, child failure cancels the parent regardless of builder. A supervisor isolates sibling cancellation, but callers must still await or otherwise account for `Deferred` outcomes.

## Worked example

JVM illustration with injected suspending operation; local result mapping is inside the child so partial success is explicit.

```kotlin
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.async
import kotlinx.coroutines.supervisorScope

suspend fun <T> attempt(operation: suspend () -> T): Result<T> =
    supervisorScope {
        async {
            try { Result.success(operation()) }
            catch (e: CancellationException) { throw e }
            catch (e: Exception) { Result.failure(e) }
        }.await()
    }
```

## Trade-offs and decision criteria

Use `launch` for an owned task with no return value and an error route; use `async` for a value that will be awaited. A direct suspend call is simpler when no parallelism is needed. Supervision is appropriate only when independent failures are meaningful.

## Failure modes

Wrapping only `await` in try/catch under `coroutineScope` may not preserve siblings: the failed child can cancel the parent first. A `launch` that throws in a supervised scope without handling can still produce an uncaught exception and leave its UI card unresolved.

## Production perspective

A dashboard requests independent badges using supervised `async` and captures each `Result` inside each child. A payment confirmation uses a direct suspend call with a typed server response, avoiding a detached launch whose failure nobody observes.

## Interview answer — short

“`launch` returns a Job and an uncaught failure is reported at its owning boundary. `async` returns Deferred and `await` rethrows its stored failure. In a normal parent, either child can still cancel the group, so I always own and observe the result.”

## Interview answer — structured

“The builder changes how the caller interacts with a computation. `launch` is for an owned task without a value; uncaught failure is handled by the Job hierarchy and eventually a suitable handler. `async` is for a value; `await` returns it or throws its exception. Both are children of their scope, and a non-cancellation exception normally cancels a non-supervised parent. If I want partial results, I supervise independent children and convert each domain failure inside its own child, preserving cancellation. I do not use an unawaited Deferred as an error suppression device.”

## Interview answer — deep senior

“I would separate the root case from the child case. A root `launch` has no result channel, so its uncaught failure reaches `CoroutineExceptionHandler` or default handling. A root `async` holds an exception until `await`. But in a normal structured scope the child’s failure also participates in parent cancellation; wrapping a later `await` may not undo it. A supervisor stops one child’s failure from cancelling sibling children, yet it still requires explicit observation: await Deferred values, and handle or report launch errors. In an Android ViewModel I prefer a suspend repository contract for request/response and publish an explicit loading/success/error state, with `CancellationException` rethrown so obsolete work does not update UI.”

## Deep-dive talking points

Compare root and child cases, then draw failure propagation for `async` under a normal parent and under supervision.

## Follow-up questions

- [COR-14](../cor-14/): Does a handler see every `async` failure? **Answer:** no; `Deferred.await` is the result/error channel.
- [COR-26](../cor-26/): How avoid fail-together behavior? **Answer:** supervise and capture separate outcomes inside children.

## Self-check rubric

Can I state both result handles, predict parent cancellation, and design explicit observation for either builder?

## References and reviewed-on date

- [Coroutine exceptions](https://kotlinlang.org/docs/exception-handling.html) — root builders and child propagation.
- [Kotlin coroutines basics](https://kotlinlang.org/docs/coroutines-basics.html) — Job versus Deferred.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
