---
id: "COR-14"
question: "When does CoroutineExceptionHandler run, and where does it not help?"
topic: "Kotlin Coroutines & Concurrency"
code: "COR"
group: "B"
phase: 1
priority: "P1"
order: 95
editorial_status: "reviewed"
---

# COR-14

## Original interview question

When does CoroutineExceptionHandler run, and where does it not help?

## What the interviewer evaluates

Can the candidate place `CoroutineExceptionHandler` at an uncaught boundary and distinguish it from recovery?

## Explanation in Arabic

`CoroutineExceptionHandler` آخر محطة لملاحظة exception غير ممسوكة من coroutine، خصوصًا root `launch` أو supervised `launch`. مش بديل `try/catch` حوالين API عايز تحول فشله إلى UI state، ومش طريقة ترجع نتيجة من `async`. في child عادي الفشل يروح للـparent؛ handler مركّب على child مش بالضرورة يستقبلها هناك.

## Why it matters and how it works

The handler observes uncaught exceptions after propagation/termination; it cannot resume the failed coroutine. `async` captures its exception in `Deferred` and `await` throws it. A handler on a normal child is usually not the effective handling point because parent propagation owns the failure. CancellationExceptions are normal control flow and are not generally reported as failures.

## Worked example

JVM illustration shows an owned supervisor with a root-like `launch`; `report` is an application logger. Production work still needs task-level state.

```kotlin
import kotlinx.coroutines.*

fun ownedScope(report: (Throwable) -> Unit): CoroutineScope {
    val handler = CoroutineExceptionHandler { _, error -> report(error) }
    return CoroutineScope(SupervisorJob() + Dispatchers.Default + handler)
}
// Owner calls scope.cancel() at shutdown; each task also returns status to its caller.
```

## Trade-offs and decision criteria

Use local `try/catch` to recover or map a known domain failure. Use a handler as last-resort telemetry for uncaught launch failure in an owned root or supervised child. A global handler that only logs can leave UI permanently loading unless task state is updated.

## Failure modes

Installing a handler on `async` and never awaiting it loses the usable error result. Installing one on a regular child can mislead reviewers about where failure is handled. Catching `CancellationException` in a generic error mapper can turn normal screen closure into a fake network error.

## Production perspective

An application sync coordinator uses a supervisor and handler to report unexpected uncaught launch failures. Each sync operation separately returns a typed status and updates durable job state. Alerts distinguish expected network errors from programming failures.

## Interview answer — short

“`CoroutineExceptionHandler` observes an uncaught coroutine exception; it does not recover the coroutine or replace local error handling. A failed `async` exposes failure through `await`. I use a handler for final reporting at an owned root and map expected errors near the operation.”

## Interview answer — structured

“A handler is a last-resort observation hook. In a normal child tree, exceptions propagate to the parent, so putting the handler on an arbitrary child may not handle them there. A root or supervised `launch` can report uncaught failure through its handler. An `async` holds failure in its Deferred and `await` throws. For a repository call I catch expected failures inside the suspend function and return a typed result or throw to the caller; the ViewModel then shows error state. Cancellation is rethrown, not treated as a user-visible API error. Use local `try/catch` to recover or map a known domain failure. Use a handler as last-resort telemetry for uncaught launch failure in an owned root or supervised child. A global handler that only logs can leave UI permanently loading unless task state is updated.”

## Interview answer — deep senior

“I would not use `CoroutineExceptionHandler` as a blanket safety net. It is invoked when an exception is uncaught at an appropriate coroutine boundary, after the failed coroutine cannot continue; it is for reporting, not retrying or producing a value. In a normal hierarchy child failures are delegated to parents, whereas a supervised `launch` can have an uncaught failure without cancelling peers. `async` intentionally exposes its exception through `await`, so an unawaited Deferred is an ownership smell. In production I define each operation’s error contract, convert expected network errors to state, preserve cancellation, and use the handler for unexpected telemetry. I also test that failure clears loading indicators and does not silently leave a durable operation stuck. The handler observes uncaught exceptions after propagation/termination; it cannot resume the failed coroutine. `async` captures its exception in `Deferred` and `await` throws it. A handler on a normal child is usually not the effective handling point because parent propagation owns the failure. CancellationExceptions are normal control flow and are not generally reported as failures. Installing a handler on `async` and never awaiting it loses the usable error result. Installing one on a regular child can mislead reviewers about where failure is handled. Catching `CancellationException` in a generic error mapper can turn normal screen closure into a fake network error.”

## Deep-dive talking points

Distinguish launch/async, normal/supervised parent and expected/unexpected errors; explain why the handler cannot resume a coroutine.

## Follow-up questions

- [COR-15](../cor-15/): Where does `async` surface failure? **Answer:** through `await`, subject to parent failure propagation.
- [COR-16](../cor-16/): What happens to cancellation? **Answer:** rethrow it; do not report it as an ordinary failure.

## Self-check rubric

Can I place a handler correctly, explain its limits, map domain errors locally, and retain cancellation?

## References and reviewed-on date

- [Coroutine exceptions](https://kotlinlang.org/docs/exception-handling.html) — handler semantics and async.
- [Android coroutines guidance](https://developer.android.com/kotlin/coroutines) — UI error ownership.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
