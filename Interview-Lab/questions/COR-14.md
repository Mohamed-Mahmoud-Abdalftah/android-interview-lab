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

## Practical walkthrough

لو `launch` تحت supervisor فشل من غير `try/catch`، ممكن `CoroutineExceptionHandler` يستقبل الخطأ بعد انتهاء الـcoroutine علشان logging. لكنه ما يرجّعش قيمة ولا يعمل retry ولا يمنع فشل business flow. `async` بيحتفظ بالخطأ للـ`await`، وتحت parent عادي الفشل يمشي عبر الـJob tree. لذلك الحل العملي غالبًا catch قريب من عملية الطلب مع حالة UI واضحة.

## Why it matters and how it works

The handler observes uncaught exceptions after propagation/termination; it cannot resume the failed coroutine. `async` captures its exception in `Deferred` and `await` throws it. A handler on a normal child is usually not the effective handling point because parent propagation owns the failure. CancellationExceptions are normal control flow and are not generally reported as failures.

## Worked example

JVM illustration shows an owned supervisor and an actual `launch`. Expected I/O failure is mapped near the call; the handler reports unexpected terminal failure. The owner calls `scope.cancel()` at shutdown.

```kotlin
import java.io.IOException
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CoroutineExceptionHandler
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.launch

fun ownedScope(report: (Throwable) -> Unit): CoroutineScope {
    val handler = CoroutineExceptionHandler { _, error -> report(error) }
    return CoroutineScope(SupervisorJob() + Dispatchers.Default + handler)
}

fun launchSync(
    scope: CoroutineScope,
    sync: suspend () -> Unit,
    onNetworkError: (IOException) -> Unit,
): Job = scope.launch {
    try { sync() }
    catch (e: CancellationException) { throw e }
    catch (e: IOException) { onNetworkError(e) }
    // Any other uncaught failure reaches the scope's handler.
}
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

“A handler is a last-resort observation hook. In a normal child tree, exceptions propagate to the parent, so putting the handler on an arbitrary child may not handle them there. A root or supervised `launch` can report uncaught failure through its handler. An `async` holds failure in its Deferred and `await` throws. For a repository call I catch expected failures inside the suspend function and return a typed result or throw to the caller; the ViewModel then shows error state. Cancellation is rethrown, not treated as a user-visible API error.”

## Interview answer — deep senior

“I would not use `CoroutineExceptionHandler` as a blanket safety net. It is invoked when an exception is uncaught at an appropriate coroutine boundary, after the failed coroutine cannot continue; it is for reporting, not retrying or producing a value. In a normal hierarchy child failures are delegated to parents, whereas a supervised `launch` can have an uncaught failure without cancelling peers. `async` intentionally exposes its exception through `await`, so an unawaited Deferred is an ownership smell. In production I define each operation’s error contract, convert expected network errors to state, preserve cancellation, and use the handler for unexpected telemetry. I also test that failure clears loading indicators and does not silently leave a durable operation stuck. I would put an expected network failure inside the operation's `try/catch` so the UI can show retry state. The handler is useful when a supervised `launch` reaches an unexpected terminal exception with no ordinary propagation path, and should send telemetry that can be correlated with the owning task. A handler attached to a normal child will not override its parent's failure path, and a handler on `async` does not replace awaiting the result.”

## How to answer in the interview

- **Why:** a last-resort handler cannot recover a failed operation.
- **How:** CoroutineExceptionHandler observes an uncaught terminal failure with no normal propagation path.
- **Trade-off:** centralized reporting is useful, local handling enables recovery.
- **Failure case:** putting a handler on a child of a normal parent or on async and expecting it to catch there.
- **Production solution:** handle expected errors at the operation and use the handler for reporting.

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

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-13; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
