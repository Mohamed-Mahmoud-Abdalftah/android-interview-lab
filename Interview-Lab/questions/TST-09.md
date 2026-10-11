---
id: "TST-09"
question: "How do you test Flow, StateFlow, and SharedFlow with Turbine?"
topic: "Testing, Quality & Reliability"
code: "TST"
group: "B"
phase: 4
priority: "P1"
order: 404
editorial_status: "reviewed"
---

# TST-09

## Original interview question

How do you test Flow, StateFlow, and SharedFlow with Turbine?

## What the interviewer evaluates

- Hot-flow subscription timing and replay/conflation semantics.
- Turbine assertions with deterministic scheduling.

## Explanation in Arabic

`Flow` البارد يبدأ عند collect؛ `StateFlow` hot وله current value وconflation بالمساواة؛ `SharedFlow` hot وreplay/buffer حسب configuration. Turbine تساعد `awaitItem()` و`expectNoEvents()` و`cancelAndIgnoreRemainingEvents()`، لكن لازم subscriber يبدأ قبل event لو replay=0. `runTest` وtest dispatcher يخلّوا التوقيت واضح.

## Why it matters and how it works

Turbine collects a Flow in a test scope. StateFlow may suppress equal updates and conflate fast changes, so a test must not demand every intermediate value unless scheduling ensures collection. SharedFlow with replay zero does not deliver past emissions to a late collector.

## Worked example

Illustrative test: `runTest { viewModel.state.test { assertEquals(Idle, awaitItem()); viewModel.load(); runCurrent(); assertEquals(Loading, awaitItem()); ... } }`. Requires Turbine, `kotlinx-coroutines-test`, JUnit assertions, and a fake repository whose completion is controlled; the ellipsis marks a sketch, not compilable code.

## Trade-offs and decision criteria

Turbine makes asynchronous assertions readable, but careless `advanceUntilIdle` can collapse intermediate StateFlow states. For one-shot UI events, design delivery and lifecycle explicitly rather than assuming SharedFlow is lossless.

## Failure modes

Emitting to SharedFlow before the test collector starts causes a missed event and apparent flake. Use subscription awareness or replay only if product semantics require it. Do not use replay solely to make the test pass if duplicate delivery is wrong.

## Production perspective

Test collector start, configuration recreation, lifecycle stop/start, equal-value updates and buffer overflow. Use stable fake sources and virtual time; integration UI tests verify actual collection behavior.

## Interview answer — short

“Turbine helps assert Flow emissions, but I account for cold versus hot flow semantics. StateFlow conflates/equality-suppresses updates, and a replay-zero SharedFlow can miss emissions before subscription.”

## Interview answer — structured

“I collect under runTest with a controlled scheduler and assert items in order with Turbine. A cold Flow starts on collection; StateFlow immediately exposes current state and can suppress equal updates; SharedFlow delivery depends on replay and buffer policy. I start collectors before emitting when appropriate, assert no unexpected events, and close the Turbine scope. I separately test lifecycle collection for UI behavior. The mechanics matter. Turbine collects a Flow in a test scope. StateFlow may suppress equal updates and conflate fast changes, so a test must not demand every intermediate value unless scheduling ensures collection. SharedFlow with replay zero does not deliver past emissions to a late collector. The choice has a trade-off. Turbine makes asynchronous assertions readable, but careless `advanceUntilIdle` can collapse intermediate StateFlow states. For one-shot UI events, design delivery and lifecycle explicitly rather than assuming SharedFlow is lossless.”

## Interview answer — deep senior

“I write tests around the semantic contract, not just an expected list. For StateFlow I decide whether intermediate Loading is observable under my scheduler; conflation can erase rapid transitions, so I control the fake repository’s timing. For SharedFlow I test subscriber timing, replay, extra-buffer capacity and overflow, especially after configuration changes. Turbine’s timeout and cancellation behavior help detect hanging collectors, but the app’s actual lifecycle collection is still a device/UI concern. I avoid changing replay to satisfy a flaky test without deciding whether duplicate event delivery is acceptable. Consider a concrete case. Illustrative test: `runTest { viewModel.state.test { assertEquals(Idle, awaitItem()); viewModel.load(); runCurrent(); assertEquals(Loading, awaitItem()); ... } }`. Requires Turbine, `kotlinx-coroutines-test`, JUnit assertions, and a fake repository whose completion is controlled; the ellipsis marks a sketch, not compilable code. A failure case illustrates the risk. Emitting to SharedFlow before the test collector starts causes a missed event and apparent flake. Use subscription awareness or replay only if product semantics require it. Do not use replay solely to make the test pass if duplicate delivery is wrong. In production, the response is concrete. Test collector start, configuration recreation, lifecycle stop/start, equal-value updates and buffer overflow. Use stable fake sources and virtual time; integration UI tests verify actual collection behavior.”

## Deep-dive talking points

Prompt for cold/hot collection, StateFlow equality, SharedFlow replay and collector startup.

## Follow-up questions

- [TST-06](../tst-06/): Which dispatcher can start collectors eagerly? **Answer:** UnconfinedTestDispatcher, used deliberately.
- [TST-18](../tst-18/): What does lifecycle add? **Answer:** collectors stop/restart and may miss or repeat events.

## Self-check rubric

Can you explain the mechanism, reproduce the example, justify the trade-off, identify the failure case, and answer both follow-ups for this question?

## References and reviewed-on date

- [Kotlin StateFlow/SharedFlow](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-state-flow/) — StateFlow semantics.
- [Turbine README](https://github.com/cashapp/turbine) — testing API.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
