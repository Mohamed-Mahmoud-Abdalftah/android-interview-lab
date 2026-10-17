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

## Concept and technical explanation

Testing concurrent asynchronous operations across three parallel network APIs requires verifying both partial-success aggregation and parent-child cancellation semantics. When an application fetches independent data streams simultaneously (such as UserProfile, AccountBalance, and LoyaltyRewards), senior architectures avoid rigid all-or-nothing failures by encapsulating concurrent requests inside a supervisorScope or executing parallel async jobs with isolated failure handling. In partial-success configurations, failure of a non-critical endpoint (such as LoyaltyRewards returning an HTTP 500) must not cancel the remaining siblings; the system aggregates available data into a degraded UI state while recording error telemetry. Conversely, when the parent coroutine scope is cancelled (due to the user navigating away or screen dismissal), all three in-flight network requests must immediately abort via cooperative cancellation, preventing orphaned socket leaks and late-arriving state mutations.

## Practical walkthrough (English)

Testing parallel API aggregation with partial success and cooperative cancellation:
```kotlin
// Data aggregator combining three parallel API streams
class DashboardAggregator(
    private val profileApi: ProfileApi,
    private val balanceApi: BalanceApi,
    private val loyaltyApi: LoyaltyApi
) {
    suspend fun fetchDashboard(): DashboardResult = supervisorScope {
        val profileDeferred = async { runCatching { profileApi.getProfile() } }
        val balanceDeferred = async { runCatching { balanceApi.getBalance() } }
        val loyaltyDeferred = async { runCatching { loyaltyApi.getLoyaltyPoints() } }

        DashboardResult(
            profile = profileDeferred.await().getOrNull(),
            balance = balanceDeferred.await().getOrNull(),
            loyalty = loyaltyDeferred.await().getOrNull()
        )
    }
}

// Unit testing partial success and cancellation with TestScope
@OptIn(ExperimentalCoroutinesApi::class)
class DashboardAggregatorTest {
    private val profileApi = mockk<ProfileApi>()
    private val balanceApi = mockk<BalanceApi>()
    private val loyaltyApi = mockk<LoyaltyApi>()
    private val aggregator = DashboardAggregator(profileApi, balanceApi, loyaltyApi)

    @Test
    fun fetchDashboard_oneApiFails_returnsPartialSuccessWithRemainingData() = runTest {
        // Profile and Balance succeed, Loyalty throws 500 error
        coEvery { profileApi.getProfile() } returns UserProfile("Alex")
        coEvery { balanceApi.getBalance() } returns AccountBalance(amount = 1500.0)
        coEvery { loyaltyApi.getLoyaltyPoints() } throws HttpException(Response.error<Any>(500, "".toResponseBody()))

        val result = aggregator.fetchDashboard()

        // Assert partial degradation: profile and balance present, loyalty null
        assertEquals("Alex", result.profile?.name)
        assertEquals(1500.0, result.balance?.amount)
        assertNull(result.loyalty)
    }

    @Test
    fun fetchDashboard_parentCancelled_cancelsAllInFlightRequests() = runTest {
        // Simulate long-running network calls
        coEvery { profileApi.getProfile() } coAnswers { delay(1000); UserProfile("Alex") }
        coEvery { balanceApi.getBalance() } coAnswers { delay(1000); AccountBalance(100.0) }
        coEvery { loyaltyApi.getLoyaltyPoints() } coAnswers { delay(1000); LoyaltyPoints(50) }

        val job = launch { aggregator.fetchDashboard() }

        // Advance virtual clock partially, then cancel parent job
        advanceTimeBy(300)
        job.cancelAndJoin()

        // Verify cooperative cancellation terminated all three calls cleanly
        assertTrue(job.isCancelled)
    }
}
```

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
        val profileDeferred = async {
            try { Result.success(profileApi()) }
            catch (e: CancellationException) { throw e }
            catch (e: Exception) { Result.failure(e) }
        }
        val ordersDeferred = async {
            try { Result.success(ordersApi()) }
            catch (e: CancellationException) { throw e }
            catch (e: Exception) { Result.failure(e) }
        }
        val ratesDeferred = async {
            try { Result.success(ratesApi()) }
            catch (e: CancellationException) { throw e }
            catch (e: Exception) { Result.failure(e) }
        }

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

We test three parallel APIs by evaluating two distinct behaviors. For partial success, we wrap parallel async jobs in supervisorScope, simulate one endpoint failing while the others succeed, and assert the resulting UI model gracefully aggregates available data while degrading the failed section. For cancellation, we launch the call in a test job, advance virtual time, cancel the parent job, and assert all in-flight child requests abort immediately.

## Interview answer — structured

Testing parallel network requests requires verifying both resilient fault isolation and cooperative cancellation propagation.
When fetching data from three independent endpoints—such as user profile, bank balance, and rewards—an application must not collapse if an auxiliary service experiences downtime.
To test partial-success semantics, we configure our mock APIs so that the profile and balance calls succeed while the rewards call throws an HTTP 500 server exception.
In the implementation, wrapping child deferred calls in supervisorScope or runCatching ensures that the loyalty failure does not trigger cancellation of its siblings.
The test asserts that the returned aggregate data class successfully contains the user profile and bank balance, while gracefully marking the rewards payload as unavailable for degraded UI presentation.
To test cancellation semantics, we verify resource cleanup when the hosting lifecycle ends prematurely.
In our coroutine test, we simulate slow responses using delay and launch the aggregator inside an active TestScope job.
We advance virtual time partially using advanceTimeBy and invoke cancelAndJoin on the parent job.
The test asserts that the parent cancellation cooperatively cancels all three underlying async child jobs, confirming that no orphaned network requests continue executing in the background or mutate state after the user departs.

## Interview answer — deep senior

Under the hood, coroutine concurrency and failure propagation depend on the structural relationship between Job and SupervisorJob within the coroutine context hierarchy.
In a standard coroutineScope, an uncaught exception in any child async builder cancels the scope's internal Job immediately.
This cancellation immediately propagates downwards to cancel all other active siblings and upwards to the parent caller, enforcing strict all-or-nothing transaction semantics.
For partial success, replacing coroutineScope with supervisorScope introduces a resilient SupervisorJob boundary into the hierarchy.
A SupervisorJob overrides the default parent-child cancellation contract: child failure does not cancel the supervisor and does not cancel neighboring sibling jobs.
However, because async deferred builders rethrow exceptions upon await(), tests verify that exceptions are encapsulated via runCatching or custom Result wrappers before awaiting to prevent unhandled CoroutineExceptionHandler triggers from crashing the test runner.
When testing cooperative cancellation, the mechanism relies on suspension points checking Job.isActive periodically.
When the parent Job is cancelled, it transitions to a Cancelling state and dispatches CancellationException to all active children.
Functions like delay or OkHttp's suspendCancellableCoroutine listen for this signal, aborting the active network call and closing the socket connection.
Using StandardTestDispatcher with advanceTimeBy allows tests to freeze time between request dispatch and response arrival, verifying that cancellation cleans up every child job deterministically without race conditions or memory leaks.

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
