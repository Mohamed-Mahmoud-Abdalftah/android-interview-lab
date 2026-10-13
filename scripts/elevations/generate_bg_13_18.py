#!/usr/bin/env python3
"""Generator for BG-13 through BG-18 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "bg.json"

BG_13_18 = [
    {
        "id": "BG-13",
        "arabic_explanation": (
            "متى يجب استخدام التنبيه الدقيق (Exact Alarm عبر AlarmManager) بدلاً من العمل الدوري (Periodic WorkManager)؟\n\n"
            "1. متى يكون الـ Exact Alarm إلزامياً ومبرراً (When Exact Alarm is Mandatory):\n   - **التطبيقات التي تتطلب الدقة بالثانية في لحظة زمنية معينة يدركها المستخدم (Clock-Exact User-Facing Events)**:\n     * تطبيق المنبه (Alarm Clock) للاستيقاظ في تمام 07:00:00 صباحاً.\n     * منبه مواعيد تناول الدواء لمرضى السكري والقلب (Medical/Medication Reminders).\n     * تذكير تقويم بالتقاء أو مكالمة فيديو يبدأ في وقت محدد.\n   - في هذه الحالات، لا يمكن الاعتماد على WorkManager لأن WorkManager يجمع المهام ويؤخرها لدقائق وساعات أثناء وضع الـ Doze Mode والبطارية.\n\n"
            "2. متى يُحظر استخدام الـ Exact Alarm (When to Avoid):\n   - مزامنة البيانات من السيرفر (Data Sync).\n   - جلب أحدث المقالات الإخبارية.\n   - فحص وجود إشعارات جديدة (Polling).\n   - في هذه الحالات، يجب استخدام WorkManager أو FCM Push Notifications.\n\n"
            "3. القيود والصلاحيات الصارمة في Android الحديث (Android 12 إلى 14):\n   - **صلاحية `SCHEDULE_EXACT_ALARM`**: تم تقييدها بشدة. في Android 13/14، لا تمنح تلقائياً إلا لتطبيقات من فئتي: المنبهات (Clock/Alarms) والتقويم (Calendar). باقي التطبيقات تتطلب توجيهاً صريحاً للمستخدم إلى شاشة إعدادات النظام للموافقة اليدوية.\n   - **صلاحية `USE_EXACT_ALARM`**: متاحة فقط للتطبيقات المتخصصة رسمياً في المنبهات على متجر Google Play."
        ),
        "practical_walkthrough": (
            "فحص الصلاحية وبرمجة Exact Alarm مع الإيقاظ في وضع Doze Mode:\n"
            "```kotlin\n"
            "class AlarmScheduler(private val context: Context) {\n"
            "    private val alarmManager = context.getSystemService(AlarmManager::class.java)\n"
            "\n"
            "    fun scheduleMedicationReminder(reminderId: Int, triggerTimeMillis: Long) {\n"
            "        // 1. التحقق من صلاحية الجدولة الدقيقة على Android 12+ (API 31+):\n"
            "        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {\n"
            "            if (!alarmManager.canScheduleExactAlarms()) {\n"
            "                // توجيه المستخدم لصفحة الإعدادات لتفعيل الصلاحية:\n"
            "                val intent = Intent(Settings.ACTION_REQUEST_SCHEDULE_EXACT_ALARM)\n"
            "                intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK\n"
            "                context.startActivity(intent)\n"
            "                return\n"
            "            }\n"
            "        }\n"
            "\n"
            "        val intent = Intent(context, AlarmReceiver::class.java).apply {\n"
            "            putExtra(\"reminder_id\", reminderId)\n"
            "        }\n"
            "        val pendingIntent = PendingIntent.getBroadcast(\n"
            "            context,\n"
            "            reminderId,\n"
            "            intent,\n"
            "            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE\n"
            "        )\n"
            "\n"
            "        // 2. إيقاظ الجهاز بالثانية حتى لو كان في وضع الخمول العميق (Doze Mode):\n"
            "        alarmManager.setExactAndAllowWhileIdle(\n"
            "            AlarmManager.RTC_WAKEUP,\n"
            "            triggerTimeMillis,\n"
            "            pendingIntent\n"
            "        )\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Use exact alarms (AlarmManager.setExactAndAllowWhileIdle) only for clock-precise, user-facing events like wakeup alarms, medical alerts, and calendar reminders. Use WorkManager for all deferrable data sync and background maintenance. Exact alarms require special permissions (SCHEDULE_EXACT_ALARM) and must not be abused for network polling.",
        "best_answer": (
            "The choice between AlarmManager and WorkManager centers on **Temporal Precision versus Resource Optimization**:\n\n"
            "1. **When to Choose Exact Alarms (`AlarmManager`)**:\n   - Mandatory only when missing the trigger time by 30 seconds ruins the core user experience: wakeup alarms, medication dosage reminders, and scheduled video-call notifications.\n   - Invoked via `setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, time, pendingIntent)`. This guarantees the device will wake from deep sleep and fire the broadcast receiver within a second of the target wall-clock time.\n\n"
            "2. **When Exact Alarms are an Anti-Pattern**:\n   - Polling an API for updates, fetching new feed posts, or cleaning local caches. Using exact alarms for data sync burns excessive battery and violates Google Play policies.\n   - For all data operations, use **WorkManager**; it batches tasks into Doze maintenance windows and respects network conditions.\n\n"
            "3. **Platform Policy & Permissions (Android 12/14+)**:\n   - Applications targeting API 31+ must hold the `SCHEDULE_EXACT_ALARM` or `USE_EXACT_ALARM` permission. In Android 14, `SCHEDULE_EXACT_ALARM` is revoked by default for newly installed apps unless explicitly categorized as an Alarm or Calendar app by Google Play."
        ),
        "deep_answer": (
            "What happens after an Exact Alarm fires?\n\n"
            "When `AlarmReceiver.onReceive()` triggers, the device is briefly awake holding a temporary partial wake-lock granted by the OS (lasting approximately 10–15 seconds).\n\n"
            "- **The Trap**: If the receiver initiates a long-running coroutine or network request inside `onReceive()`, the method returns immediately, the OS releases the temporary wake-lock, and the device goes back to sleep, freezing the coroutine midway!\n\n"
            "- **The Production Protocol**: Keep `onReceive()` lightweight. Post a high-priority heads-up notification with sound immediately. If the alarm requires heavy data processing, enqueue an **Expedited WorkRequest** via WorkManager or transition to a dedicated typed Foreground Service."
        ),
        "follow_ups": [
            {
                "question": "What is `AlarmManager.canScheduleExactAlarms()`?",
                "answer": "A method introduced in Android 12 to check whether the user has granted the app permission to schedule exact alarms before attempting to set one."
            },
            {
                "question": "Why shouldn't you use `setRepeating()` for exact alarms?",
                "answer": "Since Android 4.4 (KitKat), all repeating alarms are inexact and batched by the OS; to achieve recurring exact alarms, reschedule an exact alarm inside the receiver."
            }
        ]
    },
    {
        "id": "BG-14",
        "arabic_explanation": (
            "كيف تنسق بين WorkManager وطبقة الـ Repository ومعاملات قاعدة بيانات Room؟ وكيف تحل مشكلة وجود قاعدتي بيانات منفصلتين؟\n\n"
            "1. المعضلة المعمارية (The Two-Database Dilemma):\n   - لتطبيقك قاعدة بيانات خاصة به (`app.db`) تابعة لـ Room.\n   - ومكتبة WorkManager تمتلك قاعدة بيانات SQLite خاصة بها بالكامل (`androidx.work.workdb`).\n   - **المشكلة التقنية**: لا يمكنك عمل معملة ذرية واحدة (Distributed Transaction) تجمع بين الاثنين! إذا قمت بحفظ تعديل في Room ثم مات التطبيق قبل استدعاء `workManager.enqueue()`, فإن العملية ستظل معلقة محلياً ولن تُرسل أبداً!\n\n"
            "2. نمط الحل المعتمد: Outbox Pattern مع Startup Recovery Scan:\n   - **قاعدة بيانات Room هي الحقيقة المطلقة (Single Source of Truth)**:\n     * عند قيام المستخدم بأي تعديل، يُحفظ في جدول البيانات وفي جدول `outbox_mutations` داخل `database.withTransaction`.\n     * بعد نجاح الـ Commit، يتم استدعاء `workManager.enqueueUniqueWork(\"sync_outbox\", ExistingWorkPolicy.KEEP, request)`.\n   - **شبكة الأمان عند الإقلاع (Recovery on App Startup)**:\n     * إذا مات التطبيق بين خطوة الـ Commit وخطوة الـ Enqueue:\n     * عند تشغيل التطبيق في `Application.onCreate()`, يقوم فاحص خفيف بالتحقق: هل توجد سجلات في `outbox_mutations`؟ إذا وُجدت، يُطلق الـ WorkManager مجدداً للتأكد من عدم ضياع أي مهمة.\n\n"
            "3. دور الـ Worker:\n   - لا تمرر بيانات ضخمة (Payloads) في `Data` الخاصة بـ WorkManager (حدها الأقصى 10KB!).\n   - مرر فقط `operationId`. يقوم الـ Worker بفتح Room وقراءة البيانات وتنفيذ الطلب، وتحديث الحالة داخل Room بعد استلام رد السيرفر."
        ),
        "practical_walkthrough": (
            "تنسيق معاملات Room مع WorkManager ونظام استعادة المهام العالقة:\n"
            "```kotlin\n"
            "class SafeOutboxRepositoryImpl @Inject constructor(\n"
            "    private val db: AppDatabase,\n"
            "    private val workManager: WorkManager\n"
            ") : OutboxRepository {\n"
            "\n"
            "    override suspend fun commitAction(actionType: String, payloadJson: String) {\n"
            "        val actionId = UUID.randomUUID().toString()\n"
            "        \n"
            "        // 1. الحفظ الذري في قاعدة بيانات التطبيق أولاً:\n"
            "        db.withTransaction {\n"
            "            db.outboxDao().insertAction(OutboxEntity(id = actionId, action = actionType, payload = payloadJson))\n"
            "        }\n"
            "\n"
            "        // 2. جدولة المهمة في WorkManager بعد نجاح المعاملة:\n"
            "        dispatchSyncWork()\n"
            "    }\n"
            "\n"
            "    fun dispatchSyncWork() {\n"
            "        val syncRequest = OneTimeWorkRequestBuilder<DrainOutboxWorker>()\n"
            "            .setConstraints(Constraints.Builder().setRequiredNetworkType(NetworkType.CONNECTED).build())\n"
            "            .build()\n"
            "        \n"
            "        // ExistingWorkPolicy.KEEP يضمن تشغيل مهمة واحدة دون تكرار:\n"
            "        workManager.enqueueUniqueWork(\"drain_outbox_work\", ExistingWorkPolicy.KEEP, syncRequest)\n"
            "    }\n"
            "\n"
            "    // 3. شبكة الأمان عند إقلاع التطبيق (Startup Reconciliation):\n"
            "    suspend fun recoverPendingActionsOnStartup() {\n"
            "        if (db.outboxDao().hasPendingActions()) {\n"
            "            dispatchSyncWork() // إعادة جدولة العمليات العالقة لو مات التطبيق سابقاً\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Coordinate WorkManager with Room by establishing Room as the single source of truth using an Outbox table. Commit entities and outbox records inside a Room transaction first, then enqueue unique work. Reconcile missed enqueues via a lightweight startup check to guarantee zero lost tasks despite separate database files.",
        "best_answer": (
            "Because Room and WorkManager manage independent SQLite databases (`app.db` and `androidx.work.workdb`), atomic two-phase distributed commits are impossible on Android. A crash between a Room commit and a WorkManager enqueue risks silent operation loss.\n\n"
            "The enterprise solution coordinates both systems through the **Outbox Pattern with Startup Reconciliation**:\n\n"
            "1. **Room Commit First**: When a mutation occurs, write the entity and an `outbox_mutations` record within a single `roomDatabase.withTransaction { }`. Room represents the authoritative state of record.\n\n"
            "2. **Post-Commit Enqueue**: Immediately after the transaction commits, enqueue a unique work request (`ExistingWorkPolicy.KEEP`) with network constraints.\n\n"
            "3. **Startup Safety Net**: During `Application.onCreate()` or repository initialization, execute a fast index query: `if (outboxDao.hasPending()) dispatchSyncWork()`. If the app was killed after step 1 but before step 2, the pending mutation is resurrected and enqueued cleanly.\n\n"
            "4. **Worker Boundary**: The worker injects the repository, reads pending outbox entries from Room, executes HTTP calls with idempotency keys, and deletes outbox records upon server confirmation inside Room transactions."
        ),
        "deep_answer": (
            "Why shouldn't you pass entity payloads inside WorkManager's `Data` object?\n\n"
            "WorkManager's `Data` input payload has a **strict 10KB size limit** (`Data.MAX_DATA_BYTES = 10240`). "
            "If an image path, form draft, or JSON payload exceeds 10KB, WorkManager throws an `IllegalStateException`.\n\n"
            "**Rule**: WorkManager's input data should only ever contain foreign keys or IDs (`operationId = \"UUID\"`). The worker uses the ID to query full, rich domain entities and binaries directly from Room or app private storage, keeping WorkManager's internal SQLite database lean and fast."
        ),
        "follow_ups": [
            {
                "question": "What is the maximum payload size in WorkManager's `Data`?",
                "answer": "10,240 bytes (10KB). Passing larger datasets throws `IllegalStateException`."
            },
            {
                "question": "Can multiple DAOs participate in a single `roomDatabase.withTransaction`?",
                "answer": "Yes! All DAOs belonging to the same RoomDatabase instance share the same underlying SQLite transaction."
            }
        ]
    },
    {
        "id": "BG-15",
        "arabic_explanation": (
            "تصميم نظام رفع ملفات ضخمة (Resumable Large File Upload) يصمد أمام موت الـ Process وانقطاع الشبكة واستجابات السيرفر المجهولة:\n\n"
            "1. المخطط المعماري الكامل (Resumable Upload Architecture):\n   - **المرحلة 1: تسجيل بيانات الرفع في Room (Upload Metadata Entity)**:\n     * عند اختيار ملف (فيديو أو مستند 100MB)، نحفظ سجلاً في Room: `uploadId: UUID`, `fileUri`, `fileSizeBytes`, `bytesAcked = 0`, `serverSessionUrl = null`, `status = PENDING`.\n     * حفظ أذونات الـ URI الدائمة (`takePersistableUriPermission`).\n   - **المرحلة 2: بدء جلسة الرفع على السيرفر (Upload Session Handshake)**:\n     * يطلب الـ Worker من السيرفر فتح جلسة رفع: `POST /uploads/session` مع الحجم ونوع الملف.\n     * يعيد السيرفر رابط جلسة مخصص: `serverSessionUrl`. يتم حفظ هذا الرابط في Room فوراً.\n   - **المرحلة 3: رفع الملف كأجزاء متتالية (Chunked Upload)**:\n     * رفع الملف في أجزاء (مثل 5MB لكل Chunk) باستخدام `Content-Range: bytes 0-5242880/104857600`.\n     * مع كل جزء يؤكده السيرفر، يتم تحديث `bytesAcked` في Room.\n   - **المرحلة 4: التعافي عند انقطاع الشبكة أو موت الـ Process**:\n     * إذا انقطعت الشبكة أو مات الـ Process: عند عودة الـ Worker، **لا يبدأ الرفع من البداية**!\n     * يرسل استعلام استقصائي للسيرفر: `HEAD <serverSessionUrl>` أو فحص Range.\n     * يجيب السيرفر: 'وصلني 45MB'. يقوم الـ Worker بفتح الملف واستئناف القراءة بدءاً من البايت 45,000,001 فوراً!"
        ),
        "practical_walkthrough": (
            "تنفيذ بروتوكول استئناف رفع الملفات الكبيرة في CoroutineWorker:\n"
            "```kotlin\n"
            "@HiltWorker\n"
            "class ResumableUploadWorker @AssistedInject constructor(\n"
            "    @Assisted context: Context,\n"
            "    @Assisted params: WorkerParameters,\n"
            "    private val uploadDao: UploadDao,\n"
            "    private val uploadClient: ResumableHttpClient\n"
            ") : CoroutineWorker(context, params) {\n"
            "\n"
            "    override suspend fun doWork(): Result {\n"
            "        val uploadId = inputData.getString(\"upload_id\") ?: return Result.failure()\n"
            "        val record = uploadDao.getUpload(uploadId) ?: return Result.failure()\n"
            "\n"
            "        return try {\n"
            "            // 1. الحصول على رابط الجلسة (أو إنشاء جلسة جديدة لو لم تكن موجودة):\n"
            "            val sessionUrl = record.sessionUrl ?: run {\n"
            "                val newUrl = uploadClient.initiateSession(record.fileName, record.fileSizeBytes)\n"
            "                uploadDao.updateSessionUrl(uploadId, newUrl)\n"
            "                newUrl\n"
            "            }\n"
            "\n"
            "            // 2. استعلام السيرفر عن الإزاحة المؤكدة الحالية (Current Acked Offset):\n"
            "            val serverOffset = uploadClient.queryCurrentOffset(sessionUrl)\n"
            "            uploadDao.updateBytesAcked(uploadId, serverOffset)\n"
            "\n"
            "            if (serverOffset >= record.fileSizeBytes) {\n"
            "                uploadDao.markCompleted(uploadId)\n"
            "                return Result.success()\n"
            "            }\n"
            "\n"
            "            // 3. استئناف الرفع من نقطة الانقطاع بدقة:\n"
            "            val file = File(record.localFilePath)\n"
            "            uploadClient.uploadRemainingChunks(\n"
            "                sessionUrl = sessionUrl,\n"
            "                file = file,\n"
            "                startOffset = serverOffset,\n"
            "                onChunkAcked = { ackedBytes ->\n"
            "                    uploadDao.updateBytesAcked(uploadId, ackedBytes)\n"
            "                    setProgress(workDataOf(\"progress\" to ((ackedBytes * 100) / record.fileSizeBytes).toInt()))\n"
            "                }\n"
            "            )\n"
            "            uploadDao.markCompleted(uploadId)\n"
            "            Result.success()\n"
            "        } catch (e: IOException) {\n"
            "            Result.retry() // إعادة المحاولة لاحقاً واستئناف الرفع من آخر بايت مسجل!\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Design a resilient upload system using chunked resumable uploads. Persist upload metadata (file URI, session URL, acked bytes) in Room. When the worker resumes after process death or network loss, query the server's acknowledged byte offset via a status check and stream remaining chunks from that exact offset.",
        "best_answer": (
            "Building a resumable upload pipeline that survives process death and network drops requires dividing the upload into stateful, verifiable phases:\n\n"
            "1. **Persistent Metadata Registration**: In Room, commit an `upload_tasks` record before starting: `{ uploadId, fileUri, totalBytes, sessionUrl = null, bytesAcked = 0, status = PENDING }`. Acquire persistent URI permissions via `contentResolver.takePersistableUriPermission()`.\n\n"
            "2. **Resumable Session Handshake**: The worker initiates an upload session (`POST /uploads/sessions`). The backend provisions a unique upload URL and records the target file size. Save this `sessionUrl` in Room.\n\n"
            "3. **Chunked Streaming (`Content-Range`)**: Stream the file in deterministic chunks (e.g. 5MB) using `Content-Range: bytes START-END/TOTAL`. Each chunk acknowledgment updates `bytesAcked` in Room.\n\n"
            "4. **Offset Reconciliation on Recovery**: If the process dies or network drops mid-upload, the worker restarts under WorkManager. It queries the server (`HEAD <sessionUrl>` or `GET status`) to determine the *exact server-acknowledged byte count*. The client skips already-received bytes, streaming from `serverOffset` to EOF without duplicating bandwidth."
        ),
        "deep_answer": (
            "Foreground Notification & Execution Constraints for Large Uploads:\n\n"
            "For uploads exceeding 50MB, background execution policies in Android 14 can terminate non-expedited workers if execution exceeds quota limits. "
            "To guarantee uninterrupted execution:\n\n"
            "- Call `setForeground(createForegroundInfo(uploadId, progress))` inside the worker. This converts the worker into an OS-recognized Foreground Service with an ongoing notification.\n"
            "- Declare `android:foregroundServiceType=\"dataSync\"` in `AndroidManifest.xml`.\n"
            "- If the worker is stopped by the user via the Android 13 Task Manager, catch `CancellationException`, update Room state to `PAUSED`, and preserve the `sessionUrl` and `bytesAcked` so the user can tap 'Resume' later."
        ),
        "follow_ups": [
            {
                "question": "What is the Tus protocol (tus.io)?",
                "answer": "An open standard protocol for resumable file uploads over HTTP utilizing HEAD requests to inspect offsets and PATCH requests to upload binary chunks."
            },
            {
                "question": "Why shouldn't you upload a 2GB video in a single raw HTTP POST request?",
                "answer": "A single connection drop at 99% forces re-uploading the entire 2GB file from zero; chunked uploads isolate failures to a single 5MB chunk."
            }
        ]
    },
    {
        "id": "BG-16",
        "arabic_explanation": (
            "المهمة نُفذت مرتين (Ran Twice) بعد حدوث عطل (Crash). كيف تفرض مبدأ الـ Idempotency المعماري لمنع الآثار الجانبية المكررة؟\n\n"
            "1. لماذا تُنفذ المهمة مرتين في أنظمة الموبايل؟\n   - WorkManager يضمن الوصول على الأقل مرة واحدة (At-Least-Once Delivery).\n   - عندما تنفذ المهمة، يحدث الآتي:\n     * الخطوة 1: الـ Worker يرسل طلب الخصم أو حجز المقعد للسيرفر بنجاح.\n     * الخطوة 2: السيرفر ينفذ العملية في قاعدة بياناته.\n     * الخطوة 3: قبل أن يتمكن الـ Worker من حفظ نتيجة النجاح في قاعدة بيانات WorkManager، تنفد بطارية الهاتف أو يقتل النظام الـ Process (Crash / OOM)!\n     * الخطوة 4: عند إعادة فتح الهاتف، يرى WorkManager أن المهمة لم تُسجل كـ SUCCEEDED، فيعيد تشغيلها بالكامل!\n\n"
            "2. كيفية فرض الـ Idempotency الكامل (Full Idempotency Enforcement):\n   - **فصل محاولة الجدولة (Work Attempt) عن هوية العملية التجارية (Logical Operation ID)**:\n     * توليد معرف عملية فريد وثابت (`operationId: UUID`) قبل إرسال أول طلب، وحفظه في Room.\n   - **سجل الحالة المزدوج (State Machine in Room)**:\n     * الحالات: `DRAFT` -> `SUBMITTING` -> `CONFIRMED` -> `FAILED`.\n     * عند إعادة تشغيل الـ Worker، يقرأ الحالة من Room: إذا كانت `CONFIRMED`, ينهي بـ `Result.success()` دون استدعاء السيرفر.\n   - **السيرفر هو الحصن المنيع (Server-Side Idempotency Cache)**:\n     * السيرفر يخزن الـ `Idempotency-Key` ونتيجة العملية في Redis أو SQL لمدة 24 ساعة.\n     * إذا استلم السيرفر نفس المفتاح، يعيد نفس الرد السابق برمز `200 OK` فوراً دون تكرار أي خصم أو إنشاء."
        ),
        "practical_walkthrough": (
            "تنفيذ التحقق المزدوج للـ Idempotency على العميل والسيرفر:\n"
            "```kotlin\n"
            "class SafeOrderWorker(context: Context, params: WorkerParameters) : CoroutineWorker(context, params) {\n"
            "\n"
            "    override suspend fun doWork(): Result {\n"
            "        val orderId = inputData.getString(\"order_id\") ?: return Result.failure()\n"
            "        val db = EntryPoints.get(applicationContext, DbEntryPoint::class.java).database()\n"
            "        val api = EntryPoints.get(applicationContext, ApiEntryPoint::class.java).orderApi()\n"
            "\n"
            "        val order = db.orderDao().getOrder(orderId) ?: return Result.failure()\n"
            "\n"
            "        // 1. الفحص المحلي: إذا كانت العملية مسجلة بالفعل كـ CONFIRMED:\n"
            "        if (order.status == OrderStatus.CONFIRMED) {\n"
            "            return Result.success() // تم تأكيدها مسبقاً قبل الـ Crash! نجاح فوري\n"
            "        }\n"
            "\n"
            "        // 2. إرسال الطلب مع استخدام order.id كمفتاح Idempotency ثابت:\n"
            "        return try {\n"
            "            val receipt = api.submitOrder(\n"
            "                idempotencyKey = order.id,\n"
            "                request = order.toDto()\n"
            "            )\n"
            "            // 3. حفظ التأكيد في Room:\n"
            "            db.orderDao().updateStatus(orderId, OrderStatus.CONFIRMED, receipt.receiptId)\n"
            "            Result.success()\n"
            "        } catch (e: IOException) {\n"
            "            Result.retry()\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Enforce idempotency by separating the WorkManager retry attempt from the logical domain operation. Persist a stable operation UUID in Room. Before making network calls, verify if local state is already confirmed. On the wire, transmit the operation UUID as an Idempotency-Key header, ensuring the backend returns cached receipts on duplicate submissions.",
        "best_answer": (
            "Because WorkManager enforces At-Least-Once execution, a crash occurring after network transmission but before local database commitment guarantees that the worker will re-run. Enforcing idempotency requires coordinated client and server contracts:\n\n"
            "1. **Client Pre-Flight State Check**:\n   - Pass a durable business identifier (`orderId = UUID`) into the worker, never an ephemeral count.\n   - At the entry of `doWork()`, inspect SQLite. If `order.status == CONFIRMED`, immediately return `Result.success()`. This short-circuits execution if local state committed before WorkManager recorded task completion.\n\n"
            "2. **Wire-Level Idempotency Keys**:\n   - Transmit `Idempotency-Key: <orderId>` in the request header.\n   - The server maintains an idempotency registry (e.g. Redis). If it sees an already-processed key, it aborts business side-effects and returns the previously generated payload with `HTTP 200 OK`.\n\n"
            "3. **Reconciliation Fallback on Lost Responses**:\n   - If the call times out and restarts, query `GET /orders/{id}` using the same UUID before attempting a blind re-POST."
        ),
        "deep_answer": (
            "From a database architecture standpoint, senior engineers enforce idempotency using **Atomic State Transitions with Optimistic Locking**:\n\n"
            "```sql\n"
            "-- In Room DAO:\n"
            "UPDATE orders SET status = 'CONFIRMED', receipt = :receipt \n"
            "WHERE id = :id AND status = 'SUBMITTING';\n"
            "```\n"
            "If another thread or an asynchronous webhook already transitioned the order from `SUBMITTING` to `CONFIRMED`, the `UPDATE` query affects 0 rows. "
            "The repository detects `rowsUpdated == 0`, reads the existing confirmed state, and cleanly returns `Result.success()` without corrupting state or executing race conditions."
        ),
        "follow_ups": [
            {
                "question": "What is the difference between an Idempotent API and a Safe API?",
                "answer": "A Safe API (like GET) does not alter server state at all; an Idempotent API (like PUT or idempotent POST) can alter state on the first call, but subsequent identical calls produce no additional state changes."
            },
            {
                "question": "How long should a server retain an Idempotency Key?",
                "answer": "Typically 24 to 72 hours, sufficient to cover all possible mobile network retry windows and device reboots."
            }
        ]
    },
    {
        "id": "BG-17",
        "arabic_explanation": (
            "متطلب تجاري يطلب تنفيذ مهمة في الخلفية بدقة بالثانية بشكل دوري (Second-Perfect Periodic Background Execution). ما هي قيود Android الحتمية التي تمنع ذلك؟ وكيف تفاوض الحل؟\n\n"
            "1. الحقائق الصارمة لنظام تشغيل Android (Why This is Impossible):\n   - **Android ليس نظام تشغيل فوري (Android is NOT a Real-Time OS - RTOS)**.\n   - معمارية الطاقة في Android مبنية بالكامل على منع التطبيقات من البقاء مستيقظة في الخلفية لحماية عمر البطارية وحرارة المعالج:\n     * **قيود WorkManager**: الحد الأدنى لتكرار المهام الدورية هو 15 دقيقة، ولا تضمن دقة بالثانية إطلاقاً.\n     * **وضع الخمول (Doze Mode)**: يقطع الوصول للشبكة ويعلق المعالج ويؤخر كل المهام لساعات عند ترك الهاتف ثابتاً.\n     * **قيود الخدمات الأمامية (Foreground Services)**: تشغيل Foreground Service بتكرار كل ثانية يستهلك البطارية في 3 ساعات، وستقوم خوارزمية Battery Health بتنبيه المستخدم، وسيرفض متجر Google Play التطبيق فوراً لانتهاكه سياسات استهلاك الطاقة.\n     * **قيود AlarmManager**: التنبيهات المتكررة كل ثانية محظورة برمجياً في النظام؛ التنبيهات الدقيقة صُممت لمواعيد منبهات متباعدة وليس لحلقات تكرار كل ثانية.\n\n"
            "2. كيف يتصرف مهندس Android الأول (Negotiating Senior Solutions):\n   - **رفض الوعد المستحيل فنياً**: شرح قيود المنصة بوضوح لصاحب المنتج (Product Owner).\n   - **إعادة توجيه المتطلب لمعمارية صحيحة (Event-Driven vs. Polling)**:\n     * إذا كان الهدف معرفة تحديثات جديدة: **استبدال الـ Polling بـ Server-Sent Push Notifications (FCM)** أو WebSockets أثناء فتح التطبيق.\n     * إذا كان الهدف حسابات متعلقة بالوقت (مثل عداد تنازلي Timer): الحساب يتم رياضياً بناءً على الـ Timestamp (`targetTime - now`) عند فتح الشاشة، دون الحاجة لحلقة تكرار في الخلفية!"
        ),
        "practical_walkthrough": (
            "المقارنة بين الفكر الساذج المستحيل في الخلفية والحل المعماري الصحيح المدفوع بالأحداث:\n"
            "```kotlin\n"
            "// ❌ فكر ساذج مستحيل: حلقة تكرار كل ثانية في الخلفية (يقتلها النظام ويستنزف البطارية):\n"
            "// while (true) { delay(1000); checkServerUpdates() }\n"
            "// مصير هذا الكود: SIGKILL من Android بعد 60 ثانية، واستنزاف 20% بطارية، ورفض التطبيق في المتجر!\n"
            "\n"
            "// ✅ الحل المعماري الهندسي السليم (Event-Driven via FCM Push Notifications):\n"
            "// السيرفر هو من يراقب الحدث؛ وعند وقوعه يرسل FCM Data Message لإيقاظ التطبيق فوراً:\n"
            "class MyFirebaseMessagingService : FirebaseMessagingService() {\n"
            "    override fun onMessageReceived(remoteMessage: RemoteMessage) {\n"
            "        // يتم استدعاؤه فور وقوع الحدث على السيرفر بدون أي Polling على الهاتف!\n"
            "        val eventData = remoteMessage.data[\"critical_event\"]\n"
            "        \n"
            "        // إظهار إشعار فوري للمستخدم أو جدولة مهمة عبر WorkManager:\n"
            "        NotificationHelper.showNotification(applicationContext, \"New Event\", eventData)\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Android strictly prohibits second-perfect periodic background execution. Battery power features (Doze mode, App Standby Buckets, minimum 15-minute WorkManager intervals, FGS background start restrictions) intentionally prevent continuous background execution. Negotiate the requirement by pivoting to server-driven FCM push notifications, WebSockets during active foreground use, or timestamp math.",
        "best_answer": (
            "A senior engineer must definitively reject requests for second-perfect periodic background execution on Android due to deliberate platform architectural constraints:\n\n"
            "1. **Android Power Management Constraints**:\n   - **WorkManager Inflexibility**: Enforces a strict 15-minute floor for recurring work (`MIN_PERIODIC_INTERVAL_MILLIS`).\n   - **Doze Mode & Standby Buckets**: When the device is idle, CPU sleep states suspend all background loops. Bypassing Doze to wake the CPU every second drains the battery within a few hours and thermal-throttles the SoC.\n   - **OS Enforcement**: Running an endless background loop will trigger Android's Background Execution Limits, resulting in an immediate process `SIGKILL` by the Low Memory Killer.\n   - **Google Play Policy Violations**: Apps abusing wake-locks or running unjustified background services are flagged for excessive wakeups and battery drain (Android Vitals), leading to removal from Google Play.\n\n"
            "2. **Architectural Alternatives to Pitch to Stakeholders**:\n   - **Server-Driven Push (FCM)**: The server tracks real-time state and pushes high-priority FCM notifications only when changes actually occur.\n   - **Foreground Active Streams**: Use WebSockets or SSE only while the app is actively foregrounded by the user.\n   - **Mathematical Calculation**: For timers or auctions, calculate elapsed time algebraically on render (`remaining = targetTimestamp - currentTime`) rather than ticking a background loop."
        ),
        "deep_answer": (
            "The Android Vitals Thresholds for Excessive Wakeups:\n\n"
            "Google Play Console monitors background health using **Android Vitals** metrics:\n\n"
            "- If an app triggers more than **10 background alarms per hour** on battery, it enters the 'Bad Behavior' threshold, resulting in lower search rankings in Google Play.\n"
            "- A request for 'second-perfect execution' requires 3,600 wakeups per hour—360 times higher than the platform maximum penalty threshold!\n\n"
            "Citing concrete platform telemetry and Google Play store ranking penalties transforms a technical disagreement into an undeniable business argument that product stakeholders immediately respect."
        ),
        "follow_ups": [
            {
                "question": "Can `AlarmManager.setRepeating()` be used for a 1-second interval?",
                "answer": "No. Since Android 4.4, AlarmManager automatically inexacts and batches repeating alarms to much longer intervals; 1-second repeat is impossible."
            },
            {
                "question": "What is the battery impact of holding a `WakeLock` continuously?",
                "answer": "A continuous partial WakeLock keeps the CPU active at high power states, draining a full battery in 3–5 hours even with the screen off."
            }
        ]
    },
    {
        "id": "BG-18",
        "arabic_explanation": (
            "عملية عكس/استرداد مالي (Payment Reversal) يجب أن تصل إلى السيرفر حتماً حتى بعد خروج التطبيق. ما هي الآلية المتينة (Durable Mechanism) وعقد السيرفر المطلوب؟\n\n"
            "1. خطورة المعاملة المالية عند خروج التطبيق:\n   - المستخدم ضغط على 'إلغاء الطلب واسترداد المبلغ'.\n   - خرج المستخدم من التطبيق أو أغلق الهاتف في نفس اللحظة.\n   - إذا اعتمد التطبيق على Coroutine في الـ ViewModel، ستُلغى العملية فوراً، وسيظل طلب المستخدم معلقاً ولن يسترد أمواله!\n\n"
            "2. الآلية المتينة المحلية (Durable Client Mechanism):\n   - **تسجيل نية الاسترداد في Room أولاً (Transactional Outbox)**:\n     * قبل إظهار أي رد للـ UI، يتم حفظ المعاملة في جدول `payment_reversals` في Room: `reversalId: UUID`, `originalTransactionId`, `amount`, `status = PENDING_DISPATCH`.\n     * الـ UI تعرض للمستخدم: 'تم طلب الإلغاء، جارِ المعالجة'.\n   - **جدولة المهمة عبر WorkManager**:\n     * إطلاق `OneTimeWorkRequestBuilder<PaymentReversalWorker>()` كـ Unique Work بسياسة `APPEND_OR_REPLACE` مع شرط `NetworkType.CONNECTED`.\n     * سيقوم WorkManager بتنفيذ العملية حتماً حتى لو أُغلق التطبيق أو أعيد تشغيل الهاتف.\n\n"
            "3. عقد السيرفر الإلزامي (The Mandatory Server Contract):\n   - **Idempotency Key**: يرسل العميل `Idempotency-Key: reversalId`. يمنع السيرفر تكرار الاسترداد إذا أُعيد تشغيل الـ Worker.\n   - **State Reconciliation Endpoint**: توفير endpoint استقصائي (`GET /payments/{id}/reversal-status`) يتيح للـ Worker التحقق من حالة الاسترداد لو انقطعت الشبكة بعد إرسال الطلب وقبل استلام الرد."
        ),
        "practical_walkthrough": (
            "التطبيق المعماري المتكامل لنظام استرداد المدفوعات المتين:\n"
            "```kotlin\n"
            "// 1. تسجيل نية الاسترداد محلياً في Room أولاً:\n"
            "class PaymentReversalRepositoryImpl @Inject constructor(\n"
            "    private val db: AppDatabase,\n"
            "    private val workManager: WorkManager\n"
            ") : PaymentReversalRepository {\n"
            "\n"
            "    override suspend fun requestPaymentReversal(transactionId: String, amountCents: Long): ReversalResult {\n"
            "        val reversalId = \"rev_${transactionId}_$amountCents\"\n"
            "        \n"
            "        db.withTransaction {\n"
            "            db.reversalDao().insertIntent(\n"
            "                ReversalEntity(\n"
            "                    id = reversalId,\n"
            "                    transactionId = transactionId,\n"
            "                    amountCents = amountCents,\n"
            "                    status = ReversalStatus.PENDING\n"
            "                )\n"
            "            )\n"
            "        }\n"
            "\n"
            "        // جدولة موثوقة في WorkManager:\n"
            "        val workRequest = OneTimeWorkRequestBuilder<PaymentReversalWorker>()\n"
            "            .setInputData(workDataOf(\"reversal_id\" to reversalId))\n"
            "            .setConstraints(Constraints.Builder().setRequiredNetworkType(NetworkType.CONNECTED).build())\n"
            "            .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 15, TimeUnit.SECONDS)\n"
            "            .build()\n"
            "\n"
            "        workManager.enqueueUniqueWork(\"reversal_$reversalId\", ExistingWorkPolicy.KEEP, workRequest)\n"
            "        return ReversalResult.Submitted(reversalId)\n"
            "    }\n"
            "}\n"
            "\n"
            "// 2. الـ Worker المتين المحمي ضد التكرار وانقطاع الشبكة:\n"
            "class PaymentReversalWorker(context: Context, params: WorkerParameters) : CoroutineWorker(context, params) {\n"
            "    override suspend fun doWork(): Result {\n"
            "        val revId = inputData.getString(\"reversal_id\") ?: return Result.failure()\n"
            "        val db = EntryPoints.get(applicationContext, DbEntryPoint::class.java).database()\n"
            "        val api = EntryPoints.get(applicationContext, PaymentApiEntryPoint::class.java).api()\n"
            "\n"
            "        val entity = db.reversalDao().getReversal(revId) ?: return Result.failure()\n"
            "        if (entity.status == ReversalStatus.CONFIRMED) return Result.success()\n"
            "\n"
            "        return try {\n"
            "            val response = api.executeReversal(idempotencyKey = entity.id, transactionId = entity.transactionId)\n"
            "            db.reversalDao().markConfirmed(revId, response.settlementId)\n"
            "            Result.success()\n"
            "        } catch (e: IOException) {\n"
            "            Result.retry()\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Execute durable payment reversals after app exit by committing a persistent reversal intent to a Room Outbox table before notifying the user. Enqueue a unique WorkManager task with network constraints. The backend must enforce strict idempotency via client-supplied idempotency keys and provide status reconciliation endpoints to prevent duplicate reversals.",
        "best_answer": (
            "Guaranteeing that a mission-critical financial reversal completes after the user exits the app requires integrating persistent local queuing with strict backend transaction contracts:\n\n"
            "1. **Durable Outbox Persistence in Room**:\n   - Prior to providing feedback to the user, persist the reversal command in Room within an ACID transaction: `{ reversalId: UUID, originalTxId, amount, status = PENDING_DISPATCH }`.\n   - The UI displays: 'Cancellation submitted'. If the user immediately swipes the app away, the intent is safe in persistent flash storage.\n\n"
            "2. **Resilient Dispatch via WorkManager**:\n   - Enqueue a `OneTimeWorkRequestBuilder<PaymentReversalWorker>()` with `ExistingWorkPolicy.KEEP`, `NetworkType.CONNECTED`, and exponential backoff.\n   - WorkManager guarantees execution across app exits, background memory kills, and device reboots.\n\n"
            "3. **Server-Side Idempotency & Reconciliation Contract**:\n   - **Idempotency Key**: The client submits `Idempotency-Key: reversalId`. The backend uses distributed locks to prevent duplicate refund execution if the worker runs multiple times.\n   - **Status Reconciliation**: If the client encounters a network timeout after dispatching, it queries `GET /reversals/{reversalId}` to resolve the status before re-attempting mutations."
        ),
        "deep_answer": (
            "The Ultimate Failure Scenario: **The Indefinite Offline Device**.\n\n"
            "What happens if the user issues a payment reversal and then turns off their phone for two weeks? "
            "Financial institutions enforce settlement windows (e.g. Visa/Mastercard transaction voids must occur within 24–48 hours, after which they must be processed as refunds rather than voids).\n\n"
            "To handle this distributed timing hazard:\n"
            "- The reversal entity in Room includes `expiresAtMillis = System.currentTimeMillis() + 48.hours`.\n"
            "- If the worker awakens after the expiration window has passed, it does not submit a raw void. It submits a specialized `ExpiredReversalClaim` endpoint, allowing backend risk engines to route the transaction to manual support reconciliation."
        ),
        "follow_ups": [
            {
                "question": "What is the difference between a Payment Void and a Payment Refund?",
                "answer": "A Void cancels an unsettled transaction before funds transfer; a Refund returns settled funds after the transaction has closed."
            },
            {
                "question": "Why shouldn't a payment reversal rely on push notifications to trigger?",
                "answer": "Push notifications require device connectivity to receive; an offline client cannot receive a push to initiate work."
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

    for item in BG_13_18:
        by_id[item["id"]] = item

    output = [by_id[k] for k in sorted(by_id.keys())]
    DATA_FILE.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {DATA_FILE} with questions BG-13 to BG-18. Total questions: {len(output)}")

if __name__ == "__main__":
    main()
