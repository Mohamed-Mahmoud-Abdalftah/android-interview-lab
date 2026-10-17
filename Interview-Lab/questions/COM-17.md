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

## Concept and technical explanation

Optimizing long lists and heavy calculations in Jetpack Compose requires a layered architectural approach addressing lazy allocation, algorithmic memoization, and rendering phase separation. Long lists are optimized by pairing LazyColumn with stable unique keys, granular content types, and windowed prefetching. Expensive calculations—such as currency conversions, date parsing, or heavy cryptographic hashing—must be strictly memoized using remember with explicit cache keys or offloaded to background Dispatchers.Default coroutines inside architecture ViewModels, ensuring that the main UI rendering thread never exceeds the 16.6ms per-frame budget.

## Practical walkthrough (English)

Optimizing heavy calculations and item recycling in a financial transactions list:
```kotlin
@Composable
fun TransactionRow(
    transaction: Transaction,
    taxRate: Double,
    modifier: Modifier = Modifier
) {
    // 1. MEMOIZE EXPENSIVE COMPUTATIONS: Only recalculates when transaction or taxRate changes!
    // Avoids running heavy date formatting and tax math on every recomposition pass!
    val formattedSummary = remember(transaction.id, transaction.amount, taxRate) {
        val totalWithTax = transaction.amount * (1.0 + taxRate)
        val formattedDate = DateTimeFormatter.ISO_INSTANT.format(transaction.timestamp)
        "Total: \$$totalWithTax on $formattedDate"
    }

    Row(modifier = modifier.fillMaxWidth().padding(12.dp)) {
        Text(transaction.title, modifier = Modifier.weight(1f))
        Text(formattedSummary, style = MaterialTheme.typography.bodyMedium)
    }
}

@Composable
fun TransactionList(transactions: List<Transaction>, taxRate: Double) {
    LazyColumn {
        items(
            items = transactions,
            key = { it.id }, // Stable key avoids layout thrashing
            contentType = { "TRANSACTION_ITEM" } // ContentType reuses layout structures
        ) { transaction ->
            TransactionRow(transaction = transaction, taxRate = taxRate)
        }
    }
}
```

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

We optimize long lists using LazyColumn with stable keys to preserve scroll state and content types to reuse layout nodes. Expensive calculations are memoized using remember with explicit keys so they only re-run when inputs change, or offloaded to Dispatchers.Default in the ViewModel. We also use derivedStateOf to filter high-frequency scroll observations and defer state reads to the layout or draw phases using lambda modifiers to eliminate unnecessary recompositions.

## Interview answer — structured

Ensuring seamless, jitter-free performance in data-heavy Jetpack Compose lists requires rigorous computational discipline across both presentation and data layers.
In a long list, performance bottlenecks typically stem from three mistakes: recalculating expensive data during composition, failing to provide list recycling metadata, and triggering viewport-wide recompositions during scrolling.
To optimize calculations, any non-trivial logic—such as string formatting, date parsing, sorting, or math operations—must never run directly inside the composable body.
If the calculation must exist in the UI layer, wrap it in remember(key1, key2) with explicit dependencies, guaranteeing it re-executes only when inputs mutate.
For heavy data transformations, perform the calculations upstream inside the ViewModel on Dispatchers.Default, exposing pre-formatted immutable display models to the UI.
To optimize list scrolling, configure LazyColumn with unique stable keys and explicit contentType identifiers.
This enables Compose to move existing SlotTable nodes rather than recreating them and allows SubcomposeLayout to recycle pre-measured layouts.
Finally, when observing scroll state (such as showing a scroll-to-top button), wrap the threshold check in derivedStateOf to prevent pixel-by-pixel recomposition.

## Interview answer — deep senior

Under the hood, optimizing long lists is an exercise in controlling allocations within the 16.6-millisecond (60fps) or 8.3-millisecond (120fps) frame deadline enforced by Choreographer VSYNC pulses.
When an unmemoized calculation sits inside a composable body, every recomposition pass executes that code synchronously on the Main thread.
If 50 visible items each parse a date string taking 0.5ms, the list consumes 25ms of CPU time on the main thread, resulting in immediate frame drops and jank.
Wrapping logic in remember caches the calculated result in the SlotTable's current slot; subsequent passes inspect slot equality and return the cached reference in O(1) time without allocating temporary heap objects.
In the Lazy list layout pipeline, SubcomposeLayout coordinates with AndroidX LazyLayoutPrefetcher.
When prefetching is enabled, Compose uses idle frame windows to pre-measure and pre-compose incoming items before they physically cross into the viewport boundary.
By providing stable keys and contentTypes, Compose's prefetcher can accurately match cached SubcomposeSlots, drastically reducing the measurement duration when the user flings the list.
Furthermore, senior engineers avoid reading state values inside modifier chains, using lambda variants like Modifier.drawWithCache or Modifier.graphicsLayer to perform visual transformations on the RenderNode directly without touching the CPU composition pipeline. This structural discipline ensures zero frame drops even during intense flings across deeply nested data sets.

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
