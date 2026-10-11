---
id: "TST-05"
question: "What is runTest? How are virtual time and TestScope used?"
topic: "Testing, Quality & Reliability"
code: "TST"
group: "A"
phase: 4
priority: "P1"
order: 400
editorial_status: "reviewed"
---

# TST-05

## Original interview question

What is runTest? How are virtual time and TestScope used?

## What the interviewer evaluates

- runTest lifecycle and virtual-time scheduler semantics.
- What virtual time can and cannot control.

## Explanation in Arabic

`runTest` من `kotlinx-coroutines-test` بيشغّل test coroutine داخل `TestScope` ويضبط scheduler يقدر يعدّي `delay` افتراضيًا بدل انتظار حقيقي. `advanceTimeBy` و`runCurrent` و`advanceUntilIdle` يتحكموا في tasks المجدولة. بس لو code هرب لـ`Dispatchers.IO` حقيقي أو network حقيقية، virtual time مش هتسيطر عليه.

## Why it matters and how it works

A TestScope owns a TestCoroutineScheduler. TestDispatchers sharing that scheduler make scheduled delays deterministic. `runTest` waits for child coroutines under its rules and reports uncaught exceptions; dispatchers not replaced with test dispatchers may still use wall-clock time.

## Worked example

Illustrative test: `runTest { val dispatcher = StandardTestDispatcher(testScheduler); val job = launch(dispatcher) { delay(1_000); events += "done" }; runCurrent(); advanceTimeBy(1_000); runCurrent(); assertEquals(listOf("done"), events); job.join() }`. Requires `kotlinx-coroutines-test` and JUnit assertion imports; list defined in test scope.

## Trade-offs and decision criteria

Virtual time makes retry/backoff tests fast, but using it for real database/network calls gives false confidence. StandardTestDispatcher needs explicit scheduler progress; UnconfinedTestDispatcher starts tasks eagerly and changes ordering.

## Failure modes

A test hangs because a ViewModel uses production Main dispatcher or starts work in a scope outside the shared scheduler. Replace `Dispatchers.Main` with a test dispatcher and inject remaining dispatchers; always reset Main in teardown.

## Production perspective

Use a main-dispatcher test rule and shared scheduler across ViewModel collaborators. Verify exact retry time and cancellation, then add integration tests for actual HTTP timeouts.

## Interview answer — short

“runTest provides a TestScope with virtual time for coroutine delays. I share its scheduler with injected TestDispatchers and advance it deliberately; real I/O remains outside that control.”

## Interview answer — structured

“I use runTest for suspend and Flow logic so delay-based behavior can be checked without sleeping. TestScope owns the scheduler, and StandardTestDispatcher queues work until I call runCurrent, advanceTimeBy or advanceUntilIdle. I inject test dispatchers and replace Main for ViewModel tests. I do not assume runTest virtualizes real network or code launched on an unrelated dispatcher. The mechanics matter. A TestScope owns a TestCoroutineScheduler. TestDispatchers sharing that scheduler make scheduled delays deterministic. `runTest` waits for child coroutines under its rules and reports uncaught exceptions; dispatchers not replaced with test dispatchers may still use wall-clock time. The choice has a trade-off. Virtual time makes retry/backoff tests fast, but using it for real database/network calls gives false confidence. StandardTestDispatcher needs explicit scheduler progress; UnconfinedTestDispatcher starts tasks eagerly and changes ordering.”

## Interview answer — deep senior

“When testing retries I want to assert both order and time: initial attempt, no second attempt before backoff, second attempt at the expected virtual instant, and cancellation preventing later work. I construct all test dispatchers with `testScheduler`, inject them into the class, then advance in small steps. I inspect uncaught child exceptions and clean up Main in finally/teardown. A test that uses `advanceUntilIdle` only can miss intermediate-state bugs, so I assert between ticks. Real HTTP and Room adapters get separate integration tests. Consider a concrete case. Illustrative test: `runTest { val dispatcher = StandardTestDispatcher(testScheduler); val job = launch(dispatcher) { delay(1_000); events += "done" }; runCurrent(); advanceTimeBy(1_000); runCurrent(); assertEquals(listOf("done"), events); job.join() }`. Requires `kotlinx-coroutines-test` and JUnit assertion imports; list defined in test scope. A failure case illustrates the risk. A test hangs because a ViewModel uses production Main dispatcher or starts work in a scope outside the shared scheduler. Replace `Dispatchers.Main` with a test dispatcher and inject remaining dispatchers; always reset Main in teardown. In production, the response is concrete. Use a main-dispatcher test rule and shared scheduler across ViewModel collaborators. Verify exact retry time and cancellation, then add integration tests for actual HTTP timeouts.”

## Deep-dive talking points

Prompt for scheduler sharing, `runCurrent` versus `advanceTimeBy`, escaping real dispatchers and intermediate assertions.

## Follow-up questions

- [TST-06](../tst-06/): Which dispatcher queues launch work? **Answer:** StandardTestDispatcher until scheduler progress.
- [TST-10](../tst-10/): How test backoff? **Answer:** advance virtual time in steps and assert attempts.

## Self-check rubric

Can you explain the mechanism, reproduce the example, justify the trade-off, identify the failure case, and answer both follow-ups for this question?

## References and reviewed-on date

- [Kotlin coroutine testing](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/) — runTest and scheduler.
- [Android coroutine testing](https://developer.android.com/kotlin/coroutines/test) — test dispatchers.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
