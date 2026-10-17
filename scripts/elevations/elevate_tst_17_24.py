#!/usr/bin/env python3
"""
Elevation script for TST questions: TST-17 to TST-24.
Topic: Testing, Quality & Reliability (TST)
Phase 4, Batch 3
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", "Volumes", "M&M", "Android", "InterView", "untitled folder", "android quation", "scripts", "elevations"))
# Also add relative to the target destination
sys.path.insert(0, os.path.abspath("scripts/elevations"))
import elevation_engine as ee

TOPIC_AR = "اختبار البرمجيات والجودة والموثوقية"
REVIEWED_DATE_AR = "تمت المراجعة والتحقق في 17 أكتوبر 2026"

DATA = {}

# ==========================================
# TST-17: What are screenshot tests, Baseline Profiles, and Macrobenchmark tests?
# ==========================================
DATA["TST-17"] = {
    "concept_en": """Screenshot tests, Baseline Profiles, and Macrobenchmark tests represent three distinct advanced quality and performance disciplines in modern Android engineering. Screenshot testing (using frameworks such as Roborazzi, Paparazzi, or Shot) captures visual renderings of UI components or full screens and compares them pixel-by-pixel against versioned golden master images, detecting unintended visual regressions, typography clipping, and layout shifts. Baseline Profiles are human-readable ART compilation rules bundled into the APK that instruct Android's Ahead-Of-Time (AOT) and Profile-Guided Optimization (PGO) compiler to pre-compile critical execution paths—such as app startup, authentication, and core list scrolling—during app installation, slashing cold startup times by 30-40% and eliminating initial JIT compilation jank. Macrobenchmark tests execute black-box performance measurements on physical production-like devices without mocking, quantifying real-world frame timing, UI stutter, and cold, warm, or hot startup durations in release builds.""",
    "walkthrough_en": """Implementing screenshot tests, Baseline Profile generation, and Macrobenchmark measurements:
```kotlin
// 1. Screenshot testing a Compose component with Roborazzi
@RunWith(AndroidJUnit4::class)
@GraphicsMode(GraphicsMode.Mode.NATIVE)
class PaymentCardScreenshotTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun paymentCard_verifiedState_matchesGoldenImage() {
        composeTestRule.setContent {
            PaymentCard(
                accountNumber = "**** 4242",
                isVerified = true,
                status = CardStatus.ACTIVE
            )
        }

        // Captures screenshot and validates against golden image in source control
        composeTestRule.onRoot().captureRoboImage("golden_payment_card_verified.png")
    }
}

// 2. Baseline Profile generator for app startup and list scrolling
@RunWith(AndroidJUnit4::class)
class AppStartupBaselineProfileGenerator {
    @get:Rule
    val baselineRule = BaselineProfileRule()

    @Test
    fun generateAppStartupProfile() = baselineRule.collect(
        packageName = "com.example.banking",
        profileBlock = {
            // Cold start the application
            pressHome()
            startActivityAndWait()

            // Scroll the main transaction feed to capture JIT hotspots
            val feed = device.findObject(By.res("transaction_list"))
            feed.fling(Direction.DOWN)
            device.waitForIdle()
        }
    )
}

// 3. Macrobenchmark measuring cold startup timing with Baseline Profiles enforced
@RunWith(AndroidJUnit4::class)
class StartupMacrobenchmarkTest {
    @get:Rule
    val benchmarkRule = MacrobenchmarkRule()

    @Test
    fun measureColdStartupWithBaselineProfile() = benchmarkRule.measureRepeated(
        packageName = "com.example.banking",
        metrics = listOf(StartupTimingMetric(), FrameTimingMetric()),
        compilationMode = CompilationMode.Partial(
            baselineProfileMode = BaselineProfileMode.Require
        ),
        iterations = 10,
        startupMode = StartupMode.COLD
    ) {
        pressHome()
        startActivityAndWait()
    }
}
```""",
    "short_en": """We use screenshot tests to capture UI components and assert pixel-perfect parity against golden images, catching unintended visual shifts. Baseline Profiles generate ART compilation rules that pre-compile critical user flows during installation, eliminating JIT jank and boosting startup by up to 40%. Macrobenchmark tests run on physical devices in release mode to measure real black-box frame timing and cold startup latency, guaranteeing production performance.""",
    "structured_en": """Modern Android engineering relies on three specialized testing pillars to safeguard user experience, visual fidelity, and runtime performance.
Screenshot testing operates at the UI presentation layer.
Using tools like Roborazzi or Paparazzi, screenshot tests render composables in isolated JVM or instrumentation environments, comparing the resulting bitmap against reference golden files stored in git.
This catches regressions in font scaling, dark mode, RTL layouts, and unexpected padding adjustments that semantic assertions miss.
Baseline Profiles address Android's runtime compilation bottleneck.
Because Android's ART uses a hybrid of JIT and AOT compilation, unprofiled apps suffer from frame drops during initial user interactions while code interprets.
A Baseline Profile generator records which DEX methods and classes are executed during app launch and list scrolling, packaging these rules into the APK so the OS pre-compiles them upon installation.
Macrobenchmark tests provide rigorous empirical validation of this performance.
Running on physical devices with release minification enabled, Macrobenchmark repeatedly boots the application, measuring StartupTimingMetric and FrameTimingMetric under realistic thermal conditions.
Senior engineers combine these three disciplines to maintain flawless UI designs alongside peak runtime speed.""",
    "deep_senior_en": """Under the hood, these three specialized testing tools interact directly with Android's OS rendering pipeline, Ahead-of-Time compilation architecture, and Linux kernel tracing subsystems.
Screenshot testing via Roborazzi leverages Robolectric's native graphics engine (Skia) to rasterize Compose draw commands directly into PNG byte arrays on the desktop host, eliminating physical emulator overhead while achieving 100% deterministic pixel-perfect validation across theme variations.
Baseline Profiles manipulate ART's Profile-Guided Optimization (PGO) pipeline.
When the generator executes, it instruments the ART runtime via adb commands, dumping raw profman profile files containing method indexes and class descriptors into an assets directory.
When Google Play delivers the APK, the device installer invokes dex2oat to pre-compile these profiled methods directly into native ELF binary machine instructions (OAT files), bypassing the JIT interpreter completely during the critical first cold launch.
Macrobenchmark operates via the Jetpack Benchmark library using Android OS Perfetto tracing and simpleperf profiler hooks under the hood.
To produce reliable metrics, it enforces strict device requirements: disabling CPU thermal throttling when possible, requiring a non-debuggable release build, and executing kill-and-restart cycles to flush Android OS page caches.
By comparing CompilationMode.None against CompilationMode.Partial(BaselineProfileMode.Require), engineering teams quantify the exact millisecond startup reduction and jank-free frame percentile directly in continuous integration reporting.""",
    "meta_ar": {
        "id": "TST-17",
        "questionAr": "ما هي اختبارات لقطات الشاشة (Screenshot Tests) وملفات Baseline Profiles واختبارات Macrobenchmark؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على التمييز الدقيق بين اختبارات لقطات الشاشة (Screenshot Testing) وملفات تحسين الأداء (Baseline Profiles) واختبارات قياس الأداء الشاملة (Macrobenchmark)، وفهم آليات عمل ART و AOT والتحقق من تجربة المستخدم في الإنتاج.",
        "why_it_matters_ar": "الاختبارات التقليدية تفحص منطق الشاشة فقط ولا تكتشف تشوهات التصميم البصرية، وبدون Baseline Profiles يعاني المستخدم من تهنيج وبطء في أول فتحة للتطبيق، وتساعد هذه الأدوات في ضمان مظهر مثالي وأداء فائق السرعة.",
        "worked_example_ar": "أمثلة عملية لاختبار الشاشات وملفات Baseline Profile و Macrobenchmark:\n```kotlin\n// 1. اختبار لقطة شاشة بـ Roborazzi\ncomposeRule.setContent { PaymentCard(isVerified = true) }\ncomposeRule.onRoot().captureRoboImage(\"golden_card.png\")\n// 2. توليد Baseline Profile للإقلاع\nbaselineRule.collect(\"com.example.app\") { startActivityAndWait() }\n// 3. قياس سرعة الإقلاع بـ Macrobenchmark\nbenchmarkRule.measureRepeated(\"com.example.app\", listOf(StartupTimingMetric())) { startActivityAndWait() }\n```",
        "trade_offs_ar": "اختبارات Screenshot تتطلب صيانة وتحديث الـ Golden Images مع كل تعديل في التصميم، واختبارات Macrobenchmark تتطلب أجهزة فيزيائية حقيقية غير مقيدة بالـ Emulators، لكنها تمنح الثقة الكاملة في المظهر والأداء قبل إطلاق التطبيق.",
        "failure_modes_ar": "تشغيل Macrobenchmark على بيئة Debuggable أو على محاكي بطيء؛ مما يفسد نتائج القياس ويعطي أرقاماً مضللة لا تعكس تجربة المستخدم الحقيقي في وضع الإنتاج.",
        "production_perspective_ar": "في التطبيقات العالمية، نعتمد Roborazzi في الـ CI للتحقق من سلامة الواجهات بـ 500+ لقطة شاشة في دقائق، ونولد Baseline Profiles مع كل إصدار رسمي لتقليل وقت فتح التطبيق بنسبة تتجاوز 35%.",
        "how_to_answer_ar": "قسم الإجابة بوضوح لثلاثة محاور هندسية: أولاً اختبارات لقطات الشاشة (Screenshot Tests) كأداة لمقارنة بكسلات الواجهة بالصورة المرجعية لمنع تشوهات التصميم، ثانياً ملفات Baseline Profiles كقواعد توجيهية لمحرك ART لترجمة كود البداية والتمرير إلى Native Machine Code وقت التثبيت لإنهاء التهنيج، وثالثاً اختبارات Macrobenchmark كأداة قياس واقعية على أجهزة حقيقية لفحص سرعة فتح التطبيق واستقرار الإطارات.",
        "talking_points_ar": "مقارنة البكسلات في Screenshot Tests ومكتبات Roborazzi و Paparazzi، وتجميع ART ومفهوم AOT و JIT في Baseline Profiles، وقياس الإقلاع بـ Macrobenchmark Rule و StartupTimingMetric، وشروط بيئة الفحص بدون Debugger.",
        "follow_ups_ar": "- **المحاور:** \"كيف تمنع تذبذب اختبارات لقطات الشاشة بين أجهزة المطورين وخوادم الـ CI؟\"\n  **المرشح:** \"باستخدام مكتبات مثل Roborazzi على الـ JVM مع تفعيل محرك Skia الموحد، وتثبيت خطوط العرض والـ Font Scaling واللغة، ومقارنة الصور بنسبة تسامح طفيفة في درجات الألوان.\"\n\n- **المحاور:** \"ما الفارق بين Microbenchmark و Macrobenchmark؟\"\n  **المرشح:** \"Microbenchmark يقيس دالة برمجية محددة أو خوارزمية في الـ CPU في معزل عن النظام، بينما Macrobenchmark يفتح التطبيق بالكامل من الخارج كـ Black Box ويقيس سرعة الإقلاع وتمرير القوائم على جهاز حقيقي.\"",
        "self_check_ar": "هل فرقت بدقة بين الأدوات الثلاث؟ هل شرحت آلية عمل Baseline Profiles مع ART؟ وهل وضحت شروط تشغيل Macrobenchmark؟",
        "references_ar": f"- [Android Baseline Profiles Overview](https://developer.android.com/topic/performance/baselineprofiles/overview) — التوثيق الرسمي لجوجل حول Baseline Profiles وتحسين الأداء.\n- [Jetpack Macrobenchmark Guide](https://developer.android.com/topic/performance/benchmarking/macrobenchmark-overview) — دليل اختبارات قياس الأداء الشاملة.\n- [Roborazzi](https://github.com/takahirom/roborazzi) — توثيق مكتبة Roborazzi لاختبار لقطات الشاشة.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "الأدوات التلاتة بيمثلوا منظومة الجودة والأداء المتقدمة في أندرويد: اختبارات لقطات الشاشة (Screenshot Testing) بتلتقط صورة للواجهة وتقارنها ببكسلات الصورة المرجعية في السورس كنترول لمنع أي تشوه بصري في التصميم. وملفات Baseline Profiles هي قواعد بتحدد المسارات الحرجة في التطبيق عشان محرك ART يترجمها مسبقاً لكود آلة أصلي (AOT) وقت التثبيت، فبتقلل وقت فتح التطبيق بنسبة تصل لـ 40% وتمنع التهنيج. أما اختبارات Macrobenchmark فهي اختبارات بتشتغل على أجهزة حقيقية في وضع الـ Release لقياس سرعة فتح التطبيق الفعلية واستقرار الفريمات بدون أي Mocking.",
        "best_answer_ar": "المهندس السينيور بيعتمد على التلات أدوات دول لضمان الجودة البصرية والأداء العالي للتطبيق قبل وصوله للمستخدمين.\n\nالأداة الأولى: اختبارات لقطات الشاشة (Screenshot Testing)؛ الاختبارات العادية بتتأكد إن الزرار موجود، لكن مبتقولكش لو النص مقصوص أو اللون باهت أو التصميم بايظ في الـ Dark Mode أو الـ RTL. بنستخدم أدوات زي Roborazzi أو Paparazzi عشان ترسم الـ Composable وتقارن بكسلاته بصورة مرجعية معتمدة، وأي تغيير غير مقصود بيفشل التيست فوراً.\n\nالأداة الثانية: ملفات Baseline Profiles؛ نظام أندرويد بيعتمد على مزيج من التفسير الفوري (JIT) والترجمة المسبقة (AOT). لما التطبيق ينزل لأول مرة بيكون الكود مش مترجم، فالمستخدم بيحس بتهنيج في أول فتحة وأول سكرول. بنولد ملفات Baseline Profile تسجل المسارات الحرجة زي الإقلاع وتصفح المنتجات، وجوجل بلاي بيبعتها مع الـ APK عشان النظام يترجمها لكود آلة وقت التنزيل.\n\nالأداة الثالثة: اختبارات Macrobenchmark؛ دي وسيلتنا العلمية للتأكد من نجاح الـ Baseline Profiles. بنشغل الاختبار على جهاز فيزيائي حقيقي مقفول فيه الـ Debugger، وبنقيس بالمللي ثانية زمن الـ Cold Start واستقرار الفريمات عبر مقاييس زي `StartupTimingMetric`، وده بيدينا ثقة مطلقة في أداء الإنتاج.",
        "deep_answer_ar": "تحت الكابوت، الأدوات التلاتة بتتعامل مباشرة مع محرك الرسم في أندرويد وطبقة الـ Ahead-of-Time Compilation ونظام تتبع النواة في لينكس.\nفي اختبارات الـ Screenshot بواسطة Roborazzi، الاختبار بيستغل محرك Skia المدمج في Robolectric لرسم أوامر كومبوز في صورة مصفوفة بكسلات PNG على الـ JVM مباشرة، وده بيوفر فحص بصري دقيق جداً في ثوانٍ وبدون استهلاك موارد المحاكي.\n\nأما Baseline Profiles فبتتحكم في مسار الـ Profile-Guided Optimization التابع لـ ART؛ أثناء تشغيل مولد البروفايل، النظام بيفعل أداة profman لتسجيل الـ Method Indexes والـ Classes المستدعاة أثناء فتح الشاشة وحفظها في صيغة ثنائية.\nوقت التثبيت من متجر التطبيقات، نظام أندرويد بينادي أمر `dex2oat` لتجميع الطرق دي بالكامل إلى تعليمات Native ELF في ملفات OAT، وبالتالي التطبيق بيتخطى مرحلة الـ JIT Interpreter تماماً في أول فتحة ويشتغل بأقصى سرعة عتادية.\n\nوفي اختبارات Macrobenchmark، المحرك بيعتمد داخلياً على Perfetto Tracing و Simpleperf داخل نواة النظام؛ وعشان القياس يكون حقيقي 100%، المكتبة بتلزم إن التطبيق يكون مبني بـ R8 Minification ومش Debuggable، وبتطفي الـ Thermal Throttling وبتفرغ الـ OS Page Cache بين المحاولات المتكررة لقياس زمن استجابة الشاشة والفريمات الساقطة بدقة متناهية في خطوط الـ CI."
    }
}

# ==========================================
# TST-18: How do you test process death, rotation, and offline transitions?
# ==========================================
DATA["TST-18"] = {
    "concept_en": """Testing process death, configuration rotation, and offline transitions requires distinguishing between three fundamentally different runtime failure vectors in Android architecture. Configuration change (such as device rotation or dark mode toggling) destroys and recreates the host Activity while preserving the ViewModelStore and all in-memory ViewModel state intact. Process death occurs when the Android operating system terminates the application's background process under system-wide RAM pressure, destroying the entire JVM instance, static variables, and ViewModelStore; upon return, the application must reconstruct its state exclusively from SavedStateHandle (for ephemeral UI state under 500KB) and durable local persistence (Room SQLite or DataStore). Offline transitions test data resilience when active network sockets fail, verifying that repositories gracefully fall back to local cached SQLite entities and expose unambiguous offline UI states without throwing unhandled exceptions.""",
    "walkthrough_en": """Testing rotation, process death restoration, and offline fallback transitions:
```kotlin
// 1. Testing configuration rotation with ActivityScenario
@Test
fun profileScreen_rotation_preservesUiState() {
    val scenario = ActivityScenario.launch(ProfileActivity::class.java)

    // Type text into input field
    onView(withId(R.id.name_input)).perform(typeText("Alex"), closeSoftKeyboard())

    // Trigger physical configuration change: recreate activity
    scenario.recreate()

    // Assert ViewModel retained state preserves the entered text
    onView(withId(R.id.name_input)).check(matches(withText("Alex")))
    scenario.close()
}

// 2. Testing process death restoration using SavedStateHandle
@Test
fun checkoutViewModel_processDeath_restoresDraftOrder() {
    // Stage initial state in SavedStateHandle
    val savedState = SavedStateHandle(mapOf("draft_order_id" to "order_9988"))
    val fakeRepo = FakeOrderRepository()

    // Instantiate ViewModel simulating fresh process resurrection
    val viewModel = CheckoutViewModel(savedStateHandle = savedState, repository = fakeRepo)

    // Assert that draft order was restored directly from saved state
    assertEquals("order_9988", viewModel.uiState.value.orderId)
    assertTrue(viewModel.uiState.value.isRestoredFromDeath)
}

// 3. Testing offline network loss fallback in Repository
@Test
fun fetchFeed_networkThrowsIOException_returnsCachedDatabaseEntities() = runTest {
    val mockApi = mockk<NewsApiService>()
    val fakeDatabase = FakeNewsDao()

    // Pre-populate local cache with verified offline entities
    fakeDatabase.insertAll(listOf(NewsEntity(id = 1, title = "Offline Cached Headline")))

    // Simulate complete network disconnection
    coEvery { mockApi.getLatestNews() } throws IOException("No route to host")

    val repository = NewsRepositoryImpl(api = mockApi, dao = fakeDatabase)
    val result = repository.getNewsStream().first()

    // Assert repository recovers gracefully by emitting cached content
    assertTrue(result.isSuccess)
    assertEquals("Offline Cached Headline", result.getOrNull()?.first()?.title)
}
```""",
    "short_en": """We test rotation by calling ActivityScenario.recreate, verifying the ViewModel retains state across the destroyed Activity. We test process death by simulating OS termination, asserting the ViewModel recovers its critical state from SavedStateHandle or Room rather than resetting to defaults. We test offline transitions by mocking network IOExceptions, verifying the repository emits cached SQLite data while the UI updates to show offline mode cleanly.""",
    "structured_en": """A robust Android application must survive three distinct real-world lifecycle interruptions: screen rotation, low-memory process termination, and sudden network loss.
Screen rotation represents a transient configuration change.
The Android operating system destroys the Activity window and inflates a new layout, but the ViewModelStoreOwner survives on the non-configuration instance registry.
We test this using ActivityScenario.recreate, asserting that user input and loaded UI models persist across the transition without restarting background network fetch calls.
Process death is a far harsher survival test.
When the user switches away from the application and Android experiences memory pressure, the Linux kernel kills the entire application process.
When the user returns, Android allocates a brand new process and launches the destination Activity from scratch.
Because the ViewModel is destroyed, state can only be restored if it was written into SavedStateHandle or persisted to Room SQLite.
We test this by passing pre-populated SavedStateHandle instances into ViewModels or using StateRestorationTester in Jetpack Compose to assert exact state restoration.
Offline transitions test resilience to physical connectivity loss.
We verify our repositories by mocking network exceptions like SocketTimeoutException or UnknownHostException, asserting that the local Room cache immediately serves stale data with an offline UI indicator.""",
    "deep_senior_en": """Under the hood, these three scenarios exercise different Android operating system contracts, kernel memory management signals, and persistence lifecycles.
Configuration change lifecycle is mediated by ActivityClientRecord and ConfigurationController within the Android framework.
When rotation occurs, the ActivityThread invokes retainNonConfigurationInstances(), stashing the ViewModelStore in memory before destroying the View decor and window.
Process death, however, triggers an operating system eviction sequence orchestrated by the ActivityManagerService and the Linux Low Memory Killer (LMK) daemon.
When an app moves to the cached background LRU state, Android serializes the Activity's onSaveInstanceState bundle into an IPC binder transaction, holding this Parcelable payload in system server memory while the app's PID is SIGKILLed.
Because the Binder transaction buffer is capped at approximately one megabyte across all active transactions, passing large data models in SavedStateHandle causes a fatal TransactionTooLargeException.
Senior engineers test process death by verifying that SavedStateHandle only retains lightweight identifier tokens (such as order IDs or draft UUIDs), while heavy payload data is reloaded from local Room SQLite databases.
Offline transition testing verifies the Single Source of Truth architecture.
Repositories use Room Flows as the primary stream; when network requests fail, the coroutine catches transport exceptions without terminating the Flow collector, allowing cached database rows to render smoothly while dispatching a one-shot Snackbar event via an isolated UI channel.""",
    "meta_ar": {
        "id": "TST-18",
        "questionAr": "كيف تختبر موت التطبيق في الخلفية (Process Death) وتدوير الشاشة (Rotation) وانقطاع الإنترنت (Offline)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على التمييز الهندسي الدقيق بين تدوير الشاشة (Configuration Change) وموت العملية بواسطة الـ OS (Process Death) وانقطاع الشبكة، واختبار استعادة البيانات بـ SavedStateHandle و Room وتجنب الـ TransactionTooLargeException.",
        "why_it_matters_ar": "التطبيقات الضعيفة تفقد بيانات المستخدم ومدخلاته بمجرد خروج المستخدم للرد على مكالمة بسبب موت التطبيق، أو تنهار عند انقطاع الإنترنت، واختبار هذه السيناريوهات يحمي تجربة المستخدم وثقته في التطبيق.",
        "worked_example_ar": "اختبار تدوير الشاشة وموت العملية وانقطاع الاتصال:\n```kotlin\n// 1. فحص تدوير الشاشة بالـ Scenario\nval scenario = ActivityScenario.launch(MyActivity::class.java)\nscenario.recreate()\n// 2. فحص موت العملية بـ SavedStateHandle\nval savedState = SavedStateHandle(mapOf(\"order_id\" to \"123\"))\nval viewModel = OrderViewModel(savedState, fakeRepo)\nassertEquals(\"123\", viewModel.orderId)\n// 3. فحص انقطاع النت والاعتماد على الكاش\ncoEvery { api.getData() } throws IOException()\nval result = repo.getData().first()\nassertTrue(result.fromCache)\n```",
        "trade_offs_ar": "حفظ البيانات في SavedStateHandle سريع ومناسب للمعرفات البسيطة لكنه مقيد بحجم 1 ميجابايت كحد أقصى للـ Binder، بينما حفظها في Room دائم وغير مقيد بالحجم لكنه يتطلب قراءة وكتابة من القرص (Disk I/O).",
        "failure_modes_ar": "الاعتماد الكامل على المتغيرات داخل الـ ViewModel للاحتفاظ بالبيانات؛ فالـ ViewModel ينجو من تدوير الشاشة فقط، لكنه يتدمر تماماً ويفقد كل شيء عند حدوث Process Death في الخلفية.",
        "production_perspective_ar": "في التطبيقات الإنتاجية، نختبر Process Death برمجياً بحقن SavedStateHandle وهمي، ونلزم تخزين المعرفات فقط في الـ Bundle والبيانات الكبيرة في Room، مع تفعيل خاصية Don't keep activities أثناء الفحص اليدوي.",
        "how_to_answer_ar": "اشرح الفروق الثلاثة بوضوح سينيور: أولاً تدوير الشاشة (Rotation) يدمر الـ Activity فقط ويبقى الـ ViewModel في الذاكرة ونختبره بـ `scenario.recreate()`، ثانياً موت العملية (Process Death) يدمر الـ Process والـ ViewModel بالكامل بواسطة الـ OS ونختبر استعادة الحالة من `SavedStateHandle` و Room، وثالثاً انقطاع الإنترنت (Offline) ونختبر قدرة الـ Repository على التقاط الـ `IOException` وعرض داتا الكاش من قاعدة البيانات مع تنبيه المستخدم.",
        "talking_points_ar": "فارق تدوير الشاشة عن موت العملية، ودور ViewModelStoreOwner، وتدمير العملية بالـ Low Memory Killer، واسترجاع المعرفات بـ SavedStateHandle، وحدود الـ Binder transaction بـ 1MB، واختبار الـ Offline بـ Single Source of Truth في Room.",
        "follow_ups_ar": "- **المحاور:** \"كيف تحاكي Process Death يدوياً على جهاز حقيقي أو محاكي؟\"\n  **المرشح:** \"عن طريق تشغيل خيار `Don't keep activities` في إعدادات المطور، أو بوضع التطبيق في الخلفية وإرسال أمر `adb shell am kill <package_name>` ثم فتح التطبيق من قائمة الـ Recent Apps للتأكد من استعادة الحالة.\"\n\n- **المحاور:** \"لماذا نمنع وضع قوائم المنتجات أو البيانات الكبيرة في `SavedStateHandle`؟\"\n  **المرشح:** \"لأن الـ SavedState بيتم نقله عبر الـ Binder Transaction المحدود بـ 1 ميجابايت على مستوى نظام أندرويد بالكامل؛ ووضع بيانات ضخمة فيه بيرمي كراش قاتل هو `TransactionTooLargeException`.\"",
        "self_check_ar": "هل ميزت بين Rotation و Process Death؟ هل بينت خطورة TransactionTooLargeException؟ وهل وضحت اختبار الـ Offline؟",
        "references_ar": f"- [Restore UI state in Android](https://developer.android.com/topic/libraries/architecture/saving-states) — الدليل الرسمي لحفظ واستعادة واجهات المستخدم.\n- [Testing ViewModels with SavedStateHandle](https://developer.android.com/topic/libraries/architecture/viewmodel/viewmodel-savedstate#testing) — اختبارات الـ ViewModels مع SavedState.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "بنختبر التلات حالات بمنهجية هندسية واضحة: في تدوير الشاشة (Rotation)، الـ Activity بس بتتدمر والـ ViewModel بيفضل عايش في الذاكرة، وبنختبر ده بـ `ActivityScenario.recreate()`. أما في موت العملية (Process Death)، النظام بيموت الـ JVM والـ ViewModel بالكامل بسبب نقص الرام؛ وبنختبر استعادة الحالة بحقن كائن `SavedStateHandle` فيه المعرفات الأساسية مع استرجاع باقي الداتا من Room. وفي حالة انقطاع النت (Offline)، بنحاكي رمي `IOException` ونتأكد إن الـ Repository بيرجع البيانات المتكيفة في كاش SQLite ويعرض للواجهة حالة Offline بدون كراش.",
        "best_answer_ar": "التعامل مع انقطاع السياق من أهم المهارات اللي بتميز المهندس المحترف عن المبتدئ، لأن أغلب المشاكل في الإنتاج بتظهر لما التطبيق يرجع من الخلفية أو النت يقطع.\n\nالسيناريو الأول: تدوير الشاشة (Rotation)؛ ده مجرد Configuration Change، النظام بيهدم الـ Activity ويعيد بناءها، لكن الـ ViewModelStore بيفضل محفوظ في الذاكرة. بنختبر السيناريو ده باستخدام `ActivityScenario.recreate()` ونتأكد إن المدخلات والـ State معملتش Reset ومفيش أي Network Call اتعاد عشوائياً.\n\nالسيناريو الثاني: موت التطبيق في الخلفية (Process Death)؛ لما المستخدم يروح تطبيق تاني ورام الجهاز تقل، نواة لينكس بتموت الـ Process بالكامل، وده معناه إن الـ ViewModel والـ Singletons وكل الذاكرة بتتمسح! لما المستخدم يرجع، النظام بيفتح الـ Activity من الصفر. بنختبر الاستعادة بتمرير كائن `SavedStateHandle` للـ ViewModel والتأكد إنه قرأ معرف الطلب أو المسودة واسترجع البيانات فوراً من قاعدة بيانات Room بدلاً من العودة للشاشة الرئيسية.\n\nالسيناريو الثالث: انقطاع النت التام (Offline Transition)؛ بنعمل Mock للـ Network بحيث يرمي `SocketTimeoutException` أو `UnknownHostException`، ونتأكد إن الـ Repository بيطبق نمط Single Source of Truth؛ يعني بيبعت بيانات الكاش المحفوظة في Room عبر الـ Flow للواجهة، مع إرسال إشعار للمستخدم إنه في وضع عدم الاتصال بدون أي انهيار للتطبيق.",
        "deep_answer_ar": "تحت الكابوت، الحالات التلاتة بتشغل طبقات ومسارات مختلفة تماماً داخل معمارية نظام أندرويد وإدارة الذاكرة في النواة.\nفي تدوير الشاشة، دورة الحياة بتتم عبر `ConfigurationController` و `ActivityThread`؛ النظام بيستدعي `retainNonConfigurationInstances()` للاحتفاظ بالـ ViewModelStore في كائن الـ Host، وبالتالي الشاشة الجديدة بتتصل بنفس كائنات الـ ViewModel السابقة بدون أي Disk I/O وبدون تكرار لطلبات الشبكة.\n\nأما في موت العملية (Process Death)، فالأمر بيتم بتوجيه صارم من الـ Low Memory Killer (LMK) في نواة لينكس بالتنسيق مع `ActivityManagerService`؛ النظام بياخد البيانات اللي اتكتبت في `onSaveInstanceState` وينقلها عبر الـ Binder IPC للـ System Server Memory كـ Parcelable payload ويقتل الـ PID تماماً لتحرير الذاكرة للنظام.\nولأن قناة الـ Binder مشتركة ومحدودة بسعة 1 ميجابايت فقط لجميع العمليات، وضع قوائم أو صور فيها بيسبب فوراً استثناء `TransactionTooLargeException`؛ عشان كده في الكود السينيور بنحفظ المعرفات البسيطة والرموز المفتاحية فقط في الـ `SavedStateHandle`، وبنعتمد على Room لحفظ واسترجاع البيانات الكبيرة على القرص.\n\nوفي اختبارات الـ Offline، بنتحقق من صمود معمارية الـ Reactive Stream؛ الـ Flow بيتصل بالـ Room DAO كـ Source of Truth دائم، ومحاولة جلب الشبكة بتتم في Coroutine منفصل، ولما يفشل الاتصال بنلتقط الـ Transport Exception ونعرض الكاش للمستخدم بسلاسة فائقة وبدون أي وميض أو تذبذب أو انهيار برمجي."
    }
}

# ==========================================
# TST-19: Write tests for three parallel APIs with partial success and cancellation.
# ==========================================
DATA["TST-19"] = {
    "concept_en": """Testing concurrent asynchronous operations across three parallel network APIs requires verifying both partial-success aggregation and parent-child cancellation semantics. When an application fetches independent data streams simultaneously (such as UserProfile, AccountBalance, and LoyaltyRewards), senior architectures avoid rigid all-or-nothing failures by encapsulating concurrent requests inside a supervisorScope or executing parallel async jobs with isolated failure handling. In partial-success configurations, failure of a non-critical endpoint (such as LoyaltyRewards returning an HTTP 500) must not cancel the remaining siblings; the system aggregates available data into a degraded UI state while recording error telemetry. Conversely, when the parent coroutine scope is cancelled (due to the user navigating away or screen dismissal), all three in-flight network requests must immediately abort via cooperative cancellation, preventing orphaned socket leaks and late-arriving state mutations.""",
    "walkthrough_en": """Testing parallel API aggregation with partial success and cooperative cancellation:
```kotlin
// Data aggregator combining three parallel API streams
class DashboardAggregator(
    private val profileApi: ProfileApi,
    private val balanceApi: BalanceApi,
    private val loyaltyApi: LoyaltyApi
) {
    suspend fun fetchDashboard(): DashboardResult = supervisorScope {
        val profileDeferred = async { runCatching { profileApi.getProfile() } }
        val balanceDeferred = async { runCatching { balanceApi.getBalance() } }
        val loyaltyDeferred = async { runCatching { loyaltyApi.getLoyaltyPoints() } }

        DashboardResult(
            profile = profileDeferred.await().getOrNull(),
            balance = balanceDeferred.await().getOrNull(),
            loyalty = loyaltyDeferred.await().getOrNull()
        )
    }
}

// Unit testing partial success and cancellation with TestScope
@OptIn(ExperimentalCoroutinesApi::class)
class DashboardAggregatorTest {
    private val profileApi = mockk<ProfileApi>()
    private val balanceApi = mockk<BalanceApi>()
    private val loyaltyApi = mockk<LoyaltyApi>()
    private val aggregator = DashboardAggregator(profileApi, balanceApi, loyaltyApi)

    @Test
    fun fetchDashboard_oneApiFails_returnsPartialSuccessWithRemainingData() = runTest {
        // Profile and Balance succeed, Loyalty throws 500 error
        coEvery { profileApi.getProfile() } returns UserProfile("Alex")
        coEvery { balanceApi.getBalance() } returns AccountBalance(amount = 1500.0)
        coEvery { loyaltyApi.getLoyaltyPoints() } throws HttpException(Response.error<Any>(500, "".toResponseBody()))

        val result = aggregator.fetchDashboard()

        // Assert partial degradation: profile and balance present, loyalty null
        assertEquals("Alex", result.profile?.name)
        assertEquals(1500.0, result.balance?.amount)
        assertNull(result.loyalty)
    }

    @Test
    fun fetchDashboard_parentCancelled_cancelsAllInFlightRequests() = runTest {
        // Simulate long-running network calls
        coEvery { profileApi.getProfile() } coAnswers { delay(1000); UserProfile("Alex") }
        coEvery { balanceApi.getBalance() } coAnswers { delay(1000); AccountBalance(100.0) }
        coEvery { loyaltyApi.getLoyaltyPoints() } coAnswers { delay(1000); LoyaltyPoints(50) }

        val job = launch { aggregator.fetchDashboard() }

        // Advance virtual clock partially, then cancel parent job
        advanceTimeBy(300)
        job.cancelAndJoin()

        // Verify cooperative cancellation terminated all three calls cleanly
        assertTrue(job.isCancelled)
    }
}
```""",
    "short_en": """We test three parallel APIs by evaluating two distinct behaviors. For partial success, we wrap parallel async jobs in supervisorScope, simulate one endpoint failing while the others succeed, and assert the resulting UI model gracefully aggregates available data while degrading the failed section. For cancellation, we launch the call in a test job, advance virtual time, cancel the parent job, and assert all in-flight child requests abort immediately.""",
    "structured_en": """Testing parallel network requests requires verifying both resilient fault isolation and cooperative cancellation propagation.
When fetching data from three independent endpoints—such as user profile, bank balance, and rewards—an application must not collapse if an auxiliary service experiences downtime.
To test partial-success semantics, we configure our mock APIs so that the profile and balance calls succeed while the rewards call throws an HTTP 500 server exception.
In the implementation, wrapping child deferred calls in supervisorScope or runCatching ensures that the loyalty failure does not trigger cancellation of its siblings.
The test asserts that the returned aggregate data class successfully contains the user profile and bank balance, while gracefully marking the rewards payload as unavailable for degraded UI presentation.
To test cancellation semantics, we verify resource cleanup when the hosting lifecycle ends prematurely.
In our coroutine test, we simulate slow responses using delay and launch the aggregator inside an active TestScope job.
We advance virtual time partially using advanceTimeBy and invoke cancelAndJoin on the parent job.
The test asserts that the parent cancellation cooperatively cancels all three underlying async child jobs, confirming that no orphaned network requests continue executing in the background or mutate state after the user departs.""",
    "deep_senior_en": """Under the hood, coroutine concurrency and failure propagation depend on the structural relationship between Job and SupervisorJob within the coroutine context hierarchy.
In a standard coroutineScope, an uncaught exception in any child async builder cancels the scope's internal Job immediately.
This cancellation immediately propagates downwards to cancel all other active siblings and upwards to the parent caller, enforcing strict all-or-nothing transaction semantics.
For partial success, replacing coroutineScope with supervisorScope introduces a resilient SupervisorJob boundary into the hierarchy.
A SupervisorJob overrides the default parent-child cancellation contract: child failure does not cancel the supervisor and does not cancel neighboring sibling jobs.
However, because async deferred builders rethrow exceptions upon await(), tests verify that exceptions are encapsulated via runCatching or custom Result wrappers before awaiting to prevent unhandled CoroutineExceptionHandler triggers from crashing the test runner.
When testing cooperative cancellation, the mechanism relies on suspension points checking Job.isActive periodically.
When the parent Job is cancelled, it transitions to a Cancelling state and dispatches CancellationException to all active children.
Functions like delay or OkHttp's suspendCancellableCoroutine listen for this signal, aborting the active network call and closing the socket connection.
Using StandardTestDispatcher with advanceTimeBy allows tests to freeze time between request dispatch and response arrival, verifying that cancellation cleans up every child job deterministically without race conditions or memory leaks.""",
    "meta_ar": {
        "id": "TST-19",
        "questionAr": "كيف تكتب اختبارات لتشغيل ثلاثة اتصالات شبكة متوازية مع دعم النجاح الجزئي (Partial Success) والإلغاء (Cancellation)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على اختبار التزامن في الكوروتينز، والتمييز بين `coroutineScope` و `supervisorScope`، وتطبيق مبدأ النجاح الجزئي وعزل الأخطاء، والتحقق من إلغاء المهام الفرعية (Cooperative Cancellation) عند إلغاء الأب.",
        "why_it_matters_ar": "الاعتماد على إما الكل ينجح أو الكل يفشل يفسد تجربة المستخدم عند سقوط خدمة فرعية ثانوية، وعدم إلغاء الطلبات المعلقة يهدر باقة المستخدم والبطارية في الخلفية.",
        "worked_example_ar": "اختبار النجاح الجزئي والإلغاء لـ 3 اتصالات متوازية:\n```kotlin\n// نجاح البروفايل والرصيد مع فشل النقاط بدون إلغاء الباقي\ncoEvery { api.getProfile() } returns Profile(\"Alex\")\ncoEvery { api.getBalance() } returns Balance(100)\ncoEvery { api.getPoints() } throws IOException()\nval result = aggregator.fetchDashboard()\nassertNotNull(result.profile); assertNull(result.points)\n// فحص الإلغاء الشامل عند مغادرة الشاشة\nval job = launch { aggregator.fetchDashboard() }\njob.cancelAndJoin()\nassertTrue(job.isCancelled)\n```",
        "trade_offs_ar": "استخدام `coroutineScope` يضمن اتساق البيانات التام (All-or-Nothing) لكنه يفشل الشاشة بالكامل إذا سقطت خدمة تافهة، بينما `supervisorScope` يعزل الفشل ويتيح النجاح الجزئي لكنه يتطلب معالجة دقيقة للـ State الناقصة في الـ UI.",
        "failure_modes_ar": "استخدام `async` داخل `coroutineScope` عادي مع رمي استثناء غير معالج؛ مما يؤدي لإلغاء باقي الاتصالات فوراً وانهيار التطبيق، أو نسيان التحقق من الإلغاء مما يسرب اتصالات معلقة.",
        "production_perspective_ar": "في الشاشات الرئيسية الكبيرة (Dashboards)، نعتمد دائماً `supervisorScope` لعزل الأخطاء، ونفحص في الـ CI أن فشل العروض الترويجية لا يعطل عرض رصيد الحساب البنكي، مع التأكد من إيقاف الاتصالات بمجرد غلق الشاشة.",
        "how_to_answer_ar": "قسم الإجابة لمحورين أساسيين: أولاً النجاح الجزئي (Partial Success) باستخدام `supervisorScope` مع `async` و `runCatching` لعزل الخطأ وفحص أن فشل إحدى الخدمات لا يعطل الأخريات وتجميع البيانات المتاحة في الواجهة، ثانياً فحص الإلغاء (Cancellation) بإلغاء الـ Job الأصلي واستخدام `TestScope` للتأكد من انتشار الإلغاء فوراً لكل الـ Deferred Jobs الفرعية وإغلاق الـ Sockets.",
        "talking_points_ar": "الفارق بين coroutineScope و supervisorScope، وتأثير الاستثناء على الـ Siblings، واستخدام async مع runCatching، وانتشار الـ CancellationException، والتحكم في الوقت بـ StandardTestDispatcher.",
        "follow_ups_ar": "- **المحاور:** \"لماذا يفشل التيست لو استخدمت `coroutineScope` عادي مع فشل إحدى الدوال؟\"\n  **المرشح:** \"لأن في `coroutineScope` العادي، أي استثناء غير معالج في كوروتين فرعي بينتشر للأب فوراً وبيلغي كل الـ Siblings التانية، فالطلبين التانيين هيتكنسلوا حتى لو كانوا ناجحين.\"\n\n- **المحاور:** \"كيف تتأكد أن كولباك الشبكة توقف بالفعل عند الإلغاء؟\"\n  **المرشح:** \"باستخدام `suspendCancellableCoroutine` و `invokeOnCancellation`؛ فلما الكوروتين يتكنسل بيتم استدعاء `call.cancel()` لإغلاق اتصال الـ OkHttp Socket فوراً لمنع استهلاك الباقة.\"",
        "self_check_ar": "هل شرحت الفرق بين coroutineScope و supervisorScope؟ هل وضحت اختبار النجاح الجزئي؟ وهل أثبتت إلغاء جميع الطلبات المتزامنة؟",
        "references_ar": f"- [Kotlin Coroutines Best Practices](https://developer.android.com/kotlin/coroutines/coroutines-best-practices) — دليل ممارسات الكوروتينز الرسمي من جوجل.\n- [Testing Kotlin Coroutines](https://developer.android.com/kotlin/coroutines/test) — الدليل الرسمي لاختبار الكوروتينز مع TestScope.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "بنكتب اختبارين متكاملين لتغطية السلوك ده: أولاً اختبار النجاح الجزئي (Partial Success)، بنستخدم `supervisorScope` مع `async` و `runCatching`، وبنحاكي نجاح طلب البروفايل والرصيد وفشل طلب نقاط المكافآت بكود 500؛ التيست بيتأكد إن الفشل معطلش باقي الطلبات وإن النتيجة رجعت بيانات البروفايل والرصيد بنجاح مع عرض حالة مؤقتة للخدمة المتعطلة. ثانياً اختبار الإلغاء (Cancellation)، بنشغل الـ Job في بيئة `TestScope`، ونعمل محاكاة لتأخر الشبكة، وبعدين ننادي `job.cancelAndJoin()`؛ ونتأكد بـ `assertTrue(job.isCancelled)` إن كل الاتصالات الفرعية اتكنسلت فوراً بدون أي تسريب لاتصالات الشبكة في الخلفية.",
        "best_answer_ar": "التعامل مع اتصالات الشبكة المتوازية بيحتاج فهماً عميقاً لقواعد انتشار الأخطاء والإلغاء في الكوروتينز.\n\nالمحور الأول: اختبار النجاح الجزئي (Partial Success)؛ في شاشات زي الـ Dashboard، التطبيق بيحتاج بيانات المستخدم ورصيد الحساب وعروض الخصومات في نفس الوقت. لو خدمة العروض وقعت، مش مقبول أبداً الشاشة كلها تقفل وتظهر خطأ! الحل الهندسي هو تغليف الدوال بـ `supervisorScope` واستخدام `async` مع `runCatching`. في التيست، بنعمل Mock بحيث البروفايل والرصيد يرجعوا داتا سليمة، ونقاط الخصم ترمي خطأ شبكة؛ التيست بيعمل Assert إن الـ Result النهائية فيها بيانات الحساب سليمة وإن الجزء الفاشل بقى null لعرض واجهة بديلة، وده بيثبت عزل الفشل بنجاح.\n\nالمحور الثاني: اختبار الإلغاء التشاركي (Cooperative Cancellation)؛ لو المستخدم دخل الشاشة وخرج فوراً، لازم التلات طلبات يتلغوا فوراً لتوفير الرام والبطارية ومنع تعديل الواجهة بعد مغادرتها. بنختبر ده بتشغيل الـ Aggregator داخل كائن `Job` تجريبي في `runTest`، وبنقدم وقت الـ TestDispatcher الافتراضي شوية بدون ما الاتصالات تخلص، وبعدها بننادي `job.cancelAndJoin()`. التيست بيتأكد إن الـ Job اتلغت بنجاح وإن كل الـ Children اتوقفوا ومفيش أي استجابة متأخرة هتتنفذ بعد الخروج.",
        "deep_answer_ar": "تحت الكابوت، انتشار الأخطاء والإلغاء بيعتمد على الشجرة الهرمية للـ Job والـ CoroutineContext في مكتبة كوروتينز كوتلن.\nفي الـ `coroutineScope` الافتراضي، أي استثناء بيحصل في `async` بينتقل فوراً للأعلى، والأب بينفذ إلغاء متسلسل (Cascading Cancellation) بيلغي كل الـ Siblings التانية بدون استثناء، وده بيحقق مبدأ الـ All-or-Nothing الصارم.\nعشان نحقق النجاح الجزئي ونحافظ على استقرار الواجهة، بنستخدم `supervisorScope` اللي بيحط كائن `SupervisorJob` في جذر الشجرة الفرعية؛ ميزة الـ SupervisorJob الجوهرية إنه بيكسر حلقة انتشار الإلغاء؛ فلما طلب المكافآت يفشل، الـ Supervisor مبيتكنسلش وبيسمح للـ async التانيين يكملوا تنفيذهم بسلام ونجاح، مع استخدام `runCatching` عشان الـ `await()` ميرميش استثناء غير معالج يلغي الـ Test Thread أو يكرش التطبيق.\n\nأما في اختبار الإلغاء التشاركي، فالمحرك بيعتمد على إشارات الـ Cooperative Cancellation ونقاط التعليق (Suspension Points) وفحص راية `Job.isActive`؛ لما الأب يتكنسل، بيبعت `CancellationException` لكل المهام الفرعية التابعة له.\nدوال زي `delay` أو استدعاءات `suspendCancellableCoroutine` في OkHttp بتستقبل الإشارة دي فوراً، وبتقوم باستدعاء `call.cancel()` لإغلاق الـ Socket وتحرير موارد الـ Connection Pool فوراً.\nوباستخدام `StandardTestDispatcher` مع `advanceTimeBy`، بنقدر نجمد الزمن الافتراضي ونفحص حالة الـ Jobs بدقة متناهية ونضمن عدم وجود أي تسريب لموارد النظام أو اتصالات معلقة في الإنتاج."
    }
}

# ==========================================
# TST-20: Write tests for a payment retry path guaranteeing no duplicate charge.
# ==========================================
DATA["TST-20"] = {
    "concept_en": """Testing payment retry workflows requires enforcing strict cryptographic idempotency guarantees to ensure that network timeouts or application restarts never trigger duplicate financial charges. When a client initiates a monetary transaction, the architecture must generate a unique, cryptographically stable Idempotency Key (such as a UUIDv4 combined with order identity) and persist the transaction locally to Room SQLite in an INITIALIZED state before dispatching the HTTP network request. If a lost-response failure occurs—where the server successfully processes the charge but the client experiences a read timeout or socket drop—the client retries the transaction using the exact same Idempotency Key. The remote payment gateway recognizes the duplicate submission and returns the original authorization result without re-billing the account. Tests must verify that the same key is transmitted across retries, that process resurrection resumes from local state, and that concurrent retry attempts are debounced.""",
    "walkthrough_en": """Testing idempotent payment retry and duplicate charge prevention:
```kotlin
// Payment service enforcing idempotency and local state persistence
class PaymentRepository(
    private val paymentApi: PaymentApi,
    private val paymentDao: PaymentDao
) {
    suspend fun processPayment(orderId: String, amount: Double): PaymentResult {
        // Retrieve existing transaction or create new one with persistent idempotency key
        val transaction = paymentDao.getTransaction(orderId) ?: PaymentEntity(
            orderId = orderId,
            idempotencyKey = UUID.randomUUID().toString(),
            amount = amount,
            status = PaymentStatus.PENDING
        ).also { paymentDao.insert(it) }

        return try {
            val response = paymentApi.charge(
                idempotencyKey = transaction.idempotencyKey,
                request = ChargeRequest(orderId, amount)
            )
            paymentDao.updateStatus(orderId, PaymentStatus.SUCCESS)
            PaymentResult.Success(response.chargeId)
        } catch (e: IOException) {
            // Network dropped or timed out; transaction remains PENDING for safe retry
            PaymentResult.RetryableError("Network timeout. Safe to retry.")
        }
    }
}

// Unit tests validating idempotency key reuse on network failure
class PaymentRepositoryTest {
    private val paymentApi = mockk<PaymentApi>()
    private val paymentDao = FakePaymentDao()
    private val repository = PaymentRepository(paymentApi, paymentDao)

    @Test
    fun processPayment_lostResponseTimeout_retriesWithExactSameIdempotencyKey() = runTest {
        val capturedKeys = mutableListOf<String>()

        // First attempt throws SocketTimeoutException simulating lost response
        coEvery {
            paymentApi.charge(capture(capturedKeys), any())
        } throws SocketTimeoutException("Read timed out") andThen ChargeResponse(chargeId = "ch_9876")

        // First call fails due to timeout
        val firstResult = repository.processPayment(orderId = "order_101", amount = 99.0)
        assertTrue(firstResult is PaymentResult.RetryableError)

        // Retry the payment for the same order
        val retryResult = repository.processPayment(orderId = "order_101", amount = 99.0)
        assertTrue(retryResult is PaymentResult.Success)

        // Assert that both network attempts used the exact same idempotency key
        assertEquals(2, capturedKeys.size)
        assertEquals(capturedKeys[0], capturedKeys[1])

        // Verify database records single transaction in SUCCESS state
        assertEquals(PaymentStatus.SUCCESS, paymentDao.getTransaction("order_101")?.status)
    }

    @Test
    fun processPayment_distinctOrders_generateDifferentIdempotencyKeys() = runTest {
        val capturedKeys = mutableListOf<String>()
        coEvery { paymentApi.charge(capture(capturedKeys), any()) } returns ChargeResponse("ch_1")

        repository.processPayment("order_A", 10.0)
        repository.processPayment("order_B", 20.0)

        // Assert distinct idempotency keys per order
        assertNotEquals(capturedKeys[0], capturedKeys[1])
    }
}
```""",
    "short_en": """We test payment retries by simulating lost network responses and asserting strict idempotency key stability. The client persists an idempotency key into Room before calling the API. When a read timeout occurs after the server processed the charge, the retry logic uses the persisted key. The test captures outgoing HTTP headers to assert that both initial and retry attempts transmit the identical idempotency key, guaranteeing the server never debits the customer twice.""",
    "structured_en": """Testing payment workflows demands extreme rigor because a failure in retry logic can cause catastrophic duplicate billing of customers.
In distributed systems, the most dangerous failure mode is the lost-response scenario.
In this case, the payment gateway successfully debits the customer card, but the returning HTTP 200 response is severed by cellular packet loss or a client read timeout.
To guarantee that retrying does not create a second charge, the client must implement idempotent retries.
Before dispatching any network request, the repository creates a unique Idempotency Key and commits it to a local Room SQLite database alongside the order identifier in a pending status.
If the request fails with a network exception, the transaction record remains in the database.
When the user or a background worker retries the transaction, the repository reloads the existing record and submits the identical idempotency key in the HTTP header.
The remote payment gateway detects the key, matches it against its authorization ledger, and returns the original transaction receipt without charging the card again.
Our unit tests verify this contract by capturing all outgoing charge requests, asserting that retry calls reuse the exact same idempotency key, and verifying that the local database transitions to success without duplicate entries.""",
    "deep_senior_en": """Under the hood, payment safety depends on a coordinated distributed consensus contract between the mobile client's SQLite database and the backend payment gateway.
The core vulnerability during payment processing is non-atomic failure across process boundaries.
If an application generates an idempotency key purely in memory, an Android process death or app crash during a network timeout would cause the resurrection process to generate a new key on retry, triggering a double charge.
Senior engineers mandate an offline-first transactional sequence: the client begins a SQLite database transaction, writes the order ID and generated UUID idempotency key to disk with write-ahead logging (WAL), and commits before opening the network socket.
When MockWebServer simulates an HTTP 504 Gateway Timeout or a TCP socket drop via SocketPolicy.DISCONNECT_DURING_RESPONSE_BODY, OkHttp throws a SocketTimeoutException.
The test asserts that the repository catches this transport exception without clearing the local idempotency key.
During the subsequent retry invocation, the repository queries the database, extracts the stored key, and transmits it via the Idempotency-Key HTTP header.
On the backend, payment systems (such as Stripe or custom banking APIs) lock the idempotency key in Redis with a 24-hour TTL; if a second request arrives with that key, the gateway short-circuits execution and echoes the cached charge response.
Tests also verify process resurrection by simulating an app kill between the network drop and the retry, proving the system is resilient against sudden mobile process death.""",
    "meta_ar": {
        "id": "TST-20",
        "questionAr": "كيف تكتب اختبارات لمسار إعادة محاولة الدفع (Payment Retry) مع ضمان عدم تكرار الخصم المالي؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على تصميم واختبار أنظمة الدفع المالي الحساسة، وتطبيق مبدأ الـ Idempotency، والتعامل مع سيناريو الـ Lost Response، وحفظ مفاتيح العمليات في SQLite قبل الاتصال بالشبكة لضمان عدم سحب الأموال مرتين.",
        "why_it_matters_ar": "سحب أموال العميل مرتين بسبب إعادة المحاولة عند انقطاع النت يدمر سمعة الشركة ويسبب مشاكل قانونية كارثية، واختبار الـ Idempotency هو الصمام الفاصل لمنع هذه الكارثة.",
        "worked_example_ar": "اختبار إعادة محاولة الدفع بنفس الـ Idempotency Key:\n```kotlin\n// محاكاة سقوط الرد بعد الخصم وإعادة المحاولة بنفس المفتاح\nval keys = mutableListOf<String>()\ncoEvery { api.charge(capture(keys), any()) } throws SocketTimeoutException() andThen SuccessResponse()\nrepo.processPayment(\"order_1\", 100.0) // فشل بتايم آوت\nrepo.processPayment(\"order_1\", 100.0) // إعادة المحاولة\nassertEquals(2, keys.size)\nassertEquals(keys[0], keys[1]) // تأكيد تطابق المفتاح\n```",
        "trade_offs_ar": "توليد الـ Idempotency Key وحفظه في Room قبل الاتصال بالشبكة يضيف عملية كتابة بسيطة على القرص، لكنه الإجراء الإجباري الوحيد هندسياً لمنع سحب الأموال مرتين عند موت التطبيق.",
        "failure_modes_ar": "توليد الـ Idempotency Key في الذاكرة فقط (In-Memory) داخل كلاس الـ ViewModel؛ فإذا مات التطبيق أثناء التايم آوت سيعيد المستخدم المحاولة بمفتاح جديد تماماً ويتم خصم المبلغ مرتين.",
        "production_perspective_ar": "في تطبيقات الدفع والتجارة الإلكترونية، نلزم كتابة الـ Transaction في Room بحالة PENDING ومفتاح فريد قبل إطلاق طلب OkHttp، ونربط معالجة العمليات العالقة بـ WorkManager مع فحص تطابق الـ Headers في الـ CI.",
        "how_to_answer_ar": "اشرح السيناريو الأخطر وهو الـ Lost-Response (السيرفر خصم المبلغ لكن الرد انقطع في كابل النت)، ثم وضح الحل الهندسي المعتمد: حفظ الـ Idempotency Key في Room SQLite محلياً قبل أي اتصال بالنت، وفي التيست بنعمل محاكاة لسقوط الاتصال بـ `SocketTimeoutException` ونتأكد بـ ArgumentCaptor إن طلب الإعادة أرسل نفس الـ `Idempotency-Key` تماماً في الـ Header، وإن قاعدة البيانات حدثت الحالة لـ SUCCESS بدون إنشاء صف جديد.",
        "talking_points_ar": "سيناريو الـ Lost Response، ومفهوم الـ Idempotency في أنظمة الدفع، وتخزين المفتاح في Room قبل الـ Network Call، والتقاط الـ Headers بـ ArgumentCaptor، ودور الـ Idempotency-Key header في بوابات الدفع.",
        "follow_ups_ar": "- **المحاور:** \"ماذا يحدث لو قفل التطبيق أو مات بسبب Process Death أثناء انتظار رد عملية الدفع؟\"\n  **المرشح:** \"طالما المفتاح محفوظ في قاعدة بيانات Room بحالة PENDING، بمجرد فتح التطبيق أو تشغيل WorkManager هيقرأ نفس المفتاح ويبعته في طلب الاستعلام أو إعادة المحاولة، وبوابة الدفع هترجع تفاصيل العملية السابقة بدون أي خصم جديد.\"\n\n- **المحاور:** \"لماذا لا نكتفي بإعادة المحاولة التلقائية في OkHttp Interceptor؟\"\n  **المرشح:** \"لأن إعادة المحاولة في طبقة الشبكة للـ POST requests خطيرة جداً وممكن تكرر الخصم لو السيرفر مش Idempotent، فالإعادة لازم تكون مدارة في طبقة الـ Business Logic مع مفتاح فريد ومسجل في الداتابيز.\"",
        "self_check_ar": "هل شرحت سيناريو الـ Lost Response؟ هل وضحت حفظ الـ Idempotency Key في Room؟ وهل أثبتت تطابق المفتاح في التيست؟",
        "references_ar": f"- [Stripe Idempotent Requests Guide](https://stripe.com/docs/api/idempotent_requests) — التوثيق القياسي للـ Idempotency في بوابات الدفع العالمية.\n- [Offline-first Mobile Architecture](https://developer.android.com/topic/architecture/data-layer/offline-first) — دليل جوجل لمعمارية التطبيقات التي تعمل بدون اتصال.",
        "quick_answer_ar": "بنختبر مسار إعادة محاولة الدفع بمحاكاة أخطر سيناريو وهو الـ Lost-Response؛ يعني السيرفر يخصم الفلوس لكن الرد ينقطع بسبب تايم آوت في الشبكة. المنهجية المتبعة إن التطبيق بينشئ مفتاح فريد (Idempotency Key) ويسجله في قاعدة بيانات Room محلياً بحالة PENDING قبل ما يبعت الطلب للسيرفر. التيست بيحاكي رمي `SocketTimeoutException` في أول محاولة، وعند إعادة المحاولة للطلب نفسه، بنستخدم فاحص المعاملات للتأكد من إن الطلبين أرسلوا نفس الـ `Idempotency-Key` تماماً في الـ Headers، وبكده السيرفر بيرجع إيصال العملية السابقة بدون سحب الفلوس مرة تانية.",
        "best_answer_ar": "اختبار عمليات الدفع المالي هو مسؤولية هندسية حساسة جداً، لأن أي غلطة في كود إعادة المحاولة ممكن تخصم من كارت العميل مرتين وتدمر ثقة المستخدمين في التطبيق بالكامل.\n\nالمشكلة الحقيقية في الشبكات اللاسلكية مش إن الطلب ميوصلش، بل إنه يوصل والسيرفر يسحب الفلوس فعلاً، لكن وأنت بتستقبل الرد شبكة الموبايل تقطع ويحصل `SocketTimeoutException`. لو التطبيق أعاد المحاولة بشكل أعمى، السيرفر هيعتبره طلب جديد وهيخصم المبلغ للمرة التانية!\n\nالحل الهندسي المعياري اللي بنختبره هو الـ Idempotency؛ قبل ما نفتح اتصال الشبكة، بنفتح Transaction في Room ونسجل بيانات الطلب مع مفتاح فريد ومستقر (`UUID`) بحالة PENDING. لما يحصل خطأ في الشبكة، السجل بيفضل موجود في الداتابيز. ولما المستخدم يدوس إعادة المحاولة أو التطبيق يعيد الاتصال، الـ Repository بيجيب نفس المفتاح المحفوظ ويبعته في الـ Header للطلب التاني.\n\nفي كود التيست، بنعمل محاكاة لسقوط الاتصال في أول مرة، ونجاحه في المرة التانية. وبنلتقط الـ Headers المرسلة ونتأكد بـ `assertEquals` إن المفتاح المستخدم في المحاولتين هو نفس المفتاح بالبايت، وبكده بنثبت إن بوابة الدفع هترجع رد العملية السابقة بأمان تام وبدون أي تكرار للخصم.",
        "deep_answer_ar": "تحت الكابوت، أمان الدفع المالي بيعتمد على بروتوكول اتفاق موزع (Distributed Consensus) بين قاعدة بيانات SQLite في الموبايل وبوابة الدفع البعيدة عبر الـ Idempotency Key.\nأكبر خطأ شائع هو توليد مفتاح الـ Idempotency في الذاكرة (In-Memory) داخل الـ ViewModel؛ لأنه لو حصل انقطاع في الشبكة وتزامن مع موت العملية بـ Process Death أو كراش، التطبيق لما يفتح هيولد مفتاح جديد ويخصم المبلغ مرتين.\nعشان كده المعمارية السينيور بتعتمد على نمط Offline-First: التطبيق بيكتب الطلب والمفتاح في Room عبر الـ Write-Ahead Logging (WAL) ويعمل Commit على القرص قبل ما يفتح الـ TCP Socket مع السيرفر.\n\nأثناء الفحص بـ MockWebServer، بنستخدم `SocketPolicy.DISCONNECT_DURING_RESPONSE_BODY`؛ المحاكي بيقبل الاتصال ويبعت جزء من الهيدرز وبعدها يقفل الـ Socket فجأة، وده بيجبر OkHttp إنه يرمي `SocketTimeoutException` أصلي.\nالتيست بيتأكد إن الـ Repository بيمسك الاستثناء بأمان بدون ما يمسح المفتاح من الداتابيز.\nوفي محاولة الإعادة، بنسترجع المفتاح ونبعته في الـ `Idempotency-Key` header، وبوابة الدفع في الباك إند بتكون مسجلة المفتاح ده في كاش زي Redis مع قفل موزع (Distributed Lock)، فلما يوصلها الطلب التاني بتعرف إنه مكرر وبترجع نفس كائن الـ Charge القديم من الكاش، وده بيحقق حماية مطلقة لأموال العملاء."
    }
}

# ==========================================
# TST-21: A flaky test passes locally but fails on CI. Explain triage and mitigation.
# ==========================================
DATA["TST-21"] = {
    "concept_en": """Triaging and mitigating automated tests that pass consistently on local workstations but fail intermittently in Continuous Integration environments requires a disciplined root-cause diagnosis rather than superficial retry masking. CI runner nodes exhibit fundamentally different runtime characteristics than developer machines: virtualized headless CPU resource constraints, thread scheduling latency, lack of physical GPU rendering pipelines, unpredictable network socket jitter, randomized test class execution ordering, and dirty shared state between containerized jobs. Senior engineers isolate the root cause by gathering telemetry—inspecting failure stack traces, emulator video recordings, and Logcat dumps—before categorizing the issue into one of four primary failure modes: uncoordinated concurrency race conditions, shared static state pollution across test suites, missing Android UI idling synchronization, or aggressive CI runner CPU throttling. Mitigations enforce hermetic test sandboxing, deterministic dispatcher injection, and quarantine protocols.""",
    "walkthrough_en": """Diagnosing CI flakiness and enforcing hermetic isolation in Gradle and Kotlin:
```kotlin
// 1. Gradle configuration enforcing test sandboxing and animation disabling
android {
    testOptions {
        execution 'ANDROIDX_TEST_ORCHESTRATOR'
        animationsDisabled = true
        unitTests {
            isIncludeAndroidResources = true
            all {
                // Fail immediately on leaked background threads
                testLogging {
                    events "passed", "skipped", "failed", "standardError"
                }
                maxParallelForks = (Runtime.runtime.availableProcessors() / 2).coerceAtLeast(1)
            }
        }
    }
}

// 2. Hermetic test isolating shared preferences and coroutine dispatchers
@OptIn(ExperimentalCoroutinesApi::class)
class UserSessionManagerTest {
    private val testDispatcher = StandardTestDispatcher()
    private lateinit var sharedPreferences: SharedPreferences
    private lateinit var sessionManager: UserSessionManager

    @Before
    fun setUp() {
        // Enforce ephemeral sandbox: clear storage before EVERY test run
        val context = ApplicationProvider.getApplicationContext<Context>()
        sharedPreferences = context.getSharedPreferences("test_session", Context.MODE_PRIVATE)
        sharedPreferences.edit().clear().commit()

        Dispatchers.setMain(testDispatcher)
        sessionManager = UserSessionManager(sharedPreferences, testDispatcher)
    }

    @After
    fun tearDown() {
        // Prevent state bleed into neighboring tests
        sharedPreferences.edit().clear().commit()
        Dispatchers.resetMain()
    }

    @Test
    fun login_successfulToken_persistsSessionDeterministically() = runTest(testDispatcher) {
        sessionManager.saveToken("jwt_secret_token_123")
        advanceUntilIdle() // Eliminates async timing race conditions

        assertEquals("jwt_secret_token_123", sessionManager.getToken())
    }
}
```""",
    "short_en": """We triage CI-only flaky tests by analyzing artifacts: video recordings, thread dumps, and Logcat. We reproduce the issue locally by running tests in randomized order with throttled CPU cores. To mitigate, we isolate shared state by clearing databases and preferences between runs, eliminate timing races with TestDispatchers and IdlingResources, disable animations via testOptions, and use Android Test Orchestrator to execute tests in clean processes.""",
    "structured_en": """When a test passes on a developer laptop but fails intermittently on CI, senior engineers treat it as an urgent diagnostic priority rather than re-running the build until it passes.
The triage workflow begins with evidence collection.
We examine the CI test failure report, download the emulator screen recording, and cross-reference Logcat logs with the failure timestamp to observe the exact UI state and background thread activity at the moment of failure.
Next, we formulate and verify hypotheses.
One frequent cause is test order dependency, where an earlier test modifies a shared singleton, in-memory database, or SharedPreferences file without cleaning up, polluting the environment for subsequent tests.
We reproduce this locally by running Gradle test suites with randomized execution order using testLogging and parallel fork flags.
Another primary cause is thread scheduling starvation on low-power CI virtual machines, where background coroutines or RxJava streams execute slower than assertions expect, leading to assertion race conditions.
Mitigation follows a three-step protocol.
First, we enforce hermetic isolation by clearing all persistent storage and resetting static state in teardown methods or running tests via Android Test Orchestrator.
Second, we replace arbitrary delays with deterministic TestDispatchers and Compose synchronization.
Third, if a test cannot be fixed immediately, we quarantine it from the blocking presubmit gate to maintain team velocity while investigating.""",
    "deep_senior_en": """Under the hood, CI flakiness is primarily an entropy problem caused by architectural impedance mismatches between the host JVM, the Android OS thread scheduler, and the containerized virtual runner.
Developer workstations typically boast high clock speed multi-core processors where background threads finish almost instantaneously, masking missing synchronization bugs.
In containerized CI environments (such as Docker on Kubernetes or GitHub Actions), CPU resources are throttled, meaning background threads in Dispatchers.Default or IO may be preempted for tens of milliseconds.
If a test relies on arbitrary timing or uncoordinated coroutine execution, the assertion thread evaluates before the worker thread finishes writing memory, causing intermittent assertion errors.
To guarantee deterministic execution, tests must replace real dispatchers with StandardTestDispatcher, which virtualizes time and couples scheduler advancement to advanceUntilIdle().
For instrumented UI tests, flakiness often originates from the Android Choreographer and RenderThread missing frames due to CI virtualization lag.
Configuring testOptions { animationsDisabled = true } modifies the global system settings (window_animation_scale, transition_animation_scale, and animator_duration_scale) to 0.0, eliminating frame interpolation waits.
Finally, executing via Android Test Orchestrator isolates each test into its own freshly initialized instrumentation APK process (invoking am instrument for every method), guaranteeing zero static variable leakage or cached DexClassLoader contamination across the test suite.""",
    "meta_ar": {
        "id": "TST-21",
        "questionAr": "اختبار يفشل على خوادم الـ CI فقط وينجح على جهاز المطور (Flaky Test). كيف تشخص المشكلة وتعالجها هندسياً؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على تشخيص مشاكل الاختبارات المتذبذبة (Flaky Tests) في الـ CI، وتحليل أسبابها (Randomized Order, Concurrency Races, Static State Leaks, Resource Throttling)، واستخدام الأدوات الهندسية لمنع التذبذب كـ Test Orchestrator و TestDispatchers.",
        "why_it_matters_ar": "الاختبارات المتذبذبة تدمر ثقة الفريق في خطوط الـ CI وتدفع المطورين للضغط على Re-run بشكل عشوائي، مما يعطل نشر التحديثات ويهدر آلاف الساعات من إنتاجية الشركة.",
        "worked_example_ar": "عزل الاختبارات وضبط الـ CI لمنع التذبذب:\n```kotlin\n// 1. في build.gradle: عزل كل تيست في بروسيس منفصلة وإلغاء الأنيميشن\ntestOptions {\n    execution 'ANDROIDX_TEST_ORCHESTRATOR'\n    animationsDisabled = true\n}\n// 2. تنظيف الـ State بعد كل تيست وضبط الـ Dispatcher\n@After fun tearDown() {\n    sharedPrefs.edit().clear().commit()\n    Dispatchers.resetMain()\n}\n```",
        "trade_offs_ar": "تشغيل `Android Test Orchestrator` يفتح Process جديدة لكل تيست مما يزيد زمن الـ CI بنسبة بسيطة، لكنه يقضي تماماً على تسريب الذاكرة والـ Static State بين الاختبارات.",
        "failure_modes_ar": "إخفاء الفشل بعمل `retry(3)` في إعدادات الـ CI بدلاً من حل السبب الجذري؛ مما يزيد زمن البناء ويدفن سباقات الخيوط (Race Conditions) الخطيرة في كود الإنتاج.",
        "production_perspective_ar": "في الشركات الكبيرة، الاختبار المتذبذب يتم عزله فوراً في مسار Quarantine منفصل لمنع تعطيل الـ PRs، مع تكليف فريق لمعرفة السبب الجذري وإصلاحه خلال 48 ساعة قبل إعادته للمسار الرئيسي.",
        "how_to_answer_ar": "وضح المنهجية بأسلوب منظم: أولاً التشخيص بجمع الأدلة (فحص الـ Logs وفيديو المحاكي وتتبع الـ Threads)، ثانياً تحديد الفرضيات وأبرزها تلوث الحالة المشتركة (Shared State Leaks) وترتيب الاختبارات العشوائي وبطء خوادم الـ CI، وثالثاً الحلول الهندسية بتنظيف الداتابيز بعد كل اختبار، وتفعيل `Android Test Orchestrator`، وإلغاء حركات الأنيميشن في الـ Gradle، والتحكم في الكوروتينز بـ `StandardTestDispatcher` وعزل الاختبارات غير المستقرة (Quarantine).",
        "talking_points_ar": "جمع الأدلة وفحص Logcat، وتسريب الحالة المشتركة (State Bleed)، وفارق عتاد الـ CI وسرعة المعالجات، ودور Android Test Orchestrator، وإلغاء الأنيميشن في Gradle، وسياسة الـ Quarantine للـ Flaky tests.",
        "follow_ups_ar": "- **المحاور:** \"كيف تكتشف أن التيست يتأثر بترتيب تشغيل الاختبارات الأخرى؟\"\n  **المرشح:** \"عن طريق تشغيل التيست بمفرده في البداية؛ فإذا نجح 100 مرة بمفرده وفشل فقط عند تشغيل الـ Test Suite كاملة، بتعرف إن في تيست قبله كتب في SharedPreferences أو Singleton ومعملش Clean up.\"\n\n- **المحاور:** \"لماذا نمنع وضع Thread.sleep كحل للمشاكل دي؟\"\n  **المرشح:** \"لأن `Thread.sleep` بيخمن وقت الانتظار تخميناً أعمى؛ فلو خادم الـ CI بطيء التيست هيفشل برضه، ولو السيرفر سريع هنضيع وقت ع الفاضي، والبديل هو `IdlingResource` أو `advanceUntilIdle`.\"",
        "self_check_ar": "هل وضحت خطوات التشخيص وجمع الأدلة؟ هل بينت أسباب التذبذب في الـ CI؟ وهل ذكرت الحلول الهندسية مثل Orchestrator وتنظيف الـ State؟",
        "references_ar": f"- [Android Test Orchestrator](https://developer.android.com/training/testing/instrumented-tests/androidx-test-libraries/test-orchestrator) — الدليل الرسمي لتشغيل الاختبارات في عمليات معزولة.\n- [Google Testing Blog: Flaky Tests](https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html) — ممارسات جوجل العالمية للتعامل مع الاختبارات المتذبذبة.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "بنتعامل مع الـ Flaky Test على الـ CI بمنهجية تشخيص علمية صارمة: أولاً بنجمع الأدلة من تقارير الـ CI وفيديوهات المحاكي وسجلات Logcat لمعرفة اللحظة الدقيقة للفشل. ثانياً بنختبر الفرضيات الشائعة زي اعتماد التيست على ترتيب تشغيل معين، أو تسريب بيانات سابقة في الـ SharedPreferences، أو بطء معالجات الـ CI الافتراضية مقارنة بجهاز المطور. وثالثاً بنطبق الحلول الجذرية: بنعزل الاختبارات تماماً بتنظيف الذاكرة بعد كل تيست، ونلغي الأنيميشن في Gradle، ونستخدم `Android Test Orchestrator` لتشغيل كل تيست في بروسيس نظيفة، ونعزل التيست في مسار Quarantine لو هيأخر الـ PRs لحد ما يتحل.",
        "best_answer_ar": "فشل الاختبار على الـ CI فقط ونجاحه على جهاز المطور مش لغز ولا صدفة، بل هو نتيجة مباشرة لاختلاف بيئة التشغيل وسرعة المعالجات.\n\nخطوات التشخيص والحل بتمشي بالترتيب التالي:\nأولاً: جمع الأدلة وفحص اللوجات؛ بنزل ملفات الـ Artifacts من الـ CI، وبنتفرج على فيديو الشاشة وسجلات الـ Logcat وقت الفشل. بنشوف هل الزرار مظهرش بسبب تأخر الاتصال؟ ولا التيست حاول يدوس قبل ما الشاشة تحمل؟\n\nثانياً: التحقق من تسريب الحالة المشتركة (Shared State Bleed)؛ في أوقات كتير بيكون في تيست سابق خزن توكن في SharedPreferences أو كتب داتا في قاعدة البيانات ومعملهاش مسح، فلما خادم الـ CI يرتب الاختبارات عشوائياً، التيست اللاحق بيقرأ داتا ملوثة ويفشل. بنعيد إنتاج ده محلياً بتشغيل الاختبارات بترتيب عشوائي.\n\nثانياً: معالجة سباقات الخيوط (Concurrency Races)؛ أجهزة المطورين سريعة جداً فالكوروتينز بتخلص فوراً قبل ما التيست يعمل Assert، بينما خوادم الـ CI الافتراضية مواردها مقيدة وممكن تتأخر ميلي ثواني زيادة. الحل هو منع استخدام `Thread.sleep` نهائياً، واستخدام `StandardTestDispatcher` والتحكم في الوقت بـ `advanceUntilIdle()`.\n\nثالثاً: العزل والضبط في Gradle؛ بنلغي حركات الأنيميشن بالكامل عبر `animationsDisabled = true` في الـ testOptions، وبنفعل `Android Test Orchestrator` عشان يرستر البروسيس بين كل تيست والتاني، وبنحط التيست المتذبذب في مسار Quarantine لحماية سرعة دمج الـ PRs لباقي الفريق.",
        "deep_answer_ar": "تحت الكابوت، تذبذب الاختبارات في الـ CI بينتج عن عدم التوافق الزمني والعتادي بين بيئة التطوير المحلية وبيئة الحاويات الافتراضية (Docker/K8s).\nفي لابتوب المطور، المعالج بيحتوي على أنوية فيزيائية سريعة جداً بتخلي خيوط الـ Background في الـ Coroutines تخلص شغلها فوراً، وده بيخفي أخطاء غياب التزامن (Missing Synchronization).\nأما في بيئة الـ CI المشتركة، النواة الافتراضية بتتعرض لـ CPU Throttling قوي، وممكن خيط الـ Worker يقف مؤقتاً في طابور الجدولة، فيقوم خيط الاختبار بعمل Assert قبل ما الـ State تتكتب في الذاكرة، ويحصل استثناء AssertionFailedError عشوائي يظهر ويختفي.\nعشان نحل ده بشكل قاطع، بنستبدل الـ Dispatchers الحقيقية بـ `StandardTestDispatcher` اللي بيجمد الزمن الافتراضي وبيربط تنفيذ المهام باستدعاء `advanceUntilIdle()`.\n\nوفي اختبارات الواجهة، الـ Choreographer في المحاكي الافتراضي بيتأخر في معالجة الفريمات بسبب غياب الـ GPU Acceleration في السيرفر؛ وده بيخلي ضغطات الإسبريسو تفوت مكانها وتفشل المزامنة. ضبط `animationsDisabled = true` بيعدل إعدادات النظام الداخلية `window_animation_scale` و `animator_duration_scale` إلى صفر، فبيلغي كل حركات الانتقال الزمنية والـ Interpolation.\nوأخيراً، تشغيل `Android Test Orchestrator` بيستدعي أمر `am instrument` منفصل لكل دالة اختبار، وده بيفرغ الـ Static Memory والـ ClassLoader تماماً ويمنع أي State Leakage بين الاختبارات في خطوط الإنتاج والـ CI."
    }
}

# ==========================================
# TST-22: A database migration fails only with old customer data. How do you generate realistic fixtures?
# ==========================================
DATA["TST-22"] = {
    "concept_en": """Testing SQLite database migrations against legacy customer data requires generating production-realistic, privacy-compliant test fixtures to validate complex schema transformations before release. Database migrations frequently succeed against empty schemas but crash catastrophically in production when encountering historical edge cases: unexpected NULL values in columns subsequently designated NOT NULL, legacy un-normalized text encodings, violated foreign key constraints, or partial migrations from long-discontinued app versions. Android's official Room testing artifact provides MigrationTestHelper to mechanically construct databases at historical schema versions, execute real DDL/DML migration scripts, and validate schema integrity. To produce realistic data without violating privacy regulations (GDPR/HIPAA), engineering teams never copy raw production database dumps. Instead, they synthesize realistic fixtures using schema-aware generators that model legacy data distributions, corrupted edge cases, and extreme schema variants.""",
    "walkthrough_en": """Creating historical schema fixtures and testing Room database migrations with MigrationTestHelper:
```kotlin
@RunWith(AndroidJUnit4::class)
class CustomerDatabaseMigrationTest {
    private val TEST_DB = "migration-test.db"

    @get:Rule
    val helper: MigrationTestHelper = MigrationTestHelper(
        InstrumentationRegistry.getInstrumentation(),
        AppDatabase::class.java.canonicalName,
        FrameworkSQLiteOpenHelperFactory()
    )

    @Test
    fun migrateV1ToV2_legacyCorruptedCustomerData_migratesSuccessfully() {
        // 1. Create database at historical Version 1 using auto-generated schema JSON
        var db = helper.createDatabase(TEST_DB, 1).apply {
            // 2. Insert realistic legacy customer fixtures directly via raw SQLite
            execSQL("INSERT INTO customers (id, name, legacy_notes, phone) VALUES ('cust_101', 'O''Connor & Sons', 'Legacy customer imported in 2018', NULL)")
            execSQL("INSERT INTO customers (id, name, legacy_notes, phone) VALUES ('cust_102', 'Global Logistics Ltd', NULL, '+1-555-0199')")
            close()
        }

        // 3. Execute Migration 1 -> 2 and validate schema integrity automatically
        db = helper.runMigrationsAndValidate(TEST_DB, 2, true, MIGRATION_1_2)

        // 4. Assert that legacy data was transformed safely according to new schema rules
        val cursor = db.query("SELECT id, name, phone, status FROM customers WHERE id = 'cust_101'")
        assertTrue(cursor.moveToFirst())

        // Verify NOT NULL default constraint applied safely to legacy NULL field
        val phoneIndex = cursor.getColumnIndex("phone")
        val statusIndex = cursor.getColumnIndex("status")
        assertEquals("UNSPECIFIED", cursor.getString(phoneIndex))
        assertEquals("ACTIVE", cursor.getString(statusIndex))
        cursor.close()
    }
}
```""",
    "short_en": """We test legacy migrations using Room's MigrationTestHelper, which boots historical schemas from versioned JSON files. We never copy raw user data due to privacy laws. Instead, we generate synthetic fixtures reflecting real customer anomalies: unexpected nulls, unescaped quotes, missing foreign keys, and empty strings. We insert these into the historical database, run the migration, and assert that data transformed cleanly without data loss or crashes.""",
    "structured_en": """Database migrations represent the highest-risk release boundary because a migration crash triggers fatal SQLiteException crashes on app startup, leaving users locked out until they reinstall.
A common engineering blind spot is testing migrations against clean, newly created tables rather than realistic legacy data.
In production, databases that have survived years of updates contain subtle anomalies: NULL entries created before a column became required, non-standard text encodings, and orphan rows left by unconstrained deletions.
To validate migrations thoroughly, we leverage Room's MigrationTestHelper.
This tool reads historical schema contracts exported as JSON files in app/schemas, constructing an authentic SQLite database matching the exact structural layout of older releases.
Because privacy compliance (GDPR and HIPAA) strictly forbids copying production databases into test environments, we synthesize realistic fixtures.
We author fixture generators that populate historical schemas with realistic edge-case distributions: strings containing SQL special characters like single quotes, corrupted timestamps, and default fallbacks for newly mandated non-null columns.
We execute helper.runMigrationsAndValidate, asserting that SQLite indexes, foreign keys, and migrated values conform to the target version without data loss.""",
    "deep_senior_en": """Under the hood, Room's MigrationTestHelper coordinates SQLite master tables, JSON schema specifications, and SQLite PRAGMA table information inspection.
During the Gradle build, Room's annotation processor generates schema definitions in app/schemas/<database_class>/<version>.json, describing exact SQLite CREATE TABLE, CREATE INDEX, and table hash identities.
When helper.createDatabase(name, version) runs, the test helper interprets the JSON schema, executing low-level SQLite DDL statements on the underlying FrameworkSQLiteOpenHelper to rebuild the ancient schema.
We then execute raw SQLite INSERT queries to inject our synthetic legacy fixtures.
These fixtures intentionally stress common SQLite failure vectors: inserting NULL into columns that the upcoming migration will alter to NOT NULL with an ALTER TABLE command (which SQLite natively restricts without table re-creation), inserting non-ASCII Unicode glyphs, and creating broken foreign key relationships.
When helper.runMigrationsAndValidate is invoked, Room executes the defined Migration scripts, then queries SQLite's internal pragma table_info(tableName) and pragma index_list(tableName) to perform a field-by-field, type-affinity, and nullability comparison against the target schema JSON.
If a column affinity or nullability contract does not match with 100% precision, Room throws an IllegalStateException before production release.
Senior engineers automate matrix migration testing, verifying direct jumps from version 1 to 5 alongside incremental hops from 1 to 2, 2 to 3, and so on.""",
    "meta_ar": {
        "id": "TST-22",
        "questionAr": "فشل ترحيل قاعدة البيانات (Database Migration) مع بيانات العملاء القديمة فقط. كيف تولد بيانات اختبار واقعية؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على اختبار وترحيل قواعد بيانات SQLite/Room بأمان، واستخدام `MigrationTestHelper` والـ Schemas التاريخية، وتوليد بيانات واقعية متوافقة مع الخصوصية (Privacy-compliant Synthetic Fixtures)، وفحص الحالات الشاذة للبيانات القديمة.",
        "why_it_matters_ar": "فشل الترحيل هو أخطر خطأ برمجي لأنه يتسبب في كراش فوري عند فتح التطبيق يجبر العميل على مسح بياناته بالكامل، واختبار الترحيل ببيانات قديمة يحمي قاعدة مستخدمي التطبيق التاريخية.",
        "worked_example_ar": "اختبار ترحيل داتابيز قديمة بـ MigrationTestHelper:\n```kotlin\n// 1. بناء داتابيز بإصدار قديم (v1) وحقن بيانات واقعية شاذة\nvar db = helper.createDatabase(TEST_DB, 1).apply {\n    execSQL(\"INSERT INTO users VALUES ('1', 'O''Connor', NULL)\")\n    close()\n}\n// 2. تشغيل الترحيل للإصدار 2 والتحقق من المخطط\ndb = helper.runMigrationsAndValidate(TEST_DB, 2, true, MIGRATION_1_2)\n// 3. التأكد من معالجة القيمة الـ NULL بدون كراش\nval cursor = db.query(\"SELECT status FROM users WHERE id = '1'\")\nassertTrue(cursor.moveToFirst())\n```",
        "trade_offs_ar": "توليد بيانات اصطناعية شاذة (Synthetic Fixtures) يتطلب جهداً في تصميم الحالات النادرة، لكنه البديل القانوني والآمن الوحيد لنقل قواعد بيانات العملاء الحقيقية المحظور استخدامها بسبب قوانين حماية البيانات.",
        "failure_modes_ar": "نسخ قاعدة بيانات عملاء حقيقية من الإنتاج واستخدامها في الاختبارات؛ مما يمثل خرقاً قانونياً صريحاً لـ GDPR وتسريباً لبيانات المستخدمين الحساسة.",
        "production_perspective_ar": "في التطبيقات الكبيرة، نحتفظ بمجلد `app/schemas` في السورس كنترول كمرجع لكل الإصدارات السابقة، ونلزم تشغيل اختبارات الترحيل لكل المسارات التاريخية من الإصدار الأول حتى الأخير في الـ CI.",
        "how_to_answer_ar": "وضح المنهجية بصرامة: أولاً نمنع منعاً باتاً استخدام داتا حقيقية من الإنتاج لمخالفتها قوانين الخصوصية، ثانياً نستخدم `MigrationTestHelper` المعتمد من Room اللي بيبني الداتابيز التاريخية من ملفات الـ JSON في `app/schemas`، ثالثاً نولد بيانات اصطناعية واقعية (Synthetic Fixtures) تحاكي المشاكل الحقيقية: نصوص فيها Single Quotes، قيم NULL في حقول أصبحت إجبارية، ومفاتيح خارجية مفقودة، ونفحص نجاح الترحيل بـ `runMigrationsAndValidate`.",
        "talking_points_ar": "أداة MigrationTestHelper وملفات الـ JSON في schemas، ومخاطر انتهاك الخصوصية بـ GDPR، وتوليد بيانات اصطناعية تحاكي الحالات الشاذة (Synthetic Data)، ومشاكل تحويل الأعمدة لـ NOT NULL في SQLite، وفحص الفهارس بـ PRAGMA.",
        "follow_ups_ar": "- **المحاور:** \"لماذا تفشل عمليات الترحيل في الإنتاج بينما تنجح دائماً في التيست البسيط؟\"\n  **المرشح:** \"لأن التيست البسيط بيجرب على جداول فارغة، بينما الإنتاج فيه داتا قديمة بقيم NULL أو نصوص غريبة اتكتبت قبل سنين لما كانت القيود مختلفة، فأول ما نضيف قيد NOT NULL من غير قيمة افتراضية SQLite بيرمي كراش فوراً.\"\n\n- **المحاور:** \"كيف تتعامل مع إضافة عمود NOT NULL لجدول يحتوي على ملايين الصفوف القديمة؟\"\n  **المرشح:** \"بنحدد قيمة افتراضية في جملة الـ SQL عبر `ALTER TABLE ... ADD COLUMN ... NOT NULL DEFAULT 'DEFAULT_VALUE'`، أو بنعيد إنشاء الجدول وننقل البيانات بتنظيف القيم الـ NULL إذا كان التعديل معقداً.\"",
        "self_check_ar": "هل شرحت أداة MigrationTestHelper؟ هل أكدت على معايير الخصوصية وتوليد بيانات اصطناعية؟ وهل بينت الحالات الشاذة الشائعة في الترحيل؟",
        "references_ar": f"- [Testing Room Migrations](https://developer.android.com/training/data-storage/room/testing-db) — الدليل الرسمي لجوجل لاختبار ترحيل قواعد بيانات Room.\n- [SQLite ALTER TABLE Capabilities](https://www.sqlite.org/lang_altertable.html) — توثيق SQLite للقيود المفروضة على تعديل الجداول.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "بنحل المشكلة دي باحترافية عبر أدوات واختبارات Room الرسمية: أولاً بنمنع تماماً نسخ داتابيز حقيقية من أجهزة المستخدمين لأن ده خرق صريح لقوانين الخصوصية (GDPR). بنستخدم أداة `MigrationTestHelper` اللي بتبني الداتابيز التاريخية بدقة من ملفات الـ JSON المحفوظة في مجلد `app/schemas`. بعدين بنولد بيانات اصطناعية واقعية (Synthetic Fixtures) بتشمل كل المشاكل الشائعة: قيم NULL في حقول هتبقى NOT NULL، ونصوص فيها علامات تنصيص خاصة، وعلاقات أيتام بدون Foreign Keys. وبنشغل أمر `runMigrationsAndValidate` للتأكد من إن عملية الترحيل بتعدل الداتا القديمة بنجاح وبدون أي كراش.",
        "best_answer_ar": "فشل ترحيل قاعدة البيانات مع المستخدمين القدامى هو كابوس التطبيقات الكبيرة؛ لأن لو التيست فشل في الإنتاج، التطبيق بيقفل ومبيفتحش تاني أبداً إلا بمسح الداتا.\n\nالسبب دايماً بيكون إن المطور اختبر الترحيل على داتابيز فاضية، بينما العميل القديم عنده داتا اتخزنت من سنين بقيم وقواعد قديمة. المنهجية المتبعة لحل ده بتمشي على تلات محاور:\nالمحور الأول: احترام الخصوصية التام؛ ممنوع نهائياً سحب داتابيز حقيقية لعميل، لأن ده انتهاك خطير للـ GDPR والـ Security Compliance. الحل هو توليد بيانات اصطناعية (Synthetic Fixtures) تحاكي خصائص وأشكال الداتا القديمة.\n\nالمحور الثاني: استخدام `MigrationTestHelper`؛ الأداة دي من مكتبة اختبارات Room بتعتمد على ملفات الـ JSON التاريخية اللي بنصدرها في `app/schemas`. بنطلب من الأداة تنشئ داتابيز بالإصدار القديم وليكن Version 1.\n\nالمحور الثالث: حقن البيانات الشاذة يدوياً؛ بنكتب أوامر `execSQL` لإدخال حالات معقدة: قيم NULL في أعمدة هتبقى إجبارية لاحقاً، ونصوص قديمة فيها أحرف خاصة زي الفاصلة العليا (Single Quotes)، وتواريخ بصيغ قديمة. بعد كدة بنشغل `helper.runMigrationsAndValidate()`، وده بينفذ الـ Migration ويراجع الـ Schema الناتجة والفهارس، وبنعمل فحص بالـ Cursor للتأكد من إن البيانات القديمة تم تحويلها بالقيم الافتراضية السليمة وبدون أي فقدان للبيانات.",
        "deep_answer_ar": "تحت الكابوت، أداة `MigrationTestHelper` بتتعامل مباشرة مع جداول النظام الداخلية في SQLite وملفات توصيف المخططات بصيغة JSON.\nأثناء الـ Build، معالج Room بيطلع ملف JSON لكل إصدار بيحتوي على تفاصيل الـ DDL والـ Hashes الدقيقة للأعمدة والفهارس. لما بنستدعي `helper.createDatabase(name, 1)`، الأداة بتستخدم `FrameworkSQLiteOpenHelper` لبناء الجداول بالـ Schema القديمة تماماً.\n\nقوة الفحص بتظهر في حقن سيناريوهات الفشل الخاصة بـ SQLite؛ أشهر مشكلة هي إن SQLite مبيسمحش بإضافة عمود `NOT NULL` بدون قيمة افتراضية `DEFAULT` في أمر `ALTER TABLE`. لو التيست اتعمل على داتابيز فاضية الكود هيعدي، لكن لما يكون في صفوف قديمة في الجدول SQLite هيرمي استثناء `Cannot add a NOT NULL column with default value NULL` ويفشل الإقلاع.\nعشان كده بنحقن صفوف حقيقية فيها بيانات ناقصة ونصوص تاريخية، ونختبر إن الـ Migration بتعالج ده سواء بوضع `DEFAULT` سليم أو باتباع نمط إعادة بناء الجدول الكامل (Create temp table, copy data, drop old table, rename temp table).\n\nوفي نهاية الفحص، دالة `runMigrationsAndValidate` بتستعلم عن أوامر `PRAGMA table_info` و `PRAGMA index_list` وتقارن كل عمود ونوعه والـ Nullability بتاعته بمخطط الـ JSON المستهدف بدقة 100%، وده بيحمي قاعدة العملاء التاريخية من أي كراش مفاجئ في الإنتاج."
    }
}

# ==========================================
# TST-23: How would you create a risk-based test plan for a security-sensitive release?
# ==========================================
DATA["TST-23"] = {
    "concept_en": """Architecting a risk-based test plan for a security-sensitive Android release requires systematically aligning testing rigor with threat severity and attack likelihood rather than testing features uniformly. Guided by threat modeling methodologies (such as STRIDE: Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, and Elevation of Privilege), engineering teams identify the highest-risk architectural boundaries: cryptographic key derivation in the Android Keystore, biometric user authentication, inter-process communication (IPC) via exported components, secure deep link URL parsing, SSL/TLS certificate pinning, and on-device token caching. Critical threat boundaries receive multi-layered automated verification matrices: unit tests targeting cryptographic primitives, instrumented tests exercising hardware secure element failure paths, dynamic penetration testing against exported Intent filters, and phased canary release rollouts with real-time security anomaly monitoring.""",
    "walkthrough_en": """Automating security trust boundary tests for Keystore ciphers and deep link validation:
```kotlin
// 1. Biometric Keystore cipher verification asserting authentication gating
@RunWith(AndroidJUnit4::class)
class KeystoreSecurityTest {
    private val keyAlias = "PaymentAuthKey"

    @Before
    fun generateGatedKey() {
        val keyGenerator = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore")
        keyGenerator.init(
            KeyGenParameterSpec.Builder(
                keyAlias,
                KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
            )
                .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                .setUserAuthenticationRequired(true) // Requires active biometric auth
                .setUserAuthenticationParameters(30, KeyProperties.AUTH_BIOMETRIC_STRONG)
                .build()
        )
        keyGenerator.generateKey()
    }

    @Test
    fun cipherInit_withoutPriorBiometricAuthentication_throwsUserNotAuthenticatedException() {
        val keyStore = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
        val secretKey = keyStore.getKey(keyAlias, null) as SecretKey
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")

        // Assert that hardware key denies access when biometric prompt was bypassed
        assertThrows(UserNotAuthenticatedException::class.java) {
            cipher.init(Cipher.ENCRYPT_MODE, secretKey)
        }
    }
}

// 2. Deep link parameter sanitization test preventing path traversal and script injection
class DeepLinkSecurityValidatorTest {
    private val validator = DeepLinkSecurityValidator()

    @Test
    fun parseTargetUrl_maliciousPathTraversalAndScripts_rejectedImmediately() {
        // Reject attempts to escape domain or inject malicious schemes
        assertFalse(validator.isValidNavigationUrl("https://example.com/checkout/../../admin/delete"))
        assertFalse(validator.isValidNavigationUrl("javascript:alert(document.cookie)"))
        assertFalse(validator.isValidNavigationUrl("file:///data/data/com.example.app/databases/app.db"))

        // Accept strictly validated whitelist domain routes
        assertTrue(validator.isValidNavigationUrl("https://example.com/orders/order_12345"))
    }
}
```""",
    "short_en": """We create a risk-based test plan by prioritizing testing based on threat severity using STRIDE. Highest-risk trust boundaries—biometrics, Android Keystore encryption, token storage, exported IPC components, and deep links—receive extensive automated unit, integration, and fuzz testing. Low-risk UI changes get standard smoke tests. We validate security boundaries, perform pen-testing, and enforce phased canary rollouts with anomaly monitoring.""",
    "structured_en": """A security-sensitive release cannot be validated by standard functional testing alone; it demands a threat-driven, risk-prioritized testing strategy.
The methodology begins with architectural threat modeling using frameworks like STRIDE.
We identify the application's most critical trust boundaries: user authentication, cryptographic key lifecycles, data-at-rest encryption, inter-process communication (IPC), and remote network ingestion.
Testing investment is distributed according to risk severity.
Tier 1 encompasses critical cryptographic and authentication paths.
We write automated tests verifying that Android Keystore keys enforce biometric authentication gates, asserting that attempting to encrypt or decrypt without authenticated hardware credentials throws UserNotAuthenticatedException.
We test that sensitive tokens stored in EncryptedSharedPreferences are never leaked to plain-text log files, and verify that deep links reject directory traversal attacks (such as path traversal sequences) and unauthorized URL schemes.
Tier 2 validates IPC and component exposure.
We assert that exported Activities, Services, and BroadcastReceivers require strict custom permissions and validate incoming Intent extras against malicious spoofing payloads.
Finally, the release pipeline mandates dynamic penetration testing and phased staged rollouts (1%, 5%, 25%, 100%) paired with real-time crash and anomaly monitoring to abort the release if unauthorized access indicators trigger.""",
    "deep_senior_en": """Under the hood, risk-based security testing verifies that application contracts strictly enforce the hardware and software trust boundaries established by the Linux kernel, Android framework, and hardware abstraction layer.
In Android's security architecture, the Android Keystore operates within a hardware-isolated environment—either ARM TrustZone (TEE) or a dedicated Secure Element (StrongBox Keymaster chip).
When KeyGenParameterSpec mandates setUserAuthenticationRequired(true), the Keystore binds the generated AES cryptographic key to an internal hardware authentication token (AuthToken) signed with an HMAC secret known only to the biometric authentication daemon and Keymaster hardware.
Our automated security tests verify that initializing a Cipher without a valid biometric hardware AuthToken causes Keymaster to return KM_ERROR_KEY_USER_NOT_AUTHENTICATED, mapped directly to UserNotAuthenticatedException by the framework.
For network security, automated assertions verify that NetworkSecurityConfig enforces strict cleartextTrafficPermitted=false across all domains, enforces Certificate Transparency, and validates SSL pin digests against expired or revoked certificates.
For component security, we test AndroidManifest.xml boundaries using static analysis and instrumented tests, asserting that android:exported=false is enforced on all internal components and that PendingIntents use FLAG_IMMUTABLE to prevent Intent redirection hijacking.
During the phased canary rollout, security telemetry monitors real-time tamper-detection flags, SafetyNet/Play Integrity verdict degradation, and abnormal token revocation rates to trigger automated rollback within minutes of an emerging exploit.""",
    "meta_ar": {
        "id": "TST-23",
        "questionAr": "كيف تضع خطة اختبار قائمة على المخاطر (Risk-Based Test Plan) لإصدار عالي الحساسية الأمنية؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على وضع خطة اختبار أمنية استراتيجية معتمدة على نموذج المخاطر (STRIDE Threat Model)، وتحديد نقاط الاتصال الحساسة (Android Keystore, Biometrics, Deep Links, IPC)، والتحقق من التشفير وعزل الصلاحيات، وإدارة الإطلاق التدريجي (Canary Releases).",
        "why_it_matters_ar": "معاملة جميع أجزاء التطبيق بنفس الأهمية يهدر الوقت في فحص ألوان الشاشات ويهمل الثغرات الأمنية الكارثية في التشفير أو الصلاحيات التي قد تؤدي لاختراق بيانات المستخدمين وتسريب حساباتهم.",
        "worked_example_ar": "اختبار نقاط الأمان الحساسة في Keystore وفحص الـ Deep Links:\n```kotlin\n// 1. فحص حماية مفتاح التشفير وطلب البصمة الحيوية إجبارياً\nval cipher = Cipher.getInstance(\"AES/GCM/NoPadding\")\nassertThrows(UserNotAuthenticatedException::class.java) {\n    cipher.init(Cipher.ENCRYPT_MODE, secretKey) // يفشل بدون بصمة\n}\n// 2. فحص الـ Deep Link ومنع حقن مسارات خبيثة\nassertFalse(validator.isValidUrl(\"https://example.com/../../admin\"))\nassertTrue(validator.isValidUrl(\"https://example.com/orders/123\"))\n```",
        "trade_offs_ar": "التركيز على الاختبارات الأمنية العميقة واختبارات الاختراق يتطلب وقتاً وأدوات متخصصة، لكنه يحمي التطبيق من الغرامات القانونية وتسريب البيانات ويوجه جهد الفريق للمناطق الأكثر خطورة.",
        "failure_modes_ar": "توزيع جهد الاختبار بالتساوي على كل الميزات كأن زر تغيير الثيم بنفس خطورة كود تشفير بطاقات الدفع؛ مما يترك ثغرات أمنية حرجة بدون فحص دقيق.",
        "production_perspective_ar": "في التحديثات الأمنية الحساسة، نعتمد إطلاقاً تدريجياً صارماً (1% ثم 5% ثم 25%) مع مراقبة حية لتقارير الـ Play Integrity ومعدلات فشل التوكنات، مع تفعيل خاصية Rollback فوري عند رصد أي هجوم.",
        "how_to_answer_ar": "وضح المنهجية كقائد هندسي: أولاً تصنيف المخاطر بنموذج STRIDE لتحديد الأماكن الأكثر تهديداً، ثانياً تركيز الاختبارات الصارمة على بوابات الأمان: مفاتيح Android Keystore ومطابقة البصمة، وتشفير البيانات بـ EncryptedSharedPreferences، والتحقق من الـ Deep Links لمنع الـ Path Traversal، وحماية مكونات الـ IPC بـ `exported=false`، وثالثاً تنفيذ اختبارات اختراق واختبارات تراجع، ورابعاً إطلاق تدريجي (Canary) مع مراقبة أمنية حية.",
        "talking_points_ar": "نموذج التهديدات STRIDE، ومستويات الخطورة وتوزيع الجهد، ومفاتيح Android Keystore مع Secure Element، والتحقق من روابط Deep Links، وتأمين مكونات IPC والـ PendingIntents، والإطلاق التدريجي مع مراقبة الأمان.",
        "follow_ups_ar": "- **المحاور:** \"كيف تختبر أن الـ Deep Link لا يمكن استغلاله للوصول لملفات النظام الحساسة؟\"\n  **المرشح:** \"عن طريق كتابة اختبارات تحقق صارمة ترفض أي رابط يحتوي على `..` (Path Traversal) أو مخططات غير مسموحة زي `file://` أو `javascript:`، ومطابقة النطاق والمسار بدقة بـ Whitelist معتمدة.\"\n\n- **المحاور:** \"ما الإجراء الذي تتخذه لو اكتشفت ثغرة أمنية أثناء الإطلاق التدريجي بنسبة 5%؟\"\n  **المرشح:** \"بنوقف الإطلاق فوراً عبر Google Play Console (Halt Rollout)، وبنعطل الميزة عن بُعد عبر Firebase Remote Config لو كانت مربوطة بـ Feature Flag، وبنصدر تحديث Patch سريع لحل الثغرة قبل الاستئناف.\"",
        "self_check_ar": "هل حددت منهجية تصنيف المخاطر بنموذج STRIDE؟ هل شرحت اختبارات Keystore و Deep Links؟ وهل وضحت خطة الإطلاق والمراقبة؟",
        "references_ar": f"- [Android Security Checklist](https://developer.android.com/privacy-and-security/security-best-practices) — قائمة أفضل الممارسات الأمنية لتطبيقات أندرويد.\n- [OWASP Mobile Top 10](https://owasp.org/www-project-mobile-top-10/) — المعيار العالمي لأخطر الثغرات الأمنية في تطبيقات الموبايل.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "بنصمم خطة الاختبار القائمة على المخاطر (Risk-Based Test Plan) بتوجيه جهد الاختبار حسب درجة الخطورة ونموذج التهديدات (STRIDE)، مش بتوزيع الجهد عشوائياً. بنحدد نقاط التماس الأكثر حساسية: تشفير المفاتيح في `Android Keystore` واشتراط البصمة الحيوية، وحماية الـ Deep Links من هجمات الـ Path Traversal وحقن النصوص، والتأكد من إغلاق مكونات الـ IPC بـ `exported=false`. المناطق دي بنعمل عليها اختبارات وحدة وتكامل صارمة واختبارات اختراق، بينما الواجهات العادية بتاخد فحص سريع، وبنعتمد إطلاق تدريجي (Canary) بيبدأ بـ 1% مع مراقبة أمنية لحظية للتحقق من سلامة النظام.",
        "best_answer_ar": "في التحديثات الأمنية الحساسة، أكبر غلطة بيقع فيها الفريق هي معاملة كل أجزاء التطبيق بالتساوي؛ فحص شاشة الإعدادات مينفعش ياخد نفس تركيز واختبار كود تشفير بطاقات الدفع وتسجيل الدخول بالبصمة.\n\nالخطة الهندسية المتبعة بتعتمد على أربع ركائز أساسية:\nالركيزة الأولى: نمذجة التهديدات (Threat Modeling)؛ بنحلل مسارات البيانات الحساسة باستخدام معايير زي STRIDE أو OWASP Mobile. بنحدد المناطق الأكثر خطورة: تشفير الذاكرة، والتواصل مع السيرفر، ومكونات النظام المفتوحة.\n\nالركيزة الثانية: اختبار بوابات الأمان الأساسية (Tier 1)؛ بنكتب اختبارات أوتوماتيكية متخصصة: في البصمة، بنفحص إن مفاتيح `Android Keystore` بترمي استثناء `UserNotAuthenticatedException` لو تمت محاولة التشفير بدون التحقق من بصمة المستخدم. في الـ Deep Links، بنعمل اختبارات ضد حقن النصوص والـ Path Traversal لمنع فتح ملفات الداتابيز المحلية. وفي مكونات التطبيق، بنتأكد إن الـ Activities والـ Services مش `exported` إلا للضرورة القصوى مع حماية الـ PendingIntents بـ `FLAG_IMMUTABLE`.\n\nالركيزة الثالثة: اختبارات التراجع والاختراق؛ بنعمل Dynamic Pen-Testing لمحاكاة هجمات حقيقية على أجهزة معمول لها Root وفحص استجابة التطبيق لكشف التلاعب.\n\nالركيزة الرابعة: الإطلاق التدريجي والمراقبة الحية؛ بننشر التحديث بنسبة 1% ثم 5%، ونراقب تقارير الـ Play Integrity ونسب كراشات الأمان عبر منصات المراقبة اللحظية، وعند رصد أي سلوك مريب بنوقف الإطلاق فوراً لمنع انتشار الخطر.",
        "deep_answer_ar": "تحت الكابوت، الخطة الأمنية بتضمن احترام قيود الأمان الصارمة المفروضة من نواة لينكس ومستوى عتاد الجهاز المعزول (Hardware-backed Security).\nفي اختبارات `Android Keystore`، المفاتيح الحساسة بيتم توليدها داخل بيئة عتادية معزولة تماماً زي الـ Trusted Execution Environment (TEE) أو شريحة الـ StrongBox Keymaster المستقلة عتادياً.\nلما نحدد `setUserAuthenticationRequired(true)`، نظام الأمان بيشترط وجود توكن مصادقة عتادي مشفر (AuthToken) موقع بـ HMAC سري من سيرفس البصمة الحيوية ونواة النظام؛ والتيست بيتأكد برمجياً إن محاولة استدعاء `cipher.init()` بدون التوكن ده بتفشل من مستوى الـ Keymaster العتادي وترمي استثناء `UserNotAuthenticatedException` فوراً.\n\nأما في اختبارات الشبكة، بنفحص إن ملف `NetworkSecurityConfig` مانع لاتصالات الـ Cleartext تماماً ومفعل فيه الـ Certificate Pinning والـ Certificate Transparency للشهادات الرقمية، مع اختبار رد الفعل عند انتهاء الصلاحية.\nوفي حماية الـ IPC، بنتحقق من إن كل BroadcastReceiver أو Service غير مخصص للخارج يكون `android:exported=false` ومحمي بـ Permissions مخصصة مع إلزام `FLAG_IMMUTABLE` في الـ PendingIntents لمنع هجمات الـ Intent Spoofing.\nوأثناء الـ Canary Rollout، بنتابع مؤشرات الـ Play Integrity API ومعدلات الـ Revocation للتوكنات، وبنربط الميزات بـ Kill-Switch عبر Remote Config لتعطيل أي ميزة مخترقة في ثوانٍ معدودة وبدون الحاجة لانتظار مراجعة المتجر."
    }
}

# ==========================================
# TST-24: How do you gate PRs without creating an unreasonably slow pipeline?
# ==========================================
DATA["TST-24"] = {
    "concept_en": """Engineering a high-throughput Pull Request (PR) gating pipeline requires balancing rapid developer feedback loops (targeting sub-ten-minute validation) against comprehensive system quality assurances. Running exhaustive end-to-end emulator matrices and full UI regression suites on every commit introduces severe CI congestion, degrades developer velocity, and encourages premature merge bypasses. Senior engineering architectures resolve this tension by structuring validation into a multi-tiered testing pyramid: Tier 1 executes in fast PR presubmit gates, leveraging Git diffs and Gradle affected module detection to run only static analysis (ktlint, Detekt, Android Lint) and fast JVM unit/Robolectric tests against modified code. Expensive Tier 2 validations—including multi-device instrumented emulator suites, Macrobenchmark startup benchmarks, screenshot regression comparisons, and security vulnerability scans—are offloaded to asynchronous post-merge queues, nightly batches, or release-candidate triggers, accelerated via distributed remote build caching.""",
    "walkthrough_en": """Configuring fast affected module detection and Gradle remote build caching:
```kotlin
// 1. Enabling remote build caching and configuration caching in settings.gradle.kts
buildCache {
    local {
        isEnabled = true
        removeUnusedEntriesAfterDays = 7
    }
    remote<HttpBuildCache> {
        url = uri("https://gradle-cache.company.internal/cache/")
        isPush = System.getenv("CI_MASTER_BUILD") == "true"
        credentials {
            username = System.getenv("CACHE_USER")
            password = System.getenv("CACHE_PASSWORD")
        }
    }
}

// 2. Fast PR gating workflow command in CI pipeline
// Runs lint and JVM tests ONLY on modules affected by the current pull request branch
// ./gradlew checkAffected -PtargetBranch=origin/main --configuration-cache --parallel

// 3. GitHub Actions PR workflow tiered structure
/*
name: PR Fast Gate
on: [pull_request]

jobs:
  fast-checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'
      # Executes fast linting and unit tests on affected modules in parallel (~4-6 minutes)
      - name: Run Affected Module Tests
        run: ./gradlew testDebugUnitTest ktlintCheck --parallel --build-cache
*/
```""",
    "short_en": """We gate PRs fast by structuring a multi-tiered validation pipeline. Presubmit PR gates run in under 8 minutes by executing only fast checks on affected modules: linting, ktlint, and JVM unit tests with Gradle build caching and configuration caching. Slow tests—such as instrumented emulator runs, screenshot tests, and Macrobenchmarks—are offloaded to async merge queues or nightly builds, ensuring developers get rapid feedback without sacrificing quality.""",
    "structured_en": """Designing an effective pull request gating pipeline is an optimization problem between feedback latency and release safety.
If a PR pipeline takes 45 minutes to run, developer productivity grinds to a halt, context switching skyrockets, and engineering teams are tempted to bypass checks.
The industry gold standard is a tiered gating pyramid.
In Tier 1 (the synchronous PR presubmit gate), the goal is strict sub-ten-minute execution.
We achieve this by testing only what changed.
Using Git change detection tools (like Dropbox's Focus or Slack's affected-module-detector), Gradle identifies the delta between the PR branch and main, executing tasks exclusively on modified modules and their direct dependents while skipping unaffected library modules.
Presubmit gates are strictly confined to fast static analysis (Android Lint, Detekt, ktlint) and in-memory JVM unit and Robolectric tests.
Heavy validations belong in Tier 2 and Tier 3.
Full-suite instrumented emulator tests, Roborazzi screenshot comparisons, and Macrobenchmark performance tests run asynchronously in a post-merge queue or nightly builds.
If a nightly build flags a regression, an automated revert bot or on-call engineer handles it immediately.
Underpinning this entire pipeline is infrastructure optimization: enabling Gradle's remote HTTP build cache, persistent configuration cache, and parallel test task workers across CI runner containers.""",
    "deep_senior_en": """Under the hood, pipeline acceleration relies on Gradle's Directed Acyclic Graph (DAG) task execution engine, input/output hash fingerprinting, and distributed cache serialization.
When Gradle processes a task, it computes a composite SHA-256 fingerprint from the task inputs—source files, classpath dependencies, compiler versions, and environment variables.
With remote HTTP build caching enabled, Gradle queries the remote cache server; if a matching key exists, it downloads the pre-compiled class jars and test results, marking the task as FROM-CACHE and skipping compilation in milliseconds.
Configuration caching further accelerates runs by serializing the evaluated project model DAG to disk, bypassing the entire Groovy/Kotlin script evaluation phase on subsequent executions.
To isolate PR changes, affected module detection algorithms compute the reverse dependency tree: if a developer modifies a leaf feature module, only that feature's unit tests run; if a core shared module changes, the tool intelligently scales test coverage to all dependent consumers.
For instrumented tests that must run before merge, senior teams utilize emulator sharding (such as Flank or Marathon) across 20 concurrent cloud virtual devices, parallelizing a 60-minute test suite into 3 minutes.
Finally, predictive test selection algorithms monitor historical failure correlations, running only the top 10% of tests historically likely to catch bugs for a specific file diff, guaranteeing both peak developer velocity and rock-solid code health.""",
    "meta_ar": {
        "id": "TST-24",
        "questionAr": "كيف تضع بوابات فحص للـ PRs (PR Gating) بدون إبطاء خط أنابيب الـ CI بشكل مبالغ فيه؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على تصميم خط أنابيب CI/CD سريع وفعال للمطورين (Fast Feedback Loop)، والتمييز بين الفحوصات الفورية والفحوصات المؤجلة، واستخدام تقنيات Gradle المتقدمة كـ Remote Build Cache و Configuration Cache و Affected Module Detection.",
        "why_it_matters_ar": "خطوط الـ CI البطيئة التي تستغرق 40 دقيقة لكل PR تصيب المطورين بالإحباط وتعطل تسليم الميزات وتشجع على تخطي الفحوصات، بينما الخطوط الذكية تمنح ملاحظات في 5 دقائق مع الحفاظ على أعلى معايير الجودة.",
        "worked_example_ar": "تسريع خط الـ CI وفحص الموديولات المعدلة فقط:\n```kotlin\n// 1. تفعيل الكاش في settings.gradle.kts\nbuildCache {\n    remote<HttpBuildCache> {\n        url = uri(\"https://gradle-cache.company.internal/cache/\")\n        isPush = System.getenv(\"CI\") == \"true\"\n    }\n}\n// 2. تشغيل الفحص للموديولات المتأثرة بالـ PR فقط في الـ CI\n// ./gradlew testDebugUnitTest --parallel --build-cache\n```",
        "trade_offs_ar": "فحص الموديولات المتأثرة واختبارات الـ JVM في الـ PR وتأجيل اختبارات المحاكي للـ Nightly يوفر سرعة هائلة للمطورين، لكنه يتطلب نظام مراقبة وتنبيهات فورية لإصلاح أي كسر يظهر في البناء الليلي.",
        "failure_modes_ar": "تشغيل كل اختبارات الـ Instrumented Tests والـ Screenshot Tests على المحاكي مع كل Commit في كل PR؛ مما يؤدي لطوابير انتظار لا نهائية وتعطيل كامل للفريق.",
        "production_perspective_ar": "في المشروعات الضخمة، نلزم أن ينتهي فحص الـ PR في أقل من 7 دقائق عبر فحص الموديولات المعدلة فقط و Remote Build Cache، وننقل اختبارات الأجهزة والمحاكيات لـ Merge Queue أو البناء الليلي.",
        "how_to_answer_ar": "قسم الحل لهيكل هرمي واضح (Tiered Pipeline): المستوى الأول في الـ PR يستغرق أقل من 7 دقائق ويشمل الفحص الثابت (Lint, Detekt) واختبارات الـ JVM للموديولات المتأثرة فقط بـ Affected Module Detection، مع تسريع Gradle بـ Remote Cache والـ Configuration Cache. المستوى الثاني للاختبارات الثقيلة (Emulator Tests, Screenshots, Macrobenchmark) ينقل لـ Merge Queue أو Nightly Builds، واشرح تقنيات تقطيع الاختبارات (Sharding) على عدة أجهزة سحابية بالتوازي.",
        "talking_points_ar": "هرم الفحص المتدرج (Tiered Pyramid)، واكتشاف الموديولات المتأثرة بـ Git Diff، وتسريع Gradle بـ Remote Build Cache و Configuration Cache، وتأجيل اختبارات المحاكي للـ Nightly أو Merge Queue، وتقطيع الاختبارات بـ Sharding.",
        "follow_ups_ar": "- **المحاور:** \"كيف تكتشف الموديولات المتأثرة بالتعديل فقط في الـ PR؟\"\n  **المرشح:** \"باستخدام أدوات مثل `affected-module-detector`؛ الأداة بتقارن الـ Git Diff بين فرع الـ PR وفرع main، وبترسم شجرة الاعتماديات في Gradle فبتشغل التيست للموديول المعدل والموديولات اللي معتمدة عليه فقط، وبتتخطى باقي المشروع.\"\n\n- **المحاور:** \"ماذا تفعل لو اكتشف البناء الليلي (Nightly Build) كسراً ناتجاً عن PR تم دمجه؟\"\n  **المرشح:** \"النظام بينبه الفريق فوراً عبر قناة خاصة، والسياسة القياسية هي عمل Revert فوري للـ PR لحماية استقرار الفرع الرئيسي، وبعدين المطور بيصلح المشكلة على فرعه محلياً قبل المحاولة مرة تانية.\"",
        "self_check_ar": "هل حددت زمناً مستهدفاً للـ PR (أقل من 10 دقائق)؟ هل شرحت Affected Module Detection؟ وهل وضحت دور Remote Cache وتأجيل الاختبارات الثقيلة؟",
        "references_ar": f"- [Gradle Build Cache Best Practices](https://docs.gradle.org/current/userguide/build_cache.html) — توثيق جريدل الرسمي لتسريع البناء باستخدام الكاش.\n- [Optimizing CI/CD for Android](https://developer.android.com/studio/build/optimize-your-build) — دليل جوجل الرسمي لتحسين سرعة البناء في خطوط الإنتاج.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "بنبني بوابات فحص ذكية وسريعة للـ PRs بهيكل متدرج (Tiered Pipeline) بيحقق زمن استجابة أقل من 7 دقائق: في فحص الـ PR، بنشغل فقط الفحوصات السريعة على الموديولات اللي اتعدلت في الـ Branch الحالي باستخدام `Affected Module Detection`؛ يعني بنفحص الـ Lint واختبارات الـ JVM Unit Tests فقط، وبنسرع التنفيذ بـ `Gradle Remote Build Cache` و `Configuration Cache`. أما الاختبارات البطيئة والمكلفة زي اختبارات المحاكي والـ Screenshots و Macrobenchmark، بننقلها لمرحلة الـ Merge Queue أو البناء الليلي (Nightly Builds)، وبكده المطور بياخد Feedback فوري بدون تعطيل وبدون تراجع في الجودة.",
        "best_answer_ar": "تصميم خط فحص الـ PRs هو موازنة هندسية حاسمة بين سرعة المطورين وضمان الجودة؛ لو التيست أخد 45 دقيقة لكل PR، إنتاجية الفريق بتتدمر والناس بتبدأ تتجاوز الفحوصات.\n\nالمنهجية القياسية المعتمدة في الشركات الكبيرة بتعتمد على هرم الفحص الذكي:\nالمستوى الأول: فحص الـ PR الفوري (هدفنا أقل من 7 دقائق)؛ بنعتمد على تقنية كشف الموديولات المتأثرة (Affected Module Detection). الأداة بتقارن الـ Git Diff بالفرع الرئيسي وتحدد الموديولات اللي اتغيرت والاعتماديات التابعة ليها بس. بنشغل الفحص الثابت زي Android Lint و ktlint، واختبارات الـ JVM والـ Robolectric السريعة، وبنتخطى 80% من باقي المشروع غير المتأثر بالـ PR.\n\nالمستوى الثاني: تسريع بنية الـ Build؛ بنفعل الـ `Remote HTTP Build Cache` بحيث لو كود معين اتبنى على جهاز مطور تاني أو على الـ CI من قبل، Gradle ينزل الناتج من الكاش فوراً بـ `FROM-CACHE` في ثوانٍ معدودة، وبنفعل الـ `Configuration Cache` لتخطي قراءة ملفات الإعدادات في كل رن.\n\nالمستوى الثالث: ترحيل الفحوصات الثقيلة؛ اختبارات الـ Emulator البطيئة، واختبارات لقطات الشاشة (Screenshot Tests)، وقياس الأداء بـ Macrobenchmark بننقلها لـ Merge Queue بعد الموافقة على الـ PR أو للـ Nightly Builds اليومية، مع تقسيم اختبارات الـ Instrumentation بالتوازي عبر تقنية الـ Sharding على 15 محاكي سحابي في نفس الوقت.",
        "deep_answer_ar": "تحت الكابوت، تسريع خطوط الـ CI بيعتمد على خوارزميات الـ Task Graph في Gradle والبصمة التشفيرية للمدخلات والمخرجات (Input Fingerprinting).\nقبل تشغيل أي Task، محرك جريدل بيحسب هاش تشفيري مركب (SHA-256) بيشمل سورس الكود والـ Dependencies والـ JDK flags. بفضل تفعيل الـ `Remote Build Cache`، الـ Runner بيبعت الهاش ده لسيرفر الكاش، ولو لاقى نتيجة مطابقة بينزل الـ Jars الجاهزة فوراً بدون ما يترجم كود الـ Kotlin من جديد.\nوبالتزامن مع ده، الـ `Configuration Cache` بيحفظ الـ Task Execution Graph بالكامل على القرص، فبيتخطى مرحلة تقييم ملفات الـ build.gradle في ثوانٍ معدودة.\n\nوعلى مستوى الكود، أدوات زي `affected-module-detector` بتبني شجرة الـ Reverse Dependency Graph للمشروع بالكامل وبدقة فائقة؛ فلو التعديل في موديول فرعي للـ Feature، الجريدل بينفذ الـ Tests الخاصة بيه فقط، أما لو التعديل في موديول مشترك في الـ Core، الأداة بذكاء بتشغل التيست لكل الموديولات المعتمدة عليه.\nوفي اختبارات الـ Instrumentation الإجبارية، بنستخدم محركات متقدمة زي Marathon أو Flank لتقطيع الاختبارات (Sharding) على مصفوفة أجهزة افتراضية متعددة في السحابة؛ وبكده سويت الاختبارات الضخم اللي مدته ساعة بيتنفذ في أقل من 4 دقائق وبدون أي تعطيل لسرعة دمج الكود واستقرار بيئة الإنتاج."
    }
}

# Pre-validation word counts
def validate_words():
    print("Elevating 8 questions in TST (TST-17 to TST-24)...")
    errors = []
    for qid, d in sorted(DATA.items()):
        meta = d["meta_ar"]
        en_s = len(d["short_en"].split())
        en_st = len(d["structured_en"].split())
        en_d = len(d["deep_senior_en"].split())

        ar_q = len(meta["quick_answer_ar"].split())
        ar_b = len(meta["best_answer_ar"].split())
        ar_d = len(meta["deep_answer_ar"].split())

        print(f"{qid}: en_s={en_s}, en_st={en_st}, en_d={en_d} | ar_q={ar_q}, ar_b={ar_b}, ar_d={ar_d}")

        if not (35 <= en_s <= 110):
            errors.append(f"{qid} en_short invalid: {en_s}")
        if not (100 <= en_st <= 280):
            errors.append(f"{qid} en_structured invalid: {en_st}")
        if not (200 <= en_d <= 650):
            errors.append(f"{qid} en_deep invalid: {en_d}")

        if not (35 <= ar_q <= 110):
            errors.append(f"{qid} ar_quick invalid: {ar_q}")
        if not (90 <= ar_b <= 280):
            errors.append(f"{qid} ar_best invalid: {ar_b}")
        if not (180 <= ar_d <= 650):
            errors.append(f"{qid} ar_deep invalid: {ar_d}")

    if errors:
        print("\nPre-validation word count checks failed! Fix counts before updating files.")
        for e in errors:
            print(f"  ❌ {e}")
        sys.exit(1)
    else:
        print("\nPre-validation word count checks passed! Updating canonical questions...")

def apply_elevations():
    validate_words()

    topic_meta = {}
    for qid, d in sorted(DATA.items()):
        ee.update_canonical_question(
            qid=qid,
            concept_en=d["concept_en"],
            walkthrough_en=d["walkthrough_en"],
            structured_en=d["structured_en"],
            deep_senior_en=d["deep_senior_en"],
            short_en=d["short_en"],
        )
        topic_meta[qid] = d["meta_ar"]

    ee.save_topic_metadata("tst_17_24", topic_meta)
    ee.merge_all_metadata()

    for qid in sorted(DATA.keys()):
        ee.validate_question(qid)

    print("\nAll 8 TST questions (TST-17 to TST-24) successfully elevated and passed validation!\n")

if __name__ == "__main__":
    apply_elevations()
