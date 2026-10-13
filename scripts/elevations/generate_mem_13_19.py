#!/usr/bin/env python3
"""Generator for MEM-13 through MEM-19 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "mem.json"

MEM_13_19 = [
    {
        "id": "MEM-13",
        "arabic_explanation": (
            "تأثير حجز الـ Bitmaps ومكتبات تحميل الصور (مثل Coil و Glide) على الذاكرة في Android:\n\n"
            "1. كيف تُخزن الـ Bitmaps في الذاكرة عبر إصدارات Android؟\n"
            "   - في إصدارات قديمة (Android 3.0 إلى 7.1)، كانت بكسلات الـ Bitmap تُخزن في الـ **Java Heap**، مما كان يملأ الـ Heap سريعاً ويفجر `OutOfMemoryError`.\n"
            "   - منذ Android 8.0 (API 26+)، نُقلت بكسلات الـ Bitmap إلى **Native Memory** (C++ Heap) باستخدام كائنات `NativeAllocationRegistry`.\n"
            "   - هذا يمنع ملء الـ Java Heap المباشر، لكنه لا يعني ذاكرة غير محدودة! النظام لا يزال يفرض حدوداً صارمة على إجمالي استهلاك الذاكرة (Process RSS)، وإذا نفدت الذاكرة يُقتل التطبيق بواسطة Low Memory Killer (LMK).\n\n"
            "2. معادلة حساب حجم الـ Bitmap في الذاكرة:\n"
            "   - الحجم بالبايت = `العرض (Width) × الارتفاع (Height) × عدد البايتات لكل بكسل (Bytes Per Pixel)`.\n"
            "   - مع تنسيق `ARGB_8888` القياسي، كل بكسل يستهلك 4 بايت.\n"
            "   - صورة بدقة كاميرا حديثة (4000 × 3000 بكسل) = `12,000,000 × 4 = 48MB` من الذاكرة لصورة واحدة فقط! إذا عُرضت في ImageView بحجم 200×200 دون تصغير (Downsampling)، يتم هدر 47.8MB!\n\n"
            "3. دور مكتبات تحميل الصور الحديثة (Coil / Glide):\n"
            "   - **Downsampling**: قراءة أبعاد الـ ImageView ومطابقة مقاس الـ Bitmap عبر `inSampleSize` في `BitmapFactory.Options` قبل فك التشفير.\n"
            "   - **Memory Caching**: كاش ذكي مبني على `LruCache` يخزن صوراً بحجم الشاشة فقط ويحرر الأقدم عند الضغط.\n"
            "   - **Bitmap Pooling** (`inBitmap`): إعادة استخدام مساحات البايت المحجوزة بالفعل بدلاً من حجز وتحرير مستمر يسبب GC Churn."
        ),
        "practical_walkthrough": (
            "توضيح الفارق بين فك تشفير مباشر كارثي واستخدام مكتبة ذكية مثل Coil:\n"
            "```kotlin\n"
            "// ❌ كود بدائي خطير: فك تشفير الصورة كاملة بالحجم الأصلي يسبب OOM فوراً:\n"
            "val bitmap = BitmapFactory.decodeFile(photoFile.absolutePath) // 48MB في الذاكرة!\n"
            "imageView.setImageBitmap(bitmap)\n"
            "\n"
            "// ✅ استخدام مكتبة حديثة (Coil) لتطبيق Downsampling وإعادة التدوير تلقائياً:\n"
            "imageView.load(photoFile) {\n"
            "    crossfade(true)\n"
            "    placeholder(R.drawable.placeholder)\n"
            "    size(ViewSizeResolver(imageView)) // فك تشفير البكسلات المناسبة لمقاس العرض فقط!\n"
            "    transformations(RoundedCornersTransformation(16f))\n"
            "    // Coil تستخدم Coroutines و OkHttp و LruCache في الذاكرة دون حظر الـ Main Thread\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Bitmaps are the single largest consumer of Android memory. Since Android 8.0, pixel data resides in Native Memory, but unscaled decoding easily exhausts system limits. Modern image libraries like Coil and Glide prevent OOMs by automatically downsampling images to match target view dimensions, caching via LRU policies, and reusing buffers via bitmap pooling.",
        "best_answer": (
            "Bitmaps are historically the primary trigger for `OutOfMemoryError` in Android applications due to their raw uncompressed pixel footprint.\n\n"
            "The memory required for a decoded bitmap is calculated as `Width × Height × BytesPerPixel`. "
            "Under the standard `ARGB_8888` configuration (4 bytes per pixel), decoding a standard 12-megapixel camera image consumes 48 megabytes of memory. "
            "If loaded directly into a 200×200 avatar view, over 99% of that memory is completely wasted.\n\n"
            "While Android 8.0 (API 26) migrated bitmap pixel storage from Java Heap to Native Memory using `NativeAllocationRegistry`, native memory is still constrained by total device physical RAM and OS process limits. "
            "Excessive native allocations trigger the Android Low Memory Killer (LMK).\n\n"
            "Modern image-loading libraries like Coil and Glide solve this through three core mechanics:\n"
            "1. **Automatic Downsampling**: Inspecting target view bounds and using `inSampleSize` to decode only the required pixel density.\n"
            "2. **Multi-tier Caching**: Using memory-bounded `LruCache` (configured as a fraction of available RAM) alongside disk caching.\n"
            "3. **Bitmap Re-use / Pooling**: Re-using existing bitmap buffers via `BitmapFactory.Options.inBitmap` to eliminate memory churn."
        ),
        "deep_answer": (
            "From an architectural standpoint, Coil represents the modern Kotlin-first approach. Built entirely on Kotlin Coroutines and OkHttp, Coil integrates with Android's lifecycle to automatically cancel image decoding when a View is detached or its lifecycle transitions to `DESTROYED`.\n\n"
            "On Android 8.0+, we can also configure images to use `Bitmap.Config.HARDWARE`. "
            "Hardware bitmaps store pixel memory directly in GPU graphic memory (GraphicBuffer), making them immutable and impossible to read from software canvases, but providing zero CPU-side memory allocation and blazingly fast draw calls.\n\n"
            "When profiling image-heavy screens in Android Studio Memory Profiler, we look at the **Native** memory bar and heap allocation stack traces originating from `BitmapFactory.nativeDecodeStream()`. "
            "If bitmap allocations surge during scrolling, it indicates missing view sizing or disabled image caches."
        ),
        "follow_ups": [
            {
                "question": "What is `Bitmap.Config.HARDWARE`, and when should you avoid it?",
                "answer": "HARDWARE bitmaps store pixels directly in GPU memory, dramatically reducing RAM usage and speeding up rendering. However, they are immutable and cannot be drawn to software Canvases or modified via pixel manipulation methods like `getPixel()` without crashing or throwing an exception."
            },
            {
                "question": "How does `inBitmap` help reduce garbage collection churn?",
                "answer": "`inBitmap` instructs `BitmapFactory` to reuse an already allocated byte buffer for a new bitmap of compatible dimensions and format instead of allocating new heap/native memory and discarding the old one, preventing GC allocation spikes."
            }
        ]
    },
    {
        "id": "MEM-14",
        "arabic_explanation": (
            "كيفية تحليل الـ Heap Dump واستخدام أداة LeakCanary لاكتشاف تسريبات الذاكرة في بيئة الإنتاج والتطوير:\n\n"
            "1. ما هو الـ Heap Dump؟\n"
            "   - الـ Heap Dump هو لقطة ثنائية (Binary Snapshot بتنسيق HPROF) تحتوي على جميع الكائنات، والمصفوفات، والمراجع، والـ Primitive Fields الحية داخل ذاكرة الـ Heap في لحظة التقاطها.\n"
            "   - يمكن استخراجه يدوياً عبر Android Studio Profiler (زر Dump Java Heap) أو برمجياً عبر `Debug.dumpHprofData()`.\n\n"
            "2. كيف تعمل أداة LeakCanary؟\n"
            "   - تراقب دورات حياة الـ Activities والـ Fragments والـ ViewModels والـ Root Views تلقائياً عبر `ActivityLifecycleCallbacks` و `FragmentLifecycleCallbacks`.\n"
            "   - عند تدمير النشاط (`onDestroy()`)، تضع مرجع النشاط داخل `KeyedWeakReference` وتنتظر 5 ثوانٍ.\n"
            "   - إذا ظل الكائن موجوداً بعد 5 ثوانٍ، تُجبر الـ GC على العمل للتحقق.\n"
            "   - إذا ظل الكائن حياً، تعلن LeakCanary أن الكائن **مُحتجز (Retained)**، وتقوم بتوليد HPROF dump وتحليله في خلفية التطبيق باستخدام محرك **Shark** (محلل HPROF كوتلن فائق السرعة).\n\n"
            "3. قراءة سلسلة التسريب (Leak Trace / Retained Path):\n"
            "   - يبدأ التقرير من **GC Root** (مثل Thread نشط، أو Static Variable، أو Native Global Ref).\n"
            "   - يوضح مسار الإشارات (References) وصولاً إلى الـ Leaked Object.\n"
            "   - يبين الـ Leak Trace بدقة أي مرجع يُشتبه في أنه السبب (مُحدد بـ `Leaking: YES` مقابل `Leaking: NO`)."
        ),
        "practical_walkthrough": (
            "تثبيت وقراءة مخرجات LeakCanary وتحليل Heap Dump في Android Studio:\n"
            "```kotlin\n"
            "// 1. إضافة LeakCanary في build.gradle.kts (تعمل تلقائياً في debug فقط دون كود إضافي):\n"
            "dependencies {\n"
            "    debugImplementation(\"com.squareup.leakcanary:leakcanary-android:2.14\")\n"
            "}\n"
            "\n"
            "// 2. نموذج للـ Leak Trace الناتج عن تحليل LeakCanary:\n"
            "/*\n"
            "┬───\n"
            "│ GC Root: System class / Static field\n"
            "│\n"
            "├─ com.example.app.UserManager class\n"
            "│    Leaking: NO (Static class is never leaking)\n"
            "│    ↓ static UserManager.currentContext\n"
            "├─ com.example.app.DetailActivity instance\n"
            "│    Leaking: YES (Activity has been destroyed: onDestroy() called)\n"
            "│    Retaining: 24.3 MB across 1,420 objects\n"
            "╰→ com.example.app.DetailActivity\n"
            "*/\n"
            "```"
        ),
        "quick_answer": "LeakCanary detects leaks automatically in debug builds by tracking destroyed Activities/Fragments via `WeakReference`, prompting a heap dump, and parsing the HPROF file with Shark. Analyzing a heap dump in Android Studio Profiler or LeakCanary involves identifying the GC Root, following the retained reference chain, and determining which reference prevented legitimate garbage collection.",
        "best_answer": (
            "Analyzing memory leaks requires capturing a heap dump (.hprof file) and finding the shortest strong reference path from a GC Root to a destroyed object.\n\n"
            "In development, **LeakCanary** automates this entire workflow:\n"
            "1. It hooks into lifecycle callbacks (`ActivityLifecycleCallbacks`, `FragmentManager`).\n"
            "2. When `onDestroy()` occurs, it passes the instance to an `ObjectWatcher` wrapped in a `KeyedWeakReference` with an associated reference queue.\n"
            "3. If the reference is not cleared after 5 seconds, LeakCanary triggers a GC. If the object persists, it is flagged as *retained*.\n"
            "4. Once a threshold is reached, it dumps the heap and invokes **Shark** (Square's high-speed Kotlin HPROF parser) on a background thread to compute the leak trace.\n\n"
            "When analyzing the leak trace, we focus on the transition from `Leaking: NO` to `Leaking: YES`. That exact boundary points to the field or closure holding the rogue reference, allowing us to nullify the reference or unbind the lifecycle observer."
        ),
        "deep_answer": (
            "In complex production scenarios where LeakCanary is impractical due to heap dump overhead (dumping the heap pauses the process for hundreds of milliseconds), we analyze heap dumps offline using Android Studio Profiler or Eclipse Memory Analyzer Tool (MAT).\n\n"
            "In MAT, we run the **Dominator Tree** and **Leak Suspects** report. The Dominator Tree groups objects such that object A dominates object B if every path from a GC Root to B must pass through A. "
            "Looking at the **Retained Size** (the total memory that would be freed if an object were collected) immediately reveals culprit classes holding dozens of megabytes.\n\n"
            "To monitor leaks in production, we can use LeakCanary's Shark library paired with WorkManager to upload stripped, deduplicated leak signatures without transmitting sensitive user PII from the full memory dump."
        ),
        "follow_ups": [
            {
                "question": "What is the difference between Shallow Size and Retained Size in a heap dump?",
                "answer": "Shallow Size is the memory consumed by the object itself (its fields and header). Retained Size is the shallow size plus the memory of all objects that are exclusively reachable from this object and would be reclaimed if this object were garbage collected."
            },
            {
                "question": "Why shouldn't LeakCanary's full heap dumping be run in production builds?",
                "answer": "Dumping the heap freezes the runtime process (`Stop-The-World`), which degrades user experience and can trigger ANRs. Furthermore, heap dumps contain raw heap memory, which could expose sensitive user PII or credentials."
            }
        ]
    },
    {
        "id": "MEM-15",
        "arabic_explanation": (
            "كيفية استخدام أدوات مراقبة الذاكرة والمعالج (Android Studio Memory and CPU Profilers) لحل مشكلات الأداء:\n\n"
            "1. أداة Android Studio Memory Profiler:\n"
            "   - تعرض خطاً بيانياً حياً (Real-time Timeline) يوضح توزيع الذاكرة: **Java, Native, Graphics, Stack, Code, Others**.\n"
            "   - **Capture Heap Dump**: التقاط الـ Heap بالكامل وعرض الكائنات مصنفة حسب Class Name، مع إمكانية فرزها حسب Shallow Size و Retained Size ورؤية مراجع الـ GC Roots.\n"
            "   - **Record Java/Kotlin Allocations**: تتبع عمليات حجز الكائنات لحظة بلحظة لمعرفة الكود المسؤول عن توليد Memory Churn وسقوط الفريمات.\n\n"
            "2. أداة Android Studio CPU Profiler:\n"
            "   - تسجيل نشاط المعالج لاكتشاف الدوال التي تستهلك وقتاً طويلاً على الـ Main Thread وتسبب تشنج التطبيق (Jank) أو بطء الاستجابة.\n"
            "   - أوضاع التسجيل:\n"
            "     * **System Trace**: فحص شامل لتوقيت كل فريم على مستوى نظام التشغيل (Choreographer, SurfaceFlinger, App Threads).\n"
            "     * **Java/Kotlin Method Trace**: تسجيل استدعاءات الدوال بالكامل (Call Chart, Flame Chart, Top Down, Bottom Up).\n"
            "     * **Sampled Java/Kotlin Methods**: أخذ عينات دورية بنسبة overhead ضئيلة جداً.\n\n"
            "3. قراءة الرسوم البيانية (Flame Chart و Top Down):\n"
            "   - **Flame Chart**: يوضح تسلسل الدوال عمودياً؛ الدوال العريضة أفقياً هي التي استغرقت معظم وقت المعالج.\n"
            "   - **Top Down Tree**: يعرض شجرة الاستدعاءات بدءاً من الدالة المستدعاة مع توضيح الوقت الذاتي (Self Time) والوقت التراكمي (Total Time)."
        ),
        "practical_walkthrough": (
            "سيناريو عملي لاكتشاف دالة تستهلك المعالج باستخدام System Trace و Memory Profiler:\n"
            "```kotlin\n"
            "// استخدام كود Trace مخصص ليظهر بالاسم في تقرير System Trace / Perfetto:\n"
            "import androidx.tracing.trace\n"
            "\n"
            "fun processFeedData(rawItems: List<RawFeedItem>) {\n"
            "    // ظهور قطاع صريح باسم \"FeedProcessing\" في الـ CPU Profiler:\n"
            "    trace(\"FeedProcessing\") {\n"
            "        val processed = rawItems.map { item ->\n"
            "            // إذا ظهرت هذه الدالة عريضة في الـ Flame Chart، نقوم بتحسينها أو نقلها إلى Dispatchers.Default:\n"
            "            formatItemDetails(item)\n"
            "        }\n"
            "        updateUi(processed)\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Android Studio Profiler provides real-time diagnostics: the Memory Profiler visualizes Java/Native/Graphics heap usage and captures heap dumps to identify retained sizes and leaks. The CPU Profiler records Method and System Traces to inspect thread activity via Flame Charts, pinpointing CPU bottlenecks, lock contention, and main-thread blocking operations.",
        "best_answer": (
            "The Android Studio Profiler is our primary first-party suite for diagnosing runtime regressions.\n\n"
            "In the **Memory Profiler**:\n"
            "1. We observe real-time allocation timelines. A saw-tooth pattern indicates heavy allocation churn and frequent GC sweeps.\n"
            "2. We capture Heap Dumps to inspect object instances, filtering by package name. We sort by **Retained Size** to locate heavyweight objects and inspect the **Reference Tree** to see which field holds the strong reference preventing collection.\n"
            "3. We use Live Allocation Tracking during scrolling to identify unexpected temporary allocations inside adapters or rendering passes.\n\n"
            "In the **CPU Profiler**:\n"
            "1. We run **System Trace** to observe thread scheduling against 16.6ms frame boundaries (`Choreographer.doFrame`).\n"
            "2. We inspect the **Flame Chart** to identify wide blocks, representing long-running functions stalling the UI thread.\n"
            "3. We switch to **Bottom-Up View** to find methods with the highest self-time, isolating CPU-bound bottlenecks for asynchronous dispatching."
        ),
        "deep_answer": (
            "When profiling memory for low-end devices, analyzing the **Native** heap segment is vital. "
            "Since Android 8.0, Bitmaps, WebViews, and audio decoders allocate on the native heap. "
            "Standard Java heap dumps do not inspect C++ allocations, so we run the **Native Memory Profiler** (using `heapprofd`) to capture allocation call stacks inside `libhwui.so` and `libskia.so`.\n\n"
            "For CPU analysis, **Flame Charts** invert traditional call stacks: the X-axis represents execution time while the Y-axis shows call depth. "
            "A wide flame chart bar that remains unchanged across multiple frame intervals immediately pinpoints code blocking the Choreographer.\n\n"
            "In CI/CD automation, we run headless Android Studio profiling via Macrobenchmark, capturing trace files programmatically to ensure pull requests don't exceed frame timing or memory allocation thresholds."
        ),
        "follow_ups": [
            {
                "question": "What is the difference between Call Chart and Flame Chart in CPU Profiler?",
                "answer": "A Call Chart visualizes function execution chronologically over the timeline, preserving execution order. A Flame Chart aggregates identical call stacks across the entire trace, making it much easier to spot total cumulative time spent in specific functions."
            },
            {
                "question": "Why should you profile using a Release or Non-debuggable build?",
                "answer": "Debug builds have ART optimizations (such as inlining, dead-code elimination, and register allocation) disabled, and include debugging hooks that distort real CPU timing and allocation measurements. Profiling should always be done on a profileable release build."
            }
        ]
    },
    {
        "id": "MEM-16",
        "arabic_explanation": (
            "دور كل من StrictMode و Perfetto/System Trace و Android Vitals في تحسين أداء وتفادي أعطال التطبيق:\n\n"
            "1. أداة StrictMode:\n"
            "   - أداة تطوير مدمجة في نظام Android تكتشف وتلتقط الأخطاء العرضية التي يرتكبها المطورون أثناء التشغيل.\n"
            "   - تنقسم إلى سياستين:\n"
            "     * **ThreadPolicy**: تكتشف العمليات المحظورة على الـ Main Thread (قراءة/كتابة الديسك، استدعاءات الشبكة، بطء استدعاءات Binder).\n"
            "     * **VmPolicy**: تكتشف تسريبات الذاكرة (Activity leaks، عدم إغلاق SQLiteCursor أو Closeable objects، تسريب كائنات التسجيل).\n"
            "   - يمكن ضبطها لكتابة تحذيرات في Logcat أو التسبب في Crash فوري أثناء التطوير.\n\n"
            "2. أداة Perfetto و System Trace:\n"
            "   - منصة التتبع الأقوى على مستوى نظام Android والـ Linux Kernel بالكامل.\n"
            "   - تسجل بدقة متناهية أحداث المعالج (CPU scheduling, Frequency)، والذاكرة (Kernel RSS, Page faults, LMK events)، وتوقيت الفريمات في `SurfaceFlinger` و `Choreographer`.\n"
            "   - تتيح معرفة ما إذا كان التطبيق متأخراً بسبب كوده الخاص، أو بسبب انتظار عملية للنظام، أو بسبب اختناق في الـ GPU.\n\n"
            "3. خدمة Android Vitals:\n"
            "   - مبادرة من Google Play Console تجمع مؤشرات الأداء الحقيقية لأجهزة المستخدمين في العالم الفعلي دون أي عبء إضافي على التطبيق.\n"
            "   - تقيس المقاييس الحرجة: **ANR Rate**, **Crash Rate**, **Slow Rendering Frames (>16ms)**, **Frozen Frames (>700ms)**, **Wake locks غير المنتهية**.\n"
            "   - تجاوز العتبات السيئة (Bad Behavior Thresholds) يؤدي إلى انخفاض ترتيب التطبيق في متجر Google Play."
        ),
        "practical_walkthrough": (
            "تفعيل StrictMode في بيئة التطوير واستخدام androidx.tracing:\n"
            "```kotlin\n"
            "class MyApplication : Application() {\n"
            "    override fun onCreate() {\n"
            "        super.onCreate()\n"
            "        if (BuildConfig.DEBUG) {\n"
            "            // تفعيل StrictMode لكشف قراءات الديسك والشبكة والتسريبات:\n"
            "            StrictMode.setThreadPolicy(\n"
            "                StrictMode.ThreadPolicy.Builder()\n"
            "                    .detectDiskReads()\n"
            "                    .detectDiskWrites()\n"
            "                    .detectNetwork()\n"
            "                    .penaltyLog()\n"
            "                    .penaltyFlashScreen()\n"
            "                    .build()\n"
            "            )\n"
            "            StrictMode.setVmPolicy(\n"
            "                StrictMode.VmPolicy.Builder()\n"
            "                    .detectLeakedSqlLiteObjects()\n"
            "                    .detectLeakedClosableObjects()\n"
            "                    .detectActivityLeaks()\n"
            "                    .penaltyLog()\n"
            "                    .build()\n"
            "            )\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "StrictMode catches accidental disk, network, and leak violations on the main thread in debug builds. Perfetto provides system-wide kernel-level tracing across CPU, GPU, memory, and surface flinger. Android Vitals monitors real-world production health on Google Play, tracking ANR rates, crash rates, and frozen frames against ranking thresholds.",
        "best_answer": (
            "These three tools form a complete performance lifecycle: StrictMode for code-time prevention, Perfetto for low-level diagnosis, and Android Vitals for production governance.\n\n"
            "1. **StrictMode**: Configured in debug builds, it monitors the main thread for violations via `ThreadPolicy` (detecting disk I/O, network requests, and slow binder calls) and `VmPolicy` (detecting leaked SQLite cursors, unclosed streams, and retained Activities). Violations can log warnings or crash immediately to enforce cleanliness during feature development.\n\n"
            "2. **Perfetto / System Trace**: The modern Linux-kernel tracing platform for Android. It tracks thread scheduling, context switches, binder transactions, CPU frequency scaling, and render pipeline stages (`Choreographer` and `SurfaceFlinger`), revealing the exact system interaction that caused a dropped frame.\n\n"
            "3. **Android Vitals**: Google Play's real-user monitoring metric suite. It tracks core health metrics—specifically user-perceived ANRs, crash rates, slow render frames (>16ms), and frozen frames (>700ms). Breaching Google Play's 'bad behavior thresholds' harms store ranking and organic discovery."
        ),
        "deep_answer": (
            "Under the hood, Perfetto uses a kernel ring buffer (`ftrace`) combined with user-space tracing via the `atrace` protocol, recording events with microsecond precision and negligible performance overhead. "
            "Developers can add custom trace markers using `androidx.tracing.Trace.beginSection(\"SectionName\")` or the Kotlin `trace(\"...\")` DSL to correlate high-level app logic with system events in the Perfetto Web UI (`ui.perfetto.dev`).\n\n"
            "In Android Vitals, Google Play enforces strict thresholds: for instance, a user-perceived ANR rate above 0.47% or a crash rate above 1.09% places an app into Google Play's bad behavior threshold, which triggers search demotion and warnings on the app store listing.\n\n"
            "In our enterprise release pipeline, we integrate Google Play Developer API to pull Android Vitals automatically into our Datadog/Grafana dashboards, establishing automated rollback gates during phased rollouts."
        ),
        "follow_ups": [
            {
                "question": "Why should StrictMode be strictly disabled or removed in release builds?",
                "answer": "StrictMode introduces runtime reflection, IPC tracking, and disk monitoring overhead. Furthermore, penalties like `penaltyDeath()` would crash the app for end users on non-critical violations."
            },
            {
                "question": "What distinguishes a 'frozen frame' from a 'slow frame' in Android Vitals?",
                "answer": "A slow frame takes longer than 16ms to render (falling below 60fps). A frozen frame takes longer than 700ms to render, representing a visible freeze that severely degrades the user experience."
            }
        ]
    },
    {
        "id": "MEM-17",
        "arabic_explanation": (
            "ما هو الـ UI Jank؟ وشرح توقيت الفريمات (Frame Timing)، وإعادة التركيب المفرطة في Compose (Excessive Recompositions)، وثقل العمل على الـ Main Thread:\n\n"
            "1. ما هو الـ UI Jank؟\n"
            "   - الشاشة القياسية تعمل بمعدل تحديث 60Hz (أو 90Hz/120Hz في الشاشات الحديثة ذات التقنية العالية).\n"
            "   - في شاشة 60Hz، يمتلك التطبيق مهلة قدرها **16.6 مللي ثانية (ms)** لإنجاز كل شيء خاص بالفريم: قياس الـ Layout، الرسم، والمعالجة.\n"
            "   - في شاشة 120Hz، تنخفض المهلة إلى **8.3 مللي ثانية (ms)** فقط!\n"
            "   - إذا تأخر الـ Main Thread أو الـ RenderThread في تسليم الفريم في الوقت المحدد لـ `VSYNC`، يسقط الفريم (Dropped Frame) ويتكرر الفريم السابق، مما يظهر للمستخدم كتشنج وتقطيع في الحركة يسمى **Jank**.\n\n"
            "2. أسباب الـ Jank في الـ Views التقليدية:\n"
            "   - إجهاد الـ Main Thread بعمليات I/O أو معالجة نصوص أو حجز كائنات (Memory Churn -> GC Pauses).\n"
            "   - تعقيد شجرة الواجهة (Deep View Hierarchy) مما يسبب قياسات متداخلة وبطيئة (Multi-pass measure/layout).\n\n"
            "3. أسباب الـ Jank في Jetpack Compose (Excessive Recompositions):\n"
            "   - تمرير كائنات غير مستقرة (Unstable Parameters مثل `List<T>` العادية بدلاً من `ImmutableList`).\n"
            "   - قراءة الـ State في مرحلة التكوين (Composition Phase) بدلاً من مرحلة الرسم (Draw Phase أو Layout Phase عبر Lambdas مثل `Modifier.offset { ... }`).\n"
            "   - تكرار استدعاء دوال الحسابات داخل الـ Composable دون تغليفها بـ `remember { ... }`."
        ),
        "practical_walkthrough": (
            "مقارنة عملية لتجنب الـ Jank في Jetpack Compose:\n"
            "```kotlin\n"
            "// ❌ كود يسبب Recomposition مستمر في كل بكسل سكرول (Jank مؤكد):\n"
            "@Composable\n"
            "fun BadScrollHeader(scrollState: ScrollState) {\n"
            "    // قراءة scrollState.value مباشرة في مرحلة الـ Composition تجبر إعادة بناء الدالة كلها في كل حركة:\n"
            "    val offset = scrollState.value * 0.5f\n"
            "    Box(modifier = Modifier.offset(y = offset.dp)) {\n"
            "        HeaderContent()\n"
            "    }\n"
            "}\n"
            "\n"
            "// ✅ كود فائق السلاسة: تأجيل قراءة الـ State إلى مرحلة الـ Layout عبر Lambda Modifier:\n"
            "@Composable\n"
            "fun GoodScrollHeader(scrollState: ScrollState) {\n"
            "    // Modifier.offset(lambda) يؤجل قراءة الـ State إلى مرحلة القياس والرسم، متخطياً الـ Recomposition بالكامل:\n"
            "    Box(modifier = Modifier.offset { IntOffset(x = 0, y = (scrollState.value * 0.5f).roundToInt()) }) {\n"
            "        HeaderContent()\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "UI jank occurs when a frame fails to render within the hardware VSYNC window (16.6ms for 60Hz, 8.3ms for 120Hz), causing dropped frames. Causes include heavy work on the main thread, layout thrashing, frequent GC pauses, and excessive recompositions in Compose caused by unstable types or reading states during the composition phase instead of layout/draw phases.",
        "best_answer": (
            "UI jank is the visual stutter experienced by users when the application fails to produce a frame in time for the display's VSYNC signal.\n\n"
            "Displays refresh at fixed intervals: 60Hz displays require rendering within **16.6ms**, while modern 120Hz panels allow just **8.3ms**. "
            "A frame pipeline consists of three sequential phases: Application Main Thread (handling input, animating, measuring, and recording draw commands), RenderThread (uploading GPU commands), and SurfaceFlinger (compositing onto the hardware frame buffer).\n\n"
            "If any phase exceeds its budget, the system misses the VSYNC deadline and repeats the previous frame. "
            "In legacy Views, jank stems from nested layout passes, costly `onDraw()` operations, and GC pauses from allocation churn.\n\n"
            "In Jetpack Compose, the most common jank source is **excessive recompositions** during scrolling. "
            "Passing unstable parameters triggers unnecessary recompositions of large composable subtrees. "
            "Furthermore, reading rapidly changing state (like scroll position) during the *Composition* phase rather than deferring it to the *Layout* or *Draw* phase via lambda modifiers forces full tree recomposition on every pixel movement."
        ),
        "deep_answer": (
            "To deeply diagnose jank, we examine the Choreographer logs and Perfetto traces. The `Choreographer` class coordinates timing, scheduling callbacks for Input, Animation, Traversal, and Commit. "
            "When logs report `Skipped 30 frames! The application may be doing too much work on its main thread`, Choreographer detected that multiple VSYNC ticks elapsed before the message queue returned to idle.\n\n"
            "In Compose, we profile recomposition counts using the **Layout Inspector** and Compose Compiler Metrics (`reportsDestination`). "
            "Marking data classes with `@Immutable` or wrapping unstable collections with Kotlinx Immutable Collections (`ImmutableList`) enables the compiler to mark composables as `skippable`.\n\n"
            "Another critical lever is using `derivedStateOf { ... }`. When a state changes continuously (e.g. `scrollState.firstVisibleItemIndex`), using `derivedStateOf` ensures observers only recompose when a calculated boolean or threshold actually changes."
        ),
        "follow_ups": [
            {
                "question": "How does `derivedStateOf` prevent recomposition jank during scrolling?",
                "answer": "`derivedStateOf` acts as a dampener: it buffers high-frequency state updates (like scroll offsets changing every millisecond) and only triggers recomposition when the resulting derived calculation (like `index > 0`) changes its boolean or discrete output value."
            },
            {
                "question": "What is the role of RenderThread in modern Android?",
                "answer": "Introduced in Android 5.0, the RenderThread offloads the actual GPU rendering commands (OpenGL/Vulkan) from the Main thread, handling animations like ripples independently even if the Main thread is temporarily busy."
            }
        ]
    },
    {
        "id": "MEM-18",
        "arabic_explanation": (
            "دور حزم Baseline Profiles وأداة Macrobenchmark في تسريع أداء وتجاوب التطبيق:\n\n"
            "1. كيف يقوم نظام Android Runtime (ART) بتشغيل الكود؟\n"
            "   - في نظام Android، الكود يتم تجميعه (AOT / JIT Compilation):\n"
            "     * **JIT (Just-In-Time)**: يفسر البايت كود فورياً عند التشغيل الأول، ويقوم بتجميع الأجزاء الأكثر استخداماً (Hot paths) في الذاكرة أثناء استخدام التطبيق.\n"
            "     * المشكلة: عند التثبيت لأول مرة أو بعد التحديث، يكون التطبيق بطيئاً جداً (Cold Start) لأن الـ JIT لا يزال يترجم الكود على الطاير.\n"
            "     * **Cloud Profiles**: تقوم Google Play بجمع بيانات استخدام المستخدمين وتوليد Profile، ولكن هذا يستغرق أياماً أو أسابيع بعد طرح الإصدار!\n\n"
            "2. ما هي الـ Baseline Profiles؟\n"
            "   - هي مواصفات مسبقة لقواعد الكود الحرج (Hot methods and classes) يتم تضمينها مباشرة داخل الـ APK / AAB بواسطة المطورين.\n"
            "   - عند تثبيت التطبيق، يقوم ART بعمل تجميع مسبق (Ahead-Of-Time - AOT) لهذه المسارات الحرجة فوراً!\n"
            "   - النتيجة: تسريع تشغيل التطبيق (Startup time) بنسبة **20% إلى 40%**، وتقليل سقوط الفريمات (Jank) في أول استخدام للمستخدم بدون انتظار Cloud Profiles.\n\n"
            "3. أداة Macrobenchmark:\n"
            "   - مكتبة اختبارات برمجية دقيقة تعمل على أجهزة حقيقية لاختبار سيناريوهات المستخدم الكبيرة (مثل وقت التشغيل Cold Start، وسلاسة السكرول في القوائم Scroll Jank).\n"
            "   - تستخدم أداة Macrobenchmark لتوليد الـ Baseline Profiles آلياً، والتحقق من مقاييس الأداء لمنع التراجعات (Performance Regressions) في CI/CD."
        ),
        "practical_walkthrough": (
            "كتابة اختبار Macrobenchmark لتوليد Baseline Profile واختبار سرعة التشغيل:\n"
            "```kotlin\n"
            "// في وحدة benchmark المنفصلة (benchmark module):\n"
            "@RunWith(AndroidJUnit4::class)\n"
            "class BaselineProfileGenerator {\n"
            "    @get:Rule\n"
            "    val rule = BaselineProfileRule()\n"
            "\n"
            "    @Test\n"
            "    fun generateBaselineProfile() {\n"
            "        rule.collect(\n"
            "            packageName = \"com.example.app\",\n"
            "            includeInStartupProfile = true\n"
            "        ) {\n"
            "            // سيناريو التشغيل الحرج:\n"
            "            pressHome()\n"
            "            startActivityAndWait()\n"
            "\n"
            "            // سكرول داخل الشاشة الرئيسية لتسجيل مسارات الكود الخاصة بالقائمة:\n"
            "            device.findObject(By.res(\"com.example.app\", \"feed_list\"))\n"
            "                ?.fling(Direction.DOWN)\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Baseline Profiles supply Ahead-Of-Time (AOT) compilation hints directly in the APK, allowing Android Runtime (ART) to precompile critical startup and scroll paths upon app install, improving cold startup by 20-40%. Macrobenchmark is the testing library used to measure startup and frame timings, and programmatically generate these profiles.",
        "best_answer": (
            "Baseline Profiles bridge the critical gap between raw JIT interpretation and delayed Google Play Cloud Profiles.\n\n"
            "By default, newly installed Android apps rely on Just-In-Time (JIT) compilation, interpreting bytecode dynamically until ART identifies frequently executed 'hot code' paths. This causes sluggish first-time app launches and scroll stutter. "
            "While Google Play Cloud Profiles eventually compile these paths via background dexopt, they take several days and millions of installs to propagate.\n\n"
            "**Baseline Profiles** let developers pre-record critical execution paths—such as application startup, feed scrolling, and checkout navigation—and package them into the APK/AAB as human-readable rule definitions (`baseline-prof.txt`). "
            "During app installation, the on-device ART precompiles those exact methods Ahead-Of-Time (AOT), delivering immediate 20% to 40% improvements in launch speed and eliminating initial scroll jank.\n\n"
            "**Macrobenchmark** is the Jetpack library that runs automated, real-device integration tests simulating realistic user flows (Startup, Scroll, Navigation), generating Baseline Profiles programmatically and asserting latency thresholds in CI."
        ),
        "deep_answer": (
            "Under the hood, Baseline Profiles generate a compact binary format inside `assets/dexopt/baseline.prof`. "
            "When `pm install` completes, Android's `installd` daemon invokes `dex2oat` using the compilation filter `speed-profile`, translating designated methods directly into native machine code while leaving colder secondary paths for JIT.\n\n"
            "In Macrobenchmark tests, we can test different compilation modes explicitly: `CompilationMode.None()` (simulating unoptimized fresh install), `CompilationMode.Partial(baselineProfileMode = BaselineProfileMode.Require)` (testing baseline profile impact), and `CompilationMode.Full()`.\n\n"
            "By running Macrobenchmark in CI against both `None` and `Partial`, teams obtain concrete, verifiable metrics proving that a pull request maintains its cold start SLA (e.g. keeping startup under 800ms on a reference device)."
        ),
        "follow_ups": [
            {
                "question": "Why must Macrobenchmark tests run on a physical device rather than an emulator?",
                "answer": "Emulators use host CPU translation, virtualization layers, and synthetic clock timers that do not reflect real ARM hardware execution speeds, thermal throttling, or mobile memory bandwidth constraints."
            },
            {
                "question": "What is the Startup Profile, and how does it differ from the Baseline Profile?",
                "answer": "A Startup Profile is a focused subset of the Baseline Profile targeting only the code executed between app process launch and the first drawn frame (`reportFullyDrawn()`), prioritizing layout and classes necessary for instant launch."
            }
        ]
    },
    {
        "id": "MEM-19",
        "arabic_explanation": (
            "الفرق بين أنواع بدء تشغيل التطبيق: التشغيل البارد (Cold Start)، والدافئ (Warm Start)، والساخن (Hot Start):\n\n"
            "1. التشغيل البارد (Cold Start):\n"
            "   - **الحالة**: عملية التطبيق (App Process) غير موجودة في الذاكرة نهائياً (إما بعد إعادة تشغيل الهاتف، أو بعد إنهاء العملية بواسطة المستخدم أو النظام).\n"
            "   - **ما يحدث داخلياً**: النظام يقوم بإنشاء العملية من البداية عبر `Zygote.fork()`، وتحميل كلاسات التطبيق (ClassLoading)، وإنشاء كائن `Application` وتنفيذ `onCreate()`، ثم إنشاء الـ `Activity` وتنفيذ `onCreate() -> onStart() -> onResume()`، ثم قياس ورسم الشاشة الأولى.\n"
            "   - **الوقت المتوقع**: هو الأطول دائماً (عادة بين 1 إلى 3 ثوانٍ).\n\n"
            "2. التشغيل الدافئ (Warm Start):\n"
            "   - **الحالة**: عملية التطبيق (Process) لا تزال موجودة في الذاكرة، لكن الـ Activity دُمرت وتجب إعادة إنشائها.\n"
            "   - **أمثلة**: المستخدم غادر التطبيق وضغط على زر الرجوع (Back)، أو قتلت الـ Activity بسبب تغيير اتجاه الشاشة (Configuration Change) أو نقص ذاكرة النشاط.\n"
            "   - **ما يحدث**: يتخطى النظام إنشاء الـ Process وكائن الـ Application، ويبدأ مباشرة من إنشاء الـ Activity واستعادة حالتها (`savedInstanceState`).\n\n"
            "3. التشغيل الساخن (Hot Start):\n"
            "   - **الحالة**: عملية التطبيق والنشاط لا يزالان موجودين بالكامل في الذاكرة ولم يتم تدميرهما.\n"
            "   - **أمثلة**: المستخدم ضغط على زر Home ثم فتح التطبيق مجدداً بعد ثوانٍ.\n"
            "   - **ما يحدث**: يجلب النظام النشاط من الخلفية إلى المقدمة مباشرة، مستدعياً `onRestart() -> onStart() -> onResume()` دون أي إعادة إنشاء للـ Views أو الـ Application، وهو الأسرع على الإطلاق (أقل من بضع مئات من المللي ثانية)."
        ),
        "practical_walkthrough": (
            "استدعاء `reportFullyDrawn()` لقياس اكتمال التحميل الحقيقي للواجهة (Time to Full Display):\n"
            "```kotlin\n"
            "class MainActivity : AppCompatActivity() {\n"
            "    private val viewModel: MainViewModel by viewModels()\n"
            "\n"
            "    override fun onCreate(savedInstanceState: Bundle?) {\n"
            "        super.onCreate(savedInstanceState)\n"
            "        setContentView(R.layout.activity_main)\n"
            "\n"
            "        lifecycleScope.launch {\n"
            "            viewModel.uiState.collect { state ->\n"
            "                if (state is UiState.Success) {\n"
            "                    renderData(state.data)\n"
            "                    // إبلاغ النظام بأن التطبيق جاهز ومحمل بالكامل بالبيانات:\n"
            "                    // هذا يُسجل في Logcat ويُحسب في Android Vitals و Macrobenchmark بدقة:\n"
            "                    reportFullyDrawn()\n"
            "                }\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Cold Start starts from scratch: the OS forks the process from Zygote, initializes the Application object, and creates the Activity. Warm Start reuses an existing process but recreates the destroyed Activity. Hot Start simply brings an existing in-memory Activity and process to the foreground via `onRestart()` and `onResume()`, making it instantaneous.",
        "best_answer": (
            "The distinction between startup types hinges on whether the application process and Activity instance already reside in RAM.\n\n"
            "1. **Cold Start**: The process does not exist. The OS must fork a new process from Zygote, allocate memory, initialize runtime classes, instantiate the `Application` class, run `Application.onCreate()`, instantiate the launch `Activity`, inflate the layout, and complete the initial draw pass. It is the most expensive launch state and must be optimized aggressively.\n\n"
            "2. **Warm Start**: The application process is still resident in RAM, but the Activity was destroyed (for instance, via back navigation or memory trimming). The system skips process and Application creation, jumping directly into Activity recreation and state restoration (`savedInstanceState`).\n\n"
            "3. **Hot Start**: Both the application process and Activity remain fully initialized in memory (e.g. the user pressed Home and immediately returned). The OS merely brings the Activity to the foreground, invoking `onRestart()`, `onStart()`, and `onResume()` without recreating views, making it virtually instantaneous.\n\n"
            "In production, Google Play Vitals monitors Cold Starts targeting under **5 seconds** (ideally <1.5s), Warm starts under **2 seconds**, and Hot starts under **1.5 seconds**."
        ),
        "deep_answer": (
            "Under the hood, optimizing Cold Start requires minimizing work done in `Application.onCreate()`. "
            "Third-party SDK initializations (analytics, crash reporting, ads, feature flags) should not run synchronously on the main thread during startup. "
            "Using Jetpack **App Startup** allows libraries to share a single `ContentProvider` and define explicit dependency graphs, enabling asynchronous or on-demand initialization.\n\n"
            "Another critical milestone is the difference between **Time to Initial Display (TTID)** and **Time to Full Display (TTFD)**. "
            "TTID is the timestamp when the first visual frame is drawn (often a skeleton or splash screen). "
            "TTFD occurs when the screen has finished populating asynchronous data, marked explicitly by calling `activity.reportFullyDrawn()`. "
            "Android Vitals and Macrobenchmark use `reportFullyDrawn()` as the true golden metric for cold start quality."
        ),
        "follow_ups": [
            {
                "question": "Why is synchronous SDK initialization in a ContentProvider bad for Cold Start?",
                "answer": "All `ContentProvider.onCreate()` methods are executed synchronously on the main thread before `Application.onCreate()`. If multiple third-party SDKs install automatic ContentProviders doing heavy work, cold startup stalls before user code even executes."
            },
            {
                "question": "How does Splash Screen API (Android 12+) interact with Cold Start?",
                "answer": "The SplashScreen API displays a system-controlled window background icon immediately upon process fork, masking the latency of class loading and `Application.onCreate()` until the app draws its first frame."
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

    for item in MEM_13_19:
        by_id[item["id"]] = item

    output = [by_id[k] for k in sorted(by_id.keys())]
    DATA_FILE.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {DATA_FILE} with questions MEM-13 to MEM-19. Total questions: {len(output)}")

if __name__ == "__main__":
    main()
