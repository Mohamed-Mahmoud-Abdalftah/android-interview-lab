#!/usr/bin/env python3
"""Generator for COR-07 through COR-12 (excluding COR-11) elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "cor.json"

COR_07_12 = [
    {
        "id": "COR-07",
        "arabic_explanation": (
            "الـ `CoroutineDispatcher` هو المسؤول عن تحديد **أي Thread أو Thread Pool** سينفذ الـ Coroutine. فهم الفروق بينهم ضروري جداً لتجنب تجميد الشاشة أو إهدار موارد الجهاز:\n\n"
            "1. `Dispatchers.Main`:\n"
            "   - محصور على **Android Main (UI) Thread** المربوط بـ `Looper.getMainLooper()`.\n"
            "   - مخصص لتحديث واجهة المستخدم (Views, Jetpack Compose UI state, Dialogs) ومعالجة تفاعل المستخدم.\n"
            "   - **تحذير صارم:** لا تشغل عليه أي كود ثقيل (Disk I/O, Network, Heavy Math) لأن أي تأخير أكثر من 16ms هيوقع فريمات (Jank)، وتأخير 5 ثوانٍ هيطلع رسالة ANR.\n"
            "   - يوجد أيضاً `Dispatchers.Main.immediate` الذي ينفذ الكود فوراً بدون posting إلى message queue إذا كنت بالفعل على Main Thread.\n\n"
            "2. `Dispatchers.IO`:\n"
            "   - مخصص لعمليات الإدخال والإخراج التي تحظر الـ Thread (Blocking I/O operations).\n"
            "   - زي: قراءة/كتابة الملفات من Disk، قراءة/كتابة قاعدة بيانات SQLite/Room، واستدعاءات شبكة blocking.\n"
            "   - **حجم الـ Pool:** مصمم بحيث يتمدد حسب الحاجة (Elastic Pool) بحد أقصى **64 Threads** (أو عدد أنوية الـ CPU إن كان أكبر).\n\n"
            "3. `Dispatchers.Default`:\n"
            "   - مخصص للعمليات الحسابية المكثفة التي تستهلك المعالج (CPU-intensive tasks).\n"
            "   - زي: عمل Parsing لملف JSON ضخم، تشفير وفك تشفير، معالجة وفرز قوائم كبيرة (Sorting)، أو معالجة صور.\n"
            "   - **حجم الـ Pool:** مربوط مباشرة بعدد أنوية المعالج الفيزيائية (`Runtime.getRuntime().availableProcessors()`)، بحد أدنى 2 threads. لا يمكن أن يزيد عن عدد الأنوية لأن تشغيل threads أكتر من الأنوية على مهام CPU بيعمل context switching ع الفاضي.\n\n"
            "4. `Dispatchers.Unconfined`:\n"
            "   - لا يقيد الـ Coroutine بأي Thread معين!\n"
            "   - يبدأ التنفيذ على نفس الـ Thread الحالي للـ Caller حتى يصل لأول نقطة تعليق (Suspension point)، وبعد التعليق يكمل على الـ Thread الذي نادى دالة الـ resume.\n"
            "   - **استخدامه الإنتاجي شبه معدوم**؛ غير مخصص لكود التطبيق العادي لأنه يجعل سلوك الـ Threads غير متوقع، لكنه قد يستخدم في بعض الـ Unit Tests أو العمليات الداخلية المتخصصة جداً."
        ),
        "practical_walkthrough": (
            "في شاشة معالجة وتصدير تقرير مالي (PDF Export & Sync):\n"
            "- **توزيع العمل على الـ Dispatchers باحترافية:**\n"
            "  viewModelScope.launch(Dispatchers.Main) { // 1. نبدأ على Main لعرض شريط التحميل\n"
            "      _uiState.value = UiState.Exporting\n"
            "      \n"
            "      // 2. عمليات حسابية ثقيلة لمعالجة الأرقام ننقلها لـ Default (CPU):\n"
            "      val processedData = withContext(Dispatchers.Default) {\n"
            "          calculateFinancialSummaries(rawTransactions)\n"
            "      }\n"
            "      \n"
            "      // 3. كتابة ملف الـ PDF على القرص نرسلها لـ IO (Disk Blocking):\n"
            "      val pdfFile = withContext(Dispatchers.IO) {\n"
            "          writePdfToStorage(processedData)\n"
            "      }\n"
            "      \n"
            "      // 4. نعود تلقائياً لـ Main لإخفاء شريط التحميل وعرض إشعار النجاح:\n"
            "      _uiState.value = UiState.Success(pdfFile)\n"
            "  }"
        ),
        "quick_answer": "Dispatchers.Main runs on Android's UI thread for view updates; Dispatchers.IO manages an elastic pool of up to 64 threads for blocking disk and network I/O; Dispatchers.Default uses a thread pool sized to CPU core count for compute-heavy tasks; and Dispatchers.Unconfined starts in the caller thread and resumes in whatever thread resumed the suspension.",
        "best_answer": (
            "Dispatchers govern thread assignment for coroutines, each tailored for a specific workload characteristics:\n\n"
            "**Dispatchers.Main** is bound to the Android Main Looper thread. It is strictly reserved for UI rendering, handling touch events, and mutating Compose or LiveData UI state. Heavy work here causes frame drops and ANRs.\n\n"
            "**Dispatchers.IO** is optimized for blocking input/output operations, such as Room database operations, reading local files, or legacy blocking HTTP calls. It uses an elastic thread pool that scales up to 64 threads (or the number of CPU cores if higher), ensuring blocking I/O does not starve other tasks.\n\n"
            "**Dispatchers.Default** is reserved for CPU-intensive calculations like JSON parsing, bitmap transformations, cryptographic operations, or sorting large collections. Its thread pool is capped strictly at the number of available CPU cores (minimum 2), preventing unnecessary thread context-switching overhead.\n\n"
            "**Dispatchers.Unconfined** does not confine execution to any specific thread. It begins in the caller's thread and resumes in whichever thread resumed the continuation. Because it leads to non-deterministic thread transitions, we avoid it in production Android code."
        ),
        "deep_answer": (
            "Behind the scenes, `Dispatchers.Default` and `Dispatchers.IO` share the same underlying JVM thread pool implementation (`ExperimentalCoroutineDispatcher`). "
            "When you switch between `Default` and `IO` using `withContext`, the coroutine scheduler can often shift the task between pool sub-queues without an expensive OS thread context switch if worker threads are available.\n\n"
            "In Android development, `Dispatchers.Main.immediate` deserves special mention: standard `Dispatchers.Main` schedules execution via `Handler.post()`, introducing an asynchronous dispatch delay even if you are already on the Main thread. `Dispatchers.Main.immediate` executes synchronously if the caller is already on the UI thread, preventing momentary UI flicker.\n\n"
            "Furthermore, for fine-grained resource limits, Kotlin 1.6+ introduced `limitedParallelism(n)`. On `Dispatchers.IO`, you can create a dedicated dispatcher with a strict concurrency ceiling (e.g., `Dispatchers.IO.limitedParallelism(4)`) to avoid overwhelming local SQLite database connection pools with dozens of concurrent threads."
        ),
        "follow_ups": [
            {
                "interviewer": "Why do `Dispatchers.Default` and `Dispatchers.IO` share the same underlying pool?",
                "answer": "They share the underlying worker thread pool so that switching between CPU work (Default) and I/O work (IO) via withContext can reuse idle worker threads dynamically, minimizing thread creation churn and memory allocation overhead."
            },
            {
                "interviewer": "When would you use `limitedParallelism`?",
                "answer": "To enforce a concurrency throttle without creating a new thread pool. For instance, Room database write transactions should be capped at `limitedParallelism(1)` to eliminate SQLite locking errors, or image uploading can be limited to `limitedParallelism(4)` to prevent saturating bandwidth."
            },
            {
                "interviewer": "Can a coroutine running on `Dispatchers.Main` cause an ANR if it only calls suspending functions?",
                "answer": "No, as long as the suspending functions are genuinely non-blocking and Main-Safe. Suspension yields the main thread to Android's message queue. An ANR only happens if the coroutine executes a synchronous blocking call (like Thread.sleep or a heavy loop) on Main."
            }
        ]
    },
    {
        "id": "COR-08",
        "arabic_explanation": (
            "هذا السؤال يتعمق في البنية التحتية لـ `Dispatchers.Main` و `Dispatchers.IO` في بيئة أندرويد:\n\n"
            "1. هل `Dispatchers.Main` يستخدم الـ UI Thread الحقيقي؟\n"
            "   - **نعم، 100%!** على منصة Android، `Dispatchers.Main` مربوط بالـ `Looper.getMainLooper()` والـ `Handler` الخاص بالـ Main Thread.\n"
            "   - أي كود يتنفذ عليه بيتم إدراجه كـ `Message` داخل الـ `MessageQueue` الخاصة بالـ UI Thread.\n\n"
            "2. هل `Dispatchers.IO` يستخدم Thread Pool؟ وإزاي بيشتغل؟\n"
            "   - **نعم، يستخدم Elastic Thread Pool.**\n"
            "   - بيشارك البنية التحتية مع `Dispatchers.Default`، لكن مخصص لمهام الـ Blocking.\n"
            "   - الحد الأقصى الافتراضي لعدد الـ Threads فيه هو **64** (أو عدد الـ Cores إن كان أكبر).\n"
            "   - لو عندك 50 طلب شبكة أو قراءة ديسك blocking شغالين في نفس الوقت، الـ Pool هيفتح threads كافية حتى 64 thread لضمان عدم توقف العمليات الأخرى."
        ),
        "practical_walkthrough": (
            "فهم تأثير ذلك على استهلاك الذاكرة وتجنب التجميد:\n"
            "- لو شغلت دالة `Thread.sleep(5000)` على `Dispatchers.Main`:\n"
            "  الـ Handler هيتوقف عن معالجة رسائل اللمس والرسم الخاصة بـ `Choreographer`، وبعد 5 ثوانٍ النظام هيطلع رسالة 'Application Not Responding' (ANR).\n"
            "- لو شغلت 70 دالة `Thread.sleep(5000)` على `Dispatchers.IO`:\n"
            "  أول 64 دالة هيحجزوا الـ 64 threads في الـ IO Pool، والـ 6 المتبقين هيقفوا في طابور الانتظار (Queue) حتى يفرغ أي thread، ولكن **لن يحدث أي ANR** لأن الـ Main Thread حر تماماً."
        ),
        "quick_answer": "Yes, Dispatchers.Main uses Android's single UI thread backed by Looper.getMainLooper(). Yes, Dispatchers.IO uses an elastic thread pool that scales up to 64 worker threads, sharing worker threads with Dispatchers.Default while allowing blocking operations without exhausting CPU compute threads.",
        "best_answer": (
            "Yes to both, and understanding their runtime implementation is key to writing high-performance Android apps.\n\n"
            "`Dispatchers.Main` directly wraps the Android platform's UI thread. It is powered by `kotlinx-coroutines-android`, which provides a `HandlerDispatcher` tied to `Looper.getMainLooper()`. When you dispatch work to `Dispatchers.Main`, it posts a `Runnable` into the main thread's `MessageQueue`. That is why executing blocking code on it directly blocks the Android Choreographer from rendering 60/120Hz frames and leads to ANRs.\n\n"
            "`Dispatchers.IO` is explicitly backed by an elastic thread pool. It shares a common worker pool with `Dispatchers.Default` but overrides its parallelism limit to a default cap of 64 threads (or the number of CPU cores if greater). This design recognizes that I/O tasks spend most of their time waiting on external hardware or network sockets, so having up to 64 threads blocked on I/O does not degrade CPU performance."
        ),
        "deep_answer": (
            "At the architectural level, `Dispatchers.IO` solves the thread starvation dilemma. If blocking I/O ran on `Dispatchers.Default`, which only has as many threads as CPU cores (e.g., 4 or 8), a few blocking database reads would completely saturate all available threads, preventing compute tasks and animations from running.\n\n"
            "By setting the capacity to 64 on `Dispatchers.IO`, the coroutine scheduler can spin up additional OS threads on demand when threads block on `read()` or `write()` calls. When those threads become idle, they are eventually timed out and reclaimed by the runtime.\n\n"
            "In Android profiling, you can observe these named threads in Android Studio's Profiler as `DefaultDispatcher-worker-X`. If your application frequently hits the 64-thread ceiling due to slow external APIs, it indicates an architectural bottleneck that should be refactored using non-blocking asynchronous APIs (like OkHttp asynchronous enqueue or Flow) rather than scaling thread pools indefinitely."
        ),
        "follow_ups": [
            {
                "interviewer": "Can you change the 64-thread limit of Dispatchers.IO?",
                "answer": "Yes. You can configure the system property `kotlinx.coroutines.io.parallelism` before runtime initialization, or use `Dispatchers.IO.limitedParallelism(N)` to establish dedicated sub-pools with custom concurrency caps."
            },
            {
                "interviewer": "Why does `Dispatchers.Main` require the `kotlinx-coroutines-android` artifact?",
                "answer": "Because standard Kotlin Coroutines is a multiplatform JVM library that knows nothing about Android. The `kotlinx-coroutines-android` library provides the Android-specific implementation that hooks into `android.os.Handler` and `Looper.getMainLooper()`."
            },
            {
                "interviewer": "What happens if you use `Dispatchers.Main` in pure JVM unit tests without the Android runtime?",
                "answer": "It will throw an `IllegalStateException: Module with the Main dispatcher had failed to initialize`. In unit tests, you must replace `Dispatchers.Main` using `Dispatchers.setMain(testDispatcher)` from `kotlinx-coroutines-test`."
            }
        ]
    },
    {
        "id": "COR-09",
        "arabic_explanation": (
            "دالة `withContext` هي الأداة القياسية في Kotlin لتغيير سياق الـ Coroutine (`CoroutineContext`) بشكل معلق وآمن:\n\n"
            "1. إيه هي دالة `withContext`؟\n"
            "   - هي **Suspending Function** بتنقل تنفيذ البلوك الحالي إلى `CoroutineContext` مختلف (عادة `Dispatcher` مختلف)، وتنتظر انتهاء البلوك، وترجع النتيجة فوراً للمتصل.\n"
            "   - **ليست Coroutine Builder جديد:** يعني هي مش زي `launch` أو `async`؛ هي لا تنشئ Coroutine منفصلة في شجرة الـ Hierarchy، بل تعلق الـ Coroutine الحالية وتغير الـ Dispatcher بتاعها.\n\n"
            "2. إمتى بنستخدمها؟\n"
            "   - لتحقيق **Main-Safety**: كتابة الدوال المعلقة (Suspend functions) بحيث تنقل العمليات الثقيلة داخلياً إلى `Dispatchers.IO` أو `Dispatchers.Default`، لكي يستطيع المستدعي استدعاءها من الـ UI Thread بأمان تام.\n"
            "   - للتبديل السريع بين الـ Threads داخل نفس الـ Flow التسلسلي.\n\n"
            "3. المقارنة مع `async { ... }.await()`:\n"
            "   - كتابة `async(Dispatchers.IO) { ... }.await()` هو **Anti-Pattern خطير وسيء للأداء**! هو ينشئ Coroutine جديدة و Deferred كائن في الـ Heap بدون أي داعٍ.\n"
            "   - `withContext(Dispatchers.IO) { ... }` أسرع بكثير، أخف في الذاكرة، ويضمن معالجة الاستثناءات والإلغاء بطريقة متسلسلة ونظيفة."
        ),
        "practical_walkthrough": (
            "في دالة استرجاع ومعالجة بيانات المستخدم من قاعدة البيانات المحلية:\n"
            "```kotlin\n"
            "class UserRepositoryImpl(\n"
            "    private val userDao: UserDao,\n"
            "    private val ioDispatcher: CoroutineDispatcher = Dispatchers.IO\n"
            ") : UserRepository {\n"
            "    \n"
            "    // الدالة Main-Safe تماماً لأنها تستخدم withContext داخلياً:\n"
            "    override suspend fun getUserWithProfile(id: String): UserProfile =\n"
            "        withContext(ioDispatcher) {\n"
            "            val entity = userDao.getUserById(id) // قراءة من القرص (Blocking I/O)\n"
            "            entity.toDomainProfile() // تحويل البيانات\n"
            "        }\n"
            "}\n"
            "```\n"
            "لاحظ حقن `ioDispatcher` في الـ Constructor؛ هذا يسمح باستبداله بـ `StandardTestDispatcher` في الـ Unit Tests."
        ),
        "quick_answer": "withContext is a suspending function that temporarily switches the coroutine's context (such as its dispatcher) for a block of code, suspends until completion, and returns the result. It is the idiomatic way to achieve Main-Safety without allocating extra coroutines like async/await would.",
        "best_answer": (
            "I use `withContext` to switch execution context—most commonly to move work onto a different dispatcher and return a result to the caller synchronously from the coroutine's perspective.\n\n"
            "Its primary architectural role is enforcing **Main-Safety**. In clean architecture, repository and use-case suspend functions should be safe to call from Dispatchers.Main. By wrapping disk I/O or heavy computations in `withContext(Dispatchers.IO)` or `withContext(Dispatchers.Default)`, the function encapsulates its own threading requirements. The caller on the UI thread simply calls the suspend function without worrying about freezing the UI.\n\n"
            "A key senior distinction: never use `async { ... }.await()` to switch dispatchers for a single task. `withContext` is purpose-built for sequential context switching. It avoids creating a child coroutine and Deferred heap object, and it optimizes thread transitions under the hood."
        ),
        "deep_answer": (
            "Under the hood, `withContext` optimizes context switching using the `DispatchedCoroutine` fast path. If the target dispatcher matches the current coroutine's dispatcher, `withContext` skips dispatching altogether and executes the lambda synchronously in the current call frame, eliminating any scheduling overhead.\n\n"
            "If the dispatcher is different, it suspends the caller continuation, dispatches the block onto the new dispatcher, and upon completion, uses a specialized continuation wrapper to dispatch the return value back to the original caller dispatcher.\n\n"
            "In enterprise codebases, we mandate injecting dispatchers via dependency injection (e.g., `@IoDispatcher val dispatcher: CoroutineDispatcher`). Hardcoding `withContext(Dispatchers.IO)` in class bodies makes deterministic unit testing impossible because tests cannot control or advance virtual time without replacing the dispatcher with `StandardTestDispatcher`."
        ),
        "follow_ups": [
            {
                "interviewer": "How does cancellation behave inside `withContext`?",
                "answer": "`withContext` checks for cancellation both before entering the block and upon returning. If the coroutine is cancelled while executing inside `withContext`, cancellation is cooperative: as soon as the block reaches a suspension point or checks `ensureActive()`, it throws `CancellationException` and exits."
            },
            {
                "interviewer": "Why is hardcoding `Dispatchers.IO` inside `withContext` considered an anti-pattern?",
                "answer": "Because it breaks unit test determinism. In unit tests using `runTest`, hardcoded dispatchers run on real background threads outside the test scheduler's control, causing flakiness and race conditions. Injecting dispatchers allows tests to substitute a `TestDispatcher`."
            },
            {
                "interviewer": "What is the difference between `withContext(NonCancellable)` and regular `withContext`?",
                "answer": "`withContext(NonCancellable)` temporarily replaces the active Job with an un-cancellable job. It is used exclusively inside `finally` cleanup blocks to execute critical cleanup suspend functions (like closing files or sending cancellation analytics) that would otherwise be aborted if the coroutine was cancelled."
            }
        ]
    },
    {
        "id": "COR-10",
        "arabic_explanation": (
            "الإلغاء في Kotlin Coroutines هو **Cooperative (تعاوني)**، وهذا المفهوم هو السبب رقم واحد لحدوث أخطاء عدم توقف العمليات في الخلفية:\n\n"
            "1. ما معنى أن الإلغاء 'تعاوني' (Cooperative Cancellation)؟\n"
            "   - الكود لا يتم إيقافه بالقوة الجبرية من نظام التشغيل أو الـ JVM.\n"
            "   - استدعاء `job.cancel()` لا يعني قتل الـ Coroutine فوراً؛ هو فقط بيغير حالة الـ Job إلى `isCancelled = true`.\n"
            "   - **الـ Coroutine نفسها هي المسؤولة عن التعاون:** لازم الكود يفحص حالة الإلغاء بنفسه ويتوقف طواعية!\n\n"
            "2. ما هي نقاط الإلغاء (Cancellation Points)؟\n"
            "   - هي الأماكن التي تقوم تلقائياً بفحص الإلغاء ورمي `CancellationException` إذا كان الـ Job ملغياً.\n"
            "   - جميع الدوال المعلقة القياسية في مكتبة Kotlin (Standard Suspending Functions) هي نقاط إلغاء تلقائية، مثل:\n"
            "     * `delay()`\n"
            "     * `yield()`\n"
            "     * `withContext()`\n"
            "     * `await()`\n\n"
            "3. متى يفشل الإلغاء ويستمر الكود في العمل؟\n"
            "   - لو عندك Loop بتعمل عمليات CPU مكثفة أو Blocking I/O بدون أي دالة suspend:\n"
            "     `while (i < 1_000_000) { compute() }`\n"
            "     الكود ده هيفضل شغال حتى لو ناديت `job.cancel()` 100 مرة!\n"
            "   - **الحل:** لازم تفحص الإلغاء يدوياً داخل الـ Loop باستخدام `isActive` أو تنادي `ensureActive()` أو `yield()` في كل لفة."
        ),
        "practical_walkthrough": (
            "في دالة ضغط وتحويل ملف فيديو كبير (Video Transcoding):\n"
            "- **الكود غير المتعاون (Non-cooperative Loop):**\n"
            "  val job = scope.launch(Dispatchers.Default) {\n"
            "      for (frame in allFrames) {\n"
            "          compressFrame(frame) // لا توجد دالة تعليق هنا!\n"
            "      }\n"
            "  }\n"
            "  // المستخدم ضغط 'إلغاء' ومشي من الشاشة:\n"
            "  job.cancel() // الكود هيفضل شغال ويستهلك البطارية والمعالج حتى ينتهي كل الفيديو!\n"
            "- **الكود المتعاون الصحيح (Cooperative Loop):**\n"
            "  val job = scope.launch(Dispatchers.Default) {\n"
            "      for (frame in allFrames) {\n"
            "          ensureActive() // تفحص الإلغاء وترمي CancellationException فوراً لو تم الإلغاء\n"
            "          compressFrame(frame)\n"
            "      }\n"
            "  }\n"
            "- النتيجة: بمجرد استدعاء `job.cancel()`، العملية تتوقف فوراً في اللفة التالية ويتم تحرير موارد الجهاز."
        ),
        "quick_answer": "Coroutine cancellation is cooperative: calling cancel() merely sets the job's state to cancelled. The coroutine itself must actively cooperate by reaching a cancellation point—such as delay(), yield(), or ensureActive()—which checks that state and throws a CancellationException to terminate execution.",
        "best_answer": (
            "Coroutine cancellation is strictly cooperative. Calling `job.cancel()` does not preemptively kill the thread or forcibly terminate execution like a deprecated Thread.stop() would. Instead, it transitions the coroutine's internal Job state to 'cancelling'.\n\n"
            "The coroutine code must cooperate to actually stop. Standard library suspending functions—such as `delay()`, `withContext()`, `yield()`, and `await()`—act as built-in **cancellation points**. Before executing and immediately upon resuming, they check if their Job is cancelled. If it is, they throw a `CancellationException`, which unwinds the coroutine call stack cleanly.\n\n"
            "The failure case occurs during tight, non-suspending CPU loops or blocking Java I/O. If a coroutine executes a mathematical loop for 10 seconds without calling any suspending functions, it will completely ignore `cancel()` until the loop finishes. To make CPU-bound code cancellable, we explicitly insert `ensureActive()` or `yield()` inside the loop body."
        ),
        "deep_answer": (
            "At the runtime level, cancellation uses `CancellationException` as its unwinding vehicle. Crucially, `CancellationException` is treated specially by the coroutine machinery: it is considered normal completion of a cancelled task rather than an error. It does not cancel parent scopes or trigger uncaught exception handlers.\n\n"
            "However, this introduces a classic production trap: swallowing `CancellationException`. If a developer writes a broad catch block:\n\n"
            "```kotlin\n"
            "try {\n"
            "    doWork()\n"
            "} catch (e: Exception) { // Swallows CancellationException!\n"
            "    logError(e)\n"
            "}\n"
            "```\n\n"
            "This catches `CancellationException` and ignores it, completely breaking cancellation. The coroutine will refuse to stop! The golden rule is to either catch specific exceptions (like `IOException`) or immediately rethrow `CancellationException`:\n\n"
            "```kotlin\n"
            "} catch (e: Exception) {\n"
            "    if (e is CancellationException) throw e\n"
            "    handleError(e)\n"
            "}\n"
            "```"
        ),
        "follow_ups": [
            {
                "interviewer": "What is the difference between `ensureActive()` and checking `isActive`?",
                "answer": "`isActive` returns a boolean flag, requiring you to manually write `if (!isActive) return`. `ensureActive()` is an inline function that checks `isActive` and throws `CancellationException` immediately if false, guaranteeing standard coroutine unwinding."
            },
            {
                "interviewer": "What does `yield()` do, and how does it differ from `ensureActive()`?",
                "answer": "`ensureActive()` only checks for cancellation. `yield()` checks for cancellation AND yields the current thread to other coroutines in the dispatcher queue, allowing pending tasks to execute before resuming. It is ideal for compute loops to maintain fairness."
            },
            {
                "interviewer": "How do you run critical cleanup code after a coroutine is cancelled?",
                "answer": "By using a `try-finally` block. The `finally` block is guaranteed to execute upon cancellation. If the cleanup itself requires suspending functions (like closing a database), wrap that suspending call in `withContext(NonCancellable)` so it isn't aborted."
            }
        ]
    },
    {
        "id": "COR-12",
        "arabic_explanation": (
            "المقارنة بين `Job` و `SupervisorJob` هي أهم قاعدة في إدارة الأخطاء في شجرة الـ Coroutines (Structured Concurrency Tree):\n\n"
            "1. الـ `Job` العادي (Standard Job - Two-way Failure Propagation):\n"
            "   - العلاقة بين الأبناء والأب **ثنائية الاتجاه (Bidirectional)**.\n"
            "   - لو عندك أب (Job) أطلق طفلين A و B:\n"
            "     * لو الطفل A فشل برمي Exception (غير CancellationException):\n"
            "     * الفشل يصعد للأب فوراً.\n"
            "     * الأب يلغي نفسه.\n"
            "     * الأب يقوم بإلغاء الطفل B وجميع الأطفال الآخرين!\n"
            "   - الفلسفة هنا هي: **All-or-Nothing Transaction**. لو جزء من العملية فشل، كل العملية تلغى لتجنب حالة بيانات غير مكتملة.\n\n"
            "2. الـ `SupervisorJob` (One-way Failure Propagation):\n"
            "   - العلاقة بين الأبناء **أحادية الاتجاه للأسفل فقط (Downwards only)**.\n"
            "   - لو الطفل A فشل ورمى Exception:\n"
            "     * الفشل **لا ينتقل للأب**.\n"
            "     * الأب يظل حياً ونشطاً (`isActive = true`).\n"
            "     * الطفل B يستمر في العمل بدون أن يتأثر إطلاقاً!\n"
            "   - الإلغاء الوحيد هو من أعلى لأسفل: لو ألغيت الأب نفسه يدوياً، كل الأطفال يلغون.\n\n"
            "3. الفخ الشائع جداً في الـ SupervisorJob (Common Trap):\n"
            "   - كتابة: `launch(SupervisorJob()) { ... }` داخل `viewModelScope`.\n"
            "   - تمرير `SupervisorJob()` كـ parameter في دالة `launch` يقطع علاقة الـ Parent-Child ويجعل هذا الـ Job منفصلاً، ولا يجعل الأطفال المشتقين منه تحت إشراف supervisor كما يظن المطور!"
        ),
        "practical_walkthrough": (
            "في شاشة لوحة تحكم الأخبار (Dashboard Activity):\n"
            "- الشاشة بتعرض: 1. حالة الطقس (Weather Widget)، 2. أسعار العملات (Stock Widget)، 3. قائمة الأخبار.\n"
            "- **النهج الخاطئ باستخدام Job عادي:**\n"
            "  لو خدمة أسعار العملات فشلت ورمت NetworkException، الـ Job العادي سيلغي شاشة الأخبار بالكامل وشاشة الطقس! المستخدم يرى شاشة بيضاء خالية لمجرد أن widget فرعي فشل.\n"
            "- **النهج الصحيح باستخدام SupervisorJob / supervisorScope:**\n"
            "  في الـ ViewModel، أو باستخدام `supervisorScope`:\n"
            "  ```kotlin\n"
            "  supervisorScope {\n"
            "      launch { fetchWeather() } // لو فشل هنا، لن يؤثر على الأخبار\n"
            "      launch { fetchStocks() }  // فشل هذا Widget يعرض Retry button فقط\n"
            "      launch { fetchNews() }    // يستمر في التحميل والعرض بنجاح\n"
            "  }\n"
            "  ```"
        ),
        "quick_answer": "In a standard Job, failure propagates bidirectionally: if one child fails, it cancels the parent and all sibling coroutines. In a SupervisorJob, failure propagates only downwards: a child's failure does not cancel the parent or affect sibling coroutines.",
        "best_answer": (
            "The difference between a standard `Job` and a `SupervisorJob` lies entirely in how failure propagates through the coroutine hierarchy.\n\n"
            "With a standard `Job`, failure is bidirectional. If any child coroutine fails with an unhandled exception, it immediately notifies its parent. The parent cancels itself, which cascades down to cancel all other active siblings. This 'all-or-nothing' semantic is ideal for atomic transactions—for example, calling an order API and an inventory API where both must succeed together.\n\n"
            "With a `SupervisorJob`, failure propagates only downwards. If a child coroutine fails, the `SupervisorJob` does not cancel itself, and sibling coroutines continue executing undisturbed. Only if the `SupervisorJob` itself is explicitly cancelled will all its children be cancelled.\n\n"
            "In Android architecture, `viewModelScope` internally uses a `SupervisorJob`. This ensures that if one user action—like refreshing an avatar—throws an exception, it doesn't tear down the entire ViewModel and abort unrelated ongoing operations."
        ),
        "deep_answer": (
            "A critical interview pitfall is how developers misuse `SupervisorJob` with coroutine builders. "
            "Consider this common mistake:\n\n"
            "```kotlin\n"
            "// ❌ WRONG:\n"
            "viewModelScope.launch(SupervisorJob()) {\n"
            "    val deferred1 = async { fetchA() }\n"
            "    val deferred2 = async { fetchB() }\n"
            "}\n"
            "```\n\n"
            "Passing `SupervisorJob()` as an argument to `launch` creates a new parent job that severs structured concurrency from `viewModelScope`. Furthermore, inside the `launch` block, `launch` itself creates a regular `Job` as the parent for `deferred1` and `deferred2`. If `fetchA` fails, it still cancels `fetchB`!\n\n"
            "To correctly supervise siblings within a suspend function, you must use the `supervisorScope { }` builder. `supervisorScope` installs a `SupervisorJob` as the parent for all coroutines launched directly within its block, isolating child failures without breaking structured concurrency."
        ),
        "follow_ups": [
            {
                "interviewer": "Who handles the exception when a child fails inside a SupervisorJob?",
                "answer": "Because the failure is not swallowed or propagated to the parent SupervisorJob, each child coroutine is directly responsible for its own exception. In `launch`, it must either be caught with try-catch or handled by a `CoroutineExceptionHandler` attached to that child. Otherwise, it reaches the uncaught exception handler."
            },
            {
                "interviewer": "Why does `coroutineScope` cancel siblings while `supervisorScope` does not?",
                "answer": "`coroutineScope` uses a standard Job to enforce atomic, all-or-nothing semantics where partial failures invalidate the whole scope. `supervisorScope` uses a SupervisorJob specifically designed for independent, concurrent sub-tasks."
            },
            {
                "interviewer": "Does `SupervisorJob` affect how cancellation propagates down when `cancel()` is called?",
                "answer": "No. When you call `cancel()` on a `SupervisorJob`, downward cancellation works identically to a standard Job: the supervisor and all of its active children are cancelled immediately."
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

    for q in COR_07_12:
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
    print(f"Updated {DATA_FILE} with questions COR-07 to COR-12. Total questions: {len(combined)}")


if __name__ == "__main__":
    main()
