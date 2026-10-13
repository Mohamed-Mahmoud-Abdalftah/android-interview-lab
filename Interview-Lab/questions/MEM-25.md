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

To diagnose database lock contention ANRs, I inspect `/data/anr/traces.txt` to find the UI thread `BLOCKED` waiting on a database mutex held by a background writer thread. We fix this by enabling SQLite Write-Ahead Logging (WAL mode), eliminating any main-thread database access, and chunking large write transactions.

## Interview answer — structured

A rare ANR stemming from database lock contention occurs when the main thread attempts to execute a database query while a background worker holds an exclusive lock on the SQLite file during a large write transaction.

1. **Isolation in ANR Traces**: I examine `/data/anr/traces.txt`. In lock contention scenarios, the `"main"` thread is not in `RUNNABLE` (which would imply heavy computation), but in **`BLOCKED`** or `WAITING` waiting to acquire a monitor lock (e.g. `android.database.sqlite.SQLiteConnectionPool`). The trace explicitly notes `waiting to lock <0x...> held by thread [pool-X-thread-Y]`. Following that thread ID reveals a background worker deep inside `sqlite3_step` executing a long-running batch insert or migration.

2. **System Tracing via Perfetto**: Opening a Perfetto trace shows the main thread stalled in `SQLiteConnectionPool.waitForConnection` while disk I/O slices saturate the I/O queue.

3. **Resolution**:
   - Enable **Write-Ahead Logging (WAL)** via `RoomDatabase.JournalMode.WRITE_AHEAD_LOGGING`. Under WAL mode, readers do not block writers, and writers do not block readers.
   - Strictly audit code to eliminate `.allowMainThreadQueries()`, forcing all queries to return `Flow` or suspend.
   - Chunk massive multi-record imports into smaller transactions.

## Interview answer — deep senior

Under traditional SQLite Rollback Journal mode, any write transaction locks the entire database file exclusively; no read connections can proceed until the transaction commits and writes to disk. Under WAL mode, SQLite appends changes to a separate `-wal` file, allowing readers to read from the unmodified main database while writing occurs concurrently.

However, even with WAL mode, lock contention can still occur if multiple writers compete for the single write connection, or if SQLite triggers an automatic **WAL Checkpoint** on a thread executing a read. To prevent checkpoint stalls, high-volume apps configure custom connection pools or schedule explicit background checkpoints during device idle windows.

In Room, we also configure a dedicated query executor (`setQueryExecutor`) distinct from general background dispatchers to guarantee that disk-heavy queries never starve high-priority background UI tasks.

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
