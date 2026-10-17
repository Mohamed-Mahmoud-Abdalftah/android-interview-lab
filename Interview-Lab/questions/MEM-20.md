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

## Concept and technical explanation

Memory caches and large scrollable lists are the two most common architectural sites of memory bloat, allocation churn, and performance regressions in Android applications. An unconstrained in-memory cache—such as a static HashMap, an unbounded LRU cache, or a cache retaining heavy objects like decoded Bitmaps or database entities—grows monotonically over time. Without strict byte-bounded ceilings and eviction policies, the cache exhausts available heap space, provoking frequent Concurrent Copying GC pauses and ultimately forcing Low Memory Killer (LMK) terminations. In large lists (rendered via RecyclerView or Jetpack Compose LazyColumn), performance regressions occur when item views or composables violate recycling contracts. Allocating heavy temporary objects (such as DateFormatters, JSON parsers, lambda instances, or raw bitmap decodes) inside `onBindViewHolder` or within composable item bodies causes allocation spikes with every fling gesture. Furthermore, if list items retain references to outer scopes, Activity contexts, or Coroutine jobs that outlive the visible window, off-screen items cannot be reclaimed. Sustainable memory architectures enforce bounded LRU caches that measure size in bytes (e.g. `Bitmap.allocationByteCount`) rather than item counts, register with `ComponentCallbacks2` to evict entries during system memory pressure events (`onTrimMemory`), and employ Jetpack Paging 3 to window large datasets into memory-bounded pages.

## Practical walkthrough (English)

Building a memory-bounded cache that honors system memory pressure:
```kotlin
class MemoryBoundedImageCache(maxMemoryInBytes: Int) : ComponentCallbacks2 {
    private val cache = object : LruCache<String, Bitmap>(maxMemoryInBytes) {
        override fun sizeOf(key: String, value: Bitmap): Int {
            // Measure exact memory footprint in bytes rather than item count:
            return value.allocationByteCount
        }
    }

    fun get(key: String): Bitmap? = cache.get(key)
    fun put(key: String, bitmap: Bitmap) { cache.put(key, bitmap) }

    override fun onTrimMemory(level: Int) {
        if (level >= ComponentCallbacks2.TRIM_MEMORY_RUNNING_LOW) {
            // Evict all cached bitmaps when the device experiences severe memory pressure:
            cache.evictAll()
        } else if (level >= ComponentCallbacks2.TRIM_MEMORY_BACKGROUND) {
            // Evict half the cache when the app is backgrounded to avoid LMK termination:
            cache.trimToSize(cache.maxSize() / 2)
        }
    }

    override fun onConfigurationChanged(newConfig: Configuration) {}
    override fun onLowMemory() { cache.evictAll() }
}
```
In this implementation, the `LruCache` overrides `sizeOf` to measure `Bitmap.allocationByteCount`, preventing a scenario where a few high-resolution images consume hundreds of megabytes while remaining under a simplistic item-count threshold. By implementing `ComponentCallbacks2`, the cache listens to OS memory notifications. When `onTrimMemory` reports `TRIM_MEMORY_RUNNING_LOW`, the cache purges entries, relieving process RSS and preventing the Linux kernel from killing the app process.

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

Unbounded caches and poorly optimized lists cause memory regressions by retaining large object graphs and generating allocation churn during scrolling. Caches must enforce byte-bounded limits rather than item counts and respond to `onTrimMemory()` events. Large lists must reuse views or composables, avoid allocations inside binding passes, and window datasets using Paging 3.

## Interview answer — structured

Memory caches and long scrollable lists represent the most common vectors for memory exhaustion and frame drop regressions in mobile applications.

An improperly configured cache behaves like a managed memory leak. When developers use unbounded maps or configure an `LruCache` based on entry count rather than byte allocation, a small collection of high-resolution bitmaps can consume tens of megabytes, exhausting available heap limits and triggering aggressive garbage collection cycles.

In production, involving large lists, performance degradation typically stems from allocation churn during scroll gestures. If `onBindViewHolder` in RecyclerView or an item composable in LazyColumn repeatedly instantiates formatters, complex data structures, or lambda closures, the Android Runtime is flooded with short-lived objects. This allocation surge induces frequent Concurrent Copying GC passes, resulting in noticeable UI stutter and dropped frames.

Resilient architectures enforce two core safeguards. First, all memory caches must measure byte size and implement `ComponentCallbacks2.onTrimMemory` to evict entries when the operating system signals memory pressure. Second, large datasets must be paginated into memory using Jetpack Paging 3, ensuring that only visible and prefetch-windowed items reside in memory.


## Interview answer — deep senior

At the platform runtime and kernel layer, memory pressure is mediated through the Low Memory Killer daemon (LMKD) and ART garbage collection ergonomics. In ART, allocating objects at high velocity during list fling gestures rapidly fills the bump allocator nursery space, forcing the runtime to invoke Concurrent Copying (CC) GC cycles. Although CC GC avoids full-process stop-the-world pauses, it still incurs brief thread suspension intervals and thread contention, stealing critical milliseconds from the Choreographer rendering budget and manifesting as UI jank.
When an in-memory cache lacks explicit byte limits, process Resident Set Size (RSS) balloons. In low-RAM devices, the Linux kernel monitors memory pressure through Pressure Stall Information (PSI). When memory thresholds are breached, LMKD evaluates process OOM scores (oom_score_adj). If our application is cached or in the background and holding onto an unevicted 100MB bitmap cache, its high RSS makes it the prime candidate for immediate process termination.
To mitigate this, production caches must register with `Application.registerComponentCallbacks()`. In `onTrimMemory(level)`, engineers handle tiered levels: `TRIM_MEMORY_RUNNING_LOW` requires immediate cache eviction, while `TRIM_MEMORY_UI_HIDDEN` indicates that the user navigated away from the UI, warranting a partial cache trim to keep the process alive in the background.
For large lists, senior engineers audit RecyclerView view holders and Jetpack Compose LazyLists to ensure zero allocations during scroll passes. Date formatters, currency formatters, and click listeners must be hoisted or remembered outside item scopes. Furthermore, using Jetpack Paging 3 guarantees that off-screen pages are reclaimed and that only an optimal window of items remains reachable from the UI state holder, eliminating memory regressions across endless scroll feeds.

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
