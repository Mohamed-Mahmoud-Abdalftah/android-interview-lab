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

## Concept and technical explanation

CoroutineExceptionHandler (CEH) is an optional CoroutineContext element that serves as a global last-resort safety net for unhandled exceptions in Kotlin coroutines. It operates analogously to Thread.setDefaultUncaughtExceptionHandler in standard Java concurrency. Crucially, CEH executes only when installed on a root coroutine launched with the launch builder, or when installed on a root SupervisorJob/supervisorScope. It does not run for child coroutines, because child coroutines unconditionally delegate their uncaught exceptions up to their parent job in the hierarchy. Furthermore, CEH does not handle exceptions originating from the async builder, because async encapsulates failures inside its Deferred result. Most importantly, CEH is purely a diagnostic and reporting mechanism: by the time CEH is invoked, the coroutine has already terminated and its call stack has unwound, meaning CEH cannot recover execution, retry operations, or prevent scope cancellation.

## Practical walkthrough (English)

Demonstrating valid CEH placement versus common silent failure scenarios:
```kotlin
// 1. Ineffective placement: CEH installed on a child coroutine (Silently ignored!)
val scope = CoroutineScope(Dispatchers.Default)
val childHandler = CoroutineExceptionHandler { _, exception ->
    println("Caught: $exception") // NEVER RUNS!
}
scope.launch {
    launch(childHandler) { // Child delegates to parent; childHandler is ignored!
        throw IllegalStateException("Child failure")
    }
}

// 2. Production Placement: CEH installed at the root scope
val rootHandler = CoroutineExceptionHandler { _, exception ->
    FirebaseCrashlytics.getInstance().recordException(exception)
    Telemetry.logFatalCoroutineError(exception)
}

val applicationScope = CoroutineScope(SupervisorJob() + Dispatchers.Default + rootHandler)
applicationScope.launch {
    // Uncaught exception here reaches rootHandler cleanly without crashing the process
    performBackgroundSync()
}
```

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

CoroutineExceptionHandler is a last-resort logging element for uncaught exceptions. It only runs when attached to a root coroutine launched with launch or on a root supervisor scope. It does not run on child coroutines (which delegate to their parent), does not handle async errors (which are held in Deferred), and cannot recover or resume execution.

## Interview answer — structured

CoroutineExceptionHandler functions as a global uncaught exception listener rather than an inline error-handling control structure.

The handler executes only under two strict conditions. First, it must be installed either on a root CoroutineScope or directly on a root launch builder. Second, the operation must be launched via launch rather than async. When an unhandled exception reaches the root of the coroutine hierarchy without being caught by try-catch blocks, the framework delegates the uncaught throwable to the CoroutineExceptionHandler.

In production, engineers frequently misunderstand where the handler does not help. It is completely ignored when installed on a child coroutine, because child tasks automatically delegate failure propagation to their parent Job. Furthermore, it does not catch exceptions thrown inside async builders, because async encapsulates failures inside the returned Deferred instance until await is invoked.

CoroutineExceptionHandler is strictly a terminal reporting tool. It is designed to log crashes to telemetry engines like Crashlytics or present generic error dialogues; it cannot recover the failed operation, suppress scope cancellation, or retry the transaction.


## Interview answer — deep senior

At the lower plumbing level of kotlinx.coroutines, exception handling follows a strict escalation ladder defined in handleCoroutineException. When a coroutine launched with launch terminates with an uncaught exception, it attempts to notify its parent via childCancelled. If the parent is a standard Job, the parent absorbs the error and propagates it upward. This upward delegation continues recursively until the error reaches the root of the hierarchy.
Only when the root Job completes exceptionally does the runtime invoke handleCoroutineException(context, exception). The runtime inspects the root CoroutineContext for a registered CoroutineExceptionHandler. If discovered, its handleException method is invoked synchronously. If no handler is found in the context, the runtime iterates through Java ServiceLoader instances of CoroutineExceptionHandler, and finally falls back to the current Thread's uncaughtExceptionHandler, which typically terminates the Android OS process with a fatal crash.
This mechanism illuminates why attaching a handler to an async coroutine does nothing. The async builder instantiates a DeferredCoroutine, which overrides handleJobException to return false, suppressing invocation of handleCoroutineException. The exception is stored in the internal state of the DeferredCoroutine until await is called, at which point the continuation unrolls and rethrows the original exception directly at the await call site.
Staff Android engineers enforce three rules: use inline try-catch or runSuspendCatching at repository boundaries for recoverable business logic; attach a CoroutineExceptionHandler to global application scopes exclusively for telemetry and crash reporting; and never rely on handlers for control flow.

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
