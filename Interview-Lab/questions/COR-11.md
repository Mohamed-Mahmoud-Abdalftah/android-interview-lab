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

Can the candidate explain sibling failure versus parent cancellation, handle a failed `async` result deliberately, and avoid claiming that coroutine cancellation rolls back external side effects?

## Concept and technical explanation

Both builders create a structured child scope and return only when the block and its children complete. If the enclosing Job is cancelled, both cancel their children. In `coroutineScope`, an uncaught non-cancellation failure in a child fails the scope and cancels siblings. In `supervisorScope`, a failing direct child does not cancel the supervisor or its sibling children. A failure thrown by the supervisor block itself still fails the scope and cancels its children.

Supervision only changes failure propagation; it does not handle an error for the application. A directly supervised `launch` with an uncaught exception needs its own handling or a suitable `CoroutineExceptionHandler`. An `async` stores a failure in its `Deferred`; `await()` throws it. If `await()` throws in the supervisor block without handling, the block itself fails and cancels the other children. Catch the error inside each child or at each await boundary according to the desired partial-result contract. Preserve `CancellationException`.

## Practical walkthrough

A catalog header needs a title and currency formatter to produce one value. If either computation fails, there is no useful aggregate, so a regular `coroutineScope` is appropriate. A dashboard's profile and offers cards can render independently. Under `supervisorScope`, each child maps an ordinary load failure to that card's error state and the other card still returns. The parent screen's cancellation still cancels both requests.

Neither builder is a transaction. A remote charge or database write that already happened is not undone when a sibling fails. Payment workflows need their own provider contract, idempotency, and reconciliation.

## Explanation in Arabic

الاتنين بيعملوا Structured Scope وتستنى الـ block وأطفالها، وإلغاء الـ Parent من فوق بيوصل لهم في الحالتين. في `coroutineScope`، فشل Child غير معالج يفشل النطاق ويلغي الإخوة. في `supervisorScope`، فشل Child مباشرة ما بيلغيش إخواتها، لكن لازم تعالج خطأها. لو الـ Supervisor Block نفسها رمت، النطاق تفشل وتلغي أطفالها. ده تنظيم لفشل الـ Coroutines، مش Rollback لخصم أو كتابة تمت بالفعل.

## Why it matters and how it works

Using a regular scope for independent cards can discard a valid profile because the offers request failed. Using supervision without observing each child failure can produce an unhandled exception or turn an `await` into failure of the whole block. The choice follows whether results are one dependent value or independently useful. Cancellation from above still propagates downward in both cases.

## Worked example

Runnable Kotlin/JVM example. The injected loaders keep transport details out of the scope decision:

```kotlin
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.async
import kotlinx.coroutines.supervisorScope

data class DashboardCards(val profile: Result<String>, val offers: Result<String>)

suspend fun loadCards(
    profile: suspend () -> String,
    offers: suspend () -> String
): DashboardCards = supervisorScope {
    val profileTask = async {
        try { Result.success(profile()) }
        catch (error: CancellationException) { throw error }
        catch (error: Exception) { Result.failure(error) }
    }
    val offersTask = async {
        try { Result.success(offers()) }
        catch (error: CancellationException) { throw error }
        catch (error: Exception) { Result.failure(error) }
    }
    DashboardCards(profileTask.await(), offersTask.await())
}
```

Each card owns its ordinary error result. Cancellation is rethrown so leaving the screen still cancels both children. In a real UI, map the `Result` values to explicit loading, content, and error states.

## Trade-offs and decision criteria

Use `coroutineScope` when child results form one dependent computation and failure invalidates that computation. Use `supervisorScope` when direct children produce independently useful results and each failure has an explicit handling path. Supervision adds per-child error-state work; it is not a blanket reliability setting. Nested children still follow their immediate parent's Job rules unless they also establish supervision.

## Failure modes

An unhandled directly supervised `launch` can reach an uncaught exception handler. A failed `async` becomes an exception at `await`; throwing it from the supervisor block cancels siblings. A broad catch that swallows `CancellationException` obscures parent cancellation. The most serious design error is treating either builder as atomic rollback for a remote charge or local write.

## Production perspective

For a dashboard, expose a state per card and test a failed offers request while the profile succeeds. Test the enclosing Job cancellation separately. For a coupled calculation, use a regular scope and verify sibling cancellation on failure. For payment or other irreversible effects, use domain-specific idempotency and recovery; the coroutine scope only coordinates local tasks.

## Interview answer — short

Both builders wait for their children and pass parent cancellation down. In `coroutineScope`, a child failure fails the scope and cancels siblings. In `supervisorScope`, a direct child's failure does not cancel its siblings, but I still have to handle that child's error. If the supervisor block itself fails, its children are cancelled. Neither builder rolls back an external side effect.

## Interview answer — structured

I choose from the result contract. If parallel child computations together produce one required value, `coroutineScope` fits: an unhandled child failure fails that scope and cancels siblings. If independent dashboard cards can show partial content, `supervisorScope` lets one direct child fail without cancelling the other. Both wait for children, and cancelling their parent cancels children in either builder.

Supervision does not turn an exception into a UI state automatically. A supervised `launch` needs an error-handling path; a failed `async` throws when awaited. If I let that throw from the supervisor block, the block itself fails and cancels siblings, so I map ordinary failures inside each child or handle each await deliberately. I rethrow `CancellationException`. I never use either scope as a substitute for payment idempotency or transaction recovery.

## Interview answer — deep senior

`coroutineScope` and `supervisorScope` are both suspend functions with structured lifetimes: the block and child coroutines finish before the call returns. Their failure relationship differs. A non-cancellation failure in a child of a regular scope fails that scope, which cancels its other children and reports the failure to the caller once cleanup completes. A direct child of a supervisor does not propagate its failure to the supervisor or direct siblings. Cancellation of the enclosing parent still reaches every child. If the supervisor block itself throws, the supervisor fails and cancels its children.

That distinction is about propagation, not error recovery. A directly supervised `launch` with no catch can be reported as an uncaught exception; a `CoroutineExceptionHandler` can observe it but cannot resume the failed coroutine. A supervised `async` stores failure in its `Deferred`. Calling `await` without handling throws in the supervisor block; this block failure can cancel the other child despite the supervisor boundary. I therefore give each independent card an explicit success or error value, while preserving `CancellationException` so parent cancellation still works.

For a dashboard, a profile card and an offers card can remain independent. For a combined local calculation whose output is invalid without all parts, a regular scope expresses that coupling. Neither model makes external effects atomic: cancelling a sibling cannot reverse a completed network charge, file write, or committed database transaction. Those need domain-specific idempotency and recovery. In tests I cover sibling failure, successful partial content, and parent cancellation separately, so the selected boundary matches the product contract rather than a slogan.

## How to answer in the interview

- Start with the common structured lifetime and downward parent cancellation.
- Explain direct-child failure in each builder and failure of the supervisor block itself.
- Distinguish `launch` handling from `async.await()` and show where ordinary errors are mapped.
- State the external-side-effect limit before using a payment example.

## Deep-dive talking points

Direct children versus nested children; `Deferred.await` in a supervisor block; `CoroutineExceptionHandler` as observation, not recovery; cancellation exception preservation; transaction boundaries.

## Follow-up questions

- **Interviewer:** “Can `await()` still fail the whole `supervisorScope`?” **Answer:** “Yes. If it throws in the supervisor block without handling, the block fails and cancels other children.”
- **Interviewer:** “Does parent cancellation reach children under supervision?” **Answer:** “Yes. Supervision isolates direct child failures; it does not sever the parent lifetime.”
- **Interviewer:** “Would `coroutineScope` undo a completed payment when tax loading fails?” **Answer:** “No. Coroutine cancellation cannot roll back a remote side effect; payment needs its own idempotency and recovery contract.”

## Self-check rubric

Can I predict sibling behavior, explain `async.await` and block failure, preserve parent cancellation, and avoid claiming transaction rollback?

## References and reviewed-on date

- [Kotlin `coroutineScope` API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/coroutine-scope.html) — structured lifetime and child failure.
- [Kotlin `supervisorScope` API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/supervisor-scope.html) — direct-child isolation and block failure.
- [Kotlin exception handling and supervision](https://kotlinlang.org/docs/exception-handling.html#supervision) — supervised `launch` and `async`.

Technically reviewed against primary documentation on 2026-10-19.
