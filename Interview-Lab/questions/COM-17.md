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

`LazyColumn` ينشئ العناصر المطلوبة قرب viewport بدل بناء آلاف rows دفعة واحدة، لكن لا يحل وحده sorting/filtering مكلف على main thread أو image decode سيئ. استخدم keys ثابتة، `contentType` عندما layouts مختلفة، وPaging للبيانات الكبيرة/المستمرة. ضع calculation ثقيلة في data/ViewModel layer أو cache بمفاتيح صحيحة، وألغِ البحث القديم عند query جديدة. `remember` مناسب لحساب UI محلي صغير عند صحة keys، وليس بديلًا لحساب domain واسع. قِس release frames، allocation وscroll.

## Practical walkthrough

قائمة 10,000 منتج لازم تجمع بين lazy rendering وبين تجهيز data صح. `LazyColumn` توفر rows خارج viewport، لكن sorting 10,000 item داخل body كل حرف هيوقف main thread. خلي البحث في ViewModel/repository مع cancellation وPaging لو البيانات ضخمة، ومرر ID ثابت لكل row؛ جرب كتابة سريعة مع scroll. لو الصور بتتفكّك بحجمها الأصلي أثناء scroll، lazy list مش هتمنع jank أو memory pressure. قِس allocation وframe time مع بيانات حقيقية، وحمّل صورة بحجم مناسب للعرض.

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

“I profile the hot stage, use lazy/paged data with stable item IDs, move heavy transforms off rendering, and benchmark scrolling with real images and data. LazyColumn limits visible row work; it does not make sorting or IO free.”

## Interview answer — structured

“I first determine whether composition, layout, image decode, or data transforms consume the frame. LazyColumn limits visible composition, but a full sort inside the composable still blocks typing. I move that work to a cancellable state pipeline, use Paging if the dataset is large, and key rows by stable IDs. I cache only with correct invalidation keys, then compare release scroll and memory metrics. For a large catalog, I prepare results in a cancellable owner pipeline and key rows by product ID.”

## Interview answer — deep senior

“I avoid starting with an annotation or a remembered expression. I reproduce the slowdown with production-scale data and inspect a release trace. If the issue is a full sort on each keystroke, LazyColumn cannot solve it because the transform happens before rows are composed. I move filtering or search to an owned pipeline, cancel obsolete queries, and page results when the source is large. If row composition is costly, I simplify row content, provide stable keys and useful content types, and check whether parameter identity and state reads cause needless work. If images dominate, I request appropriate sizes and inspect decode/cache behavior. Memoization is only correct when all inputs such as query, filters, locale and dataset version are represented; a wrong key is a stale-UI bug. I measure p95 scroll frames, allocations and memory on target devices, plus loading and error behavior during refresh. A small list should remain simple. The senior decision is to spend complexity only where trace evidence shows an actual user-visible gain. I test rapid typing and scrolling together because stale results and frame stalls often appear in combination.”

## How to answer in the interview

- **Why:** lazy composition solves visible-row work, not upstream CPU.
- **How:** move filtering and sorting to cancellable data work, then key rows.
- **Trade-off:** Paging adds loading and error states.
- **Failure case:** obsolete search results replace current query.
- **Production solution:** test rapid typing, scroll, allocations, and release frames.

## Deep-dive talking points

Discuss lazy composition, paging, stable keys, preprocessing, image cost, cache invalidation, and release benchmarks.

## Follow-up questions

- Does LazyColumn make an O(n log n) sort inside composition cheap? **Answer:** no; it only limits item composition, not upstream transforms.
- Why are memoization keys a correctness concern? **Answer:** omitted inputs can return stale results.
- When should Paging be considered? **Answer:** when data is large or loaded incrementally and full materialization is costly.

## Self-check rubric

Identify the bottleneck, propose a targeted change, cover stale keys, and specify release measurements.

## References and reviewed-on date

- [Lazy lists and grids](https://developer.android.com/develop/ui/compose/lists) — keys and content types.
- [Compose performance](https://developer.android.com/develop/ui/compose/performance) — measured optimization.
- [Paging in Compose](https://developer.android.com/topic/libraries/architecture/paging/v3-overview) — incremental data.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. Workload and performance numbers are illustrative.
