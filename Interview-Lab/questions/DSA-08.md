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

Detect duplicates in O(n) time and O(n) space by inserting elements into a HashSet, where set.add() returning false identifies a duplicate. For memory-constrained environments where allocating a Set would risk OOM, sort the collection in-place in O(n log n) time and scan adjacent elements in O(1) auxiliary space.

## Interview answer — structured

Deduplicating large collections involves choosing between time-optimized and memory-constrained paradigms.

First, **Time-Optimized Hash Table Approach ($O(n)$ Time, $O(n)$ Space)**. Next, iterate through the list while streaming elements into a `HashSet`. Since `HashSet.add()` returns `false` if the item already exists, duplicates are detected in a single linear pass. In Kotlin, `list.distinct()` or `list.distinctBy { it.id }` encapsulates this pattern.
**Memory-Constrained Sorting Approach ($O(n \log n)$ Time, $O(1)$ Space)**. If working with a huge dataset on a memory-constrained Android device where allocating a 100,000-entry HashSet would trigger an `OutOfMemoryError`, sort the primitive array in-place using dual-pivot quicksort, then run a single two-pointer linear pass comparing adjacent neighbors (`arr[i] == arr[i-1]`).
**Preserving Insertion Order**. Finally, if the original order of first appearance must be preserved, Kotlin's `distinct()` uses a `LinkedHashSet` internally, retaining first-seen ordering while filtering subsequent occurrences.


## Interview answer — deep senior

In large scale mobile architecture, deduplicating incoming server data feeds presents practical challenges.

First, with Stream Processing via Kotlin Sequences, for massive datasets read from Room or local files, calling `list.distinct()` creates intermediate collection allocations in memory. Using lazy sequences (`sequence.distinct()`) processes items one-by-one, streaming deduplicated records directly to the UI without holding the entire transformed dataset in heap memory simultaneously. Next, with BitSet Optimization for Bounded Numeric IDs, if the dataset consists of integer IDs within a bounded range (e.g. User IDs $< 1,000,000$), avoid `HashSet<Int>` completely. A Java `BitSet` stores one bit per ID: 1,000,000 IDs consume just $125\text{KB}$ of RAM compared to over $32\text{MB}$ for a boxed `HashSet<Integer>`, yielding instant duplicate detection with negligible GC footprint.
Finally, with Probabilistic Deduplication with Bloom Filters, in extreme offline synchronization scenarios where hundreds of thousands of sync IDs must be checked before querying disk, a Bloom Filter provides $O(1)$ constant-time duplicate checks in minimal RAM with zero false negatives.


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
