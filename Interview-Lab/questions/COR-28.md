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

When two coroutines update a shared var balance concurrently on multi-threaded dispatchers, non-atomic read-modify-write operations cause lost updates. Fix it using an AtomicInteger for simple numbers, a coroutine Mutex (withLock) for suspending critical sections, or single-threaded confinement via limitedParallelism(1).

## Interview answer — structured

To demonstrate the race condition:

```kotlin
var balance = 0
coroutineScope {
    launch(Dispatchers.Default) { repeat(10_000) { balance++ } }
    launch(Dispatchers.Default) { repeat(10_000) { balance++ } }
}
// balance will be far less than 20,000 due to race conditions!
```

The operation `balance++` breaks into three assembly instructions: read value, increment, and write back. When executed concurrently across worker threads on `Dispatchers.Default`, Thread B overwrites Thread A's updates.

To fix it, we have three production strategies depending on the use case:
1. **AtomicInteger** for primitive counters: `val balance = AtomicInteger(0); balance.addAndGet(amount)`. This is lock-free and resolved in CPU hardware.
2. **Kotlin Mutex** when suspension is involved: protect the mutation with `mutex.withLock { balance += amount }`. Mutex suspends non-blockingly without starving worker threads.
3. **Thread Confinement**: confine the balance update to a sequential dispatcher: `withContext(Dispatchers.Default.limitedParallelism(1)) { balance += amount }`.

## Interview answer — deep senior

From a performance and benchmarking perspective: 1. `AtomicInteger` executes millions of operations per second with zero garbage collection churn and zero context switching because it uses atomic Compare-And-Swap (CAS) CPU instructions. It is the fastest possible fix for simple counters. 2. `Mutex` adds object allocation overhead (`LockContender` queues) and continuation state-machine transitions. However, if updating the balance requires calling a suspending validation function (like checking an online fraud rule or reading Room DB), `Mutex` is mandatory because atomic variables cannot protect multi-step asynchronous transactions. 3. In Android UI architecture, the most idiomatic fix is immutable state management with `MutableStateFlow`:

```kotlin
private val _balance = MutableStateFlow(0)
val balance = _balance.asStateFlow()

fun deposit(amount: Int) {
    _balance.update { current -> current + amount }
}
```

`StateFlow.update` uses an internal CAS loop that guarantees atomic updates without locks.

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
