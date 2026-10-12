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

لو 3 APIs شغالين parallel، الاختبار لازم يحدد policy الأول: `coroutineScope` مع `async/awaitAll` يفشل ويـcancel siblings عند failure؛ `supervisorScope` يسمح لكل child يخلص لكن لازم نمسك errors ونقرر partial result. Fake APIs نتحكم في delays والفشل، ونختبر cancellation/late response. مجرد “واحد فشل” مش كفاية؛ لازم expected UI/data behavior.

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

“I script three controllable APIs, fail one while others are pending, and assert the chosen policy: cancel all for atomic aggregation or preserve independent results for partial success. I also test parent cancellation and late responses.”

## Interview answer — structured

“The test begins with a product rule. If the screen requires a consistent bundle, I use coroutineScope and fail the aggregate when one child fails; siblings are canceled. If sections are independent, I use supervisorScope and handle each result explicitly. I inject fake calls that suspend until the test releases them, then assert intermediate state, cancellation and final UI. I do not infer behavior from a happy-path test where all three return immediately.”

## Interview answer — deep senior

“I build a decision table for three API outcomes: all succeed, one fails early, one fails late, parent cancels and a child ignores cancellation. With TestScope and controlled deferreds I verify launch concurrency, sibling cancellation under coroutineScope, and per-child error capture under supervisorScope. I also check that a late result cannot overwrite a newer screen generation after navigation or retry. Retrofit-level tests confirm the adapter’s cancellation semantics, while domain tests verify whether partial data is safe to show. The choice follows data consistency requirements, not a blanket preference for one scope.”

## Deep-dive talking points

Prompt for explicit product policy, controlled deferreds, sibling cancellation, exception handling and stale response.

## Follow-up questions

- [TST-10](../tst-10/): What happens if cancellation is swallowed? **Answer:** work may continue and emit stale data.
- [TST-05](../tst-05/): How control order? **Answer:** shared TestCoroutineScheduler plus gated fakes.

## Self-check rubric

Can you explain the mechanism, reproduce the example, justify the trade-off, identify the failure case, and answer both follow-ups for this question?

## References and reviewed-on date

- [Kotlin exception handling](https://kotlinlang.org/docs/exception-handling.html) — supervision/failure propagation.
- [Kotlin coroutine testing](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/) — deterministic scheduling.

Technically reviewed against the cited primary documentation on 2026-10-12; automated technical review only, not human review.
