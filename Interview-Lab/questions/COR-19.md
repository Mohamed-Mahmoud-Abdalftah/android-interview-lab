---
id: "COR-19"
question: "What is a race condition? Why are coroutines not automatically thread-safe?"
topic: "Kotlin Coroutines & Concurrency"
code: "COR"
group: "B"
phase: 1
priority: "P1"
order: 100
editorial_status: "reviewed"
---

# COR-19

## Original interview question

What is a race condition? Why are coroutines not automatically thread-safe?

## What the interviewer evaluates

Explain a read-modify-write race and why coroutine syntax does not serialize shared mutation.

## Concept and technical explanation

A race condition is a critical concurrency hazard that arises when multiple asynchronous execution pathways concurrently access and mutate shared mutable state without proper synchronization, making the final program outcome dependent on arbitrary thread scheduling and execution timing. A persistent and dangerous misconception among Android developers is assuming that Kotlin coroutines are automatically thread-safe simply because they utilize suspending functions and structured concurrency. In reality, structured concurrency manages task lifecycles, cancellation cascades, and parent-child hierarchies, but provides zero mutual exclusion or memory synchronization. Coroutine dispatchers like Dispatchers.Default and Dispatchers.IO are backed by multi-threaded thread pools (such as Java ForkJoinPool or Elastic ExecutorService pools). When multiple coroutines execute mutations concurrently across these worker threads, non-atomic compound operations—such as read-modify-write patterns like count++—interleave unpredictably. This leads to lost updates, corrupted memory structures, and concurrent modification exceptions identically to traditional Java threads. Furthermore, declaring a variable with @Volatile guarantees memory visibility across CPU caches but does not make compound read-modify-write sequences atomic.

## Practical walkthrough (English)

Consider a bank account balance updated concurrently by 1,000 coroutines on a multi-threaded dispatcher:
```kotlin
// Erroneous implementation: suffers from lost updates
var balance = 0
coroutineScope {
    repeat(1000) {
        launch(Dispatchers.Default) {
            balance++ // Non-atomic read-modify-write!
        }
    }
}
// Final balance will randomly evaluate to 890, 930, etc. instead of 1000!
```
The count++ operation compiles to three separate JVM bytecode instructions: loading the field onto the operand stack (GETFIELD), incrementing it (IADD), and storing it back (PUTFIELD). When two threads interleave, both read the identical initial value, compute the same increment, and overwrite each other, losing one update.
The thread-safe, linearizable solution using atomic primitives:
```kotlin
val atomicBalance = AtomicInteger(0)
coroutineScope {
    repeat(1000) {
        launch(Dispatchers.Default) {
            atomicBalance.incrementAndGet() // Hardware-level CAS guarantee
        }
    }
}
// Guaranteed to evaluate to exactly 1000
```

## Explanation in Arabic

المغالطة الشائعة بأن الـ Coroutines 'Thread-Safe تلقائياً' هي سبب كارثي في أخطاء التزامن (Concurrency Bugs):

1. ما هو الـ Race Condition؟
   - هو حالة تحدث عندما تحاول عمليتان أو أكثر قراءة وتعديل متغير مشترك (Shared Mutable State) في نفس الوقت، وتعتمد النتيجة النهائية على توقيت الوصول (Timing / Scheduling).
   - مثال: عمليتان تحاولان زيادة عداد `count++`. العملية تتكون من 3 خطوات في المعالج: قراءة القيمة، زيادتها، ثم حفظها. لو حدثت العمليتان بالتوازي، سيتم فقدان إحدى الزيادات وتصبح النتيجة خاطئة!

2. لماذا الـ Coroutines ليست Thread-Safe تلقائياً؟
   - الـ Coroutines تعمل على **Thread Pools** متعددة الخيوط (زي `Dispatchers.Default` و `Dispatchers.IO`).
   - لو أطلقت 100 coroutine وكل واحدة بتعدل في متغير عادي أو `ArrayList` مشترك، الـ Coroutines دي هتتنفذ على خيوط حقيقية متوازية في المعالج، وهيحصل Race Condition وتلف للبيانات أو `ConcurrentModificationException` تماماً مثل الـ Threads العادية!
   - الـ Coroutines تسهل كتابة الكود غير المتزامن، لكنها **لا تلغي قوانين الذاكرة وتزامن البيانات المشتركة (Shared State)**.

## Practical walkthrough

تطبيق حساب بنكي ومحفظة إلكترونية:
- عمليتان متزامنتان للإيداع بـ 100 جنيه لكل عملية:
```kotlin
// ❌ كود كارثي فيه Race Condition خطير:
var balance = 0
coroutineScope {
    repeat(1000) {
        launch(Dispatchers.Default) {
            balance++ // غير متزامن! في النهاية balance سيكون 920 أو 850 بدلاً من 1000!
        }
    }
}

// ✅ الحل باستخدام AtomicInteger أو Mutex:
val atomicBalance = AtomicInteger(0)
coroutineScope {
    repeat(1000) {
        launch(Dispatchers.Default) {
            atomicBalance.incrementAndGet() // عملية ذرية Hardware-level آمنة 100%
        }
    }
}
```

## Why it matters and how it works

Structured concurrency governs lifetime and failure, not mutual exclusion. Protect a shared invariant with an atomic operation, Mutex, confinement or database transaction. `@Volatile` improves visibility of a value but does not make compound read-modify-write atomic.

## Worked example

JVM example assumes `kotlinx-coroutines-core`; the atomic type makes one increment linearizable.

```kotlin
import java.util.concurrent.atomic.AtomicInteger
import kotlinx.coroutines.*

suspend fun countSafely(): Int {
    val count = AtomicInteger()
    coroutineScope {
        repeat(100) { launch(Dispatchers.Default) { count.incrementAndGet() } }
    } // all children have completed
    return count.get()
}
```

## Trade-offs and decision criteria

Atomics fit a single simple value; Mutex or a database transaction fits multi-field invariants. Confinement can simplify reasoning but creates a bottleneck. Do not use a coroutine dispatcher as an undocumented lock.

## Failure modes

`@Volatile var balance` still permits lost updates. A read, suspend, then write can race even on Main. Tests should force interleavings rather than relying on a flaky stress loop alone.

## Production perspective

A cart repository updates quantity and total together in one database transaction. UI state is derived from committed rows; concurrent taps cannot overwrite each other. Telemetry checks invariant violations and reconciliation.

## Interview answer — short

A race condition occurs when concurrent execution paths perform non-atomic read-modify-write mutations on shared state, causing non-deterministic data corruption. Coroutines are not automatically thread-safe because dispatchers like Dispatchers.Default and IO execute across multi-threaded thread pools. Structured concurrency manages lifecycles, not mutual exclusion. Developers must synchronize shared state using atomics, Mutex, confinement, or database transactions.

## Interview answer — structured

A race condition occurs when concurrent threads access and modify shared mutable memory concurrently, producing unpredictable results that depend on thread scheduling. A widespread misconception is that Kotlin coroutines prevent race conditions automatically.

Structured concurrency governs lifecycle boundaries, cancellation propagation, and child hierarchy, but provides zero serialization or mutual exclusion for shared state. Because standard dispatchers such as Dispatchers.Default and Dispatchers.IO execute across multi-threaded worker pools, multiple coroutines running in parallel can interleave on separate OS threads.

In production, compound operations like counter increments or collection modifications compile down to non-atomic read-modify-write bytecode sequences. When two coroutines read the identical state simultaneously, one modification overwrites the other, causing lost updates or concurrent modification crashes.

Developers must explicitly protect shared state using appropriate synchronization primitives. For single scalar variables, lock-free atomic primitives like AtomicInteger or AtomicReference provide hardware-level compare-and-swap guarantees, while complex multi-field invariants require suspending exclusion mechanisms like Mutex or thread confinement.


## Interview answer — deep senior

At the hardware and JVM memory model level, the execution of balance++ involves three distinct operations: reading the variable from main memory or L1 cache into a CPU register, executing the addition instruction in the arithmetic logic unit, and writing the modified value back to cache and main memory. When Dispatchers.Default schedules coroutines across multiple CPU cores, their execution pipelines interleave at the nanosecond scale. If core A and core B simultaneously read the value 42, both calculate 43, and both store 43 back into memory, resulting in a lost increment. Annotating the variable with @Volatile does not fix this race condition: @Volatile inserts memory barriers (like StoreLoad or LoadLoad fencing) ensuring that writes to the field become immediately visible to all other CPU caches, but it does not make the three-step read-modify-write sequence atomic. To guarantee correctness in concurrent coroutine architectures, engineers must choose between four proven strategies depending on data complexity and contention characteristics. First, lock-free atomics (AtomicInteger, AtomicLong, AtomicReference) leverage hardware-level CMPXCHG (compare-and-swap) instructions, delivering the lowest latency and zero thread blocking for isolated values. Second, for multi-variable state consistency where multiple fields must transition together atomically, kotlinx.coroutines.sync.Mutex provides non-blocking, suspending mutual exclusion without thread starvation. Third, thread confinement—either through dedicated single-thread dispatchers (Dispatchers.Main or limitedParallelism(1)) or actor pipelines—ensures that only one thread ever accesses the state, eliminating locks entirely. Fourth, in enterprise mobile architectures dealing with persistent business data, shared state should never reside in arbitrary memory variables; it must be managed through ACID database transactions in Room or SQLite, ensuring atomic write-ahead logging and crash recovery.

## How to answer in the interview

- **Why:** scheduling can interleave a compound update.
- **How:** demonstrate the lost update, then choose one synchronization boundary around the invariant.
- **Trade-off:** atomics fit one variable; mutex or transactions fit multi-field state.
- **Failure case:** volatile only provides visibility, not atomic read-modify-write.
- **Production solution:** use a server/database transaction for shared authoritative business state.

## Deep-dive talking points

Trace `read; suspend; write`, volatile visibility, local lock boundaries and server authority.

## Follow-up questions

- **Interviewer:** "Does running coroutines on `Dispatchers.Main` protect you from race conditions?"
  **Answer:** "Yes for purely synchronous code, because all execution is confined to the single main thread. However, if a coroutine suspends (e.g., across `delay` or network call), another event can run on the main thread during that suspension window and mutate the state, still producing a logical race condition."

- **Interviewer:** "Why is `volatile` not enough to fix `counter++`?"
  **Answer:** "`volatile` only guarantees memory visibility (that all threads read the latest value directly from main memory); it does not guarantee atomicity. The `++` operation is three separate instructions (read, increment, write). If two threads read simultaneously, one increment will overwrite the other."

- **Interviewer:** "What is the best way to handle shared mutable state in a ViewModel?"
  **Answer:** "Use `MutableStateFlow` with immutable data classes and update state via `_state.update { current -> ... }`, which performs atomic, non-blocking updates using atomic compare-and-set loops."

## Self-check rubric

Can I exhibit a lost update, explain volatile limits, choose a primitive and name the true source of truth?

## References and reviewed-on date

- [Kotlin shared mutable state](https://kotlinlang.org/docs/shared-mutable-state-and-concurrency.html) — lost updates, atomics and Mutex.

Technically reviewed against primary documentation on 2026-10-13.
