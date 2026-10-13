---
id: "DSA-16"
question: "How do you optimize an algorithm while keeping code maintainable and correct?"
topic: "Data Structures, Algorithms & Big O"
code: "DSA"
group: "C"
phase: 5
priority: "P2"
order: 455
editorial_status: "reviewed"
---

# DSA-16

## Original interview question

How do you optimize an algorithm while keeping code maintainable and correct?

## What the interviewer evaluates

- Optimization process with proof of behavior and measured bottleneck.
- Maintainability, safety and rollback thresholds.

## Explanation in Arabic

تحسين algorithm يبدأ بتحديد input range وقياس hot path، مش تحويل كل code لـlow-level loops. نثبت behavior باختبارات للحالات الحدية، نشتق complexity، نغير خطوة واحدة زي preindexing أو batching، ونقيس على جهاز ممثل. نراجع memory، concurrency وreadability؛ أسرع code مش مكسب لو بيكسر correctness أو يصعب صيانته.

## Practical walkthrough

قبل optimization اثبت bottleneck بمقياس. اكتب contract واختبارات edge cases، ثم غير algorithm في جزء واحد: مثل بدل nested scan أنشئ map واحدة. قارن output قبل وبعد على بيانات صغيرة وكبيرة، راقب memory/GC، وخلي code مفهوم لفريق Android. لو improvement 2ms لكن صعّب debugging ووضع state، قد لا يستحق؛ وثّق الافتراضات وأعد القياس في release.

## Why it matters and how it works

A valid optimization preserves observable semantics under the same inputs, including ordering, duplicates, nulls, cancellation and errors. Complexity guides candidates; benchmarks confirm real costs. Readability and maintenance affect future defect rates.

## Worked example

A list join uses nested `find` calls O(n²). Add tests for duplicate/missing prices and order, replace with one `associateBy` map O(n) expected, then benchmark at 100/1k/10k items and inspect memory. Document which duplicate wins if map overwrites earlier entries.

## Trade-offs and decision criteria

Indexing trades memory for speed; a Sequence reduces intermediates but may add overhead. If measured inputs are tiny, keep simpler code. Stop optimization when bottleneck moves elsewhere.

## Failure modes

An optimization changes duplicate handling from “first match” to “last match” by using associateBy. Tests must capture semantics or deliberately change spec. Parallelization may introduce races even if wall time improves.

## Production perspective

Code review includes before/after trace, benchmark method, edge-case tests and rollback plan. Watch production p95 jank and memory after staged release.

## Interview answer — short

“I profile first, preserve behavior with edge-case tests, improve the measured complexity, then benchmark CPU, memory and readability on real inputs.”

## Interview answer — structured

“I locate the bottleneck, derive its complexity and write tests for behavior before changing it. If a nested list join is quadratic, I may preindex one side, but I must define duplicate and missing-key semantics. I benchmark across realistic sizes on low-end devices and check allocations. I prefer a clear O(n) solution over a clever but fragile microoptimization, and I roll back if production metrics regress. Stop optimization when bottleneck moves elsewhere.”

## Interview answer — deep senior

“I optimize only after I can name the bottleneck and preserve its contract. I establish a baseline on realistic inputs and a release-like device, write tests for the current behavior and edge cases, then change one algorithmic decision. Replacing a nested scan with a map, for example, may reduce expected time from quadratic to linear but adds memory and invalidation rules. I compare outputs before and after, measure CPU, allocations, frame time and memory, and check that the new code remains understandable to the team. A clever custom data structure is not a win if it introduces concurrency bugs or hides ownership. I also distinguish a microbenchmark from user experience: a two-millisecond unit improvement may not affect frames, while a modest allocation reduction in a frequently recomposed screen may. I document assumptions such as stable IDs and maximum list size, and define a rollback trigger if production metrics worsen. The final answer is a measured, correct trade-off rather than an asymptotic label alone.”

## How to answer in the interview

- **Why:** optimization should solve measured pain.
- **How:** baseline, preserve contract, compare results.
- **Trade-off:** speed versus memory and maintainability.
- **Failure case:** microbenchmark hides UI regression.
- **Production solution:** ship with regression tests and profiling.

## Deep-dive talking points

Prompt for hypothesis, semantic tests, complexity/memory trade, realistic benchmark and rollback.

## Follow-up questions

- [DSA-12](../dsa-12/): What is a common optimization? **Answer:** build one lookup index outside per-row work.
- [DSA-14](../dsa-14/): How know it helped? **Answer:** compare traces and frame distributions on low-end hardware.

## Self-check rubric

Prove the original and optimized algorithm return the same result on edge cases, measure complexity and real latency, and keep the implementation understandable enough to maintain.

## References and reviewed-on date

- [Android performance](https://developer.android.com/topic/performance) — profiling guidance.
- [Kotlin collections overview](https://kotlinlang.org/docs/collections-overview.html) — operation semantics.

Technically reviewed against the cited primary documentation on 2026-10-13; automated technical review only, not human review.
