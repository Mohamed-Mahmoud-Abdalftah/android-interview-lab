---
id: "PAY-08"
question: "How do you avoid duplicate payment requests after UI timeout?"
topic: "Bonus: Payment/POS & Security Scenarios"
code: "PAY"
group: "B"
phase: 5
priority: "P2"
order: 478
editorial_status: "reviewed"
---

# PAY-08

## Original interview question

How do you avoid duplicate payment requests after UI timeout?

## What the interviewer evaluates

- Timeout as unknown, not declined.
- Stable operation ID, authoritative lookup and guarded user retry.

## Explanation in Arabic

الـUI timeout معناه إن الرد ما وصلش، مش إن الدفع فشل. ممكن issuer وافق قبل انقطاع الاتصال. نخلي نفس operation ID ونظهر pending/unknown، نسأل backend/provider عن status، ونمنع زر “ادفع تاني” ينشئ charge جديد قبل حل النتيجة. لو retry مسموح نستخدم نفس idempotency key والparameters تحت عقد provider.

## Practical walkthrough

لو شاشة الدفع قالت timeout، رجّع حالة `Checking` لنفس `operationId` بدل تفتح زر Pay جديد فورًا. Repository تسأل status؛ لو unknown بعد كده، خلي checkout معلّقة وابدأ reconciliation. حتى لو UI اختفت ورجعت، ID من التخزين ترجع نفس العملية بدل charge جديدة.

## Why it matters and how it works

HTTP transport timeout gives no knowledge of remote commit. The app persists the intent before sending and observes a backend-owned state. The backend atomically deduplicates retries and exposes status lookup; provider retention windows and request-parameter rules vary.

## Worked example

A customer taps Pay, then the app times out. UI displays “Checking payment” with an opaque reference and allows safe resume after process death. The repository calls `lookup(operationId)`; if still unknown, it schedules reconciliation and keeps checkout locked to that intent rather than starting a new payment.

## Trade-offs and decision criteria

A conservative pending state adds user friction but avoids double charges. An immediate retry can be safe only when the same server/provider operation identity is honored. A cancel button may mean “stop waiting,” not “reverse approved payment.”

## Failure modes

Creating a new UUID on each button tap can double-charge. Marking timeout as declined can prompt the same mistake. Test response lost after server success and duplicate taps from two devices.

## Production perspective

Backend/terminal metrics track unresolved age and duplicate attempts. Customer support can query by operation ID without card data. Long-running unknown states have a reconciliation and escalation path.

## Interview answer — short

“After a UI timeout I show a recoverable pending state and keep the original payment identity. The repository looks up the authoritative result; a second tap does not create a new charge while the first remains unknown.”

## Interview answer — structured

“The server may have completed the charge even though the response was lost. I persist an operation ID and immutable parameters before sending, then show pending or unknown after timeout. The backend provides status lookup and enforces idempotency for retries with the same identity. Until authority resolves the result, the UI prevents a new charge for that purchase and survives process death. Provider-specific retention and replay semantics must be checked. A cancel button may mean “stop waiting,” not “reverse approved payment.” The customer sees one pending operation with a reference they can return to after process death.”

## Interview answer — deep senior

“I design the timeout path as part of the state machine, not an exception handler. The client cannot infer remote failure from a socket error, so it records unknown and resumes from durable identity after restart. The backend serializes same-ID requests, rejects parameter drift, queries provider state and reconciles late webhooks. I distinguish a retry of the same operation from a new customer purchase, because the latter needs a new ID. If lookup remains unknown beyond provider windows, operations handles the case; the UI does not claim approval or decline. Tests simulate server success with a lost response and duplicate taps. Creating a new UUID on each button tap can double-charge. I would test a timeout after issuer approval, then a repeated tap, to show no new operation ID is created. The UI can say 'checking payment' and give the customer an opaque reference, but it must not quietly create another authorization for the same purchase. I keep the operation ID and request fingerprint in durable storage before sending. After timeout the repository asks the backend for status; if the backend also lacks certainty, it consults the provider or waits for reconciliation. An explicit cancel action means stop waiting unless the payment contract confirms a financial cancellation. I would test a server commit with response loss, two rapid taps, process recreation, and a second device trying the same purchase. Those cases reveal whether the lock is only visual or enforced at the business boundary.”

## How to answer in the interview

- **Why:** timeout describes missing response, not failed authorization.
- **How:** persist the attempt, lock that intent, and query status before another charge.
- **Trade-off:** the user may wait while a genuine unknown is resolved.
- **Failure case:** new ID on retry causes duplicate charge.
- **Production solution:** stable-key server dedupe, recovery UI, and escalation for long unknowns.

## Deep-dive talking points

Prompt for lost response, same-key retry, parameter immutability, process death and long-unknown escalation.

## Follow-up questions

- [PAY-02](../pay-02/): What prevents duplicate business effects? **Answer:** server-side idempotency with stable identity.
- [PAY-01](../pay-01/): What state follows timeout? **Answer:** unknown until authoritative evidence arrives.

## Self-check rubric

Can I explain timeout ambiguity, durable identity, status lookup and safe UI behavior?

## References and reviewed-on date

- [Stripe idempotent requests](https://docs.stripe.com/api/idempotent_requests) — one provider’s retry semantics.
- [Android offline-first data layer](https://developer.android.com/topic/architecture/data-layer/offline-first) — persistent state recovery.

Technically reviewed against the cited primary documentation on 2026-10-11; this is an automated editorial and technical review, not a human review.
