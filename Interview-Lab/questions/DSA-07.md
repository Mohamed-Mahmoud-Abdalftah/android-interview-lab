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

## Practical walkthrough

قبل binary search، أثبت إن collection مرتبة بنفس comparator وأن الوصول بالindex سريع. لو sorted by name وتبحث ID، النتيجة غير صحيحة مهما كان الكود. مع duplicates حدد أول occurrence كما في المثال، واختبر empty/missing/bounds. لو مرة واحدة على unsorted data، scan `O(n)` أوفر من sort `O(n log n)`.

## Why it matters and how it works

Invariant: if target exists, it remains within [low, high]. Each comparison discards half under sorted order. Midpoint as `low + (high-low)/2` avoids integer overflow in general algorithms. On a linked list, middle access is O(n), undermining logarithmic runtime.

## Worked example

Kotlin’s `binarySearch` works on a list sorted under matching comparison. For product IDs sorted ascending, find an ID and interpret negative insertion-point result per API contract. If list is updated, re-sort or use a map rather than binary-search stale ordering.

This JVM example returns the first occurrence, making duplicate semantics explicit. The caller must supply an ascending, random-access list; the function does not sort or validate it.

```kotlin
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

private fun firstIndexOf(sorted: List<Int>, target: Int): Int {
    var low = 0
    var high = sorted.lastIndex
    var found = -1
    while (low <= high) {
        val mid = low + (high - low) / 2
        when {
            sorted[mid] < target -> low = mid + 1
            sorted[mid] > target -> high = mid - 1
            else -> {
                found = mid
                high = mid - 1
            }
        }
    }
    return found
}

class BinarySearchExampleTest {
    @Test fun firstDuplicateAndMissing() {
        assertEquals(1, firstIndexOf(listOf(1, 4, 4, 9), 4))
        assertEquals(-1, firstIndexOf(listOf(1, 4, 4, 9), 5))
        assertEquals(-1, firstIndexOf(emptyList(), 5))
    }
}
```

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

“I state the sortedness invariant before writing binary search. At each step, if the target exists, it remains in the inclusive interval from low to high. Comparing the midpoint lets me discard the half that cannot contain it, so the interval shrinks logarithmically. That conclusion assumes random-access indexing is efficient and the data is sorted under the same comparator used for the search. For duplicates I define the requirement explicitly: my example keeps searching left after a match to return the first occurrence. I calculate the midpoint as `low + (high - low) / 2` and test empty, one-item, absent, first/last and duplicate cases. For a single lookup in unsorted products, sorting first is more expensive than a linear scan. For repeated lookup by ID, a map may be clearer; for ordered range queries, a maintained sorted structure may justify binary search despite insert cost. In production I prefer a standard library API when its duplicate semantics fit, and I protect the sortedness contract at the data boundary.”

## How to answer in the interview

- **Why:** halving works only with sorted input.
- **How:** show invariant and duplicate boundary.
- **Trade-off:** sort-once cost versus repeated query gain.
- **Failure case:** wrong comparator returns false absence.
- **Production solution:** encode sortedness and test edges.

## Deep-dive talking points

Prompt for invariant, sorted comparator, random access, sort-before-search cost and duplicates.

## Follow-up questions

- [DSA-08](../dsa-08/): For unsorted duplicate detection, is binary search ideal? **Answer:** usually no; set or sort first.
- [DSA-02](../dsa-02/): Why logarithmic? **Answer:** discard a constant fraction each step.

## Self-check rubric

Write the sorted-input precondition, update low/high without overflow, state O(log n) time and explain why using it on unsorted UI data returns invalid results.

## References and reviewed-on date

- [Kotlin binarySearch API](https://kotlinlang.org/api/core/kotlin-stdlib/kotlin.collections/binary-search.html) — sorted-list requirement.
- [Android performance](https://developer.android.com/topic/performance) — practical measurement.

Technically reviewed against the cited primary documentation on 2026-10-13; automated technical review only, not human review.
