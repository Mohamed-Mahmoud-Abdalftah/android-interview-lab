#!/usr/bin/env python3
"""Generator for COM-08 through COM-14 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "com.json"

COM_08_14 = [
    {
        "id": "COM-08",
        "arabic_explanation": (
            "كيفية نمذجة وتصميم الـ UI State باستخدام `StateFlow` في تطبيقات Jetpack Compose الاحترافية:\n\n"
            "1. المبادئ الأساسية لنمذجة الحالة (UI State Modeling):\n"
            "   - **Immutable Data Classes**: يجب أن تكون كلاسات الحالة غير قابلة للتعديل وتتكون فقط من `val` لضمان استقرار Compose Compiler وتجنب سباقات التعديل.\n"
            "   - **Single Source of Truth**: الشاشة يجب أن تمتلك كائناً رئيسياً واحداً يصف كل ما يُعرض على الواجهة بدلاً من توزيع الحالة عبر 10 متغيرات منفصلة.\n"
            "   - **تمثيل الحالات كـ Sealed Interface**: عندما تكون الشاشة في حالات متبادلة حصرياً (Loading, Success, Error)، فإن الـ `sealed interface` يمنع الحالات المستحيلة (مثل ظهور Loading مع Error في نفس اللحظة).\n\n"
            "2. نمط الـ Single State Stream مقابل Multiple Streams:\n"
            "   - **Sealed State Hierarchy**: ممتاز للشاشات التي تنتقل بين حالات كاملة (FullScreen Loading -> Content -> Error Screen).\n"
            "   - **Combined State Container**: ممتاز للشاشات التي تحتوي على إدخالات متعددة، وفلاتر، وقوائم؛ حيث يتم جمعها في `data class ScreenUiState` واحدة.\n\n"
            "3. تحويل التدفقات (Transformations) باستخدام `stateIn`:\n"
            "   - استخدام `stateIn(scope, SharingStarted.WhileSubscribed(5000), initialValue)`.\n"
            "   - مهلة الـ 5000ms هي المعيار الذهبي في أندرويد لحماية التدفق من إعادة التشغيل أثناء تدوير الشاشة (Configuration Change) مع إيقافه عند إخفاء التطبيق في الخلفية لتوفير البطارية والبيانات."
        ),
        "practical_walkthrough": (
            "نمذجة UI State احترافية داخل ViewModel واستهلاكها في Compose:\n"
            "```kotlin\n"
            "// 1. تعريف نموذج الحالة بصيغة Sealed Interface مانعة للحالات المتضاربة:\n"
            "sealed interface ProductUiState {\n"
            "    data object Loading : ProductUiState\n"
            "    data class Success(val products: ImmutableList<Product>, val canCheckout: Boolean) : ProductUiState\n"
            "    data class Error(val message: String) : ProductUiState\n"
            "}\n"
            "\n"
            "// 2. إدارة الحالة في ViewModel باستخدام stateIn و WhileSubscribed(5000):\n"
            "class ProductViewModel(private val repository: ProductRepository) : ViewModel() {\n"
            "    val uiState: StateFlow<ProductUiState> = repository.observeProducts()\n"
            "        .map { products -> ProductUiState.Success(products.toPersistentList(), products.isNotEmpty()) }\n"
            "        .catch { emit(ProductUiState.Error(it.localizedMessage ?: \"Unknown error\")) }\n"
            "        .stateIn(\n"
            "            scope = viewModelScope,\n"
            "            started = SharingStarted.WhileSubscribed(5_000),\n"
            "            initialValue = ProductUiState.Loading\n"
            "        )\n"
            "}\n"
            "\n"
            "// 3. استهلاك الحالة في Compose بطريقة آمنة:\n"
            "@Composable\n"
            "fun ProductScreen(viewModel: ProductViewModel = viewModel()) {\n"
            "    val state by viewModel.uiState.collectAsStateWithLifecycle()\n"
            "    when (val current = state) {\n"
            "        is ProductUiState.Loading -> LoadingSpinner()\n"
            "        is ProductUiState.Success -> ProductList(current.products)\n"
            "        is ProductUiState.Error -> ErrorBanner(current.message)\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Model UI state using immutable data classes or sealed interfaces to make illegal states unrepresentable. Expose a read-only `StateFlow` from the ViewModel using `stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), initialValue)` so upstream flows stop when the app is backgrounded while surviving configuration changes, and collect it in Compose using `collectAsStateWithLifecycle()`.",
        "best_answer": (
            "In modern Jetpack Compose architectures, modeling UI state with `StateFlow` requires adhering to immutability, representational correctness, and lifecycle-aware emission.\n\n"
            "1. **State Modeling**: We define state either as a **Sealed Interface** (ideal for mutually exclusive states like `Loading`, `Success`, and `Error`) or an **Immutable Data Class** (ideal for complex forms or dashboard screens with independent sub-widgets). This makes invalid states structurally unrepresentable at compile time.\n\n"
            "2. **StateFlow Conversion**: In the ViewModel, raw repository flows are mapped, caught, and converted to hot state streams using **`stateIn`**:\n"
            "   - `scope = viewModelScope` ensures cleanup when the ViewModel clears.\n"
            "   - `started = SharingStarted.WhileSubscribed(5_000)`: This 5-second timeout is critical. It keeps upstream collection active across rapid configuration changes (screen rotations) while canceling expensive upstream database or network emissions when the user backgrounds the app.\n"
            "   - `initialValue`: Supplies an immediate non-null initial state.\n\n"
            "3. **UI Consumption**: In Compose, the state is collected using `collectAsStateWithLifecycle()`, guaranteeing that recomposition stops when the Activity or Fragment is in the background."
        ),
        "deep_answer": (
            "Under the hood, `StateFlow` is a conflated broadcast channel that retains only the latest value and conflates intermediate emissions if the collector is slower than the emitter. "
            "Because `StateFlow` uses structural equality (`equals()`) to filter emissions, if a ViewModel emits an identical data class state, collectors are not notified, preventing unnecessary recomposition passes.\n\n"
            "A frequent architectural dilemma is **Single Stream vs Multiple Streams**. "
            "While a single `StateFlow<ScreenUiState>` simplifies synchronization, updating a minor nested field in a massive state object could trigger broad recompositions if composables read the entire container instead of granular properties. "
            "To solve this, we ensure child composables receive only primitive or stable sub-fields via parameters rather than the whole screen state object.\n\n"
            "When testing in unit tests, `StateFlow` provides immediate synchronous access via `.value`, eliminating flaky async test harnesses when verifying state transitions."
        ),
        "follow_ups": [
            {
                "question": "Why is `SharingStarted.WhileSubscribed(5000)` preferred over `Eagerly` or `Lazily`?",
                "answer": "`Eagerly` never stops, draining battery even when the app is in the background. `Lazily` never stops once started. `WhileSubscribed(5000)` stops upstream work when subscribers hit zero, with a 5-second buffer to absorb transient unsubscriptions during screen rotation."
            },
            {
                "question": "Can `StateFlow` drop emissions, and does that matter for UI state?",
                "answer": "Yes, `StateFlow` is conflated and drops intermediate emissions if the collector is busy. For UI state, this is desirable because the UI only ever needs to render the most recent, up-to-date state."
            }
        ]
    },
    {
        "id": "COM-09",
        "arabic_explanation": (
            "ما هي المشكلة التي تحلها دالة `collectAsStateWithLifecycle()` مقارنة بـ `collectAsState()` العادية؟\n\n"
            "1. المشكلة القاتلة في `collectAsState()`:\n"
            "   - دالة `collectAsState()` العادية تستمع لـ `Flow` طالما أن الـ Composable موجود في شجرة الـ Composition.\n"
            "   - **لا تراقب دورة حياة الأندرويد (Android Lifecycle)** إطلاقاً!\n"
            "   - عندما يضغط المستخدم زر Home أو ينتقل التطبيق إلى الخلفية (Background):\n"
            "     * تظل الـ Composition موجودة في الذاكرة وتظل دالة `collectAsState()` تجمع البيانات بنشاط!\n"
            "     * يؤدي هذا إلى استمرار طلبات السيرفر، استنزاف البطارية، استهلاك باقة الإنترنت، وتحديث كائنات الواجهة في الخلفية دون أن يراها أحد، وربما حدوث Crash إذا حاول الكود الوصول لموارد مقفلة!\n\n"
            "2. كيف تحل `collectAsStateWithLifecycle()` هذه الكارثة؟\n"
            "   - هي جزء من مكتبة `androidx.lifecycle:lifecycle-runtime-compose`.\n"
            "   - تراقب دورة حياة الشاشة (`LifecycleOwner`)، وتعمل افتراضياً بنظام **`Lifecycle.State.STARTED`**:\n"
            "     * عندما تصبح الشاشة مرئية (`onStart` / `onResume`)، تبدأ في جمع الـ Flow فورياً.\n"
            "     * عندما تختفي الشاشة وتدخل الخلفية (`onStop`)، تقوم بإلغاء الكوروتين وإيقاف الاستماع تلقائياً.\n"
            "     * بالتزامن مع `SharingStarted.WhileSubscribed(5000)` في الـ ViewModel، تتوقف أيضاً استعلامات السيرفر وقاعدة البيانات upstream تماماً في الخلفية!"
        ),
        "practical_walkthrough": (
            "مقارنة عملية تظهر توفير الموارد وحماية التطبيق في الخلفية:\n"
            "```kotlin\n"
            "// ❌ كود خطير: يستمر في جمع البيانات واستهلاك البطارية حتى عندما يكون التطبيق مصغراً في الخلفية:\n"
            "@Composable\n"
            "fun DangerousScreen(viewModel: StockPriceViewModel) {\n"
            "    // collectAsState لا يعرف متى يدخل التطبيق إلى onStop:\n"
            "    val price by viewModel.livePriceFlow.collectAsState()\n"
            "    Text(\"Live Stock: $$price\")\n"
            "}\n"
            "\n"
            "// ✅ كود احترافي: يلغي الجمع تلقائياً عندما تكون الشاشة في الخلفية:\n"
            "import androidx.lifecycle.compose.collectAsStateWithLifecycle\n"
            "\n"
            "@Composable\n"
            "fun SafeScreen(viewModel: StockPriceViewModel) {\n"
            "    // يوقف الكوروتين فور انتقال الـ Lifecycle إلى ما دون STARTED:\n"
            "    val price by viewModel.livePriceFlow.collectAsStateWithLifecycle()\n"
            "    Text(\"Live Stock: $$price\")\n"
            "}\n"
            "```"
        ),
        "quick_answer": "`collectAsState()` is lifecycle-unaware; it continues collecting flows when the app is in the background, wasting battery, network, and CPU. `collectAsStateWithLifecycle()` automatically pauses flow collection when the host `Lifecycle` drops below `Lifecycle.State.STARTED` (e.g. on backgrounding) and resumes when restarted, preventing resource leaks and crashes.",
        "best_answer": (
            "`collectAsStateWithLifecycle()` resolves a critical resource-leak defect present in standard `collectAsState()`.\n\n"
            "The standard `collectAsState()` API is tied purely to the Compose composition lifecycle. As long as a composable remains in the Slot Table, it collects the upstream Flow actively. "
            "However, when a user presses Home or switches apps, the Activity transitions to `STOPPED`, but the composition is not destroyed. "
            "Consequently, `collectAsState()` keeps collecting location updates, web sockets, or sensor streams, burning device battery, consuming cellular data, and computing recompositions that no user can see.\n\n"
            "**`collectAsStateWithLifecycle()`** (from `lifecycle-runtime-compose`) binds flow collection to the Android `LifecycleOwner`. "
            "By default, it uses `Lifecycle.State.STARTED`: it launches a coroutine to collect the flow when the UI becomes visible, and automatically **cancels the collection** when the app goes into the background (`onStop()`). "
            "When paired with `SharingStarted.WhileSubscribed(5_000)` in the ViewModel, upstream network and database subscriptions cleanly shut down."
        ),
        "deep_answer": (
            "Under the hood, `collectAsStateWithLifecycle()` uses `repeatOnLifecycle(minActiveState)`. "
            "When the host lifecycle transitions below `STARTED` (such as `STOPPED`), `repeatOnLifecycle` cancels the internal collection coroutine. "
            "When the lifecycle re-enters `STARTED` or `RESUMED`, it automatically launches a brand-new coroutine to re-subscribe to the Flow and populate the state.\n\n"
            "This behavior is especially critical when dealing with cold flows, camera frames, and database queries. "
            "Without lifecycle-aware collection, cold flows keep background workers running indefinitely, and camera frames dispatched to stopped surfaces trigger native driver crashes.\n\n"
            "In enterprise codebases, we enforce static analysis via Android Lint (`androidx.lifecycle.lint`) to flag any usage of `collectAsState()` in UI files and recommend replacement with `collectAsStateWithLifecycle()`."
        ),
        "follow_ups": [
            {
                "question": "Why is `collectAsStateWithLifecycle()` in a separate dependency rather than core compose runtime?",
                "answer": "Compose Runtime is platform-agnostic (used in Desktop, Web, and Multiplatform). The Android `Lifecycle` is platform-specific, so the integration is housed in `androidx.lifecycle:lifecycle-runtime-compose`."
            },
            {
                "question": "Can you configure `collectAsStateWithLifecycle` to collect only when `RESUMED`?",
                "answer": "Yes, by passing `minActiveState = Lifecycle.State.RESUMED`. This is useful for camera previews or high-frequency animations that should only run when the screen has active user focus."
            }
        ]
    },
    {
        "id": "COM-10",
        "arabic_explanation": (
            "ما هي تأثيرات الجوانب (Side Effects) في Compose؟ والمقارنة بين `LaunchedEffect` و `DisposableEffect` و `SideEffect` و `rememberCoroutineScope`:\n\n"
            "1. ما هو الـ Side Effect في Compose؟\n"
            "   - هو أي عملية تغير حالة خارج نطاق دالة الـ Composable، أو تتفاعل مع العالم الخارجي (مثل استدعاء كود غير Composable، أو تسجيل أحداث، أو بدء Coroutine، أو الاشتراك في BroadcastReceiver).\n"
            "   - يجب ألا تعمل هذه العمليات أبداً داخل جسم الـ Composable مباشرة لأن Recomposition قد يحدث 60 مرة في الثانية أو يُلغى فجأة.\n\n"
            "2. متى تستخدم كل أداة؟\n"
            "   - **`LaunchedEffect(key)`**: لتشغيل كود غير متزامن (`suspend` function) مرتبط بدورة حياة الـ Composable. يبدأ عند دخول الـ Composition، ويُلغى تلقائياً عند مغادرتها أو عند تغير الـ `key`.\n"
            "   - **`DisposableEffect(key)`**: للعمليات التي تتطلب تنظيفاً متماثلاً (Cleanup / Unregister) مثل تسجيل Listeners أو مراقبة Sensor أو مشغل فيديو. يفرض توفير دالة `onDispose { ... }` تُستدعى عند مغادرة الشاشة.\n"
            "   - **`SideEffect { ... }`**: لنشر حالة من Compose إلى كود خارجي غير مرتبط بـ Compose بعد **كل نجاح Recomposition كامل** (مثل إبلاغ مكتبة تحليلات خارجية أو تحديث شريط حالة النظام).\n"
            "   - **`rememberCoroutineScope()`**: للحصول على `CoroutineScope` مرتبط بـ Composition لإطلاق مهام معلقة استجابةً **لأحداث المستخدم (User Events)** مثل النقر على زر (`onClick { scope.launch { ... } }`)."
        ),
        "practical_walkthrough": (
            "أمثلة توضح متى وأين تستخدم كل أداة من أدوات الـ Side Effects الأربعة:\n"
            "```kotlin\n"
            "@Composable\n"
            "fun MediaScreen(\n"
            "    mediaId: String,\n"
            "    onCompleted: () -> Unit\n"
            ") {\n"
            "    val snackbarHostState = remember { SnackbarHostState() }\n"
            "    val coroutineScope = rememberCoroutineScope()\n"
            "\n"
            "    // 1. LaunchedEffect: جلب بيانات أو مهمة suspend مرتبطة بالـ mediaId:\n"
            "    LaunchedEffect(mediaId) {\n"
            "        analytics.trackMediaOpened(mediaId)\n"
            "    }\n"
            "\n"
            "    // 2. DisposableEffect: اشتراك في خدمة خارجية يحتاج تنظيفاً إلزامياً:\n"
            "    DisposableEffect(Unit) {\n"
            "        val listener = ScreenWakeLock.acquire()\n"
            "        onDispose {\n"
            "            listener.release() // تنظيف فوري عند مغادرة الـ Composable\n"
            "        }\n"
            "    }\n"
            "\n"
            "    // 3. SideEffect: مزامنة حالة داخلية مع كائن خارجي بعد كل Recomposition ناجح:\n"
            "    SideEffect {\n"
            "        externalTracker.lastRenderTimestamp = System.currentTimeMillis()\n"
            "    }\n"
            "\n"
            "    // 4. rememberCoroutineScope: إطلاق كوروتين في استجابة لحدث نقر المستخدم:\n"
            "    Button(onClick = {\n"
            "        coroutineScope.launch {\n"
            "            snackbarHostState.showSnackbar(\"Media saved!\")\n"
            "            onCompleted()\n"
            "        }\n"
            "    }) {\n"
            "        Text(\"Save\")\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "`LaunchedEffect` runs suspending tasks scoped to composition lifecycles and cancels them on departure or key change. `DisposableEffect` is for non-suspending setup that requires cleanup via `onDispose`. `SideEffect` runs non-suspending code after every successful recomposition. `rememberCoroutineScope` provides a scope to launch coroutines from user callbacks like `onClick`.",
        "best_answer": (
            "Side-effect handlers bridge Compose's declarative, restartable runtime with imperative external systems.\n\n"
            "1. **`LaunchedEffect(key1, ...)`**: Launches a coroutine in the composition scope upon entering the composition. If any key changes, the running coroutine is cancelled cooperatively and restarted. When leaving the composition, it is cancelled automatically. Used for async operations like fetching data or triggering animations.\n\n"
            "2. **`DisposableEffect(key1, ...)`**: Designed for non-suspending side-effects that require **mandatory cleanup**. It executes when entering composition and mandates an `onDispose { ... }` block that runs when leaving composition or before re-running due to key changes. Used for registering broadcast receivers, sensor listeners, or lifecycle observers.\n\n"
            "3. **`SideEffect`**: Executes its lambda after **every successful recomposition**. It is non-suspending and cannot be cancelled. Used to publish Compose state mutations to non-Compose external objects (such as updating an external tracking SDK or system properties).\n\n"
            "4. **`rememberCoroutineScope()`**: Creates a `CoroutineScope` bound to the calling composable's lifecycle. It is used to launch coroutines outside the composition phase—specifically inside **user callbacks and event listeners** like `Button(onClick = { scope.launch { ... } })`."
        ),
        "deep_answer": (
            "A critical pitfall in Compose architecture is calling `rememberCoroutineScope().launch { ... }` directly within the body of a Composable function. "
            "Because composables can recompose many times per second, doing this launches dozens of duplicate unmanaged coroutines, thrashing the CPU and creating race conditions. "
            "Coroutines executed directly within the composition body must strictly use `LaunchedEffect`.\n\n"
            "Under the hood, `LaunchedEffect` is implemented as a `DisposableEffect` that creates a `StandaloneCoroutine` under the hood. "
            "When the effect is disposed, its `Job.cancel()` is called immediately.\n\n"
            "`rememberCoroutineScope()` retrieves the `compositionContinuation`'s CoroutineContext, attaching a `SupervisorJob`. "
            "When the composable leaves the Slot Table, the `SupervisorJob` cancels, ensuring no child coroutine leaks into the application background."
        ),
        "follow_ups": [
            {
                "question": "Can you use `LaunchedEffect` inside an `onClick` lambda?",
                "answer": "No. `LaunchedEffect` is a `@Composable` function and can only be invoked within a Composable scope. For callbacks like `onClick`, you use a scope obtained via `rememberCoroutineScope()`."
            },
            {
                "question": "What happens if an exception is thrown inside a `SideEffect` block?",
                "answer": "Because `SideEffect` executes synchronously during the commit phase of the composition pass, an unhandled exception will crash the composition process and propagate as an unhandled runtime exception."
            }
        ]
    },
    {
        "id": "COM-11",
        "arabic_explanation": (
            "المقارنة بين `LaunchedEffect(Unit)` و `LaunchedEffect(key)` وكيف يؤثر اختيار الـ Key على الأداء والصحة:\n\n"
            "1. كيف تعمل `LaunchedEffect(Unit)` أو `LaunchedEffect(true)`؟\n"
            "   - تمرير قيمة ثابتة لا تتغير أبداً (مثل `Unit` أو `true`) يعني أن الـ Key **لن يتغير أبداً** طوال فترة بقاء هذا الـ Composable في شجرة الـ Composition.\n"
            "   - النتيجة: يعمل الكود **مرة واحدة فقط (Run-Once)** عند دخول الـ Composable لأول مرة، ولا يُعاد تشغيله أثناء أي Recomposition، ويُلغى فقط عند مغادرة الشاشة بالكامل.\n"
            "   - **الاستخدام المثالي**: بدء أنيميشن ابتدائي لمرة واحدة، أو استدعاء حدث لمرة واحدة للشاشة.\n\n"
            "2. كيف تعمل `LaunchedEffect(key)`؟\n"
            "   - عندما يتم تمرير متغير كـ Key (مثل `userId` أو `query` أو `filter`):\n"
            "   - في كل Recomposition، يقارن Compose قيمة الـ Key الحالية بالقيمة السابقة عبر `equals()`.\n"
            "   - إذا تغيرت القيمة: يقوم Compose **بإلغاء الكوروتين الجاري فوراً (Cancel Job)** ويبدأ كوروتين جديد بالقيمة الجديدة!\n"
            "   - **الاستخدام المثالي**: البحث اللحظي مع الكتابة (Debounced search)، وإعادة تحميل البيانات عند تغيير الـ ID المختار.\n\n"
            "3. أخطاء شائعة (Common Traps):\n"
            "   - استخدام `LaunchedEffect(Unit)` لجلب بيانات تعتمد على بارامتر `id` متغير: إذا تغير الـ `id` لاحقاً، لن يُعاد جلب البيانات ويظل المحتوى قديماً!\n"
            "   - تمرير Key يتغير في كل فريم (مثل قيمة سكرول عشوائية): يؤدي إلى إلغاء وإعادة إطلاق الكوروتين 60 مرة في الثانية وإجهاد المعالج."
        ),
        "practical_walkthrough": (
            "مقارنة عملية توضح متى نستخدم Unit ومتى نستخدم Dynamic Key:\n"
            "```kotlin\n"
            "// ❌ خطأ: استخدام Unit مع بارامتر ديناميكي؛ عند اختيار مستخدم آخر لن يتم تحديث البيانات:\n"
            "@Composable\n"
            "fun BadUserProfile(userId: String) {\n"
            "    LaunchedEffect(Unit) {\n"
            "        // 💥 إذا تغير userId لن يعمل هذا الكود مرة ثانية!\n"
            "        loadUserData(userId)\n"
            "    }\n"
            "}\n"
            "\n"
            "// ✅ الكود السليم: تمرير userId كـ Key؛ عند تغير الـ ID يُلغى الطلب القديم ويبدأ الجديد:\n"
            "@Composable\n"
            "fun GoodUserProfile(userId: String) {\n"
            "    LaunchedEffect(userId) {\n"
            "        // يُلغى الطلب السابق ويبدأ طلب المستخدم الجديد فوراً:\n"
            "        loadUserData(userId)\n"
            "    }\n"
            "}\n"
            "\n"
            "// ✅ استخدام سليم لـ Unit: مهام لا تعتمد على أي متغير وتعمل مرة واحدة فقط:\n"
            "@Composable\n"
            "fun SplashScreen(onTimeout: () -> Unit) {\n"
            "    LaunchedEffect(Unit) {\n"
            "        delay(2000)\n"
            "        onTimeout()\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "`LaunchedEffect(Unit)` executes its coroutine once upon entering composition and cancels it only when leaving composition. `LaunchedEffect(key)` executes on entry and automatically cancels and restarts its coroutine whenever `key` changes (via `equals()`). Choosing the wrong key leads to either stale data or thrashing restarts.",
        "best_answer": (
            "The difference between `LaunchedEffect(Unit)` and `LaunchedEffect(key)` lies in restart semantics based on key equality.\n\n"
            "1. **`LaunchedEffect(Unit)`**: Because `Unit` is a constant singleton, its key never changes. The coroutine launches when the composable initially enters the composition and remains running until the composable leaves the composition tree. It is ideal for fire-and-forget one-off operations that are independent of changing inputs, such as playing a screen-entry sound or showing an introductory prompt.\n\n"
            "2. **`LaunchedEffect(key)`**: Takes one or more dynamic keys (e.g. `query`, `filterId`). On every recomposition pass, Compose compares current keys against their previous instances using `equals()`. If any key has changed, Compose automatically cancels the running coroutine job cooperatively and launches a new one with the updated values. This is essential for operations like dynamic querying, pagination, or debouncing input."
        ),
        "deep_answer": (
            "A dangerous production bug occurs when developers use `LaunchedEffect(Unit)` while capturing changing parameters inside its lambda closure. "
            "Because the coroutine never restarts, the captured closure holds **stale references** to variables from the initial composition pass. "
            "If those variables must not restart the effect, developers should use `rememberUpdatedState` to read the freshest value without restarting the coroutine.\n\n"
            "Conversely, passing unstable or constantly changing keys (like `currentTimeMillis()` or non-memoized objects) triggers **restart thrashing**: canceling and spawning hundreds of coroutines per second, pegging the CPU and dropping frames.\n\n"
            "If an effect depends on multiple inputs, Compose supports vararg keys: `LaunchedEffect(key1, key2)`. The effect restarts if either key changes."
        ),
        "follow_ups": [
            {
                "question": "What is the consequence of passing an object with broken `equals()` as a key in `LaunchedEffect`?",
                "answer": "If `equals()` always returns false (or defaults to identity equality for unmemoized instances), `LaunchedEffect` will cancel and restart on every single recomposition, causing infinite loops and UI thrashing."
            },
            {
                "question": "How do you access the latest value of a changing callback inside `LaunchedEffect(Unit)`?",
                "answer": "Wrap the callback in `val currentCallback by rememberUpdatedState(onTimeout)`. The effect won't restart, but invoking `currentCallback()` accesses the latest callback passed from the parent."
            }
        ]
    },
    {
        "id": "COM-12",
        "arabic_explanation": (
            "شرح أدوات التعامل المتقدم مع الحالة: `rememberUpdatedState` و `derivedStateOf` و `snapshotFlow`:\n\n"
            "1. دالة `rememberUpdatedState`:\n"
            "   - **المشكلة**: لديك دالة كولباك أو قيمة تتغير مع كل Recomposition، لكن لديك `LaunchedEffect(Unit)` طويل الأجل لا تريد إعادة تشغيله كلما تغيرت القيمة!\n"
            "   - **الحل**: `rememberUpdatedState(newValue)` تحتفظ بمرجع للحالة الأحدث دون التسبب في إعادة تشغيل الـ Effect.\n"
            "   - مفيدة جداً مع الـ Timers والـ Splash Screens ومستمعي الأحداث.\n\n"
            "2. دالة `derivedStateOf { ... }`:\n"
            "   - **المشكلة**: لديك حالة سريعة التغير جداً (مثل موضع السكرول `scrollState.value` الذي يتغير في كل بكسل)، ولكن الواجهة تحتاج فقط لمعرفة نتيجة حسابية بسيطة (مثل `isScrolledPastHero = scrollOffset > 200.dp`).\n"
            "   - **الحل**: `derivedStateOf` تعمل كـ **ممتص صدمات (Buffer / Dampener)**؛ فهي تراقب التغيرات السريعة ولكنها لا تطلق Recomposition إلا عندما تتغير **القيمة الناتجة** (من `false` إلى `true` أو العكس)، مما يوفر آلاف عمليات الـ Recomposition غير الضرورية!\n\n"
            "3. دالة `snapshotFlow { ... }`:\n"
            "   - **الهدف**: الجسر بين عالم Compose وعالم Kotlin Coroutines Flow.\n"
            "   - تحول أي قراءة لـ Compose State إلى `Flow<T>` بارد (Cold Flow) ينبعث منه عنصر كلما تغيرت قيمة الـ State.\n"
            "   - تمكنك من استخدام عوامل تشغيل الـ Flow القوية مثل `debounce()`, `filter()`, `distinctUntilChanged()` داخل Compose."
        ),
        "practical_walkthrough": (
            "أمثلة عملية واقعية توضح استخدام كل أداة من الأدوات الثلاث:\n"
            "```kotlin\n"
            "@Composable\n"
            "fun AdvancedComposeScreen(\n"
            "    onTimeout: () -> Unit,\n"
            "    listState: LazyListState = rememberLazyListState()\n"
            ") {\n"
            "    // 1. rememberUpdatedState: قراءة أحدث نسخة من onTimeout دون إعادة تشغيل الـ timer:\n"
            "    val currentOnTimeout by rememberUpdatedState(onTimeout)\n"
            "    LaunchedEffect(Unit) {\n"
            "        delay(5000)\n"
            "        currentOnTimeout() // يستدعي أحدث دالة مررتها الواجهة بأمان\n"
            "    }\n"
            "\n"
            "    // 2. derivedStateOf: منع Recomposition في كل بكسل سكرول؛ يُعاد التركيب فقط عند تغير النتيجة:\n"
            "    val showScrollToTopButton by remember {\n"
            "        derivedStateOf { listState.firstVisibleItemIndex > 0 }\n"
            "    }\n"
            "\n"
            "    // 3. snapshotFlow: تحويل حالة السكرول إلى Flow واستخدام debounce للتحليلات:\n"
            "    LaunchedEffect(listState) {\n"
            "        snapshotFlow { listState.firstVisibleItemIndex }\n"
            "            .distinctUntilChanged()\n"
            "            .collect { index ->\n"
            "                AnalyticsTracker.logScrollIndex(index)\n"
            "            }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "`rememberUpdatedState` captures the latest value of a parameter inside long-running effects without restarting them. `derivedStateOf` creates a calculated state that dampens high-frequency state updates, recomposing only when the computed output actually changes. `snapshotFlow` bridges Compose state to Kotlin Flow, allowing operators like `debounce` and `filter`.",
        "best_answer": (
            "These three APIs represent advanced Compose state coordination tools:\n\n"
            "1. **`rememberUpdatedState(value)`**: Solves the *stale closure* problem in long-running effects. When a `LaunchedEffect(Unit)` or `DisposableEffect` must access a changing parameter or lambda without restarting the effect, `rememberUpdatedState` updates an internal state reference synchronously. The effect reads the newest value upon execution without dropping or re-triggering its lifecycle.\n\n"
            "2. **`derivedStateOf { ... }`**: Functions as a **state dampener**. When an input state mutates rapidly (such as `listState.firstVisibleItemScrollOffset` changing every single frame), reading that raw state directly in UI triggers hundreds of recompositions. Wrapping the calculation in `derivedStateOf { offset > 100 }` ensures observers only recompose when the *calculated result* transitions (e.g. from `false` to `true`).\n\n"
            "3. **`snapshotFlow { ... }`**: Bridges Compose's snapshot state into a cold Kotlin `Flow`. It runs the lambda whenever a read snapshot state mutates, emitting the result downstream. This unlocks reactive coroutine operators like `debounce()`, `sample()`, or `filter()` directly on UI state."
        ),
        "deep_answer": (
            "Under the hood, `derivedStateOf` registers a dynamic dependency set in the Snapshot system. "
            "It records every snapshot state read during the calculation block. "
            "When any dependent state mutates, `derivedStateOf` re-evaluates the block inside a snapshot; if the result is structurally equal (`equals()`) to the cached result, it silently ignores the update and suppresses recomposition notifications down the tree.\n\n"
            "A critical misuse to avoid is wrapping simple static computations inside `derivedStateOf`. "
            "For instance, `val fullName = remember(first, last) { derivedStateOf { \"$first $last\" } }` is an anti-pattern. "
            "`derivedStateOf` has allocation and tracking overhead; it is only beneficial when the **input state changes much more frequently than the output state**.\n\n"
            "`snapshotFlow` relies on `Snapshot.registerApplyObserver`. When global snapshots commit, it compares emissions using structural equality, guaranteeing that downstream flow collectors only receive changes that actually alter data."
        ),
        "follow_ups": [
            {
                "question": "When should you NOT use `derivedStateOf`?",
                "answer": "When the input state changes at the exact same frequency as the output (e.g. formatting a name from two text states). Standard `remember(key1, key2) { ... }` is faster and avoids snapshot observer overhead."
            },
            {
                "question": "Can `snapshotFlow` emit duplicate values?",
                "answer": "No. `snapshotFlow` internally applies `distinctUntilChanged()`, so consecutive identical values evaluated from the snapshot read block are discarded automatically."
            }
        ]
    },
    {
        "id": "COM-13",
        "arabic_explanation": (
            "كيفية التعامل الصحيح مع أحداث المرة الواحدة (One-off Events) مثل الـ Snackbar والتنقل (Navigation) والـ Callbacks في Jetpack Compose:\n\n"
            "1. معضلة أحداث المرة الواحدة (Single-Event Anti-Pattern):\n"
            "   - في السابق، كان المطورون يضعون `SharedFlow` أو `Channel` أو `SingleLiveEvent` لإرسال حدث مثل `ShowToast` أو `NavigateToHome`.\n"
            "   - المشكلة: الـ Channels قد تفقد الأحداث إذا حدث Configuration Change أثناء الإرسال، أو قد تعيد تنفيذ الحدث مرتين عند إعادة التدوير (Double Navigation)!\n\n"
            "2. التوجيه الرسمي الحديث من Google (State-Based Events):\n"
            "   - يجب تمثيل رسائل التنبيه والـ Snackbars **كجزء من الـ UI State نفسها**!\n"
            "   - يتم وضع كائن مثل `userMessage: UserMessage?` داخل الـ `UiState`.\n"
            "   - عندما يقرأ الـ Composable هذه الرسالة، يعرض الـ Snackbar، ثم يُرسل فورياً حدثاً للـ ViewModel يقول: `onMessageShown(messageId)` لتصفير القيمة إلى `null`.\n"
            "   - هذا يضمن الحتمية التامة؛ فحتى لو تدوّرت الشاشة أو ماتت العملية، يُعرف بالضبط هل عُرضت الرسالة أم لا.\n\n"
            "3. أحداث التنقل (Navigation Events):\n"
            "   - التنقل استجابةً لضغط المستخدم المباشر يجب أن يتم في الـ UI Layer فوراً عبر Lambdas (`onClick = { onNavigateToDetails(itemId) }`).\n"
            "   - إذا كان التنقل مشروطاً بنتيجة عملية في السيرفر (مثل تسجيل دخول ناجح)، يتم تمثيل حالة الوجهة في الـ ViewModel وعند الوصول لحالة النجاح يُستدعى التنقل ويُفرغ الحدث."
        ),
        "practical_walkthrough": (
            "النمط القياسي لعرض الـ Snackbar كجزء من الحالة وتصفيره بعد العرض:\n"
            "```kotlin\n"
            "// 1. تمثيل الرسالة في الـ UiState:\n"
            "data class EditProfileUiState(\n"
            "    val isLoading: Boolean = false,\n"
            "    val userMessage: String? = null // رسالة المرة الواحدة كـ State قابلة للإلغاء\n"
            ")\n"
            "\n"
            "// 2. معالجة الرسالة في Compose باستخدام LaunchedEffect وتصفيرها فوراً:\n"
            "@Composable\n"
            "fun EditProfileScreen(\n"
            "    viewModel: EditProfileViewModel,\n"
            "    snackbarHostState: SnackbarHostState = remember { SnackbarHostState() }\n"
            ") {\n"
            "    val uiState by viewModel.uiState.collectAsStateWithLifecycle()\n"
            "\n"
            "    // مراقبة userMessage؛ عند توفره يتم عرضه ثم إبلاغ الـ ViewModel بتصفيره:\n"
            "    LaunchedEffect(uiState.userMessage) {\n"
            "        uiState.userMessage?.let { message ->\n"
            "            snackbarHostState.showSnackbar(message)\n"
            "            viewModel.onUserMessageShown() // تصفير الرسالة لمنع تكرارها عند التدوير!\n"
            "        }\n"
            "    }\n"
            "\n"
            "    Scaffold(snackbarHost = { SnackbarHost(snackbarHostState) }) {\n"
            "        ProfileContent(uiState)\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Model one-off UI events (like Snackbars) as consumable state properties inside the UI state, displaying them via `LaunchedEffect(userMessage)` and immediately calling an `onMessageDismissed()` event to clear the state. Navigation triggered by user input should be handled directly in the UI via callbacks, while business-driven navigation is driven by explicit state transitions.",
        "best_answer": (
            "Handling one-off events in Jetpack Compose requires transitioning away from legacy event-bus and channel antipatterns toward state-driven architectures.\n\n"
            "1. **Snackbar and Transient Messages as State**: Rather than pushing side-effect events through `Channel` or `SharedFlow`, the modern official pattern models messages as state: `userMessage: UserMessage?` inside `ScreenUiState`. In Compose, a `LaunchedEffect(uiState.userMessage)` observes this field. When non-null, it invokes `snackbarHostState.showSnackbar(message)`, and immediately fires a callback `viewModel.onMessageShown(id)` to reset the state to `null`. This prevents missed messages or duplicate displays upon screen rotation.\n\n"
            "2. **User-Driven Navigation**: Clicks and direct user navigation (e.g. tapping an item) should be handled immediately in the UI layer through hoisted lambda callbacks (`onItemClick: (Id) -> Unit`), directly invoking the `NavController`.\n\n"
            "3. **Business-Driven Navigation**: When navigation depends on business outcomes (e.g. successful authentication), the ViewModel emits a distinct terminal state (e.g. `AuthState.Authenticated`), which the UI observes to execute navigation."
        ),
        "deep_answer": (
            "Why did Google advise against using `Channel` or `SharedFlow` for one-off UI events in Compose? "
            "Channels buffer events imperatively. If an event is posted while the UI is transitioning lifecycles (e.g. during an Activity recreation or rotation), the collector may either drop the event or consume it before the new composition is ready, resulting in dropped Snackbars or phantom double navigations.\n\n"
            "By embedding events in the immutable `UiState`, state restoration is guaranteed: if the screen dies and is recreated via `SavedStateHandle`, the pending message is preserved and displayed reliably.\n\n"
            "For navigation specifically, to prevent rapid double-clicks from pushing two duplicate screens onto the backstack, we either guard navigations with a boolean gate or debounce click modifiers, and verify that the destination is not already the top destination on the NavController backstack."
        ),
        "follow_ups": [
            {
                "question": "What happens if a user rotates the screen while a Snackbar is currently being displayed?",
                "answer": "If modeled as state cleared only upon `showSnackbar()` completion, the recreated screen will simply re-display the active message. If cleared immediately before display, the rotation drops it gracefully without crashing."
            },
            {
                "question": "How do you prevent rapid double-taps on navigation buttons in Compose?",
                "answer": "By using a single-click modifier that checks `SystemClock.elapsedRealtime()`, or checking that `navController.currentBackStackEntry?.destination?.route` matches the expected source route before navigating."
            }
        ]
    },
    {
        "id": "COM-14",
        "arabic_explanation": (
            "أهمية المفاتيح المستقرة (`keys`) وأنواع المحتوى (`contentType`) في قوائم `LazyColumn` و `LazyRow`:\n\n"
            "1. المشكلة عند عدم استخدام `key` في `LazyColumn`:\n"
            "   - افتراضياً، إذا لم تحدد `key`، يستخدم Compose **موضع العنصر (Item Position/Index)** كمفتاح افتراضي.\n"
            "   - إذا أضفت عنصراً في بداية القائمة أو قمت بترتيب العناصر:\n"
            "     * يتغير موضع كل العناصر التالية (العنصر 0 أصبح 1، و 1 أصبح 2).\n"
            "     * يعتقد Compose أن كل عنصر قد تغير بالكامل، فيقوم بـ **إعادة تركيب (Recomposition) وإعادة تهيئة كل العناصر**!\n"
            "     * تفقد العناصر حالتها الداخلية (مثل حالة التمرير، أو النص المكتوب داخل العنصر، أو الرسوم المتحركة).\n\n"
            "2. دور المفاتيح المستقرة (`key = { item.id }`):\n"
            "   - يمنح كل عنصر هوية فريدة وثابتة (Semantic Identity).\n"
            "   - عندما تتغير القائمة، يستطيع Compose معرفة أي عنصر تحرك بدقة، فيقوم بنقله بسلاسة وتخطي إعادة تركيبه بالكامل (`Smart Skipping`).\n"
            "   - يدعم خاصية الرسوم المتحركة التلقائية لحركة العناصر عبر `Modifier.animateItemPlacement()`.\n\n"
            "3. دور نوع المحتوى (`contentType`):\n"
            "   - في القوائم غير المتجانسة (Heterogeneous Lists التي تحتوي على رؤوس أقسام Headers، بطاقات إعلانات Ads، وبطاقات عادية Cards):\n"
            "   - يخبر `contentType` محرك Compose بنوع الـ Layout حتى يقوم **بإعادة تدوير الـ Composition Slots (Composition Recycling)** بين العناصر المتشابهة في التركيب بدلاً من التدمير وإعادة البناء من الصفر."
        ),
        "practical_walkthrough": (
            "الاستخدام الاحترافي لـ key و contentType في LazyColumn:\n"
            "```kotlin\n"
            "sealed interface FeedItem {\n"
            "    val id: String\n"
            "    data class Header(override val id: String, val title: String) : FeedItem\n"
            "    data class Post(override val id: String, val text: String, val author: String) : FeedItem\n"
            "    data class Ad(override val id: String, val bannerUrl: String) : FeedItem\n"
            "}\n"
            "\n"
            "@Composable\n"
            "fun FeedList(items: ImmutableList<FeedItem>, modifier: Modifier = Modifier) {\n"
            "    LazyColumn(modifier = modifier) {\n"
            "        items(\n"
            "            items = items,\n"
            "            key = { item -> item.id }, // مفتاح مستقر فريد يحمي الحالة ويسرع السكرول\n"
            "            contentType = { item ->\n"
            "                // تصنيف نوع المحتوى لإعادة تدوير الـ Slots بين العناصر المتشابهة:\n"
            "                when (item) {\n"
            "                    is FeedItem.Header -> \"HEADER_TYPE\"\n"
            "                    is FeedItem.Post -> \"POST_TYPE\"\n"
            "                    is FeedItem.Ad -> \"AD_TYPE\"\n"
            "                }\n"
            "            }\n"
            "        ) { item ->\n"
            "            when (item) {\n"
            "                is FeedItem.Header -> HeaderView(item)\n"
            "                is FeedItem.Post -> PostCard(item)\n"
            "                is FeedItem.Ad -> AdBanner(item)\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "In `LazyColumn`, specifying a unique `key` anchors each item to its data ID rather than its index position, preserving item state across insertions/deletions and enabling item placement animations. Providing `contentType` allows Compose to recycle slot table compositions between items with matching layouts, reducing composition overhead.",
        "best_answer": (
            "In `LazyColumn` and `LazyRow`, configuring `key` and `contentType` is vital for fluid 120fps scrolling and correct state preservation.\n\n"
            "1. **Stable Keys (`key`)**: By default, Compose uses item index as the implicit key. If an item is prepended at index 0, every existing item shifts down, causing Compose to believe all items mutated and forcing a recomposition of the entire visible viewport. Furthermore, item-level state (like text field inputs or expanded accordions) shifts onto the wrong items! Providing a persistent, unique identifier (`key = { it.id }`) preserves item identity, retains local state correctly across reorderings, and powers smooth animations via `Modifier.animateItem()`.\n\n"
            "2. **Content Types (`contentType`)**: In heterogeneous lists featuring multiple visual layouts (e.g. Header, Card, VideoPlayer, AdBanner), Compose uses `contentType` to group structurally similar items. This enables Compose to recycle Slot Table structures exclusively among items of the same type, drastically cutting down allocation overhead and layout measurement passes during rapid fling scrolls."
        ),
        "deep_answer": (
            "Under the hood, keys in `LazyLayout` must be parcelable or persistable in Android bundles because Compose uses them to retain `rememberSaveable` state per item in the `LazyLayoutItemContentFactory`. "
            "If an invalid non-unique key is used, Compose throws an `IllegalArgumentException` indicating duplicate keys within the composition.\n\n"
            "Without `contentType`, when a user scrolls and an AdBanner leaves the screen while a simple PostCard enters, Compose attempts to reuse the slot composition of the AdBanner for the PostCard. "
            "Because the composable structures mismatch completely, Compose must discard the slot group and execute a full new composition from scratch. "
            "With `contentType`, Compose preserves separate recycling pools for each layout signature, matching the recycling efficiency of `RecyclerView.getItemViewType()`.\n\n"
            "In Macrobenchmark scroll tests, adding both `key` and `contentType` to complex feeds typically slashes frame drop rates during rapid scrolls by 40-60%."
        ),
        "follow_ups": [
            {
                "question": "What happens if two items in a LazyColumn produce the same key?",
                "answer": "Compose crashes immediately at runtime with an `IllegalArgumentException: Key '...' was already used. If you are using LazyColumn, you must ensure that all keys are unique."
            },
            {
                "question": "Can you use item index as a key in `LazyColumn`?",
                "answer": "Specifying index explicitly is redundant because it is already the default behavior. It fails to preserve state during insertions, deletions, and sorting, and should be avoided in dynamic lists."
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

    for item in COM_08_14:
        by_id[item["id"]] = item

    output = [by_id[k] for k in sorted(by_id.keys())]
    DATA_FILE.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {DATA_FILE} with questions COM-08 to COM-14. Total questions: {len(output)}")

if __name__ == "__main__":
    main()
