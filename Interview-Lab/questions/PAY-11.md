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

## Practical walkthrough

في fake SDK اعمل clock قابلة للتحكم: timeout ييجي الأول وبعده callback Approved، أو callback مرتين، أو disconnect والعملية لسه remote pending. اختبر إن local state ما تتحولش Declined تلقائيًا وإن restart يعمل lookup بنفس ID. بعد unit tests لازم hardware test: firmware ممكن تعمل callbacks بترتيب مختلف عن fake.

## Why it matters and how it works

A domain test can inject a fake clock and scripted SDK callbacks to assert state transitions and durable outbox writes. The adapter contract must distinguish transport failure from authoritative decline. Hardware tests verify actual vendor semantics and recovery references.

## Worked example

Test sequence: persist attempt, invoke authorize, deliver no callback until timeout, assert UNKNOWN with same operation ID; then deliver late Approved and assert guarded transition or reconciliation. Restart repository from database and verify status lookup, not a second charge.

### Kotlin/Android sketch

```kotlin
// Domain test: fake maps an elapsed SDK timeout to Unknown; not an issuer.
@Test fun timeoutStaysUnknownUntilLookup() = runTest {
    val fake = ScriptedGateway(initial = TerminalOutcome.Unknown)
    val repo = PaymentRepository(fake, inMemoryAttempts())
    val id = "op-42"
    repo.start(id, amountMinor = 1_250)
    assertEquals(PaymentState.Unknown, repo.state(id))
    fake.lookupResult = TerminalOutcome.Approved("provider-7")
    repo.reconcile(id)
    assertTrue(repo.state(id) is PaymentState.Approved)
}
// ScriptedGateway/PaymentRepository are test doubles/app contracts.
// Imports: kotlinx.coroutines.test.runTest; org.junit.Test/Assert.*.
// Separate tests inject late and duplicate callbacks and a fake clock.
```

## Trade-offs and decision criteria

Fakes are fast and exhaustive for ordering but cannot model all firmware, power and EMV behavior. Real terminal tests are slower and may need a provider sandbox or certification environment; include both.

## Failure modes

A test only checks that UI shows an error after timeout; it misses duplicate charge risk. Another test cancels a coroutine and assumes SDK payment canceled. Assert server-side identity and reversal/reconciliation obligations explicitly.

## Production perspective

Keep a failure matrix by device model, firmware, ABI, SDK version and network mode. Release smoke tests run on actual hardware where possible and preserve redacted operation IDs for support.

## Interview answer — short

“I inject a fake gateway and clock to force the race: timeout first, approval later. The domain must keep Unknown until it has authoritative evidence, and hardware tests must confirm the adapter’s real callback behavior.”

## Interview answer — structured

“I test the state machine with a fake SDK and fake clock: no callback, callback after timeout, duplicate success, disconnect and process death. Each test asserts the persisted operation ID and whether status lookup or reversal is required. Then I repeat critical flows on real terminals and provider sandbox because firmware and EMV behavior cannot be inferred from mocks. I check that a retry never creates a new charge identity. The fake controls a late approval after timeout, and the hardware test checks whether the vendor actually behaves that way.”

## Interview answer — deep senior

“The test oracle is financial correctness, not merely a screen message. I inject faults at every durable boundary: before send, after provider approval but before callback, after callback but before DB commit, and during reversal. Tests restart the process from the same DB, replay late/duplicate callbacks, and verify one intended business effect under the backend’s idempotency contract. I also test SDK cancellation semantics separately from coroutine cancellation. Real device unplug/battery/network drills reveal vendor-specific recovery references and ABI/firmware bugs that fakes cannot cover. I assert database state after restart, not only the callback value seen by a still-open Activity. The first deterministic test makes the adapter return Unknown after its timeout and then delivers a late Approved callback. I verify that the repository neither creates a new attempt nor blindly trusts a stale callback over a reconciled state. Another test sends the callback twice; a third kills the process before final persistence and checks restart lookup. I inject clock and callback order where possible, then test the vendor adapter on actual supported terminals with a controllable network and power interruption. Fakes prove domain decisions, but they cannot validate firmware error codes or the acquirer's interpretation of a reversal. I would record the exact SDK build and hardware model for each test run.”

## How to answer in the interview

- **Why:** callback timing does not equal issuer truth.
- **How:** script timeout, late approval, duplicate callback, and disconnect around one attempt.
- **Trade-off:** fakes make deterministic tests but cannot prove firmware behavior.
- **Failure case:** cancellation hides an already approved payment.
- **Production solution:** device matrix, crash/restart drills, and provider reconciliation tests.

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
