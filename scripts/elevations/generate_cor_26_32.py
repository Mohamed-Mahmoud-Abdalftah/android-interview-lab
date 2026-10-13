#!/usr/bin/env python3
"""Generator for COR-26 through COR-32 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "cor.json"

COR_26_32 = [
    {
        "id": "COR-26",
        "arabic_explanation": (
            "استدعاء 3 APIs مستقلة بالتوازي مع الحفاظ على النجاح الجزئي (Partial Success) وعدم ابتلاع الإلغاء هو عكس السؤال السابق تماماً:\n\n"
            "1. المعمارية المطلوبة:\n"
            "   - الشاشة بتعرض: الأخبار، الطقس، والإعلانات.\n"
            "   - لو فشل جلب الطقس، نريد عرض الأخبار والإعلانات بنجاح بدلاً من تدمير الشاشة بالكامل (Graceful Degradation).\n"
            "   - **لكن انتبه للشرط الحرج:** 'دون ابتلاع الإلغاء' (Without swallowing cancellation). لو المستخدم قفل الشاشة، نريد إلغاء كل العمليات فوراً!\n\n"
            "2. الأداة المناسبة: `supervisorScope { }`:\n"
            "   - `supervisorScope` يعزل فشل الأبناء عن بعضهم؛ فشل طلب لا يلغي الإخوة.\n"
            "   - ولكنه ما زال خاضعاً لـ Structured Concurrency: لو الأب نفسه تم إلغاؤه (المستخدم غادر الشاشة)، يلغي جميع الأبناء فوراً!\n\n"
            "3. نمط الكود الصحيح:\n"
            "   - نستخدم `runCatching` أو `try-catch` حول كل استدعاء `await()` **مع إعادة رمي `CancellationException` صراحة**:\n"
            "     `if (e is CancellationException) throw e`"
        ),
        "practical_walkthrough": (
            "تنفيذ عملي لشاشة لوحة التحكم (Home Dashboard):\n"
            "```kotlin\n"
            "data class DashboardState(\n"
            "    val news: List<NewsItem>?,\n"
            "    val weather: WeatherInfo?,\n"
            "    val ads: List<AdBanner>?\n"
            ")\n"
            "\n"
            "suspend fun fetchDashboard(): DashboardState = supervisorScope {\n"
            "    val newsDeferred = async { safeApiCall { api.getNews() } }\n"
            "    val weatherDeferred = async { safeApiCall { api.getWeather() } }\n"
            "    val adsDeferred = async { safeApiCall { api.getAds() } }\n"
            "    \n"
            "    DashboardState(\n"
            "        news = newsDeferred.await(),\n"
            "        weather = weatherDeferred.await(),\n"
            "        ads = adsDeferred.await()\n"
            "    )\n"
            "}\n"
            "\n"
            "suspend fun <T> safeApiCall(block: suspend () -> T): T? = try {\n"
            "    block()\n"
            "} catch (e: CancellationException) {\n"
            "    throw e // لا نبلع الإلغاء أبداً!\n"
            "} catch (e: Exception) {\n"
            "    null // فشل جزئي آمن\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Use 'supervisorScope' with parallel 'async' tasks and handle child exceptions locally using try-catch that explicitly rethrows CancellationException. This isolates failures so successful sibling results are preserved while ensuring top-level lifecycle cancellation still terminates all work.",
        "best_answer": (
            "To preserve partial success across independent concurrent API calls without breaking cancellation, use `supervisorScope` combined with selective local error handling.\n\n"
            "Inside `supervisorScope`, each `async` coroutine is supervised. If one child throws an exception, the failure is isolated: the supervisor scope does not cancel, and sibling tasks continue running. This allows the UI to render whatever data succeeded (e.g., displaying news articles even if the weather widget fails).\n\n"
            "To satisfy the critical requirement of **not swallowing cancellation**, wrap each individual call in a try-catch block that inspects the exception: if `e is CancellationException`, rethrow it immediately. If the user navigates away and the parent ViewModel cancels the scope, the `CancellationException` propagates cleanly down and aborts all network connections."
        ),
        "deep_answer": (
            "Under the hood, `supervisorScope` installs a `SupervisorJob` as the parent context. When a child coroutine fails with a non-cancellation exception, `childCancelled` on the supervisor returns `false`. This prevents the scope from entering the `CANCELLING` state.\n\n"
            "A dangerous antipattern is writing:\n\n"
            "```kotlin\n"
            "// ❌ ANTI-PATTERN:\n"
            "supervisorScope {\n"
            "    val news = async { runCatching { api.getNews() }.getOrNull() }\n"
            "}\n"
            "```\n\n"
            "Standard `runCatching` catches `Throwable`, which intercepts `CancellationException` and converts it to a null result! When the user exits the screen, the coroutines keep running on background threads, ignoring cancellation. "
            "In production, we define a dedicated `runSuspendCatching` extension that rethrows `CancellationException`, guaranteeing both partial fault tolerance and responsive lifecycle cancellation."
        ),
        "follow_ups": [
            {
                "interviewer": "What is the difference between failure isolation in `supervisorScope` and passing `SupervisorJob()` to a regular scope?",
                "answer": "Passing `SupervisorJob()` to `launch` creates an unattached parent Job, breaking structured concurrency and preventing automatic child cancellation on scope exit. `supervisorScope` preserves structured concurrency: it is a suspending function that waits for all active children and cancels them if the parent scope cancels."
            },
            {
                "interviewer": "How do you represent partial failure in the UI layer?",
                "answer": "Using a sealed UI model or a data class where independent section models hold sealed states (e.g., `news: SectionState<List<News>>`, which can be `Success(data)` or `Error(reason)` with a localized retry action)."
            },
            {
                "interviewer": "Can you use Kotlin Flow `merge` or `zip` for this instead?",
                "answer": "Yes. You can emit each API call as a separate Flow, use `catch { emit(null) }` on individual streams, and combine them using `combine(flow1, flow2, flow3)` for reactive UI rendering."
            }
        ]
    },
    {
        "id": "COR-27",
        "arabic_explanation": (
            "حدوث Timeout في عملية الدفع بعد وصول الطلب للسيرفر وكيفية تجنب الخصم المزدوج (Duplicate Charges) هو سؤال معماري كلاسيكي في تطبيقات الـ Fintech والتجارة الإلكترونية:\n\n"
            "1. المشكلة (The Two Generals Problem in Payments):\n"
            "   - العميل ضغط 'تأكيد الدفع' بمبلغ 1,000 جنيه.\n"
            "   - التطبيق أرسل الطلب للسيرفر، والسيرفر خصم المبلغ بالفعل.\n"
            "   - ولكن قبل أن تصل رسالة الـ Response للموبايل، شبكة الهاتف قطعت أو حدث Socket Timeout على الموبايل!\n"
            "   - الموبايل يظن أن الطلب فشل! لو أعاد المحاولة ببساطة، سيتم خصم 1,000 جنيه إضافية من حساب العميل (Double Charge)!\n\n"
            "2. الحل المعماري الإلزامي: مفتاح التكرار الفريد (Idempotency Key):\n"
            "   - قبل إرسال أول طلب، التطبيق يولد **UUID فريد خاص بهذه المعاملة** (`idempotencyKey = UUID.randomUUID().toString()`).\n"
            "   - يحفظ هذا المفتاح فوراً في قاعدة البيانات المحلية (Room DB) مع حالة المعاملة `PENDING`.\n"
            "   - يرسل الـ Header في طلب الـ HTTP: `X-Idempotency-Key: <UUID>`.\n"
            "   - السيرفر وبوابة الدفع (مثل Stripe) يحتفظان بالمفتاح في الـ Cache/Database. لو وصلهم نفس الـ Key مرة ثانية أثناء الـ Retry، **لن يقوموا بخصم المبلغ مرة أخرى**؛ بل سيعيدون نتيجة المعاملة الأولى فوراً!"
        ),
        "practical_walkthrough": (
            "تنفيذ دورة حياة عملية دفع آمنة ضد التكرار (Idempotent Payment):\n"
            "```kotlin\n"
            "suspend fun executePayment(orderId: String, amount: BigDecimal): PaymentResult {\n"
            "    // 1. توليد أو استرجاع مفتاح التكرار المخزن محلياً لهذه المعاملة:\n"
            "    val transaction = paymentDao.getOrCreateTransaction(orderId) {\n"
            "        PaymentEntity(orderId = orderId, idempotencyKey = UUID.randomUUID().toString())\n"
            "    }\n"
            "    \n"
            "    // 2. إرسال الطلب مع المفتاح وإعادة المحاولة بأمان:\n"
            "    return try {\n"
            "        val response = paymentApi.charge(\n"
            "            idempotencyKey = transaction.idempotencyKey,\n"
            "            request = ChargeRequest(orderId, amount)\n"
            "        )\n"
            "        paymentDao.markSuccess(transaction.id, response.receiptId)\n"
            "        PaymentResult.Success(response.receiptId)\n"
            "    } catch (e: SocketTimeoutException) {\n"
            "        // 3. عند حدوث Timeout، لا نكرر الخصم عشوائياً؛ نستعلم عن حالة المعاملة أولاً:\n"
            "        reconcilePaymentStatus(transaction.idempotencyKey)\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Generate a unique client-side Idempotency Key (UUID) persisted locally before making the payment request, and pass it in the HTTP header (e.g., X-Idempotency-Key). On network timeout, retrying with the same idempotency key instructs the server and payment gateway to deduplicate the transaction and return the original receipt rather than charging twice.",
        "best_answer": (
            "A payment timeout is the classic distributed systems challenge: the client cannot distinguish whether the request timed out before reaching the server, while being processed, or while the response was returning over the air. Retrying blindly risks catastrophic duplicate charges.\n\n"
            "The industry-standard solution is **Idempotency Keys** paired with local persistence:\n\n"
            "1. Before dispatching the payment request, the Android app generates a cryptographically unique UUID as an idempotency key and persists it locally in Room alongside the order ID.\n"
            "2. The app sends this key in the request header (e.g., `X-Idempotency-Key: <uuid>`).\n"
            "3. The backend and payment gateway (like Stripe or Adyen) check their distributed transaction store. If a request with that key was already executed, they return the original processed receipt without re-executing the charge.\n"
            "4. If a timeout occurs, the app doesn't immediately prompt the user to re-pay. It performs a status reconciliation query (`GET /payments/status?key=<uuid>`) to check if the transaction succeeded before triggering any retries."
        ),
        "deep_answer": (
            "From an architectural resiliency standpoint, payment flows must never rely solely on transient UI state or a simple `viewModelScope.launch` retry loop. "
            "If the user loses network connectivity or kills the application during a payment timeout, an in-memory retry mechanism is lost forever.\n\n"
            "To make payments robust: "
            "1. We model payments as a local state machine in Room: `CREATED -> SUBMITTED -> SETTLED | FAILED`. "
            "2. Upon a timeout, we dispatch an idempotent status check using WorkManager with exponential backoff constraints. Even if the process dies or the device is rebooted, WorkManager queries the backend to determine if the charge succeeded, updating the local database when connectivity is restored.\n\n"
            "Finally, UI UX must guard against double-clicks by immediately disabling the 'Pay' button and enforcing a single submission token, preventing the user from triggering two parallel payment coroutines."
        ),
        "follow_ups": [
            {
                "interviewer": "What if the backend does not support idempotency keys?",
                "answer": "You must implement a two-phase check: first, call a payment intent or reservation endpoint that issues a server-side transaction ID with an expiration window. All subsequent charge or query requests reference this reservation ID."
            },
            {
                "interviewer": "How does WorkManager help in payment recovery?",
                "answer": "WorkManager guarantees execution across process death and device reboots. If a payment request times out and the user closes the app, a periodic or one-time WorkManager task reconciles payment status with the server in the background and posts a notification when confirmed."
            },
            {
                "interviewer": "Why shouldn't you generate the Idempotency Key in-memory in the ViewModel?",
                "answer": "Because if the Android OS kills the process due to low memory while the request is in flight, recreating the ViewModel will generate a brand-new UUID. Retrying with a new UUID would defeat idempotency and charge the customer twice."
            }
        ]
    },
    {
        "id": "COR-28",
        "arabic_explanation": (
            "هذا السؤال عملي ويتطلب إظهار الـ Race Condition في الكود وإصلاحه بأكثر من طريقة صحيحة:\n\n"
            "1. المشكلة بالكود (Demonstrating the Race Condition):\n"
            "   - كود بيحدث رصيد حساب مشترك من 2 coroutines بالتوازي على `Dispatchers.Default`:\n"
            "   ```kotlin\n"
            "   var balance = 0\n"
            "   coroutineScope {\n"
            "       launch(Dispatchers.Default) { repeat(10_000) { balance++ } }\n"
            "       launch(Dispatchers.Default) { repeat(10_000) { balance++ } }\n"
            "   }\n"
            "   println(balance) // النتيجة لن تكون 20,000 أبداً! ستكون مثلاً 13,450!\n"
            "   ```\n"
            "   - السبب: `balance++` ليست عملية ذرية (Not atomic). تتكون من قراءة القيمة من الذاكرة، زيادتها، ثم حفظها. التبديل بين الخيوط يسبب الكتابة فوق القيمة وضياع العمليات.\n\n"
            "2. الحلول الصحيحة (The Fixes):\n"
            "   - **الحل 1 (Atomic Types - الأسرع):** استخدام `AtomicInteger` و `incrementAndGet()`.\n"
            "   - **الحل 2 (Coroutines Mutex - للعمليات المعقدة والـ Suspend):** استخدام `Mutex` مع `mutex.withLock { balance++ }`.\n"
            "   - **الحل 3 (Thread Confinement):** حصر التنفيذ على `Dispatchers.Default.limitedParallelism(1)`."
        ),
        "practical_walkthrough": (
            "كود توضيحي متكامل يُظهر الخطأ ثم يطبّق الحل الاحترافي بـ Mutex:\n"
            "```kotlin\n"
            "class BankAccount {\n"
            "    private val mutex = Mutex()\n"
            "    var balance: Int = 0\n"
            "        private set\n"
            "\n"
            "    suspend fun deposit(amount: Int) = mutex.withLock {\n"
            "        // الدخول محمي بـ Mutex غير حاظر للخيوط:\n"
            "        val current = balance\n"
            "        delay(1) // محاكاة عملية تحقق معلقة\n"
            "        balance = current + amount\n"
            "    }\n"
            "}\n"
            "\n"
            "// في الاختبار أو التنفيذ:\n"
            "val account = BankAccount()\n"
            "coroutineScope {\n"
            "    launch(Dispatchers.Default) { repeat(100) { account.deposit(10) } }\n"
            "    launch(Dispatchers.Default) { repeat(100) { account.deposit(10) } }\n"
            "}\n"
            "assertEquals(2000, account.balance) // ينجح بنسبة 100% دائماً\n"
            "```"
        ),
        "quick_answer": "When two coroutines update a shared var balance concurrently on multi-threaded dispatchers, non-atomic read-modify-write operations cause lost updates. Fix it using an AtomicInteger for simple numbers, a coroutine Mutex (withLock) for suspending critical sections, or single-threaded confinement via limitedParallelism(1).",
        "best_answer": (
            "To demonstrate the race condition:\n\n"
            "```kotlin\n"
            "var balance = 0\n"
            "coroutineScope {\n"
            "    launch(Dispatchers.Default) { repeat(10_000) { balance++ } }\n"
            "    launch(Dispatchers.Default) { repeat(10_000) { balance++ } }\n"
            "}\n"
            "// balance will be far less than 20,000 due to race conditions!\n"
            "```\n\n"
            "The operation `balance++` breaks into three assembly instructions: read value, increment, and write back. When executed concurrently across worker threads on `Dispatchers.Default`, Thread B overwrites Thread A's updates.\n\n"
            "To fix it, we have three production strategies depending on the use case:\n"
            "1. **AtomicInteger** for primitive counters: `val balance = AtomicInteger(0); balance.addAndGet(amount)`. This is lock-free and resolved in CPU hardware.\n"
            "2. **Kotlin Mutex** when suspension is involved: protect the mutation with `mutex.withLock { balance += amount }`. Mutex suspends non-blockingly without starving worker threads.\n"
            "3. **Thread Confinement**: confine the balance update to a sequential dispatcher: `withContext(Dispatchers.Default.limitedParallelism(1)) { balance += amount }`."
        ),
        "deep_answer": (
            "From a performance and benchmarking perspective: "
            "1. `AtomicInteger` executes millions of operations per second with zero garbage collection churn and zero context switching because it uses atomic Compare-And-Swap (CAS) CPU instructions. It is the fastest possible fix for simple counters. "
            "2. `Mutex` adds object allocation overhead (`LockContender` queues) and continuation state-machine transitions. However, if updating the balance requires calling a suspending validation function (like checking an online fraud rule or reading Room DB), `Mutex` is mandatory because atomic variables cannot protect multi-step asynchronous transactions. "
            "3. In Android UI architecture, the most idiomatic fix is immutable state management with `MutableStateFlow`:\n\n"
            "```kotlin\n"
            "private val _balance = MutableStateFlow(0)\n"
            "val balance = _balance.asStateFlow()\n"
            "\n"
            "fun deposit(amount: Int) {\n"
            "    _balance.update { current -> current + amount }\n"
            "}\n"
            "```\n\n"
            "`StateFlow.update` uses an internal CAS loop that guarantees atomic updates without locks."
        ),
        "follow_ups": [
            {
                "interviewer": "Why wouldn't you use Java's `synchronized` block to fix this?",
                "answer": "Because `synchronized` blocks the underlying operating system thread. If a suspending function is called inside the synchronized block, it will fail to compile. Even for non-suspending code, blocking pool threads degrades coroutine scheduler performance and risks UI thread ANRs."
            },
            {
                "interviewer": "Can you fix this with a thread-safe collection instead?",
                "answer": "If the shared state is a collection (like a transaction list), using `ConcurrentLinkedQueue` or `CopyOnWriteArrayList` (for read-heavy scenarios) prevents `ConcurrentModificationException` during concurrent writes."
            },
            {
                "interviewer": "What is the downside of using `limitedParallelism(1)` for high-throughput operations?",
                "answer": "Every access requires a context switch and dispatch through an event queue. Under high frequency, queue management latency will be slower than lock-free atomic CAS instructions."
            }
        ]
    },
    {
        "id": "COR-29",
        "arabic_explanation": (
            "التعامل مع مكتبة أو SDK خارجي يعمل بطريقة Blocking ولا يستجيب لإلغاء الـ Coroutines هو أحد أصعب التحديات في بيئة Android:\n\n"
            "1. المشكلة:\n"
            "   - مكتبة C++ قديمة أو SDK بلوتوث أو قراءة ديسك قديمة تنفذ استدعاء يحظر الخيط بالكامل (Blocking Call زي `socket.read()` أو `legacySdk.process()`).\n"
            "   - بما أن الكود Blocking ولا يحتوي على Suspension Points، استدعاء `job.cancel()` لن يوقفه حتى ينتهي الاستدعاء بمفرده!\n\n"
            "2. الحلول الهندسية المتاحة (Engineering Solutions):\n"
            "   - **الحل 1 (عزل الـ Blocking على Dispatchers.IO):** تشغيل الكود دائماً على `Dispatchers.IO` لضمان عدم تجميد الـ UI Thread إطلاقاً، واستخدام `runInterruptible`.\n"
            "   - **الحل 2 (`runInterruptible`):** مكتبة كوتلن توفر `runInterruptible(Dispatchers.IO) { blockingCall() }`. هذه الدالة تقوم بعمل `Thread.interrupt()` للـ OS Thread عند إلغاء الـ Coroutine. لو الـ SDK يستجيب للـ Thread Interruption (زي معظم Java I/O)، سيتوقف ويرمي `InterruptedException` فوراً!\n"
            "   - **الحل 3 (إغلاق الـ Underlying Resource بالقوة):** لو الـ SDK لا يستجيب حتى للـ Interruption، الحل الوحيد هو إغلاق الـ Resource الذي ينتظره من الخارج (زي `socket.close()` أو `stream.close()`) عبر `continuation.invokeOnCancellation { socket.close() }`."
        ),
        "practical_walkthrough": (
            "تطبيق عملي باستخدام `runInterruptible` وإغلاق المورد:\n"
            "```kotlin\n"
            "suspend fun downloadLargeFile(url: URL, destination: File) = withContext(Dispatchers.IO) {\n"
            "    // runInterruptible ترسل Thread.interrupt() للـ thread الحابس عند إلغاء الـ coroutine:\n"
            "    runInterruptible {\n"
            "        url.openStream().use { input ->\n"
            "            destination.outputStream().use { output ->\n"
            "                input.copyTo(output) // Blocking Java I/O استدعاء\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "}\n"
            "\n"
            "// في حالة Socket خارجي لا يدعم interruption:\n"
            "suspend fun readFromRawSocket(socket: Socket): ByteArray = suspendCancellableCoroutine { continuation ->\n"
            "    continuation.invokeOnCancellation {\n"
            "        try { socket.close() } catch (ignored: Exception) {} // إغلاق المقبس يكسر الـ Blocking read فوراً\n"
            "    }\n"
            "    // تنفيذ القراءة في الخلفية...\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Wrap the blocking call in 'runInterruptible(Dispatchers.IO)', which issues a thread interrupt (Thread.interrupt()) to the underlying worker thread upon coroutine cancellation. If the SDK ignores thread interruption, close the underlying socket or resource via invokeOnCancellation to forcibly abort the blocking read.",
        "best_answer": (
            "When integrating a third-party SDK with blocking Java or native calls that do not cooperate with coroutine cancellation, we apply a multi-tier containment strategy:\n\n"
            "First, isolate the call onto `Dispatchers.IO` so it never blocks the main thread or compute worker pools.\n\n"
            "Second, wrap the execution inside **`runInterruptible(Dispatchers.IO) { ... }`**. When the coroutine is cancelled, `runInterruptible` issues a standard Java `Thread.interrupt()` to the executing worker thread. If the legacy SDK is blocked on standard Java I/O or sleep, it immediately throws an `InterruptedException` or closes the channel, cleanly aborting execution.\n\n"
            "Third, if the SDK uses uninterruptible I/O (like legacy blocking sockets or native C++ loops), we close the underlying resource from the outside: register an `invokeOnCancellation { socket.close() }` hook. Closing the socket or file descriptor forcibly breaks the blocking read and releases the thread."
        ),
        "deep_answer": (
            "Under the hood, `runInterruptible` tracks the executing JVM `Thread` reference. When cancellation occurs, it calls `thread.interrupt()`. However, developers must understand that some blocking operations are completely uninterruptible at the OS level (e.g., waiting on un-interruptible locks or native JNI system calls that do not check POSIX signals).\n\n"
            "If an external C++ or legacy Java library is completely unresponsive to both interruption and resource closing, that worker thread is effectively 'zombie-locked' until the operation completes or times out. "
            "In this worst-case scenario: "
            "1. We run the operation on a dedicated, isolated thread pool created via `Executors.newSingleThreadExecutor().asCoroutineDispatcher()`, preventing it from polluting and exhausting the shared `Dispatchers.IO` pool. "
            "2. We use `withTimeoutOrNull` around the caller continuation to allow our application to proceed and ignore the leaked thread until it eventually terminates."
        ),
        "follow_ups": [
            {
                "interviewer": "Why does `Thread.interrupt()` work with `runInterruptible` but not standard `launch`?",
                "answer": "Standard `launch` only sets internal Job cancellation flags; it never touches the underlying OS thread. `runInterruptible` explicitly links the coroutine cancellation signal to Java's `Thread.interrupt()` mechanism."
            },
            {
                "interviewer": "What happens to the thread if an uninterruptible blocking call never finishes?",
                "answer": "The OS worker thread remains blocked and leaked. If this happens repeatedly on `Dispatchers.IO`, you will eventually exhaust the 64-thread pool limit, starving all other I/O operations in the application."
            },
            {
                "interviewer": "Can you kill a thread running a blocking call in Android?",
                "answer": "No. The JVM deprecated `Thread.stop()` decades ago because it causes memory corruption and leaves monitors unlocked. You cannot forcibly kill a thread; you can only interrupt it or close its underlying file/socket handles."
            }
        ]
    },
    {
        "id": "COR-30",
        "arabic_explanation": (
            "السؤال عن اختفاء الـ ViewModel مع ضرورة إتمام عملية حفظ حرجة (Critical Persistence) هو اختبار مباشر للـ Architecture Ownership في Android:\n\n"
            "1. المشكلة:\n"
            "   - المستخدم كتب بيانات مهمة وضغط 'حفظ ومغادرة'. الشاشة قفلت فوراً والـ ViewModel تم تدميره واستدعى `onCleared()`.\n"
            "   - لو عملية الحفظ كانت شغالة في `viewModelScope.launch`، **ستُلغى العملية فوراً**، وتضيع بيانات المستخدم ويتلف مسار العمل!\n\n"
            "2. من الذي يجب أن يمتلك هذه العملية (Who should own this work)?\n"
            "   - **الـ ViewModel لا يمتلكها!** الـ ViewModel يمتلك فقط العمليات المرتبطة بعرض الشاشة الحالية.\n"
            "   - **الخيار الأول (عمليات سريعة في الذاكرة / Room Database):** يمتلكها **Application-Level CoroutineScope** محقون في الـ Repository. التطبيق حي، والـ Repository يكمل حفظ البيانات في Room حتى بعد موت الشاشة.\n"
            "   - **الخيار الثاني (عمليات حيوية يجب أن تكتمل حتى لو قفل التطبيق أو مات الـ Process):** يمتلكها **WorkManager**. WorkManager يضمن إرسال البيانات للسيرفر حتى لو النظام قتل التطبيق لتوفير الذاكرة أو أعاد تشغيل الهاتف."
        ),
        "practical_walkthrough": (
            "التصميم المعماري الاحترافي المعتمد من Google:\n"
            "```kotlin\n"
            "@Singleton\n"
            "class UserRepository @Inject constructor(\n"
            "    private val userDao: UserDao,\n"
            "    private val api: UserApi,\n"
            "    @ApplicationScope private val externalScope: CoroutineScope // Scope حي مع التطبيق\n"
            ") {\n"
            "    \n"
            "    suspend fun saveUserProfile(profile: UserProfile) {\n"
            "        // نطلق الحفظ داخل externalScope حتى لا يلغى بموت الـ ViewModel:\n"
            "        externalScope.launch {\n"
            "            userDao.insert(profile.toEntity()) // يكتمل 100% حتى لو المستخدم خرج من الشاشة\n"
            "        }.join() // نعلق الـ ViewModel الحالي ليرى النتيجة لو كان ما زال حياً\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "The ViewModel must NOT own critical persistence because viewModelScope cancels on onCleared(). Quick local persistence should be owned by an application-level CoroutineScope injected into the Repository layer, while critical remote uploads that must survive process death must be delegated to WorkManager.",
        "best_answer": (
            "Critical persistence must never be owned by the ViewModel. When a user navigates away or presses the back button, the ViewModel is destroyed and its `viewModelScope` cancels immediately, aborting any active database transactions or network dispatches.\n\n"
            "The ownership belongs in the Data/Repository layer using one of two mechanisms based on durability requirements:\n\n"
            "1. **In-Process Operations (Local Room DB writes or analytics):** An **Application-Level CoroutineScope** injected into the Repository. By configuring this scope with `SupervisorJob() + Dispatchers.IO` as an application-level singleton in Dagger/Hilt, the coroutine continues executing to completion even after the calling ViewModel is garbage collected.\n\n"
            "2. **Guaranteed Operations (Surviving process death & reboots):** If the work involves syncing an order or uploading photos that must complete even if the user swipes the app away from recents or the OS kills the process under low memory, it must be delegated to **WorkManager**. WorkManager persists the job in SQLite and guarantees execution with constraints."
        ),
        "deep_answer": (
            "Architecturally, this adheres to the principle of scoping work to the lifecycle of the data, not the lifecycle of the UI. "
            "In Hilt, we provide the application scope as follows:\n\n"
            "```kotlin\n"
            "@Provides\n"
            "@Singleton\n"
            "@ApplicationScope\n"
            "fun provideAppCoroutineScope(): CoroutineScope =\n"
            "    CoroutineScope(SupervisorJob() + Dispatchers.Default)\n"
            "```\n\n"
            "Inside the repository, we use the pattern of starting the work on the `externalScope` and awaiting it with `join()`:\n\n"
            "```kotlin\n"
            "suspend fun saveOrder(order: Order) {\n"
            "    externalScope.launch(Dispatchers.IO) {\n"
            "        database.orderDao().insert(order)\n"
            "    }.join()\n"
            "}\n"
            "```\n\n"
            "This pattern has a major architectural advantage: if the ViewModel remains alive, `join()` suspends so the UI can show a loading spinner and transition upon completion. But if the ViewModel is destroyed, only the caller continuation is cancelled; the launched job on `externalScope` continues running independently until completion."
        ),
        "follow_ups": [
            {
                "interviewer": "Why not use `NonCancellable` context inside `viewModelScope` instead of an ApplicationScope?",
                "answer": "Writing `withContext(NonCancellable)` inside `viewModelScope` delays cancellation for that specific block, but it keeps the ViewModel in memory until completion and is fragile. If the entire process is cleared or multiple operations queue up, relying on a dead ViewModel's scope is an architectural anti-pattern."
            },
            {
                "interviewer": "How does WorkManager handle network constraints compared to coroutines?",
                "answer": "WorkManager leverages the Android JobScheduler system daemon to defer task execution until exact device constraints are met (e.g., unmetered Wi-Fi connection, battery not low, device idle), which coroutines in an active process cannot do."
            },
            {
                "interviewer": "How do you test a repository that uses an injected application CoroutineScope?",
                "answer": "In your unit test, inject a `TestScope` as the `@ApplicationScope`. Call `testScope.advanceUntilIdle()` to deterministically assert that background persistence completed."
            }
        ]
    },
    {
        "id": "COR-31",
        "arabic_explanation": (
            "بدء Coroutine على `Dispatchers.Main` واستدعاء مكتبة تعمل بنظام Blocking وحدوث ANR هو السيناريو الكلاسيكي لأخطاء الـ Main Thread في Android:\n\n"
            "1. تحليل العطل الدقيق (The Exact Failure Mechanism):\n"
            "   - `Dispatchers.Main` مربوط بالـ `Looper.getMainLooper()` والـ `Handler` الخاص بالـ UI Thread.\n"
            "   - عندما تبدأ Coroutine على Main وتستدعي دالة Blocking من مكتبة خارجية (مثل `legacyCrypto.hash()` أو `file.readBytes()` أو `Thread.sleep()`):\n"
            "   - الـ Coroutine **لا تُعلّق (Does NOT suspend)**؛ بل تحظر خيط الـ Main Thread بالكامل (Blocks OS Main Thread)!\n"
            "   - الـ Main Thread يتوقف عن معالجة رسائل الـ `Choreographer` المسؤولة عن رسم الشاشة (Rendering frames)، ويتوقف عن معالجة أحداث اللمس (Input events).\n"
            "   - بعد 5 ثوانٍ من عدم الاستجابة، يتدخل نظام أندرويد ويعرض للمستخدم نافذة: **'Application Not Responding (ANR)'** ويطلب إغلاق التطبيق بالقوة.\n\n"
            "2. الإصلاح الدقيق (The Fix):\n"
            "   - نقل الاستدعاء الـ Blocking فوراً من الـ Main Thread إلى `Dispatchers.IO` (لو كان I/O) أو `Dispatchers.Default` (لو كان CPU math) عبر دالة **`withContext`**.\n"
            "   - بذلك تصبح الدالة **Main-Safe**، ويظل الـ Main Thread حراً لرسم الشاشة بسلاسة تامة."
        ),
        "practical_walkthrough": (
            "الكود الفاشل وإصلاحه المعماري:\n"
            "```kotlin\n"
            "// ❌ الكود المسبب للـ ANR:\n"
            "fun onProcessClicked() {\n"
            "    viewModelScope.launch(Dispatchers.Main) {\n"
            "        _uiState.value = UiState.Loading\n"
            "        // كارثة: مكتبة تحظر الـ Thread لمدة 6 ثوانٍ على الـ Main Thread:\n"
            "        val key = LegacyCryptoLib.generateRsaKeySync(4096) // ANR CRASH!\n"
            "        _uiState.value = UiState.Success(key)\n"
            "    }\n"
            "}\n"
            "\n"
            "// ✅ الإصلاح السليم بتحقيق Main-Safety:\n"
            "fun onProcessClicked() {\n"
            "    viewModelScope.launch(Dispatchers.Main) {\n"
            "        _uiState.value = UiState.Loading\n"
            "        // ننقل الحسابات الثقيلة لـ Dispatchers.Default باستخدام withContext:\n"
            "        val key = withContext(Dispatchers.Default) {\n"
            "            LegacyCryptoLib.generateRsaKeySync(4096) // يعمل في الخلفية بدون أي تأثير على UI\n"
            "        }\n"
            "        // نعود لـ Main Thread تلقائياً لتحديث الـ UI:\n"
            "        _uiState.value = UiState.Success(key)\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "The failure occurs because calling synchronous blocking code on Dispatchers.Main halts the Android UI Looper message queue, preventing Choreographer frame rendering and touch dispatch, triggering an ANR after 5 seconds. Fix it by offloading the blocking call to withContext(Dispatchers.Default) or withContext(Dispatchers.IO) to restore Main-Safety.",
        "best_answer": (
            "The exact failure mechanism is thread starvation on the Android UI Looper.\n\n"
            "`Dispatchers.Main` executes directly on Android's Main Looper thread. Marking a function as a coroutine does not change how synchronous code runs. When the coroutine executes a synchronous blocking call from a third-party library (like heavy cryptography or disk reading), it monopolizes the operating system main thread.\n\n"
            "Because the main thread is blocked, Android's `Choreographer` cannot process VSYNC pulses to draw 60/120Hz frames, and the `InputDispatcher` cannot dispatch user touch events. If an input event goes unhandled for 5 seconds, the OS flags an Application Not Responding (ANR) error and prompts the user to force-close the app.\n\n"
            "The definitive fix is enforcing **Main-Safety**: wrap the blocking library invocation inside `withContext(Dispatchers.Default)` for CPU-bound computations or `withContext(Dispatchers.IO)` for blocking I/O. The coroutine suspends, yields the main thread to the Android message queue so the UI remains fluid, executes the blocking code on a background worker thread, and seamlessly resumes on Main with the result."
        ),
        "deep_answer": (
            "From a performance monitoring and diagnostic perspective, identifying these bottlenecks in production requires strict tooling. "
            "In debug builds, we enable **StrictMode**:\n\n"
            "```kotlin\n"
            "StrictMode.setThreadPolicy(\n"
            "    StrictMode.ThreadPolicy.Builder()\n"
            "        .detectDiskReads()\n"
            "        .detectDiskWrites()\n"
            "        .detectCustomSlowCalls()\n"
            "        .penaltyLog()\n"
            "        .penaltyDeathOnNetwork()\n"
            "        .build()\n"
            ")\n"
            "```\n\n"
            "StrictMode immediately logs a red flash or crashes the app in debug builds if disk or network I/O touches the main thread.\n\n"
            "In production APM monitoring, we track **ANR Watchdog traces** and Google Play Console vitals. When inspecting an ANR trace file (`traces.txt`), a blocked coroutine on Main will show the main thread in the `BLOCKED` or `RUNNABLE` state stuck in the third-party library method frame rather than in `MessageQueue.nativePollOnce()`. Offloading that exact stack frame via `withContext` completely resolves the ANR."
        ),
        "follow_ups": [
            {
                "interviewer": "Why doesn't `suspend` automatically prevent this ANR?",
                "answer": "Because `suspend` is only a compiler marker for non-blocking suspension points. If the code inside the suspend function invokes a blocking Java or native call without switching dispatchers via withContext, it executes synchronously on the caller's thread."
            },
            {
                "interviewer": "How do you detect slow frame drops (Jank) before they become full ANRs?",
                "answer": "Using Android's `JankStats` library or Firebase Performance Monitoring to monitor dropped frames (jank occurs when a frame takes longer than 16.6ms at 60Hz or 8.3ms at 120Hz to render)."
            },
            {
                "interviewer": "Should repository methods be responsible for `withContext` or should the ViewModel handle it?",
                "answer": "The repository must be responsible. Following the Main-Safety design guideline, all public suspend functions exposed by repositories must internally guarantee that they can be safely called from Dispatchers.Main."
            }
        ]
    },
    {
        "id": "COR-32",
        "arabic_explanation": (
            "اختبار التزامن والإلغاء والمهلات الزمنية (Cancellation, Supervision, and Timeouts) بشكل حتمي وموثوق (Deterministically) بدون استخدام `Thread.sleep` هو جوهر اختبارات الـ Unit Tests الحديثة في Kotlin:\n\n"
            "1. المشكلة في اختبارات الـ Concurrency التقليدية:\n"
            "   - استخدام `Thread.sleep(1000)` يجعل الاختبارات بطيئة جداً، والأخطر: يجعلها غير مستقرة (Flaky Tests)؛ لأن توقيت الـ CPU على سيرفرات الـ CI/CD قد يتأخر بضع أجزاء من الثانية فيفشل الاختبار عشوائياً!\n\n"
            "2. الحل القياسي: `kotlinx-coroutines-test` و `runTest`:\n"
            "   - **`runTest`**: توفر بيئة اختبار ذات وقت افتراضي (Virtual Time) يتم تخطيه فوراً.\n"
            "   - **`StandardTestDispatcher`**: لا ينفذ المهام فوراً؛ بل يضعها في طابور انتظار، مما يتيح لك التحكم الدقيق في وقت التنفيذ خطوة بخطوة.\n\n"
            "3. التحكم في الوقت والمهام:\n"
            "   - `advanceTimeBy(timeMillis)`: تقديم عقارب الساعة الافتراضية بمقدار محدد (لاختبار الـ Timeouts و delay).\n"
            "   - `advanceUntilIdle()`: تنفيذ كل المهام المعلقة في الطابور حتى يفرغ تماماً.\n"
            "   - `runCurrent()`: تنفيذ المهام الجاهزة للتنفيذ في الوقت الحالي فقط."
        ),
        "practical_walkthrough": (
            "كتابة Unit Test كامل يختبر Timeout و Cancellation بشكل حتمي 100%:\n"
            "```kotlin\n"
            "@Test\n"
            "fun `fetchWithTimeout aborts and returns fallback when time exceeds 2 seconds`() = runTest {\n"
            "    // محاكاة استدعاء API يستغرق 3 ثوانٍ في الوقت الافتراضي:\n"
            "    val fakeApi = FakeApi(delayMs = 3_000L)\n"
            "    val repository = Repository(fakeApi, testScheduler)\n"
            "\n"
            "    // نطلق العملية التي بداخلها withTimeoutOrNull(2000):\n"
            "    val resultDeferred = async { repository.fetchWithTimeout() }\n"
            "\n"
            "    // نقدم الوقت بمقدار ثانية واحدة (العملية لا زالت تعمل):\n"
            "    advanceTimeBy(1_000L)\n"
            "    assertTrue(resultDeferred.isActive)\n"
            "\n"
            "    // نقدم الوقت ثانية إضافية (تم تجاوز مهلة الـ 2000ms):\n"
            "    advanceTimeBy(1_001L)\n"
            "\n"
            "    // نتحقق من النتيجة: حصل timeout ورجع الـ fallback فوراً:\n"
            "    val result = resultDeferred.await()\n"
            "    assertEquals(FallbackData, result)\n"
            "}\n"
            "```\n"
            "لاحظ: الاختبار يستغرق 5 ميلي-ثانية فقط على الـ CI/CD بدلاً من الانتظار الحقيقي لعدة ثوانٍ!"
        ),
        "quick_answer": "Use 'kotlinx-coroutines-test' with 'runTest' and 'StandardTestDispatcher'. Virtual time skipping with advanceTimeBy() tests timeouts instantly and deterministically without Thread.sleep(), while advanceUntilIdle() flushes queued tasks, completely eliminating test flakiness.",
        "best_answer": (
            "To test concurrent cancellation, supervision, and timeouts deterministically, I use the modern `kotlinx-coroutines-test` framework with `runTest`.\n\n"
            "The key architectural mechanism is **Virtual Time Control**. `runTest` provides a `TestScope` backed by a `StandardTestDispatcher` and a `TestCoroutineScheduler`. Instead of sleeping real OS threads with `Thread.sleep()`—which causes slow, flaky tests on CI—virtual time skips delays instantaneously while preserving execution order.\n\n"
            "To test timeouts: I configure the mock operation with a simulated delay (e.g., `delay(5000)`), call `advanceTimeBy(5001)`, and assert that `TimeoutCancellationException` was thrown or the timeout fallback executed.\n\n"
            "To test cancellation and supervision: I inject `testDispatcher` into my components, launch child coroutines, simulate an exception in one child, call `runCurrent()`, and assert that supervised siblings remain active while unsupervised hierarchies cancel appropriately."
        ),
        "deep_answer": (
            "Under the hood, `StandardTestDispatcher` does not execute scheduled coroutines immediately upon builder invocation. Instead, it queues tasks into the `TestCoroutineScheduler`. "
            "This gives developers three surgical levers of control: "
            "1. `runCurrent()`: Executes all scheduled tasks that are ready to run at the current virtual timestamp. "
            "2. `advanceTimeBy(millis)`: Advances the virtual clock, triggering any delayed tasks or timeouts scheduled within that window. "
            "3. `advanceUntilIdle()`: Continuously drains all pending tasks until the scheduler queue is completely empty.\n\n"
            "When testing Android ViewModels that reference `Dispatchers.Main`, you must register a `MainDispatcherRule` (a JUnit TestRule) that invokes `Dispatchers.setMain(testDispatcher)` in `@Before` and `Dispatchers.resetMain()` in `@After`.\n\n"
            "Finally, `runTest` includes an automatic uncaught exception detector: if any coroutine in the test scope fails with an unhandled exception, `runTest` fails the test automatically at the end of the block, preventing swallowed background crashes."
        ),
        "follow_ups": [
            {
                "interviewer": "What is the difference between `StandardTestDispatcher` and `UnconfinedTestDispatcher`?",
                "answer": "`StandardTestDispatcher` queues tasks and requires explicit advancement via `runCurrent()` or `advanceUntilIdle()`, giving full control over execution interleaving. `UnconfinedTestDispatcher` eagerly executes new coroutines immediately until their first suspension point, which is convenient for simple sequential tests."
            },
            {
                "interviewer": "Why must you use `Dispatchers.setMain` in unit tests?",
                "answer": "Because `Dispatchers.Main` relies on Android's `Looper.getMainLooper()`, which does not exist in local JVM unit tests and throws an IllegalStateException unless replaced with a TestDispatcher."
            },
            {
                "interviewer": "What happens if a coroutine launched in `runTest` never completes?",
                "answer": "`runTest` has a default 60-second real-time timeout. If an unfinished coroutine remains active (e.g., a leaked infinite loop or unclosed flow collection), `runTest` fails with an UncompletedCoroutinesError."
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

    for q in COR_26_32:
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
    print(f"Updated {DATA_FILE} with questions COR-26 to COR-32. Total questions: {len(combined)}")


if __name__ == "__main__":
    main()
