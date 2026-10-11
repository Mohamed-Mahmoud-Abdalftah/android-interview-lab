---
id: "DSA-12"
question: "How do you identify an accidental O(n²) transformation in a RecyclerView/Compose list?"
topic: "Data Structures, Algorithms & Big O"
code: "DSA"
group: "B"
phase: 5
priority: "P2"
order: 451
editorial_status: "reviewed"
---

# DSA-12

## Original interview question

How do you identify an accidental O(n²) transformation in a RecyclerView/Compose list?

## What the interviewer evaluates

- Detecting hidden repeated linear work in UI list transforms.
- Preindexing once and preserving lifecycle correctness.

## Explanation in Arabic

RecyclerView/Compose list ممكن تبقى O(n²) لو لكل item نعمل `others.find { id == ... }` أو `filter` على list كلها. الـUI يظهر كويس مع 20 item ويهنّج مع آلاف، خصوصًا لو transformation تتعاد في recomposition. نعمل lookup map مرة لكل snapshot أو join في data layer، ونقيس allocations والframe time.

## Why it matters and how it works

Outer per-row mapping O(n) times inner linear search O(n) gives O(n²). Rebuilding a map inside each row is also quadratic despite O(1) subsequent lookup. Create it once per data snapshot, then row lookups are expected O(1), total expected O(n) plus memory.

## Worked example

Bad: `products.map { p -> p.copy(price = prices.find { it.id == p.id }?.value) }`. Better: `val byId = prices.associateBy { it.id }; products.map { p -> p.copy(price = byId[p.id]?.value) }`. Assumes unique IDs and correct snapshot invalidation.

## Trade-offs and decision criteria

Index uses O(n) memory and build cost; for tiny lists or one lookup it may not win. If data updates often, cache invalidation and thread confinement matter. Avoid doing heavy joins inside Composable bodies.

## Failure modes

Memoizing a map without including prices in the key leaves stale prices. Moving work to `Dispatchers.Default` avoids main-thread freeze but does not fix quadratic scaling. Profile first and verify output after refactor.

## Production perspective

Use traces to split bind/recomposition time from data transform time. Benchmark scaling at n=100,1k,10k on low-end device and add a regression test for join correctness.

## Interview answer — short

“A linear lookup inside per-item mapping makes O(n²) work. I preindex the lookup data once, move transforms to the data layer, and measure frames and allocations.”

## Interview answer — structured

“I inspect nested operations, including hidden `find` or `contains` calls. If n rows each scan n prices, the transform is quadratic. Building an `associateBy` map once costs expected O(n) time/space and makes each lookup expected constant. I keep that derivation outside composition and invalidate it when inputs change. I still profile because rendering/image work can also cause jank. The mechanics matter. Outer per-row mapping O(n) times inner linear search O(n) gives O(n²). Rebuilding a map inside each row is also quadratic despite O(1) subsequent lookup. Create it once per data snapshot, then row lookups are expected O(1), total expected O(n) plus memory. The choice has a trade-off. Index uses O(n) memory and build cost; for tiny lists or one lookup it may not win. If data updates often, cache invalidation and thread confinement matter. Avoid doing heavy joins inside Composable bodies.”

## Interview answer — deep senior

“I diagnose the pipeline: data fetch, transform, diffing, binding/recomposition, image decode and GPU rendering. A trace showing CPU spent in per-row lookup points to algorithmic complexity; repeated composition alone is not proof. I use a stable map keyed by immutable ID per snapshot, validate duplicate-key behavior and avoid stale memoization. I test on low-end devices with scaling input sizes and compare frame times/allocations after change. Offloading to a worker thread can protect UI responsiveness but is not a substitute for reducing O(n²) work. Consider a concrete case. Bad: `products.map { p -> p.copy(price = prices.find { it.id == p.id }?.value) }`. Better: `val byId = prices.associateBy { it.id }; products.map { p -> p.copy(price = byId[p.id]?.value) }`. Assumes unique IDs and correct snapshot invalidation. A failure case illustrates the risk. Memoizing a map without including prices in the key leaves stale prices. Moving work to `Dispatchers.Default` avoids main-thread freeze but does not fix quadratic scaling. Profile first and verify output after refactor. In production, the response is concrete. Use traces to split bind/recomposition time from data transform time. Benchmark scaling at n=100,1k,10k on low-end device and add a regression test for join correctness.”

## Deep-dive talking points

Prompt for hidden find, one-time index, snapshot invalidation, rendering versus data trace.

## Follow-up questions

- [DSA-06](../dsa-06/): What is map lookup bound? **Answer:** expected O(1), with hash caveats.
- [DSA-14](../dsa-14/): How distinguish jank sources? **Answer:** trace CPU/render work separately.

## Self-check rubric

Can you derive the bound, explain the Android example, identify a trade-off/failure, and answer both follow-ups?

## References and reviewed-on date

- [Kotlin associateBy](https://kotlinlang.org/api/core/kotlin-stdlib/kotlin.collections/associate-by.html) — index construction.
- [Android rendering performance](https://developer.android.com/topic/performance/rendering) — frame diagnosis.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
