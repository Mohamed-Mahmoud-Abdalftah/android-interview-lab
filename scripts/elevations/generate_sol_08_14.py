#!/usr/bin/env python3
"""Generator for SOL-08 through SOL-14 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "sol.json"

SOL_08_14 = [
    {
        "id": "SOL-08",
        "arabic_explanation": (
            "المقارنة والفرق الجوهري بين مبدأ المسؤولية الواحدة (SRP) ومبدأ فصل الواجهات (ISP):\n\n"
            "1. ما هو الفرق الأساسي بينهما؟\n"
            "   - **مبدأ المسؤولية الواحدة (SRP - Single Responsibility Principle)**:\n     * يركز على **الكلاسات والتنفيذ (Classes & Implementations)**.\n     * ينظر إلى الكود من **الداخل إلى الخارج (Inside-Out)**.\n     * يسأل: *\"كم سبباً لدى هذا الكلاس ليتغير؟ ومن هو صاحب المصلحة (Actor) الذي يخدمه هذا الكلاس؟\"*\n     * الهدف: تماسك الكود (High Cohesion) ومنع الكلاسات من التضخم بمسؤوليات متعددة.\n   - **مبدأ فصل الواجهات (ISP - Interface Segregation Principle)**:\n     * يركز على **الواجهات والعملاء المستهلكين (Interfaces & Clients)**.\n     * ينظر إلى الكود من **الخارج إلى الداخل (Outside-In)**.\n     * يسأل: *\"هل هذا الـ Client مجبر على معرفة أو تنفيذ دوال لا يحتاجها في هذا الـ Interface؟\"*\n     * الهدف: تقليل الاعتمادية غير الضرورية وفصل الصلاحيات (Decoupling).\n\n"
            "2. كيف يتكاملان معاً في كود Android؟\n   - كلاس `UserRepositoryImpl` قد يكون متوافقاً تماماً مع **SRP** (مسؤول فقط عن تنسيق بيانات المستخدم).\n   - ولكنه يقدم واجهة ضخمة (Fat Interface) فيها 20 دالة.\n   - هنا يأتي دور **ISP** لتقسيم تلك الواجهة إلى `UserReader` و `UserWriter` حتى لا تجبر شاشة العرض على رؤية دوال الحذف والتعديل."
        ),
        "practical_walkthrough": (
            "توضيح التكامل بين SRP و ISP في كود Android:\n"
            "```kotlin\n"
            "// كلاس واحد محقق لمبدأ SRP (مسؤوليته الوحيدة تنسيق بيانات المستخدم في Data layer):\n"
            "class UserRepositoryImpl(\n"
            "    private val localDao: UserDao,\n"
            "    private val remoteApi: UserApi\n"
            ") : UserReader, UserWriter { // ينفذ واجهتين مفصولتين تحقيقاً لـ ISP\n"
            "\n"
            "    override fun getUser(id: String): Flow<User> = localDao.getUser(id)\n"
            "    override suspend fun updateUser(user: User) { remoteApi.update(user) }\n"
            "}\n"
            "\n"
            "// واجهات دقيقة تحقق مبدأ ISP:\n"
            "interface UserReader { // موجهة للـ Widgets والشاشات التي تقرأ فقط\n"
            "    fun getUser(id: String): Flow<User>\n"
            "}\n"
            "\n"
            "interface UserWriter { // موجهة لشاشات التعديل فقط\n"
            "    suspend fun updateUser(user: User)\n"
            "}\n"
            "```"
        ),
        "quick_answer": "SRP focuses on classes and actors: a class should have only one reason to change. ISP focuses on interfaces and clients: a client should not be forced to depend on methods it doesn't use. A class can satisfy SRP (single responsibility) while its interface violates ISP (exposing too many methods to distinct callers).",
        "best_answer": (
            "While both SRP and ISP promote modularity, they operate from opposing perspectives in the design hierarchy.\n\n"
            "1. **SRP (Single Responsibility Principle - Inside-Out Perspective)**:\n"
            "   - Governs **classes, modules, and concrete implementations**.\n   - Focuses on the *producer* of behavior.\n   - Criterion: A class must have only one reason to change, serving a single business actor (e.g. `PaymentValidator` serves business rules; `PaymentRepository` serves storage).\n   - Goal: High cohesion within the class.\n\n"
            "2. **ISP (Interface Segregation Principle - Outside-In Perspective)**:\n"
            "   - Governs **interfaces and abstractions**.\n   - Focuses on the *consumer (client)* of behavior.\n   - Criterion: No client should be forced to depend on methods it does not invoke.\n   - Goal: Loose coupling between clients and shared abstractions.\n\n"
            "A concrete class can be 100% compliant with SRP (e.g. `UserRepositoryImpl` has the single cohesive responsibility of managing user data persistence), yet violate ISP if it exposes a monolithic 30-method interface to simple read-only UI clients."
        ),
        "deep_answer": (
            "Under the hood, violating ISP harms build performance and incremental compilation in Gradle multi-module projects. "
            "If an interface `FullUserApi` is shared across 10 feature modules, modifying or adding a method used by only one feature invalidates the ABI hash. "
            "Gradle is forced to recompile all 10 consuming modules!\n\n"
            "Applying ISP prevents this ripple effect: fine-grained interfaces (`UserReader`, `UserPreferences`) isolate compilation boundaries. "
            "Updating `UserWriter` triggers recompilation strictly for the edit profile module, leaving read-only feed modules cached.\n\n"
            "In Kotlin, using interface segregation combined with delegation allows composing rich capabilities: `class FacadeRepo(reader: UserReader, writer: UserWriter) : UserReader by reader, UserWriter by writer`."
        ),
        "follow_ups": [
            {
                "question": "Can a class violate SRP while its interface satisfies ISP?",
                "answer": "Yes. A class might implement a clean 2-method interface like `Runnable`, but inside `run()` it executes networking, database parsing, and UI mutations, severely violating SRP."
            },
            {
                "question": "How does ISP benefit unit testing?",
                "answer": "Clients depending on segregated interfaces require tiny, focused test doubles (Fakes) implementing 1-2 methods rather than massive mock objects stubbing 20 irrelevant methods."
            }
        ]
    },
    {
        "id": "SOL-09",
        "arabic_explanation": (
            "ما هو مبدأ تفضيل التركيب على الوراثة (Composition over Inheritance) ولماذا هو أساسي في Android الحديث؟\n\n"
            "1. ما هو الفرق بين التركيب (Composition) والوراثة (Inheritance)؟\n   - **الوراثة (Inheritance - \"is-a\")**: كلاس فرعي يرث كل شيء من كلاس أب (`class ProfileActivity : BaseActivity()`).\n     * المشاكل القاتلة: **الاقتران الشديد (Tight Coupling)** و **هشاشة الكلاس الأساسي (Fragile Base Class)**؛ أي تعديل في الكلاس الأساسي قد يكسر عشرات الشاشات الفرعية بصمت، ولا يمكن وراثة أكثر من كلاس واحد في Kotlin/Java!\n   - **التركيب (Composition - \"has-a\")**: تجميع كائنات صغيرة مستقلة تؤدي وظائف محددة بداخل الكلاس (`class ProfileScreen(val toolbarHandler: ToolbarHandler, val analytics: AnalyticsTracker)`).\n     * المزايا: مرونة تامة، إمكانية تبديل السلوكيات في وقت التشغيل، سهولة الاختبار الفردي لكل مكون، وتجنب شجرة الوراثة المعقدة.\n\n"
            "2. كيف يظهر هذا المبدأ في Jetpack Compose؟\n   - Jetpack Compose مبني بنسبة **100% على التركيب (Composition)**!\n   - لا يوجد في Compose كلاس يرث من كلاس؛ بل شاشة `Scaffold` تركّب بداخلها `TopAppBar` و `FloatingActionButton` و `Content` كدوال مستقلة تماماً."
        ),
        "practical_walkthrough": (
            "استبدال الوراثة الهشة بكائنات مركبة عبر تفويض كوتلن (Kotlin Delegation):\n"
            "```kotlin\n"
            "// ❌ وراثة هشة: شجرة كلاسات Base عميقة يصعب تعديلها واختبارها:\n"
            "open class BaseActivity : AppCompatActivity() { /* 500 سطر للتحليلات وشريط الأدوات */ }\n"
            "open class AuthenticatedBaseActivity : BaseActivity() { /* 300 سطر للتحقق من الجلسة */ }\n"
            "class OrdersActivity : AuthenticatedBaseActivity() { /* مقيدة بشجرة وراثة صلبة! */ }\n"
            "\n"
            "// ✅ التركيب (Composition): سلوكيات مستقلة تُركب حسب الحاجة عبر Kotlin by:\n"
            "interface SessionObserver {\n"
            "    fun registerSessionTimeout(activity: Activity)\n"
            "}\n"
            "class SessionObserverImpl : SessionObserver { ... }\n"
            "\n"
            "interface AnalyticsLogger {\n"
            "    fun logScreen(name: String)\n"
            "}\n"
            "class FirebaseAnalyticsLogger : AnalyticsLogger { ... }\n"
            "\n"
            "// تركيب السلوكيات في الشاشة دون وراثة هشة:\n"
            "class OrdersActivity(\n"
            "    private val session: SessionObserver = SessionObserverImpl(),\n"
            "    private val analytics: AnalyticsLogger = FirebaseAnalyticsLogger()\n"
            ") : AppCompatActivity(), SessionObserver by session, AnalyticsLogger by analytics {\n"
            "    override fun onCreate(savedInstanceState: Bundle?) {\n"
            "        super.onCreate()\n"
            "        registerSessionTimeout(this)\n"
            "        logScreen(\"OrdersScreen\")\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Composition over inheritance favors assembling components with 'has-a' relationships over rigid 'is-a' inheritance trees. In Android, it eliminates bloated `BaseActivity` anti-patterns, enables runtime behavioral flexibility, avoids the fragile base class problem, and is the foundational architecture of Jetpack Compose.",
        "best_answer": (
            "The principle of 'Composition over Inheritance' advocates that classes should achieve polymorphic reuse by containing instances of other classes ('has-a') rather than inheriting state and behavior from a superclass ('is-a').\n\n"
            "1. **The Fragility of Inheritance**:\n"
            "   - Inheritance creates the tightest possible compile-time coupling: changes to private or protected implementations in a superclass ripple unpredictably across derived subclasses (the *Fragile Base Class problem*).\n   - Subclasses inherit irrelevant or unwanted behaviors (violating LSP).\n   - Single inheritance in Kotlin/Java prevents combining multiple orthogonal features (e.g. an Activity cannot inherit from both `BaseCameraActivity` and `BaseBillingActivity`).\n\n"
            "2. **The Power of Composition**:\n"
            "   - Components encapsulate isolated concerns (`AnalyticsHelper`, `SessionTracker`, `ToolbarCoordinator`).\n   - Components can be dynamically plugged in, swapped, or mocked in unit tests.\n   - Promotes high cohesion and clean unit testability.\n\n"
            "Jetpack Compose is the ultimate manifestation of this principle: Compose completely abandons the 15-year-old `android.view.View` inheritance tree in favor of pure, composable function graphs."
        ),
        "deep_answer": (
            "Kotlin offers first-class language support for composition via **Class Delegation (`by`)**. "
            "By declaring `class MyActivity : AppCompatActivity(), AnalyticsManager by analyticsManager`, Kotlin generates forwarding bytecode calls under the hood. "
            "This delivers the syntactic convenience of inheritance while preserving the architectural purity and loose coupling of composition.\n\n"
            "In Android Jetpack, `LifecycleObserver` and `LifecycleEventObserver` represent the official migration from inheritance to composition: instead of overriding `onStart()` in a `BaseActivity`, self-contained components observe `lifecycle.addObserver(myComponent)`, managing their own cleanup automatically."
        ),
        "follow_ups": [
            {
                "question": "When is inheritance still acceptable?",
                "answer": "When there is a genuine, immutable 'is-a' relationship where the subclass is a true specialized extension of the parent and obeys LSP without exception, or when extending third-party framework classes like `ViewModel` or `Fragment`."
            },
            {
                "question": "How does `LifecycleObserver` replace BaseActivity callbacks?",
                "answer": "Instead of subclasses calling `super.onStart()`, a component implements `DefaultLifecycleObserver` and registers itself with the Activity's lifecycle, executing setup and teardown independently."
            }
        ]
    },
    {
        "id": "SOL-10",
        "arabic_explanation": (
            "عندما يفرض كلاس `BaseFragment` تنفيذ دالة `setupToolbar()` ولكن بعض الشاشات ليس بها Toolbar: متى ينتهك هذا مبدأ LSP؟ وكيف يُعالج؟\n\n"
            "1. متى وكيف ينتهك هذا مبدأ لسكوف (LSP Violation)؟\n   - ينتهك LSP فوراً عندما يتوقع الكلاس الأساسي (أو مستدعي الكود) أن الدالة `setupToolbar()` ستقوم بتهيئة شريط أدوات صالح، ولكن الكلاس الفرعي:\n     * يرمي استثناء: `throw UnsupportedOperationException(\"No toolbar\")` مما يسبب Crash للمستخدم.\n     * أو يترك الدالة فارغة كـ No-op، فيقوم الكود الخارجي بالتعامل مع Toolbar غير موجود (NullPointer أو سلوك خفي مكسور).\n   - النتيجة: لا يمكن استبدال `BaseFragment` بـ `NoToolbarFragment` بأمان دون حدوث مفاجآت وسلوكيات مكسورة.\n\n"
            "2. العلاج المعماري الجذري:\n   - **إزالة الدالة من الـ BaseClass فوراً**: الكلاس الأساسي يجب ألا يفرض إلا السلوكيات المشتركة بين 100% من الشاشات.\n   - **إنشاء واجهة اختيارية (Marker/Capability Interface)**: `interface HasToolbar { fun getToolbar(): Toolbar }`.\n   - أو الأفضل: استخدام **Delegate مستقل** يتم استدعاؤه فقط داخل الشاشات التي تحتاج لشريط أدوات."
        ),
        "practical_walkthrough": (
            "معالجة انتهاك LSP في شاشات الـ Fragments:\n"
            "```kotlin\n"
            "// ❌ انتهاك LSP: BaseFragment يفرض Toolbar على شاشات لا تحتاجه (كالشاشات المنبثقة والشاشات الكاملة):\n"
            "abstract class LeakyBaseFragment : Fragment() {\n"
            "    abstract fun setupToolbar(): Toolbar // فرض إلزامي!\n"
            "}\n"
            "\n"
            "class FullscreenPlayerFragment : LeakyBaseFragment() {\n"
            "    override fun setupToolbar(): Toolbar {\n"
            "        // 💥 يكسر LSP: يرمي استثناء أو يعيد null بطريقة غير متوقعة:\n"
            "        throw UnsupportedOperationException(\"No toolbar in video player\")\n"
            "    }\n"
            "}\n"
            "\n"
            "// ✅ الحل المعماري المتوافق مع LSP: فصل القدرات في Interface أو Delegate:\n"
            "abstract class SafeBaseFragment : Fragment() {\n"
            "    // يحتوي فقط على السلوكيات العامة المشتركة بين 100% من الشاشات (مثل التحليلات أو الربط الأساسي)\n"
            "}\n"
            "\n"
            "// واجهة خاصة بالشاشات التي تمتلك Toolbar فقط:\n"
            "interface ToolbarProvider {\n"
            "    fun configureToolbar(toolbar: Toolbar)\n"
            "}\n"
            "\n"
            "class CatalogFragment : SafeBaseFragment(), ToolbarProvider {\n"
            "    override fun configureToolbar(toolbar: Toolbar) { /* إعداد Toolbar للشاشة */ }\n"
            "}\n"
            "\n"
            "class SafePlayerFragment : SafeBaseFragment() {\n"
            "    // لا ينفذ ToolbarProvider، ولا يكسر أي عقود!\n"
            "}\n"
            "```"
        ),
        "quick_answer": "It violates LSP when the caller expects a functional toolbar contract, but a subclass throws `UnsupportedOperationException`, returns null, or no-ops, breaking behavioral expectations. Fix it by removing `setupToolbar()` from `BaseFragment` and moving it to an optional `ToolbarProvider` capability interface or composable delegate.",
        "best_answer": (
            "A `BaseFragment` enforcing an abstract `setupToolbar()` violates the Liskov Substitution Principle (LSP) whenever a subclass cannot fulfill that contract meaningfully.\n\n"
            "Under LSP, any client holding a reference to `BaseFragment` should be able to invoke `setupToolbar()` with the guarantee that a toolbar exists, has been configured, and conforms to lifecycle invariants. "
            "When a fullscreen video player, bottom sheet, or modal dialog subclasses `BaseFragment`, it has no toolbar. If the developer:\n"
            "1. **Throws `UnsupportedOperationException`**: It breaks program execution at runtime.\n"
            "2. **Returns null or executes an empty no-op**: It breaks postconditions, leading to silent bugs or subsequent `NullPointerException`s if the host Activity queries the fragment's toolbar.\n\n"
            "**The Architectural Remedy**:\n"
            "- Remove `setupToolbar()` entirely from `BaseFragment`. A base class must define *only* invariants that apply to 100% of all derived classes.\n"
            "- Extract toolbar capability into an optional interface: `interface ToolbarHost { fun getToolbar(): Toolbar }`.\n"
            "- The hosting Activity inspects `if (fragment is ToolbarHost)` before configuring navigation bars, preserving substitution safety."
        ),
        "deep_answer": (
            "This scenario exposes the fundamental flaw of **inheritance-driven architecture**. "
            "Base classes tend to accumulate 'feature creep' over years: one developer adds toolbar logic, another adds swipe-to-refresh, a third adds FAB handling, until `BaseFragment` is 1,200 lines long and every new screen must fight against inherited assumptions.\n\n"
            "In modern Android development, the industry consensus is to **eliminate BaseFragment and BaseActivity entirely**. "
            "Shared behaviors are extracted into standalone, self-contained delegates implementing `DefaultLifecycleObserver` or composed via Jetpack Compose's `Scaffold(topBar = { ... })` where the toolbar parameter is naturally optional."
        ),
        "follow_ups": [
            {
                "question": "Why is eliminating `BaseFragment` completely considered best practice today?",
                "answer": "Base classes create rigid inheritance hierarchies, hide dependencies, cause LSP violations, and slow down build times. Composition via delegates and Compose UI provides far greater flexibility and testability."
            },
            {
                "question": "How does Jetpack Compose solve the optional toolbar problem?",
                "answer": "Compose's `Scaffold` composable accepts an optional `topBar: @Composable () -> Unit = {}` parameter. If a screen has no toolbar, you simply omit the parameter without subclassing or overriding anything."
            }
        ]
    },
    {
        "id": "SOL-11",
        "arabic_explanation": (
            "كيف تستبدل كلاس `BaseActivity` ضخم وعملاق بسلوكيات تركيبية صغيرة (Small Composable Behaviors)؟\n\n"
            "1. تشريح الـ BaseActivity العملاق (The God Base Class):\n   - يحتوي عادة على: تتبع التحليلات (Analytics tracking)، فحص الاتصال بالإنترنت (Network observer)، شريط الأدوات (Toolbar setup)، مؤشر التحميل العام (Global Progress Dialog)، وإدارة أذونات النظام (Permission handling).\n   - كل الشاشات مجبرة على وراثة كل هذا التعقيد حتى لو كانت شاشة بسيطة لا تحتاج شيئاً منه!\n\n"
            "2. استراتيجية التفكيك إلى سلوكيات تركيبية (Modular Decomposition):\n   - **السلوك 1: مراقبة دورة الحياة عبر LifecycleObserver**:\n     * سحب فحص الجلسة والتحليلات إلى كلاسات تنفذ `DefaultLifecycleObserver`.\n     * الـ Activity تقوم فقط بـ `lifecycle.addObserver(analyticsObserver)`.\n   - **السلوك 2: تفويض واجهة المستخدم عبر Jetpack Compose**:\n     * استبدال كود الـ Toolbar والـ Loading بـ Composable Reusable Scaffolds (`AppScaffold`).\n   - **السلوك 3: إدارة الأذونات عبر Activity Result APIs**:\n     * استخدام `registerForActivityResult` المدمج كـ Component مستقل."
        ),
        "practical_walkthrough": (
            "تفكيك BaseActivity عملاق إلى كلاسات LifecycleObservers ومكونات Compose:\n"
            "```kotlin\n"
            "// 1. سلوك تتبع التحليلات معزول كمراقب لدورة الحياة:\n"
            "class AnalyticsLifecycleObserver(private val tracker: AnalyticsTracker) : DefaultLifecycleObserver {\n"
            "    override fun onResume(owner: LifecycleOwner) {\n"
            "        tracker.logScreenVisit(owner.javaClass.simpleName)\n"
            "    }\n"
            "}\n"
            "\n"
            "// 2. سلوك فحص الاتصال معزول كمراقب شبكة:\n"
            "class NetworkMonitorObserver(private val networkMonitor: NetworkMonitor) : DefaultLifecycleObserver {\n"
            "    override fun onStart(owner: LifecycleOwner) { networkMonitor.start() }\n"
            "    override fun onStop(owner: LifecycleOwner) { networkMonitor.stop() }\n"
            "}\n"
            "\n"
            "// 3. النشاط أصبح نظيفاً تماماً بدون أي وراثة من BaseActivity مخصص:\n"
            "@AndroidEntryPoint\n"
            "class OrderActivity : ComponentActivity() {\n"
            "    @Inject lateinit var analyticsObserver: AnalyticsLifecycleObserver\n"
            "    @Inject lateinit var networkObserver: NetworkMonitorObserver\n"
            "\n"
            "    override fun onCreate(savedInstanceState: Bundle?) {\n"
            "        super.onCreate()\n"
            "        // تركيب السلوكيات بنعومة واستقلالية:\n"
            "        lifecycle.addObserver(analyticsObserver)\n"
            "        lifecycle.addObserver(networkObserver)\n"
            "\n"
            "        setContent {\n"
            "            AppScaffold(title = \"Orders\") {\n"
            "                OrderScreenContent()\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Replace a giant `BaseActivity` by decomposing its responsibilities into small, lifecycle-aware delegates implementing `DefaultLifecycleObserver` (for analytics and session timeouts), modern `ActivityResultContracts` (for permissions), and reusable Compose `AppScaffold` wrappers (for UI loading and toolbars).",
        "best_answer": (
            "Dismantling a monolithic `BaseActivity` requires migrating from inheritance-based coupling to modular lifecycle composition.\n\n"
            "A typical bloated `BaseActivity` agglomerates multiple orthogonal concerns:\n"
            "1. Screen analytics and tracking.\n"
            "2. Network connectivity monitoring.\n"
            "3. Global loading spinners and error dialogs.\n"
            "4. Runtime permissions management.\n"
            "5. Theme/Toolbar setup.\n\n"
            "**The Modular Replacement Architecture**:\n"
            "- **Lifecycle Concerns**: Extracted into self-contained classes implementing `DefaultLifecycleObserver` (e.g. `AnalyticsObserver`, `SessionTimeoutObserver`). Activities attach them via `lifecycle.addObserver(observer)`, allowing components to manage their own setup and teardown without overriding Activity lifecycle methods.\n"
            "- **System & Permissions Concerns**: Handled via Jetpack `registerForActivityResult(ActivityResultContracts.RequestPermission())` hoisted into standalone delegates or Compose state holders.\n"
            "- **Visual / UI Concerns**: Replaced by declarative Compose layout wrappers (e.g. `AppScaffold(showBackButton = true) { ... }`), keeping UI decorations purely functional.\n\n"
            "Activities inherit strictly from standard Android `ComponentActivity` or `AppCompatActivity`, eliminating the custom base class entirely."
        ),
        "deep_answer": (
            "Under the hood, Android Jetpack was deliberately designed to render `BaseActivity` obsolete. "
            "Before Jetpack `LifecycleOwner`, activities were the only place that received `onStart()` or `onResume()`, forcing developers to dump cross-cutting logic into `BaseActivity.onResume()`. "
            "With `DefaultLifecycleObserver`, any plain Kotlin class can observe an Activity's lifecycle safely.\n\n"
            "Furthermore, eliminating `BaseActivity` unlocks **Gradle modularization**. "
            "When every feature activity inherits from `BaseActivity` located in a common module, every feature module is circularly coupled to that base module's compilation classpath. "
            "By using composition, feature modules depend only on standard AndroidX APIs, drastically speeding up parallel compilation."
        ),
        "follow_ups": [
            {
                "question": "What is `DefaultLifecycleObserver` and why is it preferred over overriding Activity methods?",
                "answer": "It provides callbacks (`onStart`, `onResume`, `onDestroy`) that decoupled components can observe directly, removing the need for subclasses to call `super.onStart()`."
            },
            {
                "question": "How does removing `BaseActivity` improve incremental build times?",
                "answer": "In multi-module projects, modifying `BaseActivity` forces Gradle to recompile every single feature module that inherits from it. Modular delegates localize recompilations to the modified component only."
            }
        ]
    },
    {
        "id": "SOL-12",
        "arabic_explanation": (
            "كيف يدعم توجيه المدفوعات القائم على الاستراتيجية (Strategy-Based Payment Routing) مبدأ Open/Closed Principle (OCP)؟\n\n"
            "1. المشكلة في معالجة المدفوعات التقليدية:\n   - كلما أضاف البنك طريقة دفع جديدة (Credit Card, PayPal, Apple Pay, Klarna, Fawry, Vodafone Cash):\n   - في الكود التقليدي، تضطر لتعديل كلاس الـ `PaymentManager` وإضافة شروط جديدة في `when (paymentType)`.\n   - هذا ينتهك OCP بشكل صريح ويعرض المدفوعات القائمة لمخاطر الانهيار (Regression Risks)!\n\n"
            "2. تطبيق نمط الاستراتيجية (The Strategy Pattern):\n   - نقوم بتعريف واجهة عامة موحدة: `interface PaymentStrategy`.\n   - كل مزود دفع يصبح كلاس مستقل ينفذ هذه الواجهة (`StripePaymentStrategy`, `ApplePayStrategy`).\n   - كلاس `PaymentRouter` يصبح **مغلقاً للتعديل (Closed for Modification)**: لا يمتلك أي كتل `if/else`، بل يستقبل خريطة أو قائمة من الاستراتيجيات (`Map<PaymentType, PaymentStrategy>`) ويختار الاستراتيجية المناسبة في وقت التشغيل.\n\n"
            "3. النتيجة:\n   - لإضافة طريقة دفع سادسة، نقوم ببساطة بإنشاء ملف كلاس جديد وربطه عبر Dagger/Hilt، دون لمس أو تعديل سطر واحد في كلاسات الدفع القديمة!"
        ),
        "practical_walkthrough": (
            "هندسة توجيه المدفوعات باستخدام نمط Strategy و Hilt Multibindings:\n"
            "```kotlin\n"
            "// 1. العقد الموحد للاستراتيجيات (Strategy Interface):\n"
            "interface PaymentStrategy {\n"
            "    val method: PaymentMethod\n"
            "    suspend fun authorize(amountCents: Long, details: PaymentDetails): PaymentResult\n"
            "}\n"
            "\n"
            "// 2. تطبيقات مستقلة ومعزولة لكل مزود خدمة:\n"
            "class StripePaymentStrategy @Inject constructor(...) : PaymentStrategy {\n"
            "    override val method = PaymentMethod.CREDIT_CARD\n"
            "    override suspend fun authorize(amountCents: Long, details: PaymentDetails) = ...\n"
            "}\n"
            "\n"
            "class PayPalPaymentStrategy @Inject constructor(...) : PaymentStrategy {\n"
            "    override val method = PaymentMethod.PAYPAL\n"
            "    override suspend fun authorize(amountCents: Long, details: PaymentDetails) = ...\n"
            "}\n"
            "\n"
            "// 3. الموجه (PaymentRouter) مغلق تماماً للتعديل ومفتوح للتوسيع (OCP):\n"
            "class PaymentRouter @Inject constructor(\n"
            "    private val strategies: Set<@JvmSuppressWildcards PaymentStrategy>\n"
            ") {\n"
            "    suspend fun routeAndPay(method: PaymentMethod, amountCents: Long, details: PaymentDetails): PaymentResult {\n"
            "        val strategy = strategies.firstOrNull { it.method == method }\n"
            "            ?: return PaymentResult.Error(\"Payment method not supported\")\n"
            "        return strategy.authorize(amountCents, details)\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Strategy-based payment routing implements OCP by abstracting providers behind a common `PaymentStrategy` interface. A `PaymentRouter` delegates payments to the matching strategy at runtime. New payment methods are introduced by adding new strategy classes without modifying, recompiling, or risking regressions in existing payment code.",
        "best_answer": (
            "Strategy-based payment routing is the premier textbook demonstration of the Open/Closed Principle (OCP) in production architecture.\n\n"
            "1. **The Anti-Pattern (Closed to Extension, Open to Modification)**:\n"
            "   - A centralized `PaymentManager` uses a massive `when(type)` statement branching into credit card, PayPal, and crypto logic.\n   - Every time a product manager requests Apple Pay or a regional provider, engineers must edit `PaymentManager.kt`. This introduces regression risks to existing revenue streams, causes Git merge conflicts, and invalidates existing payment test suites.\n\n"
            "2. **The OCP Architecture (Open to Extension, Closed to Modification)**:\n"
            "   - **Abstractions**: Define a `PaymentStrategy` interface with `authorize(amount, details)`.\n   - **Concrete Strategies**: Each provider is encapsulated in an isolated class: `StripeStrategy`, `PayPalStrategy`, `GooglePayStrategy`.\n   - **The Open Router**: The `PaymentRouter` depends strictly on a collection of injected strategies (`Set<PaymentStrategy>`), selecting the appropriate handler by querying `strategy.method == requestedMethod`.\n\n"
            "Adding a new provider requires creating a new class and registering it with Dagger/Hilt; the core `PaymentRouter` and existing providers remain 100% untouched and closed to modification."
        ),
        "deep_answer": (
            "Under the hood, Dagger/Hilt's **Multibindings (`@IntoSet`)** perfectly operationalizes this pattern. "
            "A feature module can define `class KlarnaStrategy : PaymentStrategy` and bind it into the multibinding set inside its own internal Hilt module. "
            "The core `:feature:payment` module doesn't even have a compile-time dependency on Klarna's SDK! "
            "Dagger collects all strategies at application assembly time, realizing true runtime extensibility without coupling.\n\n"
            "In testing, verifying `PaymentRouter` requires a simple unit test with mock/fake strategies to ensure it returns the correct error when a method is unsupported, while each strategy's network integration is tested in complete isolation."
        ),
        "follow_ups": [
            {
                "question": "How do you handle provider-specific input fields (e.g. CVV vs PayPal token)?",
                "answer": "By modeling payment credentials as a sealed class hierarchy `PaymentCredentials` (`CreditCard(number, cvv)`, `PayPal(token)`). Each strategy inspects its expected credential type safely."
            },
            {
                "question": "How does Dagger `@IntoSet` multibinding support OCP?",
                "answer": "It allows independent modules to contribute their strategy implementations to a shared `Set<PaymentStrategy>` without central code having to explicitly instantiate or list them."
            }
        ]
    },
    {
        "id": "SOL-13",
        "arabic_explanation": (
            "لماذا قد يؤدي إنشاء واجهة (Interface) لكل كلاس إلى تدهور التصميم وجعله أسوأ (Interface Exhaustion / Over-abstraction)؟\n\n"
            "1. ظاهرة الـ Interface-itis (الإفراط في إنشاء الواجهات):\n   - بعض المطورين يعتقدون خطأً أن الاحترافية تعني كتابة `interface UserProfileUseCase` ومعه `class UserProfileUseCaseImpl`، و `interface CartCalculator` ومعه `class CartCalculatorImpl` لكل كلاس في التطبيق!\n\n"
            "2. لماذا يجعل هذا التصميم أسوأ؟\n   - **مضاعفة حجم وتعقيد الكود بلا داعٍ (Double the Code / Navigational Friction)**: يتضاعف عدد ملفات المشروع بنسبة 100%. عند الضغط على الدالة في Android Studio (Ctrl+B)، لا تذهب مباشرة للكود الحقيقي بل للـ Interface الفارغ، مما يشتت المطورين.\n   - **تضخم تكلفة الصيانة وتوليد الكود (Maintenance & DI Overhead)**: يتطلب كل Interface كتابة سطر `@Binds` إضافي في Dagger/Hilt، مما يزيد من وقت الـ Annotation Processing وحجم ملفات الـ DEX.\n   - **تجريد زائف (False Abstraction)**: التجريد الذي ليس له سوى تطبيق حقيقي وحيد ولن يتغير أبداً هو تجريد وهمي لا يقدم أي قيمة تعددية (Polymorphism).\n\n"
            "3. متى ننشئ Interface؟\n   - فقط عند وجود حدود معمارية حقيقية (Clean Architecture DIP)، أو وجود تطبيقات متعددة بالفعل (Polymorphism)، أو لعزل خدمات النظام الخارجية الصعبة."
        ),
        "practical_walkthrough": (
            "المقارنة بين البويلربليت غير المجدي والتصميم البراغماتي النظيف:\n"
            "```kotlin\n"
            "// ❌ OVER-ABSTRACTION: واجهة عقيمة لكل كلاس UseCase بسيط:\n"
            "interface CalculateTaxUseCase {\n"
            "    fun execute(subtotal: Long): Long\n"
            "}\n"
            "class CalculateTaxUseCaseImpl : CalculateTaxUseCase {\n"
            "    override fun execute(subtotal: Long): Long = (subtotal * 0.15).toLong()\n"
            "}\n"
            "// بالإضافة لكتابة Hilt Module كامل لربط Interface بـ Impl لمجرد عملية حسابية!\n"
            "\n"
            "// ✅ تصميم نقي وعملي: الكلاس الملموس كافٍ ومثالي وقابل للاختبار الفوري:\n"
            "class CalculateTaxUseCase {\n"
            "    operator fun invoke(subtotal: Long): Long = (subtotal * 0.15).toLong()\n"
            "}\n"
            "// في الـ Test: يتم استدعاؤه فورياً: CalculateTaxUseCase().invoke(100L) دون أي Mocking أو DI!\n"
            "```"
        ),
        "quick_answer": "Creating an interface for every class doubles file counts, introduces IDE navigation friction, adds redundant Dagger/Hilt binding boilerplate, and creates 'false abstractions' with no polymorphic value. Concrete classes are simpler, faster to compile, and trivially testable in modern Kotlin.",
        "best_answer": (
            "The dogmatic practice of creating an interface for every single concrete class (the `IFoo` / `FooImpl` anti-pattern) harms codebases through cognitive friction, maintenance bloat, and compile-time costs.\n\n"
            "1. **Navigational Friction & Cognitive Overhead**: It doubles the file count in the project. When developers navigate code in Android Studio ('Go to Implementation'), they are constantly routed through empty interface definitions rather than directly to the executing code.\n\n"
            "2. **False Abstraction**: An interface that has exactly one implementation and will only ever have one implementation is not an abstraction—it is redundant ceremony. True abstractions emerge from polymorphism or strict dependency inversion boundaries, not mechanical habits.\n\n"
            "3. **Build & Dagger Overhead**: Every 1-to-1 interface requires an explicit `@Binds` declaration in a Dagger module, bloating generated annotation processor code (KSP) and increasing APK DEX method counts.\n\n"
            "In modern Kotlin, concrete classes are open to testing (instantiating pure classes directly or using MockK), meaning speculative interfaces offer zero testing benefit for pure business classes like Use Cases."
        ),
        "deep_answer": (
            "Historically, Java codebases relied on interfaces because Java proxies (and legacy Mockito) could not mock final or concrete classes without bytecode manipulation tools like PowerMock. "
            "In modern Android with Kotlin and contemporary testing tools, this technical constraint no longer exists.\n\n"
            "Furthermore, senior architects distinguish between **API Boundaries** and **Internal Implementation Details**. "
            "Interfaces belong at architectural boundaries (such as a Domain Repository consumed by a ViewModel across a multi-module boundary). "
            "Within the boundaries of a single cohesive module, internal helper classes, validators, and single-purpose use cases should remain concrete until polymorphism is genuinely required."
        ),
        "follow_ups": [
            {
                "question": "What is the 'Rule of Three' regarding abstractions?",
                "answer": "Do not extract an abstraction or interface until you find yourself writing the same code or needing polymorphism for the third time. Premature abstraction is worse than slight duplication."
            },
            {
                "question": "Does creating an interface make code automatically decoupled?",
                "answer": "No. If an interface leaks implementation details in its method signatures or exceptions (e.g. `fun fetchSqliteUser()`), it is tightly coupled despite being an interface."
            }
        ]
    },
    {
        "id": "SOL-14",
        "arabic_explanation": (
            "كيف يدعم Hilt ربط التبعيات (Dependency Wiring) دون أن يضمن تلقائياً تطبيق مبدأ عكس التبعية (DIP)؟\n\n"
            "1. ما الذي يفعله Hilt فعلياً؟\n   - Hilt هو مكتبة لإدارة وتوليد **حقن التبعيات (Dependency Injection Container)** في وقت التجميع (Compile-time).\n   - يحل مشكلة الـ Wiring: إنشاء الكائنات، إدارة دورات حياتها (Singleton, ActivityScoped, ViewModelScoped)، وتمريرها في الـ Constructors تلقائياً.\n\n"
            "2. كيف يمكن استخدام Hilt مع انتهاك صارخ لمبدأ DIP؟\n   - يمكنك استخدام Hilt لحقن كلاس ملموس مباشر منخفض المستوى في كلاس عالي المستوى:\n     `class ProfileViewModel @Inject constructor(val api: RetrofitUserApi, val dao: UserDao)`.\n   - في هذه الحالة: Hilt يعمل بنجاح 100% ويقوم بحقن الـ Api والـ Dao في الـ ViewModel.\n   - **ولكن مبدأ DIP منتهك بالكامل!** الـ ViewModel عالي المستوى مرتبط بشكل وثيق بـ Retrofit و Room دون أي Interface أو تجريد وسيط!\n\n"
            "3. كيف تستخدم Hilt لضمان DIP؟\n   - باستخدام وسم **`@Binds`** داخل Hilt Module لربط الـ Interface المجرد في الـ Domain بالتنفيذ الحقيقي في الـ Data، وحقن الـ Interface فقط في الـ ViewModel."
        ),
        "practical_walkthrough": (
            "المقارنة بين Hilt يكسر DIP و Hilt يحقق DIP عبر @Binds:\n"
            "```kotlin\n"
            "// ❌ Hilt مستخدم بنجاح لكنه ينتهك DIP (حقن كلاسات ملموسة منخفضة المستوى مباشرة):\n"
            "@HiltViewModel\n"
            "class BadViewModel @Inject constructor(\n"
            "    private val remoteApi: RetrofitOrderApi, // 💥 كلاس شبكة ملموس!\n"
            "    private val roomDb: AppDatabase          // 💥 كلاس قاعدة بيانات ملموس!\n"
            ") : ViewModel() { ... }\n"
            "\n"
            "// ✅ Hilt يفرض DIP بنجاح عبر ربط الـ Abstractions:\n"
            "// 1. الـ ViewModel يعتمد فقط على Interface مجرد:\n"
            "@HiltViewModel\n"
            "class GoodViewModel @Inject constructor(\n"
            "    private val orderRepository: OrderRepository // Abstraction نقي\n"
            ") : ViewModel() { ... }\n"
            "\n"
            "// 2. Hilt Module يربط الـ Interface بالتنفيذ في طبقة Data عبر @Binds:\n"
            "@Module\n"
            "@InstallIn(SingletonComponent::class)\n"
            "abstract class OrderDataModule {\n"
            "    @Binds\n"
            "    abstract fun bindOrderRepository(\n"
            "        impl: OrderRepositoryImpl\n"
            "    ): OrderRepository // يضمن تطبيق DIP بشكل كامل!\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Hilt is a Dependency Injection tool that automates object creation and graph wiring, but it does not enforce architectural direction. If a developer injects concrete classes like `RetrofitApi` or `RoomDao` directly into a ViewModel, Hilt successfully wires dependencies while completely violating the Dependency Inversion Principle (DIP).",
        "best_answer": (
            "Hilt is a creational wiring mechanism, not an architectural governor. It automates Dependency Injection (DI), but **DI is agnostic to the Dependency Inversion Principle (DIP)**.\n\n"
            "A developer can build a 100% functional Hilt dependency graph that aggressively violates DIP:\n"
            "```kotlin\n"
            "@HiltViewModel\n"
            "class CheckoutViewModel @Inject constructor(\n"
            "    val retrofit: RetrofitOrderService, // Concrete detail\n"
            "    val roomDao: OrderDao               // Concrete detail\n"
            ") : ViewModel()\n"
            "```\n"
            "Hilt compiles cleanly, injects instances, and resolves scopes. Yet, the high-level presentation layer is directly coupled to low-level network and database infrastructure details, destroying JVM unit testability and violating DIP.\n\n"
            "To guarantee DIP within Hilt:\n"
            "1. High-level consumers must declare dependencies as **abstract interfaces** (`OrderRepository`).\n"
            "2. Hilt Modules must use **`@Binds`** to map the abstract interface to its concrete data layer implementation (`OrderRepositoryImpl`)."
        ),
        "deep_answer": (
            "Under the hood, Hilt generates factory classes (`CheckoutViewModel_Factory.java`) based strictly on what is declared in constructor signatures. "
            "Hilt has no built-in lint rules preventing ViewModels from injecting Retrofit services or SQLite databases.\n\n"
            "To prevent Hilt from facilitating DIP violations in large enterprise teams, we enforce architectural constraints using **Gradle Module boundaries** and **Konsist tests**:\n"
            "- Feature modules (`:feature:checkout`) do not have a Gradle dependency on network or database modules, making it impossible for Hilt constructors to reference `RetrofitOrderService`.\n"
            "- Konsist tests assert that all constructor parameters in `@HiltViewModel` classes are either interfaces or Use Cases residing in domain modules."
        ),
        "follow_ups": [
            {
                "question": "What is the difference between `@Provides` and `@Binds` in Hilt regarding DIP?",
                "answer": "`@Binds` is used specifically to bind an abstract interface to a concrete implementation, promoting DIP and generating zero bytecode boilerplate. `@Provides` is used for creating instances requiring builder or manual setup logic (like configuring Retrofit or Room)."
            },
            {
                "question": "How can Gradle modularization prevent Hilt from violating DIP?",
                "answer": "By removing dependencies between the feature module and the data/network modules. If the feature module cannot see `RetrofitService`, Hilt cannot inject it into the feature's ViewModel."
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

    for item in SOL_08_14:
        by_id[item["id"]] = item

    output = [by_id[k] for k in sorted(by_id.keys())]
    DATA_FILE.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {DATA_FILE} with questions SOL-08 to SOL-14. Total questions: {len(output)}")

if __name__ == "__main__":
    main()
