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

## Concept and technical explanation

In Kotlin coroutines, CancellationException represents the foundational cooperative control-flow signal rather than an unexpected operational failure or system crash. When a coroutine scope or parent Job cancels, active suspension points throw a CancellationException to tear down the coroutine call stack and release associated resources cleanly. If an application layer intercepts and swallows this exception via generic catch blocks like catch (e: Exception) or catch (e: Throwable) without rethrowing, structured concurrency breaks down completely. The cancelled coroutine refuses to terminate, resulting in phantom background loops, persistent network connections, and critical memory leaks. Standard library functions like kotlin.runCatching catch all Throwables indiscriminately, silently encapsulating CancellationException into a failure state unless explicitly filtered. Proper cancellation propagation requires catching only specific expected domain exceptions, immediately rethrowing CancellationException when broad catches are unavoidable, and guarding asynchronous cleanup blocks inside finally using withContext(NonCancellable) to prevent immediate premature aborts.

## Practical walkthrough (English)

Consider a repository method executing a user avatar upload from an Android ViewModel:
```kotlin
// Erroneous implementation: swallows CancellationException
suspend fun uploadAvatar(file: File) {
    try {
        api.upload(file)
    } catch (e: Exception) {
        // Catches and swallows CancellationException!
        showErrorToast()
    }
}
```
If the user exits the screen before the upload completes, viewModelScope cancels the coroutine. However, the generic catch block catches CancellationException, treats it as a standard network error, and displays an error toast on a destroyed screen while keeping background resources pinned.
The production-grade, cancellation-safe implementation:
```kotlin
suspend fun uploadAvatar(file: File) {
    try {
        api.upload(file)
    } catch (e: CancellationException) {
        throw e // Rethrow immediately to honour structured cancellation
    } catch (e: IOException) {
        showErrorToast() // Handle real network transport errors only
    } finally {
        withContext(NonCancellable) {
            tempFileManager.cleanup(file)
        }
    }
}
```

## Explanation in Arabic

التعامل مع `CancellationException` في Kotlin Coroutines هو أحد أدق وأهم المواضيع في الـ Senior Level:

1. ما هي `CancellationException`؟
   - هي الـ Exception المخصص الذي تستخدمه مكتبة Coroutines لنقل إشارة الإلغاء وتفكيك الـ Call Stack للـ Coroutine عند إلغائها.
   - هي ليست خطأ حقيقياً (Not a failure)؛ بل هي **آلية عمل طبيعية (Control-flow mechanism)**.

2. الكارثة الأكثر شيوعاً: ابتلاع الاستثناء (Swallowing CancellationException):
   - لو كتبت:
     `try { repo.fetchData() } catch (e: Exception) { Log.e("Tag", e.message) }`
   - لأن `CancellationException` تورث من `java.lang.Exception`، الـ catch block هيلتقطها ويبلعها!
   - النتيجة: الـ Coroutine ترفض التوقف! لو المستخدم قفل الشاشة والـ ViewModel اتلغى، الكود هيفضل شغال في الخلفية ويسرب الذاكرة والبطارية!

3. القاعدة الذهبية للتعامل مع CancellationException:
   - **إما أن تلتقط استثناءات محددة فقط (Catch specific exceptions):** زي `catch (e: IOException)`.
   - **أو لو مضطر تلتقط `Exception` أو `Throwable`، لازم تعيد رميها فوراً:**
     `if (e is CancellationException) throw e`

## Practical walkthrough

نمط الكود الصحيح الذي نطبقه في الـ Production:
```kotlin
// ❌ النهج الكارثي: يبلع الإلغاء ويمنع التوقف:
suspend fun uploadAvatar(file: File) {
    try {
        api.upload(file)
    } catch (e: Exception) {
        showErrorToast()
    }
}

// ✅ النهج السليم والاحترافي:
suspend fun uploadAvatar(file: File) {
    try {
        api.upload(file)
    } catch (e: CancellationException) {
        throw e // إعادة الرمي فوراً ليتم الإلغاء بنجاح
    } catch (e: IOException) {
        showErrorToast() // معالجة أخطاء الشبكة فقط
    }
}
```

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

CancellationException is the internal control-flow signal powering cooperative coroutine cancellation. It must never be swallowed or treated as an application error. When catching generic Exception or Throwable, you must immediately rethrow CancellationException so the coroutine can unwind its execution stack and transition to the cancelled state cleanly. Swallowing it prevents structured teardown and leaks background resources.

## Interview answer — structured

CancellationException represents cooperative cancellation control flow rather than a standard operational failure. When a Job is cancelled, suspending functions unblock by throwing this exception up the call stack to tear down child tasks.

The most critical mistake engineers make is wrapping suspend invocations in broad try-catch blocks that intercept generic Exception or Throwable. Because CancellationException extends java.lang.Exception, catching it indiscriminately prevents the coroutine runtime from completing its cancellation lifecycle, leaving zombie background operations active.

In production, we ensure proper propagation by adopting two strict practices. First, we restrict catch clauses to specific domain exceptions like IOException or HttpException. Alternatively, if a broad catch is unavoidable, we check if the caught throwable is a CancellationException and rethrow it immediately before performing any error handling.

Utility constructs such as standard runCatching must be avoided or wrapped in cancellation-aware extensions, because they package CancellationException into a failure result, silently violating structured concurrency contracts.


## Interview answer — deep senior

Under the hood, JobSupport transitions through a strict state machine from Active to Completing, Cancelling, and finally Cancelled. When Job.cancel is invoked, the Job creates a CancellationException containing the cancellation cause and iterates through its internal NodeList, dispatching cancellation signals to all child coroutines. Suspending primitives like suspendCancellableCoroutine install a completion handler that invokes cancel on the underlying handle and throws CancellationException directly into the resumed execution frame. Crucially, the coroutine framework treats CancellationException differently from all other throwables: it does not mark the parent Job as failed, does not report to any attached CoroutineExceptionHandler, and does not cancel innocent sibling coroutines. This distinction breaks down completely when utility libraries swallow the exception. Standard kotlin.runCatching catches all instances of Throwable, transforming a CancellationException into a Result.failure. If an engineer then executes fold, getOrElse, or retry logic on that Result, the coroutine continues executing statements after the cancellation point, producing phantom mutations and corrupting application state. In staff-level Android architectures, we replace raw runCatching with a custom runSuspendCatching utility that inspects the thrown Throwable and rethrows if it is an instance of CancellationException. Furthermore, when cleanup work in a finally block requires suspending operations, such as flushing an encrypted file buffer or releasing a distributed socket lock, those suspending calls will fail instantly because the surrounding coroutine context is already cancelled. To execute vital asynchronous teardown safely, we wrap the cleanup invocation in withContext(NonCancellable), giving the routine a non-cancellable execution frame while keeping the block tightly scoped to prevent hanging the cancellation pipeline indefinitely.

## How to answer in the interview

- **Why:** cancellation is control flow for ownership, not an ordinary domain failure.
- **How:** catch CancellationException first and rethrow it; map only expected exceptions afterward.
- **Trade-off:** Result is convenient but runCatching needs an explicit cancellation escape.
- **Failure case:** swallowed cancellation triggers retries or stale UI.
- **Production solution:** centralize a cancellation-safe outcome helper and test parent cancellation.

## Deep-dive talking points

Trace cancellation through nested try/catch, `runCatching`, a retry wrapper and a timeout boundary.

## Follow-up questions

- **Interviewer:** "Why is `kotlin.runCatching` dangerous with Coroutines?"
  **Answer:** "Because `runCatching` catches `Throwable`, which intercepts `CancellationException` and encapsulates it as a failure. This silences coroutine cancellation and causes cancelled tasks to continue executing subsequent statements."

- **Interviewer:** "Can you provide a custom message or cause when cancelling a Job?"
  **Answer:** "Yes. You can invoke `job.cancel(CancellationException("User clicked cancel", customCause))` to attach diagnostic reasons for debugging and logging."

- **Interviewer:** "What should you do if you need to run suspending cleanup code after cancellation?"
  **Answer:** "Place the cleanup logic inside a `finally` block and wrap any suspending calls in `withContext(NonCancellable)`. This prevents the cleanup coroutine from being immediately aborted by the active cancellation state."

## Self-check rubric

Can I write catch order, explain `runCatching`, handle cleanup, and test stale-result prevention?

## References and reviewed-on date

- [Coroutine exceptions](https://kotlinlang.org/docs/exception-handling.html) — CancellationException control flow.
- [Kotlin coroutines basics](https://kotlinlang.org/docs/coroutines-basics.html) — Job cancellation.

Technically reviewed against primary documentation on 2026-10-13.
