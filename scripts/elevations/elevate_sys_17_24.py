#!/usr/bin/env python3
"""
Complete elevation script for SYS questions: SYS-17 to SYS-24.
Topic: Android System Design & Architecture Decisions (SYS)
Phase 4, Batch 3 - Full bilingual parity with all 19 metadata fields
"""

import os
import sys

sys.path.insert(0, os.path.abspath("scripts/elevations"))
import elevation_engine as ee

TOPIC_AR = "تصميم أنظمة وتطبيقات الموبايل (System Design) والقرارات الهندسية"
REVIEWED_DATE_AR = "تمت المراجعة والتحقق في 17 أكتوبر 2026"

DATA = {}

# ==========================================
# SYS-17: How do you design operational monitoring and remote kill switches?
# ==========================================
DATA["SYS-17"] = {
    "concept_en": """Designing enterprise operational monitoring and remote kill switches requires a fail-safe architecture that can disable broken or vulnerable features in real time without waiting for app store review cycles. Remote configuration platforms like Firebase Remote Config or proprietary configuration gateways deliver runtime flags to mobile clients. However, naive implementations introduce dangerous failure modes, such as blocking cold application startup while fetching remote payloads or crashing when flag schemas change. A production-grade kill switch engine evaluates local cached flags from high-speed storage like EncryptedSharedPreferences or MMKV, guaranteeing zero main-thread startup delays. Critical features must operate with conservative fail-safe defaults, meaning that if network connectivity fails or flag payloads are corrupted, the application automatically defaults to disabling experimental or risky code paths. In addition, silent data-only push notifications via Firebase Cloud Messaging enable engineering teams to trigger emergency flag invalidations across active user sessions instantly, protecting production systems from runaway regressions.""",
    "walkthrough_en": """Implementing a fail-safe remote kill switch with instant push invalidation and local caching:
```kotlin
// 1. Thread-safe kill switch manager with high-speed memory caching
class KillSwitchManager @Inject constructor(
    @ApplicationContext private val context: Context,
    private val appScope: CoroutineScope
) {
    private val preferences = context.getSharedPreferences("operational_flags", Context.MODE_PRIVATE)
    private val flagCache = ConcurrentHashMap<String, Boolean>()

    init {
        // Pre-populate memory cache to ensure non-blocking synchronous reads
        preferences.all.forEach { (key, value) ->
            if (value is Boolean) flagCache[key] = value
        }
    }

    // Non-blocking evaluation with safe conservative fallback
    fun isFeatureEnabled(flagKey: String, defaultFallback: Boolean = false): Boolean {
        return flagCache[flagKey] ?: preferences.getBoolean(flagKey, defaultFallback)
    }

    fun applyEmergencyKill(flagKey: String, killFeature: Boolean) {
        val isEnabled = !killFeature
        flagCache[flagKey] = isEnabled
        preferences.edit().putBoolean(flagKey, isEnabled).apply()
    }
}

// 2. High-priority silent FCM push handler for instant remote feature deactivation
class EmergencyRevocationService : FirebaseMessagingService() {
    @Inject lateinit var killSwitchManager: KillSwitchManager

    override fun onMessageReceived(remoteMessage: RemoteMessage) {
        val payload = remoteMessage.data
        if (payload["action"] == "EMERGENCY_KILL_SWITCH") {
            val flagKey = payload["target_feature"] ?: return
            killSwitchManager.applyEmergencyKill(flagKey, killFeature = true)
        }
    }
}
```""",
    "short_en": """We design operational kill switches by pairing remote configuration with high-speed local memory caching to ensure non-blocking cold app startup. We enforce conservative fail-safe defaults when network requests fail, invalidate broken flags in real time via silent push notifications, and monitor crash rates to trigger automatic circuit breakers.""",
    "structured_en": """A resilient kill switch architecture allows mobile teams to deactivate malfunctioning features instantly without submitting emergency app store updates.
I implement a dual-layer configuration engine where remote flags are cached locally in high-speed storage to guarantee zero-latency synchronous checks on the main thread during app launch.
We never block application startup waiting for remote flag fetches. Instead, the app launches with cached values and synchronizes latest flag updates in the background.
Every kill switch defines a strict fail-safe fallback. If remote endpoints fail, the cache is corrupted, or network timeouts occur, the system defaults to the safest baseline, turning off experimental or unverified flows.
For critical operational incidents, we integrate high-priority silent push notifications that command running app instances to invalidate cached flags and shut down broken features within minutes.
Client telemetry continuously streams feature-tagged crash ratios, enabling automated backend alerts that trip remote kill switches when error thresholds are breached.""",
    "deep_senior_en": """From a staff mobile systems perspective, remote kill switches represent the final defensive layer against catastrophic production outages.
The most dangerous vulnerability in feature flagging is flag debt, where deprecated flags linger across the codebase, creating combinatorial testing explosions and obscure regression bugs. We enforce strict lifecycle governance: every flag is assigned an owning team and a mandatory expiration milestone, after which the flag must be removed via automated pull requests.
Client-side evaluation must be completely decoupled from network latency. If a screen checks a feature flag by firing an asynchronous network request, users experience UI flickering or race conditions where experimental views appear halfway through rendering. Pre-warming an in-memory concurrent hash map during early application initialization ensures immediate synchronous flag reads across all UI components.
When dealing with security or data-corrupting vulnerabilities, passive flag synchronization every twelve hours is insufficient. We establish a multi-channel invalidation strategy combining silent high-priority FCM pushes, short polling intervals during active sessions, and cache-busting headers on standard API responses.
Finally, we implement client-side safety circuits. If a newly toggled feature crashes the application repeatedly within sixty seconds of launch, the app increments a local failure counter, detects a crash loop, and autonomously overrides the flag locally, reverting to the stable baseline without requiring external server intervention.""",
    "meta_ar": {
        "id": "SYS-17",
        "questionAr": "كيف تصمم منظومة مراقبة تشغيلية ومفاتيح إيقاف عن بعد (Kill Switches) للتعامل مع طوارئ الإنتاج؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على تصميم مفاتيح إيقاف عن بعد آمنة، وفصل القراءة المتزامنة عن جلب الشبكة، وحماية إقلاع التطبيق، وتنفيذ التحديث اللحظي عبر الإشعارات الصامتة وقواطع الدائرة.",
        "why_it_matters_ar": "اكتشاف خلل كارثي بعد إطلاق التحديث في متجر التطبيقات قد يستغرق أياماً لمراجعته ونشره، مما يعرض بيانات المستخدمين للخطر أو يوقف التطبيق عن العمل تماماً دون وجود مفتاح إيقاف فوري.",
        "worked_example_ar": "نموذج فحص مفتاح إيقاف الميزة دون تجميد واجهة المستخدم:\n```kotlin\nif (killSwitchManager.isFeatureEnabled(\"new_payment_gateway\", defaultFallback = false)) {\n    launchNewGateway()\n} else {\n    launchLegacyGateway()\n}\n```",
        "trade_offs_ar": "التحقق المباشر عبر الشبكة يضمن أحدث الإعدادات ولكنه يجمد الشاشات ويؤخر إقلاع التطبيق، بينما الاعتماد على الكاش المحلي يوفر سرعة فائقة لكنه قد يؤخر استلام أمر الإيقاف لبضع ساعات ما لم نستخدم FCM صامتاً.",
        "failure_modes_ar": "تجميد خيط الواجهة بانتظار استجابة السيرفر لجلب الإعدادات، أو الوقوع في فخ الديون التقنية لتراكم مئات الأعلام القديمة في الكود دون إزالتها بعد استقرار الميزات.",
        "production_perspective_ar": "في المشروعات المصرفية، نربط مفاتيح الإيقاف بلوحات قياس لحظية تراقب نسب الانهيار؛ فإذا تجاوزت نسبة الخطأ 0.5% لميزة جديدة، يطلق النظام أمراً آلياً بتعطيل الميزة فورياً دون انتظار تدخل بشري.",
        "how_to_answer_ar": "وضح تصميم المحرك مزدوج الطبقات: كاش محلي سريع مع مزامنة خلفية. بين قاعدة السلوك الدفاعي الآمن بالعودة للوضع المستقر عند فشل الاتصال. اشرح استخدام رسائل FCM الصامتة للإلغاء الفوري وقواطع الدائرة المحلية.",
        "talking_points_ar": "إدارة دورة حياة الـ Feature Flags، وإلغاء الكاش اللحظي عبر FCM Data-only، وحماية الإقلاع البارد، ومراقبة الانهيارات عبر الـ SLOs، والتخلص الدوري من الأعلام القديمة Flag Debt.",
        "follow_ups_ar": "- **المحاور:** \"ماذا تفعل إذا أدى تفعيل مفتاح ميزة إلى انهيار التطبيق في أول ثانية من فتحه قبل استقبال أي أمر من السيرفر؟\"\n  **المرشح:** \"نطبق قاطع دائرة محلي (Crash Loop Detection)؛ إذا رصد التطبيق تكرار الانهيار مرتين متتاليتين في بداية التشغيل، يتجاوز كاش الإعدادات محلياً ويعطل كل الأعلام التجريبية تلقائياً ليعود للوضع الأساسي المستقر.\"\n\n- **المحاور:** \"كيف تضمن ألا تتسبب قراءة مفاتيح الإيقاف في تأخير رسم الشاشة؟\"\n  **المرشح:** \"نقوم بتحميل جميع الأعلام في خريطة متزامنة داخل الذاكرة (ConcurrentHashMap) أثناء تهيئة التطبيق الأولى، فتتم القراءة بزمن O(1) ومتزامن تماماً دون أي استدعاء شبكي أو قراءة قرص بطيئة.\"",
        "self_check_ar": "هل وضحت كيفية قراءة الأعلام دون تأخير الإقلاع؟ هل بينت السلوك الافتراضي الآمن عند انقطاع الاتصال؟ وهل شرحت آلية الإلغاء الفوري السحابي والمحلي؟",
        "references_ar": f"- [Firebase Remote Config Architecture](https://firebase.google.com/docs/remote-config) — التوثيق الرسمي لإدارة وتوزيع الإعدادات عن بعد.\n- [Feature Toggles (Martin Fowler)](https://martinfowler.com/articles/feature-toggles.html) — المرجع القياسي لأنماط وإدارة دورة حياة مفاتيح الميزات.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "نصمم مفاتيح الإيقاف عن بعد عبر دمج التكوين السحابي مع كاش محلي فائق السرعة لضمان قراءة الإعدادات دون تأخير إقلاع التطبيق. نطبق سلوكا دفاعيا آمنا يعطل الميزات عند فشل الاتصال، ونبطل الميزات المعيبة فوريا عبر رسائل FCM صامتة مع مراقبة نسب الأعطال لتفعيل قواطع الدائرة آليا.",
        "best_answer_ar": "تعد مفاتيح الإيقاف عن بعد صمام الأمان الأساسي لحماية التطبيقات من الأخطاء البرمجية الكارثية دون الحاجة لإطلاق تحديثات طارئة عبر المتجر. نعتمد على محرك تهيئة مزدوج يحفظ القيم في الذاكرة ومساحة التخزين السريع لتوفير فحص فوري متزامن على مسار الواجهة دون تأخير الإقلاع. لا ننتظر تحميل الإعدادات من السيرفر أثناء فتح التطبيق، بل نبدأ بالقيم المخزنة محليا ونحدث البيانات في الخلفية بهدوء. نلزم كل ميزة بسلوك دفاعي افتراضي محافظ، بحيث تعود الميزة للإلغاء التلقائي في حال انقطاع الشبكة أو حدوث تلف في البيانات المستلمة. في حالات الطوارئ القصوى، نرسل إشعارات دفع صامتة عالية الأولوية عبر FCM تأمر التطبيقات النشطة بإلغاء تفعيل الميزة فورا في الذاكرة والقرص خلال دقائق معدودة. كما نربط الميزات بمقاييس الأعطال اللحظية لتمكين أنظمة السيرفر من فصل الميزة آليا عند تجاوز معدل الأخطاء للحدود المسموحة.",
        "deep_answer_ar": "على المستوى الهندسي المتقدم، تمثل مفاتيح الإيقاف الخط الدفاعي الأخير ضد تسرب البيانات وانهيار الأنظمة في الإنتاج. يكمن الخطر الأكبر في تراكم مفاتيح الإعدادات القديمة غير المستخدمة، مما يولد تعقيدا هائلا في الاختبارات وتشابكا غير متوقع، ولذلك نفرض تاريخ انتهاء صلاحية إلزامي لكل مفتاح ومسؤولية واضحة لفريق العمل لإزالته برمجيا بعد استقرار الميزة. نحرص على أن تكون قراءة الإعدادات متزامنة ومن الذاكرة تماما، لأن الاستعلام عبر الشبكة أثناء عرض الشاشات يسبب وميضا مزعجا أو ظهور عناصر تجريبية بشكل مفاجئ أثناء تفاعل المستخدم. لمواجهة الثغرات الأمنية الحرجة، لا نكتفي بالمزامنة الدورية البطيئة، بل ندمج الإشعارات الصامتة مع ترويسات الاستجابة السريعة في طلبات الـ API العادية لتحديث القيم فوريا. كما نبرمج قاطع دائرة محلي ذكي داخل التطبيق يرصد تكرار انهيار الشاشة فور تفعيل ميزة معينة، فيقوم التطبيق بإلغاء تفعيلها محليا من تلقاء نفسه لكسر حلقة الانهيارات المستمرة وحماية تجربة المستخدم دون انتظار وصول أمر من السيرفر. كما نضع آلية استباقية لفحص التوافقية العكسية مع الإصدارات السابقة من إعدادات الـ Remote Config، ونستخدم أدوات المراقبة اللحظية مثل Datadog أو Firebase Crashlytics لرصد أي زيادة غير طبيعية في معدل الخطأ بنسبة تتجاوز نصف بالمائة، مما يؤدي تلقائيا إلى إرسال إشعار فوري لفرق العمليات لإطلاق أمر الإيقاف المركزي عبر السيرفر."
    }
}

# ==========================================
# SYS-18: How do you support version skew between older apps and newer backend contracts?
# ==========================================
DATA["SYS-18"] = {
    "concept_en": """Supporting version skew between legacy installed Android applications and evolving backend contracts is a fundamental requirement of mobile systems architecture. Unlike web browsers where users instantly execute the newest published assets upon refreshing a webpage, mobile clients exist across hundreds of disparate binary versions simultaneously. Some users disable automatic Play Store updates, running client versions that are months or years old. Backend APIs must adhere to additive change policies, strictly forbidding the removal or renaming of response fields, changing JSON property types, or converting optional parameters into required attributes. Mobile JSON serializers like Moshi or Kotlinx Serialization must be configured defensively to ignore unknown keys and provide safe default values for missing fields. When breaking backend redesigns become mandatory, teams introduce versioned URL namespaces, transmit client version headers on every request, and utilize non-dismissible force-update mechanisms to sunset unsupported legacy clients safely.""",
    "walkthrough_en": """Implementing resilient client-side version headers and defensive deserialization:
```kotlin
// 1. OkHttp interceptor transmitting client version telemetry on every outbound request
class ClientVersionInterceptor @Inject constructor(
    @ApplicationContext private val context: Context
) : Interceptor {
    private val packageInfo = context.packageManager.getPackageInfo(context.packageName, 0)
    private val appVersionCode = PackageInfoCompat.getLongVersionCode(packageInfo)
    private val appVersionName = packageInfo.versionName

    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request().newBuilder()
            .header("X-App-Version-Code", appVersionCode.toString())
            .header("X-App-Version-Name", appVersionName)
            .header("X-Client-Platform", "android")
            .build()

        val response = chain.proceed(request)

        // Handle HTTP 426 Upgrade Required for retired application binaries
        if (response.code == 426) {
            EventBus.publish(ForceUpdateRequiredEvent)
        }
        return response
    }
}

// 2. Defensive Kotlinx Serialization entity handling missing or newly added backend fields
@Serializable
data class AccountProfileDto(
    @SerialName("user_id") val userId: String,
    @SerialName("display_name") val displayName: String,
    // Additive field with default fallback protecting older clients from null pointer crashes
    @SerialName("membership_tier") val membershipTier: String = "STANDARD",
    // New complex nested object safely modeled as nullable
    @SerialName("loyalty_rewards") val loyaltyRewards: LoyaltyRewardsDto? = null
)
```""",
    "short_en": """We handle mobile version skew by enforcing additive backend contract policies and configuring client JSON serializers to ignore unknown fields with safe default fallbacks. We transmit version headers on every HTTP call and implement non-dismissible force-update dialogs for retired binary versions.""",
    "structured_en": """Supporting version skew is vital because mobile users operate across hundreds of legacy app releases that cannot be updated simultaneously.
I enforce an additive contract evolution rule on backend APIs. Server teams must never rename or delete active JSON fields, change data types, or introduce mandatory request parameters without creating a new API version.
On the Android client, we configure JSON serializers like Kotlinx Serialization or Moshi to ignore unrecognized keys and assign safe defaults for new optional fields.
Every outbound HTTP request includes custom headers carrying the app version code, version name, and platform identifier. This allows backend routing layers to track active client distributions and apply version-specific adapters.
When legacy contracts must be deprecated, the backend returns an HTTP 426 Upgrade Required status or a structured force-update envelope.
The mobile app catches this response, halts critical workflows, and displays a non-dismissible dialog directing the user to update the app on the Google Play Store.""",
    "deep_senior_en": """From a staff engineering perspective, managing mobile version skew requires robust coordination between backend release cadences, database schemas, and client sunset policies.
A frequent source of production bugs is enum deserialization crashes. When a backend team adds a new enum value to an existing endpoint, older mobile clients crash with serialization exceptions if the serializer attempts to parse an unknown string. We prevent this by avoiding raw enums in network DTOs, opting instead for sealed classes with an unknown fallback or configuring serializers with custom default enum annotators.
When a breaking backend architectural change is unavoidable, we utilize the dual-write and parallel-run pattern. The backend supports both legacy and modern contract schemas simultaneously for an established migration window, such as six months, tracking traffic volume by client version header until legacy adoption falls below an acceptable threshold like zero point five percent.
Furthermore, local database schemas must maintain backward compatibility with cloud contracts. If a database entity expects a non-null string that a legacy app version cached, but a newer backend payload sends null, the repository mapping layer must defensively sanitize the entity before persisting it to SQLite, avoiding database constraint failures.
Finally, we build flexible remote update prompts. Soft updates display a dismissible banner encouraging users to install performance improvements, whereas hard updates block the UI entirely when cryptographic protocols or security tokens become obsolete, ensuring unsupported binaries cannot compromise user accounts.""",
    "meta_ar": {
        "id": "SYS-18",
        "questionAr": "كيف تدير تفاوت الإصدارات (Version Skew) بين التطبيقات المثبتة والـ Backend الحديث؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على دعم توافقية الإصدارات المتباينة في الموبايل، وتصميم تعاقدات الـ APIs التراكمية، وضبط أدوات التحويل ضد الحقول غير المتوقعة، وتنفيذ التحديث الإجباري.",
        "why_it_matters_ar": "تطبيقات الموبايل لا يمكن تحديثها قسراً لدى جميع المستخدمين في لحظة واحدة؛ وأي تعديل غير متوافق في السيرفر سيؤدي لتعطل التطبيق لدى ملايين المستخدمين الذين يمتلكون إصدارات سابقة.",
        "worked_example_ar": "ضبط Kotlinx Serialization لتجاهل الحقول الجديدة غير المعروفة:\n```kotlin\nval json = Json {\n    ignoreUnknownKeys = true // منع الانهيار عند إضافة حقول جديدة في السيرفر\n    coerceInputValues = true // استخدام القيمة الافتراضية إذا أرسل السيرفر null لحقل أساسي\n}\n```",
        "trade_offs_ar": "إبقاء دعم المسارات القديمة في السيرفر يزيد من تعقيد وصيانة البنية التحتية، بينما التحديث الإجباري السريع يريح المطورين ولكنه قد يغضب المستخدمين الذين لا يملكون مساحة أو إنترنت سريعاً.",
        "failure_modes_ar": "استخدام Enums مباشرة في كائنات الشبكة؛ فعندما يضيف السيرفر قيمة جديدة تنهار التطبيقات القديمة فوراً أثناء محاولة فك التشفير، أو حذف حقل قديم اعتقد فريق السيرفر أنه غير مستخدم.",
        "production_perspective_ar": "في المشروعات الضخمة، نرسل رقم إصدار التطبيق ونوعه في كل طلب، ونراقب عبر لوحات التحليلات نسبة المستخدمين على كل إصدار؛ ولا نلغي أي مسار قديم إلا بعد هبوط نسبته لأقل من 0.2%.",
        "how_to_answer_ar": "اشرح مبدأ التعاقدات التراكمية (Additive Contracts). وضح الضبط الدفاعي لمحولات الـ JSON بتجاهل الحقول الغريبة ووضع قيم افتراضية. اشرح ترويسات الإصدارات وآلية التحديث الإجباري برمز 426.",
        "talking_points_ar": "خطر الـ Enums في الشبكة، وضبط ignoreUnknownKeys، ونمط Dual-Write في السيرفر، وتحديثات متجر Play المرنة والإجبارية، ومطابقة قواعد البيانات المحلية مع السحابية.",
        "follow_ups_ar": "- **المحاور:** \"كيف تتعامل مع إضافة حقل جديد بنوع Enum في السيرفر دون التسبب في انهيار التطبيقات القديمة؟\"\n  **المرشح:** \"نتجنب الـ Enums المباشرة ونستبدلها بـ Sealed Class يحتوي على حالة افتراضية Unknown(val raw: String)، أو نضبط محول الـ JSON ليعود للحالة الافتراضية عند استقبال قيمة مجهولة بدلاً من إلقاء استثناء.\"\n\n- **المحاور:** \"ما الفرق بين التحديث المرن (Soft Update) والتحديث الإجباري (Hard/Force Update)؟\"\n  **المرشح:** \"التحديث المرن يظهر إشعاراً أو شريطاً ينبه المستخدم بوجود تحسينات دون منعه من الاستخدام، بينما الإجباري يظهر شاشة مغلقة تحظر استخدام التطبيق تماماً حتى الترقية بسبب توقف البروتوكول القديم نهائياً.\"",
        "self_check_ar": "هل وضحت لماذا تختلف مشكلة تفاوت الإصدارات في الموبايل عن الويب؟ هل بينت خطورة الـ Enums؟ وهل شرحت سياسة التعديلات التراكمية في السيرفر؟",
        "references_ar": f"- [Google Play In-App Updates](https://developer.android.com/guide/playcore/in-app-updates) — التوثيق الرسمي لآليات التحديث الداخلي في أندرويد.\n- [Evolving HTTP APIs](https://martinfowler.com/articles/enterpriseREST.html) — مقال مارتن فاولر حول تطوير الـ APIs دون كسر التوافقية.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "ندير تفاوت الإصدارات عبر إلزام الخوادم بتعاقدات تراكمية لا تحذف الحقول السابقة، وضبط أدوات تحويل JSON لتجاهل الحقول الجديدة ووضع قيم افتراضية آمنة. نرسل رقم إصدار التطبيق في كل طلب، ونفعل التحديث الإجباري عبر حوار غير قابل للإلغاء عند إيقاف الإصدارات القديمة نهائيا.",
        "best_answer_ar": "يمثل تفاوت الإصدارات تحديا محوريا في هندسة الموبايل نظرا لأن ملايين المستخدمين يظلون على نسخ قديمة لا يتم تحديثها في وقت واحد. نلزم فرق الـ Backend بسياسة التطوير التراكمي الصارمة، بحيث يحظر حذف أو إعادة تسمية الحقول الحالية أو تغيير أنواعها، ويقتصر التعديل على إضافة حقول اختيارية جديدة. نضبط أدوات تحويل البيانات مثل Moshi و Kotlinx Serialization لتجاهل أي حقول غير معروفة تلقائيا وتعيين قيم افتراضية آمنة للحقول المستحدثة لتجنب انهيار التطبيق. نرفق ترويسات مخصصة في كل طلب شبكة توضح رقم إصدار التطبيق ونظامه، مما يسمح للخادم بتتبع توزيع الإصدارات وتطبيق مهايئات خاصة عند الحاجة. وعندما تنتهي فترة دعم إصدار قديم جدا، يعيد السيرفر رمز 426 Upgrade Required، ليعرض التطبيق واجهة تحديث إجبارية تمنع متابعة الاستخدام وتوجه العميل مباشرة لمتجر Google Play.",
        "deep_answer_ar": "على المستوى الهندسي المتقدم، يتطلب تفاوت الإصدارات تنسيقا عميقا بين قواعد البيانات وسياسات إيقاف الخدمات القديمة. يعد الانهيار بسبب الـ Enums غير المعروفة من أشهر أخطاء الإنتاج، فعندما يضيف الخادم قيمة جديدة لقائمة معرفة مسبقا، تنهار التطبيقات القديمة أثناء التحويل؛ ولذلك نلغي استخدام الـ Enums المباشرة في كائنات الشبكة ونستبدلها بفئات مغلقة تدعم حالة غير معروف تلقائيا. عند الاضطرار لتغيير هيكلي جذري، نطبق نمط الكتابة المزدوجة ودعم المسارين معا في السيرفر لفترة انتقالية محددة كستة أشهر، مع مراقبة انخفاض حركة المرور من الإصدارات القديمة حتى تصل إلى نسبة ضئيلة جدا قبل إيقافها. نضمن أيضا توافق قواعد بيانات Room المحلية بحيث تتقبل النماذج الحقول الفارغة وتطهر البيانات قبل الحفظ لتجنب انتهاك قيود الجداول. كما نصمم نظام تحديث مرن يشمل تحديثات اختيارية ناعمة تحث المستخدم على الترقية بهدوء، وتحديثات إجبارية صارمة تحظر الاستخدام تماما في حال تعطل البروتوكولات الأمنية القديمة أو تغير شهادات التشفير. كما نوفر في طبقة الشبكة وسيطا ذكيا يعالج أخطاء عدم تطابق الحقول ويحولها إلى سجلات تحليلية توضح نسبة الأجهزة التي تستخدم إصدارات غير متوافقة، ونحرص على ألا يؤدي وجود حقل نصي بدلا من رقمي في البيانات القديمة إلى انهيار محرك التحويل البرمجي، مع توفير واجهات معالجة أخطاء مرنة تعرض للمستخدم رسائل تنبيه واضحة في حال عدم توفر الميزة في إصداره الحالي."
    }
}

# ==========================================
# SYS-19: Your app has 20 feature teams and takes 25 minutes to build. How do you redesign team ownership and dependencies?
# ==========================================
DATA["SYS-19"] = {
    "concept_en": """Scaling an enterprise Android application across twenty autonomous feature teams with a twenty-five-minute build time requires an aggressive restructuring of the dependency graph, build infrastructure, and architectural governance. In large organizations, build bottlenecks stem from monolithic module topologies, circular and deep linear dependency chains, excessive annotation processor passes (KAPT), non-cacheable Gradle tasks, and bloated root application packaging. Redesigning this architecture begins with empirical profiling using Gradle Build Scans to identify critical-path task execution times. Teams must adopt a modularized structure separating each feature into an api contract module, an impl private implementation module, and an independent sample harness app. Sample apps enable developers to compile and test their feature in isolation within seconds without building the entire application. In addition, migrating to Kotlin Symbol Processing (KSP), enabling remote build caching, and enforcing strict module boundaries via Gradle convention plugins restores rapid feedback loops.""",
    "walkthrough_en": """Structuring isolated feature modules and standalone sample apps for lightning-fast builds:
```text
// 1. Decoupled module hierarchy with isolated sample applications
├── build-logic/ (Convention plugins managing Gradle configurations centrally)
├── core/
│    ├── network/
│    └── database/
├── features/
│    ├── checkout/
│    │    ├── api/    (Exposes pure interfaces and models; compiles in 2 seconds)
│    │    ├── impl/   (Internal business logic, depends on checkout:api and core libraries)
│    │    └── sample/ (Standalone mini-app running Checkout flow in isolation in 8 seconds!)
│    ├── search/
│    │    ├── api/
│    │    ├── impl/
│    │    └── sample/
└── app/ (Final release composition wiring all 20 feature teams together)
```
```kotlin
// 2. Gradle convention plugin enforcing shared compiler and cache settings
class AndroidFeatureConventionPlugin : Plugin<Project> {
    override fun apply(target: Project) {
        with(target) {
            pluginManager.apply("com.android.library")
            pluginManager.apply("org.jetbrains.kotlin.android")
            pluginManager.apply("com.google.devtools.ksp") // Replace slow KAPT across all squads
            // Enforce unified JVM target, strict compilation flags, and build cacheability
        }
    }
}
```""",
    "short_en": """We fix twenty-five-minute build bottlenecks by profiling Gradle tasks, migrating from KAPT to KSP, and restructuring code into decoupled api and impl modules. We provide standalone sample apps so squads build their features in seconds, while leveraging remote build caching and convention plugins for governance.""",
    "structured_en": """Resolving a twenty-five-minute build bottleneck across twenty squads requires restructuring both the dependency architecture and build pipelines.
I begin with data-driven profiling using Gradle Build Scans and Gradle Profiler to uncover task bottlenecks, non-cacheable steps, and critical compilation paths.
We reorganize the codebase into decoupled modules, splitting every feature into a lightweight api contract module and a private impl module.
Consuming squads depend strictly on api contracts, preventing downstream recompilation when private feature code changes.
We eliminate legacy KAPT annotation processing entirely, migrating to Kotlin Symbol Processing (KSP) to accelerate code generation by up to four hundred percent.
To give engineers immediate productivity, we author isolated sample testbed apps for every feature. Developers spend their day compiling only their feature sample app in under ten seconds rather than assembling the entire twenty-feature application.
Finally, we enable remote build caching in CI, allowing developers to pull precompiled module artifacts directly from cache.""",
    "deep_senior_en": """From a staff developer productivity infrastructure perspective, scaling twenty teams requires treating build performance as a core product feature with dedicated SLOs and governance.
The most impactful technical shift is enabling remote build caching. When an engineer pulls the latest main branch, their local machine should not recompile nineteen untouched feature modules. By hosting a centralized remote build cache with strict input normalization, ninety percent of Gradle tasks resolve as FROM-CACHE, cutting incremental clean builds from twenty-five minutes down to under two minutes.
To prevent the dependency graph from regressing into an entangled monolith, we enforce strict dependency rules using Gradle convention plugins defined in build-logic. Feature modules are forbidden from depending on lateral feature implementation modules; they can only reference external api modules. We enforce these constraints automatically using Gradle dependency analysis plugins and ArchUnit tests in CI.
Furthermore, we optimize our continuous integration pipelines using predictive test selection and dynamic matrix builds. Rather than executing the entire sixty-minute test suite on every commit, CI inspects the git diff, determines affected modules through dependency graph traversal, and triggers tests only for the impacted subsystem and its immediate dependents.
Finally, code ownership is codified via CODEOWNERS files mapped to squad boundaries. Teams have autonomous merge rights within their impl modules, while modifications to core infrastructure and shared api contracts require formal architectural review, preventing uncontrolled dependency bloat.""",
    "meta_ar": {
        "id": "SYS-19",
        "questionAr": "تطبيقك يعمل عليه 20 فريقاً وبناؤه يستغرق 25 دقيقة، كيف تعيد هيكلة التبعيات وسرعة البناء؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على قيادة هندسة إنتاجية المطورين، وتشخيص اختناقات Gradle، وتفكيك التبعيات المتشابكة، وإدخال أدوات KSP والكاش السحابي وتطبيقات العينات المستقلة.",
        "why_it_matters_ar": "استغراق البناء 25 دقيقة يهدر آلاف الساعات سنوياً لعشرين فريقاً ويسبب إحباطاً هائلاً للمطورين، ويؤخر تسليم التحديثات ويكلف الشركة ملايين الدولارات في خوادم البناء المستمر.",
        "worked_example_ar": "تفعيل كاش البناء وضبط إعدادات Gradle في gradle.properties:\n```properties\norg.gradle.caching=true\norg.gradle.parallel=true\norg.gradle.vfs.watch=true\norg.gradle.jvmargs=-Xmx6g -XX:+UseParallelGC\n```",
        "trade_offs_ar": "إعادة هيكلة شجرة التبعيات تتطلب جهداً هندسياً كبيراً وتدريب الفرق، ولكنها الاستثمار الوحيد الذي يخفض زمن البناء من نصف ساعة إلى دقيقتين ويضمن قابلية التوسع المستقبلي.",
        "failure_modes_ar": "الاعتماد على KAPT القديم الذي يعطل كاش البناء، أو تشابك الموديولات في سلاسل اعتماد دائرية، أو عدم عزل مدخلات المهام مما يؤدي لتعطيل كاش Gradle دائماً (Cache Miss).",
        "production_perspective_ar": "في كبرى الشركات التقنية، نخصص فريقاً متخصصاً لإنتاجية المطورين Developer Productivity يراقب أزمنة البناء أسبوعياً، ويمنع أي ميزة من الدمج إذا تسببت في زيادة زمن البناء التزايدي.",
        "how_to_answer_ar": "ابدأ بالتشخيص المعتمد على البيانات عبر Gradle Build Scan. وضح التحول من KAPT إلى KSP. اشرح فصل الميزات لـ api و impl و sample apps. واختم بالكاش السحابي المشترك وسياسات ملكية الكود بـ CODEOWNERS.",
        "talking_points_ar": "أداة Gradle Profiler و Build Scan، والترقية إلى KSP، ونمط Sample Apps السريع، والـ Remote Build Cache، والتحكم بالبناء عبر Convention Plugins في build-logic.",
        "follow_ups_ar": "- **المحاور:** \"كيف تسمح تطبيقات العينات (Sample Apps) للمطور باختبار ميزته في 10 ثوانٍ؟\"\n  **المرشح:** \"تطبيق العينة هو موديول Application صغير جداً يعتمد فقط على موديول الميزة وموديولات النواة الأساسية، فلا يحتاج Gradle لتجميع الـ 19 ميزة الأخرى ولا لحقن آلاف الفئات في حزمة واحدة.\"\n\n- **المحاور:** \"لماذا يعتبر استبدال KAPT بـ KSP عاملاً حاسماً في سرعة البناء؟\"\n  **المرشح:** \"لأن KAPT يولد ملفات كود وسيطة بلغة جافا (Java Stubs) لكل ملف كوتلن ثم يستدعي مترجم جافا، بينما KSP يتعامل مع شجرة الكود المجردة للغة كوتلن مباشرة في الذاكرة مما يسرع التوليد بمرتين إلى أربع مرات.\"",
        "self_check_ar": "هل حددت خطوات التشخيص بالأرقام؟ هل فرقت بين موديولات الـ API والـ Sample Apps؟ وهل شرحت أثر الكاش السحابي على خفض أزمنة البناء؟",
        "references_ar": f"- [Optimizing Gradle Build Speed](https://developer.android.com/studio/build/optimize-your-build) — دليل جوجل الرسمي لتحسين سرعة بناء مشاريع أندرويد.\n- [Kotlin Symbol Processing (KSP)](https://kotlinlang.org/docs/ksp-overview.html) — توثيق تقنية KSP الرسمية لتسريع توليد الأكواد.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "نعالج بطء البناء عبر تحليل مهام Gradle، واستبدال KAPT بـ KSP، وتقسيم الميزات إلى موديولات api و impl معزولة. نوفر تطبيقات عينات مصغرة لكل فريق لبناء ميزته في ثوان معدودة، ونفعل كاش البناء السحابي وإضافات Gradle المركزية لضبط الحوكمة.",
        "best_answer_ar": "يتطلب حل أزمة بطء البناء لعشرين فريق عمل تدخلا معماريا يعيد هندسة شجرة التبعيات والبنية التحتية للبناء بشكل جذري. نبدأ بتحليل أداء المهام عبر Gradle Build Scans لتحديد المهام التي تعطل التجميع وتفشل في استغلال الكاش. نقسم كل ميزة إلى موديول تعاقدات api خفيف وسريع وموديول تنفيذ impl خاص، بحيث تعتمد الفرق الأخرى على التعاقدات فقط لتجنب إعادة تجميع ميزاتها عند تعديل الكود الداخلي. نستبدل معالجات الأكواد القديمة KAPT بتقنية KSP الحديثة لتسريع توليد الأكواد بنسبة تصل إلى أربعة أضعاف. والأهم من ذلك، ننشئ تطبيقا تجريبيا مصغرا لكل ميزة يسمح للمهندس ببناء وتشغيل شاشاته في ثوان معدودة دون الحاجة لتجميع التطبيق الكامل الضخم. كما نطبق كاش البناء السحابي في خوادم الـ CI ليتمكن المطورون من تنزيل مخرجات الموديولات الجاهزة فورا دون إعادة بنائها محليا.",
        "deep_answer_ar": "على مستوى هندسة إنتاجية المطورين المتقدمة، يجب التعامل مع سرعة البناء كمنتج أساسي له مقاييس جودة واضحة. يمثل كاش البناء السحابي المركزى التحول الأكبر، فعندما يسحب المطور أحدث كود، لا يجب أن يعيد جهازه بناء موديولات الفرق الأخرى، بل يسحب المخرجات الجاهزة من السيرفر لتنخفض مدة البناء من 25 دقيقة إلى أقل من دقيقتين. لحماية شجرة التبعيات من التشابك، نستخدم إضافات Gradle الموحدة في build-logic لحظر الربط المباشر بين موديولات التنفيذ، بحيث لا تتواصل الفرق إلا عبر واجهات الـ api العامة، ونفحص ذلك آليا عبر ArchUnit في الـ CI. نطور أيضا خوادم البناء المستمر بتطبيق الفحص الانتقائي للاختبارات، فلا نشغل الاختبارات الشاملة للتطبيق كاملا في كل طلب دمج، بل نحدد الموديولات المتأثرة بالتعديل فقط ونختبرها بالتوازي. وأخيرا، ننظم ملكية الكود عبر ملفات CODEOWNERS لتمكين كل فريق من الدمج المستقل داخل موديوله الخاص، بينما تتطلب التعديلات على النواة العامة مراجعة معمارية معتمدة لمنع تكرار تضخم التبعيات. كما نطبق أدوات التحليل الآلي للتبعيات مثل Gradle Dependency Analysis Plugin للكشف عن الموديولات غير المستخدمة أو التبعيات الزائدة وإزالتها فورا من ملفات البناء، مع تخصيص أجهزة بناء عالية الأداء في بيئة التطوير السحابي تضمن تسليم الحزم النهائية واختبارات القبول الشاملة في دقائق معدودة بدلا من الانتظار الطويل."
    }
}

# ==========================================
# SYS-20: A payment was authorized but the UI timed out. Design recovery and reconciliation.
# ==========================================
DATA["SYS-20"] = {
    "concept_en": """Handling ambiguous financial transactions where a payment authorization succeeds on the backend but the mobile user interface encounters a network timeout is one of the most critical challenges in mobile architecture. In distributed systems, a network timeout represents an unknown state, not a transaction failure. The payment packet may have been captured and processed by the payment gateway, but the confirmation response was dropped due to cellular tower switching. If the mobile app naively reports a failure and allows the user to re-tap the pay button, double-charging occurs. To prevent financial discrepancies, the transaction must be persisted locally in Room as PENDING alongside a client-generated UUID idempotency key before the network call is dispatched. Upon timeout recovery or screen re-entry, the application executes a reconciliation query using the existing idempotency key. The backend inspects its immutable ledger and returns the authoritative status, allowing the client to transition cleanly to success or failure.""",
    "walkthrough_en": """Implementing robust payment reconciliation using client idempotency keys and ledger verification:
```kotlin
// 1. Immutable local transaction record persisted before network transmission
@Entity(tableName = "payment_transactions")
data class PaymentRecordEntity(
    @PrimaryKey val orderId: String,
    val idempotencyKey: String = UUID.randomUUID().toString(),
    val amountCents: Long,
    val currency: String,
    val status: PaymentStatus = PaymentStatus.PENDING,
    val createdAtMs: Long = System.currentTimeMillis()
) {
    enum class PaymentStatus { PENDING, AUTHORIZED, FAILED }
}

// 2. Reconciliation coordinator resolving ambiguous transaction outcomes
class PaymentReconciliationCoordinator @Inject constructor(
    private val paymentDao: PaymentRecordDao,
    private val paymentApi: PaymentApiService
) {
    suspend fun resolveAmbiguousPayment(orderId: String): PaymentUiOutcome {
        val record = paymentDao.getByOrderId(orderId)
            ?: return PaymentUiOutcome.Failure("Transaction not found")

        return try {
            // Reconcile status against backend ledger using original idempotency key
            val statusResponse = paymentApi.getPaymentStatusByIdempotency(record.idempotencyKey)
            when (statusResponse.state) {
                "AUTHORIZED", "CAPTURED" -> {
                    paymentDao.updateStatus(orderId, PaymentRecordEntity.PaymentStatus.AUTHORIZED)
                    PaymentUiOutcome.Success(statusResponse.receiptId)
                }
                "FAILED", "REJECTED" -> {
                    paymentDao.updateStatus(orderId, PaymentRecordEntity.PaymentStatus.FAILED)
                    PaymentUiOutcome.Failure(statusResponse.failureReason ?: "Payment rejected")
                }
                else -> {
                    // Still processing on gateway; keep UI in pending reconciliation state
                    PaymentUiOutcome.StillPending
                }
            }
        } catch (e: Exception) {
            // Network remains unavailable; persist pending state for background WorkManager recovery
            PaymentUiOutcome.StillPending
        }
    }
}
```""",
    "short_en": """When a payment times out, we mark the transaction as pending in local persistence using a client-generated idempotency key rather than claiming failure. We run a reconciliation query using that key to fetch the authoritative ledger status, preventing double charges and updating the UI accordingly.""",
    "structured_en": """Handling a payment timeout requires treating network interruption as an ambiguous state rather than an immediate transaction failure.
Before dispatching any payment request, the client generates a unique UUID idempotency key and writes the transaction to a local Room database with a pending status.
If the network call times out or the connection drops mid-flight, the UI must never display a generic payment failed screen with an active retry button, as doing so leads directly to double charges.
Instead, the UI transitions to an order verification state while a reconciliation query polls the backend using the original idempotency key.
The backend queries its transaction ledger; if the payment was already captured, it returns the confirmed receipt, allowing the client to mark the local record as authorized and display success.
If the user closes the app during the timeout, a background WorkManager task resumes the reconciliation process automatically upon reconnecting.""",
    "deep_senior_en": """From a staff financial systems perspective, client-side payment recovery requires absolute adherence to transaction idempotency and resilient distributed state machines.
The fundamental rule of payment UX is never allowing a user to re-execute a transaction without proving the fate of the previous attempt. If the UI displays an ambiguous pending state, we present clear messaging indicating that the payment is being confirmed with the financial institution and that the user's card will not be charged twice.
If the device loses connectivity entirely or the app process is killed by the Android system, recovery cannot rely on in-memory coroutines. We schedule an expedited WorkManager job backed by the local database. When network connectivity restores, WorkManager reads pending transactions, issues the reconciliation query against the backend status endpoint, and fires a high-priority local notification confirming the purchase or prompting safe recovery.
Backend payment services must be designed around strict ledger immutability. The idempotency key must be checked inside a distributed Redis lock or database unique constraint. If two identical requests hit the backend simultaneously due to aggressive client retries, the server processes the first and makes the second await the initial transaction outcome.
Finally, we implement telemetry on transaction resolution times. If the percentage of payments requiring reconciliation spikes, our monitoring triggers an alert to investigate cellular carrier issues or payment gateway webhook degradation.""",
    "meta_ar": {
        "id": "SYS-20",
        "questionAr": "تمت الموافقة على الدفع وانتهت مهلة الواجهة (UI Timeout)، كيف تصمم آلية التسوية والاستعادة؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على تصميم معماريات المعاملات المالية الآمنة، والتعامل مع حالات الشبكة الغامضة، ومنع السحب المزدوج عبر مفاتيح عدم التكرار، وتنفيذ التسوية الخلفية.",
        "why_it_matters_ar": "اعتبار انتهاء المهلة بمثابة فشل للمعاملة وإتاحة زر إعادة المحاولة يسبب خصم المبلغ من بطاقة المستخدم مرتين، مما يؤدي لمشاكل قانونية ومالية جسيمة وفقدان ثقة العملاء.",
        "worked_example_ar": "استعلام تسوية حالة الدفع عبر مفتاح عدم التكرار:\n```kotlin\nval status = paymentApi.checkStatus(idempotencyKey)\nif (status.isCaptured) {\n    showSuccessScreen(status.receiptNumber)\n} else {\n    showPendingScreen()\n}\n```",
        "trade_offs_ar": "حظر زر إعادة المحاولة فوراً قد يثير قلق المستخدم في البداية، ولكنه الخيار الهندسي الوحيد الذي يضمن منع الخصم المزدوج ويحمي أموال العميل حتى البت النهائي في حالة العملية.",
        "failure_modes_ar": "توليد مفتاح عدم تكرار جديد عند كل محاولة إعادة إرسال مما يلغي فائدته بالكامل، أو الاعتماد على كائنات الذاكرة التي تفقد إذا قتل النظام التطبيق في الخلفية أثناء انتظار الرد.",
        "production_perspective_ar": "في تطبيقات التكنولوجيا المالية، نستخدم WorkManager المجدول بمهام Expedited Worker لقراءة المعاملات المعلقة فور عودة الإنترنت وإشعار المستخدم بنتيجة الدفع عبر إشعار نظام محلي.",
        "how_to_answer_ar": "أكد أولاً أن انتهاء مهلة الشبكة يمثل حالة غامضة Unknown وليس فشلاً. اشرح توليد وحفظ مفتاح الـ Idempotency في Room قبل الإرسال. وضح استعلام التسوية الفوري والتسوية الخلفية بـ WorkManager.",
        "talking_points_ar": "مفهوم Two Generals Problem في الشبكات، ومفاتيح عدم التكرار، واستعلامات التسوية Reconciliation، وجدولة مهام WorkManager، والرسائل الشفافة في الـ UX المالي.",
        "follow_ups_ar": "- **المحاور:** \"ماذا تفعل إذا قام المستخدم بإغلاق التطبيق تماماً فور حدوث مهلة الانتظار؟\"\n  **المرشح:** \"المعاملة محفوظة في Room بحالة Pending، ولدينا مهمة WorkManager مسجلة مسبقاً تعمل فور توفر الشبكة لتستعلم عن مصير المفتاح وتحدث قاعدة البيانات وترسل تنبيهاً للمستخدم.\"\n\n- **المحاور:** \"كيف يضمن السيرفر عدم تنفيذ عمليتي خصم إذا وصله نفس المفتاح في نفس الجزء من الثانية؟\"\n  **المرشح:** \"يستخدم السيرفر قفلاً موزعاً مثل Redis Lock أو قيد فريد في قاعدة البيانات يرفض الطلب الثاني ويجعله ينتظر نتيجة معالجة الطلب الأول الجاري تنفيذها.\"",
        "self_check_ar": "هل بينت لماذا لا يعد انتهاء المهلة فشلاً نهائياً؟ هل وضحت حفظ المفتاح محلياً قبل الإرسال؟ وهل شرحت آلية الاستعادة بعد موت التطبيق؟",
        "references_ar": f"- [Designing Data-Intensive Applications (Kleppmann)](https://dataintensive.net/) — المرجع الشامل للتسوية في الأنظمة الموزعة.\n- [Stripe: Designing robust payment systems](https://stripe.com/blog/idempotency) — دليل سترايب لمعالجة المهل الزمنية وضمان عدم التكرار.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "عند انتهاء مهلة الدفع، نحفظ المعاملة محليا كمعاملة معلقة بمفتاح عدم تكرار فريد بدلا من إعلان فشلها. نجري استعلام تسوية فوري عبر المفتاح لمعرفة حالة المعاملة الحقيقية من السيرفر، مما يمنع السحب المزدوج ويحدث الواجهة بالنتيجة النهائية بدقة.",
        "best_answer_ar": "تتطلب معالجة انتهاء مهلة الدفع الحذر الشديد والتعامل مع انقطاع الاتصال كحالة غير محسومة وليست فشلا نهائيا لمنع سحب الأموال مرتين من حساب العميل. قبل إرسال طلب الدفع عبر الشبكة، يولد التطبيق مفتاح عدم تكرار فريد ويحفظ المعاملة في قاعدة بيانات Room المحلية بحالة معلقة. إذا انقطعت الشبكة أو انتهت المهلة الزمنية، لا نظهر رسالة فشل مضللة مع زر إعادة المحاولة، لأن ذلك يدفع المستخدم للضغط مجددا وسحب المبلغ مرتين. بدلا من ذلك، ننتقل بالواجهة إلى حالة التحقق من المعاملة ونجري استعلام تسوية فوري للخادم باستخدام نفس مفتاح عدم التكرار. يتحقق الخادم من سجله المالي الدائم؛ فإذا تمت المعالجة يعيد إيصال الدفع المؤكد ليحدث التطبيق حالته المحلية إلى مكتمل ويعرض شاشة النجاح. وإذا أغلق المستخدم التطبيق تماما، يتولى WorkManager في الخلفية استكمال عملية التسوية وتحديث الحالة فور عودة الاتصال.",
        "deep_answer_ar": "على المستوى الهندسي المتقدم في الأنظمة المالية، يجب حظر أي محاولة دفع جديدة حتى يتم التحقق القاطع من مصير العملية السابقة. إذا فقد الجهاز الاتصال بالكامل أو قتل النظام العملية في الخلفية، لا نعتمد على الكوروتينات في الذاكرة، بل نعتمد على WorkManager مع قيود توفر الشبكة لقراءة المعاملات المعلقة من قاعدة البيانات وإرسال استعلام التسوية للسيرفر فور عودة الاتصال وإشعار المستخدم بنتيجة الدفع عبر تنبيه محلي. في جهة الخادم، يجب فحص مفتاح عدم التكرار عبر أقفال موزعة تمنع معالجة طلبين في نفس الوقت وتلزم الطلب المكرر بانتظار نتيجة الأول. كما نضع شاشات انتظار صريحة ومطمئنة تشرح للمستخدم أن العملية قيد التحقق مع البنك ولن يتم خصم أي مبالغ إضافية. ونراقب عبر لوحات القياس زمن تسوية العمليات ونسب المعاملات المعلقة لرصد أي بطء أو خلل في بوابات الدفع البنكية بشكل استباقي. كما نضمن في واجهة المستخدم عرض رقم مرجعي فريد للمعاملة يمكن للعميل مشاركته مع فريق الدعم الفني في حال استمرار انقطاع الخدمة، ونضع سياسة استرجاع تلقائية تلغي حجز الأموال المعلقة بعد انقضاء أربع وعشرين ساعة إذا لم يؤكد الخادم نجاح المعاملة، مما يحمي حقوق العميل ويوفر أعلى درجات الشفافية المالية."
    }
}

# ==========================================
# SYS-21: Design a Home screen that relies on 3 independent services with partial failure.
# ==========================================
DATA["SYS-21"] = {
    "concept_en": """Designing an enterprise Home screen dependent on multiple independent upstream services—such as a promotional banner service, a personalized user feed, and an algorithm-driven recommendation engine—requires an architecture that isolates partial failures. In mobile application design, a single failing or slow secondary service must never compromise the entire user experience. If the recommendation engine suffers a backend outage, the user must still view their active feed items and promotional banners. The presentation layer models screen state around independent section containers, each maintaining discrete loading, success, and error states. Concurrency must be coordinated using Kotlin Coroutines where child requests execute under a SupervisorJob or via independent async blocks wrapped in runCatching, preventing uncaught cancellations from bubbling up. Furthermore, applying the Stale-While-Revalidate caching pattern allows the UI to render cached local database entities immediately while refreshing sections asynchronously over the network.""",
    "walkthrough_en": """Implementing partial failure isolation and independent section states for a Home screen:
```kotlin
// 1. Independent sealed section state modeling partial failure per surface
sealed interface SectionState<out T> {
    data object Loading : SectionState<Nothing>
    data class Success<T>(val data: T) : SectionState<T>
    data class Error(val errorMessage: String, val cachedFallback: Boolean = false) : SectionState<Nothing>
}

// 2. Composed UI state representing the entire Home screen
data class HomeUiState(
    val banners: SectionState<List<Banner>> = SectionState.Loading,
    val feed: SectionState<List<FeedItem>> = SectionState.Loading,
    val recommendations: SectionState<List<Recommendation>> = SectionState.Loading
)

// 3. ViewModel coordinating concurrent fetches without cross-job cancellation
class HomeViewModel @Inject constructor(
    private val bannerRepo: BannerRepository,
    private val feedRepo: FeedRepository,
    private val recommendationRepo: RecommendationRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(HomeUiState())
    val uiState = _uiState.asStateFlow()

    fun loadHomeScreen() = viewModelScope.launch {
        // Execute independent async jobs wrapped in runCatching to isolate failures
        val bannersDeferred = async { runCatching { bannerRepo.fetchBanners() } }
        val feedDeferred = async { runCatching { feedRepo.fetchFeed() } }
        val recommendationsDeferred = async { runCatching { recommendationRepo.fetchRecommendations() } }

        _uiState.update { current ->
            current.copy(
                banners = bannersDeferred.await().fold(
                    onSuccess = { SectionState.Success(it) },
                    onFailure = { SectionState.Error("Failed to load banners") }
                ),
                feed = feedDeferred.await().fold(
                    onSuccess = { SectionState.Success(it) },
                    onFailure = { SectionState.Error("Failed to load feed") }
                ),
                recommendations = recommendationsDeferred.await().fold(
                    onSuccess = { SectionState.Success(it) },
                    onFailure = { SectionState.Error("Recommendations unavailable") }
                )
            )
        }
    }
}
```""",
    "short_en": """We design resilient Home screens by modeling each content area with independent loading, success, and error states. We fetch data concurrently using Kotlin Coroutines wrapped in runCatching to isolate service exceptions, showing cached local data immediately while individual failed sections display retry buttons without breaking the rest of the screen.""",
    "structured_en": """Designing a Home screen powered by multiple independent backend services requires isolating failures so that a broken endpoint never brings down the whole screen.
I structure the presentation layer around independent section states. The screen UI state does not represent a binary success or failure. Instead, each section—banners, feed, and recommendations—manages its own discrete state.
In the ViewModel, we dispatch concurrent network requests using Kotlin Coroutines async blocks governed by a SupervisorJob.
Each call is wrapped inside runCatching so that an exception in one service does not cancel sibling coroutines or trigger an unhandled failure.
We adopt a Stale-While-Revalidate caching strategy using Room. When the screen opens, it immediately renders cached data from disk.
When network responses arrive, successful sections update seamlessly, while any failing section retains its cached content and displays an inline retry action without blocking user interactions with the rest of the screen.""",
    "deep_senior_en": """From a staff architecture perspective, multi-service aggregation on mobile requires defensive concurrency, selective degradation, and careful lifecycle management.
A common architectural anti-pattern is using standard coroutineScope with async when aggregating endpoints. Under standard coroutines, if the recommendation service fails with an HTTP 500, the exception automatically cancels the parent scope, aborting the feed and banner requests even if they were about to succeed. We eliminate this by utilizing supervisorScope or wrapping each async child in runCatching, ensuring failure containment.
We also introduce differential timeout budgets. User feed data is critical, so we allocate an eight-second deadline, whereas personalized recommendations are secondary and receive a strict three-second timeout. If recommendations do not respond within three seconds, the client abandons the request and collapses the section gracefully or displays popular fallbacks.
Furthermore, we prevent UI layout jank by designing skeleton placeholder loaders that match the exact aspect ratio of incoming content, preventing intrusive layout shifts when sections load at varying speeds.
To handle flaky network connections without stalling interactive rendering, each section independently tracks its own stale-while-revalidate timestamp. If the user scrolls rapidly past a failed section, the hosting recyclerview or lazy column unbinds the section view without aborting in-flight retry requests from other sections, ensuring optimal memory utilization and butter-smooth scrolling performance across legacy devices.
Finally, we implement partial refresh mechanics. When the user performs a swipe-to-refresh gesture, our state holder triggers refreshes only for stale or previously failed sections, saving bandwidth and delivering a highly responsive user experience.""",
    "meta_ar": {
        "id": "SYS-21",
        "questionAr": "كيف تصمم شاشة رئيسية تعتمد على 3 خدمات مع عزل الفشل الجزئي (Partial Failure)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على عزل الفشل الجزئي في واجهات المستخدم المعقدة، واستخدام SupervisorJob والتزامن الآمن في الكوروتين، وتطبيق نمط Stale-While-Revalidate.",
        "why_it_matters_ar": "إذا أدى تعطل خدمة تكميلية مثل شريط التوصيات إلى إظهار شاشة خطأ كاملة تحجب المحتوى الأساسي والمنشورات، فإن التطبيق يفقد وظيفته الرئيسية ويتسبب في نفور المستخدمين.",
        "worked_example_ar": "نموذج جلب متزامن معزول بـ SupervisorJob:\n```kotlin\nval banners = async(SupervisorJob()) { runCatching { bannerApi.getBanners() } }\nval feed = async(SupervisorJob()) { runCatching { feedApi.getFeed() } }\n```",
        "trade_offs_ar": "تقسيم حالة الشاشة إلى أقسام فرعية مستقلة يزيد من تعقيد كائن الـ UiState وعدد الحالات، ولكنه يضمن استقرار الواجهة واستمرار عمل الميزات السليمة بكفاءة تامة.",
        "failure_modes_ar": "استخدام coroutineScope عادي يسبب إلغاء كل الطلبات المتزامنة فور فشل أي طلب منها، أو حدوث قفزات عنيفة في الواجهة Layout Shifts عند اكتمال تحميل الأقسام في أوقات متباينة.",
        "production_perspective_ar": "في كبرى تطبيقات الترفيه والتجارة، نحدد مهلة زمنية قصيرة للخدمات الثانوية كالتوصيات (مثلاً 2.5 ثانية)؛ فإذا تأخرت نتجاهلها ونعرض المحتوى الشائع المخبأ محلياً دون تعطيل الواجهة.",
        "how_to_answer_ar": "قسم حالة الشاشة إلى أقسام فرعية مستقلة تمثل كل خدمة. اشرح التزامن المعزول بـ async و runCatching داخل supervisorScope لمنع إلغاء المهام الزميلة. واشرح عرض كاش Room فورياً.",
        "talking_points_ar": "نمط SupervisorJob مقابل Job العادي، ونمط Stale-While-Revalidate، وهياكل Shimmer التحميلية، ومهل الاستجابة المتفاوتة حسب أهمية القسم، وتحديث الأجزاء التالفة فقط.",
        "follow_ups_ar": "- **المحاور:** \"لماذا يعتبر استخدام async داخل coroutineScope العادي خطأ كبيراً عند تجميع عدة خدمات؟\"\n  **المرشح:** \"لأن coroutineScope ينقل الاستثناءات للأعلى تلقائياً؛ فإذا فشلت خدمة واحدة باستثناء 500، يلغي النطاق كل الكوروتينات الشقيقة فوراً حتى لو كانت على وشك النجاح، مما يعطل الشاشة بأكملها.\"\n\n- **المحاور:** \"كيف تمنع اهتزاز الشاشة (UI Jumping) عند تحميل الأقسام في أوقات مختلفة؟\"\n  **المرشح:** \"نستخدم مكونات تحميل هيكلية (Shimmer Skeletons) ذات ارتفاع وأبعاد ثابتة ومطابقة للمحتوى النهائي لكل قسم، مما يحافظ على ثبات موضع التمرير وراحة عين المستخدم.\"",
        "self_check_ar": "هل وضحت كيفية عزل استثناءات الكوروتين؟ هل بينت بنية الحالة المقسمة لأقسام مستقلة؟ وهل شرحت استراتيجية عرض الكاش المحلي أولاً؟",
        "references_ar": f"- [Kotlin Coroutines: Exceptions and Supervision](https://kotlinlang.org/docs/exception-handling.html) — الدليل الرسمي للتعامل مع الاستثناءات والعزل في الكوروتين.\n- [Offline-first App Architecture](https://developer.android.com/topic/architecture/data-layer/offline-first) — دليل جوجل للتطبيقات المرنة غير المتصلة.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "نصمم الشاشة الرئيسية عبر نمذجة كل قسم بحالة تحميل ونجاح وخطأ مستقلة تماما. نجلب البيانات بالتوازي عبر Coroutines محاطة بـ runCatching لعزل الاستثناءات، مع عرض الكاش المحلي فورا وإتاحة إعادة المحاولة للقسم المتعطل فقط دون المساس بباقي الشاشة.",
        "best_answer_ar": "يتطلب تصميم شاشة رئيسية متكاملة تعتمد على خدمات متعددة عزل الفشل الجزئي بحيث لا يتسبب تعطل خدمة ثانوية كالتوصيات في حرمان المستخدم من مشاهدة الإعلانات والمنشورات الأساسية. نقسم حالة الواجهة إلى أقسام فرعية مستقلة، بحيث يمتلك كل قسم حالته الخاصة للتحميل والنجاح والخطأ بدلا من حالة عامة للشاشة بالكامل. في الـ ViewModel، نطلق طلبات الشبكة بالتوازي باستخدام async داخل supervisorScope يمنع انتقال الاستثناءات بين المهام المختلفة. نحيط كل طلب بـ runCatching لضمان استمرار الطلبات الأخرى حتى لو فشل أحدها تماما. نطبق استراتيجية Stale-While-Revalidate بالاعتماد على قاعدة بيانات Room، فتعرض الشاشة البيانات المخبأة محليا بمجرد فتحها، وعند وصول استجابات الشبكة يتم تحديث الأقسام الناجحة بسلاسة بينما يعرض القسم المتعطل كاشه القديم مع زر مخصص لإعادة المحاولة دون تعطيل باقي الشاشة.",
        "deep_answer_ar": "على المستوى الهندسي المتقدم، يتطلب تجميع عدة خدمات في واجهة الموبايل إدارة صارمة للمهل الزمنية وتدرج الهبوط الوظيفي بأمان. يعد استخدام coroutineScope العادي خطأ كبيرا لأن فشل أحد الطلبات يلغي تلقائيا جميع الطلبات الزميلة الشقيقة؛ ولذلك نعتمد حصريا على supervisorScope أو runCatching لعزل كل مهمة. نحدد مهل زمنية متفاوتة بحسب أهمية المحتوى، فنمنح المنشورات الرئيسية مهلة كافية بينما نحدد للخدمات التكميلية كالتوصيات مهلة سريعة لا تتجاوز ثلاث ثوان، فإذا تأخرت نتجاهلها ونخفي مساحتها أو نعرض محتوى عاما بديلا دون تعطيل المستخدم. نمنع القفزات المزعجة في الواجهة عبر تخصيص هياكل تحميل هيكلية Shimmer بنفس مقاسات الأقسام النهائية لتجنب إعادة حساب أبعاد الشاشة عند اكتمال تحميل كل خدمة في وقت مختلف. كما نبرمج آلية السحب للتحديث الذكية لتقتصر على إعادة طلب الأقسام التي فشلت سابقا فقط، مما يوفر استهلاك البيانات ويمنح تجربة استخدام سلسة وسريعة. كما نضمن في الواجهة إمكانية التفاعل الكامل مع الأقسام الناجحة بشكل طبيعي تماما دون أي تجميد، ونضع زرا واضحا لإعادة محاولة تحميل القسم المتعطل بمفرده دون إعادة تحميل الصفحة بأكملها، مما يوفر استهلاك باقات البيانات ويحافظ على سلاسة التمرير وعمر البطارية. بالإضافة إلى ذلك، نضع مهلة زمنية قصيرة لإلغاء أي طلبات غير مكتملة عند مغادرة المستخدم للشاشة لمنع هدر موارد المعالج وذاكرة الهاتف دون جدوى."
    }
}

# ==========================================
# SYS-22: A feature flag accidentally enables a broken security-sensitive path. How do you contain the impact?
# ==========================================
DATA["SYS-22"] = {
    "concept_en": """When a remote feature flag inadvertently enables a broken, vulnerable, or security-sensitive execution path in production mobile applications, engineering teams must execute a defense-in-depth containment protocol. Relying solely on client-side flag updates is insufficient because clients may be offline, caching old values, or running behind restrictive firewalls. Rapid containment requires a multi-layered response spanning both client and backend infrastructure. At the edge network, backend API gateways must immediately reject requests originating from the compromised path with HTTP 403 Forbidden or 410 Gone, instantly neutralizing exploitation regardless of client app state. Concurrently, an emergency kill switch is pushed to active mobile clients via high-priority silent Firebase Cloud Messaging (FCM) messages, forcing instant local cache invalidation. Furthermore, if the compromised path exposes user session credentials or authentication state, the mobile client must clear local auth tokens and trigger a forced re-authentication sequence to protect customer data.""",
    "walkthrough_en": """Implementing multi-layered containment with instant remote push revocation and session invalidation:
```kotlin
// 1. Emergency containment push receiver handling instant security revocation
class SecurityRevocationReceiver : FirebaseMessagingService() {
    @Inject lateinit var killSwitchManager: KillSwitchManager
    @Inject lateinit var sessionManager: SessionManager

    override fun onMessageReceived(remoteMessage: RemoteMessage) {
        val payload = remoteMessage.data
        if (payload["action"] == "SECURITY_CONTAINMENT_REVOKE") {
            val compromisedFlag = payload["flag_key"] ?: return
            val requiresSessionPurge = payload["purge_session"]?.toBoolean() ?: false

            // Step 1: Force-kill the feature flag in local storage and memory
            killSwitchManager.applyEmergencyKill(compromisedFlag, killFeature = true)

            // Step 2: Invalidate sensitive credentials if security path was breached
            if (requiresSessionPurge) {
                sessionManager.clearSessionAndForceLogin()
            }
        }
    }
}

// 2. Client session manager clearing sensitive credentials and navigating to safe login
class SessionManager @Inject constructor(
    @ApplicationContext private val context: Context,
    private val encryptedPrefs: SharedPreferences
) {
    fun clearSessionAndForceLogin() {
        encryptedPrefs.edit().clear().commit() // Synchronous commit to prevent race conditions
        val loginIntent = Intent(context, LoginActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        }
        context.startActivity(loginIntent)
    }
}
```""",
    "short_en": """We contain a broken security path by blocking incoming requests at the backend API gateway, pushing an emergency kill switch via high-priority silent FCM to invalidate local flag caches, and wiping active session tokens on affected clients to force re-authentication and protect user data.""",
    "structured_en": """Containing an accidental activation of a broken security-sensitive path requires an immediate defense-in-depth containment strategy across client and server.
The primary containment action occurs at the backend gateway. Infrastructure teams deploy an immediate rule rejecting all HTTP calls to the vulnerable endpoints with HTTP 403 Forbidden. This instantly blocks exploitation even if mobile clients continue sending requests with cached flags.
Concurrently on the mobile side, we dispatch high-priority silent FCM data messages to all active installs.
The app receiver catches this command, immediately overrides the flag in memory and disk storage, and routes the user away from the compromised UI.
If the security flaw potentially exposed authentication tokens or user credentials, the containment command triggers an automated session purge, clearing tokens from EncryptedSharedPreferences and navigating the user to a clean login screen.
Finally, we invalidate edge CDN caches and update remote configuration servers to ensure newly launching apps download the safe configuration.""",
    "deep_senior_en": """From a staff mobile security perspective, incident response requires automated playbooks that eliminate human delay during production breaches.
Mobile clients cannot be trusted to patch themselves instantly because users may maintain offline app sessions or disable background push services. Therefore, our architectural containment model mandates that the backend is always the authoritative security boundary. When a security-sensitive feature flag is revoked, API gateways immediately block requests, revoke associated OAuth access tokens, and reject refresh attempts until clients present credentials validated under the secure flow.
On the client side, our feature flag manager incorporates a hard-coded security circuit breaker. If the local client detects that a feature flag marked with a security-critical tag is missing its cryptographic server signature or fails payload checksum validation, the manager rejects the flag and defaults to the disabled state.
To ensure silent emergency pushes reach dormant devices, we utilize high-priority data-only FCM messages that invoke a BackgroundBroadcastReceiver without displaying user-facing notifications.
Finally, after containment is verified through real-time traffic drop dashboards, we conduct a forensic blameless post-mortem. We add automated CI verification checks ensuring that feature flags governing security boundaries require two-person cryptographic sign-off before being toggled on remote configuration consoles, eliminating single-operator human error.""",
    "meta_ar": {
        "id": "SYS-22",
        "questionAr": "تم تفعيل ميزة حساسة أمنياً بالخطأ وبها خلل، كيف تحتوى الأثر وتحمي المستخدمين فوراً؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على قيادة خطط الطوارئ الأمنية، وحظر الثغرات عبر طبقات الخادم والعميل معاً، واستخدام رسائل الدفع الصامتة لإلغاء الميزات، وتطهير الجلسات المخترقة.",
        "why_it_matters_ar": "الاعتماد فقط على تحديث التطبيق أو انتظار مزامنة الـ Feature Flags العادية يترك الثغرة مفتوحة لساعات أو أيام، مما يسمح للمهاجمين باستغلالها وسرقة أموال أو بيانات العملاء.",
        "worked_example_ar": "استقبال أمر طوارئ أمني ومسح الجلسة فوراً:\n```kotlin\nif (payload[\"action\"] == \"SECURITY_PURGE\") {\n    encryptedPrefs.edit().clear().commit()\n    navigateToLogin()\n}\n```",
        "trade_offs_ar": "تسجيل خروج المستخدمين إجبارياً قد يزعج العملاء غير المتأثرين، ولكنه الإجراء الأمني الضروري لحماية الحسابات البنكية والبيانات الحساسة أثناء الحوادث الأمنية النشطة.",
        "failure_modes_ar": "الافتراض الساذج بأن إلغاء العلم في لوحة التحكم يكفي فوراً دون حظر المسار في السيرفر، أو استخدام commit غير متزامن apply() لمسح الجلسة مما قد يترك بيانات سرية قبل قتل التطبيق.",
        "production_perspective_ar": "في البنوك والتطبيقات المالية، نلزم جميع مسارات الدفع والتحويل بقواعد تحقق على السيرفر ترفض أي عملية إذا لم تكن مصحوبة بتوقيع رقمي موثق، وتلغي التوكنات فور تفعيل أمر الطوارئ.",
        "how_to_answer_ar": "قسم خطة الاحتواء إلى ثلاث طبقات متزامنة: حظر السيرفر أولاً برمز 403، إرسال أمر FCM صامت وفوري للتطبيقات النشطة، ومسح الجلسة محلياً والتحويل لصفحة الدخول في حال تأثر التوكنات.",
        "talking_points_ar": "مفهوم Defense in Depth، وحظر نقاط النهاية في الـ API Gateway، وإلغاء توكنات OAuth في السيرفر، ورسائل FCM الصامتة، ومسح EncryptedSharedPreferences بـ commit متزامن.",
        "follow_ups_ar": "- **المحاور:** \"لماذا يعتبر حظر الـ API في السيرفر أولى خطوات الاحتواء وأهمها؟\"\n  **المرشح:** \"لأن الهواتف قد تكون غير متصلة أو يستخدم أصحابها أدوات اعتراض وتلاعب بالبيانات، فالسيرفر هو نقطة الحقيقة الأمنية المطلقة؛ وحظر المسار هناك يمنع أي استغلال حتى لو ظل العلم مفعلاً في التطبيق.\"\n\n- **المحاور:** \"لماذا نستخدم commit() بدلاً من apply() عند مسح الجلسة في حالة الطوارئ الأمنية؟\"\n  **المرشح:** \"لأن apply تنفذ الحفظ بشكل غير متزامن في الخلفية، وإذا قام التطبيق بإنهاء العملية أو إعادة تشغيل الشاشة فوراً قد لا تكتمل عملية المسح؛ commit تضمن مسح البيانات من القرص في نفس اللحظة بشكل متزامن.\"",
        "self_check_ar": "هل رتبت خطوات الاحتواء بالأولوية الصحيحة؟ هل أكدت على دور الخادم كخط دفاع أول؟ وهل شرحت كيفية مسح بيانات الجلسة بأمان تام؟",
        "references_ar": f"- [OWASP Mobile Top 10](https://owasp.org/www-project-mobile-top-10/) — المرجع القياسي للمخاطر الأمنية في تطبيقات الموبايل.\n- [Incident Response Plan Guidelines](https://csrc.nist.gov/publications/detail/sp/800-61/rev-2/final) — معايير NIST للاستجابة للحوادث الأمنية واحتوائها.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "نحتوي الخلل الأمني عبر حظر نقاط النهاية فورا في بوابة السيرفر، وإرسال أمر إيقاف طارئ عبر FCM صامت لإلغاء تفعيل الميزة في كاش التطبيقات، مع مسح رموز الجلسة محليا لإجبار المستخدمين على إعادة تسجيل الدخول وحماية الحسابات.",
        "best_answer_ar": "يتطلب احتواء الخلل الأمني الناتج عن تفعيل ميزة حساسة بالخطأ خطة دفاعية متعددة الطبقات تشمل الواجهة الخلفية وتطبيقات الموبايل معا. الإجراء الأسرع والأكثر حسما يبدأ من السيرفر، حيث يضع مهندسو البنية التحتية قاعدة فورية في بوابة الـ API لرفض أي طلبات موجهة لنقاط النهاية المعيبة برمز 403 Forbidden، مما يحظر الاستغلال فورا حتى لو ظلت النسخ القديمة ترسل طلبات. بالتوازي مع ذلك، نرسل إشعار دفع صامت عالي الأولوية عبر FCM لجميع التطبيقات النشطة، فيستقبله التطبيق ويلغي تفعيل الميزة فورا في الذاكرة ومساحة التخزين المحلي. إذا كان الخلل يمس أمان الجلسة أو رموز المصادقة، يمسح التطبيق التوكنز المخزنة في EncryptedSharedPreferences فورا ويوجه المستخدم لشاشة تسجيل الدخول النظيفة. وأخيرا، نبطل كاش خوادم الـ CDN ونحدث إعدادات السيرفر لضمان حصول أي تطبيق يفتح لاحقا على الإعدادات الآمنة.",
        "deep_answer_ar": "على المستوى الهندسي الأمني المتقدم، لا يمكن الاعتماد حصريا على تحديث التطبيق لأن هواتف العملاء قد تكون غير متصلة أو متوقفة مؤقتا؛ ولذلك تظل الواجهة الخلفية هي خط الدفاع الحاسم والمطلق. عند إلغاء ميزة أمنية، يقوم السيرفر فورا بإبطال رموز الوصول OAuth ورفض تجديد الجلسات حتى يعيد العميل تسجيل الدخول وفق المسار السليم. داخل التطبيق، نطبق قاطع دائرة أمني مشفر يرفض أي إعدادات للميزات الحساسة إذا لم تكن موقعة رقميا بتوقيع السيرفر المعتمد. نعتمد في إرسال أوامر الإلغاء على رسائل FCM صامتة عالية الأولوية تنفذ فورا في الخلفية دون إظهار أي إشعارات تشوش على المستخدم. وبعد السيطرة الكاملة على الحادثة وتأكيد توقف حركة المرور المشبوهة، نجري مراجعة أمنية شاملة ونضيف قيودا صارمة في خوادم الإعدادات تمنع تفعيل أي ميزة أمنية حساسة إلا بعد موافقة وتوقيع مهندسين اثنين لمنع الأخطاء الفردية مستقبلا. كما نوفر فحصا أمنيا دوريا في مسار إقلاع التطبيق يتحقق من سلامة البيئة البرمجية وعدم التلاعب بملفات الإعدادات المحلية على الأجهزة التي تم كسر حمايتها Rooted Devices، وننبه فريق الاستجابة للحوادث فور رصد أي نشاط غير معتاد عبر لوحات مراقبة مخصصة تتابع توزيع التوكنز وتكشف أي محاولات لاستغلال الثغرات البرمجية في الوقت الفعلي."
    }
}

# ==========================================
# SYS-23: How would you migrate a large legacy XML app incrementally to Compose?
# ==========================================
DATA["SYS-23"] = {
    "concept_en": """Migrating a large-scale enterprise Android application with hundreds of legacy XML layouts and ViewBinding screens to Jetpack Compose requires a disciplined, incremental migration strategy rather than a risky whole-app rewrite. Big-bang rewrites introduce severe business regressions, stall product feature delivery, and risk introducing subtle UI discrepancies. A production-ready migration follows a bottom-up leaf-node progression: begin by porting design system components, color palettes, typography styles, and atomic custom views to Compose. Next, embed these new Compose components inside existing XML layouts using ComposeView, ensuring the ViewCompositionStrategy is explicitly set to DisposeOnViewTreeLifecycleDestroyed to prevent memory leaks with Fragment lifecycles. New screens and features are authored entirely in pure Compose. Over time, parent Fragments and Activities are refactored into pure Compose destinations, systematically retiring legacy XML files while maintaining a single, uninterrupted product release cadence.""",
    "walkthrough_en": """Embedding Compose components inside legacy XML Fragments with lifecycle safety:
```kotlin
// 1. Embedding a Compose header inside an existing XML Fragment layout
class LegacyUserProfileFragment : Fragment(R.layout.fragment_user_profile) {
    private val viewModel: UserProfileViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Locate the ComposeView embedded inside the legacy XML layout
        val composeHeaderView = view.findViewById<ComposeView>(R.id.compose_header_container)

        composeHeaderView.apply {
            // Mandatory: Configure lifecycle disposition strategy to prevent memory leaks in Fragments
            setViewCompositionStrategy(ViewCompositionStrategy.DisposeOnViewTreeLifecycleDestroyed)

            setContent {
                AppTheme {
                    val userState by viewModel.userState.collectAsStateWithLifecycle()
                    UserProfileHeader(
                        user = userState,
                        onAvatarClicked = { viewModel.onAvatarClicked() }
                    )
                }
            }
        }
    }
}

// 2. Pure Jetpack Compose component replacing legacy custom XML view
@Composable
fun UserProfileHeader(
    user: UserProfileState,
    onAvatarClicked: () -> Unit,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier
            .fillMaxWidth()
            .padding(16.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        AsyncImage(
            model = user.avatarUrl,
            contentDescription = "User Avatar",
            modifier = Modifier
                .size(64.dp)
                .clip(CircleShape)
                .clickable { onAvatarClicked() }
        )
        Spacer(modifier = Modifier.width(16.dp))
        Column {
            Text(text = user.fullName, style = MaterialTheme.typography.titleMedium)
            Text(text = user.email, style = MaterialTheme.typography.bodyMedium)
        }
    }
}
```""",
    "short_en": """We migrate legacy XML applications to Compose incrementally using a bottom-up approach. We migrate atomic design system components first, embedding them into XML layouts via ComposeView with lifecycle disposal strategies. We build all new features purely in Compose, gradually refactoring parent screens without stalling roadmap feature velocity.""",
    "structured_en": """Migrating a large legacy Android application to Jetpack Compose must be executed incrementally to prevent feature freezes and UI regressions.
I reject high-risk big-bang rewrites in favor of a bottom-up component migration.
We begin at the design system foundation, porting theme attributes, color tokens, typography, and atomic UI widgets like buttons, input fields, and badges to Compose.
These composables are integrated directly into existing XML layouts using ComposeView.
When embedding Compose inside Fragments, setting ViewCompositionStrategy to DisposeOnViewTreeLifecycleDestroyed is mandatory to prevent composition memory leaks when the Fragment view is destroyed.
Next, all newly requested product features are built in pure Compose from day one.
Finally, we migrate screen-level containers. Complex RecyclerViews are converted to LazyColumns, and parent Fragments are gradually retired in favor of Compose destinations, keeping the app stable and continuously releasable throughout the migration.""",
    "deep_senior_en": """From a staff engineering perspective, migrating to Compose is as much an architectural state-management alignment as it is a UI framework change.
The most common mistake teams make during migration is duplicating state holders. In a hybrid codebase, an XML screen and an embedded ComposeView must observe the exact same ViewModel StateFlow stream. Using collectAsStateWithLifecycle in Compose ensures that composable rendering pauses automatically when the hosting lifecycle drops below the Started state, matching the lifecycle behavior of ViewBinding.
Performance must be monitored vigilantly during hybrid coexistence. Running ComposeView inside every item of a legacy RecyclerView creates severe frame drops because the composition runtime is repeatedly initialized and disposed during scrolling. The correct approach is either migrating the entire list to a LazyColumn at once, or converting individual complex screens rather than scattering micro-composables inside scrolling view holders.
Furthermore, interoperability must handle third-party legacy views that lack native Compose equivalents, such as MapView, AdViews, or CameraX previews. We bridge these using AndroidView wrappers with explicit update lambdas, ensuring seamless two-way binding.
Finally, we track migration progress through automated dashboard metrics, measuring the ratio of Composable functions versus XML layout files in CI, providing leadership with clear visibility into code health improvements and bundle size reductions.""",
    "meta_ar": {
        "id": "SYS-23",
        "questionAr": "كيف تخطط وترقي تطبيقاً ضخماً مبنياً بـ XML تدريجياً إلى Jetpack Compose دون تعطيل العمل؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على وضع استراتيجية ترقية تدريجية من XML إلى Compose، وفهم قضايا التوافق المشترك بين النظامين، وإدارة دورة حياة ComposeView وتفادي تسريب الذاكرة ومشاكل الأداء.",
        "why_it_matters_ar": "محاولة إعادة كتابة التطبيق بالكامل من الصفر Big-Bang تؤدي لتجميد خارطة الطريق لشهور، وتتسبب في إدخال أخطاء جديدة وتراجع الإيرادات، بينما الترقية التدريجية تحافظ على استقرار الأعمال.",
        "worked_example_ar": "دمج Compose في XML مع استراتيجية تصريف الذاكرة الصارمة:\n```kotlin\ncomposeView.apply {\n    setViewCompositionStrategy(ViewCompositionStrategy.DisposeOnViewTreeLifecycleDestroyed)\n    setContent { AppTheme { UserHeader(state) } }\n}\n```",
        "trade_offs_ar": "الجمع المؤقت بين XML و Compose يزيد حجم التطبيق قليلاً ويبطئ البناء المبدئي لوجود مترجمين، ولكنه يتيح الاستمرار في تسليم الميزات والترقية السلسة دون أي انقطاع.",
        "failure_modes_ar": "نسيان ضبط setViewCompositionStrategy مما يسبب تسريب ذاكرة الـ Fragment عند تدمير واجهته، أو وضع ComposeView داخل عناصر RecyclerView مما يدمر معدل الإطارات أثناء التمرير.",
        "production_perspective_ar": "في المشروعات الضخمة، نلزم جميع الفرق بأن تكون الشاشات والميزات الجديدة بنسبة 100% بـ Compose، ونحدد هدفاً فصلياً لتحويل شاشتين أو ثلاث شاشات قديمة مع كل مرحلة تطوير.",
        "how_to_answer_ar": "ابدأ برفض فكرة إعادة الكتابة الشاملة. وضح استراتيجية الترقية من الأسفل للأعلى بدءاً بنظام التصميم Design System. اشرح دمج المكونات بـ ComposeView وضبط استراتيجية الذاكرة وبناء الميزات الجديدة بـ Compose.",
        "talking_points_ar": "استراتيجية DisposeOnViewTreeLifecycleDestroyed، وفخ الـ ComposeView داخل RecyclerView، واستخدام AndroidView للعناصر القديمة كالخرائط، وتوحيد StateFlow بين النظامين.",
        "follow_ups_ar": "- **المحاور:** \"لماذا يعتبر وضع ComposeView داخل كل عنصر في RecyclerView فكرة سيئة جداً للأداء؟\"\n  **المرشح:** \"لأن إنشاء وإلغاء الـ Composition لكل عنصر يتم تدويره يستهلك وقتاً وذاكرة أكبر بكثير من كود الـ Views القديم، مما يسبب Jank وسقوط إطارات حاد؛ والحل هو تحويل القائمة كاملة لـ LazyColumn.\"\n\n- **المحاور:** \"كيف تتعامل مع عناصر قديمة لا يوجد لها بديل مباشر في Compose مثل MapView أو CameraX؟\"\n  **المرشح:** \"نستخدم كائن `AndroidView` التوافقي الذي يسمح بإنشاء View أندرويد عادي داخل شجرة الـ Composable وربطه بدوال التحديث الخاصة بدورة حياة أندرويد بسلاسة.\"",
        "self_check_ar": "هل رفضت خيار إعادة الكتابة الشاملة؟ هل بينت استراتيجية الترقية من نظام التصميم حتى الشاشات؟ وهل شرحت إدارة الذاكرة بـ ComposeView؟",
        "references_ar": f"- [Migrating to Jetpack Compose](https://developer.android.com/jetpack/compose/migrate) — دليل جوجل الرسمي لترقية التطبيقات تدريجياً إلى كومبوز.\n- [Compose Interoperability APIs](https://developer.android.com/jetpack/compose/interop/interop-apis) — التوثيق الرسمي لدمج كومبوز مع نظام Views التقليدي.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "نرقي التطبيق تدريجيا من الأسفل للأعلى عبر تحويل عناصر نظام التصميم الأساسية أولا ودمجها في XML عبر ComposeView باستراتيجية تصريف آمنة للذاكرة. نبني الميزات الجديدة بالكامل بـ Compose، ثم نحول القوائم والشاشات تدريجيا دون إيقاف تسليم ميزات العمل.",
        "best_answer_ar": "تتطلب ترقية التطبيقات الضخمة من XML إلى Jetpack Compose خطة تدريجية مدروسة تتجنب إعادة الكتابة الشاملة التي تجمد خريطة المنتجات وتزيد من مخاطر الأعطال. نبدأ الترقية من القاعدة عبر بناء نظام التصميم بمكونات Compose الذرية كالأزرار وحقول الإدخال والألوان والخطوط. ندمج هذه المكونات في شاشات XML القائمة باستخدام ComposeView مع ضبط إلزامي لـ ViewCompositionStrategy على DisposeOnViewTreeLifecycleDestroyed لمنع تسريب الذاكرة عند تدمير واجهة الـ Fragment. نلزم الفرق ببناء كل الشاشات والميزات الجديدة بنسبة مائة بالمائة عبر Compose مباشرة. ثم ننتقل لترقية الحاويات الكبيرة، فنحول قوائم RecyclerView المعقدة إلى LazyColumn، ونستبدل الـ Fragments تدريجيا بوجهات Compose كاملة، مما يحافظ على استقرار التطبيق واستمرار إطلاقه للمستخدمين دون انقطاع.",
        "deep_answer_ar": "على المستوى الهندسي المتقدم، ترتبط ترقية الواجهات بتوحيد إدارة الحالة البرمجية، حيث يجب أن تتشارك عناصر XML و Compose نفس مصدر البيانات من StateFlow داخل الـ ViewModel. نستخدم collectAsStateWithLifecycle في Compose لضمان إيقاف إعادة التجميع عند توقف الشاشة بما يطابق سلوك دورة حياة أندرويد. نحذر من الوقوع في فخ الأداء الناتج عن وضع ComposeView داخل كل عنصر في RecyclerView قديم، لأن ذلك يستهلك موارد المعالج ويسبب سقوطا حادا في الإطارات؛ والحل الأمثل هو تحويل القائمة بالكامل إلى LazyColumn دفعة واحدة. للمكونات التي لا تمتلك بديلا مباشرا في Compose كخرائط MapView أو عروض الكاميرا، ندمجها بسلاسة عبر AndroidView مع دوال تحديث منضبطة. كما نراقب نسبة تقدم الترقية آليا في خوادم الـ CI عبر تتبع نسبة ملفات Compose مقارنة بملفات الـ XML لتقديم مؤشرات واضحة للإدارة حول تحسن جودة الكود ونقص حجم الحزمة. كما ننظم ورش عمل داخلية وتوثيقا معماريا شاملا لنماذج التصميم المعتمدة في Compose لتوجيه المطورين نحو الممارسات السليمة وتجنب إعادة بناء المكونات غير الضرورية Recomposition، ونحرص على توحيد اختبارات الواجهة البرمجية باستخدام ComposeTestRule إلى جانب الاختبارات القديمة لضمان مطابقة التصميم وسلوك المكونات بنسبة مائة بالمائة. ونشجع الفرق على البدء بالشاشات الثانوية مثل شاشة الإعدادات أو الملف الشخصي لاكتساب الخبرة العملية قبل الانتقال إلى الشاشات المعقدة ذات التدفقات المالية الحرجة."
    }
}

# ==========================================
# SYS-24: How would you design for poor connectivity and intermittent power loss?
# ==========================================
DATA["SYS-24"] = {
    "concept_en": """Designing an enterprise mobile system for hostile deployment environments—characterized by intermittent cellular connectivity, severe bandwidth throttling, sudden airplane mode switches, and abrupt power loss—requires an offline-first architecture. In such environments, the local persistent database must serve as the single source of truth, and network operations must be modeled as asynchronous synchronization events rather than prerequisites for user interaction. SQLite persistence via Room must enable Write-Ahead Logging (WAL) mode to protect database files from physical corruption during abrupt battery depletion or unexpected process termination. User actions must follow the local outbox pattern: every mutation is written to a durable pending operations table within an atomic SQLite transaction before updating the user interface. Background synchronization is delegated to WorkManager with battery-aware constraints, utilizing delta sync payloads and compact binary formats to minimize cellular overhead.""",
    "walkthrough_en": """Implementing an atomic mutation outbox with battery-conscious background synchronization:
```kotlin
// 1. Room database configured with Write-Ahead Logging for power-loss corruption resistance
@Database(entities = [OrderEntity::class, OutboxMutationEntity::class], version = 1)
abstract class ResilientAppDatabase : RoomDatabase() {
    abstract fun outboxDao(): OutboxDao
    abstract fun orderDao(): OrderDao

    companion object {
        fun buildDatabase(context: Context): ResilientAppDatabase {
            return Room.databaseBuilder(context, ResilientAppDatabase::class.java, "resilient.db")
                .setJournalMode(JournalMode.WRITE_AHEAD_LOGGING) // High durability against sudden battery shutoff
                .build()
        }
    }
}

// 2. Atomic outbox mutation record storing user intent locally before network dispatch
@Entity(tableName = "outbox_mutations")
data class OutboxMutationEntity(
    @PrimaryKey val mutationId: String = UUID.randomUUID().toString(),
    val actionType: String,
    val payloadJson: String,
    val timestampMs: Long = System.currentTimeMillis(),
    val retryCount: Int = 0
)

// 3. Scheduling battery-conscious, network-constrained synchronization via WorkManager
class ResilientSyncScheduler @Inject constructor(
    private val workManager: WorkManager
) {
    fun scheduleOutboxSync() {
        val constraints = Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .setRequiresBatteryNotLow(true)
            .build()

        val syncRequest = OneTimeWorkRequestBuilder<OutboxSyncWorker>()
            .setConstraints(constraints)
            .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 15, TimeUnit.SECONDS)
            .build()

        workManager.enqueueUniqueWork("outbox_sync", ExistingWorkPolicy.KEEP, syncRequest)
    }
}
```""",
    "short_en": """We design for poor connectivity and power loss using an offline-first architecture with Room Write-Ahead Logging to prevent database corruption. We store mutations in a local outbox table before updating the UI, delegating background uploads to WorkManager with battery and network constraints, and streaming delta updates.""",
    "structured_en": """Designing for extreme network volatility and sudden power loss requires treating local persistence as the primary source of truth.
I configure Room with SQLite Write-Ahead Logging (WAL) mode. This guarantees atomic transaction durability and prevents physical database corruption if the device shuts down mid-write.
Every user mutation follows the transactional outbox pattern. When an action occurs, the app saves the intent to an outbox table in an atomic database transaction before updating the UI optimistically.
The UI never spins with blocking network loaders; actions feel instantaneous because they commit to disk locally.
Background uploads are handed off to WorkManager configured with constraints like connected network and battery not low.
WorkManager handles exponential backoff and retries safely across device reboots.
To preserve cellular data on slow networks, synchronization requests exchange compressed delta payloads using server revision tokens rather than re-transmitting entire entities.""",
    "deep_senior_en": """From a staff mobile architecture perspective, designing for extreme environments requires managing data synchronization conflicts, radio power states, and honest user interface state indicators.
The primary risk in offline-first systems is conflict resolution. When multiple offline mutations accumulate on the client while other edits occur on the server, blind last-write-wins policies cause silent data loss. We resolve this by associating records with server revision vectors or timestamps. When the client syncs, the backend detects version divergence and executes deterministic three-way merges or flags conflicts for manual user resolution.
To survive intermittent cellular conditions, network serialization must minimize packet size. We replace verbose JSON payloads with Protocol Buffers or GZIP-compressed binary streams, significantly reducing transmission time over flaky 2G or 3G connections and lowering socket timeout rates.
Radio management is critical for devices with degraded batteries. Firing frequent small network requests keeps the cellular baseband processor energized in high-power states. Our sync engine batches pending outbox mutations, flushing up to fifty operations in a single persistent HTTP connection to allow the cellular radio to return to low-power sleep immediately.
Finally, the user experience must maintain transparent honesty. We provide visual pending indicators on un-synced items, reassuring users that their data is safely persisted on their phone and will synchronize automatically when power and signal restore.""",
    "meta_ar": {
        "id": "SYS-24",
        "questionAr": "كيف تصمم تطبيقاً يعمل بكفاءة في بيئات الاتصال شديد الضعف والانقطاع المفاجئ للطاقة والبطارية؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على بناء تطبيقات تعمل في البيئات القاسية دون اتصال، وتأمين سلامة SQLite بنمط WAL ضد انقطاع الطاقة، وتطبيق نمط Outbox، وإدارة استهلاك البطارية والمزامنة بـ WorkManager.",
        "why_it_matters_ar": "في المناطق النائية والشبكات الضعيفة، يؤدي انقطاع الطاقة المفاجئ أو الشبكة لتلف ملفات قاعدة البيانات وفقدان بيانات العمليات الحرجة التي أدخلها المستخدم، مما يوقف الأعمال الميدانية تماماً.",
        "worked_example_ar": "تفعيل نمط الحماية القصوى WAL في قاعدة بيانات Room:\n```kotlin\nRoom.databaseBuilder(context, AppDb::class.java, \"app.db\")\n    .setJournalMode(RoomDatabase.JournalMode.WRITE_AHEAD_LOGGING)\n    .build()\n```",
        "trade_offs_ar": "النمط غير المتصل أولاً (Offline-First) يتطلب بناء آليات معقدة للمزامنة وحل تضارب البيانات على السيرفر، ولكنه الحل الوحيد الذي يضمن استمرار التطبيق في بيئات العمل القاسية.",
        "failure_modes_ar": "استخدام سياسة الكتابة الأخيرة تفوز Last-Write-Wins بدون وعي مما يمسح تعديلات المستخدمين الآخرين، أو تشغيل المزامنة فوراً دون مراعاة انخفاض البطارية مما يؤدي لإطفاء الهاتف.",
        "production_perspective_ar": "في التطبيقات الميدانية وتطبيقات التوصيل، نضغط الحزم بتقنية Protocol Buffers لتوفير استهلاك باقات البيانات، ونعرض شارات مرئية ملونة على السجلات توضح حالة مزامنتها مع السيرفر.",
        "how_to_answer_ar": "ابدأ بقاعدة البيانات كأصل وحيد للحقيقة SSOT مع تفعيل نمط WAL لحماية الملفات من التلف الفيزيائي. اشرح نمط صندوق الصادر Outbox لحفظ العمليات محلياً أولاً. وضح قيود WorkManager للمزامنة مع الشاحن والواي فاي.",
        "talking_points_ar": "نمط Write-Ahead Logging في SQLite، ونمط Outbox Pattern، ومزامنة الفوارق Delta Sync، وحل التضارب عبر Revision Vectors، وتقليل استيقاظ راديو الهاتف.",
        "follow_ups_ar": "- **المحاور:** \"لماذا يعتبر نمط Write-Ahead Logging (WAL) حاسماً لمنع تلف قاعدة البيانات عند انطفاء الهاتف فجأة؟\"\n  **المرشح:** \"لأن WAL يكتب التعديلات في ملف سجل منفصل متسلسل دون المساس بملف قاعدة البيانات الأصلي مباشرة؛ فإذا انقطعت الطاقة في منتصف الكتابة، يتجاهل SQLite السجل غير المكتمل وتبقى قاعدة البيانات الأصلية سليمة تماماً دون أي تلف فيزيائي.\"\n\n- **المحاور:** \"كيف تتعامل مع تضارب التعديلات (Sync Conflicts) عندما يعدل مستخدمان نفس البيان دون اتصال؟\"\n  **المرشح:** \"نرفق مع كل سجل رقم إصدار موجه (Revision Vector)؛ وعند المزامنة يكتشف السيرفر التعارض، فإما أن يدمج الحقول غير المتضاربة آلياً، أو يحفظ النسختين ويطلب من المستخدم في الواجهة اختيار النسخة الصحيحة.\"",
        "self_check_ar": "هل بينت دور نمط WAL في حماية قاعدة البيانات من انقطاع الطاقة؟ هل شرحت نمط Outbox وتحديث الواجهة الفوري؟ وهل وضحت استراتيجيات حل التضارب؟",
        "references_ar": f"- [SQLite Write-Ahead Logging](https://www.sqlite.org/wal.html) — التوثيق الرسمي لنمط WAL لحماية قواعد البيانات.\n- [WorkManager Constraints and Backoff](https://developer.android.com/topic/libraries/architecture/workmanager/how-to/define-work) — دليل جدولة المهام وفق قيود النظام في أندرويد.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "نصمم للاتصال الضعيف وانقطاع الطاقة عبر معمارية ترتكز على التخزين المحلي كأصل وحيد للبيانات مع تفعيل WAL في Room لمنع تلف الملفات. نحفظ العمليات في جدول Outbox محلي قبل تحديث الواجهة، ونفوض الرفع لـ WorkManager بقيود الشبكة والبطارية مع تبادل التحديثات الجزئية المضغوطة.",
        "best_answer_ar": "يتطلب العمل في البيئات القاسية والشبكات المتقلبة بناء التطبيق بفلسفة العمل دون إنترنت أولا، بحيث تصبح قاعدة البيانات المحلية هي المصدر الوحيد للحقيقة وتعتبر الشبكة مجرد وسيلة مزامنة ثانوية. نعد قاعدة بيانات Room بنمط Write-Ahead Logging لضمان ذرية المعاملات وحماية الملفات من التلف الفيزيائي إذا انطفأ الهاتف فجأة أثناء الكتابة. نعتمد نمط صندوق الصادر المحلي، فعندما يقوم المستخدم بأي إجراء كإنشاء طلب، يحفظ التطبيق العملية فورا في جدول محلي داخل معاملة ذرية ويحدث الواجهة فورا دون انتظار الشبكة. نفوض مهام المزامنة لـ WorkManager مع قيود صارمة تشترط وجود اتصال بالإنترنت وعدم انخفاض البطارية، مع جدولتها بتراجع أسي عند الفشل. ولتوفير البيانات عبر شبكات الجيل الثاني والثالث البطيئة، نتبادل تحديثات جزئية مضغوطة تعتمد على أرقام مراجعات السيرفر بدلا من إعادة إرسال الكائنات كاملة.",
        "deep_answer_ar": "على المستوى الهندسي المتقدم، يمثل حل تضارب البيانات وإدارة طاقة شريحة الاتصال التحدي الأكبر في الأنظمة غير المتصلة. تسبب سياسات الكتابة الأخيرة تفوز فقدانا صامتا للبيانات عند تعديل نفس السجل من أجهزة مختلفة؛ ولذلك نربط السجلات بأرقام إصدارات موجهة تتيح للخادم اكتشاف التعارض ودمج التعديلات آليا أو تنبيه المستخدم لاتخاذ قرار يدوي. لتقليل احتمالية انقطاع المقابس، نستبدل نصوص JSON المطولة بتنسيقات ثنائية مضغوطة مثل Protocol Buffers تقلل حجم الحزم وتسرع الإرسال عبر الشبكات الضعيفة. كما نراعي دورة حياة راديو الهاتف الخلوي الذي يستهلك طاقة هائلة متى تم تفعيله، فنجمع العمليات المعلقة ونرفعها دفعة واحدة في اتصال دائم بدلا من تشتيت الطلبات وإبقاء الراديو في وضع الاستهلاك العالي. وأخيرا، نضمن الصدق والشفافية في الواجهة بعرض شارات توضح للمستخدم أن بياناته محفوظة بأمان محليا وجار مزامنتها فور توفر الطاقة والشبكة دون إشعاره بالقلق. كما نطبق آلية ضغط متقدمة للسجلات والبيانات قبل تخزينها محليا لتوفير مساحة التخزين على أجهزة الفئات الاقتصادية، ونعتمد على مؤشرات واضحة في شريط الحالة تنبه المستخدم لحالة الاتصال وعدد العمليات العالقة في صندوق الصادر، مما يمنحه ثقة تامة في أن معاملاته لم تفقد وسيتم إرسالها بمجرد عودة الطاقة والشبكة تلقائيا دون أي تدخل منه."
    }
}

# ==========================================
# Validation and Execution Functions
# ==========================================
def validate_words():
    errors = []
    for qid, d in sorted(DATA.items()):
        meta = d["meta_ar"]
        # English counts
        s_en = len(d["short_en"].split())
        st_en = len(d["structured_en"].split())
        d_en = len(d["deep_senior_en"].split())

        # Arabic counts
        q_ar = len(meta["quick_answer_ar"].split())
        b_ar = len(meta["best_answer_ar"].split())
        d_ar = len(meta["deep_answer_ar"].split())

        print(f"{qid}: en_s={s_en}, en_st={st_en}, en_d={d_en} | ar_q={q_ar}, ar_b={b_ar}, ar_d={d_ar}")

        # English checks
        if not (35 <= s_en <= 110):
            errors.append(f"{qid} short_en out of range: {s_en} (35-110)")
        if not (100 <= st_en <= 280):
            errors.append(f"{qid} structured_en out of range: {st_en} (100-280)")
        if not (200 <= d_en <= 650):
            errors.append(f"{qid} deep_senior_en out of range: {d_en} (200-650)")

        # Arabic checks
        if not (35 <= q_ar <= 110):
            errors.append(f"{qid} quick_answer_ar out of range: {q_ar} (35-110)")
        if not (90 <= b_ar <= 280):
            errors.append(f"{qid} best_answer_ar out of range: {b_ar} (90-280)")
        if not (180 <= d_ar <= 650):
            errors.append(f"{qid} deep_answer_ar out of range: {d_ar} (180-650)")

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

    ee.save_topic_metadata("sys_17_24", topic_meta)
    ee.merge_all_metadata()

    for qid in sorted(DATA.keys()):
        errs = ee.validate_question(qid)
        if errs:
            print(f"Errors in {qid}:")
            for e in errs:
                print(f"  ❌ {e}")
            sys.exit(1)

    print("\nAll 8 SYS questions (SYS-17 to SYS-24) successfully elevated and passed validation!\n")

if __name__ == "__main__":
    apply_elevations()
