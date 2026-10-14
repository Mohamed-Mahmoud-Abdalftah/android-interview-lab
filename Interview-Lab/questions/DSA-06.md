---
id: "DSA-06"
question: "What are average and worst-case HashMap lookup complexities?"
topic: "Data Structures, Algorithms & Big O"
code: "DSA"
group: "A"
phase: 5
priority: "P2"
order: 445
editorial_status: "reviewed"
---

# DSA-06

## Original interview question

What are average and worst-case HashMap lookup complexities?

## What the interviewer evaluates

- Expected versus pathological lookup cost.
- Hash quality, resizing and Android memory implications.

## Explanation in Arabic

ما هو التعقيد الزمني لعمليات البحث في الـ HashMap في الحالة المتوسطة (Average Case) والحالة الأسوأ (Worst Case)، ولماذا؟

1. كيف تعمل الـ HashMap في الذاكرة؟
   - تعتمد على مصفوفة داخلية من الـ Buckets.
   - عند البحث عن مفتاح (`get(key)`):
     1. تحسب الـ Hash Code للمفتاح: `hash = key.hashCode()`.
     2. تحدد موقع الـ Bucket: `index = hash & (n - 1)`.
     3. تفحص العناصر الموجودة داخل الـ Bucket لمطابقة المفتاح عبر `equals()`.

2. الحالة المتوسطة (Average Case: $O(1)$):
   - عندما تكون دالة الـ `hashCode()` جيدة وموزعة بانتظام، تتوزع المفاتيح بالتساوي عبر الـ Buckets.
   - معظم الـ Buckets تحتوي على عنصر واحد فقط (بدون تصادمات أو تصادمات ضئيلة جداً $O(1)$)، ويتم العثور على القيمة فوراً في وقت ثابت $O(1)$.

3. الحالة الأسوأ (Worst Case):
   - **في Java 7 والإصدارات القديمة ($O(n)$)**:
     * إذا أنتجت جميع المفاتيح نفس الـ Hash Code تماماً (Pathological Collisions)، تتجمع كل العناصر داخل Bucket واحد كـ Linked List طويلة. البحث عن عنصر يتطلب المرور الخطي على جميع العناصر $O(n)$!
   - **في Java 8 وما بعدها على أندرويد ($O(\log n)$)**:
     * عند تجاوز عدد التصادمات داخل الـ Bucket الواحد عتبة معينة (TREEIFY_THRESHOLD = 8)، تتحول القائمة المرتبطة تلقائياً إلى **شجرة حمراء-سوداء متوازنة (Red-Black Tree)**، مما يضمن أن أسوأ تعقيد للبحث لن يتجاوز $O(\log n)$.

## Practical walkthrough

مثال عملي يوضح كيف يمكن لكود Kotlin سيئ أن يدمر أداء الـ HashMap ويحولها لـ $O(n)$ أو $O(\log n)$:
```kotlin
// ❌ كارثة: دالة hashCode تعيد نفس الرقم دائماً (تصادم 100%!):
class BadKey(val id: String) {
    override fun hashCode(): Int = 42 // كل المفاتيح تذهب لنفس الـ Bucket!
    override fun equals(other: Any?): Boolean = (other as? BadKey)?.id == id
}

// ✅ التصميم الهندسي الصحيح: توزيع متجانس للمفاتيح:
data class GoodKey(val id: String) {
    // Kotlin Data Class تولد hashCode() ممتاز يوزع المفاتيح بانتظام عبر الـ Buckets:
    // مما يضمن أداء بحث O(1) حقيقي في 99.9% من الحالات.
}

fun benchmark() {
    val badMap = HashMap<BadKey, String>()
    // إضافة 10,000 عنصر هنا سيجعل البحث بطيئاً جداً (O(log n) بدلاً من O(1))
}
```

## Why it matters and how it works

A hash code selects a bucket and equality distinguishes keys. Collision chains/probing and table growth determine actual cost; exact worst-case varies by JVM/Android implementation, so do not promise universal tree-bin behavior. Kotlin `HashMap` on JVM delegates to platform implementation.

## Worked example

Build `associateBy { it.id }` once for 10k products, then lookups are expected constant. Rebuilding that map inside every item rendering costs O(n) per row and becomes O(n²) overall. Keep the index at a stable data layer and update when source changes.

## Trade-offs and decision criteria

A map trades memory and build cost for repeated lookup speed. For a tiny list or one lookup, linear scan may be simpler/faster. Ordered maps have different complexity and guarantees.

## Failure modes

Mutable key fields change hash/equality after insertion, making lookup fail. Bad hashCode with all keys same causes collision hotspot. Use immutable stable keys and test realistic distributions.

## Production perspective

Profile lookup and allocations on low-end devices; do not place expensive reindexing inside recomposition. Bound cache size and handle concurrency at repository level.

## Interview answer — short

HashMap lookup is O(1) on average because a well-distributed hashCode maps keys directly to unique bucket indices. In the worst case with high collisions, Java 7 degrades to O(n) via linked lists, while modern Java 8+ and Android ART caps worst-case lookup at O(log n) by converting buckets exceeding 8 nodes into balanced Red-Black trees.

## Interview answer — structured

The performance characteristics of HashMap lookups derive from hash table bucket distribution.

First, **Average Case — $O(1)$**. Next, when keys provide a uniform hash distribution, computing `key.hashCode()` and modulating it against bucket array size yields a deterministic index. Because each bucket contains approximately $\le 1$ element on average (governed by the load factor, typically 0.75), retrieving the entry takes constant time $O(1)$.
**Worst Case in Java 7 — $O(n)$**. If all keys hash to the identical bucket index due to poor hash functions or deliberate hash collision attacks, all entries are stored in a single linked list. Finding an element requires linear traversal comparing keys via `equals()`, degrading lookup to $O(n)$.
**Worst Case in Java 8+ / Modern ART — $O(\log n)$**. Finally, to prevent catastrophic degradation, modern runtimes introduce **bucket treeification**. When a bucket exceeds 8 entries (`TREEIFY_THRESHOLD`) and the table exceeds 64 buckets, the bucket converts from a singly-linked list into a balanced Red-Black tree (`TreeNode`), capping worst-case search complexity at $O(\log n)$.


## Interview answer — deep senior

From an Android performance and memory optimization standpoint, several nuances govern HashMaps.

First, with The Rehash Resize Penalty, when the number of entries exceeds `capacity * loadFactor` (e.g. 16 * 0.75 = 12 entries), HashMap doubles its internal bucket array (e.g. 16 to 32) and rehashes every existing entry into new bucket positions. If inserting 100,000 items without an initial capacity, the map resizes ~14 times, producing massive garbage and execution spikes. Always specify initial capacity: `HashMap(expectedSize / 0.75f + 1)`. Next, with Mutable Key Mutation Trap, if an object is used as a HashMap key and its mutable properties change after insertion, its `hashCode()` changes. Calling `map[key]` computes a new bucket index, rendering the previously inserted value permanently unfindable (a silent memory leak).
Finally, a Memory Footprint is a standard `HashMap` entry requires a `Node` object with 4 references (hash, key, value, next), taking 32 bytes on 64-bit ART plus the key and value objects themselves. For integer keys, `SparseArray` cuts this memory by over 60%.


## How to answer in the interview

- **Why:** hashing trades space for lookup speed.
- **How:** explain bucket/hash/equality and assumptions.
- **Trade-off:** expected speed versus collision and memory.
- **Failure case:** mutable key becomes unreachable.
- **Production solution:** use stable keys and profile hot path.

## Deep-dive talking points

Prompt for bucket/equality mechanics, index build cost, mutable key failure and implementation caveat.

## Follow-up questions

- **Interviewer:** "Why should you pass an initial capacity to a HashMap when the expected size is known?"
  **Answer:** "To prevent repeated bucket array doubling and rehashing passes, reducing CPU time and memory allocation churn."

- **Interviewer:** "What happens if you mutate an object that is used as a key in a HashMap?"
  **Answer:** "Its hashCode changes, meaning lookups will check the wrong bucket and fail to find the entry, causing data loss and memory leaks."

## Self-check rubric

State expected O(1) lookup under good hashing and collision behavior, explain a pathological degradation, and describe how equality/hashCode bugs can break correctness before speed.

## References and reviewed-on date

- [Kotlin Map API](https://kotlinlang.org/api/core/kotlin-stdlib/kotlin.collections/-map/) — map contract.
- [Android performance](https://developer.android.com/topic/performance) — runtime profiling.

Technically reviewed against primary documentation on 2026-10-13.
