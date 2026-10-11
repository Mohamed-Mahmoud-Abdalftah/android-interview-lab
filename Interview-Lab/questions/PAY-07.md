---
id: "PAY-07"
question: "How do you design a reversal queue that survives a battery removal?"
topic: "Bonus: Payment/POS & Security Scenarios"
code: "PAY"
group: "B"
phase: 5
priority: "P2"
order: 477
editorial_status: "reviewed"
---

# PAY-07

## Original interview question

How do you design a reversal queue that survives a battery removal?

## What the interviewer evaluates

- Reversal queue durability through process death and battery removal.
- Stable identity, at-least-once delivery and reconciliation.

## Explanation in Arabic

Reversal obligation لازم تتكتب durably قبل ما UI تختفي أو battery تتشال. نخزن outbox row فيها original transaction reference، reversal ID ثابت، state وattempt metadata آمنة؛ WorkManager ينفذ لما الشبكة ترجع. لو الرد ضاع، ما نعملش reversal جديد بهوية مختلفة: نستعلم عن الحالة أو نعيد بنفس idempotency contract. ما نعتبرش enqueue وحده ضمان نهائي.

## Why it matters and how it works

WorkManager persists scheduling intent but the application’s own DB should own financial state and queue identity. Worker execution can repeat or be interrupted; delivery is at-least-once unless server/provider deduplication and lookup close uncertain outcomes. Retry policy must respect provider windows and terminal power constraints.

## Worked example

A POS app atomically inserts `ReversalIntent(originalId, reversalId, PENDING)` with the payment’s pending status. On reboot, a worker scans pending rows, checks connectivity, calls backend with the stable reversal ID, and marks confirmed only after authoritative status. No PAN/PIN is persisted.

## Trade-offs and decision criteria

Fast in-memory queues are simpler but disappear on battery removal. Durable queues cost storage and operational monitoring. WorkManager is suited to deferrable persistent work, while time-critical regulated payment flows may need a vendor-specific service/terminal process; both still need durable state.

## Failure modes

Worker sends reversal and crashes before DB update; next run repeats. Without provider deduplication, double side effects may occur. Reconcile first when outcome is unknown and enforce one reversal identity at the backend.

## Production perspective

Alert on queue age and repeated failures, run startup reconciliation and test forced power loss at every boundary. Escalate beyond retry window rather than silently discarding a financial obligation.

## Interview answer — short

“I persist reversal intent and identity in an outbox before leaving the flow. A durable worker retries after reboot, but the backend/provider must deduplicate and reconcile unknown results.”

## Interview answer — structured

“A battery removal destroys memory, so I write the reversal obligation and original transaction reference to a local database transaction. WorkManager or a terminal-specific persistent scheduler processes the outbox after restart and connectivity. It uses a stable reversal ID, checks authoritative status after ambiguous sends and marks completion only after confirmation. I monitor queue age and escalate entries that outlive protocol windows. I never claim the worker executes exactly once.”

## Interview answer — deep senior

“My guarantee is durable intent plus eventual *attempted* delivery while the device can run, with business-effect deduplication at the server/provider. The app writes the outbox atomically with payment state; on every start a scanner repairs scheduling gaps. Workers can execute concurrently, crash or be retried, so I claim rows with a lease and unique key, use bounded backoff, and query status after lost acknowledgments. If the device never reconnects or provider retention expires, software cannot guarantee completion; operations reconciliation and escalation handle that limit. Tests remove power before commit, after commit, after send and before acknowledgment.”

## Deep-dive talking points

Prompt for durable outbox, scheduling repair, repeat delivery, provider retention and offline limit.

## Follow-up questions

- [PAY-06](../pay-06/): Why atomic status plus intent? **Answer:** no crash gap can lose the reversal obligation.
- [PAY-15](../pay-15/): What if server stays unreachable? **Answer:** retain the row and escalate after defined limits.

## Self-check rubric

Can I describe battery-removal recovery and avoid promising network delivery while permanently offline?

## References and reviewed-on date

- [Android WorkManager overview](https://developer.android.com/topic/libraries/architecture/workmanager) — persistent scheduling.
- [Android Room transactions](https://developer.android.com/reference/kotlin/androidx/room/package-summary) — local outbox commit.

Technically reviewed against the cited primary documentation on 2026-10-11; this is an automated editorial and technical review, not a human review.
