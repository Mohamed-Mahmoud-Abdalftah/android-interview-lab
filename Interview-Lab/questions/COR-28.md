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

لو coroutine A وB قرأوا balance=100 ثم كل واحدة حسبت +10 وكتبت 110، ضاع تحديث بدل 120. `suspend` أو `Dispatchers.Default` لا يحموا العملية المركبة. داخل process ممكن `Mutex` يحمي القراءة والتعديل؛ لكن balance مالية حقيقية لازم تتحسم في database/server transaction أو ledger، لأن قفل Android لا ينسّق أجهزة تانية.

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

“Two coroutines can both read 100 and each write 110, losing one update. A shared Mutex or atomic update fixes a local number. For real money I rely on a server transaction and idempotent ledger operation, not an app-only lock.”

## Interview answer — structured

“The race is a compound read-modify-write. If two coroutines read the same balance before either writes, the final value loses one delta. A Mutex around the entire local critical section prevents that for users of the same instance, while an atomic type can suit a simple number. But a financial balance crosses process and device boundaries, so the backend must commit the invariant in a transaction, ideally through an operation ID and ledger entry. I test forced interleavings and crash/retry cases, not just happy-path arithmetic. An atomic long works for a single local number, but checking limits plus posting history needs a larger transaction. Mutex is easy to reason about but process-local. For actual payments, append-only server ledger and idempotent transaction endpoint are authoritative.”

## Interview answer — deep senior

“I would first reproduce the interleaving deterministically: both tasks read 100, pause, then both write 110. A `Mutex.withLock` around read, validation and write fixes the in-process race; `@Volatile` does not because the compound operation is still not atomic. An `AtomicLong` can fix a local increment, but cannot by itself atomically add an audit entry or check credit limits. For production money, the server owns the ledger and wraps balance/constraint updates in one transaction. The client sends a stable operation key, treats timeouts as uncertain and reconciles, because process death or another device bypasses any local Mutex. Tests assert no lost update and no duplicate ledger entry under concurrent retries. The vulnerable read-modify-write spans multiple operations. `Mutex.withLock` makes the in-memory section exclusive for coroutines sharing that Mutex. A server transaction enforces the invariant across clients and crash/retry boundaries; use operation IDs to avoid duplicated increments. Test with barriers to force the two reads before writes. `@Volatile` makes reads/writes visible but does not make `balance += delta` atomic. Locking only the write still lets two callers read the same old value. A client lock is lost after process death and cannot coordinate another device. A wallet UI reads server ledger-derived balance. The backend transaction checks constraints and posts one idempotent operation.”

## Deep-dive talking points

Force the read-read-write-write schedule; compare local lock, atomic and server transaction scopes.

## Follow-up questions

- [COR-19](../cor-19/): Why are coroutines not safe automatically? **Answer:** they do not make compound shared operations atomic.
- [COR-27](../cor-27/): How handle uncertain write? **Answer:** reconcile a stable operation ID before retry.

## Self-check rubric

Can I show the lost update, protect the whole critical section, and state why the backend remains authoritative?

## References and reviewed-on date

- [Kotlin shared mutable state](https://kotlinlang.org/docs/shared-mutable-state-and-concurrency.html) — lost increments and Mutex.
- [Android offline-first guidance](https://developer.android.com/topic/architecture/data-layer/offline-first) — local/remote source-of-truth design.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
