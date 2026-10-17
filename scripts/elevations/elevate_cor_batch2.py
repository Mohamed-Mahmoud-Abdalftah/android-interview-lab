#!/usr/bin/env python3
"""Batch 2: Elevate COR-06 through COR-10."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
import scripts.elevations.elevation_engine as ee

DATA_DIR = Path(__file__).resolve().parent / "data"

# ==============================================================================
# CANONICAL ENGLISH DEFINITIONS FOR COR-06 TO COR-10
# ==============================================================================

COR_06_EN = {
    "concept_en": (
        "In Android development, managing coroutine lifespans requires choosing the correct scope boundary: viewModelScope, lifecycleScope, or a custom application-level scope. The viewModelScope is tied to the ViewModel lifecycle; it automatically cancels all child coroutines when ViewModel.onCleared is invoked. Because ViewModels survive configuration changes such as screen rotations, viewModelScope is the primary architectural boundary for initiating business logic, fetching remote data, and maintaining UI state. Conversely, lifecycleScope is bound directly to an Android LifecycleOwner, such as an Activity or Fragment. It is cancelled when the lifecycle reaches DESTROYED. Crucially, lifecycleScope provides repeatOnLifecycle and flowWithLifecycle to safely collect UI flows only when the screen is at or above a specific state (such as STARTED), pausing collection when the app is backgrounded. For operations that must survive screen destruction but remain confined to the app process (such as dispatching analytics or flushing a local database transaction), a custom application-level scope injected as a singleton with a SupervisorJob is the appropriate boundary. Finally, for work that must persist across process death and system restarts, WorkManager must be used rather than any in-memory coroutine scope."
    ),
    "walkthrough_en": (
        "Consider a chat messaging screen where a user sends a message and navigates away immediately.\n\n"
        "If the network message transmission is launched directly inside Fragment lifecycleScope:\n"
        "```kotlin\n"
        "// In ChatFragment.kt\n"
        "btnSend.setOnClickListener {\n"
        "    viewLifecycleOwner.lifecycleScope.launch {\n"
        "        // Fragile: Cancelled immediately if the user exits the fragment!\n"
        "        chatRepository.sendMessage(messageText)\n"
        "    }\n"
        "}\n"
        "```\n"
        "When the user pops the backstack, the fragment view is destroyed, cancelling lifecycleScope. The message transmission is aborted mid-flight.\n\n"
        "The correct architecture delegates execution according to lifetime guarantees:\n"
        "```kotlin\n"
        "// In ChatViewModel.kt\n"
        "fun sendMessage(text: String) {\n"
        "    // Outlives fragment recreation and screen rotation\n"
        "    viewModelScope.launch {\n"
        "        chatRepository.sendMessage(text)\n"
        "    }\n"
        "}\n\n"
        "// In ChatRepository.kt (Application-level scope for guaranteed delivery)\n"
        "suspend fun sendMessage(text: String) = withContext(ioDispatcher) {\n"
        "    // If message must be stored and synced even if ViewModel clears:\n"
        "    localDb.savePendingMessage(text)\n"
        "    appCoroutineScope.launch {\n"
        "        remoteApi.postMessage(text)\n"
        "    }\n"
        "}\n"
        "```\n"
        "In the Fragment, lifecycleScope is reserved strictly for UI state observation using viewLifecycleOwner.lifecycleScope.launch { viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) { ... } }."
    ),
    "short_en": (
        "viewModelScope outlives configuration changes and cancels on ViewModel.onCleared, making it the standard boundary for business logic. lifecycleScope is tied to Activity/Fragment lifecycles and cancelled on destruction, ideal for UI collectors with repeatOnLifecycle. Custom application scopes handle in-memory background operations that must survive screen navigation."
    ),
    "structured_en": (
        "To begin with, selecting the appropriate coroutine scope in Android is a decision of lifecycle ownership and task survival boundaries.\n\n"
        "From an architectural standpoint, viewModelScope is the standard home for screen business logic. It survives configuration changes like device rotations and guarantees deterministic cancellation when the ViewModel clears, preventing orphaned network calls.\n\n"
        "In production scenarios, lifecycleScope is strictly bound to an Activity or Fragment window. We pair it with repeatOnLifecycle to observe UI state flows safely, automatically stopping flow emissions when the UI is invisible to conserve device battery and memory.\n\n"
        "As for boundary management, when an operation must outlive screen navigation—such as writing an audit log or completing an in-memory database flush—we inject a custom application-level scope backed by a SupervisorJob. If the operation must survive process death or device reboot, we escalate to WorkManager."
    ),
    "deep_senior_en": (
        "Under the hood, viewModelScope is implemented as an extension property on ViewModel backed by an internal CloseableCoroutineScope. When the Android ViewModelProvider clears a ViewModel, it iterates through its registered closeables and invokes close() on the scope, which internally calls coroutineContext.cancel(). This cleanly cancels the root Job and cascades cancellation down through all active child coroutines. Because ViewModels are retained across configuration changes by the ViewModelStoreOwner, viewModelScope remains active while the Activity destroys and recreates its View hierarchy.\n\n"
        "In contrast, lifecycleScope is an instance of LifecycleCoroutineScopeImpl that implements LifecycleEventObserver. It monitors Lifecycle.Event.ON_DESTROY and cancels its context upon arrival. However, simply using lifecycleScope.launch for Flow collection is dangerous because it keeps collecting even when the screen is stopped in the background. Modern Android architecture requires repeatOnLifecycle(Lifecycle.State.STARTED), which creates a suspending boundary that launches a new coroutine when the lifecycle reaches the target state and cancels it whenever the lifecycle drops below that state.\n\n"
        "For application-wide operations, senior engineers inject a dedicated CoroutineScope configured with a SupervisorJob and Dispatchers.Default or Dispatchers.IO via dependency injection. This prevents a failure in one application task from cancelling the entire scope, while ensuring operations finish even after the originating screen is popped from the backstack.\n\n"
        "The ultimate boundary is persistent background execution. Neither viewModelScope nor application scopes can survive low-memory killer process termination. Any critical background work that has strict delivery guarantees—such as offline database synchronization or file uploads—must be scheduled using WorkManager, which persists job metadata in SQLite."
    ),
}

COR_07_EN = {
    "concept_en": (
        "In Kotlin coroutines, CoroutineDispatchers determine the execution thread or thread pool allocated to a coroutine's continuation. The standard library provides four primary dispatchers tailored for distinct runtime characteristics: Dispatchers.Main, Dispatchers.IO, Dispatchers.Default, and Dispatchers.Unconfined. Dispatchers.Main is confined to the Android main UI thread via the platform Looper; it is dedicated to manipulating UI components, rendering Jetpack Compose state, and processing touch input. Dispatchers.Default is backed by a shared pool of worker threads sized to the number of available CPU cores (minimum 2), specifically optimized for computation-heavy tasks such as JSON parsing, mathematical calculations, and complex sorting. Dispatchers.IO is designed for blocking I/O operations such as disk reads and synchronous network requests; it utilizes an elastic thread pool capable of expanding up to 64 threads or the core count to prevent I/O blocking from starving the system. Dispatchers.Unconfined begins execution in the caller's thread and resumes in whatever thread resumed the suspending call, lacking thread confinement and making it unsuitable for standard Android application logic."
    ),
    "walkthrough_en": (
        "Consider an analytical report generation feature that aggregates thousands of transactions, calculates tax metrics, writes a PDF document to disk, and updates the screen progress.\n\n"
        "Proper separation of concerns across dispatchers:\n"
        "```kotlin\n"
        "fun exportFinancialReport() {\n"
        "    // 1. Dispatchers.Main: Update UI loading state on the main thread\n"
        "    viewModelScope.launch(Dispatchers.Main) {\n"
        "        _uiState.value = ExportUiState.Loading\n\n"
        "        // 2. Dispatchers.Default: Heavy CPU calculations and summaries\n"
        "        val summary = withContext(Dispatchers.Default) {\n"
        "            calculateFinancialMetrics(rawTransactions)\n"
        "        }\n\n"
        "        // 3. Dispatchers.IO: Blocking disk write operation\n"
        "        val pdfFile = withContext(Dispatchers.IO) {\n"
        "            writePdfToDisk(summary)\n"
        "        }\n\n"
        "        // 4. Return to Dispatchers.Main automatically to display the success dialog\n"
        "        _uiState.value = ExportUiState.Success(pdfFile)\n"
        "    }\n"
        "}\n"
        "```\n"
        "By segmenting the pipeline, heavy mathematical computations do not block UI frame rendering, and blocking disk operations do not saturate the CPU-bound thread pool."
    ),
    "short_en": (
        "Dispatchers.Main executes on the Android UI thread for user interface updates. Dispatchers.Default is sized to CPU cores for intensive computations like JSON parsing. Dispatchers.IO uses an elastic pool of up to 64 threads for blocking disk and network I/O. Dispatchers.Unconfined executes without thread confinement, rarely used in production."
    ),
    "structured_en": (
        "To begin with, CoroutineDispatchers allocate coroutine execution across available operating system threads based on the nature of the computational workload.\n\n"
        "From an architectural standpoint, Dispatchers.Main is confined to the Android UI thread via the main Looper. It handles user interactions, Compose state changes, and View manipulations, requiring that long-running operations never execute directly upon it.\n\n"
        "In production scenarios, we distinguish between CPU-bound and I/O-bound workloads. Dispatchers.Default is backed by a thread pool sized to available CPU cores, making it optimal for heavy data parsing, crypto, and list sorting. Dispatchers.IO is an elastic thread pool scaling up to 64 threads, designed specifically for blocking disk and network I/O calls where threads spend time waiting on kernel syscalls.\n\n"
        "As for boundary management, Dispatchers.Unconfined does not restrict execution to any designated thread, resuming wherever the continuation completes. Due to its unpredictable thread hops, it is strictly avoided in production Android code."
    ),
    "deep_senior_en": (
        "Under the hood, both Dispatchers.Default and Dispatchers.IO share the exact same underlying thread scheduler: the internal CoroutineScheduler in kotlinx.coroutines. This shared scheduler implements a high-performance work-stealing algorithm with local and global task queues, designed to minimize operating system context switches and memory footprint.\n\n"
        "Dispatchers.Default operates with a target parallelism equal to Runtime.getRuntime().availableProcessors(), clamped to a minimum of two. Each worker thread runs continuously processing CPU tasks. If more CPU-bound coroutines are launched than available cores, they queue in work-stealing deques, preventing excessive kernel thread context switching that would thrash CPU instruction caches.\n\n"
        "In contrast, Dispatchers.IO is implemented as a LimitingDispatcher wrapped around the shared CoroutineScheduler. When a coroutine executing on Dispatchers.IO makes a blocking file or socket syscall, the scheduler detects that the thread is in a blocking state and spawns additional worker threads on demand, up to a maximum limit configured by kotlinx.coroutines.io.parallelism (defaulting to 64 or the core count). Because Default and IO share the same worker pool, switching between Dispatchers.Default and Dispatchers.IO via withContext often avoids an OS thread context switch entirely if a shared worker thread is already available.\n\n"
        "Dispatchers.Main is implemented in the kotlinx-coroutines-android artifact via HandlerContext, wrapping a standard android.os.Handler initialized with Looper.getMainLooper(). Dispatchers.Main.immediate provides an essential optimization by checking if Thread.currentThread() is already the main Looper thread, executing the runnable inline and avoiding an unnecessary Choreographer frame delay."
    ),
}

COR_08_EN = {
    "concept_en": (
        "The concrete threading models of Dispatchers.Main and Dispatchers.IO represent two radically different execution architectures in Android. Dispatchers.Main is strictly bound to the single Android UI thread through the platform Handler and Looper.getMainLooper() mechanism; every task dispatched to Dispatchers.Main is enqueued as a Message on the main Looper MessageQueue. Consequently, executing any blocking call or long-running CPU computation on Dispatchers.Main directly halts the main event loop, causing frame drops (jank) and triggering an Application Not Responding (ANR) error after five seconds. In contrast, Dispatchers.IO does not own a dedicated private thread pool; instead, it utilizes an elastic limiting facade on top of the shared Kotlin CoroutineScheduler. The IO pool is configured to support high-concurrency blocking I/O calls, dynamically expanding up to 64 threads (or the number of available CPU cores, whichever is larger), allowing multiple blocking syscalls to wait on network or disk operations simultaneously without starving CPU worker threads."
    ),
    "walkthrough_en": (
        "Demonstrating the difference between Dispatchers.Main and Dispatchers.IO under heavy concurrency:\n\n"
        "```kotlin\n"
        "// 1. Thread starvation on Main:\n"
        "viewModelScope.launch(Dispatchers.Main) {\n"
        "    // Fatal: Thread.sleep blocks the single Android UI thread\n"
        "    Thread.sleep(5000) // Triggers an ANR dialog!\n"
        "}\n\n"
        "// 2. High-concurrency blocking reads on IO:\n"
        "viewModelScope.launch(Dispatchers.IO) {\n"
        "    // Launching 50 concurrent blocking database reads\n"
        "    repeat(50) {\n"
        "        launch {\n"
        "            // Blocks an IO worker thread, but the elastic pool spawns up to 64 threads\n"
        "            legacyDbDriver.blockingQuery()\n"
        "        }\n"
        "    }\n"
        "    // The UI thread remains completely responsive at 60/120 fps\n"
        "}\n"
        "```\n"
        "While Dispatchers.Main can only execute one task at a time, Dispatchers.IO dynamically scales worker threads to accommodate concurrent blocking calls without impacting screen rendering."
    ),
    "short_en": (
        "Dispatchers.Main uses the single Android UI thread via Looper.getMainLooper(), where any blocking call causes an ANR. Dispatchers.IO uses an elastic thread pool scaling up to 64 threads on top of the shared CoroutineScheduler, specifically designed to handle blocking disk and network I/O without starving CPU tasks."
    ),
    "structured_en": (
        "To begin with, Dispatchers.Main and Dispatchers.IO serve fundamentally different runtime roles and rely on distinct underlying threading mechanisms.\n\n"
        "From an architectural standpoint, Dispatchers.Main is bound to the single Android UI thread. It communicates directly with the main Looper MessageQueue, ensuring thread confinement for UI widget updates while making blocking calls catastrophic for frame rendering.\n\n"
        "In production scenarios, Dispatchers.IO manages an elastic thread pool designed for blocking operations. When coroutines block on file systems or network sockets, the IO dispatcher expands its worker pool up to 64 threads, ensuring that I/O wait times do not bottleneck concurrent requests.\n\n"
        "As for boundary management, Kotlin coroutines optimize thread utilization by sharing the underlying CoroutineScheduler between Dispatchers.IO and Dispatchers.Default, preventing excessive OS thread allocation and reducing system context-switching overhead."
    ),
    "deep_senior_en": (
        "Under the hood, Dispatchers.Main in Android is an instance of HandlerDispatcher implemented by HandlerContext. When a coroutine continuation is dispatched, HandlerContext invokes handler.post(runnable) on the main Looper Handler. This schedules the continuation as a Message on the main thread MessageQueue. If the main thread is currently executing a blocking operation like Thread.sleep or a synchronous SQLite query, the MessageQueue stalls, preventing Choreographer vsync signals and touch events from processing. Dispatchers.Main.immediate avoids this overhead when already on the main thread by executing the runnable synchronously via a fast-path check, eliminating a redundant message dispatch cycle.\n\n"
        "On the other hand, Dispatchers.IO is not an isolated thread pool executor; it is an instance of LimitingDispatcher backed by the internal CoroutineScheduler. The CoroutineScheduler maintains worker threads categorized into CPU workers and blocking workers. While Dispatchers.Default limits active worker threads to the core count, Dispatchers.IO allows the scheduler to spawn additional threads when existing threads enter a blocking state (such as waiting on kernel file descriptors).\n\n"
        "The upper limit of Dispatchers.IO is controlled by the system property kotlinx.coroutines.io.parallelism, defaulting to max(64, coreCount). Because both dispatchers draw from the same scheduler thread pool, a coroutine switching from Dispatchers.IO to Dispatchers.Default via withContext can frequently reuse the same native thread if CPU quotas allow, eliminating expensive OS-level thread context switches.\n\n"
        "Understanding this architecture is essential when profiling Android apps with Systrace or Android Studio Profiler. Seeing dozens of threads in the IO pool is normal and expected during disk writes, whereas seeing long slices on the Main thread indicates severe main-safety violations."
    ),
}

COR_09_EN = {
    "concept_en": (
        "In Kotlin coroutines, withContext is a built-in suspending function that switches the execution context of the calling coroutine inline without launching a new coroutine or creating a separate Job. It takes a CoroutineContext parameter, suspends the current execution, transfers the remaining computation to the specified dispatcher, and resumes the caller with the returned result once completed. Because withContext is a suspending function rather than a coroutine builder, it executes sequentially and returns its computed value directly, avoiding the need for await or join calls. In modern Android architecture, withContext is the primary technical mechanism used to enforce the Main-Safety principle: repository, data source, and use case methods use withContext(Dispatchers.IO) or withContext(Dispatchers.Default) internally to offload disk, network, and CPU operations away from the main thread, allowing callers on the UI thread to invoke them safely and transparently without thread management boilerplate."
    ),
    "walkthrough_en": (
        "Consider a database repository that loads user preferences from local storage and maps them into domain entities.\n\n"
        "Demonstrating proper withContext usage:\n"
        "```kotlin\n"
        "class UserRepository(\n"
        "    private val localDao: UserDao,\n"
        "    private val ioDispatcher: CoroutineDispatcher = Dispatchers.IO\n"
        ") {\n"
        "    // Main-safe: Callers can safely invoke this on Dispatchers.Main\n"
        "    suspend fun getUserProfile(userId: String): UserProfile = withContext(ioDispatcher) {\n"
        "        // 1. Executes on Dispatchers.IO worker thread\n"
        "        val rawEntity = localDao.queryUserById(userId)\n"
        "        // 2. Maps to domain entity\n"
        "        UserProfile.fromEntity(rawEntity)\n"
        "    } // 3. Automatically resumes the caller on their original dispatcher (e.g., Main)\n"
        "}\n"
        "```\n"
        "A ViewModel calls this function seamlessly: val profile = userRepository.getUserProfile(id), updating UI state immediately without manually managing threads or background callbacks."
    ),
    "short_en": (
        "withContext is a suspending function that switches coroutine context inline without launching a new coroutine, returning the block result directly to the caller upon resumption. It is the standard mechanism for achieving Main-Safety in repository and domain layers by offloading heavy I/O or CPU tasks to appropriate dispatchers."
    ),
    "structured_en": (
        "To begin with, withContext is a core suspending function designed to switch execution contexts within an existing coroutine in a sequential, non-blocking manner.\n\n"
        "From an architectural standpoint, withContext does not spawn a new coroutine or create an independent Job. Instead, it temporarily shifts execution to the specified CoroutineDispatcher, suspends the caller, and returns the computed value directly upon resumption.\n\n"
        "In production scenarios, we use withContext to implement the Main-Safety contract. Repositories and data sources wrap blocking database queries or network parsers in withContext(Dispatchers.IO) or withContext(Dispatchers.Default), allowing ViewModels to consume suspending functions directly from Dispatchers.Main.\n\n"
        "As for boundary management, passing a new Job instance into withContext is an anti-pattern because it severs structured concurrency and prevents parent cancellation from propagating into the switched block."
    ),
    "deep_senior_en": (
        "Under the hood, withContext is implemented via the internal DispatchedCoroutine or UndispatchedCoroutine classes. When withContext(newContext) is invoked, the runtime merges the current coroutine context with newContext. If the target dispatcher matches the current dispatcher, the runtime optimizes execution via an undispatched fast path, running the block immediately in the current thread frame without queueing.\n\n"
        "When the target dispatcher differs from the current one, the runtime creates a DispatchedCoroutine, suspends the caller's continuation, and dispatches the execution of the block onto the new dispatcher. The calling coroutine remains suspended until the code block completes. When the block finishes, the DispatchedCoroutine captures the return value or exception and calls continuation.resumeWith, dispatching resumption back to the original caller dispatcher.\n\n"
        "A critical nuance in structured concurrency is how Job elements behave inside withContext. If a developer accidentally writes withContext(Dispatchers.IO + Job()), the explicit Job parameter breaks the parent-child hierarchy. The code inside the withContext block is no longer a child of the outer coroutine's Job. If the outer ViewModel scope is cancelled, the inner block will not receive the cancellation signal and will continue executing as an orphaned task.\n\n"
        "Additionally, withContext supports cancellation checks. When a coroutine is cancelled while suspended inside withContext, it throws a CancellationException back to the caller upon resumption, ensuring clean cancellation propagation across dispatcher boundaries without leaking resources."
    ),
}

COR_10_EN = {
    "concept_en": (
        "In Kotlin coroutines, cancellation is cooperative, meaning that a running coroutine cannot be preemptively or forcefully aborted from the outside by an operating system thread interruption. When a coroutine or its parent Job is cancelled, its state transitions to Cancelling, and it must cooperatively inspect its cancellation status to terminate execution. Cancellation points are specific locations during coroutine execution where cancellation is checked; if the coroutine has been cancelled, a CancellationException is thrown to unwind the call stack cleanly. All suspending functions provided by kotlinx.coroutines (such as delay, yield, withContext, await, and receive) are built-in cancellation points. However, if a coroutine executes a long-running CPU computation or a synchronous blocking Java I/O stream without invoking suspending functions, it will continue running unabated unless the developer explicitly inserts cancellation checks, such as calling ensureActive(), querying isActive, or invoking yield(). Furthermore, swallowing CancellationException in a generic try-catch block without re-throwing it violates cooperative cancellation, causing cancelled coroutines to silently resurrect and run indefinitely."
    ),
    "walkthrough_en": (
        "Consider a background file encryption routine executing a tight loop over thousands of byte chunks.\n\n"
        "Uncooperative implementation that ignores cancellation:\n"
        "```kotlin\n"
        "// Defective: Ignores cancellation signals\n"
        "suspend fun encryptFile(data: ByteArray): ByteArray = withContext(Dispatchers.Default) {\n"
        "    val result = ByteArray(data.size)\n"
        "    for (i in data.indices) {\n"
        "        result[i] = computeByteHash(data[i]) // Tight CPU loop, no suspension point!\n"
        "    }\n"
        "    result\n"
        "}\n"
        "```\n"
        "If the user cancels this operation, the loop continues running to completion, burning CPU cycles and draining the battery.\n\n"
        "The correct cooperative implementation:\n"
        "```kotlin\n"
        "suspend fun encryptFile(data: ByteArray): ByteArray = withContext(Dispatchers.Default) {\n"
        "    val result = ByteArray(data.size)\n"
        "    for (i in data.indices) {\n"
        "        // Check cancellation every 1,000 iterations\n"
        "        if (i % 1000 == 0) ensureActive()\n"
        "        result[i] = computeByteHash(data[i])\n"
        "    }\n"
        "    result\n"
        "}\n"
        "```\n"
        "Calling ensureActive() immediately throws CancellationException if the coroutine is cancelled, terminating execution gracefully."
    ),
    "short_en": (
        "Cancellation in Kotlin coroutines is cooperative and never preemptive. A coroutine must check its cancellation status or reach a cancellation point—such as delay(), yield(), or ensureActive()—which throws CancellationException to terminate. Swallowing CancellationException in try-catch prevents cancellation from taking effect."
    ),
    "structured_en": (
        "To begin with, cancellation in Kotlin coroutines is strictly cooperative. An external scope cannot forcibly terminate a running coroutine; instead, it signals cancellation, requiring the coroutine to check its active state.\n\n"
        "From an architectural standpoint, cancellation points are checkpoints where the coroutine checks its Job status. All standard suspending functions in kotlinx.coroutines act as cancellation points by throwing CancellationException when cancelled.\n\n"
        "In production scenarios, long CPU-bound loops or blocking stream reads lack automatic cancellation points. Engineers must explicitly include ensureActive(), check isActive, or invoke yield() periodically to allow cancellation signals to take effect.\n\n"
        "As for boundary management, resource cleanup should occur within finally blocks. If an unmanaged catch block intercepts CancellationException without re-throwing it, cancellation is silently broken, leaving orphaned background tasks running indefinitely."
    ),
    "deep_senior_en": (
        "Under the hood, coroutine cancellation operates through the Job state machine and the throwing of CancellationException. When job.cancel() is invoked, the Job transitions from Active to Cancelling. It notifies all registered children to cancel and dispatches cancellation to any currently suspended continuation.\n\n"
        "If the coroutine is currently suspended at a cancellation point—such as delay(1000)—the underlying cancellable continuation (CancellableContinuationImpl) immediately resumes the coroutine by throwing CancellationException. This unwinds the continuation stack frame by frame, triggering finally blocks along the way to release resources such as file handles or database locks.\n\n"
        "However, if the coroutine is currently executing active CPU instructions inside a non-suspending loop, it remains oblivious to the Job state until it explicitly calls a cancellation point. The standard library provides three mechanisms for non-suspending code: isActive returns a boolean check of the Job state; ensureActive() throws CancellationException immediately if the Job is no longer active; and yield() checks cancellation while also cooperatively giving up the thread to other pending coroutines on the dispatcher.\n\n"
        "A critical pitfall in production is catching Exception or Throwable. If a developer writes try { ... } catch (e: Exception) { log(e) }, the catch block intercepts CancellationException, treating it as an ordinary error and allowing execution to continue. To handle errors safely, engineers must either catch specific domain exceptions (like IOException) or explicitly re-throw CancellationException: if (e is CancellationException) throw e.\n\n"
        "Finally, if cleanup logic inside a finally block requires invoking another suspending function (such as sending a network abort signal), it must be wrapped in withContext(NonCancellable) { ... }; otherwise, the already-cancelled coroutine will immediately throw CancellationException and abort the cleanup routine."
    ),
}

# ==============================================================================
# ARABIC METADATA DEFINITIONS FOR COR-06 TO COR-10
# ==============================================================================

COR_06_META = {
    "id": "COR-06",
    "questionAr": "قارن بين viewModelScope و lifecycleScope ونطاقات التطبيق العامة (Application Scope) من حيث دورة الحياة وإدارة المهام.",
    "topicAr": "الـ Coroutines والتزامن في Kotlin",
    "evaluates_ar": (
        "- فهم التمايز الدقيق بين دورات حياة viewModelScope و lifecycleScope ونطاقات الـ Application.\n"
        "- إدراك بقاء viewModelScope حياً أثناء الـ Configuration Changes (مثل تدوير الشاشة).\n"
        "- فهم الاستخدام الصحيح لـ repeatOnLifecycle مع lifecycleScope لمنع هدر الموارد في الخلفية.\n"
        "- تحديد الحالات التي تتطلب WorkManager للمهام التي يجب أن تنجو من موت العملية (Process Death)."
    ),
    "why_it_matters_ar": (
        "اختيار النطاق (Scope) الخاطئ في تطبيقات أندرويد هو السبب الأول لتسريب الذاكرة أو انقطاع العمليات غير المكتملة. الـ viewModelScope مرتبط بدورة حياة الـ ViewModel وينتهي عند استدعاء onCleared، وميزته الذهبية أنه ينجو من تدوير الشاشة، مما يجعله المكان الطبيعي لمنطق الأعمال وجلب البيانات. في المقابل، الـ lifecycleScope مربوط بالـ Activity أو Fragment وينتهي مع onDestroy، واستخدامه الأساسي هو جمع الـ Flows عبر repeatOnLifecycle. أما العمليات التي يجب أن تستمر بعد إغلاق الشاشة (مثل مزامنة كاش محلي)، فتتطلب Application Scope محقون بـ SupervisorJob، بينما المهام الدائمة التي يجب أن تنجو من قتل التطبيق بالكامل بالـ OS تتطلب WorkManager."
    ),
    "worked_example_ar": (
        "التوزيع المعماري الصحيح للمهام عبر النطاقات المختلفة:\n"
        "```kotlin\n"
        "// 1. في الـ ViewModel: جلب البيانات وعمليات الشاشة الأساسية\n"
        "class OrderViewModel(\n"
        "    private val repository: OrderRepository\n"
        ") : ViewModel() {\n"
        "    fun submitOrder(order: Order) {\n"
        "        viewModelScope.launch {\n"
        "            repository.submitOrder(order)\n"
        "        }\n"
        "    }\n"
        "}\n\n"
        "// 2. في الـ Fragment: جمع تدفقات الواجهة بأمان مع دورة الحياة\n"
        "class OrderFragment : Fragment() {\n"
        "    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {\n"
        "        super.onViewCreated(view, savedInstanceState)\n"
        "        viewLifecycleOwner.lifecycleScope.launch {\n"
        "            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {\n"
        "                viewModel.uiState.collect { render(it) }\n"
        "            }\n"
        "        }\n"
        "    }\n"
        "}\n"
        "```\n"
        "هذا التوزيع يضمن استمرار إرسال الطلب حتى لو دُوّرت الشاشة، ويوقف جمع الواجهة تلقائياً عند وضع التطبيق في الخلفية."
    ),
    "trade_offs_ar": (
        "يوفر viewModelScope و lifecycleScope إدارة آلية ممتازة دون كتابة كود إلغاء يدوي. ولكن الاعتماد الخاطئ على lifecycleScope لإطلاق طلبات شبكة قد يؤدي لإلغائها بمجرد خروج المستخدم السريع من الشاشة. في المقابل، استخدام Application Scope للمهام الحساسة يضمن اكتمالها، لكنه لا يحميها إذا قامت الـ Low Memory Killer بقتل العملية، وهنا تكون المفاضلة بنقل المهام الحرجة إلى WorkManager."
    ),
    "failure_modes_ar": (
        "من أخطر الأخطاء إطلاق جمع StateFlow داخل lifecycleScope.launch مباشرة دون استخدام repeatOnLifecycle؛ فالكوروتين يظل نشطاً في الخلفية ويستقبل تحديثات الواجهة ويستهلك الرام والبطارية حتى لو كانت الشاشة مخفية تماماً. خطأ آخر هو إطلاق عمليات حفظ هامة داخل lifecycleScope الخاص بـ Fragment، مما يؤدي لإلغائها عند الضغط على زر الرجوع وفقدان بيانات المستخدم."
    ),
    "production_perspective_ar": (
        "في الشركات الكبرى، نعتمد معياراً صارماً: طبقة الـ UI تستخدم lifecycleScope حصراً مع repeatOnLifecycle للرسم والمراقبة. طبقة الـ Presentation تستخدم viewModelScope لجميع طلبات المستخدم والـ UseCases. وإذا وُجدت عملية يجب أن تنتهي مثل إرسال Analytics أو حفظ مسودة، نحقن ApplicationScope أحادي (Singleton) مزوداً بـ SupervisorJob و Dispatchers.Default عبر Hilt."
    ),
    "how_to_answer_ar": (
        "- **السبب المعماري:** وضح الفارق في حدود البقاء: الـ ViewModel ينجو من Configuration Change والـ Lifecycle ينتهي مع الشاشة.\n"
        "- **طريقة الشرح:** اشرح وظيفة كل نطاق: viewModelScope لمنطق الأعمال، و lifecycleScope للواجهة مع repeatOnLifecycle.\n"
        "- **المفاضلات:** بين متى يكفي Application Scope في الذاكرة ومتى يصبح WorkManager إلزامياً.\n"
        "- **أنماط الفشل:** اذكر مشكلة جمع الـ Flow في الخلفية بدون repeatOnLifecycle وإلغاء الطلبات عند التنقل.\n"
        "- **الحل الإنتاجي:** استشهد بحقن ApplicationScope للعمليات المستمرة والالتزام بـ Main-Safety."
    ),
    "talking_points_ar": (
        "اشرح كيف يطبق viewModelScope واجهة CloseableCoroutineScope ويتم إلغاؤه في ViewModel.onCleared. وضح آلية عمل repeatOnLifecycle كـ Suspending Boundary يوقف الكوروتين عند ON_STOP ويعيد إطلاقه عند ON_START. ناقش سبب خطورة استخدام GlobalScope كبديل لـ ApplicationScope."
    ),
    "follow_ups_ar": (
        "- **المحاور:** \"لماذا نفضل repeatOnLifecycle على launchWhenStarted القديمة؟\"\n"
        "  **المرشح:** \"دوال launchWhenX القديمة كانت تقوم بتعليق الكوروتين فقط عند نزول دورة الحياة عن الحالة المطلوبة، لكنها لم تكن تلغي الـ Flow Producer في الخلفية، مما يعني استمرار بث البيانات واستهلاك الموارد. أما repeatOnLifecycle فتقوم بإلغاء الكوروتين والـ Flow تماماً عند ON_STOP، وتعيد إطلاقه من جديد عند ON_START، مما يوفر البطارية والذاكرة بالكامل.\"\n\n"
        "- **المحاور:** \"ماذا يحدث لـ viewModelScope عند تدوير شاشة الهاتف؟\"\n"
        "  **المرشح:** \"لا يتأثر إطلاقاً ويستمر في العمل؛ لأن الـ ViewModel يُحفظ في ViewModelStore عبر الـ Configuration Change ولا يتم استدعاء onCleared، وبالتالي تظل الكوروتينات قيد التنفيذ وتعود الواجهة الجديدة لتستقبل البيانات فور اكتمال البناء.\"\n\n"
        "- **المحاور:** \"متى تختار WorkManager بدلاً من إنشاء Application CoroutineScope مخصص؟\"\n"
        "  **المرشح:** \"نختار WorkManager عندما تكون المهمة حاسمة ويجب أن تكتمل حتى لو قُتلت عملية التطبيق من قِبل النظام (Process Death) أو أُعيد تشغيل الهاتف، مثل رفع ملفات كبيرة أو مزامنة قواعد البيانات؛ لأن WorkManager يخزن المهام في قاعدة بيانات SQLite محلية ويعيد جدولتها عبر JobScheduler.\""
    ),
    "self_check_ar": (
        "تأكد من تغطية: مقارنة دورة حياة viewModelScope و lifecycleScope؛ توضيح دور repeatOnLifecycle؛ تعريف Application Scope ومتى يُحقن؛ والتمييز بين العمليات في الذاكرة والمهام المستمرة عبر WorkManager."
    ),
    "references_ar": (
        "- [Android lifecycle-aware coroutines](https://developer.android.com/topic/libraries/architecture/coroutines#lifecycle-aware) — التوثيق الرسمي للنطاقات المدارة بدورة الحياة.\n"
        "- [RepeatOnLifecycle API guidance](https://developer.android.com/reference/kotlin/androidx/lifecycle/package-summary#repeatOnLifecycle) — الدليل الرسمي لاستخدام repeatOnLifecycle.\n\n"
        "تمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13."
    ),
    "quick_answer_ar": (
        "الـ viewModelScope ينجو من تدوير الشاشة ويُلغى تلقائياً عند onCleared، وهو المخصص لمنطق الأعمال وعرض الشاشة. والـ lifecycleScope مربوط بالـ Activity أو Fragment ويُلغى عند onDestroy، ونستخدمه مع repeatOnLifecycle لمراقبة تدفقات الواجهة بأمان. أما Application Scope فيُستخدم للمهام التي يجب أن تستمر بعد إغلاق الشاشة داخل عمر الـ Process."
    ),
    "best_answer_ar": (
        "المقارنة بين النطاقات في أندرويد بتعتمد بالأساس على تحديد مالك دورة الحياة (Lifecycle Owner) والهدف من العملية.\n\n"
        "الـ viewModelScope هو النطاق الأساسي لمنطق الأعمال وتحميل بيانات الشاشات؛ ميزته الكبرى إنه بينجو من الـ Configuration Changes زي تدوير الشاشة، وبيتلغي تلقائياً لما الـ ViewModel يتدمر نهائياً في onCleared، وده بيمنع إعادة تحميل البيانات مع كل تدوير.\n\n"
        "الـ lifecycleScope مربوط مباشرة بالـ Activity أو الـ Fragment، وعمره بينتهي مع onDestroy. استخدامه المثالي هو مراقبة وتحديث الـ UI، ولازم نستخدمه مع repeatOnLifecycle(STARTED) عشان نضمن وقف جمع الـ Flows لما المستخدم يحط التطبيق في الخلفية، ونوفر البطارية والذاكرة.\n\n"
        "أما لو عندنا عملية لازم تكمل حتى لو المستخدم قفل الشاشة ومشي، زي حفظ مسودة في قاعدة البيانات أو إرسال Analytics، فبنستخدم Application Scope محقون بـ SupervisorJob.\n\n"
        "ولو العملية حاسمة ولازم تكتمل حتى لو النظام قتل التطبيق بالكامل أو الموبايل رستر، بنسيب الكوروتينز ونروح فوراً لـ WorkManager."
    ),
    "deep_answer_ar": (
        "على مستوى التنفيذ الداخلي، يرتبط viewModelScope بالـ ViewModel عبر خاصية ممتدة تنشئ كائناً من نوع CloseableCoroutineScope يحمل سياقاً مكوناً من SupervisorJob() + Dispatchers.Main.immediate. عند تدمير الشاشة نتيجة Configuration Change، يحتفظ الـ ViewModelStoreOwner بنفس كائن الـ ViewModel، وبالتالي تظل شجرة الـ Jobs نشطة دون أي انقطاع. وعندما يغادر المستخدم الشاشة نهائياً، يستدعي النظام ViewModel.clear() التي تمر على كل الـ Closeables المسجلة وتستدعي cancel()، مما يرسل إشارة إلغاء شلالية لكل المهام الفرعية.\n\n"
        "في المقابل، lifecycleScope هو تطبيق لـ LifecycleCoroutineScopeImpl يرث من CoroutineScope وينصت لأحداث دورة الحياة عبر LifecycleEventObserver. استدعاء lifecycleScope.launch العادي يمثل فخاً شائعاً؛ لأنه يبدأ التنفيذ ويستمر حتى تدمير الـ Lifecycle بالكامل. لذلك تم تقديم repeatOnLifecycle؛ وهو عبارة عن دالة معلقة تعلق المستدعي وتنشئ كوروتين جديداً فور وصول الحالة إلى Target State (مثل STARTED)، وتقوم بإلغائه فور نزول الحالة عن هذا الحد (عند حدوث ON_STOP). هذا التعليق والإلغاء الدوري يعيد ضبط الـ Upstream Flows ويحرر موارد الذاكرة والاتصالات.\n\n"
        "بالنسبة لـ Application Scope، فيتم بناؤه معمارياً في الـ Dependency Injection Graph كـ Singleton Scope يحتوي على SupervisorJob() + Dispatchers.Default. يتيح هذا النطاق إطلاق مهام لا تنتمي لشاشة معينة وتستمر طالما أن الـ Application Process حية في الذاكرة. ولكن من الأخطاء الجسيمة الاعتماد عليه في عمليات الدفع أو مزامنة الملفات الكبيرة؛ فالنظام في أندرويد يستطيع إنهاء العملية (Process Death) في أي لحظة تحت وطأة نقص الذاكرة، مما يجهض الكوروتينات تماماً. في هذه السيناريوهات الحرجة، يعتبر WorkManager هو الحل الهندسي الوحيد الصالح للإنتاج لأنه يضمن الثبات والتنفيذ عبر الجدولة الصارمة لنظام التشغيل."
    ),
}

COR_07_META = {
    "id": "COR-07",
    "questionAr": "ما هي وظائف الموزعات Dispatchers.Main و IO و Default و Unconfined ومتى تختار كلاً منها؟",
    "topicAr": "الـ Coroutines والتزامن في Kotlin",
    "evaluates_ar": (
        "- فهم طبيعة ودور كل موزع من موزعات كوتلن الأربعة الأساسية.\n"
        "- معرفة قيود Dispatchers.Main ومخاطر حظر ثريد الواجهة.\n"
        "- استيعاب حجم مجمعات الخيوط في Dispatchers.Default و Dispatchers.IO والاشتراك في CoroutineScheduler.\n"
        "- فهم سلوك Dispatchers.Unconfined والسبب وراء تجنبه في الكود الإنتاجي."
    ),
    "why_it_matters_ar": (
        "الـ CoroutineDispatcher هو المسؤول عن تحديد خيط المعالجة أو مجمع الخيوط الذي سينفذ الكوروتين. الاختيار الخاطئ للـ Dispatcher يتسبب في مشاكل خطيرة: تشغيل كود حظري أو حسابي على Dispatchers.Main يؤدي لتجميد الشاشة وسقوط الإطارات ورمي ANR؛ وتشغيل عمليات I/O حظرية على Dispatchers.Default يؤدي لتجويع أنوية المعالج وحرمان المهام الأخرى؛ واستخدام Dispatchers.Unconfined يجعل التنفيذ يقفز عشوائياً بين خيوط مختلفة بطريقة غير متوقعة. فهم الفروق الدقيقة يضمن أداءً فائقاً واستجابة سلسة للتطبيق."
    ),
    "worked_example_ar": (
        "توزيع مراحل تصدير تقرير مالي باحترافية عبر الـ Dispatchers:\n"
        "```kotlin\n"
        "fun exportFinancialReport() {\n"
        "    // 1. نبدأ على Main لعرض شريط التحميل للواجهة\n"
        "    viewModelScope.launch(Dispatchers.Main) {\n"
        "        _uiState.value = ExportState.Loading\n\n"
        "        // 2. عمليات حسابية ثقيلة لمعالجة الأرقام ننقلها لـ Default (CPU)\n"
        "        val summary = withContext(Dispatchers.Default) {\n"
        "            calculateFinancialMetrics(rawTransactions)\n"
        "        }\n\n"
        "        // 3. كتابة ملف الـ PDF على القرص نرسلها لـ IO (Disk Blocking)\n"
        "        val pdfFile = withContext(Dispatchers.IO) {\n"
        "            writePdfToDisk(summary)\n"
        "        }\n\n"
        "        // 4. نعود تلقائياً لـ Main لعرض إشعار النجاح للواجهة\n"
        "        _uiState.value = ExportState.Success(pdfFile)\n"
        "    }\n"
        "}\n"
        "```\n"
        "بهذا التقسيم، لا تتعطل الواجهة بالحسابات الثقيلة، ولا تحظر عمليات القرص أنوية المعالج."
    ),
    "trade_offs_ar": (
        "تحديد الـ Dispatcher المناسب يضمن استغلالاً مثالياً لعتاد الهاتف دون استنزاف الذاكرة. ولكن التبديل المفرط بين الموزعات في عمليات بالغة الصغر يضيف حمولة جدولة غير ضرورية. القاعدة هي وضع العمليات الحظرية على IO، والعمليات الحسابية الكبيرة على Default، وإبقاء خيط الواجهة خفيفاً وسريعاً."
    ),
    "failure_modes_ar": (
        "أكبر خطأ كارثي هو تنفيذ استدعاء حظري صريح مثل Thread.sleep أو قراءة ملف متزامنة داخل Dispatchers.Main، مما يجمد معالجة اللمس ويظهر خطأ ANR. خطأ آخر هو تنفيذ مئات طلبات الشبكة الحظرية القديمة على Dispatchers.Default، مما يؤدي لشغل كل أنوية المعالج المحدودة وإيقاف أي حسابات أخرى في التطبيق."
    ),
    "production_perspective_ar": (
        "في المشروعات الإنتاجية الكبرى، نمنع كتابة Dispatchers المباشرة في الكود (Hardcoded Dispatchers)؛ بل نحقنها عبر واجهة مخصصة مثل CoroutineDispatchersProvider في الـ Constructor. هذا النمط يتيح لنا استبدالها بـ StandardTestDispatcher أو UnconfinedTestDispatcher في اختبارات الـ Unit Tests للتحكم الدقيق في التوقيت والتحقق من صحة الكود."
    ),
    "how_to_answer_ar": (
        "- **السبب المعماري:** اشرح أن الـ Dispatcher يوجه الكوروتين للثريد المناسب لطبيعة الحمل التشغيلي.\n"
        "- **طريقة الشرح:** فصّل دور كل موزع: Main للواجهة، Default للحسابات ومرتبط بعدد الأنوية، IO لعمليات الإدخال والإخراج ويتمدد حتى 64 ثريد، و Unconfined بدون قيود.\n"
        "- **المفاضلات:** اشرح لماذا لا يجب خلط عمليات الـ I/O مع عمليات الـ CPU.\n"
        "- **أنماط الفشل:** اذكر تجويع الأنوية بالـ I/O على Default، وتجميد الـ Main Thread بالعمليات الحظرية.\n"
        "- **الحل الإنتاجي:** أكد على حقن الموزعات لاختبار الكود والالتزام بمبدأ Main-Safety."
    ),
    "talking_points_ar": (
        "اشرح كيف يشترك Dispatchers.Default و Dispatchers.IO في محرك CoroutineScheduler الداخلي بنظام سرقة المهام (Work-stealing). وضح كيف يعمل Dispatchers.Main.immediate لتخطي الجدولة في الـ MessageQueue إذا كان التنفيذ على خيط الواجهة بالفعل."
    ),
    "follow_ups_ar": (
        "- **المحاور:** \"لماذا يمتلك Dispatchers.IO حداً أقصى يصل إلى 64 ثريد بينما Dispatchers.Default مقيد بعدد الأنوية؟\"\n"
        "  **المرشح:** \"لأن مهام Dispatchers.Default تستهلك المعالج بنسبة 100%، وتشغيل ثريدات أكثر من عدد الأنوية سيؤدي لتضييع وقت الـ CPU في التبديل بين الخيوط (Context Switching) دون فائدة. بينما مهام Dispatchers.IO تقضي معظم وقتها معلقة في انتظار رد السيرفر أو القرص في الـ Kernel، لذا نحتاج لثريدات إضافية لتشغيل طلبات أخرى بالتوازي أثناء انتظار الخيوط المحظورة.\"\n\n"
        "- **المحاور:** \"ما هو دور Dispatchers.Main.immediate وما الفرق بينه وبين Dispatchers.Main العادي؟\"\n"
        "  **المرشح:** \"الـ Dispatchers.Main العادي يقوم دائماً بعمل handler.post للـ Runnable في طابور الـ Looper حتى لو كنت بالفعل على الـ Main Thread، مما يؤخر التنفيذ للإطار التالي. أما Dispatchers.Main.immediate فيفحص أولاً: لو كان الكود يعمل حالياً على الـ Main Thread ينفذه فوراً وبشكل متزامن دون أي تأخير، ويوفر دورة إضافية في الـ Event Loop.\"\n\n"
        "- **المحاور:** \"هل هناك أي استخدام صالح لـ Dispatchers.Unconfined في أندرويد؟\"\n"
        "  **المرشح:** \"في الكود الإنتاجي لتطبيقات أندرويد، استخدامه غير محبذ نهائياً ومحفوف بالمخاطر لأنك تفقد السيطرة على الثريد الذي يستأنف الكود. لكنه يُستخدم أحياناً في كتابة اختبارات الوحدة السريعة أو العمليات البرمجية الداخلية الخاصة جداً التي تتطلب تنفيذاً فورياً دون تكلفة جدولة.\""
    ),
    "self_check_ar": (
        "تحقق من إجابتك: ذكر الموزعات الأربعة بالتفصيل؛ شرح حجم مجمع الخيوط لكل منها؛ تبرير سبب عدم تشغيل I/O على Default؛ وبيان مخاطر Unconfined في بيئات الإنتاج."
    ),
    "references_ar": (
        "- [Kotlin coroutine dispatchers](https://kotlinlang.org/docs/coroutine-context-and-dispatchers.html#dispatchers-and-threads) — التوثيق الرسمي لموزعات كوتلن.\n"
        "- [Android dispatchers guide](https://developer.android.com/kotlin/coroutines#use-coroutines-for-main-safety) — استخدام الموزعات لتحقيق الأمان في أندرويد.\n\n"
        "تمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13."
    ),
    "quick_answer_ar": (
        "موزع Dispatchers.Main مخصص لخيط الواجهة وتحديث الشاشات. وموزع Dispatchers.Default مخصص للعمليات الحسابية المعقدة ومربوط بعدد أنوية المعالج الفيزيائية. وموزع Dispatchers.IO مخصص لعمليات القرص والشبكة الحظرية بمجمع يتسع لـ 64 ثريد. أما Dispatchers.Unconfined فيبدأ على ثريد المستدعي ويستأنف في أي ثريد، ولا يُستخدم في الإنتاج."
    ),
    "best_answer_ar": (
        "الموزعات (Dispatchers) في كوتلن هي اللي بتحدد الكوروتين هيتنفذ على أي ثريد، ولازم تختار الموزع المناسب لطبيعة الشغل:\n\n"
        "الـ Dispatchers.Main محصور على خيط الواجهة في أندرويد؛ بنستخدمه لتعديل الـ Views وحالة الـ Compose ومعالجة اللمس، وممنوع نهائياً تشغل عليه أي كود حظري أو حسابي تقيل عشان متجمدش الشاشة وتطلع ANR.\n\n"
        "الـ Dispatchers.Default مخصص لعمليات المعالج المكثفة (CPU-bound) زي معالجة الصور، التشفير، أو عمل Parse لملفات JSON ضخمة؛ المجمع بتاعه مربوط بعدد أنوية المعالج بحد أدنى 2 ثريد، عشان يمنع التبديل العشوائي بين الثريدات.\n\n"
        "الـ Dispatchers.IO مخصص لعمليات الإدخال والإخراج الحظرية (Blocking I/O) زي قراءة الملفات من القرص أو استدعاءات قواعد البيانات القديمة؛ المجمع بتاعه مرن وبيتمدد لحد 64 ثريد عشان يستوعب انتظار العمليات في الـ Kernel.\n\n"
        "أما Dispatchers.Unconfined، فبيبدأ على نفس ثريد المستدعي ويكمل بعد التعليق على الثريد اللي استدعاه؛ سلوكه غير متوقع وممنوع نستخدمه في كود الإنتاج الطبيعي.\n\n"
        "في الشركات الكبيرة، بنحقن الـ Dispatchers دي كـ Dependencies عشان نقدر نختبرها بسهولة في الـ Unit Tests."
    ),
    "deep_answer_ar": (
        "على مستوى العمارة الداخلية لمكتبة kotlinx.coroutines، يشترك Dispatchers.Default و Dispatchers.IO في نفس المحرك الأساسي وهو CoroutineScheduler. هذا المحرك هو مجمع خيوط متقدم يعتمد على خوارزمية سرقة المهام (Work-stealing Algorithm) مع وجود طوابير مهام محلية لكل ثريد وطابور عام مشترك، مما يقلل بشكل كبير من التنافس على الأقفال (Lock Contention).\n\n"
        "في Dispatchers.Default، يتم ضبط حجم مجمع الخيوط الأساسي ليطابق عدد الأنوية المتاحة عبر Runtime.getRuntime().availableProcessors(). هذا التقييد الصارم هدفه منع الإفراط في إنشاء خيوط تتنافس على المعالج، وهو ما يضمن بقاء الـ CPU Caches دافئة وفعالة أثناء الحسابات الرياضية المكثفة.\n\n"
        "في المقابل، تم بناء Dispatchers.IO كواجهة محددة (LimitingDispatcher) فوق نفس الـ CoroutineScheduler. عندما يُحظر أحد الخيوط في عملية قراءة قرص أو استدعاء شبكة عبر Socket قديم، يكتشف المحرك أن الثريد في حالة Blocking State، فيقوم بإنشاء خيوط إضافية ديناميكياً لتلبية الطلبات المعلقة حتى سقف 64 ثريداً. ونظراً لأنهما يشتركان في نفس مجمع الخيوط، فإن التبديل بين Default و IO باستخدام withContext غالباً ما يتم بسلاسة تامة وعلى نفس الـ Native Thread دون الحاجة لـ OS Context Switch إذا كانت حصة المعالج تسمح بذلك.\n\n"
        "أما بالنسبة لـ Dispatchers.Main على أندرويد، فهو تطبيق لكلاس HandlerContext الذي يغلف Handler(Looper.getMainLooper()). وعند استخدام Dispatchers.Main.immediate، يقوم الموزع بفحص Thread.currentThread()؛ فإذا كان التنفيذ جارياً بالفعل على ثريد الـ Main، يتم تنفيذ الكود فوراً وبصورة متزامنة دون إرسال رسالة إلى طابور Looper MessageQueue، مما يوفر وقتاً ثميناً ويضمن استقرار معدل الـ 120 إطاراً في الثانية."
    ),
}

COR_08_META = {
    "id": "COR-08",
    "questionAr": "هل يعتمد Dispatchers.Main على ثريد الواجهة (UI Thread)؟ وكيف يدير Dispatchers.IO مجمع الخيوط (Thread Pool)؟",
    "topicAr": "الـ Coroutines والتزامن في Kotlin",
    "evaluates_ar": (
        "- فهم التبعية الصارمة لـ Dispatchers.Main على ثريد الـ Looper الرئيسي في أندرويد.\n"
        "- معرفة عواقب استدعاء الأكواد الحظرية على Main ومسببات الـ ANR.\n"
        "- فهم البنية المرنة لمجمع خيوط Dispatchers.IO وسقفه الأعلى (64 ثريد).\n"
        "- إدراك الاشتراك في محرك CoroutineScheduler بين IO و Default."
    ),
    "why_it_matters_ar": (
        "الخلط بين مفهوم تعليق الكوروتين ومفهوم الثريد الفعلي يقود مطوري أندرويد لارتكاب أخطاء كارثية. Dispatchers.Main ليس ثريداً جديداً، بل هو خيط الواجهة الوحيد (Single UI Thread) للتطبيق؛ فأي عملية حظر للثريد (Blocking Call) داخله تجمد معالجة رسائل النظام وتتسبب فوراً في بطء وتشنج الشاشة ورمي خطأ ANR. ومن ناحية أخرى، مجمع Dispatchers.IO مصمم خصيصاً لابتلاع عمليات الحظر دون خنق النظام؛ فهو مجمع خيوط مرن يتسع حتى 64 خيطاً لضمان عدم توقف العمليات أثناء انتظار إشارات الـ I/O من نواة النظام. فهم هذا التمايز هو الفارق بين مهندس يصمم تطبيقات سلسة وآخر يعاني من تجميد الشاشات."
    ),
    "worked_example_ar": (
        "مقارنة عملية بين تأثير الحظر على Main مقابل التعامل مع IO:\n"
        "```kotlin\n"
        "// ❌ كارثة: حظر ثريد الواجهة يسبب ANR فوري\n"
        "viewModelScope.launch(Dispatchers.Main) {\n"
        "    // Thread.sleep يوقف الـ Main Looper تماماً!\n"
        "    Thread.sleep(5000) // يتجمد التطبيق وتظهر رسالة ANR\n"
        "}\n\n"
        "// ✅ الاستخدام الصحيح لمجمع IO المرن:\n"
        "viewModelScope.launch(Dispatchers.IO) {\n"
        "    // تشغيل 50 عملية قراءة متزامنة لقاعدة بيانات قديمة\n"
        "    repeat(50) {\n"
        "        launch {\n"
        "            // كل عملية ستحظر ثريداً من مجمع IO، ولكن المجمع يتمدد لخدمتها\n"
        "            legacyDatabase.blockingRead()\n"
        "        }\n"
        "    }\n"
        "    // ثريد الواجهة يظل حراً بنسبة 100% وبدون أي سقوط للفريمات\n"
        "}\n"
        "```\n"
        "في الكود الثاني، مجمع IO يتوسع ذاتياً لامتصاص عمليات الانتظار دون المساس بسلاسة الشاشة."
    ),
    "trade_offs_ar": (
        "يوفر Dispatchers.IO سعة خيوط عالية (64 خيطاً) للتعامل مع العمليات الحظرية القديمة، لكن التوسع غير المنضبط في إطلاق مئات الكوروتينات الحظرية قد يستهلك ذاكرة الـ Native Stack. الحل الأمثل في أندرويد الحديث هو التحول إلى واجهات غير حظرية بالكامل (Non-blocking APIs) مثل Room Coroutines و Retrofit Suspend، واللجوء لـ IO فقط عند التعامل مع مكتبات C++ أو Java قديمة."
    ),
    "failure_modes_ar": (
        "أخطر نمط فشل هو استدعاء Binder IPC متزامن أو قراءة SharedPreferences متزامنة على Dispatchers.Main تحت وطأة ضغط بدء التشغيل، مما يؤدي لـ ANR فوري. خطأ آخر هو محاولة عمل عمليات معالجة صور ثقيلة على Dispatchers.IO بإنشاء عشرات الخيوط التي تتنافس على المعالج وتسبب استنزافاً هائلاً للطاقة وتباطؤاً عاماً للجهاز."
    ),
    "production_perspective_ar": (
        "في بيئة الإنتاج، نفعل أداة StrictMode في نسخ التطوير (Debug Builds) لاكتشاف أي قراءة قرص أو اتصال شبكة غير مقصود على خيط الواجهة فوراً. كما نراقب مؤشرات الـ ANR Rate في Google Play Console ونحرص على ألا تتجاوز 0.47% (معيار Google لنظافة التطبيقات)، مع التأكد من أن جميع طبقات الـ Repositories تعتمد على دوال معلقة Main-Safe داخلياً."
    ),
    "how_to_answer_ar": (
        "- **السبب المعماري:** أجب بوضوح: نعم، Dispatchers.Main يعتمد كلياً على الـ Main UI Thread المربوط بـ Looper.\n"
        "- **طريقة الشرح:** اشرح آلية الـ Handler والـ MessageQueue وكيف يؤدي الحظر لـ ANR.\n"
        "- **المفاضلات:** اشرح مجمع خيوط IO المرن وسقفه الأعلى (64) واشتراكه في الـ CoroutineScheduler.\n"
        "- **أنماط الفشل:** اذكر تجمد الشاشة بالـ Thread.sleep واستدعاءات قواعد البيانات الحظرية.\n"
        "- **الحل الإنتاجي:** استشهد بأدوات المراقبة مثل StrictMode وأفضلية استخدام الواجهات المعلقة الحقيقية."
    ),
    "talking_points_ar": (
        "اشرح الربط الداخلي بين HandlerContext و Handler(Looper.getMainLooper()). وضح خاصية Dispatchers.Main.immediate وكيف توفر دورة جدولة في الـ MessageQueue. فصّل كيفية عمل LimitingDispatcher فوق CoroutineScheduler لإدارة سقف الـ 64 خيطاً."
    ),
    "follow_ups_ar": (
        "- **المحاور:** \"هل يؤدي استخدام delay() داخل Dispatchers.Main إلى تجميد الشاشة؟\"\n"
        "  **المرشح:** \"إطلاقاً؛ لأن دالة delay() هي دالة معلقة غير حظرية (Non-blocking). تقوم دالة delay بجدولة رسالة استئناف في طابور الـ Looper وتترك الثريد حراً فوراً ليرسم إطارات الشاشة ويعالج لمسات المستخدم بسلاسة، على عكس Thread.sleep التي تحظر الثريد نفسه.\"\n\n"
        "- **المحاور:** \"كيف يتعامل محرك CoroutineScheduler مع المهام إذا تم استنزاف الـ 64 ثريد في مجمع IO؟\"\n"
        "  **المرشح:** \"إذا وصل مجمع IO إلى الحد الأقصى وهو 64 ثريداً وجميعها محظورة في عمليات إدخال وإخراج، يتم وضع المهام الجديدة في طابور انتظار (Queue). وفور انتهاء أي ثريد من مهمته وعودته، يتم سحب المهمة التالية من الطابور وتنفيذها فوراً دون إنشاء خيوط جديدة تتجاوز السقف المحدد.\"\n\n"
        "- **المحاور:** \"هل تستهلك ثريدات Dispatchers.IO ذاكرة مساوية للـ JVM Heap؟\"\n"
        "  **المرشح:** \"لا، خيوط المعالجة تحجز ذاكرتها من الـ Native Memory الخاصة بنظام التشغيل لحجز مكدس الاستدعاءات (Thread Call Stack)، بحجم يتراوح بين 512KB إلى 1MB لكل خيط، بينما كائنات الـ Continuation نفسها تعيش على الـ JVM Heap.\""
    ),
    "self_check_ar": (
        "تحقق من إجابتك: التأكيد على اعتماد Main على الـ UI Thread؛ شرح آلية مجمع IO وسقفه المكون من 64 خيطاً؛ توضيح الفارق بين التعليق والحظر على ثريد الواجهة؛ وإبراز أثر ذلك على مؤشرات ANR."
    ),
    "references_ar": (
        "- [Android Main thread and looper](https://developer.android.com/guide/components/processes-and-threads) — آليات عمل ثريد الواجهة والـ Looper في أندرويد.\n"
        "- [Kotlin CoroutineScheduler source](https://github.com/Kotlin/kotlinx.coroutines/blob/master/kotlinx-coroutines-core/jvm/src/scheduling/CoroutineScheduler.kt) — كود مصدر محرك جدولة الخيوط وسرقة المهام في كوتلن.\n\n"
        "تمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13."
    ),
    "quick_answer_ar": (
        "نعم، يعتمد Dispatchers.Main كلياً على ثريد الواجهة الرئيسي (UI Thread) عبر Looper.getMainLooper()، وأي عملية حظر بداخله تتسبب في ANR. أما Dispatchers.IO فيعتمد على مجمع خيوط مرن (Elastic Thread Pool) يتسع حتى 64 ثريداً مصمم لامتصاص عمليات القراءة والكتابة الحظرية دون التأثير على أداء المعالج."
    ),
    "best_answer_ar": (
        "الإجابة المباشرة: نعم، Dispatchers.Main بيشتغل بالكامل على الـ Android UI Thread الوحيد المربوط بـ Looper.getMainLooper().\n\n"
        "ده معناه إن أي عملية حظر (Blocking Call) زي Thread.sleep أو قراءة ملف متزامنة هتحظر الـ Event Loop بالكامل، وهتمنع الـ Choreographer من رسم فريمات الشاشة وتوقع التطبيق في خطأ ANR شهير بعد 5 ثوانٍ.\n\n"
        "أما Dispatchers.IO، فهو مش ثريد واحد؛ ده مجمع خيوط مرن (Elastic Thread Pool) بيقدر يتمدد ديناميكياً لحد 64 ثريد (أو عدد الأنوية أيهما أكبر) عشان يستوعب عمليات القراءة والشبكة اللي بتفضل معلقة في انتظار رد الـ Kernel.\n\n"
        "الميزة العبقرية في كوتلن هي إن Dispatchers.IO و Dispatchers.Default بيشتركوا في نفس المحرك الداخلي اللي اسمه CoroutineScheduler؛ ولما ثريد من بتوع IO يخلص شغلته الحظرية، ممكن يتحول لخدمة مهام تانية بنظام سرقة المهام (Work-stealing).\n\n"
        "القاعدة الذهبية عندنا في أندرويد: الواجهة للرسم فقط على Main، وكل ما هو حظري أو شبكة يروح لـ IO عبر withContext."
    ),
    "deep_answer_ar": (
        "تفصيلياً، يرتبط Dispatchers.Main بنظام أندرويد عبر فئة HandlerContext في مكتبة kotlinx-coroutines-android. عندما يجدول الكوروتين استئنافاً على Dispatchers.Main، ينادي الكود داخلياً handler.post(runnable) موجهاً إلى Main Looper MessageQueue. وإذا كان خيط الواجهة محظوراً في عملية قراءة متزامنة لقاعدة بيانات SQLite أو حظر Binder متزامن، فإن طابور الرسائل يتوقف تماماً وتفشل معالجة أحداث اللمس ونداءات VSYNC، مما يدفع الـ ActivityManagerService لرمي حدث ANR. ولتخفيف هذه التكلفة، توفر كوتلن Dispatchers.Main.immediate التي تفحص ما إذا كان الثريد الحالي هو Main Thread، لتنفذ الـ Runnable فورياً دون المرور بدورة posting جديدة في طابور الرسائل.\n\n"
        "على الطرف الآخر، Dispatchers.IO ليس ExecutorService منفصلاً كما يظن البعض؛ بل هو تطبيق لـ LimitingDispatcher يعمل فوق محرك CoroutineScheduler الموحد. يحدد هذا الموزع سقف التوازي الافتراضي عبر خاصية النظام kotlinx.coroutines.io.parallelism، وتكون قيمته الافتراضية 64 خيطاً كحد أقصى. فعندما يدخل خيط في حالة استدعاء نظام حظري (مثل read من ملف أو socket)، يغير المحرك حالة الثريد إلى BLOCKING، ويسمح بإنشاء ثريدات إضافية لخدمة العمليات الحسابية المتزامنة دون المساس بحصة خيوط Dispatchers.Default المقيدة بعدد الأنوية.\n\n"
        "هذا التصميم المشترك يقلل بشكل مذهل من تكلفة الـ Context Switching واستهلاك ذاكرة الـ Native RAM؛ فالنظام لا يقوم بإنشاء مجمعات خيوط معزولة تلتهم موارد الموبايل، بل يدير خيوط التنفيذ كحوض مشترك، مما يجعل التبديل بين الحسابات وتخزين الملفات عبر withContext عملية فائقة السرعة وعالية الكفاءة."
    ),
}

COR_09_META = {
    "id": "COR-09",
    "questionAr": "ما هي دالة withContext؟ ومتى يجب استخدامها لتحقيق مبدأ Main-Safety؟",
    "topicAr": "الـ Coroutines والتزامن في Kotlin",
    "evaluates_ar": (
        "- فهم طبيعة withContext كدالة معلقة تغير السياق تسلسلياً دون إطلاق كوروتين جديد.\n"
        "- تطبيق مبدأ Main-Safety في طبقات الـ Repository والـ Data Sources.\n"
        "- التمييز بين withContext و launch/async من حيث القيمة المعادة وإدارة الـ Job.\n"
        "- إدراك خطورة تمرير كائنات Job جديدة داخل withContext(Job())."
    ),
    "why_it_matters_ar": (
        "دالة withContext هي حجر الزاوية لتطبيق مبدأ Main-Safety في هندسة تطبيقات أندرويد الحديثة. بدلاً من إجبار طبقة الواجهة (UI / ViewModel) على تذكر أسماء الموزعات والتخبط في اختيارها، تقوم دالة withContext بتمكين الدوال المعلقة في الـ Repositories من التبديل الذاتي إلى Dispatchers.IO أو Dispatchers.Default، وتنفيذ العمليات الحظرية ثم إعادة النتيجة مباشرة للمستدعي على خيط الواجهة دون إطلاق كوروتين جديد أو كسر تسلسل الكود. فهم آلية عملها يضمن كتابة كود نظيف، آمن تماماً، وسهل القراءة والاختبار."
    ),
    "worked_example_ar": (
        "تطبيق Main-Safety في مستودع بيانات مستخدم باستخدام withContext:\n"
        "```kotlin\n"
        "class UserRepository(\n"
        "    private val localDao: UserDao,\n"
        "    private val ioDispatcher: CoroutineDispatcher = Dispatchers.IO\n"
        ") {\n"
        "    // الدالة آمنة تماماً للاستدعاء من خيط الواجهة (Main-Safe)\n"
        "    suspend fun getUserProfile(userId: String): UserProfile = withContext(ioDispatcher) {\n"
        "        // 1. يتحول التنفيذ إلى ثريد من مجمع IO\n"
        "        val entity = localDao.findUserById(userId)\n"
        "        // 2. معالجة البيانات وتحويلها لـ Domain Model\n"
        "        UserProfile.fromEntity(entity)\n"
        "    } // 3. يعود التنفيذ تلقائياً لنفس ثريد المستدعي (مثلاً Main Thread)\n"
        "}\n"
        "```\n"
        "يستطيع الـ ViewModel استدعاء الدالة ببساطة: val profile = repository.getUserProfile(id) وتحديث الواجهة مباشرة بسطر واحد."
    ),
    "trade_offs_ar": (
        "توفر withContext تسلسلاً منطقياً وأماناً معمارياً فائقاً، وتلغي الحاجة للتعامل مع كائنات Job أو Deferred. في المقابل، يجب تجنب استدعاء withContext داخل حلقات تكرارية مكثفة لتغيير الثريد مع كل عنصر؛ لأن تكرار التبديل يضيف حمولة جدولة غير لازمة، والأفضل تغليف الحلقة بأكملها داخل كتلة withContext واحدة."
    ),
    "failure_modes_ar": (
        "من أخطر الأخطاء البرمجية كتابة withContext(Dispatchers.IO + Job())؛ فتمرير Job() جديد يكسر الرابط الهرمي مع الكوروتين المستدعي، وإذا تم إلغاء شاشة التطبيق، لن يستلم الكود داخل withContext إشارة الإلغاء وسيستمر في العمل كـ Zombie Task. خطأ آخر هو استخدام async بدلاً من withContext لعمليات غير متوازية، مما يضيف كائنات Deferred وتعقيد لا داعي له."
    ),
    "production_perspective_ar": (
        "في معمارية التطبيقات الكبرى، نلزم جميع المطورين بتطبيق قاعدة: 'Any public suspend function must be main-safe'. نحقن الـ Dispatchers عبر الـ Constructor Injection لضمان إمكانية استبدالها بـ StandardTestDispatcher في اختبارات الوحدة، ونمنع تماماً تمرير Dispatchers صراحة من شاشات Jetpack Compose أو الـ ViewModels."
    ),
    "how_to_answer_ar": (
        "- **السبب المعماري:** عرّف withContext كدالة معلقة تغير سياق التنفيذ وتعيد النتيجة مباشرة دون إطلاق كوروتين جديد.\n"
        "- **طريقة الشرح:** اشرح كيف تحقق مبدأ Main-Safety بنقل العمليات الحظرية لـ IO وإرجاع النتيجة للـ Main Thread.\n"
        "- **المفاضلات:** قارن بين withContext و async/await لعملية مفردة ووضح لماذا withContext أنظف وأخف.\n"
        "- **أنماط الفشل:** حذر بشدة من فخ تمرير Job() جديد داخل withContext وتأثيره على كسر الإلغاء.\n"
        "- **الحل الإنتاجي:** أكد على ميثاق الأمان Main-Safe وحقن الموزعات لاختبار الكود."
    ),
    "talking_points_ar": (
        "اشرح كيف يطبق كوتلن مسار Undispatched السريع عندما يكون الـ Dispatcher المستهدف مطابقاً للـ Dispatcher الحالي. وضح كيف تنشئ المكتبة كائن DispatchedCoroutine لتعليق المستدعي وإعادة جدولة الاستئناف عند الانتهاء مع تمرير استثناءات الإلغاء CancellationException."
    ),
    "follow_ups_ar": (
        "- **المحاور:** \"لماذا نفضل withContext على async { ... }.await() لتغيير الـ Dispatcher؟\"\n"
        "  **المرشح:** \"لأن async تنشئ كوروتين جديداً وكائناً كاملاً من نوع DeferredCoroutine في الـ Heap وتتطلب جدولة إضافية في شجرة المهام، بينما withContext دالة معلقة مصممة خصيصاً للتبديل التسلسلي وتعتبر أخف وزناً بكثير وأقل استهلاكاً للموارد وأكثر وضوحاً في التعبير عن النية المعمارية.\"\n\n"
        "- **المحاور:** \"ماذا يحدث لو تم إلغاء الكوروتين الأب أثناء تنفيذ كود داخل withContext؟\"\n"
        "  **المرشح:** \"تستقبل دالة withContext إشارة الإلغاء فوراً، وعند وصول الكود لنقطة تعليق تالية أو انتهاء التنفيذ، يُلقى استثناء CancellationException ويتم التراجع عن إرجاع القيمة وإلغاء الكوروتين المستدعي، محافظاً على التزامن المهيكل.\"\n\n"
        "- **المحاور:** \"ماذا يحدث لو قمت بكتابة withContext(Dispatchers.Main) وأنا أعمل بالفعل على Dispatchers.Main؟\"\n"
        "  **المرشح:** \"يكتشف كوتلن عبر فحص سريع أن سياق التنفيذ المستهدف يطابق السياق الحالي، فيسلك مسار التنفيذ الفوري (Undispatched execution)، وينفذ الكود مباشرة داخل نفس إطار الدالة دون أي تعليق أو جدولة في طابور الـ Looper.\""
    ),
    "self_check_ar": (
        "تأكد من شمول إجابتك: تعريف withContext بدقة؛ شرح مبدأ Main-Safety؛ المقارنة مع async/await؛ والتحذير من كسر الشجرة بتمرير Job جديد."
    ),
    "references_ar": (
        "- [Kotlin withContext documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/with-context.html) — التوثيق المرجعي لدالة withContext.\n"
        "- [Android Main-safety pattern](https://developer.android.com/kotlin/coroutines#use-coroutines-for-main-safety) — تطبيق مبدأ Main-Safety في معمارية أندرويد.\n\n"
        "تمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13."
    ),
    "quick_answer_ar": (
        "دالة withContext هي دالة معلقة تُستخدم للتبديل المؤقت لسياق الكوروتين أو الـ Dispatcher الخاص به وتنفيذ الكود تسلسلياً وإرجاع النتيجة مباشرة دون إطلاق كوروتين جديد. نستخدمها لتطبيق مبدأ Main-Safety في طبقات البيانات لضمان نقل العمليات الحظرية إلى Dispatchers.IO وإبقاء ثريد الواجهة آمناً وسلساً."
    ),
    "best_answer_ar": (
        "دالة withContext هي الأداة الأساسية اللي بنبني بيها معمارية Main-Safe في تطبيقات أندرويد.\n\n"
        "الفكرة ببساطة إنها دالة معلقة (Suspending Function) بتسمح لك بتغيير الـ Dispatcher الحالي مؤقتاً؛ بتعلق الكود الحالي، وتنقل الشغل للـ Dispatcher الجديد (زي Dispatchers.IO)، وأول ما تخلص بترجع النتيجة مباشرة لنفس الثريد اللي ناداها بدون ما تحتاج تعمل await وبدون ما تطلق كوروتين جديد بـ launch أو async.\n\n"
        "الاستخدام المعماري الأهم ليها هو تحقيق مبدأ Main-Safety: إن كل دالة suspend في طبقة الـ Repository أو الـ UseCase تكون آمنة تماماً للاستدعاء من خيط الواجهة.\n\n"
        "يعني بدلاً من إن الـ ViewModel هو اللي يقعد يحدد Dispatchers.IO، بنخلي الـ Repository نفسه يغلف قراءة الداتابيز بـ withContext(ioDispatcher)، ويرجع البيانات جاهزة للـ ViewModel اللي بيناديها من Main بأمان وسطر واحد.\n\n"
        "ولا بد من الحذر التام من تمرير Job() جديد جواها، لأن ده بيكسر شجرة التزامن المهيكل وبيمنع وصول إشارات الإلغاء."
    ),
    "deep_answer_ar": (
        "تحت الغطاء، تعتمد دالة withContext على كلاسات داخلية متخصصة مثل DispatchedCoroutine و UndispatchedCoroutine. عندما يُستدعى withContext(newContext)، يقوم الرن تايم بعملية دمج بين السياق الحالي والـ newContext؛ فإذا تبيّن أن الـ CoroutineDispatcher الممرر يطابق الموزع الحالي تماماً، يسلك الكود مسار الـ Fast Path عبر UndispatchedCoroutine، حيث يُنفذ الكود الممرر داخل نفس إطار المكدس (Stack Frame) بصورة متزامنة دون أي تعليق أو إعادة جدولة في طابور الـ Dispatcher.\n\n"
        "أما إذا كان الموزع المستهدف مختلفاً (مثل الانتقال من Main إلى IO)، تنشئ المكتبة كائناً من نوع DispatchedCoroutine، وتعلق الـ Continuation الخاص بالمستدعي، وتجدول تنفيذ البلوك على الـ Thread Pool الخاص بـ IO. يظل المستدعي معلقاً في حالة انتظار حتى ينتهي الكود داخل البلوك بالكامل؛ وحينها يستدعي DispatchedCoroutine دالة resumeWith(result)، ليعيد جدولة استئناف المستدعي على موزعه الأصلي (Main) حاملاً القيمة الناتجة أو الاستثناء في حال حدوث فشل.\n\n"
        "الأثر المعماري الحاسم لـ withContext هو الحفاظ التام على الـ Cancellation Propagation؛ فالكود داخل withContext يظل جزءاً لا يتجزأ من نفس الـ Job الأصلي للكوروتين. إذا أُلغي الـ ViewModel أثناء انتظار عملية قاعدة البيانات في IO، ترصد دالة withContext إشارة الإلغاء وترمي CancellationException لتفريغ مكدس الاستدعاءات وتنظيف الموارد فوراً.\n\n"
        "لكن الخطأ القاتل الذي يقع فيه بعض المطورين هو كتابة withContext(Dispatchers.IO + Job())؛ فهذا التركيب يحل كائن الـ Job الجديد محل الـ Job الأب، مما يعزل البلوك المنفذ تماماً عن شجرة التزامن المهيكل، ويتركه يعمل إلى ما لا نهاية في الخلفية حتى بعد خروج المستخدم من الشاشة."
    ),
}

COR_10_META = {
    "id": "COR-10",
    "questionAr": "ما هو الإلغاء التعاوني (Cooperative Cancellation)؟ وما هي نقاط الإلغاء (Cancellation Points)؟",
    "topicAr": "الـ Coroutines والتزامن في Kotlin",
    "evaluates_ar": (
        "- فهم طبيعة الإلغاء في كوتلن كإلغاء تعاوني طوعي وليس مقاطعة جبرية لنواة النظام.\n"
        "- معرفة نقاط الإلغاء المدمجة (Cancellation Points) في الدوال المعلقة المعيارية.\n"
        "- كيفية كتابة كود حسابي متعاون عبر ensureActive و isActive و yield.\n"
        "- إدراك خطورة ابتلاع CancellationException داخل كتل الـ try-catch العامة."
    ),
    "why_it_matters_ar": (
        "في كوتلن، لا يمكن إيقاف الكوروتين قسرياً من الخارج كما هو الحال في قتل الـ Threads القديمة؛ بل يتم الإلغاء عبر نموذج تعاوني (Cooperative Cancellation). عندما يُلغى الكوروتين الأب، يتغير رمز حالته إلى Cancelling، ويجب على الكود الجاري تنفيذه أن يفحص هذه الحالة ويتعاون لإنهاء نفسه. نقاط الإلغاء هي المحطات التي يُفحص فيها الإلغاء ويُرمى عندها استثناء CancellationException. إذا كان الكود يحتوي على حلقة تكرار حسابية مكثفة لا تستدعي دوال معلقة ولا تفحص الإلغاء، فإنه سيستمر في العمل واستنزاف البطارية والمعالج ولن يتوقف أبداً رغم إلغاء الشاشة. فهم هذا المبدأ ضروري لمنع تسريب العمليات والتحكم الصارم في موارد الجهاز."
    ),
    "worked_example_ar": (
        "مقارنة بين كود غير متعاون مع الإلغاء وكود متعاون باحترافية:\n"
        "```kotlin\n"
        "// ❌ كود غير متعاون: حلقة تكرار لا تتوقف عند الإلغاء وتستمر في استهلاك المعالج\n"
        "suspend fun processLargeFile(data: ByteArray): ByteArray = withContext(Dispatchers.Default) {\n"
        "    val result = ByteArray(data.size)\n"
        "    for (i in data.indices) {\n"
        "        result[i] = heavyMath(data[i]) // لا توجد نقطة تعليق!\n"
        "    }\n"
        "    result\n"
        "}\n\n"
        "// ✅ كود متعاون يفحص الإلغاء بانتظام\n"
        "suspend fun processLargeFileSafe(data: ByteArray): ByteArray = withContext(Dispatchers.Default) {\n"
        "    val result = ByteArray(data.size)\n"
        "    for (i in data.indices) {\n"
        "        // فحص الإلغاء كل 1000 عنصر لرمي CancellationException فوراً عند الإلغاء\n"
        "        if (i % 1000 == 0) ensureActive()\n"
        "        result[i] = heavyMath(data[i])\n"
        "    }\n"
        "    result\n"
        "}\n"
        "```\n"
        "باستخدام ensureActive()، يتوقف الكود فوراً وبنعومة عند مغادرة المستخدم للشاشة دون إهدار طاقة الهاتف."
    ),
    "trade_offs_ar": (
        "يوفر الإلغاء التعاوني أماناً كبيراً لسلامة البيانات؛ فهو يمنع قطع الكود في منتصف تعديل حالة غير مكتملة ويمنح فرصة لتنظيف الملفات وإغلاق الاتصالات في كتل finally. ولكن في المقابل، يتطلب من المطور وعياً دائماً بإضافة نقاط تحقق صريحة في العمليات الحسابية الطويلة، مع الحذر من فحص الإلغاء في كل لفة مفردة إذا كانت العمليات بالغة الصغر لتجنب التأثير على سرعة المعالجة."
    ),
    "failure_modes_ar": (
        "الخطأ الشائع والمدمر هو كتابة try { ... } catch (e: Exception) { log(e) } حول كود معلق؛ لأن كتلة catch تلتقط كائن CancellationException وتبتلعه، مما يمنع الكوروتين من التوقف ويجعله يكمل عمله كأن شيئاً لم يكن! الحل الحتمي هو إما التقاط استثناءات محددة (مثل IOException) أو إعادة رمي استثناء الإلغاء فوراً: if (e is CancellationException) throw e."
    ),
    "production_perspective_ar": (
        "في الكود الإنتاجي، نلزم المطورين بمراجعة جميع كتل try-catch للتحقق من عدم ابتلاع CancellationException. وفي كتل finally، إذا تطلب الأمر استدعاء دالة معلقة لتنظيف الموارد أو إرسال إشعار إلغاء للخادم، نغلف الاستدعاء بـ withContext(NonCancellable) لضمان عدم إحباط كود التنظيف فورياً نتيجة إلغاء الكوروتين الأصلي."
    ),
    "how_to_answer_ar": (
        "- **السبب المعماري:** عرّف الإلغاء التعاوني كنموذج لا يقطع الكود قسرياً، بل يطلب من الكوروتين التوقف طواعية.\n"
        "- **طريقة الشرح:** اشرح نقاط الإلغاء كأماكن تفحص حالة الـ Job وترمي CancellationException لفك مكدس الدوال.\n"
        "- **المفاضلات:** وضح أهمية الإلغاء التعاوني لحماية البيانات في كتل finally مقابل الحاجة للفحص اليدوي في الـ Loops.\n"
        "- **أنماط الفشل:** اشرح كارثة ابتلاع CancellationException في كتل catch(e: Exception).\n"
        "- **الحل الإنتاجي:** اذكر أدوات الفحص: ensureActive و isActive و yield، واستخدام NonCancellable في كود التنظيف."
    ),
    "talking_points_ar": (
        "اشرح كيف يعمل CancellableContinuationImpl عند استلام إشارة الإلغاء أثناء التعليق. قارن بين yield() التي تعطي فرصة للثريد لخدمة مهام أخرى وبين ensureActive() التي تكتفي بالتحقق من الحالة. وضح لماذا صُمم NonCancellable كـ Job أحادي مخصص لكتل التنظيف."
    ),
    "follow_ups_ar": (
        "- **المحاور:** \"ما الفرق بين استخدام isActive وبين استدعاء ensureActive()؟\"\n"
        "  **المرشح:** \"خاصية isActive تعيد قيمة Boolean تعبر عن حالة الكوروتين (true إذا كان نشطاً)، وتتيح للمطور كتابة كود مخصص للخروج السلس من الحلقة مثل break. أما ensureActive() فتقوم بفحص الحالة، وإذا كان الكوروتين ملغى، تقوم فوراً برمي CancellationException لإنهاء التنفيذ وفك المكدس في خطوة واحدة.\"\n\n"
        "- **المحاور:** \"كيف تنفذ عملية تعليق (Suspend) داخل كتلة finally لكوروتين تم إلغاؤه بالفعل؟\"\n"
        "  **المرشح:** \"بما أن الكوروتين ملغى، فإن استدعاء أي دالة معلقة عادية داخل finally سيرمي CancellationException فوراً ويفشل العملية. لتجاوز ذلك، نغلف الاستدعاء بـ withContext(NonCancellable) { api.cleanup() }؛ حيث يوفر سياقاً خاصاً محصناً ضد الإلغاء مخصصاً حصرياً لعمليات التنظيف النهائية.\"\n\n"
        "- **المحاور:** \"لماذا لا يعتبر Thread.interrupt() بديلاً مناسباً للإلغاء في الكوروتينز؟\"\n"
        "  **المرشح:** \"لأن الكوروتينز تتشارك خيوط المعالجة في مجمعات مشتركة، ومقاطعة الثريد قسرياً قد تقاطع كوروتين آخر غير معني بالإلغاء، أو قد تترك الثريد في حالة غير صالحة للعمل. الإلغاء التعاوني يضمن إنهاء الكوروتين المستهدف فقط مع الحفاظ على سلامة خيط المعالجة لخدمة باقي مهام النظام.\""
    ),
    "self_check_ar": (
        "تحقق من إجابتك: شرح مفهوم الإلغاء التعاوني؛ تعريف نقاط الإلغاء ودور CancellationException؛ ذكر أدوات الفحص ensureActive و isActive؛ والتحذير من ابتلاع الاستثناء في كتل try-catch."
    ),
    "references_ar": (
        "- [Kotlin coroutines cancellation and timeouts](https://kotlinlang.org/docs/cancellation-and-timeouts.html) — التوثيق الرسمي للإلغاء والمهلات الزمنية في كوتلن.\n"
        "- [Cancellation in coroutines deep dive](https://medium.com/androiddevelopers/cancellation-in-coroutines-aa6b88e118c9) — مقال فريق أندرويد الرسمي حول تفاصيل الإلغاء التعاوني.\n\n"
        "تمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13."
    ),
    "quick_answer_ar": (
        "الإلغاء في كوتلن هو إلغاء تعاوني وليس قسرياً؛ فالنظام لا يجبر الكوروتين على التوقف بل يطلب منه ذلك، ويجب على الكوروتين فحص حالته لإنهاء نفسه. نقاط الإلغاء هي لحظات في التنفيذ يُفحص فيها الكوروتين ويُلقى عندها CancellationException لفك المكدس وتنظيف الموارد. وابتلاع هذا الاستثناء يمنع الإلغاء تماماً."
    ),
    "best_answer_ar": (
        "الإلغاء في الكوروتينز مبني على مبدأ التعاون الطوعي (Cooperative Cancellation)، وده معناه إن مفيش قوة خارجية تقدر تقطع تنفيذ الكوروتين قسرياً وهو شغال.\n\n"
        "لما بتلغي Job، حالته بتتحول لـ Cancelling، ولكنه بيفضل شغال لحد ما يوصل لما يسمى بـ 'نقطة إلغاء' (Cancellation Point). كل الدوال المعلقة الجاهزة في كوتلن زي delay و withContext و yield بتمثل نقاط إلغاء تلقائية؛ أول ما الكود يوصلها بيلاقي الكوروتين ملغي، فبترمي فوراً استثناء CancellationException عشان تفك المكدس وتنفذ كتل الـ finally وتنظف الموارد.\n\n"
        "لكن المشكلة بتظهر لو عندك حلقة تكرار حسابية طويلة (CPU Loop) مبتحتويش على أي دوال معلقة؛ في الحالة دي الكوروتين مش هيقف وهيفضل يستنزف المعالج حتى لو المستخدم خرج من الشاشة! والحل هنا إننا نحط جواه فحص يدوي باستخدام ensureActive() أو yield().\n\n"
        "والفخ القاتل اللي بيقع فيه المطورين هو عمل try-catch عامة تبتلع الـ CancellationException، وده بيبطل الإلغاء ويخلي العملية مستمرة في الخلفية إلى ما لا نهاية."
    ),
    "deep_answer_ar": (
        "داخلياً، يعتمد بروتوكول الإلغاء في kotlinx.coroutines على كائن CancellationException كآلية انتقال نظيفة لفك إطارات المكدس (Stack Unwinding). فعند استدعاء job.cancel()، ينتقل الـ Job من حالة Active إلى حالة Cancelling. إذا كان الكوروتين في تلك اللحظة معلقاً في دالة مثل delay() أو withContext()، يقوم كائن CancellableContinuationImpl بتسجيل إشارة الإلغاء واستئناف الكوروتين فوراً عبر رمي استثناء CancellationException.\n\n"
        "هذا الاستثناء صُمم خصيصاً بحيث لا يُعامل كعطل أو كراش؛ فالـ Job الأب يعتبره إغلاقاً طبيعياً للمهمة ولا ينشر الخطأ لإلغاء باقي الشجرة. ولكن المشكلة المعقدة تحدث عندما يكون الكوروتين قيد التشغيل الفعلي على المعالج (Running State) داخل حلقة تكرار متصلة دون تعليق. في هذا السيناريو، لا يستطيع الرن تايم مقاطعة الثريد؛ ولذا يجب على المطور تضمين نقاط فحص صريحة:\n\n"
        "أولاً: خاصية isActive وهي فحص بولياني سريع لحالة الـ Job.\nثانياً: دالة ensureActive() التي تفحص الحالة وترمي CancellationException فوراً إذا لم يكن الكوروتين نشطاً.\nثالثاً: دالة yield() التي تفحص الإلغاء وتسمح أيضاً لموزع الخيوط بإفساح المجال لكوروتينات أخرى على نفس المجمع (Cooperative Yielding).\n\n"
        "ومن أكبر الكوارث في كود الإنتاج هي كتل try { ... } catch (e: Exception) العامة؛ حيث تمسك بـ CancellationException وتمنع صعوده، مما يترك الكوروتين في حالة شاذة يستمر فيها بالعمل رغم تدمير نطاقه الحاضن. ولعلاج ذلك هندسياً، نلزم المطورين إما باستثناء CancellationException صراحة أو إعادة رميه فوراً.\n\n"
        "وعند الحاجة لتنفيذ مهام إغلاق غير متزامنة داخل كتل finally (مثل إغلاق قناة شبكة أو كتابة سجل وداع في الـ DataStore)، يجب تغليف العملية داخل withContext(NonCancellable)؛ لأن كتل finally لكوروتين ملغى تكون في حالة Cancelling، وأي نداء تعليق عادي بداخلها سيرمي CancellationException فورياً ويجهض عملية التنظيف."
    ),
}

BATCH_2 = [
    ("COR-06", COR_06_EN, COR_06_META),
    ("COR-07", COR_07_EN, COR_07_META),
    ("COR-08", COR_08_EN, COR_08_META),
    ("COR-09", COR_09_EN, COR_09_META),
    ("COR-10", COR_10_EN, COR_10_META),
]


def run_batch_2():
    print("Updating Canonical Markdown files for COR-06 to COR-10...")
    metadata_batch = {}
    for qid, en_data, meta_data in BATCH_2:
        ee.update_canonical_question(
            qid=qid,
            concept_en=en_data["concept_en"],
            walkthrough_en=en_data["walkthrough_en"],
            structured_en=en_data["structured_en"],
            deep_senior_en=en_data["deep_senior_en"],
            short_en=en_data["short_en"],
        )
        metadata_batch[qid] = meta_data
        print(f"Updated {qid}.md")

    return metadata_batch


if __name__ == "__main__":
    run_batch_2()
