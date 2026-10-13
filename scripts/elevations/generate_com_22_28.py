#!/usr/bin/env python3
"""Generator for COM-22 through COM-28 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "com.json"

COM_22_28 = [
    {
        "id": "COM-22",
        "arabic_explanation": (
            "كيفية دعم إمكانية الوصول (Accessibility)، وقارئات الشاشة (TalkBack)، والتصميمات المتكيفة (Adaptive Layouts) في Jetpack Compose:\n\n"
            "1. دعم قارئات الشاشة (TalkBack) وشجرة الدلالات (Semantics Tree):\n"
            "   - في Compose، يتم تمثيل واجهة المستخدم بشجرتين: شجرة الـ Layout وشجرة الـ **Semantics Tree** التي تقرأها خدمات إمكانية الوصول.\n"
            "   - **ContentDescription**: إضافة وصف نصي واضح للأيقونات والصور غير التزيينية، ووضع `contentDescription = null` للأيقونات التزيينية فقط لتجاهلها.\n"
            "   - **دمج الدلالات (Merge Descendants)**: عند وجود بطاقة تحتوي على عنوان وسعر وحالة، يجب استخدام `Modifier.semantics(mergeDescendants = true)` حتى يقرأ TalkBack البطاقة كوحدة واحدة متماسكة بضغطة واحدة بدلاً من إجبار المستخدم على النقر 4 مرات!\n"
            "   - **Touch Targets**: الالتزام بالحد الأدنى لمساحة اللمس وهو **48dp × 48dp** لتسهيل النقر لذوي الاحتياجات الخاصة.\n\n"
            "2. التصميمات المتكيفة (Adaptive Layouts) للشاشات الكبيرة والقابلة للطي:\n"
            "   - استخدام **Window Size Classes** المعتمدة من Google (`Compact`, `Medium`, `Expanded`):\n"
            "     * **Compact (الهواتف العادية)**: واجهة بعمود واحد (Single Pane).\n"
            "     * **Medium / Expanded (الأجهزة اللوحية والقابلة للطي Foldables)**: واجهة متكيفة ذات لوحين (List-Detail Pane Scaffold).\n"
            "   - تجنب فحص أبعاد البكسل الثابتة، واستخدام مكونات Material 3 Adaptive مثل `SupportingPaneScaffold` و `NavigationSuiteScaffold`."
        ),
        "practical_walkthrough": (
            "تطبيق دمج الدلالات في TalkBack ودعم الـ Window Size Classes المتكيفة:\n"
            "```kotlin\n"
            "// 1. دمج دلالات بطاقة المنتج لقارئات الشاشة TalkBack:\n"
            "@Composable\n"
            "fun AccessibleProductCard(product: Product, onCardClick: () -> Unit) {\n"
            "    Card(\n"
            "        onClick = onCardClick,\n"
            "        modifier = Modifier\n"
            "            .fillMaxWidth()\n"
            "            // دمج العناصر الداخلية ليقرأها TalkBack جملة واحدة متسلسلة:\n"
            "            .semantics(mergeDescendants = true) {\n"
            "                contentDescription = \"Product ${product.name}, Price: ${product.price} dollars\"\n"
            "            }\n"
            "    ) {\n"
            "        Column(modifier = Modifier.padding(16.dp)) {\n"
            "            Text(product.name, style = MaterialTheme.typography.titleMedium)\n"
            "            Text(\"$${product.price}\", style = MaterialTheme.typography.bodyMedium)\n"
            "        }\n"
            "    }\n"
            "}\n"
            "\n"
            "// 2. تكييف الواجهة حسب فئة حجم الشاشة (WindowWidthSizeClass):\n"
            "@Composable\n"
            "fun AdaptiveHomeScreen(windowSizeClass: WindowWidthSizeClass) {\n"
            "    when (windowSizeClass) {\n"
            "        WindowWidthSizeClass.Compact -> SinglePaneFeed() // الهواتف العادية\n"
            "        WindowWidthSizeClass.Medium, WindowWidthSizeClass.Expanded -> TwoPaneFeedWithDetail() // التابلت والـ Foldables\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Support accessibility by populating the Semantics tree with meaningful `contentDescription`s, merging compound components with `Modifier.semantics(mergeDescendants = true)`, and ensuring minimum 48dp touch targets. Support adaptive layouts using Window Size Classes (Compact, Medium, Expanded) and Jetpack Compose Material 3 Adaptive components like List-Detail panes.",
        "best_answer": (
            "Building accessible and adaptive applications in Jetpack Compose is a core engineering requirement for global-scale products.\n\n"
            "1. **Accessibility & Semantics**:\n"
            "   - Alongside the Layout Tree, Compose generates a parallel **Semantics Tree** consumed by Android Accessibility Services (TalkBack, Switch Access).\n"
            "   - Every interactive element must supply meaningful semantics. Purely decorative icons must explicitly set `contentDescription = null` to prevent screen reader noise.\n"
            "   - For compound widgets (like a shopping cart item with title, image, and price), we apply `Modifier.semantics(mergeDescendants = true)`. This groups children into a single accessibility focus node, reading them as a coherent sentence rather than forcing frustrating sequential focus jumps.\n"
            "   - We enforce a minimum **48dp × 48dp touch target** using `Modifier.minimumInteractiveComponentSize()`.\n\n"
            "2. **Adaptive Layouts**:\n"
            "   - Rather than checking device models or orientation booleans, we categorize display width into canonical **Window Size Classes** (`Compact < 600dp`, `Medium 600-840dp`, `Expanded > 840dp`).\n"
            "   - On `Compact` screens, we show standard single-pane flows. On `Medium`/`Expanded` (foldables, tablets, Chromebooks), we render multi-pane layouts using Material 3 Adaptive components like `ListDetailPaneScaffold` and `NavigationSuiteScaffold`."
        ),
        "deep_answer": (
            "Under the hood, TalkBack navigates nodes using Android's `AccessibilityNodeInfo`. "
            "In Compose, custom actions can be exposed directly to TalkBack via `customActions`: `semantics { customActions = listOf(CustomAccessibilityAction(\"Delete item\") { ... }) }`. "
            "This empowers users relying on screen readers to trigger secondary actions without hunting for small swipe gestures or nested overflow menus.\n\n"
            "For adaptive design, foldable devices present dynamic hinge postures. "
            "Using Jetpack **WindowManager** and Compose's `FoldingFeature`, we detect tabletop and book postures, adjusting spacing so content isn't split awkwardly across a physical screen crease.\n\n"
            "We automate accessibility verification in CI using Compose UI tests with `assertHasClickAction()`, `assertContentDescriptionEquals()`, and Android Studio's Accessibility Scanner, establishing strict zero-regression gates."
        ),
        "follow_ups": [
            {
                "question": "What does `mergeDescendants = true` do in Compose semantics?",
                "answer": "It instructs accessibility services like TalkBack to treat the composable and all its child elements as a single unified semantic node, reading its contents together and combining click targets."
            },
            {
                "question": "Why should touch targets never be smaller than 48dp x 48dp?",
                "answer": "Android accessibility guidelines require a minimum 48dp physical target size to accommodate users with motor impairments or vision difficulties and prevent accidental taps."
            }
        ]
    },
    {
        "id": "COM-23",
        "arabic_explanation": (
            "تشخيص وإصلاح مشكلة إعادة تركيب الشاشة بالكامل (Excessive Recomposition) بعد كل ضغطة مفتاح في حقل الإدخال النصي:\n\n"
            "1. كيف تحدث هذه المشكلة الكارثية؟\n"
            "   - المستخدم يكتب حرفاً في `TextField`.\n"
            "   - يتم استدعاء `onQueryChange(newText)` ويقوم الـ ViewModel بتحديث كائن الـ `UiState` المجمع للشاشة بالكامل (`ScreenUiState`).\n"
            "   - إذا كانت الشاشة الرئيسية تقرأ `val uiState by viewModel.uiState.collectAsStateWithLifecycle()` في أعلى دالة الـ Screen وتمرر الـ `uiState` كاملاً إلى كل الدوال الفرعية:\n"
            "   - في كل ضغطة حرف، يتم اعتبار كل الدوال الفرعية متغيرة، فيُعاد حساب شجرة الـ Views والقوائم والصور بالكامل، مما يسبب بطء الكتابة وتشنج لوحة المفاتيح (Input Latency & Jank)!\n\n"
            "2. التشخيص العملي عبر الأدوات:\n"
            "   - فتح **Layout Inspector**: كتابة نص وملاحظة أن أرقام الـ Recomposition Count لجميع البطاقات والقوائم تتزايد بعد كل حرف!\n   - فحص الـ Flame Chart في **CPU Profiler**: رؤية وقت طويل مستهلك في تنفيذ دوال Composable أثناء حدث الـ KeyPress.\n\n"
            "3. الحلول المعمارية الثلاثة:\n"
            "   - **عزل حالة الإدخال (State Localization)**: الاحتفاظ بنص البحث محلياً أو في `StateFlow` منفصل لا يغير الـ UiState العامة للقائمة حتى اكتمال المعالجة.\n"
            "   - **تمرير الحقول الجزئية (Granular Parameter Passing)**: تمرير الخصائص التي تحتاجها الدالة فقط (`products: ImmutableList<Product>`) بدلاً من تمرير كائن `ScreenUiState` الضخم بالكامل.\n"
            "   - **تأخير البحث عبر Debounce**: استخدام `debounce(300ms)` في الـ ViewModel حتى لا يتم إرسال طلبات البحث الحسابية في كل حرف بل بعد توقف المستخدم عن الكتابة."
        ),
        "practical_walkthrough": (
            "إصلاح مشكلة الـ Keystroke Recomposition وتطبيق العزل الحبيبي للحالة:\n"
            "```kotlin\n"
            "// ❌ كود سيء: يمرر كائن الحالة بالكامل لكل المكونات، مما يعيد تركيب القائمة الثقيلة في كل حرف:\n"
            "@Composable\n"
            "fun BadSearchDashboard(viewModel: DashboardViewModel) {\n"
            "    val state by viewModel.uiState.collectAsStateWithLifecycle()\n"
            "    Column {\n"
            "        // كتابة حرف هنا تغير state.query وتجبر HeavyFeedView على إعادة التركيب فوراً!\n"
            "        SearchInput(state.query, viewModel::onQueryChange)\n"
            "        HeavyFeedView(state) // 💥 تعيد تركيب 100 عنصر في كل ضغطة مفتاح!\n"
            "    }\n"
            "}\n"
            "\n"
            "// ✅ كود احترافي: تمرير المعاملات المستقلة وعزل الـ Feed عن تغيرات نص البحث:\n"
            "@Composable\n"
            "fun GoodSearchDashboard(\n"
            "    query: String,\n"
            "    onQueryChange: (String) -> Unit,\n"
            "    feedItems: ImmutableList<FeedItem>\n"
            ") {\n"
            "    Column {\n"
            "        SearchInput(query = query, onQueryChange = onQueryChange)\n"
            "        // يتم تخطي HeavyFeedView بنسبة 100% أثناء الكتابة لأن feedItems لم تتغير!\n"
            "        HeavyFeedView(items = feedItems)\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Excessive recomposition on keystrokes occurs when a single monolithic `UiState` containing the query string is passed to child composables, invalidating the entire screen on every character. Fix it by decoupling text input state from unrelated UI branches, passing granular stable parameters, and debouncing queries in the ViewModel.",
        "best_answer": (
            "A screen re-rendering excessively after each keystroke is a classic symptom of poor state granularity and un-hoisted state coupling.\n\n"
            "1. **Root Cause**: When a user types a letter, the `TextField` emits `onValueChange`. The ViewModel modifies a property (e.g. `query`) inside a monolithic `ScreenUiState` data class. Because the root composable reads `val state by viewModel.uiState.collectAsStateWithLifecycle()`, the root and every child composable that accepts `state` as a parameter are re-evaluated. If heavy feeds, charts, or lists take `ScreenUiState`, they fail smart skipping and recompose on every typed character, inducing severe keyboard lag.\n\n"
            "2. **Diagnosis**: In the Android Studio **Layout Inspector**, I type into the search field and watch the Recomposition counter. If the product list or summary card recomposition count increments alongside the search bar, the state boundary is leaking.\n\n"
            "3. **Architectural Fix**:\n"
            "   - **Granular Parameter Passing**: Do not pass the whole state class to children. Pass only the data each child requires (e.g. `items = state.feedItems`). If `feedItems` has not mutated, Compose skips the feed completely.\n"
            "   - **State Isolation & Debouncing**: In the ViewModel, decouple raw text typing from query execution using a distinct `MutableStateFlow<String>` with `.debounce(300ms).distinctUntilChanged()` before executing searches."
        ),
        "deep_answer": (
            "Under the hood, Kotlin data classes implement structural equality across all fields. "
            "When `state.copy(query = \"a\")` produces a new instance, passing `state` into `HeavyFeedView(state)` passes an object whose `equals()` evaluates to `false` because the `query` field changed, even though `HeavyFeedView` only cares about `items`!\n\n"
            "Another critical lever is using **Lambda-based State Readers** when children only need derived calculations. "
            "If a child merely needs to check if the query is empty, pass a lambda `isQueryEmpty: () -> Boolean = { query.isEmpty() }`, keeping the state read scoped strictly to the child that needs it.\n\n"
            "In Compose Compiler metrics, we ensure all child item parameters are marked `@Immutable` or `ImmutableList` so Strong Skipping can cleanly bypass them while text mutations occur in adjacent branches."
        ),
        "follow_ups": [
            {
                "question": "Why is passing a monolithic `ScreenUiState` to child composables risky for performance?",
                "answer": "Because mutating any single property (like a typing query or transient error) produces a new `ScreenUiState` instance, causing every child that receives the whole object to fail equality checks and force recomposition."
            },
            {
                "question": "How does `debounce(300)` in the ViewModel prevent search stutter?",
                "answer": "`debounce(300)` buffers high-frequency keystrokes, waiting until the user stops typing for 300 milliseconds before firing expensive filtering, repository, or network operations."
            }
        ]
    },
    {
        "id": "COM-24",
        "arabic_explanation": (
            "عندما يستمر مستمع (Listener) في العمل واستهلاك الموارد بعد مغادرة الـ Composable للشاشة: ما هو الـ Effect الخاطئ وكيف يُعالج؟\n\n"
            "1. ما هو الـ Effect الخاطئ الشائع؟\n"
            "   - الخطأ الكلاسيكي هو استخدام **`LaunchedEffect(Unit)`** أو `SideEffect` لتسجيل Listener خارجي متزامن (مثل `SensorManager`, `LocationListener`, `BroadcastReceiver`, أو SDK Listener).\n"
            "   - `LaunchedEffect` مخصص للـ Suspending functions؛ عندما يغادر الـ Composable، يقوم بإلغاء الكوروتين الخاص به، ولكنه **لا يعرف كيف ينفذ دالة `unregisterListener()` العادية غير المعلقة!**\n"
            "   - النتيجة: يظل الـ Listener مسجلاً داخل نظام التشغيل، ويستمر في إرسال الأحداث، مما يسبب تسريب ذاكرة كارثي واستنزاف بطارية الجهاز.\n\n"
            "2. ما هو الـ Effect الصحيح الإلزامي؟\n"
            "   - الـ Effect الصحيح هو **`DisposableEffect(key)`**.\n"
            "   - يفرض `DisposableEffect` توفير كتلة تنظيف صريحة: **`onDispose { ... }`**.\n"
            "   - عند مغادرة الـ Composable للشاشة أو عند تغير الـ key، يستدعي Compose دالة `onDispose` فوراً، مما يضمن إلغاء تسجيل الـ Listener بنسبة 100% وتحرير الموارد."
        ),
        "practical_walkthrough": (
            "تصحيح تسريب مستمع المستشعر باستخدام DisposableEffect و onDispose:\n"
            "```kotlin\n"
            "// ❌ كود خاطئ: استخدام LaunchedEffect لتسجيل مستمع لا يتم تنظيفه عند المغادرة:\n"
            "@Composable\n"
            "fun BadSensorMonitor(sensorManager: SensorManager, sensor: Sensor) {\n"
            "    LaunchedEffect(Unit) {\n"
            "        val listener = object : SensorEventListener {\n"
            "            override fun onSensorChanged(event: SensorEvent?) { /* معالجة */ }\n"
            "            override fun onAccuracyChanged(s: Sensor?, a: Int) {}\n"
            "        }\n"
            "        // 💥 المستمع يستمر في العمل في خلفية الهاتف حتى بعد مغادرة الشاشة!\n"
            "        sensorManager.registerListener(listener, sensor, SensorManager.SENSOR_DELAY_UI)\n"
            "    }\n"
            "}\n"
            "\n"
            "// ✅ كود سليم: استخدام DisposableEffect مع onDispose الإلزامي للتنظيف:\n"
            "@Composable\n"
            "fun GoodSensorMonitor(sensorManager: SensorManager, sensor: Sensor) {\n"
            "    DisposableEffect(sensorManager, sensor) {\n"
            "        val listener = object : SensorEventListener {\n"
            "            override fun onSensorChanged(event: SensorEvent?) { /* معالجة */ }\n"
            "            override fun onAccuracyChanged(s: Sensor?, a: Int) {}\n"
            "        }\n"
            "        sensorManager.registerListener(listener, sensor, SensorManager.SENSOR_DELAY_UI)\n"
            "\n"
            "        // يُستدعى تلقائياً فور مغادرة الـ Composable أو تغير الـ sensor:\n"
            "        onDispose {\n"
            "            sensorManager.unregisterListener(listener)\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "The wrong effect is `LaunchedEffect(Unit)` or `SideEffect`. They lack cleanup callbacks for non-suspending listeners. When the composable leaves composition, the listener remains registered. The correct solution is `DisposableEffect`, which enforces an `onDispose { ... }` block to unregister listeners synchronously.",
        "best_answer": (
            "If a callback or listener continues operating after a composable leaves the composition, the developer mistakenly implemented the registration inside **`LaunchedEffect`** or raw composable code.\n\n"
            "`LaunchedEffect` is tailored exclusively for cooperative Kotlin coroutines. When a composable leaves the Slot Table, Compose cancels the coroutine job. "
            "However, if a non-suspending, platform-level listener (such as `LocationListener`, `SensorEventListener`, or `BroadcastReceiver`) was registered inside the coroutine body, canceling the coroutine does not invoke `unregisterListener()`. The system service retains a strong reference, causing a persistent memory leak and background battery drain.\n\n"
            "The mandatory solution is **`DisposableEffect`**:\n"
            "1. It executes registration upon entering the composition.\n"
            "2. It mandates a trailing **`onDispose { ... }`** clause.\n"
            "3. The instant the composable leaves the composition tree (or if any key argument changes), Compose synchronously executes `onDispose`, unregistering the listener cleanly."
        ),
        "deep_answer": (
            "Under the hood, `DisposableEffectImpl` implements `RememberObserver`. "
            "When the Compose runtime determines during a layout pass that an existing node was pruned from the UI hierarchy, it invokes `onForgotten()` on registered `RememberObserver` instances, directly triggering the `onDispose` lambda.\n\n"
            "Another frequent leak pattern is capturing changing parameters inside `onDispose`. "
            "If the keys passed to `DisposableEffect(key1)` mutate, Compose first executes `onDispose` for the old keys before executing the effect block for the new keys. "
            "If keys are omitted or set to `Unit` while external dependencies mutate, the unregistration might hold stale objects or unregister the wrong instance.\n\n"
            "In modern Android architectures, we often hoist these listeners entirely out of the UI into cold Flows in repository/data layers using `callbackFlow { ... awaitClose { unregisterListener() } }`, consuming them in Compose via `collectAsStateWithLifecycle()`."
        ),
        "follow_ups": [
            {
                "question": "What is `callbackFlow` and why is it preferred over `DisposableEffect` for listeners?",
                "answer": "`callbackFlow` encapsulates callback-based APIs into reactive Kotlin Flows with an `awaitClose { ... }` cleanup block, shifting lifecycle management away from UI components into domain/data layers."
            },
            {
                "question": "What happens if you omit `onDispose` inside a `DisposableEffect`?",
                "answer": "The code will not compile. The Compose compiler enforces `onDispose` as the mandatory return type of a `DisposableEffect` block."
            }
        ]
    },
    {
        "id": "COM-25",
        "arabic_explanation": (
            "عندما يضغط المستخدم على زر الحفظ (Save) مرتين بسرعة والطلب جارٍ: كيف تجعل سلوك الواجهة (UI) وسلوك النطاق (Domain) آمناً ومحمياً؟\n\n"
            "1. طبقة واجهة المستخدم (UI Layer Protection):\n"
            "   - **تعطيل الزر فورياً (Disable Button)**: بمجرد الضغط الأول، تتحول حالة `isSaving` في الـ `UiState` إلى `true`، مما يجعل `Button(enabled = !uiState.isSaving)` معطلاً فورياً.\n"
            "   - **Click Debouncing**: استخدام Modifier نقر مخصص يفحص وقت الضغط الأخير ويتجاهل أي نقرة تحدث خلال 500ms.\n\n"
            "2. طبقة الـ ViewModel (State Holder Protection):\n"
            "   - **فحص الحالة الحالية (State Guarding)**: قبل إطلاق العملية، التحقق من: `if (_uiState.value.isSaving) return`.\n"
            "   - **استخدام Mutex أو Concurrency Operators**: إما الاحتفاظ بمرجع للـ `Job` والتحقق من `if (saveJob?.isActive == true) return`، أو استخدام `Mutex` لمنع الدخول المتزامن.\n\n"
            "3. طبقة الـ Domain والـ Backend (Idempotency):\n"
            "   - حتى لو نجحت نقرتان في المرور، يجب أن تكون العملية **Idempotent**.\n"
            "   - استخدام **Idempotency Key (UUID)** يُولد مرة واحدة لكل معاملة ويُرسل في ترويسة الطلب (`Idempotency-Key: uuid`)؛ حتى لو استلم السيرفر طلبين، ينفذ الأول ويرد بنفس النتيجة للثاني دون تكرار الخصم أو الحفظ."
        ),
        "practical_walkthrough": (
            "تأمين زر الحفظ في الـ UI والـ ViewModel والـ Network Layer:\n"
            "```kotlin\n"
            "// 1. في ViewModel: حماية الطلب من التكرار عبر State Guarding ومفتاح Idempotency:\n"
            "class CheckoutViewModel(private val orderRepository: OrderRepository) : ViewModel() {\n"
            "    private val _uiState = MutableStateFlow(CheckoutUiState())\n"
            "    val uiState: StateFlow<CheckoutUiState> = _uiState.asStateFlow()\n"
            "\n"
            "    private var activeSaveJob: Job? = null\n"
            "\n"
            "    fun saveOrder() {\n"
            "        // منع التنفيذ إذا كان هناك طلب جارٍ بالفعل:\n"
            "        if (activeSaveJob?.isActive == true || _uiState.value.isSaving) return\n"
            "\n"
            "        activeSaveJob = viewModelScope.launch {\n"
            "            _uiState.update { it.copy(isSaving = true) }\n"
            "            try {\n"
            "                val idempotencyKey = UUID.randomUUID().toString()\n"
            "                orderRepository.submitOrder(idempotencyKey, _uiState.value.orderData)\n"
            "                _uiState.update { it.copy(isSaving = false, isSuccess = true) }\n"
            "            } catch (e: Exception) {\n"
            "                _uiState.update { it.copy(isSaving = false, errorMessage = e.message) }\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "}\n"
            "\n"
            "// 2. في Compose: تعطيل الزر بصرياً وإظهار مؤشر تقدم:\n"
            "@Composable\n"
            "fun SaveButton(uiState: CheckoutUiState, onSaveClick: () -> Unit) {\n"
            "    Button(\n"
            "        onClick = onSaveClick,\n"
            "        enabled = !uiState.isSaving // معطل فورياً بمجرد أول نقرة!\n"
            "    ) {\n"
            "        if (uiState.isSaving) {\n"
            "            CircularProgressIndicator(modifier = Modifier.size(16.dp), strokeWidth = 2.dp)\n"
            "        } else {\n"
            "            Text(\"Save Order\")\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Defend against rapid double-taps using defense-in-depth: disable the button in UI when `isSaving` is true, guard execution in the ViewModel by checking `if (saveJob?.isActive == true) return`, and ensure domain/backend idempotency by sending a unique client-generated Idempotency Key with the request.",
        "best_answer": (
            "Protecting against double-tap race conditions requires a defense-in-depth strategy across UI, ViewModel, and Domain/Backend boundaries.\n\n"
            "1. **UI Layer Defense**: The UI reflects saving state immediately. We set `Button(enabled = !uiState.isSaving)` and show an inline progress spinner. When disabled, Android skips touch event dispatching to that node. Additionally, click handlers can be wrapped in a single-click debounce modifier that rejects clicks within 400ms.\n\n"
            "2. **ViewModel Concurrency Guard**: Because UI recomposition occurs on the next frame (leaving a fraction of a millisecond where a second tap could fire), the ViewModel must guard execution synchronously:\n"
            "   - Maintain a reference to the active coroutine job: `if (saveJob?.isActive == true) return`.\n"
            "   - Atomically update state: `if (!_isProcessing.compareAndSet(false, true)) return`.\n\n"
            "3. **Domain & Backend Idempotency**: Network operations must be structurally idempotent. The client generates a unique `Idempotency-Key` (UUID) attached to the network payload. Even if network latency causes duplicate packets, the backend processes the transaction once and returns the cached confirmation for subsequent calls."
        ),
        "deep_answer": (
            "Under the hood, relying solely on `enabled = false` in Compose has a micro-window vulnerability. "
            "Touch input dispatch occurs on the main looper. "
            "If a user taps twice with exceptional speed within the same frame interval before the snapshot state invalidation triggers a recomposition of the button's layout node, the second click event will invoke `onClick`.\n\n"
            "This makes the ViewModel synchronous guard mandatory. "
            "By checking `saveJob?.isActive == true` at the very top of the function body on the main thread, the second invocation is discarded synchronously before any coroutine is scheduled or network request initiated.\n\n"
            "In payment flows (Fintech), we also enforce transactional database flags: setting a local database status to `PENDING_SUBMISSION` within a local Room transaction before dispatching network calls, guaranteeing crash recovery and duplicate transaction avoidance."
        ),
        "follow_ups": [
            {
                "question": "Why is disabling the button in UI insufficient on its own?",
                "answer": "Touch dispatch and recomposition are asynchronous. Two rapid taps within the same VSYNC frame will execute the click callback twice before Compose completes recomposing the button into a disabled state."
            },
            {
                "question": "How does `compareAndSet` work for atomic gating in ViewModel?",
                "answer": "`AtomicBoolean.compareAndSet(false, true)` checks and updates a flag in a single atomic CPU instruction, guaranteeing that only the first thread or event passes while subsequent calls fail immediately."
            }
        ]
    },
    {
        "id": "COM-26",
        "arabic_explanation": (
            "عندما يعود موضع التمرير (Scroll Position) في `LazyColumn` إلى البداية بعد تحديث البيانات (Data Refresh): ما الذي يجب فحصه؟\n\n"
            "1. الأسباب الجذرية لإعادة ضبط موضع السكرول (Scroll Reset):\n"
            "   - **غياب المفاتيح الثابتة (`key` Parameter)**: إذا لم توفر مفتاحاً ثابتاً، يعتمد Compose على الـ Index. إذا استبدلت القائمة بالكامل بكائنات جديدة، يعتقد Compose أن كل شيء جديد ويعيد التعيين للصفر.\n"
            "   - **توليد كائنات IDs جديدة في كل Refresh**: إذا كانت الـ Data Classes تولد معرفات مؤقتة (مثل `UUID.randomUUID()` أو `System.currentTimeMillis()`) في كل مرة يتم فيها عمل Refresh، تتغير كل الـ Keys فيفقد الـ Scroll موقعه تماماً!\n"
            "   - **إفراغ القائمة المؤقت (Transient Empty List)**: أثناء عملية الـ Refresh، يقوم الكود بنشر `emptyList()` أو الانتقال لحالة `UiState.Loading` التي تمحو الـ `LazyColumn` من الشاشة لحظياً! عند زوال الـ LazyColumn تتدمر الـ `LazyListState` ويعود السكرول للصفر عند ظهور القائمة الجديدة!\n\n"
            "2. ما الذي يجب فحصه وإصلاحه؟\n"
            "   - **فحص استقرار الـ Keys**: التأكد من استخدام معرفات ثابتة من قاعدة البيانات/السيرفر (`key = { it.serverId }`).\n"
            "   - **الحفاظ على القائمة أثناء التحميل (Retain List During Refresh)**: عدم إخفاء الـ LazyColumn أثناء التحديث؛ بل إظهار مؤشر سحب (`PullRefreshIndicator` أو شريط علوي) مع إبقاء القائمة السابقة معروضة في مكانها.\n"
            "   - **الاحتفاظ بالـ `LazyListState` في الـ ViewModel أو عبر `rememberSaveable`**."
        ),
        "practical_walkthrough": (
            "حل مشكلة فقدان موضع السكرول عبر الحفاظ على القائمة والمفاتيح المستقرة أثناء التحديث:\n"
            "```kotlin\n"
            "// ❌ كود سيء: يفرغ القائمة أثناء التحميل ويستخدم مفاتيح غير مستقرة فيعيد السكرول للصفر:\n"
            "@Composable\n"
            "fun BadFeed(uiState: FeedUiState) {\n"
            "    if (uiState.isLoading) {\n"
            "        // 💥 إخفاء LazyColumn تماماً يدمر موضع السكرول فوراً!\n"
            "        CircularProgressIndicator()\n"
            "    } else {\n"
            "        LazyColumn {\n"
            "            items(uiState.items) { item -> /* بدون key! */ }\n"
            "        }\n"
            "    }\n"
            "}\n"
            "\n"
            "// ✅ كود سليم: إبقاء القائمة ظاهرة أثناء التحديث مع مفاتيح مستقرة:\n"
            "@Composable\n"
            "fun GoodFeed(\n"
            "    items: ImmutableList<FeedItem>,\n"
            "    isRefreshing: Boolean,\n"
            "    listState: LazyListState = rememberLazyListState()\n"
            ") {\n"
            "    Box {\n"
            "        // تظل القائمة موجودة في الـ Composition فلا يفقد listState موضعه إطلاقاً:\n"
            "        LazyColumn(state = listState) {\n"
            "            items(\n"
            "                items = items,\n"
            "                key = { it.stableId } // مفتاح دائم من قاعدة البيانات\n"
            "            ) {\n"
            "                FeedCard(it)\n"
            "            }\n"
            "        }\n"
            "        if (isRefreshing) {\n"
            "            LinearProgressIndicator(modifier = Modifier.fillMaxWidth().align(Alignment.TopCenter))\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "If scroll resets on refresh, inspect three culprits: missing or unstable `key` parameters (e.g. random UUIDs), temporary emissions of an empty list during refresh that resets `firstVisibleItemIndex` to 0, or replacing the `LazyColumn` with a full-screen loading spinner that unbinds `LazyListState` from composition.",
        "best_answer": (
            "A scroll position resetting to index 0 after a data refresh stems from state lifecycle disconnections or unstable identity mapping.\n\n"
            "1. **Transient Empty List Emission**: The most frequent architectural flaw is emitting `emptyList()` or an empty state when a refresh begins. If `LazyColumn` receives an empty list, its viewport collapses to 0 items, instantly resetting `LazyListState.firstVisibleItemIndex` to 0. When the refreshed data arrives a moment later, the list remains at the top.\n\n"
            "2. **Unmounting the LazyColumn (Screen-level Loading)**: If the UI replaces the `LazyColumn` with a full-screen `CircularProgressIndicator()` while `isRefreshing` is true, the `LazyColumn` is completely unmounted from the composition tree. Its underlying `LazyListState` loses its layout connection, resetting upon re-entry.\n\n"
            "3. **Unstable or Ephemeral Keys**: If items lack keys or use transient generators (like generating new IDs during DTO mapping), Compose treats incoming items as completely novel instances, discarding prior scroll offsets."
        ),
        "deep_answer": (
            "Under the hood, `LazyListState` tracks two core integers: `firstVisibleItemIndex` and `firstVisibleItemScrollOffset`. "
            "When a new list is bound, Compose's `LazyLayoutItemAnimator` attempts to match existing viewport items to the new list using their `key`. "
            "If the key of the top-visible item is found anywhere in the new list, Compose adjusts the scroll offset to keep that exact item pinned to the screen.\n\n"
            "To properly implement pull-to-refresh without scroll resets:\n"
            "- Never clear the existing data list in the ViewModel during a refresh; set an auxiliary boolean `isRefreshing = true`.\n"
            "- Keep the `LazyColumn` persistently composed and wrap it with `PullToRefreshBox` (Material 3) or place an overlay loading indicator at the top.\n"
            "- Always declare `key = { it.id }` using immutable persistent database IDs."
        ),
        "follow_ups": [
            {
                "question": "How does `LazyListState` keep the viewport pinned when items are added above the visible item?",
                "answer": "When stable keys are provided, `LazyListState` tracks the key of the top visible item. If new items are inserted above it, Compose automatically adjusts `firstVisibleItemIndex` so the currently viewed item remains stationary on screen."
            },
            {
                "question": "Can you preserve scroll position across process death?",
                "answer": "Yes. `rememberLazyListState()` uses `rememberSaveable` internally, saving `firstVisibleItemIndex` and scroll offset into the saved instance bundle automatically."
            }
        ]
    },
    {
        "id": "COM-27",
        "arabic_explanation": (
            "كيفية اختبار شاشة Compose شاملة تغطي حالات التحميل (Loading)، الخطأ (Error)، النجاح (Success)، والأذونات (Permissions):\n\n"
            "1. الأساس المعماري للاختبار السهل (Testability Architecture):\n"
            "   - كما شرحنا في COM-18، نختبر دائماً **Stateless Screen Composable** النقي وليس الـ Route Composable المحمل بـ Hilt و Navigation.\n"
            "   - نقوم بتمرير حالات الـ `UiState` يدوياً وبشكل مباشر، مما يجعل الاختبار سريعاً، وموثوقاً، ويعمل بنسبة 100% دون أي Mocking معقد.\n\n"
            "2. كتابة اختبارات Compose باستخدام `createComposeRule()`:\n"
            "   - **حالة التحميل (Loading)**: استدعاء `composeTestRule.setContent { Screen(UiState.Loading) }` والتحقق من ظهور `assertIsDisplayed()` لمؤشر التحميل.\n"
            "   - **حالة النجاح (Success)**: تمرير قائمة بيانات وهمية والتحقق من ظهور النصوص (`assertTextEquals`)، ومحاكاة النقر (`performClick()`) والتحقق من إطلاق الـ Callback المناسب.\n"
            "   - **حالة الخطأ (Error)**: تمرير رسالة خطأ والتحقق من ظهور زر إعادة المحاولة (Retry) وإطلاقه للحدث.\n"
            "   - **حالة الأذونات (Permissions)**: تمرير حالة الإذن كـ Parameter في الـ Screen والتحقق من ظهور شاشة التبرير (Rationale) أو زر طلب الإذن."
        ),
        "practical_walkthrough": (
            "كتابة اختبار شامل لحالات الشاشة المختلفة باستخدام Compose UI Test:\n"
            "```kotlin\n"
            "@RunWith(AndroidJUnit4::class)\n"
            "class DocumentScreenTest {\n"
            "    @get:Rule\n"
            "    val composeRule = createComposeRule()\n"
            "\n"
            "    @Test\n"
            "    fun whenStateIsLoading_showsProgressIndicator() {\n"
            "        composeRule.setContent {\n"
            "            DocumentScreen(uiState = DocumentUiState.Loading, onAction = {})\n"
            "        }\n"
            "        composeRule.onNodeWithTag(\"LOADING_SPINNER\").assertIsDisplayed()\n"
            "    }\n"
            "\n"
            "    @Test\n"
            "    fun whenStateIsSuccess_displaysDocumentsAndHandlesClick() {\n"
            "        var clickedId: String? = null\n"
            "        val docs = persistentListOf(Document(\"1\", \"Invoice\"))\n"
            "\n"
            "        composeRule.setContent {\n"
            "            DocumentScreen(\n"
            "                uiState = DocumentUiState.Success(docs),\n"
            "                onAction = { if (it is DocumentAction.Open) clickedId = it.id }\n"
            "            )\n"
            "        }\n"
            "\n"
            "        composeRule.onNodeWithText(\"Invoice\").assertIsDisplayed().performClick()\n"
            "        assertEquals(\"1\", clickedId)\n"
            "    }\n"
            "\n"
            "    @Test\n"
            "    fun whenPermissionDenied_showsRationale() {\n"
            "        composeRule.setContent {\n"
            "            DocumentScreen(\n"
            "                uiState = DocumentUiState.PermissionRequired(shouldShowRationale = true),\n"
            "                onAction = {}\n"
            "            )\n"
            "        }\n"
            "        composeRule.onNodeWithText(\"Storage permission is required to view documents\").assertIsDisplayed()\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Test multi-state screens by testing the stateless Screen composable directly using `createComposeRule()`. Pass explicit state objects for Loading, Success, Error, and PermissionRequired without mocking ViewModels, and assert node visibility using Semantics finders (`onNodeWithText`, `onNodeWithTag`) and user action assertions (`performClick`).",
        "best_answer": (
            "Testing a multi-state Compose screen requires verifying that each distinct state renders its expected UI hierarchy and responds accurately to interaction callbacks.\n\n"
            "1. **Target the Stateless Screen**: We never write UI tests against the ViewModel-bound Route composable. We test the pure Screen composable (`MyScreen(uiState, onAction)`), eliminating the need for MockWebServer, Hilt, or simulated Coroutine dispatchers.\n\n"
            "2. **Structuring the Test Suite** with `createComposeRule()`:\n"
            "   - **Loading State**: Render `UiState.Loading`. Assert that the loading spinner exists and content nodes are absent.\n"
            "   - **Success State**: Render `UiState.Success(data)`. Verify item texts with `onNodeWithText()`, scroll through lists with `performScrollToIndex()`, and verify item clicks with `performClick()`, asserting that callback lambdas capture expected parameters.\n"
            "   - **Error State**: Render `UiState.Error(\"Network timeout\")`. Assert that the error banner appears, click 'Retry', and verify that `onAction(Retry)` is fired.\n"
            "   - **Permission State**: Render `UiState.PermissionDenied`. Assert that the rationale dialog is displayed and actionable."
        ),
        "deep_answer": (
            "Under the hood, Compose UI tests interact directly with the **Semantics Tree** rather than the physical Android view hierarchy. "
            "To make assertions robust against localization changes, we use `Modifier.testTag(\"tag_name\")` or check semantic properties like `hasClickAction()`.\n\n"
            "When testing asynchronous state flows in Route composables (integration testing), we use `createAndroidComposeRule<MainActivity>()`. "
            "Compose's test rule automatically synchronizes with the main looper and idling resources: `composeTestRule.waitForIdle()` waits for all recompositions, measure passes, and active animations to settle before executing assertions, eliminating flaky sleeps.\n\n"
            "In modern CI/CD, we pair these unit UI tests with **Screenshot Testing** (using Roborazzi running on JVM), rendering all four states in headless tests in seconds to detect accidental visual regressions."
        ),
        "follow_ups": [
            {
                "question": "Why is testing the stateless Screen composable faster than testing the Activity/Route?",
                "answer": "It avoids booting up Android Activities, Hilt dependency graphs, SQLite databases, and NavControllers. It mounts only the pure UI hierarchy directly into the Compose test rule."
            },
            {
                "question": "How does `composeTestRule` avoid flaky timing issues compared to Espresso?",
                "answer": "`composeTestRule` has built-in synchronization with Compose's internal clock and snapshot system, automatically advancing virtual clock time and idling until all pending recompositions and animations complete."
            }
        ]
    },
    {
        "id": "COM-28",
        "arabic_explanation": (
            "متى يجب تجنب استخدام `derivedStateOf` لأن تكلفة استخدامه (Overhead) تتجاوز فائدته؟\n\n"
            "1. كيف يعمل `derivedStateOf` وما هي تكلفته الخفية؟\n"
            "   - دالة `derivedStateOf` تنشئ كائناً خاصاً في الذاكرة يُسجل نفسه في نظام الـ Snapshot System لمراقبة كل الحالات المقروءة بداخله.\n"
            "   - في كل تعديل لأي حالة، يتم حساب الدالة، ومقارنة الناتج عبر `equals()`، وتحديث الـ Snapshot Records.\n"
            "   - هذا يعني وجود **تكلفة حجز ذاكرة (Allocation Overhead)** وتكلفة معالجة مستمرة للمراقبة.\n\n"
            "2. متى يجب **تجنب** `derivedStateOf` تماماً؟\n"
            "   - **عندما تتغير الحالة المدخلة بنفس معدل تغير الناتج (1:1 Change Ratio)**:\n"
            "     * مثال: دمج اسمين `derivedStateOf { \"$firstName $lastName\" }`.\n"
            "     * هنا، كلما تغير الاسم سيتغير الناتج حتماً! لا يوجد أي تخميد (Dampening) للتردد! استخدام `remember(firstName, lastName) { \"$firstName $lastName\" }` أسرع وأخف بمراحل بدون أي Snapshot overhead.\n"
            "   - **عند العمليات الحسابية البسيطة جداً**: العمليات البدائية (مثل جمع رقمين) لا تستحق إنشاء كائن مراقبة كامل في الـ Heap.\n\n"
            "3. متى يكون `derivedStateOf` مفيداً وضرورياً فقط؟\n"
            "   - **فقط عندما تتغير المدخلات بمعدل أعلى بكثير من تغير الناتج (Many-to-One / Frequency Dampening)**:\n"
            "     * مثال: موضع التمرير `scrollOffset` يتغير 60 مرة في الثانية (آلاف البكسلات)، ولكن الناتج قيمة منطقية بسيطة: `derivedStateOf { scrollOffset > 100 }` (تتغير مرتين فقط: true أو false)."
        ),
        "practical_walkthrough": (
            "المقارنة بين الاستخدام الخاطئ لـ derivedStateOf والاستخدام السليم:\n"
            "```kotlin\n"
            "// ❌ استخدام خاطئ: هدر في الذاكرة والمعالج؛ المدخلات تتغير بنفس معدل الناتج:\n"
            "@Composable\n"
            "fun BadFullNameDisplay(firstName: String, lastName: String) {\n"
            "    // 💥 خطأ: derivedStateOf هنا يضيف حجز كائنات ومراقبة snapshots دون أي فائدة!\n"
            "    val fullName by remember { derivedStateOf { \"$firstName $lastName\" } }\n"
            "    Text(fullName)\n"
            "}\n"
            "\n"
            "// ✅ الاستخدام الأفضل والأخف لدمج النصوص العادية: استخدام remember العادي:\n"
            "@Composable\n"
            "fun GoodFullNameDisplay(firstName: String, lastName: String) {\n"
            "    val fullName = remember(firstName, lastName) { \"$firstName $lastName\" }\n"
            "    Text(fullName)\n"
            "}\n"
            "\n"
            "// ✅ الاستخدام المثالي والضروري لـ derivedStateOf: تخميد الترددات العالية (Frequency Dampening):\n"
            "@Composable\n"
            "fun ScrollToTopButton(listState: LazyListState) {\n"
            "    // listState.firstVisibleItemIndex يتغير باستمرار مع السكرول، ولكن النتيجة Boolean تتغير نادراً:\n"
            "    val showButton by remember {\n"
            "        derivedStateOf { listState.firstVisibleItemIndex > 0 }\n"
            "    }\n"
            "    if (showButton) {\n"
            "        FloatingActionButton(onClick = { /* سكرول للأعلى */ }) { Text(\"Top\") }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Avoid `derivedStateOf` when the inputs mutate at the exact same frequency as the output (e.g. concatenating first and last name), or for trivial calculations. In 1:1 change ratios, `derivedStateOf` adds snapshot tracking and object allocation overhead with zero optimization benefit; standard `remember(keys)` is much faster.",
        "best_answer": (
            "The golden rule of `derivedStateOf` is: **Only use it when the inputs change more frequently than the output**.\n\n"
            "Under the hood, `derivedStateOf` creates a state observation wrapper in the Snapshot system. It records dependencies dynamically, re-evaluates the lambda on any dependency mutation, and performs equality comparisons to suppress downstream recomposition notifications.\n\n"
            "You should strictly avoid `derivedStateOf` in two scenarios:\n"
            "1. **1-to-1 Mutation Frequency**: Consider combining two states: `val fullName by remember { derivedStateOf { \"$first $last\" } }`. Whenever `first` or `last` changes, `fullName` *must* also change. There are zero recompositions dampened or saved. The developer has introduced unnecessary allocation overhead and snapshot observer registration. Standard `remember(first, last) { \"$first $last\" }` is significantly cheaper and faster.\n\n"
            "2. **Trivial Primitive Computations**: Wrapping simple arithmetic (e.g. `count + 1`) in `derivedStateOf` incurs more CPU and allocation cost than simply computing the value directly on every recomposition pass."
        ),
        "deep_answer": (
            "A technical edge case to be aware of: `derivedStateOf` requires at least one read of a Compose `State` object inside its lambda block to register dependencies. "
            "If developers pass standard Kotlin properties (`val first: String`) into a `derivedStateOf` block wrapped in `remember { derivedStateOf { ... } }` without keys, the `derivedStateOf` block **never recalculates**, producing a permanent stale state bug!\n\n"
            "Where `derivedStateOf` shines brilliantly is **high-frequency UI dampening**:\n"
            "- Determining whether a scroll offset has crossed a threshold: input changes 60 times/second, output changes twice (`true`/`false`).\n"
            "- Filtering a list based on an item count threshold.\n"
            "- Computing a progress percentage that maps continuous pixel scrolls into stepped discrete states.\n\n"
            "In code reviews, if the output changes every time the input changes, we immediately reject `derivedStateOf` in favor of keyed `remember(keys)`."
        ),
        "follow_ups": [
            {
                "question": "What happens if no Compose `State` is read inside a `derivedStateOf` block?",
                "answer": "It registers zero snapshot dependencies. If plain parameters change, the derived state will never invalidate or recalculate, producing a stale value indefinitely."
            },
            {
                "question": "How does `remember(keys)` differ from `derivedStateOf` in memory footprint?",
                "answer": "`remember(keys)` stores only the computed value in the Slot Table and checks parameter equality. `derivedStateOf` allocates a `DerivedSnapshotState` object, dependency tracking sets, and registers a snapshot observer."
            }
        ]
    }
]

def main() -> None:
    if DATA_FILE.exists():
        existing = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        by_id = {item["id"]: item for item in existing}
    else:
        by_id = {}

    for item in COM_22_28:
        by_id[item["id"]] = item

    output = [by_id[k] for k in sorted(by_id.keys())]
    DATA_FILE.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {DATA_FILE} with questions COM-22 to COM-28. Total questions: {len(output)}")

if __name__ == "__main__":
    main()
