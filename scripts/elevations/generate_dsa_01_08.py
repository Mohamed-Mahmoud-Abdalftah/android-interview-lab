#!/usr/bin/env python3
"""Generator for DSA-01 through DSA-08 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "dsa.json"

DSA_01_08 = [
    {
        "id": "DSA-01",
        "arabic_explanation": (
            "ما هو الفرق الجوهري بين التعقيد الزمني (Time Complexity) والتعقيد المكاني (Space Complexity) في سياق تطوير تطبيقات أندرويد؟\n\n"
            "1. التعقيد الزمني (Time Complexity):\n"
            "   - هو مقياس رياضي لمعدل نمو **عدد العمليات الحسابية والخطوات** التي تنفذها الخوارزمية مع زيادة حجم المدخلات ($n$).\n   - في أندرويد: يؤثر التعقيد الزمني مباشرة على **معدل الإطارات (Frame Rate)** وواجهة المستخدم. إذا استغرقت خوارزمية فرز أو بحث على الـ Main Thread أكثر من 16ms (أو 8.3ms لشاشات 120Hz)، يتجمد التطبيق ويسقط إطارات (Jank/Dropped Frames)، وقد يؤدي إلى خطأ ANR (Application Not Responding).\n\n"
            "2. التعقيد المكاني (Space Complexity):\n"
            "   - هو مقياس لمعدل نمو **الذاكرة المؤقتة الإضافية (Auxiliary Memory)** التي تستهلكها الخوارزمية على الـ Heap مع زيادة حجم المدخلات ($n$)، متضمنة كائنات الذاكرة و Call Stack التكرار (Recursion).\n   - في أندرويد: يؤثر التعقيد المكاني مباشرة على **الضغط على مجمع القمامة (GC Pressure)** ومساحة الذاكرة المحدودة للتطبيق (Dalvik/ART Heap Limit). الخوارزميات التي تخصص مصفوفات مؤقتة كبيرة تؤدي لتشغيل GC متكرر يوقف التطبيق مؤقتاً (GC Pauses) أو تسبب كراش OutOfMemoryError (OOM) على الهواتف الاقتصادية.\n\n"
            "3. المفاضلة الهندسية (Space-Time Trade-off):\n"
            "   - في كثير من الأحيان، نضحي بالذاكرة لتسريع الوقت (مثل استخدام HashMap للبحث في $O(1)$ بدلاً من $O(n)$ في مصفوفة، بتكلفة ذاكرة أعلى لكائنات الـ Node والـ Buckets)."
        ),
        "practical_walkthrough": (
            "مقارنة عملية في كوتلن بين خوارزمية ذات تعقيد زمني سريع ومكاني أعلى، وخوارزمية ذات تعقيد مكاني صفري:\n"
            "```kotlin\n"
            "// السيناريو: البحث عن رقمين مجموعهما Target في قائمة أسعار:\n"
            "\n"
            "// الخيار 1: استهلاك ذاكرة لتوفير الوقت (Time: O(n), Space: O(n))\n"
            "fun hasTwoSumWithExtraMemory(prices: List<Int>, target: Int): Boolean {\n"
            "    val seen = HashSet<Int>() // يستهلك ذاكرة على الـ Heap لكل عنصر\n"
            "    for (price in prices) {\n"
            "        val complement = target - price\n"
            "        if (seen.contains(complement)) return true\n"
            "        seen.add(price)\n"
            "    }\n"
            "    return false\n"
            "}\n"
            "\n"
            "// الخيار 2: الحفاظ على الذاكرة مع زيادة طفيفة في الوقت (Time: O(n log n), Space: O(1) in-place)\n"
            "fun hasTwoSumInPlace(sortedPrices: IntArray, target: Int): Boolean {\n"
            "    var left = 0\n"
            "    var right = sortedPrices.size - 1\n"
            "    while (left < right) {\n"
            "        val sum = sortedPrices[left] + sortedPrices[right]\n"
            "        when {\n"
            "            sum == target -> return true\n"
            "            sum < target -> left++\n"
            "            else -> right--\n"
            "        }\n"
            "    }\n"
            "    return false // تعقيد مكاني O(1) تماماً بدون أي تخصيص على الـ Heap\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Time complexity measures the growth rate of computational operations as input size increases, directly impacting UI frame drops and ANRs. Space complexity measures the auxiliary memory allocated on the heap and call stack, directly impacting garbage collection thrashing and OutOfMemoryErrors on constrained Android devices.",
        "best_answer": (
            "Time and space complexity quantify algorithmic scalability and resource utilization:\n\n"
            "1. **Time Complexity**:\n"
            "   - Quantifies the scaling rate of operational steps as input size $n$ approaches infinity. In Android client development, unoptimized time complexity ($O(n^2)$ transformations) on the main thread exceeds the 16.6ms per-frame rendering budget (or 8.3ms at 120Hz), resulting in UI jank, stutter, and potential Application Not Responding (ANR) dialogs.\n\n"
            "2. **Space Complexity**:\n"
            "   - Quantifies auxiliary memory allocated on the Dalvik/ART heap and recursion stack frames. In Android, aggressive memory allocation triggers frequent Garbage Collector (GC) passes that suspend thread execution (stop-the-world pauses). On low-RAM devices with tight heap budgets (e.g., 192MB), high space complexity causes immediate `OutOfMemoryError` crashes.\n\n"
            "3. **The Engineering Trade-off**:\n"
            "   - Algorithmic design frequently balances space and time: pre-indexing lists into HashMaps trades heap allocation for $O(1)$ lookups, whereas two-pointer techniques on sorted arrays achieve $O(1)$ space at the expense of upfront sorting time."
        ),
        "deep_answer": (
            "From an Android systems runtime and hardware perspective, space and time complexity interact non-linearly:\n\n"
            "1. **Memory Allocation is Time Complexity**: In theoretical computer science, memory allocation is treated as $O(1)$ space. On the Android ART runtime, allocating 100,000 small wrapper objects in a loop allocates memory fast, but immediately triggers ART Concurrent Copying (CC) Garbage Collection. The GC work steals CPU cycles from the UI thread, meaning that high auxiliary space directly manifests as severe time latency and frame drops.\n\n"
            "2. **CPU Cache Locality vs. Big O**: Two algorithms with identical theoretical $O(n)$ time complexity perform radically differently on mobile ARM processors. Iterating through a contiguous `IntArray` has outstanding CPU L1/L2 cache locality, whereas traversing a `LinkedList<Int>` or `HashMap<Int, Int>` causes constant pointer dereferencing and CPU cache misses, running 5–10x slower in practice despite identical asymptotic notation.\n\n"
            "3. **Android-Specific Collections**: To optimize the space-time trade-off on Android, the framework introduced `SparseArray` and `ArrayMap`. They sacrifice $O(1)$ average hash lookups for $O(\\log n)$ binary searches in primitive arrays, completely eliminating object boxing (`Integer`) and Node allocations to conserve critical mobile memory."
        ),
        "follow_ups": [
            {
                "question": "Why can high auxiliary space complexity directly degrade UI frame rendering on Android?",
                "answer": "Because rapid heap allocations trigger frequent Garbage Collection passes that preempt CPU cycles from the main thread, causing frame drops."
            },
            {
                "question": "Why does an `IntArray` iterate faster than an `ArrayList<Int>` with the same number of elements?",
                "answer": "Because `IntArray` stores unboxed primitives in contiguous memory blocks, maximizing CPU cache line hits and avoiding pointer dereferences."
            }
        ]
    },
    {
        "id": "DSA-02",
        "arabic_explanation": (
            "اشرح بالتفصيل مع أمثلة عملية من أندرويد التعقيدات الزمنية الشائعة: $O(1)$، $O(\\log n)$، $O(n)$، $O(n \\log n)$، و $O(n^2)$؟\n\n"
            "1. التعقيدات الزمنية من الأسرع إلى الأبطأ:\n"
            "   - **$O(1)$ - Constant Time (وقت ثابت)**:\n     * زمن التنفيذ مستقل تماماً عن حجم البيانات. مثال في أندرويد: جلب عنصر من مصفوفة عبر الـ Index (`array[0]`)، أو قراءة قيمة من `HashMap` بالـ Key عبر الـ Hash Code.\n   - **$O(\\log n)$ - Logarithmic Time (وقت لوغاريتمي)**:\n     * يقسم حجم البيانات إلى النصف في كل خطوة. سريع جداً حتى مع ملايين العناصر. مثال: البحث الثنائي (Binary Search)، أو البحث في `SparseArray` على أندرويد.\n   - **$O(n)$ - Linear Time (وقت خطي)**:\n     * ينمو الزمن طردياً مع حجم البيانات. مثال: حلقة تكرار بسيطة للمرور على قائمة عناصر، أو فلترة قائمة مستخدمين (`list.filter { it.isActive }`).\n   - **$O(n \\log n)$ - Linearithmic Time**:\n     * التعقيد الأمثل لخوارزميات الفرز المقارن العامة. مثال: خوارزمية الفرز المدمجة في كوتلن (`list.sorted()`) التي تعتمد على TimSort أو Dual-Pivot Quicksort.\n   - **$O(n^2)$ - Quadratic Time (وقت تربيعي)**:\n     * ينمو الزمن بشكل تربيعي؛ خطير جداً مع القوائم الكبيرة! مثال: حلقتان تكرار متداخلتان تفحص كل عنصر مقابل بقية العناصر، أو كتابة `listA.filter { itemA -> listB.contains(itemA) }` حيث كلتا القائمتين `List` عادية."
        ),
        "practical_walkthrough": (
            "أمثلة كود كوتلن تقارن بين هذه التعقيدات في معالجة بيانات شائعة:\n"
            "```kotlin\n"
            "// 1. O(1) - Constant: قراءة مباشرة من الخريطة\n"
            "val user = userCacheMap[userId] // O(1) average\n"
            "\n"
            "// 2. O(log n) - Logarithmic: بحث ثنائي في قائمة مرتبة\n"
            "val index = sortedIds.binarySearch(targetId) // O(log n)\n"
            "\n"
            "// 3. O(n) - Linear: عملية بحث خطي أو تحويل مباشر\n"
            "val names = users.map { it.fullName } // O(n)\n"
            "\n"
            "// 4. O(n log n) - Linearithmic: فرز قائمة المنتجات حسب السعر\n"
            "val sortedProducts = products.sortedBy { it.price } // O(n log n)\n"
            "\n"
            "// 5. O(n^2) - Quadratic (كارثة شائعة في أندرويد!):\n"
            "// إذا كان حجم القائمتين 10,000 عنصر، فهذا السطر ينفذ 100,000,000 مقارنة!\n"
            "val commonUsers = listA.filter { userA -> listB.contains(userA) } // O(n * m) -> O(n^2)\n"
            "\n"
            "// ✅ الإصلاح لتحويله إلى O(n):\n"
            "val setB = listB.toHashSet() // O(m) space and time\n"
            "val efficientCommon = listA.filter { userA -> setB.contains(userA) } // O(n * 1) -> O(n)\n"
            "```"
        ),
        "quick_answer": "O(1) executes in constant time regardless of size (HashMap lookup). O(log n) halves the search space each step (binary search). O(n) scales linearly with elements (list iteration). O(n log n) is standard for efficient sorting (TimSort). O(n²) grows quadratically (nested loops or nested list contains checks), causing severe UI lag.",
        "best_answer": (
            "Big O notations represent fundamental algorithmic growth curves:\n\n"
            "1. **$O(1)$ — Constant Time**:\n"
            "   - Execution time is invariant to input size. Examples include direct array indexing (`array[i]`), pushing to a stack, or average-case HashMap lookups.\n\n"
            "2. **$O(\\log n)$ — Logarithmic Time**:\n"
            "   - The operational problem space is divided by a constant factor (usually 2) at every iteration. Examples include binary search on a sorted collection and `SparseArray` lookups.\n\n"
            "3. **$O(n)$ — Linear Time**:\n"
            "   - Operations scale in direct proportion to input size. Examples include iterating through a list, computing a sum, or searching an unsorted array.\n\n"
            "4. **$O(n \\log n)$ — Linearithmic Time**:\n"
            "   - The mathematical benchmark for optimal comparison-based sorting algorithms (TimSort, MergeSort). Common in Android when sorting UI feeds via `list.sortedBy { ... }`.\n\n"
            "5. **$O(n^2)$ — Quadratic Time**:\n"
            "   - Operations scale with the square of the input size. Typically caused by nested loops over collections, or calling `list.contains()` inside a `filter()` block. With 5,000 items, $n^2$ produces 25,000,000 operations, freezing the UI thread."
        ),
        "deep_answer": (
            "In mobile systems engineering, the inflection point where higher-order curves overtake lower-order curves depends on constants and hardware:\n\n"
            "1. **Asymptotic Dominance vs. Small $n$**: For small datasets ($n < 20$), an $O(n^2)$ insertion sort or linear search through a contiguous array often runs faster than an $O(n \\log n)$ mergesort or $O(1)$ HashMap. The high constant overhead of object allocations, hash calculation, and branch mispredictions makes simple algorithms faster for tiny datasets.\n\n"
            "2. **The Hidden $O(n^2)$ in UI Diffing**: Android's `DiffUtil` runs Eugene Myers' diff algorithm with an average complexity of $O(n + d^2)$ where $d$ is the number of edits. If a dataset of 2,000 items changes drastically without stable IDs, DiffUtil calculation spikes on the CPU. Moving DiffUtil off the main thread to `Dispatchers.Default` (as in `ListAdapter` / `AsyncListDiffer`) prevents frame drops.\n\n"
            "3. **Big O Exponential Danger ($O(2^n)$ / $O(n!)$)**: Algorithms with exponential complexity (unmemoized recursive backtracking or naive permission permutations) freeze client devices completely even with $n=30$. Detecting and bounding these paths via dynamic programming is critical."
        ),
        "follow_ups": [
            {
                "question": "How can calling `listA.filter { listB.contains(it) }` degrade to $O(n^2)$?",
                "answer": "Because `List.contains()` is an $O(n)$ linear scan; doing that for every element in `listA` creates $n \\times n = O(n^2)$ comparisons."
            },
            {
                "question": "What is the time complexity of Kotlin's built-in `sortedBy` function?",
                "answer": "It is $O(n \\log n)$ on average and worst case, backed by TimSort."
            }
        ]
    },
    {
        "id": "DSA-03",
        "arabic_explanation": (
            "لماذا يتم تجاهل الثوابت الرياضية (Constants) والحدود الدنيا (Lower-Order Terms) في التحليل المقارب (Asymptotic Analysis)؟\n\n"
            "1. جوهر التحليل المقارب (The Core Principle):\n"
            "   - التحليل المقارب (Big O) يهدف إلى دراسة **سلوك الخوارزمية عندما يقترب حجم المدخلات من اللانهاية ($n \\to \\infty$)**.\n   - عندما يكبر $n$ بشكل هائل، يصبح الحد الأعلى (Highest-Order Term) هو المهيمن تماماً على معدل نمو العمليات، بينما تفقد الثوابت والحدود الدنيا أي تأثير معنوي.\n\n"
            "2. إهمال الحدود الدنيا (Lower-Order Terms):\n"
            "   - تخيل دالة تعقيد: $f(n) = n^2 + 1000n$.\n   - عندما يكون $n = 1,000,000$:\n     * $n^2 = 1,000,000,000,000$ (تريليون عملية!).\n     * $1000n = 1,000,000,000$ (مليار عملية، أي 0.1% فقط من الإجمالي!).\n   - بالتالي فإن $n^2$ هو الذي يحدد قابلية النظام للتوسع (Scalability)، ونهمل $1000n$ ونقول التعقيد هو $O(n^2)$.\n\n"
            "3. إهمال الثوابت (Constants):\n"
            "   - $O(2n)$ و $O(100n)$ كلاهما يعاملان كـ $O(n)$.\n   - السبب: الثوابت تتأثر بنوع لغة البرمجة، وسرعة المعالج (CPU Clock Speed)، ومترجم الـ Bytecode، وليس بطبيعة الخوارزمية نفسها. الخوارزمية ذات التعقيد $O(n)$ ستتفوق حتماً على أي خوارزمية $O(n^2)$ عند أحجام بيانات كبيرة، بغض النظر عن قيمة الثابت.\n\n"
            "4. التحذير الهندسي العملي:\n"
            "   - إهمال الثوابت هو **تبسيط نظري**. في الحياة الواقعية على أجهزة أندرويد ذات الموارد المحدودة، الثابت مهم جداً عندما يكون $n$ صغيراً؛ خوارزمية $O(1)$ مع ثابت ضخم (مثل 200ms اتصال شبكة) أسوأ بكثير من $O(n)$ مع ثابت ميكروثانية!"
        ),
        "practical_walkthrough": (
            "مثال يوضح لماذا الخوارزمية ذات الرتبة الأقل تتفوق حتماً مع نمو البيانات:\n"
            "```kotlin\n"
            "// الخوارزمية A: f(n) = 100 * n  -> O(n)\n"
            "// الخوارزمية B: g(n) = 2 * n^2  -> O(n^2)\n"
            "\n"
            "// جدول مقارنة عدد العمليات الحسابية مع نمو حجم المدخلات n:\n"
            "// n = 10    -> A: 1,000 operations | B: 200 operations   (B أسرع للقيم الصغيرة!)\n"
            "// n = 50    -> A: 5,000 operations | B: 5,000 operations (نقطة التعادل)\n"
            "// n = 1,000 -> A: 100,000 ops      | B: 2,000,000 ops    (A أسرع بـ 20 ضعفاً!)\n"
            "// n = 10,000-> A: 1,000,000 ops    | B: 200,000,000 ops  (A أسرع بـ 200 ضعف!)\n"
            "\n"
            "fun compareGrowth() {\n"
            "    // هذا يثبت رياضياً لماذا نهمل الثابت 100 والثابت 2 في التحليل المقارب:\n"
            "    // الرتبة التربيعية تنفجر وتدمر الأداء عندما تكبر البيانات!\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Constants and lower-order terms are dropped in asymptotic analysis because Big O measures the growth rate as input size approaches infinity. At scale, the highest-order term completely dominates execution time, while constants depend on machine hardware and compiler optimizations rather than intrinsic algorithmic scalability.",
        "best_answer": (
            "Asymptotic analysis focuses on the limiting behavior of functions as inputs scale toward infinity ($n \\to \\infty$):\n\n"
            "1. **Dominance of Highest-Order Terms**:\n"
            "   - Given an algorithm with operational steps $f(n) = 3n^3 + 50n^2 + 1000n + 4000$, as $n$ scales to millions, the $n^3$ term accounts for greater than 99.99% of total computation. Lower-order terms ($n^2, n, \\text{constants}$) become statistically insignificant.\n\n"
            "2. **Machine and Platform Independence**:\n"
            "   - Constant factors (e.g. $c \\cdot n$) vary widely across execution environments: CPU clock speed, hardware memory bus bandwidth, JIT compiler optimizations, and ARM vs x86 instruction sets. Big O abstracts away hardware discrepancies to categorize the fundamental mathematical scalability of the algorithm.\n\n"
            "3. **Practical Engineering Caveat**:\n"
            "   - In mobile client development, data sizes are frequently bounded ($n \\le 100$). In bounded spaces, constants matter tremendously: an $O(n)$ algorithm that allocates 100 heavy objects in each iteration will run slower and cause more GC pauses than an $O(n \\log n)$ primitive array sort."
        ),
        "deep_answer": (
            "From an engineering architecture perspective, ignoring constants can lead to catastrophic real-world mobile choices:\n\n"
            "1. **The 'Hidden Constant' Trap**: Consider an $O(1)$ operation that performs a synchronous disk read or SQLite transaction on the main thread. Theoretically it is constant time $O(1)$, but the constant $c \\approx 15\\text{ms}$ drops frames immediately. Conversely, an $O(n)$ in-memory scan of a 100-element primitive array takes $0.005\\text{ms}$. Developers must never prioritize theoretical Big O over real wall-clock latency.\n\n"
            "2. **Amortized Analysis Constants**: In resizable data structures like `ArrayList`, inserting an item is amortized $O(1)$. However, when the internal buffer reaches capacity, it reallocates a new array with $1.5\\times$ size and copies all elements, incurring an $O(n)$ spike. On the main thread, that sudden spike can stutter an ongoing Compose scroll gesture.\n\n"
            "3. **Algorithmic Threshold Switching**: Advanced libraries leverage both concepts: Java/Kotlin's TimSort switches from MergeSort ($O(n \\log n)$) to Binary Insertion Sort ($O(n^2)$) whenever sub-arrays drop below 32 elements, explicitly exploiting low constants on small inputs."
        ),
        "follow_ups": [
            {
                "question": "Can an algorithm with $O(n^2)$ complexity run faster than an $O(n)$ algorithm in production?",
                "answer": "Yes, for small inputs where the constant factor of the $O(n)$ algorithm (like object allocation or disk I/O) exceeds the operations of $O(n^2)$."
            },
            {
                "question": "Why does TimSort switch to insertion sort for arrays with fewer than 32 elements?",
                "answer": "Because insertion sort has very low overhead and cache friendly constants that beat mergesort on small datasets."
            }
        ]
    },
    {
        "id": "DSA-04",
        "arabic_explanation": (
            "هل يصف رمز Big O الحالة الأسوأ (Worst Case) بالضرورة؟ اشرح الفرق بين الحدود العليا (Upper Bounds) وحالات التنفيذ (Best, Average, Worst)؟\n\n"
            "1. المفهوم الخاطئ الشائع (The Common Myth):\n"
            "   - يعتقد الكثيرون خطأً أن Big O يعني دائماً \"الحالة الأسوأ\" (Worst Case). **هذا غير صحيح رياضياً!**\n   - **Big O ($O$)** يمثل **الحد الأعلى الرياضي (Asymptotic Upper Bound)** لدالة معينة.\n   - يمكنك حساب Big O للحالة الفضلى (Best Case)، أو المتوسطة (Average Case)، أو الأسوأ (Worst Case).\n\n"
            "2. الرموز الرياضية المقاربة (Asymptotic Notations):\n"
            "   - **Big O ($O$)**: الحد الأعلى (Upper Bound) — \"الخوارزمية لن تنمو بمعدل أسرع من هذه الدالة\".\n   - **Big Omega ($\\Omega$)**: الحد الأدنى (Lower Bound) — \"الخوارزمية لن تنمو بمعدل أبطأ من هذه الدالة\".\n   - **Big Theta ($\\Theta$)**: الحد المحكم (Tight Bound) — عندما يتطابق الحد الأعلى والحد الأدنى تماماً.\n\n"
            "3. حالات التنفيذ (Execution Cases):\n"
            "   - **Best Case (الحالة الفضلى)**: أقل عدد خطوات ممكن في أفضل مدخلات (مثلاً: البحث الخطي يجد العنصر في أول موضع -> Best case: $O(1)$).\n   - **Average Case (الحالة المتوسطة)**: السلوك المتوقع على مدخلات عشوائية.\n   - **Worst Case (الحالة الأسوأ)**: أقصى عدد خطوات ممكن على أسوأ مدخلات ممكنة (مثلاً: البحث الخطي لا يجد العنصر إلا في آخر موضع أو لا يجده إطلاقاً -> Worst case: $O(n)$)."
        ),
        "practical_walkthrough": (
            "تطبيق عملي يوضح الفوارق عبر خوارزمية Quicksort الشهيرة:\n"
            "```kotlin\n"
            "// تحليل خوارزمية Quicksort القياسية:\n"
            "// 1. Best Case: Pivot يقسم المصفوفة لنصفين متساويين في كل خطوة -> O(n log n)\n"
            "// 2. Average Case: توزيع عشوائي للبيانات -> O(n log n)\n"
            "// 3. Worst Case: مصفوفة مرتبة بالفعل واختيار أسوأ Pivot دائماً -> O(n^2)!\n"
            "\n"
            "// مثال آخر: البحث الخطي (Linear Search)\n"
            "fun findIndex(list: List<String>, target: String): Int {\n"
            "    for (i in list.indices) {\n"
            "        if (list[i] == target) return i // Best case: target هو أول عنصر -> O(1)\n"
            "    }\n"
            "    return -1 // Worst case: target غير موجود أو آخر عنصر -> O(n)\n"
            "}\n"
            "```"
        ),
        "quick_answer": "No, Big O does not inherently mean worst case. Big O is a mathematical upper bound that can describe best, average, or worst cases. For example, QuickSort has a best-case upper bound of O(n log n) and a worst-case upper bound of O(n²).",
        "best_answer": (
            "Disentangling asymptotic bounds from execution cases is a core computer science distinction:\n\n"
            "1. **Asymptotic Bounds vs. Algorithmic Cases**:\n"
            "   - **Cases (Inputs)**: Best, Average, and Worst describe the nature of input distribution (e.g., already sorted vs. completely inverted inputs).\n   - **Bounds (Mathematical Limits)**: Big O ($O$) is an asymptotic upper bound, Big Omega ($\\Omega$) is a lower bound, and Big Theta ($\\Theta$) is a tight bound.\n\n"
            "2. **Applying Big O to Different Cases**:\n"
            "   - One can analyze the Big O upper bound of any input case:\n     - Linear Search: Best Case is $O(1)$ (target at index 0); Worst Case is $O(n)$ (target absent).\n     - QuickSort: Average Case is $O(n \\log n)$; Worst Case (pathological pivot choice) is $O(n^2)$.\n     - Insertion Sort: Best Case (pre-sorted input) is $O(n)$; Worst Case is $O(n^2)$.\n\n"
            "3. **Industry Colloquialism**:\n"
            "   - In everyday engineering interviews, 'Big O' is frequently used as shorthand for 'the tightest upper bound of the worst-case scenario', but senior engineers recognize that Big O mathematically characterizes bounds across all execution cases."
        ),
        "deep_answer": (
            "From an engineering reliability and SLA standpoint, relying solely on average-case analysis can be fatal in production:\n\n"
            "1. **The Hash Collision DoS Attack (Worst-Case Exploitation)**: A standard `HashMap` lookup has an average case of $O(1)$. However, its worst case is $O(n)$ if all keys hash to the same bucket. Malicious actors can exploit this by crafting thousands of distinct keys with identical hash codes (hash collision attacks), forcing an Android backend parser or client cache to degrade into an $O(n^2)$ linked list traversal, causing Denial of Service.\n\n"
            "2. **Java 8+ Treeification Defense**: To defend against worst-case $O(n)$ hash collisions, the JVM HashMap implementation automatically transforms collision buckets exceeding 8 nodes into balanced Red-Black Trees (`TreeNode`), capping the worst-case lookup at $O(\\log n)$ rather than $O(n)$.\n\n"
            "3. **Designing for Real-Time Mobile Systems**: In UI rendering and audio synthesis threads, guarantees must be made against the **worst case**. If an algorithm runs in $O(1)$ average time but occasionally hits an $O(n)$ stop-the-world worst case, the user will experience audible pops or visual animation freezes."
        ),
        "follow_ups": [
            {
                "question": "What is the difference between Big O and Big Theta?",
                "answer": "Big O provides an asymptotic upper bound (cannot grow faster than), whereas Big Theta provides a tight bound (grows at the exact same rate from above and below)."
            },
            {
                "question": "How does Java 8+ prevent worst-case $O(n)$ performance in HashMaps with high collisions?",
                "answer": "It converts bins with more than 8 colliding nodes into Red-Black balanced trees, capping lookup complexity at $O(\\log n)$."
            }
        ]
    },
    {
        "id": "DSA-05",
        "arabic_explanation": (
            "قارن بين هياكل البيانات الأساسية: Arrays، Linked Lists، Stacks، Queues، HashMaps، و Sets من حيث الأداء وحالات الاستخدام في أندرويد؟\n\n"
            "1. مقارنة شاملة للتعقيد (Time & Space Complexity):\n"
            "   - **Array / ArrayList**:\n     * Access by Index: $O(1)$\n     * Insert/Delete at end: $O(1)$ amortized\n     * Insert/Delete in middle: $O(n)$ (يتطلب إزاحة العناصر)\n     * الذاكرة: ممتازة جداً (Contiguous Memory) وموفرة ومثالية للـ CPU Cache.\n   - **LinkedList**:\n     * Access by Index: $O(n)$ (يجب المرور من البداية عقدة بعقدة)\n     * Insert/Delete at head/tail: $O(1)$\n     * الذاكرة: سيئة في أندرويد؛ كل عنصر يخصص كائن `Node` إضافي مع مؤشرين، مما يسبب تجزئة الذاكرة وضعف الكاش.\n   - **Stack (LIFO - Last In First Out)**:\n     * Push/Pop: $O(1)$\n     * استخدام أندرويد: إدارة شاشات التنقل (BackStack) وإلغاء العمليات (Undo buffer).\n   - **Queue (FIFO - First In First Out)**:\n     * Enqueue/Dequeue: $O(1)$\n     * استخدام أندرويد: معالجة الرسائل والمهام في الـ `Looper` و `MessageQueue` وجدولة WorkManager.\n   - **HashMap / HashSet**:\n     * Search/Insert/Delete: $O(1)$ average ($O(n)$ worst-case)\n     * الذاكرة: تستهلك حجماً إضافياً للـ Buckets وعقد الـ Entry."
        ),
        "practical_walkthrough": (
            "جدول مقارنة الأداء ومثال عملي لاختيار الهيكل الأنسب في أندرويد:\n"
            "```kotlin\n"
            "// جدول التعقيد السريع:\n"
            "// Structure   | Read by Key/Index | Insert Head | Insert Tail | Memory Efficiency\n"
            "// Array       | O(1)              | O(n)        | O(1)        | High (Contiguous)\n"
            "// LinkedList  | O(n)              | O(1)        | O(1)        | Low (Node objects)\n"
            "// HashMap     | O(1) (Key)        | O(1)        | O(1)        | Medium (Buckets)\n"
            "// HashSet     | O(1) (Contains)   | O(1)        | O(1)        | Medium\n"
            "\n"
            "// مثال: استخدام ArrayDeque بدلاً من Stack أو LinkedList (أسرع وأوفر في الذاكرة):\n"
            "val navigationStack = ArrayDeque<String>()\n"
            "navigationStack.addLast(\"home_screen\") // Push O(1)\n"
            "navigationStack.addLast(\"profile_screen\")\n"
            "val currentScreen = navigationStack.removeLast() // Pop O(1)\n"
            "```"
        ),
        "quick_answer": "Arrays offer O(1) indexed access with optimal cache locality but O(n) middle insertions. LinkedLists provide O(1) head/tail insertions but O(n) search and poor memory overhead. Stacks (LIFO) and Queues (FIFO) provide O(1) push/pop. HashMaps and Sets provide average O(1) lookups via hashing at the cost of higher memory overhead.",
        "best_answer": (
            "Selecting the correct data structure balances computational time complexity against memory and cache efficiency:\n\n"
            "1. **Arrays and ArrayLists**:\n"
            "   - Constant $O(1)$ random access by index. Insertion at end is amortized $O(1)$, while arbitrary insertions require $O(n)$ element shifting. Stored contiguously in memory, yielding optimal CPU cache locality and zero node overhead.\n\n"
            "2. **LinkedLists**:\n"
            "   - Constant $O(1)$ insertion and deletion given a node reference, but $O(n)$ indexed access. In Android, `LinkedList` is generally discouraged because each entry allocates a separate `Node` object, causing memory bloat, GC churn, and cache misses.\n\n"
            "3. **Stacks and Queues**:\n"
            "   - Stack enforces LIFO; Queue enforces FIFO. Both operate with $O(1)$ enqueue/dequeue operations. In modern Kotlin/Android, `ArrayDeque` is the preferred implementation for both, outperforming legacy `java.util.Stack` and `LinkedList`.\n\n"
            "4. **HashMaps and Sets**:\n"
            "   - Provide average-case $O(1)$ search, insertion, and deletion via hash tables. They trade increased memory overhead (bucket arrays, load factors, collision nodes) for fast key-based retrieval."
        ),
        "deep_answer": (
            "From an Android internals and memory allocation perspective, standard Java collections present hidden traps:\n\n"
            "1. **The Vector / Stack Synchronization Penalty**: The legacy `java.util.Stack` inherits from `Vector`, meaning every single push and pop synchronizes on a monitor lock. In single-threaded Android UI backstack operations, this introduces pointless synchronization overhead. Always prefer `ArrayDeque`.\n\n"
            "2. **Android Primitive Sparse Collections**: Storing a mapping of `Int` to `User` in `HashMap<Int, User>` requires boxing every primitive key into a `java.lang.Integer` object, allocating 16 to 24 bytes per key on the heap. Android's native `SparseArray<User>` uses two parallel arrays (`int[]` and `Object[]`) with binary search lookup ($O(\\log n)$), eliminating all autoboxing and significantly slashing GC pressure.\n\n"
            "3. **Circular ArrayDeque Performance**: `ArrayDeque` uses a circular array buffer that automatically resizes without shifting elements on remove. It serves as both stack and queue with virtually zero garbage creation compared to linked implementations."
        ),
        "follow_ups": [
            {
                "question": "Why is `ArrayDeque` preferred over `LinkedList` for queue and stack implementations in Android?",
                "answer": "Because `ArrayDeque` uses a contiguous resizable circular array, avoiding the per-element `Node` object allocations and cache misses of `LinkedList`."
            },
            {
                "question": "What memory optimization does Android's `SparseArray` provide over `HashMap<Int, V>`?",
                "answer": "It avoids autoboxing primitive integer keys into `Integer` wrapper objects, storing keys in a raw `int[]` to reduce memory and GC overhead."
            }
        ]
    },
    {
        "id": "DSA-06",
        "arabic_explanation": (
            "ما هو التعقيد الزمني لعمليات البحث في الـ HashMap في الحالة المتوسطة (Average Case) والحالة الأسوأ (Worst Case)، ولماذا؟\n\n"
            "1. كيف تعمل الـ HashMap في الذاكرة؟\n"
            "   - تعتمد على مصفوفة داخلية من الـ Buckets.\n   - عند البحث عن مفتاح (`get(key)`):\n     1. تحسب الـ Hash Code للمفتاح: `hash = key.hashCode()`.\n     2. تحدد موقع الـ Bucket: `index = hash & (n - 1)`.\n     3. تفحص العناصر الموجودة داخل الـ Bucket لمطابقة المفتاح عبر `equals()`.\n\n"
            "2. الحالة المتوسطة (Average Case: $O(1)$):\n"
            "   - عندما تكون دالة الـ `hashCode()` جيدة وموزعة بانتظام، تتوزع المفاتيح بالتساوي عبر الـ Buckets.\n   - معظم الـ Buckets تحتوي على عنصر واحد فقط (بدون تصادمات أو تصادمات ضئيلة جداً $O(1)$)، ويتم العثور على القيمة فوراً في وقت ثابت $O(1)$.\n\n"
            "3. الحالة الأسوأ (Worst Case):\n"
            "   - **في Java 7 والإصدارات القديمة ($O(n)$)**:\n     * إذا أنتجت جميع المفاتيح نفس الـ Hash Code تماماً (Pathological Collisions)، تتجمع كل العناصر داخل Bucket واحد كـ Linked List طويلة. البحث عن عنصر يتطلب المرور الخطي على جميع العناصر $O(n)$!\n   - **في Java 8 وما بعدها على أندرويد ($O(\\log n)$)**:\n     * عند تجاوز عدد التصادمات داخل الـ Bucket الواحد عتبة معينة (TREEIFY_THRESHOLD = 8)، تتحول القائمة المرتبطة تلقائياً إلى **شجرة حمراء-سوداء متوازنة (Red-Black Tree)**، مما يضمن أن أسوأ تعقيد للبحث لن يتجاوز $O(\\log n)$."
        ),
        "practical_walkthrough": (
            "مثال عملي يوضح كيف يمكن لكود Kotlin سيئ أن يدمر أداء الـ HashMap ويحولها لـ $O(n)$ أو $O(\\log n)$:\n"
            "```kotlin\n"
            "// ❌ كارثة: دالة hashCode تعيد نفس الرقم دائماً (تصادم 100%!):\n"
            "class BadKey(val id: String) {\n"
            "    override fun hashCode(): Int = 42 // كل المفاتيح تذهب لنفس الـ Bucket!\n"
            "    override fun equals(other: Any?): Boolean = (other as? BadKey)?.id == id\n"
            "}\n"
            "\n"
            "// ✅ التصميم الهندسي الصحيح: توزيع متجانس للمفاتيح:\n"
            "data class GoodKey(val id: String) {\n"
            "    // Kotlin Data Class تولد hashCode() ممتاز يوزع المفاتيح بانتظام عبر الـ Buckets:\n"
            "    // مما يضمن أداء بحث O(1) حقيقي في 99.9% من الحالات.\n"
            "}\n"
            "\n"
            "fun benchmark() {\n"
            "    val badMap = HashMap<BadKey, String>()\n"
            "    // إضافة 10,000 عنصر هنا سيجعل البحث بطيئاً جداً (O(log n) بدلاً من O(1))\n"
            "}\n"
            "```"
        ),
        "quick_answer": "HashMap lookup is O(1) on average because a well-distributed hashCode maps keys directly to unique bucket indices. In the worst case with high collisions, Java 7 degrades to O(n) via linked lists, while modern Java 8+ and Android ART caps worst-case lookup at O(log n) by converting buckets exceeding 8 nodes into balanced Red-Black trees.",
        "best_answer": (
            "The performance characteristics of HashMap lookups derive from hash table bucket distribution:\n\n"
            "1. **Average Case — $O(1)$**:\n"
            "   - When keys provide a uniform hash distribution, computing `key.hashCode()` and modulating it against bucket array size yields a deterministic index. Because each bucket contains approximately $\\le 1$ element on average (governed by the load factor, typically 0.75), retrieving the entry takes constant time $O(1)$.\n\n"
            "2. **Worst Case in Java 7 — $O(n)$**:\n"
            "   - If all keys hash to the identical bucket index due to poor hash functions or deliberate hash collision attacks, all entries are stored in a single linked list. Finding an element requires linear traversal comparing keys via `equals()`, degrading lookup to $O(n)$.\n\n"
            "3. **Worst Case in Java 8+ / Modern ART — $O(\\log n)$**:\n"
            "   - To prevent catastrophic degradation, modern runtimes introduce **bucket treeification**. When a bucket exceeds 8 entries (`TREEIFY_THRESHOLD`) and the table exceeds 64 buckets, the bucket converts from a singly-linked list into a balanced Red-Black tree (`TreeNode`), capping worst-case search complexity at $O(\\log n)$."
        ),
        "deep_answer": (
            "From an Android performance and memory optimization standpoint, several nuances govern HashMaps:\n\n"
            "1. **The Rehash Resize Penalty**: When the number of entries exceeds `capacity * loadFactor` (e.g. 16 * 0.75 = 12 entries), HashMap doubles its internal bucket array (e.g. 16 to 32) and rehashes every existing entry into new bucket positions. If inserting 100,000 items without an initial capacity, the map resizes ~14 times, producing massive garbage and execution spikes. Always specify initial capacity: `HashMap(expectedSize / 0.75f + 1)`.\n\n"
            "2. **Mutable Key Mutation Trap**: If an object is used as a HashMap key and its mutable properties change after insertion, its `hashCode()` changes. Calling `map[key]` computes a new bucket index, rendering the previously inserted value permanently unfindable (a silent memory leak).\n\n"
            "3. **Memory Footprint**: A standard `HashMap` entry requires a `Node` object with 4 references (hash, key, value, next), taking 32 bytes on 64-bit ART plus the key and value objects themselves. For integer keys, `SparseArray` cuts this memory by over 60%."
        ),
        "follow_ups": [
            {
                "question": "Why should you pass an initial capacity to a HashMap when the expected size is known?",
                "answer": "To prevent repeated bucket array doubling and rehashing passes, reducing CPU time and memory allocation churn."
            },
            {
                "question": "What happens if you mutate an object that is used as a key in a HashMap?",
                "answer": "Its hashCode changes, meaning lookups will check the wrong bucket and fail to find the entry, causing data loss and memory leaks."
            }
        ]
    },
    {
        "id": "DSA-07",
        "arabic_explanation": (
            "ما هو البحث الثنائي (Binary Search)، وما هو الشرط الأساسي لتطبيقه، وكيف يعمل برمجياً؟\n\n"
            "1. ما هو البحث الثنائي وكيف يعمل؟\n"
            "   - خوارزمية بحث عالية الكفاءة تعمل بتعقيد زمني لوغاريتمي **$O(\\log n)$**.\n   - في كل خطوة، تقارن العنصر المستهدف (Target) بالعنصر الموجود في منتصف النطاق (Middle element):\n     * إذا كان متطابقاً، ينتهي البحث بنجاح.\n     * إذا كان الهدف أصغر من المنتصف، يتم استبعاد النصف الأيمن بالكامل والبحث في النصف الأيسر فقط.\n     * إذا كان الهدف أكبر من المنتصف، يتم استبعاد النصف الأيسر بالكامل والبحث في النصف الأيمن فقط.\n   - بهذه الطريقة، يمكن البحث بين 1,000,000 عنصر في 20 خطوة فقط!\n\n"
            "2. الشرط المسبق الإلزامي (The Strict Precondition):\n"
            "   - **يجب أن تكون البيانات مرتبة تماماً (Sorted Collection)**، وتدعم **الوصول العشوائي السريع في وقت ثابت (Random Access - $O(1)$)** مثل الـ Arrays أو الـ ArrayList.\n   - إذا كانت القائمة غير مرتبة، فإن البحث الثنائي سيعطي نتائج خاطئة تماماً.\n   - إذا طُبق البحث الثنائي على `LinkedList`، سيفقد ميزته لأن الوصول لعنصر المنتصف يستغرق $O(n)$، مما يجعل التعقيد الإجمالي ينحدر إلى $O(n)$!\n\n"
            "3. خطأ الـ Integer Overflow الشهير:\n"
            "   - كتابة `val mid = (low + high) / 2` تسبب Bug شهير إذا كان مجموع الرقمين أكبر من `Int.MAX_VALUE` ($2^{31}-1$).\n   - الحل الهندسي الصحيح: `val mid = low + (high - low) / 2` أو `val mid = (low + high) ushr 1`."
        ),
        "practical_walkthrough": (
            "كتابة خوارزمية Binary Search خالية من ثغرة الـ Integer Overflow في كوتلن:\n"
            "```kotlin\n"
            "fun binarySearch(sortedList: IntArray, target: Int): Int {\n"
            "    var low = 0\n"
            "    var high = sortedList.size - 1\n"
            "\n"
            "    while (low <= high) {\n"
            "        // ✅ تفادي طفح الأرقام الصحيحة (Integer Overflow Safe):\n"
            "        val mid = low + (high - low) / 2\n"
            "        val midVal = sortedList[mid]\n"
            "\n"
            "        when {\n"
            "            midVal == target -> return mid // تم العثور على العنصر بنجاح!\n"
            "            midVal < target -> low = mid + 1 // الهدف في النصف الأيمن\n"
            "            else -> high = mid - 1 // الهدف في النصف الأيسر\n"
            "        }\n"
            "    }\n"
            "    return -1 // العنصر غير موجود\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Binary search is an O(log n) search algorithm that repeatedly halves the search interval by comparing the target with the middle element. Its strict precondition is that the underlying collection must be pre-sorted and support O(1) random indexed access, such as an array.",
        "best_answer": (
            "Binary search is the quintessential logarithmic search algorithm:\n\n"
            "1. **Core Mechanism**:\n"
            "   - At each iteration, the algorithm inspects the middle element of the active range. If the target matches, the search concludes. If the target is smaller, the upper boundary moves to `mid - 1`; if larger, the lower boundary moves to `mid + 1`. This reduces the remaining problem space by $50\\%$ at every step, yielding an $O(\\log n)$ time complexity.\n\n"
            "2. **Strict Preconditions**:\n"
            "   - **Ordered Data**: The elements must be sorted according to a defined Comparator.\n   - **Constant-Time Random Access**: The data structure must support $O(1)$ random indexing (`Array`, `ArrayList`, `IntArray`). Executing binary search on a `LinkedList` degrades performance to $O(n)$ because locating the midpoint requires linear traversal.\n\n"
            "3. **Implementation Rigor**:\n"
            "   - In production implementations, avoid `(low + high) / 2` due to integer overflow risks when `low + high > Int.MAX_VALUE`. Use `low + (high - low) / 2` or unsigned bit-shift `(low + high) ushr 1`."
        ),
        "deep_answer": (
            "From an Android architectural perspective, binary search underpins core framework optimizations:\n\n"
            "1. **Android Framework SparseArray**: Android's `SparseArray<E>` and `LongSparseArray<E>` store primitive keys in a tightly packed `int[]` or `long[]`. Every `get(key)` invocation performs a binary search via `ContainerHelpers.binarySearch(mKeys, mSize, key)`. It sacrifices $O(1)$ hash table lookups for $O(\\log n)$ searches to achieve zero heap object allocations.\n\n"
            "2. **Kotlin Built-in `binarySearch` Contract**: Kotlin's `collections.binarySearch()` returns the index if found. If not found, it returns `-(insertionPoint + 1)`. This negative return value allows callers to locate the exact position where the missing element should be inserted while maintaining sorted order, enabling efficient sorted insertions.\n\n"
            "3. **Binary Search on Answer Space**: Beyond searching static arrays, senior engineers apply binary search to find optimal configuration thresholds: e.g. finding the maximum readable font size in a custom Canvas view that fits bounded dimensions without line wrapping."
        ),
        "follow_ups": [
            {
                "question": "Why does calculating midpoint as `(low + high) / 2` introduce a bug?",
                "answer": "If `low + high` exceeds `Int.MAX_VALUE` ($2^{31} - 1$), integer overflow occurs, resulting in a negative number and an `ArrayIndexOutOfBoundsException`."
            },
            {
                "question": "What does a negative return value from Kotlin's `binarySearch()` represent?",
                "answer": "It represents `-(insertionPoint + 1)`, indicating the item was not found but specifying the exact index where it should be inserted."
            }
        ]
    },
    {
        "id": "DSA-08",
        "arabic_explanation": (
            "كيف تكتشف وتزيل العناصر المكررة (Duplicates) بكفاءة عالية في قائمة ضخمة في أندرويد؟\n\n"
            "1. تحليل الخيارات الهندسية للكشف عن التكرار:\n"
            "   - **الخيار 1: البحث الثنائي المتداخل (Naive Nested Loops)**:\n     * مقارنة كل عنصر ببقية العناصر.\n     * التعقيد: **$O(n^2)$ Time, $O(1)$ Space** — غير مقبول تماماً مع القوائم الضخمة!\n   - **الخيار 2: استخدام الـ HashSet (الأسرع زمناً)**:\n     * المرور على القائمة وإضافة العناصر إلى `HashSet`، أو استخدام `list.distinct()`.\n     * التعقيد: **$O(n)$ Time, $O(n)$ Space**.\n     * المميزات: سريع جداً ومناسب لمعظم الحالات.\n     * العيب في أندرويد: يستهلك ذاكرة إضافية لكل عنصر على الـ Heap.\n   - **الخيار 3: الفرز الموضعي ثم الفحص المتجاور (In-Place Sort + Linear Scan)**:\n     * فرز القائمة أولاً (`list.sort()`)، ثم المرور بخطوة واحدة لمقارنة كل عنصر بمجاوره (`array[i] == array[i-1]`).\n     * التعقيد: **$O(n \\log n)$ Time, $O(1)$ Auxiliary Space**.\n     * الاستخدام: مثالي عندما تكون الذاكرة محدودة جداً وتمنع تخصيص `Set` إضافي.\n\n"
            "2. التعامل مع الكائنات المعقدة في أندرويد:\n"
            "   - عند إزالة التكرار من قائمة نماذج (`List<Product>`) بناءً على المعرف (`id`) فقط، نستخدم `distinctBy { it.id }` التي تحتفظ بأول عنصر ظهر فقط."
        ),
        "practical_walkthrough": (
            "طرق كوتلن الفعالة لاكتشاف وإزالة التكرار مع الحفاظ على الأداء والذاكرة:\n"
            "```kotlin\n"
            "data class User(val id: Long, val name: String)\n"
            "\n"
            "// 1. الطريقة الأسرع والأكثر شيوعاً (O(n) time, O(n) space):\n"
            "fun removeDuplicatesFast(users: List<User>): List<User> {\n"
            "    return users.distinctBy { it.id }\n"
            "}\n"
            "\n"
            "// 2. الكشف عن المكررات فقط وحفظها (O(n) time, O(n) space):\n"
            "fun findDuplicates(items: List<String>): Set<String> {\n"
            "    val seen = HashSet<String>()\n"
            "    val duplicates = HashSet<String>()\n"
            "    for (item in items) {\n"
            "        if (!seen.add(item)) {\n"
            "            duplicates.add(item) // تم رصده مسبقاً، إذاً هو مكرر!\n"
            "        }\n"
            "    }\n"
            "    return duplicates\n"
            "}\n"
            "\n"
            "// 3. الطريقة الصديقة للذاكرة الصارمة (O(n log n) time, O(1) extra space):\n"
            "fun removeDuplicatesInPlace(primitiveIds: LongArray): Int {\n"
            "    primitiveIds.sort() // فرز موضعي O(n log n)\n"
            "    if (primitiveIds.isEmpty()) return 0\n"
            "    var uniqueIndex = 0\n"
            "    for (i in 1 until primitiveIds.size) {\n"
            "        if (primitiveIds[i] != primitiveIds[uniqueIndex]) {\n"
            "            uniqueIndex++\n"
            "            primitiveIds[uniqueIndex] = primitiveIds[i]\n"
            "        }\n"
            "    }\n"
            "    return uniqueIndex + 1 // عدد العناصر الفريدة، بدون تخصيص أي كائن على الـ Heap!\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Detect duplicates in O(n) time and O(n) space by inserting elements into a HashSet, where set.add() returning false identifies a duplicate. For memory-constrained environments where allocating a Set would risk OOM, sort the collection in-place in O(n log n) time and scan adjacent elements in O(1) auxiliary space.",
        "best_answer": (
            "Deduplicating large collections involves choosing between time-optimized and memory-constrained paradigms:\n\n"
            "1. **Time-Optimized Hash Table Approach ($O(n)$ Time, $O(n)$ Space)**:\n"
            "   - Iterate through the list while streaming elements into a `HashSet`. Since `HashSet.add()` returns `false` if the item already exists, duplicates are detected in a single linear pass. In Kotlin, `list.distinct()` or `list.distinctBy { it.id }` encapsulates this pattern.\n\n"
            "2. **Memory-Constrained Sorting Approach ($O(n \\log n)$ Time, $O(1)$ Space)**:\n"
            "   - If working with a huge dataset on a memory-constrained Android device where allocating a 100,000-entry HashSet would trigger an `OutOfMemoryError`, sort the primitive array in-place using dual-pivot quicksort, then run a single two-pointer linear pass comparing adjacent neighbors (`arr[i] == arr[i-1]`).\n\n"
            "3. **Preserving Insertion Order**:\n"
            "   - If the original order of first appearance must be preserved, Kotlin's `distinct()` uses a `LinkedHashSet` internally, retaining first-seen ordering while filtering subsequent occurrences."
        ),
        "deep_answer": (
            "In large scale mobile architecture, deduplicating incoming server data feeds presents practical challenges:\n\n"
            "1. **Stream Processing via Kotlin Sequences**: For massive datasets read from Room or local files, calling `list.distinct()` creates intermediate collection allocations in memory. Using lazy sequences (`sequence.distinct()`) processes items one-by-one, streaming deduplicated records directly to the UI without holding the entire transformed dataset in heap memory simultaneously.\n\n"
            "2. **BitSet Optimization for Bounded Numeric IDs**: If the dataset consists of integer IDs within a bounded range (e.g. user IDs $< 1,000,000$), avoid `HashSet<Int>` completely. A Java `BitSet` stores one bit per ID: 1,000,000 IDs consume just $125\\text{KB}$ of RAM compared to over $32\\text{MB}$ for a boxed `HashSet<Integer>`, yielding instant duplicate detection with negligible GC footprint.\n\n"
            "3. **Probabilistic Deduplication with Bloom Filters**: In extreme offline synchronization scenarios where hundreds of thousands of sync IDs must be checked before querying disk, a Bloom Filter provides $O(1)$ constant-time duplicate checks in minimal RAM with zero false negatives."
        ),
        "follow_ups": [
            {
                "question": "Why is `BitSet` superior to `HashSet<Int>` for deduplicating bounded integer IDs?",
                "answer": "A BitSet uses a single bit per integer, consuming a fraction of the RAM (125KB for 1M IDs) with zero object boxing or GC overhead."
            },
            {
                "question": "How does `sequence.distinct()` improve performance over `list.distinct()` on huge datasets?",
                "answer": "Sequences evaluate lazily, evaluating items on-demand and preventing large intermediate list copies from cluttering the heap."
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
    for item in DSA_01_08:
        existing_dict[item["id"]] = item

    all_items = list(existing_dict.values())
    all_items.sort(key=lambda x: x["id"])

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)

    print(f"Updated {DATA_FILE} with questions DSA-01 to DSA-08. Total questions: {len(all_items)}")


if __name__ == "__main__":
    main()
