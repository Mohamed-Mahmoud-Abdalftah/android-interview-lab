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

Flaky UI test مش “طبيعي” لمجرد إن الاختبارات على emulator. جمّع failure evidence: seed، device/API، order، screenshots، logs ووقت الشبكة. لو test تنتظر 500ms ثابتة، استبدل live backend بfake response تتحكم في إطلاقها أو انتظر semantics state محددة بدل sleep.

## Practical walkthrough

Compose test clock تتحكم في animations، و`runTest` يتحكم في coroutines اللي داخل نطاقه؛ لا تفترض أنهما يتحكمان في كل SDK callback. اعزل DB وDI والـclock لكل test حتى لا تؤثر حالة اختبار سابق. أعد تشغيل الحالة منفردة ثم مع shard/ترتيب CI. Retry مؤقتًا للتشخيص أو quarantine بowner وexpiry، لكنه لا يثبت إن defect اختفى.

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

“I first determine whether the flake is product behavior, test synchronization or environment contamination. I preserve the failing seed, device image, build variant, screenshots, logs and test order; then reproduce the test alone and next to the preceding test in the same shard. If a checkout test sleeps 500 milliseconds for a network response, I replace the live dependency with a gate I control, assert Loading, release it and assert Approved or Unknown. I use semantics waits and Compose’s test clock for UI work, and a shared coroutine test scheduler only for coroutines it actually owns. Shared singleton fakes, database rows and leftover service workers must be reset between cases. A retry can collect evidence but is not a fix: it may turn a real race into a green dashboard. If quarantine is needed, I record an owner, affected coverage, expiry and a blocking replacement for critical payment or security paths. Finally I rerun enough repetitions and the original CI shard to show the causal change removed the failure.”

## How to answer in the interview

- **Why:** flaky green results undermine trust in the release gate.
- **How:** reproduce order/seed, replace sleeps with controlled fake and rerun original shard.
- **Trade-off:** quarantine can unblock work but leaves coverage debt.
- **Failure case:** retry masks an app race or shared singleton state.
- **Production solution:** owner, expiry, replacement gate and repeated verification.

## Deep-dive talking points

Prompt for first-failure evidence, synchronization, state isolation, bounded quarantine and app race.

## Follow-up questions

- [TST-21](../tst-21/): What if CI-only? **Answer:** compare device load, shard order and artifacts before changing timeout.
- [TST-06](../tst-06/): How control coroutine launch timing? **Answer:** TestDispatcher and shared scheduler.

## Self-check rubric

Reproduce the order-dependent or timing flake, remove wall-clock sleeps, control the fake response and Compose clock, and rerun the affected shard. Quarantine only with an owner, evidence and expiry.

## References and reviewed-on date

- [Android test reliability](https://developer.android.com/training/testing) — official testing practices.
- [Compose testing](https://developer.android.com/develop/ui/compose/testing) — clock/synchronization APIs.

Technically reviewed against the cited primary documentation on 2026-10-12; automated technical review only, not human review.
