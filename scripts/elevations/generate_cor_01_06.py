#!/usr/bin/env python3
"""Generator for COR-01 through COR-06 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "cor.json"

COR_01_06 = [
    {
        "id": "COR-01",
        "arabic_explanation": (
            "الفرق بين الـ Coroutine والـ Thread هو حجر الأساس لفهم التزامن (Concurrency) في Kotlin و Android:\n\n"
            "1. الـ Thread (خيط المعالجة في الـ OS):\n"
            "   - هو كيان ثقيل يديره نظام التشغيل (OS-managed Kernel Thread).\n"
            "   - كل Thread بيحجز مساحة ثابتة في الذاكرة للـ Stack بتاعه (عادة 1 ميجابايت على JVM وحوالي 512-1024KB على Android ART).\n"
            "   - التبديل بين الـ Threads (Context Switching) مكلف جداً في الـ CPU؛ لأنه بيتطلب الانتقال بين User Mode و Kernel Mode وتفريغ سجلات المعالج.\n"
            "   - لو حاولت تشغل 10,000 Thread في نفس الوقت على جهاز أندرويد، التطبيق هيعمل Crash بـ `OutOfMemoryError: unable to create new native thread` فوراً!\n\n"
            "2. الـ Coroutine (خيط المعالجة الخفيف في User-space):\n"
            "   - هي **Lightweight Thread** يتم إدارتها بالكامل في User Space بواسطة مكتبة Kotlin (`kotlinx.coroutines`) بدون تدخل الـ OS Kernel.\n"
            "   - مش مربوطة بـ Thread معين؛ الـ Coroutine عبارة عن State Machine وكائن صغير في الـ Heap لا يتعدى حجمه بضع مئات من الـ Bytes.\n"
            "   - عند التعليق (Suspension)، الـ Coroutine بتسيب الـ Thread بتاعها لكي ينفذ مهام تانية، ولما ترجع تشتغل، ممكن تكمل على نفس الـ Thread أو Thread تاني خالص من الـ Dispatcher Pool بدون أي Context Switch للـ OS!\n"
            "   - تقدر تشغل 100,000 Coroutine في نفس الوقت على جهاز موبايل عادي بدون أي مشكلة في الذاكرة."
        ),
        "practical_walkthrough": (
            "في شاشة قائمة المنتجات (Product Catalog):\n"
            "- محتاجين نعمل 1,000 طلب خفيف لجلب أسعار المنتجات في الخلفية.\n"
            "- **النهج الكارثي مع Threads:**\n"
            "  `repeat(1000) { Thread { fetchPrice(it) }.start() }`\n"
            "  هذا الكود سينشئ 1,000 OS Thread، يستهلك حوالي 1 جيجابايت RAM، ويسبب OOM Crash وتهنيج للجهاز بالكامل.\n"
            "- **النهج الصحيح مع Coroutines:**\n"
            "  `repeat(1000) { viewModelScope.launch(Dispatchers.IO) { fetchPrice(it) } }`\n"
            "  الـ 1,000 Coroutine هيتشاركوا في Thread Pool مكون من عدد محدود من الـ Threads (عادة 64 thread كحد أقصى في Dispatchers.IO)، ويتم تعليقهم بدون حجز أي موارد إضافية أثناء انتظار استجابة السيرفر."
        ),
        "quick_answer": "A coroutine is a lightweight, cooperative concurrency primitive managed entirely in user space by the Kotlin runtime, whereas a thread is an expensive operating-system resource with its own dedicated memory stack. Coroutines can suspend without blocking their underlying thread, allowing millions of concurrent tasks on a handful of OS threads.",
        "best_answer": (
            "The fundamental difference is that a thread is an operating system kernel resource, while a coroutine is a user-space abstraction managed by the Kotlin runtime.\n\n"
            "An OS thread is heavy: each thread allocates its own 1MB call stack in memory, and switching between threads requires expensive OS kernel context switches. Spawning thousands of threads will quickly crash an Android app with an OutOfMemoryError.\n\n"
            "A coroutine, by contrast, is completely lightweight—it is essentially an object instance in the heap representing a state machine, weighing only a few hundred bytes. When a coroutine executes a suspending operation like an API call or delay, it does not block the underlying OS thread; it unbinds itself and frees that thread to do other work, such as rendering UI frames. Once the asynchronous work completes, the coroutine resumes on an available thread in its dispatcher pool."
        ),
        "deep_answer": (
            "Under the hood, the Kotlin compiler transforms every suspending function into a state machine implementing the `Continuation<T>` interface, passing a continuation parameter under the continuation-passing style (CPS) transformation. "
            "When a suspension point is reached, the function stores its local frame state onto the heap and returns a special marker value `COROUTINE_SUSPENDED`. The underlying thread is immediately released back to its thread pool executor.\n\n"
            "In contrast to preemptive multithreading where the OS scheduler forcibly interrupts threads at arbitrary time slices, coroutines are cooperative: a coroutine runs until it explicitly yields or reaches a suspension point. "
            "In Android architecture, this distinction is vital for UI fluidity. Blocking the main thread with a synchronous call freezes the Looper message queue, dropping frames below the 16.6ms or 8.3ms threshold and triggering an ANR dialog if blocked for 5 seconds under user input. Suspending on the main thread simply returns control to the Android Choreographer loop, keeping UI touch events and 120Hz frame rendering completely smooth."
        ),
        "follow_ups": [
            {
                "interviewer": "Can a coroutine resume on a different thread than the one it started on?",
                "answer": "Yes. Unless confined to a single-threaded dispatcher like Dispatchers.Main, a coroutine running on a thread pool (like Dispatchers.Default or Dispatchers.IO) may suspend on thread A and resume execution on thread B once its asynchronous task finishes."
            },
            {
                "interviewer": "What happens if a coroutine executes a heavy blocking call like Thread.sleep() instead of delay()?",
                "answer": "Thread.sleep() blocks the underlying OS thread. If that coroutine is running on Dispatchers.Main, it freezes the Android UI and triggers an ANR. If running on a worker pool, it starves that pool's worker thread, depriving other coroutines of execution time."
            },
            {
                "interviewer": "How does memory allocation compare between 1,000 threads and 1,000 coroutines?",
                "answer": "1,000 threads require approximately 500MB to 1GB of dedicated stack memory allocated from native RAM, typically crashing mobile processes. 1,000 coroutines require only a few megabytes on the JVM heap for their Continuation instances."
            }
        ]
    },
    {
        "id": "COR-02",
        "arabic_explanation": (
            "معنى كلمة `suspend` في Kotlin هو محور شائع جداً في أسئلة المقابلات، وفيه مغالطة شهيرة بيقع فيها كتير من المطورين:\n\n"
            "1. هل `suspend` تعني أن الكود يعمل في الـ Background تلقائياً؟\n"
            "   - **إطلاقاً! لا تعني ذلك على الإطلاق! (Common Fallacy)**\n"
            "   - كتابة `suspend fun doWork()` لا تعني نقل التنفيذ لـ Background Thread.\n"
            "   - لو كتبت `suspend fun calculate() { while(true) {} }` وناديتها من `viewModelScope.launch` بدون تحديد Dispatcher، الكود هيفضل شغال على الـ **Main Thread** وهيعمل تجميد للشاشة (ANR)!\n\n"
            "2. ما هو المعنى الحقيقي لـ `suspend`؟\n"
            "   - كلمة `suspend` هي **إشارة للمترجم (Compiler Marker)** بأن هذه الدالة قادرة على 'تعليق' تنفيذها وإفساح المجال للـ Thread بدون حظر (Without blocking)، وأنها لا يمكن استدعاؤها إلا من داخل Coroutine أو دالة `suspend` أخرى.\n"
            "   - المترجم بيعيد كتابة الدالة باستخدام **CPS (Continuation Passing Style)** ويضيف لها معامل خفي `completion: Continuation<T>`.\n\n"
            "3. مبدأ الأمان للـ Main Thread (Main-Safety):\n"
            "   - كـ Senior Engineer، لازم أي `suspend fun` تكتبها تكون **Main-Safe**؛ يعني لو المتصل ناداها من الـ Main Thread، وظيفة الدالة هي نفسها اللي تنقل الشغل الثقيل لـ `Dispatchers.IO` أو `Dispatchers.Default` عبر `withContext` قبل ما ترجع."
        ),
        "practical_walkthrough": (
            "في دالة قراءة وتشفير ملف كبير:\n"
            "- **الكود الخادع (Unsafe Suspend Function):**\n"
            "  suspend fun encryptFile(file: File): ByteArray {\n"
            "      // كارثة: هذا الكود يعمل على الـ Caller Thread! لو نودي من Main هيعمل ANR\n"
            "      return Cipher.getInstance(...).doFinal(file.readBytes())\n"
            "  }\n"
            "- **الكود الاحترافي (Main-Safe Suspend Function):**\n"
            "  suspend fun encryptFile(file: File): ByteArray = withContext(Dispatchers.Default) {\n"
            "      // الآن الدالة أصبحت Main-Safe؛ أي متصل يقدر يناديها بأمان تام من Main Thread\n"
            "      Cipher.getInstance(...).doFinal(file.readBytes())\n"
            "  }\n"
            "- القاعدة الذهبية: المصمم للدالة هو المسؤول عن تحديد الـ Dispatcher المناسب، وليس المستدعي."
        ),
        "quick_answer": "No, 'suspend' does not imply background execution. It simply indicates that the function can pause its execution without blocking its current thread and resume later. By default, a suspend function runs on whichever dispatcher or thread the caller launched it on, unless it explicitly switches context using withContext.",
        "best_answer": (
            "The `suspend` keyword does not mean background execution. A common junior misconception is that marking a function with `suspend` automatically moves its execution off the main thread. It does not.\n\n"
            "If you launch a coroutine on Dispatchers.Main and call a suspend function containing a CPU-intensive loop or a blocking read, it will run directly on the main thread and freeze the Android UI.\n\n"
            "What `suspend` actually does is mark a function as capable of non-blocking suspension. The Kotlin compiler rewrites it using Continuation-Passing Style, adding a hidden `Continuation` parameter and generating a state machine. It allows the function to yield its thread during asynchronous operations like network calls or delays.\n\n"
            "As an Android architect, I enforce the principle of **Main-Safety**: every public suspend function must be safe to call from Dispatchers.Main. If the function performs disk I/O or heavy computation, it is internally responsible for wrapping that work in `withContext(Dispatchers.IO)` or `withContext(Dispatchers.Default)`."
        ),
        "deep_answer": (
            "From a bytecode standpoint, the compiler transforms `suspend fun fetch(): String` into `fun fetch(continuation: Continuation<String>): Any?`. The return type becomes `Any?` because the method can either return the concrete `String` immediately if data is already cached, or return the singleton `COROUTINE_SUSPENDED` if an asynchronous wait is required.\n\n"
            "The suspension mechanism relies on callbacks at the lowest level: when you call an asynchronous SDK via `suspendCancellableCoroutine`, you register a listener that will invoke `continuation.resume(value)` upon completion. At that moment, the coroutine is queued back onto the designated CoroutineDispatcher's event loop.\n\n"
            "In team code reviews, we treat any suspend function that blocks a thread or lacks internal dispatching for heavy work as a high-severity bug. Suspend functions must maintain zero thread affinity for the caller, guaranteeing that callers never need to guess whether they should wrap repository calls in `withContext(Dispatchers.IO)`."
        ),
        "follow_ups": [
            {
                "interviewer": "Why does Retrofit or Room not require `withContext(Dispatchers.IO)` for suspend functions?",
                "answer": "Because both Retrofit and Room are internally implemented to be Main-Safe. Retrofit uses OkHttp's asynchronous enqueue mechanism under the hood, and Room dispatches database queries to its own internal transaction executor before returning."
            },
            {
                "interviewer": "Can you call a suspend function from regular non-suspending Kotlin code?",
                "answer": "No, not directly. Suspend functions require a CoroutineContext and a Continuation to operate. To call a suspend function from non-suspending code, you must create a coroutine boundary using a builder like `launch`, `async`, or in unit tests, `runTest`."
            },
            {
                "interviewer": "What is the performance overhead of adding `suspend` to a function that doesn't actually suspend?",
                "answer": "The overhead is negligible but non-zero: the compiler still generates a small state machine and passes a Continuation parameter. If a function never suspends, marking it `suspend` is unnecessary and clutters the API contract."
            }
        ]
    },
    {
        "id": "COR-03",
        "arabic_explanation": (
            "لفهم هيكل الـ Coroutines، لازم تفكك العناصر الأربعة الأساسية اللي بتبني أي Coroutine في Kotlin:\n\n"
            "1. الـ `CoroutineContext` (سياق العمل):\n"
            "   - هو عبارة عن **Map من العناصر الفردية** التي تحدد سلوك الـ Coroutine.\n"
            "   - بيحتوي على 4 عناصر رئيسية:\n"
            "     * `Job`: يدير دورة الحياة والإلغاء والعلاقة الهرمية (Parent-Child).\n"
            "     * `CoroutineDispatcher`: يحدد أي Thread أو Thread Pool سينفذ الكود (Main, IO, Default).\n"
            "     * `CoroutineName`: اسم للـ Debugging والـ Logging.\n"
            "     * `CoroutineExceptionHandler`: يتعامل مع الـ Uncaught Exceptions في Root Coroutines.\n"
            "   - العناصر بتندمج باستخدام المعامل `+` (زي `Dispatchers.IO + CoroutineName(\"Upload\")`).\n\n"
            "2. الـ `CoroutineScope` (نطاق العمل):\n"
            "   - هو مجرد **Wrapper حول `CoroutineContext`** (`interface CoroutineScope { val coroutineContext: CoroutineContext }`).\n"
            "   - وظيفته الأساسية هي تطبيق **Structured Concurrency**: يضمن أن كل Coroutine ليها نطاق حياة محدد (Scope Boundary)، ولو انتهى الـ Scope (زي مسح الـ ViewModel)، يتم إلغاء كل العمليات التابعة له فوراً لمنع Memory Leaks.\n\n"
            "3. الـ `Job`:\n"
            "   - كائن يمثل دورة حياة الـ Coroutine وحالاتها: `isActive`, `isCompleted`, `isCancelled`.\n"
            "   - لا يحمل قيمة مرجعة؛ وظيفته التحكم في الإلغاء والانتظار (`join()`).\n\n"
            "4. الـ `Deferred<T>`:\n"
            "   - هو **Job يحمل قيمة مرجعة في المستقبل (Future/Promise)**.\n"
            "   - يورث من `Job` ويضيف دالة `await(): T` للحصول على النتيجة بمجرد اكتمالها."
        ),
        "practical_walkthrough": (
            "في دالة البحث وجلب تفاصيل المستخدم:\n"
            "- **استخدام Scope و Context و Job و Deferred معاً:**\n"
            "  // 1. الـ CoroutineScope يحدد النطاق (مثلاً viewModelScope)\n"
            "  // 2. دمج عناصر الـ CoroutineContext باستخدام +\n"
            "  val customContext = Dispatchers.IO + CoroutineName(\"UserFetchJob\")\n"
            "  // 3. launch ترجع Job للتحكم في الإلغاء بدون انتظار قيمة:\n"
            "  val syncJob: Job = viewModelScope.launch(customContext) {\n"
            "      syncDatabase()\n"
            "  }\n"
            "  // 4. async ترجع Deferred<T> لانتظار قيمة في المستقبل:\n"
            "  val userDeferred: Deferred<User> = viewModelScope.async(Dispatchers.IO) {\n"
            "      api.getUserDetails()\n"
            "  }\n"
            "  // في دالة العرض: ننتظر النتيجة بـ await()\n"
            "  val user = userDeferred.await()"
        ),
        "quick_answer": "CoroutineContext is an indexed set of elements (Job, Dispatcher, Name, ExceptionHandler) defining coroutine behavior; CoroutineScope wraps a context to enforce structured lifecycle boundaries; Job represents a cancellable task lifecycle without a result; and Deferred<T> extends Job to represent an asynchronous computation that yields a value via await().",
        "best_answer": (
            "These four concepts form the core structural architecture of Kotlin Coroutines:\n\n"
            "First, **CoroutineContext** is a persistent, indexed element set that configures the execution environment. Its key elements are the CoroutineDispatcher (which thread pool runs the code), the Job (lifecycle and cancellation tracking), the CoroutineName (for logging), and the CoroutineExceptionHandler.\n\n"
            "Second, **CoroutineScope** simply encapsulates a CoroutineContext. Its primary architectural purpose is establishing boundary ownership under structured concurrency. It ensures that coroutines are launched within a well-defined lifecycle (like `viewModelScope` or `lifecycleScope`), guaranteeing that background work is automatically cleaned up when the owner is destroyed.\n\n"
            "Third, a **Job** represents a cancellable background task with a defined state lifecycle (Active, Completing, Completed, Cancelled). It controls cancellation and parent-child hierarchy but does not return a value.\n\n"
            "Fourth, **Deferred<T>** is an interface that extends Job. It represents a promise of a future result, produced by the `async` builder, whose computed value is retrieved by calling the suspending method `await()`."
        ),
        "deep_answer": (
            "At the implementation level, `CoroutineContext` is implemented as an associative map using a polymorphic key system (`Element : CoroutineContext`). You can combine contexts using the `+` operator, where keys on the right overwrite identical keys on the left (e.g., `Dispatchers.Default + Dispatchers.IO` yields `Dispatchers.IO`).\n\n"
            "When a new coroutine is launched, the runtime calculates its effective context through **Context Inheritance**: the child coroutine inherits the parent's context, overwrites it with any arguments passed to the builder, creates a new `Job` instance representing this child, and establishes a bidirectional link between the parent Job and the child Job.\n\n"
            "This parent-child Job link is the engine of structured concurrency: 1) if the parent Job is cancelled, it immediately cancels all child Jobs; 2) if an uncaught exception occurs in a standard child Job, it cancels its parent and all sibling Jobs; and 3) a parent Job does not transition to the Completed state until all of its child Jobs have completed."
        ),
        "follow_ups": [
            {
                "interviewer": "What happens if you pass an explicit Job to `launch` inside `viewModelScope` (e.g., `viewModelScope.launch(Job())`)?",
                "answer": "Passing `Job()` breaks structured concurrency. It severs the parent-child relationship between `viewModelScope` and the new coroutine. If the ViewModel is cleared, the newly launched coroutine will NOT be cancelled automatically, causing background memory leaks."
            },
            {
                "interviewer": "How does `Job.cancel()` differ from `Job.cancelChildren()`?",
                "answer": "`Job.cancel()` cancels the parent Job and all its children permanently; the parent can never be used to launch new coroutines again. `Job.cancelChildren()` cancels all active child coroutines while keeping the parent Job active, allowing you to launch new tasks under the same scope."
            },
            {
                "interviewer": "Is `Deferred.await()` safe to call multiple times?",
                "answer": "Yes. Once a `Deferred` completes, its result is cached. Calling `await()` multiple times returns the already-computed value immediately without re-executing the underlying task."
            }
        ]
    },
    {
        "id": "COR-04",
        "arabic_explanation": (
            "الـ Structured Concurrency هي أهم فلسفة معمارية تميز Kotlin Coroutines عن أنظمة التزامن القديمة في Java (زي Thread و RxJava):\n\n"
            "1. المشكلة في التزامن غير المهيكل (Unstructured Concurrency):\n"
            "   - في الأنظمة القديمة، لما تشغل `Thread` أو `CompletableFuture` أو `GlobalScope.launch`، العمليات دي بتنطلق في الفضاء بدون أي أب شرعي (Fire and Forget).\n"
            "   - **تسريب الذاكرة (Memory Leaks):** لو المستخدم خرج من الشاشة، الـ Thread هيفضل شغال في الـ Background، يستهلك بطارية و RAM، وممكن يحاول يعدل View ملغية فيعمل Crash.\n"
            "   - **فقدان الاستثناءات (Lost Exceptions):** لو عملية في الخلفية فشلت ورمت Exception، الـ Exception بيضيع في الفضاء أو يوقع التطبيق بدون ما الكود الرئيسي يعرف.\n\n"
            "2. ما هي الـ Structured Concurrency؟\n"
            "   - هي قاعدة تنص على: **لا يمكن إطلاق أي Coroutine إلا داخل CoroutineScope محدد له دورة حياة واضحة، وكل Coroutine له أب (Parent Job) مسؤول عنه.**\n"
            "   - **شجرة العمليات (Hierarchy Tree):**\n"
            "     * إلغاء الأب يؤدي تلقائياً إلى إلغاء جميع الأبناء والأحفاد.\n"
            "     * الأب لا يعتبر منتهياً (`Completed`) إلا بعد انتهاء جميع أبنائه بنجاح.\n"
            "     * فشل أي ابن يتم تصعيده للأب فوراً ليتخذ القرار الصحيح (إلغاء باقي الإخوة أو المعالجة).\n\n"
            "3. الفائدة في تطبيقات Android الإنتاجية:\n"
            "   - الربط المباشر مع دورات حياة الـ Android عبر `viewModelScope` و `lifecycleScope` يضمن 0% Memory Leaks عند مغادرة الشاشات."
        ),
        "practical_walkthrough": (
            "في شاشة تفاصيل الحساب البنكي:\n"
            "- بنطلب الرصيد وبنطلب آخر 10 معاملات بشكل متزامن داخل ViewModel:\n"
            "- **النهج غير المهيكل والخطير (Unstructured):**\n"
            "  `GlobalScope.launch { fetchBalance() }`\n"
            "  `GlobalScope.launch { fetchTransactions() }`\n"
            "  لو المستخدم ضغط زر الرجوع (Back) فوراً، العمليتين هيفضلوا شغالين على السيرفر وبيسحبوا باقة المستخدم بدون أي فائدة!\n"
            "- **النهج المهيكل والآمن (Structured Concurrency):**\n"
            "  viewModelScope.launch {\n"
            "      coroutineScope {\n"
            "          val balance = async { repo.getBalance() }\n"
            "          val transactions = async { repo.getTransactions() }\n"
            "          _uiState.value = UiState.Success(balance.await(), transactions.await())\n"
            "      }\n"
            "  }\n"
            "- بمجرد مغادرة الشاشة، الـ ViewModel بيموت وينادي `viewModelScope.cancel()`، فتلغى عمليتا الشبكة فوراً بدون سطر كود تنظيف يدوي واحد!"
        ),
        "quick_answer": "Structured concurrency guarantees that concurrent tasks have clear hierarchical lifecycles tied to a scope. Child coroutines cannot outlive their parent, cancellation propagates down the entire hierarchy tree, parent coroutines wait for all children before completing, and child failures propagate up to prevent leaked operations.",
        "best_answer": (
            "Structured concurrency is a design paradigm ensuring that asynchronous operations are bound to a strict hierarchical lifecycle. In older models like raw threads or GlobalScope, background tasks were launched into the wild with no parent; if the calling component was destroyed, those background tasks became zombie threads, causing memory leaks, battery drain, and unhandled crashes.\n\n"
            "With structured concurrency in Kotlin, every coroutine must be launched inside a `CoroutineScope`. This establishes a formal parent-child tree governed by three foundational rules:\n\n"
            "1. **Cancellation cascades downward:** Cancelling a parent scope automatically cancels all its children and nested descendants.\n"
            "2. **Completion waits for children:** A parent coroutine or scope cannot complete until every one of its spawned children finishes.\n"
            "3. **Error propagation cascades upward:** If a child fails with an unhandled exception, that failure is immediately propagated up to the parent, which cancels sibling tasks and prevents dangling, corrupted state.\n\n"
            "In Android, this eliminates lifecycle leaks by binding coroutines directly to architectural lifecycles through `viewModelScope` and `lifecycleScope`."
        ),
        "deep_answer": (
            "Under the hood, structured concurrency is maintained through the `Job` hierarchy. When you invoke `scope.launch`, the builder extracts the parent `Job` from the scope's context and creates a new child `Job`. The child attaches a completion and cancellation listener to the parent, and the parent registers the child in its internal child list.\n\n"
            "This tree structure directly governs exception handling. When a child coroutine encounters an uncaught exception (other than `CancellationException`), it notifies its parent via `childCancelled()`. By default, standard parent jobs cancel all other active siblings to maintain transactional integrity, preventing the application from continuing in a half-finished, inconsistent state.\n\n"
            "When creating custom scopes—such as an application-wide scope for database migrations or telemetry flushing—we deliberately configure a `SupervisorJob` to prevent a single telemetry failure from tearing down the entire application scope. However, we never use `GlobalScope` because it is an unbound, top-level scope that bypasses structured concurrency entirely."
        ),
        "follow_ups": [
            {
                "interviewer": "Why is `GlobalScope` considered a dangerous anti-pattern?",
                "answer": "`GlobalScope` is an unbound, application-lifetime scope that has no parent Job. Any coroutines launched in `GlobalScope` operate outside structured concurrency: they cannot be cancelled together, their lifecycles cannot be tracked, and exceptions in them cannot be caught by local error handlers, making them a primary cause of memory leaks and zombie network requests."
            },
            {
                "interviewer": "How does `coroutineScope { }` enforce structured concurrency in suspend functions?",
                "answer": "`coroutineScope` creates a local child scope within an existing coroutine. It suspends until all coroutines launched within its block complete. If any child coroutine fails, it cancels all remaining children and rethrows the exception, ensuring the suspend function never leaves orphaned concurrent work behind."
            },
            {
                "interviewer": "What is the difference between structured concurrency failure propagation in `coroutineScope` versus `supervisorScope`?",
                "answer": "In `coroutineScope`, a failure in any child immediately cancels the scope and all sibling coroutines. In `supervisorScope`, a failure in one child is contained: siblings continue executing, and the parent scope remains active."
            }
        ]
    },
    {
        "id": "COR-05",
        "arabic_explanation": (
            "المقارنة بين `launch` و `async` بتكشف فهمك لطرق استدعاء الـ Coroutines والتعامل مع النتائج والاستثناءات:\n\n"
            "1. دالة `launch` (Fire-and-Forget):\n"
            "   - بتستخدم لما تكون عايز تبدأ عملية ومش مستني منها قيمة مرجعة (No return value).\n"
            "   - بترجع كائن `Job` يُستخدم للتحكم في دورة الحياة (زي الإلغاء بـ `job.cancel()` أو الانتظار بـ `job.join()`).\n"
            "   - **التعامل مع الاستثناءات (Exception Handling):** أي Uncaught Exception بيحدث داخل `launch` بيتم رميه وتصعيده فوراً للـ Parent Job والـ Uncaught Exception Handler؛ لا ينتظر أن تنادي أي دالة.\n\n"
            "2. دالة `async` (Compute-and-Return):\n"
            "   - بتستخدم لما تكون بتشغل عملية غير متزامنة وعايز ترجع منها نتيجة (Returns a computed value).\n"
            "   - بترجع كائن `Deferred<T>` (وهو نوع من أنواع الـ Job).\n"
            "   - للحصول على النتيجة، بتنادي الدالة المعلقة `await(): T`.\n"
            "   - **التعامل مع الاستثناءات:** الاستثناء بيتم تغليفه داخل الـ `Deferred`، وبيترمي لما المتصل ينادي `await()`. لكن انتبه: في الـ Standard `coroutineScope`، حتى لو منادتش `await()`، فشل `async` هيصعد الاستثناء للأب ويلغي باقي الإخوة!\n\n"
            "3. خطأ شائع جداً (Anti-pattern):\n"
            "   - استخدام `async` لما مفيش قيمة مرجعة، أو استخدام `async` متتالي في سطرين وراء بعض بدون توازي حقيقي: `val a = async { ... }.await()` ده بيمشي تسلسلي مش متوازي!"
        ),
        "practical_walkthrough": (
            "في شاشة الحساب: جلب الملف الشخصي وقائمة الإشعارات بالتوازي:\n"
            "- **النهج الخاطئ (Sequential async):**\n"
            "  val profile = async { api.getProfile() }.await() // انتظر حتى ينتهي بالكامل أولاً!\n"
            "  val notifications = async { api.getNotifications() }.await() // بدأ بعد ما الأول خلص!\n"
            "  كده مفيش أي توازي؛ الكود اشتغل تسلسلي وخسرنا ميزة الـ async.\n"
            "- **النهج الصحيح (True Parallelism):**\n"
            "  val profileDeferred = async { api.getProfile() } // بدأ فوراً في الخلفية\n"
            "  val notificationsDeferred = async { api.getNotifications() } // بدأ في نفس اللحظة بالتوازي\n"
            "  // الآن ننتظر النتيجتين معاً:\n"
            "  val state = UiState(profileDeferred.await(), notificationsDeferred.await())\n"
            "- **متى نستخدم launch؟**\n"
            "  `viewModelScope.launch { repo.logAnalyticsEvent(event) }` // عملية إرسال لا تحتاج انتظار نتيجة."
        ),
        "quick_answer": "Use 'launch' for fire-and-forget tasks that do not return a result, which yields a Job and throws unhandled exceptions immediately. Use 'async' when an asynchronous computation produces a result, which yields a Deferred<T> whose value is retrieved by calling await(), exposing errors at the await call site.",
        "best_answer": (
            "The distinction between `launch` and `async` comes down to return values and error dispatching.\n\n"
            "I use `launch` for 'fire-and-forget' side-effect operations where the caller does not need a computed result—such as updating a database, triggering a sync, or mutating UI state. `launch` returns a `Job`, which allows me to monitor its lifecycle, await completion with `join()`, or cancel it. If an unhandled exception occurs inside `launch`, it propagates immediately up the hierarchy tree.\n\n"
            "I use `async` when I need to compute a value asynchronously, especially when running multiple concurrent operations in parallel. `async` returns a `Deferred<T>`, which is a promise of a future value. Calling `await()` suspends until the value is ready and returns it.\n\n"
            "A critical pitfall to avoid is calling `await()` immediately on the same line as `async`. That forces sequential execution. To get true concurrency, you must start all `async` deferreds first, and only then await their results."
        ),
        "deep_answer": (
            "Under the hood, `launch` creates a `StandaloneCoroutine`, whereas `async` creates a `DeferredCoroutine<T>`. "
            "This architectural difference heavily impacts exception behavior. In a root coroutine created with `async` outside of structured supervision, uncaught exceptions are encapsulated inside the `Deferred` object and will not be thrown until `await()` is invoked. If the caller never calls `await()`, the exception could be silently dropped.\n\n"
            "However, within structured concurrency (like inside `coroutineScope { }`), `async` failures behave differently: the moment an `async` child fails, its uncaught exception cancels its parent and all sibling coroutines immediately, regardless of whether `await()` was called.\n\n"
            "From a performance perspective, `async` allocates both a `DeferredCoroutine` and a result completion object in the heap. Therefore, using `async` purely to trigger a side effect without needing a return value wastes memory; `launch` is always the leaner and more idiomatic choice for non-returning tasks."
        ),
        "follow_ups": [
            {
                "interviewer": "What happens if an `async` coroutine fails and you wrap `deferred.await()` in a `try-catch`?",
                "answer": "If you are inside a standard `coroutineScope`, wrapping `deferred.await()` in `try-catch` catches the exception locally at the call site, but the parent `coroutineScope` has already been cancelled by the failure of the child! To catch child exceptions locally without cancelling siblings, you must use `supervisorScope`."
            },
            {
                "interviewer": "Can you await multiple Deferred instances concurrently?",
                "answer": "Yes, using the `awaitAll()` extension function on a collection of Deferreds (e.g., `listOf(task1, task2).awaitAll()`). It awaits all results concurrently and returns a `List<T>`, failing fast if any of the tasks throw an exception."
            },
            {
                "interviewer": "What is `CoroutineStart.LAZY` and how does it affect `async`?",
                "answer": "By default, `async` starts executing immediately. When started with `CoroutineStart.LAZY`, the coroutine does not start executing until you either explicitly call `deferred.start()` or call `deferred.await()`. Calling `await()` on two lazy async blocks sequentially will run them sequentially rather than in parallel."
            }
        ]
    },
    {
        "id": "COR-06",
        "arabic_explanation": (
            "المقارنة بين `viewModelScope` و `lifecycleScope` والـ Custom Application Scopes هي جوهر إدارة الـ Lifecycles في Android الحديث:\n\n"
            "1. الـ `viewModelScope`:\n"
            "   - مربوط بدورة حياة الـ **ViewModel**.\n"
            "   - بينشأ تلقائياً مع الـ ViewModel، وبيتم إلغاؤه تلقائياً في `onCleared()` لما الـ ViewModel ينتهي تماماً.\n"
            "   - **ميزة جوهرية:** بيعيش ويفضل شغال عبر الـ **Configuration Changes** (زي تدوير الشاشة من Portrait لـ Landscape). لو عملية تحميل شغالة في `viewModelScope` والمستخدم دور الشاشة، العملية مش هتتلغي ولا هتبدأ من الأول!\n"
            "   - ده المكان الطبيعي لـ 90% من Business Operations والـ Data Fetching الخاصة بالـ UI.\n\n"
            "2. الـ `lifecycleScope`:\n"
            "   - مربوط بدورة حياة **Activity أو Fragment أو Composable**.\n"
            "   - بيتم إلغاؤه فوراً بمجرد تدمير الـ Activity (`onDestroy`).\n"
            "   - بيموت مع الـ Configuration Change! لو بدأت عملية تحميل فيه ودورت الشاشة، العملية هتتلغي وتضيع.\n"
            "   - مخصص فقط للأشياء المرتبطة مباشرة بالـ UI View، زي تشغيل Navigation Animation أو التعامل مع Dialogs.\n\n"
            "3. الـ Custom Application-Level Scope:\n"
            "   - نطاق مخصص مربوط بدورة حياة **التطبيق ككل (Application Process)**.\n"
            "   - بننشئه بـ `CoroutineScope(SupervisorJob() + Dispatchers.Default)` داخل Application class أو كـ Singleton في Hilt.\n"
            "   - بيستخدم للعمليات الحرجة التي **يجب ألا تضيع حتى لو المستخدم قفل الشاشة فوراً**، زي: حفظ مسودة الطلب في Database، إرسال إحصائيات الدفع، أو مزامنة التوكن."
        ),
        "practical_walkthrough": (
            "سيناريو عملي يوضح الفروق بدقة:\n"
            "1. **المستخدم بيكتب تعليق ويضغط 'إرسال':**\n"
            "   - حفظ التعليق في قاعدة البيانات المحلية: نستخدم **ApplicationScope**، حتى لو المستخدم خرج من التطبيق فوراً بعد الضغط، التعليق يتسجل وميضيعش.\n"
            "2. **تحميل تفاصيل المنشور والصور:**\n"
            "   - نستخدم **viewModelScope**، لأننا لو دورنا الشاشة، العملية تفضل مستمرة وتعرض النتيجة للـ ViewModel بدون تكرار الطلب.\n"
            "3. **عرض Tooltip إرشادي يختفي بعد 3 ثوانٍ:**\n"
            "   - نستخدم **lifecycleScope**، لأن لو الشاشة اتقفلت أو دورنا الجهاز، الـ Tooltip القديم والـ View انتهت ومش عايزين نحدث View ميتة."
        ),
        "quick_answer": "viewModelScope is bound to ViewModel lifecycle and survives configuration changes, making it ideal for business logic and UI data loading; lifecycleScope is bound to Activity/Fragment view lifecycles and cancels on onDestroy/rotation, suited for view-only animations; and custom application scopes survive screen teardowns for critical persistence operations.",
        "best_answer": (
            "Choosing the right coroutine scope in Android comes down to matching the task's longevity with the component's architectural lifecycle.\n\n"
            "**viewModelScope** is tied to the ViewModel's lifecycle. Its critical strength is that it survives configuration changes like screen rotations. It automatically cancels its work only when the ViewModel is permanently cleared in `onCleared()`. This makes it the primary default for feature business logic, repository interactions, and UI data loading.\n\n"
            "**lifecycleScope** is tied directly to an Activity or Fragment's LifecycleOwner. It is cancelled immediately when the view is destroyed in `onDestroy()`. Because configuration changes destroy the view, tasks launched in `lifecycleScope` are cancelled upon rotation. It should strictly be reserved for view-specific operations, such as UI animations or view-binding interactions.\n\n"
            "**Custom application-level scopes** are singletons tied to the `Application` process lifecycle, typically injected via Hilt using `SupervisorJob()`. We use this for critical, fire-and-forget operations that must not be interrupted when a user navigates away, such as syncing an offline order to Room or logging a critical payment transaction."
        ),
        "deep_answer": (
            "From an architectural governance standpoint, misusing scopes causes severe production bugs. "
            "If developers launch network requests in `lifecycleScope`, rotating the phone terminates the coroutine midway, wasting bandwidth and requiring a fresh network call on recreation. Conversely, if developers launch view-modifying operations inside a custom application scope, it creates hard memory leaks by capturing View or Activity references in closures, preventing garbage collection.\n\n"
            "When designing an application-level scope for Hilt/Dagger: "
            "```kotlin\n"
            "@Provides\n"
            "@Singleton\n"
            "@ApplicationScope\n"
            "fun provideAppScope(): CoroutineScope = CoroutineScope(SupervisorJob() + Dispatchers.Default)\n"
            "```\n"
            "Notice the explicit use of `SupervisorJob()`: if a routine fails with an uncaught exception, `SupervisorJob` ensures that other unrelated background jobs running in the application scope are not cancelled. "
            "Finally, for long-running background tasks that must survive process death or device reboots—like uploading heavy media—neither of these scopes is sufficient; those require WorkManager."
        ),
        "follow_ups": [
            {
                "interviewer": "Why not use `repeatOnLifecycle` inside `viewModelScope`?",
                "answer": "`repeatOnLifecycle` is an extension function designed for `LifecycleOwner` (Activities, Fragments, Composables) to collect UI flows safely while the UI is at least in a given state (e.g., STARTED) and pause collection when in the background. The ViewModel has no UI lifecycle state, so flow collection in the UI layer belongs in `lifecycleScope.launch { repeatOnLifecycle(...) }`."
            },
            {
                "interviewer": "What happens to a coroutine in `viewModelScope` if the Android OS kills the app process due to low memory?",
                "answer": "Process death terminates the entire OS Linux process instantly. Neither `onCleared()` nor coroutine cancellation hooks run. State that must survive process death must be saved using `SavedStateHandle` or persisted to disk."
            },
            {
                "interviewer": "Can you use `viewModelScope` inside a Jetpack Compose Composable?",
                "answer": "You can access the ViewModel instance and invoke its methods which use `viewModelScope` internally. However, for launching coroutines directly within the Composable itself, you should use `rememberCoroutineScope()`, which cancels when the Composable leaves composition."
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

    for q in COR_01_06:
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
    print(f"Updated {DATA_FILE} with questions COR-01 to COR-06. Total questions: {len(combined)}")


if __name__ == "__main__":
    main()
