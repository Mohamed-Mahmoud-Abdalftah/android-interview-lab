---
id: "MEM-25"
question: "How do you find a rare ANR associated with database lock contention?"
topic: "Memory Management, ANR & Performance"
code: "MEM"
group: "C"
phase: 1
priority: "P1"
order: 80
editorial_status: "reviewed"
---

# MEM-25

## Original interview question

How do you find a rare ANR associated with database lock contention?

## What the interviewer evaluates

- Inspect ANR clusters and all relevant thread stacks, not just the top Main frame.
- Identify the waiter, lock holder, long transaction, and why Main needs the resource.
- Reproduce under load and fix transaction scope or synchronous UI dependency with correctness intact.

## Concept and technical explanation

Diagnosing and resolving rare Application Not Responding (ANR) occurrences caused by database lock contention requires analyzing native thread dumps, SQLite transactional mechanics, and Android looper state. In a typical database contention scenario, a background coroutine initiates a long-running, multi-statement write transaction (such as bulk data synchronization or migration) on a SQLite database. If a user interaction on the UI thread subsequently triggers a read or write operation against the same database, the UI thread must acquire the database connection lock. In standard SQLite Rollback Journal mode, readers block writers and writers block readers. Even under Write-Ahead Logging (WAL) mode, if the connection pool is exhausted or a write lock is contended, the UI thread enters a BLOCKED or WAITING state inside native SQLiteConnectionPool or ReentrantLock routines. If the background transaction holds the lock for more than five seconds, the Activity Manager Service declares an ANR. Resolution requires inspecting /data/anr/traces.txt to identify the blocking thread ID, enabling WAL mode, breaking large transactions into batched chunks, and strictly banning all main-thread database access.

## Practical walkthrough (English)

Configuring Room for WAL mode and batched non-blocking write transactions:
```kotlin
// 1. Enable Write-Ahead Logging (WAL) in Room builder:
val database = Room.databaseBuilder(context, AppDatabase::class.java, "app.db")
    .setJournalMode(RoomDatabase.JournalMode.WRITE_AHEAD_LOGGING) // Allows concurrent readers during background write
    .build()

// 2. Chunker pattern for long-running background writes to avoid holding write locks:
class TransactionWriter(private val dao: OrderDao) {
    suspend fun insertLargeCatalog(items: List<CatalogItem>) = withContext(Dispatchers.IO) {
        // Chunk large write payload into smaller discrete transactions:
        items.chunked(100).forEach { batch ->
            dao.insertBatchTransaction(batch)
            // Yield execution briefly to allow waiting threads and checkpoints to process:
            yield()
        }
    }
}
```

## Explanation in Arabic

كيفية العثور على تشخيص الـ ANR النادر الناتج عن تزاحم الأقفال على قاعدة البيانات (Database Lock Contention):

1. ما هو تزاحم أقفال قاعدة البيانات (Database Lock Contention)؟
   - قواعد بيانات SQLite و Room تستخدم آليات حماية (Locking mechanisms) لضمان اتساق البيانات.
   - أثناء كتابة بيانات ضخمة (Transaction) في Background Thread، تقوم SQLite بحجز قفل حصري (Exclusive Lock) على ملف قاعدة البيانات.
   - إذا حاول الـ Main Thread تنفيذ استعلام قراءة (Query) أو حتى قراءة SharedPreferences متزامنة تشارك نفس الملف، يضطر الـ Main Thread للانتظار حتى ينتهي الـ Transaction بالكامل.
   - إذا استغرقت المعاملة أكثر من 5 ثوانٍ، يطلق النظام تحذير ANR فوراً!

2. كيفية العثور على هذا الـ ANR النادر وتشخيصه:
   - فحص ملف **`/data/anr/traces.txt`**:
     * النظر إلى حالة الـ `"main"` thread: ستجد حالته `BLOCKED` أو `WAITING` مع سطر يشير إلى انتظار قفل: `waiting to lock <0x...>`.
     * البحث عن الـ Thread الآخر الذي يحمل القفل (Held by thread X): ستجد background thread ينفذ `sqlite3_step` أو `room.RoomDatabase.beginTransaction`.
   - استخدام **Perfetto System Trace**: البحث عن شرائح SQLite والتحقق من Lock Contention.

3. الحلول الهندسية لمنع التزاحم:
   - **تفعيل WAL Mode (Write-Ahead Logging)**: في وضع WAL، القراءات والكتابات لا تحظر بعضها البعض! يستطيع قارئ القراءة في نفس اللحظة التي يكتب فيها كاتب.
   - **عدم تنفيذ أي استعلام لقاعدة البيانات على الـ Main Thread**: حظر استدعاء `.allowMainThreadQueries()` في Room نهائياً والاعتماد على Kotlin Flow و Coroutines.
   - تقليص حجم المعاملات (Batch transactions in smaller chunks) لتفادي احتجاز القفل لفترات طويلة.

## Practical walkthrough

تفعيل وضع WAL والتأكد من تنفيذ المعاملات بشكل آمن في Room:
```kotlin
// 1. تفعيل Write-Ahead Logging (WAL) في بناء الـ Room Database:
val db = Room.databaseBuilder(context, AppDatabase::class.java, "app_db")
    .setJournalMode(RoomDatabase.JournalMode.WRITE_AHEAD_LOGGING) // يسمح بالقراءة والكتابة المتزامنة!
    // ❌ تجنب allowMainThreadQueries() تماماً لمنع أي ANR محتمل:
    // .allowMainThreadQueries()
    .build()

// 2. تقسيم عمليات الإدخال الضخمة إلى دفعات صغيرة مع فترات راحة:
suspend fun batchInsertSafely(items: List<RecordEntity>) = withContext(Dispatchers.IO) {
    items.chunked(100).forEach { chunk ->
        db.recordDao().insertChunk(chunk)
        // إتاحة فرصة للمعاملات الأخرى للتنفيذ دون احتجاز قفل مستمر:
        yield()
    }
}
```

## Why it matters and how it works

Android reports ANR when a required app thread cannot respond in time; for input dispatch this is commonly Main, but the blocking cause may be elsewhere. Database transactions serialize some writes and can hold locks. A synchronous read on Main or a synchronous wait for a repository result makes UI hostage to another thread's transaction. Room discourages main-thread database access and supports suspend/Flow DAO patterns, but async alone does not remove a long transaction or deadlock.

## Worked example

A checkout repository opens a transaction, updates an order, then makes a network request before committing. During a slow connection, a screen waits synchronously for an order read and ANRs. The ANR stack shows Main waiting; a worker stack and trace show transaction ownership. Change the flow to persist a pending state in a short transaction, perform network work outside it with an idempotency key, and reconcile in another short transaction. This is a hypothetical root cause and proposed fix, not a reproduced device incident.

## Trade-offs and decision criteria

Short transactions improve availability but multi-step work must still preserve consistency through explicit states and idempotency. Moving the UI read off Main protects responsiveness but may leave a queue delay; show loading and investigate the lock holder. WAL or indexes may help some contention patterns but are not universal fixes. Avoid broad global mutexes that serialize unrelated operations.

## Failure modes

Looking only at `nativePollOnce` or the Main top frame misses the holder thread. Increasing an ANR threshold is not a solution. A database transaction waits on a network call and blocks all writers. A retry duplicates a payment after the first transaction outcome is unknown. Reproduce with concurrent load, latency injection, and crash recovery; assert state transitions and one external side effect.

## Production perspective

Segment ANR clusters by release, device, and operation. Add privacy-safe timing around transaction start/end, query latency, and lock waits. Capture a trace on a representative slow device with concurrent sync and UI access. Fix the longest critical section, then compare p95/p99 query time, ANR rate, and data correctness in staged rollout. Keep an operational rollback path if a migration changes transaction semantics.

## Interview answer — short

To find database lock contention ANRs, inspect /data/anr/traces.txt to identify the main thread BLOCKED on SQLiteConnectionPool or a database mutex, and locate the background holder thread. We fix it by enabling SQLite Write-Ahead Logging (WAL mode), eliminating any main-thread database access, chunking large write transactions into small batches, and using yield() between batches.

## Interview answer — structured

Database lock contention ANRs occur when the Android main thread blocks waiting for a database connection mutex held by a long-running background transaction.

The primary diagnostic artifact is the system ANR trace file located at /data/anr/traces.txt or exported via Google Play Console and Crashlytics. In this trace, we inspect the main thread stack. If the main thread state is BLOCKED or WAITING with frames indicating SQLiteConnectionPool.acquireConnection or ReentrantLock.lock, we extract the mutex lock identifier and search the file for the background worker thread holding that identical lock.

In production, the root cause is typically a background synchronization worker executing a large bulk write transaction encompassing thousands of records. In default SQLite rollback journal mode, a single write transaction places an exclusive lock on the database file, blocking all concurrent read queries.

We apply a three-tiered architectural fix. First, we enable SQLite Write-Ahead Logging (WAL mode), which allows concurrent readers while a write transaction proceeds. Second, we divide large background writes into smaller batched chunks, calling yield between batches to release the lock. Finally, we strictly enforce that the main thread never performs database operations directly, routing all queries through asynchronous Flow and suspend functions on Dispatchers.IO.


## Interview answer — deep senior

At the SQLite engine and Linux operating system level, database concurrency is governed by locking protocols on the database file descriptor. In legacy Rollback Journal mode, SQLite uses POSIX advisory file locks with states transitioning from SHARED to RESERVED, PENDING, and EXCLUSIVE. An EXCLUSIVE lock prevents all other threads and processes from reading or writing. If the main thread attempts to read while a background worker holds an EXCLUSIVE lock, the main thread hangs in native SQLite calls (such as sqlite3_step or sqlite3_prepare_v2), triggering a 5-second InputDispatching ANR.
Enabling Write-Ahead Logging (WAL mode) decouples readers from writers by appending mutations to an auxiliary `-wal` file while preserving original data in the main `.db` file. Under WAL, multiple readers can execute concurrently alongside a single active writer. However, lock contention can still cause ANRs even under WAL mode if: 1) the main thread attempts a write operation while a background write is underway; 2) the connection pool size (typically 1 writer and 4 readers in Android's SQLiteConnectionPool) is exhausted; or 3) an aggressive background writer triggers a synchronous WAL checkpoint pass that locks the entire database to transfer WAL frames back into the main database file.
Furthermore, thread scheduling introduces Priority Inversion risks. If a background worker running at Linux nice priority 10 (background cgroup) holds a database write lock, and the main thread (running at priority -10 in the top-app cgroup) blocks waiting for that lock, the background thread may be starved of CPU time on an overloaded device, prolonging the lock duration and guaranteeing an ANR.
Staff engineers eliminate these risks by configuring Room with WRITE_AHEAD_LOGGING, executing batch insertions in discrete chunks of 50 to 100 rows, inserting yield points to allow checkpoints to drain, and routing all database interactions through Dispatchers.IO with strict Architecture Component lint rules.

## How to answer in the interview

- **Why:** Follow Main's lock chain to the actual holder.
- **How:** Trace transaction span with concurrent read/write reproduction.
- **Trade-off:** Short transactions require explicit pending-state recovery.
- **Failure case:** Moving only the Main query may leave contention intact.
- **Production solution:** Keep network outside transactions and verify idempotent recovery.

## Deep-dive talking points

Discuss waiter versus holder, transaction timing, Room async boundary, network outside transaction, durable pending state, and tail latency.

## Follow-up questions

- **Interviewer:** "Why does WAL (Write-Ahead Logging) mode allow concurrent readers and writers?"
  **Answer:** "WAL writes modifications sequentially to an auxiliary `-wal` file without altering the primary database file immediately. Readers read consistent snapshots from the main DB and WAL index simultaneously without waiting for write transactions to finish."

- **Interviewer:** "What is `yield()` doing in batch insertion loops?"
  **Answer:** "`yield()` checks for coroutine cancellation and gives other dispatchable coroutines a chance to execute on the thread, preventing a tight loop from starving other cooperative background tasks."

## Self-check rubric

Find waiter and holder, reproduce with latency, shorten the transaction, preserve cross-system correctness, and compare ANR/tail metrics.

## References and reviewed-on date

- [Diagnose and fix ANRs](https://developer.android.com/topic/performance/anrs/diagnose-and-fix-anrs) — waiters, lock contention, and traces.
- [Room asynchronous queries](https://developer.android.com/training/data-storage/room/async-queries) — nonblocking DAO use.
- [RoomDatabase.Builder](https://developer.android.com/reference/androidx/room/RoomDatabase.Builder) — transaction executor behavior.

Technically reviewed against primary documentation on 2026-10-13.
