#!/usr/bin/env python3
"""Generator for DI-08 through DI-14 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "di.json"

DI_08_14 = [
    {
        "id": "DI-08",
        "arabic_explanation": (
            "ما هو الـ Qualifier في Dagger و Hilt؟ وما الفرق بين `@Named` والـ Custom Qualifiers المخصصة؟\n\n"
            "1. المشكلة التي يحلها الـ Qualifier:\n   - في Dagger، يتم تمييز التبعيات افتراضياً بناءً على نوع البيانات (Type/Class). لو كان لديك دالتان توفران نفس النوع (مثل `OkHttpClient` موجه لخدمة التحقق من الهوية بتوكنز خاصة، و `OkHttpClient` آخر عام للبيانات العامة):\n   - سيفشل Dagger في وقت التجميع مع خطأ: `[Dagger/DuplicateBindings] OkHttpClient is bound multiple times!` لأن Dagger لا يعرف أيهما يحقن.\n\n"
            "2. ما هو الـ Qualifier؟\n   - هو تعليق توضيحي (Annotation) يُضاف إلى النوع لتمييز التبعية بشكل فريد في شجرة Dagger (`Type + Qualifier = Unique Key`).\n\n"
            "3. المقارنة بين `@Named` و Custom Qualifiers:\n   - **`@Named(\"auth\")`**: يعتمد على نصوص عادية (String Keys). عيوبه خطيرة في الإنتاج: عرضة للأخطاء الإملائية (Typos)، ولا يدعم إعادة التسمية التلقائية بالـ Refactoring، ولا يكتشف المترجم تعارض النصوص في وقت مبكر.\n   - **Custom Qualifiers (`@Qualifier @Retention(RUNTIME) annotation class AuthOkHttp`)**: المعيار الذهبي الموصى به رسمياً من Google. يمنحك Type-Safety كامل، ودعم لإعادة التسمية عبر IDE Refactoring، ومنع الأخطاء الإملائية نهائياً."
        ),
        "practical_walkthrough": (
            "المقارنة العملية بين `@Named` والـ Custom Qualifiers في Hilt:\n"
            "```kotlin\n"
            "// ❌ استخدام @Named: نصوص سحرية عرضة لأخطاء الـ Typo والـ Refactoring:\n"
            "@Provides @Named(\"auth_client\")\n"
            "fun provideAuthClient(): OkHttpClient = ...\n"
            "\n"
            "@Inject constructor(@Named(\"ath_client\") val client: OkHttpClient) // Typo يسبب خطأ تجميع غامض!\n"
            "\n"
            "// ✅ استخدام Custom Type-Safe Qualifiers (أفضل ممارسة معتمدة):\n"
            "@Qualifier\n"
            "@Retention(AnnotationRetention.BINARY)\n"
            "annotation class AuthClient\n"
            "\n"
            "@Qualifier\n"
            "@Retention(AnnotationRetention.BINARY)\n"
            "annotation class PublicClient\n"
            "\n"
            "@Module\n"
            "@InstallIn(SingletonComponent::class)\n"
            "object NetworkModule {\n"
            "    @Provides @Singleton @AuthClient\n"
            "    fun provideAuthenticatedOkHttpClient(authInterceptor: AuthInterceptor): OkHttpClient {\n"
            "        return OkHttpClient.Builder().addInterceptor(authInterceptor).build()\n"
            "    }\n"
            "    \n"
            "    @Provides @Singleton @PublicClient\n"
            "    fun providePublicOkHttpClient(): OkHttpClient {\n"
            "        return OkHttpClient.Builder().build()\n"
            "    }\n"
            "}\n"
            "\n"
            "// في الـ Repository: حقن آمن ونظيف بنسبة 100%:\n"
            "class UserRepository @Inject constructor(\n"
            "    @AuthClient private val httpClient: OkHttpClient // Type-Safe ومحمي من الـ Typos\n"
            ")\n"
            "```"
        ),
        "quick_answer": "A Qualifier disambiguates multiple bindings of the identical type in the Dagger graph. While @Named uses raw string keys that are prone to typos and refactoring breakage, custom qualifiers (@Qualifier annotation class) provide compile-time type safety, IDE refactoring support, and semantic clarity.",
        "best_answer": (
            "In Dagger and Hilt, bindings are keyed by their return type. When you provide multiple instances of the same type—such as an authenticated `OkHttpClient` with tokens versus an unauthenticated client for public CDN assets—Dagger throws a duplicate binding error at compile time.\n\n"
            "A **Qualifier** decorates the type to create a compound key (`Qualifier + Type`):\n"
            "1. **`@Named`**: A built-in qualifier parameterized by a string literal (`@Named(\"auth\")`). While convenient for quick prototypes, it is brittle in enterprise codebases: strings are prone to silent typos, cannot be refactored safely across modules, and lack semantic IDE autocompletion.\n"
            "2. **Custom Qualifiers**: Defined using `@Qualifier` and `@Retention(AnnotationRetention.BINARY)`. They provide full compile-time type safety, enable seamless IDE find-usages and refactoring, and document the architectural intent directly (e.g. `@AuthOkHttp`, `@CacheDirectory`)."
        ),
        "deep_answer": (
            "Dagger indexes bindings internally in a `Key` structure comprising: `Type`, `Qualifier`, and `MultibindingContributionIdentifier`.\n\n"
            "When you define a custom qualifier, you can also include annotation parameters if you need dynamic keys: e.g. `@Qualifier annotation class Backend(val environment: Env)`. However, modern clean architecture strongly favors distinct zero-arg qualifier annotations per responsibility to prevent leaky configuration details.\n\n"
            "In Hilt, Google includes standard predefined qualifiers: `@ApplicationContext` and `@ActivityContext`. These allow injecting the exact required Android context variant without accidentally passing an Activity context where a long-lived Application context is expected."
        ),
        "follow_ups": [
            {
                "question": "What retention policy should a custom `@Qualifier` use in Kotlin?",
                "answer": "`AnnotationRetention.BINARY` or `RUNTIME`. `BINARY` is preferred because Dagger processes annotations during compilation and does not need runtime reflection overhead."
            },
            {
                "question": "Can you use multiple qualifiers on a single injection site?",
                "answer": "No. Dagger allows at most one qualifier per binding key. Applying multiple qualifiers causes a compile-time error."
            }
        ]
    },
    {
        "id": "DI-09",
        "arabic_explanation": (
            "كيفية توفير وإعداد مكتبات الطرف الثالث الشائعة مثل Retrofit و Room وربط الـ Interfaces في Hilt:\n\n"
            "1. توفير Retrofit و OkHttp:\n   - بما أن Retrofit و OkHttp كلاسات خارجية، لا يمكننا إضافة `@Inject constructor` لها.\n   - نستخدم `@Module` مع كائنات `@Provides` ونطاق `@Singleton` في `SingletonComponent`.\n   - نقوم بحقن `OkHttpClient` داخل دالة بناء `Retrofit`، ثم نوفر واجهات الـ API (مثل `UserApiService`) عبر استدعاء `retrofit.create(UserApiService::class.java)`.\n\n"
            "2. توفير قاعدة بيانات Room والـ DAOs:\n   - يتم بناء الـ `RoomDatabase` عبر `@Provides @Singleton` مع تمرير `@ApplicationContext context: Context`.\n   - يتم توفير الـ DAOs عبر استدعاء الدالة المخصصة في الـ Database: `database.userDao()`.\n\n"
            "3. ربط الـ Interfaces بالتنفيذ الفعلي (Repositories):\n   - نستخدم `@Binds` داخل `@Module abstract class` لربط `UserRepository` بـ `UserRepositoryImpl` بدون كتابة كود تنفيذي أو توليد كلاس مصنع إضافي."
        ),
        "practical_walkthrough": (
            "النمط المعماري الكامل لتوفير Retrofit و Room وربط الـ Repository في Hilt:\n"
            "```kotlin\n"
            "// 1. Network Module: توفير الـ API Client الخارجي:\n"
            "@Module\n"
            "@InstallIn(SingletonComponent::class)\n"
            "object NetworkModule {\n"
            "    @Provides @Singleton\n"
            "    fun provideRetrofit(okHttpClient: OkHttpClient): Retrofit = Retrofit.Builder()\n"
            "        .baseUrl(\"https://api.example.com/\")\n"
            "        .client(okHttpClient)\n"
            "        .addConverterFactory(Json.asConverterFactory(\"application/json\".toMediaType()))\n"
            "        .build()\n"
            "\n"
            "    @Provides @Singleton\n"
            "    fun provideUserApi(retrofit: Retrofit): UserApiService = retrofit.create(UserApiService::class.java)\n"
            "}\n"
            "\n"
            "// 2. Database Module: توفير Room و الـ DAOs:\n"
            "@Module\n"
            "@InstallIn(SingletonComponent::class)\n"
            "object DatabaseModule {\n"
            "    @Provides @Singleton\n"
            "    fun provideDatabase(@ApplicationContext context: Context): AppDatabase = Room.databaseBuilder(\n"
            "        context,\n"
            "        AppDatabase::class.java,\n"
            "        \"app.db\"\n"
            "    ).fallbackToDestructiveMigration().build()\n"
            "\n"
            "    @Provides\n"
            "    fun provideUserDao(db: AppDatabase): UserDao = db.userDao()\n"
            "}\n"
            "\n"
            "// 3. Repository Module: ربط الـ Interface بالتنفيذ الفعلي عبر @Binds:\n"
            "@Module\n"
            "@InstallIn(SingletonComponent::class)\n"
            "abstract class RepositoryModule {\n"
            "    @Binds @Singleton\n"
            "    abstract fun bindUserRepository(impl: UserRepositoryImpl): UserRepository\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Provide Retrofit and Room via @Provides methods in SingletonComponent modules using external builder calls and @ApplicationContext. Extract DAOs by invoking database.dao() provider functions. Finally, bind interface contracts (like UserRepository) to their @Inject-annotated concrete implementations using an abstract @Binds module.",
        "best_answer": (
            "Setting up Retrofit, Room, and Domain interfaces in Hilt illustrates the three core patterns of dependency provisioning:\n\n"
            "1. **Third-Party Client Construction (`@Provides`)**: Because Retrofit and OkHttp are external libraries without `@Inject` constructors, we declare a `NetworkModule` annotated with `@InstallIn(SingletonComponent::class)`. We configure `OkHttpClient` and `Retrofit` using builders, and provide typed API interfaces using `retrofit.create(ApiService::class.java)`.\n\n"
            "2. **Database & DAO Sourcing**: In `DatabaseModule`, we instantiate `Room.databaseBuilder` using `@ApplicationContext Context` to prevent Activity leaks. For DAOs, we write dedicated `@Provides` methods delegating to `database.userDao()`. This allows repositories to inject only the specific DAO they require rather than the entire database instance.\n\n"
            "3. **Contract Binding (`@Binds`)**: For domain interfaces like `UserRepository`, we declare an `abstract class RepositoryModule` using `@Binds`. The concrete `UserRepositoryImpl` has an `@Inject constructor` that accepts the API service and DAO. Dagger binds the interface directly to the implementation with zero intermediary bytecode overhead."
        ),
        "deep_answer": (
            "Architecturally, a clean enterprise setup separates these into distinct Gradle modules:\n\n"
            "- A `:core:network` module exposing only API interfaces, not raw Retrofit or OkHttp internals.\n"
            "- A `:core:database` module exposing entity DAOs, encapsulating Room migration and encryption strategies.\n"
            "- A `:data:user` module providing repository implementations via `@Binds`.\n\n"
            "A critical performance detail: Dao extraction methods like `fun provideUserDao(db: AppDatabase): UserDao = db.userDao()` do not need `@Singleton` annotations because the Room implementation caches the DAO reference internally, and creating a DAO wrapper incurs negligible overhead. However, the `AppDatabase` itself MUST be `@Singleton` to prevent opening multiple SQLite database connections simultaneously, which causes SQLite database lock contention and memory thrashing."
        ),
        "follow_ups": [
            {
                "question": "Why should you inject the DAO instead of the RoomDatabase into a Repository?",
                "answer": "Interface Segregation: Repositories should only know about their specific database operations, not the entire database lifecycle or other unrelated DAOs."
            },
            {
                "question": "What is the danger of missing `@Singleton` on the RoomDatabase provider?",
                "answer": "Every consumer creates a new RoomDatabase instance, spawning multiple SQLite connection pools, wasting memory and risking database locking errors."
            }
        ]
    },
    {
        "id": "DI-10",
        "arabic_explanation": (
            "متى تختار `@Binds` بدلاً من `@Provides` في Dagger و Hilt؟ وما هي الفروق الفنية العميقة بينهما؟\n\n"
            "1. المعيار الأساسي للاختيار:\n   - **استخدم `@Binds`**: عندما تريد ربط واجهة (Interface) بتنفيذ ملموس (Concrete Implementation) تملك أنت كوده ولديه بالفعل مشيد معلّم بـ `@Inject` (`@Inject constructor`).\n   - **استخدم `@Provides`**: في جميع الحالات الأخرى التي تتطلب كوداً تنفيذياً لإنشاء الكائن:\n     * كلاسات من مكتبات خارجية (Retrofit, OkHttp, Room, Gson, Firebase).\n     * كائنات تتطلب استدعاء نمط الـ Builder أو Factory لتكوينها.\n     * كائنات تتطلب تمرير معاملات من نظام أندرويد (مثل استخراج خدمة نظام `context.getSystemService()`).\n\n"
            "2. الفروق الجوهرية تحت الغطاء (Performance & Bytecode):\n   - **`@Provides`**: دالة عادية ملموسة تولد كلاس Java منفصل (`Module_ProvideMethodFactory`). يتطلب استدعاؤها تحميل كلاسات إضافية وتمرير مراجع.\n   - **`@Binds`**: دالة مجردة (`abstract fun`) لا تنفذ أي كود. يخبر المترجم فقط بربط المفتاحين معاً في جدول الفهرسة الداخلي (Graph Mapping) دون توليد أي كلاسات مصانع في الـ DEX."
        ),
        "practical_walkthrough": (
            "المقارنة البرمجية بين الطريقتين والأثر على الكود المولد:\n"
            "```kotlin\n"
            "// ❌ استخدام @Provides لربط Interface بتنفيذ ملموس: تبذير في الـ DEX والكود المولد:\n"
            "@Module\n"
            "@InstallIn(SingletonComponent::class)\n"
            "object InefficientModule {\n"
            "    @Provides // يولد كلاس InefficientModule_ProvideRepoFactory.class في الـ DEX!\n"
            "    fun provideRepo(impl: UserRepositoryImpl): UserRepository = impl\n"
            "}\n"
            "\n"
            "// ✅ استخدام @Binds: دالة مجردة توفر أفضل أداء وبدون أي كود مصنع إضافي:\n"
            "@Module\n"
            "@InstallIn(SingletonComponent::class)\n"
            "abstract class EfficientModule {\n"
            "    @Binds // صفر كود مولد! يتم توجيه UserRepository مباشرة إلى UserRepositoryImpl_Factory\n"
            "    abstract fun bindRepo(impl: UserRepositoryImpl): UserRepository\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Choose @Binds when mapping an interface to a concrete implementation that has an @Inject constructor. Choose @Provides when instantiation requires executable logic, configuration builders, or third-party classes from external libraries. @Binds produces zero factory bytecode overhead, making it faster to compile and lighter in DEX size.",
        "best_answer": (
            "The choice between `@Binds` and `@Provides` hinges on constructor ownership and compilation efficiency:\n\n"
            "1. **When to choose `@Binds`**: Whenever you are binding an interface or abstract class to a concrete class that you own and that has an `@Inject constructor`. It requires the method to be `abstract` and take exactly one parameter (the concrete subtype).\n\n"
            "2. **When to choose `@Provides`**: When creating the instance requires executable logic, such as invoking a builder (`Retrofit.Builder().build()`), retrieving an Android system service (`getSystemService()`), or configuring external SDK objects whose constructors cannot be annotated with `@Inject`.\n\n"
            "3. **Why it matters**: For every `@Provides` method, Dagger generates a companion `Factory` class in Java bytecode. For `@Binds`, Dagger generates **no code at all**; it simply records an alias from the interface to the concrete class factory, saving compilation time and reducing APK method count."
        ),
        "deep_answer": (
            "In large enterprise applications with thousands of bindings, replacing unnecessary `@Provides` methods with `@Binds` yields measurable compile-time and app startup improvements.\n\n"
            "Every generated Factory class must be parsed by Gradle, processed by D8/R8, and loaded by the Android runtime (ART) classloader on startup. By using `@Binds`, you eliminate dozens of intermediate factory allocations.\n\n"
            "A structural caveat: `@Binds` methods must reside in an `abstract class` or an `interface`. If you need both `@Provides` and `@Binds` in the same logical module, you can declare the module as an abstract class, put `@Binds` methods as abstract members, and put `@Provides` methods inside a nested `companion object` annotated with `@JvmStatic` or on the companion object directly."
        ),
        "follow_ups": [
            {
                "question": "Can `@Binds` take multiple arguments?",
                "answer": "No. A `@Binds` method must have exactly one parameter whose type is assignable to the return type."
            },
            {
                "question": "Does `@Binds` change the scope of a dependency?",
                "answer": "No. If you want the bound interface to be a Singleton, you must apply `@Singleton` to either the `@Binds` declaration or the implementation class."
            }
        ]
    },
    {
        "id": "DI-11",
        "arabic_explanation": (
            "كيفية حقن تطبيقات متعددة لنفس الواجهة (Multiple Implementations of the Same Contract) في Hilt:\n\n"
            "1. الحالات الشائعة:\n   - واجهة `AnalyticsTracker` ولها تطبيقان: `FirebaseAnalyticsTracker` و `MixpanelAnalyticsTracker`.\n   - واجهة `ImageLoader` ولها: `LocalCacheImageLoader` و `RemoteImageLoader`.\n\n"
            "2. الحل الأول: استخدام الـ Qualifiers (للاختيار الصريح عند الحقن):\n   - ننشئ تعليقات توضيحية مخصصة مثل `@Firebase` و `@Mixpanel`.\n   - نقوم بربط كل تطبيق باستخدام التعليق الخاص به.\n   - في الكلاس المستهلك، نطلب التطبيق المحدد: `@Firebase private val tracker: AnalyticsTracker`.\n\n"
            "3. الحل الثاني: استخدام الـ Multibindings (`@IntoSet` أو `@IntoMap`):\n   - إذا أردنا حقن جميع التطبيقات معاً في كائن مجمع (Composite Pattern):\n   - نستخدم `@IntoSet` لربط كل تطبيق داخل `Set<AnalyticsTracker>`.\n   - نقوم بحقن `Set<AnalyticsTracker>` داخل `CompositeAnalyticsTracker` الذي يقوم بالمرور على جميع المتعقبات وإرسال الحدث إليها جميعاً.\n   - الميزة: إضافة أي Tracker جديد لا تتطلب تعديل الكلاس المجمع نهائياً (Open/Closed Principle)."
        ),
        "practical_walkthrough": (
            "تطبيق Multibindings لحقن مجموعة من التطبيقات لنفس العقد:\n"
            "```kotlin\n"
            "interface AnalyticsTracker {\n"
            "    fun logEvent(name: String)\n"
            "}\n"
            "\n"
            "@Module\n"
            "@InstallIn(SingletonComponent::class)\n"
            "abstract class AnalyticsModule {\n"
            "    @Binds @IntoSet\n"
            "    abstract fun bindFirebaseTracker(impl: FirebaseTracker): AnalyticsTracker\n"
            "\n"
            "    @Binds @IntoSet\n"
            "    abstract fun bindMixpanelTracker(impl: MixpanelTracker): AnalyticsTracker\n"
            "}\n"
            "\n"
            "// الكلاس المجمع (Composite Pattern) يستقبل المجموعة كاملة تلقائياً عبر Hilt:\n"
            "@Singleton\n"
            "class CompositeAnalyticsTracker @Inject constructor(\n"
            "    private val trackers: Set<@JvmSuppressWildcards AnalyticsTracker>\n"
            ") : AnalyticsTracker {\n"
            "    override fun logEvent(name: String) {\n"
            "        trackers.forEach { it.logEvent(name) }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "To inject multiple implementations of the same contract, use Qualifiers (@Qualifier) if consumers need to choose a specific implementation explicitly at compile-time. Use Multibindings (@IntoSet or @IntoMap) if you want to assemble all implementations into a collection or map, ideal for plugins and composite dispatchers.",
        "best_answer": (
            "Depending on whether the implementations should be selected individually or aggregated together, Dagger provides two primary patterns:\n\n"
            "1. **Disambiguation via Qualifiers**: When different consumers require specific implementations (e.g. an in-memory test cache vs. an encrypted disk cache), annotate each binding and injection site with a dedicated `@Qualifier` (e.g. `@MemoryCache` and `@DiskCache`).\n\n"
            "2. **Aggregation via Multibindings (`@IntoSet` / `@IntoMap`)**: When you need to collect all implementations into an extensible system (e.g. analytics dispatchers, health checkers, or payment processors). Each module registers its implementation using `@Binds @IntoSet`. The aggregator class injects `Set<@JvmSuppressWildcards MyContract>`, iterating over all providers without knowing them individually.\n\n"
            "This adheres strictly to the Open/Closed Principle: new feature modules can contribute new implementations to the set without modifying any existing module code."
        ),
        "deep_answer": (
            "When using Dagger Multibindings in Kotlin, you must be mindful of Java generics wildcard variance.\n\n"
            "By default, Kotlin generates wildcard generic types like `Set<? extends AnalyticsTracker>` in Java bytecode. Dagger treats `Set<AnalyticsTracker>` and `Set<? extends AnalyticsTracker>` as completely distinct binding keys, causing a confusing `[Dagger/MissingBinding]` error at compile time.\n\n"
            "To fix this, always annotate the injected collection parameter with `@JvmSuppressWildcards`: e.g. `Set<@JvmSuppressWildcards AnalyticsTracker>`. This forces the Kotlin compiler to emit the raw invariant type `Set<AnalyticsTracker>` in bytecode, allowing Dagger's multibinding graph to resolve seamlessly."
        ),
        "follow_ups": [
            {
                "question": "What is the purpose of `@IntoMap` in Dagger?",
                "answer": "It allows binding implementations into a `Map<K, V>` using a custom `@MapKey` annotation (e.g. mapping an enum or string key to an implementation strategy)."
            },
            {
                "question": "Why is `@JvmSuppressWildcards` needed in Kotlin Dagger multibindings?",
                "answer": "To prevent Kotlin from emitting Java wildcard generics (`? extends T`), which causes Dagger to fail to match the invariant collection key."
            }
        ]
    },
    {
        "id": "DI-12",
        "arabic_explanation": (
            "كيف تتفاعل نطاقات Hilt مع كائنات الـ Context وملكية دورة الحياة (Lifecycle Ownership) في Android؟\n\n"
            "1. أنواع الـ Context في أندرويد:\n   - **Application Context**: يعيش طوال فترة عمل الـ Process. آمن للاستخدام في العمليات العامة ومكتبات الـ Database والـ Network.\n   - **Activity Context**: يعيش فقط من `onCreate` إلى `onDestroy`. يحتوي على معلومات الـ Window والـ Themes والـ UI Layouts.\n\n"
            "2. كارثة تسريب الذاكرة (Memory Leak via Scope Mismatch):\n   - إذا قمت بحقن `Activity Context` داخل كائن معلّم بنطاق `@Singleton`، فإن كائن الـ Singleton سيحتفظ بمرجع للـ Activity حتى بعد تدميرها (مثل عند دوران الشاشة أو الضغط على Back).\n   - النتيجة: تسريب الـ Activity كاملة بجميع الـ Views والصور والـ Drawables في الذاكرة (تسريب عشرات الميجابايتات وصولاً إلى OOM Crash).\n\n"
            "3. الحماية المعمارية في Hilt:\n   - يوفر Hilt تعليقات نوعية واقية:\n     * `@ApplicationContext context: Context`: يُحقن بأمان في أي مكان في شجرة التبعيات (خاصة في الـ Singletons).\n     * `@ActivityContext context: Context`: متاح فقط داخل `ActivityComponent` وتوابعه، وممنوع حقنه داخل الـ `SingletonComponent` في وقت التجميع."
        ),
        "practical_walkthrough": (
            "المقارنة بين الحقن الخاطئ المسبب للتسريب والحقن الآمن عبر Hilt Qualifiers:\n"
            "```kotlin\n"
            "// ❌ كارثة تسريب ذاكرة: Singleton يحتفظ بـ Activity Context:\n"
            "@Singleton\n"
            "class LeakyToastManager @Inject constructor(\n"
            "    private val context: Context // لو تم تمرير Activity هنا -> Activity تسربت للأبد في الذاكرة!\n"
            ")\n"
            "\n"
            "// ✅ حقن آمن في Singleton باستخدام @ApplicationContext:\n"
            "@Singleton\n"
            "class SafeNotificationManager @Inject constructor(\n"
            "    @ApplicationContext private val context: Context // آمن 100% طوال حياة التطبيق\n"
            ") {\n"
            "    fun notify(...) { /* استخدام Application Context لإرسال تنبيه */ }\n"
            "}\n"
            "\n"
            "// ✅ حقن ActivityContext فقط داخل كائن معلّم بـ @ActivityScoped:\n"
            "@ActivityScoped\n"
            "class DialogPresenter @Inject constructor(\n"
            "    @ActivityContext private val context: Context // مسموح: كلاهما يموت معاً في onDestroy\n"
            ") {\n"
            "    fun showDialog() { AlertDialog.Builder(context).show() }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Hilt prevents memory leaks by pairing Context lifecycles with component scopes. @ApplicationContext lives with the process and is safe for @Singleton bindings. @ActivityContext is tied to an individual UI window and must only be injected into @ActivityScoped or unscoped UI collaborators, never into Singletons or ViewModels.",
        "best_answer": (
            "The interaction between DI scopes and Android Context is the primary defense line against severe memory leaks:\n\n"
            "1. **Application Context vs. Activity Context**: `ApplicationContext` is tied to process lifetime and lacks UI theme information, making it safe for singletons like databases and notification services. `ActivityContext` holds references to the view hierarchy, window manager, and theme attributes.\n\n"
            "2. **The Scope Mismatch Bug**: If an Activity Context is injected into an object with a longer lifetime—such as an `@Singleton` repository or an `@ViewModelScoped` state holder—the destroyed Activity cannot be garbage collected after screen rotation or back-press navigation. This leaks megabytes of bitmap memory and view trees.\n\n"
            "3. **Hilt's Type-Safe Guards**: Hilt provides `@ApplicationContext` and `@ActivityContext` qualifiers. If you attempt to inject `@ActivityContext` into a class provided inside `SingletonComponent`, Dagger catches the invalid scope boundary and **fails at compile time**, preventing the leak before code ever ships to production."
        ),
        "deep_answer": (
            "A subtle production hazard occurs through **Indirect Context Capturing via Callbacks or Listeners**.\n\n"
            "Even if a `@Singleton` class only injects primitive dependencies, if an Activity registers a non-static callback or lifecycle observer on that singleton and forgets to deregister in `onDestroy`, the singleton retains the Activity instance implicitly through the callback closure (`this@MyActivity`).\n\n"
            "To mitigate this in robust architectures:\n"
            "- Never register long-lived listeners with raw Activity callbacks.\n"
            "- Expose Kotlin Flows (`SharedFlow` or `StateFlow`) from the Singleton repository, allowing UI layers to collect using `repeatOnLifecycle(Lifecycle.State.STARTED)` which cancels and detaches observation cleanly whenever the UI goes into the background."
        ),
        "follow_ups": [
            {
                "question": "Can you inflate a layout using ApplicationContext?",
                "answer": "Technically yes, but it will lack the Activity's theme and styling attributes, resulting in broken typography, incorrect colors, and layout bugs."
            },
            {
                "question": "Can `@ApplicationContext` leak an Activity?",
                "answer": "No. The ApplicationContext is a process-wide singleton created by the Android OS that lives until the entire application process terminates."
            }
        ]
    },
    {
        "id": "DI-13",
        "arabic_explanation": (
            "كيفية استبدال التبعيات في اختبارات الوحدة (Unit Tests) والاختبارات المجهزة (Instrumented Tests) في Hilt:\n\n"
            "1. في الـ JVM Unit Tests (الاختبارات النقية المعزولة):\n   - **لا تستخدم Hilt على الإطلاق!**\n   - بفضل استخدامنا لـ Constructor Injection، نقوم بإنشاء الـ ViewModel أو الـ UseCase مباشرة عبر المشيد في كود الاختبار ونمرر كائنات Fake أو Mock يدويًا: `val vm = OrderViewModel(FakeOrderRepository())`.\n   - هذا الاختبار يعمل في 10 ميلي ثانية وبدون أي معالجة لأطر العمل.\n\n"
            "2. في الـ Instrumented Tests (اختبارات الشاشات و Espresso/Compose UI):\n   - هنا نريد تشغيل الـ Android Framework و Hilt Graph الحقيقي، ولكن نريد استبدال خادم الشبكة الحقيقي أو قاعدة البيانات بـ Fake Test Double.\n   - نستخدم تعليقات Hilt الرسمية:\n     * `@HiltAndroidTest`: لتفعيل Hilt في ملف الاختبار.\n     * `@UninstallModules(NetworkModule::class)`: لإلغاء تثبيت موديول الإنتاج.\n     * كتابة `@TestInstallIn(components = [SingletonComponent::class], replaces = [NetworkModule::class])` لموديول الاختبار البديل.\n     * استخدام `@BindValue`: لحقن كائن بديل مباشرة كمتغير داخل ملف الاختبار."
        ),
        "practical_walkthrough": (
            "المقارنة بين استبدال التبعيات في Unit Test مقابل Instrumented Test مع Hilt:\n"
            "```kotlin\n"
            "// 1. في JVM Unit Test: اختبار سريع ومباشر بدون Hilt وبدون أي أطر عمل:\n"
            "class OrderViewModelTest {\n"
            "    @Test\n"
            "    fun testOrderPlacement() = runTest {\n"
            "        val fakeRepo = FakeOrderRepository()\n"
            "        val viewModel = OrderViewModel(fakeRepo) // تمرير الـ Fake مباشرة في المشيد!\n"
            "        viewModel.placeOrder(\"item_1\")\n"
            "        assertTrue(fakeRepo.hasOrder(\"item_1\"))\n"
            "    }\n"
            "}\n"
            "\n"
            "// 2. في Android Instrumented Test: استبدال موديول الإنتاج بـ Test Double:\n"
            "@UninstallModules(AnalyticsModule::class)\n"
            "@HiltAndroidTest\n"
            "class CheckoutScreenUiTest {\n"
            "    @get:Rule(order = 0)\n"
            "    var hiltRule = HiltAndroidRule(this)\n"
            "\n"
            "    // استبدال التبعية بقيمة مزيفة داخل الاختبار مباشرة:\n"
            "    @BindValue\n"
            "    val fakeAnalytics: AnalyticsTracker = FakeAnalyticsTracker()\n"
            "\n"
            "    @Before\n"
            "    fun init() {\n"
            "        hiltRule.inject()\n"
            "    }\n"
            "\n"
            "    @Test\n"
            "    fun verifyCheckoutTriggersAnalytics() {\n"
            "        // اختبار الـ UI مع التأكد من أن fakeAnalytics تم حقنه في الـ Graph الحقيقي!\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "In JVM unit tests, bypass Hilt completely and instantiate classes directly via constructor injection using in-memory Fakes. In instrumented UI and Robolectric tests, use @HiltAndroidTest, uninstall production modules via @UninstallModules or @TestInstallIn, and inject test doubles effortlessly using @BindValue.",
        "best_answer": (
            "Dependency substitution differs fundamentally between local unit tests and instrumented graph tests:\n\n"
            "1. **JVM Unit Tests (90% of your test suite)**: Never bootstrap Hilt or Dagger. Because domain and presentation classes use Constructor Injection, you instantiate the subject directly in pure Kotlin: `val viewModel = MyViewModel(fakeRepository)`. This runs in milliseconds on the JVM without annotation processors, reflection, or Android runtime overhead.\n\n"
            "2. **Instrumented & Robolectric Tests**: When testing UI navigation or database migrations that require the real Android framework, use Hilt's dedicated test support:\n"
            "   - Annotate test classes with `@HiltAndroidTest` and add the `HiltAndroidRule`.\n"
            "   - Use `@UninstallModules(ProductionModule::class)` to strip live production bindings.\n"
            "   - Provide test doubles either globally with `@TestInstallIn` or locally within the test class using `@BindValue val fakeApi: ApiService = FakeApiService()`."
        ),
        "deep_answer": (
            "A critical distinction in enterprise testing is choosing between `@TestInstallIn` and `@UninstallModules`:\n\n"
            "- **`@TestInstallIn`**: Replaces a production module across **all** tests in that test source set. This is ideal for global test doubles, such as replacing a live networking module with an in-memory mock web server or fake repository across the entire test suite.\n\n"
            "- **`@UninstallModules` + `@BindValue`**: Used for test-case-specific overrides. Each test class can inject a different mock configuration. However, be aware that each unique combination of `@UninstallModules` forces Hilt to generate a distinct Dagger component variant, which can increase instrumented test compilation times.\n\n"
            "Also, remember to configure `HiltTestRunner` in `build.gradle` (`testInstrumentationRunner = \"com.example.HiltTestRunner\"`) to ensure the test application uses Hilt's test classloader."
        ),
        "follow_ups": [
            {
                "question": "What happens if you forget `hiltRule.inject()` in a Hilt test?",
                "answer": "Any `@Inject lateinit var` fields or `@BindValue` configurations declared in the test class will remain uninitialized, throwing NullPointerException."
            },
            {
                "question": "Can you use MockK or Mockito with `@BindValue`?",
                "answer": "Yes. `@BindValue val mockRepo: Repository = mockk()` works seamlessly and binds the mock into Hilt's test component."
            }
        ]
    },
    {
        "id": "DI-14",
        "arabic_explanation": (
            "ما هي الكوارث والمشاكل التي تحدث إذا جعلت كل كائن في التطبيق `@Singleton`؟\n\n"
            "1. ظاهرة الـ Scope Inflation (تضخم الـ Singleton):\n   - يميل المطور المبتدئ إلى وضع `@Singleton` فوق كل Repository و UseCase و Helper ظناً منه أن هذا 'يوفر الذاكرة' بمنع تكرار الإنشاء.\n\n"
            "2. المشاكل الناتجة عن جعل كل شيء Singleton:\n   - **تضخم استهلاك الذاكرة (Memory Bloat)**: كائنات الـ Singleton لا يتم جمعها بواسطة مجمع القمامة (GC) أبداً طوال فترة عمل التطبيق. الكائنات التي كان ينبغي أن تعيش لمدة ثانيتين فقط أثناء تصفح شاشة معينة تظل محبوسة في الـ Heap للأبد.\n   - **تلوث الحالة والبيانات القديمة (Stale State & Memory Pollution)**: لو كان الـ Singleton يحتوي على كاش أو قائمة أو متغيرات داخلية، فإن تسجيل خروج المستخدم (Logout) لن يفرغ هذه البيانات، مما قد يعرض بيانات مستخدم سابق لمستخدم جديد!\n   - **اختبارات فاشلة وغير معزولة (Flaky & Order-Dependent Tests)**: في اختبارات الـ JVM، تتشارك الاختبارات نفس الـ Singletons، مما يجعل نجاح اختبار معتمداً على نتيجة اختبار آخر قبله.\n   - **مخاطر التزامن والـ Concurrency**: إذا طلبت عدة Threads الوصول إلى كائن Singleton في نفس اللحظة بدون مزامنة دقيقة (Thread Synchronization)، تحدث أخطاء الـ Race Conditions وتلف البيانات."
        ),
        "practical_walkthrough": (
            "المقارنة بين كائن متورط بـ Singleton غير مبرر وكائن Unscoped نقي:\n"
            "```kotlin\n"
            "// ❌ Singleton غير مبرر: يحتفظ ببيانات ملوثة في الذاكرة حتى بعد مغادرة الشاشة:\n"
            "@Singleton\n"
            "class BadInvoiceFilterHelper @Inject constructor() {\n"
            "    // كاش داخلي يظل محبوساً في الذاكرة طوال حياة التطبيق!\n"
            "    private val temporaryCache = mutableListOf<Invoice>()\n"
            "    fun filter(...) { /* ... */ }\n"
            "}\n"
            "\n"
            "// ✅ Unscoped (بدون أي Scope): كائن خفيف الوزن ينشأ ويتحرر فور انتهاء الحاجة إليه:\n"
            "class GoodInvoiceFilterHelper @Inject constructor() {\n"
            "    // دالة نقية بدون الاحتفاظ بأي حالة في الذاكرة:\n"
            "    fun filter(invoices: List<Invoice>, query: String): List<Invoice> {\n"
            "        return invoices.filter { it.matches(query) }\n"
            "    }\n"
            "}\n"
            "// مجمع القمامة في ART (Android Runtime) يجمع الكائنات الخفيفة بسرعة فائقة في الـ Young Generation!\n"
            "```"
        ),
        "quick_answer": "Making every dependency a Singleton causes permanent memory bloat, prevents garbage collection of transient objects, leads to stale state across user sessions, creates concurrency bugs across threads, and couples unit tests into order-dependent flakiness. Scopes should be applied strictly to expensive, truly process-wide shared resources.",
        "best_answer": (
            "Dogmatically annotating every class with `@Singleton` is a dangerous architectural anti-pattern known as 'Scope Inflation'.\n\n"
            "It introduces four critical production failures:\n"
            "1. **Unreclaimable Memory Retention**: Objects scoped to `@Singleton` can never be collected by the ART garbage collector while the app process lives. Transient helpers, formatters, and screen-specific caches occupy permanent RAM in the Old Generation heap.\n"
            "2. **State Leakage Across User Sessions**: If a singleton repository or manager holds user-specific data in memory, logging out and logging in with another account risks serving stale, unpurged data from the previous user, creating serious data privacy breaches.\n"
            "3. **Concurrency & Thread Safety Hazards**: Singletons are accessed concurrently by multiple background threads and coroutines. Unless internally synchronized with thread-safe primitives (like `Mutex` or atomic references), they produce subtle race conditions and data corruption.\n\n"
            "Default to **unscoped bindings**. The ART runtime allocates and garbage-collects short-lived, transient objects with virtually zero overhead. Reserve `@Singleton` exclusively for expensive, process-wide resources (Room database, HTTP connection pools, and core event buses)."
        ),
        "deep_answer": (
            "From an ART memory management standpoint, scoping an object changes its GC lifetime tier.\n\n"
            "Unscoped objects are allocated in ART's **Young Generation (Eden space)**. When their consumer leaves scope, ART collects them during minor GC cycles in sub-millisecond pauses. "
            "When an object is `@Singleton`, it quickly gets promoted to the **Old/Tenured Generation**. Collecting objects from the Old Gen requires full concurrent mark-sweep or compacting GC cycles, which cause frame drops (jank) and UI freezes.\n\n"
            "Furthermore, for user session data, the correct architectural approach is not `@Singleton`, but a custom user-scoped component or an explicit session repository that clears all in-memory flows upon receiving an `AuthEvent.LoggedOut` notification."
        ),
        "follow_ups": [
            {
                "question": "What is the memory cost of an unscoped object in Android?",
                "answer": "Negligible. Allocating a standard Kotlin object in ART takes single-digit nanoseconds, and young generation garbage collection is highly optimized."
            },
            {
                "question": "How should user-specific repositories be cleared on logout if they are `@Singleton`?",
                "answer": "Either encapsulate them within a clearable session state holder that invalidates caches on logout, or create a custom UserComponent that is destroyed upon session termination."
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

    for item in DI_08_14:
        by_id[item["id"]] = item

    output = [by_id[k] for k in sorted(by_id.keys())]
    DATA_FILE.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {DATA_FILE} with questions DI-08 to DI-14. Total questions: {len(output)}")

if __name__ == "__main__":
    main()
