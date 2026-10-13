#!/usr/bin/env python3
"""Generator for PAT-01 through PAT-06 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "pat.json"

PAT_01_06 = [
    {
        "id": "PAT-01",
        "arabic_explanation": (
            "ما هو نمط التصميم (Design Pattern) وكيف يختلف جوهرياً عن المعمارية (Architecture)؟\n\n"
            "1. ما هي المعمارية (Architecture - النظرة الشاملة من أعلى Macro)؟\n   - المعمارية هي **المخطط الهيكلي العام للبرنامج (System Blueprint)**.\n   - تحدد: كيفية تقسيم النظام ككل إلى طبقات (Presentation, Domain, Data)، اتجاه تدفق البيانات والتبعيات (Clean Architecture / MVI)، وكيف تتواصل الموديولات الكبيرة مع بعضها.\n   - قرارات المعمارية صعبة ومكلفة التغيير بعد اتخاذها؛ تغيير المعمارية يشبه تغيير أساسات المبنى بالكامل.\n\n"
            "2. ما هو نمط التصميم (Design Pattern - النظرة الدقيقة الموضعية Micro)؟\n   - نمط التصميم هو **حل نموذجي قابل لإعادة الاستخدام لمشكلة برمجية شائعة ومحددة تظهر داخل كود كلاس أو كلاسين**.\n   - أمثلة: كيفية إنشاء كائن معقد (Builder / Factory)، كيفية مطابقة واجهة غير متوافقة (Adapter)، أو كيفية إشعار عدة كائنات بحدث ما (Observer).\n   - أنماط التصميم تقع *داخل* المعمارية ويمكن استبدالها أو تعديلها موضعياً بسهولة.\n\n"
            "3. الخلاصة:\n   - المعمارية تجيب على: *\"كيف يتدفق النظام ككل وتتوزع الطبقات؟\"*\n   - نمط التصميم يجيب على: *\"كيف تحل كلاسات هذه الميزة مشكلة محددة في الكود؟\"*"
        ),
        "practical_walkthrough": (
            "المقارنة العملية بين القرار المعماري ونمط التصميم في تطبيق Android:\n"
            "```kotlin\n"
            "// 1. قرار معماري (Architecture): اختيار Clean Architecture و UDF:\n"
            "// الطبقات مقسمة إلى Presentation و Domain و Data مع تدفق أحادي الاتجاه:\n"
            "class CheckoutViewModel(private val checkoutUseCase: CheckoutUseCase) : ViewModel() {\n"
            "    val uiState: StateFlow<CheckoutUiState> = ...\n"
            "}\n"
            "\n"
            "// 2. نمط تصميم موضعي (Design Pattern - Strategy Pattern):\n"
            "// داخل طبقة Data، يتم استخدام نمط Strategy لاختيار وسيلة الدفع المناسبة:\n"
            "interface PaymentStrategy {\n"
            "    suspend fun pay(amount: Long): PaymentResult\n"
            "}\n"
            "class StripeStrategy : PaymentStrategy { ... }\n"
            "class PayPalStrategy : PaymentStrategy { ... }\n"
            "// هذا النمط يعيش داخل تفاصيل طبقة Data ولا يؤثر على هيكل المعمارية العام للنظام!\n"
            "```"
        ),
        "quick_answer": "Architecture is the macro-level system blueprint defining global layers, module boundaries, and dependency directions (e.g. Clean Architecture, MVI). Design patterns are micro-level, localized templates solving specific recurring object-oriented problems within classes (e.g. Builder, Strategy, Adapter).",
        "best_answer": (
            "The distinction between Architecture and Design Patterns is fundamentally a matter of scope and structural impact.\n\n"
            "1. **Architecture (Macro-Level / System Blueprint)**:\n   - Defines the high-level organization of the entire software system.\n   - Establishes foundational layers (Presentation, Domain, Data), dependency boundaries, data flow rules (Unidirectional Data Flow), and modularization strategy.\n   - Architectural decisions are costly and difficult to change once implemented (e.g. migrating from Monolithic MVC to Multi-Module Clean Architecture).\n   - Answers: *'Where do responsibilities live and in which direction does information flow across the app?'*\n\n"
            "2. **Design Patterns (Micro-Level / Tactical Solutions)**:\n   - Localized, reusable idioms solving specific recurring design challenges between collaborating classes.\n   - Examples: Using the Builder pattern for complex notification construction, the Adapter pattern for converting third-party analytics APIs, or the Strategy pattern for dynamic fee calculations.\n   - Tactical decisions that can be refactored within a single package without destabilizing the broader system.\n   - Answers: *'How should these specific objects collaborate to solve a localized problem?'*"
        ),
        "deep_answer": (
            "A helpful mental model is urban planning: Architecture is the zoning laws, highway networks, and utility grids of a city. Design patterns are the architectural blueprints for individual houses, doorways, and interior plumbing.\n\n"
            "Architecture dictates the constraints within which design patterns operate. "
            "For example, inside a Clean Architecture system, you might employ the **Repository pattern** to mediate data access, the **Factory pattern** to instantiate network decoders, and the **Observer pattern** (`Flow`) to project UI state. "
            "The design patterns live harmoniously within the architectural boundaries established by the system."
        ),
        "follow_ups": [
            {
                "question": "Can a bad design pattern ruin good architecture?",
                "answer": "Yes. If an anti-pattern like a monolithic God-Singleton is introduced, it creates hidden shared mutable state across architectural boundaries, corrupting the Clean Architecture dependency rule."
            },
            {
                "question": "Is the Repository pattern an architectural pattern or a design pattern?",
                "answer": "It functions at both levels: tactically as a mediator design pattern abstracting data access, and architecturally as the foundational boundary between Data and Domain layers."
            }
        ]
    },
    {
        "id": "PAT-02",
        "arabic_explanation": (
            "المقارنة بين فئات أنماط التصميم الثلاث (Gang of Four): الإنشائية (Creational)، الهيكلية (Structural)، والسلوكية (Behavioral):\n\n"
            "1. الأنماط الإنشائية (Creational Patterns):\n   - **الهدف**: التحكم في **كيفية إنشاء الكائنات وإدارتها** دون ربط الكود بتفاصيل الـ new المباشرة.\n   - **أمثلة شهيرة في أندرويد**:\n     * **Singleton**: نسخة واحدة فقط في الذاكرة (`object` في كوتلن، Room Database).\n     * **Factory / Abstract Factory**: إنشاء كائنات من عائلة معينة دون تحديد كلاساتها الملموسة (`ViewModelProvider.Factory`).\n     * **Builder**: بناء كائنات معقدة خطوة بخطوة (`NotificationCompat.Builder`, `AlertDialog.Builder`).\n\n"
            "2. الأنماط الهيكلية (Structural Patterns):\n   - **الهدف**: تنظيم **العلاقات والتركيب بين الكلاسات والكائنات** لتكوين هياكل أكبر وأكثر مرونة.\n   - **أمثلة شهيرة في أندرويد**:\n     * **Adapter**: التوفيق بين واجهتين غير متوافقتين (`RecyclerView.Adapter`).\n     * **Facade**: توفير واجهة بسيطة وموحدة لنظام معقد أو SDK خارجي.\n     * **Decorator**: إضافة سلوك لكائن ديناميكياً دون وراثة (`OkHttp Interceptor`).\n     * **Proxy**: التحكم في الوصول لكائن آخر (مثل Binder IPC في نظام أندرويد).\n\n"
            "3. الأنماط السلوكية (Behavioral Patterns):\n   - **الهدف**: تنظيم **طرق التواصل وتوزيع المسؤوليات وتدفق البيانات** بين الكائنات.\n   - **أمثلة شهيرة في أندرويد**:\n     * **Observer**: مراقبة تغيرات البيانات والتفاعل معها (`Flow`, `LiveData`, `StateFlow`).\n     * **Strategy**: تبديل الخوارزميات وطرق المعالجة في وقت التشغيل (طرق الدفع).\n     * **State**: تغيير سلوك الكائن عند تغير حالته الداخلية (آلة حالات المشغل).\n     * **Chain of Responsibility**: تمرير الطلب عبر سلسلة معالجات (`OkHttp Interceptor Chain`)."
        ),
        "practical_walkthrough": (
            "أمثلة تمثل الفئات الثلاث في كود Android:\n"
            "```kotlin\n"
            "// 1. CREATIONAL: Builder Pattern لبناء إشعار معقد بأمان:\n"
            "val notification = NotificationCompat.Builder(context, CHANNEL_ID)\n"
            "    .setContentTitle(\"Order Shipped\")\n"
            "    .setSmallIcon(R.drawable.ic_truck)\n"
            "    .setAutoCancel(true)\n"
            "    .build()\n"
            "\n"
            "// 2. STRUCTURAL: Facade Pattern لتبسيط SDK خرائط معقد خلف واجهة بسيطة:\n"
            "class LocationTrackerFacade(private val fusedClient: FusedLocationProviderClient) {\n"
            "    suspend fun getFreshCoordinates(): Coordinates = ...\n"
            "}\n"
            "\n"
            "// 3. BEHAVIORAL: Observer Pattern لمراقبة تغيرات تدفق البيانات:\n"
            "viewModel.userFlow\n"
            "    .onEach { user -> renderProfile(user) }\n"
            "    .launchIn(lifecycleScope)\n"
            "```"
        ),
        "quick_answer": "Creational patterns govern object instantiation (Singleton, Factory, Builder). Structural patterns govern class and object composition to form larger systems (Adapter, Facade, Decorator). Behavioral patterns govern communication algorithms and responsibility distribution between collaborating objects (Observer, Strategy, State).",
        "best_answer": (
            "The Gang of Four (GoF) classifies design patterns into three distinct categories based on their intent:\n\n"
            "1. **Creational Patterns (Object Instantiation Mechanisms)**:\n   - Abstract the instantiation process, making systems independent of how objects are created, composed, and represented.\n   - *Android Examples*:\n     * **Singleton**: Single shared instance (`object`, Room database instance).\n     * **Builder**: Multi-step configuration of immutable objects (`NotificationCompat.Builder`, `AlertDialog.Builder`).\n     * **Factory Method**: Delegating instantiation to subclasses or providers (`ViewModelProvider.Factory`).\n\n"
            "2. **Structural Patterns (Composition & Relationships)**:\n   - Deal with how classes and objects are assembled into larger, decoupled structures.\n   - *Android Examples*:\n     * **Adapter**: Converts one interface into another that clients expect (`RecyclerView.Adapter`).\n     * **Facade**: Exposes a simplified, cohesive API over a complex underlying subsystem (wrapping multi-step third-party SDKs).\n     * **Decorator**: Dynamically augments behavior without subclassing (`OkHttp Interceptors`).\n\n"
            "3. **Behavioral Patterns (Communication & Algorithms)**:\n   - Deal with algorithms, assignments of responsibility, and communication protocols between objects.\n   - *Android Examples*:\n     * **Observer**: Publish-subscribe reactive notifications (`StateFlow`, `SharedFlow`, `LiveData`).\n     * **Strategy**: Encapsulating interchangeable algorithms selected at runtime (Payment providers, sorting algorithms).\n     * **Chain of Responsibility**: Passing a request along a chain of handlers (`OkHttp Interceptor Chain`)."
        ),
        "deep_answer": (
            "Modern Kotlin has absorbed several GoF patterns directly into language syntax:\n"
            "- **Singleton**: Native `object` keyword.\n"
            "- **Decorator / Adapter**: First-class **Class Delegation** (`class Foo(bar: Bar) : Bar by bar`) and **Extension Functions**.\n"
            "- **Strategy**: Passing higher-order functions or lambdas (`(T) -> Boolean`) directly instead of creating single-method interface hierarchies.\n"
            "- **Builder**: Named parameters and default arguments (`data class Config(val timeout: Long = 5000, val retries: Int = 3)`).\n\n"
            "Understanding which patterns are native language idioms versus structural components helps engineers write cleaner code without unnecessary boilerplate classes."
        ),
        "follow_ups": [
            {
                "question": "How do Kotlin default arguments reduce the need for the Builder pattern?",
                "answer": "Data classes with default parameter values and named arguments allow instantiating objects with any combination of optional parameters directly in a single call, eliminating the need for separate Builder classes for basic data structures."
            },
            {
                "question": "Which category does OkHttp's Interceptor mechanism belong to?",
                "answer": "It combines both Structural (Decorator pattern, wrapping requests/responses) and Behavioral (Chain of Responsibility pattern, passing the request through the interceptor pipeline)."
            }
        ]
    },
    {
        "id": "PAT-03",
        "arabic_explanation": (
            "شرح الأنماط الإنشائية الأساسية: Singleton و Factory و Abstract Factory و Builder، ومتى نستخدم كلاً منها في Android:\n\n"
            "1. نمط الكائن الأحادي (Singleton Pattern):\n   - **الهدف**: ضمان وجود **نسخة واحدة فقط** من الكائن في الذاكرة طوال حياة التطبيق وتوفير نقطة وصول عامة له.\n   - **في Kotlin**: يُبنى بكلمة `object` أو عبر `@Singleton` في Hilt.\n   - **الاستخدام**: قواعد بيانات Room، عميل Retrofit/OkHttp، ومدير الـ Analytics.\n\n"
            "2. نمط المصنع (Factory Method Pattern):\n   - **الهدف**: تفويض إنشاء الكائن إلى دالة أو كلاس مصنع بدلاً من استدعاء الـ Constructor المباشر.\n   - **في Android**: `ViewModelProvider.Factory` لإنشاء كائنات ViewModel تحتاج لمعاملات في الـ Constructor.\n\n"
            "3. نمط المصنع المجرد (Abstract Factory Pattern):\n   - **الهدف**: مصنع للمصانع! إنشاء **عائلات كاملة من الكائنات المرتبطة** دون تحديد كلاساتها الملموسة.\n   - **الاستخدام**: عائلة مكونات واجهة تختلف حسب الثيم (DarkUIFactory ينشئ DarkButton و DarkDialog، بينما LightUIFactory ينشئ LightButton و LightDialog).\n\n"
            "4. نمط الباني (Builder Pattern):\n   - **الهدف**: بناء كائنات معقدة تحتوي على العديد من المعاملات الاختيارية خطوة بخطوة وتأكيد بنائها في النهاية بـ `.build()`.\n   - **في Android**: `NotificationCompat.Builder`, `AlertDialog.Builder`, `OkHttpClient.Builder`."
        ),
        "practical_walkthrough": (
            "أمثلة كود توضح الأنماط الإنشائية الأربعة في Android:\n"
            "```kotlin\n"
            "// 1. SINGLETON (عبر Hilt أو object):\n"
            "@Singleton\n"
            "class AppDatabaseManager @Inject constructor(@ApplicationContext context: Context) { ... }\n"
            "\n"
            "// 2. FACTORY METHOD: مصنع لإنشاء كائنات من نوع محدد بناءً على إدخال:\n"
            "interface PaymentGatewayFactory {\n"
            "    fun create(type: PaymentType): PaymentGateway\n"
            "}\n"
            "\n"
            "// 3. ABSTRACT FACTORY: مصنع لعائلات كائنات مرتبطة:\n"
            "interface UIThemeFactory {\n"
            "    fun createButton(): AppButton\n"
            "    fun createDialog(): AppDialog\n"
            "}\n"
            "class DarkThemeFactory : UIThemeFactory { ... }\n"
            "class LightThemeFactory : UIThemeFactory { ... }\n"
            "\n"
            "// 4. BUILDER: بناء كائن OkHttpClient بإعدادات متعددة:\n"
            "val client = OkHttpClient.Builder()\n"
            "    .connectTimeout(30, TimeUnit.SECONDS)\n"
            "    .readTimeout(30, TimeUnit.SECONDS)\n"
            "    .addInterceptor(AuthInterceptor())\n"
            "    .build()\n"
            "```"
        ),
        "quick_answer": "Singleton ensures a single shared instance (Room DB, OkHttp). Factory creates single objects hiding instantiation logic (`ViewModelProvider.Factory`). Abstract Factory creates families of related objects (Theme components). Builder constructs complex multi-parameter objects step-by-step (`NotificationCompat.Builder`).",
        "best_answer": (
            "These four creational patterns govern object creation boundaries in Android development:\n\n"
            "1. **Singleton**: Guarantees a class has only one instance per process lifecycle. In Kotlin, implemented natively via `object` or managed via `@Singleton` in Dagger/Hilt. Best for expensive, stateful shared resources (e.g. SQLite connection pools, OkHttp client engines).\n\n"
            "2. **Factory Method**: Defines an interface for creating an object, but lets subclasses or specialized providers decide which class to instantiate. In Android, `ViewModelProvider.Factory` creates ViewModels parameterized with dependencies that standard system reflection cannot resolve.\n\n"
            "3. **Abstract Factory**: Provides an interface for creating **families of related or dependent objects** without specifying their concrete classes. For instance, a `DesignSystemFactory` supplying matching typography, buttons, and dialogs tailored for distinct brand flavors (e.g. `ConsumerThemeFactory` vs `EnterpriseThemeFactory`).\n\n"
            "4. **Builder**: Separates the construction of a complex object from its representation, allowing step-by-step assembly and producing an immutable result via `.build()`. Ubiquitous across Android framework APIs (`NotificationCompat.Builder`, `AlertDialog.Builder`, `WorkRequest.Builder`)."
        ),
        "deep_answer": (
            "The **Builder Pattern vs Kotlin Named Arguments** trade-off is a frequent design debate. "
            "For simple domain data classes, a builder is an anti-pattern in Kotlin: `data class UserConfig(val timeout: Long = 10, val retries: Int = 3)` provides built-in validation and optionality in a single line.\n\n"
            "However, the Builder pattern remains vital in SDK design when:\n"
            "- Construction requires cross-field validation invariants checked at commit time (`build()`).\n"
            "- Step order matters or certain combinations are mutably staged before creating an immutable thread-safe core (e.g. `OkHttpClient.Builder`).\n"
            "- Java interoperability is required, as Java cannot consume Kotlin default argument bytecode ergonomically without `@JvmOverloads`."
        ),
        "follow_ups": [
            {
                "question": "Why can global Singleton objects cause issues in unit tests?",
                "answer": "Global singletons retain state across test runs, causing tests to become order-dependent and flaky. We mitigate this by scoping singletons via Hilt components that are recreated per test."
            },
            {
                "question": "What is the difference between Factory and Abstract Factory?",
                "answer": "Factory Method creates a single product. Abstract Factory is a factory of factories, creating an entire suite of related products that belong to the same family or theme."
            }
        ]
    },
    {
        "id": "PAT-04",
        "arabic_explanation": (
            "شرح الأنماط الهيكلية الأساسية: Adapter و Facade و Decorator و Proxy، وأين تظهر في Android:\n\n"
            "1. نمط المحول (Adapter Pattern):\n   - **الهدف**: التوفيق والربط بين واجهتين غير متوافقتين بحيث تعملان معاً بسلاسة.\n   - **في Android**: `RecyclerView.Adapter` يحول قائمة بيانات من الـ Domain (`List<Product>`) إلى `ViewHolders` و `Views` يفهمها نظام Android UI.\n\n"
            "2. نمط الواجهة البسيطة (Facade Pattern):\n   - **الهدف**: توفير واجهة موحدة وبسيطة لإخفاء تعقيد نظام فرعي ضخم (Subsystem) أو SDK خارجي فوضوي.\n   - **في Android**: بناء `LocationTrackerFacade` يخفي تفاصيل `FusedLocationProviderClient`، و `SettingsClient`، وأذونات النظام، مقدماً دالة واحدة بسيطة: `suspend fun getCurrentLocation(): Location`.\n\n"
            "3. نمط الزخرفة (Decorator Pattern):\n   - **الهدف**: إضافة وظائف وسلوكيات جديدة لكائن موجود ديناميكياً في وقت التشغيل دون اللجوء للوراثة (Subclassing).\n   - **في Android**: `OkHttp Interceptors`؛ كل اعتراض يغلف الـ Request ويضيف عليه Headers أو Logging ويعيد تمريره للـ Chain.\n\n"
            "4. نمط الوكيل (Proxy Pattern):\n   - **الهدف**: توفير كائن بديل أو وكيل يتحكم في الوصول للكائن الأصلي (لأسباب أمنية، كاش، أو استدعاءات عبر العمليات IPC).\n   - **في Android**: كائنات الـ **AIDL / Binder Proxies**؛ عند طلب نظام أندرويد لـ `LocationManager`، يحصل التطبيق على Binder Proxy يتولى استدعاء نظام التشغيل عبر الـ IPC."
        ),
        "practical_walkthrough": (
            "أمثلة تمثل الأنماط الهيكلية الأربعة في كود Android:\n"
            "```kotlin\n"
            "// 1. ADAPTER: تحويل بيانات النطاق إلى Views:\n"
            "class ProductAdapter(private val items: List<Product>) : RecyclerView.Adapter<ProductViewHolder>() { ... }\n"
            "\n"
            "// 2. FACADE: تبسيط SDK معقد خلف دالة واحدة نقية:\n"
            "class SimpleAudioPlayerFacade(private val exoPlayer: ExoPlayer) {\n"
            "    fun playStream(url: String) {\n"
            "        exoPlayer.setMediaItem(MediaItem.fromUri(url))\n"
            "        exoPlayer.prepare()\n"
            "        exoPlayer.play()\n"
            "    }\n"
            "}\n"
            "\n"
            "// 3. DECORATOR: تزيين استجابات الشبكة بإضافة ترويسة أمان عبر OkHttp Interceptor:\n"
            "class AuthHeaderDecorator : Interceptor {\n"
            "    override fun intercept(chain: Interceptor.Chain): Response {\n"
            "        val decoratedRequest = chain.request().newBuilder()\n"
            "            .addHeader(\"Authorization\", \"Bearer token\")\n"
            "            .build()\n"
            "        return chain.proceed(decoratedRequest)\n"
            "    }\n"
            "}\n"
            "\n"
            "// 4. PROXY: حماية كائن ثقيل وتأجيل تحميله حتى أول استخدام (Virtual Proxy):\n"
            "val heavyAnalyticsService by lazy { HeavyAnalyticsService() } // كائن Proxy يوفر Lazy Initialization\n"
            "```"
        ),
        "quick_answer": "Adapter bridges incompatible interfaces (`RecyclerView.Adapter`). Facade provides a simplified unified API over complex subsystems (wrapping ExoPlayer or location APIs). Decorator dynamically wraps objects to add behaviors (`OkHttp Interceptors`). Proxy controls access to another object (Android Binder IPC, Lazy initialization).",
        "best_answer": (
            "Structural patterns organize relationships and boundaries between collaborating objects:\n\n"
            "1. **Adapter (Interface Conversion)**:\n   - Converts the interface of a class into another interface clients expect, allowing incompatible classes to work together.\n   - *Android Example*: `RecyclerView.Adapter` bridges arbitrary application domain datasets into Android layout `ViewHolders`.\n\n"
            "2. **Facade (Unified Simplicity)**:\n   - Exposes a simplified, cohesive high-level interface that masks the complexity of an intricate subsystem or convoluted third-party library.\n   - *Android Example*: A custom `BillingFacade` wrapping Google Play Billing SDK. The facade encapsulates connection lifecycles, purchase tokens, and acknowledging flows behind simple suspending calls: `suspend fun buy(sku: String): PurchaseResult`.\n\n"
            "3. **Decorator (Dynamic Behavioral Augmentation)**:\n   - Attaches additional responsibilities to an object dynamically without subclassing, wrapping the original instance.\n   - *Android Example*: `OkHttp Interceptors`. Each interceptor wraps HTTP requests and responses, adding caching headers, Gzip compression, or authentication tokens sequentially.\n\n"
            "4. **Proxy (Surrogate Access Control)**:\n   - Provides a placeholder or surrogate for another object to control access to it (e.g. Remote Proxy, Virtual Proxy for lazy loading, Protection Proxy).\n   - *Android Example*: Android's **Binder IPC mechanism**. When an app invokes `LocationManager`, it communicates with an AIDL-generated local client Proxy that serializes calls across process boundaries into system server daemons."
        ),
        "deep_answer": (
            "Comparing **Adapter vs Facade vs Decorator**:\n"
            "- *Adapter* changes an interface to match an existing specification without altering behavior.\n"
            "- *Facade* defines a *new, simpler* interface to reduce complexity across multiple classes.\n"
            "- *Decorator* preserves the *same* interface while dynamically enhancing behavior.\n\n"
            "In modern Kotlin, the **Decorator pattern** is elegantly built via Class Delegation: `class LoggingRepository(private val delegate: UserRepository) : UserRepository by delegate`. "
            "You only override the methods you wish to decorate with logging, while Kotlin delegates all other method calls automatically, cutting boilerplate to near zero."
        ),
        "follow_ups": [
            {
                "question": "What is the difference between Facade and Adapter?",
                "answer": "An Adapter matches an existing specific interface required by a client. A Facade defines a completely new, simplified interface to make a complex subsystem easier to consume."
            },
            {
                "question": "How does Kotlin's `by` keyword implement the Decorator pattern?",
                "answer": "By delegating interface methods to an internal wrapped instance (`by delegate`), allowing developers to override only the specific methods they want to decorate."
            }
        ]
    },
    {
        "id": "PAT-05",
        "arabic_explanation": (
            "شرح الأنماط السلوكية الأساسية: Observer و Strategy و State و Command و Chain of Responsibility في Android:\n\n"
            "1. نمط المراقب (Observer Pattern):\n   - **الهدف**: علاقة One-to-Many؛ عندما يتغير كائن (Subject)، يتم إشعار جميع المراقبين (Observers) المسجلين تلقائياً.\n   - **في Android**: قلب البرمجة التفاعلية (`StateFlow`, `SharedFlow`, `LiveData`, و `SnapshotState` في Compose).\n\n"
            "2. نمط الاستراتيجية (Strategy Pattern):\n   - **الهدف**: تغليف مجموعة من الخوارزميات المتبادلة في كلاسات منفصلة، واختيار الخوارزمية في وقت التشغيل.\n   - **في Android**: اختيار طريقة الدفع (Stripe vs PayPal)، أو اختيار طريقة ترتيب القائمة (حسب السعر vs التاريخ).\n\n"
            "3. نمط الحالة (State Pattern):\n   - **الهدف**: السماح لكائن بتغيير سلوكه بالكامل عندما تتغير حالته الداخلية (كأنه يغير كلاسه).\n   - **في Android**: آلة حالات مشغل الوسائط (`IdleState`, `BufferingState`, `PlayingState`, `PausedState`)؛ ضغط زر التشغيل في `PlayingState` يوقف المشغل، بينما ضغطه في `PausedState` يستأنف التشغيل.\n\n"
            "4. نمط الأمر (Command Pattern):\n   - **الهدف**: تغليف الطلب بالكامل في كائن مستقل، مما يتيح تأجيل تنفيذه، وضعه في طابور (Queue)، أو التراجع عنه (Undo/Redo).\n   - **في Android**: مهام `WorkManager` (WorkRequest) أو أحداث الـ MVI (`UiIntent`).\n\n"
            "5. نمط سلسلة المسؤولية (Chain of Responsibility):\n   - **الهدف**: تمرير الطلب عبر سلسلة من المعالجات (Handlers)؛ كل معالج يقرر معالجة الطلب أو تمريره لمن يليه.\n   - **في Android**: `OkHttp Interceptors Chain`، وتمرير أحداث اللمس (Touch Event Dispatching في View Hierarchy من ViewGroup إلى View)."
        ),
        "practical_walkthrough": (
            "أمثلة تمثل الأنماط السلوكية الخمسة في كود Android:\n"
            "```kotlin\n"
            "// 1. OBSERVER: اشتراك تفاعلي في تدفق الحالة:\n"
            "viewModel.uiState.onEach { render(it) }.launchIn(lifecycleScope)\n"
            "\n"
            "// 2. STRATEGY: استراتيجية فرز قابلة للتبديل في وقت التشغيل:\n"
            "val sortedList = list.sortedWith(if (sortByPrice) PriceComparator() else DateComparator())\n"
            "\n"
            "// 3. STATE: مشغل وسائط يغير سلوكه حسب حالته الداخلية:\n"
            "sealed interface PlayerState {\n"
            "    fun onPlayClicked(player: MediaPlayerContext)\n"
            "}\n"
            "class PausedState : PlayerState {\n"
            "    override fun onPlayClicked(player: MediaPlayerContext) { player.start(); player.setState(PlayingState()) }\n"
            "}\n"
            "class PlayingState : PlayerState {\n"
            "    override fun onPlayClicked(player: MediaPlayerContext) { player.pause(); player.setState(PausedState()) }\n"
            "}\n"
            "\n"
            "// 4. COMMAND: تغليف عملية حفظ قابلة للوضع في طابور WorkManager:\n"
            "val syncCommand = OneTimeWorkRequestBuilder<SyncWorker>().build()\n"
            "WorkManager.getInstance(context).enqueue(syncCommand)\n"
            "\n"
            "// 5. CHAIN OF RESPONSIBILITY: معالجة أحداث اللمس في Android:\n"
            "override fun dispatchTouchEvent(ev: MotionEvent): Boolean {\n"
            "    return if (onInterceptTouchEvent(ev)) onTouchEvent(ev) else child.dispatchTouchEvent(ev)\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Observer handles reactive 1-to-N updates (`Flow`, Compose State). Strategy swaps interchangeable algorithms (payment methods). State alters object behavior based on its internal state machine (media player states). Command encapsulates executable requests (`WorkManager`). Chain of Responsibility passes requests through sequential handlers (`OkHttp Interceptors`, Touch Dispatch).",
        "best_answer": (
            "Behavioral patterns govern communication protocols, algorithms, and state transitions between decoupled objects:\n\n"
            "1. **Observer**: Defines a one-to-many dependency where state mutations in a subject broadcast notifications to subscribers. The foundation of modern reactive Android (`StateFlow`, `LiveData`, and Compose's `SnapshotMutationPolicy`).\n\n"
            "2. **Strategy**: Encapsulates a family of algorithms into interchangeable classes conforming to a common contract. Consumers delegate execution to the strategy instance injected at runtime (e.g. routing between different payment gateways).\n\n"
            "3. **State**: Allows an object to alter its behavior when its internal state changes, behaving as if its underlying class transformed. Highly effective for complex state machines (e.g. `ExoPlayer` audio state transitions or Bluetooth connection sequences: `Disconnected`, `Scanning`, `Connecting`, `Connected`).\n\n"
            "4. **Command**: Encapsulates a request as an object with its own execution context, enabling parameterization, queuing, scheduling, and undo/redo operations. Embodied by Jetpack `WorkManager` (`OneTimeWorkRequest`) and MVI `Intent` actions.\n\n"
            "5. **Chain of Responsibility**: Decouples request senders from receivers by giving multiple handlers a chance to process the request sequentially along a pipeline. Embodied by **OkHttp Interceptor chains** and Android's **`dispatchTouchEvent()` hierarchy**."
        ),
        "deep_answer": (
            "Comparing **State vs Strategy** is a classic interview inquiry:\n"
            "- Both share an identical UML class diagram (Context delegating to an Interface with multiple implementations).\n"
            "- *The difference is intent and state transitions*:\n"
            "  * In **Strategy**, the client generally configures the strategy once (e.g. user chooses 'Pay with PayPal'), and strategies rarely know about other strategies.\n"
            "  * In **State**, the context changes states dynamically as events occur, and concrete state objects frequently trigger transitions to succeeding state objects (`PausedState` directly transitions context to `PlayingState`).\n\n"
            "In modern Kotlin, the State pattern is often formalized using **Sealed Interfaces with Reducer Functions** (`MVI`), achieving mathematical state determinism."
        ),
        "follow_ups": [
            {
                "question": "What is the key difference between State and Strategy patterns?",
                "answer": "Strategy encapsulates interchangeable algorithms usually chosen once by the client. State encapsulates dynamic state machine transitions where the object actively changes its behavior and transitions to new states as events occur."
            },
            {
                "question": "How does Android's Touch Event System implement Chain of Responsibility?",
                "answer": "A touch event starts at the Window, traverses down through nested `ViewGroup`s via `dispatchTouchEvent()` and `onInterceptTouchEvent()`, until a child view consumes it or passes it back up."
            }
        ]
    },
    {
        "id": "PAT-06",
        "arabic_explanation": (
            "أين يقع نمط المستودع (Repository Pattern) كنمط معماري ونمط وصول للبيانات (Architectural / Data-Access Pattern)؟\n\n"
            "1. موقع الـ Repository في البناء المعماري (Architectural Placement):\n   - يقع الـ Repository عند **الحد الفاصل (Boundary) بين طبقة النطاق (Domain) وطبقة البيانات (Data)**.\n   - في Clean Architecture:\n     * **الواجهة (Interface)** تقع في قلب طبقة الـ Domain.\n     * **التنفيذ الفعلي (Implementation)** يقع في طبقة الـ Data.\n\n"
            "2. دوره كنمط وصول للبيانات (Data-Access Pattern):\n   - يعمل كـ **وسيط مجرد (Mediator)** يتصرف وكأنه مجموعة كائنات محفوظة في الذاكرة (In-memory collection).\n   - يخفي تفاصيل كيفية استرجاع البيانات ومصادرها (SQLite, Retrofit, Preferences, Cache).\n   - يوحد منطق إدارة الكاش والـ Offline-first.\n\n"
            "3. لماذا لا نضع الـ Repository في طبقة الـ Presentation أو ككلاس مستقل في UI؟\n   - لأن وظيفته خدمة قواعد الأعمال، وليس الواجهات.\n   - عزل الـ Repository يتيح إعادة استخدامه عبر شاشات متعددة، وفي Background Workers، ومع الإشعارات دون تكرار كود التخزين والشبكة."
        ),
        "practical_walkthrough": (
            "تموضع الـ Repository في كود Clean Architecture عبر الطبقات:\n"
            "```kotlin\n"
            "// 1. في طبقة DOMAIN: العقد المجرد للبيانات:\n"
            "interface UserRepository {\n"
            "    fun observeUser(id: String): Flow<User>\n"
            "    suspend fun refreshUser(id: String): Result<Unit>\n"
            "}\n"
            "\n"
            "// 2. في طبقة DATA: تنفيذ الـ Repository وإدارة مصادر البيانات والكاش (SSOT):\n"
            "class UserRepositoryImpl @Inject constructor(\n"
            "    private val localDao: UserDao,       // مصدر بيانات محلي\n"
            "    private val remoteApi: UserApi       // مصدر بيانات خارجي\n"
            ") : UserRepository {\n"
            "    override fun observeUser(id: String): Flow<User> = localDao.getUser(id).map { it.toDomain() }\n"
            "    override suspend fun refreshUser(id: String): Result<Unit> = runCatching {\n"
            "        val networkDto = remoteApi.fetchUser(id)\n"
            "        localDao.insert(networkDto.toEntity())\n"
            "    }\n"
            "}\n"
            "\n"
            "// 3. في طبقة PRESENTATION: ViewModel يستهلك الـ Repository دون معرفة أي تفاصيل تخزين:\n"
            "@HiltViewModel\n"
            "class ProfileViewModel @Inject constructor(\n"
            "    private val userRepository: UserRepository\n"
            ") : ViewModel() { ... }\n"
            "```"
        ),
        "quick_answer": "The Repository pattern sits at the boundary between Domain and Data layers. In Clean Architecture, its interface lives in Domain (defining what data the business requires) and its implementation lives in Data (coordinating Room, Retrofit, and caching). It abstracts data storage behind an in-memory collection facade.",
        "best_answer": (
            "The Repository pattern operates simultaneously as an architectural boundary and a specialized data-access design pattern.\n\n"
            "1. **Architectural Placement (The Clean Boundary)**:\n   - Sits squarely at the demarcation line between **Domain and Data layers**.\n   - In adherence with the Dependency Inversion Principle, the **Repository Interface** resides in the Domain layer as an abstract business requirement.\n   - The **Repository Implementation** (`RepositoryImpl`) resides in the Data layer, depending on the Domain interface and concrete DataSources (Room, Retrofit, Datastore).\n\n"
            "2. **Data-Access Responsibilities (The Mediating Facade)**:\n   - Mediates between the domain and multiple raw data sources, masquerading as an in-memory collection (`Flow<T>`, `save()`, `delete()`).\n   - Implements the **Single Source of Truth (SSOT)**: managing offline-first persistence, cache invalidation, and background synchronization policies.\n   - Maps raw technical DTOs and SQLite entities into clean Domain Entities before emitting them upward."
        ),
        "deep_answer": (
            "A frequent question is whether each database table or API endpoint requires its own Repository. "
            "The answer is no. Under Domain-Driven Design (DDD) principles, a Repository should be modeled around an **Aggregate Root**.\n\n"
            "For example, in an e-commerce app, an `Order` aggregate root might involve `orders`, `order_items`, and `delivery_addresses` tables across SQLite, alongside two distinct REST APIs. "
            "A single `OrderRepository` orchestrates all these underlying tables and network endpoints, providing a unified `Order` entity to the domain. "
            "Creating a separate repository for each individual database table leaks database schema boundaries into business code."
        ),
        "follow_ups": [
            {
                "question": "What is an Aggregate Root in the context of Repositories?",
                "answer": "An entity that acts as the gateway to a cluster of associated objects (e.g. `Order` owns `OrderItem`). The Repository is created for the Aggregate Root, not for each internal child table."
            },
            {
                "question": "Why shouldn't a ViewModel query a DataSource directly?",
                "answer": "Because DataSources represent raw individual I/O channels (one API or one DAO). The Repository provides caching, orchestration, error translation, and SSOT guarantees that DataSources lack."
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

    for item in PAT_01_06:
        by_id[item["id"]] = item

    output = [by_id[k] for k in sorted(by_id.keys())]
    DATA_FILE.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {DATA_FILE} with questions PAT-01 to PAT-06. Total questions: {len(output)}")

if __name__ == "__main__":
    main()
