#!/usr/bin/env python3
"""
Elevation script for MOD questions: MOD-08 to MOD-14.
Topic: Gradle Modularization & Dependency Boundaries (MOD)
Phase 4, Batch 2
"""

import os
import sys

sys.path.insert(0, os.path.abspath("scripts/elevations"))
import elevation_engine as ee

TOPIC_AR = "تقسيم المشروع لموديولات (Modularization) وحدود التبعيات"
REVIEWED_DATE_AR = "تمت المراجعة والتحقق في 17 أكتوبر 2026"

DATA = {}

# ==========================================
# MOD-08: What belongs in :core:network, :core:database, :core:ui, and feature modules?
# ==========================================
DATA["MOD-08"] = {
    "concept_en": """A clean multi-module architecture draws strict boundaries between reusable, domain-agnostic infrastructure and domain-specific feature logic:
- :core:network: Contains foundational transport plumbing including configured OkHttpClient instances, Retrofit builders, token refresh authenticators, certificate pinning configs, and network connectivity observers. It strictly excludes business DTOs, endpoint interfaces, and feature-specific models.
- :core:database: Provides the underlying Room database engine, base DAOs, database encryption wrappers (SQLCipher), migration runners, and common type converters. Feature entities belong in feature data modules.
- :core:ui: Holds reusable Compose widgets, layout primitives, image loader bindings, and accessibility wrappers. Pure visual styling tokens, colors, and themes reside in :core:designsystem.
- Feature modules (:feature:<name>): Encapsulate domain use cases, ViewModels, Compose screens, UI state definitions, feature-specific repository implementations, and private API service interfaces.""",
    "walkthrough_en": """Separation of concerns between infrastructure core and feature modules:
```kotlin
// 1. :core:network provides configured Retrofit factory
class NetworkClientFactory @Inject constructor(private val okHttpClient: OkHttpClient) {
    fun createRetrofit(baseUrl: String): Retrofit = Retrofit.Builder()
        .baseUrl(baseUrl)
        .client(okHttpClient)
        .addConverterFactory(Json.asConverterFactory("application/json".toMediaType()))
        .build()
}

// 2. :feature:orders defines its OWN private API interface and DTOs
interface OrdersApiService {
    @GET("/v1/orders")
    suspend fun getOrders(): List<OrderDto>
}

// 3. DI in :feature:orders binds service via :core:network factory
@Provides
fun provideOrdersApi(factory: NetworkClientFactory): OrdersApiService =
    factory.createRetrofit("https://api.store.com").create()
```""",
    "short_en": """Core modules provide domain-agnostic infrastructure: core:network handles HTTP transport and token refresh; core:database manages the Room engine and encryption; and core:ui supplies reusable layout widgets and atomic controls. Feature modules house all business logic, containing domain use cases, ViewModels, Compose screens, feature repositories, and specific API endpoints.""",
    "structured_en": """Designing a scalable modular architecture requires drawing clear boundaries between infrastructural platform modules and user-facing feature modules.
In the infrastructure tier, core:network provides preconfigured HTTP engines, certificate pinning, and authentication interceptors without containing feature API endpoints or business models.
Similarly, core:database manages the foundational Room database instance, encryption wrappers, and migration runners without defining specific feature tables.
The core:ui module supplies generic Compose modifiers, accessibility helpers, and custom layouts, while visual design tokens reside in core:designsystem.
Feature modules sit above this infrastructure tier.
Each feature module owns its entire business domain slice, including domain use cases, ViewModels, Compose screens, repository implementations, and private Retrofit service interfaces.
This separation ensures core modules remain stable, leaf-oriented dependencies that never require recompilation when product features change.""",
    "deep_senior_en": """The defining hallmark of mature Android systems architecture is the ruthless exclusion of business knowledge from infrastructural core modules.
A frequent architectural failure occurs when teams place feature-specific endpoints or business models into :core:network, turning it into a bottleneck that forces full recompilation whenever a single API endpoint changes.
In our production standard, :core:network provides only transport-level mechanics.
It exports configured Retrofit builders, OkHttp interceptors for OAuth token renewal, certificate pinning definitions, and JSON serialization converters, but zero endpoint interfaces.
Each feature module declares its own private Retrofit interfaces and network DTOs within its internal data layer.
The same strict rule applies to :core:database: it exports the Room database builder, SQLCipher passphrase providers, and migration orchestrators, while individual feature entities and DAOs are registered modularly.
At the UI layer, :core:ui provides technical interaction wrappers such as keyboard insets listeners, pull-to-refresh containers, and image loading coil bindings, whereas :core:designsystem houses atomic tokens and buttons.
Feature modules encapsulate everything related to user flows, maintaining private domain models and state machines.
This strict structural hygiene ensures that core infrastructure changes infrequently, maximizing remote build cache hit rates across distributed development teams. We also configure automated linter rules to flag any PR that introduces domain-specific entity names or endpoint paths inside infrastructure modules, preserving platform purity.""",
    "meta_ar": {
        "id": "MOD-08",
        "questionAr": "ما الذي يجب وضعه في موديولات :core:network و :core:database و :core:ui وموديولات الميزات؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "تحديد الحدود الفاصلة بين البنية التحتية المشتركة ومنطق الأعمال الخاص بكل ميزة، وتجنب تلويث موديولات core بنماذج بيانات تجارية، وتطبيق مبدأ المسؤولية الواحدة.",
        "concept_ar": "ترسم المعمارية متعددة الموديولات النظيفة حدوداً فاصلة وصارمة بين البنية التحتية المجردة ومنطق الميزات التجاري: موديول :core:network يوفر محركات الاتصال (OkHttpClient و Retrofit Builders و Interceptors لتجديد التوكن) ويحظر وضع نماذج بيانات تجارية فيه. موديول :core:database يدير محرك Room والتشفير بـ SQLCipher والترقيات Migrations. موديول :core:ui يوفر مكونات واجهة المستخدم التفاعلية العامة وأدوات الصور وتسهيلات الاستخدام. بينما تضم موديولات feature كافة تفاصيل رحلة المستخدم من شاشات وViewModels وUseCases ومستودعات وواجهات Retrofit الخاصة بتلك الميزة فقط.",
        "walkthrough_ar": """توزيع المسؤوليات البرمجية بين موديول الشبكة وموديول الميزة:
```kotlin
// في :core:network: مصنع Retrofit عام دون أي معرفة بالميزات
class CoreNetworkFactory @Inject constructor(private val okHttp: OkHttpClient) {
    fun <T> createService(serviceClass: Class<T>, baseUrl: String): T {
        return Retrofit.Builder().client(okHttp).baseUrl(baseUrl).build().create(serviceClass)
    }
}

// في :feature:orders: واجهة الـ API ونماذج البيانات الخاصة بالطلبات فقط
interface OrdersApi {
    @GET("/orders") suspend fun fetchOrders(): List<OrderDto>
}
```""",
        "why_it_matters_ar": "يمنع تلوث الموديولات الأساسية بالتفاصيل التجارية، مما يضمن بقاء موديولات core مستقرة ونادراً ما تحتاج لإعادة التجميع، ويحمي المشروع من كسر الـ Build Cache عند تعديل أي شاشة أو واجهة برمجية.",
        "worked_example_ar": "فصل واجهات API ونماذج JSON الخاصة بالمدفوعات من موديول `:core:network` ونقلها إلى داخل موديول `:feature:payment`، وملاحظة انخفاض زمن إعادة البناء عند تعديل واجهات الدفع بنسبة 80%.",
        "trade_offs_ar": "فصل البنية التحتية عن واجهات الميزات يتطلب كتابة كود إعداد وربط إضافي لكل ميزة عبر حقن التبعيات، ولكنه يمنح النظام استقراراً معمارياً ويمنع تحول موديولات core إلى عنق زجاجة.",
        "failure_modes_ar": "وضع نماذج الـ DTO وواجهات Retrofit الخاصة بكافة ميزات التطبيق داخل موديول :core:network، وخلط مكونات Compose الخاصة بالتصميم في موديول قاعدة البيانات، وتضمين منطق فحص الصلاحيات داخل core:ui.",
        "production_perspective_ar": "في كبرى التطبيقات، نطبق سياسة مراجعة صارمة تمنع إضافة أي كلاس يحمل اسماً تجارياً (مثل User, Order, Cart) داخل موديولات core، لضمان بقائها أدوات بنية تحتية برمجية نقية.",
        "how_to_answer_ar": "ابدأ ببيان القاعدة الذهبية: موديولات core خالية تماماً من منطق الأعمال التجاري، ثم فصل محتويات كل موديول (network للبنية التحتية، database للمحرك والتشفير، ui للأدوات العامة)، واختم بما يخص موديولات الميزات.",
        "talking_points_ar": "خطورة وضع نماذج DTO في core:network وتأثيرها على إعادة التجميع، الفرق بين core:ui و design-system، وكيف يمتلك موديول الميزة واجهاته البرمجية الخاصة.",
        "follow_ups_ar": "- **المحاور:** \"أين نضع نماذج البيانات المشتركة بين ميزتين مثل كائن User؟\"\n  **المرشح:** \"نضعها في موديول عقود مستقل مثل :core:model أو داخل موديول الـ API الخاص بميزة المستخدم :feature:user:api، وليس في core:network مطلقاً.\"\n\n- **المحاور:** \"ما هو الفرق الدقيق بين موديول :core:ui وموديول :core:designsystem؟\"\n  **المرشح:** \"موديول design-system يحوي السمات البصرية والألوان والأزرار الموحدة، بينما core:ui يوفر أدوات التفاعل مثل معالجة مساحات الشاشة Insets وحاويات السحب للتحديث.\"",
        "self_check_ar": "هل أكدت على خلو موديولات core من نماذج ومنطق الأعمال؟ وهل فرقت بدقة بين مسؤولية كل موديول من المذكورين في السؤال؟",
        "references_ar": f"- [Android Architecture: Core and Feature Modules](https://developer.android.com/topic/modularization/patterns) — التوثيق الرسمي لتنظيم موديولات البنية التحتية والميزات.\n- [Now in Android Core Module Boundaries](https://github.com/android/nowinandroid) — المعمارية المرجعية من جوجل لفصل موديولات core.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "توفر موديولات core بنية تحتية مجردة خالية تماماً من منطق الأعمال: core:network يدير عميل HTTP والتوكن وتثبيت الشهادات، core:database يدير محرك Room والتشفير، وcore:ui يوفر المكونات التفاعلية العامة. بينما تستأثر موديولات feature بكافة تفاصيل رحلات المستخدم من شاشات وViewModels وUseCases وواجهات API الخاصة بها.",
        "best_answer_ar": "الركيزة الأساسية في المعمارية متعددة الموديولات هي العزل التام بين أدوات البنية التحتية المجردة وبين المنطق التجاري الخاص بكل ميزة.\n\nيقتصر دور موديول core:network على توفير محركات الاتصال؛ فهو يجهز عميل OkHttpClient، ويدير آليات تجديد رموز التوثيق عبر Interceptors، ويطبق تثبيت الشهادات، دون أن يعرف أي تفصيلة عن روابط الخوادم أو نماذج بيانات المنتجات. وبالمثل، يدير موديول core:database قاعدة بيانات Room الأساسية والتشفير وتمرير الـ Migrations دون احتواء جداول تجارية خاصة بميزة معينة.\n\nأما موديول core:ui فيوفر الأدوات البصرية التفاعلية المشتركة مثل معالجة حواف الشاشة ومكتبات تحميل الصور، في حين تتركز السمات البصرية والألوان في موديول design-system. وتستقر موديولات feature في قمة هذا الهيكل لتمتلك كل منها شاشات Compose، ونماذج الـ ViewModels، ومنطق الـ UseCases، وواجهات استدعاء الخوادم الخاصة بها، مما يضمن بقاء موديولات core مستقرة ونادراً ما تحتاج لإعادة التجميع.",
        "deep_answer_ar": "في قيادة هندسة النظم البرمجية، نعتبر تسريب المعرفة التجارية إلى موديولات core خطأً معمارياً جسيماً يعطل كفاءة البناء التزايدي ويخلق اقتراناً مدمراً بين الميزات.\n\nعندما يضع الفريق واجهات Retrofit ونماذج DTO داخل موديول core:network، فإن تعديل حقل واحد في استجابة خادم السلة يجبر Gradle على إعادة تجميع موديول الشبكة، مما يبطل الـ Build Cache لكافة موديولات التطبيق المعتمدة عليه. لذلك نلزم موديول core:network بتوفير مصانع برمجية مجردة لعميل Retrofit، بينما يمتلك كل موديول ميزة واجهاته الخاصة ونماذج الـ JSON داخل طبقة البيانات الداخلية المحمية بـ internal.\n\nوينطبق هذا المبدأ بصرامة على طبقة التخزين؛ حيث يوفر core:database البنية التحتية لمحرك SQLite وتشفير SQLCipher، وتُحقن فيه جداول الميزات عبر تجميع الـ DAOs الموزعة. وفي طبقة الواجهات، يقتصر core:ui على الأدوات التقنية البحتة مثل مكتبات تحميل الصور ومعالجة قيود إمكانية الوصول، تاركاً الهوية البصرية لـ design-system.\n\nهذا التوزيع الهندسي الصارم يضمن أن موديولات البنية التحتية تمثل نهايات طرفية مستقرة في شجرة التبعيات نادراً ما تتغير، مما يحقق أعلى معدلات تجميع متوازي ممكنة للفرق المختلفة في بيئة الإنتاج. كما نضع قواعد برمجية مؤتمتة في مسارات الـ CI تفحص أسماء الكلاسات داخل موديولات core، وتمنع دمج أي تعديل يضيف كلاسات تجارية تتبع نطاق ميزة معينة، مما يحفظ نقاء البنية التحتية البرمجية واستقرارها الدائم."
    }
}

# ==========================================
# MOD-09: How should feature modules communicate without direct coupling?
# ==========================================
DATA["MOD-09"] = {
    "concept_en": """Direct dependencies between sibling feature modules violate horizontal architectural layering, generate circular dependency traps, and severely impair incremental build performance. To communicate without direct coupling, feature modules must employ decoupled interaction patterns:
1. API/Impl Separation Pattern: A feature is split into an exposed public :api module containing navigation contracts, interfaces, and minimal public models, and a private :impl module holding UI, ViewModels, and implementations. Feature A depends strictly on :feature:b:api.
2. Abstract Navigation Interfaces: Feature A declares an abstract navigation contract (e.g., CheckoutLauncher) that Feature B's implementation fulfills, wired together at the root :app level via Hilt dependency injection.
3. Deep Link Event Routing: Screens are launched via URI contracts (e.g., myapp://checkout?id=123) resolved dynamically by Android's navigation component or intent filters.
4. Reactive Domain Event Buses: Features communicate state updates asynchronously by emitting and observing shared Kotlin Flow events hosted in core domain contracts.""",
    "walkthrough_en": """Cross-feature communication via API contract interfaces and Hilt multibindings:
```kotlin
// 1. In :feature:checkout:api (Lightweight contract, no UI or ViewModels)
interface CheckoutNavigationContract {
    fun launchCheckout(context: Context, cartId: String)
}

// 2. In :feature:cart:impl (Needs to open checkout without importing its internals)
class CartViewModel @Inject constructor(
    private val checkoutNav: CheckoutNavigationContract
) : ViewModel() {
    fun onCheckoutClicked(context: Context, cartId: String) {
        checkoutNav.launchCheckout(context, cartId)
    }
}

// 3. In :feature:checkout:impl (Implements the contract)
class CheckoutNavigationImpl @Inject constructor() : CheckoutNavigationContract {
    override fun launchCheckout(context: Context, cartId: String) {
        context.startActivity(Intent(context, CheckoutActivity::class.java).putExtra("id", cartId))
    }
}

// 4. In :app (Wires interface to implementation via Hilt module)
@Module
@InstallIn(SingletonComponent::class)
abstract class NavigationWiringModule {
    @Binds abstract fun bindCheckoutNav(impl: CheckoutNavigationImpl): CheckoutNavigationContract
}
```""",
    "short_en": """Feature modules must never depend directly on sibling feature modules. They communicate through decoupled patterns: splitting features into public api contracts and private implementations; invoking abstract navigation interfaces wired by the app module via Hilt; routing destinations through deep link URIs; or observing reactive shared event flows managed in core domain contracts.""",
    "structured_en": """Direct coupling between feature modules is an architectural anti-pattern that creates circular dependencies and degrades build times.
To allow features to interact safely, we rely on decoupled architectural patterns.
The primary approach is the API and Implementation pattern.
Each feature is divided into a lightweight public api module that exposes only interfaces and contract models, and a private implementation module containing UI screens, ViewModels, and business logic.
When Feature A needs to interact with Feature B, it declares an implementation dependency strictly on Feature B's api module, keeping Feature B's implementation details encapsulated.
For navigation, Feature A invokes an abstract navigator interface.
The concrete implementation of that navigator is supplied by Feature B and wired together by the root app module using Hilt dependency injection.
For broadcast notifications, features emit domain events onto shared Kotlin Flow streams, allowing completely decoupled state updates across the app.""",
    "deep_senior_en": """In enterprise multi-module Android systems, horizontal feature-to-feature dependencies are strictly forbidden by architectural policy.
When :feature:cart imports :feature:checkout directly, any refactoring inside checkout's UI or ViewModel triggers a full recompilation of cart, invalidating the build cache and risking circular loops.
Our primary architectural solution is the API/Impl structural pattern.
Every vertical feature is bifurcated into two discrete Gradle subprojects: :feature:name:api and :feature:name:impl.
The :api module contains solely pure Kotlin interfaces, navigation routes, and immutable parcelable arguments.
It has zero dependencies on Android UI frameworks or sibling features, allowing it to compile in a fraction of a second.
When the cart feature needs to initiate checkout, it imports solely :feature:checkout:api.
The concrete implementation in :feature:checkout:impl is hidden behind Kotlin's internal visibility modifier.
The root app module acts as the mediator: it imports both :impl modules and uses Hilt to bind the interface to its concrete implementation.
At runtime, CartViewModel receives the navigator instance via constructor injection and executes navigation seamlessly.
For asynchronous state synchronization, such as clearing a shopping cart upon successful logout, we use reactive domain event streams.
An authentication feature emits a UserLoggedOutEvent onto a shared SharedFlow hosted in a core domain contract module, and independent feature repositories observe the stream without knowing which component initiated the event.""",
    "meta_ar": {
        "id": "MOD-09",
        "questionAr": "كيف تتواصل موديولات الميزات (Feature Modules) مع بعضها دون حدوث اقتران مباشر؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "تصميم أنماط التواصل المعماري بين الميزات المستقلة، وتطبيق نمط API/Impl، واستخدام الروابط العميقة ووسطاء الأحداث، وحقن التبعيات المعكوس.",
        "concept_ar": "يُحظر معمارياً وجود أي تبعية مباشرة بين موديولات الميزات الأفقية لأنها تؤدي للتبعيات الدائرية وبطء البناء التزايدي. يتم التواصل عبر أنماط معمارية غير مقترنة: نمط تقسيم الميزة إلى موديول عقود :api وموديول تنفيذ :impl، أو استخدام واجهات التنقل المجردة التي يربطها موديول app بحقن التبعيات بـ Hilt، أو استخدام الروابط العميقة Deep Links، أو بث الأحداث العامة عبر قنوات SharedFlow المشتركة.",
        "walkthrough_ar": """نمط التواصل بين موديولين عبر واجهة عقد برمجية وحقن التبعيات:
```kotlin
// في :feature:checkout:api
interface CheckoutNavigator {
    fun openCheckout(context: Context, orderId: String)
}

// في :feature:cart:impl: استدعاء الواجهة المجردة دون معرفة كود الشاشة
class CartViewModel @Inject constructor(
    private val navigator: CheckoutNavigator
) : ViewModel() {
    fun onCheckout(context: Context) = navigator.openCheckout(context, "123")
}

// في :feature:checkout:impl: تنفيذ الواجهة
class CheckoutNavigatorImpl @Inject constructor() : CheckoutNavigator {
    override fun openCheckout(context: Context, orderId: String) { /* فتح الشاشة */ }
}
```""",
        "why_it_matters_ar": "يحافظ على استقلالية الفرق وسرعة تجميع الموديولات، ويمنع النزاعات البرمجية، ويسمح بتعديل أو إعادة بناء أي ميزة داخلياً دون أن تتأثر الميزات الأخرى في المشروع.",
        "worked_example_ar": "بناء نظام تنقل يربط بين موديول `:feature:feed` وموديول `:feature:details` عبر واجهة `:feature:details:api` دون أن يستورد موديول feed أي كلاس من كلاسات كود شاشات details.",
        "trade_offs_ar": "تطبيق نمط API/Impl يضاعف عدد الموديولات ويتطلب كتابة واجهات إضافية وإعدادات ربط في موديول app، ولكنه يمنح المشروع عزلاً معمارياً مثالياً وسرعة بناء فائقة في المشاريع الكبيرة.",
        "failure_modes_ar": "استيراد موديول feature داخل feature آخر لتسهيل استدعاء دالة، واستخدام متغيرات عامة Global Singletons لمشاركة البيانات، والاعتماد المفرط على سلاسل نصوص الروابط العميقة دون تحقق من الأخطاء.",
        "production_perspective_ar": "في كبرى الشركات، نستخدم اختبارات Konsist الآلية في مسار الـ CI للتأكد من أن موديول :impl لا يمكن استيراده إلا بواسطة موديول app، بينما تستورد باقي الميزات موديولات :api فقط.",
        "how_to_answer_ar": "أكد على حظر الاعتماد المباشر بين الميزات، ثم اشرح نمط API/Impl بالتفصيل، ووضح دور Hilt وموديول app في ربط الواجهات، واختم بالحلول البديلة مثل الروابط العميقة وبث الأحداث بـ SharedFlow.",
        "talking_points_ar": "أهمية نمط API/Impl في عزل كود التنفيذ، دور Hilt في ربط الواجهات بالـ Composition Root، وكيفية مزامنة البيانات المشتركة عبر تدفقات الأحداث العامة.",
        "follow_ups_ar": "- **المحاور:** \"إذا احتجنا لمزامنة تسجيل الخروج عبر موديولات متعددة، كيف يتم ذلك؟\"\n  **المرشح:** \"نستخدم Event Flow مشترك في موديول دومين أساسي؛ موديول الحساب يبث حدث LogoutEvent، وتستمع موديولات السلة والإشعارات للحدث لتصفير بياناتها دون اقتران.\"\n\n- **المحاور:** \"ما هي ميزة الروابط العميقة Deep Links في التواصل بين الميزات؟\"\n  **المرشح:** \"تفك الاقتران البرمجي تماماً وتصلح للتنقل عبر الميزات الديناميكية والإشعارات الخارجية، ولكنها تفقدنا التحقق الصارم من صحة البيانات وقت التجميع Compile-time Safety.\"",
        "self_check_ar": "هل أكدت على حظر التبعيات الأفقية المباشرة بين الميزات؟ وهل شرحت بوضوح نمط API/Impl ودور موديول app وحقن التبعيات؟",
        "references_ar": f"- [Android Modularization: Inter-feature Communication](https://developer.android.com/topic/modularization/patterns) — أنماط التواصل النظيف بين موديولات الميزات.\n- [Dagger and Hilt Multi-module Navigation](https://developer.android.com/training/dependency-injection/hilt-multi-module) — دليل حقن التبعيات عبر الموديولات المتعددة.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "يُحظر معمارياً اعتماد موديولات الميزات على بعضها مباشرة منعاً للتبعيات الدائرية. يتم التواصل عبر أنماط غير مقترنة: تقسيم الميزات إلى موديول api عام وموديول impl خاص، أو استخدام واجهات تنقل مجردة يربطها موديول app عبر Hilt، أو التنقل بالروابط العميقة Deep Links، أو بث ومراقبة الأحداث عبر قنوات SharedFlow مشتركة.",
        "best_answer_ar": "الاعتماد المباشر بين موديولات الميزات الأفقية هو خطأ معماري جسيم يدمر استقلالية الفرق ويعطل ميزة التجميع التزايدي في Gradle.\n\nلتحقيق تواصل آمن وفعال، نطبق نمط API/Implementation كحل أساسي في المنظومة؛ حيث تقسم كل ميزة إلى موديولين: موديول :api خفيف الوزن يحتوي فقط على واجهات التنقل والتعاقدات العامة ونماذج البيانات البسيطة، وموديول :impl خاص يحتوي على الشاشات والـ ViewModels ومنطق العمل. فعندما تحتاج ميزة السلة للتنقل إلى صفحة الدفع، فإنها تعتمد على موديول :feature:payment:api فقط.\n\nتستدعي السلة واجهة التنقل المجردة PaymentNavigator، بينما يتكفل موديول app الرئيسي بربط هذه الواجهة بكلاس التنفيذ الفعلي في موديول impl باستخدام حقن التبعيات بـ Hilt. وفي سيناريوهات أخرى تتطلب تحديث الحالة عبر التطبيق كإفراغ السلة عند تسجيل الخروج، نعتمد على بث الأحداث التفاعلية عبر SharedFlow داخل موديول مشترك، لتستقبل كافة الميزات التحديثات دون أي اقتران مباشر بينها.",
        "deep_answer_ar": "في قيادة معمارية النظم متعددة الفرق، نعتبر كبسلة الميزات وحظر التبعيات الأفقية قاعدة ذهبية تحمي المشروع من التآكل البرمجي مع اتساع نطاق العمل.\n\nعندما يعتمد موديول السلة على موديول الدفع مباشرة، فإن أي تعديل طفيف في شاشات Compose الخاصة بالدفع يجبر محرك البناء على إعادة تجميع السلة بالكامل، مما يضاعف أوقات التجميع في مسار CI. ومن خلال تطبيق نمط API/Impl، نضمن أن موديول الـ api فائق الصغر وخالٍ تماماً من كود الواجهات ومكتبات أندرويد الثقيلة، مما يجعله يُجمع في أجزاء من الثانية ويوفر استقراراً ثابتاً للموديولات المستهلكة.\n\nيعتمد موديول المستهلك على واجهة مجردة لا تفصح عن تفاصيل الشاشات، ويبقى كود الـ impl الداخلي محمياً بكلمة internal الخاصة بلغة كوتلن. ويعمل موديول app كمنسق مركزي يدمج التنفيذ عبر Hilt Multibindings، مما يحقق مبدأ عكس التبعيات Dependency Inversion بأعلى درجات النقاء الهندسي.\n\nأما في الحالات التي تتطلب تنسيقاً غير متزامن للحالة، كإشعار النظام بتغيير العملة أو تسجيل خروج المستخدم، فنبتعد تماماً عن استخدام متغيرات الكائنات الأحادية Singleton العامة، ونبني بدلاً منها قنوات بث أحداث تفاعلية عبر قنوات SharedFlow معزولة في موديول عقود دومين أساسي، مما يتيح لكافة الميزات التفاعل الفوري مع الأحداث الحيوية دون أن ترتبط بأي تفصيلة في الموديول المصدر."
    }
}

# ==========================================
# MOD-10: How do navigation contracts work across modules?
# ==========================================
DATA["MOD-10"] = {
    "concept_en": """In a decoupled multi-module architecture, Feature A cannot instantiate or reference screens in Feature B at compile time because direct dependencies are forbidden. A navigation contract establishes a decoupled communication protocol separating the route destination request from its visual rendering:
- Contract Definition: Feature B's public :api module (or a shared navigation module) defines an abstract navigation interface (e.g., interface ProfileNavigator) or a serializable destination route object (e.g., @Serializable data class ProfileRoute(val userId: String)).
- Contract Implementation: Feature B's private :impl module implements the destination, configuring the Composable screen, ViewModel injection, and argument unpacking.
- Composition Wiring: The root :app module (or a global NavHost coordinator) aggregates navigation graphs using Hilt multibindings (@IntoSet) or Compose navigation destinations, allowing seamless transitions without compile-time coupling.""",
    "walkthrough_en": """Type-safe cross-module navigation using Compose Navigation routes and contract interfaces:
```kotlin
// 1. In :feature:detail:api (Lightweight contract module)
@Serializable
data class DetailRoute(val itemId: String)

interface DetailEntry {
    fun registerGraph(navGraphBuilder: NavGraphBuilder, navController: NavHostController)
}

// 2. In :feature:detail:impl (Renders the Composable screen)
class DetailEntryImpl @Inject constructor() : DetailEntry {
    override fun registerGraph(navGraphBuilder: NavGraphBuilder, navController: NavHostController) {
        navGraphBuilder.composable<DetailRoute> { backStackEntry ->
            val route = backStackEntry.toRoute<DetailRoute>()
            DetailScreen(itemId = route.itemId, onBack = { navController.popBackStack() })
        }
    }
}

// 3. In :feature:feed:impl (Navigates using only the public route contract)
@Composable
fun FeedItem(item: FeedItem, navController: NavHostController) {
    Button(onClick = { navController.navigate(DetailRoute(item.id)) }) {
        Text("View Details")
    }
}
```""",
    "short_en": """Navigation contracts allow screens in one module to open destinations in another without direct compile-time coupling. The destination exposes a public interface contract or type-safe route object in an api module, while its implementation module provides the UI screen. The app module binds the graph together using Hilt multibindings or centralized NavHost registration.""",
    "structured_en": """Cross-module navigation requires navigating between screens whose modules cannot see each other at compile time.
A navigation contract solves this problem by separating the navigation request from the destination's implementation.
The destination feature creates a public api module that exposes either a navigation interface or a type-safe Compose route object.
Feature modules that need to trigger navigation depend strictly on this lightweight api module.
To navigate, the caller simply triggers the contract with required arguments, such as an item identifier.
Inside the destination feature's private implementation module, the Composable destination is registered with the NavGraphBuilder, handling argument extraction and ViewModel setup.
The root app module acts as the central coordinator, collecting navigation destination registrations using Hilt multibindings into a set and attaching them to the root NavHost.
This architecture preserves full type safety and modular isolation.""",
    "deep_senior_en": """Designing cross-module navigation in modern Android with Jetpack Compose requires bridging the tension between modular encapsulation and type-safe routing.
Historically, teams relied on URI-based deep links or reflection to open activities across modules, but these approaches lacked compile-time verification, leading to runtime crashes when argument keys changed.
Our modern production architecture leverages Compose Navigation with Kotlin serialization and contract multibindings.
When we build :feature:checkout, we split the feature into :api and :impl subprojects.
The :feature:checkout:api module contains a type-safe route declaration, such as @Serializable data class CheckoutRoute(val cartId: String), alongside an abstract interface NavigationEntry.
Because this contract resides in an independent, leaf-level API module, :feature:cart can import :feature:checkout:api and invoke navController.navigate(CheckoutRoute(cartId)) with total type safety, autocompletion, and zero compile-time awareness of CheckoutScreen or its ViewModels.
Inside :feature:checkout:impl, a concrete NavigationEntry implementation maps CheckoutRoute to its Composable screen, injects the ViewModel, and handles backstack pop actions.
To aggregate all destinations into the root NavHost without hardcoding feature classes in :app, we utilize Hilt multibindings.
Each implementation module contributes its NavigationEntry into a Set<NavigationEntry> via @IntoSet.
The root application iterates over this injected set to build the complete graph dynamically.
This design guarantees compile-time safety, completely prevents horizontal coupling, and scales gracefully across dozens of autonomous engineering squads.""",
    "meta_ar": {
        "id": "MOD-10",
        "questionAr": "كيف تعمل عقود التنقل (Navigation Contracts) عبر موديولات أندرويد المتعددة؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "بناء عقود تنقل مجردة ومستقلة عن مكتبات العرض، والمقارنة بين Jetpack Navigation و Safe Args والروابط العميقة وواجهات التنقل المجردة، وفصل تعريف المسار عن تنفيذه.",
        "concept_ar": "عقود التنقل (Navigation Contracts) هي بروتوكول تواصل معماري مجرد يتيح الانتقال بين شاشات تقع في موديولات مختلفة دون وجود تبعية برمجية مباشرة بينها. يقوم المفهوم على فصل طلب الانتقال عن تنفيذ الشاشة الفعلي؛ حيث يعلن موديول الوجهة في موديول الـ :api الخاص به عن كائن مسار نوعي (Type-Safe Route) أو واجهة تنقل مجردة، بينما يتولى موديول الـ :impl الخاص بالوجهة تنفيذ الشاشة وربطها برسم التنقل، ويقوم موديول app بتجميع كافة الوجهات في NavHost مركزي عبر Hilt Multibindings.",
        "walkthrough_ar": """بناء عقود التنقل الآمنة عبر موديولات متعددة باستخدام Compose Navigation:
```kotlin
// 1. في :feature:details:api: مسار الوجهة وعقد التسجيل
@Serializable data class DetailsRoute(val id: String)

interface DetailsNavEntry {
    fun register(builder: NavGraphBuilder, navController: NavHostController)
}

// 2. في :feature:details:impl: تنفيذ الشاشة وربط المسار
class DetailsNavEntryImpl @Inject constructor() : DetailsNavEntry {
    override fun register(builder: NavGraphBuilder, navController: NavHostController) {
        builder.composable<DetailsRoute> { entry ->
            val route = entry.toRoute<DetailsRoute>()
            DetailsScreen(id = route.id)
        }
    }
}

// 3. في :feature:home:impl: الانتقال بالاعتماد على عقد الـ API فقط
navController.navigate(DetailsRoute("item_99"))
```""",
        "why_it_matters_ar": "يحل معضلة الانتقال بين شاشات الموديولات المنفصلة مع الحفاظ على الأمان النوعي Type-Safety ومنع الأخطاء وقت التشغيل، ويحمي استقلالية الموديولات وعزل التبعيات في Gradle.",
        "worked_example_ar": "تنفيذ مسار تنقل من موديول المنتجات إلى موديول تفاصيل الشراء عبر مسار `@Serializable` موثق في موديول API، وتجميع وجهات الشاشات في شجرة NavHost عبر `@IntoSet` في Hilt.",
        "trade_offs_ar": "استخدام عقود التنقل المجردة يتطلب هيكلة مسارات Type-Safe وبناء واجهات تسجيل لكل شاشة، ولكنه يقضي تماماً على أخطاء الانهيار الناتجة عن نسيان المعاملات البرمجية مقارنة بالنصوص العشوائية للـ Deep Links.",
        "failure_modes_ar": "الاعتماد على أسماء الكلاسات النصية بالانعكاس البرمجي Reflection مما يسبب انهيارات عند تفعيل R8، وتمرير كائنات معقدة غير قابلة للتسلسل عبر المعاملات، واقتران الموديولات المباشر لاستدعاء الأنشطة.",
        "production_perspective_ar": "في التطبيقات الإنتاجية، نستخدم مكتبة Compose Navigation مع Kotlin Serialization لإجبار المطورين على كتابة مسارات نوعية آمنة يتم التحقق من صحة معاملاتها أثناء التجميع.",
        "how_to_answer_ar": "ابدأ ببيان التحدي المعماري: كيف تتنقل لشاشة لا تستطيع استيرادها وقت التجميع؟ ثم اشرح مبدأ فصل العقد في موديول API وتنفيذه في impl، واختم بدور Hilt Multibindings في التجميع المركزي.",
        "talking_points_ar": "مفهوم Type-Safe Compose Navigation عبر Kotlin Serialization، دور Hilt @IntoSet في تسجيل الوجهات ديناميكياً، ومخاطر استخدام الانعكاس والروابط النصية المبهمة.",
        "follow_ups_ar": "- **المحاور:** \"لماذا نفضل المسارات المعرفة بـ Kotlin Serialization على الروابط العميقة النصية داخل التطبيق؟\"\n  **المرشح:** \"لأن المترجم يتحقق من تطابق أنواع المعاملات وقت البناء Compile-time Safety، مما يمنع حدوث أخطاء Null Pointer عند نسيان تمرير بارامتر مطلوب.\"\n\n- **المحاور:** \"كيف يعلم موديول الـ app بكافة شاشات التطبيق دون كتابتها يدوياً واحدة تلو الأخرى؟\"\n  **المرشح:** \"نستخدم Hilt Multibindings؛ حيث يساهم كل موديول ميزة بواجهة تسجيل NavEntry داخل Set موحدة، فيقوم موديول الـ app بالمرور عليها وتسجيلها تلقائياً.\"",
        "self_check_ar": "هل شرحت فكرة فصل العقد عن التنفيذ؟ وهل بينت كيفية استخدام Kotlin Serialization ودور Hilt في تجميع الوجهات دون اقتران؟",
        "references_ar": f"- [Type-Safe Navigation in Jetpack Compose](https://developer.android.com/guide/navigation/design) — التوثيق الرسمي للتنقل الآمن نوعياً في أندرويد.\n- [Multi-module Navigation Architecture Patterns](https://developer.android.com/topic/modularization/patterns) — أنماط التنقل بين الموديولات المتعددة.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "عقود التنقل تسمح للشاشات بفتح وجهات في موديولات أخرى دون وجود تبعية برمجية مباشرة بينها. يتم الإعلان عن كائن المسار أو واجهة التنقل في موديول api خفيف، بينما ينفذ موديول impl الشاشة الفعلية، ويتولى موديول app ربط المخطط بالكامل في NavHost مركزي عبر Hilt Multibindings.",
        "best_answer_ar": "تعتبر عقود التنقل الحل المعماري المثالي لمعضلة الانتقال بين شاشات تقع في موديولات متباعدة ومحظور اعتمادها المتبادل.\n\nتعتمد هذه العقود على فصل طلب التنقل عن تفاصيل بناء الشاشة؛ حيث ينشئ موديول الوجهة كائن مسار نوعي باستخدام مكتبة Kotlin Serialization داخل موديول الـ :api العام الخاص به، مثل كائن DetailsRoute الذي يحمل المعرفات المطلوبة كبيانات غير قابلة للتعديل. وتقوم الموديولات الأخرى باستيراد هذا العقد الخفيف واستدعاء دالة navigate بكل أمان مع التحقق التام من صحة المعاملات وقت التجميع.\n\nوفي موديول الـ :impl الخاص بالوجهة، يتم تسجيل مسار الـ Composable وتجهيز الـ ViewModel واستخراج المعاملات. ويأتي دور موديول app كنقطة ربط مركزية؛ حيث نستخدم تقنية Hilt Multibindings عبر تعليمة IntoSet لتسجيل كافة واجهات التنقل الموزعة داخل مجموعة واحدة يتم حقنها في الـ NavHost الرئيسي، مما يتيح تجربة تنقل متكاملة دون أي اقتران مباشر بين الموديولات.",
        "deep_answer_ar": "في المعمارية الحديثة لتطبيقات أندرويد المستندة إلى Jetpack Compose، يمثل التنقل عبر الموديولات تحدياً كبيراً للموازنة بين حماية الكبسولة المعمارية وضمان الأمان النوعي Type-Safety في تمرير البيانات.\n\nفي الماضي، كانت الفرق تلجأ للروابط العميقة النصية أو الانعكاس البرمجي Reflection لفتح الشاشات، ولكن هذه الحلول كانت تفتقر للتحقق البرمجي وقت التجميع وتتسبب في انهيارات مفاجئة عند تغيير أسماء المفاتيح بعد تفعيل R8. واليوم نعتمد معمارية عقود التنقل النوعية بالتعاون مع موديولات API/Impl الموزعة.\n\nيتضمن موديول الـ api كائن مسار تسلسلي @Serializable يحدد بدقة أسماء وأنواع البيانات المطلوبة لفتح الشاشة، إلى جانب واجهة تجريدية لتسجيل الوجهة. هذا العزل يسمح لموديول المتجر باستدعاء شاشة تفاصيل المنتج عبر مسارها الرسمي وتمرير المعاملات بالاعتماد على عقد الـ api فائق الخفة، دون أي حاجة لرؤية كلاسات Compose أو ViewModels الخاصة بالشاشة.\n\nوفي المقابل المعماري، ينفذ موديول الـ impl واجهة التسجيل، ويربط كائن المسار بواجهة العرض واسترجاع البيانات من المستودعات. وتكتمل المنظومة في موديول app بحقن مجموعة Set من واجهات التسجيل الموزعة عبر Hilt Multibindings، مما يسمح ببناء شجرة التنقل تلقائياً عند إطلاق التطبيق. هذا التصميم يضمن مناعة كاملة ضد أخطاء المعاملات، ويحافظ على استقلالية الموديولات، ويمنح الفرق البرمجية مرونة قصوى في تطوير وإعادة هيكلة الشاشات دون المساس بباقي أجزاء النظام."
    }
}

# ==========================================
# MOD-11: How do you manage dependency injection across modules?
# ==========================================
DATA["MOD-11"] = {
    "concept_en": """Managing Dependency Injection (DI) across a multi-module Android project requires establishing clean component lifecycles and decoupling interface contracts from concrete implementations:
- Interface Contracts in API/Core: Public contracts and repository interfaces are declared in leaf-level API or core domain modules, completely decoupled from injection frameworks.
- Module Bindings: Feature implementation modules provide Hilt/Dagger modules (annotated with @Module @InstallIn(SingletonComponent::class) or ActivityRetainedComponent) that bind the concrete class to the interface via @Binds.
- Dynamic Features & EntryPoints: Because dynamic feature modules invert dependencies and cannot be processed by the standard monolithic Hilt component at compile time, they access dependencies on-demand via @EntryPoint interfaces resolved through EntryPoints.get(applicationContext, MyEntryPoint::class).
- Multibindings for Pluggable Architecture: Sets (@IntoSet) and maps (@IntoMap) allow independent modules to register navigation destinations, network interceptors, or background workers into the root application container without central coupling.""",
    "walkthrough_en": """Multi-module Hilt setup with interface binding and dynamic feature EntryPoints:
```kotlin
// 1. In :core:network (Interface contract)
interface TokenProvider {
    fun getAuthToken(): String?
}

// 2. In :feature:auth:impl (Implements and binds the contract)
class TokenProviderImpl @Inject constructor(private val sessionManager: SessionManager) : TokenProvider {
    override fun getAuthToken(): String? = sessionManager.token
}

@Module
@InstallIn(SingletonComponent::class)
abstract class AuthBindingModule {
    @Binds abstract fun bindTokenProvider(impl: TokenProviderImpl): TokenProvider
}

// 3. In :dynamic:feature (Consumes dependency via EntryPoint)
@EntryPoint
@InstallIn(SingletonComponent::class)
interface DynamicFeatureDependencies {
    fun tokenProvider(): TokenProvider
}

fun injectDynamicFeature(context: Context) {
    val deps = EntryPoints.get(context.applicationContext, DynamicFeatureDependencies::class.java)
    val token = deps.tokenProvider().getAuthToken()
}
```""",
    "short_en": """Managing multi-module dependency injection requires declaring interfaces in api modules and providing bindings in implementation modules. Hilt aggregates these modules into the root app component during compilation. Dynamic feature modules retrieve dependencies at runtime using EntryPoints, while multibindings allow features to contribute navigation entries or interceptors into root collections without tight coupling.""",
    "structured_en": """Managing dependency injection in a multi-module Android architecture demands clean decoupling between interface contracts and concrete implementations.
We declare interfaces and repository contracts inside leaf-level api or domain modules, keeping them free of Android-specific implementation logic.
Inside the private implementation module, we write the concrete classes annotated with Inject constructor, alongside Hilt modules that bind the interface to the implementation using Binds.
During compilation, Hilt aggregates these distributed modules into the root application component in the app module.
For dynamic feature modules that invert Gradle dependencies, standard compile-time component injection is impossible.
Instead, dynamic modules define EntryPoint interfaces and retrieve dependencies on-demand at runtime using EntryPoints.get from the application context.
Furthermore, multibindings allow feature modules to contribute elements into shared sets, such as interceptors or navigation graphs, enabling a pluggable architecture.""",
    "deep_senior_en": """In enterprise Android engineering, our dependency injection architecture mirrors the Directed Acyclic Graph of our Gradle subprojects.
When using Hilt and Dagger across dozens of modules, the greatest threat is leaky abstraction and circular dependency generation.
We prevent this by strictly separating where contracts are defined from where they are bound.
Interface contracts reside in leaf-level :api modules.
Concrete implementations live in :impl modules, utilizing constructor injection.
The Hilt binding module resides directly inside the :impl module, declaring an abstract Binds method installed in SingletonComponent.
Because Hilt uses bytecode manipulation and annotation processing to aggregate all installed modules into the root ApplicationComponent inside the :app module, :feature:cart never needs to know that TokenProvider is implemented by :feature:auth:impl; it simply injects the interface.
Dynamic delivery introduces a unique constraint: dynamic feature modules depend on :app rather than the reverse, preventing Hilt from compiling them into the root component.
To resolve this, dynamic features declare an EntryPoint interface specifying the required dependencies.
At runtime, the dynamic feature resolves the interface using EntryPoints.get passing the application context.
To extend capabilities further, we leverage Dagger Multibindings with IntoSet to construct pluggable architectures.
Feature modules contribute navigation routes or OkHttp interceptors into injected collections, allowing the core network or navigation coordinator to discover feature contributions without hardcoded dependencies in the root module.""",
    "meta_ar": {
        "id": "MOD-11",
        "questionAr": "كيف تدير حقن التبعيات (Dependency Injection) عبر الموديولات المتعددة في أندرويد؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "إدارة مكونات DI مثل Hilt و Dagger عبر حدود الموديولات، واستخدام Multibindings و EntryPoints، وفصل تعريف الواجهات عن تثبيت الكلاسات المنفذة في موديول app.",
        "concept_ar": "تتطلب إدارة حقن التبعيات عبر الموديولات المتعددة فصلاً دقيقاً بين أماكن تعريف العقود وأماكن ربط التنفيذ: تعلن الواجهات المجردة في موديولات الـ :api أو الدومين، وتوفر موديولات الـ :impl كلاسات التنفيذ الموثقة بـ @Inject، مع موديولات Hilt موثقة بـ @Binds و @InstallIn(SingletonComponent). يجمع Hilt كافة الموديولات الموزعة في الكائن الجذري لموديول app وقت البناء. وتستخدم موديولات Dynamic Features تقنية @EntryPoint لجلب التبعيات في وقت التشغيل، بينما تتيح Multibindings تجميع المساهمات في قوائم موحدة دون اقتران مركزي.",
        "walkthrough_ar": """إدارة التبعيات عبر حدود الموديولات ومعالجة الميزات الديناميكية بـ EntryPoint:
```kotlin
// في موديول :feature:payment:impl: ربط الواجهة بالتنفيذ
@Module
@InstallIn(SingletonComponent::class)
abstract class PaymentModule {
    @Binds abstract fun bindGateway(impl: StripeGatewayImpl): PaymentGateway
}

// في موديول Dynamic Feature: استخراج التبعيات عبر EntryPoint
@EntryPoint
@InstallIn(SingletonComponent::class)
interface FeatureDependencies {
    fun paymentGateway(): PaymentGateway
}

val gateway = EntryPoints.get(context.applicationContext, FeatureDependencies::class.java).paymentGateway()
```""",
        "why_it_matters_ar": "يمنع تشابك الموديولات البرمجية، ويسمح لموديول app بتجميع النظام تلقائياً دون كتابة كود ربط يدوي ضخم، ويوفر طريقة معيارية لتمرير التبعيات الأساسية للموديولات الديناميكية التي يتم تنزيلها لاحقاً.",
        "worked_example_ar": "بناء نظام إشعارات مرن يجمع معالجات الإشعارات الموزعة في مختلف الموديولات داخل Set موحدة عبر `@IntoSet` في Hilt، وتمريرها لموديول استقبال رسائل Firebase المركزي.",
        "trade_offs_ar": "استخدام Hilt عبر موديولات متعددة يزيد من زمن التجميع الأولي بسبب معالجة الرموز KSP/KAPT، ولكنه يمنح المشروع أماناً نوعياً صارماً وقت التجميع وحقناً تلقائياً يقضي على أخطاء الربط اليدوي.",
        "failure_modes_ar": "محاولة حقن موديول الـ app داخل موديولات الميزات مما يخلق حلقة دائرية فورية، وإهمال استخدام EntryPoints في الميزات الديناميكية مما يسبب انهيار التطبيق لعدم وجود التبعية، واستخدام كلاسات التنفيذ بدلاً من الواجهات.",
        "production_perspective_ar": "في المشروعات الضخمة، نستخدم KSP بدلاً من KAPT مع تفعيل التجميع التزايدي لـ Hilt، ونفصل الموديولات المعتمدة على الـ Singletons عن الموديولات قصيرة الأجل لتقليل استهلاك الذاكرة العشوائية.",
        "how_to_answer_ar": "اشرح آلية عمل Hilt في تجميع الموديولات الموزعة داخل SingletonComponent، ثم وضح كيفية التعامل مع الميزات الديناميكية عبر @EntryPoint، واختم بدور Multibindings في بناء أنظمة قابلة للتوسع الإضافي.",
        "talking_points_ar": "كيف يجمع Hilt الموديولات الموزعة، دور @EntryPoint في موديولات Dynamic Features، واستخدام @IntoSet و @IntoMap لبناء أنظمة ممتدة Plug-in Architecture.",
        "follow_ups_ar": "- **المحاور:** \"لماذا تعجز Hilt عن حقن التبعيات مباشرة داخل Dynamic Feature بالطريقة المعتادة؟\"\n  **المرشح:** \"لأن الميزة الديناميكية لا يعرفها موديول app وقت التجميع؛ لذلك لا يستطيع كود Hilt المولد في الأساس تضمين كلاسات الميزة، ونلجأ لـ EntryPoints لاستخراج التبعيات وقت التشغيل.\"\n\n- **المحاور:** \"ما هي الفائدة المعمارية لـ Dagger Multibindings في المشاريع الكبيرة؟\"\n  **المرشح:** \"تسمح لكل موديول ميزة بتسجيل أدواته (مثل معترضات الشبكة أو وجهات التنقل) في قائمة موحدة يحقنها موديول الأساس دون أن يمتلك تبعية مباشرة على تلك الموديولات.\"",
        "self_check_ar": "هل شرحت توزيع موديولات Hilt عبر الموديولات؟ وهل بينت دور EntryPoint في Dynamic Features وفكرة Multibindings؟",
        "references_ar": f"- [Hilt in Multi-module Apps](https://developer.android.com/training/dependency-injection/hilt-multi-module) — الدليل الرسمي لحقن التبعيات بـ Hilt عبر الموديولات المتعددة.\n- [Dagger Multibindings](https://dagger.dev/dev-guide/multibindings) — توثيق داجر الرسمي للمجموعات والخرائط المتعددة.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "تدار التبعيات عبر الموديولات بإعلان الواجهات في موديولات api وتوفير كلاسات التنفيذ وربطها بـ Binds في موديولات impl. يجمع Hilt هذه الموديولات الموزعة في الكائن الأساسي لموديول app أثناء البناء. وتستخدم الميزات الديناميكية تقنية EntryPoints لجلب التبعيات في وقت التشغيل، بينما تتيح Multibindings تسجيل المكونات في قوائم موحدة دون اقتران مركزي.",
        "best_answer_ar": "تعتمد إدارة حقن التبعيات في المشاريع متعددة الموديولات على الموازنة الدقيقة بين عزل التبعيات وتجميع الرسم البياني العام في Hilt.\n\nنعلن واجهات العقود المجردة وواجهات المستودعات داخل موديولات الـ :api أو الدومين، لتكون خفيفة وخالية من تفاصيل التنفيذ. وداخل موديول الـ :impl الخاص بالميزة، ننشئ كلاسات التنفيذ الموثقة بـ Inject، ونعرف موديول Hilt يربط الواجهة بالتنفيذ عبر دالة مجردة Binds ومثبتة في SingletonComponent. ويتكفل Hilt وقت التجميع بمسح كافة الموديولات وتوليد كود التجميع النهائي داخل موديول app دون الحاجة لربطها يدوياً.\n\nأما في موديولات الميزات الديناميكية التي تعكس اتجاه التبعيات، فيستحيل على Hilt توليد الكود مسبقاً لأن كلاسات الميزة غير مرئية للـ app؛ ونحل هذه المعضلة باستخدام واجهات EntryPoint، حيث تطلب الميزة التبعية ديناميكياً من سياق التطبيق في وقت التشغيل عبر دالة EntryPoints.get. كما نستفيد من تقنية Multibindings لتجميع المعترضات ومسارات التنقل تلقائياً دون كتابة استدعاءات صلبة في موديول التطبيق الرئيسي.",
        "deep_answer_ar": "في المعمارية واسعة النطاق لأنظمة أندرويد، يعكس هيكل حقن التبعيات بالكامل مخطط الـ DAG لمشروع Gradle لضمان استقرار البناء ومنع التداخل بين الفرق.\n\nالمبدأ الحاكم هو حظر تسريب كلاسات التنفيذ خارج حدود موديول impl الخاص بها؛ فالواجهات البرمجية كـ PaymentRepository تستقر في موديول :api مجرد، بينما يقبع التنفيذ الفعلي داخل :impl محصناً بمعدل الرؤية internal. وتقوم موديولات Hilt الفرعية داخل :impl بربط الواجهة بالتنفيذ وتثبيتها في المكون المناسب لدورة حياتها كـ ActivityRetainedComponent أو SingletonComponent. ويقوم مجمع Hilt في موديول app بتجميع كافة هذه الموديولات الموزعة لبناء كائن التطبيق الشامل ApplicationComponent.\n\nوعند التعامل مع Dynamic Feature Modules، نواجه معضلة معمارية ناتجة عن عكس اتجاه التبعيات؛ فالميزة الديناميكية تعتمد على موديول app وليس العكس، مما يمنع Hilt من معالجة كودها وقت التجميع الأساسي. ونحل هذا التحدي باستخدام نمط EntryPoint؛ حيث تعلن الميزة واجهة تتضمن التبعيات المطلوبة، وتقوم باستخراجها في وقت التشغيل من ApplicationContext عبر EntryPoints.get بكل سلاسة وأمان نوعي.\n\nوفوق ذلك، نعتمد على Dagger Multibindings عبر تعليمتي IntoSet و IntoMap لبناء منظومة برمجية قابلة للتوسع الذاتي Plug-in Architecture. يتيح ذلك لكل موديول ميزة المساهمة بمعترضات شبكة OkHttp أو مهام WorkManager في مصفوفة موحدة، فيقوم موديول الشبكة أو موديول التطبيق الرئيسي باستهلاكها دون امتلاك أي سطر تبعية مباشر على تلك الميزات، مما يحافظ على نقاء شجرة التبعيات ويضمن أعلى سرعة تجميع متوازية ممكنة."
    }
}

# ==========================================
# MOD-12: How do version catalogs and convention plugins reduce config duplication?
# ==========================================
DATA["MOD-12"] = {
    "concept_en": """In large multi-module Android codebases spanning dozens of modules, duplicating compiler options, SDK versions, and dependency declarations across individual build.gradle.kts files creates severe maintenance debt and configuration drift. Two complementary Gradle mechanisms resolve this:
- Gradle Version Catalogs (gradle/libs.versions.toml): Centralizes all dependency coordinates, plugin identifiers, and version declarations into a single declarative file. It generates type-safe, auto-completing accessors (e.g., libs.androidx.compose.ui, libs.plugins.android.library) across all build scripts, eliminating string-literal version duplication and easing mass library upgrades.
- Gradle Convention Plugins (via build-logic composite build): Reusable custom Gradle plugins that encapsulate shared build logic and architectural standards (e.g., configuring Android SDK levels, Java/Kotlin toolchains, Compose compiler flags, and code quality linters in one place). Feature modules apply single-line convention plugins instead of copy-pasting hundreds of lines of build setup.""",
    "walkthrough_en": """Centralizing build configurations with Version Catalogs and custom Convention Plugins:
```toml
# gradle/libs.versions.toml
[versions]
compose = "1.7.0"
compileSdk = "35"

[libraries]
compose-ui = { module = "androidx.compose.ui:ui", version.ref = "compose" }
```

```kotlin
// build-logic/convention/src/main/kotlin/AndroidFeatureConventionPlugin.kt
class AndroidFeatureConventionPlugin : Plugin<Project> {
    override fun apply(target: Project) = with(target) {
        with(pluginManager) {
            apply("com.android.library")
            apply("org.jetbrains.kotlin.android")
        }
        extensions.configure<LibraryExtension> {
            compileSdk = 35
            defaultConfig { minSdk = 26 }
        }
        dependencies {
            add("implementation", project(":core:designsystem"))
        }
    }
}

// In feature/checkout/build.gradle.kts: Clean two-line configuration!
plugins {
    id("company.android.feature")
}
```""",
    "short_en": """Version catalogs centralize all library versions and plugin IDs in a single declarative TOML file, generating type-safe accessors across the project. Convention plugins encapsulate repetitive build logic, SDK versions, and compiler flags in custom Gradle plugins inside a build-logic composite build, reducing module build scripts to concise, standardized declarations.""",
    "structured_en": """Managing build configurations across dozens of Gradle subprojects requires eliminating copy-pasted build scripts to prevent configuration drift.
Gradle Version Catalogs solve the dependency coordination problem.
By consolidating all dependency coordinates, plugin IDs, and version numbers into gradle/libs.versions.toml, the entire engineering team shares a single source of truth.
Gradle generates type-safe accessors like libs.retrofit, giving developers auto-completion and compile-time verification when adding dependencies.
Convention plugins solve the build logic duplication problem.
Using a composite build typically named build-logic, we author custom plugins that configure standard build conventions.
For instance, an AndroidFeatureConventionPlugin configures the Android library plugin, Kotlin toolchains, Compose compiler options, and baseline testing dependencies.
Individual feature modules apply this single convention plugin, reducing their build.gradle.kts files from fifty lines of boilerplate to a clean, declarative configuration.""",
    "deep_senior_en": """As Android codebases scale past thirty modules, build script divergence becomes a major engineering bottleneck.
Teams copy-paste build scripts, leading to inconsistent compileSdk versions, mismatched Kotlin compiler options, missing ProGuard configurations, and configuration cache invalidations.
We solve this systematically through the combination of Version Catalogs and Convention Plugins implemented via composite builds.
The Version Catalog in gradle/libs.versions.toml acts as our immutable dependency manifest.
It categorizes versions, libraries, and bundles, providing type-safe Kotlin DSL accessors that eliminate error-prone string literals and ensure atomic, synchronized upgrades of related libraries like Jetpack Compose or KotlinX Coroutines.
To eliminate build configuration duplication, we construct an independent build-logic project included via includeBuild in settings.gradle.kts.
Unlike the legacy buildSrc directory which invalidates the build cache for the entire project upon every single edit, a composite build operates as an isolated Gradle project with its own cache lifecycle.
Within build-logic, we author lightweight, composable convention plugins.
For example, company.android.library configures compileSdk, minSdk, JVM toolchains, and freeCompilerArgs; company.android.compose attaches the Compose compiler extension and standard UI test dependencies; and company.android.feature bundles both while injecting common :core modules.
Feature build.gradle.kts files become purely declarative, often requiring under ten lines of code.
This architecture guarantees absolute configuration consistency, simplifies enterprise-wide upgrades, and preserves maximum build caching performance across our continuous integration pipeline.""",
    "meta_ar": {
        "id": "MOD-12",
        "questionAr": "كيف تقلل كتالوجات الإصدارات (Version Catalogs) وإضافات الاتفاقيات (Convention Plugins) من تكرار إعدادات البناء؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "استخدام libs.versions.toml لإدارة إصدارات التبعيات مركزياً، وبناء Convention Plugins عبر buildSrc أو build-logic، وتوحيد إعدادات Kotlin و Android و Compose عبر مئات الموديولات.",
        "concept_ar": "يحل الجمع بين Version Catalogs و Convention Plugins معضلة تكرار إعدادات البناء وتشتت الإصدارات في المشاريع الكبيرة: يجمع ملف Version Catalog (libs.versions.toml) كافة إصدارات المكتبات والإضافات في ملف تصريحي موحد ينشئ مؤشرات وصول آمنة نوعياً (Type-safe Accessors) تدعم الإكمال التلقائي في الكود. بينما تجمع إضافات الاتفاقيات (Convention Plugins) المنفذة عبر composite build (build-logic) منطق إعدادات Gradle المشترك (مثل compileSdk و Java toolchain وإعدادات Compose وفحوصات الجودة) في إضافات مخصصة تطبقها الموديولات في سطر واحد.",
        "walkthrough_ar": """توحيد إصدارات المكتبات في TOML وبناء إضافة اتفاقية موحدة:
```toml
# gradle/libs.versions.toml
[versions]
kotlin = "2.0.21"
retrofit = "2.11.0"
[libraries]
retrofit-core = { module = "com.squareup.retrofit2:retrofit", version.ref = "retrofit" }
```

```kotlin
// build-logic/convention/src/main/kotlin/AndroidLibraryConventionPlugin.kt
class AndroidLibraryConventionPlugin : Plugin<Project> {
    override fun apply(target: Project) = with(target) {
        pluginManager.apply("com.android.library")
        pluginManager.apply("org.jetbrains.kotlin.android")
        extensions.configure<LibraryExtension> {
            compileSdk = 35
            defaultConfig.minSdk = 26
        }
    }
}
// في موديول الميزة: تطبيق الإضافة في سطر واحد دون تكرار!
plugins { id("company.android.library") }
```""",
        "why_it_matters_ar": "يقضي على التباين البرمجي بين الموديولات (Configuration Drift)، ويجعل ترقية المكتبات كـ Compose أو Kotlin تتم في سطر واحد للمشروع ككل، ويسرع إعداد الموديولات الجديدة ويقلل أخطاء ملفات البناء.",
        "worked_example_ar": "إنشاء إضافة `company.android.feature` توحد إعدادات Compose ومكتبات التصميم، وتطبيقها عبر 25 موديول ميزة، مما يختصر أكثر من 1000 سطر من أكواد Gradle المكررة في المشروع.",
        "trade_offs_ar": "إعداد بيئة build-logic يتطلب مهارة وخبرة متقدمة في كتابة إضافات Gradle المخصصة مقارنة بالنسخ اليدوي، ولكنه يوفر مئات الساعات في صيانة وترقية المشاريع الضخمة على المدى الطويل.",
        "failure_modes_ar": "استخدام مجلد buildSrc التقليدي الذي يبطل كاش البناء بالكامل للمشروع عند أي تعديل، وكتابة إضافات متضخمة تفرض تبعيات غير لازمة على موديولات بسيطة، وتجاوز استخدام الكتالوج المركزي بكتابة إصدارات صريحة.",
        "production_perspective_ar": "في الشركات الكبرى، نعتمد هيكل composite build باسم `build-logic` لضمان عزل دورة حياة إضافات البناء عن التطبيق، ونربط ملف libs.versions.toml بأدوات التحديث الآلي مثل Renovate Bot.",
        "how_to_answer_ar": "ابدأ ببيان مشكلة تكرار إعدادات البناء، ثم اشرح دور Version Catalogs في توحيد الإصدارات والوصول النوعي، وفصل كيف تختصر Convention Plugins في build-logic أكواد الإعداد، واختم بفوائد الصيانة.",
        "talking_points_ar": "الفارق بين composite build و buildSrc التقليدي، دور ملف libs.versions.toml في الأمان النوعي، وكيفية بناء إضافات قابلة للتركيب مثل LibraryPlugin و ComposePlugin.",
        "follow_ups_ar": "- **المحاور:** \"لماذا نفضل استخدام composite build (build-logic) بدلاً من مجلد buildSrc التقليدي؟\"\n  **المرشح:** \"تعديل أي سطر في buildSrc يبطل كاش Gradle لكامل المشروع ويعيد تجميعه من الصفر، بينما build-logic مدمج كـ Composite Build له دورة حياة معزولة لا تؤثر على باقي الكاش.\"\n\n- **المحاور:** \"ما هي الفائدة المباشرة للـ Version Catalog في مشاريع أندرويد؟\"\n  **المرشح:** \"توحيد الإصدارات في ملف واحد، توفير الإكمال التلقائي في Kotlin DSL، ومنع وجود إصدارات متضاربة لنفس المكتبة بين الموديولات المختلفة.\"",
        "self_check_ar": "هل شرحت كلاً من Version Catalog و Convention Plugins؟ وهل بينت ميزة استخدام build-logic كـ Composite Build وتأثيرهما على صيانة الكود؟",
        "references_ar": f"- [Gradle Version Catalogs](https://docs.gradle.org/current/userguide/platforms.html) — التوثيق الرسمي لجرادل لإدارة كتالوجات الإصدارات.\n- [Sharing Build Logic with Convention Plugins](https://developer.android.com/topic/modularization/patterns#convention-plugins) — دليل جوجل الرسمي لبناء Convention Plugins.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "توحد Version Catalogs إصدارات المكتبات والإضافات في ملف TOML مركزي ينشئ مؤشرات وصول آمنة نوعياً تدعم الإكمال التلقائي. بينما تجمع Convention Plugins إعدادات البناء المتكررة مثل إصدارات SDK وإعدادات المترجم في إضافات مخصصة داخل مجلد build-logic، مما يختصر ملفات بناء الموديولات إلى سطور تصريحية موجزة.",
        "best_answer_ar": "مع نمو المشروع لعشرات الموديولات، يصبح تكرار إعدادات البناء وإصدارات المكتبات في كل ملف build.gradle.kts كابوساً تشغيلياً يؤدي لتباين الإعدادات وصعوبة الترقية.\n\nنحل هذه المعضلة عبر أداتين متكاملتين في Gradle الحديث. الأداة الأولى هي Version Catalog عبر ملف libs.versions.toml؛ حيث نضع كافة مسارات المكتبات وأرقام إصداراتها في مكان واحد مركزي، ويقوم Gradle بتوليد كود كوتلن يوفر مؤشرات وصول آمنة نوعياً Type-safe Accessors تدعم الإكمال التلقائي وتمنع كتابة النصوص يدوياً.\n\nوالأداة الثانية هي إضافات الاتفاقيات Convention Plugins المبنية داخل مشروع فرعي مدمج باسم build-logic؛ حيث نبرمج إضافات مخصصة تجمع الإعدادات المتكررة مثل ضبط compileSdk وإعدادات لغة كوتلن وأدوات فحص الجودة. وتكتفي موديولات الميزات بتطبيق إضافة واحدة مثل company.android.feature، مما يختصر عشرات الأسطر من الكود المكرر ويضمن اتساق معايير البناء عبر مئات الموديولات بسهولة فائقة.",
        "deep_answer_ar": "في قيادة هندسة البنية التحتية لتطبيقات أندرويد الضخمة، نعتبر تشتت ملفات البناء خطراً تقنياً يهدد استقرار النظام ويعطل فاعلية الـ Build Cache للفرق البرمجية.\n\nتتكامل منظومة البناء الحديثة من خلال دمج ملف libs.versions.toml مع تقنية Composite Builds لبناء بنية تحتية مستقرة وقابلة للتوسع. يمثل ملف الكتالوج المصدر الوحيد للحقيقة لكافة التبعيات؛ حيث نجمع المكتبات المرتبطة في حزم Bundles متناسقة، مما يتيح لنا ترقية حزمة Jetpack Compose أو Coroutines بالكامل بتعديل سطر واحد في ملف الكتالوج دون الحاجة للبحث في مئات الملفات.\n\nولتوحيد منطق البناء، نتجنب تماماً استخدام مجلد buildSrc الكلاسيكي؛ نظراً لأن تعديل أي حرف داخله يبطل كاش البناء بالكامل ويعيد تجميع المشروع من الصفر. وبدلاً من ذلك، نعتمد على مشروع مدمج باسم build-logic عبر includeBuild داخل ملف settings.gradle.kts، مما يمنحه دورة حياة مستقلة تحافظ على كاش المشروع.\n\nوداخل build-logic، نصمم إضافات اتفاقيات مجزأة ومترابطة بذكاء: إضافة تضبط إعدادات الأندرويد الأساسية، وإضافة تدمج إعدادات مترجم Compose، وإضافة لموديولات الميزات توحد استيراد مكونات التصميم الأساسية. هذا النهج يقلص ملفات build.gradle.kts في موديولات الميزات إلى بضعة أسطر تصريحية واضحة، مما يقضي على الأخطاء البشرية ويضمن تطبيق معايير الأداء والأمان على كل موديول جديد من اللحظة الأولى. كما نحدث كتالوج الإصدارات بشكل دوري ومؤتمت، مما يحافظ على توافق كافة موديولات التطبيق مع أحدث تقنيات أندرويد المستقرة دون عناء الصيانة الفردية."
    }
}

# ==========================================
# MOD-13: When should a module depend on an interface versus a concrete type?
# ==========================================
DATA["MOD-13"] = {
    "concept_en": """The decision to depend on an interface versus a concrete type across module boundaries governs architectural coupling and build cache efficiency:
- Depend on an Interface when: Crossing team ownership or feature boundaries; depending on volatile business implementations that change frequently; abstracting external infrastructure like network APIs, databases, or payment gateways that require test doubles in unit tests; or breaking potential circular dependency loops. Housing the interface in an independent :api module decouples consumers from internal implementation changes, preserving the Application Binary Interface (ABI) boundary.
- Depend on a Concrete Type when: The type represents an immutable value object, domain entity, or pure data transfer model without behavioral logic; relying on completely stable, foundational platform utilities that are never mocked (e.g., Kotlin standard library collections, time primitives); or operating within the private internal boundary of a single module. Creating interfaces for trivial, stable data models introduces needless indirection without architectural benefit.""",
    "walkthrough_en": """Contrasting interface contracts with concrete data models across module boundaries:
```kotlin
// 1. DEPEND ON CONCRETE TYPE: Immutable domain entity (Stable, pure data)
// In :core:model
data class MonetaryAmount(val amountInCents: Long, val currencyCode: String)

// 2. DEPEND ON INTERFACE: Volatile business capability with external I/O
// In :feature:payment:api
interface PaymentProcessor {
    suspend fun executePayment(amount: MonetaryAmount): Result<PaymentConfirmation>
}

// 3. In :feature:checkout:impl: Consumes the interface and concrete model
class CheckoutViewModel @Inject constructor(
    private val processor: PaymentProcessor // Interface dependency allows mocking in tests
) : ViewModel() {
    fun pay(cents: Long) = viewModelScope.launch {
        processor.executePayment(MonetaryAmount(cents, "USD"))
    }
}
```""",
    "short_en": """A module should depend on an interface when crossing architectural boundaries, interacting with volatile implementations, or abstracting external systems like networks and databases that require mocking. It should depend on a concrete type when dealing with immutable domain entities, stable value models, or internal utilities within the same module.""",
    "structured_en": """Deciding whether to depend on an interface or a concrete type determines how changes ripple through your multi-module build graph.
You should depend on an interface whenever you are crossing architectural or organizational boundaries.
When a feature module needs to invoke capabilities from another feature, or interacts with external I/O systems like network clients and databases, relying on an interface is essential.
This decouples the caller from volatile implementation details and allows effortless substitution with test doubles during unit testing.
Conversely, you should depend directly on concrete types when dealing with immutable data structures, domain entities, and stable value objects.
A data class representing a user identifier or monetary amount contains no execution logic and rarely changes its structure.
Wrapping pure data models in interfaces adds pointless indirection without improving decoupling.""",
    "deep_senior_en": """From a systems compilation and testing perspective, the choice between interface and concrete dependencies directly affects build cache invalidation and unit test execution speed.
When module A depends on a concrete class in module B, any modification to module B's class—including changing private variables or refactoring internal methods—alters module B's bytecode.
This triggers recompilation of module A unless strict ABI firewalls are maintained.
By introducing an interface inside an independent :api module, module A depends on a stable contract that rarely changes.
Refactoring the concrete implementation inside module B leaves module A's compile classpath clean, allowing Gradle to mark module A's compileKotlin task as UP-TO-DATE and preserving the build cache.
Furthermore, depending on interfaces is mandatory for architectural decoupling: it allows unit tests to substitute mock implementations instantly without loading device runtimes or starting real HTTP servers.
However, dogmatically creating interfaces for every single class is an anti-pattern known as interface pollution.
Immutable data models, value objects, and domain entities should always remain concrete classes.
A data class MonetaryAmount has no hidden behavior, does not perform I/O, and does not require mocking.
We reserve interfaces for components with operational behavior, external side effects, or cross-boundary coordination, ensuring maximum architectural flexibility without unneeded structural bloat.""",
    "meta_ar": {
        "id": "MOD-13",
        "questionAr": "متى يجب أن يعتمد الموديول على واجهة برمجية (Interface) ومتى يعتمد على نوع ملموس (Concrete Type)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "تطبيق مبدأ عكس التبعيات في سياق تجميع Gradle، والتمييز بين الأنواع المستقرة وتفاصيل التنفيذ المتغيرة، وتأثير الاعتماد على التجميع التزايدي.",
        "concept_ar": "يحكم قرار الاعتماد على واجهة (Interface) مقابل نوع ملموس (Concrete Type) درجة الاقتران واستقرار كاش البناء: يعتمد الموديول على واجهة برمجية عند عبور حدود الميزات أو الفرق، وعند التعامل مع أنظمة متغيرة كالشبكات وقواعد البيانات وبوابات الدفع التي تتطلب استبدالها بنماذج وهمية (Mocks) في الاختبارات، أو لحماية كاش Gradle من إعادة التجميع. بينما يعتمد الموديول على كلاس ملموس (Concrete Type) عندما يكون الكائن نموذج بيانات خالص (Pure Data Class/Entity) غير قابل للتعديل ومستقر تماماً، أو أدوات أساسية ثابتة بلغة كوتلن، أو داخل الحدود الداخلية الخاصة بنفس الموديول.",
        "walkthrough_ar": """المفاضلة العملية بين واجهة السلوكيات ونماذج البيانات الملموسة:
```kotlin
// نوع ملموس: كيان بيانات دومين ثابت وخالٍ من المنطق البرمجي (في :core:model)
data class UserAccount(val id: String, val email: String)

// واجهة برمجية: سلوك تجاري متغير يتضمن استدعاءات شبكة وتخزين (في :feature:user:api)
interface UserRepository {
    suspend fun getAccount(id: String): Result<UserAccount>
}

// في المستهلك: الاعتماد على الواجهة للسلوك والنوع الملموس للبيانات
class AccountViewModel @Inject constructor(
    private val repository: UserRepository // واجهة لسهولة الاختبار والعزل
) { /* استخدام UserAccount كنوع ملموس */ }
```""",
        "why_it_matters_ar": "يمنع التجميع المتسلسل في Gradle عبر حماية حدود ABI، ويسهل كتابة اختبارات الـ Unit Tests عبر استبدال الواجهات ببدائل وهمية، ويمنع التعقيد الزائد الناتج عن إنشاء واجهات غير لازمة لنماذج البيانات البسيطة.",
        "worked_example_ar": "تحويل الاعتماد في موديول السلة من الكلاس الملموس `StripePaymentService` إلى الواجهة `PaymentService` المعرفة في موديول API، مما أتاح كتابة اختبارات وهمية سريعة وحماية موديول السلة من التغيرات الداخلية لكود الدفع.",
        "trade_offs_ar": "استخدام الواجهات يضيف طبقة تجريد وكود ربط إضافي ولكنه يمنح مرونة تامة في الاختبارات وتطوير الميزات، بينما الاعتماد على الأنواع الملموسة أسهل وأسرع في الكتابة ولكنه يخلق اقتراناً قد يعطل استقلالية الموديولات إذا أسيء استخدامه.",
        "failure_modes_ar": "الاعتماد المباشر على كلاسات المستودعات الملموسة في الشاشات مما يصعب اختبارها، والوقوع في فخ تلويث الكود بإنشاء Interface لكل Data Class بسيط دون أي داعٍ معماري.",
        "production_perspective_ar": "في المعمارية الحديثة، نلزم المطورين باعتماد الواجهات لكافة العمليات التي تتضمن عمليات إدخال وإخراج I/O أو تنقل بين الشاشات، بينما نعتمد الكلاسات الملموسة للكيانات وقيم الدومين الثابتة Value Objects.",
        "how_to_answer_ar": "قسم الإجابة لقسمين واضحين: متى نستخدم الواجهة (عبر حدود الميزات، العمليات المتغيرة، قابلية الاختبار)، ومتى نستخدم النوع الملموس (نماذج البيانات الثابتة، الأدوات المستقرة، داخل الموديول نفسه).",
        "talking_points_ar": "تأثير الواجهات على كاش التجميع التزايدي في Gradle، تجنب ظاهرة Interface Pollution لنماذج البيانات، وأهمية الواجهات في تسهيل اختبارات الـ Unit Tests.",
        "follow_ups_ar": "- **المحاور:** \"لماذا يُعد إنشاء واجهة لكائن مثل data class User خطأ معمارياً؟\"\n  **المرشح:** \"لأن كائن البيانات لا يحتوي على منطق عملي أو عمليات I/O؛ هو مجرد وعاء لحمل البيانات وثابت بطبعه، ولا يحتاج لاستبداله بـ Mock في الاختبارات.\"\n\n- **المحاور:** \"كيف تحمي الواجهة كاش التجميع في Gradle مقارنة بالكلاس الملموس؟\"\n  **المرشح:** \"إذا عدلت كود التنفيذ في الكلاس الملموس، يتغير الـ Bytecode للموديول؛ أما الواجهة فتظل ثابتة ولا يتغير توقيعها ABI، فيعتبر Gradle الموديول المستهلك UP-TO-DATE ويتخطى إعادة تجميعه.\"",
        "self_check_ar": "هل حددت بدقة متى نستخدم الواجهة ومتى نستخدم النوع الملموس؟ وهل ربطت الإجابة بقابلية الاختبار وسرعة تجميع Gradle وتجنب Interface Pollution؟",
        "references_ar": f"- [Interface Segregation and Dependency Inversion Principles](https://martinfowler.com/) — مبادئ التصميم المعماري واستخدام الواجهات.\n- [Android Architecture Best Practices](https://developer.android.com/topic/architecture) — إرشادات جوجل لتصميم طبقات البيانات والدومين.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "يعتمد الموديول على واجهة برمجية عند عبور حدود الميزات، أو التعامل مع عمليات متغيرة تتضمن شبكات وقواعد بيانات تتطلب استبدالها بـ Mocks في الاختبارات، ولحماية كاش تجميع Gradle. بينما يعتمد على نوع ملموس للكيانات ونماذج البيانات الثابتة Data Classes، والأدوات القياسية المستقرة، أو داخل الحدود الخاصة لنفس الموديول.",
        "best_answer_ar": "تحديد الاعتماد على واجهة أو نوع ملموس يعتمد على طبيعة الكائن وموقعه في مخطط المعمارية ومسار التجميع.\n\nنلزم الموديول بالاعتماد على واجهة برمجية Interface عند عبور الحدود المعمارية بين الميزات المختلفة؛ فعندما تحتاج ميزة لاستدعاء خدمة دفع أو جلب بيانات مستخدم، فإن الاعتماد على واجهة مجردة في موديول :api يحمي المستهلك من التغييرات الداخلية لكود التنفيذ، ويتيح استبدال الخدمة ببديل وهمي Mock بسهولة أثناء كتابة اختبارات الـ Unit Tests. كما يحمي هذا التجريد كاش بناء Gradle لأن بصمة الواجهة العامة ABI تظل ثابتة فلا يُعاد تجميع الموديولات المعتمدة عليها.\n\nفي المقابل، يجب الاعتماد مباشرة على الأنواع الملموسة Concrete Types للكيانات ونماذج البيانات النقية كـ Data Classes وكائنات القيمة Value Objects؛ فهذه الكائنات تمثل بيانات غير قابلة للتعديل وخالية من العمليات الخارجية، وإنشاء واجهات لها يعد تعقيداً هندسياً زائداً بلا أي عائد حقيقي على النظام.",
        "deep_answer_ar": "في التحليل الهندسي المتقدم، يحكم الاختيار بين الواجهات والأنواع الملموسة التوازن بين مرونة التغيير وكفاءة التجميع عبر الـ Build Cache.\n\nعندما يعتمد موديول الشاشة على كلاس ملموس لمستودع بيانات، فإن أي إعادة هيكلة داخلية للكود البرمجي للمستودع تغير البايت كود المجمع؛ مما يجبر Gradle على إعادة تجميع موديول الشاشة بالكامل وضياع وقت التطوير. ولكن عند عزل العقد داخل واجهة برمجية في موديول :api مستقل، فإن التعديلات في موديول التنفيذ :impl لا تمس السطح العام للواجهة ABI، فيتخطى Gradle إعادة تجميع المستهلكين ويحتفظ بحالة UP-TO-DATE في الكاش.\n\nكما تعد الواجهات ركيزة لا غنى عنها في اختبارات منطق الأعمال؛ فهي تسمح بحقن بيئات اختبار وهمية دون تشغيل محاكيات أو استدعاء خوادم حقيقية. ومع ذلك، نحذر من الوقوع في فخ التجريد المفرط Interface Pollution بإنشاء واجهات لنماذج البيانات البسيطة مثل data class UserInfo؛ فهذه الكائنات تمثل حالات ساكنة وخالية من العمليات التفاعلية.\n\nلذلك نقصر استخدام الواجهات على العمليات ذات السلوك المتغير وعمليات الدخل والخرج I/O وعقود التنقل بين الميزات، ونعتمد الكلاسات الملموسة للبيانات الصافية والأدوات الرياضية المستقرة، لضمان معمارية نقية وعملية في آن واحد. كما نوجه المطورين الجدد في الفريق عبر أدلة إرشادية توضح معايير التجريد الصحيحة، وتمنع الإفراط في إنشاء الواجهات الوهمية التي لا تخدم استقرار البناء أو أهداف الاختبارات الآلية."
    }
}

# ==========================================
# MOD-14: How do you avoid circular dependencies and giant core/common modules?
# ==========================================
DATA["MOD-14"] = {
    "concept_en": """Scalable multi-module architectures actively prevent two widespread architectural anti-patterns:
- Circular Dependencies: Where two or more modules depend on each other directly or transitively (A -> B -> C -> A), breaking Gradle's topological sort and halting builds. Prevention requires strictly unidirectional dependency flow, extracting shared API contracts into independent submodules, applying dependency inversion via Hilt, and enforcing architectural linters.
- Giant Core/Common Module: Where teams treat :core:common as an undisciplined dumping ground for unrelated utilities (auth, analytics, string formatters, image loaders). Because nearly all feature modules import common, any change invalidates the build cache project-wide, creating a disguised monolith. Prevention requires decomposing :core into highly cohesive, single-responsibility leaf modules (e.g., :core:dispatchers, :core:crypto, :core:designsystem) and strictly localizing feature-specific helpers within their respective domains.""",
    "walkthrough_en": """Decomposing a bloated core module and breaking circular loops via contract extraction:
```text
// ❌ ANTI-PATTERN: Giant core module that breaks build cache for all features
:core:common (contains: DateUtils, AuthTokenManager, PaymentModels, BarcodeScanner)

// ✅ PRODUCTION TOPOLOGY: Decomposed into single-responsibility leaf modules
:core/
  ├── dispatchers/       (CoroutineDispatchers, test dispatchers)
  ├── crypto/            (Keystore wrappers, encryption engines)
  ├── formatting/        (Currency and date formatters)
  └── designsystem/      (Compose theme, atomic UI components)

// Breaking a circular loop between :feature:profile and :feature:auth:
// :feature:profile depends on :feature:auth:api ONLY (Unidirectional flow)
// Neither module imports the other's internal implementation!
```""",
    "short_en": """To avoid circular dependencies, enforce strictly unidirectional dependency flows and decouple cross-feature interactions using independent api contract modules and Hilt. To prevent giant core:common modules, dismantle monolithic utilities into focused, single-responsibility leaf modules like core:crypto and core:dispatchers, keeping feature-specific helpers strictly inside their owning domains.""",
    "structured_en": """Preventing circular dependencies and monolithic core modules requires deliberate architectural boundaries and automated governance.
Circular dependencies occur when modules import each other either directly or transitively, creating an impossible loop that halts Gradle compilation.
We resolve cycles by extracting shared models and interfaces into an independent, leaf-level api module, allowing both original modules to depend downward without cyclic coupling.
The giant core:common module is another common architectural pitfall where unrelated utilities are aggregated together.
Because every feature depends on common, a minor edit triggers application-wide recompilation and invalidates the remote build cache.
To eliminate this problem, we enforce a strict single-responsibility rule, decomposing common into focused leaf modules such as core:dispatchers, core:network, and core:designsystem.
Utilities that are not genuinely domain-agnostic are rejected from core and localized within their respective feature modules.""",
    "deep_senior_en": """In enterprise Android development, unmonitored modular architectures naturally decay into circular loops and giant shared garbage modules unless actively governed.
The giant core:common anti-pattern is particularly destructive because it recreates monolith bottlenecks under the illusion of modularity.
When a single module holds database helpers, authentication tokens, image loading bindings, and string extensions, it sits at the foundation of the dependency tree.
Any trivial update to a string formatter invalidates the Gradle build cache for every downstream feature, destroying build performance across the company.
Our architectural policy decomposes shared infrastructure into highly cohesive, domain-agnostic leaf subprojects: :core:dispatchers, :core:database, :core:crypto, and :core:designsystem.
If a utility does not qualify as platform-level infrastructure—such as a formatOrderReference function—it is strictly confined inside its owning feature module.
To eradicate circular dependencies, we enforce unidirectional dependency layering: presentation depends on domain, data implements domain, and features communicate solely through isolated :api contracts wired via Hilt at the app level.
We enforce these structural invariants in our CI pipeline using automated Konsist tests that scan imports across all modules, immediately failing pull requests that attempt to introduce reverse dependency edges or instantiate monolithic shared modules. We also generate automated architectural diagrams during pull request builds, giving code reviewers instant visual feedback on any suspicious dependency edge additions before merging.""",
    "meta_ar": {
        "id": "MOD-14",
        "questionAr": "كيف تتجنب التبعيات الدائرية وموديولات core/common المتضخمة التي تتحول لمونوليث مقنع؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "استراتيجيات منع تضخم موديول Common عبر التقسيم الوظيفي الدقيق، وحوكمة التبعيات لمنع الحلقات، واستخدام اختبارات المعمارية المؤتمتة Konsist/ArchUnit.",
        "concept_ar": "تتطلب حماية المعمارية النمطية التصدي لظاهرتين مدمرتين: التبعيات الدائرية التي تشل تجميع Gradle وتمنع الترتيب الطوبولوجي، وموديول core:common المتضخم الذي يتحول لمونوليث مقنع يبطل كاش البناء لكامل المشروع عند أي تعديل. يكمن الحل في فرض تدفق أحادي الاتجاه للتبعيات، واستخراج واجهات العقود المجردة في موديولات :api مستقلة، وتفكيك موديول common إلى موديولات طرفية أحادية المسؤولية مثل :core:dispatchers و :core:crypto، وفرض اختبارات معمارية مؤتمتة بـ Konsist في مسار الـ CI.",
        "walkthrough_ar": """تفكيك موديول common المتضخم إلى موديولات طرفية نظيفة:
```text
// ❌ النمط السيئ: موديول common يحوي أدوات غير مترابطة
:core:common (يحوي: تشفير، شبكات، تنسيق عملات، مكونات واجهة، توكنز)

// ✅ النمط النظيف: موديولات طرفية أحادية المسؤولية
:core/
  ├── dispatchers/   (CoroutineDispatchers فقط)
  ├── crypto/        (أدوات Keystore والتشفير فقط)
  ├── formatting/    (تنسيق الأرقام والتواريخ)
  └── designsystem/  (الألوان والمكونات البصرية الموحدة)
```""",
        "why_it_matters_ar": "يحمي زمن البناء التزايدي والاستفادة من Build Cache من الانهيار، ويمنع النزاعات البرمجية المستمرة بين الفرق، ويضمن صمود النظام وقابليته للتوسع مع نمو حجم الكود.",
        "worked_example_ar": "تفكيك موديول `:core:common` في تطبيق مصرفي كبير إلى 4 موديولات طرفية محددة، واكتشاف حلقة دائرية بين الملف الشخصي والمدفوعات وحلها بنمط API/Impl.",
        "trade_offs_ar": "تفكيك common إلى موديولات دقيقة يزيد من عدد الموديولات في المشروع وزمن الـ Configuration قليلاً، ولكنه يحقق أقصى كفاءة للتجميع المتوازي ويمنع إعادة تجميع مئات الكلاسات دون داعٍ.",
        "failure_modes_ar": "السماح بإنشاء موديول عام دون وضع حوكمة واضحة لما يدخل فيه، ودمج موديولين معاً للهروب السريع من خطأ التبعية الدائرية بدلاً من فكها هندسياً، وإهمال فحص التبعيات في الـ CI.",
        "production_perspective_ar": "في كبرى المؤسسات، نلزم المطورين باختبارات معمارية آلية عبر Konsist تفحص شجرة التبعيات في كل Pull Request وتمنع استيراد أي كلاس يعكس الاتجاه الهرمي للطبقات.",
        "how_to_answer_ar": "ناقش الخطرين بالتوازي: خطر الدوائر الدائرية وحلها بنمط API وعكس التبعيات، وخطر موديول common المتضخم وحله بالتفكيك لموديولات طرفية دقيقة، واختم بالأتمتة عبر Konsist.",
        "talking_points_ar": "خطورة موديول Common على Build Cache، تفكيك البنية التحتية إلى Leaf Modules، ودور اختبارات المعمارية بـ Konsist في حماية الحدود البرمجية.",
        "follow_ups_ar": "- **المحاور:** \"إذا احتاجت ميزتان إلى دالة مساعدة عامة جداً، أين نضعها؟\"\n  **المرشح:** \"إذا كانت الدالة بنية تحتية عامة تماماً كتنسيق التاريخ، توضع في موديول متخصص كـ :core:formatting؛ أما إذا ارتبطت بمجال الأعمال فتستقر داخل موديول الميزة صاحبة الاختصاص.\"\n\n- **المحاور:** \"كيف تكتشف مبكراً أن موديولاً ما يتحول إلى مونوليث مقنع؟\"\n  **المرشح:** \"عندما تجد أن معظم موديولات التطبيق تعتمد عليه، وأن معظم التعديلات اليومية في المشروع تمس ملفات داخله مما يبطل الكاش لكافة المطورين باستمرار.\"",
        "self_check_ar": "هل شرحت مخاطر موديول common المتضخم وكيفية تفكيكه؟ وهل بينت أسباب وحلول التبعيات الدائرية ودور الاختبارات المعمارية المؤتمتة؟",
        "references_ar": f"- [Gradle Multi-Project Architecture](https://docs.gradle.org/current/userguide/multi_project_builds.html) — أفضل ممارسات جرادل لتنظيم المشاريع الكبيرة.\n- [Konsist: Architectural Linting for Kotlin](https://consist.lemonappdev.com/) — أداة فحص وحوكمة المعمارية البرمجية في كوتلن.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "لتجنب التبعيات الدائرية، نفرض تدفقاً أحادي الاتجاه للتبعيات ونفك ارتباط الميزات عبر موديولات عقود api مستقلة وحقن التبعيات. ولمنع تضخم موديول core:common، نفككه إلى موديولات طرفية أحادية المسؤولية مثل core:crypto و core:dispatchers، مع حصر الأدوات الخاصة بالميزات داخل نطاقاتها الأصلية وفرض اختبارات Konsist الآلية.",
        "best_answer_ar": "حماية المعمارية النمطية تتطلب مكافحة حاسمة لظاهرتين مدمرتين للأداء البرمجي: الحلقات الدائرية وموديولات common المتضخمة.\n\nتنشأ التبعيات الدائرية عندما يستورد موديولان بعضهما بشكل مباشر أو عبر موديولات وسيطة، مما يشل خوارزميات الترتيب في Gradle ويوقف البناء. ونعالج هذه المشكلة بتطبيق نمط API/Implementation؛ حيث تستخرج الواجهات المشتركة في موديول عقود مستقل يعتمد عليه الموديولان في اتجاه هابط نظيف دون أي حلقة دائرية.\n\nأما موديول core:common فهو الفخ الأكبر في المشاريع الكبيرة؛ حيث يتحول لسلة مهملات لكافة الأكواد غير المصنفة، مما يجعله مونوليثاً مقنعاً يبطل كاش البناء للتطبيق بالكامل عند تعديل سطر واحد بداخله. ولحل هذه الأزمة، نفكك موديول common إلى موديولات طرفية دقيقة أحادية المسؤولية مثل موديول التشفير وموديول الموزعات، مع حظر وضع أي دالة تحمل طابعاً تجارياً داخل موديولات core وفرض اختبارات معمارية بـ Konsist في مسار الـ CI لضمان استقرار النظام.",
        "deep_answer_ar": "في قيادة هندسة المنصات، نراقب شجرة التبعيات باستمرار لمنع التآكل الهيكلي الذي يحول الموديولات إلى شبكة معقدة من التبعيات الدائرية والموديولات المشتركة المتضخمة.\n\nيمثل موديول core:common الخطر الأكبر على إنتاجية المطورين؛ فعندما يستورد هذا الموديول كافة ميزات التطبيق، فإن أي تغيير طفيف في أداة معالجة نصوص يبطل الـ Build Cache للمشروع بأكمله، ويعيد تجميع مئات الكلاسات على مسار CI وعلى أجهزة كافة المهندسين في الشركة. لذلك نطبق سياسة معمارية حاسمة تمنع وجود موديول common عام، وتفكك البنية التحتية إلى موديولات طرفية عالية التماسك: :core:dispatchers للموزعات، و :core:crypto للتشفير، و :core:formatting للأدوات الحسابية العامة.\n\nوفي سياق منع الحلقات الدائرية، نفرض تدفقاً هرمياً أحادي الاتجاه؛ حيث تحظر التبعيات الأفقية بين الميزات، وتتواصل الميزات عبر واجهات مجردة في موديولات :api خفيفة الوزن يتم ربطها عبر Hilt في موديول app الرئيسي. كما نؤمن هذا الاستقرار ببرمجة اختبارات معمارية مؤتمتة عبر أداة Konsist داخل مسار الـ Pull Requests؛ حيث تفحص الاختبارات مسارات الاستيراد وتفشل البناء فوراً إذا حاول أي مهندس إضافة تبعية دائرية أو استيراد موديول محظور، مما يحافظ على نقاء المعمارية وسرعة التجميع التزايدي مهما تضخم حجم المشروع. كما ننتج رسومات بيانية آلية توضح شجرة التبعيات في كل مراجعة كود، مما يمنح الفريق التقني رؤية فورية لأي تعديل مشبوه على حدود الموديولات قبل اعتماده ودمجه في الفرع الرئيسي."
    }
}

# ==========================================
# Runner & Validation
# ==========================================
def validate_words():
    for qid, d in sorted(DATA.items()):
        short_w = len(d["short_en"].split())
        struct_w = len(d["structured_en"].split())
        deep_w = len(d["deep_senior_en"].split())
        assert 35 <= short_w <= 110, f"{qid} short_en {short_w} out of [35, 110]"
        assert 100 <= struct_w <= 280, f"{qid} struct_en {struct_w} out of [100, 280]"
        assert 200 <= deep_w <= 650, f"{qid} deep_en {deep_w} out of [200, 650]"

        q_ar_w = len(d["meta_ar"]["quick_answer_ar"].split())
        b_ar_w = len(d["meta_ar"]["best_answer_ar"].split())
        d_ar_w = len(d["meta_ar"]["deep_answer_ar"].split())
        assert 35 <= q_ar_w <= 110, f"{qid} quick_ar {q_ar_w} out of [35, 110]"
        assert 90 <= b_ar_w <= 280, f"{qid} best_ar {b_ar_w} out of [90, 280]"
        assert 180 <= d_ar_w <= 650, f"{qid} deep_ar {d_ar_w} out of [180, 650]"
        print(f"{qid}: en_s={short_w}, en_st={struct_w}, en_d={deep_w} | ar_q={q_ar_w}, ar_b={b_ar_w}, ar_d={d_ar_w}")
    print("Pre-validation word count checks passed! Updating canonical questions...")

def apply_elevations():
    validate_words()

    topic_meta = {}
    for qid, d in sorted(DATA.items()):
        ee.update_canonical_question(
            qid=qid,
            concept_en=d["concept_en"],
            walkthrough_en=d["walkthrough_en"],
            structured_en=d["structured_en"],
            deep_senior_en=d["deep_senior_en"],
            short_en=d["short_en"],
        )
        topic_meta[qid] = d["meta_ar"]

    ee.save_topic_metadata("mod_08_14", topic_meta)
    ee.merge_all_metadata()

    for qid in sorted(DATA.keys()):
        errs = ee.validate_question(qid)
        if errs:
            print(f"Errors in {qid}:")
            for er in errs:
                print(f"  ❌ {er}")
            sys.exit(1)

    print("\nAll 7 MOD questions (MOD-08 to MOD-14) successfully elevated and passed validation!\n")

if __name__ == "__main__":
    apply_elevations()
