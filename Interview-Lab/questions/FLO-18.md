---
id: "FLO-18"
question: "Compare catch, retry, retryWhen, and onCompletion."
topic: "Flow, StateFlow, SharedFlow & Channels"
code: "FLO"
group: "B"
phase: 1
priority: "P1"
order: 131
editorial_status: "reviewed"
---

# FLO-18

## Original interview question

Compare catch, retry, retryWhen, and onCompletion.

## What the interviewer evaluates

Compare upstream catch, retry/retryWhen predicates and completion observation.

## Concept and technical explanation

Flow error handling and completion mechanisms rely on catch, retry, retryWhen, and onCompletion, which provide structured, declarative management of exceptions and termination lifecycles without disrupting coroutine hierarchies.
catch encapsulates upstream exceptions, preventing crashes by handling errors, executing recovery logic, or emitting fallback default states; crucially, it handles exceptions occurring strictly upstream, leaving downstream collector exceptions untouched.
retry and retryWhen intercept upstream exceptions and resubscribe to the upstream flow from the beginning, either for a fixed iteration count or based on dynamic predicate evaluations (such as applying exponential backoff delays for network recovery).
onCompletion acts as a reactive finally block, executing when the flow terminates either normally upon reaching EOF or exceptionally due to an unhandled failure or cancellation, receiving a nullable Throwable cause parameter to distinguish clean completion from failure.

## Practical walkthrough (English)

Resilient error handling and retry with exponential backoff:
```kotlin
fun observeExchangeRates(): Flow<ExchangeRates> = flow {
    emit(api.fetchLiveRates()) // Might throw IOException
}
.retryWhen { cause, attempt ->
    if (cause is IOException && attempt < 3) {
        val backoffDelay = (attempt + 1) * 1000L
        delay(backoffDelay) // Exponential backoff: 1s, 2s, 3s
        true // Resubscribes upstream
    } else {
        false // Do not retry, let exception propagate to catch
    }
}
.catch { throwable ->
    // Handle error gracefully by emitting offline cached rates:
    emit(cacheDao.getCachedRates())
}
.onCompletion { cause ->
    if (cause != null) logError("Stream terminated with error: $cause")
    else logInfo("Stream completed successfully")
}
```

## Explanation in Arabic

المقارنة بين مشغلات معالجة الأخطاء وإنهاء التدفق `catch` و `retry` و `retryWhen` و `onCompletion`:

1. المشغل `catch`:
   - يلتقط الاستثناءات التي تحدث في **الـ Upstream فقط (ما قبله في السلسلة)**.
   - يسمح لك بإصدار قيمة بديلة عبر `emit(fallback)` أو تسجيل الخطأ.
   - **تحذير خطير:** الـ `catch` لا يلتقط الأخطاء التي تحدث في الـ Downstream أو داخل بلوك `collect { }` الذي يليه!

2. المشغل `retry(retries)`:
   - يعيد محاولة جمع الـ Flow من البداية لعدد محدد من المرات إذا حدث استثناء في الـ Upstream.

3. المشغل `retryWhen(predicate)`:
   - أكثر مرونة وتحكماً؛ يمرر لك سبب الخطأ ورقم المحاولة الحالية (`cause: Throwable, attempt: Long`).
   - يسمح بتطبيق **Exponential Backoff** عبر مناداة `delay()` داخل البلوك وإرجاع `true` لإعادة المحاولة أو `false` للاستسلام.

4. المشغل `onCompletion`:
   - ينفذ كود عند انتهاء الـ Flow سواء انتهى بنجاح طبيعي (`cause == null`) أو انتهى بسبب استثناء أو إلغاء (`cause != null`).
   - يشبه كتلة الـ `finally` في الـ try-catch.

## Practical walkthrough

سلسلة معالجة أخطاء إنتاجية متكاملة في Repository:
```kotlin
fun getLiveFeed(): Flow<FeedState> = feedApi.streamUpdates()
    .retryWhen { cause, attempt ->
        // 1. إعادة المحاولة فقط في أخطاء الشبكة المؤقتة وبحد أقصى 3 مرات:
        if (cause is IOException && attempt < 3) {
            delay(1000L * (attempt + 1)) // exponential delay
            true // أعد المحاولة
        } else false // استسلم ومرر الخطأ للأسفل
    }
    .catch { error ->
        // 2. التقاط الخطأ النهائي وإصدار حالة الفشل بدلاً من تحطيم التطبيق:
        emit(FeedState.Error(error.message ?: "Network error"))
    }
    .onCompletion { cause ->
        // 3. تنظيف وإغلاق الاتصال:
        closeConnectionHandles()
    }
```

## Why it matters and how it works

Operator order defines which stages are covered. `retryWhen` exposes cause and attempt count for backoff; `retry` uses a simpler predicate. Upstream cold source is resubscribed, so repeatable side effects need safety. `onCompletion` can inspect cause and run cleanup, but failure still propagates unless separately caught.

## Worked example

JVM snippet retries transient read failures at most twice; cancellation remains propagated. The API call is read-only.

```kotlin
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.flow.*

fun readFeed(fetch: suspend () -> String): Flow<String> = flow { emit(fetch()) }
    .retryWhen { cause, attempt ->
        if (cause is CancellationException) throw cause
        val retryable = cause is java.io.IOException && attempt < 2
        if (retryable) kotlinx.coroutines.delay(200L * (attempt + 1))
        retryable
    }
    .catch { cause ->
        if (cause is java.io.IOException) emit("cached") else throw cause
    }
```

## Trade-offs and decision criteria

Catch can provide a user-visible fallback but may hide outages if telemetry is absent. Retry improves transient reliability but repeats cold upstream and can amplify load. onCompletion is suitable for logging or resource cleanup, not error recovery by itself.

## Failure modes

`catch` before a failing downstream `map` will not catch that map. A retry on a payment-writing flow can repeat the charge unless server idempotency is enforced. Treating cancellation as a retryable error keeps obsolete work alive.

## Production perspective

A feed repository retries transient read failures with capped backoff and then emits cached data, while recording refresh failure separately. Payment submission is modeled as durable operation state and server reconciliation, not a generic `retry` chain.

## Interview answer — short

catch captures upstream exceptions and can emit fallback values; retry and retryWhen re-collect upstream upon errors based on retry counts or backoff predicates; and onCompletion executes at stream termination, receiving a nullable Throwable indicating clean completion or failure.

## Interview answer — structured

Declarative error operators in Flow isolate exception handling from procedural try-catch blocks.

Catch intercepts errors originating strictly upstream. When an upstream database query or network call throws an exception, catch absorbs the failure, logs diagnostic telemetry, and conditionally emits a fallback state, preventing unhandled exceptions from crashing the parent CoroutineScope.

In production, transient network failures require resilience. retry resubscribes up to a fixed attempt limit, while retryWhen allows senior engineers to implement exponential backoff by inspecting the error type and applying delay before returning true.

OnCompletion serves as the declarative lifecycle finalizer. It executes regardless of whether the stream finishes normally, cancels due to lifecycle changes, or aborts via an error, enabling deterministic cleanup of socket handles, file descriptors, and loading indicators.


## Interview answer — deep senior

Under the hood in kotlinx.coroutines.flow, catch operates by intercepting exceptions thrown during upstream FlowCollector.emit or transformation calls. When an exception is trapped, catch verifies the exception type: if the exception is a CancellationException, it rethrows it immediately to preserve structured concurrency cancellation semantics.
Crucially, catch cannot trap downstream exceptions. If an exception is thrown inside the action block of collect { ... }, downstream of catch, catch will not intercept it, causing the coroutine to crash. To protect against downstream collection crashes, developers must place catch after intermediate operators or wrap the collector block in procedural try-catch.
retry and retryWhen operate by wrapping the upstream flow inside an iterative loop. When an exception occurs, if the predicate returns true, the operator cancels the failed subscription and invokes collect on the original upstream Flow from the beginning. This requires upstream producers to be idempotent; if an upstream flow performed partial mutations before throwing, retrying without rollback duplicates operations.
In addition, onCompletion intercepts stream termination by inspecting the nullable Throwable cause parameter. If upstream fails or the parent job cancels, the cause is forwarded into the lambda for diagnostics and resource cleanup before the exception propagates downstream.
Staff engineers structure error boundaries cleanly: placing retryWhen with backoff upstream, followed by catch emitting cached UI state models, and finishing with onCompletion resetting loading spinners.

## How to answer in the interview

- **Why:** error operators can repeat work or hide failures.
- **How:** show upstream boundary and retry resubscription.
- **Trade-off:** resilience versus duplicate side effects.
- **Failure case:** catching downstream errors or retrying cancellation.
- **Production solution:** classify failures and test retry counts.

## Deep-dive talking points

Trace operator placement, resubscription side effects and cancellation during backoff.

## Follow-up questions

- **Interviewer:** "Can you emit values from inside `onCompletion`?"
  **Answer:** "Yes. `onCompletion` exposes a `FlowCollector`, allowing you to emit final sentinel values (e.g., `emit(UiState.Finished)`) upon stream completion, provided the flow did not abort due to an unhandled exception."

- **Interviewer:** "Why does `retryWhen` re-collect from the beginning of the flow?"
  **Answer:** "Because cold flows are lazy blueprints. When `retryWhen` returns true, it triggers a brand-new `collect()` invocation on the upstream flow, executing its producer code from the starting state."

- **Interviewer:** "Does `catch` swallow the exception if you don't call `emit()`?"
  **Answer:** "Yes. If the `catch` lambda simply logs the error and exits, the exception is considered handled and the stream completes cleanly without throwing an exception to the caller."

## Self-check rubric

Can I identify catch coverage, count resubscriptions, preserve cancellation and distinguish observation from recovery?

## References and reviewed-on date

- [Kotlin Flow API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-flow/) — exception transparency and operators.

Technically reviewed against primary documentation on 2026-10-13.
