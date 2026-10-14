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

تصميم الـ Cache والتعامل مع القوائم الضخمة (Large Lists) وكيف يمكن أن يتسببا في تدهور الذاكرة والأداء:

1. مخاطر الـ Unbounded Caching (الكاش غير المحدود):
   - أكبر خطأ شائع هو استخدام `HashMap<Key, Value>` عادي كـ In-Memory Cache.
   - الـ HashMap العادي لا يملك آلية طرد (Eviction Policy) ولا يعرف سقفاً للذاكرة؛ كل عنصر يدخل يظل محجوزاً في الـ Heap حتى يمتلئ مسبباً `OutOfMemoryError`.
   - الحل السليم هو استخدام `LruCache` (Least Recently Used Cache) المدمج في Android Jetpack، مع تحديد حجمه بوحدات البايت (وليس عدد العناصر فقط) كنسبة محددة من الـ Heap المتاح (مثلاً 1/8 من الذاكرة).

2. مشاكل الذاكرة في القوائم الضخمة (Large Lists):
   - محاولة جلب آلاف العناصر وتخزينها في `List<Entity>` داخل الذاكرة دفعة واحدة تبتلع مساحة ضخمة من الـ RAM وتجمد الـ UI أثناء التحويل والـ Parsing.
   - في `RecyclerView`، عدم ثبات الـ ViewHolders أو عمل عمليات حجز مكلفة داخل `onBindViewHolder` يسبب سقوط فريمات (Jank).

3. الحلول المعمارية القياسية:
   - **Paging 3 Library**: تحميل البيانات على دفعات صغيرة مجزأة (Chunks) بالطلب بالتوازي مع سكرول المستخدم، مع التخلص التلقائي من الصفحات البعيدة عن نطاق الرؤية.
   - **DiffUtil / ListAdapter**: حساب الفروقات بدقة في Background Thread دون إعادة رسم القائمة كاملة.
   - الاستجابة لنداء النظام `onTrimMemory(level)`: تفريغ الكاش فوراً عند استلام `TRIM_MEMORY_RUNNING_CRITICAL`.

## Practical walkthrough

تصميم LruCache محكوم بالذاكرة مع الاستجابة لـ onTrimMemory:
```kotlin
class MemoryBoundedImageCache(maxMemoryInBytes: Int) : ComponentCallbacks2 {
    private val cache = object : LruCache<String, Bitmap>(maxMemoryInBytes) {
        override fun sizeOf(key: String, value: Bitmap): Int {
            // قياس الحجم الفعلي للـ Bitmap بالبايت وليس بعدد العناصر:
            return value.allocationByteCount
        }
    }

    fun get(key: String): Bitmap? = cache.get(key)
    fun put(key: String, bitmap: Bitmap) { cache.put(key, bitmap) }

    override fun onTrimMemory(level: Int) {
        if (level >= ComponentCallbacks2.TRIM_MEMORY_RUNNING_LOW) {
            // تفريغ الكاش عندما يتعرض الجهاز لضغط ذاكرة لتجنب القتل بواسطة LMK:
            cache.evictAll()
        }
    }

    override fun onConfigurationChanged(newConfig: Configuration) {}
    override fun onLowMemory() { cache.evictAll() }
}
```

## Why it matters and how it works

A cache retains data intentionally, so its footprint grows until a bound or eviction policy acts. An unbounded in-memory cache is behaviorally similar to a leak. Large collections may allocate copies during transformations and force expensive diff/layout work if every update replaces the whole list. Paging limits active data and UI composition, but remote/local source coordination must preserve ordering and freshness. Measure memory and frame behavior under realistic dataset sizes.

## Worked example

A marketplace loads 10,000 products into memory, maps each to UI models on every search keystroke, and caches every original image. Scrolling janks and memory rises. Move search/paging to a repository with bounded windows, request thumbnail-sized images through a bounded loader cache, and expose stable item IDs. Test query changes, offline return, and invalidation after a price update. This is a proposed redesign, not a measured repository issue.

This Android sketch bounds a bitmap cache by approximate decoded kilobytes rather than item count. It assumes the app owns invalidation and account separation; it is illustrative, not benchmarked here.

```kotlin
import android.graphics.Bitmap
import android.util.LruCache

val thumbnails = object : LruCache<String, Bitmap>(16 * 1024) {
    override fun sizeOf(key: String, value: Bitmap): Int =
        maxOf(1, value.byteCount / 1024)
}
```

The 16 MiB example is a policy input to tune for device class and the rest of the app's footprint.

## Trade-offs and decision criteria

More cache improves hit rate but increases memory and staleness. Paging reduces peak footprint but adds loading states and consistency logic. Precomputing UI models can save frame work but duplicates memory; use it where profiling justifies. Disk cache trades storage for network use. A fixed item-count eviction policy is misleading when item sizes vary widely.

## Failure modes

A cache key ignores account identity and exposes stale or cross-user data. An unlimited image cache OOMs low-memory devices. Eager `sortedBy` on Main blocks frames during typing. Replacing a whole list causes unnecessary row work even if one price changes. A paged dataset misses invalidation and shows stale order. Instrument memory, cache hit/evict, query latency, and rendering percentiles.

## Production perspective

Set memory budgets by device class where appropriate, define TTL or explicit invalidation for correctness, and respond to memory trim signals. Use production-sized test data and sustained scroll/search tests on constrained devices. Compare cache hit rate against process PSS, OOM rate, and slow frames in staged rollout; roll back a cache-size increase if user impact worsens.

## Interview answer — short

Unbounded caches like raw `HashMap` grow indefinitely and trigger OOMs, while loading unpaginated lists consumes excessive RAM and stalls the UI. In production, we enforce memory bounds using `LruCache` sized as a fraction of available heap, implement Paging 3 to stream data incrementally, and clear cached assets in `onTrimMemory()`.

## Interview answer — structured

Cache misconfigurations and unpaginated lists are two of the most frequent sources of memory leaks and UI thrashing in enterprise applications.

A standard `HashMap` retains every inserted object with strong references, providing no eviction strategy or size limits. As users browse, memory consumption climbs monotonically until an `OutOfMemoryError` occurs. To prevent this, production in-memory caches must use `LruCache`, measuring entries by **byte size** (`sizeOf()`) rather than object counts, and budgeting cache size dynamically based on `Runtime.getRuntime().maxMemory()` (typically 10-15% of available heap).

For large lists, fetching thousands of database records into an in-memory `List<T>` strains both the heap and JSON deserializer. Instead, we adopt **Jetpack Paging 3**, which loads small pages (e.g. 20-30 items) into the UI reacting to scroll position, while automatically purging distant off-screen pages.

Additionally, apps must implement `ComponentCallbacks2` and listen to `onTrimMemory(level)`. Purging secondary caches when `TRIM_MEMORY_RUNNING_LOW` arrives prevents the kernel Low Memory Killer (LMK) from terminating the app.


## Interview answer — deep senior

Under the hood, `LruCache` uses a `LinkedHashMap` configured with access-order ordering (`accessOrder = true`). Whenever `get()` or `put()` is invoked, the accessed node moves to the tail; when the byte sum exceeds `maxSize`, elements are trimmed from the head.

In `RecyclerView`, memory regressions frequently occur when developers misuse `DiffUtil` or `setHasFixedSize`. If `DiffUtil.calculateDiff()` runs on the main thread for lists exceeding a few hundred items, it blocks the main looper for 50-200ms, creating severe UI jank. Using `AsyncListDiffer` or `ListAdapter` automatically dispatches diff computation to a background executor.

In Compose, `LazyColumn` handles view recycling virtually, but keeping heavy state closures inside items can retain significant memory. Using `key` parameters on `items()` ensures that Compose preserves item identity correctly without re-allocating state instances during reordering.


## How to answer in the interview

- **Why:** Tie cache policy to byte budget and data freshness.
- **How:** Use paging and measure copying, hits, and frame tails.
- **Trade-off:** Tighter eviction saves memory but increases fetch latency.
- **Failure case:** Count-only image limits and cross-account keys fail.
- **Production solution:** Set size-aware eviction and account-aware invalidation.

## Deep-dive talking points

Discuss byte budgets, LRU/invalidation, account-key isolation, paging windows, repeated transforms, and multi-metric evaluation.

## Follow-up questions

- **Interviewer:** "What happens if you use `WeakHashMap` as an in-memory cache?"
  **Answer:** "`WeakHashMap` keys are held weakly, but the values are held with strong references. If values reference keys, the entries will never be collected. Furthermore, garbage collection sweeps can purge entries aggressively between frames, resulting in near-zero cache hit rates."

- **Interviewer:** "How does `onTrimMemory(TRIM_MEMORY_UI_HIDDEN)` differ from other trim levels?"
  **Answer:** "`TRIM_MEMORY_UI_HIDDEN` is dispatched when your app's UI moves entirely to the background (e.g. user pressed Home). This is the prime opportunity to release heavy UI resources and bitmaps before the system places the process into the cached LRU tier."

## Self-check rubric

Set a cache budget and invalidation rule, identify a list hotspot, describe a paging trade-off, and choose memory and UX metrics.

## References and reviewed-on date

- [Cache bitmaps](https://developer.android.com/topic/performance/graphics/cache-bitmap) — bounded image caching.
- [Paging overview](https://developer.android.com/topic/libraries/architecture/paging/v3-overview) — large data windows.
- [Manage app memory](https://developer.android.com/topic/performance/memory/manage-app-memory) — memory pressure response.

Technically reviewed against primary documentation on 2026-10-13.
