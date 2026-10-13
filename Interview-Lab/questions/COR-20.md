---
id: "COR-20"
question: "Compare Mutex, synchronized, atomic types, and confinement."
topic: "Kotlin Coroutines & Concurrency"
code: "COR"
group: "B"
phase: 1
priority: "P1"
order: 101
editorial_status: "reviewed"
---

# COR-20

## Original interview question

Compare Mutex, synchronized, atomic types, and confinement.

## What the interviewer evaluates

Compare suspending exclusion, blocking locks, atomics and confinement by invariant and resource cost.

## Explanation in Arabic

المقارنة بين وسائل حماية البيانات المشتركة في Kotlin Coroutines:

1. الـ `Mutex` (Kotlin Coroutines Mutex):
   - هو **Non-blocking (Suspending) Lock**.
   - لما coroutine تحاول تدخل كود محمي بـ `mutex.withLock` ويكون محجوزاً، الـ Coroutine **تُعلّق (Suspends)** وتترك الـ OS Thread حراً لينفذ مهام أخرى!
   - مخصص حصرياً لبيئة الـ Coroutines لحماية العمليات المعقدة والـ Suspend functions.

2. الـ `synchronized` (Java Monitors):
   - **Blocking Lock** على مستوى نظام التشغيل والـ JVM.
   - يحظر خيط المعالجة بالكامل (Blocks OS Thread).
   - **تحذير صارم:** لا يمكن استخدامه حول Suspend functions! ولا يجب استخدامه داخل Coroutines لأنه يستهلك الـ Threads ويسبب تجويع الـ Thread Pool و ANR.

3. الـ Atomic Types (`AtomicInteger`, `AtomicReference`):
   - مبنية على تعليمات الـ CPU المباشرة: **Compare-And-Swap (CAS)**.
   - أسرع وسيلة على الإطلاق (Lock-free و Zero-overhead) للعمليات البسيطة (زي العدادات وتحديث المراجع الفردية).
   - لا تناسب العمليات المعقدة متعددة الخطوات.

4. الـ Thread Confinement (الحصر على خيط واحد):
   - حصر جميع عمليات التعديل على Thread واحد محدد (زي `Dispatchers.Main` أو `Dispatchers.Default.limitedParallelism(1)`).
   - بسيط جداً ويمنع الحاجة لأي Locks، لكنه قد يكون عنق زجاجة لو العمليات ثقيلة جداً.

## Practical walkthrough

مقارنة عملية لاختيار الأداة المناسبة:
1. **عداد مرات النقر (Simple Counter):**
   - الأفضل: `private val clickCount = AtomicInteger(0)` -> `clickCount.incrementAndGet()` (أسرع بنية).
2. **قراءة ملف، تحديث التوكن، ثم حفظه في قاعدة البيانات (Suspending critical section):**
   - الأفضل: `private val mutex = Mutex()` -> `mutex.withLock { refreshToken() }` (يعلق بدون حظر خيوط).
3. **إدارة حالة الـ UI في الـ MVI ViewModel:**
   - الأفضل: `Thread Confinement` على Main Thread أو استخدام `MutableStateFlow.update { }`.

## Why it matters and how it works

Choose the smallest primitive that protects the entire invariant. `Mutex.withLock` is cancellable while waiting; keep its critical section short and do not call slow network operations inside. `synchronized` can be right for tiny non-suspending JVM state. Atomics provide linearizable primitives, while thread/actor confinement serializes access.

## Worked example

Kotlin/JVM illustration uses `kotlinx-coroutines-core`; both fields change under one mutex.

```kotlin
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

class Inventory {
    private val mutex = Mutex()
    private var stock = 10
    suspend fun reserve(units: Int): Boolean = mutex.withLock {
        if (units > stock) false else { stock -= units; true }
    }
}
```

## Trade-offs and decision criteria

An atomic integer is lean for counters but cannot atomically enforce a multi-field business rule alone. Mutex suspension avoids blocked waiting threads but is process-local. Database transactions and server constraints are needed for persistent/cross-device invariants.

## Failure modes

Holding a Mutex while awaiting an HTTP call serializes unrelated users and can deadlock through re-entrant paths. `synchronized` plus a suspend operation is invalid or unsafe. A process-local lock cannot prevent another device reserving the same server inventory.

## Production perspective

A repository uses a local Mutex to coalesce token refresh calls, then the server enforces account/session rules. For stock or money, the authoritative database transaction prevents cross-process races; Android locks only protect local coordination.

## Interview answer — short

Mutex is a non-blocking, suspension-aware lock designed for coroutines; synchronized is a thread-blocking Java monitor that must never be used with suspending functions; Atomic types use hardware-level compare-and-swap (CAS) for lock-free primitive updates; and Confinement confines state mutation to a single thread/dispatcher, eliminating locks entirely.

## Interview answer — structured

Choosing the right synchronization tool depends on whether the critical section suspends, how long it runs, and the complexity of the shared state.

**Mutex** is Kotlin's suspension-aware mutual exclusion lock. When a coroutine waits for a locked Mutex via `mutex.withLock`, it suspends without blocking the underlying OS thread, keeping worker pools responsive. It is the only choice when protecting a critical section that contains suspending calls.

**synchronized** is Java's traditional monitor lock. It forcibly blocks the operating system thread. You cannot call suspending functions inside a synchronized block, and using it in coroutines is an anti-pattern because it starves thread pools and can cause ANRs.

**Atomic types** (AtomicInteger, AtomicReference) provide lock-free, ultra-fast synchronization for single variables via CPU Compare-And-Swap (CAS) instructions, with zero lock contention overhead.

**Thread Confinement** confines all mutations to a single dispatcher (such as `Dispatchers.Main` or `Dispatchers.Default.limitedParallelism(1)`), eliminating the need for locks altogether through structural design.

## Interview answer — deep senior

At the performance and scheduling layer, each approach presents different trade-offs: `AtomicInteger` has zero suspension and zero lock overhead; it is resolved directly in CPU registers via cache coherency protocols (MESI). However, CAS loops can experience spinning overhead under extreme contention.

`Mutex` involves internal queue management (`LockContender` nodes on the heap). While non-blocking, acquiring and releasing a Mutex is significantly more expensive in CPU instructions than an atomic CAS. Therefore, you should never use a Mutex for a simple primitive increment.

With Thread Confinement using `limitedParallelism(1)`, Kotlin creates an exclusive sequential queue on top of the shared pool. It provides the simplicity of single-threaded programming without locking, but context switching across dispatchers via `withContext(singleThreadDispatcher)` incurs dispatch latency. In Android architecture, combining `AtomicReference` or `StateFlow.update` with immutable data structures offers the cleanest and most performant state synchronization.

## How to answer in the interview

- **Why:** choose synchronization by the shape of the invariant.
- **How:** mutex suspends waiters; synchronized blocks a JVM thread; atomic CAS protects small state; confinement serializes access.
- **Trade-off:** locks add contention and confinement adds a queue.
- **Failure case:** suspending inside a monitor or protecting only one field.
- **Production solution:** enforce authoritative cross-device invariants transactionally.

## Deep-dive talking points

Defend critical-section size, recheck-after-lock, lock scope and persistent invariants.

## Follow-up questions

- **Interviewer:** "Why does the Kotlin compiler forbid calling suspend functions inside a `synchronized` block?"
  **Answer:** "Because Java synchronized blocks bind a lock to the executing OS thread. If a coroutine suspended inside synchronized, it would yield the thread while retaining the monitor lock, creating immediate deadlocks and thread starvation across the runtime."

- **Interviewer:** "Is Kotlin's `Mutex` re-entrant?"
  **Answer:** "No! Kotlin's standard `Mutex` is non-reentrant. If a coroutine that already holds a Mutex attempts to acquire it again (e.g., in a nested function call), it will suspend and deadlock itself indefinitely."

- **Interviewer:** "How does `Dispatchers.Default.limitedParallelism(1)` compare to a single-threaded executor?"
  **Answer:** "A traditional single-threaded executor allocates a dedicated OS thread permanently. `limitedParallelism(1)` shares the general worker pool and ensures that at most one coroutine executes at any time, eliminating the overhead of keeping a dedicated thread alive."

## Self-check rubric

Can I compare waiting behavior, pick by invariant, avoid network calls under locks and state process boundaries?

## References and reviewed-on date

- [Kotlin shared mutable state](https://kotlinlang.org/docs/shared-mutable-state-and-concurrency.html) — atomics, confinement and Mutex.

Technically reviewed against primary documentation on 2026-10-13.
