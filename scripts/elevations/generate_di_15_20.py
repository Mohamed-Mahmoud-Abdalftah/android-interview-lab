#!/usr/bin/env python3
"""Generator for DI-15 through DI-20 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "di.json"

DI_15_20 = [
    {
        "id": "DI-15",
        "arabic_explanation": (
            "كيف تتعامل مع الحقن المساعد (Assisted Injection) أو المعاملات التي تُعرف فقط في وقت التشغيل (Runtime Parameters) في Dagger و Hilt؟\n\n"
            "1. ما هي المشكلة التي يحلها الـ Assisted Injection؟\n   - في الوضع الطبيعي، يعرف Dagger جميع التبعيات في وقت التجميع عبر شجرة الـ DI (مثل `UserRepository`, `Analytics`).\n   - ولكن في أحيان كثيرة، يحتاج الكائن إلى معامل لا يُعرف إلا في وقت التشغيل أو من الـ UI (مثل `orderId: String` يتم استلامه من intent أو ضغطة زر المستخدم، أو `productId`).\n   - قبل Assisted Injection، كان المطورون يضطرون لعمل حيل سيئة مثل إنشاء كائن بـ `lateinit var orderId` وتعيينها بعد الإنشاء، مما يفتح الباب لحالات `UninitializedPropertyAccessException`.\n\n"
            "2. كيف يعمل الـ Assisted Injection الرسمي؟\n   - نستخدم تعليقة `@AssistedInject` على الـ Constructor بدلاً من `@Inject`.\n   - نضع تعليقة `@Assisted` على المعاملات التي تأتي في وقت التشغيل.\n   - ننشئ واجهة مصنع (Factory Interface) معلّمة بـ `@AssistedFactory` تحتوي على دالة إنشاء تأخذ فقط المعاملات المؤقتة (`@Assisted`).\n   - يتولى Dagger توليد كود المصنع تلقائياً، بحيث يحقن التبعيات المعروفة من الـ Graph، ويطلب منك فقط تمرير الـ `orderId` عند الاستدعاء."
        ),
        "practical_walkthrough": (
            "التطبيق العملي لـ Assisted Injection لبناء كائن يحتاج لمعامل في وقت التشغيل:\n"
            "```kotlin\n"
            "// 1. الكائن يطلب تبعيات من الـ Graph وتبعية من وقت التشغيل (@Assisted):\n"
            "class OrderReceiptGenerator @AssistedInject constructor(\n"
            "    private val repository: OrderRepository, // محقون تلقائياً من Dagger Graph\n"
            "    private val formatter: CurrencyFormatter, // محقون تلقائياً من Dagger Graph\n"
            "    @Assisted private val orderId: String // معامل يأتي في وقت التشغيل فقط!\n"
            ") {\n"
            "    fun generateReceipt(): Receipt = repository.getOrder(orderId).formatWith(formatter)\n"
            "}\n"
            "\n"
            "// 2. واجهة المصنع المساعد (Assisted Factory):\n"
            "@AssistedFactory\n"
            "interface OrderReceiptFactory {\n"
            "    fun create(orderId: String): OrderReceiptGenerator\n"
            "}\n"
            "\n"
            "// 3. الاستخدام في الـ ViewModel أو الـ Presenter:\n"
            "@HiltViewModel\n"
            "class OrderDetailsViewModel @Inject constructor(\n"
            "    private val receiptFactory: OrderReceiptFactory // حقن المصنع المساعد\n"
            ") : ViewModel() {\n"
            "    fun printReceipt(selectedOrderId: String) {\n"
            "        // استدعاء دالة الإنشاء وتمرير المعامل الحي:\n"
            "        val generator = receiptFactory.create(selectedOrderId)\n"
            "        val receipt = generator.generateReceipt()\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Assisted injection combines graph dependencies known at compile time with runtime parameters known only at creation time. Annotate the target constructor with @AssistedInject, mark runtime parameters with @Assisted, and declare a factory interface annotated with @AssistedFactory. Dagger generates the factory implementation automatically.",
        "best_answer": (
            "Assisted Injection solves the problem of instantiating an object that requires both graph dependencies (managed by Dagger) and runtime parameters (known only dynamically at user interaction time, such as an `orderId` or `userId`).\n\n"
            "The pattern works in three steps:\n"
            "1. **`@AssistedInject`**: Annotate the target class constructor with `@AssistedInject` instead of `@Inject`. Mark the runtime parameters with `@Assisted`.\n"
            "2. **`@AssistedFactory`**: Define an interface with a single `create(...)` method matching the exact types and names of the `@Assisted` parameters.\n"
            "3. **Automatic Assembly**: Dagger implements the factory at compile time. Consumers simply inject the factory via standard constructor injection and invoke `factory.create(runtimeParam)` whenever the runtime parameter becomes available.\n\n"
            "For ViewModels specifically, Hilt provides built-in assisted injection for `SavedStateHandle`, eliminating the need to write custom assisted factories just to read navigation route arguments."
        ),
        "deep_answer": (
            "Prior to Dagger's native `@AssistedInject` (introduced in Dagger 2.31), developers relied on third-party libraries (Square's AssistedInject) or resorted to mutable state setters, which broke immutability and risked runtime null pointer exceptions.\n\n"
            "Under the hood, Dagger generates an implementation of your factory interface (e.g. `OrderReceiptFactory_Impl`). "
            "The generated class injects `Provider<OrderRepository>` and `Provider<CurrencyFormatter>` from the parent component, and in its `create(orderId)` method, it calls `new OrderReceiptGenerator(repositoryProvider.get(), formatterProvider.get(), orderId)`.\n\n"
            "This preserves the Inversion of Control principle: the consumer never touches or manages the compile-time dependencies, only supplying the dynamic payload, while the created object remains completely immutable (`val`)."
        ),
        "follow_ups": [
            {
                "question": "Can you have multiple `@Assisted` parameters of the same type in the constructor?",
                "answer": "Yes, but you must disambiguate them using identifier names: `@Assisted(\"sourceId\")` and `@Assisted(\"targetId\")` on both the constructor and the factory interface."
            },
            {
                "question": "How does Assisted Injection compare to passing arguments to a method?",
                "answer": "If the object needs the runtime parameter across its entire lifecycle to configure internal state, Assisted Injection is superior because fields remain constructor-initialized and immutable."
            }
        ]
    },
    {
        "id": "DI-16",
        "arabic_explanation": (
            "كيف تدمج وتدير حقن التبعيات (DI) عبر موديولات Gradle المتعددة (Multi-Module Architecture) في Hilt؟\n\n"
            "1. التحدي المعماري في الـ Multi-Module:\n   - في المشاريع المقسمة وفق Clean Architecture و Feature Modularization:\n     * موديول الـ Feature (`:feature:checkout`) لا يجب أن يعرف تفاصيل موديول الـ Implementation الخرساني (`:data:payment`).\n     * موديول الـ App الأساسي (`:app`) يجمع كل الموديولات.\n\n"
            "2. آلية عمل Hilt في الـ Multi-Module:\n   - **Decentralized Modules via `@InstallIn`**: بفضل تعليمة `@InstallIn(SingletonComponent::class)`، يمكن لأي مكتبة أو موديول Gradle فرعي أن يعلن عن الـ Bindings الخاصة به محلياً داخل الموديول نفسه.\n   - **Compilation Aggregation**: عندما يقوم موديول `:app` بالتجميع، يقوم Hilt بمسح الـ Classpath وجمع جميع الـ Modules المعلمة بـ `@InstallIn` عبر جميع موديولات Gradle ودمجها في الـ Dagger Component النهائي تلقائياً!\n\n"
            "3. أفضل ممارسة لتنظيم الـ Modules والـ DI:\n   - الموديول العام أو الـ API (`:core:network-api`) يعرّف الـ Interfaces فقط.\n   - موديول الـ Implementation (`:core:network-impl`) يطبق الـ Interface ويوفر Hilt Module يربط الـ Interface بالـ Implementation عبر `@Binds`.\n   - موديول الـ Feature يعتمد فقط على `:core:network-api` ويحقن الـ Interface مباشرة دون معرفة كلاسات الـ Implementation!"
        ),
        "practical_walkthrough": (
            "تنظيم التبعيات والـ Hilt Modules في هيكل Multi-Module نظيف:\n"
            "```kotlin\n"
            "// 📁 في موديول ':feature:login' (يعتمد فقط على :core:auth-api):\n"
            "@HiltViewModel\n"
            "class LoginViewModel @Inject constructor(\n"
            "    private val authService: AuthService // واجهة فقط من موديول الـ API!\n"
            ") : ViewModel() { /* ... */ }\n"
            "\n"
            "// 📁 في موديول ':core:auth-impl' (يحتوي على التنفيذ الفعلي وموديول Hilt):\n"
            "class AuthServiceImpl @Inject constructor(\n"
            "    private val httpClient: OkHttpClient\n"
            ") : AuthService { /* ... */ }\n"
            "\n"
            "@Module\n"
            "@InstallIn(SingletonComponent::class)\n"
            "abstract class AuthBindingModule {\n"
            "    @Binds @Singleton\n"
            "    abstract fun bindAuthService(impl: AuthServiceImpl): AuthService\n"
            "}\n"
            "\n"
            "// 📁 في موديول ':app':\n"
            "// dependencies {\n"
            "//     implementation(projects.feature.login)\n"
            "//     implementation(projects.core.authImpl)\n"
            "// }\n"
            "// يقوم Hilt تلقائياً بجمع AuthBindingModule وحقنه في LoginViewModel أثناء التجميع في :app!\n"
            "```"
        ),
        "quick_answer": "In multi-module projects, Hilt uses decentralized aggregation: individual library and data modules declare bindings locally via @InstallIn, and the :app module aggregates them all at compile time into the root component. Feature modules depend only on API interface modules, ensuring encapsulation and fast incremental builds.",
        "best_answer": (
            "Integrating Hilt across multiple Gradle modules relies on Hilt's decentralized compilation model:\n\n"
            "1. **Decentralized Binding Declaration**: Unlike pure Dagger where a central root component had to import every submodule, Hilt modules use `@InstallIn(SingletonComponent::class)` inside their respective Gradle library modules. Modules contribute bindings independently without central registration.\n\n"
            "2. **Strict Inversion of Dependencies**: A feature module (`:feature:checkout`) depends only on an API module (`:data:payment-api`) containing pure interfaces. The implementation module (`:data:payment-impl`) contains the concrete classes and the `@Module` with `@Binds`. The `:app` module depends on both, allowing Hilt to resolve the graph while the feature module remains isolated from implementation details.\n\n"
            "3. **Incremental Build Optimization**: Feature modules do not depend on sibling feature implementations. If code inside `:data:payment-impl` changes, Gradle only recompiles that module and `:app`, leaving unaffected feature modules in the Gradle build cache."
        ),
        "deep_answer": (
            "Under the hood, Hilt achieves cross-module aggregation via **Metadata Indexing**.\n\n"
            "During Gradle compilation of a library module, the Hilt symbol processor generates marker classes in an internal package (`dagger.hilt.internal.aggregatedroot` or `hilt_aggregated_deps`). "
            "These marker classes encode module references into the module's JAR metadata. "
            "When the final `:app` module builds, Hilt reads the transitively collected metadata from the classpath, constructs the master Dagger component, and verifies the entire graph.\n\n"
            "A critical nuance: **Dynamic Feature Modules (Play Feature Delivery)** invert standard dependency edges (`:app` does NOT depend on `:dynamic_feature`; rather, the dynamic feature depends on `:app`). "
            "Because `:app` cannot aggregate metadata from downstream dynamic features, standard Hilt `@InstallIn` does not work inside dynamic features. Instead, you must use `@EntryPoint` to pull dependencies from the base app."
        ),
        "follow_ups": [
            {
                "question": "Why shouldn't feature modules depend on each other's implementation modules?",
                "answer": "It creates tight coupling, circular dependency risks, and invalidates Gradle build caches, causing full rebuilds whenever any feature changes."
            },
            {
                "question": "Can you use Hilt in an Android library module that will be distributed as an AAR?",
                "answer": "No, Hilt requires the root application module to assemble the graph. Reusable public libraries should use pure constructor injection or manual factory patterns."
            }
        ]
    },
    {
        "id": "DI-17",
        "arabic_explanation": (
            "عندما يقوم SDK خارجي بإنشاء كائناته داخلياً دون دعم لـ Hilt، كيف تدمج التبعيات بأمان؟ (Integrating Hilt with Non-Hilt SDKs):\n\n"
            "1. طبيعة المشكلة:\n   - بعض مكتبات الطرف الثالث (مثل Google Maps, WorkManager قديماً, أو Payment SDKs) تطلب منك تمرير كائن أو تقوم هي بإنشاء كلاساتك عبر الـ Reflection بدون دعم لـ `@AndroidEntryPoint`.\n   - النتيجة: لا يمكنك استخدام `@Inject lateinit var` أو Constructor Injection لأن الكائن لا ينتمي لشجرة Hilt.\n\n"
            "2. الحل الرسمي في Hilt: استخدام الـ `@EntryPoint` و `EntryPoints.get()`:\n   - **تعريف الـ `@EntryPoint`**: ننشئ Interface معلّم بـ `@EntryPoint` ونحدد المكون التابع له عبر `@InstallIn(SingletonComponent::class)`.\n   - في هذه الواجهة، نعلن عن التوابع التي نحتاج استخراجها (مثل `fun getAnalytics(): AnalyticsTracker`).\n   - **استخراج التبعية يدويًا داخل كائن الـ SDK**: باستخدام دالة المساعد `EntryPoints.get(appContext, MyCustomEntryPoint::class.java)`، نقوم بسحب التبعية من شجرة Hilt في لحظة التشغيل.\n\n"
            "3. الفائدة المعمارية:\n   - يمنحك منفذ وصول شرعي ورسمي لسحب التبعيات من شجرة Hilt دون الحاجة لكسر مبادئ الحماية أو اللجوء للـ Singletons العامة الملوثة."
        ),
        "practical_walkthrough": (
            "استخدام @EntryPoint لسحب التبعيات داخل كائن غير مدار بواسطة Hilt:\n"
            "```kotlin\n"
            "// 1. تعريف نقطة الدخول (Entry Point Interface):\n"
            "@EntryPoint\n"
            "@InstallIn(SingletonComponent::class)\n"
            "interface CustomSdkEntryPoint {\n"
            "    fun getAnalyticsTracker(): AnalyticsTracker\n"
            "    fun getAuthTokenProvider(): AuthTokenProvider\n"
            "}\n"
            "\n"
            "// 2. كلاس ينشئه الـ SDK الخارجي داخلياً بدون علم Hilt:\n"
            "class ExternalVendorCallbackHandler : VendorSdkCallback {\n"
            "    override fun onVendorEvent(context: Context, eventPayload: String) {\n"
            "        // استخراج الـ EntryPoint من ApplicationContext بأمان:\n"
            "        val appContext = context.applicationContext\n"
            "        val entryPoint = EntryPoints.get(\n"
            "            appContext,\n"
            "            CustomSdkEntryPoint::class.java\n"
            "        )\n"
            "        \n"
            "        // استخدام التبعيات المحقونة من Hilt بشكل طبيعي:\n"
            "        val tracker = entryPoint.getAnalyticsTracker()\n"
            "        tracker.logEvent(\"vendor_event: $eventPayload\")\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "To integrate an SDK that instantiates objects internally without Hilt support, use Hilt's @EntryPoint pattern. Define an interface annotated with @EntryPoint and @InstallIn(SingletonComponent::class), declare the required accessor methods, and extract dependencies using EntryPoints.get(context.applicationContext, MyEntryPoint::class.java).",
        "best_answer": (
            "When integrating third-party SDKs that construct objects internally via reflection or custom factories where `@AndroidEntryPoint` cannot be attached, you bridge the gap using **Hilt Entry Points**:\n\n"
            "1. **Define the Entry Point**: Create an interface annotated with `@EntryPoint` and specify its scope with `@InstallIn(SingletonComponent::class)`. Expose getter methods for the exact dependencies the SDK component needs.\n"
            "2. **Extract Dependencies**: Inside the SDK's lifecycle method where an Android `Context` is available, retrieve the generated component via Hilt's utility: `val entryPoint = EntryPoints.get(context.applicationContext, MySdkEntryPoint::class.java)`.\n"
            "3. **Zero Leaks**: By pulling from the `applicationContext`, you ensure that the SDK object does not accidentally retain an Activity reference, and your dependencies remain managed and scoped by the central Hilt graph."
        ),
        "deep_answer": (
            "Entry Points represent Dagger's programmatic pull interface into a push-based graph.\n\n"
            "Under the hood, `@InstallIn(SingletonComponent::class)` causes Hilt to make the generated `DaggerSingletonComponent` implement your `@EntryPoint` interface. "
            "When you call `EntryPoints.get(context, MyEntryPoint::class.java)`, Hilt casts the `Application` (which implements `GeneratedComponentManager`) to the generated Dagger component interface, returning a typed instance.\n\n"
            "This pattern is heavily utilized in production for:\n"
            "- Custom Jetpack Compose composition locals that need Dagger services.\n"
            "- Custom Views inflated by XML that need dependencies before being attached to a window.\n"
            "- Legacy ContentProviders, BroadcastReceivers registered dynamically in NDK code, or custom Glide/Coil model loaders."
        ),
        "follow_ups": [
            {
                "question": "Can an `@EntryPoint` be scoped to an `ActivityComponent` instead of `SingletonComponent`?",
                "answer": "Yes. If the SDK object needs an Activity-scoped dependency, annotate the EntryPoint with `@InstallIn(ActivityComponent::class)` and pass the Activity instance to `EntryPoints.get(activity, EntryPoint::class.java)`."
            },
            {
                "question": "What is the danger of using `@EntryPoint` everywhere in your own code?",
                "answer": "It turns your architecture into a Service Locator anti-pattern. EntryPoints should be strictly reserved for framework and SDK boundaries that cannot use constructor injection."
            }
        ]
    },
    {
        "id": "DI-18",
        "arabic_explanation": (
            "تم التقاط مرجع `Activity Context` بالخطأ داخل كائن `@Singleton`. أين يكمن الخطأ المعماري في تصميم الـ DI وكيف تصححه؟\n\n"
            "1. تشريح الخطأ المعماري (Root Cause Analysis):\n   - **عدم تطابق نطاقات دورة الحياة (Scope Lifetime Mismatch)**: كائن `@Singleton` يعيش طوال فترة عمل التطبيق (`Application Lifetime`). بينما الـ `Activity` تعيش فقط حتى يتم تدميرها (مثل عند دوران الشاشة).\n   - عندما يحتفظ الـ Singleton بمرجع للـ Activity (سواء كـ Context، أو عبر Callback أو Listener مسجل بـ Anonymous Class):\n   - مجمع القمامة (Garbage Collector) يعجز عن تحرير الـ Activity المدمرة لأن هناك مسار وصول حي (GC Strong Reference) إليها من جذر الـ GC Root (الـ SingletonComponent).\n   - النتيجة: تسريب الـ Activity كاملة بشاشتها وجميع مكونات الـ Views والصور المرتبطة بها (تسريب 20-50MB مع كل تدوير للشاشة حتى الـ OOM Crash).\n\n"
            "2. التصحيح المعماري الحاسم:\n   - **إذا كان الكائن يحتاج Context فقط للوصول لموارد عامة أو خدمات النظام**: استبدل الـ Context بـ `@ApplicationContext context: Context`.\n   - **إذا كان الكائن يحتاج Activity فعلياً للتعامل مع الـ UI/Navigation**: انزع عنه نطاق `@Singleton` وانقله إلى `ActivityComponent` بنطاق `@ActivityScoped`، أو مرر الـ Activity كمعامل في الدالة (`Method Parameter`) بدلاً من تخزينها كحقل في الـ Constructor."
        ),
        "practical_walkthrough": (
            "إصلاح تسريب الـ Activity Context وإثبات الحل عبر الكود والتحقق:\n"
            "```kotlin\n"
            "// ❌ الخطأ الكارثي: Singleton يحتفظ بمرجع Activity Context:\n"
            "@Singleton\n"
            "class ToastHelper @Inject constructor(\n"
            "    private val context: Context // لو تم تمرير Activity -> تسريب دائم لكل Activity تفتحها!\n"
            ") {\n"
            "    fun showToast(msg: String) { Toast.makeText(context, msg, Toast.LENGTH_SHORT).show() }\n"
            "}\n"
            "\n"
            "// ✅ التصحيح 1: إذا كان يحتاج مجرد Context عام -> استخدام @ApplicationContext:\n"
            "@Singleton\n"
            "class ToastHelperFixed @Inject constructor(\n"
            "    @ApplicationContext private val context: Context // آمن 100% ولا يسرّب Activity أبداً\n"
            ")\n"
            "\n"
            "// ✅ التصحيح 2: إذا كان يحتاج Activity فعلياً (مثل فتح Dialog أو Transition) -> تغيير الـ Scope:\n"
            "@ActivityScoped\n"
            "class DialogHelper @Inject constructor(\n"
            "    @ActivityContext private val activityContext: Context // مسموح: كلاهما يموت معاً في onDestroy\n"
            ")\n"
            "\n"
            "// التحقق: في LeakCanary أو Android Studio Memory Profiler:\n"
            "// التأكد من عدم وجود Retained Instances للـ Activity بعد استدعاء activity.recreate()!\n"
            "```"
        ),
        "quick_answer": "The architectural defect is a scope-lifetime mismatch: a process-lived @Singleton captures an ephemeral ActivityContext, holding a strong reference that prevents garbage collection on rotation. Fix it by replacing the dependency with @ApplicationContext, or re-scoping the collaborator to @ActivityScoped in ActivityComponent.",
        "best_answer": (
            "The design defect is a **Scope-Lifetime Mismatch** where a component with an application-level lifetime retains an instance of a short-lived framework lifecycle component.\n\n"
            "1. **Root Cause**: When an Activity Context is injected into an `@Singleton` service, the singleton retains a strong reference to that specific Activity instance. When the user rotates the device or presses back, Android calls `onDestroy()`, but ART's garbage collector cannot free the Activity because a strong reference path leads from the GC Root (the singleton container) into the destroyed Activity. This leaks the entire DecorView, window manager, and all rendered bitmaps.\n\n"
            "2. **The Architectural Fix**:\n   - If the singleton only needs system services, file directories, or application resources, switch the parameter to `@ApplicationContext private val context: Context`.\n   - If the collaborator genuinely requires an Activity (e.g. for window manipulation or custom dialogs), it must **not** be a Singleton. Demote its scope to `@ActivityScoped` and install its module in `ActivityComponent`, or pass the Activity transiently as a function parameter rather than retaining it as an injected constructor property."
        ),
        "deep_answer": (
            "To detect, diagnose, and prevent this class of leaks in CI/CD pipelines and production:\n\n"
            "1. **Detection via LeakCanary**: LeakCanary intercepts destroyed Activities via `ActivityLifecycleCallbacks.onActivityDestroyed()`, waits 5 seconds, forces a GC, and if the reference persists, dumps the HPROF heap and computes the shortest retention path to the GC Root. The retention path will show `SingletonComponent_Impl -> LeakyService.context -> DestroyedActivity`.\n\n"
            "2. **Dagger Compile-Time Prevention**: In Hilt, if you try to inject `@ActivityContext` into a class installed in `SingletonComponent`, Dagger will **fail compilation** immediately with: `[Dagger/IncompatiblyScopedBindings] ActivityContext is scoped to ActivityComponent and cannot be provided to SingletonComponent`.\n\n"
            "The bug typically slips in when developers use a generic un-annotated `Context` binding or manually pass `this` from an Activity into a singleton repository method, bypassing Dagger's compile-time graph validator."
        ),
        "follow_ups": [
            {
                "question": "Can passing an Activity into a suspending function cause a leak?",
                "answer": "Yes. If the coroutine is launched in a long-lived scope (like GlobalScope or ApplicationScope) and suspends for a long time, it retains the Activity context in the coroutine continuation frame until completion."
            },
            {
                "question": "How do you verify the leak is permanently resolved?",
                "answer": "Run an automated test that rotates the Activity repeatedly (`activityScenario.recreate()`), asserts zero retained instances in LeakCanary, and inspects the Android Studio Memory Profiler heap dump."
            }
        ]
    },
    {
        "id": "DI-19",
        "arabic_explanation": (
            "موديول ميزة ديناميكية (Dynamic-Feature Module) يحتاج إلى تبعيات موفرة من تطبيق الأساس (Base App Module). ما هي الحلول والخيارات المعمارية في Hilt؟\n\n"
            "1. التحدي المعماري للـ Dynamic Feature Modules (DFMs):\n   - في موديولات أندرويد العادية، يعتمد موديول الـ `:app` على الموديولات الفرعية (`:app -> :feature`).\n   - في الـ Dynamic Features (التي يتم تنزيلها عند الطلب عبر Play Feature Delivery)، **تنعكس العلاقة**: موديول الـ DFM هو الذي يعتمد على `:app` (`:dynamic_feature -> :app`)، ولا يعرف `:app` أي كود داخل الـ DFM في وقت التجميع!\n   - بسبب هذا الانعكاس، يعجز Hilt عن تجميع الـ Modules الخاصة بالـ DFM داخل الـ `SingletonComponent` الرئيسي في `:app`.\n\n"
            "2. الخيارات والحلول المعمارية المعتمدة:\n   - **الحل الرسمي الأقوى (Hilt `@EntryPoint`)**:\n     * يحدد الـ Base App واجهات التبعيات العامة في `:app` أو `:core`.\n     * داخل الـ Dynamic Feature، ينشئ المطور `@EntryPoint` لاستخراج التبعيات من الـ `applicationContext` عبر `EntryPoints.get()`.\n   - **الحل الثاني: Dagger Component Dependencies**:\n     * إنشاء Dagger Component مستقل داخل الـ DFM يعلن عن اعتماده على الـ Base Component: `@Component(dependencies = [BaseAppComponent::class])`.\n   - **الحل الثالث: Pure Manual DI / Interfaces Boundary**:\n     * تمرير واجهات التبعيات عبر Navigation Intents أو Factory Provider مسجل في طبقة الأساس."
        ),
        "practical_walkthrough": (
            "استخدام @EntryPoint لتمرير التبعيات من الـ Base App إلى الـ Dynamic Feature Module:\n"
            "```kotlin\n"
            "// 📁 في موديول ':core' (مرئي لكل من :app و :dynamic_feature):\n"
            "@EntryPoint\n"
            "@InstallIn(SingletonComponent::class)\n"
            "interface DynamicFeatureDependencies {\n"
            "    fun getAuthRepository(): AuthRepository\n"
            "    fun getNetworkClient(): OkHttpClient\n"
            "}\n"
            "\n"
            "// 📁 داخل موديول ':feature_on_demand' (Dynamic Feature Module):\n"
            "// يتم استخراج التبعيات داخل الـ Activity أو Fragment الخاص بالميزة عند تنزيلها:\n"
            "class DynamicFeatureActivity : ComponentActivity() {\n"
            "    private lateinit var authRepository: AuthRepository\n"
            "\n"
            "    override fun onCreate(savedInstanceState: Bundle?) {\n"
            "        super.onCreate(savedInstanceState)\n"
            "        \n"
            "        // سحب التبعيات من Base App Graph عبر الـ EntryPoint:\n"
            "        val dependencies = EntryPoints.get(\n"
            "            applicationContext,\n"
            "            DynamicFeatureDependencies::class.java\n"
            "        )\n"
            "        \n"
            "        authRepository = dependencies.getAuthRepository()\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Dynamic feature modules invert the Gradle dependency edge (the feature depends on :app), preventing Hilt from aggregating feature bindings at compile time. Bridge dependencies from the base app using Hilt EntryPoints (@EntryPoint) defined in a shared core module and retrieved at runtime via EntryPoints.get(applicationContext, CoreDependencies::class.java).",
        "best_answer": (
            "Dynamic Feature Modules (DFMs) introduce an inverted dependency structure: the dynamic feature module depends on `:app`, but `:app` cannot depend on the dynamic feature. Because Hilt compiles the root component in `:app`, it cannot see classes inside DFMs at compile time, breaking standard Hilt code generation.\n\n"
            "To supply base app dependencies to a dynamic feature, senior architectures employ two proven strategies:\n\n"
            "1. **Hilt `@EntryPoint` (Recommended)**: Define an `@EntryPoint` interface in a shared `:core` module that `:app` implements. When the DFM is downloaded and launched, DFM classes pull dependencies dynamically using `EntryPoints.get(applicationContext, CoreEntryPoint::class.java)`. This works with zero custom Dagger components.\n\n"
            "2. **Dagger Component Dependencies**: If the dynamic feature needs its own internal DI graph, define a custom Dagger component inside the DFM that declares the base app's component as a dependency (`@Component(dependencies = [BaseComponent::class])`). The DFM component requests base dependencies and manages internal feature-scoped singletons."
        ),
        "deep_answer": (
            "When designing for Google Play Feature Delivery with Hilt, several edge cases require careful planning:\n\n"
            "1. **Application Classloader Isolation**: When a dynamic feature is installed on-demand, its classes are loaded into a new `SplitCompat` classloader. If the DFM uses reflection to look up classes that were stripped by R8 in the base app, it will crash with `ClassNotFoundException` unless keep rules are configured.\n\n"
            "2. **Lifecycle of Scoped Objects in DFMs**: Any object scoped inside the base app (`@Singleton`) remains alive as long as the application process lives. However, if your DFM is dynamically uninstalled or its feature activity finishes, ensure that any listeners registered with the base app are explicitly cleared to prevent leaking the DFM's classloader, which would prevent the OS from reclaiming disk and memory space."
        ),
        "follow_ups": [
            {
                "question": "Can a dynamic feature module use `@AndroidEntryPoint`?",
                "answer": "Starting with newer Hilt versions, limited DFM support exists, but standard practice still relies on `@EntryPoint` because DFMs cannot contribute bindings back into the base app's SingletonComponent."
            },
            {
                "question": "Why can't `:app` depend on a dynamic feature module?",
                "answer": "Because dynamic feature modules are packaged as separate APK splits delivered on-demand by Google Play; a compile-time dependency from `:app` would bundle it into the base APK, defeating dynamic delivery."
            }
        ]
    },
    {
        "id": "DI-20",
        "arabic_explanation": (
            "كيف تهاجر تطبيقاً ضخماً من حقن التبعيات اليدوي (Manual DI) إلى Hilt مع الحفاظ على استقرار الاختبارات وسير العمل؟\n\n"
            "1. استراتيجية الهجرة المتدرجة (Strangler Fig Pattern):\n   - محاولة تحويل التطبيق كاملاً إلى Hilt في PR واحد هي وصفة مضمونة للكوارث والتوقف عن الإنتاج.\n   - الهجرة الناجحة تتم عبر خطوات تدريجية مرحلية، مع استمرار التطبيق في البناء والعمل بنسبة 100% في كل خطوة.\n\n"
            "2. خطة العمل خطوة بخطوة:\n   - **المرحلة 1: التأسيس والبنية التحتية**: إضافة Hilt Gradle Plugin و KSP، وإعداد `@HiltAndroidApp` على كلاس الـ `Application`، وبناء Hilt Module يوفر الـ Singletons الأساسية القائمة (مثل `RoomDatabase`, `Retrofit`).\n   - **المرحلة 2: جسر الربط المؤقت (Bridge / Adapter)**: ربط الـ `AppContainer` اليدوي بـ Hilt عبر `@EntryPoint`، بحيث تستطيع الكودات القديمة سحب تبعياتها من Hilt، والعكس.\n   - **المرحلة 3: هجرة الشاشات من القمة للقاع (Top-Down by Screen)**: تحويل شاشة كاملة بمفردها (Activity/Fragment إلى `@AndroidEntryPoint` و ViewModel إلى `@HiltViewModel`)، مع الإبقاء على باقي الشاشات تعمل بالـ Manual DI.\n   - **المرحلة 4: استقرار الاختبارات**: التأكد من أن جميع Unit Tests لا تزال تعمل على الـ JVM بدون Hilt، وتحديث اختبارات الـ UI تدريجياً باستخدام `@HiltAndroidTest`."
        ),
        "practical_walkthrough": (
            "خطة الهجرة التدريجية وجسر الربط المؤقت بين Manual DI و Hilt:\n"
            "```kotlin\n"
            "// 1. التطبيق الأساسي مع تفعيل Hilt:\n"
            "@HiltAndroidApp\n"
            "class App : Application() {\n"
            "    // الاحتفاظ بالـ AppContainer القديم كجسر مؤقت أثناء الهجرة:\n"
            "    lateinit var legacyContainer: LegacyAppContainer\n"
            "    \n"
            "    override fun onCreate() {\n"
            "        super.onCreate()\n"
            "        legacyContainer = LegacyAppContainer(this)\n"
            "    }\n"
            "}\n"
            "\n"
            "// 2. توفير الـ Legacy Container داخل Hilt Graph لخدمة الكود المهاجر حديثاً:\n"
            "@Module\n"
            "@InstallIn(SingletonComponent::class)\n"
            "object LegacyBridgeModule {\n"
            "    @Provides @Singleton\n"
            "    fun provideLegacyContainer(@ApplicationContext context: Context): LegacyAppContainer {\n"
            "        return (context as App).legacyContainer\n"
            "    }\n"
            "}\n"
            "\n"
            "// 3. تحويل الشاشات تدريجياً: شاشة شاشة دون كسر أي اختبار!\n"
            "@HiltViewModel\n"
            "class MigratedFeatureViewModel @Inject constructor(\n"
            "    private val repository: ModernRepository // محقون بنظافة عبر Hilt\n"
            ") : ViewModel()\n"
            "```"
        ),
        "quick_answer": "Migrate from manual DI to Hilt incrementally using the Strangler Fig pattern. Setup @HiltAndroidApp on Application, create bridging modules to share instances between the legacy container and Hilt, and migrate one feature at a time (ViewModel to @HiltViewModel, Activity to @AndroidEntryPoint). Unit tests remain untouched because constructor injection requires no framework.",
        "best_answer": (
            "Migrating an enterprise codebase from manual DI to Hilt must be executed incrementally without stopping feature development or breaking existing test suites:\n\n"
            "1. **Phase 1: Root Foundation & Core Infrastructure**:\n   - Install Hilt plugins and apply `@HiltAndroidApp` to `Application`.\n   - Provide core process-level singletons (`AppDatabase`, `OkHttpClient`, `DataStore`) via Hilt modules in `SingletonComponent`.\n\n"
            "2. **Phase 2: Bidirectional Bridge**:\n   - Expose the legacy `AppContainer` to Hilt via a bridge module so new Hilt features can consume legacy singletons.\n   - Expose Hilt bindings to the legacy container via `@EntryPoint` so non-migrated screens can consume newly migrated Hilt services.\n\n"
            "3. **Phase 3: Screen-by-Screen Migration**:\n   - Convert features vertically: annotate the ViewModel with `@HiltViewModel` and the Activity/Fragment with `@AndroidEntryPoint`.\n   - Once all consumers of a legacy service migrate to Hilt, delete that service from `AppContainer`.\n\n"
            "4. **Phase 4: Preserving Test Seams**:\n   - JVM Unit Tests remain 100% unaffected because classes use constructor injection—they still instantiate classes directly with Fakes.\n   - Gradually migrate instrumented UI tests to `@HiltAndroidTest` using `@BindValue`."
        ),
        "deep_answer": (
            "The operational risk during a DI migration is **Instance Duplication**.\n\n"
            "If your legacy container creates an instance of `UserSessionManager` and Hilt's module creates another instance of `UserSessionManager`, the app now holds two distinct session holders in memory! "
            "A login event in the legacy screen updates instance A, but a migrated Hilt screen observes stale state in instance B, causing silent and critical production state bugs.\n\n"
            "To prevent instance duplication during the migration:\n"
            "- Designate exactly **one owner** for each singleton instance during the bridge phase. If the legacy container owns it, Hilt's `@Provides` method must delegate to `legacyContainer.userSessionManager`.\n"
            "- When ready to flip ownership, move instantiation entirely into Hilt, and have the legacy container pull it via an `@EntryPoint`.\n"
            "- Only decommission the legacy container when its member count reaches zero."
        ),
        "follow_ups": [
            {
                "question": "How do you prevent duplicate instances of singletons during migration?",
                "answer": "Designate a single source of truth: have Hilt provide the instance from the legacy container, or have the legacy container delegate to Hilt via an EntryPoint."
            },
            {
                "question": "Do JVM unit tests need to be rewritten when adopting Hilt?",
                "answer": "No. Because classes rely on constructor injection, pure unit tests continue to pass test doubles directly into constructors without touching Hilt."
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

    for item in DI_15_20:
        by_id[item["id"]] = item

    output = [by_id[k] for k in sorted(by_id.keys())]
    DATA_FILE.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {DATA_FILE} with questions DI-15 to DI-20. Total questions: {len(output)}")

if __name__ == "__main__":
    main()
