#!/usr/bin/env python3
"""
Elevation script for COM-20 to COM-28 (Jetpack Compose - Batch 3).
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
# COM-20: How do you handle previews, permissions, and navigation?
# ==========================================
DATA["COM-20"] = {
    "concept_en": """Handling previews, runtime permissions, and navigation in Jetpack Compose requires modular decoupling across the UI architecture. Previews are built using stateless Screen composables paired with @PreviewParameter and custom multi-preview annotations for light, dark, and font-scale configurations without mocking heavy framework dependencies. Permissions are managed using the official rememberLauncherForActivityResult API with RequestPermission contracts, presenting user-friendly rationale dialogs before prompting system dialogs. Navigation is isolated by hoisting navigation callbacks as pure lambdas to the top-level NavHost graph, enforcing type-safe routing and keeping leaf UI components completely agnostic of NavController instances.""",
    "walkthrough_en": """Unified demonstration of previews, permissions, and decoupled navigation:
```kotlin
// 1. Preview Provider for multi-state design testing
class UserStateProvider : PreviewParameterProvider<UserUiState> {
    override val values = sequenceOf(
        UserUiState(name = "Ahmed", hasCameraAccess = false),
        UserUiState(name = "Sara", hasCameraAccess = true)
    )
}

// 2. Stateless Screen Composable with permission request and hoisted navigation
@Composable
fun CameraScreenContent(
    state: UserUiState,
    onNavigateBack: () -> Unit,
    onRequestPermission: () -> Unit,
    modifier: Modifier = Modifier
) {
    Scaffold(modifier = modifier) { padding ->
        Column(modifier = Modifier.padding(padding).padding(16.dp)) {
            Text("User: ${state.name}")
            if (state.hasCameraAccess) {
                Text("Camera Active", color = Color.Green)
            } else {
                Button(onClick = onRequestPermission) { Text("Grant Camera Permission") }
            }
            Spacer(modifier = Modifier.height(16.dp))
            Button(onClick = onNavigateBack) { Text("Back to Home") }
        }
    }
}

// 3. Preview Annotation
@Preview(name = "Light Mode", showBackground = true)
@Preview(name = "Dark Mode", uiMode = Configuration.UI_MODE_NIGHT_YES)
@Composable
private fun CameraScreenPreview(@PreviewParameter(UserStateProvider::class) state: UserUiState) {
    MaterialTheme { CameraScreenContent(state = state, onNavigateBack = {}, onRequestPermission = {}) }
}

// 4. Route Composable handling real runtime permission launcher
@Composable
fun CameraRoute(onNavigateBack: () -> Unit) {
    var hasPermission by remember { mutableStateOf(false) }
    val permissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission()
    ) { isGranted -> hasPermission = isGranted }

    CameraScreenContent(
        state = UserUiState(name = "Production User", hasCameraAccess = hasPermission),
        onNavigateBack = onNavigateBack,
        onRequestPermission = { permissionLauncher.launch(Manifest.permission.CAMERA) }
    )
}
```""",
    "short_en": """We handle previews by designing stateless screen composables and supplying mock data via PreviewParameterProvider across light and dark multi-previews. Runtime permissions are managed using rememberLauncherForActivityResult with RequestPermission, decoupling permission launchers from presenter composables. Navigation is decoupled by hoisting event lambdas to the NavHost boundary, keeping individual screens pure, previewable, and completely independent of NavController instances.""",
    "structured_en": """Architecting a robust Jetpack Compose application requires clean separation across three major system concerns: visual tooling previews, Android runtime permissions, and navigation dispatching.
First, for Android Studio Previews, we avoid injecting ViewModels or system contexts into screen composables.
By keeping the Screen Composable stateless, we can feed it mock domain fixtures using PreviewParameterProvider.
Creating custom multi-preview meta-annotations enables instant verification across light, dark, and localized font configurations in a single compilation pass.
Second, for runtime permissions, we leverage the official Activity Result APIs inside Compose.
Using rememberLauncherForActivityResult with ActivityResultContracts.RequestPermission creates an asynchronous bridge to the platform permission manager.
We present educational in-app rationale sheets when shouldShowRequestPermissionRationale is true, and provide direct settings deep-links if permissions are permanently denied, ensuring graceful degradation.
Third, for navigation, we strictly enforce navigation hoisting.
Screens never accept NavHostController as a parameter.
Instead, they expose explicit lambda callbacks like onBackClick or onItemSelected.
The hosting Route composable maps these callbacks directly into type-safe navigation routes, ensuring leaf widgets remain 100% reusable and testable on the JVM.""",
    "deep_senior_en": """Under the hood, these three mechanisms illustrate Compose's boundary mediation with the underlying Android operating system.
The @Preview annotation relies on Android Studio's LayoutLib, a specialized headless desktop rendering engine that emulates the Android framework. Because LayoutLib lacks an active Dagger or Hilt dependency graph, passing stateful ViewModels or platform service managers into a composable immediately crashes the preview renderer. Decoupling screens into stateless presenters allows LayoutLib to render composables purely from memory fixtures in the SlotTable.
The rememberLauncherForActivityResult API interfaces with the host ComponentActivity's ActivityResultRegistry.
When the composable registers the launcher, Compose generates a unique synthetic key and attaches an observer to the Activity's lifecycle.
When the platform permission dialog returns a result, the registry routes the boolean callback to the composition thread, safely updating a SnapshotMutableState and triggering recomposition without memory leaks or configuration change losses.
For navigation, decoupling NavController preserves compiler skipping optimizations.
Because NavController is an unstable platform object containing deep backstacks, passing it down through parameters forces the Compose compiler to mark the composable as unskippable.
By converting navigation actions into stable lambda function types (such as () -> Unit), the compiler enables zero-allocation skipping, preventing entire screen trees from recomposing during unrelated parent UI updates.""",
    "meta_ar": {
        "id": "COM-20",
        "questionAr": "كيف تتعامل باحترافية مع المعاينات (Previews) والأذونات (Permissions) والتنقل في Compose؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على فصل الشاشات التقديمية لتسهيل الـ Previews بـ `@PreviewParameter`، والتعامل السليم مع أذونات النظام بـ `rememberLauncherForActivityResult`، وتطبيق مبدأ Navigation Hoisting لتجنب تمرير `NavController`.",
        "why_it_matters_ar": "الخلط بين هذه المفاهيم يفسد ميزة المعاينة في أندرويد ستوديو، ويسبب كراشات عند طلب الأذونات بعد تدوير الشاشة، ويعطل الـ Smart Skipping بسبب تمرير كائنات أندرويد غير مستقرة.",
        "worked_example_ar": "تطبيق المعاينة والأذونات وفصل التنقل:\n```kotlin\n// شاشة نقية تدعم المعاينة وتستقبل دوال الإذن والتنقل\n@Composable fun Screen(onCamera: () -> Unit, onBack: () -> Unit)\n// الـ Route يربط الإذن والتنقل\n@Composable fun Route(onBack: () -> Unit) {\n    val launcher = rememberLauncherForActivityResult(RequestPermission()) { ... }\n    Screen(onCamera = { launcher.launch(Manifest.permission.CAMERA) }, onBack = onBack)\n}\n```",
        "trade_offs_ar": "فصل الشاشات إلى Route و Screen وتجهيز Providers يتطلب كتابة كود إضافي في البداية، لكنه يمنح سرعة فائقة في المعاينة واختبار الواجهات بنسبة 100% بدون محاكي.",
        "failure_modes_ar": "تمرير `ViewModel` أو `NavController` داخل دالة المعاينة `@Preview`، مما يسبب انهيار أداة LayoutLib في أندرويد ستوديو وظهور أخطاء بيضاء.",
        "production_perspective_ar": "في المشروعات الكبيرة، نلزم المطورين بإنشاء MultiPreview Annotations تجمع بين الوضع الليلي وأحجام الخطوط، واستخدام الـ Type-Safe Navigation الحديث في Navigation 2.8+.",
        "how_to_answer_ar": "قسم الإجابة لثلاثة محاور متكاملة: أولاً المعاينات بتصميم شاشات Stateless واستخدام PreviewParameterProvider، ثانياً الأذونات باستخدام `rememberLauncherForActivityResult` وعرض شاشات التوضيح Rationale، وثالثاً التنقل برفع الكولباكات كـ Lambdas لتفادي تمرير NavController وتفعيل الـ Skipping.",
        "talking_points_ar": "أداة LayoutLib والـ Previews، وتوفير الداتا بـ PreviewParameterProvider، ودورة حياة ActivityResultRegistry للأذونات، وتأثير NavController على الـ Skipping واستقرار الكود.",
        "follow_ups_ar": "- **المحاور:** \"لماذا تفشل المعاينة `@Preview` فوراً عند محاولة تمرير `hiltViewModel()` بداخلها؟\"\n  **المرشح:** \"لأن أداة LayoutLib في أندرويد ستوديو هي بيئة سطح مكتب افتراضية معندهاش Hilt Dependency Graph ولا سياق أندرويد حقيقي، فعشان تشتغل لازم الشاشة تكون Stateless بتستقبل بيانات عادية فقط.\"\n\n- **المحاور:** \"كيف يتعامل rememberLauncherForActivityResult مع تدوير الشاشة أثناء فتح نافذة إذن النظام؟\"\n  **المرشح:** \"بيرتبط بـ ActivityResultRegistry الخاص بالأكتيفيتي، فبيسجل النتيجة حتى لو الأكتيفيتي اتدمرت ورجعت، وبيرجع القيمة للكومبوزابل فور استعادة الشاشة بدون ضياع النتيجة.\"",
        "self_check_ar": "هل غطيت المفاهيم الثلاثة بتناغم؟ هل شرحت كيفية جعل المعاينة ناجحة؟ وهل بينت الأثر المعماري على الأذونات والتنقل؟",
        "references_ar": f"- [Compose Tooling: Previews](https://developer.android.com/develop/ui/compose/tooling/previews) — التوثيق الرسمي للمعاينة في كومبوز.\n- [Activity Result in Compose](https://developer.android.com/develop/ui/compose/libraries#activityresult) — التوثيق الرسمي للتعامل مع أذونات ونتائج الأكتيفيتي في كومبوز.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "بنتعامل مع التلات محاور بفصل معماري منظم: أولاً في المعاينات (Previews)، بنخلي شاشات الـ Screen نقية وخالية من الحالة (Stateless) وبنمرر لها بيانات تجريبية عبر `PreviewParameterProvider` لدعم الوضع الليلي ومختلف مقاسات الخطوط بدون الحاجة لـ ViewModel. ثانياً في الأذونات، بنستخدم `rememberLauncherForActivityResult` مع عقد `RequestPermission` وبنعرض واجهة توضيحية للمستخدم قبل طلب الإذن لحماية تجربة الاستخدام. ثالثاً في التنقل، بنرفع الأحداث كـ Lambdas صريحة للـ Route Composable بدل تمرير `NavController`، وده بيحافظ على ميزة الـ Smart Skipping ويسهل اختبار وتعديل الشاشات في ثوانٍ.",
        "best_answer_ar": "التعامل باحترافية مع المعاينات والأذونات والتنقل بيكشف مدى التزام المطور بمبادئ فصل المسؤوليات في Jetpack Compose.\n\nالمحور الأول: المعاينات في أندرويد ستوديو؛ أكبر خطأ بنشوفه هو وضع `hiltViewModel()` أو كود نظام داخل الشاشة؛ ده بيخلي أداة LayoutLib تعطل والمعاينة تفشل. الحل هو تصميم شاشة الـ Screen كدالة نقية بتستقبل `UiState`، واستخدام `@PreviewParameter` عشان نعاين كل الحالات (التحميل، والبيانات، والخطأ، والوضع المظلم) في نفس اللحظة بدون تشغيل المحاكي.\n\nالمحور الثاني: إدارة أذونات النظام؛ بنستخدم واجهة Compose الرسمية `rememberLauncherForActivityResult` مع عقد `ActivityResultContracts.RequestPermission()`. الأسلوب الاحترافي بيتطلب فحص حالة الإذن أولاً؛ لو مرفوض بنعرض شاشة توضيحية تشرح للمستخدم الفائدة، ولو وافق بننادي `launch`، والنتيجة بترجع للكوروتين وتحدث الـ State تلقائياً حتى لو الهاتف اتدور أثناء فتح شباك النظام.\n\nالمحور الثالث: التنقل النظيف؛ بنمنع تماماً تمرير `NavController` لداخل الشاشات التقديمية. الشاشة بتصعد أحداثها كدوال كولباك عادية، والـ Route Composable هو اللي بيترجم الضغطات لمسارات تنقل آمنة النوع، وده بيضمن أعلى درجة من إعادة استخدام الكود.",
        "deep_answer_ar": "تحت الكابوت، كل أداة من الأدوات دي بتعكس كيفية تواصل كومبوز مع نظام تشغيل أندرويد والعتاد الداخلي.\n\nأداة الـ `@Preview` بتعتمد في أندرويد ستوديو على محرك افتراضي اسمه `LayoutLib`؛ المحرك ده بيحاكي فريمورك أندرويد على جهاز الكمبيوتر المكتبي بدون Dalvik أو ART حقيقي وبدون شجرة حقن التبعيات بـ Hilt. لما بتصمم شاشتك كـ Stateless Screen، أنت بتسمح لـ LayoutLib برسم الـ SlotTable مباشرة من الذاكرة في أجزاء من الميلي ثانية، وتفادي الانهيارات الناتجة عن محاولة الوصول لخدمات أندرويد غير المهيأة في بيئة التصميم المكتبي.\n\nأما دالة `rememberLauncherForActivityResult` فبترتبط مباشرة بـ `ActivityResultRegistry` التابع لكلاس `ComponentActivity`.\nالمحرك بيولد مفتاحاً فريداً لكل استدعاء ويسجل مراقب دورة حياة. لما شباك الإذن بتاع النظام يقفل والمستخدم يختار القبول أو الرفض، الأكتيفيتي بتستقبل النتيجة وتمررها عبر الـ Registry للـ Snapshot State، وده بيطلق Recomposition آمن بدون أي تسريب للذاكرة وبدون خطر فقدان النتيجة أثناء الـ Configuration Change.\n\nوبالنسبة للتنقل، عدم تمرير `NavController` للشاشات التقديمية بيحمي ميزة الـ Smart Skipping؛ لأن `NavController` كائن غير مستقر ومعقد جداً، وتمريره كباراميتر بيجبر الكومبايلر يصنف الدالة كـ Unskippable. استبداله بـ Lambdas مستقرة بيمكّن كومبوز من تخطي رندرة الشاشة بالكامل لو حالتها لم تتغير، وده بيرفع كفاءة التطبيق وسرعة استجابته لأقصى درجة ممكنة في الإنتاج."
    }
}

# ==========================================
# COM-21: What is NavHost, and how is state restored after process death?
# ==========================================
DATA["COM-21"] = {
    "concept_en": """NavHost is the foundational container composable in Jetpack Compose Navigation that hosts a self-contained navigation graph and swaps screen destinations based on NavHostController state. State restoration across Android process death operates on two architectural levels: UI presentation state and business domain state. UI widget state (such as scroll positions and uncommitted text input) is preserved using rememberSaveable backed by SaveableStateRegistry, which serializes data into the platform saved instance state Bundle. Business state inside architecture ViewModels is restored via SavedStateHandle, which automatically retains navigation arguments and query states across process recreation.""",
    "walkthrough_en": """Restoring UI and ViewModel state after process death in a Compose NavHost:
```kotlin
// 1. Business state surviving process death via ViewModel SavedStateHandle
@HiltViewModel
class SearchViewModel @Inject constructor(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {
    // Survives process termination and system RAM reclamation!
    var query: String
        get() = savedStateHandle["search_query"] ?: ""
        set(value) { savedStateHandle["search_query"] = value }
}

// 2. UI presentation state surviving process death via rememberSaveable
@Composable
fun FilterableSearchScreen(viewModel: SearchViewModel) {
    // Survives process death and config changes via Bundle serialization!
    var isFilterExpanded by rememberSaveable { mutableStateOf(false) }

    Column(modifier = Modifier.padding(16.dp)) {
        TextField(
            value = viewModel.query,
            onValueChange = { viewModel.query = it },
            placeholder = { Text("Search...") }
        )
        FilterToggle(
            isExpanded = isFilterExpanded,
            onToggle = { isFilterExpanded = !isFilterExpanded }
        )
    }
}

// 3. NavHost container managing destinations and backstack state
@Composable
fun AppNavHost(navController: NavHostController) {
    NavHost(navController = navController, startDestination = "home") {
        composable("home") { HomeScreen(onOpenSearch = { navController.navigate("search") }) }
        composable("search") {
            val searchVm: SearchViewModel = hiltViewModel()
            FilterableSearchScreen(viewModel = searchVm)
        }
    }
}
```""",
    "short_en": """NavHost is the container composable that links a NavHostController to a navigation graph, displaying destinations based on backstack state. State restoration after system process death occurs at two levels. Local UI state like toggles or draft text uses rememberSaveable, which serializes into the Activity saved instance Bundle via SaveableStateHolder. Business state and arguments are restored inside ViewModels using SavedStateHandle, ensuring seamless recovery when the operating system kills the background process.""",
    "structured_en": """Managing screen destinations and surviving system-initiated process death is a critical benchmark for enterprise-grade Android applications.
NavHost serves as the primary composition viewport for Jetpack Navigation.
It observes the destination backstack emitted by NavHostController, mapping route strings or type-safe serializable destinations to their corresponding composable contents.
When Android reclaims application memory in the background due to RAM pressure, the operating system executes process death.
Restoring application state upon return requires two coordinated mechanisms.
For presentation state within the composable tree, developers replace remember with rememberSaveable.
While remember only survives recomposition, rememberSaveable serializes data into the Android platform saved instance state Bundle using built-in Savers for primitives or custom Savers for complex objects.
For business state inside ViewModels, we rely on SavedStateHandle.
Hilt automatically injects SavedStateHandle into ViewModels, providing a persistent key-value store that survives process destruction.
Furthermore, NavHost internally wraps backstack entries with SaveableStateHolder, guaranteeing that each destination's scroll offset and input state are saved and restored automatically when popping and pushing backstack destinations.""",
    "deep_senior_en": """Under the hood, NavHost and process death state restoration rely on SaveableStateHolder and the AndroidX SavedStateRegistryOwner pipeline.
When NavHost navigates between composables, it utilizes SaveableStateHolder.SaveableStateProvider.
This component assigns a unique key to each backstack entry.
When a destination is covered by a new screen or temporarily unmounted, SaveableStateHolder invokes its internal saveState() logic, serializing that subcomposition's rememberSaveable slot values into a detached bundle dictionary rather than discarding them.
When the user pops the backstack to return, the runtime matches the entry key and restores the exact SlotTable interval values.
During system process death, the host Activity's onSaveInstanceState(outState: Bundle) triggers the root SaveableStateRegistry.
The registry serializes all active SaveableStateHolder dictionaries and ViewModel SavedStateHandles into the system-managed persistent Parcelable Bundle.
Upon process resurrection, the operating system launches a new Linux process, re-creates the Activity, and passes the saved Bundle into onCreate().
Compose's root RecomposeScope reads the registry, and SavedStateHandle restores its key-value map.
Because the operating system imposes a strict transaction buffer limit of roughly one megabyte across Binder IPC transactions, senior engineers ensure that only primitive identifiers, scroll indices, and query tokens are serialized, completely avoiding heavy domain payloads to prevent fatal TransactionTooLargeException crashes during process recreation.
Senior engineers test this resilience by enabling 'Don't keep activities' in Developer Options or executing 'adb shell am kill <package>' to verify that screens rehydrate flawlessly without throwing NullPointerExceptions or dropping user form drafts.""",
    "meta_ar": {
        "id": "COM-21",
        "questionAr": "ما هو NavHost؟ وكيف تستعيد الشاشات حالتها بعد موت العملية (Process Death) في كومبوز؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم دور `NavHost` و `NavHostController`، واستيعاب الفرق بين تدوير الشاشة وموت العملية بنقص الذاكرة (Process Death)، والقدرة على استخدام `rememberSaveable` و `SavedStateHandle`.",
        "why_it_matters_ar": "اعتماد التطبيق على `remember` العادي يجعل المستخدم يفقد كل ما كتبه في النماذج ومكان التمرير بمجرد قيام النظام بقتل التطبيق في الخلفية لتوفير الرام.",
        "worked_example_ar": "استعادة الحالة بعد موت العملية عبر rememberSaveable و SavedStateHandle:\n```kotlin\n// 1. في الواجهة: حفظ الحالة في الـ Bundle بـ rememberSaveable\nvar expanded by rememberSaveable { mutableStateOf(false) }\n// 2. في الـ ViewModel: حفظ بيانات العمل بـ SavedStateHandle\nclass SearchViewModel(private val handle: SavedStateHandle) : ViewModel() {\n    var query: String\n        get() = handle[\"q\"] ?: \"\"\n        set(v) { handle[\"q\"] = v }\n}\n```",
        "trade_offs_ar": "تخزين البيانات في `rememberSaveable` يتطلب أن تكون الكائنات قابلة للتحويل لـ Parcelable أو استخدام Saver مخصص، لكنه يضمن نجاة التطبيق من موت العملية بنسبة 100%.",
        "failure_modes_ar": "تخزين كائنات معقدة أو Bitmap ضخمة داخل `rememberSaveable`، مما يسبب كراش `TransactionTooLargeException` أثناء حفظ الـ Bundle.",
        "production_perspective_ar": "في المشروعات الكبيرة، نختبر شاشات الإدخال والتنقل دورياً بأمر `adb shell am kill` للتأكد من استعادة كل الحقول بعد موت العملية في الخلفية.",
        "how_to_answer_ar": "عرف NavHost: الحاوية التي تعرض الوجهات بناءً على مكدس التنقل، واشرح مستويي استعادة الحالة بعد Process Death: في طبقة الواجهة باستخدام `rememberSaveable` المحفوظ في الـ Bundle، وفي طبقة الـ ViewModel باستخدام `SavedStateHandle`، وحذر من قيود حجم الـ Bundle.",
        "talking_points_ar": "دور NavHost و SaveableStateHolder، والفرق بين remember و rememberSaveable، ودور SavedStateHandle في الـ ViewModel، واختبار Process Death بـ adb kill، ومخاطر TransactionTooLargeException.",
        "follow_ups_ar": "- **المحاور:** \"ما هو الفرق الجوهري بين remember و rememberSaveable؟\"\n  **المرشح:** \"`remember` بيحفظ الحالة فقط أثناء إعادة الرندرة (Recomposition) وبيضيع مع تدوير الشاشة أو موت العملية، بينما `rememberSaveable` بيخزن البيانات في `Bundle` النظام وينجو من تدوير الهاتف وموت العملية.\"\n\n- **المحاور:** \"كيف يحفظ NavHost حالة الشاشات السابقة عند الانتقال لشاشة جديدة؟\"\n  **المرشح:** \"بيستخدم مكون اسمه `SaveableStateHolder`؛ بيحفظ حالة كل صفحة في كاش داخلي بمفتاح فريد، ولما ترجع بزرار Back بيستعيد نفس موضع التمرير والبيانات بالضبط.\"",
        "self_check_ar": "هل عرفت NavHost بدقة؟ هل شرحت مستويي استعادة الحالة (الواجهة والـ ViewModel)؟ وهل بينت آلية عمل SaveableStateHolder؟",
        "references_ar": f"- [Navigation with Compose](https://developer.android.com/develop/ui/compose/navigation) — التوثيق الرسمي لجوجل للتنقل في كومبوز.\n- [State restoration in Compose](https://developer.android.com/develop/ui/compose/state-saving) — دليل حفظ واستعادة الحالة ومواجهة Process Death.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "الـ `NavHost` هو الحاوية التقديمية الأساسية في كومبوز اللي بتربط بين الـ `NavHostController` ورسمة التنقل (NavGraph)؛ وظيفته عرض الوجهة الحالية وتبديل الشاشات مع حركة المستخدم. أما استعادة الحالة بعد موت العملية (Process Death) بسبب نقص الذاكرة في الخلفية، فبتتم على مستويين متكاملين: في الواجهة بنستخدم `rememberSaveable` اللي بيسجل البيانات في كائن `Bundle` الخاص بالنظام، وفي الـ ViewModel بنستخدم `SavedStateHandle` اللي بيحفظ مدخلات البحث والمحددات، وده بيضمن عودة الشاشة بالظبط زي ما المستخدم سابها بدون فقدان أي بيانات.",
        "best_answer_ar": "الـ `NavHost` واستعادة الحالة بعد موت العملية بيمثلوا أحد أهم مقاييس النضج الهندسي لتطبيقات أندرويد في الإنتاج.\n\nالـ `NavHost` هو الـ Composable الحاوي لكل مسارات التطبيق؛ بيراقب مكدس التنقل (Backstack) اللي بيديره `NavHostController`، وأول ما المسار يتغير، بيقوم برندرة الشاشة المناسبة وعمل حركات الانتقال البصرية.\n\nالمأزق الكبير بيحصل لما التطبيق يروح في الخلفية ونظام أندرويد يقرر يقتل العملية (Process Death) عشان يوفر رام لتطبيقات تانية.\nلو كنت معتمد على `remember` العادي، كل مدخلات المستخدم ونصوص الحقول ومكان التمرير هتضيع بالكامل!\n\nالحل الهندسي المتين بيعتمد على ركيزتين:\nالركيزة الأولى: في طبقة الواجهة، بنستبدل `remember` بـ `rememberSaveable`. الأداة دي بتخزن البيانات في الـ `SavedInstanceState Bundle` لنظام أندرويد تلقائياً للأنواع الأساسية أو بـ `Saver` مخصص للكائنات المركبة، فبترجع الشاشة محتفظة بحالة القوائم المفتوحة ومكان التمرير.\n\nالركيزة الثانية: في طبقة منطق العمل، بنعتمد على `SavedStateHandle` داخل الـ ViewModel بحقن Hilt. المتغيرات المخزنة جواه بتنجو تماماً من موت العملية، وأول ما المستخدم يفتح التطبيق تاني، أندرويد بيعيد بناء الـ Activity والـ ViewModel ويسترجع كل البيانات السابقة بسلاسة متناهية.",
        "deep_answer_ar": "تحت الكابوت، التنسيق بين `NavHost` وعملية حفظ الحالة بيعتمد على معمارية معقدة جداً يقودها كائن `SaveableStateHolder` ونظام الـ `SavedStateRegistryOwner`.\n\nلما بتتنقل بين الشاشات داخل `NavHost`، المحرك مش بيهدم الشاشات القديمة تماماً، بل بيغلف كل وجهة داخل `SaveableStateProvider` بمفتاح فريد. لما تروح لشاشة تانية، الـ Holder بينادي دالة `saveState()`، فبياخد كل قيم الـ `rememberSaveable` الخاصة بالشاشة دي ويخزنها في قاموس منفصل في الذاكرة. ولما المستخدم يرجع بزرار الـ Back، المحرك بيطابق المفتاح ويسترجع نفس نودز الـ SlotTable السابقة بدون أي لخبطة.\n\nوفي لحظة حدوث الـ Process Death بسبب الـ Low Memory Killer، الأكتيفيتي بتنادي `onSaveInstanceState(outState: Bundle)`.\nهنا نظام الـ Registry بيجمع كل القواميس المتكيشة في `SaveableStateHolder` بالإضافة لكل بيانات الـ `SavedStateHandle` في الـ ViewModels، ويحولها لبيانات Parcelable داخل كائن الـ Bundle المدار بواسطة نظام التشغيل.\n\nأول ما المستخدم يرجع للتطبيق، لينكس بينشئ Process جديدة و Activity جديدة، ويمرر نفس الـ Bundle في دالة `onCreate()`.\nمحرك كومبوز بيقرأ الـ Registry في جذر الشجرة، ويعيد توزيع القيم على الشاشات والـ ViewModels في لمح البصر.\nفي الشركات الكبرى، بنختبر متانة الشاشات دي بإننا نشغل أمر `adb shell am kill <package>` ونتأكد إن المستخدم مش هيشوف شاشة بيضاء أو يواجه `NullPointerException` بعد رجوع التطبيق للحياة."
    }
}

# ==========================================
# COM-22: How do you support accessibility, screen readers, and adaptive layouts?
# ==========================================
DATA["COM-22"] = {
    "concept_en": """Supporting accessibility, screen readers, and adaptive layouts in Jetpack Compose ensures inclusive, robust applications across all device form factors. Accessibility and screen readers like TalkBack are supported via the Compose Semantics Tree, where modifiers like Modifier.semantics define contentDescription, custom roles, click actions, and state descriptions, while mergeDescendants merges fragmented child elements into coherent interactive cards. Adaptive layouts are engineered using Material 3 WindowSizeClass (Compact, Medium, Expanded), swapping navigation rails, permanent drawers, and split-pane multi-column layouts like SupportingPaneScaffold to seamlessly support foldables, tablets, and desktop form factors.""",
    "walkthrough_en": """Implementing merged accessibility semantics and adaptive layout switching:
```kotlin
// 1. Accessibility: Merge descendants into a single coherent TalkBack item
@Composable
fun AccessibleUserCard(user: User, onClick: () -> Unit) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick)
            .semantics(mergeDescendants = true) {
                // TalkBack announces this entire card as a single unified sentence!
                contentDescription = "User profile for ${user.name}, status is ${user.status}"
                role = Role.Button
            }
            .padding(16.dp)
    ) {
        Column {
            Text(user.name, style = MaterialTheme.typography.titleMedium)
            Text(user.status, style = MaterialTheme.typography.bodySmall)
        }
    }
}

// 2. Adaptive Layouts: Responsive UI switching via WindowSizeClass
@Composable
fun AdaptiveAppLayout(
    windowSizeClass: WindowSizeClass,
    content: @Composable () -> Unit
) {
    when (windowSizeClass.widthSizeClass) {
        WindowWidthSizeClass.Compact -> {
            // Standard Phone: Bottom Navigation Bar
            Scaffold(bottomBar = { BottomNavBar() }) { content() }
        }
        WindowWidthSizeClass.Medium -> {
            // Foldable / Small Tablet: Navigation Rail
            Row {
                AppNavRail()
                Box(modifier = Modifier.weight(1f)) { content() }
            }
        }
        WindowWidthSizeClass.Expanded -> {
            // Desktop / Large Tablet: Permanent Navigation Drawer + Split Pane
            PermanentNavigationDrawer(drawerContent = { DrawerContent() }) {
                content()
            }
        }
    }
}
```""",
    "short_en": """We support accessibility and screen readers using the Semantics tree, applying Modifier.semantics with contentDescription, role, and mergeDescendants to unify complex cards for TalkBack, and ensuring a minimum 48dp touch target. For adaptive layouts, we use Material 3 WindowSizeClass, adapting navigation and layouts from compact phones using bottom navigation to medium foldables using navigation rails and expanded tablets using permanent drawers and split-pane scaffolds.""",
    "structured_en": """Building production applications that serve global audiences requires equal attention to assistive accessibility technologies and multi-device form factor adaptation.
For accessibility and screen readers like TalkBack, Jetpack Compose constructs a parallel Semantics Tree alongside the visual layout tree.
Instead of allowing TalkBack to read individual fragmented text labels—forcing vision-impaired users to swipe through multiple elements for a single item—we use Modifier.semantics(mergeDescendants = true).
This collapses all child nodes into a single semantic container, announcing a unified description and a clear Role like Role.Button.
Additionally, we enforce the Android accessibility guideline requiring a minimum interactive touch target of 48dp by 48dp using Modifier.minimumInteractiveComponentSize().
For adaptive layouts, modern Compose moves beyond rigid screen width checks by embracing Material 3 WindowSizeClass.
Classified into Compact (phones in portrait), Medium (foldables and small tablets), and Expanded (large tablets and desktop monitors), window size classes dictate responsive navigation patterns.
A phone displays a BottomNavigationBar, a foldable transitions to a NavigationRail, and an expanded tablet presents a dual-column ListDetailPaneScaffold, delivering an optimized user experience across all form factors.""",
    "deep_senior_en": """Under the hood, Compose maintains two parallel node hierarchies: the LayoutNode tree for visual measurement and drawing, and the SemanticsNode tree for assistive accessibility services.
When an assistive technology like TalkBack or Switch Access connects to the Android system, the Android accessibility framework queries the app's View hierarchy.
Compose bridges this via AndroidComposeViewAccessibilityDelegateCompat.
This delegate translates Compose's SemanticsNode hierarchy into native Android AccessibilityNodeInfo objects.
When mergeDescendants is set to true on a modifier, the semantics pipeline merges the sub-tree's semantic properties into a single synthetic AccessibilityNodeInfo, suppressing individual child node traversal and drastically reducing screen reader navigation fatigue.
Custom accessibility actions can also be injected via customActions, allowing users to perform contextual actions (like deleting or archiving an email) through TalkBack menus without navigating to individual small action buttons.
Furthermore, enforcing the minimumInteractiveComponentSize modifier ensures touch targets expand invisible bounds to at least 48dp by 48dp, satisfying platform accessibility criteria even when visible icons measure only 24dp.
On the adaptive layout frontier, Compose Material 3 Adaptive integrates with AndroidX WindowManager.
It dynamically calculates WindowSizeClass from real-time window metrics, accounting for system bars, camera cutouts, and folding hinges.
Using canonical scaffold components like ListDetailPaneScaffold, Compose leverages the underlying Predictive Back and layout animation systems to automatically split or merge panes as devices fold, unfold, or rotate, maintaining uninterrupted user flow without manual activity restarts.""",
    "meta_ar": {
        "id": "COM-22",
        "questionAr": "كيف تدعم سهولة الوصول (Accessibility) وقارئات الشاشة والتصميم المتكيف (Adaptive Layouts) في Compose؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على دعم ذوي الاحتياجات الخاصة عبر شجرة الـ Semantics Tree، ودمج العناصر بـ `mergeDescendants`، وضبط أبعاد اللمس (48dp Touch Target)، واستخدام `WindowSizeClass` لدعم الهواتف والتابلت والأجهزة القابلة للطي.",
        "why_it_matters_ar": "إهمال سهولة الوصول يحرم ملايين المستخدمين من استخدام التطبيق، وتجاهل الـ Adaptive Layouts يجعل التطبيق يظهر مشوهاً أو غير مستغل لمساحة الشاشة الكبيرة في التابلت والأجهزة القابلة للطي.",
        "worked_example_ar": "دمج الـ Semantics وضبط الـ WindowSizeClass:\n```kotlin\n// 1. دمج النصوص لقارئ الشاشة TalkBack في كارت واحد\nCard(modifier = Modifier.semantics(mergeDescendants = true) { role = Role.Button }) { ... }\n// 2. تصميم متكيف حسب حجم الشاشة\nwhen (windowSizeClass.widthSizeClass) {\n    WindowWidthSizeClass.Compact -> BottomBarLayout()\n    WindowWidthSizeClass.Expanded -> TwoPaneLayout()\n}\n```",
        "trade_offs_ar": "كتابة نصوص الـ Semantics وتصميم شاشات متعددة يضيف جهداً في التطوير، لكنه يرفع تقييم التطبيق عالمياً ويضمن توافقه مع معايير المتجر والقوانين الدولية لإمكانية الوصول.",
        "failure_modes_ar": "ترك الأزرار التفاعلية بحجم لمس أصغر من 48dp، أو عدم وضع `contentDescription` للأيقونات، أو تصميم واجهات ثابتة لا تستجيب لتغيير حجم نافذة التابلت.",
        "production_perspective_ar": "في المشروعات العالمية، نلزم فحص accessibility scanner في اختبارات الـ CI، ونعتمد مكتبة `material3-adaptive` لبناء تصميمات تدعم الـ Foldables تلقائياً.",
        "how_to_answer_ar": "قسم الإجابة لقسمين متكاملين: أولاً Accessibility باستخدام شجرة الـ Semantics ودمج الأبناء بـ `mergeDescendants` وضبط مساحة اللمس على 48dp على الأقل، ثانياً Adaptive Layouts باستخدام `WindowSizeClass` (Compact, Medium, Expanded) والتبديل بين BottomBar و NavRail وتصميمات الشاشتين ListDetailPaneScaffold.",
        "talking_points_ar": "شجرة الـ Semantics ومحاكي AndroidComposeViewAccessibilityDelegate، ودمج العناصر بـ mergeDescendants، والحد الأدنى للمس 48dp، وتصنيفات WindowSizeClass، والأجهزة القابلة للطي Foldables.",
        "follow_ups_ar": "- **المحاور:** \"ما هي فائدة استخدام `mergeDescendants = true` مع الكروت والقوائم؟\"\n  **المرشح:** \"بتخلي قارئ الشاشة TalkBack يقرأ الكارت بالكامل كجملة واحدة مركزة بدلاً من إجبار المستخدم الكفيف على السحب 5 مرات لقراءة الاسم ثم الصورة ثم السعر بشكل منفصل وممل.\"\n\n- **المحاور:** \"كيف يتعامل Compose مع الهواتف القابلة للطي (Foldables) في حالة فتح وإغلاق الجهاز؟\"\n  **المرشح:** \"بنستخدم مكتبة `material3-adaptive` اللي بتحسب `WindowSizeClass` آنياً؛ فأول ما يفتح الجهاز بيتحول تلقائياً من Compact إلى Expanded ويعرض عمودين بـ `ListDetailPaneScaffold` بدون إعادة تشغيل الشاشة.\"",
        "self_check_ar": "هل غطيت إمكانية الوصول وقارئات الشاشة؟ هل شرحت دور Semantics و mergeDescendants؟ وهل بينت كيفية استخدام WindowSizeClass للأجهزة اللوحية؟",
        "references_ar": f"- [Compose Accessibility Guide](https://developer.android.com/develop/ui/compose/accessibility) — التوثيق الرسمي لإمكانية الوصول في كومبوز.\n- [Supporting different window sizes](https://developer.android.com/develop/ui/compose/layouts/adaptive) — دليل بناء الشاشات المتكيفة في كومبوز.",
        "quick_answer_ar": "بندعم إمكانية الوصول (Accessibility) وقارئات الشاشة عبر شجرة المعاني (Semantics Tree)؛ بنستخدم `Modifier.semantics` لتحديد `contentDescription` ووظيفة العنصر `role`، وبنستخدم `mergeDescendants = true` عشان TalkBack يقرأ الكارت المجمع كعنصر واحد مفيد بدل التشتيت، مع الحفاظ على مساحة لمس لا تقل عن 48dp. أما التصميم المتكيف (Adaptive Layouts) فبنبنيه باستخدام `WindowSizeClass` من Material 3؛ بنقسم الشاشات لـ Compact للموبايل بشريط تنقل سفلي، و Medium للأجهزة القابلة للطي بـ Navigation Rail، و Expanded للتابلت بشاشات مقسمة لعمودين (List-Detail Pane) لاستغلال المساحة بذكاء.",
        "best_answer_ar": "دعم إمكانية الوصول وبناء واجهات متكيفة هو الركيزة الأساسية لجعل التطبيق عالمياً وشاملاً لكل فئات المستخدمين ومختلف أحجام الأجهزة.\n\nفيما يخص سهولة الوصول وقارئات الشاشة زي TalkBack:\nكومبوز بتبني شجرة موازية اسمها `Semantics Tree`. عشان نوفر أفضل تجربة، بنجمع العناصر المتفرقة داخل الكارت باستخدام `Modifier.semantics(mergeDescendants = true)`. الحركة دي بتخلي قارئ الشاشة ينطق: 'كارت منتج كذا وسعره كذا وهو زرار قابل للنقر' في تمريرة واحدة، بدل ما يجبر المستخدم ضعيف البصر إنه يدوس على كل نص وصورة لوحدها. وكمان بنلتزم بمعيار جوجل الصارم إن أي مساحة تفاعلية لازم متقلش عن 48dp بـ `Modifier.minimumInteractiveComponentSize()` عشان سهولة الضغط.\n\nوفيما يخص التصميم المتكيف (Adaptive Layouts):\nعصر التصميم الثابت لشاشات الموبايل انتهى مع ظهور الأجهزة القابلة للطي (Foldables) والتابلت. بنستخدم معيار `WindowSizeClass` من Material 3، وبناءً على عرض النافذة بنكيف الواجهة بسلاسة:\nفي الشاشات الصغيرة (Compact)، بنعرض الشاشة كاملة مع BottomBar عادي.\nفي الشاشات المتوسطة (Medium) زي الهواتف القابلة للطي المفتوحة، بنتحول تلقائياً لـ Navigation Rail جانبي.\nوفي الشاشات الكبيرة (Expanded) زي التابلت والديسك توب، بنشغل مكونات الـ Adaptive الجاهزة زي `ListDetailPaneScaffold`؛ القائمة بتتعرض على الشمال والتفاصيل على اليمين في شاشتين متزامنتين، وده بيقدم تجربة استخدام احترافية بدون إعادة كتابة أي كود في طبقة البيانات.",
        "deep_answer_ar": "تحت الكابوت، محرك كومبوز بيحافظ على بنيتين متوازيتين بالكامل في الذاكرة: الأولى هي شجرة `LayoutNode` المسؤولة عن قياس الحجم والرسم على الشاشة، والتانية هي شجرة `SemanticsNode` المخصصة لخدمات مساعدة النظام.\n\nأول ما خدمة زي TalkBack تتصل بالنظام، أندرويد بيطلب معلومات الشاشة عبر وسيط اسمه `AndroidComposeViewAccessibilityDelegateCompat`.\nالوسيط ده بيمسك شجرة الـ Semantics ويحولها لكائنات `AccessibilityNodeInfo` الأصلية في نظام أندرويد. لما تفعل `mergeDescendants = true`، نظام الـ Semantics بيمسح النودز الفرعية من التقرير الموجه للنظام، ويولد عقدة وهمية واحدة مجمعة بتحتوي على كل النصوص والإجراءات، وده بيقلل وقت تصفح الكفيف للشاشة بأكتر من 70%.\nوفوق كده، خاصية `Modifier.minimumInteractiveComponentSize()` بتوسع مساحة اللمس غير المرئية لتصل إلى 48x48dp على الأقل حتى لو كانت الأيقونة البصرية صغيرة بحجم 24dp، لحماية المستخدمين الذين يعانون من صعوبات حركية.\n\nأما على صعيد الـ Adaptive Layouts، مكتبة `material3-adaptive` مبنية فوق نواة `AndroidX WindowManager`.\nالمكتبة دي بتحسب مقاسات الشاشة الحقيقية في كل لحظة، وبتاخد في اعتبارها مفصلات الأجهزة القابلة للطي (Folding Hinges) وحواف الشاشة وثقب الكاميرا (Cutouts). ولما المستخدم يفتح التليفون القابل للطي في وضع الـ Half-folded (زي اللابتوب)، المحرك بيكتشف الـ Hinge ويقسم المحتوى تلقائياً لنصفين علوي وسفلي، وبيدعم حركات الـ Predictive Back Animation بسلاسة فائقة وبدون الحاجة لإعادة إنشاء الـ Activity من الصفر في بيئة الإنتاج."
    }
}

# ==========================================
# COM-23: A Compose screen re-renders excessively after each keystroke. How do you profile and fix it?
# ==========================================
DATA["COM-23"] = {
    "concept_en": """Excessive recomposition on every keystroke occurs when transient text field state is hoisted unnecessarily high in the composable hierarchy or when state mutations invalidate unskippable sibling composables. Diagnosing this bottleneck involves attaching the Android Studio Layout Inspector to observe recomposition tick counters during typing, alongside running Compose Compiler Metrics to identify unstable parameter types across the view tree. Resolving the regression requires isolating the raw keystroke state locally inside the input component, hoisting only debounced query values to architecture ViewModels, and stabilizing sibling data models using @Immutable wrappers to enable smart compiler skipping.""",
    "walkthrough_en": """Diagnosing and eliminating keystroke-induced recomposition churn:
```kotlin
// ❌ FAULTY ARCHITECTURE: Top-level parent screen observes every single keystroke!
// Typing 1 character causes ParentScreen, Header, HeavyBanner, and ProductGrid to recompose!
@Composable
fun BadSearchScreen(viewModel: BadSearchViewModel) {
    val query by viewModel.queryText.collectAsStateWithLifecycle()
    val products by viewModel.products.collectAsStateWithLifecycle()

    Column {
        HeavyHeader() // Recomposes on every keystroke!
        TextField(value = query, onValueChange = { viewModel.updateQuery(it) })
        ProductGrid(products = products) // Recomposes on every keystroke if products list is unstable!
    }
}

// ✅ ARCHITECTURAL BEST PRACTICE: Isolate keystroke state and debounce upstream events!
@Composable
fun OptimizedSearchScreen(
    productsState: ImmutableProductsState,
    onQuerySubmitted: (String) -> Unit
) {
    Column {
        HeavyHeader() // Skipped! Never recomposes during typing!
        LocalSearchField(onDebouncedQuery = onQuerySubmitted) // Recomposition strictly isolated here!
        ProductGrid(products = productsState) // Skipped! Inputs remain unchanged during typing!
    }
}

@Composable
fun LocalSearchField(onDebouncedQuery: (String) -> Unit) {
    // Keystroke state is isolated to this leaf composable only!
    var localText by remember { mutableStateOf("") }

    LaunchedEffect(localText) {
        delay(300) // Debounce before sending event upstream!
        onDebouncedQuery(localText)
    }

    TextField(
        value = localText,
        onValueChange = { localText = it },
        placeholder = { Text("Search...") }
    )
}
```""",
    "short_en": """We diagnose excessive keystroke recomposition using Layout Inspector recomposition counters and Compose Compiler metrics. The primary root cause is hoisting raw keystroke state to the top-level parent, which forces unskippable siblings to re-execute on every character. We fix this by isolating local text state within the search bar component, debouncing updates sent to the ViewModel, and ensuring sibling components receive @Immutable data classes so they are skipped completely during input.""",
    "structured_en": """Diagnosing and curing excessive recomposition triggered by user keystrokes is a classic real-world Android performance problem.
When a user types in a text field, every single character change produces a state update.
If the application suffers from flawed state architecture, typing a single letter causes the entire screen—including heavy image carousels, complex lists, and navigation headers—to recompose continuously, producing noticeable typing lag and burning CPU cycles.
To profile this regression, we open Android Studio Layout Inspector while typing in a debug build.
Layout Inspector reveals the exact composables whose recomposition counters increment with every key press.
We then consult Compose Compiler Metrics to inspect the stability of the affected sibling composables.
The root cause is almost always dual-faceted: raw keystroke state was hoisted all the way to the top-level screen container, and sibling components accept unstable parameter types like raw standard Lists.
We apply a three-step architectural fix.
First, we isolate the raw text state locally inside a dedicated SearchBar composable so that only the text input node recomposes on keystrokes.
Second, we apply a debounce operator (such as delay(300)) before propagating the query upstream to the ViewModel.
Third, we ensure all sibling composables accept strictly @Immutable data models, allowing the Compose runtime to skip them entirely during input.""",
    "deep_senior_en": """Under the hood, this performance degradation is governed by RecomposeScope invalidation boundaries and SlotTable dependency tracking.
When a composable reads a SnapshotState primitive—such as collecting a query StateFlow at the root screen level—the Compose compiler associates that state read with the root composable's RecomposeScope.
Every keystroke commits a new snapshot to the global Snapshot system.
The snapshot commit notifies the root RecomposeScope that its dependencies mutated, triggering an immediate invalidation of that scope.
During the subsequent composition pass, the Composer executes the root function body from top to bottom.
If child composables accept unstable parameters (such as standard Kotlin List<Product> or lambdas capturing mutable outer variables), the compiler's synthetic changed bitmask evaluates to UNCERTAIN.
Because the arguments cannot be guaranteed stable, the compiler is prohibited from executing early-return skipping, forcing every child composable to re-execute its layout logic, re-allocate modifier nodes, and reconcile slot intervals.
By moving the mutable state read into a localized leaf composable (LocalSearchField), the root RecomposeScope never reads the active keystroke state.
Consequently, snapshot commits invalidate only the localized leaf scope, leaving the parent and all sibling scopes completely un-invalidated.
Furthermore, debouncing the upstream event using Kotlin Coroutines prevents rapid network calls and database queries from interrupting the main thread during typing, securing rock-solid 120fps input fluidity.""",
    "meta_ar": {
        "id": "COM-23",
        "questionAr": "شاشة Compose تعيد الرندرة بشكل مفرط بعد كل ضغطة حرف. كيف تشخص المشكلة وتصلحها؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على تشخيص مشاكل الأداء بالـ Layout Inspector و Compiler Metrics، وفهم حدود الـ RecomposeScope، وتطبيق مبدأ عزل الحالة (State Isolation) والـ Debounce، وضمان الـ Skipping للعناصر المجاورة.",
        "why_it_matters_ar": "إعادة رندرة الشاشة بالكامل مع كل حرف يكتبه المستخدم يسبب ثقلاً ملحوظاً في الكتابة (Typing Latency) وسخونة المعالج واستهلاكاً كبيراً للبطارية.",
        "worked_example_ar": "عزل حالة الكتابة وتطبيق Debounce:\n```kotlin\n// عزل حالة النص محلياً في مكون البحث لمنع إعادة رندرة الشاشة الأب\n@Composable fun SearchBar(onQueryDebounced: (String) -> Unit) {\n    var text by remember { mutableStateOf(\"\") }\n    LaunchedEffect(text) { delay(300); onQueryDebounced(text) }\n    TextField(value = text, onValueChange = { text = it })\n}\n```",
        "trade_offs_ar": "عزل الحالة محلياً يتطلب التعامل مع حالتين (النص المحلي المؤقت والنص النهائي في الـ ViewModel)، لكنه يقضي على التهنيج ويوفر استجابة فورية في الكتابة.",
        "failure_modes_ar": "رفع حالة كل حرف للـ ViewModel مباشرة وقراءتها في جذر الشاشة الأب مع تمرير قوائم غير مستقرة للعناصر المجاورة.",
        "production_perspective_ar": "في المشروعات الكبيرة، نعتمد عزل حالة الإدخال محلياً في مكونات الحقول، ونطبق `debounce(300ms)` قبل إرسال نصوص البحث للطبقات الخلفية، ونراجع مقاييس الكومبايلر دورياً.",
        "how_to_answer_ar": "ابدأ بالتشخيص: استخدام Layout Inspector لمراقبة عدادات الرندرة أثناء الكتابة واستخراج تقارير Compiler Metrics، وحدد السببين: رفع حالة الحروف للشاشة الأب وعدم استقرار العناصر المجاورة، واشرح الحل: عزل حالة النص محلياً في حقل البحث، وتطبيق Debounce، وجعل العناصر المجاورة `@Immutable` لتتخطاها كومبوز.",
        "talking_points_ar": "أدوات التشخيص (Layout Inspector و Metrics)، ونطاق RecomposeScope، وعزل الحالة (State Isolation)، ومفهوم Debouncing، واستقرار الباراميترات المجاورة بـ @Immutable.",
        "follow_ups_ar": "- **المحاور:** \"لماذا تعيد العناصر المجاورة لحقل البحث الرندرة إذا كانت لا تستخدم نص البحث إطلاقاً؟\"\n  **المرشح:** \"لأن حالة النص تم قراءتها في الشاشة الأب، فالأب بيعيد رندرة نفسه بالكامل؛ ولو العناصر المجاورة بتستقبل باراميترات Unstable زي `List` عادية، الكومبايلر مش بيقدر يتخطاها فبيعيد رندرتها هي كمان بالتبعية.\"\n\n- **المحاور:** \"ما هي المدة الزمنية المثالية للـ Debounce في حقول البحث في أندرويد؟\"\n  **المرشح:** \"عادة بين 300 إلى 500 ميلي ثانية؛ دي مهلة كافية تتأكد إن المستخدم خلص كتابة الكلمة بدون ما يشعر بأي تأخير ملحوظ في ظهور النتائج.\"",
        "self_check_ar": "هل شرحت خطوات التشخيص بالأدوات؟ هل حددت السبب الجذري؟ وهل قدمت الحل المعماري الكامل بعزل الحالة والـ Debounce؟",
        "references_ar": f"- [Compose Performance: Debugging](https://developer.android.com/develop/ui/compose/performance/layout-inspector) — التوثيق الرسمي لتشخيص مشاكل الأداء في كومبوز.\n- [State Hoisting and Scoping](https://developer.android.com/develop/ui/compose/state#state-hoisting) — دليل جوجل لعزل ونطاقات الحالة.",
        "quick_answer_ar": "بنشخص المشكلة باستخدام أداة Layout Inspector في أندرويد ستوديو؛ بنكتب في الحقل ونراقب عداد الـ Recomposition، وبنفتح تقارير Compose Compiler Metrics عشان نكشف الباراميترات غير المستقرة. السبب الجذري دايماً بيكون إن حالة النص المتغير مع كل حرف مرفوعة ومقروءة في جذر الشاشة الأب، وباقي المكونات المجاورة بتستقبل بيانات غير مستقرة زي `List` فبتعيد الرندرة معاها. والحل بيتلخص في تلات خطوات: عزل حالة النص محلياً داخل مكون حقل البحث، وتطبيق `delay(300)` لعمل Debounce قبل إرسال النص للـ ViewModel، وضمان استقرار بيانات المكونات المجاورة بـ `@Immutable` عشان كومبوز تتخطاها تماماً.",
        "best_answer_ar": "المشكلة دي واحدة من أشهر مشاكل الأداء الكلاسيكية في Jetpack Compose، وحلها بيكشف فهم المطور لكيفية عمل الـ RecomposeScopes ونظام الـ Snapshots.\n\nخطوات التشخيص:\nأولاً بنفتح Layout Inspector ونبدأ نكتب في حقل البحث؛ لو لاحظت إن عداد الـ Recomposition الخاص بالشاشة الرئيسية وعناصر القائمة والهيدر بيزيد مع كل حرف، فده مؤشر صريح إن نطاق التحديث غير معزول. ثانياً بنراجع تقرير Compiler Metrics عشان نتأكد من الـ Skippability الخاصة بالمكونات المجاورة.\n\nالسبب الحقيقي هو خطأ في معمارية الحالة (State Architecture):\nالمطور مخلي الـ ViewModel يحدث الـ State مع كل حرف، وبيروح يقرأ الـ State دي في أعلى نقطة في الشاشة الأب! لما الأب يعيد الرندرة، بيمر على كل الأبناء؛ ولو الأبناء بيستقبلوا باراميترات عادية مش مميزة بـ `@Immutable` (زي الـ List)، كومبوز بتضطر تعيد تشغيلهم كلهم.\n\nالحل المعماري الاحترافي:\nأولاً: عزل الحالة؛ بنخلي متغير الـ `text` يعيش كحالة محلية بـ `remember` داخل دالة حقل البحث فقط، بكده الحرف المكتوب مش هيعيد رندرة غير الحقل نفسه.\nثانياً: تطبيق الـ Debouncing؛ بنستخدم `LaunchedEffect(text)` مع `delay(300)` عشان ننتظر المستخدم يخلص كتابة، وبعدين نصعد الحدث للـ ViewModel مرة واحدة.\nثالثاً: تثبيت الموديلز؛ بنغلف القوائم في كلاسات مستقرة بـ `@Immutable`، بكده الشاشة بتفضل ثابتة وسلسة بنسبة 100% وبدون أي لاج في الكيبورد.",
        "deep_answer_ar": "تحت الكابوت، الأزمة بتتمحور حول كيفية تسجيل نطاقات إعادة التركيب (RecomposeScopes) في هيكل الـ `SlotTable`.\n\nلما بتقرأ متغير من نوع `SnapshotState` في جسم دالة الكومبوزابل الأب، نظام الـ Snapshots بيسجل تبعية قراءة مباشرة مع الـ RecomposeScope الخاص بالأب. لما المستخدم يضغط حرف على الكيبورد، الـ Snapshot بيعمل Commit لقيمة جديدة، وده بيعلم نطاق الأب بالكامل إنه غير صالح (Invalidated).\nفي الفريم التالي، المحرك بيشغل دالة الأب من أولها لآخرها. أثناء المرور على المكونات الفرعية (زي الهيدر والقائمة والبانر)، المحرك بيفحص مصفوفة الأعلام `changed bitmask`. لو المكونات دي بتستقبل باراميترات غير مستقرة (زي `List<Product>` العادية أو Lambdas ماسكة متغيرات خارجية)، الكومبايلر بيجبر قيمة البتات تكون `UNCERTAIN`، وده بيمنع استخدام تعليمة الـ Early Return ويجبر المعالج على إعادة قياس ورسم الشجرة كلها مع كل حرف!\n\nلما بنعزل قراءة متغير الحالة داخل Leaf Composable فرعي، الـ RecomposeScope الخاص بالأب مبيكونش مسجل أي قراءة للنص المتغير. النتيجة إن عملية الـ Commit بتنبه الـ Scope الفرعي فقط، فالمحرك بيعيد رندرة حقل النص الصغير فقط ويتجاهل باقي الشاشة تماماً.\nودمج ده مع Debounce في الكوروتين بيمنع إطلاق مئات الـ SQL Queries أو طلبات الشبكة، وده بيحافظ على ميزانية الـ 16ms وبيضمن استجابة فورية ونعومة تامة أثناء الكتابة السريعة."
    }
}

# ==========================================
# COM-24: A listener keeps working after a composable leaves composition. Which effect is wrong?
# ==========================================
DATA["COM-24"] = {
    "concept_en": """When a listener, broadcast receiver, sensor observer, or external callback continues executing after a composable unmounts from the composition tree, the root cause is registering imperative listeners inside inappropriate effect handlers or bare composable bodies without lifecycle cleanup. Using LaunchedEffect(Unit) or SideEffect to register an observer is a critical anti-pattern because neither primitive provides an automatic teardown callback. The correct architectural primitive is DisposableEffect, which enforces an explicit onDispose { ... } cleanup block that the Compose runtime guarantees to execute whenever the effect keys change or when the composable leaves the composition hierarchy entirely.""",
    "walkthrough_en": """Fixing a persistent listener memory leak using DisposableEffect:
```kotlin
// ❌ CRITICAL LEAK: LaunchedEffect(Unit) has NO cleanup teardown mechanism!
// When the user navigates away, sensorListener continues running, leaking memory and draining battery!
@Composable
fun LeakySensorScreen(sensorManager: SensorManager) {
    LaunchedEffect(Unit) {
        val listener = object : SensorEventListener {
            override fun onSensorChanged(event: SensorEvent?) { /* handle updates */ }
            override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {}
        }
        sensorManager.registerListener(listener, sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER), SensorManager.SENSOR_DELAY_NORMAL)
        // ❌ There is NO onDispose block! The listener outlives the composable and leaks forever!
    }
}

// ✅ ARCHITECTURAL BEST PRACTICE: DisposableEffect guarantees cleanup on exit!
@Composable
fun SafeSensorScreen(sensorManager: SensorManager) {
    DisposableEffect(sensorManager) {
        val listener = object : SensorEventListener {
            override fun onSensorChanged(event: SensorEvent?) { /* handle updates */ }
            override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {}
        }
        val sensor = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)
        sensorManager.registerListener(listener, sensor, SensorManager.SENSOR_DELAY_NORMAL)

        // ✅ onDispose executes GUARANTEED when leaving composition or when sensorManager changes!
        onDispose {
            sensorManager.unregisterListener(listener)
        }
    }
}
```""",
    "short_en": """The wrong effect being used is LaunchedEffect(Unit) or SideEffect, neither of which provides an explicit cleanup mechanism. When a composable unmounts, listeners registered inside them remain active, leaking memory and draining battery. The correct tool is DisposableEffect. DisposableEffect enforces an onDispose block that is guaranteed by the Compose runtime to execute whenever the effect key changes or when the composable leaves the composition entirely, ensuring proper resource unregistration.""",
    "structured_en": """Encountering background listeners that outlive composable lifecycles is one of the most hazardous resource leakage patterns in Jetpack Compose development.
The defect occurs when developers register external system observers—such as BroadcastReceivers, SensorEventListeners, LocationServices listeners, or third-party SDK analytics observers—inside LaunchedEffect(Unit) or directly in the composable body.
While LaunchedEffect(Unit) cancels its internal coroutine Job when leaving composition, it has no intrinsic mechanism to invoke imperative unregistration APIs on external Android system services.
Similarly, SideEffect executes on every recomposition with zero teardown capability.
Consequently, the platform service retains a strong reference to the listener callback, leaking memory, keeping GPS or sensors active, and causing background battery drain.
The correct, non-negotiable tool for this pattern is DisposableEffect.
DisposableEffect is explicitly designed for side-effects that require teardown logic.
It forces developers to supply an onDispose clause at compile time.
The Compose runtime guarantees that onDispose will execute in two deterministic scenarios: before re-executing the effect with updated keys, and immediately when the composable leaves the composition tree, ensuring reliable resource cleanup.""",
    "deep_senior_en": """Under the hood, DisposableEffect interfaces directly with the Composer's Disposables lifecycle tracking queue inside the SlotTable.
When a DisposableEffect block executes, the Compose compiler allocates a DisposableEffectImpl node within the current slot interval.
The lambda block must return a DisposableEffectResult instance, which encapsulates the user-defined onDispose() closure.
If the developer omits the onDispose block, the Kotlin compiler generates a compile-time type mismatch error, enforcing correctness before bytecode generation.
When the hosting composable unmounts from the composition tree—such as when the user navigates back or conditional UI branches evaluate to false—the Composer initiates a teardown pass across the SlotTable.
During this pass, the Composer traverses all registered DisposableEffectImpl nodes and immediately invokes their cached onDispose() lambdas synchronously on the main thread before discarding the slot memory.
By contrast, LaunchedEffect creates a StandaloneCoroutine tied to a Job.
While the Job cancels cooperatively upon unmounting, standard Java/Android listener callbacks registered with system services (like android.hardware.SensorManager) are not coroutines; canceling the coroutine Job leaves the underlying platform callback registered in Android OS memory.
Failing to unregister these listeners prevents the Garbage Collector from freeing the enclosing Activity or Context references, causing severe native handle leaks and draining the battery in the background.
Senior engineers mandate DisposableEffect in code reviews for any integration touching system services, broadcast receivers, or hardware listeners.""",
    "meta_ar": {
        "id": "COM-24",
        "questionAr": "مستمع (Listener) يستمر في العمل بعد مغادرة الكومبوزابل للشاشة. ما هي الأداة الخاطئة المستخدمة وكيف تصححها؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على تشخيص تسريبات الذاكرة الناتجة عن سوء اختيار أدوات الآثار الجانبية، وفهم الفرق بين `LaunchedEffect` و `DisposableEffect`، وإلزامية استخدام `onDispose` لتنظيف الموارد.",
        "why_it_matters_ar": "استمرار المستمعين في العمل بعد مغادرة الشاشة يسرب الذاكرة ويستنزف البطارية وخدمات الموقع في جيب المستخدم، ويؤدي إلى كراشات غير متوقعة عند محاولة المستمع تحديث واجهة لم تعد موجودة.",
        "worked_example_ar": "تصحيح تسريب المستمع بـ DisposableEffect:\n```kotlin\n// ❌ خاطئ: LaunchedEffect لا يملك آلية تنظيف للمستمعين\nLaunchedEffect(Unit) { sensorManager.registerListener(listener) }\n// ✅ صحيح: DisposableEffect يضمن إلغاء التسجيل بـ onDispose فور مغادرة الشاشة\nDisposableEffect(sensorManager) {\n    sensorManager.registerListener(listener)\n    onDispose { sensorManager.unregisterListener(listener) }\n}\n```",
        "trade_offs_ar": "استخدام `DisposableEffect` يتطلب كتابة كود تنظيف صريح في `onDispose`، وهو الإجراء الإلزامي لمنع تسريبات الذاكرة وحماية موارد الجهاز.",
        "failure_modes_ar": "استخدام `LaunchedEffect` لتسجيل BroadcastReceiver مع الاعتقاد بأن إلغاء الكوروتين يلغي تسجيل المستمع في نظام أندرويد تلقائياً.",
        "production_perspective_ar": "في المشروعات الكبيرة، نضع قواعد فحص كود (Lint / Detekt Rules) تمنع تسجيل أي listener أو receiver إلا داخل `DisposableEffect` مع التحقق من وجود `onDispose`.",
        "how_to_answer_ar": "حدد الأداة الخاطئة فوراً: استخدام `LaunchedEffect` أو `SideEffect` أو وضع الكود في جسم الدالة مباشرة، واشرح السبب: لأن هذه الأدوات ليس لديها كولباك تنظيف، واذكر الحل الصحيح: استخدام `DisposableEffect` مع توضيح أن الرنتايم يضمن تشغيل كود `onDispose` فور خروج المكون من الشاشة.",
        "talking_points_ar": "الأداة الخاطئة LaunchedEffect مقابل DisposableEffect، وآلية التنظيف بـ onDispose، والفرق بين إلغاء الكوروتين وإلغاء تسجيل المستمعين في النظام، وتسريبات الـ SensorManager والـ Receivers.",
        "follow_ups_ar": "- **المحاور:** \"لماذا لم يقم LaunchedEffect بإلغاء تسجيل المستمع عندما غادر المكون الشاشة؟\"\n  **المرشح:** \"لأن `LaunchedEffect` بيلغي كائن الـ Job الخاص بالكوروتين فقط، لكن المستمع مسجل في نظام تشغيل أندرويد (زي SensorManager)، والنظام ميعرفش أي حاجة عن الكوروتين، فلازم كود تنظيف صريح ينادي `unregister`.\"\n\n- **المحاور:** \"متى يتم استدعاء دالة onDispose في DisposableEffect؟\"\n  **المرشح:** \"في حالتين حصرياً: أولاً لما المكون يخرج تماماً من الشاشة (Leaves Composition)، وثانياً قبل إعادة تشغيل التأثير بقيم مفاتيح جديدة.\"",
        "self_check_ar": "هل حددت الأداة الخاطئة بوضوح؟ هل بينت سر استمرار التسريب؟ وهل شرحت دور DisposableEffect و onDispose؟",
        "references_ar": f"- [Side-effects in Jetpack Compose: DisposableEffect](https://developer.android.com/develop/ui/compose/side-effects#disposableeffect) — التوثيق الرسمي لجوجل لـ DisposableEffect.\n- [Preventing memory leaks in Compose](https://medium.com/androiddevelopers/) — دليل مطوري أندرويد لتفادي تسريبات الذاكرة في كومبوز.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "الأداة الخاطئة المستخدمة هي `LaunchedEffect(Unit)` أو `SideEffect` أو كتابة كود التسجيل في جسم الدالة مباشرة؛ لأن الأدوات دي معندهاش أي وسيلة لإلغاء التسجيل وتنظيف الموارد لما المكون يخرج من الشاشة. الحل الصحيح هو استخدام `DisposableEffect`؛ الأداة دي بتلزم المطور بكتابة بلوك `onDispose { ... }`، ومحرك كومبوز بيضمن بنسبة 100% إنه هينفذ كود التنظيف ويلغي تسجيل المستمع فور خروج الكومبوزابل من شجرة العرض أو عند تغير المفاتيح.",
        "best_answer_ar": "المشكلة دي واحدة من أخطر أخطاء تسريب الموارد والذاكرة في Jetpack Compose، ومقابلة السينيور بتركز عليها عشان تختبر فهم المطور العميق لدورة حياة الكومبوزابل مقابل خدمات نظام أندرويد.\n\nالأداة الخاطئة التي استخدمها المطور هي في الغالب `LaunchedEffect(Unit)`.\nالمطور اعتقد إنه بمجرد خروج الشاشة، الكوروتين هيتكنسل فالمستمع هيقف. الخطأ القاتل هنا هو إن المستمع مسجل في خدمة نظام تابعة لأندرويد خارج عالم الكومبوز تماماً، زي `SensorManager` أو `LocationManager` أو `BroadcastReceiver`. لما الكومبوزابل يخرج، الكوروتين بيلغي الـ Job بتاعه، لكن خدمة أندرويد بتفضل ماسكة مرجع قوي (Strong Reference) للمستمع وشغالة تسحب بطارية وحساسات في جيب المستخدم!\n\nالحل الصحيح والوحيد هو استخدام `DisposableEffect`:\nالدالة دي مصممة خصيصاً للآثار الجانبية اللي بتحتاج تنظيف وهدم صريح (Teardown Logic).\nبنسجل المستمع جوه جسم الدالة، وبنكتب في نهايتها بلوك `onDispose` جواه كود إلغاء التسجيل `sensorManager.unregisterListener(listener)`.\nرنتايم كومبوز بيضمن تشغيل كود `onDispose` فوراً في لحظة مغادرة المكون لشجرة العرض، وده بيقفل المستمع وينظف الذاكرة تماماً.",
        "deep_answer_ar": "تحت الكابوت، الـ `DisposableEffect` بتتعامل مباشرة مع طابور دورة حياة الـ Disposables اللي بيحتفظ بيه كائن الـ Composer داخل مصفوفة الـ `SlotTable`.\n\nأثناء تنفيذ `DisposableEffect`، الكومبايلر بيحجز نود من نوع `DisposableEffectImpl` في الـ Slot الحالي. الدالة دي مش بترجع Unit عادي، بل بتلزم المطور يرجع كائن `DisposableEffectResult` اللي بيغلف دالة الـ `onDispose()`. لو نسيت تكتب `onDispose`، الكومبايلر هيرمي خطأ تجميع فوري (Compile-time Error).\n\nأول ما الكومبوزابل يخرج من شجرة العرض—سواء المستخدم داس زرار الرجوع أو بسبب شرط `if/else` أصبح false—المحرك بينفذ تمرير هدم كامل (Teardown Pass) على الـ SlotTable. بيمسك كل كائنات `DisposableEffectImpl` المسجلة وينادي دوال `onDispose()` بتاعتها بشكل متزامن على الخيط الرئيسي قبل ما يمسح النودز من الذاكرة.\n\nبينما `LaunchedEffect` بيعمل مجرد `StandaloneCoroutine`؛ الكوروتين بيتعلق بـ Job، ولما المكون يخرج بيحصل له Cooperative Cancellation. لكن كولباكات الجافا وأندرويد الكلاسيكية مش كوروتينات، فإلغاء الـ Job ملوش أي تأثير على المستمع المسجل في خدمات النظام في C++ والـ Framework. وعدم إلغاء التسجيل بيمنع الـ Garbage Collector من تنظيف كائن الـ Activity ويسرب الذاكرة ويستنزف بطارية الهاتف والـ GPS في جيب المستخدم.\nعشان كده في مراجعات الكود للإنتاج، بنرفض تماماً تسجيل أي Listener أو Receiver إلا داخل `DisposableEffect` لضمان الحفاظ على موارد النظام."
    }
}

# ==========================================
# COM-25: A user taps Save twice while a request is in flight. How do you make UI and domain behavior safe?
# ==========================================
DATA["COM-25"] = {
    "concept_en": """Preventing duplicate submission when a user rapidly double-taps an action requires a coordinated defense across UI presentation, ViewModel concurrency, and domain idempotency. At the UI presentation layer, the interactive component must be immediately disabled using state (enabled = !state.isSubmitting) or visually replaced with a progress indicator to prevent further click gestures. At the ViewModel layer, coroutine concurrency must be guarded using Mutex locks, atomic boolean flags, or Flow operators like mapLatest or dropWhile. At the domain and backend layers, every submission must carry a unique idempotency key (such as a UUID) to guarantee that duplicate network transmissions execute as a safe no-op.""",
    "walkthrough_en": """Defending against rapid double-tap submissions across UI, ViewModel, and Network:
```kotlin
// 1. UI Layer: Disable button immediately when isSubmitting is true
@Composable
fun SaveTaskButton(
    isSubmitting: Boolean,
    onSaveClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Button(
        onClick = onSaveClick,
        enabled = !isSubmitting, // UI-level instant disablement!
        modifier = modifier
    ) {
        if (isSubmitting) {
            CircularProgressIndicator(modifier = Modifier.size(20.dp), strokeWidth = 2.dp)
        } else {
            Text("Save Task")
        }
    }
}

// 2. ViewModel & Domain Layer: Concurrency guard and Idempotency Key
@HiltViewModel
class TaskViewModel @Inject constructor(
    private val saveTaskUseCase: SaveTaskUseCase
) : ViewModel() {
    private val _uiState = MutableStateFlow(TaskUiState())
    val uiState = _uiState.asStateFlow()

    private var activeJob: Job? = null
    private val submitMutex = Mutex()

    fun submitTask(taskData: TaskData) {
        // Guard 1: Ignore call if already in-flight!
        if (activeJob?.isActive == true) return

        activeJob = viewModelScope.launch {
            if (!submitMutex.tryLock()) return@launch // Guard 2: Mutex prevents concurrent entry!

            try {
                _uiState.update { it.copy(isSubmitting = true) }
                // Guard 3: Pass idempotent UUID so backend processes duplicate requests safely
                val idempotencyKey = UUID.randomUUID().toString()
                saveTaskUseCase(taskData, idempotencyKey)
                _uiState.update { it.copy(isSubmitting = false, isSuccess = true) }
            } catch (e: Exception) {
                _uiState.update { it.copy(isSubmitting = false, errorMessage = e.message) }
            } finally {
                submitMutex.unlock()
            }
        }
    }
}
```""",
    "short_en": """We defend against double-taps through a layered strategy. In the UI, we disable the button immediately using enabled = !state.isSubmitting and show a loading spinner. In the ViewModel, we guard against concurrent execution using activeJob.isActive checks or Mutex.tryLock() to reject duplicate calls while a request is in flight. At the domain and network layers, we pass a client-generated idempotency key (UUID) so the backend processes duplicated packets safely without duplicating transactions.""",
    "structured_en": """Handling rapid duplicate user taps is an essential resilience pattern tested in senior Android engineering interviews.
A user pressing Save twice in rapid succession can trigger duplicate database entries, double financial payments, or corrupted state.
A robust architecture implements a multi-layered defense.
Layer one is UI presentation deterrence.
The button's enabled parameter must bind to the reactive UI state (enabled = !uiState.isSubmitting).
The moment the first click registers, the UI updates its state, immediately disabling the button and ignoring subsequent click gestures.
However, UI disablement alone is insufficient because touch dispatch queues can fire two tap events within the same frame before recomposition finishes.
Layer two is ViewModel concurrency gating.
Inside the ViewModel, we guard the submission method against concurrent execution.
We check if the existing coroutine Job is active (if (job?.isActive == true) return) or utilize Mutex.tryLock() to ensure that only a single submission coroutine can execute at any given time.
Layer three is domain and network idempotency.
Every mutation request generates a client-side idempotency key (such as a UUID).
The backend uses this token to deduplicate requests, guaranteeing that even if a retry mechanism sends duplicate network packets, the transaction is processed exactly once.""",
    "deep_senior_en": """Under the hood, addressing double-tap race conditions exposes the asynchronous latency between hardware touch event dispatch and Compose frame recomposition.
When a user double-taps rapidly, the platform hardware digitizer generates two MotionEvents spaced mere milliseconds apart.
Because Compose dispatches touch events through the PointerInputModifierNode pipeline during hit testing, both clicks can be processed and queued on the Main thread before the first click's state mutation can trigger Choreographer VSYNC, execute recomposition, and update the Button's enabled constraint.
Relying solely on enabled = false leaves a microscopic timing window where both clicks invoke the onClick callback.
To neutralize this window, senior engineers implement thread-safe concurrency guards inside the architecture ViewModel.
Using Kotlin Coroutines Mutex with tryLock() guarantees atomic entrance.
If thread execution enters while a lock is held, tryLock() returns false immediately without suspending, safely dropping the redundant second event.
Alternatively, engineers utilize AtomicBoolean.compareAndSet(false, true) for lock-free state synchronization.
At the network layer, integrating RFC-7231 or IETF draft Idempotency-Key headers in HTTP requests ensures distributed transaction safety across cloud microservices.
If network timeouts cause OkHttp to retry or if the user forces a resubmission, the backend caches the idempotency token in Redis, returning the original response without executing duplicate database inserts or processing duplicate financial debits.""",
    "meta_ar": {
        "id": "COM-25",
        "questionAr": "المستخدم ضغط على زر حفظ مرتين وراء بعض والطلب شغال. كيف تجعل سلوك الواجهة وطبقة الـ Domain آمناً؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على تأمين التطبيق ضد النقرات المزدوجة (Double-taps)، وفهم الفرق بين حماية الواجهة وحماية الـ ViewModel، واستخدام تقنيات التزامن (Mutex و Job.isActive) ومفاتيح الـ Idempotency.",
        "why_it_matters_ar": "الضغط المزدوج قد يسبب خصم الأموال مرتين في تطبيقات الدفع أو تكرار إنشاء الحسابات والطلبات في السيرفر وتلف البيانات.",
        "worked_example_ar": "حماية ثلاثية الطبقات للضغط المزدوج:\n```kotlin\n// 1. في الواجهة: تعطيل الزرار فوراً\nButton(onClick = onSave, enabled = !state.isSubmitting) { ... }\n// 2. في الـ ViewModel: منع التكرار بالكوروتين والـ Mutex ومفتاح الـ UUID\nfun save() {\n    if (job?.isActive == true) return\n    job = viewModelScope.launch {\n        api.save(data, idempotencyKey = UUID.randomUUID().toString())\n    }\n}\n```",
        "trade_offs_ar": "تنفيذ الحماية ثلاثية الطبقات يتطلب تنسيقاً بين الواجهة والـ ViewModel والـ Backend، لكنه الإجراء الأمني القياسي لمنع تكرار المعاملات المالية وتلف البيانات.",
        "failure_modes_ar": "الاعتماد على `enabled = false` في الزرار فقط؛ لأن الشاشات السريعة قد تستقبل لمستين في نفس الفريم قبل أن تلحق كومبوز إتمام الـ Recomposition وتعطيل الزرار.",
        "production_perspective_ar": "في تطبيقات البنوك والتجارة الإلكترونية، نلزم تمرير `Idempotency-Key` في ترويسات HTTP لكل طلبات الدفع والإنشاء، ونمنع إطلاق العمليات المتزامنة في الـ ViewModel.",
        "how_to_answer_ar": "اشرح خطة الدفاع ثلاثية الطبقات: أولاً في الواجهة بتعطيل الزرار بـ `enabled = !isSubmitting` وعرض مؤشر تحميل، ثانياً في الـ ViewModel بفحص `job?.isActive` أو استخدام `Mutex.tryLock()` لإسقاط النقرة الثانية فوراً، وثالثاً في الـ Domain والـ Backend بتوليد `Idempotency Key (UUID)` لضمان عدم تكرار المعاملة في السيرفر.",
        "talking_points_ar": "الثغرة الزمنية بين اللمس والـ Recomposition، وحماية الواجهة بـ enabled، وحماية الـ ViewModel بـ Mutex و AtomicBoolean، والـ Idempotency Keys مع الـ Backend.",
        "follow_ups_ar": "- **المحاور:** \"لماذا لا يكفي الاعتماد على تعطيل الزرار بـ `enabled = false` في الواجهة فقط؟\"\n  **المرشح:** \"لأن شاشة اللمس ممكن تلتقط لمستين في كسر من الثانية قبل ما كومبوز ترسم الفريم الجديد وتعطل الزرار، فتتنادى دالة onClick مرتين في نفس الفريم.\"\n\n- **المحاور:** \"كيف يضمن السيرفر عدم تكرار العملية لو وصله نفس الطلب مرتين بسبب ضعف الشبكة؟\"\n  **المرشح:** \"عبر `Idempotency Key` (زي UUID بيتبعت في الـ Headers)؛ السيرفر بيسجل المفتاح في كاش زي Redis، فلو وصله نفس المفتاح تاني بيرجع النتيجة السابقة فوراً بدون تكرار الحفظ في الداتابيز.\"",
        "self_check_ar": "هل شرحت طبقات الحماية الثلاثة؟ هل بينت عيب الاعتماد على الواجهة وحدها؟ وهل ذكرت تقنيات التزامن في ViewModel والـ Idempotency في السيرفر؟",
        "references_ar": f"- [Robust Android UI: Handling Clicks](https://developer.android.com/develop/ui/compose/touch-input/pointer-input) — التوثيق الرسمي للمدخلات واللمس في كومبوز.\n- [IETF Idempotency-Key Specification](https://datatracker.ietf.org/doc/html/draft-ietf-httpapi-idempotency-key-header-02) — مواصفات مفاتيح عدم التكرار العالمية.",
        "quick_answer_ar": "بنامن السلوك ضد الضغط المزدوج (Double-tap) بخطة دفاع ثلاثية الطبقات: أولاً في طبقة الواجهة، بنعطل الزرار فوراً بـ `enabled = !state.isSubmitting` ونعرض مؤشر تحميل لمنع الضغطات الإضافية. ثانياً في الـ ViewModel، بنحمي الدالة بفحص `if (job?.isActive == true) return` أو باستخدام `Mutex.tryLock()` عشان نسقط أي استدعاء متزامن والطلب الأول شغال. ثالثاً في طبقة الـ Domain والشبكة، بنولد مفتاح فريد لعدم التكرار `Idempotency Key` (زي كود UUID) ونمرره مع الطلب للسيرفر، فلو وصل الطلب مرتين لأي سبب، السيرفر بينفذه مرة واحدة فقط وميكررش العملية.",
        "best_answer_ar": "حماية التطبيق من الضغط المزدوج (Double-tap) هي مسألة أمان واستقرار بالغة الأهمية، خصوصاً في شاشات الدفع وحفظ البيانات الحساسة.\n\nالخطة الهندسية المتينة بتعتمد على تلات طبقات:\nالطبقة الأولى: حماية الواجهة التقديمية (UI Layer)؛ الزرار بيستقبل `enabled = !isSubmitting`. أول ما المستخدم يدوس، الحالة بتتغير والزرار بيتعطل ويتعرض بداله مؤشر تحميل `CircularProgressIndicator`.\n\nالطبقة الثانية: صمام أمان الـ ViewModel (Concurrency Guard)؛ دي الخطوة الأهم اللي بتميز المهندس السينيور؛ لأن شاشة اللمس ممكن تلتقط لمستين سريعتين في أجزاء من الميلي ثانية قبل ما كومبوز ترسم الفريم الجديد وتعطل الزرار. بنحمي الدالة في الـ ViewModel بإننا نتأكد إن مفيش Job شغال: `if (saveJob?.isActive == true) return`، أو بنستخدم `Mutex.tryLock()`، فلو فيه عملية شغالة، الاستدعاء التاني بيتم إسقاطه فوراً في لمح البصر.\n\nالطبقة الثالثة: حماية الـ Domain والسيرفر (Idempotency)؛ بنولد مع الطلب رمز فريد `Idempotency Key` كـ UUID ونبعته في ترويسات الـ HTTP. السيرفر بيسجل المفتاح ده في الكاش؛ لو استقبل نفس المفتاح تاني خلال دقيقة، مش هيكرر عملية الخصم أو الحفظ في الداتابيز، بل هيرجع نفس الرد السابق، وده بيقضي على خطر تكرار المعاملات تماماً.",
        "deep_answer_ar": "تحت الكابوت، المشكلة بتنبع من الفارق الزمني (Latency Window) بين معالجة عتاد اللمس (Hardware Digitizer) ورندرة فريمات كومبوز عبر نبضات الـ VSYNC.\nلما المستخدم يضغط مرتين بسرعة، نظام التشغيل بيولد حدثين `MotionEvent` متتاليين. معالج اللمس في كومبوز بيوزع الأحداث دي في الـ Main Thread. لو الضغطتين حصلوا في نفس نافذة الـ 16ms، دالة `onClick` هتتنفذ مرتين قبل ما دورة الـ Recomposition تقدر تعطل الزرار فعلياً على الشاشة! الاعتماد على `enabled = false` لوحده بيسيب ثغرة زمنية خطيرة.\n\nعشان نقفل الثغرة دي في الـ ViewModel، بنستخدم أدوات التزامن الذرية (Atomic Concurrency Primitives) في كوتلن كوروتينز.\nاستخدام `Mutex.tryLock()` هو الحل الأرقى؛ لو القفل محجوز، الدالة بترجع `false` فوراً بدون تعليق (Non-suspending) وبتسقط الطلب التاني بدون استهلاك أي وقت معالجة. أو بنستخدم `AtomicBoolean.compareAndSet(false, true)` لحماية المدخلات بشكل خفيف ومحكم.\n\nوعلى مستوى الشبكة والـ Backend، تطبيق بروتوكول الـ `Idempotency-Key` المعتمد في منظمة IETF بيضمن سلامة المعاملات حتى لو طبقة الـ OkHttp عملت إعادة محاولة تلقائية (Automatic Retries) بسبب ضعف الاتصال؛ السيرفر بيخزن الـ Key في كاش سريع زي Redis، ويتعامل مع الطلبات المكررة بذرية مطلقة تمنع أي تكرار محاسبي أو خصم مالي مزدوج من حساب العميل."
    }
}

# ==========================================
# COM-26: A LazyColumn scroll position resets after data refresh. What should you inspect?
# ==========================================
DATA["COM-26"] = {
    "concept_en": """When a LazyColumn's scroll position unexpectedly resets to index zero after a data refresh, it indicates a violation of list identity or state preservation across composition cycles. The primary culprit is omitting stable keys in the items() block, causing Compose to rely on fluctuating list indices that reset when items are prepended, sorted, or replaced. The second major culprit is re-instantiating the LazyListState by placing rememberLazyListState() inside a conditional composable branch (such as if (isLoading) LoadingView() else LazyColumn()) that disposes of the state holder when loading toggles. Engineers resolve this by providing unique stable keys and hoisting LazyListState above conditional branches.""",
    "walkthrough_en": """Diagnosing and fixing LazyColumn scroll reset regressions:
```kotlin
// ❌ REGRESSION 1: Conditional branch destroys LazyListState on refresh!
// When isRefreshing is true, LazyColumn is unmounted, destroying its remembered scroll state!
@Composable
fun BadRefreshableList(isRefreshing: Boolean, items: List<Item>) {
    if (isRefreshing) {
        LoadingSpinner() // LazyColumn is destroyed! Scroll position is lost forever!
    } else {
        // ❌ REGRESSION 2: Missing stable keys! Index reset happens on new dataset emission!
        LazyColumn {
            items(items) { item -> ItemCard(item) }
        }
    }
}

// ✅ FIXED: Hoist state, provide stable keys, and overlay loading indicators!
@Composable
fun SafeRefreshableList(
    isRefreshing: Boolean,
    items: List<Item>,
    listState: LazyListState = rememberLazyListState() // State preserved across refreshes!
) {
    Box(modifier = Modifier.fillMaxSize()) {
        LazyColumn(state = listState) {
            items(
                items = items,
                key = { it.id }, // STABLE KEY: Preserves exact scroll offset across data updates!
                contentType = { "ITEM_TYPE" }
            ) { item ->
                ItemCard(item)
            }
        }

        // Overlay refresh indicator instead of tearing down the LazyColumn!
        if (isRefreshing) {
            CircularProgressIndicator(modifier = Modifier.align(Alignment.TopCenter))
        }
    }
}
```""",
    "short_en": """To fix scroll position resets after a refresh, inspect two critical areas. First, verify that items() has a unique stable key (key = { it.id }); without stable keys, dataset mutations cause Compose to lose track of items and reset scroll to zero. Second, check if LazyColumn is wrapped in a conditional branch like if (isLoading) which unmounts the list and destroys rememberLazyListState(). We fix this by supplying stable keys, hoisting LazyListState, and overlaying loading spinners instead of destroying the list.""",
    "structured_en": """A LazyColumn scroll position resetting to the top upon refreshing data is one of the most frustrating user experience bugs in Android apps.
When diagnosing this regression, senior engineers systematically inspect two primary architecture failure points.
Failure point one is the absence of unique stable keys inside items().
When the key parameter is omitted, LazyColumn uses the item's integer index as its identity.
If a data refresh prepends a single item or alters the list sorting order, index zero now maps to a completely different item.
Compose cannot correlate old items with new items, discarding internal scroll offset calculations and resetting the viewport to the top.
Providing key = { it.id } binds scroll position directly to the persistent item identity.
Failure point two is state destruction caused by conditional composition branching.
A common anti-pattern is writing: if (state.isLoading) LoadingScreen() else LazyColumn().
When a pull-to-refresh occurs, isLoading flips to true.
Compose unmounts the entire LazyColumn subtree, instantly purging the remembered LazyListState from the SlotTable.
When loading completes, Compose instantiates a brand-new LazyListState initialized to index zero.
To resolve this, engineers keep the LazyColumn mounted continuously—overlaying the progress indicator via a Box—and hoist LazyListState above transient loading states.""",
    "deep_senior_en": """Under the hood, LazyColumn scroll maintenance is mediated by LazyListState and its internal LazyListScrollPosition tracker.
LazyListScrollPosition stores two values: the index of the first visible item and the exact pixel scroll offset.
When a stable key is supplied, LazyListScrollPosition registers a key-to-index mapping inside its internal ItemProvider.
When a data flow emits a new immutable list, the Lazy layout pipeline executes a measure pass.
It queries the ItemProvider for the new index of the previously pinned stable key.
If an item was prepended at index 0, the pinned key's index shifts from 0 to 1, and Compose adjusts the scroll position synchronously by updating the anchor index without jumping.
If keys are omitted, the ItemProvider defaults to position integers; any dataset shift invalidates the anchor, forcing the scroll position to fall back to index 0.
Regarding conditional branching, rememberLazyListState() registers an entry in the local SlotTable.
When an if (isLoading) branch swaps out LazyColumn, the Composer executes an unmount pass, invoking dispose() on the RecomposeScope and releasing the SlotTable interval.
Even if rememberSaveable is used, if the composable leaves the composition entirely without a preserved SaveableStateHolder key, the in-memory state is cleared.
Maintaining the LazyColumn in the composition hierarchy and toggling loading indicators through Box overlays or SwipeRefresh containers preserves the SlotTable intact, securing seamless scroll retention across high-frequency network refreshes.""",
    "meta_ar": {
        "id": "COM-26",
        "questionAr": "موضع التمرير في LazyColumn يرجع للبداية (Resets to top) بعد تحديث البيانات. ماذا يجب أن تفحص؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على تشخيص أسباب فقدان موضع التمرير في القوائم، وفحص المفاتيح المستقرة `key`، وفحص هدم الـ `LazyListState` في الشروط البرمجية (Conditional Composition)، وتطبيق حلول الـ Overlay.",
        "why_it_matters_ar": "رجوع القائمة لأعلى الشاشة بعد كل تحديث يفسد تجربة المستخدم تماماً ويجعله يفقد العنصر الذي كان يقرأه في القوائم الطويلة.",
        "worked_example_ar": "حماية موضع التمرير من الضياع بعد التحديث:\n```kotlin\n// 1. تثبيت المفتاح المستقر\nLazyColumn(state = listState) {\n    items(items, key = { it.id }) { ... }\n}\n// 2. تجنب هدم القائمة في شرط if (loading) بل وضع مؤشر التحميل كـ Overlay\nBox { LazyColumn(...); if (loading) CircularProgressIndicator() }\n```",
        "trade_offs_ar": "توفير المفاتيح المستقرة وإبقاء القائمة في الشجرة يستهلك ذاكرة بسيطة للمحافظة على الـ State، لكنه يضمن بقاء مكان التمرير ثابتاً وسلساً للمستخدم.",
        "failure_modes_ar": "كتابة شرط `if (isLoading) Loader() else LazyColumn()` مما يهدم شجرة القائمة والـ State بتاعتها مع كل Refresh.",
        "production_perspective_ar": "في المشروعات الكبيرة، نمنع إخفاء القوائم أثناء الـ Refresh، ونستخدم مكونات الـ Pull-to-refresh الرسمية مع تثبيت الـ `key` المستمد من الـ Backend ID.",
        "how_to_answer_ar": "افحص نقطتين حاسمتين: أولاً فحص وجود `key = { it.id }` في `items()` لأن غيابه يجعل كومبوز تعتمد على الـ index وتفقد المكان عند دخول عناصر جديدة، ثانياً فحص شروط `if (isLoading)` التي تهدم `LazyColumn` وتفرغ `rememberLazyListState` من الذاكرة، وقدم حل وضع التحميل كـ Overlay فوق القائمة.",
        "talking_points_ar": "دور المفاتيح المستقرة (Stable Keys)، وهدم الـ LazyListState في الشروط البرمجية (Conditional Composition)، ومكون LazyListScrollPosition، وحل الـ Box Overlay لـ Pull to Refresh.",
        "follow_ups_ar": "- **المحاور:** \"لماذا يؤدي شرط `if (isLoading) Loader() else LazyColumn()` إلى تصفير مكان التمرير؟\"\n  **المرشح:** \"لأن أول ما `isLoading` تبقى true، كومبوز بتعمل Dispose لـ `LazyColumn` وتمسح الـ `rememberLazyListState` من الـ SlotTable، ولما التحميل يخلص بتبني قائمة جديدة تماماً بـ State جديدة بادئة من الصفر.\"\n\n- **المحاور:** \"كيف يتعامل LazyListScrollPosition مع إضافة عنصر جديد في أول القائمة لو مستخدمين stable key؟\"\n  **المرشح:** \"بيطابق المفتاح المثبت في الشاشة مع مكانه الجديد في الـ ItemProvider؛ فلو العنصر اتشفت من 0 لـ 1، كومبوز بتعدل رقم الـ Anchor تلقائياً وبتفضل الشاشة ثابتة على نفس العنصر بدون قفز.\"",
        "self_check_ar": "هل حددت النقطتين الحاسمتين (Keys وهدم الشجرة بالشروط)؟ هل شرحت آلية عمل LazyListScrollPosition؟ وهل قدمت الحل الصحيح بـ Overlay؟",
        "references_ar": f"- [Compose Lists: Maintain scroll position](https://developer.android.com/develop/ui/compose/lists#item-keys) — التوثيق الرسمي للحفاظ على مكان التمرير في كومبوز.\n- [Common Jetpack Compose Pitfalls](https://medium.com/androiddevelopers/) — دليل جوجل للأخطاء الشائعة في القوائم.",
        "quick_answer_ar": "لما موضع التمرير في `LazyColumn` يرجع للبداية بعد الـ Refresh، لازم تفحص نقطتين أساسيتين فوراً: أولاً تفحص وجود مفتاح مستقر `key = { it.id }` في دالة `items()`؛ لأن غياب المفتاح بيخلي كومبوز تعتمد على رقم الترتيب (Index)، فلو وصل عنصر جديد أو اتغير الترتيب، القائمة بتفقد مكانها وترجع للصفر. ثانياً تفحص هل القائمة محطوطة داخل شرط تفريعي زي `if (isLoading) LoadingView() else LazyColumn()`؛ لأن الشرط ده بيهدم الـ `LazyColumn` بالكامل من الذاكرة ويمسح كائن `rememberLazyListState`، ولما التحميل يخلص بيعيد بنائها من الصفر. والحل هو وضع المفاتيح وإبقاء القائمة في الشاشة وعرض مؤشر التحميل كـ Overlay فوقها.",
        "best_answer_ar": "تصفير موضع التمرير (Scroll Reset) بعد تحديث البيانات هو واحد من أكثر الأخطاء إزعاجاً للمستخدم في تطبيقات أندرويد، وتصليحه بيعتمد على فحص نقطتين حاسمتين:\n\nالنقطة الأولى: نسيان المفاتيح المستقرة (Missing Stable Keys)؛ لو كاتب `items(users)` بدون تحديد `key = { it.id }`، كومبوز بتستخدم رقم ترتيب العنصر (Index) كهوية له. لما تعمل Refresh وتنزل بيانات جديدة، لو نزل بوست جديد في الأول، كل العناصر بتتشفت، وكومبوز مش بتقدر تطابق العناصر القديمة بالجديدة، فبتفقد الـ Scroll Offset وترجع الشاشة لأول عنصر فوق.\n\nالنقطة الثانية: هدم الـ State في الشروط التفريعية (Conditional Unmounting)؛ دي أكبر غلطة بنشوفها في الكود: المطور يكتب: `if (state.isLoading) CircularProgressIndicator() else LazyColumn()`. الكارثة هنا إن أول ما المستخدم يسحب الشاشة عشان يحدث، `isLoading` بتبقى `true`؛ كومبوز بتقوم بهدم الـ `LazyColumn` فوراً ومسح الـ `rememberLazyListState` من الـ SlotTable! ولما التحميل يخلص، كومبوز بتنشئ `LazyListState` جديدة تماماً بادئة من الصفر.\n\nالحل الهندسي المعتمد:\nأولاً: تمرير `key = { it.id }` مستقر وفريد لكل عنصر.\nثانياً: إبقاء `LazyColumn` عايشة دايماً في الشاشة، ونستخدم `Box` ونحط مؤشر التحميل كـ Overlay فوق القائمة، أو نستخدم مكونات الـ PullRefresh الرسمية، ونرفع الـ `LazyListState` في مكان آمن لضمان ثبات الشاشة بنسبة 100%.",
        "deep_answer_ar": "تحت الكابوت، إدارة موضع التمرير بتتم عبر كائن `LazyListState` ومكون داخلي اسمه `LazyListScrollPosition`.\n\nالمكون ده بيحتفظ بقيمتين: رقم ترتيب أول عنصر ظاهر (Index) والإزاحة الدقيقة بالبكسل (Scroll Offset). لما بتحدد `key` مستقر، المحرك بيسجل خريطة بين المفاتيح والأماكن في الـ `ItemProvider`. أثناء عملية الـ Measure التالية لصدور قائمة البيانات الجديدة، المحرك بيبحث عن المفتاح اللي كان مثبت على الشاشة؛ لو لقى إن مكانه اتغير من 0 إلى 1 بسبب نزول عنصر جديد في البداية، المحرك بيعدل الـ Anchor Index تلقائياً في نفس الفريم، فالمستخدم مبيحسش بأي قفزة وتفضل الشاشة واقفة على نفس المحتوى بالضبط.\n\nأما بخصوص الشروط البرمجية، دالة `rememberLazyListState()` بتسجل حالة في الـ SlotTable داخل النطاق التابع لـ `LazyColumn`. لما تحط شرط `if (isLoading)`، المحرك بينفذ عملية `Dispose` كاملة للشجرة الفرعية، وبيرمي كل كائنات الذاكرة المحجوزة في الـ Slot.\nحتى لو كنت مستخدم `rememberSaveable`، خروج المكون تماماً من الشاشة بيمسح الـ In-memory cache لو مفيش `SaveableStateHolder` بيحميه.\nعشان كده، المحافظة على وجود الـ `LazyColumn` في الشجرة وعرض لودر التحديث كـ Overlay داخل `Box`، مع تحديد نوع المحتوى `contentType` لتحسين إعادة استخدام النودز، بيحافظ على سلامة الـ SlotTable بالكامل، وده بيضمن أعلى درجة من الثبات وسلاسة الاستخدام في تطبيقات الإنتاج."
    }
}

# ==========================================
# COM-27: How do you test a screen with loading, error, success, and permission states?
# ==========================================
DATA["COM-27"] = {
    "concept_en": """Testing a Jetpack Compose screen across loading, error, success, and permission states requires a multi-tiered testing strategy combining JVM component tests, screenshot tests, and ViewModel state verification. By decoupling the architecture into stateless Screen composables and stateful Routes, presentation testing becomes pure and fast. Using Compose UI Test APIs (createComposeRule()), engineers inject static state fixtures into the Screen composable to verify semantic visibility, button enablement, and retry callbacks directly on the JVM with Robolectric or on emulators. Screenshot testing tools like Paparazzi or Roborazzi capture pixel-perfect golden images of all state permutations without mocking Android platform dependencies.""",
    "walkthrough_en": """Testing multi-state UI variants using Compose UI Test rules and semantic assertions:
```kotlin
// Stateless Screen under test
@Composable
fun ProfileScreen(state: ProfileUiState, onRetry: () -> Unit, onRequestPermission: () -> Unit) {
    when (state) {
        is ProfileUiState.Loading -> CircularProgressIndicator(modifier = Modifier.testTag("loading_tag"))
        is ProfileUiState.Error -> Column {
            Text(text = state.message)
            Button(onClick = onRetry) { Text("Retry") }
        }
        is ProfileUiState.PermissionRequired -> Button(onClick = onRequestPermission) { Text("Grant Access") }
        is ProfileUiState.Success -> Text(text = "Welcome, ${state.user.name}")
    }
}

// JVM / Instrumented Compose UI Test
class ProfileScreenTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun errorState_showsMessage_andTriggersRetryCallback() {
        var retryClicked = false

        // Inject Error State Fixture
        composeTestRule.setContent {
            ProfileScreen(
                state = ProfileUiState.Error("Network Timeout"),
                onRetry = { retryClicked = true },
                onRequestPermission = {}
            )
        }

        // Verify Semantics and Interactions
        composeTestRule.onNodeWithText("Network Timeout").assertIsDisplayed()
        composeTestRule.onNodeWithText("Retry").assertIsDisplayed().performClick()

        assertTrue(retryClicked)
    }

    @Test
    fun loadingState_showsProgressIndicator() {
        composeTestRule.setContent {
            ProfileScreen(state = ProfileUiState.Loading, onRetry = {}, onRequestPermission = {})
        }
        composeTestRule.onNodeWithTag("loading_tag").assertIsDisplayed()
    }
}
```""",
    "short_en": """We test multi-state Compose screens by decoupling them into stateless Screen composables and verifying each state variant independently. Using createComposeRule(), we inject static UI state fixtures (Loading, Error, Success, Permission) into the screen, asserting that correct texts, loaders, and buttons appear and that callbacks fire when clicked. We also run screenshot tests using Paparazzi or Roborazzi to verify visual fidelity across all states on the JVM without needing emulators.""",
    "structured_en": """Thoroughly verifying complex UI states—Loading, Error, Success, and Permission Required—is made exceptionally fast and deterministic through Jetpack Compose's declarative model.
In traditional XML testing, validating multi-state screens required complex Espresso orchestration, mocking network endpoints, and waiting for asynchronous ViewModels.
In Compose, our architecture cleanly separates the stateful Route from the stateless Screen presenter.
This separation transforms UI testing into pure state projection verification.
Using the official Compose Test API via createComposeRule(), we author isolated UI component tests.
For the Loading state, we inject the loading fixture and assert that the progress indicator node is displayed using onNodeWithTag().
For the Error state, we inject an error model, assert that the error description renders, and simulate a user click on the Retry button to verify that the retry callback lambda fires with the correct payload.
For the Permission state, we verify that the educational rationale and grant button render appropriately.
Finally, we complement semantic tests with JVM screenshot tests using tools like Paparazzi or Roborazzi.
Screenshot tests render all four state variants across phone and tablet configurations in seconds, establishing baseline golden images that catch accidental visual regressions in CI.""",
    "deep_senior_en": """Under the hood, Compose UI testing operates by querying the Semantics Tree rather than traversing the physical LayoutNode or Android View hierarchies.
When createComposeRule().setContent {} executes, the test runner builds a headless Composition hierarchy.
Assertion methods like onNodeWithText() and onNodeWithTag() execute search algorithms across the SemanticsNode tree matching SemanticsPropertyKey entries (such as Text, TestTag, and Role).
Because testing targets the stateless Screen composable directly, tests run synchronously on the JVM using Robolectric or headless desktop runners without launching Android Activity lifecycles, Hilt dependency injection graphs, or MockWebServer instances.
Furthermore, Compose UI tests integrate automatic synchronization via IdlingResource mechanics.
The ComposeTestRule automatically waits for the Compose runtime to settle—ensuring all pending recompositions, layout passes, draw steps, and coroutine effect blocks within the composition scope finish before assertions execute.
If testing requires verifying intermediate animations or infinite progress bars, developers control the virtual clock using mainClock.autoAdvance = false and advanceTimeBy() to take deterministic snapshots.
For testing the stateful Route and ViewModel layers, engineers author complementary Unit tests using Turbine.
Turbine collects the ViewModel's uiState StateFlow, asserting that user action events transition the state sequentially: from Loading, to Error, and finally to Success.
This layered testing pyramid provides 100% test coverage with sub-second execution speeds in automated CI pipelines.""",
    "meta_ar": {
        "id": "COM-27",
        "questionAr": "كيف تختبر شاشة في Compose تحتوي على حالات: التحميل والخطأ والنجاح وطلب الإذن؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على وضع استراتيجية اختبار متكاملة لشاشات كومبوز، واستخدام `createComposeRule()` لاختبار الشاشات النقية، وفحص شجرة الـ Semantics، وتطبيق اختبارات الـ Screenshot بـ Roborazzi، واختبار الـ ViewModel بـ Turbine.",
        "why_it_matters_ar": "الاعتماد على الاختبار اليدوي أو اختبارات المحاكي البطيئة يهدر ساعات في التطوير، بينما الاختبار النظيف على الـ JVM يكتشف الأخطاء في أجزاء من الثانية ويضمن استقرار كل الحالات في الـ CI.",
        "worked_example_ar": "اختبار حالات الشاشة بـ ComposeTestRule:\n```kotlin\n@Test fun testErrorState() {\n    var retried = false\n    composeRule.setContent {\n        Screen(state = UiState.Error(\"Failed\"), onRetry = { retried = true })\n    }\n    composeRule.onNodeWithText(\"Failed\").assertIsDisplayed()\n    composeRule.onNodeWithText(\"Retry\").performClick()\n    assertTrue(retried)\n}\n```",
        "trade_offs_ar": "كتابة اختبارات لكل حالة يتطلب وقتاً إضافياً في البداية، لكنه يوفر حماية كاملة ضد تكرار الأخطاء (Regressions) ويسمح بإجراء refactoring بثقة تامة.",
        "failure_modes_ar": "محاولة اختبار الشاشة وهي مربوطة بالـ ViewModel ومكتبات الشبكة مباشرة، مما يجعل الاختبار بطيئاً جداً وغير مستقر (Flaky).",
        "production_perspective_ar": "في المشروعات الكبيرة، نعتمد هرم اختبار متكامل: Unit Tests للـ ViewModel بـ Turbine، واختبارات مكونات الشاشة بـ ComposeRule، واختبارات بصرية بـ Roborazzi في الـ CI.",
        "how_to_answer_ar": "قسم الاختبار لثلاث طبقات: أولاً اختبار الشاشة التقديمية النقية (Stateless Screen) بحقن كائنات State ثابتة لكل حالة (Loading, Error, Success, Permission) واستخدام `createComposeRule` لفحص النصوص والكولباكات، ثانياً اختبار الـ ViewModel بـ Turbine، وثالثاً اختبارات الـ Screenshot بـ Roborazzi لتوثيق شكل كل الحالات بدون محاكي.",
        "talking_points_ar": "فصل الـ Screen عن الـ Route، واختبار شجرة الـ Semantics بـ onNodeWithText، والتزامن التلقائي بـ ComposeTestRule، واختبارات الـ Screenshot بـ Roborazzi و Paparazzi، واختبار الـ StateFlow بـ Turbine.",
        "follow_ups_ar": "- **المحاور:** \"كيف تضمن ComposeTestRule أن الرندرة اكتملت قبل فحص العناصر في الاختبار؟\"\n  **المرشح:** \"كومبوز بتوفر نظام مزامنة آلي مدمج؛ الـ Rule بتعلق تنفيذ الاختبار لحد ما كل عمليات الـ Recomposition والـ Layout والأنيميشن تخلص تماماً وتستقر الشاشة.\"\n\n- **المحاور:** \"ما هي فائدة اختبارات الـ Screenshot بـ Roborazzi مقارنة باختبارات الـ Semantics؟\"\n  **المرشح:** \"اختبارات الـ Semantics بتتأكد إن النص موجود في الشجرة، لكن مش بتضمن إنه مش متغطي بعنصر تاني أو لونه مش مقروء؛ الـ Screenshot بيتأكد من المظهر البصري الفعلي في ثوانٍ على الـ JVM.\"",
        "self_check_ar": "هل شرحت اختبار الحالات الأربعة بوضوح؟ هل بينت استخدام createComposeRule و Semantics؟ وهل ذكرت اختبارات الـ Screenshot والـ ViewModel؟",
        "references_ar": f"- [Testing in Jetpack Compose](https://developer.android.com/develop/ui/compose/testing) — الدليل الرسمي لجوجل لاختبار شاشات كومبوز.\n- [Compose UI Test Semantics](https://developer.android.com/develop/ui/compose/testing#semantics) — توثيق فحص شجرة المعاني في الاختبارات.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "بنختبر الشاشة متعددة الحالات باتباع معمارية اختبار سريعة ومحكمة من تلات طبقات: أولاً بنختبر شاشة الـ Screen النقية (Stateless) باستخدام أداة `createComposeRule()`؛ بنمرر كائن حالة ثابت لكل سيناريو (التحميل، والخطأ، والنجاح، والإذن)، ونتأكد بـ `onNodeWithText` أو `assertIsDisplayed` إن النصوص واللودر ظاهرين، وبنعمل `performClick` عشان نختبر إن كولباك إعادة المحاولة اشتغل. ثانياً بنعمل اختبارات بصرية (Screenshot Testing) بـ Roborazzi أو Paparazzi عشان نلتقط صوراً لكل الحالات على الـ JVM في ثوانٍ. ثالثاً بنختبر منطق الـ ViewModel وتدفق الحالات باستخدام مكتبة Turbine للتأكد من إنتاج الحالات بالترتيب السليم.",
        "best_answer_ar": "اختبار الشاشات المعقدة في Jetpack Compose أصبح أسرع وأسهل بكثير من نظام XML القديم بفضل المعمارية التصريحية وفصل الشاشات إلى Route و Screen.\n\nالاستراتيجية الاحترافية بتعتمد على تلات مراحل:\nالمرحلة الأولى: اختبار الواجهة النقية (Component Testing)؛ لأن دالة الـ Screen مفصولة تماماً عن الـ ViewModel، بنقدر نختبرها في بيئة معزولة على الـ JVM باستخدام `createComposeRule()` مع Robolectric. بنعمل Test Case لكل حالة:\nفي حالة الـ Loading: بنمرر `ProfileUiState.Loading` ونتأكد إن مؤشر التحميل ظاهر.\nفي حالة الـ Error: بنمرر `ProfileUiState.Error` ونتأكد إن رسالة الخطأ معروضة، وبنضغط على زرار 'إعادة المحاولة' بـ `performClick()` ونتأكد إن الـ Lambda اتنادت.\nوفي حالة الـ Permission: بنمرر حالة طلب الإذن ونتأكد إن زرار منح الصلاحية ظاهر وشغال.\n\nالمرحلة الثانية: الاختبارات البصرية (Screenshot Testing)؛ بنستخدم مكتبات زي Roborazzi أو Paparazzi؛ بتولد صور PNG حقيقية لكل حالة في ثوانٍ معدودة وبدون الحاجة لتشغيل محاكي، وبنحطها في الـ CI كـ Baseline تكشف أي تشوه بصري غير مقصود.\n\nالمرحلة الثالثة: اختبار الـ ViewModel؛ بنختبر منطق إنتاج الحالات باستخدام مكتبة `Turbine`؛ بنتأكد إن أول ما الدالة تبدأ بتصدر حالة Loading، ولما السيرفر يرجع داتا بتتحول لـ Success، وبكده بنضمن تغطية الشاشة بنسبة 100%.",
        "deep_answer_ar": "تحت الكابوت، اختبارات كومبوز المعتمدة على `createComposeRule()` مش بتبحث في شجرة كائنات الـ Views التقليدية ولا في شجرة الـ LayoutNode، بل بتبحث حصرياً في شجرة المعاني (Semantics Tree).\n\nدوال الفحص زي `onNodeWithText()` و `onNodeWithTag()` بتعمل مسح سريع للـ `SemanticsNode` وتطابق الخصائص المسجلة في الـ SlotTable. الأداء فائق السرعة لأن الاختبار بيشتغل مباشرة على الـ JVM بدون الحاجة لبناء Hilt Graph كامل أو عمل Mock لمكتبات الشبكة والـ Retrofit.\n\nوفوق كده، أداة `ComposeTestRule` بتحتوي على آلية مزامنة ذاتية عبقرية (Built-in Auto-synchronization).\nقبل ما الاختبار ينفذ أي Assertion، الرنتايم بيوقف التنفيذ تلقائياً لحد ما كل عمليات الـ Recomposition المعلقة، ومراحل القياس والرسم، وأي كود Coroutine شغال داخل الـ Composition Context يخلص تماماً وتستقر الشاشة، وده بيقضي تماماً على ظاهرة الـ Flaky Tests الشائعة في Espresso. ولو عندك أنيميشن لا نهائي، بتقدر تتحكم في ساعة الاختبار بـ `mainClock.autoAdvance = false` وتقدم الوقت يدوياً لالتقاط الحالة الدقيقة.\n\nولما ندمج ده مع اختبارات الـ Screenshot بـ Roborazzi، بنقدر نتحقق من صحة الرندرة لـ 4 حالات عبر شاشات الهاتف والتابلت والوضع المظلم في أقل من 5 ثوانٍ، وده بيحقق أعلى معايير الجودة في خطوط الـ CI/CD للشركات الكبرى."
    }
}

# ==========================================
# COM-28: When should you avoid derivedStateOf because its overhead exceeds the benefit?
# ==========================================
DATA["COM-28"] = {
    "concept_en": """While derivedStateOf is a vital optimization tool in Jetpack Compose, it introduces measurable memory and computation overhead that can degrade performance if misused. derivedStateOf should be strictly avoided when the calculated output state mutates at the exact same or higher frequency as the input state, such as performing simple string concatenations or basic uppercase transformations. In these scenarios, derivedStateOf cannot filter out any recompositions, but still incurs the continuous penalty of allocating DerivedSnapshotState objects, maintaining dependency read observers, and performing change comparisons. It should also be avoided when calculating values derived from plain Kotlin variables that are not Compose Snapshot States.""",
    "walkthrough_en": """Contrasting wasteful vs beneficial uses of derivedStateOf:
```kotlin
// ❌ ANTI-PATTERN: Wasteful derivedStateOf! Output changes on EVERY input change!
// When 'query' updates, 'uppercaseQuery' updates simultaneously! Zero recomposition filtering!
// Incurs allocation overhead of DerivedSnapshotState and read tracking for NO benefit!
@Composable
fun BadSearchInput(query: String) {
    // ❌ WRONG: Plain calculation is cheaper than derivedStateOf!
    val uppercaseQuery = remember {
        derivedStateOf { query.uppercase() }
    }
    // ✅ BETTER: Just compute directly or use simple remember(query)!
    // val uppercaseQuery = remember(query) { query.uppercase() }
    Text("Search: ${uppercaseQuery.value}")
}

// ✅ ARCHITECTURAL BEST PRACTICE: High-frequency input -> Low-frequency output!
// Input (scrollOffset) changes hundreds of times per second (every pixel)!
// Output (showScrollToTop) changes ONLY TWICE (false -> true or true -> false)!
// Saves thousands of recomposition passes during scrolling!
@Composable
fun OptimizedScrollToTopButton(listState: LazyListState) {
    val showButton by remember {
        derivedStateOf { listState.firstVisibleItemIndex > 5 }
    }

    if (showButton) {
        FloatingActionButton(onClick = { /* scroll to top */ }) { Icon(Icons.Default.KeyboardArrowUp, "Top") }
    }
}
```""",
    "short_en": """Avoid derivedStateOf when the output changes at the same frequency as the input, such as converting text to uppercase or simple formatting. In these cases, derivedStateOf cannot filter out any recompositions, but still adds the overhead of allocating snapshot state objects and tracking dependency reads. Only use derivedStateOf when the input updates significantly more frequently than the output, like checking a scroll threshold where pixels change constantly but the boolean output changes rarely.""",
    "structured_en": """Understanding when NOT to use derivedStateOf separates junior Compose developers from seasoned performance engineers.
The purpose of derivedStateOf is to act as a recomposition filter: it prevents observers from recomposing when high-frequency input mutations do not alter the final calculated output.
Consequently, applying derivedStateOf is counterproductive in two primary scenarios.
First, avoid derivedStateOf when the derived result mutates at the exact same frequency as the input state.
A classic anti-pattern is writing: derivedStateOf { firstName + " " + lastName } or derivedStateOf { text.uppercase() }.
Every time the input changes, the derived string changes as well.
Because the output changes on every single step, derivedStateOf skips zero recompositions.
However, it still incurs the penalty of allocating a DerivedSnapshotState heap object, registering snapshot read observers, and executing equality comparisons on every frame.
In this case, a plain inline expression or simple remember(key) is vastly faster and consumes less memory.
Second, avoid derivedStateOf when inputs are not Compose Snapshot States.
If the dependencies inside the lambda are standard Kotlin variables or immutable parameters, derivedStateOf cannot observe them, leading to stale or broken UI states.""",
    "deep_senior_en": """Under the hood, derivedStateOf instantiates an internal DerivedSnapshotState<T> object, which is significantly more complex and resource-intensive than a standard MutableState primitive.
When a derivedStateOf calculation executes, Compose initializes a calculation scope and attaches an active Snapshot.readObserver.
This observer intercepts every SnapshotMutableState read within the lambda block, constructing a dynamic dependency array stored in the SlotTable.
On every subsequent frame where any state commits in the global Snapshot system, the Compose runtime must traverse these registered dependency arrays to determine if any tracked inputs were modified.
If inputs changed, it executes the calculation lambda, retrieves the new result, and performs an equals() structural equality check against the cached value.
If the output changed, it invalidates downstream RecomposeScopes.
If you apply this machinery to a 1:1 mapping (where input change always produces output change), you force the CPU to perform all this dependency recording, array traversal, and equality diffing without gaining any skipping benefits.
By contrast, a simple remember(key1, key2) { calculation } uses standard compiler bitmask checks: if the keys equal their previous SlotTable slot values, it returns the cached instance in O(1) time with zero read-observer overhead.
Senior engineers reserve derivedStateOf strictly for N:1 reduction scenarios, such as mapping continuous pixel scroll offsets to boolean visibility toggles.""",
    "meta_ar": {
        "id": "COM-28",
        "questionAr": "متى يجب تجنب استخدام derivedStateOf لأن العبء الحسابي (Overhead) يفوق فائدتها في Compose؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "الفهم المعماري الدقيق لـ `derivedStateOf`، وإدراك متى تكون مفيدة (N:1 reduction) ومتى تكون مضرة، ومعرفة التكلفة الحسابية لكائن `DerivedSnapshotState` ومراقبة الـ Read Observers.",
        "why_it_matters_ar": "الاستخدام العشوائي لـ `derivedStateOf` في العمليات البسيطة يثقل الذاكرة بحجز كائنات ومراقبين في كل فريم دون توفير أي عمليات Recomposition، مما يضر بالأداء بدلاً من تحسينه.",
        "worked_example_ar": "الفرق بين الاستخدام الضار والاستخدام المفيد:\n```kotlin\n// ❌ استهلاك ضار: المخرج يتغير مع كل تغير للمدخل (1:1) -> استخدم remember(text) فقط!\nval upper = remember { derivedStateOf { text.uppercase() } }\n// ✅ استهلاك عبقري: المدخل يتغير مئات المرات (بكسلات) والمخرج يتغير مرتين فقط (Boolean)!\nval showButton by remember { derivedStateOf { listState.firstVisibleItemIndex > 5 } }\n```",
        "trade_offs_ar": "استخدام `derivedStateOf` ممتاز فقط عندما يكون معدل تغير المدخلات أكبر بكثير من معدل تغير المخرجات؛ أما في التغير المتطابق فإن الحساب المباشر أو `remember(keys)` أسرع وأخف بكثير.",
        "failure_modes_ar": "استخدام `derivedStateOf` لعمليات دمج نصوص بسيطة أو استخدامه مع متغيرات كوتلن عادية ليست من نوع Snapshot State.",
        "production_perspective_ar": "في المشروعات الكبيرة، نراجع استخدام `derivedStateOf` بدقة؛ نمنع استخدامه لعمليات الـ 1:1 ونقصره على مراقبة التمرير والأنيميشن وحالات الـ Thresholds.",
        "how_to_answer_ar": "وضح القاعدة الذهبية: `derivedStateOf` وظيفته فلترة الرندرة (N to 1 reduction)؛ لذا تجنبه تماماً في حالتين: أولاً عندما يتغير المخرج بنفس معدل تغير المدخل (زي تحويل النص لـ uppercase) لأنه لا يوفر أي رندرة ويضيف تكلفة حجز كائنات ومراقبين، وثانياً عندما لا تكون المدخلات كائنات Snapshot State، واشرح أن `remember(key)` العادي أسرع وأخف بكثير في هذه الحالات.",
        "talking_points_ar": "قاعدة N to 1 reduction، والعبء الحسابي لـ DerivedSnapshotState و Read Observers، والفرق بين remember(keys) و derivedStateOf، وحالات الـ Thresholds مقابل الحسابات البسيطة.",
        "follow_ups_ar": "- **المحاور:** \"ما هو البديل الأفضل لـ derivedStateOf عندما نريد حساب ناتج يتغير مع تغير المدخلات دائماً؟\"\n  **المرشح:** \"البديل الأفضل هو `remember(key1, key2)` العادي أو حسابه مباشرة كـ inline expression؛ لأنه بيفحص المساواة في خطوة واحدة O(1) وبدون حجز مراقبي Snapshots في الذاكرة.\"\n\n- **المحاور:** \"ماذا يحدث لو استخدمت derivedStateOf مع متغيرات Kotlin عادية ليست MutableState؟\"\n  **المرشح:** \"المحرك مش هيقدر يرصد تغير المتغيرات العادية لأنها مش مدعومة بنظام الـ Snapshots، فالقيمة المحسوبة مش هتتحدث أبداً وهتفضل محبوسة في القيمة القديمة.\"",
        "self_check_ar": "هل شرحت متى يكون derivedStateOf ضاراً؟ هل بينت قاعدة N to 1؟ وهل قارنتها مع remember(keys) العادي؟",
        "references_ar": f"- [Compose Performance: derivedStateOf](https://developer.android.com/develop/ui/compose/performance/derived-state) — التوثيق الرسمي لجوجل لاستخدام derivedStateOf بحكمة.\n- [Jetpack Compose Mental Model: derivedStateOf vs remember](https://medium.com/androiddevelopers/) — مقال مطوري أندرويد المعماري.",
        "quick_answer_ar": "يجب تجنب `derivedStateOf` تماماً لما يكون الناتج المحسوب بيتغير بنفس وتيرة تغير المدخلات (علاقة 1:1)؛ زي دمج اسمين أو تحويل نص لحروف كبيرة. في الحالة دي، `derivedStateOf` مش هتوفر أي عمليات إعادة رندرة إطلاقاً، لكنها هتضيف تكلفة باهظة في الذاكرة لحجز كائن `DerivedSnapshotState` ومراقبة قراءات الـ Snapshots في كل فريم. القاعدة الذهبية إنك تستخدمها فقط لما تكون المدخلات بتتغير بسرعة جنونية بينما المخرج بيتغير نادراً (علاقة N:1) زي مراقبة بكسلات التمرير لتحويل boolean. وفي غير ذلك، استخدام `remember(keys)` العادي أسرع وأخف بكثير.",
        "best_answer_ar": "معرفة متى تمتنع عن استخدام `derivedStateOf` هي واحدة من أدق علامات النضج الهندسي في Jetpack Compose.\n\nالهدف الأساسي من `derivedStateOf` هو إنه يشتغل كـ 'فلتر رندرة'؛ يعني لما المدخلات تتغير 100 مرة في الثانية، هو يمنع الشاشة من إعادة الرندرة إلا لو الناتج النهائي اتغير فعلاً (علاقة N:1).\n\nبناءً على ده، لازم نتجنب استخدامها في سيناريوهين قاتلين للأداء:\nالسيناريو الأول: لما يكون التغير 1:1؛ يعني كل ما المدخل يتغير، المخرج بيتغير معاه بالضرورة. مثلاً لو كتبت: `derivedStateOf { text.uppercase() }`؛ كل ما المستخدم يكتب حرف، المدخل بيتغير والناتج بيتغير معاه! هنا `derivedStateOf` موفرتش أي رندرة إطلاقاً، لكنها حملت الجهاز تكلفة حجز كائن معقد في الذاكرة وتسجيل مراقبين بيفحصوا التغيير في كل فريم. الحل هنا هو استخدام `remember(text)` العادي أو حسابها مباشرة.\n\nالسيناريو الثاني: لما تكون المتغيرات اللي جوه البلوك مش من نوع `SnapshotState`؛ يعني متغيرات كوتلن عادية. كومبوز مش هتعرف ترصد تغيرها، وبالتالي المعادلة مش هتتحسب تاني والواجهة هتعرض داتا قديمة.\n\nلذلك في كود الإنتاج، بنحصر استخدام `derivedStateOf` حصرياً في حالات الـ Thresholds وحسابات التمرير وقوائم الـ LazyLayouts.",
        "deep_answer_ar": "تحت الكابوت، كائن `derivedStateOf` مش مجرد متغير عادي، بل هو كلاس معقد اسمه `DerivedSnapshotState<T>`.\n\nأول ما الدالة دي بتتنفذ، رنتايم كومبوز بينشئ بيئة حسابية خاصة وبيفعل مراقب قراءة نشط اسمه `Snapshot.readObserver`. المراقب ده بيلتقط كل قراءة لمتغيرات الـ `SnapshotState` داخل البلوك، ويبني مصفوفة تبعيات (Dependency Array) ديناميكية بيتم تخزينها في الـ `SlotTable`.\nمع كل فريم تالي يحصل فيه Commit لأي Snapshot في التطبيق، الرنتايم بيضطر يمر على كل مصفوفات التبعيات دي، ويفحص هل المدخلات اتغيرت؟ ولو اتغيرت ينفذ المعادلة من جديد، وبعدين يعمل فحص مساواة `equals()` بين القيمة الجديدة والقديمة عشان يقرر هل ينبه الـ RecomposeScopes ولا لأ!\n\nلو طبقت الميكانيزم التقيل ده على عملية تحويل نص بسيطة (1:1)، أنت بتجبر المعالج على تسجيل التبعيات ومسح المصفوفات وعمل مقارنات مستمرة في كل فريم بدون ما تكسب أي توفير في الرندرة.\nبينما دالة `remember(key1, key2)` العادية بتعتمد في البايت كود على فحص سريع جداً O(1) لأعلام الـ `changed bitmask`؛ لو المفاتيح متطابقة بترجع القيمة المتكيشة فوراً بصفر مراقبين وبدون حجز كائنات زائدة في الـ Heap.\nعشان كده، مهندس الأندرويد السينيور بيلتزم بقاعدة: استخدم `derivedStateOf` فقط لتقليص النطاق من تكرار عالي جداً إلى مخرج قليل التغير (N to 1 reduction)."
    }
}

def main():
    print("Elevating 9 questions in COM (COM-20 to COM-28)...")
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

    ee.save_topic_metadata("com_20_28", topic_meta)
    ee.merge_all_metadata()

    # Validate each question
    for qid in sorted(DATA.keys()):
        if DATA[qid] is None:
            continue
        ee.validate_question(qid)

    print("\nAll 9 COM questions (COM-20 to COM-28) successfully elevated and passed validation!")

if __name__ == "__main__":
    main()
