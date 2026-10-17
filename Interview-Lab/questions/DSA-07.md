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

## Concept and technical explanation

Binary search is an optimal divide-and-conquer search algorithm that executes in logarithmic time by repeatedly partitioning the search space:
- Algorithmic Mechanics:
  - Compares the target value against the middle element of a candidate range.
  - If target equals the midpoint, the search terminates immediately.
  - If target is smaller, the search range is restricted to the lower half; if larger, to the upper half.
  - Halves the candidate search space in each iteration, yielding an $O(\log n)$ time complexity and $O(1)$ auxiliary space for iterative implementations.
- Mandatory Preconditions:
  - Strict Ordering (Monotonicity): The collection must be pre-sorted in ascending or descending order according to the search comparator.
  - Fast Random Access ($O(1)$ Indexing): The data structure must support constant-time element retrieval by index (such as `Array`, `IntArray`, or `ArrayList`). If attempted on a `LinkedList`, navigating to the midpoint requires $O(n)$ pointer traversal, degrading overall binary search performance to a sluggish $O(n)$ while adding logarithmic overhead.
- Critical Implementation Traps:
  - Integer Overflow Bug: Computing `val mid = (low + high) / 2` causes 32-bit signed integer overflow when `low + high > Int.MAX_VALUE` (2,147,483,647), yielding a negative index and triggering `ArrayIndexOutOfBoundsException`. The safe implementation uses `low + (high - low) / 2` or unsigned bit shift `(low + high) ushr 1`.
  - Infinite Loops on Boundary Updates: Updating bounds with `low = mid` or `high = mid` can cause infinite loops when candidate range length is two. Boundaries must advance strictly with `low = mid + 1` and `high = mid - 1`.
- Kotlin Standard Library Integration:
  - `Collections.binarySearch()` returns the non-negative index if the key is found. If missing, it returns `(-insertion_point - 1)`, providing callers the exact index where the element should be inserted to maintain sorted order.

## Practical walkthrough (English)

Safe Kotlin implementation of binary search and standard library integration:
```kotlin
// Robust binary search implementation preventing integer overflow
fun <T : Comparable<T>> binarySearchSafe(list: List<T>, target: T): Int {
    var low = 0
    var high = list.size - 1

    while (low <= high) {
        // Safe midpoint calculation using unsigned right bit shift
        val mid = (low + high) ushr 1
        val midVal = list[mid]
        val cmp = midVal.compareTo(target)

        when {
            cmp < 0 -> low = mid + 1
            cmp > 0 -> high = mid - 1
            else -> return mid // Key found
        }
    }
    // Key not found; returns inverted insertion point
    return -(low + 1)
}

// Utilizing Kotlin standard library binary search
fun findProductPosition(sortedIds: List<Long>, targetId: Long): Int {
    val index = sortedIds.binarySearch(targetId)
    if (index >= 0) {
        println("Found product at index: $index")
    } else {
        val insertionPoint = -index - 1
        println("Missing product should be inserted at index: $insertionPoint")
    }
    return index
}
```

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

Binary search is a divide-and-conquer algorithm operating in O(log n) time by halving the search space each step. Its mandatory preconditions are that the collection must be pre-sorted and support O(1) random access by index. Midpoints must be computed safely using unsigned bit shifts to prevent integer overflow, and boundary updates must advance past mid to avoid infinite loops.

## Interview answer — structured

Binary search is an exceptionally efficient search algorithm designed to find elements in logarithmic time.
The algorithm operates on the divide-and-conquer principle, comparing the search target against the middle element of a candidate range and discarding half the remaining elements in each pass. This delivers an O(log n) time complexity, requiring only twenty comparisons to locate a record among one million items.
However, binary search imposes two mandatory preconditions. First, the collection must be sorted according to the comparison key. Second, the underlying data structure must support constant-time O(1) random access, such as an Array or ArrayList. Running binary search over a LinkedList fails to achieve logarithmic performance because finding the middle node requires an O(n) sequential traversal.
A classic pitfall is computing the midpoint as low plus high divided by two, which overflows thirty-two-bit integers for large datasets. Safe implementations compute mid using an unsigned right bit shift, advancing boundaries strictly past the midpoint to prevent infinite loops.

## Interview answer — deep senior

From an algorithmic verification and low-level runtime perspective, binary search exemplifies how mathematical elegance collides with physical hardware limits.
The theoretical foundation of binary search relies on monotonicity. By inspecting the midpoint element, the algorithm eliminates half of the search interval in every comparison step. For a list of one million elements, binary search terminates in at most twenty steps, compared to one million steps for a linear scan.
However, achieving this O of log n guarantee requires strict adherence to architectural preconditions. The most overlooked requirement is constant-time indexing. On a contiguous array or ArrayList, accessing list of mid is an instantaneous O of one memory read. If an engineer naively invokes binary search on a LinkedList, traversing to the middle node requires pointer chasing that takes O of n time at every recursive step, degrading the algorithm into a clumsy O of n log n process that runs slower than a simple linear scan.
Furthermore, writing a bug-free binary search is notoriously difficult due to edge-case mechanics. For decades, standard implementations contained an integer overflow bug: computing low plus high divided by two overflows signed thirty-two-bit integer limits when array sizes exceed one billion, producing negative indices that crash the process. The correct implementation calculates mid as low plus high minus low divided by two, or utilizes the unsigned right shift operator ushr one.
Finally, Kotlin standard library integration provides powerful semantic guarantees. When binarySearch fails to find an item, it returns negative insertion point minus one. In an Android UI displaying sorted chat messages or transaction ledgers, this return value allows developers to insert new entries at their exact sorted position in O of n time without triggering an expensive full-collection re-sort.

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
