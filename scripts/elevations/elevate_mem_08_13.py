#!/usr/bin/env python3
"""Elevate MEM-08 through MEM-13 for bilingual parity and senior spoken answers."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(ROOT / "scripts" / "elevations"))
import elevation_engine as ee

TOPIC_AR = "إدارة الذاكرة والـ ANR وتحسين الأداء"

EN_DATA = {
    "MEM-08": {
        "concept_en": (
            "The memory leak caused by a Singleton holding an Activity Context stems from a fundamental lifecycle mismatch. "
            "A Singleton has process-level lifetime; its instance is anchored to a static variable or an application-scoped "
            "dependency injection container (such as Hilt @Singleton), persisting in memory for the entire lifespan of the Linux OS process. "
            "An Activity, in contrast, is an ephemeral UI component with a transient lifecycle tied to user navigation and configuration "
            "changes such as screen rotation. An Activity instance is never a lightweight object; it retains a substantial transitively "
            "reachable object graph, including its PhoneWindow, DecorView, inflated view trees, drawables, localized resources, and input "
            "dispatchers. When a long-lived Singleton retains an Activity reference, that reference acts as an unbroken path from a GC Root "
            "to the Activity. Consequently, when the user rotates the device or finishes the screen, the destroyed Activity cannot be "
            "reclaimed by the Garbage Collector, permanently wasting tens of megabytes of heap memory."
        ),
        "walkthrough_en": (
            "Comparing leaky Singleton context retention with safe application context extraction:\n"
            "```kotlin\n"
            "// Leaky Singleton: Holding Activity Context:\n"
            "object LocationTracker {\n"
            "    private var context: Context? = null\n"
            "    fun init(activityContext: Context) {\n"
            "        this.context = activityContext // Retains Activity forever; leaks on rotation!\n"
            "    }\n"
            "}\n"
            "\n"
            "// Safe Singleton: Extracting Application Context:\n"
            "class SafeLocationTracker private constructor(context: Context) {\n"
            "    // applicationContext has process-level lifetime, matching the Singleton:\n"
            "    private val appContext = context.applicationContext\n"
            "\n"
            "    companion object {\n"
            "        @Volatile private var instance: SafeLocationTracker? = null\n"
            "        fun getInstance(context: Context): SafeLocationTracker =\n"
            "            instance ?: synchronized(this) {\n"
            "                instance ?: SafeLocationTracker(context).also { instance = it }\n"
            "            }\n"
            "    }\n"
            "}\n"
            "```\n"
            "By invoking context.applicationContext, the singleton safely anchors to the process-level context, allowing destroyed "
            "Activity instances and their associated view hierarchies to be garbage collected immediately upon screen teardown."
        ),
        "short_en": (
            "A Singleton has process-level lifetime anchored to static memory, whereas an Activity has a transient lifecycle destroyed "
            "on screen exit or rotation. If a Singleton holds an Activity Context, that Activity cannot be collected by the GC, "
            "leaking its entire view tree, bitmaps, and resources. Singletons should only hold applicationContext or use dependency "
            "injection with proper lifecycle scoping."
        ),
        "structured_en": (
            "To begin with, memory leaks caused by singletons holding Context are among the most prevalent architectural flaws in Android development. "
            "The root cause is a lifecycle mismatch: a Singleton instance lives in static memory for the entire duration of the application "
            "process, whereas an Activity is an ephemeral UI component designed to be destroyed and recreated across configuration changes "
            "and navigation. From an architectural standpoint, an Activity context does not exist in isolation; it holds direct references "
            "to the PhoneWindow, the DecorView, inflated view hierarchies, drawables, and localized resource caches. When a Singleton retains "
            "an Activity reference, it forms an unbreakable path from a GC Root to that Activity. Consequently, when the user navigates away "
            "or rotates the device, the destroyed Activity cannot be reclaimed. In production scenarios, rotating a screen five times retains "
            "five complete Activity trees, multiplying memory consumption and triggering out-of-memory crashes. As for boundary management, "
            "singletons must either extract context.applicationContext or leverage dependency injection frameworks like Hilt to bind dependencies "
            "strictly to ActivityRetainedScoped or Singleton containers with clean boundaries."
        ),
        "deep_senior_en": (
            "In deep memory profiling, an Activity leak caused by a static singleton presents a distinct signature in HPROF heap dumps. "
            "In Android Studio Profiler or Eclipse Memory Analyzer Tool, inspecting the Dominator Tree reveals that the retained heap "
            "of the leaked Activity often exceeds 20 to 50 megabytes. This bloated footprint is not caused by the Activity class fields alone, "
            "but by its retained transitively held dependencies: the mWindow reference points to PhoneWindow, which anchors the DecorView, "
            "holding every inflated ViewGroup, TextView, and hardware-backed Bitmap loaded into memory.\n\n"
            "When analyzing the leak path in LeakCanary, the engine computes the Shortest Path to GC Roots, highlighting a static field "
            "such as com.example.Manager.Companion.instance holding a reference to mActivity. To resolve this at a platform architecture level, "
            "staff engineers enforce strict context policies. If a service requires UI capabilities—such as inflating layouts with custom "
            "themes or showing alert dialogs—that service must be scoped to the Activity lifecycle and unregistered in onDestroy(). If a "
            "singleton only requires system services, shared preferences, or database access, it must strictly reference context.applicationContext "
            "or inject ApplicationContext via Hilt. Furthermore, static analysis tools like Android Lint with the StaticFieldLeak rule and "
            "automated LeakCanary assertions in Espresso integration tests should be configured on CI pipelines to catch static context leaks "
            "before pull requests are merged."
        ),
    },
    "MEM-09": {
        "concept_en": (
            "Both ViewModels and coroutines can leak memory when their lifecycles and reference scopes are improperly managed. A ViewModel "
            "is designed to outlive an Activity or Fragment across configuration changes, retained by the ViewModelStoreOwner. If a ViewModel "
            "holds a direct or indirect reference to an Activity, Fragment, View, or ViewBinding (for instance, via a listener or callback "
            "interface), that reference prevents the destroyed Activity from being garbage collected across rotations. Coroutines leak memory "
            "when launched in scopes that outlive the host component—such as GlobalScope, an unmanaged CoroutineScope, or a long-running "
            "background dispatcher—while capturing the outer Activity or Fragment reference in their closure or suspension state machine. "
            "Until the coroutine completes or is explicitly cancelled, the entire captured UI hierarchy is retained in heap memory."
        ),
        "walkthrough_en": (
            "Demonstrating ViewModel and coroutine leak scenarios and their remediation:\n"
            "```kotlin\n"
            "// Leaky ViewModel: Holding a View reference and unmanaged coroutine:\n"
            "class LeakyOrderViewModel : ViewModel() {\n"
            "    var orderView: View? = null // Leaks view across rotation!\n"
            "\n"
            "    fun startPolling() {\n"
            "        // Leaks outer class and runs indefinitely if not cancelled:\n"
            "        CoroutineScope(Dispatchers.IO).launch {\n"
            "            while (true) {\n"
            "                delay(5000)\n"
            "                updateUi() // Captures outer class reference\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "}\n"
            "\n"
            "// Safe ViewModel: Using StateFlow and viewModelScope:\n"
            "class SafeOrderViewModel(private val repository: OrderRepository) : ViewModel() {\n"
            "    private val _uiState = MutableStateFlow<OrderUiState>(OrderUiState.Loading)\n"
            "    val uiState: StateFlow<OrderUiState> = _uiState.asStateFlow()\n"
            "\n"
            "    fun startPolling() {\n"
            "        // Automatically cancelled when onCleared() is invoked:\n"
            "        viewModelScope.launch {\n"
            "            repository.pollOrders()\n"
            "                .collect { orders -> _uiState.value = OrderUiState.Success(orders) }\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```\n"
            "Using viewModelScope ensures that all active child jobs are automatically cancelled when the ViewModel is destroyed in onCleared(), "
            "freeing all captured references."
        ),
        "short_en": (
            "ViewModels leak memory if they hold references to Activities, Views, or callbacks that outlive configuration changes. "
            "Coroutines leak memory when launched in non-lifecycle scopes like GlobalScope or unmanaged scopes while capturing UI "
            "references in their execution closures. To prevent leaks, ViewModels must expose state via Flow without holding View "
            "references, and coroutines must use viewModelScope or repeatOnLifecycle."
        ),
        "structured_en": (
            "To begin with, neither ViewModels nor coroutines are inherently immune to memory leaks; leaks occur when their operational "
            "lifetimes exceed the lifespan of the components they reference. A Jetpack ViewModel is intentionally preserved across configuration "
            "changes inside the ViewModelStore. If a ViewModel holds a reference to an Activity, Fragment, or View—either directly or through "
            "an anonymous callback—that reference pins the destroyed screen in memory across device rotation until the ViewModel itself is cleared. "
            "From an architectural standpoint, coroutines introduce leak risks through execution closures. When a coroutine is launched in "
            "GlobalScope or a custom unmanaged CoroutineScope, its underlying continuation captures the enclosing class instance. If that coroutine "
            "performs a long network request, delays indefinitely, or blocks on I/O, the captured Activity cannot be garbage collected for the "
            "entire duration of the job. In production scenarios, observing flows in the UI without lifecycle awareness causes background "
            "collection to continue even when the screen is hidden. As for boundary management, developers must bind all ViewModel work to "
            "viewModelScope, decouple UI interactions through unidirectional StateFlow, and collect flows in the UI using repeatOnLifecycle."
        ),
        "deep_senior_en": (
            "Under the hood, Kotlin coroutine compilation provides deep insights into why uncancelled coroutines leak memory. When the Kotlin "
            "compiler processes a suspend function or coroutine builder, it transforms the code into a state machine implementing the Continuation "
            "interface. This generated continuation object maintains references to local variables, execution state labels, and an implicit reference "
            "to the outer class instance (this$0) if any outer member is accessed. Active worker threads in dispatchers like Dispatchers.Default and "
            "Dispatchers.IO act as active GC Roots. As long as a coroutine job is active, suspended, or waiting for a delay timer, the dispatcher "
            "thread holds the continuation, which in turn holds the enclosing class.\n\n"
            "If that enclosing class is an Activity or Fragment, the entire view hierarchy and context graph remain anchored to the thread pool GC Root. "
            "In Jetpack Architecture Components, viewModelScope mitigates this by binding a SupervisorJob to the ViewModel. When the user permanently "
            "finishes the Activity, ViewModelStore.clear() invokes ViewModel.onCleared(), which immediately cancels the underlying CoroutineContext and "
            "unregisters active continuation callbacks. In the UI layer, collecting a cold Flow or hot SharedFlow inside lifecycleScope.launch without "
            "repeatOnLifecycle keeps the collector running while the app is in the background, consuming CPU and retaining views. By wrapping UI "
            "collections in viewLifecycleOwner.repeatOnLifecycle with Lifecycle.State.STARTED, Android suspends and cancels collector coroutines "
            "automatically whenever the view moves below the started state, eliminating both background thread leaks and UI update crashes."
        ),
    },
    "MEM-10": {
        "concept_en": (
            "An Application Not Responding (ANR) error is an Android system-level watchdog failure triggered when an application's main thread "
            "is blocked for too long and cannot process incoming user input or system callbacks. The operating system monitors main thread "
            "responsiveness via ActivityManagerService and AnrHelper. If the app fails to dispatch an input event (touch, key press) within 5 "
            "seconds, finish executing a foreground BroadcastReceiver within 10 to 20 seconds (60 seconds in background), or complete a foreground "
            "Service lifecycle callback within 20 seconds (200 seconds in background), the OS halts the process, logs an ANR trace, and displays "
            "the system ANR dialog. Common causes include running synchronous disk I/O or database queries on the main thread, performing network "
            "requests, executing CPU-intensive algorithms, deadlocks and lock contention waiting on background threads, and IPC Binder call starvation."
        ),
        "walkthrough_en": (
            "Identifying main-thread blockage and moving work to background dispatchers:\n"
            "```kotlin\n"
            "// ANR Trigger: Synchronous disk I/O and heavy parsing on the Main Thread:\n"
            "class BadSettingsActivity : AppCompatActivity() {\n"
            "    override fun onCreate(savedInstanceState: Bundle?) {\n"
            "        super.onCreate(savedInstanceState)\n"
            "        // Blocking main thread with disk read and JSON parsing in onCreate:\n"
            "        val rawConfig = File(filesDir, \"config.json\").readText() // Disk I/O on Main Thread!\n"
            "        val parsed = JSONObject(rawConfig) // CPU-heavy parsing blocking Looper!\n"
            "        applyConfig(parsed)\n"
            "    }\n"
            "}\n"
            "\n"
            "// Clean Architecture: Asynchronous execution on Dispatchers.IO:\n"
            "class GoodSettingsActivity : AppCompatActivity() {\n"
            "    override fun onCreate(savedInstanceState: Bundle?) {\n"
            "        super.onCreate(savedInstanceState)\n"
            "        lifecycleScope.launch {\n"
            "            val parsed = withContext(Dispatchers.IO) {\n"
            "                val rawConfig = File(filesDir, \"config.json\").readText()\n"
            "                JSONObject(rawConfig)\n"
            "            }\n"
            "            applyConfig(parsed)\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```\n"
            "Offloading file operations and JSON parsing to Dispatchers.IO keeps the Main Thread Looper free to process frame rendering and touch "
            "events without triggering watchdog timeouts."
        ),
        "short_en": (
            "An ANR occurs when the main thread looper is blocked and cannot respond to user input within 5 seconds, a broadcast receiver "
            "within 10 to 20 seconds, or a service within 20 seconds. Common causes include synchronous disk or database I/O on the main "
            "thread, lock contention with background threads, network calls, and long garbage collection pauses. Profiling traces.txt "
            "helps identify root causes."
        ),
        "structured_en": (
            "To begin with, an Application Not Responding condition is not a runtime crash or an out-of-memory error, but an operating system "
            "responsiveness failure. The Android OS monitors main thread execution through watchdog timers managed by ActivityManagerService. "
            "When an app fails to respond to touch or key input within five seconds, finish a foreground BroadcastReceiver within ten to twenty "
            "seconds, or execute a foreground Service callback within twenty seconds, the system displays the ANR dialog and allows the user "
            "to kill the process. From an architectural standpoint, an ANR occurs whenever the Main Thread Looper message queue is prevented "
            "from processing pending messages. The most frequent triggers are synchronous disk reads or writes, database operations, network "
            "calls, and complex JSON deserialization executed directly on the UI thread. In production scenarios, subtle ANRs are caused by "
            "thread lock contention, where the main thread attempts to acquire a synchronized mutex held by a low-priority background thread. "
            "As for boundary management, senior engineers enforce strict threading boundaries, offloading all non-UI computation to background "
            "coroutine dispatchers and instrumenting debug builds with StrictMode."
        ),
        "deep_senior_en": (
            "At a staff engineering level, triaging production ANRs centers on analyzing thread execution states and kernel wait-channels "
            "inside the system ANR trace file (data anr traces.txt) or Google Play Console Android Vitals. When an ANR occurs, the Android kernel "
            "dumps stack traces for all active threads in the process. When inspecting the main thread in the trace, we examine its execution "
            "state: RUNNABLE, BLOCKED, or WAITING. If the main thread is in the BLOCKED state, the trace reveals the specific monitor lock it is "
            "waiting to acquire, along with the thread ID holding that lock. This signature immediately points to multi-threading lock contention "
            "or priority inversion, where a background thread was preempted while holding a critical shared resource.\n\n"
            "If the main thread is marked as WAITING or NATIVE in a Binder call (such as BinderProxy.transact), the application is stalled "
            "waiting on a synchronous IPC response from a system service or another application process. Furthermore, we evaluate total CPU "
            "utilization reported in the ANR header: if CPU usage is near 100% with high kswapd0 or ART GC daemon activity, the ANR is an indirect "
            "casualty of extreme memory pressure or allocation churn, where continuous stop-the-world GC cycles starved the main thread of CPU "
            "execution slices. To prevent ANRs proactively, we configure StrictMode in debug environments and monitor our Google Play Console "
            "ANR rate to remain comfortably below the bad behavior threshold of 0.47%."
        ),
    },
    "MEM-11": {
        "concept_en": (
            "Releasing Fragment ViewBinding references is mandatory because a Fragment instance has a different, longer lifecycle than "
            "its associated View hierarchy. When a Fragment is added to the navigation backstack (for example, via FragmentTransaction replace "
            "with addToBackStack), its view hierarchy is destroyed via onDestroyView(), but the Fragment class instance itself remains cached "
            "in memory in the FragmentManager. A generated ViewBinding object holds strong references to the root View and every bound subview, "
            "widget, and layout container in the XML hierarchy. If the Fragment maintains a strong, non-null reference to the binding after "
            "onDestroyView(), the entire destroyed view tree, along with all attached listeners, drawables, and contextual references, is "
            "leaked in heap memory until the Fragment is permanently popped from the backstack."
        ),
        "walkthrough_en": (
            "Implementing the standard nullable backing property pattern:\n"
            "```kotlin\n"
            "// Leaky Fragment: Retaining ViewBinding after onDestroyView:\n"
            "class LeakyFragment : Fragment(R.layout.fragment_detail) {\n"
            "    // Permanent reference keeps the entire View tree in memory on the backstack:\n"
            "    private lateinit var binding: FragmentDetailBinding\n"
            "\n"
            "    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {\n"
            "        super.onViewCreated(view, savedInstanceState)\n"
            "        binding = FragmentDetailBinding.bind(view)\n"
            "    }\n"
            "}\n"
            "\n"
            "// Correct Implementation: Clearing binding in onDestroyView:\n"
            "class SafeFragment : Fragment(R.layout.fragment_detail) {\n"
            "    private var _binding: FragmentDetailBinding? = null\n"
            "    // Read-only property valid strictly between onCreateView and onDestroyView:\n"
            "    private val binding get() = _binding!!\n"
            "\n"
            "    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {\n"
            "        super.onViewCreated(view, savedInstanceState)\n"
            "        _binding = FragmentDetailBinding.bind(view)\n"
            "    }\n"
            "\n"
            "    override fun onDestroyView() {\n"
            "        super.onDestroyView()\n"
            "        // Release strong reference so the view tree can be collected:\n"
            "        _binding = null\n"
            "    }\n"
            "}\n"
            "```\n"
            "Nulling out _binding in onDestroyView() severs the reference path, allowing the ART Garbage Collector to reclaim the destroyed "
            "view hierarchy while the Fragment waits on the backstack."
        ),
        "short_en": (
            "A Fragment outlives its View hierarchy when placed on the navigation backstack. In this state, onDestroyView is called, "
            "but the Fragment instance remains retained in memory. Because ViewBinding holds strong references to the entire view tree, "
            "failing to clear the binding reference in onDestroyView leaks the view hierarchy, its drawables, and listeners on the heap."
        ),
        "structured_en": (
            "To begin with, the necessity of clearing Fragment ViewBinding references stems from the dual lifecycle architecture unique to "
            "Android Fragments. While an Activity's lifecycle is unified with its window, a Fragment's instance lifecycle is distinct from "
            "its view lifecycle. When a user navigates to a subsequent screen and the current Fragment is pushed onto the navigation backstack, "
            "its view hierarchy is destroyed through onDestroyView(), yet the Fragment instance remains alive in memory to preserve state "
            "and argument bundles. From an architectural standpoint, a generated ViewBinding class holds direct strong references to the root "
            "view and every nested widget in the layout. If a Fragment retains its binding field past onDestroyView(), that binding holds "
            "the entire view tree alive on the managed heap. In production scenarios where users navigate through deep backstack journeys, "
            "each retained Fragment leaks its entire layout, quickly wasting hundreds of megabytes of RAM. As for boundary management, developers "
            "must adopt the nullable backing property pattern, clearing _binding to null in onDestroyView(), or employ custom view-lifecycle "
            "binding delegates that automate cleanup upon view destruction."
        ),
        "deep_senior_en": (
            "From a memory profiling and dominator tree perspective, a leaked Fragment view hierarchy is among the largest leaks in modern "
            "Android codebases. When analyzing an HPROF snapshot in LeakCanary, a leaked ViewBinding exhibits a high Retained Size because a "
            "single root ViewGroup anchors a deep tree of child views, custom layout managers, RecyclerView adapter pools, and image drawables "
            "holding hardware bitmaps. Furthermore, each view holds an implicit reference to the host Context, which can transitively prevent "
            "the host Activity from being cleaned up if listeners are attached.\n\n"
            "To eliminate boilerplate and human error in enterprise codebases, engineering teams often implement an AutoClearedValue delegate "
            "or a lifecycle-aware property delegate that observes viewLifecycleOwner.lifecycle. By registering an observer that listens for "
            "Lifecycle.Event.ON_DESTROY on the view lifecycle, the delegate automatically sets the binding reference to null as soon as "
            "onDestroyView() executes, throwing an informative IllegalStateException if code attempts to access the binding outside the view's "
            "active lifespan. Notably, in modern Android development adopting Jetpack Compose, this entire class of bugs is completely eradicated: "
            "Composable functions do not utilize XML view hierarchies or ViewBinding, and UI state is managed through recomposition rather than "
            "mutable view reference caching. From a bytecode and compiler perspective, synthetic accessors generated for ViewBinding must not retain references past lifecycle teardown, ensuring that class unloaders and generational garbage collectors can sweep the detached view hierarchies without retaining unreachable nodes."
        ),
    },
    "MEM-12": {
        "concept_en": (
            "Callbacks, Handlers, observers, listeners, and static variables cause memory leaks through the creation of unintentional, "
            "persistent reference chains from long-lived GC Roots to short-lived UI components. In the Java and Kotlin object model, non-static "
            "inner classes, anonymous interfaces, and lambdas implicitly capture a strong reference to their enclosing outer class instance (this$0). "
            "When an Activity or Fragment registers such a callback with a long-lived component—such as an active Handler message queue, a "
            "singleton event bus, a system sensor manager, or a static list—the short-lived UI component becomes transitively anchored to an enduring "
            "GC Root. Even after the Activity finishes or is recreated on rotation, the garbage collector cannot reclaim it because the live root path "
            "preserves reachability, causing steady memory accumulation."
        ),
        "walkthrough_en": (
            "Analyzing Handler message leak mechanics and lifecycle-safe remediation:\n"
            "```kotlin\n"
            "// Leaky Handler: Anonymous Runnable holds implicit reference to Activity:\n"
            "class LeakyActivity : AppCompatActivity() {\n"
            "    private val handler = Handler(Looper.getMainLooper())\n"
            "\n"
            "    override fun onCreate(savedInstanceState: Bundle?) {\n"
            "        super.onCreate(savedInstanceState)\n"
            "        // Delayed message holds Runnable, which holds LeakyActivity via this$0:\n"
            "        handler.postDelayed({\n"
            "            updateTitle() // Implicitly references LeakyActivity.this\n"
            "        }, 60_000) // 1-minute delay leaks Activity across rotation!\n"
            "    }\n"
            "}\n"
            "\n"
            "// Correct: Removing callbacks symmetrically or using lifecycle coroutines:\n"
            "class SafeActivity : AppCompatActivity() {\n"
            "    override fun onCreate(savedInstanceState: Bundle?) {\n"
            "        super.onCreate(savedInstanceState)\n"
            "        // Coroutine automatically cancelled when Activity finishes:\n"
            "        lifecycleScope.launch {\n"
            "            delay(60_000)\n"
            "            updateTitle()\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```\n"
            "Using lifecycleScope ensures that when the Activity is destroyed, the coroutine is cancelled and the continuation is released "
            "from the main looper, preventing memory retention."
        ),
        "short_en": (
            "Callbacks, Handlers, listeners, and static fields cause leaks when they hold implicit or explicit references to short-lived "
            "Activities or Fragments from long-lived GC roots. An unexecuted Handler message or unreleased static listener keeps the entire "
            "Activity reachable after it is destroyed. Leaks are avoided through symmetrical unregistration, static classes with WeakReferences, "
            "or lifecycle-aware coroutines."
        ),
        "structured_en": (
            "To begin with, reference leaks involving callbacks, Handlers, and static variables represent the classic failure mechanism of "
            "object retention in Android. In Kotlin and Java, any non-static inner class, anonymous listener, or lambda that touches an outer "
            "member implicitly captures a reference to that outer class instance. When an Activity registers an anonymous callback with a "
            "long-lived publisher—such as a location manager, an event bus, or a background worker—a direct reference edge is established. "
            "From an architectural standpoint, if the publisher outlives the screen and the developer fails to unregister the listener symmetrically "
            "in onStop() or onDestroy(), the publisher acts as a GC Root that keeps the destroyed Activity reachable. Similarly, posting a delayed "
            "Message to a Handler enqueues an object in the main thread's MessageQueue; the message references the Handler, which captures the Activity, "
            "retaining it until the message executes. As for boundary management, developers must maintain strict lifecycle symmetry, clear pending "
            "Handler messages via removeCallbacksAndMessages(null), or replace legacy callbacks with lifecycle-aware coroutines."
        ),
        "deep_senior_en": (
            "Under the hood, analyzing how the Android MessageQueue operates clarifies why Handler leaks occur so frequently. When "
            "handler.postDelayed(runnable, delay) is called, the runtime constructs a Message object where msg.target is assigned to the "
            "Handler, and msg.callback is assigned to the Runnable. This Message is inserted into the native MessageQueue ordered by execution "
            "timestamp. The native Looper associated with the active main thread continues polling this queue. Because the thread is an active "
            "GC Root, any pending message in the queue is strongly reachable. If the Runnable was declared as an anonymous class or a lambda "
            "capturing a view or Activity method, its implicit this$0 field keeps the entire Activity in the retained heap. If the user rotates "
            "the screen or navigates back while a 30-second delay is pending, the destroyed Activity remains leaked for the duration of that timer.\n\n"
            "When dealing with static references, the issue is even more severe: a static collection like companion object holding listeners is "
            "rooted directly to the java.lang.Class object loaded by the application class loader, creating an immortal leak that persists until "
            "process death. To diagnose these retention chains in production, staff engineers use Android Studio Profiler's Paths to GC Roots tree. "
            "In modern architectures, legacy Handlers and callbacks should be refactored to kotlinx.coroutines. If a legacy API must be supported, "
            "engineers encapsulate the reference inside a WeakReference or utilize static nested classes to sever the implicit outer pointer, "
            "combined with defensive unregistration inside lifecycle teardown hooks."
        ),
    },
    "MEM-13": {
        "concept_en": (
            "Bitmaps represent one of the largest single consumers of runtime memory in mobile applications. The memory footprint of an "
            "uncompressed bitmap is determined strictly by its pixel dimensions and color configuration: width multiplied by height multiplied "
            "by bytes per pixel. For the default Bitmap.Config.ARGB_8888, each pixel requires 4 bytes. Consequently, naively decoding a "
            "12-megapixel smartphone camera photo (4000x3000) requires approximately 48 megabytes of contiguous memory, regardless of whether "
            "the compressed JPEG on disk was only 2MB! Historically, Android allocated bitmap pixel buffers on the Java heap (Android 3.0 to 7.1), "
            "which caused frequent GC fragmentation and out-of-memory errors. Starting with Android 8.0 (API 26), pixel memory is allocated on "
            "the native C++ heap managed via NativeAllocationRegistry, with hardware textures (Bitmap.Config.HARDWARE) stored directly in graphic "
            "GPU memory. Modern image libraries (Coil, Glide) prevent OOMs by downsampling images to match target view dimensions, pooling pixel "
            "buffers via inBitmap, and caching decoded bitmaps in bounded memory budgets."
        ),
        "walkthrough_en": (
            "Decoding an image with subsampling versus naive decoding:\n"
            "```kotlin\n"
            "// Inefficient: Decoding full 48MB bitmap for a 200x200 thumbnail:\n"
            "val fullBitmap = BitmapFactory.decodeFile(imagePath) // 48MB native allocation!\n"
            "\n"
            "// Efficient: Two-pass decoding with target-size downsampling:\n"
            "fun decodeSampledBitmap(path: String, reqWidth: Int, reqHeight: Int): Bitmap {\n"
            "    val options = BitmapFactory.Options().apply {\n"
            "        inJustDecodeBounds = true // Reads image dimensions without allocating pixel memory\n"
            "    }\n"
            "    BitmapFactory.decodeFile(path, options)\n"
            "\n"
            "    // Calculate inSampleSize (power of 2):\n"
            "    var inSampleSize = 1\n"
            "    if (options.outHeight > reqHeight || options.outWidth > reqWidth) {\n"
            "        val halfHeight = options.outHeight / 2\n"
            "        val halfWidth = options.outWidth / 2\n"
            "        while ((halfHeight / inSampleSize) >= reqHeight && (halfWidth / inSampleSize) >= reqWidth) {\n"
            "            inSampleSize *= 2\n"
            "        }\n"
            "    }\n"
            "\n"
            "    options.inSampleSize = inSampleSize\n"
            "    options.inJustDecodeBounds = false\n"
            "    return BitmapFactory.decodeFile(path, options) // Decodes only required pixels!\n"
            "}\n"
            "```\n"
            "Downsampling by a factor of 4 reduces pixel count by 16x, slashing memory consumption from 48MB down to just 3MB while preserving "
            "visual fidelity on screen."
        ),
        "short_en": (
            "Bitmap memory is calculated as width times height times bytes per pixel (4 bytes for ARGB_8888), making high-resolution images "
            "huge memory consumers regardless of compressed file size. Since Android 8.0, pixel data lives in native memory managed via "
            "NativeAllocationRegistry. Image-loading libraries like Coil and Glide prevent OOMs by downsampling images to target view bounds, "
            "pooling bitmaps to avoid allocation churn, and caching within memory budgets."
        ),
        "structured_en": (
            "To begin with, managing Bitmap allocations is critical to avoiding out-of-memory crashes because raw pixel data consumes massive "
            "memory relative to standard application objects. The memory required by a decoded bitmap depends strictly on its resolution "
            "and color format, calculated as width multiplied by height multiplied by color depth. For instance, a standard twelve-megapixel "
            "image decoded using ARGB_8888 consumes nearly forty-eight megabytes of contiguous memory, even if the compressed JPEG file was "
            "only two megabytes on disk. From an architectural standpoint, the Android platform has transitioned bitmap storage over time: "
            "while older versions held pixel data on the Java heap, Android 8.0 moved pixel buffers into native C++ memory, tracked by "
            "NativeAllocationRegistry and hardware GPU textures. In production scenarios, decoding unscaled images directly into small UI "
            "views quickly exhausts native address space. As for boundary management, production applications should never decode raw files "
            "manually without sub-sampling. Modern image loading libraries like Coil and Glide handle this automatically by reading view "
            "dimensions, setting inSampleSize, reusing pixel buffers via inBitmap, and maintaining an in-memory LruCache bounded by device RAM."
        ),
        "deep_senior_en": (
            "At a staff engineering level, profiling bitmap memory requires inspecting both the Java heap and the native graphics memory "
            "using adb shell dumpsys meminfo and the Android Studio Profiler. In modern Android versions, because bitmap pixel memory is "
            "allocated in native heap, a Java-only heap dump might appear healthy with only 40MB allocated, while the overall process PSS "
            "exceeds 300MB due to native and graphics memory bloat. The garbage collector still reclaims native bitmap memory, but it does so "
            "through NativeAllocationRegistry, which registers a cleaner callback invoked when the Java Bitmap wrapper becomes unreachable. "
            "However, because the Java wrapper is small (under 100 bytes), the ART GC may not feel sufficient heap pressure to trigger collection "
            "promptly, allowing native memory to swell dangerously.\n\n"
            "To optimize high-density image displays, senior engineers utilize Bitmap.Config.HARDWARE, which delegates bitmap storage directly "
            "to GPU VRAM with zero-copy rendering pipelines, cutting CPU-to-GPU memory transfer overhead. However, hardware bitmaps are immutable "
            "and cannot be drawn to a software Canvas, requiring fallback to ARGB_8888 for image editing pipelines. Furthermore, image libraries "
            "implement Bitmap Pooling using BitmapFactory.Options.inBitmap. Instead of allocating and freeing pixel byte arrays on every image "
            "transition—which causes severe memory churn and GC pauses—the library reuses existing allocated byte buffers of identical or smaller "
            "sizes. Combined with memory budgets dynamically calculated from ActivityManager.getMemoryClass() and listening for onTrimMemory "
            "callbacks, this architecture ensures high-performance, stutter-free visual rendering across diverse Android hardware tiers."
        ),
    },
}

AR_DATA = {
    "MEM-08": {
        "id": "MEM-08",
        "questionAr": "لماذا يتسبب احتفاظ الـ Singleton بسياق النشاط (Activity Context) في تسريب الذاكرة؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": (
            "- تفسير عدم تطابق دورة الحياة (Lifetime Mismatch) وشجرة المراجع الضخمة المحتجزة مع الـ Activity المسربة.\n"
            "- اختيار `applicationContext` للعمليات التي لا تتطلب سمات واجهة المستخدم (Themes) أو إمكانيات الشاشة الحصرية.\n"
            "- تصحيح حدود الملكية بدقة بدلاً من الاستبدال العشوائي لكل سياق بدون فهم هندسي."
        ),
        "why_it_matters_ar": (
            "السبب الجوهري لحدوث تسريب الذاكرة عند احتفاظ الـ Singleton بسياق الـ Activity يرجع إلى عدم تطابق فترات البقاء في الذاكرة (Lifetime Mismatch). "
            "كائن الـ Singleton يرتبط بحقل ثابت (Static Field) أو بحاوية حقن تبعيات على مستوى التطبيق، وبالتالي يعيش طوال فترة بقاء العملية (Process Lifetime). "
            "في المقابل، الـ Activity كائن مؤقت مرتبط بنافذة العرض وتفاعلات المستخدم وتدوير الشاشة. الـ Activity في أندرويد ليست مجرد كود، بل تمسك بـ PhoneWindow "
            "و DecorView وشجرة الـ Views كاملة ومصفوفات الرسوميات. عندما يمسك الـ Singleton بمرجع قوي للـ Activity، يظل مسار الوصول متصلاً من جذر GC Root حي، "
            "مما يمنع الـ Garbage Collector من تحرير الشاشة عند تدميرها، فتتراكم الشاشات في الـ Heap حتى ينهار التطبيق بـ OutOfMemoryError."
        ),
        "worked_example_ar": (
            "المقارنة بين كود يسرب الـ Activity وكود آمن يستخلص سياق التطبيق:\n"
            "```kotlin\n"
            "// ❌ كود يسرب الـ Activity للأبد:\n"
            "object LocationTracker {\n"
            "    private var context: Context? = null\n"
            "    fun init(activityContext: Context) {\n"
            "        this.context = activityContext // يسرب الشاشة عند التدوير أو الخروج!\n"
            "    }\n"
            "}\n"
            "\n"
            "// ✅ كود آمن يعتمد على Application Context:\n"
            "class SafeLocationTracker private constructor(context: Context) {\n"
            "    private val appContext = context.applicationContext // يعيش بعمر العملية بأمان\n"
            "\n"
            "    companion object {\n"
            "        @Volatile private var instance: SafeLocationTracker? = null\n"
            "        fun getInstance(context: Context): SafeLocationTracker =\n"
            "            instance ?: synchronized(this) {\n"
            "                instance ?: SafeLocationTracker(context).also { instance = it }\n"
            "            }\n"
            "    }\n"
            "}\n"
            "```\n"
            "باستخدام `context.applicationContext`، يرتبط الـ Singleton بسياق العملية ككل، مما يسمح للـ Garbage Collector بتحرير شاشة الـ Activity بمجرد تدميرها دون أي عوائق."
        ),
        "trade_offs_ar": (
            "استخدام `applicationContext` آمن في الكائنات طويلة الأجل وخدمات النظام زي LocationManager والتخزين، لكنه يفتقر إلى الـ Theme والـ Styling "
            "ومعلومات النوافذ؛ لذا لا يمكن استخدامه لنفخ واجهات المستخدم (Layout Inflation) أو إظهار الـ Dialogs. في المقابل، العمليات المرئية تتطلب حتماً "
            "سياق الـ Activity، ولكن يجب قصر استخدامها على مكونات مرتبطة بدورة حياة الشاشة وإلغاء تسجيلها في `onDestroy`. التصميم السليم لا يعتمد على استبدال "
            "كل Context بـ ApplicationContext بشكل أعمى، بل بتحديد مسؤولية كل كائن بدقة."
        ),
        "failure_modes_ar": (
            "تدوير الشاشة 5 مرات متتالية مع وجود Singleton يحتفظ بـ Activity Context يؤدي لاحتجاز 5 نسخ كاملة من الشاشة في الـ Heap، مما يستنزف عشرات الميجابايت "
            "ويؤدي لكراش OOM حتمي. استخدام `applicationContext` بالخطأ لنفخ Views يؤدي لفقدان التنسيقات والألوان المخصصة (Theme Attributes) وظهور الواجهة بمظهر مكسور. "
            "محاولة إظهار `AlertDialog` باستخدام `applicationContext` تفجر استثناء `WindowManager.BadTokenException` فوري لأن سياق التطبيق لا يملك نافذة معتمدة على الشاشة."
        ),
        "production_perspective_ar": (
            "في المشروعات الكبرى، نفرض قواعد صارمة عبر Hilt؛ حيث يتم حقن `@ApplicationContext` في الفئات المعرفة بـ `@Singleton`، بينما تُحقن شاشات الـ Activities "
            "في نطاق `@ActivityScoped` فقط. يتم تفعيل فحص `StaticFieldLeak` في Android Lint كخطوة أساسية في الـ CI/CD لمنع دمج أي متغير ثابت يشير لـ Context. "
            "كما تُفحص تقارير LeakCanary دورياً للتأكد من عدم وجود سلاسل مراجع تصل من الـ Singletons إلى كائنات الـ UI."
        ),
        "how_to_answer_ar": (
            "- **شرح عدم تطابق العمر:** ابدأ بتوضيح الفارق بين عمر الـ Singleton (بعمر العملية) وعمر الـ Activity (مؤقت وقصير).\n"
            "- **تحليل الموارد المحتجزة:** وضّح أن التسريب لا يشمل كائن الـ Activity وحده، بل يجر معه نافذة العرض وشجرة الواجهة والرسوميات.\n"
            "- **الحل الهندسي والمفاضلة:** اشرح متى نستخدم `applicationContext` ومتى نحتاج سياق الشاشة، واذكر استثناء الـ BadTokenException عند فتح النوافذ."
        ),
        "talking_points_ar": (
            "ناقش مفهوم شجرة المراجع المحتجزة (Retained Heap) في HPROF، وتفاصيل استثناء BadTokenException، وكيفية تنظيم نطاقات الـ Dependency Injection في Hilt، "
            "واستخدام المراجع الضعيفة (WeakReference) كحل أخير إذا كان لا بد من الاحتفاظ بمرجع شاشة مؤقت."
        ),
        "follow_ups_ar": (
            "- **المحاور:** \"هل ينفع نصلح المشكلة دي بأننا نستخدم `WeakReference<Activity>` جوه الـ Singleton؟\"\n"
            "  **المرشح:** \"نظرياً الـ WeakReference هيكسر سلسلة المراجع وهيخلي الـ GC قادر يحرر الـ Activity عند تدميرها، لكن ده بيتطلب فحص القيمة باستمرار لتجنب الـ Nullability، والأصح معمارياً هو استخدام `applicationContext` لو الكائن محتاج خدمات عامة، أو ربط الكائن بدورة حياة الـ Activity لو محتاج قدرات مرئية.\"\n\n"
            "- **المحاور:** \"إيه اللي هيحصل لو حاولنا نعرض `AlertDialog` باستخدام `applicationContext`؟\"\n"
            "  **المرشح:** \"التطبيق هيضرب كراش فوري بـ `WindowManager.BadTokenException: Unable to add window -- token null is not valid`؛ لأن الـ Dialog محتاج Window Token مخصص بتوفره الـ Activity فقط ومش موجود في سياق التطبيق.\""
        ),
        "self_check_ar": (
            "اشرح معنى Lifetime Mismatch؛ حدد ثلاثة مكونات فرعية تسربها الـ Activity المسربة؛ واذكر سيناريوهين لا يجوز فيهما استخدام applicationContext."
        ),
        "references_ar": (
            "- [التعامل السليم مع الـ Context في أندرويد](https://developer.android.com/reference/android/content/Context) — الفروق بين أنواع السياق المختلفة ودورات حياتها.\n"
            "- [دليل تجنب تسريبات الذاكرة في الـ Singletons](https://developer.android.com/topic/performance/memory) — إرشادات إدارة سياق التطبيق.\n\n"
            "تمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13."
        ),
        "quick_answer_ar": (
            "الـ Singleton بيعيش في الذاكرة طوال فترة تشغيل التطبيق لأنه مربوط بـ Static Field، بينما الـ Activity كائن مؤقت بيتدمر ويعاد إنشاؤه مع التدوير أو الخروج. "
            "لما الـ Singleton يمسك مرجع للـ Activity، بيمنع مجمع النفايات من مسحها، فبتفضل الشاشة بكل ما فيها من Views ورسوميات محبوسة في الرام. الحل إن الـ Singleton "
            "يمسك `applicationContext` فقط لو محتاج خدمات عامة."
        ),
        "best_answer_ar": (
            "المشكلة دي سببها الجوهري هو عدم تطابق فترات الحياة في الذاكرة أو ما نسميه Lifetime Mismatch. الـ Singleton مربوط بحقل ثابت أو بـ DI Scope على مستوى "
            "الـ Application، يعني عمره من عمر الـ Linux Process ككل ومبيموتش غير لما النظام يقفل التطبيق.\n\n"
            "على النقيض تماماً، الـ Activity كائن قصير العمر جداً وخاضع لتحولات دورة الحياة وتدوير الشاشة. والـ Activity في أندرويد مش كائن صغير، ده بيمتلك الـ PhoneWindow "
            "والـ DecorView وشجرة الـ Views كاملة بكل الصور والـ Drawables المحملة فيها. لما الـ Singleton يمسك Activity Context كـ Strong Reference، بيخلق مسار مباشر "
            "من GC Root حي للشاشة دي كلها.\n\n"
            "لو المستخدم دور الجهاز 5 مرات، بنلاقي 5 نسخ كاملة من الـ Activity محبوسة في الـ Heap، وده بياكل عشرات الميجابايت وبيفجر OutOfMemoryError. القاعدة الذهبية "
            "إن أي كائن Singleton محتاج Context لعمليات غير مرئية زي الداتابيز أو Shared Preferences، لازم يستخلص `context.applicationContext`، بينما العمليات المرئية "
            "لازم ترتبط بدورة حياة الشاشة نفسها."
        ),
        "deep_answer_ar": (
            "في تحليل تفريغ الذاكرة بملفات الـ HPROF عبر Android Studio Profiler أو Memory Analyzer Tool، تسريب الـ Activity بواسطة Singleton بيبان كواحد من أضخم "
            "الـ Dominator Nodes في الـ Heap. الـ Retained Size للشاشة المسربة بيتراوح عادة بين 20 لـ 50 ميجابايت؛ لأن حقل `mWindow` بيشير للـ `PhoneWindow`، وده "
            "بيشد معاه الـ `DecorView`، اللي بدوره بيشد كل الـ ViewGroups والـ Bitmaps ومصفوفات العرض الرسومية المتصلة بنظام الـ RenderNode.\n\n"
            "لما بنفحص المسار في LeakCanary، بنلاقي الـ Shortest Path to GC Root بيشاور على Static Field في الـ Singleton كعنصر حابس للـ Context. الحل الهندسي على "
            "مستوى الـ Architecture مش بس إننا ننادي `applicationContext`؛ لأن لو الكائن محتاج ينفخ واجهات أو يعرض تنبيهات، الـ `applicationContext` هيضرب "
            "`BadTokenException` لغياب الـ Window Token.\n\n"
            "في معمارية التطبيقات الحديثة بنحل ده بفصل المسؤوليات عبر Dependency Injection باستخدام Hilt: الخدمات العامة بنحقن فيها `@ApplicationContext` جوه كائنات "
            "`@Singleton`، والخدمات المرئية بنقيدها بـ `@ActivityScoped` وننظف مراجعها في `onDestroy`. وبنضيف قاعدة `StaticFieldLeak` في الـ CI Linting مع اختبارات "
            "Espresso بترصد عدم بقاء الشاشات في الـ ObjectWatcher لمنع وصول التسريبات دي للإنتاج. بالإضافة لكده، في الفرق الهندسية الكبيرة بنعمل Static Analysis مستمر باستخدام Android Lint وقواعد حظر الـ Static Fields غير المؤمنة لمنع حدوث هذا النمط من التسريبات في الـ CI."
        ),
    },
    "MEM-09": {
        "id": "MEM-09",
        "questionAr": "هل يمكن للـ ViewModel أو الـ Coroutine تسريب الذاكرة؟ وكيف يحدث ذلك؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": (
            "- تجنب الادعاء الخاطئ بأن استخدام `viewModelScope` يحمي تلقائياً من كافة تسريبات الذاكرة.\n"
            "- تحديد مراجع الـ Views والـ Activities المحتجزة والمهام المطلقة في نطاقات تدوم أطول من الشاشة.\n"
            "- تفسير آليات إلغاء المهام وتنظيف الـ Callbacks والتحقق من مسارات الاحتجاز عبر الـ Profiler."
        ),
        "why_it_matters_ar": (
            "الاعتقاد بأن الـ ViewModel أو الـ Coroutines محصنة ضد تسريبات الذاكرة هو وهم شائع. الـ ViewModel صُمم ليعيش بعد تدمير الـ Activity أثناء التدوير، "
            "حيث يُحفظ في `ViewModelStoreOwner`. إذا احتفظ الـ ViewModel بمرجع لشاشة، أو واجهة View، أو ViewBinding، أو مستمع مجهول يشير ضمنياً للشاشة، فإن شاشة "
            "الـ Activity القديمة ستتسرب بالكامل في الذاكرة طوال فترة بقاء الـ ViewModel. وبالمثل، إذا أُطلقت Coroutine في نطاق طويل الأجل مثل `GlobalScope` أو "
            "نطاق غير مدار ينفذ عملية طويلة أو حلقة لا نهائية، فإن الـ Continuation الخاص بها يلتقط كائن الشاشة ويحتجزه كـ GC Root حتى اكتمال المهمة أو إلغائها صراحة."
        ),
        "worked_example_ar": (
            "المقارنة بين كود يسرب الشاشة في ViewModel وكود ملتزم بالمعمارية النظيفة:\n"
            "```kotlin\n"
            "// ❌ كود يسرب الـ Activity عبر مرجع View ونطاق غير منظم:\n"
            "class BadViewModel : ViewModel() {\n"
            "    var titleView: TextView? = null // يسرب شجرة العرض عند التدوير!\n"
            "\n"
            "    fun startPolling() {\n"
            "        // نطاق غير مربوط بدورة الحياة يلتقط كائن الشاشة:\n"
            "        CoroutineScope(Dispatchers.IO).launch {\n"
            "            while (true) {\n"
            "                delay(3000)\n"
            "                updateData() // يلتقط المرجع الخارجي\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "}\n"
            "\n"
            "// ✅ كود آمن يعتمد على StateFlow و viewModelScope:\n"
            "class SafeViewModel(private val repository: DataRepository) : ViewModel() {\n"
            "    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)\n"
            "    val uiState: StateFlow<UiState> = _uiState.asStateFlow()\n"
            "\n"
            "    fun startPolling() {\n"
            "        // يتم إلغاء المهمة تلقائياً عند استدعاء onCleared():\n"
            "        viewModelScope.launch {\n"
            "            repository.pollData().collect { data ->\n"
            "                _uiState.value = UiState.Success(data)\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```\n"
            "باستخدام `viewModelScope` وتدفق البيانات الأحادي عبر `StateFlow`، تنقطع كافة المراجع وتُلغى العمليات تلقائياً عند مغادرة الشاشة نهائياً واستدعاء `onCleared()`."
        ),
        "trade_offs_ar": (
            "الـ ViewModel يجب أن يكون مستقلاً تماماً عن أي مراجع للواجهة، ويعتمد فقط على تصدير حالات غير قابلة للتعديل عبر `StateFlow`. إذا احتاج الـ ViewModel "
            "إلى سياق، يجب استخدام `AndroidViewModel` مع `getApplication()` فقط، وتفادي تمرير الـ Activity Context نهائياً. استخدام `viewModelScope` يضمن إلغاء "
            "المهام عند خروج المستخدم النهائي، لكنه لا يلغي المهام أثناء وجود التطبيق في الخلفية؛ لذا يجب جمع البيانات في الشاشة عبر `repeatOnLifecycle` لضمان "
            "وقف الاستهلاك عندما لا تكون الواجهة مرئية."
        ),
        "failure_modes_ar": (
            "الاحتفاظ بمرجع ViewBinding داخل ViewModel يسرب شجرة الـ Views وموارد الرسوميات مع أول دوران للجهاز. إطلاق مهام Coroutines في `GlobalScope` لا يراعي "
            "تدمير الشاشات ويبقي الخيوط الخلفية نشطة وتستهلك طاقة البطارية والذاكرة. جمع التدفقات (Collecting Flows) في الواجهة باستخدام `lifecycleScope.launch` "
            "العادي يستمر في استقبال البيانات وتحديث كائنات الواجهة حتى والشاشة في الخلفية، مما قد يسبب كراشات واستهلاك موارد بلا طائل."
        ),
        "production_perspective_ar": (
            "في بيئات الإنتاج، تُطبق حوكمة معمارية تمنع استقبال أي كائن من حزمة `android.view` داخل الـ ViewModels عبر قواعد Architecture Rules في Detekt أو Konsist. "
            "كما تُقيد مراقبة الـ Flows في الـ Fragments بـ `viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED)` لإيقاف التجميع تلقائياً عند انتقال الشاشة "
            "لوضع التوقف (Stop) وإعادة تشغيله عند العودة للظهور."
        ),
        "how_to_answer_ar": (
            "- **الإجابة المباشرة:** أجب بـ 'نعم بالتأكيد'، واشرح أن المناعة المزعومة مشروطة بالاستخدام المعماري الصحيح.\n"
            "- **سيناريو الـ ViewModel:** اشرح كيف يؤدي حفظ مرجع View أو Context إلى احتجاز الشاشة عبر الـ Configuration Changes.\n"
            "- **سيناريو الـ Coroutine:** وضّح كيف تحتجز الـ Continuation كائنات الـ Scope والـ Outer Class عند إطلاق مهام في نطاقات غير منضبطة."
        ),
        "talking_points_ar": (
            "ناقش توليد المترجم لكائنات الـ Continuation State Machine، وآلية عمل `SupervisorJob` المربوط بـ `viewModelScope`، ودور `repeatOnLifecycle` في تعليق "
            "وإلغاء جامعي التدفقات مقارنة بـ `launchWhenStarted` القديم."
        ),
        "follow_ups_ar": (
            "- **المحاور:** \"ليه `launchWhenStarted` اعتبروها Deprecated وتم استبدالها بـ `repeatOnLifecycle`؟\"\n"
            "  **المرشح:** \"لأن `launchWhenStarted` كانت بتعلق الـ Coroutine بس مبتلغيش جمع الـ Flow في الخلفية؛ فالـ Producer كان بيفضل شغال ويبعت بيانات للشاشة وهي في الـ Stop، وده بيستهلك CPU وبطارية وذاكرة. أما `repeatOnLifecycle(STARTED)` فبتلغي الـ Collector تماماً في onStop وتنشئه من جديد في onStart.\"\n\n"
            "- **المحاور:** \"هل تمرير Application Context داخل ViewModel يعتبر تسريباً؟\"\n"
            "  **المرشح:** \"لأ مش تسريب، لأن الـ Application Context بيعيش بعمر العملية كلها وهو نفس عمر الـ ViewModel أو أطول منه، لكن يفضل برمجياً حقن الـ Dependencies المسؤولة بدل تمرير الـ Context مباشرة للحفاظ على سهولة الاختبار.\""
        ),
        "self_check_ar": (
            "اشرح دورة حياة الـ ViewModel بالنسبة للـ Activity؛ بيّن كيف تحتجز الـ Continuation مراجع الشاشة؛ وقارن بين سلوك viewModelScope و GlobalScope."
        ),
        "references_ar": (
            "- [نظرة عامة على دورة حياة ViewModel](https://developer.android.com/topic/libraries/architecture/viewmodel) — إدارة النطاقات والاحتفاظ بالحالة.\n"
            "- [أفضل الممارسات لـ Coroutines في أندرويد](https://developer.android.com/kotlin/coroutines/coroutines-best-practices) — تجنب التسريبات وإدارة النطاقات.\n\n"
            "تمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13."
        ),
        "quick_answer_ar": (
            "نعم، الـ ViewModel والـ Coroutines ممكن يسربوا الذاكرة بسهولة لو تم استخدامهم بشكل غير صحيح. الـ ViewModel بيسرب لو احتفظ بمرجع لشاشة Activity أو View "
            "أو Callback؛ لأنه بيعيش بعد تدمير الشاشة عند التدوير. والـ Coroutine بتسرب لو انطلقت في `GlobalScope` أو نطاق غير مدار وعملت Capture لكائن الشاشة؛ فالخيط "
            "الخلفي بيفضل ماسكها لحد ما تخلص. الحل هو الالتزام بـ `viewModelScope` وتصدير الحالات عبر `StateFlow`."
        ),
        "best_answer_ar": (
            "الاعتقاد بأن الـ ViewModel أو الـ Coroutines ضد التسريب بشكل سحري هو فخ هندسي كبير. الـ ViewModel بطبيعه مصمم إنه يعيش بعد تدمير الـ Activity في "
            "الـ Configuration Changes عبر الـ ViewModelStoreOwner.\n\n"
            "لو الـ ViewModel مسك مرجع مباشر لـ Activity أو View أو ViewBinding، أو حتى مررنا له كائن Listener داخلي بيمسك الشاشة ضمنياً، فالـ Activity القديمة "
            "هتفضل محبوسة في الـ Heap مع كل تدويرة للجهاز لحد ما الـ ViewModel نفسه يتنظف، وده بيسرب شاشات كتيرة جداً.\n\n"
            "أما الـ Coroutines فبتسرب عن طريق الـ Scope والـ Closures. لو أطلقنا Coroutine في `GlobalScope` أو Scope مخصص ملوش علاقة بدورة الحياة، الـ Kotlin Compiler "
            "بيولد كائن Continuation شايل جواه حقل خفي بيشاور على الـ Outer Class. لو العملية دي بتعمل I/O طويل أو Delay، خيوط الـ Dispatcher النشطة بتتصرف كـ GC Roots "
            "وبتمنع مسح الشاشة طوال فترة العملية.\n\n"
            "الحل القياسي هو إن الـ ViewModel لا يمسك أي Views ويعتمد فقط على `StateFlow`، وكل المهام ترتبط بـ `viewModelScope` اللي بيلغي كل العمليات في `onCleared()`."
        ),
        "deep_answer_ar": (
            "تحت الكابوت، لما مترجم كوتلن بيعالج دوال الـ Coroutines المعلقة (Suspend Functions)، بيحول الكود لـ State Machine بتنفذ واجهة `Continuation`. الكائن "
            "ده بيحتفظ بمتغيرات التنفيذ وبمرجع ضمني `this$0` للكلاس الخارجي لو استخدمنا أي متغير أو دالة تابعة ليه. الخيوط النشطة في `Dispatchers.IO` أو `Default` "
            "بتشتغل كـ GC Roots دائمة طالما الـ Task شغالة. لو الـ Task دي مش مربوطة بـ Lifecycle Scope ومستمرة لدقائق، الشاشة بكل مراجعها بتفضل متثبتة في الـ Retained "
            "Dominator Tree ومش هتتمسح أبداً.\n\n"
            "في Jetpack، الـ `viewModelScope` بيحل المشكلة دي بربط `SupervisorJob` بدورة حياة الـ ViewModel. بمجرد ما المستخدم يقفل الشاشة نهائياً، الـ `ViewModelStore` "
            "بينادي `onCleared()`، وده بيبعت Cancel للـ Job ويفرغ كل الـ Continuations من الـ Dispatcher Queues. لكن حتى مع `viewModelScope`، لو المطور خزن View "
            "في حقل أو احتفظ بـ Callback، الـ Activity هتتسرب أثناء التدوير لأن الـ ViewModel عايش وماتنظفش.\n\n"
            "وعلى مستوى الواجهة، جمع البيانات عبر الـ Flow داخل `lifecycleScope.launch` بدون وعي بيسرب وقت المعالج في الخلفية. الحل الهندسي هو استخدام "
            "`viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED)`، وده بيستخدم ميكانيكا الـ Cancellation التلقائي لإلغاء الـ Collector coroutine "
            "فور انتقال الشاشة لـ `onStop`، وإعادة تشغيلها في `onStart`، مما يضمن أمان الذاكرة والبطارية بالكامل دون أي تسريبات."
        ),
    },
    "MEM-10": {
        "id": "MEM-10",
        "questionAr": "ما هو الـ ANR (تطبيق لا يستجيب)؟ وما هي أسبابه الأكثر شيوعاً؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": (
            "- تعريف الـ ANR كفشل في استجابة خيط الواجهة يخضع لمهلات زمنية محددة من النظام، وليس مجرد كراش برمجي.\n"
            "- تشخيص انسداد خيط الواجهة الرئيسي، وتنافس الأقفال (Lock Contention)، وانتظار الـ Binder، والمهام الثقيلة في أجهزة الاستقبال والخدمات.\n"
            "- تحليل ملفات الـ traces.txt وأدلة التوقيت وسجلات النظام قبل اقتراح الحلول الهندسية."
        ),
        "why_it_matters_ar": (
            "خطأ تطبيق لا يستجيب (ANR - Application Not Responding) هو آلية حماية على مستوى نظام تشغيل أندرويد عبر `ActivityManagerService` لمراقبة سرعة استجابة "
            "التطبيقات للمستخدم. عندما يعجز التطبيق عن معالجة حدث إدخال (لمس الشاشة أو ضغط الأزرار) خلال 5 ثوانٍ، أو يستغرق BroadcastReceiver أكثر من 10 إلى 20 "
            "ثانية (60 ثانية في الخلفية)، أو تستغرق الخدمة (Service) أكثر من 20 ثانية (200 ثانية في الخلفية)، يقوم النظام بتعليق العملية، وتسجيل تقرير traces.txt "
            "كامل، وإظهار نافذة ANR للمستخدم ليقرر إغلاق التطبيق. أشهر الأسباب تشمل تنفيذ عمليات قراءة وكتابة القرص (Disk I/O) أو استعلامات قواعد البيانات على خيط "
            "الواجهة، وإجراء طلبات الشبكة، والعمليات الحسابية المعقدة، والانسداد المتبادل للأقفال (Deadlocks)، وتوقف خيوط الـ Binder IPC."
        ),
        "worked_example_ar": (
            "المقارنة بين كود يسبب ANR فوري وكود معالج في الخلفية:\n"
            "```kotlin\n"
            "// ❌ كود يسبب ANR: قراءة ملف وتحليل JSON على خيط الواجهة في onCreate:\n"
            "class BadSettingsActivity : AppCompatActivity() {\n"
            "    override fun onCreate(savedInstanceState: Bundle?) {\n"
            "        super.onCreate(savedInstanceState)\n"
            "        // حظر خيط الـ Main Thread بعمليات قرص ومعالجة ثقيلة:\n"
            "        val rawConfig = File(filesDir, \"config.json\").readText() // Disk I/O!\n"
            "        val parsed = JSONObject(rawConfig) // CPU parsing!\n"
            "        applyConfig(parsed)\n"
            "    }\n"
            "}\n"
            "\n"
            "// ✅ كود آمن: نقل العمليات غير المرئية إلى Dispatchers.IO:\n"
            "class GoodSettingsActivity : AppCompatActivity() {\n"
            "    override fun onCreate(savedInstanceState: Bundle?) {\n"
            "        super.onCreate(savedInstanceState)\n"
            "        lifecycleScope.launch {\n"
            "            val parsed = withContext(Dispatchers.IO) {\n"
            "                val rawConfig = File(filesDir, \"config.json\").readText()\n"
            "                JSONObject(rawConfig)\n"
            "            }\n"
            "            applyConfig(parsed)\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```\n"
            "بنقل قراءة الملف وتحليل الـ JSON إلى `Dispatchers.IO`، يظل طابور رسائل خيط الواجهة (Looper) حراً لمعالجة لمسات المستخدم ورسم الفريمات دون أي تأخير."
        ),
        "trade_offs_ar": (
            "نقل العمليات لخيوط الخلفية عبر `Dispatchers.IO` يحمي خيط الواجهة من الـ ANR، ولكنه يتطلب إدارة صحيحة لحالات التحميل (Loading States) والتعامل مع "
            "العمليات غير المتزامنة وتفادي سباق البيانات (Race Conditions). تشغيل أدوات المراقبة مثل StrictMode في نسخ التطوير يكشف انتهاكات القرص والشبكة فوراً، "
            "لكنه يسبب وقفات فحص طفيفة يجب تعطيلها تماماً في نسخ الإنتاج النهائية."
        ),
        "failure_modes_ar": (
            "استدعاء `SharedPreferences.apply()` بكثافة قد يبدو آمناً، لكن عند تدمير الشاشة أو إيقاف الخدمة ينتظر النظام تفريغ كل المهام على القرص متزامناً مما قد "
            "يسبب ANR خفي. طلب خدمة نظام عبر Binder (IPC) قد يعلق التطبيق إذا كانت الخدمة الحكومية مهنجة أو تحت ضغط شديد. استخدام أقفال `synchronized` المشتركة "
            "بين خيط خلفي بطيء وخيط الواجهة يؤدي إلى Lock Contention وتجميد الواجهة حتى ينتهي الخيط الخلفي."
        ),
        "production_perspective_ar": (
            "في المشروعات الكبيرة، نراقب مؤشر الـ ANR Rate في Google Play Console Android Vitals للتأكد من بقائه أقل من النسبة الحرجة 0.47%. نستخدم أدوات APM "
            "ومكتبات تتبع الـ Main Thread Lag لرصد بطء الفريمات قبل تحوله لـ ANR. عند وقوع ANR في الإنتاج، نقوم بتنزيل ملف الـ Traces وفحص حالة الخيط الرئيسي لمعرفة "
            "السطر المتسبب بدقة."
        ),
        "how_to_answer_ar": (
            "- **التعريف بالمهلات:** عرّف الـ ANR بمهلاته الرسمية (Input 5s, Broadcast 10-20s, Service 20s) وبيّن أنه آلية حماية من النظام.\n"
            "- **الأسباب الشائعة:** اذكر عمليات الـ I/O والشبكة، وتنافس الأقفال (Lock Contention)، وتوقف استدعاءات الـ Binder.\n"
            "- **أدوات التشخيص:** اشرح كيفية فحص ملف `/data/anr/traces.txt` والتحقق من حالة خيط الـ main والـ Locks المسببة للانسداد."
        ),
        "talking_points_ar": (
            "ناقش تفاصيل ملف الـ traces.txt (حالات الخيوط RUNNABLE, BLOCKED, WAITING)، واستخدام StrictMode للرصد المبكر، والفرق بين Foreground و Background BroadcastReceiver "
            "timeouts، وأثر الـ GC Thrashing في إشعال الـ ANR."
        ),
        "follow_ups_ar": (
            "- **المحاور:** \"هل ممكن الـ ANR يحصل والتطبيق مبيعملش أي I/O على الـ Main Thread؟\"\n"
            "  **المرشح:** \"أيوة جداً؛ أشهر حالتين هما تنافس الأقفال (Lock Contention) لما الـ Main Thread يحاول يدخل بلوك `synchronized` ماسكه Background Thread شغال، أو حالة الـ Binder Transaction لما التطبيق ينادي خدمة تابعة للنظام والخدمة تعلق في الـ IPC.\"\n\n"
            "- **المحاور:** \"إيه هو الـ StrictMode وإزاي بيساعدنا نتفادى الـ ANR؟\"\n"
            "  **المرشح:** \"الـ StrictMode أداة تطوير في أندرويد بنفعلها في الـ Debug، بتراقب خيط الواجهة وبترمي تحذيرات أو تفجر كراش لو الكود عمل قراءة أو كتابة على القرص أو حاول يفتح اتصال شبكة على الـ Main Thread.\""
        ),
        "self_check_ar": (
            "اذكر المهلات الزمنية الثلاث للـ ANR؛ اشرح سيناريو حدوث ANR بسبب الأقفال؛ وبيّن كيفية فحص traces.txt."
        ),
        "references_ar": (
            "- [دليل تشخيص وحل أخطاء ANR](https://developer.android.com/topic/performance/vitals/anr) — مهلات النظام وكيفية قراءة التقارير.\n"
            "- [استخدام StrictMode لاكتشاف بطء الخيوط](https://developer.android.com/reference/android/os/StrictMode) — مراقبة عمليات القرص والشبكة.\n\n"
            "تمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13."
        ),
        "quick_answer_ar": (
            "الـ ANR هو خطأ تطبيقي يتدخل فيه نظام أندرويد لما خيط الواجهة الرئيسي يعجز عن معالجة مدخلات المستخدم خلال 5 ثوانٍ، أو لما BroadcastReceiver يطول عن "
            "10 لـ 20 ثانية، أو Service تزيد عن 20 ثانية. أسبابه الشائعة هي تشغيل عمليات قراءة وكتابة القرص، أو استعلامات قواعد البيانات، أو طلبات الشبكة، أو تنافس "
            "الأقفال مع خيوط الخلفية، أو بطء دورات الـ GC المتكررة."
        ),
        "best_answer_ar": (
            "الـ ANR أو Application Not Responding مش مجرد كراش عادي؛ ده Watchdog Timer من نظام تشغيل أندرويد بيراقب استجابة التطبيق للمستخدم عبر `ActivityManagerService`.\n\n"
            "النظام حاطط مهلات محددة وصارمة: لو المستخدم لمس الشاشة والتطبيق مردش خلال 5 ثوانٍ، أو لو مسجل BroadcastReceiver في الـ Foreground وخد أكتر من 10 لـ 20 "
            "ثانية، أو Service في الـ Foreground استمرت أكتر من 20 ثانية، النظام بيجمد العملية ويطلع Dialog للمستخدم يخيره يقفل التطبيق ولا يستنى.\n\n"
            "السبب الهندسي هو انسداد طابور رسائل الـ Main Thread Looper. ده بيحصل لما المطور يعمل Disk I/O متزامن، أو يقرأ Shared Preferences ضخمة، أو يعمل استعلام Room، "
            "أو يفك ملف JSON كبير على خيط الواجهة. وكمان بيحصل بسبب مشاكل الـ Concurrency، زي إن خيط الواجهة يكون مستني Lock ماسكه خيط خلفي بطيء.\n\n"
            "عشان نمنع الـ ANR، بنلتزم بنقل كل الشغل الثقيل لـ `Dispatchers.IO` وبنراقب مؤشرات الـ ANR Rate في Google Play Console للتأكد من إنها أقل من 0.47%."
        ),
        "deep_answer_ar": (
            "في تشخيص الـ ANRs المتقدمة على مستوى الإنتاج، المرجع الأساسي لينا هو ملف `/data/anr/traces.txt` وتقارير Android Vitals. لما الـ ANR بيحصل، الـ Linux Kernel "
            "بيعمل Dump لكل الخيوط بحالاتها الحالية. أول حاجة بنعملها هي فحص خيط الـ `main`: لو لقينا حالته `BLOCKED`، بنبص فوراً على الـ Monitor Lock اللي مستنيه "
            "(مثلاً: `waiting to lock <0x...> held by thread 14`). ده بيكشف تنافس الأقفال أو مشكلة Priority Inversion، حيث خيط خلفي قليل الأولوية واخد قفل وعطل خيط الواجهة.\n\n"
            "أما لو لقينا الـ `main` thread حالته `NATIVE` في سطر `android.os.BinderProxy.transact`، فالمشكلة مش في كودنا أصلاً، بل في انتظار استجابة IPC من خدمة تابعة "
            "لنظام أندرويد (زي LocationManagerService أو Telephony) والخدمة دي معلقة في الـ System Server. كمان بنبص على الـ CPU Usage في ترويسة التقرير: لو المعالج "
            "شغال 100% وفي استهلاك عالي لعمليات الـ GC أو الـ Memory Paging، بنعرف إن الـ ANR سببه الحقيقي هو Memory Pressure وتوقفات تنظيف متواصلة خنقت المعالج.\n\n"
            "كـ Staff Engineers، بنحمي الكود استباقياً بتفعيل `StrictMode.ThreadPolicy` في الـ Debug Builds لرصد أي Disk Reads أو Network Calls فوراً، وبنستبدل "
            "الـ Shared Preferences بـ Jetpack DataStore المعتمد بالكامل على الـ Coroutines، وبنلغي أي أقفال متزامنة بين الـ Main Thread وخيوط المعالجة الخلفية لتأمين الواجهة."
        ),
    },
    "MEM-11": {
        "id": "MEM-11",
        "questionAr": "لماذا يجب تحرير مراجع ViewBinding في الـ Fragment مع انتهاء دورة حياة الواجهة؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": (
            "- التمييز الدقيق بين دورة حياة كائن الـ Fragment ودورة حياة واجهته الرسومية (View Lifecycle)، وشرح شجرة المراجع المحتجزة.\n"
            "- تصفير مرجع الـ Binding في `onDestroyView()` ومراقبة تدفقات الواجهة بالارتباط بـ `viewLifecycleOwner`.\n"
            "- التعامل السليم مع الـ Callbacks غير المتزامنة بعد تدمير الواجهة دون إخفاء عيوب دورة الحياة."
        ),
        "why_it_matters_ar": (
            "تعد الـ Fragments في أندرويد فريدة بامتلاكها دورتي حياة منفصلتين: دورة حياة كائن الـ Fragment نفسه، ودورة حياة الواجهة الرسومية التابعة له (`viewLifecycleOwner`). "
            "عندما ينتقل المستخدم إلى شاشة جديدة وتوضع الـ Fragment الحالية في الـ Backstack (عبر `addToBackStack`)، يقوم النظام بتدمير الواجهة الرسومية عبر استدعاء "
            "`onDestroyView()` لتوفير الذاكرة، ولكنه يحتفظ بكائن الـ Fragment حياً في الذاكرة للحفاظ على حالته. كائن الـ ViewBinding المولد يحتفظ بمراجع قوية لكل عناصر "
            "الواجهة وشجرة الـ Views بالكامل. إذا لم يتم تصفير مرجع الـ Binding في `onDestroyView`، تظل شجرة الواجهة المدمرة بكل صورها ومستمعيها محبوسة في الـ Heap، "
            "مما يتسبب في تسريب ذاكرة ضخم يتضاعف مع كل انتقال في الـ Backstack."
        ),
        "worked_example_ar": (
            "النمط المعماري السليم لإدارة ViewBinding في الـ Fragment:\n"
            "```kotlin\n"
            "// ❌ كود يسرب شجرة الـ Views في الـ Backstack:\n"
            "class LeakyFragment : Fragment(R.layout.fragment_detail) {\n"
            "    private lateinit var binding: FragmentDetailBinding // يظل ممسوكاً بعد onDestroyView!\n"
            "\n"
            "    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {\n"
            "        super.onViewCreated(view, savedInstanceState)\n"
            "        binding = FragmentDetailBinding.bind(view)\n"
            "    }\n"
            "}\n"
            "\n"
            "// ✅ النمط الصحيح: استخدام Nullable Backing Property:\n"
            "class SafeFragment : Fragment(R.layout.fragment_detail) {\n"
            "    private var _binding: FragmentDetailBinding? = null\n"
            "    // خاصية للقراءة صالحة فقط بين onCreateView و onDestroyView:\n"
            "    private val binding get() = _binding!!\n"
            "\n"
            "    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {\n"
            "        super.onViewCreated(view, savedInstanceState)\n"
            "        _binding = FragmentDetailBinding.bind(view)\n"
            "    }\n"
            "\n"
            "    override fun onDestroyView() {\n"
            "        super.onDestroyView()\n"
            "        // تصفير المرجع فوراً لتحرير شجرة الواجهة لمجمع النفايات:\n"
            "        _binding = null\n"
            "    }\n"
            "}\n"
            "```\n"
            "بتصفير `_binding` في `onDestroyView()`، تنقطع سلسلة المراجع وتتحرر شجرة الواجهة بالكامل من الـ Heap بينما تنتظر الـ Fragment في الـ Backstack بأمان."
        ),
        "trade_offs_ar": (
            "استخدام نمط الـ Nullable Backing Property (`_binding` و `binding`) يفرض كتابة كود مكرر (Boilerplate) في كل Fragment، لكنه الضمان الهندسي الأقوى "
            "لمنع تسريب شجرة الواجهة في الـ Backstack. يمكن تبسيط الكود باستخدام Custom Property Delegates أو مكتبات مساعدة تعتمد على مراقبة "
            "`viewLifecycleOwner.lifecycle` وتصفير المرجع آلياً عند حدث `ON_DESTROY`. في المقابل، التحول الكامل إلى Jetpack Compose يلغي الـ XML ViewBinding "
            "ودورة حياة الـ View التقليدية نهائياً، مما يقضي على هذه الفئة من التسريبات من جذورها."
        ),
        "failure_modes_ar": (
            "الاحتفاظ بمرجع ViewBinding في Fragment على الـ Backstack يسرب عشرات الـ Views والـ Bitmaps ومستمعي الأحداث، مما يرفع الذاكرة بمقدار 10 إلى 30 ميجابايت "
            "لكل شاشة في المكدس. محاولة الوصول إلى `binding` بعد استدعاء `onDestroyView` (مثلاً من خلال Callback شبكة متأخر) يرمي استثناء `NullPointerException` "
            "أو `IllegalStateException` حتمي؛ والحل الصحيح ليس الإبقاء على الـ Binding حياً، بل إلغاء مهام الشبكة أو التأكد من دورة حياة الواجهة."
        ),
        "production_perspective_ar": (
            "في التطبيقات الإنتاجية، تُعتبر تسريبات الـ ViewBinding من أكثر التسريبات التي يرصدها LeakCanary في شاشات الـ Fragments. يتم التحقق من تصفير الـ Binding "
            "تلقائياً عبر كتابة Property Delegate مخصص يتصل بـ `viewLifecycleOwner.lifecycle`، وتفعيل قواعد الفحص في Android Lint للتحذير من استخدام `lateinit var binding` "
            "داخل الـ Fragments."
        ),
        "how_to_answer_ar": (
            "- **فصل دورتي الحياة:** ابدأ بشرح الفارق بين دورة حياة كائن الـ Fragment ودورة حياة الـ View (`viewLifecycleOwner`).\n"
            "- **سيناريو الـ Backstack:** وضّح ماذا يحدث للواجهة عندما تنتقل الشاشة للـ Backstack واستدعاء `onDestroyView` مع بقاء كائن الـ Fragment.\n"
            "- **الحل العملي:** اشرح نمط الـ Backing Property وتصفير `_binding = null`، واذكر كيف يقضي Compose على المشكلة تماماً."
        ),
        "talking_points_ar": (
            "ناقش حجم الشجرة المحتجزة للـ Views، ومخاطر استدعاء الـ Binding في الـ Asynchronous Callbacks بعد تدمير الواجهة، وتصميم الـ Lifecycle-aware Property Delegates، "
            "ومقارنة نموذج Views بنموذج Jetpack Compose الخالي من شجرة الـ Views."
        ),
        "follow_ups_ar": (
            "- **المحاور:** \"ليه بنحتاج نعمل ده في الـ Fragment ومش بنحتاجه في الـ Activity؟\"\n"
            "  **المرشح:** \"لأن الـ Activity ليها دورة حياة واحدة متطابقة مع الواجهة بتاعتها؛ لما الشاشة بتتدمر في `onDestroy` كائن الـ Activity كله بواجهته بيتحرر مع بعض. أما الـ Fragment فممكن تفضل حية في الـ Backstack بعد ما واجهتها تتدمر في `onDestroyView`.\"\n\n"
            "- **المحاور:** \"لو استلمت استجابة API في Coroutine بعد ما الشاشة دخلت الـ Backstack وحاولت أكتب `binding.textView.text = data`، إيه اللي هيحصل؟\"\n"
            "  **المرشح:** \"لو متبع النمط السليم ومصفر الـ `_binding`، الكود هيرمي `NullPointerException` فوري؛ وعشان نتفادى ده، لازم نربط المراقبة بـ `viewLifecycleOwner.repeatOnLifecycle(STARTED)` عشان الـ Coroutine تتوقف تلقائياً ومتحاولش تلمس الـ View المدمرة.\""
        ),
        "self_check_ar": (
            "فرّق بين عمر كائن الـ Fragment وعمر واجهته؛ اشرح أثر الـ Backstack على الذاكرة؛ واكتب نمط الـ Backing Property الصحيح."
        ),
        "references_ar": (
            "- [استخدام ViewBinding في الـ Fragments](https://developer.android.com/topic/libraries/view-binding#fragments) — التوثيق الرسمي لتصفير المراجع في onDestroyView.\n"
            "- [دورة حياة الـ Fragment](https://developer.android.com/guide/fragments/lifecycle) — استقلال دورة حياة الواجهة عن كائن الشاشة.\n\n"
            "تمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13."
        ),
        "quick_answer_ar": (
            "الـ Fragment في أندرويد بتمتلك دورتين حياة منفصلتين: دورة حياة الكائن نفسه ودورة حياة الواجهة الرسومية (View). لما الشاشة بتدخل الـ Backstack، النظام "
            "بيستدعي `onDestroyView` ويدمر الواجهة لتوفير الرام، لكن كائن الـ Fragment بيفضل حي. كائن الـ ViewBinding بيمسك شجرة الـ Views كلها؛ فلو مفرغناش المرجع "
            "في `onDestroyView`، شجرة الواجهة كلها هتتسرب في الذاكرة."
        ),
        "best_answer_ar": (
            "السبب الجوهري هو معمارية الـ Fragment الفريدة في أندرويد اللي بتفصل بين عمر الكائن وعمر الواجهة الرسومية الخاصة بيه عبر `viewLifecycleOwner`.\n\n"
            "لما بنعمل انتقال لشاشة تانية ونضيف الـ Fragment الحالية في الـ Backstack عبر `addToBackStack`، النظام بيستدعي `onDestroyView()` عشان يدمر الواجهة الرسومية "
            "ويوفر الرام، لكنه بيحتفظ بكائن الـ Fragment نفسه في الـ FragmentManager عشان يحتفظ بالحالة والبيانات.\n\n"
            "كائن الـ ViewBinding المولد مش مجرد مؤشر بسيط، ده شايل مراجع قوية للـ Root View وكل الـ Widgets والنصوص والصور والـ Listeners اللي تحتها. لو المطور عرف "
            "الـ Binding كـ `lateinit var` وسابه بعد `onDestroyView`، الـ Fragment اللي قاعدة في الـ Backstack هتفضل شادة شجرة الواجهة المدمرة دي كلها في الـ Heap.\n\n"
            "عشان كده النمط القياسي الإجباري هو الـ Nullable Backing Property: بنعرف `_binding` كـ Nullable، وبنخليه `null` في `onDestroyView()`، عشان نسمح للـ "
            "Garbage Collector إنه يحرر مساحة الشاشة بالكامل أثناء انتظارها في الـ Backstack."
        ),
        "deep_answer_ar": (
            "في فحص الـ HPROF Dumps بـ LeakCanary، تسريب الـ Fragment ViewBinding بيمثل أعلى نسبة تسريبات الـ Views في تطبيقات أندرويد المعتمدة على الـ XML. "
            "الـ Retained Size للـ ViewBinding المسرب بيكون ضخم جداً، لأن الـ Root ViewGroup مش بس ماسك الـ Views، بل ماسك الـ Context اللي بيشاور على الـ Activity، "
            "وماسك الـ RecyclerView Adapter وماسك الـ Drawables اللي شايلة بكسلات الـ Bitmaps، فالتسريب بيحتجز عشرات الميجابايت مع كل شاشة على الـ Backstack.\n\n"
            "لتفادي كتابة كود مكرر في كل Fragment، الفرق الهندسية المتقدمة بتعمل Custom ViewBinding Property Delegate بيتصل بـ `viewLifecycleOwner.lifecycle`. "
            "الـ Delegate بيسجل Observer بيستمع لحدث `Lifecycle.Event.ON_DESTROY` الخاص بالواجهة، وأول ما الحدث يتنادى بيصفر المرجع تلقائياً بدون تدخل يدوي من المطور، "
            "وبيرمي `IllegalStateException` واضحة لو الكود حاول يلمس الـ Binding بعد تدمير الواجهة.\n\n"
            "والجدير بالذكر إن في العصر الحديث مع Jetpack Compose، المعضلة دي انتهت تماماً؛ لأن الـ Composable Functions مبتبنيش XML View Hierarchy معقدة ولا "
            "بتعتمد على ViewBinding، بل بتعتمد على State Recomposition، وبالتالي مفيش أي شجرة Views بتتسرب في الـ Backstack نهائياً. "
            "وفي الفرق الكبيرة بنفعل قواعد Detekt و Konsist لمنع أي كلاس Fragment من امتلاك حقل binding بدون تصفيره في onDestroyView."
        ),
    },
    "MEM-12": {
        "id": "MEM-12",
        "questionAr": "كيف تتسبب الـ Callbacks والـ Handler والمراقبون (Observers) والمراجع الثابتة في تسريب الذاكرة؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": (
            "- تتبع سلاسل المراجع الصريحة والضمنية الممتدة من الـ GC Roots طويلة الأجل إلى شاشات العرض المؤقتة.\n"
            "- اختيار استراتيجيات التناظر في دورة الحياة (Lifecycle Symmetry)، والمراقبة الواعية لدورة الحياة، وإلغاء المهام المعلقة.\n"
            "- الفصل الدقيق بين المنع الجذري لتسريب الذاكرة ومجرد إخفاء الاستثناءات أو كتم الأخطاء البرمجية."
        ),
        "why_it_matters_ar": (
            "تعتبر هذه الأنماط الأربعة من الكلاسيكيات المسببة لتسريب الذاكرة في أندرويد نتيجة احتجاز مراجع ضمنية (Implicit References):\n"
            "1. الكلاسات الداخلية غير الثابتة (Non-static Inner Classes) والـ Anonymous Listeners والـ Lambdas تحتفظ برابط خفي (`this$0`) يشير للكلاس الخارجي (الـ Activity).\n"
            "2. الـ Handler: عند إرسال رسالة مؤجلة بـ `postDelayed`، تُحفظ الرسالة في `MessageQueue` الخاص بالـ Main Looper؛ والرسالة تمسك بالـ Handler الذي يمسك بالـ Activity عبر `this$0`. يظل مسار الوصول متصلاً من الـ Thread (GC Root) حتى انقضاء مهلة الرسالة.\n"
            "3. الـ Observers والـ Listeners: تسجيل شاشة في EventBus أو LocationManager أو Repository دون إلغاء التسجيل المتناظر في `onStop` أو `onDestroy` يبقي الشاشة متصلة بالناشر للأبد.\n"
            "4. المراجع الثابتة (Static References): أي متغير ثابت في Companion Object أو Static Field يشير لشاشة أو View يرتبط بالـ ClassLoader ويظل مسرباً حتى موت العملية."
        ),
        "worked_example_ar": (
            "المقارنة بين كود يسرب الشاشة عبر Handler وكود آمن يعتمد على الـ Coroutines ودورة الحياة:\n"
            "```kotlin\n"
            "// ❌ كود يسرب الـ Activity عبر Handler برابط مجهول ومؤجل:\n"
            "class LeakyActivity : AppCompatActivity() {\n"
            "    private val handler = Handler(Looper.getMainLooper())\n"
            "\n"
            "    override fun onCreate(savedInstanceState: Bundle?) {\n"
            "        super.onCreate(savedInstanceState)\n"
            "        // رسالة مؤجلة لمدة دقيقة تمسك بالـ Activity عبر this$0:\n"
            "        handler.postDelayed({\n"
            "            updateTitle() // مرجع ضمني لـ LeakyActivity\n"
            "        }, 60_000) // تسريب الشاشة لمدة دقيقة كاملة بعد الخروج أو التدوير!\n"
            "    }\n"
            "}\n"
            "\n"
            "// ✅ كود آمن يعتمد على lifecycleScope والإلغاء التلقائي:\n"
            "class SafeActivity : AppCompatActivity() {\n"
            "    override fun onCreate(savedInstanceState: Bundle?) {\n"
            "        super.onCreate(savedInstanceState)\n"
            "        lifecycleScope.launch {\n"
            "            delay(60_000)\n"
            "            updateTitle() // يتم إلغاء الـ Coroutine وتفريغ المرجع فور إغلاق الشاشة\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```\n"
            "باستخدام `lifecycleScope`، يتم إلغاء الـ Coroutine تلقائياً عند تدمير الشاشة وإسقاط المرجع من طابور الـ Looper دون ترك أي مراجع معلقة."
        ),
        "trade_offs_ar": (
            "استخدام الـ `WeakReference<Activity>` داخل الـ Listeners والـ Handlers يمنع تسريب الذاكرة ولكنه يفرض فحص القيمة ضد `null` قبل كل استخدام، "
            "وقد يفشل الإجراء بصمت إذا دُمرت الشاشة قبل وصول الحدث. الحل المعماري الأفضل هو الحفاظ على التناظر التام (Symmetry): التسجيل في `onStart` "
            "يقابله إلغاء في `onStop`، والتسجيل في `onCreate` يقابله إلغاء في `onDestroy`. في الكود الحديث، استبدال الـ Handlers والـ Callbacks بـ Coroutines "
            "و Flows يوفر إدارة تلقائية وأكثر أماناً."
        ),
        "failure_modes_ar": (
            "رسالة مؤجلة لمدة 10 دقائق في Handler تسرب الشاشة بالكامل لمدة 10 دقائق بعد خروج المستخدم. نسيان إلغاء تسجيل BroadcastReceiver في `onStop` يفجر "
            "تسريباً للذاكرة وقد يرمي استثناء `IntentReceiverLeaked` في سجلات النظام. المتغيرات الثابتة التي تحتفظ بـ Views أو Activities تسبب تسريباً دائماً "
            "لا يمكن استرداده أبداً حتى إعادة تشغيل التطبيق."
        ),
        "production_perspective_ar": (
            "في الأنظمة الحديثة، نلزم الفرق الهندسية باستبدال كائنات الـ Handler القديمة بـ Coroutines المرتبطة بنطاق دورة الحياة. وفي الحالات النادرة التي "
            "تتطلب استخدام الـ Handler، يُفرض استخدام Static Nested Class مع `WeakReference` واستدعاء `handler.removeCallbacksAndMessages(null)` داخل `onDestroy` "
            "لضمان إفراغ طابور الرسائل تماماً."
        ),
        "how_to_answer_ar": (
            "- **شرح المرجع الضمني:** وضّح كيف يولد المترجم حقل `this$0` الخفي في الـ Anonymous Classes والـ Lambdas.\n"
            "- **تحليل الـ Handler:** اشرح مسار الوصول: Active Thread -> Looper -> MessageQueue -> Message -> Handler -> Activity.\n"
            "- **الحلول الهندسية:** اشرح التناظر في دورة الحياة (Symmetry)، واستخدام المراجع الضعيفة، والاستبدال بـ Coroutines."
        ),
        "talking_points_ar": (
            "ناقش كود الـ Bytecode وتوليد `this$0`، وإعادة تدوير كائنات `Message` في الـ Android Looper عبر الـ Object Pool الداخلي، ودور LeakCanary في رصد "
            "حقول `MessageQueue.mMessages`."
        ),
        "follow_ups_ar": (
            "- **المحاور:** \"ليه الـ Kotlin Lambda ممكن تسرب الشاشة بينما دالة static في Java مبتسربش؟\"\n"
            "  **المرشح:** \"لأن الـ Lambda في Kotlin لو لمست أي دالة أو متغير تابع للكلاس الخارجي، المترجم بيعتبرها 'Capturing Lambda' وبيعمل Capture لمرجع `this` كحقل داخل كائن الـ Function، بينما الـ Static Method معندهاش أي مرجع للكائن الخارجي إطلاقاً.\"\n\n"
            "- **المحاور:** \"لو مضطرين نستخدم Handler في كود قديم، إزاي نمنع التسريب بنسبة 100%؟\"\n"
            "  **المرشح:** \"بنعمل الـ Handler كـ `static class` داخلي ونمرر الـ Activity جواه في `WeakReference<Activity>`، وفي دالة `onDestroy()` بنستدعي إجبارياً `handler.removeCallbacksAndMessages(null)` عشان نفرغ كل الرسائل المؤجلة من الـ MessageQueue.\""
        ),
        "self_check_ar": (
            "اشرح كيف يلتقط الـ Lambda مرجع `this$0`؛ ارسم سلسلة المراجع الممتدة من الـ Looper؛ واذكر سطر الكود الحاسم لتنظيف الـ Handler."
        ),
        "references_ar": (
            "- [التعامل مع الـ Handlers والرسائل المؤجلة](https://developer.android.com/reference/android/os/Handler) — التوثيق الرسمي لإدارة الرسائل والـ Loopers.\n"
            "- [دليل تجنب التسريبات في المراقبين والمستمعين](https://developer.android.com/topic/performance/memory) — أفضل ممارسات إدارة المراجع.\n\n"
            "تمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13."
        ),
        "quick_answer_ar": (
            "الـ Callbacks والـ Handlers والـ Listeners بتسرب الذاكرة لأن الكلاسات الداخلية والـ Lambdas بتحتفظ برابط خفي للكلاس الخارجي (`this$0`). لما بنبعت "
            "رسالة مؤجلة لـ Handler أو نسجل Listener في مكان طويل الأجل ومانلغيهوش، كائن الـ Activity بيفضل مشدود لـ GC Root نشط ومجمع النفايات مبيقدرش يمسحه. "
            "الحل هو التناظر في دورة الحياة، وتفريغ رسائل الـ Handler بـ `removeCallbacksAndMessages`، أو الاعتماد على Coroutines دورة الحياة."
        ),
        "best_answer_ar": (
            "السبب المشترك في كل الحالات دي هو نشوء مسار مراجع غير مقصود بيربط كائن قصير العمر زي الـ Activity بـ GC Root دائم ومستمر في الذاكرة.\n\n"
            "في الـ Java والـ Kotlin، أي Anonymous Class أو Lambda بتستخدم أي عنصر من الكلاس الخارجي، المترجم بيولد جواها حقل خفي اسمه `this$0` بيشير لكائن الـ Activity. "
            "لو سجلنا الـ Callback ده في Singleton أو EventBus أو LocationManager ومنسينا نلغي تسجيله في `onStop` أو `onDestroy`، الـ Publisher ده هيفضل ماسك الشاشة للأبد.\n\n"
            "في حالة الـ Handler، الموضوع أدق: لما بننادي `handler.postDelayed`، الـ Message بتدخل طابور الـ `MessageQueue` بتاع الـ Main Thread. الـ Thread شغال دايماً "
            "كـ GC Root، والـ Message ماسكة الـ Handler، والـ Handler ماسك الـ Activity. فلو الرسالة مؤجلة لدقيقة والمستخدم خرج بعد ثانيتين، الشاشة هتفضل مسربة في "
            "الذاكرة دقيقة كاملة.\n\n"
            "الحل الهندسي بيعتمد على تصفية الطوابير بـ `removeCallbacksAndMessages(null)` في `onDestroy`، أو استخدام `WeakReference`، والأفضل في أندرويد الحديث هو "
            "استبدال كل ده بـ `lifecycleScope` اللي بيلغي العمليات آلياً."
        ),
        "deep_answer_ar": (
            "تحت الكابوت، الـ Android Looper بيعتمد على Native MessageQueue مدعوم بـ Linux `epoll` لمراقبة وصول الرسائل والأحداث. كائنات `android.os.Message` "
            "بيعاد تدويرها عبر Global Object Pool داخلي في النظام. لما بتعمل `postDelayed(runnable, delay)`، بيتعمل `Message` حقل `target` بتاعها هو الـ Handler، "
            "وحقل `callback` هو الـ Runnable. طالما الـ Timestamp بتاع الرسالة لسه ما جاش، الرسالة بتفضل متعلقة في السلسلة المتصلة بالـ Looper بتاع الـ Main Thread، "
            "اللي هو واحد من أقوى الـ GC Roots في بيئة ART.\n\n"
            "لو الـ Runnable ده معمول كـ Lambda بتنادي ميثود في الـ Activity، الـ Bytecode بيلتقط `this` صراحة. وعشان كده في فحص الـ HPROF Dumps بـ LeakCanary، "
            "بنلاقي دايماً المسار: `Thread (main) -> Looper -> MessageQueue -> mMessages -> Message.callback -> Runnable -> Activity`.\n\n"
            "أما بالنسبة للـ Static References، فالمتغير الثابت بيتعلق بكائن `java.lang.Class` اللي اتحمل بالـ Application ClassLoader، وده تسريب أبدي مبيتمسحش "
            "غير بـ Process Death. في الفرق الهندسية المتقدمة، بنمنع الـ Handlers تماماً ونستبدلها بـ Coroutine Builders المرتبطة بـ `LifecycleOwner`. وفي الحالات "
            "الاستثنائية اللي بنحتاج فيها Handler، بنستخدم Static Class مع `WeakReference` ونلزم المطورين باستدعاء `handler.removeCallbacksAndMessages(null)` "
            "في `onDestroy` لحذف الرسائل المعلقة من الـ Queue فوراً دون أي تسريب."
        ),
    },
    "MEM-13": {
        "id": "MEM-13",
        "questionAr": "كيف تؤثر عمليات تخصيص الـ Bitmap ومكتبات تحميل الصور على الذاكرة؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": (
            "- حساب حجم الذاكرة المستهلكة من البكسلات المفكوكة فعلياً بدلاً من الاعتماد المضلل على حجم الملف المضغوط على القرص.\n"
            "- فهم تقنيات التحجيم بحسب أبعاد العرض (Target-size decoding)، وإلغاء الطلبات المتوافقة مع دورة الحياة، والتخزين المؤقت، وإدارة الذاكرة الرسومية الأصلية.\n"
            "- تجنب الاستدعاء اليدوي الخطير لدالة `recycle()` والتحكم في ميزانية الذاكرة عند استخدام مكتبات مثل Coil و Glide."
        ),
        "why_it_matters_ar": (
            "تعد الـ Bitmaps أكبر مستهلك منفرد للذاكرة في تطبيقات أندرويد. حجم الصورة في الذاكرة لا يحدده حجم ملف الـ JPG أو PNG المضغوط على القرص، بل أبعاد البكسل "
            "الفعلية وصيغة الألوان: `width * height * bytesPerPixel`. صورة بدقة 12 ميجابكسل (4000x3000) بصيغة `ARGB_8888` (4 بايت لكل بكسل) تستهلك 48 ميجابايت "
            "من الذاكرة المتصلة، حتى لو كان حجم الملف على القرص 2 ميجابايت فقط! تاريخياً، كانت البكسلات تُخزن على الـ Java Heap مسببة تجزئة مستمرة، لكن منذ أندرويد "
            "8.0 (API 26) تم نقلها إلى الـ Native Memory عبر `NativeAllocationRegistry` مع إتاحة قوام العتاد `Bitmap.Config.HARDWARE` على الـ GPU. مكتبات تحميل "
            "الصور الحديثة (Coil و Glide) تحمي التطبيق من الـ OOM عبر فك تشفير البكسلات بحجم الـ View فقط، وإعادة استخدام مساحات البايت المحجوزة عبر `inBitmap`، "
            "وضبط كاش الذاكرة بميزانية مدروسة."
        ),
        "worked_example_ar": (
            "المقارنة بين فك التشفير الخام المسبب للانهيار والفك الذكي المحجم:\n"
            "```kotlin\n"
            "// ❌ كود يسبب OOM: فك تشفير صورة 48MB كاملة لعرضها في Thumbnail صغير:\n"
            "val fullBitmap = BitmapFactory.decodeFile(imagePath) // حجز 48MB في Native Memory!\n"
            "\n"
            "// ✅ كود محسّن: فك التشفير على خطوتين بحجم الـ View المطلوب (Subsampling):\n"
            "fun decodeSampledBitmap(path: String, reqWidth: Int, reqHeight: Int): Bitmap {\n"
            "    val options = BitmapFactory.Options().apply {\n"
            "        inJustDecodeBounds = true // قراءة الأبعاد فقط دون حجز أي بكسلات في الذاكرة\n"
            "    }\n"
            "    BitmapFactory.decodeFile(path, options)\n"
            "\n"
            "    // حساب معامل التصغير inSampleSize (مضاعفات الرقم 2):\n"
            "    var inSampleSize = 1\n"
            "    if (options.outHeight > reqHeight || options.outWidth > reqWidth) {\n"
            "        val halfHeight = options.outHeight / 2\n"
            "        val halfWidth = options.outWidth / 2\n"
            "        while ((halfHeight / inSampleSize) >= reqHeight && (halfWidth / inSampleSize) >= reqWidth) {\n"
            "            inSampleSize *= 2\n"
            "        }\n"
            "    }\n"
            "\n"
            "    options.inSampleSize = inSampleSize\n"
            "    options.inJustDecodeBounds = false\n"
            "    return BitmapFactory.decodeFile(path, options) // فك البكسلات المطلوبة فقط!\n"
            "}\n"
            "```\n"
            "باستخدام معامل تصغير 4، ينخفض عدد البكسلات بمقدار 16 ضعفاً، ويهبط استهلاك الذاكرة من 48 ميجابايت إلى 3 ميجابايت فقط مع الحفاظ على وضوح الصورة على الشاشة."
        ),
        "trade_offs_ar": (
            "استخدام صيغة `Bitmap.Config.HARDWARE` يوفر أداء رسومياً خارقاً وينقل البكسلات لـ VRAM بدون نسخ (Zero-Copy)، ولكنه يجعل الصورة غير قابلة للتعديل "
            "بـ Software Canvas أو القراءة المباشرة للبكسلات. التخزين المؤقت في الذاكرة (Memory Cache) يمنع إعادة تحميل الصور ويسرع التمرير، لكنه يحجز مساحة "
            "مستمرة؛ لذا يجب ربطه بـ LruCache بميزانية لا تتجاوز 20-25% من الـ Heap وتفريغه عند استقبال تنبيهات `onTrimMemory`. لا يجب استدعاء `bitmap.recycle()` "
            "يدوياً عند استخدام مكتبات الصور لتجنب أخطاء Canvas الرسم."
        ),
        "failure_modes_ar": (
            "فك تشفير عدة صور عالية الدقة في قائمة سريعة دون تحجيم يفجر استثناء OutOfMemoryError في لحظات، إما لنفاد الـ Heap أو نفاد الذاكرة الأصلية (Native Space). "
            "رسم صورة بعد استدعاء `recycle()` يدوياً يفجر كراش فوري بـ `RuntimeException: Canvas: trying to use a recycled bitmap`. عدم ضبط ميزانية قصوى للـ Image "
            "Cache يؤدي إلى بطء عام وتدخل الـ Low Memory Killer لإنهاء التطبيق."
        ),
        "production_perspective_ar": (
            "في بيئات الإنتاج، نعتمد كلياً على مكتبات معتمدة مثل Coil في مشاريع Jetpack Compose و Kotlin Coroutines، أو Glide في مشاريع Views القديمة. نراقب "
            "استهلاك الـ Native Memory عبر أمر `adb shell dumpsys meminfo`، ونحرص على ربط طلبات الصور بدورة حياة الشاشة لإلغاء تحميل الصور فور خروج العنصر من "
            "مجال الرؤية، مع تفعيل الاستجابة لـ `onTrimMemory(TRIM_MEMORY_RUNNING_LOW)`."
        ),
        "how_to_answer_ar": (
            "- **معادلة حجم البكسل:** ابدأ بحساب الحجم: العرض × الارتفاع × البايت لكل بكسل، وبيّن أن حجم الملف على القرص مضلل.\n"
            "- **تطور النظام:** اشرح نقل البكسلات من Java Heap إلى الـ Native Memory في أندرويد 8.0 واستخدام صور HARDWARE.\n"
            "- **دور المكتبات الحديثة:** وضّح دور Coil و Glide في أربع ركائز: التحجيم (Downsampling)، وإعادة الاستخدام (Bitmap Pooling بـ inBitmap)، والتخزين المؤقت، وإلغاء الطلبات مع دورة الحياة."
        ),
        "talking_points_ar": (
            "ناقش آلية عمل `NativeAllocationRegistry`، والفروق بين صيغ الألوان (ARGB_8888, RGB_565, HARDWARE)، وتصميم الـ Bitmap Pool لتفادي الـ Memory Churn، "
            "ومراقبة استهلاك الـ Graphics و PSS في التقارير."
        ),
        "follow_ups_ar": (
            "- **المحاور:** \"ليه لما بفتح صورة مساحتها على كارت الميموري 2 ميجابايت بتستهلك في الرام 50 ميجابايت؟\"\n"
            "  **المرشح:** \"لأن مساحة الـ 2 ميجابايت دي مساحة ملف الـ JPG أو PNG المضغوط على القرص بخوارزميات زي Huffman و DCT. لكن عشان الشاشة تعرض الصورة، لازم نظام أندرويد يفك الضغط بالكامل لكل بكسل خام في الذاكرة؛ فصورة 4000x3000 بكسل بصيغة ARGB_8888 بتضرب 12 مليون بكسل في 4 بايت، فبتستهلك 48 ميجابايت RAM فوراً.\"\n\n"
            "- **المحاور:** \"إيه هي الـ Bitmap Pooling وإزاي بتمنع الـ Jank في القوائم؟\"\n"
            "  **المرشح:** \"الـ Bitmap Pooling تقنية بتستخدمها مكتبات زي Coil و Glide عبر معامل `BitmapFactory.Options.inBitmap`. بدل ما نحجز مصفوفة بايت جديدة في الرام ونمسح القديمة مع كل صورة في السكرول، بنعيد استخدام نفس الـ Byte Array المحجوزة مسبقاً لكتابة الصورة الجديدة فيها، وده بيلغي الـ Allocation Churn وتوقفات الـ GC تماماً.\""
        ),
        "self_check_ar": (
            "احسب حجم صورة بدقة 1080x1920 بصيغة ARGB_8888؛ اشرح دور inSampleSize؛ وبيّن ميزة وعيب استخدام Bitmap.Config.HARDWARE."
        ),
        "references_ar": (
            "- [إدارة استهلاك الذاكرة في الـ Bitmaps](https://developer.android.com/topic/performance/graphics/manage-memory) — التحجيم وإعادة الاستخدام الرسمية.\n"
            "- [تحميل الصور بكفاءة عالية](https://developer.android.com/topic/performance/graphics/load-bitmap) — استخدام BitmapFactory وتقنيات Subsampling.\n\n"
            "تمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13."
        ),
        "quick_answer_ar": (
            "الـ Bitmap بتستهلك ذاكرة ضخمة بتتحسب بضرب العرض في الارتفاع في عدد البايت لكل بكسل (4 بايت لصيغة ARGB_8888)، وبالتالي حجم الملف المضغوط على القرص "
            "ملوش أي علاقة بالاستهلاك في الرام. من أندرويد 8.0 فما فوق، بكسلات الصور بتتسجل في الـ Native Memory. مكتبات الصور زي Coil و Glide بتحمي الذاكرة من "
            "الـ OOM عن طريق تصغير حجم الصورة لأبعاد الـ View، وإعادة استخدام مساحات البايت بـ `inBitmap`، والتخزين المؤقت بميزانية محددة."
        ),
        "best_answer_ar": (
            "الـ Bitmaps هي أكبر خطر ممكن يفجر الـ OutOfMemoryError في تطبيقات أندرويد لو متدارتش بوعي هندسي. الفكرة الأساسية إن حجم ملف الصورة على القرص أو الشبكة "
            "مضغوط بصيغ زي JPEG أو WebP، لكن كارت الشاشة والـ Canvas محتاجين البكسلات مفرودة بالكامل بصيغتها الأولية.\n\n"
            "المعادلة البسيطة هي: العرض × الارتفاع × البايت لكل بكسل. فلو فكينا صورة كاميرا عادية 12 ميجابكسل بصيغة `ARGB_8888`، هتستهلك حوالي 48 ميجابايت من "
            "الذاكرة المتصلة، وتكرار ده كفيل يخنق أي جهاز متوسط في لحظات. وتاريخياً من أندرويد 8.0، البكسلات اتنقلت من Java Heap للـ Native Memory عبر `NativeAllocationRegistry` "
            "لتقليل تجزئة الذاكرة المدارة.\n\n"
            "عشان كده الاعتماد على مكتبات زي Coil أو Glide إلزامي في مشاريع الإنتاج؛ لأنها بتعمل أربع حاجات حاسمة: أولاً بتعمل Downsampling وبتفك البكسلات على مقاس "
            "الـ ImageView فقط عبر `inSampleSize`. ثانياً بتعمل Bitmap Pooling وبتعيد استخدام نفس مصفوفة البايت عبر `inBitmap` لمنع الـ GC Churn. ثالثاً بتدير Memory "
            "Cache بميزانية محسوبة من حجم رام الجهاز، ورابعاً بتلغي طلبات الصور تلقائياً مع حركة الـ Lifecycle."
        ),
        "deep_answer_ar": (
            "في التحليل الهندسي المتقدم لاستهلاك الذاكرة، فحص الـ Java Heap لوحده مش كفاية لمراقبة الـ Bitmaps من بعد أندرويد 8.0. كائن الـ `Bitmap` على الـ Java Heap "
            "حجمه لا يتعدى 100 بايت كـ Wrapper، بينما ملايين البايتات للبكسلات بتعيش في الـ Native C++ Heap مدعومة بـ `NativeAllocationRegistry`. الـ GC بينظف الذاكرة "
            "الأصلية دي عبر Cleaner Callback أول ما الـ Java Wrapper يفقد مراجعة، لكن لو الـ Java Heap مش تحت ضغط، مجمع النفايات ممكن يتأخر في التدخل فتتضخم الـ Native "
            "Memory ويحصل OOM في النظام.\n\n"
            "لتفادي ده، بنفحص الـ PSS والـ Graphics Memory عبر أمر `adb shell dumpsys meminfo` ونراقب تخصيصات الـ Native Heap في الـ Profiler. في واجهات العرض الحديثة، "
            "بنعتمد على `Bitmap.Config.HARDWARE` اللي بيعمل GraphicBuffer textures بتتسجل مباشرة في ذاكرة كارت الشاشة (GPU VRAM) بأسلوب Zero-Copy، وده بيوفر الرام ويسرع "
            "العرض جداً، لكن عيبها إنها Immutable ومينفعش تتعدل بـ Software Canvas.\n\n"
            "كمان بنربط مكتبة الصور بـ `ComponentCallbacks2.onTrimMemory`، وبنحدد حجم الـ LruCache بحد أقصى 20% لـ 25% من الـ Memory Class المتاحة من "
            "`ActivityManager.getMemoryClass()`. ده مع الـ Request Cancellation التلقائي عند تدوير الشاشة أو السكرول السريع بيضمن إن التطبيق يفضل مستقر وسلس حتى "
            "على الهواتف الاقتصادية ذات سعة الرام المحدودة."
        ),
    },
}

def main():
    print("=== Elevating MEM-08 to MEM-13 ===")
    out_meta = {}

    for qid in ["MEM-08", "MEM-09", "MEM-10", "MEM-11", "MEM-12", "MEM-13"]:
        print(f"Updating canonical question {qid}...")
        en = EN_DATA[qid]
        ee.update_canonical_question(
            qid=qid,
            concept_en=en["concept_en"],
            walkthrough_en=en["walkthrough_en"],
            structured_en=en["structured_en"],
            deep_senior_en=en["deep_senior_en"],
            short_en=en["short_en"],
        )
        out_meta[qid] = AR_DATA[qid]

    meta_path = ee.DATA_DIR / "metadata_mem_08_13.json"
    meta_path.write_text(json.dumps(out_meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {len(out_meta)} metadata records to {meta_path}")

    ee.merge_all_metadata()

    has_err = False
    for qid in ["MEM-08", "MEM-09", "MEM-10", "MEM-11", "MEM-12", "MEM-13"]:
        errs = ee.validate_question(qid)
        if errs:
            has_err = True
            print(f"ERRORS in {qid}:")
            for e in errs:
                print(f"  - {e}")
        else:
            print(f"PASS: {qid} (0 errors)")

    if has_err:
        sys.exit(1)
    print("Batch 2 (MEM-08 to MEM-13) completed successfully!")

if __name__ == "__main__":
    main()
