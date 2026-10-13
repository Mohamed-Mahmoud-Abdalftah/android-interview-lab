#!/usr/bin/env python3
"""Generator for MEM-01 through MEM-06 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "mem.json"

MEM_01_06 = [
    {
        "id": "MEM-01",
        "arabic_explanation": (
            "إدارة الذاكرة في Android ودور مجمع النفايات (Garbage Collector - GC) هي عصب أداء التطبيقات:\n\n"
            "1. كيف يدير نظام Android الذاكرة؟\n"
            "   - كل تطبيق يعمل داخل **Android Runtime (ART)** محدد بسقف أقصى للذاكرة (Heap Limit، عادة 192MB إلى 512MB حسب عتاد الجهاز).\n"
            "   - الذاكرة مقسمة إلى: **RAM Heap** (للكائنات والبيانات)، و **Stack** (لإطارات استدعاء الدوال والمتغيرات المحلية)، و **Native Memory** (للـ Bitmaps وكود C++).\n\n"
            "2. ما الذي يفعله الـ Garbage Collector (GC)؟\n"
            "   - الـ GC هو محرك آلي يبحث دورياً عن **الكائنات غير المستخدمة (Unreachable Objects)** على الـ Heap ويقوم بتحرير مساحتها في الذاكرة لتجنب نفاد الرام.\n"
            "   - في ART الحديث، الـ GC يعمل بنظام **Generational GC و Concurrent Mark-Sweep (CMS)**:\n"
            "     * الكائنات الجديدة توضع في الـ Young Generation؛ ومعظمها يموت سريعاً ويتم تنظيفه بـ Minor GC سريع جداً.\n"
            "     * الكائنات التي تعيش طويلاً تنتقل إلى Old Generation.\n\n"
            "3. أثر الـ GC على أداء وسلاسة التطبيق (Jank):\n"
            "   - إذا كان الكود ينشئ ملايين الكائنات المؤقتة داخل Loops أو في دالة `onDraw`، يحدث ما يسمى **Memory Churn**.\n"
            "   - يؤدي ذلك إلى إجبار الـ GC على إيقاف خيوط التطبيق مؤقتاً (Stop-The-World Pauses)، مما يسبب سقوط فريمات وتشنج في الشاشة (UI Jank)."
        ),
        "practical_walkthrough": (
            "المقارنة بين كود يسبب ضغطاً على الـ GC وكود محسّن:\n"
            "```kotlin\n"
            "// ❌ كود سيء يسبب Memory Churn و GC Pauses داخل RecyclerView أو onDraw:\n"
            "override fun onBindViewHolder(holder: ViewHolder, position: Int) {\n"
            "    // إنشاء كائنات Formatters وتواريخ جديدة في كل لفة سكرول:\n"
            "    val formatter = SimpleDateFormat(\"yyyy-MM-dd\", Locale.US) // allocation في Heap!\n"
            "    holder.dateText.text = formatter.format(Date(items[position].timestamp))\n"
            "}\n"
            "\n"
            "// ✅ كود محسّن يعيد استخدام الكائنات (Zero Allocations in Scroll):\n"
            "companion object {\n"
            "    private val DATE_FORMATTER = DateTimeFormatter.ISO_LOCAL_DATE // كائن واحد معاد استخدامه\n"
            "}\n"
            "override fun onBindViewHolder(holder: ViewHolder, position: Int) {\n"
            "    holder.dateText.text = DATE_FORMATTER.format(items[position].localDate)\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Android manages memory via the Android Runtime (ART) with per-app heap limits. The Garbage Collector automatically tracks object reachability from GC Roots and reclaims unreachable memory using generational collection, but excessive allocations cause Stop-The-World GC pauses and UI jank.",
        "best_answer": (
            "Android manages memory through the Android Runtime (ART), assigning each application a sandboxed virtual machine with a strict heap limit (typically 192MB-512MB).\n\n"
            "The **Garbage Collector (GC)** is the automated memory manager that reclaims heap memory occupied by objects that are no longer referenced or reachable by the application:\n\n"
            "1. **Tracing Reachability**: The GC starts from a set of **GC Roots** (active thread stacks, static variables, JNI global references) and traverses object reference graphs. Any object that cannot be reached from any GC Root is marked as garbage.\n\n"
            "2. **Generational Collection**: ART separates objects into generations: newly allocated objects reside in the *Young Generation*, while long-lived objects advance to the *Old Generation*. Minor GCs clean short-lived objects rapidly with minimal latency.\n\n"
            "3. **Performance Impact**: While ART employs concurrent garbage collection, high allocation churn (creating thousands of temporary objects in loops or `onDraw()`) triggers frequent GC sweeps that briefly pause application threads, causing dropped frames (jank)."
        ),
        "deep_answer": (
            "Under the hood, ART has evolved through multiple GC implementations: from the Dalvik Stop-The-World collector, to ART's Concurrent Mark-Sweep (CMS), to the **Concurrent Copying (CC) GC** introduced in Android 8.0+. "
            "The Concurrent Copying collector is a compacting collector: it moves live objects to contiguous memory regions while application threads continue running, virtually eliminating heap fragmentation without long pause times.\n\n"
            "However, ART still enforces hard memory ceilings (`getMemoryClass()` and `getLargeMemoryClass()`). "
            "If an allocation request exceeds the available process heap and the GC cannot reclaim sufficient contiguous memory through collection and compaction, ART throws an irrecoverable `OutOfMemoryError` (OOM).\n\n"
            "In Android profiling, we monitor the **Allocations Track** in Android Studio Profiler to identify memory churn: high saw-tooth allocation spikes immediately indicate unnecessary object creation in high-frequency rendering paths."
        ),
        "follow_ups": [
            {
                "interviewer": "Can you force garbage collection by calling `System.gc()`?",
                "answer": "Calling `System.gc()` is only a hint to the runtime, not a guarantee. Even if it triggers collection, calling it manually is an antipattern because it forces an expensive full-heap sweep, halting threads and causing noticeable UI stutter."
            },
            {
                "interviewer": "Where are Bitmaps allocated in modern Android (API 26+)?",
                "answer": "Starting in Android 8.0 (API 26), Bitmap pixel data is allocated in native C++ memory (graphics heap) rather than the Java heap, though the garbage collector still manages their lifecycle through NativeAllocationRegistry."
            },
            {
                "interviewer": "What is the difference between `getMemoryClass()` and `getLargeMemoryClass()`?",
                "answer": "`getMemoryClass()` returns the standard heap limit in megabytes. `getLargeMemoryClass()` returns the expanded limit available only if `android:largeHeap=\"true\"` is declared in the manifest (which should only be used for specialized apps like photo editors)."
            }
        ]
    },
    {
        "id": "MEM-02",
        "arabic_explanation": (
            "ما هي الـ GC Roots وكيف يحدد مجمع النفايات إمكانية الوصول للكائنات (Reachability Analysis)؟\n\n"
            "1. ما هو جذر تتبع القمامة (GC Root)؟\n"
            "   - الـ GC Root هو كائن في الذاكرة يُعتبر **حياً بطبيعته ونقطة بداية موثوقة (Anchor of Liveness)** لا يمكن للـ GC حذفها.\n"
            "   - أمثلة على الـ GC Roots:\n"
            "     * **خيوط المعالجة النشطة (Active Threads):** أي كائن `Thread` يعمل حالياً في النظام، بما في ذلك الـ Main Thread وخيوط Coroutines.\n"
            "     * **المتغيرات المحلية على الـ Stack (Stack Frames):** المتغيرات والمعاملات الموجودة داخل الدوال الجاري تنفيذها حالياً في أي Thread.\n"
            "     * **المتغيرات الثابتة للكلاسات (Static Fields):** أي متغير `static` أو كائن `companion object` في كلاس محمل في الذاكرة.\n"
            "     * **مراجع الـ JNI العامة (JNI Global References):** كائنات Java الممسوكة من كود C++ عبر `NewGlobalRef`.\n\n"
            "2. كيف يحدد الـ GC إمكانية الوصول (Reachability)؟\n"
            "   - يقوم الـ GC بعمل خوارزمية **Mark-and-Sweep**:\n"
            "     * يبدأ من جميع الـ GC Roots ويتتبع كل المراجع (References) الخارجة منها كشجرة علاقات (Directed Graph).\n"
            "     * أي كائن متصل بـ GC Root عبر سلسلة مراجع قوية (Strong Reference Chain) يُعتبر **Reachable (حي)** ويُترك في الذاكرة.\n"
            "     * أي كائن غير متصل بأي GC Root يُعتبر **Unreachable (ميت)** ويتم مسحه وتحرير مساحته، حتى لو كانت هناك كائنات ميتة أخرى تشير إليه (Cyclic References)!"
        ),
        "practical_walkthrough": (
            "توضيح عملي للـ Reference Chains وكيف يحدث الـ Leak:\n"
            "```text\n"
            "[GC Root: Active Main Thread]\n"
            "       |\n"
            "       v\n"
            "[Looper Message Queue]\n"
            "       |\n"
            "       v\n"
            "[Pending Message: 10-second delay]\n"
            "       |\n"
            "       v (target)\n"
            "[Anonymous Handler Runnable]\n"
            "       |\n"
            "       v (implicit outer reference)\n"
            "[Old Destroyed MainActivity]  <--- LEAKED! لانها متصلة بـ GC Root!\n"
            "```\n"
            "طالما أن الـ Message معلقة في الـ MessageQueue، فالـ MainActivity تعتبر Reachable بالنسبة للـ GC ولن يستطيع مسحها من الذاكرة حتى ينتهي الـ 10 ثوانٍ."
        ),
        "quick_answer": "GC Roots are objects always deemed alive (active threads, local stack variables, static fields, JNI global handles). The GC traverses outgoing strong references forming a directed graph; objects reachable from any GC Root are retained, while unreachable objects are reclaimed.",
        "best_answer": (
            "Garbage collection in Android determines an object's liveness through **Reachability Analysis** originating from **GC Roots**:\n\n"
            "A **GC Root** is an anchor object that is fundamentally alive and cannot be collected:\n\n"
            "1. **Active Threads**: The Main UI thread and any running worker thread or coroutine thread pool.\n"
            "2. **Thread Stack Frames**: Local variables and parameters currently residing on active function call stacks.\n"
            "3. **Static Fields**: Variables owned by loaded classes or Kotlin companion objects/singletons.\n"
            "4. **JNI References**: Global C/C++ native pointers created via `NewGlobalRef`.\n\n"
            "During a collection cycle, the GC traces outward from all GC Roots across object reference pointers in a directed graph. If an object has a valid path of strong references connecting it to at least one GC Root, it is **Reachable** and preserved. If no path exists, it is **Unreachable** and its memory is reclaimed."
        ),
        "deep_answer": (
            "A vital senior distinction is understanding how tracing garbage collection handles **Cyclic References** compared to naive reference counting:\n\n"
            "If Object A references Object B, and Object B references Object A, but neither A nor B is reachable from any GC Root, ART's reachability graph correctly identifies both as unreachable garbage and collects both simultaneously. Cycles of unreachable objects do not cause memory leaks in Android.\n\n"
            "The type of reference pointer also modifies reachability:\n\n"
            "- **Strong Reference**: Default reference. Prevents collection completely as long as reachable from a GC Root.\n"
            "- **Soft Reference (`SoftReference`)**: Retained until memory pressure becomes critical before throwing an OOM. (Discouraged for caches in modern Android in favor of explicit `LruCache`).\n"
            "- **Weak Reference (`WeakReference`)**: Does not protect the target from collection. Reclaimed immediately in the next GC cycle if no strong references exist."
        ),
        "follow_ups": [
            {
                "interviewer": "Why are `SoftReference`s discouraged for image caching in Android?",
                "answer": "Because the runtime GC doesn't have sufficient heuristics on bitmap memory size vs overall system pressure, often evicting soft references either too aggressively or too late. An explicit `LruCache` with a fixed byte-budget in RAM is far more predictable."
            },
            {
                "interviewer": "What is a `PhantomReference`?",
                "answer": "A `PhantomReference` is enqueued after an object has been finalized and its memory is scheduled for reclamation, used primarily for low-level resource cleanup tracking."
            },
            {
                "interviewer": "Can an active coroutine be a GC Root?",
                "answer": "Yes. An active coroutine running on a dispatcher thread keeps its Continuation state machine reachable. If the coroutine captures an Activity reference in its closure and runs an infinite loop, that Activity is reachable from a GC Root and leaks indefinitely."
            }
        ]
    },
    {
        "id": "MEM-03",
        "arabic_explanation": (
            "المقارنة الجوهرية بين الـ Stack والـ Heap في إدارة الذاكرة: ما الذي يعيش على كل منهما؟\n\n"
            "1. الـ Stack (ذاكرة الاستدعاء السريعة):\n"
            "   - **طبيعتها:** ذاكرة سريعة جداً وخاصة بكل خيط معالجة (Per-Thread Memory) تعمل بنظام LIFO (Last-In, First-Out).\n"
            "   - **ما الذي يعيش عليها؟**\n"
            "     * إطارات استدعاء الدوال (Stack Frames).\n"
            "     * المتغيرات المحلية الأولية (Primitive types: `int`, `boolean`, `long`, `float`).\n"
            "     * مراجع المؤشرات للكائنات (Reference Pointers) التي تشير إلى أماكن الكائنات في الـ Heap.\n"
            "   - **إدارة الذاكرة:** تدار تلقائياً بواسطة المعالج (CPU)؛ بمجرد خروج التنفيذ من الدالة، يتم مسح الـ Stack Frame فوراً وبدون أي تدخل من الـ GC.\n"
            "   - **المشكلة الشائعة:** `StackOverflowError` لو حدث استدعاء ذاتي لا نهائي (Infinite Recursion).\n\n"
            "2. الـ Heap (ذاكرة الكائنات المشتركة):\n"
            "   - **طبيعتها:** مساحة ذاكرة ضخمة مشتركة بين جميع خيوط التطبيق (Shared across all threads).\n"
            "   - **ما الذي يعيش عليها؟**\n"
            "     * **جميع الكائنات (All Objects):** كلاسات، Strings، Arrays، Bitmaps، كائنات الـ Coroutines (Continuations)، والـ Collections.\n"
            "   - **إدارة الذاكرة:** تدار حصرياً بواسطة مجمع النفايات (Garbage Collector).\n"
            "   - **المشكلة الشائعة:** `OutOfMemoryError` لو امتلاء الـ Heap بالكامل."
        ),
        "practical_walkthrough": (
            "تحليل سطر كود واحد لمعرفة ما يذهب للـ Stack وما يذهب للـ Heap:\n"
            "```kotlin\n"
            "fun calculate() {\n"
            "    val age = 25              // 1. القيمة 25 مخزنة على الـ Stack مباشرة (Primitive)\n"
            "    val name = \"Mohamed\"      // 2. المؤشر name على الـ Stack، وكائن String نفسه على الـ Heap!\n"
            "    val user = User(age, name)// 3. المؤشر user على الـ Stack، وكائن User بالكامل على الـ Heap!\n"
            "}\n"
            "```\n"
            "بمجرد انتهاء دالة `calculate()`: المتغيرات `age`, `name`, `user` تمسح فوراً من الـ Stack في جزء من النانو-ثانية. وكائن `User` يظل في الـ Heap حتى يأتي الـ GC ويمسحه."
        ),
        "quick_answer": "Stack is fast, thread-local LIFO memory holding primitive local variables, function frames, and object reference pointers, cleaned up immediately on function return. Heap is large, shared memory holding all instantiated objects, arrays, and closures, managed asynchronously by the Garbage Collector.",
        "best_answer": (
            "The Stack and Heap represent the two foundational memory areas in Android runtime execution:\n\n"
            "**The Stack**:\n\n"
            "- **Scope & Lifecycle**: Thread-local. Every OS thread has its own dedicated call stack.\n"
            "- **What lives here**: Function call frames, local primitive variables (`int`, `boolean`, `double`), and reference pointers pointing to objects in the heap.\n"
            "- **Management**: Managed directly by CPU instruction pointer registers in a LIFO order. Memory allocation and deallocation happen in O(1) instant time when functions are pushed and popped. Zero GC involvement.\n\n"
            "**The Heap**:\n\n"
            "- **Scope & Lifecycle**: Globally shared across all threads within the app process.\n"
            "- **What lives here**: All instantiated objects (`class`, `data class`), arrays, collections, boxed primitives (`Integer`), coroutine state machines, and string contents.\n"
            "- **Management**: Dynamically allocated and asynchronously reclaimed by the Garbage Collector."
        ),
        "deep_answer": (
            "Understanding Stack vs Heap allocation boundaries is essential for optimization. "
            "For example, Kotlin's **Value Classes (`@JvmInline value class`)** leverage this distinction: "
            "When a function accepts an unboxed value class (like `@JvmInline value class UserId(val id: Long)`), the compiler inlines the `Long` directly onto the call stack as a 64-bit primitive rather than allocating a wrapper object on the heap.\n\n"
            "Conversely, when local variables inside a function are captured by an escaping lambda or coroutine:\n\n"
            "```kotlin\n"
            "fun track() {\n"
            "    var count = 0\n"
            "    button.setOnClickListener { count++ } // Escapes stack frame!\n"
            "}\n"
            "```\n\n"
            "Because the lambda outlives the `track()` function's stack frame, the compiler promotes `count` from the stack to the heap, wrapping it in a heap-allocated `Ref.IntRef` object. This is known as **Variable Escaping**."
        ),
        "follow_ups": [
            {
                "interviewer": "What causes a `StackOverflowError`?",
                "answer": "A `StackOverflowError` occurs when the execution stack exhausts its allocated memory limit (typically ~1MB), almost always caused by unbounded or deep recursive function calls without tail-call optimization (`tailrec`)."
            },
            {
                "interviewer": "Can objects live on the Stack in Java/Kotlin?",
                "answer": "No. In the standard JVM and ART specifications, all object instances are allocated on the Heap. Only primitive values and object reference pointers live on the Stack."
            },
            {
                "interviewer": "Why is Stack access faster than Heap access?",
                "answer": "Stack memory operations operate on contiguous memory mapped directly into CPU L1/L2 cache lines with zero pointer indirection, while Heap memory involves dynamic pointer lookups and cache misses."
            }
        ]
    },
    {
        "id": "MEM-04",
        "arabic_explanation": (
            "المقارنة بين تسريب الذاكرة (Memory Leak) والحجم الضخم للذاكرة (Large Memory Allocation):\n\n"
            "1. ما هو تسريب الذاكرة (Memory Leak)؟\n"
            "   - هو بقاء كائن في الذاكرة **لم يعد التطبيق بحاجة إليه إطلاقاً**، ولكن مجمع النفايات (GC) **عاجز عن حذفه** لأن هناك كائن حي آخر يمسك به بـ Strong Reference!\n"
            "   - مثال: إغلاق شاشة `ProfileActivity`، ولكن كلاس Singleton ما زال ممسكاً بـ Reference لها. الشاشة أصبحت ميتة وظيفياً، لكنها محبوسة في الـ Heap.\n"
            "   - **الخاصية المميزة:** المشكلة في **الملكية والربط (Retention Bug)**، وتتراكم الذاكرة تدريجياً بمرور الوقت حتى ينهار التطبيق.\n\n"
            "2. ما هو الحجم الضخم للذاكرة (Large Memory Allocation)؟\n"
            "   - هو حجز مساحة كبيرة جداً من الذاكرة في لحظة واحدة لكائن **يحتاجه التطبيق فعلياً ويستخدمه حالياً (Legitimate Usage)**.\n"
            "   - مثال: تحميل صورة 4K غير مضغوطة بحجم 40 ميجابايت لعرضها على الشاشة.\n"
            "   - **الخاصية المميزة:** المشكلة في **الكفاءة والحجم (Footprint / Scale)**، ويمكن للـ GC حذف الكائن فور الانتهاء من استخدامه.\n\n"
            "3. الفارق في العلاج:\n"
            "   - تسريب الذاكرة يعالج بـ: قطع الروابط، تصفير الـ References (`_binding = null`)، واستخدام Lifecycle Observers.\n   - الحجم الضخم يعالج بـ: تصغير حجم الصور (`inSampleSize`, downsampling)، استخدام Pagination، وضبط الـ Caching."
        ),
        "practical_walkthrough": (
            "مقارنة عملية في الكود:\n"
            "```kotlin\n"
            "// 1. Large Allocation (ليس تسريباً): يحجز 50MB لكنه مشروع ويحرر فور انتهاء الدالة:\n"
            "fun processHighResBanner() {\n"
            "    val bigBitmap = Bitmap.createBitmap(4000, 4000, Bitmap.Config.ARGB_8888) // 64 MB!\n"
            "    renderBanner(bigBitmap)\n"
            "    // بمجرد انتهاء الدالة، bigBitmap يصبح Unreachable والـ GC يستطيع حذفه بنجاح.\n"
            "}\n"
            "\n"
            "// 2. Memory Leak (تسريب ذاكرة خطير): كائن صغير أو كبير يظل محبوساً للأبد:\n"
            "object BadRepository {\n"
            "    val listeners = mutableListOf<OnDataLoadedListener>() // لا يتم تفريغه أبداً!\n"
            "}\n"
            "class MyActivity : AppCompatActivity() {\n"
            "    override fun onCreate(savedInstanceState: Bundle?) {\n"
            "        super.onCreate(savedInstanceState)\n"
            "        BadRepository.listeners.add(this) // تسريب! الـ Activity لن تموت أبداً!\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "A memory leak is a structural retention bug where an unneeded object cannot be garbage collected due to an unintended lingering reference. A large memory allocation is a legitimate, high-volume memory consumption (like a 50MB bitmap) that is fully reclaimable by the GC once out of scope.",
        "best_answer": (
            "The distinction between a memory leak and a large memory allocation comes down to **retention correctness versus volumetric consumption**:\n\n"
            "A **Memory Leak** is an architectural bug where memory that is no longer needed by the business logic cannot be reclaimed by the Garbage Collector because an active GC Root inadvertently retains a strong reference to it (e.g., an Activity retained inside a static singleton listener list). Leaks accumulate silently over time as the user navigates the app, gradually starving the heap until the app crashes with an `OutOfMemoryError`.\n\n"
            "A **Large Memory Allocation** is a valid allocation that consumes a significant portion of memory (e.g., loading an uncompressed 50MB bitmap or parsing a 20MB JSON string into memory). The allocation is legitimate, intentional, and fully eligible for garbage collection the moment execution exits its scope.\n\n"
            "While a large allocation can trigger an immediate OOM if memory is already tight, a memory leak is a persistent defect that guarantees eventual failure."
        ),
        "deep_answer": (
            "In production performance profiling, distinguishing between the two dictates the diagnosis methodology:\n\n"
            "1. **Diagnosing Large Allocations**: Open the Android Studio CPU/Memory Profiler and inspect the **Memory Allocation Graph**. A large allocation appears as an immediate, sharp vertical cliff in memory usage. Once the operation finishes, a GC sweep causes the graph to drop back down to baseline. The remedy is technical optimization: image downsampling (`inSampleSize`), streaming JSON parsing via Jackson/Moshi streaming readers, or lazy pagination.\n\n"
            "2. **Diagnosing Memory Leaks**: A memory leak produces a **sawtooth graph that never returns to baseline**: with each screen rotation or navigation transition, the minimum heap baseline ratchets upward. Taking a heap dump (`.hprof`) via LeakCanary reveals the exact shortest reference path connecting the dead Activity to an active GC Root."
        ),
        "follow_ups": [
            {
                "interviewer": "Can a small memory leak of just 100 bytes cause an OutOfMemoryError?",
                "answer": "Yes! If a 100-byte listener leaks an entire Activity instance via its implicit outer class reference, that 100-byte leak actually pins the Activity, its View hierarchy, Drawables, and Bitmaps—retaining dozens of megabytes per leak."
            },
            {
                "interviewer": "Can an app have zero memory leaks and still crash with an OutOfMemoryError?",
                "answer": "Absolutely. If an app attempts to allocate a single 200MB bitmap on a device with a 192MB heap limit, it will crash with an OOM immediately despite having zero memory leaks."
            },
            {
                "interviewer": "How does `largeHeap=\"true\"` relate to these two issues?",
                "answer": "`largeHeap` requests an expanded heap ceiling, which can accommodate legitimate large memory allocations (like photo editing apps), but it will never fix a memory leak—it only delays the inevitable crash."
            }
        ]
    },
    {
        "id": "MEM-05",
        "arabic_explanation": (
            "المقارنة الشاملة بين كوارث أندرويد الأربعة: `Memory Leak` و `OutOfMemoryError` و `ANR` و `StackOverflowError`:\n\n"
            "1. الـ Memory Leak (تسريب الذاكرة):\n"
            "   - **السبب:** كائن لم يعد مطلوباً ولكنه محبوس في الـ Heap بسبب Strong Reference متصل بـ GC Root.\n"
            "   - **الأثر:** لا يسبب كراش فوري؛ بل تراكم بطيء للذاكرة.\n\n"
            "2. الـ OutOfMemoryError - OOM (نفاد الذاكرة):\n"
            "   - **السبب:** التطبيق طلب حجز ذاكرة على الـ **Heap** (مثل Bitmap ضخم)، ولكن الـ Heap ممتلئ تماماً والـ GC عاجز عن توفير مساحة.\n"
            "   - **الأثر:** Crash فوري وانهيار للتطبيق.\n\n"
            "3. الـ ANR - Application Not Responding (تجميد التطبيق):\n"
            "   - **السبب:** حظر الـ **Main (UI) Thread** لعدة ثوانٍ (عمليات حسابية ثقيلة، قراءة ديسك، أو Thread.sleep) مما يمنع معالجة أحداث اللمس ورسم الفريمات.\n"
            "   - **الأثر:** لا يغلق التطبيق فوراً؛ يظهر للمستخدم نافذة من النظام تخبره بأن التطبيق لا يستجيب وتسأله هل يريد إغلاقه.\n\n"
            "4. الـ StackOverflowError (فيضان الـ Stack):\n"
            "   - **السبب:** امتلاء ذاكرة الـ **Stack** الخاصة بالـ Thread بسبب استدعاءات دوال متداخلة لا نهائية (Infinite Recursion).\n"
            "   - **الأثر:** Crash فوري في كود التنفيذ."
        ),
        "practical_walkthrough": (
            "جدول مقارنة حاسم وسريع:\n"
            "| الكارثة | مكان الحدوث | السبب الجوهري | النتيجة الظاهرة |\n"
            "| :--- | :--- | :--- | :--- |\n"
            "| **Memory Leak** | Heap | كائن ميت ممسوك بـ Reference | استهلاك RAM متزايد تدريجياً |\n"
            "| **OOM** | Heap | امتلاء الـ Heap وعدم كفاية الرام | Crash فوري بـ OutOfMemoryError |\n"
            "| **ANR** | Main Thread | حظر الـ UI Thread لأكثر من 5 ثوانٍ | نافذة 'التطبيق لا يستجيب' |\n"
            "| **StackOverflow** | Call Stack | استدعاء دالة متداخل لا نهائي | Crash فوري بـ StackOverflowError |"
        ),
        "quick_answer": "A Memory Leak is an unintended object retention in the Heap; an OutOfMemoryError is a Heap exhaustion crash; an ANR is a Main Thread freeze (>5s) blocking user input; and a StackOverflowError is a Thread call stack exhaustion crash caused by infinite recursion.",
        "best_answer": (
            "These four system failure modes represent fundamentally different failure domains across memory and threading architecture:\n\n"
            "1. **Memory Leak**: An architectural retention defect where unreachable heap objects are retained by active GC Roots. It does not crash immediately, but progressively inflates the heap baseline.\n\n"
            "2. **OutOfMemoryError (OOM)**: A runtime fatal error thrown when the application requests heap allocation (e.g. allocating a bitmap) and the ART garbage collector cannot reclaim sufficient contiguous memory despite garbage collection.\n\n"
            "3. **ANR (Application Not Responding)**: A threading and responsiveness defect caused by blocking the **Main UI Thread** for longer than 5 seconds (preventing touch input dispatch) or 10-20 seconds in services and broadcast receivers. It prompts a system dialog offering the user to force-close the app.\n\n"
            "4. **StackOverflowError**: A thread call stack failure thrown when the LIFO execution stack exceeds its physical frame budget (typically 1MB), almost universally caused by infinite or excessively deep recursive method calls."
        ),
        "deep_answer": (
            "In Android production diagnostics, each failure triggers different tracing artifacts:\n\n"
            "- **OOM**: Captured in Crashlytics with stack traces originating at allocation sites (e.g., `BitmapFactory.nativeDecodeStream` or `ByteArrayOutputStream.toByteArray()`). Resolving it requires analyzing heap dumps (`.hprof`) via LeakCanary or Memory Profiler.\n\n"
            "- **ANR**: Captured in the Android OS system dump `/data/anr/traces.txt`. The trace reveals what state the Main thread was in (e.g., `BLOCKED` on a database lock or executing a synchronous network read). It is resolved by offloading the blocked work to `withContext(Dispatchers.IO)`.\n\n"
            "- **StackOverflowError**: Manifests with hundreds of repeated lines of the same method in Crashlytics. It is resolved by applying tail recursion (`tailrec`) or converting recursive algorithms into iterative loops with explicit queue/stack data structures."
        ),
        "follow_ups": [
            {
                "interviewer": "Can a memory leak cause an ANR?",
                "answer": "Indirectly, yes! When memory leaks fill the heap near capacity, ART triggers continuous, aggressive garbage collection sweeps in a desperate attempt to free memory. These frequent GC pauses halt the main thread, leading to severe jank and eventually triggering an ANR."
            },
            {
                "interviewer": "Can an ANR happen if CPU usage is 0%?",
                "answer": "Yes. If the Main thread is blocked waiting on a lock held by a background thread (Deadlock) or waiting on a synchronous IPC call, CPU usage is 0% but the thread is blocked, triggering an ANR."
            },
            {
                "interviewer": "Does Kotlin's `tailrec` prevent `StackOverflowError`?",
                "answer": "Yes. When a recursive function is marked `tailrec`, the Kotlin compiler transforms the recursion into a standard iterative loop in bytecode, executing within a single stack frame and completely preventing stack overflow."
            }
        ]
    },
    {
        "id": "MEM-06",
        "arabic_explanation": (
            "الـ Boxing والـ Unboxing في Kotlin ومتى يؤثر بشكل ملحوظ على أداء الذاكرة (Allocation Performance):\n\n"
            "1. ما هو الـ Boxing والـ Unboxing؟\n"
            "   - **الـ Boxing (التغليف):** هو تحويل نوع أولي خفيف يعيش على الـ Stack (مثل `int` أو `long` البدائي) إلى كائن كلاس ثقيل في الـ Heap (مثل `java.lang.Integer` أو `java.lang.Long`).\n"
            "   - **الـ Unboxing (فك التغليف):** هو استخراج القيمة الأولية من كائن الـ Wrapper.\n\n"
            "2. ما هي تكلفة الـ Boxing في الذاكرة؟\n"
            "   - الـ `int` البدائي يستغرق **4 Bytes** فقط على الـ Stack.\n"
            "   - كائن الـ `Integer` المغلف يستغرق **16 إلى 24 Bytes** على الـ Heap (Object header + primitive value + memory padding) بالإضافة لمؤشر العنوان (4-8 bytes)!\n"
            "   - زيادة استهلاك الذاكرة بأكثر من 400% لكل رقم، بالإضافة لضغط الـ GC عند حذفه!\n\n"
            "3. متى يحدث الـ Boxing في Kotlin؟\n"
            "   - **مع الـ Nullable Types (`Int?`):** الأنواع الأولية في الـ JVM لا تقبل `null`؛ لذلك `Int?` تُجبر المترجم على استخدام `java.lang.Integer` المغلف في الـ Heap.\n"
            "   - **مع الـ Generic Collections (`List<Int>`, `Map<Int, String>`):** لأن الـ Java Generics تدعم الكائنات فقط، كل رقم داخل `List<Int>` هو كائن مغلف في الـ Heap!\n   - **مع الـ Value Classes:** عندما تستخدم `@JvmInline value class` كـ Generic أو كـ Nullable.\n\n"
            "4. متى يشكل ذلك خطراً على الأداء؟\n"
            "   - في الـ Hot Loops، معالجة الصوت، الرسوميات، وقوائم البيانات الضخمة التي تحتوي على مئات الآلاف من الأرقام."
        ),
        "practical_walkthrough": (
            "مقارنة عملية في استهلاك الذاكرة بين Boxing وبدائل الأداء:\n"
            "```kotlin\n"
            "// ❌ كود يسبب Boxing لملايين الكائنات في الـ Heap:\n"
            "val numbers = ArrayList<Int>() // كل رقم هو Integer كائن في الـ Heap!\n"
            "for (i in 0 until 1_000_000) {\n"
            "    numbers.add(i) // 1,000,000 كائن في الـ Heap -> يستهلك حوالي 24MB!\n"
            "}\n"
            "\n"
            "// ✅ كود محسّن بدون أي Boxing (Primitives):\n"
            "val primitiveNumbers = IntArray(1_000_000) // مصفوفة أرقام أولية contiguous memory\n"
            "for (i in 0 until 1_000_000) {\n"
            "    primitiveNumbers[i] = i // 0 objects allocated -> يستهلك 4MB فقط!\n"
            "}\n"
            "```\n"
            "في أندرويد، نستخدم أيضاً مجموعات أولية مخصصة مثل `SparseIntArray` لتجنب الـ Boxing في الخرائط."
        ),
        "quick_answer": "Boxing converts stack-allocated primitives (int) into heap-allocated wrapper objects (Integer), increasing memory consumption by 400% per value. It occurs when using nullable primitives (Int?), generic collections (List<Int>), or boxed value classes, degrading performance in hot loops and high-throughput data processing.",
        "best_answer": (
            "Boxing is the conversion of an unboxed primitive (like `int`, `long`, `boolean`) into its corresponding object wrapper (`java.lang.Integer`, `java.lang.Long`, `java.lang.Boolean`) on the heap. Unboxing is the inverse.\n\n"
            "**Memory Cost**:\n"
            "A bare `int` occupies strictly 4 bytes on the stack. An `Integer` wrapper on 64-bit Android requires an 8-12 byte object header, 4 bytes for the int value, and 4 bytes of memory alignment padding, consuming **16 to 24 bytes on the heap**, plus an object reference pointer. That represents a 4x to 6x memory overhead.\n\n"
            "**When Boxing Occurs in Kotlin**:\n\n"
            "1. **Nullable Primitives (`Int?`)**: The JVM primitives cannot represent `null`. Declaring `var age: Int? = null` forces ART to box the value as `java.lang.Integer` whenever non-null.\n"
            "2. **Generic Collections (`List<Int>`, `Map<K, V>`)**: Because Java/Kotlin generics erase to `Object`, collections cannot store primitives directly, boxing every single element.\n"
            "3. **Value Classes**: Using `@JvmInline value class` in generic or nullable positions.\n\n"
            "**When It Matters**: For everyday business logic, boxing overhead is negligible. However, in hot execution loops (audio signal processing, game loops, image filtering, or processing collections with 100,000+ items), boxing allocates millions of short-lived objects, triggering severe GC churn and frame drops."
        ),
        "deep_answer": (
            "To eliminate boxing in performance-critical Android systems, we employ specialized primitive architectures:\n\n"
            "1. **Primitive Arrays**: Use `IntArray`, `LongArray`, and `FloatArray` instead of `Array<Int>` or `List<Int>`. In bytecode, `IntArray` compiles to `int[]`, a single contiguous native memory block with zero object overhead per element.\n\n"
            "2. **Android Sparse Arrays**: In collections mapping integer keys, replace `HashMap<Int, T>` with Android's **`SparseArray<T>`**, **`SparseIntArray`**, or **`SparseLongArray`**. These are binary-search backed array collections that avoid boxing both the integer keys and values, reducing memory consumption by over 50%.\n\n"
            "3. **Fast Primitive Collections**: For high-throughput graphics or math, libraries like HPPC (High Performance Primitive Collections) provide primitive-specialized sets and maps."
        ),
        "follow_ups": [
            {
                "interviewer": "Why does Kotlin cache small Integer boxes?",
                "answer": "Like Java, ART caches boxed `Integer` instances in an `IntegerCache` between -128 and 127. Values in this range reuse cached singleton objects without allocating new heap instances."
            },
            {
                "interviewer": "What is the difference between `Array<Int>` and `IntArray` in Kotlin?",
                "answer": "`Array<Int>` compiles to `java.lang.Integer[]` (an array of object pointers, boxing every integer). `IntArray` compiles to `int[]` (a flat array of raw 32-bit primitives with zero boxing)."
            },
            {
                "interviewer": "Does using `var x: Int = 10` ever box if not nullable?",
                "answer": "No. When declared as a non-null local variable or non-generic property, the Kotlin compiler compiles `Int` strictly to the primitive `int` bytecode instruction."
            }
        ]
    }
]


def main() -> None:
    existing = []
    if DATA_FILE.exists():
        try:
            existing = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except Exception:
            existing = []

    combined = []
    seen = set()
    for q in existing:
        combined.append(q)
        seen.add(q["id"])

    for q in MEM_01_06:
        if q["id"] not in seen:
            combined.append(q)
            seen.add(q["id"])
        else:
            for idx, item in enumerate(combined):
                if item["id"] == q["id"]:
                    combined[idx] = q
                    break

    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(combined, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {DATA_FILE} with questions MEM-01 to MEM-06. Total questions: {len(combined)}")


if __name__ == "__main__":
    main()
