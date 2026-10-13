#!/usr/bin/env python3
"""Generator for TST-01 through TST-08 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "tst.json"

TST_01_08 = [
    {
        "id": "TST-01",
        "arabic_explanation": (
            "قارن بين اختبارات الوحدة (Unit)، والتكامل (Integration)، والأجهزة (Instrumentation)، والواجهة (UI)، والنهاية للنهاية (End-to-End)؟\n\n"
            "1. طيف الاختبارات في أندرويد (The Android Testing Spectrum):\n   - **Unit Tests (Local JVM Tests)**: تُنفذ على الـ JVM المحلي داخل الحاسوب دون الحاجة لمشغل أو محاكي أندرويد (`src/test/`). سريعة جداً (بضعة أجزاء من الثانية لكل اختبار)، وتختبر دالة أو كلاس واحد بمعزل عن النظام (ViewModels, UseCases, Mappers).\n   - **Integration Tests**: تختبر تفاعل مكونين أو أكثر معاً للتأكد من صحة الاتصال (مثل اختبار Repository يتصل بـ Room Database محلية أو MockWebServer).\n   - **Instrumentation Tests (On-Device Tests)**: تتطلب تشغيل جهاز أندرويد حقيقي أو محاكي (`src/androidTest/`). تختبر كوداً يعتمد على Android Framework الحقيقي (SQLite، SharedPreferences، الخدمات، ومدير الحزم).\n   - **UI Tests (Compose / Espresso)**: تختبر الشاشات وتفاعل المستخدم (الضغط على الأزرار، التمرير، وظهور النصوص وقراءة Semantics شجرة الـ Compose).\n   - **End-to-End Tests (E2E)**: تختبر تدفق المستخدم الكامل من البداية للنهاية (تسجيل دخول -> إضافة للسلة -> إتمام الدفع عبر بيئة Staging حقيقية).\n\n"
            "2. المفاضلات الهندسية (Trade-offs):\n   - كلما صعدت لأعلى (من Unit إلى E2E): تزداد الموثوقية وواقعية الاختبار، ولكن **تزداد التكلفة والبطء واحتمالية الاختبارات المتقلبة (Flakiness)**."
        ),
        "practical_walkthrough": (
            "المقارنة بين Unit Test سريع على JVM و Instrumented Test يتطلب جهازاً حقيقياً في Room:\n"
            "```kotlin\n"
            "// 1. Unit Test سريع في src/test/ (ينفذ في 10ms على JVM بدون أندرويد):\n"
            "class PriceCalculatorTest {\n"
            "    @Test\n"
            "    fun `calculateDiscount applies percentage correctly`() {\n"
            "        val calculator = PriceCalculator()\n"
            "        val finalPrice = calculator.applyDiscount(originalPrice = 100.0, discountPercent = 20)\n"
            "        assertEquals(80.0, finalPrice, 0.001)\n"
            "    }\n"
            "}\n"
            "\n"
            "// 2. Instrumented Integration Test في src/androidTest/ (يتطلب محاكي لفحص SQLite الحقيقي):\n"
            "@RunWith(AndroidJUnit4::class)\n"
            "class UserDaoTest {\n"
            "    private lateinit var db: AppDatabase\n"
            "    private lateinit var userDao: UserDao\n"
            "\n"
            "    @Before\n"
            "    fun createDb() {\n"
            "        val context = ApplicationProvider.getApplicationContext<Context>()\n"
            "        db = Room.inMemoryDatabaseBuilder(context, AppDatabase::class.java).build()\n"
            "        userDao = db.userDao()\n"
            "    }\n"
            "\n"
            "    @Test\n"
            "    fun insertAndReadUser() = runTest {\n"
            "        val user = UserEntity(id = \"1\", name = \"Ahmed\")\n"
            "        userDao.insert(user)\n"
            "        val byId = userDao.getUserById(\"1\")\n"
            "        assertEquals(\"Ahmed\", byId?.name)\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Unit tests run on the local JVM in milliseconds testing isolated logic. Integration tests verify interactions between components like repositories and databases. Instrumentation tests run on Android devices/emulators testing framework code. UI tests verify user interactions, and E2E tests validate complete user journeys across real backends.",
        "best_answer": (
            "The Android testing spectrum balances execution speed, maintenance costs, and production confidence:\n\n"
            "1. **Local Unit Tests (`src/test/`)**:\n"
            "   - Execute on the host machine's JVM without an emulator. Run in milliseconds. Ideal for ViewModels, pure domain UseCases, business algorithms, and data mappers.\n\n"
            "2. **Integration Tests**:\n"
            "   - Verify that multiple collaborating units interact correctly across module boundaries (e.g. testing Room DAOs against SQLite, or network parsers against OkHttp MockWebServer).\n\n"
            "3. **Instrumentation Tests (`src/androidTest/`)**:\n"
            "   - Execute inside an Android OS process on physical hardware or emulators. Used whenever real Android OS runtime primitives (ART, Binder IPC, Keystore, real SQLite drivers) must be validated.\n\n"
            "4. **UI Tests (Compose Test / Espresso)**:\n"
            "   - Programmatically interact with UI nodes: asserting text presence, triggering clicks, verifying recomposition stability and accessibility semantics.\n\n"
            "5. **End-to-End (E2E) Tests**:\n"
            "   - Exercise complete end-to-end user journeys (e.g., login, onboarding, checkout) against staging server infrastructure. Provide highest confidence, but carry highest execution duration and flake risks."
        ),
        "deep_answer": (
            "From an engineering management and CI governance perspective, test tiering dictates pipeline velocity:\n\n"
            "1. **The Cost-Velocity Ratio**: 1,000 local unit tests run in 5 seconds on developer machines and cost zero cloud infrastructure. 20 UI instrumentation tests require booting an emulator, waiting for system initialization, and running for 5 minutes. High-performing engineering teams push 70–80% of test coverage into fast local JVM unit tests.\n\n"
            "2. **Robolectric vs. Instrumentation**: Robolectric allows running Android framework tests (like inspecting Android Intent extras, Context resources, or Fragment lifecycles) directly on the local JVM by shadowing Android bytecode. It bridges the gap between speed and framework verification, though it does not replace real device verification for hardware-accelerated rendering or SQLite edge cases.\n\n"
            "3. **Hermetic Test Environments**: Reliable CI pipelines mandate hermetic test boundaries. E2E tests that communicate with live external third-party services (e.g. live payment gateways) flake due to network latency; mock external boundaries using WireMock or controlled test stubs."
        ),
        "follow_ups": [
            {
                "question": "What is Robolectric and when should you use it?",
                "answer": "A framework that provides simulated Android bytecode on the local JVM, allowing Android framework-dependent tests to run in seconds without an emulator."
            },
            {
                "question": "Why are E2E tests often flaky in continuous integration pipelines?",
                "answer": "Due to external dependencies: network timeouts, test database state contamination, asynchronous UI animation delays, and backend server restarts."
            }
        ]
    },
    {
        "id": "TST-02",
        "arabic_explanation": (
            "قارن بين الـ Dummy، والـ Fake، والـ Stub، والـ Spy، والـ Mock، ومفهوم الـ Test Double العام وفقاً لمعايير مارتن فاولر؟\n\n"
            "1. ما هو الـ Test Double؟\n   - هو المفهوم المظلي الشامل لأي كائن بديل يُستخدم في بيئة الاختبار ليحل محل كائن حقيقي معقد أو يعتمد على موارد خارجية (مثل الشبكة أو قاعدة البيانات).\n\n"
            "2. الأنواع الخمسة للـ Test Doubles:\n   - **1. Dummy**: كائن يمرر فقط لملء المعاملات المطلوبة (Parameters) لتفادي أخطاء الـ NullPointerException، ولا يتم استخدام كوده أو استدعاء دواله إطلاقاً.\n   - **2. Stub**: كائن يقدم إجابات معلبة وجاهزة مسبقاً (Canned Answers) لاستدعاءات محددة أثناء الاختبار (مثلاً: دالة `getUser()` تعيد دائماً مستخدماً ثابتاً `User(\"1\")`).\n   - **3. Spy**: كائن يسجل معلومات حول كيفية استدعائه (مثل: كم مرة تم استدعاؤه، وما هي المعاملات التي مُررت له) للتحقق منها لاحقاً.\n   - **4. Mock**: كائن مبرمج مسبقاً بتوقعات صريحة (Expectations)؛ يتحقق تلقائياً من استدعاء دوال محددة بترتيب محدد عبر أدوات مثل MockK أو Mockito.\n   - **5. Fake**: **البديل الأفضل والأكثر موثوقية**! كائن يملك تنفيذاً حقيقياً وشغالاً لمنطق العمل (Working Implementation)، ولكنه يعتمد على اختصار خفيف (مثل استبدال قاعدة بيانات SQLite بـ `MutableList` في الذاكرة)."
        ),
        "practical_walkthrough": (
            "المقارنة البرمجية بين كتابة Fake قوي وكتابة Mock هش باستخدام MockK:\n"
            "```kotlin\n"
            "// 1. Fake Repository (تطبيق شغال وقوي وخالٍ من الهشاشة في الذاكرة):\n"
            "class FakeUserRepository : UserRepository {\n"
            "    private val users = mutableMapOf<String, User>()\n"
            "\n"
            "    override suspend fun getUser(id: String): User? = users[id]\n"
            "    override suspend fun saveUser(user: User) {\n"
            "        users[user.id] = user\n"
            "    }\n"
            "}\n"
            "\n"
            "// 2. استخدام Mock عبر MockK (يتحقق من تفاصيل الاستدعاء ولكنه قد يكون هشاً عند إعادة الهيكلة):\n"
            "class UserViewModelTest {\n"
            "    @Test\n"
            "    fun `loadUser calls repository exactly once with mock`() = runTest {\n"
            "        val mockRepo = mockk<UserRepository>()\n"
            "        coEvery { mockRepo.getUser(\"101\") } returns User(\"101\", \"Mohamed\")\n"
            "\n"
            "        val viewModel = UserViewModel(mockRepo)\n"
            "        viewModel.loadUser(\"101\")\n"
            "\n"
            "        // التحقق من أن الدالة تم استدعاؤها تحديداً مرة واحدة بنفس الـ ID:\n"
            "        coVerify(exactly = 1) { mockRepo.getUser(\"101\") }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Test double is the umbrella term. Dummies fill parameter slots without being used. Stubs return canned responses. Spies record interactions for verification. Mocks define pre-programmed expectations verified on assertions. Fakes provide lightweight, working in-memory implementations (like an in-memory list repository).",
        "best_answer": (
            "Understanding test doubles follows the classic Martin Fowler taxonomy:\n\n"
            "1. **Dummy**:\n"
            "   - Objects passed around simply to satisfy method signatures (e.g. an empty constructor parameter), never actually interrogated or invoked.\n\n"
            "2. **Stub**:\n"
            "   - Provides canned responses to method calls during a test (e.g. `every { api.getUser() } returns sampleUser`). Stubs do not verify interaction behavior; they only supply required data state.\n\n"
            "3. **Spy**:\n"
            "   - Wraps a real or stubbed instance to record telemetry: capturing argument parameters, invocation counts, and order of calls for post-execution assertions.\n\n"
            "4. **Mock**:\n"
            "   - Objects pre-programmed with expected interaction behavior and verified at assertion time (`verify { service.trackEvent(\"purchase\") }`). Mocks focus on behavior verification rather than state verification.\n\n"
            "5. **Fake**:\n"
            "   - Objects that have working business logic, but take shortcuts unsuitable for production (e.g., an in-memory `FakeUserRepository` backed by a `ConcurrentHashMap` rather than SQLite)."
        ),
        "deep_answer": (
            "From a software maintainability and Google engineering practices perspective, Fakes are heavily favored over Mocks:\n\n"
            "1. **The Fragility of Over-Mocking**: Tests relying heavily on MockK/Mockito verify implementation details (which methods were called and how many times) rather than observable behavior and state. When an engineer refactors internal repository code to batch calls or use caching, mocked tests break instantly despite correct user behavior.\n\n"
            "2. **Fakes Enable Realistic Multi-Feature Tests**: A well-designed `FakeCartRepository` behaves like the real repository: saving items, updating quantities, and emitting reactive state flows. Multiple ViewModels and tests can share the same fake across integration suites with zero mocking boilerplate.\n\n"
            "3. **When Mocks are Justified**: Use mocks sparingly: primarily for un-fakeable external boundaries where asserting exact side effects is the direct goal (e.g. asserting that a payment SDK's `initiatePayment()` or analytics tracker was triggered exactly once)."
        ),
        "follow_ups": [
            {
                "question": "Why does Google's Android testing guidance recommend Fakes over Mocks for Repositories?",
                "answer": "Fakes provide realistic stateful behavior, survive internal code refactoring without breaking tests, and can be reused across hundreds of tests without brittle mock setup."
            },
            {
                "question": "What is the risk of using relaxed mocks in MockK (relaxed = true)?",
                "answer": "Relaxed mocks return default dummy values (0, empty string, null) for unmocked calls, which can mask missing setup errors and hide broken data flow."
            }
        ]
    },
    {
        "id": "TST-03",
        "arabic_explanation": (
            "ما هي الأدوار المحددة لكل من JUnit 4/5، و MockK/Mockito، و Espresso، و Compose UI Testing في منظومة الاختبار؟\n\n"
            "1. إطار عمل الاختبارات الأساسي (JUnit 4 vs. JUnit 5):\n   - **JUnit (Test Runner & Lifecycle)**: هو الإطار الأساسي الذي ينظم الاختبارات (`@Test`, `@Before`, `@After`) ويدير دورة حياة التشغيل وفحص التوكيدات (`assertEquals`).\n   - JUnit 5 يوفر ميزات متقدمة: Nested Tests (`@Nested`), Parameterized Tests (`@ParameterizedTest`), و Display Names.\n\n"
            "2. مكتبات المحاكاة (MockK vs. Mockito):\n   - **Mockito**: مكتبة Java الشهيرة؛ كانت تواجه صعوبات مع كلاسات Kotlin المغلقة (final classes) ودوال الـ Coroutines المعلقة (Suspend functions).\n   - **MockK**: مكتبة بنيت من الصفر بلغة كوتلن! تدعم Coroutines بشكل طبيعي (`coEvery`, `coVerify`), وتدعم الـ Extension functions, والـ Object singletons, والـ Sealed classes.\n\n"
            "3. اختبارات الواجهة التقليدية (Espresso):\n   - مخصصة للـ View System القديم (XML). تعتمد على معادلة: `onView(withId(...)).perform(click()).check(matches(isDisplayed()))`.\n   - مشكلتها التاريخية: عدم استقرار المزامنة مع العمليات غير المتزامنة والحاجة لـ IdlingResources.\n\n"
            "4. اختبارات واجهات Compose (Compose UI Testing):\n   - تعتمد على شجرة المعاني (Semantics Tree) بدلاً من معرّفات الـ IDs: `composeTestRule.onNodeWithText(\"Submit\").performClick()`.\n   - **مزامنة تلقائية مدمجة (Auto-Synchronization)**: تنتظر اكتمال الـ Recomposition والـ Animations تلقائياً قبل فحص النتائج."
        ),
        "practical_walkthrough": (
            "المقارنة بين اختبار Espresso القديم واختبار Compose الحديث المعتمد على Semantics:\n"
            "```kotlin\n"
            "// 1. اختبار واجهة قديم بـ Espresso في XML (يعتمد على ViewMatcher و R.id):\n"
            "@Test\n"
            "fun legacyEspressoTest() {\n"
            "    onView(withId(R.id.login_button))\n"
            "        .check(matches(isDisplayed()))\n"
            "        .perform(click())\n"
            "    onView(withId(R.id.error_text))\n"
            "        .check(matches(withText(\"Invalid password\")))\n"
            "}\n"
            "\n"
            "// 2. اختبار واجهة حديث بـ Compose Testing (يعتمد على Semantics Tree والمزامنة التلقائية):\n"
            "@get:Rule\n"
            "val composeTestRule = createComposeRule()\n"
            "\n"
            "@Test\n"
            "fun modernComposeUiTest() {\n"
            "    composeTestRule.setContent {\n"
            "        LoginScreen(onLoginSubmitted = { /* ... */ })\n"
            "    }\n"
            "\n"
            "    // البحث عن العقد في شجرة الـ Semantics والتفاعل معها بسلاسة:\n"
            "    composeTestRule.onNodeWithText(\"Log In\")\n"
            "        .assertIsDisplayed()\n"
            "        .performClick()\n"
            "\n"
            "    composeTestRule.onNodeWithText(\"Invalid password\")\n"
            "        .assertIsDisplayed()\n"
            "}\n"
            "```"
        ),
        "quick_answer": "JUnit manages test lifecycles and execution assertions. MockK provides Kotlin-idiomatic mocking with first-class coroutine suspend support. Espresso automates legacy XML View hierarchies, while Compose UI Testing inspects the Semantics Tree with built-in auto-synchronization for compositions and animations.",
        "best_answer": (
            "The modern Android testing stack divides responsibilities across runner, mocking, and UI automation layers:\n\n"
            "1. **JUnit (Test Execution Framework)**:\n"
            "   - Provides test suite runners, lifecycle hooks (`@BeforeEach`, `@AfterEach`), assertions, and dynamic test execution. JUnit 4 remains default in many AGP setups, while JUnit 5 provides parameterized tests and nested hierarchy structures.\n\n"
            "2. **MockK vs. Mockito (Mocking Engines)**:\n"
            "   - While Mockito originated in Java, **MockK** was engineered specifically for Kotlin. It natively handles Kotlin language constructs without configuration hacks: coroutine suspend functions (`coEvery`, `coVerify`), extension functions, private methods, and Kotlin object singletons.\n\n"
            "3. **Espresso (View Hierarchy Automation)**:\n"
            "   - Interacts with traditional Android View trees via Matcher/Action/Assertion chains (`onView().perform().check()`). Requires custom `IdlingResource` implementations to coordinate background async operations.\n\n"
            "4. **Compose UI Testing**:\n"
            "   - Driven via `createComposeRule()`. Rather than querying layout IDs, it inspects the **Semantics Tree** (`onNodeWithText`, `onNodeWithContentDescription`). Features native automatic clock synchronization that waits for recomposition passes and animations to settle before evaluating assertions."
        ),
        "deep_answer": (
            "From an architectural quality perspective, Compose UI tests solve the long-standing synchronization problem in Android testing:\n\n"
            "1. **Idling & Clock Synchronization**: In Espresso, tests frequently flaked because animations or background threads caused race conditions unless engineers manually registered `IdlingResource` instances. In Compose, the test framework hooks directly into the Compose frame clock (`mainClock`). It pauses virtual time, advances frame-by-frame, and automatically synchronizes with coroutines launched within the composition.\n\n"
            "2. **Isolated Screen / Component Unit Tests**: Compose UI tests do not require launching a heavy full-screen Activity. Using `createComposeRule()`, you can mount a single composable button or card in isolation (`composeTestRule.setContent { MyCustomCard() }`), testing UI rendering and click callbacks in under 1 second without full screen navigation.\n\n"
            "3. **Semantics for Accessibility & Testing**: Compose testing forces accessibility best practices. Because nodes are selected via semantics (`contentDescription`, `onClick`, `text`), designing a testable Compose UI inherently produces accessible software for Screen Readers (TalkBack)."
        ),
        "follow_ups": [
            {
                "question": "How do you control animations in Compose UI tests?",
                "answer": "Use composeTestRule.mainClock.autoAdvance = false and manually call mainClock.advanceTimeBy(millis) to assert UI states at specific animation frames."
            },
            {
                "question": "Can MockK mock final classes and methods in Kotlin by default?",
                "answer": "Yes, MockK uses dynamic bytecode generation (Byte Buddy) to mock final classes and methods natively without requiring special plugin configurations."
            }
        ]
    },
    {
        "id": "TST-04",
        "arabic_explanation": (
            "ما الذي يجعل الكلاس أو المكون البرمجي قابلاً للاختبار (Testable) في معمارية أندرويد الحديثة؟\n\n"
            "1. الخصائص الهندسية للكود القابل للاختبار (Testability Attributes):\n   - **حقن التبعيات الصريح (Constructor Dependency Injection)**: استقبال كل التبعيات عبر الـ Constructor بدلاً من إنشائها داخلياً (`val repo = UserRepositoryImpl()`) أو الاعتماد على Singletons عامة.\n   - **الاعتماد على التجريد (Depend on Abstractions / Interfaces)**: جعل الكلاس يعتمد على Interface للـ Repository والـ Services يتيح استبدالها بـ Fakes في الاختبارات.\n   - **حقن مشغلات الكوروتين (Coroutine Dispatcher Injection)**: عدم كتابة `Dispatchers.IO` صراحة داخل الكود! يجب تمرير الـ Dispatcher في الـ Constructor لاستبداله بـ `StandardTestDispatcher` في الاختبارات.\n   - **دوال نقية وخالية من الآثار الجانبية (Pure Functions)**: دوال تأخذ مدخلات وتخرج نتائج محددة دون تعديل حالة عامة (State).\n\n"
            "2. ما الذي يدمر قابلية الاختبار (Anti-Patterns)?:\n   - الوصول المباشر لكائنات الـ Android Framework (مثل `Context.getString()`, `SharedPreferences`, `Log.*`) داخل دوال الـ Business Logic.\n   - استخدام `System.currentTimeMillis()` مباشرة (يجعل الاختبار غير حتمي؛ يجب حقن كائن `Clock`)."
        ),
        "practical_walkthrough": (
            "المقارنة بين كلاس غير قابل للاختبار وكلاس مصمم بقابلية اختبار فائقة عبر حقن التبعيات والـ Dispatchers والـ Clock:\n"
            "```kotlin\n"
            "// ❌ كود سيئ يستحيل اختباره في Unit Test منعزل:\n"
            "class BadUserManager(private val context: Context) {\n"
            "    // إنشاء التبعيات داخلياً والاعتماد على Singletons و Dispatcher ثابت ووقت النظام:\n"
            "    private val api = NetworkClient.instance.api\n"
            "    private val prefs = context.getSharedPreferences(\"user_prefs\", Context.MODE_PRIVATE)\n"
            "\n"
            "    fun saveUserSession(token: String) {\n"
            "        CoroutineScope(Dispatchers.IO).launch { // استخدام Dispatchers.IO و Scope غير مراقب!\n"
            "            prefs.edit().putString(\"token\", token).putLong(\"time\", System.currentTimeMillis()).apply()\n"
            "        }\n"
            "    }\n"
            "}\n"
            "\n"
            "// ✅ كود مصمم باحترافية وقابل للاختبار الفوري على الـ JVM:\n"
            "class TestableUserManager @Inject constructor(\n"
            "    private val tokenStorage: TokenStorage,       // مفصول عبر Interface\n"
            "    private val clock: Clock,                     // حقن الوقت لضمان الحتمية في الاختبارات\n"
            "    private val ioDispatcher: CoroutineDispatcher // حقن الـ Dispatcher لاستبداله بـ TestDispatcher\n"
            ") {\n"
            "    suspend fun saveUserSession(token: String) = withContext(ioDispatcher) {\n"
            "        tokenStorage.saveToken(token, timestamp = clock.millis())\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "A class is testable when it receives all dependencies explicitly via its constructor, depends on interfaces rather than concrete singletons, injects CoroutineDispatchers rather than hardcoding Dispatchers.IO, avoids direct Android Context references, and injects Clock abstractions for time.",
        "best_answer": (
            "Testability is a direct reflection of architectural decoupling and inversion of control:\n\n"
            "1. **Constructor Dependency Injection**:\n"
            "   - Classes must never instantiate their own dependencies (`MyRepository()`) or reach out to global singleton state. Passing dependencies via constructors allows unit tests to inject fakes, mocks, or stubs effortlessly.\n\n"
            "2. **Decoupling from the Android Framework**:\n"
            "   - Domain and business logic classes should contain zero imports from `android.*`. Passing `Context` into domain calculators or repositories tethers code to the Android runtime, forcing slow emulator execution or complex mocking.\n\n"
            "3. **Injected Coroutine Dispatchers**:\n"
            "   - Never hardcode `Dispatchers.IO` or `Dispatchers.Default`. Inject dispatchers as constructor parameters (e.g. `@IoDispatcher ioDispatcher: CoroutineDispatcher`). Tests can inject a `StandardTestDispatcher` or `UnconfinedTestDispatcher` to control virtual time deterministically.\n\n"
            "4. **Deterministic Time and Randomness**:\n"
            "   - Never invoke `System.currentTimeMillis()` or `UUID.randomUUID()` directly in business rules. Inject a `Clock` or `IdGenerator` abstraction so tests can assert exact timestamp calculations and deterministic IDs."
        ),
        "deep_answer": (
            "From a software design principles viewpoint, testability directly enforces SOLID principles:\n\n"
            "1. **Single Responsibility Principle (SRP)**: Classes with poor testability usually perform too many duties: fetching data, parsing JSON, formatting strings, and executing navigation. Splitting concerns creates small, cohesive classes whose single responsibility is verified in 3 concise unit tests.\n\n"
            "2. **State Immutability & Observable Streams**: Classes exposing public mutable variables (`var user: User?`) invite race conditions and test state leaks. Testable ViewModels expose immutable `StateFlow<UiState>` streams driven by private unidirectional reducers, making state verification a matter of asserting stream emissions.\n\n"
            "3. **Eliminating Global Static Singletons**: Static state (`object DatabaseHolder`) leaks state across independent unit tests, causing test order dependencies where test B passes if run alone but fails if run after test A. Inversion of control ensures every test creates fresh, isolated instances."
        ),
        "follow_ups": [
            {
                "question": "Why is hardcoding Dispatchers.IO bad for unit testing?",
                "answer": "Because tests cannot control thread scheduling or virtual time on real Dispatchers.IO, leading to race conditions, thread leaks, and flaky tests."
            },
            {
                "question": "How do you test Android resource strings in a pure JVM ViewModel test?",
                "answer": "Expose typed StringResource wrappers or message IDs from the ViewModel; let the Composable layer resolve context.getString(id)."
            }
        ]
    },
    {
        "id": "TST-05",
        "arabic_explanation": (
            "ما هي دالة `runTest` في مكتبة `kotlinx-coroutines-test`، وكيف يعمل الوقت الافتراضي (Virtual Time) و `TestScope`؟\n\n"
            "1. ما هي `runTest`؟\n   - هي أداة تشغيل الكوروتين الرسمية للاختبارات التي حلت محل `runBlockingTest` القديمة.\n   - تقوم بإنشاء **TestScope** مخصص للاختبار يتحكم بالكامل في تقدم الوقت وتزامن الـ Coroutines.\n\n"
            "2. سحر الوقت الافتراضي (Virtual Time & Delay Skipping):\n   - إذا كان الكود يحتوي على تأخير زمني: `delay(10_000L)` (10 ثوانٍ)، فإن اختبار الـ Unit العادي بـ `runBlocking` سيتجمد وينتظر 10 ثوانٍ كاملة في العالم الحقيقي!\n   - مع `runTest`، **يتم تخطي التأخير الزمني تلقائياً (Delay Skipping)**! الـ TestScope يقفز بالوقت الافتراضي 10 ثوانٍ للأمام في أقل من جزء من الثانية (`currentTime += 10000`) دون أي انتظار حقيقي!\n\n"
            "3. التحكم بالوقت عبر `advanceTimeBy` و `advanceUntilIdle`:\n   - **`advanceTimeBy(millis)`**: يتقدم بالوقت الافتراضي بمقدار محدد وينفذ الـ Coroutines المجدولة في ذلك النطاق الزمني.\n   - **`advanceUntilIdle()`**: يفرغ طابور المهام وينفذ كل الكوروتينات المعلقة حتى يفرغ الطابور تماماً.\n\n"
            "4. التحقق التلقائي من عدم تسريب الكوروتينات (Coroutine Leak Detection):\n   - عند انتهاء بلوك `runTest`، تفحص الدالة الـ Scope؛ إذا كان هناك كوروتين لا زال قيد التشغيل ولم يكتمل، يفشل الاختبار فوراً لمنع تسريب العمليات في الخلفية."
        ),
        "practical_walkthrough": (
            "اختبار دالة تحتوي على تأخير زمني طويل عبر runTest وتخطي الوقت الافتراضي:\n"
            "```kotlin\n"
            "class TimerViewModel : ViewModel() {\n"
            "    var countdownFinished = false\n"
            "        private set\n"
            "\n"
            "    fun startTimer() {\n"
            "        viewModelScope.launch {\n"
            "            delay(60_000L) // انتظار دقيقة كاملة!\n"
            "            countdownFinished = true\n"
            "        }\n"
            "    }\n"
            "}\n"
            "\n"
            "class TimerTest {\n"
            "    @Test\n"
            "    fun `test countdown fast-forwards 60 seconds instantly`() = runTest {\n"
            "        // 1. إعداد الـ Dispatcher التجريبي\n"
            "        val testDispatcher = StandardTestDispatcher(testScheduler)\n"
            "        Dispatchers.setMain(testDispatcher)\n"
            "\n"
            "        val viewModel = TimerViewModel()\n"
            "        viewModel.startTimer()\n"
            "\n"
            "        // قبل تقدم الوقت: العد لم ينتهِ\n"
            "        assertFalse(viewModel.countdownFinished)\n"
            "\n"
            "        // 2. التقدم بالوقت الافتراضي دقيقة كاملة في 1 ميلي ثانية:\n"
            "        advanceTimeBy(60_000L)\n"
            "        runCurrent() // تنفيذ المهام المجدولة عند هذا التوقيت\n"
            "\n"
            "        // 3. التحقق من اكتمال الحدث بنجاح:\n"
            "        assertTrue(viewModel.countdownFinished)\n"
            "\n"
            "        Dispatchers.resetMain()\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "runTest is the official coroutine test runner that executes tests inside a TestScope equipped with virtual time. It automatically skips delays so that long delay() operations resolve instantaneously, provides fine-grained control via advanceTimeBy() and advanceUntilIdle(), and asserts that no background jobs are leaked.",
        "best_answer": (
            "`runTest` (from `kotlinx-coroutines-test`) provides deterministic coroutine execution by orchestrating virtual time via `TestScope` and `TestScheduler`:\n\n"
            "1. **Automatic Delay Skipping**:\n"
            "   - Calls to `delay(60_000L)` inside coroutines run under `runTest` do not block thread execution for 60 seconds. The underlying `TestScheduler` detects scheduled delays and advances virtual time (`currentTime`) instantaneously, executing tests in milliseconds.\n\n"
            "2. **Fine-Grained Virtual Time Manipulation**:\n"
            "   - `advanceTimeBy(millis)`: Advances virtual time by an exact duration, triggering tasks scheduled within that temporal window.\n   - `runCurrent()`: Executes tasks currently scheduled at the active virtual timestamp without advancing time.\n   - `advanceUntilIdle()`: Continuously drains the scheduler until no pending or delayed tasks remain in the queue.\n\n"
            "3. **Automatic Leak & Exception Detection**:\n"
            "   - Upon exiting the `runTest` block, the runner asserts that all active children coroutines have concluded. If an orphaned background job remains running, `runTest` throws an `UncompletedCoroutinesError`, guaranteeing clean test boundaries."
        ),
        "deep_answer": (
            "From an advanced concurrency testing perspective, understanding the relationship between runTest, TestScope, and MainDispatcherRule is vital:\n\n"
            "1. **Sharing the TestScheduler**: A frequent testing pitfall occurs when a ViewModel launches coroutines on a `TestDispatcher` that does not share the same `TestScheduler` as `runTest`. In `kotlinx.coroutines.test`, `runTest` creates a root `TestScope`. When replacing `Dispatchers.Main`, you must bind it to the active `testScheduler` (e.g. `StandardTestDispatcher(testScheduler)`) so that time advances synchronously across all coroutine scopes.\n\n"
            "2. **Handling Infinite Loop Coroutines**: If code under test launches an infinite ticker (e.g. `while(isActive) { delay(1000); emit() }`), invoking `advanceUntilIdle()` triggers an infinite loop and crashes with an out-of-memory or timeout error. For infinite loops, advance time incrementally with `advanceTimeBy()` and explicitly cancel the parent job before exiting `runTest`.\n\n"
            "3. **Default Timeout (60 Seconds)**: `runTest` enforces a 60-second virtual time timeout to prevent hanging test suites if non-virtual blocking operations (like standard `Thread.sleep` or un-yielded loops) block the thread."
        ),
        "follow_ups": [
            {
                "question": "What happens if you use Thread.sleep() inside runTest?",
                "answer": "Thread.sleep() blocks the actual operating system thread and cannot be skipped by virtual time, stalling test execution."
            },
            {
                "question": "What is the difference between advanceUntilIdle() and runCurrent()?",
                "answer": "runCurrent() runs only tasks scheduled for the current exact virtual millisecond; advanceUntilIdle() advances virtual time repeatedly until all pending delays execute."
            }
        ]
    },
    {
        "id": "TST-06",
        "arabic_explanation": (
            "قارن بين `StandardTestDispatcher` و `UnconfinedTestDispatcher`، ومتى تختار كلاً منهما في اختبارات الـ Coroutines؟\n\n"
            "1. ما هو `StandardTestDispatcher`؟\n   - هو **الخيار الافتراضي الأكثر دقة وواقعية**.\n   - **السلوك**: لا ينفذ الكوروتين الجديد فوراً! بل يضعه في طابور مهام الـ Scheduler. يتطلب منك استدعاء `runCurrent()` أو `advanceUntilIdle()` صراحة لتقديم التنفيذ.\n   - **الميزة الكبرى**: يتيح لك محاكاة وتدقيق الحالات البينية (Intermediate States) بدقة متناهية (مثلاً: التحقق من أن حالة الـ `Loading` تظهر قبل أن تصل استجابة الشبكة).\n\n"
            "2. ما هو `UnconfinedTestDispatcher`؟\n   - **السلوك**: يبدأ بتنفيذ الكوروتين **فورياً وبشكل متزامن (Eager Execution)** على الخيط الحالي حتى يصل لأول نقطة تعليق (Suspension point).\n   - **الميزة**: كود اختبار أبسط وأقصر؛ لا يتطلب كتابة `runCurrent()` أو `advanceUntilIdle()` بعد كل استدعاء دالة.\n   - **العيب**: قد يتخطى الحالات البينية؛ لأنه يقفز فوراً إلى النتيجة النهائية، مما يجعله غير مناسب لاختبار خطوات مثل شاشات التحميل السريعة.\n\n"
            "3. قاعدة الاختيار الذهبية:\n   - استخدم `UnconfinedTestDispatcher` للاختبارات البسيطة وسريعة الكتابة التي تهتم فقط بالحالة النهائية.\n   - استخدم `StandardTestDispatcher` للاختبارات الدقيقة التي تفحص تسلسل الأحداث، شاشات التحميل، وتدفقات البيانات المعقدة."
        ),
        "practical_walkthrough": (
            "المقارنة العملية: اختبار حالة Loading باستخدام StandardTestDispatcher مقابل تخطيها بـ UnconfinedTestDispatcher:\n"
            "```kotlin\n"
            "class SearchViewModel(private val ioDispatcher: CoroutineDispatcher) : ViewModel() {\n"
            "    var isLoading = false\n"
            "    var results = emptyList<String>()\n"
            "\n"
            "    fun search(query: String) {\n"
            "        viewModelScope.launch(ioDispatcher) {\n"
            "            isLoading = true\n"
            "            delay(500) // محاكاة طلب شبكة\n"
            "            results = listOf(\"Result 1\", \"Result 2\")\n"
            "            isLoading = false\n"
            "        }\n"
            "    }\n"
            "}\n"
            "\n"
            "class DispatcherComparisonTest {\n"
            "    @Test\n"
            "    fun `StandardTestDispatcher allows asserting intermediate loading state`() = runTest {\n"
            "        val dispatcher = StandardTestDispatcher(testScheduler)\n"
            "        val viewModel = SearchViewModel(dispatcher)\n"
            "\n"
            "        viewModel.search(\"Android\")\n"
            "        // مع StandardTestDispatcher: الكوروتين مجدول ولم ينفذ بعد\n"
            "        runCurrent() // تنفيذ الخطوة الأولى حتى أول تعليق\n"
            "        assertTrue(viewModel.isLoading) // نجح التحقق من ظهور الـ Loading!\n"
            "\n"
            "        advanceTimeBy(500)\n"
            "        runCurrent()\n"
            "        assertFalse(viewModel.isLoading) // انتهى الـ Loading وظهرت النتائج\n"
            "        assertEquals(2, viewModel.results.size)\n"
            "    }\n"
            "\n"
            "    @Test\n"
            "    fun `UnconfinedTestDispatcher executes eagerly without runCurrent`() = runTest {\n"
            "        val dispatcher = UnconfinedTestDispatcher(testScheduler)\n"
            "        val viewModel = SearchViewModel(dispatcher)\n"
            "\n"
            "        viewModel.search(\"Android\")\n"
            "        // بدأ فوراً وأصبح isLoading = true تلقائياً دون استدعاء runCurrent\n"
            "        assertTrue(viewModel.isLoading)\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "StandardTestDispatcher queues coroutines without executing them immediately, giving full control over virtual time and intermediate states via advanceUntilIdle() and runCurrent(). UnconfinedTestDispatcher executes coroutines eagerly and synchronously until the first suspension point, offering simpler test code at the cost of skipping intermediate state verification.",
        "best_answer": (
            "Choosing between coroutine test dispatchers dictates how coroutine execution is scheduled relative to test assertions:\n\n"
            "1. **StandardTestDispatcher (Queued & Deterministic)**:\n"
            "   - **Behavior**: Does not execute newly launched coroutines eagerly. Instead, coroutines are queued on the `TestScheduler`.\n   - **Usage**: Requires explicit calls to `runCurrent()`, `advanceTimeBy()`, or `advanceUntilIdle()` to trigger execution.\n   - **Ideal For**: Testing sequential UI progression and intermediate states (e.g., verifying that `UiState.Loading` is emitted before network responses resolve to `UiState.Success`).\n\n"
            "2. **UnconfinedTestDispatcher (Eager & Immediate)**:\n"
            "   - **Behavior**: Newly launched coroutines begin execution immediately and eagerly on the calling thread until they hit their first suspension point (`delay()` or async I/O).\n   - **Usage**: Eliminates boilerplate calls to `runCurrent()` across simple unit tests.\n   - **Ideal For**: Testing simple StateFlow collections or direct state mappings where only the final outcome matters."
        ),
        "deep_answer": (
            "From an architectural best-practices standpoint, standardizing test dispatchers across enterprise codebases avoids flakiness:\n\n"
            "1. **Turbine Flow Testing with StandardTestDispatcher**: When collecting Kotlin Flows using Turbine, `StandardTestDispatcher` provides rock-solid predictability. You can assert that an initial value is emitted, trigger a user action, advance time, and assert that the next emission arrives in order without timing races.\n\n"
            "2. **The MainDispatcherRule Pattern**: Rather than instantiating dispatchers manually in every test class, build a reusable JUnit TestRule:\n   ```kotlin\n   class MainDispatcherRule(val testDispatcher: TestDispatcher = StandardTestDispatcher()) : TestWatcher() {\n       override fun starting(d: Description) = Dispatchers.setMain(testDispatcher)\n       override fun finished(d: Description) = Dispatchers.resetMain()\n   }\n   ```\n   This ensures clean setup and teardown of `Dispatchers.Main` across all JVM unit tests.\n\n"
            "3. **Pragmatic Recommendation**: Default to `StandardTestDispatcher` across the entire codebase. It mimics real-world concurrency queues most faithfully and prevents false-positive test passes where eager execution masks async race conditions."
        ),
        "follow_ups": [
            {
                "question": "Why is Dispatchers.setMain required when testing ViewModels?",
                "answer": "Because viewModelScope launches on Dispatchers.Main by default; on the local JVM, the Android Main thread looper does not exist and throws an IllegalStateException without setMain."
            },
            {
                "question": "Can UnconfinedTestDispatcher skip delays automatically in runTest?",
                "answer": "Yes, both dispatchers share the underlying TestScheduler and skip delay() durations inside runTest blocks."
            }
        ]
    },
    {
        "id": "TST-07",
        "arabic_explanation": (
            "ما هو هرم الاختبارات (Test Pyramid) في أندرويد، وأين تقع اختبارات التعاقد (Contract Tests) ضمن هذا الهرم؟\n\n"
            "1. هرم الاختبارات الكلاسيكي في أندرويد (The Android Testing Pyramid):\n   - **القاعدة (Unit Tests - 70%)**: أكبر عدد من الاختبارات. سريعة، رخيصة، تختبر منطق الأعمال المنعزل على JVM (ViewModels, UseCases, Repositories).\n   - **الوسط (Integration Tests - 20%)**: عدد متوسط. تختبر تفاعل المكونات (Room DB, OkHttp Interceptors, WorkManager).\n   - **القمة (UI & E2E Tests - 10%)**: أقل عدد من الاختبارات. بطيئة، مكلفة، تختبر أهم مسارات المستخدم الحرجة (Critical User Journeys مثل تسجيل الدخول وإتمام الدفع) على أجهزة حقيقية.\n\n"
            "2. أين تقع اختبارات التعاقد (Contract Tests)؟\n   - تقع في **طبقة الـ Integration Tests في منتصف الهرم**.\n   - **وظيفتها**: التحقق من أن العقد المتفق عليه بين تطبيق الموبايل وخادم الـ Backend (الـ API Request & Response JSON Schema) لم ينكسر!\n   - بدلاً من تشغيل اختبار E2E بطيء يتصل بسيرفر حقيقي، يقوم الـ Contract Test بفحص الـ Payload مقابل مواصفات الـ API (مثل Pact أو WireMock) على الـ JVM المحلي في ثوانٍ معدودة!\n\n"
            "3. الفائدة الجوهرية لاختبارات التعاقد:\n   - تمنع كسر التطبيق في الإنتاج عندما يقوم فريق الـ Backend بحذف أو تعديل حقل في الـ JSON دون إعلام فريق الموبايل."
        ),
        "practical_walkthrough": (
            "تنفيذ Contract Test باستخدام MockWebServer للتحقق من توافق الـ JSON Schema مع كلاسات الـ DTO:\n"
            "```kotlin\n"
            "class ApiContractTest {\n"
            "    private lateinit var mockWebServer: MockWebServer\n"
            "    private lateinit var apiService: UserApiService\n"
            "\n"
            "    @Before\n"
            "    fun setup() {\n"
            "        mockWebServer = MockWebServer()\n"
            "        apiService = Retrofit.Builder()\n"
            "            .baseUrl(mockWebServer.url(\"/\"))\n"
            "            .addConverterFactory(MoshiConverterFactory.create())\n"
            "            .build()\n"
            "            .create(UserApiService::class.java)\n"
            "    }\n"
            "\n"
            "    @Test\n"
            "    fun `user profile response contract satisfies expected domain schema`() = runTest {\n"
            "        // محاكاة استجابة الـ JSON المعتمدة في مواصفات الـ OpenAPI:\n"
            "        val contractJson = \"\"\"\n"
            "            {\n"
            "                \"user_id\": \"usr_9988\",\n"
            "                \"email\": \"dev@example.com\",\n"
            "                \"is_active\": true\n"
            "            }\n"
            "        \"\"\".trimIndent()\n"
            "\n"
            "        mockWebServer.enqueue(MockResponse().setResponseCode(200).setBody(contractJson))\n"
            "\n"
            "        val response = apiService.getUserProfile(\"usr_9988\")\n"
            "        \n"
            "        // التحقق من أن السيريالايزر قرأ الحقول بنجاح دون أي تعارض في الأنواع:\n"
            "        assertEquals(\"usr_9988\", response.id)\n"
            "        assertEquals(\"dev@example.com\", response.email)\n"
            "        assertTrue(response.isActive)\n"
            "    }\n"
            "\n"
            "    @After\n"
            "    fun tearDown() = mockWebServer.shutdown()\n"
            "}\n"
            "```"
        ),
        "quick_answer": "The test pyramid balances 70% fast local unit tests at the base, 20% integration tests in the middle, and 10% UI/E2E tests at the apex. Contract tests sit in the integration layer, verifying that client network serialization and DTO expectations strictly match backend API schemas without running heavy end-to-end device tests.",
        "best_answer": (
            "The testing pyramid structures test investments to maximize regression detection while minimizing execution duration:\n\n"
            "1. **The Modern Android Test Pyramid**:\n"
            "   - **Base (Unit Tests ~70%)**: High-volume, fast local JVM tests verifying business algorithms, ViewModels, UseCases, and state reducers in milliseconds.\n   - **Middle (Integration Tests ~20%)**: Medium-volume tests validating component boundaries: Room database transactions, WorkManager scheduling, and network DTO parsers.\n   - **Apex (UI / E2E ~10%)**: Low-volume, high-fidelity instrumentation and Compose tests verifying core customer conversion funnels (checkout, login).\n\n"
            "2. **Positioning Contract Tests**:\n"
            "   - Contract tests reside in the **Integration Layer**.\n   - Rather than relying on slow, brittle E2E tests against live backend staging clusters to verify that API responses match client expectations, contract tests validate client-server JSON schemas (using Pact, WireMock, or OpenAPI schema validators) locally on the JVM in seconds.\n\n"
            "3. **Value Proposition**:\n"
            "   - Contract testing catches API contract drift, unexpected nullability shifts, and renamed JSON fields early in CI before code merges, eliminating a major source of production outages."
        ),
        "deep_answer": (
            "From an organizational architecture perspective, contract testing enables autonomous cross-team deployments:\n\n"
            "1. **Consumer-Driven Contract Testing (Pact)**: The mobile client defines the contract by publishing a Pact file specifying the exact request parameters and response fields it consumes. When the backend team runs their CI pipeline, Pact replays the mobile contract against their active API routes. If a backend PR drops a field required by the mobile app, backend CI fails before deployment.\n\n"
            "2. **The Testing Trophy Alternative**: Some engineering leaders propose the **Testing Trophy** model (advocated by Kent C. Dodds), which places heavy emphasis on integration tests over isolated unit tests. In modern Android, integration tests combining ViewModels, Repositories, and in-memory Fakes provide higher confidence than unit tests mocking every collaborator.\n\n"
            "3. **Automated Flake Monitoring**: The apex of the pyramid (E2E) must have strict reliability budgets. If an E2E test fails more than 1% of the time due to non-deterministic timeouts, quarantine it immediately to maintain developer trust in CI gates."
        ),
        "follow_ups": [
            {
                "question": "What is Consumer-Driven Contract Testing?",
                "answer": "A paradigm where API consumers (mobile app) define and publish their contract expectations, and provider backends validate those contracts in their CI before deployment."
            },
            {
                "question": "Why are Contract Tests faster than End-to-End tests?",
                "answer": "They run on the local JVM using mock servers or schema validators, eliminating emulator boot times, network round-trips, and live backend staging dependencies."
            }
        ]
    },
    {
        "id": "TST-08",
        "arabic_explanation": (
            "كيف تقوم باختبار الـ ViewModels والـ UseCases والـ Repositories باحترافية وبشكل منعزل على الـ JVM؟\n\n"
            "1. اختبار الـ UseCases (Domain Layer):\n   - أسهل طبقة في الاختبار؛ لأنها كود Kotlin نقي وخالٍ من أي كود يخص أندرويد.\n   - نمرر لها Fake Repositories، ونختبر منطق العمل وحسابات البيانات وحالات الخطأ مباشرة.\n\n"
            "2. اختبار الـ ViewModels (Presentation Layer):\n   - **التحدي**: `viewModelScope` يعتمد على `Dispatchers.Main` الذي لا يعمل على JVM بدون محاكي!\n   - **الحل**: استبدال الـ Main Dispatcher بـ `StandardTestDispatcher` عبر `Dispatchers.setMain()`.\n   - نقوم بإرسال أحداث (Events) للـ ViewModel ونفحص تدفق الـ `StateFlow` الناتج باستخدام مكتبة **Turbine** للتأكد من تسلسل الحالات.\n\n"
            "3. اختبار الـ Repositories (Data Layer):\n   - نختبر التنسيق بين الـ Local Data Source (قاعدة البيانات) والـ Remote Data Source (الشبكة).\n   - نستخدم Fake DAO و MockWebServer للتأكد من أن البيانات تُجلب من الشبكة وتُحفظ في قاعدة البيانات المحلية بشكل سليم عند عمل Refresh."
        ),
        "practical_walkthrough": (
            "تنفيذ اختبارات وحدة متكاملة لـ UseCase و ViewModel باستخدام MainDispatcherRule ومكتبة Turbine:\n"
            "```kotlin\n"
            "// 1. اختبار UseCase نقي مع Fake Repository:\n"
            "class FormatOrderSummaryUseCaseTest {\n"
            "    @Test\n"
            "    fun `formatSummary calculates tax and returns domain model`() = runTest {\n"
            "        val fakeCartRepo = FakeCartRepository(items = listOf(CartItem(\"item1\", priceCents = 1000)))\n"
            "        val useCase = FormatOrderSummaryUseCase(fakeCartRepo)\n"
            "\n"
            "        val summary = useCase.execute()\n"
            "        assertEquals(\"$10.00\", summary.formattedSubtotal)\n"
            "        assertEquals(\"$1.40\", summary.formattedTax) // ضريبة 14%\n"
            "    }\n"
            "}\n"
            "\n"
            "// 2. اختبار ViewModel مع استبدال Main Dispatcher واستخدام Turbine لفحص StateFlow:\n"
            "class OrderViewModelTest {\n"
            "    @get:Rule\n"
            "    val mainDispatcherRule = MainDispatcherRule() // يستبدل Dispatchers.Main بـ StandardTestDispatcher\n"
            "\n"
            "    @Test\n"
            "    fun `loadOrder emits Loading then Success state`() = runTest {\n"
            "        val fakeRepo = FakeOrderRepository(order = Order(id = \"123\", total = 100))\n"
            "        val viewModel = OrderViewModel(fakeRepo)\n"
            "\n"
            "        // مراقبة الـ StateFlow باستخدام Turbine:\n"
            "        viewModel.uiState.test {\n"
            "            assertEquals(OrderUiState.Idle, awaitItem()) // الحالة الأولية\n"
            "\n"
            "            viewModel.loadOrder(\"123\")\n"
            "            mainDispatcherRule.testDispatcher.scheduler.runCurrent()\n"
            "\n"
            "            assertEquals(OrderUiState.Loading, awaitItem()) // حالة التحميل\n"
            "            \n"
            "            mainDispatcherRule.testDispatcher.scheduler.advanceUntilIdle()\n"
            "            val successState = awaitItem() as OrderUiState.Success\n"
            "            assertEquals(\"123\", successState.order.id)\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Test UseCases on the JVM as pure functions using Fake repositories. Test ViewModels by swapping Dispatchers.Main with a TestDispatcher via a JUnit rule and asserting StateFlow transitions with Turbine. Test Repositories by verifying coordination between in-memory Room DAOs and MockWebServer network responses.",
        "best_answer": (
            "Unit testing across presentation, domain, and data layers requires tailored testing strategies per layer:\n\n"
            "1. **Testing UseCases (Domain Layer)**:\n"
            "   - UseCases are pure Kotlin business orchestrators with zero framework dependencies. Test them synchronously or via `runTest`. Inject in-memory Fakes for repositories, verify business calculations, and assert that business boundary errors (e.g. empty cart validations) throw typed domain exceptions.\n\n"
            "2. **Testing ViewModels (Presentation Layer)**:\n"
            "   - **Main Dispatcher Replacement**: Replace `Dispatchers.Main` with `StandardTestDispatcher` using a reusable JUnit `@Rule` (`MainDispatcherRule`).\n   - **Reactive StateFlow Verification with Turbine**: Collect the ViewModel's `StateFlow` inside a `turbine.test { }` block. Trigger user intent events, advance virtual time, and assert state emissions sequentially (`Idle -> Loading -> Success`).\n\n"
            "3. **Testing Repositories (Data Layer)**:\n"
            "   - Test caching and synchronization logic. Supply an in-memory SQLite DAO (or Fake DAO) and a `MockWebServer` network client. Verify that fetching data updates local storage, handles 500 network exceptions gracefully by returning cached data, and maps network DTOs into domain models accurately."
        ),
        "deep_answer": (
            "From an architectural rigor perspective, isolating tests prevents coupling to UI rendering lifecycles:\n\n"
            "1. **Testing WhileSubscribed(5000) Flows**: In production ViewModels, `stateIn` typically uses `SharingStarted.WhileSubscribed(5000)`. In unit tests without Turbine, collecting `uiState.value` directly returns the initial state because no UI collector is active! Using Turbine's `.test { }` creates an active subscription, ensuring the upstream cold flow executes and emits values.\n\n"
            "2. **Testing Unhandled Coroutine Exceptions**: When testing error scenarios in ViewModels, ensure exceptions inside `viewModelScope.launch` are caught inside `CoroutineExceptionHandler` or wrapped in `Result<T>`. Unhandled exceptions inside coroutine builders bubble up and fail the `runTest` scope with unhandled test failures.\n\n"
            "3. **Repository Offline Sync Tests**: When verifying offline-first repositories, write scenarios simulating network loss: insert a pending item locally, assert local emission, simulate network restoration with MockWebServer, trigger background sync, and assert that the item status flips to `SYNCED`."
        ),
        "follow_ups": [
            {
                "question": "Why does uiState.value return initial state in tests when using SharingStarted.WhileSubscribed?",
                "answer": "Because WhileSubscribed only triggers upstream flow collection when an active subscriber is listening; without Turbine or a collector, upstream never starts."
            },
            {
                "question": "What is the primary benefit of testing UseCases independently from ViewModels?",
                "answer": "It tests core business algorithms in complete isolation, allowing test reuse across multiple presentation screens and platforms (KMP)."
            }
        ]
    }
]


def update_tst_data() -> None:
    data = []
    if DATA_FILE.exists():
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))

    existing_map = {item["id"]: item for item in data}
    for item in TST_01_08:
        existing_map[item["id"]] = item

    updated = [existing_map[k] for k in sorted(existing_map.keys())]
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(updated, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {DATA_FILE} with questions TST-01 to TST-08. Total questions: {len(updated)}")


if __name__ == "__main__":
    update_tst_data()
