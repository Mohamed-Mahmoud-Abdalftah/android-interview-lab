#!/usr/bin/env python3
"""Generator for COM-15 through COM-21 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "com.json"

COM_15_21 = [
    {
        "id": "COM-15",
        "arabic_explanation": (
            "ماذا يعني استقرار الأنواع والبارامترات (Type & Parameter Stability) في Jetpack Compose؟\n\n"
            "1. العقد الأساسي للاستقرار (Stability Contract):\n"
            "   - الـ Compose Compiler يفحص كل نوع (Class / Interface) ويصنفه ليحدد ما إذا كان يمكنه **تخطي (Skip)** الـ Composable أثناء إعادة التركيب أم لا.\n"
            "   - الشروط الثلاثة للنوع المستقر (Stable):\n"
            "     * نتيجة مقارنة `equals()` بين كائنين متماثلين تعطي دائماً نفس النتيجة لنفس الكائنات.\n"
            "     * إذا تغيرت خاصية عامة في الكائن، يُشعر الكائن محرك Compose بالتغيير (عبر `SnapshotState`).\n"
            "     * كل الحقول العامة للكائن من أنواع مستقرة أيضاً.\n\n"
            "2. تصنيفات المترجم الثلاثة:\n"
            "   - **`@Immutable`**: نوع ثابت لا يتغير أبداً بعد إنشائه؛ جميع حقوله `val` من أنواع بدائية أو Immutable. يقدم أعلى درجات التحسين والتخطي.\n"
            "   - **`@Stable`**: نوع قد يحتوي على خصائص متغيرة، ولكنه يضمن إشعار Compose عند حدوث أي تعديل (مثل كائن يحمل `mutableStateOf`).\n"
            "   - **`Unstable`**: أي كائن يحتوي على حقول `var` عادية، أو واجهات (Interfaces)، أو مجموعات كوتلن القياسية مثل `List<T>` (لأن الـ `List` قد تكون في الحقيقة `ArrayList` قابلة للتعديل خلف الستار!).\n\n"
            "3. الحلول العملية لمشكلة الـ Unstable Types:\n"
            "   - استخدام **Kotlinx Immutable Collections** (`ImmutableList<T>`, `PersistentList<T>`).\n"
            "   - وسم الـ Data Classes الخارجية أو الـ Models بـ `@Immutable` صراحة.\n"
            "   - الاعتماد على **Strong Skipping Mode** المتاح في المترجم الحديث لتخطي الكائنات بالمرجع."
        ),
        "practical_walkthrough": (
            "جعل الكائنات مستقرة وإصلاح عدم الاستقرار في Data Models:\n"
            "```kotlin\n"
            "// ❌ كائن غير مستقر: المترجم يعتبره Unstable بسبب List و var:\n"
            "data class BadUserModel(\n"
            "    val id: String,\n"
            "    val tags: List<String>, // List هي Interface غير مضمونة الثبات للمترجم!\n"
            "    var score: Int // وجود var يجعل الكائن Unstable فوراً!\n"
            ")\n"
            "\n"
            "// ✅ كائن مستقر بنسبة 100% ويقبل التخطي الذكي (Skippable):\n"
            "import androidx.compose.runtime.Immutable\n"
            "import kotlinx.collections.immutable.ImmutableList\n"
            "\n"
            "@Immutable\n"
            "data class GoodUserModel(\n"
            "    val id: String,\n"
            "    val tags: ImmutableList<String>,\n"
            "    val score: Int\n"
            ")\n"
            "```"
        ),
        "quick_answer": "In Compose, type stability determines whether a composable can be skipped during recomposition. An `@Immutable` type never mutates; a `@Stable` type notifies Compose if it mutates. Unstable types—such as classes with mutable `var` properties or standard Kotlin `List<T>`—force recomposition of the composables that accept them.",
        "best_answer": (
            "Type stability is the core contract that governs the Compose Compiler's smart skipping optimization.\n\n"
            "When a parent composable recomposes, Compose evaluates child composables. If all parameters passed to a child are **Stable** and their values evaluate as equal via `equals()`, Compose skips re-executing that child composable entirely.\n\n"
            "The compiler infers stability into three categories:\n"
            "1. **Immutable (`@Immutable`)**: All public properties are `val` and their types are also immutable. The object's state is guaranteed never to change post-creation (e.g. primitives, `String`, or annotated data classes).\n"
            "2. **Stable (`@Stable`)**: The object may be mutable, but it guarantees that any state mutations notify the composition (such as holding `mutableStateOf` properties).\n"
            "3. **Unstable**: Any class containing public `var` properties, external multi-module classes uncompiled by the Compose compiler plugin, or standard Kotlin collection interfaces (`List`, `Set`, `Map`). Because `List<T>` is an interface that could hide a mutable `ArrayList`, Compose assumes it can change without notification, marking any composable accepting it as unskippable."
        ),
        "deep_answer": (
            "To resolve collection instability in production architectures, teams historically wrapped lists in `@Immutable data class ImmutableHolder<T>(val items: List<T>)` or adopted `kotlinx.collections.immutable` (`ImmutableList<T>`). "
            "Annotating domain entities with `@Immutable` promises the compiler that callers will treat the model as immutable, allowing full skipping.\n\n"
            "In recent releases, Compose introduced **Strong Skipping Mode** (standard in Kotlin 2.0+). "
            "Under strong skipping, composables with unstable parameters *can* still be skipped if the instance reference has not changed (`===`), and lambdas with captures are automatically remembered. "
            "However, if a new instance of an unstable class is passed—even with identical data—it still forces recomposition.\n\n"
            "We audit stability using Compose Compiler metrics (`./gradlew assembleRelease -PcomposeCompilerReports=true`), inspecting the generated `-classes.txt` and `-composables.txt` files to eliminate any accidental stability regressions."
        ),
        "follow_ups": [
            {
                "question": "Why is standard `List<T>` considered unstable by the Compose Compiler?",
                "answer": "`List<T>` in Kotlin is a read-only interface, not an immutable one. At runtime, the backing implementation may be a mutable `ArrayList` whose contents could change without altering the list reference, so Compose cannot safely skip."
            },
            {
                "question": "How do you enable Strong Skipping Mode in Kotlin 2.0+?",
                "answer": "In Kotlin 2.0+, Strong Skipping Mode is enabled by default in the new Jetpack Compose Compiler Gradle plugin, though explicit stability annotations remain best practice for cross-module boundary optimization."
            }
        ]
    },
    {
        "id": "COM-16",
        "arabic_explanation": (
            "كيفية اكتشاف وتحديد عمليات الـ Recomposition الزائدة غير الضرورية (Avoidable Recompositions) ومعالجتها:\n\n"
            "1. الأدوات الرسمية لاكتشاف الـ Recomposition المفرط:\n"
            "   - **Layout Inspector في Android Studio**:\n"
            "     * يعرض عمودين حاسمين لكل Composable: **Recomposition Count** و **Skip Count**.\n"
            "     * إذا رأيت الـ Recomposition Count يتزايد باستمرار مع كل حركة بينما الـ Skip Count ثابت عند 0، فهذا مؤشر صريح على وجود Recomposition زائد!\n"
            "   - **Compose Compiler Metrics**:\n"
            "     * توليد تقارير الـ HTML والـ Text لمعرفة الدوال المصنفة كـ `restartable` فقط دون `skippable`، وتحديد البارامترات الـ `unstable` بالاسم.\n\n"
            "2. الأسباب الشائعة للـ Avoidable Recompositions:\n"
            "   - **تمرير بارامترات Unstable**: تمرير `List<T>` عادية أو كلاس خارجي.\n"
            "   - **كتابة كائنات جديدة داخل الـ Composable**: مثل إنشاء `Modifier.padding()` جديد داخل حلقة أو إنشاء كائنات Formatter بدون `remember`.\n"
            "   - **قراءة الـ State في مرحلة مبكرة جداً**: قراءة حالة سريعة التغير في مرحلة التكوين (Composition Phase) بدلاً من مرحلة الـ Layout/Draw عبر Lambdas.\n\n"
            "3. استراتيجية الإصلاح:\n"
            "   - استخدام `remember` للكائنات الحسابية.\n"
            "   - استخدام Lambdas لتأجيل قراءة الـ State (`Modifier.offset { ... }`).\n"
            "   - استخدام `derivedStateOf` لامتصاص الترددات العالية."
        ),
        "practical_walkthrough": (
            "تشخيص وإصلاح Recomposition متكرر أثناء الكتابة في حقل نصي:\n"
            "```kotlin\n"
            "// ❌ كود يسبب إعادة تركيب الشاشة بالكامل في كل حرف يُكتب:\n"
            "@Composable\n"
            "fun BadSearchScreen() {\n"
            "    var query by remember { mutableStateOf(\"\") }\n"
            "    Column {\n"
            "        TextField(value = query, onValueChange = { query = it })\n"
            "        // 💥 قراءة query هنا تجبر HeavyResultsList على إعادة التركيب في كل ضغطة مفتاح:\n"
            "        HeavyResultsList(query = query)\n"
            "    }\n"
            "}\n"
            "\n"
            "// ✅ كود مفصول: عزل الحالة، وإجراء البحث عبر Debounced ViewModel، وتخطي القائمة الثقيلة:\n"
            "@Composable\n"
            "fun GoodSearchScreen(viewModel: SearchViewModel = viewModel()) {\n"
            "    val query by viewModel.query.collectAsStateWithLifecycle()\n"
            "    val results by viewModel.searchResults.collectAsStateWithLifecycle()\n"
            "\n"
            "    Column {\n"
            "        SearchInput(query = query, onQueryChange = viewModel::onQueryChanged)\n"
            "        // HeavyResultsList يعاد تركيبها فقط عندما تتغير نتائج البحث الفعلية وليس مع كل حرف:\n"
            "        HeavyResultsList(results = results)\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Identify avoidable recomposition using Android Studio Layout Inspector (tracking Recomposition Counts vs Skip Counts) and Compose Compiler Metrics. Fix it by eliminating unstable parameters, wrapping heavy allocations in `remember`, deferring state reads to the layout/draw phases via lambdas, and dampening high-frequency reads with `derivedStateOf`.",
        "best_answer": (
            "Detecting and eliminating avoidable recompositions is central to maintaining 60/120fps UI fluidity.\n\n"
            "1. **Detection Tools**:\n"
            "   - **Android Studio Layout Inspector**: We enable recomposition highlights and inspect the **Recomposition Count** and **Skip Count** columns in real-time. If interacting with a single widget (e.g. typing in a search bar) increments the recomposition count of distant, unrelated UI elements while their skip count remains zero, a state leak or unstable parameter is present.\n"
            "   - **Compose Compiler Metrics**: Generating compiler metrics reveals which composables are marked as `unskippable` and highlights exact unstable parameters.\n\n"
            "2. **Common Root Causes & Fixes**:\n"
            "   - **Unstable Parameter Leaks**: Using unstable collections (`List<T>`). Solved with `@Immutable` or `ImmutableList`.\n"
            "   - **Premature State Reading**: Reading rapidly changing state (like scroll offset) in the *composition phase*. Solved by deferring reads to the *layout or draw phase* using lambda-based modifiers (`Modifier.offset { ... }` or `drawBehind { ... }`).\n"
            "   - **Unmemoized Allocations**: Creating fresh objects on every recomposition pass without `remember`."
        ),
        "deep_answer": (
            "Understanding Compose's three rendering phases—**Composition**, **Layout**, and **Draw**—is the highest-leverage insight for optimization. "
            "If a state is read during the Composition phase, any mutation forces the composable function to re-execute from top to bottom. "
            "If state is read strictly during the Layout phase (inside `MeasurePolicy` or a layout lambda modifier), Compose **skips composition entirely** and executes only layout measurement. "
            "If state is read in the Draw phase (inside `Modifier.drawWithContent { ... }`), Compose skips both composition and layout, jumping directly to the canvas draw pass!\n\n"
            "Another critical check is **Lambda Stabilization**. "
            "Passing inline lambdas that capture changing values or unstable parent properties invalidates the lambda instance on every pass unless Strong Skipping is enabled or the lambda is hoisted or wrapped in `remember`."
        ),
        "follow_ups": [
            {
                "question": "What is the three-phase pipeline of Jetpack Compose?",
                "answer": "The three phases are: 1. Composition (what UI to show - running composable functions), 2. Layout (where to place UI - measure and position nodes), and 3. Drawing (how to render UI - issuing GPU draw calls to Canvas)."
            },
            {
                "question": "How does `Modifier.offset { ... }` differ from `Modifier.offset(x, y)`?",
                "answer": "`Modifier.offset(x, y)` accepts concrete values and reads state in the Composition phase. `Modifier.offset { IntOffset(...) }` accepts a lambda, deferring state reads to the Layout phase, completely bypassing recomposition."
            }
        ]
    },
    {
        "id": "COM-17",
        "arabic_explanation": (
            "كيفية تحسين أداء القوائم الطويلة (Long Lists) والعمليات الحسابية المكلفة في Jetpack Compose:\n\n"
            "1. تحسين القوائم الطويلة في `LazyColumn`:\n"
            "   - **تحديد المفاتيح المستقرة (`key = { it.id }`)**: لتمكين التخطي الذكي وحماية الحالة أثناء السكرول والتعديل.\n"
            "   - **تحديد نوع المحتوى (`contentType`)**: لإعادة تدوير الـ Slots بين العناصر المتشابهة في القوائم غير المتجانسة.\n"
            "   - **تجنب العمليات الثقيلة داخل عناصر القائمة**: لا تقم أبداً بقراءة ملفات، فك تشفير صور يدوياً، أو تنسيق تواريخ معقدة داخل دالة الـ Item Composable دون `remember`.\n"
            "   - **LazyListState Optimization**: عدم قراءة موضع السكرول مباشرة داخل محتوى العنصر؛ بل استخدم `derivedStateOf` للأزرار العائمة خارج القائمة.\n\n"
            "2. تحسين الحسابات المكلفة (Expensive Calculations):\n"
            "   - استخدام `remember(key1, key2) { ... }` لحساب النتائج المعقدة لمرة واحدة فقط طالما أن المدخلات لم تتغير.\n"
            "   - ترحيل العمليات الحسابية الضخمة (مثل الفرز Sorting، والفلترة Filtering، وتحليل النصوص) إلى الـ `ViewModel` على **`Dispatchers.Default`** وتمرير النتائج الجاهزة كـ State نهائي للشاشة."
        ),
        "practical_walkthrough": (
            "تحسين قائمة طويلة تحتوي على حسابات معقدة وفلاتر:\n"
            "```kotlin\n"
            "// ❌ كود سيء: يقوم بفرز وتصفية 5000 عنصر في كل فريم Recomposition:\n"
            "@Composable\n"
            "fun BadProductList(products: List<Product>, filterText: String) {\n"
            "    // 💥 كارثة: معالجة ثقيلة جداً تعطل الـ Main Thread في كل سكرول!\n"
            "    val filtered = products.filter { it.name.contains(filterText) }.sortedBy { it.price }\n"
            "    LazyColumn {\n"
            "        items(filtered) { Text(it.name) }\n"
            "    }\n"
            "}\n"
            "\n"
            "// ✅ كود محسن: حفظ نتيجة الفلترة باستخدام remember وحماية القائمة بـ Keys:\n"
            "@Composable\n"
            "fun GoodProductList(\n"
            "    products: ImmutableList<Product>,\n"
            "    filterText: String,\n"
            "    modifier: Modifier = Modifier\n"
            ") {\n"
            "    // إعادة الحساب فقط إذا تغيرت قائمة المنتجات أو نص الفلترة:\n"
            "    val filtered = remember(products, filterText) {\n"
            "        products.filter { it.name.contains(filterText, ignoreCase = true) }\n"
            "            .sortedBy { it.price }\n"
            "            .toPersistentList()\n"
            "    }\n"
            "\n"
            "    LazyColumn(modifier = modifier) {\n"
            "        items(\n"
            "            items = filtered,\n"
            "            key = { it.id }, // مفتاح مستقر فريد\n"
            "            contentType = { \"PRODUCT_CARD\" } // نوع محتوى ثابت لإعادة التدوير\n"
            "        ) { product ->\n"
            "            ProductItemCard(product)\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Optimize long lists in Compose by providing unique stable `key`s and `contentType`s in `LazyColumn`, eliminating allocations inside item composables, and memoizing expensive computations with `remember(keys)` or offloading sorting and filtering to `Dispatchers.Default` in the ViewModel.",
        "best_answer": (
            "High-performance scrolling in Jetpack Compose requires eliminating work from the frame budget during list layout.\n\n"
            "1. **LazyList Optimization Pillars**:\n"
            "   - **Stable Keys**: Always declare `key = { it.id }` in `items()`. This lets Compose map items to stable slot table entries, skipping item recomposition when lists shift or reorder.\n"
            "   - **Content Types**: Specify `contentType` for heterogeneous lists to enable slot recycling across visually identical views.\n"
            "   - **Subcomposition Overhead**: Minimize nested `LazyRow` components or deep layout hierarchies inside items; keep item composables flat and lightweight.\n\n"
            "2. **Handling Expensive Calculations**:\n"
            "   - **Memoization**: If computations depend on UI inputs, wrap them in `remember(key1, key2) { expensiveComputation() }` so they re-run only when dependencies change.\n"
            "   - **Background Offloading**: Truly CPU-heavy tasks—such as sorting 10,000 items, searching, or regex filtering—do not belong in the UI layer. They must be executed inside the ViewModel or Domain layer via `flowOn(Dispatchers.Default)` and exposed as pre-calculated, ready-to-render immutable lists."
        ),
        "deep_answer": (
            "Under the hood, `LazyColumn` uses a specialized subcomposition pipeline called `SubcomposeLayout`. "
            "Unlike standard layouts that measure and compose in a single pass, `SubcomposeLayout` delays the composition of off-screen items until the scrolling measurement pass determines they are about to become visible. "
            "If an item's composable function does heavy work during this deferred composition pass, the frame budget (16.6ms at 60Hz or 8.3ms at 120Hz) is exceeded instantly, resulting in visible scroll jank.\n\n"
            "Another critical lever is image loading. "
            "When using Coil, always configure explicit sizing (`size(ViewSizeResolver)` or modifier constraints) and bitmap pooling. "
            "If images are loaded without fixed bounds in a LazyColumn, Coil decodes full images before layout measurement can constrain them, blowing through memory.\n\n"
            "In Macrobenchmark tests, we measure scroll performance using `FrameTimingMetric()` across continuous fling scrolls to ensure 99th percentile frame times stay strictly under the display hardware refresh limit."
        ),
        "follow_ups": [
            {
                "question": "What is `SubcomposeLayout` and why does it have an overhead compared to normal Layout?",
                "answer": "`SubcomposeLayout` allows measuring one child to decide what to compose in another (used by `LazyColumn` and `Scaffold`). It carries a runtime penalty because it interrupts the standard single-pass composition pipeline to execute dynamic subcomposition passes."
            },
            {
                "question": "Why shouldn't you place a `LazyColumn` inside a vertically scrolling `Column`?",
                "answer": "A scrolling `Column` provides infinite vertical constraints (`Constraints.Infinity`). A `LazyColumn` cannot calculate viewport bounds against infinite constraints, throwing an `IllegalStateException` at runtime."
            }
        ]
    },
    {
        "id": "COM-18",
        "arabic_explanation": (
            "الفرق المعماري بين الـ Route Composable والـ Screen Composable وكيف يعزز هذا الفصل جودة واختبار التطبيق:\n\n"
            "1. ما هو الـ Route Composable (المكون الموجّه)؟\n"
            "   - هو المكون المرتبط مباشرة بنظام التنقل (`NavGraphBuilder.composable(\"route\")`).\n"
            "   - **مسؤولياته**:\n"
            "     * حقن الـ `ViewModel` (عبر `hiltViewModel()` أو `viewModel()`).\n"
            "     * جمع الـ UI State عبر `collectAsStateWithLifecycle()`.\n"
            "     * تمرير الأحداث والتنقل (`onNavigateBack`, `onNavigateToDetails`).\n"
            "     * لا يحتوي على أي عناصر تصميم أو كود Layout مباشر!\n\n"
            "2. ما هو الـ Screen Composable (المكون البصري للشاشة)؟\n"
            "   - هو المكون البصري النقي الذي يرسم عناصر الشاشة الفعلية (Scaffold, Column, Cards).\n"
            "   - **مسؤولياته**:\n"
            "     * استقبال الـ `UiState` المكتمل كـ Parameter.\n"
            "     * استقبال أحداث المستخدم كـ Lambdas مستقلة (`onItemClicked: (Id) -> Unit`).\n"
            "     * **عديم الحالة تماماً (Stateless)** ولا يعلم أي شيء عن وجود `ViewModel` أو `NavController`!\n\n"
            "3. لماذا يُعتبر هذا الفصل معياراً إجبارياً في الشركات الكبرى؟\n"
            "   - **إمكانية عمل Previews فورية في Android Studio**: الـ Screen Composable لا يعتمد على ViewModel أو DI، لذا يعمل الـ `@Preview` ببيانات وهمية فوراً!\n"
            "   - **سهولة كتابة اختبارات Screenshot و UI Tests**: يمكنك اختبار رسم حالات الخطأ والنجاح دون الحاجة لـ Mocking لمكتبات Hilt و Navigation."
        ),
        "practical_walkthrough": (
            "الفصل المعماري القياسي بين Route Composable و Screen Composable:\n"
            "```kotlin\n"
            "// 1. Route Composable: يربط التنقل والـ ViewModel بالواجهة (Stateful Coordinator):\n"
            "@Composable\n"
            "fun OrderDetailsRoute(\n"
            "    onNavigateBack: () -> Unit,\n"
            "    viewModel: OrderDetailsViewModel = hiltViewModel()\n"
            ") {\n"
            "    val uiState by viewModel.uiState.collectAsStateWithLifecycle()\n"
            "\n"
            "    OrderDetailsScreen(\n"
            "        uiState = uiState,\n"
            "        onBackClicked = onNavigateBack,\n"
            "        onCancelOrder = viewModel::cancelOrder\n"
            "    )\n"
            "}\n"
            "\n"
            "// 2. Screen Composable: كود بصري نقي بدون أي ارتباط بـ ViewModel أو Navigation (Stateless UI):\n"
            "@Composable\n"
            "fun OrderDetailsScreen(\n"
            "    uiState: OrderDetailsUiState,\n"
            "    onBackClicked: () -> Unit,\n"
            "    onCancelOrder: () -> Unit,\n"
            "    modifier: Modifier = Modifier\n"
            ") {\n"
            "    Scaffold(modifier = modifier) {\n"
            "        when (uiState) {\n"
            "            is OrderDetailsUiState.Loading -> LoadingView()\n"
            "            is OrderDetailsUiState.Success -> {\n"
            "                OrderContent(order = uiState.order, onCancel = onCancelOrder)\n"
            "            }\n"
            "            is OrderDetailsUiState.Error -> ErrorView(uiState.message)\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "A Route Composable is stateful and navigation-aware: it injects the ViewModel, collects `StateFlow` via `collectAsStateWithLifecycle()`, and binds navigation lambdas. A Screen Composable is stateless and pure: it accepts plain `UiState` and event lambdas, enabling instant Android Studio Previews and isolated UI testing.",
        "best_answer": (
            "Separating a feature screen into a **Route Composable** and a **Screen Composable** is the industry standard for scalable Jetpack Compose architecture.\n\n"
            "1. **The Route Composable (`...Route`)**: Acts as the orchestration boundary registered inside the `NavHost`. Its sole purpose is dependency resolution and lifecycle coordination: it retrieves the ViewModel (e.g. `hiltViewModel()`), collects UI state using `collectAsStateWithLifecycle()`, and bridges navigation callbacks (`onNavigateToDetail`). It contains zero layout logic.\n\n"
            "2. **The Screen Composable (`...Screen`)**: Acts as the pure declarative presentation layer. It takes only the resolved, immutable `UiState` and hoisted event callbacks (`onAction: (Action) -> Unit`). It knows nothing about `ViewModel`, Hilt, or `NavController`.\n\n"
            "This architectural separation delivers enormous benefits:\n"
            "- **Frictionless Previews**: The Screen composable can be rendered in Android Studio `@Preview` instantly with fake data without mocking complex ViewModel dependencies.\n"
            "- **Screenshot & UI Testing**: Screenshot tests (using Paparazzi or Roborazzi) and Compose UI tests can assert every visual permutation (`Loading`, `Error`, `Empty`) purely by passing fake states."
        ),
        "deep_answer": (
            "Under the hood, passing a `ViewModel` directly into a leaf UI Composable creates tight architectural coupling. "
            "If a composable references `viewModel.someProperty` or `navController.navigate()`, testing that composable requires a simulated `ViewModelStoreOwner`, instantiated coroutine dispatchers, and mocked navigation graphs.\n\n"
            "Furthermore, passing `NavController` deep into composable trees violates encapsulation and modularization. "
            "In multi-module Android apps, feature modules should not depend on the global app navigation graph. "
            "By hoisting navigation callbacks out of the Screen composable up to the Route composable, each feature module remains completely isolated and independently compilable.\n\n"
            "In our enterprise design pattern, every screen file has the canonical structure: `OrderDetailsRoute` at the top, `OrderDetailsScreen` below it, and multiple preview functions demonstrating distinct UI states."
        ),
        "follow_ups": [
            {
                "question": "Why shouldn't you pass `NavController` directly into a Screen Composable?",
                "answer": "Passing `NavController` couples your UI to navigation implementation details, prevents previews in Android Studio, complicates UI unit testing, and breaks multi-module encapsulation boundaries."
            },
            {
                "question": "Can a Route Composable be previewed in Android Studio?",
                "answer": "Typically no, because it requires active Hilt injection and navigation backstacks. We preview the pure Screen Composable instead."
            }
        ]
    },
    {
        "id": "COM-19",
        "arabic_explanation": (
            "كيفية بناء نظام تصميم (Design System) وثيمات (Themes) قابلة لإعادة الاستخدام في Jetpack Compose:\n\n"
            "1. ركائز نظام التصميم في Compose (Material 3 Foundations):\n"
            "   - **الألوان (Color Scheme)**: لوحات ألوان متوافقة مع الوضع الفاتح والداكن (Light & Dark) ودعم Dynamic Color (Material You في أندرويد 12+).\n"
            "   - **الخطوط والطباعة (Typography)**: أنماط نصية معيارية (`displayLarge`, `headlineMedium`, `bodySmall`) مبنية على كلاسات `TextStyle`.\n"
            "   - **الأشكال والحدود (Shapes)**: مستويات استدارة الحواف (`extraSmall`, `medium`, `large`).\n\n"
            "2. توفير الـ Theme عبر الـ CompositionLocal:\n"
            "   - يقوم الثيم بتغليف المحتوى باستخدام `MaterialTheme(...)`.\n"
            "   - يتم تمرير الألوان والخطوط ضمنياً عبر شجرة الـ Composition باستخدام `staticCompositionLocalOf` أو `compositionLocalOf`.\n"
            "   - الوصول للألوان في أي مكان يكون عبر: `MaterialTheme.colorScheme.primary` دون الحاجة لتمرير الثيم كـ Parameter في كل دالة!\n\n"
            "3. بناء سمات مخصصة تزيد عن Material Theme (Extended Design Tokens):\n"
            "   - عندما تحتاج الشركة لرموز تصميم خاصة لا توجد في Material 3 (مثل ألوان تحذير خاصة، أبعاد Spacings موحدة، أو مقاسات أيقونات):\n"
            "   - نقوم بإنشاء `data class AppSpacing(...)` و `CompositionLocalProvider(LocalAppSpacing provides customSpacing)`.\n"
            "   - ننشئ Object مخصص للوصول: `AppTheme.spacing.medium`."
        ),
        "practical_walkthrough": (
            "بناء Theme متكامل يدعم توكنز مخصصة للمسافات (Custom Spacing Tokens):\n"
            "```kotlin\n"
            "// 1. تعريف توكنز المسافات المخصصة:\n"
            "@Immutable\n"
            "data class AppSpacing(\n"
            "    val extraSmall: Dp = 4.dp,\n"
            "    val small: Dp = 8.dp,\n"
            "    val medium: Dp = 16.dp,\n"
            "    val large: Dp = 24.dp\n"
            ")\n"
            "val LocalAppSpacing = staticCompositionLocalOf { AppSpacing() }\n"
            "\n"
            "// 2. إنشاء Theme مخصص يدمج MaterialTheme مع التوكنز الجديدة:\n"
            "@Composable\n"
            "fun EnterpriseAppTheme(\n"
            "    darkTheme: Boolean = isSystemInDarkTheme(),\n"
            "    content: @Composable () -> Unit\n"
            ") {\n"
            "    val colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme\n"
            "    val spacing = AppSpacing()\n"
            "\n"
            "    CompositionLocalProvider(LocalAppSpacing provides spacing) {\n"
            "        MaterialTheme(\n"
            "            colorScheme = colorScheme,\n"
            "            typography = AppTypography,\n"
            "            shapes = AppShapes,\n"
            "            content = content\n"
            "        )\n"
            "    }\n"
            "}\n"
            "\n"
            "// 3. كائن وصول سريع (Theme Accessor):\n"
            "object AppTheme {\n"
            "    val spacing: AppSpacing\n"
            "        @Composable\n"
            "        @ReadOnlyComposable\n"
            "        get() = LocalAppSpacing.current\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Build reusable design systems in Compose using Material 3 themes providing `ColorScheme`, `Typography`, and `Shapes`. Extend custom branding tokens (like Spacings or elevation) using `staticCompositionLocalOf`, provide them via `CompositionLocalProvider`, and expose a clean accessor object like `AppTheme.spacing`.",
        "best_answer": (
            "A production-grade design system in Jetpack Compose is anchored on Material 3 foundations augmented with custom design tokens.\n\n"
            "1. **Core Material 3 Contracts**: We define standard tokens using `lightColorScheme` and `darkColorScheme`, supporting Android 12+ dynamic theming via `dynamicLightColorScheme(context)` when appropriate. Typography is centralized in `Typography`, ensuring consistent scaling across accessibility font scales, and `Shapes` standardizes border radii.\n\n"
            "2. **Custom Design Tokens (Extensions)**: Enterprise design systems frequently require dimensions that Material 3 does not model—such as standardized component paddings (`Spacing`), custom border widths, or domain-specific semantic colors (e.g. `cryptoGreen`, `fraudAlertRed`). We model these as immutable data classes and provide them through **`CompositionLocal`**:\n"
            "   - `val LocalAppSpacing = staticCompositionLocalOf { AppSpacing() }`\n"
            "   - In the top-level theme composable, we wrap the hierarchy with `CompositionLocalProvider(LocalAppSpacing provides spacing)`.\n\n"
            "3. **Unified Accessor**: We provide an ergonomic theme accessor object `AppTheme` with `@ReadOnlyComposable` getters, allowing engineers to write `AppTheme.spacing.medium` with zero recomposition overhead."
        ),
        "deep_answer": (
            "The choice between `compositionLocalOf` and `staticCompositionLocalOf` is a key performance consideration. "
            "`staticCompositionLocalOf` does not track reads during composition; when its value changes, the **entire composition tree below the provider is recomposed from scratch**. "
            "Because design system tokens (colors, spacings, fonts) rarely or never change dynamically within a single user session (only on dark-mode toggle), `staticCompositionLocalOf` is drastically faster because it skips registering per-read slot observers.\n\n"
            "In large design systems, we build custom UI component libraries (Buttons, InputFields, Cards) that enforce strict internal modifier rules. "
            "For example, an `AppButton` internally enforces standard touch targets (minimum 48dp for accessibility), applies `AppTheme.spacing` internal padding, and maps visual variants to semantic tokens, preventing inconsistent raw Material calls across feature teams."
        ),
        "follow_ups": [
            {
                "question": "What is the difference between `compositionLocalOf` and `staticCompositionLocalOf`?",
                "answer": "`compositionLocalOf` tracks state reads and recomposes only the specific composables that read `.current`. `staticCompositionLocalOf` doesn't track individual reads; when its value changes, it recomposes the entire child tree. It is preferred for static theme values because it avoids tracking overhead."
            },
            {
                "question": "Why should theme accessor properties be annotated with `@ReadOnlyComposable`?",
                "answer": "`@ReadOnlyComposable` signals to the Compose compiler that the getter reads composition locals but emits no UI nodes and does not restart or generate a recomposition group, saving bytecode size and runtime overhead."
            }
        ]
    },
    {
        "id": "COM-20",
        "arabic_explanation": (
            "كيفية التعامل الاحترافي مع المعاينات (Previews)، الأذونات (Permissions)، والتنقل (Navigation) في Jetpack Compose:\n\n"
            "1. المعاينات (Compose Previews):\n"
            "   - استخدام الـ **Multipreview Annotations** لإنشاء وسم مخصص مثل `@DevicePreviews` يجمع بين:\n"
            "     * وضع النهار ووضع الليل (Light / Dark).\n"
            "     * أحجام شاشات متعددة (Phone, Tablet, Foldable).\n"
            "     * أحجام خطوط وصول متعددة (Font Scale 1.5x للتحقق من إمكانية الوصول Accessibility).\n"
            "   - استخدام `PreviewParameterProvider` لتمرير حالات بيانات مختلفة (Loading, Error, Success) إلى نفس دالة المعاينة.\n\n"
            "2. التعامل مع الأذونات (Runtime Permissions):\n"
            "   - استخدام مكتبة **Accompanist Permissions** أو الـ `rememberLauncherForActivityResult` المدمج مع `ActivityResultContracts.RequestPermission()`.\n"
            "   - التعامل مع تدفق الأذونات بثلاث حالات:\n"
            "     * إذن ممنوح (`PermissionStatus.Granted`): عرض الميزة فوراً.\n"
            "     * إذن مرفوض مع مبرر (`shouldShowRationale`): عرض شاشة تشرح للمستخدم لماذا يحتاج التطبيق هذا الإذن.\n"
            "     * إذن مرفوض نهائياً: توجيه المستخدم لفتح إعدادات النظام (`Settings`).\n\n"
            "3. التنقل (Navigation):\n"
            "   - استخدام **Type-Safe Navigation** المتاح في Jetpack Navigation 2.8+ المبني على Kotlin Serialization بدلاً من الـ String URLs القديمة والمعرضة للأخطاء الإملائية."
        ),
        "practical_walkthrough": (
            "إعداد Multipreview احترافي واستخدام Type-Safe Navigation وطلب الأذونات:\n"
            "```kotlin\n"
            "// 1. Multipreview Annotation لاختبار كل حالات الشاشة بضغطة زر:\n"
            "@Retention(AnnotationRetention.BINARY)\n"
            "@Target(AnnotationTarget.FUNCTION)\n"
            "@Preview(name = \"Light Phone\", showBackground = true)\n"
            "@Preview(name = \"Dark Phone\", uiMode = Configuration.UI_MODE_NIGHT_YES, showBackground = true)\n"
            "@Preview(name = \"Large Font\", fontScale = 1.5f, showBackground = true)\n"
            "annotation class DevicePreviews\n"
            "\n"
            "// 2. استخدام Type-Safe Navigation مع Kotlinx Serialization (Navigation 2.8+):\n"
            "import kotlinx.serialization.Serializable\n"
            "\n"
            "@Serializable\n"
            "data object HomeDestination\n"
            "\n"
            "@Serializable\n"
            "data class ProfileDestination(val userId: String)\n"
            "\n"
            "fun NavGraphBuilder.appNavGraph(navController: NavController) {\n"
            "    composable<HomeDestination> {\n"
            "        HomeScreen(onProfileClick = { id -> navController.navigate(ProfileDestination(id)) })\n"
            "    }\n"
            "    composable<ProfileDestination> {\n"
            "        ProfileRoute()\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Handle Previews using custom Multipreview annotations and `PreviewParameterProvider` for multi-state rendering. Manage runtime permissions cleanly using `rememberLauncherForActivityResult` with rationale handling. Implement navigation using modern Type-Safe Navigation (Navigation 2.8+) via `@Serializable` classes instead of fragile route strings.",
        "best_answer": (
            "Managing Previews, Permissions, and Navigation cleanly requires adopting modern Jetpack Compose tooling standards.\n\n"
            "1. **Compose Previews**: Rather than writing individual `@Preview` annotations per file, we define custom **Multipreview Annotations** (e.g. `@ThemePreviews`, `@DevicePreviews`) that automatically render composables in Light mode, Dark mode, large accessibility font scales (1.5x), and tablet layouts. For state permutations, we use `@PreviewParameter(UserProvider::class)` to render empty, loaded, and error variants simultaneously.\n\n"
            "2. **Runtime Permissions**: We manage runtime permissions using `rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission())` paired with rationale logic. If denied, we check `ActivityCompat.shouldShowRationale()` to explain the user value before requesting again; if permanently denied, we provide a clean intent redirecting to Android System Settings.\n\n"
            "3. **Type-Safe Navigation (Navigation 2.8+)**: We discard legacy string URLs (`\"profile/{userId}\"`) in favor of official **Type-Safe Navigation**. Destined routes and arguments are modeled as `@Serializable` data classes and objects. The compiler verifies parameter types at compile time, eliminating URL encoding bugs and null-pointer parsing errors."
        ),
        "deep_answer": (
            "Type-Safe Navigation in Navigation 2.8+ transforms route handling under the hood. "
            "When navigating to `navController.navigate(ProfileDestination(userId = \"123\"))`, Navigation serializes the object into an internal route bundle using Kotlinx Serialization. "
            "Inside `composable<ProfileDestination> { backStackEntry -> ... }`, accessing arguments is completely type-safe: `val profile = backStackEntry.toRoute<ProfileDestination>()`, with automatic parsing of custom parcelable objects and primitive types.\n\n"
            "For permissions, handling configuration changes during an in-flight permission dialog is critical. "
            "Because `rememberLauncherForActivityResult` hooks into `ActivityResultRegistry`, recreation during rotation preserves the pending request callback, resolving correctly when the permission dialog dismisses.\n\n"
            "In testing, Type-Safe destinations make asserting navigation trivial: in Compose UI tests, we can query `navController.currentBackStackEntry?.toRoute<ProfileDestination>()` to verify that a button click routed to the expected typed destination."
        ),
        "follow_ups": [
            {
                "question": "What is the primary advantage of Type-Safe Navigation in Navigation 2.8+?",
                "answer": "Compile-time validation of route parameters, eliminating runtime typos, manual URI string building, manual bundle key retrieval, and parameter type casting bugs."
            },
            {
                "question": "Why shouldn't you request a runtime permission directly in `LaunchedEffect(Unit)`?",
                "answer": "Triggering permission dialogs automatically without user context or gesture violates Android guidelines, confuses users, and leads to high permission denial rates. Permissions should always be requested in response to an explicit user interaction."
            }
        ]
    },
    {
        "id": "COM-21",
        "arabic_explanation": (
            "كيف يعمل الـ `NavHost` وكيف يتم استعادة حالة التطبيق بعد موت العملية (Process Death) في Jetpack Compose:\n\n"
            "1. كيف يعمل الـ NavHost داخلياً؟\n"
            "   - الـ `NavHost` هو حاوية Composable ترتبط بكائن الـ `NavHostController`.\n"
            "   - يحتفظ بـ **BackStack** مكوّن من كائنات `NavBackStackEntry`.\n"
            "   - كل `NavBackStackEntry` يمتلك دورة حياة خاصة به (`Lifecycle`), و `ViewModelStore` خاص به (لحفظ ViewModels خاصة بالوجهة), و `SavedStateRegistry` خاص به لاستعادة الحالة.\n\n"
            "2. ما هو موت العملية (System-Initiated Process Death)؟\n"
            "   - عندما يضع المستخدم التطبيق في الخلفية لعدة ساعات أو يفتح لعبة ثقيلة، يقوم نظام التشغيل بإنهاء عملية التطبيق (Kill Process) لتحرير الذاكرة.\n"
            "   - عندما يعود المستخدم للتطبيق، يحاول النظام استعادة الشاشة التي كان يقف عليها بالضبط.\n\n"
            "3. كيف تُستعاد الحالة عبر الـ NavHost و SavedStateHandle؟\n"
            "   - يحتفظ الـ `NavHost` تلقائياً بمسار الـ BackStack بالكامل داخل الـ `Bundle` الخاص بالنشاط (`onSaveInstanceState`).\n"
            "   - عند إعادة التشغيل، يعيد الـ `NavHost` بناء شجرة الشاشات السابقة بنفس الترتيب.\n"
            "   - كائنات `rememberSaveable` في الشاشات السابقة تُستعاد فورياً من الـ `SaveableStateRegistry`.\n"
            "   - الـ ViewModels المرتبطة بالوجهات تستعيد متغيراتها المحفوظة تلقائياً عبر **`SavedStateHandle`**."
        ),
        "practical_walkthrough": (
            "استعادة حالة البحث وتفاصيل الشاشة عبر SavedStateHandle بعد موت العملية:\n"
            "```kotlin\n"
            "// في ViewModel: قراءة وحفظ الحالة داخل SavedStateHandle لضمان بقائها بعد موت العملية:\n"
            "class SearchViewModel(private val savedStateHandle: SavedStateHandle) : ViewModel() {\n"
            "    // getStateFlow تحفظ القيمة تلقائياً في SavedStateHandle وتستعيدها فور موت العملية:\n"
            "    val searchQuery: StateFlow<String> = savedStateHandle.getStateFlow(\"QUERY_KEY\", \"\")\n"
            "\n"
            "    fun onQueryChanged(newQuery: String) {\n"
            "        savedStateHandle[\"QUERY_KEY\"] = newQuery\n"
            "    }\n"
            "}\n"
            "\n"
            "// في الـ NavHost: التنقل واستعادة الوجهة والحالة تلقائياً:\n"
            "@Composable\n"
            "fun AppNavHost(navController: NavHostController = rememberNavController()) {\n"
            "    NavHost(navController = navController, startDestination = \"home\") {\n"
            "        composable(\"home\") { HomeScreen(...) }\n"
            "        composable(\"search\") {\n"
            "            // ViewModel مرتبط بالـ NavBackStackEntry ويستعيد SavedStateHandle تلقائياً:\n"
            "            val searchVm: SearchViewModel = hiltViewModel()\n"
            "            SearchRoute(viewModel = searchVm)\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "`NavHost` coordinates navigation by rendering composables bound to a backstack of `NavBackStackEntry` instances, each possessing its own Lifecycle, ViewModelStore, and SavedStateRegistry. Following process death, `NavHost` restores the full backstack hierarchy from the Activity's saved instance state bundle, while ViewModels recover state via `SavedStateHandle`.",
        "best_answer": (
            "The `NavHost` manages the presentation of destinations defined in a navigation graph, mapping navigation backstack entries to active composables.\n\n"
            "1. **BackStack Architecture**: Under the hood, the `NavHost` orchestrates a stack of `NavBackStackEntry` objects. Each entry is an isolated architectural scope with three distinct responsibilities:\n"
            "   - Its own **Lifecycle**: Transitions to `RESUMED` when on top, and `CREATED` when pushed into the backstack.\n"
            "   - Its own **ViewModelStore**: Scoping destination-specific ViewModels that survive configuration changes and clear only when popped off the backstack.\n"
            "   - Its own **SavedStateRegistry**: Providing slot isolation for `rememberSaveable` calls.\n\n"
            "2. **Process Death Restoration**: When the OS terminates an application in the background, Android invokes Activity `onSaveInstanceState()`. The `NavController` serializes the destination backstack and typed route arguments into this Bundle.\n\n"
            "Upon relaunch, `NavHost` rebuilds the backstack structure. Screen composables restore local UI state through `rememberSaveable`, while ViewModels restore saved inputs and queries via **`SavedStateHandle`**, making process recovery seamless to the user."
        ),
        "deep_answer": (
            "Testing process death restoration is mandatory for enterprise applications. "
            "We verify this via ADB: putting the app in the background (`pressHome()`) and executing `adb shell am kill <package_name>`, then relaunching the app from the recent apps switcher. "
            "If a screen crashes or resets to a blank state, it exposes un-hoisted memory state that wasn't backed by `SavedStateHandle` or `rememberSaveable`.\n\n"
            "Inside `NavHost`, transitions between destinations are animated using Compose animations (`enterTransition`, `exitTransition`). "
            "When navigating forward, `SaveableStateHolder` saves the composition state of the leaving composable and unbinds its Slot Table nodes from memory to preserve RAM. "
            "When popping the backstack, `SaveableStateHolder` restores the saved composition state, instantly recovering scroll positions and local text fields without re-instantiating the screen."
        ),
        "follow_ups": [
            {
                "question": "What is `SaveableStateHolder` and how does NavHost use it?",
                "answer": "`SaveableStateHolder` allows saving and restoring the composition state of composable subtrees by key. `NavHost` uses it to preserve the UI state of backstack entries that are not currently displayed on screen."
            },
            {
                "question": "How do you test process death locally without waiting for OS low-memory events?",
                "answer": "Enable 'Don't keep activities' in Developer Options to test configuration death, or send the app to background and run `adb shell am kill <package-name>` to simulate true OS process death."
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

    for item in COM_15_21:
        by_id[item["id"]] = item

    output = [by_id[k] for k in sorted(by_id.keys())]
    DATA_FILE.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {DATA_FILE} with questions COM-15 to COM-21. Total questions: {len(output)}")

if __name__ == "__main__":
    main()
