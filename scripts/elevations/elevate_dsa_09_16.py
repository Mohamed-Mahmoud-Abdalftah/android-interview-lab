#!/usr/bin/env python3
"""
Elevation script for DSA questions: DSA-09 to DSA-16.
Topic: Data Structures, Algorithms & Big O (DSA)
Phase 5, Batch 2
"""

import os
import sys

sys.path.insert(0, os.path.abspath("scripts/elevations"))
import elevation_engine as ee

TOPIC_AR = "هياكل البيانات والخوارزميات والـ Big O"
REVIEWED_DATE_AR = "تمت المراجعة والتحقق في 17 أكتوبر 2026"

DATA = {}

# ==========================================
# DSA-09: How do you calculate complexity for nested loops with dependent bounds?
# ==========================================
DATA["DSA-09"] = {
    "concept_en": """Calculating time complexity when loop iterations depend dynamically on an outer index requires evaluating arithmetic summations rather than multiplying upper bounds:
- Independent vs Dependent Loops:
  - Independent Loops: `for (i in 0 until n) for (j in 0 until m)` executes strictly $n \times m$ times, yielding $O(n \times m)$ or $O(n^2)$ when $m = n$.
  - Dependent Loops: `for (i in 0 until n) for (j in i + 1 until n)` executes a varying number of steps: when $i = 0$, inner runs $n - 1$ times; when $i = 1$, $n - 2$ times; down to $0$ when $i = n - 1$.
- Arithmetic Series Derivation:
  - Total operations $S = (n - 1) + (n - 2) + \dots + 2 + 1 + 0$.
  - Using Gauss\'s summation formula: $S = \frac{n(n - 1)}{2} = \frac{n^2 - n}{2} = \frac{1}{2}n^2 - \frac{1}{2}n$.
  - In asymptotic Big O notation, constants like $\frac{1}{2}$ and lower-order terms like $-\frac{1}{2}n$ are dropped.
  - Final Complexity: $O(n^2)$ Quadratic Time.
  - Mathematical Invariant: Even though the loop executes half the iterations of a full $n \times n$ matrix, its growth rate remains strictly quadratic.
- Geometric and Doubling Loops:
  - If the inner loop doubles (`var j = 1; while (j < i) j *= 2`), inner executes $\log_2 i$ times: $\sum_{i=1}^n \log i = \log(n!) = O(n \log n)$ via Stirling\'s approximation.
  - If the outer loop doubles (`var i = 1; while (i <= n) i *= 2`) and inner runs $i$ times: $\sum_{k=0}^{\log n} 2^k = 2^{\log_2 n + 1} - 1 = 2n - 1 = O(n)$ Linear Time!""",
    "walkthrough_en": """Kotlin examples analyzing nested loops with dependent arithmetic and doubling bounds:
```kotlin
// Example 1: Triangular Dependent Loop -> O(n^2)
// Total iterations: (n - 1) + (n - 2) + ... + 1 = n(n - 1) / 2 -> O(n^2)
fun compareAllPairs(items: List<String>) {
    val n = items.size
    for (i in 0 until n) {
        for (j in i + 1 until n) {
            // Evaluates every unique pair exactly once
            val pairComparison = items[i] == items[j]
        }
    }
}

// Example 2: Outer loop doubles, inner loop runs up to i -> O(n) Linear Time!
// Iterations: 1 + 2 + 4 + 8 + ... + n = 2n - 1 -> O(n)
fun doublingOuterLoop(n: Int) {
    var count = 0
    var i = 1
    while (i <= n) {
        for (j in 0 until i) {
            count++
        }
        i *= 2 // Geometric expansion
    }
}
```""",
    "short_en": """Calculate complexity for nested loops with dependent bounds by expressing the total steps as a mathematical summation rather than naively multiplying loop limits. For triangular loops where inner runs n minus i times, the sum equals n multiplied by n minus one over two, which simplifies asymptotically to O(n^2). Geometric doubling patterns require summing powers of two or logarithms.""",
    "structured_en": """Calculating time complexity for nested loops with dependent bounds requires setting up and evaluating mathematical summations rather than multiplying bounds.
When the inner loop bound depends on the outer loop variable, such as iterating from i plus one to n, the inner loop executes a decreasing number of operations on each pass. For a list of size n, the inner loop runs n minus one times, then n minus two times, continuing down to one operation.
This forms an arithmetic series known as Gauss\'s summation. The sum equals n multiplied by n minus one divided by two. Multiplying this out yields one-half n squared minus one-half n. Because asymptotic analysis omits multiplicative constants and lower-order terms, the complexity simplifies directly to O(n^2).
Even though the loop processes only half of an n by n grid, its fundamental growth rate remains strictly quadratic. For non-linear bounds where variables double geometrically, engineers sum powers of two or logarithms, which can yield surprising linear O(n) or linearithmic O(n log n) results.""",
    "deep_senior_en": """From an algorithmic proof and performance modeling perspective, analyzing dependent loops exposes the danger of mechanical Big O heuristics. Many engineers glance at nested loops and assume quadratic time, or mistakenly conclude that running half an iteration makes an algorithm sub-quadratic.
The rigorous methodology constructs a formal summation. In a triangular nested loop comparing all unique pairs, the outer index i increments from zero to n minus one, while the inner index j runs from i plus one to n. The total operation count is represented by the summation of n minus one minus i for i equals zero to n minus one. Expanding this series produces Gauss\'s formula: n times n minus one divided by two. In asymptotic notation, the coefficient of one-half is dropped, leaving O of n squared. The practical mobile takeaway is that cutting operations in half does not change algorithmic scalability; as catalog sizes scale by a factor of ten, execution time still increases hundredfold.
Furthermore, analyzing non-standard dependent boundaries reveals counter-intuitive complexities. Consider a loop where the outer index doubles on each iteration while the inner loop runs linearly up to i. A naive analysis might predict O of n log n. However, expressing the iterations as the summation of two to the power of k for k equals zero to log n forms a geometric series. The sum evaluates to two n minus one, proving that the algorithm actually runs in strictly linear O of n time.
In Android development, mastering these summation patterns is essential when profiling layout measurement passes, custom Canvas drawing routines, or DiffUtil list comparisons to identify whether nested logic will scale smoothly across growing datasets.""",
    "meta_ar": {
        "id": "DSA-09",
        "questionAr": "كيف تحسب التعقيد الزمني للحلقات المتداخلة ذات الحدود المعتمدة (Dependent Bounds)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "التحليل الرياضي للمتسلسلات الحسابية، صيغة مجموع غاوس n(n-1)/2، إهمال المعامل 1/2 للوصول لـ O(n^2)، وتحليل الحلقات الهندسية المضاعفة (Doubling Loops).",
        "concept_ar": "يتطلب حساب التعقيد الزمني للحلقات المتداخلة عندما يعتمد حد الحلقة الداخلية على متغير الحلقة الخارجية استخدام المتسلسلات الحسابية (Summations) بدلاً من الضرب التقليدي: في الحلقات المستقلة التي تدور فيها كل حلقة $n$ مرات، يكون التعقيد ببساطة $n \times n = O(n^2)$. أما في الحلقات المعتمدة مثل `for (i in 0 until n) for (j in i + 1 until n)`، فالحلقة الداخلية تدور $n - 1$ مرة في الدورة الأولى، ثم $n - 2$ مرة، نزولاً إلى 1 و0. إجمالي العمليات يمثل متسلسلة غاوس الحسابية: $S = \frac{n(n - 1)}{2} = \frac{1}{2}n^2 - \frac{1}{2}n$. وبإهمال الثابت $\frac{1}{2}$ والحد الأدنى $-\frac{1}{2}n$ في تحليل Big O، يستقر التعقيد عند $O(n^2)$ تربيعياً. ورغم أن الكود ينفذ نصف عدد عمليات المصفوفة الكاملة، إلا أن معدل نموه يظل تربيعياً بحتاً. أما إذا كانت الحدود تتضاعف هندسياً (مثل ضرب العداد في 2)، فيتحول التحليل إلى متسلسلة هندسية تنتج تعقيدات مفاجئة مثل $O(n)$ أو $O(n \log n)$.",
        "walkthrough_ar": """تحليل حسابي وعملي للحلقات المعتمدة في كوتلن:
```kotlin
// مثال 1: حلقة تعتمد على i لتقييم الأزواج الفريدة -> O(n^2)
// عدد الخطوات: (n-1) + (n-2) + ... + 1 = n(n-1)/2 -> O(n^2)
fun evaluateUniquePairs(items: List<String>) {
    val n = items.size
    for (i in 0 until n) {
        for (j in i + 1 until n) {
            // تفحص كل زوج فريد مرة واحدة فقط
            val match = items[i] == items[j]
        }
    }
}

// مثال 2: الحلقة الخارجية تتضاعف هندسياً والداخلية خطية -> O(n) مفاجئة!
// المجموع: 1 + 2 + 4 + 8 + ... + n = 2n - 1 -> O(n)
fun geometricLoop(n: Int) {
    var count = 0
    var i = 1
    while (i <= n) {
        for (j in 0 until i) {
            count++
        }
        i *= 2 // تضاعف هندسي
    }
}
```""",
        "why_it_matters_ar": "الاعتقاد الخاطئ بأن تقليل نصف العمليات ينقل الخوارزمية من O(n^2) إلى رتبة أسرع يؤدي لبناء شاشات تنهار وتتجمد عند زيادة البيانات في أندرويد.",
        "worked_example_ar": "عند مقارنة كل عنصر بما بعده في قائمة 2000 منتج، ينفذ الكود مليوني عملية بدلاً من أربعة ملايين؛ ورغم تقليص النصف، يظل النمو تربيعياً ويجمد الشاشة لمدة 80ms.",
        "trade_offs_ar": "الحساب السطحي بالضرب يفشل في معرفة التعقيد الحقيقي؛ بينما كتابة المتسلسلة الرياضية يعطي الرقم الدقيق للسلوك الحسابي للخوارزمية عند الأحجام الكبيرة.",
        "failure_modes_ar": "أخطر الأخطاء هو افتراض أن أي حلقة داخلية تبدأ من i + 1 هي O(n log n)، أو عدم الانتباه لتضاعف المتغير بالضرب (*= 2) الذي يحول التعقيد إلى لوغاريتمي.",
        "production_perspective_ar": "في كود أندرويد المتقدم، يُحظر استخدام الحلقات المتداخلة داخل دوال رسم Canvas أو حسابات قياس الحجم (onMeasure) لضمان عدم هبوط معدل الإطارات.",
        "how_to_answer_ar": "ابدأ ببيان الفرق بين الحلقات المستقلة والمعتمدة، ثم اكتب معادلة متسلسلة غاوس n(n-1)/2، ووضح لماذا يظل التعقيد O(n^2) بإهمال النصف، واذكر مثال التضاعف الهندسي.",
        "talking_points_ar": "المتسلسلات الحسابية Summations، متسلسلة غاوس n(n-1)/2، إهمال الثابت 1/2، ثبات الرتبة التربيعية O(n^2)، والحلقات الهندسية المضاعفة وتأثيرها الخطي O(n).",
        "follow_ups_ar": "كيف تحسب تعقيد دالة تقسم المصفوفة للنصف في كل استدعاء وتكرر حلقة داخلية؟ وكيف تطبق نظرية Master Theorem في هذا السياق؟",
        "self_check_ar": "هل شرحت متسلسلة غاوس الحسابية، وأكدت على أن نصف المصفوفة يظل O(n^2)، وشرحت مثال التضاعف الهندسي؟",
        "references_ar": f"- [Khan Academy: Sum of an arithmetic series](https://www.khanacademy.org/math/algebra2/x2ec2f6f830c9fb89:series/x2ec2f6f830c9fb89:arith-series/a/arithmetic-series-formula) — الشرح الرياضي القياسي لحساب متسلسلات الجمع الحسابية.\n- [Introduction to Algorithms (CLRS): Summations](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/) — المرجع الأكاديمي الكلاسيكي في تحليل الحلقات والمتسلسلات.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """نحسب تعقيد الحلقات المعتمدة بصياغتها كمتسلسلة رياضية بدلاً من ضرب الحدود؛ فالحلقة التي تدور n ناقص i مرة تمثل متسلسلة غاوس الحسابية ومجموعها ن مضروباً في ن ناقص واحد على اثنين. وبإهمال المعاملات والثوابت في تحليل Big O، يكون التعقيد هو O(n^2) تربيعياً. أما إذا كان العداد يتضاعف بالضرب، فإن المتسلسلة الهندسية تنتج تعقيداً خطياً O(n).""",
        "best_answer_ar": """حساب التعقيد الزمني للحلقات المتداخلة ذات الحدود المعتمدة يتطلب نمذجة خطوات التنفيذ كمتسلسلة حسابية بدلاً من الاكتفاء بضرب نهايات الحلقات.
فعندما تبدأ الحلقة الداخلية من دليل الحلقة الخارجية زائدا واحد وحتى نهاية المصفوفة، فإنها تنفذ عدداً متناقصاً من العمليات في كل دورة؛ فتبدأ بـ ن ناقص واحد، ثم ن ناقص اثنين، وصولاً إلى عملية واحدة في الدورة قبل الأخيرة.
ويمثل هذا النمط متسلسلة حسابية شهيرة تُعرف بمتسلسلة غاوس، ويساوي مجموع خطواتها ن مضروباً في ن ناقص واحد مقسوماً على اثنين، وهو ما يؤول إلى نصف ن تربيع ناقص نصف ن. وفي تحليل Big O، نهمل المعامل العددي نصف والحدود الدنيا، ليستقر التعقيد عند O(n^2) تربيعياً.
ورغم أن الكود ينفذ عملياً نصف عدد العمليات مقارنة بمصفوفة كاملة، إلا أن معدل النمو يظل تربيعياً بحتاً؛ فمضاعفة البيانات عشر مرات تضاعف وقت التنفيذ مئة مرة. أما إذا كانت الحدود تتضاعف هندسياً عبر الضرب، فإن مجموع قوى الرقم اثنين يثمر عن تعقيد خطي O(n) أو شبه خطي.""",
        "deep_answer_ar": """من منظور البرهان الرياضي وهندسة نمذجة الأداء، يوضح تحليل الحلقات المعتمدة خطورة الاعتماد على القواعد الميكانيكية التبسيطية في حساب Big O.
فالكثير من المطورين يقعون في وهم هندسي مفاده أن تقليص العمليات إلى النصف يمنح الخوارزمية كفاءة تفوق التعقيد التربيعي. والمنهج الرياضي السليم يبني معادلة تجميعية تمثل عدد مرات التنفيذ بدقة؛ ففي الحلقات المثلثية التي تقارن الأزواج الفريدة، يكون المجموع التراكمي لخطوات الحلقة الداخلية هو متسلسلة متناقصة تبدأ من ن ناقص واحد وتنتهي بالصفر. وبفك أقواس صيغة غاوس الرياضية وقسمتها على ن تربيع، يتضح أن ناتج النهاية عند اللانهاية يستقر عند نصف، مما يثبت رياضياً أن سلوك النمو يطابق O of n squared تماماً.
وعلى الجانب الآخر، يكشف تحليل الحدود غير الخطية عن مفاجآت معمارية بالغة الأهمية؛ فإذا كانت الحلقة الخارجية تتضاعف هندسياً بالضرب في اثنين بينما تنفذ الحلقة الداخلية عمليات خطية بقدر العداد الحالي، فقد يظن المهندس للوهلة الأولى أنها تستغرق وقتاً شبه خطي. ولكن بصياغة المتسلسلة كمجموع قوى الرقم اثنين حتى لوغاريتم ن، نكتشف أن المجموع الرياضي يساوي اثنين ن ناقص واحد؛ مما يعني أن الخوارزمية تعمل في زمن خطي O of n حتمي وفائق السرعة.
وفي تطوير أندرويد، يعد هذا التدقيق الرياضي ركيزة أساسية عند فحص خوارزميات التباين في DiffUtil أو دوال الرسم المخصص على الشاشة للتأكد من قدرتها على مجاراة البيانات المتزايدة دون تجمد الشاشة."""
    }
}

# ==========================================
# DSA-10: How do you design and analyze an LRU cache?
# ==========================================
DATA["DSA-10"] = {
    "concept_en": """A Least Recently Used (LRU) Cache discards the oldest unaccessed items when reaching capacity, requiring strictly constant-time eviction and retrieval:
- Dual-Structure Architecture for $O(1)$ Operations:
  - Hash Map (`HashMap<K, Node<K, V>>`): Provides $O(1)$ constant-time lookup by mapping keys directly to corresponding node references on the heap.
  - Doubly-Linked List (`head` <-> `tail`): Tracks access recency. Adding to the front (Most Recently Used / MRU) and evicting from the back (Least Recently Used / LRU) execute in strictly $O(1)$ time by manipulating neighboring pointers without shifting elements.
- Algorithmic Mechanics:
  - `get(key)`: If missing, return `null`. If present, locate `Node` via HashMap, detach it from its current list position, reinsert it at the head (MRU), and return value. Complexity: $O(1)$.
  - `put(key, value)`: If key exists, update value and move `Node` to head. If key is new: instantiate `Node`, insert at head, and insert reference into HashMap. If `size > capacity`, evict the node immediately preceding dummy `tail` (LRU), remove its key from HashMap, and decrement size. Complexity: $O(1)$.
- Android Platform Standards (`LruCache`):
  - Android provides `android.util.LruCache` (and `androidx.collection.LruCache`).
  - Internally wraps a Java `LinkedHashMap(capacity, 0.75f, accessOrder = true)`.
  - Memory-Sized Caching: In Android image and bitmap caching, overriding `sizeOf(key, value)` to measure memory bytes (`bitmap.byteCount`) rather than item counts prevents OutOfMemoryError crashes.
  - Sizing Rule: Cache budgets are allocated as a fraction of available heap: `val cacheSize = (Runtime.getRuntime().maxMemory() / 8).toInt()`.""",
    "walkthrough_en": """Custom O(1) LRU Cache implementation and Android LruCache usage:
```kotlin
// Custom O(1) LRU Cache combining HashMap and DoublyLinkedList
class CustomLruCache<K, V>(private val capacity: Int) {
    private class Node<K, V>(val key: K, var value: V) {
        var prev: Node<K, V>? = null
        var next: Node<K, V>? = null
    }

    private val map = HashMap<K, Node<K, V>>()
    private val head = Node<K, V>(null as K, null as V) // Dummy head
    private val tail = Node<K, V>(null as K, null as V) // Dummy tail

    init {
        head.next = tail
        tail.prev = head
    }

    fun get(key: K): V? {
        val node = map[key] ?: return null
        moveToHead(node) // Mark as MRU
        return node.value
    }

    fun put(key: K, value: V) {
        val node = map[key]
        if (node != null) {
            node.value = value
            moveToHead(node)
        } else {
            val newNode = Node(key, value)
            map[key] = newNode
            addNode(newNode)
            if (map.size > capacity) {
                val lru = popTail()
                map.remove(lru.key)
            }
        }
    }

    private fun addNode(node: Node<K, V>) {
        node.prev = head
        node.next = head.next
        head.next?.prev = node
        head.next = node
    }

    private fun removeNode(node: Node<K, V>) {
        node.prev?.next = node.next
        node.next?.prev = node.prev
    }

    private fun moveToHead(node: Node<K, V>) {
        removeNode(node)
        addNode(node)
    }

    private fun popTail(): Node<K, V> {
        val res = tail.prev!!
        removeNode(res)
        return res
    }
}
```""",
    "short_en": """An LRU cache achieves O(1) get and put operations by combining a HashMap for constant-time key lookup with a Doubly-Linked List for constant-time recency tracking. On access, nodes move to the head, and upon capacity overflow, the tail node is evicted. Android provides LruCache, which teams size by memory bytes rather than count to manage Bitmaps safely.""",
    "structured_en": """Designing a Least Recently Used cache requires pairing two complementary data structures to guarantee constant-time performance across all operations.
A standalone HashMap provides O(1) lookups but cannot maintain order without scanning. A standalone array or list maintains order but requires O(n) time to find or shift elements. By combining a HashMap with a Doubly-Linked List, we achieve the best of both worlds.
The HashMap maps each key to its corresponding list node in O(1) time. The Doubly-Linked List maintains access recency: newly inserted or accessed items are moved to the head as Most Recently Used, while the tail represents the Least Recently Used item.
When capacity is exceeded during a put operation, the node preceding the tail is removed from both the list and the map in O(1) pointer updates. In Android development, the platform provides LruCache, which wraps LinkedHashMap with access-order mode. For media apps, overriding sizeOf to budget cache limits by bitmap byte counts rather than item counts prevents out-of-memory crashes.""",
    "deep_senior_en": """From a systems architecture and memory management perspective, the LRU cache represents the canonical design pattern for bounded in-memory caching under resource constraints.
The architectural brilliance of an LRU cache lies in its zero-shifting pointer mechanics. If an engineer attempts to implement an LRU cache using an ArrayList, accessing an element requires an O of n linear search, followed by an O of n array copy to shift elements forward. By employing a Doubly-Linked List flanked by sentinel dummy head and dummy tail nodes, detaching and prepending a node involves exactly four pointer reassignments, completing in strictly deterministic O of one time. Pairing this with a HashMap that stores direct memory references to these nodes eliminates traversal overhead completely.
In the Android ecosystem, the framework provides android.util.LruCache, which delegates internally to Java\'s LinkedHashMap configured with access-order set to true. However, senior Android engineers recognize that item-count sizing is a dangerous anti-pattern for mobile image caching. A cache limited to fifty items could hold fifty thumbnail images consuming five megabytes, or fifty high-resolution camera photos consuming four hundred megabytes, instantly exhausting the ART heap and triggering an OutOfMemoryError.
The production solution is memory-weighted caching. We allocate a safe fraction of the application\'s runtime memory—typically one-eighth of maxMemory—and override LruCache.sizeOf() to return the exact byte footprint of each cached Bitmap via bitmap.byteCount. Furthermore, we synchronize operations or utilize concurrent wrappers to prevent race conditions across parallel Coroutine dispatchers, guaranteeing thread-safe, sub-millisecond retrieval without risking heap exhaustion.""",
    "meta_ar": {
        "id": "DSA-10",
        "questionAr": "كيف تصمم وتحلل ذاكرة تخزين مؤقت خوارزمية (LRU Cache) بتعقيد O(1) في أندرويد؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "تصميم LRU Cache بتعقيد O(1)، الدمج المعماري بين HashMap وDoublyLinkedList، استخدام فئة LruCache في أندرويد، وتحديد السعة بحجم البايتات (Byte Count) بدلاً من عدد العناصر لتفادي OOM.",
        "concept_ar": "تعتمد ذاكرة التخزين المؤقت الأقل استخداماً مؤخراً (LRU Cache) على طرد أقدم العناصر وصولاً عند امتلاء السعة، وتتطلب معماريتها تحقيق تعقيد ثابت $O(1)$ لكافة عمليات القراءة والإضافة: لتحقيق ذلك، ندمج هيكلين معاً: جدول التجزئة (HashMap) الذي يربط المفتاح برابط العقدة في الذاكرة لتوفير بحث في $O(1)$، وقائمة مترابطة مزدوجة (Doubly-Linked List) برأس وذيل وهميين لتتبع ترتيب الاستخدام؛ حيث يتم نقل أي عنصر يُقرأ أو يُعدل إلى مقدمة القائمة (MRU)، ويُطرد العنصر الموجود عند الذيل (LRU) فور تجاوز السعة بتحديث أربعة مؤشرات في $O(1)$ دون أي إزاحة لعناصر أخرى. وتوفر منصة أندرويد فئة جاهزة ومحكمة هي `android.util.LruCache` مبنية داخلياً فوق `LinkedHashMap`. وفي تطبيقات أندرويد التي تتعامل مع الصور والـ Bitmaps، تشترط المعمارية السليمة تخصيص السعة بحجم البايتات المستهلكة من الذاكرة (`bitmap.byteCount`) بدلاً من عدد العناصر عبر تجاوز دالة `sizeOf`، مع تخصيص ثمن مساحة الـ Heap الكلية للذاكرة المؤقتة لتفادي انهيارات نفاد الذاكرة OOM.",
        "walkthrough_ar": """تصميم LRU Cache مخصص واستخدام LruCache بحجم البايتات في أندرويد:
```kotlin
import android.graphics.Bitmap
import androidx.collection.LruCache

// استخدام LruCache الرسمي في أندرويد مع حساب حجم الذاكرة بالبايت للصور
class ImageMemoryCache {
    // تخصيص ثمن الذاكرة القصوى المتاحة للتطبيق كحد أقصى للكاش
    private val maxMemory = (Runtime.getRuntime().maxMemory() / 1024).toInt()
    private val cacheSize = maxMemory / 8

    val memoryCache = object : LruCache<String, Bitmap>(cacheSize) {
        override fun sizeOf(key: String, bitmap: Bitmap): Int {
            // قياس الحجم الفعلي للـ Bitmap بالكيلوبايت بدلاً من عد العناصر
            return bitmap.byteCount / 1024
        }
    }

    fun getBitmap(url: String): Bitmap? = memoryCache.get(url) // O(1)

    fun putBitmap(url: String, bitmap: Bitmap) {
        memoryCache.put(url, bitmap) // O(1) مع طرد أقدم عنصر تلقائياً
    }
}
```""",
        "why_it_matters_ar": "بناء الكاش بقائمة عادية يحول البحث لـ O(n) ويبطئ التطبيق، وتحديد سعة الكاش بعدد الصور بدلاً من حجم الذاكرة يفجر انهيار OOM سريعاً.",
        "worked_example_ar": "في تطبيق لعرض الصور، قمنا بضبط LruCache بقياس byteCount وتحديد 1/8 من الذاكرة؛ مما سمح بتخزين 40 صورة في الذاكرة دون أن يتجاوز استهلاك الـ Heap حد الأمان.",
        "trade_offs_ar": "الدمج بين HashMap وDoublyLinkedList يوفر سرعة O(1) فائقة ولكنه يستهلك ذاكرة إضافية لمؤشرات العقد السابقة والتالية في الذاكرة.",
        "failure_modes_ar": "أخطر الأخطاء هو ضبط حجم LruCache بعدد العناصر (مثل 50 صورة)، فإذا كانت الصور عالية الدقة (4K) ستستهلك 600MB وتسبب انهيار التطبيق بـ OOM فوراً.",
        "production_perspective_ar": "في كبرى مكتبات الصور مثل Coil وGlide، يُستخدم LruCache داخلياً مع التفاعل مع أحداث النظام OnTrimMemory لتفريغ الكاش عند انخفاض ذاكرة الجهاز.",
        "how_to_answer_ar": "اشرح دمج HashMap مع Doubly-Linked List لتحقيق O(1)، ووضح كيفية عمل get وput ونقل العقد، ثم قدم فئة أندرويد الرسمية وركز على تخصيص الحجم بالبايت للصور.",
        "talking_points_ar": "دمج HashMap مع DoublyLinkedList، مؤشرات الرأس والذيل الوهميين، تعقيد O(1) الحتمي، فئة LruCache في أندرويد، دالة sizeOf وحساب byteCount، وتجنب OOM.",
        "follow_ups_ar": "كيف تدير تزامن الخيوط في LruCache عند استدعائه من عدة Coroutines؟ وكيف تتكامل مع OnTrimMemory لتفريغ الكاش؟",
        "self_check_ar": "هل شرحت دمج الهيكلين لتحقيق O(1)، وذكرت فئة أندرويد LruCache وأكدت على حساب الحجم بالبايتات للـ Bitmaps؟",
        "references_ar": f"- [Android Developers: LruCache documentation](https://developer.android.com/reference/android/util/LruCache) — التوثيق الرسمي لفئة LruCache في حزمة أدوات أندرويد.\n- [Coil: Memory Cache Architecture](https://coil-kt.github.io/coil/caches/) — التوثيق المعماري لكيفية إدارة كاش الصور في مكتبة Coil الحديثة.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """يحقق LRU Cache كفاءة O(1) بالدمج بين HashMap للبحث اللحظي وقائمة مترابطة مزدوجة لتتبع ترتيب الاستخدام بنقل العناصر للرأس وطرد الذيل دون إزاحة. وفي أندرويد، نستخدم فئة LruCache الرسمية مع تخصيص السعة بحجم البايتات للصور عبر دالة sizeOf بدلاً من عدد العناصر لحماية الذاكرة من انهيار OOM.""",
        "best_answer_ar": """تصميم ذاكرة LRU Cache بكفاءة ثابتة O(1) لكافة العمليات يتطلب دمج هيكلي بيانات متكاملين لعلاج عيوب كل هيكل بمزايا الآخر.
فلو استخدمنا HashMap وحدها لما استطعنا معرفة أقدم عنصر مستخدم دون مسح خطي، ولو استخدمنا مصفوفة عادية لاحتجنا وقتاً خطياً لإزاحة العناصر. ولذلك ندمج HashMap لتوفير وصول مباشر للعقد بروابطها في الذاكرة في زمن O(1)، مع قائمة مترابطة مزدوجة Doubly-Linked List تمتلك رأساً وذيلاً وهميين.
عند قراءة أي عنصر، نجلبه من الخريطة ونفصله من موضعه ونعيده لمقدمة القائمة كأحدث عنصر مستخدم في O(1). وعند إضافة عنصر جديد مع امتلاء السعة، نطرد العقدة السابقة للذيل فوراً من القائمة والخريطة بتعديل مؤشرين فقط.
وفي بيئة أندرويد، تقدم المنصة فئة LruCache الجاهزة المبنية على LinkedHashMap بنمط ترتيب الوصول. ومن القواعد الحيوية في تطبيقات الوسائط عدم ضبط السعة بعدد العناصر، بل بحجم البايتات الفعلي للصور عبر دالة sizeOf وتخصيص ثمن الذاكرة القصوى للكاش لمنع نفاد ذاكرة الـ Heap تماماً.""",
        "deep_answer_ar": """من منظور معمارية النظم وإدارة الذاكرة في أجهزة أندرويد، يمثل LRU Cache النمط المعماري القياسي للاحتفاظ بالبيانات في الذاكرة الحية تحت قيود الموارد الصارمة.
العبقرية المعمارية لهذا التصميم تكمن في الاعتماد على مناورة المؤشرات دون أي إزاحة في خلايا الذاكرة؛ فاستخدام مصفوفة عادية يتطلب عمليات نسخ باهظة في كل عملية وصول أو حذف. بينما استخدام القائمة المترابطة المزدوجة المعززة برأس وذيل اصطناعيين يحصر عملية إعادة ترتيب العقدة في تعديل أربعة مؤشرات ذاكرة بدقة متناهية وفي وقت حتمي O of one. وبدمج ذلك مع HashMap تخزن مراجع هذه العقد مباشرة، نحصل على كاش فائق السرعة والاستجابة.
وفي منظومة أندرويد، توفر مكتبة الدعم فئة android.util.LruCache التي تدير هذه الآلية بسلاسة. ولكن يدرك مهندسو الأداء أن تقييد الكاش بعدد العناصر يمثل فخاً كارثياً في التعامل مع الصور والـ Bitmaps؛ فعشر صور ملتقطة بكاميرا حديثة قد تستهلك نصف غيغابايت من الذاكرة وتفجر انهيار OutOfMemoryError فورياً.
ولذلك نلزم كود الإنتاج بتخصيص ميزانية الذاكرة وفق حجم البايت الفعلي؛ حيث نشتق سعة الكاش من الذاكرة القصوى المتاحة للتطبيق Runtime.getRuntime().maxMemory مقسومة على ثمانية، ونعيد كتابة دالة sizeOf لتعيد الحجم الحقيقي للبايتات عبر bitmap.byteCount. وبدمج ذلك مع الاستجابة لنداءات النظام onTrimMemory لتفريغ الكاش عند اختناق الذاكرة في الخلفية، نحقق توازناً مثالياً بين سرعة العرض واستقرار النظام على كافة الأجهزة."""
    }
}

# ==========================================
# DSA-11: Explain BFS versus DFS and their typical applications.
# ==========================================
DATA["DSA-11"] = {
    "concept_en": """Breadth-First Search (BFS) and Depth-First Search (DFS) represent the foundational graph and tree traversal paradigms with contrasting traversal mechanics and memory profiles:
- Breadth-First Search (BFS):
  - Traversal Strategy: Explores the graph level by level, visiting all immediate neighbors of the current vertex before advancing to the next depth tier.
  - Core Data Structure: FIFO Queue (`ArrayDeque`).
  - Complexity: $O(V + E)$ Time, $O(V)$ Auxiliary Space (governed by maximum graph breadth or leaf layer width).
  - Android Applications: Finding the shortest path in unweighted graphs (e.g., shortest navigation hops in a subway map), finding the nearest matching UI node, breadth-first traversal of a `ViewGroup` hierarchy (`ViewGroup.getChildAt()`), and peer-to-peer device discovery in nearby mesh networks.
- Depth-First Search (DFS):
  - Traversal Strategy: Plunges along each branch to its deepest leaf before backtracking.
  - Core Data Structure: LIFO Stack (explicit `ArrayDeque` or implicit recursion call stack).
  - Complexity: $O(V + E)$ Time, $O(H)$ Space for trees of height $H$, or $O(V)$ for degenerate graphs.
  - Android Applications: Topological sorting for dependency resolution (Dagger/Hilt component graph compilation, Gradle task dependency execution), detecting cycles in navigation backstacks or circular dependencies, and Abstract Syntax Tree (AST) inspection in custom Android Lint rules.
- Mobile Stack Safety Invariant:
  - Recursive DFS on deep trees risks triggering `StackOverflowError` if recursion depth exceeds the JVM/ART thread stack size limit (typically 1MB). Production Android systems mandate iterative DFS using an explicit heap-allocated `ArrayDeque` to guarantee crash-free traversal.""",
    "walkthrough_en": """Kotlin implementations comparing iterative BFS and stack-safe iterative DFS:
```kotlin
// Graph node representation
class GraphNode(val id: String, val neighbors: MutableList<GraphNode> = mutableListOf())

// 1. Breadth-First Search (BFS): Level-by-level traversal using FIFO Queue
fun traverseBfs(root: GraphNode, targetId: String): GraphNode? {
    val queue = ArrayDeque<GraphNode>()
    val visited = HashSet<String>()

    queue.addLast(root)
    visited.add(root.id)

    while (queue.isNotEmpty()) {
        val current = queue.removeFirst() // Dequeue
        if (current.id == targetId) return current // Shortest path guarantee in unweighted graph

        for (neighbor in current.neighbors) {
            if (visited.add(neighbor.id)) {
                queue.addLast(neighbor)
            }
        }
    }
    return null
}

// 2. Depth-First Search (DFS): Stack-safe iterative traversal using LIFO Stack
fun traverseDfsIterative(root: GraphNode, targetId: String): GraphNode? {
    val stack = ArrayDeque<GraphNode>()
    val visited = HashSet<String>()

    stack.addFirst(root) // Push
    visited.add(root.id)

    while (stack.isNotEmpty()) {
        val current = stack.removeFirst() // Pop
        if (current.id == targetId) return current

        for (neighbor in current.neighbors) {
            if (visited.add(neighbor.id)) {
                stack.addFirst(neighbor) // Push neighbor
            }
        }
    }
    return null
}
```""",
    "short_en": """BFS explores graphs level-by-level using a FIFO queue, delivering shortest-path guarantees in unweighted graphs like UI view-tree scans. DFS explores deeply down branches using a stack or recursion, ideal for topological sorting, cycle detection, and AST linting. In Android, production DFS uses an explicit heap-allocated ArrayDeque to prevent StackOverflowError crashes.""",
    "structured_en": """Breadth-First Search and Depth-First Search represent the two fundamental strategies for traversing trees and graphs.
Breadth-First Search explores outward layer by layer, visiting all immediate neighbors before penetrating deeper into the graph. It uses a FIFO queue, typically implemented with ArrayDeque, and runs in O of V plus E time. In Android development, BFS is the algorithm of choice for finding the shortest path in unweighted networks and for level-order scans of ViewGroup hierarchies.
Depth-First Search explores as deep as possible along each branch before backtracking, utilizing a LIFO stack. It operates in O of V plus E time with memory proportional to tree height. DFS powers critical architectural processes such as topological sorting in Dagger dependency injection graphs, cycle detection in navigation backstacks, and AST parsing in custom Lint rules.
To ensure safety on mobile devices, production Android code avoids recursive DFS on arbitrary user-generated structures. Because thread call stacks are limited to approximately one megabyte, recursive calls risk StackOverflowError. We mandate iterative DFS using a heap-allocated ArrayDeque.""",
    "deep_senior_en": """From an algorithmic theory and platform engineering perspective, BFS and DFS embody distinct trade-offs between search optimality, traversal order, and memory topology.
BFS operates with a FIFO queue to guarantee shortest path discovery in unweighted graphs. Because it expands monotonically outward, the first time BFS encounters a target node, it is mathematically proven to have arrived via the minimum number of edges. However, its memory footprint is dictated by the maximum width of the graph. When traversing a wide, shallow tree—such as a complex Android UI hierarchy with dozens of siblings per ViewGroup—the queue expands to hold the entire breadth, consuming O of V memory on the heap.
DFS operates with LIFO stack semantics, prioritizing path depth over breadth. In balanced trees, DFS consumes only O of H memory, proportional to tree height, making it far more memory-frugal than BFS for deep, narrow structures. This property makes DFS the ideal engine for topological sorting and cycle detection. In Android build toolchains and dependency injection frameworks like Dagger, DFS performs post-order traversal to resolve dependency graphs, compiling leaf modules before their consumers.
However, in mobile runtimes, the implementation pattern is a critical reliability concern. Writing DFS recursively relies on the execution call stack. On Android, thread stacks are constrained by ART to small memory boundaries. If recursive DFS encounters a degenerate linked structure or deeply nested JSON tree, the runtime exhausts stack frames and crashes the process with an uncatchable StackOverflowError. Senior Android engineers mandate iterative DFS using an explicit heap-allocated ArrayDeque, converting dangerous call-stack allocations into safe, managed heap memory.""",
    "meta_ar": {
        "id": "DSA-11",
        "questionAr": "اشرح الفارق بين خوارزميتي البحث بالعرض (BFS) والبحث بالعمق (DFS) وتطبيقاتهما في أندرويد.",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "المقارنة بين BFS وDFS، هياكل البيانات المستخدمة (Queue مقابل Stack)، ضمان المسار الأقصر في BFS، استخدامات DFS في الترتيب الطوبولوجي وكشف الحلقات، وخطر StackOverflowError في أندرويد.",
        "concept_ar": "تمثل خوارزميتا البحث بالعرض (BFS) والبحث بالعمق (DFS) النهجين الأساسيين للتنقل في الرسوم البيانية والأشجار البرمجية: البحث بالعرض (BFS) يستكشف الرسم طبقة تلو الأخرى؛ فيزور كافة الجيران المباشرين قبل الانتقال للعمق التالي، معتمداً على طابور FIFO (`ArrayDeque`). يتميز BFS بضمان الوصول لأقصر مسار في الرسوم غير الموزونة، ويُستخدم في أندرويد للبحث في شجرة الواجهات (`ViewGroup Hierarchy`) والعثور على أقرب المكونات. أما البحث بالعمق (DFS) فيتوغل في كل فرع لأقصى عمق ممكن قبل التراجع (Backtracking)، معتمداً على مكدس LIFO (عبر الاستدعاء الذاتي أو `ArrayDeque`). يُستخدم DFS في الترتيب الطوبولوجي لفك الاعتماديات (Topological Sort) في Dagger/Hilt، وكشف الحلقات الدائرية (Cycle Detection)، وفحص الشفرة في أندرويد لنت (Lint AST). وفي بيئة أندرويد، يُحظر استخدام DFS بالاستدعاء الذاتي (Recursion) على هياكل غير مضمونة العمق لتفادي انهيار مكدس الاستدعاءات (`StackOverflowError`)، ويُلزم باستخدام الحل التكراري بمكدس على الـ Heap.",
        "walkthrough_ar": """تطبيقات كوتلن للمسار الأقصر بـ BFS والتنقل الآمن بمكدس الـ Heap في DFS:
```kotlin
class Node(val id: String, val children: MutableList<Node> = mutableListOf())

// 1. البحث بالعرض BFS: استكشاف طبقي يضمن أقصر مسار باستخدام الطابور
fun findShortestPathBfs(root: Node, targetId: String): Node? {
    val queue = ArrayDeque<Node>()
    queue.addLast(root)

    while (queue.isNotEmpty()) {
        val current = queue.removeFirst()
        if (current.id == targetId) return current // أول وصول يمثل أقصر مسار

        for (child in current.children) {
            queue.addLast(child)
        }
    }
    return null
}

// 2. البحث بالعمق DFS: تنفيذ تكراري آمن يتفادى خطأ StackOverflowError
fun traverseDfsSafe(root: Node, targetId: String): Node? {
    val stack = ArrayDeque<Node>()
    stack.addFirst(root) // Push

    while (stack.isNotEmpty()) {
        val current = stack.removeFirst() // Pop
        if (current.id == targetId) return current

        for (child in current.children) {
            stack.addFirst(child)
        }
    }
    return null
}
```""",
        "why_it_matters_ar": "اختيار الخوارزمية الخاطئة يمنع العثور على أقصر مسار، واستخدام الاستدعاء الذاتي في DFS قد يسقط التطبيق فجأة بانهيار StackOverflowError.",
        "worked_example_ar": "في محرك البحث داخل شجرة واجهة مستخدم معقدة، استبدلنا الاستدعاء الذاتي بـ BFS عبر ArrayDeque؛ فضمنّا الوصول لأقرب زر في الشاشة دون المخاطرة بفيضان المكدس.",
        "trade_offs_ar": "خوارزمية BFS تضمن أقصر مسار ولكنها تستهلك ذاكرة أكبر تتناسب مع عرض الشجرة؛ بينما DFS توفر الذاكرة في الأشجار العميقة ولكنها لا تضمن أقصر مسار وتتطلب مكدساً آمناً.",
        "failure_modes_ar": "أخطر الأخطاء هو تنفيذ DFS باستخدام الدالة التكرارية Recursive على هياكل عميقة مما يفجر خطأ StackOverflowError فوري نظراً لمحدودية مساحة الـ Stack في أندرويد (1MB).",
        "production_perspective_ar": "في كود أدوات أندرويد الداخلية ومكتبات مثل Dagger وGradle، يُستخدم DFS لحل شجرة الاعتماديات وضمان عدم وجود حلقات دائرية تعطل البناء.",
        "how_to_answer_ar": "ابدأ ببيان أسلوب التنقل وهيكل البيانات لكل منهما، ووضح ميزة BFS في أقصر مسار وتطبيقه في شجرة الواجهات، واشرح دور DFS في الترتيب الطوبولوجي، واختم بالتحذير من StackOverflowError.",
        "talking_points_ar": "الاستكشاف الطبقي لـ BFS، طابور ArrayDeque، ضمان المسار الأقصر، التوغل العميق لـ DFS، الترتيب الطوبولوجي في Dagger، وخطر StackOverflowError والحل التكراري.",
        "follow_ups_ar": "كيف تستخدم DFS لاكتشاف وجود اعتماديات دائرية (Circular Dependencies) في مشروع أندرويد؟ ومتى يكون BFS مكلفاً جداً في الذاكرة؟",
        "self_check_ar": "هل فرقت بين الطابور والمكدس، وشرحت ميزة أقصر مسار لـ BFS واستخدام DFS في الترتيب الطوبولوجي وحذرت من فيضان المكدس؟",
        "references_ar": f"- [Android Developers: View and ViewGroup hierarchy](https://developer.android.com/reference/android/view/ViewGroup) — التوثيق الرسمي لهيكل شجرة الواجهات في أندرويد وكيفية التنقل فيها.\n- [Dagger: Dependency Graph Generation](https://dagger.dev/dev-guide/) — التوثيق الرسمي لكيفية حل شجرة الاعتماديات طوبولوجياً عبر خوارزميات الرسم البياني.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """يستكشف BFS الرسم طبقة تلو الأخرى باستخدام طابور FIFO ويضمن أقصر مسار في الرسوم غير الموزونة كشجرة الواجهات. بينما يتوغل DFS في أقصى عمق لكل فرع باستخدام مكدس LIFO ويناسب الترتيب الطوبولوجي في Dagger وكشف الحلقات. وفي أندرويد، نلزم DFS بالتنفيذ التكراري بمكدس على الـ Heap لتفادي انهيار StackOverflowError.""",
        "best_answer_ar": """يمثل البحث بالعرض والبحث بالعمق استراتيجيتين متناقضتين في استكشاف الأشجار والرسوم البيانية مع اختلاف طبيعة الذاكرة والتنقل.
يستكشف البحث بالعرض BFS البيانات أفقياً طبقة تلو الأخرى؛ فيزور كافة الجيران المباشرين قبل النزول للعمق التالي، معتمداً على طابور FIFO من نوع ArrayDeque. وميزته الجوهرية أنه يضمن رياضياً العثور على أقصر مسار في الرسوم غير الموزونة؛ ولذلك يمثل الخيار المثالي لفحص شجرة الواجهات وتحديد أقرب عنصر للمستخدم.
أما البحث بالعمق DFS، فيتوغل رأسياً في كل فرع حتى نهايته قبل التراجع للفرع الآخر، معتمداً على مكدس LIFO. ويعد DFS المحرك الأساسي لحل الاعتماديات في مكتبات مثل Dagger عبر الترتيب الطوبولوجي، وكشف الحلقات الدائرية في مسارات التنقل، وفحص شفرة المصدر في أندرويد لنت.
ومن قواعد الأمان الصارمة في أندرويد تجنب استخدام DFS بالاستدعاء الذاتي التكراري؛ لأن مكدس استدعاء الخيط محدود بحوالي ميغابايت واحد، وتكرار النداء في هياكل عميقة يفجر خطأ فيضان المكدس فوراً؛ ولذا نلزم استخدام البديل التكراري بمكدس محجوز على الـ Heap لضمان استقرار التطبيق.""",
        "deep_answer_ar": """من منظور النظرية الخوارزمية وهندسة المنصات، يجسد BFS وDFS مفاضلة عميقة بين مثالية المسار وتوزيع استهلاك الذاكرة في عتاد أندرويد.
ينطلق BFS بنمط تدفق منتظم يضمن أنه بمجرد وصوله للعنصر المستهدف، يكون قد سلك أقصر عدد من الحواف؛ مما يجعله مثالياً لمسارات التنقل في الخرائط واكتشاف الأجهزة المجاورة. ولكن ضريبته تكمن في استهلاك الذاكرة؛ فحجم الطابور يتسع ليتناسب مع أقصى عرض للشجرة. وفي شاشات أندرويد المعقدة التي تحتوي على عشرات العناصر في نفس الطبقة، يتسع الطابور ليحجز مساحة خطية O of V على الـ Heap.
وفي المقابل، يتميز DFS باقتصاد هائل في الذاكرة في الأشجار المتوازنة؛ حيث ينحصر استهلاكه في عمق الشجرة O of H فقط. وتستغل أداة Dagger هذه الخاصية لإجراء فرز طوبولوجي يحدد ترتيب تجميع المكونات، وبناء العقد التابعة قبل العقد الرئيسية بدقة متناهية، مع إطلاق إنذار فوري عند اكتشاف أي حلقة مغلقة تكسر المعمارية.
إلا أن الخطر التشغيلي الأكبر في أجهزة الهواتف هو نمط الاستدعاء؛ فالاعتماد على استدعاء الدوال المتداخل ذاتياً يستهلك مكدس النظام Thread Call Stack المقيد بشدة من قِبل بيئة تشغيل ART. وإذا صادف الكود هيكلاً متداخلاً بعمق كبير، يسقط التطبيق بانهيار غير قابل للاعتراض وهو StackOverflowError. ولذلك يفرض كبار مهندسي أندرويد استبعاد الاستدعاء الذاتي نهائياً، وتطبيق DFS عبر حلقة تكرار بسيطة تقودها فئة ArrayDeque محجوزة بأمان على ذاكرة الـ Heap، محولين الخطر الكارثي إلى إدارة آمنة للذاكرة."""
    }
}

# ==========================================
# DSA-12: How do you identify an accidental O(n²) transformation in a RecyclerView/Compose list?
# ==========================================
DATA["DSA-12"] = {
    "concept_en": """Accidental quadratic complexity in UI lists occurs when a linear $O(n)$ search is nested inside an $O(n)$ item binding, composition, or diffing pass:
- Root Causes of Accidental $O(n^2)$ Transformations:
  - In `RecyclerView.Adapter.onBindViewHolder`: Calling `selectedIdsList.contains(item.id)` where `selectedIdsList` is an `ArrayList`. When binding $n$ items, checking membership takes $O(n)$ sequential scans, producing $n \times O(n) = O(n^2)$ work on the Main Thread during fast scrolling.
  - In Jetpack Compose `LazyColumn`: Invoking `categories.first { it.id == item.categoryId }` inside an item composable row. For $n$ displayed rows, scanning the category list scales quadratically.
  - In `DiffUtil.Callback.areItemsTheSame`: Performing nested collection scans or secondary iterations inside diff comparison callbacks.
- Detection & Diagnostic Profiling:
  - System Trace (Perfetto) & CPU Profiler: Flame charts reveal deep, repetitive call stacks during list scrolling. The Main Thread is monopolized by `java.util.ArrayList.indexOf` or `ArrayList.contains` rather than UI drawing routines.
  - Frame Drop Symptoms: Choreographer logs report: `Skipped 45 frames! The application may be doing too much work on its main thread.`
- Architectural Remediation:
  - Pre-indexing Data: Transform secondary lookup collections into a `HashSet` or `HashMap` in the ViewModel or repository before dispatching state to the UI.
  - Membership checks convert from $O(n)$ sequential scans to instantaneous $O(1)$ lookups, collapsing total list transformation complexity back to strictly linear $O(n)$.""",
    "walkthrough_en": """Refactoring an accidental O(n^2) RecyclerView binding into an optimal O(n) pipeline:
```kotlin
data class CartItem(val id: String, val name: String, val categoryId: String)
data class Category(val id: String, val displayName: String)

// ANTI-PATTERN: Accidental O(n^2) during list scrolling
class SlowCartAdapter(
    private val items: List<CartItem>,
    private val categories: List<Category> // List lookup inside binding!
) : RecyclerView.Adapter<CartViewHolder>() {

    override fun onBindViewHolder(holder: CartViewHolder, position: Int) {
        val item = items[position]
        // O(n) search inside O(n) binding pass -> O(n^2) total!
        val category = categories.firstOrNull { it.id == item.categoryId }
        holder.bind(item, category?.displayName ?: "")
    }

    override fun getItemCount(): Int = items.size
}

// BEST PRACTICE: Pre-indexed O(n) pipeline with O(1) lookups
class FastCartAdapter(
    private val items: List<CartItem>,
    categories: List<Category>
) : RecyclerView.Adapter<CartViewHolder>() {

    // Pre-index categories into a HashMap once: O(m) preparation
    private val categoryMap: Map<String, String> = categories.associate { it.id to it.displayName }

    override fun onBindViewHolder(holder: CartViewHolder, position: Int) {
        val item = items[position]
        // Instant O(1) map lookup -> Total list binding is O(n)
        val categoryName = categoryMap[item.categoryId] ?: ""
        holder.bind(item, categoryName)
    }

    override fun getItemCount(): Int = items.size
}
```""",
    "short_en": """Identify accidental O(n^2) transformations in UI lists by profiling scroll passes in Android Studio CPU Profiler or Perfetto, looking for wide spikes in ArrayList.contains or firstOrNull inside onBindViewHolder or Compose rows. Eliminate this anti-pattern by pre-indexing lookup lists into HashSets or HashMaps in the ViewModel, restoring binding complexity to O(1) per item and O(n) overall.""",
    "structured_en": """Accidental quadratic complexity in Android UI lists is one of the most common causes of dropped frames and visual stutter during scrolling.
The defect occurs when an engineer unintentionally embeds a linear O(n) search inside an item binding callback. A classic example is calling contains on an ArrayList of selected IDs inside onBindViewHolder, or calling firstOrNull on a categories list inside a Jetpack Compose LazyColumn row. Because the list binds n items, executing a linear scan for each row multiplies operations into a disastrous O(n^2) workload on the main thread.
To detect this issue, we capture a System Trace using Perfetto or the Android Studio CPU Profiler during active scrolling. The flame chart reveals massive execution blocks dominated by ArrayList indexOf rather than view measurement or layout passes.
We resolve this by pre-computing lookup collections before passing data to the UI. Converting secondary lists into a HashSet or HashMap allows each row to retrieve its data in constant O(1) time, permanently restoring overall list rendering to smooth O(n) linear performance.""",
    "deep_senior_en": """From an Android UI rendering internals and frame-rate optimization standpoint, accidental O of n squared transformations represent a catastrophic breakdown of architectural discipline.
The Android Choreographer enforces a relentless frame cadence: a frame must be prepared, measured, drawn, and submitted to the hardware surface every sixteen milliseconds for 60Hz panels, or every eight milliseconds for 120Hz displays. When an engineer writes an onBindViewHolder or LazyColumn row that executes a linear search over a secondary collection, that computation runs synchronously on the main thread during the scroll gesture. If a catalog contains two thousand items and the user scrolls rapidly, searching through lists on each bind pass consumes tens of milliseconds, blowing past the frame budget and causing severe visual Jank.
Diagnosing this bottleneck requires evidence-based profiling rather than code skimming. In Android Studio CPU Profiler or Perfetto trace recordings, an algorithmic quadratic bottleneck displays a distinct signature: long, uninterrupted call stacks on the main thread where the overwhelming majority of CPU samples reside in java.util.ArrayList.indexOf, ArrayList.contains, or Kotlin CollectionsKt.find. Meanwhile, the GPU RenderThread sits completely idle, waiting for the main thread to unblock.
The remediation is structural. We mandate that UI adapters and Compose rows receive fully prepared, presentation-ready ViewModels. If items require enrichment from secondary datasets, the ViewModel pre-indexes the secondary list into a Map or transforms an ID list into a HashSet ahead of time on Dispatchers.Default. Inside onBindViewHolder, looking up properties becomes a sub-microsecond O of one operation. The entire screen binding pass completes in deterministic linear time, guaranteeing smooth, stutter-free scrolling across even the most constrained low-end devices.""",
    "meta_ar": {
        "id": "DSA-12",
        "questionAr": "كيف تكتشف وتعالج التعقيد التربيعي العرضي (Accidental O(n²)) في قوائم RecyclerView أو Compose؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "تشخيص التعقيد التربيعي العرضي في واجهات أندرويد، كشف استدعاءات البحث الخطي (contains, find) داخل دوال الربط (onBindViewHolder / LazyColumn)، استخدام Android Profiler وPerfetto، والحل عبر الفهرسة المسبقة بـ HashSet وHashMap.",
        "concept_ar": "يحدث التعقيد التربيعي العرضي (Accidental O(n^2)) في واجهات أندرويد عندما يضع المطور عملية بحث خطية $O(n)$ دون قصد داخل دالة ربط العناصر التي تتكرر $O(n)$ مرات: من أشهر الأمثلة استدعاء `selectedIdsList.contains(item.id)` على قائمة ArrayList عادية داخل دالة `onBindViewHolder`، أو استدعاء `categories.first { it.id == item.catId }` داخل صف في Compose LazyColumn؛ مما يحول رسم القائمة من عملية خطية سلسة إلى كارثة تربيعية $n \times O(n) = O(n^2)$ تجمد خيط الواجهة أثناء التمرير وتسقط عشرات الإطارات. ويتم اكتشاف هذه المشكلة عبر تسجيل مسار الأداء (System Trace / Perfetto) في Android Studio؛ حيث يظهر الرسم البياني هيمنة دوال `ArrayList.indexOf` أو `contains` على وقت المعالج بدلاً من دوال الرسم. ويكمن العلاج المعماري في الفهرسة المسبقة للبيانات (Pre-indexing) داخل الـ ViewModel بتحويل القوائم الثانوية إلى `HashSet` أو `HashMap` قبل إرسالها للواجهة؛ مما يجعل الوصول لكل عنصر فورياً بتعقيد ثابت $O(1)$ ويعيد معالجة القائمة بأكملها إلى الكفاءة الخطية $O(n)$.",
        "walkthrough_ar": """إصلاح التعقيد التربيعي العرضي بتحويل البحث إلى O(1) في كوتلن:
```kotlin
data class Product(val id: String, val name: String, val categoryId: String)
data class Category(val id: String, val name: String)

// المعالجة المعمارية الصحيحة في ViewModel: الفهرسة المسبقة في خيط الخلفية
class ProductListViewModel : ViewModel() {

    fun prepareUiState(products: List<Product>, categories: List<Category>): List<ProductUiModel> {
        // تحويل قائمة الفئات إلى HashMap مرة واحدة مسبقاً: O(m)
        val categoryMap = categories.associate { it.id to it.name }

        // تحويل المنتجات في مرور خطي واحد: O(n)
        return products.map { p ->
            ProductUiModel(
                id = p.id,
                name = p.name,
                categoryName = categoryMap[p.categoryId] ?: "عام" // وصول O(1)
            )
        }
    }
}
```""",
        "why_it_matters_ar": "التعقيد التربيعي في القوائم هو السبب الأول لسقوط الإطارات وتهنيج الشاشات أثناء التمرير، وتحويله إلى خطي ينقذ التطبيق من التقييمات السلبية.",
        "worked_example_ar": "في قائمة تضم 1500 منتج، كان البحث عن اسم الفئة بـ first داخل onBindViewHolder يستغرق 35ms لكل إطار ويجمد الشاشة؛ وبتحويلها لـ HashMap انخفض الوقت لـ 0.2ms وعادت الشاشة لـ 60fps.",
        "trade_offs_ar": "الفهرسة المسبقة تستهلك مقداراً بسيطاً جداً من الذاكرة لبناء HashMap؛ في مقابل إنقاذ المعالج من ملايين المقارنات وضمان استجابة لحظية في واجهة المستخدم.",
        "failure_modes_ar": "أخطر الأخطاء هو فحص كود الواجهة بالعين المجردة دون استخدام Profiler، أو استخدام contains على List داخل DiffUtil.areItemsTheSame مما يشل عملية مقارنة القوائم بالكامل.",
        "production_perspective_ar": "في كود الإنتاج، نلزم المطورين بتجهيز UiState يحتوي على نصوص كاملة وجاهزة للعرض المباشر، ويُحظر تماماً تمرير قوائم ثانوية للمهايئ (Adapter) للبحث بداخلها.",
        "how_to_answer_ar": "ابدأ بشرح كيف ينشأ التعقيد التربيعي من وضع بحث خطي داخل حلقة القائمة، ثم وضح كيفية اكتشافه بـ Perfetto وProfiler، واشرح الحل المعماري عبر الفهرسة المسبقة بـ HashMap.",
        "talking_points_ar": "التعقيد التربيعي العرضي، دالة onBindViewHolder، فحص contains على ArrayList، تشخيص Perfetto وCPU Flame Chart، حل الفهرسة المسبقة Pre-indexing، ومفهوم UiState الجاهز للعرض.",
        "follow_ups_ar": "كيف تتجنب نفس الفخ في Jetpack Compose عند التعامل مع عناصر مشتقة عبر derivedStateOf؟ وما أثر تكرار حساب الهاش داخل LazyColumn؟",
        "self_check_ar": "هل شرحت كيف يتحول الكود لـ O(n^2)، وطريقة كشفه بأدوات التحليل، وعلاجه بالفهرسة المسبقة في الـ ViewModel؟",
        "references_ar": f"- [Android Developers: Inspect CPU activity with CPU Profiler](https://developer.android.com/studio/profile/cpu-profiler) — الدليل الرسمي لتحليل المسار الحرج للمهام واكتشاف اختناقات المعالج.\n- [Android Developers: Performance in Jetpack Compose](https://developer.android.com/jetpack/compose/performance) — أفضل الممارسات لتجنب الحسابات المكلفة داخل دوال الرسم وإعادة التركيب.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """نكتشف التعقيد التربيعي العرضي بتسجيل الأداء بـ CPU Profiler أو Perfetto، حيث تظهر كتل زمنية عريضة لدوال ArrayList.contains أو find داخل onBindViewHolder أو صفوف Compose. ونعالج ذلك بنقل البحث خارج الواجهة وتجهيز خريطة HashMap أو HashSet مسبقاً في الـ ViewModel، ليصبح الوصول لحظياً بـ O(1) وتعود القائمة للكفاءة الخطية O(n).""",
        "best_answer_ar": """يمثل التعقيد التربيعي العرضي في واجهات أندرويد السبب الأبرز لسقوط الإطارات وتقطيع الشاشة أثناء التمرير في القوائم.
تنشأ المشكلة عندما يستدعي المطور دالة بحث خطية مثل contains أو firstOrNull على قائمة عادية داخل دالة ربط العناصر onBindViewHolder أو داخل صف في Compose LazyColumn. ولأن القائمة تحتوي على ن من العناصر، فإن تنفيذ بحث خطي لكل عنصر يحول الرسم إلى عملية تربيعية كارثية O(n^2) تستهلك عشرات المللي ثواني على خيط الواجهة.
ونكتشف هذه المشكلة عبر تسجيل مسار النظام بأداة Perfetto أو CPU Profiler أثناء التمرير؛ حيث يكشف المخطط البياني عن هيمنة دوال البحث النصي في ArrayList بدلاً من دوال قياس ورسم الواجهة، مع إطلاق إنذار بسقوط عشرات الإطارات.
ونعالج هذا الخلل هندسياً بالفهرسة المسبقة للبيانات في الـ ViewModel؛ حيث نحول القوائم الثانوية إلى جدول تجزئة HashMap أو مجموعة HashSet في خيط الخلفية قبل تمرير الحالة للشاشة. وبذلك يتحول الوصول لكل عنصر إلى تعقيد ثابت O(1)، مما يعيد المعالجة الإجمالية إلى مسار خطي فائق النعومة.""",
        "deep_answer_ar": """من منظور معمارية رسم الواجهات والتحكم في معدل الإطارات بأجهزة أندرويد، يمثل التعقيد التربيعي العرضي فشلاً معمارياً يعطل منظومة العرض البصري بالكامل.
تفرض شاشات الهواتف الحديثة ميزانية زمنية حاسمة لا تتجاوز ثمانية مللي ثوانٍ للشاشات بتردد مئة وعشرين هرتز. وعندما يدمج المطور بحثاً خطياً داخل دورة الربط، يتفاجأ Choreographer بوجود عمليات حسابية طويلة تحجب خيط الواجهة الرئيسي وتمنعه من إرسال أوامر الرسم لمعالج الرسوميات RenderThread الذي يظل معطلاً بانتظار فك الاختناق.
وتشخيص هذه العلة لا يتم بالتخمين المجرد بل بالاعتماد على أدوات قياس النظم؛ ففي مخططات Perfetto، تظهر بصمة واضحة للتعقيد التربيعي تتمثل في كتل زمنية مستمرة تحتكر خيط العرض الرئيسي، وتتركز معظم عينات المعالج داخل توابع ArrayList.indexOf أو دوال الفرز والتصفية المتكررة.
والعلاج الجذري يكمن في الفصل الصارم بين معالجة البيانات وعرضها؛ فنلزم المعمارية بتجهيز كائنات UiModel كاملة ومفهرسة مسبقاً داخل الـ ViewModel بالاعتماد على Dispatchers.Default. وتُحول المعرفات والبيانات المرجعية إلى هياكل سريعة كالـ HashSets والـ Maps؛ ليقتصر دور المهايئ في onBindViewHolder على استدعاء مباشر في زمن O of one حتمي. هذا الانضباط المعماري يحافظ على نقاء خيط الواجهة ويضمن تجربة تمرير انسيابية ومستقرة عبر كافة الأجهزة وتفادي أي سقوط للإطارات حتى مع آلاف العناصر المعقدة ذات التراكيب المتشابكة."""
    }
}

# ==========================================
# DSA-13: How can Kotlin collection chaining create temporary allocations?
# ==========================================
DATA["DSA-13"] = {
    "concept_en": """Chaining standard Kotlin collection transformations evaluates eagerly, creating intermediate collection allocations that inflate heap consumption and garbage collection churn:
- Eager Evaluation Mechanics:
  - Standard library operations on `Iterable` (`map`, `filter`, `take`, `groupBy`) are eager and greedy.
  - Each individual transformation constructs, populates, and returns a completely new `ArrayList` instance on the heap.
  - Example: `users.filter { it.isActive }.map { it.name }.take(10)`
    - Step 1: `filter` creates and populates a new `ArrayList` containing all active users.
    - Step 2: `map` creates a second new `ArrayList` containing the transformed names of all active users.
    - Step 3: `take` creates a third `ArrayList` containing the first 10 names.
    - Result: The two large intermediate lists from steps 1 and 2 become immediate garbage on the heap.
- Impact on the Android Runtime (ART):
  - Generates severe Memory Churn: Fast allocation and discarding of temporary arrays quickly fills ART\'s young-generation (nursery) heap space.
  - Triggers frequent Concurrent Mark-Sweep and Generational GC cycles. Each GC cycle consumes CPU cores and introduces micro-pauses that cause visual stutter in scrolling lists and animations.
- Remediation via Lazy Sequences (`asSequence()`):
  - Sequences evaluate lazily using a streaming, element-by-element pipeline.
  - An element passes through `filter`, then `map`, then `take` before the next element is processed.
  - Zero intermediate collection allocations.
  - Short-circuiting efficiency: Terminal operators like `take(10)` or `first()` stop pipeline execution as soon as the condition is satisfied, avoiding evaluating the remaining thousands of items.
- When NOT to Use Sequences:
  - For very small collections ($n < 20$), the overhead of allocating the `Sequence` wrapper and iterator state machine exceeds the cost of simple array allocation. Direct loops (`for`) or eager collections are faster for small $n$.""",
    "walkthrough_en": """Demonstrating intermediate allocation churn vs lazy Sequences in Kotlin:
```kotlin
data class Transaction(val id: String, val amount: Double, val isPending: Boolean)

// ANTI-PATTERN: Eager collection chaining creates multiple temporary ArrayLists on the heap
fun getTopTenPendingEager(transactions: List<Transaction>): List<Double> {
    return transactions
        .filter { it.isPending } // Allocates Temporary List 1 (e.g. 5,000 items)
        .map { it.amount }       // Allocates Temporary List 2 (e.g. 5,000 items)
        .take(10)                // Allocates Final List 3 (10 items)
    // Lists 1 and 2 are immediately discarded, triggering aggressive GC pauses!
}

// BEST PRACTICE: Lazy Sequence pipeline with ZERO intermediate collection allocations
fun getTopTenPendingLazy(transactions: List<Transaction>): List<Double> {
    return transactions
        .asSequence()            // Switch to lazy evaluation
        .filter { it.isPending } // Evaluated element-by-element
        .map { it.amount }
        .take(10)                // Short-circuits after finding 10 items!
        .toList()                // Single final collection allocation
}
```""",
    "short_en": """Kotlin collection chaining evaluates eagerly, where each map or filter step constructs and populates a new temporary ArrayList on the heap. On Android, this creates severe memory churn that triggers frequent garbage collection pauses during scrolling. Remediate this by using asSequence() to evaluate items lazily in a single pass without intermediate collections, short-circuiting early when possible.""",
    "structured_en": """Chaining transformation functions on standard Kotlin collections introduces significant memory overhead due to eager evaluation.
When applying chained operators like filter, map, and sorted on a standard Iterable, each step immediately evaluates the entire collection and returns a brand-new intermediate ArrayList on the heap. In a chain of three operations over a list of ten thousand items, two large intermediate lists are allocated and instantly discarded, serving no purpose other than passing data to the next step.
In Android environments, this behavior causes rapid memory churn. Filling the heap with transient collections forces the Android Runtime garbage collector to run repeatedly, inducing micro-pauses that drop frames during UI scrolling and animations.
We eliminate intermediate allocations by converting collections into lazy streams using asSequence. Sequences evaluate operations element by element in a single pipeline, allocating only the final collection. Furthermore, Sequences support short-circuiting, meaning operations like take or first terminate evaluation immediately upon reaching their quota, avoiding processing the remaining data entirely.""",
    "deep_senior_en": """From an ART memory allocator and language runtime perspective, eager collection chaining is a hidden performance tax that frequently degrades high-scale mobile applications.
Under the hood, Kotlin\'s standard library collection extensions are simple inline loops that instantiate ArrayLists. When a pipeline executes list.filter followed by list.map, the filter function iterates the source, allocates an internal backing array, and returns a populated list. The map function then inspects this new list, allocates another array, and transforms its contents. For a dataset of twenty thousand network entities, this pipeline allocates tens of thousands of object references across temporary array buffers.
In the Android Runtime, memory churn of this magnitude accelerates generational garbage collection. The young generation fills up in milliseconds, triggering concurrent GC passes that steal CPU cycles from the main thread and Choreographer. If memory becomes fragmented, the runtime enforces stop-the-world pauses, resulting in visible Jank.
Senior engineers mitigate this through lazy evaluation. Converting the pipeline with asSequence() substitutes eager array creation with an iterator-based state machine. Each element flows vertically through filter, map, and downstream operators before the next element is fetched. No intermediate lists are ever allocated. Moreover, Sequences enable short-circuiting: a pipeline with take(10) halts after locating ten matching records, entirely bypassing the evaluation of the remaining nineteen thousand items.
However, architectural pragmatism requires recognizing boundaries. For small collections under twenty items, the iterator state machine of a Sequence incurs more allocation overhead than a simple eager list. Understanding this trade-off ensures we apply Sequences where they deliver genuine garbage collection relief.""",
    "meta_ar": {
        "id": "DSA-13",
        "questionAr": "كيف تتسبب سلاسل دوال المجموعات (Collection Chaining) في كوتلن في حجز كائنات مؤقتة، وكيف تتفاداها؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم التقييم العاجل (Eager Evaluation) في مجموعات كوتلن، حجز القوائم الوسيطة في الذاكرة، ظاهرة تقلب الذاكرة (Memory Churn) وإجهاد مجمع القمامة (GC Pauses)، والحل المعماري عبر التسلسلات الكسولة (Sequences).",
        "concept_ar": "تعمل دوال تحويل المجموعات القياسية في كوتلن (مثل `map` و`filter` و`take`) بأسلوب التقييم العاجل (Eager Evaluation)؛ مما يعني أن كل دالة في السلسلة تنشئ وتملأ قائمة جديدة كاملة (`ArrayList`) على الـ Heap وتمررها للدالة التالية: فلو طبقنا `list.filter { ... }.map { ... }.take(10)` على قائمة تضم 10,000 عنصر، سيتم حجز قائمتين وسيطتين ضخمتين في الذاكرة ومسحهما فوراً بعد انتهاء السلسلة. وتؤدي هذه الظاهرة إلى ما يُعرف بتقلب الذاكرة الحاد (Memory Churn)؛ حيث يمتلئ الجيل الصغير في ذاكرة ART بسرعة فائقة، مما يجبر مجمع القمامة (GC) على تشغيل دورات تنظيف متتالية توقف معالجة الشاشة مؤقتاً (GC Pauses) وتسبب سقوط الإطارات. ونتفادى هذه المشكلة باستخدام التسلسلات الكسولة (`asSequence()`)؛ حيث تتدفق العناصر رأسياً واحداً تلو الآخر عبر السلسلة دون إنشاء أي قوائم وسيطة، مع ميزة التوقف المبكر (Short-circuiting) فور تلبية شرط `take(10)` دون معالجة باقي العناصر.",
        "walkthrough_ar": """مقارنة عملية بين الحجز المتكرر في القوائم العادية وانعدامه في كوتلن Sequences:
```kotlin
data class Order(val id: String, val total: Double, val isCompleted: Boolean)

// نمط معطوب: ينشئ قائمتين وسيطتين ضخمتين في الذاكرة (Memory Churn)
fun getCompletedTotalsEager(orders: List<Order>): List<Double> {
    return orders
        .filter { it.isCompleted } // ينشئ قائمة وسيطة 1
        .map { it.total }          // ينشئ قائمة وسيطة 2
        .take(5)                   // ينشئ القائمة النهائية 3
}

// النمط الهندسي الأمثل: استخدام Sequences لصفرية القوائم الوسيطة
fun getCompletedTotalsLazy(orders: List<Order>): List<Double> {
    return orders
        .asSequence()              // تحويل التقييم لكسول (Lazy)
        .filter { it.isCompleted } // معالجة عنصر بعنصر
        .map { it.total }
        .take(5)                   // توقف فوري بمجرد العثور على 5 عناصر!
        .toList()                  // حجز قائمة واحدة نهائية فقط
}
```""",
        "why_it_matters_ar": "توليد قوائم وسيطة ضخمة يرهق مجمع القمامة ويسبب تقطيعاً ملحوظاً في التمرير، بينما Sequences توفر الذاكرة وتسرع المعالجة.",
        "worked_example_ar": "في شاشة عرض المعاملات، استبدلنا سلاسل العمليات على 5000 عنصر بـ asSequence؛ فانخفض استهلاك الذاكرة المؤقتة من 4MB إلى بضعة كيلوبايتات واختفت وقفات الـ GC تماماً.",
        "trade_offs_ar": "استخدام Sequences يوفر الذاكرة في المجموعات الكبيرة ولكنه يضيف كلفة استدعاء لمؤشرات الكائنات؛ ولذلك في المجموعات الصغيرة جداً (أقل من 20 عنصراً) تكون القوائم العادية أسرع.",
        "failure_modes_ar": "أخطر الأخطاء هو استخدام Sequences مع مجموعات صغيرة جداً مما يزيد كلفة الكائنات العابرة، أو استخدام عمليات فرز مكلفة مثل sorted داخل Sequence مما يلغي ميزة المعالجة الفورية للعناصر.",
        "production_perspective_ar": "في كود الإنتاج، نلزم استخدام asSequence() في أي سلسلة تحويل تضم أكثر من دالتين على مجموعات غير محدودة الحجم، ونستخدم حلقة for بسيطة عند الرغبة في الأداء الأقصى.",
        "how_to_answer_ar": "ابدأ بشرح التقييم العاجل وكيف تنشئ كل دالة قائمة ArrayList جديدة، ثم وضح خطر Memory Churn على الـ GC وسقوط الإطارات، واشرح الحل عبر asSequence وميزة التوقف المبكر.",
        "talking_points_ar": "التقييم العاجل Eager Evaluation، القوائم الوسيطة Intermediate Lists، تقلب الذاكرة Memory Churn، دورات مجمع القمامة GC Pauses، التسلسلات الكسولة Sequences، وميزة Short-circuiting.",
        "follow_ups_ar": "كيف تؤثر عملية مثل sortedBy على سلوك Sequence الكسول؟ ومتى تكون حلقة for المباشرة أفضل أداءً من Sequence في كوتلن؟",
        "self_check_ar": "هل شرحت حجز القوائم الوسيطة وأثره على الـ GC، وقدمت حل asSequence() مع التوقف المبكر، وذكرت استثناء المجموعات الصغيرة؟",
        "references_ar": f"- [Kotlin Documentation: Sequences](https://kotlinlang.org/docs/sequences.html) — الدليل الرسمي لاستخدام التسلسلات الكسولة وتفادي الحجز الوسيط في كوتلن.\n- [Android Developers: Manage your app\'s memory](https://developer.android.com/topic/performance/memory) — أفضل الممارسات لإدارة الذاكرة وتقليل ضغط مجمع القمامة.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """تنشئ سلاسل دوال المجموعات في كوتلن قوائم وسيطة جديدة كـ ArrayList في كل خطوة تحويل بسبب التقييم العاجل، مما يسبب تقلب الذاكرة وإجهاد مجمع القمامة وتجمد الشاشات. ونتفادى ذلك باستخدام asSequence لتحويل التقييم إلى كسول؛ حيث تعالج العناصر بالتتابع دون قوائم وسيطة مع توقف فوري للعمليات المقيدة كـ take.""",
        "best_answer_ar": """ينتج استهلاك الذاكرة المفرط في سلاسل دوال كوتلن عن طبيعة التقييم العاجل الذي تتبعه المجموعات القياسية.
فعند تطبيق دوال مثل filter وmap على قائمة عادية، تنفذ كل دالة عمليتها على كامل المجموعة وتبني في الذاكرة قائمة ArrayList جديدة بالكامل؛ فإذا تضمنت السلسلة ثلاث عمليات على عشرة آلاف عنصر، يتم تخصيص قائمتين وسيطتين ضخمتين على الـ Heap والاستغناء عنهما فورياً.
وفي أجهزة أندرويد، يؤدي هذا الإهدار إلى ظاهرة تقلب الذاكرة السريع؛ حيث تمتلئ ذاكرة التطبيق بكائنات عابرة تجبر مجمع القمامة على التدخل بوقفات متكررة تسرق موارد المعالج وتسقط إطارات التمرير والرسوم المتحركة.
ولحل هذه المعضلة، نحول المجموعة إلى تسلسل كسول باستخدام دالة asSequence؛ حيث تلغي التسلسلات حجز القوائم الوسيطة وتمرر كل عنصر بمفرده عبر خط الأنابيب البرمجي بالكامل. وتتميز Sequences أيضاً بخاصية التوقف المبكر؛ فدوال مثل take تنهي المعالجة بمجرد استيفاء العدد المطلوب دون معالجة بقية العناصر، مما يوفر الذاكرة ويحافظ على انسيابية التطبيق.""",
        "deep_answer_ar": """من منظور إدارة ذاكرة ART وهندسة لغة كوتلن، تمثل سلاسل التحويل العاجلة ضريبة خفية تؤثر سلباً على أداء التطبيقات واسعة الانتشار.
داخلياً، صُممت دوال التوسعة للمجموعات في كوتلن كحلقات تكرارية عادية تنشئ كائنات مصفوفات جديدة؛ فدالة filter تحجز مصفوفة وتملأها، ثم تأتي دالة map لتحجز مصفوفة ثانية، مما يولد آلاف الكائنات والمؤشرات في زمن قياسي.
وفي بيئة تشغيل أندرويد، يؤدي هذا التدفق المستمر للكائنات العابرة إلى ملء الجيل الشاب من ذاكرة الـ Heap في أجزاء من الثانية؛ مما يجبر محرك ART على تشغيل دورات تنظيف القمامة المتزامنة، وقد تتطور إلى وقفات حتمية تعلق خيط واجهة المستخدم وتفقد الشاشة معدل الستين إطاراً في الثانية.
والنهج الهندسي الرصين يعتمد على التقييم الكسول عبر Sequences؛ حيث يُستبدل حجز المصفوفات بمحرك حالات يعتمد على مكررات الذاكرة. فيتدفق العنصر الأول عبر كافة شروط التصفية والتحويل قبل استدعاء العنصر الثاني، دون الحاجة لأي قائمة وسيطة. كما تبرز القوة الحقيقية في عمليات الاقتصار؛ فعند استدعاء take بخمسة عناصر، يتوقف التدفق فوراً، متجاهلاً آلاف السجلات المتبقية.
ومع ذلك، يلتزم مهندس النظم بالحذر؛ ففي المجموعات الصغيرة التي تقل عن عشرين عنصراً، تكون كلفة إنشاء كائنات التسلسل أعلى من القائمة العادية، مما يتطلب موازنة واعية بين حجم البيانات والأداة المختارة."""
    }
}

# ==========================================
# DSA-14: A product list freezes on low-end devices. How do you distinguish rendering bottlenecks from algorithmic complexity?
# ==========================================
DATA["DSA-14"] = {
    "concept_en": """Diagnosing UI thread freezing requires empirical profiling using Android Studio System Trace (Perfetto) to isolate algorithmic CPU computation from UI layout/rendering pipeline bottlenecks:
- Diagnostic Instrumentation via System Trace (Perfetto):
  - Record active scrolling traces on budget test hardware to capture exact thread timelines across the Main Thread, Choreographer, RenderThread, and GPU.
- Signature 1: Algorithmic Complexity Bottleneck:
  - Main Thread Timeline: Displays massive, continuous execution blocks inside application business logic (e.g., `DiffUtil.calculateDiff`, JSON deserialization, `List.filter`, in-memory sorting, or database querying).
  - Choreographer State: `Choreographer.doFrame()` is blocked from executing on time because the Main Thread is held hostage by heavy CPU calculations.
  - RenderThread & GPU State: Completely idle! RenderThread sits starved waiting for the Main Thread to finish business logic and dispatch display lists.
  - Remediation: Offload computation to `Dispatchers.Default`, optimize complexity from $O(n^2)$ to $O(n)$ using HashMaps, or memoize calculations.
- Signature 2: UI Rendering Pipeline Bottleneck:
  - Main Thread Timeline: Spends excessive time inside platform view traversal methods: `View.measure()`, `View.layout()`, or Jetpack Compose `LayoutNode.measure`.
  - Cause: Deeply nested layouts (e.g., multiple nested `RelativeLayouts` or complex `ConstraintLayout` barriers) forcing multi-pass exponential measurement passes.
  - RenderThread & GPU Timeline: RenderThread shows huge spikes inside `DrawFrame` and GPU synchronization.
  - Overdraw Inspection: The Device Developer Options "Debug GPU Overdraw" shows extensive red zones, indicating pixels being redrawn 4+ times per frame.
  - Remediation: Flatten view hierarchies, migrate to Jetpack Compose, use `remember` to skip recompositions, reduce overdraw, and downscale images before decoding.""",
    "walkthrough_en": """Profiling and isolating algorithmic vs rendering bottlenecks in Android:
```kotlin
// Scenario: Optimizing product list that drops frames on low-end hardware

// 1. Algorithmic Fix: Move heavy filtering and sorting off the Main Thread
class ProductViewModel(private val repository: ProductRepository) : ViewModel() {
    private val _uiState = MutableStateFlow<List<ProductUiModel>>(emptyList())
    val uiState: StateFlow<List<ProductUiModel>> = _uiState

    fun loadProducts() {
        viewModelScope.launch {
            // Offload heavy O(n log n) sorting and mapping to Background Worker Pool
            val processedList = withContext(Dispatchers.Default) {
                val rawProducts = repository.getProducts()
                rawProducts
                    .asSequence()
                    .filter { it.inStock }
                    .sortedBy { it.price }
                    .map { it.toUiModel() }
                    .toList()
            }
            // Dispatch strictly presentation-ready data to UI
            _uiState.value = processedList
        }
    }
}

// 2. Rendering Fix in Compose: Use remember and keys to prevent layout thrashing
@Composable
fun ProductList(products: List<ProductUiModel>) {
    LazyColumn {
        items(
            items = products,
            key = { it.id } // Enables smart item reuse without full remeasuring
        ) { product ->
            ProductRow(product)
        }
    }
}
```""",
    "short_en": """Distinguish rendering from algorithmic bottlenecks using Android Studio System Trace (Perfetto). An algorithmic bottleneck shows the Main Thread blocked by business logic or collection loops while the RenderThread sits idle. A rendering bottleneck shows excessive time in View.measure, View.layout, or long RenderThread DrawFrame passes with GPU overdraw. Fix algorithmic issues with background dispatchers and rendering issues by flattening layouts.""",
    "structured_en": """Differentiating between rendering bottlenecks and algorithmic complexity requires analyzing thread traces in Android Studio System Trace or Perfetto rather than guessing.
When an algorithmic bottleneck causes the freeze, the CPU trace shows the main thread monopolized by application business code, such as DiffUtil calculations, sorting, or collection transformations. In this scenario, Choreographer is blocked from running, while the RenderThread and GPU sit completely idle waiting for display list commands.
Conversely, a rendering bottleneck displays the opposite profile. The main thread spends excessive time within platform layout methods like View.measure and View.layout, typically caused by deeply nested layouts forcing multi-pass measurement. Furthermore, the RenderThread displays long DrawFrame durations, and GPU overdraw inspection shows pixels being redrawn multiple times.
Once identified, algorithmic bottlenecks are resolved by moving work to Dispatchers.Default and optimizing data structures. Rendering bottlenecks are resolved by flattening view hierarchies, optimizing Compose recomposition scopes, and downscaling images.""",
    "deep_senior_en": """From a systems profiling and platform diagnostics perspective, resolving UI freezing on low-end Android hardware demands an evidence-driven triage process.
The primary diagnostic tool is System Trace via Perfetto. When analyzing a dropped frame trace, we inspect the synchronized timelines of the Main Thread and RenderThread. An algorithmic bottleneck produces an unmistakable signature: the Main Thread exhibits continuous, uninterrupted slices inside application code—such as GSON parsing, collection filtering, or quadratic search loops. Choreographer doFrame events are visibly pushed beyond the sixteen-millisecond boundary. Crucially, the RenderThread is starved of work, exhibiting empty gaps while awaiting sync frames from the main thread.
A rendering bottleneck presents a distinctly different pathology. The Main Thread is not running business logic; instead, it is bogged down in platform UI traversal. You observe massive spikes in View.measure and View.layout. In legacy views, this indicates multi-pass layout hierarchy penalties, such as nested RelativeLayouts with wrap_content dependencies that trigger exponential measurement passes. In Jetpack Compose, this manifests as excessive recomposition loops across unstable lambdas. Concurrently, the RenderThread shows protracted DrawFrame and queueBuffer slices, while GPU Profiler highlights severe overdraw where stacked background drawables paint the same pixel five times per frame.
Remediation requires targeted architectural intervention. For algorithmic defects, we offload heavy computation to Dispatchers.Default, optimize list operations to linear O of n using HashMaps, and ensure DiffUtil runs asynchronously. For rendering defects, we flatten the layout tree, remove redundant background colors to eliminate overdraw, configure Compose item keys to enable smart layout reuse, and ensure bitmaps are downsampled to exact view dimensions before decoding into memory.""",
    "meta_ar": {
        "id": "DSA-14",
        "questionAr": "قائمة منتجات تتجمد على الأجهزة الاقتصادية. كيف تميز بين اختناقات الرسم (Rendering) والتعقيد الخوارزمي (Algorithmic Complexity)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "تشخيص الأداء بـ System Trace وPerfetto، تمييز بصمة التعقيد الخوارزمي (Main Thread مشغول والـ RenderThread عاطل)، تمييز بصمة اختناقات الرسم (View.measure, Overdraw, Compose Recomposition)، والحلول المعمارية لكل حالة.",
        "concept_ar": "يتطلب تشخيص تجمد القوائم في أندرويد استخدام أدوات القياس الدقيقة عبر مسار النظام (System Trace / Perfetto) في Android Studio بدلاً من التخمين لفصل مشاكل المعالج عن مشاكل معالج الرسوميات: بصمة التعقيد الخوارزمي (Algorithmic Bottleneck): يظهر خيط الواجهة (Main Thread) محتجزاً بكتل زمنية طويلة داخل شفرة منطق العمل (مثل فرز القوائم، أو حسابات DiffUtil، أو فك تشفير JSON، أو حلقات البحث)؛ بينما يظل خيط الرسم (RenderThread) ومعالج الرسوميات (GPU) في حالة خمول تام (Idle) بانتظار إفراج الـ Main Thread عن أوامر العرض. ويُعالج ذلك بنقل الحسابات لخيوط الخلفية (`Dispatchers.Default`) وتحسين التعقيد إلى $O(n)$. أما بصمة اختناقات الرسم (Rendering Bottleneck): فيقضي خيط الواجهة وقتاً طويلاً داخل دوال قياس وحساب أبعاد العناصر (`View.measure` و`View.layout`) بسبب تداخل الطبقات (Nested Layouts) أو إعادة التركيب الزائدة في Compose؛ ويظهر خيط RenderThread مستهلكاً في نداءات `DrawFrame` مع ظهور مناطق حمراء داكنة في أداة فحص الرسم الزائد (GPU Overdraw). ويُعالج ذلك بتسطيح طبقات الواجهة وحذف الخلفيات المكررة وتصغير الصور قبل فك تشفيرها.",
        "walkthrough_ar": """حل عملي لنقل الحسابات للخلفية وضبط كفاءة الرسم في أندرويد:
```kotlin
// 1. معالجة التعقيد الخوارزمي: نقل الفرز والتصفية لخيوط الخلفية
class ProductViewModel(private val repo: ProductRepository) : ViewModel() {
    val productsState = MutableStateFlow<List<ProductUiModel>>(emptyList())

    fun loadData() {
        viewModelScope.launch {
            // معالجة القائمة على Dispatchers.Default لمنع حجز خيط الواجهة
            val uiModels = withContext(Dispatchers.Default) {
                repo.getProducts()
                    .asSequence()
                    .filter { it.isAvailable }
                    .sortedBy { it.price }
                    .map { it.toUiModel() }
                    .toList()
            }
            productsState.value = uiModels // إرسال بيانات جاهزة للرسم
        }
    }
}

// 2. معالجة اختناق الرسم في Compose: استخدام keys لتجنب إعادة الحسابات
@Composable
fun ProductListScreen(products: List<ProductUiModel>) {
    LazyColumn {
        items(
            items = products,
            key = { it.id } // يمنع إعادة قياس وتكوين العناصر غير المتغيرة
        ) { product ->
            ProductCard(product)
        }
    }
}
```""",
        "why_it_matters_ar": "علاج الخلل بالافتراض الخاطئ (مثل تعديل الواجهة بينما المشكلة في خوارزمية فرز ثقيلة) يهدر وقت الفريق ولا يحل مشكلة تجمد الشاشة.",
        "worked_example_ar": "فحصنا تجمد قائمة بـ Perfetto؛ فاكتشفنا أن خيط الواجهة يستغرق 40ms في DiffUtil بينما RenderThread عاطل؛ فنقلنا الحسابات لـ Dispatchers.Default وعادت الشاشة لـ 60fps.",
        "trade_offs_ar": "نقل المعالجة للخلفية Dispatchers.Default يحمي خيط الواجهة ولكنه يتطلب إدارة التزامن عبر StateFlow؛ بينما إصلاح الرسم يتطلب إعادة هيكلة ملفات XML وCompose.",
        "failure_modes_ar": "أخطر الأخطاء هو محاولة تسريع القائمة بحذف الرسوميات بينما السبب الحقيقي هو وجود دالة بحث O(n^2) داخل المهايئ، أو تجاهل فحص GPU Overdraw على الأجهزة الاقتصادية.",
        "production_perspective_ar": "في الفرق الكبرى، يُجرى اختبار تجمد القوائم على أضعف الأجهزة المستهدفة فعلياً (Low-End Test Devices) مع تفعيل إظهار الـ Overdraw باللون الأحمر للتحقق البصري.",
        "how_to_answer_ar": "ابدأ بأهمية القياس بـ Perfetto والـ Profiler، ثم اشرح بصمة التعقيد الخوارزمي (خيط الواجهة محتجز والـ RenderThread عاطل)، ثم بصمة اختناق الرسم (دوال measure وDrawFrame وOverdraw)، واختم بحلول كل حالة.",
        "talking_points_ar": "أداة Perfetto وSystem Trace، خمول RenderThread، استهلاك خيط الواجهة في منطق العمل، دوال View.measure وlayout، فحص GPU Overdraw، ونقل العمل لـ Dispatchers.Default.",
        "follow_ups_ar": "كيف تستخدم أداة Layout Inspector في أندرويد ستوديو لاكتشاف مرات إعادة التركيب (Recomposition Counts) في Compose؟",
        "self_check_ar": "هل ميزت بين بصمتي الخلل في خيوط المعالج، وذكرت أدوات الفحص، وشرحت العلاج المناسب لكل مسار؟",
        "references_ar": f"- [Android Developers: Overview of system tracing and Perfetto](https://developer.android.com/topic/performance/tracing) — الدليل الرسمي لتتبع مسار خيوط المعالج واكتشاف أسباب بطء التطبيق.\n- [Android Developers: Reduce overdraw](https://developer.android.com/topic/performance/rendering/overdraw) — إرشادات رسمية للحد من إعادة رسم البكسلات وتحسين أداء الرسوميات.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """نميز بينهما بتسجيل الأداء عبر Perfetto؛ فإذا كان الاختناق خوارزمياً يظهر خيط الواجهة محتجزاً في كود منطق العمل والفرز بينما يظل خيط RenderThread عاطلاً عن العمل. أما إذا كان الاختناق في الرسم، فيقضي خيط الواجهة وقته في دوال قياس الأبعاد View.measure مع استغراق RenderThread وقتاً طويلاً في DrawFrame وظهور مناطق حمراء في فحص Overdraw.""",
        "best_answer_ar": """التفريق بين اختناقات الرسم والتعقيد الخوارزمي يتطلب تشخيصاً علمياً عبر مسار النظام بـ Perfetto بدلاً من التخمين المجرد.
عندما يكون السبب خوارزمياً، يظهر خيط واجهة المستخدم الرئيسي في المخطط البياني محتجزاً بكتل زمنية طويلة تنفذ عمليات معالجة داخل كود التطبيق، مثل مقارنات DiffUtil أو فرز القوائم أو فك تشفير البيانات. والملمح الحاسم هنا هو أن خيط الرسم RenderThread ومعالج الرسوميات يظلان في حالة خمول تام بانتظار إفراج الخيط الرئيسي عن أوامر العرض. ونعالج هذا الخلل بنقل الحسابات إلى خيوط الخلفية عبر Dispatchers.Default وتحسين كفاءة البيانات.
أما عندما يكون السبب في منظومة الرسم، فيظهر العكس تماماً؛ حيث يقضي خيط الواجهة وقته داخل دوال النظام مثل View.measure وView.layout نتيجة تعقيد وتداخل طبقات الواجهة، بينما يسجل خيط RenderThread فترات عمل مفرطة في رسم الإطارات، وتكشف أداة فحص الشاشة عن إعادة رسم البكسلات عدة مرات فوق بعضها. ونعالج هذا المسار بتبسيط وتسطيح طبقات الواجهة واستخدام مفاتيح العناصر في Compose لمنع إعادة القياس غير المبررة.""",
        "deep_answer_ar": """من منظور فحص النظم الدقيق وهندسة المعالجات الرسومية في أندرويد، يمثل تجمد الشاشات على الأجهزة الاقتصادية تحدياً يتطلب فك الارتباط بين معالجة البيانات ودورة رسم الإطارات.
نبدأ التشخيص بتسجيل جلسة تتبع حية عبر Perfetto على عتاد منخفض المواصفات؛ حيث نراقب التزامن بين خيط واجهة المستخدم وخيط RenderThread. فإذا كانت العلة خوارزمية، نلاحظ احتجاز الخيط الرئيسي في دوال برمجية واضحة كالبحث الخطي أو تصفية القوائم؛ مما يؤخر استدعاء Choreographer doFrame متجاوزاً ميزانية الستة عشر مللي ثانية. والمؤشر القاطع على ذلك هو بقاء خيط RenderThread في حالة فراغ تام، محروماً من أي بيانات جديدة لعرضها.
وعلى النقيض من ذلك، يظهر اختناق الرسم البصري عندما يكون خيط الواجهة مستهلكاً بالكامل في هندسة الشاشة؛ ففي واجهات XML التقليدية، تتسبب الطبقات المتداخلة ذات الأبعاد النسبية في مضاعفة دورات القياس والحساب. وفي Jetpack Compose، يظهر الخلل في دورات إعادة التركيب المتكررة للواجهة بسبب دوال لامدا غير المستقرة. ويترافق ذلك مع ضغط هائل على معالج الرسوميات ينعكس في نداءات DrawFrame الطويلة وظهور مساحات حمراء واسعة في فحص GPU Overdraw نتيجة تكديس خلفيات رسومية غير مرئية للمستخدم.
ولذلك يعتمد العلاج على تصنيف البصمة؛ فننقل الخوارزميات الثقيلة فوراً إلى Dispatchers.Default مع تحويل هياكل البحث لـ O of one، بينما نعالج اختناقات الرسم بتسطيح الشاشات وحذف الخلفيات الزائدة وتصغير الصور مسبقاً لتطابق أبعاد العرض، مما يحقق سلاسة تامة وثباتاً بصرياً على كافة الفئات السعرية للهواتف."""
    }
}

# ==========================================
# DSA-15: Build a rate limiter or deduplication map for requests. What data structure fits?
# ==========================================
DATA["DSA-15"] = {
    "concept_en": """Designing client-side rate limiters and in-flight request deduplication systems requires choosing data structures that ensure thread-safety, bounded memory footprints, and low-latency execution:
- Sliding Window Log (Rate Limiting):
  - Architecture: A thread-safe map (`ConcurrentHashMap<String, ArrayDeque<Long>>`) mapping endpoint keys to queues of request epoch timestamps.
  - Algorithm: On an incoming request, purge timestamps older than `now - windowDuration` from the queue front. If remaining count is below the threshold, append `now` and approve; otherwise, throttle.
  - Complexity: Amortized $O(1)$ operations, exact boundary accuracy, with memory bounded by `maxRequestsPerWindow` timestamps per key.
- Token Bucket (Low-Footprint Rate Limiting):
  - Architecture: Tracks two primitive numeric variables per endpoint: `availableTokens: Double` and `lastRefillTimestamp: Long`.
  - Algorithm: On arrival, calculates tokens accumulated since last refill: `tokens += (now - lastRefill) * refillRate`. If `tokens >= 1.0`, decrement and allow; otherwise, reject.
  - Complexity: Strictly $O(1)$ constant time and $O(1)$ memory (only 16 bytes per endpoint), allowing burst capacity while smoothing traffic.
- In-Flight Request Deduplication (Coalescing):
  - Architecture: `ConcurrentHashMap<RequestKey, Deferred<Response>>`.
  - Algorithm: When a network request fires (such as repeated button taps or parallel screen initializations), inspect the map. If an active `Deferred` exists, await it directly without launching a second HTTP call.
  - Clean-up Invariant: A `finally` block or completion callback guarantees key removal upon request termination, preventing memory leaks and stale cached responses.""",
    "walkthrough_en": """Thread-safe Sliding Window Rate Limiter and Request Deduplicator in Kotlin:
```kotlin
import kotlinx.coroutines.*
import java.util.concurrent.ConcurrentHashMap

// 1. Thread-safe Sliding Window Rate Limiter
class SlidingWindowRateLimiter(
    private val maxRequests: Int,
    private val windowDurationMs: Long
) {
    private val requestLogs = ConcurrentHashMap<String, ArrayDeque<Long>>()

    @Synchronized
    fun shouldAllowRequest(endpointKey: String): Boolean {
        val now = System.currentTimeMillis()
        val queue = requestLogs.getOrPut(endpointKey) { ArrayDeque() }

        // Evict expired timestamps outside the active window
        while (queue.isNotEmpty() && (now - queue.first()) > windowDurationMs) {
            queue.removeFirst()
        }

        return if (queue.size < maxRequests) {
            queue.addLast(now)
            true // Request permitted
        } else {
            false // Throttled
        }
    }
}

// 2. Coroutine-based In-Flight Request Deduplicator
class RequestDeduplicator {
    private val inFlight = ConcurrentHashMap<String, Deferred<String>>()

    suspend fun executeDeduplicated(key: String, networkCall: suspend () -> String): String {
        val deferred = inFlight.compute(key) { _, existing ->
            existing ?: CoroutineScope(Dispatchers.IO).async {
                try {
                    networkCall()
                } finally {
                    inFlight.remove(key) // Guaranteed memory cleanup
                }
            }
        }!!
        return deferred.await()
    }
}
```""",
    "short_en": """Implement a rate limiter using a sliding window log via ConcurrentHashMap and ArrayDeque for precise timestamp eviction, or a Token Bucket for minimal O(1) memory overhead. Deduplicate in-flight requests using a ConcurrentHashMap of Coroutine Deferred instances, allowing concurrent calls to share a single network invocation with guaranteed cleanup in a finally block.""",
    "structured_en": """Designing rate limiting and request deduplication on Android requires matching data structures to specific concurrency and memory constraints.
For rate limiting with strict boundary precision, the sliding window log is an excellent fit. It utilizes a ConcurrentHashMap mapping endpoint keys to an ArrayDeque of timestamps. When a request arrives, timestamps older than the active window are evicted from the queue. If the remaining count is within limits, the request proceeds, delivering amortized O(1) performance.
If memory efficiency is paramount, the Token Bucket algorithm stores just two numbers per endpoint: current tokens and last refill timestamp. It runs in strictly O(1) constant time and negligible memory, smoothly accommodating bursts.
For request deduplication, we use a ConcurrentHashMap mapping request keys to active Coroutine Deferred objects. When duplicate requests fire simultaneously, subsequent callers attach to the in-flight Deferred rather than spawning duplicate network requests. An explicit finally block guarantees map eviction upon completion, preventing memory leaks.""",
    "deep_senior_en": """From a high-concurrency client systems perspective, request governance mechanisms protect both mobile battery life and backend microservices from accidental Denial of Service conditions.
When architecting a client-side rate limiter, the sliding window log offers superior accuracy compared to fixed-window counters, which suffer from boundary traffic spikes where double the limit executes across the reset boundary. By maintaining a timestamp queue inside an ArrayDeque, we achieve amortized O of one eviction. However, if thousands of unique parameterized query keys are generated, the map can grow unbounded. We resolve this by constraining the map with an LRU eviction policy or adopting the Token Bucket algorithm. Token Bucket calculates available capacity lazily through timestamp deltas, requiring only two numeric primitives per key and zero object allocations during active traffic.
Request deduplication requires atomic state coordination. A frequent bug in Android networking occurs when a user repeatedly taps a purchase or refresh button, or when multiple ViewModels request the same user profile simultaneously. If unmanaged, the app initiates redundant HTTP requests, wasting cellular data and risking duplicate state mutations.
By maintaining a ConcurrentHashMap of Coroutine Deferred objects, we coalesce duplicate requests atomically. The first caller initiates the network call and registers the Deferred. Concurrent callers atomically acquire the existing Deferred and await the identical response. To ensure fault tolerance and prevent memory leaks, we wrap the execution in a try-finally construct that removes the key from the map upon completion or cancellation. This architecture guarantees single-flight network efficiency with ironclad thread safety.""",
    "meta_ar": {
        "id": "DSA-15",
        "questionAr": "كيف تصمم محدد معدل الطلبات (Rate Limiter) وخريطة منع تكرار الطلبات (Request Deduplication)؟ وما هو هيكل البيانات الأنسب؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "تصميم خوارزميات الـ Rate Limiting، خوارزمية Sliding Window Log مع ArrayDeque، خوارزمية Token Bucket الموفرة للذاكرة، دمج الطلبات المتزامنة (In-Flight Deduplication) عبر Coroutines Deferred، وتفادي تسريب الذاكرة.",
        "concept_ar": "يتطلب تصميم محدد معدل الطلبات (Rate Limiter) ومنع تكرار الطلبات المتزامنة (Deduplication) اختيار هياكل بيانات تضمن الأمان التام بين الخيوط (Thread-Safety) واستهلاكاً ثابتاً للذاكرة: لتحديد معدل الطلبات بدقة زمنية، نستخدم خوارزمية السجل المنزلق (Sliding Window Log) المكونة من `ConcurrentHashMap` يربط المفتاح بطابور زمني `ArrayDeque<Long>`؛ حيث تُطرد الطوابع الزمنية القديمة الخارجة عن النافذة، وتُقبل الطلبات إذا كان حجم الطابور أقل من السقف المحدد بتعقيد $O(1)$ المستهلك. ولتوفير الذاكرة بالكامل، نستخدم خوارزمية وعاء الرموز (Token Bucket) التي تحتفظ برقمين فقط لكل نقطة: عدد الرموز المتاحة ووقت التعبئة الأخير؛ مما يوفر تعقيداً مكانياً وزمنياً ثابتاً $O(1)$ مع مرونة في استقبال دفعات الطلبات. أما لمنع تكرار الطلبات الشبكية المتزامنة (In-Flight Deduplication) عند نقر المستخدم المتكرر على زر، فنستخدم `ConcurrentHashMap<String, Deferred<Response>>`؛ حيث ينفذ الطلب الأول الاتصال بالشبكة، وتنتظر باقي النداءات نفس كائن `Deferred` دون فتح اتصالات جديدة، مع مسح المفتاح في كتلة `finally` لضمان عدم تسريب الذاكرة.",
        "walkthrough_ar": """تصميم محدد معدل بالنافذة المنزلقة ومدمج الطلبات في كوتلن:
```kotlin
import kotlinx.coroutines.*
import java.util.concurrent.ConcurrentHashMap

// 1. محدد معدل الطلبات بالنافذة المنزلقة (Sliding Window)
class RateLimiter(private val maxLimit: Int, private val windowMs: Long) {
    private val logs = ConcurrentHashMap<String, ArrayDeque<Long>>()

    @Synchronized
    fun allow(key: String): Boolean {
        val now = System.currentTimeMillis()
        val queue = logs.getOrPut(key) { ArrayDeque() }

        // التخلص من الطوابع الزمنية المنتهية
        while (queue.isNotEmpty() && now - queue.first() > windowMs) {
            queue.removeFirst()
        }

        return if (queue.size < maxLimit) {
            queue.addLast(now)
            true // السماح بالطلب
        } else {
            false // حجب الطلب (Throttled)
        }
    }
}

// 2. منع تكرار الطلبات الشبكية المتزامنة عبر Coroutines Deferred
class RequestDeduplicator {
    private val activeCalls = ConcurrentHashMap<String, Deferred<String>>()

    suspend fun execute(key: String, call: suspend () -> String): String {
        val deferred = activeCalls.compute(key) { _, current ->
            current ?: CoroutineScope(Dispatchers.IO).async {
                try {
                    call()
                } finally {
                    activeCalls.remove(key) // تنظيف حتمي للذاكرة
                }
            }
        }!!
        return deferred.await()
    }
}
```""",
        "why_it_matters_ar": "غياب محدد الطلبات يستنزف باقة المستخدم وبطارية الهاتف، وتكرار إرسال الطلبات يسبب أخطاء في المدفوعات والعمليات الحساسة.",
        "worked_example_ar": "عند نقر المستخدم السريع 5 مرات على زر الدفع، قام Deduplicator بدمجها في طلب شبكي واحد عبر Deferred، مما منع سحب المبلغ مكرراً.",
        "trade_offs_ar": "خوارزمية Sliding Window دقيقة للغاية في حماية الحدود الزمنية ولكنها تستهلك ذاكرة لطوابع الوقت؛ بينما Token Bucket فائقة التوفير ولكنها تسمح بدفعات مفاجئة.",
        "failure_modes_ar": "أخطر الأخطاء هو نسيان مسح مفتاح الطلب من الخريطة في كتلة finally مما يسبب تسريب الذاكرة، أو استخدام HashMap عادية غير متزامنة مما يسبب تعليق الخيوط.",
        "production_perspective_ar": "في كود الإنتاج، تُربط خريطة الطلبات بـ LruCache لحذف المفاتيح القديمة غير المستخدمة تلقائياً وضمان عدم تضخم الذاكرة مع ملايين الاستدعاءات.",
        "how_to_answer_ar": "ابدأ بتقديم Sliding Window Log مع ArrayDeque لحساب الدقة، ثم اطرح Token Bucket كبديل فائق التوفير، واشرح دمج الطلبات المتزامنة عبر ConcurrentHashMap وDeferred مع مسح finally.",
        "talking_points_ar": "خوارزمية Sliding Window Log، طابور ArrayDeque، خوارزمية Token Bucket الموفرة، دمج الطلبات In-Flight Coalescing، كائنات Coroutine Deferred، وتنظيف الذاكرة في finally.",
        "follow_ups_ar": "كيف تتعامل مع إلغاء Coroutine (Job Cancellation) لضمان عدم بقاء مفتاح الطلب معلقاً؟ وما الفارق بين Leaky Bucket وToken Bucket؟",
        "self_check_ar": "هل شرحت هيكل Sliding Window وToken Bucket، وفصلت آلية دمج الطلبات بـ Deferred ومسح الذاكرة في finally؟",
        "references_ar": f"- [Kotlin Coroutines: Deferred documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-deferred/) — التوثيق الرسمي لكائنات العمليات غير المتزامنة المؤجلة في كوتلن.\n- [Martin Fowler: Circuit Breaker and Rate Limiting patterns](https://martinfowler.com/bliki/CircuitBreaker.html) — المرجع الكلاسيكي لأنماط حماية استقرار النظم والحد من الطلبات.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """نصمم محدد الطلبات باستخدام ConcurrentHashMap مع طابور ArrayDeque لخوارزمية Sliding Window لطرد الطوابع الزمنية القديمة بدقة، أو بخوارزمية Token Bucket لتوفير الذاكرة برقمين فقط لكل نقطة. ولمنع تكرار الطلبات الشبكية، نستخدم ConcurrentHashMap مع كائنات Coroutine Deferred لدمج النداءات المتزامنة في اتصال واحد مع تنظيف المفتاح في finally.""",
        "best_answer_ar": """تصميم محدد معدل الطلبات ومنع التكرار في أندرويد يتطلب اختيار هياكل بيانات تضمن الأمان المتزامن وانضباط الذاكرة.
بالنسبة لتحديد معدل الطلبات بدقة زمنية متناهية، نعتمد على خوارزمية السجل المنزلق Sliding Window Log؛ حيث نستخدم خريطة متزامنة ConcurrentHashMap تربط مسار الطلب بطابور ArrayDeque يحفظ الطوابع الزمنية. وعند وصول أي طلب، نطرد الطوابع الأقدم من مدة النافذة، ونسمح بالطلب إذا كان الحجم المتبقي دون الحد الأقصى في زمن حتمي سريع.
أما إذا كانت الذاكرة مقيدة بشدة، فنعتمد على خوارزمية Token Bucket التي تقتصر على متغيرين رقميين فقط لحساب الرموز ووقت التعبئة الأخير؛ مما يوفر استهلاكاً ثابتاً للذاكرة مع استيعاب الدفعات اللحظية.
وفيما يخص منع تكرار الطلبات المتزامنة عند النقر السريع، نستخدم خريطة من كائنات Coroutine Deferred؛ فإذا كان هناك اتصال جارٍ لنفس العملية، تشترك كافة النداءات في انتظار نفس الاستجابة دون فتح اتصالات مكررة، مع إزالة المفتاح حتمياً في كتلة finally لمنع أي تسريب للذاكرة.""",
        "deep_answer_ar": """من منظور هندسة الأنظمة عالية التزامن في أندرويد، تلعب آليات حوكمة الطلبات دوراً حاسماً في حماية بطارية الهاتف والواجهات الخلفية من الضغط العشوائي.
تتفوق خوارزمية السجل المنزلق على العدادات الثابتة التي تعاني من ثغرة مضاعفة الطلبات عند تقاطع النوافذ الزمنية؛ فباستخدام ArrayDeque داخل ConcurrentHashMap، نحصل على طرد فوري للطوابع القديمة بتعقيد O of one حتمي. ومع ذلك، نراعي حماية الذاكرة من التضخم عند تعدد المفاتيح بربط الخريطة بحد أقصى أو اللجوء لخوارزمية Token Bucket التي تحسب الاستحقاق كمعادلة زمنية مجردة برقمين فقط دون حجز أي كائنات إضافية على الـ Heap.
وعلى صعيد دمج الطلبات المتزامنة، نواجه كثيراً مشكلة النقر المتكرر على أزرار الدفع أو تحديث الشاشات؛ مما يهدد بفتح عدة اتصالات شبكية لنفس الغرض. والمعالجة المعمارية تكمن في دمج الطلبات أثناء الطيران عبر خريطة كائنات Deferred غير المتزامنة.
يبدأ الطلب الأول عملية الشبكة ويسجل الرابط، بينما ترتبط النداءات اللاحقة بنفس الكائن وتنتظر نتيجته ذرياً. ونلزم الكود بهيكل try-finally محكم يضمن حذف المفتاح فور اكتمال المهمة أو إلغائها، مما يوفر حماية مطلقة ضد تكرار البيانات ويمنع تسريب الذاكرة في كافة الحالات الاستثنائية، مع التعامل الحصيف مع إلغاء مهام الكوروتين حتى لا تظل أي مفاتيح عالقة في الخريطة دون معالجة حتمية."""
    }
}

# ==========================================
# DSA-16: How do you optimize an algorithm while keeping code maintainable and correct?
# ==========================================
DATA["DSA-16"] = {
    "concept_en": """Disciplined algorithmic optimization balances runtime performance gains against architectural readability, testability, and maintainability:
- Guiding Axiom:
  - \\"Premature optimization is the root of all evil\\" (Donald Knuth).
  - Never optimize based on intuition; always optimize based on empirical profiling data.
- Systematic 6-Step Engineering Framework:
  1. Empirical Measurement & Profiling:
     - Profile code under realistic workloads using Android Studio Profiler, Perfetto, or Jetpack Benchmark. Identify the exact line or method dominating the critical execution path.
  2. Establish Comprehensive Baseline Test Suite:
     - Before writing a single line of optimized code, construct an exhaustive unit test suite.
     - Cover nominal inputs, extreme edge cases (empty lists, duplicates, maximum boundary values, nulls), and property-based randomized inputs.
  3. Decouple Behind Clean Abstractions (Strategy Pattern):
     - Encapsulate the algorithmic implementation behind an interface or clean domain UseCase (e.g., `interface SearchStrategy`).
     - Allows refactoring or rolling back implementations without altering client UI or repository code.
  4. Idiomatic High-Level Optimization First:
     - Prioritize fundamental algorithmic complexity reduction (e.g., replacing $O(n^2)$ with $O(n)$ via `HashSet`, or using `asSequence()`) before resorting to low-level micro-optimizations like raw bit manipulation or primitive array arrays.
  5. Document Non-Obvious Complexity:
     - Add explicit KDoc explaining *why* an intricate structure was chosen, citing empirical benchmark metrics and link to the corresponding performance issue.
  6. Verify Correctness and Performance Parity:
     - Re-run the comprehensive test suite to confirm zero regressions.
     - Re-benchmark against the recorded baseline to prove measurable improvements on physical Android hardware.""",
    "walkthrough_en": """Refactoring an algorithm safely behind a test-driven domain abstraction:
```kotlin
// Step 1: Encapsulate algorithm behind a clean domain interface
interface RouteOptimizer {
    fun calculateOptimalStops(locations: List<Location>): List<Location>
}

// Step 2: Implement optimized version with documented rationale
class FastSpatialRouteOptimizer : RouteOptimizer {
    override fun calculateOptimalStops(locations: List<Location>): List<Location> {
        if (locations.size <= 2) return locations

        // Optimized from O(n^2) brute-force to O(n log n) using Spatial Indexing
        // Benchmark proof: Reduced execution from 140ms to 4ms for 5,000 waypoints
        return locations
            .asSequence()
            .sortedBy { it.geohash }
            .distinctBy { it.gridCellId }
            .toList()
    }
}

// Step 3: Comprehensive verification test asserting behavioral correctness
class RouteOptimizerTest {
    private val optimizer: RouteOptimizer = FastSpatialRouteOptimizer()

    @Test
    fun `assert nominal and boundary cases behave correctly`() {
        val emptyResult = optimizer.calculateOptimalStops(emptyList())
        assertEquals(0, emptyResult.size)

        val duplicates = listOf(Location(1.0, 1.0), Location(1.0, 1.0))
        val deduplicated = optimizer.calculateOptimalStops(duplicates)
        assertEquals(1, deduplicated.size)
    }
}
```""",
    "short_en": """Optimize algorithms safely by first measuring with profiling tools like Perfetto, building an exhaustive test suite before refactoring, and hiding the algorithm behind a clean interface. Prioritize reducing Big O complexity over obscure micro-optimizations, document the rationale and benchmark results in KDoc, and re-benchmark on physical devices to prove performance gains.""",
    "structured_en": """Optimizing an algorithm without sacrificing code maintainability requires a structured, measurement-driven engineering methodology.
The process begins with empirical profiling using Android Studio CPU Profiler or Jetpack Benchmark. We never optimize based on intuition; we optimize only when profilers prove that a specific algorithm is the critical bottleneck.
Before modifying any implementation, we construct an exhaustive test suite covering nominal behavior and edge cases like empty collections, single elements, and boundary limits. This establishes a safety net to guarantee behavioral correctness.
Next, we encapsulate the algorithm behind a domain interface using the Strategy pattern. This isolates callers from implementation changes. We focus on high-level Big O improvements first, such as switching from quadratic to linear time using HashSets, rather than obscure micro-optimizations.
Finally, we document the rationale and benchmark metrics clearly in KDoc and re-benchmark on physical Android devices to confirm measurable gains without regressions.""",
    "deep_senior_en": """From an engineering leadership and software craftsmanship perspective, optimizing an algorithm is an exercise in risk management and long-term code stewardship.
The greatest danger of performance optimization is premature complexity. Code that is clever, dense, and full of bitwise tricks is notoriously difficult to maintain, prone to subtle edge-case bugs, and resistant to team collaboration. Senior engineers adhere to Donald Knuth\\'s maxim by establishing a strict rule: optimization begins only after profiling proves a measurable defect under realistic production workloads using tools like Perfetto or Macrobenchmark.
Once a bottleneck is identified, the first line of defense is behavioral regression prevention. We construct an unyielding test suite that exercises boundary conditions: zero-length inputs, maximum integer limits, duplicate keys, and degenerate arrangements. If an optimized algorithm fails on a single edge case, its speed is irrelevant.
To preserve clean architecture, we isolate the algorithm behind a dedicated domain abstraction or Strategy interface. The UI and repository layers remain blissfully ignorant of whether the calculation uses a naive search or an advanced binary tree.
We then focus on algorithmic leverage rather than hardware hacks. Moving an algorithm from O of n squared to O of n via a hash map or Sequence yields orders-of-magnitude improvements that dwarf micro-optimizations. If specialized structures like BitSet or custom array pools are truly necessary, we mandate thorough KDoc explaining the mechanical rationale, complete with links to the corresponding benchmark commit. Re-benchmarking on physical budget hardware ensures we deliver genuine user value while leaving a clean, maintainable codebase.""",
    "meta_ar": {
        "id": "DSA-16",
        "questionAr": "كيف تحسن أداء خوارزمية مع الحفاظ على قابلية قراءة الكود وصيانته وخلوه من الأخطاء؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "منهجية التحسين المنضبط (Measurement-driven Optimization)، تجنب التحسين المبكر (Premature Optimization)، بناء شبكة اختبارات شاملة أولاً، عزل الخوارزمية خلف واجهات نظيفة (Strategy Pattern)، وتوثيق المقاييس.",
        "concept_ar": "يتطلب تحسين أداء الخوارزميات دون التضحية بقابلية صيانة الكود اتباع منهجية هندسية منضبطة تبدأ بالقياس وتنتهي بالتحقق البرمجي: تنطلق المنهجية من مقولة دونالد كنوث الشهيرة بأن التحسين المبكر هو أصل كل الشرور؛ فلا يجوز التعديل بناءً على التخمين، بل بالاعتماد على أدوات قياس حقيقية مثل Android Studio Profiler وPerfetto لإثبات وجود اختناق في المسار الحرج. وقبل كتابة أي كود محسن، يُبنى جناح اختبارات شامل يغطي الحالات العادية والحدود الحرجة (مثل القوائم الفارغة والتكرار وحدود الأرقام) كصمام أمان لا يقبل التنازل. بعد ذلك، تُعزل الخوارزمية خلف واجهة برمجية مجردة (Interface / Strategy Pattern) لعزل الشاشات عن تفاصيل التنفيذ. ونبدأ دائماً بتحسين رتبة الـ Big O (كنقل التعقيد من $O(n^2)$ إلى $O(n)$ عبر جداول التجزئة) قبل اللجوء للحيل البرمجية المعقدة، مع توثيق الأسباب الرياضية وأرقام المقاييس في توثيق KDoc، وإعادة تشغيل الاختبارات والمقاييس على أجهزة حقيقية لضمان سلامة الكود وسرعته.",
        "walkthrough_ar": """نمط التصميم الآمن لعزل الخوارزمية واختبارها قبل وبعد التحسين:
```kotlin
// 1. عزل الخوارزمية خلف واجهة معمارية نظيفة (Strategy Pattern)
interface ProductFilterStrategy {
    fun filterProducts(products: List<Product>): List<Product>
}

// 2. تطبيق الخوارزمية المحسنة مع توثيق أسباب الاختيار والتحسين
class FastCategoryFilter : ProductFilterStrategy {
    override fun filterProducts(products: List<Product>): List<Product> {
        // تحسين من O(n^2) إلى O(n) باستخدام HashSet
        // نتيجة القياس: انخفض وقت المعالجة من 80ms إلى 2ms لـ 10,000 عنصر
        val activeIds = HashSet<String>()
        return products.filter { activeIds.add(it.id) }
    }
}

// 3. شبكة اختبارات شاملة تضمن مطابقة السلوك وصحة الحالات الحافة
class FilterTest {
    private val filter: ProductFilterStrategy = FastCategoryFilter()

    @Test
    fun `test empty and boundary cases`() {
        assertTrue(filter.filterProducts(emptyList()).isEmpty())
    }
}
```""",
        "why_it_matters_ar": "التحسين العشوائي المبكر يعقد الكود ويملؤه بالثغرات الخفية ويصعب صيانته، والتحسين المنهجي المنضبط يحقق أقصى سرعة مع الحفاظ على نقاء المعمارية.",
        "worked_example_ar": "عزلنا خوارزمية حساب المسافات خلف واجهة DistanceCalculator؛ وكتبنا 15 اختبار وحدة، ثم حولنا الكود من بحث تربيعي إلى فرز لوغاريتمي فائق السرعة دون كسر سطر واحد في الشاشات.",
        "trade_offs_ar": "الكود فائق البساطة قد يكون بطيئاً في الأحجام الكبيرة؛ بينما الكود فائق التعقيد بالعمليات الثنائية صعب الصيانة؛ والتوازن يكمن في خفض Big O مع الحفاظ على كود كوتلن القياسي المقروء.",
        "failure_modes_ar": "أخطر الأخطاء هو الشروع في التحسين دون كتابة اختبارات مسبقة مما يتسبب في تسريب أخطاء كارثية للإنتاج، أو تحسين دوال لا تمثل اختناقاً حقيقياً في أداء التطبيق.",
        "production_perspective_ar": "في الفرق الهندسية الكبرى، يُرفض أي PR يزعم تحسين الأداء إذا لم يتضمن نتائج قياس مقارنة موثقة بأداة Jetpack Benchmark قبل وبعد التعديل.",
        "how_to_answer_ar": "ابدأ برفض التحسين المبكر وضرورة القياس بـ Profiler، ثم اشرح الخطوات الست: كتابة الاختبارات أولاً، عزل الخوارزمية خلف Interface، خفض Big O أولاً، توثيق المقاييس، وإعادة التحقق.",
        "talking_points_ar": "التحسين المبكر Premature Optimization، القياس بأدوات Profiler وPerfetto، كتابة الاختبارات الشاملة أولاً، نمط Strategy وعزل الواجهات، خفض Big O، وتوثيق KDoc بالأرقام.",
        "follow_ups_ar": "كيف تستخدم مكتبة Jetpack Macrobenchmark لكتابة اختبارات أداء مؤتمتة في خطوط الـ CI؟ ومتى يكون التراجع عن التحسين هو القرار الهندسي الصائب؟",
        "self_check_ar": "هل أكدت على القياس قبل التحسين، وكتابة الاختبارات كخطوة أولى، وعزل الكود خلف Interface، وتوثيق أرقام الأداء؟",
        "references_ar": f"- [Donald Knuth: Structured Programming with go to Statements](https://doi.org/10.1145/356635.356640) — الورقة البحثية التاريخية التي وردت فيها عبارة التحسين المبكر أصل الشرور.\\n- [Android Developers: Benchmark your app with Jetpack Benchmark](https://developer.android.com/topic/performance/benchmarking/benchmarking-overview) — الدليل الرسمي لقياس أداء الكود البرمجي بدقة متناهية في أندرويد.\\n\\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """نحسن الخوارزميات بأمان بالقياس أولاً بأدوات Profiler لإثبات وجود الاختناق، ثم كتابة شبكة اختبارات شاملة لكافة الحالات الحافة قبل كتابة أي كود، وعزل الخوارزمية خلف واجهة برمجية نظيفة. ونبدأ دائماً بخفض تعقيد الـ Big O قبل الحيل المعقدة، مع توثيق نتائج القياس في KDoc وإعادة التحقق على هواتف حقيقية.""",
        "best_answer_ar": """تحسين أداء الخوارزميات دون المساس بسلامة الكود وقابليته للصيانة يتطلب اتباع منهجية هندسية منضبطة تقودها البيانات لا التخمين.
تبدأ المنهجية بالقياس العملي باستخدام أدوات مثل Android Studio CPU Profiler أو Perfetto لإثبات أن هناك دالة معينة تمثل عنق زجاجة حقيقي في المسار الحرج؛ امتثالاً لمبدأ تجنب التحسين المبكر غير المبرر.
وقبل تعديل سطر واحد، نبني شبكة اختبارات وحدة شاملة تغطي السلوك الطبيعي وكافة الحالات الاستثنائية والحدود القصوى والقوائم الفارغة، لتشكل صمام أمان يمنع أي تراجع سلوكي.
بعد ذلك، نعزل الخوارزمية خلف واجهة برمجية مجردة بنمط Strategy؛ مما يفصل كود الواجهة والـ ViewModel عن تفاصيل التنفيذ الداخلي. ونركز أولاً على تقليص تعقيد Big O الجذري كنقل الكود من التربيعي إلى الخطي عبر جداول التجزئة بدلاً من الانجرار للحيل المعقدة غير المقروءة.
وأخيراً، نوثق الأسباب والأرقام بدقة في KDoc، ونعيد قياس الأداء على هواتف اقتصادية للتأكد من تحقيق مكاسب حقيقية وملموسة للمستخدم.""",
        "deep_answer_ar": """من منظور القيادة الهندسية والانضباط البرمجي، يمثل تحسين أداء الخوارزميات موازنة دقيقة بين جودة التجربة وإدارة المخاطر التقنية طويلة الأجل.
الخطر الأكبر في تحسين الأداء هو التعقيد المبكر؛ فالكود المليء بالحيل الملتوية والعمليات الثنائية المعقدة يصعب اختباره وصيانته ويولد ثغرات خفية تنفجر في الإنتاج. ولذلك يفرض مهندسو النظم قاعدة صارمة: لا تحسين دون برهان قياسي من أدوات التتبع كـ Perfetto أو Macrobenchmark يثبت تعطيل الخوارزمية للمسار الحرج تحت ضغط البيانات الحقيقية.
وعند إثبات الحاجة، تكون الخطوة الدفاعية الأولى هي بناء جناح اختبارات حاسم يغطي الحالات القصوى والمدخلات الصفرية والتكرار العشوائي؛ فالخوارزمية السريعة التي تخطئ في حالة حافة واحدة هي خوارزمية فاشلة هندسياً.
ثم نطبق مبدأ العزل المعماري بتغليف المنطق داخل واجهة برمجية نظيفة؛ مما يتيح تغيير الخوارزمية أو التراجع عنها بنقرة زر دون المساس بباقي طبقات التطبيق.
ونبدأ دوماً بالتحسين الخوارزمي الأعلى أثراً؛ فاستبدال خوارزمية تربيعية بأخرى خطية يوفر قفزات هائلة في السرعة تتضاءل أمامها أي تحسينات سطحية. وإذا اضطررنا لاستخدام هياكل بيانات مخصصة أو مصفوفات بتات، نلزم المطور بكتابة توثيق KDoc وافٍ يشرح المبرر الهندسي ويوثق أرقام قياس الأداء بدقة. وأخيراً، نتحقق من زوال الاختناق بإعادة الاختبار على أجهزة حقيقية منخفضة المواصفات، محققين التوازن الأمثل بين السرعة الفائقة ونقاء المعمارية."""
    }
}

# ==========================================
# Validation & Runner logic
# ==========================================
def validate_words():
    print("Checking word counts and spoken style for DSA-09 to DSA-16...")
    for qid, d in sorted(DATA.items()):
        # Short answer (35 - 110)
        c_short = len(d["short_en"].split())
        assert 35 <= c_short <= 110, f"{qid}: short_en word count {c_short} out of range (35-110)"

        # Structured answer (100 - 280)
        c_struct = len(d["structured_en"].split())
        assert 100 <= c_struct <= 280, f"{qid}: structured_en word count {c_struct} out of range (100-280)"

        # Deep senior answer (200 - 650)
        c_deep = len(d["deep_senior_en"].split())
        assert 200 <= c_deep <= 650, f"{qid}: deep_senior_en word count {c_deep} out of range (200-650)"

        meta = d["meta_ar"]
        # Quick answer AR (35 - 110)
        c_qar = len(meta["quick_answer_ar"].split())
        assert 35 <= c_qar <= 110, f"{qid}: quick_answer_ar word count {c_qar} out of range (35-110)"

        # Best answer AR (90 - 280)
        c_bar = len(meta["best_answer_ar"].split())
        assert 90 <= c_bar <= 280, f"{qid}: best_answer_ar word count {c_bar} out of range (90-280)"

        # Deep answer AR (180 - 650)
        c_dar = len(meta["deep_answer_ar"].split())
        assert 180 <= c_dar <= 650, f"{qid}: deep_answer_ar word count {c_dar} out of range (180-650)"

        # Check spoken style (no bullets, no numbered lists)
        for field_name, text in [
            ("structured_en", d["structured_en"]),
            ("deep_senior_en", d["deep_senior_en"]),
            ("best_answer_ar", meta["best_answer_ar"]),
            ("deep_answer_ar", meta["deep_answer_ar"]),
        ]:
            assert not any(line.strip().startswith(("-", "*", "•")) for line in text.splitlines()), f"{qid}: {field_name} contains bullets"
            assert not any(line.strip() and line.strip()[0].isdigit() and line.strip()[1:3] in (". ", ") ") for line in text.splitlines()), f"{qid}: {field_name} contains numbered list"

        assert "على الجانب الآخر، فيما يخص" not in meta["best_answer_ar"], f"{qid}: best_answer_ar contains cliché"
        assert "على الجانب الآخر، فيما يخص" not in meta["deep_answer_ar"], f"{qid}: deep_answer_ar contains cliché"

    print("Pre-validation word count checks passed! Updating canonical questions...")

def apply_elevations():
    validate_words()

    topic_meta = {}
    for qid, d in sorted(DATA.items()):
        ee.update_canonical_question(
            qid=qid,
            concept_en=d["concept_en"],
            walkthrough_en=d["walkthrough_en"],
            structured_en=d["structured_en"],
            deep_senior_en=d["deep_senior_en"],
            short_en=d["short_en"],
        )
        topic_meta[qid] = d["meta_ar"]

    ee.save_topic_metadata("dsa_09_16", topic_meta)
    ee.merge_all_metadata()

    for qid in sorted(DATA.keys()):
        errs = ee.validate_question(qid)
        if errs:
            print(f"Errors in {qid}:")
            for er in errs:
                print(f"  ❌ {er}")
            sys.exit(1)

    print(f"\\nAll {len(DATA)} DSA questions (DSA-09 to DSA-16) successfully elevated and passed validation!\\n")

if __name__ == "__main__":
    apply_elevations()
