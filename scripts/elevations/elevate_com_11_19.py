#!/usr/bin/env python3
"""
Elevation script for COM-11 to COM-19 (Jetpack Compose - Batch 2).
Complete bilingual parity, senior conversational spoken style, zero bullet points in spoken text.
"""

import sys
from pathlib import Path

# Add scripts/elevations to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts" / "elevations"))
import elevation_engine as ee

TOPIC_AR = ee.TOPIC_AR_NAMES["COM"]
REVIEWED_DATE_AR = "تمت المراجعة في 17 أكتوبر 2026"

DATA = {}

# ==========================================
# COM-11: Compare LaunchedEffect(Unit) and LaunchedEffect(key).
# ==========================================
DATA["COM-11"] = {
    "concept_en": """LaunchedEffect is a composable effect handler that launches a coroutine scoped to the composition lifecycle. The crucial distinction lies in the key argument passed to it: LaunchedEffect(Unit) or LaunchedEffect(true) uses a constant key, guaranteeing that the coroutine runs exactly once when entering the composition and remains active until the composable leaves the composition tree. In contrast, LaunchedEffect(key) binds the coroutine lifecycle to a dynamic state variable. Whenever key evaluates to a new value via structural equality, Compose immediately cancels the currently executing coroutine job and launches a fresh coroutine with the updated key, ensuring the asynchronous operation stays synchronized with changing parameters.""",
    "walkthrough_en": """Contrasting static LaunchedEffect(Unit) with dynamic LaunchedEffect(key) in a search screen:
```kotlin
// ❌ ANTI-PATTERN: LaunchedEffect(Unit) misses dynamic query updates!
@Composable
fun StaleSearchScreen(query: String, viewModel: SearchViewModel) {
    // Runs ONLY ONCE when first entering composition!
    // When the user types a new query, this coroutine DOES NOT RESTART!
    LaunchedEffect(Unit) {
        viewModel.performSearch(query) // Captures stale initial query!
    }
}

// ✅ BEST PRACTICE: LaunchedEffect(key) cancels and restarts when parameter changes
@Composable
fun ReactiveSearchScreen(query: String, viewModel: SearchViewModel) {
    // Whenever 'query' changes, Compose cancels the previous search coroutine
    // and launches a new one with the updated query!
    LaunchedEffect(query) {
        if (query.isNotBlank()) {
            delay(300) // Built-in debounce mechanism!
            viewModel.performSearch(query)
        }
    }
}
```""",
    "short_en": """LaunchedEffect(Unit) executes its suspending block once when entering composition and only cancels when the composable leaves the composition entirely. In contrast, LaunchedEffect(key) binds coroutine execution to dynamic state. Whenever the key changes, Compose cancels the existing coroutine and restarts a new one with the latest value. Using Unit for dynamic parameters produces stale state bugs, while using a rapidly changing key causes continuous cancellation thrashing.""",
    "structured_en": """Mastering the key semantics of LaunchedEffect is essential for preventing coroutine lifecycle leaks and stale asynchronous operations in Jetpack Compose.
When you pass a constant like Unit or true to LaunchedEffect, you instruct the Compose runtime that the side-effect has no external dynamic dependencies. The runtime allocates the coroutine scope when the composable enters the composition tree and maintains that scope untouched across subsequent recompositions. It only cancels the job when the composable unmounts. This makes LaunchedEffect(Unit) ideal for one-time initialization tasks, such as triggering an initial analytics screen-view beacon or requesting runtime Bluetooth permissions upon screen opening.
However, passing Unit when the coroutine reads a changing parameter is a hazardous anti-pattern that creates stale closures.
If a screen accepts an itemId and you launch your network fetch inside LaunchedEffect(Unit), changing the itemId will never trigger a reload because the key never changes.
Passing LaunchedEffect(itemId) solves this cleanly.
Whenever itemId updates, Compose cancels the running coroutine and starts a new one with the fresh identifier.
If a network call was in flight, its cancellation signal cascades upstream, terminating the active HTTP connection and conserving mobile data.""",
    "deep_senior_en": """Under the hood, LaunchedEffect delegates to the Composer's internal effect management APIs and integrates directly with Kotlin Coroutines cancellation machinery.
When the Compose compiler processes LaunchedEffect, it stores a LaunchedEffectImpl object inside the SlotTable. This object retains the previous key argument and the running Job reference.
During each recomposition pass, the Composer executes an equality comparison between the current key argument and the key stored in the slot using standard structural equality (equals).
If the keys are equal, the Composer skips the effect entirely, allowing the running coroutine job to proceed undisturbed.
If the key has changed, the Composer executes Job.cancel() on the existing coroutine job. This throws a CancellationException inside the coroutine, cleanly canceling any suspending network calls, delay timers, or database transactions.
Once cancellation completes, the Composer launches a brand-new coroutine on the composition's Apply-dispatcher, passing the latest lambda block.
Senior engineers must be cautious with key selection. Passing an unstable object or an object that generates new instances on every recomposition triggers cancellation thrashing, where the coroutine is cancelled and relaunched on every single frame before finishing its work.
Conversely, if an effect reads multiple changing state values, developers should pass multiple keys or a consolidated data holder to ensure complete synchronization.""",
    "meta_ar": {
        "id": "COM-11",
        "questionAr": "قارن بين LaunchedEffect(Unit) و LaunchedEffect(key) في Jetpack Compose.",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم دورة حياة الكوروتين المرتبط بالمفاتيح في كومبوز، وإدراك متى يُستخدم المفتاح الثابت ومخاطر إغلاق الحالة القديمة (Stale Closures)، وكيفية عمل الإلغاء التلقائي (Automatic Cancellation).",
        "why_it_matters_ar": "استخدام `Unit` مع باراميتر متغير يجعل التطبيق يعرض بيانات قديمة ولا يتفاعل مع تغيير المعرفات، بينما وضع مفتاح سريع التغير يسبب إلغاء الكوروتين باستمرار وتشنج التطبيق.",
        "worked_example_ar": "الفرق بين المفتاح الثابت والمفتاح المتغير:\n```kotlin\n// مفتاح ثابت: يعمل مرة واحدة عند فتح الشاشة\nLaunchedEffect(Unit) { analytics.trackScreen() }\n// مفتاح متغير: يعيد التحميل ويلغي الطلب السابق فور تغير الـ id\nLaunchedEffect(userId) { vm.loadUser(userId) }\n```",
        "trade_offs_ar": "تحديد المفتاح بدقة يضمن بقاء البيانات متزامنة، لكن اختيار مفاتيح غير مستقرة يؤدي لإلغاء وإعادة تشغيل الكوروتين في كل فريم دون اكتمال العمل.",
        "failure_modes_ar": "تمرير `Unit` لعملية بحث تعتمد على نص متغير `query`، مما يجعل عملية البحث لا تتكرر عند كتابة كلمات جديدة.",
        "production_perspective_ar": "في المشروعات الكبيرة، نراجع كل `LaunchedEffect` في فحص الكود؛ العمليات التي تعتمد على مدخلات الشاشة يجب أن تأخذ تلك المدخلات كمفاتيح لضمان عدم حدوث Stale State.",
        "how_to_answer_ar": "ابدأ بالفارق الأساسي: `LaunchedEffect(Unit)` يعمل مرة واحدة فقط طوال بقاء المكون في الشجرة، بينما `LaunchedEffect(key)` يراقب المفتاح ويعيد تشغيل الكوروتين مع إلغاء القديم فور تغير قيمته، وحذر من فخ Stale Closure عند استخدام Unit مع بيانات متغيرة.",
        "talking_points_ar": "دورة حياة المفتاح، وآلية إلغاء الكوروتين القديم بـ CancellationException، وفخ Stale Closures، ومخاطر Cancellation Thrashing مع المفاتيح غير المستقرة.",
        "follow_ups_ar": "- **المحاور:** \"ماذا يحدث للطلب القديم إذا تغير المفتاح أثناء تشغيل عملية شبكة طويلة؟\"\n  **المرشح:** \"كومبوز بتلغي الـ Job القديم فوراً، والـ CancellationException بينهي الاتصال ويوفر الباقة، ويبدأ الطلب الجديد بالمفتاح الحديث.\"\n\n- **المحاور:** \"هل يمكن تمرير أكثر من مفتاح لـ LaunchedEffect؟\"\n  **المرشح:** \"نعم، الدالة تدعم تمرير مفتاحين أو ثلاثة أو مصفوفة مفاتيح `vararg keys`، وأي تغيير في أي مفتاح منهم بيعيد تشغيل الكوروتين.\"",
        "self_check_ar": "هل وضحت الفارق بين المفتاح الثابت والديناميكي؟ هل شرحت آلية الإلغاء؟ وهل حذرت من فخ إغلاق البيانات القديمة؟",
        "references_ar": f"- [Side-effects in Jetpack Compose: LaunchedEffect](https://developer.android.com/develop/ui/compose/side-effects#launchedeffect) — الدليل الرسمي لجوجل للآثار الجانبية.\n- [Jetpack Compose Effect Lifecycle](https://medium.com/androiddevelopers/) — مقال معماري لدورة حياة التأثيرات.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "دالة `LaunchedEffect(Unit)` بتنفذ كود الكوروتين المعلق مرة واحدة فقط لما المكون يدخل شجرة العرض (Composition)، وبتفضل شغالة لحد ما المكون يخرج تماماً من الشاشة. في المقابل، `LaunchedEffect(key)` بتربط دورة حياة الكوروتين بقيمة مفتاح متغير؛ أول ما قيمة المفتاح تتغير، كومبوز بتلغي الكوروتين القديم فوراً وتطلق كوروتين جديد بالقيمة المحدثة. استخدام `Unit` مع بيانات متغيرة زي الـ ID بيسبب عيب خطير بنسميه Stale State بحيث البيانات مش بتتحدث، بينما وضع مفتاح عشوائي بيسبب إلغاء مستمر للكوروتين قبل ما يلحق يخلص.",
        "best_answer_ar": "المقارنة بين `LaunchedEffect(Unit)` و `LaunchedEffect(key)` هي واحدة من أهم النقاط التي تميز المطور الفاهم لدورة حياة الآثار الجانبية في كومبوز.\n\nلما بنمرر قيمة ثابتة زي `Unit` أو `true`، إحنا بنبلغ محرك كومبوز إن الكود المعلق ده معندوش أي اعتماديات خارجية ديناميكية محتاج يراقبها. الرنتايم بيشغل الكوروتين أول ما الشاشة تفتح، وبيحميه من أي إعادة تشغيل مع عمليات الـ Recomposition المتكررة، ومش بيلغيه إلا لما المستخدم يخرج من الشاشة خالص. النمط ده مثالي لمهام البداية فقط، زي إرسال حدث تحليلات عند فتح الشاشة أو طلب إذن محدد لمرة واحدة.\n\nالمشكلة الكارثية بتظهر لما المطور يستخدم `Unit` داخل شاشة بتعتمد على مدخلات متغيرة، زي `userId`.\nلو المستخدم غير الحساب، الكوروتين مش هيشتغل تاني لأن المفتاح لسه `Unit`، والواجهة هتفضل محبوسة في البيانات القديمة (Stale Closure).\n\nالحل هو استخدام `LaunchedEffect(userId)`.\nهنا كومبوز بتراقب المتغير بـ `equals()`؛ أول ما الـ `userId` يتغير، المحرك بيلغي طلب الشبكة القديم في ثوانٍ، ويطلق كوروتين جديد يحمل بيانات المستخدم الجديد.\nده بيضمن إن الواجهة دايماً متزامنة مع أحدث مدخلات، وبيوفر استهلاك الإنترنت لأن الطلبات القديمة بيتم إيقافها تلقائياً.",
        "deep_answer_ar": "تحت الكابوت، مترجم كومبوز بيخزن كائن `LaunchedEffectImpl` داخل مصفوفة الـ `SlotTable` لكل استدعاء.\n\nالكائن ده بيحتفظ بمرجع لآخر قيمة مفتاح تم تمريرها، ومرجع لكائن الـ `Job` الخاص بالكوروتين الشغال. أثناء كل دورة Recomposition، المحرك بيعمل مقارنة مساواة بين المفتاح الحالي والمفتاح القديم المسجل في الـ SlotTable باستخدام `equals()`.\nلو المفتاحين متطابقين، الرنتايم بيتخطى الدالة بالكامل ويكمل الكوروتين عمله بدون أي مقاطعة.\n\nلو المفتاح اختلف، المحرك بينادي فوراً `job.cancel()` على الكوروتين القديم. ده بيولد استثناء `CancellationException` بيوقف أي دوال معلقة زي `delay` أو طلبات Ktor و Retrofit فوراً، وبيمنع أي كتابة في الحالة من الكود القديم. وبعد اكتمال الإلغاء، المحرك بيشغل كوروتين جديد تماماً على الـ Dispatcher المناسب ويمرر له أحدث كود.\n\nالنقطة المعمارية الحرجة اللي بنركز عليها في كود الإنتاج هي تجنب ظاهرة الـ Cancellation Thrashing؛ لو مررت مفتاحاً غير مستقر زي كائن جديد بيتبني في كل رندرة، الكوروتين هيتكنسل ويتعاد تشغيله 60 مرة في الثانية ومش هيخلص شغله أبداً. ولو الكود بيعتمد على أكتر من متغير، لازم تمررهم كلهم كمفاتيح لضمان التزامن الكامل.\n\nوفوق كده، استخدام الكوروتين المنضبط مع دورة حياة المفتاح بيضمن عدم حدوث أي تضارب بيانات (Race Conditions) بين استجابات الشبكة المختلفة، لأن الإلغاء التعاوني بيرمي الاستجابات المتأخرة فوراً."
    }
}

# ==========================================
# COM-12: What are rememberUpdatedState, derivedStateOf, and snapshotFlow?
# ==========================================
DATA["COM-12"] = {
    "concept_en": """Jetpack Compose provides three advanced state bridge primitives to solve edge cases in asynchronous state management. rememberUpdatedState captures a frequently changing value (such as a callback lambda or parameter) inside a long-lived effect without restarting the effect when the value updates. derivedStateOf calculates a derived state value from one or more snapshot states, acting as an optimization filter that triggers recomposition only when the computed output actually changes, rather than when the input states change. snapshotFlow bridges the Compose declarative state world to Kotlin Coroutines by converting Compose Snapshot State reads into a cold Flow, allowing engineers to leverage standard Flow operators like debounce, filter, and distinctUntilChanged on UI state.""",
    "walkthrough_en": """Demonstrating rememberUpdatedState, derivedStateOf, and snapshotFlow in practice:
```kotlin
@Composable
fun AdvancedStateDemo(
    onTimeout: () -> Unit, // Rapidly changing lambda callback
    listState: LazyListState
) {
    // 1. rememberUpdatedState: Effect runs once, but always invokes the LATEST callback!
    val currentOnTimeout by rememberUpdatedState(onTimeout)
    LaunchedEffect(Unit) {
        delay(5000)
        currentOnTimeout() // Never captures a stale closure!
    }

    // 2. derivedStateOf: Scroll position changes every pixel, but output changes ONLY at threshold!
    // Prevents recomposing on every single scrolled pixel!
    val showScrollToTop by remember {
        derivedStateOf { listState.firstVisibleItemIndex > 5 }
    }

    // 3. snapshotFlow: Convert state reads to a cold Flow to debounce analytics or search
    LaunchedEffect(listState) {
        snapshotFlow { listState.firstVisibleItemIndex }
            .distinctUntilChanged()
            .filter { it > 10 }
            .collect { index ->
                analytics.track("User scrolled past item $index")
            }
    }
}
```""",
    "short_en": """rememberUpdatedState captures a changing value inside a long-running effect so the effect reads the newest value without restarting. derivedStateOf computes derived state and prevents recomposition unless the calculated result changes, effectively filtering out high-frequency input mutations. snapshotFlow converts Compose snapshot state reads into a cold Flow, allowing developers to apply coroutine operators like debounce, distinctUntilChanged, and mapLatest to UI state changes.""",
    "structured_en": """These three primitives represent Compose's advanced toolkit for fine-grained state observation and cross-paradigm bridging.
First, rememberUpdatedState resolves the stale lambda closure dilemma. When an effect like LaunchedEffect(Unit) executes a long asynchronous delay or listens to a timer, it captures the callback passed at inception. If the parent recomposes and provides a new lambda, the effect would execute the stale initial lambda unless restarted. Wrapping the lambda with rememberUpdatedState creates an internal MutableState holder that updates on every recomposition while keeping the effect running undisturbed.
Second, derivedStateOf is a critical performance optimization tool.
In scenarios where input state updates with high frequency—such as LazyListState scrolling by individual pixels—reading the state directly in a composable triggers recompositions on every single pixel delta.
Wrapping the calculation in derivedStateOf ensures observers recompose only when the derived boolean or value transitions across a threshold.
Third, snapshotFlow bridges Compose's snapshot system to reactive Kotlin Coroutines.
It observes state reads in a block and emits values down a Flow whenever snapshot mutations occur.
This enables developers to apply debounce or filter operators before triggering network requests or analytics.""",
    "deep_senior_en": """Under the hood, each of these three primitives interfaces with distinct subsystems of the Compose runtime.
rememberUpdatedState is implemented as a simple remember block that instantiates a mutableStateOf(newValue) and mutates value = newValue on every recomposition. Because the state holder object reference remains referentially identical across passes, effect blocks capturing that state holder read the latest value transparently through its getter without invalidating the effect's key.
derivedStateOf instantiates a DerivedSnapshotState instance.
When evaluated, it registers a snapshot read observer to record all SnapshotMutableState instances accessed inside the calculation lambda.
During subsequent state updates, Compose checks whether the recorded dependencies changed.
If they did, it re-evaluates the calculation; however, it invalidates downstream recomposition scopes only if the newly calculated result is not equal (via equals) to the previously cached result.
This calculation memoization completely eliminates frame drops during rapid scrolling.
snapshotFlow relies on Snapshot.registerApplyObserver.
It establishes a cold flow that takes an initial snapshot read of the block and registers a listener for global snapshot commits.
When any state variable read inside the block is committed anywhere in the process, the apply observer wakes up the flow collector, verifies if the output changed via equals(), and emits the new value down the coroutine channel.
Senior engineers use these tools to prevent recomposition churn and orchestrate clean reactive pipelines.""",
    "meta_ar": {
        "id": "COM-12",
        "questionAr": "ما هي أدوات rememberUpdatedState و derivedStateOf و snapshotFlow في كومبوز؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على حل مشاكل الـ Stale Closures بـ `rememberUpdatedState`، وتحسين الأداء ومنع الـ Recomposition المتكرر بـ `derivedStateOf`، وتحويل حالة كومبوز إلى Coroutines Flow بـ `snapshotFlow`.",
        "why_it_matters_ar": "إهمال هذه الأدوات يسبب كوارث شائعة: إما إعادة تشغيل المؤقتات باستمرار بسبب تغير الدوال، أو انهيار الفريمات أثناء التمرير لقراءة عداد البكسلات مباشرة، أو صعوبة تطبيق مشغلات الـ Debounce على واجهة المستخدم.",
        "worked_example_ar": "استخدام الأدوات الثلاث باحترافية:\n```kotlin\n// 1. تحديث الكولباك دون إعادة تشغيل الكوروتين\nval currentAction by rememberUpdatedState(onDone)\nLaunchedEffect(Unit) { delay(3000); currentAction() }\n// 2. فلترة الرندرة عند تخطي العنصر الخامس فقط\nval showTop by remember { derivedStateOf { listState.firstVisibleItemIndex > 5 } }\n// 3. تحويل الحالة لـ Flow وتطبيق debounce\nLaunchedEffect(Unit) {\n    snapshotFlow { query }.debounce(300).collect { vm.search(it) }\n}\n```",
        "trade_offs_ar": "استخدام `derivedStateOf` يحمل تكلفة حسابية صغيرة في المراقبة، لذا يجب استخدامه فقط عندما يتغير المدخل بوتيرة أسرع بكثير من المخرج (مثل تغير البكسلات مقابل ناتج boolean).",
        "failure_modes_ar": "استخدام `derivedStateOf` لعمليات حسابية بسيطة لا تعتمد على متغيرات State، مما يضيف تعقيداً بدون أي فائدة للأداء.",
        "production_perspective_ar": "في كود الإنتاج عالي المستوى، نعتمد `rememberUpdatedState` في أي دالة مخصصة تطلق تأثيراً يستقبل كولباك، ونستخدم `derivedStateOf` في كل أزرار العودة للأعلى (Scroll to Top buttons).",
        "how_to_answer_ar": "اشرح كل أداة بدورها المحدد: `rememberUpdatedState` لتحديث قيمة داخل تأثير طويل الأمد دون إعادة تشغيله، و `derivedStateOf` لحساب حالة مشتقة وتصفية عمليات إعادة التركيب الزائدة، و `snapshotFlow` لتحويل قراءات الحالة إلى Kotlin Flow وتطبيق مشغلات الكوروتين.",
        "talking_points_ar": "حل مشكلة Stale Lambda بـ rememberUpdatedState، وتصفية رندرة التمرير بـ derivedStateOf، وتطبيق debounce بـ snapshotFlow، وآلية Snapshot.registerApplyObserver.",
        "follow_ups_ar": "- **المحاور:** \"متى يكون استخدام derivedStateOf غير مفيد ويزيد الحمل؟\"\n  **المرشح:** \"لو كانت الحالة المشتقة بتتغير بنفس معدل تغير الحالة الأصلية؛ يعني لو المدخل بيتغير 10 مرات والمخرج بينتج 10 قيم مختلفة، هنا derivedStateOf مش هتوفر رندرة وهتضيف Overhead حسابي فقط.\"\n\n- **المحاور:** \"كيف تمنع rememberUpdatedState تسريب الذاكرة في الكولباكات القديمة؟\"\n  **المرشح:** \"بإنها بتحتفظ بالحالة كـ MutableState داخلي، فالتأثير بيقرأ دايماً القيمة الحالية من خلال getter، وبترمي المرجع القديم فور تحديثه مع الرندرة الجديدة.\"",
        "self_check_ar": "هل عرفت الأدوات الثلاث بدقة؟ هل وضحت سيناريو استخدام كل واحدة؟ وهل بينت كيف يعمل derivedStateOf من الداخل؟",
        "references_ar": f"- [Side-effects in Jetpack Compose](https://developer.android.com/develop/ui/compose/side-effects#rememberupdatedstate) — التوثيق الرسمي لجوجل لأدوات الحالة المتقدمة.\n- [Compose Performance: derivedStateOf](https://developer.android.com/develop/ui/compose/performance/derived-state) — دليل جوجل لتحسين الأداء باستخدام derivedStateOf.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "دي تلات أدوات متقدمة للتحكم في الحالة: الأولى `rememberUpdatedState` بتحفظ أحدث قيمة لمتغير أو كولباك داخل تأثير طويل الأمد (زي الكوروتين) عشان التأثير يقرأ القيمة الأحدث دايماً بدون ما يضطر يعيد تشغيل نفسه من الأول. التانية `derivedStateOf` بتحسب حالة معتمدة على حالات تانية وبتشتغل كفلتر يمنع إعادة التركيب إلا لو الناتج النهائي اتغير فعلاً (زي إظهار زرار التمرير للأعلى بعد العنصر العاشر). التالتة `snapshotFlow` بتحول قراءات الـ State في كومبوز إلى Kotlin Flow بارد عشان تقدر تطبق عليه مشغلات الكوروتين زي `debounce` و `distinctUntilChanged`.",
        "best_answer_ar": "الأدوات دي بتعتبر العصب المتقدم لإدارة ومراقبة الحالة في Jetpack Compose لحل أعقد المشاكل المعمارية.\n\nالأداة الأولى `rememberUpdatedState` حلت معضلة الـ Stale Closures.\nلو عندك دالة بتشغل عداد تنازلي لمدة 5 ثواني داخل `LaunchedEffect(Unit)` وبعدها بتنادي كولباك `onTimeout`؛ لو الشاشة رندرت والـ Lambda اتغيرت في الأب، الكوروتين هيفضل ماسك في الـ Lambda القديمة اللي دخل بيها أول مرة. لو حطيت الـ Lambda في مفتاح التأثير، التأثير هيتعاد تشغيله من الأول والعداد هيصفر! الحل السحري هو `rememberUpdatedState`؛ بتخلي الكوروتين شغال مستمر وفي نفس الوقت يقرأ أحدث نسخة من الكولباك في لحظة التنفيذ.\n\nالأداة الثانية `derivedStateOf` هي المنقذ الأول للأداء مع التمرير السريع.\nفي القوائم، حالة التمرير `listState` بتتغير مع كل بكسل واحد يتحرك على الشاشة. لو كتبت كود عادي بيفحص `index > 0`، الشاشة هتعيد الرندرة مئات المرات مع كل بكسل! لما تلف الحسبة دي في `derivedStateOf`، كومبوز مش هتعيد تشغيل الشاشة إلا لما الناتج يتحول من `false` إلى `true`، وده بيوفر آلاف العمليات الحسابية.\n\nالأداة الثالثة `snapshotFlow` بتعمل جسر بين عالم كومبوز التصريحي وتدفقات كوتلن التفاعلية.\nبتراقب قراءة متغيرات الحالة وتبثها كـ Flow، وده بيسمح لك تعمل Debounce لحقل البحث أو تراقب سرعة التمرير بدقة وتكامل تام مع مكتبات النطاق الخلفي.",
        "deep_answer_ar": "تحت الكابوت، كل أداة من الأدوات دي متصلة مباشرة بنواة محرك كومبوز ونظام إدارة الـ Snapshots.\n\nدالة `rememberUpdatedState` في الحقيقة هي دالة بسيطة جداً بتنشئ `mutableStateOf` داخل الـ `remember` وبتحدث قيمته `state.value = newValue` في كل دورة Recomposition. لأن المرجع نفسه ثابت في الـ SlotTable، الكوروتين اللي ماسك المرجع ده بيقرأ القيمة الأحدث دايماً من خلال استدعاء الـ getter بدون الحاجة لإلغاء الـ Job.\n\nدالة `derivedStateOf` بتنشئ كائن من كلاس `DerivedSnapshotState`.\nأول ما الدالة دي بتتنفذ، بتسجل مراقب قراءة (Snapshot Read Observer) بيلتقط كل متغيرات الـ State اللي اتقرأت داخل البلوك. لما أي متغير منهم يتغير في الـ Snapshot التالي، محرك كومبوز بيعيد حساب المعادلة في الخلفية، ويقارن القيمة الجديدة بالقديمة باستخدام `equals()`. لو القيمة متطابقة (مثلاً كانت true وفضلت true)، المحرك بيلغي عملية الـ Recomposition لنطاقات الدوال المراقبة تماماً، وده بيقضي على الـ Jank أثناء التمرير.\n\nودالة `snapshotFlow` بتعتمد في باطنها على `Snapshot.registerApplyObserver`.\nبتفتح كوليكشن بارد، وبتقرأ البلوك في لقطة أولية، وتسجل مراقب عام على مستوى التطبيق. أول ما يحصل Commit لأي SnapshotState متأثر، المراقب بيصحي الكوروتين، ويفحص الناتج، ويبث القيمة الجديدة في الـ Flow فقط لو اتغيرت، وده بيوفر تناغماً هندسياً مبهراً بين الكوروتين وكومبوز."
    }
}

# ==========================================
# COM-13: How do you correctly implement Snackbar, navigation, and callbacks?
# ==========================================
DATA["COM-13"] = {
    "concept_en": """Implementing Snackbar messages, navigation transitions, and event callbacks in Jetpack Compose requires a disciplined separation between persistent UI state and transient UI effects. Rather than relying on fragile single-shot channels or passing ambient navigation controllers down the UI hierarchy, modern Compose architecture treats one-off events as consumable state or hoisted lambda callbacks. Snackbars are orchestrated via a hoisted SnackbarHostState inside Scaffold and launched in a coroutine scope. Navigation is decoupled by hoisting navigation callbacks to top-level navigation graphs, keeping screen composables completely agnostic of NavController instances.""",
    "walkthrough_en": """Architectural implementation of Snackbar, navigation, and callbacks:
```kotlin
// 1. Screen Composable: Completely stateless, receives lambdas, NO NavController passed!
@Composable
fun ProductDetailContent(
    productName: String,
    onBackClick: () -> Unit,
    onShowMessage: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    Column(modifier = modifier.padding(16.dp)) {
        IconButton(onClick = onBackClick) { Icon(Icons.Default.ArrowBack, "Back") }
        Text("Product: $productName", style = MaterialTheme.typography.headlineMedium)
        Button(onClick = { onShowMessage("Item added to cart!") }) {
            Text("Add to Cart")
        }
    }
}

// 2. Route Composable: Orchestrates Scaffold, SnackbarHostState, and Navigation
@Composable
fun ProductDetailRoute(
    productId: String,
    onNavigateBack: () -> Unit,
    viewModel: ProductViewModel = hiltViewModel()
) {
    val snackbarHostState = remember { SnackbarHostState() }
    val scope = rememberCoroutineScope()

    Scaffold(
        snackbarHost = { SnackbarHost(snackbarHostState) }
    ) { padding ->
        ProductDetailContent(
            productName = "Pixel 9 Pro",
            onBackClick = onNavigateBack,
            onShowMessage = { msg ->
                scope.launch {
                    snackbarHostState.currentSnackbarData?.dismiss() // Dismiss previous!
                    snackbarHostState.showSnackbar(msg)
                }
            },
            modifier = Modifier.padding(padding)
        )
    }
}
```""",
    "short_en": """We implement Snackbars using a hoisted SnackbarHostState inside a Scaffold, triggering showSnackbar() within a rememberCoroutineScope or LaunchedEffect. For navigation and callbacks, we hoist lambda events to the navigation graph level instead of passing NavController into screen composables. This keeps screens stateless, enables seamless Compose Previews, and makes unit and screenshot testing trivial without mocking Android navigation classes.""",
    "structured_en": """Managing transient UI events like Snackbars and navigation transitions is a frequent architectural testing ground in Android interviews.
In legacy architectures, developers relied on SingleLiveEvent or Channel anti-patterns that frequently leaked events or dropped them during configuration changes.
Modern Jetpack Compose adheres to clean architectural decoupling.
For Snackbars, the standard pattern utilizes Scaffold and its dedicated snackbarHost parameter.
The screen creates a remembered SnackbarHostState.
When a user action triggers a message, a coroutine launched via rememberCoroutineScope or a state-driven LaunchedEffect invokes snackbarHostState.showSnackbar().
Calling dismiss() on currentSnackbarData before showing a new snackbar prevents stacking delayed message queues.
For navigation, a major industry rule is never passing NavHostController down into presenter composables.
Passing NavController tightly couples the UI to a specific navigation library, destroys Android Studio Previews, and prevents isolated UI testing.
Instead, screens expose explicit callback lambdas like onNavigateToDetails or onBackClick.
The outer navigation graph or route composable implements these lambdas, invoking navController.navigate() at the top boundary.""",
    "deep_senior_en": """Under the hood, SnackbarHostState acts as an asynchronous state coordinator powered by Kotlin Coroutines Mutex locks.
When showSnackbar() is called, SnackbarHostState acquires an internal Mutex. If another snackbar is currently visible, the calling coroutine suspends until the existing snackbar dismisses, times out, or is explicitly cancelled via currentSnackbarData?.dismiss().
This built-in suspension mechanism guarantees thread-safe, serialized message presentation without requiring custom queue data structures.
When integrating with architecture ViewModels, transient events should be modeled either as consumable state properties inside an immutable UiState data class (cleared via an onEventConsumed callback once displayed) or emitted through a state-driven UI message queue.
Regarding navigation, decoupling NavController from leaf composables is critical for compiler skipping and multiplatform modularization.
NavController is a complex, mutable Android platform class that is marked unstable by the Compose compiler. Passing it down as a parameter immediately renders the child composable unskippable.
By replacing NavController with stable lambda function types (such as () -> Unit), the Compose compiler marks the parameter as stable, enabling zero-overhead smart skipping across the entire presenter layer.
Furthermore, this separation allows the same presenter screen to be reused across standard phone screens, navigation drawer panels, and adaptive foldable split-panes without altering a single line of presentation code.""",
    "meta_ar": {
        "id": "COM-13",
        "questionAr": "كيف تنفذ رسائل الـ Snackbar والتنقل (Navigation) والكولباكات باحترافية في Compose؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على فصل إدارة الـ Snackbar عبر `SnackbarHostState`، وتطبيق مبدأ رفع أحداث التنقل (Navigation Hoisting)، وتجنب تمرير `NavController` داخل الشاشات، وإدراك تأثير ذلك على الـ Skipping واستقرار الكود.",
        "why_it_matters_ar": "تمرير `NavController` داخل الشاشات الفرعية يفسد إمكانية عمل Previews، ويعطل الـ Smart Skipping لأن الكائن غير مستقر، ويجعل كتابة اختبارات الواجهة معقدة للغاية.",
        "worked_example_ar": "فصل التنقل والـ Snackbar عبر الـ Lambdas:\n```kotlin\n// شاشة نقية بدون NavController\n@Composable fun DetailsScreen(onBack: () -> Unit, onShowMsg: (String) -> Unit)\n// الـ Route يربط الـ NavController والـ Scaffold\n@Composable fun DetailsRoute(navController: NavController) {\n    val snackbarState = remember { SnackbarHostState() }\n    val scope = rememberCoroutineScope()\n    Scaffold(snackbarHost = { SnackbarHost(snackbarState) }) {\n        DetailsScreen(onBack = { navController.popBackStack() }, onShowMsg = { scope.launch { snackbarState.showSnackbar(it) } })\n    }\n}\n```",
        "trade_offs_ar": "رفع الكولباكات يزيد عدد الباراميترات في الشاشات العلوية، لكنه يمنح استقلالية تامة للشاشة ويسمح بمعاينتها في Preview واختبارها على الـ JVM بسهولة.",
        "failure_modes_ar": "تمرير `navController` كباراميتر في كل دالة Composable صغيرة، مما يربط كل الواجهات بمكتبة التنقل ويعطل ميزة الـ Skipping.",
        "production_perspective_ar": "في المشروعات الكبيرة، نمنع تمرير `NavController` تحت مستوى الـ Route Composable، ونجمع أحداث الشاشة في Sealed Interface أو Lambdas واضحة.",
        "how_to_answer_ar": "اشرح جزئيتين: للـ Snackbar استخدم `SnackbarHostState` المدار عبر `Scaffold` وإطلاقه بكوروتين مع إلغاء الرسائل السابقة، وللتنقل شدد على قاعدة عدم تمرير `NavController` للأسفل بل رفع الأحداث كـ Lambdas في الـ Route لضمان الـ Skipping وقابلية المعاينة بـ Previews.",
        "talking_points_ar": "إدارة SnackbarHostState والـ Mutex الداخلي، وقاعدة Navigation Hoisting، ومخاطر تمرير NavController على استقرار الأنواع والـ Skipping، وتسهيل Previews.",
        "follow_ups_ar": "- **المحاور:** \"لماذا نعتبر تمرير NavController داخل دوال الشاشات خطأ معمارياً كبيراً؟\"\n  **المرشح:** \"لأنه كائن أندرويد معقد وغير مستقر (Unstable) بيعطل الـ Skipping في كومبوز، وبيلغي إمكانية تشغيل الـ Previews، وبيصعب كتابة Screenshot Tests أو مشاركة الكود مع KMP.\"\n\n- **المحاور:** \"كيف يتعامل SnackbarHostState مع استدعاء showSnackbar عدة مرات متتالية؟\"\n  **المرشح:** \"بيستخدم Mutex داخلي بيعلق الكوروتين الجديد لحد ما الرسالة الحالية تخلص، أو نقدر ننادي `dismiss()` على الرسالة الحالية عشان نظهر الجديدة فوراً.\"",
        "self_check_ar": "هل شرحت تنفيذ الـ Snackbar عبر Scaffold؟ هل شددت على عدم تمرير NavController؟ وهل بينت الأثر على الـ Skipping والمعاينة؟",
        "references_ar": f"- [Compose Scaffold and Snackbars](https://developer.android.com/develop/ui/compose/components/scaffold#snackbar) — دليل جوجل الرسمي لـ Scaffold ورسائل Snackbar.\n- [Navigation in Jetpack Compose](https://developer.android.com/develop/ui/compose/navigation) — التوثيق الرسمي للتنقل النظيف في كومبوز.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "بننفذ الـ Snackbar باستخدام كائن `SnackbarHostState` داخل مكون `Scaffold`، وبنطلق رسالة `showSnackbar()` عبر كوروتين من `rememberCoroutineScope` أو `LaunchedEffect` لما يحصل حدث معين. أما بخصوص التنقل (Navigation) والكولباكات، فالقاعدة الذهبية هي إننا منمررش كائن `NavController` نهائياً داخل الشاشات التقديمية (Presenters). بدل كده، الشاشة بتصعد الأحداث كـ Lambdas عادية زي `onNavigateBack`، والـ Route أو الـ NavGraph هو اللي بيستقبل الـ Lambda دي وينادي `navController.navigate()`، وده بيخلي الشاشات نقية وقابلة للمعاينة في Previews واختبارها بدون أي تعقيد.",
        "best_answer_ar": "تنفيذ رسائل الـ Snackbar والتنقل باحترافية بيكشف مدى فهم المطور لقواعد المعمارية النظيفة (Clean Architecture) وفصل المسؤوليات في Jetpack Compose.\n\nفي التعامل مع رسائل الـ Snackbar، الطريقة الصحيحة هي الاعتماد على `Scaffold` وتمرير `SnackbarHostState` محفوط بـ `remember`. لما المستخدم يعمل حركة محتاجة تنبيه، بنطلق دالة `showSnackbar()` بكوروتين. ولضمان تجربة مستخدم ممتازة، لو المستخدم داس كذا مرة بنعمل `dismiss()` للرسالة الحالية الأول عشان الرسالة الجديدة تظهر فوراً وميحصلش طابور طويل من الرسائل المتأخرة.\n\nأما بخصوص التنقل والكولباكات، فأكبر غلطة بيقع فيها المطورون المبتدئون هي تمرير `navController` كباراميتر داخل كل شاشة ومكون فرعي.\nالحركة دي بتدمر المعمارية تماماً؛ لأنها بتربط الواجهة بمكتبة أندرويد ثقيلة، وبتحرمك من تشغيل الـ `@Preview` في أندرويد ستوديو، وبتخلي الـ Unit Tests شبه مستحيلة.\n\nالتصميم المتين بيعتمد على نمط الـ Navigation Hoisting:\nالشاشة بتكون Stateless تماماً؛ كل اللي بتعرفه إن عندها زرار، فبتستقبل Lambda اسمها `onItemClick: (String) -> Unit`. وفوق في الـ NavGraph بنعرف الوجهة، ونمرر الـ Lambda دي بحيث تنادي `navController.navigate(\"details/$id\")`. النتيجة إن الشاشة أصبحت مستقلة بنسبة 100% وممكن يعاد استخدامها في تابلت أو شاشة جانبية بدون أي تعديل.",
        "deep_answer_ar": "تحت الكابوت، كائن `SnackbarHostState` بيشتغل كمنسق متزامن للحالة مدعوم بـ `Mutex` داخلي من مكتبة كوتلن كوروتينز.\nلما بتنادي `showSnackbar()`، الدالة بتطلب حجز الـ Mutex؛ لو فيه رسالة معروضة حالياً، الكوروتين بيتعلق (Suspends) تلقائياً لحد ما الرسالة الحالية تخلص مدتها أو تتلغي. ده بيضمن أمان الخيوط (Thread-safety) وبيمنع تداخل الرسائل فوق بعضها بدون الحاجة لبناء Queue معقد يدوياً.\n\nومن منظور أداء المترجم (Compiler Performance)، عدم تمرير `NavController` للشاشات هو قرار حاسم لكفاءة التطبيق.\nكائن `NavController` هو كلاس أندرويد ضخم ومعقد ومليان State متغير، وبالتالي مترجم كومبوز بيصنفه كـ Unstable Type. لو مررته للشاشة، الشاشة دي هتفقد ميزة الـ Smart Skipping وهتعيد تشغيل نفسها في كل مرة الشاشة الأب ترندر فيها.\n\nبينما لما تستبدله بدوال Lambdas مستقرة، الكومبايلر بيصنف الباراميترات كـ Stable، وده بيمكّن كومبوز من تخطي رندرة الشاشة بالكامل لو حالتها لم تتغير. وفوق كده، الفصل ده بيسمح بتشغيل الشاشات في معمارية Kotlin Multiplatform مستقبلاً لأن الشاشة معندهاش أي ارتباط بـ `androidx.navigation` الخاصة بأندرويد.\n\nوعلاوة على ذلك، هذا الفصل المعماري بيمكّن فريق العمل من عمل اختبارات الواجهة (Compose UI Tests) بسرعة خارقة وبدون الحاجة لعمل Mock لكلاسات أندرويد المعقدة، وبيمهد الطريق لمشاركة نفس الشاشات التقديمية مع تطبيقات سطح المكتب والويب عبر Kotlin Multiplatform بدون أي عوائق."
    }
}

# ==========================================
# COM-14: What are stable keys and content types in LazyColumn?
# ==========================================
DATA["COM-14"] = {
    "concept_en": """In Jetpack Compose Lazy layouts, stable keys and content types are vital optimization mechanisms that govern item identity and composition recycling. A stable key (provided via key = { item.id }) supplies a unique, persistent identifier for each item instead of relying on default list position indices, preserving scroll position and enabling item placement animations during dataset mutations. The contentType parameter (provided via contentType = { item.type }) classifies items by their visual layout structure, allowing the Compose subcomposition pipeline to reuse composition slots and SlotTable layouts between items of identical structure, mirroring legacy RecyclerView view pools.""",
    "walkthrough_en": """Applying stable keys and content types in a heterogeneous LazyColumn:
```kotlin
sealed interface FeedItem {
    val id: String
    data class Header(override val id: String, val title: String) : FeedItem
    data class Post(override val id: String, val content: String, val author: String) : FeedItem
    data class BannerAd(override val id: String, val adUrl: String) : FeedItem
}

@Composable
fun FeedList(items: List<FeedItem>, modifier: Modifier = Modifier) {
    LazyColumn(modifier = modifier) {
        items(
            items = items,
            // 1. STABLE KEY: Preserves scroll state, avoids item recreation on insert/delete
            key = { item -> item.id },
            // 2. CONTENT TYPE: Reuses composition slots between identical layout structures!
            contentType = { item ->
                when (item) {
                    is FeedItem.Header -> "HEADER_TYPE"
                    is FeedItem.Post -> "POST_TYPE"
                    is FeedItem.BannerAd -> "AD_TYPE"
                }
            }
        ) { item ->
            when (item) {
                is FeedItem.Header -> HeaderItemView(item)
                is FeedItem.Post -> PostItemView(item)
                is FeedItem.BannerAd -> AdBannerView(item)
            }
        }
    }
}
```""",
    "short_en": """Stable keys and content types optimize LazyColumn performance. A stable key provides a unique, persistent identity (like an ID) for each item, preventing scroll jumps, avoiding state loss, and enabling item placement animations when the list changes. The contentType classifies items by their visual structure, allowing Compose to reuse composition slots and nodes between items of the same type, drastically reducing allocation and measurement overhead during fast scrolling.""",
    "structured_en": """Achieving smooth 60fps scrolling in Jetpack Compose Lazy lists relies directly on configuring stable keys and explicit content types.
By default, if you omit the key parameter in items(), LazyColumn uses the item's integer position in the list as its identity.
This default behavior causes severe bugs when the list updates dynamically.
If an item is prepended at index zero, every existing item's index shifts by one. Compose assumes every item has been replaced, discarding item-level remembered state, losing scroll position, and triggering unnecessary recomposition passes for the entire viewport.
Providing a stable, unique key (such as item.id) binds item identity to the underlying data model.
Compose accurately tracks item movement, preserves scroll offsets, and smoothly animates insertions and reorderings using Modifier.animateItem().
The contentType parameter introduces an additional rendering optimization.
In heterogeneous lists with multiple view layouts (like headers, post cards, and banner ads), Compose uses contentType to pool and reuse composition slots.
When an item of a given type scrolls off-screen, Compose reuses its existing layout node structure for a newly entering item of the same contentType, eliminating redundant slot tree construction and layout measurement overhead.""",
    "deep_senior_en": """Under the hood, LazyColumn relies on SubcomposeLayout to lazily measure and compose only the items visible within the current viewport plus a configurable prefetch distance.
When key is omitted, the subcomposition mechanism assigns the index integer as the composition key in the SlotTable. When items are inserted, deleted, or reordered, the index mapping fails, causing Compose to dispose of the old SlotTable intervals and allocate completely new ones, discarding any remembered state holders (such as expandable card toggles or inner scroll states) and creating significant garbage collection pressure.
When a stable key is supplied, Compose stores the key inside its ItemProvider. During list mutations, Compose matches the keys across frames, moving existing SlotTable nodes rather than disposing of them.
The contentType parameter operates directly on Compose's node reuse algorithm.
When an item scrolls out of bounds, its SubcomposeSlot is moved to an internal recycling cache.
Without contentType, Compose has no knowledge of whether the next entering item shares the same composable hierarchy; if the next item has a completely different layout (e.g., recycling a simple Header slot for a complex multi-layered VideoCard), Compose must tear down the entire slot subtree and rebuild it from scratch.
With contentType, Compose queries the cache for a slot matching that exact content type identifier, reusing the pre-existing node structure and executing only a fast recomposition of modified text and images.
This mirrors the efficiency of RecyclerView.RecycledViewPool, eliminating frame drops during rapid list flings.""",
    "meta_ar": {
        "id": "COM-14",
        "questionAr": "ما هي المفاتيح المستقرة (Stable Keys) وأنواع المحتوى (Content Types) في LazyColumn؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم آلية عمل الـ `LazyColumn` وإعادة تدوير النودز، ودور الـ `key` في الحفاظ على موضع التمرير والـ State، ودور `contentType` في إعادة استخدام الـ Composition Slots المشابهة لـ RecycledViewPool.",
        "why_it_matters_ar": "إهمال الـ keys يجعل القائمة تفقد مكان التمرير وحالة العناصر عند إضافة عناصر جديدة، وإهمال `contentType` يسبب تهنيجاً وتقطيعاً (Jank) أثناء التمرير السريع في القوائم غير المتجانسة.",
        "worked_example_ar": "تحديد الـ key والـ contentType في LazyColumn:\n```kotlin\nLazyColumn {\n    items(\n        items = feedItems,\n        key = { it.id }, // مفتاح فريد يمنع فقدان المكان\n        contentType = { it.layoutType } // نوع المحتوى لإعادة استخدام الـ Slots\n    ) { item -> RenderItem(item) }\n}\n```",
        "trade_offs_ar": "توفير المفاتيح والأنواع يتطلب كوداً إضافياً لتعريف المعرفات، لكنه يرفع كفاءة التمرير إلى 60 إطاراً في الثانية ويمنع إعادة بناء الشجرة من الصفر.",
        "failure_modes_ar": "استخدام الـ index الافتراضي كمفتاح، أو استخدام مفاتيح مكررة في الداتا، مما يسبب كراش فوري بـ `IllegalArgumentException` بسبب تضارب المفاتيح.",
        "production_perspective_ar": "في المشروعات الكبيرة، نلزم المطورين في فحص الـ PR بوضع `key` مستقر مستمد من الـ Backend ID لكل قائمة، وتحديد `contentType` في أي قائمة تحتوي على أكثر من شكل تصميمي.",
        "how_to_answer_ar": "اشرح المفهومين: المفتاح المستقر `key` يحدد هوية العنصر الفريدة لمنع فقدان مكان التمرير والـ State عند التعديل، بينما `contentType` يصنف أشكال العناصر لإعادة استخدام الـ Slots الجاهزة في الذاكرة زي `RecycledViewPool` في XML القديم.",
        "talking_points_ar": "هوية العناصر بـ key، والحفاظ على Scroll Position، وتفعيل animateItemPlacement، وآلية contentType المشابهة لـ ViewPool، وتفادي هدم وبناء النودز في الذاكرة.",
        "follow_ups_ar": "- **المحاور:** \"ماذا يحدث لو تكرر نفس المفتاح key لعنصرين في نفس القائمة؟\"\n  **المرشح:** \"كومبوز هترمي استثناء فوري `IllegalArgumentException: There are multiple items with the same key`؛ لأن المفتاح لازم يكون فريداً بنسبة 100% داخل القائمة.\"\n\n- **المحاور:** \"كيف يساعد contentType في توفير وقت المعالج أثناء التمرير السريع؟\"\n  **المرشح:** \"كومبوز بتخزن الـ SlotTable بتاع العنصر اللي خرج من الشاشة، وتستخدم نفس الهيكل لعنصر داخل جديد من نفس النوع، فبتعدل النصوص فقط بدل ما تهدم وتبني شجرة نودز جديدة.\"",
        "self_check_ar": "هل شرحت دور الـ key في حفظ المكان والأنيميشن؟ هل بينت دور contentType في إعادة استخدام الهياكل؟ وهل قارنتها بنظام الـ ViewPool القديم؟",
        "references_ar": f"- [Compose Lazy layouts documentation](https://developer.android.com/develop/ui/compose/lists#item-keys) — التوثيق الرسمي لجوجل لمفاتيح القوائم.\n- [Optimizing LazyColumn with Content Types](https://medium.com/androiddevelopers/) — مقال معماري لتحسين أداء القوائم في كومبوز.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "المفاتيح المستقرة (Stable Keys) وأنواع المحتوى (Content Types) هما أهم أداتين لتحقيق سلاسة الـ 60 فريم في `LazyColumn`. الـ `key` بيدي كل عنصر في القائمة هوية فريدة وثابتة (زي الـ ID) بدل الاعتماد على رقم الترتيب (index)، وده بيحمي موضع التمرير من القفز وبيمنع ضياع الحالة الداخلية للعناصر وبيفعل حركات الأنيميشن. أما الـ `contentType` فهو تصنيف لشكل تصميم العنصر (زي Header أو PostCard)، وده بيسمح لكومبوز بإعادة استخدام قوالب الذاكرة (Slots) بين العناصر المتشابهة في الشكل، بالظبط زي فكرة `RecycledViewPool` في RecyclerView القديم.",
        "best_answer_ar": "تحقيق أداء تمرير فائق السرعة وبدون أي تهنيج في `LazyColumn` بيعتمد بشكل مباشر على الفهم العميق لـ `key` و `contentType`.\n\nافتراضياً، لو مكتبتش باراميتر `key` في دالة `items()`، كومبوز بتستخدم رقم ترتيب العنصر (Index) كهوية له.\nالكارثة بتظهر لما تضيف عنصر جديد في أول القائمة؛ كل العناصر اللي تحته ترتيبها بيتشفت برقم واحد! كومبوز بتفتكر إن كل العناصر اتغيرت، فترمي كل الـ State المحفوظة، ومكان التمرير يقفز بشكل مزعج، والشاشة تعيد رندرة كل العناصر بدون أي داعٍ.\nلما تحدد `key = { it.id }`، أنت بتربط هوية العنصر ببياناته الحقيقية؛ كومبوز بتعرف إن العنصر مجرد اتحرك مكانه، فبتحافظ على الـ State ومكان التمرير وتشغل أنيميشن تحرك سلس بـ `Modifier.animateItem()`.\n\nأما الـ `contentType` فهو السلاح السري للقوائم غير المتجانسة اللي فيها تصميمات مختلفة (مثلاً: إعلانات، وبوستات، وفواصل).\nبدون `contentType`، لما بوست يخرج من الشاشة وإعلان يدخل مكانه، كومبوز بتضطر تهدم شجرة النودز بالكامل وتبني شجرة جديدة للإعلان من الصفر، وده بيسبب دروب في الفريمات.\nلما تحدد الـ `contentType`، كومبوز بتعمل Pools منفصلة لكل نوع، وتعيد استخدام هيكل الشجرة الجاهز للعناصر المتشابهة في التصميم، وتكتفي بتحديث البيانات فقط.",
        "deep_answer_ar": "تحت الكابوت، الـ `LazyColumn` بتعتمد على معمارية `SubcomposeLayout`؛ يعني مش بترندر القائمة كلها، بل بتقيس وترندر العناصر الظاهرة في شاشة العرض فقط مع مسافة أمان صغيرة (Prefetching).\n\nلما بتحدد `key` مستقر، المحرك بيسجل المفتاح ده في كائن الـ `ItemProvider` الداخلي. أثناء عمليات التعديل أو الحذف، المحرك بيطابق المفاتيح عبر الفريمات وينقل نودز الـ SlotTable القديمة مكانها الجديد بدون ما يعمل لها `Dispose`، وده بيوفر على الـ Garbage Collector عناء تنظيف وإعادة حجز كائنات الذاكرة باستمرار.\n\nأما ميزة `contentType` اللي نزلت في كومبوز الحديثة، فهي مطابقة تماماً لفكرة `getItemViewType` و `RecycledViewPool` في نظام الـ RecyclerView القديم.\nالمحرك بيحتفظ بكاش فرعي للـ Slots غير المستخدمة مصنفة حسب الـ `contentType`. أول ما عنصر جديد يدخل الشاشة، المحرك بيفحص الكاش الخاص بنوعه؛ لو لقى Slot متاح من نفس الـ ContentType، بيعمل له إعادة استخدام فورية بنفس هيكل الشجرة وبدون أي هدم، وبيعمل فقط Recomposition للبيانات المتغيرة داخل النود.\n\nده بيقلل وقت الـ Measure والـ Layout في كل فريم بنسبة تتخطى 40% أثناء التمرير السريع، وبيضمن استقرار التطبيق على 60 فريم كاملة حتى على أضعف الهواتف الاقتصادية، وده بيمنع أي لاج أو سقوط في الفريمات حتى مع القوائم الضخمة التي تحتوي على آلاف العناصر المتنوعة."
    }
}

# ==========================================
# COM-15: What does stability mean for Compose types and parameters?
# ==========================================
DATA["COM-15"] = {
    "concept_en": """Stability in Jetpack Compose is a compile-time and runtime behavioral contract that defines whether a data type guarantees immutable or predictable equality over time. The Compose compiler analyzes all classes and categorizes them as Stable, Immutable, or Unstable. A type is Stable if two instances comparing equal via equals() are guaranteed to notify Compose whenever any internal state mutates, or if the type is completely immutable. Stability directly controls smart skipping: a composable function can be skipped during recomposition only if all of its input parameters are proven Stable. Unstable types force conservative, unconditional recompositions on every frame.""",
    "walkthrough_en": """Inspecting stability categories and fixing unstable data models:
```kotlin
// ❌ UNSTABLE: Contains a mutable 'var' and a raw standard Kotlin List!
// Any composable taking UserProfile will NEVER be skipped!
data class UserProfile(
    var name: String, // 'var' makes class unstable!
    val friends: List<String> // Standard List interface is considered unstable by compiler!
)

// ✅ STABLE / IMMUTABLE: Explicit contract promises compiler data never mutates silently
@Immutable
data class StableUserProfile(
    val name: String, // Immutable val
    val friends: ImmutableList<String> // Kotlinx Immutable Collections guarantee stability!
)

// ✅ Skippable Composable: Both parameters are stable!
@Composable
fun UserCard(
    user: StableUserProfile, // Stable type!
    onFollowClick: () -> Unit // Function types (lambdas) are stable!
) {
    // Compose compiler generates zero-overhead early return skipping for this function!
    Text("User: ${user.name}")
}
```""",
    "short_en": """Stability in Compose is a contract indicating whether a type's equality remains predictable over time. Primitives, Strings, function types, and classes with only val properties of stable types are automatically stable. The compiler marks classes with var properties or standard collections like List as unstable because they can mutate silently. A composable can only be skipped if all its parameters are stable. We enforce stability using @Immutable, @Stable, Kotlinx Immutable Collections, or Strong Skipping Mode.""",
    "structured_en": """Stability is the central compiler mechanism determining whether Jetpack Compose can skip re-executing functions during recomposition.
The Compose compiler inspects every type passed as a composable parameter and assigns it a stability classification based on strict contracts.
An Immutable type guarantees that its public properties will never change after instantiation. Primitives, Strings, and data classes with val fields of other immutable types are automatically inferred as immutable.
A Stable type guarantees that if two instances are equal via equals(), they will remain equal unless Compose is explicitly notified of a mutation, such as through a MutableState field.
Any type that violates these guarantees is classified as Unstable.
The most frequent source of instability is Kotlin's standard collection interfaces, like List, Set, or Map. Because List is a read-only interface rather than an immutable collection, a caller could pass a mutable ArrayList behind the scenes.
The Compose compiler cannot verify that the list will not mutate without its knowledge, so it marks any composable receiving a raw List as unskippable.
To resolve this, engineers wrap lists in @Immutable classes, adopt Kotlinx Immutable Collections, or leverage Kotlin 2.0 Strong Skipping Mode.""",
    "deep_senior_en": """Under the hood, stability inference is performed by the Compose Compiler plugin during the Kotlin frontend IR lowering phase.
The compiler analyzes class declarations and appends synthetic metadata markers, assigning a $stable bit flag to stable classes.
When a composable function is compiled, the compiler inspects every parameter's stability flag. If all parameters are stable, the compiler generates a change-tracking bitmask check at the beginning of the function body.
During recomposition, if the bitmask indicates that all stable parameters evaluate to SAME or have STATIC references, the method executes an early-return opcode, skipping function body execution and avoiding all SlotTable reads and allocations.
If even a single parameter is marked unstable, the compiler flags the parameter as UNCERTAIN. In standard skipping mode, this forces the composable to execute unconditionally, even if the underlying data has not changed.
In modern Compose compilers (Kotlin 2.0+), Google introduced Strong Skipping Mode, enabled by default.
Strong skipping transforms this behavior by allowing composables with unstable parameters to be skipped if their instances compare equal via structural equality (equals()).
Furthermore, developers can configure compiler stability configuration files (stability_config.conf) to mark external third-party classes (like java.time.Instant or external network DTOs) as stable without adding annotations to foreign libraries.""",
    "meta_ar": {
        "id": "COM-15",
        "questionAr": "ماذا يعني مفهوم الاستقرار (Stability) للأنواع والباراميترات في Jetpack Compose؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم معايير الاستقرار (Stable vs Immutable vs Unstable)، وإدراك سبب تصنيف الـ `List` كنوع غير مستقر، واستيعاب تأثير الاستقرار على الـ Smart Skipping، ودور ميزة Strong Skipping Mode وملفات Stability Config.",
        "why_it_matters_ar": "الأنواع غير المستقرة تجبر كومبوز على إعادة تشغيل الشاشات والقوائم بالكامل في كل فريم، مما يسبب بطء التطبيق ونفاذ بطارية المستخدم.",
        "worked_example_ar": "الفرق بين كلاس غير مستقر وكلاس مستقر:\n```kotlin\n// غير مستقر: يحتوي على var وقائمة عادية\ndata class BadUser(var name: String, val tags: List<String>)\n// مستقر 100%: استخدام val ومكتبة ImmutableList\n@Immutable data class GoodUser(val name: String, val tags: ImmutableList<String>)\n```",
        "trade_offs_ar": "استخدام مكتبات الـ Immutability يتطلب إضافة مكتبات جديدة لكوتلن، لكنه يضمن التخطي الذكي ويمنع آلاف عمليات الرندرة الزائدة.",
        "failure_modes_ar": "وضع متغيرات `var` داخل كلاسات البيانات الممررة للواجهة، أو الاعتقاد بأن `List` مستقرة لمجرد أنها Read-only في كوتلن.",
        "production_perspective_ar": "في المشروعات الكبيرة، نعتمد كوتلن 2.0 مع Strong Skipping Mode، ونستخدم ملف `compose_compiler_config.conf` لجعل كلاسات الموديل الخارجية مستقرة تلقائياً.",
        "how_to_answer_ar": "عرف الاستقرار: عقد يضمن للكومبايلر ثبات المساواة عبر الوقت، وصنف الأنواع: Immutable (لا يتغير أبداً)، و Stable (يبلغ كومبوز عند التغيير)، و Unstable (قد يتغير بالخفاء زي List و var)، واشرح ارتباطه المباشر بالـ Smart Skipping وحلوله بـ @Immutable أو Strong Skipping.",
        "talking_points_ar": "عقد الاستقرار والـ Compiler Lowering، والأنواع البدائية مقابل Collections، ومأزق List في كوتلن، ومصفوفة الـ Changed Bitmask، و Strong Skipping Mode.",
        "follow_ups_ar": "- **المحاور:** \"لماذا تعتبر واجهة `List` في كوتلن Unstable رغم أنها لا تحتوي على دوال تعديل زي add()؟\"\n  **المرشح:** \"لأن `List` هي Read-only Interface وليست كائناً غير قابل للتعديل فعلياً؛ ممكن كود خارجي يمرر `ArrayList` ويعدل فيها في الخلفية بدون علم كومبوز.\"\n\n- **المحاور:** \"كيف نصلح استقرار كلاس من مكتبة خارجية تابعة لطرف ثالث دون تعديل الكود المصدري؟\"\n  **المرشح:** \"بنستخدم ملف `stability_config.conf` في الجرادل ونحدد الكلاسات دي كـ Stable، أو نغلفها داخل Data Class مميز بـ `@Immutable`.\"",
        "self_check_ar": "هل عرفت الاستقرار بدقة؟ هل وضحت الفرق بين Stable و Immutable؟ وهل بينت مشكلة List وحلها بالتقنيات الحديثة؟",
        "references_ar": f"- [Compose Stability Explanation](https://developer.android.com/develop/ui/compose/performance/stability) — التوثيق الرسمي لجوجل لاستقرار الأنواع.\n- [Compose Strong Skipping Mode](https://developer.android.com/develop/ui/compose/performance/stability/strongskipping) — التوثيق الرسمي لميزة التخطي القوي.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "الاستقرار (Stability) في كومبوز هو عقد أمان بيفحصه الكومبايلر عشان يعرف هل الكائن قيمته ثابتة ومضمونة مع مرور الوقت ولا لأ. الكومبايلر بيصنف الأنواع لتلات فئات: غير قابلة للتغيير (Immutable) زي الأرقام والنصوص، أو مستقرة (Stable) بتعدل بياناتها عبر قنوات بتبلغ كومبوز زي `MutableState`، أو غير مستقرة (Unstable) زي الكلاسات اللي فيها `var` أو القوائم العادية `List`. القاعدة إن الدالة مينفعش يحصل لها تخطي ذكي (Smart Skipping) إلا لو كانت كل الباراميترات الممررة لها مستقرة تماماً، وإلا كومبوز هتعيد رندرتها في كل فريم بحذر شديد.",
        "best_answer_ar": "مفهوم الاستقرار هو القلب النابض اللي بيتحكم في سرعة وأداء أي تطبيق مبني بـ Jetpack Compose.\n\nالكومبايلر بيحلل كل باراميتر ممرر لدالة الـ Composable ويصنفه هندسياً:\nالنوع الأول هو `Immutable`؛ كائن كل حقوله `val` من أنواع مستقرة، وده بيضمن للكومبايلر إن بياناته مستحيل تتغير بعد إنشائه.\nالنوع الثاني هو `Stable`؛ كائن ممكن تتغير بياناته، لكنه بيضمن إنه لو اتغير هيبلغ نظام كومبوز رسمياً بحدث التغيير، ولو قورن كائنين بـ `equals()` وفضلوا متطابقين هيفضلوا كده للأبد.\nالنوع الثالث هو `Unstable`؛ أي كلاس بيخالف الشروط دي، زي وجود متغير `var`.\n\nالمأزق الكلاسيكي اللي بنسأل عنه دايماً هو الـ `List<T>`. في كوتلن، `List` هي Read-only وليست Immutable؛ الكومبايلر ميعرفش هل الكائن الحقيقي في الذاكرة هو `ArrayList` بيتم التعديل فيه في الخلفية ولا لأ، فعشان يحمي التطبيق من عرض داتا غلط بيصنفها كـ Unstable. النتيجة إن أي شاشة بتستقبل List بتفقد ميزة الـ Smart Skipping وتعيد الرندرة في كل مرة!\n\nالحل في المشروعات الاحترافية هو استخدام `@Immutable` أو مكتبة `kotlinx.collections.immutable`، أو الاعتماد على ميزة Strong Skipping Mode في كوتلن 2.0 اللي بتعمل مقارنة بـ `equals()` وتتخطى الدوال بأمان تام.",
        "deep_answer_ar": "تحت الكابوت، فحص الاستقرار (Stability Inference) بيتم أثناء مرحلة الـ Frontend IR Lowering بواسطة الـ Compose Compiler Plugin.\n\nالكومبايلر بيمسك كل كلاس ويحقن جواه علامة بايت كود اصطناعية اسمها `$stable` بتحدد درجة استقراره. ولما بيترجم دالة Composable، بيفحص مصفوفة الأعلام `changed bitmask` للباراميترات. لو كل الباراميترات مستقرة وقيمها متطابقة مع المسجل في الـ SlotTable، الكومبايلر بينفذ تعليمة `Early Return Opcode` فورية، وده بيتخطى قراءة النودز ورسم الشاشة تماماً في أجزاء من الميكروثانية.\n\nلو باراميتر واحد فقط اتصنف كـ Unstable، الكومبايلر بيجبر قيمة البتات تكون `UNCERTAIN`، وده بيمنع التخطي ويجبر الدالة على إعادة التنفيذ في كل دورة Recomposition.\n\nفي كوتلن 2.0، جوجل غيرت المعادلة بميزة Strong Skipping Mode؛ الميزة دي خلت الكومبايلر يتخطى الدوال حتى لو فيها باراميترات Unstable بشرط تطابقها بمقارنة `equals()` العادية، وحولت كل الـ Lambdas لكائنات محاطة بـ `remember` تلقائياً.\nوعلاوة على كده، وفرت جوجل ملف تكوين اسمه `stability_config.conf` بنقدر نحط فيه كلاسات الموديل الخارجية من مكتبات الطرف الثالث (زي كلاسات التاريخ والشبكة) عشان نصنفها كـ Stable بدون ما نضطر نعدل كود المكتبة نفسها.\n\nوفوق كده، مراجعة تقارير المترجم بشكل دوري في الـ CI بتمنع تسلل أي Unstable Models لطبقة العرض، وبتحافظ على ثبات وسرعة التطبيق مع كل تحديث جديد."
    }
}

# ==========================================
# COM-16: How do you identify avoidable recomposition?
# ==========================================
DATA["COM-16"] = {
    "concept_en": """Identifying avoidable recomposition in Jetpack Compose involves systematically auditing UI trees using developer tooling, compiler metrics, and runtime profiling. Avoidable recompositions occur when composable functions re-execute despite their visually rendered content remaining unchanged, typically triggered by unstable parameter types, frequent ambient state reads hoisted unnecessarily high, or instantiating unmemoized objects inside composable bodies. Engineers diagnose these regressions using the Android Studio Layout Inspector recomposition counters, Compose Compiler metrics reports, and runtime recomposition highlighting modifiers.""",
    "walkthrough_en": """Diagnosing and eliminating an avoidable recomposition loop:
```kotlin
// ❌ AVOIDABLE RECOMPOSITION: Reading scroll position too early in parent hierarchy!
// The entire ParentScreen recomposes on every single scrolled pixel!
@Composable
fun BadParentScreen(listState: LazyListState) {
    // ❌ ANTI-PATTERN: Reading scroll offset directly causes entire screen to recompose on every pixel!
    val offset = listState.firstVisibleItemScrollOffset

    HeaderView(offset = offset)
    LazyColumn(state = listState) { /* items */ }
}

// ✅ FIXED: Defer state reads using lambda modifiers or derivedStateOf!
@Composable
fun OptimizedParentScreen(listState: LazyListState) {
    // Reading state is deferred directly to the layout phase via a lambda!
    HeaderView(
        modifier = Modifier.offset {
            // State read happens in LAYOUT phase, completely bypassing COMPOSITION phase!
            IntOffset(x = 0, y = listState.firstVisibleItemScrollOffset)
        }
    )
    LazyColumn(state = listState) { /* items */ }
}
```""",
    "short_en": """We identify avoidable recompositions using Android Studio Layout Inspector, Compose Compiler metrics reports, and runtime profiling tools. Layout Inspector displays real-time recomposition and skip counts for every node. Compiler metrics generate reports flagging restartable and skippable composables and highlighting unstable parameters. Common fixes include stabilizing data models, wrapping expensive objects in remember, using derivedStateOf, and deferring state reads to the layout phase via lambda modifiers.""",
    "structured_en": """Diagnosing and eliminating avoidable recomposition is a core discipline for senior Android engineers ensuring fluid 60fps or 120fps UI performance.
Avoidable recompositions occur when composables re-run without producing any visual change.
The primary diagnostic tool is Android Studio's Layout Inspector.
When connected to a running debug build, Layout Inspector overlays live Recomposition Count and Skip Count columns beside the component tree.
If a component's recomposition count increments continuously during idle states or simple scrolling while its skip count remains zero, that composable is suffering from avoidable recomposition.
The second essential tool is Compose Compiler Metrics.
By passing compiler flags like reportsDestination in Gradle, the compiler generates text files detailing which composables are skippable versus restartable-only, explicitly listing unstable parameters like standard Lists or third-party classes.
The third diagnostic technique is using debug highlighting modifiers like recomposeHighlighter, which flashes colored bounding boxes around composables as they recompose.
Once identified, engineers resolve these bottlenecks by wrapping collections in @Immutable wrappers, deferring state reads to layout or draw phases, and memoizing lambdas and calculations with remember.""",
    "deep_senior_en": """Under the hood, diagnosing recompositions requires understanding Compose's three distinct rendering phases: Composition, Layout, and Draw.
Avoidable recomposition regressions almost always stem from reading high-frequency state during the Composition phase when the read could have been deferred to the Layout or Draw phases.
When you read a SnapshotState primitive (such as scroll offset or animation progress) directly in a composable function body, Compose registers a dependency inside the current RecomposeScope. Every frame tick invalidates that scope, forcing the Compose runtime to re-execute the function, allocate new layout nodes, and reconcile the SlotTable.
By deferring the state read using lambda-based modifiers—such as Modifier.offset { IntOffset(0, state.value) } or Modifier.drawBehind { drawCircle(...) }—the state read is deferred past the Composition phase entirely.
When the state mutates, Compose skips the Composition phase and invalidates only the LayoutNode or RenderNode directly on the hardware canvas, achieving near-zero CPU overhead.
Furthermore, analyzing compiler metrics reports (specifically *-composables.txt and *-classes.txt) reveals stability signatures.
If a function is marked restartable but not skippable, the report pinpoints the exact culprit parameter marked as unstable.
Senior engineers integrate compiler metrics audits into CI pipelines to fail pull requests that introduce accidental stability regressions into critical user journeys. This automated enforcement guarantees that production apps maintain zero-jank UI responsiveness across all supported device tiers.""",
    "meta_ar": {
        "id": "COM-16",
        "questionAr": "كيف تحدد وتعالج عمليات إعادة التركيب غير الضرورية (Avoidable Recomposition) في Compose؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على استخدام أدوات قياس أداء كومبوز (Layout Inspector و Compose Compiler Metrics)، وفهم مراحل الرندرة الثلاث (Composition, Layout, Draw)، وتأجيل قراءة الحالة عبر الـ Lambdas.",
        "why_it_matters_ar": "عمليات إعادة التركيب الزائدة تؤدي لتشنج الشاشة (UI Jank) وسخونة المعالج واستهلاك البطارية بمجرد لمس الشاشة أو التمرير الخفيف.",
        "worked_example_ar": "تأجيل قراءة الحالة لمنع الـ Recomposition:\n```kotlin\n// ❌ سيئ: يعيد رندرة الدالة بالكامل مع كل بكسل تمرير\nModifier.offset(y = listState.firstVisibleItemScrollOffset.dp)\n// ✅ ممتاز: يقرأ الحالة في مرحلة الـ Layout فقط ويتخطى الـ Composition!\nModifier.offset { IntOffset(0, listState.firstVisibleItemScrollOffset) }\n```",
        "trade_offs_ar": "فحص وتحليل المقاييس يتطلب تشغيل أدوات خاصة وضبط إعدادات الجرادل، لكنه الإجراء الحاسم لضمان استقرار التطبيق على 60 إطاراً في الثانية.",
        "failure_modes_ar": "قراءة متغيرات الأنيميشن أو التمرير السريع داخل جسم دالة الكومبوزابل مباشرة، مما يجبر الشاشة على إعادة الرندرة 120 مرة في الثانية.",
        "production_perspective_ar": "في المشروعات الكبيرة، نعتمد تقارير Compose Compiler Metrics كجزء من فحص الـ CI لمنع دمج أي PR يحول شاشة رئيسية إلى Unskippable.",
        "how_to_answer_ar": "وضح أدوات التشخيص الثلاث: أولاً Layout Inspector لمراقبة عدادات Recomposition و Skips، ثانياً Compose Compiler Metrics لكشف الباراميترات غير المستقرة، واشرح مراحل الرندرة الثلاث (Composition, Layout, Draw) وكيفية تأجيل قراءة الحالة بـ Lambda Modifiers لمنع تشغيل الدالة أصلاً.",
        "talking_points_ar": "عدادات Layout Inspector، وتقارير Compiler Metrics، ومراحل الرندرة الثلاث، وتأجيل قراءة الـ State بـ Lambdas، ومعدل الـ Skipping.",
        "follow_ups_ar": "- **المحاور:** \"ما هو الفرق بين مرحلة الـ Composition ومرحلة الـ Layout في قراءة الـ State؟\"\n  **المرشح:** \"لو قرأت الحالة في جسم الدالة، كومبوز هتعيد تشغيل الدالة كلها في مرحلة الـ Composition، بينما لو قرأتها جوه Lambda في الـ Modifier، كومبوز هتتخطى مرحلة الكومبوزيشن وتروح تعدل مكان العنصر في الـ Layout مباشرة بدون إعادة تشغيل الدالة.\"\n\n- **المحاور:** \"كيف تفعل تقارير Compose Compiler Metrics في مشروعك؟\"\n  **المرشح:** \"بنضيف إعدادات `reportsDestination` و `metricsDestination` في ملف build.gradle لمترجم كومبوز، وبنراجع ملفات التكست الناتجة لمعرفة الـ Composables غير القابلة للتخطي.\"",
        "self_check_ar": "هل شرحت أدوات القياس كـ Layout Inspector والمقاييس؟ هل بينت مراحل الرندرة الثلاث؟ وهل وضحت حل تأجيل القراءة بـ Lambdas؟",
        "references_ar": f"- [Compose Performance: Inspecting recomposition](https://developer.android.com/develop/ui/compose/performance/layout-inspector) — التوثيق الرسمي لاستخدام Layout Inspector.\n- [Compose Compiler Metrics Guide](https://github.com/androidx/androidx/blob/androidx-main/compose/compiler/design/compiler-metrics.md) — دليل مقاييس مترجم كومبوز الرسمي.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "بنحدد عمليات الـ Recomposition غير الضرورية باستخدام تلات أدوات رئيسية: أولاً أداة Layout Inspector في أندرويد ستوديو اللي بتعرض عدادات حية لعدد مرات إعادة الرندرة (Recomposition Counts) وعدد مرات التخطي (Skip Counts). ثانياً تقارير Compose Compiler Metrics اللي بتولد ملفات توضح الدوال غير القابلة للتخطي والباراميترات غير المستقرة. ثالثاً استخدام Recomposition Highlighters لإظهار وميض ملون على الشاشات التي تعيد الرندرة. وبنعالج المشكلة بتثبيت كلاسات الموديل بـ `@Immutable`، واستخدام `derivedStateOf`، وتأجيل قراءة الحالة لمرحلة الـ Layout عبر الـ Lambda Modifiers.",
        "best_answer_ar": "اكتشاف وعلاج الـ Avoidable Recomposition هو الاختبار الحقيقي لمهندس الأندرويد السينيور لضمان سلاسة التطبيق على 60 و 120 فريم.\n\nالعملية بتبدأ بالتشخيص عبر أداتين أساسيتين:\nالأداة الأولى هي Layout Inspector؛ بنوصل الهاتف بوضع الـ Debug ونفتح الشاشة؛ بتلاقي جدول فيه عمودين: Recomposition Count و Skip Count. لو الشاشة ثابتة مفيهاش تفاعل ولقيت العداد بيزيد باستمرار، أو مع التمرير البسيط بتلاقي الكومبوزابل بيعيد تشغيل نفسه وعدد الـ Skips صفر، هنا فوراً بنعرف إن فيه رندرة غير مبررة.\n\nالأداة الثانية هي Compose Compiler Metrics؛ بنفعلها في الجرادل فبتطلع تقرير نصي كامل بيصنف كل دالة: هل هي Skippable ولا Restartable فقط، وبيحدد بالاسم الباراميترات غير المستقرة زي `List` أو كلاسات خارجية.\n\nالعلاج الأكثر احترافية بيعتمد على فهم مراحل الرندرة الثلاث: التكوين (Composition)، ثم القياس والتموضع (Layout)، ثم الرسم (Draw).\nالكارثة الأكبر إن المطور بيقرأ قيمة التمرير أو الأنيميشن في جسم الدالة مباشرة؛ ده بيجبر كومبوز تعيد تشغيل الدالة في مرحلة الـ Composition مع كل بكسل يتحرك. الحل هو تأجيل قراءة الحالة لمرحلة الـ Layout باستخدام Lambda Modifiers زي `Modifier.offset { IntOffset(0, scroll.value) }`؛ بكده كومبوز بتتخطى مرحلة الـ Composition تماماً وتعدل مكان العنصر على الكانفاس مباشرة بصفر استهلاك للمعالج.",
        "deep_answer_ar": "تحت الكابوت، لما بتقرأ متغير من نوع `SnapshotState` داخل جسم دالة `@Composable`، نظام الـ Snapshot بيسجل تبعية (Read Dependency) ويربط المتغير ده بكائن الـ `RecomposeScope` الخاص بالدالة في الـ SlotTable. أول ما المتغير يتغير (زي بكسلات التمرير السريع)، الرنتايم بيعلم النطاق ده كـ Invalidated، وده بيجبر المعالج على إعادة تشغيل الدالة وبناء كائنات جديدة وإجراء مقارنات شجرة النودز بالكامل.\n\nالسر الهندسي لتفادي ده هو تفهم الفرق بين Phases كومبوز الثلاث:\nفي مرحلة الـ Composition: بنشغل كود كوتلن عشان نبني الـ Layout Nodes.\nفي مرحلة الـ Layout: بنقيس النودز دي ونحدد إحداثياتها (X, Y).\nوفي مرحلة الـ Draw: بنرسم البكسلات على كائن הـ Canvas الخاص بالعتاد.\n\nلما بتستخدم دالة بتاخد Lambda زي `Modifier.offset { ... }` أو `Modifier.drawBehind { ... }`، أنت بتنقل قراءة متغير الحالة من مرحلة الـ Composition إلى مرحلة الـ Layout أو الـ Draw مباشرة. محرك كومبوز ذكي جداً؛ لما الحالة تتغير، بيتخطى مرحلة الـ Composition تماماً ومبيشغلش دالة الكومبوزابل، بل بيروح يعدل إحداثيات الـ `LayoutNode` في كود C++ الداخلي ويرسم على الشاشة فوراً، وده بيخفض زمن معالجة الفريم من 16ms لأقل من 2ms ويوفر تجربة استخدام فائقة السلاسة."
    }
}

# ==========================================
# COM-17: How do you optimize a long list and expensive calculations?
# ==========================================
DATA["COM-17"] = {
    "concept_en": """Optimizing long lists and heavy calculations in Jetpack Compose requires a layered architectural approach addressing lazy allocation, algorithmic memoization, and rendering phase separation. Long lists are optimized by pairing LazyColumn with stable unique keys, granular content types, and windowed prefetching. Expensive calculations—such as currency conversions, date parsing, or heavy cryptographic hashing—must be strictly memoized using remember with explicit cache keys or offloaded to background Dispatchers.Default coroutines inside architecture ViewModels, ensuring that the main UI rendering thread never exceeds the 16.6ms per-frame budget.""",
    "walkthrough_en": """Optimizing heavy calculations and item recycling in a financial transactions list:
```kotlin
@Composable
fun TransactionRow(
    transaction: Transaction,
    taxRate: Double,
    modifier: Modifier = Modifier
) {
    // 1. MEMOIZE EXPENSIVE COMPUTATIONS: Only recalculates when transaction or taxRate changes!
    // Avoids running heavy date formatting and tax math on every recomposition pass!
    val formattedSummary = remember(transaction.id, transaction.amount, taxRate) {
        val totalWithTax = transaction.amount * (1.0 + taxRate)
        val formattedDate = DateTimeFormatter.ISO_INSTANT.format(transaction.timestamp)
        "Total: \\$$totalWithTax on $formattedDate"
    }

    Row(modifier = modifier.fillMaxWidth().padding(12.dp)) {
        Text(transaction.title, modifier = Modifier.weight(1f))
        Text(formattedSummary, style = MaterialTheme.typography.bodyMedium)
    }
}

@Composable
fun TransactionList(transactions: List<Transaction>, taxRate: Double) {
    LazyColumn {
        items(
            items = transactions,
            key = { it.id }, // Stable key avoids layout thrashing
            contentType = { "TRANSACTION_ITEM" } // ContentType reuses layout structures
        ) { transaction ->
            TransactionRow(transaction = transaction, taxRate = taxRate)
        }
    }
}
```""",
    "short_en": """We optimize long lists using LazyColumn with stable keys to preserve scroll state and content types to reuse layout nodes. Expensive calculations are memoized using remember with explicit keys so they only re-run when inputs change, or offloaded to Dispatchers.Default in the ViewModel. We also use derivedStateOf to filter high-frequency scroll observations and defer state reads to the layout or draw phases using lambda modifiers to eliminate unnecessary recompositions.""",
    "structured_en": """Ensuring seamless, jitter-free performance in data-heavy Jetpack Compose lists requires rigorous computational discipline across both presentation and data layers.
In a long list, performance bottlenecks typically stem from three mistakes: recalculating expensive data during composition, failing to provide list recycling metadata, and triggering viewport-wide recompositions during scrolling.
To optimize calculations, any non-trivial logic—such as string formatting, date parsing, sorting, or math operations—must never run directly inside the composable body.
If the calculation must exist in the UI layer, wrap it in remember(key1, key2) with explicit dependencies, guaranteeing it re-executes only when inputs mutate.
For heavy data transformations, perform the calculations upstream inside the ViewModel on Dispatchers.Default, exposing pre-formatted immutable display models to the UI.
To optimize list scrolling, configure LazyColumn with unique stable keys and explicit contentType identifiers.
This enables Compose to move existing SlotTable nodes rather than recreating them and allows SubcomposeLayout to recycle pre-measured layouts.
Finally, when observing scroll state (such as showing a scroll-to-top button), wrap the threshold check in derivedStateOf to prevent pixel-by-pixel recomposition.""",
    "deep_senior_en": """Under the hood, optimizing long lists is an exercise in controlling allocations within the 16.6-millisecond (60fps) or 8.3-millisecond (120fps) frame deadline enforced by Choreographer VSYNC pulses.
When an unmemoized calculation sits inside a composable body, every recomposition pass executes that code synchronously on the Main thread.
If 50 visible items each parse a date string taking 0.5ms, the list consumes 25ms of CPU time on the main thread, resulting in immediate frame drops and jank.
Wrapping logic in remember caches the calculated result in the SlotTable's current slot; subsequent passes inspect slot equality and return the cached reference in O(1) time without allocating temporary heap objects.
In the Lazy list layout pipeline, SubcomposeLayout coordinates with AndroidX LazyLayoutPrefetcher.
When prefetching is enabled, Compose uses idle frame windows to pre-measure and pre-compose incoming items before they physically cross into the viewport boundary.
By providing stable keys and contentTypes, Compose's prefetcher can accurately match cached SubcomposeSlots, drastically reducing the measurement duration when the user flings the list.
Furthermore, senior engineers avoid reading state values inside modifier chains, using lambda variants like Modifier.drawWithCache or Modifier.graphicsLayer to perform visual transformations on the RenderNode directly without touching the CPU composition pipeline. This structural discipline ensures zero frame drops even during intense flings across deeply nested data sets.""",
    "meta_ar": {
        "id": "COM-17",
        "questionAr": "كيف تُحسن أداء القوائم الطويلة والعمليات الحسابية الثقيلة في Jetpack Compose؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على تحسين أداء القوائم المعقدة، واستخدام `remember` بمفاتيح محددة لتكييش الحسابات الثقيلة، ونقل المعالجة لـ `Dispatchers.Default`، وتطبيق تقنيات `contentType` و `derivedStateOf` وتأجيل الرندرة.",
        "why_it_matters_ar": "إجراء عمليات تحويل نصوص أو تواريخ داخل دالة القائمة مباشرة يستهلك وقت المعالج على الخيط الرئيسي، مما يؤدي لسقوط الفريمات (Dropped Frames) وتجربة مستخدم بطيئة وغير مقبولة.",
        "worked_example_ar": "تكييش الحسابات وضبط القوائم:\n```kotlin\n// 1. تكييش الحسبة الثقيلة بمفاتيح صريحة\nval summary = remember(item.id, rate) { calculateTax(item.amount, rate) }\n// 2. ضبط القائمة بمفاتيح ونوع المحتوى\nLazyColumn { items(list, key = { it.id }, contentType = { it.type }) { ... } }\n```",
        "trade_offs_ar": "استخدام `remember` يستهلك مساحة صغيرة في الـ SlotTable، لكنه يوفر ملايين دورات المعالج ويمنع تجميد الشاشة أثناء التمرير السريع.",
        "failure_modes_ar": "عمل فرز (Sorting) لقائمة أو تحويل صيغ التواريخ (Date Formatting) داخل جسم الكومبوزابل مباشرة في كل فريم.",
        "production_perspective_ar": "في المشروعات الكبيرة، نلزم المطورين بتجهيز البيانات وتنسيق النصوص مسبقاً في الـ ViewModel داخل `Dispatchers.Default`، لتصل الشاشة كـ UI Models جاهزة للعرض فوراً بصفر عمليات حسابية.",
        "how_to_answer_ar": "قسم الحل لثلاثة محاور: أولاً القوائم بضبط `key` و `contentType` في LazyColumn، ثانياً العمليات الحسابية بتكييشها بـ `remember(keys)` أو نقلها للـ ViewModel على `Dispatchers.Default`، وثالثاً تصفية التمرير بـ `derivedStateOf` وتأجيل الرندرة بـ Lambda Modifiers لحماية ميزانية الـ 16ms لكل فريم.",
        "talking_points_ar": "ميزانية الـ 16.6ms لكل فريم، وتكييش الـ remember بمفاتيح، ونقل المعالجة لـ ViewModel و Dispatchers.Default، ودور LazyLayoutPrefetcher، وفلترة التمرير بـ derivedStateOf.",
        "follow_ups_ar": "- **المحاور:** \"أين هو المكان الأفضل هندسياً لإجراء عمليات معالجة البيانات وتنسيق العملات؟\"\n  **المرشح:** \"المكان الأفضل هو الـ ViewModel على `Dispatchers.Default`؛ بحيث البيانات تخرج للشاشة جاهزة كـ Formatted Strings، والكومبوزابل ميعملش أي عمليات حسابية.\"\n\n- **المحاور:** \"كيف تساعد ميزة الـ Prefetching في LazyColumn على تحسين التمرير؟\"\n  **المرشح:** \"كومبوز بتستغل أجزاء الفراغ الزمني في الفريم الحالي عشان تقيس وتجهز العنصر التالي في القائمة قبل ما يظهر للمستخدم في الشاشة، فلما يدخل الشاشة يترسم فوراً بدون تأخير.\"",
        "self_check_ar": "هل غطيت تحسين القوائم والحسابات الثقيلة؟ هل شرحت دور remember بمفاتيح؟ وهل ذكرت ميزانية الـ 16ms ونقل الشغل لـ Dispatchers.Default؟",
        "references_ar": f"- [Jetpack Compose Performance Guide](https://developer.android.com/develop/ui/compose/performance) — الدليل الرسمي لتحسين أداء كومبوز.\n- [Best practices for Compose lists](https://developer.android.com/develop/ui/compose/lists) — أفضل الممارسات للقوائم وسرعة التمرير.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "بنحسن أداء القوائم الطويلة والحسابات الثقيلة باتباع معمارية محكمة من تلات خطوات: أولاً في القوائم، بنستخدم `LazyColumn` مع تحديد مفاتيح مستقرة `key` لكل عنصر ونوع المحتوى `contentType` لإعادة استخدام قوالب النودز في الذاكرة. ثانياً في العمليات الحسابية، بنمنع تماماً وضع أي كود بطيء (زي تنسيق التواريخ أو الفرز) في جسم الدالة مباشرة، وبنكّيش النتيجة بـ `remember(key1, key2)` أو الأفضل بننقلها للـ ViewModel على `Dispatchers.Default` عشان توصل للشاشة جاهزة للعرض فوراً. ثالثاً بنستخدم `derivedStateOf` لمراقبة التمرير لتفادي إعادة الرندرة مع كل بكسل وحماية ميزانية الـ 16ms لكل فريم.",
        "best_answer_ar": "تحسين الأداء في القوائم الضخمة والحسابات المعقدة هو المعيار الأساسي لضمان تجربة مستخدم حريرية بدون سقوط أي فريم من الـ 60 أو 120 فريم في الثانية.\n\nالمعادلة الهندسية بتنقسم لتلات محاور:\nالمحور الأول: العمليات الحسابية؛ أكبر خطأ بنشوفه هو إن المطور يعمل `SimpleDateFormat` أو `BigDecimal math` داخل جسم دالة الكومبوزابل. الكود ده بيتكرر في كل رندرة لكل عنصر في القائمة! لو الحسبة لازم تكون في الواجهة، بنغلفها بـ `remember(key)` بمفاتيح صريحة، فالنتيجة بتتحفظ ومبتتحسبش تاني إلا لو المفتاح اتغير. والحل الهندسي الأرقى في كود الإنتاج هو نقل كل الحسابات دي للـ ViewModel وتشغيلها على خلفية `Dispatchers.Default`، بحيث الشاشة تستقبل داتا كلاس جاهز فيه نصوص معروضة مباشرة.\n\nالمحور الثاني: كفاءة القوائم؛ بنلزم استخدام `key = { it.id }` عشان نمنع القفز وضياع الحالة، وبنحدد `contentType` عشان نسمح لمحرك كومبوز بإعادة تدوير النودز الجاهزة في الذاكرة بدون هدم وبناء.\n\nالمحور الثالث: عزل الرندرة؛ بنراقب التمرير بـ `derivedStateOf` فقط، وبنستخدم Lambda Modifiers زي `Modifier.graphicsLayer` أو `Modifier.drawWithCache` عشان التعديلات البصرية تتم مباشرة على كارت الشاشة بدون استهلاك وقت المعالج الرئيسي.",
        "deep_answer_ar": "تحت الكابوت، كل فريم شاشة على 60Hz له ميزانية زمنية صارمة قدرها 16.6 ميلي ثانية (أو 8.3ms على شاشات 120Hz) بيحكمها نبضات الـ VSYNC الخاصة بالمعالج.\nلو عندك 30 عنصر ظاهرين وكل عنصر بيعمل عملية حسابية صغيرة بتاخد 0.5ms، إجمالي الوقت المستهلك على الخيط الرئيسي هيكون 15ms، وده هيؤدي فوراً لتجاوز الميزانية وسقوط فريمات (Jank).\n\nاستخدام `remember` مع مفاتيح بيخزن القيمة الناتجة في الـ SlotTable، وفي الفريمات التالية بيعمل فحص مساواة سريع O(1) ويرجع المرجع المتكيّش بدون حجز كائنات جديدة في الـ Heap، وده بيوفر ضغطاً ضخماً على الـ Garbage Collector.\n\nوفوق كده، معمارية `LazyColumn` بتتعاون مع مكون ذكي اسمه `LazyLayoutPrefetcher`.\nالمكون ده بيستغل الفترات الميتة اللي بيكون فيها المعالج فاضي في الفريم الحالي، ويروح يقيس ويركب العناصر اللي دورها يظهر في التمرير قبل ما تلمس حافة الشاشة. لما تكون محدد `key` و `contentType`، الـ Prefetcher بيقدر يلاقي Slots جاهزة من نفس النوع في الكاش، فيقيسها في زمن شبه معدوم، ولما المستخدم يعمل Scroll عنيف (Fling) يلاقي كل العناصر جاهزة ومرسومة بسلاسة مطلقة وبدون أي تقطيع.\n\nوعلاوة على كده، نقل الحسابات الثقيلة لـ `Dispatchers.Default` بيضمن إن الخيط الرئيسي يفضل مفرغ تماماً لاستقبال لمسات المستخدم وتحديث الفريمات في ميعادها المحدد بدون أي تعطيل."
    }
}

# ==========================================
# COM-18: What are Route Composable and Screen Composable?
# ==========================================
DATA["COM-18"] = {
    "concept_en": """The Route Composable and Screen Composable pattern is an industry-standard architectural separation of concerns in Jetpack Compose applications. A Route Composable (also known as a Destination or Stateful Composable) serves as the integration orchestrator: it sits at the navigation boundary, resolves destination arguments, injects the architecture ViewModel (via hiltViewModel()), collects reactive UI state with lifecycle awareness, and maps user action lambdas to navigation destinations or ViewModel intents. In contrast, a Screen Composable (Stateless Composable) is a pure presentation component that accepts strictly immutable state data and lambda callbacks, remaining completely decoupled from ViewModels, navigation controllers, and Android framework lifecycles.""",
    "walkthrough_en": """Architectural separation between Route and Screen composables:
```kotlin
// 1. STATELESS SCREEN COMPOSABLE: Pure UI, highly previewable, zero Android framework dependencies
@Composable
fun OrderDetailsScreen(
    state: OrderDetailsUiState,
    onBackClick: () -> Unit,
    onCancelOrder: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    Scaffold(modifier = modifier) { padding ->
        Column(modifier = Modifier.padding(padding).padding(16.dp)) {
            Text("Order #${state.orderId}", style = MaterialTheme.typography.titleLarge)
            Text("Status: ${state.status}")
            Button(onClick = { onCancelOrder(state.orderId) }) { Text("Cancel Order") }
        }
    }
}

// 2. STATEFUL ROUTE COMPOSABLE: Coordinates ViewModel, Navigation, and Lifecycle
@Composable
fun OrderDetailsRoute(
    onNavigateBack: () -> Unit,
    viewModel: OrderDetailsViewModel = hiltViewModel()
) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()

    OrderDetailsScreen(
        state = state,
        onBackClick = onNavigateBack,
        onCancelOrder = { orderId -> viewModel.cancelOrder(orderId) }
    )
}

// 3. COMPOSE PREVIEW: Works instantly without ViewModels or Mocking!
@Preview(showBackground = true)
@Composable
private fun OrderDetailsScreenPreview() {
    OrderDetailsScreen(
        state = OrderDetailsUiState(orderId = "9942", status = "Shipped"),
        onBackClick = {},
        onCancelOrder = {}
    )
}
```""",
    "short_en": """The Route Composable is stateful and acts as the orchestrator at the navigation boundary, injecting the ViewModel, collecting StateFlow with lifecycle awareness, and handling navigation callbacks. The Screen Composable is completely stateless and handles pure presentation, accepting immutable UI state and plain lambda callbacks. This separation enables seamless Compose Previews, simplifies screenshot and JVM unit testing, and maximizes component reusability across phone, tablet, and foldable layouts.""",
    "structured_en": """Separating composables into Route and Screen layers is an enterprise architectural pattern recommended by Google to ensure clean modularity and testability.
In unorganized codebases, developers often create monolithic composables that directly inject ViewModels, call navController.navigate(), and render UI elements simultaneously.
This anti-pattern creates severe friction: the screen cannot be rendered in Android Studio @Preview without extensive ViewModel mocking, unit testing requires instrumented Android devices, and reusing the UI in another container is impossible.
The Route/Screen pattern cleanly splits these responsibilities.
The Route Composable is the stateful coordinator.
It is declared in the navigation graph, extracts navigation route arguments, obtains the scoped ViewModel via Hilt, and collects UI state using collectAsStateWithLifecycle().
It translates incoming state into domain models and passes them down.
The Screen Composable is the stateless presenter.
It accepts only an immutable UiState object and raw lambda callbacks like onAction.
It has zero knowledge of ViewModels, Navigation, or Android platform APIs.
Because it is a pure function, developers can preview it instantly across light and dark themes in Android Studio, execute rapid JVM screenshot tests using Paparazzi or Roborazzi, and reuse it inside multi-pane layouts on foldables.""",
    "deep_senior_en": """Under the hood, the Route/Screen architectural split optimizes both developer velocity and Compose Compiler runtime efficiency.
From a compiler perspective, the Screen Composable represents an optimal candidate for smart skipping.
Because its inputs consist exclusively of an immutable UiState data class and stable function types (lambdas), the Compose compiler generates an optimized changed bitmask check. If the parent Route recomposes but the collected UiState instance remains referentially or structurally equal, the Screen Composable executes an immediate early return, skipping entire layout subtrees.
If the ViewModel were passed directly into the Screen Composable, the compiler would encounter an unstable, complex object, forcing conservative recomposition passes on every frame tick.
From an automated testing standpoint, this architectural pattern provides a massive cost reduction.
Stateless Screen composables can be fully tested on the JVM using Compose UI test APIs (createComposeRule()) or screenshot testing engines without spinning up Hilt dependency injection graphs, mock WebServers, or Robolectric shadows.
Tests simply inject static data fixtures and assert that clicking buttons fires the expected lambda callback payloads.
Furthermore, this separation facilitates modern adaptive design; the same stateless Screen composable can be displayed in a single-column layout on mobile, or hosted alongside a list in a two-pane scaffold on foldables and tablets, with zero refactoring of presentation logic.""",
    "meta_ar": {
        "id": "COM-18",
        "questionAr": "ما هو الفرق بين دالة Route Composable ودالة Screen Composable في كومبوز؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم معمارية فصل الشاشات (Stateful Route vs Stateless Screen)، وتطبيق مبادئ الـ Clean Architecture، وتسهيل عمل الـ Previews واختبارات الـ JVM، وتفعيل الـ Smart Skipping بتجنب تمرير الـ ViewModel.",
        "why_it_matters_ar": "دمج الـ ViewModel والـ Navigation داخل الشاشة مباشرة يجعل من المستحيل معاينتها في `@Preview`، ويعطل اختبارات الـ Unit Tests، ويجعل إعادة استخدام الواجهة في شاشات التابلت أو الأجهزة القابلة للطي مستحيلة.",
        "worked_example_ar": "الفصل بين Route و Screen:\n```kotlin\n// Stateless Screen: واجهة نقية تستقبل داتا و lambdas فقط\n@Composable fun UserScreen(state: UserState, onSave: () -> Unit)\n// Stateful Route: يربط الـ ViewModel والـ Navigation مع الشاشة\n@Composable fun UserRoute(vm: UserViewModel = hiltViewModel()) {\n    val state by vm.state.collectAsStateWithLifecycle()\n    UserScreen(state = state, onSave = { vm.save() })\n}\n```",
        "trade_offs_ar": "يتطلب كتابة دالتين لكل شاشة، لكنه يوفر استقلالية تامة للشاشة ويسمح بمعاينتها فوراً وتشغيل اختبارات الـ Screenshot بدون محاكي.",
        "failure_modes_ar": "تمرير كائن `ViewModel` داخل دالة الـ Composable التقديمية، مما يدمر ميزة الـ Previews والـ Skipping.",
        "production_perspective_ar": "في المشروعات الكبيرة، نعتمد هذه المعمارية كمعيار إلزامي صارم؛ لا يدخل أي ViewModel أو NavController تحت مستوى الـ Route، وكل شاشة يجب أن تمتلك `@Preview` مستقل.",
        "how_to_answer_ar": "عرف الـ Route Composable: المكون المسؤول عن التنسيق وحقن الـ ViewModel وجمع الحالة بـ collectAsStateWithLifecycle وإدارة التنقل، وعرف الـ Screen Composable: المكون النقي المسؤول عن العرض ويستقبل فقط State غير قابل للتعديل و Lambdas، واشرح فوائد الفصل للـ Previews والاختبارات والـ Skipping.",
        "talking_points_ar": "مفهوم Stateful vs Stateless، وتسهيل Android Studio Previews، وتجنب تمرير الـ ViewModel للحفاظ على الـ Skipping، واختبارات الـ JVM و Roborazzi، ودعم الـ Adaptive Layouts.",
        "follow_ups_ar": "- **المحاور:** \"لماذا لا نمرر كائن الـ ViewModel مباشرة لدالة الـ Screen Composable؟\"\n  **المرشح:** \"لأنه كائن غير مستقر بيعطل الـ Smart Skipping، وبيمنع تشغيل الـ `@Preview` تماماً في أندرويد ستوديو، وبيجبرك تعمل Mocking معقد في كل اختبار واجهة.\"\n\n- **المحاور:** \"كيف يساعد هذا الفصل في بناء شاشات متكيفة (Adaptive Layouts) للأجهزة اللوحية؟\"\n  **المرشح:** \"نفس دالة الـ Screen النقية ممكن نعرضها كشاشة كاملة في الموبايل، أو نحطها كعمود جانبي بجانب القائمة في التابلت بدون كتابة سطر كود واحد إضافي في الواجهة.\"",
        "self_check_ar": "هل وضحت الفارق بين الـ Route والـ Screen؟ هل بينت عيوب تمرير الـ ViewModel؟ وهل شرحت الفائدة لاختبارات الـ JVM والمعاينة؟",
        "references_ar": f"- [Android Architecture: UI Layer](https://developer.android.com/topic/architecture/ui-layer) — الدليل الرسمي لجوجل لمعمارية طبقة الواجهة.\n- [Compose State Hoisting Patterns](https://developer.android.com/develop/ui/compose/state#state-hoisting) — دليل رفع الحالة وتصميم الدوال النقية.",
        "quick_answer_ar": "الفرق الجوهري هو فصل المسؤوليات بين التنسيق والعرض: دالة `Route Composable` هي دالة محملة بالحالة (Stateful) بتقف على حدود التنقل؛ بتحقن الـ ViewModel باستخدام Hilt، وبتجمع تدفق الحالة بـ `collectAsStateWithLifecycle()`، وبتربط أحداث المستخدم بالـ Navigation والـ ViewModel. أما دالة `Screen Composable` فهي دالة نقية وخالية من الحالة (Stateless) ومسؤولة حصرياً عن العرض والتصميم؛ بتستقبل كائن حالة غير قابل للتعديل (Immutable State) ودوال كولباك (Lambdas) فقط. الفصل ده بيخلي الشاشة قابلة للمعاينة الفورية في `@Preview`، وسهلة جداً في الاختبار على الـ JVM، ومثالية لإعادة الاستخدام عبر مختلف أحجام الشاشات.",
        "best_answer_ar": "نمط الـ Route والـ Screen هو واحد من أهم المعايير المعمارية الحديثة التي تفرضها جوجل في بناء تطبيقات أندرويد الاحترافية باستخدام Jetpack Compose.\n\nفي الكود غير المنظم، المطور بيعمل دالة ضخمة بتطلب الـ ViewModel بـ `hiltViewModel()`، وبتنادي `navController.navigate()`، وبترسم الزراير والنصوص في نفس المكان. الكارثة هنا إن الشاشة دي بتموت معمارياً؛ مينفعش تفتح لها `@Preview` في أندرويد ستوديو لأن مفيش ViewModel متوفر، ومينفعش تعمل لها Screenshot Test سريع على الـ JVM، ومستحيل تعيد استخدامها في شاشة تابلت بجانب شاشة تانية.\n\nالحل هو الفصل الصارم لدالتين:\nالدالة الأولى هي `Route Composable` (المنسق): بتعيش في الـ NavGraph، بتستقبل المعرفات من الرابط، وتحقن الـ ViewModel، وتجمع تدفق البيانات كحالة متزامنة، وتمرر البيانات للشاشة التقديمية، ولما المستخدم يدوس حاجة، الـ Route هو اللي بينادي دوال الـ ViewModel أو بينفذ التنقل.\n\nالدالة الثانية هي `Screen Composable` (المقدم): دالة نقية 100% معندهاش أي فكرة مين هو الـ ViewModel ولا إيه هو الـ NavController. بتستقبل فقط `UiState` وكولباكات عادية زي `onItemClick`. النتيجة إنك تقدر تعمل لها 5 معاينات مختلفة في الـ IDE (حالة التحميل، النجاح، الخطأ، الوضع المظلم)، وتختبرها في أجزاء من الثانية باختبارات Unit Test بدون محاكي أندرويد.",
        "deep_answer_ar": "تحت الكابوت، فصل الـ Route عن الـ Screen بيحقق أقصى استفادة من خوارزميات الـ Compose Compiler والـ Smart Skipping.\n\nدالة الـ Screen بتستقبل فقط Immutable Data Class ودوال Lambdas مستقرة؛ المترجم بيحلل الباراميترات دي ويولد في البايت كود فحص `changed bitmask` مثالي. لو الـ Route أعاد الرندرة لأي سبب خارجي وكانت الـ State الخاصة بالـ Screen متطابقة بـ `equals()`، المحرك بينفذ `Early Return` ويتخطى رندرة شجرة الشاشة بالكامل بصفر استهلاك معالج.\nلو كنت مررت كائن الـ ViewModel مباشرة للشاشة، الكومبايلر كان هيصنفه كـ Unstable Type، وده كان هيعطل التخطي ويجبر الشاشة على إعادة الرندرة في كل فريم.\n\nومن ناحية اختبارات الأداء وهندسة الجودة (QA Engineering)، هذا الفصل بيقلل تكلفة كتابة الاختبارات المؤتمتة بشكل هائل.\nشاشات الـ Screen النقية بنقدر نختبرها بالكامل على الـ JVM العادي باستخدام أدوات الـ Screenshot Testing زي Paparazzi أو Roborazzi بدون الحاجة لتشغيل محاكي وبدون بناء شبكة Mocks معقدة للـ ViewModels أو الـ Repositories. بنمرر كائن State ثابت ونتأكد من صحة الرسم وتجاوب الـ Lambdas في ميلي ثوانٍ.\nوفوق كده، النمط ده هو الأساس لبناء الـ Adaptive Layouts للأجهزة اللوحية والقابلة للطي؛ فنفس دالة الـ Screen النقية ممكن نستضيفها كشاشة كاملة في الموبايل أو نضعها كعمود جانبي داخل `TwoPaneScaffold` على التابلت بدون تعديل حرف واحد في كود العرض."
    }
}

# ==========================================
# COM-19: How do you implement a reusable design system and themes?
# ==========================================
DATA["COM-19"] = {
    "concept_en": """Implementing a reusable design system and custom theme in Jetpack Compose involves creating a unified system of design tokens—Colors, Typography, Shapes, and Spacing—and distributing them through the composition tree via CompositionLocal. Rather than hardcoding styles or relying solely on standard MaterialTheme defaults, enterprise teams define strongly typed, immutable token models and wrap their application inside a custom Theme composable backed by CompositionLocalProvider. By exposing convenient accessor objects (such as AppTheme.colors and AppTheme.spacing), UI components consume standardized tokens with automatic dark mode adaptation, dynamic theming support, and zero performance overhead.""",
    "walkthrough_en": """Building a custom design system token hierarchy in Jetpack Compose:
```kotlin
// 1. Define custom design tokens (e.g. Spacing)
@Immutable
data class AppSpacing(
    val extraSmall: Dp = 4.dp,
    val small: Dp = 8.dp,
    val medium: Dp = 16.dp,
    val large: Dp = 24.dp,
    val extraLarge: Dp = 32.dp
)

// 2. Create static CompositionLocals (Static prevents re-evaluating the whole tree on reads!)
val LocalAppSpacing = staticCompositionLocalOf { AppSpacing() }

// 3. Custom Theme composable providing tokens
@Composable
fun AppDesignTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    spacing: AppSpacing = AppSpacing(),
    content: @Composable () -> Unit
) {
    CompositionLocalProvider(
        LocalAppSpacing provides spacing
    ) {
        MaterialTheme(content = content)
    }
}

// 4. Clean theme accessor object for developers
object AppTheme {
    val spacing: AppSpacing
        @Composable
        @ReadOnlyComposable
        get() = LocalAppSpacing.current
}

// 5. Usage in any UI component
@Composable
fun ThemedCard(title: String) {
    Card(modifier = Modifier.padding(AppTheme.spacing.medium)) {
        Text(title, modifier = Modifier.padding(AppTheme.spacing.small))
    }
}
```""",
    "short_en": """We implement a custom design system by defining strongly typed, immutable token models for Colors, Typography, Shapes, and Spacing, and providing them down the composition tree using staticCompositionLocalOf. A custom AppTheme composable wraps the content and provides these values via CompositionLocalProvider. We expose an accessor object like AppTheme.spacing and AppTheme.colors so UI components consume consistent design tokens that support dark mode and dynamic theming seamlessly.""",
    "structured_en": """Constructing a scalable, multiplatform design system in Jetpack Compose requires centralizing visual tokens and distributing them cleanly without prop drilling.
A robust design system standardizes four primary token pillars: Color palettes (supporting Light, Dark, and High-Contrast schemes), Typography scales, Shape definitions, and Spacing/Elevation dimensions.
The implementation begins by modeling these tokens as @Immutable data classes.
To expose tokens globally without passing them as parameters to every composable, we leverage CompositionLocal.
Choosing between compositionLocalOf and staticCompositionLocalOf is a crucial architectural decision.
For design system tokens that rarely change at runtime—such as typography styles, shapes, and spacing—we use staticCompositionLocalOf.
When a static CompositionLocal's value changes, Compose invalidates the entire content tree; however, because theme tokens change only during rare events like toggling dark mode, using static composition locals eliminates internal tracking overhead, speeding up normal frame execution.
Finally, we provide a unified AppTheme object with @ReadOnlyComposable accessors, enabling developers to write AppTheme.spacing.medium or AppTheme.colors.brandPrimary cleanly across all app modules.""",
    "deep_senior_en": """Under the hood, CompositionLocal mechanisms govern token propagation throughout the Compose SlotTable hierarchy.
When a token is provided using CompositionLocalProvider, the Composer inserts a new entry into the ambient locals map for that subcomposition scope.
The architectural difference between compositionLocalOf and staticCompositionLocalOf centers on dependency tracking and invalidation scopes.
compositionLocalOf registers a snapshot read dependency whenever .current is read inside a composable function. If the provided value changes, the Compose runtime invalidates only the specific RecomposeScopes that read that token. However, this fine-grained tracking incurs a continuous memory and CPU cost to maintain read records in the SlotTable.
In contrast, staticCompositionLocalOf does not track individual consumer reads.
If a static token changes, the runtime conservatively re-executes the entire content lambda provided to CompositionLocalProvider.
Because design system tokens (such as Spacing dimensions, Typography fonts, and CornerRadius shapes) never change on a frame-by-frame basis—they change only during user-initiated theme toggles or system dark-mode switches—staticCompositionLocalOf is the mathematically optimal choice, delivering maximum runtime performance and zero memory bloat during standard rendering.
Furthermore, annotating accessor getters with @ReadOnlyComposable informs the Compose compiler that reading AppTheme.spacing produces no mutable state reads or slot writes, allowing the compiler to optimize the calling site into a direct property access.""",
    "meta_ar": {
        "id": "COM-19",
        "questionAr": "كيف تبني وتنفذ نظام تصميم وثيمات قابلة لإعادة الاستخدام (Design System & Themes) في Compose؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على هندسة Design System مخصص في كومبوز، وفهم ركائز الـ Tokens (الألوان، الخطوط، الأشكال، المسافات)، واستخدام `CompositionLocalProvider`، والفرق بين `staticCompositionLocalOf` و `compositionLocalOf`.",
        "why_it_matters_ar": "كتابة مسافات وألوان عشوائية داخل الشاشات يجعل تغيير الهوية أو دعم الوضع المظلم كابوساً، بينما الـ Design System الموحد يضمن اتساق الواجهات وسرعة بناء شاشات جديدة متناسقة 100%.",
        "worked_example_ar": "بناء Design Token للمسافات وتوفيره بـ CompositionLocal:\n```kotlin\n@Immutable data class Spacing(val sm: Dp = 8.dp, val md: Dp = 16.dp)\nval LocalSpacing = staticCompositionLocalOf { Spacing() }\n// توفيره في الثيم واستهلاكه بسهولة\n@Composable fun AppTheme(content: @Composable () -> Unit) {\n    CompositionLocalProvider(LocalSpacing provides Spacing(), content = content)\n}\n// استخدام منظم: AppTheme.spacing.md\n```",
        "trade_offs_ar": "بناء Design System في بداية المشروع يتطلب وقتاً إضافياً في التأسيس، لكنه يختصر نصف وقت تطوير الشاشات لاحقاً ويسهل تغيير الألوان ودعم الـ Dark Theme عالمياً.",
        "failure_modes_ar": "استخدام `compositionLocalOf` العادي لرموز التصميم الثابتة كالخطوط والمسافات، مما يثقل الـ SlotTable بمراقبة قراءات لا تتغير أبداً أثناء تشغيل التطبيق.",
        "production_perspective_ar": "في الشركات الكبرى، نبني Design System كـ Multiplatform Module مستقل، ونعتمد `staticCompositionLocalOf` لكل الـ Tokens، ونوفر كائن `AppTheme` موحد لكل الفرق البرمجية.",
        "how_to_answer_ar": "اشرح الخطوات المعمارية: أولاً نمذجة الـ Tokens (الألوان والخطوط والأشكال والمسافات Spacing) كـ Immutable Data Classes، ثانياً توفيرها بـ `staticCompositionLocalOf` وشرح سر اختيار static لتوفير موارد المعالج، ثالثاً بناء كائن وصول `AppTheme` بدوال `@ReadOnlyComposable`، ورابعاً دعم الوضع المظلم والـ Dynamic Colors.",
        "talking_points_ar": "ركائز الـ Design Tokens الأربعة، وآلية عمل CompositionLocal، والفرق بين staticCompositionLocalOf و compositionLocalOf، وكائن الوصول AppTheme، ودور @ReadOnlyComposable.",
        "follow_ups_ar": "- **المحاور:** \"لماذا نفضل staticCompositionLocalOf على compositionLocalOf لرموز نظام التصميم؟\"\n  **المرشح:** \"لأن رموز الثيم زي الخطوط والمسافات نادر جداً ما تتغير أثناء الاستخدام؛ فـ static بتلغي تتبع القراءات في الـ SlotTable وتوفر الذاكرة، والتحديث بيتم للشجرة كلها مرة واحدة فقط لما المستخدم يغير الثيم.\"\n\n- **المحاور:** \"ما هي فائدة كتابة `@ReadOnlyComposable` فوق دوال كائن AppTheme؟\"\n  **المرشح:** \"بتعرف كومبايلر كومبوز إن الدالة دي مجرد قراءة لبيانات ثابتة ومبتعملش أي كتابة في الـ SlotTable، فالكومبايلر بيعمل لها Inline Optimization سريع جداً.\"",
        "self_check_ar": "هل غطيت خطوات بناء الـ Design System؟ هل شرحت ركائز الـ Tokens؟ وهل بينت الفرق المعماري بين static و dynamic CompositionLocal؟",
        "references_ar": f"- [Jetpack Compose Theming guide](https://developer.android.com/develop/ui/compose/designsystems/anatomy) — الدليل الرسمي لجوجل لتشريح وبناء أنظمة التصميم.\n- [CompositionLocal in Jetpack Compose](https://developer.android.com/develop/ui/compose/compositionlocal) — توثيق جوجل الرسمي لـ CompositionLocal.",
        "quick_answer_ar": "بنبني نظام تصميم (Design System) قابل لإعادة الاستخدام في كومبوز عن طريق تعريف ركائز التصميم (Design Tokens) كـ Data Classes غير قابلة للتعديل تشمل: الألوان، والخطوط (Typography)، والأشكال (Shapes)، والمسافات (Spacing). بنمرر القيم دي عبر الشجرة باستخدام `CompositionLocalProvider`. ولتحقيق أعلى أداء، بنستخدم `staticCompositionLocalOf` لأن رموز الثيم نادراً ما تتغير، وده بيلغي تتبع القراءات ويوفر الذاكرة. وأخيراً بنعمل كائن موحد اسمه `AppTheme` بدوال `@ReadOnlyComposable` عشان المطورين يوصلوا للقيم بسهولة زي `AppTheme.spacing.medium` و `AppTheme.colors.brandPrimary` مع دعم تلقائي للوضع المظلم.",
        "best_answer_ar": "بناء نظام تصميم وثيمات متين في Jetpack Compose هو الأساس المعماري اللي بيخلي التطبيق متناسق وسهل التوسع والصيانة ومستعد للعمل على مختلف الأنظمة والمنصات.\n\nالهندسة الصحيحة بتعتمد على أربع خطوات:\nالخطوة الأولى: نمذجة الـ Tokens؛ بنعمل كلاسات داتا مميزة بـ `@Immutable` لأربعة عناصر أساسية: الألوان (Dark and Light Palettes)، والخطوط، والأشكال، والمسافات (`AppSpacing`) اللي جوجل لسبب غريب نسيت تحطها في `MaterialTheme` الافتراضي.\n\nالخطوة الثانية: اختيار آلية التمرير؛ بنستخدم `staticCompositionLocalOf` مش `compositionLocalOf`. لأن قيم المسافات والخطوط قيم ثابتة مش بتتغير في كل فريم، فاستخدام الـ static بيمنع كومبوز من تسجيل ومراقبة كل قراءة في الذاكرة، وبيوفر أداءً فائقاً.\n\nالخطوة الثالثة: دالة الثيم الموحدة `AppTheme`؛ بتستقبل المحتوى وتغلفه داخل `CompositionLocalProvider` اللي بيبث الـ Tokens للأسفل في الشجرة.\n\nالخطوة الرابعة: كائن الوصول السريع؛ بنعمل `object AppTheme` جواه getters مميزة بـ `@ReadOnlyComposable` عشان المطور يقدر يكتب `AppTheme.spacing.large` بسهولة، وبدون تمرير باراميترات يدوية (Prop Drilling) عبر الشاشات، مع دعم سلس لتبديل الألوان مع الوضع الليلي وألوان Material You الديناميكية.",
        "deep_answer_ar": "تحت الكابوت، الـ `CompositionLocal` هي أداة سحرية بتمرر البيانات في شجرة الـ Composition بشكل ضمني (Implicit Data Flow) عبر خريطة داخلية بيحتفظ بيها كائن الـ Composer.\n\nالفارق المعماري الحاسم اللي بيفرق بين مهندس عادي وسينيور هو التمييز بين `compositionLocalOf` و `staticCompositionLocalOf`:\nدالة `compositionLocalOf` العادية بتسجل مراقبة قراءة (Read Tracking) في الـ SlotTable لكل كومبوزابل يقرأ `.current`. لو القيمة اتغيرت، كومبوز بتروح تنادي الـ RecomposeScope الخاص بالدوال دي فقط بدون ما تلمس باقي الشجرة. لكن المراقبة الدقيقة دي بتكلف معالج ورام في كل فريم.\n\nفي المقابل، دالة `staticCompositionLocalOf` معندهاش أي تتبع للقراءات الفردية. لو القيمة اتغيرت، كومبوز بتلغي الـ Composition بالكامل وتعيد رندرة الشجرة كلها من الصفر.\nولأن رموز الـ Design System (زي المسافات والأشكال والخطوط) مستحيل تتغير أثناء تشغيل الفريمات العادية—بل بتتغير فقط كحدث نادر لما المستخدم يغير ثيم الهاتف أو يقلب Dark Mode—فاستخدام `staticCompositionLocalOf` هو القرار الهندسي الأمثل، لأنه بيلغي تماماً تكلفة المراقبة في الـ SlotTable ويوفر أقصى سرعة استجابة في رندرة الشاشات.\n\nودمج ده مع علامة `@ReadOnlyComposable` فوق الـ getters بيعلم الكومبايلر إن الدالة دي بتقرأ فقط ومبتعملش أي كتابة في الـ Slots، فالكومبايلر بيحولها في البايت كود لقراءة خاصية مباشرة (Inline Property Access) بدون أي عبء حسابي إضافي."
    }
}

def main():
    print("Elevating 9 questions in COM (COM-11 to COM-19)...")
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

    ee.save_topic_metadata("com_11_19", topic_meta)
    ee.merge_all_metadata()

    # Validate each question
    for qid in sorted(DATA.keys()):
        if DATA[qid] is None:
            continue
        ee.validate_question(qid)

    print("\nAll 9 COM questions (COM-11 to COM-19) successfully elevated and passed validation!")

if __name__ == "__main__":
    main()
