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

Array/`ArrayList` random access سريع O(1) ونقل عناصر عند insert في النص O(n). Linked list insert قرب node O(1) لكن الوصول لمكانها O(n) وmemory/cache أسوأ غالبًا. Stack LIFO، queue FIFO؛ استخدم `ArrayDeque` مناسب في Kotlin. HashMap key→value وHashSet membership متوقع O(1) لكن memory إضافية وhash quality مهمة.

### Practical walkthrough in Egyptian Arabic

اختيار structure حسب operations: array/list لفهرسة وتصفح، linked list لinsert/delete مع node معلوم، stack للرجوع، queue للشغل بالترتيب، map للlookup بمفتاح، set للmembership. في Kotlin `List` interface لا يضمن random access لكل implementation. لو عندك product feed، غالبًا `ArrayList` للعرض وmap جانبية للـID أفضل من البحث الخطي لكل row.

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

“Arrays/lists favor indexed access; linked lists favor local link edits; stacks are LIFO, queues FIFO; hash maps/sets favor expected fast keyed lookup or membership. I choose by operations and memory.”

## Interview answer — structured

“I compare costs for the operation the feature actually performs. An array-backed list gives constant indexed access but middle insert shifts elements. A linked list can relink in constant time only after locating the node. A stack serves LIFO, a queue FIFO, and hash maps/sets provide expected constant lookup with memory and collision caveats. On Android, allocations, locality, concurrency and persistence may outweigh textbook complexity.”

## Interview answer — deep senior

“I choose a data structure from the operations the feature performs. An array-backed list supports efficient indexed reads and iteration but insertion in the middle shifts elements. A linked list can splice a known node cheaply yet finding that node and indexing are expensive and each node costs memory. A stack gives last-in-first-out behavior for undo, a queue gives first-in-first-out behavior for pending work, a hash map maps IDs to values with expected fast lookup, and a set represents membership or uniqueness. I do not assume Kotlin’s `List` interface implies one physical structure or O(1) indexed access. For a product feed, I might keep a list for display order and a map for lookup by stable ID, accepting extra memory to avoid repeated per-row scans. For financial operations, an in-memory set is not durable deduplication. I state time and space costs for the actual operations, define mutation and concurrency ownership, then test edge cases and measure on target devices.”

## How to answer in the interview

- **Why:** operations determine structure.
- **How:** compare lookup, insert, order and memory.
- **Trade-off:** index speed versus update cost.
- **Failure case:** assuming every List index is constant.
- **Production solution:** pick collection from access pattern.

## Deep-dive talking points

Prompt for operation matrix, locating linked node, hash caveat, durable queue versus memory.

## Follow-up questions

- [DSA-08](../dsa-08/): Which structure detects duplicates? **Answer:** HashSet with expected O(n) scan.
- [DSA-10](../dsa-10/): Which combination builds LRU? **Answer:** map plus recency order structure.

## Self-check rubric

Choose array, linked list, stack, queue, map or set for one Android data-flow need; compare lookup/insertion order, locality and memory cost rather than memorizing only Big O.

## References and reviewed-on date

- [Kotlin collections overview](https://kotlinlang.org/docs/collections-overview.html) — standard collections.
- [Kotlin ArrayDeque API](https://kotlinlang.org/api/core/kotlin-stdlib/kotlin.collections/-array-deque/) — deque semantics.

Technically reviewed against the cited primary documentation on 2026-10-13; automated technical review only, not human review.
