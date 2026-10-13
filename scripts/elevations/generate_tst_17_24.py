#!/usr/bin/env python3
"""Generator for TST-17 through TST-24 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "tst.json"

TST_17_24 = [
    {
        "id": "TST-17",
        "arabic_explanation": (
            "ما هي اختبارات لقطات الشاشة (Screenshot Tests)، والـ Baseline Profiles، واختبارات الـ Macrobenchmark في معايير الجودة الحديثة؟\n\n"
            "1. اختبارات لقطات الشاشة (Screenshot / Visual Regression Tests):\n   - **فكرتها**: التقاط صورة بكسل-ببكسل (PNG) لكل مكون Composable أو شاشة، ومقارنتها بصورة معتمدة سابقة (Golden Image).\n   - **الميزة**: تكشف أي تشوه بصري غير مقصود (مثل تداخل النصوص، اختفاء مسافات الـ Padding، أو أخطاء في الـ Dark Mode وتكبير الخطوط).\n   - **المكتبات الرائدة**: **Roborazzi** (تعمل بسرعة فائقة على الـ JVM المحلي عبر Robolectric)، و **Paparazzi**، و **Shot**.\n\n"
            "2. ما هي الـ Baseline Profiles؟\n   - ملفات قواعد يتم توليدها آلياً تحدد الكلاسات والدوال الأكثر استخداماً في مسارات فتح التطبيق الحرجة (Critical User Journeys).\n   - يقوم نظام Android OS عند تثبيت التطبيق بتجميع هذه الدوال مسبقاً (Ahead-Of-Time - AOT)، مما **يسرع زمن فتح التطبيق (Cold Start) بنسبة تصل إلى 40% ويقضي على الـ Jank** في أول تجربة للمستخدم!\n\n"
            "3. اختبارات الـ Macrobenchmark:\n   - اختبارات رسمية تعمل على أجهزة حقيقية لقياس أداء التطبيق الفعلي ككل: قياس زمن الفتح (`StartupTimingMetric`) ومعدل سلاسة الإطارات أثناء التمرير (`FrameTimingMetric`)."
        ),
        "practical_walkthrough": (
            "تنفيذ اختبار Screenshot باستخدام Roborazzi واختبار Macrobenchmark لقياس سرعة التشغيل:\n"
            "```kotlin\n"
            "// 1. اختبار Screenshot حديث باستخدام Roborazzi و Compose على الـ JVM المحلي:\n"
            "@RunWith(RobolectricTestRunner::class)\n"
            "@GraphicsMode(GraphicsMode.Mode.NATIVE)\n"
            "class PaymentCardScreenshotTest {\n"
            "    @get:Rule\n"
            "    val composeRule = createComposeRule()\n"
            "\n"
            "    @Test\n"
            "    fun paymentCard_rendersAccurately_inDarkAndLightMode() {\n"
            "        composeRule.setContent {\n"
            "            AppTheme(darkTheme = true) {\n"
            "                PaymentCard(cardNumber = \"**** 4321\", balance = \"$1,250.00\")\n"
            "            }\n"
            "        }\n"
            "\n"
            "        // التقاط لقطة الشاشة ومقارنتها تلقائياً بالصورة المرجعية المخزنة:\n"
            "        composeRule.onRoot().captureRoboImage(\"screenshots/payment_card_dark.png\")\n"
            "    }\n"
            "}\n"
            "\n"
            "// 2. اختبار Macrobenchmark لقياس زمن الـ Cold Start على جهاز حقيقي:\n"
            "@RunWith(AndroidJUnit4::class)\n"
            "class ColdStartupBenchmark {\n"
            "    @get:Rule\n"
            "    val benchmarkRule = MacrobenchmarkRule()\n"
            "\n"
            "    @Test\n"
            "    fun measureColdStartup() = benchmarkRule.measureRepeated(\n"
            "        packageName = \"com.example.app\",\n"
            "        metrics = listOf(StartupTimingMetric()),\n"
            "        iterations = 5,\n"
            "        startupMode = StartupMode.COLD\n"
            "    ) {\n"
            "        pressHome()\n"
            "        startActivityAndWait()\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Screenshot tests capture and pixel-diff rendered UI against baseline golden images to catch visual regressions. Baseline Profiles pre-compile critical execution paths at install time via AOT compilation to eliminate launch jank. Macrobenchmark tests measure real-world startup latency and scroll frame metrics on physical devices.",
        "best_answer": (
            "Modern Android reliability and performance testing relies on three specialized verification technologies:\n\n"
            "1. **Screenshot / Visual Regression Tests (Roborazzi / Paparazzi)**:\n"
            "   - Render Composables off-screen and compare output PNGs pixel-by-pixel against committed golden reference images. They catch unintended regressions in theme inheritance, text truncation across dynamic font scales, and RTL mirror alignments in seconds on the JVM.\n\n"
            "2. **Baseline Profiles**:\n"
            "   - Human-readable specifications of classes and methods compiled during app installation using Android Runtime (ART) Ahead-Of-Time (AOT) compilation. By pre-compiling critical user paths (app startup, feed scrolling), Baseline Profiles eliminate runtime JIT interpretation pauses, improving cold launch speed by 30–40%.\n\n"
            "3. **Macrobenchmark Testing**:\n"
            "   - Black-box performance testing running against non-debuggable release builds on physical hardware. Uses Android OS trace instrumentation to measure `StartupTimingMetric` (Time to Initial Display) and `FrameTimingMetric` (measuring 90th/99th percentile frame drops during fast scrolling lists)."
        ),
        "deep_answer": (
            "From an engineering platform and release infrastructure perspective, incorporating these tools requires dedicated pipeline stages:\n\n"
            "1. **CI Screenshot Differential Reporting**: When a visual regression occurs, CI should not merely fail the build. Integrate tools (like GitHub Action artifact reports) that generate an HTML visual diff carousel showing the original Golden, the Candidate, and an overlay diff highlighting mismatched pixels in red.\n\n"
            "2. **Baseline Profile Automation**: Configure AGP's Baseline Profile Gradle plugin (`androidx.baselineprofile`). Schedule automated monthly Macrobenchmark profiling runs in CI that traverse critical user journeys, generate fresh `baseline-prof.txt` rules, and commit them directly to the repository before major releases.\n\n"
            "3. **Device Requirements for Benchmarks**: Never run Macrobenchmark on standard emulators or debug builds. ART compiles debuggable builds with optimizations disabled, skewing measurements. Always execute benchmarks on real, rooted or userdebug physical devices pinned at stable thermal CPU frequencies."
        ),
        "follow_ups": [
            {
                "question": "Why is Roborazzi faster than traditional on-device screenshot testing?",
                "answer": "Roborazzi runs on the host JVM using Robolectric's native graphics engine, generating and comparing screenshots in seconds without booting an Android emulator."
            },
            {
                "question": "What is the difference between Time to Initial Display and Time to Full Display in Macrobenchmark?",
                "answer": "Initial Display measures when the first frame renders; Full Display measures when asynchronous network data completes and reportFullyDrawn() is called."
            }
        ]
    },
    {
        "id": "TST-18",
        "arabic_explanation": (
            "كيف تختبر سيناريوهات موت العملية (Process Death)، وتدوير الشاشة (Screen Rotation)، والانتقال لوضع عدم الاتصال (Offline Transitions)؟\n\n"
            "1. اختبار موت العملية (Process Death Testing):\n   - **المشكلة**: عند تشغيل التطبيق ووضعه في الخلفية، قد يقوم نظام أندرويد بقتل الـ Process لتوفير الذاكرة! عندما يعود المستخدم، يعاد بناء الـ Activity ولكن كل المتغيرات العادية في الذاكرة تصبح `null`.\n   - **طريقة الاختبار**: استخدام `SavedStateHandle` ومحاكاة موت العملية برمجياً في الاختبارات باستخدام `ActivityScenario.recreate()` أو أمر ADB:\n     `adb shell am kill <package_name>`.\n\n"
            "2. اختبار تدوير الشاشة (Configuration Changes / Rotation):\n   - التأكد من أن الـ ViewModel يحتفظ بالبيانات المحملة مسبقاً ولا يعيد طلبها من الشبكة عند تدوير الهاتف.\n   - التأكد من أن حالات واجهة Compose المحفوظة بـ `rememberSaveable` تستعيد قيمها بدقة.\n\n"
            "3. اختبار الانتقال لوضع عدم الاتصال (Offline Transition Testing):\n   - قطع الاتصال بالإنترنت أثناء استخدام المستخدم للتطبيق، والتأكد من ظهور رسالة تنبيهية للمستخدم دون انهيار، وتخزين العمليات في طابور الـ Outbox المحلي."
        ),
        "practical_walkthrough": (
            "اختبار استعادة الحالة بعد موت العملية باستخدام SavedStateHandle في Unit Test محلي:\n"
            "```kotlin\n"
            "class RegistrationViewModel(private val savedStateHandle: SavedStateHandle) : ViewModel() {\n"
            "    var email: String\n"
            "        get() = savedStateHandle.get<String>(\"key_email\") ?: \"\"\n"
            "        set(value) = savedStateHandle.set(\"key_email\", value)\n"
            "\n"
            "    var step: Int\n"
            "        get() = savedStateHandle.get<Int>(\"key_step\") ?: 1\n"
            "        set(value) = savedStateHandle.set(\"key_step\", value)\n"
            "}\n"
            "\n"
            "class ProcessDeathStateRestorationTest {\n"
            "    @Test\n"
            "    fun `state survives process death simulation via SavedStateHandle`() {\n"
            "        // 1. محاكاة الحالة قبل موت العملية:\n"
            "        val initialHandle = SavedStateHandle()\n"
            "        val viewModelBeforeDeath = RegistrationViewModel(initialHandle)\n"
            "        viewModelBeforeDeath.email = \"user@example.com\"\n"
            "        viewModelBeforeDeath.step = 2\n"
            "\n"
            "        // 2. محاكاة حفظ الحالة واستعادتها في Process جديدة تماماً:\n"
            "        val savedBundle = initialHandle.savedStateProvider().saveState()\n"
            "        val restoredHandle = SavedStateHandle.createHandle(savedBundle, null)\n"
            "\n"
            "        // 3. إنشاء ViewModel جديد في العملية المستعادة والتحقق من بقاء البيانات:\n"
            "        val viewModelAfterDeath = RegistrationViewModel(restoredHandle)\n"
            "        assertEquals(\"user@example.com\", viewModelAfterDeath.email)\n"
            "        assertEquals(2, viewModelAfterDeath.step)\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Test process death by verifying SavedStateHandle state restoration in JVM unit tests, or by calling ActivityScenario.recreate() and adb shell am kill in instrumentation tests. Test rotation by verifying ViewModels retain data without re-fetching, and test offline transitions using reactive NetworkCallback fakes.",
        "best_answer": (
            "Testing OS lifecycle edge cases verifies resilience against system memory pressure and hardware configuration shifts:\n\n"
            "1. **Testing Process Death**:\n"
            "   - **JVM Unit Testing (SavedStateHandle)**: Save a state snapshot via `savedStateHandle.savedStateProvider().saveState()`, feed the bundle into a fresh `SavedStateHandle.createHandle()`, instantiate a new ViewModel, and assert that form inputs, active step indexes, and navigation tokens survive.\n   - **On-Device Instrumentation Testing**: Use AndroidX `ActivityScenario`. Navigate through a flow, background the app, trigger process death via `adb shell am kill <package>`, bring the app foreground, and assert that the activity restores state without crashing.\n\n"
            "2. **Testing Configuration Changes (Rotation)**:\n"
            "   - In Compose tests or `ActivityScenario`, invoke `scenario.recreate()`. Assert that the screen rebinds to existing ViewModel state flows without re-triggering network fetches or resetting scroll offsets.\n\n"
            "3. **Testing Dynamic Offline Transitions**:\n"
            "   - Inject a `FakeNetworkMonitor` exposing a `Flow<Boolean>`. While collecting active UI flows, flip network availability to `false`. Assert that the UI renders an offline banner, falls back to cached Room records, and routes mutations to an internal pending outbox."
        ),
        "deep_answer": (
            "From an architectural systems perspective, handling process death exposes state boundaries:\n\n"
            "1. **Transient UI State vs. Heavy Domain State**: A frequent architectural anti-pattern is storing large domain objects (such as complete 5MB JSON lists) in `SavedStateHandle`. Android restricts the system `TransactionTooLargeException` buffer to 1MB across the entire process. Tests must assert that only lightweight restoration keys (e.g., `selectedUserId: String`, `scrollIndex: Int`) are saved to state bundles.\n\n"
            "2. **rememberSaveable Custom Savers**: In Jetpack Compose, test custom savers (`Saver<T, Any>`) by writing unit tests that serialize custom UI state objects to bundles and deserialize them, asserting object equivalence.\n\n"
            "3. **Network Flakiness Injection via OkHttp**: Rather than relying on physical airplane mode toggles in CI, inject an OkHttp interceptor into the test network client that programmatically drops connections after the 2nd request, asserting that retry queues and offline outboxes trigger reliably."
        ),
        "follow_ups": [
            {
                "question": "What is TransactionTooLargeException in Android?",
                "answer": "An exception thrown when data passed across Binder IPC (such as saved instance state or intent extras) exceeds the shared 1MB buffer limit."
            },
            {
                "question": "Why does ActivityScenario.recreate() not fully simulate process death?",
                "answer": "recreate() destroys and recreates the Activity within the same process, keeping static and singleton memory intact; real process death destroys the entire OS Linux process."
            }
        ]
    },
    {
        "id": "TST-19",
        "arabic_explanation": (
            "اكتب اختبارات وحدة (Unit Tests) لثلاث استدعاءات متزامنة في الشبكة (3 Parallel APIs) تدعم النجاح الجزئي (Partial Success) وإلغاء العمليات (Cancellation)؟\n\n"
            "1. سيناريو الاختبار المطلوب:\n   - شاشة الـ Dashboard تقوم بجلب بيانات: (1) الـ User Profile، (2) الـ Transactions، (3) الـ Exchange Rates بشكل متزامن عبر `async/await`.\n   - **سيناريو النجاح الجزئي (Partial Success)**: إذا فشلت خدمة أسعار الصرف (Exchange Rates) في الشبكة، يجب ألا يفشل الاختبار أو ينهار التطبيق؛ يجب أن تنجح بيانات الـ Profile والـ Transactions وتُعرض للمستخدم مع علامة خطأ للقسم الفاشل فقط.\n   - **سيناريو الإلغاء (Cancellation)**: إذا ألغى المستخدم العملية أو خرج من الشاشة، يجب إلغاء جميع الاستدعاءات الثلاثة فوراً في نفس اللحظة.\n\n"
            "2. كيفية الاختبار باستخدام `runTest` و `StandardTestDispatcher`:\n   - نستخدم Fakes أو Mocks لتمثيل الخدمات الثلاث، ونتحكم في وقت الاستجابة والتعليق لإثبات التزامن الحقيقي وإلغاء الـ Jobs المعلقة."
        ),
        "practical_walkthrough": (
            "كتابة كود الـ Coordinator واختبارات الـ Partial Success والـ Cancellation التام باستخدام runTest:\n"
            "```kotlin\n"
            "// 1. الكود المراد اختباره: جلب متزامن مع دعم الفشل الجزئي عبر supervisorScope:\n"
            "class DashboardAggregator(\n"
            "    private val profileApi: suspend () -> String,\n"
            "    private val ordersApi: suspend () -> List<String>,\n"
            "    private val ratesApi: suspend () -> Double\n"
            ") {\n"
            "    suspend fun loadDashboard(): DashboardResult = supervisorScope {\n"
            "        val profileDeferred = async { runCatching { profileApi() } }\n"
            "        val ordersDeferred = async { runCatching { ordersApi() } }\n"
            "        val ratesDeferred = async { runCatching { ratesApi() } }\n"
            "\n"
            "        DashboardResult(\n"
            "            profile = profileDeferred.await().getOrNull(),\n"
            "            orders = ordersDeferred.await().getOrDefault(emptyList()),\n"
            "            ratesError = ratesDeferred.await().exceptionOrNull() != null\n"
            "        )\n"
            "    }\n"
            "}\n"
            "\n"
            "// 2. اختبارات الوحدة الشاملة في JVM:\n"
            "class DashboardAggregatorTest {\n"
            "    @Test\n"
            "    fun `partial failure allows profile and orders to succeed when rates service fails`() = runTest {\n"
            "        val aggregator = DashboardAggregator(\n"
            "            profileApi = { \"Ahmed\" },\n"
            "            ordersApi = { listOf(\"Order #1\") },\n"
            "            ratesApi = { throw IOException(\"Rates service unavailable\") }\n"
            "        )\n"
            "\n"
            "        val result = aggregator.loadDashboard()\n"
            "        assertEquals(\"Ahmed\", result.profile)\n"
            "        assertEquals(1, result.orders.size)\n"
            "        assertTrue(result.ratesError)\n"
            "    }\n"
            "\n"
            "    @Test\n"
            "    fun `canceling parent job cancels all three parallel calls immediately`() = runTest {\n"
            "        var child1Cancelled = false\n"
            "        val aggregator = DashboardAggregator(\n"
            "            profileApi = { try { delay(1000); \"Done\" } finally { child1Cancelled = true } },\n"
            "            ordersApi = { delay(1000); emptyList() },\n"
            "            ratesApi = { delay(1000); 1.0 }\n"
            "        )\n"
            "\n"
            "        val job = launch { aggregator.loadDashboard() }\n"
            "        runCurrent()\n"
            "        job.cancel() // إلغاء المهمة الرئيسية\n"
            "        runCurrent()\n"
            "\n"
            "        assertTrue(\"Child coroutine must execute cancellation cleanup\", child1Cancelled)\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Test parallel APIs by wrapping concurrent async calls inside supervisorScope with runCatching to assert partial success when one dependency throws an exception. Test cancellation by launching the aggregation job, invoking job.cancel(), and asserting via finally blocks that child coroutines execute cancellation cleanup immediately.",
        "best_answer": (
            "Writing tests for concurrent multi-service aggregation requires validating both partial fault tolerance and structured cancellation boundaries:\n\n"
            "1. **Testing Partial Success (Fault Isolation)**:\n"
            "   - Implement the aggregator using `supervisorScope` so that failure in one async branch does not automatically cancel sibling branches.\n   - Configure test stubs such that Service A returns valid user data, Service B returns order records, and Service C throws `IOException(\"503 Service Unavailable\")`.\n   - Assert that the aggregated result contains populated data for Services A and B alongside an explicit typed error or empty fallback for Service C, verifying graceful UI degradation.\n\n"
            "2. **Testing Coordinated Cancellation**:\n"
            "   - Launch the aggregation call inside a parent `launch` coroutine job.\n   - Provide mock functions configured with long delays (`delay(10_000L)`) instrumented with `finally` blocks tracking cancellation flags.\n   - Advance time partially, invoke `job.cancel()`, and advance the scheduler.\n   - Assert that `job.isCancelled` becomes true and all child jobs terminate cleanly without leaking un-cancelled background coroutines."
        ),
        "deep_answer": (
            "From an advanced concurrency testing perspective, verifying thread safety and race conditions requires strict assertions:\n\n"
            "1. **Concurrent Dispatcher Stress Testing**: In addition to virtual time tests in `runTest`, run concurrent aggregation routines against `Dispatchers.Default` under multi-threaded stress tests with 100 iterations. This verifies that shared state aggregators or cache mutations do not throw `ConcurrentModificationException` when three parallel network threads complete at the exact same physical millisecond.\n\n"
            "2. **Asserting Non-Blocking Concurrency**: Assert that execution is genuinely parallel rather than sequential by measuring virtual elapsed time. If three independent APIs each take 1,000ms, the entire aggregated call must complete in exactly 1,000ms of virtual time, not 3,000ms.\n\n"
            "3. **CancellationException Preservation**: Ensure your error-handling operators (`runCatching`) do not swallow `CancellationException`. If cancellation is swallowed, cancelling the screen or leaving the view fails to abort child HTTP requests, resulting in wasted radio bandwidth."
        ),
        "follow_ups": [
            {
                "question": "What happens if you use coroutineScope instead of supervisorScope for parallel calls?",
                "answer": "If any child coroutine fails in coroutineScope, the entire scope fails immediately and cancels all other sibling coroutines."
            },
            {
                "question": "How do you verify that three async calls ran in parallel rather than sequentially?",
                "answer": "Assert that total execution virtual time equals the maximum individual call duration rather than the sum of all durations."
            }
        ]
    },
    {
        "id": "TST-20",
        "arabic_explanation": (
            "اكتب مجموعة اختبارات وحدة (Unit Tests) لمسار إعادة محاولة الدفع البنكي (Payment Retry Path) تضمن قطعياً عدم حدوث سحب مالي مزدوج (No Duplicate Charge)؟\n\n"
            "1. متطلبات الاختبار الحتمية لمعاملات الدفع:\n   - **الاختبار 1: التحقق من ثبات مفتاح الـ Idempotency**: التأكد من أن جميع محاولات إعادة الدفع لنفس الطلب ترسل نفس الـ UUID بالضبط دون توليد مفتاح جديد.\n   - **الاختبار 2: معالجة الـ Timeout والمطابقة السيرفرية (Reconciliation)**: إذا حدث انقطاع في الشبكة أثناء أول طلب، يجب أن يستعلم الاختبار عن حالة المعاملة أولاً (`GET /status`)، وإذا وجد أن السيرفر قد خصم المبلغ بنجاح، يُمنع إرسال طلب خصم ثانٍ فوراً!\n   - **الاختبار 3: حظر محاولات الخصم المتزامنة (Concurrency Lock)**: التأكد من أن الضغط السريع المتكرر على زر الدفع (Double-Tap) يُشغل معاملة واحدة فقط ويحظر الباقي.\n\n"
            "2. كيفية الإثبات في كود الاختبار:\n   - نستخدم MockWebServer أو Fake Payment API يسجل عدد طلبات الـ POST الصادرة؛ ونؤكد أن عدد طلبات الخصم الحقيقية لا يتجاوز 1 تحت أي ظرف."
        ),
        "practical_walkthrough": (
            "كتابة اختبارات وحدة صارمة تضمن عدم تكرار سحب الأموال عند حدوث Timeout أو ضغطات متكررة:\n"
            "```kotlin\n"
            "class PaymentSafetyTest {\n"
            "    @Test\n"
            "    fun `network timeout triggers reconciliation and never executes duplicate charge`() = runTest {\n"
            "        var chargeCallCount = 0\n"
            "        var reconciliationCallCount = 0\n"
            "\n"
            "        val fakePaymentApi = object : PaymentApiService {\n"
            "            override suspend fun executeCharge(idempotencyKey: String, amount: Long): ChargeResponse {\n"
            "                chargeCallCount++\n"
            "                // محاكاة سحب حقيقي على السيرفر لكن انقطعت الاستجابة قبل وصولها للموبايل:\n"
            "                throw SocketTimeoutException(\"Read timeout\")\n"
            "            }\n"
            "\n"
            "            override suspend fun reconcileStatus(idempotencyKey: String): PaymentStatusResponse {\n"
            "                reconciliationCallCount++\n"
            "                // السيرفر يؤكد أن المعاملة تم خصمها بنجاح بالفعل:\n"
            "                return PaymentStatusResponse(isAuthorized = true, transactionId = \"tx_9988\")\n"
            "            }\n"
            "        }\n"
            "\n"
            "        val coordinator = PaymentCoordinator(fakePaymentApi, FakePaymentDao())\n"
            "        val result = coordinator.payOrder(orderId = \"order_1\", amountCents = 5000)\n"
            "\n"
            "        // 1. التأكد من نجاح العملية للمستخدم بناءً على الاستعلام السيرفري:\n"
            "        assertTrue(result is PaymentResult.Success)\n"
            "        assertEquals(\"tx_9988\", (result as PaymentResult.Success).transactionId)\n"
            "\n"
            "        // 2. البرهان الحاسم: طلب الخصم تم استدعاؤه مرة واحدة فقط ولم يتكرر إطلاقاً!\n"
            "        assertEquals(1, chargeCallCount)\n"
            "        assertEquals(1, reconciliationCallCount)\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Test payment safety by asserting that all retry attempts transmit the identical UUID idempotency key, verifying that socket timeouts trigger read-only reconciliation queries rather than blind charge replays, and strictly asserting that the payment gateway charge method was invoked exactly once.",
        "best_answer": (
            "Testing payment paths requires mathematical guarantees that duplicate charges are impossible under any failure permutation:\n\n"
            "1. **Asserting Idempotency Key Stability**:\n"
            "   - Write a test verifying that when an order is created, an `idempotencyKey = UUID` is persisted locally. Assert that across multiple retry loops, crashes, and app restarts for that order ID, the captured HTTP `Idempotency-Key` header remains identical.\n\n"
            "2. **Verifying Reconciliation Over Retry**:\n"
            "   - Simulate a network socket timeout on the initial charge request. Configure the test stub to throw `SocketTimeoutException` while recording that the backend processed the charge.\n   - Assert that the client payment coordinator catches the timeout and invokes `reconcileStatus(idempotencyKey)` rather than invoking `executeCharge()` a second time.\n   - Assert that `executeCharge()` call count strictly equals 1, proving zero duplicate charges were attempted.\n\n"
            "3. **Rapid Double-Tap Concurrency Protection**:\n"
            "   - Launch two concurrent payment requests for the same order simultaneously on two parallel coroutine jobs.\n   - Assert that an internal Mutex drops or rejects the second call, and that only one charge request hits the network."
        ),
        "deep_answer": (
            "From a financial compliance and test harness perspective, payment testing requires exhaustive state space exploration:\n\n"
            "1. **Testing Database Transaction Rollbacks**: Test what happens if the local database crashes immediately before dispatching the network call. Assert that if inserting the local `PENDING` record fails, zero network calls execute, preventing untracked charges.\n\n"
            "2. **Simulating Gateway 'Unknown' Statuses**: If the reconciliation query itself times out, assert that the coordinator transitions state to `PENDING_MANUAL_VERIFICATION`. Assert that the UI renders a customer-support ticket reference and blocks the user from retrying the payment button until backend resolution confirms the order status.\n\n"
            "3. **Idempotency Header Telemetry Assertions**: Assert via MockWebServer's `takeRequest()` that outgoing charge requests pass standard payment headers: `Idempotency-Key`, `X-Client-Timestamp`, and masked audit metadata."
        ),
        "follow_ups": [
            {
                "question": "What is the single most critical assertion in a payment retry unit test?",
                "answer": "Asserting that the charge mutation call count equals exactly 1 and was not re-invoked following a network timeout."
            },
            {
                "question": "How do you test that double-clicking the payment button does not trigger parallel requests?",
                "answer": "Launch two concurrent payment coroutines simultaneously and assert that the payment API mock receives exactly one invocation."
            }
        ]
    },
    {
        "id": "TST-21",
        "arabic_explanation": (
            "اختبار ينجح دائماً على جهازك المحلي (Local Machine) ولكنه يفشل بشكل متقطع على خوادم الـ CI (Flaky Test). اشرح منهجية التشخيص والحل الجذري؟\n\n"
            "1. لماذا تفشل الاختبارات على الـ CI بينما تنجح محلياً؟\n   - **اختلاف قوة المعالجة والـ Resources**: حاسوبك يملك 8-16 Core قوية، بينما خادم الـ CI يعمل على Virtual Machine بـ 2 Cores فقط وعليها ضغط عالي؛ أي عملية تعتمد على سباق توقيت أو تأخير بسيط ستفشل على الـ CI!\n   - **اختلاف المنطقة الزمنية والـ Locale**: جهازك مضبوط على `GMT+2` بينما الـ CI مضبوط على `UTC`؛ إذا كان الكود يتعامل مع تواريخ ونصوص دون تحديد الـ Locale يدوياً، ستفشل الـ Assertions!\n   - **تشغيل الاختبارات بالتوازي (Parallel Execution)**: الـ CI يشغل أكثر من Fork في نفس الوقت، مما يسبب تنافساً على الـ Ports أو قواعد البيانات المشتركة.\n\n"
            "2. منهجية التشخيص خطوة بخطوة (Triage Protocol):\n   - **الخطوة 1: إعادة إنتاج المشكلة محلياً عبر الضغط المكثف (Stress Testing)**: تشغيل الاختبار 100 مرة متتالية محلياً:\n     `./gradlew test --tests MyFlakyTest --repeat 100`.\n   - **الخطوة 2: فحص مخرجات الـ CI**: فحص صور الشاشة وسجلات الـ Logcat وملفات الـ HTML reports الناتجة عن الفشل.\n   - **الخطوة 3: تحديد السبب الجذري**: هل هو بسبب `Thread.sleep`؟ هل هو بسبب `Dispatchers.Main`؟ هل هو بسبب الـ Timezone؟\n\n"
            "3. الحل الجذري والوقاية:\n   - استبدال أي انتظار عشوائي بـ `advanceUntilIdle()` أو Compose synchronization.\n   - تثبيت الـ Locale والـ Timezone في الـ Test Setup (`Locale.setDefault(Locale.US)`).\n   - عزل الاختبار فوراً في `@FlakyTest` لمنع تعطيل الـ PRs لحين إصلاحه."
        ),
        "practical_walkthrough": (
            "تثبيت المنطقة الزمنية واللغة في اختبارات الـ JVM وإعادة إنتاج الاختبار المتقلب محلياً:\n"
            "```bash\n"
            "# 1. أمر تشغيل الاختبار المتكرر 50 مرة محلياً لاكتشاف أخطاء التزامن الخفية:\n"
            "./gradlew testDebugUnitTest --tests \"com.example.OrderHistoryTest\" --rerun-tasks\n"
            "```\n\n"
            "```kotlin\n"
            "// 2. ضبط إعدادات الـ Locale والـ Timezone برمجياً في Test Rule لمنع تباين الـ CI:\n"
            "class DeterministicLocaleRule : TestWatcher() {\n"
            "    private val originalLocale = Locale.getDefault()\n"
            "    private val originalTimeZone = TimeZone.getDefault()\n"
            "\n"
            "    override fun starting(description: Description) {\n"
            "        Locale.setDefault(Locale.US)\n"
            "        TimeZone.setDefault(TimeZone.getTimeZone(\"UTC\"))\n"
            "    }\n"
            "\n"
            "    override fun finished(description: Description) {\n"
            "        Locale.setDefault(originalLocale)\n"
            "        TimeZone.setDefault(originalTimeZone)\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Triage flaky CI tests by reproducing locally via stress-run loops (--repeat 100), inspecting CI logcat and failure screenshots, checking for CPU throttling and timing races, standardizing Locale/TimeZone to UTC, and replacing arbitrary sleeps with deterministic coroutine TestDispatchers.",
        "best_answer": (
            "A test that passes locally but fails intermittently on CI indicates an environmental assumption or timing vulnerability:\n\n"
            "1. **Root Cause Analysis (Local vs. CI Discrepancies)**:\n"
            "   - **CPU Throttling & Core Starvation**: CI virtual runners operate on resource-constrained containers (1–2 vCPUs) under high I/O load. Operations that execute in 5ms locally take 500ms on CI, exposing uncoordinated asynchronous race conditions.\n   - **Locale & Timezone Drift**: Host developer machines run local timezones (e.g. Cairo GMT+2, US PST), while CI runs on `UTC`. Tests formatting dates or decimal numbers fail if assertions assume local time.\n   - **Parallel Execution Contamination**: Shared files or static singletons leak state when Gradle runs parallel test workers on CI.\n\n"
            "2. **Triaging Protocol**:\n"
            "   - **Stress-Run Locally**: Execute the test 100 times in a loop locally: `./gradlew test --tests MyFlakyTest --rerun-tasks`.\n   - **Inspect CI Artifacts**: Review Logcat dumps, stack traces, and emulator video recordings generated at failure time.\n\n"
            "3. **Definitive Remediation**:\n"
            "   - Replace all asynchronous timing sleeps with `StandardTestDispatcher` and Turbine.\n   - Enforce explicit `Locale.US` and `UTC` timezones inside test setup rules.\n   - Quarantine the test with a team alert ticket if immediate resolution cannot be found within 2 hours, preventing PR pipeline paralysis."
        ),
        "deep_answer": (
            "From an engineering governance and infrastructure perspective, managing flaky tests requires automated quarantine policies:\n\n"
            "1. **Automated Quarantine Gateways**: Configure CI pipelines (e.g. using TestFlaky Gradle plugins) to automatically detect tests failing intermittently without code changes. Automatically tag them as `@Quarantine`, route them to an isolated non-blocking monitoring track, and create an automated engineering ticket assigned to the owning team.\n\n"
            "2. **Emulator Snapshot & Cold Boot Stability**: For UI tests, CI emulators often flake during initial boot. Ensure CI setup scripts execute `adb wait-for-device` and check `sys.boot_completed=1` before triggering test execution.\n\n"
            "3. **Zero-Flake SLA**: Establish a team SLA: a PR cannot merge if it introduces flaky tests. High-performing engineering cultures treat a 1% flaky test rate as equivalent to a broken build because it desensitizes engineers to legitimate regressions."
        ),
        "follow_ups": [
            {
                "question": "Why does Date formatting frequently cause tests to fail on CI?",
                "answer": "Because default SimpleDateFormat formats use the machine's local TimeZone and Locale; CI machines configured to UTC mismatch developer local timezones."
            },
            {
                "question": "What is test quarantining?",
                "answer": "Moving an intermittently failing test into a separate non-blocking suite so it does not block pull requests while engineers investigate the root cause."
            }
        ]
    },
    {
        "id": "TST-22",
        "arabic_explanation": (
            "ترقية قاعدة بيانات (Room Migration) تفشل فقط عند تطبيقها على بيانات حقيقية لعملاء قدامى في الإنتاج. كيف تنشئ عينات اختبار واقعية (Realistic Fixtures) لحل المشكلة؟\n\n"
            "1. لماذا تفشل الترقيات على بيانات الإنتاج وتنجح في الاختبارات البسيطة؟\n   - في الاختبارات الأولية، يختبر المطور بيانات مثالية ونظيفة (`User(\"1\", \"Ahmed\")`).\n   - في بيانات الإنتاج الواقعية لآلاف العملاء القدامى، توجد حالات شاذة:\n     * حقول قديمة تحتوي على قيم `NULL` بينما يفرض الـ Migration الجديد `NOT NULL` بدون قيمة افتراضية!\n     * نصوص تحتوي على Emojis ورموز غير قياسية (Unicode Characters).\n     * سجلات تالفة أو مفاتيح خارجية مفقودة (Orphaned Foreign Keys) بسبب انهيارات قديمة.\n     * جداول ضخمة تحتوي على ملايين السجلات تستهلك الذاكرة وتتجاوز مهلة الـ SQLite Transaction.\n\n"
            "2. كيفية إنشاء Realistic Test Fixtures حتمية:\n   - **أخذ نسخة مشفرة ومطهرة (Anonymized & Sanitized DB Dump)**: استخراج عينة من قاعدة بيانات إنتاج قديمة، وتطهيرها من جميع البيانات الحساسة (PII) لاستخدامها كملف اختبار.\n   - **إنشاء سكريبت ملء بيانات شاذة (Dirty Data Populator)**: إدخال بيانات تحتوي على نصوص فارغة، رموز صينية، أرقام سالبة، وقيم قصوى في جدول الـ v1 قبل بدء الـ Migration.\n   - **فحص استثناء `SQLiteConstraintException`** وإصلاح الـ SQL بإضافة `DEFAULT` values أو تنظيف السجلات التالفة داخل الـ Migration نفسه."
        ),
        "practical_walkthrough": (
            "إنشاء عينة بيانات إنتاج معقدة وشاذة واختبار هجرة Room المخصصة عليها:\n"
            "```kotlin\n"
            "@RunWith(AndroidJUnit4::class)\n"
            "class RealisticCustomerMigrationTest {\n"
            "    @get:Rule\n"
            "    val helper = MigrationTestHelper(\n"
            "        InstrumentationRegistry.getInstrumentation(),\n"
            "        AppDatabase::class.java\n"
            "    )\n"
            "\n"
            "    @Test\n"
            "    fun migration2To3_handlesDirtyCustomerDataGracefully() {\n"
            "        val dbV2 = helper.createDatabase(\"dirty-data-test.db\", 2).apply {\n"
            "            // 1. إدخال بيانات غير مثالية ومطابقة لحالات الإنتاج الواقعية:\n"
            "            execSQL(\"INSERT INTO customers (id, name, legacy_email) VALUES ('c1', 'Ali 😊', NULL)\") // Legacy email is NULL!\n"
            "            execSQL(\"INSERT INTO customers (id, name, legacy_email) VALUES ('c2', '', 'user@test.com')\") // Empty name!\n"
            "            close()\n"
            "        }\n"
            "\n"
            "        // 2. تنفيذ الـ Migration الذي يضيف عمود NOT NULL:\n"
            "        // إذا لم يكن كود الـ Migration يحتوي على DEFAULT value صريح، سيفشل هذا السطر برمي SQLiteConstraintException!\n"
            "        val dbV3 = helper.runMigrationsAndValidate(\"dirty-data-test.db\", 3, true, MIGRATION_2_3)\n"
            "\n"
            "        // 3. التحقق من بقاء بيانات العميل c1 دون انهيار واستبدال الـ NULL بقيمة آمنة:\n"
            "        val cursor = dbV3.query(\"SELECT id, name, standardized_email FROM customers WHERE id = 'c1'\")\n"
            "        assertTrue(cursor.moveToFirst())\n"
            "        assertEquals(\"Ali 😊\", cursor.getString(1))\n"
            "        assertEquals(\"no-email@domain.com\", cursor.getString(2))\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Generate realistic fixtures by creating pre-migration v1 SQLite databases populated with dirty legacy data: null values in deprecated columns, Unicode/emoji strings, and orphaned keys. Test using MigrationTestHelper to ensure ALTER TABLE and copy queries handle edge cases without SQLiteConstraintExceptions.",
        "best_answer": (
            "Database migrations frequently pass clean unit tests but crash on real devices due to historical dirty data accumulated across years of app usage:\n\n"
            "1. **Production Dirty Data Realities**:\n"
            "   - Adding a `NOT NULL` column to an existing table without an explicit `DEFAULT` value fails when legacy rows exist.\n   - Historical rows with `NULL` or empty strings in fields previously unconstrained.\n   - Broken foreign keys (orphaned rows) resulting from unconstrained deletes in legacy app versions.\n   - Non-standard UTF-8 strings (emojis, RTL Arabic scripts, zero-width spaces).\n\n"
            "2. **Constructing Realistic Test Fixtures**:\n"
            "   - Use `helper.createDatabase(DB_NAME, oldVersion)` to boot the historical schema.\n   - Populate the table with adversarial edge-case fixtures: `NULL` entries, 50,000 dummy rows to test SQLite transaction memory limits, malformed timestamps, and corrupted foreign key IDs.\n\n"
            "3. **Hardening Migration Logic**:\n"
            "   - Update manual SQL migrations to scrub or sanitize dirty data inline: execute `UPDATE customers SET email = 'unknown' WHERE email IS NULL` before executing the `ALTER TABLE` statement or table-copy routine."
        ),
        "deep_answer": (
            "From an operational data integrity perspective, preventing migration crashes requires defensive SQL design:\n\n"
            "1. **Table Recreation Pattern for Complex Migrations**: SQLite versions prior to 3.35.0 do not support dropping columns. Complex migrations require: (1) creating `new_table`, (2) copying sanitized rows with `INSERT OR IGNORE INTO new_table SELECT ... FROM old_table`, (3) dropping `old_table`, and (4) renaming `new_table` to `old_table`. Test this exact 4-step sequence against dirty fixtures.\n\n"
            "2. **Sanitized Production Snapshot Testing**: For high-risk financial migrations, export an anonymized SQLite dump from an internal test account that has existed through 5 years of production upgrades. Load this real SQLite binary directly into an instrumented migration test fixture in CI.\n\n"
            "3. **Transaction Rollback Safety**: Verify that if a migration statement fails mid-script, the entire migration aborts atomically without leaving the database in an unrecoverable mixed-version schema state."
        ),
        "follow_ups": [
            {
                "question": "Why does adding a NOT NULL column without a DEFAULT fail in SQLite?",
                "answer": "Because SQLite cannot populate existing historical rows for the new column, triggering an immediate SQLiteConstraintException: Cannot add a NOT NULL column with default value NULL."
            },
            {
                "question": "What is the 12-step table recreation procedure in SQLite?",
                "answer": "The official SQLite pattern for modifying existing table structures (such as changing column constraints or types) by copying data into a newly created schema and dropping the old table."
            }
        ]
    },
    {
        "id": "TST-23",
        "arabic_explanation": (
            "كيف تضع خطة اختبار مبنية على المخاطر (Risk-Based Test Plan) لإصدار أمني حساس (Security-Sensitive Release) لتطبيق بنكي؟\n\n"
            "1. مفهوم الـ Risk-Based Testing في أندرويد:\n   - التركيز على الميزات الأكثر خطورة (High-Impact / High-Probability Areas) بدلاً من إضاعة الوقت في اختبار شاشات ثابتة.\n   - في التطبيقات المالية، المجالات الأكثر خطورة هي: **المصادقة وتخزين التوكنز، التشفير العتادي، تحويل الأموال، وحماية الذاكرة**.\n\n"
            "2. محاور خطة الاختبار الأمني الحساسة (The 4 Security Testing Pillars):\n   - **1. اختبارات الـ Cryptographic Integrity**: التحقق من أن مفاتيح Keystore AES-GCM مقفلة عتادياً بالبصمة ولا تفتح برمجياً عند محاكاة نجاح البصمة بدون `CryptoObject`.\n   - **2. اختبارات هجمات التلاعب (Tampering & Hooking via Frida)**: تشغيل اختبارات أمنية على محاكي معمول له Root وتطبيق سكربتات Frida للتحقق من أن التطبيق يرفض العمليات السيرفرية عند غياب شهادة Play Integrity.\n   - **3. اختبارات تسريب البيانات (Data Leakage Verification)**: فحص ملفات Logcat، والـ Screenshots في الـ App Switcher، وتقارير الأعطال للتأكد من خلوها تماماً من أي Bearer tokens أو أرقام بطاقات (PAN).\n   - **4. اختبارات التوافق العكسي وتشفير التخزين**: اختبار فتح قاعدة بيانات SQLCipher المشفرة والتأكد من عدم تخزين المفتاح كنص صريح في الـ SharedPreferences."
        ),
        "practical_walkthrough": (
            "مصفوفة اختبار أمني مبنية على المخاطر لتوثيق وتغطية المسارات الحساسة:\n"
            "```text\n"
            "مصفوفة الاختبار الأمني المبني على المخاطر (Risk-Based Test Matrix):\n"
            "┌────────────────────────────┬─────────────────────────────┬──────────────────────────────────────────┐\n"
            "│ المسار الحساس (Asset)      │ مستوى الخطر (Risk Level)     │ الاختبارات الإلزامية (Verification)       │\n"
            "├────────────────────────────┼─────────────────────────────┼──────────────────────────────────────────┤\n"
            "│ Biometric Keystore Unlock  │ Critical (High Impact)      │ اختبار أوتوماتيكي مع CryptoObject حقيقي   │\n"
            "│ Payment Double-Charge      │ Critical (Financial Loss)   │ اختبار شبكي لـ Idempotency Key مع Timeout │\n"
            "│ Sensitive Screen Capture   │ High (Compliance Violation) │ فحص تفعيل FLAG_SECURE في Recent Apps     │\n"
            "│ Logcat Token Leakage       │ High (PII Leak)             │ فحص آلي بـ Semgrep / Custom Lint في CI   │\n"
            "│ Root / Frida Detection     │ Medium (Client Friction)    │ فحص السلوك المتدرج مع السيرفر            │\n"
            "└────────────────────────────┴─────────────────────────────┴──────────────────────────────────────────┘\n"
            "```"
        ),
        "quick_answer": "Create a risk-based test plan by ranking features by financial and security impact, prioritizing hardware Keystore cryptography, payment idempotency, and token leakage surfaces. Combine automated linting for PII leaks, on-device instrumentation tests for biometric ciphers, and simulated hooking attacks to verify server-side zero-trust defenses.",
        "best_answer": (
            "A risk-based security test plan prioritizes engineering verification according to asset criticality and threat modeling:\n\n"
            "1. **Threat Modeling & Risk Stratification**:\n"
            "   - Categorize application components into Risk Tiers. Tier 1 (Critical): Authentication tokens, Keystore encryption, biometric authorization, payment checkout. Tier 2 (Moderate): Profile management, deep link routing. Tier 3 (Low): Static marketing content.\n\n"
            "2. **Automated Security Gates in CI**:\n"
            "   - **Static Analysis**: Enforce custom Android Lint and Semgrep rules scanning for hardcoded secrets, missing `FLAG_SECURE`, cleartext traffic permissions, and insecure `FLAG_MUTABLE` PendingIntents.\n   - **Dependency Vulnerability Scanning**: Run automated CVE scans against all third-party Gradle dependencies.\n\n"
            "3. **Dynamic On-Device Security Assertions**:\n"
            "   - Execute instrumented tests verifying that Keystore keys mandate `setUserAuthenticationRequired(true)`.\n   - Assert that invoking biometric callbacks without valid hardware `CryptoObject` releases triggers `UserNotAuthenticatedException`.\n\n"
            "4. **Data Exfiltration Audits**:\n"
            "   - Audit release build outputs: inspect Logcat outputs, memory heap dumps, and SQLite database files to assert that PAN numbers, CVVs, and auth tokens are strictly absent from unencrypted storage."
        ),
        "deep_answer": (
            "From an organizational compliance and release governance perspective, high-assurance releases require multi-party sign-offs:\n\n"
            "1. **Independent Penetration Testing (OWASP MASTG)**: Validate the release candidate against OWASP Mobile Application Security Testing Guide (MASTG) benchmarks. Engage external penetration testers to attempt dynamic method hooking (Frida), local storage extraction (`adb backup`), and proxy interception (Burp Suite).\n\n"
            "2. **Server-Side Zero Trust Verification**: Test that backend endpoints reject requests if the client's Play Integrity verdict indicates a tampered APK or unrecognized signing certificate SHA-256.\n\n"
            "3. **Rollback & Blast-Radius Mitigation**: Ensure the security release is backed by active remote feature kill switches. If an unanticipated issue occurs post-release, the security feature can be disarmed remotely without deploying an emergency app store update."
        ),
        "follow_ups": [
            {
                "question": "What is the primary objective of Risk-Based Testing?",
                "answer": "To allocate testing effort and time proportionally to the areas of highest business, financial, and security risk."
            },
            {
                "question": "Why is static analysis alone insufficient for a security-sensitive release?",
                "answer": "Static analysis inspects code syntax, but cannot verify dynamic runtime behavior like Keystore hardware key unlocks, memory dumps, or network race conditions."
            }
        ]
    },
    {
        "id": "TST-24",
        "arabic_explanation": (
            "كيف تفرض بوابات اختبار صارمة (Gate PRs) على طلبات الدمج دون التسبب في بطء مفرط وتعطيل خط الإنتاج في الـ CI/CD؟\n\n"
            "1. معضلة سرعة الـ CI مقابل دقة الاختبارات:\n   - إذا قمت بتشغيل كل اختبارات الـ Unit والاختبارات البصرية والـ End-to-End على كل PR، سيستغرق الـ CI أكثر من 40 دقيقة لكل Commit!\n   - هذا يصيب المطورين بالإحباط ويعطل إنتاجية الفريق بالكامل.\n\n"
            "2. استراتيجية البوابات متعددة المراحل (Tiered PR Gating Pipeline):\n   - **المرحلة 1: بوابة الـ PR السريعة (Fast PR Gate - أقل من 5 دقائق)**:\n     * فحص التنسيق والجودة الساكنة (ktlint, detekt, Android Lint للملفات المعدلة فقط).\n     * **اختبار الموديولات المتأثرة فقط (Affected Module Testing)**: باستخدام أدوات مثل `affected-module-detector`؛ إذا عدل المطور كود في موديول `:feature:profile`، يقوم Gradle باختبار هذا الموديول فقط متخطياً باقي الـ 40 موديول في المشروع!\n     * تشغيل اختبارات الـ Unit السريعة على الـ JVM المحلي فقط.\n   - **المرحلة 2: بوابة الدمج النهائي (Merge Queue / Pre-Merge Gate - 10-15 دقيقة)**:\n     * تُنفذ بعد موافقة الـ Reviewers وقبل دمج الكود في الـ Main branch مباشرة.\n     * تشغيل اختبارات التكامل وفحص توافق الـ APIs.\n   - **المرحلة 3: مسار الاختبارات الثقيلة الليلي (Nightly Builds / Post-Merge)**:\n     * تشغيل اختبارات الـ UI على المحاكيات (Compose / Espresso)، واختبارات لقطات الشاشة (Screenshot Tests)، والـ Macrobenchmarks بشكل مجمع في الليل دون تعطيل عمل المطورين اليومي."
        ),
        "practical_walkthrough": (
            "تكوين اختبار الموديولات المتأثرة واستخدام Gradle Build Cache في GitHub Actions للوصول لسرعة < 5 دقائق:\n"
            "```yaml\n"
            "# جزء من ملف .github/workflows/pr-gate.yml السريع:\n"
            "name: Fast PR Gate\n"
            "on: [pull_request]\n"
            "\n"
            "jobs:\n"
            "  fast-validation:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n"
            "        with:\n"
            "          fetch-depth: 0 # لجلب سجل التغييرات واكتشاف الموديولات المعدلة\n"
            "\n"
            "      - name: Setup Java Toolchain\n"
            "        uses: actions/setup-java@v4\n"
            "        with:\n"
            "          distribution: 'temurin'\n"
            "          java-version: '17'\n"
            "\n"
            "      - name: Setup Gradle Cache\n"
            "        uses: gradle/actions/setup-gradle@v3\n"
            "\n"
            "      # 1. تشغيل الفحص والاختبارات للموديولات المتأثرة فقط بـ PR Diff:\n"
            "      - name: Run Affected Unit Tests Only\n"
            "        run: ./gradlew runAffectedUnitTests -Paffected_module_detector.enable\n"
            "```"
        ),
        "quick_answer": "Gate PRs under 5 minutes by testing only modules impacted by the PR diff via affected-module-detector, executing fast local JVM unit tests, leveraging remote Gradle build caching, and offloading heavy on-device UI and Macrobenchmark tests to merge queues or nightly builds.",
        "best_answer": (
            "Maintaining rigorous quality gates without degrading developer velocity requires a tiered pipeline strategy:\n\n"
            "1. **Affected Module Testing**:\n"
            "   - In a multi-module codebase (e.g. 50+ modules), running every test suite on every PR is wasteful. Use tools like **Affected Module Detector** to analyze Git diffs. If a PR touches only `:feature:checkout`, Gradle compiles and executes tests strictly for `:feature:checkout` and its direct dependents, skipping the other 45 modules.\n\n"
            "2. **Tier 1: Fast PR Feedback (< 5 Minutes)**:\n"
            "   - Target: Fast block/unblock signal for developers.\n   - Executes: Incremental static analysis (ktlint, detekt, modified-file Android Lint) and affected JVM unit tests.\n   - Powered by **Remote Gradle Build Cache**, downloading pre-compiled binaries for unaffected modules.\n\n"
            "3. **Tier 2: Merge Queue Gate (10–15 Minutes)**:\n"
            "   - Runs when a PR is approved and queued for merge.\n   - Executes full project compilation, integration contract tests, and release APK assembly smoke tests.\n\n"
            "4. **Tier 3: Asynchronous Nightly Suite**:\n"
            "   - Executes heavy, slow, or resource-intensive suites: full emulator instrumentation tests, visual screenshot diffs, and Macrobenchmark performance profiles."
        ),
        "deep_answer": (
            "From an infrastructure optimization and developer productivity perspective, pipeline velocity relies on caching and sharding:\n\n"
            "1. **Remote Build Cache Hit Rate Optimization**: A well-tuned remote build cache achieves an 80%+ cache hit rate. Tasks like `compileKotlin` and `lint` pull outputs instantly from the shared cache. Measure and monitor cache hit rates; a drop in cache hits indicates non-deterministic task inputs.\n\n"
            "2. **Parallel Test Worker Allocation**: Configure `gradle.properties` on CI runners with `org.gradle.parallel=true` and allocate optimal test workers (`maxParallelForks = Runtime.runtime.availableProcessors() / 2`). Running independent module tests across parallel workers reduces execution wall-clock time by 60%.\n\n"
            "3. **Fail-Fast Configuration**: Configure test runners with `--fail-fast`. If an assertion fails on test 3 out of 100, Gradle terminates execution immediately, providing instant error feedback to the author rather than wasting 10 minutes completing remaining tests."
        ),
        "follow_ups": [
            {
                "question": "What is Affected Module Testing?",
                "answer": "A build optimization that analyzes Git commit diffs to compile and test only the specific modules changed by the PR and their downstream dependents."
            },
            {
                "question": "What is the benefit of the --fail-fast flag in Gradle tests?",
                "answer": "It stops test execution immediately upon encountering the first test failure, saving CI runner time and accelerating developer feedback."
            }
        ]
    }
]


def update_tst_data() -> None:
    data = []
    if DATA_FILE.exists():
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))

    existing_map = {item["id"]: item for item in data}
    for item in TST_17_24:
        existing_map[item["id"]] = item

    updated = [existing_map[k] for k in sorted(existing_map.keys())]
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(updated, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {DATA_FILE} with questions TST-17 to TST-24. Total questions: {len(updated)}")


if __name__ == "__main__":
    update_tst_data()
