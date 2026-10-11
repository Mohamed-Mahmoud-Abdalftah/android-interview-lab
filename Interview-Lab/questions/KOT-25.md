---
id: "KOT-25"
question: "Your app has a mutable val list shared across threads. Is it thread-safe? Explain."
topic: "Kotlin Core & Advanced"
code: "KOT"
group: "C"
phase: 1
priority: "P1"
order: 25
editorial_status: "reviewed"
---

# KOT-25

## Original interview question

Your app has a mutable val list shared across threads. Is it thread-safe? Explain.

## What the interviewer evaluates

Reject the false equation of `val` with immutability or thread safety and propose safe ownership.

## Explanation in Arabic

`val shared = mutableListOf<Item>()` يثبّت الـreference بس. كل thread يقدر ينادي `add` أو يقرأ في نفس الوقت، و`MutableList`/`ArrayList` ما عندهاش synchronization contract؛ النتيجة ممكن race، lost update، inconsistent iteration، أو exception. حتى لو `List` read-only alias، writer تاني يغير الـbacking. عشان تبقى آمنة اختار single owner (actor أو thread confinement)، lock/`Mutex` للعمليات المركبة، أو immutable snapshots منشورة عبر state holder مناسب. قرارك لازم يشمل atomicity للـread-modify-write، مش مجرد visibility.

## Why it matters and how it works

Thread safety belongs to access protocol and data structure, not variable binding. Unsynchronized read/write can violate invariants; even synchronized individual operations may not make a multi-step transaction atomic.

## Worked example

JVM example using a lock for a compound append-and-snapshot operation; callers receive a copy.
```kotlin
class SafeQueue<T> {
    private val lock = Any()
    private val items = mutableListOf<T>()
    fun addAndSnapshot(item: T): List<T> = synchronized(lock) {
        items.add(item)
        items.toList()
    }
}
```
This is synchronous; do not hold a JVM monitor across a suspending call.

## Trade-offs and decision criteria

A lock is simple for short critical sections but can block and deadlock if misused. `Mutex` supports suspending coroutines, but a single-writer model may be clearer. Immutable snapshots simplify readers at allocation cost. Atomic references work for small immutable state with retryable updates, not arbitrary mutable list operations.

## Failure modes

Two coroutines read `size`, append, and assume each got a unique index. `val` offers no atomicity; separate method calls can interleave. Protect the whole invariant or use a state update operation. Avoid modifying a list while Compose/RecyclerView reads it.

## Production perspective

A shopping-cart repository serializes updates in one owner and emits immutable cart snapshots to UI. Tests use concurrent producers and verify item count and order invariants. Large carts may use a persistent structure or database transaction after profiling.

## Interview answer — short

No. `val` only prevents rebinding the list variable; the `MutableList` remains mutable and unsynchronized. Shared reads and writes need confinement, a lock or Mutex, or immutable state with atomic publication.

## Interview answer — structured

I separate three issues: stable reference, mutable object, and concurrent access. `val` solves only the first. A shared `MutableList` can race during add, iteration, or compound read-modify-write operations. I choose a single writer or guard the complete operation with synchronization, then expose immutable snapshots to readers. A read-only `List` view of the same backing list is not enough. Suppose two workers append and then read the list size. Their operations can interleave, so even a synchronized `add` alone does not necessarily protect the compound invariant they expect. Which option is best depends on access frequency and whether the operation suspends. For a UI-facing API I expose a snapshot or a state stream, not the mutable list itself. That keeps readers from observing a collection mid-update.

## Interview answer — deep senior

For this specific scenario I would inspect who writes, who reads, and the invariant: order, uniqueness, count, or snapshot consistency. `ArrayList` has no general concurrent mutation guarantee, and the Java memory model does not make unsynchronized access safe because the reference is final-like. Synchronizing only `add` while iterating elsewhere still fails. In a coroutine app I may use a `Mutex` or single actor; for UI state I favor immutable snapshots and atomic updates. I test interleavings and keep expensive work outside critical sections. The keyword answers only whether the variable can be rebound. The object behind a `val MutableList` is still mutable, and a typical list implementation has no general guarantee for concurrent reads and writes. A read-only `List` alias does not protect against mutation through another alias. I would define the actual invariant: perhaps unique IDs and a consistent ordered snapshot. Then I would guard the entire read-modify-write sequence, not merely individual methods, or confine writes to one owner. Concurrent tests and UI snapshot tests should verify behavior rather than relying on `val` as a concurrency claim. I also distinguish visibility from atomicity: a volatile or final-like reference does not make a series of list operations indivisible. The solution must match the invariant and the caller lifetime, and be tested under concurrent producers rather than inferred from syntax.

## Deep-dive talking points

Discuss visibility versus atomicity, iteration under mutation, lock scope, `Mutex`, single-writer architecture and snapshot cost.

## Follow-up questions

- [KOT-02](../kot-02/): What does `val` actually guarantee? **Answer:** no reassignment of the binding after initialization.
- [KOT-16](../kot-16/): Would exposing `List` fix the race? **Answer:** no; it only limits caller methods, not backing mutations.

## Self-check rubric

Identify the race despite `val`, propose a complete invariant-preserving strategy, and explain why read-only view is insufficient.

## References and reviewed-on date

- [Kotlin shared mutable state](https://kotlinlang.org/docs/shared-mutable-state-and-concurrency.html) — concurrency strategies.
- [Kotlin collections overview](https://kotlinlang.org/docs/collections-overview.html) — mutable/read-only contracts.

Technically reviewed against the linked primary documentation on 2026-10-11. Examples are illustrative JVM snippets unless explicitly labeled conceptual; no Android device claim is made.
