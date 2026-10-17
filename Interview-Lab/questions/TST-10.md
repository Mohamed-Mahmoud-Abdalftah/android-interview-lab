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

## Concept and technical explanation

Testing coroutine cancellation, error propagation, retries, timeouts, and exponential backoff requires strict deterministic control over virtual time and failure injection. Cancellation in Kotlin is cooperative and mediated by CancellationException; tests verify that parent scopes cancel child jobs cleanly without propagating failure upward or leaking unclosed resources. Error testing validates that domain exceptions are caught, logged, or mapped to typed Result failures rather than crashing the hosting scope. Retry and exponential backoff algorithms are tested by combining fake network endpoints that simulate transient failures with runTest's TestScope, advancing virtual time via advanceTimeBy() to assert that retry attempts execute at precise exponential delay intervals without real-world latency. Timeouts are verified using withTimeout or withTimeoutOrNull to ensure operations abort cleanly when deadlines expire.

## Practical walkthrough (English)

Testing retry with exponential backoff and cancellation using virtual time:
```kotlin
class RetryBackoffTest {
    // Fake client failing twice with IOException before succeeding
    class FlakyApiClient {
        var attempts = 0
        suspend fun fetchData(): String {
            attempts++
            if (attempts <= 2) throw IOException("Transient server blip")
            return "Success"
        }
    }

    suspend fun fetchWithBackoff(client: FlakyApiClient): String {
        var currentDelay = 1000L
        repeat(3) {
            try {
                return client.fetchData()
            } catch (e: IOException) {
                delay(currentDelay)
                currentDelay *= 2 // Exponential backoff: 1000ms -> 2000ms
            }
        }
        return client.fetchData()
    }

    @Test
    fun retryWithBackoff_retriesAtExactVirtualTimeIntervals() = runTest {
        val client = FlakyApiClient()
        val job = launch { fetchWithBackoff(client) }

        // Attempt 1 fails immediately at T = 0ms; schedules delay(1000)
        runCurrent()
        assertEquals(1, client.attempts)

        // Advance past first backoff interval (1000ms)
        advanceTimeBy(1001)
        // Attempt 2 fails; schedules delay(2000)
        assertEquals(2, client.attempts)

        // Advance past second backoff interval (2000ms)
        advanceTimeBy(2001)
        // Attempt 3 succeeds!
        assertEquals(3, client.attempts)

        job.join()
    }
}
```

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

In production, do not assume `IOException` alone classifies all transient failures; define explicit retry policies per request type, and ensure payment operations require fixed idempotency keys and server deduplication guarantees.

## Trade-offs and decision criteria

Retries improve transient resilience but can amplify outages and duplicate non-idempotent work. Exponential backoff with jitter reduces synchronized load in production; deterministic injected randomness makes tests reproducible.

## Failure modes

A broad `catch(Exception)` swallows CancellationException and schedules another retry after the screen is gone. Re-throw cancellation and test it. `runTest` may not control an uninjected IO dispatcher, causing flaky wall-time tests.

## Production perspective

Use unit tests for state/timing, MockWebServer for HTTP classes, and backend/provider sandbox tests for financial deduplication. Telemetry tracks retry counts and unknown outcomes without sensitive payloads.

## Interview answer — short

We test cancellation, errors, and backoff deterministically using runTest. Cancellation is tested by canceling jobs and asserting that CancellationException is respected without leaking tasks. Errors are tested by injecting mock exceptions and verifying domain Result mapping. Retries with exponential backoff are tested by advancing virtual time with advanceTimeBy, asserting that retry attempts execute at exact mathematical delay intervals without sleeping real threads.

## Interview answer — structured

Validating asynchronous error resilience and lifecycle cancellation is essential for mission-critical enterprise Android applications.
Testing cancellation requires verifying coroutine cooperative behavior.
When a test cancels a parent Job via job.cancel(), it must assert that active child coroutines abort promptly, release locks, and unregister listeners without bubbling up as fatal test exceptions, since CancellationException is a normal completion signal in coroutines.
Testing error handling focuses on exception boundaries.
By injecting fake data sources that throw custom domain or network exceptions, tests verify that repositories catch low-level throwables and encapsulate them into sealed Result.Failure models rather than permitting uncaught exceptions to crash the application.
Testing retries, timeouts, and exponential backoff algorithms relies entirely on the virtual time capabilities of runTest.
When an operation fails with a transient error and initiates exponential backoff (such as waiting one second, then two seconds, then four seconds), tests do not block execution with thread sleeps.
Instead, developers query invocation counters at exact points along the virtual timeline using advanceTimeBy(millis).
The test asserts that the retry occurs only after the designated backoff interval elapses, verifying that retry budgets are respected and that non-retryable 4xx client errors abort immediately without wasteful retransmissions.

## Interview answer — deep senior

Under the hood, testing cancellation and backoff exposes the delicate interaction between Kotlin's Continuation state machine and TestCoroutineScheduler.
When testing cancellation, senior engineers strictly verify that business code does not catch CancellationException under a broad catch (e: Exception) clause.
Swallowing CancellationException prevents the coroutine runtime from transitioning the Job into the Cancelling state, causing jobs to hang and leaking background threads.
In unit tests, if a coroutine swallows cancellation, runTest detects the leaked active child upon completion and throws an UncompletedCoroutinesError.
When testing exponential backoff, the algorithm schedules delayed resumptions by invoking delay(currentDelay).
Under runTest, the TestDispatcher enqueues these resumptions into the scheduler's Min-Heap queue.
When advanceTimeBy(millis) is called, the scheduler advances its currentTime property and dispatches all scheduled continuations whose trigger timestamp has arrived.
This allows tests to verify intricate backoff formulas—including full jitter calculations—by asserting invocation timestamps down to the exact millisecond.
When testing timeouts via withTimeout(duration), the coroutine library schedules a TimeoutCancellationException on the scheduler.
If the monitored task completes before the virtual clock reaches the duration, the timeout task is cancelled from the queue.
If the virtual clock reaches the timeout threshold, the scheduler throws the timeout exception, unwinding the stack and canceling child operations cleanly.
This ensures that long-running operations fail gracefully in milliseconds without requiring flaky wall-clock timeouts on CI runners.

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
