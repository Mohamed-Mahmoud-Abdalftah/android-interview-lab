#!/usr/bin/env python3
"""Elevate TST-01 to TST-08: Software Testing, Quality & Reliability (Batch 1)."""
import os
import sys
from pathlib import Path

# Insert elevations directory to import elevation_engine
ROOT = Path("/Volumes/M&M/Android/InterView/untitled folder/android quation")
sys.path.insert(0, str(ROOT / "scripts" / "elevations"))
import elevation_engine as ee

TOPIC_CODE = "TST"
TOPIC_AR = ee.TOPIC_AR_NAMES[TOPIC_CODE]
REVIEWED_DATE_AR = "تمت المراجعة والتدقيق الهندسي في 17 أكتوبر 2026."

DATA = {}

# ==========================================
# TST-01: Compare unit, integration, instrumentation, UI, and end-to-end tests.
# ==========================================
DATA["TST-01"] = {
    "concept_en": """The Android testing spectrum spans five distinct tiers of speed, fidelity, and execution environments. Unit tests execute on the local host JVM in milliseconds, isolating individual classes like ViewModels, UseCases, or business mappers without booting the Android operating system. Integration tests verify the interoperation between two or more architectural layers, such as validating a repository communicating with a local SQLite database or an HTTP client against a mock server. Instrumentation tests run inside real or virtual Android devices via the Android Test Orchestrator, compiling against the real Android Runtime to verify framework integrations like SharedPreferences, hardware sensors, and native platform services. UI tests validate visual hierarchy, screen transitions, and accessibility semantics using Compose UI Test APIs or Espresso. End-to-end tests exercise complete user journeys from login to checkout against staging microservices, validating the entire compiled software stack under realistic device constraints.""",
    "walkthrough_en": """Contrasting lightweight JVM unit tests with on-device instrumented database integration tests:
```kotlin
// 1. JVM Unit Test in src/test/ (Executes in ~10ms without Android OS dependencies)
class DiscountCalculatorTest {
    @Test
    fun calculateFinalPrice_appliesDiscountAndRoundsCorrectly() {
        val calculator = DiscountCalculator()
        val result = calculator.calculate(basePrice = 100.0, discountPercentage = 25)
        assertEquals(75.0, result, 0.001)
    }
}

// 2. Instrumented Integration Test in src/androidTest/ (Runs on real ART against SQLite)
@RunWith(AndroidJUnit4::class)
class UserDaoIntegrationTest {
    private lateinit var database: AppDatabase
    private lateinit var userDao: UserDao

    @Before
    fun createDb() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        database = Room.inMemoryDatabaseBuilder(context, AppDatabase::class.java).build()
        userDao = database.userDao()
    }

    @After
    fun closeDb() {
        database.close()
    }

    @Test
    fun insertUser_andReadByUid_matchesDatabaseEntity() = runBlocking {
        val user = UserEntity(uid = 42, displayName = "Mahmoud")
        userDao.insert(user)
        val loaded = userDao.findByUid(42)
        assertEquals("Mahmoud", loaded?.displayName)
    }
}
```""",
    "short_en": """We structure testing across five tiers based on speed and fidelity. Unit tests run on the host JVM in milliseconds, verifying isolated business logic. Integration tests check interactions between two components like repositories and databases. Instrumentation tests run on real Android devices or emulators, validating Android framework APIs. UI tests verify user interactions and Compose semantics trees. Finally, end-to-end tests validate complete user journeys across the entire system, trading execution speed for maximum production fidelity.""",
    "structured_en": """A mature engineering strategy balances test execution speed against production fidelity across five distinct layers of the testing pyramid.
At the base, unit tests execute purely on the host development machine within the local Java Virtual Machine.
Because they bypass the Android OS and device boot cycles, thousands of unit tests execute in seconds, making them our primary tool for testing mathematical logic, ViewModels, UseCases, and domain algorithms.
Moving upward, integration tests verify that architectural boundaries communicate without protocol mismatches, such as checking that an offline-first repository correctly caches API payloads into a local SQLite database.
Instrumentation tests introduce the real Android execution environment by packaging code into an auxiliary test APK that runs on an emulator or physical device.
These are essential when verifying platform-bound behaviors, such as hardware biometrics, Room database migrations, and native system services that cannot be simulated accurately on the desktop JVM.
UI tests focus on the presentation layer, verifying Compose semantics trees, click dispatches, and navigation flows using ComposeTestRule or Espresso.
At the summit, end-to-end tests exercise complete user journeys—such as onboarding, browsing catalog products, and submitting a test payment—against staging servers, giving teams ultimate confidence before releasing builds to production.""",
    "deep_senior_en": """Under the hood, the fundamental distinction across these testing layers lies in the compilation pipeline, runtime bytecode execution, and thread scheduling models.
Local JVM unit tests reside in src/test and compile against mockable-android.jar provided by the Android Gradle Plugin.
Because the standard Android library on host machines contains method stubs that throw RuntimeException('Stub!'), any invocation of an unmocked Android API immediately fails unless developers configure returnDefaultValues in build scripts or inject mock abstractions.
In contrast, instrumentation tests in src/androidTest produce two distinct APKs: the application APK and the test runner APK.
The Android operating system installs both APKs and launches the instrumentation runner via an am instrument command through the ActivityManagerService.
The runner executes inside the target application's Linux process, sharing its ClassLoader and application Context, which enables native interaction with SQLite engines, hardware sensors, and native C++ graphics libraries.
UI tests built with ComposeTestRule bypass physical view hierarchies entirely by querying the SemanticsNode tree.
The Compose test runner integrates with the Choreographer and coroutine dispatchers, automatically idling until recomposition scopes and draw passes settle.
End-to-end testing introduces network latency, server state volatility, and background process management.
Senior engineers prevent test suite degradation by pushing 80% of assertion volume down to deterministic JVM unit tests, using instrumentation strictly for hardware and database boundaries, and reserving end-to-end device testing for critical monetization funnels in scheduled nocturnal CI pipelines.""",
    "meta_ar": {
        "id": "TST-01",
        "questionAr": "قارن بين اختبارات الوحدة (Unit) والتكامل (Integration) والأجهزة (Instrumentation) والواجهة (UI) واختبارات النهاية للنهاية (End-to-End).",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على التمييز بين مستويات الاختبار الخمسة، وفهم بيئات التشغيل (JVM مقابل ART)، واختيار المستوى المناسب لكل ميزة برمجية لتحقيق التوازن بين السرعة والموثوقية.",
        "why_it_matters_ar": "الخلط بين بيئات الاختبار يهدر ساعات العمل؛ كتابة اختبارات منطق أعمال على المحاكي تجعل الـ CI بطيئاً جداً، بينما إهمال اختبارات الأجهزة الحقيقية يمرر أخطاء قواعد البيانات وتوافق العتاد للمستخدمين.",
        "worked_example_ar": "مقارنة عملية بين اختبار وحدة سريع على JVM واختبار تكاملي على جهاز حقيقي:\n```kotlin\n// 1. Unit Test سريع على JVM ينفذ في بضعة أجزاء من الثانية\nclass CalculatorTest {\n    @Test fun testMath() = assertEquals(4, 2 + 2)\n}\n// 2. Instrumented Test يتطلب محاكي لفحص SQLite الحقيقي داخل نظام أندرويد\n@RunWith(AndroidJUnit4::class)\nclass RoomTest {\n    @Test fun testDb() = runBlocking { dao.insert(user); assertNotNull(dao.find(1)) }\n}\n```",
        "trade_offs_ar": "اختبارات الـ JVM فائقة السرعة لكنها لا تختبر عتاد الجهاز، بينما اختبارات الـ Instrumentation والـ E2E تعطي أقصى واقعية وموثوقية لكنها بطيئة جداً ومكلفة وعرضة للتذبذب.",
        "failure_modes_ar": "الاعتماد الكامل على اختبارات الـ UI والـ E2E وفحص كل التفاصيل عبر المحاكي، مما يرفع زمن بناء الـ CI إلى ساعات ويؤدي إلى اختبارات متقلبة (Flaky Tests).",
        "production_perspective_ar": "في المشروعات الكبيرة، نطبق هرم الاختبارات الصارم: 70% إلى 80% اختبارات Unit سريعة على الـ JVM، و15% اختبارات تكامل لـ Room و MockWebServer، و5% فقط لاختبارات الـ E2E على أجهزة حقيقية قبل الإصدار.",
        "how_to_answer_ar": "رتب الإجابة من القاعدة للقمة: ابدأ بـ Unit tests على الـ JVM المحلي وسرعتها، ثم Integration tests لفحص اتصال طبقتين، ثم Instrumentation tests على أجهزة أندرويد الحقيقية، ثم UI tests لفحص الشاشات والـ Semantics، وأخيراً E2E tests للرحلات الكاملة، مع توضيح الفارق بين بيئة JVM وبيئة أندرويد الحقيقية.",
        "talking_points_ar": "بيئة JVM مقابل ART والمحاكي، وسرعة التنفيذ والتكلفة، ودور mockable-android.jar، واختبارات الـ Semantics في Compose، وتوزيع نسب الاختبارات في هرم الاختبارات.",
        "follow_ups_ar": "- **المحاور:** \"لماذا يفشل اختبار الـ Unit على الـ JVM فوراً عند استدعاء `Log.d` أو `TextUtils`؟\"\n  **المرشح:** \"لأن مكتبة أندرويد على جهاز الكمبيوتر المكتبي بتحتوي على Stubs فارغة بترمي استثناء `Stub!`، وعشان تشتغل لازم نعمل Mock للدوال دي أو نستخدم Robolectric أو نفعل `returnDefaultValues`.\"\n\n- **المحاور:** \"متى تضطر حتماً لكتابة Instrumented Test بدلاً من Unit Test؟\"\n  **المرشح:** \"لما أكون بختبر ميزات مرتبطة بنظام أندرويد الحقيقي زي ترقية قواعد بيانات Room المعقدة، أو فحص التشفير في الـ Android Keystore، أو فحص الـ WorkManager والـ Services.\"",
        "self_check_ar": "هل غطيت المستويات الخمسة بدقة؟ هل وضحت الفرق بين بيئة JVM وبيئة الجهاز الحقيقي؟ وهل بينت المفاضلة الهندسية بين السرعة والموثوقية؟",
        "references_ar": f"- [Android Testing Fundamentals](https://developer.android.com/training/testing/fundamentals) — التوثيق الرسمي لمبادئ ومستويات الاختبار في أندرويد.\n- [Google Testing Blog: Just Say No to More End-to-End Tests](https://testing.googleblog.com/) — مقال جوجل الكلاسيكي حول ترشيد اختبارات E2E والاعتماد على Unit tests.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "بنقسم الاختبارات لخمس طبقات حسب السرعة والموثوقية: أولاً اختبارات الوحدة (Unit) بتشتغل على الـ JVM المحلي في بضعة أجزاء من الثانية لاختبار المنطق الداخلي للكلاسات بمعزل عن النظام. ثانياً اختبارات التكامل (Integration) بتتحقق من توافق طبقتين زي الـ Repository وقاعدة البيانات. ثالثاً اختبارات الـ Instrumentation بتشتغل داخل جهاز أو محاكي أندرويد حقيقي لفحص مكونات النظام زي SQLite والخدمات. رابعاً اختبارات الواجهة (UI) بتفحص تفاعل المستخدم وشجرة الـ Semantics. وأخيراً اختبارات الـ End-to-End بتتحقق من رحلة المستخدم الكاملة من أول الشاشة لحد السيرفر لضمان سلامة التدفق التجاري النهائي.",
        "best_answer_ar": "المقارنة بين مستويات الاختبار الخمسة هي المعيار الأساسي لتقييم قدرة المهندس على تصميم خطة جودة متوازنة وسريعة في بيئة العمل.\n\nفي قاعدة الهرم، اختبارات الـ Unit بتشتغل بالكامل على الـ JVM بتاع الكمبيوتر المكتبي في مجلد `src/test`. ميزتها الكبرى هي السرعة الخارقة؛ بنقدر نشغل آلاف الاختبارات في ثوانٍ لاختبار الـ ViewModels والـ UseCases وحسابات العمليات الرياضية بدون الحاجة لفتح محاكي أو استهلاك ذاكرة.\n\nالمستوى الثاني هو اختبارات التكامل (Integration)؛ هدفها التأكد إن طبقتين بيكلموا بعض صح، مثلاً هل الـ Repository بياخد البيانات من الشبكة ويخزنها في Room Database بدون أخطاء في الـ Mapping.\n\nالمستوى الثالث هو اختبارات الـ Instrumentation في مجلد `src/androidTest`؛ دي بتتطلب تشغيل محاكي أو جهاز أندرويد حقيقي، لأنها بتختبر ميزات مربوطة بنظام تشغيل أندرويد الفعلي زي ترقيات الداتابيز أو التشفير بـ Android Keystore.\n\nالمستوى الرابع هو اختبارات الـ UI؛ بنفحص بيها دقة ظهور النصوص وتفاعل الأزرار وشجرة الـ Semantics في Jetpack Compose.\n\nوفي قمة الهرم بتيجي اختبارات الـ End-to-End؛ دي بتختبر تدفق العميل الكامل من تسجيل الدخول حتى إتمام الدفع ضد سيرفرات Staging حقيقية. رغم واقعيتها، بنقلل منها لأنها بطيئة جداً وعرضة للفشل بسبب مشاكل الشبكة، ونعتمد بنسبة 80% على الـ Unit Tests.",
        "deep_answer_ar": "تحت الكابوت، الفارق الجوهري بين مستويات الاختبار دي بيكمن في خط أنابيب البناء، ونوع الـ Bytecode، وبيئة التنفيذ والذاكرة.\n\nاختبارات الـ Unit على الـ JVM بتترجم ضد ملف `mockable-android.jar` اللي بيوفره الـ AGP. الملف ده بيحتوي على هياكل فارغة بدون كود حقيقي بترمي `RuntimeException('Stub!')` عند أي استدعاء لكود أندرويد زي `Log` أو `Bundle`، عشان كده بنعزل كودنا تماماً بحقن التبعيات أو بنستخدم فريمورك Robolectric اللي بيستبدل كود أندرويد بـ Shadow Objects على الديسك توب.\n\nبينما في اختبارات الـ Instrumentation، نظام البناء بيولد ملفين APK: ملف تطبيقك وملف الـ Test Runner. نظام التشغيل بيثبت الـ APK التاني ويشغل الـ Instrumentation Runner عبر أمر `am instrument` في الـ ActivityManagerService.\nالـ Runner بيشتغل داخل نفس الـ Linux Process ومساحة الذاكرة الخاصة بالتطبيق، وبيمتلك `Context` حقيقي ومحرك SQLite أصلي ومحرك الرسومات في ART.\n\nوفي اختبارات واجهات Compose الحديثة بـ `createComposeRule()`، الرنتايم مبيعتمدش على أبعاد البكسل على الشاشة، بل بيبحث في شجرة الـ SemanticsNode الموازية في الذاكرة، وبيتحكم في الـ Choreographer وساعة الكوروتينات لتعليق الفحص لحد ما تستقر كل دورات الـ Recomposition.\nعشان كده، المهندس السينيور بيمنع إرهاق خوادم الـ CI بكتابة 80% من الاختبارات كـ JVM Unit Tests نظيفة، وحصر الـ Instrumentation في اختبارات الداتابيز ومكونات النظام التي يستحيل محاكاتها بدون أندرويد حقيقي."
    }
}

# ==========================================
# TST-02: Compare fake, mock, stub, spy, and test double.
# ==========================================
DATA["TST-02"] = {
    "concept_en": """In automated software testing, Test Double is the generic umbrella term coined by Gerard Meszaros for any surrogate object that replaces a production dependency during verification. Within this taxonomy, each double fulfills a specialized architectural role. A Dummy is an inert object passed solely to satisfy method signatures without ever being accessed. A Stub returns hardcoded, canned responses to incoming queries, serving as a passive data fixture without recording invocation history. A Spy wraps a real object or mimics an interface while recording interaction metadata, such as method call counts and received arguments, allowing state and behavioral inspection. A Mock is pre-configured with strict expectations and call verifications, driving interaction-based assertions where success depends on whether exact methods were invoked in sequence. A Fake is a fully functional, stateful implementation using algorithmic shortcuts—such as an in-memory HashMap repository—providing high fidelity without production infrastructure overhead.""",
    "walkthrough_en": """Implementing and contrasting Fakes, Stubs, Mocks, and Spies in Kotlin:
```kotlin
// 1. Production Contract
interface UserRepository {
    suspend fun getUser(id: String): User?
    suspend fun saveUser(user: User)
}

// 2. FAKE: Working in-memory implementation with internal state
class FakeUserRepository : UserRepository {
    private val memoryStore = mutableMapOf<String, User>()
    override suspend fun getUser(id: String): User? = memoryStore[id]
    override suspend fun saveUser(user: User) { memoryStore[user.id] = user }
}

// 3. STUB: Canned static responses without state tracking
class StubUserRepository(private val cannedUser: User) : UserRepository {
    override suspend fun getUser(id: String): User = cannedUser
    override suspend fun saveUser(user: User) { /* no-op */ }
}

// 4. SPY: Tracks invocations and inspects argument history
class SpyUserRepository(private val realRepo: UserRepository) : UserRepository by realRepo {
    var saveCallCount = 0
        private set
    var lastSavedUser: User? = null
        private set

    override suspend fun saveUser(user: User) {
        saveCallCount++
        lastSavedUser = user
        realRepo.saveUser(user)
    }
}

// 5. MOCK: Declarative expectation and verification using MockK
class UserUseCaseTest {
    @Test
    fun execute_verifiesStrictInteraction() = runTest {
        val mockRepo = mockk<UserRepository>()
        coEvery { mockRepo.saveUser(any()) } returns Unit

        val useCase = SaveUserUseCase(mockRepo)
        useCase(User("42", "Ali"))

        coVerify(exactly = 1) { mockRepo.saveUser(match { it.id == "42" }) }
    }
}
```""",
    "short_en": """Test double is the universal umbrella term for any test substitute. A dummy is an unused placeholder to satisfy parameters. A stub provides canned data without logic. A spy records method calls and arguments for later inspection. A mock defines strict expectations on interactions, failing if expected calls do not occur. Finally, a fake is a working implementation with simplified state, such as an in-memory database, providing the highest fidelity and maintainability without external dependencies.""",
    "structured_en": """Mastering Gerard Meszaros' test double taxonomy allows senior developers to author resilient, expressive test suites while avoiding fragile mock traps.
Test double is the generic umbrella category that encompasses all test stand-ins.
A dummy is the simplest double; it exists purely to fill mandatory method parameters, such as passing a blank context or empty logger that is never exercised during the test.
A stub acts as an indirect input provider, returning predetermined, hardcoded results to specific method queries without maintaining internal state or validating how it was called.
A spy acts as an indirect output observer; it records telemetry about interactions—such as the number of times a method was called and the exact arguments passed—allowing assertions to inspect historical invocations after the execution finishes.
A mock is configured with pre-programmed behavioral expectations.
Rather than verifying resulting state, mock tests assert that specific methods were invoked with specific parameters, making the test focus heavily on execution mechanics.
A fake provides a fully operational, lightweight implementation of the production interface, such as maintaining an in-memory HashMap to simulate a database.
Senior engineers strongly favor fakes over mocks because fakes simulate real-world state transitions, do not break when internal class details are refactored, and execute without bytecode proxy overhead.""",
    "deep_senior_en": """Under the hood, the choice between fakes and mocks dramatically impacts test runtime performance, refactoring safety, and internal compilation mechanics.
Mocking libraries like MockK and Mockito rely on dynamic bytecode generation.
On the JVM, they utilize ByteBuddy or Java dynamic proxies to subclass target interfaces and intercept method calls at runtime.
On Android ART devices, mocking is even more expensive, requiring dexmaker to dynamically patch Dalvik bytecode into the application's executable cache directory.
Every mock invocation traverses deep reflection interceptor call stacks to evaluate argument matchers and record invocation history.
Furthermore, mock-heavy testing often results in severe test brittleness; because assertions verify exact method names and call counts, harmless internal refactorings that preserve behavior can cause hundreds of mock tests to fail.
In contrast, a fake is compiled as standard Kotlin bytecode utilizing ordinary polymorphic dispatch.
An in-memory fake repository executes millions of operations per second using standard CPU cache lines and HashMap algorithms without reflection, proxy allocations, or dex patching.
Fakes enable state-based verification: the test exercises business actions and asserts the resulting domain state, leaving the internal collaboration details completely unconstrained.
Senior engineers maintain shared fake implementations alongside production code in dedicated testing modules, ensuring that contract updates immediately propagate to all unit tests across the engineering organization.""",
    "meta_ar": {
        "id": "TST-02",
        "questionAr": "قارن بين الـ Fake والـ Mock والـ Stub والـ Spy والـ Test Double.",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "الفهم المعماري الدقيق لتصنيف Gerard Meszaros لبدائل الاختبار (Test Doubles)، وإدراك الفروق السلوكية بينها، ومعرفة متى يفضل استخدام الـ Fake على الـ Mock لتجنب هشاشة الاختبارات.",
        "why_it_matters_ar": "الاستخدام المفرط للـ Mocks يجعل الاختبارات هشة (Brittle Tests) تنهار مع أي تعديل بسيط في الكود، بينما استخدام الـ Fakes يبني اختبارات قوية وسريعة تركز على النتائج بدلاً من تفاصيل التنفيذ.",
        "worked_example_ar": "تطبيق الفروق بين الأنواع في كود Kotlin:\n```kotlin\n// Stub: يرجع قيمة جاهزة ثابتة\nclass StubRepo : Repo { override fun get() = \"Data\" }\n// Spy: يسجل عدد مرات الاستدعاء للمراقبة\nclass SpyRepo : Repo { var calls = 0; override fun get() = \"Data\".also { calls++ } }\n// Fake: كلاس حقيقي شغال بذاكرة داخلية (HashMap)\nclass FakeRepo : Repo { val store = mutableMapOf<Int, String>() }\n```",
        "trade_offs_ar": "الـ Mocks سريعة في الإعداد باستخدام MockK لكنها تربط الاختبار بتفاصيل التنفيذ الداخلي، بينما الـ Fakes تتطلب كتابة كود إضافي وصيانة مستمرة لكنها تقدم أعلى موثوقية ولا تنكسر مع الـ Refactoring.",
        "failure_modes_ar": "استخدام الـ Mock للتحقق من كل تفصيلة صغيرة في الاستدعاءات الداخلية، مما يجعل الاختبار يفشل حتى لو كانت النتيجة النهائية سليمة تماماً، وهو ما يسمى over-mocking.",
        "production_perspective_ar": "في المشروعات الكبيرة، نعتمد استراتيجية 'Fake over Mock' في طبقة الـ Data؛ بنبني كلاسات Fake Repositories مشتركة في موديول الاختبار الداخلي وتستخدمها كل الفرق لضمان واقعية النتائج وسرعة الـ CI.",
        "how_to_answer_ar": "عرف أولاً أن Test Double هو المصطلح الشامل (Umbrella term)، ثم اشرح الخمسة بالتسلسل: Dummy لملء الباراميترات، Stub لتقديم بيانات ثابتة، Spy لمراقبة وتسجيل الاستدعاءات، Mock للتحقق من صحة حدوث الاستدعاءات، و Fake كنسخة شغالة كاملة بذاكرة بسيطة، واختم بتفضيل الـ Fakes في بيئة الإنتاج.",
        "talking_points_ar": "تصنيف Gerard Meszaros، والفرق بين التحقق من الحالة (State verification) والتحقق من التفاعل (Behavior verification)، وعيوب الـ Over-mocking وهشاشة الاختبارات، وميزات الـ Fake السلوكية والسرعة.",
        "follow_ups_ar": "- **المحاور:** \"لماذا يفضل مهندسو جوجل استخدام Fake Repository بدلاً من mockk<Repository>()؟\"\n  **المرشح:** \"لأن الـ Fake بيعتمد على التحقق من الحالة النهائية (State-based)، فلو غيرنا اسم دالة داخلية أو عدلنا طريقة الاستعلام الكود مش هيكسر الاختبار، بعكس الـ Mock اللي بيكسر فوراً مع أي تغيير بسيط في التنفيذ الداخلي.\"\n\n- **المحاور:** \"ما هو الفرق الجوهري بين Stub و Mock؟\"\n  **المرشح:** \"الـ Stub وظيفته توفير بيانات جاهزة للمدخلات (Indirect Inputs) ومبيهتمش مين ناداه، بينما الـ Mock بيتحقق من المخرجات وطريقة التفاعل وهل الدالة اتنادت بالباراميترات المطلوبة ولا لأ (Indirect Outputs).\"",
        "self_check_ar": "هل عرفت Test Double كاسم شامل؟ هل شرحت الفروق الدقيقة بين الفئات الخمسة؟ وهل بينت أسباب تفضيل الـ Fake في الإنتاج؟",
        "references_ar": f"- [Martin Fowler: Mocks Aren't Stubs](https://martinfowler.com/articles/mocksArentStubs.html) — المقال المعماري التأسيسي لمارتن فاولر حول تصنيف بدائل الاختبار.\n- [Google Testing on the Toilet: Know Your Test Doubles](https://testing.googleblog.com/) — دليل مهندسي جوجل العملي لبدائل الاختبار.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "الـ `Test Double` هو الاسم العام والشامل لأي كائن بديل بنستخدمه في الاختبارات بدل الكائن الحقيقي. بيتفرع منه خمسة أنواع رئيسية: الـ `Dummy` مجرد عنصر شكلي بنمرره عشان نملأ خانة باراميتر إجباري ومش بنستخدمه. الـ `Stub` بيرجع بيانات ثابتة ومحددة سلفاً بدون أي منطق. الـ `Spy` كائن بيسجل عدد مرات استدعاء الدوال والباراميترات اللي اتبعتت عشان نفحصها بعد التنفيذ. الـ `Mock` بيتحقق من صحة التفاعل وسلوك التنفيذ وبيتأكد إن دوال معينة اتنادت بترتيب محدد. وأخيراً الـ `Fake` هو تطبيق برمجي شغال وله حالة حقيقية لكن بذاكرة بسيطة زي `HashMap`، وده أفضل وأمتن نوع في كود الإنتاج.",
        "best_answer_ar": "التمييز بين أنواع بدائل الاختبار بيعكس مدى نضج المطور في بناء اختبارات قوية وسهلة الصيانة بدون الوقوع في فخ الاختبارات الهشة.\n\nالمصطلح العام هو `Test Double`، وتحته خمسة أدوار محددة:\nأولاً: الـ `Dummy`؛ ده مجرد كائن بنحطه في مدخلات الدالة عشان نرضي الكومبايلر، زي تمرير كائن `Logger` أو كائن فارغ لا يتم استدعاء أي ميثود عليه نهائياً أثناء الفحص.\n\nثانياً: الـ `Stub`؛ وظيفته توفير بيانات جاهزة وسريعة، كأنك تقوله لما يتنادى `getUser()` رجع الكائن ده فوراً، ومبيهتمش مين ناداه ولا كام مرة.\n\nثالثاً: الـ `Spy`؛ ده بيراقب التفاعل الفعلي؛ بيسمح بتنفيذ الكود ويسجل إحصائيات زي: 'دالة الإرسال اتنادت 3 مرات ببيانات معينة' عشان نعمل Assert على السجل ده في الآخر.\n\nرابعاً: الـ `Mock`؛ ده كائن بيتبرمج مسبقاً بتوقعات صارمة (Expectations)؛ بنحدد له في أول التيست إنه يتوقع استدعاء دالة الحفظ مرة واحدة فقط ببيانات مطابقة، ولو الكود مناداش الدالة دي التيست بيفشل فوراً.\n\nخامساً: الـ `Fake`؛ وده البطل الحقيقي في بنية التطبيقات الكبيرة؛ هو كلاس حقيقي بيعمل Implement لنفس الـ Interface وبيحتفظ بالحالة جواه باستخدام `mutableMapOf` بدلاً من الداتابيز الحقيقية. الـ Fake بيخلينا نختبر منطق التطبيق الحقيقي بنسبة 100% بدون أي تعقيد أو مكتبات توليد أكواد.",
        "deep_answer_ar": "تحت الكابوت، الاختيار بين الـ Mocks والـ Fakes بيأثر بشكل جذري على أداء بيئة الاختبار وثبات الكود ضد الـ Refactoring.\n\nمكتبات الـ Mocking زي MockK و Mockito بتعتمد في الـ JVM على توليد كود بايت كود ديناميكي عبر مكتبات زي ByteBuddy، وبتحجز Dynamic Proxies في الـ Heap مع كل استدعاء. وعلى أجهزة أندرويد الحقيقية، الموضوع بيكون أثقل لأن المكتبة بتضطر تستخدم `dexmaker` لتعديل ملفات الـ DEX في الذاكرة لتجاوز قيود ART.\nكل استدعاء لموك بيمر بسلسلة من Reflection Interceptors عشان يطابق الـ Matchers ويسجل الـ Invocations في مصفوفة داخلية، وده بيستهلك وقت معالجة ورام ملحوظة.\nوالأخطر من كده، الاعتماد المفرط على الـ Mocks بيخلق مشكلة 'هشاشة الاختبارات' (Test Fragility)؛ لأنك بتعمل فحص للتفاصيل الداخلية (Implementation Details) بدل التحقق من النتيجة النهائية (State-based Verification).\nلو غيرت اسم ميثود داخلية أو دمجت خطوتين مع الحفاظ على سلامة النتيجة، كل اختبارات الموك هتنهار وهتطلب ساعات لتحديث التوقعات.\n\nبينما الـ Fake بيتترجم كـ Bytecode كوتلن طبيعي فائق السرعة، بينفذ العمليات في الذاكرة مباشرة عبر دوال المجموعات العادية O(1) وبدون أي Reflection أو Proxies.\nعشان كده، كبرى الشركات التقنية زي جوجل بتلزم المطورين بكتابة Fakes رسمية لكل الـ Repositories في موديول التيست، لضمان استقرار الاختبارات وسرعة الـ CI لأقصى حد."
    }
}

# ==========================================
# TST-03: What are JUnit, MockK/Mockito, Espresso, and Compose UI Testing?
# ==========================================
DATA["TST-03"] = {
    "concept_en": """The modern Android testing stack relies on four complementary libraries addressing distinct execution tiers. JUnit (JUnit 4 and JUnit 5 Jupiter) serves as the foundational test execution framework, managing test lifecycles (@Before, @After, @Test), assertion evaluation, test runners, and test rules. MockK and Mockito provide mocking, stubbing, and verification capabilities, with MockK offering native, first-class Kotlin support for coroutines, suspension functions, inline value classes, and object mocks. Espresso is the legacy UI testing framework for View-based hierarchies, synchronizing with the Android main message looper to execute view interactions and assertions. Compose UI Testing is the modern declarative UI testing framework that interfaces directly with the Compose Semantics tree via createComposeRule(), automatically synchronizing with the Compose Recomposer clock without requiring manual idling resources.""",
    "walkthrough_en": """Contrasting MockK unit testing with Compose UI semantic testing:
```kotlin
// 1. JUnit 4 + MockK Unit Test (Testing a ViewModel)
class LoginViewModelTest {
    private val authRepository = mockk<AuthRepository>()
    private lateinit var viewModel: LoginViewModel

    @Before
    fun setup() {
        viewModel = LoginViewModel(authRepository)
    }

    @Test
    fun login_success_updatesUiStateToAuthenticated() = runTest {
        coEvery { authRepository.login("user", "pass") } returns AuthResult.Success
        viewModel.onLoginClick("user", "pass")
        assertEquals(LoginUiState.Authenticated, viewModel.uiState.value)
    }
}

// 2. Compose UI Test using createComposeRule (Testing semantic tree)
class LoginScreenTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun loginButton_displaysCorrectText_andRespondsToClick() {
        var clicked = false
        composeTestRule.setContent {
            LoginButton(isLoading = false, onClick = { clicked = true })
        }

        // Semantic query and assertion
        composeTestRule.onNodeWithText("Sign In")
            .assertIsDisplayed()
            .performClick()

        assertTrue(clicked)
    }
}
```""",
    "short_en": """The Android testing stack uses four core tools. JUnit manages test lifecycles, runners, and assertions. MockK and Mockito provide mocking and verification, with MockK offering native support for Kotlin coroutines, suspend functions, and inline classes. Espresso tests View-based UIs by matching View hierarchies and waiting for Looper idleness. Compose UI Testing tests declarative Compose trees by querying the Semantics tree using createComposeRule, automatically synchronizing with recomposition clocks.""",
    "structured_en": """Building a comprehensive automated testing pipeline requires understanding the complementary responsibilities across JUnit, MockK, Espresso, and Compose UI Testing.
JUnit is the foundation of the entire testing ecosystem.
Whether running on the JVM or on-device, JUnit orchestrates test execution, manages setup and teardown fixtures via annotations like @Before and @After, evaluates assertion logic, and organizes test suites.
MockK and Mockito handle dependency isolation through test doubles.
While Mockito historically pioneered Java mocking, MockK is tailored exclusively for modern Kotlin.
It natively mocks suspend functions without awkward runBlocking wrappers, understands Kotlin object singletons, inspects inline value classes, and offers relaxed mocks to reduce boilerplate.
For the user interface layer, the framework choice matches the UI rendering architecture.
Espresso is built for traditional Android Views.
It operates through a three-step cycle: finding views via ViewMatchers, dispatching touch events via ViewActions, and verifying state via ViewAssertions, synchronizing execution by listening to the Main Looper's MessageQueue.
Compose UI Testing replaces Espresso for declarative user interfaces.
Utilizing createComposeRule(), it bypasses physical pixels to query the parallel Compose Semantics tree.
It automatically synchronizes with the Compose Recomposer, virtualizing time and waiting for state settling without manual synchronization hooks.""",
    "deep_senior_en": """Under the hood, these four tools expose radically different thread synchronization, class loading, and layout inspection architectures.
JUnit relies on a dedicated runner pipeline.
In JUnit 4, TestRule objects intercept test method execution via the Statement design pattern, allowing developers to wrap execution with Coroutine test dispatchers or database transactions.
JUnit 5 modernized this by replacing rules with composable Extension APIs, though Android instrumented testing still predominantly uses JUnit 4 due to AndroidX test runner integration constraints.
MockK differentiates itself from Mockito through its bytecode engine.
When mocking a Kotlin singleton object or coroutine suspend function, MockK uses inline bytecode transformation to intercept continuation dispatchers, passing fake Continuation instances directly into suspend bytecode state machines without deadlocking the test thread.
On the UI frontier, Espresso and Compose diverge fundamentally in synchronization mechanics.
Espresso queries the Android platform Choreographer and main Looper.
If an animation or background worker keeps posting messages to the Handler queue, Espresso indefinitely hangs or times out with IdlingResourceTimeoutException.
Compose UI Testing abandons looper polling.
Instead, createComposeRule() interfaces with the root Snapshot state system and the internal Compose TestCoroutineScheduler.
When a test performs an action via performClick(), the test rule forces the Recomposer to synchronously drain all pending state invalidations, execute layout measurement passes, and settle animations before advancing to assertion assertions.
This deterministic synchronization guarantees that Compose UI tests execute with zero flakiness on CI servers.""",
    "meta_ar": {
        "id": "TST-03",
        "questionAr": "ما هي الأدوار المحددة لكل من JUnit و MockK/Mockito و Espresso و Compose UI Testing؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على تحديد وظيفة كل مكتبة في منظومة الاختبار الحديثة، وفهم الفارق بين أدوات الـ Views القديمة والـ Compose، ومعرفة آليات المزامنة التلقائية ومحاكاة الكوروتينات.",
        "why_it_matters_ar": "استخدام أدوات غير متوافقة (زي محاولة اختبار Compose بـ Espresso العادي بدون Semantics) يسبب بطء شديد وتذبذب في الاختبارات ويفسد خطوط الـ CI.",
        "worked_example_ar": "الجمع بين الأدوات في كود اختبار احترافي:\n```kotlin\n// JUnit ينظم التشغيل والـ MockK يحاكي الكوروتين\n@Test fun testViewModel() = runTest {\n    coEvery { repo.load() } returns \"Data\"\n    assertEquals(\"Data\", viewModel.getData())\n}\n// Compose Test Rule لفحص الواجهة عبر الـ Semantics\n@Test fun testCompose() {\n    rule.setContent { Button(onClick = {}) { Text(\"Save\") } }\n    rule.onNodeWithText(\"Save\").assertIsDisplayed()\n}\n```",
        "trade_offs_ar": "مكتبة MockK توفر دعماً ممتازاً لكوتلن لكنها أبطأ قليلاً في البداية مقارنة بالـ Fakes، واختبارات Compose UI أسرع وأثبت من Espresso لكنها تختبر شجرة الـ Semantics وليس بكسلات الشاشة الفعلية.",
        "failure_modes_ar": "استخدام Thread.sleep في اختبارات Espresso لانتظار تحميل البيانات بدلاً من مزامنة الـ IdlingResource أو استخدام اختبارات Compose المباشرة.",
        "production_perspective_ar": "في المشروعات الكبيرة، نعتمد JUnit 4/5 كأساس، ونستخدم MockK للـ Unit Tests، ونمنع Espresso تماماً في الشاشات الجديدة لصالح `ComposeTestRule` لضمان استقرار الـ CI بنسبة 100%.",
        "how_to_answer_ar": "قسم الأدوات لأربع ركائز واضحة: أولاً JUnit كهيكل تشغيل وإدارة دورة حياة الاختبارات، ثانياً MockK/Mockito لمحاكاة التبعيات مع توضيح تميز MockK في الكوروتينات، ثالثاً Espresso للواجهات الكلاسيكية (Views)، ورابعاً Compose UI Testing للواجهات التصريحية عبر فحص شجرة الـ Semantics والمزامنة الآلية.",
        "talking_points_ar": "هيكل تشغيل JUnit ودورة حياته، ودعم MockK الأصلي لدوال الـ Suspend والـ Singletons، وآلية عمل Espresso مع الـ Looper، وشجرة الـ Semantics والمزامنة في Compose.",
        "follow_ups_ar": "- **المحاور:** \"لماذا يفضل مجتمع أندرويد استخدام MockK بدلاً من Mockito في مشاريع Kotlin الحديثة؟\"\n  **المرشح:** \"لأن MockK مبني من الصفر لـ Kotlin؛ بيدعم محاكاة دوال الـ suspend بدون مشاكل، وبيقدر يعمل Mock لكائنات الـ object والـ Top-level functions والـ Inline classes بسهولة بدون إعدادات معقدة.\"\n\n- **المحاور:** \"كيف تختلف المزامنة التلقائية في Compose UI Test عن Espresso؟\"\n  **المرشح:** \"Espresso بيراقب طابور رسائل الـ Main Looper وممكن يعلق لو فيه أنيميشن شغال، بينما Compose Test Rule مربوط بمحرك الـ Recomposer وساعة الـ Snapshots وبيمشي الوقت افتراضياً لحد ما تستقر كل حالات الرندرة بدون تأخير.\"",
        "self_check_ar": "هل شرحت دور كل مكتبة من الأربعة بوضوح؟ هل بينت ميزة MockK مع كوتلن؟ وهل قارنت بدقة بين Espresso واختبارات Compose؟",
        "references_ar": f"- [Android Testing Tools](https://developer.android.com/training/testing/tools) — التوثيق الرسمي لأدوات الاختبار في أندرويد.\n- [Compose UI Testing Guide](https://developer.android.com/develop/ui/compose/testing) — دليل جوجل الرسمي لاختبار واجهات Jetpack Compose.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "منظومة الاختبار في أندرويد بتعتمد على أربع أدوات متكاملة: أولاً `JUnit` هو الإطار الأساسي اللي بينظم تشغيل الاختبارات ويدير دورة حياتها (زي `@Test` و `@Before`) ويفحص شروط النجاح. ثانياً `MockK` و `Mockito` أدوات لعزل ومحاكاة التبعيات، مع تفوق MockK لدعمه الأصلي لكوروتينات كوتلن ودوال الـ suspend. ثالثاً `Espresso` أداة اختبار واجهات أندرويد التقليدية المبنية بنظام الـ Views عبر مراقبة الـ Looper. رابعاً `Compose UI Testing` هي الأداة الحديثة لاختبار واجهات Jetpack Compose بالتعامل مباشرة مع شجرة المعاني (Semantics Tree) وبمزامنة تلقائية تامة تمنع تذبذب الاختبارات.",
        "best_answer_ar": "كل مكتبة من الأدوات الأربعة بتلعب دوراً تخصصياً حاسماً في بناء خط اختبارات متين ومتكامل:\n\nأولاً: `JUnit`؛ ده العمود الفقري لأي اختبار في أندرويد، وظيفته إدارة دورة حياة الاختبار؛ بيحدد دالة البداية `@Before` ودالة التنظيف `@After`، وبيوفر دوال الـ `assertEquals` والـ Assertions، وبيقوم بتنظيم الـ Test Runners سواء على الـ JVM أو على جهاز حقيقي.\n\nثانياً: `MockK` و `Mockito`؛ دول أدوات محاكاة التبعيات. رغم شهرة Mockito التاريخية، MockK هو الخيار القياسي الحديث لمشاريع كوتلن، لأنه بيدعم دوال الـ suspend الأصلية بـ `coEvery` و `coVerify`، وبيقدر يحاكي كائنات الـ Singleton والـ Value Classes بدون أي تعقيد.\n\nثالثاً: `Espresso`؛ دي مكتبة جوجل الكلاسيكية لاختبار الـ Views القديمة (XML). بتعتمد على تلات خطوات: العثور على العنصر بـ `onView`، وتنفيذ حركة بـ `perform`، والتحقق بـ `check`، وميزتها إنها بتراقب خيط الـ Main Looper وتنتظر فراغه قبل ما تدوس.\n\nرابعاً: `Compose UI Testing`؛ ده الجيل الجديد كلياً لاختبارات واجهات كومبوز. بنستخدم `createComposeRule()`؛ مش بنتعامل مع عناصر الشاشة العادية بل مع شجرة المعاني (Semantics Tree). الميزة الجوهرية هنا هي المزامنة الآلية الذكية؛ الأداة مربوطة بمحرك الـ Recomposition وبتوقف الاختبار لحد ما كل الرندرة والأنيميشن يكتملوا تماماً، وده بيقضي نهائياً على كوابيس الـ Flaky Tests في الـ CI.",
        "deep_answer_ar": "تحت الكابوت، الفوارق المعمارية بين الأدوات دي بتظهر في طريقة التعامل مع الخيوط وتعديل الـ Bytecode في الذاكرة.\n\nمكتبة JUnit 4 بتعتمد في الـ Extensibility على كائنات الـ `TestRule` اللي بتطبق نمط التصميم `Statement`؛ وده بيمكّننا من لف كود الاختبار بـ Coroutine Dispatchers أو تشغيل Transaction للداتابيز تتراجع في الآخر. أما في JUnit 5 فتم استبدال الـ Rules بنظام `Extension API` الأكثر مرونة وحداثة.\n\nوفي المقارنة بين أدوات المحاكاة، MockK بتتميز عن Mockito بتعديل البايت كود المباشر؛ لما بتعمل Mock لدالة suspend، المكتبة بتتدخل في الـ Continuation State Machine الأصلية في كوتلن، وتمرر كائن Fake Continuation بيلغي تعليق الكوروتين فوراً بدون ما يعمل Deadlock لخيط الاختبار.\n\nأما في طبقة الواجهة، الفارق بين Espresso و Compose جوهري جداً في آليات المزامنة.\nEspresso بيراقب الـ MessageQueue التابع لـ `Looper.getMainLooper()` ونبضات الـ Choreographer؛ فلو التطبيق فيه Progress Bar لا نهائي أو أنيميشن متكرر، Espresso هيفضل متعلق لحد ما يرمي `IdlingResourceTimeoutException`.\nبينما Compose UI Testing مبني فوق نظام الـ Snapshots وساعة الـ Virtual Time؛ أول ما تدوس على زرار بـ `performClick()`، الرنتايم بيجبر محرك الـ Recomposer على تنفيذ כל الـ Invalidation Passes وتحديث الـ Layout Node فوراً وتصفية العمليات في نفس اللحظة.\nده اللي بيخلي اختبارات Compose مستقرة بنسبة 100% وسريعة جداً على خوادم الـ CI."
    }
}

# ==========================================
# TST-04: What makes a class testable?
# ==========================================
DATA["TST-04"] = {
    "concept_en": """A class is architecturally testable when its dependencies, side-effects, execution timing, and internal state transitions can be isolated, controlled, and observed deterministically from an external test harness. Achieving high testability requires adhering to core software design principles: Dependency Injection via constructor arguments rather than internal instantiation or global singletons, programming against polymorphic abstractions (interfaces) rather than concrete classes, isolating side-effects into dedicated boundaries, avoiding hardcoded concurrency dispatchers by injecting CoroutineDispatcher instances, avoiding direct system clock queries by abstracting time, and designing pure, deterministic business functions where identical inputs always yield identical outputs without ambient hidden state.""",
    "walkthrough_en": """Refactoring an untestable class into an architecturally pristine testable design:
```kotlin
// ❌ UNTESTABLE CLASS: Hardcoded dependencies, hardcoded IO dispatcher, hardcoded System time!
class BadOrderProcessor {
    private val api = RetrofitClient.orderApi // Hidden singleton! Cannot be mocked!
    private val database = RoomDb.getDatabase() // Hardcoded system database!

    fun processOrder(orderId: String) {
        CoroutineScope(Dispatchers.IO).launch { // Hardcoded dispatcher and scope! Leaks execution!
            val order = api.fetchOrder(orderId)
            if (System.currentTimeMillis() > order.expiryDate) { // Hardcoded system clock!
                database.orderDao().saveStatus(orderId, "EXPIRED")
            }
        }
    }
}

// ✅ ARCHITECTURALLY TESTABLE CLASS: Constructor injection, injected dispatcher, abstract clock!
class TestableOrderProcessor(
    private val orderApi: OrderApi,
    private val orderDao: OrderDao,
    private val ioDispatcher: CoroutineDispatcher = Dispatchers.IO,
    private val clock: Clock = Clock.systemUTC()
) {
    suspend fun processOrder(orderId: String): OrderResult = withContext(ioDispatcher) {
        val order = orderApi.fetchOrder(orderId)
        val isExpired = clock.instant().toEpochMilli() > order.expiryDate
        val status = if (isExpired) "EXPIRED" else "PROCESSED"
        orderDao.saveStatus(orderId, status)
        OrderResult(orderId, status)
    }
}
```""",
    "short_en": """A class is testable when its dependencies and side-effects are completely controllable from the outside. Key characteristics include constructor dependency injection, coding to interfaces rather than concrete classes, injecting CoroutineDispatchers instead of hardcoding Dispatchers.IO, abstracting system clocks to control time, and writing pure deterministic functions without hidden singleton or static states. This allows tests to substitute fakes and assert outputs deterministically on the JVM.""",
    "structured_en": """Designing classes for testability is not an afterthought; it is an architectural discipline that directly shapes production software quality.
An untestable class is characterized by tight coupling: it instantiates its own dependencies internally using the new operator, calls global singletons like MyDatabase.getInstance(), hardcodes Dispatchers.IO, and queries System.currentTimeMillis() directly.
Testing such a class requires heavy bytecode manipulation frameworks and emulators, leading to slow, brittle test suites.
In contrast, a highly testable class adheres to five architectural pillars.
First, it uses constructor dependency injection, receiving all collaborators as explicit constructor parameters.
Second, it programs against polymorphic interfaces, allowing test fixtures to substitute lightweight fakes or mocks without modifying production code.
Third, it manages concurrency transparently by injecting CoroutineDispatcher instances, enabling tests to pass StandardTestDispatcher or UnconfinedTestDispatcher to control coroutine execution synchronously.
Fourth, it abstracts physical time through a Clock interface, allowing tests to travel into the future or simulate expiration conditions instantly.
Fifth, it favors pure functions and immutability, ensuring that given the exact same input arguments, the class consistently produces the exact same output without mutating ambient global state.""",
    "deep_senior_en": """Under the hood, testability principles directly influence the Java bytecode emitted by the Kotlin compiler and how the CPU executes method invocations.
When a class instantiates a concrete dependency inside its body using MyRepositoryImpl(), the compiler generates an invoke-special bytecode instruction tightly binding the class to that specific implementation.
Because invoke-special targets a fixed constructor signature, testing tools cannot intercept the instantiation on standard JVMs without loading specialized bytecode agents that rewrite class definitions before class loading.
Similarly, calling global companion objects or singletons generates static get-static calls, forcing state to persist across test boundaries and contaminating subsequent test runs with dirty memory.
By injecting dependencies via constructor parameters, the compiler emits invoke-virtual or invoke-interface instructions.
This enables dynamic method dispatch at runtime, allowing the JVM to resolve method calls polymorphically to lightweight in-memory fake classes stored in test cache registers.
Furthermore, hardcoding Dispatchers.IO binds coroutines to the platform thread pool, which launches real operating system threads and causes uncontrollable race conditions during assertion execution.
Injecting a CoroutineDispatcher allows unit tests to supply a TestDispatcher tied to a virtual TestCoroutineScheduler.
The scheduler intercepts suspension continuations, executing them deterministically within the calling thread's CPU time slice without thread context switching or asynchronous latency.
Senior engineers treat testability as the ultimate indicator of clean separation of concerns and low architectural coupling.""",
    "meta_ar": {
        "id": "TST-04",
        "questionAr": "ما الذي يجعل الكلاس أو المكون البرمجي قابلاً للاختبار (Testable) في معمارية أندرويد الحديثة؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على تقييم وتصميم كود عالي القابلية للاختبار، وتطبيق مبادئ حقن التبعيات (Dependency Injection)، وفصل الاعتماديات الزمنية وتزامن الكوروتينات (Coroutine Dispatchers).",
        "why_it_matters_ar": "الكلاسات غير القابلة للاختبار تجبر المطورين على الاعتماد على الاختبار اليدوي البطيء، وتؤدي إلى تراكم الديون التقنية وتفشي الأخطاء في الإنتاج عند إجراء أي تعديل.",
        "worked_example_ar": "تحويل كلاس سيء لكلاس عالي الاختبارية:\n```kotlin\n// كلاس ممتاز للاختبار: يستقبل تبعياته في البناء ومحقون فيه الـ Dispatcher والـ Clock\nclass OrderProcessor(\n    private val api: OrderApi,\n    private val dispatcher: CoroutineDispatcher = Dispatchers.IO,\n    private val clock: Clock = Clock.systemUTC()\n) {\n    suspend fun process() = withContext(dispatcher) { ... }\n}\n```",
        "trade_offs_ar": "تصميم كود قابل للاختبار يتطلب كتابة Interfaces وتمرير باراميترات إضافية عبر الـ Constructor، لكنه يمنح مرونة معمارية هائلة وتغطية اختبارية تصل إلى 100% في أجزاء من الثانية.",
        "failure_modes_ar": "تثبيت `Dispatchers.IO` بشكل صلب (Hardcoded) داخل الـ ViewModel أو الـ Repository، مما يجعل اختبار الكوروتينات مستحيلاً بدون مشاكل سباق (Race Conditions).",
        "production_perspective_ar": "في المشروعات الكبيرة، نلزم المطورين بقواعد Detekt تمنع استدعاء `Dispatchers.IO` مباشرة في كود العمل، وتلزم حقن `CoroutineDispatcher` مخصص لتسهيل الاختبارات.",
        "how_to_answer_ar": "حدد الركائز الخمسة للكود القابل للاختبار: حقن التبعيات عبر الـ Constructor، والبرمجة ضد الـ Interfaces، وحقن الـ CoroutineDispatcher بدلاً من تثبيته، وتجريد الوقت عبر Clock interface، والاعتماد على الدوال النقية (Pure functions) وتجنب الـ Singletons والـ Static state.",
        "talking_points_ar": "حقن التبعيات (Constructor Injection)، وتجريد الاعتماديات بـ Interfaces، وحقن الـ Dispatchers واختبار الكوروتينات، وتجريد الوقت (Clock abstraction)، وتفادي الـ Global Singletons.",
        "follow_ups_ar": "- **المحاور:** \"لماذا يعتبر تثبيت `Dispatchers.IO` مباشرة داخل الكلاس كارثة في الاختبارات؟\"\n  **المرشح:** \"لأنه بيشغل الكوروتين على خيوط النظام الحقيقية بالتوازي، فلما التيست يوصل لسطر الـ Assert، الكوروتين بيكون لسه مخلصش على الخيط التاني، فبيرمي خطأ سباق. لكن لو حقنا الـ Dispatcher هنمرر `TestDispatcher` ينفذ كل حاجة متزامنة في نفس اللحظة.\"\n\n- **المحاور:** \"كيف يؤثر استدعاء `System.currentTimeMillis()` على اختبارية الكلاس؟\"\n  **المرشح:** \"بيخلي الكود بيعتمد على ساعة النظام الحقيقية؛ فمش هنعرف نختبر حالات انتهاء الصلاحية أو مرور 30 يوم إلا لو حقنا `Clock` نقدر نقدم ساعته في التيست براحتنا.\"",
        "self_check_ar": "هل شرحت الركائز الخمسة للاختبارية؟ هل بينت خطورة تثبيت Dispatchers.IO و System time؟ وهل شرحت أثر ذلك على كود الإنتاج؟",
        "references_ar": f"- [Android Guide: Write testable code](https://developer.android.com/training/testing/fundamentals/testable-code) — توثيق جوجل الرسمي لكتابة كود عالي القابلية للاختبار.\n- [Clean Code: Principles of Testability](https://martinfowler.com/) — مقالات مارتن فاولر حول هندسة الكود النظيف والقابل للفحص.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "الكلاس بيكون قابلاً للاختبار (Testable) لما نقدر نعزل تبعياته ونتحكم في بيئة تشغيله وتوقيته بشكل قطعي من خارج الكود. ده بيتحقق بخمس ممارسات أساسية: أولاً حقن كل التبعيات عبر الـ Constructor. ثانياً البرمجة ضد الواجهات (Interfaces) بدل الكلاسات الصريحة. ثالثاً حقن مفرقات الكوروتينات `CoroutineDispatcher` بدل تثبيت `Dispatchers.IO`. رابعاً تجريد ساعة النظام باستخدام `Clock interface` للتحكم في الزمن. وخامساً تصميم دوال نقية (Pure Functions) خالية من الكائنات العامة (Singletons) والمتغيرات الساكنة المشتركة.",
        "best_answer_ar": "قابلية الكلاس للاختبار (Testability) هي انعكاس مباشر لجودة ونقاء التصميم المعماري للكود في أندرويد.\n\nالكلاس غير القابل للاختبار هو اللي بيصنع تبعياته بنفسه جوه الدالة باستخدام `new`، أو بينادي كائنات عامة ثابتة زي `Database.getInstance()`، أو بيثبت `Dispatchers.IO` و `System.currentTimeMillis()` جواه. الكود ده بيبقى مربوط بالنظام ويستحيل اختباره على الـ JVM بدون كراشات.\n\nعشان نخلي الكلاس عالي الاختبارية بنلتزم بخمسة مبادئ هندسية:\nأولاً: حقن التبعيات (Constructor Injection)؛ كل حاجة الكلاس محتاجها بتجيله من بره في الـ Constructor، وده بيسمح لنا نمرر كائنات Fake في الاختبار بسهولة.\n\nثانياً: الاعتماد على الـ Interfaces؛ الكلاس بيتعامل مع `UserRepository` كـ Interface مش مع الـ Implementation، فنقدر نستبدلها بنسخة الذاكرة في التيست بدون تعديل سطر واحد في كود الإنتاج.\n\nثالثاً: حقن الـ CoroutineDispatcher؛ بنمرر الـ Dispatcher كباراميتر قيمته الافتراضية `Dispatchers.IO`، وفي التيست بنمرر مكانه `TestDispatcher` عشان نجبر الكوروتين يشتغل بشكل متزامن وتحت سيطرتنا التامة.\n\nرابعاً: تجريد الوقت؛ بدل `System.currentTimeMillis()` بنحقن كائن `Clock`، فنقدر نحاكي مرور 30 يوم وانتهاء صلاحية التوكن في جزء من الثانية.\n\nخامساً: الدوال النقية؛ بنحرص إن الدوال تكون مدخلاتها واضحة ومخرجاتها محددة وخالية من أي كائنات عامة (Singletons) بتسرب حالة بين الاختبارات.",
        "deep_answer_ar": "تحت الكابوت، مبادئ قابلية الاختبار بتنعكس مباشرة على كود الـ Bytecode اللي بيطلعه كومبايلر كوتلن في الـ JVM.\nلما كلاس بينشئ تبعيته بنفسه باستخدام `MyRepo()`، الكومبايلر بيولد تعليمة بايت كود صلبة اسمها `invokespecial` بتربط الكلاس فوراً بتلك النسخة في الذاكرة. مفيش أي وسيلة في الـ JVM لتجاوز `invokespecial` بدون تشغيل أدوات تعديل البايت كود المتقدمة زي ByteBuddy وقت تحميل الكلاس، وده بيثقل الاختبارات جداً.\nونفس الأمر بيحصل مع الـ Singletons العامة؛ استدعاؤها بيولد تعليمات `getstatic` بتخلي الحالة مشتركة في الذاكرة وممكن اختبار يلوث بيانات اختبار تاني (State Pollution).\n\nبينما لما بنحقن التبعيات كـ Interfaces في الـ Constructor، الكومبايلر بيولد تعليمات `invokeinterface` أو `invokevirtual`.\nالتعليمات دي بتعتمد على الـ Polymorphic Dispatch؛ الرنتايم بيقرر في أجزاء من النانو ثانية ينفذ دالة كائن الـ Fake المخزن في سجلات المعالج بدون أي كلفة أو Reflection.\n\nوفوق كده، تثبيت `Dispatchers.IO` بشكل صلب بيجبر الكوروتين على تشغيل Threads حقيقية في نظام التشغيل؛ ولما خيط التيست يوصل لسطر الـ Assert بيكون خيط الـ IO لسه بيكتب في الذاكرة، فبيحصل خطأ سباق (Race Condition) ويفشل التيست بشكل متقلب (Flaky).\nحقن الـ Dispatcher بيمكننا من استخدام `TestCoroutineScheduler`؛ المحرك بيلغي الخيوط المتوازية وينفذ كل الكوروتينات على نفس خيط التيست بشكل تسلسلي مضبوط بالمللي ثانية، وده سر نجاح الاختبارات في الشركات الكبرى."
    }
}

# ==========================================
# TST-05: What is runTest? How are virtual time and TestScope used?
# ==========================================
DATA["TST-05"] = {
    "concept_en": """runTest is the official coroutine test runner provided by kotlinx-coroutines-test that executes suspending test blocks synchronously while controlling execution timing via virtual time virtualization. Built on top of TestScope and TestCoroutineScheduler, runTest creates an isolated testing environment where delay() calls skip real-world wall-clock latency, executing long delays in sub-millisecond CPU time. The underlying TestScope exposes virtual time control primitives—including advanceTimeBy(), advanceUntilIdle(), and runCurrent()—alongside an internal currentTime property that mirrors virtual elapsed milliseconds. Additionally, runTest automatically monitors unhandled coroutine exceptions, guarantees that all child coroutines launched in the test scope finish or are cancelled before the test exits, and enforces a safety timeout to prevent deadlocks.""",
    "walkthrough_en": """Controlling virtual time and testing long delays using runTest and TestScope:
```kotlin
class AutoLogoutUseCaseTest {
    @Test
    fun userInactivity_triggersLogout_afterThirtySeconds() = runTest {
        var isLoggedOut = false

        // Launch an asynchronous coroutine that delays for 30 real seconds!
        val job = backgroundScope.launch {
            delay(30_000) // Skips 30 seconds instantly via virtual time!
            isLoggedOut = true
        }

        // 1. Initial assertion at time T = 0ms
        assertEquals(0, currentTime)
        assertFalse(isLoggedOut)

        // 2. Fast-forward virtual clock by 10 seconds (T = 10,000ms)
        advanceTimeBy(10_000)
        assertEquals(10_000, currentTime)
        assertFalse(isLoggedOut)

        // 3. Fast-forward past the threshold (T = 30,000ms)
        advanceTimeBy(20_001)
        assertEquals(30_001, currentTime)
        assertTrue(isLoggedOut)

        job.cancel()
    }
}
```""",
    "short_en": """runTest is the primary test runner in kotlinx-coroutines-test that executes suspending code with virtual time control. Delays are skipped instantly, allowing hours of simulated time to pass in milliseconds. It provides a TestScope backed by TestCoroutineScheduler, exposing controls like advanceTimeBy to move the virtual clock, advanceUntilIdle to run all pending work, and runCurrent to drain current tasks, guaranteeing synchronous, deterministic coroutine testing without thread sleeps.""",
    "structured_en": """Testing asynchronous coroutine workflows reliably requires eliminating unpredictable wall-clock latency, which is the primary purpose of runTest.
Replacing deprecated testing utilities like runBlockingTest and runBlocking, runTest creates a dedicated TestScope configured with a TestCoroutineScheduler.
When a coroutine inside runTest invokes delay(10_000), it does not pause or block the operating system thread for ten seconds.
Instead, the scheduler captures the continuation and schedules it on an internal virtual timeline, skipping the delay instantly.
Within the runTest lambda, developers control time progression deterministically using three core TestScope APIs.
advanceTimeBy(millis) moves the virtual clock forward by a specified duration, executing all scheduled tasks whose trigger times fall within that window.
advanceUntilIdle() advances virtual time until the scheduler's queue is completely empty, ensuring all active and delayed background coroutines run to completion.
runCurrent() executes all tasks scheduled at the current exact timestamp without advancing the virtual clock.
Furthermore, runTest provides built-in safety: it fails the test if unhandled exceptions occur in child coroutines, asserts that no active jobs are leaked upon completion, and enforces a default sixty-second execution timeout to prevent infinite loops.""",
    "deep_senior_en": """Under the hood, runTest coordinates its deterministic execution through TestCoroutineScheduler, which replaces the physical system clock with an event-driven virtual priority queue.
When runTest initializes, it instantiates a TestScope whose CoroutineContext contains a StandardTestDispatcher linked to this shared scheduler.
Every coroutine launched inside the test scope or using backgroundScope inherits this scheduler.
When a coroutine calls delay(duration), the Kotlin coroutines runtime intercepts the suspension point.
Rather than dispatching to an OS timer via ScheduledExecutorService, the StandardTestDispatcher wraps the Continuation into a timed task object and inserts it into the scheduler's Min-Heap priority queue, indexed by target virtual timestamp (currentTime + duration).
The coroutine yields execution, returning control immediately to the test runner thread.
When the developer invokes advanceTimeBy(duration), the scheduler advances its internal currentTime variable and enters an execution loop.
It pops all scheduled tasks whose execution timestamp is less than or equal to the new currentTime, dispatching their continuations synchronously on the test thread in chronological order.
Calling advanceUntilIdle() repeatedly inspects the priority queue and advances currentTime to match the next scheduled task until the queue is completely drained.
If background jobs run forever—such as infinite while(true) event loops—developers launch them inside backgroundScope.
runTest automatically cancels the backgroundScope upon test completion, preventing pending continuous tasks from hanging the test runner while verifying state transitions with zero real-world execution delay.""",
    "meta_ar": {
        "id": "TST-05",
        "questionAr": "ما هي دالة `runTest` في مكتبة `kotlinx-coroutines-test`؟ وكيف يُستخدم الوقت الافتراضي (Virtual Time) و `TestScope`؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على اختبار الكوروتينات باحترافية، وفهم آلية الوقت الافتراضي (Virtual Time) لتخطي الـ delays، واستخدام دوال التحكم في الجدولة (`advanceTimeBy` و `advanceUntilIdle`) ودور `backgroundScope`.",
        "why_it_matters_ar": "استخدام `runBlocking` مع دوال تحتوي على `delay` يوقف خيط الاختبار لثوانٍ حقيقية، مما يفسد سرعة الـ CI ويجعل اختبار المهام الزمنية الطويلة بطيئاً جداً وغير مستقر.",
        "worked_example_ar": "التحكم في الوقت الافتراضي بـ runTest وتخطي 30 ثانية في جزء من الميلي ثانية:\n```kotlin\n@Test fun testTimeout() = runTest {\n    var triggered = false\n    backgroundScope.launch { delay(30_000); triggered = true }\n    assertFalse(triggered)\n    advanceTimeBy(30_001) // تقديم الوقت الافتراضي فوراً\n    assertTrue(triggered)\n}\n```",
        "trade_offs_ar": "استخدام `runTest` يوفر سرعة مذهلة في اختبارات الكوروتينات المعقدة، لكنه يتطلب فهماً عميقاً لفرق الجدولة بين العمليات المتزامنة والعمليات المؤجلة لتفادي الأخطاء الوهمية.",
        "failure_modes_ar": "إطلاق كوروتين لا نهائي (`while(true)`) داخل الـ Scope العادي لـ `runTest`، مما يسبب فشل التيست بـ `UncompletedCoroutinesError` بدلاً من إطلاقه داخل `backgroundScope`.",
        "production_perspective_ar": "في المشروعات الكبيرة، نمنع استخدام `runBlocking` أو `Thread.sleep` نهائياً في الاختبارات، ونلزم تشغيل كل اختبارات الكوروتينات داخل `runTest` مع التحكم بالساعة الافتراضية.",
        "how_to_answer_ar": "عرف دالة runTest كإطار اختبار رسمي للكوروتينات يوفر بيئة TestScope، واشرح مفهوم الوقت الافتراضي (Virtual Time) لتخطي الـ delay فوراً، واذكر الدوال الثلاثة للتحكم: advanceTimeBy و advanceUntilIdle و runCurrent، واشرح دور backgroundScope في إدارة المهام المستمرة.",
        "talking_points_ar": "مفهوم Virtual Time وتخطي الـ delay، ودور TestCoroutineScheduler، ودوال advanceTimeBy و advanceUntilIdle و runCurrent، وإدارة المهام اللانهائية بـ backgroundScope، والحماية من تسريب الـ Jobs.",
        "follow_ups_ar": "- **المحاور:** \"ما هو الفرق الجوهري بين `runBlocking` و `runTest`؟\"\n  **المرشح:** \"`runBlocking` بيوقف الخيط الحقيقي في نظام التشغيل لو فيه `delay(5000)`، فالتيست هياخد 5 ثواني حقيقية، بينما `runTest` بيستخدم ساعة افتراضية بتقدم الـ 5 ثواني في جزء من الميلي ثانية وبدون أي انتظار حقيقي.\"\n\n- **المحاور:** \"متى يجب استخدام `backgroundScope` داخل `runTest`؟\"\n  **المرشح:** \"لما نكون بنختبر جمع بيانات من Flow مستمر أو وظيفة فيها لوب لا نهائي؛ عشان `runTest` ميعلقش مستني الكوروتين يخلص، بل يقفله تلقائياً أول ما كود التيست ينتهي.\"",
        "self_check_ar": "هل شرحت فكرة الوقت الافتراضي بوضوح؟ هل بينت استخدامات advanceTimeBy و advanceUntilIdle؟ وهل ذكرت دور backgroundScope؟",
        "references_ar": f"- [Kotlin Coroutines Test Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/) — التوثيق الرسمي لمكتبة اختبار الكوروتينات من JetBrains.\n- [Testing Coroutines on Android](https://developer.android.com/kotlin/coroutines/test) — دليل جوجل الرسمي لاختبار الكوروتينات في أندرويد.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "دالة `runTest` هي أداة الاختبار الرسمية للكوروتينات في مكتبة `kotlinx-coroutines-test`؛ وظيفتها تشغيل كود الـ Coroutines والـ suspend functions بشكل متزامن وبتحكم كامل في الوقت عبر تقنية الوقت الافتراضي (Virtual Time). دالة `delay()` جواها مش بتوقف خيط المعالج، بل بتتخطى الوقت فوراً، فتقدر تختبر تأخير مدته ساعة كاملة في كسر من الميلي ثانية. وبتوفر كائن `TestScope` اللي بيمكّننا من تحريك ساعة الاختبار يدويياً باستخدام `advanceTimeBy` أو تنفيذ كل المهام المعلقة بـ `advanceUntilIdle` مع ضمان تنظيف الكوروتينات عند انتهاء الفحص.",
        "best_answer_ar": "دالة `runTest` هي المعيار الحديث والبديل الرسمي لـ `runBlockingTest` و `runBlocking` القديمة، ومصممة خصيصاً للقضاء على الانتظار الحقيقي في اختبارات أندرويد.\n\nالميزة الجوهرية هي تقنية الوقت الافتراضي (Virtual Time)؛ لو كود العمل بتاعك فيه `delay(60_000)` عشان يعمل Auto-logout بعد دقيقة، `runTest` مش بتوقف خيط التيست 60 ثانية حقيقية، بل بتسجل الكوروتين في جدول زمني افتراضي وتتخطى الدقيقة دي في جزء من الميلي ثانية بدون أي استهلاك لوقت الـ CI.\n\nجوا البلوك بتاع `runTest`، بنكون شغالين داخل `TestScope`، وده بيدينا تلات دوال سحرية للتحكم في تدفق الزمن:\nأولاً: `advanceTimeBy(millis)`؛ دي بتمشي عقارب الساعة الافتراضية مدة معينة للأمام، وتنفذ أي كوروتين كان مستني في الفترة دي.\n\nثانياً: `advanceUntilIdle()`؛ دي بتمشي الزمن وبتنفذ كل الكوروتينات المعلقة في الطابور لحد ما الطابور يفضى تماماً، وده ممتاز للتأكد إن كل العمليات الخلفية خلصت.\n\nثالثاً: `runCurrent()`؛ دي بتنفذ المهام المجدولة في نفس اللحظة الحالية بدون تقديم الساعة.\n\nوفوق كده، `runTest` بتحمينا من تسريب الكوروتينات؛ لو فيه كوروتين رمى Exception غير معالج التيست بيفشل فوراً، ولو فيه مهام لا نهائية بنشغلها في `backgroundScope` فبيتم إلغاؤها أوتوماتيكياً أول ما التيست يخلص.",
        "deep_answer_ar": "تحت الكابوت، السحر كله في `runTest` بيتم إدارته عبر كائن داخلي اسمه `TestCoroutineScheduler`.\nأول ما `runTest` بتبدأ، بتنشئ `TestScope` بيحتوي على دسباتشر من نوع `StandardTestDispatcher` مربوط بجدول الـ Scheduler ده. كل الكوروتينات اللي بتنطلق داخل التيست بتشارك نفس الـ Scheduler وساعة الـ Virtual Time الموحدة.\n\nلما الكود ينادي `delay(duration)`، الكوروتين بينادي `Continuation.suspendCoroutine`. في الوضع الطبيعي، النظام بيبعت المهمة لـ OS Timer. لكن دسباتشر الاختبار بيتدخل، وبياخد كائن الـ Continuation ويغلفه في مهمة زمنية محددة بوقت الهدف `currentTime + duration` ويضيفها في طابور أولويات (Min-Heap Priority Queue) داخل الـ Scheduler، ويرجع التحكم فوراً لخيط التيست بدون أي نوم للخيط!\n\nلما المطور ينادي `advanceTimeBy(duration)`، الـ Scheduler بيعدل قيمة متغير `currentTime`، وبيدخل في حلقة تفريغ؛ بيمسك كل المهام المسجلة في الـ Priority Queue اللي وقتها أقل من أو يساوي الوقت الجديد، ويطلق الـ Continuations بتاعتها بشكل متزامن على خيط الفحص بالترتيب الزمني الصحيح.\nودالة `advanceUntilIdle()` بتكرر العملية دي أوتوماتيكياً لحد ما الطابور يفرغ تماماً. وفوق كده، دالة `runTest` بتمتلك تايم آوت أمان مدته 60 ثانية افتراضياً لحماية خوادم الـ CI من التعليق اللا نهائي لو فيه كوروتين فضل مستني تدفق مبيخلصش، وده بيضمن أعلى درجة من الانضباط والموثوقية في خطوط البناء المستمر للشركات الكبرى.\nعشان كده، كود الإنتاج بيختبر أصعب سيناريوهات الـ Timeouts والـ Delays بدون أي Flakiness وبأقصى سرعة ممكنة."
    }
}

# ==========================================
# TST-06: Compare StandardTestDispatcher and UnconfinedTestDispatcher.
# ==========================================
DATA["TST-06"] = {
    "concept_en": """kotlinx-coroutines-test provides two specialized test dispatchers that manage task queuing, virtual time coordination, and execution eagerness differently. StandardTestDispatcher queues all coroutine tasks onto the underlying TestCoroutineScheduler without executing them eagerly; newly launched coroutines suspend at launch until the test author explicitly advances virtual time via advanceUntilIdle(), advanceTimeBy(), or runCurrent(). This ensures deterministic, fine-grained control over concurrency and race conditions. In contrast, UnconfinedTestDispatcher executes coroutines eagerly and eagerly dispatches them immediately on the caller thread until their first suspension point. This eliminates manual scheduler pumps for simple, sequential coroutine tests, but can obscure concurrent race conditions if misapplied.""",
    "walkthrough_en": """Contrasting the execution behavior of StandardTestDispatcher vs UnconfinedTestDispatcher:
```kotlin
// 1. StandardTestDispatcher: QUEUES execution; requires explicit scheduler pumping!
@Test
fun standardDispatcher_requiresExplicitAdvancement() = runTest {
    val standardDispatcher = StandardTestDispatcher(testScheduler)
    var step = 1

    CoroutineScope(standardDispatcher).launch {
        step = 2 // Does NOT execute immediately! Queued in scheduler!
    }

    // Step is still 1 because the coroutine is queued, not executed!
    assertEquals(1, step)

    // Explicitly drain the scheduler queue
    runCurrent()
    assertEquals(2, step)
}

// 2. UnconfinedTestDispatcher: EAGER execution; runs immediately until suspension!
@Test
fun unconfinedDispatcher_executesEagerly() = runTest {
    val unconfinedDispatcher = UnconfinedTestDispatcher(testScheduler)
    var step = 1

    CoroutineScope(unconfinedDispatcher).launch {
        step = 2 // Executes IMMEDIATELY on the current thread!
    }

    // Step is ALREADY 2 without calling runCurrent()!
    assertEquals(2, step)
}
```""",
    "short_en": """StandardTestDispatcher queues newly launched coroutines without executing them immediately, requiring explicit calls like advanceUntilIdle() or runCurrent() to progress. This provides fine-grained control to test race conditions and concurrency. In contrast, UnconfinedTestDispatcher executes coroutines eagerly on the caller thread until the first suspension point, removing the need for manual scheduler advancement in simple sequential tests.""",
    "structured_en": """Selecting between StandardTestDispatcher and UnconfinedTestDispatcher is an important architectural decision when testing asynchronous Kotlin flows.
Both dispatchers share the exact same TestCoroutineScheduler and virtual clock, but they differ fundamentally in execution eagerness.
StandardTestDispatcher is the default dispatcher utilized by runTest.
It adopts a strict, non-eager scheduling policy: whenever a new coroutine is launched, its execution block is placed into the scheduler's queue and yields control.
The coroutine will not execute a single line of code until the test author explicitly pumps the queue using runCurrent(), advanceTimeBy(), or advanceUntilIdle().
This behavior provides ultimate deterministic control, making StandardTestDispatcher indispensable for simulating race conditions, verifying intermediate loading states, and inspecting UI state before an asynchronous operation completes.
Conversely, UnconfinedTestDispatcher embraces eager execution.
When a coroutine is launched on UnconfinedTestDispatcher, it immediately hijacks the calling thread and executes synchronously until it encounters its first true suspension point.
This eager behavior closely mimics synchronous code, eliminating the boilerplate of calling advanceUntilIdle() for straightforward, sequential tests such as mapping ViewModels or testing simple StateFlow emissions.""",
    "deep_senior_en": """Under the hood, the architectural disparity between StandardTestDispatcher and UnconfinedTestDispatcher lies inside their respective dispatch() and isDispatchNeeded() implementations.
When a coroutine is launched or resumed via CoroutineScope.launch(StandardTestDispatcher), the dispatcher's isDispatchNeeded() method returns true.
Its internal dispatch(context, block) method packages the Runnable block into a ScheduledDispatchTask and enqueues it directly into the TestCoroutineScheduler's task queue without invoking block.run().
The calling thread continues executing subsequent test assertions uninterrupted, guaranteeing that concurrent coroutines remain suspended in their initial state until the developer explicitly triggers queue execution.
Furthermore, because StandardTestDispatcher forces coroutines to yield until the scheduler advances, senior engineers utilize it when orchestrating multi-step architectural assertions, verifying that UI widgets display intermediate shimmers or loading placeholders before long-running network responses complete.
In stark contrast, UnconfinedTestDispatcher overrides dispatch behavior to achieve eager execution.
When launch(UnconfinedTestDispatcher) is invoked, isDispatchNeeded() evaluates to false for unconfined entries, or its dispatch implementation immediately invokes block.run() synchronously on the current thread.
The coroutine executes its instructions until it encounters a suspending call (such as a network call or delay).
Only upon actual suspension does it yield control back to the test runner.
While UnconfinedTestDispatcher streamlines testing by reducing manual scheduler calls, senior engineers exercise caution: because eager execution alters the natural concurrency interleaving of production dispatchers (like Dispatchers.Default or Dispatchers.IO), it can inadvertently mask real concurrency race conditions and deadlocks that occur in multi-threaded production environments.""",
    "meta_ar": {
        "id": "TST-06",
        "questionAr": "قارن بين `StandardTestDispatcher` و `UnconfinedTestDispatcher` في اختبارات الكوروتينات.",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على المقارنة بين الدسباتشر القياسي والتلقائي في مكتبة الاختبار، وفهم سلوك التنفيذ المؤجل (Queued) مقابل الفوري (Eager)، واختيار الأنسب لمنع الأخطاء التزامنية الخفية.",
        "why_it_matters_ar": "سوء اختيار الدسباتشر قد يخفي عيوب سباق حقيقية في الكود (Race Conditions) لأن `Unconfined` ينفذ الكود فوراً، بينما `Standard` يتيح فحص الحالات البينية بدقة متناهية.",
        "worked_example_ar": "الفرق بين التنفيذ المؤجل والفوري برمجياً:\n```kotlin\n// Standard: يضع المهمة في الطابور ولا ينفذها إلا بطلب صريح\nlaunch(StandardTestDispatcher(testScheduler)) { state = \"Loaded\" }\nassertEquals(\"Initial\", state); runCurrent(); assertEquals(\"Loaded\", state)\n\n// Unconfined: ينفذ الكود فوراً حتى أول نقطة تعليق\nlaunch(UnconfinedTestDispatcher(testScheduler)) { state = \"Loaded\" }\nassertEquals(\"Loaded\", state) // اتنفذ فوراً بدون runCurrent\n```",
        "trade_offs_ar": "`UnconfinedTestDispatcher` يجعل الاختبارات أبسط وأقصر بدون استدعاءات `runCurrent` يدوية، لكنه قد يخفي عيوب التزامن؛ بينما `StandardTestDispatcher` يتطلب تحكماً يدوياً لكنه يوفر أقصى دقة لمحاكاة التزامن الحقيقي.",
        "failure_modes_ar": "استخدام `UnconfinedTestDispatcher` لاختبار حالة التحميل `isLoading = true` متبوعة بـ `false`؛ لأن التنفيذ الفوري سيتخطى حالة الـ true ولن تتمكن من فحص ظهور الـ Loader في الواجهة.",
        "production_perspective_ar": "في المشروعات الكبيرة، نعتمد `StandardTestDispatcher` كخيار افتراضي في قواعد الـ MainDispatcherRule لفحص الحالات الانتقالية، ونقصر `Unconfined` على اختبارات تدفق البيانات البسيطة.",
        "how_to_answer_ar": "وضح الفارق الجوهري: كلاهما يشترك في نفس الـ Scheduler، لكن StandardTestDispatcher يضع المهام في الطابور ولا ينفذها إلا باستدعاء صريح (Queued execution) مما يتيح فحص الحالات الانتقالية، بينما UnconfinedTestDispatcher ينفذ الكود فوراً على نفس الخيط (Eager execution) حتى أول نقطة تعليق، مع ذكر محاذير إخفاء عيوب السباق.",
        "talking_points_ar": "مفهوم Queued مقابل Eager execution، وفحص الحالات الانتقالية (Loading states)، والاشتراك في نفس TestCoroutineScheduler، ومخاطر إخفاء الـ Race Conditions بـ Unconfined.",
        "follow_ups_ar": "- **المحاور:** \"لماذا يعتبر StandardTestDispatcher أفضل عند اختبار حالات الـ Loading في الـ ViewModel؟\"\n  **المرشح:** \"لأنه مبيشغلش الكوروتين فوراً، فبنقدر نعمل Assert إن `isLoading == true`، وبعدين ننادي `advanceUntilIdle()` ونعمل Assert إنها رجعت `false`، بعكس Unconfined اللي هينفذ الدالة كلها في لحظتها ومش هنلحق نشوف حالة الـ Loading.\"\n\n- **المحاور:** \"هل يختلف الاثنان في كيفية التعامل مع الـ delay والوقت الافتراضي؟\"\n  **المرشح:** \"لا، كلاهما بيعتمد على نفس كائن `TestCoroutineScheduler` وبيتخطوا الـ delay بالوقت الافتراضي بنفس الكفاءة.\"",
        "self_check_ar": "هل شرحت الفرق بين التنفيذ المؤجل والفوري؟ هل وضحت سيناريو فحص الـ Loading state؟ وهل ذكرت الفارق المعماري في dispatching؟",
        "references_ar": f"- [Kotlin Testing Dispatchers](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/kotlinx.coroutines.test/-test-dispatcher/) — التوثيق الرسمي لدسباتشرات الاختبار في كوتلن.\n- [Testing Coroutines: Dispatcher Best Practices](https://developer.android.com/kotlin/coroutines/test) — دليل جوجل العملي لاختيار دسباتشر الاختبار.",
        "quick_answer_ar": "الاختلاف الجوهري بين `StandardTestDispatcher` و `UnconfinedTestDispatcher` بيكمن في توقيت وحماسة التنفيذ (Eagerness)، مع إن الاتنين مربوطين بنفس جدول الوقت الافتراضي (`TestCoroutineScheduler`). الـ `StandardTestDispatcher` هو الافتراضي؛ بيحط الكوروتينات الجديدة في طابور انتظار ومش بينفذها نهائياً إلا لما تطلب ده صراحة بـ `runCurrent()` أو `advanceUntilIdle()`، وده بيديك تحكم كامل لفحص الحالات البينية والتسابق. أما الـ `UnconfinedTestDispatcher` فبينفذ الكود بحماسة وفوراً (Eagerly) على نفس الخيط لحد ما يقابل أول نقطة تعليق، وده بيسهل التيستات البسيطة بدون الحاجة لاستدعاء دوال تفريغ الطابور يدوياً.",
        "best_answer_ar": "المقارنة بين الدسباتشرين دول بتوضح مدى فهم المهندس للتحكم في تزامن الكوروتينات داخل بيئة الاختبار.\n\nكلا الدسباتشرين بيعتمدوا على نفس ساعة الوقت الافتراضي، لكن فلسفة التشغيل مختلفة تماماً:\n\n`StandardTestDispatcher` بيتبع سياسة 'التنفيذ المؤجل في الطابور' (Queued Execution)؛ أول ما تطلق كوروتين جديد، هو مبيشتغلش فوراً، بل بيتحط في طابور المهام. الميزة العبقرية هنا هي إنك تقدر تفحص الحالة البينية؛ يعني مثلاً بعد استدعاء دالة جلب البيانات، تقدر تتأكد إن `uiState.isLoading == true`، وبعدين تستدعي `advanceUntilIdle()` وتتأكد إن البيانات وصلت واللودر اختفى. ده بيخليه الأداة المثالية لاختبار الـ ViewModels والتسابق (Race Conditions).\n\nأما `UnconfinedTestDispatcher` فبيتبع سياسة 'التنفيذ الفوري المتحمس' (Eager Execution)؛ أول ما تطلق الكوروتين، بيخطف الخيط الحالي وينفذ الكود فوراً وبشكل متزامن لحد ما يقابل أول دالة suspend حقيقية. ده بيخلي التيست يبان زي الكود المتزامن العادي ومبيحتاجش منك تنادي `runCurrent()` بعد كل خطوة.\n\nلكن العيب الخطير في `Unconfined` إنه ممكن يخفي عيوب سباق حقيقية في كود الإنتاج؛ لأن التنفيذ الفوري بيغير الترتيب الطبيعي للخيوط، عشان كده المهندس السينيور بيعتمد على `StandardTestDispatcher` في معظم الحالات لضمان محاكاة الواقع بدقة.",
        "deep_answer_ar": "تحت الكابوت، الفارق المعماري بين الدسباتشرين بيكمن في كود دالة `dispatch()` ودالة `isDispatchNeeded()` داخل مكتبة `kotlinx-coroutines-test`.\n\nفي `StandardTestDispatcher`، دالة `isDispatchNeeded()` بترجع دايماً `true`. ولما كود التيست ينادي `launch`، دالة `dispatch(context, block)` بتاخد الـ Runnable بتاع الكوروتين وتغلفه في كائن اسمه `ScheduledDispatchTask` وتضيفه مباشرة في طابور الـ Min-Heap التابع لـ `TestCoroutineScheduler` بدون ما تنادي `block.run()` إطلاقاً. خيط الاختبار بيفضل ماشي في السطور التالية بدون مقاطعة، والكوروتين بيفضل معلق في حالة خمول لحد ما يحصل Pump صريح للطابور.\n\nبينما في `UnconfinedTestDispatcher`، دالة `isDispatchNeeded()` بترجع `false` عند بدء الإطلاق الأول، أو دالة `dispatch` بتستدعي `block.run()` فوراً وبشكل متزامن على خيط الفحص الحالي! الكوروتين بيبدأ يشتغل وينفذ كل التعليمات البرمجية سطر بسطر لحد ما يوصل لنقطة تعليق حقيقية (Suspension Point). ساعتها بس بيتوقف ويرجع التحكم لسطر التيست.\nوفوق كده، ميزة `StandardTestDispatcher` الكبرى إنها بتخليك تفحص ظهور هياكل الـ Shimmer ومؤشرات التحميل في واجهات كومبوز خطوة بخطوة قبل اكتمال الاستجابة، وده بيضمن أعلى معايير الجودة والاستقرار في بيئات العمل الحقيقية.\n\nالخطورة هنا إن دسباتشرات الإنتاج الحقيقية زي `Dispatchers.IO` و `Dispatchers.Default` شغالة بـ Queued Execution على خيوط تانية؛ فلو اعتمدت دايماً على `Unconfined` في اختباراتك، أنت بتلغي احتمالية حدوث أي Interleaving بين العمليات المتزامنة، وممكن تمرر أخطاء Deadlocks و Race Conditions خطيرة لخوادم الإنتاج بدون ما تكتشفها في الـ CI."
    }
}

# ==========================================
# TST-07: What is the test pyramid, and where do contract tests fit?
# ==========================================
DATA["TST-07"] = {
    "concept_en": """The Test Pyramid is a foundational software engineering framework, originally popularized by Mike Cohn, that dictates the strategic distribution of automated tests across an enterprise application. The pyramid prescribes a broad base of fast, deterministic, inexpensive unit tests (comprising approximately 70-80% of test volume), a middle tier of integration and component tests (15-20%), and a narrow apex of end-to-end and UI instrumentation tests (5-10%). Contract Testing sits at the critical integration boundary between mobile client applications and backend microservices. Rather than spinning up heavyweight end-to-end device environments against live staging servers, contract testing uses tools like Pact or JSON schema validators to establish and verify explicit, versioned agreements between client serialization models and backend API responses on the JVM.""",
    "walkthrough_en": """Verifying consumer-driven contract agreements using JSON Schema and MockWebServer:
```kotlin
// 1. Consumer Contract Specification (Client Model Expectation)
@Serializable
data class UserContractDto(
    val id: String,
    val email: String,
    val isVerified: Boolean // Contract requires non-null boolean!
)

// 2. JVM Contract Verification Test using MockWebServer
class UserApiContractTest {
    private val mockWebServer = MockWebServer()
    private lateinit var api: UserApiService

    @Before
    fun setup() {
        mockWebServer.start()
        api = Retrofit.Builder()
            .baseUrl(mockWebServer.url("/"))
            .addConverterFactory(Json.asConverterFactory("application/json".toMediaType()))
            .build()
            .create(UserApiService::class.java)
    }

    @After
    fun tearDown() = mockWebServer.shutdown()

    @Test
    fun contractVerification_matchesBackendAgreement() = runTest {
        // Enforce shared Pact contract fixture
        val contractJson = "{\"id\": \"usr_101\", \"email\": \"dev@company.com\", \"isVerified\": true}"
        mockWebServer.enqueue(MockResponse().setBody(contractJson).setResponseCode(200))

        val result = api.getUser("usr_101")

        assertEquals("usr_101", result.id)
        assertEquals("dev@company.com", result.email)
        assertTrue(result.isVerified)
    }
}
```""",
    "short_en": """The test pyramid distributes tests strategically: 70-80% fast, isolated unit tests at the base, 15-20% integration tests in the middle, and 5-10% end-to-end UI tests at the peak. Contract tests fit at the client-server integration boundary. Using consumer-driven contracts like Pact, they verify that API JSON payloads match client data models and nullability expectations on the JVM, catching breaking backend changes without expensive end-to-end tests.""",
    "structured_en": """The test pyramid is the premier architectural blueprint for maintaining scalable, cost-effective test automation in enterprise mobile engineering.
The pyramid is structured into three primary tiers defined by their execution speed, cost, and fidelity.
At the broad base reside unit tests, representing roughly 70 to 80 percent of the total suite.
Because they execute on the local host JVM in milliseconds without platform overhead, they exhaustively verify business rules, domain invariants, and mathematical calculations.
The middle tier consists of integration tests, accounting for 15 to 20 percent of tests, which validate boundary communication between repositories, local SQLite databases, and networking serialization layers.
At the narrow peak are end-to-end and UI tests, representing only 5 to 10 percent of tests, which validate critical revenue paths on real device emulators.
Contract tests fit squarely at the integration layer between the mobile application and backend microservices.
In microservice architectures, mobile apps frequently break when backend teams rename JSON keys, alter field nullability, or change date formats.
Rather than attempting to detect these regressions via flaky, slow end-to-end tests, teams implement Consumer-Driven Contracts using frameworks like Pact.
The mobile app defines a strict contract specifying the exact JSON schemas and field types it consumes.
Both client and server validate against this shared contract in their respective CI pipelines, catching breaking API changes instantly on the JVM.""",
    "deep_senior_en": """Under the hood, the test pyramid and contract testing address the fundamental economics of automated verification: test execution duration, infrastructure compute cost, and test flakiness.
In an inverted test pyramid (an anti-pattern often referred to as the Ice Cream Cone), organizations write hundreds of UI and end-to-end tests while neglecting unit tests.
Because end-to-end tests depend on device emulators, Wi-Fi connectivity, database seeds, and backend staging health, their failure probability compounds exponentially across multiple network hops.
Contract testing neutralizes this systemic flakiness through schema decoupling and deterministic JVM execution.
When using Consumer-Driven Contract testing via tools like Pact or OpenAPI Schema Validation, the mobile client authors an executable contract fixture in JSON format detailing expected endpoints, HTTP methods, headers, and response bodies with explicit Kotlinx Serialization constraints.
During client CI builds, MockWebServer replays the contract file locally, asserting that the Kotlin serialization engine deserializes every field without throwing SerializationException or MissingFieldException.
Simultaneously, the backend CI pipeline downloads the identical contract file from a central Pact Broker and runs a provider verification pass, asserting that the live backend endpoints produce payloads matching the consumer's schema.
If a backend engineer makes a previously mandatory field nullable, the provider contract verification immediately fails in their pull request before any code merges.
This eliminates breaking API regressions across distributed engineering organizations without firing a single mobile emulator.""",
    "meta_ar": {
        "id": "TST-07",
        "questionAr": "ما هو هرم الاختبارات (Test Pyramid) في أندرويد؟ وأين تقع اختبارات العقود (Contract Tests)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على وضع استراتيجية توزيع الاختبارات (الهرم مقابل مخروط الآيس كريم المقلوب)، وفهم مفهوم الـ Contract Testing ودورها في حماية تكامل الـ Mobile مع الـ Backend بـ Pact.",
        "why_it_matters_ar": "إهمال هرم الاختبارات يجعل الـ CI بطيئاً وهشاً، وتجاهل اختبارات العقود يؤدي لانهيار التطبيق في الإنتاج فجأة بسبب تغيير مهندسي الـ Backend لاسم حقل في الـ JSON.",
        "worked_example_ar": "فحص عقد الـ API على الـ JVM باستخدام MockWebServer:\n```kotlin\n// فحص تطابق الـ JSON المستلم مع الـ DTO لمنع انهيار Serialization\n@Test fun testApiContract() = runTest {\n    server.enqueue(MockResponse().setBody(\"\"\"{\"id\":\"1\",\"email\":\"a@b.com\",\"isVerified\":true}\"\"\"))\n    val user = api.getUser(\"1\")\n    assertEquals(\"a@b.com\", user.email)\n}\n```",
        "trade_offs_ar": "اختبارات الـ Contract تتطلب تنسيقاً مستمراً بين فرق الموبايل والـ Backend واستخدام Pact Broker، لكنها تحمي التطبيق من أخطاء الـ API القاتلة بدون الحاجة لتشغيل اختبارات E2E بطيئة ومكلفة.",
        "failure_modes_ar": "قلب الهرم لكعكة آيس كريم (Ice Cream Cone Anti-pattern) بالاعتماد على اختبارات الـ UI والمحاكي بنسبة 80%، مما يجعل خط البناء يستغرق 3 ساعات ويعاني من اختبارات متذبذبة.",
        "production_perspective_ar": "في المشروعات الكبيرة، نلزم المطورين بنسبة 70/20/10 لهرم الاختبارات، ونفعل فحص عقود الـ API عبر Pact في الـ CI لرفض دمج أي PR في الـ Backend يغير شكل الـ JSON المتوقع.",
        "how_to_answer_ar": "اشرح هرم الاختبارات الكلاسيكي بنسبه الثلاثة (70-80% Unit، و 15-20% Integration، و 5-10% E2E)، وحذر من نمط الآيس كريم المقلوب، ثم بين موقع Contract Tests عند حدود التكامل بين الموبايل والسيرفر، واشرح كيف تمنع كراشات الـ Serialization باستخدام أدوات زي Pact.",
        "talking_points_ar": "توزيع نسب هرم الاختبارات، ومخاطر الـ Ice Cream Cone، واختبارات العقود (Contract Testing) بـ Pact، وحماية الـ Serialization من أخطاء الـ Backend، والـ Pact Broker في الـ CI.",
        "follow_ups_ar": "- **المحاور:** \"ما هي مشكلة الـ Ice Cream Cone Anti-pattern في مشاريع أندرويد؟\"\n  **المرشح:** \"إن الفرق تعتمد على اختبارات الـ UI والـ E2E بنسبة 80% وتهمل الـ Unit Tests؛ وده بيخلي الـ CI ياخد ساعات طويلة ويفشل عشوائياً بسبب بطء المحاكيات ومشاكل الشبكة.\"\n\n- **المحاور:** \"كيف تمنع اختبارات الـ Contract كراش `MissingFieldException` في الإنتاج؟\"\n  **المرشح:** \"عبر فحص الـ Schema بين الفريقين بـ Pact؛ السيرفر مش بيقدر يعمل دمج للـ PR بتاعه إلا لما يثبت إن الـ Endpoints بتطلع نفس الـ JSON اللي كوتلن مستنياه بالضبط.\"",
        "self_check_ar": "هل شرحت طبقات هرم الاختبارات ونسبها بدقة؟ هل بينت موقع ووظيفة Contract Tests؟ وهل وضحت آلية عمل Pact والـ Schema verification؟",
        "references_ar": f"- [Martin Fowler: The Practical Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html) — الدليل المعماري الكلاسيكي لمارتن فاولر حول هرم الاختبارات.\n- [Pact Foundation: Consumer-Driven Contracts](https://docs.pact.io/) — التوثيق الرسمي لاختبارات العقود بين تطبيقات الموبايل والميكروسيرفيسز.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "هرم الاختبارات (Test Pyramid) هو المخطط المعماري اللي بيحدد التوزيع المثالي لاختبارات التطبيق لتحقيق أقصى جودة بأقل تكلفة وزمن. بيتكون من قاعدة عريضة من اختبارات الوحدة (Unit Tests) بنسبة 70% إلى 80% لسرعتها الفائقة على الـ JVM، تليها طبقة متوسطة من اختبارات التكامل (Integration Tests) بنسبة 15% إلى 20%، وقمة ضيقة من اختبارات الـ UI والـ E2E بنسبة 5% إلى 10%. اختبارات العقود (Contract Tests) بتقع في طبقة التكامل بين تطبيق الموبايل وسيرفرات الـ Backend؛ وظيفتها التأكد من تطابق شكل الـ JSON والبيانات مع توقعات كوتلن لمنع انهيار التطبيق بدون الحاجة لتشغيل محاكيات بطيئة.",
        "best_answer_ar": "هرم الاختبارات هو صمام الأمان اللي بيحمي فرق هندسة أندرويد من استنزاف الوقت في صيانة اختبارات بطيئة وهشة.\n\nالهرم بيقسم الاختبارات لتلات مستويات أساسية:\nقاعدة الهرم: اختبارات الـ Unit Tests بنسبة 70% إلى 80%؛ دي بتشتغل على الـ JVM المحلي في ثوانٍ معدودة بدون نظام أندرويد، وظيفتها فحص قواعد الأعمال والـ ViewModels والعمليات الرياضية.\n\nوسط الهرم: اختبارات الـ Integration بنسبة 15% إلى 20%؛ دي بتفحص تواصل المكونات مع بعضها، زي الـ Repository مع داتابيز Room أو مع سيرفر وهمي MockWebServer.\n\nقمة الهرم: اختبارات الـ UI والـ E2E بنسبة 5% إلى 10%؛ دي بتختبر الشاشات الحقيقية وتدفق الدفع والتسجيل على أجهزة أو محاكيات حقيقية.\n\nأكبر خطأ بنشوفه هو قلب الهرم لما يسمى 'مخروط الآيس كريم' (Ice Cream Cone)، بحيث تلاقي الفريق كاتب 200 اختبار UI وبطيء ومستهتر بالـ Unit Tests، فالـ CI ياخد 3 ساعات ويفشل عشوائياً!\n\nوهنا بتبرز أهمية اختبارات العقود (Contract Testing)؛ دي بتقع بالضبط عند نقطة التكامل بين الموبايل والـ Backend. بنستخدم أدوات زي Pact عشان نعمل عقد متفق عليه مسبقاً لشكل الـ JSON وأنواع الحقول. الـ Backend مبيقدرش يدمج كوده إلا لو الـ CI أثبت إنه ملتزم بنفس العقد، وده بيمنع تماماً كراشات `SerializationException` بدون الحاجة لتشغيل بيئة E2E مكلفة.",
        "deep_answer_ar": "تحت الكابوت، هرم الاختبارات واختبارات العقود بيعالجوا المعادلة الاقتصادية لجودة البرمجيات: تكلفة زمن التنفيذ، واحتمالية تذبذب الاختبارات (Flakiness Rate).\n\nفي المشاريع التي تعاني من الـ Ice Cream Cone، كل اختبار E2E بيمر عبر شبكة محلية، واتصال بالإنترنت، وخدمات أندرويد، ومحاكي، وسيرفر Staging. نظرية الاحتمالات بتقول إن لو عندك 100 اختبار وكل خطوة نجاحها 99%، احتمال نجاح خط البناء بالكامل بينخفض لأقل من 36%، وده بيفسر ليه اختبارات الـ E2E بتفشل عشوائياً بدون وجود خطأ حقيقي في الكود!\n\nاختبارات العقود بتلغي الفوضى دي تماماً من خلال مبدأ الـ Consumer-Driven Contracts.\nفريق الموبايل بيولد ملف العقد بصيغة JSON بيحدد فيه الـ Endpoints المتوقعة، والترويسات، وحقول الـ JSON مع قيود `kotlinx.serialization` الصارمة. في خط الـ CI بتاع الموبايل، بنشغل MockWebServer بيقرأ نفس ملف العقد ويتحقق إن دوال الـ DTO بتعمل Parse سليم O(1) على الـ JVM بدون فتح محاكي.\n\nوفي نفس الوقت، سيرفر الـ Backend بينزل نفس ملف العقد من وسيط اسمه `Pact Broker`؛ والـ CI بتاع الـ Backend بيشغل Provider Verification Test ضد الـ Endpoints الحقيقية للتأكد إن السيرفر مبيطلعش حقول ناقصة أو أنواع مختلفة.\nلو مهندس الباك إند غير حقل إجباري وخلّاه Nullable، التيست عنده هيفشل فوراً في الـ Pull Request بتاعه قبل ما الكود يوصل للموبايل.\nده بيحقق أعلى درجات الأمان المعماري والتوافق بين الفرق الكبيرة بدون تضييع دقيقة واحدة على المحاكيات."
    }
}

# ==========================================
# TST-08: How do you unit-test ViewModels, UseCases, and Repositories?
# ==========================================
DATA["TST-08"] = {
    "concept_en": """Unit testing ViewModels, UseCases, and Repositories on the host JVM requires a layered isolation strategy that replaces heavy Android framework dependencies with test doubles, swaps the Android main thread dispatcher with a virtual TestDispatcher, and verifies reactive asynchronous streams using Turbine. UseCases are tested in pure isolation against fake or mocked repositories to assert domain business rules and edge conditions. Repositories are tested by coordinating fake network data sources and in-memory caches, validating offline-first policies, DTO mapping, and exception wrapping. ViewModels are tested using a custom JUnit TestRule (MainDispatcherRule) that replaces Dispatchers.Main with StandardTestDispatcher or UnconfinedTestDispatcher, capturing state emissions from StateFlow and SharedFlow to assert deterministic UI state transitions.""",
    "walkthrough_en": """Testing UseCases, Repositories, and ViewModels using MainDispatcherRule and Turbine:
```kotlin
// 1. Reusable JUnit Rule to replace Dispatchers.Main on JVM
class MainDispatcherRule(
    val testDispatcher: TestDispatcher = StandardTestDispatcher()
) : TestWatcher() {
    override fun starting(description: Description) = Dispatchers.setMain(testDispatcher)
    override fun finished(description: Description) = Dispatchers.resetMain()
}

// 2. Unit Testing ViewModel using MainDispatcherRule and Turbine
class UserProfileViewModelTest {
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private val getUserUseCase = mockk<GetUserUseCase>()
    private lateinit var viewModel: UserProfileViewModel

    @Before
    fun setup() {
        viewModel = UserProfileViewModel(getUserUseCase)
    }

    @Test
    fun loadUser_emitsLoadingThenSuccess_usingTurbine() = runTest {
        val user = User(id = "1", name = "Mohamed")
        coEvery { getUserUseCase("1") } returns Result.success(user)

        viewModel.uiState.test {
            // Initial state
            assertEquals(ProfileUiState.Idle, awaitItem())

            viewModel.loadProfile("1")

            // Intermediate Loading state
            assertEquals(ProfileUiState.Loading, awaitItem())

            // Final Success state
            assertEquals(ProfileUiState.Success(user), awaitItem())
        }
    }
}
```""",
    "short_en": """We unit-test clean architecture layers in isolation on the JVM. UseCases are tested against fake repositories to verify business logic. Repositories are tested by mocking network and local sources to verify caching and error handling. ViewModels are tested by applying a MainDispatcherRule that replaces Dispatchers.Main with a TestDispatcher, using Turbine to collect and assert StateFlow emissions sequentially across loading, error, and success states.""",
    "structured_en": """Architecting robust unit tests across ViewModels, UseCases, and Repositories requires distinct testing strategies tailored to each architectural boundary.
At the domain layer, UseCases are the easiest to test because they contain zero Android framework dependencies.
We test them purely on the JVM, passing in fake or mocked repositories to verify business validation rules, authorization logic, and domain transformations across success and error permutations.
At the data layer, Repositories coordinate remote network datasources and local databases.
We test repositories by injecting mock network APIs and in-memory Room DAOs, asserting that the repository implements correct offline-first synchronization, handles network timeouts gracefully, maps raw DTOs into immutable domain entities, and catches low-level exceptions.
At the presentation layer, testing ViewModels introduces two unique concurrency challenges: Dispatchers.Main and reactive StateFlow emission streams.
Because the Android platform Main Looper does not exist on the desktop JVM, any call to Dispatchers.Main immediately crashes with an initialization exception.
To resolve this, we apply a reusable JUnit TestWatcher rule—MainDispatcherRule—that invokes Dispatchers.setMain(testDispatcher) before every test and resets it afterward.
We then employ the Turbine library to open a test collector on the ViewModel's uiState StateFlow, sequentially asserting that user intent triggers an immediate Loading state followed deterministically by a Success or Error state.""",
    "deep_senior_en": """Under the hood, unit testing Clean Architecture layers on the JVM hinges on replacing platform dispatchers and handling hot coroutine stream lifecycles.
When testing ViewModels, viewModelScope defaults internally to Dispatchers.Main.immediate.
On the JVM, the kotlinx-coroutines-android artifact attempts to resolve the Main dispatcher via ServiceLoader, which queries Android's native android.os.Looper.
Because Looper.getMainLooper() returns null outside the Android ART runtime, attempting to launch a coroutine throws IllegalStateException('Module with the Main dispatcher had failed to initialize').
MainDispatcherRule bypasses this framework check by directly invoking Dispatchers.setMain(testDispatcher), injecting a virtualized TestDispatcher into the coroutine runtime's internal dispatcher registry.
When testing StateFlow emissions, standard collection via launch { viewModel.uiState.collect { ... } } is prone to deadlocks and race conditions because StateFlow is a hot, conflated stream that never completes naturally.
Turbine overcomes this by hooking into the StateFlow collector via a FlowTurbine channel.
Every time the ViewModel updates its state using _uiState.update { ... }, Turbine enqueues the state emission into an internal rendezvous channel.
When the test invokes awaitItem(), Turbine suspends until the next emission arrives or immediately pops the item if already enqueued, failing the test with a descriptive error if unexpected emissions occur or if the stream throws an unhandled exception.
Senior engineers combine MainDispatcherRule and Turbine to achieve 100% deterministic assertion coverage over complex reactive UI flows without a single flaky millisecond.""",
    "meta_ar": {
        "id": "TST-08",
        "questionAr": "كيف تقوم باختبار الـ ViewModels والـ UseCases والـ Repositories باحترافية وبشكل منعزل على الـ JVM؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على عزل واختبار طبقات المعمارية النظيفة (Clean Architecture)، واستخدام `MainDispatcherRule` لاستبدال `Dispatchers.Main` على الـ JVM، واستخدام مكتبة `Turbine` لاختبار تدفقات الـ StateFlow.",
        "why_it_matters_ar": "محاولة اختبار الـ ViewModel على الـ JVM بدون استبدال الـ Main Dispatcher تسبب انهيار فوري بـ IllegalStateException، واختبار الـ StateFlow بدون Turbine يسبب تعليق الاختبار أو سقوط تحديثات الحالة.",
        "worked_example_ar": "اختبار طبقات التطبيق واستخدام MainDispatcherRule مع Turbine:\n```kotlin\n@Test fun testViewModelState() = runTest {\n    // اختبار تسلسل الحالات: Idle ثم Loading ثم Success\n    viewModel.uiState.test {\n        assertEquals(UiState.Idle, awaitItem())\n        viewModel.fetchData()\n        assertEquals(UiState.Loading, awaitItem())\n        assertEquals(UiState.Success(\"Data\"), awaitItem())\n    }\n}\n```",
        "trade_offs_ar": "استخدام مكتبة Turbine و MainDispatcherRule يضيف تبعيات إضافية للاختبارات، لكنه الحل القياسي الحصري لاختبار تدفقات الكوروتينات والـ StateFlow بدقة متناهية وبدون أي Flakiness.",
        "failure_modes_ar": "نسيان عمل `Dispatchers.resetMain()` بعد انتهاء الاختبار، مما يلوث بيئة الاختبار لباقي الكلاسات ويسبب أخطاء غريبة يصعب تتبعها في الـ CI.",
        "production_perspective_ar": "في المشروعات الكبيرة، ننشئ قاعدة `MainDispatcherRule` مركزية في موديول الاختبار المشترك ونلزم استخدام Turbine لفحص كل حالات شاشات الـ MVI و MVVM.",
        "how_to_answer_ar": "قسم الإجابة لثلاث طبقات: أولاً UseCases واختبار منطق الأعمال الصافي بـ Fake Repositories، ثانياً Repositories واختبار دمج الشبكة والداتابيز بـ MockWebServer و In-memory Room، ثالثاً ViewModels وشرح تحدي `Dispatchers.Main` وحله بـ `MainDispatcherRule`، وشرح فحص الـ StateFlow باستخدام مكتبة `Turbine` عبر `awaitItem()`.",
        "talking_points_ar": "اختبار الـ UseCases ككود نقي، واختبار الـ Repository وإدارة الكاش والـ DTO mapping، وانهيار Dispatchers.Main على JVM وحله بـ MainDispatcherRule، ومكتبة Turbine لاختبار StateFlow.",
        "follow_ups_ar": "- **المحاور:** \"لماذا يرمي الـ ViewModel خطأ `IllegalStateException` فوراً عند اختباره على الـ JVM بدون Rules؟\"\n  **المرشح:** \"لأن `viewModelScope` بيستخدم `Dispatchers.Main` افتراضياً، وعلى الـ JVM مفيش أندرويد Main Looper، فالمحرك بيفشل. الحل هو عمل `Dispatchers.setMain(testDispatcher)` قبل بدء الفحص.\"\n\n- **المحاور:** \"ما هي ميزة استخدام مكتبة Turbine مقارنة بـ `toList()` أو جمع الـ Flow يدوياً؟\"\n  **المرشح:** \"الـ StateFlow هو Hot Flow لا نهائي، فلو عملت `toList()` الاختبار هيعلق للأبد (Deadlock). Turbine بتعمل قناة مؤقتة وبتسمح لنا بفحص كل حالة بتوصل خطوة بخطوة بـ `awaitItem()` وبدون أي تعليق.\"",
        "self_check_ar": "هل غطيت الطبقات الثلاثة بالتفصيل؟ هل شرحت آلية عمل MainDispatcherRule؟ وهل بينت كيفية استخدام Turbine مع StateFlow؟",
        "references_ar": f"- [Testing ViewModels](https://developer.android.com/topic/libraries/architecture/viewmodel/viewmodel-testing) — دليل جوجل الرسمي لاختبار الـ ViewModels.\n- [CashApp Turbine Library](https://github.com/cashapp/turbine) — التوثيق الرسمي لمكتبة Turbine لاختبار تدفقات الـ Flow.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "بنختبر الطبقات التلاتة بمعزل تام وسرعة خارقة على الـ JVM باتباع استراتيجية معمارية منظمة: أولاً الـ `UseCases` بنختبرها ككود كوتلن نقي ضد Fake Repositories لفحص منطق الأعمال والتحويلات بدون أي محاكيات. ثانياً الـ `Repositories` بنختبرها بحقن Mock WebServer و In-memory Room لفحص سياسات الكاش والتعامل مع أخطاء الشبكة. ثالثاً الـ `ViewModels` بنختبرها باستخدام قاعدة `MainDispatcherRule` اللي بتستبدل `Dispatchers.Main` بـ `TestDispatcher` لمنع كراشات الـ Looper، وبنستخدم مكتبة `Turbine` للتحقق من تدفق الحالات في الـ `StateFlow` خطوة بخطوة (Loading ثم Success).",
        "best_answer_ar": "اختبار طبقات الـ Clean Architecture على الـ JVM هو المعيار الذهبي لسرعة وموثوقية تطبيقات أندرويد في الشركات الكبرى.\n\nالاستراتيجية الاحترافية بتتعامل مع كل طبقة حسب طبيعتها:\nالطبقة الأولى: الـ UseCases؛ دي أسهل وأسرع طبقة في الاختبار؛ لأنها كود كوتلن نقي وخالي تماماً من أي تبعيات لأندرويد. بنمرر لها Fake Repository في الـ Constructor، ونعمل Assert على صحة العمليات الحسابية والتحقق من الشروط وحالات الخطأ في بضعة أجزاء من الميلي ثانية.\n\nالطبقة الثانية: الـ Repositories؛ هنا بنختبر التنسيق بين مصادر البيانات؛ بنحقن كائن API وهمي (بـ MockK أو MockWebServer) وداتابيز محلية بـ Room، وبنتأكد إن الـ Repository بينفذ سياسة Offline-first صح، وإنه بيحول الـ DTOs لـ Domain Models ويلف أخطاء الشبكة في Result كائن آمن.\n\nالطبقة الثالثة: الـ ViewModels؛ دي الطبقة اللي بتواجه تحديين كبار:\nالتحدي الأول هو `Dispatchers.Main`؛ لأن `viewModelScope` بيعتمد عليه، والـ Main Looper مش موجود على الديسك توب. بنحل ده فوراً بإنشاء `MainDispatcherRule` بتعمل `Dispatchers.setMain(testDispatcher)` قبل التيست وتعمل Reset بعده.\nالتحدي الثاني هو اختبار الـ `StateFlow`؛ لأنه تدفق ساخن لا نهائي، مينفعش نعمله collect عادي وإلا التيست هيعلق للأبد (Deadlock). بنستخدم مكتبة `Turbine`؛ بنفتح بلوك `viewModel.uiState.test { ... }` ونستقبل الحالات بالترتيب بـ `awaitItem()`: نتأكد الأول إن اللودر اشتغل (Loading)، وبعدين البيانات نزلت بنجاح (Success)، وده بيوفر تغطية اختبارية كاملة في ثوانٍ معدودة.",
        "deep_answer_ar": "تحت الكابوت، اختبار طبقات العمارة النظيفة على الـ JVM بيتعامل مع معضلة الـ Threading ونظام المراقبة للـ Hot Streams.\n\nفي الـ ViewModel، دالة `viewModelScope` بتشير داخلياً إلى `Dispatchers.Main.immediate`. مكتبة `kotlinx-coroutines-android` لما بتشتغل على الـ JVM، بتستخدم `ServiceLoader` للبحث عن الـ Main Dispatcher، فبتحاول تستدعي كلاس `Looper.getMainLooper()` الأصلي في أندرويد. ولأننا شغالين على كمبيوتر مكتبي عادي، الاستدعاء ده بيرجع `null`، فالمحرك بيرمي `IllegalStateException('Module with the Main dispatcher had failed to initialize')` وبيفشل التيست فوراً قبل ما يبدأ.\nقاعدة `MainDispatcherRule` بتعالج ده على مستوى مكتبة الكوروتينات نفسها عبر `Dispatchers.setMain(testDispatcher)`؛ فبتستبدل المرجع الداخلي بـ `TestDispatcher` افتراضي.\n\nأما بخصوص الـ `StateFlow`، فهو بيختلف عن الـ Cold Flow العادي بأنه Conflated ولا يغلق أبداً؛ يعني بيفضل باعت آخر قيمة ومستني مستمعين جدد. لو كتبت `launch { viewModel.uiState.collect() }`، التيست هيدخل في حالة تعليق كامل (Hanging).\nمكتبة Turbine بتحل المشكلة دي عن طريق فتح قناة داخلية (Rendezvous Channel) بترتبط بالـ Flow.\nأول ما الـ ViewModel ينادي `_uiState.update { ... }`، محرك Turbine بيلتقط القيمة الجديدة فوراً ويحطها في القناة. ولما التيست ينادي `awaitItem()`، بيحصل استهلاك فوري للقيمة في خطوة O(1) متزامنة، ولو وصل State غير متوقع أو حصل كراش غير معالج، Turbine بترمي تقرير مفصل بيكشف الفرق الدقيق بين الحالة المتوقعة والحالة المستلمة، وده بيقضي تماماً على تذبذب الاختبارات في الـ CI."
    }
}

def main():
    print("Elevating 8 questions in TST (TST-01 to TST-08)...")
    all_valid = True
    for qid, d in sorted(DATA.items()):
        if d is None:
            continue
        en_s = len(d["short_en"].split())
        en_st = len(d["structured_en"].split())
        en_d = len(d["deep_senior_en"].split())
        ar_q = len(d["meta_ar"]["quick_answer_ar"].split())
        ar_b = len(d["meta_ar"]["best_answer_ar"].split())
        ar_d = len(d["meta_ar"]["deep_answer_ar"].split())
        print(f"{qid}: en_s={en_s}, en_st={en_st}, en_d={en_d} | ar_q={ar_q}, ar_b={ar_b}, ar_d={ar_d}")

        if not (35 <= en_s <= 110):
            print(f"  ❌ {qid} en_short invalid: {en_s}")
            all_valid = False
        if not (100 <= en_st <= 280):
            print(f"  ❌ {qid} en_structured invalid: {en_st}")
            all_valid = False
        if not (200 <= en_d <= 650):
            print(f"  ❌ {qid} en_deep invalid: {en_d}")
            all_valid = False
        if not (35 <= ar_q <= 110):
            print(f"  ❌ {qid} ar_quick invalid: {ar_q}")
            all_valid = False
        if not (90 <= ar_b <= 280):
            print(f"  ❌ {qid} ar_best invalid: {ar_b}")
            all_valid = False
        if not (180 <= ar_d <= 650):
            print(f"  ❌ {qid} ar_deep invalid: {ar_d}")
            all_valid = False

    if not all_valid:
        print("\nPre-validation word count checks failed! Fix counts before updating files.")
        sys.exit(1)

    print("\nPre-validation word count checks passed! Updating canonical questions...")

    topic_meta = {}
    for qid, d in sorted(DATA.items()):
        if d is None:
            continue
        ee.update_canonical_question(
            qid=qid,
            concept_en=d["concept_en"],
            walkthrough_en=d["walkthrough_en"],
            short_en=d["short_en"],
            structured_en=d["structured_en"],
            deep_senior_en=d["deep_senior_en"]
        )
        topic_meta[qid] = d["meta_ar"]

    ee.save_topic_metadata("tst_01_08", topic_meta)
    ee.merge_all_metadata()

    # Validate each question
    for qid in sorted(DATA.keys()):
        if DATA[qid] is None:
            continue
        ee.validate_question(qid)

    print("\nAll 8 TST questions (TST-01 to TST-08) successfully elevated and passed validation!")

if __name__ == "__main__":
    main()
