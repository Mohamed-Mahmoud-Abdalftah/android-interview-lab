---
id: "DAT-06"
question: "What is a Room Entity, DAO, transaction, migration, and Flow query?"
topic: "Networking, Room, DataStore & Offline-First"
code: "DAT"
group: "A"
phase: 3
priority: "P1"
order: 263
editorial_status: "reviewed"
---

# DAT-06

## Original interview question

What is a Room Entity, DAO, transaction, migration, and Flow query?

## What the interviewer evaluates

Explain Room schema/access components, all-or-nothing transaction, migration and invalidation Flow.

## Explanation in Arabic

`Entity` تمثل row/table، `DAO` يحدد SQL access، و`@Transaction` أو `withTransaction` تجمع updates كلها commit أو rollback. `Migration` تغيّر schema بين versions من غير مسح data. `Flow` query تعيد emission عند invalidation للجداول المعنية؛ مش promise إن كل intermediate row change هتوصل كevent مستقل. لازم نختبر migration من schemas القديمة.

## Why it matters and how it works

Room compiles DAO queries and maps entities. Transactions protect multi-table invariants. Observable Flow reruns query after invalidation and fits a local source of truth, but consumers may see coalesced snapshots. Schema export and migration tests protect user data across releases.

## Worked example

Conceptual Room DAO with AndroidX Room imports; `OrderEntity` and `ItemEntity` are app-owned entities.

```kotlin
import androidx.room.Dao
import androidx.room.Insert
import androidx.room.Query
import androidx.room.Transaction
import kotlinx.coroutines.flow.Flow

@Dao interface OrderDao {
    @Query("SELECT * FROM orders") fun observe(): Flow<List<OrderEntity>>
    @Insert suspend fun insertOrder(order: OrderEntity)
    @Insert suspend fun insertItems(items: List<ItemEntity>)
    @Transaction suspend fun save(order: OrderEntity, items: List<ItemEntity>) {
        insertOrder(order); insertItems(items)
    }
}
```

## Practical walkthrough

`@Entity` بتحدد جدول وprimary key، `@Dao` بتحدد SQL/insert/update، `@Transaction` بتربط عمليات محلية لازم تنجح أو تفشل مع بعض. لو حفظت order header وبعدين items في call منفصل، crash بين الاتنين يسيب order ناقصة؛ خليهم transaction واحدة. `Flow` query تراقب invalidation وتطلع snapshot جديد عند تغييرات tables ذات الصلة، لكنها مش server push ومش ضمان إن كل intermediate state هتتشاف. migration بين versions لازم تحافظ على صفوف المستخدم وتختبر exported schemas والقيود. لا تعمل network call جوه transaction عشان ما تمسكش DB lock مدة I/O.

## Trade-offs and decision criteria

Room improves SQL safety and observability but does not decide remote conflict policy or encryption. Auto migrations handle supported schema changes; complex transforms need manual migration. Transactional writes can still fail from disk full and need error handling.

## Failure modes

A destructive fallback migration can erase offline drafts. Writing order header and items in separate transactions can expose incomplete order. A Flow query cannot serve as an audit log of every mutation.

## Production perspective

An offline order repository stores header/items atomically, exposes DAO Flow to UI, and syncs server status by version. CI exports schemas and tests upgrade paths from shipped versions with real sample rows.

## Interview answer — short

“Entity maps table rows, DAO defines access, transaction groups writes atomically, migration evolves schema, and Flow query observes updated snapshots. I test migrations and do not treat query emissions as an event log.”

## Interview answer — structured

“Room sits above SQLite. I define entities for persisted rows and DAOs for verified queries. A transaction wraps related writes so callers see either the whole update or none. A migration moves stored user data to a new schema when app versions change; schema export and tests are essential. A DAO Flow reruns its query when relevant tables invalidate, giving UI current snapshots. That is useful for offline-first rendering, but it does not by itself resolve server conflicts or preserve every intermediate change.”

## Interview answer — deep senior

For a real order workflow, schema, consistency and observation are separate concerns. Entities and DAOs define local representation and access. I put header/item changes in one Room transaction, because a process crash between two independent writes would leave an invalid order. A migration preserves existing files across releases; I export schemas and run upgrade tests from every supported shipped version, including representative rows and constraints. A Flow query is an invalidation-driven snapshot stream, so UI can render the current state after a transaction, but it is not a transaction history. Server synchronization needs IDs, versions and conflict rules outside Room’s local atomicity. I also test disk-full and corrupted-file paths.

I would design the local invariant first: an order header, lines, and a pending-sync marker must appear together. An Entity defines stored rows, a DAO owns typed operations, and a Room transaction gives local all-or-nothing behavior for those operations. A Flow query lets UI observe database invalidation and reload, but it is not a live network feed and should be collected with lifecycle awareness. A migration is a shipped-data contract, not just a version increment. I export schemas and test upgrades from supported old versions with realistic rows and foreign keys. I keep remote calls outside the DB transaction and handle server consistency with a separate protocol.

## How to answer in the interview

- **Why:** Preserve local invariants across crashes and upgrades.
- **How:** Tie Entity, DAO, transaction, migration and Flow query to one order.
- **Trade-offs:** Keep transactions short; use Flow for observation, not sync itself.
- **Failure cases:** Half-written order, destructive migration, or network wait in transaction.
- **Production solution:** Export schemas and test representative upgrade paths.

## Deep-dive talking points

Trace local atomicity, observable snapshots, migration chain and remote conflict boundary.

## Follow-up questions

- [DAT-12](../dat-12/): How write two tables atomically? **Answer:** one Room transaction.
- [DAT-11](../dat-11/): How test upgrades? **Answer:** exported schemas and migration tests from shipped versions.

## Self-check rubric

Can I define each component, explain Flow invalidation and test a migration without data loss?

## References and reviewed-on date

- [Android Room guide](https://developer.android.com/training/data-storage/room) — entities, DAOs and database.
- [Android Room migrations](https://developer.android.com/training/data-storage/room/migrating-db-versions) — schema evolution tests.

Technically reviewed against linked primary documentation on 2026-10-13. Examples are conceptual unless explicitly stated otherwise; no Android device execution is claimed.
