---
id: "PAY-03"
question: "What are authorization, reversal, void, refund, and reconciliation?"
topic: "Bonus: Payment/POS & Security Scenarios"
code: "PAY"
group: "A"
phase: 5
priority: "P2"
order: 473
editorial_status: "reviewed"
---

# PAY-03

## Original interview question

What are authorization, reversal, void, refund, and reconciliation?

## What the interviewer evaluates

- Distinct meanings of authorization, reversal, void, refund and reconciliation.
- Provider/network-specific timing and state.

## Explanation in Arabic

Authorization طلب موافقة وحجز/اعتماد حسب rail؛ reversal رسالة لإلغاء أثر authorization غير محسوم أو لم يكتمل ضمن قواعد الشبكة؛ void يلغي عملية قبل settlement حسب provider؛ refund يرجّع مال بعد عملية مكتملة؛ reconciliation يطابق سجلات terminal/backend/provider ويكشف الفروق. الأسماء والتوقيت مش universal؛ لازم نلتزم بعقد acquirer.

## Practical walkthrough

لو authorization approved ولسه مش captured، void/cancel أو reversal ممكن ينفع حسب rail والنافذة الزمنية؛ بعد settlement refund غالبًا workflow جديدة. متستخدمش الأسماء كأنها API موحدة لكل acquirer. في المقابلة اربط كل operation بـoriginal reference، حالة التسوية، deadline، ودليل نهائي من provider.

## Why it matters and how it works

The payment lifecycle has separate business and accounting effects. An approved authorization is not automatically settled cash. Reversal, void and refund have different allowed windows, references and provider APIs. Reconciliation compares independent ledgers and resolves unknown/missing outcomes.

## Worked example

A POS authorization times out after the issuer approved it. The terminal marks unknown, queries status and may send a reversal with the original transaction reference under the acquirer protocol. If a settled customer purchase is returned days later, that is a refund workflow, not an authorization reversal.

## Trade-offs and decision criteria

Automatic reversal can limit open authorizations, but an incorrect reversal may conflict with completed sale state. Refunds have customer-service and fraud considerations. Decide only after authoritative status and provider-specific rules.

## Failure modes

Treating every timeout as “refund” can create a second financial movement even if the original payment never settled. Treating void and reversal as synonyms can call the wrong API. Maintain explicit states and protocol references.

## Production perspective

Document provider mapping and settlement cutoffs with payments specialists. Reconciliation jobs compare transaction IDs and amounts, flag mismatches, and route unresolved cases to operations without exposing PAN/PIN in logs.

## Interview answer — short

“I would first ask whether the payment is only authorized, captured, or settled. Then I choose the provider-supported cancellation, reversal, void, or refund flow and reconcile the resulting ledger entry.”

## Interview answer — structured

“These terms represent different lifecycle moments. Authorization is the approval request, not necessarily final settlement. A reversal addresses an authorization that should not stand, often after an uncertain terminal outcome; a void cancels a transaction before settlement under a provider’s rules; a refund is a new return of funds after completion. Reconciliation compares terminal, backend and provider records to resolve gaps. I follow the exact acquirer contract, because naming and windows vary. Refunds have customer-service and fraud considerations. A same-day uncaptured authorization and a return after settlement require different operations.”

## Interview answer — deep senior

“I build an explicit mapping from provider statuses and references to our state machine. A lost authorization response becomes unknown, prompting status lookup and possibly reversal tied to the original operation. A void is used only when the provider allows canceling an unsettled transaction; a refund has a separate authorization and idempotency identity after capture/settlement. Reconciliation runs independently of UI lifetime, compares ledgers by safe correlation IDs and investigates mismatches. I test duplicate reversals, late approvals and settlement cutoff transitions against the certified integration. Maintain explicit states and protocol references. I would not call a POS reversal a refund merely because both may restore customer funds. I would ask for the rail, provider, capture mode, and settlement status before naming a recovery action. An authorization may be a hold rather than collected funds. A void or cancellation can be available before capture or settlement, while a refund normally addresses a completed charge and has its own record and customer experience. A reversal in a POS protocol can be a specific message tied to the original transaction and strict timing; it is not a generic API alias for refund. Reconciliation is the evidence process that compares terminal, backend, and provider ledgers and finds missing or mismatched entries. I would document each operation's permitted window, original reference, acknowledgment, and retry policy.”

## How to answer in the interview

- **Why:** these operations act at different lifecycle and accounting stages.
- **How:** identify the original authorization, settlement state, and permitted provider action.
- **Trade-off:** provider vocabulary and windows vary.
- **Failure case:** treating a settled charge as voidable or a lost response as decline.
- **Production solution:** map the acquirer contract, record references, and reconcile ledgers.

## Deep-dive talking points

Prompt for lifecycle timing, original reference, separate refund identity and reconciliation ledger matching.

## Follow-up questions

- [PAY-01](../pay-01/): Why is unknown a state? **Answer:** timeout cannot prove issuer decline.
- [PAY-15](../pay-15/): How do reversals retry? **Answer:** durable original identity and provider-specific deduplication.

## Self-check rubric

Can I classify five terms by lifecycle stage and avoid assuming universal provider behavior?

## References and reviewed-on date

- [Stripe PaymentIntent lifecycle](https://docs.stripe.com/payments/paymentintents/lifecycle) — provider-specific authorization/capture states.
- [Stripe refunds](https://docs.stripe.com/refunds) — refund as separate workflow.

Technically reviewed against the cited primary documentation on 2026-10-11; this is an automated editorial and technical review, not a human review.
