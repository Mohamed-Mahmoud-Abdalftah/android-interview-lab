---
id: "PAY-11"
question: "How would you test SDK callback timeout and device disconnection?"
topic: "Bonus: Payment/POS & Security Scenarios"
code: "PAY"
group: "B"
phase: 5
priority: "P2"
order: 481
editorial_status: "reviewed"
---

# PAY-11

## Original interview question

How would you test SDK callback timeout and device disconnection?

## What the interviewer evaluates

- Deterministic callback/time control plus real device disconnection tests.
- Lost response, duplicate callback and late success cases.

## Explanation in Arabic

لازم نختبر SDK timeout/disconnect كـunknown financial outcome، مش بس exception في UI. Fake adapter يتحكم في callback order والوقت: success بعد timeout، callback مرتين، disconnection أثناء authorization، process kill. وhardware tests تفصل الجهاز أو الشبكة فعلًا؛ fake وحده ما يثبتش behavior بتاع firmware/acquirer.

## Why it matters and how it works

A domain test can inject a fake clock and scripted SDK callbacks to assert state transitions and durable outbox writes. The adapter contract must distinguish transport failure from authoritative decline. Hardware tests verify actual vendor semantics and recovery references.

## Worked example

Test sequence: persist attempt, invoke authorize, deliver no callback until timeout, assert UNKNOWN with same operation ID; then deliver late Approved and assert guarded transition or reconciliation. Restart repository from database and verify status lookup, not a second charge.

## Trade-offs and decision criteria

Fakes are fast and exhaustive for ordering but cannot model all firmware, power and EMV behavior. Real terminal tests are slower and may need a provider sandbox or certification environment; include both.

## Failure modes

A test only checks that UI shows an error after timeout; it misses duplicate charge risk. Another test cancels a coroutine and assumes SDK payment canceled. Assert server-side identity and reversal/reconciliation obligations explicitly.

## Production perspective

Keep a failure matrix by device model, firmware, ABI, SDK version and network mode. Release smoke tests run on actual hardware where possible and preserve redacted operation IDs for support.

## Interview answer — short

“I script timeout, duplicate and late callbacks in adapter tests, then run hardware disconnection/power tests. A timeout stays unknown until provider status resolves it; coroutine cancellation does not prove payment cancellation.”

## Interview answer — structured

“I test the state machine with a fake SDK and fake clock: no callback, callback after timeout, duplicate success, disconnect and process death. Each test asserts the persisted operation ID and whether status lookup or reversal is required. Then I repeat critical flows on real terminals and provider sandbox because firmware and EMV behavior cannot be inferred from mocks. I check that a retry never creates a new charge identity. The mechanics matter. A domain test can inject a fake clock and scripted SDK callbacks to assert state transitions and durable outbox writes. The adapter contract must distinguish transport failure from authoritative decline. Hardware tests verify actual vendor semantics and recovery references. The choice has a trade-off. Fakes are fast and exhaustive for ordering but cannot model all firmware, power and EMV behavior. Real terminal tests are slower and may need a provider sandbox or certification environment; include both.”

## Interview answer — deep senior

“The test oracle is financial correctness, not merely a screen message. I inject faults at every durable boundary: before send, after provider approval but before callback, after callback but before DB commit, and during reversal. Tests restart the process from the same DB, replay late/duplicate callbacks, and verify one intended business effect under the backend’s idempotency contract. I also test SDK cancellation semantics separately from coroutine cancellation. Real device unplug/battery/network drills reveal vendor-specific recovery references and ABI/firmware bugs that fakes cannot cover. Consider a concrete case. Test sequence: persist attempt, invoke authorize, deliver no callback until timeout, assert UNKNOWN with same operation ID; then deliver late Approved and assert guarded transition or reconciliation. Restart repository from database and verify status lookup, not a second charge. A failure case illustrates the risk. A test only checks that UI shows an error after timeout; it misses duplicate charge risk. Another test cancels a coroutine and assumes SDK payment canceled. Assert server-side identity and reversal/reconciliation obligations explicitly. In production, the response is concrete. Keep a failure matrix by device model, firmware, ABI, SDK version and network mode. Release smoke tests run on actual hardware where possible and preserve redacted operation IDs for support.”

## Deep-dive talking points

Prompt for fake clock/callback order, persisted-state assertions, cancellation distinction and hardware matrix.

## Follow-up questions

- [PAY-08](../pay-08/): What does timeout mean? **Answer:** unknown until authority resolves it.
- [PAY-09](../pay-09/): What does an adapter fake test? **Answer:** domain mapping/order, not certified hardware behavior.

## Self-check rubric

Can I propose a failure matrix that checks financial state, not just UI exceptions?

## References and reviewed-on date

- [Android testing guidance](https://developer.android.com/training/testing) — test layers and device tests.
- [Kotlin cancellation](https://kotlinlang.org/docs/cancellation-and-timeouts.html) — cancellation semantics.

Technically reviewed against the cited primary documentation on 2026-10-11; this is an automated editorial and technical review, not a human review.
