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

A race condition occurs when concurrent tasks read and modify shared mutable state without synchronization, yielding corrupted results. Coroutines are not automatically thread-safe because they execute across multi-threaded dispatcher pools (like Default and IO); accessing shared mutable state concurrently causes identical data races and memory corruption as traditional threads.

## Interview answer — structured

A race condition happens when multiple concurrent execution paths access and mutate shared state without coordination, producing non-deterministic bugs that depend on thread execution timing.

A frequent misconception is that switching from Java threads to Kotlin coroutines magically makes code thread-safe. It does not. Coroutines dispatched on `Dispatchers.Default` or `Dispatchers.IO` execute on underlying multi-threaded worker pools. If two coroutines simultaneously read, increment, and write back a shared variable like `counter++`, CPU thread switching causes lost updates.

Furthermore, standard Java collections like `ArrayList` or `HashMap` have no internal synchronization; concurrent coroutine writes will corrupt their internal arrays and throw `ConcurrentModificationException`.

To prevent race conditions, we must synchronize access using techniques suited for coroutines: thread confinement, atomic primitives, Kotlin's non-blocking `Mutex`, or immutable state flows.

## Interview answer — deep senior

At the hardware and memory architecture level, modern multicore processors use private L1 and L2 caches. Without memory synchronization barriers, writes performed by a coroutine on Core A may remain in Core A's store buffer and not be visible to Core B executing another coroutine. This violates the Java Memory Model's (JMM) 'happens-before' guarantee.

When dealing with suspension points, race conditions can become even more insidious: a coroutine might read a shared balance, suspend across a network call, and then write back the balance. During the suspension window, another coroutine could have modified the balance multiple times, causing a classic Time-of-Check to Time-of-Use (TOCTOU) race condition.

In modern Android MVI/Unidirectional Data Flow architectures, the ultimate cure for race conditions is eliminating shared mutable state entirely: we confine state mutation to a single coroutine dispatcher or use atomic compare-and-swap loops inside `MutableStateFlow.update { current -> current.copy(...) }`.

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
