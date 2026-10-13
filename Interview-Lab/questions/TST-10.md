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

افصل الحالات بدل test واحدة تقول “retry اشتغلت”. في failure عادي حدّد error قابل لإعادة المحاولة، عدد المحاولات، backoff والحد الأقصى. بـ`runTest` تأكد إن الطلب الثاني لم يخرج قبل الوقت المحدد، ثم ألغِ parent قبل المحاولة التالية وتحقق إن ما فيش request جديد؛ `CancellationException` لازم تفضل cancellation مش تتحول إلى failure قابلة للretry.

## Practical walkthrough

Timeout غير HTTP error: قد يكون server نفّذ العملية والرد ضاع، خصوصًا في payment؛ هنا استخدم نفس operation ID واستعلام status، مش إنشاء charge جديدة. fake clock/scheduler للتحكم في الوقت، وHTTP integration test لسلوك adapter. تأكد من jitter في حدود يمكن اختبارها بحَقن policy أو مصدر randomness. لا تستخدم `Thread.sleep` ولا تعتمد على سرعة CI.

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

“I inject time and dispatchers, script failures, advance virtual time stepwise, and assert attempts and cancellation. For payments, timeout is unknown and retries require a stable server-enforced idempotency identity.”

## Interview answer — structured

“I test normal result, transient error, permanent error, timeout, cancellation and backoff at each retry boundary. With runTest I control delays and verify attempt counts before and after each virtual-time step. I make sure CancellationException propagates instead of being treated as a retryable error. For a remote payment, I test lost response after server success and require the same operation ID; local tests alone cannot guarantee server deduplication.”

## Interview answer — deep senior

“I write a decision table before testing retries: which failures are retryable, what the attempt cap is, how backoff is calculated, and what cancellation must stop. Under `runTest`, a fake endpoint fails twice, and I assert the exact call count at t=0, just before and at the backoff boundary. I cancel the parent before a later scheduled attempt and assert no more calls or stale UI emissions. I do not catch `CancellationException` as ordinary data; otherwise the operation may continue after the owner disappears. I test timeout separately from a known server rejection. A timeout can mean the server committed but the response was lost, so a payment client must retain the same durable operation ID and reconcile status under a backend idempotency contract. I also test a non-retryable 4xx or validation error, max attempts, jitter bounds and a successful attempt after a transient failure. Unit tests prove policy and scheduling; an HTTP adapter test verifies request identity and cancellation propagation. The backend, not the Android fake, proves duplicate-safe business effects.”

## How to answer in the interview

- **Why:** retry can multiply side effects or continue after cancellation.
- **How:** assert attempt counts at virtual timestamps and stop after parent cancellation.
- **Trade-off:** resilience versus load and user-visible delay.
- **Failure case:** a lost payment reply is treated as a safe new charge.
- **Production solution:** stable identity, status lookup and backend idempotency.

## Deep-dive talking points

Prompt for cooperative cancellation, virtual timing, lost-response ambiguity, stable payment ID and jitter.

## Follow-up questions

- [TST-20](../tst-20/): What test proves no duplicate charge? **Answer:** backend/provider idempotency integration after response loss.
- [TST-05](../tst-05/): How avoid real sleeps? **Answer:** TestCoroutineScheduler.

## Self-check rubric

Assert call counts and virtual timestamps across two failures and backoff, cancel before the next retry, and verify no further request is sent. Keep timeout, cancellation and a payment lost-response case distinct.

## References and reviewed-on date

- [Kotlin cancellation](https://kotlinlang.org/docs/cancellation-and-timeouts.html) — cooperative cancellation.
- [Kotlin coroutine testing](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/) — virtual time.

Technically reviewed against the cited primary documentation on 2026-10-12; automated technical review only, not human review.
