---
id: "TST-15"
question: "How do you reduce flaky UI tests and control scheduling?"
topic: "Testing, Quality & Reliability"
code: "TST"
group: "B"
phase: 4
priority: "P1"
order: 410
editorial_status: "reviewed"
---

# TST-15

## Original interview question

How do you reduce flaky UI tests and control scheduling?

## What the interviewer evaluates

- Root causes of flakiness rather than blanket retries.
- Scheduler, network, state isolation and device control.

## Explanation in Arabic

Flaky UI test غالبًا سببه timing غير متحكم فيه، shared state، network حقيقية، animation أو device load. بدل `Thread.sleep` نستخدم test clock/idling، fake backend، reset database/permissions، وstable selectors. Retry في CI ممكن يكشف intermittency لكنه ما يصلحش العيب؛ نسجل first-failure evidence ونصلح السبب.

## Why it matters and how it works

Android/Compose test frameworks can synchronize with UI work they know about, but custom background work and external I/O need explicit idling or controlled dependencies. Isolate test data and reset device state. Reproduce with repeated focused runs and capture timeline.

## Worked example

A checkout UI test fails once in 30 runs because network response arrives after fixed 500 ms sleep. Replace live backend with a controllable fake, wait for the Loading node then release result, and assert Approved or Unknown. Use Compose test clock for animation, not wall time.

## Trade-offs and decision criteria

Fakes improve determinism but may hide integration faults; keep separate contract/E2E coverage. Longer timeouts reduce false failures but slow detection. Quarantine only with owner, deadline and release-risk decision.

## Failure modes

Automatic rerun that turns red into green conceals a race in production code. Record original failure, investigate scheduler/thread traces and shared test order. Do not delete a flaky security/payment test without replacement.

## Production perspective

CI stores screenshots, logs and test seed/attempt IDs with redaction. Track flake rate by test and device, and address highest-cost or highest-risk cases first.

## Interview answer — short

“I remove uncontrolled time and state: use scheduler/idling, fake network, reset fixtures and semantic selectors. Retries are diagnostic, not a fix, and quarantined tests need ownership and expiry.”

## Interview answer — structured

“I first identify whether the flake comes from app race, test synchronization, environment or shared data. I reproduce it with repeated focused runs and capture the first failure. I replace sleeps with UI synchronization or test clocks, control network responses and isolate database/permissions. A retry may keep CI moving temporarily but remains visible and time-limited. Critical payment and security tests stay release-gating unless an equivalent check exists.”

## Interview answer — deep senior

“I measure flake frequency and correlate it with device, OS, shard and test order. If a test waits on custom background work, I expose a deterministic completion signal rather than extend sleeps; if the app has a race, I fix production state ownership and add a lower-level test. Fakes handle UI determinism while contract/E2E tests still cover real integrations. I preserve artifacts from the first attempt even when a rerun passes, assign an owner and deadline to quarantine, and avoid normalizing flaky tests as harmless noise.”

## Deep-dive talking points

Prompt for first-failure evidence, synchronization, state isolation, bounded quarantine and app race.

## Follow-up questions

- [TST-21](../tst-21/): What if CI-only? **Answer:** compare device load, shard order and artifacts before changing timeout.
- [TST-06](../tst-06/): How control coroutine launch timing? **Answer:** TestDispatcher and shared scheduler.

## Self-check rubric

Can you explain the mechanism, reproduce the example, justify the trade-off, identify the failure case, and answer both follow-ups for this question?

## References and reviewed-on date

- [Android test reliability](https://developer.android.com/training/testing) — official testing practices.
- [Compose testing](https://developer.android.com/develop/ui/compose/testing) — clock/synchronization APIs.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
