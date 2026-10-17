---
id: "DSA-08"
question: "How would you detect duplicates efficiently in a large list?"
topic: "Data Structures, Algorithms & Big O"
code: "DSA"
group: "B"
phase: 5
priority: "P2"
order: 447
editorial_status: "reviewed"
---

# DSA-08

## Original interview question

How would you detect duplicates efficiently in a large list?

## What the interviewer evaluates

- Expected-linear set scan versus sorting or brute force.
- Large-input memory, streaming and key-equivalence decisions.

## Concept and technical explanation

Efficient duplicate detection in large datasets requires balancing time complexity, memory allocation budgets, and collection mutability:
- Architectural Evaluation of Duplicate Detection Strategies:
  1. Naive Nested Loops (Brute Force):
     - Compares every element against every subsequent element.
     - Complexity: $O(n^2)$ Time, $O(1)$ Space.
     - Android Reality: Catastrophic anti-pattern. For a list of 50,000 items, it performs $1.25 	imes 10^9$ comparisons, freezing the main thread for several seconds and triggering an ANR dialog.
  2. Hash-Based Detection (HashSet / LinkedHashSet):
     - Inserts elements into a `HashSet` while checking return values: `set.add(item)` returns `false` if the element is already present.
     - Complexity: $O(n)$ Average Time, $O(n)$ Auxiliary Space.
     - Android Reality: The industry-standard approach for general business objects. Fast single-pass execution, but allocates `Node` wrapper objects and bucket arrays on the heap.
  3. Sort and Scan (In-Place / Monotonic):
     - Sorts the collection in $O(n \log n)$ time, then performs an $O(n)$ linear scan comparing adjacent pairs (`list[i] == list[i+1]`).
     - Complexity: $O(n \log n)$ Time, $O(1)$ to $O(n)$ Space (depending on primitive in-place array sorting).
     - Android Reality: Preferred when memory is severely constrained, avoiding thousands of object allocations on low-end devices if modifying the original list order is acceptable.
  4. BitSet Optimization (Primitive Dense Ranges):
     - If elements are non-negative integer IDs within a bounded range ($0 \le 	ext{id} \le N$), a `java.util.BitSet` tracks existence using single bits.
     - Complexity: $O(n)$ Time, $O(N / 8)$ Bytes Space. Slashing memory consumption by over $95\%$ compared to a `HashSet<Int>` by eliminating object boxing completely.

## Practical walkthrough (English)

Kotlin implementations comparing Hash-based, Sort-based, and BitSet duplicate detection:
```kotlin
// Approach 1: High-speed O(n) Hash-based duplicate finder (Best general approach)
fun <T> findDuplicatesFast(items: List<T>): Set<T> {
    val seen = HashSet<T>(items.size)
    val duplicates = HashSet<T>()
    for (item in items) {
        if (!seen.add(item)) { // add() returns false if already present
            duplicates.add(item)
        }
    }
    return duplicates
}

// Approach 2: Memory-efficient O(n log n) Sort and Scan (Zero auxiliary allocations for primitives)
fun hasDuplicatesSorted(arr: IntArray): Boolean {
    arr.sort() // In-place Dual-Pivot QuickSort
    for (i in 0 until arr.size - 1) {
        if (arr[i] == arr[i + 1]) return true
    }
    return false
}

// Approach 3: Ultra-low memory BitSet detection for bounded integer IDs
import java.util.BitSet
fun hasDuplicateIds(ids: List<Int>, maxExpectedId: Int): Boolean {
    val bitSet = BitSet(maxExpectedId + 1)
    for (id in ids) {
        if (bitSet.get(id)) return true // Duplicate found
        bitSet.set(id)
    }
    return false // Consumes 1 bit per ID instead of 24-32 bytes per Integer node!
}
```

## Explanation in Arabic

كيف تكتشف وتزيل العناصر المكررة (Duplicates) بكفاءة عالية في قائمة ضخمة في أندرويد؟

1. تحليل الخيارات الهندسية للكشف عن التكرار:
   - **الخيار 1: البحث الثنائي المتداخل (Naive Nested Loops)**:
     * مقارنة كل عنصر ببقية العناصر.
     * التعقيد: **$O(n^2)$ Time, $O(1)$ Space** — غير مقبول تماماً مع القوائم الضخمة!
   - **الخيار 2: استخدام الـ HashSet (الأسرع زمناً)**:
     * المرور على القائمة وإضافة العناصر إلى `HashSet`، أو استخدام `list.distinct()`.
     * التعقيد: **$O(n)$ Time, $O(n)$ Space**.
     * المميزات: سريع جداً ومناسب لمعظم الحالات.
     * العيب في أندرويد: يستهلك ذاكرة إضافية لكل عنصر على الـ Heap.
   - **الخيار 3: الفرز الموضعي ثم الفحص المتجاور (In-Place Sort + Linear Scan)**:
     * فرز القائمة أولاً (`list.sort()`)، ثم المرور بخطوة واحدة لمقارنة كل عنصر بمجاوره (`array[i] == array[i-1]`).
     * التعقيد: **$O(n \log n)$ Time, $O(1)$ Auxiliary Space**.
     * الاستخدام: مثالي عندما تكون الذاكرة محدودة جداً وتمنع تخصيص `Set` إضافي.

2. التعامل مع الكائنات المعقدة في أندرويد:
   - عند إزالة التكرار من قائمة نماذج (`List<Product>`) بناءً على المعرف (`id`) فقط، نستخدم `distinctBy { it.id }` التي تحتفظ بأول عنصر ظهر فقط.

## Practical walkthrough

طرق كوتلن الفعالة لاكتشاف وإزالة التكرار مع الحفاظ على الأداء والذاكرة:
```kotlin
data class User(val id: Long, val name: String)

// 1. الطريقة الأسرع والأكثر شيوعاً (O(n) time, O(n) space):
fun removeDuplicatesFast(users: List<User>): List<User> {
    return users.distinctBy { it.id }
}

// 2. الكشف عن المكررات فقط وحفظها (O(n) time, O(n) space):
fun findDuplicates(items: List<String>): Set<String> {
    val seen = HashSet<String>()
    val duplicates = HashSet<String>()
    for (item in items) {
        if (!seen.add(item)) {
            duplicates.add(item) // تم رصده مسبقاً، إذاً هو مكرر!
        }
    }
    return duplicates
}

// 3. الطريقة الصديقة للذاكرة الصارمة (O(n log n) time, O(1) extra space):
fun removeDuplicatesInPlace(primitiveIds: LongArray): Int {
    primitiveIds.sort() // فرز موضعي O(n log n)
    if (primitiveIds.isEmpty()) return 0
    var uniqueIndex = 0
    for (i in 1 until primitiveIds.size) {
        if (primitiveIds[i] != primitiveIds[uniqueIndex]) {
            uniqueIndex++
            primitiveIds[uniqueIndex] = primitiveIds[i]
        }
    }
    return uniqueIndex + 1 // عدد العناصر الفريدة، بدون تخصيص أي كائن على الـ Heap!
}
```

## Why it matters and how it works

HashSet uses hash/equality; equality semantics determine duplicates. For a stream larger than memory, use bounded external sort or database uniqueness/index and pagination. Approximate filters can reduce I/O but cannot prove absence without confirmation.

## Worked example

Illustrative Kotlin: `val seen = HashSet<String>(); val firstDuplicate = ids.firstOrNull { !seen.add(it) }`. Assumes IDs are normalized and memory fits. In Room, a unique index can enforce no duplicate persisted IDs across concurrent writers.

For an unsorted stream, keep only seen values and stop at the first repeated value in input order. The map/set memory cost is the trade-off; for unbounded data use a bounded window or a durable external index with an explicit definition of “duplicate.”

```kotlin
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

private fun firstRepeated(ids: Iterable<String>): String? {
    val seen = HashSet<String>()
    for (id in ids) if (!seen.add(id)) return id
    return null
}

class DuplicateDetectionExampleTest {
    @Test fun inputOrderAndNoDuplicate() {
        assertEquals("a", firstRepeated(listOf("a", "b", "a", "b")))
        assertEquals(null, firstRepeated(listOf("a", "b")))
    }
}
```

## Trade-offs and decision criteria

Set gives fast expected detection but retains keys. Sorting can use less extra memory if in-place sorting is allowed, but changes order and costs more CPU. DB uniqueness moves enforcement to durable boundary.

## Failure modes

Using mutable data class as set key then mutating it breaks hash lookup. Normalization mismatch (`abc` versus `ABC`) may hide logical duplicates. In concurrent updates, a client-side set is not an atomic uniqueness guarantee.

## Production perspective

For an Android import, normalize IDs, check memory budget, use a DB unique constraint for durable writes and report duplicate count safely without logging personal data.

## Interview answer — short

Detect duplicates efficiently in O(n) time using a HashSet, which flags duplicates in a single pass when add() returns false. If heap memory is constrained, sorting the list in O(n log n) and scanning adjacent items avoids object allocations. For bounded integer IDs, a BitSet provides linear time detection while reducing memory footprint by over 95% compared to object sets.

## Interview answer — structured

Selecting an optimal duplicate detection strategy depends on data size, available heap memory, and item types.
For general business objects, the industry standard is using a HashSet. By iterating through the collection in a single pass, we inspect the boolean result of set.add(item). If it returns false, a duplicate is instantly detected, achieving linear O(n) time complexity at the cost of O(n) auxiliary memory.
When heap memory is severely constrained on low-end Android devices, allocating thousands of HashSet nodes can trigger garbage collection pauses. An effective alternative is in-place sorting, executing in O(n log n) time followed by a linear scan checking adjacent elements, which eliminates auxiliary node allocations.
For datasets consisting of bounded integer IDs, such as user or product identifiers, utilizing a BitSet provides the ultimate mobile optimization. It achieves O(n) linear detection while storing each identifier as a single bit rather than a boxed thirty-two-byte object, slashing memory consumption by ninety-five percent.

## Interview answer — deep senior

From an algorithmic efficiency and mobile memory optimization standpoint, duplicate detection in large Android datasets requires evaluating the operational constraints of the runtime environment.
A naive double loop comparing all pairs represents an unacceptable O of n squared failure mode that freezes the main thread and risks ANR terminations for datasets exceeding a few thousand items. The standard production solution is single-pass hash filtering. By iterating through the collection, we leverage the O of one average insertion time of HashSet. The set.add() method returns a boolean indicating whether the element was already present, allowing us to identify duplicates in pure O of n linear time.
However, in memory-sensitive Android environments, a HashSet of fifty thousand objects carries substantial hidden overhead. Each entry requires an internal Node object, integer boxing if handling primitive IDs, and a hash bucket array, consuming several megabytes of heap space and triggering ART garbage collection churn.
To address memory constraints, senior engineers deploy domain-specific optimizations. If sorting the input data is permissible, we utilize in-place sorting. Sorting primitive arrays runs in O of n log n time with zero auxiliary heap allocation, followed by a linear scan comparing adjacent indices.
Furthermore, if the data consists of dense positive integer identifiers, such as catalog SKU numbers, we deploy java.util.BitSet. A BitSet represents existence using individual bits in a long array. Checking fifty thousand identifiers consumes less than seven kilobytes of memory, compared to over one megabyte for a HashSet of boxed Integers. This eliminates object allocations, prevents garbage collection stutter, and maintains optimal 120fps scrolling smoothness.

## How to answer in the interview

- **Why:** duplicate scans can become quadratic.
- **How:** use seen set and define first repeated semantics.
- **Trade-off:** linear memory versus sorting or nested scans.
- **Failure case:** unbounded set leaks memory.
- **Production solution:** bounded window or server uniqueness contract.

## Deep-dive talking points

Prompt for equality definition, HashSet memory, sort trade-off, streaming and durable constraint.

## Follow-up questions

- **Interviewer:** "Why is `BitSet` superior to `HashSet<Int>` for deduplicating bounded integer IDs?"
  **Answer:** "A BitSet uses a single bit per integer, consuming a fraction of the RAM (125KB for 1M IDs) with zero object boxing or GC overhead."

- **Interviewer:** "How does `sequence.distinct()` improve performance over `list.distinct()` on huge datasets?"
  **Answer:** "Sequences evaluate lazily, evaluating items on-demand and preventing large intermediate list copies from cluttering the heap."

## Self-check rubric

Compare a hash-set scan with sorting for duplicate detection; state expected time and extra memory, preserve first-duplicate semantics if required, and test empty and large inputs.

## References and reviewed-on date

- [Kotlin set operations](https://kotlinlang.org/docs/set-operations.html) — set semantics.
- [Room indices](https://developer.android.com/training/data-storage/room/defining-data) — unique indexed storage.

Technically reviewed against primary documentation on 2026-10-13.
