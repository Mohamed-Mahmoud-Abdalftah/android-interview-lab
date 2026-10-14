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

catch intercepts upstream exceptions and emits fallback values; retry attempts upstream re-collection for a fixed count; retryWhen provides dynamic retry predicates with exponential backoff; and onCompletion executes cleanup upon completion or failure, analogous to a finally block.

## Interview answer — structured

These operators handle resilience, recovery, and cleanup across the lifecycle of a Flow:

**`catch`** intercepts exceptions thrown by upstream operators or the producer block. It allows graceful recovery by inspecting the error, logging telemetry, or emitting a fallback state via `emit()`. Crucially, `catch` only intercepts upstream errors; it does not catch exceptions thrown inside the downstream `collect { }` block.

**`retry`** transparently re-subscribes to the upstream flow if an upstream exception occurs, up to a specified attempt count.

**`retryWhen`** is the advanced predicate version, passing the `Throwable` and the current `attempt` counter. It allows implementing exponential backoff with jitter via `delay()` and selectively retrying transient IOExceptions while failing immediately on permanent 4xx errors.

**`onCompletion`** executes when the stream terminates, receiving a nullable `Throwable?` parameter. If `cause == null`, the flow finished normally; if non-null, it completed due to an exception or cancellation. It serves as Flow's reactive `finally` block for closing resources.


## Interview answer — deep senior

A frequent architecture trap in code reviews is placing `catch` above operators that might also fail, or failing to handle errors thrown inside `collect`:

```kotlin
// ❌ BUG: catch does not intercept collect errors:
flow.catch { emit(Fallback) }
    .collect { throw RuntimeException() } // Crash! catch cannot see this!
```

To catch errors that occur during element handling, the recommended pattern is moving the collection logic into `onEach` before `catch`, and terminating with a plain `collect()`:

```kotlin
// ✅ SAFE: catches both producer and processing errors:
flow
    .onEach { processItem(it) }
    .catch { handleException(it) }
    .collect()
```

Furthermore, inside `catch`, `CancellationException` is respected by default: if a collector coroutine is cancelled, `catch` rethrows `CancellationException` to preserve structured concurrency.


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
