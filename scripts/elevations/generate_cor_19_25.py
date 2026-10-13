#!/usr/bin/env python3
"""Generator for COR-19 through COR-25 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "cor.json"

COR_19_25 = [
    {
        "id": "COR-19",
        "arabic_explanation": (
            "المغالطة الشائعة بأن الـ Coroutines 'Thread-Safe تلقائياً' هي سبب كارثي في أخطاء التزامن (Concurrency Bugs):\n\n"
            "1. ما هو الـ Race Condition؟\n"
            "   - هو حالة تحدث عندما تحاول عمليتان أو أكثر قراءة وتعديل متغير مشترك (Shared Mutable State) في نفس الوقت، وتعتمد النتيجة النهائية على توقيت الوصول (Timing / Scheduling).\n"
            "   - مثال: عمليتان تحاولان زيادة عداد `count++`. العملية تتكون من 3 خطوات في المعالج: قراءة القيمة، زيادتها، ثم حفظها. لو حدثت العمليتان بالتوازي، سيتم فقدان إحدى الزيادات وتصبح النتيجة خاطئة!\n\n"
            "2. لماذا الـ Coroutines ليست Thread-Safe تلقائياً؟\n"
            "   - الـ Coroutines تعمل على **Thread Pools** متعددة الخيوط (زي `Dispatchers.Default` و `Dispatchers.IO`).\n"
            "   - لو أطلقت 100 coroutine وكل واحدة بتعدل في متغير عادي أو `ArrayList` مشترك، الـ Coroutines دي هتتنفذ على خيوط حقيقية متوازية في المعالج، وهيحصل Race Condition وتلف للبيانات أو `ConcurrentModificationException` تماماً مثل الـ Threads العادية!\n"
            "   - الـ Coroutines تسهل كتابة الكود غير المتزامن، لكنها **لا تلغي قوانين الذاكرة وتزامن البيانات المشتركة (Shared State)**."
        ),
        "practical_walkthrough": (
            "تطبيق حساب بنكي ومحفظة إلكترونية:\n"
            "- عمليتان متزامنتان للإيداع بـ 100 جنيه لكل عملية:\n"
            "```kotlin\n"
            "// ❌ كود كارثي فيه Race Condition خطير:\n"
            "var balance = 0\n"
            "coroutineScope {\n"
            "    repeat(1000) {\n"
            "        launch(Dispatchers.Default) {\n"
            "            balance++ // غير متزامن! في النهاية balance سيكون 920 أو 850 بدلاً من 1000!\n"
            "        }\n"
            "    }\n"
            "}\n"
            "\n"
            "// ✅ الحل باستخدام AtomicInteger أو Mutex:\n"
            "val atomicBalance = AtomicInteger(0)\n"
            "coroutineScope {\n"
            "    repeat(1000) {\n"
            "        launch(Dispatchers.Default) {\n"
            "            atomicBalance.incrementAndGet() // عملية ذرية Hardware-level آمنة 100%\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "A race condition occurs when concurrent tasks read and modify shared mutable state without synchronization, yielding corrupted results. Coroutines are not automatically thread-safe because they execute across multi-threaded dispatcher pools (like Default and IO); accessing shared mutable state concurrently causes identical data races and memory corruption as traditional threads.",
        "best_answer": (
            "A race condition happens when multiple concurrent execution paths access and mutate shared state without coordination, producing non-deterministic bugs that depend on thread execution timing.\n\n"
            "A frequent misconception is that switching from Java threads to Kotlin coroutines magically makes code thread-safe. It does not. Coroutines dispatched on `Dispatchers.Default` or `Dispatchers.IO` execute on underlying multi-threaded worker pools. If two coroutines simultaneously read, increment, and write back a shared variable like `counter++`, CPU thread switching causes lost updates.\n\n"
            "Furthermore, standard Java collections like `ArrayList` or `HashMap` have no internal synchronization; concurrent coroutine writes will corrupt their internal arrays and throw `ConcurrentModificationException`.\n\n"
            "To prevent race conditions, we must synchronize access using techniques suited for coroutines: thread confinement, atomic primitives, Kotlin's non-blocking `Mutex`, or immutable state flows."
        ),
        "deep_answer": (
            "At the hardware and memory architecture level, modern multicore processors use private L1 and L2 caches. Without memory synchronization barriers, writes performed by a coroutine on Core A may remain in Core A's store buffer and not be visible to Core B executing another coroutine. This violates the Java Memory Model's (JMM) 'happens-before' guarantee.\n\n"
            "When dealing with suspension points, race conditions can become even more insidious: a coroutine might read a shared balance, suspend across a network call, and then write back the balance. During the suspension window, another coroutine could have modified the balance multiple times, causing a classic Time-of-Check to Time-of-Use (TOCTOU) race condition.\n\n"
            "In modern Android MVI/Unidirectional Data Flow architectures, the ultimate cure for race conditions is eliminating shared mutable state entirely: we confine state mutation to a single coroutine dispatcher or use atomic compare-and-swap loops inside `MutableStateFlow.update { current -> current.copy(...) }`."
        ),
        "follow_ups": [
            {
                "interviewer": "Does running coroutines on `Dispatchers.Main` protect you from race conditions?",
                "answer": "Yes for purely synchronous code, because all execution is confined to the single main thread. However, if a coroutine suspends (e.g., across `delay` or network call), another event can run on the main thread during that suspension window and mutate the state, still producing a logical race condition."
            },
            {
                "interviewer": "Why is `volatile` not enough to fix `counter++`?",
                "answer": "`volatile` only guarantees memory visibility (that all threads read the latest value directly from main memory); it does not guarantee atomicity. The `++` operation is three separate instructions (read, increment, write). If two threads read simultaneously, one increment will overwrite the other."
            },
            {
                "interviewer": "What is the best way to handle shared mutable state in a ViewModel?",
                "answer": "Use `MutableStateFlow` with immutable data classes and update state via `_state.update { current -> ... }`, which performs atomic, non-blocking updates using atomic compare-and-set loops."
            }
        ]
    },
    {
        "id": "COR-20",
        "arabic_explanation": (
            "المقارنة بين وسائل حماية البيانات المشتركة في Kotlin Coroutines:\n\n"
            "1. الـ `Mutex` (Kotlin Coroutines Mutex):\n"
            "   - هو **Non-blocking (Suspending) Lock**.\n"
            "   - لما coroutine تحاول تدخل كود محمي بـ `mutex.withLock` ويكون محجوزاً، الـ Coroutine **تُعلّق (Suspends)** وتترك الـ OS Thread حراً لينفذ مهام أخرى!\n"
            "   - مخصص حصرياً لبيئة الـ Coroutines لحماية العمليات المعقدة والـ Suspend functions.\n\n"
            "2. الـ `synchronized` (Java Monitors):\n"
            "   - **Blocking Lock** على مستوى نظام التشغيل والـ JVM.\n"
            "   - يحظر خيط المعالجة بالكامل (Blocks OS Thread).\n"
            "   - **تحذير صارم:** لا يمكن استخدامه حول Suspend functions! ولا يجب استخدامه داخل Coroutines لأنه يستهلك الـ Threads ويسبب تجويع الـ Thread Pool و ANR.\n\n"
            "3. الـ Atomic Types (`AtomicInteger`, `AtomicReference`):\n"
            "   - مبنية على تعليمات الـ CPU المباشرة: **Compare-And-Swap (CAS)**.\n"
            "   - أسرع وسيلة على الإطلاق (Lock-free و Zero-overhead) للعمليات البسيطة (زي العدادات وتحديث المراجع الفردية).\n"
            "   - لا تناسب العمليات المعقدة متعددة الخطوات.\n\n"
            "4. الـ Thread Confinement (الحصر على خيط واحد):\n"
            "   - حصر جميع عمليات التعديل على Thread واحد محدد (زي `Dispatchers.Main` أو `Dispatchers.Default.limitedParallelism(1)`).\n"
            "   - بسيط جداً ويمنع الحاجة لأي Locks، لكنه قد يكون عنق زجاجة لو العمليات ثقيلة جداً."
        ),
        "practical_walkthrough": (
            "مقارنة عملية لاختيار الأداة المناسبة:\n"
            "1. **عداد مرات النقر (Simple Counter):**\n"
            "   - الأفضل: `private val clickCount = AtomicInteger(0)` -> `clickCount.incrementAndGet()` (أسرع بنية).\n"
            "2. **قراءة ملف، تحديث التوكن، ثم حفظه في قاعدة البيانات (Suspending critical section):**\n"
            "   - الأفضل: `private val mutex = Mutex()` -> `mutex.withLock { refreshToken() }` (يعلق بدون حظر خيوط).\n"
            "3. **إدارة حالة الـ UI في الـ MVI ViewModel:**\n"
            "   - الأفضل: `Thread Confinement` على Main Thread أو استخدام `MutableStateFlow.update { }`."
        ),
        "quick_answer": "Mutex is a non-blocking, suspension-aware lock designed for coroutines; synchronized is a thread-blocking Java monitor that must never be used with suspending functions; Atomic types use hardware-level compare-and-swap (CAS) for lock-free primitive updates; and Confinement confines state mutation to a single thread/dispatcher, eliminating locks entirely.",
        "best_answer": (
            "Choosing the right synchronization tool depends on whether the critical section suspends, how long it runs, and the complexity of the shared state.\n\n"
            "**Mutex** is Kotlin's suspension-aware mutual exclusion lock. When a coroutine waits for a locked Mutex via `mutex.withLock`, it suspends without blocking the underlying OS thread, keeping worker pools responsive. It is the only choice when protecting a critical section that contains suspending calls.\n\n"
            "**synchronized** is Java's traditional monitor lock. It forcibly blocks the operating system thread. You cannot call suspending functions inside a synchronized block, and using it in coroutines is an anti-pattern because it starves thread pools and can cause ANRs.\n\n"
            "**Atomic types** (AtomicInteger, AtomicReference) provide lock-free, ultra-fast synchronization for single variables via CPU Compare-And-Swap (CAS) instructions, with zero lock contention overhead.\n\n"
            "**Thread Confinement** confines all mutations to a single dispatcher (such as `Dispatchers.Main` or `Dispatchers.Default.limitedParallelism(1)`), eliminating the need for locks altogether through structural design."
        ),
        "deep_answer": (
            "At the performance and scheduling layer, each approach presents different trade-offs: "
            "`AtomicInteger` has zero suspension and zero lock overhead; it is resolved directly in CPU registers via cache coherency protocols (MESI). "
            "However, CAS loops can experience spinning overhead under extreme contention.\n\n"
            "`Mutex` involves internal queue management (`LockContender` nodes on the heap). While non-blocking, acquiring and releasing a Mutex is significantly more expensive in CPU instructions than an atomic CAS. Therefore, you should never use a Mutex for a simple primitive increment.\n\n"
            "With Thread Confinement using `limitedParallelism(1)`, Kotlin creates an exclusive sequential queue on top of the shared pool. It provides the simplicity of single-threaded programming without locking, but context switching across dispatchers via `withContext(singleThreadDispatcher)` incurs dispatch latency. "
            "In Android architecture, combining `AtomicReference` or `StateFlow.update` with immutable data structures offers the cleanest and most performant state synchronization."
        ),
        "follow_ups": [
            {
                "interviewer": "Why does the Kotlin compiler forbid calling suspend functions inside a `synchronized` block?",
                "answer": "Because Java synchronized blocks bind a lock to the executing OS thread. If a coroutine suspended inside synchronized, it would yield the thread while retaining the monitor lock, creating immediate deadlocks and thread starvation across the runtime."
            },
            {
                "interviewer": "Is Kotlin's `Mutex` re-entrant?",
                "answer": "No! Kotlin's standard `Mutex` is non-reentrant. If a coroutine that already holds a Mutex attempts to acquire it again (e.g., in a nested function call), it will suspend and deadlock itself indefinitely."
            },
            {
                "interviewer": "How does `Dispatchers.Default.limitedParallelism(1)` compare to a single-threaded executor?",
                "answer": "A traditional single-threaded executor allocates a dedicated OS thread permanently. `limitedParallelism(1)` shares the general worker pool and ensures that at most one coroutine executes at any time, eliminating the overhead of keeping a dedicated thread alive."
            }
        ]
    },
    {
        "id": "COR-21",
        "arabic_explanation": (
            "الـ `Semaphore` في Kotlin Coroutines هو أداة للتحكم في عدد العمليات المتزامنة وتحديد سقف التوازي (Concurrency Throttling):\n\n"
            "1. ما هو الـ Semaphore؟\n"
            "   - هو عداد تصاريح (Permit Counter) معلق.\n"
            "   - يسمح لعدد محدد فقط من الـ Coroutines بالدخول في نفس الوقت (مثلاً: 3 coroutines فقط بالتوازي).\n"
            "   - أي Coroutine إضافية تحاول الدخول **تُعلّق (Suspends)** بدون حظر الـ Thread، حتى تفرغ إحدى العمليات الحالية وتطلق التصريح (`release()`).\n\n"
            "2. ما الفرق بين الـ Mutex والـ Semaphore؟\n"
            "   - الـ `Mutex` هو حالة خاصة من الـ Semaphore بتصريح واحد فقط (`permits = 1`)، ويضمن الاستبعاد المتبادل الحصري (Mutual Exclusion).\n"
            "   - الـ `Semaphore` يسمح بـ N تصاريح (`permits = N`) لتحديد سقف التوازي.\n\n"
            "3. متى نستخدمه في Android الإنتاجي؟\n"
            "   - **رفع ملفات وصور متعددة بالتوازي:** لو المستخدم بيختار 50 صورة لرفعها، لا نريد إطلاق 50 طلب شبكة في نفس اللحظة لإرهاق الـ Socket والـ Bandwidth؛ نستخدم Semaphore بـ 3 تصاريح.\n"
            "   - **تحديد استهلاك الـ Memory والـ CPU** في معالجة الـ Bitmaps."
        ),
        "practical_walkthrough": (
            "في شاشة رفع ألبوم صور (Batch Image Uploader):\n"
            "```kotlin\n"
            "class ImageUploadRepository(private val api: MediaApi) {\n"
            "    // نحدد الحد الأقصى للرفع المتزامن بـ 3 صور فقط:\n"
            "    private val uploadSemaphore = Semaphore(permits = 3)\n"
            "\n"
            "    suspend fun uploadAllImages(images: List<File>): List<UploadResult> = coroutineScope {\n"
            "        images.map { imageFile ->\n"
            "            async(Dispatchers.IO) {\n"
            "                // acquire تصريح، وتنفيذ الرفع، ثم تحرير التصريح تلقائياً عبر withPermit:\n"
            "                uploadSemaphore.withPermit {\n"
            "                    api.uploadImage(imageFile)\n"
            "                }\n"
            "            }\n"
            "        }.awaitAll()\n"
            "    }\n"
            "}\n"
            "```\n"
            "النتيجة: يتم رفع الـ 50 صورة بالكامل، ولكن بحد أقصى 3 صور في نفس اللحظة بسلاسة تامة وبدون خنق لشبكة الجهاز."
        ),
        "quick_answer": "A Semaphore limits concurrency by maintaining a pool of permits. Coroutines acquire a permit before entering a critical block and release it when done; if no permits are available, incoming coroutines suspend without blocking their threads until a permit is freed.",
        "best_answer": (
            "A `Semaphore` controls concurrent access to a resource by maintaining a set of available permits. It is the primary tool for concurrency throttling in Kotlin Coroutines.\n\n"
            "When a coroutine invokes `semaphore.withPermit { ... }`, it attempts to acquire a permit. If permits are available, the permit count decrements and the coroutine proceeds immediately. If all permits are exhausted, subsequent coroutines suspend non-blockingly until an active coroutine finishes and releases its permit.\n\n"
            "I use Semaphores in Android whenever I need to bound parallel resource consumption—such as limiting concurrent media uploads to 3 at a time, restricting simultaneous image decodes to avoid memory spikes, or capping database write connections. It prevents thread starvation, network congestion, and out-of-memory crashes."
        ),
        "deep_answer": (
            "Internally, Kotlin's `Semaphore` is implemented as a lock-free segment-based queue of continuations. When permits reach zero, callers are suspended and their continuations are enqueued onto a lock-free linked list. When a permit is released, the head continuation is resumed and dispatched to its coroutine dispatcher.\n\n"
            "In modern Kotlin (1.6+), you can also limit parallelism at the dispatcher level using `dispatcher.limitedParallelism(N)`. "
            "How do they compare? "
            "`limitedParallelism(N)` creates a new Dispatcher view that constrains execution to N threads, which limits CPU/thread allocation. "
            "`Semaphore(N)` controls logical permit access regardless of which dispatcher is running the work. For example, if you want tasks to run on the broad `Dispatchers.IO` pool (scaling up to 64 threads) but want strictly 4 concurrent network uploads to an API, `Semaphore(4)` is the right abstraction."
        ),
        "follow_ups": [
            {
                "interviewer": "What happens if a coroutine holding a Semaphore permit is cancelled?",
                "answer": "When using `semaphore.withPermit`, the release is wrapped in a `try-finally` block. If the coroutine is cancelled while holding the permit, the `finally` block executes and releases the permit automatically, preventing permit leaks."
            },
            {
                "interviewer": "Can a Semaphore be initialized with 1 permit?",
                "answer": "Yes. A Semaphore with 1 permit behaves conceptually like a Mutex, but `Mutex` is preferred for single-permit mutual exclusion because it provides clearer ownership semantics and dedicated locking helpers."
            },
            {
                "interviewer": "How does Semaphore compare to Java's `java.util.concurrent.Semaphore`?",
                "answer": "Java's Semaphore blocks the OS thread when `acquire()` is called without permits. Kotlin's `kotlinx.coroutines.sync.Semaphore` is non-blocking: its `acquire()` is a suspending function that frees the underlying thread."
            }
        ]
    },
    {
        "id": "COR-22",
        "arabic_explanation": (
            "استخدام `ensureActive()` و `yield()` أثناء العمليات المكثفة على المعالج (CPU-Bound Work) ضروري لضمان التعاونية وعدم تجويع العمليات الأخرى:\n\n"
            "1. المشكلة في الـ CPU-Bound Loops:\n"
            "   - لما coroutine تنفذ كود حسابي مكثف (زي تشفير، معالجة صور، أو فحص مصفوفات ضخمة)، الكود لا يحتوي على أي دالة تعليق (`suspend`).\n"
            "   - لو تم استدعاء `job.cancel()`، الـ Coroutine **لن تتوقف أبداً** وهتفضل شغالة وتستهلك البطارية!\n"
            "   - وأيضاً لو الـ Dispatcher Pool فيه عدد threads محدود، الـ Loop دي هتحجز الـ Thread بالكامل وتمنع باقي الـ Coroutines من التنفيذ (Starvation).\n\n"
            "2. دور دالة `ensureActive()`:\n"
            "   - بتفحص: هل الـ Job الحالي تم إلغاؤه؟\n"
            "   - لو تم إلغاؤه: ترمي `CancellationException` فوراً وتنهي التنفيذ.\n"
            "   - لو لم يتم إلغاؤه: تكمل التنفيذ بدون أي تبديل خيوط وبدون أي تأخير (Zero overhead).\n\n"
            "3. دور دالة `yield()`:\n"
            "   - بتفحص الإلغاء وترمي `CancellationException` تماماً مثل `ensureActive()`.\n"
            "   - **الإضافة الجوهرية في `yield()`:** تقوم بتعليق الـ Coroutine مؤقتاً وتضعها في نهاية طابور الـ Dispatcher، وتمنح فرصة للـ Coroutines الأخرى في نفس الـ Pool أن تتنفس وتتنفذ (Fair Scheduling)!\n\n"
            "4. متى نستخدم كل واحدة منهما؟\n"
            "   - استخدم `ensureActive()` لو الـ Loop سريعة والمطلوب فقط فحص الإلغاء بأعلى سرعة.\n"
            "   - استخدم `yield()` لو الـ Loop ثقيلة جداً وتريد إعطاء فرصة لباقي المهام في الـ Thread Pool حتى لا تتجمد."
        ),
        "practical_walkthrough": (
            "في دالة توليد صورة مصغرة (Thumbnail Processing Loop):\n"
            "```kotlin\n"
            "suspend fun processLargeDataSet(records: List<RawRecord>) = withContext(Dispatchers.Default) {\n"
            "    val results = mutableListOf<ProcessedRecord>()\n"
            "    for ((index, record) in records.withIndex()) {\n"
            "        // 1. فحص الإلغاء في كل لفة:\n"
            "        ensureActive()\n"
            "        \n"
            "        // 2. كل 100 لفة نمنح فرصة للمهام الأخرى عبر yield:\n"
            "        if (index % 100 == 0) {\n"
            "            yield()\n"
            "        }\n"
            "        \n"
            "        results.add(transformRecord(record))\n"
            "    }\n"
            "    results\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Use ensureActive() to verify cancellation and throw CancellationException immediately with zero scheduling overhead. Use yield() to both check for cancellation and yield the current thread to other waiting coroutines in the dispatcher queue, ensuring fair scheduling during heavy CPU tasks.",
        "best_answer": (
            "During intensive CPU-bound calculations, coroutines do not hit natural suspension points like network calls or delays. This causes two production problems: they ignore cancellation, and they monopolize worker threads in the dispatcher pool.\n\n"
            "I use `ensureActive()` when I strictly want cancellation responsiveness with maximum performance. It checks the Job's active state and immediately throws `CancellationException` if the job was cancelled. If the job is active, it does nothing and has zero dispatching or scheduling overhead.\n\n"
            "I use `yield()` when a CPU-bound task is heavy and I want fair scheduling. `yield()` checks for cancellation just like `ensureActive()`, but if active, it suspends the coroutine and dispatches it to the back of the dispatcher's work queue. This temporarily releases the OS thread so other waiting coroutines on the same dispatcher can execute, preventing thread starvation."
        ),
        "deep_answer": (
            "Under the hood, `ensureActive()` is an inline extension function on `CoroutineScope` and `Job` that executes:\n\n"
            "```kotlin\n"
            "if (!isActive) throw getCancellationException()\n"
            "```\n\n"
            "Because it is inlined, it compiles directly to a simple conditional jump in bytecode without creating any continuation frames or dispatch objects.\n\n"
            "`yield()`, by contrast, is a true suspending function. It captures the current `Continuation` and dispatches it via `dispatcher.dispatchYield()`. If the dispatcher's event queue is empty, the runtime immediately reschedules and resumes the coroutine on the same thread with minimal latency. If other tasks are enqueued, they execute first.\n\n"
            "In high-frequency loops (e.g., iterating 100,000 times), calling `yield()` on every single iteration causes excessive scheduling overhead and degrades throughput. The senior engineering pattern is batching: call `ensureActive()` on every iteration, and throttle `yield()` to once every 100 or 500 iterations."
        ),
        "follow_ups": [
            {
                "interviewer": "Can `yield()` be called on `Dispatchers.Unconfined`?",
                "answer": "Calling `yield()` on `Dispatchers.Unconfined` still yields execution, but because Unconfined has no thread queue, it might resume on whichever thread triggered the yield, which can lead to unpredictable stack depths."
            },
            {
                "interviewer": "Why not just use `delay(1)` instead of `yield()`?",
                "answer": "`delay(1)` forces the coroutine to pause for at least 1 millisecond by scheduling a timer event. `yield()` introduces zero artificial sleep delay; if no other coroutines are waiting, it resumes immediately without waiting."
            },
            {
                "interviewer": "What is the difference between `Thread.yield()` and Coroutines `yield()`?",
                "answer": "`Thread.yield()` is an OS-level hint to the thread scheduler to yield the current CPU quantum. Coroutines `yield()` is a cooperative user-space suspension that yields the worker thread to other coroutines in the Kotlin dispatcher queue."
            }
        ]
    },
    {
        "id": "COR-23",
        "arabic_explanation": (
            "تحويل الـ Callback APIs القديمة في Android إلى Suspending Functions هو أحد أهم الاختبارات العملية في المقابلات:\n\n"
            "1. الأداة المعيارية: `suspendCancellableCoroutine`:\n"
            "   - تُعلق الـ Coroutine وتوفر كائن `CancellableContinuation<T>`.\n"
            "   - لما الـ Callback ينجح: ننادي `continuation.resume(result)`.\n"
            "   - لما الـ Callback يفشل: ننادي `continuation.resumeWithException(error)`.\n\n"
            "2. أهمية التعامل مع الإلغاء (`invokeOnCancellation`):\n"
            "   - لو المتصل لغى الـ Coroutine قبل ما الـ Callback يرجع، لازم نلغي الـ Listener أو الطلب في الـ SDK الخارجي عبر `continuation.invokeOnCancellation { ... }` لمنع تسريب الذاكرة (Memory Leak) واستمرار العمليات في الخلفية.\n\n"
            "3. تحذير خطير: تجنب `suspendCoroutine` العادية:\n"
            "   - دالة `suspendCoroutine` (بدون Cancellable) لا تدعم الإلغاء! لو تم إلغاء الـ Coroutine، ستظل معلقة حتى ينتهي الـ Callback، مما يكسر مبدأ الـ Structured Concurrency."
        ),
        "practical_walkthrough": (
            "تحويل Firebase أو Location Manager Callback لـ Suspend Function:\n"
            "```kotlin\n"
            "suspend fun FusedLocationProviderClient.awaitCurrentLocation(): Location =\n"
            "    suspendCancellableCoroutine { continuation ->\n"
            "        val cancellationSource = CancellationTokenSource()\n"
            "        \n"
            "        // 1. طلب الموقع من Google Play Services:\n"
            "        getCurrentLocation(Priority.PRIORITY_HIGH_ACCURACY, cancellationSource.token)\n"
            "            .addOnSuccessListener { location ->\n"
            "                continuation.resume(location)\n"
            "            }\n"
            "            .addOnFailureListener { exception ->\n"
            "                continuation.resumeWithException(exception)\n"
            "            }\n"
            "            \n"
            "        // 2. الربط مع إلغاء الـ Coroutine لمنع تسريب الـ GPS:\n"
            "        continuation.invokeOnCancellation {\n"
            "            cancellationSource.cancel()\n"
            "        }\n"
            "    }\n"
            "```"
        ),
        "quick_answer": "Use suspendCancellableCoroutine to convert callbacks into suspending functions. Resume with continuation.resume() on success, continuation.resumeWithException() on error, and crucially register continuation.invokeOnCancellation to unregister listeners and abort external tasks when cancelled.",
        "best_answer": (
            "To adapt asynchronous callback APIs into idiomatic suspending functions, I always use `suspendCancellableCoroutine`.\n\n"
            "It suspends the coroutine and provides a `CancellableContinuation<T>` handle. Inside the callback listener: on success, I call `continuation.resume(data)`; on failure, I call `continuation.resumeWithException(throwable)`.\n\n"
            "The critical architectural step that separates senior engineers from juniors is handling cancellation: you must invoke `continuation.invokeOnCancellation { ... }` to detach the callback listener or signal cancellation to the underlying SDK. Without this, if the calling coroutine is cancelled, the underlying third-party listener remains registered, leaking memory and leaving network or location hardware active.\n\n"
            "Never use the older `suspendCoroutine` builder because it cannot respond to coroutine cancellation."
        ),
        "deep_answer": (
            "Under the hood, `suspendCancellableCoroutine` provides strict safety guarantees regarding resume calls. A continuation can only be resumed once. If a third-party SDK accidentally triggers both a success and an error callback, or triggers a callback after cancellation, `CancellableContinuation` guards against illegal multi-resumes by ignoring or throwing an IllegalStateException.\n\n"
            "For streaming callback APIs that deliver multiple events over time (such as GPS location updates or WebSocket messages), adapting them to a single suspending function is an anti-pattern. Instead, stream APIs must be adapted to Kotlin Flow using `callbackFlow { }`:\n\n"
            "```kotlin\n"
            "fun observeLocation(): Flow<Location> = callbackFlow {\n"
            "    val listener = LocationListener { location -> trySend(location) }\n"
            "    client.register(listener)\n"
            "    awaitClose { client.unregister(listener) }\n"
            "}\n"
            "```\n\n"
            "`callbackFlow` uses `awaitClose` to guarantee listener cleanup when flow collection halts."
        ),
        "follow_ups": [
            {
                "interviewer": "What happens if a callback is invoked after the coroutine has already been cancelled?",
                "answer": "If the coroutine is cancelled, `CancellableContinuation` discards any subsequent `resume()` calls. If `resume()` provides an allocated resource that must be closed, you can use `continuation.resume(value) { value.close() }` to ensure resources are cleaned up if cancelled concurrently."
            },
            {
                "interviewer": "Why is `callbackFlow` preferred over `suspendCancellableCoroutine` for multiple values?",
                "answer": "A suspending function can only return a single value once. For streams emitting multiple values over time, `callbackFlow` provides an asynchronous cold stream backed by a Channel that buffers emissions and manages cleanup via `awaitClose`."
            },
            {
                "interviewer": "Can you call `continuation.resume()` from any thread?",
                "answer": "Yes. `CancellableContinuation.resume()` is thread-safe. When invoked, it automatically dispatches the resumption back to the coroutine's designated CoroutineDispatcher."
            }
        ]
    },
    {
        "id": "COR-24",
        "arabic_explanation": (
            "استخدام `GlobalScope` أو إنشاء CoroutineScope داخل دوال الـ Repository هو أحد أسوأ الـ Anti-Patterns التي تدمر الـ Architecture:\n\n"
            "1. مخاطر `GlobalScope`:\n"
            "   - هو نطاق غير مقيد (Unbound Scope) بدون أي أب شرعي، ويعيش طوال حياة التطبيق.\n"
            "   - **تسريب الموارد والذاكرة (Resource Leaks):** العمليات المطلقة فيه لا يمكن إلغاؤها عند مغادرة الشاشة؛ تظل تستهلك البطارية و RAM والشبكة في الخلفية.\n"
            "   - **فقدان الاستثناءات والـ Crashes:** الاستثناءات فيه لا تخضع للـ Structured Concurrency، وتؤدي إما لانهيار التطبيق أو ضياع الأخطاء بصمت.\n\n"
            "2. مخاطر إنشاء `CoroutineScope` داخل دوال الـ Repository:\n"
            "   - كتابة `fun fetch() { CoroutineScope(Dispatchers.IO).launch { ... } }`.\n"
            "   - **كسر دورة الحياة:** في كل مرة تنادي الدالة، يتم إنشاء Scope جديد منفصل تماماً ملوش أي علاقة بالـ ViewModel أو الـ UI.\n"
            "   - **مستحيل إلغاؤه (Uncancellable):** لو المستخدم خرج من الشاشة، الـ Repository هيفضل شغال ويجلب بيانات مفيش حد مستنيها!\n"
            "   - **كسر الـ Testing:** اختبارات الـ Unit Tests تفشل لأن الـ Scope الجديد يعمل على threads خارج سيطرة الـ TestDispatcher.\n\n"
            "3. النمط المعماري الصحيح (The Architecture Standard):\n"
            "   - دوال الـ Repository يجب أن تكون **`suspend fun` عادية** (تستقبل الـ Scope من المتصل) أو ترجع `Flow<T>`.\n"
            "   - الـ ViewModel هو المسؤول الوحيد عن إطلاق الـ Coroutines عبر `viewModelScope`."
        ),
        "practical_walkthrough": (
            "مقارنة بين التصميم السيئ والتصميم المعماري النظيف:\n"
            "```kotlin\n"
            "// ❌ تصميم كارثي في الـ Repository:\n"
            "class BadUserRepository {\n"
            "    fun updateUser(user: User) {\n"
            "        // كارثة: ينشئ scope مستقل غير مربوط بالـ lifecycle ولا يمكن إلغاؤه!\n"
            "        CoroutineScope(Dispatchers.IO).launch {\n"
            "            api.update(user)\n"
            "        }\n"
            "    }\n"
            "}\n"
            "\n"
            "// ✅ التصميم النظيف المتوافق مع Clean Architecture:\n"
            "class GoodUserRepository(private val api: Api, private val ioDispatcher: CoroutineDispatcher) {\n"
            "    // الدالة معلقة، Main-Safe، ومربوطة بنطاق المتصل:\n"
            "    suspend fun updateUser(user: User) = withContext(ioDispatcher) {\n"
            "        api.update(user)\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "GlobalScope and ad-hoc repository scopes destroy structured concurrency. They produce un-cancellable background tasks that leak memory, waste network bandwidth, bypass exception handling, and make deterministic unit testing impossible. Repositories should expose suspend functions or Flows, leaving lifecycle scoping to ViewModels.",
        "best_answer": (
            "Using `GlobalScope` or creating ad-hoc `CoroutineScope` instances inside repository methods completely breaks structured concurrency.\n\n"
            "When a repository creates its own scope (e.g., `CoroutineScope(Dispatchers.IO).launch`), that coroutine is detached from the calling ViewModel's lifecycle. If the user navigates away and the screen is destroyed, the ViewModel's `viewModelScope` cancels, but the repository coroutine keeps running in the background. This wastes CPU, leaks network bandwidth, and can trigger database race conditions.\n\n"
            "Furthermore, detached scopes swallow or misdirect exceptions, making centralized error handling impossible, and they break unit testing because test runners cannot wait for or control un-tracked scopes.\n\n"
            "In clean architecture, repositories should never launch coroutines. Repositories should expose **suspend functions** for one-shot operations (using `withContext` for main-safety) or **Flow** for streams. The ViewModel remains the sole owner of the lifecycle scope via `viewModelScope`."
        ),
        "deep_answer": (
            "From an architectural governance perspective, there is only one legitimate use case for a non-ViewModel scope in the data layer: operations that **must survive UI teardown** (like saving an offline transaction or uploading an analytics batch). "
            "However, even in that scenario, creating ad-hoc scopes inside methods is forbidden. "
            "Instead, we use an explicitly injected **ApplicationScope**:\n\n"
            "```kotlin\n"
            "class OrderRepository @Inject constructor(\n"
            "    @ApplicationScope private val externalScope: CoroutineScope,\n"
            "    private val api: OrderApi\n"
            ") {\n"
            "    suspend fun submitOrder(order: Order) {\n"
            "        externalScope.launch { api.submit(order) }.join()\n"
            "    }\n"
            "}\n"
            "```\n\n"
            "By injecting a singleton `ApplicationScope` bound to a `SupervisorJob`, the lifecycle is formally tracked by the DI container, exceptions are captured by a centralized handler, and unit tests can easily inject a `TestScope` to verify background completion."
        ),
        "follow_ups": [
            {
                "interviewer": "Why does `GlobalScope` prevent unit test determinism?",
                "answer": "Because `GlobalScope` runs on background JVM threads completely outside the `kotlinx-coroutines-test` test scheduler. Unit tests will finish and exit before the `GlobalScope` coroutine completes, causing false passes or intermittent race condition test failures."
            },
            {
                "interviewer": "When should work be offloaded to WorkManager instead of an ApplicationScope?",
                "answer": "Use ApplicationScope for short tasks that should survive screen navigation while the app process is alive (e.g., in-memory cache sync). Use WorkManager for persistent tasks that must survive app process death, low memory kills, or device reboots (e.g., large file uploads, sync jobs)."
            },
            {
                "interviewer": "What is the rule of thumb for repository API contracts?",
                "answer": "Repositories expose suspend functions for one-shot requests and Flow<T> for continuous observable streams. Repositories do not launch coroutines; they only execute inside the caller's coroutine."
            }
        ]
    },
    {
        "id": "COR-25",
        "arabic_explanation": (
            "استدعاء 3 APIs معتمدة على بعضها بالتوازي مع الإلغاء الفوري عند فشل أي منها (Fail-Fast with Sibling Cancellation) هو النمط الكلاسيكي للـ Structured Concurrency:\n\n"
            "1. المعمارية المطلوبة:\n"
            "   - نريد تشغيل 3 طلبات بالتوازي لتوفير الوقت.\n"
            "   - إذا فشل أي طلب، نريد **إلغاء الطلبين الآخرين فوراً** لمنع إهدار باقة وبيانات المستخدم.\n"
            "   - إرجاع خطأ موحد ومتسق للمتصل.\n\n"
            "2. الأداة المناسبة: `coroutineScope { }`:\n"
            "   - دالة `coroutineScope` هي الحل المثالي لأنها تستخدم **Standard Job**.\n"
            "   - بمجرد أن يفشل أي `async` child برمي Exception، يقوم `coroutineScope` بإلغاء جميع الـ `async` الآخرين فوراً، ويعيد رمي الاستثناء الأصلي للأعلى.\n\n"
            "3. ما الذي يجب تجنبه؟\n"
            "   - تجنب `supervisorScope` هنا، لأن `supervisorScope` يعزل الفشل ويترك باقي الطلبات تعمل حتى لو فشل أحدها!\n"
            "   - تجنب وضع `try-catch` حول كل `async.await()` داخل `coroutineScope` لأن ذلك قد يربك معالجة الأخطاء."
        ),
        "practical_walkthrough": (
            "تنفيذ عملي لحجز رحلة يتطلب حجز الطيران والفندق وتأجير السيارة معاً:\n"
            "```kotlin\n"
            "suspend fun bookPackage(userId: String): BookingConfirmation = coroutineScope {\n"
            "    // نطلق الـ 3 عمليات بالتوازي داخل coroutineScope:\n"
            "    val flightDeferred = async { flightApi.bookFlight(userId) }\n"
            "    val hotelDeferred = async { hotelApi.bookHotel(userId) }\n"
            "    val carDeferred = async { carApi.bookCar(userId) }\n"
            "    \n"
            "    // إذا فشل bookFlight مثلاً، coroutineScope سيلغي hotelDeferred و carDeferred فوراً!\n"
            "    BookingConfirmation(\n"
            "        flight = flightDeferred.await(),\n"
            "        hotel = hotelDeferred.await(),\n"
            "        car = carDeferred.await()\n"
            "    )\n"
            "}\n"
            "```\n"
            "في الـ ViewModel: نحيط استدعاء `bookPackage` بـ `try-catch` لمعالجة الخطأ الموحد وإظهار رسالة 'فشل حجز الباقة' للمستخدم."
        ),
        "quick_answer": "Use 'coroutineScope' with parallel 'async' tasks. Because coroutineScope uses a standard Job, if any child fails, it automatically cancels all active siblings immediately (fail-fast) and rethrows the failure, guaranteeing consistent transactional error handling without orphaned background requests.",
        "best_answer": (
            "To call 3 dependent APIs concurrently and ensure that the failure of any one immediately cancels the others, the standard architectural pattern is using `coroutineScope` combined with `async`.\n\n"
            "`coroutineScope` creates a structured child scope backed by a standard `Job`. Inside the block, we launch all three network requests in parallel using `async`. We then await all three results:\n\n"
            "```kotlin\n"
            "suspend fun fetchDashboardData(): DashboardData = coroutineScope {\n"
            "    val user = async { api.getUser() }\n"
            "    val config = async { api.getConfig() }\n"
            "    val feed = async { api.getFeed() }\n"
            "    DashboardData(user.await(), config.await(), feed.await())\n"
            "}\n"
            "```\n\n"
            "If `api.getUser()` fails with a NetworkException, structured concurrency guarantees that the failure propagates to `coroutineScope`. The scope cancels itself and immediately sends cancellation signals to `config` and `feed`, aborting their HTTP connections and rethrowing the initial exception to the caller."
        ),
        "deep_answer": (
            "Under the hood, when `user` throws an exception, it triggers `parent.childCancelled(cause)`. The parent `coroutineScope` transitions into the `CANCELLING` state and traverses its child list, invoking `child.cancel(CancellationException(cause))` on `config` and `feed`. "
            "If OkHttp or Ktor is used, the underlying HTTP socket connection is immediately closed and its read loop is interrupted.\n\n"
            "If one of the sibling coroutines also throws an exception while being cancelled, `coroutineScope` collects that secondary exception and adds it to the root cause via `Throwable.addSuppressed()`. This preserves full diagnostic logging in Crashlytics.\n\n"
            "Do NOT use `supervisorScope` for this use case: a supervisor scope would isolate the failure, allowing the remaining two calls to complete and waste bandwidth on a request that has already fundamentally failed."
        ),
        "follow_ups": [
            {
                "interviewer": "Why wouldn't you wrap each `await()` in a `try-catch` inside `coroutineScope`?",
                "answer": "Because in a standard `coroutineScope`, once an `async` child fails, the scope is ALREADY cancelled. Even if you catch the exception at `await()`, subsequent operations inside that scope will fail with CancellationException because the scope is dead."
            },
            {
                "interviewer": "How do you test this scenario deterministically in a unit test?",
                "answer": "Using `runTest`: configure one mock API call to throw an exception and the other two to have simulated delays. Verify that the test throws the expected exception and assert that the other two API jobs were cancelled without completing."
            },
            {
                "interviewer": "What happens if all 3 APIs need rollback logic if one fails?",
                "answer": "If any successful booking must be reversed upon sibling failure, catch the exception outside `coroutineScope`, and in the catch block or using a saga pattern, launch compensatory rollback calls (like refunding the successful flight)."
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

    for q in COR_19_25:
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
    print(f"Updated {DATA_FILE} with questions COR-19 to COR-25. Total questions: {len(combined)}")


if __name__ == "__main__":
    main()
