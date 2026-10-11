---
id: "COR-11"
question: "Compare coroutineScope and supervisorScope including failure propagation."
topic: "Kotlin Coroutines & Concurrency"
code: "COR"
group: "B"
phase: 1
priority: "P1"
order: 92
editorial_status: "reviewed"
---

# COR-11

## Original interview question

Compare coroutineScope and supervisorScope including failure propagation.

## What the interviewer evaluates

Whether the candidate compares sibling failure propagation while remembering that both boundaries await children and respect parent cancellation.

## Explanation in Arabic

`coroutineScope` و`supervisorScope` الاتنين بيعملوا boundary منظمة وبيستنوا كل الأطفال قبل ما يرجعوا. الفرق إن فشل child في `coroutineScope` العادية بيلغي إخوته ويُفشل الـscope؛ في `supervisorScope` child فاشل ما يلغيّش إخوته تلقائيًا. لكن لو الـparent اتلغى، كل الأطفال بيتلغوا في الحالتين، ولازم نمسك failures الفردية في supervision.

## Why it matters and how it works

With `coroutineScope`, a child exception cancels the scope and sibling Jobs. With `supervisorScope`, direct children are supervised; a failing `launch` can reach an exception handler, while a failed `async` stores failure for `await`. Failure of the supervisor block itself still cancels children. Supervision changes propagation among siblings, not the need to return an outcome.

## Worked example

JVM illustration assumes two independent suspend data sources. Each `async` catches its own domain failure but rethrows cancellation.

```kotlin
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.async
import kotlinx.coroutines.supervisorScope

suspend fun twoCards(a: suspend () -> String, b: suspend () -> String) =
    supervisorScope {
        val first = async { try { Result.success(a()) }
            catch (e: CancellationException) { throw e }
            catch (e: Exception) { Result.failure<String>(e) } }
        val second = async { try { Result.success(b()) }
            catch (e: CancellationException) { throw e }
            catch (e: Exception) { Result.failure<String>(e) } }
        first.await() to second.await()
    }
```

## Trade-offs and decision criteria

Choose `coroutineScope` when all results are required to form a valid unit. Choose `supervisorScope` when independent results can be shown separately and every failure is accounted for. Supervision is not a blanket try/catch and should not hide a broken contract.

## Failure modes

Putting a try/catch only around `await` in an ordinary scope may not preserve siblings: a child failure can already cancel the parent. In a supervised scope, an unhandled failing `launch` can still be reported as uncaught. Cancellation must not be turned into a partial success.

## Production perspective

A dashboard has independent weather and messages cards. A supervised repository returns a typed outcome for each and the UI can render one card while the other shows retry. A checkout total requiring price, tax and discount consistency instead uses all-or-nothing scope.

## Interview answer — short

“Both scope builders wait for children. In `coroutineScope`, child failure cancels siblings and the scope; `supervisorScope` isolates sibling failures. Parent cancellation still cancels all children, and I explicitly handle each supervised failure.”

## Interview answer — structured

“I choose the boundary from product semantics. `coroutineScope` suits an all-or-nothing aggregate: a failing child cancels peer work and throws to the caller after cleanup. `supervisorScope` lets sibling children continue when one fails, so it suits independent widgets. It still waits for children and is cancelled by its parent. For partial success I turn each child’s domain failure into a typed result inside that child, rethrow `CancellationException`, and await every outcome. I do not assume a `CoroutineExceptionHandler` will turn failures into values. Choose `coroutineScope` when all results are required to form a valid unit. Choose `supervisorScope` when independent results can be shown separately and every failure is accounted for. Supervision is not a blanket try/catch and should not hide a broken contract.”

## Interview answer — deep senior

“The subtle point is where failure occurs. A direct child failing in `supervisorScope` does not cancel its siblings, but an exception thrown by the supervisor block itself cancels its children. A failing `launch` is effectively uncaught unless it handles the error; a failing `async` holds the error until `await`. In a normal `coroutineScope`, one child’s failure cancels the Job tree, even if I planned to catch a later `await`. For an all-or-nothing response I want that behavior, and I make operations safe to cancel. For partial success, I use supervision, capture outcomes within children and report them separately. Neither scope survives process death or guarantees an external request was rolled back. With `coroutineScope`, a child exception cancels the scope and sibling Jobs. With `supervisorScope`, direct children are supervised; a failing `launch` can reach an exception handler, while a failed `async` stores failure for `await`. Failure of the supervisor block itself still cancels children. Supervision changes propagation among siblings, not the need to return an outcome. Putting a try/catch only around `await` in an ordinary scope may not preserve siblings: a child failure can already cancel the parent. In a supervised scope, an unhandled failing `launch` can still be reported as uncaught. Cancellation must not be turned into a partial success.”

## Deep-dive talking points

Trace child failure in both scope builders, failure in the block itself, parent cancellation and failed `launch` versus `async`.

## Follow-up questions

- [COR-12](../cor-12/): How does `SupervisorJob` differ? **Answer:** it changes child failure propagation for a Job hierarchy, whereas `supervisorScope` is a suspending boundary.
- [COR-26](../cor-26/): How return partial results? **Answer:** supervise children and capture each domain result inside its child.

## Self-check rubric

Can I predict all four failure paths, choose a scope by product semantics, and preserve cancellation?

## References and reviewed-on date

- [Coroutine exceptions](https://kotlinlang.org/docs/exception-handling.html) — supervision semantics.
- [Kotlin coroutines basics](https://kotlinlang.org/docs/coroutines-basics.html) — scope completion.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
