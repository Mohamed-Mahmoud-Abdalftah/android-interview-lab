#!/usr/bin/env python3
"""
Elevation script for DSA questions: DSA-01 to DSA-08.
Topic: Data Structures, Algorithms & Big O (DSA)
Phase 5, Batch 1
"""

import os
import sys

sys.path.insert(0, os.path.abspath("scripts/elevations"))
import elevation_engine as ee

TOPIC_AR = "هياكل البيانات والخوارزميات والـ Big O"
REVIEWED_DATE_AR = "تمت المراجعة والتحقق في 17 أكتوبر 2026"

DATA = {}

# ==========================================
# DSA-01: What is time complexity versus space complexity?
# ==========================================
DATA["DSA-01"] = {
    "concept_en": """Time and space complexity quantify the asymptotic consumption of computational resources as input size scales toward infinity:
- Time Complexity:
  - Mathematical formulation of how execution duration or operation counts increase relative to input size $n$.
  - Android Runtime Implications: The Android Main (UI) thread operates on a strict frame budget: 16.6 milliseconds per frame for 60Hz displays, or 8.3 milliseconds for 120Hz displays. Long-running computations on the Main thread cause dropped frames (Jank), UI stutter, and trigger Application Not Responding (ANR) watchdog dialogs after 5 seconds.
- Space Complexity:
  - Mathematical formulation of auxiliary memory allocated on the heap and stack (such as recursive call frames) as input size $n$ scales.
  - Android Runtime Implications: Android devices enforce strict Dalvik/ART heap limits per process (e.g., 192MB to 512MB). Excessive heap allocations create memory churn, triggering frequent concurrent and stop-the-world Garbage Collection (GC) pauses that freeze UI animations and risk OutOfMemoryError (OOM) aborts.
- The Space-Time Trade-off in Mobile Engineering:
  - Developers frequently trade memory footprint to optimize CPU execution cycles, such as indexing collections in a `HashMap` for $O(1)$ retrieval rather than an $O(n)$ sequential search, accepting the node allocation overhead to preserve UI rendering smoothness.""",
    "walkthrough_en": """Benchmarking time vs space trade-offs in Kotlin list transformations:
```kotlin
// Scenario: Finding two elements that sum to a target price
data class Item(val id: String, val price: Int)

// Approach 1: Zero auxiliary space, but slow quadratic time O(n^2)
// Risk: Freezes UI thread if list has 5,000 items
fun hasPairWithSumBruteForce(items: List<Item>, target: Int): Boolean {
    for (i in items.indices) {
        for (j in i + 1 until items.size) {
            if (items[i].price + items[j].price == target) return true
        }
    }
    return false
}

// Approach 2: Linear time O(n), but allocates auxiliary HashSet memory O(n)
// Best Practice: Sacrifices memory to guarantee sub-millisecond execution
fun hasPairWithSumOptimized(items: List<Item>, target: Int): Boolean {
    val seenPrices = HashSet<Int>(items.size)
    for (item in items) {
        val complement = target - item.price
        if (seenPrices.contains(complement)) return true
        seenPrices.add(item.price)
    }
    return false
}
```""",
    "short_en": """Time complexity measures how execution steps grow as input size scales, dictating UI thread responsiveness and frame drops. Space complexity measures auxiliary memory growth on the heap and recursion stack, dictating garbage collection pauses and OOM risks. Senior mobile engineers continually balance the space-time trade-off to maintain smooth 60fps or 120fps rendering without exhausting Android heap quotas.""",
    "structured_en": """Time complexity and space complexity represent the two fundamental constraints governing mobile software performance.
Time complexity quantifies how algorithmic execution time grows as input size expands. On Android, time complexity directly impacts the main thread. Because modern displays require rendering a frame every 8 to 16 milliseconds, any algorithmic task with high time complexity running on the main thread drops frames and risks triggering an Application Not Responding error.
Space complexity measures auxiliary memory consumed on the heap and call stack during execution. In mobile devices with constrained heap budgets, high space complexity induces aggressive memory churn. Rapid allocation and deallocation of temporary objects forces the Android Runtime garbage collector to run repeatedly, causing micro-stutter during scrolling and risking OutOfMemory crashes.
Senior Android engineers manage this dynamic through conscious space-time trade-offs, often trading modest heap allocations for linear or constant-time algorithms to safeguard frame rates while remaining well within device memory budgets.""",
    "deep_senior_en": """From an Android runtime internals and systems architecture perspective, time and space complexity govern device hardware sustainability and user perceived latency.
When evaluating time complexity, mobile engineers must view Big O through the lens of the Android main thread and Choreographer frame callbacks. A naive quadratic algorithm executing inside a Compose layout pass or RecyclerView DiffUtil callback might run unnoticed on a high-end development device with a small mock dataset. In production, when a user catalog scales to thousands of entries, that same quadratic complexity starves the CPU, blowing past the eight-millisecond frame budget and inducing severe visual Jank. If blocking continues for five seconds, the system watchdog terminates the process with an ANR.
Conversely, space complexity directly dictates Dalvik and ART garbage collection ergonomics. Many developers mistakenly believe that modern multi-gigabyte device RAM makes space complexity irrelevant. However, the ART heap allocated per application is strictly bounded by device manufacturer configurations. Furthermore, high space complexity frequently creates generational memory churn. Allocating thousands of short-lived iterator objects or defensive collections in a loop fills young-generation heap regions rapidly, triggering Concurrent Mark-Sweep or Generative GC pauses that freeze the main thread.
Therefore, mobile architecture demands holistic complexity analysis. We optimize CPU-bound tasks by offloading heavy work to Dispatchers.Default, while simultaneously optimizing space by leveraging primitive-specialized collections like SparseArray or using Sequence transformations to prevent intermediate list allocations. Balancing both dimensions ensures battery efficiency, smooth animations, and zero out-of-memory crashes across diverse consumer hardware.""",
    "meta_ar": {
        "id": "DSA-01",
        "questionAr": "ما هو الفرق بين التعقيد الزمني (Time Complexity) والتعقيد المكاني (Space Complexity) في سياق تطبيقات أندرويد؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم التعقيد الزمني والمكاني، أثر الأداء الزمني على خيط واجهة المستخدم والـ 60fps/120fps والـ ANR، أثر التعقيد المكاني على ذاكرة الـ Heap ومجمع القمامة (GC Pauses) وOOM، وإدارة المفاضلة بين الوقت والمساحة.",
        "concept_ar": "يمثل التعقيد الزمني والمكاني المقياسين الرياضيين الأساسيين لتقييم كفاءة الخوارزميات مع نمو حجم المدخلات: يقيس التعقيد الزمني (Time Complexity) معدل تزايد عدد العمليات الحسابية اللازمة لتنفيذ الخوارزمية؛ وفي أندرويد، ينعكس هذا مباشرة على خيط واجهة المستخدم (Main Thread) المقيد بميزانية زمنية صارمة تبلغ 16.6 مللي ثانية لشاشات 60Hz أو 8.3 مللي ثانية لشاشات 120Hz؛ حيث يؤدي أي بطء زمني إلى سقوط الإطارات (Jank) وظهور رسالة التطبيق لا يستجيب (ANR) بعد 5 ثوانٍ. أما التعقيد المكاني (Space Complexity)، فيقيس حجم الذاكرة المؤقتة الإضافية (Auxiliary Memory) المستهلكة على الـ Heap ومكدس الاستدعاءات (Call Stack)؛ وفي أندرويد، يؤدي الاستهلاك المرتفع للذاكرة إلى إجهاد مجمع القمامة (Garbage Collector) مما يسبب وقفات تجميد مؤقتة (GC Pauses) ويعرض التطبيق لانهيارات نفاد الذاكرة (OutOfMemoryError). وتتطلب هندسة أندرويد الموازنة الذكية بين التضحية بذاكرة إضافية محسوبة لكسب سرعة زمنية تحافظ على سلاسة الواجهة.",
        "walkthrough_ar": """مقارنة بين خوارزمية تضحي بالذاكرة لتسريع الوقت وأخرى بطيئة دون ذاكرة إضافية:
```kotlin
// السيناريو: فحص وجود عنصرين مجموعهما يساوي القيمة المستهدفة
data class Product(val id: String, val price: Int)

// النهج 1: مساحة إضافية صفرية O(1) ولكن وقت تربيعي بطيء O(n^2)
fun hasPairBruteForce(products: List<Product>, target: Int): Boolean {
    for (i in products.indices) {
        for (j in i + 1 until products.size) {
            if (products[i].price + products[j].price == target) return true
        }
    }
    return false
}

// النهج 2: وقت خطي سريع O(n) مع استهلاك ذاكرة إضافية O(n)
fun hasPairOptimized(products: List<Product>, target: Int): Boolean {
    val seen = HashSet<Int>(products.size)
    for (p in products) {
        if (seen.contains(target - p.price)) return true
        seen.add(p.price)
    }
    return false
}
```""",
        "why_it_matters_ar": "الخوارزميات البطيئة زمنياً تجمد الشاشة وتسبب تقييمات سيئة على المتجر، والخوارزميات المستهلكة للذاكرة تؤدي لإغلاق التطبيق فجأة بسبب OOM على الهواتف الاقتصادية.",
        "worked_example_ar": "في شاشة بحث عن المنتجات، استبدلنا البحث التكراري في القائمة بجدول تجزئة HashSet؛ فانخفض وقت الاستجابة من 45ms إلى أقل من 1ms متجنبين إسقاط الإطارات أثناء التمرير.",
        "trade_offs_ar": "التضحية بالذاكرة عبر التخزين المؤقت يسرع التنفيذ ولكنه يزيد استهلاك الـ Heap؛ بينما الحفاظ التام على الذاكرة دون هياكل مساعدة يزيد استهلاك المعالج ويبطئ الواجهة.",
        "failure_modes_ar": "أخطر الأخطاء هو تنفيذ خوارزميات بترتيب تربيعي O(n^2) داخل دوال Compose أو onBindViewHolder، أو تجاهل مساحة مكدس الاستدعاءات في الخوارزميات التكرارية مما يسبب StackOverflowError.",
        "production_perspective_ar": "في بيئات الإنتاج، تُراقب أوقات تنفيذ الخوارزميات باستخدام Android Profiler وTrace للتحقق من عدم تجاوز الـ Main Thread لميزانية 8ms، وتُستخدم هياكل مثل SparseArray لتوفير الذاكرة.",
        "how_to_answer_ar": "عرف التعقيد الزمني وأثره المباشر على معدل الإطارات والـ ANR، ثم عرف التعقيد المكاني وأثره على الـ GC وOOM، واشرح مفاضلة الوقت والمساحة في أندرويد بأمثلة واقعية.",
        "talking_points_ar": "ميزانية الإطارات 16ms و8ms، خطأ ANR، ضغط مجمع القمامة GC Pressure، انهيار OOM، المفاضلة بين الوقت والذاكرة Space-Time Trade-off، وهياكل البيانات البديلة.",
        "follow_ups_ar": "كيف يؤثر استخدام Kotlin Sequences على التعقيد المكاني لسلاسل العمليات؟ ومتى يكون استخدام SparseArray أفضل من HashMap لتوفير الذاكرة؟",
        "self_check_ar": "هل ربطت التعقيد الزمني بمعدل الإطارات وANR، والتعقيد المكاني بضغط الـ GC وOOM ومفاضلة المساحة والوقت؟",
        "references_ar": f"- [Android Developers: Inspect your app\'s memory with Memory Profiler](https://developer.android.com/studio/profile/memory-profiler) — الدليل الرسمي لمراقبة استهلاك الذاكرة وتفادي ضغط مجمع القمامة.\n- [Android Developers: Profileable applications and frame rendering](https://developer.android.com/topic/performance/rendering/profile-gpu-rendering) — توثيق رسمي لمراقبة معدل الإطارات وتجنب بطء واجهة المستخدم.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """يقيس التعقيد الزمني معدل نمو العمليات الحسابية مع زيادة البيانات، ويؤثر مباشرة في أندرويد على سلاسة واجهة المستخدم ومعدل الإطارات وتفادي رسائل ANR. أما التعقيد المكاني فيقيس حجم الذاكرة المؤقتة الإضافية المستهلكة، ويؤثر على ضغط مجمع القمامة وخطر انهيار الذاكرة OOM. ويوازن المهندس المحترف بينهما لضمان سرعة العرض دون استنزاف ذاكرة الجهاز.""",
        "best_answer_ar": """يمثل التعقيد الزمني والتعقيد المكاني ركيزتي تقييم الأداء البرمجي في بيئة أندرويد المقيدة الموارد.
يقيس التعقيد الزمني كيفية تزايد زمن تنفيذ العمليات مع زيادة حجم المدخلات. وفي أندرويد، يرتبط هذا المقياس مباشرة بخيط واجهة المستخدم الرئيسي؛ حيث تفرض الشاشات الحديثة ميزانية زمنية لا تتعدى ثمانية إلى ستة عشر مللي ثانية لكل إطار، وأي خوارزمية ذات تعقيد زمني مرتفع تعمل على هذا الخيط ستتسبب في سقوط الإطارات وتجمد الرسوم المتحركة وصولاً لخطأ التطبيق لا يستجيب بعد خمس ثوانٍ.
أما التعقيد المكاني، فيقيس حجم الذاكرة المؤقتة الإضافية التي تخصصها الخوارزمية على الـ Heap ومكدس الاستدعاءات. وفي الهواتف ذات الميزانيات المحدودة للذاكرة، يؤدي التعقيد المكاني المرتفع إلى خلق دورات حجز وحذف سريعة للكائنات، مما يرفع ضغط مجمع القمامة ويتسبب في وقفات تجميد متكررة ويزيد من مخاطر انهيار نفاد الذاكرة.
ولذلك يعتمد مهندس أندرويد على مبدأ المفاضلة بين الوقت والمساحة؛ حيث نضحي بمقدار محسوب من الذاكرة عبر جداول التجزئة لتحقيق استجابة زمنية خطية أو ثابتة تحافظ على استقرار وسلاسة تجربة المستخدم.""",
        "deep_answer_ar": """من منظور البنية الداخلية لبيئة تشغيل أندرويد ومعمارية النظم، يحكم التعقيد الزمني والمكاني مدى استدامة التطبيق على العتاد وتجربة المستخدم الفعلية.
عند تحليل التعقيد الزمني، ينبغي على مهندس أندرويد ربط Big O مباشرة بنداءات Choreographer المسؤولة عن رسم إطارات الشاشة. فالخوارزميات التربيعية التي تعمل داخل مقارنات القوائم أو دورات إعادة التركيب في Compose قد تبدو مقبولة على بيانات تجريبية صغيرة في أجهزة التطوير القوية، لكنها عند زيادة البيانات في الإنتاج تتجاوز ميزانية الثمانية مللي ثوانٍ، مما يولد تقطيعاً بصرياً فادحاً يهدد ثقة المستخدم. وإذا استمر التعطيل، يتدخل النظام لإغلاق التطبيق قسراً عبر حوار ANR.
وعلى الجانب الآخر، يحدد التعقيد المكاني سلوك مجمع القمامة في بيئة تشغيل أندرويد الحديثة. والاعتقاد بأن توفر عدة غيغابايت من الرام في الهواتف يلغي أهمية الذاكرة هو وهم هندسي؛ فمساحة الـ Heap المخصصة لكل تطبيق تخضع لقيود صارمة من الشركة المصنعة. وتخصيص آلاف الكائنات المؤقتة داخل حلقات المعالجة يملأ الجيل الصغير من الذاكرة بسرعة، مما يجبر محرك ART على تشغيل دورات تجميع قمامة توقف التطبيق وتستنزف المعالج والبطارية.
ولذلك تتطلب الهندسة الرفيعة تحليلاً متوازناً؛ فننقل الحسابات الزمنية الثقيلة لخيوط الخلفية، بينما نحد من الاستهلاك المكاني باستخدام هياكل مخصصة مثل SparseArray أو توظيف Sequences لمنع إنشاء قوائم وسيطة، مما يضمن أداء فائق النعومة وخالياً من الانهيارات عبر مختلف أجهزة المستخدمين."""
    }
}

# ==========================================
# DSA-02: Explain O(1), O(log n), O(n), O(n log n), and O(n²).
# ==========================================
DATA["DSA-02"] = {
    "concept_en": """Asymptotic growth tiers categorize how algorithms scale under expanding input sizes:
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
  - Android Examples: Naive nested iteration comparing every item against every other item (e.g., duplicate detection without a Set), BubbleSort, and accidental nested iterations within `RecyclerView.Adapter.onBindViewHolder`.""",
    "walkthrough_en": """Kotlin implementations illustrating the five core complexity classes:
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
```""",
    "short_en": """O(1) executes in constant time regardless of size, O(log n) halves the search space each step like binary search, O(n) inspects every item linearly, O(n log n) represents optimal comparison sorting like TimSort, and O(n^2) grows quadratically via nested loops. Senior engineers select data structures that keep operations at O(1) or O(log n) to prevent UI frame starvation.""",
    "structured_en": """The core Big O complexity classes define how algorithm performance scales as dataset sizes increase.
Constant time O(1) represents operations that execute in a fixed number of steps, such as accessing an element by index in an array or average HashMap lookups. Logarithmic time O(log n) represents algorithms that divide the problem space in half with every step, exemplified by binary search in a sorted array, making it exceptionally fast even for millions of records.
Linear time O(n) means processing time increases proportionally with the input count, seen in single-pass iterations, linear searches, and JSON parsing. Linearithmic time O(n log n) is the benchmark for efficient sorting algorithms like TimSort, used internally by Kotlin collections, which divides the data and merges it linearly.
Quadratic time O(n^2) indicates algorithms where execution steps multiply quadratically, typically seen in nested loops comparing items against each other. In Android development, avoiding quadratic operations on the main thread is essential to prevent severe visual Jank and keep rendering within 16-millisecond frame budgets.""",
    "deep_senior_en": """From a computational complexity and runtime performance engineering perspective, these five complexity classes represent distinct scalability profiles that dictate whether code is viable for production mobile devices.
In Android systems, O(1) operations are our foundational building blocks. Array index lookups and average-case HashMap lookups provide predictable, sub-microsecond latency. However, senior engineers understand the hidden overheads: while an unboxed array access is pure O(1) with zero allocations, a HashMap get operation involves hash code calculation, bucket indexing, and potential linked-node pointer chasing that incurs CPU cache misses.
Logarithmic algorithms like binary search offer dramatic scalability advantages. Searching through a sorted catalog of one million items requires approximately twenty comparisons, making it millions of times faster than an O(n) sequential scan. This makes maintaining sorted lists and binary indexing vital when designing local Room queries or in-memory caches.
Linear algorithms represent the standard expectation for data processing pipelines, such as mapping or filtering network DTOs into domain models. While acceptable for modest datasets, chaining multiple linear operations without Sequences introduces hidden allocations that degrade performance.
Linearithmic complexity O(n log n) is the mathematical lower bound for comparison sorting. Kotlin standard collections employ TimSort, an adaptive algorithm combining MergeSort and InsertionSort that exploits existing ordered runs, executing in linear time on nearly-sorted data.
Finally, quadratic complexity O(n^2) is an absolute anti-pattern on UI rendering paths. A classic failure mode in Android occurs when an engineer performs an O(n) search inside a RecyclerView onBindViewHolder callback or a Compose item row. Because the adapter binds n items, the overall screen rendering degrades into an accidental O(n^2) operation, causing dropped frames and severe stutter. Mastering these classifications enables engineers to proactively refactor algorithms before code reaches production devices.""",
    "meta_ar": {
        "id": "DSA-02",
        "questionAr": "اشرح الفروق بين رتب التعقيد: O(1)، O(log n)، O(n)، O(n log n)، وO(n²).",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم رتب التعقيد الحسابي الشائعة، تطبيقات كل رتبة في كوتلن وأندرويد، خصائص النمو الرياضي، وتأثير العمليات التربيعية على أداء واجهة المستخدم.",
        "concept_ar": "تصنف رتب التعقيد الحسابي الشائعة معدلات نمو الخوارزميات مع تضاعف حجم المدخلات: تمثل O(1) التعقيد الثابت (Constant Time)؛ حيث لا يتغير زمن التنفيذ مهما كبرت البيانات، مثل الوصول لعنصر في المصفوفة عبر الفهرس أو القراءة من جدول التجزئة في الحالة المتوسطة. وتمثل O(log n) التعقيد اللوغاريتمي (Logarithmic Time)؛ حيث يتقلص نطاق البحث إلى النصف في كل خطوة، كما في خوارزمية البحث الثنائي (Binary Search). وتمثل O(n) التعقيد الخطي (Linear Time)؛ حيث يتناسب وقت التنفيذ طردياً مع عدد العناصر، مثل المرور على القائمة بحلقة تكرار واحدة أو تصفية العناصر عبر filter. أما O(n log n) فتمثل التعقيد شبه الخطي (Linearithmic Time)؛ وهي الكفاءة القياسية لخوارزميات الفرز المقارن مثل TimSort المستخدمة في كوتلن. وأخيراً تمثل O(n^2) التعقيد التربيعي (Quadratic Time)؛ الناتج عن الحلقات التكرارية المتداخلة، وهو نمط خطير يسبب بطئاً شديداً في أندرويد إذا نُفذ داخل قوائم العرض.",
        "walkthrough_ar": """تطبيقات عملية في كوتلن على الرتب الخمس للتعقيد:
```kotlin
// 1. O(1) تعقيد ثابت: قراءة عنصر عبر الفهرس مباشرة
fun getItemAt(list: List<String>, index: Int): String = list[index]

// 2. O(log n) تعقيد لوغاريتمي: البحث الثنائي في مصفوفة مرتبة
fun searchLog(sortedList: List<Int>, key: Int): Int = sortedList.binarySearch(key)

// 3. O(n) تعقيد خطي: تصفية قائمة كاملة بمرور واحد
fun getActive(users: List<User>): List<User> = users.filter { it.isActive }

// 4. O(n log n) تعقيد شبه خطي: فرز قائمة منتجات باستخدام TimSort
fun sortList(items: List<Product>): List<Product> = items.sortedBy { it.price }

// 5. O(n^2) تعقيد تربيعي: حلقات متداخلة تفحص كل عنصر ضد كافة العناصر
fun findDuplicatesNaive(list: List<String>): Boolean {
    for (i in list.indices) {
        for (j in i + 1 until list.size) {
            if (list[i] == list[j]) return true
        }
    }
    return false
}
```""",
        "why_it_matters_ar": "الخلط بين هذه الرتب يؤدي إلى اتخاذ قرارات معمارية خاطئة؛ مثل استخدام خوارزمية تربيعية تجمد الشاشة بدلاً من هيكل بيانات خطي أو ثابت.",
        "worked_example_ar": "عند مقارنة قائمتين من 10,000 عنصر، كانت المقارنة المتداخلة O(n^2) تستغرق عدة ثوانٍ وتجمد الشاشة، وباستخدام HashSet تحولت العملية لـ O(n) ونُفذت في 15ms.",
        "trade_offs_ar": "خوارزميات O(log n) تتطلب أن تكون البيانات مرتبة مسبقاً بتكلفة O(n log n)؛ بينما البحث الخطي O(n) يعمل على البيانات غير المرتبة فوراً دون تكلفة تجهيز مسبقة.",
        "failure_modes_ar": "أخطر الأخطاء هو تنفيذ عملية بحث خطي O(n) داخل دالة onBindViewHolder لكل عنصر، مما يحول عرض القائمة بالكامل إلى كارثة تربيعية O(n^2) تسقط إطارات التمرير.",
        "production_perspective_ar": "في كود الإنتاج، تُصمم شاشات أندرويد لتعمل بالكامل بتعقيد O(1) أو O(log n) للعمليات المتكررة، مع ترحيل عمليات O(n log n) لخيوط العمل في الخلفية.",
        "how_to_answer_ar": "ابدأ بشرح كل رتبة بالترتيب من الأسرع للأبطأ، واذكر مثالاً واقعياً من كوتلن وأندرويد لكل رتبة، وركز على خطورة O(n^2) على سلاسة الواجهة ومعدل الـ 60fps.",
        "talking_points_ar": "التعقيد الثابت O(1)، البحث الثنائي O(log n)، التصفية الخطية O(n)، فرز TimSort بـ O(n log n)، الحلقات المتداخلة O(n^2)، ومصيدة الحسابات داخل دوال القوائم.",
        "follow_ups_ar": "لماذا يعد خوارزمية TimSort في كوتلن أسرع عملياً من QuickSort على البيانات شبه المرتبة؟ وكيف تتجنب التعقيد التربيعي العرضي في Compose؟",
        "self_check_ar": "هل شرحت الرتب الخمس بالتسلسل وربطت كل رتبة بأمثلة كوتلن وحذرت من O(n^2) في واجهة المستخدم؟",
        "references_ar": f"- [Kotlin Standard Library: Collections Sorting](https://kotlinlang.org/api/latest/jvm/stdlib/kotlin.collections/sorted.html) — التوثيق الرسمي لخوارزميات الفرز وكفاءتها في كوتلن.\n- [Big-O Cheat Sheet](https://www.bigocheatsheet.com/) — المرجع القياسي العالمي لرتب التعقيد الحسابي ومقارنتها.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """تمثل O(1) التعقيد الثابت اللحظي مثل الوصول للمصفوفة، وO(log n) التعقيد اللوغاريتمي الذي يقلص نطاق البحث للنصف كالبحث الثنائي، وO(n) التعقيد الخطي الذي يمر على العناصر، وO(n log n) كفاءة الفرز القياسية كـ TimSort، وO(n^2) التعقيد التربيعي البطيء الناتج عن الحلقات المتداخلة ويجب تجنبه في واجهة أندرويد.""",
        "best_answer_ar": """تحدد رتب التعقيد الحسابي الخمس نمط توسع الخوارزميات ومدى ملاءمتها للأجهزة المحمولة.
التعقيد الثابت O(1) ينفذ العمليات في خطوات محددة بغض النظر عن حجم البيانات، مثل قراءة عنصر من مصفوفة عبر الفهرس أو استرجاع قيمة من جدول التجزئة في المتوسط. والتعقيد اللوغاريتمي O(log n) يقسم مساحة البحث إلى النصف في كل خطوة، مثل البحث الثنائي في مصفوفة مرتبة، وهو فائق السرعة حتى مع ملايين العناصر.
أما التعقيد الخطي O(n) فينمو فيه وقت المعالجة طردياً مع عدد المدخلات، كما في المرور على عناصر القائمة أو تصفيتها أو قراءة نصوص JSON المتسلسلة. ويعد التعقيد شبه الخطي O(n log n) المعيار الذهبي لخوارزميات الفرز الفعالة مثل TimSort المعتمدة في كوتلن، والتي تقسم البيانات ثم تدمجها خطياً.
وفي المقابل، يمثل التعقيد التربيعي O(n^2) الخطر الأكبر لأنه يضاعف العمليات بصورة حادة نتيجة الحلقات المتداخلة التي تقارن كل عنصر بالآخرين؛ وتجنب هذا النمط في خيط واجهة المستخدم بأندرويد أمر حاسم لمنع تجمد الشاشة وسقوط الإطارات.""",
        "deep_answer_ar": """من منظور هندسة الحوسبة وتحسين الأداء في أجهزة أندرويد، تحدد هذه الرتب الخمس ما إذا كان الكود البرمجي قابلاً للعمل في بيئة الإنتاج دون مشاكل.
تمثل عمليات O(1) حجر الزاوية في بناء الأنظمة السريعة؛ فقراءة المصفوفات وجداول التجزئة تمنح استجابة فورية. ومع ذلك، يدرك المهندس المتمرس الفروق الدقيقة للعتاد؛ فالوصول لمصفوفة بدائية يتميز بذاكرة متصلة وكاش معالج مباشر، بينما يتطلب جدول التجزئة حساب الهاش وتتبع مؤشرات الذاكرة التي قد تسبب إخفاقات في كاش المعالج.
وتبرز قوة التعقيد اللوغاريتمي O(log n) في سرعة التعامل مع البيانات الضخمة؛ فالبحث في مليون سجل عبر البحث الثنائي يتطلب عشرين مقارنة فقط مقارنة بمليون عملية في البحث الخطي، مما يجعل الفهرسة المرتبة في قواعد بيانات Room والذاكرة أمراً جوهرياً للأداء.
أما العمليات الخطية O(n)، فهي النمط المعتاد لتحويل واستخراج البيانات، ولكن تكرار دمجها دون استخدام Sequences ينشئ مصفوفات وسيطة ترهق الذاكرة. وبالنسبة لفرز البيانات، تستخدم كوتلن خوارزمية TimSort ذات الكفاءة O(n log n)، والتي تستغل الأجزاء المرتبة مسبقاً في البيانات لتصل إلى سرعة خطية في الحالات المثالية.
وأخيراً، يعد التعقيد التربيعي O(n^2) خطيئة كبرى على خيط واجهة المستخدم؛ وأشهر فخاخ الأداء في أندرويد هو كتابة بحث خطي داخل دالة onBindViewHolder أو داخل عناصر Compose؛ مما يحول رسم القائمة من عملية خطية سلسة إلى كارثة تربيعية تسقط إطارات العرض وتدمر تجربة المستخدم بالكامل."""
    }
}

# ==========================================
# DSA-03: Why are constants and lower-order terms omitted in asymptotic analysis?
# ==========================================
DATA["DSA-03"] = {
    "concept_en": """Asymptotic analysis abstracts low-level hardware variations to describe theoretical growth trends as input sizes scale toward infinity:
- Mathematical Dominance at Scale ($n \to \infty$):
  - Consider the execution step polynomial $f(n) = 3n^2 + 500n + 10000$.
  - When $n = 10$, lower-order terms dominate: $10000$ represents the vast majority of operations.
  - When $n = 1,000,000$, $3n^2 = 3 \times 10^{12}$, while $500n = 5 \times 10^8$ and $10000$ becomes negligible noise ($< 0.02\%$ of total work).
  - Mathematically, $\lim_{n \to \infty} \frac{3n^2 + 500n + 10000}{n^2} = 3$. The highest-order term dictates the fundamental growth rate.
- Machine and Platform Independence:
  - Multiplicative constants reflect clock speeds, CPU architectures, compiler optimizations, and ART JIT compilation tiers.
  - Big O purposefully abstracts hardware variables to characterize the inherent efficiency of the algorithm itself across heterogeneous client devices.
- The Real-World Mobile Caveat: Constants Matter for Small $n$!
  - In mobile apps, $n$ is frequently small (e.g., $n \le 30$ in a settings menu or navigation tab list).
  - An $O(n)$ algorithm with tight cache locality (such as contiguous memory in an `Array` or `IntArray`) frequently outperforms an $O(1)$ `HashMap` lookup due to high constant overheads in hashing, object header metadata, boxing, and pointer dereferencing.""",
    "walkthrough_en": """Benchmarking why constants matter for small datasets in Android:
```kotlin
// Demonstrating where an O(n) array scan beats an O(1) HashMap lookup for small n
fun benchmarkSmallN() {
    val size = 15 // Typical size for tabs, filter tags, or settings
    val keys = IntArray(size) { it }
    val values = Array(size) { "Item $it" }

    // HashMap: Theoretically O(1), but carries high constant factor:
    // (Hash computation + Entry object pointer chase + boxing)
    val map = HashMap<Int, String>(size).apply {
        for (i in 0 until size) put(keys[i], values[i])
    }

    // Benchmark lookup for target key
    val target = 14

    // Linear scan: Theoretically O(n), but extremely low constant factor:
    // (Contiguous CPU L1 cache prefetching, zero boxing, zero hashing)
    var foundValue: String? = null
    for (i in 0 until size) {
        if (keys[i] == target) {
            foundValue = values[i]
            break
        }
    }

    // For n <= 20, the O(n) contiguous array scan often completes in fewer
    // CPU clock cycles than the O(1) HashMap lookup!
}
```""",
    "short_en": """Constants and lower-order terms are omitted in Big O analysis because as input sizes grow toward infinity, the highest-order term mathematically dominates the overall growth rate. Omitting constants ensures hardware-independent algorithmic evaluation. However, in mobile engineering where input sizes are often small, low constant factors and CPU cache locality can make an O(n) array scan faster than an O(1) hash map.""",
    "structured_en": """In asymptotic analysis, constants and lower-order terms are omitted to focus on the fundamental growth rate of an algorithm as inputs scale toward infinity.
Mathematically, as the input size expands into thousands or millions, the highest-order term completely dominates the total execution time. For an equation like 5n squared plus 100n plus 5000, the n squared term accounts for over 99 percent of operations at large scales, rendering lower-order terms and coefficients mathematically insignificant.
Furthermore, constants are omitted to maintain platform independence. Multiplicative constants reflect CPU clock rates, memory bandwidth, and compiler optimizations rather than algorithmic design.
However, senior Android engineers recognize a vital mobile caveat: constants matter significantly for small datasets. When dealing with lists of fewer than twenty items, an O(n) linear scan across a contiguous array often runs faster than an O(1) HashMap lookup because the array enjoys contiguous CPU cache prefetching and zero hashing or object boxing overhead.""",
    "deep_senior_en": """From the dual perspectives of theoretical computer science and low-level mobile systems engineering, the omission of constants in asymptotic analysis serves a distinct purpose that must be balanced against physical hardware realities.
Theoretically, Big O notation is designed to classify algorithms by their asymptotic scalability as n approaches infinity. When analyzing an equation like 4n squared plus 200n plus 1000, lower-order terms become mathematically inconsequential as datasets expand. Dividing the entire polynomial by its highest-order term reveals that the limit converges to a finite constant. By dropping coefficients and lower-order terms, Big O provides an invariant measure of algorithmic scalability that remains true whether code executes on an Android emulator, a budget smartphone, or an enterprise cloud cluster.
However, in physical Android application engineering, the assumption that n approaches infinity is frequently violated. Mobile UI components routinely process bounded datasets: a bottom navigation bar has five tabs, a profile screen displays ten fields, and a settings menu contains twenty toggles.
In these small-n domains, constant factors and hardware mechanics dominate performance. A HashMap offers theoretical O(1) average-case lookups, but its constant factor includes hash code generation, bucket indexing, Entry object allocation, and pointer dereferencing that routinely triggers CPU cache misses. In contrast, an O(n) linear search over a contiguous primitive IntArray or Android SparseArray benefits from CPU hardware prefetching and spatial cache locality. For small datasets, the linear scan often executes in fewer CPU cycles than the hash lookup. Senior engineers leverage asymptotic notation for architecture, while respecting constant factors during micro-optimization on mobile hardware.""",
    "meta_ar": {
        "id": "DSA-03",
        "questionAr": "لماذا يتم إهمال الثوابت (Constants) والحدود الدنيا (Lower-Order Terms) في تحليل الـ Big O؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "الأساس الرياضي لتحليل التقارب (Asymptotic Analysis)، هيمنة الحد الأعلى عند نمو البيانات، عزل تأثير العتاد والـ JIT، والفارق العملي بين النظرية والواقع في أندرويد عند التعامل مع أحجام صغيرة.",
        "concept_ar": "يتم إهمال الثوابت والحدود الدنيا في تحليل الـ Big O للتركيز على معدل النمو الحقيقي للخوارزمية عند اقتراب حجم المدخلات من اللانهاية ($n \to \infty$): رياضياً، عندما تكبر المدخلات لتصل إلى مئات الآلاف، يهيمن الحد الأعلى (Highest-Order Term) على أكثر من 99% من زمن التنفيذ؛ ففي معادلة مثل $3n^2 + 500n + 10000$، يصبح تأثير الـ $500n$ والـ $10000$ ضئيلاً للغاية مقارنة بـ $3n^2$. ثانياً، تُهمل الثوابت لعزل الفروق العتادية؛ فالثوابت تتغير بتغير سرعة المعالج ومعمارية الشريحة وتحسينات مترجم الـ ART JIT، والهدف من Big O هو تقييم جودة الخوارزمية ذاتها مجردة عن بيئة التشغيل. ولكن في واقع أندرويد العملي، تكتسب الثوابت أهمية قصوى عند التعامل مع بيانات صغيرة ($n \le 20$)؛ حيث يتفوق البحث الخطي $O(n)$ في مصفوفة متصلة على جدول التجزئة $O(1)$ بسبب الاستفادة من كاش المعالج وغياب تكلفة التجزئة وتغليف الكائنات (Boxing).",
        "walkthrough_ar": """مقارنة عملية توضح تفوق البحث الخطي على HashMap في الأحجام الصغيرة:
```kotlin
// فحص تفوق المصفوفة المتصلة على HashMap عندما يكون الحجم صغيراً (n = 15)
fun compareSmallLookup() {
    val size = 15
    val keys = IntArray(size) { it }
    val values = Array(size) { "Value $it" }

    // HashMap: نظرياً O(1) ولكنها تحمل ثوابت عالية (حساب الهاش + مؤشرات الذاكرة + Boxing)
    val map = HashMap<Int, String>()
    for (i in 0 until size) map[keys[i]] = values[i]

    val targetKey = 14

    // البحث الخطي: نظرياً O(n) ولكنه يتميز بثوابت بالغة الصغر
    // (ذاكرة L1 Cache متصلة + قراءة فورية بدون كائنات إضافية)
    var result: String? = null
    for (i in 0 until size) {
        if (keys[i] == targetKey) {
            result = values[i]
            break
        }
    }
    // في الأحجام الصغيرة، البحث الخطي ينفذ في دورات معالج أقل بكثير من HashMap!
}
```""",
        "why_it_matters_ar": "فهم إهمال الثوابت يمنع الوقوع في فخ التحسين المبكر النظري، ويوضح لماذا قد تكون الخوارزمية الأبسط أسرع عملياً على الهواتف الذكية.",
        "worked_example_ar": "في شاشة إعدادات بها 12 عنصراً، كان استخدام مصفوفة IntArray بسيطة بالبحث الخطي أسرع في استهلاك الذاكرة والمعالج من بناء HashMap معقدة.",
        "trade_offs_ar": "التحليل النظري يركز على سلوك البيانات الضخمة عند اللانهاية؛ بينما الهندسة العملية في الموبايل تراعي الثوابت المادية وكاش المعالج للأحجام الصغيرة المحصورة.",
        "failure_modes_ar": "أخطر الأخطاء هو افتراض أن O(1) أسرع دائماً في كافة الظروف، أو استخدام هياكل بيانات ثقيلة ذات ثوابت عالية لمعالجة 5 عناصر في واجهة المستخدم.",
        "production_perspective_ar": "في كود أندرويد الداخلي، توفر منصة أندرويد هياكل مخصصة مثل SparseArray وArrayMap مخصصة للأحجام الصغيرة لتفادي ثوابت الذاكرة في HashMap.",
        "how_to_answer_ar": "ابدأ بالتفسير الرياضي وهيمنة الحد الأعلى عند نمو البيانات، ثم فسر عزل أثر العتاد، واختم بالحقيقة العملية في أندرويد وتأثير الثوابت وكاش المعالج في الأحجام الصغيرة.",
        "talking_points_ar": "التحليل التقاربي Asymptotic Analysis، هيمنة الحد الأعلى، استقلال التحليل عن العتاد، أهمية الثوابت في الموبايل، كاش المعالج L1 Cache، وهياكل SparseArray.",
        "follow_ups_ar": "متى تبدأ خوارزمية O(1) في التفوق الفعلي على O(n) في أندرويد؟ وكيف صممت Google هيكل ArrayMap لتوفير الذاكرة؟",
        "self_check_ar": "هل شرحت الأساس الرياضي لإهمال الثوابت، وأكدت على أهميتها العملية في الأحجام الصغيرة وكاش المعالج في أندرويد؟",
        "references_ar": f"- [Android Developers: SparseArray documentation](https://developer.android.com/reference/android/util/SparseArray) — التوثيق الرسمي لهيكل البيانات المحسن لاستهلاك الذاكرة في أندرويد.\n- [Introduction to Algorithms (CLRS): Asymptotic Notation](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/) — المرجع الأكاديمي الكلاسيكي لتحليل التقارب وإهمال الثوابت.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """تُهمل الثوابت والحدود الدنيا رياضياً لأن الحد الأعلى يهيمن تماماً على وقت التنفيذ مع نمو البيانات نحو اللانهاية، ولعزل المتغيرات العتادية كسرعة المعالج ومترجم الـ JIT. ولكن في أندرويد، تكتسب الثوابت أهمية بالغة في المجموعات الصغيرة حيث يتفوق البحث الخطي في مصفوفة متصلة على جدول التجزئة بفضل كاش المعالج وانعدام التجزئة.""",
        "best_answer_ar": """يتم إهمال الثوابت والحدود الدنيا في تحليل Big O للتركيز على معدل التوسع الجذري للخوارزمية مع نمو حجم المدخلات نحو أرقام هائلة.
رياضياً، عندما يقترب الحجم من اللانهاية، يبتلع الحد الأعلى النسبة العظمى من العمليات؛ ففي معادلة تضم ن تربيع مع حد خطي وثابت، يمثل الحد التربيعي أكثر من تسعة وتسعين بالمئة من وقت التشغيل عند وصول البيانات للملايين، مما يجعل باقي الحدود غير مؤثرة حسابياً.
كما أن إهمال المعاملات الثابتة يضمن تقييماً مجرداً لا يتأثر بنوع الجهاز؛ فالثابت العددي يتغير بحسب سرعة معالج الهاتف ونوع الذاكرة وتحسينات المترجم.
ومع ذلك، يدرك مهندس أندرويد الخبير استثناءً عملياً بالغ الأهمية؛ ففي التطبيقات المحمولة تكون أحجام البيانات محصورة وصغيرة في كثير من الشاشات، مثل قوائم الخيارات التي لا تتعدى عشرين عنصراً. وفي هذه المساحة الصغيرة، تتفوق الثوابت المنخفضة في المصفوفات المتصلة بفضل كاش المعالج السريع على جداول التجزئة ذات التعقيد الثابت نظرياً ولكن بتكلفة ثوابت مرتفعة في الهاش وحجز الكائنات.""",
        "deep_answer_ar": """من منظور علم الحاسوب النظري والهندسة الدقيقة لأنظمة أندرويد، يحقق إهمال الثوابت هدفين جوهريين يجب موازنتهما مع الواقع المادي للعتاد.
من الناحية الرياضية، صُمم ترميز Big O لتصنيف الخوارزميات وفق سلوكها التقاربي عند اقتراب المدخلات من اللانهاية؛ فعند قسمة معادلة الأداء على حدها الأكبر، تتلاشى الحدود الدنيا تدريجياً لتصل إلى الصفر، مما يثبت أن الحد الأعلى وحده هو الحاكم لمسار النمو. وإلغاء المعاملات الثابتة يتيح مقارنة الخوارزميات بمعيار موضوعي مستقل عن تردد المعالج أو ذاكرة الجهاز أو اختلافات بيئة تشغيل ART بين الهواتف الاقتصادية والرائدة.
ولكن في العالم الواقعي لتطوير تطبيقات الهواتف، نادراً ما تقترب البيانات من اللانهاية في الشاشات العادية؛ فالقوائم غالباً ما تحتوي على عناصر محدودة كعشرة خيارات في ملف المستخدم أو خمسة ألسنة في شريط التنقل.
وهنا تفرض فيزياء العتاد نفسها؛ فجدول التجزئة HashMap وإن كان يمتلك تعقيداً ثابتاً نظرياً، إلا أن الثابت الزمني له ضخم؛ فهو يتضمن حساب الهاش، وتوزيع الـ Buckets، وحجز كائنات العقد، وملاحقة مؤشرات الذاكرة التي تسبب إخفاقات متتالية في كاش المعالج. وفي المقابل، يتميز البحث الخطي في مصفوفة بدائية متصلة مثل IntArray بثوابت متناهية الصغر؛ حيث يقرأ المعالج البيانات مسبقاً في كاش L1 دفعة واحدة. ولذلك يتفوق البحث الخطي في هذه الأحجام الصغيرة، مما دفع جوجل لابتكار هياكل مخصصة مثل SparseArray للموازنة بين النظرية والواقع العملي."""
    }
}

# ==========================================
# DSA-04: Does Big O necessarily describe the worst case? Explain upper bounds versus cases.
# ==========================================
DATA["DSA-04"] = {
    "concept_en": """A foundational misconception in computer science is conflating asymptotic mathematical bounds ($O, \Omega, \Theta$) with algorithmic scenario cases (Best, Average, Worst):
- Asymptotic Bounds (Mathematical Formulations):
  - Big O ($O$): Represents an asymptotic upper bound. $f(n) = O(g(n))$ states that growth rate is bounded from above by $c \cdot g(n)$ for all sufficiently large $n$. It defines a mathematical growth ceiling.
  - Big Omega ($\Omega$): Represents an asymptotic lower bound. It defines a mathematical growth floor.
  - Big Theta ($\Theta$): Represents an asymptotically tight bound. Holds when an algorithm is simultaneously $O(g(n))$ and $\Omega(g(n))$.
- Algorithmic Cases (Execution Scenarios):
  - Best-Case: Scenario where input data structure requires minimal work (e.g., searching for an element located at index 0).
  - Average-Case: Expected computational work across all randomized input permutations.
  - Worst-Case: Adversarial or pathological input permutation requiring maximum work (e.g., searching for an element not present in the list).
- Big O Describes ANY Case:
  - Big O is not synonymous with the worst case; one can formulate the Big O upper bound of any scenario case:
    - Linear Search: Best-case is $O(1)$, worst-case is $O(n)$, average-case is $O(n)$.
    - InsertionSort: Best-case (pre-sorted input) is $O(n)$, worst-case (reverse-sorted) is $O(n^2)$.
    - QuickSort: Best-case is $O(n \log n)$, average-case is $O(n \log n)$, worst-case (degenerate pivot selection) is $O(n^2)$.
- Mobile Systems Engineering Reality:
  - While average-case determines battery and CPU thermal throttling, mobile engineers must architect against worst-case Big O bounds on the UI thread to guarantee that degenerate inputs never induce frame drops or ANR freezes.""",
    "walkthrough_en": """Kotlin examples illustrating distinct case complexities and their Big O bounds:
```kotlin
// Demonstrating Best, Average, and Worst case complexities with Big O bounds
class SearchService {

    // Linear Search:
    // - Best-case scenario (target at index 0): O(1)
    // - Worst-case scenario (target missing or at end): O(n)
    // - Average-case scenario: O(n)
    fun findUserIndex(users: List<String>, target: String): Int {
        for (i in users.indices) {
            if (users[i] == target) return i // Best-case early return
        }
        return -1 // Worst-case full traversal
    }

    // Insertion Sort:
    // - Best-case scenario (already sorted): O(n) operations
    // - Worst-case scenario (reverse sorted): O(n^2) operations
    fun insertionSort(arr: IntArray) {
        for (i in 1 until arr.size) {
            val key = arr[i]
            var j = i - 1
            while (j >= 0 && arr[j] > key) {
                arr[j + 1] = arr[j]
                j--
            }
            arr[j + 1] = key
        }
    }
}
```""",
    "short_en": """Big O does not inherently mean worst case; it is a mathematical upper bound that can describe any execution scenario. Algorithms have best, average, and worst-case scenarios, and each scenario has its own Big O bound. For example, linear search has an O(1) best-case and an O(n) worst-case. In Android, engineers design against worst-case bounds on the UI thread to guarantee frame rate stability.""",
    "structured_en": """Big O notation is frequently misunderstood as synonymous with worst-case performance, but it is actually a mathematical tool describing an asymptotic upper bound.
In algorithmic analysis, there are two orthogonal dimensions: asymptotic bounds and scenario cases. The bounds are Big O for upper bounds, Big Omega for lower bounds, and Big Theta for tight bounds. The scenario cases describe real-world inputs: best case, average case, and worst case.
Big O can be applied to any of these cases. For instance, in linear search, the best case occurs when the target is at index zero, which has a Big O bound of O(1). The worst case occurs when the target is missing, which has a Big O bound of O(n).
In Android mobile development, understanding this distinction is crucial. While average-case complexity predicts typical battery and CPU thermal efficiency, engineers must architect for worst-case Big O bounds on the main thread to ensure pathological user inputs never freeze rendering or trigger Application Not Responding crashes.""",
    "deep_senior_en": """From a formal computer science and mobile systems reliability perspective, conflating Big O with worst-case analysis represents an imprecise understanding of algorithmic modeling.
Big O notation is purely a mathematical ceiling function. Stating that a function is O of g of n means that past a certain threshold, the function never exceeds a constant multiple of g of n. Big Omega provides the corresponding mathematical floor, while Big Theta denotes that the upper and lower bounds meet, establishing an exact asymptotic rate of growth.
Orthogonal to these mathematical notations are algorithmic execution cases. An algorithm encounters different operational paths depending on input arrangement. In QuickSort, the best and average cases partition data evenly, running in O of n log n time. However, if pivot selection degenerates on an already sorted array, QuickSort encounters its worst-case scenario, running in O of n squared time. Here, O of n squared is the upper bound of the worst-case, while O of n log n is the upper bound of the average-case.
In Android production systems, this distinction directly dictates threading and safety architectures. A common engineering defect is relying on average-case guarantees on the main thread. A HashMap provides O of one average lookups, but in the pathological worst-case of hash collisions, lookups degrade to linear or logarithmic scans. If an algorithm running inside a scroll handler relies on optimistic average cases, an adversarial or degenerate input triggers worst-case behavior, causing dropped frames and UI lockups. Senior engineers evaluate worst-case Big O ceilings for UI-bound code while utilizing average-case models for background synchronization pipelines.""",
    "meta_ar": {
        "id": "DSA-04",
        "questionAr": "هل يصف الـ Big O بالضرورة أسوأ حالة (Worst Case)؟ اشرح الفارق بين الحدود الرياضية وحالات التشغيل.",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "التمييز بين الحدود الرياضية (Big O, Big Omega, Big Theta) وسيناريوهات التشغيل (Best, Average, Worst Case)، إمكانية تطبيق Big O على أي حالة، وأهمية مراعاة أسوأ الحالات في خيط واجهة مستخدم أندرويد.",
        "concept_ar": "من الأخطاء الشائعة في هندسة البرمجيات الخلط بين الـ Big O وأسوأ حالة تشغيل؛ فالـ Big O في الأصل هو سقف رياضي أعلى (Upper Bound) يمكن استخدامه لوصف أي سيناريو تشغيلي: تنقسم المفاهيم إلى بعدين مستقلين: الأول هو الحدود الرياضية وتشمل Big O (الحد الأقصى للنمو)، وBig Omega (الحد الأدنى للنمو)، وBig Theta (الحد الحتمي المحصور بين الأدنى والأقصى). أما البعد الثاني فهو حالات التشغيل الواقعية وتشمل أفضل حالة (Best Case)، والحالة المتوسطة (Average Case)، وأسوأ حالة (Worst Case). ويمكن تطبيق Big O على أي من هذه الحالات؛ فمثلاً في خوارزمية البحث الخطي، أفضل حالة هي العثور على العنصر في أول موضع وتعقيدها هو $O(1)$، بينما أسوأ حالة عند عدم وجود العنصر وتعقيدها هو $O(n)$. وفي أندرويد، يجب على المهندس دائماً معرفة السقف الأعلى لأسوأ حالة على الـ Main Thread لضمان عدم انهيار سلاسة الإطارات عند استقبال مدخلات استثنائية أو معطوبة.",
        "walkthrough_ar": """تطبيق يوضح الحالات المختلفة للخوارزمية وحدودها الرياضية في كوتلن:
```kotlin
class SearchExample {
    // خوارزمية البحث الخطي:
    // أفضل حالة (العنصر في البداية): تعقيدها O(1)
    // أسوأ حالة (العنصر غير موجود): تعقيدها O(n)
    // الحالة المتوسطة (العنصر في المنتصف): تعقيدها O(n)
    fun linearSearch(list: List<Int>, target: Int): Int {
        for (i in list.indices) {
            if (list[i] == target) return i // أفضل حالة خروج فوري
        }
        return -1 // أسوأ حالة تفتيش كامل
    }

    // خوارزمية الفرز بالإدراج Insertion Sort:
    // أفضل حالة (المصفوفة مرتبة مسبقاً): O(n)
    // أسوأ حالة (المصفوفة معكوسة الترتيب): O(n^2)
    fun insertionSort(arr: IntArray) {
        for (i in 1 until arr.size) {
            val key = arr[i]
            var j = i - 1
            while (j >= 0 && arr[j] > key) {
                arr[j + 1] = arr[j]
                j--
            }
            arr[j + 1] = key
        }
    }
}
```""",
        "why_it_matters_ar": "الاعتماد على أن Big O يمثل أسوأ حالة دائماً يسبب سوء فهم لأداء الخوارزميات، والاعتماد على الحالة المتوسطة في الـ Main Thread قد يجمد التطبيق في الإنتاج.",
        "worked_example_ar": "في خوارزمية QuickSort، الحالة المتوسطة هي O(n log n) ولكن أسوأ حالة هي O(n^2)؛ ونقل فرز القوائم لخيط الخلفية يضمن عدم تجمد الشاشة إذا صادف التطبيق أسوأ حالة.",
        "trade_offs_ar": "التصميم للحالة المتوسطة يسهل كتابة الكود ويوفر استهلاك البطارية في الظروف العادية؛ بينما التصميم للحد الأقصى لأسوأ حالة يضمن استقرار الواجهة في كافة الظروف الحافة (Edge Cases).",
        "failure_modes_ar": "أخطر الأخطاء هو تشغيل خوارزمية على الـ UI Thread بافتراض حالتها المتوسطة O(1) مثل HashMap، لتفاجأ في الإنتاج بحالة تصادم هاش تنحدر إلى O(n) وتسقط إطارات التمرير.",
        "production_perspective_ar": "في كبرى التطبيقات، تُختبر شاشات العرض ببيانات غير عشوائية تماثل أسوأ السيناريوهات (Adversarial Data) للتحقق من عدم حدوث أي تهنيج أو ANR في الإنتاج.",
        "how_to_answer_ar": "انفِ بقوة أن Big O يعني أسوأ حالة حصراً، ثم اشرح الفارق بين الحدود الرياضية (O, Omega, Theta) وحالات التشغيل (Best, Average, Worst)، واذكر أمثلة واقعية وأهمية ذلك في أندرويد.",
        "talking_points_ar": "السقف الأعلى الرياضي Upper Bound، الفارق بين الحدود وحالات التشغيل، Big Omega وBig Theta، مثال البحث الخطي والفرز بالإدراج، ومخاطر أسوأ الحالات على خيط الواجهة.",
        "follow_ups_ar": "متى تستخدم Big Theta بدلاً من Big O في تحليل الدوال؟ وكيف تحمي التطبيق من هجمات الـ HashDoS التي تستهدف أسوأ حالات جداول التجزئة؟",
        "self_check_ar": "هل وضحت أن Big O سقف رياضي يصف أي حالة، وشرحت الفارق بين الحالات والحدود، وأكدت على أهمية أسوأ حالة في الـ Main Thread؟",
        "references_ar": f"- [MIT OpenCourseWare: Introduction to Algorithms, Asymptotic Notation](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/resources/lecture-1-algorithmic-thinking-peak-finding/) — محاضرة MIT التأسيسية حول المفاهيم الدقيقة للحدود الرياضية.\n- [Introduction to Algorithms (CLRS): Growth of Functions](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/) — المرجع القياسي العالمي في التمييز بين الحالات والحدود التقاربية.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """لا يعني Big O بالضرورة أسوأ حالة، بل هو سقف رياضي أعلى يصف معدل النمو لأي سيناريو تشغيلي. فالخوارزميات تمتلك أفضل حالة ومتوسط حالة وأسوأ حالة، ولكل حالة حد Big O خاص بها. فمثلاً البحث الخطي يمتلك أفضل حالة بـ O(1) وأسوأ حالة بـ O(n). وفي أندرويد، نراعي سقف أسوأ حالة دائماً على خيط الواجهة لمنع سقوط الإطارات.""",
        "best_answer_ar": """يعد الاعتقاد بأن Big O يعبر دائماً عن أسوأ حالة مفهوماً غير دقيق رياضياً؛ فالـ Big O في جوهره أداة رياضية تصف السقف التقاربي الأعلى لنمو الدوال.
في التحليل الخوارزمي، نتعامل مع بعدين منفصلين تماماً؛ الحدود الرياضية وتشمل Big O للسقف الأعلى وBig Omega للحد الأدنى وBig Theta للحد المطابق الحتمي. والبعد المقابل هو سيناريوهات التشغيل التي تصف شكل المدخلات، وتضم أفضل حالة، والحالة المتوسطة، وأسوأ حالة.
ويمكننا تطبيق Big O لحساب السقف الأعلى لأي من هذه الحالات؛ ففي خوارزمية الفرز بالإدراج، تكون أفضل حالة عند إدخال مصفوفة مرتبة بالفعل وسقفها هو O(n)، بينما تكون أسوأ حالة عند إدخال مصفوفة معكوسة وسقفها هو O(n^2).
وفي بيئة أندرويد، يكتسب هذا التمييز أهمية معمارية بالغة؛ فبينما تعكس الحالة المتوسطة الاستهلاك الطبيعي للبطارية والمعالج، يتعين على المهندس مراعاة أسوأ حالة على خيط واجهة المستخدم للتأكد من أن أسوأ سيناريو لن يتسبب في سقوط إطارات الشاشة أو إطلاق تنبيه التطبيق لا يستجيب.""",
        "deep_answer_ar": """من منظور علم الحاسوب النظري وهندسة موثوقية النظم في أندرويد، يمثل الخلط بين ترميز Big O وسيناريو أسوأ حالة قصوراً في النمذجة الرياضية للأداء.
الـ Big O هو دالة سقف رياضي بحت؛ فالقول بأن خوارزمية ما هي O of g of n يعني رياضياً أنها لن تتجاوز مضاعفاً ثابتاً لتلك الدالة عند كبر المدخلات. والحدود الرياضية تعبر عن خصائص المعادلات، بينما سيناريوهات التشغيل تعبر عن طبيعة البيانات الممررة للخوارزمية في الواقع العملي.
وفي خوارزمية مثل QuickSort، تنجح الخوارزمية في تقسيم البيانات بالتساوي في الحالتين الفضلى والمتوسطة، ويكون سقف نموها الرياضي هو O of n log n. أما إذا كانت البيانات مرتبة مسبقاً وتراجع أداء عنصر الارتكاز، تنحدر الخوارزمية لأسوأ سيناريو تشغيلي وسقفه هو O of n squared. وبالتالي فإن O of n squared هو سقف أسوأ حالة، بينما O of n log n هو سقف الحالة المتوسطة.
وفي تطبيقات أندرويد الإنتاجية، يترتب على هذا الفهم قرارات معمارية حاسمة تتعلق بتوزيع المهام بين الخيوط؛ فالاعتماد الساذج على الحالة المتوسطة لخوارزمية ما على خيط الواجهة يعد خطأ خطيراً؛ فإذا استقبل التطبيق مدخلات استثنائية تفجر أسوأ حالة ممكنة للخوارزمية، سيتجمد العرض البصري ويسقط معدل الإطارات فوراً. ولذلك يفرض مهندسو النظم حصر العمليات على خيط الواجهة في الخوارزميات التي تمتلك سقفاً حتمياً آمناً في أسوأ حالاتها، مع ترحيل أي خوارزمية ذات تذبذب حاد إلى خيوط الخلفية عبر Coroutines."""
    }
}

# ==========================================
# DSA-05: Compare arrays, linked lists, stacks, queues, hash maps, and sets.
# ==========================================
DATA["DSA-05"] = {
    "concept_en": """Selecting optimal collection data structures dictates memory locality, algorithmic complexity, and cache ergonomics in Android:
- Array & Dynamic Array (`Array`, `ArrayList`):
  - Memory: Contiguous memory allocation.
  - Access: $O(1)$ random access by index via direct pointer arithmetic.
  - Insertion/Deletion: $O(1)$ amortized at the end; $O(n)$ at arbitrary positions due to element shifting.
  - Cache Ergonomics: Exceptional CPU L1/L2 cache locality; sequential elements are pre-fetched into hardware cache lines.
- Linked List (`LinkedList`):
  - Memory: Doubly-linked nodes scattered across the heap with pointer references.
  - Access: $O(n)$ sequential traversal.
  - Insertion/Deletion: $O(1)$ once a node reference is held; $O(n)$ if traversal is required.
  - Android Reality: `LinkedList` is almost universally an anti-pattern on Android. Each node incurs a 24-to-32-byte object header overhead, inducing memory fragmentation and cache misses. Prefer `ArrayDeque` or `ArrayList`.
- Stacks & Queues (`ArrayDeque`):
  - Memory: Resizable circular array buffer.
  - Operations: $O(1)$ amortized push/pop for stacks (LIFO), and $O(1)$ enqueue/dequeue for queues (FIFO).
  - Android Reality: Far superior to `java.util.Stack` (which carries obsolete synchronized lock overhead) and `LinkedList` queues. Used internally for Activity backstacks, navigation stacks, and background job queues.
- Hash Map (`HashMap`):
  - Memory: Array of buckets containing linked lists or balanced Red-Black trees.
  - Operations: $O(1)$ average get/put; $O(n)$ or $O(\log n)$ worst-case under pathological collisions.
  - Android Memory Considerations: High memory overhead per entry. For small collections ($n < 1,000$), Android provides `ArrayMap` and primitive-specialized `SparseArray` to eliminate node and autoboxing memory waste.
- Set (`HashSet`, `LinkedHashSet`):
  - Memory: Backed by a `HashMap` where values are dummy object references.
  - Operations: $O(1)$ average add, remove, and contains; guarantees element uniqueness.
  - `LinkedHashSet` preserves insertion order using a doubly-linked bucket structure with slight extra memory cost.""",
    "walkthrough_en": """Idiomatic Kotlin collection usage and Android memory-optimized alternatives:
```kotlin
// 1. Array / ArrayList: Optimal for fast indexed reads and sequential UI lists
val userList = ArrayList<String>() // Backed by contiguous array

// 2. ArrayDeque: Optimal stack (LIFO) and queue (FIFO) implementation
val navigationStack = ArrayDeque<String>()
navigationStack.push("HomeScreen")
navigationStack.push("DetailsScreen")
val currentScreen = navigationStack.pop() // O(1) without LinkedList node overhead

// 3. Set: Unique element tracking with O(1) membership checks
val selectedIds = HashSet<String>()
selectedIds.add("item_101")
val isSelected = selectedIds.contains("item_101") // O(1)

// 4. Android SparseArray: Avoids Integer autoboxing and Entry node overhead
// Replaces HashMap<Int, User> with contiguous primitive arrays
import android.util.SparseArray
val userCache = SparseArray<User>()
userCache.put(101, User("Mohamed"))
val user = userCache.get(101) // O(log n) via binary search, but 60% less RAM!
```""",
    "short_en": """Arrays provide O(1) index access with excellent CPU cache locality, while LinkedLists suffer from pointer overhead and cache misses, making them an Android anti-pattern. Stacks and Queues are best implemented via ArrayDeque for O(1) operations without node allocation. HashMaps and Sets deliver O(1) average key lookups at the expense of memory, which Android optimizes using SparseArray and ArrayMap.""",
    "structured_en": """Choosing the appropriate data structure requires balancing access complexity against memory allocation and hardware cache locality.
Arrays and ArrayLists store data contiguously, providing constant-time O(1) random access and superior CPU cache prefetching, though insertions at arbitrary indices require O(n) element shifts. In contrast, LinkedLists scatter nodes across memory; while insertions are O(1) when holding a reference, random access requires O(n) traversal. On Android, LinkedList is generally an anti-pattern due to excessive pointer overhead and poor cache locality.
For LIFO stacks and FIFO queues, ArrayDeque is the gold standard, offering amortized O(1) operations over a circular array buffer without object node overhead.
HashMaps and HashSets provide constant-time O(1) average lookups and additions by hashing keys into buckets. However, because standard HashMaps allocate multiple wrapper objects and Entry nodes, Android platforms provide memory-efficient alternatives like SparseArray and ArrayMap for smaller datasets, avoiding autoboxing and dramatically reducing garbage collection churn.""",
    "deep_senior_en": """From a systems hardware and mobile memory architecture perspective, evaluating collections requires looking beneath asymptotic Big O into physical memory layout, CPU cache hierarchies, and garbage collection pressure.
While classical computer science teaches that LinkedList provides O(1) insertions compared to ArrayList\'s O(n) shifts, in real-world Android runtimes, ArrayList almost always outperforms LinkedList. Modern mobile ARM processors rely heavily on L1 and L2 cache lines. When iterating an ArrayList, contiguous memory addresses are prefetched into cache lines in single hardware cycles. With LinkedList, each node is an independent heap allocation containing sixteen bytes of object header and two eight-byte pointers. Traversing a LinkedList involves chasing memory pointers across a fragmented heap, triggering relentless CPU cache misses and creating thousands of objects that burden the ART garbage collector.
For stack and queue semantics, ArrayDeque is our architectural standard. It avoids the obsolete synchronization locks of legacy Vector-based Stack classes and eliminates the node allocation penalties of LinkedList, implementing circular array wrapping with amortized O(1) bounds.
HashMaps provide unmatched O(1) associative lookups, but their memory tax on mobile is severe. A standard HashMap allocates bucket arrays and Entry nodes, while boxing primitive integers into reference objects. In high-frequency UI scrolling lists, this allocation churn causes frame stutter. Android engineers resolve this by deploying Google\'s specialized collections: SparseArray stores integer keys in a sorted primitive array and values in an Object array, utilizing binary search O of log n lookups while slashing memory consumption by over fifty percent and completely eliminating autoboxing. Selecting the correct structure is thus a hardware-conscious engineering decision.""",
    "meta_ar": {
        "id": "DSA-05",
        "questionAr": "قارن بين المصفوفات (Arrays)، والقوائم المترابطة (Linked Lists)، والـ Stacks، والـ Queues، والـ Hash Maps، والـ Sets.",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "المقارنة المعمارية بين هياكل البيانات، كفاءة الذاكرة وتجاورها (Memory Locality)، كاش المعالج (CPU Cache)، عيوب LinkedList في أندرويد، تفوق ArrayDeque، وبدائل أندرويد الموفرة للذاكرة مثل SparseArray وArrayMap.",
        "concept_ar": "تختلف هياكل البيانات في نمط تخزينها في الذاكرة وكفاءتها الحسابية وتأثيرها على كاش المعالج ومجمع القمامة في أندرويد: المصفوفات (Arrays وArrayList) تخزن البيانات في كتل متصلة في الذاكرة؛ مما يمنحها وصولاً عشوائياً فائق السرعة $O(1)$ عبر الفهرس وتوافقاً مذهلاً مع كاش المعالج (CPU Cache Locality). القوائم المترابطة (LinkedList) تخزن البيانات في عقد متباعدة يربطها مؤشرات؛ ورغم أنها تتيح الإضافة والحذف في $O(1)$ عند امتلاك المؤشر، إلا أنها تعد نمطاً سيئاً (Anti-pattern) في أندرويد بسبب استهلاكها لذاكرة ضخمة لكل عقدة وإحداثها إخفاقات مستمرة في كاش المعالج وإجهادها لمجمع القمامة. الـ Stacks والـ Queues تُنفذ بكفاءة عبر ArrayDeque بمصفوفة دائرية ذات تعقيد $O(1)$ دون إنشاء عقد. جداول التجزئة (HashMap وHashSet) توفر بحثاً وإضافة في $O(1)$ في المتوسط بتكلفة ذاكرة مرتفعة؛ وتوفر منصة أندرويد هياكل متخصصة مثل SparseArray وArrayMap لتقليص استهلاك الذاكرة وإلغاء تغليف الأرقام (Autoboxing).",
        "walkthrough_ar": """استخدام الهياكل القياسية والبدائل الموفرة في أندرويد بلغة كوتلن:
```kotlin
// 1. ArrayList: الخيار الافتراضي للقوائم المتصلة بالقراءة السريعة
val list = ArrayList<String>()

// 2. ArrayDeque: التطبيق الأمثل للمكدس والرتل دون عقد إضافية
val queue = ArrayDeque<String>()
queue.addLast("Job1") // Enqueue
val nextJob = queue.removeFirst() // Dequeue O(1)

// 3. HashSet: لضمان فرادة العناصر والبحث السريع
val uniqueTags = HashSet<String>()
uniqueTags.add("android")

// 4. SparseArray في أندرويد: بديل موفر للذاكرة لـ HashMap<Int, Value>
// يوفر أكثر من 50% من الذاكرة ويلغي تغليف الأرقام البدائية
import android.util.SparseArray
val userMap = SparseArray<String>()
userMap.put(10, "Mohamed") // لا يوجد حجز لكائن Integer
val name = userMap.get(10) // بحث ثنائي O(log n)
```""",
        "why_it_matters_ar": "اختيار هيكل بيانات غير مناسب مثل LinkedList يعطل كاش المعالج ويملأ الذاكرة بكائنات مؤقتة تسبب تقطيعاً بصرياً فادحاً في واجهة المستخدم.",
        "worked_example_ar": "استبدلنا استخدام HashMap<Int, Model> في قائمة تحتوي على 2000 عنصر بهيكل SparseArray؛ فانخفض استهلاك الذاكرة من 120KB إلى 45KB مع إلغاء آلاف عمليات الـ Autoboxing.",
        "trade_offs_ar": "هيكل SparseArray يضحي بسرعة البحث لتصبح O(log n) بدلاً من O(1) في HashMap، ولكنه يوفر نصف مساحة الذاكرة ويلغي عمليات حجز الكائنات تماماً.",
        "failure_modes_ar": "أخطر الأخطاء هو استخدام LinkedList لبناء قوائم RecyclerView متكررة، أو استخدام فئة Stack القديمة في جافا التي تحتوي على أقفال مزامنة متزامنة (Synchronized) تبطئ الخيط.",
        "production_perspective_ar": "في كود أندرويد المتقدم، يُحظر استخدام LinkedList تماماً، وتُستخدم ArrayDeque لكافة عمليات الطابور والمكدس، وتُستبدل الخرائط الصغيرة بـ ArrayMap أو SparseArray.",
        "how_to_answer_ar": "ابدأ بالمصفوفات وميزتها في كاش المعالج، ثم انقد LinkedList واشرح لماذا هي anti-pattern في أندرويد، وقدم ArrayDeque للـ Stacks والـ Queues، واختم بـ HashMap وبدائل SparseArray.",
        "talking_points_ar": "تجاور الذاكرة Contiguous Memory، كاش المعالج L1 Cache، عيوب LinkedList، هيكل ArrayDeque الدائري، تكلفة HashMap، وهياكل أندرويد SparseArray وArrayMap.",
        "follow_ups_ar": "لماذا تعد فئة java.util.Stack عتيقة ومرفوضة معمارياً؟ وكيف يعمل هيكل ArrayMap داخلياً بمصفوفتين بدائيتين؟",
        "self_check_ar": "هل قارنت الهياكل من حيث الوصول والذاكرة، وانتقدت LinkedList في أندرويد، وشرحت مميزات SparseArray وArrayDeque؟",
        "references_ar": f"- [Android Developers: SparseArray documentation](https://developer.android.com/reference/android/util/SparseArray) — الدليل الرسمي لهياكل البيانات المحسنة لذاكرة أجهزة أندرويد.\n- [Oracle Java Docs: ArrayDeque](https://docs.oracle.com/javase/8/docs/api/java/util/ArrayDeque.html) — التوثيق الرسمي لأفضل تطبيق للمكدس والطابور في الجافا وكوتلن.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """توفر المصفوفات وصولاً بـ O(1) وتفوقاً هائلاً في كاش المعالج، بينما تعتبر LinkedList نمطاً سيئاً في أندرويد لتباعد ذاكرتها وإجهادها لمجمع القمامة. وتعد ArrayDeque الخيار الأمثل للمكدس والطابور لعملياتها اللحظية، بينما توفر HashMap وSet بحثاً في O(1) بتكلفة ذاكرة تعالجها أندرويد عبر SparseArray وArrayMap.""",
        "best_answer_ar": """اختيار هيكل البيانات المناسب في أندرويد يتطلب الموازنة بين التعقيد الحسابي وتوزيع الذاكرة وسلوك كاش المعالج.
المصفوفات وArrayList تخزن عناصرها في مساحات متصلة بالذاكرة، مما يوفر وصولاً عشوائياً بالـ O(1) واستغلالاً مثالياً لخطوط كاش المعالج، وإن كانت الإضافة في المنتصف تتطلب إزاحة خطية. وفي المقابل، تشتت LinkedList عناصرها في كائنات مستقلة؛ ورغم أن الإضافة فيها سريعة عند امتلاك المؤشر، إلا أنها تمثل خياراً سيئاً في أندرويد بسبب تكلفتها العالية للذاكرة وتسببها في إخفاقات مستمرة لكاش المعالج.
ولتنفيذ هياكل المكدس والطابور، تبرز فئة ArrayDeque كمعيار هندسي مثالي يعتمد على مصفوفة دائرية ذات تعقيد O(1) دون إهدار الذاكرة في عقد إضافية أو أقفال مزامنة قديمة.
أما جداول التجزئة HashMap وHashSet، فتمنح وصولاً وإضافة في O(1) في المتوسط عبر توزيع المفاتيح في مجموعات. ونظراً لاستهلاكها المرتفع للذاكرة وحجز كائنات العقد، توفر منصة أندرويد بدائل فائقة الكفاءة مثل SparseArray وArrayMap للمجموعات الصغيرة؛ حيث تتخلص من تغليف الأرقام البدائية وتوفر أكثر من نصف مساحة الذاكرة مع الحفاظ على سرعة فائقة.""",
        "deep_answer_ar": """من منظور هندسة النظم وتصميم الذاكرة في معالجات ARM المحمولة، يتطلب تقييم هياكل البيانات النظر إلى ما وراء Big O المجرد للوصول إلى فيزياء العتاد وسلوك مجمع القمامة.
في علم الحاسوب الأكاديمي، يُشار إلى أن LinkedList تتفوق في الإضافة على ArrayList، لكن في واقع تشغيل أندرويد، تتفوق مصفوفات ArrayList باكتساح. فالمعالجات تعتمد على كاش L1 وL2 فائق السرعة؛ وعند قراءة مصفوفة متصلة، يسحب المعالج العناصر المتجاورة في دورة عتادية واحدة. أما في LinkedList، فكل عنصر يمثل كائناً مستقلاً على الـ Heap يحمل ستة عشر بايت لرأس الكائن ومؤشرات إضافية؛ مما يحول المرور عليها إلى مطاردة عشوائية للمؤشرات تفجر إخفاقات كاش المعالج وتولد آلاف الكائنات التي ترهق محرك ART.
ولبناء مكدسات التنقل وقوائم الانتظار، نعتمد حصراً على ArrayDeque التي تدير مصفوفة دائرية مرنة بحدود زمنية O(1) حتمية دون حجز عقد جديدة، متفوقة على فئة Stack القديمة المحملة بأقفال تزامن غير ضرورية.
وعلى صعيد الخرائط وجداول التجزئة، تمنحنا HashMap وصولاً فورياً، لكن ضريبتها على الذاكرة باهظة في أجهزة الهواتف؛ فهي تحجز مصفوفات حاويات وعقد ربط وتغلف الأرقام البدائية في كائنات مرجعية. ولمنع استنزاف الذاكرة في القوائم الضخمة، توظف منصة أندرويد هياكل مبتكرة مثل SparseArray؛ حيث تخزن المفاتيح في مصفوفة أرقام بدائية متصلة والقيم في مصفوفة كائنات، وتعتمد على البحث الثنائي O of log n للوصول. هذا التصميم يقلص الذاكرة بأكثر من خمسين بالمئة ويمنع الـ Autoboxing تماماً، مما يقلل وقفات مجمع القمامة ويضمن انسيابية مطلقة في الشاشات."""
    }
}

# ==========================================
# DSA-06: What are average and worst-case HashMap lookup complexities?
# ==========================================
DATA["DSA-06"] = {
    "concept_en": """The lookup complexity of a HashMap depends on the distribution uniformity of its hashing function and collision resolution mechanisms:
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
  - When total entries exceed the threshold (`capacity * loadFactor`, typically $0.75$), HashMap allocates a new array of double the size ($2 \times$) and rehashes all elements in an $O(n)$ operation.
  - Android Best Practice: Pre-sizing HashMaps (`HashMap(expectedCount / 0.75f + 1)`) prevents expensive runtime rehashing cycles during JSON parsing or data synchronization.""",
    "walkthrough_en": """Demonstrating pathological hash degradation and pre-sized initialization:
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
```""",
    "short_en": """HashMap lookup executes in O(1) average time when hash distributions are uniform. In worst-case pathological collision scenarios, complexity degrades to O(n) in legacy lists, or O(log n) in modern ART/Java 8+ via Red-Black tree conversion. Senior engineers write robust hashCode implementations and pre-size maps to prevent expensive O(n) runtime rehashing cycles.""",
    "structured_en": """The lookup complexity of a HashMap hinges on hash distribution uniformity and bucket collision management.
In the average case, HashMap delivers constant-time O(1) performance. The key hash code is masked against the bucket array length to identify the index, retrieving the value in a single step without collision traversal.
In the worst case, where multiple keys hash to the same bucket index, performance degrades. In older runtimes, buckets maintained simple linked lists, resulting in O(n) linear search degradation. Modern Android runtimes inherit Java 8 treeification: when a bucket accumulates more than eight colliding nodes and the map capacity reaches sixty-four, the linked list converts into a balanced Red-Black tree, improving worst-case search complexity to O(log n).
Additionally, HashMaps undergo an O(n) rehashing cycle whenever entries exceed the seventy-five percent load factor. In Android production apps, pre-allocating HashMap capacity based on expected item counts eliminates runtime array resizing and reduces garbage collection churn.""",
    "deep_senior_en": """From an algorithmic internals and systems security perspective, HashMap lookup mechanics reveal the critical interplay between software contracts and hardware efficiency.
Under optimal conditions, HashMap achieves theoretical O(1) lookups via deterministic memory offset calculation. However, achieving this requires obeying the hash distribution contract. The 32-bit integer returned by hashCode() is mixed using an internal bit-spread function to disperse high bits, followed by power-of-two masking. If two distinct keys produce identical bucket indices, a collision occurs.
Historically, hash collisions resolved strictly via singly-linked Node chaining, leaving systems vulnerable to O(n) degradation and algorithmic complexity attacks (HashDoS), where adversaries submit crafted inputs to freeze servers or mobile parsing pipelines. To neutralize this, modern Android ART runtimes adopt Java 8 treeification. When a bucket\'s collision depth reaches eight entries, the runtime inspects whether the total map capacity is at least sixty-four. If so, it transforms the linked list into a self-balancing Red-Black TreeNode structure, bounding worst-case traversal to O of log n.
Beyond collision dynamics, mobile engineers must manage the hidden tax of capacity expansion. When the number of entries exceeds the threshold of capacity multiplied by the 0.75 load factor, the map allocates a new array of double the size, re-indexes every entry, and discards the old array. In a mobile environment processing thousands of network records, these repeated O(n) rehashing events spike memory allocation and trigger garbage collection pauses. Pre-sizing collections by calculating the exact expected capacity completely circumvents rehashing, ensuring deterministic O(1) latency across all lifecycle passes.""",
    "meta_ar": {
        "id": "DSA-06",
        "questionAr": "ما هو التعقيد الزمني للبحث في الـ HashMap في الحالة المتوسطة (Average) وأسوأ حالة (Worst Case)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "التحليل الداخلي لـ HashMap، الحالة المتوسطة O(1)، أسوأ حالة O(n) وتحولها لـ O(log n) عبر Red-Black Trees (Treeification)، أسباب تصادم الهاش، وتكلفة إعادة التوزيع (Rehashing).",
        "concept_ar": "يعتمد التعقيد الزمني لعملية البحث في HashMap على مدى كفاءة دالة التجزئة (Hash Function) وتوزيع المفاتيح داخل مصفوفة الحاويات (Buckets): في الحالة المتوسطة (Average Case)، يكون التعقيد $O(1)$ ثابتاً؛ حيث توزع دالة الهاش المفاتيح بانتظام، ويُحسب الفهرس بعملية إخفاء بتات سريعة للوصول للعنصر مباشرة. أما في أسوأ حالة (Worst Case)، فتحدث عند تصادم كافة المفاتيح في نفس الحاوية (Bucket Collision)؛ وفي بيئات جافا وأندرويد القديمة، كان التعقيد ينحدر إلى $O(n)$ خطياً لتحول الحاوية لقائمة مترابطة. أما في بيئات أندرويد الحديثة (ART المتوافقة مع Java 8+)، فعندما يتجاوز عدد التصادمات في الحاوية الواحدة 8 عناصر وتتعدى السعة الكلية 64، تتحول القائمة تلقائياً إلى شجرة بحث متوازنة (Red-Black Tree)، فيتحسن تعقيد أسوأ حالة ليصبح $O(\log n)$. كما تتضمن HashMap تكلفة إعادة التوزيع (Rehashing) بتعقيد $O(n)$ عند امتلاء 75% من سعتها؛ ولذلك يُنصح بتحديد السعة الابتدائية مسبقاً في أندرويد لتفادي التوزيع المتكرر.",
        "walkthrough_ar": """توضيح انحدار الأداء بسبب دالة الهاش السيئة والتهيئة المسبقة للسعة:
```kotlin
// دالة هاش فاسدة تسبب تصادم كافة العناصر في حاوية واحدة
data class BadKey(val id: String) {
    override fun hashCode(): Int = 1 // تجبر HashMap على استخدام حاوية واحدة دائماً!
    override fun equals(other: Any?): Boolean = other is BadKey && other.id == this.id
}

fun testHashMapPerformance() {
    val totalItems = 5000
    
    // الممارسة القياسية: تحديد السعة الابتدائية مسبقاً لتفادي إعادة التوزيع O(n)
    // السعة = (العدد المطلوب / 0.75) + 1
    val initialCapacity = (totalItems / 0.75f).toInt() + 1
    val map = HashMap<String, String>(initialCapacity)

    for (i in 0 until totalItems) {
        map["key_$i"] = "data_$i" // لا تحدث أي عمليات إعادة بناء للمصفوفة
    }

    // بحث الحالة المتوسطة O(1)
    val value = map["key_2500"]
}
```""",
        "why_it_matters_ar": "كتابة دالة hashCode سيئة يحول جداول التجزئة السريعة إلى قوائم خطية بطيئة تجمد واجهة أندرويد، وعدم تحديد السعة الابتدائية يهدر الذاكرة والوقت.",
        "worked_example_ar": "في تطبيق يقرأ 10,000 عنصر من استجابة JSON، حددنا السعة الابتدائية للـ HashMap بـ 13,334؛ مما ألغى 14 عملية إعادة توزيع متتالية وسرع استيراد البيانات بمقدار الضعف.",
        "trade_offs_ar": "تحويل الحاويات لأشجار Red-Black Tree يضمن تعقيد O(log n) في أسوأ الحالات ولكنه يزيد استهلاك الذاكرة لكل عقدة شجرية؛ وتحديد سعة كبيرة مقدماً يستهلك ذاكرة أكبر لحساب السرعة.",
        "failure_modes_ar": "أخطر الأخطاء هو كتابة كلاس مخصص واستبدال equals دون استبدال hashCode، أو جعل دالة الهاش ترجع قيمة ثابتة مما يدمر أداء الـ HashMap بالكامل.",
        "production_perspective_ar": "في كود الإنتاج، تُعتمد Data Classes في كوتلن لتوليد equals وhashCode تلقائياً وفق معايير مثالية تضمن توزيع الهاش بانتظام وتمنع التصادمات العرضية.",
        "how_to_answer_ar": "ابدأ ببيان الحالة المتوسطة O(1)، ثم فسر أسوأ حالة والفرق بين الأنظمة القديمة O(n) والحديثة O(log n) عبر الـ Treeification، واشرح أسباب التصادم وأهمية تحديد السعة مسبقاً.",
        "talking_points_ar": "الحالة المتوسطة O(1)، أسوأ حالة O(n) وO(log n)، ميزة Treeification وشجرة Red-Black Tree، عتبة التحول 8 عناصر، دورة Rehashing بـ O(n)، وأهمية التهيئة المسبقة للسعة.",
        "follow_ups_ar": "لماذا تشترط HashMap أن تكون سعة المصفوفة من مضاعفات الرقم 2 دائماً؟ وما هو هجوم الـ HashDoS وكيف يعالجه أندرويد؟",
        "self_check_ar": "هل ميزت بين الحالة المتوسطة وأسوأ حالة، وشرحت التحول لشجرة Red-Black Tree وتكلفة الـ Rehashing؟",
        "references_ar": f"- [OpenJDK: HashMap source code and Treeification](https://github.com/openjdk/jdk/blob/master/src/java.base/share/classes/java/util/HashMap.java) — الشفرة المصدرية الرسمية لـ HashMap وتوثيق خوارزمية التحول للشجرة.\n- [Android Developers: Optimize memory and collection sizing](https://developer.android.com/topic/performance/reduce-apk-size) — إرشادات رسمية لحجم المجموعات وتقليص استهلاك الذاكرة في أندرويد.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """يبلغ تعقيد البحث في HashMap في الحالة المتوسطة O(1) عند التوزيع المنتظم للمفاتيح. وفي أسوأ حالة تصادم تنحدر الكفاءة إلى O(n) في الأنظمة القديمة، بينما تتحسن إلى O(log n) في أندرويد الحديث بفضل تحويل الحاوية إلى شجرة Red-Black متوازنة عند تجاوز 8 تصادمات. كما يجب تحديد السعة مسبقاً لتفادي إعادة التوزيع المكلفة بـ O(n).""",
        "best_answer_ar": """يعتمد التعقيد الزمني لعملية البحث في HashMap على دقة توزيع الهاش وآلية التعامل مع التصادمات في الحاويات.
في الحالة المتوسطة المعتادة، تنجز HashMap البحث في تعقيد ثابت O(1)؛ حيث يتم حساب كود الهاش وتطبيقه على سعة المصفوفة للوصول المباشر للحاوية واسترجاع العنصر في خطوة واحدة.
أما في أسوأ حالة ناتجة عن تصادم مفاتيح متعددة في نفس الحاوية، فيتأثر الأداء بنسخة بيئة التشغيل؛ ففي الأنظمة القديمة كانت الحاويات تتراجع إلى قوائم مترابطة ذات تعقيد خطي O(n). ولكن في بيئات أندرويد الحديثة المعتمدة على جافا 8، تتدخل ميزة الشجرة المتوازنة؛ فعندما يتجاوز عدد التصادمات داخل حاوية واحدة ثمانية عناصر وتتخطى سعة الجدول أربعة وستين، تتحول الحاوية تلقائياً إلى شجرة Red-Black Tree متوازنة تضمن سقف بحث لا يتجاوز O(log n).
وبالإضافة إلى ذلك، تواجه الخريطة تكلفة إعادة توزيع خطية O(n) كلما تجاوزت نسبة الملء خمسة وسبعين بالمئة؛ ولذلك نحرص في تطبيقات أندرويد على تحديد السعة الابتدائية مسبقاً لمنع إعادة تجميع المصفوفة وتوفير موارد المعالج والذاكرة.""",
        "deep_answer_ar": """من منظور الآليات الداخلية لجداول التجزئة وهندسة الأمان في أنظمة أندرويد، يعكس سلوك البحث في HashMap الترابط الوثيق بين العقود البرمجية واستقرار النظم.
في الظروف القياسية، تحقق الخريطة تعقيداً ثابتاً O(1) عبر حسابات رياضية حتمية؛ حيث يتم خلط بتات كود الهاش وإسقاطها على سعة مصفوفة تكون دائماً من قوى الرقم اثنين. وعندما تعمل دالة الهاش بكفاءة، تتوزع المفاتيح بانتظام ولا تتكدس.
ولكن في سيناريوهات التصادم الحاد الناتجة عن دوال هاش معيبة أو هجمات تعقيد متعمدة تهدف لشل النظام، كانت الأنظمة القديمة تضع كافة العناصر المصطدمة في قائمة متصلة واحدة، مما يحول البحث إلى مسح خطي O(n) يجمد واجهة المستخدم. ولمعالجة هذه الثغرة، تبنت بيئة تشغيل ART الحديثة معمارية تحويل الحاويات؛ فعندما يصل عمق التصادم إلى ثمانية عناصر مع وصول سعة الخريطة إلى أربعة وستين، يُعاد هيكلة الحاوية من عقد ربط بسيطة إلى شجرة Red-Black Tree متوازنة تضمن انحصار البحث في O of log n حتى في أشد حالات التصادم سوءاً.
وفضلاً عن ذلك، يجب على مهندس أندرويد الانتباه إلى ضريبة التوسع الديناميكي؛ فعندما تتجاوز العناصر حد عامل التحميل البالغ صفر فاصل خمسة وسبعين، تنشئ الخريطة مصفوفة جديدة بضعف الحجم وتعيد حساب مواضع كافة العناصر بتكلفة خطية O(n). وتكرار هذه العملية أثناء جلب آلاف السجلات من الشبكة يسبب وقفات ملحوظة في مجمع القمامة؛ ولذلك فإن تهيئة الخريطة مسبقاً بالسعة المتوقعة مقسومة على عامل التحميل يلغي دورات التوسع العشوائية ويحافظ على استجابة فورية ومستقرة."""
    }
}

# ==========================================
# DSA-07: What is binary search, and what precondition does it require?
# ==========================================
DATA["DSA-07"] = {
    "concept_en": """Binary search is an optimal divide-and-conquer search algorithm that executes in logarithmic time by repeatedly partitioning the search space:
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
  - `Collections.binarySearch()` returns the non-negative index if the key is found. If missing, it returns `(-insertion_point - 1)`, providing callers the exact index where the element should be inserted to maintain sorted order.""",
    "walkthrough_en": """Safe Kotlin implementation of binary search and standard library integration:
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
```""",
    "short_en": """Binary search is a divide-and-conquer algorithm operating in O(log n) time by halving the search space each step. Its mandatory preconditions are that the collection must be pre-sorted and support O(1) random access by index. Midpoints must be computed safely using unsigned bit shifts to prevent integer overflow, and boundary updates must advance past mid to avoid infinite loops.""",
    "structured_en": """Binary search is an exceptionally efficient search algorithm designed to find elements in logarithmic time.
The algorithm operates on the divide-and-conquer principle, comparing the search target against the middle element of a candidate range and discarding half the remaining elements in each pass. This delivers an O(log n) time complexity, requiring only twenty comparisons to locate a record among one million items.
However, binary search imposes two mandatory preconditions. First, the collection must be sorted according to the comparison key. Second, the underlying data structure must support constant-time O(1) random access, such as an Array or ArrayList. Running binary search over a LinkedList fails to achieve logarithmic performance because finding the middle node requires an O(n) sequential traversal.
A classic pitfall is computing the midpoint as low plus high divided by two, which overflows thirty-two-bit integers for large datasets. Safe implementations compute mid using an unsigned right bit shift, advancing boundaries strictly past the midpoint to prevent infinite loops.""",
    "deep_senior_en": """From an algorithmic verification and low-level runtime perspective, binary search exemplifies how mathematical elegance collides with physical hardware limits.
The theoretical foundation of binary search relies on monotonicity. By inspecting the midpoint element, the algorithm eliminates half of the search interval in every comparison step. For a list of one million elements, binary search terminates in at most twenty steps, compared to one million steps for a linear scan.
However, achieving this O of log n guarantee requires strict adherence to architectural preconditions. The most overlooked requirement is constant-time indexing. On a contiguous array or ArrayList, accessing list of mid is an instantaneous O of one memory read. If an engineer naively invokes binary search on a LinkedList, traversing to the middle node requires pointer chasing that takes O of n time at every recursive step, degrading the algorithm into a clumsy O of n log n process that runs slower than a simple linear scan.
Furthermore, writing a bug-free binary search is notoriously difficult due to edge-case mechanics. For decades, standard implementations contained an integer overflow bug: computing low plus high divided by two overflows signed thirty-two-bit integer limits when array sizes exceed one billion, producing negative indices that crash the process. The correct implementation calculates mid as low plus high minus low divided by two, or utilizes the unsigned right shift operator ushr one.
Finally, Kotlin standard library integration provides powerful semantic guarantees. When binarySearch fails to find an item, it returns negative insertion point minus one. In an Android UI displaying sorted chat messages or transaction ledgers, this return value allows developers to insert new entries at their exact sorted position in O of n time without triggering an expensive full-collection re-sort.""",
    "meta_ar": {
        "id": "DSA-07",
        "questionAr": "ما هو البحث الثنائي (Binary Search)، وما هي شروطه المسبقة الحتمية لتطبيقه؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم خوارزمية البحث الثنائي وكفاءتها اللوغاريتمية O(log n)، الشروط المسبقة الحتمية (الترتيب والوصول العشوائي O(1))، خطأ تجاوز سعة الأرقام (Integer Overflow Bug)، وسلوك دالة binarySearch في كوتلن.",
        "concept_ar": "تعد خوارزمية البحث الثنائي (Binary Search) من أهم خوارزميات فرق تسد (Divide-and-Conquer)؛ حيث تبحث عن عنصر في مصفوفة بتعقيد لوغاريتمي $O(\log n)$ عبر تقليص نطاق البحث إلى النصف في كل خطوة مقارنة مع العنصر الأوسط (Midpoint). وتشترط الخوارزمية شرطين مسبقين حتميين: أولاً، أن تكون البيانات مرتبة تصاعدياً أو تنازلياً وفق مفتاح المقارنة. ثانياً، أن يدعم هيكل البيانات الوصول العشوائي اللحظي $O(1)$ عبر الفهرس (مثل Array وArrayList)؛ فإذا طُبقت على LinkedList، سينحدر الأداء إلى $O(n)$ لأن الوصول للمنتصف يتطلب مشياً تسلسلياً عبر المؤشرات. وتتطلب البرمجة الدقيقة تجنب فخ تجاوز سعة الأرقام الصحيحة عند حساب المنتصف باستخدام الإزاحة الثنائية غير الموقعة `(low + high) ushr 1`، وتحديث الحدود بـ `mid + 1` و`mid - 1` لتفادي الحلقات اللانهائية. وتوفر كوتلن دالة binarySearch التي ترجع موضع الإدراج المعكوس في حال عدم وجود العنصر.",
        "walkthrough_ar": """تطبيق آمن للبحث الثنائي يمنع تجاوز سعة الأرقام في كوتلن:
```kotlin
// تطبيق آمن للبحث الثنائي يتفادى خطأ Integer Overflow
fun binarySearchInt(arr: IntArray, target: Int): Int {
    var low = 0
    var high = arr.size - 1

    while (low <= high) {
        // استخدام الإزاحة الثنائية ushr يمنع تجاوز سعة Int.MAX_VALUE
        val mid = (low + high) ushr 1
        val midVal = arr[mid]

        when {
            midVal < target -> low = mid + 1
            midVal > target -> high = mid - 1
            else -> return mid // تم العثور على العنصر
        }
    }
    // لم يتم العثور على العنصر؛ إرجاع موضع الإدراج المحتمل
    return -(low + 1)
}

// استخدام دالة كوتلن الرسمية لإدراج عنصر جديد في مكانه المرتب
fun insertSorted(list: MutableList<Int>, value: Int) {
    val index = list.binarySearch(value)
    val insertionPoint = if (index >= 0) index else -index - 1
    list.add(insertionPoint, value) // إدراج مباشر في الموضع الصحيح
}
```""",
        "why_it_matters_ar": "البحث الثنائي يقلص خطوات البحث في مليون عنصر من مليون خطوة إلى 20 خطوة فقط، واستخدامه على بيانات غير مرتبة أو LinkedList يعطي نتائج كارثية.",
        "worked_example_ar": "في قائمة تضم 50,000 معرف مستخدم مرتبة، استبدلنا indexOf بالبحث الثنائي binarySearch؛ فانخفض وقت البحث من 8ms إلى أقل من 0.01ms، مما منع أي جلبة في الـ UI.",
        "trade_offs_ar": "البحث الثنائي فائق السرعة O(log n) ولكنه يشترط تكلفة فرز مسبقة O(n log n)؛ فإذا كانت البيانات تبحث لمرة واحدة فقط، فإن البحث الخطي المباشر O(n) يكون أسرع وأوفر.",
        "failure_modes_ar": "أخطر الأخطاء هو تطبيق البحث الثنائي على LinkedList، أو حساب المنتصف بـ (low + high) / 2 مما يسبب تجاوز سعة الأرقام في المصفوفات الضخمة وتوقف التطبيق فجأة.",
        "production_perspective_ar": "في تطبيقات أندرويد الحقيقية، يُستفاد من القيمة السالبة الناتجة عن binarySearch لإدراج العناصر الجديدة في مكانها المرتب فورياً دون الحاجة لإعادة فرز القائمة بالكامل.",
        "how_to_answer_ar": "عرف الخوارزمية وكفاءتها O(log n)، ثم اذكر الشرطين الحتميين (الترتيب والوصول العشوائي O(1))، وحذر من خطأ Integer Overflow، واشرح ميزة دالة كوتلن في إرجاع موضع الإدراج.",
        "talking_points_ar": "تقليص النطاق للنصف، تعقيد O(log n)، شرط الترتيب Monotonicity، شرط الوصول العشوائي O(1)، خطأ تجاوز السعة Integer Overflow، والإزاحة الثنائية ushr.",
        "follow_ups_ar": "ماذا يحدث بالضبط إذا طبقت البحث الثنائي على LinkedList؟ وكيف تستفيد من مصفوفة الإدخال السالبة في كوتلن لتحديث واجهة المستخدم؟",
        "self_check_ar": "هل ذكرت شرطي الترتيب والوصول العشوائي O(1)، وشرحت تفادي خطأ تجاوز السعة وميزة كوتلن في موضع الإدراج؟",
        "references_ar": f"- [Joshua Bloch: Extra, Extra - Read All About It: Nearly All Binary Searches and Mergesorts are Broken](https://ai.googleblog.com/2006/06/extra-extra-read-all-about-it-nearly.html) — مقال جوجل الكلاسيكي الشهير حول خطأ تجاوز السعة في البحث الثنائي.\n- [Kotlin Standard Library: binarySearch documentation](https://kotlinlang.org/api/latest/jvm/stdlib/kotlin.collections/binary-search.html) — التوثيق الرسمي لدالة البحث الثنائي في كوتلن.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """البحث الثنائي خوارزمية ذكية تقسم نطاق البحث للنصف في كل خطوة بتعقيد لوغاريتمي O(log n). وتشترط حتماً أن تكون البيانات مرتبة مسبقاً، وأن يدعم الهيكل الوصول العشوائي المباشر O(1) كالمصفوفات. ويجب حساب المنتصف بأمان عبر الإزاحة الثنائية لتجنب تجاوز سعة الأرقام الصحيحة وتفادي الحلقات اللانهائية بتحديث الحدود بدقة.""",
        "best_answer_ar": """يعد البحث الثنائي خوارزمية بحث قياسية تعمل بمبدأ فرق تسد لتقليص مساحة البحث إلى النصف في كل مقارنة بتعقيد لوغاريتمي فائق السرعة O(log n).
ومع ذلك، يفرض البحث الثنائي شرطين مسبقين حتميين لا يمكن التنازل عنهما؛ الأول هو أن تكون عناصر المجموعة مرتبة مسبقاً بشكل متصاعد أو تنازلي وفق مفتاح البحث. والشرط الثاني هو أن يدعم هيكل البيانات الوصول العشوائي المباشر في تعقيد ثابت O(1) مثل مصفوفات Array وArrayList؛ فإذا طُبق البحث الثنائي على LinkedList، سيفقد كفاءته اللوغاريتمية لأن الوصول للعنصر الأوسط سيتطلب مشياً تسلسلياً يستغرق وقتاً خطياً.
ومن الناحية البرمجية، يقع الكثير من المطورين في فخ تجاوز سعة الأرقام الصحيحة عند جمع المؤشر الأدنى والأعلى؛ ولذلك يُحسب المنتصف بأمان باستخدام الإزاحة الثنائية ushr، مع تحريك الحدود متجاوزة نقطة المنتصف لمنع الحلقات المفرغة.
وتتميز كوتلن بدعم مدمج لهذه الخوارزمية؛ حيث تعيد دالة binarySearch موضع الإدراج المتوقع كقيمة سالبة في حال غياب العنصر، مما يتيح إدراجه فوراً في مكانه المرتب دون إعادة فرز القائمة.""",
        "deep_answer_ar": """من منظور التحقق الخوارزمي وهندسة النظم الدقيقة في أندرويد، يجسد البحث الثنائي التحدي المستمر بين البساطة الرياضية النظرية والقيود الفيزيائية للعتاد.
تعتمد الفلسفة الرياضية للبحث الثنائي على رتابة البيانات؛ فبمقارنة القيمة المستهدفة مع منتصف النطاق، نستبعد نصف الاحتمالات في كل خطوة؛ مما يعني أن البحث في قائمة تضم مليون عنصر ينتهي في عشرين خطوة كحد أقصى مقارنة بمليون عملية في البحث الخطي.
ولكن هذا الأداء اللوغاريتمي O of log n مشروط بطبيعة الهيكل التخزيني؛ ففي المصفوفات المتصلة، يمثل الوصول للمنتصف قراءة فورية في الذاكرة. أما في القوائم المترابطة LinkedList، فإن الوصول للمنتصف يتطلب تتبع المؤشرات خطوة بخطوة بتكلفة O of n، مما يحول الخوارزمية إلى عملية أبطأ من البحث الخطي العادي.
وفضلاً عن ذلك، ارتبط البحث الثنائي بأحد أشهر الأخطاء البرمجية في تاريخ لغة جافا، والمتمثل في تجاوز سعة الأرقام الصحيحة؛ فحساب المنتصف بالجمع المباشر يفيض ليصبح سالباً في المصفوفات الكبيرة ويفجر خطأ كسر حدود المصفوفة. والحل الهندسي المعتمد هو استخدام الإزاحة الثنائية غير الموقعة ushr التي تمنع الفيضان تماماً.
وأخيراً، توفر كوتلن ميزة معمارية بالغة الذكاء في مكتبتها القياسية؛ فعند عدم العثور على العنصر، تعيد دالة البحث الثنائي قيمة موضع الإدراج المحتمل. وفي شاشات أندرويد مثل سجلات المعاملات المالية المرتبة، يتيح هذا السلوك للمهندس إدراج السجل الجديد في موضعه الصحيح بتكلفة إزاحة خطية بسيطة بدلاً من تشغيل خوارزمية فرز كاملة تستهلك المعالج وتجمد واجهة المستخدم."""
    }
}

# ==========================================
# DSA-08: How would you detect duplicates efficiently in a large list?
# ==========================================
DATA["DSA-08"] = {
    "concept_en": """Efficient duplicate detection in large datasets requires balancing time complexity, memory allocation budgets, and collection mutability:
- Architectural Evaluation of Duplicate Detection Strategies:
  1. Naive Nested Loops (Brute Force):
     - Compares every element against every subsequent element.
     - Complexity: $O(n^2)$ Time, $O(1)$ Space.
     - Android Reality: Catastrophic anti-pattern. For a list of 50,000 items, it performs $1.25 \times 10^9$ comparisons, freezing the main thread for several seconds and triggering an ANR dialog.
  2. Hash-Based Detection (HashSet / LinkedHashSet):
     - Inserts elements into a `HashSet` while checking return values: `set.add(item)` returns `false` if the element is already present.
     - Complexity: $O(n)$ Average Time, $O(n)$ Auxiliary Space.
     - Android Reality: The industry-standard approach for general business objects. Fast single-pass execution, but allocates `Node` wrapper objects and bucket arrays on the heap.
  3. Sort and Scan (In-Place / Monotonic):
     - Sorts the collection in $O(n \log n)$ time, then performs an $O(n)$ linear scan comparing adjacent pairs (`list[i] == list[i+1]`).
     - Complexity: $O(n \log n)$ Time, $O(1)$ to $O(n)$ Space (depending on primitive in-place array sorting).
     - Android Reality: Preferred when memory is severely constrained, avoiding thousands of object allocations on low-end devices if modifying the original list order is acceptable.
  4. BitSet Optimization (Primitive Dense Ranges):
     - If elements are non-negative integer IDs within a bounded range ($0 \le \text{id} \le N$), a `java.util.BitSet` tracks existence using single bits.
     - Complexity: $O(n)$ Time, $O(N / 8)$ Bytes Space. Slashing memory consumption by over $95\%$ compared to a `HashSet<Int>` by eliminating object boxing completely.""",
    "walkthrough_en": """Kotlin implementations comparing Hash-based, Sort-based, and BitSet duplicate detection:
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
```""",
    "short_en": """Detect duplicates efficiently in O(n) time using a HashSet, which flags duplicates in a single pass when add() returns false. If heap memory is constrained, sorting the list in O(n log n) and scanning adjacent items avoids object allocations. For bounded integer IDs, a BitSet provides linear time detection while reducing memory footprint by over 95% compared to object sets.""",
    "structured_en": """Selecting an optimal duplicate detection strategy depends on data size, available heap memory, and item types.
For general business objects, the industry standard is using a HashSet. By iterating through the collection in a single pass, we inspect the boolean result of set.add(item). If it returns false, a duplicate is instantly detected, achieving linear O(n) time complexity at the cost of O(n) auxiliary memory.
When heap memory is severely constrained on low-end Android devices, allocating thousands of HashSet nodes can trigger garbage collection pauses. An effective alternative is in-place sorting, executing in O(n log n) time followed by a linear scan checking adjacent elements, which eliminates auxiliary node allocations.
For datasets consisting of bounded integer IDs, such as user or product identifiers, utilizing a BitSet provides the ultimate mobile optimization. It achieves O(n) linear detection while storing each identifier as a single bit rather than a boxed thirty-two-byte object, slashing memory consumption by ninety-five percent.""",
    "deep_senior_en": """From an algorithmic efficiency and mobile memory optimization standpoint, duplicate detection in large Android datasets requires evaluating the operational constraints of the runtime environment.
A naive double loop comparing all pairs represents an unacceptable O of n squared failure mode that freezes the main thread and risks ANR terminations for datasets exceeding a few thousand items. The standard production solution is single-pass hash filtering. By iterating through the collection, we leverage the O of one average insertion time of HashSet. The set.add() method returns a boolean indicating whether the element was already present, allowing us to identify duplicates in pure O of n linear time.
However, in memory-sensitive Android environments, a HashSet of fifty thousand objects carries substantial hidden overhead. Each entry requires an internal Node object, integer boxing if handling primitive IDs, and a hash bucket array, consuming several megabytes of heap space and triggering ART garbage collection churn.
To address memory constraints, senior engineers deploy domain-specific optimizations. If sorting the input data is permissible, we utilize in-place sorting. Sorting primitive arrays runs in O of n log n time with zero auxiliary heap allocation, followed by a linear scan comparing adjacent indices.
Furthermore, if the data consists of dense positive integer identifiers, such as catalog SKU numbers, we deploy java.util.BitSet. A BitSet represents existence using individual bits in a long array. Checking fifty thousand identifiers consumes less than seven kilobytes of memory, compared to over one megabyte for a HashSet of boxed Integers. This eliminates object allocations, prevents garbage collection stutter, and maintains optimal 120fps scrolling smoothness.""",
    "meta_ar": {
        "id": "DSA-08",
        "questionAr": "كيف تكتشف العناصر المكررة (Duplicates) بكفاءة عالية في قائمة ضخمة في أندرويد؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "استراتيجيات كشف التكرار، مقارنة كفاءة HashSet الزمنية O(n) مع استهلاك الذاكرة، بديل الفرز والمقارنة O(n log n) لتوفير الذاكرة، واستخدام BitSet للأرقام البدائية لتقليص استهلاك الـ Heap.",
        "concept_ar": "يتطلب كشف التكرار في القوائم الضخمة موازنة هندسية بين السرعة الزمنية واستهلاك ذاكرة الـ Heap في هواتف أندرويد: النهج القياسي الأكثر شيوعاً هو استخدام جدول التجزئة (HashSet)؛ حيث نمر على القائمة بمرور واحد خطي $O(n)$ ونستفيد من أن دالة `set.add(item)` ترجع `false` إذا كان العنصر موجوداً مسبقاً، مما يكشف التكرار في $O(n)$ زمناً بتكلفة $O(n)$ ذاكرة. ولكن في الهواتف الاقتصادية ذات الذاكرة المحدودة، يؤدي حجز آلاف كائنات العقد في HashSet إلى إجهاد مجمع القمامة (GC Churn)؛ ولتوفير الذاكرة، نلجأ لخيار الفرز الموضعي (In-Place Sorting) بتعقيد $O(n \log n)$ ثم فحص العناصر المتجاورة في مرور خطي دون حجز ذاكرة إضافية. وإذا كانت البيانات عبارة عن معرفات رقمية موجبة (IDs)، فإن استخدام `BitSet` يمثل الحل المعماري الأقوى في أندرويد؛ حيث يمثل كل رقم ببت واحد (Bit) فقط في الذاكرة بدلاً من حجز كائن كامل، مما يقلص استهلاك الذاكرة بأكثر من 95% ويحقق سرعة خطية $O(n)$ تامة.",
        "walkthrough_ar": """تطبيقات كوتلن لكشف التكرار عبر HashSet والفرز وهيكل BitSet الموفر:
```kotlin
// النهج 1: السرعة القصوى O(n) باستخدام HashSet (الأنسب لكافة الكائنات)
fun <T> hasDuplicatesFast(list: List<T>): Boolean {
    val seen = HashSet<T>(list.size)
    for (item in list) {
        if (!seen.add(item)) return true // تكرار فوري
    }
    return false
}

// النهج 2: توفير الذاكرة O(n log n) عبر الفرز وفحص العناصر المتجاورة
fun hasDuplicatesLowMemory(arr: IntArray): Boolean {
    arr.sort() // فرز موضعي بدون حجز ذاكرة جديدة
    for (i in 0 until arr.size - 1) {
        if (arr[i] == arr[i + 1]) return true
    }
    return false
}

// النهج 3: استهلاك ذاكرة بالحد الأدنى للأرقام باستخدام BitSet
import java.util.BitSet
fun hasDuplicateIds(ids: List<Int>, maxId: Int): Boolean {
    val bits = BitSet(maxId + 1)
    for (id in ids) {
        if (bits.get(id)) return true
        bits.set(id)
    }
    return false // يستهلك 1 بت لكل رقم بدلاً من 24 بايت لكل كائن!
}
```""",
        "why_it_matters_ar": "كشف التكرار بحلقات متداخلة O(n^2) يجمد التطبيق فوراً في القوائم الكبيرة، والحل العشوائي بـ HashSet قد يسبب OOM على الأجهزة الضعيفة إذا كانت البيانات بالملايين.",
        "worked_example_ar": "في تطبيق مزامنة جهات اتصال تضم 20,000 رقم، استبدلنا الفحص التكراري بـ HashSet؛ فانخفض زمن الكشف من 4 ثوانٍ إلى 12 مللي ثانية فقط، مما منع ظهور حوار ANR.",
        "trade_offs_ar": "استخدام HashSet يوفر سرعة خطية O(n) ولكنه يستهلك ذاكرة O(n)؛ بينما الفرز In-Place يوفر الذاكرة بالكامل ولكنه يستغرق وقتاً أطول O(n log n) ويغير ترتيب القائمة الأصلي.",
        "failure_modes_ar": "أخطر الأخطاء هو استخدام دالة contains داخل حلقة تكرار على List عادية مما يحول الكود إلى كارثة تربيعية O(n^2) دون انتباه، أو استخدام HashSet مع كائنات لا تملك equals وhashCode سليمين.",
        "production_perspective_ar": "في كود الإنتاج، توفر كوتلن دوال جاهزة عالية الكفاءة مثل list.distinct() أو list.toSet()، وتُستخدم BitSet في معالجة سجلات المعرفات الضخمة لصفرية ضغط الـ GC.",
        "how_to_answer_ar": "ابدأ بحل HashSet الخطي القياسي، ثم اشرح كيف ترجع دالة add قيمة false، واطرح بديل الفرز الموضعي لحماية الذاكرة، واختم بحل BitSet المبتكر للأرقام والمعرفات.",
        "talking_points_ar": "كفاءة HashSet بـ O(n)، استغلال مخرج add() البولياني، بديل الفرز الموضعي In-Place Sort، مشكلة الـ Memory Churn، وهيكل BitSet الموفر للأرقام.",
        "follow_ups_ar": "كيف تعمل دالة distinct() في مكتبة كوتلن القياسية داخلياً؟ ومتى تستخدم فلاتر بلوم (Bloom Filters) لاكتشاف التكرار التقريبي في البيانات الضخمة؟",
        "self_check_ar": "هل شرحت حل HashSet والفرز الموضعي، واستخدام BitSet للأرقام، وحذرت من O(n^2)؟",
        "references_ar": f"- [Kotlin Collections: distinct and toSet](https://kotlinlang.org/api/latest/jvm/stdlib/kotlin.collections/distinct.html) — التوثيق الرسمي لدوال كشف التكرار في كوتلن.\n- [Java Platform: BitSet Class](https://docs.oracle.com/javase/8/docs/api/java/util/BitSet.html) — الدليل الرسمي لاستخدام مصفوفات البتات لتوفير الذاكرة.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """نكتشف التكرار بكفاءة عالية في وقت خطي O(n) باستخدام HashSet بمرور واحد بالاستفادة من أن دالة add ترجع false عند تكرار العنصر. وإذا كانت الذاكرة محدودة جداً، نفرز القائمة موضعياً في O(n log n) ونفحص العناصر المتجاورة. وللمعرفات الرقمية البدائية، يوفر هيكل BitSet كشفاً خطياً مع تقليص الذاكرة بأكثر من 95%.""",
        "best_answer_ar": """يعتمد اختيار الأسلوب الأمثل لاكتشاف التكرار في القوائم الكبيرة على الموازنة بين السرعة الزمنية المتاحة وميزانية الذاكرة على الهاتف.
الخيار القياسي والأسرع برمجياً لمعظم كائنات البيانات هو استخدام جدول التجزئة HashSet؛ حيث نمر على القائمة في دورة خطية واحدة O(n) ونفحص مخرج دالة set.add(item)؛ فإذا أرجعت الدالة قيمة false، فهذا يعني أن العنصر مكرر وموجود بالفعل، مما يحقق كشفاً فورياً دون الحاجة لتكرار البحث.
أما إذا كانت الذاكرة مقيدة بشدة على هواتف اقتصادية ونخشى إجهاد مجمع القمامة بكائنات العقد الكثيرة، فيمكننا اللجوء لخيار الفرز الموضعي In-Place Sorting؛ حيث تُفرز المصفوفة في O(n log n)، ثم يُجرى مسح خطي للمقارنة بين العناصر المتجاورة فقط، مما يلغي تماماً استهلاك الذاكرة الإضافية.
وفي حال كانت البيانات عبارة عن معرفات رقمية موجبة، فإن استخدام هيكل BitSet يمثل القمة في توفير الذاكرة؛ حيث يمثل كل رقم ببت واحد فقط، مما يقلص حجم الذاكرة المستهلكة بأكثر من خمسة وتسعين بالمئة مقارنة بمجموعات الكائنات العادية ويضمن سلاسة مطلقة في الأداء.""",
        "deep_answer_ar": """من منظور كفاءة الخوارزميات وتحسين استهلاك الذاكرة في أجهزة أندرويد، يتطلب اكتشاف التكرار في مجموعات البيانات الضخمة تحليلاً دقيقاً لبيئة التشغيل وتكلفة تخصيص الكائنات على الـ Heap.
الحل المبدئي الساذج القائم على الحلقات المتداخلة يمثل كارثة تربيعية O of n squared تسقط إطارات الشاشة وتؤدي حتماً إلى إغلاق التطبيق بإنذار ANR عند تجاوز القائمة لعدة آلاف من العناصر. ولذلك فإن المعيار الهندسي المعتمد للبيانات العامة هو التصفية الخطية بالمرور المفرد؛ حيث نعتمد على تعقيد الإضافة اللحظي O of one في HashSet؛ وبمجرد أن ترجع دالة الإضافة قيمة تفيد بوجود العنصر، يُرصد التكرار فورياً في وقت خطي O of n.
ومع ذلك، يدرك مهندس النظم المحترف أن بناء HashSet لخمسين ألف عنصر يحمل كلفة خفية على الهواتف الضعيفة؛ فكل عنصر يتطلب كائن عقدة ومؤشرات ذاكرة وتغليفاً للأرقام، مما يولد ضغطاً ملحوظاً على مجمع القمامة في ART ويتسبب في تقطيع بصري أثناء التمرير.
ولمعالجة هذه المعضلة في الأنظمة المقيدة، نلجأ إلى تقنيات معمارية متخصصة؛ فإذا كان تغيير ترتيب البيانات مسموحاً، نعتمد على الفرز الموضعي للمصفوفات البدائية بتعقيد O of n log n دون حجز أي بايت إضافي على الـ Heap، متبوعاً بمسح خطي لمقارنة العناصر المتجاورة.
وإذا كانت البيانات عبارة عن معرفات رقمية متتالية مثل أرقام المنتجات، نستخدم هيكل java.util.BitSet؛ حيث نخصص بتاً واحداً لكل معرف داخل مصفوفة أرقام طويلة. هذا الهيكل يخفض استهلاك الذاكرة من عدة ميغابايت إلى بضعة كيلوبايتات فقط، ويلغي حجز الكائنات تماماً، مما يضمن أداء فائق السرعة وخالياً من الوقفات المفاجئة حتى على أضعف الهواتف."""
    }
}

# ==========================================
# Validation & Runner logic
# ==========================================
def validate_words():
    print("Checking word counts and spoken style for DSA-01 to DSA-08...")
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

    ee.save_topic_metadata("dsa_01_08", topic_meta)
    ee.merge_all_metadata()

    for qid in sorted(DATA.keys()):
        errs = ee.validate_question(qid)
        if errs:
            print(f"Errors in {qid}:")
            for er in errs:
                print(f"  ❌ {er}")
            sys.exit(1)

    print(f"\nAll {len(DATA)} DSA questions (DSA-01 to DSA-08) successfully elevated and passed validation!\n")

if __name__ == "__main__":
    apply_elevations()
