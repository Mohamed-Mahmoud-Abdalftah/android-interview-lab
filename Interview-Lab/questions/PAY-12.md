---
id: "PAY-12"
question: "A POS transaction is approved by issuer but the terminal loses power before saving it. Describe recovery and reconciliation."
topic: "Bonus: Payment/POS & Security Scenarios"
code: "PAY"
group: "C"
phase: 5
priority: "P2"
order: 482
editorial_status: "reviewed"
---

# PAY-12

## Original interview question

A POS transaction is approved by issuer but the terminal loses power before saving it. Describe recovery and reconciliation.

## What the interviewer evaluates

- Recovery when issuer approved but terminal lost power before local save.
- Need for backend/provider record and reconciliation beyond local DB.

## Explanation in Arabic

ده أسوأ crash window: issuer وافق، terminal اتطفت قبل ما تحفظ approval. لو حفظنا intent والـoperation ID قبل الإرسال نقدر بعد reboot نسأل backend/provider. لو حتى intent ما اتحفظتش، terminal وحدها ما تقدرش تثبت النتيجة؛ لازم backend/acquirer ledger وbatch reconciliation يطابقوا العملية. ما نعيدش charge بهوية جديدة.

## Why it matters and how it works

Local and remote commits cannot be atomic. A write-ahead attempt reduces uncertainty, while server operation records and provider references supply independent evidence. Reconciliation compares terminal, backend and issuer/acquirer status; a protocol-specific reversal may be required when sale completion cannot be confirmed.

## Worked example

On restart, load nonterminal attempts and query status by original operation ID. If approval is found, persist it and decide whether the sale can complete or needs reversal under the acquirer’s rules. If no local attempt survived, backend reconciles provider records using terminal/batch references and raises an operations case.

## Trade-offs and decision criteria

More durable pre-send writes add latency but reduce orphaned approvals. Local backup is insufficient for a physically destroyed terminal; central records are necessary. Provider status APIs may be delayed, so unknown may persist temporarily.

## Failure modes

Marking the transaction declined because no local row exists can prompt a second charge. Trusting a new local row to undo issuer approval is also wrong. Test power removal at every point and reconcile independently of terminal UI.

## Production perspective

Use an operations dashboard for orphaned authorizations, settlement mismatches and reversal deadlines. Store only safe references locally; provider/backend retains authoritative financial records and incident runbooks.

## Interview answer — short

“Issuer approval can precede terminal persistence. I write a stable intent before sending and reconcile after reboot; if local evidence is lost, backend/provider ledgers must find the orphan. I never infer decline or issue a new charge blindly.”

## Interview answer — structured

“A local database cannot commit atomically with an issuer. Before authorization I persist an operation ID and safe request metadata. After power loss I scan pending attempts and query the backend/acquirer using that ID. If approval occurred, I record it and follow the provider’s completion or reversal rule. If the local record itself is missing, server/provider reconciliation must detect the orphaned authorization. The UI remains unknown until authority resolves it.”

## Interview answer — deep senior

“I analyze two crash windows separately: after write-ahead intent but before response save, and before any durable local intent. The first is recoverable by same-ID lookup; the second requires a central operation ledger, terminal sequence/batch references and acquirer reconciliation. Neither a Room transaction nor WorkManager provides atomicity with the issuer. I test battery removal immediately after approval, late callbacks and delayed provider status. Unknown cases have SLA and human escalation, and reversals use the original references under the payment network’s actual rules rather than a guessed local status.”

## Deep-dive talking points

Prompt for pre-send intent, missing-local-record case, central ledger, delayed status and reversal SLA.

## Follow-up questions

- [PAY-04](../pay-04/): Why persist before send? **Answer:** to retain a lookup identity after power loss.
- [PAY-03](../pay-03/): What may resolve an orphan? **Answer:** reconciliation and protocol-specific reversal.

## Self-check rubric

Can I recover with and without a local intent and explain the unavoidable distributed gap?

## References and reviewed-on date

- [Android Room transactions](https://developer.android.com/reference/kotlin/androidx/room/package-summary) — local transaction boundary.
- [Stripe PaymentIntent lifecycle](https://docs.stripe.com/payments/paymentintents/lifecycle) — example provider status lifecycle.

Technically reviewed against the cited primary documentation on 2026-10-11; this is an automated editorial and technical review, not a human review.
