#!/usr/bin/env python3
"""Generator for MEM-07 through MEM-12 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "mem.json"

MEM_07_12 = [
    {
        "id": "MEM-07",
        "arabic_explanation": (
            "الفرق بين النوعين الأوليين `int` و `Integer` والتعامل بين Kotlin و Java على مستوى الذاكرة والأداء:\n\n"
            "1. كيف يترجم كود Kotlin إلى بايت كود JVM؟\n"
            "   - في Kotlin، النوع `Int` غير القابل للعدم (`Int`) يترجم دائماً في البايت كود إلى `int` بدائي (primitive) على الـ JVM، ولا يستهلك سوى 4 بايت مباشرة في الـ Stack أو كـ field داخل الكائن.\n"
            "   - أما إذا كان نوعه يقبل العدم `Int?`، فيجب على المترجم تمثيل القيمة كـ Reference Object وهو `java.lang.Integer` (Boxed)، لأنه لا يمكن وضع `null` داخل `int` بدائي.\n\n"
            "2. كلفة الـ Object Overhead في `Integer`:\n"
            "   - الـ `int` البدائي: 4 بايت فقط.\n"
            "   - الـ `Integer` المُغلّف (Boxed Object): يحتوي على Object Header (عادة 12 بايت) + الـ value (4 بايت) + Padding للمحاذاة على 8 بايت = 16 إلى 24 بايت على الـ Heap، بالإضافة إلى 4-8 بايت لعنوان الإشارة (Pointer Reference) إليه!\n"
            "   - هذا يعني زيادة في الذاكرة بنسبة 400% إلى 600% لكل رقم، بالإضافة إلى Memory Churn وضغط على الـ Garbage Collector.\n\n"
            "3. الـ Autoboxing في الحلقات والمجموعات (Collections):\n"
            "   - استخدام `List<Int>` في Kotlin يترجم إلى `java.util.List<Integer>`، مما يجبر كل عنصر على أن يكون مغلفاً في كائن `Integer` على الـ Heap.\n"
            "   - في المعالجات الحسابية الثقيلة أو قوائم الإحداثيات والرسوم، يُفضل دائماً استخدام المصفوفات البدائية: `IntArray` بدلاً من `Array<Int>` أو `List<Int>`."
        ),
        "practical_walkthrough": (
            "مقارنة عملية تظهر تأثير التغليف (Boxing) على الذاكرة وسرعة المعالجة:\n"
            "```kotlin\n"
            "// ❌ كود سيء: يسبب Autoboxing مستمر لكل عنصر في القائمة، مهدراً الذاكرة ومسبباً GC Churn:\n"
            "fun calculateSum(numbers: List<Int>): Long { // List<Int> تخزن كائنات java.lang.Integer\n"
            "    var total: Long = 0L\n"
            "    for (num in numbers) { // Unboxing من Integer إلى int في كل دورة\n"
            "        total += num\n"
            "    }\n"
            "    return total\n"
            "}\n"
            "\n"
            "// ✅ كود احترافي: استخدام Primitive Array بدون أي Heap Allocation لكل رقم:\n"
            "fun calculateSumFast(numbers: IntArray): Long { // يترجم مباشرة إلى int[] في الـ JVM\n"
            "    var total: Long = 0L\n"
            "    for (num in numbers) { // قراءة مباشرة من الذاكرة المتتالية بدون فك تغليف\n"
            "        total += num\n"
            "    }\n"
            "    return total\n"
            "}\n"
            "```"
        ),
        "quick_answer": "In Kotlin, a non-nullable `Int` compiles to JVM primitive `int` (4 bytes on the stack), whereas nullable `Int?` or generic collections like `List<Int>` compile to boxed `java.lang.Integer` (16-24 bytes on the heap). Boxed integers multiply memory footprint and cause GC churn, so high-performance paths should use `IntArray` or primitive-specialized collections.",
        "best_answer": (
            "Under the hood, Kotlin does not expose primitives directly in syntax, but its compiler maps them intelligently based on nullability and generics.\n\n"
            "A standard non-nullable `Int` compiles directly to a primitive `int` on JVM bytecode, occupying just 4 bytes of contiguous memory with zero object overhead. "
            "However, when an `Int` is marked nullable (`Int?`) or used as a type argument in standard generics like `List<Int>`, the runtime must represent it as a boxed reference: `java.lang.Integer`.\n\n"
            "The memory impact is drastic: while a primitive `int` requires 4 bytes, a `java.lang.Integer` requires a 12-byte object header, 4 bytes of value payload, and 8-byte alignment padding, consuming 16 to 24 bytes on the heap, plus 4 to 8 bytes for the reference pointer. "
            "In high-frequency loops or graphics/sensor processing, this creates massive memory bloat and garbage collection churn. "
            "In production, we mitigate this by using primitive arrays like `IntArray` instead of `Array<Int>`, or specialized Android collections like `SparseIntArray` to avoid boxing entirely."
        ),
        "deep_answer": (
            "Java interoperability introduces subtle boxing pitfalls. If a Kotlin function expects `Int` and calls a Java method returning `Integer`, or vice-versa with platform types (`Integer!`), implicit boxing and unboxing occur at bytecode boundaries (`Integer.valueOf()` and `intValue()`). "
            "Furthermore, unboxing a null `Integer` returned from Java produces a fatal `NullPointerException` at runtime in Kotlin.\n\n"
            "Another critical JVM optimization to understand is the **Integer Cache** (`java.lang.IntegerCache`), which caches boxed values between -128 and 127 by default. "
            "Comparing boxed integers inside this range with reference equality (`===`) might deceptively evaluate to `true`, but comparing values outside this range fails because distinct instances are allocated on the heap.\n\n"
            "When profiling memory in Android Studio, collections of boxed primitives appear as massive retained sizes dominated by millions of tiny `java.lang.Integer` instances. "
            "Replacing `Map<Int, CustomObject>` with Android's `SparseArray<CustomObject>` eliminates the `Integer` key boxing completely, saving megabytes of heap in large list adapters or cache layers."
        ),
        "follow_ups": [
            {
                "question": "What happens if a Java method returns `Integer` and is assigned to a non-nullable Kotlin `Int`?",
                "answer": "The compiler accepts it as a platform type `Int!`. If the Java method returns null, unboxing it into Kotlin's primitive `int` invokes `intValue()`, which instantly throws a `NullPointerException`. We always annotate Java boundaries with `@NonNull` or type it explicitly as `Int?` in Kotlin."
            },
            {
                "question": "Why does `IntArray` not box elements while `Array<Int>` does?",
                "answer": "`IntArray` compiles directly to JVM bytecode primitive array `int[]`, storing contiguous 4-byte values. In contrast, `Array<Int>` compiles to `Integer[]`, which is an array of object pointers pointing to separate `Integer` instances on the heap."
            }
        ]
    },
    {
        "id": "MEM-08",
        "arabic_explanation": (
            "تسريب الذاكرة الناتج عن احتفاظ كائن أحادي (Singleton) بسياق النشاط (Activity Context):\n\n"
            "1. طبيعة دورة حياة الـ Singleton مقابل الـ Activity:\n"
            "   - الـ Singleton هو كائن يعيش طوال فترة تشغيل التطبيق (Process Lifetime) لأنه ممسوك بـ Static Reference في كلاس لودر النظام (ClassLoader).\n"
            "   - الـ Activity هو كائن واجهة مستخدم دورة حياته مؤقتة؛ يُدمر ويُعاد إنشاؤه عند تغيير اتجاه الشاشة (Configuration Change مثل دوران الشاشة) أو عند ضغط زر الرجوع (Back navigation).\n\n"
            "2. كيف يحدث التسريب الفعلي (The Retained Root)?\n"
            "   - إذا قمت بتمرير `activityContext` إلى Singleton واحتفظ به في متغير (Field):\n"
            "   - عند تدمير النشاط (`onDestroy()`)، يحاول مجمع النفايات (GC) تنظيف النشاط.\n"
            "   - لكن الـ GC يجد أن الـ Activity لا يزال متصلاً بـ GC Root نشط وهو (Static Singleton -> Activity Reference).\n"
            "   - نتيجة لذلك، تظل الـ Activity محبوسة في الـ Heap، وممسوك معها شجرة الواجهة بالكامل (View Hierarchy)، وكل الصور (Bitmaps)، والمكونات التابعة، مما يستهلك عشرات الميجابايتات في كل دورة شاشة!\n\n"
            "3. الحل الهندسي السليم:\n"
            "   - إذا كان الـ Singleton بحاجة إلى Context لفتح ملفات أو قراءة موارد النظام، يجب دائماً استخدام `context.applicationContext`.\n"
            "   - الـ Application Context دورة حياته مطابقة تماماً لدورة حياة العملية (Process)، فلا يمكن أن يسرب Activity أبداً."
        ),
        "practical_walkthrough": (
            "مثال عملي يوضح التسريب وكيفية إصلاحه:\n"
            "```kotlin\n"
            "// ❌ كائن أحادي كارثي: يسرب Activity Context وكل ما ترتبط به:\n"
            "object LocationTracker {\n"
            "    private var context: Context? = null // تسريب صريح!\n"
            "\n"
            "    fun init(activityContext: Context) {\n"
            "        this.context = activityContext // النشاط لن يتحرر أبداً من الذاكرة عند التدوير!\n"
            "    }\n"
            "}\n"
            "\n"
            "// ✅ الكود السليم هندسياً: الاحتفاظ بـ Application Context فقط:\n"
            "class LocationTracker private constructor(private val appContext: Context) {\n"
            "    companion object {\n"
            "        @Volatile\n"
            "        private var INSTANCE: LocationTracker? = null\n"
            "\n"
            "        fun getInstance(context: Context): LocationTracker {\n"
            "            return INSTANCE ?: synchronized(this) {\n"
            "                INSTANCE ?: LocationTracker(context.applicationContext).also {\n"
            "                    INSTANCE = it\n"
            "                }\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "A Singleton lives for the entire application process lifetime via a static reference. If it retains an Activity Context, the Garbage Collector cannot reclaim the Activity after `onDestroy()`, retaining its entire View hierarchy and Bitmaps on the heap. Singletons should only reference `applicationContext` or avoid holding Context entirely.",
        "best_answer": (
            "A Singleton has a process-level lifecycle because it is anchored to a static reference in memory. An Activity, on the other hand, is transient and frequently destroyed and recreated, such as during configuration changes or screen navigation.\n\n"
            "When a Singleton holds a strong reference to an Activity Context, that Activity cannot be collected by the Garbage Collector after `onDestroy()` is called. "
            "Because an Activity holds references to its entire `Window`, `DecorView`, View hierarchy, resource managers, and loaded Bitmaps, this single reference retains megabytes of dead memory on the heap. "
            "If the user rotates the device ten times, ten dead Activity instances remain pinned in memory, quickly leading to an `OutOfMemoryError`.\n\n"
            "The standard production fix is ensuring Singletons only ever take `context.applicationContext`. The Application context shares the process lifecycle, making it leak-free for long-lived components. "
            "Alternatively, we use dependency injection frameworks like Hilt with `@Singleton` scoped classes that inject `@ApplicationContext` directly."
        ),
        "deep_answer": (
            "It is also critical to understand when `applicationContext` is *not* a drop-in replacement. "
            "The Application context does not have a themed UI scope or a Window token. "
            "If you attempt to inflate themed views or display a Dialog (`AlertDialog.Builder(applicationContext)`), the app will crash with an `IllegalStateException` or render without the appropriate theme attributes.\n\n"
            "When analyzing a memory dump in LeakCanary or Memory Profiler, this pattern manifests as a clear shortest path to GC Root: `com.example.Singleton.context` -> `MainActivity`. "
            "The retained size will equal the entire Activity graph.\n\n"
            "If a component truly needs short-term access to an Activity (for example, a global UI navigator or lifecycle observer), it should either accept the Activity as a method parameter rather than storing it as a property, or wrap it in a `WeakReference<Activity>` and verify nullability before invoking UI operations."
        ),
        "follow_ups": [
            {
                "question": "Can using `WeakReference<Activity>` in a Singleton completely eliminate the leak risk?",
                "answer": "Yes, `WeakReference` allows the GC to reclaim the Activity during collection. However, it requires null-checking on every access and may become null unexpectedly during orientation change. The cleaner pattern is passing the Activity ephemerally as a method argument or using an Activity-scoped dependency."
            },
            {
                "question": "Can inflating a View with `applicationContext` cause issues even if it doesn't crash?",
                "answer": "Yes. `applicationContext` lacks Activity theme overlays and configuration metrics (like multi-window bounds or system bar insets), which causes UI components to render with wrong typography, missing colors, or incorrect dimensions."
            }
        ]
    },
    {
        "id": "MEM-09",
        "arabic_explanation": (
            "هل يمكن للـ ViewModel أو الـ Coroutine تسريب الذاكرة؟ وكيف يحدث ذلك؟\n\n"
            "1. تسريب الذاكرة عبر الـ ViewModel:\n"
            "   - الـ `ViewModel` مصمم ليعيش أطول من الـ Activity الفردية؛ فهو يبقى حياً أثناء تدوير الشاشة (Configuration Change) ويتم التخلص منه فقط عند استدعاء `onCleared()`.\n"
            "   - إذا قمت بتخزين مرجع مباشر لـ `Activity` أو `View` أو `Fragment` داخل الـ ViewModel، فإن الـ ViewModel سيمنع الـ GC من تحرير الـ Activity القديمة أثناء التدوير، مما يسبب تسريباً صريحاً!\n\n"
            "2. تسريب الذاكرة عبر الـ Coroutines:\n"
            "   - الـ Coroutine التي تعمل في نطاق غير مرتبط بدورة الحياة (مثل `GlobalScope` أو نطاق لا يتم إلغاؤه) تظل نشطة في الخلفية.\n"
            "   - إذا كانت هذه الـ Coroutine تلتقط (captures) مرجعاً ضمنياً لـ Activity أو كائن واجهة داخل الـ lambda الخاص بها، أو إذا كانت معلقة (suspended) في انتظار استجابة شبكة بطيئة أو Flow غير منتهٍ، فإن الـ Continuation الخاص بها سيحتفظ بمرجع النشاط حياً على الـ Heap إلى أجل غير مسمى.\n\n"
            "3. الحلول القياسية في Production:\n"
            "   - في الـ ViewModel: لا تخزن أي مرجع للـ View إطلاقاً؛ استخدم StateFlow و SharedFlow لتمرير البيانات للأعلى، واجعل الـ View هو الذي يراقب.\n"
            "   - إذا كنت بحاجة لـ Context في الـ ViewModel، استخدم `AndroidViewModel(application)` للوصول لـ Application Context فقط.\n"
            "   - في الـ Coroutines: اربط كل عملية بـ `viewModelScope` أو `lifecycleScope`. هذه النطاقات تلغي جميع المهام الفرعية تلقائياً عند انتهاء دورة الحياة."
        ),
        "practical_walkthrough": (
            "أمثلة توضح التسريب في ViewModel و Coroutine وحلولها:\n"
            "```kotlin\n"
            "// ❌ كود خاطئ: تسريب Activity عبر ViewModel و Coroutine طويلة الأمد:\n"
            "class BadViewModel : ViewModel() {\n"
            "    var listener: ((String) -> Unit)? = null // إذا كان الـ listener لامبدا من Activity يمسك this!\n"
            "\n"
            "    fun startListening() {\n"
            "        // GlobalScope لا يتم إلغاؤه مع ViewModel، ويمسك reference للـ ViewModel والـ listener:\n"
            "        GlobalScope.launch {\n"
            "            val data = repository.streamData()\n"
            "            listener?.invoke(data)\n"
            "        }\n"
            "    }\n"
            "}\n"
            "\n"
            "// ✅ كود سليم هندسياً: مبني على StateFlow و viewModelScope:\n"
            "class GoodViewModel(private val repository: DataRepository) : ViewModel() {\n"
            "    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)\n"
            "    val uiState: StateFlow<UiState> = _uiState.asStateFlow()\n"
            "\n"
            "    fun loadData() {\n"
            "        // viewModelScope يلغي الكوروتين تلقائياً داخل onCleared():\n"
            "        viewModelScope.launch {\n"
            "            repository.streamData()\n"
            "                .catch { emit(UiState.Error(it)) }\n"
            "                .collect { _uiState.value = UiState.Success(it) }\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Yes. A ViewModel leaks memory if it retains references to Views, Activities, or Fragments across configuration changes. A coroutine leaks memory if launched in an unbound scope like `GlobalScope` or left suspended while capturing a transient Context or View reference. Using `viewModelScope` and observing unidirectional data flows via `StateFlow` prevents these leaks.",
        "best_answer": (
            "Yes, both ViewModels and coroutines can leak memory if lifecycle boundaries are violated.\n\n"
            "A `ViewModel` is scoped to survive configuration changes. If it stores a reference to an Activity, Fragment, View, or an Activity-bound callback, that transient UI component remains pinned in the heap when the user rotates the device or navigates away. "
            "To prevent this, ViewModels must strictly expose state unidirectionally via `StateFlow` or `LiveData` and never hold UI references. If a Context is mandatory, `AndroidViewModel` should be used to restrict access to `applicationContext`.\n\n"
            "Similarly, a coroutine leaks memory when launched in an unmanaged scope—such as `GlobalScope` or an uncancelled custom `CoroutineScope`. "
            "If that coroutine suspends indefinitely (such as awaiting a long network request or observing a cold flow) and captures a reference to a View or Activity within its lambda closure, the underlying `Continuation` object acts as an active GC Root pinning the entire UI graph in memory. "
            "Using `viewModelScope` and `lifecycleScope` ensures automatic cooperative cancellation when the host lifecycle terminates."
        ),
        "deep_answer": (
            "Under the hood, Kotlin coroutines compile suspension points into state machines where local variables and captured closures are stored inside a heap-allocated `Continuation` object. "
            "If a coroutine is suspended waiting on a non-cancelling callback or an uncompleted `CompletableDeferred`, ART's GC traverses: Active Thread -> Event Loop / CoroutineDispatcher -> Continuation -> Captured Outer Scope (Activity/View). "
            "This creates a persistent leak even if the coroutine isn't actively doing CPU work.\n\n"
            "Another subtle leak occurs with `suspendCancellableCoroutine` if developers forget to install `invokeOnCancellation { ... }` when wrapping legacy asynchronous SDKs. "
            "If the coroutine scope cancels, but the underlying third-party listener remains registered, the callback retains the resumed continuation indefinitely.\n\n"
            "In production testing, we verify coroutine cleanup by ensuring unit tests run with `runTest` and that `StandardTestDispatcher` detects uncompleted child jobs, and we use LeakCanary to detect stranded `DispatchedContinuation` instances."
        ),
        "follow_ups": [
            {
                "question": "Can `repeatOnLifecycle` leak if called from `lifecycleScope` incorrectly?",
                "answer": "No, `repeatOnLifecycle` cancels its internal coroutine block automatically whenever the lifecycle falls below the specified state (like `STARTED`), stopping collection and dropping active emission references."
            },
            {
                "question": "What is the consequence of passing an Activity Context into `AndroidViewModel` constructor via casting?",
                "answer": "It leaks the Activity immediately across configuration changes because `ViewModelStore` retains the `AndroidViewModel` instance while the Activity is destroyed and recreated."
            }
        ]
    },
    {
        "id": "MEM-10",
        "arabic_explanation": (
            "تعريف ظاهرة ANR (Application Not Responding) وأسبابها الجذرية وكيفية معالجتها:\n\n"
            "1. ما هو الـ ANR؟\n"
            "   - الـ ANR هو تنبيه يعرضه نظام تشغيل Android للمستخدم (مع خيار إغلاق التطبيق بالقوة Force Close أو الانتظار Wait) عندما يفشل التطبيق في الاستجابة لمدخلات المستخدم خلال مهلة زمنية محددة.\n"
            "   - المهل الزمنية الشائعة:\n"
            "     * **Input dispatching timeout**: عدم الاستجابة للمس الشاشة أو ضغط الأزرار خلال **5 ثوانٍ**.\n"
            "     * **BroadcastReceiver**: عدم إنهاء دالة `onReceive()` خلال **10 إلى 60 ثانية** (حسب Foreground/Background).\n"
            "     * **Service execution**: استغراق الـ Service أكثر من **20 ثانية** (Foreground) أو **200 ثانية** (Background) في معالجة أمر.\n\n"
            "2. الأسباب الشائعة للـ ANR:\n"
            "   - **I/O blocking on Main Thread**: قراءة أو كتابة ملفات، استدعاء قاعدة بيانات Room، أو قراءة SharedPreferences المتزامنة على الـ Main Thread.\n"
            "   - **Network calls on Main Thread**: محاولة الاتصال بالإنترنت مباشرة (يسبب `NetworkOnMainThreadException` غالباً، ولكن أحياناً عبر مكتبات C++).\n"
            "   - **Lock Contention (Deadlock/LiveLock)**: الـ Main Thread ينتظر قفل (Mutex/synchronized) ممسوكاً بواسطة Background Thread يقوم بعملية طويلة.\n"
            "   - **Heavy CPU Calculations**: تشفير، ضغط صور، أو معالجة JSON ضخمة على الـ Main Thread.\n\n"
            "3. كيف نحقق في الـ ANR؟\n"
            "   - فحص ملف **traces.txt** المأخوذ من مسار `/data/anr/traces.txt` عبر adb أو فحص تقارير Android Vitals و Firebase Crashlytics.\n"
            "   - الملف يسجل Stack Trace لكل الـ Threads في اللحظة التي حدث فيها الـ ANR بدقة."
        ),
        "practical_walkthrough": (
            "سيناريو عملي لتجنب حظر الـ Main Thread ومنع الـ ANR:\n"
            "```kotlin\n"
            "// ❌ كود كارثي: تنفيذ عمليات ديسك وتشفير على الـ Main Thread يسبب ANR فوراً:\n"
            "class BadSettingsActivity : AppCompatActivity() {\n"
            "    override fun onCreate(savedInstanceState: Bundle?) {\n"
            "        super.onCreate(savedInstanceState)\n"
            "        // قراءة متزامنة لملف كبير أو SharedPreferences على الـ Main Thread:\n"
            "        val heavyConfig = File(filesDir, \"config.json\").readText() // IO Blocking!\n"
            "        applyConfig(heavyConfig)\n"
            "    }\n"
            "}\n"
            "\n"
            "// ✅ كود احترافي: نقل العمليات الثقيلة إلى Dispatchers.IO عبر Coroutines:\n"
            "class SafeSettingsActivity : AppCompatActivity() {\n"
            "    override fun onCreate(savedInstanceState: Bundle?) {\n"
            "        super.onCreate(savedInstanceState)\n"
            "        lifecycleScope.launch {\n"
            "            val heavyConfig = withContext(Dispatchers.IO) {\n"
            "                File(filesDir, \"config.json\").readText() // يتم في Background Thread بأمان\n"
            "            }\n"
            "            applyConfig(heavyConfig) // العودة للـ Main Thread لتحديث الـ UI\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "An ANR (Application Not Responding) occurs when the main thread is blocked and cannot respond to user input within 5 seconds, finish a BroadcastReceiver within 10-60 seconds, or execute a Service within 20 seconds. Common causes include disk I/O, heavy computation, lock contention, and IPC on the UI thread.",
        "best_answer": (
            "An ANR happens when the application's main looper is frozen and the system Activity Manager detects that the app is unresponsive.\n\n"
            "The primary triggers and system timeout thresholds are:\n"
            "1. **Input Events**: Failing to process a touch, key, or motion event within **5 seconds**.\n"
            "2. **BroadcastReceivers**: Failing to complete `onReceive()` within **10 seconds** for foreground broadcasts or 60 seconds for background.\n"
            "3. **Services**: Failing to execute lifecycle callbacks within **20 seconds** (foreground) or 200 seconds (background).\n\n"
            "The root cause is almost always offloading inappropriate work to the main thread: performing synchronous disk reads/writes (like Room database calls or raw file parsing), parsing large JSON payloads, running cryptographic hashing, or suffering from **lock contention** where the UI thread blocks on a `synchronized` monitor or mutex held by a busy background worker.\n\n"
            "In production, we maintain strict ANR budgets by enforcing `StrictMode` in debug builds to catch disk/network violations on the main thread, routing I/O to `Dispatchers.IO`, and diagnosing production ANRs via Android Vitals and system traces (`/data/anr/traces.txt`)."
        ),
        "deep_answer": (
            "Diagnosing an ANR requires dissecting the system trace report. When an ANR occurs, the Android framework sends `SIGQUIT` to the process, generating a dump in `/data/anr/traces.txt`. "
            "When analyzing this dump, we inspect the `\"main\"` thread state: is it `RUNNABLE` (indicating an infinite loop or heavy CPU computation), `BLOCKED` (waiting on a lock held by another thread), or `TIMED_WAIT` / `WAITING` (waiting for a condition variable or synchronous IPC)?\n\n"
            "A frequent hidden cause of ANRs in enterprise apps is **Binder transaction saturation**. "
            "Calling synchronous system services or IPC methods (like `PackageManager`, `TelephonyManager`, or `AccountManager`) on the main thread can stall if the remote system server is under heavy load, blocking the main thread indefinitely.\n\n"
            "To capture ANRs before users experience them in production, we integrate ANR-WatchDog or Bugsnag/Sentry ANR detectors, which post a heartbeat runnable to the main handler every 2 seconds; if the runnable doesn't execute within 5 seconds, they capture thread stacks and upload a detailed snapshot."
        ),
        "follow_ups": [
            {
                "question": "What is lock contention, and how does it cause an ANR?",
                "answer": "Lock contention happens when the main thread tries to enter a synchronized block or acquire a mutex that is currently locked by a background thread doing heavy I/O or computation. The main thread is forced into a BLOCKED state until the background worker releases the lock."
            },
            {
                "question": "How does `goAsync()` in a BroadcastReceiver help avoid ANRs?",
                "answer": "`goAsync()` flags to the system that the receiver will finish its work asynchronously on a background dispatcher, returning immediately from `onReceive()` while retaining a `PendingResult` to call `finish()` later, avoiding the main thread timeout."
            }
        ]
    },
    {
        "id": "MEM-11",
        "arabic_explanation": (
            "لماذا يجب تحرير مراجع `ViewBinding` في الـ Fragment بالتزامن مع دورة حياة الـ View (`onDestroyView`)؟\n\n"
            "1. اختلاف دورة حياة الـ Fragment عن دورة حياة الـ View الخاص بها:\n"
            "   - الـ Fragment يمتلك **دورتي حياة منفصلتين**: دورة حياة الـ Fragment نفسه (`onCreate` إلى `onDestroy`)، ودورة حياة الـ View التابع له (`onCreateView` إلى `onDestroyView`).\n"
            "   - عندما ينتقل الـ Fragment إلى الـ BackStack (عند عمل `fragmentTransaction.replace().addToBackStack()`)، يتم تدمير الـ View واستدعاء `onDestroyView()` لتوفير الذاكرة، بينما **يبقى كائن الـ Fragment نفسه حياً** في الـ BackStack!\n\n"
            "2. أثر الاحتفاظ بمرجع الـ ViewBinding:\n"
            "   - كائن الـ ViewBinding يحتفظ بمرجع مباشر لـ `root` View ولكل العناصر التابعة (TextViews, ImageViews, RecyclerViews).\n"
            "   - إذا كان الـ Binding محفوظاً كمتغير غير قابل للعدم في الـ Fragment ولم يتم تصفيره (`binding = null`) في `onDestroyView()`:\n"
            "   - يظل كائن الـ Binding ومعه شجرة الـ Views كاملة ممسوكاً في الذاكرة طوال فترة بقاء الـ Fragment في الـ BackStack، مسبباً تسريباً ضخماً للـ Views!\n\n"
            "3. النمط القياسي للحل:\n"
            "   - استخدام Backing Property: `private var _binding: FragmentExampleBinding? = null` مع `private val binding get() = _binding!!`.\n"
            "   - تصفير `_binding = null` صراحة داخل `onDestroyView()`."
        ),
        "practical_walkthrough": (
            "النمط الموصى به لتفادي تسريب الـ ViewBinding في الـ Fragments:\n"
            "```kotlin\n"
            "// ❌ كود خاطئ: يسرب الـ View Hierarchy عندما يذهب الـ Fragment إلى الـ BackStack:\n"
            "class LeakyFragment : Fragment(R.layout.fragment_detail) {\n"
            "    private lateinit var binding: FragmentDetailBinding // لن يتم تصفيرها في onDestroyView!\n"
            "\n"
            "    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {\n"
            "        super.onViewCreated(view, savedInstanceState)\n"
            "        binding = FragmentDetailBinding.bind(view)\n"
            "    }\n"
            "}\n"
            "\n"
            "// ✅ كود قياسي وآمن هندسياً: تصفير المرجع صراحة في onDestroyView:\n"
            "class SafeFragment : Fragment(R.layout.fragment_detail) {\n"
            "    private var _binding: FragmentDetailBinding? = null\n"
            "    private val binding get() = _binding!! // صالح للاستخدام فقط بين onCreateView و onDestroyView\n"
            "\n"
            "    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {\n"
            "        super.onViewCreated(view, savedInstanceState)\n"
            "        _binding = FragmentDetailBinding.bind(view)\n"
            "    }\n"
            "\n"
            "    override fun onDestroyView() {\n"
            "        super.onDestroyView()\n"
            "        _binding = null // تحرير شجرة الواجهة للسماح للـ GC بجمعها فوراً!\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "A Fragment outlives its View when pushed to the backstack; its View is destroyed in `onDestroyView()` while the Fragment instance remains in memory. If the ViewBinding reference is not cleared to null in `onDestroyView()`, it retains the entire View hierarchy and its associated Bitmaps and contexts, causing a severe memory leak.",
        "best_answer": (
            "In Android architecture, a Fragment has two distinct lifecycles: the Fragment instance lifecycle and the Fragment View lifecycle.\n\n"
            "When a Fragment transaction replaces a fragment and adds it to the backstack, the system destroys the Fragment's view hierarchy to conserve memory, invoking `onDestroyView()`. "
            "However, the Fragment object itself remains alive in the `FragmentManager` backstack waiting for the user to navigate back.\n\n"
            "A ViewBinding instance holds a strong reference to the root `View` and direct references to every view in that hierarchy. "
            "If the Fragment holds a strong property reference to that binding and fails to clear it in `onDestroyView()`, the entire view tree, along with bound Bitmaps, view listeners, and window attachments, cannot be collected by the Garbage Collector. "
            "If the user stacks several fragments, each retaining its destroyed view hierarchy, the app will rapidly hit an OutOfMemoryError.\n\n"
            "The official pattern is using a nullable backing property `_binding` that is set to `null` inside `onDestroyView()`, or using an auto-cleared lifecycle delegate."
        ),
        "deep_answer": (
            "Under the hood, views hold a reference back to their hosting `Context` (`mContext`), which is typically the `Activity`. "
            "Therefore, retaining a dead ViewBinding in a backstack Fragment not only retains views, but also retains the Activity context if the backstack outlives a recreation, compounding the severity of the leak.\n\n"
            "To eliminate boilerplate in large production codebases, many engineering teams use a custom `LifecycleObserver` property delegate (often called `AutoClearedValue` or `viewBinding()` delegate). "
            "This delegate listens to `viewLifecycleOwner.lifecycle` and automatically sets the binding reference to `null` upon `ON_DESTROY` of the view lifecycle.\n\n"
            "When running LeakCanary or Memory Profiler, this issue surfaces as a leak path through `Fragment.binding` -> `FragmentBindingImpl` -> `mRoot` (`ConstraintLayout`/`RecyclerView`). "
            "LeakCanary explicitly flags this with a high confidence rating because it detects that the Fragment is alive while its `getView()` is null."
        ),
        "follow_ups": [
            {
                "question": "Why does an Activity not require setting its ViewBinding to null in onDestroy?",
                "answer": "In an Activity, the View lifecycle and the Activity instance lifecycle are identical. When the Activity is destroyed, the Activity instance and its binding property become eligible for garbage collection together."
            },
            {
                "question": "What happens if someone accesses `binding` after `onDestroyView()` in the Fragment?",
                "answer": "With the standard backing property pattern (`_binding!!`), it immediately throws a clear `NullPointerException`, preventing silent bugs where code attempts to modify a detached, dead view hierarchy."
            }
        ]
    },
    {
        "id": "MEM-12",
        "arabic_explanation": (
            "كيف تسبب الكولباكس (Callbacks)، الـ Handlers، الـ Observers، الـ Listeners، والمراجع الاستاتيكية (Static References) تسريبات ذاكرة؟\n\n"
            "1. المراجع الاستاتيكية (Static References):\n"
            "   - أي متغير ثابت (`companion object` أو `static field` في Java) يعيش في الذاكرة طوال حياة التطبيق.\n"
            "   - إذا احتفظ المتغير الاستاتيكي بمرجع لنشاط (Activity) أو View أو كائن واجهة، فلن يستطيع مجمع النفايات تحريره إطلاقاً، مما يجعله GC Root دائم.\n\n"
            "2. الـ Handlers والـ MessageQueue:\n"
            "   - الـ `Handler` غير الثابت (Non-static inner class) في Java/Kotlin يحتفظ ضمنياً بمرجع للكائن الخارجي (`this@Activity`).\n"
            "   - عندما ترسل رسالة مؤجلة (`handler.postDelayed(runnable, 60000)`):\n"
            "   - الرسالة توضع في الـ `MessageQueue` الخاص بالـ Looper الرئيسي.\n"
            "   - الكائن `Message` يحتفظ بمرجع للـ `Handler` (target)، والـ `Handler` يحتفظ بمرجع للـ `Activity`.\n"
            "   - إذا خرج المستخدم من الشاشة، يظل النشاط مسرباً في الذاكرة طوال الـ 60 ثانية حتى يتم استهلاك الرسالة!\n\n"
            "3. الـ Listeners والـ Observers غير الملغاة:\n"
            "   - تسجيل Listener في خدمة طويلة الأجل (مثل `LocationManager` أو `SensorManager` أو Event Bus أحادي) يضيف مرجعاً للـ Activity إلى قائمة الملاحظين.\n"
            "   - إذا نسيت إلغاء التسجيل في `onStop()` أو `onDestroy()` (`unregisterListener()`)، تظل الخدمة ممسكة بالـ Activity إلى الأبد."
        ),
        "practical_walkthrough": (
            "أمثلة شائعة للتسريبات وكيفية معالجتها بدقة:\n"
            "```kotlin\n"
            "// ❌ أمثلة شائعة للتسريب:\n"
            "class LeakyActivity : AppCompatActivity() {\n"
            "    private val handler = Handler(Looper.getMainLooper()) // كائن داخلي يمسك النشاط\n"
            "\n"
            "    override fun onStart() {\n"
            "        super.onStart()\n"
            "        // 1. تسريب Handler: مهمة مؤجلة تبقى في MessageQueue:\n"
            "        handler.postDelayed({ showPromotionDialog() }, 120_000)\n"
            "\n"
            "        // 2. تسريب Listener: تسجيل في Singleton بدون إلغاء التسجيل:\n"
            "        AuthManager.registerListener { onAuthStatusChanged(it) }\n"
            "    }\n"
            "}\n"
            "\n"
            "// ✅ الكود النظيف المحمي من التسريب:\n"
            "class SafeActivity : AppCompatActivity() {\n"
            "    private val handler = Handler(Looper.getMainLooper())\n"
            "    private val authListener: (Boolean) -> Unit = { onAuthStatusChanged(it) }\n"
            "\n"
            "    override fun onStart() {\n"
            "        super.onStart()\n"
            "        AuthManager.registerListener(authListener)\n"
            "    }\n"
            "\n"
            "    override fun onStop() {\n"
            "        super.onStop()\n"
            "        // إلغاء المهام المؤجلة وإلغاء تسجيل الملاحظين فوراً:\n"
            "        handler.removeCallbacksAndMessages(null) // مسح الـ MessageQueue\n"
            "        AuthManager.unregisterListener(authListener) // تحرير مرجع النشاط\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Non-static Handlers retain outer Activity references; delayed messages in the MessageQueue keep the Activity pinned in memory until processed. Similarly, static fields act as permanent GC roots, and unregistered listeners or observers in long-lived singletons or system services keep transient UI components alive indefinitely.",
        "best_answer": (
            "Memory leaks from callbacks, Handlers, observers, and static references stem from breaking object lifecycle symmetry.\n\n"
            "1. **Handlers & MessageQueue**: A non-static Handler holds an implicit reference to its enclosing Activity. When a message is scheduled with `postDelayed()`, the `Message` in the main thread's `MessageQueue` holds a reference to the Handler target, which holds the Activity. Until the message executes or is cleared with `removeCallbacksAndMessages(null)`, the entire Activity graph is retained as a GC Root.\n\n"
            "2. **Static References**: Any `companion object` property or static variable persists across the entire application process. Assigning an Activity or View to a static field directly prevents GC reclamation.\n\n"
            "3. **Unregistered Observers**: When an Activity registers as a listener with a long-lived publisher—such as `LocationManager`, `SensorManager`, or a singleton EventBus—the publisher stores a strong reference. Failing to unregister symmetry (`unregisterListener()` in `onStop()` or `onDestroy()`) creates a permanent leak.\n\n"
            "In modern Android development, we prevent these by replacing raw Handlers with lifecycle-aware coroutines (`lifecycleScope`), binding observers with `LifecycleOwner`, and utilizing `AutoCloseable` or structured cleanup patterns."
        ),
        "deep_answer": (
            "Under the hood, Java and Kotlin inner classes differ in reference semantics: a standard inner class holds an implicit `$this$0` synthetic pointer to the outer instance. "
            "In Kotlin, declaring an anonymous lambda or `object : Runnable` inside an Activity implicitly captures the outer instance unless it references no instance properties or is explicitly declared in a `companion object` or static file-level context.\n\n"
            "When dealing with Handlers specifically, the classic Java remedy was declaring a static class paired with a `WeakReference<Activity>`. "
            "However, in modern Kotlin, Handlers are largely legacy; suspending coroutines with `delay()` within `lifecycleScope` are automatically cancelled via cooperative cancellation when the `LifecycleOwner` reaches `DESTROYED`, dropping the continuation and preventing the leak entirely.\n\n"
            "In enterprise monitoring, LeakCanary excels at pinpointing these leaks by identifying the `target` field in queued `android.os.Message` instances or scanning registered observer arrays in system managers."
        ),
        "follow_ups": [
            {
                "question": "What happens if a static Handler has no delayed messages but is active?",
                "answer": "If it has no messages in the queue, it does not retain memory. But if a message is posted, each queued `Message` references the Handler as `msg.target`. If that Handler holds an outer reference, the entire outer scope is retained until queue execution."
            },
            {
                "question": "How do modern Android Jetpack components eliminate manual listener cleanup?",
                "answer": "Components like `LiveData` and `Flow` combined with `lifecycleScope` or `repeatOnLifecycle` automatically attach and detach observers in synchrony with lifecycle events, eliminating human error in unregistering."
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

    for item in MEM_07_12:
        by_id[item["id"]] = item

    output = [by_id[k] for k in sorted(by_id.keys())]
    DATA_FILE.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {DATA_FILE} with questions MEM-07 to MEM-12. Total questions: {len(output)}")

if __name__ == "__main__":
    main()
