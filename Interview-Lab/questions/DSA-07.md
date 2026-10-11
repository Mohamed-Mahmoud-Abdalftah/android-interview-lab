---
id: "DSA-07"
question: "What is binary search, and what precondition does it require?"
topic: "Data Structures, Algorithms & Big O"
code: "DSA"
group: "A"
phase: 5
priority: "P2"
order: 446
editorial_status: "reviewed"
---

# DSA-07

## Original interview question

What is binary search, and what precondition does it require?

## What the interviewer evaluates

- Sorted random-access precondition and loop invariant.
- Overflow-safe midpoint and duplicate handling.

## Explanation in Arabic

Binary search بيقسم search range كل خطوة، فـO(log n)، لكن لازم data مرتبة بنفس comparator المستخدم. على random-access list بنمسك `low/high` ونقارن middle؛ لو أقل نروح يمين وإلا شمال. لو unsorted النتيجة غلط حتى لو code شغال. للduplicates لازم نحدد هل عايزين أي عنصر ولا أول/آخر occurrence.

## Why it matters and how it works

Invariant: if target exists, it remains within [low, high]. Each comparison discards half under sorted order. Midpoint as `low + (high-low)/2` avoids integer overflow in general algorithms. On a linked list, middle access is O(n), undermining logarithmic runtime.

## Worked example

Kotlin’s `binarySearch` works on a list sorted under matching comparison. For product IDs sorted ascending, find an ID and interpret negative insertion-point result per API contract. If list is updated, re-sort or use a map rather than binary-search stale ordering.

## Trade-offs and decision criteria

Sorting first costs O(n log n), so one search on unsorted input is not improved over O(n) scan. Repeated searches can justify keeping sorted order, but inserts may cost O(n) in array-backed lists.

## Failure modes

Searching a list sorted by name using an ID comparator violates precondition. Test empty, one item, absent target, duplicates, first/last element and large bounds.

## Production perspective

Keep sortedness as a type/data-layer invariant where feasible; use standard library rather than hand-written binary search unless custom boundary semantics are required.

## Interview answer — short

“Binary search is O(log n) because it halves a sorted random-access range. Sortedness under the same comparator is mandatory; otherwise the result is invalid.”

## Interview answer — structured

“I maintain low and high bounds, compare the midpoint and discard the half that cannot contain the target. The reasoning depends on sorted data and efficient indexed access. For one query on unsorted input, sorting first may cost more than a scan; for many queries I can maintain sorted order or build a map. I test absent and duplicate cases and use Kotlin’s library API when it fits.”

## Interview answer — deep senior

“I state the invariant and data precondition before code. The target, if present, stays in the current interval; each step shrinks it by about half, giving logarithmic comparisons. The whole operation is logarithmic only if midpoint access is constant and the collection is already sorted under the exact comparator. I use an overflow-safe midpoint in generic implementations and define boundary semantics for duplicates. In an Android repository, an index or map may be preferable if insert frequency or key lookup pattern makes sorted arrays costly. ”

## Deep-dive talking points

Prompt for invariant, sorted comparator, random access, sort-before-search cost and duplicates.

## Follow-up questions

- [DSA-08](../dsa-08/): For unsorted duplicate detection, is binary search ideal? **Answer:** usually no; set or sort first.
- [DSA-02](../dsa-02/): Why logarithmic? **Answer:** discard a constant fraction each step.

## Self-check rubric

Can you derive the bound, explain the Android example, identify a data or memory trade-off, and answer both follow-ups?

## References and reviewed-on date

- [Kotlin binarySearch API](https://kotlinlang.org/api/core/kotlin-stdlib/kotlin.collections/binary-search.html) — sorted-list requirement.
- [Android performance](https://developer.android.com/topic/performance) — practical measurement.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
