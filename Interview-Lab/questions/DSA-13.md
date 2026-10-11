---
id: "DSA-13"
question: "How can Kotlin collection chaining create temporary allocations?"
topic: "Data Structures, Algorithms & Big O"
code: "DSA"
group: "B"
phase: 5
priority: "P2"
order: 452
editorial_status: "reviewed"
---

# DSA-13

## Original interview question

How can Kotlin collection chaining create temporary allocations?

## What the interviewer evaluates

- Eager collection operators and temporary list allocations.
- Sequences, Flow and loop alternatives with lifecycle caveats.

## Explanation in Arabic

Kotlin `list.filter().map().sorted()` على Iterable غالبًا تعمل intermediate collections؛ كل مرحلة تزور عناصر وتخصص memory. `asSequence()` يخلي filter/map lazy ويقلل intermediates، لكن `sorted()` materializes لأن الترتيب يحتاج كل العناصر. Sequence مش دايمًا أسرع للlists الصغيرة بسبب overhead؛ نقيس. `Flow` للasync stream مش بديل تلقائي لكل collection chain.

## Why it matters and how it works

Iterable extension functions like filter/map return new lists. A Sequence composes lazy operations and produces elements on terminal evaluation; stateful operations such as sorting still buffer. Android allocations can increase GC/jank if chain runs on every keystroke/recomposition.

## Worked example

For 10k products, `products.filter { it.active }.map { it.name }` creates filtered and mapped lists. `products.asSequence().filter { it.active }.map { it.name }.toList()` typically avoids the filtered intermediate. For a 5-item menu, the simple chain is likely clearer and adequate.

## Trade-offs and decision criteria

Sequences save some allocations on longer pipelines or early termination, but add iterator overhead and can complicate debugging. A hand-written loop can be fastest but less declarative; choose after profiling.

## Failure modes

Calling `asSequence().sorted().toList()` and claiming constant memory is wrong. Forgetting terminal operation means no work executes. Capturing mutable state in a lazy sequence can change results unexpectedly.

## Production perspective

Profile allocation counts and latency on realistic input sizes, especially transformations feeding Compose. Cache stable derived state in the right layer and test invalidation.

## Interview answer — short

“Kotlin Iterable chains can allocate intermediate lists; Sequences fuse lazy steps until a terminal operation, but stateful operations still buffer. I use them when measured allocation savings justify it.”

## Interview answer — structured

“`filter` then `map` on a List usually creates two lists and traverses data twice. A Sequence can fuse those operations and avoid one intermediate allocation, but `sorted` still needs materialization and small inputs may be slower due to iterator overhead. On Android I watch allocations in hot UI paths, keep simple code for small data, and benchmark before changing to sequences or manual loops. The mechanics matter. Iterable extension functions like filter/map return new lists. A Sequence composes lazy operations and produces elements on terminal evaluation; stateful operations such as sorting still buffer. Android allocations can increase GC/jank if chain runs on every keystroke/recomposition. The choice has a trade-off. Sequences save some allocations on longer pipelines or early termination, but add iterator overhead and can complicate debugging. A hand-written loop can be fastest but less declarative; choose after profiling.”

## Interview answer — deep senior

“I examine both asymptotic cost and allocation profile. A chain of eager list operators can be O(k·n) with k traversals and O(n) temporary space; that is still O(n) for fixed k but may cause GC churn per frame. Sequences fuse stateless operators and can stop early, yet sorting/grouping materializes, and terminal execution timing matters. `Flow` adds asynchronous/cancellation semantics and is not a drop-in microoptimization. I move expensive derivations out of recomposition, use stable snapshots and measure low-end-device frame impact. Consider a concrete case. For 10k products, `products.filter { it.active }.map { it.name }` creates filtered and mapped lists. `products.asSequence().filter { it.active }.map { it.name }.toList()` typically avoids the filtered intermediate. For a 5-item menu, the simple chain is likely clearer and adequate. A failure case illustrates the risk. Calling `asSequence().sorted().toList()` and claiming constant memory is wrong. Forgetting terminal operation means no work executes. Capturing mutable state in a lazy sequence can change results unexpectedly. In production, the response is concrete. Profile allocation counts and latency on realistic input sizes, especially transformations feeding Compose. Cache stable derived state in the right layer and test invalidation. The decision has a trade-off. Sequences save some allocations on longer pipelines or early termination, but add iterator overhead and can complicate debugging. A hand-written loop can be fastest but less declarative; choose after profiling.”

## Deep-dive talking points

Prompt for eager intermediates, lazy terminal, sorting materialization, small-input overhead.

## Follow-up questions

- [DSA-12](../dsa-12/): What is worse than allocations? **Answer:** hidden O(n²) lookup inside chain.
- [DSA-16](../dsa-16/): How optimize safely? **Answer:** profile, preserve behavior and benchmark after change.

## Self-check rubric

Can you derive the bound, explain the Android example, identify a trade-off/failure, and answer both follow-ups?

## References and reviewed-on date

- [Kotlin sequences](https://kotlinlang.org/docs/sequences.html) — lazy pipeline semantics.
- [Kotlin collection filtering](https://kotlinlang.org/docs/collection-filtering.html) — eager list operations.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
