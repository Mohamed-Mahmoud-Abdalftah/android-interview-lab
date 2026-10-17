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

## Concept and technical explanation

Enforcing ACID atomicity across multi-step database writes in Room prevents partial data corruption and state inconsistencies:
- Atomicity Guarantee (All-or-Nothing): A database transaction ensures that a group of interdependent SQL write operations (inserts, updates, deletes) either all succeed completely and commit to disk, or if any single operation fails or throws a runtime exception, the entire operation is rolled back to the exact initial state.
- Implementation Paradigms in Room:
  1. The @Transaction DAO Annotation: When a DAO method is annotated with @Transaction, Room automatically wraps its execution body within a SQLite transaction block (beginTransaction / setTransactionSuccessful / endTransaction). It is commonly applied to methods that clear existing cache and insert fresh items, or queries fetching @Relation composite entities.
  2. Programmatic RoomDatabase.withTransaction: A Kotlin Coroutines extension function designed for repository or UseCase layers. It enables cross-DAO transactional boundaries, allowing writes across multiple distinct tables and DAOs to execute atomically within a single SQLite transaction on Dispatchers.IO.
- Concurrency & SQLite WAL Mode: Room operates in SQLite Write-Ahead Logging (WAL) mode by default. Transactions use beginTransactionNonExclusive(), allowing concurrent read operations from the UI thread or background workers to proceed unimpeded without being blocked by active write transactions.

## Practical walkthrough (English)

Atomic cache replacement using @Transaction and cross-DAO withTransaction:
```kotlin
// 1. DAO-level Transaction for atomic cache refresh
@Dao
interface OrderDao {
    @Query("DELETE FROM orders WHERE status = :status")
    suspend fun deleteOrdersByStatus(status: String)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertOrders(orders: List<OrderEntity>)

    // Atomic All-or-Nothing execution: if insert fails, delete is rolled back
    @Transaction
    suspend fun refreshOrders(status: String, newOrders: List<OrderEntity>) {
        deleteOrdersByStatus(status)
        insertOrders(newOrders)
    }
}

// 2. Repository-level cross-DAO atomic transaction
class CheckoutRepository(
    private val db: AppDatabase,
    private val orderDao: OrderDao,
    private val inventoryDao: InventoryDao
) {
    suspend fun completePurchase(order: OrderEntity, items: List<OrderItemEntity>): Result<Unit> = runCatching {
        // Enforces atomic boundary across distinct tables
        db.withTransaction {
            orderDao.insertOrder(order)
            items.forEach { item ->
                val updated = inventoryDao.decrementStock(item.productId, item.quantity)
                if (updated == 0) throw IllegalStateException("Insufficient inventory for product ${item.productId}")
            }
        }
    }
}
```

## Explanation in Arabic

كيف تستخدم معاملات Room (@Transaction / withTransaction) لتنفيذ عمليات كتابة ذرية كلية أو لا شيء (All-or-Nothing Writes)؟

1. ما هي المعاملة الذرية (Atomic Transaction)؟
   - هي ضمان خاصية الـ Atomicity من مبادئ ACID في قواعد البيانات.
   - إذا كانت العملية تتطلب كتابة في جدولين معاً (مثل جدول الطلب الرئيسي `Order` وجدول عناصر الطلب `OrderItem`)، أو حذف بيانات قديمة وكتابة بيانات جديدة:
   - تضمن المعاملة أن تُنفذ جميع الخطوات بنجاح ككتلة واحدة (`COMMIT`)، أو تُلغى جميع التعديلات ويعود كل شيء كما كان إذا حدث أي خطأ أو استثناء (`ROLLBACK`).

2. طريقتان للتنفيذ في Room:
   - **تعليمة `@Transaction` على دوال الـ DAO**: مثالية عندما تكون العمليات محصورة داخل DAO واحد (مثل استبدال عناصر السلة).
   - **دالة `roomDatabase.withTransaction { }` في الكوروتين**: المعيار الأفضل في طبقة الـ Repository لتنسيق عمليات ذرية تمتد عبر عدة DAOs مختلفة (مثل تحديث `OrderDao` وتحديث `InventoryDao` معاً).

3. حدود الضمان المعماري:
   - الـ Transaction تضمن الذرية محلياً فقط على مستوى SQLite على الهاتف؛ **لا تشمل ولا تضمن عمليات الشبكة (Network Calls)**! لا تضع استدعاءات API داخل `withTransaction` أبداً.

## Practical walkthrough

المقارنة بين @Transaction داخل DAO و withTransaction عبر عدة DAOs في الـ Repository:
```kotlin
// 1. @Transaction داخل DAO: لعملية ذرية محلية في جدول واحد:
@Dao
interface FeedDao {
    @Query("DELETE FROM feed_posts")
    suspend fun clearFeed()

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertPosts(posts: List<PostEntity>)

    @Transaction
    suspend fun clearAndInsert(posts: List<PostEntity>) {
        clearFeed()
        insertPosts(posts) // لو حدث OOM أو Crash، لا يتم مسح الكاش القديم!
    }
}

// 2. withTransaction في الـ Repository: لعملية ذرية تمتد عبر DAOs متعددة:
class CheckoutRepositoryImpl @Inject constructor(
    private val appDatabase: AppDatabase,
    private val orderDao: OrderDao,
    private val cartDao: CartDao,
    private val analyticsDao: LocalAnalyticsDao
) : CheckoutRepository {

    override suspend fun finalizeOrderLocally(order: OrderEntity, items: List<OrderItemEntity>) {
        // فتح معاملة ذرية على مستوى قاعدة البيانات بالكامل:
        appDatabase.withTransaction {
            orderDao.insertOrder(order)
            orderDao.insertOrderItems(items)
            cartDao.clearActiveCart()
            analyticsDao.recordEvent("order_created_locally", order.id)
            // لو فشل أي سطر هنا، يتم Rollback للجميع ولن تفقد السلة بدون حفظ الطلب!
        }
    }
}
```

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

Room transactions enforce atomic all-or-nothing guarantees, ensuring multiple writes commit completely or roll back entirely upon failure. They can be declared via the @Transaction annotation on DAO methods or programmatically across multiple DAOs using RoomDatabase.withTransaction, operating with SQLite WAL mode to prevent blocking concurrent reads.

## Interview answer — structured

Using Room transactions guarantees data consistency by enforcing atomic all-or-nothing writes across database tables.
First, atomicity ensures that when executing multi-step updates, such as clearing a cache table and inserting fresh records, any mid-operation failure cleanly reverts the database to its pre-transaction state, preventing partial data corruption.
Second, Room supports two implementation approaches: annotating DAO methods with @Transaction for single-DAO operations, or utilizing the RoomDatabase.withTransaction coroutine extension for coordinating multi-DAO transactions at the repository level.
Third, Room combines transactions with SQLite Write-Ahead Logging (WAL) mode. This architectural separation ensures that background write transactions execute without locking the database against concurrent read queries, keeping UI Flow rendering smooth and uninterrupted.

## Interview answer — deep senior

In complex mobile applications, maintaining database invariants across multi-table writes without transactions is impossible.
Consider an e-commerce checkout flow where an app must insert an order record, insert line items, and decrement local stock counters.
If the device process dies midway due to low memory or an uncaught exception, executing these statements independently leaves the local database in a corrupted state: the order exists, but stock was never decremented and line items are missing.
By wrapping the logic inside db.withTransaction, Room binds the coroutine context to an exclusive database transaction.
Under the hood, Room invokes beginTransactionNonExclusive().
If any statement throws an exception or the coroutine job is cancelled, SQLite executes a rollback, restoring all tables to their exact state prior to the transaction.
Furthermore, Room's default Write-Ahead Logging mode provides snapshot isolation: readers read from the main database file while writes append to the -wal journal file.
This means active write transactions never block the Main thread from querying Room via Flow, completely preventing UI jank.
However, senior engineers avoid wrapping heavy network calls or complex business computations inside withTransaction, as keeping a SQLite transaction open excessively long locks out other background write workers and risks database busy timeouts.
By keeping transaction blocks micro-scoped and atomic, we guarantee pristine data integrity while maintaining peak database throughput across concurrent background threads.

## How to answer in the interview

- **Why:** Prevent partial local orders and lost sync intent.
- **How:** Put header, lines and outbox row in one Room transaction.
- **Trade-offs:** Keep network outside the short local transaction.
- **Failure cases:** Crash between writes or server ack before local acknowledgement.
- **Production solution:** Rollback test plus idempotent outbox reconciliation.

## Deep-dive talking points

Draw local commit boundary and remote workflow; test crash between writes.

## Follow-up questions

- **Interviewer:** "Does Room's `@Transaction` work with `@Query` methods returning Relations?"
  **Answer:** "Yes! When querying `@Relation` objects (which executes multiple SELECT queries under the hood), `@Transaction` is mandatory to avoid race conditions between parent and child queries."

- **Interviewer:** "What is the threading model of `database.withTransaction`?"
  **Answer:** "It runs on an internal Room transaction dispatcher, acquiring a dedicated SQLite thread from Room's internal executor."

## Self-check rubric

Can I protect the full local invariant, avoid network inside transaction and define remote reconciliation?

## References and reviewed-on date

- [Android Room transactions](https://developer.android.com/training/data-storage/room/accessing-data#transaction) — transaction API.
- [Android offline-first guidance](https://developer.android.com/topic/architecture/data-layer/offline-first) — queued writes.

Technically reviewed against primary documentation on 2026-10-13.
