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

نختبر cancellation/error/retry/timeout/backoff بتحديد clock وdispatcher وfake dependency. نعمل failure قبل وبعد side effect، نتأكد `CancellationException` ما تتبلعش، ونعدّ المحاولات مع virtual time بدل sleeps. لو HTTP operation مالية، retry لازم نفس operation ID وعقد idempotency من server؛ test محلي ما يثبتش منع duplicate charge لو server مش بيطبقه.

## Why it matters and how it works

Coroutine cancellation is cooperative; suspending points and explicit checks observe it. `withTimeout` cancels its block, but remote work may already have completed. Backoff timing can be tested with TestCoroutineScheduler, while server deduplication needs contract/integration tests.

## Worked example

Test a repository that fails twice then succeeds: at t=0 one call, before t=1s still one, at t=1s second call, then cancel before t=3s and assert no third. Separate test simulates server success with lost response and verifies same payment ID on retry.

## Trade-offs and decision criteria

Retries improve transient resilience but can amplify outages and duplicate non-idempotent work. Exponential backoff with jitter reduces synchronized load in production; deterministic injected randomness makes tests reproducible.

## Failure modes

A broad `catch(Exception)` swallows CancellationException and schedules another retry after the screen is gone. Re-throw cancellation and test it. `runTest` may not control an uninjected IO dispatcher, causing flaky wall-time tests.

## Production perspective

Use unit tests for state/timing, MockWebServer for HTTP classes, and backend/provider sandbox tests for financial deduplication. Telemetry tracks retry counts and unknown outcomes without sensitive payloads.

## Interview answer — short

“I inject time and dispatchers, script failures, advance virtual time stepwise, and assert attempts and cancellation. For payments, timeout is unknown and retries require a stable server-enforced idempotency identity.”

## Interview answer — structured

“I test normal result, transient error, permanent error, timeout, cancellation and backoff at each retry boundary. With runTest I control delays and verify attempt counts before and after each virtual-time step. I make sure CancellationException propagates instead of being treated as a retryable error. For a remote payment, I test lost response after server success and require the same operation ID; local tests alone cannot guarantee server deduplication. ”

## Interview answer — deep senior

“I build a failure table that includes where the side effect may have occurred. A timeout before connecting and a response lost after commit look identical to the client but demand the same safe recovery: status lookup or retry under a documented idempotency contract. Unit tests prove retry policy and cancellation, MockWebServer proves HTTP mapping, and backend contract tests prove duplicate-safe business behavior. I inject jitter/clock to keep timing deterministic, check no retry after cancellation, and bound attempts so an outage does not stampede the service. Re-throw cancellation and test it. ”

## Deep-dive talking points

Prompt for cooperative cancellation, virtual timing, lost-response ambiguity, stable payment ID and jitter.

## Follow-up questions

- [TST-20](../tst-20/): What test proves no duplicate charge? **Answer:** backend/provider idempotency integration after response loss.
- [TST-05](../tst-05/): How avoid real sleeps? **Answer:** TestCoroutineScheduler.

## Self-check rubric

Can you explain the mechanism, reproduce the example, justify the trade-off, identify the failure case, and answer both follow-ups for this question?

## References and reviewed-on date

- [Kotlin cancellation](https://kotlinlang.org/docs/cancellation-and-timeouts.html) — cooperative cancellation.
- [Kotlin coroutine testing](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/) — virtual time.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
