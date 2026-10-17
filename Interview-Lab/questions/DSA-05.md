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

## Concept and technical explanation

Selecting optimal collection data structures dictates memory locality, algorithmic complexity, and cache ergonomics in Android:
- Array & Dynamic Array (`Array`, `ArrayList`):
  - Memory: Contiguous memory allocation.
  - Access: $O(1)$ random access by index via direct pointer arithmetic.
  - Insertion/Deletion: $O(1)$ amortized at the end; $O(n)$ at arbitrary positions due to element shifting.
  - Cache Ergonomics: Exceptional CPU L1/L2 cache locality; sequential elements are pre-fetched into hardware cache lines.
- Linked List (`LinkedList`):
  - Memory: Doubly-linked nodes scattered across the heap with pointer references.
  - Access: $O(n)$ sequential traversal.
  - Insertion/Deletion: $O(1)$ once a node reference is held; $O(n)$ if traversal is required.
  - Android Reality: `LinkedList` is almost universally an anti-pattern on Android. Each node incurs a 24-to-32-byte object header overhead, inducing memory fragmentation and cache misses. Prefer `ArrayDeque` or `ArrayList`.
- Stacks & Queues (`ArrayDeque`):
  - Memory: Resizable circular array buffer.
  - Operations: $O(1)$ amortized push/pop for stacks (LIFO), and $O(1)$ enqueue/dequeue for queues (FIFO).
  - Android Reality: Far superior to `java.util.Stack` (which carries obsolete synchronized lock overhead) and `LinkedList` queues. Used internally for Activity backstacks, navigation stacks, and background job queues.
- Hash Map (`HashMap`):
  - Memory: Array of buckets containing linked lists or balanced Red-Black trees.
  - Operations: $O(1)$ average get/put; $O(n)$ or $O(\log n)$ worst-case under pathological collisions.
  - Android Memory Considerations: High memory overhead per entry. For small collections ($n < 1,000$), Android provides `ArrayMap` and primitive-specialized `SparseArray` to eliminate node and autoboxing memory waste.
- Set (`HashSet`, `LinkedHashSet`):
  - Memory: Backed by a `HashMap` where values are dummy object references.
  - Operations: $O(1)$ average add, remove, and contains; guarantees element uniqueness.
  - `LinkedHashSet` preserves insertion order using a doubly-linked bucket structure with slight extra memory cost.

## Practical walkthrough (English)

Idiomatic Kotlin collection usage and Android memory-optimized alternatives:
```kotlin
// 1. Array / ArrayList: Optimal for fast indexed reads and sequential UI lists
val userList = ArrayList<String>() // Backed by contiguous array

// 2. ArrayDeque: Optimal stack (LIFO) and queue (FIFO) implementation
val navigationStack = ArrayDeque<String>()
navigationStack.push("HomeScreen")
navigationStack.push("DetailsScreen")
val currentScreen = navigationStack.pop() // O(1) without LinkedList node overhead

// 3. Set: Unique element tracking with O(1) membership checks
val selectedIds = HashSet<String>()
selectedIds.add("item_101")
val isSelected = selectedIds.contains("item_101") // O(1)

// 4. Android SparseArray: Avoids Integer autoboxing and Entry node overhead
// Replaces HashMap<Int, User> with contiguous primitive arrays
import android.util.SparseArray
val userCache = SparseArray<User>()
userCache.put(101, User("Mohamed"))
val user = userCache.get(101) // O(log n) via binary search, but 60% less RAM!
```

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

Arrays provide O(1) index access with excellent CPU cache locality, while LinkedLists suffer from pointer overhead and cache misses, making them an Android anti-pattern. Stacks and Queues are best implemented via ArrayDeque for O(1) operations without node allocation. HashMaps and Sets deliver O(1) average key lookups at the expense of memory, which Android optimizes using SparseArray and ArrayMap.

## Interview answer — structured

Choosing the appropriate data structure requires balancing access complexity against memory allocation and hardware cache locality.
Arrays and ArrayLists store data contiguously, providing constant-time O(1) random access and superior CPU cache prefetching, though insertions at arbitrary indices require O(n) element shifts. In contrast, LinkedLists scatter nodes across memory; while insertions are O(1) when holding a reference, random access requires O(n) traversal. On Android, LinkedList is generally an anti-pattern due to excessive pointer overhead and poor cache locality.
For LIFO stacks and FIFO queues, ArrayDeque is the gold standard, offering amortized O(1) operations over a circular array buffer without object node overhead.
HashMaps and HashSets provide constant-time O(1) average lookups and additions by hashing keys into buckets. However, because standard HashMaps allocate multiple wrapper objects and Entry nodes, Android platforms provide memory-efficient alternatives like SparseArray and ArrayMap for smaller datasets, avoiding autoboxing and dramatically reducing garbage collection churn.

## Interview answer — deep senior

From a systems hardware and mobile memory architecture perspective, evaluating collections requires looking beneath asymptotic Big O into physical memory layout, CPU cache hierarchies, and garbage collection pressure.
While classical computer science teaches that LinkedList provides O(1) insertions compared to ArrayList's O(n) shifts, in real-world Android runtimes, ArrayList almost always outperforms LinkedList. Modern mobile ARM processors rely heavily on L1 and L2 cache lines. When iterating an ArrayList, contiguous memory addresses are prefetched into cache lines in single hardware cycles. With LinkedList, each node is an independent heap allocation containing sixteen bytes of object header and two eight-byte pointers. Traversing a LinkedList involves chasing memory pointers across a fragmented heap, triggering relentless CPU cache misses and creating thousands of objects that burden the ART garbage collector.
For stack and queue semantics, ArrayDeque is our architectural standard. It avoids the obsolete synchronization locks of legacy Vector-based Stack classes and eliminates the node allocation penalties of LinkedList, implementing circular array wrapping with amortized O(1) bounds.
HashMaps provide unmatched O(1) associative lookups, but their memory tax on mobile is severe. A standard HashMap allocates bucket arrays and Entry nodes, while boxing primitive integers into reference objects. In high-frequency UI scrolling lists, this allocation churn causes frame stutter. Android engineers resolve this by deploying Google's specialized collections: SparseArray stores integer keys in a sorted primitive array and values in an Object array, utilizing binary search O of log n lookups while slashing memory consumption by over fifty percent and completely eliminating autoboxing. Selecting the correct structure is thus a hardware-conscious engineering decision.

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
