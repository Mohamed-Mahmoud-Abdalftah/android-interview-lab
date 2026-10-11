---
id: "PAY-06"
question: "How do you ensure atomic persistence of transaction status and reversal intent?"
topic: "Bonus: Payment/POS & Security Scenarios"
code: "PAY"
group: "B"
phase: 5
priority: "P2"
order: 476
editorial_status: "reviewed"
---

# PAY-06

## Original interview question

How do you ensure atomic persistence of transaction status and reversal intent?

## What the interviewer evaluates

- Atomic local transition pairing payment status with reversal intent.
- Limits of local atomicity across provider boundary.

## Explanation in Arabic

لو status اتكتب `unknown` لكن reversal intent ما اتكتبش بسبب crash، العملية ممكن تفضل approved عند issuer من غير متابعة. اكتب تغيير الحالة والـoutbox row في نفس Room/SQLite transaction، بحيث يا الاتنين موجودين يا الاتنين لا. بعدها worker يرسل reversal بالـoriginal operation ID ويتابع acknowledgment. ده atomic محلي فقط؛ provider يحتاج dedup/status reconciliation.

## Why it matters and how it works

Room `withTransaction` can commit related local rows atomically. A transactional outbox record describes the required future side effect. A worker processes outbox rows with retries; completion is marked only after authoritative confirmation. The external call must occur outside the DB transaction and tolerate repeated delivery.

## Worked example

When a payment timeout requires reversal, one transaction updates `attempt.state=REVERSAL_PENDING` and inserts `ReversalIntent(originalOperationId, status=PENDING)`. WorkManager later sends it. If the app dies after send but before marking sent, it may send again; server/provider deduplicates by stable identity.

## Trade-offs and decision criteria

Local transaction adds consistency but cannot force exactly-once network delivery. Keeping the DB transaction open during an SDK call is unsafe and can block other work. Outbox processing is at-least-once with explicit idempotency.

## Failure modes

Two separate writes leave a crash gap. Marking reversal done after HTTP 200 without checking provider semantics may be wrong. Test crash before commit, after commit, after send and before acknowledgment.

## Production perspective

Production has unique constraints on original operation ID, a worker lease/claim strategy, retry backoff, observability of queue age and escalation after retention windows. A backend ledger remains authoritative.

## Interview answer — short

“I commit transaction status and reversal intent in one local database transaction, then deliver the outbox item with a stable ID. Remote delivery may repeat, so server/provider idempotency and reconciliation remain required.”

## Interview answer — structured

“I use a transactional outbox. The local state change to reversal-pending and the new reversal row commit together in Room; no network call occurs inside that transaction. A worker later sends the reversal and marks it resolved only after authoritative acknowledgment. If the process dies after sending, it may retry, so the reversal carries the original operation identity under the provider’s deduplication contract. Local atomicity does not span the network.”

## Interview answer — deep senior

“I draw all crash windows. Before the DB commit there is no reversal obligation recorded; after commit there is one durable pending row; after remote send but before local acknowledgment the outcome is unknown. A stable reversal identity and status lookup make that last window safe. I put a uniqueness constraint on the original transaction reference, coordinate multiple workers and keep retry/backoff plus dead-letter escalation. I test battery removal around every boundary and verify the backend/provider actually supports deduplication for the relevant retention period. WorkManager later sends it. A backend ledger remains authoritative.”

## Deep-dive talking points

Prompt for Room transaction, outbox uniqueness, remote repeatability, crash matrix and provider contract.

## Follow-up questions

- [PAY-07](../pay-07/): What runs after reboot? **Answer:** a durable worker processes pending reversals.
- [PAY-15](../pay-15/): Can retries be exactly once? **Answer:** transport can repeat; enforce one business effect.

## Self-check rubric

Can I place the transaction boundary and describe the remaining distributed gap?

## References and reviewed-on date

- [Android Room transactions](https://developer.android.com/reference/kotlin/androidx/room/package-summary) — local atomicity.
- [Android WorkManager overview](https://developer.android.com/topic/libraries/architecture/workmanager) — persistent work.

Technically reviewed against the cited primary documentation on 2026-10-11; this is an automated editorial and technical review, not a human review.
