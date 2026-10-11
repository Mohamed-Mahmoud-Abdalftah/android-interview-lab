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

الـrace condition بتحصل لما النتيجة تعتمد على ترتيب interleaving بين عمليات متزامنة. `counter++` قراءة ثم حساب ثم كتابة، مش خطوة atomic؛ coroutines على `Default` ممكن تشتغل على threads مختلفة وتضيّع تحديثات. وحتى على thread واحد، suspension بين القراءة والكتابة يسمح coroutine تانية تغيّر القيمة.

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

“A race is an outcome that depends on execution order. Coroutines do not make `read; modify; write` atomic. I protect the shared invariant with an atomic primitive, Mutex, confinement or database transaction.”

## Interview answer — structured

“Coroutines can run concurrently or in parallel, so shared mutable state has the usual race problems. `counter++` contains separate read and write steps and can lose increments. A single thread is not automatically safe if an operation suspends between those steps. I choose an atomic operation for a simple counter, Mutex for in-memory multi-step state, or a database transaction for persistent invariants. `@Volatile` alone does not solve compound updates.”

## Interview answer — deep senior

“I first identify the invariant, not just the variable. An atomic integer can make a simple increment linearizable, but a balance update that must check funds and append a ledger entry needs a transaction at the authoritative store. A Mutex only protects participants using that same in-process lock and disappears after process death; it cannot coordinate other devices or server workers. A confined actor can serialize messages, but may bottleneck throughput. I test a forced interleaving of two updates and then assert the invariant, and I keep server-side financial authority even if the Android client uses a local synchronization primitive.”

## Deep-dive talking points

Trace `read; suspend; write`, volatile visibility, local lock boundaries and server authority.

## Follow-up questions

- [COR-20](../cor-20/): Which primitive fits multiple fields? **Answer:** Mutex or a transaction, depending on where the invariant lives.
- [COR-28](../cor-28/): Why is `balance++` unsafe? **Answer:** it is a compound read-modify-write operation.

## Self-check rubric

Can I exhibit a lost update, explain volatile limits, choose a primitive and name the true source of truth?

## References and reviewed-on date

- [Kotlin shared mutable state](https://kotlinlang.org/docs/shared-mutable-state-and-concurrency.html) — lost updates, atomics and Mutex.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
