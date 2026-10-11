---
id: "MEM-20"
question: "How can cache design and large lists trigger memory or performance regressions?"
topic: "Memory Management, ANR & Performance"
code: "MEM"
group: "B"
phase: 1
priority: "P1"
order: 75
editorial_status: "reviewed"
---

# MEM-20

## Original interview question

How can cache design and large lists trigger memory or performance regressions?

## What the interviewer evaluates

- Bound caches by bytes or an appropriate unit and include eviction/trim behavior.
- Explain duplicated large lists, eager transforms, image buffers, and UI rendering costs.
- Measure hit rate, memory baseline, frame time, and correctness together.

## Explanation in Arabic

الـcache تقلل network أو decode، لكن لو بتحتفظ بكل صفحة أو bitmap للأبد هتعمل retained memory عالي وربما OOM. `LruCache` بميزانية مناسبة ممكن تطرد القديم، لكن لازم تقيس بالـbytes للصور مش بعدد العناصر فقط؛ 100 صورة صغيرة غير 100 صورة 4K. القوائم الكبيرة كمان تكلف لو حملت كل البيانات مرة واحدة، وعملت `map/filter/sort` في كل recomposition، أو نسختها عدة مرات لكل layer. استخدم paging أو windowing حسب الحالة، stable IDs، وحسابات خارج مسار frame. لا تجعل cache هي المصدر الوحيد للحقيقة؛ راجع freshness وinvalidation وحالة offline.

## Why it matters and how it works

A cache retains data intentionally, so its footprint grows until a bound or eviction policy acts. An unbounded in-memory cache is behaviorally similar to a leak. Large collections may allocate copies during transformations and force expensive diff/layout work if every update replaces the whole list. Paging limits active data and UI composition, but remote/local source coordination must preserve ordering and freshness. Measure memory and frame behavior under realistic dataset sizes.

## Worked example

A marketplace loads 10,000 products into memory, maps each to UI models on every search keystroke, and caches every original image. Scrolling janks and memory rises. Move search/paging to a repository with bounded windows, request thumbnail-sized images through a bounded loader cache, and expose stable item IDs. Test query changes, offline return, and invalidation after a price update. This is a proposed redesign, not a measured repository issue.

## Trade-offs and decision criteria

More cache improves hit rate but increases memory and staleness. Paging reduces peak footprint but adds loading states and consistency logic. Precomputing UI models can save frame work but duplicates memory; use it where profiling justifies. Disk cache trades storage for network use. A fixed item-count eviction policy is misleading when item sizes vary widely.

## Failure modes

A cache key ignores account identity and exposes stale or cross-user data. An unlimited image cache OOMs low-memory devices. Eager `sortedBy` on Main blocks frames during typing. Replacing a whole list causes unnecessary row work even if one price changes. A paged dataset misses invalidation and shows stale order. Instrument memory, cache hit/evict, query latency, and rendering percentiles.

## Production perspective

Set memory budgets by device class where appropriate, define TTL or explicit invalidation for correctness, and respond to memory trim signals. Use production-sized test data and sustained scroll/search tests on constrained devices. Compare cache hit rate against process PSS, OOM rate, and slow frames in staged rollout; roll back a cache-size increase if user impact worsens.

## Interview answer — short

“Caches trade memory for speed, so they need a size bound and invalidation policy. Large lists can cause extra allocations and frame work through eager loading and repeated transforms; paging and measurement help.”

## Interview answer — structured

“I ask what the cache holds, how large each value can be, and how entries are evicted or invalidated. A count limit is insufficient for images with very different byte sizes. For lists, loading 10,000 rows and sorting them on every keystroke can raise memory and block Main; paging and moving transforms to the data layer may help. I keep stable IDs and avoid replacing unrelated UI state. I measure cache hit rate, retained/process memory, query latency, and slow frames together, because a faster average query is not a win if low-memory users start OOMing.”

## Interview answer — deep senior

“I treat a cache as an explicit memory allocation policy, not a free speed improvement. I identify the source of truth, freshness requirements, value-size distribution, and a byte budget with eviction. For account-specific data I include identity in keys and clear or partition on logout. In a large list I profile how many items are loaded, copied, sorted, and rendered for a typical interaction. Paging can limit active pages and UI work, but it introduces loading, invalidation, and offline-ordering concerns that I test. Image requests use target dimensions and a bounded library cache rather than full-resolution bitmaps. I compare sustained navigation and scroll on constrained devices, watching PSS, OOMs, allocation rate, frame tails, cache hit rate, and stale-data defects. If a cache increase improves hits but worsens crashes, I reduce it or choose disk/network trade-offs instead.”

## Deep-dive talking points

Discuss byte budgets, LRU/invalidation, account-key isolation, paging windows, repeated transforms, and multi-metric evaluation.

## Follow-up questions

- Why is an item-count limit weak for image caches? **Answer:** decoded image sizes vary greatly, so a byte-based budget better reflects memory pressure.
- Can an intentionally retained cache become a leak? **Answer:** yes in practical terms if it grows without a bound or useful ownership policy.
- What correctness risk does cache optimization add? **Answer:** stale or cross-account data if invalidation and keys are wrong.

## Self-check rubric

Set a cache budget and invalidation rule, identify a list hotspot, describe a paging trade-off, and choose memory and UX metrics.

## References and reviewed-on date

- [Cache bitmaps](https://developer.android.com/topic/performance/graphics/cache-bitmap) — bounded image caching.
- [Paging overview](https://developer.android.com/topic/libraries/architecture/paging/v3-overview) — large data windows.
- [Manage app memory](https://developer.android.com/topic/performance/memory/manage-app-memory) — memory pressure response.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. The marketplace redesign is illustrative.
