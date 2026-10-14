---
id: "COM-17"
question: "How do you optimize a long list and expensive calculations?"
topic: "Jetpack Compose"
code: "COM"
group: "B"
phase: 3
priority: "P1"
order: 246
editorial_status: "reviewed"
---

# COM-17

## Original interview question

How do you optimize a long list and expensive calculations?

## What the interviewer evaluates

- Diagnose whether list, data transform, image, or layout is the bottleneck.
- Use lazy items, stable identity, paging and cancellation appropriately.
- Measure release performance and avoid stale memoized data.

## Explanation in Arabic

كيفية تحسين أداء القوائم الطويلة (Long Lists) والعمليات الحسابية المكلفة في Jetpack Compose:

1. تحسين القوائم الطويلة في `LazyColumn`:
   - **تحديد المفاتيح المستقرة (`key = { it.id }`)**: لتمكين التخطي الذكي وحماية الحالة أثناء السكرول والتعديل.
   - **تحديد نوع المحتوى (`contentType`)**: لإعادة تدوير الـ Slots بين العناصر المتشابهة في القوائم غير المتجانسة.
   - **تجنب العمليات الثقيلة داخل عناصر القائمة**: لا تقم أبداً بقراءة ملفات، فك تشفير صور يدوياً، أو تنسيق تواريخ معقدة داخل دالة الـ Item Composable دون `remember`.
   - **LazyListState Optimization**: عدم قراءة موضع السكرول مباشرة داخل محتوى العنصر؛ بل استخدم `derivedStateOf` للأزرار العائمة خارج القائمة.

2. تحسين الحسابات المكلفة (Expensive Calculations):
   - استخدام `remember(key1, key2) { ... }` لحساب النتائج المعقدة لمرة واحدة فقط طالما أن المدخلات لم تتغير.
   - ترحيل العمليات الحسابية الضخمة (مثل الفرز Sorting، والفلترة Filtering، وتحليل النصوص) إلى الـ `ViewModel` على **`Dispatchers.Default`** وتمرير النتائج الجاهزة كـ State نهائي للشاشة.

## Practical walkthrough

تحسين قائمة طويلة تحتوي على حسابات معقدة وفلاتر:
```kotlin
// ❌ كود سيء: يقوم بفرز وتصفية 5000 عنصر في كل فريم Recomposition:
@Composable
fun BadProductList(products: List<Product>, filterText: String) {
    // 💥 كارثة: معالجة ثقيلة جداً تعطل الـ Main Thread في كل سكرول!
    val filtered = products.filter { it.name.contains(filterText) }.sortedBy { it.price }
    LazyColumn {
        items(filtered) { Text(it.name) }
    }
}

// ✅ كود محسن: حفظ نتيجة الفلترة باستخدام remember وحماية القائمة بـ Keys:
@Composable
fun GoodProductList(
    products: ImmutableList<Product>,
    filterText: String,
    modifier: Modifier = Modifier
) {
    // إعادة الحساب فقط إذا تغيرت قائمة المنتجات أو نص الفلترة:
    val filtered = remember(products, filterText) {
        products.filter { it.name.contains(filterText, ignoreCase = true) }
            .sortedBy { it.price }
            .toPersistentList()
    }

    LazyColumn(modifier = modifier) {
        items(
            items = filtered,
            key = { it.id }, // مفتاح مستقر فريد
            contentType = { "PRODUCT_CARD" } // نوع محتوى ثابت لإعادة التدوير
        ) { product ->
            ProductItemCard(product)
        }
    }
}
```

## Why it matters and how it works

Lazy layouts reduce composed item count but each visible item still costs composition, measure and draw. Preprocessing an entire dataset in a composable can block frames before the lazy list helps. Stable keys preserve item state across reorder, while content types improve compatible reuse. Paging bounds fetched data and supports incremental loading, with its own loading/error states.

## Worked example

A 10,000-product catalog filters and sorts on every character inside `CatalogScreen`. Move query processing to a cancellable ViewModel pipeline, request pages from storage/search, key rows by product ID, and use an image loader with size-aware requests. Test rapid typing and scroll while new pages arrive; compare frame timing and allocation against baseline.

### Compose/Kotlin walkthrough

```kotlin
// ui.products is already filtered/paged by the owner; no sort in composition.
@Composable
fun ProductList(products: List<ProductUi>, onOpen: (String) -> Unit) {
    LazyColumn {
        items(products, key = ProductUi::id, contentType = { "product" }) { product ->
            Text(product.title, Modifier.clickable { onOpen(product.id) })
        }
    }
}
// Imports: foundation.lazy.LazyColumn/items, foundation.clickable.
// For remote large data, collect Paging data and use paging-compose APIs.
```

## Trade-offs and decision criteria

Caching reduces repeated calculation but costs memory and invalidation complexity. Paging adds state and boundary handling but avoids loading all records. Precomputing results improves UI responsiveness only if it avoids moving the same expensive work to another hot path. A small fixed list may need no optimization beyond readable code.

## Failure modes

Memoization keys omit locale or filter and show stale results. Index keys move row state after insert. Diff-like work runs on main thread for every query. The list is fast in debug sample data but janks on release devices with real images. Prefetching too much causes memory pressure.

## Production perspective

Profile representative devices and real data, track p95 scroll frames and memory, and maintain a benchmark for critical feeds. Test paging refresh, load errors, inserts, and cancellation; optimize the proven stage rather than only list recomposition counts.

## Interview answer — short

Optimize long lists in Compose by providing unique stable `key`s and `contentType`s in `LazyColumn`, eliminating allocations inside item composables, and memoizing expensive computations with `remember(keys)` or offloading sorting and filtering to `Dispatchers.Default` in the ViewModel.

## Interview answer — structured

High-performance scrolling in Jetpack Compose requires eliminating work from the frame budget during list layout.

First, **LazyList Optimization Pillars**. Next, with Stable Keys, always declare `key = { it.id }` in `items()`. This lets Compose map items to stable slot table entries, skipping item recomposition when lists shift or reorder.
Additionally, with Content Types, specify `contentType` for heterogeneous lists to enable slot recycling across visually identical views. With Subcomposition Overhead, minimize nested `LazyRow` components or deep layout hierarchies inside items; keep item composables flat and lightweight.
**Handling Expensive Calculations**. With Memoization, if computations depend on UI inputs, wrap them in `remember(key1, key2) { expensiveComputation() }` so they re-run only when dependencies change.
Finally, with Background Offloading, truly CPU-heavy tasks—such as sorting 10,000 items, searching, or regex filtering—do not belong in the UI layer. They must be executed inside the ViewModel or Domain layer via `flowOn(Dispatchers.Default)` and exposed as pre-calculated, ready-to-render immutable lists.


## Interview answer — deep senior

Under the hood, `LazyColumn` uses a specialized subcomposition pipeline called `SubcomposeLayout`. Unlike standard layouts that measure and compose in a single pass, `SubcomposeLayout` delays the composition of off-screen items until the scrolling measurement pass determines they are about to become visible. If an item's composable function does heavy work during this deferred composition pass, the frame budget (16.6ms at 60Hz or 8.3ms at 120Hz) is exceeded instantly, resulting in visible scroll jank.

Another critical lever is image loading. When using Coil, always configure explicit sizing (`size(ViewSizeResolver)` or modifier constraints) and bitmap pooling. If images are loaded without fixed bounds in a LazyColumn, Coil decodes full images before layout measurement can constrain them, blowing through memory.

In Macrobenchmark tests, we measure scroll performance using `FrameTimingMetric()` across continuous fling scrolls to ensure 99th percentile frame times stay strictly under the display hardware refresh limit.


## How to answer in the interview

- **Why:** lazy composition solves visible-row work, not upstream CPU.
- **How:** move filtering and sorting to cancellable data work, then key rows.
- **Trade-off:** Paging adds loading and error states.
- **Failure case:** obsolete search results replace current query.
- **Production solution:** test rapid typing, scroll, allocations, and release frames.

## Deep-dive talking points

Discuss lazy composition, paging, stable keys, preprocessing, image cost, cache invalidation, and release benchmarks.

## Follow-up questions

- **Interviewer:** "What is `SubcomposeLayout` and why does it have an overhead compared to normal Layout?"
  **Answer:** "`SubcomposeLayout` allows measuring one child to decide what to compose in another (used by `LazyColumn` and `Scaffold`). It carries a runtime penalty because it interrupts the standard single-pass composition pipeline to execute dynamic subcomposition passes."

- **Interviewer:** "Why shouldn't you place a `LazyColumn` inside a vertically scrolling `Column`?"
  **Answer:** "A scrolling `Column` provides infinite vertical constraints (`Constraints.Infinity`). A `LazyColumn` cannot calculate viewport bounds against infinite constraints, throwing an `IllegalStateException` at runtime."

## Self-check rubric

Identify the bottleneck, propose a targeted change, cover stale keys, and specify release measurements.

## References and reviewed-on date

- [Lazy lists and grids](https://developer.android.com/develop/ui/compose/lists) — keys and content types.
- [Compose performance](https://developer.android.com/develop/ui/compose/performance) — measured optimization.
- [Paging in Compose](https://developer.android.com/topic/libraries/architecture/paging/v3-overview) — incremental data.

Technically reviewed against primary documentation on 2026-10-13.
