#!/usr/bin/env python3
"""Generator for SYS-17 through SYS-24 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "sys.json"

SYS_17_24 = [
    {
        "id": "SYS-17",
        "arabic_explanation": (
            "كيف تصمم نظام مراقبة تشغيلية (Operational Monitoring) ومفاتيح إيقاف طارئة (Remote Kill Switches) لإدارة الأزمات في الإنتاج؟\n\n"
            "1. ما هو الـ Remote Kill Switch ولماذا هو ضروري؟\n   - في تطبيقات الموبايل، نشر تحديث جديد لعلاج ثغرة أمنية أو انهيار كارثي يستغرق ساعات أو أياماً عبر مراجعة Google Play (Play Store Review Delay).\n   - الـ Kill Switch يمنح فريق الهندسة القدرة على **إيقاف ميزة معينة فورياً عن بُعد (Real-Time Feature Shutdown)** خلال ثوانٍ معدودة دون الحاجة لتحديث الـ APK.\n\n"
            "2. المعمارية الهندسية لمفاتيح الإيقاف السريعة (Bypass & Distribution Channels):\n   - **قناة التوزيع فائقة السرعة**: لا تعتمد على الـ Polling الدوري البطيء (الذي قد يستغرق 12 ساعة). استخدم إشعارات **High-Priority Data FCM** التي توقظ التطبيق في الخلفية فور إرسال إشارة الطوارئ وتجبره على تحديث الـ Config.\n   - **التخزين المؤقت المحلي (Local Disk Fallback)**: حفظ حالة الـ Kill Switches في مساحة تخزين فورية سريعة القراءة (`SharedPreferences` أو `DataStore`) لتطبيقها بشكل متزامن عند فتح التطبيق.\n   - **السلوك الآمن عند الانقطاع (Fail-Safe Defaults)**: في حال عدم توفر اتصال بالإنترنت، يجب أن يعمل التطبيق بالوضع الافتراضي الآمن (Safe Mode) للميزات الحساسة.\n\n"
            "3. أتمتة الإيقاف عبر مؤشرات المراقبة (Automated Tripwires):\n   - ربط نظام الـ APM ومراقبة الأعطال (Sentry / Datadog) بـ Alert Webhook؛ إذا تجاوز معدل الانهيار في ميزة جديدة 2%، يقوم النظام تلقائياً بتفعيل الـ Kill Switch دون انتظار تدخل بشري."
        ),
        "practical_walkthrough": (
            "تنفيذ حاجز برمجي (Kill Switch Guard) يعطل الميزة فورياً ويعرض واجهة صيانة بديلة:\n"
            "```kotlin\n"
            "class KillSwitchManager @Inject constructor(\n"
            "    @ApplicationContext private val context: Context\n"
            ") {\n"
            "    private val prefs = context.getSharedPreferences(\"emergency_kill_switches\", Context.MODE_PRIVATE)\n"
            "\n"
            "    fun isFeatureKilled(featureKey: String): Boolean {\n"
            "        // فحص فوري وسريع من الذاكرة/الملف المحلي دون تعطيل الـ Main Thread\n"
            "        return prefs.getBoolean(\"kill_$featureKey\", false)\n"
            "    }\n"
            "\n"
            "    fun applyEmergencyKill(featureKey: String, isKilled: Boolean) {\n"
            "        prefs.edit().putBoolean(\"kill_$featureKey\", isKilled).apply()\n"
            "    }\n"
            "}\n"
            "\n"
            "// استخدام الـ Guard في واجهة المستخدم (Jetpack Compose):\n"
            "@Composable\n"
            "fun PaymentScreen(\n"
            "    killSwitchManager: KillSwitchManager,\n"
            "    onFallbackRequested: () -> Unit\n"
            ") {\n"
            "    val isPaymentKilled = remember { killSwitchManager.isFeatureKilled(\"instant_checkout\") }\n"
            "\n"
            "    if (isPaymentKilled) {\n"
            "        // عرض واجهة بديلة آمنة للمستخدم تمنع الانهيار أو استغلال الثغرة\n"
            "        ServiceUnavailableBanner(message = \"Instant checkout is temporarily under maintenance. Please use standard transfer.\")\n"
            "    } else {\n"
            "        StandardCheckoutFlow()\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Design operational kill switches by wrapping critical components in cached feature flag guards, propagating emergency toggles within seconds via high-priority FCM data pushes and CDN-cached configs, and automating shutoffs using alerting tripwires connected to crash and anomaly monitoring.",
        "best_answer": (
            "Designing remote kill switches addresses the fundamental reality that mobile apps cannot be patched instantly due to app store review latency:\n\n"
            "1. **Granular Component-Level Guards**:\n"
            "   - Wrap risky features (e.g. new biometric flows, experimental payment gateways, third-party advertising SDKs) inside explicit kill-switch checks. If a component is tripped, the UI gracefully falls back to an older stable flow or displays a friendly maintenance banner.\n\n"
            "2. **Fast-Propagation Delivery Channels**:\n"
            "   - Standard remote configs with 12-hour cache TTLs are inadequate for active incidents. Distribute emergency kill signals through high-priority silent FCM messages, coupled with a lightweight CDN-hosted JSON manifest (`status.example.com/kill-switches.json`) fetched on every app launch.\n\n"
            "3. **Zero-Latency Local Evaluation**:\n"
            "   - Persist kill-switch values in local storage so that evaluations are instant and synchronous on the main thread, preventing UI blocking during startup.\n\n"
            "4. **Automated Incident Tripwires**:\n"
            "   - Integrate crash monitoring webhooks with deployment tooling. If Crashlytics reports that a specific feature version is generating crash spikes (> 2% crash rate), automated pipelines toggle the remote kill switch to prevent widespread customer disruption."
        ),
        "deep_answer": (
            "From an operational reliability perspective, kill switches must be designed with defensive fail-safe postures:\n\n"
            "1. **Fail-Safe vs. Fail-Secure Posture**: Decide default behaviors per domain. For non-critical features (e.g. animations, recommendations), fail-safe by enabling the feature if config fetching fails. For high-risk financial or security flows (e.g. biometric bypass, one-click payment), adopt a **Fail-Secure** posture: if the remote health check cannot be verified and risk signals are ambiguous, disable the feature until connectivity is restored.\n\n"
            "2. **SDK Sandboxing & Emergency Disablement**: Third-party SDKs (analytics, tracking, ads) are a notorious source of startup crashes. Wrap third-party SDK initializations inside remote kill switches evaluated in `Application.onCreate`. If an external SDK causes widespread SIGSEGV native crashes, toggle the kill switch to skip SDK initialization entirely.\n\n"
            "3. **Audit Trails & Role-Based Access Control (RBAC)**: Toggling a production kill switch can impact millions of active users. Restrict kill switch toggles behind multi-party authorization (two-person rule) in the deployment control panel, and record immutable audit logs with timestamps and operator IDs."
        ),
        "follow_ups": [
            {
                "question": "What is the difference between a feature flag and a kill switch?",
                "answer": "Feature flags manage gradual rollouts and experiments with standard cache TTLs; kill switches are high-priority emergency overrides designed for instantaneous incident containment."
            },
            {
                "question": "Why should you avoid hardcoding a hard app-crash in response to a tripped kill switch?",
                "answer": "Hard crashes produce terrible user ratings, churn, and prevent the app from fetching newer configurations; graceful degradation or friendly maintenance screens preserve user trust."
            }
        ]
    },
    {
        "id": "SYS-18",
        "arabic_explanation": (
            "كيف تدير انحراف وتفاوت الإصدارات (Version Skew) بين إصدارات التطبيق القديمة في السوق وتحديثات الـ Backend الجديدة؟\n\n"
            "1. حقيقة الـ Version Skew في عالم الموبايل:\n   - على الويب: مجرد نشر كود الـ Frontend الجديد يُجبر جميع المستخدمين على استخدام أحدث إصدار عند عمل Refresh.\n   - في الموبايل: هناك مستخدمون ما زالوا يستخدمون إصدارات تم تنزيلها قبل 6 أشهر أو سنة كاملة! بعضهم لا يملك مساحة لتحديث التطبيق، وبعضهم ألغى التحديث التلقائي.\n   - **القاعدة الهندسية الأولى**: **الـ Backend يجب أن يدعم التوافقية العكسية (Backward Compatibility) لعدة إصدارات سابقة دائماً**.\n\n"
            "2. القواعد الذهبية لتطور الـ Backend APIs:\n   - **ممنوع حذف أو إعادة تسمية الحقول القديمة**: إذا أردت استبدال حقل `userName` بـ `fullName`، احتفظ بالحقلين معاً في الـ JSON حتى يتم إيقاف الإصدارات القديمة رسمياً.\n   - **الحقول الجديدة تكون اختيارية (Optional/Nullable)**: لا تجعل الحقول الجديدة إجبارية حتى لا تفشل الإصدارات القديمة.\n   - **نمط القارئ المتسامح (Tolerant Reader Pattern)**: تكوين مكتبات السيريالايزيشن في الموبايل (Moshi / Kotlinx Serialization) لتجاهل الحقول المجهولة (`ignoreUnknownKeys = true`).\n\n"
            "3. سياسة التحديث الإجباري والتدريجي (Force Update & Soft Update):\n   - إرجاع هيدر في استجابات الـ API مثل `X-Minimum-Supported-Version: 2.4.0`.\n   - إذا كان إصدار العميل أقل من الحد الأدنى، يعرض التطبيق شاشة **Force Update** تمنع الاستخدام وتوجه المستخدم لـ Google Play (باستخدام In-App Update API)."
        ),
        "practical_walkthrough": (
            "تنفيذ فحص إصدار التطبيق والتعامل مع التحديث الإجباري عبر In-App Updates أو شاشة الحظر:\n"
            "```kotlin\n"
            "class AppVersionInterceptor(\n"
            "    private val currentVersionCode: Long,\n"
            "    private val onForceUpdateRequired: () -> Unit\n"
            ") : Interceptor {\n"
            "    override fun intercept(chain: Interceptor.Chain): Response {\n"
            "        val request = chain.request().newBuilder()\n"
            "            // 1. إرسال إصدار التطبيق في كل طلب لتتبع الـ Telemetry من جهة السيرفر\n"
            "            .header(\"X-App-Version\", currentVersionCode.toString())\n"
            "            .header(\"X-Platform\", \"android\")\n"
            "            .build()\n"
            "\n"
            "        val response = chain.proceed(request)\n"
            "\n"
            "        // 2. إذا أعاد السيرفر رمز 426 Upgrade Required أو هيدر الحد الأدنى المدعوم:\n"
            "        val minSupported = response.header(\"X-Min-Supported-Version\")?.toLongOrNull() ?: 0L\n"
            "        if (response.code == 426 || (minSupported > currentVersionCode)) {\n"
            "            // تفعيل مسار التحديث الإجباري ومنع العمليات الحساسة\n"
            "            onForceUpdateRequired()\n"
            "        }\n"
            "\n"
            "        return response\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Support mobile version skew by enforcing strict backward compatibility on backends, using the Tolerant Reader pattern (ignoreUnknownKeys) on clients, appending client version headers to all requests, and managing end-of-life versions gracefully via HTTP 426 and Google Play In-App Updates.",
        "best_answer": (
            "Managing version skew is a defining challenge of mobile platform engineering, as hundreds of disparate app versions coexist indefinitely in the wild:\n\n"
            "1. **Backend Evolution Rules (Additive Only)**:\n"
            "   - Never remove existing JSON fields or alter data types in active API versions. Schema evolution must be strictly additive.\n   - When introducing newer data models, deprecate old fields with graceful sunset schedules (e.g. 12-month deprecation policy) while monitoring active version telemetry.\n\n"
            "2. **Tolerant Reader Configuration**:\n"
            "   - Configure client parsers (Kotlinx Serialization or Moshi) with `ignoreUnknownKeys = true`. When backends introduce new fields for newer releases, older clients parse payloads smoothly without deserialization exceptions.\n\n"
            "3. **Version Identification Headers**:\n"
            "   - Attach semantic client headers (`X-App-Version: 3.2.1`, `X-Build-Number: 450`) to every HTTP request. Backends use these headers for telemetry, routing, and phased contract migrations.\n\n"
            "4. **Graduated Update Strategy (Soft vs. Force Update)**:\n"
            "   - **Soft Update**: For non-breaking improvements, display a dismissible in-app update prompt using Google Play's `AppUpdateManager` (Flexible flow).\n   - **Force Update**: For breaking security changes or decommissioned APIs, the server responds with `HTTP 426 Upgrade Required`. The client presents an unskippable full-screen blocker routing the user directly to the Play Store."
        ),
        "deep_answer": (
            "From an enterprise API lifecycle perspective, managing version skew requires operational discipline across organizational boundaries:\n\n"
            "1. **URL vs. Header API Versioning**: Major architectural contract shifts require formal API versioning (e.g., `/v2/checkout` alongside `/v1/checkout`). Backends maintain adapter translation layers mapping deprecated `/v1` requests to new internal microservice schemas, allowing older apps to function until their active user share drops below target deprecation thresholds (e.g. < 0.2%).\n\n"
            "2. **Feature Flags as Contract Gateways**: When shipping client changes that depend on newly deployed backend features, protect client code with feature flags. Deploy the mobile code dormant, verify backend stability across multi-region clusters, and activate the mobile flag remotely only once backend coverage is 100% verified.\n\n"
            "3. **Automated Backward Compatibility CI Checks**: Run contract testing in backend CI against historical mobile DTO schemas. If a backend PR removes a field or alters a nullable constraint expected by any app version released within the last year, the backend CI build fails automatically."
        ),
        "follow_ups": [
            {
                "question": "What is Google Play In-App Update API Flexible vs Immediate flow?",
                "answer": "Flexible allows the user to continue using the app while the download occurs in the background; Immediate blocks the UI until the update completes and restarts the app."
            },
            {
                "question": "Why should enum values in API models always include an UNKNOWN fallback on the client?",
                "answer": "If the backend adds a new enum constant, older clients without an UNKNOWN fallback will crash during JSON deserialization."
            }
        ]
    },
    {
        "id": "SYS-19",
        "arabic_explanation": (
            "تطبيق يعمل عليه 20 فريقاً برمجياً ويستغرق وقت البناء (Build Time) حوالي 25 دقيقة. كيف تعيد تصميم ملكية الكود والتبعيات لتسريع التطوير؟\n\n"
            "1. تشخيص أسباب بطء البناء (Root Cause Analysis via Build Scans):\n   - **تشغيل Gradle Build Scan (`--scan`)**: لتحديد المراحل والـ Tasks الأكثر استهلاكاً للوقت.\n   - **المشاكل المعتادة**: موديول أحادي ضخم (`:app`)، تبعيات دائرية، تعطيل الـ Configuration Cache، كثرة كود الـ Annotation Processing (KAPT بدلاً من KSP)، وغياب الـ Remote Build Cache.\n\n"
            "2. إعادة الهيكلة المعمارية (Modular Redesign & Dependency Decoupling):\n   - **تفكيك الميزات إلى API و Implementation**:\n     * `:feature:profile:api` (خفيف، كود عام فقط).\n     * `:feature:profile:impl` (التنفيذ الفعلي، لا يعتمد عليه أحد).\n   - **كسر التبعيات المباشرة بين الميزات**: منع أي موديول Feature من الاعتماد على موديول Feature آخر، وتمرير الاتصال عبر الـ DI والـ Core modules.\n   - **إنشاء Sample Apps مستقلة لكل فريق**:\n     * فريق الـ Profile يعمل داخل موديول تطبيقي صغير `:feature:profile:sample`. هذا التطبيق يُبنى ويشتغل في 10 ثوانٍ فقط، مما ينقذ إنتاجية الفريق اليومية!\n\n"
            "3. تحسينات أدوات البناء والبنية التحتية (Build Infrastructure Optimization):\n   - الانتقال من KAPT إلى **KSP (Kotlin Symbol Processing)** لتسريع معالجة الـ Annotations بنسبة 2x.\n   - تفعيل **Gradle Configuration Cache** و **Build Cache** المشترك على شبكة الـ CI (Remote Build Cache).\n   - تحديد ملف `CODEOWNERS` لفرض ملكية واضحة للموديولات ومنع التعديلات العشوائية."
        ),
        "practical_walkthrough": (
            "هيكلة إعدادات Gradle باستخدام Convention Plugins و Sample Apps لتقليص زمن البناء:\n"
            "```text\n"
            "// هيكل الموديولات المصغر لفرق العمل المستقلة:\n"
            "├── build-logic/ (Convention plugins لإدارة إعدادات Gradle مركزياً)\n"
            "├── core/ (Modules منخفضة المستوى)\n"
            "│    ├── network/\n"
            "│    └── database/\n"
            "├── features/\n"
            "│    ├── checkout/\n"
            "│    │    ├── api/    (العقود العامة فقط: تترجم في ثوانٍ)\n"
            "│    │    ├── impl/   (التنفيذ الداخلي الخاص بالفريق)\n"
            "│    │    └── sample/ (تطبيق مستقل مصغر لبناء واختبار الـ Checkout فقط في 8 ثوانٍ!)\n"
            "└── app/ (التطبيق النهائي المجمع للإنتاج)\n"
            "```"
        ),
        "quick_answer": "Redesign build performance by decoupling features into isolated :api and :impl modules, providing dedicated lightweight sample apps for each team, migrating from KAPT to KSP, enabling Gradle configuration and remote build caching, and enforcing architectural boundaries via automated linters and CODEOWNERS.",
        "best_answer": (
            "Addressing a 25-minute build across 20 feature teams requires both architectural modularization and build toolchain optimization:\n\n"
            "1. **Architecture & Dependency Decoupling**:\n"
            "   - Decouple feature interdependencies using the **API/Implementation pattern** (`:feature:x:api` and `:feature:x:impl`). Modifying implementation code in one feature will not invalidate the build cache of dependent features.\n   - Eliminate the monolithic `:app` bottleneck. Provide each team with a dedicated, lightweight `:feature:x:sample` runner module. Feature engineers build and iterate within their sample app in under 10 seconds without compiling the remaining 19 domains.\n\n"
            "2. **Toolchain Modernization**:\n"
            "   - Replace legacy KAPT annotation processors with **KSP (Kotlin Symbol Processing)** for Room, Moshi, and Dagger/Hilt, reducing annotation processing overhead by 50%.\n   - Enable Gradle's **Configuration Cache** (`org.gradle.configuration-cache=true`) to bypass project configuration evaluation on incremental builds.\n\n"
            "3. **Distributed Remote Build Caching**:\n"
            "   - Deploy a remote Gradle Build Cache server on the corporate network and CI. Outputs compiled on CI or colleagues' machines are pulled as precompiled binaries rather than re-executed locally.\n\n"
            "4. **Organizational Governance**:\n"
            "   - Enforce directory-level ownership using GitHub `CODEOWNERS`, and integrate Konsist or ArchUnit tests into CI to block PRs that introduce forbidden cross-feature dependencies."
        ),
        "deep_answer": (
            "From a staff platform engineering perspective, managing developer velocity at this scale requires continuous telemetry:\n\n"
            "1. **Build Velocity Telemetry**: Instrument local developer and CI builds with Gradle Enterprise / Develocity. Monitor metrics across p50, p90, and p99 build times, task cache miss rates, and garbage collection pauses to identify pathological dependencies before they cascade.\n\n"
            "2. **Binary Dependency Substitution (Focus Mode)**: For engineers working on specific verticals, implement an internal Gradle plugin that substitutes source module dependencies (`project(\":core:network\")`) with pre-compiled AAR binaries published to an internal Artifactory cache on every main-branch merge. Engineers compile only their 2 active modules from source.\n\n"
            "3. **Non-Transitive R Classes**: Enable `android.nonTransitiveRClass=true` in `gradle.properties`. This ensures that each module's `R` class contains only its own resources rather than aggregating resource IDs from all upstream dependencies, preventing cascading recompilations when a string resource changes."
        ),
        "follow_ups": [
            {
                "question": "What is the benefit of android.nonTransitiveRClass=true?",
                "answer": "It prevents Gradle from copying upstream resource IDs into downstream R classes, drastically reducing recompilations when resources change."
            },
            {
                "question": "How does KSP achieve 2x faster performance than KAPT?",
                "answer": "KSP operates directly on Kotlin AST symbols without generating intermediate Java stubs, eliminating costly stub generation and javac execution."
            }
        ]
    },
    {
        "id": "SYS-20",
        "arabic_explanation": (
            "تم خصم وتفويض عملية دفع بنكية بنجاح، ولكن واجهة التطبيق واجهت انقطاعاً في الشبكة (Timeout) قبل استلام التأكيد. كيف تصمم آلية استعادة ومطابقة (Recovery & Reconciliation) تمنع السحب المزدوج؟\n\n"
            "1. طبيعة المشكلة (The In-Flight Network Drop Problem):\n   - المستخدم ضغط \"ادفع الآن\"، طلب الـ POST وصل للسيرفر، السيرفر خصم المبلغ من بطاقة المستخدم بنجاح، ولكن أثناء إرسال استجابة `200 OK` إلى الموبايل انقطعت شبكة الهاتف!\n   - واجهة التطبيق أظهرت خطأ \"انتهت مهلة الاتصال (Timeout)\".\n   - إذا ضغط المستخدم على زر الدفع مجدداً دون حماية، سيتم خصم المبلغ مرة ثانية!\n\n"
            "2. خطوات الاستعادة والمطابقة التلقائية (Reconciliation Protocol):\n   - **استخدام مفتاح عدم التكرار الثابت (Idempotency Key)**: كل معاملة ترتبط بـ UUID فريد يتم حفظه في قاعدة بيانات الهاتف المحلية (Room) قبل إرسال أول طلب.\n   - **منع تكرار طلب الدفع المباشر**: عند حدوث Timeout، **يُمنع منعاً باتاً إعادة إرسال طلب الدفع الأصلي فوراً**.\n   - **الاستعلام عن حالة المعاملة (Reconciliation Query)**: يقوم التطبيق بإرسال طلب استعلام آمن:\n     `GET /payments/reconcile?idempotency_key=<uuid>`.\n   - إذا كانت المعاملة قد تمت بنجاح على السيرفر، يعيد السيرفر تفاصيل الإيصال، فيقوم التطبيق بتحديث حالة الطلب إلى `SUCCESS` وعرض شاشة النجاح للمستخدم!\n   - إذا لم تصل المعاملة للسيرفر أصلاً، يمكن للتطبيق إعادة المحاولة بأمان باستخدام نفس مفتاح الـ Idempotency دون أي خوف من التكرار.\n\n"
            "3. المعالجة عند إعادة فتح التطبيق (App Restart Recovery):\n   - عند فتح التطبيق، يفحص الـ Repository جدول المعاملات المعلقة (`PENDING_RECONCILIATION`) ويقوم بمطابقتها في الخلفية مع السيرفر وتحديث الواجهة تلقائياً."
        ),
        "practical_walkthrough": (
            "تنفيذ دورة مطابقة المعاملات البنكية بعد الـ Timeout وحمايتها بمفتاح الـ Idempotency في Room:\n"
            "```kotlin\n"
            "class PaymentReconciliationManager @Inject constructor(\n"
            "    private val paymentDao: PaymentTransactionDao,\n"
            "    private val paymentApi: PaymentApiService\n"
            ") {\n"
            "    suspend fun resolveTimedOutPayment(orderId: String): PaymentUiState {\n"
            "        val record = paymentDao.getTransaction(orderId) ?: return PaymentUiState.Error(\"Transaction not found\")\n"
            "        \n"
            "        return try {\n"
            "            // 1. الاستعلام الآمن عن حالة المعاملة عبر مفتاح عدم التكرار\n"
            "            val reconciliationResponse = paymentApi.queryTransactionStatus(record.idempotencyKey)\n"
            "            \n"
            "            when (reconciliationResponse.status) {\n"
            "                \"AUTHORIZED\", \"CAPTURED\" -> {\n"
            "                    // تم الخصم بنجاح بالفعل على السيرفر! تحديث الحالة وعرض النجاح للمستخدم:\n"
            "                    paymentDao.updateStatus(orderId, TransactionStatus.COMPLETED)\n"
            "                    PaymentUiState.Success(reconciliationResponse.receiptId)\n"
            "                }\n"
            "                \"FAILED\" -> {\n"
            "                    paymentDao.updateStatus(orderId, TransactionStatus.FAILED)\n"
            "                    PaymentUiState.Failed(reconciliationResponse.errorMessage)\n"
            "                }\n"
            "                \"NOT_FOUND\" -> {\n"
            "                    // الطلب لم يصل للسيرفر أصلاً؛ الآن فقط يمكن إعادة المحاولة بأمان\n"
            "                    PaymentUiState.CanRetrySafely(record.idempotencyKey)\n"
            "                }\n"
            "                else -> PaymentUiState.Pending\n"
            "            }\n"
            "        } catch (e: Exception) {\n"
            "            // في حال استمرار انقطاع الشبكة: تظل المعاملة معلقة للمطابقة في الخلفية\n"
            "            PaymentUiState.NetworkUnavailable(canCheckLater = true)\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Never retry timed-out payments blindly. Persist a client-generated UUID idempotency key before dispatching charges. On timeout or app restart, initiate a reconciliation query (GET /payments/reconcile?key=uuid) to verify whether the backend authorized the charge, transitioning to success if captured, or retrying safely with the same key if not found.",
        "best_answer": (
            "When a payment request times out, the client cannot distinguish between a failure during request delivery versus a failure during response delivery. Recovering gracefully requires a strict reconciliation workflow:\n\n"
            "1. **Pre-Flight Local Persistence**:\n"
            "   - Before dispatching the payment request, insert an atomic transaction record into Room containing the order ID, a client-generated UUID `idempotencyKey`, and status `IN_FLIGHT`.\n\n"
            "2. **Handling Timeouts Without Blind Retries**:\n"
            "   - If the network drops or the socket times out, **do not replay the charge mutation**. Re-invoking charge mutations without idempotency guarantees creates duplicate charges.\n   - Transition local state to `PENDING_RECONCILIATION` and disable immediate retry buttons on the UI.\n\n"
            "3. **Idempotent Reconciliation Protocol**:\n"
            "   - Dispatch a read-only reconciliation query (`GET /payments/status?idempotency_key=<key>`).\n   - If the backend returns `CAPTURED` or `AUTHORIZED`, update local storage to `SUCCESS` and navigate to the order confirmation screen.\n   - If the backend returns `TRANSACTION_NOT_FOUND`, the original request never reached the payment gateway. The client can now safely retry the charge using the identical idempotency key.\n\n"
            "4. **Startup Reconciliation Hooks**:\n"
            "   - If the app crashed or was killed during timeout, check for unresolved `PENDING_RECONCILIATION` records on next launch, reconciliate them in the background, and notify the user via a banner."
        ),
        "deep_answer": (
            "From a distributed systems and fintech compliance perspective, client reconciliation must interface with server webhooks:\n\n"
            "1. **Server Webhook Authority**: The payment processor (e.g. Stripe/Adyen) notifies your backend asynchronously via cryptographic webhooks (`payment_intent.succeeded`). Even if the mobile device stays offline for hours, the backend marks the order paid and sends a push notification.\n\n"
            "2. **Polling Backoff & Timeout Windows**: Implement a polling state machine with exponential backoff for the reconciliation endpoint (polling at 2s, 4s, 8s intervals, capping at 30s). If reconciliation remains unresolved after 30 seconds, transition the UI to an asynchronous pending screen: 'Your payment is being verified with your bank. We will notify you shortly.'\n\n"
            "3. **Customer Support Idempotency Traceability**: Display the idempotency key or a short human-readable transaction reference on the pending UI screen. If customer support is contacted, agents can query the payment gateway logs instantly using that exact key."
        ),
        "follow_ups": [
            {
                "question": "Why is GET /payments/status safe to retry indefinitely?",
                "answer": "GET requests are inherently idempotent and read-only; polling status cannot alter server balances or duplicate charges."
            },
            {
                "question": "What is the role of payment gateway webhooks in transaction reconciliation?",
                "answer": "Webhooks provide authoritative, out-of-band confirmation directly from payment processors to backend servers, independent of mobile network reliability."
            }
        ]
    },
    {
        "id": "SYS-21",
        "arabic_explanation": (
            "كيف تصمم شاشة رئيسية (Home Screen) تعتمد على 3 خدمات مستقلة وتدعم الفشل الجزئي (Partial Failure) دون تعطل الشاشة بالكامل؟\n\n"
            "1. خطأ التصميم الكارثي (The All-or-Nothing Anti-Pattern):\n   - استخدام `zip` أو `awaitAll` لدمج استجابات الخدمات الثلاث (مثلاً: Stories API, Feed API, Recommendations API).\n   - **المشكلة**: إذا فشلت خدمة التوصيات (Recommendations) أو استغرقت 10 ثوانٍ، فإن الشاشة بالكامل تفشل وتعرض شاشة بيضاء أو رسالة خطأ، وتمنع المستخدم من رؤية الـ Feed والـ Stories الأساسية!\n\n"
            "2. المعمارية السليمة: العزل التام والتراجع المتدرج (Graceful Degradation):\n   - **استقلالية الجلب (Independent Concurrent Fetching)**: جلب بيانات كل خدمة في Coroutine مستقل مع عزل الأخطاء عبر `runCatching`.\n   - **تمثيل الحالة المنفصل (Independent State Streams)**: كل ميزة تمتلك حالة خاصة بها:\n     `storiesState: StateFlow<SectionState<List<Story>>>`,\n     `feedState: StateFlow<SectionState<List<Post>>>`,\n     `recommendationsState: StateFlow<SectionState<List<Recommendation>>>`.\n   - **التراجع للكاش المحلي (Cache Fallback)**: إذا فشلت خدمة الـ Feed عبر الإنترنت، يتم عرض آخر بيانات مخزنة محلياً من الـ Room DB مع علامة صغيرة توضح أن البيانات غير محدثة.\n   - **واجهة مستخدم مرنة في Compose**: تعرض الـ Stories والـ Feed بشكل طبيعي، بينما تعرض خانة الـ Recommendations زراً صغيراً لإعادة المحاولة (Inline Retry) أو تخفي القسم بهدوء دون إفساد تجربة المستخدم."
        ),
        "practical_walkthrough": (
            "تنفيذ تجميع مرن ومقاوم للفشل الجزئي لثلاث خدمات مستقلة في ViewModel و Compose:\n"
            "```kotlin\n"
            "sealed interface SectionState<out T> {\n"
            "    object Loading : SectionState<Nothing>\n"
            "    data class Success<T>(val data: T) : SectionState<T>\n"
            "    data class Error(val message: String, val cachedFallback: Boolean = false) : SectionState<Nothing>\n"
            "}\n"
            "\n"
            "data class HomeUiState(\n"
            "    val banners: SectionState<List<Banner>> = SectionState.Loading,\n"
            "    val feedItems: SectionState<List<FeedItem>> = SectionState.Loading,\n"
            "    val recommendations: SectionState<List<Recommendation>> = SectionState.Loading\n"
            ")\n"
            "\n"
            "class HomeViewModel @Inject constructor(\n"
            "    private val bannerRepo: BannerRepository,\n"
            "    private val feedRepo: FeedRepository,\n"
            "    private val recsRepo: RecommendationsRepository\n"
            ") : ViewModel() {\n"
            "    private val _uiState = MutableStateFlow(HomeUiState())\n"
            "    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()\n"
            "\n"
            "    fun loadHomeScreenData() {\n"
            "        // 1. جلب Banners بشكل مستقل مع عزل الخطأ\n"
            "        viewModelScope.launch {\n"
            "            bannerRepo.getBanners()\n"
            "                .onSuccess { data -> _uiState.update { it.copy(banners = SectionState.Success(data)) } }\n"
            "                .onFailure { _uiState.update { it.copy(banners = SectionState.Error(\"Could not load banners\")) } }\n"
            "        }\n"
            "\n"
            "        // 2. جلب الـ Feed بشكل مستقل\n"
            "        viewModelScope.launch {\n"
            "            feedRepo.getFeedStream().collect { feed ->\n"
            "                _uiState.update { it.copy(feedItems = SectionState.Success(feed)) }\n"
            "            }\n"
            "        }\n"
            "\n"
            "        // 3. جلب الـ Recommendations بشكل مستقل؛ الفشل هنا لا يؤثر إطلاقاً على الـ Feed أو الـ Banners!\n"
            "        viewModelScope.launch {\n"
            "            recsRepo.getRecommendations()\n"
            "                .onSuccess { recs -> _uiState.update { it.copy(recommendations = SectionState.Success(recs)) } }\n"
            "                .onFailure { _uiState.update { it.copy(recommendations = SectionState.Error(\"Recommendations unavailable\")) } }\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Design aggregate screens for partial failure by fetching independent services concurrently using isolated coroutine scopes and runCatching blocks. Represent sections with independent state streams in a unified UI state, fall back to local cached data where available, and render inline section retries without blocking or failing the entire screen.",
        "best_answer": (
            "Aggregating multiple microservices into a single mobile dashboard requires defensive concurrency and resilient UI state composition:\n\n"
            "1. **Avoid All-or-Nothing Composition**:\n"
            "   - Combining calls via `zip`, `combine` with synchronous throws, or `awaitAll` creates an all-or-nothing anti-pattern. If a non-essential service (e.g. Recommendations) throws a 500 or times out, the entire screen fails.\n\n"
            "2. **Independent Section Concurrency**:\n"
            "   - Launch three independent coroutine jobs within `viewModelScope` using `runCatching` or supervisory scopes. If the Recommendations service fails, its exception is caught in isolation, allowing the Feed and Hero Banners to load and render immediately.\n\n"
            "3. **Modular State Modeling**:\n"
            "   - Model the overall screen state as an aggregate data class holding individual `SectionState<T>` wrappers (`Loading`, `Success`, `Error`). Compose renders each section according to its discrete state.\n\n"
            "4. **Graceful UI Degradation & Cache Fallbacks**:\n"
            "   - If a service fails, check Room persistence for cached records. If cached data exists, render it with a subtle 'Offline' chip. If no cache exists, render an inline retry placeholder or cleanly collapse the section without breaking the parent layout."
        ),
        "deep_answer": (
            "From a staff-level systems perspective, partial failure resilience extends into network protocol design and backend orchestration:\n\n"
            "1. **Backend-for-Frontend (BFF) vs. Client Aggregation**: In enterprise architectures, mobile clients should ideally query a single mobile BFF gateway. The BFF aggregates the 3 microservices concurrently on high-speed datacenter backbones. If recommendations time out within 150ms, the BFF returns a partial JSON payload containing banners and feed items along with a partial-error metadata flag, saving mobile battery and round-trips.\n\n"
            "2. **Independent Section Pull-to-Refresh**: When the user performs a pull-to-refresh gesture, trigger refresh jobs across all three sections concurrently. Keep already-rendered cached content on screen while refreshing, transitioning sections to loading indicators only if no data was previously visible.\n\n"
            "3. **Targeted Telemetry & Alerting**: Log individual endpoint failure rates. If Recommendations fail for 15% of sessions while Core Feed succeeds, telemetry surfaces microservice-specific degradation rather than generic app-level crash alarms."
        ),
        "follow_ups": [
            {
                "question": "What is SupervisorJob and why is it useful when fetching multiple independent services?",
                "answer": "A SupervisorJob ensures that failure in one child coroutine does not automatically cancel its sibling coroutines or the parent scope."
            },
            {
                "question": "How should Compose handle an empty state versus an error state in a lazy list section?",
                "answer": "An empty state displays a friendly empty graphic or collapses gracefully; an error state provides an inline error message with a dedicated section retry button."
            }
        ]
    },
    {
        "id": "SYS-22",
        "arabic_explanation": (
            "مفتاح ميزة (Feature Flag) تم تفعيله بالخطأ ففتح مساراً يحتوي على ثغرة أمنية حرجة. كيف تحتوي الأثر (Contain the Impact) هندسياً وعملياتياً؟\n\n"
            "1. خطة الطوارئ لاحتواء الكارثة (Emergency Containment Playbook):\n   - **الخطوة 0: الدفاع السيرفري الفوري (Backend & Gateway First)**: لا تنتظر تطبيق الموبايل! أول وأسرع إجراء هو **إغلاق الـ Endpoint المصابة أو فرض قواعد فحص صارمة على مستوى الـ API Gateway / WAF** فوراً. حتى لو كان التطبيق يرسل الطلب المصاب، السيرفر سيرفضه ويعيد `403 Forbidden`.\n   - **الخطوة 1: قلب مفتاح الـ Feature Flag عن بُعد (Remote Kill Switch)**: تحويل قيمة الـ Flag إلى `false` في لوحة تحكم الـ Remote Config (Firebase / LaunchDarkly) مع إجبار تفريغ الكاش على الـ CDN.\n   - **الخطوة 2: إرسال إشعار تفريغ صامت (Silent Push Invalidation)**: إرسال High-Priority FCM Push لجميع الأجهزة النشطة لإجبارها على تحديث الـ Config فوراً ومسح الـ In-Memory Cache.\n   - **الخطوة 3: إبطال الجلسات المخترقة (Session Revocation)**: إذا كانت الثغرة تسمح بتسريب توكنز أو تجاوز صلاحيات، يقوم السيرفر بقطع جميع الجلسات التي مرت عبر هذا المسار وإجبار أصحابها على إعادة تسجيل الدخول.\n\n"
            "2. التحقيق الجنائي والوقاية المستقبلية (Post-Mortem & Prevention):\n   - إجراء Post-Mortem هندسي بدون لوم (Blameless Post-Mortem).\n   - منع تفعيل الـ Flags الحساسة أمنياً بدون موافقة ثنائية (Four-Eyes Principle / Peer Approval) في لوحة التحكم.\n   - ربط فحوصات الأمان الآلية في CI لمنع إطلاق أي كود يتجاوز الـ Auth حتى لو تم تفعيل الـ Flag."
        ),
        "practical_walkthrough": (
            "تصميم نظام استجابة طوارئ للـ Feature Flags مع إمكانية الإبطال الفوري عبر Silent Push:\n"
            "```kotlin\n"
            "class EmergencyFlagPushReceiver : FirebaseMessagingService() {\n"
            "    @Inject lateinit var featureFlagManager: FeatureFlagManager\n"
            "    @Inject lateinit var sessionManager: SessionManager\n"
            "\n"
            "    override fun onMessageReceived(remoteMessage: RemoteMessage) {\n"
            "        // 1. استقبال أمر طوارئ مشفر وموقع من السيرفر\n"
            "        val action = remoteMessage.data[\"action\"]\n"
            "        val targetFlag = remoteMessage.data[\"flag_key\"]\n"
            "\n"
            "        if (action == \"EMERGENCY_KILL_FLAG\" && targetFlag != null) {\n"
            "            // 2. إلغاء تفعيل الميزة فوراً في الـ Storage والـ Memory:\n"
            "            featureFlagManager.forceOverrideFlag(targetFlag, value = false)\n"
            "            \n"
            "            // 3. إذا كان المسار يمس أمان الجلسة: مسح التوكنز وتوجيه المستخدم لتسجيل الدخول\n"
            "            if (remoteMessage.data[\"revoke_session\"] == \"true\") {\n"
            "                sessionManager.forceLogoutDueToSecurityIncident()\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Contain a compromised feature flag by immediately blocking the vulnerable path at the backend API Gateway, toggling the remote flag to FALSE across CDNs, dispatching high-priority silent FCM pushes to force local cache invalidation, revoking impacted sessions server-side, and enforcing peer review rules on flag changes.",
        "best_answer": (
            "Containing an accidental rollout of a security-sensitive code path requires executing a prioritized, multi-tiered incident response playbook:\n\n"
            "1. **Immediate Server-Side Gateway Mitigation (Minutes 0–5)**:\n"
            "   - Never rely on mobile clients to patch themselves. Mobile clients may be offline, backgrounded, or caching stale configs. The immediate containment step is blocking or rate-limiting the vulnerable endpoint at the backend API Gateway / WAF level, rejecting compromised requests with `403 Forbidden`.\n\n"
            "2. **Remote Kill Switch Flip (Minutes 5–10)**:\n"
            "   - Set the flag value to `false` in the remote configuration provider (LaunchDarkly, Firebase Remote Config). Purge edge CDN caches to ensure subsequent client config fetches retrieve the disabled state.\n\n"
            "3. **High-Priority Silent Invalidation (Minutes 10–20)**:\n"
            "   - Dispatch high-priority silent FCM push messages to active mobile clients. The client's background service immediately clears in-memory flag caches, rewrites persistent storage, and terminates compromised views.\n\n"
            "4. **Session Invalidation & Audit**:\n"
            "   - If the flaw exposed unauthorized privilege escalation or data leakage, the backend identifies users who traversed the endpoint, revokes their active refresh tokens, and prompts for credential resets."
        ),
        "deep_answer": (
            "From an engineering governance and post-mortem perspective, systemic controls must prevent recurrence:\n\n"
            "1. **The Four-Eyes Principle for Sensitive Flags**: Classify feature flags by risk tier. Operational or UI flags can be flipped by individual engineers; security, auth, and financial flags mandate two-person cryptographic sign-off (Four-Eyes Principle) in release management consoles before propagation.\n\n"
            "2. **Default-Deny In-Code Security Assertions**: Client code protected by feature flags must still adhere to defense-in-depth. If a flag enables a new payment feature, the underlying code must still enforce token validation, biometric challenges, and server nonces. A feature flag should only toggle UI exposure, never disable core cryptographic checks.\n\n"
            "3. **Canary Phased Ring Deployment**: Enforce mandatory phased rollout rings: Internal Dogfood (1%) -> Beta (5%) -> General Canary (10%) with automated 24-hour observation windows, preventing accidental 100% blast-radius rollouts."
        ),
        "follow_ups": [
            {
                "question": "Why is backend gateway mitigation prioritized over flipping the client feature flag?",
                "answer": "Backend gateway changes take effect globally within seconds, whereas client flag updates depend on network polling, app restarts, and cached local configs."
            },
            {
                "question": "What is a Blameless Post-Mortem?",
                "answer": "An incident review focused on identifying systemic process and tooling failures rather than punishing individuals, designing safeguards to prevent recurrence."
            }
        ]
    },
    {
        "id": "SYS-23",
        "arabic_explanation": (
            "كيف تهاجر تطبيق أندرويد ضخم وقديم مبني بـ XML View System إلى Jetpack Compose بشكل تدريجي وآمن؟\n\n"
            "1. استراتيجية الهجرة الواقعية (Pragmatic Migration Strategy):\n   - **قاعدة ذهبية**: تجنب فكرة \"إعادة كتابة التطبيق بالكامل من الصفر (Complete Rewrite)\"! إعادة الكتابة الكاملة تستغرق سنوات وتوقف تطوير الميزات وتخلق أخطاء جديدة غير متوقعة.\n   - **الهجرة التدريجية (Incremental Migration)** هي الحل الصحيح والمعتمد في الشركات الكبرى (مثل Google, Twitter, Airbnb).\n\n"
            "2. مسارات الهجرة التدريجية (Bottom-Up vs. Top-Down):\n   - **Bottom-Up (من الأسفل للأعلى - الموصى به للميزات القائمة)**:\n     * البدء بالمكونات الصغيرة المنعزلة (Leaf Views مثل الأزرار، الكروت، وقوائم الـ Dialogs) باستخدام `ComposeView` داخل ملفات الـ XML القديمة.\n     * بعد تحويل عناصر القوائم، يتم استبدال `RecyclerView` بـ `LazyColumn`.\n   - **Top-Down (من الأعلى للأسفل - للميزات الجديدة بالكامل)**:\n     * أي شاشة جديدة تُبنى بنسبة 100% بـ Jetpack Compose داخل `ComponentActivity.setContent`.\n\n"
            "3. جسر نظام التصميم (Design System Bridging):\n   - توحيد الـ Themes: ربط ألوان وخطوط وأشكال الـ XML القديمة (`Theme.MaterialComponents`) برموز الـ Compose `MaterialTheme` حتى تبدو شاشات الـ XML وشاشات الـ Compose متطابقة تماماً للمستخدم.\n\n"
            "4. التعايش وإدارة دورة الحياة (Interoperability & Lifecycle):\n   - استخدام `ViewCompositionStrategy.DisposeOnViewTreeLifecycleDestroyed` لمنع تسريب الذاكرة عند استخدام Compose داخل Fragments."
        ),
        "practical_walkthrough": (
            "دمج Compose داخل Fragment قديم يعتمد على XML وتطبيق استراتيجية التخلص الآمن من الذاكرة:\n"
            "```kotlin\n"
            "class LegacyProfileFragment : Fragment(R.layout.fragment_legacy_profile) {\n"
            "    private val viewModel: ProfileViewModel by viewModels()\n"
            "\n"
            "    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {\n"
            "        super.onViewCreated(view, savedInstanceState)\n"
            "        \n"
            "        // 1. العثور على الـ ComposeView المدمج داخل ملف الـ XML القديم:\n"
            "        val composeView = view.findViewById<ComposeView>(R.id.compose_header_container)\n"
            "        \n"
            "        composeView.apply {\n"
            "            // 2. إلزامي: ضبط استراتيجية التخلص من الـ Composition لمنع تسريب الذاكرة مع دورة حياة الـ Fragment:\n"
            "            setViewCompositionStrategy(ViewCompositionStrategy.DisposeOnViewTreeLifecycleDestroyed)\n"
            "            \n"
            "            setContent {\n"
            "                // 3. تغليف الـ Composable بنظام الـ Theme الموحد:\n"
            "                AppTheme {\n"
            "                    val profileState by viewModel.uiState.collectAsStateWithLifecycle()\n"
            "                    ProfileHeaderComponent(\n"
            "                        state = profileState,\n"
            "                        onEditClicked = { navigateToEditProfile() }\n"
            "                    )\n"
            "                }\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Migrate legacy XML to Jetpack Compose incrementally: build new screens entirely in Compose, migrate existing screens bottom-up by embedding ComposeView into XML layouts with DisposeOnViewTreeLifecycleDestroyed, bridge themes via MaterialTheme wrappers, and replace RecyclerViews with LazyColumns gradually.",
        "best_answer": (
            "Migrating an enterprise Android app from the View system to Jetpack Compose requires an incremental coexistence strategy rather than a risky all-at-once rewrite:\n\n"
            "1. **Pragmatic Migration Direction**:\n"
            "   - **Top-Down for New Features**: Mandate that all net-new screens are written exclusively in 100% Jetpack Compose using `ComponentActivity.setContent { }`.\n   - **Bottom-Up for Existing Screens**: Convert leaf components (buttons, custom cards, headers) first. Embed them inside legacy XML layouts using `ComposeView`.\n\n"
            "2. **Lifecycle & Memory Management in Fragments**:\n"
            "   - In Android Fragments, the Fragment View lifecycle is distinct from the Fragment instance lifecycle. When using `ComposeView` in Fragments, always set `setViewCompositionStrategy(ViewCompositionStrategy.DisposeOnViewTreeLifecycleDestroyed)`. Failing to do so leaks View compositions across fragment backstack transactions.\n\n"
            "3. **Design System & Theme Bridging**:\n"
            "   - Maintain visual parity by bridging your existing XML theme attributes into Compose `MaterialTheme` tokens (using `accompanist/themeadapter-material` or custom mappers). This ensures that XML views and Compose widgets share identical colors, shapes, and typography during migration.\n\n"
            "4. **RecyclerView to LazyColumn Transition**:\n"
            "   - As individual `ViewHolder` items are migrated to Composables, avoid leaving hundreds of tiny `ComposeView` wrappers inside a `RecyclerView` due to layout measurement overhead. Once item viewholders are composed, replace the parent `RecyclerView` with a native Compose `LazyColumn`."
        ),
        "deep_answer": (
            "From an architectural governance and performance perspective, managing hybrid View/Compose runtimes requires strict profiling:\n\n"
            "1. **Interoperability Layout Overhead**: Nesting Views inside Compose via `AndroidView` or nesting Compose inside Views via `ComposeView` incurs measurement overhead. Hybrid lists with `ComposeView` inside `RecyclerView` can drop frames during fast flings unless items use fixed height modifiers or enable Baseline Profiles.\n\n"
            "2. **Baseline Profiles for Startup & Jank**: Jetpack Compose relies on runtime compilation (AOT/JIT). Uncompiled Compose code can cause significant jank on first run. Generate and bundle **Baseline Profiles** using Macrobenchmark to pre-compile critical Composable paths during app installation, restoring 60fps scrolling.\n\n"
            "3. **State Management Bridging**: Legacy ViewModels exposing `LiveData` should be converted to reactive `StateFlow`. In Compose, observe them via `collectAsStateWithLifecycle()` to automatically halt collection when the host Activity/Fragment is backgrounded."
        ),
        "follow_ups": [
            {
                "question": "Why is DisposeOnViewTreeLifecycleDestroyed required in Fragments?",
                "answer": "Because a Fragment's view can be destroyed while the Fragment instance remains in memory; this strategy disposes the composition when the view hierarchy is detached, preventing memory leaks."
            },
            {
                "question": "How do you embed a legacy custom Android View inside a Jetpack Compose screen?",
                "answer": "Using the AndroidView composable: AndroidView(factory = { context -> LegacyCustomView(context) }, update = { view -> view.setData(...) })."
            }
        ]
    },
    {
        "id": "SYS-24",
        "arabic_explanation": (
            "كيف تصمم تطبيقاً يعمل بكفاءة تحت ظروف الاتصال الضعيف جداً (Poor Connectivity) والانقطاع المفاجئ للطاقة والبطارية (Intermittent Power Loss)؟\n\n"
            "1. تحديات البيئات القاسية (Harsh Constraints / Emerging Markets):\n   - شبكات 2G/3G متقطعة، زمن استجابة عالي (Latency > 2000ms)، باقات بيانات مكلفة ومحدودة.\n   - بطاريات هواتف رديئة، وإمكانية إغلاق الهاتف فجأة في أي ثانية بسبب نفاد الشحن.\n\n"
            "2. تقليص استهلاك الشبكة (Data Thrift & Bandwidth Optimization):\n   - **ضغط البيانات بصيغ حديثة**: استخدام **Protocol Buffers (Protobuf)** أو GZIP JSON لتقليص حجم البايتات بنسبة 60-80% مقارنة بالنصوص العادية.\n   - **تحسين الصور**: استخدام صيغ WebP أو AVIF، وجلب صور مصغرة جداً (Thumbnails) تناسب أبعاد الشاشة فقط، ومنع تحميل الصور عالية الدقة إلا على شبكات Wi-Fi.\n   - **Delta Sync**: جلب البيانات المعدلة فقط منذ آخر فحص بدلاً من إعادة تنزيل القوائم كاملة.\n\n"
            "3. الحماية ضد انقطاع الطاقة المفاجئ (Power Loss & Crash Resilience):\n   - **المعاملات الذرية في SQLite (Atomic Transactions & WAL Mode)**: استخدام Room داخل `database.withTransaction { ... }` وتفعيل وضع Write-Ahead Logging (WAL). هذا يضمن أنه لو انطفأ الهاتف أثناء الكتابة، لن يتلف ملف قاعدة البيانات أبداً.\n   - **جدولة المهام الموفرة للطاقة عبر WorkManager**:\n     * وضع قيود صارمة على مهام الخلفية: `setRequiresBatteryNotLow(true)` و `setRequiresCharging(true)` لضمان عدم استنزاف طاقة المستخدم عند قرب نفاد البطارية."
        ),
        "practical_walkthrough": (
            "تطبيق إعدادات توفير البيانات وحماية قاعدة البيانات من الانقطاع المفاجئ للطاقة:\n"
            "```kotlin\n"
            "// 1. إعدادات Room Database محمية بـ WAL Mode لمنع تلف الملفات عند انطفاء الهاتف:\n"
            "@Database(entities = [TransactionEntity::class], version = 1)\n"
            "abstract class ResilientDatabase : RoomDatabase() {\n"
            "    companion object {\n"
            "        fun create(context: Context): ResilientDatabase {\n"
            "            return Room.databaseBuilder(context, ResilientDatabase::class.java, \"resilient.db\")\n"
            "                .setJournalMode(JournalMode.WRITE_AHEAD_LOGGING) // حماية فائقة ضد انقطاع الطاقة المفاجئ\n"
            "                .build()\n"
            "        }\n"
            "    }\n"
            "}\n"
            "\n"
            "// 2. جدولة مزامنة البيانات الكبيرة مع مراعاة حالة البطارية والشبكة:\n"
            "fun scheduleBatteryAwareSync(workManager: WorkManager) {\n"
            "    val constraints = Constraints.Builder()\n"
            "        .setRequiredNetworkType(NetworkType.UNMETERED) // مزامنة البيانات الضخمة فقط على Wi-Fi\n"
            "        .setRequiresBatteryNotLow(true)               // منع التشغيل إذا كانت البطارية منخفضة (< 15%)\n"
            "        .setRequiresCharging(false)\n"
            "        .build()\n"
            "\n"
            "    val syncWork = PeriodicWorkRequestBuilder<HeavySyncWorker>(6, TimeUnit.HOURS)\n"
            "        .setConstraints(constraints)\n"
            "        .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 15, TimeUnit.MINUTES)\n"
            "        .build()\n"
            "\n"
            "    workManager.enqueueUniquePeriodicWork(\"heavy_sync\", ExistingPeriodicWorkPolicy.KEEP, syncWork)\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Design for extreme constraints using compact binary payloads (Protobuf), WebP image compression, and local-first delta sync. Guard against sudden power loss using SQLite Write-Ahead Logging in atomic transactions, and defer heavy synchronization to Wi-Fi and healthy battery states via WorkManager constraints.",
        "best_answer": (
            "Designing for poor connectivity and sudden power loss treats resource scarcity as the default operating environment:\n\n"
            "1. **Bandwidth Thrift & Binary Encoding**:\n"
            "   - Replace verbose JSON payloads with Protocol Buffers (gRPC/Protobuf) or enforce HTTP GZIP/Brotli compression, reducing network payload size by up to 70%.\n   - Downsample media server-side to match the exact physical display density. Serve modern image formats (WebP or AVIF), deferring high-resolution asset downloads until unmetered Wi-Fi is detected.\n\n"
            "2. **Resilience Against Sudden Power Loss**:\n"
            "   - Budget devices frequently experience sudden shutdowns due to degraded batteries under load. Prevent SQLite database corruption by enabling **Write-Ahead Logging (WAL)** mode in Room.\n   - Execute multi-table writes strictly inside atomic `database.withTransaction { }` blocks. If power drops mid-write, SQLite rolls back to the last consistent checkpoint on reboot without corrupting database pages.\n\n"
            "3. **Battery-Aware Scheduling via WorkManager**:\n"
            "   - Schedule background data syncs with explicit hardware constraints: `.setRequiresBatteryNotLow(true)` and `.setRequiredNetworkType(NetworkType.CONNECTED)`. This prevents the application from waking up the CPU when battery levels drop below 15%."
        ),
        "deep_answer": (
            "From a low-level platform architecture perspective, intermittent connectivity requires intelligent connection management:\n\n"
            "1. **Adaptive Network Quality Telemetry**: Monitor cellular connection quality using Android's `ConnectivityManager.NetworkCallback` and bandwidth meters. When throughput drops below 50 kbps (2G/Edge), switch the app dynamically into 'Data Saver Mode': disable auto-playing videos, suppress decorative graphics, and request low-bandwidth text payloads from the backend.\n\n"
            "2. **Atomic Disk File Operations**: When saving downloaded files or JSON caches to disk, never write directly to the target file path. Write data to a temporary file (`temp_file.tmp`) and atomically rename it using `File.renameTo()` or `AtomicFile`. If power cuts out mid-write, the original file remains uncorrupted.\n\n"
            "3. **Aggressive Offline Queuing (The Outbox Pattern)**: Queue all user actions in persistent SQLite tables. Users in the field can continue creating invoices, taking notes, or logging deliveries offline with 100% responsiveness, confident that the synchronization engine will replay records deterministically when cellular coverage returns."
        ),
        "follow_ups": [
            {
                "question": "What is the benefit of using Android's AtomicFile helper class?",
                "answer": "AtomicFile writes data to a temporary file and performs an atomic rename, ensuring that sudden process death or power loss never leaves a corrupted, half-written file on disk."
            },
            {
                "question": "Why is Write-Ahead Logging (WAL) mode safer during sudden power loss?",
                "answer": "WAL appends modifications to a separate log file without modifying original database pages directly, making recovery trivial if power cuts before a checkpoint."
            }
        ]
    }
]


def update_sys_data() -> None:
    data = []
    if DATA_FILE.exists():
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))

    existing_map = {item["id"]: item for item in data}
    for item in SYS_17_24:
        existing_map[item["id"]] = item

    updated = [existing_map[k] for k in sorted(existing_map.keys())]
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(updated, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {DATA_FILE} with questions SYS-17 to SYS-24. Total questions: {len(updated)}")


if __name__ == "__main__":
    update_sys_data()
