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

## Concept and technical explanation

A common concurrency misconception in Kotlin is assuming that declaring a collection with `val` makes it immutable or thread-safe. In Kotlin, `val` provides reference immutability only: it guarantees that the variable binding cannot be reassigned to point to another object reference. It provides zero guarantees regarding the internal mutability or structural thread safety of the referenced instance. When a mutable collection—such as `mutableListOf()` which aliases `java.util.ArrayList`—is shared across multiple concurrent threads or coroutines without synchronization, data race conditions inevitably occur. Concurrent additions, removals, and reads will trigger `ConcurrentModificationException`, corrupt the internal capacity backing array, cause lost updates, or produce silent data inconsistencies. Thread safety is an architectural property of access synchronization protocols and data structures, not variable declaration keywords.

## Practical walkthrough (English)

Consider a background telemetry reporter where multiple coroutines write event logs to a shared list declared as `val events = mutableListOf<String>()`. Simultaneously, a periodic flusher reads `events.toList()` or iterates over `events` to transmit data to the network. Because `ArrayList` is unsynchronized, when Thread A appends an item while Thread B iterates the list, Thread B crashes with a `ConcurrentModificationException` because the internal `modCount` changed during iteration. Even worse, if two background threads append simultaneously, both may observe the same internal array size, write to the same index, and increment size once, silently losing telemetry events. The architectural resolution requires either explicit synchronization: `val queue = ConcurrentLinkedQueue<String>()` or a Mutex in coroutines: `private val mutex = Mutex(); suspend fun log(event: String) = mutex.withLock { events.add(event) }`. In presentation layers, state should be modeled using immutable snapshots emitted via `StateFlow<List<String>>`.

## Explanation in Arabic

السؤال عن `val list = mutableListOf<String>()` بيختبر فهمك للفرق الجوهري بين **Immutability of Reference** و **Thread Safety of Data**:

1. معنى `val` في Kotlin:
   - `val` تعني فقط إن الـ **Reference** (المؤشر) نفسه ثابت لا يمكن إعادة إسناده لكائن آخر في الـ Heap.
   - `val` **لا تعني أبداً** إن الكائن نفسه Immutable!

2. هل `mutableListOf()` Thread-Safe؟
   - **إطلاقاً! لا توجد أي Thread-Safety!**
   - `mutableListOf()` في الـ JVM بترجع `java.util.ArrayList`. الـ ArrayList غير محمية بأي مزامنة (Non-synchronized).
   - لو Thread بيكتب عنصر (`add()`) في نفس الوقت اللي Thread تاني بيقرأ أو بيلف على الـ List (`for` loop):
     * هيحصل `ConcurrentModificationException` فوراً.
     * أو يحصل Data Corruption وفقدان بيانات في الـ internal array بدون استثناء ظاهر (Silent Bug).

3. الحلول الإنتاجية الصحيحة (Production Solutions):
   - **Concurrent Collections:** استخدام `CopyOnWriteArrayList` (لو القراءات كتيرة جداً والتعديلات نادرة).
   - **مزامنة عبر Coroutines:** حصر تعديل وقراءة الـ List على Single Thread أو استخدام Coroutines Mutex (`Mutex.withLock`).
   - **StateFlow مع Immutable Snapshots:** في الـ MVI، بنحتفظ بـ `List` غير قابلة للتعديل ونعمل Update بإنشاء New List باستخدام `_state.update { it.copy(...) }`.

## Practical walkthrough

في شاشة الدردشة وتلقي الرسائل عبر WebSocket:
- الرسائل بتوصل من WebSocket Thread، وشاشة العرض بتقرأ القائمة في الـ Main Thread.
- **الكود الكارثي:**
  val messages = mutableListOf<Message>()
  // في WebSocket Thread:
  messages.add(newMessage)
  // في UI Thread:
  for (msg in messages) render(msg) // CRASH: ConcurrentModificationException!
- **الحل الإنتاجي باستخدام Mutex و Defensive Copying:**
  private val mutex = Mutex()
  private val _messages = mutableListOf<Message>()
  suspend fun addMessage(msg: Message) = mutex.withLock {
      _messages.add(msg)
  }
  suspend fun getSnapshot(): List<Message> = mutex.withLock {
      _messages.toList() // Snapshot آمن تماماً للقراءة في الـ UI
  }

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

Declaring a mutable list with val guarantees only reference immutability, not thread safety. The underlying ArrayList remains completely mutable and unsynchronized; concurrent reads and writes across threads cause data races, corrupted internal arrays, and ConcurrentModificationException crashes.

## Interview answer — structured

Declaring a list with val in Kotlin ensures only that the reference variable cannot be reassigned to another object on the heap. It provides absolutely zero guarantees regarding the thread safety or structural immutability of the underlying collection instance.

An ArrayList is completely unsynchronized. If multiple concurrent threads or coroutines perform unsynchronized reads and writes on a shared mutable list, the application will experience severe data race conditions.

In production, iterating over the list on one thread while another thread appends an element triggers an immediate ConcurrentModificationException due to mismatched modification counts.

Thread safety requires disciplined ownership: encapsulating mutations behind a Mutex or synchronization lock, adopting concurrent collections, or emitting immutable snapshots through unidirectional data flow pipelines.


## Interview answer — deep senior

From the perspective of the Java Memory Model (JMM) and modern multi-core CPU architectures, `val` on a mutable collection provides neither atomicity nor memory visibility. Under the hood, `java.util.ArrayList` stores its elements in an internal `transient Object[] elementData` array accompanied by a primitive `int size` field. Neither of these internal fields is marked `volatile`. Consequently, when Thread 1 appends an element, the write to the internal array and the write to the `size` counter may be reordered by the CPU or cached inside Core 1's L1 cache without issuing a memory barrier. Thread 2 executing on Core 2 can observe an updated `size` while reading stale or null references from the backing array. Furthermore, when an `ArrayList` exceeds its capacity, it allocates a new, larger array and executes `System.arraycopy()`. If another thread reads or writes during this expansion window, it can read uninitialized memory or write to the abandoned array, causing irrecoverable data loss. In modern Kotlin Coroutines architectures, blocking primitives like `synchronized` or `ReentrantLock` should not be used across suspension points because holding a monitor while suspending blocks the underlying carrier thread. Instead, engineers employ `kotlinx.coroutines.sync.Mutex`, confine state mutations to a single dispatcher via an actor pattern, or utilize persistent data structures from `kotlinx.collections.immutable` where every state update yields a structural-sharing snapshot safe for concurrent dissemination.

## How to answer in the interview

- **Why:** Distinguish reference immutability (`val`) from thread-safe access to underlying collections.
- **How:** Protect shared mutable data using synchronization primitives (`Mutex`, `AtomicReference`, synchronized blocks) or confinement to a single thread/dispatcher.
- **Trade-offs:** Locking introduces contention, thread blocking, and potential deadlocks; copying collections on every write introduces garbage collection churn.
- **Failure cases:** Sharing a `val list = mutableListOf<T>()` across multiple coroutine dispatchers without synchronization, causing data corruption or `ConcurrentModificationException`.
- **Production solution:** Confine state mutations to a single dispatcher or actor loop, publish immutable snapshots (`List<T>`), or use thread-safe data structures like `ConcurrentHashMap`.

## Deep-dive talking points

Discuss visibility versus atomicity, iteration under mutation, lock scope, `Mutex`, single-writer architecture and snapshot cost.

## Follow-up questions

- **Interviewer:** "Why is `CopyOnWriteArrayList` not suitable for frequent write operations?"
  **Answer:** "Because every single write operation (add, remove, set) creates a full copy of the entire underlying array. If you have 5,000 items and append 100 items per second, it allocates 100 arrays of 5,000 items every second, creating extreme heap churn and triggering severe GC pauses."

- **Interviewer:** "How does `StateFlow.update { }` ensure thread safety without locks?"
  **Answer:** "`StateFlow.update` uses an atomic Compare-And-Set (CAS) loop on an `AtomicReference`. It reads the current value, computes the new value in the transform lambda, and attempts an atomic CAS. If another thread updated the state in the meantime, the CAS fails and it retries the loop automatically."

- **Interviewer:** "What is the difference between Kotlin's Mutex and Java's synchronized block?"
  **Answer:** "A Java synchronized block blocks the underlying OS thread, keeping it idle and unavailable for other work. Kotlin's Mutex is suspension-aware: when a coroutine waits for a locked Mutex, it suspends its state machine, freeing the underlying thread to execute other coroutines."

## Self-check rubric

Identify the race despite `val`, propose a complete invariant-preserving strategy, and explain why read-only view is insufficient.

## References and reviewed-on date

- [Kotlin shared mutable state](https://kotlinlang.org/docs/shared-mutable-state-and-concurrency.html) — concurrency strategies.
- [Kotlin collections overview](https://kotlinlang.org/docs/collections-overview.html) — mutable/read-only contracts.

Technically reviewed against primary documentation on 2026-10-13.
