#!/usr/bin/env python3
"""Generator for PAT-07 through PAT-12 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "pat.json"

PAT_07_12 = [
    {
        "id": "PAT-07",
        "arabic_explanation": (
            "ما الذي يحققه نمط حقن التبعيات (Dependency Injection - DI كنمط تصميم) في تطبيقات Android؟\n\n"
            "1. ما هي المشكلة بدون حقن التبعيات؟\n   - عندما يقوم الكلاس بإنشاء التبعيات التي يحتاجها بنفسه داخل جسمه (`val api = Retrofit.Builder()...build()` أو `val repo = UserRepositoryImpl()`):\n   - **اقتران شديد (Hard Coupling)**: الكلاس ارتهن بكلاس ملموس محدد، ولا يمكن تبديله.\n   - **استحالة الـ Unit Testing**: لا يمكنك اختبار الكلاس بشكل معزول على الـ JVM، لأنك لا تستطيع استبدال `api` أو `db` بـ Fake أو Mock.\n   - **فوضى إدارة دورات الحياة (Lifecycle Chaos)**: كل كلاس ينشئ نسخته الخاصة، مما يكرر كائنات ثقيلة في الذاكرة.\n\n"
            "2. ما الذي يحققه نمط الـ Dependency Injection (DI)؟\n   - **فصل الإنشاء عن الاستخدام (Separation of Creation from Consumption)**: الكلاس يعلن فقط عما يحتاجه في الـ Constructor (`Constructor Injection`)، ويتولى مجمع خارجي (DI Container مثل Hilt/Koin) تزويده بها.\n   - **سهولة الاختبار الخارق (Testability)**: في الـ Unit Test، تمرر ببساطة `FakeUserRepository()` في الـ Constructor مباشرة دون الحاجة لأي مكتبات أو أطر عمل.\n   - **إدارة مركزية للـ Scopes ودورات الحياة**: ضمان مشاركة نسخة واحدة من كائن الـ Singleton وتحرير الكائنات المرتبطة بنشاط محدد عند انتهائه."
        ),
        "practical_walkthrough": (
            "المقارنة بين كلاس ينشئ تبعياته بنفسه وكلاس يعتمد على الـ Dependency Injection:\n"
            "```kotlin\n"
            "// ❌ بدون DI: كلاس ينشئ تبعياته بنفسه؛ اقتران صلب واستحالة للاختبار:\n"
            "class BadOrderViewModel : ViewModel() {\n"
            "    // إنشاء مباشر يربط الـ ViewModel بالسيرفر وقاعدة البيانات الحقيقية:\n"
            "    private val repository = OrderRepositoryImpl(RetrofitClient.api, AppDatabase.getDao())\n"
            "    // لا يمكن اختبار هذا الـ ViewModel على الـ JVM دون تشغيل قاعدة بيانات وشبكة حقيقية!\n"
            "}\n"
            "\n"
            "// ✅ مع Dependency Injection (Constructor Injection):\n"
            "@HiltViewModel\n"
            "class GoodOrderViewModel @Inject constructor(\n"
            "    private val repository: OrderRepository // التبعية تُمرر من الخارج\n"
            ") : ViewModel() {\n"
            "    val orders = repository.observeOrders()\n"
            "}\n"
            "\n"
            "// في الـ Unit Test: اختبار فوري في 2 مللي ثانية بتمرير Fake:\n"
            "@Test\n"
            "fun testOrderViewModel() {\n"
            "    val fakeRepo = FakeOrderRepository()\n"
            "    val viewModel = GoodOrderViewModel(fakeRepo) // تمرير التبعية يدوياً بسهولة فائقة!\n"
            "    assertNotNull(viewModel.orders)\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Dependency Injection as a pattern decouples object consumption from object creation by passing dependencies from the outside (typically via constructor injection). It enables effortless JVM unit testing via Fakes, centralizes lifecycle and scope management, and enforces the Inversion of Control principle.",
        "best_answer": (
            "Dependency Injection (DI) is a specialized form of the Inversion of Control (IoC) pattern where an object receives its dependencies from an external assembler rather than instantiating them internally.\n\n"
            "1. **Core Problem Solved**:\n   - Without DI, a class hardcodes its dependencies (`val api = RetrofitInstance.create()`). The class becomes tightly coupled to concrete implementations, lifecycle configuration, and infrastructure environments.\n   - Unit testing becomes impossible because collaborators cannot be substituted with test doubles.\n\n"
            "2. **What DI Accomplishes**:\n   - **Separation of Creation from Use**: Classes declare *what* collaborators they need in their constructor; an external container (Hilt, Koin, or manual DI) decides *how and when* to instantiate them.\n   - **Frictionless Unit Testing**: In JVM tests, developers instantiate classes directly, passing fast in-memory Fakes without bootstrapping DI containers or Android frameworks.\n   - **Centralized Scope & Lifecycle Management**: Tools like Hilt manage object scopes (`@Singleton`, `@ViewModelScoped`, `@ActivityScoped`), eliminating manual memory retention and teardown boilerplate."
        ),
        "deep_answer": (
            "A vital architectural realization is that **Dependency Injection is a pattern, not a library**. "
            "You can practice clean DI using **Pure / Manual Constructor Injection** without Dagger, Hilt, or Koin. "
            "Frameworks simply automate the tedious compile-time graph resolution and factory generation.\n\n"
            "There are three types of Dependency Injection:\n"
            "1. **Constructor Injection**: The gold standard in modern Android. Guarantees that dependencies are non-null, immutable (`val`), and explicit upon creation.\n"
            "2. **Method / Parameter Injection**: Passing a collaborator into a specific function (e.g. `useCase.execute(dispatcher)`).\n"
            "3. **Field Injection**: Necessary in Android only when the system instantiates classes via reflection (e.g. Activities and Services in `@AndroidEntryPoint`)."
        ),
        "follow_ups": [
            {
                "question": "Why is Constructor Injection preferred over Field Injection?",
                "answer": "Constructor injection ensures dependencies are required, immutable (`val`), and fully initialized at construction time, preventing temporal coupling and allowing classes to be instantiated cleanly in unit tests without reflection."
            },
            {
                "question": "What is the difference between Service Locator and Dependency Injection?",
                "answer": "A Service Locator queries an external registry internally (`locator.get<Repo>()`), hiding dependencies inside the class. DI inverts control by explicitly passing dependencies into the constructor from the outside."
            }
        ]
    },
    {
        "id": "PAT-08",
        "arabic_explanation": (
            "أين تظهر أنماط Singleton و Adapter و Observer بشكل طبيعي في مكونات وأطر عمل Android؟\n\n"
            "1. نمط الكائن الأحادي (Singleton Pattern in Android):\n   - **أين يظهر؟**:\n     * كائنات `object` في Kotlin.\n     * مدير قاعدة بيانات **Room Database** عبر `Room.databaseBuilder()` الموجه كـ Singleton.\n     * عميل شبكة **OkHttpClient** و **Retrofit**؛ مشاركة connection pool و cache عبر التطبيق.\n     * خدمات نظام أندرويد (System Services مثل `getSystemService(Context.CONNECTIVITY_SERVICE)`).\n\n"
            "2. نمط المحول (Adapter Pattern in Android):\n   - **أين يظهر؟**:\n     * **`RecyclerView.Adapter`**: يحول قائمة كائنات بيانات غير متوافقة مع الـ Views إلى `ViewHolders` تفهمها شجرة العرض.\n     * **`ArrayAdapter`** في الـ Spinners و AutoCompleteTextViews.\n     * محولات التنسيق في Retrofit: **`Converter.Factory`** (Moshi / Gson / Kotlinx Serialization) التي تحول HTTP ResponseBody إلى Kotlin Data Classes.\n\n"
            "3. نمط المراقب (Observer Pattern in Android):\n   - **أين يظهر؟**:\n     * **Kotlin Flow & StateFlow & SharedFlow**: اشتراك تفاعلي يراقب انبعاثات البيانات.\n     * **`LiveData`** ومراقبتها في الـ UI عبر `observe(lifecycleOwner)`.\n     * **`BroadcastReceiver`**: مراقبة أحداث نظام التشغيل (مثل انقطاع الإنترنت أو شحن البطارية).\n     * **`SnapshotState`** في Jetpack Compose؛ يعيد تشغيل الـ Composable فور تغير الحالة المراقبة."
        ),
        "practical_walkthrough": (
            "توضيح ظهور الأنماط الثلاثة داخل دورة حياة تطبيق Android:\n"
            "```kotlin\n"
            "// 1. SINGLETON: قاعدة بيانات Room واحدة مشتركة عبر Hilt:\n"
            "@Module\n"
            "@InstallIn(SingletonComponent::class)\n"
            "object DatabaseModule {\n"
            "    @Provides\n"
            "    @Singleton // نمط Singleton يضمن حجز DB واحدة فقط في الذاكرة\n"
            "    fun provideDatabase(@ApplicationContext context: Context): AppDatabase {\n"
            "        return Room.databaseBuilder(context, AppDatabase::class.java, \"app.db\").build()\n"
            "    }\n"
            "}\n"
            "\n"
            "// 2. ADAPTER: تحويل بيانات إلى ViewHolders في RecyclerView:\n"
            "class UserAdapter : RecyclerView.Adapter<UserViewHolder>() {\n"
            "    // يحول الـ Data Object إلى Android View layout\n"
            "}\n"
            "\n"
            "// 3. OBSERVER: مراقبة الـ StateFlow بنمط مراقب حديث مرتبط بدورة الحياة:\n"
            "viewLifecycleOwner.lifecycleScope.launch {\n"
            "    viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {\n"
            "        viewModel.uiState.collect { state -> // Observer Pattern\n"
            "            renderUi(state)\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Singleton appears in Room database instances, OkHttpClient, and Android System Services. Adapter appears in `RecyclerView.Adapter`, `ArrayAdapter`, and Retrofit Converter Factories. Observer appears in `StateFlow`, `LiveData`, `BroadcastReceiver`, and Jetpack Compose's Snapshot state system.",
        "best_answer": (
            "These three Gang of Four patterns are deeply woven into the fabric of the Android Operating System and Jetpack libraries:\n\n"
            "1. **Singleton Pattern in Android**:\n   - **Room Database**: Creating multiple database instances causes database lock contention and memory thrashing; Room requires a single process-level instance.\n   - **OkHttpClient**: Shares an HTTP connection pool, thread pool, and disk cache across the application.\n   - **Android System Services**: System managers retrieved via `context.getSystemService()` (e.g. `NotificationManager`, `ConnectivityManager`) act as system-wide service singletons.\n\n"
            "2. **Adapter Pattern in Android**:\n   - **`RecyclerView.Adapter`**: Converts raw application domain collections (`List<Item>`) into Android UI nodes (`ViewHolder` and `View`).\n   - **Retrofit Converter Factories**: Adapts raw HTTP byte streams from OkHttp into structured Kotlin data classes via Moshi or Kotlinx Serialization.\n\n"
            "3. **Observer Pattern in Android**:\n   - **Reactive Streams (`StateFlow` / `LiveData`)**: Observables emit state updates to observing UI controllers.\n   - **`BroadcastReceiver`**: The OS acts as the Subject broadcasting system events (battery status, network changes) to registered receiver Observers.\n   - **Jetpack Compose Runtime**: Compose's Snapshot system registers composable scopes as observers of `State<T>` properties, re-executing functions upon mutation."
        ),
        "deep_answer": (
            "Under the hood, understanding how the OS implements these patterns avoids common bugs:\n"
            "- A non-scoped Singleton holding an Activity Context produces a severe memory leak, which is why Android Singletons must strictly bind to `applicationContext`.\n"
            "- In `RecyclerView.Adapter`, calling `notifyDataSetChanged()` is an unoptimized observer broadcast invalidating the whole layout; using `ListAdapter` with `DiffUtil` applies granular observer updates (`notifyItemInserted`, `notifyItemMoved`).\n"
            "- In Compose, the Snapshot observer system operates at the microsecond level, tracking exact property reads within the Slot Table to skip recomposition of unobserved UI branches."
        ),
        "follow_ups": [
            {
                "question": "Why does OkHttpClient need to be a Singleton?",
                "answer": "Each OkHttpClient instance creates its own connection pool, thread pool, and cache. Creating multiple instances wastes memory, exhausts file descriptors, and prevents HTTP/2 multiplexing across requests."
            },
            {
                "question": "How does DiffUtil improve upon standard RecyclerView.Adapter updates?",
                "answer": "DiffUtil calculates the minimal list mutations on a background thread using Myers' diff algorithm, dispatching precise structural adapter updates rather than redrawing the whole screen."
            }
        ]
    },
    {
        "id": "PAT-09",
        "arabic_explanation": (
            "المقارنة الدقيقة بين نمط الحالة (State Pattern) ونمط الاستراتيجية (Strategy Pattern) مع أمثلة عملية واقعية في Android:\n\n"
            "1. وجه الشبه الخادع (The Identical Structure):\n   - النمطان يمتلكان نفس المخطط الهيكلي (UML Structure) تماماً: كلاس سياق (Context Class) يمتلك مرجعاً لـ Interface مجرد، وهذا الـ Interface له عدة تطبيقات ملموسة.\n\n"
            "2. الفرق الجوهري في النية والسلوك (Intent & Behavior):\n   - **نمط الاستراتيجية (Strategy Pattern)**:\n     * **النية**: تبديل **خوارزميات متبادلة (Interchangeable Algorithms)** تؤدي نفس الهدف بأساليب مختلفة.\n     * **طريقة الاستخدام**: العميل (Client) يحدد الاستراتيجية غالباً مرة واحدة (مثل اختيار المستخدم: \"أريد الدفع بـ PayPal\")، والاستراتيجيات لا تعلم شيئاً عن بعضها البعض.\n     * **مثال**: استراتيجيات ضغط الصور (JPEG vs WebP vs PNG) أو استراتيجيات الدفع.\n   - **نمط الحالة (State Pattern)**:\n     * **النية**: جعل الكائن **يغير سلوكه بالكامل عندما تتغير حالته الداخلية** (Finite State Machine).\n     * **طريقة الاستخدام**: الحالة تتغير تلقائياً وبشكل ديناميكي ومستمر استجابةً للأحداث، وحالات الـ State غالباً هي التي تقرر وتطلق الانتقال إلى الحالة التالية بنفسها!\n     * **مثال**: آلة حالات اتصال البلوتوث (`Disconnected -> Connecting -> Connected -> Disconnecting`)."
        ),
        "practical_walkthrough": (
            "مقارنة بين Strategy للدفع و State لاتصال البلوتوث في كود Kotlin:\n"
            "```kotlin\n"
            "// 1. STRATEGY PATTERN: خوارزميات متبادلة لا تغير نفسها ولا تعلم عن بعضها:\n"
            "interface ImageCompressionStrategy {\n"
            "    fun compress(bitmap: Bitmap): ByteArray\n"
            "}\n"
            "class JpegCompression : ImageCompressionStrategy { ... }\n"
            "class WebPCompression : ImageCompressionStrategy { ... }\n"
            "// العميل يختار استراتيجية واحدة ويمررها للعملية:\n"
            "imageSaver.save(bitmap, WebPCompression())\n"
            "\n"
            "// 2. STATE PATTERN: آلة حالات ديناميكية حيث تغير الحالات سلوك الجهاز وتنتقل ذاتياً:\n"
            "sealed interface BleConnectionState {\n"
            "    fun connect(context: BleManager)\n"
            "    fun disconnect(context: BleManager)\n"
            "}\n"
            "\n"
            "class DisconnectedState : BleConnectionState {\n"
            "    override fun connect(context: BleManager) {\n"
            "        context.startScan()\n"
            "        context.transitionTo(ConnectingState()) // الحالة تنقل السياق للحالة التالية!\n"
            "    }\n"
            "    override fun disconnect(context: BleManager) { /* لا شيء */ }\n"
            "}\n"
            "\n"
            "class ConnectingState : BleConnectionState {\n"
            "    override fun connect(context: BleManager) { /* تجاهل: الاتصال جارٍ بالفعل */ }\n"
            "    override fun disconnect(context: BleManager) { context.cancel(); context.transitionTo(DisconnectedState()) }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Strategy encapsulates interchangeable algorithms usually chosen once by the client (e.g. Payment methods, image compression). State models a dynamic state machine where an object alters its behavior based on internal state changes, with states often triggering transitions to succeeding states (e.g. Media playback or Bluetooth connectivity).",
        "best_answer": (
            "While State and Strategy share an identical structural UML diagram (a Context class delegating to an Interface with polymorphic implementations), they diverge sharply in architectural intent and lifecycle behavior.\n\n"
            "1. **Strategy Pattern (Interchangeable Algorithms)**:\n   - **Intent**: Provide alternative ways of accomplishing the exact same task.\n   - **Selection**: Configured from the outside by the client or dependency injection container (e.g. selecting `PaypalStrategy` vs `StripeStrategy`, or sorting via `PriceComparator`).\n   - **Independence**: Strategies are completely decoupled from each other and have no awareness of succeeding strategies.\n\n"
            "2. **State Pattern (Dynamic Behavioral Transformation)**:\n   - **Intent**: Enable an object to behave like an entirely different class when its internal state changes (Finite State Machine).\n   - **Transitions**: Driven internally by events occurring over time. State implementations actively invoke callbacks on the Context to transition it to succeeding states (e.g. `ConnectingState` transitions the context to `ConnectedState` upon receiving a BLE GATT callback).\n   - **Coupling**: States often hold references to valid neighboring target states in the state machine."
        ),
        "deep_answer": (
            "In modern Android architecture, the classic GoF State pattern has evolved into **Declarative State Machines (MVI)**. "
            "Instead of mutable context objects passing polymorphic pointers (`context.transitionTo(...)`), modern Kotlin architecture uses:\n"
            "- A `sealed interface DeviceState` representing immutable state models.\n"
            "- A `sealed interface DeviceEvent` representing incoming triggers.\n"
            "- A pure Reducer function: `reduce(currentState: DeviceState, event: DeviceEvent): DeviceState`.\n\n"
            "This functional evolution preserves the exact intent of the State pattern while guaranteeing complete thread-safety, zero memory leaks, and seamless integration with Jetpack Compose."
        ),
        "follow_ups": [
            {
                "question": "Can a class use both State and Strategy simultaneously?",
                "answer": "Yes. An `AudioPlayer` can use the State pattern to manage playback lifecycles (`Playing`, `Paused`, `Buffering`), while simultaneously using the Strategy pattern to select an audio decoding strategy (`OpusDecoder` vs `FlacDecoder`)."
            },
            {
                "question": "How does the State pattern eliminate complex nested if/else statements?",
                "answer": "Instead of checking `if (state == PLAYING) ... else if (state == PAUSED)` in every method, the context delegates execution directly to `currentState.handle()`, replacing branching logic with polymorphism."
            }
        ]
    },
    {
        "id": "PAT-10",
        "arabic_explanation": (
            "المقارنة بين نمط المصنع (Factory Method) ونمط المصنع المجرد (Abstract Factory) مع أمثلة عملية في Android:\n\n"
            "1. نمط دالة المصنع (Factory Method Pattern):\n   - **الهدف**: إنشاء **كائن منتج واحد (Single Product)** وتفويض قرار اختيار الكلاس الملموس إلى دالة المصنع.\n   - **التركيز**: إنشاء كائن من عائلة محددة بناءً على بارامتر.\n   - **في Android**: `ViewModelProvider.Factory`؛ مسؤوليته إنشاء كائن ViewModel واحد بناءً على كلاس الـ ViewModel المطلوب.\n\n"
            "2. نمط المصنع المجرد (Abstract Factory Pattern):\n   - **الهدف**: مصنع للمصانع! توفير واجهة لإنشاء **عائلات كاملة من الكائنات المرتبطة والمتوافقة (Families of Related Products)** دون تحديد كلاساتها الملموسة.\n   - **التركيز**: الاتساق والتطابق بين مجموعة كائنات كاملة.\n   - **في Android**: نظام الثيمات الموحد؛ `DesignSystemFactory` ينشئ (زر + مربع حوار + بطاقة) متطابقة تماماً لثيم معين (DarkTheme vs LightTheme)؛ مما يضمن استحالة وضع زر من ثيم النهار داخل حوار من ثيم الليل بالخطأ!"
        ),
        "practical_walkthrough": (
            "المقارنة بين Factory Method و Abstract Factory في كود Kotlin:\n"
            "```kotlin\n"
            "// 1. FACTORY METHOD: ينشئ كائناً واحداً فقط من نوع محدد:\n"
            "interface NotificationFactory {\n"
            "    fun createNotification(type: String): Notification\n"
            "}\n"
            "class AppNotificationFactory : NotificationFactory {\n"
            "    override fun createNotification(type: String): Notification = when(type) {\n"
            "        \"PROMO\" -> PromoNotification()\n"
            "        \"ALERT\" -> AlertNotification()\n"
            "        else -> DefaultNotification()\n"
            "    }\n"
            "}\n"
            "\n"
            "// 2. ABSTRACT FACTORY: ينشئ عائلة كاملة من المكونات المتوافقة معاً:\n"
            "interface DialogComponentFactory { // عائلة مكونات كاملة\n"
            "    fun createHeader(): DialogHeader\n"
            "    fun createButton(): DialogButton\n"
            "    fun createBackground(): DialogBackground\n"
            "}\n"
            "\n"
            "class PremiumDialogFactory : DialogComponentFactory {\n"
            "    override fun createHeader() = GoldHeader()\n"
            "    override fun createButton() = GoldButton()\n"
            "    override fun createBackground() = BlurBackground()\n"
            "}\n"
            "\n"
            "class StandardDialogFactory : DialogComponentFactory {\n"
            "    override fun createHeader() = SimpleHeader()\n"
            "    override fun createButton() = StandardButton()\n"
            "    override fun createBackground() = FlatBackground()\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Factory Method creates a single product by delegating instantiation to a method (`ViewModelProvider.Factory`). Abstract Factory creates entire families of related or dependent products without specifying concrete classes (e.g. creating matching themed buttons, headers, and backgrounds for dark vs light themes).",
        "best_answer": (
            "The distinction between Factory Method and Abstract Factory hinges on product scope and familial relationship guarantees.\n\n"
            "1. **Factory Method (Single Product Focus)**:\n   - Defines an interface with a method that creates a **single product object**.\n   - Subclasses or implementers decide which concrete class to instantiate.\n   - *Android Example*: `ViewModelProvider.Factory`. It defines `create(modelClass: Class<T>): T`, instantiating a single specific ViewModel requested by the UI controller.\n\n"
            "2. **Abstract Factory (Product Family Focus)**:\n   - Defines an interface with multiple methods designed to create **an entire family of mutually compatible products**.\n   - Guarantees that clients never accidentally mix incompatible products (e.g. mixing an iOS-styled button with an Android Material dialog).\n   - *Android Example*: A multi-brand design system where `BrandFactory` exposes `createButton()`, `createCard()`, and `createTextField()`. The `EnterpriseBrandFactory` produces enterprise-styled variants of all three components, guaranteeing complete visual cohesion across the suite."
        ),
        "deep_answer": (
            "Under the hood, an Abstract Factory is often implemented as a class whose individual methods are Factory Methods. "
            "In modern Dagger/Hilt architectures, **Dagger Component and Subcomponent interfaces are essentially compile-time Abstract Factories**! "
            "When Dagger declares an interface providing various dependencies for an Activity scope, Dagger generates the concrete factory implementation under the hood.\n\n"
            "In Kotlin, using Factory patterns can often be simplified using top-level functions or companion objects: `companion object { fun create(...) = ... }`. "
            "Senior architects reserve explicit Factory and Abstract Factory classes for scenarios where instantiation requires dynamic dependency injection or complex configuration policies."
        ),
        "follow_ups": [
            {
                "question": "How does Dagger use the Abstract Factory pattern?",
                "answer": "Dagger Components are Abstract Factories. You declare an abstract component interface with methods returning various dependencies, and Dagger generates the concrete factory class (`DaggerAppComponent`) implementing it."
            },
            {
                "question": "When should you prefer a Factory over direct constructor invocation?",
                "answer": "When object construction involves complex conditional logic, requires caching or pooling existing instances, or when the calling client must remain decoupled from concrete implementation types."
            }
        ]
    },
    {
        "id": "PAT-11",
        "arabic_explanation": (
            "أين ومتى يكون نمط الباني (Builder Pattern) مفيداً وضرورياً في تصميم الـ APIs والمكتبات (SDK Design) في Android؟\n\n"
            "1. متى يكون الـ Builder مفيداً في تصميم الـ SDKs؟\n   - **الكائنات ذات الإعدادات المتعددة والمعقدة (Complex Configuration Objects)**: عندما يحتوي الكائن على 10 إلى 20 إعداداً مختلفاً، ومعظمها اختياري (مثل إعدادات شبكة OkHttp، أو إعدادات مشغل الفيديو، أو مكتبة تحليلات).\n   - **التوافق التام مع لغة Java (Java Interoperability)**: في Kotlin لدينا Default Arguments، ولكن مطور Java الذي يستخدم مكتبتك لا يمكنه الاستفادة منها وسيعاني من استدعاء Constructor يحتوي على 15 بارامتر! الـ Builder يوفر تجربة سلسة (Fluent API) لمطوري Java و Kotlin معاً.\n   - **التحقق من صحة البيانات المتشابكة قبل البناء (Cross-field Validation)**: فحص شروط تتطلب وجود حقلين معاً (مثل: إذا تم تحديد `timeout` يجب تحديد `retryPolicy`)؛ دالة `build()` تفحص كل هذه الشروط وتطلق استثناءً واضحاً قبل إنشاء الكائن غير القابل للتعديل (Immutable Object).\n\n"
            "2. أمثلة حية من نظام Android:\n   - `NotificationCompat.Builder`\n   - `WorkRequest.Builder` (OneTimeWorkRequestBuilder)\n   - `OkHttpClient.Builder`\n   - `Room.databaseBuilder()`."
        ),
        "practical_walkthrough": (
            "تصميم Builder احترافي لمكتبة Analytics SDK تضمن التحقق من الشروط وسلامة الكائن:\n"
            "```kotlin\n"
            "class AnalyticsConfig private constructor(\n"
            "    val apiKey: String,\n"
            "    val serverUrl: String,\n"
            "    val batchSize: Int,\n"
            "    val isDebugLoggingEnabled: Boolean\n"
            ") {\n"
            "    class Builder(private val apiKey: String) { // الحقل الإجباري في constructor الـ Builder\n"
            "        private var serverUrl: String = \"https://analytics.default.com\"\n"
            "        private var batchSize: Int = 50\n"
            "        private var isDebugLogging: Boolean = false\n"
            "\n"
            "        fun setServerUrl(url: String) = apply { this.serverUrl = url }\n"
            "        fun setBatchSize(size: Int) = apply { this.batchSize = size }\n"
            "        fun enableDebugLogging(enabled: Boolean) = apply { this.isDebugLogging = enabled }\n"
            "\n"
            "        fun build(): AnalyticsConfig {\n"
            "            // التحقق من صحة الشروط المتشابكة قبل إنشاء الكائن النهائي غير القابل للتعديل:\n"
            "            require(apiKey.isNotBlank()) { \"API key must not be blank\" }\n"
            "            require(batchSize in 1..500) { \"Batch size must be between 1 and 500\" }\n"
            "            return AnalyticsConfig(apiKey, serverUrl, batchSize, isDebugLogging)\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Builder is essential in SDK and public API design for constructing complex configuration objects with many optional parameters, maintaining seamless Java interoperability, enforcing atomic cross-field validation rules during `build()`, and guaranteeing final object immutability.",
        "best_answer": (
            "While Kotlin data classes with default arguments eliminate builders for internal domain models, the Builder pattern remains indispensable in **public SDK design and framework architecture**.\n\n"
            "1. **Java Interoperability**: If an Android library or SDK is consumed by Java codebases, Kotlin's named parameters are inaccessible. Without a Builder, Java developers are forced to invoke telescoping constructors with dozens of null parameters. A Builder provides a clean, fluent Java API.\n\n"
            "2. **Cross-Field Validation & Invariant Enforcement**: In complex SDK configurations (e.g. `WorkRequest.Builder`, `OkHttpClient.Builder`), parameters have interdependencies (e.g. 'if backoff policy is exponential, delay cannot be under 10 seconds'). A constructor cannot execute multi-step validation cleanly; the builder stages mutable state and executes comprehensive invariant checks atomically inside `.build()` before constructing the object.\n\n"
            "3. **Enforcing Immutability**: The builder can be mutable while building, but the resulting object is strictly immutable and thread-safe post-build, preventing clients from mutating network configurations or security keys at runtime."
        ),
        "deep_answer": (
            "In modern Kotlin SDK design, senior architects provide the best of both worlds using **Type-Safe Builders with Kotlin DSLs**: "
            "By pairing a standard Builder with a trailing lambda function utilizing an extension receiver (`fun analyticsConfig(apiKey: String, block: Builder.() -> Unit): AnalyticsConfig`), Kotlin developers enjoy idiomatic DSL syntax: `analyticsConfig(\"key\") { setBatchSize(100) }`, while Java developers enjoy standard fluent method chaining: `new Builder(\"key\").setBatchSize(100).build()`.\n\n"
            "This dual API design guarantees maximum adoption across heterogeneous enterprise teams."
        ),
        "follow_ups": [
            {
                "question": "What is the 'Telescoping Constructor' anti-pattern?",
                "answer": "An anti-pattern where a class provides multiple overloaded constructors with increasing parameter counts (1 param, 2 params, 3 params), leading to unreadable instantiation code and accidental argument swapping."
            },
            {
                "question": "How does Kotlin DSL combine with the Builder pattern?",
                "answer": "By creating a high-level function accepting a lambda with receiver `Builder.() -> Unit`, allowing developers to write declarative, type-safe configuration blocks that call builder methods under the hood."
            }
        ]
    },
    {
        "id": "PAT-12",
        "arabic_explanation": (
            "كيف يبسط نمط الواجهة (Facade Pattern) التعامل مع مكتبة خارجية غير موثوقة أو فوضوية (Unreliable Third-Party SDK)؟\n\n"
            "1. مشكلة التعامل المباشر مع مكتبات الـ Third-Party الفوضوية:\n   - مكتبات الدفع، الخرائط، البلوتوث، أو الإعلانات الخارجية غالباً ما تكون سيئة التصميم:\n     * تفرض كوداً طويلاً ومعقداً لبدء اتصال بسيط.\n     * ترمي استثناءات غير متوقعة، أو تحتوي على Listeners غريبة.\n     * إذا قمت باستدعائها في كل مكان في شاشات التطبيق، تصبح رهينة لهذه المكتبة، وتغييرها أو تحديثها مستقبلاً يتطلب تعديل عشرات الشاشات!\n\n"
            "2. كيف يحل الـ Facade Pattern هذه الكارثة؟\n   - نقوم ببناء كلاس وسيط يسمى **Facade** (مثل `BiometricAuthFacade` أو `MapsLocationFacade`).\n   - **يخفي كل التعقيد والقذارة بداخل كود واحد محصور**:\n     * يبتلع الاستثناءات العشوائية ويحولها إلى Results آمنة.\n     * ينسق الخطوات الخمسة المعقدة للـ SDK ويختصرها في دالة واحدة معلقة: `suspend fun authenticate(): Boolean`.\n   - تصبح شاشات التطبيق نظيفة وتتعامل مع الـ Facade فقط. إذا قررت الشركة غداً استبدال الـ SDK بمكتبة أخرى، فالتعديل ينحصر داخل الـ Facade فقط دون المساس بأي شاشة في التطبيق!"
        ),
        "practical_walkthrough": (
            "بناء Facade لتبسيط SDK بصمة فوضوي ومعقد:\n"
            "```kotlin\n"
            "// كلاس Facade يعزل مكتبة البصمة الفوضوية خلف واجهة نظيفة معلقة:\n"
            "class BiometricAuthFacade @Inject constructor(\n"
            "    @ApplicationContext private val context: Context\n"
            ") {\n"
            "    suspend fun authenticateUser(title: String, subtitle: String): BiometricResult = suspendCancellableCoroutine { continuation ->\n"
            "        try {\n"
            "            val promptInfo = BiometricPrompt.PromptInfo.Builder()\n"
            "                .setTitle(title)\n"
            "                .setSubtitle(subtitle)\n"
            "                .setNegativeButtonText(\"Cancel\")\n"
            "                .build()\n"
            "\n"
            "            // إخفاء كل تعقيد الـ Callbacks والـ Executors داخل الـ Facade:\n"
            "            val callback = object : BiometricPrompt.AuthenticationCallback() {\n"
            "                override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {\n"
            "                    continuation.resume(BiometricResult.Success)\n"
            "                }\n"
            "                override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {\n"
            "                    continuation.resume(BiometricResult.Error(errString.toString()))\n"
            "                }\n"
            "            }\n"
            "            // تنفيذ طلب البصمة...\n"
            "        } catch (e: Exception) {\n"
            "            continuation.resume(BiometricResult.Error(e.localizedMessage ?: \"Biometric failed\"))\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "A Facade encapsulates an unreliable third-party SDK behind a simplified, resilient application-owned API. It converts cumbersome callbacks into suspending coroutines, absorbs unpredictable exceptions into safe Result types, and acts as an anti-corruption layer so swapping the vendor SDK later touches only the Facade.",
        "best_answer": (
            "Wrapping an unreliable third-party SDK inside a **Facade** acts as an **Anti-Corruption Layer (ACL)**, protecting the core application from external instability and poor vendor API design.\n\n"
            "1. **API Simplification**: Third-party SDKs frequently demand multi-step initialization rituals (setting listeners, configuring flags, handling token exchanges). A Facade condenses 10 steps into a single cohesive, high-level suspending method: `suspend fun scanDocument(): DocumentResult`.\n\n"
            "2. **Resilience & Error Containment**: Volatile vendor libraries often throw undocumented runtime exceptions or return obscure integer error codes. The Facade catches vendor exceptions, intercepts error codes, and maps them into safe, typed domain results (`Result<T>`), preventing vendor crashes from taking down the app.\n\n"
            "3. **Vendor Insulation (Zero Lock-in)**: By consuming only the Facade, feature ViewModels and Use Cases never import vendor package classes (`com.vendor.sdk.*`). If the vendor doubles their pricing or deprecates their library, swapping to a competitor requires rewriting only the internal implementation of the Facade; the rest of the application remains completely untouched."
        ),
        "deep_answer": (
            "In modern Android, Facades excel at **converting legacy Callback APIs into Coroutines and Flows**. "
            "Vendors often supply outdated Java listener interfaces (`onSuccess`, `onError`). "
            "Inside the Facade, we wrap these callbacks using `suspendCancellableCoroutine` or `callbackFlow`, installing proper cancellation cleanup in `awaitClose { ... }`.\n\n"
            "Furthermore, a Facade allows injecting **Feature Flags and Fallback Mechanisms**. "
            "If the third-party analytics or crash SDK crashes or hangs, the Facade can evaluate an in-memory killswitch, silently bypassing the vendor call and returning a cached fallback without the UI ever knowing a failure occurred."
        ),
        "follow_ups": [
            {
                "question": "What is an Anti-Corruption Layer (ACL) in Domain-Driven Design?",
                "answer": "A translation layer (typically implemented as a Facade and Adapter) that sits between your clean domain model and a messy external system, preventing foreign concepts from polluting your code."
            },
            {
                "question": "How does `suspendCancellableCoroutine` help in a Facade?",
                "answer": "It bridges asynchronous callback-based third-party SDK APIs into modern Kotlin suspending functions, supporting cooperative cancellation if the calling coroutine scope cancels."
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

    for item in PAT_07_12:
        by_id[item["id"]] = item

    output = [by_id[k] for k in sorted(by_id.keys())]
    DATA_FILE.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {DATA_FILE} with questions PAT-07 to PAT-12. Total questions: {len(output)}")

if __name__ == "__main__":
    main()
