#!/usr/bin/env python3
"""Elevate MEM-21 through MEM-26 for bilingual parity and senior spoken answers."""
from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import elevation_engine as ee

DATA = {}

# ==========================================
# MEM-21: Multi-day production memory creep
# ==========================================
DATA["MEM-21"] = {
    "concept_en": """Investigating gradual, multi-day memory creep in production Android applications requires differentiating between episodic Activity leaks and insidious monotonic heap expansion. In long-running mobile deployments, memory creep typically stems from unbounded in-memory caches, accumulating singleton observer registrations, uncollected native resources (such as WebViews, Bitmaps, or JNI allocations), or static collections that append telemetry events during extended background execution. Because user sessions in production can span days through device standby, the ART Generational Concurrent Copying garbage collector cannot reclaim references rooted in long-lived or static scopes. Isolating the root cause necessitates a tiered observability pipeline: segmenting production Proportional Set Size (PSS) metrics across session durations in telemetry, automating continuous stress testing using UI Automator and monkey runs on physical device farms, and capturing differential heap snapshots (HPROF) before and after sustained workloads to identify retaining paths and dominant dominator trees using memory analyzers like Shark or Eclipse Memory Analyzer (MAT).""",
    "walkthrough_en": """Reproducing and diagnosing memory creep in a test harness:
```kotlin
// Automated stress test driving continuous user navigation to trigger slow creep
@RunWith(AndroidJUnit4::class)
class MemoryCreepTest {
    @Test
    fun simulateSustainedUsageAndCheckHeap() {
        val device = UiDevice.getInstance(InstrumentationRegistry.getInstrumentation())
        val context = ApplicationProvider.getApplicationContext<Context>()

        // 1. Establish initial baseline heap snapshot after warm-up GC:
        Runtime.getRuntime().gc()
        val initialHeap = Debug.getNativeHeapAllocatedSize()

        // 2. Simulate 500 repeated feed navigations and item views:
        repeat(500) { iteration ->
            device.findObject(By.res("com.example.app", "feed_item")).click()
            device.pressBack()
            if (iteration % 100 == 0) {
                Runtime.getRuntime().gc()
            }
        }

        // 3. Dump HPROF file for differential offline analysis:
        val dumpFile = File(context.cacheDir, "post_stress_heap.hprof")
        Debug.dumpHprofData(dumpFile.absolutePath)
        
        // Assert heap growth threshold:
        val finalHeap = Debug.getNativeHeapAllocatedSize()
        val deltaMb = (finalHeap - initialHeap) / (1024 * 1024)
        assertTrue("Memory grew unexpectedly by ${deltaMb}MB", deltaMb < 30)
    }
}
```""",
    "short_en": """To isolate multi-day memory creep, I correlate production PSS telemetry against session lengths and feature usage, reproduce the accumulation in laboratory environments using automated stress testing, and capture differential HPROF heap dumps. Analyzing dominator trees in MAT or Shark reveals retained size growth and identifies static collections or unpruned caches retaining objects across garbage collection cycles.""",
    "structured_en": """To begin with, multi-day memory creep represents a slow, cumulative accumulation of retained objects that eventually causes OutOfMemory crashes during prolonged user sessions.
From an architectural standpoint, my diagnosis begins with production telemetry. We monitor Proportional Set Size (PSS) alongside session duration and user journey metadata to determine whether memory growth correlates with background synchronization, continuous navigation, or specific third-party SDK lifecycles.
In production scenarios, reproducing the failure under controlled conditions is vital. We construct automated endurance tests using UI Automator on physical lab devices, simulating thousands of user interactions while periodically invoking garbage collection to clear transient allocations. Once memory reaches an elevated plateau, we dump HPROF heap profiles at predefined intervals.
As for boundary management, we ingest the heap dumps into Shark or Eclipse Memory Analyzer (MAT) to perform differential analysis. By computing the delta between instance counts and examining dominator trees, we pinpoint retaining paths rooted in static registries, unbounded telemetry queues, or singleton event buses, allowing us to implement bounded LRU eviction policies and lifecycle-aware observer cleanups.""",
    "deep_senior_en": """At the lower runtime and ART tier, multi-day memory accumulation presents unique challenges because the Generational Concurrent Copying garbage collector rapidly promotes surviving objects from the young generation (nursery) into the old generation space. Once an object resides in the old generation, it escapes minor GC collection passes and incurs reclamation cost only during major GC cycles, which increases application pause latency and power consumption.
When investigating production creep, standard LeakCanary instrumentation is often insufficient because it is tuned for immediate Activity and Fragment destruction leaks rather than slow collection accretion inside live singletons. To bridge this gap, senior engineers deploy custom Shark-based background heap sampling in internal canine builds. We sample the live heap when PSS crosses predefined memory thresholds (such as reaching 80% of the device's heap limit) and strip personal data before uploading stripped object graphs.
Offline analysis in Eclipse MAT focuses on comparing two snapshots: a baseline capture taken ten minutes after cold start, and an endurance capture taken after continuous automated test execution. We calculate the \"Compare Basket\" delta to detect monotonically increasing instance counts. The primary culprits in enterprise applications are: unbounded reactive streams (such as SharedFlow buffers configured with excessive replay or buffer capacities), static analytics lists that queue failed payloads indefinitely without exponential backoff limits, and JNI global references holding uncollected graphic or cryptographic handles in native memory.
Resolution involves replacing static caches with memory-sensitive structures like LruCache bounded by actual byte size, wrapping observers in auto-disposing lifecycle scopes, and registering ComponentCallbacks2 to aggressively purge non-essential in-memory assets on onTrimMemory signals.""",
    "meta_ar": {
        "id": "MEM-21",
        "questionAr": "كيف تعزل وتشخص مشكلة زيادة استهلاك الذاكرة تدريجياً على مدار أيام في الإنتاج؟",
        "topicAr": "إدارة الذاكرة والـ ANR وتحسين الأداء",
        "evaluates_ar": "- التمييز بين تسريب دورة حياة الشاشات اللحظي وبين تراكم الذاكرة التدريجي (Memory Creep).\n- استخدام بيانات الـ PSS والـ Telemetry في الإنتاج لتحديد الميزات المسؤولة عن التراكم.\n- تطبيق اختبارات التحمل (Stress Testing) ومقارنة ملفات الـ HPROF عبر Dominator Trees.",
        "why_it_matters_ar": "الزيادة التدريجية في الذاكرة (Memory Creep) هي أخطر أنواع التسريب؛ لأنها لا تظهر في الاستخدام السريع، بل تتراكم على مدار أيام من استخدام التطبيق في الخلفية حتى تفجر كراشات OutOfMemory متكررة وتقتل التطبيق في أوقات حساسة، مما يضر بمعدلات استقرار التطبيق على متجر جوجل بلاي.",
        "worked_example_ar": "بناء اختبار تحمل آلي لتوليد وتفريغ الـ Heap Dump عند ثبات التراكم:\n```kotlin\n@Test\nfun testMemoryEndurance() {\n    val device = UiDevice.getInstance(InstrumentationRegistry.getInstrumentation())\n    Runtime.getRuntime().gc()\n    val initialHeap = Debug.getNativeHeapAllocatedSize()\n\n    // محاكاة تنقل مستمر لـ 500 دورة لرصد التراكم:\n    repeat(500) {\n        device.findObject(By.res(\"com.example.app\", \"item\")).click()\n        device.pressBack()\n    }\n\n    Runtime.getRuntime().gc()\n    val dumpFile = File(context.cacheDir, \"memory_creep.hprof\")\n    Debug.dumpHprofData(dumpFile.absolutePath) // استخراج ملف الـ Heap للتحليل\n}\n```",
        "trade_offs_ar": "إجراء فحص كامل للذاكرة في بيئة الإنتاج يستهلك طاقة المعالج وقد يسبب تجميداً مؤقتاً للتطبيق أثناء الـ Heap Dump، لذا نعتمد على تفعيل أخذ اللقطات بنسبة مئوية صغيرة (Sampling) في النسخ الداخلية أو بيئات الاختبار قبل الإطلاق العام للجمهور.",
        "failure_modes_ar": "الاعتماد فقط على أداة LeakCanary العادية؛ لأنها تراقب تدمير الشاشات فقط، ولا تكتشف تراكم الكائنات داخل كلاسات الـ Singleton والقوائم الثابتة المستمرة. خطأ آخر هو محاولة حل المشكلة بزيادة `largeHeap` في الـ Manifest، مما يفاقم المشكلة ويؤخر كراش الـ OOM دون علاجه.",
        "production_perspective_ar": "في تطبيقات الشركات الكبرى، نراقب مؤشر PSS عبر Firebase Performance و Datadog، ونربطه بمدة الجلسة (Session Duration). وإذا لاحظنا ارتفاعاً مستمراً في الذاكرة مع طول وقت الجلسة، نوقف الميزة ونعزل الكاش غير المحدود ونستبدله بـ LruCache محدد الحجم بالبايت.",
        "how_to_answer_ar": "- **التشخيص المبدئي:** فرّق بين تسريب الشاشات السريع وتراكم الذاكرة البطيء في الـ Singletons.\n- **جمع البيانات:** وضح استخدام الـ Telemetry ومراقبة الـ PSS مقارنة بطول مدة الاستخدام.\n- **إعادة الإنتاج:** اشرح بناء اختبارات تحمل عبر UI Automator ومحاكاة آلاف العمليات.\n- **التحليل العمقي:** وضح مقارنة ملفات HPROF عبر أدوات MAT أو Shark وفحص Dominator Tree.\n- **الحلول الهندسية:** استبدال القوائم العادية بـ LruCache والاستجابة لـ onTrimMemory.",
        "talking_points_ar": "ناقش انتقال الكائنات من الـ Young Generation إلى الـ Old Generation في مترجم ART، وتكلفة الـ Major GC، وتسريب مراجع الـ JNI والـ WebViews، وكيفية حساب Retained Size بدقة.",
        "follow_ups_ar": "- **المحاور:** \"لماذا تفشل LeakCanary في كشف الـ Memory Creep التدريجي؟\"\n  **المرشح:** \"لأن LeakCanary مصممة لمراقبة الكائنات التي تمتلك دورة حياة محددة كالشاشات والـ Fragments عبر WeakReference؛ أما تراكم الذاكرة التدريجي فيحدث عادة داخل Singletons أو Caches حية لا يتم تدميرها أصلاً، فلا تعتبرها LeakCanary تسريباً صريحاً.\"\n\n- **المحاور:** \"كيف تفرق بين الـ Shallow Heap والـ Retained Heap أثناء فحص المشكلة؟\"\n  **المرشح:** \"الـ Shallow Heap هو حجم الكائن نفسه فقط في الذاكرة بدون ما يحمله من مراجع، أما الـ Retained Heap فهو الحجم الإجمالي الذي سيتحرر لو قمنا بحذف هذا الكائن وكل الكائنات التابعة له فقط، وهو الرقم الأهم لتحديد رأس التسريب.\"",
        "self_check_ar": "هل ميزت بين تسريب الشاشات والتراكم البطيء؟ هل وضحت استخدام PSS في الإنتاج؟ وهل شرحت أسلوب المقارنة التفاضلية لملفات HPROF؟",
        "references_ar": "- [Inspect your app's memory usage](https://developer.android.com/studio/profile/memory-profiler) — فحص استهلاك الذاكرة وملفات HPROF.\n- [Eclipse Memory Analyzer (MAT)](https://eclipse.dev/mat/) — تحليل الـ Dominator Tree والتسريبات المعقدة.\n\nتمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13.",
        "quick_answer_ar": "لعزل مشكلة تراكم الذاكرة التدريجي على مدار أيام، بربط بيانات الـ Telemetry ومؤشر PSS بمدة جلسات المستخدمين في الإنتاج، وبنعيد إنتاج التراكم في المعمل باختبارات تحمل آلية عبر UI Automator، وبناخد لقطتين للـ Heap Dump (HPROF) قبل وبعد الضغط لمقارنتهم في MAT أو Shark وتحديد الكلاسات ذات الحجم المتزايد.",
        "best_answer_ar": "مشكلة الـ Memory Creep التدريجي من أصعب المشاكل لأنها مبتظهرش في الاستخدام العادي السريع، وغالباً بتكون ناتجة عن كاشات داخلية غير محدودة أو قوائم تتبع في الـ Singletons بتجمع بيانات ومبتفضيهاش.\n\nخطتي لتشخيص المشكلة بتبدأ من بيانات الإنتاج؛ بنحلل الـ Telemetry وبنقيس الـ Proportional Set Size (PSS) ونربطه بمدة الجلسة (Session Length) علشان نتأكد هل التراكم مرتبط بميزة معينة أو استخدام طويل في الخلفية.\n\nبعدها بنعيد إنتاج المشكلة في المعمل باستخدام اختبارات تحمل آلية (Endurance Testing) عبر UI Automator على أجهزة حقيقية، بنخلي السكريبت يتنقل آلاف المرات بين الشاشات ويطلب بيانات وينادي الـ GC دورياً للتخلص من الكائنات العابرة.\n\nولما الذاكرة تثبت على رقم عالي جداً، بناخد لقطة HPROF ونقارنها بلقطة البداية عبر Eclipse MAT أو Shark؛ بنبص على الـ Dominator Tree وفارق عدد الـ Instances لنحدد الكائنات اللي ماسكة Retained Size ضخم، وبنحل المشكلة بوضع حدود صارمة على الكاشات باستخدام LruCache والاستجابة لـ onTrimMemory.",
        "deep_answer_ar": "على مستوى الـ ART Garbage Collector، الكائنات المتراكمة دي بتهرب بسرعة من منطقة الـ Young Generation وبتروح للـ Old Generation space لأنها بتفضل عايشة لفترات طويلة. في الـ Old Generation، مجمّع القمامة مش بيلمسها في الـ Minor GC، وبيحتاج يعمل Major Concurrent Copying GC متكرر، وده بيستهلك المعالج والبطارية ويسبب Jank في الواجهة لحد ما يفجر OutOfMemoryError.\n\nأداة LeakCanary العادية مش كافية هنا؛ لأنها بتراقب الشاشات الميتة عبر ReferenceQueue و WeakReference، بينما الـ Creep بيحصل داخل كائنات حية في الـ Singleton scope زي مستودعات البيانات وكاشات الـ Bitmaps وقوائم الـ Analytics اللي بتجمع Events وقت انقطاع الشبكة ومبتمسحهاش.\n\nعلشان كده بنعتمد على التحليل التفاضلي للـ HPROF عبر Eclipse MAT؛ بنحسب الـ Retained Heap والـ Dominator Tree وبنعمل مقارنة بين لقطتين عبر الـ Compare Basket. في معظم التطبيقات الإنتاجية، الجناة الأساسيين بيكونوا إما SharedFlow buffers معمولة بـ replay ضخم وبدون اشتراك نشط، أو JNI Global References ماسكة مساحات Native في WebViews أو مكتبات صوت ومعالجة صور.\n\nالحل الهندسي بيشمل استبدال كل الكاشات الثابتة بـ LruCache مبني على الحجم بالبايت، واستخدام Lifecycle-aware collectors لتفريغ المشتركين، وتسجيل ComponentCallbacks2 لتفريغ الذاكرة فوراً بمجرد ما النظام يبعت إشارة TRIM_MEMORY_RUNNING_CRITICAL."
    }
}

# =======================================================
# MEM-22: Main thread blocked despite launching coroutine
# =======================================================
DATA["MEM-22"] = {
    "concept_en": """A widespread misconception among Android developers is that wrapping execution inside a coroutine builder like launch automatically offloads work to a background worker thread. In standard Android architecture, builders like viewModelScope.launch and lifecycleScope.launch inherit their default dispatcher from Dispatchers.Main.immediate. Consequently, executing blocking operations—such as Thread.sleep, synchronous file I/O, heavy cryptographic hashing, complex JSON deserialization, or acquiring a contended database lock—directly executes on the Android Main (UI) thread. This starves the thread's underlying Looper and MessageQueue, preventing the Android Choreographer from processing VSYNC pulses and handling input touch events. If the main looper message dispatch latency exceeds five seconds (or input queues stall for five seconds), the Activity Manager Service declares an Application Not Responding (ANR) fatal condition.""",
    "walkthrough_en": """Demonstrating the blocking trap versus proper dispatcher switching:
```kotlin
// ❌ Flawed implementation: blocks the Android Main Looper directly
class OrderViewModel(private val api: OrderApi) : ViewModel() {
    fun processReceipt(orderId: String) {
        viewModelScope.launch { // Defaults to Dispatchers.Main.immediate!
            // Flawed: Thread.sleep blocks the UI thread, freezing all animations:
            Thread.sleep(3000) 
            
            // Flawed: Synchronous file read executes directly on Main Looper:
            val localReceipt = File("/sdcard/receipt.pdf").readBytes()
            showReceipt(localReceipt)
        }
    }
}

// ✅ Production implementation: Main-safe suspending functions
class CorrectOrderViewModel(private val repository: ReceiptRepository) : ViewModel() {
    fun processReceipt(orderId: String) {
        viewModelScope.launch { // Executes on Main to safely update UI state
            // Offload CPU and I/O work cleanly to background thread pools:
            val receipt = repository.loadReceiptSafely(orderId)
            showReceipt(receipt)
        }
    }
}

// Inside Repository: Main-safety guarantee using withContext
class ReceiptRepository {
    suspend fun loadReceiptSafely(orderId: String): ByteArray = withContext(Dispatchers.IO) {
        File("/sdcard/receipt.pdf").readBytes() // Safely runs on IO worker thread pool
    }
}
```""",
    "short_en": """Launching a coroutine in viewModelScope or lifecycleScope runs on Dispatchers.Main by default. Coroutines are not automatically background threads; they merely manage suspension. If the coroutine executes blocking calls like Thread.sleep, synchronous file/DB operations, or heavy parsing without switching via withContext(Dispatchers.IO or Default), it directly blocks the Main Looper, causing frame drops and ANRs.""",
    "structured_en": """To begin with, launching a coroutine does not imply background execution; it simply launches an asynchronous continuation within a specific CoroutineDispatcher.
From an architectural standpoint, standard Android scopes like viewModelScope and lifecycleScope are configured with Dispatchers.Main by default. When developers write synchronous or blocking operations directly inside these launch blocks, those instructions execute directly on the Android OS main thread.
In production scenarios, the most common blocking culprits include synchronous file access, large JSON payload parsing, Thread.sleep invocations, and thread synchronization locks. Because the main thread's Looper is occupied executing these blocking tasks, it cannot process input touch events, execute Measure/Layout/Draw passes, or service Choreographer frame callbacks, directly resulting in severe jank and ANRs.
As for boundary management, senior engineers enforce the Main-Safety principle. Every public suspending function exposed by repositories and data sources must be intrinsically safe to call from the main thread, encapsulating any blocking I/O or heavy computation inside withContext(Dispatchers.IO) or withContext(Dispatchers.Default).""",
    "deep_senior_en": """At the Android platform architecture level, the main thread operates as an infinite event dispatch loop driven by Looper.loop() and MessageQueue. The thread sleeps via the Linux epoll_wait system call until the Linux kernel signals events on its native file descriptors, such as hardware VSYNC pulses from the SurfaceFlinger hardware composer or input touch events delivered via Binder IPC from InputManagerService.
When a coroutine scheduled on Dispatchers.Main executes a blocking statement (such as Thread.sleep, synchronous Room database queries, or heavy XML parsing), the main thread remains trapped in that execution frame, unable to return control to Looper.loop(). As a result, incoming Message objects—including MSG_DO_FRAME callbacks posted by the Choreographer every 16.6 milliseconds (or 8.3ms on 120Hz displays)—remain queued and unhandled. When the InputDispatcher attempts to deliver a touch event and discovers that the main looper has not acknowledged the previous message within the 5-second timeout window, the ActivityManagerService issues a fatal ANR and dumps thread stacks into /data/anr/traces.txt.
Furthermore, substituting delay with Thread.sleep illustrates the fundamental mechanical difference between suspension and thread blocking. delay instantiates a CancellableContinuation and schedules a delayed message on the Handler without monopolizing the thread, allowing the Looper to process intervening frame renders. Thread.sleep puts the OS thread to sleep entirely.
Staff engineers enforce Main-Safety via static analysis: configuring Android Lint to flag disk or network operations on the main thread, banning Thread.sleep in production code, and ensuring that all repository calls offload to appropriate thread pools using withContext.""",
    "meta_ar": {
        "id": "MEM-22",
        "questionAr": "لماذا قد يتعرض الـ Main Thread للحظر بالرغم من أنك أطلقت كودك داخل Coroutine؟",
        "topicAr": "إدارة الذاكرة والـ ANR وتحسين الأداء",
        "evaluates_ar": "- إدراك أن الكوروتينات في viewModelScope تعمل على Dispatchers.Main افتراضياً.\n- الفهم الدقيق لآلية عمل الـ Main Looper والـ MessageQueue ودور Choreographer.\n- تطبيق مبدأ الـ Main-Safety باستخدام withContext لعزل العمليات الثقيلة.",
        "why_it_matters_ar": "الاعتقاد الخاطئ بأن مجرد استخدام `launch` ينقل الكود للخلفية تلقائياً هو أحد أكثر أسباب الـ ANRs وسقوط الإطارات انتشاراً في أندرويد. خيط الـ Main هو المسؤول عن رسم الشاشة والتفاعل، وحظره بأي عملية I/O أو فك تشفير ثقيل يجمد واجهة المستخدم ويدمر تجربة الاستخدام.",
        "worked_example_ar": "توضيح الخطأ القاتل وكيفية تحقيق الـ Main-Safety بالـ Dispatcher الصحيح:\n```kotlin\n// ❌ كود يحظر خيط الـ Main مباشرة ويسبب ANR:\nviewModelScope.launch { // يعمل على Dispatchers.Main افتراضياً!\n    Thread.sleep(2000) // حظر صريح لخيط الواجهة\n    val data = File(\"/sdcard/file.txt\").readText() // قراءة ملف متزامنة\n}\n\n// ✅ الحل الهندسي بتطبيق الـ Main-Safety:\nclass DataRepository {\n    suspend fun loadData(): String = withContext(Dispatchers.IO) {\n        File(\"/sdcard/file.txt\").readText() // يعمل بأمان على ثريدات الـ IO\n    }\n}\n```",
        "trade_offs_ar": "نقل العمليات لخيوط الـ IO أو Default عبر withContext يحرر خيط الواجهة تماماً ويمنع الـ ANR، ولكنه يضيف تكلفة Context Switching وتبديل خيوط طفيفة جداً، لذا يجب حصر التبديل في العمليات الثقيلة الحقيقية وعدم التبديل العشوائي للعمليات الحسابية المتناهية في الصغر.",
        "failure_modes_ar": "استخدام `Thread.sleep` بدلاً من `delay` داخل الكوروتين؛ فالأول يحظر الخيط بالكامل بينما الثاني يعلق الكوروتين ويسمح للـ Looper برسم الشاشة. خطأ آخر هو تنفيذ عمليات تشفير أو فك ضغط ملفات JSON ضخمة داخل launch ظناً أنها تجري في الخلفية.",
        "production_perspective_ar": "في تطبيقات الإنتاج، نطبق قاعدة Main-Safety الصارمة؛ أي دالة `suspend` في طبقة الـ Repository أو الـ UseCase يجب أن تكون آمنة للاستدعاء من خيط الـ Main مباشرة عبر عزل عملياتها داخل `withContext(Dispatchers.IO)`. كما نفعل StrictMode في نسخ التطوير لكشف أي قراءة ملفات على الـ Main Thread فوراً.",
        "how_to_answer_ar": "- **السبب الجذري:** وضح أن viewModelScope.launch تعمل على Dispatchers.Main افتراضياً.\n- **طبيعة الكوروتين:** أكد أن الكوروتين ليست ثريداً منفصلاً، بل وحدة إدارة مهام تعمل على الخيط المحدد لها.\n- **آلية الـ Main Thread:** اشرح دور الـ Looper والـ MessageQueue وكيف يمنع الحظر رسم الفريمات.\n- **الحل المعماري:** اشرح مبدأ الـ Main-Safety واستخدام `withContext(Dispatchers.IO)`.\n- **الفرق الجوهري:** قارن بين حظر `Thread.sleep` وتعليق `delay`.",
        "talking_points_ar": "ناقش دورة Looper.loop ونداءات epoll_wait في نواة لينكس، واستقبال نبضات VSYNC من Choreographer كل 16 ملي ثانية، وتفاصيل مهلة الـ 5 ثوانٍ للـ ANR في InputDispatcher.",
        "follow_ups_ar": "- **المحاور:** \"ما الفرق في التأثير على الـ Main Thread بين `Thread.sleep(1000)` و `delay(1000)` داخل viewModelScope؟\"\n  **المرشح:** \"دالة `Thread.sleep` بتحظر خيط الـ Main بالكامل وبتمنع الـ Looper من معالجة أي رسائل رسم أو لمس فيتجمد التطبيق تماماً. أما `delay` فبتعلق الكوروتين وتسجل رسالة مؤجلة في الـ Handler، وتترك خيط الـ Main حراً يرسم الفريمات ويتفاعل مع المستخدم بسلاسة.\"\n\n- **المحاور:** \"ما هو مبدأ الـ Main-Safety وكيف تطبقه في الـ Clean Architecture؟\"\n  **المرشح:** \"المبدأ ينص على أن أي دالة `suspend` معروضة للطبقات العليا يجب أن تضمن بداخلها أنها آمنة للاستدعاء من خيط الواجهة بدون أن يحتاج مستدعيها لتبديل الـ Dispatcher، ويتم تطبيقه بتغليف الـ I/O بـ withContext(Dispatchers.IO) داخل الـ Data Layer.\"",
        "self_check_ar": "هل وضحت الـ Dispatcher الافتراضي لـ viewModelScope؟ هل بينت آلية حظر الـ Looper؟ وهل شرحت الـ Main-Safety والفرق بين sleep و delay؟",
        "references_ar": "- [Coroutines best practices on Android](https://developer.android.com/kotlin/coroutines/coroutines-best-practices) — إرشادات التزامن والـ Main-Safety.\n- [Keep your app responsive (ANR)](https://developer.android.com/topic/performance/vitals/anr) — أسباب حظر خيط الواجهة وحدوث الـ ANR.\n\nتمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13.",
        "quick_answer_ar": "لأن إطلاق الكوروتين بـ `viewModelScope.launch` بيشتغل على `Dispatchers.Main` افتراضياً. الكوروتينات مش ثريدات خلفية سحرية؛ هي بتشتغل على الـ Dispatcher المحدد ليها. فلو الكود جواه عمليات حظر زي `Thread.sleep` أو قراءة ملفات أو فك تشفير بدون استخدام `withContext(Dispatchers.IO)`، هينفذها على خيط الواجهة مباشرة ويجمد الـ Looper ويسبب ANR.",
        "best_answer_ar": "فيه مفهوم خاطئ منتشر إن مجرد استخدام `launch` بيخلي الكود يشتغل في الخلفية تلقائياً، وده غير صحيح بالمرة.\n\nنطاقات أندرويد المعمارية زي `viewModelScope` و `lifecycleScope` مضبوطة افتراضياً على `Dispatchers.Main.immediate`. ده معناه إن الكوروتين بتبدأ وتشتغل مباشرة على خيط الـ Main التابع لنظام أندرويد.\n\nفلو المهندس كتب جواها عملية حظر متزامنة زي `Thread.sleep` أو قراءة ملفات من الذاكرة أو استعلام ثقيل في قاعدة البيانات، العمليات دي هتتنفذ مباشرة على خيط الـ Main وهتحظر الـ MessageQueue والـ Looper المسؤول عن استقبال لمسات المستخدم واستدعاءات الـ Choreographer لرسم الفريمات، وده اللي بيسبب تجميد الواجهة والـ ANR.\n\nالحل الهندسي المعتمد هو تطبيق مبدأ الـ Main-Safety؛ أي كود في طبقة الـ Repository بيعمل شغل I/O أو عمليات حسابية ثقيلة لازم يضمن بنفسه إنه آمن للاستدعاء، عن طريق تغليف الكود بـ `withContext(Dispatchers.IO)` أو `withContext(Dispatchers.Default)`، وبكده الـ ViewModel يقدر يستدعيه بأمان تام من خيط الواجهة.",
        "deep_answer_ar": "على مستوى الـ Android Platform Internals، خيط الـ Main شغال بنظام حلقة أحداث لا نهائية عبر `Looper.loop()` و `MessageQueue`. الخيط بينام في نواة لينكس عبر نداء النظام `epoll_wait` لحد ما يجيله إشعار على الـ File Descriptors، زي نبضات الـ VSYNC اللي بيبعتها الـ SurfaceFlinger كل 16.6 ملي ثانية (أو 8.3ms على شاشات 120Hz) للـ Choreographer علشان يبدأ دورات القياس والرسم (Measure, Layout, Draw).\n\nلما كوروتين شغالة على `Dispatchers.Main` تنفذ عملية حظر حقيقية (زي Thread.sleep أو Binder call متزامن أو parsing لملف JSON ضخم)، خيط الـ Main بيفضل محبوس داخل إطار التنفيذ ده ومش بيعرف يرجع لـ `Looper.loop()` لسحب الرسائل التالية في الطابور. فلما المستخدم يلمس الشاشة، الـ `InputDispatcher` بيبعت لمسة عبر الـ Binder IPC، ولما يلاقي إن الرسالة السابقة متمتش معالجتها خلال مهلة الـ 5 ثوانٍ، نظام الـ ActivityManagerService بيتدخل فوراً ويطلع حوار الـ ANR.\n\nالفرق الجوهري بين `Thread.sleep` و `delay` بيوضح آلية الكوروتينات؛ دالة `delay` مش بتحظر الثريد، دي بتعلق الكوروتين وتسجل كائن `CancellableContinuation` في الـ Handler كرسالة مستقبلية وتترك خيط الـ Main يكمل رسم الشاشة بسلاسة. أما `Thread.sleep` فبينيم ثريد نظام التشغيل بالكامل.\n\nعلشان كده في الفرق الهندسية الكبيرة، بنشغل أداة StrictMode في الـ Debug builds ونفعل قواعد Lint صارمة تمنع تشغيل أي I/O على الـ Main Thread وتلزم باستخدام `withContext(Dispatchers.IO)` لحماية استجابة التطبيق بنسبة 100%."
    }
}

# =======================================================
# MEM-23: App freeze when decoding large image
# =======================================================
DATA["MEM-23"] = {
    "concept_en": """Application freezes during image decoding occur primarily due to two interrelated performance bottlenecks: main-thread CPU blocking during rasterization, and aggressive memory allocation thrashing triggering major garbage collection pauses. Digital cameras and modern smartphones capture images at resolutions exceeding 48 megapixels (e.g., 8000x6000 pixels). Attempting to decode such an image naively via BitmapFactory.decodeStream without downsampling requires loading the entire uncompressed pixel buffer into memory. In ARGB_8888 configuration (4 bytes per pixel), an 8000x6000 image demands roughly 192 megabytes of contiguous heap allocation in a single instant. Allocating this massive buffer on the Android runtime triggers synchronous Large Object Space (LOS) allocations and forces Concurrent Copying GC pauses. Diagnosing the issue involves using the CPU Profiler's System Trace to capture BitmapFactory.nativeDecode latency and Memory Profiler to inspect heap spikes. Resolution requires downsampling via BitmapFactory.Options.inSampleSize, decoding on Dispatchers.IO, and leveraging modern memory-efficient formats like Bitmap.Config.HARDWARE.""",
    "walkthrough_en": """Efficiently downsampling and decoding high-resolution images:
```kotlin
// Production utility: Memory-safe image decoding using inSampleSize
suspend fun decodeSampledBitmapFromUri(
    context: Context,
    uri: Uri,
    reqWidth: Int,
    reqHeight: Int
): Bitmap = withContext(Dispatchers.IO) {
    val options = BitmapFactory.Options().apply {
        // Step 1: Decode dimensions only without allocating pixel memory
        inJustDecodeBounds = true
    }
    context.contentResolver.openInputStream(uri)?.use { stream ->
        BitmapFactory.decodeStream(stream, null, options)
    }

    // Step 2: Calculate the optimal power-of-two inSampleSize
    options.inSampleSize = calculateInSampleSize(options, reqWidth, reqHeight)

    // Step 3: Decode the actual downsampled bitmap using hardware configuration
    options.inJustDecodeBounds = false
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
        options.inPreferredConfig = Bitmap.Config.HARDWARE // Immutable GraphicBuffer in GPU memory
    }

    context.contentResolver.openInputStream(uri)?.use { stream ->
        BitmapFactory.decodeStream(stream, null, options)
            ?: throw IllegalStateException("Failed to decode bitmap from stream")
    }
}

fun calculateInSampleSize(options: BitmapFactory.Options, reqWidth: Int, reqHeight: Int): Int {
    val (height: Int, width: Int) = options.outHeight to options.outWidth
    var inSampleSize = 1
    if (height > reqHeight || width > reqWidth) {
        val halfHeight: Int = height / 2
        val halfWidth: Int = width / 2
        while (halfHeight / inSampleSize >= reqHeight && halfWidth / inSampleSize >= reqWidth) {
            inSampleSize *= 2
        }
    }
    return inSampleSize
}
```""",
    "short_en": """Freezes during image decoding occur when large images are decoded synchronously on the main thread or trigger massive memory allocations that force garbage collection thrashing. Diagnose the issue using System Trace for nativeDecode slices and Memory Profiler for allocation spikes. Fix it by calculating inSampleSize via inJustDecodeBounds, offloading to Dispatchers.IO, and using Bitmap.Config.HARDWARE.""",
    "structured_en": """To begin with, an app freeze during image decoding indicates either main-thread compute saturation or severe memory allocation pressure.
From an architectural standpoint, an uncompressed bitmap requires width multiplied by height multiplied by color depth in bytes. Decoding a modern 48-megapixel camera capture using ARGB_8888 demands nearly 200 megabytes of memory. If decoded naively on the main thread, the native C++ rasterizer monopolizes CPU cycles for seconds. Even on background threads, requesting such a large allocation instantly forces the ART runtime to execute synchronous garbage collections to compact the heap, pausing UI rendering.
In production scenarios, diagnosis begins in Android Studio Profiler. In CPU System Trace, we inspect the main thread for long BitmapFactory.nativeDecode slices overlapping frame drops. In Memory Profiler, we observe immediate vertical allocation spikes inside the Large Object Space (LOS).
As for boundary management, we resolve the bottleneck through three steps. First, we read image dimensions without pixel allocation using inJustDecodeBounds. Second, we compute a power-of-two inSampleSize to downsample the image to match the target View dimensions. Finally, we execute decoding inside withContext(Dispatchers.IO) and set Bitmap.Config.HARDWARE to store pixel buffers directly in GPU memory.""",
    "deep_senior_en": """Under the hood of the Android graphics pipeline, bitmap allocation semantics evolved significantly between Android 8.0 (API 26) and modern versions. Prior to Android 8.0, bitmap pixel byte arrays resided in the Java heap, directly competing for application heap limits and frequently throwing OutOfMemoryError. From Android 8.0 onwards, Skia allocates bitmap pixel memory in the native process heap via native malloc. However, native allocation does not grant immunity from memory pressure: the ART runtime tracks native allocations through NativeAllocationRegistry, and when native usage surges, it triggers synchronous Java GC passes to clean up unreachable native wrappers.
Furthermore, massive allocations utilize the Large Object Space (LOS), which bypasses standard generational copying collection and incurs substantial page-clearing and page-fault overhead in the Linux kernel. If the image resolution is extreme, decoding on the main thread triggers an immediate Choreographer frame drop sequence, leading directly to an ANR.
Using Bitmap.Config.HARDWARE (introduced in API 26) delivers substantial performance advantages. When configured, Skia allocates the bitmap as an immutable GraphicBuffer or AHardwareBuffer shared directly with the GPU. This eliminates CPU-to-GPU memory copies during rendering passes and reduces process RAM footprint because pixel data is not mapped twice in user space. The primary limitation is that hardware bitmaps cannot be drawn onto with a software Canvas or modified with pixel manipulation APIs.
In staff-level architectures, custom manual decoding should rarely exist in application code. Teams integrate battle-tested libraries like Coil or Glide, which implement automatic inSampleSize downsampling, memory pooling via BitmapPool (reusing inBitmap buffers), and lifecycle-aware caching out of the box.""",
    "meta_ar": {
        "id": "MEM-23",
        "questionAr": "التطبيق يتجمد فقط عند فك تشفير صورة كبيرة. كيف تشخص وتعالج المشكلة؟",
        "topicAr": "إدارة الذاكرة والـ ANR وتحسين الأداء",
        "evaluates_ar": "- حساب استهلاك الذاكرة الفعلي للصور (العرض × الارتفاع × البايت لكل بكسل).\n- تشخيص عنق الزجاجة باستخدام CPU System Trace و Memory Profiler.\n- تطبيق تقنيات الـ Downsampling عبر inSampleSize واستخدام Bitmap.Config.HARDWARE.",
        "why_it_matters_ar": "فك تشفير الصور عالية الدقة (كاميرات 48+ ميجابكسل) قد يطلب 200 ميجابايت من الذاكرة في لحظة واحدة. إذا تم هذا الإجراء على خيط الواجهة، فإنه يحظر الـ Main Thread في كود Native لثوانٍ معدودة، أو يضغط على مجمّع القمامة (GC Trashing) فيتوقف التطبيق عن الاستجابة تماماً ويحدث ANR.",
        "worked_example_ar": "فك تشفير آمن يحسب أبعاد الصورة أولاً ثم يصغرها قبل حجز الذاكرة:\n```kotlin\nsuspend fun decodeSampledBitmap(context: Context, uri: Uri, reqW: Int, reqH: Int): Bitmap =\n    withContext(Dispatchers.IO) {\n        val options = BitmapFactory.Options().apply {\n            inJustDecodeBounds = true // قراءة الأبعاد فقط دون حجز أي بكسل في الذاكرة\n        }\n        context.contentResolver.openInputStream(uri)?.use {\n            BitmapFactory.decodeStream(it, null, options)\n        }\n\n        options.inSampleSize = calculateInSampleSize(options, reqW, reqH) // تصغير الأبعاد\n        options.inJustDecodeBounds = false\n        options.inPreferredConfig = Bitmap.Config.HARDWARE // تخزين مباشر في ذاكرة الـ GPU\n\n        context.contentResolver.openInputStream(uri)?.use {\n            BitmapFactory.decodeStream(it, null, options)!!\n        }\n    }\n```",
        "trade_offs_ar": "استخدام الـ Downsampling يقلل استهلاك الذاكرة وزمن المعالجة بنسبة 80%، ولكنه يقلل دقة الصورة إذا احتاجها المستخدم للتقريب الشديد (Zoom-in). استخدام `Bitmap.Config.HARDWARE` يخفض الذاكرة ويسرع الرسم على كارت الشاشة ولكنه يمنع تعديل الصورة بـ Software Canvas.",
        "failure_modes_ar": "فك تشفير الصورة مباشرة بـ `BitmapFactory.decodeFile` على خيط الـ Main، مما يحظر الواجهة فوراً. خطأ آخر هو نسيان غلق الـ InputStream، مما يسبب تسريب مراجع الملفات، أو محاولة تعديل Hardware Bitmap بفرشاة رسم مما يفجر كراش `IllegalArgumentException`.",
        "production_perspective_ar": "في تطبيقات الإنتاج الكبيرة، نمنع التعامل اليدوي المباشر مع BitmapFactory؛ نعتمد على مكتبات ناضجة مثل Coil أو Glide لأنها تطبق الـ Downsampling التلقائي بناءً على حجم الـ ImageView، وتستخدم كاش الذاكرة والـ Disk Cache وتعيد تدوير البايتات عبر `inBitmap`.",
        "how_to_answer_ar": "- **السبب المزدوج:** وضح أن التجمد ينتج إما عن حظر خيط الـ Main في الـ Native Rasterizer أو ضغط هائل على الـ GC.\n- **الحسبة الهندسية:** اشرح معادلة حجم الصورة (العرض × الارتفاع × 4 بايت لـ ARGB_8888).\n- **أدوات التشخيص:** اذكر CPU System Trace للبحث عن `nativeDecode` و Memory Profiler لقفزات الذاكرة.\n- **خطوات الحل:** 1) قراءة الأبعاد بـ inJustDecodeBounds؛ 2) حساب inSampleSize؛ 3) النقل لـ Dispatchers.IO؛ 4) استخدام Hardware Bitmaps.\n- **منظور الإنتاج:** الاعتماد على مكتبات Coil أو Glide وإعادة تدوير البكسلات.",
        "talking_points_ar": "اشرح موقع بكسلات الصور في الـ Native Memory منذ أندرويد 8.0 ودور NativeAllocationRegistry، وآلية Large Object Space في ART، ومفهوم AHardwareBuffer في معالجات الرسوميات.",
        "follow_ups_ar": "- **المحاور:** \"أين تخزن بكسلات الـ Bitmap في إصدارات أندرويد الحديثة (Android 8.0+)؟\"\n  **المرشح:** \"منذ أندرويد 8.0 (API 26)، أصبحت بكسلات الصور تُخزن في الـ Native C++ Heap عبر Skia وليس في الـ Java Heap، ولكن الـ Runtime يراقب حجمها عبر NativeAllocationRegistry ويشغل الـ GC إذا زادت المساحة المستهلكة.\"\n\n- **المحاور:** \"ما هي ميزة وعيب استخدام `Bitmap.Config.HARDWARE`؟\"\n  **المرشح:** \"الميزة أنها تُخزن مباشرة كـ GraphicBuffer في ذاكرة كارت الشاشة (GPU) مما يلغي نسخ البيانات ويسرع الرسم جداً. والعيب أنها كائنات غير قابلة للتعديل (Immutable) ولا يمكن الرسم عليها عبر Canvas أو استخراج بكسلاتها للتعديل البرمجي.\"",
        "self_check_ar": "هل حسبت حجم الذاكرة رياضياً؟ هل شرحت كيفية التشخيص بـ Profiler؟ وهل وضحت خطوات الحل الثلاثية بـ inSampleSize و Hardware Config؟",
        "references_ar": "- [Loading large bitmaps efficiently](https://developer.android.com/topic/performance/graphics/load-bitmap) — الدليل الرسمي لتحميل الصور وتقليل أبعادها.\n- [Manage bitmap memory](https://developer.android.com/topic/performance/graphics/manage-memory) — إدارة ذاكرة الصور وإعادة التدوير.\n\nتمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13.",
        "quick_answer_ar": "تجمد التطبيق عند فك تشفير صورة كبيرة بيحصل إما بسبب تشغيل عملية الـ Decode على خيط الـ Main، أو لأن الصورة حجمها ضخم جداً (مثلاً 200 ميجابايت) فبتجبر مجمّع القمامة يعمل GC Pauses متكررة. بنشخص ده بـ CPU Profiler للبحث عن `nativeDecode`، وبنعالجه بنقل الفك لـ `Dispatchers.IO` واستخدام `inSampleSize` لتصغير الصورة واستخدام `Bitmap.Config.HARDWARE`.",
        "best_answer_ar": "التجمد أثناء فك تشفير الصور بينتج عن عاملين أساسيين: استهلاك عالي لوقت المعالج في خيط الواجهة، أو ضغط مفاجئ على الذاكرة بيشغل مجمّع القمامة بشكل هستيري.\n\nلو الصورة ملتقطة بكاميرا حديثة بدقة 48 ميجابكسل، وفككناها بنمط ARGB_8888، حجم البكسلات في الذاكرة بيوصل لـ 200 ميجابايت تقريباً (8000 × 6000 × 4 بايت). لو العملية دي اتعملت على خيط الـ Main، كود الـ Native في مكتبة Skia هيحظر المعالج لثوانٍ معدودة ويفجر ANR فوري.\n\nطريقتي في التشخيص بتبدأ بفتح Android Studio Profiler؛ في الـ CPU System Trace هشوف شريحة طويلة جداً باسم `BitmapFactory.nativeDecode` حاظرة خيط الواجهة، وفي الـ Memory Profiler هشوف قفزة رأسية ضخمة في الـ Native memory.\n\nولحل المشكلة بنمشي على خطوات هندسية واضحة: أولاً بنقيس أبعاد الصورة فقط بدون حجز بكسلات باستخدام `inJustDecodeBounds = true`. ثانياً بنحسب معامل تصغير `inSampleSize` مناسب لحجم الشاشة. ثالثاً بننقل الفك لـ `Dispatchers.IO`. ورابعاً بنستخدم `Bitmap.Config.HARDWARE` علشان الصورة تتخزن مباشرة في ذاكرة كارت الشاشة GPU.",
        "deep_answer_ar": "تحت الكابوت في الـ Android Graphics Pipeline، بكسلات الصور مرت بتطورات معمارية كبيرة؛ قبل أندرويد 8 كانت البكسلات بتتحجز في الـ Java Heap وتنافس كود التطبيق وتفجر OOM سريعاً. ومن أندرويد 8.0 (API 26) فصاعداً، أصبحت مكتبة Skia بتحجز البكسلات في الـ Native Process Memory عبر malloc. لكن ده مش معناه إننا في أمان من الـ GC؛ لأن الـ ART بيراقب استهلاك الذاكرة دي بكائن `NativeAllocationRegistry`، ولما يلاقي قفزة بـ 200 ميجا بيعمل Forced Synchronous GC علشان يضغط الـ Heap، وده اللي بيسبب تجميد الواجهة.\n\nالصور الضخمة بتتحجز في منطقة متخصصة اسمها Large Object Space (LOS)، ودي عمليات حجزها وتفريغها بطيئة جداً وبتحتاج تعديل في صفحات الذاكرة بنظام Linux Page Faults.\n\nاستخدام `Bitmap.Config.HARDWARE` بيقدم نقلة نوعية؛ لأنه بيحجز الصورة كـ `AHardwareBuffer` أو `GraphicBuffer` بتتشير مباشرة مع الـ GPU، فبيوفر الذاكرة ويلغي عمليات الـ Memory Copy وقت الرسم. العيب الوحيد إنه مينفعش تعدل في بكسلاتها أو ترسم عليها بـ Software Canvas.\n\nوفي بيئات الإنتاج للشركات الكبيرة، بنمنع المطورين من كتابة كود فك تشفير يدوي بـ BitmapFactory؛ بنعتمد حصراً على مكتبات زي Coil أو Glide لأنها بتدمج الـ Downsampling التلقائي بحجم الـ ImageView، وبتعيد استخدام كائنات الـ Bitmap القديمة عبر خاصية `inBitmap` من الـ BitmapPool لتفادي تخصيص أي بايت جديد في الذاكرة."
    }
}

# =======================================================
# MEM-24: Reduce slow app startup without breaking correctness
# =======================================================
DATA["MEM-24"] = {
    "concept_en": """Optimizing slow Android application cold start without sacrificing runtime correctness requires targeting the critical execution path between process initialization and first-frame rendering. During cold startup, the Android OS creates the application process via zygote fork, executes ActivityThread.bindApplication, instantiates and attaches Application, initializes registered ContentProviders, and invokes Application.onCreate before launching the entry Activity. A primary anti-pattern in legacy codebases is ContentProvider bloat: third-party SDKs leverage auto-initializing providers to initialize prematurely, monopolizing main-thread time before the user interface appears. Resolving startup latency requires profiling with Perfetto and Macrobenchmark to establish baseline Time to Initial Display (TTID) and Time to Full Display (TTFD) metrics, consolidating initializations via Jetpack App Startup, deferring non-critical telemetry and network warm-ups to background worker threads, and packaging Baseline Profiles to pre-compile startup bytecode Ahead-of-Time.""",
    "walkthrough_en": """Consolidating and deferring initializations with Jetpack App Startup:
```kotlin
// Consolidating initializations into an explicit, dependency-managed initializer
class TelemetryInitializer : Initializer<TelemetryManager> {
    override fun create(context: Context): TelemetryManager {
        val manager = TelemetryManager(context)
        // Defer heavy network handshakes and disk caching to a background thread:
        CoroutineScope(Dispatchers.IO).launch {
            manager.warmUpBackgroundCaches()
        }
        return manager
    }

    override fun dependencies(): List<Class<out Initializer<*>>> = emptyList()
}

// In AndroidManifest.xml: replace multiple ContentProviders with App Startup
// <provider
//     android:name="androidx.startup.InitializationProvider"
//     android:authorities="${applicationId}.androidx-startup"
//     android:exported="false"
//     tools:node="merge">
//     <meta-data
//         android:name="com.example.TelemetryInitializer"
//         android:value="androidx.startup" />
// </provider>
```""",
    "short_en": """To reduce slow startup safely, profile the critical path using Perfetto and Macrobenchmark, measuring TTID and TTFD. Audit Application.onCreate and ContentProviders to eliminate blocking I/O, consolidate SDK initializations using Jetpack App Startup, defer non-critical dependencies to background threads, and bundle Baseline Profiles to precompile hot startup paths.""",
    "structured_en": """To begin with, optimizing app startup requires accelerating the delivery of the initial UI frame without compromising dependencies or security.
From an architectural standpoint, startup latency is segmented into Time to Initial Display (TTID), representing the first visible frame drawn by the system, and Time to Full Display (TTFD), indicating when interactive content is fully populated. Our goal is to minimize the critical path leading to TTID by eliminating blocking operations between zygote process creation and entry Activity display.
In production scenarios, we identify bottlenecks by capturing detailed Perfetto traces. We audit Application.onCreate and auto-initializing ContentProviders installed by third-party SDKs, which execute synchronously on the main thread before Application.onCreate completes. We replace fragmented ContentProviders with Jetpack App Startup, consolidating initializers and establishing explicit dependency graphs.
As for boundary management, components are categorized into three categories: critical components required immediately for UI rendering are initialized synchronously; non-critical telemetry and logging SDKs are deferred to background coroutines; and deep secondary features are lazily initialized only when the user navigates to their specific screens. Finally, bundling Baseline Profiles pre-compiles these startup code paths into native code at installation time.""",
    "deep_senior_en": """At the lower operating system and platform tier, cold start involves a sequence of Binder IPC handshakes orchestrated by the ActivityManagerService (AMS) and WindowManagerService (WMS). When a user launches an application, the OS forks a new process from the Zygote daemon. Zygote loads common framework classes and resources, then branches into ActivityThread.main. The entry process communicates with AMS via attachApplication, after which the main thread executes ActivityThread.bindApplication, instantiating the Application object and executing ContentProvider.onCreate for every provider declared in the merged AndroidManifest.
ContentProvider bloat is particularly damaging because ContentProviders initialize before Application.onCreate. If five analytics and crash SDKs each insert a provider, the main looper incurs repeated disk reads and class-loading delays before application logic even starts. Jetpack App Startup addresses this by combining multiple initializers into a single InitializationProvider, eliminating provider dispatch overhead.
Tracing startup with Perfetto reveals exact slice durations. Senior engineers look for Binder IPC stalls (such as synchronous SharedPreferences disk flushes via apply or commit), class verification overhead, and JIT compilation delays. By generating Baseline Profiles using Macrobenchmark, we provide ART with pre-computed compilation rules that pre-compile startup classes with dex2oat at installation, yielding a 20% to 40% reduction in cold start latency.
Correctness is preserved by maintaining a strict initialization graph: authentication tokens and database schema initializers execute on the critical path, while analytics handshakes, remote config prefetching, and crash reporter network beacons are dispatched asynchronously on background thread pools.""",
    "meta_ar": {
        "id": "MEM-24",
        "questionAr": "كيف تقلص وقت بدء تشغيل التطبيق البطيء دون الإخلال بصحة العمل وسلوك التطبيق؟",
        "topicAr": "إدارة الذاكرة والـ ANR وتحسين الأداء",
        "evaluates_ar": "- قياس وفهم الفارق بين مؤشر TTID (زمن أول فريم) ومؤشر TTFD (اكتمال تحميل المحتوى).\n- التخلص من تضخم الـ ContentProviders ودمجها عبر Jetpack App Startup.\n- تقسيم التهيئة إلى فورية ومؤجلة وكسولة وتوظيف الـ Baseline Profiles لتسريع الـ Cold Start.",
        "why_it_matters_ar": "بدء التشغيل البطيء (Slow Cold Start) يرفع معدلات التخلي عن التطبيق ويزيد نسبة الحذف في الأيام الأولى للمستخدمين. وضع كل كود التهيئة في `Application.onCreate` يحظر خيط الـ Main ويؤخر ظهور أول شاشة، مما يضع التطبيق في المنطقة الحمراء في تقارير Google Play Vitals.",
        "worked_example_ar": "توظيف مكتبة Jetpack App Startup وتاجيل التهيئة غير الحرجة للخلفية:\n```kotlin\nclass AnalyticsInitializer : Initializer<Unit> {\n    override fun create(context: Context) {\n        // تأجيل تهيئة SDK الإحصائيات لثريد خلفي لمنع حظر خيط الواجهة:\n        CoroutineScope(Dispatchers.IO).launch {\n            AnalyticsSdk.init(context)\n        }\n    }\n    override fun dependencies(): List<Class<out Initializer<*>>> = emptyList()\n}\n```\nيتم دمج هذا المكون في مصفوفة App Startup داخل الـ Manifest لتفادي فتح ContentProvider مستقل.",
        "trade_offs_ar": "تأجيل تهيئة بعض الـ SDKs للخلفية يسرع ظهور أول فريم بنسبة 40%، لكنه يتطلب التأكد من أن الكود لا يستدعي تلك المكتبات قبل اكتمال تهيئتها لمنع حدوث NullPointerException أو ضياع أول حدث إحصائي.",
        "failure_modes_ar": "تأجيل التحقق من الـ Auth Token أو أمان الجلسة للخلفية مما يسمح للمستخدم برؤية شاشات خاصة قبل طرده لصفحة تسجيل الدخول. خطأ آخر هو استخدام `SharedPreferences.commit()` المتزامنة على خيط الـ Main أثناء الإقلاع بدلاً من `apply()` أو DataStore.",
        "production_perspective_ar": "في تطبيقات الشركات الكبرى، نحدد ميزانية إقلاع صارمة (أقل من 1.2 ثانية للـ Cold Start). نستخدم Macrobenchmark لقياس TTID و TTFD في الـ CI، ونولد Baseline Profiles مع كل إصدار، ونقسم التهيئة إلى 3 مسارات: حرج فوري، ومؤجل بالخلفية، وكسول عند الطلب (Lazy).",
        "how_to_answer_ar": "- **المؤشرات الهندسية:** ابدأ بتعريف TTID (أول رسمة) و TTFD (جاهزية التفاعل الكاملة).\n- **أدوات القياس:** اذكر Perfetto لفحص الـ Slices و Macrobenchmark للتحقق الرقمي.\n- **الجناة الأساسيون:** وضح تضخم ContentProviders وقراءة الملفات المتزامنة في `Application.onCreate`.\n- **استراتيجية الحل:** 1) Jetpack App Startup؛ 2) تأجيل غير الحرج للـ IO؛ 3) التهيئة الكسولة (Lazy)؛ 4) Baseline Profiles.\n- **ضمان الصحة:** أكد على عدم تأجيل الأمان والـ Database Schemas لتفادي الأعطال.",
        "talking_points_ar": "اشرح مسار Zygote fork واستدعاء ActivityThread.bindApplication، وسبب تشغيل ContentProvider قبل Application.onCreate، وتأثير AOT compilation عبر dex2oat في تقليل Class Loading.",
        "follow_ups_ar": "- **المحاور:** \"لماذا تشغل مكتبات كثيرة ContentProvider خاص بها بدلاً من طلب التهيئة في Application؟\"\n  **المرشح:** \"لتوفير تجربة تثبيت سريعة للمطور بدون كتابة كود يدوي (Auto-init)؛ ولكن عند تراكم عدة مكتبات، تتعدد الـ ContentProviders التي تعمل تسلسلياً على خيط الـ Main قبل حتى استدعاء Application.onCreate، وده بيسبب بطء إقلاع التطبيق، والحل هو دمجها بـ Jetpack App Startup.\"\n\n- **المحاور:** \"ما الفرق بين TTID و TTFD في قياس الإقلاع؟\"\n  **المرشح:** \"الـ TTID (Time to Initial Display) هو الزمن حتى رسم أول فريم للواجهة على الشاشة، أما الـ TTFD (Time to Full Display) فهو الزمن حتى اكتمال تحميل البيانات التفاعلية من الشبكة واستدعاء reportFullyDrawn().\"",
        "self_check_ar": "هل عرفت TTID و TTFD؟ هل شرحت مشكلة ContentProviders؟ وهل وضحت استراتيجية التقسيم الثلاثي للتهيئة واستخدام Baseline Profiles؟",
        "references_ar": "- [App startup time](https://developer.android.com/topic/performance/vitals/launch-time) — إرشادات أندرويد لتقليص زمن الإقلاع.\n- [App Startup library](https://developer.android.com/topic/libraries/app-startup) — التوثيق الرسمي لمكتبة Jetpack App Startup.\n\nتمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13.",
        "quick_answer_ar": "لتقليص وقت الإقلاع بأمان، بنقيس المسار الحرج بـ Perfetto و Macrobenchmark لتحديد مؤشرات TTID و TTFD. بنفحص `Application.onCreate` والـ ContentProviders ونلغي أي قراءة ملفات أو شبكة متزامنة، وبنجمع المكتبات عبر Jetpack App Startup، وبنأجل الإحصائيات لثريدات خلفية، وبنرفق Baseline Profiles لترجمة كود الإقلاع مسبقاً.",
        "best_answer_ar": "تسريع بدء التشغيل (Cold Start) بيتطلب تحسين المسار الحرج اللي بيوصلنا لأول فريم ظاهر للمستخدم، وهو مؤشر TTID، بدون ما نكسر منطق التطبيق وأمانه.\n\nخطتي بتبدأ بالقياس الدقيق باستخدام أدوات Perfetto و Macrobenchmark علشان نعرف بالملي ثانية فين الوقت بيضيع. الجاني الأكبر في معظم التطبيقات هو تكدس تهيئة الـ SDKs داخل `Application.onCreate`، وتضخم الـ ContentProviders الخفية اللي بتنزلها مكاتب الطرف الثالث علشان تعمل Auto-init لنفسها، لأن الـ Providers دي بتشتغل على خيط الـ Main حتى قبل ما دالة `onCreate` بتاعة التطبيق تبدأ.\n\nالحل بنطبقه عبر استراتيجية تصنيف ثلاثية: أولاً، الكود الحرج جداً زي فحص الـ Auth ومسار قاعدة البيانات بنخليه فوري ومحسن. ثانياً، المكتبات الثانوية زي الـ Analytics وأدوات الـ Tracking بنجمعها داخل مكتبة Jetpack App Startup في Provider واحد ونأجل نداءاتها للـ Background عبر Coroutines. ثالثاً، الميزات غير المستخدمة فوراً بنخليها Lazy عند فتح شاشاتها.\n\nوأخيراً بنولد ونرفق Baseline Profile مع التطبيق، وده بيخلي مترجم ART يترجم كود الإقلاع كاملاً لـ Machine Code وقت التثبيت ويقلل زمن الفتح بنسبة تصل لـ 40%.",
        "deep_answer_ar": "على مستوى الـ Android OS Internals، الـ Cold Start بيبدأ لما نظام التشغيل يعمل Fork لعملية جديدة من سيرفر الـ Zygote daemon. العملية بتبدأ بتشغيل `ActivityThread.main` اللي بيبعت نداء Binder لـ ActivityManagerService عبر `attachApplication`، والـ AMS بيرد بأمر `bindApplication`. في المرحلة دي خيط الـ Main بينفذ `ContentProvider.onCreate` لكل البروفايدرز المسجلة في الـ Manifest، وبعدها مباشرة بيستدعي `Application.onCreate` ثم دورة حياة الـ Activity.\n\nتضخم الـ ContentProviders بيعمل كارثة؛ لأن كل Provider بينفذ استعلامات وقراءة إعدادات من الـ Disk على خيط الـ Main قبل ظهور أي شاشة. مكتبة Jetpack App Startup بتحل ده بإنها بتدمج كل الـ Initializers داخل `InitializationProvider` واحد وبترتب شجرة الاعتماديات بكفاءة.\n\nعبر Perfetto Traces، بنفتش على الـ Binder IPC Calls المتزامنة، زي استخدام `SharedPreferences.commit()` أو فتح اتصالات مشفرة مبكرة. بنستبدل ده بالتهيئة الخلفية مع مراعاة صحة العمل؛ يعني لو الـ Token محتاج فحص، بنفحصه سريعاً على الـ Main لو الكاش جاهز، لكن بنمنع أي نداءات شبكة حظرية.\n\nوفي بيئات الإنتاج، بنربط قياساتنا بـ `reportFullyDrawn()` لحساب الـ TTFD بدقة، وبنستخدم أداة Macrobenchmark في مسار الـ CI للتأكد من إن أي تعديل معماري ميرجعش زمن الإقلاع للوراء، وبنعتمد على فلاتر الـ Speed-profile في الـ Baseline Profiles لضمان تسريع الـ Class Loading والـ Method Invocations وقت الإقلاع بنسبة تتراوح بين 25% و 40%."
    }
}

# =======================================================
# MEM-25: Rare ANR from database lock contention
# =======================================================
DATA["MEM-25"] = {
    "concept_en": """Diagnosing and resolving rare Application Not Responding (ANR) occurrences caused by database lock contention requires analyzing native thread dumps, SQLite transactional mechanics, and Android looper state. In a typical database contention scenario, a background coroutine initiates a long-running, multi-statement write transaction (such as bulk data synchronization or migration) on a SQLite database. If a user interaction on the UI thread subsequently triggers a read or write operation against the same database, the UI thread must acquire the database connection lock. In standard SQLite Rollback Journal mode, readers block writers and writers block readers. Even under Write-Ahead Logging (WAL) mode, if the connection pool is exhausted or a write lock is contended, the UI thread enters a BLOCKED or WAITING state inside native SQLiteConnectionPool or ReentrantLock routines. If the background transaction holds the lock for more than five seconds, the Activity Manager Service declares an ANR. Resolution requires inspecting /data/anr/traces.txt to identify the blocking thread ID, enabling WAL mode, breaking large transactions into batched chunks, and strictly banning all main-thread database access.""",
    "walkthrough_en": """Configuring Room for WAL mode and batched non-blocking write transactions:
```kotlin
// 1. Enable Write-Ahead Logging (WAL) in Room builder:
val database = Room.databaseBuilder(context, AppDatabase::class.java, "app.db")
    .setJournalMode(RoomDatabase.JournalMode.WRITE_AHEAD_LOGGING) // Allows concurrent readers during background write
    .build()

// 2. Chunker pattern for long-running background writes to avoid holding write locks:
class TransactionWriter(private val dao: OrderDao) {
    suspend fun insertLargeCatalog(items: List<CatalogItem>) = withContext(Dispatchers.IO) {
        // Chunk large write payload into smaller discrete transactions:
        items.chunked(100).forEach { batch ->
            dao.insertBatchTransaction(batch)
            // Yield execution briefly to allow waiting threads and checkpoints to process:
            yield()
        }
    }
}
```""",
    "short_en": """To find database lock contention ANRs, inspect /data/anr/traces.txt to identify the main thread BLOCKED on SQLiteConnectionPool or a database mutex, and locate the background holder thread. We fix it by enabling SQLite Write-Ahead Logging (WAL mode), eliminating any main-thread database access, chunking large write transactions into small batches, and using yield() between batches.""",
    "structured_en": """To begin with, database lock contention ANRs occur when the Android main thread blocks waiting for a database connection mutex held by a long-running background transaction.
From an architectural standpoint, the primary diagnostic artifact is the system ANR trace file located at /data/anr/traces.txt or exported via Google Play Console and Crashlytics. In this trace, we inspect the main thread stack. If the main thread state is BLOCKED or WAITING with frames indicating SQLiteConnectionPool.acquireConnection or ReentrantLock.lock, we extract the mutex lock identifier and search the file for the background worker thread holding that identical lock.
In production scenarios, the root cause is typically a background synchronization worker executing a large bulk write transaction encompassing thousands of records. In default SQLite rollback journal mode, a single write transaction places an exclusive lock on the database file, blocking all concurrent read queries.
As for boundary management, we apply a three-tiered architectural fix. First, we enable SQLite Write-Ahead Logging (WAL mode), which allows concurrent readers while a write transaction proceeds. Second, we divide large background writes into smaller batched chunks, calling yield between batches to release the lock. Finally, we strictly enforce that the main thread never performs database operations directly, routing all queries through asynchronous Flow and suspend functions on Dispatchers.IO.""",
    "deep_senior_en": """At the SQLite engine and Linux operating system level, database concurrency is governed by locking protocols on the database file descriptor. In legacy Rollback Journal mode, SQLite uses POSIX advisory file locks with states transitioning from SHARED to RESERVED, PENDING, and EXCLUSIVE. An EXCLUSIVE lock prevents all other threads and processes from reading or writing. If the main thread attempts to read while a background worker holds an EXCLUSIVE lock, the main thread hangs in native SQLite calls (such as sqlite3_step or sqlite3_prepare_v2), triggering a 5-second InputDispatching ANR.
Enabling Write-Ahead Logging (WAL mode) decouples readers from writers by appending mutations to an auxiliary `-wal` file while preserving original data in the main `.db` file. Under WAL, multiple readers can execute concurrently alongside a single active writer. However, lock contention can still cause ANRs even under WAL mode if: 1) the main thread attempts a write operation while a background write is underway; 2) the connection pool size (typically 1 writer and 4 readers in Android's SQLiteConnectionPool) is exhausted; or 3) an aggressive background writer triggers a synchronous WAL checkpoint pass that locks the entire database to transfer WAL frames back into the main database file.
Furthermore, thread scheduling introduces Priority Inversion risks. If a background worker running at Linux nice priority 10 (background cgroup) holds a database write lock, and the main thread (running at priority -10 in the top-app cgroup) blocks waiting for that lock, the background thread may be starved of CPU time on an overloaded device, prolonging the lock duration and guaranteeing an ANR.
Staff engineers eliminate these risks by configuring Room with WRITE_AHEAD_LOGGING, executing batch insertions in discrete chunks of 50 to 100 rows, inserting yield points to allow checkpoints to drain, and routing all database interactions through Dispatchers.IO with strict Architecture Component lint rules.""",
    "meta_ar": {
        "id": "MEM-25",
        "questionAr": "كيف تعثر وتشخص وتصلح الـ ANR النادر الناتج عن تزاحم أقفال قاعدة البيانات؟",
        "topicAr": "إدارة الذاكرة والـ ANR وتحسين الأداء",
        "evaluates_ar": "- قراءة وتحليل ملف /data/anr/traces.txt وتحديد الثريد الحابس والمحبوس.\n- فهم الفارق بين Rollback Journal و Write-Ahead Logging (WAL mode) في SQLite.\n- معالجة مشاكل الـ Priority Inversion وتجزئة المعاملات الكبيرة عبر Chunks و yield.",
        "why_it_matters_ar": "أعطال الـ ANR الناتجة عن أقفال قاعدة البيانات نادرة وصعبة التكرار في بيئات التطوير، لكنها تظهر بكثافة في الإنتاج على أجهزة المستخدمين الضعيفة عند تشغيل مزامنة خلفية أثناء تصفح التطبيق، مما يرفع مؤشر الـ Bad Behavior في تقارير Vitals.",
        "worked_example_ar": "تفعيل نمط الـ WAL وتجزئة عمليات الكتابة الكبيرة لمنع حظر القفل:\n```kotlin\n// 1. تفعيل نمط WAL للسماح بالقراءة المتزامنة أثناء الكتابة:\nval db = Room.databaseBuilder(context, AppDatabase::class.java, \"app.db\")\n    .setJournalMode(RoomDatabase.JournalMode.WRITE_AHEAD_LOGGING)\n    .build()\n\n// 2. تجزئة الإدخال الضخم لمنح فرصة للثريدات الأخرى لاستخدام القاعدة:\nsuspend fun saveCatalog(items: List<Item>) = withContext(Dispatchers.IO) {\n    items.chunked(100).forEach { batch ->\n        dao.insertBatch(batch) // معاملة صغيرة وسريعة\n        yield() // إتاحة الفرصة للـ Checkpoint والثريدات الأخرى\n    }\n}\n```",
        "trade_offs_ar": "تفعيل نمط WAL يزيد من سرعة القراءة والكتابة المتزامنة بشكل ملحوظ، ولكنه يستهلك مساحة تخزين إضافية لملفي `-wal` و `-shm` على القرص. تجزئة المعاملات لـ Chunks تمنع الـ ANR ولكنها تفقد الذرية الكاملة (All-or-Nothing) للعملية ككل، ما لم يتم معالجتها منطقياً.",
        "failure_modes_ar": "الاعتماد على Rollback Journal القديم مع تشغيل مزامنة بآلاف السجلات، مما يقفل ملف الداتابيز تماماً. خطأ آخر هو محاولة القراءة من قاعدة البيانات مباشرة من خيط الـ Main عبر `allowMainThreadQueries()`، أو حدوث Priority Inversion بتشغيل كاتب الخلفية بأولوية منخفضة جداً تحرمه من المعالج أثناء حبسه للقفل.",
        "production_perspective_ar": "في تطبيقات التكنولوجيا المالية، نمنع نهائياً أي استعلام لقاعدة البيانات على خيط الـ Main. نفعل نمط WAL في Room، ونقسم عمليات التزامن الكبيرة إلى كتل صغيرة مع إضافة `yield()` بينها، ونراقب تقارير الـ ANR Clusters في Google Play Console للتحقق من زوال تزاحم الأقفال.",
        "how_to_answer_ar": "- **مصدر الحقيقة:** ابدأ بملف `/data/anr/traces.txt` أو تقارير Crashlytics ANR.\n- **طريقة الفحص:** وضح فحص خيط الـ Main والبحث عن حالة BLOCKED أو WAITING على `SQLiteConnectionPool`.\n- **تحديد الفاعل:** بيّن كيفية البحث عن الثريد الحامل لنفس الـ Lock ID في الملف.\n- **السبب الجذري:** اشرح القفل الحصري في Rollback Journal وتزاحم المعاملات الكبيرة.\n- **العلاج الهندسي:** 1) تفعيل WAL mode؛ 2) تجزئة المعاملات لـ Chunks بـ yield؛ 3) منع استدعاء الداتابيز من خيط الواجهة نهائياً.",
        "talking_points_ar": "ناقش آلية POSIX file locking في SQLite، ودور ملفات wal و shm، وظاهرة Priority Inversion وكيف تؤخر الـ Low-priority background thread أثناء حبس الـ Main thread، والتحكم في حجم الـ Connection Pool.",
        "follow_ups_ar": "- **المحاور:** \"كيف يساعد نمط Write-Ahead Logging (WAL) في تقليل الـ Lock Contention؟\"\n  **المرشح:** \"في نمط Rollback Journal العادي، الكتابة بتقفل القاعدة تماماً وتمنع أي قراءة. نمط الـ WAL بيكتب التعديلات في ملف منفصل `-wal` ويترك ملف `.db` الأصلي متاحاً، وده بيسمح للقراء (Readers) يقرأوا بالتوازي في نفس اللحظة اللي فيها كاتب واحد شغال، فبيمنع حظر القراءة تماماً.\"\n\n- **المحاور:** \"ما هي ظاهرة الـ Priority Inversion في سياق هذا الـ ANR؟\"\n  **المرشح:** \"تحصل لما ثريد خلفي بأولوية منخفضة (Background Cgroup) يكون ماسك قفل الداتابيز، وخيط الـ Main (أعلى أولوية) يحاول ياخد نفس القفل وينتظر. نظام التشغيل على جهاز مضغوط ممكن يحرم الثريد المنخفض من دورات المعالج، فيفضل ماسك القفل لفترة أطول من 5 ثوانٍ، ويتفجر الـ ANR في وش خيط الواجهة.\"",
        "self_check_ar": "هل حددت ملف traces.txt؟ هل شرحت كيفية ربط الثريد الحابس بالمحبوس؟ وهل وضحت دور WAL وتجزئة المعاملات وظاهرة Priority Inversion؟",
        "references_ar": "- [SQLite Write-Ahead Logging](https://www.sqlite.org/wal.html) — التوثيق الرسمي لنمط WAL والتزامن.\n- [Diagnose ANRs](https://developer.android.com/topic/performance/vitals/anr#diagnose) — قراءة ملفات traces.txt وتشخيص تجميد التطبيق.\n\nتمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13.",
        "quick_answer_ar": "لتشخيص ANR تزاحم أقفال الداتابيز، بفتح ملف `/data/anr/traces.txt` وبشوف خيط الـ Main؛ لو لقيته `BLOCKED` أو `WAITING` على `SQLiteConnectionPool`، باخد كود الـ Lock وأدور في الملف على الثريد الخلفي اللي ماسكه. وبنصلح المشكلة بتفعيل نمط الـ WAL في Room، وتقسيم المعاملات الكبيرة لـ Chunks صغيرة بـ yield، ومنع أي كود داتابيز من لمس خيط الواجهة نهائياً.",
        "best_answer_ar": "الـ ANR الناتج عن تزاحم أقفال قاعدة البيانات (Database Lock Contention) بيكون من أصعب المشاكل في التتبع لأنه بيحصل بشكل متقطع ومش منتظم.\n\nخطوتي الأولى للتشخيص هي فحص ملف التتبع الرسمي `/data/anr/traces.txt` اللي بيسجله أندرويد وقت الكراش. بفتح الملف وببص على الـ main thread؛ لو لقيت حالته `BLOCKED` أو `WAITING` على نداءات تابعة لـ `SQLiteConnectionPool.acquireConnection` أو `ReentrantLock`، بحدد الـ Lock Address أو الـ Mutex اللي الخيط مستنيه، وببحث في نفس الملف عن الثريد التاني اللي معاه نفس الـ Lock ده، وغالباً بيكون Background Sync Worker بيسجل بيانات كتيرة.\n\nالسبب الأساسي هو إن قاعدة البيانات شغالة بنمط الـ Rollback Journal القديم، وده بيعمل Exclusive Lock على ملف الداتابيز، فلما خيط الواجهة يطلب قراءة سريعة، بيفضل محبوس ومستني المعاملة الخلفية تخلص لحد ما تفوت 5 ثوانٍ ويحصل ANR.\n\nالحل الهندسي بيعتمد على تلات خطوات: أولاً، بنفعل نمط Write-Ahead Logging (WAL) في Room، وده بيسمح للقراء يقرأوا بالتوازي أثناء كتابة الخلفية بدون أي تعارض. ثانياً، بنقسم المعاملات الضخمة لـ Batches صغيرة لا تتجاوز 100 عنصر ونحط بينهم `yield()` لإتاحة فرصة للقفل إنه يتحرر. وثالثاً، بنمنع منعاً باتاً استدعاء أي كود داتابيز من خيط الواجهة مباشرة.",
        "deep_answer_ar": "على مستوى الـ SQLite Engine ونظام تشغيل لينكس، قفل قاعدة البيانات بيتم عبر POSIX Advisory File Locks. في نمط الـ Rollback Journal التقليدي، المعاملة بتتحرك من SHARED لـ RESERVED ثم PENDING وأخيراً EXCLUSIVE. القفل الـ Exclusive بيحظر تماماً أي عملية قراءة أو كتابة تانية في الملف. لو خيط الـ Main حاول يقرأ عبر `sqlite3_step`، هيفضل محبوس في الـ Native C++ layer.\n\nتفعيل نمط الـ WAL mode بيحل الجزء الأكبر من الأزمة لأنه بيكتب التعديلات في ملف ملحق اسمه `-wal` ويسيب الـ `.db` الأصلي للقراء بدون أقفال حصرية. بس لازم ننتبه إن الـ ANR ممكن يحصل حتى في الـ WAL mode في حالتين: لو خيط الـ Main حاول يكتب وهو فيه كاتب تاني شغال، أو لو كاتب الخلفية ضخم جداً وفجر عملية `checkpoint` متزامنة لقفل كل الفريمات ونقلها للقاعدة الأصلية.\n\nكمان فيه خطر معماري خطير اسمه Priority Inversion؛ لما الكاتب في الخلفية يكون واخد أولوية Thread منخفضة (Background cgroup) وماسك القفل، وخيط الـ Main واخد أعلى أولوية (top-app) ومستني القفل ده. نظام التشغيل تحت الضغط هيدي المعالج لثريدات تانية ويحرم ثريد الخلفية، فالقفل هيفضل محبوس لأكتر من 5 ثوانٍ وينفجر ANR فوري.\n\nعلشان كده في بيئات الإنتاج، بنفعل `setJournalMode(WRITE_AHEAD_LOGGING)` في Room، وبنقسم العمليات لـ Chunks صغيرة عبر `withContext(Dispatchers.IO)`، وبنستدعي `yield()` علشان نسمح لثريد الـ Checkpoint والثريدات التانية تشتغل، وبنراقب الـ ANR Clusters في Google Play Console للتأكد من انعدام التزاحم بنسبة 100%."
    }
}

# =======================================================
# MEM-26: Performance budgets and regression tests
# =======================================================
DATA["MEM-26"] = {
    "concept_en": """Establishing measurable performance budgets and automated regression testing prevents application degradation across rapid continuous integration cycles. A performance budget defines strict, non-negotiable quantitative thresholds across key operational dimensions: Cold Start Time to Initial Display (<1200ms on median hardware), slow rendering frame rate (<2% of frames exceeding 16.6ms), background memory baseline (PSS below allocated tier limits), and downloadable binary size (DEX and APK deltas). Enforcing these budgets requires moving beyond non-deterministic synthetic benchmarks run on emulator pools. Teams implement Jetpack Macrobenchmark executing on dedicated physical device testbeds or Gradle Managed Devices in CI. Tests automate end-to-end critical user journeys using UI Automator, enforce CompilationMode.Partial with Baseline Profiles, and assert against StartupTimingMetric and FrameTimingMetric. Binary deltas are gated via tools like Diffuse, failing pull requests that introduce unauthorized method count or byte expansions.""",
    "walkthrough_en": """Automating startup and frame pacing regression gates with Macrobenchmark:
```kotlin
// In a dedicated macrobenchmark module:
@RunWith(AndroidJUnit4::class)
@LargeTest
class PerformanceRegressionBenchmark {
    @get:Rule
    val benchmarkRule = MacrobenchmarkRule()

    @Test
    fun verifyColdStartupBudget() = benchmarkRule.measureRepeated(
        packageName = "com.example.app",
        metrics = listOf(StartupTimingMetric()),
        compilationMode = CompilationMode.Partial(BaselineProfileMode.Require),
        iterations = 10,
        startupMode = StartupMode.COLD
    ) {
        pressHome()
        startActivityAndWait()
        
        // Assert on median startup duration directly in test runner or CI parser:
        // Startup must remain below 1200ms budget threshold
    }

    @Test
    fun verifyScrollingFramePacingBudget() = benchmarkRule.measureRepeated(
        packageName = "com.example.app",
        metrics = listOf(FrameTimingMetric()),
        compilationMode = CompilationMode.Partial(BaselineProfileMode.Require),
        iterations = 5,
        startupMode = StartupMode.WARM
    ) {
        startActivityAndWait()
        val feed = device.findObject(By.res("com.example.app", "feed_list"))
        feed.setGestureMargin(device.displayWidth / 10)
        feed.fling(Direction.DOWN)
        device.waitForIdle()
    }
}
```""",
    "short_en": """To enforce performance budgets, I establish numeric thresholds for cold start (<1.2s), jank frames (<2%), memory PSS, and APK size. We automate regression tests in CI using Jetpack Macrobenchmark on physical testbeds or Gradle Managed Devices, compare binary deltas with Diffuse, and gate pull requests before merge.""",
    "structured_en": """To begin with, performance budgets define clear numeric thresholds that prevent gradual performance regressions during rapid continuous development.
From an architectural standpoint, our budget establishes explicit quantitative targets: cold startup Time to Initial Display under 1200 milliseconds on median devices, slow rendering frames below two percent, background memory PSS capped at a defined tier, and strict download size limits.
In production scenarios, these budgets are enforced through automated continuous integration gates. Rather than relying on synthetic microbenchmarks or fluctuating cloud emulators, we execute Jetpack Macrobenchmark suites on dedicated physical device testbeds or Gradle Managed Devices. These tests exercise critical user journeys using UI Automator while capturing StartupTimingMetric and FrameTimingMetric alongside Perfetto trace files.
As for boundary management, pull requests are validated through multi-layer gates. Binary size regressions are audited using Diffuse to flag unexpected method count or asset growth. If a PR violates startup latency or frame drop thresholds, the CI pipeline fails automatically, requiring the author to optimize code or justify a budget adjustment before merging.""",
    "deep_senior_en": """At the systems engineering and automation level, building a trustworthy performance regression pipeline requires eliminating measurement noise, environmental flakiness, and thermal throttling. Standard cloud CI runners and generic emulators produce unacceptable variance due to CPU host contention and lack of hardware GPU acceleration. To achieve mathematical determinism, enterprise teams deploy physical device testbeds (such as Pixel devices running custom non-rooted eng or userdebug builds) with CPU clock locking, or leverage Gradle Managed Devices configured with isolated AVD snapshots.
Macrobenchmark enforces release-like fidelity by testing non-debuggable APKs with the profileable manifest flag enabled. It automatically clears operating system compilation caches, pre-warms caches, and averages metrics across multiple iterations (typically 10 to 20 runs) to produce statistically significant median and 95th percentile metrics. If an architectural refactor—such as introducing a new dependency injection graph or migrating a list to Jetpack Compose—causes FrameTimingMetric 95th percentile frame durations to jump from 12ms to 20ms, the pipeline surfaces Perfetto trace links directly in the PR review interface.
Binary budget auditing operates in tandem using tools like Diffuse. Diffuse compares the base branch APK against the PR artifact, calculating precise byte differentials across DEX code, uncompressed assets, and resource tables. PR checks block merges if DEX method count exceeds budget thresholds or if APK download size spikes without prior architecture council sign-off.
Finally, production telemetry closes the feedback loop. We ingest Android Vitals metrics and OpenTelemetry data into Datadog, asserting that real-world 99th percentile startup and slow frame rates remain strictly compliant with the defined engineering budget.""",
    "meta_ar": {
        "id": "MEM-26",
        "questionAr": "كيف تنشئ ميزانيات أداء قابلة للقياس (Performance Budgets) واختبارات لمنع التراجع؟",
        "topicAr": "إدارة الذاكرة والـ ANR وتحسين الأداء",
        "evaluates_ar": "- تحديد أرقام ومؤشرات قياسية صريحة (Cold start < 1.2s, Jank < 2%, APK size).\n- أتمتة اختبارات الـ Macrobenchmark داخل الـ CI على أجهزة حقيقية أو GMD.\n- تطبيق بوابات منع الدمج (Blocking CI Gates) وفحص فروق الباينري بأدوات زي Diffuse.",
        "why_it_matters_ar": "بدون ميزانيات أداء رقمية صارمة ومؤتمتة في الـ CI، يتراجع أداء التطبيق تدريجياً مع كل Pull Request دون أن يلاحظ أحد، حتى يفاجأ الفريق ببطء الإقلاع وسقوط الفريمات وتراجع تقييم التطبيق على متجر جوجل بلاي.",
        "worked_example_ar": "كتابة اختبار Macrobenchmark مؤتمت يختبر ميزانية الـ Startup وسلاسة السكرول:\n```kotlin\n@RunWith(AndroidJUnit4::class)\nclass StartupBenchmark {\n    @get:Rule\n    val rule = MacrobenchmarkRule()\n\n    @Test\n    fun testStartupBudget() = rule.measureRepeated(\n        packageName = \"com.example.app\",\n        metrics = listOf(StartupTimingMetric()),\n        compilationMode = CompilationMode.Partial(BaselineProfileMode.Require),\n        iterations = 10,\n        startupMode = StartupMode.COLD\n    ) {\n        pressHome()\n        startActivityAndWait()\n        // يتم التحقق من أن متوسط الـ StartupTiming أقل من 1200ms في سكريبت الـ CI\n    }\n}\n```",
        "trade_offs_ar": "تشغيل اختبارات Macrobenchmark على أجهزة حقيقية في الـ CI يوفر قياسات دقيقة جداً وموثوقة، ولكنه يزيد من وقت تنفيذ خط الأتمتة (Build Time) ويتطلب بنية تحتية مخصصة للأجهزة، لذا يتم تشغيلها إما مع كل PR للمسارات الحساسة أو كفحص يومي مجدول (Nightly Build).",
        "failure_modes_ar": "تشغيل اختبارات الأداء على محاكيات سحابية رخيصة تشهد تبايناً هائلاً في سرعة المعالج (Flakiness)، مما يجعل الأرقام غير مفيدة. خطأ آخر هو قياس الـ Debug builds بدلاً من الـ Release builds المقفلة، أو عدم تثبيت تردد المعالج مما يسبب Thermal Throttling يشوه النتائج.",
        "production_perspective_ar": "في الشركات الكبرى، نضع بوابات صارمة تمنع دمج الـ PR إذا زاد حجم الـ APK بأكثر من 100 كيلوبايت دون تبرير عبر Diffuse، أو إذا تراجع زمن الـ Cold Start عن 1.2 ثانية. ونربط ذلك بتقارير Google Play Vitals في الإنتاج لضمان بقاء التطبيق ضمن أفضل 1% من التطبيقات في فئته.",
        "how_to_answer_ar": "- **تحديد الميزانية:** ابدأ بأرقام محددة (Cold start < 1.2s، فريمات ساقطة < 2%، حجم APK محدد).\n- **أداة الاختبار:** اشرح استخدام Jetpack Macrobenchmark و UI Automator لقياس رحلات المستخدم.\n- **بيئة الاختبار:** أكد على استخدام أجهزة حقيقية أو Gradle Managed Devices وتجنب المحاكيات المتقلبة.\n- **بوابات الأتمتة:** وضح فحص فروق الـ DEX والـ APK بأداة Diffuse وحظر الدمج التلقائي عند التراجع.\n- **التكامل في الإنتاج:** بيّن مراقبة مؤشرات Android Vitals ومطابقتها للميزانية المقررة.",
        "talking_points_ar": "ناقش الفرق بين Microbenchmark و Macrobenchmark، ومشاكل الـ Thermal Throttling وكيفية قفل الـ CPU Clocks في مختبرات الفحص، وتتبع مؤشرات الـ P90 والـ P95 في Perfetto.",
        "follow_ups_ar": "- **المحاور:** \"لماذا نرفض تشغيل اختبارات أداء الواجهة والإقلاع على الـ Debug build؟\"\n  **المرشح:** \"لأن الـ Debug build يحتوي على كود فحص إضافي وغير محسن بـ R8، وتكون سرعة الـ ART فيه بنمط الـ JIT البطيء، ولا تتوفر فيه الـ Baseline Profiles، فتكون أرقام الأداء مشوهة تماماً ومتباعدة عن الواقع الحقيقي للمستخدمين.\"\n\n- **المحاور:** \"كيف تمنع تقلب نتائج الأداء (Flakiness) في خط الـ CI؟\"\n  **المرشح:** \"باستخدام أجهزة حقيقية مخصصة أو Gradle Managed Devices مع صور نظام معزولة، وقفل ترددات المعالج (CPU Clock Locking) لمنع الـ Thermal Throttling، وتكرار الاختبار لـ 10 إلى 20 دورة وحساب الوسيط (Median) والـ 95th Percentile بدلاً من الاعتماد على تشغيلة واحدة.\"",
        "self_check_ar": "هل حددت أرقام الميزانية بوضوح؟ هل شرحت دور Macrobenchmark؟ وهل وضحت فحص الباينري بـ Diffuse وبوابات الـ CI الصارمة؟",
        "references_ar": "- [Define performance budgets](https://web.dev/performance-budgets-101/) — المفاهيم الهندسية لميزانيات الأداء.\n- [Macrobenchmark overview](https://developer.android.com/topic/performance/benchmarking/macrobenchmark-overview) — أتمتة اختبارات الأداء في أندرويد.\n\nتمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13.",
        "quick_answer_ar": "ببني ميزانية الأداء بوضع أرقام صريحة غير قابلة للتفاوض: الإقلاع البارد أقل من 1.2 ثانية، والفريمات البطيئة أقل من 2%، وحد أقصى لحجم الـ APK. وبنأتمت اختبارات الـ Macrobenchmark في الـ CI على أجهزة حقيقية أو GMD لاختبار رحلات المستخدم الحقيقية، وبنفحص فروق الباينري بـ Diffuse ونمنع دمج أي PR يكسر الميزانية.",
        "best_answer_ar": "ميزانية الأداء (Performance Budget) هي العقد الهندسي اللي بيمنع تدهور جودة التطبيق مع سرعة وتتابع الـ Pull Requests.\n\nبنبدأ بتحديد أهداف رقمية واضحة وقابلة للقياس: زمن الـ Cold Start لا يتعدى 1.2 ثانية على الأجهزة المتوسطة (TTID)، ومعدل سقوط الفريمات (Jank Rate) أقل من 2%، واستهلاك الذاكرة في الخلفية محكوم بحد أقصى، وميزانية محددة لحجم الـ APK.\n\nوعلشان نضمن عدم التراجع، بنأتمت الاختبارات داخل الـ CI pipeline باستخدام مكتبة Jetpack Macrobenchmark على أجهزة حقيقية مخصصة أو Gradle Managed Devices؛ بنحاكي رحلات مستخدم كاملة بـ UI Automator ونقيس مؤشرات `StartupTimingMetric` و `FrameTimingMetric`.\n\nوبنحط بوابات فحص صارمة (Blocking Gates)؛ بنستخدم أداة Diffuse لفحص الفروق في ملفات الـ DEX والـ Resources مع كل PR، ولو أي كود سبب زيادة غير مبررة في حجم الباينري أو تراجع في أزمنة الإطارات، الاختبار بيفشل تلقائياً ويمنع الدمج لحد ما المطور يحسن الكود أو يبرر التغيير أمام اللجنة المعمارية.",
        "deep_answer_ar": "على مستوى البنية التحتية لهندسة الأداء، التحدي الأكبر في الـ CI هو التغلب على الـ Measurement Noise وتذبذب النتائج الناتج عن الـ Thermal Throttling وتشغيل المحاكيات السحابية المشتركة. علشان نحقق نتائج حتمية بدقة رياضية، بنشغل الاختبارات إما على مزارع أجهزة حقيقية بنظام قفل ترددات المعالج (CPU Clocks Locking)، أو بنستخدم Gradle Managed Devices مضبوطة على لقطات AVD معزولة ونظيفة.\n\nاختبارات الـ Macrobenchmark بتشتغل حصراً على Release builds مفعل فيها الـ profileable tag في الـ Manifest، وبتنظف كاش الـ Compilation قبل كل لفة، وبتكرر القياس من 10 لـ 20 مرة علشان تطلع أرقام إحصائية موثوقة للـ Median والـ 95th Percentile. فلو حصل Re-composition غير مقصود في Jetpack Compose رفع الـ 95th percentile من 10ms لـ 18ms، السكريبت بيرفض الـ PR فوراً ويرفق رابط لملف الـ Perfetto Trace المجمع أثناء الاختبار.\n\nوبالتوازي، أداة Diffuse بتعمل تحليل مجهري لحجم الباينري؛ بتقارن الـ APK مع الـ Main branch وتوضح بالبايت الزيادة في كود الـ DEX وعدد الدوال (Method Count) ومساحة الصور والملفات المضغوطة.\n\nوأخيراً بنقفل الدائرة بمراقبة الـ Telemetry في الإنتاج عبر Google Play Vitals API و Datadog، ونتأكد إن الأرقام الواقعية لمستخدمي التطبيق مطابقة تماماً للميزانية الهندسية اللي بنفحصها في الـ CI."
    }
}

def run():
    print(f"Elevating {len(DATA)} remaining MEM questions: {sorted(DATA.keys())}")
    
    # 1. Update canonical markdown files
    for qid in sorted(DATA.keys()):
        data = DATA[qid]
        ee.update_canonical_question(
            qid=qid,
            concept_en=data["concept_en"],
            walkthrough_en=data["walkthrough_en"],
            structured_en=data["structured_en"],
            deep_senior_en=data["deep_senior_en"],
            short_en=data["short_en"],
        )
        print(f"Updated canonical question {qid}")

    # 2. Save Arabic metadata dictionary
    meta_dict = {qid: DATA[qid]["meta_ar"] for qid in sorted(DATA.keys())}
    meta_file = SCRIPT_DIR / "data" / "metadata_mem_21_26.json"
    meta_file.write_text(json.dumps(meta_dict, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Saved Arabic metadata to {meta_file}")

    # 3. Merge all metadata
    ee.merge_all_metadata()

    # 4. Validate each question
    all_passed = True
    for qid in sorted(DATA.keys()):
        errs = ee.validate_question(qid)
        if errs:
            all_passed = False
            print(f"❌ {qid} validation failed with {len(errs)} errors:")
            for e in errs:
                print("  -", e)
        else:
            print(f"✅ {qid} passed validation with 0 errors!")

    if not all_passed:
        print("Some questions failed validation!", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"All {len(DATA)} MEM questions successfully elevated and passed validation!")

if __name__ == "__main__":
    run()
