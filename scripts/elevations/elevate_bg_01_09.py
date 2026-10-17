#!/usr/bin/env python3
"""Elevate BG-01 through BG-09 for bilingual parity and senior spoken answers."""
from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import elevation_engine as ee

TOPIC_AR = "المهام الخلفية و WorkManager وقيود النظام"
REVIEWED_DATE_AR = "تمت المراجعة الفنية استناداً إلى توثيق أندرويد الرسمي في 2026-10-14."

DATA = {}

# ==========================================
# BG-01: Coroutine vs WorkManager vs Foreground Service vs AlarmManager
# ==========================================
DATA["BG-01"] = {
    "concept_en": """Selecting the appropriate background execution mechanism in Android hinges on two primary architectural criteria: whether the work is ephemeral or durable, and whether execution requires user-perceived ongoing operations or exact clock timing. Kotlin coroutines running in viewModelScope or lifecycleScope manage immediate in-process tasks that cancel naturally when the user navigates away or the process terminates. WorkManager is the platform standard for persistent, deferrable background execution, persisting job metadata in an internal SQLite database to guarantee execution across process death and device reboots under system constraints. Foreground Services are strictly reserved for operations the user actively perceives and expects to continue uninterrupted, mandating an ongoing system notification and explicit runtime types (such as mediaPlayback or location). AlarmManager is intended exclusively for clock-exact, user-facing triggers like alarms and calendar reminders.""",
    "walkthrough_en": """Selecting the right background execution tool in practice:
```kotlin
// 1. Coroutine: Ephemeral in-process work tied to screen lifecycle
class ProductDetailsViewModel(private val api: ProductApi) : ViewModel() {
    fun loadDetails(productId: String) {
        viewModelScope.launch { // Cancels automatically when screen is popped
            _uiState.value = api.fetchDetails(productId)
        }
    }
}

// 2. WorkManager: Durable background work surviving process death and reboots
fun schedulePhotoUpload(context: Context, photoUri: Uri) {
    val request = OneTimeWorkRequestBuilder<UploadPhotoWorker>()
        .setConstraints(Constraints.Builder().setRequiredNetworkType(NetworkType.CONNECTED).build())
        .setInputData(workDataOf("uri" to photoUri.toString()))
        .build()
    WorkManager.getInstance(context).enqueueUniqueWork("upload_photo", ExistingWorkPolicy.KEEP, request)
}

// 3. AlarmManager: Clock-exact user reminder waking the device from idle
fun scheduleMorningAlarm(context: Context, triggerEpochMs: Long, pendingIntent: PendingIntent) {
    val alarmManager = context.getSystemService(AlarmManager::class.java)
    alarmManager.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, triggerEpochMs, pendingIntent)
}
```""",
    "short_en": """Use coroutines in viewModelScope for immediate in-process tasks tied directly to screen lifecycles. Use WorkManager for persistent, deferrable background execution that must survive process death and device reboots, such as offline syncing and analytics uploads. Use Foreground Services only for long-running operations the user actively perceives with a persistent notification like audio playback or navigation. Use AlarmManager strictly for clock-exact, time-critical user alarms, never for routine background data polling.""",
    "structured_en": """Selecting the appropriate background execution mechanism in Android requires evaluating task durability, user awareness, and execution timing precision.
Kotlin coroutines operating within viewModelScope or lifecycleScope manage immediate, in-process asynchronous tasks. When the user leaves the screen or the operating system reclaims the host process, these coroutines cancel cooperatively. This makes them ideal for fetching screen data, debouncing queries, and running presentation animations.
WorkManager serves as the official platform standard for persistent, deferrable background work. It guarantees completion even if the application process dies or the device reboots by persisting job metadata inside an internal SQLite database and delegating execution to the platform JobScheduler. WorkManager is essential for offline outbox synchronization, batch uploads, and database housekeeping under network and battery constraints.
Foreground Services are reserved strictly for long-running tasks that users actively observe and expect to persist while navigating away, such as turn-by-turn GPS navigation, VoIP calls, or music playback. They mandate a persistent system notification and require declaring explicit runtime foregroundServiceType permissions under modern Android platform constraints.
Finally, AlarmManager is intended exclusively for clock-exact, user-facing events such as morning wake-up alarms and medication reminders using exact alarm permissions. It wakes the device CPU from low-power states and should never be used for periodic polling or general background data processing.""",
    "deep_senior_en": """Under the hood, modern Android operating system releases—specifically Android 12 through 15—have systematically restricted background execution to maximize battery life and system health.
In earlier Android eras, developers routinely launched background services or scheduled inexact alarms for periodic synchronization. Today, background services face severe restrictions: starting a foreground service from the background throws ForegroundServiceStartNotAllowedException on Android 12 and later, unless the application meets narrow platform exemptions such as handling a high-priority Firebase Cloud Messaging push or user interaction with a home screen widget.
Furthermore, AlarmManager now requires user-granted exact alarm permissions like SCHEDULE_EXACT_ALARM or USE_EXACT_ALARM, which Google Play strictly regulates under policy enforcement. Using exact alarms to poll backend servers wastes radio power and will result in store rejection.
To bridge the gap between deferrable jobs and immediate execution without relying on fragile foreground services, WorkManager provides Expedited Work. Expedited work grants a high-priority execution quota managed by the platform JobScheduler. It executes within seconds of being enqueued, operates without requiring a user-visible notification on Android 12+, and falls back to a temporary foreground service on older API levels.
Staff engineers enforce this operational hierarchy by establishing lint rules: viewModels handle transient in-memory operations, repositories register durable synchronization jobs via WorkManager with exponential backoff, and foreground services remain strictly quarantined behind specialized media or location modules.""",
    "meta_ar": {
        "id": "BG-01",
        "questionAr": "متى تختار Coroutines، أو WorkManager، أو Foreground Service، أو AlarmManager؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على تصنيف المهام الخلفية حسب دورة الحياة والتأجيل وإدراك المستخدم، ومعرفة قيود النظام الحديثة في أندرويد 12+ واستخدام Expedited Work.",
        "why_it_matters_ar": "اختيار الأداة الخاطئة يتسبب في فقدان مهام المستخدم عند إغلاق التطبيق، أو استهلاك البطارية وقتل الـ Process بواسطة نظام التشغيل، أو رمي استثناءات أمنية في أندرويد الحديث.",
        "worked_example_ar": "مصفوفة الاختيار البرمجي:\n```kotlin\n// 1. Coroutine: مهمة شاشة فورية\nviewModelScope.launch { loadProducts() }\n// 2. WorkManager: رفع ملف دائم حتى لو أُغلق التطبيق\nWorkManager.getInstance(ctx).enqueueUniqueWork(\"upload\", ExistingWorkPolicy.KEEP, req)\n// 3. AlarmManager: منبه استيقاظ بالثانية\nalarmManager.setExactAndAllowWhileIdle(RTC_WAKEUP, triggerAt, pendingIntent)\n```",
        "trade_offs_ar": "الـ Coroutines سريعة وخفيفة لكنها تموت مع الشاشة، والـ WorkManager دائم ومضمون لكنه يقبل التأجيل، والـ Foreground Service مستمرة لكنها تتطلب إشعاراً دائماً وقيود تشغيل صارمة.",
        "failure_modes_ar": "تشغيل عملية رفع ملفات أو مزامنة بيانات مالية داخل `viewModelScope` فقط، مما يؤدي لموت المهمة وفقدان بيانات العميل فور خروجه من الشاشة أو تدمير النظام للتطبيق.",
        "production_perspective_ar": "في التطبيقات العالمية، نفرض تشغيل أي مزامنة أو حفظ بيانات في WorkManager مع Outbox Pattern، ونقصر استخدام Foreground Service على الملاحة والصوت مع تحديد النوع في المانيفست بدقة.",
        "how_to_answer_ar": "ابدأ بشجرة القرار: هل المهمة مرتبطة بالشاشة أم دائمة؟ هل تحتاج توقيتاً دقيقاً بالثانية أم تقبل التأجيل؟ ثم استعرض كل أداة وسياقها المثالي وقيود أندرويد الحديثة.",
        "talking_points_ar": "شجرة اتخاذ القرار، ومفهوم Durable Work، وقيود تشغيل الخدمات الخلفية في أندرويد 12+، وميزة Expedited Work في WorkManager، وصلاحيات AlarmManager الدقيقة.",
        "follow_ups_ar": "- **المحاور:** \"هل ينفع نستخدم AlarmManager لعمل مزامنة دورية مع السيرفر كل نصف ساعة؟\"\n  **المرشح:** \"ممنوع تماماً؛ لأن AlarmManager مصمم للمنبهات الدقيقة للمستخدم فقط، واستخدامه للمزامنة يضر البطارية ويخالف سياسات جوجل بلاي؛ والأداة الصحيحة هي PeriodicWorkRequest في WorkManager.\"\n\n- **المحاور:** \"ماذا يحدث لكوروتين شغال في `GlobalScope` لو نظام التشغيل قتل الـ Process؟\"\n  **المرشح:** \"يموت الكوروتين فوراً وتضيع المهمة لأن GlobalScope يظل داخل حدود الذاكرة (In-Process)، والحل الوحيد للمهام الدائمة هو WorkManager.\"",
        "self_check_ar": "هل فرقت بوضوح بين العمل المرتبط بالشاشة والعمل الدائم؟ هل وضحت الاستخدام الحصري لـ AlarmManager؟ وهل شرحت قيود أندرويد 12+ على Foreground Services؟",
        "references_ar": f"- [Android background work guide](https://developer.android.com/guide/background) — الدليل الرسمي لجوجل لاختيار الآلية المناسبة للمهام الخلفية.\n- [Foreground service restrictions in Android 12+](https://developer.android.com/about/versions/12/behavior-changes-12#foreground-service-launch-restrictions) — التغييرات الجذرية على تشغيل الخدمات الأمامية.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "بنختار الكوروتينات للمهام الفورية المرتبطة بواجهة المستخدم واللي بتلغى طبيعياً مع تدمير الشاشة زي جلب البيانات. وبنختار WorkManager للمهام الدائمة اللي لازم تتنفذ حتماً حتى لو التطبيق اتقفل أو الموبايل عمل ريستارت زي المزامنة ورفع الملفات. والـ Foreground Service للعمليات الطويلة اللي المستخدم واعي بيها ومحتاجة إشعار مستمر زي تشغيل الصوت والملاحة. و AlarmManager فقط للمنبهات الدقيقة بالثانية زي منبه الاستيقاظ.",
        "best_answer_ar": "اختيار الأداة المناسبة للمهام الخلفية في أندرويد بيتوقف على معيارين أساسيين: هل المهمة مرتبطة بدورة حياة الواجهة أم دائمة، وهل التوقيت مطلوب بالثانية أم يقبل التأجيل.\n\nالكوروتينات على مستوى `viewModelScope` أو `lifecycleScope` مخصصة للعمليات الفورية داخل حدود الـ Process. أول ما المستخدم يخرج من الشاشة، الكوروتين بيلغى تلقائياً، وده مثالي للبحث وعرض القوائم ومعالجة استجابات الواجهة السريعة.\n\nلو المهمة لازم تكتمل حتى لو المستخدم قفل التطبيق أو النظام قفل الـ Process لتوفير الذاكرة، فاختيارنا الإجباري هو WorkManager. هو المحرك الرسمي للمهام المؤجلة والدائمة، وبيحفظ بيانات الطلب في قاعدة بيانات SQLite مدمجة ويشغلها عبر JobScheduler وفق شروط توفر الإنترنت والشحن.\n\nأما الـ Foreground Service فبنستخدمها حصرياً للعمليات الطويلة المستمرة اللي المستخدم واعي بوجودها بنشاط زي تشغيل الأغاني أو الملاحة بالـ GPS، وبتتطلب إشعاراً دائماً لا يمكن حذفه ونوع خدمة محدد في المانيفست.\n\nوأخيراً، الـ AlarmManager محجوز تماماً للتنبيهات الصارمة بالثانية زي منبه الاستيقاظ أو مواعيد الأدوية عبر صلاحيات خاصة، وممنوع نهائياً استخدامه لجلب الداتا أو المزامنة.",
        "deep_answer_ar": "تحت الكابوت، إصدارات أندرويد الحديثة من أندرويد 12 وحتى 15 فرضت قيوداً صارمة جداً على المهام الخلفية للحفاظ على استهلاك البطارية والذاكرة. تشغيل الـ Foreground Service من الخلفية أصبح ممنوعاً تماماً وبيرمي `ForegroundServiceStartNotAllowedException` إلا في استثناءات ضيقة جداً زي استقبال إشعار FCM فائق الأهمية أو تفاعل المستخدم مع Widget.\n\nبالإضافة لده، استخدام AlarmManager الدقيق بقى بيتطلب صلاحية خاصة `SCHEDULE_EXACT_ALARM`، وجوجل بلاي بتدقق عليها بشدة وممكن ترفض التطبيق لو استخدمتها لمزامنة عادية بدل التنبيهات الحقيقية.\n\nعلشان نحل الفجوة بين المهام المؤجلة والمهام اللي محتاجة تنفيذ سريع وفوري، WorkManager بيوفر ميزة الـ Expedited Work. الميزة دي بتطلب من نظام التشغيل حصة تنفيذ فورية ذات أولوية عالية بدون الحاجة لعرض إشعار دائم للمستخدم على أندرويد 12 فما فوق، وبترجع تشتغل كـ Foreground Service مؤقتة على الأجهزة القديمة.\n\nالمهندسون الكبار بيصمموا معمارية التطبيق بحيث تكون الكوروتينات محصورة في منطق الواجهة اللحظي، بينما أي حفظ أو رفع لبيانات حساسة بيتم تسجيله في الـ Database المحلية كمسودة وينطلق له Worker دائم، وده بيضمن عدم ضياع أي معاملة للعميل حتى في أسوأ ظروف انقطاع الشبكة أو موت الـ Process المفاجئ، مع الحفاظ الكامل على عمر شحن بطارية الهاتف واستقرار النظام."
    }
}

# ==========================================
# BG-02: What is WorkManager and Guarantees
# ==========================================
DATA["BG-02"] = {
    "concept_en": """WorkManager is an Android Jetpack library designed for persistent, deferrable background work. It provides several core architectural guarantees: guaranteed execution (persisting work requests in an internal Room SQLite database so that tasks survive process death, application crashes, and device reboots), constraint satisfaction (executing only when specified environmental conditions like unmetered Wi-Fi, battery charging, or storage adequacy are fulfilled), battery-friendly scheduling (delegating to the platform JobScheduler and honoring Doze mode and App Standby buckets), managed retries (offering configurable exponential and linear backoff algorithms upon failure), and observability (exposing continuous LiveData and Flow streams of WorkInfo to track state transitions and progress).""",
    "walkthrough_en": """Configuring and observing persistent work in WorkManager:
```kotlin
// 1. Defining a persistent worker
class DatabasePruneWorker(
    appContext: Context,
    workerParams: WorkerParameters
) : CoroutineWorker(appContext, workerParams) {
    override suspend fun doWork(): Result = withContext(Dispatchers.IO) {
        runCatching {
            // Intensive database maintenance
            AppDatabase.getInstance(applicationContext).pruneExpiredSessions()
            Result.success()
        }.getOrElse { Result.retry() } // Automatically triggers exponential backoff
    }
}

// 2. Scheduling with constraints and observing status
fun enqueueMaintenanceWork(context: Context) {
    val constraints = Constraints.Builder()
        .setRequiresCharging(true)
        .setRequiresDeviceIdle(true)
        .build()

    val request = OneTimeWorkRequestBuilder<DatabasePruneWorker>()
        .setConstraints(constraints)
        .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 15, TimeUnit.SECONDS)
        .build()

    val workManager = WorkManager.getInstance(context)
    workManager.enqueueUniqueWork("db_prune", ExistingWorkPolicy.KEEP, request)

    // 3. Observing work status reactively via Flow
    workManager.getWorkInfoByIdFlow(request.id).map { it?.state }
}
```""",
    "short_en": """WorkManager is Android's recommended library for persistent, deferrable background work. It guarantees execution across process death and device reboots by persisting requests in an internal SQLite database. It guarantees constraint satisfaction, executing only when conditions like network and charging are met, while respecting Doze mode. It provides built-in exponential backoff retry policies and observable work status via WorkInfo flows.""",
    "structured_en": """WorkManager provides a robust, battery-conscious framework for background processing, establishing several critical architectural guarantees.
First, it guarantees persistent execution. When a work request is enqueued, WorkManager serializes its parameters and persists the request in an internal Room SQLite database. If the operating system reclaims the application process or the user restarts the phone, WorkManager reconciles its database upon boot and re-schedules pending tasks through the platform JobScheduler.
Second, it guarantees constraint satisfaction. Tasks declare environmental constraints—such as requiring unmetered Wi-Fi, battery not low, or device charging. WorkManager monitors system broadcast triggers and defers execution until all constraints are concurrently fulfilled.
Third, it guarantees managed retries and backoff. When a worker returns Result.retry(), WorkManager reschedules execution using configurable linear or exponential backoff policies to prevent hammering backend servers during outages.
Finally, it provides observable status. WorkManager exposes reactive streams of WorkInfo through Flow or LiveData, allowing presentation code to monitor state transitions, progress updates, and output data seamlessly.""",
    "deep_senior_en": """Under the hood, WorkManager operates as an abstraction layer above underlying Android operating system scheduling engines. It intelligently selects the optimal execution engine based on API level: JobScheduler on Android 5.0+ (API 21+), complemented by internal platform optimizations on Android 12+ for expedited execution.
Because WorkManager persists work state to disk before executing, it is completely immune to low-memory process kills. However, senior engineers understand that WorkManager provides at-least-once execution guarantees rather than exactly-once execution. If a Worker is executing when the operating system abruptly kills the host process, or if an unexpected timeout occurs during network transmission, WorkManager re-enqueues the work. Consequently, the work will be re-attempted upon restart.
This at-least-once guarantee mandates that all worker implementations must be strictly idempotent. If a worker submits payment data or modifies remote entities, it must pass a client-generated UUID or idempotency token. If the worker retries after an unexpected interruption, the backend recognizes the repeated token and avoids processing duplicate transactions.
Staff engineers also configure WorkManager custom initialization via Configuration.Provider. Disabling the default automatic ContentProvider initialization prevents startup bottlenecks and enables injecting constructor dependencies into custom WorkerFactory instances via Hilt, keeping background workers fully testable and decoupled. This comprehensive architecture ensures that enterprise mobile applications maintain total data integrity without introducing flaky tests or background performance regressions.""",
    "meta_ar": {
        "id": "BG-02",
        "questionAr": "ما هو WorkManager وما هي الضمانات التي يقدمها؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم دور WorkManager كمعيار رسمي للمهام الدائمة، وإدراك ضمانة التنفيذ الأكيد عبر SQLite الداخلي، ومفهوم At-least-once Execution، وضرورة الـ Idempotency.",
        "why_it_matters_ar": "الاعتقاد بأن WorkManager ينفذ العمليات فوراً أو بالضبط مرة واحدة يؤدي لمشاكل في التوقيت وتكرار المعاملات المالية عند إعادة المحاولة التلقائية.",
        "worked_example_ar": "جدولة مهمة بمحددات وتتبع حالتها عبر Flow:\n```kotlin\nval req = OneTimeWorkRequestBuilder<SyncWorker>()\n    .setConstraints(Constraints.Builder().setRequiredNetworkType(NetworkType.UNMETERED).build())\n    .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 15, TimeUnit.SECONDS)\n    .build()\nWorkManager.getInstance(ctx).getWorkInfoByIdFlow(req.id).collect { info ->\n    if (info?.state == WorkInfo.State.SUCCEEDED) println(\"Done!\")\n}\n```",
        "trade_offs_ar": "الـ WorkManager يضمن التنفيذ ويحافظ على البطارية، لكنه يضحي بالتوقيت اللحظي ويخضع لتأجيلات النظام ونوافذ الصيانة في وضع Doze.",
        "failure_modes_ar": "افتراض أن المهمة ستعمل مرة واحدة فقط (Exactly-once)، مما يتسبب في تكرار خصم الأموال أو إرسال طلبات مكررة عند إعادة تشغيل الـ Worker بعد انقطاع مفاجئ.",
        "production_perspective_ar": "في المشروعات الإنتاجية، نوقف الـ Auto-initialization لـ WorkManager ونحقن WorkerFactory مخصص عبر Hilt لتمرير الـ Repositories في الـ Constructor.",
        "how_to_answer_ar": "عرف WorkManager واشرح ضماناته الأساسية: استمرارية التنفيذ بعد ريستارت الهاتف وموت الـ Process، واحترام محددات النظام والبطارية، ونظام إعادة المحاولة الذكي، ثم وضح حقيقة At-least-once Execution.",
        "talking_points_ar": "ضمانة التنفيذ المؤكد عبر SQLite الداخلي، وضمانة استيفاء القيود، والتنفيذ لمرة واحدة على الأقل (At-least-once)، ومفهوم Idempotency، وحقن Hilt عبر Custom WorkerFactory.",
        "follow_ups_ar": "- **المحاور:** \"هل يضمن WorkManager تنفيذ المهمة فوراً بالثانية؟\"\n  **المرشح:** \"لا؛ الـ WorkManager مخصص للمهام القابلة للتأجيل (Deferrable)، والنظام قد يؤجل التنفيذ حتى تتوفر الشروط أو تفتح نافذة الصيانة في وضع Doze، إلا لو استخدمنا Expedited Work للأولويات العالية.\"\n\n- **المحاور:** \"كيف يتعامل WorkManager مع إعادة تشغيل الهاتف (Device Reboot)؟\"\n  **المرشح:** \"لأنه بيسجل كل طلبات العمل في قاعدة بيانات SQLite داخلية، أول ما الجهاز يفتح، WorkManager بيستمع لـ BOOT_COMPLETED ويعيد جدولة المهام تلقائياً مع نظام التشغيل.\"",
        "self_check_ar": "هل شرحت التخزين الداخلي في SQLite؟ هل ذكرت ضمانة القيود وإعادة المحاولة؟ وهل بينت حقيقة At-least-once وضرورة الـ Idempotency؟",
        "references_ar": f"- [WorkManager Architecture & Guarantees](https://developer.android.com/topic/libraries/architecture/workmanager) — التوثيق الرسمي لدور وضمانات مكتبة WorkManager.\n- [Custom WorkManager Configuration](https://developer.android.com/topic/libraries/architecture/workmanager/advanced/custom-configuration) — تهيئة وإعداد حقن التبعيات لمكتبة WorkManager.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "مكتبة WorkManager هي معيار أندرويد الرسمي لإدارة المهام الخلفية الدائمة والقابلة للتأجيل. بتقدم ضمانات جوهرية أهمها ضمان استمرار التنفيذ حتى لو التطبيق اتقفل أو النظام قتل الـ Process أو الموبايل اتعمل له ريستارت، وده لأنه بيحفظ الطلبات في قاعدة بيانات SQLite داخلية. وبيضمن استيفاء القيود زي توفر الواي فاي والشاحن، وبيدير إعادة المحاولة بـ Exponential Backoff، وبيوفر مراقبة حية لحالة المهمة عبر Flow.",
        "best_answer_ar": "مكتبة WorkManager بتقدم إطار عمل متين وموفر للبطارية لإدارة المهام الخلفية، وبتوفر مجموعة من الضمانات المعمارية الصارمة.\n\nأول ضمانة هي التنفيذ الدائم المستمر؛ أول ما بتضيف WorkRequest، المكتبة بتسجل بياناته ومحدداته في قاعدة بيانات Room SQLite داخلية. فلو نظام التشغيل قتل الـ Process لتوفير الميموري أو المستخدم عمل ريستارت للهاتف، WorkManager بيسترجع المهام المعلقة ويعيد جدولتها تلقائياً مع نظام التشغيل عبر JobScheduler.\n\nتاني ضمانة هي الالتزام الكامل بالقيود؛ فلو حددت إن المهمة محتاجة اتصال إنترنت غير محدود أو شاحن متصل، الـ Worker مش هيشتغل غير لما كل القيود دي تتحقق في نفس اللحظة.\n\nتالت ضمانة هي إدارة الفشل وإعادة المحاولة التلقائية؛ فلما الـ Worker يرجع Result.retry()، النظام بيعيد جدولته تلقائياً وفق سياسة Exponential Backoff لتقليل الضغط على السيرفر.\n\nوأخيراً، بيوفر المراقبة التفاعلية لحالة المهام من خلال تدفقات Flow و LiveData لكائن WorkInfo، مما يتيح للواجهة متابعة تقدم التنفيذ والنتائج بسلاسة تامة.",
        "deep_answer_ar": "تحت الكابوت، WorkManager بيشتغل كطبقة تجريد ذكية فوق محركات الجدولة في نظام أندرويد، وبيعتمد أساسياً على JobScheduler في إصدارات أندرويد الحديثة مع تحسينات الـ Expedited Jobs في أندرويد 12.\n\nالميزة الأهم هي التخزين الدائم على القرص قبل بدء التنفيذ، وده بيحميه تماماً من موت الـ Process. ولكن كمهندسين كبار، لازم ندرك إن ضمانة التنفيذ في WorkManager هي At-least-once Execution وليست Exactly-once. لو الـ Worker شغال وحصل انقطاع مفاجئ في الاتصال أو النظام قفل الـ Process قبل ما يرجع Result.success()، الـ WorkManager هيعيد تشغيل الـ Worker من البداية عند استقرار الظروف.\n\nالحقيقة دي بتفرض قاعدة هندسية حاسمة: كل Workers لازم تكون Idempotent قطيعاً. لو بتنفذ معاملة مالية أو مزامنة، لازم تمرر مع كل طلب كود عملية فريد UUID، علشان لو حصلت إعادة محاولة، السيرفر يكتشف تكرار العملية ويرجع نجاح بدل ما يخصم المبلغ مرتين.\n\nالمهندسون الكبار بيعطلوا كمان الـ Default ContentProvider Initialization لمكتبة WorkManager في ملف المانيفست، ويطبقوا Configuration.Provider لحقن الـ WorkerFactory عبر Hilt، وده بيسمح بتمرير الـ Repositories في كونستركتور الـ Worker واختباره بسهولة فائقة، مع الحفاظ على عزل المعمارية النظيفة وسرعة إقلاع التطبيق بدون أي تأخير، وضمان بقاء المهام الخلفية قيد التنفيذ الموثوق تحت كافة ظروف النظام وبيئاته التشغيلية المختلفة."
    }
}

# ==========================================
# BG-03: OneTimeWorkRequest vs PeriodicWorkRequest
# ==========================================
DATA["BG-03"] = {
    "concept_en": """OneTimeWorkRequest and PeriodicWorkRequest represent the two foundational request modalities in WorkManager, differing fundamentally in execution lifecycle, scheduling guarantees, and platform constraints. OneTimeWorkRequest runs exactly once per lifecycle, supports sequential and parallel work chaining via beginWith().then(), allows initial delays, and can be configured as Expedited Work for immediate priority execution. In contrast, PeriodicWorkRequest executes recurringly at defined intervals. To preserve battery life and prevent resource exhaustion, the Android platform enforces a strict minimum repeat interval of 15 minutes (MIN_PERIODIC_INTERVAL_MILLIS). Periodic work cannot be chained, cannot execute as expedited work, and supports a flex interval that defines an execution window [repeatInterval - flexInterval, repeatInterval] allowing the OS to batch work during battery-efficient radio wakeups.""",
    "walkthrough_en": """Comparing OneTimeWorkRequest chaining with PeriodicWorkRequest scheduling:
```kotlin
// 1. OneTimeWorkRequest: Chained execution with initial delay
val compressRequest = OneTimeWorkRequestBuilder<CompressImageWorker>()
    .setInputData(workDataOf("image_id" to 101))
    .build()

val uploadRequest = OneTimeWorkRequestBuilder<UploadImageWorker>()
    .setConstraints(Constraints.Builder().setRequiredNetworkType(NetworkType.CONNECTED).build())
    .build()

// Chaining: Compress first, then upload
WorkManager.getInstance(context)
    .beginWith(compressRequest)
    .then(uploadRequest)
    .enqueue()

// 2. PeriodicWorkRequest: Recurring background sync with Flex window
// Runs every 1 hour, but flexibly allowed to execute in the last 15 minutes of that hour
val periodicSyncRequest = PeriodicWorkRequestBuilder<SyncCatalogWorker>(
    repeatInterval = 1, repeatIntervalTimeUnit = TimeUnit.HOURS,
    flexTimeInterval = 15, flexTimeIntervalUnit = TimeUnit.MINUTES
).setConstraints(
    Constraints.Builder().setRequiresBatteryNotLow(true).build()
).build()

WorkManager.getInstance(context).enqueueUniquePeriodicWork(
    "catalog_sync",
    ExistingPeriodicWorkPolicy.UPDATE,
    periodicSyncRequest
)
```""",
    "short_en": """OneTimeWorkRequest executes once, supports chaining through beginWith and then, allows initial execution delays, and supports expedited priority execution. PeriodicWorkRequest executes on a recurring schedule with a mandatory platform minimum interval of 15 minutes. It cannot be chained or run as expedited work, but supports a flex interval that allows the operating system to batch execution windows for battery optimization.""",
    "structured_en": """WorkManager divides background scheduling into one-time and recurring executions, each engineered for distinct operational requirements.
OneTimeWorkRequest represents single-run tasks. It offers maximum flexibility: requests can be chained sequentially or in parallel graphs using beginWith and then. It supports initial execution delays and can be configured with setExpedited for immediate high-priority processing. When combined with unique work policies like APPEND or REPLACE, it excels at user-initiated actions like photo uploads and database migrations.
In contrast, PeriodicWorkRequest is designed for routine maintenance tasks such as log rotation, cache pruning, and daily data prefetching. The Android operating system enforces a hard minimum interval of 15 minutes to prevent battery drain. Unlike one-time requests, periodic work cannot be chained, and it does not support expedited execution.
A key architectural feature of periodic requests is the flex interval. By defining a flex period—which cannot be less than five minutes—developers grant the system an execution window within each cycle, allowing JobScheduler to batch work with other apps during Doze maintenance windows.""",
    "deep_senior_en": """Under the hood, understanding the execution mechanics of PeriodicWorkRequest is critical for avoiding subtle scheduling bugs. Many developers mistakenly believe that specifying a repeat interval of one hour means the worker will execute precisely on the hour mark.
In reality, periodic execution times drift. When a device enters Doze mode, background alarms and JobScheduler triggers are batched into infrequent maintenance windows. If a periodic interval expires while the device is in deep Doze, the task is held until the next window opens.
The flex interval (MIN_PERIODIC_FLEX_MILLIS, which defaults to 5 minutes) formalizes this flexibility. If you configure a repeat interval of 60 minutes with a flex interval of 15 minutes, the operating system is permitted to trigger the worker anywhere between the 45th and 60th minute of each cycle. This allows the OS radio scheduler to bundle your network request alongside other apps that have already powered up the cellular modem, conserving significant battery.
Furthermore, handling unique periodic work requires careful policy selection. With Android Jetpack WorkManager 2.8+, ExistingPeriodicWorkPolicy.UPDATE allows updating constraints or intervals without canceling in-flight workers or resetting execution timers, solving a long-standing issue where ExistingPeriodicWorkPolicy.REPLACE would prematurely reset the repeat cycle.
Staff engineers enforce that clock-critical deadlines (such as taking a dose of medication at precisely 8:00 AM) are never scheduled via PeriodicWorkRequest, delegating them strictly to AlarmManager.""",
    "meta_ar": {
        "id": "BG-03",
        "questionAr": "قارن بين OneTimeWorkRequest و PeriodicWorkRequest.",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "المقارنة الدقيقة بين الطلبات الأحادية والدورية في WorkManager، وفهم حد الـ 15 دقيقة الإجباري، ومفهوم Flex Interval، وسلوك الجدولة مع وضع Doze.",
        "why_it_matters_ar": "محاولة تشغيل PeriodicWorkRequest كل دقيقة أو افتراض دقة التوقيت بالثانية يؤدي لتعطيل الجدولة واستنزاف البطارية أو فشل متطلبات البيزنس.",
        "worked_example_ar": "مقارنة برمجية بين الطلب الأحادي المتسلسل والدوري بنافذة مرنة:\n```kotlin\n// OneTime يدعم السلسلة: اضغط ثم ارفع\nworkManager.beginWith(compressReq).then(uploadReq).enqueue()\n// Periodic يتكرر كل ساعة مع نافذة مرنة 15 دقيقة وبحد أدنى 15 دقيقة للتكرار\nval periodic = PeriodicWorkRequestBuilder<SyncWorker>(1, TimeUnit.HOURS, 15, TimeUnit.MINUTES).build()\n```",
        "trade_offs_ar": "الطلب الأحادي يوفر مرونة وسلسلة كاملة وتنفيذاً فورياً عبر Expedited، بينما الدوري يحافظ على التكرار الآلي والبطارية لكنه يمنع السلسلة ويخضع لحد الـ 15 دقيقة.",
        "failure_modes_ar": "استخدام PeriodicWorkRequest لمنبه صباحي أو تذكير دواء دقيق، مما يؤدي لتأخير الرنين لمدة نصف ساعة بسبب تجميع المهام في وضع Doze.",
        "production_perspective_ar": "في المشروعات الكبرى، نستخدم `ExistingPeriodicWorkPolicy.UPDATE` لتحديث مواعيد المزامنة الدورية بدون إعادة تصفير العداد الزمني للمهمة أو إلغاء التنفيذ الجاري.",
        "how_to_answer_ar": "قارن بينهما في: دورة الحياة، إمكانية السلسلة (Chaining)، الحد الأدنى للتكرار (15 دقيقة)، والنافذة المرنة (Flex Interval)، ودقة التوقيت مع وضع Doze.",
        "talking_points_ar": "حد الـ 15 دقيقة الإجباري (MIN_PERIODIC_INTERVAL_MILLIS)، ومفهوم Flex Interval، وسلسلة المهام عبر beginWith/then، وسياسة UPDATE في WorkManager الحديث.",
        "follow_ups_ar": "- **المحاور:** \"هل أقدر أعمل PeriodicWorkRequest يتكرر كل 5 دقائق؟\"\n  **المرشح:** \"مستحيل برمجياً؛ لأن نظام أندرويد يفرض حداً أدنى إجبارياً قدره 15 دقيقة، ولو حددت 5 دقائق، WorkManager هيعدلها تلقائياً لـ 15 دقيقة لحماية البطارية.\"\n\n- **المحاور:** \"ما هي فائدة الـ Flex Interval في PeriodicWorkRequest؟\"\n  **المرشح:** \"هي نافذة مرنة بتسمح للنظام بتشغيل المهمة في أي وقت خلال نهاية الدورة لتجميعها مع مهام تطبيقات تانية لما شريحة الاتصال تصحى، وده بيوفر شحن الموبايل جداً.\""
      ,
        "self_check_ar": "هل ذكرت حد الـ 15 دقيقة؟ هل شرحت مفهوم الـ Flex Interval؟ وهل بينت أن السلسلة مقتصرة على OneTimeWorkRequest؟",
        "references_ar": f"- [Periodic work requests](https://developer.android.com/topic/libraries/architecture/workmanager/how-to/define-work#periodic_work) — التوثيق الرسمي لتعريف وجدولة المهام الدورية.\n- [WorkManager Chaining Guide](https://developer.android.com/topic/libraries/architecture/workmanager/how-to/chain-work) — دليل بناء سلاسل المهام المتتالية والمتوازية.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "الـ OneTimeWorkRequest بيشتغل مرة واحدة بس، وبيدعم ربط المهام في سلاسل متتالية بـ beginWith و then، وبيدعم التنفيذ الفوري السريع عبر Expedited Work. أما الـ PeriodicWorkRequest فمخصص للمهام المتكررة بانتظام، والنظام بيفرض عليه حداً أدنى للتكرار هو 15 دقيقة لحماية البطارية، ومينفعش يتربط في سلاسل ولا يشتغل كـ Expedited، لكنه بيدعم Flex Interval بتدي النظام مرونة لتجميع العمليات الموفرة للطاقة.",
        "best_answer_ar": "المقارنة بين OneTimeWorkRequest و PeriodicWorkRequest بتعكس اختلاف الهدف المعماري بين المهام التفاعلية ومهام الصيانة الدورية.\n\nالـ OneTimeWorkRequest مخصص للمهام الفردية اللي بتشتغل مرة واحدة. بيتميز بمرونة فائقة؛ فتقدر ترتب عدة مهام ورا بعض في سلاسل متتالية أو متوازية، زي ضغط الصورة أولاً ثم رفعها للسيرفر. وبيدعم تأخير البدء، وتقدر تخليه يشتغل بأولوية فورية عبر Expedited Work، ومثالي جداً للعمليات اللي بيطلبها المستخدم زي رفع ملف أو مزامنة فورية.\n\nعلى الجانب التاني، الـ PeriodicWorkRequest مخصص للمهام الدورية المتكررة زي تنظيف الكاش ومزامنة البيانات اليومية. نظام أندرويد بيفرض عليه حداً أدنى صارماً للتكرار هو 15 دقيقة، وتحديد أي رقم أقل من كده بيتم تجاهله تلقائياً ورفعه لـ 15 دقيقة لحماية البطارية. والطلب الدوري مينفعش يتربط في سلاسل، ومينفعش يشتغل كـ Expedited Work.\n\nالميزة الأهم في الطلب الدوري هي الـ Flex Interval، ودي نافذة مرنة بتحددها في نهاية كل دورة، بتسمح لنظام التشغيل باختيار اللحظة المثالية لتشغيل المهمة بالتزامن مع استيقاظ شبكة الموبايل لتطبيقات تانية لتوفير الطاقة.",
        "deep_answer_ar": "تحت الكابوت، فهم كواليس عمل PeriodicWorkRequest ضروري جداً لتجنب الأخطاء الشائعة في مواعيد التنفيذ. كتير من المطورين بيفتكروا إن تحديد تكرار كل ساعة معناه إن المهمة هتتنفذ بالثانية على رأس كل ساعة، وده غير صحيح.\n\nفي الواقع، مواعيد المهام الدورية بتنزاح بسبب وضع Doze لتوفير الطاقة؛ فالنظام بيعطل الجدولة العادية ويجمعها داخل نوافذ صيانة متباعدة. وهنا بتظهر أهمية الـ Flex Interval، فالحد الأدنى ليها هو 5 دقائق. لو حددت التكرار كل 60 دقيقة والـ Flex بـ 15 دقيقة، فالنظام معاه تصريح يشغل المهمة في أي وقت بين الدقيقة 45 والدقيقة 60، وده بيخلي الـ Radio Scheduler يشغل النت لمهمتك في نفس اللحظة اللي جهاز المودم صحي فيها لتطبيق تاني، فيوفر شحن البطارية بشكل هائل.\n\nبالإضافة لده، في إدارة المهام الدورية الفريدة، بنستخدم `ExistingPeriodicWorkPolicy.UPDATE` اللي نزلت في التحديثات الأخيرة لمكتبة WorkManager، لأنها بتسمح بتحديث الـ Constraints أو فترات التكرار بدون ما تلغي المهمة اللي شغالة حالياً أو تصفر عداد الوقت التراكمي زي ما كان بيحصل قديماً مع سياسة REPLACE.\n\nالمهندسون الكبار بيحذروا دائماً من استخدام PeriodicWorkRequest للمهام اللي محتاجة مواعيد دقيقة بالثانية زي منبه الاستيقاظ، وبيلجأوا حصرياً لـ AlarmManager في السيناريوهات دي."
    }
}

# ==========================================
# BG-04: Worker vs CoroutineWorker vs ListenableWorker
# ==========================================
DATA["BG-04"] = {
    "concept_en": """Worker, CoroutineWorker, and ListenableWorker represent the three fundamental implementation abstractions provided by WorkManager for authoring background operations. ListenableWorker serves as the foundational base class for all background tasks; it defines startWork(), which returns a ListenableFuture<Result> to support arbitrary asynchronous execution, making it the primary choice for Java codebases and RxJava integrations (via RxWorker). Worker is a synchronous subclass of ListenableWorker that executes its doWork() method on a dedicated background thread provided by WorkManager's background executor, blocking that thread until completion. CoroutineWorker is the idiomatic, Kotlin-first subclass of ListenableWorker; it provides a suspending doWork() function that executes within a CoroutineScope on Dispatchers.Default by default, seamlessly propagating WorkManager cancellation to Kotlin coroutine jobs and supporting structured concurrency and cooperative cancellation.""",
    "walkthrough_en": """Implementing synchronous Worker versus suspending CoroutineWorker:
```kotlin
// 1. Worker: Synchronous blocking implementation (Java / legacy compatibility)
class SyncDataWorker(context: Context, params: WorkerParameters) : Worker(context, params) {
    override fun doWork(): Result {
        // Blocks the background executor thread directly
        val response = httpUrlConnectionFetch()
        return if (response.isSuccess) Result.success() else Result.retry()
    }
}

// 2. CoroutineWorker: Idiomatic Kotlin suspending worker with cooperative cancellation
class SuspendingDownloadWorker(
    context: Context,
    params: WorkerParameters,
    private val api: DownloadApi,
    private val ioDispatcher: CoroutineDispatcher = Dispatchers.IO
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result = withContext(ioDispatcher) {
        try {
            // Emits progress reactively to WorkInfo observers
            setProgress(workDataOf("percent" to 50))
            api.downloadLargeFile() // Suspending call: automatically cancels if WorkManager stops work!
            Result.success()
        } catch (e: CancellationException) {
            // WorkManager stopped this worker: handle cooperative cleanup
            throw e
        } catch (e: Exception) {
            Result.retry()
        }
    }
}
```""",
    "short_en": """ListenableWorker is the core base class returning a ListenableFuture for custom asynchronous execution. Worker is a synchronous subclass that runs its doWork method on a background thread, blocking until completion. CoroutineWorker is the idiomatic Kotlin-first subclass providing a suspending doWork function with built-in coroutine cancellation propagation, structured concurrency, and reactive progress reporting via setProgress.""",
    "structured_en": """WorkManager provides three core worker classes tailored for different concurrency paradigms and language runtimes.
ListenableWorker is the fundamental base class upon which all WorkManager tasks are built. Instead of blocking a thread, its startWork method returns a Guava ListenableFuture of Result. This architecture provides maximum flexibility, making it the foundation for non-blocking asynchronous implementations, Java CompletableFuture workflows, and RxJava integrations via RxWorker.
Worker is a synchronous subclass designed for straightforward, blocking tasks. When using Worker, you override doWork, which executes on a background thread pool managed by WorkManager's Configuration executor. The thread is held synchronously until doWork returns Result.success(), Result.retry(), or Result.failure().
CoroutineWorker is the recommended, idiomatic standard for modern Kotlin Android development. It replaces blocking threads with a suspending doWork method. By default, it runs on Dispatchers.Default, but developers can switch to Dispatchers.IO inside the coroutine body.
CoroutineWorker bridges WorkManager lifecycle directly with Kotlin structured concurrency: when WorkManager cancels a task, the underlying coroutine job is cancelled cooperatively, immediately halting active network or database operations.""",
    "deep_senior_en": """Under the hood, selecting between these three classes impacts resource utilization, thread starvation, and cancellation responsiveness.
When using standard Worker, every running task consumes an entire operating system thread from WorkManager's background executor pool (which defaults to a fixed number of threads based on CPU cores). If several workers perform blocking I/O concurrently, the executor pool becomes starved, delaying other pending background jobs.
CoroutineWorker eliminates thread starvation by leveraging Kotlin suspending functions. Instead of blocking a thread while awaiting network or disk I/O, the coroutine suspends and releases the underlying thread back to the pool, allowing other workers or coroutines to utilize CPU cycles.
Furthermore, cancellation handling in CoroutineWorker is exceptionally elegant. When WorkManager stops a running job—due to constraint violations, timeout, or explicit cancellation—it cancels the CoroutineWorker's CoroutineScope. If your worker invokes suspending functions like delay or Ktor/Retrofit suspending endpoints, the cancellation propagates instantly, throwing a CancellationException.
In contrast, a traditional Worker must imperatively poll isStopped throughout its execution loop; if a blocking call does not check isStopped, the worker continues wasting device battery and memory until the operation eventually returns.
Staff engineers exclusively standardize on CoroutineWorker for all new features, utilizing custom WorkerFactory injection to supply dependencies directly via constructor injection.""",
    "meta_ar": {
        "id": "BG-04",
        "questionAr": "ما الفرق بين Worker و CoroutineWorker و ListenableWorker؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم التسلسل الهرمي لكلاسات WorkManager، وإدراك الفرق بين التنفيذ المتزامن وغير المتزامن، واستيعاب التزامن الهيكلي (Structured Concurrency) وإلغاء الكوروتينات في CoroutineWorker.",
        "why_it_matters_ar": "استخدام Worker التقليدي لعمليات طويلة يستهلك ثريدات النظام ويسبب Thread Starvation، بينما CoroutineWorker يوفر استهلاك الموارد ويدعم الإلغاء الفوري.",
        "worked_example_ar": "مقارنة doWork المتزامنة مع دوال التعليق في CoroutineWorker:\n```kotlin\n// CoroutineWorker نقي يدعم suspend و setProgress\nclass MyWorker(ctx: Context, params: WorkerParameters) : CoroutineWorker(ctx, params) {\n    override suspend fun doWork(): Result = withContext(Dispatchers.IO) {\n        setProgress(workDataOf(\"progress\" to 100))\n        Result.success()\n    }\n}\n```",
        "trade_offs_ar": "الـ Worker بسيط للعمليات المتزامنة في جافا، و ListenableWorker يوفر مرونة للفيوتشرز و RxJava، بينما CoroutineWorker هو الأفضل والأكثر كفاءة لكود كوتلن.",
        "failure_modes_ar": "تشغيل دوال حجب (Blocking I/O) داخل CoroutineWorker على Dispatchers.Default بدون استخدام withContext(Dispatchers.IO)، مما يعطل معالجة الكوروتينات الحسابية.",
        "production_perspective_ar": "في المشروعات الحديثة، نعتمد CoroutineWorker حصرياً في 100% من المهام، ونمرر التبعيات عبر Hilt و AssistedInject لضمان سهولة كتابة Unit Tests للمهام.",
        "how_to_answer_ar": "وضح أن ListenableWorker هو الكلاس الأساسي غير المتزامن، وأن Worker هو ابن متزامن يحجز ثريداً كاملاً، وأن CoroutineWorker هو الخيار القياسي لكوتلن بدعم التعليق والإلغاء.",
        "talking_points_ar": "الكلاس الأساسي ListenableWorker وعلاقته بـ ListenableFuture، واستهلاك الثريدات في Worker، ودعم suspend في CoroutineWorker، وتمرير الإلغاء التلقائي (Cooperative Cancellation).",
        "follow_ups_ar": "- **المحاور:** \"كيف يتعامل CoroutineWorker مع إلغاء المهمة لو انقطع شاحن الهاتف مثلاً؟\"\n  **المرشح:** \"أول ما تنكسر الشروط، WorkManager بيلغي الـ CoroutineScope الخاص بالـ Worker، فالكوروتين بيرمي CancellationException ويلغي دوال الـ suspend فوراً بدون أي تأخير.\"\n\n- **المحاور:** \"ما هو الـ Dispatcher الافتراضي الذي يعمل عليه CoroutineWorker؟\"\n  **المرشح:** \"يعمل افتراضياً على `Dispatchers.Default`؛ لذلك للعمليات الخاصة بالشبكة وقواعد البيانات، يجب التحويل صراحة لـ `Dispatchers.IO` عبر `withContext`.\""
      ,
        "self_check_ar": "هل وضحت دور ListenableWorker كأصل للكلاسات؟ هل بينت عيب حجز الثريدات في Worker؟ وهل شرحت مزايا CoroutineWorker في الإلغاء والتعليق؟",
        "references_ar": f"- [Threading in WorkManager](https://developer.android.com/topic/libraries/architecture/workmanager/advanced/coroutineworker) — الدليل الرسمي لاستخدام CoroutineWorker والكوروتينات.\n- [ListenableWorker API Reference](https://developer.android.com/reference/androidx/work/ListenableWorker) — التوثيق المصدري للكلاس الأساسي ListenableWorker.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "الـ ListenableWorker هو الكلاس الأساسي المجرد اللي بتتبني عليه كل مهام WorkManager وبيرجع ListenableFuture للعمليات غير المتزامنة ومناسب جداً لجافا و RxJava. والـ Worker هو كلاس متزامن بينفذ دالة doWork وبيحجز ثريد كامل من مجمع الثريدات لحد ما يخلص. أما CoroutineWorker فهو الخيار القياسي والحديث في كوتلن، بيوفر دالة doWork معلقة (suspend) بتدعم التزامن الهيكلي والإلغاء التلقائي للمهام مع توفير كبير في الموارد.",
        "best_answer_ar": "مكتبة WorkManager بتقدم ثلاثة كلاسات أساسية بتناسب لغات البرمجة المختلفة وأنماط التزامن المتنوعة.\n\nالـ ListenableWorker هو الكلاس الأساسي والأب لكل الـ Workers في المكتبة. دالة `startWork` جواه مش بتحجز ثريد بل بترجع كائن `ListenableFuture`، وده بيمنحه مرونة فائقة للتعامل مع العمليات غير المتزامنة، وبيعتبر الأساس لمكتبات جافا و RxWorker.\n\nأما الـ Worker العادي فهو كلاس مشتق ومتزامن؛ لما بتعمل Override لدالة `doWork`، المهمة بتشتغل على ثريد مخصص من مجمع ثريدات WorkManager، والثريد بيفضل محجوز ومجمد بالكامل لحد ما الدالة ترجع النتيجة.\n\nوالـ CoroutineWorker هو المعيار القياسي والأمثل لتطبيقات أندرويد الحديثة بلغة كوتلن. بيستبدل حجز الثريدات بدالة معلقة `suspend fun doWork()`، وبيشتغل افتراضياً على `Dispatchers.Default` مع إمكانية التحويل لـ `Dispatchers.IO`.\n\nالميزة الأقوى في CoroutineWorker هي التكامل التام مع الإلغاء؛ فلو محددات المهمة انكسرت أو أُلغيت، الـ Coroutine Job بتتلغي فوراً وبترمي `CancellationException` فتتوقف عمليات الشبكة والقراءة من القرص في اللحظة نفسها.",
        "deep_answer_ar": "تحت الكابوت، الاختيار بين الكلاسات دي بيأثر بشكل مباشر على كفاءة استهلاك الموارد ومنع ظاهرة الـ Thread Starvation. لما تستخدم Worker العادي، كل مهمة شغالة بتحجز ثريد كامل من الـ Thread Pool الخاص بـ WorkManager، فلو اشتغلت كذا مهمة بتعمل عمليات إدخال وإخراج بطيئة في نفس الوقت، المجمع هيتخنق تماماً وتتعطل باقي المهام المعلقة في الطابور.\n\nعلى النقيض تماماً، CoroutineWorker بيقضي على المشكلة دي بفضل طبيعة الكوروتينات في التعليق؛ فلما تنادي عملية شبكة معلقة، الكوروتين بيعلق تشغيله ويسيب الثريد للمهام التانية تستفيد منه، ويرجع يستأنف عمله أول ما الاستجابة توصل.\n\nبالإضافة لده، آلية الإلغاء في CoroutineWorker فائقة الدقة. لما WorkManager يقرر يوقف المهمة بسبب انقطاع الواي فاي أو انتهاء الوقت، بيلغي الـ CoroutineScope مباشرة، فدوال زي delay أو طلبات Retrofit المعلقة بتتوقف في أجزاء من الميلي ثانية.\n\nبينما في الـ Worker التقليدي، المطور بيضطر يكتب كود يفحص قيمة `isStopped` يدوياً بعد كل خطوة، ولو نادى دالة حجب متزامنة، الـ Worker هيفضل شغال ويستهلك البطارية لحد ما تخلص العملية.\n\nالمهندسون الكبار بيعتمدوا CoroutineWorker حصرياً في كل مشاريع كوتلن، وبيستخدموا Hilt مع `@HiltWorker` لتمرير الـ Repositories عبر الـ Constructor بسهولة فائقة، مع الاستفادة الكاملة من ميزات Structured Concurrency وإلغاء المهام التلقائي وحماية موارد النظام واستقرار التطبيق في بيئة الإنتاج."
    }
}

# ==========================================
# BG-05: Constraints, Backoff Policies, and Unique Work
# ==========================================
DATA["BG-05"] = {
    "concept_en": """Constraints, backoff policies, and unique work constitute the core policy configuration mechanisms that govern execution eligibility, error recovery, and deduplication in WorkManager. Constraints define prerequisite system conditions—such as network connectivity (Connected, Unmetered, NotRoaming), charging status, battery not low, storage not low, or device idle—that must be concurrently satisfied for work to run; if constraints break mid-execution, WorkManager halts the worker and reschedules it. Backoff policies govern retry intervals when a worker returns Result.retry(), offering Linear or Exponential backoff algorithms starting from a platform-enforced minimum of 10 seconds. Unique work provides name-based deduplication through enqueueUniqueWork, enforcing ExistingWorkPolicy strategies (KEEP, REPLACE, APPEND, APPEND_OR_REPLACE) to prevent redundant concurrent operations.""",
    "walkthrough_en": """Configuring Constraints, Exponential Backoff, and Unique Work:
```kotlin
// 1. Defining environmental constraints
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.UNMETERED) // Wi-Fi only
    .setRequiresCharging(true)                     // Plugged in
    .setRequiresBatteryNotLow(true)                // Above 15-20%
    .build()

// 2. Defining OneTimeWorkRequest with Exponential Backoff
val analyticsRequest = OneTimeWorkRequestBuilder<UploadAnalyticsWorker>()
    .setConstraints(constraints)
    .setBackoffCriteria(
        backoffPolicy = BackoffPolicy.EXPONENTIAL, // Delays double: 30s, 60s, 120s...
        backoffDelay = 30,
        timeUnit = TimeUnit.SECONDS
    )
    .build()

// 3. Enqueuing as Unique Work to prevent duplicate background pipelines
WorkManager.getInstance(context).enqueueUniqueWork(
    "upload_analytics_job",
    ExistingWorkPolicy.KEEP, // If job is already pending or running, keep it and ignore the new request
    analyticsRequest
)
```""",
    "short_en": """Constraints specify prerequisite environmental conditions like network connectivity, charging, and battery levels required for work to execute. Backoff policies determine retry delay schedules using linear or exponential algorithms starting from a minimum of ten seconds when workers return Result.retry. Unique work provides named deduplication using ExistingWorkPolicy modes like KEEP, REPLACE, APPEND, and APPEND_OR_REPLACE to prevent concurrent duplicate jobs.""",
    "structured_en": """WorkManager provides fine-grained operational control over background jobs through constraints, backoff policies, and unique work deduplication.
Constraints specify the environmental prerequisites required before a worker is permitted to run. These include network types (such as requiring unmetered Wi-Fi or non-roaming connections), battery thresholds (requiring the battery not to be low), device charging states, and idle status. If any constraint is violated while a task is running, WorkManager halts the worker and returns it to the queue.
Backoff policies dictate how WorkManager reschedules execution when a worker returns Result.retry(). Developers select between Linear backoff, where delays increase by a fixed duration each attempt, and Exponential backoff, where retry delays double progressively. The minimum allowable backoff delay enforced by the platform is ten seconds.
Unique work prevents duplicate tasks from running simultaneously by associating work requests with a unique string identifier. When enqueuing unique work, developers declare an ExistingWorkPolicy: KEEP preserves existing pending or running work while ignoring new requests; REPLACE cancels existing work to start fresh; APPEND chains new tasks after existing ones; and APPEND_OR_REPLACE guarantees sequential chaining while replacing failed precursors.""",
    "deep_senior_en": """Under the hood, these three mechanisms work together to guarantee system resource hygiene and prevent thundering herd problems on backend servers.
When evaluating constraints, WorkManager registers system broadcast receivers and network callbacks with the platform ConnectivityManager. Rather than polling device state continuously, WorkManager sleeps until the operating system signals that all designated constraints are satisfied simultaneously.
For backoff policies, Exponential backoff is the mandatory standard for network operations. If a backend service experiences an outage or rate-limiting threshold (HTTP 429 / 503), linear retries or immediate re-executions cause thousands of mobile clients to hammer the server in lockstep. Exponential backoff naturally spreads client retries across widening windows (e.g., 30s, 60s, 120s, up to a maximum cap of 5 hours), allowing backend services to recover safely.
When configuring unique work, selecting the proper ExistingWorkPolicy directly impacts data integrity. For example, with an offline photo upload queue, using ExistingWorkPolicy.APPEND ensures that user photos upload sequentially in the exact order they were taken without racing each other.
Conversely, for user profile updates or telemetry reporting, ExistingWorkPolicy.REPLACE ensures that the latest user edits overwrite stale pending requests, conserving radio data and avoiding redundant updates.
Staff engineers enforce these policies universally, preventing rogue background tasks from depleting device batteries or overwhelming infrastructure.""",
    "meta_ar": {
        "id": "BG-05",
        "questionAr": "ما هي محددات التنفيذ (Constraints)، وسياسات التراجع (Backoff)، والعمل الفريد (Unique Work)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم محددات العمل في WorkManager، وتطبيق سياسات Exponential Backoff لمنع إغراق السيرفر، واستخدام سياسات Unique Work (KEEP, REPLACE, APPEND) لمنع تكرار المهام.",
        "why_it_matters_ar": "غياب الـ Constraints يستنزف باقة العميل، وغياب Exponential Backoff يسقط السيرفر في فخ Thundering Herd، وغياب Unique Work يؤدي لتكرار رفع البيانات عدة مرات.",
        "worked_example_ar": "بناء طلب فريد بمحددات وسياسة تراجع مضاعفة:\n```kotlin\nval req = OneTimeWorkRequestBuilder<SyncWorker>()\n    .setConstraints(Constraints.Builder().setRequiredNetworkType(NetworkType.UNMETERED).build())\n    .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 30, TimeUnit.SECONDS)\n    .build()\nworkManager.enqueueUniqueWork(\"sync\", ExistingWorkPolicy.KEEP, req)\n```",
        "trade_offs_ar": "الـ Constraints الدقيقة تضمن سلامة البطارية لكنها قد تؤخر المهمة لأيام إذا لم يتوفر واي فاي، والـ Unique Work يمنع التكرار لكنه يتطلب اختيار السياسة المناسبة بعناية.",
        "failure_modes_ar": "استخدام سياسة تراجع خطية (Linear) بفاصل ثوان معدودة عند انقطاع السيرفر، مما يسبب إغراق السيرفر بملايين الطلبات المتكررة فور عودته للعمل.",
        "production_perspective_ar": "في تطبيقات المراسلة والتجارة، نستخدم `ExistingWorkPolicy.APPEND` لطابور إرسال الرسائل لضمان الترتيب، ونستخدم `ExistingWorkPolicy.REPLACE` لمزامنة الموقع الحالي لتقليل البيانات.",
        "how_to_answer_ar": "قسم الإجابة لثلاثة محاور: قيود النظام (شبكة، شحن، بطارية)، وسياسات إعادة المحاولة (Linear و Exponential وحساباتها)، وسياسات العمل الفريد (KEEP, REPLACE, APPEND).",
        "talking_points_ar": "أنواع Constraints وسلوك انكسارها، والـ Exponential Backoff لمنع Thundering Herd، والحد الأدنى 10 ثوان، وسياسات ExistingWorkPolicy الأربعة.",
        "follow_ups_ar": "- **المحاور:** \"ماذا يحدث لو انكسر أحد الـ Constraints أثناء تشغيل الـ Worker؟\"\n  **المرشح:** \"الـ WorkManager بيوقف الـ Worker فوراً وبيرسله إشارة إلغاء، ويعيد جدولته في الطابور تلقائياً علشان يشتغل أول ما الشروط تتحقق من جديد.\"\n\n- **المحاور:** \"ما الفرق بين سياستي KEEP و REPLACE في Unique Work؟\"\n  **المرشح:** \"سياسة KEEP بتحتفظ بالمهمة الموجودة حالياً وتتجاهل الطلب الجديد لو فيه مهمة شغالة أو معلقة، بينما REPLACE بتلغي المهمة القديمة فوراً وتبدأ تنفيذ الطلب الجديد.\""
      ,
        "self_check_ar": "هل شرحت أنواع الـ Constraints؟ هل فرقت بين Linear و Exponential Backoff؟ وهل وضحت سياسات ExistingWorkPolicy المختلفة؟",
        "references_ar": f"- [WorkManager Constraints](https://developer.android.com/topic/libraries/architecture/workmanager/how-to/define-work#work-constraints) — التوثيق الرسمي لتحديد قيود التشغيل.\n- [Unique Work Management](https://developer.android.com/topic/libraries/architecture/workmanager/how-to/unique-work) — دليل إدارة المهام الفريدة ومنع التكرار.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "الـ Constraints هي الشروط البيئية اللي لازم تتحقق علشان المهمة تشتغل، زي وجود واي فاي أو شاحن أو عدم انخفاض البطارية، ولو انكسرت والمهمة شغالة بتتوقف وتتجدول تاني. والـ Backoff Policies هي سياسات تأخير إعادة المحاولة لما الـ Worker يرجع Result.retry()، إما خطية بزيادة ثابتة أو أسية (Exponential) بمضاعفة وقت الانتظار لحماية السيرفر بحد أدنى 10 ثوانٍ. والـ Unique Work هو نمط لتسمية المهمة ومنع تكرارها بسياسات زي KEEP للاحتفاظ بالمهمة الحالية، أو REPLACE لاستبدالها، أو APPEND لترتيبها في سلسلة.",
        "best_answer_ar": "مكتبة WorkManager بتوفر تحكماً تشغيلياً فائق الدقة في المهام الخلفية من خلال المحددات وسياسات التراجع والعمل الفريد.\n\nأولاً، الـ Constraints بتمثل الشروط البيئية المسبقة لتشغيل المهمة؛ زي اشتراط شبكة غير محدودة (Unmetered) أو اتصال الشاحن أو عدم انخفاض شحن البطارية. لو انكسر أي شرط والمهمة شغالة في النص، WorkManager بيوقف الـ Worker تلقائياً ويرجعه للطابور ليعاد تشغيله عند استيفاء الشروط.\n\nثانياً، سياسات الـ Backoff بتحدد وقت الانتظار قبل إعادة المحاولة لما الـ Worker يرجع `Result.retry()`. بنختار بين التراجع الخطي (Linear) بزيادة وقت ثابتة، أو التراجع الأسي (Exponential) اللي بيضاعف وقت الانتظار مع كل محاولة (زي 30 ثم 60 ثم 120 ثانية) بحد أدنى 10 ثوانٍ يفرضه النظام لمنع إرهاق السيرفرات.\n\nثالثاً، الـ Unique Work بيمنع تكرار المهام المتطابقة بربطها باسم فريد واستخدام سياسات `ExistingWorkPolicy`. سياسة KEEP بتحافظ على المهمة الشغالة وتتجاهل الجديدة، وسياسة REPLACE بتلغي المهمة الحالية وتبدأ الجديدة فوراً، وسياسة APPEND بترتب المهام الجديدة ورا القديمة في طابور متسلسل، وسياسة APPEND_OR_REPLACE بتضمن استمرار السلسلة حتى لو فشلت مهمة سابقة.",
        "deep_answer_ar": "تحت الكابوت، تكامل الآليات دي هو اللي بيحمي بطارية الموبايل ويمنع مشاكل الـ Thundering Herd على السيرفرات. أثناء فحص الـ Constraints، مكتبة WorkManager مش بتعمل استطلاع مستمر يستهلك المعالج، بل بتسجل Broadcast Receivers و Network Callbacks في نظام التشغيل، وبتفضل نايمة تماماً لحد ما النظام يبلغها إن كل الشروط اتحققت.\n\nوفي سياسات الـ Backoff، استخدام Exponential Backoff إلزامي هندسياً لأي عمليات شبكة؛ لأن السيرفر لو واقع أو بيرجع 503، المحاولات الخطية السريعة هتخلي ملايين الأجهزة تضرب السيرفر في اللحظة نفسها وتوقعه أكتر. التراجع الأسي بيوزع محاولات الأجهزة على فترات متباعدة تتيح للباك إند التعافي بأمان.\n\nوعلى مستوى الـ Unique Work، اختيار السياسة السليمة بيحمي اتساق البيانات؛ ففي رفع الصور مثلاً بنستخدم `ExistingWorkPolicy.APPEND` علشان نضمن رفع الصور بالترتيب الزمني اللي المستخدم التقطه بدون تداخل أو سباق بيانات. بينما في تحديث الموقع الجغرافي أو تعديل الملف الشخصي بنستخدم `ExistingWorkPolicy.REPLACE` علشان نلغي الطلب القديم المعلق ونرفع أحدث داتا وصلتنا بدون إهدار باقة الإنترنت.\n\nالمهندسون الكبار بيحرصوا دائماً على دمج الآليات التلاتة مع بعض في كل Worker لضمان استقرار التطبيق وحماية البنية التحتية للسيرفرات، مع توفير تجربة مستخدم سلسة وموثوقة تتفادى استنزاف البطارية أو تكرار العمليات وحماية موارد الشبكة من الإرهاق غير المبرر على كافة الأصعدة."
    }
}

# ==========================================
# BG-06: Doze Mode and App Standby Restrictions
# ==========================================
DATA["BG-06"] = {
    "concept_en": """Doze mode and App Standby are battery-saving power management systems introduced in Android 6.0 (API 23) and enhanced in subsequent releases to drastically curb background battery consumption. Doze mode activates when a device is unplugged from power, stationary, and has its screen turned off for an extended period, operating in two stages: Light Doze (restricting network access and deferring jobs during brief screen-off phases) and Deep Doze (suspending network access, ignoring wake locks, deferring JobScheduler tasks, and silencing standard alarms). Deep Doze periodically opens brief maintenance windows to process batched work. App Standby categorizes apps into standby buckets (Active, Working Set, Frequent, Rare, Restricted) based on recency of user engagement, restricting background job frequency accordingly. WorkManager is fully compliant with both mechanisms.""",
    "walkthrough_en": """Adapting background work for Doze mode and App Standby:
```kotlin
// 1. Regular WorkManager tasks: Automatically deferred until Doze maintenance windows
val regularSyncRequest = OneTimeWorkRequestBuilder<SyncWorker>()
    .setConstraints(Constraints.Builder().setRequiredNetworkType(NetworkType.CONNECTED).build())
    .build()
WorkManager.getInstance(context).enqueue(regularSyncRequest) // Waits for maintenance window

// 2. Expedited Work: Executes out-of-quota even during Doze for time-sensitive tasks
val criticalMessageRequest = OneTimeWorkRequestBuilder<SendMessageWorker>()
    .setExpedited(OutOfQuotaPolicy.RUN_AS_NON_EXPEDITED_WORK_REQUEST)
    .build()
WorkManager.getInstance(context).enqueue(criticalMessageRequest)

// 3. Exact user alarm: Penetrates Doze mode strictly for alarms (e.g., wake-up alarm)
fun setDozePenetratingAlarm(context: Context, triggerEpochMs: Long, pi: PendingIntent) {
    val am = context.getSystemService(AlarmManager::class.java)
    am.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, triggerEpochMs, pi)
}
```""",
    "short_en": """Doze mode restricts network access, ignores wake locks, and defers background jobs and alarms when a device is unplugged, stationary, and screen-off, opening brief maintenance windows periodically to process batched work. App Standby places unused apps into buckets like Working Set, Frequent, and Rare, limiting their job and alarm execution frequency. WorkManager natively complies with both power systems by deferring normal jobs while supporting expedited work for urgent tasks.""",
    "structured_en": """Doze mode and App Standby are Android's primary platform mechanisms designed to prevent rogue background processes from depleting battery life.
Doze mode activates when a device is disconnected from power, stationary, and left with its screen turned off. It operates across two phases: Light Doze applies initial network restrictions while allowing job execution, while Deep Doze engages when the device remains stationary for an extended period. Under Deep Doze, the system suspends all network access, ignores CPU wake locks, defers standard JobScheduler tasks, and suppresses ordinary alarms. Periodically, the operating system opens brief maintenance windows to execute queued network requests and pending jobs before re-entering deep sleep with progressively widening intervals.
App Standby evaluates individual application usage patterns independently of device state. It classifies apps into App Standby Buckets—Active, Working Set, Frequent, Rare, and Restricted—based on how recently and frequently the user interacts with the app. Apps in lower buckets face severe daily limits on JobScheduler execution time and restricted network access.
WorkManager natively harmonizes with both power systems: standard workers defer until maintenance windows or bucket allowances open, while urgent tasks can leverage Expedited Work quotas to execute promptly.""",
    "deep_senior_en": """Under the hood, understanding Doze mode transitions is essential for diagnosing delayed background processing in enterprise applications.
When a device transitions into Deep Doze, the Linux kernel enters low-power sleep states. If an application holds a Partial WakeLock, Android ignores the lock to preserve power. Furthermore, network access is completely blocked at the iptables firewall layer for all applications except those with whitelisted high-priority push exemptions.
During the periodic maintenance windows, the system unblocks network access and triggers JobScheduler to flush accumulated jobs. However, each successive maintenance window is scheduled farther apart (e.g., 15 minutes, 30 minutes, 1 hour, up to several hours), meaning non-critical background synchronization can be delayed for hours while the user sleeps.
Developers often attempt to bypass Doze mode by requesting battery optimization whitelisting via the REQUEST_IGNORE_BATTERY_OPTIMIZATIONS permission. However, Google Play strictly prohibits this permission for general-purpose apps, reserving it exclusively for core tracking, health monitor, or VoIP applications; misuse results in immediate store rejection.
Instead, staff engineers architect applications around platform compliance: routine tasks run as standard WorkManager requests awaiting maintenance windows, time-critical messages utilize high-priority Firebase Cloud Messaging (FCM) data pushes that grant temporary Doze exemption windows, and true user-facing clock alarms utilize AlarmManager's setExactAndAllowWhileIdle.""",
    "meta_ar": {
        "id": "BG-06",
        "questionAr": "ما هو وضع Doze وقيود وضع الاستعداد للتطبيقات (App Standby)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم آليات توفير الطاقة في أندرويد (Doze Mode و App Standby Buckets)، ومعرفة تأثيرها على الشبكة والـ WakeLocks، والتعامل السليم معها في WorkManager دون مخالفة سياسات جوجل بلاي.",
        "why_it_matters_ar": "تجاهل قيود Doze Mode يؤدي لفشل المزامنة وتأخر الإشعارات، ومحاولة تجاوزها بطلب استثناء البطارية يؤدي لحذف التطبيق من متجر Google Play.",
        "worked_example_ar": "التعامل مع قيود وضع Doze بالوسائل المعتمدة:\n```kotlin\n// للمهام العادية: تنتظر نافذة الصيانة بسلام وتوفر البطارية\nval normalWork = OneTimeWorkRequestBuilder<SyncWorker>().build()\n// للمهام العاجلة: استخدام Expedited Work لتخطي قيود Doze المؤقتة\nval urgentWork = OneTimeWorkRequestBuilder<MsgWorker>()\n    .setExpedited(OutOfQuotaPolicy.RUN_AS_NON_EXPEDITED_WORK_REQUEST)\n    .build()\n```",
        "trade_offs_ar": "وضع Doze يحمي بطارية الهاتف بشكل جذري، لكنه يؤخر المهام الخلفية غير العاجلة لساعات حتى تفتح نوافذ الصيانة (Maintenance Windows).",
        "failure_modes_ar": "طلب صلاحية `REQUEST_IGNORE_BATTERY_OPTIMIZATIONS` لتطبيق تجارة أو تواصل عادي، مما يسبب رفض التطبيق فوراً في مراجعات متجر جوجل بلاي.",
        "production_perspective_ar": "في المشروعات الكبرى، نعتمد على رسائل FCM فائقة الأهمية (High Priority) لإيقاظ التطبيق مؤقتاً عند وصول رسالة جديدة، ونجعل WorkManager يتولى باقي المعالجة في نافذة الصيانة.",
        "how_to_answer_ar": "اشرح وضع Doze بمرحلتيه (Light و Deep) وسلوك نوافذ الصيانة، ثم وضح فئات App Standby Buckets الخمسة، واشرح كيف يتكيف WorkManager معها برمجياً.",
        "talking_points_ar": "مراحلا Doze Mode (الخفيف والعميق)، ونوافذ الصيانة المتسعة (Maintenance Windows)، وتصنيفات App Standby Buckets، وسياسات متجر جوجل بلاي بشأن البطارية.",
        "follow_ups_ar": "- **المحاور:** \"ماذا يحدث للـ WakeLocks وشبكة الإنترنت أثناء الـ Deep Doze؟\"\n  **المرشح:** \"النظام بيتجاهل أي WakeLock تماماً، وبيقفل اتصال الإنترنت على مستوى جدار الحماية (iptables)، ومفيش أي تطبيق يقدر يتصل بالنت غير لما تفتح نافذة الصيانة.\"\n\n- **المحاور:** \"كيف نرسل تنبيهاً فورياً للمستخدم أثناء تواجد الهاتف في وضع Doze؟\"\n  **المرشح:** \"عبر إرسال High-Priority Data Message من Firebase Cloud Messaging (FCM)؛ دي بتمنح التطبيق نافذة استيقاظ مؤقتة وصغيرة لعرض الإشعار للمستخدم.\""
      ,
        "self_check_ar": "هل فرقت بين Light Doze و Deep Doze؟ هل شرحت نوافذ الصيانة؟ وهل بينت تصنيفات App Standby وموقف جوجل بلاي من تجاوز البطارية؟",
        "references_ar": f"- [Optimize for Doze and App Standby](https://developer.android.com/training/monitoring-device-state/doze-standby) — الدليل الرسمي لتحسين التطبيقات والتعامل مع قيود الطاقة.\n- [App Standby Buckets](https://developer.android.com/topic/performance/app-standby-buckets) — توثيق تصنيف التطبيقات حسب استخدام المستخدم ونسب استهلاك الموارد.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "وضع Doze بيقيد اتصال الإنترنت ويتجاهل الـ WakeLocks ويأجل المهام والمنبهات العادية لما يكون الموبايل مفصولاً عن الشاحن وثابتاً وشاشته مطفية، وبيفتح نوافذ صيانة دورية متباعدة لتشغيل المهام المجمعة. أما App Standby فبيقسم التطبيقات غير المستخدمة لفئات زي Frequent و Rare بناءً على تفاعل المستخدم، ويحدد لكل فئة حصصاً معينة من تشغيل المهام. ومكتبة WorkManager متوافقة طبيعياً مع النظامين وبتأجل المهام العادية لنوافذ الصيانة مع دعم Expedited Work للمهام العاجلة.",
        "best_answer_ar": "وضع Doze وقيود App Standby هما الركيزتان الأساسيتان في نظام أندرويد لحماية البطارية من التطبيقات التي تعمل بشكل عشوائي في الخلفية.\n\nوضع Doze بيشتغل لما الموبايل يكون مفصولاً عن الشحن، ومستقراً بدون حركة، وشاشته مقفولة لفترة. بيشتغل على مرحلتين: الـ Light Doze بيقيد الشبكة مع السماح بالمهام، والـ Deep Doze بيتفعل مع السكون التام، وفيه النظام بيعطل النت تماماً، ويتجاهل أي WakeLock، ويأجل استدعاءات JobScheduler والمنبهات العادية. وبشكل دوري، النظام بيفتح نوافذ صيانة (Maintenance Windows) قصيرة بتتسع فتراتها تدريجياً لتشغيل كل المهام المتراكمة دفعة واحدة قبل ما يرجع ينام تاني.\n\nأما الـ App Standby فبيركز على سلوك المستخدم مع كل تطبيق بشكل منفصل؛ بيقسم التطبيقات لخمس فئات هي Active و Working Set و Frequent و Rare و Restricted. كل ما قل استخدام العميل للتطبيق، النظام بيفرض عليه قيود أشد في عدد مرات تشغيل مهام الخلفية والوصول للشبكة يومياً.\n\nمكتبة WorkManager متوافقة تماماً مع القيود دي؛ فالمهام العادية بتنتظر فتح نوافذ الصيانة لتوفير الشحن، بينما المهام الحساسة بنشغلها عبر Expedited Work للحصول على حصة تنفيذ سريعة.",
        "deep_answer_ar": "تحت الكابوت، فهم كواليس Doze Mode بيحل ألغاز تأخر المهام الخلفية في التطبيقات الكبيرة. لما الموبايل يدخل في Deep Doze، نواة لينكس (Kernel) بتدخل في حالات توفير طاقة عميقة، وبيتم حجب الاتصال بالإنترنت على مستوى جدار حماية iptables لكل التطبيقات بدون استثناء إلا في حالات معينة.\n\nنوافذ الصيانة بتفتح بعد فترات متباعدة بتزيد تدريجياً، يعني ممكن تبدأ بعد ربع ساعة، ثم نصف ساعة، ثم ساعة، وممكن توصل لكذا ساعة لو الموبايل متروك طول الليل. فلو عندك مزامنة عادية، متوقع جداً تتأخر ساعات لحد ما يصحى المستخدم أو تفتح نافذة الصيانة.\n\nكتير من المطورين بيحاولوا يهربوا من القيود دي بطلب استثناء البطارية عبر صلاحية `REQUEST_IGNORE_BATTERY_OPTIMIZATIONS`، وده تصرف كارثي لأن سياسات متجر Google Play صارمة جداً وبتحظر الصلاحية دي للتطبيقات العادية وبترفضها فوراً في المراجعة.\n\nالمهندسون الكبار بيصمموا النظام بالتوافق مع المعايير الرسمية: العمليات العادية بتتسجل في WorkManager وتنتظر نوافذ الصيانة بهدوء، والرسائل الفورية بتتبعت عبر FCM High-Priority Data Messages اللي بتمنح التطبيق نافذة استيقاظ مؤقتة لعرض الإشعار، والتنبيهات الزمنية الحقيقية بتستخدم `setExactAndAllowWhileIdle` في AlarmManager، مما يضمن أداء مستقراً للمشروع بدون استنزاف البطارية أو انتهاك إرشادات وسياسات المتجر وتوفير أفضل تجربة تشغيل ممكنة للمستخدم تلبي احتياجاته بكفاءة وأمان كاملين."
    }
}

# ==========================================
# BG-07: Lifecycle-Bound Work vs Durable Work
# ==========================================
DATA["BG-07"] = {
    "concept_en": """The distinction between lifecycle-bound work and durable work is a cornerstone of robust Android application architecture, defining task survival against screen destruction, process death, and operating system lifecycle events. Lifecycle-bound work is tied to an in-memory component lifecycle—such as a ViewModel via viewModelScope or an Activity/Fragment via lifecycleScope. It executes strictly within the host process memory space and cancels cooperatively when the associated lifecycle transitions to DESTROYED or when the process is reclaimed by the operating system. Conversely, durable work guarantees execution regardless of UI destruction, process termination, or device reboots. It is serialized and persisted to disk (such as via WorkManager's internal SQLite database) and scheduled through platform daemons, ensuring execution under specified environmental constraints.""",
    "walkthrough_en": """Contrasting lifecycle-bound coroutines with durable WorkManager jobs:
```kotlin
// 1. Lifecycle-Bound Work: Transient UI operation (Cancelled if user exits screen)
class UserProfileViewModel(private val repository: UserRepository) : ViewModel() {
    fun updateProfileDisplayName(newName: String) {
        viewModelScope.launch { // CANCELLED if user navigates back before network finishes!
            repository.updateNameOnline(newName)
        }
    }
}

// 2. Durable Work: Guaranteed execution (Survives process death, low memory, and reboot)
fun enqueueDurableProfileUpdate(context: Context, newName: String) {
    // A. Commit intent locally in Room database as PENDING
    // B. Enqueue durable WorkManager request
    val request = OneTimeWorkRequestBuilder<SyncProfileWorker>()
        .setInputData(workDataOf("name" to newName))
        .setConstraints(Constraints.Builder().setRequiredNetworkType(NetworkType.CONNECTED).build())
        .build()

    WorkManager.getInstance(context).enqueueUniqueWork(
        "sync_profile",
        ExistingWorkPolicy.KEEP,
        request // WorkManager persists request to SQLite and executes even after process death
    )
}
```""",
    "short_en": """Lifecycle-bound work runs in memory tied to UI scopes like viewModelScope and cancels when the user navigates away or the process dies. It is suited for immediate presentation operations like loading screen content. Durable work is persisted to disk using WorkManager, surviving UI destruction, low-memory process kills, and device reboots, making it mandatory for business-critical operations like offline sync and uploads.""",
    "structured_en": """The distinction between lifecycle-bound and durable work determines whether an operation survives beyond the immediate presentation lifecycle.
Lifecycle-bound work is hosted entirely within process memory and bound to an Android lifecycle owner. Tasks launched inside viewModelScope or lifecycleScope cancel automatically when their associated View or ViewModel is cleared. This ephemeral execution is ideal for user-driven presentation actions—such as querying an API for list items, debouncing search input, or triggering UI state animations—where completing the operation becomes pointless once the user abandons the screen.
Durable work, by contrast, must execute to completion regardless of user navigation, low-memory process termination, or operating system restarts. WorkManager provides this guarantee by persisting work specifications in an internal Room database and delegating execution to system daemons like JobScheduler.
A fundamental architectural flaw in mobile engineering is executing durable business operations within lifecycle-bound scopes. For example, initiating a checkout payment or file upload solely inside viewModelScope risks data loss if the user backs out of the screen while the network request is in flight.""",
    "deep_senior_en": """Under the hood, conflating lifecycle-bound work with durable work represents one of the most common causes of silent data corruption in Android applications.
When a user taps 'Submit Order' and immediately presses the home button or navigates backward, the Activity and its ViewModel are destroyed. The viewModelScope triggers cancellation of its child coroutines, closing active network sockets mid-transmission. Even worse, if Android's Low Memory Killer (LMK) terminates the application process while an in-memory coroutine is executing, all active threads and memory states vanish instantly without running catch or finally blocks.
To guarantee durability, senior engineers apply the Outbox Pattern. When a mutation occurs, the ViewModel performs an atomic write to the local database, saving the record with a PENDING status. The ViewModel then enqueues a durable WorkManager request before finishing its presentation responsibilities.
Because WorkManager serializes the request to disk before returning from enqueue(), the operation is completely immune to process death. If the process is reclaimed, WorkManager re-spawns a worker via JobScheduler once network connectivity is available, reads the PENDING record from the database, executes the network call, and updates the state.
Staff engineers enforce this boundary across code reviews: UI scopes handle ephemeral observation, while all side-effecting mutations that must reach the server are routed through durable WorkManager pipelines.""",
    "meta_ar": {
        "id": "BG-07",
        "questionAr": "ما الفرق بين العمل المرتبط بدورة الحياة (Lifecycle-Bound) والعمل الدائم (Durable Work)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "التمييز المعماري بين المهام المرتبطة بالواجهة والمهام المستمرة، وإدراك مخاطر تشغيل العمليات الحساسة في viewModelScope، وتطبيق نمط Outbox مع WorkManager لضمان عدم ضياع البيانات.",
        "why_it_matters_ar": "تشغيل عمليات الدفع أو حفظ البيانات داخل scopes مرتبطة بالشاشة يؤدي لضياع المعاملات وفساد البيانات فور خروج المستخدم أو قتل النظام للتطبيق في الخلفية.",
        "worked_example_ar": "مقارنة كود الشاشة بكود المهمة الدائمة:\n```kotlin\n// Lifecycle-bound: يلغى فور الخروج من الشاشة\nviewModelScope.launch { searchItems(query) }\n// Durable: مضمون التنفيذ عبر WorkManager حتى بعد موت الـ Process\nworkManager.enqueueUniqueWork(\"order_sync\", KEEP, orderWorkRequest)\n```",
        "trade_offs_ar": "العمل المرتبط بدورة الحياة سريع وخفيف ولا يستهلك قرص التخزين، بينما العمل الدائم يتطلب كتابة على الـ SQLite وتجهيز Workers لكنه يضمن نجاة البيانات بنسبة 100%.",
        "failure_modes_ar": "تشغيل رفع إيصال الدفع داخل `viewModelScope.launch`؛ فلو ضغط المستخدم زر الرجوع أثناء الرفع، يلغى الكوروتين فوراً ولا يصل الإيصال للسيرفر أبداً.",
        "production_perspective_ar": "في تطبيقات البنوك والنقل، نسجل كل معاملة في Room كمسودة معلقة أولاً، ثم نطلق WorkManager دائم، ونمنع في الـ Code Review أي نداء شبكة يحفظ بيانات داخل viewModelScope.",
        "how_to_answer_ar": "قارن بينهما في: مكان الوجود (الذاكرة مقابل القرص)، ومصير المهمة عند الخروج من الشاشة أو موت الـ Process، واستعرض السيناريوهات المناسبة لكل منهما ونمط Outbox.",
        "talking_points_ar": "فناء الـ viewModelScope مع خروج المستخدم، وموت الـ Process عبر Low Memory Killer، وضمانة التخزين في SQLite، ونمط Outbox للمهام الدائمة.",
        "follow_ups_ar": "- **المحاور:** \"ماذا يحدث لكوروتين شغال في viewModelScope لو المستخدم ضغط زر الرجوع (Back Button)؟\"\n  **المرشح:** \"الـ ViewModel بيتدمر ودالة onCleared بتتنفذ، فالـ viewModelScope بيلغي كل الكوروتينات التابعة له فوراً، وطلب الشبكة بيتقفل في نصه وتضيع العملية.\"\n\n- **المحاور:** \"كيف نضمن عدم ضياع المعاملة لو نظام التشغيل قتل الـ Process فجأة لتوفير الميموري؟\"\n  **المرشح:** \"بحفظ العملية في قاعدة بيانات Room المحلية أولاً كمسودة بحالة PENDING، وجدولة Worker في WorkManager؛ لأن WorkManager بيحفظ الطلب على القرص ويعيد تشغيله تلقائياً بعد استعادة النظام.\""
      ,
        "self_check_ar": "هل وضحت إلغاء viewModelScope عند تدمير الشاشة؟ هل شرحت كيفية نجاة WorkManager عبر التخزين على القرص؟ وهل ذكرت نمط Outbox؟",
        "references_ar": f"- [Android Architecture: WorkManager for Background Work](https://developer.android.com/topic/libraries/architecture/workmanager) — توثيق جوجل للفرق بين مهام الواجهة والمهام الدائمة.\n- [Coroutines and Lifecycle Scopes](https://developer.android.com/topic/libraries/architecture/coroutines#lifecyclescope) — التعامل مع Scopes المرتبطة بدورة حياة الواجهة.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "العمل المرتبط بدورة الحياة (Lifecycle-Bound) بيعيش في رامات التطبيق ومرتبط بدورة حياة الشاشة زي `viewModelScope`، وبيلغى فوراً لو المستخدم خرج من الشاشة أو النظام قفل التطبيق، وده مناسب لعرض البيانات والأنيميشن. أما العمل الدائم (Durable Work) فبيحفظ بياناته في قاعدة بيانات على القرص عبر WorkManager، وبيضمن إنه يتنفذ حتماً حتى لو الشاشة اتقفلت أو الـ Process مات أو الموبايل اتعمل له ريستارت، وده إلزامي للعمليات الحساسة زي الدفع ومزامنة البيانات.",
        "best_answer_ar": "الفرق بين العمل المرتبط بدورة الحياة والعمل الدائم هو الفاصل المعماري بين المهام اللحظية العابرة والمهام الحيوية التي لا يجوز ضياعها تحت أي ظرف.\n\nالعمل المرتبط بدورة الحياة بيشتغل بالكامل داخل ذاكرة الـ Process الحالية، ومرتبط بـ LifecycleOwner معين؛ فالعمليات اللي بنشغلها جوه `viewModelScope` أو `lifecycleScope` بتتلغي تلقائياً أول ما الشاشة تتدمر أو يخرج منها المستخدم. ده سلوك ممتاز لمهام العرض زي جلب تفاصيل منتج أو فلترة قائمة؛ لأن استكمال العملية بعد خروج المستخدم ملوش أي قيمة وبيعتبر إهداراً للموارد.\n\nعلى النقيض تماماً، العمل الدائم هو أي مهمة بيزنس لازم تكتمل بنسبة 100% حتى لو المستخدم قفل التطبيق أو نظام أندرويد قتل الـ Process لتوفير الميموري أو الموبايل طفى واشتغل. مكتبة WorkManager بتقدم الضمانة دي بتسجيل تفاصيل المهمة على القرص في قاعدة بيانات SQLite مدمجة وتفويض تشغيلها لـ JobScheduler.\n\nمن أكبر الأخطاء البرمجية الشائعة هي تشغيل عمليات دفع أو رفع ملفات حساسة داخل `viewModelScope` فقط؛ لأن خروج المستخدم في اللحظة دي بيلغي الكوروتين فوراً ويقطع الاتصال بالسيرفر، مسبباً فقدان البيانات.",
        "deep_answer_ar": "تحت الكابوت، الخلط بين العمل المرتبط بالشاشة والعمل الدائم هو السبب الأول لمشاكل تسريب وفساد البيانات الصامتة في أندرويد. لما المستخدم يضغط على زر تأكيد الشراء ويقفل التطبيق بسرعة، الـ ViewModel بيتدمر فوراً والـ viewModelScope بيلغي الكوروتينات التابعة له ويقفل منافذ السوكت في نص نداء الشبكة.\n\nوالأخطر من كده، لو جهاز الموبايل احتاح رامات ونظام أندرويد شغّل الـ Low Memory Killer (LMK) لقتل الـ Process، كل العمليات اللي شغالة في الذاكرة بتتبخر في جزء من الثانية بدون حتى ما تنفذ بلوكات `finally` لتنظيف الموارد.\n\nعلشان نضمن بقاء المهام الحساسة، المهندسون الكبار بيطبقوا نمط الـ Outbox Pattern؛ فأول ما المستخدم يتخذ إجراء، الـ ViewModel بيكتب العملية داخل قاعدة بيانات Room المحلية في Transaction فورية وبحالة PENDING، وبعدين بيسجل طلب عمل دائم في WorkManager قبل ما يقفل الشاشة.\n\nولأن WorkManager بيكتب الطلب على القرص قبل ما يرجع من دالة `enqueue`، فالمهمة أصبحت محصنة تماماً ضد موت الـ Process. أول ما تتوفر الشروط والشبكة، النظام هيشغل الـ Worker في خلفية مستقرة، يقرأ المعاملة المعلقة من Room، يرسلها للسيرفر، ويحدث الحالة لـ SYNCED.\n\nالمهندسون الكبار بيمنعوا تماماً في مراجعات الكود أي حفظ بيانات أو نداءات شبكة مؤثرة داخل scopes الواجهة، وبيفرضو مسار WorkManager للمهام الحيوية."
    }
}

# ==========================================
# BG-08: Queueing Offline Sync and Retry with WorkManager
# ==========================================
DATA["BG-08"] = {
    "concept_en": """Queueing offline synchronization and retry with WorkManager relies on the Outbox architectural pattern, establishing a reliable transactional bridge between local persistent storage and remote servers. When a user creates or modifies data while offline, the repository immediately commits the mutation to the local Room database within a transaction, assigning the record a pending sync state and a client-generated UUID. The repository then enqueues a unique OneTimeWorkRequest configured with network constraints and exponential backoff retry criteria. When execution conditions are satisfied, the CoroutineWorker retrieves pending mutations, transmits them to the backend with idempotency headers, marks local records as synced upon success, and triggers exponential retries via Result.retry() if network interruptions occur.""",
    "walkthrough_en": """Implementing the Outbox Pattern with WorkManager and Room:
```kotlin
// 1. Room Entity with local sync status tracking
@Entity(tableName = "posts")
data class PostEntity(
    @PrimaryKey val id: String = UUID.randomUUID().toString(),
    val content: String,
    val syncStatus: SyncStatus = SyncStatus.PENDING // PENDING, SYNCED, FAILED
)

// 2. Repository commits locally and schedules unique WorkManager task
class PostRepositoryImpl(
    private val postDao: PostDao,
    private val workManager: WorkManager
) : PostRepository {
    override suspend fun createPost(content: String) {
        val post = PostEntity(content = content, syncStatus = SyncStatus.PENDING)
        postDao.insertPost(post) // 1. Immediate local persistence (SSOT)

        // 2. Enqueue unique durable worker
        val syncRequest = OneTimeWorkRequestBuilder<SyncPostsWorker>()
            .setConstraints(Constraints.Builder().setRequiredNetworkType(NetworkType.CONNECTED).build())
            .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 15, TimeUnit.SECONDS)
            .build()

        workManager.enqueueUniqueWork("sync_posts_work", ExistingWorkPolicy.KEEP, syncRequest)
    }
}

// 3. CoroutineWorker batches pending items and commits status atomically
class SyncPostsWorker(context: Context, params: WorkerParameters) : CoroutineWorker(context, params) {
    override suspend fun doWork(): Result = withContext(Dispatchers.IO) {
        val dao = AppDatabase.getInstance(applicationContext).postDao()
        val api = NetworkClient.api
        val pendingPosts = dao.getPendingPosts()

        if (pendingPosts.isEmpty()) return@withContext Result.success()

        runCatching {
            pendingPosts.forEach { post ->
                api.uploadPost(PostDto(id = post.id, content = post.content)) // Idempotent by UUID!
                dao.updateSyncStatus(post.id, SyncStatus.SYNCED)
            }
            Result.success()
        }.getOrElse { Result.retry() } // Triggers exponential backoff on network failure
    }
}
```""",
    "short_en": """Queue offline synchronization using the Outbox pattern: save the mutation to the local Room database immediately with a PENDING state and unique UUID, then enqueue a unique WorkManager request with a connected network constraint and exponential backoff. The worker reads pending items, posts them to the API idempotently, marks them as SYNCED upon success, and returns Result.retry on network errors.""",
    "structured_en": """Implementing robust offline synchronization requires combining local persistence with durable WorkManager background execution through the Outbox pattern.
The workflow begins at the data layer. When a user performs an action—such as submitting an order or creating a comment—the repository writes the record directly to the local Room database inside an atomic transaction. The record is flagged with a sync status of PENDING and stamped with a client-generated UUID. This delivers immediate, zero-latency feedback to the UI.
Next, the repository enqueues a OneTimeWorkRequest using unique work scheduling with ExistingWorkPolicy.KEEP. The request configures a network constraint requiring NetworkType.CONNECTED and sets an exponential backoff policy starting at fifteen seconds.
When network connectivity becomes available, WorkManager executes the worker on a background dispatcher. The worker queries Room for all PENDING mutations, batches them to the backend API, and attaches each record's UUID as an idempotency key.
Upon receiving a successful HTTP response, the worker updates the local Room entities to SYNCED. If the network call throws an IOException or the server returns a temporary error, the worker returns Result.retry(), prompting WorkManager to back off exponentially before re-attempting.""",
    "deep_senior_en": """Under the hood, executing offline synchronization across distributed mobile networks requires solving synchronization race conditions, payload batching, and server idempotency.
A critical architectural trap is attempting to pass large mutation payloads directly inside WorkManager's Data object via setInputData(). The WorkManager Data container is constrained by Android Binder transaction buffer limits (strictly capped at 10KB total). Passing large JSON strings or image byte arrays triggers an IllegalStateException or fatal TransactionTooLargeException.
Instead, the Outbox pattern uses WorkManager purely as an execution trigger. The actual data payload resides safely inside the persistent Room SQLite database. The worker simply wakes up, queries the database for pending records, processes the batch, and updates local rows transactionally.
Furthermore, because mobile network connections frequently drop mid-transmission, a worker might successfully send data to the backend but crash or disconnect before receiving the HTTP 200 response. When WorkManager retries, the worker will submit the exact same mutation again.
Staff engineers guarantee transactional safety by designing idempotent backend APIs. The client-generated UUID assigned during the initial Room insert acts as an Idempotency-Key header in the HTTP request. When the server encounters a duplicate UUID, it returns the cached success response rather than creating a duplicate database record, ensuring flawless data integrity under erratic network conditions.""",
    "meta_ar": {
        "id": "BG-08",
        "questionAr": "كيف تدير طابور المزامنة دون إنترنت (Offline Sync) وإعادة المحاولة عبر WorkManager؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "إتقان تطبيق نمط Outbox Pattern، واستخدام Room كقاعدة انطلاق للمزامنة، وتجنب فخ حدود Binder Data في WorkManager (حد الـ 10KB)، وتصميم استدعاءات شبكة تدعم Idempotency.",
        "why_it_matters_ar": "تمرير بيانات ضخمة في InputData يسبب TransactionTooLargeException وانهيار التطبيق، والافتقار لـ Idempotency يسبب تكرار إنشاء البيانات في السيرفر عند إعادة المحاولة.",
        "worked_example_ar": "تطبيق نمط Outbox:\n```kotlin\n// 1. الحفظ في Room كـ PENDING\npostDao.insert(post.copy(syncStatus = PENDING))\n// 2. جدولة WorkManager بمحدد النت والتراجع الأسي\nval req = OneTimeWorkRequestBuilder<SyncWorker>()\n    .setConstraints(Constraints.Builder().setRequiredNetworkType(CONNECTED).build())\n    .setBackoffCriteria(EXPONENTIAL, 15, SECONDS).build()\nworkManager.enqueueUniqueWork(\"sync_outbox\", KEEP, req)\n```",
        "trade_offs_ar": "نمط Outbox يضمن استقرار البيانات بنسبة 100% ودعم العمل بدون إنترنت، لكنه يتطلب إدارة حالات المزامنة في قاعدة البيانات وتصميم APIs تدعم Idempotency.",
        "failure_modes_ar": "محاولة تمرير JSON أو صور في `setInputData` الخاصة بـ WorkManager، مما يؤدي لانهيار التطبيق بـ `IllegalStateException` لتجاوز حد الـ 10 كيلوبايت.",
        "production_perspective_ar": "في المشروعات الكبرى، نرسل في كل طلب شبكة ترويسة `Idempotency-Key: <UUID>`، ونستخدم Transaction واحدة في Room لتحديث حالة العناصر دفعة واحدة بعد نجاح الاتصال.",
        "how_to_answer_ar": "اشرح نمط Outbox: الحفظ المحلي الفوري في Room بحالة PENDING، وجدولة Unique Work مع محدد الشبكة وتراجع أسي، وحذر من تمرير بيانات ضخمة في InputData، ووضح الـ Idempotency.",
        "talking_points_ar": "نمط Outbox Pattern، وتفادي فخ الـ 10KB في WorkManager Data، وترويسة Idempotency-Key، وسياسة ExistingWorkPolicy.KEEP، والمعاملات الذرية في Room.",
        "follow_ups_ar": "- **المحاور:** \"لماذا لا نمرر كائن البيانات المراد رفعه مباشرة داخل `setInputData` في WorkManager؟\"\n  **المرشح:** \"لأن كائن Data في WorkManager مقيد بذاكرة الـ Binder بحد أقصى 10 كيلوبايت فقط، وتجاوزها يسبب كراش `TransactionTooLargeException`؛ والأصح تخزين البيانات في Room واستخدام Worker كمشغل فقط.\"\n\n- **المحاور:** \"كيف تمنع تكرار إنشاء البوست في السيرفر لو النت قطع بعد وصول الطلب وقبل استلام الرد؟\"\n  **المرشح:** \"عن طريق توليد UUID في الموبايل عند إنشاء البوست وإرساله في ترويسة `Idempotency-Key`؛ فلو الـ Worker أعاد المحاولة، السيرفر بيتعرف على الـ UUID ويرجع نجاح بدون تكرار الحفظ.\""
      ,
        "self_check_ar": "هل شرحت نمط Outbox؟ هل حذرت من حد الـ 10KB في InputData؟ وهل وضحت دور UUID و Idempotency في منع التكرار؟",
        "references_ar": f"- [Android offline-first data layer](https://developer.android.com/topic/architecture/data-layer/offline-first) — الدليل الرسمي لبناء تطبيقات تدعم العمل دون اتصال بالإنترنت.\n- [WorkManager Input/Output Data](https://developer.android.com/topic/libraries/architecture/workmanager/how-to/define-work#input_data) — توثيق حدود وتفاصيل تمرير البيانات في WorkManager.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "بندير طابور المزامنة دون إنترنت بتطبيق نمط Outbox Pattern: أول ما المستخدم يكتب بيانات، بنحفظها فوراً في قاعدة بيانات Room المحلية بحالة PENDING ومفتاح UUID فريد لإعطاء تجربة فورية وسريعة للواجهة. بعدين بنجدول طلب عمل فريد في WorkManager بمحدد توفر الإنترنت وسياسة Exponential Backoff. لما النت يرجع، الـ Worker بيقرأ العمليات المعلقة من Room ويرسلها للسيرفر بترويسة Idempotency-Key، وأول ما ينجح بيحدث حالتها في Room لـ SYNCED، ولو النت فصل بيرجع Result.retry لتكرار المحاولة تدريجياً.",
        "best_answer_ar": "إدارة المزامنة عند انقطاع الإنترنت بتتطلب الربط المتين بين التخزين المحلي والجدولة الدائمة عبر نمط الـ Outbox Pattern.\n\nالبداية بتكون في طبقة البيانات؛ لما المستخدم يعمل إجراء زي كتابة تعليق أو طلب شراء والإنترنت مقطوع، الـ Repository بيكتب البيانات فوراً داخل قاعدة بيانات Room المحلية داخل Transaction ذرية. السجل بيتسجل بحالة PENDING ومعاه معرف فريد UUID متولد على الموبايل، وبكده الواجهة بتعرض التعديل فورياً بدون أي شاشات تحميل أو أخطاء.\n\nبعد الحفظ المحلي، الـ Repository بيجدول طلب OneTimeWorkRequest فريد باستخدام سياسة `ExistingWorkPolicy.KEEP`، مع اشتراط توفر اتصال إنترنت، وسياسة تراجع أسي تبدأ من 15 ثانية.\n\nأول ما الإنترنت يرجع، WorkManager بيشغل الـ Worker في الخلفية. الـ Worker بيفتح قاعدة بيانات Room ويجلب كل السجلات اللي حالتها PENDING، ويرسلها للسيرفر كدفعة واحدة مع إرفاق الـ UUID في الـ Headers.\n\nلو الرد رجع بنجاح 200، الـ Worker بيحدث حالة السجلات في Room لـ SYNCED فتنتهي المهمة. ولو حصل انقطاع في الشبكة، الـ Worker بيرجع `Result.retry()`، ونظام WorkManager بيتولى تأخير المحاولة التالية تصاعدياً لحماية البطارية والسيرفر.",
        "deep_answer_ar": "تحت الكابوت، بناء معمارية مزامنة قوية عبر شبكات الموبايل المتقلبة بيتطلب تجنب مصائد خطيرة في نقل البيانات وتكرار المعاملات. من أشهر الأخطاء القاتلة هي محاولة تمرير البيانات المطلوب رفعها جوه كائن `Data` في WorkManager عبر `setInputData`؛ لأن الكائن ده بيمر عبر الـ Binder ومقيد بسعة 10 كيلوبايت فقط، وتجاوزها بيرمي فوراً `TransactionTooLargeException` ويكرش التطبيق.\n\nنمط Outbox بيتفادى الفخ ده تماماً؛ لأن WorkManager بيستخدم فقط كمنبه تشغيل (Trigger)، بينما البيانات الحقيقية مخزنة بأمان داخل جداول Room SQLite على القرص. الـ Worker أول ما يصحى بيستعلم من قاعدة البيانات ويعالج الدفعة في مسار خلفي.\n\nالمعضلة التانية هي انقطاع النت في اللحظة الحرجة: الـ Worker يبعت البيانات للسيرفر والسيرفر يسجلها، لكن النت يفصل قبل ما الموبايل يستلم رد HTTP 200! في الحالة دي، WorkManager هيعتبر العملية فشلت ويعيد تشغيل الـ Worker، وممكن يرفع البوست أو يخصم المبلغ مرتين.\n\nالمهندسون الكبار بيحلوا المعضلة دي بتصميم APIs تدعم الـ Idempotency؛ الـ UUID اللي اتولد في Room أول مرة بيتبعت في ترويسة `Idempotency-Key`. لما السيرفر يستقبل نفس الـ UUID في المحاولة التانية، بيكتشف إنه اتسجل مسبقاً، فبيرجع كود نجاح فوراً بدون تكرار الحفظ في الداتابيز، وده بيضمن سلامة البيانات بنسبة مئة بالمئة."
    }
}

# ==========================================
# BG-09: Cancelling or Replacing Unique Background Work
# ==========================================
DATA["BG-09"] = {
    "concept_en": """Cancelling or replacing unique background work in WorkManager involves coordinating unique naming identifiers, ExistingWorkPolicy replacement strategies, explicit cancellation APIs, and cooperative cancellation in workers. WorkManager provides cancelUniqueWork(uniqueWorkName), cancelWorkById(id), and cancelAllWorkByTag(tag) to abort pending or running jobs, transitioning their state to CANCELLED. To atomically supersede an ongoing background pipeline with fresh data, developers enqueue a unique work request using ExistingWorkPolicy.REPLACE. When work is cancelled or replaced, WorkManager signals cooperative cancellation: in CoroutineWorker, the underlying CoroutineScope is cancelled, causing suspending functions to throw CancellationException, while standard Workers must check isStopped or implement onStopped() to perform resource cleanup.""",
    "walkthrough_en": """Cancelling, replacing, and cooperatively handling work stoppage:
```kotlin
// 1. Atomically replacing an ongoing unique work request with new parameters
fun replaceSearchIndexSync(context: Context, newQueryFilter: String) {
    val newRequest = OneTimeWorkRequestBuilder<IndexSyncWorker>()
        .setInputData(workDataOf("filter" to newQueryFilter))
        .build()

    // Atomically cancels any active/pending sync and enqueues the fresh request immediately
    WorkManager.getInstance(context).enqueueUniqueWork(
        "search_index_sync",
        ExistingWorkPolicy.REPLACE,
        newRequest
    )
}

// 2. Explicit cancellation by unique name or tag
fun stopAllSyncJobs(context: Context) {
    val workManager = WorkManager.getInstance(context)
    workManager.cancelUniqueWork("search_index_sync") // Aborts the unique pipeline
    workManager.cancelAllWorkByTag("analytics_tag")   // Aborts all tasks matching tag
}

// 3. Cooperative cancellation handling inside CoroutineWorker
class IndexSyncWorker(context: Context, params: WorkerParameters) : CoroutineWorker(context, params) {
    override suspend fun doWork(): Result = withContext(Dispatchers.IO) {
        try {
            while (hasMoreData()) {
                // If work is cancelled or replaced, yield() checks cancellation and throws CancellationException!
                yield()
                processNextBatch()
            }
            Result.success()
        } finally {
            // Clean up resources, close file streams, delete temp files on cancellation
            cleanupTemporaryFiles()
        }
    }
}
```""",
    "short_en": """Cancel background work using cancelUniqueWork, cancelWorkById, or cancelAllWorkByTag. To atomically replace active work with updated tasks, enqueue a unique work request using ExistingWorkPolicy.REPLACE. In CoroutineWorker, cancellation propagates automatically by cancelling its CoroutineScope, which causes suspending functions to throw CancellationException and allows cleanup inside finally blocks.""",
    "structured_en": """Managing the cancellation and replacement of background tasks in WorkManager requires understanding unique work policies, cancellation APIs, and cooperative worker cleanup.
To abort scheduled or executing tasks, WorkManager provides explicit cancellation methods including cancelUniqueWork by unique name, cancelWorkById by UUID, and cancelAllWorkByTag by tag. When invoked, WorkManager transitions the work status to CANCELLED in its internal database and ceases future execution.
To update an ongoing operation without writing complex cancellation logic, developers utilize ExistingWorkPolicy.REPLACE when calling enqueueUniqueWork. This atomically cancels any pending or currently executing instance of the named task and enqueues the new work request immediately. This pattern is ideal for search indexing, location tracking, or draft autosaving where newer data renders older tasks obsolete.
Crucially, cancellation in WorkManager is cooperative. When a job is cancelled, WorkManager signals the running worker to stop. In CoroutineWorker, the task's CoroutineScope is cancelled, causing active suspending functions to throw CancellationException. Workers should use try-finally blocks to release file handles, close database connections, and delete transient cache files.""",
    "deep_senior_en": """Under the hood, handling background cancellation requires addressing race conditions between operating system process lifecycles and background worker threads.
When you call cancelUniqueWork() or trigger ExistingWorkPolicy.REPLACE, WorkManager immediately updates the task's state to CANCELLED inside its internal SQLite database. However, if the worker is actively executing code on a background thread, Java cannot forcibly terminate the thread without risking memory corruption.
Consequently, execution stoppage relies entirely on cooperative cancellation. In a traditional Worker, developers must periodically inspect the boolean flag isStopped. If isStopped returns true, the worker must exit its execution loop and return Result.failure() or Result.retry(). Failure to check isStopped results in a zombie worker that continues consuming battery and CPU cycles in the background despite being marked as cancelled in the database.
In contrast, CoroutineWorker integrates natively with Kotlin's cooperative cancellation model. When cancellation occurs, the underlying Job transitions to Cancelling. Calling standard suspending functions like delay, withContext, or explicitly invoking yield() checks the active job status and immediately raises CancellationException.
Furthermore, WorkManager provides the onStopped() callback, which is invoked regardless of which worker subclass you use.
Staff engineers leverage onStopped() or finally blocks to clean up partially written disk files, abort HTTP multipart uploads, and release camera or sensor locks, ensuring that background cancellations never leave the application in an inconsistent state.""",
    "meta_ar": {
        "id": "BG-09",
        "questionAr": "كيف تلغي أو تستبدل المهام الخلفية الفريدة (Unique Background Work)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "إتقان استخدام دوال الإلغاء في WorkManager، وفهم سياسة ExistingWorkPolicy.REPLACE، وتطبيق الإلغاء التعاوني (Cooperative Cancellation) والتنظيف عبر finally و onStopped.",
        "why_it_matters_ar": "عدم التعامل مع الإلغاء التعاوني يترك Workers معلقة (Zombie Workers) تستهلك البطارية والذاكرة رغم إلغائها في قاعدة البيانات.",
        "worked_example_ar": "إلغاء واستبدال المهمة والتنظيف في finally:\n```kotlin\n// استبدال ذري بمهمة جديدة\nworkManager.enqueueUniqueWork(\"sync\", ExistingWorkPolicy.REPLACE, newReq)\n// إلغاء صريح\nworkManager.cancelUniqueWork(\"sync\")\n// تنظيف الموارد في CoroutineWorker\ntry { process() } finally { cleanTempFiles() }\n```",
        "trade_offs_ar": "استبدال المهمة بـ REPLACE يضمن حداثة البيانات فوراً، لكنه يلغي أي تقدم محرز في المهمة السابقة ما لم تكن تدعم استئناف التحميل المتقطع.",
        "failure_modes_ar": "تجاهل فحص `isStopped` أو ابتلاع `CancellationException` في CoroutineWorker عبر `catch (e: Exception)`، مما يمنع إلغاء المهمة وتظل تعمل في الخلفية دون جدوى.",
        "production_perspective_ar": "في تطبيقات الميديا، نستخدم `ExistingWorkPolicy.REPLACE` عند تغيير جودة الفيديو، ونحذف أجزاء الملفات المؤقتة داخل بلوك `finally` فور استلام إشارة الإلغاء لمنع امتلاء مساحة الهاتف.",
        "how_to_answer_ar": "وضح شقين: استبدال المهام ذرياً عبر `ExistingWorkPolicy.REPLACE` أو إلغائها عبر `cancelUniqueWork`، وشق الإلغاء التعاوني في الـ Worker وكيفية تنظيف الملفات المؤقتة.",
        "talking_points_ar": "دوال الإلغاء الصريح، وسياسة ExistingWorkPolicy.REPLACE الذرية، والإلغاء التعاوني (Cooperative Cancellation)، واستثناء CancellationException، وتنظيف الموارد عبر finally و onStopped.",
        "follow_ups_ar": "- **المحاور:** \"ماذا يحدث لو قمت بعمل `catch (e: Exception)` عام داخل doWork في CoroutineWorker؟\"\n  **المرشح:** \"لو بلعت الـ Exception بدون إعادة رمي `CancellationException`، الكوروتين مش هيعرف إنه اتلغى، والـ Worker هيفضل شغال ويضيع ميزة الإلغاء التعاوني الذكي.\"\n\n- **المحاور:** \"ما هو الـ Zombie Worker وكيف نتفاداه في Worker العادي؟\"\n  **المرشح:** \"هو Worker ملغي في الداتابيز لكنه لسه شغال وبيستهلك بطارية؛ وبنتفاداه بفحص `isStopped` دورياً جوه حلقة التكرار أو استخدام CoroutineWorker اللي بيدعم ده تلقائياً.\""
      ,
        "self_check_ar": "هل شرحت دوال الإلغاء؟ هل وضحت سياسة REPLACE؟ وهل بينت آلية الإلغاء التعاوني واستثناء CancellationException؟",
        "references_ar": f"- [Cancelling Work in WorkManager](https://developer.android.com/topic/libraries/architecture/workmanager/how-to/cancel-work) — التوثيق الرسمي لإلغاء وتتبع حالة المهام الخلفية.\n- [Kotlin Coroutines Cancellation](https://kotlinlang.org/docs/cancellation-and-timeouts.html) — الدليل الرسمي للإلغاء التعاوني واستثناء CancellationException.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "بنلغي المهام الخلفية باستخدام `cancelUniqueWork` بالاسم، أو `cancelWorkById` بالمعرف، أو `cancelAllWorkByTag` بالوسم. ولو عاوزين نستبدل مهمة شغالة بمهمة أحدث فوراً، بنستخدم سياسة `ExistingWorkPolicy.REPLACE` اللي بتلغي القديمة ذرياً وتشغل الجديدة في نفس اللحظة. وفي الـ CoroutineWorker، الإلغاء بيتم تعاونياً بإلغاء الـ CoroutineScope ورمي `CancellationException` في الدوال المعلقة، فبنقدر ننظف الموارد والملفات المؤقتة داخل بلوك `finally`.",
        "best_answer_ar": "إدارة إلغاء واستبدال المهام في WorkManager بتتطلب التنسيق بين دوال الإلغاء وسياسات العمل الفريد وآلية الإلغاء التعاوني في الكود.\n\nلو عاوز تلغي مهمة بشكل صريح، WorkManager بيوفر دوال زي `cancelUniqueWork` بالاسم الفريد، أو `cancelWorkById` بالـ UUID، أو `cancelAllWorkByTag` لمجموعة مهام تشترك في وسم معين. أول ما بتناديها، حالة المهمة في قاعدة البيانات بتتحول فوراً لـ CANCELLED.\n\nأما لو الهدف هو تحديث مهمة شغالة ببيانات جديدة، الأسلوب الأمثل هو استخدام سياسة `ExistingWorkPolicy.REPLACE` عند استدعاء `enqueueUniqueWork`. السياسة دي بتلغي أي مهمة قائمة أو معلقة وتحط المهمة الجديدة مكانها بشكل ذري فوري، وده مثالي لتحديث فهارس البحث أو حفظ المسودات لتفادي العمل على داتا قديمة.\n\nالنقطة الأهم هي إن الإلغاء في أندرويد بيتم بشكل تعاوني (Cooperative Cancellation)؛ النظام مبيقدرش يقتل الثريد بالقوة علشان ميحصلش فساد في الذاكرة. في الـ CoroutineWorker، أول ما المهمة تتلغي، الـ CoroutineScope بيتلغي ويرمي `CancellationException` في أي دالة معلقة شغالة، وده بيسمح بكتابة كود تنظيف في بلوك `finally` لحذف الملفات المؤقتة وقفل الاتصالات.",
        "deep_answer_ar": "تحت الكابوت، التعامل مع إلغاء المهام الخلفية بيتطلب وعياً كاملاً بالفارق بين حالة المهمة في الداتابيز وما يحدث فعلياً على مستوى الثريدات. لما تستدعي `cancelUniqueWork()`، الـ WorkManager بيسجل فوراً في قاعدة بيانات SQLite إن المهمة اتلغت، لكن الثريد اللي بينفذ الكود بيفضل شغال إلا لو الكود تعاون مع الإلغاء.\n\nفي كلاس الـ Worker العادي، مفيش طريقة سحرية لإيقاف الثريد؛ المطور لازم يفحص المتغير `isStopped` داخل حلقات التكرار، ولو أهمله، الـ Worker هيتحول لـ Zombie Worker يفضل يسحب بطارية ورامات لحد ما يخلص مع إنه ملغي في النظام!\n\nأما في CoroutineWorker، التوافق مع Kotlin Coroutines بيخلي العملية تلقائية ومحكمة. إلغاء المهمة بيلغي الـ Job التابع للكوروتين، فلو الكود بينادي دوال معلقة زي `delay` أو استدعاءات شبكة، أو حتى نادى `yield()` في حلقة التكرار، هيرمي فوراً `CancellationException`.\n\nمن أخطر الأخطاء هنا كتابة `catch (e: Exception)` بدون إعادة رمي `CancellationException`؛ لأن ده بيبتلع إشارة الإلغاء ويخلي الكوروتين يكمل شغله بدون ما يتوقف!\n\nبالإضافة لده، دالة `onStopped()` بتتنفذ دائماً عند إلغاء أي Worker. المهندسون الكبار بيستخدموها بالاشتراك مع بلوكات `finally` لمسح أجزاء الملفات المحملة جزئياً، وإلغاء رفع الصور الكبيرة، وتحرير الموارد لضمان نظافة النظام تماماً."
    }
}


def main():
    print(f"Elevating {len(DATA)} questions in BG (BG-01 to BG-09)...")
    for qid, data in DATA.items():
        ee.update_canonical_question(
            qid=qid,
            concept_en=data["concept_en"],
            walkthrough_en=data["walkthrough_en"],
            short_en=data["short_en"],
            structured_en=data["structured_en"],
            deep_senior_en=data["deep_senior_en"]
        )

    # Save metadata for this batch
    ee.save_topic_metadata("bg_01_09", {qid: d["meta_ar"] for qid, d in DATA.items()})

    # Merge into main metadata
    ee.merge_all_metadata()

    # Validate each question
    all_ok = True
    for qid in DATA:
        errs = ee.validate_question(qid)
        if errs:
            print(f"❌ {qid} validation errors:")
            for e in errs:
                print(f"   - {e}")
            all_ok = False
        else:
            print(f"✅ {qid} passed validation with 0 errors!")

    if all_ok:
        print("\nAll 9 BG questions (BG-01 to BG-09) successfully elevated and passed validation!")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
