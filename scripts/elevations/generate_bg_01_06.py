#!/usr/bin/env python3
"""Generator for BG-01 through BG-06 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "bg.json"

BG_01_06 = [
    {
        "id": "BG-01",
        "arabic_explanation": (
            "متى تختار Coroutines، أو WorkManager، أو Foreground Service، أو AlarmManager في Android؟\n\n"
            "1. شجرة اتخاذ القرار المعماري (Decision Tree Matrix):\n   - **Kotlin Coroutines (`viewModelScope` / `lifecycleScope`)**:\n     * **طبيعة العمل**: عمل غير متزامن فوري مرتبط بدورة حياة الشاشة (Immediate In-Process Work).\n     * **أمثلة**: جلب بيانات لعرضها في الشاشة، تصفية قائمة محلياً، أو استجابة لضغطة زر أثناء تواجد المستخدم في الشاشة.\n     * **مصيره عند خروج المستخدم**: يُلغى فوراً مع انتهاء الـ Scope (لا يعيش بعد تدمير الشاشة أو موت الـ Process).\n   - **WorkManager (العمل المستمر الموثوق - Persistent / Deferrable Work)**:\n     * **طبيعة العمل**: عمل يجب تنفيذه حتماً حتى لو أغلق المستخدم التطبيق، أو مات الـ Process، أو أعيد تشغيل الهاتف (Survives Process Death & Device Reboot).\n     * **أمثلة**: مزامنة التعديلات غير المتصلة (Offline Sync)، رفع سجلات الأخطاء (Log Upload)، ضغط وتصدير تقرير، أو تنزيل تحديث بيانات دوري.\n     * **شروطه**: يقبل التأجيل (Deferrable)، ويخضع لقيود النظام (مثل توفر الإنترنت أو الشاحن).\n   - **Foreground Service (الخدمة الأمامية - User-Perceived Long-Running Work)**:\n     * **طبيعة العمل**: مهمة مستمرة طويلة الأمد يدركها المستخدم بنشاط وتتطلب إشعاراً دائماً لا يمكن إزالته.\n     * **أمثلة**: تشغيل الموسيقى في الخلفية، الملاحة بـ GPS خطوة بخطوة (Turn-by-turn Navigation)، مكالمة فيديو، أو تسجيل الصوت.\n   - **AlarmManager (التنبيهات اللحظية الدقيقة - Exact Time-Sensitive Triggers)**:\n     * **طبيعة العمل**: إيقاظ الجهاز عند ثانية محددة في المستقبل.\n     * **أمثلة**: منبه الاستيقاظ، تنبيه موعد الدواء، أو تذكير التقويم.\n     * **تحذير**: لا يُستخدم للـ Network Polling أو المزامنة الدورية؛ بل لتنبيه المستخدم فقط ويتطلب صلاحية `SCHEDULE_EXACT_ALARM`."
        ),
        "practical_walkthrough": (
            "المقارنة العملية بالكود لاختيار الأداة المناسبة حسب طبيعة المهمة:\n"
            "```kotlin\n"
            "// 1. Coroutines: عمل فوري مرتبط بالشاشة فقط:\n"
            "class SearchViewModel : ViewModel() {\n"
            "    fun onSearchQuery(query: String) {\n"
            "        viewModelScope.launch { // يُلغى تلقائياً لو خرج المستخدم من الشاشة\n"
            "            val results = searchApi.query(query)\n"
            "            _uiState.value = results\n"
            "        }\n"
            "    }\n"
            "}\n"
            "\n"
            "// 2. WorkManager: عمل دائم يجب أن يكتمل حتماً حتى لو أُغلق التطبيق:\n"
            "fun scheduleLogUpload(context: Context) {\n"
            "    val uploadRequest = OneTimeWorkRequestBuilder<UploadLogsWorker>()\n"
            "        .setConstraints(Constraints.Builder().setRequiredNetworkType(NetworkType.CONNECTED).build())\n"
            "        .build()\n"
            "    WorkManager.getInstance(context).enqueueUniqueWork(\"upload_logs\", ExistingWorkPolicy.KEEP, uploadRequest)\n"
            "}\n"
            "\n"
            "// 3. AlarmManager: إيقاظ الهاتف في وقت محدد بالثانية لمنبه حقيقي:\n"
            "fun setExactAlarm(context: Context, triggerAtMillis: Long, pendingIntent: PendingIntent) {\n"
            "    val alarmManager = context.getSystemService(AlarmManager::class.java)\n"
            "    alarmManager.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, triggerAtMillis, pendingIntent)\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Use coroutines (viewModelScope) for immediate UI-bound work that dies with the screen. Use WorkManager for persistent, deferrable background tasks that must survive app exit and reboots. Use Foreground Services for long-running tasks the user is actively aware of with a persistent notification (audio, navigation). Use AlarmManager only for exact, second-precise user alarms.",
        "best_answer": (
            "Selecting the correct background mechanism in Android hinges on two questions: **Is the work tied to the UI lifecycle?** and **Is the timing second-exact or deferrable?**\n\n"
            "1. **Coroutines (`viewModelScope` / `lifecycleScope`)**: Designed for immediate, ephemeral in-process execution. If the user navigates away or the app process is reclaimed, the coroutine is cancelled. Perfect for UI data fetching, query debouncing, and local calculations.\n\n"
            "2. **WorkManager**: The default engine for persistent, deferrable background execution. Guarantees execution even if the app exits, the process dies, or the device reboots. Work requests are persisted in an internal SQLite database and executed via system `JobScheduler` respecting Doze mode and OS power constraints. Essential for offline sync, analytics uploading, and background database pruning.\n\n"
            "3. **Foreground Service**: Reserved exclusively for long-running operations the user is actively conscious of, mandated by a persistent status bar notification. Strictly categorized by `foregroundServiceType` in modern Android (e.g. `mediaPlayback`, `location`, `phoneCall`).\n\n"
            "4. **AlarmManager**: Intended exclusively for clock-exact calendar reminders and wake-up alarms (`setExactAndAllowWhileIdle`). Never use AlarmManager for periodic data sync or network polling."
        ),
        "deep_answer": (
            "Modern Android OS restrictions (Android 12+ / 14+) enforce strict limitations on these APIs:\n\n"
            "- **Foreground Service Background-Start Restrictions**: Starting a Foreground Service from the background is heavily blocked on Android 12+ (throws `ForegroundServiceStartNotAllowedException`), except for narrow exemptions (FCM high-priority push, user click on a widget, or companion device pairing).\n\n"
            "- **WorkManager Expedited Jobs**: For tasks that cannot wait for idle windows (e.g. sending a critical chat message or processing a payment receipt), WorkManager provides **Expedited Work** (`setExpedited(OutOfQuotaPolicy.RUN_AS_NON_EXPEDITED_WORK_REQUEST)`). On older APIs it runs as a foreground service, while on Android 12+ it leverages platform JobScheduler expedited quotas without user-visible notification boilerplate."
        ),
        "follow_ups": [
            {
                "question": "Can WorkManager execute a task every 5 seconds?",
                "answer": "No. PeriodicWorkRequest enforces a hard platform minimum interval of 15 minutes to preserve device battery."
            },
            {
                "question": "What happens to a coroutine launched in `GlobalScope` when the process dies?",
                "answer": "It dies immediately. `GlobalScope` does not survive Android process death; it only outlives the active Activity while the process is warm."
            }
        ]
    },
    {
        "id": "BG-02",
        "arabic_explanation": (
            "ما هي مكتبة WorkManager، وما هي الضمانات الحقيقية والحدود التقنية التي تقدمها في Android؟\n\n"
            "1. ما هي مكتبة WorkManager؟\n   - هي جزء من مكتبات Android Jetpack، وهي الحل القياسي المعتمد رسمياً من Google لجدولة المهام الخلفية القابلة للتأجيل (Deferrable) والتي تتطلب تنفيذاً مضموناً (Guaranteed Execution).\n   - تعمل كطبقة تجريد ذكية: تختار تحت الغطاء أفضل مشغل نظام متاح بناءً على إصدار Android:\n     * على Android 5.0+ (API 21+): تستخدم `JobScheduler` المدمج في النظام.\n     * توفر حماية ذاتية عبر قاعدة بيانات SQLite داخلية لتسجيل المهام وحالاتها.\n\n"
            "2. ما هي الضمانات الحقيقية التي تقدمها (True Guarantees)؟\n   - **ضمان الاستمرارية (Persistence Guarantee)**: إذا تم تسجيل المهمة عبر `enqueue()`, فإنها تُحفظ في ملف SQLite محلي. إذا مات الـ Process، أو نفدت بطارية الهاتف وأعيد تشغيل الجهاز (Reboot)، سيقوم WorkManager باستعادة المهمة وتنفيذها تلقائياً فور توفر الشروط.\n   - **احترام قيود النظام (Constraints Execution)**: تضمن عدم تشغيل المهمة إلا عند تحقق الشروط المحددة (مثل: `NetworkType.CONNECTED`, `RequiresCharging`, `RequiresBatteryNotLow`).\n\n"
            "3. ما هي الأشياء التي لا تضمنها WorkManager إطلاقاً (Non-Guarantees)؟\n   - **لا تضمن التوقيت الدقيق بالثانية (Not Exact-Time)**: إذا طلبت تشغيل مهمة بعد 10 دقائق، فقد يشغلها النظام بعد 12 أو 18 دقيقة حسب حالة الـ Doze Mode والبطارية.\n   - **لا تضمن التنفيذ لمرة واحدة فقط على السيرفر (At-Least-Once, Not Exactly-Once)**: إذا انقطع الاتصال أو حدث Crash في منتصف المهمة، قد يُعاد تشغيل الـ Worker، مما يتطلب أن تكون العملية Idempotent على السيرفر."
        ),
        "practical_walkthrough": (
            "بناء مهمة WorkManager مضمونة مع قيود النظام ومعالجة إعادة المحاولة:\n"
            "```kotlin\n"
            "// 1. تعريف الـ Worker باستخدام CoroutineWorker:\n"
            "class SyncAnalyticsWorker(\n"
            "    context: Context,\n"
            "    params: WorkerParameters\n"
            ") : CoroutineWorker(context, params) {\n"
            "\n"
            "    override suspend fun doWork(): Result {\n"
            "        return try {\n"
            "            // قراءة البيانات من Room وإرسالها للسيرفر:\n"
            "            val analyticsRepo = EntryPoints.get(applicationContext, AnalyticsEntryPoint::class.java).repo()\n"
            "            analyticsRepo.flushPendingEvents()\n"
            "            Result.success() // تم بنجاح\n"
            "        } catch (e: IOException) {\n"
            "            // فشل شبكة عابر: نطلب إعادة المحاولة تلقائياً وفق سياسة الـ Backoff:\n"
            "            Result.retry()\n"
            "        } catch (e: Exception) {\n"
            "            // خطأ دائم غير قابل للإصلاح: ننهي المهمة بفشل:\n"
            "            Result.failure()\n"
            "        }\n"
            "    }\n"
            "}\n"
            "\n"
            "// 2. جدولة المهمة مع قيود البطارية والشبكة وسياسة التكرار الفريد:\n"
            "fun scheduleSync(context: Context) {\n"
            "    val constraints = Constraints.Builder()\n"
            "        .setRequiredNetworkType(NetworkType.CONNECTED)\n"
            "        .setRequiresBatteryNotLow(true)\n"
            "        .build()\n"
            "\n"
            "    val syncRequest = OneTimeWorkRequestBuilder<SyncAnalyticsWorker>()\n"
            "        .setConstraints(constraints)\n"
            "        .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 15, TimeUnit.SECONDS)\n"
            "        .build()\n"
            "\n"
            "    WorkManager.getInstance(context).enqueueUniqueWork(\n"
            "        \"unique_analytics_sync\",\n"
            "        ExistingWorkPolicy.KEEP, // لو كانت مجدولة مسبقاً، نحتفظ بها ولا نكررها\n"
            "        syncRequest\n"
            "    )\n"
            "}\n"
            "```"
        ),
        "quick_answer": "WorkManager guarantees persistent, deferrable background execution that survives process death and phone reboots by persisting work requests in SQLite and coordinating with JobScheduler. It guarantees constraint enforcement (network, charging), but provides at-least-once execution (not exactly-once) and cannot guarantee exact second-precise execution times.",
        "best_answer": (
            "WorkManager is Android's recommended library for persistent, deferrable background processing. It abstracts platform schedulers (`JobScheduler` on API 23+, `AlarmManager + BroadcastReceiver` on legacy APIs) while providing two ironclad guarantees:\n\n"
            "1. **Persistence Across Reboots & Process Death**: Work requests submitted via `enqueue()` are immediately committed to an internal SQLite database managed by WorkManager. If the user swipes the app away, the OS reclaims memory, or the phone runs out of battery, WorkManager reconstructs the task graph and executes it when conditions are satisfied.\n\n"
            "2. **Constraint-Driven Execution**: Tasks pause and resume based on environmental conditions (`NetworkType.UNMETERED`, `RequiresCharging`, `StorageNotLow`).\n\n"
            "Crucially, senior engineers understand its limits: WorkManager provides **At-Least-Once Execution**, not Exactly-Once. If a worker crashes or encounters a network timeout, it may be re-executed, demanding idempotent operations. Furthermore, execution timing is flexible and batched by the OS to preserve battery life; it is never a second-precise cron scheduler."
        ),
        "deep_answer": (
            "Behind the scenes, WorkManager coordinates with Android's **Battery Optimization and Doze Mode** mechanics:\n\n"
            "When a device enters Deep Doze (screen off, stationary, on battery), standard network access and JobScheduler tasks are paused. "
            "WorkManager does **NOT** bypass Doze mode. Instead, it waits for Android's periodic **Doze Maintenance Windows** to batch and flush queued work requests. "
            "If an application requires immediate execution that cannot wait for a maintenance window (e.g. processing an incoming high-priority chat message), you must either use **WorkManager Expedited Work** or handle it via a high-priority Firebase Cloud Messaging (FCM) push payload."
        ),
        "follow_ups": [
            {
                "question": "Can WorkManager run when the app is force-stopped by the user in Settings?",
                "answer": "No. When an app is force-stopped by the user, the Android OS puts it into a stopped state where no alarms, jobs, or broadcast receivers can run until the user explicitly taps the app icon."
            },
            {
                "question": "What is the internal database WorkManager uses?",
                "answer": "It maintains an internal Room database (`androidx.work.workdb`) in the app's private data folder to track work specifications, states, and constraints."
            }
        ]
    },
    {
        "id": "BG-03",
        "arabic_explanation": (
            "مقارنة متعمقة بين `OneTimeWorkRequest` و `PeriodicWorkRequest` في WorkManager:\n\n"
            "1. `OneTimeWorkRequest` (طلب التنفيذ لمرة واحدة):\n   - **كيف يعمل**: يمثل مهمة تنفذ مرة واحدة فقط (Single Execution). يمكن إعادة محاولتها تلقائياً عند الفشل عبر `Result.retry()`.\n   - **أفضل استخدام**: العمليات المرتبطة بحدث محدد: رفع صورة معينة، مزامنة تعديل قام به المستخدم، أو ضغط ملف تم إنشاؤه للتو.\n   - **الميزات الخاصة**: يدعم السلاسل والاعتماديات المعقدة (Chaining via `beginWith(...).then(...)`)، ويدعم التنفيذ المعجل السريع (Expedited Work).\n\n"
            "2. `PeriodicWorkRequest` (طلب التنفيذ الدوري المستمر):\n   - **كيف يعمل**: يمثل مهمة تتكرر باستمرار على فترات زمنية محددة.\n   - **الحدود الصارمة في نظام أندرويد**:\n     * **الحد الأدنى للفترة هو 15 دقيقة (Minimum 15-minute interval)**: إذا كتبت `PeriodicWorkRequestBuilder(5, TimeUnit.MINUTES)`، سيقوم WorkManager تلقائياً بفرض حد الـ 15 دقيقة لحماية بطارية الجهاز!\n     * **المرونة الزمنية (Flex Interval)**: يدعم تحديد نافذة مرنة (Flex Window - الحد الأدنى 5 دقائق)، مثل: 'شغل المهمة كل ساعتين، ولكن اسمح بتشغيلها في آخر 15 دقيقة من الساعتين عند توفر Wi-Fi'.\n   - **أفضل استخدام**: المهام الدورية غير العاجلة: مسح الكاش القديم كل 24 ساعة، أو مزامنة التفضيلات كل 6 ساعات.\n   - **قيود**: `PeriodicWorkRequest` **لا يدعم Chaining** ولا يدعم Expedited Work."
        ),
        "practical_walkthrough": (
            "المقارنة البرمجية بين بناء OneTimeWorkRequest و PeriodicWorkRequest:\n"
            "```kotlin\n"
            "// 1. OneTimeWorkRequest: يدعم السلاسل، والتنفيذ المعجل، وإعادة المحاولة:\n"
            "val compressWork = OneTimeWorkRequestBuilder<CompressImageWorker>().build()\n"
            "val uploadWork = OneTimeWorkRequestBuilder<UploadImageWorker>().build()\n"
            "\n"
            "// تشغيل متسلسل (Chaining): ضغط الصورة أولاً ثم رفعها:\n"
            "WorkManager.getInstance(context)\n"
            "    .beginWith(compressWork)\n"
            "    .then(uploadWork)\n"
            "    .enqueue()\n"
            "\n"
            "// 2. PeriodicWorkRequest: تكرار دوري مع نافذة مرنة (Flex Interval):\n"
            "val dailyCleanupRequest = PeriodicWorkRequestBuilder<CleanupCacheWorker>(\n"
            "    repeatInterval = 24, repeatIntervalTimeUnit = TimeUnit.HOURS,\n"
            "    flexTimeInterval = 2, flexTimeIntervalUnit = TimeUnit.HOURS // تشغيل مرن في آخر ساعتين\n"
            ").setConstraints(\n"
            "    Constraints.Builder()\n"
            "        .setRequiresCharging(true) // لا يعمل إلا عند توصيل الهاتف بالشاحن ليلاً\n"
            "        .setRequiresDeviceIdle(true) // والهاتف غير مستخدم\n"
            "        .build()\n"
            ").build()\n"
            "\n"
            "WorkManager.getInstance(context).enqueueUniquePeriodicWork(\n"
            "    \"daily_cache_cleanup\",\n"
            "    ExistingPeriodicWorkPolicy.KEEP,\n"
            "    dailyCleanupRequest\n"
            ")\n"
            "```"
        ),
        "quick_answer": "OneTimeWorkRequest executes a task once, supports work chaining and expedited execution, and handles retries. PeriodicWorkRequest schedules recurring tasks with an enforced platform minimum interval of 15 minutes and flexible execution windows, but cannot be chained and is subject to Doze mode deferrals.",
        "best_answer": (
            "The architectural differences between `OneTimeWorkRequest` and `PeriodicWorkRequest` revolve around lifecycle, chaining, and OS interval constraints:\n\n"
            "1. **`OneTimeWorkRequest`**:\n   - Executes exactly once per submission. If it fails with `Result.retry()`, it re-executes based on its backoff criteria until hitting max attempts.\n   - **Chaining Capabilities**: Supports complex directed graphs of work (`beginWith(A).then(listOf(B, C)).then(D)`).\n   - **Expedited Support**: Can be marked as expedited to run immediately on Android 12+.\n   - Best for event-driven transactions: media upload, offline form submission, document export.\n\n"
            "2. **`PeriodicWorkRequest`**:\n   - Executes on a recurring interval. The platform enforces a **strict minimum repeat interval of 15 minutes** (`PeriodicWorkRequest.MIN_PERIODIC_INTERVAL_MILLIS`).\n   - **Flex Interval**: Supports defining a flex window (`MIN_PERIODIC_FLEX_MILLIS = 5 minutes`). For a 1-hour interval with a 15-minute flex window, the OS can batch execution anywhere in the final 15 minutes when constraints align.\n   - **No Chaining**: Periodic work requests cannot be chained in sequences.\n   - Best for recurring maintenance: cache pruning, analytics rollups, daily content sync."
        ),
        "deep_answer": (
            "A frequent misconception is expecting `PeriodicWorkRequest` to execute at exact wall-clock intervals (e.g. exactly at 02:00 AM every night).\n\n"
            "Android's power management features (Doze mode, App Standby Buckets) dynamically throttle periodic jobs. "
            "If a user rarely opens your app, Android assigns it to the **'Rare' or 'Restricted' App Standby Bucket**, which restricts periodic jobs to running at most once every 24 hours or delays execution until the phone is connected to power.\n\n"
            "If your business requirement genuinely demands an exact daily execution (e.g. an alarm clock or medicine reminder), you must use **AlarmManager** with exact alarms, not `PeriodicWorkRequest`."
        ),
        "follow_ups": [
            {
                "question": "What happens if you set a PeriodicWorkRequest interval to 5 minutes?",
                "answer": "WorkManager silently clamps the interval to the 15-minute minimum and logs a warning."
            },
            {
                "question": "How do you stop a scheduled PeriodicWorkRequest?",
                "answer": "Call `workManager.cancelUniqueWork(\"unique_work_name\")` or `cancelWorkById(uuid)`."
            }
        ]
    },
    {
        "id": "BG-04",
        "arabic_explanation": (
            "المقارنة الفنية بين أنواع الـ Workers في WorkManager:\n`Worker`، و `CoroutineWorker`، و `ListenableWorker`، ومتى تستخدم كلاً منها؟\n\n"
            "1. `Worker` (الكلاس الأساسي المتزامن):\n   - **كيف يعمل**: يوفر دالة متزامنة `doWork(): Result` تعمل على خيط خلفي (Background Thread) يوفره الـ `Configuration.executor` الخاص بـ WorkManager.\n   - **متى يُستخدم**: للمهام المتزامنة القديمة في مشاريع Java، أو لمهام الحسابات الرياضية المباشرة وحجب الخيوط القصير (Blocking IO) دون الحاجة لـ Coroutines.\n\n"
            "2. `CoroutineWorker` (المعيار الذهبي في Kotlin):\n   - **كيف يعمل**: يوفر دالة تعليق غير متزامنة `suspend fun doWork(): Result`.\n   - **المميزات الخارقة**:\n     * يدمج مباشرة مع Kotlin Coroutines والـ Structured Concurrency.\n     * يعمل افتراضياً على `Dispatchers.Default` (ويمكن تبديله لـ `Dispatchers.IO`).\n     * **دعم تلقائي للإلغاء التعاوني (Cooperative Cancellation)**: إذا ألغى النظام المهمة بسبب فقدان شرط الشبكة أو قيود البطارية، يتم إلغاء الـ Coroutine تلقائياً وإطلاق `CancellationException`، مما يتيح إغلاق الملفات والاتصالات فوراً في كتل `finally` أو `invokeOnCancellation`.\n   - **متى يُستخدم**: في 99% من تطبيقات Kotlin الحديثة لاستدعاء دوال الـ Repositories والـ Suspending APIs.\n\n"
            "3. `ListenableWorker` (الكلاس الأساسي المنخفض المستوى - Base Class):\n   - **كيف يعمل**: الكلاس الجذري الذي يرث منه `Worker` و `CoroutineWorker`. يعيد `ListenableFuture<Result>` من مكتبة Guava.\n   - **متى يُستخدم**: إذا كنت تبني إطار عمل مخصصاً، أو تدمج مع مكتبات خارجية تعتمد على كائنات الـ Future (مثل RxJava عبر `RxWorker` أو Guava)."
        ),
        "practical_walkthrough": (
            "التطبيق المعياري لـ CoroutineWorker مع دعم الإلغاء التعاوني النظيف:\n"
            "```kotlin\n"
            "@HiltWorker\n"
            "class DownloadReportWorker @AssistedInject constructor(\n"
            "    @Assisted context: Context,\n"
            "    @Assisted params: WorkerParameters,\n"
            "    private val reportApi: ReportApiService,\n"
            "    private val reportStorage: ReportFileStorage\n"
            ") : CoroutineWorker(context, params) {\n"
            "\n"
            "    override suspend fun doWork(): Result {\n"
            "        // تبديل الـ Dispatcher إلى IO لمعالجة الملفات والشبكة:\n"
            "        return withContext(Dispatchers.IO) {\n"
            "            try {\n"
            "                val reportData = reportApi.downloadReport(reportId = inputData.getString(\"report_id\")!!)\n"
            "                reportStorage.saveReport(reportData)\n"
            "                Result.success()\n"
            "            } catch (e: CancellationException) {\n"
            "                // التعامل مع الإلغاء إذا سحب النظام الصلاحية أو انقطعت الشبكة:\n"
            "                reportStorage.deletePartialDownload()\n"
            "                throw e // يجب إعادة إطلاق CancellationException ليعلم WorkManager بالإلغاء\n"
            "            } catch (e: IOException) {\n"
            "                Result.retry()\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Worker is a synchronous Java-friendly worker running on a background executor. CoroutineWorker is the modern Kotlin standard providing a suspending doWork() on Dispatchers.Default with cooperative coroutine cancellation. ListenableWorker is the low-level base class returning a ListenableFuture, ideal for custom future or RxJava (RxWorker) integrations.",
        "best_answer": (
            "WorkManager exposes three worker abstractions tailored to different execution models and language idioms:\n\n"
            "1. **`CoroutineWorker` (Modern Kotlin Standard)**:\n   - Exposes `suspend fun doWork(): Result` running by default on `Dispatchers.Default`.\n   - Native integration with structured concurrency and Kotlin suspension points.\n   - **Automatic Cancellation Propagation**: When WorkManager stops work (due to unmet constraints or explicit cancellation), it cancels the underlying `Job`. Suspending functions throw `CancellationException`, enabling immediate resource cleanup.\n   - This is the default choice for virtually all modern Android codebases.\n\n"
            "2. **`Worker` (Synchronous Worker)**:\n   - Exposes synchronous `doWork(): Result` executed on a background thread pool managed by WorkManager's `Configuration.executor`.\n   - Intended for synchronous blocking tasks or legacy Java codebases.\n\n"
            "3. **`ListenableWorker` (Low-Level Root Primitive)**:\n   - The abstract base class that both `Worker` and `CoroutineWorker` extend under the hood. Returns a Guava `ListenableFuture<Result>`.\n   - Reserved for custom concurrency adapters or RxJava integration (`RxWorker`)."
        ),
        "deep_answer": (
            "A critical pitfall in `CoroutineWorker` cancellation is **Swallowing the `CancellationException`**:\n\n"
            "```kotlin\n"
            "// ❌ ANTI-PATTERN:\n"
            "try {\n"
            "    repository.uploadLargeFile()\n"
            "    Result.success()\n"
            "} catch (e: Exception) { // Catches CancellationException!\n"
            "    Result.failure() // Reports failure instead of clean cancellation!\n"
            "}\n"
            "```\n"
            "If an unconstrained `catch (e: Exception)` catches Kotlin's `CancellationException`, WorkManager considers the job terminated with `Result.failure()` rather than stopped due to an unmet constraint. "
            "Always re-throw `CancellationException` or use `catch (e: IOException)` to ensure WorkManager knows the task was stopped by the system and can re-enqueue it when constraints recover."
        ),
        "follow_ups": [
            {
                "question": "How do you inspect the reason why a worker was cancelled?",
                "answer": "On Android 12+, call `getStopReason()` inside the worker to determine if it stopped due to timeout, constraint loss, or user cancellation."
            },
            {
                "question": "Can you inject dependencies into a CoroutineWorker with Hilt?",
                "answer": "Yes, using `@HiltWorker` and `@AssistedInject` on the constructor, combined with `HiltWorkerFactory` configured in the Application class."
            }
        ]
    },
    {
        "id": "BG-05",
        "arabic_explanation": (
            "ما هي قيود النظام (Constraints)، وسياسات التراجع (Backoff Policies)، والعمل الفريد (Unique Work) في WorkManager؟\n\n"
            "1. قيود النظام (Constraints):\n   - شروط بيئية يجب أن تتوفر في الهاتف ليسمح WorkManager بتشغيل المهمة:\n     * `setRequiredNetworkType(NetworkType.CONNECTED / UNMETERED)`: الاتصال بالإنترنت عموماً أو Wi-Fi فقط.\n     * `setRequiresCharging(true)`: الهاتف موصول بالشاحن.\n     * `setRequiresBatteryNotLow(true)`: البطارية ليست منخفضة (أعلى من 15-20%).\n     * `setRequiresDeviceIdle(true)`: الهاتف في وضع الخمول وغير مستخدم.\n   - إذا فُقد أي شرط أثناء تشغيل المهمة (مثل فصل الشاحن)، يقوم WorkManager بإيقاف الـ Worker فوراً وإعادة جدولته تلقائياً.\n\n"
            "2. سياسات التراجع (Backoff Policies):\n   - تحدد كيفية حساب وقت الانتظار قبل إعادة تشغيل المهمة عندما تعيد `Result.retry()`:\n     * `BackoffPolicy.LINEAR`: زيادة خطية (مثلاً: 10s ثم 20s ثم 30s).\n     * `BackoffPolicy.EXPONENTIAL`: زيادة أسية (مثلاً: 10s ثم 20s ثم 40s ثم 80s حتى حد أقصى 5 ساعات).\n\n"
            "3. العمل الفريد (Unique Work):\n   - يمنع تكرار جدولة نفس المهمة مراراً وتكراراً عبر تعيين اسم فريد ثابت لها (`\"sync_orders\"`):\n     * `ExistingWorkPolicy.KEEP`: إذا كانت هناك مهمة بنفس الاسم مجدولة أو قيد التنفيذ، احتفظ بها وتجاهل الطلب الجديد.\n     * `ExistingWorkPolicy.REPLACE`: ألغِ المهمة القديمة فوراً واستبدلها بالطلب الجديد.\n     * `ExistingWorkPolicy.APPEND_OR_REPLACE`: ضع الطلب الجديد في طابور بعد انتهاء القديم."
        ),
        "practical_walkthrough": (
            "تطبيق شامل يجمع Constraints و BackoffPolicy و Unique Work:\n"
            "```kotlin\n"
            "fun scheduleDailyBackup(context: Context) {\n"
            "    // 1. قيود صارمة: شاحن + واي فاي + خمول الجهاز ليلاً:\n"
            "    val constraints = Constraints.Builder()\n"
            "        .setRequiredNetworkType(NetworkType.UNMETERED) // Wi-Fi فقط\n"
            "        .setRequiresCharging(true)                     // موصول بالشاحن\n"
            "        .setRequiresDeviceIdle(true)                   // المستخدم نائم ولا يستخدم الهاتف\n"
            "        .build()\n"
            "\n"
            "    // 2. إعداد الطلب مع Exponential Backoff:\n"
            "    val backupRequest = OneTimeWorkRequestBuilder<DatabaseBackupWorker>()\n"
            "        .setConstraints(constraints)\n"
            "        .setBackoffCriteria(\n"
            "            backoffPolicy = BackoffPolicy.EXPONENTIAL,\n"
            "            backoffDelay = 30,\n"
            "            timeUnit = TimeUnit.SECONDS // تكرار أسي يبدأ من 30 ثانية\n"
            "        )\n"
            "        .build()\n"
            "\n"
            "    // 3. جدولة المهمة كعمل فريد يمنع التكرار:\n"
            "    WorkManager.getInstance(context).enqueueUniqueWork(\n"
            "        \"database_cloud_backup\",\n"
            "        ExistingWorkPolicy.KEEP, // لو كانت مجدولة مسبقاً، لا تنشئ مهمة مكررة!\n"
            "        backupRequest\n"
            "    )\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Constraints define execution prerequisites (network, charging, idle). Backoff policies (LINEAR or EXPONENTIAL) govern delay intervals between Result.retry() attempts. Unique Work prevents duplicate task accumulation by identifying jobs via unique string keys under policies like KEEP, REPLACE, or APPEND.",
        "best_answer": (
            "These three mechanisms govern how WorkManager tasks interact with the operating system, network failures, and redundant invocations:\n\n"
            "1. **Execution Constraints (`Constraints`)**:\n   - Environmental prerequisites checked before launch and continuously monitored during execution.\n   - If a constraint breaks while the worker is actively running (e.g., the user disconnects Wi-Fi mid-upload), WorkManager immediately interrupts the worker and reschedules it.\n\n"
            "2. **Retry Backoff Policies (`BackoffPolicy`)**:\n   - Dictates how delay intervals scale after a worker returns `Result.retry()`.\n   - `BackoffPolicy.EXPONENTIAL` doubles wait times ($15s, 30s, 60s, ...$ up to 5 hours max), shielding backends from aggressive retry loops.\n\n"
            "3. **Unique Work Management (`enqueueUniqueWork`)**:\n   - Deduplicates work requests using a persistent string identifier.\n   - `ExistingWorkPolicy.KEEP`: If work with that key is pending or running, retains the existing instance and ignores the new request.\n   - `ExistingWorkPolicy.REPLACE`: Cancels and drops the existing instance, immediately substituting the new request.\n   - `ExistingWorkPolicy.APPEND_OR_REPLACE`: Queues the new work behind the current task."
        ),
        "deep_answer": (
            "Senior engineers recognize that **Unique Work is NOT a substitute for Server Idempotency**.\n\n"
            "While `ExistingWorkPolicy.KEEP` guarantees that WorkManager will not maintain two duplicate work specifications in its internal SQLite database, it does **NOT** guarantee that a backend API endpoint won't be called twice. "
            "If Worker A sends an HTTP request, the server executes it, and the app crashes before Worker A returns `Result.success()`, WorkManager's retry engine will execute Worker A again upon relaunch! "
            "Unique Work manages local scheduling deduplication; backend operations must always be secured with client-generated Idempotency Keys."
        ),
        "follow_ups": [
            {
                "question": "What is the minimum backoff delay in WorkManager?",
                "answer": "10 seconds (`WorkRequest.MIN_BACKOFF_MILLIS`). Setting anything lower is automatically clamped to 10 seconds."
            },
            {
                "question": "Can constraints include checking for available device storage?",
                "answer": "Yes, `setRequiresStorageNotLow(true)` ensures the task only runs when the device has sufficient free flash storage."
            }
        ]
    },
    {
        "id": "BG-06",
        "arabic_explanation": (
            "ما هو وضع الخمول (Doze Mode) وقيود وضع الاستعداد للتطبيقات (App Standby Buckets) في Android؟ وكيف تؤثر على المهام الخلفية؟\n\n"
            "1. وضع الخمول (Doze Mode - أُضيف في Android 6.0):\n   - **متى يعمل**: عندما يترك المستخدم الهاتف ثابتاً على الطاولة، والشاشة مطفأة، والهاتف غير موصول بالشاحن.\n   - **ماذا يفعل النظام (Restrictions)**:\n     * يقطع الوصول للشبكة بالكامل عن التطبيقات في الخلفية.\n     * يعلق الـ JobScheduler و WorkManager والـ Sync Adapters.\n     * يتجاهل الـ WakeLocks لمنع استنزاف المعالج.\n     * يعلق تنبيهات AlarmManager العادية.\n   - **نوافذ الصيانة (Maintenance Windows)**:\n     * يفتح النظام نافذة صيانة دورية كل فترة (تتباعد تدريجياً: بعد 10 دقائق، ثم ساعة، ثم عدة ساعات) لتشغيل المهام المؤجلة ومزامنة البيانات دفعة واحدة (Batching)، ثم يعود للخمول العميق.\n\n"
            "2. وضع الاستعداد للتطبيقات (App Standby Buckets - أُضيف في Android 9.0):\n   - يصنف النظام التطبيقات إلى 5 مجموعات بناءً على مدى استخدام المستخدم لها:\n     * **Active**: التطبيق مفتوح الآن أو قيد الاستخدام الفعلي -> لا قيود.\n     * **Working Set**: يستخدمه المستخدم يومياً -> قيود خفيفة جداً.\n     * **Frequent**: يستخدمه بانتظام أسبوعياً -> قيود على عدد المهام والـ Jobs المسموحة يومياً.\n     * **Rare**: نادراً ما يفتحه المستخدم -> لا يُسمح بتشغيل Jobs إلا مرة واحدة كل 24 ساعة!\n     * **Restricted**: التطبيق يستهلك موارد مفرطة -> حظر كامل تقريباً في الخلفية.\n\n"
            "3. كيف يتعامل مهندس Android المحترف مع هذه القيود؟\n   - تصميم التطبيق ليكون متسامحاً مع التأجيل (Delay-Tolerant).\n   - استخدام FCM High-Priority Push Notifications للرسائل العاجلة لإيقاظ التطبيق مؤقتاً.\n   - عدم محاولة التحايل على النظام بحيل مشبوهة تؤدي لرفض التطبيق في متجر Google Play."
        ),
        "practical_walkthrough": (
            "توضيح دورة حياة Doze Mode ونوافذ الصيانة وتصنيف App Standby Buckets:\n"
            "```text\n"
            "🌙 دورة حياة Doze Mode:\n"
            "Screen OFF & Stationary ──► [Light Doze] ──► [Deep Doze (No Network, No Jobs, No WakeLocks)]\n"
            "                                                 │\n"
            "                                                 ├──► [Maintenance Window] (WorkManager flushes jobs)\n"
            "                                                 │\n"
            "                                                 └──► [Deep Doze resumes (Longer delay)]\n"
            "\n"
            "📦 تصنيفات App Standby Buckets:\n"
            "┌───────────────┬──────────────────────────────────┬─────────────────────────────────┐\n"
            "│ Bucket        │ نمط استخدام المستخدم             │ قيود المهام الخلفية (Jobs/Sync) │\n"
            "├───────────────┼──────────────────────────────────┼─────────────────────────────────┤\n"
            "│ Active        │ مفتوح الآن في الشاشة             │ لا توجد أي قيود                 │\n"
            "│ Working Set   │ يُفتح يومياً بانتظام             │ تأخير مهام بسيط (دقائق)         │\n"
            "│ Frequent      │ يُفتح بضعة أيام في الأسبوع       │ حد أقصى للـ Jobs كل بضع ساعات   │\n"
            "│ Rare          │ نادراً ما يُفتح (مرة أسبوعياً)   │ حد أقصى للـ Jobs: مرة كل 24 ساعة│\n"
            "│ Restricted    │ يستهلك بطارية مفرطة وتم تقييده   │ محظور من الخلفية تماماً         │\n"
            "└───────────────┴──────────────────────────────────┴─────────────────────────────────┘\n"
            "```"
        ),
        "quick_answer": "Doze mode suspends network access, jobs, and alarms when the device is unplugged, stationary, and screen-off, executing work only during periodic maintenance windows. App Standby Buckets throttle background tasks based on user engagement frequency (Active, Working Set, Frequent, Rare), restricting rare apps to at most once-daily job executions.",
        "best_answer": (
            "Doze Mode and App Standby Buckets represent Android's core OS power management architecture designed to maximize battery life:\n\n"
            "1. **Doze Mode (Device-Level Power Policy)**:\n   - Enters **Light Doze** shortly after screen-off, restricting network and deferring jobs.\n   - Transitions into **Deep Doze** when stationary and unplugged. Disables network access entirely, suspends JobScheduler and WorkManager tasks, ignores standard WakeLocks, and defers standard alarms.\n   - Executes deferred work only during periodic, increasingly spaced **Maintenance Windows** (e.g. 10m, 30m, 1h, 2h).\n\n"
            "2. **App Standby Buckets (App-Level Engagement Policy)**:\n   - Categorizes apps into tiers based on recency and frequency of user interaction:\n     * **Active**: App is currently in foreground or running a foreground service.\n     * **Working Set**: Used daily; minimal restrictions.\n     * **Frequent**: Used regularly but not daily; jobs throttled to intervals.\n     * **Rare**: Rarely opened; jobs capped at once every 24 hours.\n     * **Restricted**: Extreme background limits, zero background network jobs."
        ),
        "deep_answer": (
            "Architectural Strategies to build resilient apps under Doze and Standby Buckets:\n\n"
            "1. **Design for Delay-Tolerance**: Assume background synchronization can be delayed by 2–4 hours. When the user returns to the foreground, trigger a proactive refresh in `onStart()` or `repeatOnLifecycle`.\n\n"
            "2. **FCM High-Priority Push for Time-Critical Events**: High-priority Firebase Cloud Messaging grants a temporary Doze exemption window and network ticket, allowing the app to display a critical notification or run a short expedited job.\n\n"
            "3. **Testing Doze Mode via ADB**: Senior engineers verify background behavior in CI and local testing using ADB commands:\n   - Force Doze: `adb shell dumpsys deviceidle force-idle`\n   - Inspect Standby Bucket: `adb shell am get-inactive <package>`\n   - Set Bucket: `adb shell am set-standby-bucket <package> rare`"
        ),
        "follow_ups": [
            {
                "question": "Can an app request battery optimization whitelist exemption (`REQUEST_IGNORE_BATTERY_OPTIMIZATIONS`)?",
                "answer": "Yes, but Google Play policy strictly limits this permission to specialized use cases (health monitoring, VoIP, navigation); violating it leads to app removal."
            },
            {
                "question": "Does AlarmManager `setExactAndAllowWhileIdle()` fire during Deep Doze?",
                "answer": "Yes, but the OS limits how frequently it can wake the device (at most once every 9–15 minutes) and network access remains restricted."
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

    for item in BG_01_06:
        by_id[item["id"]] = item

    output = [by_id[k] for k in sorted(by_id.keys())]
    DATA_FILE.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {DATA_FILE} with questions BG-01 to BG-06. Total questions: {len(output)}")

if __name__ == "__main__":
    main()
