---
id: "PAY-01"
question: "What is a payment state machine (initiated, processing, approved, declined, unknown, reversed)?"
topic: "Bonus: Payment/POS & Security Scenarios"
code: "PAY"
group: "A"
phase: 5
priority: "P2"
order: 471
editorial_status: "reviewed"
---

# PAY-01

## Original interview question

What is a payment state machine (initiated, processing, approved, declined, unknown, reversed)?

## What the interviewer evaluates

- Explicit legal transitions and unknown state.
- Separation of terminal display, backend/provider truth and reversal.

## Explanation in Arabic

Payment state machine بتحدد انتقالات مسموحة: `initiated` قبل الإرسال، `processing` أثناء محاولة، `approved` أو `declined` بعد رد موثوق، `unknown` لما الرد ضاع، و`reversed` بعد تأكيد إلغاء الأثر وفق بروتوكول الـprovider. الـtimeout مش `declined`؛ ممكن issuer وافق والرد ما وصلش. كل transition لازم مربوط بـoperation ID ثابت ويتسجل durably.

## Why it matters and how it works

State transitions are guarded by server/provider evidence and transaction identity. A client callback can report observations, not final financial truth. Unknown is a first-class state that triggers status lookup, reconciliation or reversal under the payment contract. A terminal state should not be rewritten by a stale callback.

## Worked example

After sending authorization, the terminal loses network. Persist `unknown(operationId)` and show “checking status”; query backend/provider when connected. If authoritative status says approved, show approved; if a reversal is required, enqueue a durable reversal intent. Never create a new purchase ID for a retry.

## Trade-offs and decision criteria

A strict state machine adds implementation work but makes crash recovery and audit possible. Provider-specific states may be richer; map them carefully without collapsing pending/unknown into failure.

## Failure modes

UI navigation exits and discards `processing` state, then a late approval arrives. Persist before network send and let a repository/backend own transitions. Test duplicate callbacks, timeout then success and process death.

## Production perspective

Keep a transition table with allowed evidence, actor and durable write for each state. Log opaque IDs and state changes, reconcile unresolved records, and test against the provider’s documented authorization/reversal semantics.

## Interview answer — short

“A payment state machine makes `unknown` explicit after timeout. Only authoritative provider or backend evidence moves a transaction to approved, declined or reversed; retries retain one operation identity.”

## Interview answer — structured

“I model initiated, processing, approved, declined, unknown and reversal states with guarded transitions. An authorization response can be lost after issuer approval, so a timeout means unknown. I persist the operation ID and state before sending, then query or reconcile through the backend. UI callbacks display state but do not create financial truth. Late or duplicate callbacks cannot overwrite a newer terminal state. ”

## Interview answer — deep senior

“I define each transition with an evidence source, durable commit and replay behavior. The terminal records intent before external I/O, sends a stable operation identity, and treats transport errors as unknown. Reconciliation obtains authoritative provider state and can schedule a protocol-specific reversal. Concurrent duplicate responses converge through an atomic compare-and-set/transaction, and stale callbacks are ignored. The UI observes this state but does not own it. I test lost responses, battery removal, reversal failure and provider disagreement; the operational playbook handles states still unknown after automated lookup.”

## Deep-dive talking points

Prompt for transition table, unknown timeout, durable intent, late callback ordering and provider evidence.

## Follow-up questions

- [PAY-02](../pay-02/): Why stable identity? **Answer:** retries must not create a second business operation.
- [PAY-12](../pay-12/): What after power loss? **Answer:** load durable intent and reconcile issuer/backend state.

## Self-check rubric

Can I distinguish timeout from decline, identify authoritative transitions and describe recovery?

## References and reviewed-on date

- [Stripe PaymentIntent lifecycle](https://docs.stripe.com/payments/paymentintents/lifecycle) — one provider’s state model.
- [Android offline-first data layer](https://developer.android.com/topic/architecture/data-layer/offline-first) — durable local data concepts.

Technically reviewed against the cited primary documentation on 2026-10-11; this is an automated editorial and technical review, not a human review.
