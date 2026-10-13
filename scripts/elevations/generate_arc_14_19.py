#!/usr/bin/env python3
"""Generator for ARC-14 through ARC-19 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "arc.json"

ARC_14_19 = [
    {
        "id": "ARC-14",
        "arabic_explanation": (
            "لماذا يجب ألا تتصل طبقة واجهة المستخدم (UI Layer) بمكتبات Retrofit أو Room DAOs مباشرة؟\n\n"
            "1. مخاطر الارتباط المباشر (Tight Coupling):\n"
            "   - إذا كان الـ ViewModel أو الـ Composable يستدعي Retrofit أو Room مباشرة، فإنه يصبح مرتبطاً بشكل وثيق (Coupled) بتفاصيل الـ Networking وقواعد البيانات المحلية.\n   - أي تعديل في الـ Backend API (مثل تغيير مسار Endpoint، أو إضافة Headers، أو تعديل شكل الـ JSON) يجبرك على تعديل كود الـ UI والـ ViewModel مباشرة، مما يكسر مبدأ Single Responsibility.\n\n"
            "2. انهيار قابلية الاختبار (Destruction of Testability):\n"
            "   - لا يمكنك كتابة Unit Test نظيف وسريع للـ ViewModel على الـ JVM دون استحضار أدوات Mocking معقدة للـ HTTP Client (مثل MockWebServer) أو SQLite In-Memory Database، مما يجعل الاختبارات بطيئة وهشة.\n\n"
            "3. غياب استراتيجية الكاش والمصدر الوحيد للحقيقة (No Caching / Offline Support):\n   - استدعاء الشبكة مباشرة يحرم التطبيق من وجود وسيط ينظم حفظ البيانات محلياً؛ فلن يعمل التطبيق دون اتصال بالإنترنت (No Offline-first).\n   - الـ Repository هو الذي يوحد إدارة الـ Caching والـ Retries والـ Error Mapping بعيداً عن أعين الـ UI."
        ),
        "practical_walkthrough": (
            "مقارنة بين استدعاء مباشر كارثي واستخدام الـ Repository Pattern:\n"
            "```kotlin\n"
            "// ❌ استدعاء مباشر كارثي: ViewModel يتصل بـ Retrofit مباشرة ويعالج تفاصيل HTTP:\n"
            "class BadUserViewModel(private val api: RetrofitUserApi) : ViewModel() {\n"
            "    fun loadUser() {\n"
            "        viewModelScope.launch {\n"
            "            val response = api.getUserProfile() // تسريب تفاصيل الشبكة إلى الـ UI!\n"
            "            if (response.isSuccessful) {\n"
            "                _uiState.value = response.body()!!.toUi()\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "}\n"
            "\n"
            "// ✅ كود سليم ومعزول: ViewModel يتصل بـ Repository وسيط يوفر بيانات نظيفة:\n"
            "class GoodUserViewModel @Inject constructor(\n"
            "    private val userRepository: UserRepository // عقد وسيط مجرد\n"
            ") : ViewModel() {\n"
            "    val uiState: StateFlow<UserUiState> = userRepository.observeUser()\n"
            "        .map { UserUiState.Success(it) }\n"
            "        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), UserUiState.Loading)\n"
            "}\n"
            "```"
        ),
        "quick_answer": "UI calling Retrofit or Room directly tightly couples the presentation layer to network/database implementation details, destroys JVM unit testability, eliminates offline caching strategies, and duplicates error-handling logic across screens. A Repository must mediate to enforce SSOT.",
        "best_answer": (
            "Bypassing the data/domain layer to call Retrofit or Room DAOs directly from the UI layer is a critical architectural violation.\n\n"
            "1. **Tight Coupling to Infrastructure Details**: The UI layer's sole concern is rendering state and capturing user intent. Calling Retrofit couples the UI to HTTP verbs, status codes, query parameters, and JSON parsing. Calling Room couples it to SQL tables, migrations, and database cursors. Any backend schema or database change directly breaks presentation code.\n\n"
            "2. **Destruction of Unit Testability**: If a ViewModel interacts directly with Retrofit or Room, testing its presentation logic requires complex mock servers (MockWebServer) or SQLite fixtures. With a Repository abstraction, the ViewModel is tested via a lightweight Fake Repository in sub-second JVM tests.\n\n"
            "3. **Loss of Caching and Offline Resilience**: A direct API call in the UI provides zero offline capability. The Repository pattern is where caching policies, SQLite write-through caching, and network retries live, presenting a cohesive Single Source of Truth to the UI."
        ),
        "deep_answer": (
            "Under the hood, direct data source calls also lead to **threading and main-safety violations**. "
            "While Room and Retrofit support suspend functions, direct invocation often leads developers to execute database transactions or large JSON deserializations directly in UI scopes without appropriate dispatcher switches.\n\n"
            "Furthermore, direct calls create **duplicate business logic**. "
            "If Screen A and Screen B both query `UserApi.getProfile()`, both ViewModels must independently handle token refresh logic, HTTP 401 handling, DTO mapping, and error messages. "
            "Centralizing this within `UserRepository` guarantees that network resilience logic is written and tested once.\n\n"
            "In enterprise codebases, we enforce this boundary via Gradle modularization and static analysis: the `:ui` module does not have a dependency on Retrofit, OkHttp, or Room libraries, making direct invocation impossible at compile time."
        ),
        "follow_ups": [
            {
                "question": "Can a ViewModel call a Room DAO directly if the app has no network layer?",
                "answer": "Even in an offline-only app, a Repository is still recommended. It abstracts SQLite details, handles mapping from database entities to UI/Domain models, and manages transactions cleanly."
            },
            {
                "question": "How do you enforce that the UI layer cannot import Retrofit?",
                "answer": "By splitting Gradle modules: `:feature:home` depends on `:core:domain` or `:core:data-api`, but has no dependency on `:core:network` or `com.squareup.retrofit2`."
            }
        ]
    },
    {
        "id": "ARC-15",
        "arabic_explanation": (
            "متى تقوم بإنشاء واجهات (Interfaces)، ومتى تكون الكلاسات الحقيقية الملموسة (Concrete Implementations) كافية دون إفراط؟\n\n"
            "1. متى يكون الـ Interface واجباً ومبرراً بنسبة 100%؟\n   - **تطبيق مبدأ Inversion of Control (عكس التبعية)**: في حدود الـ Clean Architecture؛ مثل `UserRepository` في الـ Domain والـ `UserRepositoryImpl` في الـ Data، لمنع الـ Domain من الاعتماد على مكتبات خارجية.\n   - **تعدد طرق التنفيذ الفعلية (Polymorphism / Multiple Implementations)**: مثل `PaymentProcessor` الذي يمتلك تنفيذين حقيقيين: `StripeProcessor` و `GooglePayProcessor`.\n   - **عزل المكونات الخارجية صعبة الاختبار (Flaky / Native / Third-Party)**: مثل خدمات الموقع `LocationProvider`، مشغل الصوت `MediaPlayer`، أو مستشعرات البلوتوث؛ حيث تحتاج لـ `FakeLocationProvider` للاختبار على الـ JVM.\n\n"
            "2. متى تكون الكلاسات الملموسة (Concrete Classes) كافية ويفضل تجنب الـ Interfaces؟\n   - **كلاسات الـ UseCases الفردية**: الـ `PlaceOrderUseCase` هو كلاس كوتلن نقي 100% ليس له سوى تنفيذ وحيد؛ إنشاء `interface PlaceOrderUseCase` ومعه `PlaceOrderUseCaseImpl` هو تكرار عقيم وبويلربليت لا فائدة منه (Interface-itis).\n   - **الـ ViewModels**: لا تحتاج إطلاقاً لـ Interface لأن الـ Composable أو الـ Fragment يستهلكها كـ Concrete Holder.\n   - **خدمات البيانات الداخلية غير المعقدة** التي ليس لها سوى تطبيق واحد."
        ),
        "practical_walkthrough": (
            "المقارنة بين استخدام مبرر لـ Interface واستخدام غير مبرر (Boilerplate):\n"
            "```kotlin\n"
            "// ❌ INTERFACE-ITIS (بويلربليت غير مبرر): كلاس نقي له تطبيق وحيد:\n"
            "interface CalculateDiscountUseCase {\n"
            "    fun execute(order: Order): Long\n"
            "}\n"
            "class CalculateDiscountUseCaseImpl : CalculateDiscountUseCase {\n"
            "    override fun execute(order: Order): Long = (order.total * 0.1).toLong()\n"
            "}\n"
            "\n"
            "// ✅ الكود الأبسط والأنظف: UseCase كـ Concrete Class مباشرة:\n"
            "class CalculateDiscountUseCase {\n"
            "    operator fun invoke(order: Order): Long = (order.total * 0.1).toLong()\n"
            "}\n"
            "\n"
            "// ✅ استخدام مبرر وممتاز للـ Interface: عزل خدمة خارجية وتعدد التنفيذات:\n"
            "interface AnalyticsTracker {\n"
            "    fun track(event: String, params: Map<String, Any> = emptyMap())\n"
            "}\n"
            "class FirebaseAnalyticsTracker : AnalyticsTracker { ... }\n"
            "class DebugConsoleAnalyticsTracker : AnalyticsTracker { ... } // مفيد للـ Debug\n"
            "class FakeAnalyticsTracker : AnalyticsTracker { ... } // مفيد للـ Unit Tests\n"
            "```"
        ),
        "quick_answer": "Introduce interfaces at architectural boundaries to invert dependencies (e.g. Domain Repository interfaces), when multiple production implementations exist (e.g. Stripe vs Google Pay), or to abstract volatile external systems (e.g. GPS, Bluetooth). Concrete classes are sufficient for single-implementation Use Cases and ViewModels.",
        "best_answer": (
            "Deciding when to introduce interfaces distinguishes pragmatic senior engineers from dogmatic architects suffering from 'Interface-itis'.\n\n"
            "1. **When Interfaces are Genuinely Necessary**:\n"
            "   - **Inversion of Control across Boundaries**: The quintessential Clean Architecture contract: the Domain layer declares `interface OrderRepository`, and the Data layer implements it, keeping the Domain pure.\n"
            "   - **Multiple Real Implementations**: When the system genuinely supports swappable implementations (e.g. `interface PaymentGateway` implemented by `StripeGateway` and `PayPalGateway`).\n"
            "   - **Abstracting Flaky External Systems**: Wrapping hardware, system frameworks, or third-party SDKs (`LocationManager`, `BluetoothScanner`, `BiometricAuth`) behind an interface allows creating high-speed `Fake` implementations for JVM unit testing.\n\n"
            "2. **When Concrete Classes are Sufficient**:\n"
            "   - **Use Cases (Interactors)**: A Use Case encapsulates a single business scenario in pure Kotlin. Creating `interface CheckoutUseCase` paired with `CheckoutUseCaseImpl` is 100% redundant boilerplate.\n"
            "   - **ViewModels**: ViewModels have a single implementation bound to UI state.\n"
            "   - **Internal Utilities**: Helper classes and mappers."
        ),
        "deep_answer": (
            "A legacy justification for interfaces was testability in Java: developers couldn't mock concrete classes without interfaces. "
            "In modern Kotlin, with MockK and Mockito-inline, mocking concrete classes is trivial. "
            "More importantly, modern testing best practices advocate using **Fakes over Mocks**. "
            "For a pure Kotlin Use Case, you don't even need a mock or a fake—you instantiate the concrete class directly in your test!\n\n"
            "In large multi-module codebases, interfaces enable **Compilation Avoidance**. "
            "If an interface lives in an API module (`:feature:chat:api`) and its implementation lives in an implementation module (`:feature:chat:impl`), changing the internal implementation logic does not invalidate or recompile the dozens of downstream modules that only depend on the API module.\n\n"
            "We adhere to the Rule of Three: do not abstract with an interface until you have two distinct implementations or a strict architectural dependency boundary."
        ),
        "follow_ups": [
            {
                "question": "What is 'Interface-itis'?",
                "answer": "The dogmatic anti-pattern of creating a 1-to-1 interface for every single class in an application (e.g. `Foo` and `FooImpl`), which doubles file counts and maintenance overhead without providing any polymorphism or decoupling value."
            },
            {
                "question": "How do API/Impl module splits leverage interfaces for faster build times?",
                "answer": "Consuming modules depend only on the stable API module containing interfaces. When code inside the Impl module changes, Gradle skips recompiling the consuming modules because public ABI signatures haven't changed."
            }
        ]
    },
    {
        "id": "ARC-16",
        "arabic_explanation": (
            "المقارنة الهيكلية بين تنظيم الحزم حسب الطبقة (Package-by-Layer) وحسب الميزة (Package-by-Feature):\n\n"
            "1. تنظيم الحزم حسب الطبقة (Package-by-Layer):\n"
            "   - تقسيم الكود أفقياً بناءً على نوع المكون البرمجي:\n     `com.example.app/`\n       `├── presentation/` (كل الـ Activities, Composables, ViewModels)\n       `├── domain/` (كل الـ UseCases, Entities)\n       `├── data/` (كل الـ Repositories, DAOs, DTOs)\n   - **المشكلة الكبرى**: مع نمو التطبيق (أكثر من 30 شاشة)، يصبح كل مجلد متضخماً بمئات الملفات غير المرتبطة ببعضها. كما أن التعديل في ميزة واحدة (مثل الدفع Payment) يجبرك على القفز بين 4 مجلدات مختلفة في أطراف المشروع!\n\n"
            "2. تنظيم الحزم حسب الميزة (Package-by-Feature):\n"
            "   - تقسيم الكود عمودياً بناءً على مجالات العمل وميزات المستخدم:\n     `com.example.app/`\n       `├── checkout/` (ViewModel, UI, UseCases, Repositories الخاصة بالـ Checkout)\n       `├── auth/` (كل ما يخص تسجيل الدخول)\n       `├── catalog/` (كل ما يخص تصفح المنتجات)\n   - **المزايا الخارقة**: التماسك العالي (High Cohesion)، سهولة العثور على الملفات، واستخدام الـ Visibility Modifiers (`internal` في كوتلن) لحماية الكود الداخلي للميزة.\n\n"
            "3. المعمارية الهجينة الحديثة في أندرويد (Feature Modules with Layers):\n   - التطبيقات الكبرى تنظم الكود أولاً **حسب الميزة** (Modules per Feature)، وداخل كل ميزة يتم تنظيم الكود داخلياً **حسب الطبقات** (`presentation`, `domain`, `data`)."
        ),
        "practical_walkthrough": (
            "مقارنة هيكل المجلدات بين النمطين في مشروع حقيقي:\n"
            "```text\n"
            "// ❌ Package-by-Layer (ضعيف التماسك وصعب الصيانة في المشاريع الكبيرة):\n"
            "com.example.app/\n"
            "├── ui/\n"
            "│   ├── LoginScreen.kt, HomeScreen.kt, CheckoutScreen.kt, ProfileScreen.kt...\n"
            "├── viewmodel/\n"
            "│   ├── LoginViewModel.kt, HomeViewModel.kt, CheckoutViewModel.kt...\n"
            "├── repository/\n"
            "│   ├── AuthRepository.kt, CartRepository.kt, ProfileRepository.kt...\n"
            "\n"
            "// ✅ Package-by-Feature (عالي التماسك وسهل التوزيع والتحويل لـ Modules):\n"
            "com.example.app/\n"
            "├── auth/\n"
            "│   ├── LoginScreen.kt\n"
            "│   ├── LoginViewModel.kt\n"
            "│   ├── AuthRepository.kt\n"
            "│   └── AuthModels.kt\n"
            "├── checkout/\n"
            "│   ├── CheckoutScreen.kt\n"
            "│   ├── CheckoutViewModel.kt\n"
            "│   └── CartRepository.kt\n"
            "└── core/\n"
            "    ├── database/\n"
            "    └── network/\n"
            "```"
        ),
        "quick_answer": "Package-by-layer groups files by technical role (all ViewModels together, all Repositories together), causing scattered feature code and low cohesion. Package-by-feature groups files by business capability (all auth code together, all cart code together), providing high cohesion, encapsulation, and an easy path to Gradle modularization.",
        "best_answer": (
            "Packaging strategy determines cognitive load, code navigation speed, and modularization readiness in growing codebases.\n\n"
            "1. **Package-by-Layer (Horizontal Partitioning)**:\n"
            "   - Groups files strictly by their technical classification (`presentation`, `domain`, `data`).\n"
            "   - *Drawbacks*: As the app grows beyond a few screens, packages balloon to hundreds of files. Feature cohesion is completely lost: developing a single feature requires jumping across multiple directories. Everything must be marked `public`, destroying encapsulation.\n\n"
            "2. **Package-by-Feature (Vertical Partitioning)**:\n"
            "   - Groups all artifacts required for a specific business capability into a single cohesive package (`auth`, `checkout`, `profile`).\n"
            "   - *Benefits*: High cohesion. Deleting or modifying a feature touches files in a single self-contained directory. Allows leveraging Kotlin's `internal` visibility to hide feature-internal implementation details.\n\n"
            "3. **Modern Hybrid Standard**:\n"
            "   - In enterprise Android architecture, we package **by feature at the macro level** (often as separate Gradle modules), and **by layer at the micro level** within that feature (`:feature:checkout/ui`, `.../domain`, `.../data`)."
        ),
        "deep_answer": (
            "The major architectural triumph of package-by-feature is enabling painless **Multi-Module Migration**. "
            "A project structured by layer is nearly impossible to modularize because circular dependencies between packages are rampant across features. "
            "In contrast, a project structured by feature can extract `auth/` or `checkout/` directly into an independent Gradle module `:feature:auth` within hours.\n\n"
            "Encapsulation is another vital advantage. "
            "Under package-by-layer, a repository implementation class in `data` must be declared `public` so a use case in `domain` or a ViewModel in `ui` can access it. "
            "Under package-by-feature in separate modules, concrete implementation classes can be marked `internal`, exposing only a clean public interface or entry point.\n\n"
            "Shared infrastructure (Network clients, Database drivers, Common UI Design Tokens) lives in dedicated core packages (`core:network`, `core:database`, `core:designsystem`)."
        ),
        "follow_ups": [
            {
                "question": "Where should shared cross-cutting code live in a package-by-feature setup?",
                "answer": "In dedicated foundation modules or packages prefixed with `core/` (e.g. `core/network`, `core/database`, `core/ui`), consumed by feature packages."
            },
            {
                "question": "How does package-by-feature improve PR review velocity?",
                "answer": "Reviewers can review changes localized to a single directory rather than diffs scattered across presentation, domain, and data layers, speeding up comprehension and reducing merge conflicts."
            }
        ]
    },
    {
        "id": "ARC-17",
        "arabic_explanation": (
            "كيف تدير أحداث المرة الواحدة (One-Time Effects) مثل الـ Snackbars، الـ Toasts، وأحداث التنقل في معمارية UDF؟\n\n"
            "1. معضلة أحداث المرة الواحدة في UDF:\n   - في المعمارية أحادية الاتجاه (UDF)، الواجهة عبارة عن مراقب لحالة مستمرة (`StateFlow<UiState>`).\n   - الأحداث العابرة (مثل إظهار رسالة خطأ سريعة Snackbar أو التنقل لشاشة أخرى عند نجاح الدفع) ليست حالات مستمرة؛ بل هي أحداث يجب أن تستهلك **مرة واحدة فقط (Fire-and-Forget)**.\n   - إذا وضعت حدثاً كـ Boolean في الـ State (مثل `showError = true`) دون تصفيره، فعند تدوير الشاشة (Configuration Change) يعاد استهلاك الحدث ويظهر الـ Snackbar مرة أخرى للمستخدم بدون داعٍ!\n\n"
            "2. الطريقة الحديثة الرسمية الموصى بها (State-Based Event Consumption):\n   - تمثيل الحدث ككائن قابل للاستهلاك في الـ State: `val userMessage: UserMessage? = null`.\n   - عندما تقرأه الواجهة، تعرض الـ Snackbar فوراً، ثم ترسل حدثاً للـ ViewModel: `onMessageDismissed(messageId)` لتصفيره إلى `null`.\n   - الميزة: استعادة تامة وموثوقة للحالة حتى مع موت العملية (Process Death).\n\n"
            "3. بديل الـ Channels الموجهة للـ UI:\n   - استخدام `Channel<UiEffect>(Channel.BUFFERED)` والتحويل إلى `receiveAsFlow()`.\n   - يتم استقبالها في Compose عبر `LaunchedEffect`.\n   - تنبيه: يجب جمع الـ Channel عبر دورة حياة آمنة (`repeatOnLifecycle`) لمنع فقدان الأحداث أثناء وجود التطبيق في الخلفية."
        ),
        "practical_walkthrough": (
            "تنفيذ أحداث المرة الواحدة باستخدام نمط الرسائل القابلة للاستهلاك ونمط الـ Channel:\n"
            "```kotlin\n"
            "// النمط الرسمي الموصى به: State-Based مع تصفير الحدث بعد استهلاكه:\n"
            "data class PaymentUiState(\n"
            "    val isProcessing: Boolean = false,\n"
            "    val pendingMessage: String? = null // يمثل حدث المرة الواحدة كـ State\n"
            ")\n"
            "\n"
            "@Composable\n"
            "fun PaymentScreen(\n"
            "    viewModel: PaymentViewModel,\n"
            "    snackbarHostState: SnackbarHostState = remember { SnackbarHostState() }\n"
            ") {\n"
            "    val state by viewModel.uiState.collectAsStateWithLifecycle()\n"
            "\n"
            "    // مراقبة الرسالة؛ عرضها ثم إبلاغ الـ ViewModel بتصفيرها فوراً:\n"
            "    LaunchedEffect(state.pendingMessage) {\n"
            "        state.pendingMessage?.let { msg ->\n"
            "            snackbarHostState.showSnackbar(msg)\n"
            "            viewModel.onMessageShown() // تصفير لمنع تكرار العرض عند تدوير الشاشة!\n"
            "        }\n"
            "    }\n"
            "\n"
            "    Scaffold(snackbarHost = { SnackbarHost(snackbarHostState) }) {\n"
            "        PaymentContent(state)\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Manage one-time effects either by modeling them as consumable state in `UiState` and clearing them via an `onDismissed()` callback immediately after display (Google's official recommendation), or via a buffered `Channel<UiEffect>` collected with `LaunchedEffect` and `repeatOnLifecycle`.",
        "best_answer": (
            "Managing one-time transient events (Snackbars, toasts, navigation triggers) in Unidirectional Data Flow requires balancing state immutability with single-consumption guarantees.\n\n"
            "1. **The Consumable State Pattern (Official Google Recommendation)**:\n"
            "   - Model the one-off event directly inside the `UiState`: `userMessage: UserMessage?`.\n   - In Compose, a `LaunchedEffect(state.userMessage)` triggers when non-null, displays the Snackbar via `snackbarHostState.showSnackbar(message)`, and immediately invokes a callback `viewModel.onMessageShown(id)` to clear the state back to `null`.\n   - *Advantage*: Guarantees state restoration across process death via `SavedStateHandle` without event dropping or phantom repeats.\n\n"
            "2. **The Buffered Channel Pattern (Side-Effect Stream)**:\n"
            "   - In the ViewModel, declare `private val _effectChannel = Channel<UiEffect>(Channel.BUFFERED)` exposed as `val effects = _effectChannel.receiveAsFlow()`.\n   - In Compose, collect effects inside `LaunchedEffect(Unit)`.\n   - *Advantage*: Zero boilerplate callback required to clear state; strictly delivers events sequentially.\n   - *Caution*: Must be collected with lifecycle awareness (`flowWithLifecycle` or `repeatOnLifecycle`) so events emitted while in the background are buffered rather than dropped."
        ),
        "deep_answer": (
            "Why did the classic `SharedFlow(replay = 0)` fail for single-shot events? "
            "`SharedFlow` with zero replay acts as a hot broadcast. "
            "If an event is emitted while the UI is executing an orientation change or navigation transition, no collector is actively subscribed. "
            "The event is silently dropped into the void, and the user never sees the Snackbar or confirmation alert!\n\n"
            "A `Channel(Channel.BUFFERED)` solves this by maintaining an internal queue. "
            "If the UI is temporarily unsubscribed during screen rotation, the channel buffers the event until the new Activity/Composable subscribes, delivering it reliably without loss.\n\n"
            "For user-driven navigation, remember that not all navigation is a ViewModel effect: clicking an item to open details should directly invoke `navController.navigate()` from the UI callback, avoiding roundtrips through the ViewModel."
        ),
        "follow_ups": [
            {
                "question": "Why is `SharedFlow(replay = 0)` problematic for one-time events?",
                "answer": "It drops emissions if there are no active subscribers at the exact millisecond of emission, causing lost navigation or toast events during configuration changes or background transitions."
            },
            {
                "question": "Can `Channel.receiveAsFlow()` be collected by multiple collectors?",
                "answer": "No. Channels are unicast by default; emissions are consumed by whichever collector retrieves them first, which is ideal for single-screen UI effects."
            }
        ]
    },
    {
        "id": "ARC-18",
        "arabic_explanation": (
            "كيف تحافظ على الـ ViewModel آمناً للـ Main Thread (Main-Safe) وقابلاً للاختبار بنسبة 100% (Testable)؟\n\n"
            "1. الحفاظ على الـ Main-Safety:\n   - **مبدأ Main-Safety**: يجب أن يكون أي استدعاء داخل الـ ViewModel آمناً للتنفيذ مباشرة من الـ Main Thread دون حظر الـ Looper.\n   - **حقن الـ Coroutine Dispatchers**: لا تستخدم أبداً `Dispatchers.IO` أو `Dispatchers.Default` بشكل هاردكود داخل الكود!\n     * قم بحقن الموزعات عبر الـ Constructor Injection (`@IoDispatcher private val ioDispatcher: CoroutineDispatcher`).\n     * في بيئة الاختبارات، يمكنك استبدال الموزع المحقون بـ `StandardTestDispatcher()` أو `UnconfinedTestDispatcher()`.\n\n"
            "2. الحفاظ على قابلية الاختبار (Testability):\n   - **عدم استيراد أي Android Framework Classes**: لا Context، لا Resources، ولا Views.\n   - **استخدام Fakes بدلاً من Mocks المعقدة**: حقن Fake Repositories بسيطة في الـ Unit Tests.\n   - **اختبار الـ StateFlow عبر مكتبة Turbine**: استخدام `turbine` للاستماع لتدفقات الحالة وفحص الانبعاثات بالترتيب الزمني الدقيق."
        ),
        "practical_walkthrough": (
            "تصميم ViewModel آمن تماماً للـ Main وقابل للاختبار الفوري بوحدة اختبار JVM:\n"
            "```kotlin\n"
            "// 1. VIEWMODEL: حقن الـ Dispatchers واستخدام Main-safe patterns:\n"
            "@HiltViewModel\n"
            "class TaskViewModel @Inject constructor(\n"
            "    private val taskRepository: TaskRepository,\n"
            "    @IoDispatcher private val ioDispatcher: CoroutineDispatcher = Dispatchers.IO\n"
            ") : ViewModel() {\n"
            "    private val _uiState = MutableStateFlow<TaskUiState>(TaskUiState.Loading)\n"
            "    val uiState: StateFlow<TaskUiState> = _uiState.asStateFlow()\n"
            "\n"
            "    fun loadTasks() {\n"
            "        viewModelScope.launch { // ينطلق على Main بأمان\n"
            "            _uiState.value = TaskUiState.Loading\n"
            "            val result = withContext(ioDispatcher) { taskRepository.fetchTasks() }\n"
            "            _uiState.value = TaskUiState.Success(result)\n"
            "        }\n"
            "    }\n"
            "}\n"
            "\n"
            "// 2. UNIT TEST: اختبار فوري على الـ JVM باستخدام Turbine و TestDispatcher:\n"
            "class TaskViewModelTest {\n"
            "    private val testDispatcher = StandardTestDispatcher()\n"
            "    private val fakeRepo = FakeTaskRepository()\n"
            "    private lateinit var viewModel: TaskViewModel\n"
            "\n"
            "    @Before\n"
            "    fun setup() {\n"
            "        Dispatchers.setMain(testDispatcher) // ضبط Main dispatcher للاختبار\n"
            "        viewModel = TaskViewModel(fakeRepo, testDispatcher)\n"
            "    }\n"
            "\n"
            "    @After\n"
            "    fun tearDown() { Dispatchers.resetMain() }\n"
            "\n"
            "    @Test\n"
            "    fun loadTasks_emitsLoadingThenSuccess() = runTest(testDispatcher) {\n"
            "        viewModel.uiState.test {\n"
            "            assertEquals(TaskUiState.Loading, awaitItem())\n"
            "            viewModel.loadTasks()\n"
            "            testDispatcher.scheduler.advanceUntilIdle()\n"
            "            val successState = awaitItem() as TaskUiState.Success\n"
            "            assertEquals(2, successState.tasks.size)\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Keep a ViewModel main-safe by never running blocking operations and injecting `CoroutineDispatcher`s via constructor injection rather than hardcoding them. Keep it testable by avoiding Android framework classes, using Fake repositories, and testing `StateFlow` emissions with Turbine and `StandardTestDispatcher`.",
        "best_answer": (
            "Ensuring a ViewModel remains main-safe and thoroughly testable requires disciplined concurrency and dependency decoupling.\n\n"
            "1. **Enforcing Main-Safety**:\n"
            "   - `viewModelScope.launch` launches on `Dispatchers.Main.immediate` by default. Heavy I/O or CPU operations must be switched using `withContext`.\n"
            "   - **Never hardcode dispatchers**: Always inject `CoroutineDispatcher` instances using Dagger/Hilt qualifiers (`@IoDispatcher`, `@DefaultDispatcher`). Hardcoding `Dispatchers.IO` breaks test determinism because background thread timing cannot be paused or advanced virtually in unit tests.\n\n"
            "2. **Maximizing Testability**:\n"
            "   - **Zero Android Framework Dependencies**: The ViewModel must contain no imports of Android `Context`, `View`, or platform managers. Localized strings use the `UiText` resource ID pattern.\n"
            "   - **Testing with Turbine and TestDispatchers**: We set up tests using `StandardTestDispatcher()` and `Dispatchers.setMain()`. Using Cash App's **Turbine** library, we assert emissions from `StateFlow` sequentially and deterministically without arbitrary sleeps."
        ),
        "deep_answer": (
            "Under the hood, `StandardTestDispatcher` shares a `TestCoroutineScheduler`. "
            "When `runTest` executes, coroutines are queued rather than executed immediately. "
            "Calling `advanceUntilIdle()` or `advanceTimeBy(ms)` steps virtual execution forward instantaneously, allowing tests covering complex delays, debounces, and retries to execute in 5 milliseconds of real clock time.\n\n"
            "If a ViewModel hardcodes `Dispatchers.IO`, `runTest` loses control over thread execution. "
            "The coroutine jumps onto the real JVM background thread pool, creating flaky race conditions where tests assert state before the background worker has finished writing.\n\n"
            "In enterprise CI pipelines, tests using injected dispatchers and Turbine run in headless JVM suites, executing thousands of ViewModel test cases in seconds with 0% flakiness."
        ),
        "follow_ups": [
            {
                "question": "What is the difference between `StandardTestDispatcher` and `UnconfinedTestDispatcher`?",
                "answer": "`StandardTestDispatcher` queues coroutines until manually advanced via its scheduler, giving full control over execution order. `UnconfinedTestDispatcher` eagerly executes coroutines eagerly until their first suspension point."
            },
            {
                "question": "Why is Cash App's Turbine library preferred over `first()` or `toList()` for testing flows?",
                "answer": "Turbine asserts the exact temporal order of emissions, captures errors, verifies that no unexpected items are emitted, and properly cancels flow collections upon completion."
            }
        ]
    },
    {
        "id": "ARC-19",
        "arabic_explanation": (
            "كيف تدير تحديثات الكاش (Cache) والسيرفر (Server) داخل طبقة البيانات (Data Layer) باحترافية؟\n\n"
            "1. استراتيجيات مزامنة البيانات الشائعة:\n   - **Network-Bound Resource (Offline-First / Cache-First)**:\n     * نقرأ ونعرض البيانات المحفوظة محلياً في الـ Database فوراً للمستخدم.\n     * في نفس الوقت نطلب أحدث البيانات من السيرفر في الخلفية.\n     * عند نجاح الطلب، نحدث الـ Database محلياً، فتقوم قاعدة البيانات بإطلاق تحديث تلقائي للواجهة.\n   - **Cache-Aside / Read-Through**:\n     * فحص الكاش في الذاكرة أولاً؛ إذا كانت منتهية الصلاحية (Stale)، يتم طلب السيرفر وتحديث الكاش.\n   - **Optimistic Updates (التحديث التفاؤلي)**:\n     * عند اتخاذ المستخدم لإجراء (مثل عمل Like لبوست)، نقوم بتحديث الـ Database المحلية والـ UI فوراً دون انتظار رد السيرفر!\n     * إذا فشل طلب السيرفر لاحقاً، نقوم بالتراجع (Rollback) وإظهار تنبيه للمستخدم.\n\n"
            "2. دور الـ Invalidation Tracker وإدارة تضارب التعديلات:\n   - استخدام الـ ETag و `If-None-Match` في طلبات HTTP لتجنب تنزيل البيانات غير المعدلة (304 Not Modified).\n   - إدارة المعاملات في قاعدة البيانات عبر `@Transaction` لضمان كتابة البيانات دفعة واحدة دون تشويه الحالة."
        ),
        "practical_walkthrough": (
            "تنفيذ نمط Network-Bound Resource وتحديث الـ Cache في طبقة البيانات:\n"
            "```kotlin\n"
            "class ProductRepositoryImpl(\n"
            "    private val localDao: ProductDao,\n"
            "    private val remoteApi: ProductApi\n"
            ") : ProductRepository {\n"
            "\n"
            "    // نمط Offline-First: يقرأ من DB فوراً، ويطلب السيرفر ويحدث DB عند النجاح:\n"
            "    override fun getProducts(): Flow<Resource<List<Product>>> = flow {\n"
            "        // 1. انبعاث البيانات المتاحة في الكاش فوراً:\n"
            "        val cached = localDao.getProductsSync().map { it.toDomain() }\n"
            "        emit(Resource.Loading(cached))\n"
            "\n"
            "        try {\n"
            "            // 2. جلب أحدث البيانات من السيرفر:\n"
            "            val remoteDtos = remoteApi.fetchProducts()\n"
            "            // 3. تحديث قاعدة البيانات داخل Transaction:\n"
            "            localDao.updateProductsTransaction(remoteDtos.map { it.toEntity() })\n"
            "        } catch (e: Exception) {\n"
            "            emit(Resource.Error(e.message ?: \"Sync failed\", cached))\n"
            "        }\n"
            "\n"
            "        // 4. انبعاث البيانات النهائية المحدثة من الـ DB:\n"
            "        emitAll(localDao.observeProducts().map { Resource.Success(it.map { e -> e.toDomain() }) })\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Manage cache and server updates within the data layer using the Offline-First (Network-Bound Resource) pattern: emit local cached data from Room immediately, fetch updates from the network in the background, write payloads into the database inside a transaction, and let Room reactively emit updated state.",
        "best_answer": (
            "Managing cache and server synchronization is the primary responsibility of the Data layer, isolating presentation code from networking and storage complexity.\n\n"
            "1. **The Offline-First (Network-Bound Resource) Pattern**:\n"
            "   - **Immediate Local Emission**: The repository reads from the local database (Room) and emits cached data immediately, providing instantaneous screen loads.\n"
            "   - **Background Synchronization**: Concurrently, the repository triggers an asynchronous network fetch.\n"
            "   - **Atomic Ingestion**: When the network succeeds, the repository writes the new entities into Room inside a database transaction (`@Transaction`), clearing obsolete records.\n"
            "   - **Reactive Propagation**: Room's `InvalidationTracker` detects the write and emits the fresh dataset on the active `Flow`, updating observers automatically.\n\n"
            "2. **Optimistic Updates**:\n"
            "   - For interactive user mutations (e.g. liking a post or archiving an email), waiting for server roundtrips introduces unacceptable UI latency.\n"
            "   - The repository modifies local database state immediately. If the network request fails, the repository rolls back the mutation and surfaces an actionable error."
        ),
        "deep_answer": (
            "Under the hood, HTTP cache headers play a pivotal role. "
            "By configuring OkHttp's `Cache` directory and leveraging `ETag` and `If-None-Match` headers, the server can return HTTP `304 Not Modified` with zero body payload. "
            "This conserves battery and mobile bandwidth while confirming that local cache is fresh.\n\n"
            "For conflict resolution (when both client and server update data concurrently), enterprise repositories employ **Conflict Resolution Policies**:\n"
            "- *Server-Wins*: The default in most consumer apps; server timestamps overwrite local modifications.\n"
            "- *Client-Wins / Last-Write-Wins (LWW)*: Based on monotonic client timestamps.\n"
            "- *Merge Policies*: Employed in collaborative apps where fields are merged individually.\n\n"
            "In testing, repository synchronization is verified by asserting that simulated network failures still yield cached data, and network successes overwrite stale database records."
        ),
        "follow_ups": [
            {
                "question": "What is an Optimistic Update, and how do you handle rollbacks?",
                "answer": "An optimistic update mutates the local database immediately to provide zero-latency UI feedback. If the subsequent network call fails, the repository executes a compensating transaction to revert the change and notify the UI."
            },
            {
                "question": "Why should database writes be wrapped in `@Transaction`?",
                "answer": "Transactions ensure atomicity: either all records are updated or none are. If an error occurs halfway through, the database rolls back, preventing corrupt partial states."
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

    for item in ARC_14_19:
        by_id[item["id"]] = item

    output = [by_id[k] for k in sorted(by_id.keys())]
    DATA_FILE.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {DATA_FILE} with questions ARC-14 to ARC-19. Total questions: {len(output)}")

if __name__ == "__main__":
    main()
