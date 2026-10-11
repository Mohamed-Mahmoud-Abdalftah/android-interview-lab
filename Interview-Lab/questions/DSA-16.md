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

“Optimization is an engineering experiment. I state a hypothesis, baseline measurement and acceptance threshold; isolate the hot path; preserve semantics including ordering, equality, cancellation and thread safety; and change one variable. An index may reduce O(n²) to expected O(n) but increase memory and alter duplicate behavior, so tests and code review cover those risks. I benchmark cold/warm cases and p95 frames, then monitor staged rollout. If the code becomes harder to maintain for negligible gain, I reject it. Stop optimization when bottleneck moves elsewhere.”

## Deep-dive talking points

Prompt for hypothesis, semantic tests, complexity/memory trade, realistic benchmark and rollback.

## Follow-up questions

- [DSA-12](../dsa-12/): What is a common optimization? **Answer:** build one lookup index outside per-row work.
- [DSA-14](../dsa-14/): How know it helped? **Answer:** compare traces and frame distributions on low-end hardware.

## Self-check rubric

Can you derive the bound, explain the Android example, identify a trade-off/failure, and answer both follow-ups?

## References and reviewed-on date

- [Android performance](https://developer.android.com/topic/performance) — profiling guidance.
- [Kotlin collections overview](https://kotlinlang.org/docs/collections-overview.html) — operation semantics.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
