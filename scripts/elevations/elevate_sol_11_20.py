#!/usr/bin/env python3
"""
Elevation script for SOL-11 to SOL-20 (SOLID Principles & OOP - Batch 2).
Complete bilingual parity, senior conversational spoken style, zero bullet points in spoken text.
"""

import sys
from pathlib import Path

# Add scripts/elevations to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts" / "elevations"))
import elevation_engine as ee

TOPIC_AR = ee.TOPIC_AR_NAMES["SOL"]
REVIEWED_DATE_AR = "تمت المراجعة في 17 أكتوبر 2026"

DATA = {}

# ==========================================
# SOL-11: How would you replace a giant BaseActivity with smaller composable behaviors?
# ==========================================
DATA["SOL-11"] = {
    "concept_en": """Replacing a bloated BaseActivity with smaller composable behaviors embodies the composition over inheritance principle and Interface Segregation. A monolithic BaseActivity acts as an anti-pattern God Class that accumulates analytics tracking, toolbar setup, permission handling, loading dialogs, network connectivity monitoring, and dependency injection ceremony. Instead of forcing every screen to inherit this heavy baggage, senior engineers decompose these orthogonal concerns into focused DefaultLifecycleObserver classes, ActivityResultContract delegates, custom view components, or Jetpack Compose composition wrappers.""",
    "walkthrough_en": """Decomposing a God BaseActivity into decoupled lifecycle observers and delegates:
```kotlin
// BAD ANTI-PATTERN: God BaseActivity forces all screens to inherit bloated baggage
abstract class GodBaseActivity : AppCompatActivity() {
    fun trackScreenView() { /* analytics */ }
    fun showLoadingDialog() { /* dialog */ }
    fun monitorNetwork() { /* broadcast receiver */ }
    fun requestCameraPermission() { /* permission logic */ }
}

// ARCHITECTURAL BEST PRACTICE: Standalone lifecycle-aware behavioral delegates
class AnalyticsTrackerDelegate(
    private val screenName: String,
    private val analytics: AnalyticsService
) : DefaultLifecycleObserver {
    override fun onResume(owner: LifecycleOwner) {
        analytics.trackScreen(screenName)
    }
}

class NetworkMonitorDelegate(
    private val context: Context,
    private val onConnectionChanged: (Boolean) -> Unit
) : DefaultLifecycleObserver {
    override fun onStart(owner: LifecycleOwner) { /* register network callback */ }
    override fun onStop(owner: LifecycleOwner) { /* unregister network callback */ }
}

// Clean Activity composed of only the behaviors it actually needs
class UserProfileActivity : AppCompatActivity() {
    private val analyticsTracker by lazy { AnalyticsTrackerDelegate("ProfileScreen", getAnalyticsService()) }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        lifecycle.addObserver(analyticsTracker)
        // Screen only subscribes to behaviors it genuinely requires
    }
}
```""",
    "short_en": """We replace a giant BaseActivity by decomposing its responsibilities into small, focused lifecycle observers and behavioral delegates. Instead of forcing all screens into an inheritance hierarchy with unwanted analytics, permission, and network boilerplate, we create dedicated classes implementing DefaultLifecycleObserver. Activities then plug in only the specific behaviors they require using lifecycle.addObserver or Kotlin class delegation, eliminating rigid coupling and making each capability independently testable on the JVM.""",
    "structured_en": """Eliminating a monolithic BaseActivity is a critical architectural milestone in modernizing Android codebases.
In legacy Android development, BaseActivity became the default repository for any reusable UI logic. Over time, it accumulated analytics trackers, permission request managers, network status observers, progress dialog helpers, and authentication checkers. This violated the Single Responsibility Principle and forced child screens into rigid inheritance coupling, often breaking Liskov Substitution when child activities had to override unwanted base methods with empty implementations.
To dismantle this anti-pattern, we categorize base behaviors and isolate each into a dedicated delegate.
First, lifecycle-bound operations like analytics screen tracking and sensor listeners are moved into classes implementing DefaultLifecycleObserver, registered explicitly via lifecycle.addObserver in the child activity.
Second, interactive workflows like camera permissions or file picking are migrated to Jetpack ActivityResultContracts injected or declared at the call site.
Third, UI chrome such as top app bars and loading indicators are encapsulated inside reusable Jetpack Compose layout containers or custom view components.
This compositional model ensures activities declare only the exact behaviors they need, keeping inheritance trees flat and modular.""",
    "deep_senior_en": """Under the hood, dismantling BaseActivity directly addresses classloader performance, Dalvik method dispatch overhead, and testability boundaries in modern Android runtime environments.
When a monolithic BaseActivity defines dozens of open methods and lifecycle overrides, every single derived Activity inherits an inflated virtual method table (v-table). The Android ART runtime must maintain these expanded dispatch tables in memory, increasing class verification time upon initial APK startup and reducing CPU cache locality during polymorphic dispatch.
Furthermore, BaseActivity creates a hidden coupling hazard in multi-module architectures. Because BaseActivity typically lives in a common core UI module, that module must import analytics SDKs, network connectivity managers, and authentication repositories. This pulls heavy infrastructure dependencies into the core module, forcing every feature module to recompile whenever an underlying tracking library updates.
By transitioning to standalone DefaultLifecycleObserver components, each delegate resides in its respective domain or feature module. A feature screen simply attaches the delegates it requires.
From a testing perspective, testing an Activity tied to BaseActivity requires launching an instrumentation test runner or Robolectric shadow environment to satisfy all inherited dependencies. With delegates, engineers write lightning-fast JVM unit tests verifying that the delegate accurately handles lifecycle callbacks without ever instantiating an Android Activity context, ensuring resilient continuous integration pipelines.""",
    "meta_ar": {
        "id": "SOL-11",
        "questionAr": "كيف تستبدل BaseActivity العملاق بسلوكيات قابلة للتركيب (Composable Behaviors) في أندرويد؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على تفكيك كلاسات BaseActivity المتضخمة، وتطبيق مبدأ التركيب بدلاً من الوراثة (Composition over Inheritance)، واستخدام DefaultLifecycleObserver وعقود النشاطات (ActivityResultContracts).",
        "why_it_matters_ar": "كلاسات BaseActivity المتضخمة تتحول إلى God Classes تجمع التحليلات والأذونات ومراقبة الشبكة، مما يجعل كود التطبيق شديد التشابك، ويبطئ سرعة البناء ويمنع كتابة اختبارات آلية خفيفة.",
        "worked_example_ar": "تفكيك BaseActivity إلى كلاسات LifecycleObserver:\n```kotlin\n// مفوض مستقل لتتبع الشاشات\nclass AnalyticsDelegate(val name: String) : DefaultLifecycleObserver {\n    override fun onResume(owner: LifecycleOwner) { track(name) }\n}\n// الشاشة تشترك فقط في السلوكيات التي تحتاجها\nclass ProfileActivity : AppCompatActivity() {\n    init { lifecycle.addObserver(AnalyticsDelegate(\"Profile\")) }\n}\n```",
        "trade_offs_ar": "يتطلب كتابة سطر لتسجيل المفوض في الشاشة بدلاً من وراثته آلياً، لكنه يقضي تماماً على تلوث الوراثة ويجعل كل ميزة مستقلة وقابلة للاختبار المنفصل.",
        "failure_modes_ar": "الاستمرار في إضافة دوال مساعدة لـ BaseActivity حتى يصبح كلاس من 2000 سطر يعتمد عليه كل شاشات التطبيق ويستحيل حذفه.",
        "production_perspective_ar": "في الفرق الكبيرة، نمنع إنشاء BaseActivity تماماً ونضع فحصاً في Lint أو Detekt، ونعتمد كلياً على Lifecycle Observers ومكونات Compose القابلة لإعادة الاستخدام.",
        "how_to_answer_ar": "اشرح عيوب BaseActivity كـ God Class يكسر مبادئ SOLID، ووضح خطوات التفكيك: استخدام DefaultLifecycleObserver لتتبع الشاشات ومراقبة الشبكة، واستخدام ActivityResultContracts للأذونات، واستخدام Compose Wrappers لواجهات التحميل والتولبار.",
        "talking_points_ar": "مبدأ Composition over Inheritance، واستخدام DefaultLifecycleObserver، وتأثير v-table على وقت تشغيل ART، وسرعة البناء في Gradle بعزل التبعيات.",
        "follow_ups_ar": "- **المحاور:** \"ماذا لو كان لدي كود مشترك يحتاجه 90% من الشاشات مثل شريط العنوان (Toolbar)؟\"\n  **المرشح:** \"في Compose بنعمل Composable Layout زي `AppScaffold` بيحتوي على الـ Toolbar ونمرر له المحتوى كـ Lambda، وفي الـ Views بنعمل Custom View أو Layout Include بدل ما نفرضه بالوراثة.\"\n\n- **المحاور:** \"كيف تؤثر إزالة BaseActivity على سهولة كتابة الـ Unit Tests؟\"\n  **المرشح:** \"المفوضات المستقلة بتعتمد على Interfaces ونقدر نختبرها بالكامل على الـ JVM مع LifecycleOwner وهمي بدون الحاجة لإنشاء Activity حقيقية أو استخدام محاكي بطيء.\"",
        "self_check_ar": "هل بينت عيوب الوراثة العميقة؟ هل شرحت استخدام DefaultLifecycleObserver؟ وهل دعمت إجابتك بأثر ذلك على الـ JVM وتصميم Compose؟",
        "references_ar": f"- [Android Lifecycle-aware Components](https://developer.android.com/topic/libraries/architecture/lifecycle) — التوثيق الرسمي لجوجل لمكونات دورة الحياة.\n- [Composition over Inheritance in Android](https://developer.android.com/topic/architecture) — إرشادات معمارية أندرويد الرسمية.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "بنستبدل كلاس الـ BaseActivity العملاق عن طريق تفكيك مسؤولياته لكائنات ومفوضات صغيرة متخصصة بتعتمد على مبدأ التركيب بدل الوراثة. السلوكيات المرتبطة بدورة الحياة زي تتبع التحليلات ومراقبة الإنترنت بنحولها لكلاسات بتنفذ `DefaultLifecycleObserver`، والأذونات بنحولها لـ `ActivityResultContracts`، وعناصر الواجهة المشتركة بنغلفها في دوال Compose أو Custom Views. بكده كل شاشة بتختار بدقة السلوكيات اللي محتاجاها بدون ما تشيل حمل كلاس عملاق مش بتاعها.",
        "best_answer_ar": "استبدال BaseActivity هو خطوة حاسمة لنقل معمارية التطبيق من الكود القديم المتشابك للتصميم الحديث القابل للتوسع.\n\nفي المشاريع القديمة، كان أي مبرمج محتاج ميزة مشتركة يروح يحطها في `BaseActivity`، فتجمع الكلاس ده كود التحليلات، ورسائل التحميل، وفحص صلاحيات الكاميرا، ومراقبة شبكة الواي فاي. النتيجة كانت ظهور God Class مرعب بيجبر كل شاشة في التطبيق تورث كود ملوش أي علاقة بشاشتها، وده كسر صريح لمبادئ SRP و Liskov.\n\nالحل الهندسي بيعتمد على تفكيك المسؤوليات إلى مفوضات مستقلة:\nالعمليات المعتمدة على دورة الحياة بنعزلها في كلاسات بتطبق `DefaultLifecycleObserver`، والشاشة بتسجل المفوض ده بساطة عبر `lifecycle.addObserver`.\nعمليات طلب الأذونات والتقاط الصور بننقلها بالكامل لـ `ActivityResultContracts` المعيارية من جيتباك.\nوعناصر الواجهة زي الـ Toolbars وحوارات الانتظار بنحولها لـ Reusable Composables زي `AppScaffold` بنلف بيها الشاشات.\n\nالنتيجة إننا بنحافظ على شجرة الوراثة مسطحة تماماً، وبنخلي كل سلوك معزولاً وقابلاً لإعادة الاستخدام والاختبار في أجزاء من الثانية على الـ JVM.",
        "deep_answer_ar": "تحت الكابوت، التخلص من BaseActivity بيحسن كفاءة بيئة تشغيل ART ومساحة الذاكرة وحدود الـ Compilation في Gradle بشكل جوهري.\n\nلما كلاس BaseActivity يكون فيه عشرات الدوال الافتراضية، كل كلاس مشتق منه بيضطر يحتفظ بجدول دوال افتراضية ضخم (v-table) في ذاكرة الـ Heap. ده بيبطئ عملية الـ Class Verification وقت تشغيل التطبيق أول مرة ويزيد من استهلاك الـ RAM. لما نستبدل الوراثة بالتركيب عبر مفوضات صغيرة، بنحافظ على صغر حجم جداول التوجيه وسرعة تنفيذ تعليمات الميثودز في معالج الجهاز.\n\nعلاوة على كده، وجود BaseActivity في موديول مشترك بيجبر الموديول ده إنه يستورد مكتبات الـ Analytics والـ Network ومكتبات واجهة المستخدم الثقيلة. ده بيدمر ميزة الـ Modularization؛ لأن أي تحديث في كود التحليلات هيجبر Gradle إنه يعيد بناء كل موديولات التطبيق المعتمدة على الكور. بينما لما تكون السلوكيات مفصولة في كلاسات `DefaultLifecycleObserver`، كل مفوض بيعيش في موديوله الخاص بتبعيات مستقلة تماماً.\n\nوعلى صعيد التيستنج، اختبار Activity وارثة من كلاس عملاق بيتطلب تشغيل محاكي أو مكتبة Robolectric عشان نوفر كل الاعتماديات الموروثة. لكن مع المفوضات المستقلة، بنقدر نختبر منطق المفوض لوحده على الـ JVM العادي بـ Mock Lifecycle بسيط، مما يضمن ثبات وسرعة خط أنابيب الـ CI/CD."
    }
}

# ==========================================
# SOL-12: How does strategy-based payment routing support OCP?
# ==========================================
DATA["SOL-12"] = {
    "concept_en": """Strategy-based payment routing supports the Open/Closed Principle (OCP) by encapsulating variable payment provider mechanics behind a stable, polymorphic contract. In transactional systems, business logic must adapt dynamically to diverse payment rails such as Google Pay, Stripe, PayPal, and local gateways without continually editing core checkout workflows. By defining a common PaymentStrategy interface and leveraging dependency injection multibindings, adding a new gateway becomes an entirely additive operation: developers write a new isolated strategy class and register it into the DI graph, keeping core orchestrator classes strictly closed to modification.""",
    "walkthrough_en": """Implementing an extensible payment routing architecture adhering to OCP:
```kotlin
// 1. Stable abstraction contract
interface PaymentStrategy {
    fun supports(method: PaymentMethod): Boolean
    suspend fun processPayment(amount: Long, payload: PaymentData): Result<TransactionReceipt>
}

// 2. Additive concrete payment rail implementations
class StripePaymentStrategy @Inject constructor(private val stripeClient: StripeClient) : PaymentStrategy {
    override fun supports(method: PaymentMethod) = method is PaymentMethod.CreditCard
    override suspend fun processPayment(amount: Long, payload: PaymentData): Result<TransactionReceipt> {
        return runCatching { stripeClient.charge(amount, payload.token) }
    }
}

class GooglePayStrategy @Inject constructor(private val gPayClient: GooglePayClient) : PaymentStrategy {
    override fun supports(method: PaymentMethod) = method is PaymentMethod.GooglePay
    override suspend fun processPayment(amount: Long, payload: PaymentData): Result<TransactionReceipt> {
        return runCatching { gPayClient.authorizeAndCapture(amount) }
    }
}

// 3. Routing orchestrator is strictly CLOSED to modification
class PaymentRouter @Inject constructor(
    private val strategies: Set<@JvmSuppressWildcards PaymentStrategy>
) {
    suspend fun routePayment(method: PaymentMethod, amount: Long, payload: PaymentData): Result<TransactionReceipt> {
        val strategy = strategies.firstOrNull { it.supports(method) }
            ?: return Result.failure(IllegalArgumentException("Unsupported payment rail: $method"))
        return strategy.processPayment(amount, payload)
    }
}
```""",
    "short_en": """Strategy-based payment routing upholds OCP by delegating transaction execution to polymorphic strategy classes conforming to a common interface. Instead of maintaining a central checkout class with growing when statements that require editing for every new payment method, the router receives a collection of strategies via dependency injection. Adding a new provider like Google Pay simply requires implementing the interface in a new class, leaving the orchestrator completely untouched and free from regression risks.""",
    "structured_en": """Using the Strategy pattern for payment routing is a quintessential textbook demonstration of the Open/Closed Principle in enterprise Android engineering.
In anti-pattern architectures, payment routing is implemented through a centralized checkout manager with a massive when expression. Every time business requirements introduce a new payment method or regional banking rail, engineers are forced to open the critical checkout class, add a new conditional branch, and modify existing code. This introduces high regression risk, invalidates past QA certification, and causes merge conflicts among feature teams.
To uphold OCP, the checkout mechanism is divided into an orchestrator and isolated strategies.
First, a PaymentStrategy interface defines the contract, requiring each strategy to declare which payment methods it supports and execute the transaction.
Second, each provider (Stripe, PayPal, Google Pay) is implemented as a self-contained strategy class encapsulating its specific SDK dependencies and error mapping.
Third, the orchestrating PaymentRouter injects a set of strategies using Dagger Multibindings (@IntoSet). At runtime, it iterates through the injected set to select and execute the appropriate strategy polymorphically.
When new payment methods arrive, engineers write a new strategy without altering a single line of existing routing logic.""",
    "deep_senior_en": """Under the hood, strategy-based payment routing replaces hardcoded compiler branch instructions (tableswitch or lookupswitch bytecodes) with dynamic polymorphic dispatch and set lookups.
In a large multi-module Gradle architecture, this pattern provides significant compilation avoidance benefits. If the central payment router directly imports Stripe, PayPal, and Google Pay SDKs, the payment feature module becomes coupled to massive external vendor dependencies. Upgrading the Stripe SDK triggers a complete recompilation of the checkout feature module and all its consumers.
By applying OCP with Dagger Multibindings, the core :feature:checkout module depends solely on the abstract PaymentStrategy interface. Each provider lives in its own isolated Gradle module: :payment:stripe, :payment:googlepay, and :payment:paypal.
These provider modules plug their strategies into the Dagger dependency graph via @Binds @IntoSet within their respective Hilt modules. The :feature:checkout module never compiles against the third-party payment SDKs, keeping incremental compilation times minimal and enabling parallel compilation across CI build nodes.
Furthermore, this architecture maximizes runtime safety and testing velocity. Unit testing the PaymentRouter requires only passing a simple mock or fake strategy into the set, verifying routing logic in milliseconds on the JVM without loading heavyweight merchant SDKs or native cryptography libraries. This design isolates transient vendor API breaking changes from affecting the core checkout pipeline, guaranteeing maximum transactional reliability.""",
    "meta_ar": {
        "id": "SOL-12",
        "questionAr": "كيف يدعم توجيه المدفوعات القائم على الاستراتيجية (Strategy-based Payment Routing) مبدأ OCP؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم مبدأ الفتح والإغلاق (OCP)، والقدرة على تطبيق نمط Strategy مع Dagger Multibindings لحقن الخدمات، وإدراك فوائد ذلك في عزل الموديولات وتسريع البناء ومنع الـ Regressions.",
        "why_it_matters_ar": "الاعتماد على جمل when المركزية في شاشات الدفع يجعل كود المعاملات المالية الحساس عرضة للأخطاء مع كل إضافة لبوابة دفع جديدة، ويجبر الفريق على إعادة اختبار النظام بالكامل.",
        "worked_example_ar": "توجيه المدفوعات بنمط Strategy و Hilt Multibindings:\n```kotlin\n// إنترفيس الاستراتيجية\ninterface PayStrategy { fun supports(m: Method): Boolean; suspend fun pay(amt: Long) }\n// الراوتر يستقبل مجموعة الاستراتيجيات ومغلق للتعديل تماماً\nclass PayRouter @Inject constructor(val list: Set<@JvmSuppressWildcards PayStrategy>) {\n    suspend fun route(m: Method, amt: Long) = list.first { it.supports(m) }.pay(amt)\n}\n```",
        "trade_offs_ar": "يتطلب إعداد Dagger Multibindings وإنشاء كلاسات متعددة، لكنه يمنح أماناً مالياً تاماً ويسمح بإضافة بوابات دفع جديدة في موديولات مستقلة بدون لمس الكود القديم.",
        "failure_modes_ar": "استخدام كتل when مركزية تفحص نوع الدفع وتستورد مكتبات Stripe و PayPal في نفس الكلاس، مما يجعل الكود معقداً ومعرضاً للانهيار.",
        "production_perspective_ar": "في تطبيقات التجارة الكبرى، نضع كل بوابة دفع في موديول Gradle منفصل، ونحقن الاستراتيجيات عبر `@IntoSet` في Hilt، مما يتيح تفعيل أو تعطيل بوابات الدفع حسب البلد بسهولة.",
        "how_to_answer_ar": "عرف المبدأ: الكود مفتوح للإضافة ومغلق للتعديل، واشرح عيوب كتل when في كلاسات الدفع، واعرض الحل بتعريف PaymentStrategy واستخدام Dagger Multibindings (@IntoSet)، ووضح كيف يتم إضافة بوابة جديدة بمجرد كتابة كلاس جديد دون لمس الراوتر.",
        "talking_points_ar": "مفهوم OCP، ونمط Strategy، وتقنية Dagger Multibindings (@IntoSet)، وتسريع Compilation Avoidance في Gradle بعزل مكتبات الـ SDKs.",
        "follow_ups_ar": "- **المحاور:** \"كيف يتعامل الراوتر إذا لم تكن هناك أي استراتيجية تدعم وسيلة الدفع المطلوبة؟\"\n  **المرشح:** \"الراوتر بيفحص الاستراتيجيات عبر `firstOrNull`، وإذا لم يجد أي تطابق بيرجع `Result.failure` مع استثناء صريح بنوع وسيلة الدفع غير المدعومة، بدون حدوث أي Crash.\"\n\n- **المحاور:** \"هل إضافة بوابة دفع جديدة تتطلب إعادة بناء موديول الشراء (Checkout Module)؟\"\n  **المرشح:** \"لا، لأن موديول الشراء بيعتمد فقط على الـ Interface النقي، والبوابة الجديدة بتعيش في موديولها المستقل، ويتم ربطها في موديول الـ App الرئيسي فقط.\"",
        "self_check_ar": "هل بينت كيف يمنع النمط تعديل الكود القديم؟ هل شرحت استخدام Dagger `@IntoSet`؟ وهل وضحت عزل موديولات الـ Gradle؟",
        "references_ar": f"- [Dagger Multibindings Documentation](https://dagger.dev/dev-guide/multibindings.html) — الدليل الرسمي لحقن المجموعات في داجر.\n- [Clean Architecture: Open-Closed Principle](https://blog.cleancoder.com/) — مقالات العم بوب حول معمارية OCP.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "توجيه المدفوعات بنمط Strategy بيحقق مبدأ OCP عن طريق عزل منطق كل بوابة دفع في كلاس مستقل بيطبق إنترفيس موحد `PaymentStrategy`. كلاس الراوتر بيستقبل مجموعة الاستراتيجيات دي تلقائياً عبر حقن التبعيات بـ Dagger Multibindings، وبيختار البوابة المناسبة في وقت التشغيل. لما نحتاج ندعم وسيلة دفع جديدة زي Google Pay، كل اللي بنعمله إننا بنكتب كلاس جديد يطبق الإنترفيس، بدون ما نعدل سطر واحد في كلاس الراوتر أو نعرض العمليات المالية القديمة لأي خطر.",
        "best_answer_ar": "توجيه المدفوعات بنمط الاستراتيجية هو النموذج المثالي لتطبيق مبدأ Open/Closed في الأنظمة المالية الحساسة.\n\nفي الكود السيئ، بيكون عندنا كلاس مركزي فيه دالة دفع جواها `when` بتفحص إذا كان الدفع كاش أو فيزا أو باي بال، وتستدعي مكتبة كل شركة مباشرة. المشكلة إن كل ما الشركة تقرر تضيف بوابة دفع جديدة زي ميزة أو Google Pay، المطور لازم يدخل يعدل في نفس الكلاس القديم المختبر، وده بيفتح الباب لأخطاء Regression كارثية ممكن توقف الدفع في التطبيق بالكامل.\n\nعشان نطبق OCP بامتياز، بنقسم المنظومة لجزأين:\nأولاً: عقد مجرد `PaymentStrategy` بيحدد دالة لمعرفة هل الاستراتيجية تدعم وسيلة الدفع دي ولا لأ، ودالة لتنفيذ عملية الدفع.\nثانياً: كل بوابة دفع (Stripe، PayPal، Apple Pay) بتعيش في كلاس مستقل تماماً بينفذ العقد ده.\nكلاس الراوتر الأساسي بيكون مغلق تماماً للتعديل، وبيستقبل الـ Strategies دي كمجموعة محقونة عبر Dagger Multibindings (`@IntoSet`).\n\nلما يطلب البيزنس إضافة وسيلة دفع جديدة، المهندس بيكتب كلاس جديد خالص ويربطه في الـ DI، وكود الراوتر القديم بيفضل شغال ومحمي بنسبة 100% بدون أي تعديل.",
        "deep_answer_ar": "تحت الكابوت، تحويل كود فحص الدفع من كتل `when` إلى نمط الاستراتيجية بيستبدل أوامر التفرع الثابتة في الـ Bytecode بتوجيه ديناميكي متعدد الأشكال (Polymorphic Dynamic Dispatch).\n\nفي المعمارية متعددة الموديولات في أندرويد، التصميم ده بيعطي دفعة هائلة لسرعة الـ Compilation في Gradle عبر ميزة الـ Compilation Avoidance. لو كلاس الدفع الرئيسي بيستورد مكتبات الـ SDKs الخاصة بـ Stripe و Google Pay مباشرة، أي تحديث في إصدار مكتبة Stripe هيجبر الكومبايلر إنه يعيد بناء موديول الشراء بالكامل وكل الشاشات التابعة له. بينما مع نمط الاستراتيجية، موديول الشراء `:feature:checkout` بيعتمد فقط على الـ Interface النقي، وكل بوابة دفع بتعيش في موديول Gradle مستقل بذاته.\n\nالموديولات المستقلة دي بتسجل استراتيجياتها في شجرة Dagger باستخدام `@Binds @IntoSet`، وموديول الشراء عمره ما بيشوف كود الـ SDKs الملموس وقت الـ Compile time، وده بيسمح لـ Gradle إنه يبني موديولات بوابات الدفع بالتوازي التام على سيرفرات الـ CI/CD.\n\nعلاوة على كده، الأمان والموثوقية بيتضاعفوا في الاختبارات؛ لأن اختبار كلاس الـ Router على الـ JVM مش محتاج تشغيل أي SDK حقيقي أو عمل تهيئة لبيئة التشفير المعقدة للشركات المالية، بل بنمرر مجرد Fake Strategy خفيف، وبنختبر سيناريوهات التوجيه والتعامل مع الأخطاء في أجزاء من الثانية."
    }
}

# ==========================================
# SOL-13: Why can creating an interface for every class make design worse?
# ==========================================
DATA["SOL-13"] = {
    "concept_en": """Creating an interface for every single concrete class—frequently referred to as the 'Interface-itis' or '1:1 Interface-to-Implementation' anti-pattern—degrades software architecture by adding needless indirection, cognitive friction, and maintenance overhead without providing genuine abstraction. While abstractions are essential at genuine architectural boundaries (such as isolating domain logic from external data sources), blindly pairing every simple utility, helper, or single-implementation service with an interface violates YAGNI (You Aren't Gonna Need It) and the KISS principle. In modern Kotlin, where classes can be easily faked or mocked directly on the JVM, unjustified interfaces pollute IDE navigation and create illusory flexibility.""",
    "walkthrough_en": """Contrasting unnecessary interface ceremony with pragmatic, clean concrete design:
```kotlin
// BAD ANTI-PATTERN: Speculative generality creating 1:1 Interface-to-Implementation bloat
interface UserProfileDateFormatter { // Only used in one place, has exactly one implementation
    fun formatJoinedDate(timestamp: Long): String
}

class UserProfileDateFormatterImpl @Inject constructor() : UserProfileDateFormatter {
    override fun formatJoinedDate(timestamp: Long): String = DateUtils.format(timestamp)
}

// ARCHITECTURAL BEST PRACTICE: Pragmatic concrete class without unnecessary abstraction
// Cohesive, pure, deterministic Kotlin class that is trivially testable on JVM without an interface!
class UserProfileDateFormatter @Inject constructor() {
    fun formatJoinedDate(timestamp: Long): String {
        return DateTimeFormatter.ISO_INSTANT.format(Instant.ofEpochMilli(timestamp))
    }
}

// Inject directly into callers: Zero navigation friction, zero boilerplate maintenance!
class UserProfileViewModel @Inject constructor(
    private val dateFormatter: UserProfileDateFormatter // Direct concrete dependency
) : ViewModel()
```""",
    "short_en": """Creating an interface for every class makes design worse because it introduces speculative generality, doubles the number of files, and adds cognitive friction without delivering architectural value. In modern Kotlin, you do not need an interface to write unit tests on the JVM. Unless a class represents a genuine architectural boundary, has multiple runtime implementations, or requires physical decoupling across Gradle modules, writing a direct, cohesive concrete class is far cleaner and adheres to YAGNI and KISS.""",
    "structured_en": """The dogmatic rule of creating an interface for every class is a legacy habit from early Java enterprise development that actively harms modern Android codebases.
When developers automatically create an interface alongside every single class (like UserDateFormatter and UserDateFormatterImpl), the codebase suffers from severe architectural bloat.
First, it creates cognitive tax and hurts developer ergonomics. When navigating code in Android Studio, clicking on a method call jumps to the interface definition rather than the actual execution logic, requiring an extra navigation step (Cmd+Option+B) every single time.
Second, it violates YAGNI (You Aren't Gonna Need It). In ninety percent of cases, that single implementation never acquires a second variant throughout the entire application lifecycle. The abstraction was purely speculative.
Third, the historical argument that interfaces were strictly necessary for unit testing is obsolete. Modern Kotlin testing tools like Mockk easily mock final classes, and pure domain classes can be instantiated directly in JVM tests without any mocks at all.
Senior engineers introduce interfaces purposefully: at module boundaries, for polymorphic strategies, or to decouple pure domain rules from volatile I/O infrastructure.""",
    "deep_senior_en": """Under the hood, widespread 1:1 interface-to-implementation bloat degrades compilation efficiency, increases DEX method count, and impairs runtime inline optimizations in the Android ART runtime.
Every interface declared in Kotlin generates its own .class bytecode file and corresponding DEX type descriptor entry. In large applications with thousands of classes, redundant interfaces inflate the total method references inside the DEX file, inching closer to multidex splitting limits and bloating the download APK size.
At runtime, invoking a method on an interface requires ART to execute an invoke-interface bytecode instruction rather than an invoke-virtual or invoke-direct instruction. While ART's Inline Cache (IC) mitigates interface call overhead for monomorphic call sites, invoke-interface still involves a slightly more complex runtime dispatch resolution table lookup compared to direct devirtualized calls.
Furthermore, redundant interfaces create high maintenance friction during rapid refactoring. If an engineer changes a method parameter type, they must update both the interface contract and the implementation class in tandem, doubling Git diff noise.
Staff engineers follow the Rule of Three: write clean, cohesive concrete classes first. Extract an interface only when a second genuine implementation emerges, or when physical decoupling across Gradle module boundaries is strictly mandated by Dependency Inversion. This pragmatic approach keeps codebases lean, understandable, and immediately navigable.""",
    "meta_ar": {
        "id": "SOL-13",
        "questionAr": "لماذا قد يؤدي إنشاء Interface لكل كلاس إلى جعل التصميم أسوأ في أندرويد؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "النضج الهندسي والقدرة على تجنب الإفراط في التجريد (Over-abstraction)، وفهم مبادئ YAGNI و KISS، وإدراك متى يكون الـ Interface واجباً معمارياً ومتى يكون مجرد بويلربليت يعطل العمل.",
        "why_it_matters_ar": "الالتزام الحرفي الأعمى بقاعدة 'إنترفيس لكل كلاس' يضاعف عدد ملفات المشروع، ويزيد الجهد الذهني في التصفح، ويخلق تجريدات وهمية لا يحتاجها التطبيق إطلاقاً.",
        "worked_example_ar": "المقارنة بين التجريد المفرط والكود النظيف المباشر:\n```kotlin\n// كود سيئ: إنترفيس وهمي لكلاس بسيط ملوش غير تنفيذ واحد\ninterface DateFormatter { fun fmt(t: Long): String }\nclass DateFormatterImpl : DateFormatter { ... }\n// كود نظيف: كلاس ملموس مباشر وسهل الاختبار على الـ JVM\nclass DateFormatter @Inject constructor() { fun fmt(t: Long) = ... }\n```",
        "trade_offs_ar": "الكلاس الملموس المباشر يوفر نصف عدد الملفات ويسهل التصفح الفوري في الـ IDE، بينما الـ Interface يجب تركه للحدود المعمارية الحقيقية فقط.",
        "failure_modes_ar": "إنشاء إنترفيس وتسميته بـ `Impl` لكل كلاس مساعد أو Repository بسيط لا يملك سوى تنفيذ واحد ولن يتغير أبداً.",
        "production_perspective_ar": "في المشروعات الكبيرة، نطبق قاعدة 'قاعدة الثلاثة' (Rule of Three)؛ نبدأ بكلاس ملموس نقي، ولا نستخرج Interface إلا عند ظهور تنفيذ حقيقي ثانٍ أو عند الحاجة لعزل موديول في Gradle.",
        "how_to_answer_ar": "وضح أن التجريد بدون داعٍ يكسر YAGNI و KISS، واشرح عيوب التصفح في Android Studio (القفز للإنترفيس بدل الكود)، ووضح أن كوتلن الحديثة ومكتبة Mockk تسمح باختبار الكلاسات الملموسة بسهولة على الـ JVM، وحدد الحالات الحقيقية التي تستدعي إنشاء Interface.",
        "talking_points_ar": "مفهوم Speculative Generality، ومبدأ YAGNI، وصعوبة التصفح (Cmd+B)، وتأثير invoke-interface على ART، وقاعدة Rule of Three في التصميم.",
        "follow_ups_ar": "- **المحاور:** \"أليس الـ Interface ضرورياً لعمل Mocking في الـ Unit Tests؟\"\n  **المرشح:** \"تاريخياً في جافا القديمة كان صحيحاً، لكن في كوتلن الحديثة أدوات زي Mockk تقدر تعمل Mock لـ final classes بسهولة، والأفضل من ده إن الكلاسات البسيطة تقدر تختبرها مباشرة بدون Mock أصلاً.\"\n\n- **المحاور:** \"متى يكون إنشاء الـ Interface إلزامياً معمارياً؟\"\n  **المرشح:** \"عند حدود الموديولات في Clean Architecture لعزل الـ Domain عن الـ Data، أو عند وجود عدة استراتيجيات في وقت التشغيل زي بوابات الدفع.\"",
        "self_check_ar": "هل وضحت الفارق بين التجريد المفيد والبويلربليت؟ هل ذكرت أثر ذلك على تصفح الكود وعدد الملفات؟ وهل بينت متى نستخدم الإنترفيس فعلياً؟",
        "references_ar": f"- [Refactoring: Speculative Generality by Martin Fowler](https://refactoring.guru/smells/speculative-generality) — شرح العيب البرمجي للتجريد المسبق.\n- [YAGNI Principle](https://martinfowler.com/bliki/Yagni.html) — مقال مارتن فاولر حول عدم بناء ما لا تحتاجه الآن.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "إنشاء إنترفيس لكل كلاس بدون داعٍ بيخلي التصميم أسوأ لأنه بيزود التعقيد الذهني، ويضاعف عدد ملفات المشروع، ويقع في فخ التجريد المسبق (Speculative Generality) اللي بيخالف مبادئ YAGNI و KISS. في كوتلن الحديثة، مش محتاج إنترفيس عشان تكتب Unit Test؛ الكلاس الملموس النقي تقدر تختبره مباشرة على الـ JVM. التجريد بيكون مفيد فقط عند الحدود المعمارية الحقيقية زي عزل موديول الدومين أو لما يكون عندك بالفعل أكثر من تنفيذ في وقت التشغيل.",
        "best_answer_ar": "عادة إنشاء إنترفيس وتسميته بـ `Impl` لكل كلاس هي عادة قديمة موروثة من بيئات جافا Enterprise القديمة، وللأسف بتضر مشروعات أندرويد الحديثة أكتر ما بتفيدها.\n\nالضرر الأول هو زيادة الحمل الذهني وتخريب تجربة تصفح الكود في Android Studio. لما تضغط `Cmd+B` على أي دالة عشان تفهم بتعمل إيه، الـ IDE بيوديك للـ Interface الفاضي، وتضطر تضغط اختصار تاني عشان تروح للتنفيذ الحقيقي، وده بيضيع تركيز المطورين عشرات المرات يومياً.\n\nالضرر الثاني هو انتهاك مبدأ YAGNI (You Aren't Gonna Need It). في أكثر من 90% من الحالات، الكلاس ده بيفضل طول عمر المشروع ملوش غير تنفيذ وحيد، فوجود الإنترفيس كان مجرد تكلفة صيانة مضاعفة بدون أي عائد حقيقي.\n\nالضرر الثالث هو إن الحجة التاريخية بإن الإنترفيس ضروري للاختبارات مبقتش صحيحة؛ في كوتلن، مكتبات زي Mockk بتعمل Mocking للكلاسات العادية بسهولة، والأنضج هندسياً إن الكلاسات الصغيرة والمساعدة زي الـ Formatters والـ Validators تكون كلاسات ملموسة نقية تختبرها مباشرة بمدخلات ومخرجات حقيقية.\n\nالمهندس المحترف بيطبق 'قاعدة الثلاثة' (Rule of Three): ابدأ بكلاس ملموس وبسيط، واعمل Interface فقط لما يظهر تنفيذ حقيقي ثانٍ، أو لما تحتاج تفصل حدود الموديولات في Clean Architecture عشان مبدأ قلب الاعتماديات.",
        "deep_answer_ar": "تحت الكابوت، ظاهرة الـ 1:1 Interface-to-Implementation بتؤثر سلباً على حجم ملف الـ DEX، وسرعة الـ Compilation، وكفاءة تنفيذ التعليمات في معالج أندرويد.\n\nكل إنترفيس بتعرفه في كوتلن بيولد ملف `.class` مستقل وبيحجز مساحة لتعريف النوع (Type Descriptor) وجداول الميثودز في ملف الـ DEX. في التطبيقات الضخمة، وجود آلاف الواجهات الوهمية بيستهلك الحد الأقصى للميثودز في الـ DEX ويقرب التطبيق من تقسيمات الـ Multidex بدون أي فائدة ويزيد من حجم الـ APK.\n\nوعلى مستوى بيئة تشغيل ART، استدعاء دالة من خلال إنترفيس بيولد تعليمة بايت كود `invoke-interface` بدلاً من `invoke-virtual` أو `invoke-direct`. ورغم إن محرك ART بيعمل تحسينات عبر الـ Inline Caching للكولسايتس الأحادية (Monomorphic Call Sites)، إلا إن `invoke-interface` بيتطلب فحصاً إضافياً في جداول التوجيه وقت التشغيل مقارنة بالاستدعاء المباشر للكلاس الملموس.\n\nعلاوة على كده، الواجهات غير المبررة بتصعب التعديلات السريعة (Refactoring)؛ لأن أي تغيير في نوع باراميتر بيتطلب تعديل ملفين والـ Git Diff بيكبر للضعف، وده بيزود احتمالات الـ Merge Conflicts بين أفراد الفريق.\n\nالمهندسون الكبار بيميزوا بوضوح بين التجريد المعماري المفروض لعزل طبقة الـ Domain عن الـ Framework، وبين البويلربليت غير المجدي اللي بيعقد الكود بلا داعٍ، وهذا التوازن البراغماتي هو ما يضمن استدامة وسرعة تسليم التطبيق بجودة استثنائية."
    }
}

# ==========================================
# SOL-14: How does Hilt support dependency wiring without automatically guaranteeing DIP?
# ==========================================
DATA["SOL-14"] = {
    "concept_en": """Hilt acts as a dependency injection framework that automates object graph creation and lifecycle scoping, but using Hilt does not inherently guarantee compliance with the Dependency Inversion Principle (DIP). DIP is an architectural principle mandating that high-level modules must depend on abstract contracts rather than concrete details. If an engineer uses Hilt's @Inject constructor to inject a concrete Room database entity or Retrofit API class directly into a ViewModel, Dependency Injection is operational, but Dependency Inversion is completely broken because the high-level presentation layer remains tightly coupled to infrastructure details.""",
    "walkthrough_en": """Contrasting Hilt wiring that violates DIP against Hilt wiring that fulfills DIP:
```kotlin
// SCENARIO 1: Hilt used, but Dependency Inversion Principle VIOLATED!
// ViewModel depends directly on concrete Room implementation detail
class BadUserViewModel @Inject constructor(
    private val localRoomDao: UserDaoImpl // Direct concrete class coupling! Violates DIP!
) : ViewModel()

// SCENARIO 2: Hilt used, and Dependency Inversion Principle FULFILLED!
// 1. High-level Domain module defines pure Kotlin contract
interface UserRepository {
    suspend fun fetchUserProfile(): Result<UserProfile>
}

// 2. Low-level Data module implements the contract
class UserRepositoryImpl @Inject constructor(
    private val localRoomDao: UserDaoImpl
) : UserRepository {
    override suspend fun fetchUserProfile() = runCatching { localRoomDao.getUser().toDomain() }
}

// 3. Hilt module binds the abstraction to implementation using @Binds
@Module
@InstallIn(SingletonComponent::class)
abstract class UserDomainModule {
    @Binds
    abstract fun bindUserRepository(impl: UserRepositoryImpl): UserRepository
}

// 4. ViewModel depends strictly on the Domain abstraction! Fulfills DIP!
class CleanUserViewModel @Inject constructor(
    private val repository: UserRepository // Abstract interface dependency
) : ViewModel()
```""",
    "short_en": """Hilt provides the plumbing for dependency injection by instantiating and passing dependencies via constructors, but it does not dictate architectural rules. If you use Hilt to inject concrete classes like RoomUserDao or OkHttpClient directly into a ViewModel, you are practicing dependency injection while completely violating the Dependency Inversion Principle. Fulfilling DIP requires defining abstract domain interfaces and using Hilt's @Binds or @Provides to deliver concrete implementations behind those abstractions.""",
    "structured_en": """Distinguishing Hilt's operational mechanics from the architectural goals of Dependency Inversion is a fundamental senior engineering skill.
Hilt is an automated tool implementing Inversion of Control. It eliminates manual object instantiation by generating factory boilerplate, managing component lifecycles, and injecting dependencies via @Inject constructors. However, Hilt is completely agnostic about whether the injected dependency is an interface or a concrete class.
When an engineer uses Hilt to inject a concrete Room database or Retrofit service directly into a ViewModel or UseCase, the system practices Dependency Injection, but it flatly violates the Dependency Inversion Principle.
In this flawed setup, high-level business logic is directly coupled to low-level SQLite annotations and HTTP networking drivers. Upgrading or swapping the database forces rewrites across the UI and presentation layer.
To achieve true DIP with Hilt, the dependency direction must be inverted.
The high-level Domain layer declares pure Kotlin repository interfaces.
The low-level Data layer implements those interfaces.
Finally, a Hilt @Module uses @Binds to map the interface to the concrete implementation. Hilt delivers the object, but the architecture satisfies DIP.""",
    "deep_senior_en": """Under the hood, failing to enforce DIP while using Hilt dismantles the compilation firewalls of multi-module Android architectures.
In a multi-module enterprise project, Gradle modules should enforce architectural layers: :feature depends on :domain, and :data depends on :domain. The :domain module remains pure Kotlin with zero Android framework or database dependencies.
When engineers bypass DIP and inject concrete classes via Hilt, the :feature module must declare a direct Gradle dependency on the :data module (implementation(project(":data"))). This exposes Room database DAOs, SQLite drivers, and Retrofit network response DTOs directly to the UI presentation layer.
Any internal change to a database column or an OkHttp interceptor invalidates Gradle's build cache for the :data module, triggering an unnecessary recompilation cascade across all dependent :feature modules and inflating build times.
When DIP is enforced, Hilt bindings are declared in the root :app assembly module or dedicated binding submodules. The :feature module compiles solely against the abstract interfaces in :domain, allowing Gradle's Compilation Avoidance to completely skip feature recompilation during data layer changes.
Furthermore, testing harnesses benefit enormously. Testing a ViewModel that injects a DIP-compliant interface requires zero reflection, zero Hilt test runners, and zero Mockk agents; a 5-line pure Kotlin fake repository provides deterministic, millisecond-fast JVM test execution.""",
    "meta_ar": {
        "id": "SOL-14",
        "questionAr": "كيف تدعم مكتبة Hilt توصيل التبعيات دون أن تضمن تلقائياً تحقيق مبدأ DIP؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على التمييز بين أداة حقن التبعيات (Hilt) والمبدأ المعماري لقلب الاعتماديات (DIP)، وفهم خطورة حقن الكلاسات الملموسة عبر حدود الموديولات، وكيفية استخدام `@Binds` لتحقيق العزل الحقيقي.",
        "why_it_matters_ar": "الاعتقاد بأن استخدام Hilt يعني تلقائياً تطبيق Clean Architecture يجعل المطورين يحقنون كلاسات Room و Retrofit مباشرة في الـ ViewModels، مما يدمر استقلالية منطق العمل ويمنع تشغيل اختبارات JVM سريعة.",
        "worked_example_ar": "تحقيق DIP باستخدام `@Binds` في Hilt:\n```kotlin\n// إنترفيس في موديول الدومين\ninterface UserRepo { suspend fun getUser(): User }\n// التنفيذ في موديول الداتا\nclass UserRepoImpl @Inject constructor(val dao: RoomDao) : UserRepo\n// ربط التجريد بالتنفيذ في موديول Hilt\n@Module @InstallIn(SingletonComponent::class)\nabstract class RepoModule {\n    @Binds abstract fun bindRepo(impl: UserRepoImpl): UserRepo\n}\n```",
        "trade_offs_ar": "استخدام Hilt لحقن كلاسات ملموسة أسرع ولا يتطلب كتابة موديولات `@Binds`، لكن ربطه بالواجهات هو الوحيد الذي يحقق العزل المعماري وسرعة البناء في Gradle.",
        "failure_modes_ar": "حقن كلاسات قواعد البيانات أو عملاء الشبكة مباشرة في الـ ViewModels باستخدام `@Inject constructor` دون وجود أي واجهة تفصل بينهما.",
        "production_perspective_ar": "في المشروعات الكبيرة، نمنع موديول الـ `:feature` من رؤية موديول الـ `:data` في Gradle، ونلزم المطورين بحقن الواجهات المعرفة في موديول `:domain` حصرياً عبر Hilt.",
        "how_to_answer_ar": "وضح أن Hilt هو مجرد أداة وأتمتة (Mechanism) لتمرير التبعيات، بينما DIP هو مبدأ معماري استراتيجي (Architectural Principle)، واشرح كيف يمكن كتابة كود يستخدم Hilt لكنه يحقن كلاسات ملموسة فيكسر DIP، واعرض الحل بربط الواجهات عبر `@Binds` في Hilt Module.",
        "talking_points_ar": "الفرق بين الأداة والمبدأ المعماري، وسيناريو حقن كلاس ملموس عبر `@Inject`، ودور `@Binds` في Hilt، وأثر ذلك على استقلالية موديولات Gradle واختبارات الـ JVM.",
        "follow_ups_ar": "- **المحاور:** \"ما هو الفرق العملي بين `@Binds` و `@Provides` في Hilt عند تطبيق DIP؟\"\n  **المرشح:** \"`@Binds` بتستخدم لربط Interface بتنفيذ ملموس بدون توليد كود إضافي وميثودها بتكون Abstract، فداجر بيتعامل معاها بأعلى كفاءة، بينما `@Provides` بنستخدمها لما نحتاج نكتب كود تهيئة يدوي أو مكتبات طرف تالت.\"\n\n- **المحاور:** \"لو موديول الـ Feature اعتمد على موديول الـ Data مباشرة في Gradle، ما أثر ذلك على كاش البناء؟\"\n  **المرشح:** \"أي تغيير بسيط في جداول Room أو Retrofit هيلغي كاش موديول الداتا ويجبر Gradle يعيد بناء موديول الشاشة بالكامل، وده بيضيع وقت طويل جداً في الـ CI/CD.\"",
        "self_check_ar": "هل فرقت بوضوح بين Hilt كأداة و DIP كمبدأ؟ هل شرحت مثال كسر DIP مع وجود Hilt؟ وهل بينت دور `@Binds` في تحقيق العزل؟",
        "references_ar": f"- [Hilt Dependency Injection Guide](https://developer.android.com/training/dependency-injection/hilt-android) — دليل جوجل الرسمي لمكتبة Hilt.\n- [Dependency Inversion in Android Architecture](https://developer.android.com/topic/architecture) — دليل معمارية أندرويد الرسمية.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "مكتبة Hilt هي مجرد أداة لتوصيل وحقن التبعيات آلياً (Plumbing Mechanism)، لكنها مفيهاش ذكاء يضمن تطبيق مبدأ قلب الاعتماديات (DIP). لو استخدمت Hilt عشان تحقن كلاس ملموس زي `RoomUserDaoImpl` مباشرة في الـ ViewModel عبر الكونستركتور، أنت كده بتطبق نمط الـ DI بنجاح لكنك كاسر مبدأ الـ DIP تماماً لأن الشاشة معتمدة على تفاصيل قاعدة البيانات. عشان تحقق DIP مع Hilt، لازم الشاشة تعتمد على إنترفيس نظيف في الدومين، وتستخدم `@Binds` في موديول Hilt لربطه بالتنفيذ.",
        "best_answer_ar": "الفرق بين Hilt و DIP بيوضح النضج بين مجرد استخدام أدوات ومكتبات شائعة، وبين فهم المبادئ الهندسية الحاكمة للمعمارية.\n\nHilt هي أداة تشغيلية ممتازة لوظيفتها؛ بتبني شجرة الكائنات وتدير دورة حياتها وتمررها عبر الـ `@Inject constructor` عشان تريحك من كتابة الفاكتوري يدوياً. لكن Hilt محايدة تماماً ومبيهمهاش أنت بتحقن إيه.\n\nلو قمت بحقن كلاس ملموس لقاعدة بيانات Room أو كلاس عميل Retrofit مباشرة في الـ ViewModel؛ هنا Hilt اشتغلت بنجاح ووفرت الكائن، لكنك انتهكت مبدأ الـ DIP بنسبة 100%! لأن منطق الشاشة أصبح مربوطاً ومقيداً بمكتبات التخزين والشبكة، ولو حبيت تغير الداتابيز هتضطر تعدل في الشاشات، وهيستحيل عليك كتابة Unit Tests سريعة على الـ JVM بدون بيئة أندرويد.\n\nالتطبيق الحقيقي لمبدأ DIP مع Hilt بيتطلب تلات خطوات:\nأولاً: موديول الـ Domain يعرف Interface مجرد زي `UserRepository` بدون أي استيراد لمكتبات خارجية.\nثانياً: موديول الـ Data يحتوي على الكلاس الملموس `UserRepositoryImpl` اللي بينفذ الواجهة دي.\nثالثاً: نعمل موديول Hilt نستخدم فيه `@Binds` عشان نعلم Hilt إن لما أي ViewModel يطلب الإنترفيس ده، يمرر له التنفيذ الملموس.\n\nبكده بنستخدم قوة Hilt في التوصيل، وفي نفس الوقت بنحمي معمارية التطبيق بمبدأ قلب الاعتماديات.",
        "deep_answer_ar": "تحت الكابوت، الخلط بين توصيل Hilt ومبدأ DIP بيدمر تماماً حواجز العزل في المشاريع المقسمة لموديولات متعددة (Multi-module Gradle Architecture).\n\nفي المعمارية النظيفة الحقيقية، موديول الشاشة `:feature` بيعتمد على موديول الـ `:domain`، وموديول الـ `:data` بيعتمد برضه على الـ `:domain`. موديول الـ Domain بيعيش في عزلة تامة ككود كوتلن نقي بدون أي سطر من نظام أندرويد. لما المطورين يكسروا DIP ويحقنوا كلاسات ملموسة، بيضطر موديول الـ `:feature` إنه يضيف موديول الـ `:data` في ملف الـ `build.gradle` بتاعه (`implementation(project(\":data\"))`). الحركة دي بتكشف كل الـ DAOs والـ Entities الخاصة بـ Room وعملاء الشبكة داخل طبقة الواجهة، وده بيدمر كاش البناء في Gradle؛ لأن أي تعديل في سكيما قاعدة البيانات هيجبر Gradle إنه يعيد بناء موديول الشاشات وكل الميزات التابعة له.\n\nبينما لما نطبق DIP بحزم مع Hilt، بنعمل موديول الربط في الموديول التجميعي النهائي (`:app`). موديول الشاشة عمره ما بيشوف موديول الداتا في الـ Compile time، فميزة الـ Compilation Avoidance في Gradle بتشتغل بأقصى كفاءة وبتتخطى إعادة بناء الشاشات تماماً عند تعديل منطق حفظ البيانات.\n\nوفوق كده، اختبارات الـ Unit Tests للـ ViewModel بتتحول لعملية فائقة السرعة؛ لأن الشاشة معتمدة على الإنترفيس النقي، مش بنحتاج نشغل بيئة Hilt Test المعقدة ولا بنحتاج Mockito أو Robolectric، بل بنمرر كلاس Fake مكتوب في 5 سطور، وبيتم تشغيل مئات الاختبارات في ثوانٍ معدودة على الـ JVM العادي."
    }
}

# ==========================================
# SOL-15: How would you split a large interface with mostly unused methods?
# ==========================================
DATA["SOL-15"] = {
    "concept_en": """Splitting a bloated interface with mostly unused methods enforces the Interface Segregation Principle (ISP) and eliminates fragile client coupling. When an interface combines disparate operational concerns, it becomes a 'fat interface' that forces callers to implement or depend on methods they never invoke. To split it effectively, senior engineers analyze client usage patterns, partition the contract along natural actor and consumer boundaries into fine-grained role interfaces (frequently Single Abstract Method / SAM interfaces in Kotlin), and use interface inheritance, composite interfaces, or Kotlin class delegation (by) to preserve backward compatibility where unified access is legitimately required.""",
    "walkthrough_en": """Refactoring a fat media player interface into cohesive role interfaces:
```kotlin
// BAD ANTI-PATTERN: Fat interface violating ISP (Forces audio-only player to implement video methods)
interface MediaPlayerController {
    fun play()
    fun pause()
    fun seekTo(positionMs: Long)
    fun setVideoSurface(surface: Surface) // Video-only concern!
    fun adjustSubtitleTrack(trackId: Int) // Video-only concern!
    fun setPlaybackSpeed(speed: Float)
}

// ARCHITECTURAL BEST PRACTICE: Segregated role interfaces based on client capabilities
interface PlaybackControls {
    fun play()
    fun pause()
    fun seekTo(positionMs: Long)
}

interface SpeedAdjustable {
    fun setPlaybackSpeed(speed: Float)
}

interface VideoSurfaceController {
    fun setVideoSurface(surface: Surface)
    fun adjustSubtitleTrack(trackId: Int)
}

// Composite interface for clients that genuinely need full multimedia capabilities
interface FullVideoPlayerContract : PlaybackControls, SpeedAdjustable, VideoSurfaceController

// Concrete implementation satisfies granular interfaces cleanly
class ExoPlayerWrapper @Inject constructor() : FullVideoPlayerContract {
    override fun play() { /* ... */ }
    override fun pause() { /* ... */ }
    override fun seekTo(positionMs: Long) { /* ... */ }
    override fun setPlaybackSpeed(speed: Float) { /* ... */ }
    override fun setVideoSurface(surface: Surface) { /* ... */ }
    override fun adjustSubtitleTrack(trackId: Int) { /* ... */ }
}

// Audio-only notification widget depends strictly on minimal playback controls!
class AudioWidgetPresenter(private val controls: PlaybackControls) {
    fun onPlayClicked() = controls.play()
}
```""",
    "short_en": """We split a large interface by identifying cohesive groupings based on client consumption rather than implementation convenience. Following ISP, we break the monolith into focused role interfaces, such as separating a bloated media player into PlaybackControls, SpeedAdjustable, and VideoSurfaceController. Clients like audio widgets depend only on the playback controls they actually use. For callers needing all features, we provide a composite interface combining the smaller ones, maintaining clean decoupling and zero unused boilerplate.""",
    "structured_en": """Refactoring a bloated interface into client-centric role interfaces is a direct application of the Interface Segregation Principle.
When an interface accumulates too many methods, it becomes a fat interface. Callers requiring only a small subset of features are forced to depend on methods they never invoke. In Android, this leads to empty stub implementations, brittle test mocks, and unwanted recompilation cycles whenever unused method signatures change.
The refactoring process follows a disciplined three-step workflow.
First, perform client consumption analysis. Audit all existing consumers to map which methods each caller actually invokes. Natural cluster boundaries will emerge between read operations, write operations, administrative actions, or media types.
Second, extract fine-grained role interfaces matching these consumer clusters. In Kotlin, these often take the form of functional types, SAM interfaces, or small 2-to-3 method contracts like PlaybackControls and VideoSurfaceController.
Third, satisfy backward compatibility and full-featured implementations using composite interfaces and Kotlin class delegation. A full player class can implement multiple role interfaces simultaneously, while callers depend strictly on their dedicated slice of functionality.""",
    "deep_senior_en": """Under the hood, splitting fat interfaces preserves binary interface stability (ABI) and unlocks Gradle Compilation Avoidance in large-scale multi-module Android codebases.
When a module depends on a bloated interface, any modification to an uncalled method's signature alters the interface's public ABI bytecode. When Gradle compiles the project, its incremental analysis detects an ABI change in the upstream dependency, forcing the invalidation of compile caches and triggering a full recompilation of the consumer module even though the consumer's source code never referenced the altered method.
By decomposing the fat interface into granular role interfaces, the consumer module depends exclusively on its specific contract. Changes to unrelated methods remain isolated to their respective interfaces, allowing Gradle to completely skip recompilation of unaffected modules during continuous integration builds.
Furthermore, interface segregation dramatically simplifies test harness engineering. In unit tests for components depending on a fat interface, developers must create voluminous mock objects or stubs for dozens of methods to prevent NullPointerExceptions or unmet mock expectations.
With segregated role interfaces, test doubles require only implementing the one or two methods relevant to the test case, often represented as pure Kotlin lambdas, enabling clean, deterministic, and blazing-fast JVM test suites. This razor-thin contract segregation protects client modules from unrelated API refactoring across the repository.""",
    "meta_ar": {
        "id": "SOL-15",
        "questionAr": "كيف تُقسّم واجهة برمجية ضخمة (Large Interface) تحتوي على دوال غير مستخدمة لمعظم العملاء؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم مبدأ فصل الواجهات (ISP)، والقدرة على تحليل احتياجات العملاء (Client Consumption Analysis)، وتفكيك الواجهات المتضخمة إلى واجهات دورية (Role Interfaces)، واستخدام الواجهات المركبة وتفويض كوتلن.",
        "why_it_matters_ar": "الواجهات المتضخمة تجبر المطورين على كتابة دوال فارغة لا قيمة لها، وتكسر كاش الـ Gradle مع أي تعديل بسيط في دالة غير مستخدمة، وتجعل كتابة الـ Unit Tests كابوساً من إعداد الـ Mocks.",
        "worked_example_ar": "تفكيك واجهة مشغل وسائط ضخمة إلى واجهات متخصصة:\n```kotlin\n// تقسيم الواجهة لعقود صغيرة متخصصة\ninterface PlaybackControls { fun play(); fun pause() }\ninterface VideoControls { fun setSurface(s: Surface) }\n// واجهة مجمعة لمن يحتاج كل شيء\ninterface FullPlayer : PlaybackControls, VideoControls\n// ودجت الصوت يعتمد على التحكم في التشغيل فقط!\nclass AudioWidget(val controls: PlaybackControls)\n```",
        "trade_offs_ar": "يزيد من عدد ملفات الإنترفيسات في المشروع، لكنه يقضي تماماً على الدوال الفارغة، ويسرع وقت البناء، ويسهل كتابة التستات الخفيفة على الـ JVM.",
        "failure_modes_ar": "ترك الواجهة الضخمة كما هي وإجبار الشاشات على كتابة `override fun` بأجسام فارغة أو رمي أخطاء لتجاهل الدوال غير المطلوبة.",
        "production_perspective_ar": "في المشروعات الكبيرة، نصمم الواجهات وفق أسلوب Consumer-Driven Contracts؛ الشاشة هي التي تحدد الواجهة التي تحتاجها، ونجمع الواجهات عند التنفيذ باستخدام ميزة `by` في كوتلن.",
        "how_to_answer_ar": "اشرح خطوات التفكيك: أولاً تحليل استخدام العملاء وتحديد المجموعات الطبيعية للدوال، ثانياً استخراج Role Interfaces صغيرة ومحددة، ثالثاً توفير Composite Interface لمن يحتاج كل الوظائف، ورابعاً استخدام كوتلن delegation لتسهيل التنفيذ، مع توضيح أثر ذلك على كاش Gradle والاختبارات.",
        "talking_points_ar": "مبدأ ISP، وتحليل احتياجات العميل (Consumer-driven)، والواجهات المركبة (Composite Interfaces)، وميزة Compilation Avoidance في Gradle، وتبسيط الـ Mocks.",
        "follow_ups_ar": "- **المحاور:** \"كيف نحافظ على التوافق مع الكود القديم الذي كان يعتمد على الواجهة الضخمة؟\"\n  **المرشح:** \"بنعمل Composite Interface بترث من كل الواجهات الصغيرة الجديدة بنفس الاسم القديم؛ بكده الكود القديم يفضل شغال، بينما الكود الجديد بيعتمد على الواجهات الدقيقة فقط.\"\n\n- **المحاور:** \"كيف تساعد ميزة Interface Delegation في كوتلن عند تقسيم الواجهات؟\"\n  **المرشح:** \"بتسمح لكلاس المشغل يطبق الواجهات الصغيرة عن طريق تمرير كائنات منفصلة بكلمة `by` بدون ما يضطر يعيد كتابة وتوجيه كل دالة يدوياً (Zero boilerplate forwarding).\"",
        "self_check_ar": "هل وضحت خطوات تحليل العميل واستخراج الواجهات؟ هل ذكرت فكرة Composite Interface؟ وهل بينت الفائدة في Gradle واختبارات الـ JVM؟",
        "references_ar": f"- [Interface Segregation in Practice](https://blog.cleancoder.com/) — مقالات العم بوب حول تقسيم الواجهات.\n- [Kotlin Delegation Pattern](https://kotlinlang.org/docs/delegation.html) — التوثيق الرسمي لتفويض الكلاسات في كوتلن.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "بنقسم الواجهة الضخمة بتطبيق مبدأ فصل الواجهات (ISP) على تلات خطوات منظمة: أولاً بنعمل تحليل لاحتياجات العملاء (Client Consumption Analysis) عشان نعرف كل شاشة بتنادي إيه فعلياً. ثانياً بنفكك الواجهة لعقود صغيرة متخصصة بنسميها Role Interfaces زي فصل مشغل الوسائط لـ `PlaybackControls` و `VideoSurfaceController`. ثالثاً بنعمل Composite Interface يجمعهم مع بعض لخدمة الكلاسات اللي محتاجة المشغل الكامل، ونخلي كل شاشة تعتمد فقط وبدقة على الواجهة اللي محتاجاها.",
        "best_answer_ar": "تقسيم الواجهات المتضخمة هو علاج أساسي لمشكلة شائعة في المشروعات الكبيرة بنسميها الـ Fat Interfaces.\n\nالمشكلة بتبدأ لما إنترفيس زي مشغل الميديا يجمع دوال التشغيل والإيقاف مع دوال شاشات الفيديو وعرض الترجمة. لما يجي ودجت صوتي في شريط الإشعارات محتاج يشغل ويوقف بس، بيلاقي نفسه مجبر يكتب دوال فاضية للفيديو والترجمة، وأي تعديل مستقبلي في دوال الفيديو بيكسر كود الإشعار الصوتي!\n\nخطة التفكيك الهندسية بتتم كالآتي:\nأولاً: فحص الكود الحالي وحصر استخدامات الشاشات؛ بنكتشف إن الدوال بتنقسم بطبيعتها لمجموعات متجانسة: دوال تحكم في الصوت، ودوال شاشة الفيديو، ودوال سرعة التشغيل.\nثانياً: استخراج واجهات صغيرة ومحددة بنسميها Role Interfaces، زي `PlaybackControls` فيها دوال التشغيل الأساسية بس.\nثالثاً: بالنسبة للعملاء اللي محتاجين المشغل بالكامل، بنعمل Composite Interface بيرث من كل الواجهات الصغيرة معاً، وبنخلي الكلاس الملموس يطبقهم كلهم بسلاسة باستخدام ميزة تفويض الكلاسات `by` في كوتلن.\n\nبكده بنقضي على الأجسام الفارغة في الكود، وبنخلي كل شاشة معزولة تماماً ومحمية من أي تغييرات في ميزات مش مستخدماها.",
        "deep_answer_ar": "تحت الكابوت، تفكيك الواجهات الكبيرة بيحافظ على استقرار الـ Binary Interface (ABI) ويفعل ميزة الـ Compilation Avoidance في مشاريع Gradle متعددة الموديولات.\n\nلو موديول الإشعارات بيعتمد على Fat Interface موجود في موديول الوسائط، أي تعديل في توقيع دالة خاصة بالفيديو داخل الإنترفيس ده هيغير الـ ABI العام بتاع الموديول. ده بيجبر Gradle إنه يلغي كاش البناء ويعيد تجميع موديول الإشعارات بالكامل، رغم إن كوده لم يلمس دالة الفيديو نهائياً. لما نقسم الواجهة لعقود دقيقة ومستقلة، موديول الإشعارات بيعتمد على `PlaybackControls` فقط، والتعديلات في دوال الفيديو بتفضل معزولة، فـ Gradle بيتخطى إعادة بناء الموديولات غير المتأثرة وبيوفر وقت البناء في الـ CI/CD.\n\nبالإضافة لكده، تقسيم الواجهات بيعالج أزمة كبيرة في هندسة الاختبارات المؤتمتة (Test Harness). لما كلاس بيعتمد على Fat Interface فيه 20 دالة، كتابة Test Double أو Mock للكلاس ده بتتطلب كتابة عشرات الأسطر لتهيئة ميثودز فارغة عشان نتجنب الـ NullPointerExceptions أو كسر الـ Mock Expectations.\n\nمع الواجهات المفصولة، بنقدر نعمل Mock أو نكتب Fake بسيط جداً في الذاكرة بيحتوي بس على الدالة أو الدالتين اللي بنختبرهم، وغالباً بتكون الواجهة عبارة عن SAM Interface نقدر نمررها كـ Kotlin Lambda مباشرة، وده بيضمن تشغيل اختبارات JVM فائقة السرعة والاستقرار."
    }
}

# ==========================================
# SOL-16: How do you identify cohesive responsibilities within a God Class?
# ==========================================
DATA["SOL-16"] = {
    "concept_en": """Identifying cohesive responsibilities within a God Class involves analyzing cohesion metrics, state usage clusters, and distinct business stakeholders (actors) to deconstruct monolithic classes into single-responsibility components. In software architecture, a God Class typically exhibits a high Lack of Cohesion of Methods (LCOM), where disjoint subsets of methods operate on mutually exclusive member variables. By auditing field access graphs, identifying competing reasons to change, and grouping operations by their business domains (such as caching, network synchronization, UI presentation, and input validation), senior engineers isolate natural responsibility boundaries for extraction into dedicated UseCases and Repositories.""",
    "walkthrough_en": """Analyzing field clustering to decompose a God Class into cohesive components:
```kotlin
// BAD ANTI-PATTERN: God Class with high Lack of Cohesion of Methods (LCOM)
class GodUserProfileController {
    // Cluster 1 fields: Validation & Formatting
    private val emailRegex = Regex("^[A-Za-z0-9+_.-]+@(.+)\\$")
    fun validateEmail(email: String) = email.matches(emailRegex)

    // Cluster 2 fields: Database Caching
    private val userDao: UserDao = getDatabase().userDao()
    suspend fun cacheUser(user: UserEntity) = userDao.insert(user)

    // Cluster 3 fields: HTTP Remote Networking
    private val api: UserApi = getRetrofit().create(UserApi::class.java)
    suspend fun fetchRemoteUser(id: String) = api.getUser(id)

    // Cluster 4 fields: UI Presentation State
    private val _uiState = MutableStateFlow<ProfileUiState>(ProfileUiState.Loading)
    val uiState = _uiState.asStateFlow()
}

// ARCHITECTURAL BEST PRACTICE: Cohesive, single-responsibility components
class UserInputValidator @Inject constructor() {
    fun isValidEmail(email: String): Boolean = email.isNotBlank() && email.contains("@")
}

class UserRepository @Inject constructor(
    private val api: UserApi,
    private val dao: UserDao
) {
    suspend fun getUser(id: String): Result<User> = runCatching {
        dao.getUser(id)?.toDomain() ?: api.getUser(id).toDomain().also { dao.insert(it.toEntity()) }
    }
}

class ProfileViewModel @Inject constructor(
    private val repository: UserRepository,
    private val validator: UserInputValidator
) : ViewModel() {
    // Pure UI presentation state machine
}
```""",
    "short_en": """We identify cohesive responsibilities within a God Class by analyzing its field-method access graph and identifying distinct business actors. A God Class reveals itself when disjoint groups of methods access only specific subsets of member variables without cross-interaction, exhibiting high Lack of Cohesion of Methods (LCOM). By clustering methods around their shared state—separating network APIs, database DAOs, input validation, and UI state—we delineate clean boundaries to extract into dedicated Repositories, UseCases, and ViewModels.""",
    "structured_en": """Deconstructing a God Class requires a systematic methodology rather than arbitrary file splitting.
A God Class arises when developers continually append new requirements to an existing file, gradually combining networking, storage, validation, and presentation.
Senior engineers use three complementary techniques to identify natural responsibility seams.
First, perform field-method cluster analysis. Diagram which methods access which member variables. In a God Class, you will discover distinct, disconnected islands of state: validation regexes used only by input checkers, database DAOs used only by persistence functions, and HTTP clients used only by network calls. These isolated clusters represent textbook candidates for extraction.
Second, identify business actors and change triggers. Ask: who requests modifications to this method? Marketing changes analytics events, backend architects alter API schemas, DBAs modify caching tables, and UX designers adjust screen layouts. Methods driven by different actors belong in different classes.
Third, extract components progressively along architectural boundaries: moving validation to pure utility classes, data persistence to Repositories, and business orchestration to UseCases, leaving the host class focused strictly on its primary responsibility.""",
    "deep_senior_en": """Under the hood, cohesion can be mathematically formalized using the Lack of Cohesion of Methods (LCOM) metric suite (such as LCOM4).
In graph theory, LCOM4 constructs an undirected graph where nodes represent class methods, and edges connect methods that access at least one shared instance variable or invoke each other directly. In an ideal single-responsibility class, LCOM4 equals 1, indicating a single connected component where all methods collaborate on a cohesive state. In an Android God Activity or God ViewModel, LCOM4 frequently reaches 5 or higher, proving that the class is a composite artifact artificially grouping independent subgraphs.
Extracting these subgraphs into isolated classes directly impacts memory allocation and Garbage Collection behavior in the Android ART runtime. Monolithic God Classes hold long-lived references to multiple heavyweight resources simultaneously—SQLite database connections, OkHttpClient instances, Bitmaps, and View contexts. Because these references reside in the same object graph, their memory lifetimes are tied together, preventing generational Garbage Collection from reclaiming temporary buffers and driving up memory pressure.
By decomposing the God Class into fine-grained, scoped dependencies managed by Hilt or Dagger, memory lifecycles decouple. Transient objects are collected promptly in generation-zero heap allocations, reducing GC pause frequencies and eliminating hidden memory leaks during Android screen configuration changes.""",
    "meta_ar": {
        "id": "SOL-16",
        "questionAr": "كيف تحدد المسؤوليات المترابطة (Cohesive Responsibilities) داخل God Class لتفكيكه؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على تحليل الكود المتضخم، وفهم مقاييس التماسك (Cohesion) ومقياس LCOM، وتحليل مجموعات الحقول والدوال المترابطة، واستخراج المسؤوليات إلى UseCases و Repositories متخصصة.",
        "why_it_matters_ar": "كائنات الـ God Classes تمثل الخطر الأكبر في مشاريع أندرويد؛ تفكيكها العشوائي قد يخلق فوضى أكبر، بينما تفكيكها المنهجي يعيد للتطبيق مرونته وسرعة صيانته واختباره.",
        "worked_example_ar": "تحليل الحقول واستخراج الكلاسات المتماسكة:\n```kotlin\n// كود سيئ: كلاس واحد يجمع الشبكة والداتابيز والـ UI\nclass GodVM { val api: Api; val dao: Dao; val uiState: Flow }\n// تفكيك متماسك: عزل البيانات في Repository وعزل الواجهة في ViewModel\nclass UserRepo(val api: Api, val dao: Dao) { ... }\nclass ProfileVM(val repo: UserRepo) : ViewModel() { ... }\n```",
        "trade_offs_ar": "يتطلب وقتاً في التحليل وإعادة هيكلة التبعيات، لكنه يقلل استهلاك الذاكرة، ويمنع تسريبات الـ Memory Leaks، ويجعل الكود قابلاً للاختبار المنفصل.",
        "failure_modes_ar": "التقطيع العشوائي للكلاس إلى ملفات متعددة دون فهم تماسك البيانات، مما يخلق كوداً متشابكاً بتبعيات دائرية (Circular Dependencies).",
        "production_perspective_ar": "في المشروعات الكبيرة، نستخدم أدوات التحليل الساكن زي SonarQube أو Detekt لمراقبة مقياس التعقيد الدوري (Cyclomatic Complexity) وعدد أسطر الكلاس لمنع ولادة أي God Class.",
        "how_to_answer_ar": "اشرح المنهجية العلمية: أولاً تحليل استخدام الحقول والدوال (Field-Method Clustering) واكتشاف الجزر المعزولة من البيانات، ثانياً تحديد الجهات المسؤولة عن التغيير (Actors)، وثالثاً ذكر مقياس LCOM رياضياً، ورابعاً خطوات الاستخراج لـ UseCases و Repositories.",
        "talking_points_ar": "مفهوم High Cohesion، ومقياس LCOM4، وتحليل مجموعات البيانات المستقلة (State Clustering)، وتحديد الـ Actors، وأثر التفكيك على دورة حياة الذاكرة وجمع القمامة (GC).",
        "follow_ups_ar": "- **المحاور:** \"ما هو مقياس LCOM وكيف نستخدمه عملياً؟\"\n  **المرشح:** \"مقياس Lack of Cohesion of Methods بيمثل رسم بياني؛ لو الدوال بتشارك نفس المتغيرات بتكون القيمة 1 وده ممتاز، ولو كل مجموعة دوال شغالة على متغيرات تانية القيمة بتزيد، وده دليل قاطع على وجود كذا مسؤولية لازم تتفصل.\"\n\n- **المحاور:** \"كيف يحمي تفكيك الـ God Class ذاكرة التطبيق من الـ Leaks؟\"\n  **المرشح:** \"الكلاس العملاق بيحتفظ بمراجع للـ Context والـ Bitmaps وقواعد البيانات معاً، فبتفضل عايشة في الـ Heap، بينما تفكيكها بيسمح لـ Garbage Collector بتنظيف الكائنات المؤقتة بسرعة.\"",
        "self_check_ar": "هل شرحت فكرة تجميع الحقول والدوال؟ هل ذكرت مفهوم الـ Actors ومقياس LCOM؟ وهل ربطت الإجابة بإدارة الذاكرة في أندرويد؟",
        "references_ar": f"- [Cohesion in Software Engineering](https://en.wikipedia.org/wiki/Cohesion_(computer_science)) — المرجع الأكاديمي لمقاييس التماسك.\n- [LCOM Metric Explained](https://www.ndepend.com/docs/code-metrics#LCOM) — شرح مقاييس LCOM في هندسة البرمجيات.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "بنحدد المسؤوليات المتماسكة داخل الـ God Class عن طريق فحص العلاقات بين الدوال والمتغيرات (Field-Method Clustering) وتحديد الجهات المسؤولة عن التغيير (Actors). الكلاس العملاق بيكشف نفسه لما تلاقي جزر معزولة من الكود؛ دوال معينة بتستخدم فقط كائنات الشبكة، ودوال تانية بتستخدم فقط كائنات الداتابيز، ودوال تالتة بتتعامل مع الـ UI. بنرصد التشتت ده علمياً بمقياس LCOM، وبنعزل كل جزيرة متجانسة في كلاس مستقل زي UseCase أو Repository متخصص.",
        "best_answer_ar": "تفكيك الـ God Class محتاج منهجية هندسية دقيقة عشان مننقلش الفوضى من كلاس واحد لمجموعة كلاسات مشوهة.\n\nالخطوة الأولى هي تحليل مجموعات البيانات والدوال (State Clustering). لو مسكت كلاس زي `UserProfileManager` ورسمت خريطة لمتغيراته، هتكتشف فوراً إن الكود متقسم جزر ملهاش دعوة ببعض: متغيرات التحقق من الإيميل مش بتدخل غير في دوال الفاليديشن، ومتغيرات قاعدة البيانات مش بتدخل غير في دوال الحفظ، ومتغيرات الحالة مش بتدخل غير في دوال الرسم. كل جزيرة مستقلة من دول هي في الحقيقة كائن متماسك بيصرخ عشان يستقل بذاته.\n\nالخطوة الثانية هي فحص أسباب التغيير والجهات المعنية (Actors). بنسأل نفسنا: لو الميزة دي اتغيرت، مين صاحب القرار؟ لو تغيير في شكل الواجهة بيطلبوا مصمم الـ UI، وتغيير السيرفر بيطلبه فريق الباك إند، وتغيير التخزين بيطلبه مهندس الداتابيز؛ يبقى يستحيل منطق التلاتة يفضل محشور في نفس الملف.\n\nالخطوة الثالثة هي الاستخراج التدريجي: بننقل الفاليديشن لكلاس نقي، والتخزين والشبكة لـ Repository، والعمليات المعقدة لـ UseCases، ونسيب الـ ViewModel يدير حالة الشاشة فقط.",
        "deep_answer_ar": "تحت الكابوت، التماسك الداخلي للكلاس له تأصيل رياضي في هندسة البرمجيات عبر مقياس يسمى Lack of Cohesion of Methods (LCOM4).\n\nفي نظرية المخططات (Graph Theory)، مقياس LCOM4 بيعتبر دوال الكلاس عقد (Nodes) والروابط بينها هي استخدام نفس المتغيرات العامة (Instance Variables). في الكلاس النظيف والمثالي، قيمة LCOM4 بتكون 1، يعني المخطط مترابط تماماً وكل الدوال بتتعاون على نفس البيانات. في كائنات الـ God Class في أندرويد، القيمة بتوصل لـ 5 أو 10، وده معناه وجود عدة مكونات مستقلة ومفصولة تماماً تم حشرها خطأً في كلاس واحد.\n\nتفكيك الكلاسات دي له أثر مباشر على أداء الـ Garbage Collector والـ Heap Memory في بيئة تشغيل ART. الكلاس العملاق بيحتفظ بمراجع (References) طويلة الأمد لكائنات ثقيلة معاً في نفس الوقت: كائنات Room، وعملاء OkHttp، وسياق الـ Activity، وصور الـ Bitmaps. وجودهم مع بعض بيجعل دورة حياتهم مربوطة بالكائن الأكبر، وبيمنع محرك جمع القمامة من التخلص من الكائنات المؤقتة في الـ Young Generation.\n\nلما نفكك الكلاس لكائنات صغيرة ونحقنها بـ Hilt بنطاقات دورة حياة دقيقة (Scoped Dependencies)، الكائنات المؤقتة بتتحرر فوراً من الذاكرة، وده بيقلل الـ Garbage Collection Pauses، ويمنع هبوط معدل الإطارات (Frame Drops)، ويحمي التطبيق من الـ Memory Leaks أثناء تدوير الشاشة."
    }
}

# ==========================================
# SOL-17: A subclass needs to throw UnsupportedOperationException for a base behavior. What design principle might be violated?
# ==========================================
DATA["SOL-17"] = {
    "concept_en": """When a subclass throws UnsupportedOperationException to opt out of a method inherited from its parent class or interface, the Liskov Substitution Principle (LSP) is directly violated. LSP, formalized by Barbara Liskov, asserts that subtypes must be completely substitutable for their base types without altering program correctness or violating consumer expectations. Throwing an exception strengthens method preconditions and shatters behavioral subtyping, breaking the contract promised by the base abstraction. The solution requires replacing monolithic inheritance hierarchies with fine-grained interfaces (Interface Segregation) or composition.""",
    "walkthrough_en": """Contrasting an LSP violation with behavioral subtyping in an Android data repository:
```kotlin
// BAD ANTI-PATTERN: Violates LSP (Subclass breaks base contract by throwing runtime exception)
interface DocumentStorage {
    suspend fun readDocument(id: String): Document
    suspend fun writeDocument(doc: Document) // Base contract implies all implementations can write!
}

class ReadOnlyCloudDocumentStorage : DocumentStorage {
    override suspend fun readDocument(id: String) = fetchFromCloud(id)
    override suspend fun writeDocument(doc: Document) {
        // Blatant LSP Violation! Calling code expecting DocumentStorage crashes at runtime!
        throw UnsupportedOperationException("Read-only cloud storage cannot write documents")
    }
}

// ARCHITECTURAL BEST PRACTICE: Segregated behavioral contracts adhering to LSP
interface ReadableStorage { suspend fun readDocument(id: String): Document }
interface WritableStorage { suspend fun writeDocument(doc: Document) }

// Fully substitutable read-only storage
class ReadOnlyCloudStorage(private val api: DocApi) : ReadableStorage {
    override suspend fun readDocument(id: String) = api.getDocument(id)
}

// Fully substitutable read-write storage
class LocalDiskStorage(private val dao: DocDao) : ReadableStorage, WritableStorage {
    override suspend fun readDocument(id: String) = dao.getDocument(id)
    override suspend fun writeDocument(doc: Document) = dao.saveDocument(doc)
}
```""",
    "short_en": """Throwing an UnsupportedOperationException in a subclass directly violates the Liskov Substitution Principle (LSP). LSP dictates that any subclass must be safely substitutable for its parent type without breaking caller expectations. When a subclass refuses an inherited method by throwing an exception, it shatters the behavioral contract, causing runtime crashes for callers relying on polymorphism. The proper fix is segregating the bloated base contract into smaller, focused interfaces that subclasses can fulfill completely.""",
    "structured_en": """When a subclass throws an UnsupportedOperationException for an inherited method, it is the textbook indicator of a broken Liskov Substitution Principle (LSP).
LSP asserts that if program S is designed to operate on base type T, S must function correctly when given any subtype of T without knowing the concrete variant. A base class or interface establishes an implicit contract: every public method represents a valid, supported capability.
When a subclass overrides a method with UnsupportedOperationException, it breaks this contract.
In Android, this anti-pattern frequently surfaces in repository hierarchies and collection adapters. For instance, creating a general-purpose DocumentStorage interface with both read and write methods, and then implementing a ReadOnlyDocumentStorage that throws an exception in the write method. When a background sync worker or ViewModel invokes write, the application crashes in production.
The remedy is to refactor the inheritance hierarchy using the Interface Segregation Principle.
Split the contract into fine-grained interfaces: ReadableStorage and WritableStorage.
Classes that only support reading implement only the readable contract. Clients expecting write capabilities accept only WritableStorage, transforming runtime exception crashes into safe, compile-time type guarantees.""",
    "deep_senior_en": """Under the hood, throwing UnsupportedOperationException shatters the mathematical foundation of Design by Contract that governs the Liskov Substitution Principle.
In contract theory, a method defines preconditions (requirements the caller must satisfy before execution) and postconditions (guarantees the method provides upon completion). To maintain behavioral subtyping, a subtype may weaken preconditions (demand less) and strengthen postconditions (guarantee more), but it must never strengthen preconditions.
Throwing an UnsupportedOperationException effectively strengthens the precondition to 'false'—meaning the method cannot be called under any condition whatsoever. This shatters polymorphism at the bytecode level, forcing callers to employ dirty runtime inspections like 'if (storage is ReadOnlyStorage)' before invoking methods, defeating the entire purpose of object-oriented design.
A notorious framework example occurred in legacy Java with Collections.unmodifiableList(), which implemented java.util.List but threw UnsupportedOperationException on add(). If an Android developer passed an unmodifiable list into an adapter expecting a standard mutable list, the application crashed with a fatal exception.
Kotlin eradicated this design defect at the language level by bifurcating the collection hierarchy into List (read-only covariant interface) and MutableList (read-write invariant interface).
Senior Android engineers apply this exact principle to domain modeling: never use exceptions to opt out of inherited contracts. Segregate interfaces or switch to composition so that every type satisfies its full contract unconditionally.""",
    "meta_ar": {
        "id": "SOL-17",
        "questionAr": "إذا اضطر كلاس فرعي لرمي UnsupportedOperationException لدالة موروثة، فما هو المبدأ المنتهك؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم مبدأ استبدال ليسكوف (LSP) وعقود السلوك البرمجي (Design by Contract)، والقدرة على اكتشاف الانتهاكات الشائعة وحلها بفصل الواجهات (ISP) أو التفضيل للتركيب بدلاً من الوراثة.",
        "why_it_matters_ar": "رمي استثناءات لتعطيل دوال موروثة يفخخ كود التطبيق بانهيارات غير متوقعة في وقت التشغيل (Runtime Crashes) عندما يعتمد النظام على التعددية الشكلية (Polymorphism).",
        "worked_example_ar": "حل انتهاك ليسكوف بفصل واجهات القراءة والكتابة:\n```kotlin\n// انتهاك ليسكوف: كلاس يرمي استثناء لتعطيل الحفظ\nclass ReadOnlyRepo : Repo { override fun save() = throw UnsupportedOperationException() }\n// كود نظيف متوافق مع ليسكوف 100%\ninterface Reader { fun get(): Data }\ninterface Writer { fun save(d: Data) }\nclass ReadOnlyRepo : Reader { override fun get() = ... }\n```",
        "trade_offs_ar": "يتطلب تفكيك الواجهة الكبيرة إلى واجهات أصغر، لكنه يمنع انهيارات الإنتاج تماماً ويحول الأخطاء إلى أخطاء وقت الـ Compilation.",
        "failure_modes_ar": "وراثة كلاس وإعادة كتابة دالة لترمي استثناء أو ترك جسمها فارغاً، وإجبار الكود المنادي على كتابة فحص بالنوع `if (repo is ReadOnly)`.",
        "production_perspective_ar": "في كود الإنتاج عالي الجودة، نقتدي بتصميم كوتلن التي فصلت `List` عن `MutableList`، ونمنع قبول أي كلاس يرمي استثناء في دالة موروثة عبر مراجعات الكود الصارمة.",
        "how_to_answer_ar": "حدد المبدأ فوراً: مبدأ استبدال ليسكوف (LSP)، واشرح لماذا: الكلاس الابن يجب أن يحل محل الكلاس الأب دون كسر توقعات المنادي، ووضح أن رمي الاستثناء يكسر عقد السلوك البرمجي، واعرض الحل بفصل الواجهات واستشهد بمثال `List` و `MutableList` في كوتلن.",
        "talking_points_ar": "مبدأ Liskov Substitution Principle (LSP)، ومفهوم Design by Contract، وانتهاك التعددية الشكلية، والحل بفصل الواجهات، ومثال Java Collections مقابل Kotlin Collections.",
        "follow_ups_ar": "- **المحاور:** \"ما هو التأثير المباشر لانتهاك ليسكوف على كود الشاشات والـ ViewModels؟\"\n  **المرشح:** \"المطورين بيضطروا يكتبوا `if (repo is ReadOnlyRepo)` قبل استدعاء الدالة عشان يتجنبوا الـ Crash، وده بيكسر مبدأ OCP ويلغي فائدة الـ Polymorphism تماماً.\"\n\n- **المحاور:** \"هل ترك جسم الدالة فارغاً (Empty body / No-op) يعتبر انتهاكاً لليسكوف مثل رمي الاستثناء؟\"\n  **المرشح:** \"نعم بالتأكيد، لو كان العقد الموروث يفترض حفظ بيانات أو إطلاق كولباك معين، وتجاهله تسبب في ترك النظام في حالة غير متسقة، فهو انتهاك كامل لليسكوف.\"",
        "self_check_ar": "هل حددت مبدأ ليسكوف بوضوح؟ هل شرحت مفهوم العقد السلوكي؟ وهل بينت الحل بفصل الواجهات مع الاستشهاد بتصميم كوتلن للقوائم؟",
        "references_ar": f"- [Liskov Substitution Principle by Barbara Liskov](https://en.wikipedia.org/wiki/Liskov_substitution_principle) — المرجع الكلاسيكي لمبدأ ليسكوف.\n- [Design by Contract Principles](https://en.wikipedia.org/wiki/Design_by_contract) — التوثيق الأكاديمي لمفهوم التصميم بالعقود.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "المبدأ المنتهك هنا صراحة هو مبدأ استبدال ليسكوف (Liskov Substitution Principle - LSP). المبدأ ده بينص على إن أي كلاس ابن لازم يقدر يحل محل الكلاس الأب بتاعه بالكامل بدون ما يكسر تصرف البرنامج أو يغير التوقعات المتفق عليها. لما الكلاس الابن يعمل Override لدالة ويرمي جواها `UnsupportedOperationException`، هو كده كسر العقد البرمجي وخان ثقة الكود اللي بيناديه، وهيسبب Crash في الإنتاج. الحل الهندسي هو تفكيك الواجهة الكبيرة لإنترفيسات متخصصة أصغر بتطبيق مبدأ فصل الواجهات (ISP).",
        "best_answer_ar": "السيناريو ده هو المثال الأوضح والأكثر شهرة في هندسة البرمجيات لانتهاك مبدأ استبدال ليسكوف (LSP).\n\nمبدأ ليسكوف مش مجرد توافق في أسماء الدوال وقت الـ Compile time، بل هو توافق في السلوك والوعود البرمجية (Behavioral Subtyping). لما تعرف إنترفيس فيه دالة `saveData` أو `printDocument`، أنت بتعطي وعداً صريحاً لكل أجزاء التطبيق إن أي كائن بيحمل النوع ده يقدر ينفذ العملية دي بأمان.\n\nلما يجي كلاس مشتق ويرمي `UnsupportedOperationException`، هو كده بيتنصل من الوعد ده وبيكسر التعددية الشكلية (Polymorphism). الكود المنادي في الخلفية أو في الـ ViewModel معندوش أي فكرة إن الكائن اللي في إيده ده كائن 'معطوب'، فهيستدعي الدالة بثقة كاملة ويتفاجأ بانهيار فوري للتطبيق في الإنتاج.\n\nالنتيجة الأسوأ لده إن المطورين بيبدأوا يكتبوا كود سيئ عشان يتحايلوا على المشكلة، فيكتبوا فحص بالنوع زي `if (storage is ReadOnlyStorage)` قبل الاستدعاء، وده بيلغي قيمة البرمجة الكائنية تماماً.\n\nالحل الصحيح هو تفكيك الواجهة الكبيرة باستخدام مبدأ فصل الواجهات (ISP): نفصل القراءة في `ReadableStorage` والكتابة في `WritableStorage`. الكلاس اللي بيقرأ فقط هيطبق واجهة القراءة فقط، والكومبايلر نفسه هيمنع أي استدعاء خاطئ للدوال غير المدعومة.",
        "deep_answer_ar": "تحت الكابوت، رمي `UnsupportedOperationException` بيهدم الأساس الرياضي لنظرية التصميم بالعقود (Design by Contract) الحاكمة لمبدأ ليسكوف.\n\nفي نظرية العقود، كل دالة برمجية لها شروط مسبقة (Preconditions) لازم المنادي يوفرها، وشروط لاحقة (Postconditions) بتضمن الدالة تحقيقها بعد التنفيذ. عشان يتحقق مبدأ استبدال ليسكوف رياضياً، مسموح للكلاس الابن إنه يخفف الشروط المسبقة أو يشدد الشروط اللاحقة، لكن ممنوع قطعياً إنه يشدد الشروط المسبقة (Subtypes cannot strengthen preconditions).\n\nلما كلاس ابن يرمي `UnsupportedOperationException`، هو فعلياً شدد الشروط المسبقة لدرجة مستحيلة (أصبحت Precondition = False)، وده معناه إنه مفيش أي حالة على الإطلاق تسمح باستدعاء الدالة دي، وده كسر صريح للعقد البرمجي على مستوى الـ Bytecode.\n\nالمشكلة دي عانت منها لغة جافا لعقود في حزمة الـ Collections؛ لما كانت بتعمل `Collections.unmodifiableList()`، كانت القائمة بتطبق `java.util.List` لكن بترمي استثناء لو ناديت دالة `add()`. في أندرويد، لو مررت القائمة دي لأدابتر متوقع قائمة عادية، كان التطبيق بينهار فوراً في وقت التشغيل.\n\nلغة كوتلن حلت العيب التاريخي ده في صلب نظام الأنواع بتاعها عن طريق فصل القوائم لنوعين: `List` كـ Read-only Interface متوافق كلياً مع القراءة، و `MutableList` كـ Read-Write Interface. المهندسون الكبار بيطبقوا نفس الفلسفة دي في تصميم طبقات الدومين والبيانات لمنع أي انهيارات برمجية غير متوقعة."
    }
}

# ==========================================
# SOL-18: A new payment provider requires editing 10 existing classes. Which principles would help?
# ==========================================
DATA["SOL-18"] = {
    "concept_en": """When integrating a single new payment provider forces changes across ten existing classes, the codebase is suffering from the 'Shotgun Surgery' architectural code smell, directly violating the Open/Closed Principle (OCP), the Single Responsibility Principle (SRP), and the Dependency Inversion Principle (DIP). In well-architected systems, adding a variant capability should be an additive change requiring zero edits to existing, tested orchestration code. By encapsulating payment execution behind a polymorphic PaymentStrategy interface, centralizing payment routing, and inverting dependencies, new payment rails can be introduced simply by writing a new strategy class.""",
    "walkthrough_en": """Refactoring Shotgun Surgery into an OCP/DIP-compliant strategy architecture:
```kotlin
// BAD ANTI-PATTERN: Shotgun Surgery (Adding ApplePay forces modifying 10 ViewModels, Services, and DAOs)
class CheckoutViewModel {
    fun pay(type: String) {
        when(type) {
            "Stripe" -> stripeService.pay()
            "PayPal" -> payPalService.pay()
            // Modified here, modified in Analytics, modified in ReceiptGenerator, modified in DB...
        }
    }
}

// ARCHITECTURAL BEST PRACTICE: Closed to modification, open to extension via Strategy and DIP
interface PaymentGateway {
    fun handles(type: PaymentMethod): Boolean
    suspend fun executePayment(amount: Long): Result<PaymentReceipt>
}

// New provider added as a standalone class: ZERO edits to existing classes!
class ApplePayGateway @Inject constructor(private val applePayClient: ApplePayClient) : PaymentGateway {
    override fun handles(type: PaymentMethod) = type is PaymentMethod.ApplePay
    override suspend fun executePayment(amount: Long) = runCatching { applePayClient.charge(amount) }
}

// Central PaymentProcessor is 100% CLOSED to modification
class PaymentProcessor @Inject constructor(
    private val gateways: Set<@JvmSuppressWildcards PaymentGateway>
) {
    suspend fun process(method: PaymentMethod, amount: Long): Result<PaymentReceipt> {
        val gateway = gateways.firstOrNull { it.handles(method) }
            ?: return Result.failure(IllegalStateException("No gateway for $method"))
        return gateway.executePayment(amount)
    }
}
```""",
    "short_en": """The principles that resolve this issue are the Open/Closed Principle (OCP), Single Responsibility Principle (SRP), and Dependency Inversion Principle (DIP). Modifying ten classes to add one payment rail is the classic Shotgun Surgery code smell, caused by hardcoded conditional logic and leaking provider details across layers. By encapsulating payment logic inside a polymorphic PaymentStrategy interface and inverting dependencies, adding a new provider becomes a purely additive operation involving only a new class.""",
    "structured_en": """Having to modify ten existing classes to support a single new payment provider is the hallmark symptom of Shotgun Surgery, caused by violations across the SOLID spectrum.
This anti-pattern occurs when payment handling logic is fragmented across the application: ViewModels check string flags in when blocks, network repositories format provider-specific payloads, and analytics classes maintain hardcoded vendor mappings. When a new provider like Apple Pay is added, the developer must open and modify every single one of those files.
Three core SOLID principles resolve this architectural flaw.
First, the Open/Closed Principle (OCP) mandates that the system should be open for extension but closed for modification. We achieve this using the Strategy pattern, where all payment providers adhere to a unified PaymentGateway interface.
Second, the Single Responsibility Principle (SRP) isolates payment orchestration into a dedicated processor, removing payment branching from ViewModels and UI layers.
Third, the Dependency Inversion Principle (DIP) ensures that high-level checkout flows depend only on the abstract PaymentGateway contract.
By combining these principles with Dagger Multibindings, adding a new payment rail requires writing exactly one new class and registering it in the dependency graph, leaving all ten existing classes completely untouched.""",
    "deep_senior_en": """Under the hood, Shotgun Surgery represents the inverse problem of the Divergent Change code smell, and its presence indicates severe architectural erosion across Gradle module boundaries.
When adding a payment provider touches ten classes, it proves that low-level infrastructure details have leaked upward into high-level presentation and domain state machines. In a multi-module enterprise Android application, this leak creates extensive build invalidation cascades. If ten classes across :feature:checkout, :core:analytics, and :data:repository contain explicit references to payment provider implementations, changing or adding a provider invalidates the Gradle build cache across all three modules, triggering massive recompilations.
By restructuring the system around OCP and DIP, the payment domain boundary becomes fortified. The :domain module defines the abstract PaymentGateway interface and PaymentMethod sealed class.
Each payment vendor lives inside its own isolated Gradle feature module (such as :payment:stripe and :payment:applepay).
These modules bind their gateway implementations into Dagger's dependency injection container using @Binds @IntoSet.
The orchestrating PaymentProcessor in the checkout module injects the Set<PaymentGateway>, routing transactions polymorphically at runtime.
Adding a new payment vendor touches zero existing files, generates zero merge conflicts in Git, and causes zero recompilation of existing modules, preserving long-term developer velocity and architectural purity. This decoupling ensures that enterprise applications scale frictionlessly without destabilizing previously certified core features.""",
    "meta_ar": {
        "id": "SOL-18",
        "questionAr": "إذا تطلب إضافة مزود دفع جديد تعديل 10 كلاسات موجودة بالفعل، فما هي المبادئ التي تعالج ذلك؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على تشخيص مشكلة الـ Shotgun Surgery، وتطبيق مبادئ OCP و SRP و DIP لحلها جذرياً، وهندسة نظام مدفوعات مرن يعتمد على نمط Strategy وحقن المجموعات في Dagger.",
        "why_it_matters_ar": "الاضطرار لتعديل 10 ملفات مع كل ميزة جديدة يعطل الإنتاجية، ويخلق صراعات دمج مستمرة في Git، ويزيد من مخاطر ظهور أخطاء غير متوقعة في كود مستقر في الإنتاج.",
        "worked_example_ar": "علاج الـ Shotgun Surgery بنمط Strategy و DIP:\n```kotlin\n// كود نظيف: بوابة دفع موحدة ومستقلة تماماً\ninterface PaymentGateway { fun handles(m: Method): Boolean; suspend fun pay(amt: Long) }\n// إضافة مزود جديد بكلاس مستقل تماماً بدون لمس أي ملف قديم!\nclass ApplePayGateway : PaymentGateway { ... }\n// المنسق المركزي مغلق للتعديل ويستقبل أي بوابة عبر الـ DI\nclass PaymentProcessor(val gateways: Set<PaymentGateway>) { ... }\n```",
        "trade_offs_ar": "يتطلب إعادة هيكلة شاملة للكود القديم وتوحيد نماذج الدفع، لكنه يحمي المشروع مستقبلاً ويجعل إضافة أي مزود جديد عملية آمنة وسريعة بنسبة 100%.",
        "failure_modes_ar": "استمرار كتابة كتل when وفحص أنواع الدفع داخل الـ ViewModels والـ Repositories في كل مكان، مما يزيد من تشابك الكود.",
        "production_perspective_ar": "في الشركات الكبرى، نعتبر تعديل ملفات متعددة لإضافة ميزة واحدة مؤشراً خطيراً في Code Review (Shotgun Surgery Smell)، ونرفض الـ PR ونطلب إعادة هيكلته بـ Strategy و OCP.",
        "how_to_answer_ar": "سم المشكلة البرمجية فوراً: Shotgun Surgery Code Smell، وحدد المبادئ الثلاثة المعالجة: OCP (الفتح والإغلاق) و SRP (المسؤولية الواحدة) و DIP (قلب الاعتماديات)، واشرح الحل الهندسي: توحيد الدفع وراء إنترفيس PaymentGateway، واستخدام نمط Strategy مع Dagger Multibindings لحقن البوابات، لتصبح الإضافة بكلاس جديد فقط.",
        "talking_points_ar": "عيب Shotgun Surgery، ومبادئ OCP و SRP و DIP، ونمط Strategy، وتقنية Dagger @IntoSet، وأثر الحل على تقليل الـ Merge Conflicts وسرعة البناء.",
        "follow_ups_ar": "- **المحاور:** \"ما هو الفرق بين Shotgun Surgery و Divergent Change؟\"\n  **المرشح:** \"الـ Shotgun Surgery بتعني إن تعديل واحد بيجبرك تعدل في ملفات كتير، وده كسر لـ OCP و DIP؛ أما Divergent Change فبتعني إن ملف واحد بيتعدل لأسباب كتير مختلفة، وده كسر صريح لـ SRP.\"\n\n- **المحاور:** \"كيف نضمن ألا ينسى المطور تسجيل مزود الدفع الجديد في شجرة الـ DI؟\"\n  **المرشح:** \"عبر الـ Multibindings في Hilt؛ بمجرد كتابة `@Binds @IntoSet` في موديول البوابة الجديدة، Hilt بتجمعها آلياً في القائمة بدون الحاجة لتسجيلها يدوياً في أي كلاس مركزي.\"",
        "self_check_ar": "هل سميت مشكلة Shotgun Surgery؟ هل شرحت دور OCP و SRP و DIP؟ وهل بينت الحل بنمط Strategy و Dagger Multibindings؟",
        "references_ar": f"- [Refactoring: Shotgun Surgery by Martin Fowler](https://refactoring.guru/smells/shotgun-surgery) — الشرح المرجعي لمشكلة الجراحة المتناثرة.\n- [Clean Code: Principles of OOD](https://en.wikipedia.org/wiki/SOLID) — كتاب الكود النظيف للعم بوب.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "المشكلة دي في هندسة البرمجيات بنسميها 'Shotgun Surgery'؛ والمبادئ الأساسية اللي بتعالجها هي مبدأ الفتح والإغلاق (OCP)، ومبدأ المسؤولية الواحدة (SRP)، ومبدأ قلب الاعتماديات (DIP). المشكلة حصلت لأن تفاصيل مزودي الدفع متسربة ومبعثرة في الشاشات والـ ViewModels. بنحلها بإننا نوحد عقود الدفع وراء إنترفيس `PaymentGateway` باستخدام نمط Strategy ونحقن البوابات كـ Set عبر Dagger. بكده إضافة مزود جديد بتتحول لعملية إضافة كلاس جديد خالص بدون تعديل سطر واحد في الكلاسات القديمة.",
        "best_answer_ar": "الاضطرار لتعديل 10 كلاسات عشان تضيف مزود دفع جديد هو العرض الكلاسيكي لرائحة كود شهيرة بنسميها 'الجراحة المتناثرة' (Shotgun Surgery)، وده دليل قاطع على إن كود الدفع متشابك ومنتهك لمبادئ SOLID الأساسية.\n\nالمبادئ اللي بتنقذ الكود ده هي تلاتة:\nأولاً: مبدأ الفتح والإغلاق (OCP)؛ السيستم المفروض يكون مفتوحاً لإضافة بوابات جديدة، ومغلقاً تماماً أمام تعديل الكلاسات القديمة.\nثانياً: مبدأ المسؤولية الواحدة (SRP)؛ الـ ViewModels والشاشات مسؤوليتها إدارة الواجهة وتجربة المستخدم، مش فحص أسماء بوابات الدفع وشروطها.\nثالثاً: مبدأ قلب الاعتماديات (DIP)؛ منطق الدفع في التطبيق لازم يعتمد على تجريد مجرد مش كلاسات ومكتبات البنوك الملموسة.\n\nالعلاج الهندسي المتين بيتم في خطوتين:\nأولاً: بنعمل إنترفيس موحد اسمه `PaymentGateway` فيه دالة لتنفيذ الدفع ودالة لمعرفة هل البوابة بتدعم وسيلة الدفع دي ولا لأ.\nثانياً: كل بوابة (Stripe أو Apple Pay) بتتعمل في كلاس مستقل، وبنعمل كلاس منسق مركزي `PaymentProcessor` بيستقبل البوابات دي تلقائياً عبر Dagger Multibindings (`@IntoSet`).\n\nلما يطلب البيزنس إضافة مزود عاشر، المهندس بيكتب كلاس المزود الجديد فقط بدون لمس الـ 10 كلاسات القديمة نهائياً، وده بيمنع أي أخطاء Regression ويقضي على صراعات دمج الفروع في Git.",
        "deep_answer_ar": "تحت الكابوت، مشكلة الـ Shotgun Surgery بتمثل اختراقاً خطيراً لحدود الموديولات المعمارية في مشاريع أندرويد الضخمة، ولها تأثير مباشر على استقرار الـ CI/CD وسرعة الـ Compilation.\n\nلو إضافة مزود دفع جديد بتجبرك تعدل 10 كلاسات متوزعة بين موديول الشاشات وموديول التحليلات وموديول قواعد البيانات، ده معناه إن تفاصيل البنية التحتية لمكتبات الـ SDKs الخاصة بالدفع اتسربت للموديولات العليا. النتيجة إن أي تعديل بيلغي كاش البناء (Build Cache) لموديولات المشروع كلها، وبيجبر Gradle إنه يعيد بناء التطبيق بالكامل ويضيع وقت مهندسي الفريق.\n\nلما نطبق OCP و DIP بصرامة، بنبني حدود معمارية صلبة؛ موديول الـ `:domain` بيحتوي فقط على إنترفيس `PaymentGateway` ونوع الـ Sealed class المجرد. وكل مزود دفع بيعيش في موديول مستقل ومعزول تماماً (`:payment:stripe` و `:payment:applepay`).\n\nالموديولات دي بتسجل تنفيذاتها في شجرة التبعيات عبر `@Binds @IntoSet` في Hilt. كلاس المنسق `PaymentProcessor` بيعيش في موديول الشراء ومبيعرفش غير الإنترفيس النقي، وبيوجه المعاملات المالية في وقت التشغيل عبر التعددية الشكلية (Polymorphic Routing).\n\nإضافة أي مزود جديد بتكون مجرد إضافة موديول جديد في Gradle بدون لمس حرف واحد في كود الموديولات السابقة، وده بيضمن أعلى درجات الـ Parallel Compilation وبيحمي كود المعاملات الحساس من أي عبث غير مقصود."
    }
}

# ==========================================
# SOL-19: When should you deliberately accept a little duplication instead of introducing an abstraction?
# ==========================================
DATA["SOL-19"] = {
    "concept_en": """Deliberately accepting a little duplication instead of introducing a premature abstraction is a hallmark of mature software engineering, famously articulated by Sandi Metz: 'Duplication is far cheaper than the wrong abstraction.' While the Don't Repeat Yourself (DRY) principle cautions against duplicate knowledge, superficial code similarity frequently represents accidental duplication rather than shared domain concepts. In Android development, when two features exhibit similar UI layouts or data structures but evolve under different business stakeholders or change velocities, forcing them into a shared base class or generic abstraction couples their lifecycles, causing architectural rigidity and regression cascades.""",
    "walkthrough_en": """Contrasting the wrong abstraction against pragmatic, independent duplication:
```kotlin
// BAD ANTI-PATTERN: The Wrong Abstraction! (Forcing Auth and Checkout into a bloated shared form model)
open class GenericInputFormModel(
    val email: String,
    val isTermsAccepted: Boolean,
    val promoCode: String? = null, // Leaked from Checkout into Auth!
    val isSocialLogin: Boolean = false // Leaked from Auth into Checkout!
)

// ARCHITECTURAL BEST PRACTICE: Independent, cohesive models with accidental duplication
// 1. Auth Feature Model (Owned strictly by Auth Team / Login Stakeholders)
data class LoginCredentials(
    val email: String,
    val passwordHash: String
)

// 2. Checkout Feature Model (Owned strictly by Commerce Team / Billing Stakeholders)
data class CheckoutCustomerInfo(
    val email: String,
    val shippingAddress: String,
    val promotionalCode: String?
)
// Although both have 'email', their business reasons to change are 100% disconnected!
// Preserving independent models prevents cross-feature coupling!
```""",
    "short_en": """You should deliberately accept duplication when the similarity is accidental rather than conceptual, or when the requirements are still rapidly evolving. In Android, feature modules frequently have similar UI models or validation checks that serve different business actors. Forcing them into a premature shared abstraction creates tight coupling and makes future changes painful. As Sandi Metz observed, duplication is far cheaper than the wrong abstraction; wait until true domain commonality stabilizes.""",
    "structured_en": """Choosing pragmatic duplication over premature abstraction is an essential judgment call that separates dogmatic coders from senior architects.
The DRY (Don't Repeat Yourself) principle is frequently misinterpreted as an absolute ban on duplicate lines of code. However, DRY is fundamentally about avoiding the duplication of business knowledge and authority, not syntactic similarity.
There are three clear scenarios where accepting duplication is the superior architectural decision.
First, when code similarity is accidental rather than essential. If an e-commerce checkout screen and a user profile registration screen both collect an address and an email, their technical data structures look identical. However, marketing may change profile registration rules while payment gateways alter billing address rules. Coupling them to a single shared AddressModel forces one feature to inherit breaking changes meant for another.
Second, during early feature discovery and rapid prototyping. When requirements are fluid, the cost of guessing the wrong abstraction and continually adding boolean flags to accommodate edge cases is astronomically higher than maintaining two separate 20-line classes.
Third, across Gradle module boundaries. Forcing two independent feature modules to share a common utility module just for a minor helper function introduces unnecessary compilation coupling, slowing down builds.""",
    "deep_senior_en": """Under the hood, the wrong abstraction is an architectural debt multiplier that actively dismantles modularity and increases cognitive load.
When developers prematurely merge two similar code paths into a shared class or generic UseCase, they create an artificial coupling point. As the two features inevitably diverge, the shared abstraction cannot adapt cleanly. Developers begin introducing conditional flags, nullable parameters, and boolean mode switches (like isCheckoutMode or skipValidation). The shared class mutates into a brittle state machine violating both SRP and OCP.
In multi-module Android architectures, premature abstractions create toxic dependency graphs. If :feature:auth and :feature:cart share a bloated :core:user-form model, both modules must recompile whenever either team modifies the form.
By deliberately accepting isolated duplication—allowing each feature module to define its own local DTO or UI state representation—modules compile in parallel without shared state locks.
Furthermore, memory locality and ART runtime optimizations favor simple, monomorphic concrete classes over heavily genericized, polymorphic wrapper abstractions that allocate boxed objects and trigger additional virtual method lookups.
Staff engineers follow the Rule of Three: tolerate duplication once, tolerate it twice, but when you encounter the exact same structural pattern a third time with identical change drivers, only then synthesize a deliberate, battle-tested abstraction. This disciplined restraint maintains rapid iteration cycles.""",
    "meta_ar": {
        "id": "SOL-19",
        "questionAr": "متى تقبل بوجود تكرار بسيط في الكود (Duplication) عمداً بدلاً من إنشاء تجريد مبكر (Abstraction)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "النضج الهندسي في فهم حدود مبدأ DRY، وتجنب التجريد الخاطئ (The Wrong Abstraction)، والتفريق بين التكرار العرضي (Accidental) والتكرار الجوهري (Essential Duplication)، وتطبيق قاعدة Rule of Three.",
        "why_it_matters_ar": "التطبيق الأعمى لمنع التكرار ينتج عنه كائنات مشتركة مشوهة مليئة بالـ if-conditions والأعلام المنطقية (Boolean flags)، مما يجعل تعديل ميزة واحدة يكسر ميزات أخرى في الإنتاج.",
        "worked_example_ar": "المقارنة بين التجريد الخاطئ والكود المستقل:\n```kotlin\n// تجريد خاطئ: دمج نموذج الدفع مع تسجيل الدخول لجمع الحقول المتشابهة\nclass SharedForm(val email: String, val isCheckout: Boolean, val promo: String?)\n// كود نظيف: قبول تكرار حقل email لضمان استقلالية كل ميزة تماماً\nclass LoginData(val email: String, val pass: String)\nclass CheckoutData(val email: String, val address: String, val promo: String?)\n```",
        "trade_offs_ar": "قبول تكرار بسيط في كود الموديولات يمنح استقلالية كاملة ويسرع التطوير، بينما التجريد الخاطئ يكلف وقتاً هائلاً في فك التشابك والصيانة.",
        "failure_modes_ar": "دمج كلاسين مختلفين في المعنى لمجرد تشابه بعض الحقول، ثم إضافة شروط `if (mode == LOGIN)` لتفادي الأخطاء.",
        "production_perspective_ar": "في الشركات الكبرى، نفضل استقلالية موديولات الـ Features على مشاركة كلاسات DTO صغيرة، ونعتمد مقولة ساندي ميتز: 'التكرار أرخص بكثير من التجريد الخاطئ'.",
        "how_to_answer_ar": "استشهد بمقولة Sandi Metz: 'Duplication is far cheaper than the wrong abstraction'، وفرق بين التكرار الشكلي والتكرار في منطق العمل (Accidental vs Essential)، واشرح متى نقبل التكرار: اختلاف الـ Actors، واختلاف سرعة التغيير، وفي المراحل الأولى للميزات، واختم بـ Rule of Three.",
        "talking_points_ar": "مفهوم The Wrong Abstraction، والفرق بين Accidental و Essential Duplication، ومبدأ DRY الحقيقي، وأثر التجريد الخاطئ على حدود موديولات Gradle، وقاعدة Rule of Three.",
        "follow_ups_ar": "- **المحاور:** \"ما هو الخطر الأكبر للتجريد الخاطئ (The Wrong Abstraction)؟\"\n  **المرشح:** \"إنه بيتحول لكائن مشوه مليان باراميترز اختيارية و if-conditions عشان يرضي حالتين مختلفين، وأي تعديل فيه لصالح ميزة بيكسر الميزة التانية بدون قصد.\"\n\n- **المحاور:** \"ما هي قاعدة الثلاثة (Rule of Three) في هندسة البرمجيات؟\"\n  **المرشح:** \"إنك تكتب الكود أول مرة، ولما تحتاجه تاني مرة تكرره بدون قلق، لكن لما تلاقيه اتكرر تالت مرة بنفس السلوك ونفس أسباب التغيير، هنا فقط تبني Abstraction حقيقي ومدروس.\"",
        "self_check_ar": "هل ذكرت مقولة ساندي ميتز الشهيرة؟ هل فرقت بين التكرار الشكلي وتكرار منطق العمل؟ وهل بينت أثر ذلك على استقلالية موديولات أندرويد؟",
        "references_ar": f"- [The Wrong Abstraction by Sandi Metz](https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction) — المقال المرجعي الأشهر في هندسة البرمجيات.\n- [DRY Principle by Andy Hunt and Dave Thomas](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself) — أصل مبدأ عدم تكرار المعرفة.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "بنقبل بوجود تكرار بسيط عمداً لما يكون التكرار مجرد تشابه شكلي وعرضي (Accidental Duplication) مش تكرار في قواعد العمل، أو لما تكون الميزة لسه في بدايتها ومتطلباتها بتتغير بسرعة. دمج كود شاشتين مختلفتين لمجرد تشابه بعض الحقول بيخلق تجريداً خاطئاً ومعقداً ملياناً شروط وأعلام منطقية. زي ما قالت المهندسة ساندي ميتز: 'التكرار أرخص بكثير من التجريد الخاطئ'، فالأفضل ننتظر حتى تتضح الصورة ونطبق قاعدة الثلاثة (Rule of Three).",
        "best_answer_ar": "قرار قبول التكرار عمداً هو علامة فارقة بتفصل بين المطور المبتدئ اللي بيطبق القواعد بحفظ أعمى، وبين المهندس السينيور اللي فاهم العواقب المعمارية للكود.\n\nمبدأ DRY (Don't Repeat Yourself) للأسف بيفهمه البعض غلط على إنه منع تكرار كتابة أي سطرين متشابهين. لكن في الحقيقة، مبدأ DRY بيتكلم عن منع تكرار 'المعرفة وقواعد العمل' (Knowledge and Authority)، مش مجرد تشابه شكل الكود.\n\nبنقبل التكرار ونفضله في تلات حالات أساسية:\nأولاً: لما يكون التكرار عرضي (Accidental Duplication). لو شاشة البروفايل وشاشة الشراء فيهم حقل الإيميل والعنوان؛ تشابه الحقول هنا صدفة شكلية. فريق الماركتنج ممكن يغير شروط البروفايل، بينما بوابات الدفع بتغير شروط الشراء. لو جمعناهم في كلاس مشترك، تعديل البروفايل هيعرض كود الدفع لمخاطر الـ Regression.\nثانياً: في بداية بناء الميزات الجديدة؛ لما تكون المتطلبات لسه مش مستقرة، محاولة اختراع Abstraction مسبق بتجبرك بعد أسبوع إنك تضيف `if (isCheckout)` و `boolean flags` مشوهة عشان توفق بين الحالتين.\nثالثاً: بين موديولات الـ Features في أندرويد؛ نسخ كلاس DTO صغير في موديولين منفصلين أفضل بكتير من ربط الموديولين بكور مشترك يبطئ الـ Build في Gradle.\n\nالقاعدة الذهبية هي 'قاعدة الثلاثة' (Rule of Three): اكتب الكود، ولو تكرر مرتين سيبه مستقل، ولما يتكرر تالت مرة بنفس السلوك والهدف، هنا فقط اعمل له Abstraction نظيف ومدروس.",
        "deep_answer_ar": "تحت الكابوت، التجريد الخاطئ (The Wrong Abstraction) هو مضاعف ديون تقنية خطير، وبيدمر استقلالية الموديولات وأداء الـ Compilation في مشاريع أندرويد الضخمة.\n\nلما المطورين يدمجوا مسارين عمل مختلفين في كلاس مشترك عشان يحققوا DRY بشكل سطحي، الكلاس المشترك بيتحول مع الوقت لـ God Class مشوه. بتلاقي الكلاس مليان باراميترز بتقبل Null، وشروط `when (featureMode)` بتفحص الميزة الحالية، وده انتهاك صارخ لمبادئ SRP و OCP. لو الموديولين دول عايشين في `:feature:login` و `:feature:checkout`، دمجهم في كلاس مشترك بيجبر الموديولين يعتمدوا على نفس الموديول، وأي تعديل يعمله فريق تسجيل الدخول هيجبر Gradle إنه يعيد بناء موديول الشراء بالكامل ويلغي ميزة الـ Parallel Compilation.\n\nبينما لما نقبل التكرار المستقل، كل موديول بيملك الـ DTO أو الـ Validator الخاص بيه، وبكده موديولات الـ Features بتتبني في بيئة الـ CI/CD بالتوازي التام وبدون أي قفل تبعيات مشترك (Zero Shared Locks).\n\nوعلى مستوى بيئة تشغيل ART، الكلاسات الملموسة البسيطة بتعطي معالج الجهاز فرصة أفضل بكثير لعمل Inlining للتعليمات والتنفيذ المباشر (Devirtualization)، مقارنة بالتجريدات المعقدة اللي بتستخدم Generics و Wrappers بتزود من استهلاك كائنات الـ Boxed types في الذاكرة وتضغط على الـ Garbage Collector، وهذا الفهم العميق هو ما يميز مهندس الأندرويد الخبير القادر على حماية استقرار وسرعة بناء النظام."
    }
}

# ==========================================
# SOL-20: How would you explain SOLID trade-offs to a team overengineering a small feature?
# ==========================================
DATA["SOL-20"] = {
    "concept_en": """Explaining SOLID trade-offs to an overengineering team requires pragmatic technical leadership that balances long-term architectural hygiene with immediate product delivery velocity. SOLID principles are not dogmatic laws that must be implemented universally; they are risk-mitigation strategies designed to manage complexity in evolving, enterprise software. When junior or mid-level engineers introduce dozens of speculative interfaces, multi-layer UseCases, and abstract factories for simple CRUD screens, they incur high cognitive tax and maintenance overhead without deriving any architectural benefits. Senior leaders guide teams toward evolutionary architecture, teaching them to apply KISS and YAGNI first, scaling to full SOLID patterns only as feature volatility and domain complexity legitimately demand it.""",
    "walkthrough_en": """Simplifying an overengineered feature into a pragmatic, maintainable design:
```kotlin
// BAD OVERENGINEERED PATTERN: Excessive abstraction for a simple static FAQ screen
interface FaqAnalyticsTracker { fun track() }
interface FaqFormatter { fun format(raw: String): String }
interface FaqRepository { suspend fun getFaqs(): List<Faq> }
class GetFaqsUseCase @Inject constructor(private val repo: FaqRepository) { suspend operator fun invoke() = repo.getFaqs() }
class FaqViewModel @Inject constructor(
    private val useCase: GetFaqsUseCase,
    private val tracker: FaqAnalyticsTracker,
    private val formatter: FaqFormatter
) : ViewModel()

// ARCHITECTURAL BEST PRACTICE: Pragmatic, clean architecture scaled to feature complexity
// Single cohesive ViewModel fetching static FAQ data directly: 1 file instead of 8!
class FaqViewModel @Inject constructor(
    private val faqApi: FaqApi // Direct dependency appropriate for low-complexity, static read-only screen
) : ViewModel() {
    private val _faqs = MutableStateFlow<List<FaqItem>>(emptyList())
    val faqs: StateFlow<List<FaqItem>> = _faqs.asStateFlow()

    fun loadFaqs() {
        viewModelScope.launch {
            _faqs.value = runCatching { faqApi.fetchFaqs().map { it.toUiModel() } }.getOrDefault(emptyList())
        }
    }
}
```""",
    "short_en": """I explain SOLID trade-offs by framing them as tools for managing complexity, not moral requirements. Every abstraction introduces cognitive tax, extra files, and navigation overhead. For a simple or stable feature, overengineering with speculative interfaces and redundant UseCases wastes engineering time and slows down builds without adding value. I encourage the team to follow YAGNI and KISS first, building clean concrete code and applying advanced SOLID patterns progressively as feature complexity and business volatility genuinely demand it.""",
    "structured_en": """Guiding a team away from overengineering requires empathy, architectural pragmatism, and clear economic reasoning.
When enthusiastic engineers overengineer small features, they believe they are following 'best practices' by creating interfaces for every class, writing single-line UseCases, and engineering elaborate factories for static screens.
I address this through a structured mentorship conversation.
First, reframe the purpose of SOLID. Explain that SOLID principles are risk-mitigation mechanisms designed to counter the cost of change in volatile systems. If a screen has low business volatility (such as an About Us or static FAQ screen), the risk of change is nearly zero, making complex abstractions an unnecessary expense.
Second, highlight the real costs of over-abstraction. Show the team that every redundant interface doubles the file count, impairs IDE navigation, complicates debugging, and inflates Gradle compilation times.
Third, introduce the concept of Evolutionary Architecture and the Rule of Three. Encourage the team to start with the simplest workable design that satisfies clean coding standards (KISS and YAGNI).
As requirements evolve and true business variation emerges, the team can refactor toward full SOLID abstractions incrementally with full test coverage, ensuring engineering time delivers tangible business value.""",
    "deep_senior_en": """Under the hood, overengineering directly penalizes engineering velocity, developer onboarding time, and CI/CD build economics in production Android teams.
When a simple feature with 200 lines of functional logic is fragmented across 12 files (interfaces, implementations, mappers, delegates, and UseCases), the cognitive load required to understand the control flow skyrockets. New engineers spending hours tracing call graphs through single-implementation abstractions experience high onboarding friction.
At the build system level, unnecessary class definitions inflate the Gradle task graph. Every additional interface and Dagger component adds annotations that the Kotlin Symbol Processing (KSP) tool must inspect. In massive multi-module projects, speculative abstraction bloat noticeably degrades incremental compilation performance and dev-loop turnaround times.
Furthermore, premature abstraction impairs runtime performance. In the Android ART runtime, deeply nested layers of UseCases and delegates create chains of method forwarding, increasing stack frame depth and allocating temporary wrapper objects that add pressure to the garbage collector.
Staff engineers establish pragmatic architectural guidelines: simple CRUD screens connect ViewModels directly to Repositories, omitting intermediate UseCases unless cross-repository orchestration or complex business logic is genuinely present.
Architecture is a spectrum, and true seniority is knowing how much architecture a specific problem actually warrants. This balanced technical mindset protects teams from burning velocity on low-value architectural ceremony.""",
    "meta_ar": {
        "id": "SOL-20",
        "questionAr": "كيف تشرح مقايضات (Trade-offs) مبادئ SOLID لفريق يبالغ في هندسة ميزة برمجية بسيطة (Overengineering)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القيادة التقنية والنضج المعماري (Technical Leadership)، والقدرة على الموازنة بين المعمارية النظيفة وسرعة تسليم المنتج، وتوجيه الفريق نحو المعمارية التطورية (Evolutionary Architecture) ومبادئ KISS و YAGNI.",
        "why_it_matters_ar": "المبالغة في الهندسة تحول الميزات البسيطة كشاشات العرض الثابتة إلى كابوس من الواجهات وطبقات الـ UseCases التي تبطئ سرعة الفريق، وتزيد وقت الـ Build، وترفع التكلفة الذهنية للصيانة.",
        "worked_example_ar": "تبسيط ميزة بسيطة مبالغ في هندستها:\n```kotlin\n// كود مبالغ فيه لميزة بسيطة: إنترفيسات و UseCases لكود سطر واحد\nclass GetFaqUseCase(val repo: FaqRepo) { suspend fun invoke() = repo.get() }\n// كود براغماتي نظيف: ViewModel يتواصل مباشرة مع الـ Repository أو الـ Api\nclass FaqVM(val api: FaqApi) : ViewModel() { /* كود بسيط في ملف واحد بدل 8 ملفات */ }\n```",
        "trade_offs_ar": "الكود البسيط يقلل عدد الملفات ويسرع التطوير ويسهل فهم الكود للجدد، مع الاحتفاظ بالقدرة على التوسع المعماري عندما تتطلب الميزة ذلك فعلاً.",
        "failure_modes_ar": "التعامل مع مبادئ SOLID كقوانين دينية ملزمة في كل سطر كود، ورفض الـ PRs لمجرد أن كلاس بسيط لا يملك Interface أو UseCase.",
        "production_perspective_ar": "في الشركات الكبرى، نحدد معايير معمارية براغماتية: الشاشات البسيطة تقرأ مباشرة من الـ Repository، والـ UseCases لا تُستخرج إلا عند وجود منطق عمل مركب بين أكثر من مستودع.",
        "how_to_answer_ar": "وضح أن مبادئ SOLID هي أدوات لإدارة التعقيد (Risk Mitigation Tools) وليست قيوداً مقدسة، واشرح تكلفة التجريد الزائد: إبطاء البناء في Gradle، وزيادة الحمل الذهني وتشتيت التصفح، واعرض الحل بتطبيق مبادئ KISS و YAGNI والمعمارية التطورية التي تبدأ بسيطة وتتوسع تدريجياً.",
        "talking_points_ar": "مفهوم Evolutionary Architecture، والقيادة التقنية البراغماتية، وتكلفة التجريد الذهنية والزمنية، ومبادئ KISS و YAGNI، ومتى نتجاوز طبقة الـ UseCase لشاشات الـ CRUD البسيطة.",
        "follow_ups_ar": "- **المحاور:** \"هل تخطي طبقة الـ UseCase في شاشة CRUD بسيطة يعتبر انتهاكاً لـ Clean Architecture؟\"\n  **المرشح:** \"إطلاقاً، دليل جوجل الرسمي لمعمارية أندرويد بينص صراحة على إن طبقة الـ Domain اختيارية (Optional Layer)؛ بنستخدمها فقط لما يكون فيه بيزنس معقد أو تنسيق بين كذا Repository.\"\n\n- **المحاور:** \"كيف تقنع مهندساً جونيور متحمساً بتبسيط كوده بدون إحباطه؟\"\n  **المرشح:** \"بأثني على حرصه على كتابة كود نظيف أولاً، وبعدين أشاركه التكلفة الحقيقية: وقت الـ Build، وصعوبة التصفح، وأفهمه إن البراغماتية واختيار الحل الأنسب لحجم المشكلة هو جوهر عمل المهندس المحترف.\"",
        "self_check_ar": "هل أظهرت عقلية القيادة التقنية؟ هل وضحت تكلفة الـ Overengineering في الوقت والـ Build؟ وهل بينت متى نبسط الكود ومتى نطبق SOLID بالكامل؟",
        "references_ar": f"- [Google Guide to App Architecture: Domain Layer](https://developer.android.com/topic/architecture/domain-layer#architecture) — توثيق جوجل الرسمي بأن طبقة الدومين اختيارية.\n- [KISS and YAGNI Principles](https://martinfowler.com/bliki/Yagni.html) — مقالات مارتن فاولر حول بساطة التصميم.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "بشرح للفريق إن مبادئ SOLID هي أدوات هندسية لإدارة التعقيد وتقليل المخاطر (Risk Mitigation)، مش قواعد مقدسة لازم نطبقها في كل شاشة. كل تجريد بتعمله له ضريبة وتكلفة: بيزود عدد الملفات، ويبطئ وقت الـ Build في Gradle، وبيصعب تصفح الكود على المطورين الجدد. في الميزات البسيطة زي شاشات العرض الثابتة، خطر التغيير شبه منعدم، وبالتالي بناء واجهات وطبقات UseCases كتيرة هو إهدار للوقت. الحل هو البدء بأبسط كود نظيف يطبق مبادئ KISS و YAGNI، والتوسع في SOLID تدريجياً لما التعقيد يفرض ده فعلياً.",
        "best_answer_ar": "توجيه الفريق بعيداً عن المبالغة في الهندسة (Overengineering) بيتطلب قيادة تقنية واعية بتوازن بين نظافة الكود واقتصاديات تسليم المنتج.\n\nالمطورون المتحمسون غالباً بيبالغوا في الهندسة لأنهم معتقدين إن ده هو 'الكود الصح'، فتلاقيه في شاشة ثابتة بتعرض أسئلة شائعة (FAQ) عامل 8 ملفات: إنترفيس للـ Repository، وإنترفيس للـ Formatter، و UseCase فيه سطر واحد بينادي الداتا، ومفوض للـ Analytics. النتيجة هي تعقيد مصطنع لبيزنس في منتهى البساطة.\n\nفي نقاشي مع الفريق بركز على تلات نقاط أساسية:\nأولاً: إعادة تعريف الهدف؛ مبادئ SOLID معمولة لمواجهة التعقيد وإدارة التغييرات في الأنظمة المتغيرة بسرعة. الميزة البسيطة الثابتة مفيهاش أي تعقيد ولا مخاطر، فالتجريد هنا بيحل مشكلة مش موجودة أصلاً.\nثانياً: توضيح التكلفة الحقيقية؛ كل إنترفيس إضافي بيضاعف وقت تصفح الكود، وبيزود شغل معالجة الرموز في KSP وداجر، وبيبطل كاش Gradle وبيزود وقت الـ Build للجميع.\nثالثاً: تشجيع المعمارية التطورية (Evolutionary Architecture)؛ نبدأ بتصميم مباشر ونظيف (KISS و YAGNI)، والـ ViewModel يكلم الـ Repository مباشرة. لو الميزة كبرت في المستقبل وتطلبت دمج كذا مصدر بيانات، نقدر وقتها نستخرج UseCases ونطبق SOLID تدريجياً وبأمان وبدعم التستات.\n\nالمهندس السينيور الحقيقي مبيتباهى بعدد الواجهات والطبقات اللي كتبها، بل بقدرته على حل مشكلة البيزنس بأبسط وأوضح وأسرع تصميم ممكن.",
        "deep_answer_ar": "تحت الكابوت، المبالغة في الهندسة بتتحول لخسارة اقتصادية وتقنية مباشرة بتبطئ سرعة الفريق وترفع تكلفة البنية التحتية في أندرويد.\n\nلما ميزة بسيطة لا تتعدى 200 سطر تتوزع على 12 كلاس وملف، الحمل الذهني (Cognitive Load) المطلوب من أي مهندس عشان يفهم سريان الكود بيتضاعف. المطورين الجدد بيضيعوا ساعات طويلة في تتبع المكالمات عبر واجهات ملهاش غير تنفيذ واحد، وده بيرفع وقت الـ Onboarding للفريق بصورة غير مبررة.\n\nوعلى مستوى نظام البناء، كل كلاس وإنترفيس و UseCase بيحتاج توليد شفرة ومراجعة Annotations عبر الـ Kotlin Symbol Processing (KSP) ومكتبات الحقن زي Hilt. في المشاريع متعددة الموديولات، تضخم الكلاسات الوهمية بيزيد من وقت الـ Incremental Compilation ووقت الـ CI/CD، وده بيعطل مسار المطورين اليومي.\n\nأما على مستوى بيئة تشغيل أندرويد ART، السلسلة الطويلة من الـ UseCases والمفوضات اللي بتعيد توجيه المكالمات لبعضها (Forwarding Calls) بتزود من عمق الـ Call Stack Frames، وبتنشئ كائنات وسيطة في الذاكرة بتزود الضغط على محرك جمع القمامة (GC Pressure) بدون أي داعٍ.\n\nالمهندسون الكبار بيضعوا معايير معمارية براغماتية: شاشات الـ CRUD البسيطة بتوصل الـ ViewModel بالـ Repository مباشرة؛ حتى دليل جوجل الرسمي صرح بأن طبقة الـ Domain هي طبقة اختيارية. النضج المعماري الحقيقي هو إنك تعرف بالظبط إمتى الميزة محتاجة تجريد متقدم، وإمتى تكون البساطة هي قمة الاحترافية."
    }
}


def main():
    print(f"Elevating 10 questions in SOL (SOL-11 to SOL-20)...")
    all_valid = True
    for qid, d in sorted(DATA.items()):
        en_s = len(d["short_en"].split())
        en_st = len(d["structured_en"].split())
        en_d = len(d["deep_senior_en"].split())
        ar_q = len(d["meta_ar"]["quick_answer_ar"].split())
        ar_b = len(d["meta_ar"]["best_answer_ar"].split())
        ar_d = len(d["meta_ar"]["deep_answer_ar"].split())
        print(f"{qid}: en_s={en_s}, en_st={en_st}, en_d={en_d} | ar_q={ar_q}, ar_b={ar_b}, ar_d={ar_d}")

        if not (35 <= en_s <= 110):
            print(f"  ❌ {qid} en_short invalid: {en_s}")
            all_valid = False
        if not (100 <= en_st <= 280):
            print(f"  ❌ {qid} en_structured invalid: {en_st}")
            all_valid = False
        if not (200 <= en_d <= 650):
            print(f"  ❌ {qid} en_deep invalid: {en_d}")
            all_valid = False
        if not (35 <= ar_q <= 110):
            print(f"  ❌ {qid} ar_quick invalid: {ar_q}")
            all_valid = False
        if not (90 <= ar_b <= 280):
            print(f"  ❌ {qid} ar_best invalid: {ar_b}")
            all_valid = False
        if not (180 <= ar_d <= 650):
            print(f"  ❌ {qid} ar_deep invalid: {ar_d}")
            all_valid = False

    if not all_valid:
        print("\nPre-validation word count checks failed! Fix counts before updating files.")
        sys.exit(1)

    print("\nPre-validation word count checks passed! Updating canonical questions...")

    topic_meta = {}
    for qid, d in sorted(DATA.items()):
        ee.update_canonical_question(
            qid=qid,
            concept_en=d["concept_en"],
            walkthrough_en=d["walkthrough_en"],
            short_en=d["short_en"],
            structured_en=d["structured_en"],
            deep_senior_en=d["deep_senior_en"]
        )
        topic_meta[qid] = d["meta_ar"]

    ee.save_topic_metadata("sol_11_20", topic_meta)
    ee.merge_all_metadata()

    # Validate each question
    for qid in sorted(DATA.keys()):
        ee.validate_question(qid)

    print("\nAll 10 SOL questions (SOL-11 to SOL-20) successfully elevated and passed validation!")


if __name__ == "__main__":
    main()
