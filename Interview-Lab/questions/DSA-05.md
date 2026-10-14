---
id: "DSA-05"
question: "Compare arrays, linked lists, stacks, queues, hash maps, and sets."
topic: "Data Structures, Algorithms & Big O"
code: "DSA"
group: "A"
phase: 5
priority: "P2"
order: 444
editorial_status: "reviewed"
---

# DSA-05

## Original interview question

Compare arrays, linked lists, stacks, queues, hash maps, and sets.

## What the interviewer evaluates

- Operation-specific costs of six structures.
- Android/Kotlin library implementation and memory caveats.

## Explanation in Arabic

قارن بين هياكل البيانات الأساسية: Arrays، Linked Lists، Stacks، Queues، HashMaps، و Sets من حيث الأداء وحالات الاستخدام في أندرويد؟

1. مقارنة شاملة للتعقيد (Time & Space Complexity):
   - **Array / ArrayList**:
     * Access by Index: $O(1)$
     * Insert/Delete at end: $O(1)$ amortized
     * Insert/Delete in middle: $O(n)$ (يتطلب إزاحة العناصر)
     * الذاكرة: ممتازة جداً (Contiguous Memory) وموفرة ومثالية للـ CPU Cache.
   - **LinkedList**:
     * Access by Index: $O(n)$ (يجب المرور من البداية عقدة بعقدة)
     * Insert/Delete at head/tail: $O(1)$
     * الذاكرة: سيئة في أندرويد؛ كل عنصر يخصص كائن `Node` إضافي مع مؤشرين، مما يسبب تجزئة الذاكرة وضعف الكاش.
   - **Stack (LIFO - Last In First Out)**:
     * Push/Pop: $O(1)$
     * استخدام أندرويد: إدارة شاشات التنقل (BackStack) وإلغاء العمليات (Undo buffer).
   - **Queue (FIFO - First In First Out)**:
     * Enqueue/Dequeue: $O(1)$
     * استخدام أندرويد: معالجة الرسائل والمهام في الـ `Looper` و `MessageQueue` وجدولة WorkManager.
   - **HashMap / HashSet**:
     * Search/Insert/Delete: $O(1)$ average ($O(n)$ worst-case)
     * الذاكرة: تستهلك حجماً إضافياً للـ Buckets وعقد الـ Entry.

## Practical walkthrough

جدول مقارنة الأداء ومثال عملي لاختيار الهيكل الأنسب في أندرويد:
```kotlin
// جدول التعقيد السريع:
// Structure   | Read by Key/Index | Insert Head | Insert Tail | Memory Efficiency
// Array       | O(1)              | O(n)        | O(1)        | High (Contiguous)
// LinkedList  | O(n)              | O(1)        | O(1)        | Low (Node objects)
// HashMap     | O(1) (Key)        | O(1)        | O(1)        | Medium (Buckets)
// HashSet     | O(1) (Contains)   | O(1)        | O(1)        | Medium

// مثال: استخدام ArrayDeque بدلاً من Stack أو LinkedList (أسرع وأوفر في الذاكرة):
val navigationStack = ArrayDeque<String>()
navigationStack.addLast("home_screen") // Push O(1)
navigationStack.addLast("profile_screen")
val currentScreen = navigationStack.removeLast() // Pop O(1)
```

## Why it matters and how it works

Data structure choice depends on operations: lookup, ordered traversal, insertion, deletion and bounded memory. Stack/queue are access disciplines that can be implemented on arrays/deques or linked nodes. Complexity statements assume a particular implementation and resizing/collision behavior.

## Worked example

Back navigation uses a stack; pending local tasks use FIFO queue; product lookup by ID uses HashMap; dedup IDs use HashSet; visible immutable product list uses array-backed list. Do not choose LinkedList just because frequent insertion is mentioned if finding position dominates.

## Trade-offs and decision criteria

Array-backed structures have good locality but shifting cost; hash tables trade memory/order for expected lookup speed. Linked nodes avoid shifting but add allocation and cache misses. Thread-safety is separate from data structure choice.

## Failure modes

Using a mutable HashMap from two coroutines without synchronization causes race; expected O(1) says nothing about concurrency. A queue in memory loses work after process death; durable outbox is needed for payments.

## Production perspective

For Android choose structures from actual access pattern, profile allocation/jank and persist financial obligations. Use collection APIs whose semantics are clear and test ordering.

## Interview answer — short

Arrays offer O(1) indexed access with optimal cache locality but O(n) middle insertions. LinkedLists provide O(1) head/tail insertions but O(n) search and poor memory overhead. Stacks (LIFO) and Queues (FIFO) provide O(1) push/pop. HashMaps and Sets provide average O(1) lookups via hashing at the cost of higher memory overhead.

## Interview answer — structured

Selecting the correct data structure balances computational time complexity against memory and cache efficiency.

First, **Arrays and ArrayLists**. Next, constant $O(1)$ random access by index. Insertion at end is amortized $O(1)$, while arbitrary insertions require $O(n)$ element shifting. Stored contiguously in memory, yielding optimal CPU cache locality and zero node overhead.
**LinkedLists**. Constant $O(1)$ insertion and deletion given a node reference, but $O(n)$ indexed access. In Android, `LinkedList` is generally discouraged because each entry allocates a separate `Node` object, causing memory bloat, GC churn, and cache misses.
**Stacks and Queues**. Stack enforces LIFO; Queue enforces FIFO. Both operate with $O(1)$ enqueue/dequeue operations. In modern Kotlin/Android, `ArrayDeque` is the preferred implementation for both, outperforming legacy `java.util.Stack` and `LinkedList`.
**HashMaps and Sets**. Finally, provide average-case $O(1)$ search, insertion, and deletion via hash tables. They trade increased memory overhead (bucket arrays, load factors, collision nodes) for fast key-based retrieval.


## Interview answer — deep senior

From an Android internals and memory allocation perspective, standard Java collections present hidden traps.

First, a The Vector / Stack Synchronization Penalty is the legacy `java. Util.Stack` inherits from `Vector`, meaning every single push and pop synchronizes on a monitor lock. In single-threaded Android UI backstack operations, this introduces pointless synchronization overhead. Always prefer `ArrayDeque`. Next, with Android Primitive Sparse Collections, storing a mapping of `Int` to `User` in `HashMap<Int, User>` requires boxing every primitive key into a `java.lang.Integer` object, allocating 16 to 24 bytes per key on the heap. Android's native `SparseArray<User>` uses two parallel arrays (`int[]` and `Object[]`) with binary search lookup ($O(\log n)$), eliminating all autoboxing and significantly slashing GC pressure.
Finally, with Circular ArrayDeque Performance, `ArrayDeque` uses a circular array buffer that automatically resizes without shifting elements on remove. It serves as both stack and queue with virtually zero garbage creation compared to linked implementations.


## How to answer in the interview

- **Why:** operations determine structure.
- **How:** compare lookup, insert, order and memory.
- **Trade-off:** index speed versus update cost.
- **Failure case:** assuming every List index is constant.
- **Production solution:** pick collection from access pattern.

## Deep-dive talking points

Prompt for operation matrix, locating linked node, hash caveat, durable queue versus memory.

## Follow-up questions

- **Interviewer:** "Why is `ArrayDeque` preferred over `LinkedList` for queue and stack implementations in Android?"
  **Answer:** "Because `ArrayDeque` uses a contiguous resizable circular array, avoiding the per-element `Node` object allocations and cache misses of `LinkedList`."

- **Interviewer:** "What memory optimization does Android's `SparseArray` provide over `HashMap<Int, V>`?"
  **Answer:** "It avoids autoboxing primitive integer keys into `Integer` wrapper objects, storing keys in a raw `int[]` to reduce memory and GC overhead."

## Self-check rubric

Choose array, linked list, stack, queue, map or set for one Android data-flow need; compare lookup/insertion order, locality and memory cost rather than memorizing only Big O.

## References and reviewed-on date

- [Kotlin collections overview](https://kotlinlang.org/docs/collections-overview.html) — standard collections.
- [Kotlin ArrayDeque API](https://kotlinlang.org/api/core/kotlin-stdlib/kotlin.collections/-array-deque/) — deque semantics.

Technically reviewed against primary documentation on 2026-10-13.
