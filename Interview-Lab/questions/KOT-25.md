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

## Practical walkthrough

لو `val events = mutableListOf<Event>()` بتتكتب من network callback وتتقرأ من UI thread، ثبات reference ما يمنعش race، lost update، ولا iteration exception. حدّد الـinvariant: هل order مهم؟ هل snapshot لازم يكون consistent؟ في المثال `synchronized(lock)` بيغطي add والنسخ في critical section واحدة، فكل snapshot تشوف ترتيبًا كاملًا حتى وقت النداءات المتزامنة. لكن ما تمسكش monitor أثناء suspend أو I/O. في ViewModel غالبًا خلي التحديثات مملوكة لكوروتين/dispatcher واحد أو استخدم `MutableStateFlow.update` للـstate immutable، مع الانتباه إن العناصر الداخلية ما تكونش mutable aliases.

## Trade-offs and decision criteria

A lock is simple for short critical sections but can block and deadlock if misused. `Mutex` supports suspending coroutines, but a single-writer model may be clearer. Immutable snapshots simplify readers at allocation cost. Atomic references work for small immutable state with retryable updates, not arbitrary mutable list operations.

## Failure modes

Two coroutines read `size`, append, and assume each got a unique index. `val` offers no atomicity; separate method calls can interleave. Protect the whole invariant or use a state update operation. Avoid modifying a list while Compose/RecyclerView reads it.

## Production perspective

A shopping-cart repository serializes updates in one owner and emits immutable cart snapshots to UI. Tests use concurrent producers and verify item count and order invariants. Large carts may use a persistent structure or database transaction after profiling.

## Interview answer — short

No. `val` fixes the list reference, but `MutableList` operations are not generally safe under concurrent reads and writes. I define the required invariant, then serialize updates or use a lock and publish immutable snapshots. I never hold a JVM lock across suspension.

## Interview answer — structured

I would ask which threads write and what readers need to observe. A `val` list still mutates, and compound operations such as append then snapshot can race with another writer or iterator. If the invariant is an ordered snapshot, I protect both mutation and copying with the same lock, or give a single owner responsibility for updates. In a ViewModel, immutable state values and atomic `MutableStateFlow.update` may fit better, provided I do not leak mutable nested objects. I avoid blocking or suspending work while holding a monitor and test contention rather than assuming a passing single-thread test proves safety.

## Interview answer — deep senior

For this specific scenario I would inspect who writes, who reads, and the invariant: order, uniqueness, count, or snapshot consistency. `ArrayList` has no general concurrent mutation guarantee, and the Java memory model does not make unsynchronized access safe because the reference is final-like. Synchronizing only `add` while iterating elsewhere still fails. In a coroutine app I may use a `Mutex` or single actor; for UI state I favor immutable snapshots and atomic updates. I test interleavings and keep expensive work outside critical sections. The keyword answers only whether the variable can be rebound.

In a payment-attempt queue, an append and subsequent snapshot must form one coherent operation if the UI promises ordered history. Locking only the append while another thread iterates is insufficient; the same owner or lock must cover the read. I would keep blocking I/O and suspension outside a JVM monitor. In a coroutine architecture, immutable state with atomic `MutableStateFlow.update` can be appropriate, but its update lambda may be reevaluated under contention, so side effects do not belong inside it. I would stress-test concurrent writers and make the observable invariant explicit rather than relying on `val`.

## How to answer in the interview

- **Why:** Distinguish reference immutability (`val`) from thread-safe access to underlying collections.
- **How:** Protect shared mutable data using synchronization primitives (`Mutex`, `AtomicReference`, synchronized blocks) or confinement to a single thread/dispatcher.
- **Trade-offs:** Locking introduces contention, thread blocking, and potential deadlocks; copying collections on every write introduces garbage collection churn.
- **Failure cases:** Sharing a `val list = mutableListOf<T>()` across multiple coroutine dispatchers without synchronization, causing data corruption or `ConcurrentModificationException`.
- **Production solution:** Confine state mutations to a single dispatcher or actor loop, publish immutable snapshots (`List<T>`), or use thread-safe data structures like `ConcurrentHashMap`.

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

Technically reviewed against the linked primary documentation on 2026-10-13. Examples are illustrative JVM snippets unless explicitly labeled conceptual; no Android device claim is made.
