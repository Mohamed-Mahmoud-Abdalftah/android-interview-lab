---
id: "SEC-27"
question: "An attacker modifies an APK and bypasses client-only checks. How should the backend defend itself?"
topic: "Android Security, Crypto & Fintech Threat Modeling"
code: "SEC"
group: "C"
phase: 3
priority: "P1"
order: 324
editorial_status: "reviewed"
---

# SEC-27

## Original interview question

An attacker modifies an APK and bypasses client-only checks. How should the backend defend itself?

## What the interviewer evaluates

- A repackaged APK can forge all client-only decisions.
- Backend reconstruction of identity, price, state and replay protection.

## Explanation in Arabic

لو attacker عدّل APK وعدّى client check، backend ما ينفعش يصدق `approved=true` أو amount جاي من الواجهة. يجيب price والـownership والـtransaction state من قواعده، يتحقق من session وحدود الحساب، ويربط request بـoperation ID ثابت عشان retries ما تعملش charge تاني. App attestation signal مفيد، بس مش بديل للقرار السيرفري.

## Practical walkthrough

APK معدّلة بعتت `amountMinor=1` لطلب ثمنه الحقيقي 10000. backend يجيب السعر والعملة وحالة order من DB بدل request، ويتحقق من session والownership، ثم ينفّذ transition واحدة مرتبطة بـoperation ID ثابت. حتى لو Play Integrity قال app سليمة، ده ما يعفيش server من تحقق amount والحدود؛ وأي timeout مع provider يحتاج reconciliation.

## Why it matters and how it works

Client input is untrusted regardless of app signing or obfuscation. The backend validates authenticated principal, authorization for resource, canonical pricing, legal state transition and replay/idempotency contract inside a transaction. Provider callbacks are verified via their documented mechanism and reconciled against server records.

## Worked example

A patched checkout sends `{itemId, amountMinor: 1, approved: true}`. The server reads product price and pending order from its database, rejects amount mismatch, creates one operation ID and calls the provider under an idempotency contract. It marks approved only after an authoritative provider result.

## Trade-offs and decision criteria

Recomputing business state server-side costs backend complexity but is necessary for financial authority. Integrity checks may add fraud signals and friction; their absence should follow a documented tiered policy rather than make forged values acceptable.

## Failure modes

Relying on a local signature or native SDK Boolean for charge approval permits tampering. Racing two identical requests can also create duplicates if server-side uniqueness is not atomic. Test modified APK requests and concurrent retries.

## Production perspective

Backend tests include changed amount, foreign order ID, stale state, duplicate operation and provider callback replay. Audit logs use opaque IDs; fraud monitoring flags inconsistent device signals without storing sensitive payloads.

## Interview answer — short

“A modified APK controls every client-only check. The backend must authenticate, authorize, derive price and state from trusted records, enforce idempotency, and confirm provider outcomes before changing financial state.”

## Interview answer — structured

“I assume the attacker can change UI flags and request fields. The server validates the user’s ownership, canonical amount, order state and allowed transition, then uses a stable idempotency identity for the provider call. It verifies provider results independently and never accepts a client `approved` value. Play Integrity may inform risk scoring, but server business rules remain mandatory even for a recognized app. ”

## Interview answer — deep senior

“For a payment endpoint I define an invariant: one order and operation identity can cause at most one intended financial effect under the provider contract. Within a server transaction I check the authenticated account, server-priced order, allowed state transition and uniqueness; I record an operation before external work and reconcile unknown outcomes. Concurrent requests with the same identity converge, while changed parameters are rejected. Provider webhooks or status lookups require verification. I test requests from a repackaged client that lie about price, success and device trust, plus retries after lost responses. No local control can confer authority. For payments I would make the server's state transition and provider idempotency contract explicit. The same operation ID must not cause a second intended charge during retries, and a timeout is Pending until the provider or ledger resolves it. I would fuzz the endpoint with altered amount, currency, account and `approved` flags from a modified client. Integrity signals can add context but never replace these server checks.”

## How to answer in the interview

- **Why:** all client fields and checks can be forged.
- **How:** recompute canonical amount and allowed state server-side before payment.
- **Trade-off:** server validation adds reads and coordination.
- **Failure case:** trusting approved=true or a client price.
- **Production solution:** transactional idempotency plus provider reconciliation.

## Deep-dive talking points

Prompt for canonical server price, authorization, atomic uniqueness, provider confirmation and tampered-client tests.

## Follow-up questions

- [PAY-02](../pay-02/): Why stable operation ID? **Answer:** retries must converge on one business intent.
- [SEC-21](../sec-21/): What role for Integrity? **Answer:** a server-verified risk signal, not authorization.

## Self-check rubric

Can I reject a forged amount/status and describe duplicate-request protection?

## References and reviewed-on date

- [Play Integrity overview](https://developer.android.com/google/play/integrity/overview) — server-side decisions.
- [Stripe idempotent requests](https://docs.stripe.com/api/idempotent_requests) — one provider’s retry contract.

Technically reviewed against the cited primary documentation on 2026-10-13; this is an automated editorial and technical review, not a human review.
