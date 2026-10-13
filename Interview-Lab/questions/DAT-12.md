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

## Practical walkthrough

لو checkout local save محتاج header، line items، وoutbox marker، الثلاثة لازم يدخلوا transaction واحدة؛ من غيرها crash ممكن يسيب order ناقصة أو intent sync مفقودة. `@Transaction` على DAO function أو `database.withTransaction` يدي SQLite atomicity داخل DB واحدة، مش network+DB distributed transaction. خليك قصير جوه transaction: insert/update فقط، وخلّي API call بعد commit. لو server call نجحت والack المحلي ضاع، marker لسه pending؛ worker يصالحها بـidempotency key/status query. اختبر exception في نص inserts وتأكد no partial rows، واختبر Flow ما تعرضش حالة half-write للـUI.

## Trade-offs and decision criteria

One transaction protects consistency but can increase contention if too broad. For a complex repository operation, `RoomDatabase.withTransaction` may coordinate multiple DAOs. Neither approach offers distributed transaction with a payment server.

## Failure modes

Separate inserts can leave orphaned order rows after crash. A transaction that calls a slow HTTP API holds database resources and still cannot undo server commit if local rollback occurs. Retrying blindly can duplicate remote operations.

## Production perspective

An order repository first persists a Pending operation and lines in one Room transaction, then a worker submits it with stable ID. Server status reconciles outcome; UI observes one local state transition after each commit.

## Interview answer — short

“Room transactions make related local writes all-or-nothing. I wrap the full database invariant, keep network calls outside, and use operation IDs and reconciliation for remote effects that SQLite cannot roll back.”

## Interview answer — structured

“If an order header and line items must always agree, I put both DAO writes inside one transaction. A failure rolls back the local set, and observers see a consistent committed snapshot. I keep transactions short to avoid contention. The transaction cannot include a remote payment as one atomic unit, so I persist a pending operation and use an idempotent server contract with a worker/reconciliation flow.”

## Interview answer — deep senior

I define the invariant before choosing the transaction boundary. For local order creation, header, lines and pending sync marker should commit together; otherwise a crash can expose a half-written order or lose the intent to sync. Room’s transaction mechanisms give local SQLite atomicity and observable queries update after commit, but a remote API is outside that ACID boundary. Holding a database transaction while awaiting network is harmful and still cannot roll back the server. I split the workflow into local atomic acceptance, remote idempotent execution and authoritative status reconciliation. Tests inject failure after the first insert, process restart before enqueue and duplicate worker execution. Test forced failure between writes. Retrying blindly can duplicate remote operations.

I define the invariant before the annotation: an order header, its lines, and a pending-sync row must either all exist or none do. Room can commit those local writes atomically through a DAO transaction or database transaction API. The network request is not inside that SQLite atomic boundary; holding a transaction during I/O would increase contention and still would not make the remote server roll back with it. I commit local intent first, then send through a worker with a stable operation ID. A crash after server success but before local acknowledgement is handled by reconciliation. I inject a failure between inserts to prove rollback and observe the UI only after committed state.

## How to answer in the interview

- **Why:** Prevent partial local orders and lost sync intent.
- **How:** Put header, lines and outbox row in one Room transaction.
- **Trade-offs:** Keep network outside the short local transaction.
- **Failure cases:** Crash between writes or server ack before local acknowledgement.
- **Production solution:** Rollback test plus idempotent outbox reconciliation.

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

Technically reviewed against linked primary documentation on 2026-10-13. Examples are conceptual unless explicitly stated otherwise; no Android device execution is claimed.
