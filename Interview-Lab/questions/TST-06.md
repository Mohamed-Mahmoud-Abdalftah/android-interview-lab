---
id: "TST-06"
question: "Compare StandardTestDispatcher and UnconfinedTestDispatcher."
topic: "Testing, Quality & Reliability"
code: "TST"
group: "A"
phase: 4
priority: "P1"
order: 401
editorial_status: "reviewed"
---

# TST-06

## Original interview question

Compare StandardTestDispatcher and UnconfinedTestDispatcher.

## What the interviewer evaluates

- Dispatch and execution order differences.
- Choosing scheduler control versus eager execution deliberately.

## Explanation in Arabic

`StandardTestDispatcher` بيجدول coroutine على `TestCoroutineScheduler` ومش بيشغّل `launch` فورًا؛ لازم `runCurrent` أو تقدم الوقت. `UnconfinedTestDispatcher` يبدأ coroutine الجديدة eagerly لحد أول suspension، فاختبارات بسيطة تبقى أسهل لكن order ممكن يختلف عن production. الاتنين يشاركوا virtual scheduler لو اتبْنوا صح.

## Why it matters and how it works

Standard gives deterministic explicit ordering; Unconfined enters new coroutines eagerly and resumes according to scheduler behavior. Neither is a production dispatcher simulation in all respects. Test correctness should not depend accidentally on eager execution.

## Worked example

For a ViewModel that emits Loading then Success, use StandardTestDispatcher to assert Loading before advancing queued repository response. With Unconfined, success may appear immediately and obscure the intermediate state. Construct both with the runTest scheduler when mixing.

## Trade-offs and decision criteria

Unconfined reduces boilerplate for collectors that must be ready immediately; Standard exposes scheduling boundaries and race conditions. Choose intentionally, not because one makes a failing test pass.

## Failure modes

A test asserts an emission before `runCurrent()` and fails under Standard; switching blindly to Unconfined hides the timing assumption. Fix the test to advance scheduler and assert the expected sequence.

## Production perspective

Team test conventions use Standard by default for state machines, with documented Unconfined use for collectors. Review dispatcher injection and race-prone paths; run integration tests for real-thread behavior.

## Interview answer — short

“StandardTestDispatcher queues work until the scheduler runs; UnconfinedTestDispatcher enters coroutines eagerly. I prefer Standard for ordering-sensitive tests and use Unconfined only when eager collection is intentional.”

## Interview answer — structured

“Both belong to kotlinx-coroutines-test and can share one virtual scheduler. StandardTestDispatcher makes launch timing explicit, which helps inspect loading, retry and cancellation states. UnconfinedTestDispatcher enters launched work eagerly until suspension, simplifying some collectors but potentially hiding ordering bugs. I pick based on what the test needs to prove and avoid treating either as exact production scheduling.”

## Interview answer — deep senior

“For a senior-level concurrency test, I first state the happens-before relationships I need. With Standard I can stop before dispatch, after launch, after a virtual delay and after cancellation, asserting state at each point. With Unconfined I may start a Flow collector eagerly so it does not miss an event, but I keep that use local and explicit. Sharing one TestCoroutineScheduler across injected dispatchers prevents unexplained hangs. I also test real adapter behavior where thread confinement or race conditions depend on Android/runtime scheduling.”

## Deep-dive talking points

Prompt for eager entry, queue progress, shared scheduler and ordering-risk trade-off.

## Follow-up questions

- [TST-05](../tst-05/): Who controls virtual time? **Answer:** the shared TestCoroutineScheduler in TestScope.
- [TST-09](../tst-09/): Why eager collector setup? **Answer:** avoid subscription timing races in event tests.

## Self-check rubric

Can you explain the mechanism, reproduce the example, justify the trade-off, identify the failure case, and answer both follow-ups for this question?

## References and reviewed-on date

- [Kotlin TestDispatcher API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/) — dispatcher semantics.
- [Android coroutine testing](https://developer.android.com/kotlin/coroutines/test) — dispatcher usage.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
