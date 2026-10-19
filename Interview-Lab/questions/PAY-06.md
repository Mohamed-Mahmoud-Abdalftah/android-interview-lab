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

Pair a conditional local payment-state transition with a uniquely identified reversal intent in one database transaction. Explain the limits: scheduling, provider delivery, power-loss durability, and whether reversal is appropriate all remain separate decisions.

## Concept and technical explanation

Once a provider contract determines that a particular attempt requires reversal, updating the local attempt and inserting its outbox intent in separate writes creates a crash gap. A Room `withTransaction` block can conditionally update the attempt and insert a unique intent in the same SQLite database; an error rolls back both local writes. The network request and WorkManager enqueue are outside this transaction. A recovery scan must find pending rows if scheduling is missed. Timeout alone means outcome unknown, not that reversal is always correct. SQLite atomicity for local rows does not make provider delivery exactly once or guarantee the latest commit survives every power loss; synchronous mode and storage matter.

## Practical walkthrough (English)

After provider-specific inquiry or rules establish that operation `op-42` needs reversal, conditionally move its local state from `UNKNOWN` to `REVERSAL_PENDING` and insert an outbox row with a unique original-operation ID in one Room transaction. If no row changed, inspect the current state rather than adding another intent. After commit, schedule a worker, while startup or periodic recovery scans pending rows if the app dies before enqueue. Worker delivery and authoritative acknowledgment happen separately.

## Explanation in Arabic

لو الـ provider contract قال إن محاولة محددة تحتاج Reversal، ما ينفعش تحدّث `attempt.state` في DB ثم تضيف `reversal_intent` بكتابة منفصلة؛ Crash بينهما يترك الحالة المحلية من غير التزام استرداد مسجل. داخل `RoomDatabase.withTransaction` حدّث الحالة المشروطة بـ original operation ID، وأدخل Outbox Row فريدة لنفس العملية. لو أي خطوة فشلت، الـ local transaction تتراجع. بعد الـ Commit، Worker تقرأ الـ Outbox وترسل الطلب وفق Contract الـ provider، وتتحقق من النتيجة authoritative قبل ما تعتبر الالتزام اكتمل.

لكن DB Transaction لا تشمل WorkManager queue ولا Network ولا Host Ledger. لو العملية توقفت بعد الـ Commit وقبل Enqueue، لازم Recovery Scan أو جدولة دورية تلتقط الـ pending row. ولو اتبعتت ثم مات التطبيق قبل حفظ الـ Ack، ممكن تتبعت تاني؛ استخدم Stable Identity وDeduplication حسب Contract. Timeout وحده حالة UNKNOWN، وممكن تحتاج Status Inquiry قبل أي Reversal. SQLite atomicity بين الصفين المحليين لا تعني ضمان بقاء آخر Commit عند كل Power Loss؛ ده يتأثر بـ sync mode والتخزين، ويستلزم Reconciliation.

## Practical walkthrough

افترض Status Inquiry أكدت إن محاولة `op-42` محتاجة Reversal وفق عقد المعالج. في DB Transaction واحدة: `UPDATE attempts ... WHERE id='op-42' AND state='UNKNOWN'`؛ لو `rowCount != 1` راجع الحالة بدل إنشاء Intent جديدة. بعد نجاحه، `INSERT reversal_intents(original_operation_id='op-42', status='PENDING')` مع UNIQUE Constraint. بعد Commit، Scheduler توقظ Worker، لكن Scanner عند بدء التطبيق تراجع الـ pending intents لو الجدولة ضاعت. Worker تستعمل identifiers المسموحة من العقد، وتسجل Ack أو نتيجة Status Inquiry بشكل منفصل بعد تأكيدها.

## Why it matters and how it works

The local transaction closes the two-row crash gap. It cannot atomically include WorkManager's database, the provider call, or the host ledger. An outbox record represents an obligation to perform a later action, not proof that the action succeeded.

## Worked example

This conceptual SQL uses a single local SQLite database. Production code checks affected-row count, rolls back when it is not one, and enforces a UNIQUE original-operation ID. The worker and provider call run after commit.

```sql
BEGIN TRANSACTION;
UPDATE attempts SET state = 'REVERSAL_PENDING'
 WHERE id = :operation_id AND state = 'UNKNOWN';
-- if affected rows != 1: ROLLBACK and inspect current state
INSERT INTO reversal_intents(original_operation_id, state)
 VALUES (:operation_id, 'PENDING');
-- original_operation_id has a UNIQUE constraint
COMMIT;
```

## Trade-offs and decision criteria

An outbox adds storage, recovery scheduling, and monitoring but keeps related local writes atomic. Holding a DB transaction open during a network or SDK call blocks local work without making the provider part of the transaction. Dispatch may be repeated; stable references and provider-approved recovery are needed. Store only permitted payment data.

## Failure modes

A timeout is marked failed and reversal is dispatched before provider-specific inquiry. Separate local writes leave a crash gap. The app dies after DB commit but before WorkManager enqueue: a scanner must rediscover the intent. It dies after provider send but before acknowledgment: duplicate delivery is possible. WAL with `synchronous=NORMAL` can lose a recent commit on hard power loss. Each needs a recovery or reconciliation path, not an assumed financial outcome.

## Production perspective

Persist permitted original-operation and correlation identifiers, a UNIQUE outbox key, status, attempts, and next-check time. Lease or claim work to control concurrent dispatch and use a provider-specific retry or status API. Monitor pending age and escalate past contract windows. Backend or processor records remain authoritative; device and provider integration tests are needed for end-to-end financial claims.

## Interview answer — short

Use one Room/SQLite transaction to conditionally update the attempt and insert a unique reversal-intent outbox row. Either both local writes commit or both roll back. A worker handles the outbox after commit, and a recovery scanner catches pending rows if scheduling was missed. This does not include WorkManager or the provider in the transaction. Timeout is unknown outcome; reversal must follow the provider contract or status inquiry.

## Interview answer — structured

Two separate local writes create a crash window: the attempt becomes `REVERSAL_PENDING`, but no outbox row exists if the process dies before the insert. Once the provider contract establishes reversal is required, I conditionally update the original attempt and insert an intent with a UNIQUE original-operation ID inside one Room `withTransaction`. If the prior state is wrong or the insert fails, roll back or inspect the existing state.

After commit, WorkManager may wake a worker, but its enqueue is not part of the Room transaction. A startup or periodic scanner must find pending rows if the app died before scheduling. If delivery happened but acknowledgment was not saved, the worker may retry; the stable reference and recovery rules must follow the provider contract.

I would not treat timeout as failed or universally trigger reversal. It is initially unknown and may require status inquiry. Local atomicity also does not prove host outcome or universal survival of a recent commit through power loss. Reconcile with the authoritative provider or backend record.

## Interview answer — deep senior

This is a device-level dual-write problem. Updating `attempt.state` and inserting `reversal_intent` in separate operations leaves a process-crash gap. Use a transaction in the same SQLite database: a conditional transition from `UNKNOWN` to the provider-appropriate pending state, then insert an outbox row with a UNIQUE original-operation ID. If the update affects no row, examine the current state; if insert fails, roll back. This keeps the two local records consistent but includes neither network nor WorkManager in its commit.

Deciding to create a reversal intent is a separate business and protocol step. Timeout leaves outcome unknown; the provider may require status inquiry or another recovery action. Once the action is selected, a worker reads pending outbox rows and delivers with contract-approved references and retry rules. If the process dies after DB commit and before enqueue, a recovery scan finds the row. If it dies after host send and before saving acknowledgment, duplicate delivery is possible. Do not claim exactly-once; deduplication and status checks depend on the provider.

Durability needs a precise caveat. SQLite preserves transaction atomicity for local rows, but survival of a recent commit across a hard power loss depends on WAL synchronous settings and storage behavior. WAL with `synchronous=NORMAL` may roll back a recent commit after power failure while remaining consistent. Financial recovery therefore needs reconciliation with a backend or processor ledger, not a statement that the local queue is permanently safe in all circumstances.

In production I would add a UNIQUE key, worker claim/lease, backoff, pending-age monitoring, and escalation around provider retention windows. Test crashes before commit, after commit, and after send before acknowledgment. A local SQLite test proves row-level rollback and commit only; provider sandbox or terminal integration is required for financial delivery claims.

## How to answer in the interview

- **Local boundary:** conditional status update plus unique outbox insert in one DB transaction.
- **After commit:** worker and recovery scan.
- **Unknown outcome:** inquiry or reversal depends on provider contract.
- **Limits:** duplicate dispatch, power-loss settings, and authoritative reconciliation.

## Deep-dive talking points

Room `withTransaction`, conditional update, UNIQUE original ID, outbox recovery, WorkManager outside transaction, at-least-once dispatch, provider-specific reversal, WAL synchronous settings, and reconciliation.

## Follow-up questions

- **Interviewer:** "What if the app dies after DB commit but before `WorkManager.enqueue`?"
  **Answer:** "The outbox row remains pending; startup or periodic scanning must find and schedule it. Enqueue is not atomic with Room."

- **Interviewer:** "Does the DB transaction prove the reversal happened at the host?"
  **Answer:** "No. It pairs local records only. Delivery and confirmation are separate and may require retry, status inquiry, and reconciliation under the provider contract."

## Self-check rubric

Place the DB transaction boundary, describe crashes before and after commit and send, distinguish UNKNOWN from reversal decision, and avoid power-loss or exactly-once guarantees.

## References and reviewed-on date

- [Room `withTransaction`](https://developer.android.com/reference/kotlin/androidx/room/package-summary) — local transaction scope.
- [SQLite synchronous PRAGMA](https://www.sqlite.org/pragma.html#pragma_synchronous) — power-loss durability settings.
- [Android WorkManager](https://developer.android.com/reference/androidx/work/WorkManager) — work scheduling.
- [Adyen transaction status](https://docs.adyen.com/point-of-sale/basic-tapi-integration/verify-transaction-status/) — one provider-specific recovery contract.

Technically reviewed against primary documentation on 2026-10-19.
