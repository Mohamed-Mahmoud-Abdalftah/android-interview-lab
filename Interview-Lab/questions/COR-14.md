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

الـ `CoroutineExceptionHandler` (CEH) هو من أكثر الأدوات التي يساء فهمها في Kotlin Coroutines:

1. متى يعمل الـ `CoroutineExceptionHandler`؟
   - يعمل **فقط** كـ **Last-Resort Global Catch Block** (ملاذ أخير) للتعامل مع الـ Uncaught Exceptions.
   - يعمل **فقط** إذا كان ملحقاً بـ **Root Coroutine** (أي Coroutine يتم إطلاقها مباشرة من Scope، زي `scope.launch(ceh)`).
   - يعمل فقط مع `launch`؛ ولا يعمل أبداً مع `async` لأن `async` تغلف استثناءها داخل كائن `Deferred`!

2. أين لا يساعد الـ CEH ولا يعمل إطلاقاً (Where it does NOT help)?
   - **داخل Child Coroutines:** لو وضعت CEH على ابن داخل `coroutineScope`، فلن يُستدعى أبداً! لأن الابن يصعد الاستثناء لأبيه فوراً.
   - **مع `async`:** استثناءات `async` لا تذهب للـ CEH؛ هي تنتظر حتى يتم استدعاء `await()`.
   - **للتعافي من الخطأ (Error Recovery):** الـ CEH لا يمكنه إعادة تشغيل الـ Coroutine أو إخفاء الخطأ؛ عند وصول الاستثناء للـ CEH، تكون الـ Coroutine قد ماتت بالفعل وانتهت!
   - وظيفته الصحيحة الوحيدة: تسجيل الخطأ للـ Crashlytics، أو إظهار رسالة عامة للمستخدم، وليس استعادة مسار العمل.

## Practical walkthrough

توضيح عملي للفرق بين المكان الصحيح والخاطئ لـ CEH:
```kotlin
val handler = CoroutineExceptionHandler { _, exception ->
    Log.e("App", "Uncaught exception: $exception")
}

// ✅ يعمل بنجاح: ملحق بـ Root Coroutine مستخدمة launch:
val scope = CoroutineScope(SupervisorJob() + handler)
scope.launch {
    throw RuntimeException("Root failed!") // سيتم التقاطه في handler
}

// ❌ لن يعمل إطلاقاً (فخ شائع):
scope.launch { // Root
    launch(handler) { // Child! الـ handler هنا سيتم تجاهله تماماً!
        throw RuntimeException("Child failed!") // يصعد للـ Root ويتجاهل handler الابن
    }
}
```

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

CoroutineExceptionHandler only catches uncaught exceptions in root coroutines launched with 'launch'. It does not catch exceptions in child coroutines (which delegate to their parent), it does not catch exceptions in 'async' (which encapsulate errors until await), and it cannot recover from failures—it only logs or reports them after the coroutine has already terminated.

## Interview answer — structured

A `CoroutineExceptionHandler` (CEH) is purely a last-resort error logging and global reporting mechanism, not a general error recovery tool.

It only triggers under strict conditions: 1) It must be installed on a **root coroutine** or scope; and 2) the coroutine must be launched via `launch`. If an unhandled exception reaches the root of the hierarchy, the CEH executes its callback, typically used to log breadcrumbs to Crashlytics or show a generic error toast.

Where it does NOT help: First, it has zero effect when attached to child coroutines. A child coroutine always delegates unhandled exceptions upward to its parent, ignoring its own CEH. Second, it does not catch exceptions from `async` coroutines, which encapsulate errors inside the `Deferred` until `await()` is called. Third, it cannot recover or resume execution—by the time CEH runs, the coroutine has already crashed and unwound.

## Interview answer — deep senior

Under the hood, exception handling in structured concurrency operates through a hierarchical delegation chain. When a child coroutine throws an unhandled exception, it checks if it has a parent. If a parent Job exists, the child passes the exception to the parent via `parent.childCancelled(cause)` and terminates. It completely bypasses its own context's `CoroutineExceptionHandler`.

Only when the exception reaches the root `Job` (a Job with no parent), does the coroutine machinery check the root context for a `CoroutineExceptionHandler`. If present, it invokes `handleException(context, exception)`. If no CEH is found in the root context, it delegates to the JVM's `Thread.currentThread().uncaughtExceptionHandler`, which results in a fatal Android app crash.

In production architecture, CEH should never replace standard `try-catch` blocks or domain Result wrapping in repositories and ViewModels. It should only be configured once on top-level scopes (like custom application-level scopes) as a safety net against unexpected runtime crashes.

## How to answer in the interview

- **Why:** a last-resort handler cannot recover a failed operation.
- **How:** CoroutineExceptionHandler observes an uncaught terminal failure with no normal propagation path.
- **Trade-off:** centralized reporting is useful, local handling enables recovery.
- **Failure case:** putting a handler on a child of a normal parent or on async and expecting it to catch there.
- **Production solution:** handle expected errors at the operation and use the handler for reporting.

## Deep-dive talking points

Distinguish launch/async, normal/supervised parent and expected/unexpected errors; explain why the handler cannot resume a coroutine.

## Follow-up questions

- **Interviewer:** "Why does attaching CEH to `async` not catch the exception?"
  **Answer:** "Because `async` wraps its result and any thrown exception inside the `Deferred<T>` object. The exception is considered handled until someone invokes `deferred.await()`, at which point it is rethrown at the `await()` call site. CEH only handles uncaught exceptions from `launch`."

- **Interviewer:** "Can you use `try-catch` around a `launch` call to catch exceptions thrown inside it?"
  **Answer:** "No! Wrapping `try { scope.launch { throw Exception() } } catch (e: Exception)` does nothing because `launch` returns immediately and executes asynchronously on a dispatcher. The exception is thrown inside the coroutine block, not in the calling thread."

- **Interviewer:** "Where should error handling actually live in an Android app?"
  **Answer:** "In the repository or use-case layer using `try-catch` wrapped into domain Result/Either sealed classes, or in the ViewModel around suspending calls, so the UI can gracefully show retry buttons and descriptive error messages."

## Self-check rubric

Can I place a handler correctly, explain its limits, map domain errors locally, and retain cancellation?

## References and reviewed-on date

- [Coroutine exceptions](https://kotlinlang.org/docs/exception-handling.html) — handler semantics and async.
- [Android coroutines guidance](https://developer.android.com/kotlin/coroutines) — UI error ownership.

Technically reviewed against primary documentation on 2026-10-13.
