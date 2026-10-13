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

CancellationException is coroutines' internal control-flow signal for cooperative cancellation. It must never be swallowed. If catching broad Exception or Throwable, you must always rethrow CancellationException immediately so the coroutine can unwind its call stack and terminate cleanly.

## Interview answer — structured

In Kotlin Coroutines, `CancellationException` is not a bug or system failure; it is the fundamental control-flow mechanism used to unwind the coroutine call stack when a task is cancelled.

The most dangerous and common pitfall is swallowing `CancellationException` by catching generic `Exception`:

```kotlin
try {
    doWork()
} catch (e: Exception) {
    // BUG: Swallows CancellationException!
}
```

Because `CancellationException` inherits from `java.lang.Exception`, this catch block suppresses the cancellation signal. The coroutine assumes it recovered, refuses to terminate, and continues executing, creating background resource leaks and zombie network requests.

To propagate it correctly: either catch only specific domain exceptions like `IOException` or `HttpException`, or if you must catch broad `Exception`, check for `if (e is CancellationException) throw e` before handling other errors.

## Interview answer — deep senior

Under the hood, when `Job.cancel()` is called, active suspension points throw a `CancellationException`. The coroutine runtime distinguishes `CancellationException` from other throwables: it does not mark the Job as failed, does not report to `CoroutineExceptionHandler`, and does not cancel the parent Job. It simply transitions the coroutine to the CANCELLED state.

This has serious implications for utility methods like `runCatching` in the standard library. `kotlin.runCatching` catches all `Throwable` instances, including `CancellationException`. If you use `runCatching` around suspending calls, it converts `CancellationException` into a `Result.failure`, breaking structured concurrency unless you explicitly inspect and rethrow it.

In our Android architecture, we forbid raw `runCatching` on suspend functions in code review, replacing it with a custom `runSuspendCatching` helper that automatically rethrows `CancellationException`.

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
