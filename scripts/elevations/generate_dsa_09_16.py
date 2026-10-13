#!/usr/bin/env python3
"""Generator for DSA-09 through DSA-16 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "dsa.json"

DSA_09_16 = [
    {
        "id": "DSA-09",
        "arabic_explanation": (
            "كيف تحسب التعقيد الزمني بدقة للحلقات التكرارية المتداخلة ذات الحدود المعتمدة على بعضها (Dependent Bounds)؟\n\n"
            "1. خطأ الضرب السطحي الشائع (The Naive Multiplication Error):\n"
            "   - كثير من المطورين ينظرون لحلقتين متداخلتين ويفترضون تلقائياً أن التعقيد هو $O(n \\times m)$ دائماً بمجرد ضرب الحدود!\n   - إذا كانت الحلقة الداخلية تعتمد على متغير الحلقة الخارجية ($j$ يعتمد على $i$)، يجب **حساب مجموع المتسلسلة الرياضية (Summation)** بدقة بدلاً من الضرب السطحي.\n\n"
            "2. الحالة الكلاسيكية: المتسلسلة الحسابية (Arithmetic Series):\n"
            "   - حلقة خارجية `for (i in 0 until n)`، وحلقة داخلية `for (j in i until n)`:\n     * عندما $i = 0$: تنفذ الحلقة الداخلية $n$ مرة.\n     * عندما $i = 1$: تنفذ الحلقة الداخلية $n - 1$ مرة.\n     * عندما $i = n - 1$: تنفذ الحلقة الداخلية $1$ مرة.\n   - إجمالي الخطوات:\n     $$S = n + (n - 1) + (n - 2) + \\dots + 1 = \\sum_{k=1}^n k = \\frac{n(n + 1)}{2} = \\frac{n^2}{2} + \\frac{n}{2}$$\n   - بإهمال الثوابت والحدود الدنيا، يصبح التعقيد **$O(n^2)$**.\n\n"
            "3. المفاجأة الرياضية: المتسلسلة الهندسية (Geometric Series):\n"
            "   - تخيل حلقة يتضاعف فيها $i$ (`i *= 2`) بينما تنفذ الحلقة الداخلية $i$ مرة:\n     * إجمالي الخطوات: $1 + 2 + 4 + 8 + \\dots + n = 2n - 1$.\n   - التعقيد هنا هو **$O(n)$ خطي وليس $O(n^2)$ ولا $O(n \\log n)$** على الإطلاق! لذلك الحساب الرياضي الدقيق إلزامي."
        ),
        "practical_walkthrough": (
            "تحليل عملي للفرق بين المتسلسلة الحسابية والمتسلسلة الهندسية في كود كوتلن:\n"
            "```kotlin\n"
            "// 1. المتسلسلة الحسابية O(n^2):\n"
            "fun printPairs(n: Int) {\n"
            "    var totalSteps = 0\n"
            "    for (i in 0 until n) {\n"
            "        for (j in i until n) { // j يعتمد على i\n"
            "            totalSteps++\n"
            "        }\n"
            "    }\n"
            "    // totalSteps = n * (n + 1) / 2 -> O(n^2)\n"
            "}\n"
            "\n"
            "// 2. المتسلسلة الهندسية O(n) (حلقة متداخلة تبدو مخادعة ولكنها خطية!):\n"
            "fun geometricDependentLoop(n: Int) {\n"
            "    var totalSteps = 0\n"
            "    var i = 1\n"
            "    while (i <= n) {\n"
            "        for (j in 0 until i) { // j يعتمد على i المتضاعف\n"
            "            totalSteps++\n"
            "        }\n"
            "        i *= 2 // تضاعف أسي\n"
            "    }\n"
            "    // الخطوات: 1 + 2 + 4 + 8 + ... + 2^k = 2 * n - 1 -> O(n)!\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Calculate complexity for dependent nested loops by writing out the exact mathematical summation of inner loop executions across each outer iteration rather than naively multiplying bounds. An arithmetic inner loop running n - i steps yields n(n+1)/2 = O(n²), whereas an exponentially stepping outer loop running i steps sums to 2n - 1 = O(n).",
        "best_answer": (
            "Evaluating dependent nested loop complexity requires formulating and solving mathematical summations:\n\n"
            "1. **Formulating the Summation**:\n"
            "   - Instead of multiplying outer loop limit by inner loop limit, represent total operations as $\\sum_{i} T(i)$, where $T(i)$ is the number of operations executed by the inner loop for a specific value of $i$.\n\n"
            "2. **The Arithmetic Dependent Loop ($O(n^2)$)**:\n"
            "   - In algorithms like Selection Sort or pair combinations (`for i in 0 until n`, `for j in i until n`), the inner loop runs $n, n-1, n-2, \\dots, 1$ times.\n   - The summation $\\sum_{i=1}^n i = \\frac{n(n + 1)}{2} = \\frac{1}{2}n^2 + \\frac{1}{2}n$. Applying asymptotic rules (dropping constant $\\frac{1}{2}$ and lower-order $\\frac{1}{2}n$) confirms $O(n^2)$.\n\n"
            "3. **The Geometric Dependent Loop ($O(n)$)**:\n"
            "   - When the outer loop scales geometrically ($i = 1, 2, 4, 8, \\dots, n$) and the inner loop executes $i$ steps, total work is $\\sum_{k=0}^{\\log_2 n} 2^k = 2^{\\log_2 n + 1} - 1 = 2n - 1 = O(n)$.\n   - Despite having nested loops, total work scales strictly linearly."
        ),
        "deep_answer": (
            "From an algorithmic analysis and optimization angle, dependent loop bounds frequently emerge in string algorithms and parsers:\n\n"
            "1. **Amortized Analysis in Two Pointers**: In sliding window algorithms (e.g. longest substring without repeating characters), a `while` loop is nested inside a `for` loop. A naive glance suggests $O(n^2)$. However, because the inner window pointer `left` only advances forward and never resets backward, the inner pointer moves at most $n$ times across the entire algorithm lifecycle. The amortized complexity is $O(n + n) = O(n)$.\n\n"
            "2. **Quadratic String Concatenation**: In legacy Java/Android code, running a loop where a string is concatenated inside an outer loop creates a hidden dependent quadratic loop. Because strings are immutable, each `str += char` creates a new character array copying $1 + 2 + 3 + \\dots + n$ characters, exploding into $O(n^2)$ time and massive heap churn. `StringBuilder` eliminates this by buffering in amortized $O(1)$.\n\n"
            "3. **Big O Master Theorem & Recurrence Trees**: For recursive dependent problems (e.g. divide and conquer), summation trees determine whether work is dominated by leaf nodes, root nodes, or balanced across tree levels."
        ),
        "follow_ups": [
            {
                "question": "Why does a sliding window algorithm with nested while loops have $O(n)$ complexity rather than $O(n^2)$?",
                "answer": "Because the inner window pointer advances monotonically forward at most $n$ times across the entire execution, resulting in an amortized $O(n)$ runtime."
            },
            {
                "question": "What is the closed form sum of $1 + 2 + 3 + \\dots + n$?",
                "answer": "$\\frac{n(n + 1)}{2}$, which asymptotically scales to $O(n^2)$."
            }
        ]
    },
    {
        "id": "DSA-10",
        "arabic_explanation": (
            "كيف تقوم بتصميم وتحليل كاش الـ LRU (Least Recently Used Cache) برمجياً، وما هو دوره في أندرويد؟\n\n"
            "1. ما هو كاش الـ LRU؟\n"
            "   - كاش ذو حجم ثابت ومحدود. عندما يمتلئ الكاش ونحتاج لإضافة عنصر جديد، نقوم بطرد العنصر **الأقل استخداماً في الآونة الأخيرة (Least Recently Used)**.\n   - الشرط الهندسي الصارم: يجب أن تكون عمليتا القراءة (`get`) والإضافة والتحديث (`put`) في **وقت ثابت $O(1)$**.\n\n"
            "2. هيكل البيانات المثالي لتحقيق $O(1)$:\n"
            "   - **قائمة ثنائية الترابط (Doubly Linked List)**:\n     * تحفظ ترتيب الاستخدام الزمني.\n     * الرأس (Head): أحدث عنصر تم استخدامه (Most Recently Used).\n     * الذيل (Tail): أقدم عنصر وأقلها استخداماً (Least Recently Used - المرشح للطرد).\n     * ميزتها: إزالة أي عقدة أو إضافتها في البداية تتم في **$O(1)$** بشرط امتلاك مؤشر العقدة.\n   - **خريطة هاش (HashMap)**:\n     * تربط المفتاح (Key) بمؤشر العقدة في القائمة (`Node`).\n     * ميزتها: البحث عن العقدة في **$O(1)$**.\n   - في كوتلن/جافا القياسية: كلاس `LinkedHashMap(capacity, loadFactor, accessOrder = true)` يدمج كلا الهيكلين جاهزاً.\n\n"
            "3. كاش الـ LruCache في أندرويد:\n"
            "   - يوفر أندرويد `androidx.collection.LruCache`.\n   - الاستخدام الأهم: كاش الصور (Bitmap Memory Cache). يتم قياس حجم الكاش بالبايت (`sizeOf { _, bitmap -> bitmap.byteCount }`) وتحديد حد أقصى (مثلاً $\\frac{1}{8}$ من ذاكرة الـ Heap المتاحة) لمنع الـ OOM."
        ),
        "practical_walkthrough": (
            "تصميم LRU Cache متكامل في كوتلن، واستخدام `LruCache` الرسمي في أندرويد:\n"
            "```kotlin\n"
            "// 1. تصميم LRU Cache من الصفر باستخدام Doubly LinkedList + HashMap:\n"
            "class CustomLruCache<K, V>(private val capacity: Int) {\n"
            "    private class Node<K, V>(val key: K, var value: V, var prev: Node<K, V>? = null, var next: Node<K, V>? = null)\n"
            "    private val map = HashMap<K, Node<K, V>>()\n"
            "    private val head = Node<K?, V?>(null, null)\n"
            "    private val tail = Node<K?, V?>(null, null)\n"
            "\n"
            "    init { head.next = tail; tail.prev = head }\n"
            "\n"
            "    fun get(key: K): V? {\n"
            "        val node = map[key] ?: return null\n"
            "        moveToHead(node) // O(1) نقل للمقدمة كأحدث عنصر\n"
            "        return node.value\n"
            "    }\n"
            "\n"
            "    fun put(key: K, value: V) {\n"
            "        map[key]?.let {\n"
            "            it.value = value\n"
            "            moveToHead(it)\n"
            "        } ?: run {\n"
            "            if (map.size >= capacity) removeTail() // O(1) طرد الأقدم\n"
            "            val newNode = Node(key, value)\n"
            "            map[key] = newNode\n"
            "            addToHead(newNode)\n"
            "        }\n"
            "    }\n"
            "\n"
            "    private fun removeNode(node: Node<K, V>) {\n"
            "        node.prev?.next = node.next\n"
            "        node.next?.prev = node.prev\n"
            "    }\n"
            "    private fun addToHead(node: Node<K, V>) {\n"
            "        node.next = head.next\n"
            "        node.prev = head\n"
            "        head.next?.prev = node\n"
            "        head.next = node\n"
            "    }\n"
            "    private fun moveToHead(node: Node<K, V>) { removeNode(node); addToHead(node) }\n"
            "    private fun removeTail() { tail.prev?.takeIf { it != head }?.let { removeNode(it); map.remove(it.key) } }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "An LRU cache maintains a fixed capacity, evicting the least recently accessed item when full. It achieves O(1) get and put operations by combining a Doubly Linked List (for O(1) access-order tracking) with a HashMap (for O(1) key-to-node lookups). Android provides this natively via androidx.collection.LruCache.",
        "best_answer": (
            "Designing an LRU cache requires coupling two data structures to guarantee constant-time access and eviction:\n\n"
            "1. **The Combined Data Structure Architecture**:\n"
            "   - **Doubly Linked List**: Tracks recency of access. The most recently accessed node is placed at the head; the least recently accessed node sits at the tail. Given a direct node reference, unlinking and prepending operates in $O(1)$ without element shifting.\n   - **HashMap (`HashMap<Key, Node>`)**: Maps keys directly to their corresponding doubly linked list node pointers, enabling $O(1)$ lookups.\n\n"
            "2. **Operational Workflow ($O(1)$ Time)**:\n"
            "   - **`get(key)`**: Lookup node in map. If present, unlink the node and move it to the head of the list; return value ($O(1)$).\n   - **`put(key, value)`**: If key exists, update value and move node to head. If absent, create new node, insert at head, and store in map. If size exceeds capacity, evict the tail node from both list and map in $O(1)$.\n\n"
            "3. **Android Platform `LruCache`**:\n"
            "   - Android's `androidx.collection.LruCache` is internally backed by a Java `LinkedHashMap(capacity, 0.75f, true)` configured with `accessOrder = true`. It supports custom metric weighting via `sizeOf()`."
        ),
        "deep_answer": (
            "In Android production systems, LRU cache tuning determines stability against OutOfMemory crashes:\n\n"
            "1. **Byte-Weighted Cache Sizing**: When caching memory-heavy assets like Android `Bitmap`s, sizing by element count (`capacity = 50`) is fatal because a single uncompressed 4K Bitmap can consume 33MB of RAM while an icon consumes 10KB. Always override `sizeOf(key, value)` to return byte count, sizing the cache dynamically against available runtime memory:\n   `val cacheSize = (Runtime.getRuntime().maxMemory() / 1024 / 8).toInt()`.\n\n"
            "2. **Thread Safety**: Android's `LruCache` methods are synchronized internally using intrinsic locks (`synchronized (this)`). If accessed across hundreds of parallel coroutine workers, lock contention can stall threads. High-concurrency systems use sharded LRU partitions or lock-free concurrent caches.\n\n"
            "3. **Eviction Hooks (`entryRemoved`)**: In Android, when Bitmaps or native buffers are evicted from an LRU cache, overriding `entryRemoved(evicted, key, oldValue, newValue)` enables recycling pooled buffers (e.g. `BitmapPool`) to prevent memory allocation churn on subsequent renders."
        ),
        "follow_ups": [
            {
                "question": "Why is a Doubly Linked List required instead of a Singly Linked List for an LRU Cache?",
                "answer": "Because deleting a node in $O(1)$ requires an immediate reference to its predecessor (`prev`), which a Singly Linked List lacks without an $O(n)$ scan."
            },
            {
                "question": "How does `LinkedHashMap` support LRU eviction out of the box in Java/Kotlin?",
                "answer": "By passing `accessOrder = true` in its constructor and overriding `removeEldestEntry()` to return true when size exceeds capacity."
            }
        ]
    },
    {
        "id": "DSA-11",
        "arabic_explanation": (
            "اشرح الفرق الجوهري بين خوارزميتي BFS و DFS، وما هي تطبيقاتهما العملية الشائعة في هندسة تطبيقات أندرويد؟\n\n"
            "1. البحث بالعرض أولاً (Breadth-First Search - BFS):\n"
            "   - الاستراتيجية: يستكشف العقد مستوى بمستوى (Level by Level)، ويزور جميع الجيران المباشرين قبل التعمق للأسفل.\n   - هيكل البيانات: يعتمد على **طابور (Queue - FIFO)**.\n   - التعقيد الزمني: **$O(V + E)$** (حيث $V$ العقد و $E$ الحواف).\n   - التعقيد المكاني: **$O(W)$** حيث $W$ هو أقصى عرض للشجرة/الرسم البياني.\n   - الاستخدام الأبرز: **إيجاد أقصر مسار (Shortest Path)** في الرسوم البيانية غير الموزونة.\n\n"
            "2. البحث بالعمق أولاً (Depth-First Search - DFS):\n"
            "   - الاستراتيجية: يتعمق في مسار واحد حتى يصل إلى النهاية (Leaf)، ثم يتراجع (Backtracks) لاستكشاف المسارات الأخرى.\n   - هيكل البيانات: يعتمد على **مكدس (Stack - LIFO)** أو التكرار الذاتي (Recursion).\n   - التعقيد الزمني: **$O(V + E)$**.\n   - التعقيد المكاني: **$O(H)$** حيث $H$ هو أقصى عمق للشجرة (Call Stack Height).\n   - الاستخدام الأبرز: **اكتشاف الدورات المغلقة (Cycle Detection)** والترتيب الطوبولوجي (Topological Sort).\n\n"
            "3. تطبيقات أندرويد الواقعية:\n"
            "   - **DFS**: اكتشاف الاعتماديات الدائرية (Circular Dependencies) في مكتبات حقن التبعيات (Dagger/Hilt)، وحساب عمق شجرة الواجهة (View Hierarchy Depth) لكشف التداخلات المفرطة.\n   - **BFS**: البحث في شجرة الـ View للعثور على أول عنصر يطابق شرطاً معيناً بأقل عمق ممكن، وحساب أقصر مسار تنقل بين الشاشات في شجرة الـ Navigation."
        ),
        "practical_walkthrough": (
            "تطبيق خوارزميتي BFS و DFS لفحص شجرة الـ Android View للعثور على زر معين:\n"
            "```kotlin\n"
            "// نموذج شجرة الواجهة المبسط:\n"
            "class ViewNode(val id: String, val children: List<ViewNode> = emptyList())\n"
            "\n"
            "// 1. BFS باستخدام Queue (الأفضل للعثور على أقرب عنصر سطحي):\n"
            "fun findViewBfs(root: ViewNode, targetId: String): ViewNode? {\n"
            "    val queue = ArrayDeque<ViewNode>()\n"
            "    queue.addLast(root)\n"
            "    while (queue.isNotEmpty()) {\n"
            "        val current = queue.removeFirst()\n"
            "        if (current.id == targetId) return current\n"
            "        for (child in current.children) {\n"
            "            queue.addLast(child)\n"
            "        }\n"
            "    }\n"
            "    return null\n"
            "}\n"
            "\n"
            "// 2. DFS باستخدام Recursion (الأفضل لفحص العمق واكتشاف المسارات):\n"
            "fun findViewDfs(current: ViewNode, targetId: String): ViewNode? {\n"
            "    if (current.id == targetId) return current\n"
            "    for (child in current.children) {\n"
            "        val found = findViewDfs(child, targetId)\n"
            "        if (found != null) return found\n"
            "    }\n"
            "    return null\n"
            "}\n"
            "```"
        ),
        "quick_answer": "BFS traverses nodes level-by-level using a FIFO Queue, making it ideal for finding the shortest path in unweighted graphs. DFS explores branches deeply using a LIFO Stack or recursion, making it ideal for cycle detection, topological sorting of dependency graphs, and exhaustive tree traversal. Both run in O(V + E) time.",
        "best_answer": (
            "BFS and DFS are fundamental graph and tree traversal algorithms with distinct structural properties:\n\n"
            "1. **Breadth-First Search (BFS)**:\n"
            "   - **Mechanism**: Explores all neighbors at the current depth level before progressing to deeper tiers, driven by an explicit FIFO queue (`ArrayDeque`).\n   - **Complexity**: $O(V + E)$ time; $O(W)$ auxiliary space where $W$ is the maximum graph width.\n   - **Primary Use Cases**: Shortest-path discovery in unweighted graphs (e.g. shortest navigation hops between app screens), shallow UI tree inspections, and peer-to-peer network discovery.\n\n"
            "2. **Depth-First Search (DFS)**:\n"
            "   - **Mechanism**: Plunges along each branch to leaf terminations before backtracking, driven by call-stack recursion or an explicit LIFO stack.\n   - **Complexity**: $O(V + E)$ time; $O(H)$ auxiliary space where $H$ is the maximum graph depth.\n   - **Primary Use Cases**: Cycle detection in dependency injection graphs (Dagger), topological sorting of Gradle module compilation dependencies, and deep syntax tree evaluations."
        ),
        "deep_answer": (
            "From an Android systems engineering angle, stack safety and tree bounds dictate choices:\n\n"
            "1. **Call Stack Overflow Risks with Recursive DFS**: In deep Android View trees or complex JSON object graphs, recursive DFS can exceed the thread's stack limit, throwing a fatal `StackOverflowError`. Recursive DFS must either be transformed into an iterative DFS utilizing an explicit heap-allocated `ArrayDeque`, or guarded with depth bounds.\n\n"
            "2. **Compose Semantic Node Trees**: Jetpack Compose test assertions (`onNodeWithText`, `printToLog`) use BFS traversal under the hood to find matching semantic layout nodes closest to the tree root, prioritizing shallow surface nodes over deeply nested implementation composables.\n\n"
            "3. **Graph Cycle Detection in Build Tooling**: Gradle and Hilt use Tarjan's or Kosaraju's DFS-based algorithms to detect Strongly Connected Components (cycles) during annotation processing. If module A depends on B and B depends on A, DFS back-edge detection halts compilation with a circular dependency error."
        ),
        "follow_ups": [
            {
                "question": "Why is BFS guaranteed to find the shortest path in an unweighted graph while DFS is not?",
                "answer": "Because BFS explores nodes in order of their exact distance (number of edges) from the root, encountering the target at the earliest possible depth."
            },
            {
                "question": "What is the primary operational risk of using recursive DFS on Android?",
                "answer": "Deep recursion on large trees exhausts the thread stack size, triggering an unrecoverable `StackOverflowError`."
            }
        ]
    },
    {
        "id": "DSA-12",
        "arabic_explanation": (
            "كيف تكتشف وتصلح التحويلات الحسابية ذات التعقيد التربيعي العرضي ($O(n^2)$) داخل قوائم RecyclerView أو Compose؟\n\n"
            "1. الفخ القاتل الشائع (The Accidental $O(n^2)$ Trap):\n"
            "   - في كثير من التطبيقات، يطلب مصمم الواجهة عرض علامة \"محدد\" (Selected Checkbox) بجانب كل عنصر.\n   - يقوم المطور بكتابة الكود التالي داخل `onBindViewHolder` أو داخل Compose `items()`:\n     `val isSelected = selectedIdsList.contains(item.id)`\n   - حيث `selectedIdsList` هي `List<String>` عادية!\n   - الكارثة: `List.contains()` هي عملية بحث خطي تستغرق $O(m)$. وبما أن RecyclerView أو LazyColumn يمر على $n$ عنصر، فإن التكلفة الإجمالية تصبح **$O(n \\times m) \\approx O(n^2)$** مع كل عملية تمرير أو إعادة رسم!\n   - إذا كانت القائمة تحتوي على 5,000 عنصر، فإن التمرير يتطلب ملايين المقارنات في أجزاء من الثانية على الـ Main Thread، مما يجمد الشاشة ويسقط الإطارات فوراً.\n\n"
            "2. فخاخ تربيعية أخرى:\n   - استدعاء `list.indexOf(item)` داخل حلقة العرض.\n   - عمل `items.filter { ... }` داخل دالة الـ Composable أثناء كل Recomposition.\n\n"
            "3. الحل الهندسي الصارم:\n   - تحويل هياكل البيانات المساعدة إلى **`Set`** أو **`Map`** ذات بحث في وقت ثابت **$O(1)$** (`selectedIds.toHashSet()`).\n   - إجراء جميع التحويلات في الـ ViewModel مسبقاً قبل إرسال الـ UI State للشاشة."
        ),
        "practical_walkthrough": (
            "مقارنة بين الكود الكارثي والإصلاح الهندسي المحسن في كوتلن:\n"
            "```kotlin\n"
            "// ❌ الكود الكارثي: O(n^2) داخل Compose LazyColumn يسبب Jank شديد:\n"
            "@Composable\n"
            "fun ProductListBad(products: List<Product>, selectedIdsList: List<String>) {\n"
            "    LazyColumn {\n"
            "        items(products, key = { it.id }) { product ->\n"
            "            // كل عنصر يقوم ببحث خطي O(m) في قائمة selectedIdsList:\n"
            "            val isSelected = selectedIdsList.contains(product.id) // O(n * m) -> O(n^2)!\n"
            "            ProductItemRow(product, isSelected)\n"
            "        }\n"
            "    }\n"
            "}\n"
            "\n"
            "// ✅ الإصلاح الهندسي الأول: تحويل الـ List إلى HashSet للبحث في O(1):\n"
            "@Composable\n"
            "fun ProductListOptimized(products: List<Product>, selectedIdsList: List<String>) {\n"
            "    // تذكر تحويل القائمة إلى Set لضمان بحث O(1) ثابت:\n"
            "    val selectedSet = remember(selectedIdsList) { selectedIdsList.toHashSet() }\n"
            "    LazyColumn {\n"
            "        items(products, key = { it.id }) { product ->\n"
            "            val isSelected = selectedSet.contains(product.id) // O(1) lookup!\n"
            "            ProductItemRow(product, isSelected)\n"
            "        }\n"
            "    }\n"
            "}\n"
            "\n"
            "// 🏆 الإصلاح الأفضل معمارياً: دمج الحالة في ViewModel قبل إرسالها للـ UI:\n"
            "data class ProductUiModel(val product: Product, val isSelected: Boolean)\n"
            "// تحويل القائمة مرة واحدة فقط على Dispatchers.Default في ViewModel\n"
            "```"
        ),
        "quick_answer": "Accidental O(n²) transformations occur when calling linear-time operations like List.contains() or List.indexOf() inside onBindViewHolder or LazyColumn items(). Fix them by transforming secondary collections into HashSets for O(1) contains checks, and moving data mapping upstream into the ViewModel on background dispatchers.",
        "best_answer": (
            "Accidental quadratic operations in Android list adapters represent the leading cause of scrolling jank:\n\n"
            "1. **The Classic Vulnerability Pattern**:\n"
            "   - Calling `list.contains(id)` inside item binding. Because `List.contains()` performs an $O(m)$ linear scan, evaluating it across $n$ list items multiplies complexity to $O(n \\times m) \\approx O(n^2)$. Under rapid scrolling, this triggers thousands of redundant object comparisons on the Main Thread.\n\n"
            "2. **Detection Techniques**:\n"
            "   - **Android Studio CPU Profiler**: Record a trace during fast fling scrolling. Look for call-tree hotspots dominated by `ArrayList.contains()`, `ArrayList.indexOf()`, or `equals()` invocations.\n   - **AndroidX JankStats**: Flags dropped frames exceeding 16.6ms.\n\n"
            "3. **Architectural Remediation**:\n"
            "   - **Collection Indexing**: Convert secondary lookup collections to `HashSet` or `Map`, reducing membership lookups from $O(m)$ to $O(1)$.\n   - **ViewModel Pre-Mapping**: Never compute data relations inside Composable bodies or ViewHolders. Map entities into composite UI state models (`ProductItemUiState(item, isSelected)`) on `Dispatchers.Default` before emitting to the UI."
        ),
        "deep_answer": (
            "From an ART compilation and Compose recomposition perspective, hidden quadratic costs ripple through layout cycles:\n\n"
            "1. **Compose Recomposition Amplification**: In Jetpack Compose, if `selectedIdsList` changes, every item in `LazyColumn` reading that unstable list recomposes. If each item recalculates an $O(n)$ check, the main thread locks up during animations. Using `@Immutable` state holders and pre-calculated booleans prevents nested recomposition passes.\n\n"
            "2. **RecyclerView DiffUtil Complexity Multiplication**: `DiffUtil.calculateDiff` runs in $O(n \\cdot d)$. If your `areItemsTheSame` or `areContentsTheSame` callbacks inadvertently execute linear scans (e.g. comparing inner lists), the diffing calculation explodes beyond $O(n^2)$, stalling UI updates. DiffUtil callbacks must execute strictly in $O(1)$ constant time.\n\n"
            "3. **Zero-Allocation Primitive Collections**: For selection sets of primitive IDs (`Long`), using AndroidX's `LongSparseArray` or primitive `LongArray` with binary search avoids autoboxing overhead while keeping lookup costs tightly bounded."
        ),
        "follow_ups": [
            {
                "question": "Why should `DiffUtil` callbacks (`areItemsTheSame`) strictly execute in $O(1)$ time?",
                "answer": "Because DiffUtil compares items across lists hundreds or thousands of times; non-$O(1)$ comparisons inside the callback explode total diff calculation time."
            },
            {
                "question": "What is the Big O time complexity of `HashSet.contains()` compared to `List.contains()`?",
                "answer": "`HashSet.contains()` operates in $O(1)$ average time, whereas `List.contains()` operates in $O(n)$ linear time."
            }
        ]
    },
    {
        "id": "DSA-13",
        "arabic_explanation": (
            "كيف تسبب سلاسل دوال كولكشنز كوتلن (Collection Chaining) تخصيصات ذاكرة مؤقتة هائلة، وكيف تحلها باستخدام Sequences أو In-Place Loops؟\n\n"
            "1. المشكلة في معالجة القوائم القياسية (Eager Evaluation):\n"
            "   - دوال المجموعات القياسية في كوتلن (`map`, `filter`, `sorted`, `distinct`) تعمل بنظام **التقييم الفوري (Eager Evaluation)**.\n   - كل دالة في السلسلة **تنشئ وتخصص كائن `ArrayList` جديد تماماً في الذاكرة** لتخزين النتائج الوسيطة!\n   - إذا كتبت:\n     `users.filter { ... }.map { ... }.filter { ... }.distinct()`\n   - على قائمة تحتوي على 100,000 عنصر، فأنت تقوم بتخصيص 4 قوائم ضخمة وملايين الكائنات على الـ Heap في غضون ثوانٍ قليلة.\n\n"
            "2. الكارثة على أندرويد:\n   - **GC Pressure هائل**: يمتلئ الـ Heap بالـ Garbage، مما يجبر نظام ART على إطلاق مجمع القمامة (Concurrent Copying GC) بشكل متكرر، متسبباً في توقفات ملحوظة (Jank) واستهلاك مفرط للبطارية.\n\n"
            "3. الحلول الهندسية:\n   - **1. استخدام متتاليات كوتلن (`asSequence()`)**:\n     * تعمل بنظام **التقييم الكسول (Lazy Evaluation)**؛ يمر كل عنصر بمفرده عبر السلسلة بأكملها (Element-by-Element) دون إنشاء أي قوائم وسيطة في الذاكرة!\n   - **2. الحلقات الموضعية المباشرة (In-Place Loops)**:\n     * في المسارات الحرجة جداً (مثل معالجة الإطارات أو الصوت)، استخدام حلقة `for` بسيطة مع `ArrayList` محجوزة مسبقاً يلغي أي تخصيصات إضافية."
        ),
        "practical_walkthrough": (
            "مقارنة عملية توضح الفرق بين السلسلة الفورية والسلسلة الكسولة عبر `asSequence()`:\n"
            "```kotlin\n"
            "// ❌ السلسلة الفورية (Eager) - تخصص 3 قوائم وسيطة في الذاكرة:\n"
            "fun processOrdersEager(orders: List<Order>): List<String> {\n"
            "    return orders\n"
            "        .filter { it.isCompleted } // قائمة جديدة في الذاكرة!\n"
            "        .map { it.customerEmail }  // قائمة ثانية في الذاكرة!\n"
            "        .take(10)                  // قائمة ثالثة في الذاكرة!\n"
            "}\n"
            "\n"
            "// ✅ السلسلة الكسولة (Lazy Sequence) - صفر قوائم وسيطة وتتوقف فور الوصول لـ 10 عناصر:\n"
            "fun processOrdersLazy(orders: List<Order>): List<String> {\n"
            "    return orders\n"
            "        .asSequence()              // تحويل لمعالجة متدفقة كسولة\n"
            "        .filter { it.isCompleted }\n"
            "        .map { it.customerEmail }\n"
            "        .take(10)                  // ميزة رائعة: تقف بعد أول 10 طلبات دون فحص باقي القائمة!\n"
            "        .toList()                  // إنشاء القائمة النهائية الوحيدة فقط\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Chaining Kotlin standard collection operators eagerly creates intermediate ArrayList allocations at each transformation step, generating heavy heap churn and GC pressure. Fix this by using Kotlin Sequences (.asSequence()) for lazy element-by-element evaluation without intermediate collections, or single-pass imperative loops.",
        "best_answer": (
            "Chained transformations on standard Kotlin collections trigger significant heap allocation overhead due to eager evaluation:\n\n"
            "1. **Eager Evaluation Mechanics**:\n"
            "   - Operators on `Iterable` (`filter`, `map`, `distinct`) execute eagerly. Each chained step instantiates and populates a new intermediate `ArrayList`. A chain of 4 operations over 50,000 objects allocates 4 distinct collections and hundreds of thousands of heap references.\n\n"
            "2. **Android Runtime Impact**:\n"
            "   - The rapid generation of short-lived intermediate lists saturates the ART young generation space, triggering frequent Garbage Collection cycles. On the main thread, GC pauses preempt frame rendering budgets, manifesting as noticeable UI stutter.\n\n"
            "3. **Resolution via Kotlin Sequences (`asSequence()`)**:\n"
            "   - Sequences evaluate lazily: elements are piped through the entire transformation pipeline one by one. Terminal operations (`toList()`, `first()`) consume elements on-demand, eliminating intermediate list allocations entirely.\n   - Short-circuit operations like `take(5)` terminate processing immediately after finding 5 matches, skipping remaining items."
        ),
        "deep_answer": (
            "From a performance benchmarking perspective, choosing between Collections, Sequences, and Loops requires nuance:\n\n"
            "1. **The Sequence Overhead Penalty for Small Collections**: Sequences wrap operations in iterator and lambda closure state machines. For small collections ($n < 50$), the iterator object overhead exceeds the cost of a simple eager list allocation. Sequences deliver substantial net benefits primarily on large datasets ($n > 500$) or chains with multiple filtering steps.\n\n"
            "2. **Stateful Sequence Operators**: Not all sequence operators are completely memory-free. Stateful operators like `sorted()` or `distinct()` must buffer elements internally to establish ordering or uniqueness before emitting, though they still avoid multi-step intermediate list duplication.\n\n"
            "3. **Zero-Allocation Imperative Hot Paths**: In high-frequency Android code paths (Canvas `onDraw`, custom gesture detectors, physics calculations), neither collections nor sequences are acceptable. Engineers write manual `for` loops utilizing pre-sized reusable buffers to maintain a 100% allocation-free runtime."
        ),
        "follow_ups": [
            {
                "question": "Why shouldn't you use Kotlin Sequences for very small lists (e.g. fewer than 20 items)?",
                "answer": "Because the overhead of instantiating sequence iterators and state machine wrappers outweighs the minor cost of a small eager list allocation."
            },
            {
                "question": "What happens when you use a short-circuit operator like `take(5)` on a Sequence versus an Iterable?",
                "answer": "A Sequence stops processing the remaining items as soon as 5 matches are found, whereas an Iterable processes every single element before taking the first 5."
            }
        ]
    },
    {
        "id": "DSA-14",
        "arabic_explanation": (
            "قائمة المنتجات تتجمد وتتوقف عن التمرير بسلاسة على الأجهزة الاقتصادية الضعيفة. كيف تميز هندسياً بين اختناقات الرسم (Rendering Bottlenecks) والتعقيد الخوارزمي (Algorithmic Complexity)؟\n\n"
            "1. منهجية التشخيص والفرز الهندسي (Diagnostic Isolation):\n"
            "   - لا تخمن السبب أبداً! استخدم أدوات القياس الرسمية: **Android Studio CPU Profiler** و **Perfetto / Systrace**.\n\n"
            "2. علامات الاختناق الخوارزمي (Algorithmic Bottlenecks):\n"
            "   - **مؤشرات Profiler**: وقت الـ CPU يضيع في كود الـ Application (دوال Kotlin خاصة بك مثل `prepareUiModel`, `List.contains`, `filter`, فرز القوائم).\n   - **مكان التنفيذ**: استهلاك كامل للـ CPU على خيط الـ Main Thread في حسابات بيانات.\n   - **الحل**: نقل الحسابات إلى `Dispatchers.Default`، تحسين التعقيد من $O(n^2)$ إلى $O(n)$، واستخدام الـ HashMaps.\n\n"
            "3. علامات اختناق الرسم والواجهة (Rendering Bottlenecks):\n"
            "   - **مؤشرات Profiler / Systrace**: وقت الـ CPU يضيع داخل إطار عمل أندرويد: `Choreographer.doFrame`, `View.onDraw`, `measure`, `layout`, أو دوال Compose: `recompose`, `Modifier.layout`.\n   - **مؤشرات الـ GPU**: معدل Overdraw أحمر داكن (إعادة رسم البكسل أكثر من 4 مرات فوق بعضه)، أو شجرة Views شديدة العمق (View Hierarchy > 10 مستويات).\n   - **الحل**: تسطيح الـ Layout، إزالة الخلفيات المكررة، استخدام Compose `derivedStateOf` لمنع الـ Recompositions غير الضرورية، وتفعيل التمرير المسبق (Prefetching)."
        ),
        "practical_walkthrough": (
            "خطة عملية لعزل سبب البطء وفحص مؤشرات الأداء بالخطوات البرمجية:\n"
            "```kotlin\n"
            "// 1. اختبار العزل السريع (Isolation Test):\n"
            "// استبدل محتوى الـ Item مؤقتاً بـ Text بسيط: Text(\"Item\")\n"
            "// إذا استمر التجمد -> المشكلة خوارزمية (في DiffUtil أو معالجة البيانات).\n"
            "// إذا اختفى التجمد وأصبح التمرير 60fps -> المشكلة في رسم وتعقيد الـ UI Item Layout!\n"
            "\n"
            "// 2. استخدام Trace رسمي في الكود لمشاهدة الدالة في Perfetto / Systrace:\n"
            "import androidx.tracing.trace\n"
            "\n"
            "fun bindItem(product: Product) {\n"
            "    trace(\"ProductItemBinding\") {\n"
            "        // إذا ظهر هذا القسم في Perfetto مستغرقاً 14ms -> اختناق حسابي داخل الربط\n"
            "        val state = calculateComplexDiscount(product)\n"
            "        applyStateToView(state)\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Distinguish bottlenecks using Android Studio CPU Profiler and Perfetto. If execution time is concentrated in application business logic, sorting, or collection lookups on the main thread, the bottleneck is algorithmic. If time is spent in Choreographer.doFrame, view measure/layout passes, or GPU overdraw, the bottleneck is rendering.",
        "best_answer": (
            "Diagnosing list stutter on low-end hardware requires systematic profiling to separate computational complexity from layout rendering pipeline limits:\n\n"
            "1. **Profiling Trace Analysis via Perfetto**:\n"
            "   - **Algorithmic Complexity Signature**: The main thread thread-state shows continuous `Running` blocks with stack traces anchored in application domain logic: data parsing, reflection mappers, unmemoized sorting, or linear collection searches. Frame drops happen because calculations starve the UI thread of frame budgets.\n   - **Rendering Bottleneck Signature**: Time is spent inside Android framework methods: `View.measure()`, `View.layout()`, `View.draw()`, or Compose `LayoutNode.remeasure()`. Systrace reveals heavy `Choreographer#doFrame` stretches and RenderThread GPU sync stalls.\n\n"
            "2. **Empirical A/B Isolation Test**:\n"
            "   - Temporarily replace complex row items with a plain lightweight `Text(\"Item\")`. If scrolling remains laggy, the root cause is upstream algorithmic computation (e.g. DiffUtil recalculations or reactive stream thrashing). If scrolling instantly stabilizes at 60fps, the culprit is layout complexity or image decoding.\n\n"
            "3. **Resolution Pathways**:\n"
            "   - Fix algorithmic lag by offloading computations to `Dispatchers.Default` and caching calculations.\n   - Fix rendering lag by flattening view hierarchies, optimizing Compose keys, and removing transparent Overdraw layers."
        ),
        "deep_answer": (
            "On low-end Android hardware (e.g. Android Go with weak Quad-Core Cortex-A53 processors), hardware limits exacerbate specific failure modes:\n\n"
            "1. **Core Starvation & Priority Inversion**: On weak devices, running heavy background algorithmic tasks on `Dispatchers.Default` can saturate all CPU cores, starving the UI thread of operating system scheduling slots. Explicitly tuning background thread priorities (`Process.setThreadPriority(THREAD_PRIORITY_BACKGROUND)`) ensures the UI thread preempts background calculations.\n\n"
            "2. **Garbage Collection Pauses as Root Cause**: Often, a list freeze is neither pure math nor pure rendering—it is memory churn. Low-end devices with 2GB RAM run ART with minimal heap ceilings. If item binding creates temporary lambdas, string builders, or boxed primitives, ART triggers blocking GC passes that pause all threads.\n\n"
            "3. **Compose Modifier Re-instantiation**: In Jetpack Compose, declaring complex inline modifiers without caching allocates new modifier chains on every recomposition. Caching modifiers or using `@Stable` state models eliminates layout phase invalidation."
        ),
        "follow_ups": [
            {
                "question": "What is the quickest empirical test to verify whether a list lag is caused by item layout rendering?",
                "answer": "Temporarily replace the complex item layout with a static simple text label; if smooth scrolling returns, rendering is the bottleneck."
            },
            {
                "question": "Why can heavy background tasks cause UI frame drops on low-end quad-core Android devices?",
                "answer": "Because background workers can saturate all available physical CPU cores, causing OS thread scheduling starvation for the main thread."
            }
        ]
    },
    {
        "id": "DSA-15",
        "arabic_explanation": (
            "كيف تبني نظام تحديد معدل الطلبات (Rate Limiter) أو خريطة لمنع تكرار الطلبات المتزامنة (Request Deduplication) في أندرويد، وما هو الهيكل الأنسب؟\n\n"
            "1. متطلبات النظام:\n"
            "   - **Rate Limiting**: السماح بحد أقصى من الطلبات (مثلاً: 5 طلبات في الثانية) ورفض أو تأخير الطلبات الزائدة.\n   - **Request Deduplication**: إذا تم استدعاء نفس الـ API بنفس المعاملات 3 مرات بالتوازي قبل اكتمال الطلب الأول، يتم تنفيذ **طلب شبكة واحد فقط** ومشاركة النتيجة مع المستدعين الثلاثة (Coalescing).\n\n"
            "2. اختيار هياكل البيانات المناسبة:\n"
            "   - **للـ Rate Limiting (خوارزمية Sliding Window Log)**:\n     * **`ArrayDeque<Long>`**: لتخزين الطوابع الزمنية (Timestamps) للطلبات الأخيرة.\n     * عند كل طلب جديد: نزيل الطوابع الأقدم من (`now - windowSize`) من بداية الـ Deque في $O(1)$.\n     * إذا كان حجم الـ Deque أقل من الحد المسموح، نضيف الوقت الحالي ونقبل الطلب، وإلا نرفضه.\n   - **للـ Deduplication (دمج الطلبات المتزامنة)**:\n     * **`ConcurrentHashMap<String, Deferred<Response>>`** (مع Kotlin Coroutines):\n     * إذا كان المفتاح موجوداً في الخريطة، نقوم بعمل `await()` على نفس النتيجة الجاري تحميلها دون فتح اتصال جديد!\n     * عند انتهاء الطلب، نزيل المفتاح من الخريطة في بلوك `finally`."
        ),
        "practical_walkthrough": (
            "تنفيذ Rate Limiter و Request Deduplication في كوتلن بشكل آمن ومتزامن:\n"
            "```kotlin\n"
            "// 1. Sliding Window Rate Limiter آمن الخيوط (Thread-Safe):\n"
            "class SlidingWindowRateLimiter(private val maxRequests: Int, private val windowDurationMs: Long) {\n"
            "    private val timestamps = ArrayDeque<Long>()\n"
            "    private val lock = Any()\n"
            "\n"
            "    fun tryAcquire(): Boolean = synchronized(lock) {\n"
            "        val now = System.currentTimeMillis()\n"
            "        // إزالة الطوابع الزمنية المنتهية الصلاحية من بداية الطابور:\n"
            "        while (timestamps.isNotEmpty() && (now - timestamps.first()) > windowDurationMs) {\n"
            "            timestamps.removeFirst()\n"
            "        }\n"
            "        if (timestamps.size < maxRequests) {\n"
            "            timestamps.addLast(now)\n"
            "            true // مسموح بالطلب\n"
            "        } else {\n"
            "            false // تم تجاوز المعدل (Rate limited)\n"
            "        }\n"
            "    }\n"
            "}\n"
            "\n"
            "// 2. Request Deduplicator (Single-Flight Pattern) باستخدام Coroutines:\n"
            "class RequestDeduplicator<T> {\n"
            "    private val inFlight = ConcurrentHashMap<String, Deferred<T>>()\n"
            "\n"
            "    suspend fun execute(key: String, block: suspend () -> T): T = coroutineScope {\n"
            "        val deferred = inFlight.computeIfAbsent(key) {\n"
            "            async(Dispatchers.IO) { block() }\n"
            "        }\n"
            "        try {\n"
            "            deferred.await() // ينتظر الطلب المشترك\n"
            "        } finally {\n"
            "            inFlight.remove(key, deferred) // تنظيف بعد الاكتمال\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "For a rate limiter, a sliding window log using an ArrayDeque of timestamps fits best, pruning expired entries in O(1) amortized time. For concurrent request deduplication, use a ConcurrentHashMap mapping request keys to in-flight Coroutine Deferred instances (Single-Flight pattern), coalescing concurrent duplicate calls into a single network invocation.",
        "best_answer": (
            "Designing rate limiters and deduplication managers requires thread-safe collections tailored to sliding time windows and task coalescing:\n\n"
            "1. **Sliding Window Rate Limiter (`ArrayDeque<Long>`)**:\n"
            "   - **Mechanism**: Maintains timestamps of recent requests in an `ArrayDeque`. On each incoming request at time $t$, pop timestamps older than $t - \\text{windowDuration}$ from the head in $O(1)$ time. If the remaining deque size is within limits, push $t$ to the tail and allow the request; otherwise, throttle.\n   - **Trade-off**: Provides exact precision without the boundary burst vulnerabilities of fixed-window counters, consuming minimal $O(k)$ memory where $k$ is the rate limit.\n\n"
            "2. **Concurrent Request Deduplication (Single-Flight Pattern)**:\n"
            "   - **Mechanism**: Use a `ConcurrentHashMap<String, Deferred<Result>>`. When a request arrives, invoke `computeIfAbsent(key) { async { executeNetworkCall() } }`. Multiple concurrent callers subscribe to the identical `Deferred.await()`, eliminating duplicate network traffic.\n   - **Cleanup**: In a `finally` block, remove the key from the map once the network call completes to ensure subsequent requests fetch fresh data."
        ),
        "deep_answer": (
            "From an Android networking and resilience perspective, these patterns protect battery and server quotas:\n\n"
            "1. **Thundering Herd Mitigation on Screen Launch**: When 4 distinct UI components on a dashboard independently request the current user profile upon startup, naive code fires 4 duplicate HTTP requests. The Single-Flight deduplication pattern coalesces these into 1 HTTP call, saving radio wakeups and network bandwidth.\n\n"
            "2. **Token Bucket Algorithm Alternative**: For high-throughput client scenarios, the Token Bucket algorithm (`AtomicInteger` tokens replenished at a constant rate) is preferred over timestamp deques because it consumes $O(1)$ space and handles traffic bursts gracefully without logging individual timestamps.\n\n"
            "3. **Handling Network Failures in Deduplication**: If the in-flight network call fails with an exception, all awaiting callers must receive the exception cleanly, and the key must be removed from the map immediately so retry logic is not stuck on a failed cached future."
        ),
        "follow_ups": [
            {
                "question": "What is the primary advantage of the sliding window log over a fixed-window counter for rate limiting?",
                "answer": "It prevents the double-burst edge case where twice the allowed requests arrive across the boundary between two adjacent fixed windows."
            },
            {
                "question": "Why is `remove(key, deferred)` preferred over `remove(key)` in the deduplication cleanup block?",
                "answer": "It atomically ensures you only remove the entry if it still points to the exact completed task, avoiding race conditions with newly started requests."
            }
        ]
    },
    {
        "id": "DSA-16",
        "arabic_explanation": (
            "كيف تقوم بتحسين خوارزمية برمجية في أندرويد مع الحفاظ التام على نظافة الكود (Maintainability) وصحته وسهولة اختباره؟\n\n"
            "1. المبدأ الذهبي في هندسة البرمجيات:\n"
            "   - قاعدة دونالد كنوث الشهيرة: **\"التحسين المبكر هو أصل كل الشرور (Premature optimization is the root of all evil)\"**.\n   - لا تقم بتحسين كود معقد أو كتابة خوارزميات صعبة الفهم قبل أن تثبت بالأرقام وجود مشكلة أداء حقيقية تؤثر على تجربة المستخدم.\n\n"
            "2. المنهجية الهندسية ثلاثية الخطوات (Kent Beck's Rule):\n   - **1. Make it Work (اجعله يعمل أولاً)**: كتابة الحل الأبسط والأنظف والأكثر وضوحاً، مع كتابة مجموعة شاملة من Unit Tests تغطي الحالات العادية والحدية (Edge Cases).\n   - **2. Make it Right (اجعله صحيحاً ومعمارياً)**: فصل المسؤوليات، وتسمية الدوال والمتغيرات بوضوح، وضمان سهولة قراءة الكود للزملاء.\n   - **3. Make it Fast (اجعله سريعاً فقط عند الحاجة)**: إذا أظهر الـ Profiler وجود عنق زجاجة، قم بتحسين الخوارزمية مع الاعتماد على الـ Unit Tests لضمان عدم كسر أي منطق عمل.\n\n"
            "3. استراتيجيات الحفاظ على نظافة الكود أثناء التحسين:\n   - **عزل الكود المحسن وراء Interface**: إبقاء الواجهة العامة نظيفة وبسيطة، وحصر التعقيد الخوارزمي في كلاس مخصص ومعزول.\n   - **التوثيق الواضح للتعقيد (Big O Documentation)**: كتابة تعليقات تشرح أسباب اختيار هيكل بيانات غير تقليدي وتعقيده الزمني والمكاني.\n   - **اختبارات الأداء الآلية (Microbenchmarks)**: استخدام Jetpack Macrobenchmark / Microbenchmark لإثبات نسبة التحسين ومراقبة عدم تراجع الأداء مع التحديثات."
        ),
        "practical_walkthrough": (
            "منهجية تحسين خوارزمية مع الحفاظ على عزل الكود ونظافته في كوتلن:\n"
            "```kotlin\n"
            "// 1. واجهة نظيفة ومستقرة تفصل الواجهة عن تفاصيل التحسين الداخلي:\n"
            "interface SearchIndex {\n"
            "    fun findMatches(query: String): List<String>\n"
            "}\n"
            "\n"
            "// 2. التنفيذ المحسن خوارزمياً (Trie / Prefix Tree) معزول تماماً وموثق:\n"
            "/**\n"
            " * Optimized prefix search backed by a Trie.\n"
            " * Lookup Time: O(L) where L is query length, replacing naive O(N * L) scans.\n"
            " * Space Complexity: O(Total Characters across words).\n"
            " */\n"
            "class TrieSearchIndex(words: List<String>) : SearchIndex {\n"
            "    private class TrieNode {\n"
            "        val children = HashMap<Char, TrieNode>()\n"
            "        var isWord = false\n"
            "    }\n"
            "    private val root = TrieNode()\n"
            "\n"
            "    init {\n"
            "        words.forEach { insert(it) }\n"
            "    }\n"
            "\n"
            "    private fun insert(word: String) {\n"
            "        var curr = root\n"
            "        for (ch in word) {\n"
            "            curr = curr.children.computeIfAbsent(ch) { TrieNode() }\n"
            "        }\n"
            "        curr.isWord = true\n"
            "    }\n"
            "\n"
            "    override fun findMatches(query: String): List<String> {\n"
            "        // منطق بحث فائق السرعة O(L) معزول داخل الكلاس\n"
            "        return emptyList() // implementation\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Optimize algorithms without sacrificing maintainability by following 'Make it work, make it right, make it fast'. Write comprehensive unit tests first to guard correctness, profile to prove real bottlenecks, encapsulate optimized complexity behind clean interface abstractions, and document Big O trade-offs and benchmarks directly in code comments.",
        "best_answer": (
            "Disciplined algorithmic optimization maintains software quality without introducing fragile complexity:\n\n"
            "1. **Test-First Safety Harness**:\n"
            "   - Before modifying an algorithm, author an exhaustive suite of unit and property-based tests covering edge cases (empty collections, duplicates, boundary values). This guarantees that optimizations do not introduce subtle behavioral regressions.\n\n"
            "2. **Profile-Driven Optimization**:\n"
            "   - Adhere to the rule: 'Make it work, make it right, make it fast'. Never optimize based on theoretical intuition; measure using Android Studio CPU Profiler or Jetpack Benchmark. If a method consumes $0.1\\%$ of frame time, optimizing it adds technical debt for zero user benefit.\n\n"
            "3. **Encapsulation Behind Clean Abstractions**:\n"
            "   - Hide complex data structures (e.g. Tries, interval trees, bit manipulation) behind clear public domain interfaces. The rest of the codebase interacts with simple inputs and outputs, decoupling consumers from optimization mechanics.\n\n"
            "4. **Explicit Documentation & Microbenchmarking**:\n"
            "   - Document the asymptotic Big O time and space complexity in KDoc, noting why a specific data structure was chosen over standard library primitives."
        ),
        "deep_answer": (
            "From an engineering leadership and team governance perspective, algorithmic maintenance requires strict guardrails:\n\n"
            "1. **The 'Clever Code' Anti-Pattern**: Code that relies on obscure bitwise hacks or undocumented side-effects is difficult to review and dangerous to maintain. If an engineer leaves the company, unreadable optimizations become untouchable legacy code. When bitwise or in-place optimizations are necessary, pair them with readable reference implementations in test suites.\n\n"
            "2. **Automated CI Regression Benchmarking**: High-performing teams run automated Jetpack Microbenchmark tasks in CI nightly builds. If an algorithmic change degrades throughput or spikes memory allocations by more than $5\\%$, the build triggers a performance regression alert.\n\n"
            "3. **Standard Library Primacy**: Modern standard library implementations (Kotlin stdlib, Guava, AndroidX) are extensively tested, vectorized, and optimized for JVM/ART runtimes. Replacing standard library calls with custom algorithmic implementations should only occur when profiling demonstrates an order-of-magnitude performance gain."
        ),
        "follow_ups": [
            {
                "question": "What is the primary role of unit tests before initiating an algorithmic refactoring?",
                "answer": "They act as a regression safety net, proving that the optimized algorithm produces identical outputs for all edge cases."
            },
            {
                "question": "Why should algorithmic optimizations be encapsulated behind interfaces?",
                "answer": "To prevent internal complexity from leaking into callers and to allow switching between implementations without affecting consumers."
            }
        ]
    }
]


def main() -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    existing_data: list[dict] = []
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            existing_data = json.load(f)

    existing_dict = {item["id"]: item for item in existing_data}
    for item in DSA_09_16:
        existing_dict[item["id"]] = item

    all_items = list(existing_dict.values())
    all_items.sort(key=lambda x: x["id"])

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)

    print(f"Updated {DATA_FILE} with questions DSA-09 to DSA-16. Total questions: {len(all_items)}")


if __name__ == "__main__":
    main()
