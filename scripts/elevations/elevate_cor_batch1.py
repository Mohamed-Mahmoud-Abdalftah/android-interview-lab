#!/usr/bin/env python3
"""Batch 1: Elevate COR-01 through COR-05."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
import scripts.elevations.elevation_engine as ee

DATA_DIR = Path(__file__).resolve().parent / "data"

# ==============================================================================
# CANONICAL ENGLISH DEFINITIONS FOR COR-01 TO COR-05
# ==============================================================================

COR_01_EN = {
    "concept_en": (
        "A coroutine is a cooperative, user-space concurrency primitive that represents a suspendable computation capable of pausing and resuming without blocking the underlying operating system thread. In traditional computing models, an operating system thread is a heavy kernel-level abstraction created and scheduled by the OS kernel, requiring a dedicated call stack typically allocated between 512 kilobytes and one megabyte of memory. Preemptive multithreading between kernel threads incurs significant CPU overhead due to context switches between user and kernel modes, CPU register swapping, and CPU cache invalidation. Coroutines eliminate this heavy overhead by executing as lightweight cooperative state machines managed entirely in user space by the Kotlin coroutines runtime. When a coroutine suspends during an asynchronous operation such as network I/O or a timer, it relinquishes its executing thread back to the designated dispatcher thread pool, allowing that thread to execute other workloads or render UI frames seamlessly. Consequently, applications can comfortably maintain hundreds of thousands of concurrent coroutines simultaneously on limited mobile hardware where attempting to spawn equivalent OS threads would immediately crash the process with an out of memory error."
    ),
    "walkthrough_en": (
        "Consider an e-commerce catalog screen where the application needs to retrieve prices for one thousand items concurrently in the background.\n\n"
        "If an engineer implements this using OS threads:\n"
        "```kotlin\n"
        "repeat(1000) {\n"
        "    Thread {\n"
        "        fetchPrice(it)\n"
        "    }.start()\n"
        "}\n"
        "```\n"
        "This approach attempts to allocate one thousand kernel threads. Each thread reserves a dedicated stack, consuming approximately one gigabyte of RAM, quickly triggering an OutOfMemoryError unable to create new native thread crash and freezing the entire operating system.\n\n"
        "In contrast, implementing this with coroutines:\n"
        "```kotlin\n"
        "repeat(1000) {\n"
        "    viewModelScope.launch(Dispatchers.IO) {\n"
        "        fetchPrice(it)\n"
        "    }\n"
        "}\n"
        "```\n"
        "All one thousand coroutines execute concurrently while sharing a bounded thread pool managed by Dispatchers.IO. As each network request suspends waiting for server responses, the underlying worker threads are instantly released to service other tasks, operating within minimal heap allocations without any OS thread exhaustion."
    ),
    "short_en": (
        "A coroutine is a lightweight cooperative concurrency primitive managed entirely in user space by the Kotlin runtime, whereas an operating system thread is an expensive kernel-managed resource backed by a dedicated call stack. Coroutines can suspend execution without blocking their underlying OS thread, releasing worker threads back to the dispatcher pool and enabling massive concurrency without exhausting system memory."
    ),
    "structured_en": (
        "To begin with, the fundamental distinction between a thread and a coroutine lies in kernel management versus user-space abstraction. An operating system thread is a heavy, kernel-level construct that requires a dedicated memory stack of up to one megabyte, making context switching costly due to kernel-mode transitions and cache invalidations.\n\n"
        "From an architectural standpoint, a coroutine is a lightweight user-space execution unit represented by an allocated continuation instance on the heap. When a coroutine reaches a suspension point, it yields its executing thread back to the coroutine dispatcher instead of blocking it, allowing the underlying thread to process other operations such as UI rendering or concurrent computations.\n\n"
        "In production scenarios, spawning thousands of operating system threads will rapidly crash an Android process with an out of memory error. Conversely, thousands of coroutines can multiplex cooperatively across a fixed thread pool without degrading system performance.\n\n"
        "As for boundary management, coroutines integrate natively with structured concurrency, ensuring that asynchronous operations are automatically cancelled when their hosting lifecycle owner is destroyed, preventing background resource leaks that often plague unmanaged background threads."
    ),
    "deep_senior_en": (
        "Under the hood, the Kotlin compiler transforms every suspending function into a discrete state machine using continuation-passing style. Every suspend function receives an implicit continuation parameter that encapsulates the execution frame, local variables, and current label. When an asynchronous operation suspends, the function stores its local state in the continuation heap object and immediately returns the CoroutineSuspended singleton marker. This non-blocking return allows the executing thread to exit the call frame and return to its event loop or thread pool executor, entirely bypassing expensive operating system kernel context switches.\n\n"
        "In contrast to preemptive kernel thread scheduling where the operating system timer forcibly interrupts threads at arbitrary execution cycles, coroutine concurrency is strictly cooperative. A coroutine retains execution ownership until it explicitly reaches a suspension point, yields control, or finishes its work. On Android, this architectural divergence is paramount for main thread responsiveness. When executing on Dispatchers.Main, a blocking thread invocation halts the main Looper message queue and triggers an Application Not Responding dialog. Suspending on Dispatchers.Main, however, posts a message to resume the continuation onto the Choreographer loop only when data becomes available, ensuring uninterrupted sixty and one hundred twenty hertz frame rendering.\n\n"
        "From an allocation perspective, coroutine objects typically occupy only a few hundred bytes on the JVM heap. Dispatchers.Default and Dispatchers.IO manage underlying worker pools using a shared work-stealing scheduler, dynamically mapping millions of coroutines onto a bounded set of kernel threads. Furthermore, structured concurrency arranges coroutines in a strict parent-child Job hierarchy, guaranteeing deterministic cancellation propagation and preventing orphan background tasks when UI screens tear down."
    ),
}

COR_02_EN = {
    "concept_en": (
        "The suspend keyword in Kotlin is a compiler directive that marks a function as capable of non-blocking suspension and resumption within a coroutine context, but it does not imply background execution or automatic thread offloading. A common misconception among junior developers is assuming that marking a method with suspend automatically shifts its execution onto a background worker thread. In reality, a suspend function executes synchronously on whichever thread and dispatcher the caller launched it on, unless the function explicitly transitions its execution context using withContext. At the bytecode compilation level, the Kotlin compiler transforms suspending functions using Continuation-Passing Style, adding a synthetic Continuation parameter and generating a state machine that handles asynchronous pausing. If a developer invokes a suspend function containing heavy CPU calculations or synchronous file I/O directly on Dispatchers.Main without an explicit context switch, the function will execute directly on the Android UI thread, blocking the main Looper message queue and causing severe UI frame drops or application not responding errors. Professional Android architecture therefore enforces the Main-Safety principle: every public suspend function exposed by domain or data layers must be completely safe to invoke from Dispatchers.Main, meaning it must internally manage its own dispatcher switches."
    ),
    "walkthrough_en": (
        "Consider a cryptography repository function that decrypts an encrypted payload from disk storage.\n\n"
        "If written incorrectly without internal dispatcher offloading:\n"
        "```kotlin\n"
        "suspend fun decryptPayload(file: File): ByteArray {\n"
        "    // Dangerous: Executes directly on the caller thread!\n"
        "    val bytes = file.readBytes() // Blocking disk I/O\n"
        "    return cipher.doFinal(bytes) // Heavy CPU computation\n"
        "}\n"
        "```\n"
        "If a ViewModel invokes this function from viewModelScope.launch without specifying a background dispatcher, the blocking disk read and cryptographic calculation will run directly on the Android Main thread, freezing the user interface.\n\n"
        "The correct implementation enforces Main-Safety internally:\n"
        "```kotlin\n"
        "suspend fun decryptPayload(file: File): ByteArray = withContext(Dispatchers.Default) {\n"
        "    val bytes = withContext(Dispatchers.IO) { file.readBytes() }\n"
        "    cipher.doFinal(bytes)\n"
        "}\n"
        "```\n"
        "The function now guarantees main-safety; callers on Dispatchers.Main can safely execute it without risking dropped frames or thread starvation."
    ),
    "short_en": (
        "The suspend modifier does not imply background execution. It signifies that a function can pause non-blockingly and resume later, executing on the caller's current dispatcher by default. To prevent freezing the main thread, CPU or I/O operations inside a suspend function must explicitly shift execution to background dispatchers using withContext."
    ),
    "structured_en": (
        "To begin with, the suspend modifier is strictly a compiler marker indicating that a function can suspend without blocking its current thread, and it requires a coroutine environment to execute. It does not automatically dispatch work to a background thread.\n\n"
        "From an architectural standpoint, a suspend function executes by default on the dispatcher inherited from the caller's CoroutineScope. If invoked from viewModelScope without a dispatcher argument, it runs directly on Dispatchers.Main. Running synchronous blocking calls or long computational loops inside an unshifted suspend function will freeze the Android UI thread.\n\n"
        "In production scenarios, we mandate the Main-Safety architectural pattern. Every repository and use case suspend function must be safe to call from the main thread, internally delegating heavy workloads to Dispatchers.IO or Dispatchers.Default via withContext.\n\n"
        "As for boundary management, placing dispatcher responsibility inside the data layer shields presentation layers from threading details, ensuring seamless UI state updates while guaranteeing optimal resource allocation."
    ),
    "deep_senior_en": (
        "At the compiler level, the Kotlin compiler transforms a suspend function through Continuation-Passing Style. A function signature such as suspend fun fetch(): User is rewritten in bytecode into fun fetch(continuation: Continuation<User>): Any?. The return type becomes Any? because the function either returns the concrete result immediately if data is readily available, or returns the special COROUTINE_SUSPENDED sentinel value if an asynchronous wait is required.\n\n"
        "The compiler synthesizes a nested subclass of ContinuationImpl representing a discrete state machine. Local variables and the program counter are preserved across suspension points via an internal label integer. When an asynchronous operation like an HTTP call completes, its underlying callback invokes continuation.resumeWith(result), which posts a task to the designated CoroutineDispatcher event loop to re-enter the state machine at the preserved label.\n\n"
        "Crucially, the suspend modifier introduces no thread hops on its own. Thread transitions occur exclusively when a CoroutineDispatcher intercepts the continuation and schedules its execution onto a target thread pool. If a developer performs a blocking socket call or a tight CPU loop inside a suspend function without wrapping it in withContext(Dispatchers.IO) or withContext(Dispatchers.Default), the executing thread remains fully blocked throughout the operation.\n\n"
        "In production Android systems, failing to understand this distinction is a leading cause of UI stutter and ANR crashes. Main-safety is an invariant contract: repository and data source methods must encapsulate the appropriate dispatcher switches, allowing ViewModels and UI layers to consume suspending APIs without ever worrying about thread confinement."
    ),
}

COR_03_EN = {
    "concept_en": (
        "In Kotlin coroutines, CoroutineScope, CoroutineContext, Job, and Deferred are the fundamental structural abstractions that govern lifecycle, context propagation, and asynchronous results. A CoroutineScope is an interface that encapsulates a single CoroutineContext reference; it defines the structural boundary and lifetime within which child coroutines are spawned. The CoroutineContext is an indexed, type-safe heterogeneous collection of Element objects, such as a Job, CoroutineDispatcher, CoroutineExceptionHandler, and CoroutineName. The Job element controls the coroutine lifecycle through well-defined states including New, Active, Completing, Completed, Cancelling, and Cancelled, while organizing coroutines into parent-child hierarchies where parent cancellation recursively cascades to all children. A Deferred is a specialized subtype of Job created by the async builder; it represents an active computation that produces a future value accessed via the suspending await method. Together, these abstractions enforce structured concurrency: when an enclosing CoroutineScope is cancelled, its internal Job terminates all descendant Jobs and Deferred operations deterministically, preventing background leaks and orphaned network requests."
    ),
    "walkthrough_en": (
        "Consider a user profile screen where an application must fetch user profile details and user permissions concurrently before displaying the screen.\n\n"
        "If an engineer breaks structured concurrency by instantiating an ad-hoc unmanaged CoroutineScope:\n"
        "```kotlin\n"
        "fun loadProfile() {\n"
        "    // Anti-pattern: Creating an unlinked scope loses lifecycle binding\n"
        "    CoroutineScope(Dispatchers.IO).launch {\n"
        "        val user = api.fetchUser()\n"
        "        val perms = api.fetchPermissions()\n"
        "        updateUi(user, perms) // Leaks work if the screen is closed!\n"
        "    }\n"
        "}\n"
        "```\n"
        "If the user navigates away immediately, this detached scope continues executing, wasting battery and attempting to update destroyed UI views.\n\n"
        "The correct architecture leverages structured scope boundaries:\n"
        "```kotlin\n"
        "fun loadProfile() {\n"
        "    viewModelScope.launch {\n"
        "        val userDeferred: Deferred<User> = async(Dispatchers.IO) { api.fetchUser() }\n"
        "        val permsDeferred: Deferred<Permissions> = async(Dispatchers.IO) { api.fetchPermissions() }\n"
        "        val user = userDeferred.await()\n"
        "        val perms = permsDeferred.await()\n"
        "        _uiState.value = ProfileUiState.Success(user, perms)\n"
        "    }\n"
        "}\n"
        "```\n"
        "Here, viewModelScope provides the enclosing CoroutineScope. The launch builder creates a child Job linked to the ViewModel lifecycle, while async creates two child Deferred instances. If the ViewModel clears, the parent Job cancels both child Deferred computations immediately."
    ),
    "short_en": (
        "CoroutineScope defines the lifetime boundary holding a CoroutineContext. CoroutineContext is an indexed set of elements including Dispatcher, Job, and ExceptionHandler. Job manages lifecycle states and cancellation trees. Deferred is a Job subclass created by async that produces a future value accessible via await."
    ),
    "structured_en": (
        "To begin with, CoroutineScope serves as the lifecycle anchor for launching coroutines, exposing a CoroutineContext that defines the operating environment for all spawned children.\n\n"
        "From an architectural standpoint, CoroutineContext is an immutable, type-safe map of elements accessed by unique Key types. It holds critical components such as the CoroutineDispatcher, CoroutineExceptionHandler, CoroutineName, and the active Job.\n\n"
        "In production scenarios, the Job element represents the coroutine lifecycle state machine, managing transitions between Active, Cancelling, and Completed. When a parent Job is cancelled, it recursively cancels its entire child Job tree. Deferred extends Job by encapsulating an eventual result, exposing the suspending await method to retrieve the computed value.\n\n"
        "As for boundary management, adhering to structured concurrency means never instantiating arbitrary unmanaged scopes like CoroutineScope(Dispatchers.IO). Instead, work must belong to established owners like viewModelScope to ensure automatic cleanup upon screen departure."
    ),
    "deep_senior_en": (
        "Under the hood, CoroutineContext operates as a persistent data structure resembling a type-indexed map, implemented via CombinedContext, Element, and EmptyCoroutineContext. When coroutines are launched, context inheritance follows a precise merging algorithm: ChildContext equals ParentContext plus BuilderArguments. By default, the builder generates a brand-new child Job instance that registers itself with the parent Job in the context, forming a bidirectional tree node.\n\n"
        "The Job state machine governs execution integrity through distinct states: New, Active, Completing, Completed, Cancelling, and Cancelled. A parent Job cannot transition from Completing to Completed until every single one of its registered child Jobs has terminated. If a child Job fails with an uncaught exception, it propagates the failure upward to its parent Job, which in turn cancels all other sibling Jobs before failing itself. The only exception to this bidirectional failure propagation is when the parent context contains a SupervisorJob.\n\n"
        "Deferred is a parameterized specialization of Job that represents a non-blocking asynchronous value computation. Underneath, Deferred holds an internal state of type Incomplete or CompletedWithResult. When await is invoked on an incomplete Deferred, it suspends the calling coroutine and registers its continuation with the Deferred completion listener. If the Deferred completes with an exception, await unpacks and re-throws that exact exception to the caller.\n\n"
        "In enterprise Android codebases, mismanaging these primitives leads to memory leaks and broken cancellation. Injecting CoroutineDispatcher instances while allowing the host CoroutineScope to provide the parent Job ensures that tests can control execution timing with TestScope while preserving production lifecycle safety."
    ),
}

COR_04_EN = {
    "concept_en": (
        "Structured concurrency is an architectural paradigm and runtime contract ensuring that concurrent tasks have bounded, well-defined lifetimes tied directly to an enclosing scope and parent Job hierarchy. In unconstrained or unstructured concurrency models, such as raw thread instantiation, GlobalScope, or unlinked Future objects, background tasks are detached from their spawning context, frequently leading to orphaned computations, memory leaks, lost exceptions, and unpredictable resource exhaustion when the originating screen is closed. Kotlin achieves structured concurrency by mandating that every coroutine is launched within a CoroutineScope that provides a parent Job. This forms a strict parent-child tree where three inviolable rules govern execution: first, a parent coroutine cannot complete until all of its child coroutines have completed; second, cancelling a parent coroutine immediately and recursively cascades cancellation down to all of its children; and third, if any child coroutine encounters an unhandled exception, it propagates the failure up to the parent, cancelling all sibling coroutines and the parent itself. This paradigm guarantees deterministic cleanup, predictable failure modes, and leak-free asynchronous execution across complex mobile application lifecycles."
    ),
    "walkthrough_en": (
        "Consider a checkout screen that concurrently executes two independent operations: validating payment authorization and reserving inventory items.\n\n"
        "If implemented using unstructured concurrency:\n"
        "```kotlin\n"
        "fun executeCheckout() {\n"
        "    // Antipattern: GlobalScope detaches tasks from the caller\n"
        "    GlobalScope.launch {\n"
        "        val authJob = launch { authorizePayment() }\n"
        "        val inventoryJob = launch { reserveInventory() }\n"
        "    }\n"
        "}\n"
        "```\n"
        "If authorizePayment fails with a network exception, inventoryJob continues running in the background, reserving stock for an order that will never complete. If the user exits the checkout screen, both operations continue running as orphans.\n\n"
        "Structured concurrency resolves this via coroutineScope:\n"
        "```kotlin\n"
        "suspend fun executeCheckout(): CheckoutResult = coroutineScope {\n"
        "    val authDeferred = async { authorizePayment() }\n"
        "    val inventoryDeferred = async { reserveInventory() }\n"
        "    CheckoutResult(authDeferred.await(), inventoryDeferred.await())\n"
        "}\n"
        "```\n"
        "If authorizePayment throws an exception, coroutineScope immediately cancels inventoryDeferred, releases pending network resources, and re-throws the failure to the caller, ensuring atomic and clean failure recovery."
    ),
    "short_en": (
        "Structured concurrency guarantees that concurrent tasks have explicit parent-child relationships and bounded lifetimes. A parent scope cannot complete until all its children finish, cancelling a parent recursively cancels all children, and an uncaught child failure cancels siblings, preventing leaked background operations and orphaned tasks."
    ),
    "structured_en": (
        "To begin with, structured concurrency is the foundational principle that concurrent operations must be anchored to explicit lifecycle scopes rather than floating as detached background threads.\n\n"
        "From an architectural standpoint, every coroutine spawned within a scope becomes a child in a hierarchical Job tree. This relationship establishes strict structural guarantees: a parent coroutine suspends completion until all registered child jobs have completely finished their execution.\n\n"
        "In production scenarios, cancellation flows seamlessly down the hierarchy. When a user navigates away and the ViewModel clears its scope, the parent Job cancels all running child network requests and database operations instantly, preventing battery drain and memory leaks.\n\n"
        "As for boundary management, failure propagation maintains system consistency. If one child in an all-or-nothing operation fails, the parent scope cancels all remaining sibling tasks, ensuring that partial or corrupt state is never persisted."
    ),
    "deep_senior_en": (
        "Under the hood, structured concurrency is enforced through the internal node linkages of the Job hierarchy. When a coroutine builder like launch or async is invoked, it retrieves the parent Job from the enclosing CoroutineScope context and constructs a new ChildJob instance. The builder invokes parentJob.attachChild(childJob), which returns a ChildHandle that maintains bidirectional references between parent and child.\n\n"
        "This bidirectional link enforces the coroutine completion protocol. When a coroutine body finishes executing, its Job transitions into the Completing state rather than Completed. In Completing, the parent waits for all active children in its child list to reach their final termination states. Only after every child has completed does the parent transition to Completed.\n\n"
        "In terms of failure propagation, if a child fails with an unhandled exception other than CancellationException, it executes childCancelled(cause) on its parent handle. The parent immediately cancels itself with that cause, enters the Cancelling state, and iterates through its registered children to dispatch cancellation notifications to every active sibling. This automatic teardown prevents orphaned background workloads from consuming bandwidth or holding open file descriptors.\n\n"
        "The architectural benefit in Android development is immense. In legacy architectures using raw Threads or RxJava subscriptions, developers had to manually maintain CompositeDisposable collections and remember to clear them in onDestroy. Structured concurrency makes this lifecycle binding automatic and compiler-enforced, eliminating entire categories of concurrency bugs, leaked Activity contexts, and race conditions."
    ),
}

COR_05_EN = {
    "concept_en": (
        "The launch and async coroutine builders are the two primary mechanisms for creating new coroutines in Kotlin, differing fundamentally in their intent, return types, and exception propagation semantics. The launch builder is designed for fire-and-forget asynchronous tasks where the caller does not require a computed result value; it returns a Job instance that allows the caller to monitor lifecycle state, join completion, or cancel execution. Exceptions thrown inside a launch coroutine are considered uncaught failures and are immediately propagated up the Job hierarchy to the enclosing parent scope, triggering sibling cancellation and delegating to any configured CoroutineExceptionHandler or terminating the process. Conversely, the async builder is designed for concurrent computations that yield an eventual result; it returns a Deferred<T> instance, which is a lightweight future subclassing Job. The caller retrieves the computed result by calling the suspending await method. In terms of exception propagation, while an async root coroutine encapsulates exceptions within the Deferred until await is called, an async coroutine launched inside a standard coroutineScope will still propagate its failure up to the parent Job immediately upon crashing, cancelling the entire scope even before await is invoked."
    ),
    "walkthrough_en": (
        "Consider a dashboard screen that triggers an analytics event while concurrently loading two independent data widgets.\n\n"
        "Illustrating the distinct usage of launch versus async:\n"
        "```kotlin\n"
        "fun refreshDashboard() {\n"
        "    // 1. launch: Fire-and-forget side effect, returns Job\n"
        "    viewModelScope.launch {\n"
        "        analyticsTracker.logEvent(\"dashboard_refreshed\")\n"
        "    }\n\n"
        "    // 2. async: Concurrent value computations, returns Deferred<T>\n"
        "    viewModelScope.launch {\n"
        "        val balanceDeferred: Deferred<AccountBalance> = async(Dispatchers.IO) {\n"
        "            accountApi.fetchBalance()\n"
        "        }\n"
        "        val notificationsDeferred: Deferred<List<Notification>> = async(Dispatchers.IO) {\n"
        "            notificationApi.fetchNotifications()\n"
        "        }\n\n"
        "        // Await concurrent values in parallel\n"
        "        val balance = balanceDeferred.await()\n"
        "        val notifications = notificationsDeferred.await()\n"
        "        _uiState.value = DashboardUiState.Ready(balance, notifications)\n"
        "    }\n"
        "}\n"
        "```\n"
        "If fetchBalance throws an exception, the async child fails. Even if await has not yet been called on notificationsDeferred, the failure propagates up the parent Job, immediately cancelling notificationsDeferred and the parent coroutine, preventing wasted network operations."
    ),
    "short_en": (
        "launch is a fire-and-forget coroutine builder returning a Job for operations where no value is returned, propagating uncaught exceptions immediately up the Job hierarchy. async is for concurrent computations returning a Deferred<T>, allowing callers to retrieve the result via await. Within a standard scope, async exceptions still cancel the parent hierarchy immediately."
    ),
    "structured_en": (
        "To begin with, the core distinction between launch and async centers on whether the asynchronous operation produces a computational result or performs a fire-and-forget action.\n\n"
        "From an architectural standpoint, launch returns a Job that represents the running task, making it ideal for background operations such as logging analytics, caching database entries, or firing UI notifications where the caller only cares about completion status.\n\n"
        "In production scenarios, async returns a Deferred instance, which represents a promise of an eventual value retrieved through the suspending await method. We use async primarily when decomposing a complex screen into parallel network calls that need to be aggregated together.\n\n"
        "As for boundary management, exception handling differs significantly. Uncaught exceptions in launch immediately propagate up the parent Job hierarchy. With async, while exceptions are thrown when calling await, an unhandled failure in an async child inside a standard scope still cancels the parent Job and all siblings immediately, unless wrapped in a supervisorScope."
    ),
    "deep_senior_en": (
        "Under the hood, launch creates a StandaloneCoroutine instance, whereas async creates a DeferredCoroutine instance. Both inherit the CoroutineScope context and instantiate a child Job linked to the parent. However, their internal completion and exception reporting logic diverges markedly in the handleJobException method.\n\n"
        "In a StandaloneCoroutine created by launch, an unhandled exception thrown in the coroutine body causes the coroutine to cancel itself and call parentContext.handleCoroutineException(exception). The failure traverses directly up to the root Job. If no supervisor boundary exists, the root coroutine either delegates the exception to an installed CoroutineExceptionHandler or passes it to the thread default uncaught exception handler, crashing the Android runtime.\n\n"
        "In contrast, a DeferredCoroutine created by async stores the resulting outcome—whether a value or an exception—inside its internal state. When await is called, the state is evaluated: if the computation completed normally, the value is returned; if it completed exceptionally, await unpacks and re-throws the original exception. However, a critical pitfall in Kotlin coroutines is assuming that wrapping await in a try-catch block protects the scope from cancellation. Inside a regular coroutineScope, the Deferred child notifies its parent of failure immediately upon crashing. By the time await throws the exception in the caller, the parent Job is already in the Cancelling state, and all siblings have been cancelled.\n\n"
        "To achieve true resilience when using async for parallel operations where one failure should not cancel the others, senior engineers wrap the parallel operations in supervisorScope or invoke supervisorScope with individual try-catch blocks around each await call."
    ),
}

# ==============================================================================
# ARABIC METADATA DEFINITIONS FOR COR-01 TO COR-05
# ==============================================================================

COR_01_META = {
    "id": "COR-01",
    "questionAr": "ما هي الـ Coroutine، وما الفرق الجوهري بينها وبين الـ Thread في Kotlin وأندرويد؟",
    "topicAr": "الـ Coroutines والتزامن في Kotlin",
    "evaluates_ar": (
        "- التمييز الدقيق بين وحدة معالجة قابلة للتعليق (Coroutine) وخيط المعالجة التابع لنواة النظام (OS Kernel Thread).\n"
        "- فهم تكلفة التبديل بين السياقات (Context Switching) واستهلاك الذاكرة للـ Call Stack.\n"
        "- استيعاب آلة الحالة (Continuation State Machine) وآلية التعليق بدون حظر الثريد (Non-blocking Suspension).\n"
        "- اختيار النطاق المالك والـ Dispatcher المناسب في بيئة أندرويد لتفادي الـ ANRs وتجميد الشاشة."
    ),
    "why_it_matters_ar": (
        "في بيئة تشغيل JVM و Android ART، يمثل الـ Thread كياناً ثقيلاً تديره نواة نظام التشغيل ويحجز مساحة ذاكرة ثابتة للـ Stack تتراوح عادة بين 512 كيلوبايت و 1 ميجابايت. التبديل بين الـ Threads يتطلب تدخلاً من الـ OS Scheduler وتبديلاً بين وضع المستخدم (User Mode) ووضع النواة (Kernel Mode) مع تفريغ سجلات المعالج ومسح الكاش. في المقابل، الـ Coroutine هي تجريد برمجي خفيف في الـ User-space، تُعامل ككائن عادي على الـ Heap لا يتجاوز بضع مئات من البايتات. الميزة الجوهرية هي التعليق بدون حظر؛ فعند انتظار طلب شبكة أو عملية إدخال وإخراج، لا يتم إيقاف الـ Thread بل يتحرر فوراً لخدمة مهام أخرى، مما يسمح بتشغيل مئات الآلاف من العمليات المتزامنة بكفاءة متناهية على عتاد الموبايل المحدود."
    ),
    "worked_example_ar": (
        "في شاشات التجارة الإلكترونية، عند الحاجة لجلب أسعار مئات المنتجات بصورة متزامنة:\n"
        "```kotlin\n"
        "class ProductCatalogViewModel(\n"
        "    private val repository: ProductRepository,\n"
        "    private val ioDispatcher: CoroutineDispatcher = Dispatchers.IO\n"
        ") : ViewModel() {\n\n"
        "    fun loadPrices(productIds: List<String>) {\n"
        "        viewModelScope.launch {\n"
        "            productIds.forEach { id ->\n"
        "                launch(ioDispatcher) {\n"
        "                    val price = repository.fetchPrice(id)\n"
        "                    updateItemPrice(id, price)\n"
        "                }\n"
        "            }\n"
        "        }\n"
        "    }\n"
        "}\n"
        "```\n"
        "هذا الكود يوزع الطلبات على مجمع خيوط Dispatchers.IO المحدود بمرونة، ويعلق المهام أثناء انتظار استجابة الشبكة بدون حجز ثريدات نظام جديدة، بينما محاولة إنشاء ألف Thread حقيقي كانت ستؤدي فوراً إلى انهيار التطبيق بخطأ OutOfMemoryError."
    ),
    "trade_offs_ar": (
        "توفر الـ Coroutines نموذج تزامن تعبيري ونظيف يتفوق على تعقيدات سلاسل الـ Callbacks والـ Reactive Streams، كما تضمن إدارة دورة الحياة عبر التزامن المهيكل. ومع ذلك، فإن رخص إنشاء الكوروتين لا يعني أن المعالجة الحسابية (CPU-bound) أو البيانات المشتركة أصبحت مجانية؛ فالوصول إلى Mutable State مشترك بدون حماية لا يزال يسبب Race Conditions، والعمليات الحسابية الثقيلة لا تزال تتطلب التوزيع على Dispatchers.Default. إضافة إلى ذلك، الكوروتينز لا تلغي الحاجة إلى WorkManager للمهام التي يجب أن تستمر بعد موت عملية التطبيق (Process Death)."
    ),
    "failure_modes_ar": (
        "من أشهر الأخطاء الشائعة الاعتقاد بأن مجرد إطلاق كوروتين عبر launch ينقل التنفيذ تلقائياً إلى خيط خلفي؛ فإذا ورث الكوروتين سياق Dispatchers.Main ونفذ عمليات قراءة متزامنة أو استدعاء Thread.sleep أو تشفير ملفات، فإنه سيجمد ثريد الواجهة ويتسبب في ANR. الخطأ الكارثي الآخر هو استخدام GlobalScope لطلبات الشاشة، مما يؤدي إلى تسريب العمليات في الخلفية وتحديث واجهات تم تدميرها بالفعل بعد خروج المستخدم."
    ),
    "production_perspective_ar": (
        "في التطبيقات الإنتاجية الضخمة، نلزم جميع الدوال المعلقة (Suspend Functions) في طبقات الـ Repository والـ Data بأن تكون Main-Safe ذاتياً؛ أي أنها المسؤولة داخلياً عن التبديل إلى Dispatchers.IO عبر withContext عند تنفيذ قراءة قاعدة بيانات أو طلب شبكة. يتم إطلاق كافة العمليات المرتبطة بالواجهة داخل viewModelScope لضمان الإلغاء التلقائي عند مغادرة المستخدم للشاشة، مع حقن الـ Dispatchers كمعاملات (Dependency Injection) لتسهيل كتابة اختبارات الوحدة باستخدام StandardTestDispatcher."
    ),
    "how_to_answer_ar": (
        "- **السبب المعماري:** وضح الفارق الأساسي بين خيط نظام التشغيل المدار بالنواة (Kernel Thread) والكوروتين كآلة حالة في مساحة المستخدم (User-space State Machine).\n"
        "- **طريقة الشرح:** ركز على مفهوم التعليق بدون حظر (Suspending without blocking) وتحرير الثريد للـ Event Loop.\n"
        "- **المفاضلات:** اشرح لماذا الكوروتين خفيف في الذاكرة ولكن لا يحل تلقائياً مشاكل Shared Mutable State بدون آليات تزامن.\n"
        "- **أنماط الفشل:** نبه إلى خطأ تشغيل كود حظري (Blocking Code) على Dispatchers.Main والخلط بين launch ونقل الثريد.\n"
        "- **الحل الإنتاجي:** استشهد بتطبيق مبدأ Main-Safety وحقن الـ Dispatchers والإلغاء المنسق عبر viewModelScope."
    ),
    "talking_points_ar": (
        "ناقش تحويل المترجم لدوال الـ suspend إلى نمط Continuation-Passing Style مع توليد كائن آلة الحالة، وكيف يعيد الـ CoroutineDispatcher جدولة الـ Continuation عبر Looper أو ThreadPool. قارن بين الإلغاء التعاوني (Cooperative Cancellation) والمقاطعة الجبرية للـ Threads. وضح الفارق بين التزامن المتوازي الحقيقي (Parallelism) وتعدد المهام التعاوني (Concurrency)."
    ),
    "follow_ups_ar": (
        "- **المحاور:** \"هل يمكن للكوروتين أن يستأنف تنفيذه على ثريد مختلف عن الثريد الذي بدأ عليه؟\"\n"
        "  **المرشح:** \"نعم بالتأكيد. طالما أن الكوروتين يعمل على مجمع خيوط متعدد مثل Dispatchers.Default أو Dispatchers.IO، فإنه عند حدوث التعليق يتحرر الثريد الأصلي، وعند اكتمال العملية غير المتزامنة يقوم الموزع بجدولة استئناف الـ Continuation على أي ثريد متاح في المجمع، إلا إذا كان مقيداً بموزع أحادي مثل Dispatchers.Main.\"\n\n"
        "- **المحاور:** \"ماذا يحدث لو قمت باستدعاء Thread.sleep داخل كوروتين يعمل على Dispatchers.Main؟\"\n"
        "  **المرشح:** \"سيؤدي ذلك إلى حظر خيط الواجهة الرئيسي بالكامل وتجميد معالجة رسائل الـ Looper وتوقف رسم الإطارات، مما يسبب سقوط فريمات يتبعه ظهور نافذة خطأ التطبيق لا يستجيب ANR فور تجاوز مهلة الخمس ثوانٍ. البديل الصحيح هو استخدام دالة delay المعلقة.\"\n\n"
        "- **المحاور:** \"كيف تختلف متطلبات الذاكرة بين إنشاء ألف ثريد وألف كوروتين؟\"\n"
        "  **المرشح:** \"ألف ثريد في نظام التشغيل تتطلب حجز مساحة Stack خاصة لكل منها في الذاكرة الأصلية (Native Memory)، مما يستهلك ما يقارب 500 إلى 1000 ميجابايت من الرام ويتسبب سريعاً في انهيار التطبيق بـ OutOfMemoryError. في المقابل، ألف كوروتين تستهلك فقط بضعة ميجابايتات على الـ Heap ككائنات Continuation خفيفة للغاية.\""
    ),
    "self_check_ar": (
        "قيّم إجابتك وفق المعايير التالية: التمييز بوضوح بين الكوروتين وثريد النظام؛ شرح آلية التعليق بدون حظر؛ توضيح دور الموزعات (Dispatchers)؛ تشخيص مخاطر استدعاء الأكواد الحظرية على ثريد الواجهة؛ وتبرير اختيار النطاقات المحددة بدورة حياة المكون في أندرويد."
    ),
    "references_ar": (
        "- [Kotlin coroutines basics](https://kotlinlang.org/docs/coroutines-basics.html) — مفاهيم التعليق والموزعات وخيوط المعالجة في كوتلن.\n"
        "- [Android coroutines guidance](https://developer.android.com/kotlin/coroutines) — التوجيهات الرسمية لاستخدام الكوروتينز وإدارة دورة الحياة في أندرويد.\n\n"
        "تمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13."
    ),
    "quick_answer_ar": (
        "الـ Coroutine هي وحدة تزامن خفيفة وتعاونية تديرها مكتبة كوتلن بالكامل في مساحة المستخدم (User-space)، بينما الـ Thread هو مورد ثقيل يديره نظام التشغيل ويحجز Stack خاص في الذاكرة بحجم يصل إلى ميجابايت. الميزة الأساسية للكوروتين هي التعليق بدون حظر؛ فالعملية المعلقة تترك الثريد لخدمة مهام أخرى وتستأنف لاحقاً، مما يتيح تشغيل آلاف المهام المتزامنة بكفاءة وبدون استنزاف موارد النظام."
    ),
    "best_answer_ar": (
        "الفارق الجوهري بين الكوروتين والثريد يكمن في مستوى الإدارة واستهلاك الموارد في النظام.\n\n"
        "خيط المعالجة (OS Thread) هو مورد ثقيل تابع لنواة نظام التشغيل، يحجز مساحة ثابتة للـ Stack تصل لميجابايت، والتبديل بين الثريدات يتطلب Context Switch مكلف جداً على المعالج لنقل التنفيذ بين مساحة المستخدم والنواة. محاولة تشغيل آلاف الثريدات على جهاز أندرويد تؤدي سريعاً لانهيار التطبيق بنفاد الذاكرة.\n\n"
        "أما الكوروتين، فهي تجريد خفيف للغاية يدار في مساحة المستخدم؛ الكوروتين مجرد كائن Continuation يمثل آلة حالة (State Machine) على الـ Heap ولا يتجاوز حجمه بضع مئات من البايتات.\n\n"
        "الميزة السحرية هنا هي آلية التعليق؛ فعند تنفيذ عملية معلقة مثل طلب شبكة، لا يقوم الكوروتين بحظر الثريد، بل يحرره فوراً ليعود لمجمع الخيوط أو يرسم إطارات الواجهة، وعند عودة البيانات يُستأنف الكوروتين على أي ثريد متاح في الـ Dispatcher.\n\n"
        "في المعمارية النظيفة، بنعتمد على الكوروتينز لضمان بقاء ثريد الواجهة حراً وسلساً، مع ربط كل العمليات بدورات حياة الشاشات عبر التزامن المهيكل لمنع أي تسريب للموارد."
    ),
    "deep_answer_ar": (
        "على مستوى المترجم والـ Bytecode، يقوم مترجم كوتلن بإعادة كتابة كل دالة معلقة عبر تحويل Continuation-Passing Style إلى آلة حالة كاملة ترث من الفئة ContinuationImpl. الدالة المعلقة يضاف لها معامل ضمني يمثل الـ Continuation، وتتغير قيم الـ Label الداخلي مع كل نقطة تعليق (Suspension Point). عند وصول التنفيذ لعملية غير متزامنة، تخزن الدالة حالتها ومتغيراتها المحلية على الـ Heap وتعيد فوراً القيمة الرمزية COROUTINE_SUSPENDED، مما ينهي إطار استدعاء الدالة على الثريد الفعلي ويعيده فوراً للـ Event Loop أو الـ Thread Pool Executor بدون أي تدخل من نواة نظام التشغيل وبدون تفريغ لسجلات الـ CPU.\n\n"
        "هذا النموذج يختلف جوهرياً عن تعدد المهام الإجباري (Preemptive Multithreading) المتبع في نظام التشغيل؛ فالـ OS Scheduler يقطع الثريدات قسرياً عند انتهاء الشريحة الزمنية (Time Slice)، بينما الكوروتينز تعمل بنظام التعاون الطوعي (Cooperative Concurrency)، حيث يستمر الكوروتين في التنفيذ حتى يعلن صراحة عن التعليق أو يفرغ من مهمته.\n\n"
        "في بيئة أندرويد، هذا التمايز يحدد الفارق بين سلاسة التطبيق وظهور الـ ANR؛ فعند استدعاء عملية حظر على خيط الواجهة، يتعطل مجمع رسائل Looper الرئيسي وتتوقف نداءات Choreographer المسؤولة عن معالجة اللمس ورسم الواجهة بمعدل 120 إطاراً في الثانية. أما تعليق الكوروتين على Dispatchers.Main، فيعني جدولة رسالة استئناف الـ Continuation في طابور الـ MessageQueue عند جاهزية النتيجة، مما يضمن تدفقاً سلساً للإطارات.\n\n"
        "من منظور إدارة الموارد، يعتمد كوتلن على موزع افتراضي يشترك في جدولة خيوط المعالجة بنظام سرقة المهام (Work-stealing Scheduler) عبر CoroutineScheduler، مما يتيح توزيع آلاف الكوروتينز على عدد خيوط يطابق عدد أنوية المعالج في Dispatchers.Default، أو مجمع موسع في Dispatchers.IO، مع ضمان الربط الهرمي للـ Jobs لتحقيق إلغاء منسق ومحكم للمهام عند تدمير شاشات التطبيق."
    ),
}

COR_02_META = {
    "id": "COR-02",
    "questionAr": "ماذا تعني الكلمة المفتاحية suspend؟ وهل تعني بالضرورة التنفيذ في الخلفية؟",
    "topicAr": "الـ Coroutines والتزامن في Kotlin",
    "evaluates_ar": (
        "- فهم المعنى الحقيقي لكلمة suspend ودورها كإشارة للمترجم (Compiler Marker).\n"
        "- دحض الفكرة الخاطئة الشائعة بأن suspend تعني النقل التلقائي لخيط خلفي (Background Thread).\n"
        "- شرح تطبيق مبدأ الأمان لخيط الواجهة (Main-Safety) واستخدام withContext.\n"
        "- فهم تحويل الدالة عبر الـ Continuation-Passing Style والقيمة COROUTINE_SUSPENDED."
    ),
    "why_it_matters_ar": (
        "الكلمة المفتاحية suspend لا تعني على الإطلاق تشغيل الكود في الخلفية؛ بل هي إشارة تتيح للمترجم معرفة أن هذه الدالة تمتلك القدرة على تعليق تنفيذها مؤقتاً بدون حظر الثريد الحالي، وأنها لا تُستدعى إلا من داخل كوروتين أو دالة suspend أخرى. إذا كانت الدالة تحتوي على عمليات قراءة قرص حظرية أو معالجة حسابية ثقيلة وتم استدعاؤها من Dispatchers.Main بدون استخدام withContext، فإنها ستتنفذ مباشرة على ثريد الواجهة وتؤدي إلى تجميد الشاشة وظهور ANR. لذلك، يقع على عاتق كاتب الدالة في طبقة البيانات تأمينها لتكون Main-Safe بحيث يتمكن أي مستدعٍ في طبقة الواجهة من تشغيلها بأمان تام."
    ),
    "worked_example_ar": (
        "تطبيق مبدأ Main-Safety في دالة قراءة ومعالجة ملف:\n"
        "```kotlin\n"
        "class FileRepository(\n"
        "    private val ioDispatcher: CoroutineDispatcher = Dispatchers.IO,\n"
        "    private val defaultDispatcher: CoroutineDispatcher = Dispatchers.Default\n"
        ") {\n"
        "    // الدالة تضمن الأمان التام لمستدعيها على خيط الواجهة\n"
        "    suspend fun parseAndCache(file: File): ParsedData {\n"
        "        // 1. قراءة الملف عبر ثريد مخصص لعمليات القرص\n"
        "        val content = withContext(ioDispatcher) {\n"
        "            file.readText()\n"
        "        }\n"
        "        // 2. تحليل البيانات الحسابية عبر ثريد مخصص لمعالجة الـ CPU\n"
        "        return withContext(defaultDispatcher) {\n"
        "            parseJsonData(content)\n"
        "        }\n"
        "    }\n"
        "}\n"
        "```\n"
        "بهذا الأسلوب، يستطيع الـ ViewModel استدعاء الدالة مباشرة من viewModelScope دون الحاجة للقلق بشأن نوع الثريد أو تعطل الشاشة."
    ),
    "trade_offs_ar": (
        "كتابة دوال suspend تجعل الكود غير المتزامن يظهر بشكل تسلسلي ومقروء للغاية كأنه كود متزامن عادي، مع توفير آليات إلغاء تعاونية طبيعية. في المقابل، يجب الحذر من الإفراط في التبديل بين الـ Dispatchers داخل الحلقات التكرارية الدقيقة عبر withContext؛ لأن التبديل المتكرر يضيف تكلفة جدولة وإنشاء كائنات Continuation، والأفضل تجميع العمليات الحظرية ونقلها دفعة واحدة إلى الـ Dispatcher المناسب."
    ),
    "failure_modes_ar": (
        "الخطأ الكارثي هو تحويل دالة بطيئة fun calculate(): Result إلى suspend fun calculate(): Result والظن بأن ذلك حل مشكلة تجميد الشاشة! فإذا لم يُضف withContext بداخلها، فستظل الدالة تعمل على نفس خيط الـ Caller. خطأ آخر هو ابتلاع استثناء الإلغاء CancellationException داخل كتل try-catch عامة دون إعادة رميه، مما يمنع الكوروتين من التوقف عند تدمير شاشة التطبيق."
    ),
    "production_perspective_ar": (
        "في الفرق الهندسية المتقدمة، نعتبر كسر مبدأ Main-Safety خطأً يمنع الموافقة على الـ Pull Request. نلزم جميع الـ Repositories بتحديد الـ Dispatchers الخاصة بها عبر الـ Constructor Injection، مما يسهل استبدالها بـ TestDispatcher في اختبارات الـ Unit Tests، ونمنع تماماً تمرير Dispatchers صراحة من طبقة الـ UI أو الـ Composable functions."
    ),
    "how_to_answer_ar": (
        "- **السبب المعماري:** أكد فوراً وبحسم أن suspend لا تعني التنفيذ في الخلفية، بل هي علامة للمترجم لتحويل الكود إلى CPS.\n"
        "- **طريقة الشرح:** وضح أن الكوروتين يظل يعمل على الثريد الذي تم إطلاقه عليه ما لم يُنقل صراحة عبر withContext.\n"
        "- **المفاضلات:** اشرح تكلفة التبديل المفرط للسياقات مقابل وضوح الكود المتسلسل.\n"
        "- **أنماط الفشل:** استشهد بمثال دالة تشفير تعمل على Main Thread وتسبب ANR لعدم احتوائها على withContext.\n"
        "- **الحل الإنتاجي:** صرح بقاعدة Main-Safety كمعيار ذهبي لتصميم طبقات البيانات والنطاق (Data and Domain Layers)."
    ),
    "talking_points_ar": (
        "اشرح كيف يضيف المترجم معامل Continuation خفي ويعدل نوع الإرجاع إلى Any? ليتمكن من إعادة COROUTINE_SUSPENDED. ناقش كيفية بناء دوال معلقة مخصصة للتكامل مع الـ Callbacks القديمة عبر suspendCancellableCoroutine، مع توضيح أهمية استدعاء continuation.invokeOnCancellation لتنظيف الموارد غير المدارة."
    ),
    "follow_ups_ar": (
        "- **المحاور:** \"ماذا تعيد دالة الـ suspend في الـ Bytecode إذا لم تكن بحاجة للتعليق (مثل إرجاع قيمة من الكاش)؟\"\n"
        "  **المرشح:** \"إذا كانت القيمة جاهزة وموجودة في الذاكرة دون الحاجة لانتظار عملية غير متزامنة، تعيد الدالة القيمة المحسوبة مباشرة بصورة فورية، ولا تعيد رمز COROUTINE_SUSPENDED، مما يتيح للـ Caller إكمال التنفيذ فوراً دون أي جدولة إضافية.\"\n\n"
        "- **المحاور:** \"كيف تحول مكتبة قديمة تعتمد على الـ Callbacks والـ Listeners إلى دالة suspend حديثة؟\"\n"
        "  **المرشح:** \"نستخدم الدالة المعيارية suspendCancellableCoroutine؛ حيث نسجل الـ Listener الذي ينادي continuation.resume عند النجاح و continuation.resumeWithException عند الفشل، ونربط دالة إلغاء الطلب في الـ SDK القديم عبر continuation.invokeOnCancellation لضمان عدم تسريب الاتصال.\"\n\n"
        "- **المحاور:** \"لماذا نفضل withContext على إطلاق كوروتين جديد بـ launch أو async داخل دالة الـ suspend؟\"\n"
        "  **المرشح:** \"لأن withContext دالة معلقة تحافظ على التسلسل المنطقي وتعيد النتيجة مباشرة إلى نفس سياق الاستدعاء دون الحاجة لإدارة Jobs منفصلة، بينما إطلاق كوروتين جديد بداخل الدالة يكسر النمط التعبيري المتسلسل ويخلق تفرعات غير مرغوبة في شجرة المهام.\""
    ),
    "self_check_ar": (
        "تأكد من تغطية النقاط التالية: نفي دلالة الخلفية التلقائية لكلمة suspend؛ شرح آلية عمل CPS والـ Continuation؛ إيضاح مبدأ Main-Safety؛ وتطبيق withContext مع حقن الموزعات لاختبار الكود."
    ),
    "references_ar": (
        "- [Kotlin suspend functions](https://kotlinlang.org/docs/coroutines-basics.html) — توثيق كوتلن الرسمي للتعليق وآلية عمل الدوال المعلقة.\n"
        "- [Android coroutines best practices](https://developer.android.com/kotlin/coroutines/coroutines-best-practices) — ممارسات الأمان والـ Main-Safety في أندرويد.\n\n"
        "تمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13."
    ),
    "quick_answer_ar": (
        "كلمة suspend لا تعني على الإطلاق أن الكود يعمل في الخلفية تلقائياً. هي مجرد علامة للمترجم تفيد بأن هذه الدالة قادرة على تعليق تنفيذها مؤقتاً بدون حظر الثريد واستئنافها لاحقاً. الدالة المعلقة تعمل افتراضياً على نفس الثريد والـ Dispatcher الخاص بالـ Caller، وما لم تنقل العمل صراحة باستخدام withContext، فإن أي كود حظري بداخلها سيتنفذ على ثريد الواجهة."
    ),
    "best_answer_ar": (
        "من أكبر المفاهيم الخاطئة عند المطورين الاعتقاد بأن وضع كلمة suspend قبل الدالة ينقلها تلقائياً للعمل في الخلفية.\n\n"
        "الحقيقة إن كلمة suspend هي علامة للمترجم (Compiler Marker) بتعرفه إن الدالة دي قابلة للتعليق، ويتم تحويلها بنمط Continuation-Passing Style بإضافة كائن Continuation وإدارة آلة حالة داخلية.\n\n"
        "الدالة المعلقة بتشتغل افتراضياً على نفس الـ Dispatcher اللي تم استدعاؤها منه؛ يعني لو ناديتها من viewModelScope العادي، هتتنفذ مباشرة على خيط الواجهة (Main Thread)، ولو فيها كود حسابي معقد أو قراءة ملفات، هتجمد الشاشة وتسبب ANR فوراً.\n\n"
        "علشان كده، بنطبق دائماً مبدأ Main-Safety: وهو إن أي دالة معلقة في طبقة الـ Repository أو الـ UseCase لازم تكون آمنة تماماً للاستدعاء من خيط الواجهة، وهي المسؤولة ذاتياً عن نقل الشغل الثقيل إلى Dispatchers.IO أو Dispatchers.Default باستخدام withContext.\n\n"
        "ده بيفصل تماماً بين مسؤوليات طبقة الواجهة ومسؤوليات إدارة الخيوط في طبقة البيانات."
    ),
    "deep_answer_ar": (
        "على مستوى الـ Bytecode، يقوم المترجم بإعادة تشكيل توقيع الدالة بالكامل؛ فالدالة suspend fun getData(): Data تتحول داخلياً إلى fun getData(continuation: Continuation<Data>): Any?. سبب تحويل نوع القيمة المعادة إلى Any? هو أن الدالة قد ترجع كائن Data فورياً إذا كانت القيمة جاهزة ومخزنة في الكاش، أو ترجع الرمز الثابت COROUTINE_SUSPENDED إذا تطلب الأمر انتظار استجابة شبكة أو عملية غير متزامنة.\n\n"
        "تولّد مكتبة كوتلن كلاس داخلي يرث من ContinuationImpl، يحتوي على حقل label يمثل عداد البرنامج (Program Counter). عند كل نقطة تعليق، يتم تخزين المتغيرات المحلية وحالة المكدس في هذا الكائن، وعند اكتمال العملية غير المتزامنة، يُستدعى التابع continuation.resumeWith(result) الذي يعيد جدولة آلة الحالة على الـ CoroutineDispatcher المحدد لتدخل في الـ switch-case الخاص بالـ label التالي.\n\n"
        "غياب النقل التلقائي للثريد ينبع من الفلسفة التصميمية للـ Coroutines؛ فالتعليق هو عملية تجريدية لا تتطلب بالضرورة ثريداً آخر؛ فعلى سبيل المثال دالة delay لا تحجز أي ثريد على الإطلاق، بل تسجل مؤقتاً في الـ Event Loop. ولذلك، إذا لم يستخدم المطور دالة withContext لنقل العمليات الحظرية الصريحة مثل استدعاءات Java Socket أو SQLite القديمة، فإن خيط التنفيذ الحالي يظل محظوراً بالكامل.\n\n"
        "في معمارية الأنظمة الكبيرة على أندرويد، نلزم المطورين بحقن CoroutineDispatcher عبر Hilt، ونكتب اختبارات وحدة باستخدام StandardTestDispatcher للتحقق من أن دوال الـ Repository تستدعي withContext ولا تفرط في التبديل بين السياقات مما قد يرهق الـ Thread Pool."
    ),
}

COR_03_META = {
    "id": "COR-03",
    "questionAr": "ما هي أدوار CoroutineScope و CoroutineContext و Job و Deferred وكيف تتكامل معاً؟",
    "topicAr": "الـ Coroutines والتزامن في Kotlin",
    "evaluates_ar": (
        "- فهم التمايز المعماري بين CoroutineScope كحاوية دورة حياة والـ CoroutineContext كمجموعة عناصر.\n"
        "- معرفة دور الـ Job كمدير لحالات الكوروتين وشجرة الإلغاء الهرمية.\n"
        "- فهم طبيعة الـ Deferred كنوع خاص من Job يعيد قيمة مستقبلية عبر await.\n"
        "- إدراك مخاطر كسر التزامن المهيكل عبر إنشاء نطاقات عشوائية غير مدارة."
    ),
    "why_it_matters_ar": (
        "تمثل هذه العناصر الأربعة الأعمدة الأساسية التي يقوم عليها نموذج التزامن في كوتلن. الـ CoroutineScope يحدد نطاق دورة الحياة وحدود العمليات لضمان عدم بقاء أي مهمة معلقة في الذاكرة بعد تدمير صاحبها. الـ CoroutineContext هو وعاء مفهرس يحتوي على تكوين الكوروتين من ثريدات ومعالجات أخطاء وهوية. الـ Job هو المتحكم في دورة حياة الكوروتين وحالاته وتفرعاته الشجرية، بينما الـ Deferred هو امتداد للـ Job يُستخدم عند انتظار نتيجة حسابية معينة عبر await. فهم التكامل بينهم يحمي التطبيق من تسريبات الذاكرة والمهام التائهة في الخلفية."
    ),
    "worked_example_ar": (
        "كيف تتكامل هذه العناصر في سيناريو شاشة عرض بيانات المستخدم:\n"
        "```kotlin\n"
        "class UserProfileViewModel(\n"
        "    private val repository: UserRepository,\n"
        "    private val ioDispatcher: CoroutineDispatcher = Dispatchers.IO\n"
        ") : ViewModel() {\n\n"
        "    fun loadProfileData() {\n"
        "        // viewModelScope يمثل الـ CoroutineScope المرتبط بدورة حياة الشاشة\n"
        "        // launch ينشئ Job فرعي مدمج في سياق النطاق\n"
        "        val parentJob: Job = viewModelScope.launch {\n"
        "            // async ينشئ Deferred لاسترجاع بيانات غير متزامنة\n"
        "            val userDeferred: Deferred<User> = async(ioDispatcher) {\n"
        "                repository.fetchUserInfo()\n"
        "            }\n"
        "            val statsDeferred: Deferred<UserStats> = async(ioDispatcher) {\n"
        "                repository.fetchUserStats()\n"
        "            }\n"
        "            // await توقف الكوروتين الحالي حتى تكتمل الحسابات\n"
        "            val user = userDeferred.await()\n"
        "            val stats = statsDeferred.await()\n"
        "            _uiState.value = ProfileState.Ready(user, stats)\n"
        "        }\n"
        "    }\n"
        "}\n"
        "```\n"
        "إذا غادر المستخدم الشاشة، يقوم viewModelScope بإلغاء parentJob، والذي يلغي بدوره تلقائياً كلاً من userDeferred و statsDeferred."
    ),
    "trade_offs_ar": (
        "يوفر الـ CoroutineScope تحكماً صارماً في دورات حياة العمليات غير المتزامنة، ويمنع تماماً المهام التائهة. ومع ذلك، فإن إساءة استخدام النطاقات، مثل استبدال الـ Job داخل سياق النطاق عبر withContext(Job())، يقطع شجرة التزامن المهيكل ويعزل العمليات الفرعية عن الإلغاء، مما يعيد التطبيق لمشاكل تسريب الذاكرة التي صُمم النموذج لمنعها."
    ),
    "failure_modes_ar": (
        "من أخطر الأخطاء البرمجية إنشاء CoroutineScope جديد داخل دوال الـ Repository أو الـ UseCases مثل CoroutineScope(Dispatchers.IO).launch؛ لأن هذا الكود ينشئ شجرة مستقلة تماماً لا تتبع دورة حياة الشاشة، وتستمر في العمل واستنزاف البطارية حتى بعد خروج المستخدم. خطأ شائع آخر هو مناداة await على كائن Deferred تم إنشاؤه في نطاق منفصل دون التعامل مع الاستثناءات المحتملة."
    ),
    "production_perspective_ar": (
        "في معمارية التطبيقات الضخمة، نتبع قاعدة ذهبية: لا تنشئ CoroutineScope يدوياً داخل طبقات الـ Business Logic أو الـ Data Sources مطلقاً. الدوال في هذه الطبقات يجب أن تكون دوال معلقة عادية ترث سياق المستدعي، بينما تنحصر إدارة الـ Scopes في طبقة العرض عبر viewModelScope أو نطاق التطبيق المحقون (ApplicationScope) للعمليات التي يجب أن تستمر طوال فترة تشغيل التطبيق."
    ),
    "how_to_answer_ar": (
        "- **السبب المعماري:** اشرح الغرض من كل عنصر وكيف يشكلون معاً نموذج التزامن المهيكل في كوتلن.\n"
        "- **طريقة الشرح:** عرّف الـ Scope كحدود، والـ Context كحقيبة إعدادات، والـ Job كمدير حالات، والـ Deferred كـ Future يحمل قيمة.\n"
        "- **المفاضلات:** حذر من كسر الشجرة الهرمية عبر تمرير كائنات Job جديدة داخل معلمات الـ Builders.\n"
        "- **أنماط الفشل:** اذكر كارثة إنشاء CoroutineScope(Dispatchers.IO) داخل الدوال البرمجية.\n"
        "- **الحل الإنتاجي:** أكد على استخدام viewModelScope وحقن الـ Dispatchers واقتصار الـ async على العمليات المتوازية."
    ),
    "talking_points_ar": (
        "ناقش التركيب الداخلي لـ CombinedContext وكيف يعمل كـ Type-safe Heterogeneous Map. اشرح الحالات الست لدورة حياة الـ Job: New و Active و Completing و Completed و Cancelling و Cancelled، وكيف ينتظر الـ Job في حالة Completing انتهاء جميع أطفاله قبل أن يكتمل."
    ),
    "follow_ups_ar": (
        "- **المحاور:** \"ما الفرق بين استدعاء job.cancel() واستدعاء job.cancelChildren()؟\"\n"
        "  **المرشح:** \"دالة job.cancel() تلغي الـ Job نفسه وجميع أطفاله التابعين له وتنقله إلى حالة Cancelling ثم Cancelled، وبالتالي لا يمكن إطلاق كوروتينات جديدة عليه لاحقاً. بينما job.cancelChildren() تلغي فقط جميع المهام الفرعية النشطة حالياً وتبقي الـ Job الرئيسي في حالة Active وقادراً على استقبال مهام جديدة.\"\n\n"
        "- **المحاور:** \"ماذا يحدث إذا قمت بتمرير Job() جديد كمعامل داخل viewModelScope.launch(Job())؟\"\n"
        "  **المرشح:** \"هذا فخ مشهور جداً؛ تمرير Job() جديد يكسر الرابط الهرمي مع viewModelScope، ويجعل الكوروتين الجديد مستقلاً عن دورة حياة الـ ViewModel. فإذا تم تدمير الـ ViewModel، لن يتأثر هذا الكوروتين بالإلغاء وسيستمر في العمل في الخلفية مسبباً تسريباً للموارد.\"\n\n"
        "- **المحاور:** \"هل Deferred يعيد طرح الاستثناءات عند حدوث خطأ حتى لو لم نقم باستدعاء await()؟\"\n"
        "  **المرشح:** \"إذا كان الـ Deferred طفلاً داخل coroutineScope عادي، فإن فشله يؤدي فوراً إلى إلغاء الأب وإلغاء جميع الإخوة في نفس اللحظة حتى قبل مناداة await(). أما إذا تم إطلاقه في جذر supervisorScope، فسيظل الخطأ محبوساً داخل كائن الـ Deferred ولن يظهر إلا عند مناداة await().\""
    ),
    "self_check_ar": (
        "تأكد من شمول إجابتك للتالي: تعريف CoroutineScope ودوره كمرساة دورة حياة؛ تفصيل محتويات CoroutineContext؛ شرح حالات الـ Job ودوره في الإلغاء؛ وتوضيح طبيعة Deferred وطريقة عمل await."
    ),
    "references_ar": (
        "- [Kotlin coroutine context and dispatchers](https://kotlinlang.org/docs/coroutine-context-and-dispatchers.html) — توثيق كوتلن الرسمي لعناصر السياق والموزعات.\n"
        "- [Kotlin Job and hierarchy](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-job/) — التوثيق المرجعي لـ Job وشجرة التزامن.\n\n"
        "تمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13."
    ),
    "quick_answer_ar": (
        "الـ CoroutineScope يحدد نطاق دورة الحياة وحدود إطلاق الكوروتينات. الـ CoroutineContext هو مجموعة عناصر التكوين مثل الموزع ورمز المهمة ومعالج الأخطاء. الـ Job يدير دورة حياة الكوروتين وحالاته وشجرة الإلغاء الهرمية. والـ Deferred هو نوع مخصص من Job ينتج قيمة مستقبلية غير متزامنة يمكن استلامها عبر await."
    ),
    "best_answer_ar": (
        "لفهم التزامن في كوتلن كمهندس محترف، لازم تميز بدقة بين الأدوار الأربعة دي:\n\n"
        "الـ CoroutineScope هو المظلة أو مرساة دورة الحياة اللي بتحكم عمر العمليات غير المتزامنة، وبداخله بنطلق الكوروتينات عشان نضمن إن مفيش شغل يفضل شغال بعد تدمير المكون الحاضن.\n\n"
        "الـ CoroutineContext هو حقيبة التكوين؛ عبارة عن قاموس من العناصر المفهرسة بالنوع، بيحتوي على الـ Dispatcher اللي بيحدد الثريد، والـ Job، ومعالج الاستثناءات CoroutineExceptionHandler، واسم الكوروتين.\n\n"
        "الـ Job هو كيان إدارة دورة الحياة وحالة التنفيذ (Active, Cancelling, Completed)؛ وظيفته الأساسية هي تنظيم العلاقات الهرمية بين الآباء والأبناء وتوزيع الإلغاء تلقائياً.\n\n"
        "أما الـ Deferred فهو Job مضاف له ميزة إرجاع نتيجة؛ بنحصل عليه من باني async، وبنستخدم await لتعليق الكود لحين وصول القيمة المحسوبة.\n\n"
        "في مشاريع أندرويد الحقيقية، بنحافظ على التزامن المهيكل بالاعتماد على viewModelScope ومستحيل ننشئ Scopes عشوائية غير مدارة في طبقات البيانات."
    ),
    "deep_answer_ar": (
        "على المستوى المعماري الداخلي، الـ CoroutineContext مبني كهيكل بيانات غير قابل للتعديل (Persistent Data Structure) يشبه القائمة المرتبطة من نوع CombinedContext. عند إطلاق أي كوروتين جديد عبر launch أو async، تحدث عملية دمج سياقات طبقا للمعادلة: سياق الطفل يساوي سياق النطاق مضافاً إليه المعاملات الممررة في الباني ومضافاً إليه كائن Job جديد يتم إنشاؤه تلقائياً.\n\n"
        "هذا الـ Job الجديد يتم تسجيله كتابع مباشر (Child Job) في قائمة أطفال الـ Job الخاص بالنطاق الأب عبر استدعاء parentJob.attachChild(childJob). شجرة الـ Job هذه هي المحرك الأساسي لبروتوكول الاكتمال في التزامن المهيكل؛ فالـ Job الأب عند انتهاء الكود الخاص به لا ينتقل مباشرة إلى حالة Completed، بل يدخل في حالة وسيطة تسمى Completing، ولا يغادرها ليكتمل نهائياً إلا بعد اكتمال أو إلغاء كل طفل مسجل في قائمته.\n\n"
        "الـ Deferred يمثل تجسيداً لنمط الـ Future ولكن بأسلوب التعليق؛ فهو كائن DeferredCoroutine يرث من JobSupport ويطبق واجهة Deferred<T>. يحتوي داخلياً على حالة تكون إما Incomplete أو CompletedWithResult. عند مناداة await، إذا كان الحساب جارياً، يتم تعليق الـ Continuation الخاص بالمستدعي وتسجيله في طابور انتظار الكائن، وفور اكتمال الحساب يتم استئناف الـ Continuation بالنتيجة أو إعادة رمي الاستثناء إن حدث فشل.\n\n"
        "الخطأ الأكثر فداحة في الإنتاج هو كسر هذه الشجرة؛ فعندما يمرر مطور كائناً جديداً مثل launch(Job())، يقوم الـ Job الجديد بقطع الصلة الهرمية مع سياق الـ ViewModel، مما يمنع وصول إشارات الإلغاء إليه، ويترك طلبات الشبكة وقواعد البيانات تعمل إلى ما لا نهاية في الذاكرة بعد إغلاق المستخدم للشاشة."
    ),
}

COR_04_META = {
    "id": "COR-04",
    "questionAr": "ما هو التزامن المهيكل (Structured Concurrency)، ولماذا يُعد جوهرياً في تطبيقات أندرويد؟",
    "topicAr": "الـ Coroutines والتزامن في Kotlin",
    "evaluates_ar": (
        "- استيعاب مفهوم التزامن المهيكل والفرق الجوهري بينه وبين التزامن غير المنضبط (Unstructured Concurrency).\n"
        "- فهم القواعد الثلاث الحاكمة لشجرة المهام: اكتمال الأب، انتشار الإلغاء، وانتشار الفشل.\n"
        "- إدراك أهمية التزامن المهيكل في منع تسريبات الذاكرة والعمليات التائهة في أندرويد.\n"
        "- تطبيق دوال النطاق مثل coroutineScope لتنظيم العمليات المتوازية بأمان."
    ),
    "why_it_matters_ar": (
        "التزامن المهيكل هو المبدأ المعماري الذي يضمن أن العمليات غير المتزامنة لها بداية ونهاية واضحة ومقيدة بنطاق زمني محدد يتبع دورة حياة كائن مالك. في النماذج القديمة مثل Threads العادية أو GlobalScope، كانت المهام تنطلق في الخلفية ككيانات تائهة؛ فإذا خرج المستخدم من الشاشة، تظل الطلبات تعمل وتستنزف الرام والبطارية وقد تؤدي لانهيار التطبيق عند محاولة تحديث واجهات لم تعد موجودة. التزامن المهيكل يفرض علاقة أبوية صارمة: الأب لا ينتهي حتى ينتهي أطفاله، إلغاء الأب يلغي الأطفال فوراً، وفشل أي طفل يلغي باقي الإخوة والأب معاً، مما يضمن اتساق النظام ونظافة الذاكرة."
    ),
    "worked_example_ar": (
        "استخدام coroutineScope لتنفيذ عمليتين متوازيتين مع ضمان الإلغاء الذري:\n"
        "```kotlin\n"
        "suspend fun fetchCheckoutSummary(): CheckoutSummary = coroutineScope {\n"
        "    // العمليتان تنطلقان في نفس الوقت كأطفال للنطاق المهيكل\n"
        "    val cartDeferred = async { cartApi.getCartItems() }\n"
        "    val discountsDeferred = async { promoApi.getApplicableDiscounts() }\n"
        "\n"
        "    // إذا فشلت cartApi واستثنت، يتم فوراً إلغاء discountsDeferred تلقائياً\n"
        "    val cart = cartDeferred.await()\n"
        "    val discounts = discountsDeferred.await()\n"
        "    CheckoutSummary(cart, discounts)\n"
        "}\n"
        "```\n"
        "إذا حدث انقطاع في الشبكة أثناء جلب السلة، يقوم coroutineScope فوراً بإلغاء طلب الخصومات دون أي هدر في الباندويث، ويعيد الخطأ إلى المستدعي دون ترك أي مهام معلقة."
    ),
    "trade_offs_ar": (
        "يوفر التزامن المهيكل أماناً استثنائياً وسلوكاً متوقعاً للأخطاء وتلقائية في تنظيف الموارد دون الحاجة لكتابة كود تنظيف يدوي معقد. على الجانب الآخر، فإن قاعدة إلغاء الإخوة عند فشل أحدهم قد لا تناسب الشاشات التي تحتوي على عناصر مستقلة (مثل لوحة تحكم بها 5 ودجات مستقلة)؛ وفي تلك الحالات المحددة، نتجه صراحة لاستخدام supervision عبر supervisorScope بدلاً من النطاق الافتراضي الصارم."
    ),
    "failure_modes_ar": (
        "الاستخدام الكارثي للـ GlobalScope هو أبرز صور كسر التزامن المهيكل؛ حيث تطلق الكوروتينات على مستوى التطبيق ككل وتفقد أي ارتباط بدورة حياة الشاشة. خطأ آخر شائع هو التقاط استثناء الإلغاء CancellationException داخل catch(e: Exception) وعدم إعادة رميه، مما يكسر آلية انتشار الإلغاء ويجعل الكوروتين يستمر في التنفيذ رغم إلغاء الأب."
    ),
    "production_perspective_ar": (
        "في التطبيقات التجارية الكبرى، نمنع استخدام GlobalScope برمجياً عبر قواعد Lint صارمة في الـ CI/CD تمنع عمل Build إذا وُجدت. نربط كل عمليات الشاشات بـ viewModelScope، ونستخدم coroutineScope داخل طبقة الـ Repository عندما نحتاج لتقسيم مهمة واحدة إلى عدة طلبات فرعية متوازية لضمان اكتمالها كلها بنجاح أو فشلها جميعاً كنواة واحدة."
    ),
    "how_to_answer_ar": (
        "- **السبب المعماري:** عرّف التزامن المهيكل كعقد يربط عمر المهام غير المتزامنة بحدود دورة حياة واضحة.\n"
        "- **طريقة الشرح:** اذكر القواعد الثلاث: الأب ينتظر أطفاله، الإلغاء ينزل هرمياً، والفشل يلغي الإخوة والأب.\n"
        "- **المفاضلات:** وضح متى يكون نموذج All-or-Nothing مطلوباً ومتى نحتاج لعزل المهام عبر supervisorScope.\n"
        "- **أنماط الفشل:** ركز على كارثة GlobalScope وابتلاع CancellationException في كتل الـ catch.\n"
        "- **الحل الإنتاجي:** اربط المفهوم بحماية أجهزة المستخدم من استنزاف البطارية ومنع الـ Memory Leaks بعد تدمير الشاشات."
    ),
    "talking_points_ar": (
        "قارن بين التزامن المهيكل والبرمجة المهيكلة الكلاسيكية (Structured Programming) مثل حظر استخدام goto واستبدالها بـ if و while. اشرح كيف يتعامل JobSupport داخلياً مع قائمة الأطفال عبر ChildHandle وكيف يتم تمرير إشارات CancellationException هبوطاً وصعوداً."
    ),
    "follow_ups_ar": (
        "- **المحاور:** \"لماذا يعتبر GlobalScope خطيراً جداً في تطبيقات أندرويد؟\"\n"
        "  **المرشح:** \"لأنه يطلق الكوروتين على مستوى الـ Process كلها بدون أي ربط بدورة حياة الشاشات أو الـ ViewModels. فإذا غادر المستخدم الشاشة، يستمر الكوروتين في العمل في الخلفية مسبباً تسريباً للذاكرة وهدراً للبطارية والبيانات، وقد يؤدي لانهيار التطبيق إذا حاول لمس واجهة تم تدميرها بالفعل.\"\n\n"
        "- **المحاور:** \"ماذا يحدث لو قمت بابتلاع CancellationException داخل دالة تنفذ عملية طويلة؟\"\n"
        "  **المرشح:** \"ابتلاع CancellationException يمنع الكوروتين من التوقف عند إلغاء الأب؛ لأن الكوروتين يعتمد على هذا الاستثناء لإنهاء آلة الحالة الخاصة به والخروج من حلقات التكرار. النتيجة هي أن الكوروتين سيظل ينفذ الكود في الخلفية كأنه لم يُلغَ أبداً، مهدراً موارد المعالج.\"\n\n"
        "- **المحاور:** \"ما الفرق بين coroutineScope و GlobalScope.launch في طريقة التعامل مع استثناءات الأطفال؟\"\n"
        "  **المرشح:** \"في coroutineScope، إذا فشل أي طفل، يتم فوراً إلغاء جميع الأطفال الآخرين وإلغاء النطاق وإعادة طرح الاستثناء للأب للتعامل معه. أما في GlobalScope.launch، فالمهام غير مرتبطة هرمياً، وفشل أحدها لا يوقف الآخرين ويذهب الاستثناء مباشرة لـ UncaughtExceptionHandler مما قد يسقط التطبيق بأكمله.\""
    ),
    "self_check_ar": (
        "تأكد من استيفاء المعايير التالية: شرح مفهوم التزامن المهيكل بدقة؛ توضيح القواعد الثلاث لشجرة الـ Jobs؛ بيان أثر غيابه على تسريب الذاكرة في أندرويد؛ وذكر البدائل الموجهة للمهام المستقلة مثل supervisorScope."
    ),
    "references_ar": (
        "- [Structured concurrency in Kotlin](https://kotlinlang.org/docs/coroutines-basics.html#structured-concurrency) — الدليل الرسمي لمبادئ التزامن المهيكل في كوتلن.\n"
        "- [Android coroutine lifecycle guidance](https://developer.android.com/kotlin/coroutines) — إرشادات أندرويد لربط التزامن بدورات حياة المكونات.\n\n"
        "تمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13."
    ),
    "quick_answer_ar": (
        "التزامن المهيكل هو المبدأ الهندسي الذي يضمن أن كل كوروتين يتم إطلاقه داخل نطاق محدد له عمر واضح وشجرة مهام هرمية. يضمن هذا النموذج أن الأب لا يكتمل إلا بعد اكتمال أطفاله، وأن إلغاء الأب يلغي جميع الأطفال تلقائياً، وأن فشل أي طفل يلغي باقي الإخوة، مما يمنع تسريب الذاكرة والعمليات التائهة في الخلفية."
    ),
    "best_answer_ar": (
        "التزامن المهيكل هو العمود الفقري لنموذج الـ Coroutines في كوتلن، وهدفه الأساسي هو التخلص من فوضى المهام غير المتزامنة التائهة في الخلفية.\n\n"
        "في الطرق القديمة زي الثريدات العادية أو الـ GlobalScope، لما تطلق مهمة في الخلفية بتفقد السيطرة عليها؛ لو المستخدم قفل الشاشة، المهمة بتفضل شغالة وممكن تسرب الذاكرة وتصرف بطارية وانترنت على الفاضي.\n\n"
        "التزامن المهيكل بيحل ده بقواعد صارمة مبنية على شجرة الـ Jobs الهرمية:\n\n"
        "أولاً: الكوروتين الأب مبيخلصش غير لما كل الكوروتينات الأطفال اللي جواه يخلصوا شغلهم بالكامل.\n\n"
        "ثانياً: لو الكوروتين الأب اتلغى، إشارة الإلغاء بتنزل شلالياً لكل الأطفال في لحظة واحدة.\n\n"
        "ثالثاً: لو طفل من الأطفال ضرب استثناء غير ممسوك، النظام بيلغي باقي الإخوة فوراً ويلغي الأب لمنع حفظ بيانات ناقصة أو مشوهة.\n\n"
        "في أندرويد، التزامن المهيكل هو الضمان الوحيد لعدم تسريب Context الشاشات وبقاء التطبيق مستقراً وسريع الاستجابة."
    ),
    "deep_answer_ar": (
        "تاريخياً، جاء مفهوم Structured Concurrency امتداداً لمفهوم البرمجة المهيكلة (Structured Programming) التي استبدلت القفز العشوائي عبر goto بهياكل تحكم واضحة ذات نقطة دخول وخروج واحدة. في التزامن، يطبق كوتلن هذا العقد من خلال ربط كل كوروتين بنود في شجرة كائنات Job تحت مظلة CoroutineScope محدد.\n\n"
        "الارتباط بين الأب والابن يتحقق عبر واجهة ChildHandle المتبادلة؛ فعندما يطلق كود فرعي داخل دالة coroutineScope، ينشئ باني الكوروتين كائناً يطبق ChildJob ويسجله في قائمة الأطفال لدى الأب. من خلال هذه القائمة، يدير الأب مرحلة الانتقال بين حالتي Completing و Completed؛ حيث يظل الأب معلقاً في حالة Completing حتى تؤكد جميع كائنات الـ ChildHandle انتهاء مهامها الفرعية بنجاح أو بإلغاء.\n\n"
        "أما في مسار الفشل، فعند حدوث Uncaught Exception داخل أي طفل، يستدعي الطفل دالة parentCancelled(cause) عبر مقبضه، مما يجبر الأب على الانتقال فوراً إلى حالة Cancelling. يقوم الأب آنذاك بالمرور التكراري على كل الأطفال الآخرين المسجلين في الشجرة وإرسال CancellationException لهم، مما يؤدي إلى قطع اتصالات الشبكة النشطة وتحرير موارد الإدخال والإخراج فوراً.\n\n"
        "هذا التصميم يقضي نهائياً على ما يُعرف بـ Leaked Work أو Zombie Tasks. ففي أندرويد، بمجرد استدعاء ViewModel.onCleared، يتم إلغاء الـ Job الجذري الخاص بـ viewModelScope، مما يؤدي إلى تنظيف فوري وهادئ لكل العمليات الجارية في الشجرة دون أن يضطر المطور لكتابة سطر واحد من كود التنظيف اليدوي."
    ),
}

COR_05_META = {
    "id": "COR-05",
    "questionAr": "قارن بين بانيي الكوروتين launch و async/await من حيث آلية الاستخدام ومعالجة الاستثناءات.",
    "topicAr": "الـ Coroutines والتزامن في Kotlin",
    "evaluates_ar": (
        "- المقارنة الدقيقة بين هدفي الاستخدام: Fire-and-forget لـ launch مقابل جلب قيمة غير متزامنة لـ async.\n"
        "- فهم الفروق في أنواع الإرجاع: Job لمراقبة الحالة والإلغاء مقابل Deferred للحصول على النتيجة عبر await.\n"
        "- التمييز العميق في آلية انتشار الاستثناءات بين البانيين وسلوك async داخل coroutineScope.\n"
        "- معرفة الفخ الشهير لمحاولة التقاط استثناءات async بكتل try-catch داخل النطاقات العادية."
    ),
    "why_it_matters_ar": (
        "يعد launch و async الأداتين الأساسيتين لبدء الكوروتينات في كوتلن، والخلط بينهما أو إساءة فهم طريقة معالجة الأخطاء فيهما يتسبب في كوارث برمجية وانهيارات غير متوقعة للتطبيق. باني launch مصمم للمهام التي لا تنتج قيمة يطلبها المستدعي، وينشر استثناءاته فوراً صعوداً في شجرة المهام ليتم التعامل معها أو إسقاط التطبيق. في المقابل، باني async مصمم لإجراء عمليات حسابية متوازية وإرجاع كائن Deferred يحتوي على النتيجة المؤجلة لاستلامها عبر await. النقطة المحورية التي يختبرها المحاورون هي أن فشل async داخل coroutineScope عادي يؤدي لإلغاء الأب فوراً حتى لو لم يستدع المطور await على الإطلاق."
    ),
    "worked_example_ar": (
        "مقارنة عملية توضح الاستخدام الأمثل لكل باني وفخ معالجة الأخطاء:\n"
        "```kotlin\n"
        "class DashboardViewModel(\n"
        "    private val api: DashboardApi,\n"
        "    private val analytics: AnalyticsTracker\n"
        ") : ViewModel() {\n\n"
        "    fun loadDashboard() {\n"
        "        // 1. launch لمهمة Fire-and-Forget لا ننتظر منها نتيجة\n"
        "        viewModelScope.launch {\n"
        "            analytics.trackScreenOpened(\"dashboard\")\n"
        "        }\n\n"
        "        // 2. async لتشغيل طلبين متوازيين واستلام قيمتيهما معاً\n"
        "        viewModelScope.launch {\n"
        "            val balanceDeferred = async(Dispatchers.IO) { api.getBalance() }\n"
        "            val cardsDeferred = async(Dispatchers.IO) { api.getCards() }\n\n"
        "            try {\n"
        "                val balance = balanceDeferred.await()\n"
        "                val cards = cardsDeferred.await()\n"
        "                _uiState.value = DashboardState.Success(balance, cards)\n"
        "            } catch (e: Exception) {\n"
        "                _uiState.value = DashboardState.Error(e.message)\n"
        "            }\n"
        "        }\n"
        "    }\n"
        "}\n"
        "```\n"
        "إذا فشل getBalance، يتم إلقاء الاستثناء عند await ليتم التقاطه في catch، ولكن يجب الانتباه إلى أن وجودهما داخل coroutineScope فرعي عادي كان سيلغي النطاق الأب ما لم يُستخدم supervisorScope."
    ),
    "trade_offs_ar": (
        "استخدام launch خفيف ومباشر للعمليات الجانبية، بينما async يتيح تجزئة العمليات لمهام متوازية تقلل الزمن الإجمالي للاستجابة. ومع ذلك، فإن الإفراط في استخدام async للمهام المتسلسلة العادية يعد Antipattern يضيف تعقيداً غير مبرر؛ فإذا كانت العمليات تعتمد على بعضها البعض بالترتيب، فإن استدعاء دوال suspend المتسلسلة مباشرة بدون async هو الأبسط والأكفأ."
    ),
    "failure_modes_ar": (
        "أشهر فخ في مقابلات أندرويد هو كتابة try { deferred.await() } catch (e: Exception) داخل coroutineScope عادي والاعتقاد بأن الخطأ تم احتواؤه! ففي النطاق العادي، فور فشل async، يتم إرسال إشارة إلغاء للأب قبل حتى أن يصل التنفيذ لسطر await، مما يلغي النطاق بأكمله. الحل الصحيح لعزل أخطاء async هو استخدام supervisorScope."
    ),
    "production_perspective_ar": (
        "في الكود الإنتاجي، نفضل دائماً كتابة دوال suspend نظيفة تتسلسل طبيعياً، ونحصر استخدام async فقط عند وجود طلبين أو أكثر مستقلين تماماً عن بعضهما ويمكن تنفيذهما بالتوازي لتسريع تحميل الشاشة. وإذا كان أحد الطلبين اختيارياً، نغلفهما دائماً داخل supervisorScope لضمان ألا يؤدي فشل الطلب الثانوي إلى إلغاء البيانات الأساسية."
    ),
    "how_to_answer_ar": (
        "- **السبب المعماري:** قارن بين أهداف البانيين: launch للأفعال والآثار الجانبية، و async للحسابات واسترجاع القيم.\n"
        "- **طريقة الشرح:** بيّن الفارق بين نوع الإرجاع Job مقابل Deferred<T>، ودور دالة await.\n"
        "- **المفاضلات:** اشرح لماذا الدوال المعلقة المتسلسلة أفضل من async إذا لم تكن هناك حاجة للتوازي الفعلي.\n"
        "- **أنماط الفشل:** اشرح بدقة متناهية فخ try-catch حول await داخل coroutineScope العادي.\n"
        "- **الحل الإنتاجي:** استشهد باستخدام supervisorScope لعزل المهام المتوازية المستقلة في الشاشات الإنتاجية."
    ),
    "talking_points_ar": (
        "ناقش الاختلافات في الكلاسات الداخلية: StandaloneCoroutine لـ launch مقابل DeferredCoroutine لـ async. وضح كيف يتعامل handleJobException في كل منهما، وكيف يقوم async بتغليف الاستثناء داخل حالة Completing الخاصة به، ولماذا تتطلب الجذور Root async مناداة await لكشف الخطأ بينما تختلف كطفل داخل شجرة مهام عادية."
    ),
    "follow_ups_ar": (
        "- **المحاور:** \"ماذا يحدث لو أطلقت async ولم أنادِ await() عليها وحدث بداخلها استثناء؟\"\n"
        "  **المرشح:** \"إذا كانت async عبارة عن Root Coroutine تم إطلاقها مباشرة على CoroutineScope(SupervisorJob())، فسيظل الاستثناء مخزناً بداخل كائن Deferred ولن يظهر أو يسقط التطبيق طالما لم يتم استدعاء await(). ولكن إذا كانت async طفلاً داخل coroutineScope عادي، فإن فشلها يلغي النطاق الأب وجميع المهام الشقيقة فوراً في لحظة وقوع الخطأ حتى لو لم يستدع أحد await() نهائياً.\"\n\n"
        "- **المحاور:** \"هل يصح استخدام async لتشغيل مهمة واحدة فقط داخل دالة suspend؟\"\n"
        "  **المرشح:** \"لا، هذا Antipattern شائع؛ فإذا كان لديك استدعاء واحد فقط، فإن كتابته كدالة suspend عادية مثل val user = api.getUser() يكون أسرع وأنظف وأقل استهلاكاً للذاكرة؛ لأن استخدام async في هذه الحالة يضيف كائن Deferred وجدولة إضافية بدون أي فائدة توازي حقيقية.\"\n\n"
        "- **المحاور:** \"كيف تتعامل مع الأخطاء بأمان عند تشغيل عدة مهام async متوازية بحيث لا يلغي فشل إحداها الأخرى؟\"\n"
        "  **المرشح:** \"نغلف العمليات داخل supervisorScope، ونستخدم try-catch حول استدعاء await لكل مهمة على حدة، أو نستخدم awaitAll متبوعة بمعالجة الأخطاء، مما يضمن أن فشل مهمة فرعية يظل معزولاً ولا يعطل المهام الناجحة الأخرى.\""
    ),
    "self_check_ar": (
        "تحقق من إجابتك: التمييز بين غرض launch وغرض async؛ توضيح نوع الإرجاع Job مقابل Deferred؛ شرح آلية التقاط الأخطاء وتأثيرها على الأب؛ وتوضيح دور supervisorScope في حماية المهام المتوازية."
    ),
    "references_ar": (
        "- [Composing suspending functions](https://kotlinlang.org/docs/composing-suspending-functions.html) — استخدام async والتعامل مع الدوال المعلقة في كوتلن.\n"
        "- [Kotlin coroutines exception handling](https://kotlinlang.org/docs/exception-handling.html) — توثيق كوتلن الرسمي للتعامل مع استثناءات launch و async.\n\n"
        "تمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13."
    ),
    "quick_answer_ar": (
        "باني launch مخصص لمهام Fire-and-Forget التي لا تنتج قيمة، ويعيد كائن Job وتنتشر استثناءاته فوراً في شجرة المهام. أما async فهو مخصص للحسابات المتوازية التي تنتج قيمة، ويعيد كائن Deferred يسمح باستلام النتيجة عبر await. والفرق الأهم هو أن فشل async داخل نطاق عادي يلغي الأب فوراً حتى لو لم تستدع await."
    ),
    "best_answer_ar": (
        "المقارنة بين launch و async هي من أهم الأسئلة في المقابلات لأنها بتبين فهمك للتعامل مع النتائج والأخطاء.\n\n"
        "باني launch بنستخدمه للعمليات اللي مش محتاجين منها قيمة راجعة (Fire-and-Forget)، زي تسجيل Analytics أو حفظ في داتابيز محلياً، وبيرجع كائن Job لمتابعة حالة التنفيذ أو الإلغاء. أي استثناء بيحصل جواه بيطلع فوراً للأب ويلغي الشجرة.\n\n"
        "أما async، فهو مخصص للعمليات المتوازية اللي بتنتج نتيجة، وبيرجع كائن Deferred<T> اللي هو في الحقيقة Job بيحتوي على قيمة مستقبلية بنستلمها بمناداة await.\n\n"
        "الفارق الجوهري اللي بيقع فيه كتير من المطورين هو آلية انتشار الأخطاء:\n\n"
        "لو استخدمت async كـ Root في supervisorScope، الاستثناء بيفضل محبوس جواها ومش هيترمي إلا لما تنادي await.\n\n"
        "لكن لو async شغالة جوه coroutineScope عادي، فشلها بيلغي الأب وكل الإخوة في نفس اللحظة، وعمل try-catch حوالين await مش هيمنع الإلغاء ده!\n\n"
        "عشان كده في الإنتاج، لما نحب نشغل طلبات شبكة متوازية ومستقلة، بنستخدم supervisorScope مع async لضمان عزل الأخطاء."
    ),
    "deep_answer_ar": (
        "تحت الغطاء، يبني launch كائناً من نوع StandaloneCoroutine، بينما يبني async كائناً من نوع DeferredCoroutine. كلاهما يرث من AbstractCoroutine، ولكن الاختلاف يكمن في كيفية التعامل مع دالة handleJobException وطريقة إنهاء الـ Job.\n\n"
        "في StandaloneCoroutine، عند حدوث استثناء غير معالج، يقوم الكوروتين بإرسال الاستثناء فوراً إلى سياق الأب عبر parentContext.handleCoroutineException(exception). هذا يعني أن الاستثناء لا ينتظر أحداً، ويتحرك صعوداً في الشجرة الهرمية حتى يصل للجذر، فإذا لم يتم اعتراضه بموزع مشرف، يتم تمريره إلى CoroutineExceptionHandler أو إلى معالج الاستثناءات الافتراضي للـ Thread، مما يتسبب في كراش للتطبيق.\n\n"
        "في المقابل، DeferredCoroutine يمسك بنتيجة التنفيذ سواء كانت قيمة ناجحة أو كائن Throwable ويخزنها كحالة اكتمال داخلية. عند استدعاء await، تفحص الدالة هذه الحالة؛ إذا كانت ناجحة تعيد القيمة، وإذا كانت فاشلة تقوم بفك وتغليف الاستثناء وإعادة طرحه في نقطة استدعاء await مع الحفاظ على الـ Coroutine Stack Trace.\n\n"
        "لكن الخطورة تكمن في الخلط بين تغليف الاستثناء في Deferred وسلوك التزامن المهيكل؛ فإذا كانت async طفلاً في شجرة مهام عادية، فإنها فور وقوع الخطأ تستدعي cancelParent(exception). هذا الاستدعاء يضع الأب في حالة Cancelling ويلغي جميع الإخوة الشغالين بالتوازي. وعندما يصل كود المطور لسطر await داخل كتلة try-catch، ينجح الـ catch في مسك الاستثناء الناتج عن await، لكنه يكتشف بعد فوات الأوان أن النطاق الأب تم تدميره وإلغاؤه بالفعل! الحل الهندسي الصارم في أندرويد هو الجمع بين supervisorScope و async عندما تكون العمليات المتوازية غير معتمدة على نجاح بعضها البعض."
    ),
}

BATCH_1 = [
    ("COR-01", COR_01_EN, COR_01_META),
    ("COR-02", COR_02_EN, COR_02_META),
    ("COR-03", COR_03_EN, COR_03_META),
    ("COR-04", COR_04_EN, COR_04_META),
    ("COR-05", COR_05_EN, COR_05_META),
]


def run_batch_1():
    print("Updating Canonical Markdown files for COR-01 to COR-05...")
    metadata_batch = {}
    for qid, en_data, meta_data in BATCH_1:
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
    run_batch_1()
