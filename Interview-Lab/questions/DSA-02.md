---
id: "DSA-02"
question: "Explain O(1), O(log n), O(n), O(n log n), and O(n²)."
topic: "Data Structures, Algorithms & Big O"
code: "DSA"
group: "A"
phase: 5
priority: "P2"
order: 441
editorial_status: "reviewed"
---

# DSA-02

## Original interview question

Explain O(1), O(log n), O(n), O(n log n), and O(n²).

## What the interviewer evaluates

- Interpreting common growth classes quantitatively.
- Input assumptions and O(n²) UI risk.

## Explanation in Arabic

`O(1)` ثابت بالنسبة لـn، `O(log n)` بيقلل البحث بنسبة ثابتة كل خطوة، `O(n)` مرور واحد، `O(n log n)` زي sort comparison غالبًا، و`O(n²)` كل عنصر يقارن بكل عنصر. Big O حد نمو مش وقت بالثواني؛ O(1) operation ممكن تكون غالية وO(n) على 10 عناصر سريعة.

### Practical walkthrough in Egyptian Arabic

في Android، قراءة قيمة من map متوقعة `O(1)`، binary search على sorted array `O(log n)`، scan `O(n)`، sort `O(n log n)`، والمقارنة بين كل زوج `O(n²)`. اشرح كل فئة بمقدار العمل عند مضاعفة n، ولا تخلط expected hash performance بضمان worst case. لو العملية في recomposition أو binding، حتى `O(n)` قد تتكرر كثيرًا.

## Why it matters and how it works

For n=1,000, doubling n has approximate effects: constant unchanged, logarithmic grows slightly, linear doubles, n log n a bit more than doubles, quadratic quadruples. These are asymptotic patterns, not exact predictions.

## Worked example

A product search over sorted IDs can use binary search O(log n); filtering all products is O(n); sorting new data O(n log n); calling `list.find` inside a map over all rows becomes O(n²). In Compose, avoid repeating such work on recomposition.

## Trade-offs and decision criteria

Better complexity may require precomputation/memory or sorted input. A hash map lookup is expected O(1) but not guaranteed worst case. Choose according to update frequency and list size.

## Failure modes

Quoting binary search as O(log n) without sorted input is invalid. A loop that calls a hidden O(n) function is not O(n). Inspect callees and data invariants.

## Production perspective

Use benchmarks and traces to verify hot-path assumptions on low-end devices. Precompute indexes only where repeated lookups justify memory and maintenance cost.

## Interview answer — short

“The common growth classes range from constant to quadratic. I derive them from operations and input invariants, then use profiling to decide whether the difference matters in the app.”

## Interview answer — structured

“O(1) is input-independent work, O(log n) repeatedly halves a search space, O(n) scans, O(n log n) often appears in comparison sorting, and O(n²) often comes from nested work. The label describes growth, not exact latency. For a product list, a repeated linear lookup inside a per-row map can freeze low-end devices as n grows; I would index or precompute if measurements justify it.”

## Interview answer — deep senior

“I explain these classes by what happens when input doubles. Constant-time indexed access or expected hash lookup barely changes with n under its assumptions. Binary search halves a sorted random-access interval and takes logarithmic comparisons. A scan grows linearly; comparison sorting commonly grows around n log n; checking every pair grows quadratically. I do not treat the labels as performance guarantees: a hash map has collision and allocation costs, and an `O(n)` loop that decodes images on Main can be worse than a clean `O(n log n)` sort off Main. In an Android product list, I would first identify whether a per-row lookup makes total rendering quadratic, then pre-index IDs once if memory allows. I also name preconditions: binary search requires sorted input, and map keys need stable equality. I test sizes that represent production, use a profiler for CPU and allocations, and explain the trade-off between asymptotic growth and constants before choosing an optimization.”

## How to answer in the interview

- **Why:** growth predicts user-facing scaling.
- **How:** tie each class to a concrete operation.
- **Trade-off:** fast expected case versus worst-case assumptions.
- **Failure case:** nested scan repeats per row.
- **Production solution:** measure call frequency and input size.

## Deep-dive talking points

Prompt for doubling intuition, hidden work, sorted precondition and practical crossover.

## Follow-up questions

- [DSA-07](../dsa-07/): What enables log search? **Answer:** sorted random-access data.
- [DSA-12](../dsa-12/): How can list code become quadratic? **Answer:** linear lookup inside a per-item transformation.

## Self-check rubric

Give one growth example for each listed class, compare n and 10n behavior, and explain why an O(n log n) implementation may still lose on tiny inputs.

## References and reviewed-on date

- [Kotlin collections overview](https://kotlinlang.org/docs/collections-overview.html) — collection operations.
- [Android performance](https://developer.android.com/topic/performance) — measurement context.

Technically reviewed against the cited primary documentation on 2026-10-13; automated technical review only, not human review.
