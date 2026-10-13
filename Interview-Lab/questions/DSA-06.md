---
id: "DSA-06"
question: "What are average and worst-case HashMap lookup complexities?"
topic: "Data Structures, Algorithms & Big O"
code: "DSA"
group: "A"
phase: 5
priority: "P2"
order: 445
editorial_status: "reviewed"
---

# DSA-06

## Original interview question

What are average and worst-case HashMap lookup complexities?

## What the interviewer evaluates

- Expected versus pathological lookup cost.
- Hash quality, resizing and Android memory implications.

## Explanation in Arabic

`HashMap` lookup غالبًا expected O(1) مع hash distribution كويس وload factor مناسب. Worst case ممكن يوصل O(n) لو collisions كثيرة أو adversarial keys، مع اختلاف implementation الداخلية. Resize/rehash بيعمل spike حتى لو average/amortized جيد. استخدام map لكل عنصر في Compose list ممكن يوفر scan لكن يزود memory وallocations.

### Practical walkthrough in Egyptian Arabic

HashMap lookup عادة expected `O(1)` مع hash distribution مناسبة، لكن collisions/resizing/hostile keys تؤثر في worst case وlatency. Kotlin `Map` interface لا يضمن implementation بعينها. لا تخزن mutable object كمفتاح ثم تغير حقول equality/hashCode؛ lookup ممكن يفشل. في production قس عدد العناصر وحجم الذاكرة واستخدم stable immutable key مثل product ID.

## Why it matters and how it works

A hash code selects a bucket and equality distinguishes keys. Collision chains/probing and table growth determine actual cost; exact worst-case varies by JVM/Android implementation, so do not promise universal tree-bin behavior. Kotlin `HashMap` on JVM delegates to platform implementation.

## Worked example

Build `associateBy { it.id }` once for 10k products, then lookups are expected constant. Rebuilding that map inside every item rendering costs O(n) per row and becomes O(n²) overall. Keep the index at a stable data layer and update when source changes.

## Trade-offs and decision criteria

A map trades memory and build cost for repeated lookup speed. For a tiny list or one lookup, linear scan may be simpler/faster. Ordered maps have different complexity and guarantees.

## Failure modes

Mutable key fields change hash/equality after insertion, making lookup fail. Bad hashCode with all keys same causes collision hotspot. Use immutable stable keys and test realistic distributions.

## Production perspective

Profile lookup and allocations on low-end devices; do not place expensive reindexing inside recomposition. Bound cache size and handle concurrency at repository level.

## Interview answer — short

“HashMap lookup is expected O(1) under reasonable hashing, but collisions can degrade it and resizing adds spikes. I build indexes once when repeated lookups justify memory.”

## Interview answer — structured

“A hash map computes a hash to select a bucket and then compares keys. With good distribution, lookup is expected constant; pathological collisions can make it linear depending on implementation. Table growth has occasional rehash cost. For Android lists I avoid rebuilding a map per row, use immutable IDs, and measure whether one-time indexing beats a simple scan for the actual workload.”

## Interview answer — deep senior

“A hash map computes a hash to find a bucket and then uses equality to locate a key. With a reasonable distribution and managed load factor, lookup is expected constant time, but collisions, resizing and implementation details affect the worst case and latency. Kotlin’s `Map` is an interface, so I do not promise internals for every implementation. The most important correctness trap is using a mutable key whose fields participate in `equals` and `hashCode`; mutating it after insertion can make the entry unreachable by a logically matching lookup. In an Android repository I use immutable product or account IDs as keys and avoid storing unbounded user-controlled keys without a retention policy. If lookup is called for every visible list row, an index may be worth the extra memory; if the list is tiny, a scan may be simpler. I test collisions and key equivalence where custom keys exist, and profile allocation and memory at production size rather than claiming O(1) means free.”

## How to answer in the interview

- **Why:** hashing trades space for lookup speed.
- **How:** explain bucket/hash/equality and assumptions.
- **Trade-off:** expected speed versus collision and memory.
- **Failure case:** mutable key becomes unreachable.
- **Production solution:** use stable keys and profile hot path.

## Deep-dive talking points

Prompt for bucket/equality mechanics, index build cost, mutable key failure and implementation caveat.

## Follow-up questions

- [DSA-04](../dsa-04/): Does O(1) imply worst case? **Answer:** no, state expected/average assumption.
- [DSA-12](../dsa-12/): How does list mapping become O(n²)? **Answer:** rebuild/search map for every row.

## Self-check rubric

State expected O(1) lookup under good hashing and collision behavior, explain a pathological degradation, and describe how equality/hashCode bugs can break correctness before speed.

## References and reviewed-on date

- [Kotlin Map API](https://kotlinlang.org/api/core/kotlin-stdlib/kotlin.collections/-map/) — map contract.
- [Android performance](https://developer.android.com/topic/performance) — runtime profiling.

Technically reviewed against the cited primary documentation on 2026-10-13; automated technical review only, not human review.
