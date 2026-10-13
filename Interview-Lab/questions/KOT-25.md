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

No, it is completely thread-unsafe. The 'val' keyword only makes the variable reference immutable, not the underlying collection. Because mutableListOf returns an unsynchronized ArrayList, concurrent reads and writes across threads will cause ConcurrentModificationExceptions, index corruption, and silent data loss.

## Interview answer — structured

It is definitively not thread-safe. A common misconception is that declaring a collection with `val` confers immutability or concurrency protection. In reality, `val` simply prevents reassigning the variable reference to another object on the heap; the underlying object itself remains completely mutable.

Under the hood, `mutableListOf()` instantiates a `java.util.ArrayList`. ArrayList has zero internal synchronization. If one thread is executing `add()` while another is iterating the list, the `modCount` counter mismatch will throw a `ConcurrentModificationException`. Even worse, if two background threads execute `add()` simultaneously, race conditions on the internal array index can overwrite elements, corrupt the list size, or cause an internal ArrayIndexOutOfBoundsException.

To handle concurrent collections in production, I use one of three strategies: 1) synchronize access using a Coroutines `Mutex`; 2) use thread-safe data structures like `CopyOnWriteArrayList` for read-heavy scenarios; or 3) follow functional state management with `MutableStateFlow` and immutable lists, updating state atomically via `_state.update { current -> current + newItem }`.

## Interview answer — deep senior

At the memory architecture level, standard Java collections like ArrayList do not use memory barriers or volatile writes for internal array elements. This means writes from thread A may remain cached in CPU L1/L2 caches and never become visible to thread B in a timely fashion, violating the happens-before relationship defined by the Java Memory Model (JMM).

In modern Android architecture, using traditional Java synchronization like `synchronized(lock)` or `Collections.synchronizedList()` is discouraged because it blocks operating system threads, which can cause ANR (Application Not Responding) if invoked on the main thread.

Instead, we adopt structured concurrency paradigms: 1. Confinement: confine state mutation to a single coroutine dispatcher, or use a dedicated Actor / single-threaded dispatcher (`Dispatchers.Default.limitedParallelism(1)`). 2. Non-blocking synchronization: use Kotlin Coroutines `Mutex`, ensuring suspending calls rather than thread-blocking locks. 3. Pure immutability: store only persistent immutable lists (`persistentListOf()`), replacing the reference atomically via compare-and-swap (CAS) loops inside `AtomicReference` or `StateFlow.update()`.

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
