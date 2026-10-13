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

ما هو البحث الثنائي (Binary Search)، وما هو الشرط الأساسي لتطبيقه، وكيف يعمل برمجياً؟

1. ما هو البحث الثنائي وكيف يعمل؟
   - خوارزمية بحث عالية الكفاءة تعمل بتعقيد زمني لوغاريتمي **$O(\log n)$**.
   - في كل خطوة، تقارن العنصر المستهدف (Target) بالعنصر الموجود في منتصف النطاق (Middle element):
     * إذا كان متطابقاً، ينتهي البحث بنجاح.
     * إذا كان الهدف أصغر من المنتصف، يتم استبعاد النصف الأيمن بالكامل والبحث في النصف الأيسر فقط.
     * إذا كان الهدف أكبر من المنتصف، يتم استبعاد النصف الأيسر بالكامل والبحث في النصف الأيمن فقط.
   - بهذه الطريقة، يمكن البحث بين 1,000,000 عنصر في 20 خطوة فقط!

2. الشرط المسبق الإلزامي (The Strict Precondition):
   - **يجب أن تكون البيانات مرتبة تماماً (Sorted Collection)**، وتدعم **الوصول العشوائي السريع في وقت ثابت (Random Access - $O(1)$)** مثل الـ Arrays أو الـ ArrayList.
   - إذا كانت القائمة غير مرتبة، فإن البحث الثنائي سيعطي نتائج خاطئة تماماً.
   - إذا طُبق البحث الثنائي على `LinkedList`، سيفقد ميزته لأن الوصول لعنصر المنتصف يستغرق $O(n)$، مما يجعل التعقيد الإجمالي ينحدر إلى $O(n)$!

3. خطأ الـ Integer Overflow الشهير:
   - كتابة `val mid = (low + high) / 2` تسبب Bug شهير إذا كان مجموع الرقمين أكبر من `Int.MAX_VALUE` ($2^{31}-1$).
   - الحل الهندسي الصحيح: `val mid = low + (high - low) / 2` أو `val mid = (low + high) ushr 1`.

## Practical walkthrough

كتابة خوارزمية Binary Search خالية من ثغرة الـ Integer Overflow في كوتلن:
```kotlin
fun binarySearch(sortedList: IntArray, target: Int): Int {
    var low = 0
    var high = sortedList.size - 1

    while (low <= high) {
        // ✅ تفادي طفح الأرقام الصحيحة (Integer Overflow Safe):
        val mid = low + (high - low) / 2
        val midVal = sortedList[mid]

        when {
            midVal == target -> return mid // تم العثور على العنصر بنجاح!
            midVal < target -> low = mid + 1 // الهدف في النصف الأيمن
            else -> high = mid - 1 // الهدف في النصف الأيسر
        }
    }
    return -1 // العنصر غير موجود
}
```

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

Binary search is an O(log n) search algorithm that repeatedly halves the search interval by comparing the target with the middle element. Its strict precondition is that the underlying collection must be pre-sorted and support O(1) random indexed access, such as an array.

## Interview answer — structured

Binary search is the quintessential logarithmic search algorithm:

1. **Core Mechanism**:
   - At each iteration, the algorithm inspects the middle element of the active range. If the target matches, the search concludes. If the target is smaller, the upper boundary moves to `mid - 1`; if larger, the lower boundary moves to `mid + 1`. This reduces the remaining problem space by $50\%$ at every step, yielding an $O(\log n)$ time complexity.

2. **Strict Preconditions**:
   - **Ordered Data**: The elements must be sorted according to a defined Comparator.
   - **Constant-Time Random Access**: The data structure must support $O(1)$ random indexing (`Array`, `ArrayList`, `IntArray`). Executing binary search on a `LinkedList` degrades performance to $O(n)$ because locating the midpoint requires linear traversal.

3. **Implementation Rigor**:
   - In production implementations, avoid `(low + high) / 2` due to integer overflow risks when `low + high > Int.MAX_VALUE`. Use `low + (high - low) / 2` or unsigned bit-shift `(low + high) ushr 1`.

## Interview answer — deep senior

From an Android architectural perspective, binary search underpins core framework optimizations:

1. **Android Framework SparseArray**: Android's `SparseArray<E>` and `LongSparseArray<E>` store primitive keys in a tightly packed `int[]` or `long[]`. Every `get(key)` invocation performs a binary search via `ContainerHelpers.binarySearch(mKeys, mSize, key)`. It sacrifices $O(1)$ hash table lookups for $O(\log n)$ searches to achieve zero heap object allocations.

2. **Kotlin Built-in `binarySearch` Contract**: Kotlin's `collections.binarySearch()` returns the index if found. If not found, it returns `-(insertionPoint + 1)`. This negative return value allows callers to locate the exact position where the missing element should be inserted while maintaining sorted order, enabling efficient sorted insertions.

3. **Binary Search on Answer Space**: Beyond searching static arrays, senior engineers apply binary search to find optimal configuration thresholds: e.g. finding the maximum readable font size in a custom Canvas view that fits bounded dimensions without line wrapping.

## How to answer in the interview

- **Why:** halving works only with sorted input.
- **How:** show invariant and duplicate boundary.
- **Trade-off:** sort-once cost versus repeated query gain.
- **Failure case:** wrong comparator returns false absence.
- **Production solution:** encode sortedness and test edges.

## Deep-dive talking points

Prompt for invariant, sorted comparator, random access, sort-before-search cost and duplicates.

## Follow-up questions

- **Interviewer:** "Why does calculating midpoint as `(low + high) / 2` introduce a bug?"
  **Answer:** "If `low + high` exceeds `Int.MAX_VALUE` ($2^{31} - 1$), integer overflow occurs, resulting in a negative number and an `ArrayIndexOutOfBoundsException`."

- **Interviewer:** "What does a negative return value from Kotlin's `binarySearch()` represent?"
  **Answer:** "It represents `-(insertionPoint + 1)`, indicating the item was not found but specifying the exact index where it should be inserted."

## Self-check rubric

Write the sorted-input precondition, update low/high without overflow, state O(log n) time and explain why using it on unsorted UI data returns invalid results.

## References and reviewed-on date

- [Kotlin binarySearch API](https://kotlinlang.org/api/core/kotlin-stdlib/kotlin.collections/binary-search.html) — sorted-list requirement.
- [Android performance](https://developer.android.com/topic/performance) — practical measurement.

Technically reviewed against primary documentation on 2026-10-13.
