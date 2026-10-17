# Batch 2: MEM-18, MEM-19, MEM-20
DATA = {}

DATA["MEM-18"] = {
    "concept_en": """Android Runtime (ART) compilation balances app installation speed, storage footprint, and execution performance using a hybrid execution model combining an interpreter, a Just-In-Time (JIT) compiler with a profile saver, and Ahead-Of-Time (AOT) compilation via dex2oat. When an app is newly installed or updated, classes and methods start uncompiled in JIT/interpreted mode, causing sluggish cold starts and frame drops during initial user interactions until ART discovers \"hot\" execution paths over repeated usage. Baseline Profiles solve this cold start penalty. They are plain-text rule files compiled into binary ART profile formats (`baseline.prof`) bundled within the APK or AAB asset directory (`assets/dexopt/baseline.prof`). When Google Play distributes the app, the cloud compilation service or local package manager passes the profile to `dex2oat` during installation, pre-compiling critical classes and methods into optimized machine code before the user launches the app for the very first time. Macrobenchmark is a Jetpack benchmarking tool that drives and measures end-to-end integration journeys on real devices. Unlike Microbenchmark (which benchmarks isolated in-memory algorithms), Macrobenchmark controls application process lifecycles (cold startup, warm startup, process termination) and automates UI interactions using UI Automator. It outputs deterministic metrics, including `StartupTimingMetric` and `FrameTimingMetric`, while capturing detailed Perfetto traces. Crucially, Macrobenchmark includes the `BaselineProfileRule`, which automates the discovery and generation of Baseline Profiles by recording which DEX classes and methods execute during critical user journeys.""",
    "walkthrough_en": """Generating a Baseline Profile using Macrobenchmark:
```kotlin
// In a dedicated benchmark module (avoids mixing test code with app code):
@RunWith(AndroidJUnit4::class)
class BaselineProfileGenerator {
    @get:Rule
    val rule = BaselineProfileRule()

    @Test
    fun generateBaselineProfile() {
        rule.collect(
            packageName = "com.example.app",
            includeInStartupProfile = true
        ) {
            // Define critical cold start user journey:
            pressHome()
            startActivityAndWait()

            // Scroll the main feed to capture critical list rendering and viewholder code paths:
            device.findObject(By.res("com.example.app", "feed_list"))
                ?.fling(Direction.DOWN)
        }
    }
}
```
Once the test runs on a physical device running Android 7.0+ (API 24+), Macrobenchmark outputs `baseline-prof.txt` containing method descriptors and class signatures. Placing this file into `src/main/baseline-prof.txt` of the app module ensures that Android Gradle Plugin (AGP) compiles it into binary format. To verify the performance gain, write a companion Macrobenchmark test using `CompilationMode.None` versus `CompilationMode.Partial(BaselineProfileMode.Require)` to objectively measure startup time and frame render improvements.""",
    "short_en": """Baseline Profiles provide ART with pre-defined compilation rules bundled in the APK, allowing critical startup and scrolling code to be pre-compiled into native machine code at install time instead of running interpreted. Macrobenchmark generates these profiles automatically through UI user journeys and rigorously measures startup and frame latency in release-like builds.""",
    "structured_en": """To begin with, Android Runtime startup latency has historically suffered from the JIT compilation warm-up phase on newly installed or updated applications.
From an architectural standpoint, Baseline Profiles bridge this gap by supplying ART with an explicit manifest of critical classes and methods that must be pre-compiled Ahead-Of-Time (AOT). Bundled directly inside the APK or AAB assets, these profiles enable the device package manager and dex2oat daemon to compile critical execution paths at install time, yielding immediate 20% to 40% improvements in cold start and scrolling smoothness.
In production scenarios, Macrobenchmark operates as the companion measurement and generation engine. Located in an isolated testing module, Macrobenchmark drives end-to-end user journeys using UI Automator while capturing low-level system traces. Its BaselineProfileRule automates the generation of baseline-prof.txt by recording actual class loadings and method invocations during critical app flows like app startup and feed scrolling.
As for boundary management, teams validate Baseline Profile effectiveness by running comparative Macrobenchmark test suites asserting on StartupTimingMetric and FrameTimingMetric, contrasting fully compiled execution against uncompiled baselines to ensure zero regressions in CI pipelines.""",
    "deep_senior_en": """At the low-level platform tier, Android Runtime compilation has evolved across multiple generations. In early Android, Dalvik used pure JIT, while Android 5.0 introduced full Ahead-of-Time dex2oat compilation, which caused agonizingly long app installation times and excessive disk usage. Android 7.0 introduced the PGO (Profile-Guided Optimization) hybrid model, where the JIT compiler identifies hot methods and writes them to a profile file in the app data directory during runtime idle maintenance. However, this meant users experienced slow initial cold starts until the device completed background idle optimization cycles.
Baseline Profiles bypass this multi-day discovery lag by bundling pre-computed PGO profiles created by engineers at build time. When Play Store delivers the app, dex2oat compiles these classes using the speed-profile compilation filter. ART compiles the indexed DEX bytecodes directly into native machine code (`.oat` / `.art` files), eliminating JIT interpretation overhead, class loading delays, and dexopt lock contention during the first frame render pass.
Macrobenchmark ensures that profile generation and performance verification are completely reproducible. Running on physical devices or Gradle Managed Devices, Macrobenchmark enforces non-debuggable release builds using the profileable manifest attribute. It clears OS compilation caches using `pm compile` shell commands to establish pristine test environments. By orchestrating repeated iterations of StartupMode.COLD and measuring both Time to Initial Display (TTID) and Time to Full Display (TTFD), Macrobenchmark produces statistically sound metrics alongside deep Perfetto traces.
In large-scale continuous deployment pipelines, senior staff engineers automate Baseline Profile generation as a scheduled workflow. When significant architectural shifts occur—such as migrating to Jetpack Compose or adopting a new dependency graph—the CI pipeline regenerates the profile, runs comparative Macrobenchmark suites, and flags any regression in frame pacing or startup budgets before binary publication.""",
    "metadata_ar": {
        "id": "MEM-18",
        "questionAr": "كيف تساعد الـ Baseline Profiles واختبارات Macrobenchmark في تحسين الأداء؟",
        "topicAr": "إدارة الذاكرة والـ ANR وتحسين الأداء",
        "evaluates_ar": "- فهم آلية عمل مترجم ART ونماذج الـ AOT و JIT والـ Profile-Guided Optimization.\n- كتابة واستخراج الـ Baseline Profiles لتحسين زمن بدء التشغيل وسلاسة القوائم بنسبة 20-40%.\n- تطبيق اختبارات Macrobenchmark للتحقق الإحصائي من مؤشرات الأداء في بيئات الـ CI.",
        "why_it_matters_ar": "نظام Android Runtime (ART) بيعتمد على نموذج هجين يجمع بين الـ JIT والـ AOT Compilation. التطبيق بعد التثبيت أو التحديث بيبدأ بكود غير مترجم (Interpreted)، وده بيسبب بطء ملحوظ في الـ Cold Start وسقوط إطارات في الشاشات الأولى لحد ما النظام يكتشف الكود الساخن (Hot Code) مع الاستخدام المتكرر. الـ Baseline Profiles بتحل المشكلة دي جذرياً؛ لأنها حزمة قواعد نصية بنرفقها مع التطبيق، بتخلي الـ ART يترجم أهم الكلاسات والدوال مسبقاً إلى Native Machine Code وقت التثبيت عبر `dex2oat`. ومكتبة Macrobenchmark هي الأداة الرسمية لتوليد هذه الملفات وقياس تأثيرها الفعلي على أجهزة حقيقية بدقة متناهية.",
        "worked_example_ar": "كتابة اختبار Macrobenchmark لتوليد Baseline Profile واختبار مسار التشغيل الحرج:\n```kotlin\n@RunWith(AndroidJUnit4::class)\nclass BaselineProfileGenerator {\n    @get:Rule\n    val rule = BaselineProfileRule()\n\n    @Test\n    fun generateBaselineProfile() {\n        rule.collect(\n            packageName = \"com.example.app\",\n            includeInStartupProfile = true\n        ) {\n            pressHome()\n            startActivityAndWait()\n\n            device.findObject(By.res(\"com.example.app\", \"feed_list\"))\n                ?.fling(Direction.DOWN)\n        }\n    }\n}\n```\nالملف الناتج `baseline-prof.txt` بيتحط في موديول التطبيق الرئيسي ويتم دمجه تلقائياً مع الـ AAB.",
        "trade_offs_ar": "إضافة Baseline Profiles بتحسن زمن التشغيل وسلاسة السكرول بنسبة تصل إلى 40% بدون أي تعديل في كود الـ Business Logic. لكن تضمين ملف بروفايل ضخم جداً بدون داعٍ بيزيد من حجم الـ APK ومساحة الـ Storage المحجوزة للكود المترجم على جهاز المستخدم، بالإضافة لزيادة وقت التثبيت. القرار الهندسي الصح هو حصر البروفايل في المسارات الحرجة فقط: رحلة بدء التشغيل والشاشة الرئيسية وأول قائمة يتفاعل معها العميل.",
        "failure_modes_ar": "توليد البروفايل على بيئة Debuggable أو محاكي Emulator غير دقيق بيطلع ملف قواعد مشوه وغير متطابق مع بيئة الإنتاج. خطأ آخر هو نسيان اختبار الشاشات الرئيسية أثناء جمع البروفايل، فيتم تسريع الـ Splash Screen فقط وتظل القوائم تعاني من الـ Jank. كما أن عدم التحقق بمقارنة أرقام `CompilationMode.None` مقابل `CompilationMode.Partial` في Macrobenchmark يترك المهندس بدون دليل رقمي يثبت فاعلية البروفايل.",
        "production_perspective_ar": "في الشركات الكبيرة، بنضيف خطوة أتمتة في الـ CI لتشغيل Macrobenchmark دورياً على Gradle Managed Devices حقيقية. بنقارن أزمنة الـ StartupTimingMetric وسرعة الـ FrameTimingMetric، ونمنع إطلاق أي تحديث رئيسي إلا بعد إعادة توليد الـ Baseline Profile والتأكد من عدم وجود أي تراجع في أزمنة الإطارات.",
        "how_to_answer_ar": "- **البداية بالمشكلة:** وضح بطء الـ Cold Start بسبب عمل ART بأسلوب JIT بعد التثبيت مباشرة.\n- **شرح الحل:** بيّن كيف تتيح Baseline Profiles الترجمة المسبقة (AOT) لأهم الكود وقت التثبيت.\n- **دور Macrobenchmark:** اشرح كيفية توليد الملف وقياس أزمنة التشغيل على أجهزة حقيقية.\n- **المفاضلة:** اذكر زيادة حجم التخزين مقابل مكسب السرعة وضرورة التركيز على المسارات الحرجة.\n- **حل الإنتاج:** وضح إدماج الاختبارات في الـ CI للتحقق الإحصائي من التحسن.",
        "talking_points_ar": "اشرح مسار تطور مترجم ART من Dalvik إلى dex2oat والـ PGO، وفلاتر الترجمة speed-profile مقابل speed، وآلية عمل Cloud Profiles على Google Play، وكيفية تكامل BaselineProfileRule مع UI Automator، وقياس TTID و TTFD في Macrobenchmark.",
        "follow_ups_ar": "- **المحاور:** \"ما الفرق بين الـ Cloud Profiles والـ Baseline Profiles؟\"\n  **المرشح:** \"الـ Cloud Profiles بتجمعها جوجل تلقائياً من أجهزة المستخدمين بعد تشغيل التطبيق وتوزعها مع التحديثات، لكنها بتحتاج أيام أو أسابيع لحد ما تتكون، أما الـ Baseline Profiles فالمطور بيبنيها بنفسه وبيرفقها داخل الـ APK فبتشتغل فوراً من أول لحظة تشغيل حتى لأول مستخدم ينزل التطبيق.\"\n\n- **المحاور:** \"ليه بنحط اختبارات Macrobenchmark في موديول منفصل عن موديول التطبيق؟\"\n  **المرشح:** \"لأن Macrobenchmark بتتحكم في التطبيق من الخارج كعملية منفصلة باستخدام UI Automator، وبتقيس الـ Release build الفعلي بدون وجود أي كود اختبارات مشوه للـ Memory أو الـ Class Loading داخل التطبيق نفسه.\"",
        "self_check_ar": "اشرح دورة ترجمة ART؛ وضح آلية Baseline Profiles؛ قس الأثر باستخدام Macrobenchmark؛ وحدد مسارات الاستخدام الحرجة.",
        "references_ar": "- [Baseline Profiles overview](https://developer.android.com/topic/performance/baselineprofiles/overview) — آلية عمل وتوليد ملفات البروفايل.\n- [Macrobenchmark overview](https://developer.android.com/topic/performance/benchmarking/macrobenchmark-overview) — فحص رحلات المستخدم وقياس الأداء.\n- [Measure Baseline Profiles](https://developer.android.com/topic/performance/baselineprofiles/measure-baselineprofile) — مقارنة الأداء قبل وبعد تطبيق البروفايل.\n\nتمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13.",
        "quick_answer_ar": "الـ Baseline Profiles هي قواعد بتدمج في التطبيق بتخلي مترجم ART يترجم أهم الكلاسات مسبقاً (Ahead-of-Time) وقت التثبيت بدلاً من الانتظار لترجمتها بالـ JIT أثناء التشغيل. ومكتبة Macrobenchmark بتولد القواعد دي تلقائياً عن طريق محاكاة رحلات المستخدم الحقيقية، وبتقيس زمن بدء التشغيل وسلاسة الإطارات للتأكد من تسريع التطبيق بنسبة تصل لـ 40%.",
        "best_answer_ar": """تعتبر الـ Baseline Profiles من أهم النقلات النوعية في تحسين أداء تطبيقات أندرويد الحديثة.

الفكرة إن الـ Android Runtime (ART) بطبيعته بيعتمد على JIT compiler بعد التثبيت، فبيشغل الكود بنمط Interpreted لحد ما يكتشف الـ Hot Paths، وده اللي كان بيخلي أول فتح للتطبيق بعد التنزيل أو التحديث بطيء ومليان تقطيع.

الـ Baseline Profiles بتمكننا من تحديد الكود الحرج ده مسبقاً ونرفقه داخل ملف الـ APK. لما المستخدم يثبت التطبيق، نظام الـ OS بيستخدم `dex2oat` لترجمة الكلاسات دي مسبقاً لـ Native Code، وده بيحقق تحسن فوري في الـ Cold Start وسلاسة التمرير بنسبة بتوصل لـ 30-40%.

وعشان نعمل ده باحترافية، بنستخدم مكتبة Jetpack Macrobenchmark في موديول منفصل؛ بنكتب اختبار بيحاكي فتح التطبيق وعمل سكرول في الشاشة الرئيسية، والأداة بتولد ملف `baseline-prof.txt` بدقة.

بنفس الأداة بنقيس الأداء بمقارنة أزمنة التشغيل قبل وبعد البروفايل للتأكد من فاعلية التحسين بالأرقام.""",
        "deep_answer_ar": """على مستوى هندسة الـ Android Runtime المنخفضة، ART بيعتمد على مفهوم Profile-Guided Optimization (PGO). في أندرويد 7.0 وما بعده، الـ JIT Compiler بيراقب تنفيذ الكود، ولما التطبيق يكون في وضع الخمول أثناء الشحن، خدمة dexopt بتترجم الدوال الأكثر تكراراً عبر فلتر `speed-profile`. المشكلة إن المستخدمين بيتحملوا بطء التطبيق في الأيام الأولى لحد ما تكتمل الدورة دي.

الـ Baseline Profiles بتلغي فترة الانتظار دي تماماً؛ لأنها بتسلم الـ Package Manager والـ dex2oat ملف البروفايل جاهز لحظة التثبيت. الأداة بتسجل بصمات الـ DEX Method IDs والـ Class Descriptors في صيغة ثنائية خفيفة. ولما التطبيق يتثبت، الـ ART بيعمل Ahead-Of-Time (AOT) Compilation للنقاط دي بالتحديد، فبيقلل زمن الـ Class Loading والـ Verification وكسر الـ Bytecode في أول إطار.

مكتبة Macrobenchmark بتعتمد على أجهزة حقيقية وبترن على نسخ Release بتفعيل خاصية Profileable. الأداة بتستخدم أوامر Shell منخفضة لإفراغ الـ Caches، وبعدها بتشغل رحلات المستخدم عبر UI Automator وتسجل تفاصيل الـ StartupTimingMetric بدقة متناهية.

في معمارية التطبيقات الكبرى، بنعتمد على تقريرين رئيسيين: Time to Initial Display (TTID) اللي بيعبر عن ظهور أول إطار عبر ActivityRecord، و Time to Full Display (TTFD) اللي بيسجله استدعاء `reportFullyDrawn()`.

بنربط توليد الـ Baseline Profiles بـ CI Pipeline آلي بيفحص أي تغييرات معمارية (زي التحول لـ Compose)، وبنضمن إن التطبيق نازل للمتجر ومعه أقصى درجات التحسين الممكنة."""
    }
}

DATA["MEM-19"] = {
    "concept_en": """Android defines three distinct application launch states characterized by system process availability, Activity back stack residency, and initialization cost. A Cold Start occurs when the application process does not exist in Linux memory (for example, on first launch after device reboot, after the user force-stops the app, or after the OS kills the process due to memory pressure). In a cold start, the OS must fork a new process from Zygote, initialize the Android Runtime, load DEX bytecodes, invoke ContentProviders declared in the manifest, instantiate the Application class and execute `Application.onCreate()`, instantiate the entry Activity, inflate the view hierarchy or invoke initial Composable functions, perform measure and layout passes, and draw the initial frame to the screen. A Warm Start occurs when the application process is already resident in memory, but the target Activity must be re-created from scratch (such as when the system killed the Activity to reclaim memory while the user was in another app, or when the user navigates back to the app with a recreation intent). Warm starts bypass Zygote process creation and `Application.onCreate()`, but still incur Activity creation, dependency injection, and UI inflation overhead. A Hot Start occurs when both the application process and the Activity instance are already resident in memory and the activity is simply brought to the foreground from the back stack. The system only needs to invoke `onRestart()`, `onStart()`, and `onResume()`, rendering the existing view tree with zero inflation or process initialization latency.""",
    "walkthrough_en": """Measuring real startup readiness using `reportFullyDrawn()`:
```kotlin
class MainActivity : AppCompatActivity() {
    private val viewModel: MainViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        lifecycleScope.launch {
            viewModel.uiState.collect { state ->
                if (state is UiState.Success) {
                    renderData(state.data)
                    // Signals to the OS and Play Vitals that all critical asynchronous content is rendered:
                    // This completes the Time to Full Display (TTFD) benchmark:
                    reportFullyDrawn()
                }
            }
        }
    }
}
```
In this implementation, the system logs two critical launch milestones in Logcat: the initial frame display (`Displayed com.example.app/.MainActivity: +450ms`, representing Time to Initial Display or TTID) and the full data render (`Fully drawn com.example.app/.MainActivity: +920ms`, representing Time to Full Display or TTFD). Calling `reportFullyDrawn()` ensures that automated Macrobenchmark suites and Google Play Console Android Vitals record true usable startup performance rather than measuring an empty loading skeleton.""",
    "short_en": """A Cold Start creates a new Linux process from Zygote, executing Application and Activity initialization from scratch. A Warm Start reuses an existing app process but must recreate the Activity and inflate its UI. A Hot Start brings an existing, resident Activity from the background back to the foreground, requiring only lifecycle resumption callbacks.""",
    "structured_en": """To begin with, understanding Android launch states is essential for diagnosing startup latency and setting realistic performance budgets.
From an architectural standpoint, a Cold Start is the most expensive state because no process exists in memory. The operating system must fork a new process from Zygote, initialize the Android Runtime, execute ContentProviders, run `Application.onCreate()`, instantiate the launch Activity, inflate the view tree, and render the first frame.
In production scenarios, a Warm Start represents a partial launch lifecycle. The Linux process and Application singleton are already resident in memory, but the target Activity was destroyed and must be recreated. While this bypasses process initialization, it still incurs Activity creation, dependency injection, and layout inflation latency.
As for boundary management, a Hot Start is the fastest launch condition because both the process and the Activity instance remain intact in memory. The system simply brings the Activity window to the foreground, invoking `onStart()` and `onResume()`.
Optimizing startup requires separating Time to Initial Display from Time to Full Display by deferring non-essential initialization and calling `reportFullyDrawn()` once interactive data is rendered.""",
    "deep_senior_en": """At the Linux kernel and platform runtime layer, a Cold Start initiates with an IPC Binder transaction to `ActivityManagerService` (or `ActivityTaskManagerService` in modern Android). AMS communicates with the Zygote daemon via a local Unix domain socket, requesting a fork of the zygote process. Because Zygote has pre-loaded core framework classes and pre-warmed graphics assets, the forked process inherits clean memory pages via copy-on-write (COW). Once forked, the process initializes the `ActivityThread`, creates the Main Looper, and invokes `LoadedApk.makeApplication()`.
Crucially, all ContentProviders declared in the AndroidManifest are initialized sequentially on the Main Thread prior to `Application.onCreate()`. In modern modularized codebases, third-party SDKs frequently exploit empty ContentProviders for zero-code auto-initialization, severely degrading cold start times before a single line of app code executes. This makes the Jetpack App Startup library vital for coalescing multiple initializers into a single component.
Measuring cold launch latency requires distinguishing between TTID and TTFD. Time to Initial Display represents the duration from process launch until SurfaceFlinger presents the very first frame (often a placeholder, theme window background, or skeleton screen). Time to Full Display, triggered by `Activity.reportFullyDrawn()`, measures when asynchronous data fetching and UI population conclude, giving the user an interactive surface. Android Vitals enforces a bad behavior threshold of 5 seconds for cold start and 2 seconds for warm start.
Senior staff engineers audit cold starts using Perfetto System Traces and Macrobenchmark with `StartupMode.COLD`. In the trace, we inspect thread slices between `bindApplication` and the first `Choreographer.doFrame`. Any class loading spikes, synchronized disk reads, or Dagger/Hilt dependency graph instantiations during this window are prioritized for lazy initialization or background coroutine dispatch.""",
    "metadata_ar": {
        "id": "MEM-19",
        "questionAr": "ما هي حالات بدء التشغيل: Cold start و Warm start و Hot start؟ وكيف نقيسها؟",
        "topicAr": "إدارة الذاكرة والـ ANR وتحسين الأداء",
        "evaluates_ar": "- التمييز المعماري الدقيق بين حالات التشغيل الثلاث ومسؤوليات النظام في كل حالة.\n- فهم تسلسل التهيئة من شوكة Zygote والـ ContentProviders حتى استدعاء `Application.onCreate`.\n- قياس أزمنة التشغيل والتفريق بين Time to Initial Display (TTID) و Time to Full Display (TTFD) واستخدام `reportFullyDrawn()`.",
        "why_it_matters_ar": "حالات بدء التشغيل بتمثل الانطباع الأول للمستخدم عن جودة وسرعة التطبيق. الـ Cold Start هو الأثقل والأعلى استهلاكاً للموارد لأن النظام بيضطر ينشئ Process جديد تماماً من Zygote، ويحمل كلاسات الـ DEX، ويهيئ الـ ContentProviders والـ Application class، قبل إنشاء الـ Activity وبناء واجهتها. الـ Warm Start بيحصل لما تكون العملية عايشة في الذاكرة لكن الـ Activity اتدمرت ومحتاجة إعادة بناء. أما الـ Hot Start فالعملية والـ Activity موجودين بالفعل وكل اللي بيحصل هو إعادة الشاشة للواجهة عبر `onResume`. فهم الفروق دي حاسم لتحديد مكان عنق الزجاجة وتفادي تخطي عتبات Google Play Vitals.",
        "worked_example_ar": "استدعاء `reportFullyDrawn()` لقياس اكتمال التحميل الحقيقي للواجهة (Time to Full Display):\n```kotlin\nclass MainActivity : AppCompatActivity() {\n    private val viewModel: MainViewModel by viewModels()\n\n    override fun onCreate(savedInstanceState: Bundle?) {\n        super.onCreate(savedInstanceState)\n        setContentView(R.layout.activity_main)\n\n        lifecycleScope.launch {\n            viewModel.uiState.collect { state ->\n                if (state is UiState.Success) {\n                    renderData(state.data)\n                    reportFullyDrawn()\n                }\n            }\n        }\n    }\n}\n```\nالاستدعاء ده بيسجل في Logcat زمن TTFD بدقة ويمنح Android Vitals و Macrobenchmark التوقيت الفعلي لاكتمال تحميل البيانات.",
        "trade_offs_ar": "عرض واجهة Splash Screen خفيفة أو شاشة هيكلية (Skeleton) بيحقق زمن TTID سريع جداً وبيعطي انطباع فوري بالاستجابة، لكنه لا يعني جاهزية التطبيق للاستخدام. إذا كان الكود بيعمل عمليات جلب شبكة ثقيلة بعد الفتح مباشرة بدون كاش محلي، المستخدم هيفضل ينتظر زمناً طويلاً. القرار الهندسي السليم هو الموازنة بين تقليل مهام الـ Application.onCreate وعرض واجهة مبدئية سريعة مع قراءة كاش محلي فوري واستدعاء `reportFullyDrawn` بمجرد اكتمال البيانات الأساسية.",
        "failure_modes_ar": "أكبر خطأ هو حشو دالة `Application.onCreate()` بتهيئة متزامنة لجميع مكتبات الـ SDKs (التحليلات، الإعلانات، خدمات التتبع)، مما يرفع زمن الـ Cold Start لعدة ثوانٍ ويؤدي لتسجيل مخالفات في Android Vitals. خطأ آخر هو الاعتماد على ContentProviders مخفية من مكتبات خارجية لتهيئة نفسها تلقائياً قبل تشغيل Application.onCreate دون علم المطور. كما أن استدعاء `reportFullyDrawn()` مبكراً جداً قبل تحميل البيانات الفعلية يعطي أرقاماً وهمية ويخفي بطء التطبيق الحقيقي.",
        "production_perspective_ar": "في بيئات الإنتاج، بنراقب نسبة الـ Cold Start البطيئة (أكثر من 5 ثوانٍ) والـ Warm Start (أكثر من ثانيتين) عبر Google Play Console. بنستخدم Jetpack App Startup لتجميع تهيئة المكتبات والـ SDKs في مسار واحد، ونؤجل تهيئة الأدوات غير الحرجة إلى Background Coroutine بعد ظهور الشاشة الأولى.",
        "how_to_answer_ar": "- **التعريف بالترتيب:** ابدأ بشرح الحالات الثلاث من الأثقل (Cold) إلى الأسرع (Hot).\n- **تشريح دورة الـ Cold:** اذكر Zygote fork، و ContentProviders، و Application.onCreate، و Activity lifecycle.\n- **القياس المعياري:** وضّح الفرق بين TTID (أول إطار) و TTFD (البيانات الكاملة) ودور `reportFullyDrawn()`.\n- **سيناريو الفشل:** حذر من التهيئة المتزامنة للـ SDKs في Application class.\n- **حل الإنتاج:** اشرح مكتبة App Startup والتهيئة الكسولة واستخدام Macrobenchmark.",
        "talking_points_ar": "ناقش Zygote copy-on-write، ودور ContentProviders في التمهيد قبل onCreate، والفرق بين TTID و TTFD، واستدعاء reportFullyDrawn، وعتبات Android Vitals للتشغيل، واستخدام StartupTimingMetric في Macrobenchmark.",
        "follow_ups_ar": "- **المحاور:** \"لماذا تبدأ الـ ContentProviders بالعمل قبل دالة `Application.onCreate()`؟\"\n  **المرشح:** \"لأن نظام أندرويد صمم ContentProviders كنقاط دخول لمشاركة البيانات بين العمليات، فبيحتاج يهيئها مبكراً جداً في دورة حياة الـ Process؛ ولهذا السبب مكتبات زي Firebase بتستخدم Empty ContentProvider للتهيئة التلقائية بدون كود، وده لو زاد عن حده بيبطئ الـ Cold Start.\"\n\n- **المحاور:** \"ما الفارق بين TTID و TTFD في قياس تجربة المستخدم؟\"\n  **المرشح:** \"الـ TTID هو وقت ظهور أول بكسل أو واجهة هيكلية على الشاشة، أما الـ TTFD فهو الوقت اللي بيستغرقه التطبيق لحد ما يعرض المحتوى الحقيقي ويكون جاهز لتفاعل المستخدم، وهو المقياس الأكثر صدقاً لتجربة المستخدم الفعلية.\"",
        "self_check_ar": "ميز بين حالات التشغيل الثلاث؛ اشرح تسلسل التهيئة في الـ Cold Start؛ واستدع `reportFullyDrawn()` لقياس الـ TTFD بدقة.",
        "references_ar": "- [App startup time](https://developer.android.com/topic/performance/issues/launch-time) — تعريفات ومراحل Cold و Warm و Hot start.\n- [Macrobenchmark overview](https://developer.android.com/topic/performance/benchmarking/macrobenchmark-overview) — قياس أزمنة StartupMode بدقة.\n\nتمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13.",
        "quick_answer_ar": "الـ Cold Start بيحصل لما التطبيق يبدأ من الصفر بدون عملية حية في الذاكرة، فالنظام بينشئ Process جديد ويهيئ الـ Application والـ Activity من البداية. الـ Warm Start بيحصل لما تكون العملية موجودة في الذاكرة ولكن الـ Activity محتاجة إعادة بناء. أما الـ Hot Start فالعملية والـ Activity موجودين بالكامل وكل اللي بيحصل هو استعادة الشاشة للواجهة عبر onResume.",
        "best_answer_ar": """في أندرويد، بنصنف تشغيل التطبيق لثلاث حالات بتحددها حالة الـ Process والـ Activity في الذاكرة.

الـ Cold Start هو الأثقل لأن التطبيق ملوش أي وجود في الذاكرة؛ النظام بيبدأ بطلب fork لـ Linux process جديد من Zygote، ويحمل الـ DEX files، ويشغل الـ ContentProviders، وبعدين يستدعي `Application.onCreate()`، وأخيراً ينشئ الـ Activity ويعمل Measure و Layout ويرسم أول إطار.

الـ Warm Start بيكون أسرع لأن الـ Process والـ Application class موجودين بالفعل في الذاكرة، لكن الـ Activity اتدمرت ومحتاجة تتبني من جديد وتعمل Inflation للواجهة.

الـ Hot Start هو الأسرع على الإطلاق لأن الـ Activity والـ Process الاتنين لسه في الذاكرة؛ النظام مجرد بيجيب الشاشة للواجهة عبر `onStart` و `onResume` بدون أي إعادة بناء.

من الناحية الهندسية، بنقيس الأداء بمؤشرين: TTID لسرعة ظهور أول إطار، و TTFD اللي بنعلنه عبر استدعاء `reportFullyDrawn()` لما البيانات الحقيقية تكتمل، وبنراقب ده في Android Vitals عشان نضمن عدم تجاوز الـ 5 ثوانٍ في الـ Cold Start.""",
        "deep_answer_ar": """على مستوى نظام التشغيل والـ Linux Kernel، الـ Cold Start بيبدأ لما الـ ActivityManagerService (AMS) يتواصل مع سيرفر Zygote عبر Unix Domain Socket. عملية الـ Fork بتستفيد من آلية Copy-On-Write لمشاركة كلاسات الفريموورك المحملة مسبقاً في الذاكرة. بعد الـ Fork، الـ ActivityThread بيبدأ الـ Main Looper، ويستدعي `bindApplication`.

نقطة حاسمة بيغفل عنها كتير من المطورين هي إن جميع الـ ContentProviders المعرفة في الـ AndroidManifest بتتنفذ دوال `onCreate` بتاعتها على الـ Main Thread قبل استدعاء `Application.onCreate`! في المشاريع الكبيرة، وجود 5 أو 6 مكتبات بتستخدم Providers للتهيئة التلقائية بيستهلك مئات المللي ثواني من ميزانية الإقلاع قبل تشغيل أول سطر كود من التطبيق.

عشان كده بنلجأ لمكتبة Jetpack App Startup اللي بتدمج كل التهيئة دي في Provider واحد، وبنفرز الـ SDKs؛ الأدوات الحرجة بس زي Crashlytics بتفضل في الـ Main Thread، وباقي الأدوات بنرحلها لـ Background Coroutine.

في قياس الإنتاج، Google Play بتراقب عتبات صارمة جداً في Android Vitals: التطبيق بيعتبر ذو أداء سيئ لو تجاوز 5 ثوانٍ في الـ Cold Start أو ثانيتين في الـ Warm Start.

باستخدام Macrobenchmark و Perfetto، بنفحص خط الـ StartupTimingMetric، وبنتأكد إن المطورين بيستدعوا `reportFullyDrawn()` بمجرد ما الـ ViewModel يستلم البيانات من الـ Repository، وده بيدينا مقياس حقيقي لـ Time to Full Display (TTFD) بعيداً عن مجرد عرض شاشة بيضاء أو Shimmer Skeleton فارغ."""
    }
}

DATA["MEM-20"] = {
    "concept_en": """Memory caches and large scrollable lists are the two most common architectural sites of memory bloat, allocation churn, and performance regressions in Android applications. An unconstrained in-memory cache—such as a static HashMap, an unbounded LRU cache, or a cache retaining heavy objects like decoded Bitmaps or database entities—grows monotonically over time. Without strict byte-bounded ceilings and eviction policies, the cache exhausts available heap space, provoking frequent Concurrent Copying GC pauses and ultimately forcing Low Memory Killer (LMK) terminations. In large lists (rendered via RecyclerView or Jetpack Compose LazyColumn), performance regressions occur when item views or composables violate recycling contracts. Allocating heavy temporary objects (such as DateFormatters, JSON parsers, lambda instances, or raw bitmap decodes) inside `onBindViewHolder` or within composable item bodies causes allocation spikes with every fling gesture. Furthermore, if list items retain references to outer scopes, Activity contexts, or Coroutine jobs that outlive the visible window, off-screen items cannot be reclaimed. Sustainable memory architectures enforce bounded LRU caches that measure size in bytes (e.g. `Bitmap.allocationByteCount`) rather than item counts, register with `ComponentCallbacks2` to evict entries during system memory pressure events (`onTrimMemory`), and employ Jetpack Paging 3 to window large datasets into memory-bounded pages.""",
    "walkthrough_en": """Building a memory-bounded cache that honors system memory pressure:
```kotlin
class MemoryBoundedImageCache(maxMemoryInBytes: Int) : ComponentCallbacks2 {
    private val cache = object : LruCache<String, Bitmap>(maxMemoryInBytes) {
        override fun sizeOf(key: String, value: Bitmap): Int {
            // Measure exact memory footprint in bytes rather than item count:
            return value.allocationByteCount
        }
    }

    fun get(key: String): Bitmap? = cache.get(key)
    fun put(key: String, bitmap: Bitmap) { cache.put(key, bitmap) }

    override fun onTrimMemory(level: Int) {
        if (level >= ComponentCallbacks2.TRIM_MEMORY_RUNNING_LOW) {
            // Evict all cached bitmaps when the device experiences severe memory pressure:
            cache.evictAll()
        } else if (level >= ComponentCallbacks2.TRIM_MEMORY_BACKGROUND) {
            // Evict half the cache when the app is backgrounded to avoid LMK termination:
            cache.trimToSize(cache.maxSize() / 2)
        }
    }

    override fun onConfigurationChanged(newConfig: Configuration) {}
    override fun onLowMemory() { cache.evictAll() }
}
```
In this implementation, the `LruCache` overrides `sizeOf` to measure `Bitmap.allocationByteCount`, preventing a scenario where a few high-resolution images consume hundreds of megabytes while remaining under a simplistic item-count threshold. By implementing `ComponentCallbacks2`, the cache listens to OS memory notifications. When `onTrimMemory` reports `TRIM_MEMORY_RUNNING_LOW`, the cache purges entries, relieving process RSS and preventing the Linux kernel from killing the app process.""",
    "short_en": """Unbounded caches and poorly optimized lists cause memory regressions by retaining large object graphs and generating allocation churn during scrolling. Caches must enforce byte-bounded limits rather than item counts and respond to `onTrimMemory()` events. Large lists must reuse views or composables, avoid allocations inside binding passes, and window datasets using Paging 3.""",
    "structured_en": """To begin with, memory caches and long scrollable lists represent the most common vectors for memory exhaustion and frame drop regressions in mobile applications.
From an architectural standpoint, an improperly configured cache behaves like a managed memory leak. When developers use unbounded maps or configure an `LruCache` based on entry count rather than byte allocation, a small collection of high-resolution bitmaps can consume tens of megabytes, exhausting available heap limits and triggering aggressive garbage collection cycles.
In production scenarios involving large lists, performance degradation typically stems from allocation churn during scroll gestures. If `onBindViewHolder` in RecyclerView or an item composable in LazyColumn repeatedly instantiates formatters, complex data structures, or lambda closures, the Android Runtime is flooded with short-lived objects. This allocation surge induces frequent Concurrent Copying GC passes, resulting in noticeable UI stutter and dropped frames.
As for boundary management, resilient architectures enforce two core safeguards. First, all memory caches must measure byte size and implement `ComponentCallbacks2.onTrimMemory` to evict entries when the operating system signals memory pressure. Second, large datasets must be paginated into memory using Jetpack Paging 3, ensuring that only visible and prefetch-windowed items reside in memory.""",
    "deep_senior_en": """At the platform runtime and kernel layer, memory pressure is mediated through the Low Memory Killer daemon (LMKD) and ART garbage collection ergonomics. In ART, allocating objects at high velocity during list fling gestures rapidly fills the bump allocator nursery space, forcing the runtime to invoke Concurrent Copying (CC) GC cycles. Although CC GC avoids full-process stop-the-world pauses, it still incurs brief thread suspension intervals and thread contention, stealing critical milliseconds from the Choreographer rendering budget and manifesting as UI jank.
When an in-memory cache lacks explicit byte limits, process Resident Set Size (RSS) balloons. In low-RAM devices, the Linux kernel monitors memory pressure through Pressure Stall Information (PSI). When memory thresholds are breached, LMKD evaluates process OOM scores (oom_score_adj). If our application is cached or in the background and holding onto an unevicted 100MB bitmap cache, its high RSS makes it the prime candidate for immediate process termination.
To mitigate this, production caches must register with `Application.registerComponentCallbacks()`. In `onTrimMemory(level)`, engineers handle tiered levels: `TRIM_MEMORY_RUNNING_LOW` requires immediate cache eviction, while `TRIM_MEMORY_UI_HIDDEN` indicates that the user navigated away from the UI, warranting a partial cache trim to keep the process alive in the background.
For large lists, senior engineers audit RecyclerView view holders and Jetpack Compose LazyLists to ensure zero allocations during scroll passes. Date formatters, currency formatters, and click listeners must be hoisted or remembered outside item scopes. Furthermore, using Jetpack Paging 3 guarantees that off-screen pages are reclaimed and that only an optimal window of items remains reachable from the UI state holder, eliminating memory regressions across endless scroll feeds.""",
    "metadata_ar": {
        "id": "MEM-20",
        "questionAr": "كيف يؤدي تصميم الكاش والقوائم الكبيرة لتسريبات الذاكرة وتراجع الأداء؟",
        "topicAr": "إدارة الذاكرة والـ ANR وتحسين الأداء",
        "evaluates_ar": "- تصميم كاش محكوم بالحجم الفعلي بالبايت (Byte-bounded) بدلاً من عدد العناصر.\n- الاستجابة لإشارات النظام لضغط الذاكرة عبر `ComponentCallbacks2.onTrimMemory`.\n- تجنب الـ Allocation Churn داخل دوال التمرير في RecyclerView و Compose LazyColumn وتطبيق Paging 3.",
        "why_it_matters_ar": "الكاش غير المنضبط والقوائم الطويلة بيمثلوا أكبر بؤرتين لتسريب الذاكرة وهبوط الإطارات في تطبيقات أندرويد. وجود كاش غير محكوم بحجم أقصى بالبايت بيخلي الذاكرة تتضخم تدريجياً لحد ما تفجر OutOfMemoryError أو تخلي التطبيق هدفاً سهلاً للقتل بواسطة Low Memory Killer (LMK). وفي القوائم، تكرار حجز كائنات مؤقتة (زي Formatters أو Lambdas أو Bitmaps) داخل دوال التمرير والربط `onBindViewHolder` بيعمل ضغط هائل على الـ Garbage Collector (GC Churn) وبيسبب تقطيعاً مستمراً في الإطارات.",
        "worked_example_ar": "تصميم LruCache محكوم بالذاكرة بالبايت مع الاستجابة لـ onTrimMemory:\n```kotlin\nclass MemoryBoundedImageCache(maxMemoryInBytes: Int) : ComponentCallbacks2 {\n    private val cache = object : LruCache<String, Bitmap>(maxMemoryInBytes) {\n        override fun sizeOf(key: String, value: Bitmap): Int {\n            return value.allocationByteCount\n        }\n    }\n\n    fun get(key: String): Bitmap? = cache.get(key)\n    fun put(key: String, bitmap: Bitmap) { cache.put(key, bitmap) }\n\n    override fun onTrimMemory(level: Int) {\n        if (level >= ComponentCallbacks2.TRIM_MEMORY_RUNNING_LOW) {\n            cache.evictAll()\n        } else if (level >= ComponentCallbacks2.TRIM_MEMORY_BACKGROUND) {\n            cache.trimToSize(cache.maxSize() / 2)\n        }\n    }\n\n    override fun onConfigurationChanged(newConfig: Configuration) {}\n    override fun onLowMemory() { cache.evictAll() }\n}\n```",
        "trade_offs_ar": "زيادة حجم الكاش في الذاكرة بيسرع عرض البيانات ويقلل استهلاك الشبكة، لكنه بيستهلك الـ RAM وبيعرض التطبيق للقتل عند الانتقال للخلفية. صغر حجم الكاش بيحمي الذاكرة لكنه بيزيد من استهلاك البطارية والشبكة نتيجة إعادة تحميل البيانات باستمرار. الحل الهندسي هو ربط حجم الكاش بنسبة مئوية من الذاكرة المتاحة (مثل 15% من Max Heap) وتفريغه استجابةً لـ onTrimMemory.",
        "failure_modes_ar": "استخدام `HashMap` عادية أو كاش يعتمد على عدد العناصر (Item Count) بدلاً من حجم البايت؛ فخمس صور عالية الدقة قد تستهلك 100MB وتفجر الذاكرة رغم أن عددها قليل. خطأ آخر هو حجز كائنات جديدة داخل `onBindViewHolder` أو داخل جسم الـ Composable في القائمة مع كل بكسل سكرول، مما يدخل المعالج في دوامة GC Churn مستمرة ويسبب سقوط إطارات كارثي.",
        "production_perspective_ar": "في التطبيقات الضخمة، بنعتمد على مكتبة Jetpack Paging 3 لتقسيم القوائم الطويلة لصفحات محكومة بالذاكرة، وبنلزم المطورين بعدم إنشاء أي كائنات مؤقتة في الـ ViewHolders عبر قواعد Lint صارمة. وبنراقب معدلات الـ OOM ومستويات ضغط الذاكرة في الإنتاج لضبط أحجام الكاش تلقائياً حسب فئة الجهاز (Low-end vs High-end).",
        "how_to_answer_ar": "- **البداية بالسببين:** حدد أن المشكلة تنقسم لكاش غير مقيد يلتهم الذاكرة، وقوائم غير منضبطة تولد GC Churn.\n- **هندسة الكاش:** اشرح حساب الحجم بالبايت (`allocationByteCount`) والاستجابة لـ `onTrimMemory`.\n- **هندسة القوائم:** وضح تفادي الحجز المتكرر داخل `onBindViewHolder` واستخدام Paging 3.\n- **المفاضلة:** قارن بين سرعة الكاش ومخاطر الـ OOM Killer.\n- **حل الإنتاج:** اذكر تقسيم الذاكرة كنسبة مئوية واستخدام أدوات المراقبة.",
        "talking_points_ar": "اشرح آلية عمل LruCache، وقياس allocationByteCount في Bitmaps، ومستويات TRIM_MEMORY_RUNNING_LOW و TRIM_MEMORY_UI_HIDDEN، وتأثير GC Churn على نبضات VSYNC، واستراتيجيات التخزين المؤقت في Jetpack Paging 3.",
        "follow_ups_ar": "- **المحاور:** \"ما الفرق بين `onLowMemory()` و `onTrimMemory(level)`؟\"\n  **المرشح:** \"دالة `onLowMemory()` قديمة وكانت بتنادى فقط لما النظام يوصل لمرحلة حرجة جداً قبل قتل العمليات مباشرة، أما `onTrimMemory(level)` فظهرت في API 14 وبتقدم مستويات تدرجية دقيقة بتسمح للتطبيق بتحرير أجزاء من الذاكرة مبكراً حسب حالة التطبيق (شغال في الواجهة، أو في الخلفية، أو النظام كله تحت ضغط).\"\n\n- **المحاور:** \"كيف تمنع الـ GC Churn أثناء التمرير السريع في قائمة طويلة؟\"\n  **المرشح:** \"بإعادة استخدام الكائنات وتجنب أي حجز لكائنات جديدة داخل `onBindViewHolder` أو الـ Composable item؛ يعني نرفع تعريف الـ DateFormatters والـ Click Listeners خارج دوال الربط، ونستخدم مكتبة صور زي Coil بتعيد تدوير الـ Bitmaps تلقائياً.\"",
        "self_check_ar": "اضبط حجم الكاش بالبايت؛ استجب لـ onTrimMemory؛ امنع الحجز داخل الـ ViewHolders؛ واعتمد على Paging 3 للقوائم الضخمة.",
        "references_ar": "- [Cache bitmaps](https://developer.android.com/topic/performance/graphics/cache-bitmap) — استراتيجيات الكاش المحكوم بالذاكرة.\n- [Paging overview](https://developer.android.com/topic/libraries/architecture/paging/v3-overview) — تقسيم مجموعات البيانات الكبيرة.\n- [Manage app memory](https://developer.android.com/topic/performance/memory/manage-app-memory) — التعامل مع ضغط الذاكرة وإشارات النظام.\n\nتمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13.",
        "quick_answer_ar": "الكاش غير المقيد بحجم البايت بيتسبب في استنزاف الذاكرة تدريجياً وحدوث OOM أو إغلاق التطبيق بواسطة LMK، لذلك يجب تحديد حجمه بالبايت والاستجابة لإشارات onTrimMemory لتفريغه عند ضغط النظام. وفي القوائم الطويلة، تكرار حجز كائنات جديدة داخل دوال الـ Binding بيسبب GC Churn وهبوط إطارات، وحلها هو إعادة استخدام الكائنات وتجزئة البيانات عبر Paging 3.",
        "best_answer_ar": """الكاش والقوائم الطويلة هما أكبر مصدرين لتدهور الذاكرة والأداء لو متصمموش بوعي هندسي دقيق.

في الكاش، الخطأ الشائع هو الاعتماد على عدد العناصر بدل الحجم الفعلي بالبايت؛ فممكن كاش يشيل 20 صورة بس يستهلك أكتر من 100 ميجابايت ويفجر الذاكرة. الحل إننا نستخدم `LruCache` ونعمل Override لدالة `sizeOf` بحيث تقيس الحجم الحقيقي بالبايت عبر `allocationByteCount`.

بالإضافة لكده، الكاش لازم يطبق واجهة `ComponentCallbacks2` ويستمع لـ `onTrimMemory`؛ فأول ما النظام يبعت إشارة ضغط ذاكرة زي `TRIM_MEMORY_RUNNING_LOW`، بنفرغ الكاش فوراً عشان نحمي التطبيق من القتل بواسطة Low Memory Killer.

أما في القوائم الكبيرة سواء في RecyclerView أو Compose LazyColumn، المشكلة الأساسية بتكون الـ Allocation Churn. لما المطورين بيحجزوا كائنات مؤقتة زي DateFormatters أو دوال lambda داخل `onBindViewHolder`، النظام بيغرق في كائنات قصيرة العمر بتجبر الـ GC إنه يشتغل مع كل سكرول ويوقع إطارات.

الحل هو رفع الكائنات دي برة دوال الربط واستخدام Jetpack Paging 3 لتقسيم البيانات على صفحات محكومة الذاكرة.""",
        "deep_answer_ar": """على مستوى الـ Android Runtime والـ Kernel، لما الكاش بيكبر بدون سقف محكوم، الـ Resident Set Size (RSS) للتطبيق بيتضخم. في نظام أندرويد، الـ Low Memory Killer Daemon (LMKD) بيراقب باستمرار مؤشرات ضغط الذاكرة عبر الـ Pressure Stall Information (PSI) في الكيرنل. لو التطبيق نزل في الـ Background وهو محتفظ بكاش صور ضخم، تصنيفه في الـ oom_score_adj بينزل ويكون أول ضحية يتم قتل عمليتها لتحرير الذاكرة للنظام.

عشان كده بنربط الكاش بنسبة مئوية آمنة من الـ Max Heap المتاح (عادة من 10% إلى 15%)، وبنتعامل مع مستويات `onTrimMemory` بدقة: لما التطبيق يروح للخلفية بنستلم `TRIM_MEMORY_UI_HIDDEN`، فبنصغر الكاش للنصف، ولما الضغط يشتد بنفرغه بالكامل.

في القوائم الضخمة، مشكلة الـ GC Churn بتظهر بسبب طريقة عمل الـ Bump Allocator في ART. حجز كائنات مؤقتة سريعة في كل بكسل سكرول بيملأ مساحة الـ Nursery بسرعة، فبيجبر الـ Runtime على تشغيل Concurrent Copying GC متكرر. ورغم إن الـ CC GC بيكون معظمه متزامن بدون توقيف كامل، إلا إنه بيستهلك وقت المعالج وبينافس الـ Main Thread، وده بيضيع نافذة الـ 16.6ms ويسقط إطارات الـ Choreographer.

في الأنظمة المتقدمة، بنمنع أي Object Allocations في مسار الـ Scroll عبر أدوات الـ Lint والـ Profiler، وبنطبق Jetpack Paging 3 مع استراتيجيات Prefetch ذكية بتضمن إن البيانات المحفوظة في الذاكرة تكون مقتصرة فقط على الشاشة الحالية وهوامش التمرير القريبة."""
    }
}
