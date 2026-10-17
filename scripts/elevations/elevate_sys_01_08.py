#!/usr/bin/env python3
"""
Elevation script for SYS questions: SYS-01 to SYS-08.
Topic: Android System Design & Architecture Decisions (SYS)
Phase 4, Batch 1
"""

import os
import sys

sys.path.insert(0, os.path.abspath("scripts/elevations"))
import elevation_engine as ee

TOPIC_AR = "تصميم أنظمة ومعمارية أندرويد"
REVIEWED_DATE_AR = "تمت المراجعة والتحقق في 17 أكتوبر 2026"

DATA = {}

# ==========================================
# SYS-01: How do you begin a mobile system-design interview (requirements, scale, constraints, trade-offs)?
# ==========================================
DATA["SYS-01"] = {
    "concept_en": """A mobile system design interview differs fundamentally from backend system design. While backends prioritize queries per second, distributed database sharding, and consensus algorithms, mobile design centers on client resource scarcity, network volatility, operating system lifecycle constraints, and offline data consistency. Beginning an interview effectively requires a structured, collaborative engineering framework. In the first five to seven minutes, the engineer must clarify functional scope, defining core user journeys while explicitly bounding what is out of scope to avoid low-impact rabbit holes. Next, non-functional requirements must be established with concrete mobile metrics: offline-first versus online-only durability, cold startup latency thresholds (such as under 400 milliseconds), disk cache size ceilings (such as 150 megabytes), battery and cellular data constraints, and target hardware tiers (such as low-end Android devices with two gigabytes of RAM). Before selecting any libraries or third-party frameworks, the high-level architecture must be established around unidirectional data flow: UI state holders observing reactive database streams, domain use cases orchestrating business rules, and repositories mediating between local persistence and remote network APIs. Only after aligning on data flow and state ownership should the discussion drill down into complex subsystems, failure modes, and architectural trade-offs.""",
    "walkthrough_en": """Structuring the mobile system design scaffold with clear boundaries and domain contracts:
```kotlin
// 1. Domain contracts establishing repository boundaries before technical implementations
interface FeedRepository {
    // Local single source of truth streaming reactive UI state from disk
    fun getFeedStream(): Flow<PagingData<FeedItem>>

    // Explicit background synchronization contract with configurable strategy
    suspend fun syncFeed(strategy: SyncStrategy): Result<SyncSummary>
}

sealed interface SyncStrategy {
    data object CacheFirst : SyncStrategy
    data object NetworkFirst : SyncStrategy
    data class DeltaSync(val lastSyncTimestampMs: Long) : SyncStrategy
}

// 2. Unidirectional UI State modeling to handle partial failures and offline modes
data class FeedUiState(
    val isLoading: Boolean = false,
    val isOfflineMode: Boolean = false,
    val pendingUploadsCount: Int = 0,
    val bannerMessage: String? = null
)

// 3. User intent actions dispatched to the state machine
sealed interface FeedUserAction {
    data object RefreshTriggered : FeedUserAction
    data class ItemLiked(val itemId: String) : FeedUserAction
    data class RetrySyncRequested(val failedBatchId: String) : FeedUserAction
}
```""",
    "short_en": """We begin a mobile system design interview by clarifying functional boundaries and mobile-specific constraints before sketching architecture or picking libraries. We define core user journeys, latency budgets, offline expectations, battery limits, and budget device targets. Then we sketch unidirectional data flow from presentation to persistence, proactively addressing process death, network volatility, and local data consistency.""",
    "structured_en": """A disciplined mobile system design interview begins with collaborative problem scoping rather than immediate architecture diagrams.
In the first five minutes, I clarify primary user journeys and establish what is deliberately out of scope to prevent unproductive diversions.
Next, I establish mobile-specific non-functional requirements that directly dictate architectural decisions: whether the application must be offline-first, the acceptable latency threshold for screen rendering, cache size limits, and the minimum hardware envelope like budget Android devices with two gigabytes of RAM.
Once requirements and scale are bounded, I establish high-level boundaries showing unidirectional data flow: UI state holders observing reactive database streams, domain interactors executing business policies, and repositories coordinating remote APIs with local persistence.
Only after aligning on data flow and state ownership do we dive deep into complex bottlenecks like background synchronization conflict resolution, payload compaction, and process death recovery, concluding with explicit failure modes and architectural trade-offs.""",
    "deep_senior_en": """What distinguishes a staff-level mobile engineer in system design is recognizing that mobile clients run inside an untrusted, resource-constrained, and hostile operating environment.
Unlike backend nodes that run in controlled server clusters, Android applications face spontaneous process termination by the Low Memory Killer, battery preservation restrictions imposed by Doze mode, and hostile network handoffs between cellular towers and Wi-Fi.
When opening the interview, I proactively articulate these runtime realities before the interviewer prompts me.
I frame the client database as the local single source of truth and the remote network as an asynchronous synchronization mechanism.
This immediately sets up a discussion around data durability, write queues, and idempotent mutations.
Furthermore, I establish operational trade-offs upfront.
Choosing an offline-first Room architecture with delta synchronization delivers instant UI rendering and zero offline perceived latency, but introduces substantial complexity around distributed conflict resolution, database schema migrations, and sync queuing overhead.
Conversely, an online-only cache-aside strategy simplifies state management and cuts client storage footprint, but degrades user experience during poor connectivity and increases backend request volume.
To complete the system envelope, I establish operational monitoring metrics including ANR rate thresholds under zero point four percent, cold startup latency targets under four hundred milliseconds, and automated contract testing with backend teams to validate schema evolution before shipping client releases.
Framing every decision around concrete trade-offs, operational failure modes, and client resource budgets demonstrates production maturity.""",
    "meta_ar": {
        "id": "SYS-01",
        "questionAr": "كيف تبدأ مقابلة تصميم أنظمة الموبايل (المتطلبات، المقاييس، القيود، والمفاضلات) باحترافية؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على قيادة مقابلة تصميم الأنظمة بشكل منظم، وتحديد المتطلبات الوظيفية وغير الوظيفية الخاصة بالموبايل، ورسم تدفق البيانات قبل اختيار التقنيات، ومناقشة المفاضلات الهندسية ونقاط الفشل.",
        "concept_ar": "مقابلة تصميم أنظمة الموبايل تختلف جذرياً عن الـ Backend؛ فبدلاً من التركيز على الـ QPS والـ Sharding، ينصب التركيز على قيود أجهزة الموبايل (الذاكرة المحدودة، استهلاك البطارية، انقطاع الشبكة، وموت العمليات في الخلفية). تبدأ المقابلة الناجحة بتوضيح نطاق العمل وتحديد حالات الاستخدام الأساسية واستبعاد الميزات الثانوية، ثم قياس المتطلبات غير الوظيفية بدقة، ورسم المعمارية الكلية بتدفق أحادي للبيانات، قبل الغوص في تفاصيل المزامنة وحل النزاعات.",
        "walkthrough_ar": "هيكلة إطار عمل مقابلة الـ System Design في كود معماري يوضح فصل المسؤوليات والـ High-Level Contracts:\n```kotlin\n// 1. تحديد الـ Domain Models والـ Contracts الصريحة قبل الخوض في التفاصيل:\ninterface FeedRepository {\n    fun getFeedStream(): Flow<PagingData<FeedItem>>\n    suspend fun syncFeed(strategy: SyncStrategy): Result<SyncSummary>\n}\n\nsealed interface SyncStrategy {\n    data object CacheFirst : SyncStrategy\n    data object NetworkFirst : SyncStrategy\n    data class DeltaSync(val lastSyncTimestampMs: Long) : SyncStrategy\n}\n\n// 2. نمذجة حالات الواجهة الصريحة (Unidirectional Data Flow):\ndata class FeedUiState(\n    val isLoading: Boolean = false,\n    val isOfflineMode: Boolean = false,\n    val pendingUploadsCount: Int = 0,\n    val bannerMessage: String? = null\n)\n```",
        "why_it_matters_ar": "البدء الخاطئ في المقابلة بكتابة كود عشوائي أو رسم جداول قواعد البيانات يضيع الوقت ويظهر نقص الخبرة القيادية؛ المقابل يبحث عن مهندس يستطيع فهم المشكلة الكبرى وتحديد القيود الحرجة وقيادة النقاش نحو حلول متوازنة.",
        "worked_example_ar": "نموذج وثيقة قرار تصميم معماري مختصرة تحدد القيود الأساسية:\n```kotlin\ndata class SystemDesignBrief(\n    val isOfflineFirstRequired: Boolean,\n    val maxColdStartLatencyMs: Long,\n    val maxDiskCacheMegabytes: Int,\n    val targetMemoryTier: DeviceMemoryTier,\n    val acceptablePartialFailure: Boolean\n)\n\nenum class DeviceMemoryTier { LOW_END_2GB, MID_RANGE_4GB, FLAGSHIP_8GB }\n```",
        "trade_offs_ar": "طرح أسئلة كثيرة بلا هدف يستهلك وقت المقابلة، لذا يجب حصر الأسئلة في القيود التي تغير معمارية النظام فعلياً. اختيار معمارية Offline-First يمنح سرعة فائقة لكنه يعقد حل نزاعات البيانات والترقيات، بينما الاعتماد الكامل على الشبكة يبسط التطبيق لكنه يجعله عاجزاً عند ضعف الاتصال.",
        "failure_modes_ar": "افتراض اتصال دائم بالإنترنت مما يفشل التطبيق في البيئات الحقيقية، أو اعتبار انتهاء مهلة الشبكة (Timeout) فشلاً نهائياً للعملية في معاملات الدفع، أو رسم مربعات عامة دون تحديد من يمتلك البيانات وكيف يتعافى التطبيق من موت العملية (Process Death).",
        "production_perspective_ar": "في تطبيقات التجارة العالمية، نفصل التصفح كـ Offline-First مدعوماً بـ Room مع مزامنة تفاضلية، بينما نحصر خطوة إتمام الطلب والدفع كـ Server-Authoritative عبر الشبكة مع مفاتيح Idempotency وتتبع دقيق لاستهلاك الذاكرة ومعدلات استقرار التطبيق.",
        "how_to_answer_ar": "ابدأ بطرح أسئلة لتحديد النطاق الأساسي وتوضيح ما هو خارج النطاق، ثم حدد قيود الموبايل الأربعة: الشبكة، والبطارية، والذاكرة، وموت العملية. ارسم تدفق البيانات الأحادي من الواجهة إلى قاعدة البيانات والسيرفر، ثم تعمق في التحدي الأكبر وناقش المفاضلات ونقاط الفشل بثقة.",
        "talking_points_ar": "الفرق بين تصميم الموبايل وتصميم السيرفرات، وإدارة قيود الذاكرة والبطارية، ونمط Single Source of Truth، وموت العمليات في أندرويد، ومفاضلات Offline-First مقابل Online-Only.",
        "follow_ups_ar": "- **المحاور:** \"ما هو أكبر خطأ يقع فيه المهندسون عند بدء مقابلة تصميم نظام موبايل؟\"\n  **المرشح:** \"القفز فوراً لاختيار المكتبات ورسم كلاسات الواجهة وقواعد البيانات قبل الاتفاق على متطلبات العمل وقيود الشبكة ومقاييس الأداء الأساسية.\"\n\n- **المحاور:** \"كيف تتصرف إذا طرح عليك المحاور متطلبات مبهمة عمداً؟\"\n  **المرشح:** \"أصرح بافتراضاتي الهندسية بوضوح وبصوت مسموع، وأسأل المقابل عما إذا كانت هذه الافتراضات مناسبة لمسار النقاش وأسجلها على اللوح كمرجع.\"",
        "self_check_ar": "هل وضحت القيود الخاصة بالموبايل بدقة؟ هل بنيت تدفق بيانات أحادي واضح؟ وهل ناقشت المفاضلات بين الحلول المختلفة؟",
        "references_ar": f"- [Guide to app architecture](https://developer.android.com/topic/architecture) — دليل جوجل الرسمي لمعمارية وتصميم تطبيقات أندرويد الحديثة.\n- [Mobile System Design Primer](https://github.com/mfonville/mobile-system-design-primer) — مرجع شامل لمقابلات تصميم أنظمة الموبايل والقيود الهندسية.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "نبدأ مقابلة تصميم أنظمة الموبايل بتوضيح المتطلبات الوظيفية وتحديد ما هو خارج النطاق في أول خمس دقائق، ثم نحدد قيود الموبايل الجوهرية مثل العمل دون إنترنت واستهلاك البطارية ومحدودية ذاكرة الأجهزة الضعيفة. بعد ذلك نرسم تدفق البيانات الأحادي من واجهة المستخدم إلى مخزن البيانات المحلي وقنوات الشبكة، ونقود النقاش نحو التعامل مع موت العمليات وتذبذب الاتصال والمفاضلات المعمارية.",
        "best_answer_ar": "البداية الاحترافية لمقابلة تصميم أنظمة الموبايل تعتمد على قيادة مهندس سينيور للنقاش دون تسرع في رسم الواجهات أو اختيار التقنيات.\n\nفي الدقائق الأولى، أحدد نطاق المشكلة بدقة عبر توضيح رحلة المستخدم الأساسية والاتفاق مع المقابل على ما يقع خارج النطاق لتجنب تشتيت الوقت. بعد ذلك، أنتقل لتحديد المتطلبات غير الوظيفية الحاكمة في بيئة الموبايل: هل التطبيق Offline-First أم يعتمد على الشبكة، وما هو الحد الأقصى المسموح به لزمن بدء التشغيل وحجم الكاش على القرص، وما هي مواصفات الأجهزة المستهدفة في الإنتاج.\n\nبمجرد الاتفاق على النطاق والقيود، أرسم معمارية تدفق البيانات الكلية: واجهات عرض تعتمد على StateFlow، وطبقة Domain UseCases لمعالجة قواعد العمل، وطبقة Repository تمثل مصدر الحقيقة الوحيد وتربط بين قاعدة بيانات Room وواجهات الـ REST أو gRPC. وبعد استقرار المعمارية الكلية، نتعمق في التحدي الأكبر مثل مزامنة البيانات وحل التعارضات، ونختم بمناقشة سيناريوهات الفشل والمفاضلات الهندسية الواعية.",
        "deep_answer_ar": "المهندس في مستوى Staff يميز مقابلة الموبايل بإدراك أن أجهزة المستخدمين بيئة غير موثوقة ومحدودة الموارد وتخضع لإدارة صارمة من نظام التشغيل.\n\nعلى عكس السيرفرات التي تعمل في بيئات سحابية مستقرة، يواجه تطبيق أندرويد إنهاء مفاجئ للعملية بواسطة الـ Low Memory Killer، وقيوداً على الاتصال والبطارية تفرضها ميزات Doze Mode، بالإضافة إلى التبديل المستمر بين شبكات المحمول والواي فاي. لذلك أبدأ بطرح هذه الحقائق كركائز أساسية للتصميم قبل أن يسألني المقابل عنها.\n\nأطرح قاعدة البيانات المحلية كمصدر وحيد للحقيقة للواجهة، بينما أتعامل مع الشبكة كقناة مزامنة غير متزامنة، وهو ما يفتح المجال فوراً لمناقشة طوابير الكتابة المؤجلة ومفاتيح عدم تكرار العمليات Idempotency Keys لضمان عدم فقدان بيانات المستخدم. وأبرز المفاضلات الهندسية بصراحة؛ فاختيار معمارية Offline-First يمنح المستخدم تجربة فورية وسلسة حتى في الأنفاق، لكنه يفرض تعقيداً كبيراً في فض النزاعات وترقية الجداول وتدبير المساحة التخزينية.\n\nولإحكام تصميم النظام، أطرح مقاييس المراقبة التشغيلية مثل الحفاظ على معدل ANR أقل من 0.4% ومعدل بدء تشغيل بارد أقل من 400 جزء من الثانية، مع تطبيق اختبارات العقود مع فرق السيرفر للتحقق من تطور المخططات البرمجية. المقارنة بين هذه القرارات وتوضيح نقاط الفشل في الإنتاج يعكس نضجاً هندسياً رفيعاً."
    }
}

# ==========================================
# SYS-02: Design a scalable multi-feature Android application.
# ==========================================
DATA["SYS-02"] = {
    "concept_en": """Designing a scalable multi-feature Android application for dozens of engineers requires strict modularization, clear data ownership, and decoupled navigation. A monolithic codebase creates severe build bottlenecks, merge conflicts, and tight cross-team coupling. Modern enterprise architecture organizes code into three distinct tiers: feature modules containing UI and presentation logic, core infrastructure modules (networking, database, security, design system tokens), and domain API contract modules. Feature modules never depend directly on sibling feature implementations; instead, they communicate through abstract API contracts or event-driven navigation routers. This separation decouples compile-time graphs, enables fine-grained Gradle build caching, allows teams to operate with high velocity, and ensures that feature modules can be compiled and tested in standalone sample runner applications.""",
    "walkthrough_en": """Implementing decoupled multi-feature API/Impl architecture and navigation contract:
```kotlin
// 1. Feature API module (:feature:checkout-api) exposing contracts only
interface CheckoutFeatureApi {
    fun getCheckoutDestination(orderId: String): NavigationDestination
    suspend fun isUserEligibleForInstantCheckout(userId: String): Boolean
}

data class NavigationDestination(val route: String)

// 2. Feature Implementation module (:feature:checkout-impl) keeping logic private
class CheckoutFeatureApiImpl @Inject constructor(
    private val checkoutRepository: CheckoutRepository
) : CheckoutFeatureApi {
    override fun getCheckoutDestination(orderId: String): NavigationDestination {
        return NavigationDestination(route = "checkout/flow/$orderId")
    }

    override suspend fun isUserEligibleForInstantCheckout(userId: String): Boolean {
        return checkoutRepository.hasValidPaymentMethod(userId)
    }
}

// 3. Central Application Graph (:app) assembling implementations via Dagger/Hilt
@Module
@InstallIn(SingletonComponent::class)
abstract class FeatureBindingsModule {
    @Binds
    @Singleton
    abstract fun bindCheckoutApi(impl: CheckoutFeatureApiImpl): CheckoutFeatureApi
}
```""",
    "short_en": """We design a scalable multi-feature application by separating features into API and implementation modules to eliminate cross-feature compile-time coupling. Sibling features communicate through abstract domain contracts or deep links rather than direct references. Core shared infrastructure like networking, persistence, and design system tokens reside in stable foundational modules, enabling parallel Gradle compilation, clear team code ownership, and rapid feature development.""",
    "structured_en": """Designing a multi-feature application that scales across dozens of engineers requires enforcing architectural decoupling, strict data ownership, and build pipeline optimization.
We organize the codebase into three horizontal layers and multiple vertical feature slices.
Vertically, each business capability like authentication, search, or checkout is isolated into its own module pair: a lightweight API module exposing interfaces and models, and an implementation module containing private UI and logic.
Sibling feature implementations never depend directly on each other.
When the cart screen needs to invoke checkout, it communicates via the checkout API contract or deep-link navigation, completely breaking circular compilation dependencies.
Horizontally, we provide stable foundational modules containing the network client, local storage, security utilities, and the Compose design system.
Dependency injection dynamically binds implementations into the application module at the top of the dependency graph.
This structure enables clear code ownership using CODEOWNERS files, accelerates local and CI build times through fine-grained Gradle task caching, and prevents unintended architectural regressions across growing feature teams.""",
    "deep_senior_en": """At scale, the hardest challenges in multi-feature architecture are dependency explosion, transitive ABI changes, and fragmented application state.
When dozens of teams modify shared code, modifying a single core module invalidates Gradle caches across the entire project, inflating build times from minutes to half an hour.
To maintain build health, we strictly enforce the API and Implementation module pattern, using Gradle api dependencies exclusively for exported interfaces and implementation dependencies for internal libraries.
Furthermore, data ownership must be strictly localized.
A common anti-pattern is sharing a centralized, mutable database entity across multiple feature modules, which leads to unpredictable race conditions and tight schema coupling.
Instead, each feature owns its persistence boundary or interacts through an authoritative domain repository.
Navigation between features is abstracted through a central navigation contract or deep-link URI router, allowing feature teams to develop and test their flows using standalone sample apps without compiling the full monolithic application.
For runtime state management, we adopt unidirectional data flow within each feature, exposing immutable StateFlow streams and encapsulating side effects within dedicated coroutine scopes tied to the feature lifecycle.
We also configure a distributed remote Gradle build cache across developer machines and continuous integration workers, ensuring that clean builds achieve hit rates above eighty percent on unmodified feature modules.
This architecture guarantees high developer velocity, modular testability, and operational stability in enterprise production environments.""",
    "meta_ar": {
        "id": "SYS-02",
        "questionAr": "كيف تصمم تطبيق أندرويد ضخم متعدد الميزات (Scalable Multi-Feature) يدعم عشرات الفرق البرمجية؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على تقسيم التطبيق إلى وحدات برمجية مستقلة، وفصل واجهات الـ API عن التنفيذ، وإدارة التبعيات، وتفادي الاعتماد الدائري، وتسريع أزمنة بناء Gradle في المشروعات الضخمة.",
        "concept_ar": "تصميم التطبيقات متعددة الميزات لفرق هندسية متعددة يتطلب اعتماد نمط تقسيم الوحدات (Modularization) الصارم بنمط API/Impl؛ حيث يحتوي موديول الـ API على العقود والنماذج المجردة، بينما يحفظ موديول الـ Implementation تفاصيل الشاشات والكود الداخلي. تتواصل الميزات أفقياً عبر واجهات مجردة أو عبر التوجيه بالروابط العميقة، بينما توضع المكونات المشتركة كالشبكات والتصميم في موديولات أساسية مستقرة، مما يعزل تأثير التعديلات ويسرع الكاش لـ Gradle.",
        "walkthrough_ar": "تطبيق نمط عزل الميزات عبر موديولات الـ API والـ Implementation مع ربط الـ Navigation:\n```kotlin\n// موديول العقد فقط :feature:checkout-api\ninterface CheckoutFeatureApi {\n    fun getCheckoutDestination(orderId: String): NavigationDestination\n    suspend fun isUserEligibleForInstantCheckout(userId: String): Boolean\n}\n\ndata class NavigationDestination(val route: String)\n\n// موديول التنفيذ الداخلي :feature:checkout-impl\nclass CheckoutFeatureApiImpl @Inject constructor(\n    private val checkoutRepository: CheckoutRepository\n) : CheckoutFeatureApi {\n    override fun getCheckoutDestination(orderId: String) = NavigationDestination(\"checkout/flow/$orderId\")\n    override suspend fun isUserEligibleForInstantCheckout(userId: String) = checkoutRepository.hasValidPaymentMethod(userId)\n}\n```",
        "why_it_matters_ar": "التطبيقات المتجانسة (Monolith) في الشركات الكبرى تؤدي لبطء البناء الذي يستغرق نصف ساعة وتضارب دمج الكود بين عشرات المطورين؛ العزل المعماري السليم يتيح لكل فريق التطوير والاختبار والنشر باستقلالية وسرعة تامة.",
        "worked_example_ar": "هيكل شجرة الاعتماديات لتطبيق متعدد الميزات يمنع الاعتماد المباشر بين الموديولات:\n```text\n:app (Application Root - تجميع التبعيات)\n  ├── :feature:cart:impl -> :feature:checkout:api\n  ├── :feature:checkout:impl -> :core:network, :core:database\n  └── :core:design-system\n```",
        "trade_offs_ar": "تطبيق Monolith بسيط في البداية ولا يتطلب إعدادات Gradle معقدة ولكنه ينهار مع زيادة حجم الفريق. بينما الـ Multi-Module يزيد من التعقيد المبدئي وإدارة نصوص Gradle، لكنه يوفر سرعة بناء مذهلة بفضل الكاش والتوازي وعزل المسؤوليات.",
        "failure_modes_ar": "الاعتماد الدائري بين الميزات (Circular Dependencies)، أو مشاركة جداول قاعدة البيانات ذاتها بين فرق مختلفة مما يسبب سباق البيانات، أو جعل كل الموديولات تعتمد على موديول عام ضخم يسمى core-utils يؤدي لإلغاء كاش Gradle بالكامل عند أي تعديل تافه.",
        "production_perspective_ar": "في الشركات الكبرى، ننشئ تطبيقات مصغرة (Sample Apps) لكل ميزة بحيث يستطيع مطور ميزة الدفع تشغيل ميزته بمفردها واختبارها في خمس ثوانٍ دون الحاجة لتجميع باقي التطبيق الضخم، مع فرض قواعد CODEOWNERS في Git لمنع التعديل غير المصرح به.",
        "how_to_answer_ar": "قسم الإجابة إلى ثلاث طبقات: طبقة الميزات الرأسية بنمط API و Impl، وطبقة البنية التحتية الأفقية المشتركة، وطبقة الـ App المجمعة. وضح كيفية انتقال المستخدم بين الميزات دون اعتماد كودي مباشر، واشرح أثر ذلك على تحسين أزمنة بناء Gradle وتقليل تضارب الكود.",
        "talking_points_ar": "نمط API/Impl Modules، وموجهات التنقل (Deep Linking و NavGraphs)، وإدارة كاش Gradle، وفصل ملكية البيانات، وتطبيقات العينات (Sample Apps).",
        "follow_ups_ar": "- **المحاور:** \"كيف تمنع ميزة العربة (Cart) من الاعتماد البرمجي المباشر على ميزة الدفع (Checkout)؟\"\n  **المرشح:** \"ميزة العربة تعتمد فقط على موديول العقد `:feature:checkout-api` وتستدعي واجهة مجردة، بينما التنفيذ الفعلي يتم حقنه في موديول التطبيق الرئيسي `:app` عبر Hilt أو يتم التوجيه عبر Deep Link.\"\n\n- **المحاور:** \"ما هي مشكلة وجود موديول `core` أو `common` ضخم يحتوي على كل شيء؟\"\n  **المرشح:** \"أي تغيير بحرف واحد داخله يبطل كاش الـ ABI لكل موديولات المشروع ويجبر Gradle على إعادة تجميع كل شيء؛ الحل هو تفتيته لموديولات دقيقة مثل `:core:network` و`:core:database`.\"",
        "self_check_ar": "هل وضحت كيفية كسر الاعتماد الدائري بين الميزات؟ هل فرقت بين موديولات الـ API والـ Impl؟ وهل بينت أثر الهيكلة على سرعة البناء في Gradle؟",
        "references_ar": f"- [Guide to Android app modularization](https://developer.android.com/topic/modularization) — وثيقة جوجل الرسمية حول تقسيم تطبيقات أندرويد المعقدة.\n- [Modularizing Android Applications (Dropbox Tech Blog)](https://dropbox.tech/mobile) — تجارب دروب بوكس في هندسة وتوسيع التطبيقات الضخمة.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "نصمم التطبيق الضخم متعدد الميزات بتقسيم كل ميزة إلى زوج من الوحدات: موديول API خفيف يعرض العقود والنماذج المجردة، وموديول Implementation يحتوي على كود الواجهة والمنطق الداخلي. الميزات لا تعتمد على بعضها برمجياً بل تتواصل عبر الروابط العميقة أو العقود، بينما ترقد البنية التحتية المشتركة كالشبكات وقواعد البيانات في موديولات أساسية دقيقة، مما يسرع بناء Gradle ويمنع تضارب الكود بين الفرق.",
        "best_answer_ar": "تصميم تطبيق أندرويد ضخم يعمل عليه عشرات المهندسين يتطلب اعتماد استراتيجية تجزئة صارمة تعزل نطاقات العمل وتحافظ على صحة البناء.\n\nنقسم التطبيق رأسياً إلى ميزات مستقلة مثل الدفع والبحث والحساب الشخصي، حيث تتكون كل ميزة من موديولين: الأول هو API Module يحتوي فقط على الواجهات ونماذج البيانات العامة، والثاني هو Impl Module يحتوي على كود Jetpack Compose والـ ViewModels ولا يراه أحد خارج الميزة. إذا احتاجت صفحة العربة فتح شاشة الدفع، فإنها لا تعتمد على كود الدفع مباشرة، بل تستدعي واجهة مجردة من موديول الـ API أو تطلق حدث تنقل عبر Deep Link، وهو ما يكسر الاعتماد الدائري تماماً.\n\nأفقياً، نوفر موديولات بنية تحتية مستقرة ومتخصصة تشمل عميل الشبكة وقاعدة البيانات المحلية ونظام التصميم Design System. ويقوم موديول التطبيق الرئيسي في أعلى الهرم بربط كل هذه التطبيقات وحقن التبعيات عبر Hilt. هذه المعمارية تضمن أقصى استفادة من كاش Gradle التزايدي، وتتيح لكل فريق تشغيل تطبيقه التجريبي Sample App الخاص به دون الحاجة لتجميع كامل المشروع، مما يرفع إنتاجية الفرق بشكل هائل.",
        "deep_answer_ar": "التحدي الحقيقي في المعماريات متعددة الميزات في الشركات الكبرى يكمن في إدارة انفجار التبعيات وتجنب كسر كاش الـ ABI الخاص بـ Gradle.\n\nعندما تعتمد الموديولات على بعضها بكلمة `api` بدلاً من `implementation`، فإن أي تعديل طفيف في دالة خاصة يمتد كدومينو عبر المشروع ويجبر Gradle على إعادة ترجمة عشرات الموديولات، مما يرفع زمن البناء من ثوانٍ إلى نصف ساعة. لذلك نلزم الفرق بنمط API/Impl الصارم؛ فموديول الـ API نادراً ما يتغير ويوفر عقداً ثابتاً، مما يسمح للفرق بالتطوير بالتوازي التام.\n\nوعلى صعيد ملكية البيانات، يعد مشاركة جداول قاعدة البيانات ذاتها بين فرق متعددة خطأ فادحاً يسبب سباق العمليات وتلف البيانات. الحل السليم هو أن تمتلك كل ميزة قاعدة بياناتها أو مستودعها الخاص، وتشارك فقط كيانات النطاق المجردة. أما بالنسبة للتنقل بين الشاشات، فنعتمد موجه تنقل مركزي يتعامل مع الروابط العميقة، مما يتيح تشغيل ميزة معينة كـ Dynamic Feature يتم تنزيلها عند الطلب لتقليل حجم الـ APK، مع استخدام ملفات CODEOWNERS في نظام التحكم بالإصدار لفرض الرقابة والمراجعة الصارمة على حدود الوحدات البرمجية المشتركة.\n\nكما نفعل الكاش البعيد المشترك (Remote Build Cache) لخوادم الـ CI ومطوري الفريق، مما يرفع نسبة إصابة الكاش إلى أكثر من 80% ويجعل زمن بناء الوحدات غير المعدلة يقترب من الصفر عملياً."
    }
}

# ==========================================
# SYS-03: Design login, session management, and secure token refresh.
# ==========================================
DATA["SYS-03"] = {
    "concept_en": """Designing enterprise mobile authentication requires defense-in-depth security coupled with race-safe concurrency controls. Access tokens are short-lived JSON Web Tokens (JWTs) stored securely in hardware-backed storage (EncryptedSharedPreferences backed by Android Keystore), while refresh tokens are longer-lived credentials used exclusively to issue new access tokens. The primary architectural challenge is handling concurrent HTTP requests encountering HTTP 401 Unauthorized errors simultaneously. Without synchronization, multiple threads trigger redundant token refresh network calls, which invalidates the refresh token if the backend implements refresh token rotation. The production solution employs an OkHttp Authenticator combined with a coroutine Mutex to serialize refresh requests, updating the shared session state atomically and retrying queued requests seamlessly with the newly issued token.""",
    "walkthrough_en": """Implementing race-safe token refresh with OkHttp Authenticator, Mutex, and Keystore storage:
```kotlin
// 1. Thread-safe Session Manager backed by Android Keystore
class SessionManager @Inject constructor(
    private val encryptedPrefs: SharedPreferences
) {
    private val mutex = Mutex()
    private val _authState = MutableStateFlow<AuthStatus>(AuthStatus.Initial)
    val authState: StateFlow<AuthStatus> = _authState.asStateFlow()

    fun getAccessToken(): String? = encryptedPrefs.getString("KEY_ACCESS_TOKEN", null)
    fun getRefreshToken(): String? = encryptedPrefs.getString("KEY_REFRESH_TOKEN", null)

    suspend fun updateTokens(accessToken: String, refreshToken: String) {
        mutex.withLock {
            encryptedPrefs.edit()
                .putString("KEY_ACCESS_TOKEN", accessToken)
                .putString("KEY_REFRESH_TOKEN", refreshToken)
                .apply()
            _authState.value = AuthStatus.Authenticated(accessToken)
        }
    }

    suspend fun clearSession() {
        mutex.withLock {
            encryptedPrefs.edit().clear().apply()
            _authState.value = AuthStatus.Unauthenticated
        }
    }
}

// 2. OkHttp Authenticator serializing concurrent 401 recovery
class TokenAuthenticator @Inject constructor(
    private val sessionManager: SessionManager,
    private val authApiProvider: Provider<AuthApiService>
) : Authenticator {
    private val refreshMutex = Mutex()

    override fun authenticate(route: Route?, response: Response): Request? {
        val currentToken = sessionManager.getAccessToken() ?: return null
        
        // Fast-path: check if another thread already refreshed the token
        val requestToken = response.request.header("Authorization")?.removePrefix("Bearer ")
        if (requestToken != currentToken) {
            return response.request.newBuilder()
                .header("Authorization", "Bearer $currentToken")
                .build()
        }

        return runBlocking {
            refreshMutex.withLock {
                val latestToken = sessionManager.getAccessToken()
                if (latestToken != currentToken && latestToken != null) {
                    return@withLock response.request.newBuilder()
                        .header("Authorization", "Bearer $latestToken")
                        .build()
                }

                val refreshToken = sessionManager.getRefreshToken() ?: return@withLock null
                val refreshResult = authApiProvider.get().refreshToken(RefreshTokenRequest(refreshToken))

                if (refreshResult.isSuccessful && refreshResult.body() != null) {
                    val tokens = refreshResult.body()!!
                    sessionManager.updateTokens(tokens.accessToken, tokens.refreshToken)
                    response.request.newBuilder()
                        .header("Authorization", "Bearer ${tokens.accessToken}")
                        .build()
                } else {
                    sessionManager.clearSession()
                    null // Abort retries and trigger login navigation
                }
            }
        }
    }
}
```""",
    "short_en": """We design session management using short-lived access tokens and longer-lived refresh tokens stored in EncryptedSharedPreferences backed by Android Keystore. For race-safe token refresh, we use an OkHttp Authenticator with a Mutex to serialize concurrent 401 responses. Only the first request triggers the refresh API call; queued requests wait for the new access token and retry seamlessly without duplicate authentication calls or user interruption.""",
    "structured_en": """A production-grade mobile authentication system must guarantee cryptographic credential security, seamless user experience, and race-safe token refreshing.
We store sensitive JWT access and refresh tokens in EncryptedSharedPreferences, where encryption keys are managed by the hardware-backed Android Keystore.
Our networking layer utilizes OkHttp interceptors and an Authenticator.
When an API call returns HTTP 401 Unauthorized, OkHttp delegates recovery to the Authenticator.
Because multiple parallel network calls can fail simultaneously, we guard the refresh routine with a coroutine Mutex or synchronized lock.
The first failing request acquires the lock, verifies whether another thread already refreshed the token, and if not, dispatches a refresh request using the refresh token.
Once a new token pair arrives, we persist it atomically and release the lock.
The pending requests resume, updating their Authorization headers with the new token and executing without failure.
If the refresh token itself is expired or revoked, the Authenticator triggers an unauthenticated session event, clearing local credentials and navigating the user securely to the login screen.""",
    "deep_senior_en": """Under the hood, token refresh architectures must anticipate refresh token rotation, process termination, and background synchronization failures.
When backends implement refresh token rotation for enhanced security, issuing a refresh request immediately invalidates the previous refresh token.
If two concurrent mobile network requests trigger duplicate refresh calls with the old refresh token, the second call will be rejected by the backend as a replay attack, causing an unintended session termination.
To prevent this, our Authenticator checks if the request's Authorization header already contains an outdated token compared to the current in-memory token.
If another thread already completed a refresh, the Authenticator retries immediately with the existing fresh token without making another network call.
If a refresh is required, the Mutex ensures strictly one in-flight refresh request.
Furthermore, we decouple the authentication state machine into a reactive SessionManager exposing a StateFlow of AuthStatus to the presentation layer.
When a refresh permanently fails with HTTP 400 or 403, SessionManager wipes cached user data from Room and Keystore, cancels in-flight background sync jobs in WorkManager, and emits an unauthenticated state that routes the UI to authentication.
For high-assurance banking features, we wrap the access token decryption inside a BiometricPrompt CryptoObject, ensuring that credentials cannot be retrieved from hardware Keystore without physical fingerprint or facial authorization.
This guarantees total data isolation between user sessions on shared devices.""",
    "meta_ar": {
        "id": "SYS-03",
        "questionAr": "كيف تصمم نظام مصادقة وإدارة جلسات وتجديد آمن للتوكنز (Session Management & Token Refresh)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على تأمين بيانات الاعتماد في العتاد، وتصميم دورة حياة الجلسات، وحل سباق العمليات (Race Conditions) عند تجديد التوكنات المتزامنة بواسطة OkHttp Authenticator و Mutex.",
        "concept_ar": "إدارة جلسات المصادقة في تطبيقات الإنتاج تتطلب تخزين توكنات الوصول (Access Tokens) وتوكنات التجديد (Refresh Tokens) في EncryptedSharedPreferences المدعومة بـ Android Keystore. المشكلة الهندسية الكبرى تكمن في انطلاق عدة طلبات شبكية بالتوازي وحصولها على خطأ 401 في نفس اللحظة؛ فإذا حاول كل طلب تجديد التوكن منفرداً، ستفشل الجلسة بسبب تقنية تدوير التوكنات (Token Rotation). الحل يكمن في استخدام OkHttp Authenticator محمي بـ Mutex لمزامنة التجديد وتحديث الطلبات المنتظرة تلقائياً.",
        "walkthrough_ar": "تطبيق نمط تجديد التوكنات الآمن ضد سباق العمليات باستخدام OkHttp Authenticator و Mutex:\n```kotlin\nclass TokenAuthenticator @Inject constructor(\n    private val sessionManager: SessionManager,\n    private val authApi: Provider<AuthApiService>\n) : Authenticator {\n    private val mutex = Mutex()\n\n    override fun authenticate(route: Route?, response: Response): Request? {\n        val currentToken = sessionManager.getAccessToken() ?: return null\n        // التحقق مما إذا كان طلب آخر قد أتم التجديد بالفعل\n        if (response.request.header(\"Authorization\") != \"Bearer $currentToken\") {\n            return response.request.newBuilder().header(\"Authorization\", \"Bearer $currentToken\").build()\n        }\n        return runBlocking {\n            mutex.withLock {\n                val freshToken = sessionManager.getAccessToken()\n                if (freshToken != currentToken) {\n                    return@withLock response.request.newBuilder().header(\"Authorization\", \"Bearer $freshToken\").build()\n                }\n                val newTokens = authApi.get().refreshToken(sessionManager.getRefreshToken() ?: \"\")\n                if (newTokens.isSuccessful) {\n                    sessionManager.updateTokens(newTokens.body()!!.access, newTokens.body()!!.refresh)\n                    response.request.newBuilder().header(\"Authorization\", \"Bearer ${newTokens.body()!!.access}\").build()\n                } else {\n                    sessionManager.clearSession()\n                    null\n                }\n            }\n        }\n    }\n}\n```",
        "why_it_matters_ar": "التعامل الخاطئ مع الجلسات يؤدي لتسريب بيانات المستخدمين أو طرد المستخدم فجأة من التطبيق أثناء التصفح بسبب فشل تجديد التوكن، وهو ما يدمر تجربة المستخدم وثقة العملاء.",
        "worked_example_ar": "نموذج توجيه واجهة المستخدم عند انتهاء الجلسة عبر StateFlow:\n```kotlin\nsealed interface SessionState {\n    data class Active(val userId: String) : SessionState\n    data object Expired : SessionState\n}\n\n// مراقبة حالة الجلسة في الواجهة وتوجيه المستخدم لشاشة تسجيل الدخول فوراً\n```",
        "trade_offs_ar": "استخدام توكنات وصول طويلة العمر يقلل مكالمات التجديد لكنه يمثل خطراً أمنياً هائلاً عند السرقة، بينما التوكنات القصيرة جداً تزيد العبء على السيرفر ومخاطر انتهاء المهلة وتتطلب معالجة سباق دقيقة للغاية في الموبايل.",
        "failure_modes_ar": "حدوث Deadlock إذا تم قفل الـ Mutex داخل خيط الواجهة، أو الدخول في حلقة تجديد لا نهائية (Infinite Loop) إذا كان مسار تجديد التوكن نفسه يرجع خطأ 401، أو تسريب بيانات المستخدم القديم في قاعدة البيانات بعد تسجيل خروجه.",
        "production_perspective_ar": "في التطبيقات المالية، نضيف توقيعاً بيومترياً (Biometric Prompt) مربوطاً بمفتاح تشفير Keystore للعمليات الحساسة، ونقوم بإلغاء كل مهام WorkManager وتفريغ كاش الـ Disk وقاعدة البيانات فور انتهاء الجلسة لمنع أي تسريب على الأجهزة المشتركة.",
        "how_to_answer_ar": "ابدأ بطبرقة الأمان: تخزين الـ JWT في مساحة مشفرة بـ Android Keystore. ثم اشرح معمارية الشبكة: Interceptor لإضافة التوكن و Authenticator لمعالجة خطأ 401. ركز على حل سباق الطلبات المتزامنة عبر قفل Mutex وفحص التوكن الحالي قبل طلب سيرفر جديد، ثم وضح سيناريو تسجيل الخروج الإجباري وتفريغ البيانات.",
        "talking_points_ar": "تقنية Token Rotation، وتأمين المفاتيح في Keystore، والفرق بين Interceptor و Authenticator في OkHttp، والتعامل مع سباق العمليات بـ Mutex، وتأمين الجلسات عند موت العمليات.",
        "follow_ups_ar": "- **المحاور:** \"ما الفرق بين استخدام Interceptor واستخدام Authenticator في OkHttp لتجديد التوكن؟\"\n  **المرشح:** \"الـ Interceptor يعترض الطلبات قبل إرسالها أو بعدها فوراً، بينما الـ Authenticator لا يتم استدعاؤه إلا حصراً عند استقبال خطأ 401 من السيرفر ومصمم خصيصاً لإعادة بناء الطلب وإعادة المحاولة تلقائياً.\"\n\n- **المحاور:** \"كيف تتعامل مع ميزة Token Rotation إذا رفض السيرفر طلب التجديد باعتباره هجوماً مكرراً؟\"\n  **المرشح:** \"أتحقق في الـ Authenticator أولاً هل التوكن الموجود في رأس الطلب يختلف عن أحدث توكن في الذاكرة، فإذا كان مختلفاً أعيد إرسال الطلب بالتوكن الجديد فوراً دون استدعاء مسار التجديد مجدداً.\"",
        "self_check_ar": "هل وضحت كيفية منع تجديد التوكن المتكرر للطلبات المتزامنة؟ هل ذكرت تأمين التخزين بالـ Keystore؟ وهل عالجت سيناريو فشل التجديد النهائي وتفريغ الجلسة؟",
        "references_ar": f"- [OkHttp Authenticator Documentation](https://square.github.io/okhttp/features/calls/#authenticator) — التوثيق الرسمي لمعالجة المصادقة وإعادة المحاولة في OkHttp.\n- [Android Keystore System](https://developer.android.com/privacy-and-security/keystore) — دليل جوجل لحماية وتشفير مفاتيح الاعتماد في العتاد.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "نصمم نظام الجلسات بتخزين توكنات الوصول والتجديد في مساحة مشفرة بـ Android Keystore لضمان أقصى حماية. وعند حدوث خطأ 401 في مكالمات متزامنة، نستخدم OkHttp Authenticator مع قفل Mutex لضمان تنفيذ طلب تجديد واحد فقط عبر الشبكة، بينما تنتظر باقي الطلبات التوكن الجديد وتعيد المحاولة تلقائياً دون مقاطعة المستخدم، مع مسح بيانات الجلسة بالكامل إذا انتهت صلاحية التجديد.",
        "best_answer_ar": "إدارة الجلسات في تطبيقات الإنتاج الاحترافية تتطلب تصميماً أمنياً صارماً ومعالجة دقيقة لسباق العمليات المتزامنة في الشبكة.\n\nمن الناحية الأمنية، نخزن توكنات الوصول القصيرة وتوكنات التجديد الطويلة في EncryptedSharedPreferences مع مفتاح تشفير يولد ويحفظ داخل شريحة العتاد Android Keystore لضمان عدم استخراجها حتى على الأجهزة المكسورة الحماية. وفي طبقة الشبكة، نستخدم عميل OkHttp ونزوده بـ Interceptor يضيف توكن الوصول تلقائياً في رأس كل طلب، ونربطه بـ Authenticator لمعالجة استجابات خطأ 401 Unauthorized.\n\nوعندما تنطلق خمسة طلبات شبكية بالتوازي في شاشة معقدة وتنتهي صلاحية التوكن، ستستقبل كلها خطأ 401 في نفس اللحظة. هنا يتدخل الـ Authenticator المحمي بقفل Mutex؛ حيث يفحص أولاً هل التوكن المرفق في الطلب يطابق التوكن المخزن حالياً، فإذا كان مختلفاً فهذا يعني أن خيطاً آخر أتم التجديد بالفعل فيعيد الطلب فوراً بالتوكن الجديد. وإذا كان هو أول خيط، يستحوذ على القفل وينفذ طلب التجديد الفعلي عبر الشبكة، ثم يحدث الجلسة ويحرر القفل لتعبر باقي الطلبات بنجاح. وفي حال فشل التجديد نهائياً لانتهاء صلاحية الجلسة، يقوم الـ SessionManager بتفريغ كل البيانات المحلية وتوجيه الواجهة لشاشة الدخول.",
        "deep_answer_ar": "العمق الهندسي الحقيقي في إدارة الجلسات يكمن في التعامل مع تقنية تدوير التوكنات (Refresh Token Rotation) وحماية التطبيق من الانهيار عند موت العمليات أو انقطاع الاتصال.\n\nفي الأنظمة المصرفية، يقوم السيرفر بحرق توكن التجديد وإصدار زوج جديد بالكامل مع كل عملية تجديد، ويعتبر أي استخدام لتوكن تجديد قديم بمثابة هجوم تكرار أمني خبيث مما يؤدي لإلغاء الجلسة فوراً. فإذا أرسل تطبيق الموبايل طلبين تجديد بالتوكن القديم في نفس اللحظة، سيتم طرد المستخدم. لذلك نلزم الـ Authenticator بالعمل تحت قفل Mutex صارم وبنية فحص مزدوج (Double-Checked Locking) تقارن التوكن الموجود في الـ Request Header مع التوكن المخزن في الذاكرة لتفادي أي مكالمة شبكة زائدة.\n\nبالإضافة إلى ذلك، نقوم بنمذجة حالة الجلسة كـ StateFlow من كائن مختوم AuthStatus تراقبه طبقة الواجهة. وعندما يرجع مسار التجديد خطأ 403 أو 400 غير قابل للاسترجاع، يقوم الـ SessionManager بمسح الجداول الحساسة من قاعدة بيانات Room وإلغاء جميع مهام المزامنة المجدولة في WorkManager ومسح الكاش السري، لمنع تسريب بيانات العميل السابق إذا استخدم شخص آخر نفس الجهاز. وفي العمليات البنكية فائقة الحساسية، نربط مفتاح فك التشفير في الـ Keystore بكائن BiometricPrompt.CryptoObject، بحيث يتعذر استخراج توكن الوصول من شريحة العتاد دون التحقق البيومتري المباشر من بصمة المستخدم الحالية."
    }
}

# ==========================================
# SYS-04: Design an offline-first system with a local source of truth.
# ==========================================
DATA["SYS-04"] = {
    "concept_en": """An offline-first mobile architecture treats local persistence (typically a Room SQLite database) as the single source of truth (SSOT) and the remote network as an asynchronous synchronization mechanism. The UI layer never observes network responses directly; instead, it observes reactive database queries via Kotlin Flow or PagingData, ensuring immediate rendering and zero offline latency. When a user creates or modifies content, changes are applied optimistically to local tables alongside an atomic insertion into a durable Outbox table containing mutation payloads and client-generated idempotency keys. Background synchronization engines, implemented with WorkManager and exponential backoff, drain the Outbox table when connectivity is restored, transmitting payloads to the backend and reconciling state seamlessly.""",
    "walkthrough_en": """Implementing an offline-first repository with Room Single Source of Truth and the Outbox Pattern:
```kotlin
// 1. Database entities: Main content and durable mutation Outbox
@Entity(tableName = "notes")
data class NoteEntity(
    @PrimaryKey val id: String,
    val title: String,
    val content: String,
    val syncStatus: SyncStatus,
    val updatedAtMs: Long
)

enum class SyncStatus { SYNCED, PENDING_SYNC, FAILED }

@Entity(tableName = "sync_outbox")
data class OutboxEntity(
    @PrimaryKey val mutationId: String, // Client-generated UUID idempotency key
    val entityId: String,
    val payloadJson: String,
    val mutationType: String, // INSERT, UPDATE, DELETE
    val createdAtMs: Long
)

// 2. Offline-First Repository executing optimistic updates inside an atomic transaction
class NoteRepositoryImpl @Inject constructor(
    private val database: AppDatabase,
    private val noteDao: NoteDao,
    private val outboxDao: OutboxDao,
    private val workManager: WorkManager
) : NoteRepository {

    // Single source of truth streaming from Room to UI
    override fun getNotesStream(): Flow<List<Note>> =
        noteDao.getAllNotesFlow().map { list -> list.map { it.toDomain() } }

    override suspend fun updateNote(id: String, newContent: String): Result<Unit> = runCatching {
        val now = System.currentTimeMillis()
        val mutationId = UUID.randomUUID().toString()

        database.withTransaction {
            // Optimistic update of local entity
            noteDao.updateContent(id = id, content = newContent, status = SyncStatus.PENDING_SYNC, timestamp = now)
            
            // Durable record in outbox table
            outboxDao.insert(
                OutboxEntity(
                    mutationId = mutationId,
                    entityId = id,
                    payloadJson = "{\"content\":\"$newContent\"}",
                    mutationType = "UPDATE",
                    createdAtMs = now
                )
            )
        }

        // Trigger WorkManager synchronization with network constraints
        val syncRequest = OneTimeWorkRequestBuilder<SyncOutboxWorker>()
            .setConstraints(Constraints.Builder().setRequiredNetworkType(NetworkType.CONNECTED).build())
            .build()
        workManager.enqueueUniqueWork("SYNC_OUTBOX", ExistingWorkPolicy.KEEP, syncRequest)
    }
}
```""",
    "short_en": """We build offline-first systems by making a local Room database the single source of truth that UI components observe via reactive Flows. When users create or edit data, we write optimistically to the database and record mutations in a durable Outbox table inside an atomic transaction. WorkManager processes queued outbox records with exponential backoff and network constraints, guaranteeing eventual consistency and complete offline usability.""",
    "structured_en": """In an offline-first architecture, local persistence is the authoritative source of truth for the presentation layer, while the network functions as an asynchronous data pipeline.
When the UI loads, it subscribes to reactive database streams using Kotlin Flow.
All reads come directly from disk, delivering instantaneous screen rendering with zero network latency.
When a user creates or modifies content offline, we execute an optimistic local update.
Within a single atomic SQLite transaction, we update the local entity state and insert an entry into a durable Sync Outbox table with a unique idempotency key and pending status.
This guarantees that user intent is never lost, even if the application process dies immediately.
A dedicated background synchronization engine managed by WorkManager monitors network connectivity.
When a connection is established, the sync worker transmits pending outbox payloads in sequence.
Upon server acknowledgment, the outbox record is purged, and the local entity is marked as synchronized.
If conflicts arise, version timestamps or server-authoritative reconciliation strategies resolve differences, streaming the merged state directly to the UI.""",
    "deep_senior_en": """The engineering complexity of offline-first architectures centers on conflict resolution, mutation ordering, and database transaction boundaries.
A naive approach performs network calls first and updates the database upon success; under flaky connectivity, this creates dropped mutations and inconsistent UI state.
By adopting the Outbox pattern with atomic transactions, we decouple user interaction from network availability.
When persisting local mutations, we generate a client-side UUID and an idempotency token.
If the device experiences intermittent connectivity or sudden process termination, WorkManager automatically resumes the sync worker with exponential backoff.
Because the server enforces idempotency via the client token, duplicate deliveries caused by lost HTTP response packets do not create duplicate records on the backend.
For conflict resolution, we choose between Last-Write-Wins based on synchronized server timestamps, field-level merging, or three-way merge vectors depending on domain criticality.
In financial or collaborative domains, server-authoritative rejection is handled by rolling back the optimistic entity in Room and surfacing a non-blocking resolution banner to the user.
Furthermore, Room's InvalidationTracker detects table changes and pushes fresh queries through Flow pipelines to Compose UI without manual refresh logic, achieving seamless consistency across online and offline states.
Underneath SQLite, we enable Write-Ahead Logging to decouple background outbox writes from foreground UI queries, preventing database lock contention.
Additionally, we handle device storage limits by catching SQLiteFullException and applying automated pruning to non-essential cached media, ensuring core mutation records always persist.""",
    "meta_ar": {
        "id": "SYS-04",
        "questionAr": "كيف تصمم نظاماً يعمل بمبدأ أولوية عدم الاتصال (Offline-First) مع مصدر وحيد للحقيقة؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على تصميم معمارية Offline-First باستخدام Room كمصدر وحيد للحقيقة (SSOT)، وتطبيق نمط Outbox لتخزين العمليات محلياً، والمزامنة بالخلفية عبر WorkManager، وحل نزاعات البيانات.",
        "concept_ar": "معمارية Offline-First تعامل قاعدة البيانات المحلية (Room SQLite) كمصدر وحيد للحقيقة (Single Source of Truth)، بينما تعتبر الشبكة وسيلة مزامنة غير متزامنة. الواجهة تقرأ حصرياً من قاعدة البيانات عبر StateFlow، مما يضمن ظهور الشاشات فوراً دون انتظار استجابة السيرفر. وعند قيام المستخدم بأي تعديل، يُكتب التعديل تفاؤلياً في الجداول المحلية مع إدراج سجل في جدول Outbox داخل Transaction ذرية واحدة، وتتولى WorkManager رفع التعديلات للسيرفر عند توفر الاتصال بمفاتيح Idempotency فريدة.",
        "walkthrough_ar": "تطبيق نمط Outbox ومصدر الحقيقة الوحيد باستخدام Room و WorkManager:\n```kotlin\n@Entity(tableName = \"notes\")\ndata class NoteEntity(@PrimaryKey val id: String, val title: String, val syncStatus: SyncStatus)\n\n@Entity(tableName = \"outbox\")\ndata class OutboxEntity(@PrimaryKey val mutationId: String, val entityId: String, val payloadJson: String)\n\nclass NoteRepositoryImpl(private val db: AppDatabase, private val noteDao: NoteDao, private val outboxDao: OutboxDao) {\n    fun getNotes(): Flow<List<NoteEntity>> = noteDao.getAllNotesFlow()\n\n    suspend fun updateNote(id: String, content: String) = db.withTransaction {\n        noteDao.update(id, content, SyncStatus.PENDING)\n        outboxDao.insert(OutboxEntity(UUID.randomUUID().toString(), id, content))\n    }\n}\n```",
        "why_it_matters_ar": "في العالم الحقيقي، شبكات الموبايل متذبذبة وغير مستقرة؛ إجبار المستخدم على الانتظار أو فقدان البيانات التي كتبها لمجرد انقطاع الاتصال بلحظة يؤدي لفقدان العملاء وتدمير موثوقية التطبيق.",
        "worked_example_ar": "إدارة قفل المعاملات وتفادي تكرار إرسال التعديلات عبر UniqueWorkPolicy في WorkManager:\n```kotlin\nval syncWork = OneTimeWorkRequestBuilder<SyncWorker>()\n    .setConstraints(Constraints.Builder().setRequiredNetworkType(NetworkType.CONNECTED).build())\n    .build()\nworkManager.enqueueUniqueWork(\"OUTBOX_SYNC\", ExistingWorkPolicy.KEEP, syncWork)\n```",
        "trade_offs_ar": "معمارية Offline-First تقدم سرعة خارقة وموثوقية استثنائية للمستخدم، لكنها تزيد من تعقيد الكود بمقدار الضعف بسبب إدارة جداول الـ Outbox وفض نزاعات البيانات (Conflict Resolution) وإدارة ترقيات قواعد البيانات المتكررة.",
        "failure_modes_ar": "تحديث الكيان المحلي دون كتابة سجل الـ Outbox في Transaction ذرية مما يسبب فقدان المزامنة عند إغلاق التطبيق فجأة، أو إرسال طلبات المزامنة دون مفتاح Idempotency مما يسبب تكرار السجلات على السيرفر عند انقطاع الـ Ack.",
        "production_perspective_ar": "في تطبيقات الملاحظات والمهام مثل Google Keep، نطبق استراتيجية Last-Write-Wins معتمدة على توقيتات السيرفر الموحدة، مع إبقاء مؤشر مرئي يوضح للمستخدم ما إذا كانت الملاحظة محفوظة محلياً فقط أم تم تأكيد مزامنتها سحابياً.",
        "how_to_answer_ar": "وضح المبدأ أولاً: الواجهة تقرأ دائماً من داتابيز Room وليس من الشبكة مباشرة. ثم اشرح نمط الـ Outbox لحفظ التعديلات في جدول مؤقت داخل Transaction ذرية واحدة. اشرح دور WorkManager في المزامنة بالخلفية بشروط اتصال محددة، واختم بآليات فض النزاعات وكيفية إخطار الواجهة بالتغييرات عبر Flow.",
        "talking_points_ar": "نمط Single Source of Truth، ونمط Outbox، والـ InvalidationTracker في Room، وحل النزاعات (Last-Write-Wins مقابل CRDT)، ومفاتيح Idempotency في السيرفر.",
        "follow_ups_ar": "- **المحاور:** \"ماذا يحدث لو عدل المستخدم نفس العنصر ثلاث مرات متتالية بدون إنترنت؟\"\n  **المرشح:** \"نقوم إما بتجميع (Coalescing) التعديلات في الـ Outbox للاحتفاظ بآخر حالة نهائية فقط لتوفير استهلاك الشبكة، أو إرسالها بالترتيب الزمني الصارم إذا كان الترتيب يغير الحالة التجارية.\"\n\n- **المحاور:** \"كيف يتعامل التطبيق مع تعارض التعديل لو كان السيرفر قد استقبل تعديلاً من جهاز آخر لنفس الحساب؟\"\n  **المرشح:** \"نستخدم إصدارات الوثائق (ETags أو Version Numbers)؛ فإذا اكتشف السيرفر تعارضاً، يرجع استجابة تعارض ويقوم التطبيق بتنبيه المستخدم أو دمج التعديلات تلقائياً بحسب القواعد المعتمدة.\"",
        "self_check_ar": "هل أكدت على أن الواجهة تقرأ من قاعدة البيانات فقط؟ هل شرحت نمط الـ Outbox والعمليات الذرية؟ وهل بينت كيفية إدارة التزامن وفض النزاعات؟",
        "references_ar": f"- [Android Architecture: Data Layer](https://developer.android.com/topic/architecture/data-layer) — دليل جوجل الرسمي لطبقة البيانات ومصادر الحقيقة الوحيدة.\n- [Offline-first Android Apps](https://developer.android.com/topic/architecture/data-layer/offline-first) — إرشادات جوجل لتصميم تطبيقات تدعم العمل دون اتصال.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "نصمم نظام أولوية عدم الاتصال بجعل قاعدة بيانات Room هي المصدر الوحيد للحقيقة الذي تراقبه واجهة المستخدم عبر التدفقات التفاعلية Flow، مما يحقق ظهوراً فورياً للشاشات دون انتظار الشبكة. وعند إجراء تعديل دون اتصال، نحدث الكيان المحلي ونحفظ أمر التعديل في جدول Outbox داخل معاملة ذرية واحدة، وتتولى WorkManager رفع التعديلات للسيرفر تلقائياً بمجرد عودة الاتصال باستخدام مفاتيح Idempotency لمنع التكرار.",
        "best_answer_ar": "تصميم نظام يعمل بكفاءة تامة دون اتصال يعتمد على فصل تدفق القراءة عن تدفق الكتابة واستخدام قاعدة البيانات كمرجع وحيد للحقيقة.\n\nفي مسار القراءة، تتصل الواجهة بقاعدة بيانات Room مباشرة عبر Flow أو PagingData؛ أي قراءة تنفذ من القرص في أجزاء من الثانية مما يمنح التطبيق سرعة مذهلة حتى في وضع الطيران. ولا تستقبل شاشات الـ Compose أي بيانات من الشبكة بشكل مباشر على الإطلاق.\n\nأما في مسار الكتابة والتعديل، فنطبق نمط Outbox التفاؤلي؛ فعندما يضغط المستخدم على حفظ، نفتح معاملة ذرية SQLite Transaction نقوم فيها بتحديث الكيان المحلي فوراً لتراه الواجهة لحظياً، وفي نفس اللحظة نسجل طلباً في جدول خاص يسمى Outbox يحتوي على كود العملية والبيانات المشفرة ومفتاح تتبع UUID فريد. ثم نجدول مهمة خلفية في WorkManager تشترط توفر الشبكة. وعند استعادة الاتصال، يقرأ الـ Worker سجلات الـ Outbox ويرسلها للسيرفر بالتتابع، وعند نجاح المعاملة يمسح السجل من الـ Outbox، مما يضمن اتساق البيانات حتى لو تم إغلاق التطبيق بالقوة أثناء التعديل.",
        "deep_answer_ar": "العمق الهندسي في معمارية Offline-First يتبلور في استراتيجيات فض النزاعات وضمان عدم تكرار العمليات عبر مفاتيح عدم التكرار Idempotency Keys.\n\nعندما يكون الجهاز غير متصل، قد تنقطع حزمة استجابة السيرفر في الهواء بعد أن تمت معالجة الطلب على الخادم بالفعل، فإذا أعاد التطبيق إرسال الطلب دون تدابير حماية، ستتكرر العملية. لذلك نولد UUID محلي لكل تعديل نرسله كـ Idempotency-Key في الـ Header، مما يجبر السيرفر على التحقق من عملياته المسجلة وإرجاع نتيجة سابقة دون تكرار التنفيذ.\n\nأما بالنسبة لفض نزاعات التعديل المتزامن من أجهزة متعددة، فنعتمد على أرقام الإصدارات ومطابقة الـ ETags. إذا استقبل التطبيق خطأ 409 Conflict، فإننا نطبق إما قاعدة Last-Write-Wins بالاعتماد على توقيت الخادم الموحد، أو نقوم بعكس التعديل التفاؤلي في Room وإرجاع الكيان لشكله الأصلي مع إظهار شريط تنبيه غير مانع للواجهة يوضح للمستخدم سبب رفض التعديل. وبفضل آلية InvalidationTracker المدمجة في Room، تتلقى واجهات Compose التحديثات وتلغي تكويناتها تلقائياً فور كتابة السيرفر للبيانات المحدثة في الداتابيز، مما يضمن تجربة سلسة وخالية من وميض الشاشة.\n\nوعلى صعيد محرك SQLite، نفعل وضع Write-Ahead Logging (WAL) لتفادي حظر استعلامات القراءة أثناء كتابة الـ Worker في جدول الـ Outbox. ونتعامل بحذر مع امتلاء مساحة الهاتف عبر اعتراض استثناء SQLiteFullException وتفريغ الملفات المؤقتة غير الضرورية تلقائياً لضمان عدم ضياع التعديلات."
    }
}

# ==========================================
# SYS-05: Design a robust payment transaction lifecycle.
# ==========================================
DATA["SYS-05"] = {
    "concept_en": """Designing a robust mobile payment transaction lifecycle requires treating the mobile client as an untrusted, highly volatile coordinator. Mobile devices face abrupt network drops, socket timeouts, low-memory process termination, and unpredictable user abandonment during critical payment steps. Under no circumstances should the mobile client be the final authority on payment success or failure, nor should an ambiguous network timeout ever be interpreted as a failed transaction. A resilient architecture relies on client-generated idempotency keys, an explicit payment state machine (Draft, Processing, Pending Verification, Authorized, Settled, and Failed), durable transaction records in local persistence, and background reconciliation loops combining push notifications with exponential backoff polling to verify actual transaction state before permitting retries.""",
    "walkthrough_en": """Implementing a resilient payment state machine and reconciliation flow:
```kotlin
// 1. Explicit payment state machine representing all lifecycle stages
sealed interface PaymentTransactionState {
    data object Idle : PaymentTransactionState
    data class Processing(val idempotencyKey: String) : PaymentTransactionState
    data class PendingVerification(val idempotencyKey: String, val orderId: String) : PaymentTransactionState
    data class Succeeded(val transactionId: String, val orderId: String) : PaymentTransactionState
    data class Failed(val reason: String, val canRetrySafely: Boolean) : PaymentTransactionState
}

// 2. Payment repository orchestrating idempotency and status reconciliation
class PaymentRepositoryImpl @Inject constructor(
    private val paymentApi: PaymentApiService,
    private val paymentDao: PaymentDao
) : PaymentRepository {

    override suspend fun executePayment(orderId: String, amountCents: Long): PaymentTransactionState {
        val idempotencyKey = UUID.randomUUID().toString()

        // 1. Persist intent locally before initiating network request
        paymentDao.insert(
            PaymentEntity(orderId = orderId, idempotencyKey = idempotencyKey, state = "PROCESSING")
        )

        return try {
            val response = paymentApi.charge(
                idempotencyKey = idempotencyKey,
                request = ChargeRequest(orderId = orderId, amountCents = amountCents)
            )

            if (response.isSuccessful && response.body()?.status == "AUTHORIZED") {
                paymentDao.updateState(orderId, "SUCCEEDED")
                PaymentTransactionState.Succeeded(response.body()!!.transactionId, orderId)
            } else {
                paymentDao.updateState(orderId, "FAILED")
                PaymentTransactionState.Failed(response.errorBody()?.string() ?: "Declined", canRetrySafely = true)
            }
        } catch (e: IOException) {
            // CRITICAL: Network timeout is NOT a failure. Must reconcile to prevent double charge!
            paymentDao.updateState(orderId, "PENDING_VERIFICATION")
            PaymentTransactionState.PendingVerification(idempotencyKey, orderId)
        }
    }
}
```""",
    "short_en": """We design payment lifecycles around idempotency and explicit state machines where the backend remains the ultimate authority. Every payment intent receives a client-generated UUID idempotency key. If a network timeout occurs during authorization, the client transitions into a pending verification state rather than failing. We poll the backend or await push notifications to reconcile the actual payment status before allowing any retry, preventing double charging.""",
    "structured_en": """Designing a robust payment transaction lifecycle requires handling network drops, process death, and payment gateway redirects without risking double charging.
The architecture centers on an explicit payment state machine with states like Draft, Processing, Pending Verification, Authorized, and Failed.
When a user taps to pay, we generate a unique idempotency key on the device and submit it with the payment intent.
The backend uses this key to ensure that duplicate HTTP submissions execute exactly once.
If the network drops or the HTTP socket times out while awaiting the gateway response, we strictly avoid marking the payment as failed.
Instead, we persist the transaction locally as Pending Verification and inform the user that payment confirmation is in progress.
The mobile client initiates exponential backoff polling against a dedicated transaction status endpoint, while also listening for Firebase Cloud Messaging push webhooks triggered by backend-to-gateway callbacks.
Only when the backend confirms final settlement does the state transition to Completed.
This eliminates duplicate charges and maintains financial integrity under worst-case mobile connectivity.""",
    "deep_senior_en": """From a staff-level systems perspective, the most critical vulnerability in mobile payment design is the ambiguous network timeout.
When an HTTP POST request to execute a payment times out, the client cannot know whether the packet was lost on the outbound journey, processed successfully by the payment provider with a lost response, or rejected mid-flight.
Treating a timeout as a failure invites the user to tap pay again, causing an immediate double debit and severe customer dissatisfaction.
To solve this, our payment architecture decouples payment execution from payment reconciliation.
The initial submission creates a durable transaction record in local storage containing the idempotency key, amount, and order ID, locking the checkout UI against further interaction.
If the response drops, our background sync layer and UI polling mechanism query the backend using the same idempotency key to inspect the server's ledger.
If the backend has not received the transaction, it safely cancels the intent or permits a guarded retry.
If the payment succeeded at the gateway, the backend returns the settled order, and the client transitions seamlessly to the success confirmation screen.
Furthermore, we log comprehensive audit trail events across every lifecycle transition, enabling operational support teams to trace discrepancies between mobile telemetry, payment gateway logs, and core banking ledgers.""",
    "meta_ar": {
        "id": "SYS-05",
        "questionAr": "كيف تصمم دورة حياة معاملات دفع قوية ومرنة (Payment Transaction Lifecycle) تمنع السحب المزدوج؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على تصميم معمارية مدفوعات مالية آمنة، واستخدام مفاتيح Idempotency، ومعالجة انقطاع الاتصال والمهلات الزمنية دون سحب مالي مزدوج، وإدارة التسوية (Reconciliation).",
        "concept_ar": "التعامل مع المدفوعات على الموبايل يتطلب افتراض أن هاتف المستخدم غير موثوق وعرضة لانقطاع الاتصال وموت العملية في أي لحظة. القاعدة الذهبية هي ألا يكون تطبيق الموبايل هو صاحب القرار في نجاح أو فشل العملية، وألا يعتبر انتهاء مهلة الشبكة (Socket Timeout) فشلاً أبداً. يعتمد النظام على آلة حالة واضحة (State Machine)، واستخدام مفاتيح عدم التكرار (Idempotency Keys)، وفصل مرحلة الإرسال عن مرحلة التسوية والمطابقة عبر السيرفر.",
        "walkthrough_ar": "تطبيق نمط آلة حالة المدفوعات والتعامل مع انتهاء المهلة كحالة معلقة تتطلب مطابقة:\n```kotlin\nsealed interface PaymentState {\n    data class Processing(val idempotencyKey: String) : PaymentState\n    data class PendingVerification(val orderId: String) : PaymentState\n    data class Succeeded(val transactionId: String) : PaymentState\n    data class Failed(val error: String) : PaymentState\n}\n\nsuspend fun executePayment(orderId: String): PaymentState = try {\n    val res = api.pay(orderId, idempotencyKey)\n    if (res.isSuccessful) PaymentState.Succeeded(res.body()!!.id) else PaymentState.Failed(res.message())\n} catch (e: IOException) {\n    // انقطاع الشبكة ليس فشلاً بل حالة معلقة حتى التحقق من السيرفر\n    PaymentState.PendingVerification(orderId)\n}\n```",
        "why_it_matters_ar": "خطأ برمجي واحد في دورة حياة الدفع قد يتسبب في خصم المبلغ من العميل مرتين أو إظهار شاشة خطأ بينما تم السحب بالفعل، مما يؤدي لمشاكل قانونية ومالية جسيمة وفقدان كامل لثقة المستخدمين.",
        "worked_example_ar": "نموذج استعلام فحص حالة المعاملة (Reconciliation Polling) قبل السماح للمستخدم بإعادة المحاولة:\n```kotlin\nsuspend fun pollPaymentStatus(orderId: String, key: String): PaymentStatus {\n    repeat(5) {\n        val status = api.checkStatus(orderId, key)\n        if (status.isFinal) return status\n        delay(2000L)\n    }\n    return PaymentStatus.REQUIRES_MANUAL_SUPPORT\n}\n```",
        "trade_offs_ar": "عرض نتيجة فورية بعد الدفع يحسن تجربة المستخدم ولكنه مستحيل تقنياً في بعض بوابات الدفع التي تتطلب توجيهاً ثلاثي الأبعاد 3DS، لذا يجب الموازنة بين السرعة واستخدام حالات التحقق المعلقة (Pending Verification).",
        "failure_modes_ar": "اعتبار انتهاء مهلة الاتصال Timeout فشلاً وإظهار زر إعادة المحاولة للمستخدم، مما يؤدي للضغط مجدداً والخصم المزدوج، أو حفظ أرقام البطاقات الحساسة على ذاكرة الموبايل بدلاً من استخدام الـ Tokenization عبر بوابة الدفع.",
        "production_perspective_ar": "في التطبيقات المالية الكبرى، نغلق زر الدفع فور الضغط عليه (Debounce + Disable)، ونولد مفتاح UUID فريد لكل طلب ونحفظه في قاعدة البيانات، وإذا انقطع الاتصال ننتقل لشاشة جاري التحقق من عملية الدفع مع الاستماع لإشعارات الـ Push من السيرفر لتحديث الحالة فور استقرارها.",
        "how_to_answer_ar": "ابدأ بالقاعدة الذهبية: السيرفر هو مصدر الحقيقة الوحيد والعميل مجرد منسق غير موثوق. اشرح استخدام الـ Idempotency Key لمنع تكرار المعاملات، ووضح آلة الحالة (Draft -> Processing -> Pending -> Succeeded/Failed)، وركز بشدة على كيفية معالجة انقطاع الاتصال عبر التسوية (Reconciliation) بدلاً من اعتبارها فاشلة.",
        "talking_points_ar": "مفاتيح Idempotency، وخطورة انقطاع الاتصال (Ambiguous Timeout)، وآلة حالة المدفوعات، والمطابقة الخلفية (Reconciliation Polling)، والتوافق مع PCI-DSS والـ Tokenization.",
        "follow_ups_ar": "- **المحاور:** \"ماذا تفعل لو انقطع الاتصال والـ Socket انتهت مهلته أثناء انتظار استجابة البنك؟\"\n  **المرشح:** \"أعتبر العملية في حالة 'معلقة للتحقق' (Pending Verification) ولا أسمح للمستخدم بالدفع مجدداً لنفس الطلب، وأبدأ استعلام السيرفر بشكل تكراري للتأكد هل تم قيد العملية في دفتر الأستاذ لديه أم لا.\"\n\n- **المحاور:** \"كيف تمنع هجمات التكرار أو تكرار النقر من المستخدم في الواجهة؟\"\n  **المرشح:** \"أعطل زر الدفع فور أول نقرة، وأربط الطلب بـ Idempotency Key فريد يتم التحقق منه على مستوى بوابة الدفع وخادم التطبيق لرفض أي طلب مكرر يحمل نفس المفتاح.\"",
        "self_check_ar": "هل شددت على عدم اعتبار انقطاع الشبكة فشلاً نهائياً؟ هل شرحت دور مفاتيح الـ Idempotency؟ وهل بينت آلية المطابقة والتسوية مع السيرفر؟",
        "references_ar": f"- [Stripe Engineering: Designing robust payment APIs](https://stripe.com/blog/idempotency) — مقال سترايب الكلاسيكي حول هندسة المدفوعات المقاومة للأخطاء ومفاتيح عدم التكرار.\n- [Google Pay API Developer Guide](https://developers.google.com/pay/api/android/overview) — التوثيق الرسمي لدمج خدمات الدفع الآمنة على أندرويد.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "نصمم دورة حياة المدفوعات بالاعتماد على مفاتيح عدم التكرار Idempotency Keys وآلة حالة صريحة يكون السيرفر فيها هو صاحب القرار النهائي. يولد التطبيق مفتاح UUID فريداً لكل محاولة دفع، وإذا حدث انقطاع في الشبكة أو انتهاء مهلة الاتصال، نعتبر العملية معلقة للتحقق بدلاً من اعتبارها فاشلة، ونبدأ مطابقة الحالة مع السيرفر عبر الاستعلام المكرر أو إشعارات الـ Push لمنع الخصم المزدوج نهائياً.",
        "best_answer_ar": "التعامل مع المدفوعات المالية على الموبايل يتطلب عقيدة هندسية صارمة تعتبر العميل بيئة غير موثوقة وعرضة لانقطاع الاتصال وموت العملية في أي لحظة.\n\nالركيزة الأساسية هي أن تطبيق الموبايل لا يملك أبداً سلطة إعلان نجاح أو فشل المعاملة بمفرده. عندما يضغط المستخدم على تأكيد الدفع، نعطل الزر فوراً لمنع التكرار، ونولد مفتاح عدم تكرار فريد Idempotency Key نسجله محلياً مع الطلب ونرسله لبوابة الدفع. يضمن هذا المفتاح على الخادم أنه مهما تكرر وصول الطلب بسبب مشاكل الشبكة، فلن يتم سحب الأموال سوى مرة واحدة فقط.\n\nأما السيناريو الأكثر خطورة فهو انقطاع الاتصال بعد إرسال الطلب وقبل استلام الرد؛ اعتبار هذا الانقطاع فشلاً وإظهار زر إعادة المحاولة هو السبب الرئيسي في الكارثة المالية للخصم المزدوج. لذلك ننقل المعاملة لحالة Pending Verification ونوضح للمستخدم أننا نتحقق من حسابه البنكي. ونقوم عبر مهمة خلفية أو عبر شاشة الانتظار بالاستعلام الدوري عن حالة المفتاح ذاته، كما نستمع لإشعار Push من السيرفر بمجرد إتمام التسوية مع البنك، ولا ننتقل لشاشة الإتمام أو الإلغاء إلا بعد الحصول على تأكيد حاسم من السيرفر.",
        "deep_answer_ar": "التحليل الهندسي المتقدم لمعاملات الدفع في الموبايل يركز على معالجة حالة الغموض الشبكي (Ambiguous Network State) وفصل دورة حياة واجهة المستخدم عن دورة حياة المعاملة المالية.\n\nعندما تطلق دالة الاتصال استثناء SocketTimeoutException، يستحيل على الموبايل معرفة هل سقط الطلب قبل وصوله للبنك أم تمت معالجته وسقطت حزمة التأكيد في طريق العودة. إذا سمحنا للمستخدم بإعادة المحاولة، ستقوم بوابة الدفع بفتح معاملة ثانية وخصم نفس القيمة مرتين. لحل هذه المعضلة، نصمم طبقة الدفع كمعاملة غير متزامنة ذات مرحلتين (Two-Phase Reconciliation)؛ حيث يتم حفظ طلب الدفع في قاعدة بيانات Room المحلية بحالة Processing مع مفتاح الـ UUID قبل إطلاق طلب الشبكة بجزء من الثانية.\n\nإذا سقط الاتصال، لا يلغى الطلب، بل تتولى طبقة المزامنة إرسال استعلام تحقق بالـ Idempotency Key إلى خادم التطبيق لمعرفة موقف العملية في البنك. إذا أبلغنا البنك أن المعاملة لم تسجل، نقوم بإلغاء الإذن بأمان والسماح بإعادة المحاولة. وإذا كان البنك قد سحب المبلغ بالفعل، يقوم خادمنا بإصدار تأكيد الشراء، وتتلقى شاشة الموبايل التحديث عبر WebSocket أو Silent Push Notification، مما يضمن اتساق الدفاتر المالية وحماية العميل من أي خصم عشوائي.\n\nولضمان الامتثال التام للمتطلبات المصرفية، نسجل كل انتقال في آلة الحالة داخل سجل تدقيق مشفر (Encrypted Audit Log) محلياً، ونرسل قياسات زمن الاستجابة إلى أنظمة المراقبة التشغيلية لاكتشاف أي تباطؤ في بوابات الدفع والتدخل الفوري."
    }
}

# ==========================================
# SYS-06: Design caching, pagination, and remote synchronization.
# ==========================================
DATA["SYS-06"] = {
    "concept_en": """Designing mobile caching, pagination, and remote data synchronization requires balancing network bandwidth, memory pressure, and UI frame rate stability. A modern Android pagination architecture pairs Jetpack Paging 3 with Room local database caching via a RemoteMediator. RemoteMediator bridges remote REST/GraphQL APIs with the local SQLite persistence layer, requesting subsequent network pages only when the user scrolls near the boundary of cached data. Fetched items are persisted directly into Room within an atomic transaction alongside a dedicated RemoteKeys table tracking page tokens or timestamps. The Compose UI observes a continuous Flow of PagingData sourced directly from Room's PagingSource, guaranteeing 60/120 FPS jank-free scrolling, zero-latency offline access, and automatic memory windowing.""",
    "walkthrough_en": """Implementing robust caching, pagination, and sync with Jetpack Paging 3 and RemoteMediator:
```kotlin
// 1. Entities for Content and Pagination Remote Keys
@Entity(tableName = "articles")
data class ArticleEntity(
    @PrimaryKey val id: String,
    val title: String,
    val summary: String,
    val publishedAtMs: Long
)

@Entity(tableName = "article_remote_keys")
data class ArticleRemoteKeys(
    @PrimaryKey val articleId: String,
    val prevKey: Int?,
    val nextKey: Int?
)

// 2. RemoteMediator coordinating network page fetches with Room caching
@OptIn(ExperimentalPagingApi::class)
class ArticleRemoteMediator(
    private val database: AppDatabase,
    private val apiService: ArticleApiService
) : RemoteMediator<Int, ArticleEntity>() {

    override suspend fun load(
        loadType: LoadType,
        state: PagingState<Int, ArticleEntity>
    ): MediatorResult {
        val page = when (loadType) {
            LoadType.REFRESH -> {
                val remoteKeys = getRemoteKeyClosestToPosition(state)
                remoteKeys?.nextKey?.minus(1) ?: 1
            }
            LoadType.PREPEND -> return MediatorResult.Success(endOfPaginationReached = true)
            LoadType.APPEND -> {
                val remoteKeys = getRemoteKeyForLastItem(state)
                val nextKey = remoteKeys?.nextKey
                    ?: return MediatorResult.Success(endOfPaginationReached = remoteKeys != null)
                nextKey
            }
        }

        return try {
            val response = apiService.getArticles(page = page, pageSize = state.config.pageSize)
            val articles = response.items
            val endOfPaginationReached = articles.isEmpty()

            database.withTransaction {
                if (loadType == LoadType.REFRESH) {
                    database.articleRemoteKeysDao().clearRemoteKeys()
                    database.articleDao().clearArticles()
                }

                val prevKey = if (page == 1) null else page - 1
                val nextKey = if (endOfPaginationReached) null else page + 1
                val keys = articles.map { ArticleRemoteKeys(it.id, prevKey, nextKey) }

                database.articleRemoteKeysDao().insertAll(keys)
                database.articleDao().insertAll(articles.map { it.toEntity() })
            }

            MediatorResult.Success(endOfPaginationReached = endOfPaginationReached)
        } catch (e: Exception) {
            MediatorResult.Error(e)
        }
    }

    private suspend fun getRemoteKeyForLastItem(state: PagingState<Int, ArticleEntity>): ArticleRemoteKeys? {
        return state.pages.lastOrNull { it.data.isNotEmpty() }?.data?.lastOrNull()?.let { article ->
            database.articleRemoteKeysDao().getRemoteKeyByArticleId(article.id)
        }
    }

    private suspend fun getRemoteKeyClosestToPosition(state: PagingState<Int, ArticleEntity>): ArticleRemoteKeys? {
        return state.anchorPosition?.let { position ->
            state.closestItemToPosition(position)?.id?.let { articleId ->
                database.articleRemoteKeysDao().getRemoteKeyByArticleId(articleId)
            }
        }
    }
}
```""",
    "short_en": """We combine Jetpack Paging 3 with Room database caching using a RemoteMediator. The UI observes a reactive PagingData stream directly from Room, guaranteeing instant offline rendering and smooth scrolling. As the user approaches the scroll boundary, RemoteMediator fetches the next page from the network, stores it in Room alongside boundary keys in a single transaction, and automatically updates the UI.""",
    "structured_en": """A scalable pagination and caching architecture utilizes Room persistence as the backing store for Jetpack Paging 3, orchestrated by RemoteMediator.
Instead of loading network payloads directly into memory-backed lists that are lost on process death, all paginated data flows from the network into Room tables.
The UI observes a continuous Flow of PagingData sourced from a Room PagingSource, ensuring that list items remain available offline and survive orientation changes without re-fetching.
When the user scrolls near the list boundary, Paging 3 signals RemoteMediator to fetch additional items.
RemoteMediator looks up the corresponding page token from a dedicated RemoteKeys table, executes the HTTP request, and saves both the new items and updated keys within a single atomic database transaction.
If the network request fails, Paging 3 surfaces the error state directly to the UI's load state adapter, allowing users to retry with a single tap while continuing to view previously cached content.
This decouples network latency from UI rendering and optimizes memory consumption.""",
    "deep_senior_en": """Under the hood, the combination of Paging 3 and Room eliminates common production pitfalls like duplicate items, scroll jumps, and memory bloat.
In memory-only pagination, rapid user scrolling accumulates thousands of heavy object allocations in the heap, eventually triggering garbage collection pauses and OutOfMemory errors.
By backing the PagingSource with SQLite, Room and Paging 3 utilize windowed cursor queries, holding only the active viewport items and a small prefetch buffer in memory while paging data in and out of disk seamlessly.
The critical design challenge in RemoteMediator is managing cache invalidation and prepend or append boundary keys.
We maintain a separate RemoteKeys table storing next and previous page identifiers keyed by item ID.
During a user pull-to-refresh action, RemoteMediator triggers a REFRESH load type, clearing stale entities and resetting remote keys in an atomic transaction before writing fresh items.
Furthermore, we decouple item identity using stable keys in LazyColumn, which prevents Compose recomposition flicker during item updates.
For freshness, we store a sync timestamp; if the cached dataset exceeds our time-to-live threshold, RemoteMediator initiates a background refresh while immediately displaying the cached data, achieving instantaneous startup performance.
Additionally, to avoid exceeding Android's two-megabyte SQLite CursorWindow threshold on media-heavy datasets, our Room queries select only the minimal columns needed for list rendering, preventing CursorWindowAllocationException under high scroll velocity.""",
    "meta_ar": {
        "id": "SYS-06",
        "questionAr": "كيف تصمم نظام تخزين مؤقت (Caching) وتقسيم صفحات (Pagination) ومزامنة بيانات عن بُعد؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على دمج Jetpack Paging 3 مع قاعدة بيانات Room عبر RemoteMediator، وإدارة مفاتيح الصفحات RemoteKeys، وتفادي استهلاك الذاكرة وتجمد الشاشات أثناء التمرير السريع.",
        "concept_ar": "تصميم التخزين المؤقت وتقسيم الصفحات بكفاءة يتطلب ربط مكتبة Jetpack Paging 3 مع Room باستخدام RemoteMediator. في هذا النموذج، لا تستهلك واجهة المستخدم كود الشبكة مباشرة، بل تعرض البيانات المخزنة محلياً في SQLite، بينما يتولى RemoteMediator طلب الصفحات الجديدة من الشبكة عندما يقترب المستخدم من نهاية القائمة وتخزينها في قاعدة البيانات في معاملة ذرية مع مفاتيح الصفحات RemoteKeys، مما يوفر سلاسة 120 إطاراً في الثانية دون استهلاك زائد للرام.",
        "walkthrough_ar": "تطبيق RemoteMediator لربط شبكة API بقاعدة بيانات Room مع إدارة مفاتيح الصفحات:\n```kotlin\n@OptIn(ExperimentalPagingApi::class)\nclass ArticleRemoteMediator(private val db: AppDatabase, private val api: ArticleApiService) : RemoteMediator<Int, ArticleEntity>() {\n    override suspend fun load(loadType: LoadType, state: PagingState<Int, ArticleEntity>): MediatorResult {\n        val page = when (loadType) {\n            LoadType.REFRESH -> 1\n            LoadType.PREPEND -> return MediatorResult.Success(endOfPaginationReached = true)\n            LoadType.APPEND -> db.remoteKeysDao().getLastKey()?.nextKey ?: return MediatorResult.Success(true)\n        }\n        val res = api.getArticles(page, state.config.pageSize)\n        db.withTransaction {\n            if (loadType == LoadType.REFRESH) db.articleDao().clearAll()\n            db.articleDao().insertAll(res.items)\n            db.remoteKeysDao().insert(ArticleRemoteKeys(res.nextPage))\n        }\n        return MediatorResult.Success(endOfPaginationReached = res.items.isEmpty())\n    }\n}\n```",
        "why_it_matters_ar": "تحميل القوائم الطويلة في ذاكرة الرام فقط يؤدي لاستهلاك هائل للذاكرة وتوقف التطبيق بـ OutOfMemoryError، بالإضافة لفقدان القائمة وإعادة تحميلها عند تدوير الشاشة أو انقطاع النت.",
        "worked_example_ar": "مراقبة الـ PagingData في Compose واستخدام المفاتيح الثابتة لمنع وميض الشاشة:\n```kotlin\nval items = viewModel.articlesFlow.collectAsLazyPagingItems()\nLazyColumn {\n    items(count = items.itemCount, key = items.itemKey { it.id }) {\n        ArticleRow(items[it])\n    }\n}\n```",
        "trade_offs_ar": "التخزين في الذاكرة فقط (In-Memory Paging) سهل التنفيذ وسريع البرمجة لكنه غير دائم ويستهلك الرام. بينما استخدام Room مع RemoteMediator يتطلب كتابة جداول إضافية ومعاملات معقدة لكنه يوفر عملاً Offline وتصفحاً سلساً وثابتاً.",
        "failure_modes_ar": "عدم استخدام معاملات ذرية عند حفظ الصفحات ومفاتيح الـ RemoteKeys مما يؤدي لخلل في ترتيب الصفحات، أو حذف البيانات القديمة قبل نجاح تحميل الصفحة الجديدة مما يترك المستخدم بشاشة بيضاء خالية عند انقطاع الاتصال.",
        "production_perspective_ar": "في تطبيقات الأخبار والتواصل العالمية، نحدد سياسة انتهاء صلاحية (Cache TTL) لمدة 15 دقيقة؛ إذا فتح المستخدم التطبيق يرى البيانات المخزنة فوراً، ويبدأ RemoteMediator تلقائياً في الخلفية بجلب أحدث المقالات دون حجب الواجهة.",
        "how_to_answer_ar": "وضح المعمارية ثلاثية الأبعاد: واجهة Compose تعرض PagingData، وقاعدة بيانات Room تعمل كمخزن محلي، و RemoteMediator ينسق جلب البيانات من الشبكة. اشرح دور جدول الـ RemoteKeys في تتبع مفاتيح الصفحات السابقة والتالية، وبين كيف تحمي هذه المعمارية ذاكرة التطبيق من الانهيار.",
        "talking_points_ar": "مكتبة Jetpack Paging 3، ودور RemoteMediator، وجدول RemoteKeys، والتحكم في كاش SQLite Cursor Window، وسياسات التحميل المسبق (Prefetch Distance).",
        "follow_ups_ar": "- **المحاور:** \"لماذا نستخدم جدولاً منفصلاً يسمى RemoteKeys بدلاً من تخزين رقم الصفحة في نفس جدول الكيان؟\"\n  **المرشح:** \"لأن رقم الصفحة ليس من خصائص العنصر التجارية وقد يتغير عند إضافة عناصر جديدة في السيرفر، وتخزينه في جدول مستقل يسمح بتنظيفه وتحديثه بحرية دون لمس بيانات الكيان الأصلية.\"\n\n- **المحاور:** \"كيف تمنع وميض الشاشة (Flicker) أثناء تحديث عناصر القائمة في Compose؟\"\n  **المرشح:** \"باستخدام مفاتيح تعريفية ثابتة `key = { it.id }` داخل `items()` في `LazyColumn`؛ هذا يتيح لـ Compose معرفة العناصر التي تغيرت وتحديثها فقط دون إعادة رسم القائمة بأكملها.\"",
        "self_check_ar": "هل شرحت تكامل Paging 3 مع Room؟ هل وضحت وظيفة RemoteMediator وجدول RemoteKeys؟ وهل بينت كيفية إدارة الذاكرة وتفادي OOM؟",
        "references_ar": f"- [Paging 3 library overview](https://developer.android.com/topic/libraries/architecture/paging/v3-overview) — دليل جوجل الرسمي لتقسيم الصفحات في أندرويد.\n- [Page from network and database with RemoteMediator](https://developer.android.com/topic/libraries/architecture/paging/v3-network-db) — الدليل الشامل لربط قاعدة البيانات بالشبكة في Paging 3.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "نصمم نظام التخزين المؤقت وتقسيم الصفحات بدمج Jetpack Paging 3 مع قاعدة بيانات Room بواسطة RemoteMediator. تقرأ الواجهة بيانات القائمة مباشرة من قاعدة البيانات المحلية عبر تدفق PagingData لعرض فوري وسلس دون استهلاك زائد للرام. وعند اقتراب المستخدم من نهاية القائمة، يتولى RemoteMediator جلب الصفحة التالية من الشبكة وتخزينها في Room مع مفاتيح الصفحات في معاملة ذرية واحدة.",
        "best_answer_ar": "تصميم نظام تقسيم الصفحات والتخزين المؤقت في تطبيقات الإنتاج الضخمة يعتمد على معمارية هجينة تجمع بين كفاءة Room ومكتبة Jetpack Paging 3.\n\nالمبدأ المعماري الحاكم هو أن القوائم المعروضة على الشاشة لا تتغذى من الشبكة مباشرة، لأن حفظ مئات العناصر والصور في الذاكرة الحية يسبب توقفات متكررة لجامع القمامة Garbage Collection وقد ينتهي بانهيار التطبيق بـ OutOfMemoryError. بدلاً من ذلك، نستخدم Room كمخزن مؤقت للقرص، ونربطه بواجهة الـ Compose عبر `PagingSource` الذي يقوم بجلب نوافذ صغيرة من البيانات عبر SQLite Cursor حسب موضع التمرير الفعلي للمستخدم.\n\nوعندما يقترب المستخدم من حافة التمرير، تستدعي المكتبة مكون `RemoteMediator`؛ حيث يقرأ مفتاح الصفحة التالية من جدول منفصل يسمى `RemoteKeys`، ويرسل طلب الشبكة لجلب البيانات الجديدة. وفور وصول الاستجابة، نفتح معاملة ذرية `database.withTransaction` نحفظ فيها العناصر الجديدة ونحدث مفاتيح الصفحات في وقت واحد. وبفضل التدفق التفاعلي لـ Room، تظهر العناصر الجديدة في القائمة بنعومة وسلاسة 120 إطاراً في الثانية مع دعم كامل للعمل دون اتصال بالإنترنت.",
        "deep_answer_ar": "تحت الكابوت، تكمن قوة Paging 3 مع RemoteMediator في السيطرة الدقيقة على استهلاك الذاكرة وتجنب التناقض الزمني في البيانات المقسمة.\n\nعندما تطلب الواجهة تحديثاً كاملاً عبر السحب للأسفل Pull-To-Refresh، يمرر الرنتايم نوع التحميل `LoadType.REFRESH`. هنا يجب فتح معاملة ذرية لتنظيف مفاتيح الصفحات القديمة وحفظ العناصر الجديدة لتجنب عرض عناصر مكررة. كما نحتفظ بجدول `RemoteKeys` مستقلاً تماماً؛ لأن الاعتماد على مجرد عداد الصفحات قد يتسبب في تكرار العناصر إذا تم نشر مقال جديد على السيرفر أثناء تصفح المستخدم، مما يغير حدود الصفحات، لذا نفضل مفاتيح التمرير المعتمدة على المؤشرات (Cursor-Based Pagination Tokens).\n\nوعلى صعيد واجهة المستخدم في Jetpack Compose، نلزم المطورين بتمرير معرف فريد ومستقر لكل عنصر عبر باراميتر `key` في `LazyColumn`. هذا يمنع المحرك من إعادة إنشاء المكونات الرسومية بالكامل ويسمح له بنقل العناصر المتحركة بسلاسة. وإذا فشل طلب الشبكة أثناء التمرير، يمرر RemoteMediator حالة الخطأ إلى كائن `CombinedLoadStates`، مما يسمح للواجهة بعرض زر إعادة المحاولة المدمج في ذيل القائمة دون أن يفقد المستخدم ما تم تحميله مسبقاً، محققاً أعلى معايير استقرار التطبيقات عالمياً.\n\nولتفادي تجاوز حد الـ CursorWindow البالغ 2 ميجابايت في محرك SQLite عند عرض قوائم غنية بالوسائط، نحرص في استعلامات Room على جلب الحقول المعروضة فقط لتجنب استثناء CursorWindowAllocationException عند التمرير السريع."
    }
}

# ==========================================
# SYS-07: Design a notification system with deep links.
# ==========================================
DATA["SYS-07"] = {
    "concept_en": """Designing a mobile push notification and deep-link routing system requires orchestrating multiple ingress pathways: Firebase Cloud Messaging (FCM) data/notification payloads, verified Android App Links (HTTPS), custom URI schemes, and local alarms. The architecture must accommodate all application lifecycle phases: cold start from process death, warm start from background state, and active foreground execution. Core technical requirements include: decoupling sensitive data from push payloads (passing lightweight IDs and fetching details from authenticated APIs), centralizing URI parsing and permission validation within a dedicated DeepLinkRouter, constructing logical synthetic back-stacks via TaskStackBuilder so pressing the back button navigates up to parent screens rather than exiting the application, and ensuring full compliance with Android 12+ trampoline restrictions and Android 13+ POST_NOTIFICATIONS runtime permissions.""",
    "walkthrough_en": """Implementing a secure notification dispatcher and synthetic back-stack routing:
```kotlin
// 1. Firebase Messaging Service receiving payloads and dispatching notifications
class AppFirebaseMessagingService : FirebaseMessagingService() {

    override fun onMessageReceived(remoteMessage: RemoteMessage) {
        val data = remoteMessage.data
        val targetUri = data["deep_link_uri"] ?: return
        val title = data["title"] ?: "New Notification"
        val message = data["message"] ?: ""

        sendNotification(title, message, Uri.parse(targetUri))
    }

    private fun sendNotification(title: String, message: String, deepLink: Uri) {
        val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        val channelId = "critical_updates_channel"

        // Construct synthetic back-stack targeting DeepLinkDispatchActivity
        val intent = Intent(this, MainActivity::class.java).apply {
            action = Intent.ACTION_VIEW
            this.data = deepLink
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
        }

        val pendingIntent = TaskStackBuilder.create(this).run {
            addNextIntentWithParentStack(intent)
            getPendingIntent(
                deepLink.hashCode(),
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
            )
        }

        val notification = NotificationCompat.Builder(this, channelId)
            .setSmallIcon(R.drawable.ic_notification)
            .setContentTitle(title)
            .setContentText(message)
            .setAutoCancel(true)
            .setContentIntent(pendingIntent)
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .build()

        notificationManager.notify(deepLink.hashCode(), notification)
    }
}

// 2. Centralized Deep Link Router validating routes and user authorization
object DeepLinkRouter {
    fun route(context: Context, uri: Uri, isAuthenticated: Boolean): NavigationCommand {
        val path = uri.path ?: return NavigationCommand.ToHome

        // Route validation and auth gatekeeper
        return when {
            path.startsWith("/orders/") -> {
                val orderId = uri.lastPathSegment ?: ""
                if (isAuthenticated) {
                    NavigationCommand.ToOrderDetail(orderId)
                } else {
                    NavigationCommand.ToLogin(redirectUri = uri)
                }
            }
            path.startsWith("/promo/") -> NavigationCommand.ToPromo(uri.getQueryParameter("code") ?: "")
            else -> NavigationCommand.ToHome
        }
    }
}

sealed interface NavigationCommand {
    data object ToHome : NavigationCommand
    data class ToOrderDetail(val orderId: String) : NavigationCommand
    data class ToLogin(val redirectUri: Uri) : NavigationCommand
    data class ToPromo(val code: String) : NavigationCommand
}
```""",
    "short_en": """We design notification and deep-link systems using Firebase Cloud Messaging, a centralized DeepLinkRouter, and TaskStackBuilder. Push payloads contain only metadata and target URIs rather than raw sensitive data. When tapped, the router parses and validates the deep link, constructs a proper synthetic back-stack so pressing back returns to the parent screen, and handles user authentication status before routing to the destination.""",
    "structured_en": """A robust push notification and deep linking architecture guarantees secure delivery, seamless routing, and proper back-stack reconstruction across all application lifecycle states.
In the data layer, our FirebaseMessagingService receives push payloads containing lightweight metadata and action URIs, never sensitive personal data.
If the app is in the background or killed, the system tray notification carries a PendingIntent targeting our centralized DeepLinkRouter.
When the user taps the notification, the router intercepts the URI, verifies user authentication state, and validates target parameters against an authorized routing registry to prevent malicious link injection.
To maintain an intuitive user experience, we use Android's TaskStackBuilder to construct a synthetic back-stack.
For example, deep linking directly into an order details screen synthesizes the order history and home screens beneath it, ensuring that pressing the back button navigates logically upward instead of abruptly exiting to the Android home screen.
If the destination requires authentication and the user is logged out, the router caches the pending deep link and resumes navigation after successful login.""",
    "deep_senior_en": """From a systems architecture standpoint, handling deep links reliably requires accommodating cold starts, process death, and platform version discrepancies.
On Android 12 and above, the operating system enforces strict trampoline restrictions, blocking broadcast receivers and background services from starting activities directly.
Consequently, all notification PendingIntents must launch an Activity directly or dispatch through an immutable PendingIntent with the FLAG_IMMUTABLE flag.
In cold-start scenarios, the target screen often depends on essential asynchronous initialization, such as session validation, remote config fetching, or database decryption.
If the deep link routes immediately before these dependencies are ready, the app risks crashing or leaking unauthenticated screens.
Our architecture uses an application-level NavigationCoordinator that checks the startup readiness state.
If initialization is pending, the coordinator enqueues the deep-link command until authentication and configuration resolve.
Furthermore, we implement Android App Links with verified digital asset links on the web server, ensuring that verified HTTPS URLs open our app directly without displaying the ambiguous Android disambiguation dialog.
Finally, we sanitize all incoming URI query parameters against path traversal and SQL injection vectors before passing arguments to ViewModels, safeguarding internal application boundaries.
We also configure notification channels with clear user-facing importance levels and manage dynamic badge counts through OEM-compatible badge APIs, ensuring consistent visual affordance across varied device manufacturers.""",
    "meta_ar": {
        "id": "SYS-07",
        "questionAr": "كيف تصمم نظام إشعارات (Push Notifications) مع روابط عميقة (Deep Links) وبناء مكدس التنقل؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على معالجة إشعارات FCM في مختلف حالات دورة حياة التطبيق، وإعادة بناء مكدس التنقل الخلفي عبر TaskStackBuilder، وتأمين الروابط العميقة، والالتزام بقيود Android 12+ Trampolines.",
        "concept_ar": "تصميم نظام الإشعارات والروابط العميقة يتطلب التعامل مع مسارات متعددة تشمل إشعارات FCM والروابط الموثقة Android App Links. يجب أن تحتوي حزم الإشعارات على معرفات ومعلومات توجيه فقط دون بيانات سرية، مع توجيه المستخدم عبر موجه مركزي DeepLinkRouter يتحقق من تسجيل الدخول قبل فتح الشاشة. كما يجب استخدام TaskStackBuilder لإعادة بناء مكدس التنقل الخلفي الاصطناعي (Synthetic Back-Stack) حتى لا يخرج المستخدم من التطبيق عند الضغط على زر الرجوع.",
        "walkthrough_ar": "تطبيق استقبال إشعارات FCM وبناء مكدس الرجوع وتوجيه الروابط العميقة بأمان:\n```kotlin\nclass PushService : FirebaseMessagingService() {\n    override fun onMessageReceived(msg: RemoteMessage) {\n        val uri = Uri.parse(msg.data[\"deep_link\"] ?: return)\n        val intent = Intent(this, MainActivity::class.java).apply { data = uri }\n        val pendingIntent = TaskStackBuilder.create(this).run {\n            addNextIntentWithParentStack(intent)\n            getPendingIntent(0, PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)\n        }\n        val notification = NotificationCompat.Builder(this, \"default_channel\")\n            .setContentIntent(pendingIntent)\n            .setAutoCancel(true)\n            .setContentTitle(msg.data[\"title\"])\n            .build()\n        NotificationManagerCompat.from(this).notify(1, notification)\n    }\n}\n```",
        "why_it_matters_ar": "إذا لم يتم بناء مكدس التنقل الخلفي، فإن المستخدم عندما يفتح إشعار تفاصيل الطلب ويضغط زر الرجوع سيخرج فوراً إلى شاشة الهاتف الرئيسية، مما يقطع رحلة الاستخدام ويحرم التطبيق من استكشاف باقي الميزات.",
        "worked_example_ar": "معالجة التوجيه في حالة كان المستخدم غير مسجل الدخول وحفظ الرابط للعودة بعد التسجيل:\n```kotlin\nfun handleDeepLink(uri: Uri, isAuth: Boolean) {\n    if (requiresAuth(uri) && !isAuth) {\n        sessionManager.setPendingDeepLink(uri)\n        navController.navigate(\"login_screen\")\n    } else {\n        navController.navigate(uri.toRoute())\n    }\n}\n```",
        "trade_offs_ar": "إرسال البيانات الكاملة داخل حزمة الإشعار يتيح عرض المحتوى فوراً لكنه يشكل خطراً أمنياً إذا تم اعتراضه، بينما إرسال المعرف فقط (ID) يتطلب طلباً شبكياً عند الفتح ولكنه يحمي الخصوصية تماماً.",
        "failure_modes_ar": "مخالفة قيود Notification Trampolines في أندرويد 12 بتشغيل Service من الـ Notification بدلاً من فتح Activity مباشرة، أو عدم فحص وتطهير باراميترات الرابط مما يفتح ثغرات أمنية في التطبيق.",
        "production_perspective_ar": "في التطبيقات العالمية، نوثق نطاقات الروابط عبر ملف assetlinks.json على السيرفر لتفعيل Android App Links وتفادي ظهور مربع الحوار المربك للمستخدم، مع تتبع معدل فتح الإشعارات بدقة عبر Firebase Analytics.",
        "how_to_answer_ar": "ابدأ بطبقة البيانات والأمان: حزم الـ Push تحتوي فقط على بيانات توجيه خفيفة. ثم اشرح معالجة الإشعار في الخلفية وبناء PendingIntent غير قابل للتعديل (FLAG_IMMUTABLE). ركز على دور TaskStackBuilder في بناء مكدس الرجوع الاصطناعي، واشرح كيف يتعامل الـ Router مع المستخدم إذا كان غير مسجل الدخول.",
        "talking_points_ar": "خدمة Firebase Cloud Messaging، وبناء مكدس الرجوع بـ TaskStackBuilder، وقيود Notification Trampolines في أندرويد 12، وروابط Android App Links والتحقق بـ assetlinks.json، وأمان الروابط العميقة.",
        "follow_ups_ar": "- **المحاور:** \"ما هي قيود الـ Notification Trampolines التي فرضتها جوجل في أندرويد 12؟\"\n  **المرشح:** \"منعت جوجل فتح الأنشطة (Activities) بشكل غير مباشر عبر Service أو BroadcastReceiver من الإشعار؛ يجب أن يشير الـ PendingIntent مباشرة إلى الـ Activity وإلا سيقوم النظام بحجب الفتح وإلقاء خطأ في الـ Log.\"\n\n- **المحاور:** \"ماذا تفعل لو فتح المستخدم رابط إشعار لصفحة حساسة وهو غير مسجل الدخول؟\"\n  **المرشح:** \"أقوم بتعليق التوجيه وحفظ الرابط في الـ SessionManager، ثم توجيه المستخدم لشاشة تسجيل الدخول، وفور نجاح المصادقة أسترجع الرابط وأكمل التوجيه للوجهة المطلوبة بسلاسة.\"",
        "self_check_ar": "هل ذكرت استخدام TaskStackBuilder لبناء مكدس الرجوع؟ هل راعيت أمان الروابط العميقة وتطهير المدخلات؟ وهل التزمت بقيود أندرويد 12 للإشعارات؟",
        "references_ar": f"- [Create a Deep Link for a Destination](https://developer.android.com/guide/navigation/design/deep-link) — توثيق جوجل الرسمي لتصميم وإدارة الروابط العميقة.\n- [Notification Trampoline Restrictions in Android 12](https://developer.android.com/about/versions/12/behavior-changes-12#notification-trampolines) — التغييرات السلوكية لإشعارات أندرويد 12.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "نصمم نظام الإشعارات والروابط العميقة بالاعتماد على Firebase Cloud Messaging وموجه مركزي DeepLinkRouter وأداة TaskStackBuilder. نحرص على ألا تحمل حزم الـ Push سوى معرفات وروابط خفيفة دون بيانات حساسة. وعند النقر على الإشعار، يتحقق الموجه من حالة تسجيل الدخول وصلاحية الرابط، ويقوم TaskStackBuilder ببناء مكدس رجوع اصطناعي لضمان عودة المستخدم للشاشات الأب عند الضغط على زر الرجوع بدلاً من الخروج من التطبيق.",
        "best_answer_ar": "بناء معمارية إشعارات وروابط عميقة موثوقة في أندرويد يتطلب التنسيق بين قنوات الوصول المختلفة وإعادة بناء مكدس التنقل وحماية خصوصية المستخدم.\n\nفي طبقة الاستقبال، تتلقى خدمة FirebaseMessagingService رسائل الـ Data Payloads التي تحتوي على عنوان الإشعار ورابط التنقل فقط، متجنبين تماماً إرسال نصوص حساسة مثل الأرصدة البنكية عبر قنوات الـ Push العامة. ونقوم ببناء الـ PendingIntent الخاص بالإشعار باستخدام علم FLAG_IMMUTABLE وفق متطلبات أندرويد الحديثة.\n\nالمعيار الهندسي الأهم لتجربة المستخدم هو استخدام TaskStackBuilder لبناء مكدس الرجوع الاصطناعي (Synthetic Back-Stack). إذا وصل إشعار بخصم مالي ونقر عليه المستخدم، فإن النظام لا يفتح شاشة تفاصيل المعاملة كجزيرة منعزلة؛ بل يقوم الـ StackBuilder بإدراج شاشة قائمة الحسابات والشاشة الرئيسية في خلفيتها. وبالتالي، عندما يضغط المستخدم زر الرجوع في الهاتف، يصعد منطقياً للشاشة السابقة بدلاً من أن يغلق التطبيق في وجهه فجأة. كما نربط كل الروابط بموجه تنقل موحد يتحقق من حالة المصادقة ويعلق الرابط لحين تسجيل الدخول إذا كانت الجلسة منتهية.",
        "deep_answer_ar": "الرؤية المتقدمة لتصميم الروابط العميقة والإشعارات تتعامل مع تحديات بدء التشغيل البارد (Cold Start) وقيود نظام أندرويد الصارمة على مستوى الأمان والتنفيذ.\n\nمنذ أندرويد 12، حظرت جوجل ما يعرف بـ Notification Trampolines، وهي الممارسة القديمة التي تطلق BroadcastReceiver لمعالجة الإحصائيات قبل فتح الشاشة؛ انتهاك هذا الحظر يؤدي لتجاهل النظام للنقرة وظهور بطء شديد. لذلك نوجه الـ PendingIntent مباشرة نحو النشاط الرئيسي، ونعهد بمهمة التوجيه لمكون NavigationCoordinator.\n\nوفي حالات البدء البارد، عندما يكون التطبيق مقفلاً في الذاكرة، قد يستغرق تهيئة حقن التبعيات بـ Hilt وتحميل إعدادات التشفير وفحص الجلسة بضع مئات من الأجزاء من الثانية. إذا حاول الرابط العميق فتح ViewModel يعتمد على بيانات مستخدم غير محملة بعد، فسينهار التطبيق حتماً بـ NullPointerException. لذلك نصمم طابور انتظار للأوامر (Navigation Command Queue)؛ حيث يستقبل الـ Router الرابط ويفحصه ضد هجمات الـ Path Traversal، ثم ينتظر إشارة الجاهزية isInitialized من الـ Application قبل تفريغ أمر التنقل. كما نقوم بإعداد روابط الويب عبر Android App Links بملف assetlinks.json المعتمد على نطاق HTTPS، مما يضمن فتح التطبيق مباشرة دون إظهار نافذة الاختيار المربكة للمستخدم.\n\nكما ندير قنوات الإشعارات (Notification Channels) بوعي تقني عالي مع تحديد مستويات الأهمية المناسبة، والتعامل مع قيود استهلاك البطارية الصارمة التي يفرضها مصنعو الهواتف الذكية لضمان تسليم الإشعارات في موعدها."
    }
}

# ==========================================
# SYS-08: Design a feature flags and staged rollout system.
# ==========================================
DATA["SYS-08"] = {
    "concept_en": """A feature flag and staged rollout architecture enables continuous integration, trunk-based development, dark launching, A/B experimentation, and emergency operational kill switches without publishing new APKs. Core system components include: strongly typed flag definitions (Boolean, String, JSON, and Multivariant), a multi-tiered evaluation hierarchy (local compile-time defaults, cached server configs, and runtime debug overrides), deterministic percentage hashing using stable client identifiers (such as hashing the user ID combined with the feature key modulo 100), offline caching in Proto DataStore or EncryptedSharedPreferences, and operational kill switches capable of instantly deactivating malfunctioning code paths via high-priority silent pushes or startup configuration polling.""",
    "walkthrough_en": """Implementing a typed feature flag manager with deterministic rollout hashing and kill switches:
```kotlin
// 1. Strongly typed feature flag definitions with default fallbacks
enum class FeatureFlag(val key: String, val defaultValue: Boolean) {
    NEW_CHECKOUT_FLOW("new_checkout_flow_enabled", defaultValue = false),
    BIOMETRIC_AUTH("biometric_auth_v2_enabled", defaultValue = true),
    DARK_MODE_V2("dark_mode_v2_enabled", defaultValue = false)
}

// 2. Feature Flag Manager with deterministic user hashing and local caching
class FeatureFlagManager @Inject constructor(
    private val localConfigStore: SharedPreferences,
    private val sessionManager: SessionManager
) {
    // Kill switches that take immediate precedence
    private val killSwitches = ConcurrentHashMap<String, Boolean>()

    fun isFeatureEnabled(flag: FeatureFlag): Boolean {
        // Priority 1: Emergency Kill Switch
        killSwitches[flag.key]?.let { isKilled ->
            if (isKilled) return false
        }

        // Priority 2: Cached remote configuration
        if (localConfigStore.contains(flag.key)) {
            return localConfigStore.getBoolean(flag.key, flag.defaultValue)
        }

        // Priority 3: Bundled compile-time default
        return flag.defaultValue
    }

    // Deterministic rollout bucket calculation (0-99%) based on stable User ID
    fun isUserInRolloutBucket(flagKey: String, rolloutPercentage: Int): Boolean {
        val userId = sessionManager.getUserId() ?: return false
        val hash = (userId + flagKey).hashCode().absoluteValue % 100
        return hash < rolloutPercentage
    }

    fun applyEmergencyKillSwitch(flagKey: String) {
        killSwitches[flagKey] = true
    }

    fun updateRemoteFlags(flags: Map<String, Boolean>) {
        localConfigStore.edit().apply {
            flags.forEach { (key, value) -> putBoolean(key, value) }
            apply()
        }
    }
}
```""",
    "short_en": """We design feature flags using strongly typed definitions evaluated through a multi-tiered provider system. The system evaluates local build-time defaults, cached remote configs, and debug overrides. Staged percentage rollouts use deterministic hashing on user IDs to ensure stable feature assignment. Critical flags support emergency kill switches fetched at startup or via silent push, allowing instant feature deactivation without requiring new app releases.""",
    "structured_en": """A production feature flag architecture separates software deployment from feature release, enabling safe staged rollouts and emergency remediation.
We model all feature flags as strongly typed enums or value classes with compile-time default values to prevent null pointer exceptions if the network is unreachable.
The evaluation engine resolves flags across a tiered hierarchy: developer debug overrides take precedence during testing, followed by cached server-delivered configurations, falling back to bundled hardcoded defaults.
For staged rollouts, we calculate a deterministic hash of the user ID combined with the feature key, mapping the result to a percentile between zero and one hundred.
This guarantees that a user assigned to a ten percent rollout bucket consistently experiences the feature across app restarts and device rotations without requiring persistent server state.
To mitigate production incidents, our architecture includes a remote kill switch mechanism.
By sending a high-priority silent push or polling lightweight config endpoints on startup, we can deactivate a malfunctioning feature globally within seconds, completely isolating production issues without waiting for Play Store review cycles.""",
    "deep_senior_en": """At enterprise scale, the primary hazards of feature flagging are technical debt accumulation, stale flag pollution, and subtle race conditions during startup.
If an app evaluates flags dynamically during mid-session flows, a user could see a screen change its layout or business rules while interacting with it, creating severe UI confusion.
We address this by establishing flag evaluation lifecycles: flags are classified as startup-bound, session-bound, or dynamic.
Startup-bound flags, such as new architecture migrations or core database schemas, are evaluated once during Application initialization from cached disk storage (such as Proto DataStore) and frozen for the remainder of the process.
Session-bound flags are refreshed upon cold startup or user login and held immutable throughout the active user session.
Furthermore, stale flags represent dead code paths that complicate unit tests and bloat bytecode.
We enforce automated flag governance: every feature flag definition in code includes an expiration date and owner metadata.
If a flag remains in the codebase beyond its target deprecation date, our CI lint check fails the build, prompting engineers to clean up the code branch and remove obsolete conditions.
Finally, we integrate flag evaluation events directly into our analytics pipeline, tagging every crash report and business event with the active variant bucket to ensure statistically sound A/B experimentation without client attribution bias.
This disciplined approach guarantees operational agility without sacrificing codebase maintainability.""",
    "meta_ar": {
        "id": "SYS-08",
        "questionAr": "كيف تصمم نظام Feature Flags و Staged Rollout مع زر إيقاف فوري (Kill Switch) ودعم Offline؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على فصل نشر الكود عن إطلاق الميزات، وتصميم نظام Feature Flags متعدد الطبقات، وحساب نسب الطرح التدريجي عبر الـ Hashing الحتمي، وتفعيل مفاتيح الإلغاء الفوري Kill Switch.",
        "concept_ar": "نظام الـ Feature Flags يسمح بإطلاق الميزات تدريجياً وإجراء اختبارات A/B والتحكم في إيقاف الميزات المعطوبة فوراً دون الحاجة لتحديث التطبيق من المتجر. يتكون النظام من تعريفات صارمة للأنواع (Typed Flags)، ومحرك تقييم متعدد المستويات (قيم افتراضية مدمجة، كاش محلي في DataStore، وتعديلات المطورين أثناء الاختبار). ويتم حساب نسب الطرح التدريجي (مثلاً 10%) عبر خوارزمية Hashing حتمية لمعرف المستخدم واسم الميزة لضمان ثبات التجربة لنفس المستخدم.",
        "walkthrough_ar": "تطبيق محرك Feature Flags يدعم التقييم متعدد الطبقات وزر الإيقاف الفوري:\n```kotlin\nenum class FeatureFlag(val key: String, val defaultValue: Boolean) {\n    NEW_CHECKOUT(\"new_checkout_enabled\", false),\n    DARK_MODE(\"dark_mode_enabled\", true)\n}\n\nclass FeatureFlagManager(private val prefs: SharedPreferences) {\n    private val killSwitches = ConcurrentHashMap<String, Boolean>()\n\n    fun isEnabled(flag: FeatureFlag): Boolean {\n        if (killSwitches[flag.key] == true) return false\n        return if (prefs.contains(flag.key)) prefs.getBoolean(flag.key, flag.defaultValue) else flag.defaultValue\n    }\n\n    fun isUserInBucket(userId: String, flagKey: String, percentage: Int): Boolean {\n        val bucket = (userId + flagKey).hashCode().absoluteValue % 100\n        return bucket < percentage\n    }\n}\n```",
        "why_it_matters_ar": "إطلاق ميزة برمجية جديدة لجميع المستخدمين دفعة واحدة قد يؤدي لانهيار التطبيق أو توقف المبيعات إذا ظهر خطأ غير متوقع؛ وجود Feature Flag مع Kill Switch يتيح تعطيل الميزة في خمس ثوانٍ وإنقاذ الشركة من كارثة دون انتظار مراجعة جوجل بلاي.",
        "worked_example_ar": "نموذج فحص إيقاف الميزة قبل فتح الشاشة وتوجيه المستخدم للواجهة القديمة بأمان:\n```kotlin\nfun openCheckout(nav: NavController, flags: FeatureFlagManager) {\n    if (flags.isEnabled(FeatureFlag.NEW_CHECKOUT)) {\n        nav.navigate(\"checkout_v2\")\n    } else {\n        nav.navigate(\"checkout_legacy\")\n    }\n}\n```",
        "trade_offs_ar": "إضافة أعلام كثيرة يزيد من مرونة التطبيق والتحكم، ولكنه يضاعف عدد مسارات الكود المتفرعة مما يعقد اختبارات الـ Unit ويراكم ديوناً تقنية ضخمة (Technical Debt) إذا لم يتم حذف الأعلام المنتهية.",
        "failure_modes_ar": "تغير قيمة العلم في منتصف جلسة المستخدم مما يسبب ارتباكاً أو انهياراً في واجهة العرض، أو تأخير فتح التطبيق بانتظار استجابة السيرفر لجلب الأعلام بدلاً من القراءة من الكاش المحلي.",
        "production_perspective_ar": "في الشركات الكبرى، نحدد دورة حياة لكل علم (Flag Lifecycle)؛ فالعلم يعتبر مؤقتاً وله تاريخ انتهاء محدد بـ 90 يوماً ويقوم روبوت الـ CI بإسقاط الـ PR إذا لم يقم الفريق بتنظيف الكود القديم وحذف العلم بعد استقرار الميزة بنسبة 100%.",
        "how_to_answer_ar": "اشرح الفكرة المعمارية: فصل نشر الكود (Deployment) عن إطلاق الميزة (Release). وضح مستويات التقييم الثلاثة: قيم مدمجة في الكود، كاش محلي سريع، وقيم السيرفر. اشرح كيف تحسب نسب الـ Rollout عبر Hashing معرف المستخدم، وركز على دور الـ Kill Switch في الاستجابة السريعة للطوارئ عبر Silent Push.",
        "talking_points_ar": "فصل النشر عن الإطلاق، وحساب النسب بالـ Deterministic Hashing، ومستويات تقييم الأعلام (Startup مقابل Session)، وتثبيت القيم في DataStore، وتنظيف ديون الأعلام عبر الـ CI Linters.",
        "follow_ups_ar": "- **المحاور:** \"كيف تضمن أن المستخدم الذي وقع ضمن شريحة الـ 10% لا تتغير تجربته عند إعادة تشغيل التطبيق؟\"\n  **المرشح:** \"باستخدام Hashing حتمي لمعرف المستخدم الثابت مدمجاً مع اسم الميزة `(userId + flagKey).hashCode() % 100`؛ هذه المعادلة الرياضية ترجع دائماً نفس الرقم لنفس المستخدم دون الحاجة لتخزين حالته على السيرفر.\"\n\n- **المحاور:** \"ماذا تفعل لو أدى إطلاق ميزة جديدة لانهيارات واسعة في الإنتاج؟\"\n  **المرشح:** \"أفعل زر الـ Kill Switch فوراً من لوحة التحكم، حيث يستقبل التطبيق إشعار Silent Push سريع أو يقرأ التحديث عند بدء التشغيل، مما يعطل مسار الكود الجديد ويعيد المستخدمين للمسار القديم المستقر في ثوانٍ.\"",
        "self_check_ar": "هل بينت كيف يعمل الـ Rollout التدريجي؟ هل شرحت دور الـ Kill Switch في الطوارئ؟ وهل أوضحت كيفية إدارة ديون الأعلام البرمجية القديمة؟",
        "references_ar": f"- [Firebase Remote Config documentation](https://firebase.google.com/docs/remote-config) — دليل فايربيز لإدارة الإعدادات والأعلام عن بُعد.\n- [Martin Fowler: Feature Toggles](https://martinfowler.com/articles/feature-toggles.html) — المرجع الكلاسيكي العالمي لأنماط واستراتيجيات الـ Feature Flags.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "نصمم نظام Feature Flags بتعريفات صارمة للأنواع يتم تقييمها عبر نظام متعدد الطبقات يقرأ من القيم الافتراضية المدمجة في الكود والكاش المحلي المخزن في DataStore وإعدادات السيرفر. نعتمد على Hashing حتمي لمعرف المستخدم لتوزيع نسب الطرح التدريجي بثبات، مع توفير زر إيقاف فوري Kill Switch يتم تفعيله عبر إشعار صامت أو عند بدء التشغيل لإلغاء أي ميزة معطوبة فوراً دون انتظار إصدار جديد.",
        "best_answer_ar": "فصل عملية نشر الكود البرمجي عن إطلاق الميزات للمستخدمين هو جوهر استقرار وتطور التطبيقات الحديثة في بيئات العمل الكبرى.\n\nنصمم كل علم بربحه بنوع صريح (Enum أو Value Class) ونرفق معه قيمة افتراضية مدمجة برمجياً لتفادي أي استثناء Null إذا تعذر الاتصال بالسيرفر. ويتبع محرك التقييم تسلسلاً هرمياً واضحاً؛ حيث تمنح الأولوية لأزرار الطوارئ Kill Switches، ثم إعدادات المطورين أثناء الاختبار، ثم الإعدادات المحملة من السيرفر والمخزنة محلياً في DataStore، وأخيراً القيم الافتراضية المدمجة.\n\nولتنفيذ الطرح التدريجي (Staged Rollout) بنسب محددة مثل 10% أو 50%، لا نعتمد على أرقام عشوائية، بل نطبق خوارزمية Hashing حتمية تجمع معرف المستخدم مع اسم العلم وتأخذ باقي القسمة على مئة. هذا يضمن أن المستخدم يظل في نفس الشريحة دائماً عند تدوير الشاشة أو إعادة فتح التطبيق. وإذا تسببت الميزة الجديدة في أي مشاكل، يمكننا من خلال السيرفر تفعيل الـ Kill Switch عالمياً في ثوانٍ ليعود التطبيق تلقائياً إلى مسار الكود القديم المستقر دون الحاجة لرفع تحديث جديد إلى متجر جوجل بلاي.",
        "deep_answer_ar": "على المستوى المتقدم، يتمثل التحدي الأكبر في إدارة دورة حياة الأعلام داخل الذاكرة وتفادي الديون التقنية وتشتت واجهة المستخدم.\n\nإذا قمنا بتقييم الأعلام بشكل ديناميكي لحظي أثناء تنقل المستخدم، فقد يرى المستخدم شاشة تغير تصميمها أو سلوكها في منتصف التفاعل، مما يسبب ارتباكاً حاداً. لذلك نقسم الأعلام لثلاث فئات: أعلام مرتبطة ببدء التشغيل (Startup-bound) يتم تقييمها وتجميدها في مساحة الذاكرة أثناء تهيئة كلاس الـ Application من القرص، وأعلام مرتبطة بالجلسة (Session-bound) يتم تثبيتها فور تسجيل الدخول وتظل غير قابلة للتغيير طوال الجلسة، وأعلام حركية للمحتوى الترويجي.\n\nكما أن التراكم العشوائي لأعلام الـ Feature Flags يمثل سمّاً برمجياً بطيئاً يعقد فروع الكود واختبارات الـ Unit Tests ويزيد من حجم الـ Bytecode. ولمواجهة ذلك، نلزم الفرق بسياسة حوكمة آلية؛ حيث يحتوي كل تعريف للعلم على تاريخ انتهاء ومسؤول محدد. وإذا تخطى العلم مدة 90 يوماً في الكود بعد اكتمال إطلاقه، يقوم فحص مخصص في الـ CI Linter بإسقاط أي دمج للكود حتى يقوم الفريق بمسح فروع الـ if-else القديمة وتنظيف الكود، مما يضمن الحفاظ على معمارية نظيفة ومرنة.\n\nوأخيراً، نربط متغيرات الأعلام بكل أحداث التحليلات وسجلات Crashlytics، مما يتيح لفريق البيانات مقارنة استقرار النسخة التجريبية مقابل النسخة المستقرة إحصائياً واتخاذ قرارات طرح مدروسة."
    }
}

# ==========================================
# Validation and Execution
# ==========================================
def validate_words():
    print(f"Elevating {len(DATA)} questions in SYS (SYS-01 to SYS-08)...")
    errors = []
    for qid, d in sorted(DATA.items()):
        en_s = len(d["short_en"].split())
        en_st = len(d["structured_en"].split())
        en_d = len(d["deep_senior_en"].split())

        ar_q = len(d["meta_ar"]["quick_answer_ar"].split())
        ar_b = len(d["meta_ar"]["best_answer_ar"].split())
        ar_d = len(d["meta_ar"]["deep_answer_ar"].split())

        print(f"{qid}: en_s={en_s}, en_st={en_st}, en_d={en_d} | ar_q={ar_q}, ar_b={ar_b}, ar_d={ar_d}")

        if not (35 <= en_s <= 110):
            errors.append(f"{qid} en_short invalid: {en_s}")
        if not (100 <= en_st <= 280):
            errors.append(f"{qid} en_structured invalid: {en_st}")
        if not (200 <= en_d <= 650):
            errors.append(f"{qid} en_deep invalid: {en_d}")

        if not (35 <= ar_q <= 110):
            errors.append(f"{qid} ar_quick invalid: {ar_q}")
        if not (90 <= ar_b <= 280):
            errors.append(f"{qid} ar_best invalid: {ar_b}")
        if not (180 <= ar_d <= 650):
            errors.append(f"{qid} ar_deep invalid: {ar_d}")

    if errors:
        print("\nPre-validation word count checks failed! Fix counts before updating files.")
        for e in errors:
            print(f"  ❌ {e}")
        sys.exit(1)
    else:
        print("\nPre-validation word count checks passed! Updating canonical questions...")

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

    ee.save_topic_metadata("sys_01_08", topic_meta)
    ee.merge_all_metadata()

    for qid in sorted(DATA.keys()):
        ee.validate_question(qid)

    print("\nAll 8 SYS questions (SYS-01 to SYS-08) successfully elevated and passed validation!\n")

if __name__ == "__main__":
    apply_elevations()
