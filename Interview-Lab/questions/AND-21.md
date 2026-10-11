---
id: "AND-21"
question: "A payment screen is killed by Android mid-operation. What must be reconstructed, and what must not be repeated?"
topic: "Android Fundamentals, Lifecycle & Context"
code: "AND"
group: "C"
phase: 1
priority: "P1"
order: 51
editorial_status: "reviewed"
---

# AND-21

## Original interview question

A payment screen is killed by Android mid-operation. What must be reconstructed, and what must not be repeated?

## What the interviewer evaluates

- Treat a lost client response as an unknown outcome rather than proof of failure.
- Separate reconstructable UI state from durable transaction identity and server authority.
- Explain safe retry, idempotency, reconciliation, and process-death testing.

## Explanation in Arabic

لو Android قتل process أثناء الدفع، الـscreen وViewModel وcoroutine كلهم يختفوا. لازم يكون عندك قبل إرسال الطلب `attemptId` وidempotency key محفوظين بشكل durable، مع order ID وحالة محلية مثل pending. عند الرجوع، تبني الـUI من البيانات المحفوظة وتستعلم من الـbackend عن حالة نفس العملية. ما تعيدش `charge` جديد تلقائيًا لمجرد إن الـclient ما شافش الرد: ممكن الخادم يكون نفّذ الدفع فعلًا والرد ضاع. كمان ما تعتبرش local success flag دليلًا نهائيًا؛ الـserver والـpayment provider هما مصدر الحقيقة حسب العقد. لو النتيجة unknown، اظهرها بصراحة وواصل reconciliation بدل تخمين النجاح أو الفشل.

## Why it matters and how it works

Process death destroys in-memory state and may occur after the server committed a payment but before the device received a response. The app therefore needs durable operation identity written before submission, an API contract that binds retries to the same idempotency key and unchanged parameters, and a status endpoint or webhook-backed backend record. On restoration, read the persisted attempt, authenticate the user, fetch authoritative status, then render succeeded, declined, pending, or unknown. Small saved UI state may restore the selected screen, but it is not the payment ledger.

## Worked example

Illustrative sequence with an app database and server contract: `transaction { insert(attemptId, orderId, idempotencyKey, PENDING) }`; submit the order through the backend; if the HTTP response is lost, persist `UNKNOWN` for this attempt rather than another new attempt; on screen recreation, fetch `GET /payment-attempts/{attemptId}`. A retry is permitted only when backend semantics explicitly accept the same key and payload. The pseudocode is architectural; the endpoint and atomicity guarantees must be provided by the actual backend.

## Trade-offs and decision criteria

Immediate screen reconciliation improves feedback but requires connectivity; scheduled recovery with WorkManager can continue after the UI leaves, subject to OS scheduling and network constraints. Server webhooks can establish eventual status but need authentication, replay defense, and duplicate handling. Local Room persistence helps the client remember identity, yet cannot make a charge exactly once. Provider idempotency is scoped to its documented retention and parameter rules; the backend should own the durable business transaction and avoid relying solely on a client-generated key.

## Failure modes

A naive `onCreate { charge() }` creates a second charge after recreation. A timeout handler that labels the payment failed might falsely encourage the user to pay again. A key reused with different amount or merchant data can be rejected or produce unsafe semantics. A local success flag can be stale or tampered with. Handle explicit declines, timeout/unknown, authentication expiry, and server status unavailability separately; alert operations on attempts stuck pending beyond a defined threshold.

## Production perspective

Persist attempt identity before submission, bind it to authenticated order and amount on the backend, and make status reads safe to repeat. The screen observes a repository that reconciles local state with server state. A unique WorkManager job may retry *status lookup* after restart; it should not initiate a new financial operation unless the server contract proves it safe. Tests inject process death before request, after server commit/before response, and during reconciliation, then assert one logical attempt and a recoverable UI. Log opaque attempt IDs rather than card data.

## Interview answer — short

“I reconstruct the screen from a persisted attempt ID and query the backend for the actual payment status. I do not repeat the charge because a missing response could mean the server committed it. The same operation needs an idempotency contract, and unknown status must remain explicit until reconciled.”

## Interview answer — structured

“Before sending payment, I persist a unique attempt and idempotency key. If Android kills the process, the ViewModel is gone, so on return I reload the attempt and ask the server whether it succeeded, declined, or remains pending. I restore minor UI inputs separately. A transport timeout is an unknown outcome, not a failed payment, and I never create a new charge just because the Activity restarted. Retrying the same request is allowed only under a documented backend/provider idempotency contract.”

## Interview answer — deep senior

“I treat payment as a distributed state machine whose authority is the backend, not the Activity. The device durably records attempt identity before the request; the backend binds that identity to authenticated order, amount, and provider call. A process kill may cut the response path at any point, so recovery first performs an authenticated status read. We model pending and unknown separately from success and decline, and use the same idempotency key only under the provider's documented parameter and retention rules. WorkManager may schedule reconciliation, while the visible screen can query immediately. I test kill points around persistence, send, provider commit, response, and status lookup, and monitor stuck unknown attempts without exposing card data.”

## Deep-dive talking points

Discuss write-before-send ordering, uncertain network outcomes, provider versus backend idempotency scope, status read versus charge retry, webhook reconciliation, process-death testing, and how to avoid logging sensitive payment material.

## Follow-up questions

- [AND-07](../and-07/): Does ViewModel preserve the attempt? **Answer:** no; it is lost with the process, so persist attempt identity first.
- [PAY-02](../pay-02/): Can a timeout be treated as decline? **Answer:** no; it is unknown until backend reconciliation.
- [PAY-04](../pay-04/): Does idempotency imply exactly-once execution? **Answer:** no; it controls duplicate effects only within the specific server/provider contract.

## Self-check rubric

Place the durable write before the network send; distinguish timeout from decline; identify the backend as status authority; describe one safe retry condition; and test at least three process-kill points without issuing a second logical payment.

## References and reviewed-on date

- [Android save UI states](https://developer.android.com/topic/libraries/architecture/saving-states) — process restoration and saved-state limits.
- [Android persistent work](https://developer.android.com/develop/background-work/background-tasks/persistent) — recovery scheduling limits.
- [Stripe idempotent requests](https://docs.stripe.com/api/idempotent_requests) — one provider's documented key and parameter semantics; other providers require their own contract review.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. The endpoint sequence is illustrative; no real payment backend was implemented or tested here.
