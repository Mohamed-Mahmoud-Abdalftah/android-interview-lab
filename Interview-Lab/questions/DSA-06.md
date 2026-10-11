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

“I separate per-operation lookup from total workflow cost. Building an index is O(n) time and memory, then repeated queries are expected O(1); if I rebuild it during every recomposition, I may regress to quadratic work. Worst-case behavior depends on collision handling, which I do not assume identical across Java/Android versions. I test stable key hash/equality contracts, avoid mutable keys, and watch allocations and GC on constrained devices. If ordering or range queries matter, another structure may fit better.”

## Deep-dive talking points

Prompt for bucket/equality mechanics, index build cost, mutable key failure and implementation caveat.

## Follow-up questions

- [DSA-04](../dsa-04/): Does O(1) imply worst case? **Answer:** no, state expected/average assumption.
- [DSA-12](../dsa-12/): How does list mapping become O(n²)? **Answer:** rebuild/search map for every row.

## Self-check rubric

Can you derive the bound, explain the Android example, identify a data or memory trade-off, and answer both follow-ups?

## References and reviewed-on date

- [Kotlin Map API](https://kotlinlang.org/api/core/kotlin-stdlib/kotlin.collections/-map/) — map contract.
- [Android performance](https://developer.android.com/topic/performance) — runtime profiling.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
