#!/usr/bin/env python3
"""Generator for TST-09 through TST-16 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "tst.json"

TST_09_16 = [
    {
        "id": "TST-09",
        "arabic_explanation": (
            "كيف تختبر الـ Flow، والـ StateFlow، والـ SharedFlow باحترافية باستخدام مكتبة Turbine؟\n\n"
            "1. ما هي مكتبة Turbine ولماذا نحتاجها؟\n   - في الكوتلن، الـ Flows عبارة عن تدفقات غير متزامنة (Asynchronous Streams). إذا حاولت اختبارها بجمع البيانات يدوياً في قائمة، قد تتجمد الاختبارات أو تحدث Race Conditions.\n   - **Turbine** هي المكتبة الرسمية الموصى بها من CashApp/Square لاختبار الـ Flows بطريقة تسلسلية وحتمية: `flow.test { ... }`.\n\n"
            "2. الفروق الجوهرية عند اختبار أنواع الـ Flows المختلفة:\n   - **اختبار Cold Flow**: يبدأ في إصدار البيانات فقط عند استدعاء `test { }`. نستقبل العناصر عنصراً بعنصر عبر `awaitItem()`.\n   - **اختبار `StateFlow` (Hot Stream)**: يملك قيمة أولية دائماً! أول استدعاء لـ `awaitItem()` سيعيد **القيمة الابتدائية (Initial State)**. كما أنه يطبق خاصية `distinctUntilChanged` تلقائياً؛ إذا أصدرت نفس القيمة مرتين فلن تظهر في الـ Flow.\n   - **اختبار `SharedFlow` (Hot Event Stream)**: لا يحتفظ بالبيانات السابقة افتراضياً (إلا إذا كان له `replay > 0`). يجب بدء الاستماع له عبر `test { }` **قبل** استدعاء الدالة التي تصدر الحدث في كود الـ ViewModel، وإلا ستضيع الانبعاثات!\n\n"
            "3. دوال Turbine الأساسية:\n   - `awaitItem()`: ينتظر وصول العنصر التالي.\n   - `awaitComplete()`: ينتظر اكتمال الـ Flow بنجاح.\n   - `awaitError()`: ينتظر ويرجع الاستثناء إذا فشل الـ Flow.\n   - `expectNoEvents()`: يتأكد من عدم حدوث أي انبعاثات جديدة."
        ),
        "practical_walkthrough": (
            "اختبار StateFlow و SharedFlow باستخدام Turbine ومحاكاة انبعاثات الـ ViewModel:\n"
            "```kotlin\n"
            "class NotificationViewModel : ViewModel() {\n"
            "    // StateFlow للحالة المستمرة\n"
            "    private val _uiState = MutableStateFlow<String>(\"Initial\")\n"
            "    val uiState: StateFlow<String> = _uiState.asStateFlow()\n"
            "\n"
            "    // SharedFlow للأحداث الفردية السريعة (One-off snackbar events)\n"
            "    private val _events = MutableSharedFlow<String>()\n"
            "    val events: SharedFlow<String> = _events.asSharedFlow()\n"
            "\n"
            "    fun updateState(newValue: String) {\n"
            "        _uiState.value = newValue\n"
            "    }\n"
            "\n"
            "    fun triggerAlert(message: String) {\n"
            "        viewModelScope.launch {\n"
            "            _events.emit(message)\n"
            "        }\n"
            "    }\n"
            "}\n"
            "\n"
            "class FlowTurbineTest {\n"
            "    @get:Rule\n"
            "    val mainDispatcherRule = MainDispatcherRule()\n"
            "\n"
            "    @Test\n"
            "    fun `test StateFlow emissions with Turbine`() = runTest {\n"
            "        val viewModel = NotificationViewModel()\n"
            "\n"
            "        viewModel.uiState.test {\n"
            "            // 1. أول عنصر دائماً هو القيمة الابتدائية للـ StateFlow:\n"
            "            assertEquals(\"Initial\", awaitItem())\n"
            "\n"
            "            viewModel.updateState(\"Updated\")\n"
            "            assertEquals(\"Updated\", awaitItem())\n"
            "\n"
            "            expectNoEvents()\n"
            "        }\n"
            "    }\n"
            "\n"
            "    @Test\n"
            "    fun `test SharedFlow requires collecting before emitting`() = runTest {\n"
            "        val viewModel = NotificationViewModel()\n"
            "\n"
            "        viewModel.events.test {\n"
            "            // 2. يجب بدء الـ test block أولاً، ثم استدعاء دالة الإرسال:\n"
            "            viewModel.triggerAlert(\"Error occurred\")\n"
            "            mainDispatcherRule.testDispatcher.scheduler.runCurrent()\n"
            "\n"
            "            assertEquals(\"Error occurred\", awaitItem())\n"
            "            expectNoEvents()\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Test reactive flows using Turbine's flow.test { } DSL to assert sequential emissions via awaitItem() and awaitError(). For StateFlow, account for the immediate initial state emission and distinct-until-changed behavior. For SharedFlow, establish the collection block before triggering emissions to avoid dropped events.",
        "best_answer": (
            "Turbine provides a lightweight, deterministic testing harness for Kotlin asynchronous streams without manual collection coroutines:\n\n"
            "1. **Testing Cold Flows**:\n"
            "   - Cold flows execute on demand upon collection. Wrapping them in `flow.test { }` triggers collection, allowing assertions item-by-item (`awaitItem()`), followed by terminal assertions (`awaitComplete()` or `awaitError()`).\n\n"
            "2. **Testing `StateFlow`**:\n"
            "   - StateFlow is a confluent hot stream with conflation and replay size 1. The first invocation of `awaitItem()` **always** yields the initial state.\n   - StateFlow enforces `distinctUntilChanged` equivalence; emitting identical sequential states emits only once, which Turbine verifies.\n\n"
            "3. **Testing `SharedFlow`**:\n"
            "   - SharedFlow does not retain past emissions unless configured with `replay > 0`. Because emissions before active collection are dropped, the test must enter the `sharedFlow.test { }` block **before** invoking the ViewModel method that emits the event.\n\n"
            "4. **Asserting Absence of Events**:\n"
            "   - `expectNoEvents()` ensures no unhandled or duplicate events are currently queued, guaranteeing stream purity."
        ),
        "deep_answer": (
            "From an advanced concurrency testing perspective, Turbine solves timing races with SharedFlow and WhileSubscribed streams:\n\n"
            "1. **SharingStarted.WhileSubscribed(5000)**: In production ViewModels, flows are converted to state via `.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), Initial)`. Direct value reads (`uiState.value`) outside a collector return the initial state forever because upstream is cold. Turbine's `test { }` starts a real subscriber, advancing upstream collection deterministically.\n\n"
            "2. **Turbine Timeouts & Cancellation**: Turbine enforces an internal timeout (default 1 second). If a flow fails to emit, Turbine fails fast with a descriptive `TimeoutCancellationException` rather than hanging the entire CI test suite.\n\n"
            "3. **Cancel and Ignore Remaining Events**: When testing infinite flows (e.g. database change observers), use `cancelAndIgnoreRemainingEvents()` at the end of the test block to cleanly unsubscribe and cancel the underlying coroutine collector."
        ),
        "follow_ups": [
            {
                "question": "Why does StateFlow ignore duplicate identical values during testing?",
                "answer": "StateFlow internally implements Any.equals() equality checks on new values and suppresses emissions if the new value matches the current value."
            },
            {
                "question": "What is the purpose of cancelAndIgnoreRemainingEvents() in Turbine?",
                "answer": "It unregisters the collector and halts the stream without failing the test if additional emissions remain pending in an infinite flow."
            }
        ]
    },
    {
        "id": "TST-10",
        "arabic_explanation": (
            "كيف تختبر سيناريوهات الإلغاء (Cancellation)، والأخطاء (Errors)، وإعادة المحاولة (Retries)، وفترات الانتظار (Timeouts) للكوروتينات حتمياً؟\n\n"
            "1. اختبار إلغاء الكوروتين (Cancellation Testing):\n   - التأكد من أن إلغاء الـ `Job` يوقف العمل فوراً ولا يترك أي مهام معلقة في الخلفية.\n   - التحقق من تنفيذ كود التنظيف داخل `withContext(NonCancellable)` أو داخل بلوك `finally`.\n   - **قاعدة حرجة**: التحقق من أن الكود لا يبتلع `CancellationException` ويقوم بإعادة رميها دائماً.\n\n"
            "2. اختبار فترات الانتظار (Timeouts):\n   - اختبار الدوال التي تستخدم `withTimeout(duration)` عبر القفز بالوقت الافتراضي في `runTest`.\n   - نستخدم `advanceTimeBy(timeoutMs)` للتحقق من رمي `TimeoutCancellationException` بدقة دون انتظار حقيقي.\n\n"
            "3. اختبار إعادة المحاولة والتأخير التضاعفي (Exponential Backoff):\n   - اختبار خوارزمية الـ Retry التي تعيد المحاولة 3 مرات عند حدوث خطأ في الشبكة.\n   - نتحقق من عدد المحاولات والتقدم بالوقت الافتراضي بين كل محاولة وأخرى للتأكد من حساب فترات الانتظار بدقة."
        ),
        "practical_walkthrough": (
            "اختبار إعادة المحاولة التلقائية مع Exponential Backoff والتحقق من السلوك بالوقت الافتراضي:\n"
            "```kotlin\n"
            "class NetworkRetryEngine {\n"
            "    suspend fun <T> fetchWithRetry(maxRetries: Int = 3, block: suspend () -> T): T {\n"
            "        var attempts = 0\n"
            "        while (true) {\n"
            "            try {\n"
            "                return block()\n"
            "            } catch (e: IOException) {\n"
            "                attempts++\n"
            "                if (attempts >= maxRetries) throw e\n"
            "                val delayMs = 1000L * (1 shl (attempts - 1)) // 1s, 2s, 4s...\n"
            "                delay(delayMs)\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "}\n"
            "\n"
            "class RetryEngineTest {\n"
            "    @Test\n"
            "    fun `fetchWithRetry retries 3 times with exponential delays then succeeds`() = runTest {\n"
            "        val engine = NetworkRetryEngine()\n"
            "        var callCount = 0\n"
            "\n"
            "        val deferredResult = async {\n"
            "            engine.fetchWithRetry(maxRetries = 3) {\n"
            "                callCount++\n"
            "                if (callCount < 3) throw IOException(\"Network failed\")\n"
            "                \"Success\"\n"
            "            }\n"
            "        }\n"
            "\n"
            "        // المحاولة 1: تفشل فوراً (callCount = 1) وتبدأ delay(1000)\n"
            "        runCurrent()\n"
            "        assertEquals(1, callCount)\n"
            "\n"
            "        // التقدم بالوقت 1000ms: المحاولة 2 تفشل (callCount = 2) وتبدأ delay(2000)\n"
            "        advanceTimeBy(1000)\n"
            "        runCurrent()\n"
            "        assertEquals(2, callCount)\n"
            "\n"
            "        // التقدم بالوقت 2000ms: المحاولة 3 تنجح!\n"
            "        advanceTimeBy(2000)\n"
            "        runCurrent()\n"
            "        assertEquals(3, callCount)\n"
            "        assertEquals(\"Success\", deferredResult.await())\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Test cancellation by asserting job.cancel() propagates and cleanup blocks execute under NonCancellable. Test timeouts and exponential retries deterministically by advancing virtual time using advanceTimeBy() in runTest, verifying attempt counts and interval spacing without real clock delays.",
        "best_answer": (
            "Testing asynchronous failure modes requires coordinating virtual clocks and exception dispatchers:\n\n"
            "1. **Testing Coroutine Cancellation**:\n"
            "   - Launch a coroutine job under test, verify it enters active processing, and invoke `job.cancel()`.\n   - Assert that `job.isCancelled` becomes true, child jobs terminate, and cleanup routines (e.g. closing network streams or wiping memory buffers) inside `withContext(NonCancellable)` or `finally` execute completely.\n   - Assert that code never swallows `CancellationException`, which breaks structured concurrency.\n\n"
            "2. **Testing Timeouts (`withTimeout`)**:\n"
            "   - Execute code wrapped in `withTimeout(5000L)` inside `runTest`.\n   - Advance virtual time via `advanceTimeBy(5001L)`.\n   - Assert that `TimeoutCancellationException` is thrown, or that `withTimeoutOrNull` safely returns `null` without hanging the test.\n\n"
            "3. **Testing Exponential Backoff and Retries**:\n"
            "   - Simulate network failures and step through retry intervals using `advanceTimeBy()`. Validate that calls occur at exact mathematical intervals (1s, 2s, 4s) and assert that terminal failures surface the original exception once maximum retry thresholds are reached."
        ),
        "deep_answer": (
            "From an advanced concurrency testing perspective, handling exception boundaries requires strict isolation:\n\n"
            "1. **CoroutineExceptionHandler in Unit Tests**: Unhandled exceptions launched via `launch` bubble to the parent scope and crash `runTest`. To assert that a ViewModel handles unexpected network errors gracefully, supply a custom `CoroutineExceptionHandler` or wrap repository results in `runCatching` / `Result<T>`.\n\n"
            "2. **SupervisorScope Isolation**: When testing concurrent operations where one worker fails (e.g., three parallel API requests), wrap child jobs in `supervisorScope`. Assert that an exception in child A does not cancel child B or child C, verifying resilient partial execution.\n\n"
            "3. **Testing Jitter Distributions**: When retries use randomized jitter (`Random.nextLong(0, delay)`), inject a deterministic pseudo-random generator or seed so that backoff test assertions do not flake due to unpredictable random values."
        ),
        "follow_ups": [
            {
                "question": "Why does catching generic Exception inside a coroutine cause bugs?",
                "answer": "Because CancellationException extends Exception; catching Exception without rethrowing CancellationException prevents coroutine cancellation from functioning."
            },
            {
                "question": "How do you test that withTimeoutOrNull returns a fallback value?",
                "answer": "Call advanceTimeBy(timeoutMillis + 1) in runTest and assert that the returned variable equals null or the fallback object."
            }
        ]
    },
    {
        "id": "TST-11",
        "arabic_explanation": (
            "كيف تختبر دوال الـ Room DAOs، وترقيات قاعدة البيانات (Database Migrations)، والمعاملات الذرية (Transactions) بشكل معزول؟\n\n"
            "1. اختبار الـ Room DAOs (In-Memory Database):\n   - نستخدم `Room.inMemoryDatabaseBuilder()` في مجلد `src/test/` (مع Robolectric) أو `src/androidTest/` (على محاكي حقيقي).\n   - ميزة قاعدة البيانات في الذاكرة: سرعة فائقة، وتبدأ فارغة تماماً مع كل اختبار، وتُحذف فور إغلاقها (`db.close()`) دون ترك أي ملفات ملوثة على القرص.\n   - تفعيل `allowMainThreadQueries()` لتسهيل كتابة الاختبارات المتزامنة.\n\n"
            "2. اختبار ترقيات قاعدة البيانات (Room Migration Testing):\n   - **قاعدة ذهبية**: لا تعتمد على التجربة اليدوية! استخدم أداة `MigrationTestHelper` الرسمية.\n   - يقوم الاختبار بإنشاء قاعدة بيانات حقيقية بالإصدار 1 (باستخدام ملف الـ Schema JSON القديم)، وإدخال بيانات حقيقية، ثم تنفيذ الـ Migration إلى الإصدار 2، والتحقق من أن البيانات لم تُفقد وأن الجداول والأعمدة الجديدة مطابقة للـ Hash الجديد.\n\n"
            "3. اختبار المعاملات الذرية (Transactions Testing):\n   - التحقق من أنه إذا فشلت عملية كتابة في المنتصف، يتم التراجع عن جميع العمليات السابقة (Rollback) ولا تُترك قاعدة البيانات في حالة متناقضة."
        ),
        "practical_walkthrough": (
            "اختبار DAO في الذاكرة واختبار هجرة Room باستخدام MigrationTestHelper:\n"
            "```kotlin\n"
            "// 1. اختبار Room DAO في الذاكرة (In-Memory Database Test):\n"
            "@RunWith(AndroidJUnit4::class)\n"
            "class UserDaoInMemoryTest {\n"
            "    private lateinit var db: AppDatabase\n"
            "    private lateinit var userDao: UserDao\n"
            "\n"
            "    @Before\n"
            "    fun createDb() {\n"
            "        val context = ApplicationProvider.getApplicationContext<Context>()\n"
            "        db = Room.inMemoryDatabaseBuilder(context, AppDatabase::class.java)\n"
            "            .allowMainThreadQueries()\n"
            "            .build()\n"
            "        userDao = db.userDao()\n"
            "    }\n"
            "\n"
            "    @Test\n"
            "    fun insertUserAndReadInList() = runTest {\n"
            "        val user = UserEntity(id = \"usr_1\", name = \"Sarah\")\n"
            "        userDao.insert(user)\n"
            "        val users = userDao.getAllUsers().first()\n"
            "        assertEquals(1, users.size)\n"
            "        assertEquals(\"Sarah\", users[0].name)\n"
            "    }\n"
            "\n"
            "    @After\n"
            "    fun closeDb() = db.close()\n"
            "}\n"
            "\n"
            "// 2. اختبار Migration حقيقي من الإصدار 1 إلى 2 عبر MigrationTestHelper:\n"
            "@RunWith(AndroidJUnit4::class)\n"
            "class DatabaseMigrationTest {\n"
            "    private val TEST_DB = \"migration-test.db\"\n"
            "\n"
            "    @get:Rule\n"
            "    val helper: MigrationTestHelper = MigrationTestHelper(\n"
            "        InstrumentationRegistry.getInstrumentation(),\n"
            "        AppDatabase::class.java\n"
            "    )\n"
            "\n"
            "    @Test\n"
            "    fun migrate1To2_preservesExistingUserData() {\n"
            "        // إنشاء قاعدة بيانات بالإصدار 1 وإدخال بيانات قديمة\n"
            "        helper.createDatabase(TEST_DB, 1).apply {\n"
            "            execSQL(\"INSERT INTO users (id, name) VALUES ('u1', 'Omar')\")\n"
            "            close()\n"
            "        }\n"
            "\n"
            "        // تشغيل الـ Migration إلى الإصدار 2 والتحقق من صحة الـ Schema\n"
            "        val dbV2 = helper.runMigrationsAndValidate(TEST_DB, 2, true, MIGRATION_1_2)\n"
            "        \n"
            "        // التأكد من أن بيانات Omar ما زالت موجودة والعمود الجديد أخذ قيمته الافتراضية:\n"
            "        val cursor = dbV2.query(\"SELECT id, name, loyalty_points FROM users WHERE id = 'u1'\")\n"
            "        assertTrue(cursor.moveToFirst())\n"
            "        assertEquals(\"Omar\", cursor.getString(1))\n"
            "        assertEquals(0, cursor.getInt(2)) // القيمة الافتراضية المضافة في v2\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Test Room DAOs using in-memory databases with allowMainThreadQueries() to ensure rapid, isolated tests. Test database migrations using Room's MigrationTestHelper in instrumented tests, verifying that existing records are preserved and new schema constraints match versioned schema JSON files.",
        "best_answer": (
            "Room database testing divides into DAO functional validation and schema migration verification:\n\n"
            "1. **In-Memory DAO Testing**:\n"
            "   - Instantiate tests using `Room.inMemoryDatabaseBuilder(context, AppDatabase::class.java).allowMainThreadQueries().build()`.\n   - In-memory databases exist strictly in RAM and are completely destroyed upon `db.close()`, guaranteeing test isolation without disk file leftovers.\n   - Test reactive DAO flows using Turbine to assert that SQL inserts/updates emit fresh lists to active flow collectors.\n\n"
            "2. **Automated Migration Testing (`MigrationTestHelper`)**:\n"
            "   - Use Room's `MigrationTestHelper` in instrumented tests.\n   - Step 1: `helper.createDatabase(DB_NAME, 1)` boots SQLite using the version 1 JSON schema. Insert sample records via raw SQL.\n   - Step 2: `helper.runMigrationsAndValidate(DB_NAME, 2, true, MIGRATION_1_2)` applies the migration and automatically validates SQLite column types and foreign keys against the version 2 JSON schema.\n   - Step 3: Query the migrated database to assert that historical records survived uncorrupted and new columns received default values.\n\n"
            "3. **Transaction Atomicity Verification**:\n"
            "   - Test methods marked `@Transaction`. Inject an intentional exception halfway through a batch operation, and assert that previously written rows in that transaction were rolled back completely."
        ),
        "deep_answer": (
            "From an enterprise storage engineering perspective, database tests must validate SQLite constraints and threading boundaries:\n\n"
            "1. **Foreign Key Constraint Verification**: By default, SQLite disables foreign key enforcement unless explicitly enabled via `PRAGMA foreign_keys = ON;`. In-memory tests must configure Room callbacks or open helper factories to enable foreign keys, ensuring tests catch constraint violations before production.\n\n"
            "2. **Multi-Version Migration Chains (v1 -> v4)**: Write automated test permutations that test direct multi-version hops (`1->4`) alongside sequential hops (`1->2->3->4`), verifying that legacy users upgrading across multiple years do not encounter `IllegalStateException` on launch.\n\n"
            "3. **Robolectric SQLite vs. Real Device SQLite**: While Robolectric runs SQLite tests on the host machine using SQLite4Java or native macOS/Linux SQLite libraries, OEM Android devices run customized SQLite engines. Always execute complex migration and WAL concurrency tests on real Android instrumented test runners."
        ),
        "follow_ups": [
            {
                "question": "Why is allowMainThreadQueries() safe in Room unit tests?",
                "answer": "Because test runners execute synchronously on single test threads; main thread blocking rules are unnecessary overhead in isolated test suites."
            },
            {
                "question": "What happens if a migration fails during helper.runMigrationsAndValidate()?",
                "answer": "It throws an IllegalStateException with a detailed diff explaining which table, column, or index mismatched the expected schema JSON."
            }
        ]
    },
    {
        "id": "TST-12",
        "arabic_explanation": (
            "كيف تختبر سيناريوهات فشل الشبكة (HTTP Failures, Timeouts, Malformed JSON) باحترافية باستخدام `MockWebServer`؟\n\n"
            "1. ما هو `MockWebServer`؟\n   - خادم HTTP حقيقي وخفيف يعمل محلياً داخل جهازك أثناء الاختبار (من مكتبة Square OkHttp).\n   - يتيح لك اختبار طبقة الشبكة بالكامل (OkHttp, Retrofit, Converters, Interceptors, Repositories) عبر شبكة حقيقية مشفرة محلياً دون الحاجة لاتصال خارجي بالإنترنت!\n\n"
            "2. سيناريوهات الفشل التي يجب اختبارها:\n   - **أخطاء الخادم (HTTP 500, 502, 503)**: التحقق من أن التطبيق يعرض رسالة خطأ ملائمة للمستخدم ولا ينهار.\n   - **أخطاء المصادقة (HTTP 401 Unauthorized)**: التحقق من أن الـ Authenticator يحاول تجديد التوكن أو توجيه المستخدم لشاشة الدخول.\n   - **الاستجابات المشوهة (Malformed / Broken JSON)**: إرجاع نص JSON مكسور والتحقق من التقاط خطأ الـ `JsonDataException` بسلاسة.\n   - **انقطاع الشبكة ومهلة الانتظار (Socket Timeouts)**: محاكاة انقطاع الاتصال المفاجئ عبر `SocketPolicy.NO_RESPONSE` أو `SocketPolicy.DISCONNECT_AT_START`.\n\n"
            "3. فحص الطلبات الصادرة (Verifying Outgoing Requests):\n   - استخدام `mockWebServer.takeRequest()` للتحقق من أن التطبيق أرسل الـ Headers الصحيحة (مثل `Authorization: Bearer ...`) والـ Query Parameters والـ Body المطلوب."
        ),
        "practical_walkthrough": (
            "اختبار أخطاء الشبكة والـ 401 والتأكد من هيدرز الطلب الصادر عبر MockWebServer:\n"
            "```kotlin\n"
            "class NetworkRepositoryTest {\n"
            "    private lateinit var server: MockWebServer\n"
            "    private lateinit var api: UserApiService\n"
            "\n"
            "    @Before\n"
            "    fun setup() {\n"
            "        server = MockWebServer()\n"
            "        server.start()\n"
            "        api = Retrofit.Builder()\n"
            "            .baseUrl(server.url(\"/\"))\n"
            "            .addConverterFactory(MoshiConverterFactory.create())\n"
            "            .build()\n"
            "            .create(UserApiService::class.java)\n"
            "    }\n"
            "\n"
            "    @Test\n"
            "    fun `server 500 internal error returns failure result without crashing`() = runTest {\n"
            "        // 1. محاكاة استجابة خطأ 500 من الخادم:\n"
            "        server.enqueue(MockResponse().setResponseCode(500).setBody(\"Internal Server Error\"))\n"
            "\n"
            "        val repository = UserRepositoryImpl(api)\n"
            "        val result = repository.fetchUser(\"123\")\n"
            "\n"
            "        assertTrue(result.isFailure)\n"
            "    }\n"
            "\n"
            "    @Test\n"
            "    fun `verify request outgoing headers and path`() = runTest {\n"
            "        server.enqueue(MockResponse().setResponseCode(200).setBody(\"{\\\"id\\\":\\\"123\\\",\\\"name\\\":\\\"Ali\\\"}\"))\n"
            "\n"
            "        val repository = UserRepositoryImpl(api)\n"
            "        repository.fetchUser(\"123\")\n"
            "\n"
            "        // 2. فحص تفاصيل الطلب الصادر من التطبيق:\n"
            "        val recordedRequest = server.takeRequest()\n"
            "        assertEquals(\"/users/123\", recordedRequest.path)\n"
            "        assertEquals(\"GET\", recordedRequest.method)\n"
            "    }\n"
            "\n"
            "    @After\n"
            "    fun tearDown() = server.shutdown()\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Test network failures using Square's MockWebServer by enqueuing MockResponse instances with error codes (401, 500), malformed JSON payloads, or SocketPolicy.NO_RESPONSE. Assert that repositories handle failures gracefully, and verify outgoing headers and payload bodies using takeRequest().",
        "best_answer": (
            "MockWebServer enables hermetic, end-to-end testing of the complete networking stack (OkHttp, Retrofit, interceptors, and serializers) on the local JVM:\n\n"
            "1. **Simulating HTTP Error Statuses**:\n"
            "   - Enqueue explicit response codes: `MockResponse().setResponseCode(500).setBody(\"Internal Server Error\")`.\n   - Enqueue `401 Unauthorized` to test whether token refresh interceptors intercept the failure, refresh credentials, and replay the original request.\n\n"
            "2. **Simulating Network Timeouts & Abrupt Drops**:\n"
            "   - Configure low-level socket policies: `MockResponse().setSocketPolicy(SocketPolicy.NO_RESPONSE)` simulates gateway timeouts, while `SocketPolicy.DISCONNECT_AFTER_REQUEST` tests sudden socket terminations mid-handshake.\n\n"
            "3. **Malformed & Incomplete Payloads**:\n"
            "   - Enqueue truncated or malformed JSON (`MockResponse().setBody(\"{\\\"id\\\": 123, \")`) to verify that JSON deserialization errors (`JsonEncodingException`) are caught and mapped into domain network errors rather than unhandled app crashes.\n\n"
            "4. **Asserting Outgoing Requests (`takeRequest()`)**:\n"
            "   - Inspect `server.takeRequest()` to assert that outgoing authorization tokens, API keys, User-Agent strings, and JSON request bodies strictly match backend contract expectations."
        ),
        "deep_answer": (
            "From an enterprise testing architecture perspective, MockWebServer provides deterministic replay capabilities:\n\n"
            "1. **Dispatcher for Multi-Endpoint Scenarios**: Instead of using sequential `enqueue()`, configure a custom `Dispatcher`. The dispatcher inspects `request.path` and routes responses dynamically (e.g. returning 200 for `/auth/refresh` while returning 401 for `/v1/orders`), enabling complex multi-request concurrency testing.\n\n"
            "2. **Simulating Throttling and Slow Radios**: Test loading spinners and UI cancellation by simulating slow cellular networks using `MockResponse().throttleBody(1024, 1, TimeUnit.SECONDS)`. This streams 1KB per second, giving tests time to verify progress bars and cancel requests mid-stream.\n\n"
            "3. **Port Collisions in Parallel CI**: Never hardcode port numbers (e.g. `localhost:8080`). Invoke `server.start()` without parameters; MockWebServer automatically binds to an ephemeral open operating system port, preventing port collisions when multiple Gradle test workers run concurrently."
        ),
        "follow_ups": [
            {
                "question": "What is the difference between enqueue() and setDispatcher() in MockWebServer?",
                "answer": "enqueue() queues responses FIFO regardless of request path; setDispatcher() inspects the request URI and headers to return specific responses dynamically."
            },
            {
                "question": "Why should you avoid hardcoding port numbers with MockWebServer?",
                "answer": "Hardcoded ports cause BindException collisions when multiple tests run in parallel or when previous server instances fail to release sockets immediately."
            }
        ]
    },
    {
        "id": "TST-13",
        "arabic_explanation": (
            "كيف تختبر استبدال التبعيات في الـ Dependency Injection (DI Substitutions) والتبعيات المربوطة بنطاقات (Scoped Dependencies)؟\n\n"
            "1. استبدال التبعيات في اختبارات الوحدة (Local Unit Tests):\n   - في الـ Unit Tests على JVM: **لا تستخدم Hilt أو Dagger إطلاقاً**!\n   - اعتمد على حقن التبعيات عبر الـ Constructor يدوياً (Manual Constructor Injection). هذا يوفر سرعة فائقة في التنفيذ وتجنب أي تعقيد في معالجة الـ Code Generation.\n\n"
            "2. استبدال التبعيات في اختبارات التكامل والأجهزة عبر Hilt (`@HiltAndroidTest`):\n   - في اختبارات الـ UI والـ Integration Tests التي تتطلب تشغيل Hilt، نستخدم:\n     * `@UninstallModules(ProductionNetworkModule::class)` لإلغاء الموديول الحقيقي الخاص بالإنتاج.\n     * `@BindValue` لحقن كائن Fake أو Mock مباشرة داخل الـ Hilt Dependency Graph للاختبار الحالي.\n\n"
            "3. اختبار التبعيات المربوطة بنطاقات (Scoped Dependencies):\n   - **`@Singleton`**: يجب التأكد من عدم تسريب حالتها بين الاختبارات المستقلة (Test Leakage).\n   - **`@ViewModelScoped` / `@ActivityScoped`**: التحقق من إعادة إنشاء التبعية عند تدمير وإعادة إنشاء الـ Scope المقترن بها."
        ),
        "practical_walkthrough": (
            "استبدال موديول الإنتاج بـ Fake في اختبارات Hilt عبر @UninstallModules و @BindValue:\n"
            "```kotlin\n"
            "@HiltAndroidTest\n"
            "@UninstallModules(AnalyticsModule::class) // 1. إلغاء موديول الإنتاج الحقيقي\n"
            "@RunWith(AndroidJUnit4::class)\n"
            "class CheckoutFlowIntegrationTest {\n"
            "\n"
            "    @get:Rule(order = 0)\n"
            "    val hiltRule = HiltAndroidRule(this)\n"
            "\n"
            "    @get:Rule(order = 1)\n"
            "    val composeTestRule = createAndroidComposeRule<MainActivity>()\n"
            "\n"
            "    // 2. حقن كائن Fake بديل مباشرة داخل شجرة الـ DI الخاصة بـ Hilt:\n"
            "    @BindValue\n"
            "    val fakeAnalyticsTracker: AnalyticsTracker = FakeAnalyticsTracker()\n"
            "\n"
            "    @Before\n"
            "    fun init() {\n"
            "        hiltRule.inject()\n"
            "    }\n"
            "\n"
            "    @Test\n"
            "    fun checkoutScreen_triggersPurchaseEventOnFakeAnalytics() {\n"
            "        composeTestRule.onNodeWithText(\"Complete Order\").performClick()\n"
            "        \n"
            "        // التحقق من أن الـ Fake Analytics استقبل الحدث بنجاح:\n"
            "        assertEquals(1, (fakeAnalyticsTracker as FakeAnalyticsTracker).capturedEvents.size)\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "In local unit tests, substitute dependencies via direct constructor injection without DI frameworks. In Hilt instrumentation tests, use @HiltAndroidTest with @UninstallModules to remove production bindings, replacing them surgically with @BindValue or custom test modules to inject fakes into the active dependency graph.",
        "best_answer": (
            "Managing dependency injection substitutions in test suites requires separating fast JVM unit tests from full container integration tests:\n\n"
            "1. **Local JVM Testing (Pure Constructor Injection)**:\n"
            "   - Bypassing Dagger/Hilt entirely in `src/test/` is an industry best practice. When classes follow constructor injection, tests simply pass instantiated Fakes (`MyViewModel(FakeUserRepository())`). This avoids annotation processing overhead and runs in milliseconds.\n\n"
            "2. **Hilt Integration Testing (`@HiltAndroidTest`)**:\n"
            "   - When testing full Activity or Fragment flows requiring real dependency graphs:\n     - Decorate test classes with `@HiltAndroidTest` and attach `HiltAndroidRule(this)`.\n     - Use `@UninstallModules(ProductionDataModule::class)` to decouple real network/storage bindings.\n     - Use `@BindValue` on a field to automatically bind a Fake instance into the dependency container for that specific test run.\n\n"
            "3. **Verifying Scoped Lifecycles**:\n   - Verify that `@ActivityScoped` bindings produce distinct instances when transitioning between activities, while `@Singleton` bindings persist within the test process."
        ),
        "deep_answer": (
            "From an architectural systems perspective, managing test DI containers requires preventing cross-test state pollution:\n\n"
            "1. **Singleton State Leaks Across Tests**: If a Fake bound as a `@Singleton` maintains in-memory state (e.g. `FakeDatabase` holding user records), that state persists across consecutive `@Test` methods unless explicitly wiped in `@After` teardown hooks. Build explicit `clear()` methods on all stateful test fakes.\n\n"
            "2. **Custom Test Application in Instrumentation**: Hilt generates `HiltTestApplication` for instrumented tests. Ensure your `app/build.gradle.kts` sets `testInstrumentationRunner = \"com.example.HiltTestRunner\"`, which subclasses `AndroidJUnitRunner` and boots `HiltTestApplication` as the root application context.\n\n"
            "3. **Dynamic Test Components**: For feature-modular codebases, avoid a single monolithic test module. Create isolated test modules per feature (`:feature:checkout:testing`) exporting modular fakes, allowing feature tests to compose test graphs independently."
        ),
        "follow_ups": [
            {
                "question": "What does @BindValue do in Hilt testing?",
                "answer": "It binds a test class property into the Hilt dependency graph, replacing any existing binding of that type for the duration of the test."
            },
            {
                "question": "Why must HiltAndroidRule have an order index of 0?",
                "answer": "Because Hilt must initialize the dependency injection container before other rules (like ActivityScenarioRule or ComposeRule) launch the UI components."
            }
        ]
    },
    {
        "id": "TST-14",
        "arabic_explanation": (
            "كيف تختبر شجرة المعاني (Semantics Tree)، والتنقل (Navigation)، وإمكانية الوصول (Accessibility) في Jetpack Compose؟\n\n"
            "1. اختبار شجرة المعاني في Compose (Semantics Tree Testing):\n   - في Compose، لا توجد View IDs! الواجهة تُمثل كـ **Semantics Tree** يصف معنى ومحتوى كل عنصر للمستخدم وقارئات الشاشة.\n   - **أدوات الاختيار والتوثيق**:\n     * `onNodeWithText(\"Submit\")`: البحث بالنص المعروض.\n     * `onNodeWithContentDescription(\"Back\")`: البحث بوصف المحتوى للأيقونات.\n     * `onNodeWithTag(\"login_button\")`: البحث بـ TestTag صريح (يُستخدم كحل أخير إذا لم يتوفر نص أو وصف).\n   - **التوكيدات (Assertions)**:\n     * `assertIsDisplayed()`, `assertIsEnabled()`, `assertIsSelected()`, `assertHasClickAction()`.\n\n"
            "2. اختبار التنقل (Compose Navigation Testing):\n   - نستخدم `TestNavHostController` من مكتبة `navigation-testing`.\n   - نقوم بربط الـ Controller بـ `NavHost`، وتنفيذ إجراءات النقر، والتحقق من المسار الحالي:\n     `assertEquals(\"details/{orderId}\", navController.currentBackStackEntry?.destination?.route)`.\n\n"
            "3. فحص إمكانية الوصول (Accessibility Testing - A11y):\n   - التأكد من أن مساحة النقر لا تقل عن 48×48dp (Touch Target Size).\n   - دمج العقد المترابطة لتسهيل القراءة عبر `Modifier.semantics(mergeDescendants = true)`."
        ),
        "practical_walkthrough": (
            "اختبار شجرة المعاني والتنقل وفحص إمكانية الوصول في Compose:\n"
            "```kotlin\n"
            "class ComposeUiAndNavigationTest {\n"
            "    @get:Rule\n"
            "    val composeTestRule = createComposeRule()\n"
            "    private lateinit var navController: TestNavHostController\n"
            "\n"
            "    @Before\n"
            "    fun setupAppNavHost() {\n"
            "        composeTestRule.setContent {\n"
            "            navController = TestNavHostController(LocalContext.current)\n"
            "            navController.navigatorProvider.addNavigator(ComposeNavigator())\n"
            "            AppNavHost(navController = navController)\n"
            "        }\n"
            "    }\n"
            "\n"
            "    @Test\n"
            "    fun navigateFromHomeToDetails_verifiesRouteAndAccessibility() {\n"
            "        // 1. التحقق من وجود الزر بإمكانية وصول سليمة والضغط عليه:\n"
            "        composeTestRule.onNodeWithContentDescription(\"View Order Details\")\n"
            "            .assertIsDisplayed()\n"
            "            .assertHasClickAction()\n"
            "            .performClick()\n"
            "\n"
            "        // 2. التحقق من انتقال الـ NavController إلى الشاشة والمسار الصحيح:\n"
            "        assertEquals(\"order_details/{id}\", navController.currentBackStackEntry?.destination?.route)\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Test Compose UI via createComposeRule by querying the Semantics Tree with onNodeWithText or onNodeWithContentDescription and asserting states like assertIsDisplayed(). Test navigation using TestNavHostController to assert active backstack routes. Validate accessibility by enforcing semantic content descriptions and 48dp minimum touch targets.",
        "best_answer": (
            "Testing Jetpack Compose interfaces exercises the semantic contract presented to users and assistive technologies:\n\n"
            "1. **Semantics Tree Node Queries**:\n"
            "   - Query UI nodes using real user semantics: `composeTestRule.onNodeWithText(\"Checkout\")` or `onNodeWithContentDescription(\"Shopping Cart\")`. Prefer semantic matchers over arbitrary `Modifier.testTag()`, as semantic matchers validate that the UI is accessible to screen readers.\n\n"
            "2. **State & Action Assertions**:\n"
            "   - Assert node properties: `assertIsDisplayed()`, `assertIsEnabled()`, `assertIsToggleable()`, `assertValueEquals(\"100\")`. Trigger actions via `performClick()`, `performScrollTo()`, or `performTextInput(\"text\")`.\n\n"
            "3. **Navigation Contract Testing**:\n"
            "   - Mount the `NavHost` using `TestNavHostController(LocalContext.current)`.\n   - Execute UI interactions, then assert destination state via `assertEquals(\"details_route\", navController.currentBackStackEntry?.destination?.route)` without launching real activities.\n\n"
            "4. **Accessibility (a11y) Auditing**:\n"
            "   - Enable AndroidX `AccessibilityChecks.enable()` during Compose tests. The framework automatically flags insufficient color contrast, missing content descriptions, and touch targets smaller than 48x48dp."
        ),
        "deep_answer": (
            "From an advanced design system testing perspective, semantic merging and unmerged tree inspection provide deep control:\n\n"
            "1. **Merged vs. Unmerged Semantics Trees**: By default, Compose merges child semantics into parent nodes for accessibility (e.g. merging a `Button` with its inner `Text` label into a single clickable node). If you need to test a specific inner element, query the unmerged tree explicitly: `onNodeWithText(\"Subtext\", useUnmergedTree = true)`.\n\n"
            "2. **Testing Custom Semantics Properties**: When building custom UI components (e.g. custom sliders, star ratings), expose custom semantic properties via `Modifier.semantics { set(CustomKey, value) }`. In tests, query and assert against these typed semantic keys directly.\n\n"
            "3. **Robolectric Compose UI Testing**: With modern Robolectric, Compose UI tests using `createComposeRule()` execute directly on the host JVM in seconds, providing rapid UI verification without booting Android emulators."
        ),
        "follow_ups": [
            {
                "question": "What is the difference between merged and unmerged semantics trees in Compose?",
                "answer": "The merged tree collapses child nodes into parent containers for screen readers (TalkBack); the unmerged tree preserves every individual composable node."
            },
            {
                "question": "Why should Modifier.testTag() be used as a last resort in Compose tests?",
                "answer": "Test tags do not improve accessibility for real users; querying by text, content description, or semantic role validates both functionality and accessibility."
            }
        ]
    },
    {
        "id": "TST-15",
        "arabic_explanation": (
            "كيف تقضي على الاختبارات المتقلبة (Flaky UI Tests) وتتحكم في الجدولة الزمنية وتزامن العمليات غير المتزامنة؟\n\n"
            "1. ما هو الـ Flaky Test ولماذا هو عدو الـ CI/CD الأول؟\n   - هو الاختبار الذي ينجح أحياناً ويفشل أحياناً أخرى على نفس الكود بالضبط دون أي تغيير!\n   - يدمر ثقة المطورين في الـ CI، ويؤخر دمج الـ PRs، ويخفي الأخطاء الحقيقية.\n\n"
            "2. الأسباب الجذرية للـ Flakiness في اختبارات أندرويد:\n   - **استخدام `Thread.sleep()`**: جريمة برمجية! إذا كان جهاز الـ CI بطيئاً، سينتهي الـ Sleep قبل اكتمال العملية ويفشل الاختبار.\n   - **حركات الواجهة والـ Animations**: حركات التلاشي والانتقالات تؤخر ظهور العناصر. **الحل**: تعطيل جميع حركات النظام في المحاكي قبل بدء الاختبارات.\n   - **التنافس الشبكي (Network Timing Races)**: الاتصال بسيرفرات حقيقية. **الحل**: استخدام MockWebServer محلي أو Fakes.\n\n"
            "3. أدوات التحكم والمزامنة الحتمية:\n   - **في Compose**: استخدام `composeTestRule.mainClock.autoAdvance = false` للتحكم في تقدم الإطارات يدوياً.\n   - **في Espresso**: استخدام `CountingIdlingResource` أو تحويل الكود إلى Coroutines يتم التحكم بها عبر `StandardTestDispatcher`.\n   - **Android Test Orchestrator**: تشغيل كل اختبار في Process مستقلة تماماً ومسح بيانات التطبيق بين الاختبارات لمنع تراكم الحالة."
        ),
        "practical_walkthrough": (
            "تعطيل Animations النظام برمجياً عبر ADB واستخدام IdlingResource أو MainClock في Compose:\n"
            "```bash\n"
            "# 1. أوامر إجبارية في CI لتعطيل الـ Animations في المحاكي ومنع الـ Flakiness:\n"
            "adb shell settings put global window_animation_scale 0\n"
            "adb shell settings put global transition_animation_scale 0\n"
            "adb shell settings put global animator_duration_scale 0\n"
            "```\n\n"
            "```kotlin\n"
            "// 2. التحكم الحتمي في ساعة Compose لمنع سباقات التوقيت مع الأنيميشن:\n"
            "@Test\n"
            "fun testAnimatedBannerAppearsDeterministically() {\n"
            "    // إيقاف التقدم التلقائي لساعة الـ Frame Clock:\n"
            "    composeTestRule.mainClock.autoAdvance = false\n"
            "\n"
            "    composeTestRule.setContent {\n"
            "        AnimatedBannerScreen()\n"
            "    }\n"
            "\n"
            "    // التقدم بالساعة 500ms حتمياً لإكمال الأنيميشن بدقة:\n"
            "    composeTestRule.mainClock.advanceTimeBy(500)\n"
            "\n"
            "    composeTestRule.onNodeWithText(\"Welcome Back\")\n"
            "        .assertIsDisplayed()\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Eliminate UI flakiness by banning Thread.sleep(), disabling system animations on test devices, mocking external network boundaries with MockWebServer, controlling Compose clocks deterministically via mainClock.autoAdvance = false, and running tests in isolated processes via Android Test Orchestrator.",
        "best_answer": (
            "Flaky UI tests degrade engineering trust and stall deployment pipelines. Eliminating flakiness requires controlling concurrency, animation timing, and environment isolation:\n\n"
            "1. **Ban Arbitrary Sleeps**:\n"
            "   - Never write `Thread.sleep(2000)`. Use synchronization hooks: in Espresso, register `CountingIdlingResource`; in Compose, rely on native auto-synchronization or manually advance `composeTestRule.mainClock`.\n\n"
            "2. **Disable System Animations on CI Devices**:\n"
            "   - UI tests click coordinates based on settled layout trees. If a window transition or fade animation is midway, clicks miss targets. Execute shell commands on CI emulators to disable all animation scales (`window_animation_scale 0`, `transition_animation_scale 0`, `animator_duration_scale 0`).\n\n"
            "3. **Hermetic Test Environments**:\n"
            "   - Flakiness often mirrors network flakiness. Mock external HTTP endpoints using `MockWebServer` running on `localhost`. Isolate storage by resetting test databases between tests.\n\n"
            "4. **Android Test Orchestrator**:\n"
            "   - Enable `execution 'ANDROIDX_TEST_ORCHESTRATOR'`. Orchestrator launches each test method in its own fresh `Instrumentation` process, clearing application memory, static singletons, and SQLite files between runs."
        ),
        "deep_answer": (
            "From an infrastructure resilience perspective, managing flaky tests at scale requires quarantine policies and sharding:\n\n"
            "1. **Automated Quarantine Pipelines**: Implement CI tooling (e.g., Flank or Test Grid) that tracks test pass rates over 14 days. If a test fails intermittently without code changes, automatically flag it as `@FlakyTest`, quarantine it into a non-blocking diagnostic suite, and alert the owning team.\n\n"
            "2. **Targeted Polling Matchers (`waitUntil`)**: When awaiting complex asynchronous conditions in Compose, use explicit condition timeouts:\n   ```kotlin\n   composeTestRule.waitUntil(timeoutMillis = 5000) {\n       composeTestRule.onAllNodesWithText(\"Ready\").fetchSemanticsNodes().isNotEmpty()\n   }\n   ```\n   This polls at frame boundaries, proceeding immediately when the condition is satisfied rather than waiting for worst-case time ceilings.\n\n"
            "3. **Device Matrix Sharding**: Shard instrumentation suites across 4–8 parallel emulators in CI. Sharding keeps individual runner sessions under 5 minutes, preventing emulator memory bloat and thermal throttling that cause late-suite test timeouts."
        ),
        "follow_ups": [
            {
                "question": "What does Android Test Orchestrator do?",
                "answer": "It runs each test in its own dedicated Android instrumentation process, ensuring zero state or static memory leaks between test executions."
            },
            {
                "question": "How does composeTestRule.waitUntil() differ from Thread.sleep()?",
                "answer": "waitUntil polls a condition predicate on every frame clock tick and unblocks immediately when true, avoiding wasted time and race conditions."
            }
        ]
    },
    {
        "id": "TST-16",
        "arabic_explanation": (
            "ما هي المعايير الدقيقة لتحديد ما يجب اختباره كـ Unit Test على الـ JVM وما يجب التحقق منه على محاكي أو جهاز حقيقي (Emulator/Device)؟\n\n"
            "1. المبدأ المعماري التوجيهي (The Golden Rule):\n   - **اختبر على الـ JVM المحلي كل ما هو منطق برمجي بحت (Logic & State)**.\n   - **اختبر على الجهاز الحقيقي كل ما يعتمد على عتاد الهاتف، نظام التشغيل، أو تعاريف النظام المنخفضة (Hardware, OS Drivers, Security)**.\n\n"
            "2. ما يجب اختباره حصرياً كـ Unit Test على JVM (`src/test/`):\n   - منطق الـ ViewModels وتدفقات الـ StateFlow والـ Events.\n   - الـ UseCases وقواعد العمل وحسابات الأسعار والخصومات.\n   - خوارزميات تحويل وتنسيق البيانات (Mappers & Adapters).\n   - محاكاة أخطاء الـ API والـ Retries عبر MockWebServer.\n\n"
            "3. ما يجب اختباره على جهاز حقيقي أو محاكي (`src/androidTest/`):\n   - **العمليات التشفيرية العتادية (Android Keystore / StrongBox)**: الـ TEE والـ Hardware Keymaster غير موجودين على JVM!\n   - **المصادقة البيومترية (BiometricPrompt)**: تتطلب عتاد مستشعر البصمة ونظام النظام.\n   - **ترقيات قاعدة البيانات (Room Migrations)**: لاختبار محرك SQLite الحقيقي للأندرويد.\n   - **الرسم المتقدم والـ Custom Views والأداء**: قياس الـ Frame Drops (JankStats) واختبارات الـ Macrobenchmark.\n   - **مكونات الـ IPC والـ AndroidManifest**: مثل الـ ContentProviders و Deep Links والـ BroadcastReceivers."
        ),
        "practical_walkthrough": (
            "المقارنة بين كود يختبر على الـ JVM وكود يستحيل اختباره إلا على جهاز حقيقي:\n"
            "```kotlin\n"
            "// 1. يختبر على الـ JVM في 5ms (منطق أعمال نقي - Domain Logic):\n"
            "class LoanEligibilityCalculatorTest {\n"
            "    @Test\n"
            "    fun `eligible for loan when credit score above 700`() {\n"
            "        val calculator = LoanEligibilityCalculator()\n"
            "        val isEligible = calculator.evaluate(creditScore = 720, debtToIncomeRatio = 0.25)\n"
            "        assertTrue(isEligible)\n"
            "    }\n"
            "}\n"
            "\n"
            "// 2. يستحيل اختباره إلا على جهاز/محاكي حقيقي (تشفير عتادي بالـ Keystore):\n"
            "@RunWith(AndroidJUnit4::class)\n"
            "class HardwareKeystoreCryptoTest {\n"
            "    @Test\n"
            "    fun `keystore generates hardware key and encrypts payload`() {\n"
            "        val cryptoManager = KeystoreCryptoManager()\n"
            "        val secret = \"ConfidentialToken123\".toByteArray()\n"
            "        \n"
            "        val encrypted = cryptoManager.encrypt(secret)\n"
            "        val decrypted = cryptoManager.decrypt(encrypted)\n"
            "        \n"
            "        // يعتمد على شريحة الـ Keymaster الحقيقية داخل الهاتف:\n"
            "        assertEquals(\"ConfidentialToken123\", String(decrypted))\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Test pure business rules, ViewModels, UseCases, mappers, and state machines on the local JVM for millisecond speed. Reserve on-device/emulator tests for framework and hardware boundaries: Android Keystore, BiometricPrompt, Room SQLite migrations, Macrobenchmark performance, and IPC components.",
        "best_answer": (
            "Allocating tests between the local JVM and real devices balances execution economics against operational fidelity:\n\n"
            "1. **Local JVM Tests (`src/test/`) — The 80% Rule**:\n"
            "   - **Scope**: ViewModels, pure domain UseCases, reactive StateFlow pipelines, business algorithms, DTO mappers, and state machines.\n   - **Why JVM**: Executes in milliseconds. Zero emulator boot overhead. Allows rapid Test-Driven Development (TDD) iteration without blocking local machines.\n\n"
            "2. **On-Device / Emulator Tests (`src/androidTest/`) — The 20% Rule**:\n"
            "   - **Hardware & Security Boundaries**: Android Keystore hardware-backed keys, Secure Element operations, and `BiometricPrompt` flows (the JVM has no Keymaster TEE daemon).\n   - **Real SQLite Engine**: Room database migrations and complex multi-threaded WAL transactions (desktop SQLite diverges from mobile OEM SQLite builds).\n   - **Framework IPC**: Validating exported ContentProviders, BroadcastReceivers, and Deep Link intent filter matching.\n   - **Performance Profiling**: Baseline Profiles and Macrobenchmark measuring real frame rendering and startup latency."
        ),
        "deep_answer": (
            "From an engineering resource allocation and cloud cost perspective, minimizing on-device testing saves thousands of engineering hours:\n\n"
            "1. **The Infrastructure Cost Calculation**: 1,000 local unit tests execute in ~10 seconds on a standard GitHub Actions runner. 1,000 instrumented tests require spinning up dozens of nested-virtualization emulator containers, consuming 40+ minutes of cloud runner compute and thousands of dollars in monthly CI billing.\n\n"
            "2. **Robolectric as the Middle Tier**: Where code requires light Android framework abstractions (e.g. `Bundle`, `Intent`, `Parcelable`, or `ColorRes`), use Robolectric on the JVM. This keeps tests in `src/test/` while providing simulated framework fidelity without emulator overhead.\n\n"
            "3. **Architectural Separation as an Enabler**: When architecture cleanly decouples domain logic into pure Kotlin modules (`:core:domain`), developers are physically prevented from importing Android framework classes, ensuring code remains 100% JVM testable by design."
        ),
        "follow_ups": [
            {
                "question": "Can Android Keystore encryption be tested on a standard JVM unit test?",
                "answer": "No; AndroidKeyStore is an Android OS system provider coupled to hardware daemons (keystored/TEE), throwing NoSuchProviderException on a plain JVM."
            },
            {
                "question": "Why should Macrobenchmark tests run only on physical devices or specialized emulators?",
                "answer": "Because standard emulators have artificial thermal and CPU profiles; Macrobenchmark requires real hardware to measure true user-perceived frame drops and cold start times."
            }
        ]
    }
]


def update_tst_data() -> None:
    data = []
    if DATA_FILE.exists():
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))

    existing_map = {item["id"]: item for item in data}
    for item in TST_09_16:
        existing_map[item["id"]] = item

    updated = [existing_map[k] for k in sorted(existing_map.keys())]
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(updated, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {DATA_FILE} with questions TST-09 to TST-16. Total questions: {len(updated)}")


if __name__ == "__main__":
    update_tst_data()
