---
id: "TST-20"
question: "Write tests for a payment retry path guaranteeing no duplicate charge."
topic: "Testing, Quality & Reliability"
code: "TST"
group: "C"
phase: 4
priority: "P1"
order: 415
editorial_status: "reviewed"
---

# TST-20

## Original interview question

Write tests for a payment retry path guaranteeing no duplicate charge.

## What the interviewer evaluates

- Lost-response test and distinction between local retry behavior and real server guarantee.
- Stable idempotency identity, process death and reconciliation.

## Explanation in Arabic

اختبار “no duplicate charge” لازم يحاكي server نفّذ charge لكن response ضاع. العميل يحتفظ بنفس operation ID والamount، يحوّل state لـunknown، ويسأل status أو يعيد بنفس key تحت عقد provider. Unit test يثبت client ما يولّدش UUID جديد؛ backend/provider integration test يثبت dedup atomically. من غير server contract ما نقدرش نضمن الأثر المالي.

## Why it matters and how it works

Idempotency protects one intended business effect across repeated deliveries; it does not make network execution exactly once. The server must bind key to immutable parameters and decide concurrent requests atomically. The client persists the identity before the first send.

## Worked example

Test sequence: create intent P1, fake server records approval then drops response, restart client repository, trigger retry, assert request uses P1 and original amount, and status becomes Approved via lookup. Run two concurrent P1 calls against backend test environment and assert one charge record.

## Trade-offs and decision criteria

Local test is fast but only checks emitted requests. Provider sandbox may differ from production retention/race behavior; document its contract and perform reconciliation tests. Conservative Unknown UI adds friction but avoids blind double charge.

## Failure modes

A mock returns timeout without recording a server effect, so test falsely assumes no charge. Explicitly place the fault after remote commit. Changed amount under same key must be rejected, not treated as a new operation.

## Production perspective

CI has unit/client HTTP tests, backend concurrency/idempotency tests, and provider sandbox reconciliation. Alerts watch duplicate IDs and unresolved unknowns without card data.

## Interview answer — short

“I simulate approval followed by lost response, then retry with the same durable operation ID and verify server-side deduplication. A client test alone cannot guarantee no duplicate charge.”

## Interview answer — structured

“I first persist an immutable payment intent and idempotency key. The test server commits one charge, then drops the reply so the client sees timeout. The client must show Unknown, reuse the key on retry or query status, and survive process death. A separate backend integration test sends concurrent same-key requests and proves only one business effect; changed parameters are rejected. Provider-specific retention and reconciliation remain part of the release plan. The mechanics matter. Idempotency protects one intended business effect across repeated deliveries; it does not make network execution exactly once. The server must bind key to immutable parameters and decide concurrent requests atomically. The client persists the identity before the first send. The choice has a trade-off. Local test is fast but only checks emitted requests. Provider sandbox may differ from production retention/race behavior; document its contract and perform reconciliation tests. Conservative Unknown UI adds friction but avoids blind double charge.”

## Interview answer — deep senior

“The critical assertion spans a trust boundary. A client test proves it does not change operation identity after timeout, including restart and duplicate taps; an HTTP test proves the header/body remain stable; a backend transaction test proves concurrent requests converge; a provider sandbox test validates its documented idempotency and status lookup. I inject the fault after the server commits, not before send, because that is the dangerous ambiguity. I also test key expiry and unresolved status, which require reconciliation rather than a blind new charge. No test justifies claiming exactly-once packet delivery. Consider a concrete case. Test sequence: create intent P1, fake server records approval then drops response, restart client repository, trigger retry, assert request uses P1 and original amount, and status becomes Approved via lookup. Run two concurrent P1 calls against backend test environment and assert one charge record. A failure case illustrates the risk. A mock returns timeout without recording a server effect, so test falsely assumes no charge. Explicitly place the fault after remote commit. Changed amount under same key must be rejected, not treated as a new operation. In production, the response is concrete. CI has unit/client HTTP tests, backend concurrency/idempotency tests, and provider sandbox reconciliation. Alerts watch duplicate IDs and unresolved unknowns without card data.”

## Deep-dive talking points

Prompt for after-commit fault, immutable parameters, concurrent server test, retention window and process death.

## Follow-up questions

- [PAY-02](../pay-02/): What does idempotency guarantee? **Answer:** one business effect under a server contract, not one HTTP execution.
- [PAY-08](../pay-08/): What does UI show? **Answer:** Unknown/pending until authority resolves status.

## Self-check rubric

Can you explain the mechanism, reproduce the example, justify the trade-off, identify the failure case, and answer both follow-ups for this question?

## References and reviewed-on date

- [Stripe idempotent requests](https://docs.stripe.com/api/idempotent_requests) — provider-specific contract.
- [Android offline-first data layer](https://developer.android.com/topic/architecture/data-layer/offline-first) — durable client state.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
