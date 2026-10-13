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

## Practical walkthrough

عند timeout يستوجب reversal، `attempt.state=REVERSAL_PENDING` وoutbox row لازم ينجحوا أو يفشلوا مع بعض. استخدم transaction محلية ثم شغّل worker بعد commit؛ متستناش الشبكة جوّه transaction. لو حصل crash بعد send وقبل acknowledgment، worker ممكن يعيد؛ لذلك reversal ID ثابت وlookup قبل اعتبار العملية مكتملة.

## Why it matters and how it works

Room `withTransaction` can commit related local rows atomically. A transactional outbox record describes the required future side effect. A worker processes outbox rows with retries; completion is marked only after authoritative confirmation. The external call must occur outside the DB transaction and tolerate repeated delivery.

## Worked example

When a payment timeout requires reversal, one transaction updates `attempt.state=REVERSAL_PENDING` and inserts `ReversalIntent(originalOperationId, status=PENDING)`. WorkManager later sends it. If the app dies after send but before marking sent, it may send again; server/provider deduplicates by stable identity.

### Kotlin/Android sketch

```kotlin
// App DAO contract; @Transaction wraps both local SQL writes.
@Dao
interface PaymentDao {
    @Query("UPDATE attempts SET state = 'REVERSAL_PENDING' " +
           "WHERE id = :id AND state = 'UNKNOWN'")
    suspend fun markPending(id: String): Int
    @Insert(onConflict = OnConflictStrategy.ABORT)
    suspend fun insertIntent(intent: ReversalIntent)
    @Transaction
    suspend fun queueReversal(id: String, intent: ReversalIntent): Boolean {
        if (markPending(id) != 1) return false
        insertIntent(intent)
        return true
    }
}
// Imports: androidx.room.Dao/Query/Insert/Transaction/OnConflictStrategy.
// ReversalIntent has a unique original ID; a conflicting insert rolls back.
// The real DAO validates original references and provider-specific rules.
```

## Trade-offs and decision criteria

Local transaction adds consistency but cannot force exactly-once network delivery. Keeping the DB transaction open during an SDK call is unsafe and can block other work. Outbox processing is at-least-once with explicit idempotency.

## Failure modes

Two separate writes leave a crash gap. Marking reversal done after HTTP 200 without checking provider semantics may be wrong. Test crash before commit, after commit, after send and before acknowledgment.

## Production perspective

Production has unique constraints on original operation ID, a worker lease/claim strategy, retry backoff, observability of queue age and escalation after retention windows. A backend ledger remains authoritative.

## Interview answer — short

“I atomically persist the pending status and reversal outbox row, then let a worker send outside the database transaction. A repeated send is expected, so the backend/provider must handle the stable reversal identity safely.”

## Interview answer — structured

“I use a transactional outbox. The local state change to reversal-pending and the new reversal row commit together in Room; no network call occurs inside that transaction. A worker later sends the reversal and marks it resolved only after authoritative acknowledgment. If the process dies after sending, it may retry, so the reversal carries the original operation identity under the provider’s deduplication contract. Local atomicity does not span the network. The transaction covers only local rows; sending to the provider occurs afterward.”

## Interview answer — deep senior

“I draw all crash windows. Before the DB commit there is no reversal obligation recorded; after commit there is one durable pending row; after remote send but before local acknowledgment the outcome is unknown. A stable reversal identity and status lookup make that last window safe. I put a uniqueness constraint on the original transaction reference, coordinate multiple workers and keep retry/backoff plus dead-letter escalation. I test battery removal around every boundary and verify the backend/provider actually supports deduplication for the relevant retention period. WorkManager later sends it. A backend ledger remains authoritative. I would crash immediately after the remote send to prove a repeated worker attempt remains duplicate-safe. My local transaction updates the attempt only if it is in a state that legitimately requires reversal, and inserts one outbox row keyed by the original attempt and stable reversal ID. The transaction ends before any network call. If the app crashes before commit, neither row appears; after commit, both appear and a startup scanner can schedule delivery. If it crashes after the provider accepted the reversal but before local acknowledgment, a worker can send again, so the remote side must deduplicate or permit status lookup under its protocol. I would test database rollback, concurrent workers, a lost response, and a reversal that remains unknown beyond the allowed window.”

## How to answer in the interview

- **Why:** a status without its obligation can strand an approved transaction.
- **How:** change attempt and insert reversal intent in one database transaction.
- **Trade-off:** remote delivery remains at least once.
- **Failure case:** crash between two local writes or after send before ack.
- **Production solution:** durable outbox, deduplication, and authoritative confirmation.

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
