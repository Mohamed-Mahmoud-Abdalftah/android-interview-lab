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

O(1) executes in constant time regardless of size (HashMap lookup). O(log n) halves the search space each step (binary search). O(n) scales linearly with elements (list iteration). O(n log n) is standard for efficient sorting (TimSort). O(n²) grows quadratically (nested loops or nested list contains checks), causing severe UI lag.

## Interview answer — structured

Big O notations represent fundamental algorithmic growth curves:

1. **$O(1)$ — Constant Time**:
   - Execution time is invariant to input size. Examples include direct array indexing (`array[i]`), pushing to a stack, or average-case HashMap lookups.

2. **$O(\log n)$ — Logarithmic Time**:
   - The operational problem space is divided by a constant factor (usually 2) at every iteration. Examples include binary search on a sorted collection and `SparseArray` lookups.

3. **$O(n)$ — Linear Time**:
   - Operations scale in direct proportion to input size. Examples include iterating through a list, computing a sum, or searching an unsorted array.

4. **$O(n \log n)$ — Linearithmic Time**:
   - The mathematical benchmark for optimal comparison-based sorting algorithms (TimSort, MergeSort). Common in Android when sorting UI feeds via `list.sortedBy { ... }`.

5. **$O(n^2)$ — Quadratic Time**:
   - Operations scale with the square of the input size. Typically caused by nested loops over collections, or calling `list.contains()` inside a `filter()` block. With 5,000 items, $n^2$ produces 25,000,000 operations, freezing the UI thread.

## Interview answer — deep senior

In mobile systems engineering, the inflection point where higher-order curves overtake lower-order curves depends on constants and hardware:

1. **Asymptotic Dominance vs. Small $n$**: For small datasets ($n < 20$), an $O(n^2)$ insertion sort or linear search through a contiguous array often runs faster than an $O(n \log n)$ mergesort or $O(1)$ HashMap. The high constant overhead of object allocations, hash calculation, and branch mispredictions makes simple algorithms faster for tiny datasets.

2. **The Hidden $O(n^2)$ in UI Diffing**: Android's `DiffUtil` runs Eugene Myers' diff algorithm with an average complexity of $O(n + d^2)$ where $d$ is the number of edits. If a dataset of 2,000 items changes drastically without stable IDs, DiffUtil calculation spikes on the CPU. Moving DiffUtil off the main thread to `Dispatchers.Default` (as in `ListAdapter` / `AsyncListDiffer`) prevents frame drops.

3. **Big O Exponential Danger ($O(2^n)$ / $O(n!)$)**: Algorithms with exponential complexity (unmemoized recursive backtracking or naive permission permutations) freeze client devices completely even with $n=30$. Detecting and bounding these paths via dynamic programming is critical.

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
