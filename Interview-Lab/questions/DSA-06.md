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

## Concept and technical explanation

The lookup complexity of a HashMap depends on the distribution uniformity of its hashing function and collision resolution mechanisms:
- Average-Case Lookup Complexity: $O(1)$ Constant Time:
  - When keys exhibit uniform hash code distribution across the underlying bucket array.
  - The lookup hashes the key, computes the bucket index via bitwise masking (`hash & (table.length - 1)`), and directly retrieves the single stored node.
- Worst-Case Lookup Complexity:
  - Without Treeification (Legacy Java/Android): $O(n)$ Linear Time. If all keys collide into the exact same bucket, the bucket degenerates into an unindexed linked list requiring linear traversal.
  - With Treeification (Java 8+ and modern Android ART): $O(\log n)$ Logarithmic Time. When collisions in a single bucket exceed the treeification threshold (`TREEIFY_THRESHOLD = 8`) and total table capacity reaches at least 64, the linked list converts into a balanced Red-Black Tree (`TreeNode`), bounding worst-case searches to $O(\log n)$.
- Root Causes of Worst-Case Collisions:
  - Pathological `hashCode()` Implementations: Returning a constant value (e.g., `override fun hashCode(): Int = 42`) forces all entries into bucket zero.
  - Adversarial Collisions (HashDoS Attacks): Malicious actors sending network payloads engineered with identical hashes to freeze backend parsers or client JSON processing.
- Amortized Rehashing Costs:
  - When total entries exceed the threshold (`capacity * loadFactor`, typically $0.75$), HashMap allocates a new array of double the size ($2 	imes$) and rehashes all elements in an $O(n)$ operation.
  - Android Best Practice: Pre-sizing HashMaps (`HashMap(expectedCount / 0.75f + 1)`) prevents expensive runtime rehashing cycles during JSON parsing or data synchronization.

## Practical walkthrough (English)

Demonstrating pathological hash degradation and pre-sized initialization:
```kotlin
// Demonstrating the impact of a degenerate hashCode implementation
data class BrokenKey(val id: String) {
    // ANTI-PATTERN: Forces all keys into the same bucket, degrading lookups to O(log n) or O(n)
    override fun hashCode(): Int = 42
    override fun equals(other: Any?): Boolean = other is BrokenKey && other.id == this.id
}

fun demonstrateHashMapBehavior() {
    val count = 10_000

    // Best Practice: Pre-size HashMap to avoid expensive O(n) rehashing
    // Default load factor is 0.75f -> capacity = (count / 0.75) + 1
    val initialCapacity = (count / 0.75f).toInt() + 1
    val optimizedMap = HashMap<String, String>(initialCapacity)

    for (i in 0 until count) {
        optimizedMap["key_$i"] = "value_$i" // No rehashing pauses occur
    }

    // Average-case lookup: O(1)
    val fastLookup = optimizedMap["key_5000"]
}
```

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

HashMap lookup executes in O(1) average time when hash distributions are uniform. In worst-case pathological collision scenarios, complexity degrades to O(n) in legacy lists, or O(log n) in modern ART/Java 8+ via Red-Black tree conversion. Senior engineers write robust hashCode implementations and pre-size maps to prevent expensive O(n) runtime rehashing cycles.

## Interview answer — structured

The lookup complexity of a HashMap hinges on hash distribution uniformity and bucket collision management.
In the average case, HashMap delivers constant-time O(1) performance. The key hash code is masked against the bucket array length to identify the index, retrieving the value in a single step without collision traversal.
In the worst case, where multiple keys hash to the same bucket index, performance degrades. In older runtimes, buckets maintained simple linked lists, resulting in O(n) linear search degradation. Modern Android runtimes inherit Java 8 treeification: when a bucket accumulates more than eight colliding nodes and the map capacity reaches sixty-four, the linked list converts into a balanced Red-Black tree, improving worst-case search complexity to O(log n).
Additionally, HashMaps undergo an O(n) rehashing cycle whenever entries exceed the seventy-five percent load factor. In Android production apps, pre-allocating HashMap capacity based on expected item counts eliminates runtime array resizing and reduces garbage collection churn.

## Interview answer — deep senior

From an algorithmic internals and systems security perspective, HashMap lookup mechanics reveal the critical interplay between software contracts and hardware efficiency.
Under optimal conditions, HashMap achieves theoretical O(1) lookups via deterministic memory offset calculation. However, achieving this requires obeying the hash distribution contract. The 32-bit integer returned by hashCode() is mixed using an internal bit-spread function to disperse high bits, followed by power-of-two masking. If two distinct keys produce identical bucket indices, a collision occurs.
Historically, hash collisions resolved strictly via singly-linked Node chaining, leaving systems vulnerable to O(n) degradation and algorithmic complexity attacks (HashDoS), where adversaries submit crafted inputs to freeze servers or mobile parsing pipelines. To neutralize this, modern Android ART runtimes adopt Java 8 treeification. When a bucket's collision depth reaches eight entries, the runtime inspects whether the total map capacity is at least sixty-four. If so, it transforms the linked list into a self-balancing Red-Black TreeNode structure, bounding worst-case traversal to O of log n.
Beyond collision dynamics, mobile engineers must manage the hidden tax of capacity expansion. When the number of entries exceeds the threshold of capacity multiplied by the 0.75 load factor, the map allocates a new array of double the size, re-indexes every entry, and discards the old array. In a mobile environment processing thousands of network records, these repeated O(n) rehashing events spike memory allocation and trigger garbage collection pauses. Pre-sizing collections by calculating the exact expected capacity completely circumvents rehashing, ensuring deterministic O(1) latency across all lifecycle passes.

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
