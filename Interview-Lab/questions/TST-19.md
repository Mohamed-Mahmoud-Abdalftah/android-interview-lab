---
id: "TST-19"
question: "Write tests for three parallel APIs with partial success and cancellation."
topic: "Testing, Quality & Reliability"
code: "TST"
group: "C"
phase: 4
priority: "P1"
order: 414
editorial_status: "reviewed"
---

# TST-19

## Original interview question

Write tests for three parallel APIs with partial success and cancellation.

## What the interviewer evaluates

- Testing all-or-nothing versus partial-success semantics for three parallel APIs.
- Cancellation propagation and late-result handling.

## Explanation in Arabic

اكتب اختبارات وحدة (Unit Tests) لثلاث استدعاءات متزامنة في الشبكة (3 Parallel APIs) تدعم النجاح الجزئي (Partial Success) وإلغاء العمليات (Cancellation)؟

1. سيناريو الاختبار المطلوب:
   - شاشة الـ Dashboard تقوم بجلب بيانات: (1) الـ User Profile، (2) الـ Transactions، (3) الـ Exchange Rates بشكل متزامن عبر `async/await`.
   - **سيناريو النجاح الجزئي (Partial Success)**: إذا فشلت خدمة أسعار الصرف (Exchange Rates) في الشبكة، يجب ألا يفشل الاختبار أو ينهار التطبيق؛ يجب أن تنجح بيانات الـ Profile والـ Transactions وتُعرض للمستخدم مع علامة خطأ للقسم الفاشل فقط.
   - **سيناريو الإلغاء (Cancellation)**: إذا ألغى المستخدم العملية أو خرج من الشاشة، يجب إلغاء جميع الاستدعاءات الثلاثة فوراً في نفس اللحظة.

2. كيفية الاختبار باستخدام `runTest` و `StandardTestDispatcher`:
   - نستخدم Fakes أو Mocks لتمثيل الخدمات الثلاث، ونتحكم في وقت الاستجابة والتعليق لإثبات التزامن الحقيقي وإلغاء الـ Jobs المعلقة.

## Practical walkthrough

كتابة كود الـ Coordinator واختبارات الـ Partial Success والـ Cancellation التام باستخدام runTest:
```kotlin
// 1. الكود المراد اختباره: جلب متزامن مع دعم الفشل الجزئي عبر supervisorScope:
class DashboardAggregator(
    private val profileApi: suspend () -> String,
    private val ordersApi: suspend () -> List<String>,
    private val ratesApi: suspend () -> Double
) {
    suspend fun loadDashboard(): DashboardResult = supervisorScope {
        val profileDeferred = async { runCatching { profileApi() } }
        val ordersDeferred = async { runCatching { ordersApi() } }
        val ratesDeferred = async { runCatching { ratesApi() } }

        DashboardResult(
            profile = profileDeferred.await().getOrNull(),
            orders = ordersDeferred.await().getOrDefault(emptyList()),
            ratesError = ratesDeferred.await().exceptionOrNull() != null
        )
    }
}

// 2. اختبارات الوحدة الشاملة في JVM:
class DashboardAggregatorTest {
    @Test
    fun `partial failure allows profile and orders to succeed when rates service fails`() = runTest {
        val aggregator = DashboardAggregator(
            profileApi = { "Ahmed" },
            ordersApi = { listOf("Order #1") },
            ratesApi = { throw IOException("Rates service unavailable") }
        )

        val result = aggregator.loadDashboard()
        assertEquals("Ahmed", result.profile)
        assertEquals(1, result.orders.size)
        assertTrue(result.ratesError)
    }

    @Test
    fun `canceling parent job cancels all three parallel calls immediately`() = runTest {
        var child1Cancelled = false
        val aggregator = DashboardAggregator(
            profileApi = { try { delay(1000); "Done" } finally { child1Cancelled = true } },
            ordersApi = { delay(1000); emptyList() },
            ratesApi = { delay(1000); 1.0 }
        )

        val job = launch { aggregator.loadDashboard() }
        runCurrent()
        job.cancel() // إلغاء المهمة الرئيسية
        runCurrent()

        assertTrue("Child coroutine must execute cancellation cleanup", child1Cancelled)
    }
}
```

## Why it matters and how it works

`awaitAll` in a normal scope propagates a child failure and cancels the scope’s remaining children. SupervisorScope changes sibling failure propagation but does not handle exceptions automatically; each async result still needs await/catch. Tests should assert launch, cancellation and final aggregation policy.

## Worked example

Use three controlled `CompletableDeferred` responses for profile, balance and offers. Complete profile, fail balance, leave offers pending. This JUnit 5 example uses `kotlinx-coroutines-test` and proves the all-or-nothing contract without real network calls:

```kotlin
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.test.runCurrent
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class ParallelApisTest {
    @OptIn(ExperimentalCoroutinesApi::class)
    @Test fun oneFailureCancelsPendingSibling() = runTest {
        val gates = List(3) { CompletableDeferred<String>() }
        var offersStopped = false
        val outcome = async {
            runCatching {
                coroutineScope {
                    val profile = async { gates[0].await() }
                    val balance = async { gates[1].await() }
                    val offers = async {
                        try { gates[2].await() }
                        finally { offersStopped = true }
                    }
                    awaitAll(profile, balance, offers)
                }
            }
        }

        runCurrent() // Ensure all three calls have started.
        gates[0].complete("profile")
        gates[1].completeExceptionally(IllegalStateException("balance failed"))
        assertTrue(outcome.await().isFailure)
        assertTrue(offersStopped) // The still-pending offers child was canceled.
    }
}
```

For partial success, use `supervisorScope` and catch each child's ordinary failure at its own result boundary; rethrow `CancellationException`. Add a second test that cancels the parent while all three gates are pending and asserts all three child jobs finish by cancellation. The screen assertion then follows the chosen policy: no partial UI for this test, but independently completed sections for the supervised design.

## Trade-offs and decision criteria

All-or-nothing is simple when fields must be consistent; partial success improves availability for independent sections but complicates UI and error representation. Tests must encode the product decision.

## Failure modes

If test completes all fakes instantly, it never observes failure propagation or cancellation. Step scheduler deliberately and verify a slow sibling receives cancellation. Avoid swallowing CancellationException in each request wrapper.

## Production perspective

Production telemetry records per-call status and aggregate outcome without PII. Integration tests confirm Retrofit cancellation behavior; unit tests prove scope policy and UI state.

## Interview answer — short

Test parallel APIs by wrapping concurrent async calls inside supervisorScope with runCatching to assert partial success when one dependency throws an exception. Test cancellation by launching the aggregation job, invoking job.cancel(), and asserting via finally blocks that child coroutines execute cancellation cleanup immediately.

## Interview answer — structured

Writing tests for concurrent multi-service aggregation requires validating both partial fault tolerance and structured cancellation boundaries:

1. **Testing Partial Success (Fault Isolation)**:
   - Implement the aggregator using `supervisorScope` so that failure in one async branch does not automatically cancel sibling branches.
   - Configure test stubs such that Service A returns valid user data, Service B returns order records, and Service C throws `IOException("503 Service Unavailable")`.
   - Assert that the aggregated result contains populated data for Services A and B alongside an explicit typed error or empty fallback for Service C, verifying graceful UI degradation.

2. **Testing Coordinated Cancellation**:
   - Launch the aggregation call inside a parent `launch` coroutine job.
   - Provide mock functions configured with long delays (`delay(10_000L)`) instrumented with `finally` blocks tracking cancellation flags.
   - Advance time partially, invoke `job.cancel()`, and advance the scheduler.
   - Assert that `job.isCancelled` becomes true and all child jobs terminate cleanly without leaking un-cancelled background coroutines.

## Interview answer — deep senior

From an advanced concurrency testing perspective, verifying thread safety and race conditions requires strict assertions:

1. **Concurrent Dispatcher Stress Testing**: In addition to virtual time tests in `runTest`, run concurrent aggregation routines against `Dispatchers.Default` under multi-threaded stress tests with 100 iterations. This verifies that shared state aggregators or cache mutations do not throw `ConcurrentModificationException` when three parallel network threads complete at the exact same physical millisecond.

2. **Asserting Non-Blocking Concurrency**: Assert that execution is genuinely parallel rather than sequential by measuring virtual elapsed time. If three independent APIs each take 1,000ms, the entire aggregated call must complete in exactly 1,000ms of virtual time, not 3,000ms.

3. **CancellationException Preservation**: Ensure your error-handling operators (`runCatching`) do not swallow `CancellationException`. If cancellation is swallowed, cancelling the screen or leaving the view fails to abort child HTTP requests, resulting in wasted radio bandwidth.

## How to answer in the interview

- **Why:** partial success is a product consistency decision.
- **How:** gate three calls, fail one while another waits, and assert cancellation or supervised results.
- **Trade-off:** atomic bundle simplicity versus independent-section availability.
- **Failure case:** late child overwrites state after retry/navigation.
- **Production solution:** explicit UI error model and adapter cancellation tests.

## Deep-dive talking points

Prompt for explicit product policy, controlled deferreds, sibling cancellation, exception handling and stale response.

## Follow-up questions

- **Interviewer:** "What happens if you use coroutineScope instead of supervisorScope for parallel calls?"
  **Answer:** "If any child coroutine fails in coroutineScope, the entire scope fails immediately and cancels all other sibling coroutines."

- **Interviewer:** "How do you verify that three async calls ran in parallel rather than sequentially?"
  **Answer:** "Assert that total execution virtual time equals the maximum individual call duration rather than the sum of all durations."

## Self-check rubric

Make all three calls controllable. Fail balance while offers is pending and assert sibling cancellation for all-or-nothing; repeat under supervision and assert explicit partial results. Cancel the parent and reject a late stale result.

## References and reviewed-on date

- [Kotlin exception handling](https://kotlinlang.org/docs/exception-handling.html) — supervision/failure propagation.
- [Kotlin coroutine testing](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/) — deterministic scheduling.

Technically reviewed against primary documentation on 2026-10-13.
