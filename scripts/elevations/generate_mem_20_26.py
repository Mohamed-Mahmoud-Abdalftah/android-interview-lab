#!/usr/bin/env python3
"""Generator for MEM-20 through MEM-26 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "mem.json"

MEM_20_26 = [
    {
        "id": "MEM-20",
        "arabic_explanation": (
            "تصميم الـ Cache والتعامل مع القوائم الضخمة (Large Lists) وكيف يمكن أن يتسببا في تدهور الذاكرة والأداء:\n\n"
            "1. مخاطر الـ Unbounded Caching (الكاش غير المحدود):\n"
            "   - أكبر خطأ شائع هو استخدام `HashMap<Key, Value>` عادي كـ In-Memory Cache.\n"
            "   - الـ HashMap العادي لا يملك آلية طرد (Eviction Policy) ولا يعرف سقفاً للذاكرة؛ كل عنصر يدخل يظل محجوزاً في الـ Heap حتى يمتلئ مسبباً `OutOfMemoryError`.\n"
            "   - الحل السليم هو استخدام `LruCache` (Least Recently Used Cache) المدمج في Android Jetpack، مع تحديد حجمه بوحدات البايت (وليس عدد العناصر فقط) كنسبة محددة من الـ Heap المتاح (مثلاً 1/8 من الذاكرة).\n\n"
            "2. مشاكل الذاكرة في القوائم الضخمة (Large Lists):\n"
            "   - محاولة جلب آلاف العناصر وتخزينها في `List<Entity>` داخل الذاكرة دفعة واحدة تبتلع مساحة ضخمة من الـ RAM وتجمد الـ UI أثناء التحويل والـ Parsing.\n"
            "   - في `RecyclerView`، عدم ثبات الـ ViewHolders أو عمل عمليات حجز مكلفة داخل `onBindViewHolder` يسبب سقوط فريمات (Jank).\n\n"
            "3. الحلول المعمارية القياسية:\n"
            "   - **Paging 3 Library**: تحميل البيانات على دفعات صغيرة مجزأة (Chunks) بالطلب بالتوازي مع سكرول المستخدم، مع التخلص التلقائي من الصفحات البعيدة عن نطاق الرؤية.\n"
            "   - **DiffUtil / ListAdapter**: حساب الفروقات بدقة في Background Thread دون إعادة رسم القائمة كاملة.\n"
            "   - الاستجابة لنداء النظام `onTrimMemory(level)`: تفريغ الكاش فوراً عند استلام `TRIM_MEMORY_RUNNING_CRITICAL`."
        ),
        "practical_walkthrough": (
            "تصميم LruCache محكوم بالذاكرة مع الاستجابة لـ onTrimMemory:\n"
            "```kotlin\n"
            "class MemoryBoundedImageCache(maxMemoryInBytes: Int) : ComponentCallbacks2 {\n"
            "    private val cache = object : LruCache<String, Bitmap>(maxMemoryInBytes) {\n"
            "        override fun sizeOf(key: String, value: Bitmap): Int {\n"
            "            // قياس الحجم الفعلي للـ Bitmap بالبايت وليس بعدد العناصر:\n"
            "            return value.allocationByteCount\n"
            "        }\n"
            "    }\n"
            "\n"
            "    fun get(key: String): Bitmap? = cache.get(key)\n"
            "    fun put(key: String, bitmap: Bitmap) { cache.put(key, bitmap) }\n"
            "\n"
            "    override fun onTrimMemory(level: Int) {\n"
            "        if (level >= ComponentCallbacks2.TRIM_MEMORY_RUNNING_LOW) {\n"
            "            // تفريغ الكاش عندما يتعرض الجهاز لضغط ذاكرة لتجنب القتل بواسطة LMK:\n"
            "            cache.evictAll()\n"
            "        }\n"
            "    }\n"
            "\n"
            "    override fun onConfigurationChanged(newConfig: Configuration) {}\n"
            "    override fun onLowMemory() { cache.evictAll() }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Unbounded caches like raw `HashMap` grow indefinitely and trigger OOMs, while loading unpaginated lists consumes excessive RAM and stalls the UI. In production, we enforce memory bounds using `LruCache` sized as a fraction of available heap, implement Paging 3 to stream data incrementally, and clear cached assets in `onTrimMemory()`.",
        "best_answer": (
            "Cache misconfigurations and unpaginated lists are two of the most frequent sources of memory leaks and UI thrashing in enterprise applications.\n\n"
            "A standard `HashMap` retains every inserted object with strong references, providing no eviction strategy or size limits. As users browse, memory consumption climbs monotonically until an `OutOfMemoryError` occurs. "
            "To prevent this, production in-memory caches must use `LruCache`, measuring entries by **byte size** (`sizeOf()`) rather than object counts, and budgeting cache size dynamically based on `Runtime.getRuntime().maxMemory()` (typically 10-15% of available heap).\n\n"
            "For large lists, fetching thousands of database records into an in-memory `List<T>` strains both the heap and JSON deserializer. "
            "Instead, we adopt **Jetpack Paging 3**, which loads small pages (e.g. 20-30 items) into the UI reacting to scroll position, while automatically purging distant off-screen pages.\n\n"
            "Additionally, apps must implement `ComponentCallbacks2` and listen to `onTrimMemory(level)`. Purging secondary caches when `TRIM_MEMORY_RUNNING_LOW` arrives prevents the kernel Low Memory Killer (LMK) from terminating the app."
        ),
        "deep_answer": (
            "Under the hood, `LruCache` uses a `LinkedHashMap` configured with access-order ordering (`accessOrder = true`). "
            "Whenever `get()` or `put()` is invoked, the accessed node moves to the tail; when the byte sum exceeds `maxSize`, elements are trimmed from the head.\n\n"
            "In `RecyclerView`, memory regressions frequently occur when developers misuse `DiffUtil` or `setHasFixedSize`. "
            "If `DiffUtil.calculateDiff()` runs on the main thread for lists exceeding a few hundred items, it blocks the main looper for 50-200ms, creating severe UI jank. "
            "Using `AsyncListDiffer` or `ListAdapter` automatically dispatches diff computation to a background executor.\n\n"
            "In Compose, `LazyColumn` handles view recycling virtually, but keeping heavy state closures inside items can retain significant memory. "
            "Using `key` parameters on `items()` ensures that Compose preserves item identity correctly without re-allocating state instances during reordering."
        ),
        "follow_ups": [
            {
                "question": "What happens if you use `WeakHashMap` as an in-memory cache?",
                "answer": "`WeakHashMap` keys are held weakly, but the values are held with strong references. If values reference keys, the entries will never be collected. Furthermore, garbage collection sweeps can purge entries aggressively between frames, resulting in near-zero cache hit rates."
            },
            {
                "question": "How does `onTrimMemory(TRIM_MEMORY_UI_HIDDEN)` differ from other trim levels?",
                "answer": "`TRIM_MEMORY_UI_HIDDEN` is dispatched when your app's UI moves entirely to the background (e.g. user pressed Home). This is the prime opportunity to release heavy UI resources and bitmaps before the system places the process into the cached LRU tier."
            }
        ]
    },
    {
        "id": "MEM-21",
        "arabic_explanation": (
            "كيفية عزل وتشخيص مشكلة زيادة استهلاك الذاكرة تدريجياً على مدار أيام في بيئة الإنتاج (Production Memory Creep):\n\n"
            "1. فهم طبيعة الـ Memory Creep / Slow Leak:\n"
            "   - التسريب البطيء لا يفجر التطبيق فوراً بـ OOM، ولكنه يتراكم مع الاستخدام الطويل (مثل تطبيقات التوصيل، أجهزة نقاط البيع POS، أو الشاشات المعلقة في المتاجر).\n"
            "   - أسبابه المعتادة: كائنات Singleton تجمع بيانات أحداث (Event Logs / Analytics Queue) دون حد أقصى، أو Coroutine Jobs معلقة، أو اشتراكات RxJava/Flow لم يتم إلغاؤها.\n\n"
            "2. استراتيجية العزل والتشخيص خطوة بخطوة:\n"
            "   - **الخطوة 1: التقاط مقاييس الإنتاج (Production Telemetry)**:\n"
            "     * إرسال مقاييس دورية مع أحداث التحليلات: `Debug.getPss()`, `Runtime.getRuntime().totalMemory()`, و `onTrimMemory` events.\n"
            "     * ربط الزيادة بـ User Sessions أو ميزات محددة (Feature flags / Screens).\n"
            "   - **الخطوة 2: محاكاة الاستخدام المكثف في المعمل (Monkey / Stress Testing)**:\n"
            "     * كتابة سكربت UI Automator أو تشغيل `adb shell monkey` لتكرار نفس السيناريوهات آلاف المرات لمدة 12-24 ساعة.\n"
            "   - **الخطوة 3: مقارنة لقطات الـ Heap (Differential Heap Dumps)**:\n"
            "     * أخذ Heap Dump في بداية التشغيل (Baseline Dump)، وأخذ Dump آخر بعد 10 ساعات.\n"
            "     * فتح الملفين في Eclipse MAT أو Android Studio وعمل **Compare Heap Dumps** لمعرفة الكلاسات التي زاد عدد كائناتها بشكل مطرد.\n\n"
            "3. الحل والوقاية:\n"
            "   - إضافة حدود قصوى (Bounded FIFO / Circular Buffers) لأي طوابير تخزين في الذاكرة.\n"
            "   - تفعيل اختبارات آلية تفحص تسريبات الذاكرة قبل كل Release."
        ),
        "practical_walkthrough": (
            "كود لاكتشاف تراكم الذاكرة وإطلاق تحذيرات القياس عن بعد (Telemetry):\n"
            "```kotlin\n"
            "class MemoryTelemetryWorker(context: Context, params: WorkerParameters) : CoroutineWorker(context, params) {\n"
            "    override fun suspend fun doWork(): Result {\n"
            "        val runtime = Runtime.getRuntime()\n"
            "        val usedMemoryMb = (runtime.totalMemory() - runtime.freeMemory()) / (1024 * 1024)\n"
            "        val maxMemoryMb = runtime.maxMemory() / (1024 * 1024)\n"
            "\n"
            "        val memoryPressure = usedMemoryMb.toDouble() / maxMemoryMb.toDouble()\n"
            "\n"
            "        if (memoryPressure > 0.80) { // تنبيه إذا تجاوز الاستهلاك 80% من سقف الـ Heap\n"
            "            AnalyticsTracker.logNonFatal(\n"
            "                \"HighMemoryWarning\",\n"
            "                mapOf(\n"
            "                    \"usedMb\" to usedMemoryMb.toString(),\n"
            "                    \"maxMb\" to maxMemoryMb.toString(),\n"
            "                    \"screen\" to NavigationTracker.getCurrentScreen()\n"
            "                )\n"
            "            )\n"
            "        }\n"
            "        return Result.success()\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "To isolate a multi-day memory creep, I correlate production telemetry (PSS, OOM events, session lengths) against specific features, reproduce the issue in lab conditions using automated stress tests (UI Automator/Monkey), and capture differential heap dumps in Android Studio or MAT to identify classes whose instance counts grow monotonically.",
        "best_answer": (
            "Isolating a slow, multi-day memory leak in production requires a systematic, data-driven approach combining telemetry, reproducible load testing, and heap diffing.\n\n"
            "1. **Triage via Production Telemetry**: First, I analyze production analytics to correlate memory growth. We track PSS (`Debug.getPss()`) and free heap metrics attached to heartbeat pings. I check whether the creep correlates with specific screens, app versions, or long-running background tasks (like location tracking or foreground services).\n\n"
            "2. **Lab Reproduction & Stress Testing**: Because we cannot attach debuggers to production devices for days, I reproduce the usage profile locally using automated test runners (`UI Automator` or `adb shell monkey`) running an accelerated loop of core app journeys continuously over several hours.\n\n"
            "3. **Differential Heap Analysis**: I capture a baseline heap dump at hour 1, and a comparison heap dump at hour 6. Using Eclipse MAT or Android Studio Memory Profiler, I run a **Heap Diff**. The culprit is rarely a destroyed Activity; it is almost always an unbounded collection—such as an in-memory analytics queue, an event bus observer map, or cached network tokens that append without eviction."
        ),
        "deep_answer": (
            "Under the hood, memory creep often hides inside native memory or static data structures rather than traditional Activity leaks. "
            "For instance, if an app uses WebViews, image decoders, or JNI libraries, native buffers or file descriptors (`lsof`) can leak without appearing as Java objects on the JVM heap. "
            "Using `dumpsys meminfo <package_name>` reveals whether the growth is in `Java Heap`, `Native Heap`, `Code`, or `Graphics`.\n\n"
            "If the Java Heap is clean but total process RSS climbs, the issue is native memory fragmentation or a C++ library leak, diagnosable using Android's native memory profiler (`heapprofd`).\n\n"
            "Once identified, the permanent fix involves introducing structural boundaries: converting unbounded lists to bounded circular FIFO buffers, utilizing `WeakReference` for dynamic registries, and enforcing automated LeakCanary and Macrobenchmark assertions in our staging pipeline."
        ),
        "follow_ups": [
            {
                "question": "What is PSS (Proportional Set Size) and why is it preferred over Private Dirty?",
                "answer": "PSS accounts for an app's private memory plus its proportional share of shared libraries and memory pages shared with other processes and Zygote. It provides the most accurate reflection of an app's true memory footprint on system RAM."
            },
            {
                "question": "How do you catch unbounded collections before they reach production?",
                "answer": "We enforce static analysis lint rules prohibiting unbounded static lists or maps, and require team members to use bounded collections like `LruCache` or ring buffers with explicit capacity caps."
            }
        ]
    },
    {
        "id": "MEM-22",
        "arabic_explanation": (
            "لماذا قد يتعرض الـ Main Thread للحظر والتجمد بالرغم من أنك أطلقت كودك داخل Coroutine (`launch`)؟\n\n"
            "1. الفهم الخاطئ لـ Coroutines والـ Dispatcher الافتراضي:\n"
            "   - الـ Coroutines لا تعني سحراً ينقل الكود إلى خلفية النظام تلقائياً!\n"
            "   - إطلاق الكوروتين عبر `lifecycleScope.launch` أو `viewModelScope.launch` ينفذ الكود افتراضياً على **`Dispatchers.Main`** (أي على الـ UI Thread نفسه).\n"
            "   - إذا وضعت كوداً يحظر المعالج (Blocking Code) داخل هذا الـ Coroutine، فإنك تحظر الـ Main Thread مباشرة وتتسبب في سقوط فريمات أو ANR!\n\n"
            "2. ما الذي يُعتبر حظراً للـ Thread (Thread-Blocking Call)؟\n"
            "   - استدعاء `Thread.sleep()` بدلاً من الدالة المعلقة `delay()`.\n"
            "   - تنفيذ قراءات ديسك متزامنة (`File.readBytes()`, `SharedPreferences.getString()`, `Room/SQLite raw queries`).\n"
            "   - استدعاءات شبكة متزامنة عبر `OkHttpClient.newCall().execute()` بدلاً من `await()`.\n"
            "   - معالجات حسابية ثقيلة (CPU-intensive مثل تشفير، ضغط صور، فك ضغط ملفات).\n\n"
            "3. الحل السليم:\n"
            "   - نقل العمليات الثقيلة صراحة إلى الموزع المناسب:\n"
            "     * `Dispatchers.IO`: لعمليات الديسك والشبكة (I/O operations).\n"
            "     * `Dispatchers.Default`: للعمليات الحسابية الثقيلة ومعالجة البيانات (CPU-bound work).\n"
            "   - تطبيق مبدأ **Main-Safety**: يجب أن تكون كل دالة `suspend` آمنة للاستدعاء من الـ Main Thread باستخدام `withContext` داخل الدالة نفسها."
        ),
        "practical_walkthrough": (
            "تطبيق مبدأ Main-Safety لتجنب حظر الـ Main Thread في Coroutines:\n"
            "```kotlin\n"
            "// ❌ كود خاطئ: إطلاق كوروتين على Main ولكن مع كود يحظر الـ Thread:\n"
            "fun loadConfigBad() {\n"
            "    viewModelScope.launch { // يعمل على Dispatchers.Main.immediate!\n"
            "        // 💥 قراءة ملف متزامنة تحظر الـ Main Looper وتسبب ANR:\n"
            "        val data = File(context.filesDir, \"config.json\").readText()\n"
            "        _uiState.value = parse(data)\n"
            "    }\n"
            "}\n"
            "\n"
            "// ✅ كود احترافي: تطبيق Main-Safety باستخدام withContext:\n"
            "class ConfigRepository(private val ioDispatcher: CoroutineDispatcher = Dispatchers.IO) {\n"
            "    // الدالة آمنة للاستدعاء من أي ثريد بما فيه Main:\n"
            "    suspend fun loadConfig(): Config = withContext(ioDispatcher) {\n"
            "        val raw = File(context.filesDir, \"config.json\").readText() // ينفذ على IO Thread بأمان\n"
            "        parseConfig(raw)\n"
            "    }\n"
            "}\n"
            "\n"
            "// في الـ ViewModel:\n"
            "fun loadConfigGood() {\n"
            "    viewModelScope.launch {\n"
            "        // الاستدعاء آمن تماماً، والـ Main thread لا يتم حظره أثناء القراءة:\n"
            "        val config = repository.loadConfig()\n"
            "        _uiState.value = config\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Launching a coroutine with `viewModelScope.launch` or `lifecycleScope.launch` runs on `Dispatchers.Main` by default. If the coroutine executes blocking operations like `Thread.sleep()`, synchronous file/DB I/O, or heavy CPU parsing without switching via `withContext(Dispatchers.IO)` or `Dispatchers.Default`, it blocks the Android main looper directly, triggering jank or an ANR.",
        "best_answer": (
            "The common misconception is that simply wrapping code inside a coroutine makes it asynchronous and backgrounded. In reality, coroutines are cooperatively scheduled tasks, and their execution thread is dictated strictly by their assigned `CoroutineDispatcher`.\n\n"
            "`viewModelScope` and `lifecycleScope` are explicitly configured to launch on **`Dispatchers.Main.immediate`** by design, allowing developers to manipulate UI state directly. "
            "If code inside that coroutine executes a thread-blocking call—such as `Thread.sleep()`, synchronous database queries, large JSON deserialization, or file reads—it blocks the underlying Java thread. Because that thread is the Android main thread, the Choreographer and MessageQueue freeze, causing dropped frames and ANRs.\n\n"
            "The architectural solution is adhering to the **Main-Safety convention**: every suspending function must be safe to invoke from the main thread. "
            "Data and domain layer functions should encapsulate their thread switching internally using `withContext(Dispatchers.IO)` for I/O and `withContext(Dispatchers.Default)` for CPU-intensive computations."
        ),
        "deep_answer": (
            "Under the hood, a coroutine suspends without blocking a thread only when calling cooperative suspending functions (like `delay()` or `suspendCancellableCoroutine`). "
            "If standard synchronous JVM blocking code is invoked, the thread's execution loop is monopolized at the OS thread level; the coroutine runtime has no power to preempt synchronous bytecode execution.\n\n"
            "Another subtle trap is **Dispatcher saturation** or using `runBlocking` on the main thread to wait for a coroutine launched on `Dispatchers.Main`. "
            "This causes an immediate, unrecoverable deadlock: the main thread blocks waiting for the coroutine to complete, while the coroutine is queued on the main looper waiting for the main thread to unblock.\n\n"
            "In unit testing and architecture enforcement, we inject `CoroutineDispatcher` instances via constructor injection (e.g. `@IoDispatcher ioDispatcher: CoroutineDispatcher`), enabling replacement with `StandardTestDispatcher` in tests and avoiding hardcoded dispatcher bugs."
        ),
        "follow_ups": [
            {
                "question": "What is the difference between `delay(1000)` and `Thread.sleep(1000)` inside a coroutine?",
                "answer": "`delay(1000)` suspends the coroutine, freeing the underlying thread to process other messages or UI events in the meantime. `Thread.sleep(1000)` blocks the entire physical thread, freezing everything running on that thread for one full second."
            },
            {
                "question": "What happens if you invoke `runBlocking` from the Android main thread?",
                "answer": "`runBlocking` halts the calling thread until the inner coroutine finishes. If the inner coroutine depends on main thread dispatching or takes longer than 5 seconds, it causes severe UI freezes or an instant ANR."
            }
        ]
    },
    {
        "id": "MEM-23",
        "arabic_explanation": (
            "تشخيص وعلاج تجمد التطبيق (App Freeze) الذي يحدث فقط عند فك تشفير صورة كبيرة (Decoding Large Image):\n\n"
            "1. الأسباب الجذرية لتجمد التطبيق عند فك تشفير الصور:\n"
            "   - **Main Thread Decoding**: استدعاء `BitmapFactory.decode*` مباشرة على الـ UI Thread؛ فك تشفير صورة بدقة 20 ميجابكسل يستغرق 300-800ms من الحسابات الثقيلة، مما يجمد الشاشة ويسقط عشرات الفريمات.\n"
            "   - **Out of Memory Heap Thrashing**: الصورة تستهلك عشرات الميجابايتات؛ قبل حدوث OOM صريح، يحاول الـ Garbage Collector القيام بـ GC Compactions متتالية في وضع Stop-The-World في محاولة يائسة لتوفير مساحة متصلة، مما يوقف التطبيق لعدة ثوانٍ.\n\n"
            "2. التشخيص المنهجي (Diagnosis Workflow):\n"
            "   - فحص الـ **Logcat**: البحث عن رسائل `Choreographer: Skipped XX frames` أو رسائل ART GC مثل `Background concurrent copying GC freed ...` متكررة.\n"
            "   - فتح **CPU Profiler**: تشغيل System Trace ورؤية هل الـ `main` thread مشغول في دالة `BitmapFactory.nativeDecodeStream()`.\n"
            "   - فحص **Memory Profiler**: رؤية قفزة هائلة في مساحة الذاكرة (Native أو Java Heap) بالتزامن مع لحظة الضغط على الصورة.\n\n"
            "3. الحل الهندسي المتكامل:\n"
            "   - **نقل فك التشفير إلى Background Thread**: استخدام `withContext(Dispatchers.IO)`.\n"
            "   - **Subsampling (inJustDecodeBounds & inSampleSize)**: قراءة أبعاد الصورة الأصلية أولاً دون تحميل بكسلاتها، ثم حساب معامل التصغير المناسب لحجم الشاشة فقط.\n"
            "   - **Bitmap Region Decoder**: للصور العملاقة والخرائط، فك تشفير الجزء المعروض على الشاشة فقط (`BitmapRegionDecoder`)."
        ),
        "practical_walkthrough": (
            "كود فك تشفير صورة آمن هندسياً ومحمي من التجمد والـ OOM:\n"
            "```kotlin\n"
            "suspend fun decodeSampledBitmapFromUri(\n"
            "    context: Context,\n"
            "    uri: Uri,\n"
            "    reqWidth: Int,\n"
            "    reqHeight: Int\n"
            "): Bitmap? = withContext(Dispatchers.IO) { // 1. ضمان التنفيذ في Background Thread تماماً\n"
            "    // 2. قراءة الأبعاد فقط دون حجز ذاكرة للبكسلات:\n"
            "    val options = BitmapFactory.Options().apply {\n"
            "        inJustDecodeBounds = true\n"
            "    }\n"
            "    context.contentResolver.openInputStream(uri)?.use {\n"
            "        BitmapFactory.decodeStream(it, null, options)\n"
            "    }\n"
            "\n"
            "    // 3. حساب معامل التصغير المناسب (Power of 2):\n"
            "    var inSampleSize = 1\n"
            "    val (height: Int, width: Int) = options.outHeight to options.outWidth\n"
            "    if (height > reqHeight || width > reqWidth) {\n"
            "        val halfHeight = height / 2\n"
            "        val halfWidth = width / 2\n"
            "        while (halfHeight / inSampleSize >= reqHeight && halfWidth / inSampleSize >= reqWidth) {\n"
            "            inSampleSize *= 2\n"
            "        }\n"
            "    }\n"
            "    options.inSampleSize = inSampleSize\n"
            "    options.inJustDecodeBounds = false\n"
            "\n"
            "    // 4. فك تشفير الصورة بالمقاس المخفض المناسب للشاشة:\n"
            "    context.contentResolver.openInputStream(uri)?.use {\n"
            "        BitmapFactory.decodeStream(it, null, options)\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "App freezes during image decoding are caused by decoding high-resolution images synchronously on the main thread, or triggering severe GC thrashing from multi-megabyte allocations. Diagnosis involves using CPU Profiler's System Trace to locate `BitmapFactory.nativeDecode` and Memory Profiler to inspect heap spikes. Resolution requires decoding on `Dispatchers.IO` using `inSampleSize` downsampling.",
        "best_answer": (
            "An app freeze localized to image decoding points to two culprits: executing the decode operation synchronously on the main thread, or triggering intense Garbage Collector thrashing due to severe memory pressure.\n\n"
            "1. **Diagnosis**: I begin by reproducing the freeze with the **Android Studio CPU Profiler** recording a System Trace. If the Flame Chart reveals `BitmapFactory.nativeDecodeStream()` occupying hundreds of milliseconds on the `main` thread, the root cause is thread misplacement. "
            "Concurrently, in the Memory Profiler, I check whether memory spikes into near-OOM territory. If memory is exhausted, ART executes back-to-back compacting GCs, freezing application threads in Stop-The-World pauses.\n\n"
            "2. **Resolution**: First, all decoding must be isolated on a background dispatcher (`Dispatchers.IO`). "
            "Second, we must avoid full-resolution decodes by implementing two-pass downsampling: using `BitmapFactory.Options.inJustDecodeBounds = true` to query the image's raw dimensions with zero pixel allocation, calculating a power-of-two `inSampleSize` matching the destination ImageView bounds, and decoding only the scaled-down bitmap."
        ),
        "deep_answer": (
            "Under the hood, `BitmapFactory` utilizes native Skia C++ decoders (`libskia.so`). "
            "When dealing with ultra-high-resolution images (such as architectural diagrams or 100-megapixel panoramas), downsampling still degrades quality if users need to zoom in. "
            "In those cases, the production standard is using `BitmapRegionDecoder`, which decodes only the visible viewport tile on demand as the user pans and zooms.\n\n"
            "Another nuance is color depth: by default, `BitmapFactory` decodes in `ARGB_8888` (4 bytes/pixel). "
            "If alpha transparency is unnecessary, decoding using `RGB_565` (2 bytes/pixel) cuts memory consumption by 50% immediately.\n\n"
            "In modern enterprise apps, rather than writing custom `BitmapFactory` code, we rely on established libraries like **Coil**, configuring custom `Decoder.Factory` components and enabling `Bitmap.Config.HARDWARE` to offload bitmap storage to GPU graphic buffers."
        ),
        "follow_ups": [
            {
                "question": "Why must `inSampleSize` ideally be a power of two?",
                "answer": "`BitmapFactory` decoders can optimize decoding by skipping decoder passes when `inSampleSize` is a power of 2 (2, 4, 8), resulting in substantially faster native decoding compared to non-power-of-two ratios."
            },
            {
                "question": "What is `BitmapRegionDecoder` and when is it preferred?",
                "answer": "`BitmapRegionDecoder` decodes specific rectangular sub-regions of a large image on demand, which is essential for map viewers and deep-zoom image galleries to prevent loading the full multi-hundred-megabyte image into RAM."
            }
        ]
    },
    {
        "id": "MEM-24",
        "arabic_explanation": (
            "كيفية تسريع بدء تشغيل التطبيق البطيء (Slow App Startup) دون الإخلال بصحة العمل وسلوك التطبيق:\n\n"
            "1. استراتيجية تقليص وقت الـ Cold Start:\n"
            "   - **قياس دقيق قبل أي تعديل**: استخدام Macrobenchmark و System Trace (Perfetto) لمعرفة التوقيت الدقيق لكل جزء من `Application.onCreate` و `Activity.onCreate`.\n"
            "   - معرفة الـ Time to Initial Display (TTID) والـ Time to Full Display (TTFD).\n\n"
            "2. تفكيك عنق الزجاجة في `Application.onCreate`:\n"
            "   - تطبيقات كثيرة تقوم بتهيئة 15 مكتبة SDK مختلفة في `Application.onCreate` بشكل متزامن على الـ Main Thread (Analytics, Crashlytics, Ads, Push Notifications, Payment, Security, DeepLinks).\n"
            "   - الحل: تصنيف الـ SDKs إلى ثلاث فئات:\n"
            "     * **حرجة فورية (Critical)**: مثل Crashlytics و Security checks (تظل في `onCreate`).\n"
            "     * **يمكن تأجيلها للـ Background Thread**: مثل تتبع التحليلات وقواعد البيانات؛ تشغيلها عبر Coroutine في Background Dispatcher.\n"
            "     * **تهيئة بالطلب (Lazy / On-demand)**: مثل SDK الدفع والخرائط؛ لا يتم تهيئتها إلا عندما يفتح المستخدم شاشتها فعلياً!\n\n"
            "3. استخدام حزمة Baseline Profiles و App Startup:\n"
            "   - تضمين Baseline Profile لتجميع كود الـ Startup عبر AOT مسبقاً.\n"
            "   - استخدام مكتبة Jetpack **App Startup** لتوحيد الـ ContentProviders في Provider واحد منظم.\n"
            "   - استدعاء `reportFullyDrawn()` فور اكتمال أول قائمة بالبيانات."
        ),
        "practical_walkthrough": (
            "هندسة تهيئة الـ SDKs بشكل غير متزامن وكسول في Application class:\n"
            "```kotlin\n"
            "class OptimizedApplication : Application() {\n"
            "    private val appScope = CoroutineScope(SupervisorJob() + Dispatchers.Default)\n"
            "\n"
            "    override fun onCreate() {\n"
            "        super.onCreate()\n"
            "        // 1. فقط المكونات الحرجة فورياً تُهيأ على الـ Main Thread:\n"
            "        initializeCrashReporting()\n"
            "\n"
            "        // 2. ترحيل باقي الـ SDKs الثقيلة إلى Background Thread:\n"
            "        appScope.launch {\n"
            "            initializeAnalyticsAsync()\n"
            "            preloadCacheDataAsync()\n"
            "        }\n"
            "    }\n"
            "\n"
            "    private fun initializeCrashReporting() {\n"
            "        // Crashlytics خفيفة وحرجة لالتقاط أي انهيار فوري أثناء التشغيل\n"
            "    }\n"
            "\n"
            "    private suspend fun initializeAnalyticsAsync() = withContext(Dispatchers.IO) {\n"
            "        // تهيئة أدوات التحليلات وقراءة المعرفات دون حظر الـ Main Thread\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "To reduce slow startup without breaking correctness, I profile cold start using Perfetto and Macrobenchmark, audit `Application.onCreate()` to defer non-critical SDKs to background threads or lazy on-demand initialization, integrate Jetpack App Startup to eliminate ContentProvider bloat, and package Baseline Profiles to precompile hot startup paths.",
        "best_answer": (
            "Reducing slow app startup requires surgical optimization of the cold launch path while preserving dependency guarantees.\n\n"
            "1. **Baseline Measurement**: I never optimize blindly. I measure baseline cold start times using Jetpack Macrobenchmark and inspect a Perfetto trace to identify wide methods executing between process fork and the first frame.\n\n"
            "2. **Deconstructing `Application.onCreate`**: The number one startup inhibitor is synchronous SDK initialization. I categorize every library:\n"
            "   - *Critical at Launch* (e.g. Crashlytics, DI initialization, security attestation): Kept synchronous on the main thread.\n"
            "   - *Deferred Background* (e.g. Analytics, remote config, push registration): Dispatched immediately on background coroutines (`Dispatchers.Default` / `IO`).\n"
            "   - *Lazy On-Demand* (e.g. Maps SDK, Payment gateways): Initialized only when the respective feature is accessed.\n\n"
            "3. **Eliminating ContentProvider Overhead**: Many libraries leverage implicit ContentProviders for zero-code setup, which execute before `Application.onCreate()` on the main thread. I disable automatic providers and consolidate them using Jetpack App Startup.\n\n"
            "4. **AOT Compilation via Baseline Profiles**: We package an automated Baseline Profile to ensure ART precompiles startup classes Ahead-Of-Time."
        ),
        "deep_answer": (
            "Under the hood, layout inflation in the launch Activity often consumes 30-40% of TTID (Time to Initial Display). "
            "To streamline this, we simplify the landing screen hierarchy, avoid complex nested view hierarchies, and adopt Jetpack Compose with strict skippability rules.\n\n"
            "Another critical technique is **Splash Screen Window Backgrounding**. "
            "Using the modern `androidx.core.splashscreen.SplashScreen` API, the system window displays an immediate branded background drawable before app code is even loaded into ART, eliminating perceived latency for the user.\n\n"
            "To guarantee correctness during asynchronous initialization, if a deferred SDK (like user identity) is required by a secondary screen, we model initialization as a deferred StateFlow or `CompletableDeferred` so downstream dependencies cleanly await readiness without blocking the UI thread."
        ),
        "follow_ups": [
            {
                "question": "What happens if a deferred SDK is needed before background initialization finishes?",
                "answer": "We wrap the initialization in a thread-safe `CompletableDeferred` or `StateFlow`. Any component requesting the SDK suspends cooperatively until initialization completes, preserving correctness without blocking the main looper."
            },
            {
                "question": "How does Jetpack App Startup improve over individual ContentProviders?",
                "answer": "Each ContentProvider adds process-level instantiation and binder overhead. Jetpack App Startup merges multiple component initializers into a single `InitializationProvider`, sorting initializers topologically to resolve dependencies cleanly."
            }
        ]
    },
    {
        "id": "MEM-25",
        "arabic_explanation": (
            "كيفية العثور على تشخيص الـ ANR النادر الناتج عن تزاحم الأقفال على قاعدة البيانات (Database Lock Contention):\n\n"
            "1. ما هو تزاحم أقفال قاعدة البيانات (Database Lock Contention)؟\n"
            "   - قواعد بيانات SQLite و Room تستخدم آليات حماية (Locking mechanisms) لضمان اتساق البيانات.\n"
            "   - أثناء كتابة بيانات ضخمة (Transaction) في Background Thread، تقوم SQLite بحجز قفل حصري (Exclusive Lock) على ملف قاعدة البيانات.\n"
            "   - إذا حاول الـ Main Thread تنفيذ استعلام قراءة (Query) أو حتى قراءة SharedPreferences متزامنة تشارك نفس الملف، يضطر الـ Main Thread للانتظار حتى ينتهي الـ Transaction بالكامل.\n"
            "   - إذا استغرقت المعاملة أكثر من 5 ثوانٍ، يطلق النظام تحذير ANR فوراً!\n\n"
            "2. كيفية العثور على هذا الـ ANR النادر وتشخيصه:\n"
            "   - فحص ملف **`/data/anr/traces.txt`**:\n"
            "     * النظر إلى حالة الـ `\"main\"` thread: ستجد حالته `BLOCKED` أو `WAITING` مع سطر يشير إلى انتظار قفل: `waiting to lock <0x...>`.\n"
            "     * البحث عن الـ Thread الآخر الذي يحمل القفل (Held by thread X): ستجد background thread ينفذ `sqlite3_step` أو `room.RoomDatabase.beginTransaction`.\n"
            "   - استخدام **Perfetto System Trace**: البحث عن شرائح SQLite والتحقق من Lock Contention.\n\n"
            "3. الحلول الهندسية لمنع التزاحم:\n"
            "   - **تفعيل WAL Mode (Write-Ahead Logging)**: في وضع WAL، القراءات والكتابات لا تحظر بعضها البعض! يستطيع قارئ القراءة في نفس اللحظة التي يكتب فيها كاتب.\n"
            "   - **عدم تنفيذ أي استعلام لقاعدة البيانات على الـ Main Thread**: حظر استدعاء `.allowMainThreadQueries()` في Room نهائياً والاعتماد على Kotlin Flow و Coroutines.\n"
            "   - تقليص حجم المعاملات (Batch transactions in smaller chunks) لتفادي احتجاز القفل لفترات طويلة."
        ),
        "practical_walkthrough": (
            "تفعيل وضع WAL والتأكد من تنفيذ المعاملات بشكل آمن في Room:\n"
            "```kotlin\n"
            "// 1. تفعيل Write-Ahead Logging (WAL) في بناء الـ Room Database:\n"
            "val db = Room.databaseBuilder(context, AppDatabase::class.java, \"app_db\")\n"
            "    .setJournalMode(RoomDatabase.JournalMode.WRITE_AHEAD_LOGGING) // يسمح بالقراءة والكتابة المتزامنة!\n"
            "    // ❌ تجنب allowMainThreadQueries() تماماً لمنع أي ANR محتمل:\n"
            "    // .allowMainThreadQueries()\n"
            "    .build()\n"
            "\n"
            "// 2. تقسيم عمليات الإدخال الضخمة إلى دفعات صغيرة مع فترات راحة:\n"
            "suspend fun batchInsertSafely(items: List<RecordEntity>) = withContext(Dispatchers.IO) {\n"
            "    items.chunked(100).forEach { chunk ->\n"
            "        db.recordDao().insertChunk(chunk)\n"
            "        // إتاحة فرصة للمعاملات الأخرى للتنفيذ دون احتجاز قفل مستمر:\n"
            "        yield()\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "To diagnose database lock contention ANRs, I inspect `/data/anr/traces.txt` to find the UI thread `BLOCKED` waiting on a database mutex held by a background writer thread. We fix this by enabling SQLite Write-Ahead Logging (WAL mode), eliminating any main-thread database access, and chunking large write transactions.",
        "best_answer": (
            "A rare ANR stemming from database lock contention occurs when the main thread attempts to execute a database query while a background worker holds an exclusive lock on the SQLite file during a large write transaction.\n\n"
            "1. **Isolation in ANR Traces**: I examine `/data/anr/traces.txt`. In lock contention scenarios, the `\"main\"` thread is not in `RUNNABLE` (which would imply heavy computation), but in **`BLOCKED`** or `WAITING` waiting to acquire a monitor lock (e.g. `android.database.sqlite.SQLiteConnectionPool`). "
            "The trace explicitly notes `waiting to lock <0x...> held by thread [pool-X-thread-Y]`. Following that thread ID reveals a background worker deep inside `sqlite3_step` executing a long-running batch insert or migration.\n\n"
            "2. **System Tracing via Perfetto**: Opening a Perfetto trace shows the main thread stalled in `SQLiteConnectionPool.waitForConnection` while disk I/O slices saturate the I/O queue.\n\n"
            "3. **Resolution**:\n"
            "   - Enable **Write-Ahead Logging (WAL)** via `RoomDatabase.JournalMode.WRITE_AHEAD_LOGGING`. Under WAL mode, readers do not block writers, and writers do not block readers.\n"
            "   - Strictly audit code to eliminate `.allowMainThreadQueries()`, forcing all queries to return `Flow` or suspend.\n"
            "   - Chunk massive multi-record imports into smaller transactions."
        ),
        "deep_answer": (
            "Under traditional SQLite Rollback Journal mode, any write transaction locks the entire database file exclusively; no read connections can proceed until the transaction commits and writes to disk. "
            "Under WAL mode, SQLite appends changes to a separate `-wal` file, allowing readers to read from the unmodified main database while writing occurs concurrently.\n\n"
            "However, even with WAL mode, lock contention can still occur if multiple writers compete for the single write connection, or if SQLite triggers an automatic **WAL Checkpoint** on a thread executing a read. "
            "To prevent checkpoint stalls, high-volume apps configure custom connection pools or schedule explicit background checkpoints during device idle windows.\n\n"
            "In Room, we also configure a dedicated query executor (`setQueryExecutor`) distinct from general background dispatchers to guarantee that disk-heavy queries never starve high-priority background UI tasks."
        ),
        "follow_ups": [
            {
                "question": "Why does WAL (Write-Ahead Logging) mode allow concurrent readers and writers?",
                "answer": "WAL writes modifications sequentially to an auxiliary `-wal` file without altering the primary database file immediately. Readers read consistent snapshots from the main DB and WAL index simultaneously without waiting for write transactions to finish."
            },
            {
                "question": "What is `yield()` doing in batch insertion loops?",
                "answer": "`yield()` checks for coroutine cancellation and gives other dispatchable coroutines a chance to execute on the thread, preventing a tight loop from starving other cooperative background tasks."
            }
        ]
    },
    {
        "id": "MEM-26",
        "arabic_explanation": (
            "كيفية إنشاء ميزانيات أداء قابلة للقياس (Performance Budgets) واختبارات منع التراجع (Regression Tests):\n\n"
            "1. ما هي ميزانية الأداء (Performance Budget)؟\n"
            "   - هي حدود رقمية صارمة متفق عليها هندسياً لا يُسمح لأي كود جديد بتجاوزها.\n"
            "   - أمثلة على الميزانيات العملية في تطبيقات Android الاحترافية:\n"
            "     * **Cold Startup**: أقل من 1.2 ثانية على جهاز مرجعي متوسط (Pixel 4a أو ما يوازيه).\n"
            "     * **Frame Timing / Jank**: أقل من 2% من الفريمات تتجاوز 16ms أثناء سكرول القائمة الرئيسية.\n"
            "     * **Memory Footprint**: ألا يتجاوز استهلاك الذاكرة الأساسي (Baseline PSS) 150MB.\n"
            "     * **APK / AAB Size**: ألا تزيد حزمة التطبيق عن 25MB، مع حد أقصى للزيادة لكل PR لا يتعدى 200KB.\n\n"
            "2. أتمتة اختبارات منع التراجع (Regression Testing in CI/CD):\n"
            "   - استخدام **Jetpack Macrobenchmark**: تشغيل سيناريوهات القياس آلياً في CI على Physical Device Farm.\n"
            "   - دمج فحص حجم الـ APK عبر **Diffuse** أو أداة تحليل الحزم: مقارنة الـ PR الحالي مع فرع `main`.\n"
            "   - استخدام **LeakCanary in Instrumentation Tests**: تشغيل مسار المستخدم والتأكد من خلوه تماماً من أي تسريب ذاكرة قبل دمج الكود.\n\n"
            "3. مراقبة الإنتاج وإغلاق الحلقة (Production Observability):\n"
            "   - ربط مؤشرات Android Vitals و Firebase Performance بـ Alerting System (مثل PagerDuty / Slack).\n"
            "   - تطبيق نظام الفحص المرحلي (Phased Rollouts): إيقاف طرح التحديث إذا تجاوز معدل الـ ANRs أو الـ Crashes العتبة المتفق عليها."
        ),
        "practical_walkthrough": (
            "كتابة اختبار Macrobenchmark يفرض ميزانية أداء صارمة ويمنع التراجع في CI:\n"
            "```kotlin\n"
            "@RunWith(AndroidJUnit4::class)\n"
            "class StartupPerformanceTest {\n"
            "    @get:Rule\n"
            "    val benchmarkRule = MacrobenchmarkRule()\n"
            "\n"
            "    @Test\n"
            "    fun coldStartupBudget_mustBeUnder1200ms() {\n"
            "        benchmarkRule.measureRepeated(\n"
            "            packageName = \"com.example.app\",\n"
            "            metrics = listOf(StartupTimingMetric()),\n"
            "            iterations = 5,\n"
            "            startupMode = StartupMode.COLD\n"
            "        ) {\n"
            "            pressHome()\n"
            "            startActivityAndWait()\n"
            "        }\n"
            "        // يتم جمع مقاييس زمن التشغيل ومقارنتها تلقائياً مع ميزانية الأداء في خط أنابيب CI\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "To enforce performance budgets, I define explicit numeric thresholds for cold start (<1.2s), jank rate (<2%), memory baseline, and APK size. We automate regression tests in CI using Macrobenchmark on physical testbeds, compare binary deltas using tools like Diffuse, and enforce blocking PR checks alongside production Android Vitals alerts.",
        "best_answer": (
            "Establishing performance budgets transforms performance from an afterthought into a measurable engineering contract.\n\n"
            "1. **Defining Explicit Numeric Budgets**: In an enterprise Android app, we define contracts around four core pillars:\n"
            "   - **Startup Latency**: Cold start < 1,200ms, Warm start < 800ms on reference mid-tier hardware.\n"
            "   - **Render Smoothness**: Frame drop rate < 2% and zero frozen frames (>700ms) during standard user flows.\n"
            "   - **Memory Retained Size**: Process baseline PSS < 160MB, with 0 detected leaks.\n"
            "   - **Binary Size**: Max APK download size of 30MB, with PR budget capped at +250KB.\n\n"
            "2. **Automating CI Regression Testing**: We integrate **Jetpack Macrobenchmark** running on a dedicated physical device farm (or Firebase Test Lab). Macrobenchmark measures startup timing and frame duration over multiple iterations, generating JSON results that compare pull requests against the target branch.\n\n"
            "3. **Gating & Tooling**: We use **Diffuse** in GitHub Actions to comment detailed DEX, resource, and asset size diffs on every PR. If a benchmark exceeds budget thresholds by >5%, the CI build fails automatically."
        ),
        "deep_answer": (
            "Under the hood, executing reliable performance tests in CI requires eliminating thermal and CPU throttling noise. "
            "Running Macrobenchmark requires a rooted physical test device configured with locked CPU clock frequencies (`adb shell stop; adb shell setprop ...`) to ensure stable run-to-run variance under 2%.\n\n"
            "For memory regression testing, we utilize LeakCanary's instrumentation test runner (`LeakAssertions.assertNoLeaks()`). "
            "Running UI journeys via Espresso or UI Automator finishes with an automated leak check that dumps heap and fails the test if any destroyed Activity or View remains retained.\n\n"
            "Finally, in production, we close the feedback loop using Firebase Performance Monitoring and Google Play Vitals API. "
            "If an incremental rollout in production breaches the ANR threshold (>0.47%) or cold launch SLA, an automated webhook halts the phased release in Google Play Console."
        ),
        "follow_ups": [
            {
                "question": "How do you handle variance and flaky results in performance CI tests?",
                "answer": "We run Macrobenchmark tests for 5-10 iterations, take the median (50th percentile) and 95th percentile metrics, lock CPU clocks on dedicated physical test devices, and allow a minor margin of tolerance (e.g. ±3%) before failing the build."
            },
            {
                "question": "What is the tool Diffuse and how does it prevent app bloat?",
                "answer": "Diffuse is an open-source APK/AAB diffing tool by Jake Wharton that breaks down byte changes across DEX code, resources, assets, and compression, giving PR reviewers an exact view of what contributed to size increases."
            }
        ]
    }
]

def main() -> None:
    if DATA_FILE.exists():
        existing = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        by_id = {item["id"]: item for item in existing}
    else:
        by_id = {}

    for item in MEM_20_26:
        by_id[item["id"]] = item

    output = [by_id[k] for k in sorted(by_id.keys())]
    DATA_FILE.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {DATA_FILE} with questions MEM-20 to MEM-26. Total questions: {len(output)}")

if __name__ == "__main__":
    main()
