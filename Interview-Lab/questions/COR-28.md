---
id: "COR-28"
question: "Two coroutines update a shared balance. Demonstrate and fix a race condition."
topic: "Kotlin Coroutines & Concurrency"
code: "COR"
group: "C"
phase: 1
priority: "P1"
order: 109
editorial_status: "reviewed"
---

# COR-28

## Original interview question

Two coroutines update a shared balance. Demonstrate and fix a race condition.

## What the interviewer evaluates

Demonstrate lost update on balance and choose local plus authoritative transaction fixes.

## Concept and technical explanation

A race condition on a shared balance variable occurs when multiple concurrent coroutines interleave non-atomic read-modify-write operations across worker threads, leading to lost updates. If an initial balance of 100 is concurrently updated by coroutine A adding 50 and coroutine B adding 100 on Dispatchers.Default, both coroutines may read the baseline 100 into local CPU registers simultaneously. Coroutine A computes 150 and writes it to memory; microseconds later, coroutine B computes 200 and overwrites memory, completely obliterating coroutine A's 50-dollar increment. In Kotlin coroutines, fixing this requires choosing the appropriate synchronization abstraction. For local in-memory coordination across suspending boundaries, kotlinx.coroutines.sync.Mutex provides non-blocking mutual exclusion via withLock, ensuring only one coroutine updates the state while others suspend without consuming thread resources. For single numerical fields, AtomicLong provides lock-free hardware compare-and-swap guarantees. However, in enterprise financial production systems, monetary balances should never reside in volatile memory variables; they must be managed through ACID database transactions in Room using @Transaction and verified against backend double-entry ledgers.

## Practical walkthrough (English)

Consider two coroutines concurrently updating an in-memory balance:
```kotlin
// Erroneous implementation: suffers from lost updates
class UnsafeLedger {
    var balance = 100L

    suspend fun deposit(amount: Long) {
        val current = balance // Read
        delay(10) // Simulates asynchronous processing gap
        balance = current + amount // Non-atomic write!
    }
}
// Running deposit(50) and deposit(100) concurrently results in balance = 200 instead of 250!

// In-memory fix using Mutex:
class MutexLedger {
    private val mutex = Mutex()
    var balance = 100L
        private set

    suspend fun deposit(amount: Long) = mutex.withLock {
        val current = balance
        delay(10)
        balance = current + amount
    }
}

// Enterprise production fix using Room ACID Transactions:
@Dao
interface AccountDao {
    @Query("SELECT balance FROM accounts WHERE id = :accountId")
    suspend fun getBalance(accountId: String): Long

    @Query("UPDATE accounts SET balance = balance + :amount WHERE id = :accountId")
    suspend fun addAmount(accountId: String, amount: Long)

    @Transaction
    suspend fun depositAtomic(accountId: String, amount: Long) {
        addAmount(accountId, amount)
    }
}
```

## Explanation in Arabic

هذا السؤال عملي ويتطلب إظهار الـ Race Condition في الكود وإصلاحه بأكثر من طريقة صحيحة:

1. المشكلة بالكود (Demonstrating the Race Condition):
   - كود بيحدث رصيد حساب مشترك من 2 coroutines بالتوازي على `Dispatchers.Default`:
   ```kotlin
   var balance = 0
   coroutineScope {
       launch(Dispatchers.Default) { repeat(10_000) { balance++ } }
       launch(Dispatchers.Default) { repeat(10_000) { balance++ } }
   }
   println(balance) // النتيجة لن تكون 20,000 أبداً! ستكون مثلاً 13,450!
   ```
   - السبب: `balance++` ليست عملية ذرية (Not atomic). تتكون من قراءة القيمة من الذاكرة، زيادتها، ثم حفظها. التبديل بين الخيوط يسبب الكتابة فوق القيمة وضياع العمليات.

2. الحلول الصحيحة (The Fixes):
   - **الحل 1 (Atomic Types - الأسرع):** استخدام `AtomicInteger` و `incrementAndGet()`.
   - **الحل 2 (Coroutines Mutex - للعمليات المعقدة والـ Suspend):** استخدام `Mutex` مع `mutex.withLock { balance++ }`.
   - **الحل 3 (Thread Confinement):** حصر التنفيذ على `Dispatchers.Default.limitedParallelism(1)`.

## Practical walkthrough

كود توضيحي متكامل يُظهر الخطأ ثم يطبّق الحل الاحترافي بـ Mutex:
```kotlin
class BankAccount {
    private val mutex = Mutex()
    var balance: Int = 0
        private set

    suspend fun deposit(amount: Int) = mutex.withLock {
        // الدخول محمي بـ Mutex غير حاظر للخيوط:
        val current = balance
        delay(1) // محاكاة عملية تحقق معلقة
        balance = current + amount
    }
}

// في الاختبار أو التنفيذ:
val account = BankAccount()
coroutineScope {
    launch(Dispatchers.Default) { repeat(100) { account.deposit(10) } }
    launch(Dispatchers.Default) { repeat(100) { account.deposit(10) } }
}
assertEquals(2000, account.balance) // ينجح بنسبة 100% دائماً
```

## Why it matters and how it works

The vulnerable read-modify-write spans multiple operations. `Mutex.withLock` makes the in-memory section exclusive for coroutines sharing that Mutex. A server transaction enforces the invariant across clients and crash/retry boundaries; use operation IDs to avoid duplicated increments. Test with barriers to force the two reads before writes.

## Worked example

Kotlin/JVM local illustration; this only protects one `Ledger` instance, not cross-device money.

```kotlin
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

class LocalBalance(initial: Long) {
    private val mutex = Mutex()
    private var cents = initial
    suspend fun add(delta: Long): Long = mutex.withLock {
        cents += delta
        cents
    }
}
```

## Trade-offs and decision criteria

An atomic long works for a single local number, but checking limits plus posting history needs a larger transaction. Mutex is easy to reason about but process-local. For actual payments, append-only server ledger and idempotent transaction endpoint are authoritative.

## Failure modes

`@Volatile` makes reads/writes visible but does not make `balance += delta` atomic. Locking only the write still lets two callers read the same old value. A client lock is lost after process death and cannot coordinate another device.

## Production perspective

A wallet UI reads server ledger-derived balance. The backend transaction checks constraints and posts one idempotent operation. The Android repository may use a Mutex to coalesce local requests, but always reconciles with server state after uncertain network outcomes.

## Interview answer — short

A balance race condition occurs when concurrent coroutines interleave read-modify-write sequences on a multi-threaded dispatcher, overwriting updates. In memory, this is resolved using Mutex.withLock to suspend competing coroutines non-blockingly, or AtomicLong for lock-free CAS. In enterprise production, monetary balances must be persisted in SQLite using Room @Transaction to enforce ACID consistency and prevent state corruption.

## Interview answer — structured

Demonstrating a race condition on a shared balance highlights the fundamental concurrency hazard where compound read-modify-write operations interleave across threads. When two coroutines update a shared balance variable concurrently on Dispatchers.Default, both coroutines read the identical initial balance, compute their respective additions independently, and store their results back, causing one update to be completely lost.

Resolving this hazard requires isolating the critical section. For in-memory coordination where the update involves suspending operations, kotlinx.coroutines.sync.Mutex is the idiomatic solution. By wrapping the update inside mutex.withLock, the second coroutine suspends without blocking physical operating system threads until the first coroutine releases the lock.

In production, financial balances must never be treated as mutable memory fields. We persist balances in a local SQLite database using Room, executing updates inside an atomic database transaction annotated with @Transaction.

Local transactions must reconcile with backend authoritative accounting systems using double-entry bookkeeping, ensuring mathematical consistency across device reboots and network partitions.


## Interview answer — deep senior

At the bytecode and machine instruction level, balance = balance + amount decompiles into separate GETFIELD, LADD, and PUTFIELD opcodes. On modern multi-core processors, CPU caches maintain local copies of memory lines. Without synchronization, core 1 and core 2 execute the addition in parallel registers and flush their respective store buffers non-deterministically. Marking the balance variable with @Volatile guarantees cache coherence and visibility across cores, but does not provide mutual exclusion: the read-modify-write sequence remains non-atomic and will still suffer from lost increments under high contention. For purely in-memory coordination, engineers can adopt lock-free atomics: AtomicLong.addAndGet executes a hardware-level LOCK XADD or CAS loop, providing maximum throughput with zero thread suspension. However, when the balance modification involves multi-field invariants—such as checking if balance >= withdrawalAmount before deducting and logging an audit event—Atomics become unwieldy. Here, Mutex.withLock provides non-blocking mutual exclusion. Unlike Java's synchronized monitor, which blocks the OS kernel thread, Mutex suspends the calling coroutine and enqueues its continuation. When the active coroutine exits the withLock block, the next waiting continuation is resumed directly in user space. In staff-level architecture, we elevate this to the persistence layer: financial state must survive unexpected application process death by the Android Low Memory Killer. We model ledger mutations as immutable append-only transaction records in Room. Using Room's @Transaction decorator enforces SQLite BEGIN IMMEDIATE TRANSACTION semantics, guaranteeing atomic write-ahead logging (WAL), crash recovery, and isolation levels that prevent concurrent in-memory corruptions entirely.

## How to answer in the interview

- **Why:** read-modify-write is a compound operation.
- **How:** show the 100→110 lost update, then protect the whole local critical section with Mutex.
- **Trade-off:** an atomic counter is simpler for one number but cannot include validation and audit.
- **Failure case:** volatile or write-only locking leaves the race.
- **Production solution:** an idempotent server transaction is authoritative for money.

## Deep-dive talking points

Force the read-read-write-write schedule; compare local lock, atomic and server transaction scopes.

## Follow-up questions

- **Interviewer:** "Why wouldn't you use Java's `synchronized` block to fix this?"
  **Answer:** "Because `synchronized` blocks the underlying operating system thread. If a suspending function is called inside the synchronized block, it will fail to compile. Even for non-suspending code, blocking pool threads degrades coroutine scheduler performance and risks UI thread ANRs."

- **Interviewer:** "Can you fix this with a thread-safe collection instead?"
  **Answer:** "If the shared state is a collection (like a transaction list), using `ConcurrentLinkedQueue` or `CopyOnWriteArrayList` (for read-heavy scenarios) prevents `ConcurrentModificationException` during concurrent writes."

- **Interviewer:** "What is the downside of using `limitedParallelism(1)` for high-throughput operations?"
  **Answer:** "Every access requires a context switch and dispatch through an event queue. Under high frequency, queue management latency will be slower than lock-free atomic CAS instructions."

## Self-check rubric

Can I show the lost update, protect the whole critical section, and state why the backend remains authoritative?

## References and reviewed-on date

- [Kotlin shared mutable state](https://kotlinlang.org/docs/shared-mutable-state-and-concurrency.html) — lost increments and Mutex.
- [Android offline-first guidance](https://developer.android.com/topic/architecture/data-layer/offline-first) — local/remote source-of-truth design.

Technically reviewed against primary documentation on 2026-10-13.
