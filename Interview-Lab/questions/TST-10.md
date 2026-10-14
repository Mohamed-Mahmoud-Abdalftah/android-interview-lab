---
id: "TST-10"
question: "How do you test cancellation, error, retry, timeout, and backoff?"
topic: "Testing, Quality & Reliability"
code: "TST"
group: "B"
phase: 4
priority: "P1"
order: 405
editorial_status: "reviewed"
---

# TST-10

## Original interview question

How do you test cancellation, error, retry, timeout, and backoff?

## What the interviewer evaluates

- Deterministic failure matrix and virtual-time checks.
- Cooperative cancellation and retry safety for non-idempotent operations.

## Explanation in Arabic

كيف تختبر سيناريوهات الإلغاء (Cancellation)، والأخطاء (Errors)، وإعادة المحاولة (Retries)، وفترات الانتظار (Timeouts) للكوروتينات حتمياً؟

1. اختبار إلغاء الكوروتين (Cancellation Testing):
   - التأكد من أن إلغاء الـ `Job` يوقف العمل فوراً ولا يترك أي مهام معلقة في الخلفية.
   - التحقق من تنفيذ كود التنظيف داخل `withContext(NonCancellable)` أو داخل بلوك `finally`.
   - **قاعدة حرجة**: التحقق من أن الكود لا يبتلع `CancellationException` ويقوم بإعادة رميها دائماً.

2. اختبار فترات الانتظار (Timeouts):
   - اختبار الدوال التي تستخدم `withTimeout(duration)` عبر القفز بالوقت الافتراضي في `runTest`.
   - نستخدم `advanceTimeBy(timeoutMs)` للتحقق من رمي `TimeoutCancellationException` بدقة دون انتظار حقيقي.

3. اختبار إعادة المحاولة والتأخير التضاعفي (Exponential Backoff):
   - اختبار خوارزمية الـ Retry التي تعيد المحاولة 3 مرات عند حدوث خطأ في الشبكة.
   - نتحقق من عدد المحاولات والتقدم بالوقت الافتراضي بين كل محاولة وأخرى للتأكد من حساب فترات الانتظار بدقة.

## Practical walkthrough

اختبار إعادة المحاولة التلقائية مع Exponential Backoff والتحقق من السلوك بالوقت الافتراضي:
```kotlin
class NetworkRetryEngine {
    suspend fun <T> fetchWithRetry(maxRetries: Int = 3, block: suspend () -> T): T {
        var attempts = 0
        while (true) {
            try {
                return block()
            } catch (e: IOException) {
                attempts++
                if (attempts >= maxRetries) throw e
                val delayMs = 1000L * (1 shl (attempts - 1)) // 1s, 2s, 4s...
                delay(delayMs)
            }
        }
    }
}

class RetryEngineTest {
    @Test
    fun `fetchWithRetry retries 3 times with exponential delays then succeeds`() = runTest {
        val engine = NetworkRetryEngine()
        var callCount = 0

        val deferredResult = async {
            engine.fetchWithRetry(maxRetries = 3) {
                callCount++
                if (callCount < 3) throw IOException("Network failed")
                "Success"
            }
        }

        // المحاولة 1: تفشل فوراً (callCount = 1) وتبدأ delay(1000)
        runCurrent()
        assertEquals(1, callCount)

        // التقدم بالوقت 1000ms: المحاولة 2 تفشل (callCount = 2) وتبدأ delay(2000)
        advanceTimeBy(1000)
        runCurrent()
        assertEquals(2, callCount)

        // التقدم بالوقت 2000ms: المحاولة 3 تنجح!
        advanceTimeBy(2000)
        runCurrent()
        assertEquals(3, callCount)
        assertEquals("Success", deferredResult.await())
    }
}
```

## Why it matters and how it works

Coroutine cancellation is cooperative; suspending points and explicit checks observe it. `withTimeout` cancels its block, but remote work may already have completed. Backoff timing can be tested with TestCoroutineScheduler, while server deduplication needs contract/integration tests.

## Worked example

This JVM example tests a retry policy's timing and cancellation with `kotlinx-coroutines-test` and JUnit 5. A separate HTTP/backend integration test must verify payment identity after a lost response.

```kotlin
import java.io.IOException
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.advanceTimeBy
import kotlinx.coroutines.test.runCurrent
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

private suspend fun retryTransient(action: suspend () -> Unit) {
    repeat(3) { attempt ->
        try {
            action()
            return
        } catch (cancel: CancellationException) {
            throw cancel
        } catch (transient: IOException) {
            if (attempt == 2) throw transient
            delay(1_000)
        }
    }
}

@OptIn(ExperimentalCoroutinesApi::class)
class RetryCancellationExampleTest {
    @Test fun cancellationPreventsTheNextAttempt() = runTest {
        var calls = 0
        val request = launch {
            retryTransient {
                calls++
                throw IOException("offline")
            }
        }

        runCurrent()
        assertEquals(1, calls)
        advanceTimeBy(999)
        runCurrent()
        assertEquals(1, calls)
        advanceTimeBy(1)
        runCurrent()
        assertEquals(2, calls)
        request.cancel()
        advanceTimeBy(5_000)
        runCurrent()
        assertEquals(2, calls)
        request.join()
    }
}
```

في production لا تفترض إن `IOException` وحدها تصنف كل transient failure؛ عرّف policy حسب نوع الطلب، واجعل إعادة عملية الدفع مشروطة بهوية ثابتة وضمان deduplication من الخادم.

## Trade-offs and decision criteria

Retries improve transient resilience but can amplify outages and duplicate non-idempotent work. Exponential backoff with jitter reduces synchronized load in production; deterministic injected randomness makes tests reproducible.

## Failure modes

A broad `catch(Exception)` swallows CancellationException and schedules another retry after the screen is gone. Re-throw cancellation and test it. `runTest` may not control an uninjected IO dispatcher, causing flaky wall-time tests.

## Production perspective

Use unit tests for state/timing, MockWebServer for HTTP classes, and backend/provider sandbox tests for financial deduplication. Telemetry tracks retry counts and unknown outcomes without sensitive payloads.

## Interview answer — short

Test cancellation by asserting job.cancel() propagates and cleanup blocks execute under NonCancellable. Test timeouts and exponential retries deterministically by advancing virtual time using advanceTimeBy() in runTest, verifying attempt counts and interval spacing without real clock delays.

## Interview answer — structured

Testing asynchronous failure modes requires coordinating virtual clocks and exception dispatchers.

First, **Testing Coroutine Cancellation**. Next, launch a coroutine job under test, verify it enters active processing, and invoke `job.cancel()`.
Assert that `job.isCancelled` becomes true, child jobs terminate, and cleanup routines (e.g. Closing network streams or wiping memory buffers) inside `withContext(NonCancellable)` or `finally` execute completely. Assert that code never swallows `CancellationException`, which breaks structured concurrency.
**Testing Timeouts (`withTimeout`)**. Execute code wrapped in `withTimeout(5000L)` inside `runTest`.
Advance virtual time via `advanceTimeBy(5001L)`. Assert that `TimeoutCancellationException` is thrown, or that `withTimeoutOrNull` safely returns `null` without hanging the test.
**Testing Exponential Backoff and Retries**. Finally, simulate network failures and step through retry intervals using `advanceTimeBy()`. Validate that calls occur at exact mathematical intervals (1s, 2s, 4s) and assert that terminal failures surface the original exception once maximum retry thresholds are reached.


## Interview answer — deep senior

From an advanced concurrency testing perspective, handling exception boundaries requires strict isolation.

First, with CoroutineExceptionHandler in Unit Tests, unhandled exceptions launched via `launch` bubble to the parent scope and crash `runTest`. To assert that a ViewModel handles unexpected network errors gracefully, supply a custom `CoroutineExceptionHandler` or wrap repository results in `runCatching` / `Result<T>`. Next, with SupervisorScope Isolation, when testing concurrent operations where one worker fails (e.g., three parallel API requests), wrap child jobs in `supervisorScope`. Assert that an exception in child A does not cancel child B or child C, verifying resilient partial execution.
Finally, with Testing Jitter Distributions, when retries use randomized jitter (`Random.nextLong(0, delay)`), inject a deterministic pseudo-random generator or seed so that backoff test assertions do not flake due to unpredictable random values.


## How to answer in the interview

- **Why:** retry can multiply side effects or continue after cancellation.
- **How:** assert attempt counts at virtual timestamps and stop after parent cancellation.
- **Trade-off:** resilience versus load and user-visible delay.
- **Failure case:** a lost payment reply is treated as a safe new charge.
- **Production solution:** stable identity, status lookup and backend idempotency.

## Deep-dive talking points

Prompt for cooperative cancellation, virtual timing, lost-response ambiguity, stable payment ID and jitter.

## Follow-up questions

- **Interviewer:** "Why does catching generic Exception inside a coroutine cause bugs?"
  **Answer:** "Because CancellationException extends Exception; catching Exception without rethrowing CancellationException prevents coroutine cancellation from functioning."

- **Interviewer:** "How do you test that withTimeoutOrNull returns a fallback value?"
  **Answer:** "Call advanceTimeBy(timeoutMillis + 1) in runTest and assert that the returned variable equals null or the fallback object."

## Self-check rubric

Assert call counts and virtual timestamps across two failures and backoff, cancel before the next retry, and verify no further request is sent. Keep timeout, cancellation and a payment lost-response case distinct.

## References and reviewed-on date

- [Kotlin cancellation](https://kotlinlang.org/docs/cancellation-and-timeouts.html) — cooperative cancellation.
- [Kotlin coroutine testing](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/) — virtual time.

Technically reviewed against primary documentation on 2026-10-13.
