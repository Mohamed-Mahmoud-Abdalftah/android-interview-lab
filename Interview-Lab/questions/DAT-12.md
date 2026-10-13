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

Use Room's @Transaction on DAO methods or database.withTransaction { } in repositories to guarantee ACID atomicity across multi-table writes. If an exception occurs, changes roll back completely, preventing partial database states. Never execute network calls inside database transactions to avoid blocking SQLite threads.

## Interview answer — structured

Room transactions provide ACID atomicity, guaranteeing that multi-step database writes either completely succeed or completely roll back:

1. **DAO-Level Transactions (`@Transaction`)**: Used when combining multiple queries within a single DAO (e.g. deleting old cached posts and inserting fresh posts). If the app crashes or throws an exception during insertion, the delete operation rolls back automatically, preventing an empty UI state.

2. **Repository-Level Transactions (`roomDatabase.withTransaction { }`)**: The preferred coroutine construct for multi-DAO atomic operations. For example, saving an order in `OrderDao`, recording line items in `OrderItemDao`, and clearing the shopping cart in `CartDao` must occur atomically. `withTransaction` wraps the block in SQLite `BEGIN TRANSACTION ... COMMIT`.

3. **Consistency for Observers**: Observers watching Room `Flow` queries only receive an updated dataset *after* the entire transaction commits. They never observe intermediate, half-written states.

## Interview answer — deep senior

A critical concurrency trap is **Executing Network Calls inside `withTransaction`**:

```kotlin
// ❌ ANTI-PATTERN:
database.withTransaction {
    orderDao.savePendingOrder(order)
    val response = networkApi.submit(order) // BLOCKS SQLITE CONNECTION POOL FOR 5 SECONDS!
    orderDao.markConfirmed(response.id)
}
```
SQLite has a limited connection pool (often 1 write connection in WAL mode). Holding an open database transaction while awaiting a remote HTTP call locks the database for seconds, starving all other read and write threads and causing widespread `SQLiteDatabaseLockedException` and UI ANRs.

**Rule**: Network operations must happen outside database transactions. First write the pending state in a fast 2ms transaction, make the network call, and update status in a second fast transaction.

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
