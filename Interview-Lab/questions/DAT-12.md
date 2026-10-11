---
id: "DAT-12"
question: "How do you use Room transactions for all-or-nothing writes?"
topic: "Networking, Room, DataStore & Offline-First"
code: "DAT"
group: "B"
phase: 3
priority: "P1"
order: 269
editorial_status: "reviewed"
---

# DAT-12

## Original interview question

How do you use Room transactions for all-or-nothing writes?

## What the interviewer evaluates

Use Room transaction for atomic multi-table writes and explain scope of guarantee.

## Explanation in Arabic

لو بنكتب order header وline items، لازم الاتنين يدخلوا مع بعض أو ولا واحد. Room `@Transaction` أو `withTransaction` تعمل local SQLite transaction: exception تلغي تغييراتها، وcollector يشوف snapshot متسقة بعد commit. لكنها لا تضم network call في نفس atomicity؛ backend write تحتاج idempotency/saga أو reconciliation منفصل.

## Why it matters and how it works

Transaction boundaries should be short and include the full local invariant. Room suspending DAO methods can participate in a transaction. Avoid slow network I/O inside a database transaction, which holds locks and cannot atomically roll back remote side effects. Test forced failure between writes.

## Worked example

Conceptual Room DAO; OrderEntity and LineEntity are application entities.

```kotlin
import androidx.room.Dao
import androidx.room.Insert
import androidx.room.Transaction

@Dao interface CheckoutDao {
    @Insert suspend fun insertOrder(order: OrderEntity)
    @Insert suspend fun insertLines(lines: List<LineEntity>)
    @Transaction suspend fun save(order: OrderEntity, lines: List<LineEntity>) {
        insertOrder(order)
        insertLines(lines)
    }
}
```

## Trade-offs and decision criteria

One transaction protects consistency but can increase contention if too broad. For a complex repository operation, `RoomDatabase.withTransaction` may coordinate multiple DAOs. Neither approach offers distributed transaction with a payment server.

## Failure modes

Separate inserts can leave orphaned order rows after crash. A transaction that calls a slow HTTP API holds database resources and still cannot undo server commit if local rollback occurs. Retrying blindly can duplicate remote operations.

## Production perspective

An order repository first persists a Pending operation and lines in one Room transaction, then a worker submits it with stable ID. Server status reconciles outcome; UI observes one local state transition after each commit.

## Interview answer — short

“Room transactions make related local writes all-or-nothing. I wrap the full database invariant, keep network calls outside, and use operation IDs and reconciliation for remote effects that SQLite cannot roll back.”

## Interview answer — structured

“If an order header and line items must always agree, I put both DAO writes inside one transaction. A failure rolls back the local set, and observers see a consistent committed snapshot. I keep transactions short to avoid contention. The transaction cannot include a remote payment as one atomic unit, so I persist a pending operation and use an idempotent server contract with a worker/reconciliation flow. One transaction protects consistency but can increase contention if too broad. For a complex repository operation, `RoomDatabase.withTransaction` may coordinate multiple DAOs. Neither approach offers distributed transaction with a payment server. An order repository first persists a Pending operation and lines in one Room transaction, then a worker submits it with stable ID. Server status reconciles outcome; UI observes one local state transition after each commit.”

## Interview answer — deep senior

“I define the invariant before choosing the transaction boundary. For local order creation, header, lines and pending sync marker should commit together; otherwise a crash can expose a half-written order or lose the intent to sync. Room’s transaction mechanisms give local SQLite atomicity and observable queries update after commit, but a remote API is outside that ACID boundary. Holding a database transaction while awaiting network is harmful and still cannot roll back the server. I split the workflow into local atomic acceptance, remote idempotent execution and authoritative status reconciliation. Tests inject failure after the first insert, process restart before enqueue and duplicate worker execution. Transaction boundaries should be short and include the full local invariant. Room suspending DAO methods can participate in a transaction. Avoid slow network I/O inside a database transaction, which holds locks and cannot atomically roll back remote side effects. Test forced failure between writes. Separate inserts can leave orphaned order rows after crash. A transaction that calls a slow HTTP API holds database resources and still cannot undo server commit if local rollback occurs. Retrying blindly can duplicate remote operations. An order repository first persists a Pending operation and lines in one Room transaction, then a worker submits it with stable ID.”

## Deep-dive talking points

Draw local commit boundary and remote workflow; test crash between writes.

## Follow-up questions

- [DAT-06](../dat-06/): What does @Transaction protect? **Answer:** related local database operations in one atomic unit.
- [DAT-20](../dat-20/): How recover remote uncertainty? **Answer:** stable operation ID and server status query.

## Self-check rubric

Can I protect the full local invariant, avoid network inside transaction and define remote reconciliation?

## References and reviewed-on date

- [Android Room transactions](https://developer.android.com/training/data-storage/room/accessing-data#transaction) — transaction API.
- [Android offline-first guidance](https://developer.android.com/topic/architecture/data-layer/offline-first) — queued writes.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
