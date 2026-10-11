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

`Mutex` بيعمل critical section للـcoroutines و`lock` بتعلّق بدل ما تحجز thread وهي مستنية. `synchronized` lock للـJVM بيحجز thread أثناء الانتظار ومينفعش تحط suspend call داخل الـmonitor. Atomic types ممتازة لعملية صغيرة على قيمة واحدة. Confinement معناه مالك واحد يعدّل الـstate، وده يبسط التصميم لكن ممكن يبقى bottleneck.

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

“Mutex gives coroutine-friendly exclusion; synchronized blocks a thread; atomics suit simple single-value operations; confinement serializes access under one owner. I choose based on the invariant and whether it is local or persistent.”

## Interview answer — structured

“If I only increment one counter, an atomic primitive is simple and efficient. If I must check and update multiple in-memory fields together, `Mutex.withLock` gives a suspending wait and a clear critical section. `synchronized` is acceptable for tiny non-suspending JVM code but blocks waiting threads. Confinement can remove locks by giving state one owner, at a throughput cost. For data that must remain correct across processes or devices, I use a database or server transaction instead of trusting an app-level lock. An atomic integer is lean for counters but cannot atomically enforce a multi-field business rule alone. Mutex suspension avoids blocked waiting threads but is process-local. Database transactions and server constraints are needed for persistent/cross-device invariants. A repository uses a local Mutex to coalesce token refresh calls, then the server enforces account/session rules.”

## Interview answer — deep senior

“I distinguish local coordination from the authoritative invariant. A Mutex protects coroutines that share that exact instance and its `lock` suspends while waiting, but the lock does not survive process death. A JVM monitor can be fast for tiny synchronous sections, yet blocking and suspension do not mix inside it. Atomics are ideal for a single CAS-style operation; combining fields often requires a loop or stronger transaction. Confinement, such as an actor, serializes mutations and makes ordering explicit but can become a hotspot. In a token refresh repository I might use a Mutex to prevent duplicate refresh calls and recheck the token inside the lock. For financial balance, server transaction and idempotent operation records remain authoritative. Choose the smallest primitive that protects the entire invariant. `Mutex.withLock` is cancellable while waiting; keep its critical section short and do not call slow network operations inside. `synchronized` can be right for tiny non-suspending JVM state. Atomics provide linearizable primitives, while thread/actor confinement serializes access. Holding a Mutex while awaiting an HTTP call serializes unrelated users and can deadlock through re-entrant paths. `synchronized` plus a suspend operation is invalid or unsafe. A process-local lock cannot prevent another device reserving the same server inventory. A repository uses a local Mutex to coalesce token refresh calls, then the server enforces account/session rules.”

## Deep-dive talking points

Defend critical-section size, recheck-after-lock, lock scope and persistent invariants.

## Follow-up questions

- [COR-19](../cor-19/): Why is volatile insufficient? **Answer:** it does not make compound updates atomic.
- [COR-28](../cor-28/): What fixes balance races? **Answer:** a transaction at the authoritative ledger, with local synchronization only as support.

## Self-check rubric

Can I compare waiting behavior, pick by invariant, avoid network calls under locks and state process boundaries?

## References and reviewed-on date

- [Kotlin shared mutable state](https://kotlinlang.org/docs/shared-mutable-state-and-concurrency.html) — atomics, confinement and Mutex.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
