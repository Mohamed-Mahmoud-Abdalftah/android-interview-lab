#!/usr/bin/env python3
"""Generator for DI-01 through DI-07 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "di.json"

DI_01_07 = [
    {
        "id": "DI-01",
        "arabic_explanation": (
            "ما هو نمط حقن التبعيات (Dependency Injection - DI) وما هي المشاكل الحقيقية التي يحلها في Android؟\n\n"
            "1. المفهوم الجوهري:\n"
            "   - التبعية (Dependency) هي أي كائن أو خدمة يحتاجها كلاس آخر ليؤدي وظيفته (مثل `UserRepository` أو `HttpClient` داخل `OrderViewModel`).\n"
            "   - نمط الـ DI هو تطبيق لمبدأ الـ Inversion of Control (IoC): بدلاً من أن يقوم الكلاس بإنشاء تبعياته بنفسه من الداخل (`val repo = UserRepositoryImpl()`)، يتم تمرير هذه التبعيات إليه جاهزة من الخارج عبر الـ Constructor (`Constructor Injection`).\n\n"
            "2. المشاكل الكبرى التي يحلها الـ DI:\n"
            "   - **الاقتران الصلب (Tight Coupling)**: بدون DI، يرتبط الكلاس بتنفيذ ملموس محدد (Concrete Class) وبإعداداته. مع DI، يرتبط فقط بـ Interface أو Abstraction، مما يجعل استبداله سهلاً دون تعديل الكود المستهلك.\n"
            "   - **استحالة الاختبار المعزول (Testability)**: بدون DI، لا يمكنك تشغيل Unit Test سريع على الـ JVM للـ ViewModel دون الاتصال بشبكة وقاعدة بيانات حقيقية. مع DI، تمرر ببساطة `FakeUserRepository` في ثوانٍ.\n"
            "   - **فوضى إدارة دورة الحياة والذاكرة (Lifecycle & Scoping)**: بدون إدارة مركزية، تتكرر كائنات ثقيلة مثل الـ Database Client في كل مكان، أو يتم تسريب الـ Context داخل كائنات عامة.\n"
            "   - **إعادة استخدام الكود (Reusability)**: الكلاسات تصبح نقية وتعتمد فقط على مدخلاتها."
        ),
        "practical_walkthrough": (
            "المقارنة بين كلاس ينشئ تبعياته بنفسه وكلاس يطبق الـ Dependency Injection:\n"
            "```kotlin\n"
            "// ❌ بدون DI: اقتران صلب، استحالة للـ Unit Test، وإنشاء متكرر لكائنات ثقيلة:\n"
            "class BadProfileViewModel : ViewModel() {\n"
            "    // الكلاس متحكم في كيفية بناء التبعية ومقيد بـ Implementation محدد:\n"
            "    private val api = Retrofit.Builder().baseUrl(\"https://api.example.com\").build().create(Api::class.java)\n"
            "    private val repository = ProfileRepositoryImpl(api)\n"
            "    \n"
            "    fun loadProfile() { /* ... */ }\n"
            "}\n"
            "\n"
            "// ✅ مع Dependency Injection (Constructor Injection النقي):\n"
            "@HiltViewModel\n"
            "class GoodProfileViewModel @Inject constructor(\n"
            "    private val repository: ProfileRepository // التبعية تمرر من الخارج عبر الـ Constructor\n"
            ") : ViewModel() {\n"
            "    val profileState = repository.getProfileStream()\n"
            "}\n"
            "\n"
            "// في الـ JVM Unit Test: اختبار فوري بدون تشغيل Hilt أو Android Framework:\n"
            "@Test\n"
            "fun profileViewModelLoadsDataCorrectly() = runTest {\n"
            "    val fakeRepo = FakeProfileRepository(testUser)\n"
            "    val viewModel = GoodProfileViewModel(fakeRepo) // تمرير Test Double في ثوانٍ!\n"
            "    assertEquals(testUser, viewModel.profileState.first())\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Dependency Injection is a design pattern where an object receives its collaborators from an external provider rather than creating them itself. It decouples classes from concrete implementations, enables effortless JVM unit testing using test doubles, and centralizes lifecycle and object graph management across the application.",
        "best_answer": (
            "Dependency Injection is a concrete implementation of Inversion of Control where a class defines *what* collaborators it needs in its constructor, and an external assembler provides them.\n\n"
            "It solves three fundamental engineering problems in Android:\n"
            "1. **Tight Coupling**: When a ViewModel constructs its own `Retrofit` instance or `RoomDatabase`, it is tightly bound to external infrastructure. With DI, the class depends on an abstract interface (`UserRepository`), allowing implementation details to change without touching consumer code.\n"
            "2. **Unit Testability**: Hardcoded dependencies make isolated JVM tests impossible because you cannot swap live networking or persistence with fast in-memory Fakes. Constructor injection makes test seams trivial.\n"
            "3. **Lifecycle & Scoping Management**: Android components have complex lifecycles (Process, Application, Activity, ViewModel). DI frameworks like Hilt manage object scopes cleanly, preventing memory leaks and avoiding redundant, memory-heavy object allocations."
        ),
        "deep_answer": (
            "A crucial distinction senior engineers make is that **DI is an architectural pattern, not a framework**. "
            "You can execute pure Manual DI using pure Kotlin constructor parameters and an `AppContainer`. "
            "Frameworks like Dagger and Hilt simply automate graph assembly at compile-time to eliminate manual factory boilerplate.\n\n"
            "Without DI, codebases inevitably degrade into **Service Locator anti-patterns** or global mutable singletons (`object ServiceRegistry`). "
            "Service Locators hide dependencies inside method bodies (`ServiceLocator.get<AuthManager>()`), breaking the explicit dependency contract, making refactoring treacherous, and risking runtime crashes if a collaborator is uninitialized. "
            "Constructor-based DI forces all dependencies to be explicit, immutable (`val`), non-null, and validated at compile time."
        ),
        "follow_ups": [
            {
                "question": "What is the difference between DI and a Service Locator?",
                "answer": "DI pushes dependencies into a class via its constructor (Inversion of Control), making dependencies explicit. A Service Locator pulls dependencies from an ambient registry inside the class, hiding dependencies and deferring missing dependencies to runtime failures."
            },
            {
                "question": "Does DI improve app performance?",
                "answer": "Not directly at runtime. In fact, reflection-based DI slows startup, while compile-time DI (Dagger/Hilt) generates standard factory code with zero reflection overhead. The primary gains are maintainability, test seams, and lifecycle safety."
            }
        ]
    },
    {
        "id": "DI-02",
        "arabic_explanation": (
            "مقارنة متعمقة بين Constructor Injection، و Field Injection، و Manual DI في Android:\n\n"
            "1. Constructor Injection (الحقن عبر المشيد):\n   - **كيف يعمل**: تمرير التبعيات مباشرة كـ `val` في الـ Constructor للكلاس.\n   - **المميزات**: هو المعيار الذهبي (Gold Standard). يجعل التبعيات صريحة وغير قابلة للتغيير (Immutable)، ويمنع الكائن من التواجد في حالة غير مكتملة (Partially Constructed State). يتيح الـ Unit Testing على الـ JVM بسهولة فائقة دون أي أطر عمل.\n   - **العيوب في Android**: لا يمكن استخدامه مباشرة مع الكلاسات التي ينشئها نظام أندرويد عبر الـ Reflection (مثل Activity, Fragment, Service, BroadcastReceiver).\n\n"
            "2. Field Injection (الحقن عبر الحقول `@Inject lateinit var`):\n   - **كيف يعمل**: يتم إنشاء الكائن بواسطة الـ Android OS، ثم يقوم المجمع (Dagger/Hilt) بحقن الحقول بعد الإنشاء مباشرة عبر `@AndroidEntryPoint`.\n   - **المميزات**: الحل الإجباري للأصناف التي يتحكم النظام في إنشائها (Activities, Services).\n   - **العيوب**: المتغيرات تكون `lateinit var` وقابلة للتعديل (Mutable). احتمالية حدوث `UninitializedPropertyAccessException` إذا تم استدعاء الحقل قبل إتمام الحقن، وصعوبة إجراء Unit Testing بدون استدعاء دوال حقن مخصصة.\n\n"
            "3. Manual DI (حقن التبعيات اليدوي):\n   - **كيف يعمل**: بناء شجرة التبعيات يدوياً باستخدام كلاسات Kotlin عادية (`AppContainer`) بدون استخدام Dagger أو Hilt.\n   - **المميزات**: وقت تجميع سريع جداً (صفر كود مولد أو Annotation Processing)، سهولة قراءة الـ Stack Trace بدون ألغاز، ومثالي للمشاريع والمكتبات الصغيرة.\n   - **العيوب**: يتطلب كتابة كميات ضخمة من كود المصانع (Factory Boilerplate) يدوياً، وصعوبة إدارة الـ Scoping ودورات حياة أندرويد المعقدة يدوياً في المشاريع الضخمة."
        ),
        "practical_walkthrough": (
            "المقارنة العملية بالكود بين الأنماط الثلاثة:\n"
            "```kotlin\n"
            "// 1. Constructor Injection: الأفضل والأكثر أماناً للكلاسات العادية والـ ViewModels:\n"
            "class FetchUserDataUseCase @Inject constructor(\n"
            "    private val repository: UserRepository // Immutable, non-null, explicit\n"
            ") {\n"
            "    suspend operator fun invoke() = repository.getUser()\n"
            "}\n"
            "\n"
            "// 2. Field Injection: إجباري لمكونات أندرويد التي ينشئها النظام (Activities/Services):\n"
            "@AndroidEntryPoint\n"
            "class MainActivity : ComponentActivity() {\n"
            "    @Inject lateinit var analytics: AnalyticsTracker // يتم حقنه بعد onCreate وقبل استخدامه\n"
            "    \n"
            "    override fun onCreate(savedInstanceState: Bundle?) {\n"
            "        super.onCreate(savedInstanceState)\n"
            "        // آمن للاستخدام بعد استدعاء super.onCreate()\n"
            "        analytics.trackScreen(\"Main\")\n"
            "    }\n"
            "}\n"
            "\n"
            "// 3. Manual DI: إدارة الحاوية يدوياً بدون مكتبات خارجية:\n"
            "class AppContainer(private val context: Context) {\n"
            "    val database: AppDatabase by lazy { Room.databaseBuilder(context, AppDatabase::class.java, \"db\").build() }\n"
            "    val userRepository: UserRepository by lazy { UserRepositoryImpl(database.userDao()) }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Constructor injection passes immutable dependencies explicitly via constructor parameters and is the gold standard for testability and immutability. Field injection is required for Android-instantiated components (Activities, Services) where Hilt injects lateinit vars after creation. Manual DI wires graphs using pure Kotlin containers without frameworks, avoiding build overhead but requiring extensive factory boilerplate.",
        "best_answer": (
            "Choosing between constructor injection, field injection, and manual DI depends on class ownership and framework integration.\n\n"
            "1. **Constructor Injection**: Always the default choice for repositories, use cases, and ViewModels. It ensures dependencies are explicit, immutable (`val`), non-null, and fully satisfied before the object can exist. It allows pure JVM unit testing by passing mocks or fakes into the constructor without any DI framework.\n\n"
            "2. **Field Injection**: Android creates Activities, Services, and BroadcastReceivers via reflection through their default no-arg constructors. Because we cannot alter their constructor signatures, Hilt/Dagger uses field injection (`@Inject lateinit var`). The container populates these fields immediately after creation. The trade-off is mutability and the risk of accessing uninitialized fields before injection.\n\n"
            "3. **Manual DI**: Building the object graph by hand using an `AppContainer`. It provides lightning-fast compile times, zero annotation processing, and crystal-clear stack traces. However, on large multi-module teams, manually maintaining factories and matching Android component scopes becomes an overwhelming maintenance burden."
        ),
        "deep_answer": (
            "Under the hood, Dagger and Hilt bridge the gap between Constructor and Field injection via generated code:\n\n"
            "For Constructor Injection, Dagger generates a `Factory<T>` (e.g. `UserRepository_Factory`), implementing `get(): T { return new UserRepository(provider.get()); }`. It is clean, direct instantiation with zero reflection.\n\n"
            "For Field Injection in `@AndroidEntryPoint Activity`, Hilt generates a base class (or uses bytecode transformation via the Hilt Gradle Plugin) that intercepts `onCreate()` before `super.onCreate()`. It retrieves the `ActivityComponent` from the Application's generated entry point and invokes a `MembersInjector<MainActivity>` (e.g. `MainActivity_MembersInjector.injectAnalytics(instance, provider.get())`). If you attempt to access an `@Inject lateinit var` inside an initializer block (`init { ... }`) or before `super.onCreate()`, the app crashes with an `UninitializedPropertyAccessException` because field injection has not executed yet."
        ),
        "follow_ups": [
            {
                "question": "Can we use constructor injection in Fragments?",
                "answer": "Yes, using FragmentFactory with Hilt or Dagger. However, with Jetpack Compose, Activities host Composables directly, largely rendering FragmentFactory unnecessary."
            },
            {
                "question": "Why is method injection rarely used in Android?",
                "answer": "Method injection executes after constructor injection but before field usage. In modern Android, passing dependencies directly as method parameters (`useCase.execute(param)`) or via the constructor is cleaner and less ambiguous."
            }
        ]
    },
    {
        "id": "DI-03",
        "arabic_explanation": (
            "المقارنة الجوهرية بين Dagger و Hilt في بيئة تطوير تطبيقات Android الحديثة:\n\n"
            "1. العلاقة بينهما:\n   - **Hilt ليس إطار عمل منفصل أو منافس لـ Dagger**؛ بل هو طبقة موجهة ومعيارية (Opinionated Layer) مبنية بالكامل فوق Dagger 2 ومخصصة لتطبيقات Android من Google.\n   - Hilt يولد مكونات Dagger العادية (`@Component`, `@Subcomponent`) تحت الغطاء نيابة عنك في وقت التجميع.\n\n"
            "2. أوجه المقارنة التفصيلية:\n   - **الـ Boilerplate و Components**: في Pure Dagger، كنت مضطراً لبناء `AppComponent`, `ActivityComponent`, `Subcomponents`, والـ Component Builders يدوياً وكتابة مئات الأسطر من الكود. في Hilt، كل المكونات الأساسية مدمجة مسبقاً (`SingletonComponent`, `ActivityComponent`, `ViewModelComponent`).\n   - **Android Lifecycle Integration**: يدعم Hilt حقن الـ ViewModels تلقائياً عبر `@HiltViewModel` بدون كتابة Custom ViewModelFactory مخصص ومزعج كالسابق.\n   - **Modularization**: في Pure Dagger، إدارة الـ Multi-module تتطلب ربط يدوي معقد. في Hilt، استخدام `@InstallIn(...)` يسمح لكل موديول بإعلان توفير كائناته مباشرة دون لمس الـ Base App Module.\n   - **Instrumentation Testing**: يدمج Hilt دعم مدمج للاختبارات عبر `@HiltAndroidTest` و `@UninstallModules` و `@BindValue`، بينما كان إعداد الاختبارات في Pure Dagger كابوساً يتطلب TestComponent مخصصاً."
        ),
        "practical_walkthrough": (
            "المقارنة بين إعداد الـ ViewModel في Pure Dagger وفي Hilt:\n"
            "```kotlin\n"
            "// ❌ في Pure Dagger القديم: تطلب الأمر كتابة Multibindings و ViewModelFactory مخصص:\n"
            "@MapKey\n"
            "@Target(AnnotationTarget.FUNCTION)\n"
            "annotation class ViewModelKey(val value: KClass<out ViewModel>)\n"
            "\n"
            "@Module\n"
            "abstract class ViewModelModule {\n"
            "    @Binds @IntoMap @ViewModelKey(OrderViewModel::class)\n"
            "    abstract fun bindOrderViewModel(vm: OrderViewModel): ViewModel\n"
            "    \n"
            "    @Binds\n"
            "    abstract fun bindFactory(factory: DaggerViewModelFactory): ViewModelProvider.Factory\n"
            "}\n"
            "// هذا الإعداد تطلب عشرات الملفات والـ Subcomponents المعقدة!\n"
            "\n"
            "// ✅ في Hilt الحديث: سطر واحد فقط ويتولى Hilt كل شيء تلقائياً:\n"
            "@HiltViewModel\n"
            "class OrderViewModel @Inject constructor(\n"
            "    private val repository: OrderRepository\n"
            ") : ViewModel() {\n"
            "    // جاهز للاستخدام مباشرة في الـ Activity أو Compose عبر hiltViewModel()!\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Hilt is an opinionated, compile-time framework built directly on top of Dagger specifically for Android. It eliminates Dagger's massive boilerplate by providing standard predefined components (SingletonComponent, ViewModelComponent), automatic Android lifecycle integration, simplified multi-module binding via @InstallIn, and native test runners via @HiltAndroidTest.",
        "best_answer": (
            "Hilt is not a replacement for Dagger; it is an opinionated abstraction layer over Dagger 2 engineered by Google to standardize Android dependency injection.\n\n"
            "Key architectural differences:\n"
            "1. **Predefined Component Hierarchy**: In pure Dagger, developers spent hundreds of lines defining custom Components, Subcomponents, and custom ViewModel Factories. Hilt provides a battle-tested hierarchy mapped directly to Android lifecycles (`SingletonComponent`, `ActivityRetainedComponent`, `ViewModelComponent`, `ActivityComponent`).\n"
            "2. **Decentralized Multi-Module Setup**: Pure Dagger required a central root component to declare all subcomponents. Hilt uses `@InstallIn`, allowing library and feature modules to independently contribute bindings to the shared graph without editing the base application module.\n"
            "3. **First-Class Testing**: Hilt provides built-in testing APIs (`@HiltAndroidTest`, `@UninstallModules`) that allow substituting production modules with test doubles in Robolectric and Android instrumented tests without maintaining duplicate test components."
        ),
        "deep_answer": (
            "At the compilation level, Hilt acts as an annotation processor that generates standard Dagger code before Dagger's own compiler runs.\n\n"
            "When you annotate a class with `@HiltAndroidApp`, Hilt generates a base application class that instantiates the generated Dagger `SingletonComponent`. "
            "When you use `@InstallIn(SingletonComponent::class)`, Hilt's byte-code/symbol processing collects these module definitions across all Gradle submodules into an aggregated metadata package. "
            "Dagger then consumes this generated metadata and performs standard compile-time graph validation.\n\n"
            "However, Hilt's opinionated design limits flexibility in edge cases. Pure Dagger allows arbitrary, deeply nested subcomponent lifetimes (e.g. a custom `LoggedInSessionComponent` or a `PlaybackFlowComponent`). "
            "Hilt strictly adheres to its built-in lifecycle components. While custom components can be created in Hilt using `@DefineComponent`, they require manual lifecycle management and entry points, forfeiting some of Hilt's zero-boilerplate ergonomics."
        ),
        "follow_ups": [
            {
                "question": "Can you mix Pure Dagger and Hilt in the same project?",
                "answer": "Yes. Hilt is built on Dagger. You can expose bindings from pure Dagger components into Hilt using Entry Points or incorporate Hilt into existing Dagger subcomponents during migrations."
            },
            {
                "question": "What is the compile-time impact of Hilt compared to pure Dagger?",
                "answer": "Hilt adds an extra metadata aggregation step, which can slightly increase build times compared to hand-rolled Dagger, but this is mitigated significantly by KSP (Kotlin Symbol Processing)."
            }
        ]
    },
    {
        "id": "DI-04",
        "arabic_explanation": (
            "شرح مفصل لوظائف التعليقات التوضيحية الأساسية في Dagger و Hilt:\n`@Inject`، و `@Module`، و `@Provides`، و `@Binds`:\n\n"
            "1. `@Inject` (طلب أو إعلان الحقن):\n   - **في الـ Constructor**: يعلم Dagger بكيفية بناء الكائن وما هي التبعيات التي يحتاجها. يتيح لـ Dagger إضافة الكائن إلى شجرة التبعيات تلقائياً دون الحاجة لكتابة كود في Module.\n   - **في الـ Fields**: يعلم Dagger بحقن التبعيات في هذه المتغيرات داخل الكلاسات التي ينشئها النظام (مثل `@Inject lateinit var api: Api` في Activity).\n\n"
            "2. `@Module` (مستودع تعريفات التبعيات):\n   - كلاس أو interface يعلم Dagger بكيفية إنشاء أو ربط كائنات لا تملك وصولاً لتعديل الـ Constructor الخاص بها (مثل كلاسات خارجية من مكتبات كـ Retrofit أو OkHttp أو Room).\n\n"
            "3. `@Provides` (دالة بناء الكائنات الحسابية أو الخارجية):\n   - دالة داخل `@Module` تحتوي على كود تنفيذي ينشئ ويعيد كائناً معيناً (مثل استدعاء `Retrofit.Builder().build()`).\n   - يولد Dagger كود مصنع كامل (`Factory`) لكل دالة `@Provides`.\n\n"
            "4. `@Binds` (ربط مجرد لواجهة بتنفيذها - Interface Binding):\n   - دالة مجردة (`abstract fun`) داخل `@Module abstract class` تأخذ التنفيذ الفعلي كمعامل وتعيد الـ Interface.\n   - **أفضل من `@Provides` للأداء**: لا تولد دالة مصنع منفصلة في الـ Bytecode، بل تقوم بتوجيه Dagger مباشرة إلى الـ Constructor الخاص بالـ Implementation، مما يقلل حجم ملفات الـ DEX ويسرع وقت التجميع."
        ),
        "practical_walkthrough": (
            "المقارنة البرمجية بين `@Provides` و `@Binds` وأماكن استخدام كل منها:\n"
            "```kotlin\n"
            "@Module\n"
            "@InstallIn(SingletonComponent::class)\n"
            "object NetworkModule {\n"
            "    // ✅ استخدام @Provides: لأن OkHttpClient كلاس خارجي من مكتبة طرف ثالث:\n"
            "    @Provides\n"
            "    @Singleton\n"
            "    fun provideOkHttpClient(): OkHttpClient {\n"
            "        return OkHttpClient.Builder()\n"
            "            .connectTimeout(30, TimeUnit.SECONDS)\n"
            "            .build()\n"
            "    }\n"
            "}\n"
            "\n"
            "// التنفيذ الفعلي لكلاس الـ Repository ولديه @Inject constructor:\n"
            "class UserRepositoryImpl @Inject constructor(\n"
            "    private val api: UserApi\n"
            ") : UserRepository\n"
            "\n"
            "@Module\n"
            "@InstallIn(SingletonComponent::class)\n"
            "abstract class RepositoryModule {\n"
            "    // ✅ استخدام @Binds: لربط الـ Interface بالـ Implementation بدون توليد كود مصنع إضافي:\n"
            "    @Binds\n"
            "    @Singleton\n"
            "    abstract fun bindUserRepository(\n"
            "        impl: UserRepositoryImpl\n"
            "    ): UserRepository\n"
            "}\n"
            "```"
        ),
        "quick_answer": "@Inject requests dependencies on fields or tells Dagger how to construct a class via its constructor. @Module defines a container for dependency bindings. @Provides provides third-party or builder-constructed instances using executable code. @Binds is an abstract method that binds an interface to its concrete implementation with zero bytecode overhead.",
        "best_answer": (
            "These four annotations form the foundational vocabulary of Dagger and Hilt:\n\n"
            "1. **`@Inject`**: Serves two purposes. On a constructor, it registers the class into Dagger's dependency graph, telling the compiler how to instantiate it. On a field, it requests member injection from the component (used in Android lifecycle classes).\n\n"
            "2. **`@Module`**: Marks a class or interface as a provider of dependency definitions for types Dagger cannot construct via constructor injection (e.g. interfaces, abstract classes, third-party libraries, system services).\n\n"
            "3. **`@Provides`**: Used on concrete functions inside a module to instantiate objects requiring configuration or third-party builders (e.g. `Retrofit`, `RoomDatabase`). Dagger generates an explicit `Factory` class for every `@Provides` method.\n\n"
            "4. **`@Binds`**: Used on abstract functions to bind an interface to a concrete implementation that already has an `@Inject` constructor. It has zero runtime or bytecode overhead because Dagger delegates directly to the implementation's factory without creating intermediary factory classes."
        ),
        "deep_answer": (
            "Under the hood, understanding the DEX impact between `@Provides` and `@Binds` is a classic senior distinction:\n\n"
            "When you write a `@Provides` method:\n"
            "```kotlin\n"
            "@Provides fun provideRepo(impl: UserRepoImpl): UserRepo = impl\n"
            "```\n"
            "Dagger generates a dedicated class `NetworkModule_ProvideRepoFactory.java` implementing `Factory<UserRepo>`. This adds extra method counts, field allocations, and class loading overhead during app startup.\n\n"
            "When you write `@Binds`:\n"
            "```kotlin\n"
            "@Binds abstract fun bindRepo(impl: UserRepoImpl): UserRepo\n"
            "```\n"
            "Dagger generates **zero extra factory classes**. It simply aliases `UserRepo` directly to `UserRepoImpl_Factory` in its internal graph index. This reduces APK DEX size, accelerates compile times, and eliminates unnecessary bridge method execution."
        ),
        "follow_ups": [
            {
                "question": "Can `@Binds` and `@Provides` coexist in the same module?",
                "answer": "Yes, but only if the module is declared as an abstract class or interface, and the `@Provides` methods are placed inside a nested companion object or marked with `@JvmStatic`."
            },
            {
                "question": "What happens if a type has both an `@Inject` constructor and a `@Provides` method?",
                "answer": "Dagger will fail with a compile-time duplicate binding error unless one of them is disambiguated with a Qualifier annotation."
            }
        ]
    },
    {
        "id": "DI-05",
        "arabic_explanation": (
            "شرح تعليقات Hilt الأساسية لتكامل دورة حياة Android:\n`@HiltAndroidApp`، و `@AndroidEntryPoint`، و `@HiltViewModel`:\n\n"
            "1. `@HiltAndroidApp`:\n   - توضع فوق كلاس الـ `Application` الأساسي في التطبيق.\n   - **وظيفتها**: تشعل وتولد شجرة الـ Dagger Graph بالكامل. تولد كود المكون الجذري `SingletonComponent` وتربطه بدورة حياة التطبيق.\n   - بدون هذه التعليمة في `Application` وتسجيله في `AndroidManifest.xml`، سيفشل Hilt تماماً ولن يعمل أي حقن في التطبيق.\n\n"
            "2. `@AndroidEntryPoint`:\n   - توضع فوق كلاسات Android Framework التي ينشئها النظام (Activity, Fragment, View, Service, BroadcastReceiver).\n   - **وظيفتها**: تولد كلاس أساسي (Base Class) يربط دورة حياة هذا المكون بالمكون المناظر له في Hilt (مثل `ActivityComponent` للـ Activity، أو `FragmentComponent` للـ Fragment).\n   - تقوم بتنفيذ الـ Field Injection تلقائياً لجميع الحقول المعلمة بـ `@Inject` قبل وصول الاستدعاء لـ `onCreate`.\n   - **شرط إلزامي**: إذا قمت بتعليم Fragment بـ `@AndroidEntryPoint`، يجب أن تكون الـ Activity الحاضنة له معلمة أيضاً بـ `@AndroidEntryPoint`.\n\n"
            "3. `@HiltViewModel`:\n   - توضع فوق كلاسات الـ `ViewModel`.\n   - **وظيفتها**: تسجل الـ ViewModel داخل `ViewModelComponent`، مما يمكن Hilt من حقن الـ ViewModel عبر الـ Constructor مع الحفاظ على دورة حياة الـ ViewModel التي تعبر تغيرات التكوين (Configuration Changes) مثل دوران الشاشة."
        ),
        "practical_walkthrough": (
            "التطبيق العملي المتكامل لتعليقات Hilt في تطبيق Android:\n"
            "```kotlin\n"
            "// 1. التطبيق الأساسي لتوليد الـ SingletonComponent:\n"
            "@HiltAndroidApp\n"
            "class MainApplication : Application()\n"
            "\n"
            "// 2. الـ ViewModel يتم حقنه عبر المشيد وتسجيله في ViewModelComponent:\n"
            "@HiltViewModel\n"
            "class CartViewModel @Inject constructor(\n"
            "    private val cartRepository: CartRepository,\n"
            "    private val savedStateHandle: SavedStateHandle // محقون تلقائياً بواسطة Hilt!\n"
            ") : ViewModel() {\n"
            "    val cartItems = cartRepository.observeCart()\n"
            "}\n"
            "\n"
            "// 3. الـ Activity تستقبل الـ Field Injection والـ ViewModel:\n"
            "@AndroidEntryPoint\n"
            "class CartActivity : ComponentActivity() {\n"
            "    @Inject lateinit var analytics: AnalyticsHelper // Field Injection\n"
            "    \n"
            "    // إنشاء الـ ViewModel عبر Hilt Factory الرسمية:\n"
            "    private val viewModel: CartViewModel by viewModels()\n"
            "    \n"
            "    override fun onCreate(savedInstanceState: Bundle?) {\n"
            "        super.onCreate(savedInstanceState)\n"
            "        analytics.logEvent(\"cart_opened\")\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "@HiltAndroidApp triggers Hilt's root code generation and instantiates the application-level SingletonComponent. @AndroidEntryPoint attaches Hilt component lifecycles and enables field injection in Android classes like Activities and Fragments. @HiltViewModel registers a ViewModel with Hilt's ViewModelComponent, enabling constructor injection while surviving configuration changes.",
        "best_answer": (
            "These three annotations map directly to Android's process, component, and ViewModel lifecycles:\n\n"
            "1. **`@HiltAndroidApp`**: Required on the custom `Application` class. It initiates Hilt's root code generation, creating the base class that instantiates the top-level `SingletonComponent` during `Application.onCreate()`. All downstream injection relies on this entry point.\n\n"
            "2. **`@AndroidEntryPoint`**: Applied to framework-instantiated classes (Activities, Fragments, Views, Services, BroadcastReceivers). It creates an internal component boundary (e.g. `ActivityComponent`), performing member field injection before `onCreate` completes. A Fragment cannot use `@AndroidEntryPoint` unless its parent Activity is also annotated.\n\n"
            "3. **`@HiltViewModel`**: Applied to Jetpack ViewModels to enable constructor injection without manual `ViewModelProvider.Factory` boilerplate. It automatically provisions `SavedStateHandle` and retains the ViewModel instance across Activity configuration changes (screen rotations)."
        ),
        "deep_answer": (
            "Behind the scenes, the mechanics of bytecode generation and component creation are sophisticated:\n\n"
            "1. **Bytecode Transformation**: The Hilt Gradle plugin transforms `@AndroidEntryPoint class MainActivity` into inheriting from a generated `Hilt_MainActivity`. This generated class overrides `onCreate()` to retrieve the `ActivityComponentManager` and inject fields before user code runs.\n\n"
            "2. **`@HiltViewModel` Mechanism**: Hilt generates an internal multibinding map of ViewModel providers keyed by their Class token. When you call `by viewModels()`, Jetpack's `DefaultViewModelProviderFactory` delegates to Hilt's `HiltViewModelFactory`. This factory resolves the requested ViewModel from `ViewModelComponent` while integrating `SavedStateRegistryOwner`.\n\n"
            "3. **A Common Anti-Pattern**: Never attempt to inject a `@HiltViewModel` via field injection (`@Inject lateinit var vm: MyViewModel`). Doing so bypasses Android's `ViewModelStoreOwner`, instantiating the ViewModel as an ordinary disposable object that will be destroyed and recreated on every screen rotation."
        ),
        "follow_ups": [
            {
                "question": "Can you use `@AndroidEntryPoint` on a Worker in WorkManager?",
                "answer": "No. WorkManager requires `@HiltWorker` combined with HiltWorkerFactory because workers are instantiated by WorkManager's own worker factory infrastructure."
            },
            {
                "question": "What happens if you inject a ViewModel manually using its constructor in production?",
                "answer": "It will not be retained by the Android ViewModelStore and will leak or die immediately on configuration changes."
            }
        ]
    },
    {
        "id": "DI-06",
        "arabic_explanation": (
            "ما هو الـ Dependency Graph (شجرة التبعيات) وما هو الـ Component Hierarchy (تسلسل المكونات الهرمي) في Hilt؟\n\n"
            "1. الـ Dependency Graph (رسم بياني موجه للتبعيات):\n   - هو رسم بياني موجه بدون حلقات (Directed Acyclic Graph - DAG) يربط كل كائن بالتبعيات التي يحتاجها لإنشائه.\n   - يقوم Dagger في وقت التجميع (Compile-time) بفحص هذا الرسم البياني بالكامل للتحقق من:\n     * عدم وجود تبعيات مفقودة (Missing Bindings).\n     * عدم وجود تعارض أو غموض (Ambiguous Bindings).\n     * عدم وجود حلقات دائرية مستحيلة (Cyclic Dependencies، مثل A يحتاج B و B يحتاج A).\n\n"
            "2. الـ Component Hierarchy في Hilt:\n   - يقسم Hilt شجرة التبعيات إلى مكونات هرمية مرتبطة بدورة حياة أندرويد:\n     `SingletonComponent` (طوال عمر التطبيق)\n       └── `ActivityRetainedComponent` (يعبر الـ Configuration Changes)\n             └── `ViewModelComponent` (مرتبط بعمر الـ ViewModel)\n       └── `ActivityComponent` (مرتبط بدورة حياة الـ Activity الواحدة)\n             └── `FragmentComponent` (مرتبط بدورة حياة الـ Fragment)\n                   └── `ViewComponent`\n\n"
            "3. قواعد الرؤية والـ Scoping في التسلسل الهرمي:\n   - **الرؤية باتجاه واحد للأسفل**: المكون الابن (Child) يرى جميع كائنات المكون الأب (Parent) وأجداده، ولكن المكون الأب لا يستطيع رؤية كائنات المكون الابن!\n   - **قاعدة منع التسريب**: لا يمكن لكائن في `SingletonComponent` أن يعتمد على كائن في `ActivityComponent` لأن عمر الـ Singleton أطول بكثير وسيؤدي ذلك إلى تسريب الـ Activity في الذاكرة (Memory Leak)."
        ),
        "practical_walkthrough": (
            "توضيح التسلسل الهرمي وقواعد الرؤية ومنع التبعيات الدائرية:\n"
            "```kotlin\n"
            "// 1. كائن في SingletonComponent: متاح للجميع طوال عمر التطبيق:\n"
            "@Module\n"
            "@InstallIn(SingletonComponent::class)\n"
            "object AppModule {\n"
            "    @Provides @Singleton\n"
            "    fun provideDatabase(@ApplicationContext context: Context): AppDatabase = ...\n"
            "}\n"
            "\n"
            "// 2. كائن في ActivityComponent: يرى الـ Database، ولكن الـ Database لا تراه:\n"
            "@Module\n"
            "@InstallIn(ActivityComponent::class)\n"
            "object ActivityModule {\n"
            "    @Provides @ActivityScoped\n"
            "    fun provideNavigator(activity: Activity): AppNavigator {\n"
            "        return AppNavigator(activity) // مسموح: ActivityComponent لديه مرجع للـ Activity\n"
            "    }\n"
            "}\n"
            "\n"
            "// ❌ خطأ تجميعي فادح يمنعه Dagger:\n"
            "// لو حاول كائن في SingletonComponent طلب AppNavigator:\n"
            "// [Dagger/MissingBinding] AppNavigator cannot be provided without an @Provides-annotated method in SingletonComponent!\n"
            "```"
        ),
        "quick_answer": "A DI graph is a directed acyclic graph (DAG) mapping all application dependencies and validated at compile time. A component hierarchy organizes this graph into parent-child lifecycle scopes (SingletonComponent -> ActivityRetainedComponent -> ActivityComponent -> FragmentComponent). Child components can access parent bindings, but parents cannot access children, preventing memory leaks.",
        "best_answer": (
            "A Dependency Injection Graph is a directed acyclic graph (DAG) where nodes represent objects and directed edges represent dependency requirements. Dagger validates this graph at compile time, guaranteeing zero runtime `NoSuchBeanException` crashes.\n\n"
            "Hilt maps this DAG into an explicit **Component Hierarchy** aligned with Android's system lifecycles:\n"
            "- **`SingletonComponent`**: Root of the graph, lives as long as the application process.\n"
            "- **`ActivityRetainedComponent`**: Survives configuration changes; parents the `ViewModelComponent`.\n"
            "- **`ActivityComponent`**: Bound to a single Activity instance lifecycle.\n"
            "- **`FragmentComponent` & `ViewComponent`**: Bound to individual UI elements.\n\n"
            "The cardinal rule of the hierarchy is **unidirectional visibility**: child components inherit and see all bindings provided by their ancestors, but parents cannot see children. This fundamentally prevents short-lived dependencies (like an `ActivityContext`) from being captured by long-lived singletons."
        ),
        "deep_answer": (
            "In graph theory terms, Dagger builds a topological sort of all requested bindings during compilation.\n\n"
            "If class `A` depends on `B` and class `B` depends on `A`, Dagger detects a **cyclic dependency** and fails compilation with a descriptive cycle trace. In Android, cycles are resolved either by refactoring to an Observer/Event pattern, or by injecting `Lazy<A>` or `Provider<A>`, which defers instantiation and breaks the initialization cycle.\n\n"
            "Regarding component scopes: when you annotate a binding with `@ActivityScoped`, Dagger stores the instantiated object in a cache inside the generated `ActivityComponent`. As long as that specific Activity instance is alive, every injection request receives that identical instance. Once the Activity finishes and its component is garbage-collected, all scoped objects are released. This eliminates manual cache invalidation code."
        ),
        "follow_ups": [
            {
                "question": "How do you break a cyclic dependency between two services in Dagger?",
                "answer": "Inject `dagger.Lazy<T>` or `Provider<T>` into one of the services to defer resolution until runtime, or extract the shared dependency into a third service."
            },
            {
                "question": "Can a ViewModelScoped dependency be injected into an Activity?",
                "answer": "No. `ActivityComponent` is not a child of `ViewModelComponent`. They branch separately under `ActivityRetainedComponent`."
            }
        ]
    },
    {
        "id": "DI-07",
        "arabic_explanation": (
            "مقارنة دقيقة وشاملة بين نطاقات Hilt الثلاثة الأكثر أهمية:\n`@Singleton`، و `@ViewModelScoped`، و `@ActivityScoped`:\n\n"
            "1. `@Singleton` (مرتبط بـ `SingletonComponent`):\n   - **فترة الحياة**: طوال فترة بقاء عملية التطبيق في الذاكرة (Application Process Lifetime).\n   - **متى يُستخدم**: للموارد المشتركة الثقيلة التي يجب أن تكون نسخة واحدة فقط في التطبيق كله (مثل `RoomDatabase`, `OkHttpClient`, `DataStore`, `UserSessionRepository`).\n   - **الخطر**: احتفاظه بأي كائن يحتوي على مرجع لـ Activity أو View يسبب تسريب ذاكرة دائم (Permanent Memory Leak).\n\n"
            "2. `@ViewModelScoped` (مرتبط بـ `ViewModelComponent`):\n   - **فترة الحياة**: يعيش طالما أن الـ ViewModel لا يزال حياً في الـ `ViewModelStore`.\n   - **الميزة العبقرية**: **يعبر تغيرات التكوين (Survives Configuration Changes)** مثل دوران الشاشة (Screen Rotation) وتغيير اللغة.\n   - **متى يُستخدم**: لكائنات إدارة الحالة ومنطق الأعمال التفاعلي الخاص بشاشة أو ميزة معينة والتي يجب ألا يُعاد إنشاؤها عند تدوير الشاشة.\n\n"
            "3. `@ActivityScoped` (مرتبط بـ `ActivityComponent`):\n   - **فترة الحياة**: مرتبط بنسخة الـ Activity الواحدة من `onCreate` حتى `onDestroy`.\n   - **السلوك مع الدوران**: **يتم تدميره وإعادة إنشائه بالكامل مع كل دوران للشاشة!**\n   - **متى يُستخدم**: للكائنات المرتبطة مباشرة بالـ UI والـ Window الخاص بنسخة الـ Activity (مثل Navigator الذي يحتفظ بمرجع للـ Activity للتعامل مع الـ Intents والـ Transitions)."
        ),
        "practical_walkthrough": (
            "المقارنة العملية لتأثير دوران الشاشة على كل Scope:\n"
            "```kotlin\n"
            "// 1. Singleton: نسخة واحدة تعيش طوال عمر تشغيل التطبيق:\n"
            "@Singleton\n"
            "class NetworkMonitor @Inject constructor(@ApplicationContext context: Context)\n"
            "\n"
            "// 2. ViewModelScoped: يعبر دوران الشاشة، مثالي للمنطق الخاص بالشاشة:\n"
            "@ViewModelScoped\n"
            "class OrderFlowCoordinator @Inject constructor(\n"
            "    private val cartRepository: CartRepository\n"
            ")\n"
            "\n"
            "// 3. ActivityScoped: يموت ويُعاد إنشاؤه مع كل دوران للشاشة:\n"
            "@ActivityScoped\n"
            "class ScreenNavigator @Inject constructor(\n"
            "    private val activity: Activity // آمن هنا لأن كلاهما يموت معاً في onDestroy\n"
            ")\n"
            "\n"
            "// جدول مقارنة الـ Scopes وسلوكها:\n"
            "// Scope               Component                Survives Rotation?   Typical Target\n"
            "// @Singleton          SingletonComponent       YES                  Database, Network, Session\n"
            "// @ViewModelScoped   ViewModelComponent       YES                  Screen state holder, UseCase cache\n"
            "// @ActivityScoped    ActivityComponent        NO                   Dialog manager, UI Navigator\n"
            "```"
        ),
        "quick_answer": "@Singleton binds an instance to the application process lifetime for shared resources like databases. @ViewModelScoped binds to the ViewModel lifecycle and survives configuration changes (rotations), ideal for screen-level logic. @ActivityScoped binds strictly to an Activity's window lifecycle and is recreated on screen rotation, designed for UI/Navigation helpers holding an Activity reference.",
        "best_answer": (
            "The difference between these three scopes centers on lifecycle boundaries and behavior during Android configuration changes:\n\n"
            "1. **`@Singleton` (`SingletonComponent`)**: Lives for the entire duration of the application process. It is reserved for expensive, stateless, or application-wide singletons such as `RoomDatabase`, `Retrofit`, and repository caches. Never inject an Activity Context into a Singleton.\n\n"
            "2. **`@ViewModelScoped` (`ViewModelComponent`)**: Bound to the Jetpack ViewModel lifecycle. Its defining trait is that it **survives configuration changes (screen rotations)**. It is ideal for screen-specific use cases, state coordinators, and pagination managers that must retain state across rotations without leaking the UI.\n\n"
            "3. **`@ActivityScoped` (`ActivityComponent`)**: Bound to a single concrete `Activity` instance. It **does NOT survive configuration changes**—it is destroyed when the Activity is destroyed and recreated during recreation. It is meant exclusively for collaborators that require a direct reference to the current `Activity` window, such as custom navigators, dialog coordinators, or view animation controllers."
        ),
        "deep_answer": (
            "A critical pitfall in Android architectural design is **Scope Inflation** (making everything `@Singleton` out of convenience).\n\n"
            "When you annotate a stateful class with `@Singleton`, its memory is never reclaimed by GC until the process dies. In contrast, un-scoped bindings (`Unscoped`) create a lightweight new instance on demand, allowing the ART garbage collector to collect them as soon as their consumers leave scope.\n\n"
            "Furthermore, note the relationship between `@ViewModelScoped` and `@ActivityRetainedScoped`. `@ActivityRetainedComponent` is the parent of `ViewModelComponent`. Both survive configuration changes, but `@ActivityRetainedScoped` instances are shared across **all ViewModels** belonging to that Activity, whereas `@ViewModelScoped` dependencies are scoped strictly to their individual ViewModel instance."
        ),
        "follow_ups": [
            {
                "question": "What happens if a class has no scope annotation in Hilt?",
                "answer": "It is unscoped. Hilt creates a fresh new instance every time that dependency is requested anywhere in the graph."
            },
            {
                "question": "Can an `@ActivityScoped` dependency be injected into a `@ViewModelScoped` class?",
                "answer": "No. A longer-lived component (`ViewModelComponent`, which survives rotation) cannot hold a reference to a shorter-lived component (`ActivityComponent`, which dies on rotation), as this would leak the destroyed Activity."
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

    for item in DI_01_07:
        by_id[item["id"]] = item

    output = [by_id[k] for k in sorted(by_id.keys())]
    DATA_FILE.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {DATA_FILE} with questions DI-01 to DI-07. Total questions: {len(output)}")

if __name__ == "__main__":
    main()
