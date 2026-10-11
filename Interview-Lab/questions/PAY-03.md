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

“Authorization requests approval; reversal unwinds an authorization under network rules; void cancels before settlement when supported; refund returns funds after a completed charge; reconciliation matches independent records.”

## Interview answer — structured

“These terms represent different lifecycle moments. Authorization is the approval request, not necessarily final settlement. A reversal addresses an authorization that should not stand, often after an uncertain terminal outcome; a void cancels a transaction before settlement under a provider’s rules; a refund is a new return of funds after completion. Reconciliation compares terminal, backend and provider records to resolve gaps. I follow the exact acquirer contract, because naming and windows vary.”

## Interview answer — deep senior

“I build an explicit mapping from provider statuses and references to our state machine. A lost authorization response becomes unknown, prompting status lookup and possibly reversal tied to the original operation. A void is used only when the provider allows canceling an unsettled transaction; a refund has a separate authorization and idempotency identity after capture/settlement. Reconciliation runs independently of UI lifetime, compares ledgers by safe correlation IDs and investigates mismatches. I test duplicate reversals, late approvals and settlement cutoff transitions against the certified integration.”

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
