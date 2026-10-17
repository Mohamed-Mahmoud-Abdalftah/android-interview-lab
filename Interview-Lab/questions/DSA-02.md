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

## Concept and technical explanation

Asymptotic growth tiers categorize how algorithms scale under expanding input sizes:
- $O(1)$ — Constant Time:
  - Execution duration remains invariant regardless of input size $n$.
  - Android Examples: Array indexing (`list[index]`), accessing a `HashMap` key on average, pushing/popping from an `ArrayDeque`, or reading a primitive variable.
- $O(\log n)$ — Logarithmic Time:
  - Execution steps increase logarithmically; the problem search space is halved in each step. Highly efficient and scalable.
  - Android Examples: Binary search in a sorted array or list (`binarySearch()`), operations on balanced binary search trees (e.g., Red-Black trees in `TreeMap`).
- $O(n)$ — Linear Time:
  - Execution duration scales in direct 1:1 proportion to input size $n$.
  - Android Examples: Iterating through an unindexed list (`for (item in list)`), finding minimum/maximum elements, linear filtering (`list.filter { ... }`), sequential JSON parsing, and standard layout passes measuring children.
- $O(n \log n)$ — Linearithmic Time:
  - Standard complexity for comparison-based divide-and-conquer sorting algorithms. Breaks the input into $\log n$ recursive levels and performs $O(n)$ work at each level.
  - Android Examples: Kotlin standard library sorting (`list.sorted()`, TimSort), MergeSort, and QuickSort average case. Essential for sorting catalog items before display.
- $O(n^2)$ — Quadratic Time:
  - Execution duration grows with the square of the input size, typically caused by nested loops over the same dataset.
  - Android Examples: Naive nested iteration comparing every item against every other item (e.g., duplicate detection without a Set), BubbleSort, and accidental nested iterations within `RecyclerView.Adapter.onBindViewHolder`.

## Practical walkthrough (English)

Kotlin implementations illustrating the five core complexity classes:
```kotlin
// 1. O(1) Constant Time: Direct index lookup
fun getFirstItem(items: List<String>): String? = items.firstOrNull()

// 2. O(log n) Logarithmic Time: Binary search on sorted array
fun binarySearchPrice(sortedPrices: IntArray, target: Int): Int {
    var low = 0
    var high = sortedPrices.size - 1
    while (low <= high) {
        val mid = (low + high) ushr 1
        val midVal = sortedPrices[mid]
        when {
            midVal < target -> low = mid + 1
            midVal > target -> high = mid - 1
            else -> return mid // Key found
        }
    }
    return -1
}

// 3. O(n) Linear Time: Single pass filtering
fun filterActiveUsers(users: List<User>): List<User> = users.filter { it.isActive }

// 4. O(n log n) Linearithmic Time: Sorting list
fun sortProductsByPrice(products: List<Product>): List<Product> = products.sortedBy { it.price }

// 5. O(n^2) Quadratic Time: Nested loops comparison (Anti-pattern for large lists)
fun findCommonItemsNaive(listA: List<String>, listB: List<String>): List<String> {
    val common = mutableListOf<String>()
    for (a in listA) {
        for (b in listB) { // Nested iteration creates O(n * m) or O(n^2)
            if (a == b) common.add(a)
        }
    }
    return common
}
```

## Explanation in Arabic

اشرح بالتفصيل مع أمثلة عملية من أندرويد التعقيدات الزمنية الشائعة: $O(1)$، $O(\log n)$، $O(n)$، $O(n \log n)$، و $O(n^2)$؟

1. التعقيدات الزمنية من الأسرع إلى الأبطأ:
   - **$O(1)$ - Constant Time (وقت ثابت)**:
     * زمن التنفيذ مستقل تماماً عن حجم البيانات. مثال في أندرويد: جلب عنصر من مصفوفة عبر الـ Index (`array[0]`)، أو قراءة قيمة من `HashMap` بالـ Key عبر الـ Hash Code.
   - **$O(\log n)$ - Logarithmic Time (وقت لوغاريتمي)**:
     * يقسم حجم البيانات إلى النصف في كل خطوة. سريع جداً حتى مع ملايين العناصر. مثال: البحث الثنائي (Binary Search)، أو البحث في `SparseArray` على أندرويد.
   - **$O(n)$ - Linear Time (وقت خطي)**:
     * ينمو الزمن طردياً مع حجم البيانات. مثال: حلقة تكرار بسيطة للمرور على قائمة عناصر، أو فلترة قائمة مستخدمين (`list.filter { it.isActive }`).
   - **$O(n \log n)$ - Linearithmic Time**:
     * التعقيد الأمثل لخوارزميات الفرز المقارن العامة. مثال: خوارزمية الفرز المدمجة في كوتلن (`list.sorted()`) التي تعتمد على TimSort أو Dual-Pivot Quicksort.
   - **$O(n^2)$ - Quadratic Time (وقت تربيعي)**:
     * ينمو الزمن بشكل تربيعي؛ خطير جداً مع القوائم الكبيرة! مثال: حلقتان تكرار متداخلتان تفحص كل عنصر مقابل بقية العناصر، أو كتابة `listA.filter { itemA -> listB.contains(itemA) }` حيث كلتا القائمتين `List` عادية.

## Practical walkthrough

أمثلة كود كوتلن تقارن بين هذه التعقيدات في معالجة بيانات شائعة:
```kotlin
// 1. O(1) - Constant: قراءة مباشرة من الخريطة
val user = userCacheMap[userId] // O(1) average

// 2. O(log n) - Logarithmic: بحث ثنائي في قائمة مرتبة
val index = sortedIds.binarySearch(targetId) // O(log n)

// 3. O(n) - Linear: عملية بحث خطي أو تحويل مباشر
val names = users.map { it.fullName } // O(n)

// 4. O(n log n) - Linearithmic: فرز قائمة المنتجات حسب السعر
val sortedProducts = products.sortedBy { it.price } // O(n log n)

// 5. O(n^2) - Quadratic (كارثة شائعة في أندرويد!):
// إذا كان حجم القائمتين 10,000 عنصر، فهذا السطر ينفذ 100,000,000 مقارنة!
val commonUsers = listA.filter { userA -> listB.contains(userA) } // O(n * m) -> O(n^2)

// ✅ الإصلاح لتحويله إلى O(n):
val setB = listB.toHashSet() // O(m) space and time
val efficientCommon = listA.filter { userA -> setB.contains(userA) } // O(n * 1) -> O(n)
```

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

O(1) executes in constant time regardless of size, O(log n) halves the search space each step like binary search, O(n) inspects every item linearly, O(n log n) represents optimal comparison sorting like TimSort, and O(n^2) grows quadratically via nested loops. Senior engineers select data structures that keep operations at O(1) or O(log n) to prevent UI frame starvation.

## Interview answer — structured

The core Big O complexity classes define how algorithm performance scales as dataset sizes increase.
Constant time O(1) represents operations that execute in a fixed number of steps, such as accessing an element by index in an array or average HashMap lookups. Logarithmic time O(log n) represents algorithms that divide the problem space in half with every step, exemplified by binary search in a sorted array, making it exceptionally fast even for millions of records.
Linear time O(n) means processing time increases proportionally with the input count, seen in single-pass iterations, linear searches, and JSON parsing. Linearithmic time O(n log n) is the benchmark for efficient sorting algorithms like TimSort, used internally by Kotlin collections, which divides the data and merges it linearly.
Quadratic time O(n^2) indicates algorithms where execution steps multiply quadratically, typically seen in nested loops comparing items against each other. In Android development, avoiding quadratic operations on the main thread is essential to prevent severe visual Jank and keep rendering within 16-millisecond frame budgets.

## Interview answer — deep senior

From a computational complexity and runtime performance engineering perspective, these five complexity classes represent distinct scalability profiles that dictate whether code is viable for production mobile devices.
In Android systems, O(1) operations are our foundational building blocks. Array index lookups and average-case HashMap lookups provide predictable, sub-microsecond latency. However, senior engineers understand the hidden overheads: while an unboxed array access is pure O(1) with zero allocations, a HashMap get operation involves hash code calculation, bucket indexing, and potential linked-node pointer chasing that incurs CPU cache misses.
Logarithmic algorithms like binary search offer dramatic scalability advantages. Searching through a sorted catalog of one million items requires approximately twenty comparisons, making it millions of times faster than an O(n) sequential scan. This makes maintaining sorted lists and binary indexing vital when designing local Room queries or in-memory caches.
Linear algorithms represent the standard expectation for data processing pipelines, such as mapping or filtering network DTOs into domain models. While acceptable for modest datasets, chaining multiple linear operations without Sequences introduces hidden allocations that degrade performance.
Linearithmic complexity O(n log n) is the mathematical lower bound for comparison sorting. Kotlin standard collections employ TimSort, an adaptive algorithm combining MergeSort and InsertionSort that exploits existing ordered runs, executing in linear time on nearly-sorted data.
Finally, quadratic complexity O(n^2) is an absolute anti-pattern on UI rendering paths. A classic failure mode in Android occurs when an engineer performs an O(n) search inside a RecyclerView onBindViewHolder callback or a Compose item row. Because the adapter binds n items, the overall screen rendering degrades into an accidental O(n^2) operation, causing dropped frames and severe stutter. Mastering these classifications enables engineers to proactively refactor algorithms before code reaches production devices.

## How to answer in the interview

- **Why:** growth predicts user-facing scaling.
- **How:** tie each class to a concrete operation.
- **Trade-off:** fast expected case versus worst-case assumptions.
- **Failure case:** nested scan repeats per row.
- **Production solution:** measure call frequency and input size.

## Deep-dive talking points

Prompt for doubling intuition, hidden work, sorted precondition and practical crossover.

## Follow-up questions

- **Interviewer:** "How can calling `listA.filter { listB.contains(it) }` degrade to $O(n^2)$?"
  **Answer:** "Because `List.contains()` is an $O(n)$ linear scan; doing that for every element in `listA` creates $n \times n = O(n^2)$ comparisons."

- **Interviewer:** "What is the time complexity of Kotlin's built-in `sortedBy` function?"
  **Answer:** "It is $O(n \log n)$ on average and worst case, backed by TimSort."

## Self-check rubric

Give one growth example for each listed class, compare n and 10n behavior, and explain why an O(n log n) implementation may still lose on tiny inputs.

## References and reviewed-on date

- [Kotlin collections overview](https://kotlinlang.org/docs/collections-overview.html) — collection operations.
- [Android performance](https://developer.android.com/topic/performance) — measurement context.

Technically reviewed against primary documentation on 2026-10-13.
