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

“The map points to nodes in a doubly linked list. A hit moves its node to most-recent position; an insertion evicts from the least-recent tail when over capacity. That makes lookup and recency updates constant time, assuming hash lookup is expected constant. For Android images I use a size-aware LruCache, monitor memory and treat misses as normal after process death. I consider TTL or other policies if LRU thrashes. The mechanics matter. A map alone gives lookup but not least-recent ordering; a list alone gives ordering but linear lookup. Combined, node removal and move are constant time if each node has previous/next links. Android LruCache provides a library implementation with synchronized operations under its documented contract.”

## Interview answer — deep senior

“I define cache semantics first: byte capacity, key equivalence, expiry, invalidation and concurrency. A map plus linked order supports O(1) average lookup and O(1) node moves; Android’s LruCache avoids hand-written pointer bugs for common cases. I would test overwrite, eviction order, large-item rejection and concurrent access according to the chosen implementation. Cache data is disposable, so a payment status cannot live only there. I measure hit rate against memory/GC costs and respond to low-memory signals. Consider a concrete case. Image thumbnail cache keyed by URL/size: `get` refreshes recency, `put` evicts until size budget. Do not cache full-resolution bitmaps with “100 entries” if each varies wildly in bytes. `LruCache` can size by `Bitmap.byteCount` where applicable. A failure case illustrates the risk. A custom cache forgets to unlink node before reinserting, creating a cycle/leak. Concurrent get/put without lock corrupts list. Cache is not source of truth: process death clears it. In production, the response is concrete. Profile hit rate, byte use, GC and OOMs; cap by device class and clear on memory pressure as appropriate. Keep repository/network as authoritative source. The decision has a trade-off. LRU is simple but can evict frequently accessed items under scan workloads; LFU/TTL may fit other patterns. More cache memory reduces I/O but increases OOM pressure. Disk cache has different durability and eviction needs.”

## Deep-dive talking points

Prompt for map+list mechanics, byte sizing, concurrency, process-death disposal.

## Follow-up questions

- [DSA-06](../dsa-06/): Is map lookup absolute O(1)? **Answer:** expected under hashing assumptions.
- [DSA-15](../dsa-15/): Can LRU store payment dedup truth? **Answer:** no; durable server identity is required.

## Self-check rubric

Can you derive the bound, explain the Android example, identify a trade-off/failure, and answer both follow-ups?

## References and reviewed-on date

- [Android LruCache](https://developer.android.com/reference/android/util/LruCache) — API and sizing.
- [Kotlin collection overview](https://kotlinlang.org/docs/collections-overview.html) — map semantics.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
