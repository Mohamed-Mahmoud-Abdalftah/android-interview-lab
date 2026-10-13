---
id: "PAY-15"
question: "The server is unreachable when a reversal is due. How do you guarantee eventual delivery without duplicates?"
topic: "Bonus: Payment/POS & Security Scenarios"
code: "PAY"
group: "C"
phase: 5
priority: "P2"
order: 485
editorial_status: "reviewed"
---

# PAY-15

## Original interview question

The server is unreachable when a reversal is due. How do you guarantee eventual delivery without duplicates?

## What the interviewer evaluates

- Eventual-delivery conditions and the impossibility of guaranteeing reconnect.
- Durable queue, duplicate-safe retries, status lookup and escalation.

## Explanation in Arabic

لو server unreachable وقت reversal، ما نرميش الطلب ولا نعمل reversal جديدة كل retry. نخزن intent وهوية ثابتة في outbox، نعيد بمواعيد/backoff لما الاتصال يرجع، ونستعلم عن status لو الرد ضاع. لكن لو الجهاز ما رجعش online أو provider retention انتهت، ما ينفعش نعد “guaranteed delivery” مطلق؛ لازم backend reconciliation وoperations escalation.

## Practical walkthrough

لو terminal offline أسبوع، WorkManager مش هتقدر تبعت حاجة؛ لذلك قُل ضمان مشروط: row محفوظة، جهاز يرجع online، والـprovider لسه يقبل operation. كرر بنفس reversal ID مع backoff، ولو response ضاعت اسأل status. بعد deadline أو جهاز مفقود، backend reconciliation وoperations escalation لازم يغطوا الفجوة.

## Why it matters and how it works

A durable outbox preserves obligation through process death. WorkManager can retry under constraints but does not ensure execution while a device is off or disconnected. At-least-once send attempts plus provider/server idempotency and authoritative lookup aim for one business effect; retention windows and protocol rules must be explicit.

## Worked example

On `IOException`, leave `ReversalIntent(id=R1, original=P1, PENDING)` in Room and schedule constrained work with backoff. On restart, scan pending rows. If a send times out, query backend/provider for R1 before retrying; if still unknown, retry same identity under contract. Escalate aging entries.

### Kotlin/Android sketch

```kotlin
// Inside an injected CoroutineWorker: one durable row, same ID on retries.
override suspend fun doWork(): Result {
    val pending = dao.pendingReversals()
    for (intent in pending) {
        when (gateway.lookupOrSend(intent.reversalId, intent.originalId)) {
            ReversalStatus.Confirmed -> dao.markConfirmed(intent.reversalId)
            ReversalStatus.Unknown -> return Result.retry()
            ReversalStatus.Expired -> dao.markEscalated(intent.reversalId)
        }
    }
    return Result.success()
}
// App-defined gateway/status; server enforces deduplication and deadlines.
```

## Trade-offs and decision criteria

Aggressive retries reduce latency but may overload provider or exceed windows. Conservative backoff saves resources but delays reversal. Choose based on acquirer deadlines, network quality and operational SLA.

## Failure modes

Generating a fresh reversal ID after each timeout can create duplicate effects. Marking done when the request merely left the terminal loses unknown outcomes. Never delete a pending row solely because retry budget expired; move it to an escalated state.

## Production perspective

Backend reconciliation runs independently from terminal connectivity where possible. Dashboards page on queue age and mismatched ledgers. Test server outage, response loss, power removal, duplicate workers and expiry of provider deduplication window.

## Interview answer — short

“I can promise durable intent and duplicate-safe attempts under stated assumptions, not unconditional delivery from a permanently offline terminal. I keep the row, retry the same identity, reconcile uncertain results, and escalate ageing reversals.”

## Interview answer — structured

“When the server is unreachable, the reversal stays in a durable outbox with its original transaction reference and stable reversal ID. A worker retries with backoff when connected and queries status after ambiguous responses. The backend/provider must enforce duplicate-safe semantics for that identity. I monitor age and protocol deadlines, escalate unresolved cases, and never silently drop the row. WorkManager cannot deliver while a terminal is permanently off, so the guarantee has explicit assumptions. The outbox is durable, but a permanently offline terminal still cannot deliver.”

## Interview answer — deep senior

“I define liveness and safety separately. Safety means duplicate sends cannot produce duplicate business effects: stable identity, immutable parameters, server uniqueness and provider-specific reconciliation. Liveness means the obligation is eventually attempted while storage survives and the device resumes with connectivity; neither Android nor a worker can guarantee delivery from a destroyed/offline terminal. The backend should have its own ledger and reconciliation job, with provider status and reversal deadlines. I test crash after send before acknowledgment, parallel workers, server outage longer than idempotency retention and delayed callbacks. Unresolved rows transition to an escalated operational state, never to silent success. On restart, scan pending rows. Escalate aging entries.  I would test a lost acknowledgment and a retry after the provider’s key-retention window, then define escalation. I separate safety from liveness. Safety means repeated delivery attempts under the same reversal identity do not create multiple financial effects; the backend or provider must enforce that under its documented retention and parameter rules. Liveness depends on the row surviving, the terminal or backend running again, connectivity returning, and the reversal still being valid within its protocol window. WorkManager cannot satisfy those assumptions on a device that never powers on. The backend should keep an independent ledger and reconcile with provider status where possible. I alert on ageing rows, escalate expired or ambiguous cases to operations, and never turn a retry budget exhaustion into a silent success or deletion.”

## How to answer in the interview

- **Why:** delivery requires connectivity and a live execution path.
- **How:** durable outbox, stable ID, status lookup, and retry after reconnection.
- **Trade-off:** fast retries versus provider limits and battery.
- **Failure case:** new IDs after each timeout or deleting an aged row.
- **Production solution:** independent backend reconciliation, retention-aware alerts, and human escalation.

## Deep-dive talking points

Prompt for safety versus liveness, same reversal ID, retention window, independent backend reconciliation and permanent-offline limit.

## Follow-up questions

- [PAY-07](../pay-07/): What survives battery removal? **Answer:** local outbox row if it was durably committed.
- [PAY-02](../pay-02/): Does idempotency mean exactly-once HTTP? **Answer:** no; it protects intended business effect under the contract.

## Self-check rubric

Can I state the conditional guarantee and explain duplicate-safe retries plus escalation?

## References and reviewed-on date

- [Android WorkManager overview](https://developer.android.com/topic/libraries/architecture/workmanager) — persistent scheduling constraints.
- [Stripe idempotent requests](https://docs.stripe.com/api/idempotent_requests) — provider-specific retry semantics.

Technically reviewed against the cited primary documentation on 2026-10-11; this is an automated editorial and technical review, not a human review.
