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

“I compare costs for the operation the feature actually performs. An array-backed list gives constant indexed access but middle insert shifts elements. A linked list can relink in constant time only after locating the node. A stack serves LIFO, a queue FIFO, and hash maps/sets provide expected constant lookup with memory and collision caveats. On Android, allocations, locality, concurrency and persistence may outweigh textbook complexity. The mechanics matter. Data structure choice depends on operations: lookup, ordered traversal, insertion, deletion and bounded memory. Stack/queue are access disciplines that can be implemented on arrays/deques or linked nodes. Complexity statements assume a particular implementation and resizing/collision behavior. The choice has a trade-off. Array-backed structures have good locality but shifting cost; hash tables trade memory/order for expected lookup speed. Linked nodes avoid shifting but add allocation and cache misses. Thread-safety is separate from data structure choice.”

## Interview answer — deep senior

“For a product feed I usually keep an array-backed immutable snapshot because iteration and indexed access dominate; for ID joins I build a map once rather than scan per row. For a retry queue I may use FIFO discipline in memory for execution, but the source of truth is a durable database, not an ArrayDeque. I account for amortized resize, hash collision, object overhead and thread confinement. A LinkedList’s O(1) insertion claim is irrelevant if each insertion first performs O(n) search. Consider a concrete case. Back navigation uses a stack; pending local tasks use FIFO queue; product lookup by ID uses HashMap; dedup IDs use HashSet; visible immutable product list uses array-backed list. Do not choose LinkedList just because frequent insertion is mentioned if finding position dominates. A failure case illustrates the risk. Using a mutable HashMap from two coroutines without synchronization causes race; expected O(1) says nothing about concurrency. A queue in memory loses work after process death; durable outbox is needed for payments. In production, the response is concrete. For Android choose structures from actual access pattern, profile allocation/jank and persist financial obligations. Use collection APIs whose semantics are clear and test ordering.”

## Deep-dive talking points

Prompt for operation matrix, locating linked node, hash caveat, durable queue versus memory.

## Follow-up questions

- [DSA-08](../dsa-08/): Which structure detects duplicates? **Answer:** HashSet with expected O(n) scan.
- [DSA-10](../dsa-10/): Which combination builds LRU? **Answer:** map plus recency order structure.

## Self-check rubric

Can you derive the bound, explain the Android example, identify a data or memory trade-off, and answer both follow-ups?

## References and reviewed-on date

- [Kotlin collections overview](https://kotlinlang.org/docs/collections-overview.html) — standard collections.
- [Kotlin ArrayDeque API](https://kotlinlang.org/api/core/kotlin-stdlib/kotlin.collections/-array-deque/) — deque semantics.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
