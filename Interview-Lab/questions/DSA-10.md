---
id: "DSA-10"
question: "How do you design and analyze an LRU cache?"
topic: "Data Structures, Algorithms & Big O"
code: "DSA"
group: "B"
phase: 5
priority: "P2"
order: 449
editorial_status: "reviewed"
---

# DSA-10

## Original interview question

How do you design and analyze an LRU cache?

## What the interviewer evaluates

- O(1) lookup and recency update using map plus ordered links.
- Capacity, expiry, concurrency and Android cache policy.

## Explanation in Arabic

LRU cache تطرد الأقل استخدامًا لما capacity تتملي. تصميم O(1) تقليدي: HashMap من key إلى node، وdoubly linked list ترتيب recency؛ `get` ينقل node للمقدمة، `put` يحدث أو يضيف، وعند overflow نشيل tail. في Android فيه `LruCache` لmemory cache، لكن لازم تحدد `sizeOf` إن الحجم بالbytes مهم، وتتعامل مع thread-safety/eviction.

## Practical walkthrough

LRU تحتاج map للlookup وorder للrecency، وكل hit ينقل العنصر إلى most recent؛ عند زيادة budget يخرج least recent. Android `LruCache` يغني عن pointer bugs، لكن `sizeOf` مهم للصور لأن 100 bitmap ليست حجمًا ثابتًا. cache قابلة للفقد بعد process death، فلا تخزن فيها payment status كمصدر وحيد. راقب hit rate وGC وmemory pressure.

## Why it matters and how it works

A map alone gives lookup but not least-recent ordering; a list alone gives ordering but linear lookup. Combined, node removal and move are constant time if each node has previous/next links. Android LruCache provides a library implementation with synchronized operations under its documented contract.

## Worked example

Image thumbnail cache keyed by URL/size: `get` refreshes recency, `put` evicts until size budget. Do not cache full-resolution bitmaps with “100 entries” if each varies wildly in bytes. `LruCache` can size by `Bitmap.byteCount` where applicable.

## Trade-offs and decision criteria

LRU is simple but can evict frequently accessed items under scan workloads; LFU/TTL may fit other patterns. More cache memory reduces I/O but increases OOM pressure. Disk cache has different durability and eviction needs.

## Failure modes

A custom cache forgets to unlink node before reinserting, creating a cycle/leak. Concurrent get/put without lock corrupts list. Cache is not source of truth: process death clears it.

## Production perspective

Profile hit rate, byte use, GC and OOMs; cap by device class and clear on memory pressure as appropriate. Keep repository/network as authoritative source.

## Interview answer — short

“An LRU cache combines a hash map for lookup with recency ordering for eviction, giving O(1) get/put under a fixed-capacity model. On Android I usually use LruCache and budget bytes, not just entries.”

## Interview answer — structured

“The map points to nodes in a doubly linked list. A hit moves its node to most-recent position; an insertion evicts from the least-recent tail when over capacity. That makes lookup and recency updates constant time, assuming hash lookup is expected constant. For Android images I use a size-aware LruCache, monitor memory and treat misses as normal after process death. I consider TTL or other policies if LRU thrashes. ”

## Interview answer — deep senior

“An LRU cache needs fast lookup and fast recency updates. A hash map points to entries in a doubly linked recency order; a hit moves its node to the recent end, and an insertion evicts the least recent when the capacity is exceeded. Expected lookup and node moves are constant time, assuming stable hashing. On Android I normally use `LruCache` instead of maintaining pointers myself. I size image entries by bytes, not just count, because one thumbnail and one full-resolution bitmap have very different memory cost. I define invalidation, concurrency, expiry and whether a miss can be reloaded; process death means the memory cache is disposable. The trade-off is better hit latency against heap pressure and GC. A scan-heavy workload can thrash LRU, so I measure hit rate and eviction frequency. I test replacement and eviction order, large-entry behavior and low-memory handling. I would never use an LRU cache as the sole ledger for payment status or other durable business state.”

## How to answer in the interview

- **Why:** cache improves repeated read latency.
- **How:** describe map plus recency and byte budget.
- **Trade-off:** hit rate versus memory pressure.
- **Failure case:** cache mistaken for durable ledger.
- **Production solution:** use LruCache and monitor eviction.

## Deep-dive talking points

Prompt for map+list mechanics, byte sizing, concurrency, process-death disposal.

## Follow-up questions

- [DSA-06](../dsa-06/): Is map lookup absolute O(1)? **Answer:** expected under hashing assumptions.
- [DSA-15](../dsa-15/): Can LRU store payment dedup truth? **Answer:** no; durable server identity is required.

## Self-check rubric

Specify hash map plus doubly linked recency list or a suitable ordered map, show get/put/eviction invariants, and state capacity, synchronization and stale-value policy.

## References and reviewed-on date

- [Android LruCache](https://developer.android.com/reference/android/util/LruCache) — API and sizing.
- [Kotlin collection overview](https://kotlinlang.org/docs/collections-overview.html) — map semantics.

Technically reviewed against the cited primary documentation on 2026-10-13; automated technical review only, not human review.
