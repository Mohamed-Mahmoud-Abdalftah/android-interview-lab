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

## Practical walkthrough

في كاشير POS، terminal تبعت authorization برقم `operationId` وتفصل الشبكة قبل الرد. اكتب `Unknown` بدل `Declined`، وخلّي التطبيق بعد restart يعمل status lookup لنفس الهوية. لو callback قديمة وصلت بعد تأكيد أحدث، transition guard تمنع الرجوع لحالة غير صحيحة. أسماء الحالات دي domain model؛ provider الحقيقي ممكن يستخدم حالات تانية ولازم mapping موثق.

## Why it matters and how it works

State transitions are guarded by server/provider evidence and transaction identity. A client callback can report observations, not final financial truth. Unknown is a first-class state that triggers status lookup, reconciliation or reversal under the payment contract. A terminal state should not be rewritten by a stale callback.

## Worked example

After sending authorization, the terminal loses network. Persist `unknown(operationId)` and show “checking status”; query backend/provider when connected. If authoritative status says approved, show approved; if a reversal is required, enqueue a durable reversal intent. Never create a new purchase ID for a retry.

### Kotlin/Android sketch

```kotlin
// Domain model; provider statuses must be mapped under its contract.
sealed interface PaymentState {
    data object Initiated : PaymentState
    data object Processing : PaymentState
    data object Unknown : PaymentState
    data class Approved(val providerRef: String) : PaymentState
    data class Declined(val reasonCode: String) : PaymentState
    data class Reversed(val reversalRef: String) : PaymentState
}
fun onTimeout(current: PaymentState): PaymentState =
    if (current == PaymentState.Processing) PaymentState.Unknown else current
```

## Trade-offs and decision criteria

A strict state machine adds implementation work but makes crash recovery and audit possible. Provider-specific states may be richer; map them carefully without collapsing pending/unknown into failure.

## Failure modes

UI navigation exits and discards `processing` state, then a late approval arrives. Persist before network send and let a repository/backend own transitions. Test duplicate callbacks, timeout then success and process death.

## Production perspective

Keep a transition table with allowed evidence, actor and durable write for each state. Log opaque IDs and state changes, reconcile unresolved records, and test against the provider’s documented authorization/reversal semantics.

## Interview answer — short

“I would treat Unknown as a real state, not a synonym for Declined. A POS timeout after authorization may hide an approval, so I retain the same operation ID, consult authoritative status, and only then advance the durable state.”

## Interview answer — structured

“I model initiated, processing, approved, declined, unknown and reversal states with guarded transitions. An authorization response can be lost after issuer approval, so a timeout means unknown. I persist the operation ID and state before sending, then query or reconcile through the backend. UI callbacks display state but do not create financial truth. Late or duplicate callbacks cannot overwrite a newer terminal state. For example, losing connectivity after authorization moves the attempt to Unknown, not Declined.”

## Interview answer — deep senior

“I define each transition with an evidence source, durable commit and replay behavior. The terminal records intent before external I/O, sends a stable operation identity, and treats transport errors as unknown. Reconciliation obtains authoritative provider state and can schedule a protocol-specific reversal. Concurrent duplicate responses converge through an atomic compare-and-set/transaction, and stale callbacks are ignored. The UI observes this state but does not own it. I test lost responses, battery removal, reversal failure and provider disagreement; the operational playbook handles states still unknown after automated lookup. I would ask the interviewer which response is authoritative and show how late callbacks are rejected after reconciliation. I would draw the transition table on the whiteboard: Initiated becomes Processing only after the local intent is committed; Processing becomes Approved or Declined only with a trusted response; and transport loss becomes Unknown. Reversed is not simply an opposite Boolean of Approved, because the acquirer's reversal acknowledgment and settlement timing determine what it means. Each transition needs a unique original operation ID, source of evidence, and idempotent database update. I would also name an explicit escalation state or operational queue for unresolved Unknown records. This makes it possible to audit why the terminal displayed a result and to repair the state after power loss.”

## How to answer in the interview

- **Why:** timeout leaves financial outcome unknown.
- **How:** tie every legal transition to evidence and a durable operation ID.
- **Trade-off:** the model must map richer provider states without inventing equivalence.
- **Failure case:** a late callback overwrites a reconciled result.
- **Production solution:** commit intent before I/O, guard transitions, and reconcile nonfinal rows.

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
