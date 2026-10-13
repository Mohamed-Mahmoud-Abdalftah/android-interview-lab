#!/usr/bin/env python3
"""Generator for BG-07 through BG-12 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "bg.json"

BG_07_12 = [
    {
        "id": "BG-07",
        "arabic_explanation": (
            "ما هو الفرق الجوهري بين العمل المرتبط بدورة الحياة (Lifecycle-Bound Work) والعمل الدائم (Durable Work) في Android؟\n\n"
            "1. العمل المرتبط بدورة الحياة (Lifecycle-Bound Work):\n   - **فترة البقاء**: يعيش فقط طالما أن المكون البرمجي الخاص به حي في الذاكرة (مثل `Activity` أو `Fragment` أو `ViewModel`).\n   - **كيف يُنفذ**: عبر `lifecycleScope.launch` أو `viewModelScope.launch`.\n   - **سلوكه عند الخروج**: إذا ضغط المستخدم على زر الرجوع (Back) أو غادر الشاشة، يُلغى الكوروتين فوراً وتتوقف العملية.\n   - **متى يُستخدم**: للمهام العابرة التي لا معنى لها بدون شاشة: البحث الفوري أثناء الكتابة (Autocomplete/Search debounce)، تحميل صورة لعرضها الآن، أو استماع للـ Sensors لتحديث أنيميشن الشاشة.\n\n"
            "2. العمل الدائم الموثوق (Durable Work):\n   - **فترة البقاء**: ينجو من موت الشاشة، وموت الـ Process، وإعادة تشغيل الهاتف (Survives Process Death and Device Reboot).\n   - **كيف يُنفذ**: يجب أن يبدأ بحفظ نية العملية (Intent) في قاعدة بيانات محلية دائمية (Room / SQLite Outbox)، ثم جدولتها عبر `WorkManager`.\n   - **متى يُستخدم**: للعمليات التجارية الهامة التي وعدت المستخدم بتنفيذها: إرسال رسالة شات، إتمام دفع، حفظ طلب، رفع ملف بعد ضغط 'إرسال'، أو مزامنة التعديلات غير المتصلة.\n\n"
            "3. الفخ الشائع (The GlobalScope Illusion):\n   - يعتقد بعض المطورين أن استخدام `GlobalScope.launch` أو `CoroutineScope(SupervisorJob())` يجعل العمل 'دائماً'. هذا وهم خطير! بمجرد قيام Android OS بإنهاء عملية التطبيق (Kill Process) لتوفير الذاكرة، تموت كل خيوط الـ JVM فوراً وتضيع العملية للأبد إذا لم تكن مسجلة في Room و WorkManager."
        ),
        "practical_walkthrough": (
            "المقارنة البرمجية بين العمل المرتبط بالشاشة والعمل الدائم في تطبيق مراسلة:\n"
            "```kotlin\n"
            "// ❌ عمل عابر مرتبط بالشاشة فقط (Lifecycle-bound): لو خرج المستخدم تضيع الرسالة:\n"
            "class ChatViewModel : ViewModel() {\n"
            "    fun sendMessageWrong(text: String) {\n"
            "        viewModelScope.launch {\n"
            "            // لو أغلق المستخدم الشاشة فوراً -> يُلغى viewModelScope ولن تصل الرسالة أبداً!\n"
            "            chatApi.send(text)\n"
            "        }\n"
            "    }\n"
            "}\n"
            "\n"
            "// ✅ عمل دائم موثوق (Durable Work): يضمن وصول الرسالة حتى لو أُغلق التطبيق فوراً:\n"
            "class ChatRepositoryImpl @Inject constructor(\n"
            "    private val messageDao: MessageDao,\n"
            "    private val workManager: WorkManager\n"
            ") : ChatRepository {\n"
            "    suspend fun sendMessageDurable(text: String) {\n"
            "        // 1. حفظ الرسالة محلياً في Room أولاً بحالة PENDING_SEND:\n"
            "        val messageId = UUID.randomUUID().toString()\n"
            "        messageDao.insert(MessageEntity(id = messageId, text = text, status = SyncStatus.PENDING))\n"
            "        \n"
            "        // 2. جدولة إرسال موثوق عبر WorkManager:\n"
            "        val sendWork = OneTimeWorkRequestBuilder<SendMessageWorker>()\n"
            "            .setInputData(workDataOf(\"message_id\" to messageId))\n"
            "            .setConstraints(Constraints.Builder().setRequiredNetworkType(NetworkType.CONNECTED).build())\n"
            "            .build()\n"
            "        workManager.enqueueUniqueWork(\"send_$messageId\", ExistingWorkPolicy.KEEP, sendWork)\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Lifecycle-bound work is in-process and cancelled immediately when the UI component or ViewModel dies (viewModelScope). Durable work is persistent work that must complete regardless of UI navigation, process death, or device reboots, implemented by saving state to Room and executing via WorkManager.",
        "best_answer": (
            "The distinction between lifecycle-bound work and durable work is fundamental to Android reliability:\n\n"
            "1. **Lifecycle-Bound Work (In-Process & Ephemeral)**:\n   - Managed by coroutines scopes tied to Android components (`viewModelScope`, `lifecycleScope`).\n   - Its value exists strictly while the user is actively viewing the screen. When the lifecycle owner transitions to `DESTROYED`, structured concurrency cancels child coroutines.\n   - Examples: UI animation coordination, search query filtering, loading viewport items.\n\n"
            "2. **Durable Work (Process-Independent & Persistent)**:\n   - The work represents a user commitment that must complete even if the user leaves the app, the OS terminates the process in the background, or the device reboots.\n   - Implemented via a **Persistent Outbox pattern in Room** orchestrated by **WorkManager**.\n   - Examples: Chat message dispatch, offline payment authorization, media upload.\n\n"
            "A critical pitfall is using `GlobalScope` or application-level coroutine scopes for critical work: they live in process memory; when Android kills the process, uncompleted work is lost forever."
        ),
        "deep_answer": (
            "From an OS process hierarchy standpoint, Android manages memory through **Low Memory Killer Daemon (LMKD)** and OOM Adjustment (`oom_adj`) scores:\n\n"
            "- When an app is in the foreground, its `oom_adj` score is 0 (`FOREGROUND_APP`), giving it maximum CPU priority.\n"
            "- As soon as the user presses Home, the app transitions to `CACHED_APP` (`oom_adj >= 900`). The Linux kernel can reclaim and SIGKILL the process at any moment without warning to free RAM for other apps.\n\n"
            "Any in-flight thread or coroutine in memory terminates instantly during a process kill. "
            "Durable work solves this because WorkManager registers the task with the OS platform scheduler (`JobScheduler`), which acts as an external watchdog outside the app's process, respawning the app when system resources or network connectivity allow."
        ),
        "follow_ups": [
            {
                "question": "Can an Application-scoped coroutine (`ProcessLifecycleOwner`) survive process death?",
                "answer": "No. It survives Activity destruction, but when the OS kills the process or the user swipes the app away, all in-memory coroutine scopes terminate."
            },
            {
                "question": "What is the role of Room in durable work?",
                "answer": "Room acts as the local source of truth for the entity state and the mutation outbox, ensuring the worker has durable data to resume from after a crash."
            }
        ]
    },
    {
        "id": "BG-08",
        "arabic_explanation": (
            "كيف تدير طابور المزامنة في وضع عدم الاتصال (Offline Sync Queue) وإعادة المحاولة عبر WorkManager؟\n\n"
            "1. معمارية طابور الـ Outbox:\n   - **جدول الـ Outbox في Room**: جدول محلي يحتوي على العمليات المعلقة: `id`, `entity_type`, `action (INSERT/UPDATE/DELETE)`, `payload_json`, `created_at`, `status`.\n   - **الذرية المحلية**: عند قيام المستخدم بأي تعديل، يُكتب التعديل في جدول البيانات الأساسي وفي جدول الـ Outbox معاً داخل `database.withTransaction`.\n\n"
            "2. جدولة وتفعيل المزامنة:\n   - يتم إطلاق `SyncOutboxWorker` كـ Unique Work بسياسة `KEEP` مع شرط `NetworkType.CONNECTED`.\n   - إذا كان الهاتف متصلاً، يبدأ العمل فوراً؛ وإذا كان غير متصل، ينتظر في صمت دون استهلاك أي موارد حتى تتوفر الشبكة.\n\n"
            "3. معالجة الأخطاء وإعادة المحاولة بذكاء:\n   - أخطاء الشبكة المؤقتة والـ Timeouts: يُرجع الـ Worker تعليمة `Result.retry()`، ويطبق WorkManager سياسة الـ Exponential Backoff.\n   - أخطاء السيرفر الدائمة (400 Bad Request): يتم تسجيل الخطأ محلياً ووسمه كـ FAILED لمنع حظر الطابور.\n   - أخطاء التعارض (409 Conflict): تحويل السجل إلى حالة `CONFLICT` لعرض شاشة تسوية للمستخدم."
        ),
        "practical_walkthrough": (
            "تنفيذ طابور المزامنة التتابعي المتكامل في CoroutineWorker:\n"
            "```kotlin\n"
            "@HiltWorker\n"
            "class OutboxDrainWorker @AssistedInject constructor(\n"
            "    @Assisted context: Context,\n"
            "    @Assisted params: WorkerParameters,\n"
            "    private val db: AppDatabase,\n"
            "    private val api: SyncApiService\n"
            ") : CoroutineWorker(context, params) {\n"
            "\n"
            "    override suspend fun doWork(): Result {\n"
            "        // 1. قراءة أقدم العمليات المعلقة بالترتيب الزمني (FIFO):\n"
            "        val pendingActions = db.outboxDao().getPendingActions(limit = 10)\n"
            "        if (pendingActions.isEmpty()) return Result.success()\n"
            "\n"
            "        for (action in pendingActions) {\n"
            "            try {\n"
            "                // 2. إرسال العملية مع مفتاح تكرار فريد وثابت:\n"
            "                api.syncAction(action.id, action.actionType, action.payloadJson)\n"
            "                \n"
            "                // 3. حذف العملية من الطابور بعد تأكيد السيرفر:\n"
            "                db.withTransaction {\n"
            "                    db.outboxDao().deleteAction(action.id)\n"
            "                    db.itemsDao().markSynced(action.targetEntityId)\n"
            "                }\n"
            "            } catch (e: IOException) {\n"
            "                // انقطاع شبكة عابر: نطلب إعادة المحاولة تلقائياً بـ Exponential Backoff:\n"
            "                return Result.retry()\n"
            "            } catch (e: HttpException) {\n"
            "                if (e.code() in 400..499 && e.code() != 409) {\n"
            "                    // خطأ دائم في العميل: نحذف من الطابور لمنع تعليق باقي العمليات:\n"
            "                    db.outboxDao().markPermanentFailure(action.id, e.message())\n"
            "                } else {\n"
            "                    return Result.retry()\n"
            "                }\n"
            "            }\n"
            "        }\n"
            "        return Result.success()\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Queue offline sync by committing mutations to a Room outbox table and triggering a constrained WorkManager worker. When online, the worker processes outbox records sequentially using idempotency keys, deletes acknowledged records, and returns Result.retry() on transient network failures to invoke exponential backoff.",
        "best_answer": (
            "Managing offline synchronization through WorkManager relies on the **Transactional Outbox Pattern** to guarantee consistency between local database state and backend services:\n\n"
            "1. **Outbox Persistence**: When the user creates or edits data while offline, commit the mutation to the entity table and an `outbox_mutations` table atomically within a single `roomDatabase.withTransaction { }`. This ensures zero mutations exist without a corresponding sync intent.\n\n"
            "2. **Constraint-Driven Dispatch**: Trigger `OneTimeWorkRequestBuilder<SyncWorker>()` configured with `NetworkType.CONNECTED` and an exponential backoff policy, submitted via `enqueueUniqueWork(..., ExistingWorkPolicy.KEEP)`.\n\n"
            "3. **Sequential Execution & Idempotency**: The worker reads outbox entries in FIFO order. Each request attaches `Idempotency-Key: <outboxId>`. Upon HTTP 200/201, the entry is deleted from the outbox in a database transaction.\n\n"
            "4. **Error Partitioning**: Transient network drops return `Result.retry()`. Permanent validation failures (HTTP 400) are flagged and removed from the active queue to prevent pipeline head-of-line blocking."
        ),
        "deep_answer": (
            "A critical engineering requirement in outbox processing is **Preventing Head-of-Line (HoL) Blocking**.\n\n"
            "If Mutation #1 in the queue is malformed and permanently triggers an unhandled HTTP 500 or validation error, a naive FIFO queue will retry Mutation #1 endlessly, completely stalling Mutations #2 through #50 behind it.\n\n"
            "To solve HoL blocking in production:\n"
            "- Implement a `retry_count` column on outbox records. If an individual record fails 5 times, quarantine it to a `dead_letter_queue` table, notify the user with a localized sync alert, and proceed to process the remaining queue items.\n"
            "- Ensure the backend returns structured error envelopes distinguishing transient server overloads from permanent validation rejections."
        ),
        "follow_ups": [
            {
                "question": "What happens if the phone reboots while the outbox queue has 20 pending items?",
                "answer": "WorkManager reconstructs the worker from SQLite upon device reboot and executes it as soon as the network connected constraint is satisfied."
            },
            {
                "question": "Why shouldn't you send all 20 outbox items concurrently in parallel coroutines?",
                "answer": "Parallel dispatch risks out-of-order execution on the server (e.g. executing an item update before its creation has processed)."
            }
        ]
    },
    {
        "id": "BG-09",
        "arabic_explanation": (
            "كيف تلغي أو تستبدل المهام الخلفية الفريدة (Cancel & Replace Unique Work) في WorkManager؟ وما هي الحدود البرمجية؟\n\n"
            "1. آليات الإلغاء والاستبدال في WorkManager:\n   - **الإلغاء بالاسم الفريد (Cancel by Name)**: `workManager.cancelUniqueWork(\"upload_media\")`.\n   - **الإلغاء بالمعرف الفريد (Cancel by UUID)**: `workManager.cancelWorkById(uuid)`.\n   - **الإلغاء بالوسم (Cancel by Tag)**: `workManager.cancelAllWorkByTag(\"user_123\")`.\n   - **الاستبدال بالسياسة (ExistingWorkPolicy.REPLACE)**:\n     * عند إرسال طلب جديد بنفس الاسم، يقوم WorkManager تلقائياً بإلغاء المهمة السابقة واستبدالها بالمهمة الجديدة فوراً.\n\n"
            "2. ما الذي يعنيه 'الإلغاء' محلياً (Local Cooperative Cancellation):\n   - الإلغاء هو إشارة محلية (Signal). إذا كانت المهمة قيد التشغيل بالفعل داخل `CoroutineWorker`، يقوم WorkManager بإلغاء الـ Coroutine Context وإطلاق `CancellationException`.\n   - يجب أن يتعاون كود الـ Worker مع الإلغاء بفحص `isStopped` أو التوقف عند نقاط التعليق (Suspension Points) وتحرير الموارد (مثل حذف ملف مؤقت).\n\n"
            "3. الحدود البرمجية الكبرى (What Cancellation CANNOT Do):\n   - **إلغاء المهمة في WorkManager لا يلغي العملية على السيرفر!**\n   - إذا أرسل الـ Worker طلب HTTP وقبله السيرفر، فإن إلغاء الـ Worker محلياً لا يمنع السيرفر من إتمام العملية. إذا كانت العملية تتطلب إلغاءً فعلياً على السيرفر (مثل إلغاء حجز أو إرجاع طلب)، يجب إرسال طلب HTTP صريح للإلغاء (`POST /cancel`)."
        ),
        "practical_walkthrough": (
            "المقارنة العملية بين استبدال المهمة والإلغاء التعاوني داخل الـ Worker:\n"
            "```kotlin\n"
            "// 1. استبدال مهمة جارية بمهمة أحدث (ExistingWorkPolicy.REPLACE):\n"
            "// ممتاز لمزامنة شاشات مثل البحث أو الفلترة حيث تلغي الفلاتر الجديدة الفلاتر القديمة:\n"
            "fun enqueueUpdatedFilterSync(context: Context, newFilterQuery: String) {\n"
            "    val request = OneTimeWorkRequestBuilder<SyncFilterWorker>()\n"
            "        .setInputData(workDataOf(\"query\" to newFilterQuery))\n"
            "        .build()\n"
            "\n"
            "    // REPLACE: يلغي أي Worker قيد التشغيل حالياً بنفس الاسم ويشغل الجديد فوراً:\n"
            "    WorkManager.getInstance(context).enqueueUniqueWork(\n"
            "        \"active_filter_sync\",\n"
            "        ExistingWorkPolicy.REPLACE,\n"
            "        request\n"
            "    )\n"
            "}\n"
            "\n"
            "// 2. داخل CoroutineWorker: التعامل مع إشارة الإلغاء وتنظيف الموارد:\n"
            "class SyncFilterWorker(context: Context, params: WorkerParameters) : CoroutineWorker(context, params) {\n"
            "    override suspend fun doWork(): Result {\n"
            "        return try {\n"
            "            // فحص الإلغاء التعاوني:\n"
            "            filterApi.fetchFilteredData()\n"
            "            Result.success()\n"
            "        } catch (e: CancellationException) {\n"
            "            // يتم استدعاؤه فور قيام REPLACE أو cancel بإلغاء المهمة:\n"
            "            cleanUpTempFiles()\n"
            "            throw e // إعادة إطلاق الاستثناء لإعلام WorkManager\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Cancel unique work by name or tag via cancelUniqueWork(), or replace it automatically using ExistingWorkPolicy.REPLACE. Cancellation triggers cooperative cancellation in CoroutineWorker via CancellationException. However, cancelling a local worker does not undo server-side mutations already committed over the network.",
        "best_answer": (
            "Managing lifecycle transitions for unique background work involves coordinating local scheduling states with external network operations:\n\n"
            "1. **Cancellation APIs**:\n   - `cancelUniqueWork(name)`: Cancels all pending or running jobs registered under that unique name.\n   - `cancelAllWorkByTag(tag)`: Cancels all tasks sharing a domain tag (e.g. `tag = \"upload_user_42\"`).\n\n"
            "2. **ExistingWorkPolicy.REPLACE**:\n   - When submitting a new work request under an active unique name, `REPLACE` instructs WorkManager to immediately mark the existing running worker as stopped and queue the new request. Ideal for user interactions where latest input invalidates previous work (e.g. search query syncing or draft autosaving).\n\n"
            "3. **Cooperative Cancellation Mechanics**:\n   - In `CoroutineWorker`, cancellation is cooperative. The coroutine job is cancelled, causing suspension points to throw `CancellationException`. Developers must clean up local file descriptors and temporary staging caches in `finally` blocks.\n\n"
            "4. **The Network Boundary Limit**: Cancelling a local worker sends an interrupt to the device socket; it does **not** roll back mutations already received and committed by backend databases. Reversing committed server state requires an explicit domain reversal endpoint."
        ),
        "deep_answer": (
            "When a worker is cancelled via `REPLACE` while actively executing an HTTP call, OkHttp's underlying socket is interrupted.\n\n"
            "If the server already processed the request, the client observes an `IOException` due to socket cancellation. "
            "If the app re-submits a similar operation without tracking operation identity, it risks duplicating business side-effects. "
            "To safeguard against this in financial operations, never use `ExistingWorkPolicy.REPLACE` for non-idempotent mutations. Reserve `REPLACE` strictly for idempotent queries, cache updates, and read-side synchronization."
        ),
        "follow_ups": [
            {
                "question": "What is the difference between `ExistingWorkPolicy.KEEP` and `REPLACE`?",
                "answer": "`KEEP` ignores the new request and lets the current work finish; `REPLACE` terminates the current work and starts the new request."
            },
            {
                "question": "Can cancelled work be restarted?",
                "answer": "No. Once a work request reaches the `CANCELLED` terminal state in WorkManager, it cannot be restarted; a new WorkRequest must be enqueued."
            }
        ]
    },
    {
        "id": "BG-10",
        "arabic_explanation": (
            "كيف تحفظ تقدم المهمة الخلفية (Persist Progress) وتنقله لشاشة المستخدم (Communicate with UI) بأمان؟\n\n"
            "1. طريقتان للتواصل بين WorkManager والـ UI:\n   - **الطريقة 1: آلية WorkManager الرسمية (`setProgress` و `getWorkInfoByIdFlow`)**:\n     * يستدعي الـ Worker دالة `setProgress(workDataOf(\"progress\" to 65))` أثناء العمل.\n     * في الـ UI، يراقب الـ ViewModel تدفق `workManager.getWorkInfoByIdFlow(uuid)` ويقرأ نسبة التقدم من `workInfo.progress`.\n     * **المميزات**: مدمجة وسهلة للمهام الفورية والأنيميشن.\n     * **العيوب**: التقدم عابر وغير متين؛ إذا انتهت المهمة أو مات الـ Worker، لا يعود الـ progress متاحاً بالتفصيل.\n   - **الطريقة 2: المعيار المعماري الموصى به (Room as Single Source of Truth)**:\n     * يكتب الـ Worker نسبة التقدم ومراحله مباشرة في جدول قاعدة بيانات Room (`upload_tasks` table).\n     * يراقب الـ ViewModel تدفق `taskDao.observeTask(taskId): Flow<TaskEntity>`.\n     * **المميزات**: متين ومستمر 100%، ينجو من موت الـ Process وإعادة التشغيل، ويعمل حتى لو كانت الشاشة مغلقة وفتحها المستخدم لاحقاً.\n\n"
            "2. أفضل ممارسة في الإنتاج:\n   - دمج الطريقتين: استخدام Room للبيانات المتينة وحالة المهمة العامة (`PENDING`, `UPLOADING`, `COMPLETED`)، واستخدام `setProgress` لعرض شريط تقدم ناعم (Progress Bar Animation) أثناء فتح الشاشة."
        ),
        "practical_walkthrough": (
            "تحديث التقدم عبر WorkManager وعبر Room وعرضه في Jetpack Compose:\n"
            "```kotlin\n"
            "// 1. داخل الـ CoroutineWorker: تحديث التقدم عبر WorkManager و Room:\n"
            "class UploadVideoWorker(context: Context, params: WorkerParameters) : CoroutineWorker(context, params) {\n"
            "    override suspend fun doWork(): Result {\n"
            "        val taskId = inputData.getString(\"task_id\")!!\n"
            "        val db = EntryPoints.get(applicationContext, DbEntryPoint::class.java).database()\n"
            "        \n"
            "        for (percent in 1..100 step 10) {\n"
            "            delay(500) // محاكاة الرفع\n"
            "            \n"
            "            // أ. إرسال تقدم فوري لـ WorkManager UI:\n"
            "            setProgress(workDataOf(\"percent\" to percent))\n"
            "            \n"
            "            // ب. حفظ التقدم الدائم في Room لحمايته عبر إعادة تشغيل التطبيق:\n"
            "            db.uploadDao().updateProgress(taskId, percent)\n"
            "        }\n"
            "        return Result.success()\n"
            "    }\n"
            "}\n"
            "\n"
            "// 2. في الـ ViewModel: مراقبة تقدم المهمة كتدفق تفاعلي:\n"
            "@HiltViewModel\n"
            "class UploadViewModel @Inject constructor(\n"
            "    private val taskDao: UploadTaskDao,\n"
            "    private val workManager: WorkManager\n"
            ") : ViewModel() {\n"
            "    fun observeUploadTask(taskId: String): Flow<UploadTaskEntity?> = taskDao.observeTask(taskId)\n"
            "}\n"
            "\n"
            "// 3. في Jetpack Compose UI:\n"
            "@Composable\n"
            "fun UploadProgressScreen(viewModel: UploadViewModel, taskId: String) {\n"
            "    val task by viewModel.observeUploadTask(taskId).collectAsState(initial = null)\n"
            "    \n"
            "    task?.let {\n"
            "        LinearProgressIndicator(progress = { it.progressPercent / 100f })\n"
            "        Text(\"${it.progressPercent}% Uploaded\")\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Communicate transient worker progress to UI via setProgress() observed through workManager.getWorkInfoByIdFlow(). For durable, mission-critical progress that survives process death and screen re-entry, persist progress directly to Room and observe it as a reactive Flow in ViewModels.",
        "best_answer": (
            "Communicating background progress to the UI requires balancing immediate UI responsiveness against long-term persistence:\n\n"
            "1. **Transient Progress (`setProgress` + `WorkInfo`)**:\n   - Inside `CoroutineWorker`, invoke `setProgress(workDataOf(\"progress\" to percentage))`.\n   - ViewModels observe `workManager.getWorkInfoByIdFlow(uuid)` or `getWorkInfosForUniqueWorkFlow(name)`.\n   - Excellent for driving real-time progress bars and spinners while the user actively watches the screen.\n   - **Limitation**: `WorkInfo.progress` is ephemeral; once the worker finishes with `Result.success()`, the progress map is cleared.\n\n"
            "2. **Durable Business Progress (Room as Single Source of Truth)**:\n   - For multi-step uploads or migrations that may span hours across app restarts, write progress checkpoints directly into an internal Room table (`uploadedBytes`, `totalBytes`, `currentPhase`).\n   - The ViewModel observes `taskDao.observeTaskFlow()`. When the user re-opens the app 3 hours later, the UI immediately displays exact progress from SQLite."
        ),
        "deep_answer": (
            "Performance Guardrail: **Do Not Over-Saturate `setProgress()`**.\n\n"
            "Under the hood, every call to `setProgress()` in WorkManager executes an internal SQLite transaction in `androidx.work.workdb` and broadcasts an Intent to notify observers across processes. "
            "If a worker uploads a file in 4KB chunks and calls `setProgress()` 500 times per second, it will thrash the disk, trigger SQLite lock contention, and drop UI frames.\n\n"
            "**Rule**: Throttle progress updates to at most once every 250–500ms, or emit only when integer percentages change (`if (currentPercent != lastReportedPercent) setProgress(...)`)."
        ),
        "follow_ups": [
            {
                "question": "Can `WorkInfo` observe the state of tasks enqueued by another component?",
                "answer": "Yes, WorkInfo queries are process-wide and can be observed anywhere by UUID, unique name, or tag."
            },
            {
                "question": "What are the possible states in `WorkInfo.State`?",
                "answer": "`ENQUEUED`, `RUNNING`, `SUCCEEDED`, `FAILED`, `BLOCKED`, and `CANCELLED`."
            }
        ]
    },
    {
        "id": "BG-11",
        "arabic_explanation": (
            "كيف تتجنب المعالجة المكررة (Duplicate Processing) عندما يُعاد تشغيل الـ Worker بعد عطل أو فشل؟\n\n"
            "1. حتمية التكرار في WorkManager (At-Least-Once Execution):\n   - يجب أن يدرك كل مهندس أن WorkManager **لا يضمن التنفيذ مرة واحدة فقط (Does NOT guarantee exactly-once)**.\n   - إذا أرسل الـ Worker طلباً بنجاح، ومات التطبيق (Process Crash أو Out of Memory) قبل أن يتمكن من كتابة `Result.success()` في قاعدة بيانات WorkManager، سيعتبر WorkManager المهمة فاشلة ويعيد تشغيلها بالكامل عند الإقلاع التالي!\n\n"
            "2. استراتيجية الحماية المعمارية ضد التكرار (Idempotent Execution Pipeline):\n   - **المعرف الفريد الثابت (Durable Operation ID)**: يجب أن يمرر للمهمة معرف ثابت للعملية (`operationId: UUID`) محفوظ في Room مسبقاً، ولا يجوز توليد معرف جديد داخل الـ Worker.\n   - **فحص الحالة المحلية قبل الإرسال (Pre-Flight Local State Check)**:\n     * عند بدء تشغيل الـ Worker، يفحص قاعدة بيانات Room أولاً:\n     * إذا وجد أن المعاملة مسجلة بالفعل كـ `COMPLETED` أو `ACKNOWLEDGED`، يعيد `Result.success()` فوراً دون لمس السيرفر!\n   - **إرسال الـ Idempotency Key للسيرفر**:\n     * في طلب الشبكة، يرسل `Idempotency-Key: operationId` لضمان أن السيرفر لن يكرر الخصم أو الإنشاء لو وصله الطلب سابقاً."
        ),
        "practical_walkthrough": (
            "كتابة Worker محمي ضد التكرار عند إعادة التشغيل:\n"
            "```kotlin\n"
            "class SafePaymentWorker(context: Context, params: WorkerParameters) : CoroutineWorker(context, params) {\n"
            "    override suspend fun doWork(): Result {\n"
            "        val operationId = inputData.getString(\"op_id\") ?: return Result.failure()\n"
            "        val db = EntryPoints.get(applicationContext, DbEntryPoint::class.java).database()\n"
            "        val api = EntryPoints.get(applicationContext, ApiEntryPoint::class.java).api()\n"
            "\n"
            "        // 1. فحص محلي: هل تم تأكيد هذه العملية مسبقاً قبل الـ Crash؟\n"
            "        val record = db.transactionDao().getTransaction(operationId)\n"
            "        if (record == null) return Result.failure()\n"
            "        if (record.isConfirmed) {\n"
            "            // العملية تمت بالفعل في تشغيل سابق! ننهي بنجاح فوري دون تكرار:\n"
            "            return Result.success()\n"
            "        }\n"
            "\n"
            "        return try {\n"
            "            // 2. إرسال مع Idempotency Key:\n"
            "            val response = api.submitPayment(idempotencyKey = operationId, record.toRequest())\n"
            "            \n"
            "            // 3. تأكيد الحالة محلياً في Room:\n"
            "            db.transactionDao().markConfirmed(operationId, response.receiptId)\n"
            "            Result.success()\n"
            "        } catch (e: IOException) {\n"
            "            Result.retry() // إعادة المحاولة بأمان\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Prevent duplicate processing under Worker retries by treating WorkManager as at-least-once. Pass a persistent operation ID into the worker, check local database state before executing to return success if already completed, and attach client-generated Idempotency Keys to all network requests.",
        "best_answer": (
            "Because WorkManager enforces **At-Least-Once delivery semantics**, workers will occasionally run multiple times for the same logical operation (e.g. if the process is killed after network transmission but before WorkManager marks the task succeeded in SQLite).\n\n"
            "To guarantee idempotent processing without duplicate side-effects:\n\n"
            "1. **Durable Operation Identity**: Never generate operation UUIDs dynamically inside `doWork()`. The business operation ID must be generated upstream, saved to Room, and passed into the worker via `Data.Builder().putString(\"operation_id\", id)`.\n\n"
            "2. **Pre-Flight State Validation**: The first action inside `doWork()` is checking local SQLite state: `if (repository.isOperationAcknowledged(opId)) return Result.success()`. If a previous run already completed the work before a crash, exit immediately.\n\n"
            "3. **Wire-Level Idempotency**: Transmit `Idempotency-Key: <operationId>` on the network call. If the previous attempt succeeded on the backend, the server returns the cached response rather than duplicating the write.\n\n"
            "4. **Atomic Local Commitment**: Persist the server acknowledgment in Room before returning `Result.success()`."
        ),
        "deep_answer": (
            "A subtle failure mode is the **Crash-After-Commit Window**:\n\n"
            "```kotlin\n"
            "api.chargeCard(idempotencyKey, payload) // 1. Server commits card charge\n"
            "// <-- PROCESS KILLED BY OS HERE!\n"
            "db.markConfirmed(id)                   // 2. Never executes\n"
            "return Result.success()                 // 3. Never executes\n"
            "```\n"
            "When WorkManager re-runs the worker, the local database still shows `status = PENDING`. "
            "Because the worker uses the *identical* `idempotencyKey`, the payment API returns the previously generated charge receipt (`HTTP 200` with `Idempotent-Replayed: true`). "
            "The worker parses the receipt, updates SQLite to `status = CONFIRMED`, and returns `Result.success()`. The customer is charged exactly once."
        ),
        "follow_ups": [
            {
                "question": "Can `runAttemptCount` help detect retries in WorkManager?",
                "answer": "Yes. `runAttemptCount` exposes how many times this specific worker has been retried, allowing you to trigger reconciliation on repeated retries."
            },
            {
                "question": "What happens if a worker never returns a Result?",
                "answer": "If a worker hangs or blocks its thread without completing, the OS eventually terminates the worker when timeouts or constraints expire, scheduling a retry."
            }
        ]
    },
    {
        "id": "BG-12",
        "arabic_explanation": (
            "ما هي قيود الخدمات الأمامية (Foreground Service Restrictions) ومتطلبات الإشعارات في إصدارات Android الحديثة؟\n\n"
            "1. التحول الصارم في Android الحديث (Android 12 إلى 15):\n   - تاريخياً، كان المطورون يسيئون استخدام الخدمات الأمامية (Foreground Services) كحيلة لتشغيل كود في الخلفية إلى ما لا نهاية وتفادي قيود النظام.\n   - **Android 12+ (حظر البدء من الخلفية - FGS Background Launch Restrictions)**: حظر النظام تماماً تشغيل أي Foreground Service أثناء وجود التطبيق في الخلفية! محاولة تشغيلها تؤدي إلى انهيار فوري بـ `ForegroundServiceStartNotAllowedException`، باستثناء حالات نادرة (مثل FCM High-Priority Push أو أجهزة بلوتوث متصلة).\n   - **Android 14+ (إلزامية تحديد النوع - Mandatory FGS Types)**: يجب تحديد `android:foregroundServiceType` صريح في الـ Manifest وفي كود التشغيل (مثل `mediaPlayback`, `location`, `connectedDevice`, `health`). إذا شغلت خدمة بنوع غير معلن أو بدون تبرير، ينهار التطبيق فوراً ويرفضه متجر Google Play.\n\n"
            "2. متطلبات الإشعارات (Notification Requirements):\n   - **إشعار دائم وظاهر (Ongoing Notification)**: يجب إرفاق إشعار فوري عبر `startForeground(id, notification)` في غضون 5 إلى 10 ثوانٍ كحد أقصى من بدء الخدمة (وإلا يحدث ANR).\n   - **صلاحية الإشعارات (`POST_NOTIFICATIONS` في Android 13+)**: يجب الحصول على موافقة المستخدم الصريحة لإظهار الإشعارات.\n   - **مركز أمان Android 13 (FGS Task Manager)**: يوفر النظام للمستخدم زراً في شريط الإشعارات يتيح له إيقاف أي Foreground Service قيد التشغيل بضغطة زر واحدة (Stop button)."
        ),
        "practical_walkthrough": (
            "إعداد Foreground Service متوافق مع Android 14 مع تحديد النوع والصلاحيات:\n"
            "```xml\n"
            "<!-- 1. في AndroidManifest.xml: إعلان الصلاحيات ونوع الخدمة المحدد: -->\n"
            "<uses-permission android:name=\"android.permission.FOREGROUND_SERVICE\" />\n"
            "<uses-permission android:name=\"android.permission.FOREGROUND_SERVICE_LOCATION\" />\n"
            "<uses-permission android:name=\"android.permission.POST_NOTIFICATIONS\" />\n"
            "\n"
            "<service\n"
            "    android:name=\".tracking.LocationTrackingService\"\n"
            "    android:foregroundServiceType=\"location\"\n"
            "    android:exported=\"false\" />\n"
            "```\n"
            "\n"
            "```kotlin\n"
            "// 2. في كود الخدمة: ربط الإشعار وتحديد نوع الخدمة في startForeground:\n"
            "class LocationTrackingService : Service() {\n"
            "    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {\n"
            "        val notification = createTrackingNotification()\n"
            "        \n"
            "        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {\n"
            "            // تحديد النوع البرمجي الإلزامي في Android 14+:\n"
            "            startForeground(NOTIFICATION_ID, notification, ServiceInfo.FOREGROUND_SERVICE_TYPE_LOCATION)\n"
            "        } else {\n"
            "            startForeground(NOTIFICATION_ID, notification)\n"
            "        }\n"
            "        \n"
            "        startLocationUpdates()\n"
            "        return START_STICKY\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Android 12+ strictly blocks starting Foreground Services from the background, throwing ForegroundServiceStartNotAllowedException. Android 14+ mandates declaring specific foregroundServiceTypes in Manifest and code (e.g. location, mediaPlayback). A persistent ongoing notification must be attached within seconds, and users can terminate FGS tasks via the Android 13 Task Manager.",
        "best_answer": (
            "Foreground Services in modern Android are subjected to severe architectural restrictions to protect user privacy and battery life:\n\n"
            "1. **Background Start Restrictions (Android 12+)**: Applications cannot launch a Foreground Service while running in the background. Doing so throws a runtime `ForegroundServiceStartNotAllowedException`. Allowed exceptions are narrowly restricted: high-priority FCM notifications, user interaction via widgets or pending intents, or Companion Device Manager exemptions.\n\n"
            "2. **Mandatory Typed Services (Android 14+)**: Android 14 requires specifying an explicit `foregroundServiceType` in `AndroidManifest.xml` and passing it to `startForeground(id, notification, type)`. Permitted types include `camera`, `location`, `mediaPlayback`, `microphone`, `phoneCall`, and `dataSync`. Google Play requires policy justifications for each declared type.\n\n"
            "3. **Notification Governance**: Services must call `startForeground()` within milliseconds of creation with an ongoing notification. Starting in Android 13, the `POST_NOTIFICATIONS` runtime permission is required, and the Android OS Task Manager allows users to stop running Foreground Services directly from the notification shade."
        ),
        "deep_answer": (
            "What should you use instead of Foreground Services for background work?\n\n"
            "Google's official architecture guidance recommends migrating **90% of data-sync Foreground Services to WorkManager**:\n\n"
            "- For background syncing, backups, or offline uploads, use **WorkManager with Constraints**.\n"
            "- If the task is urgent and user-initiated (e.g. sending an instant chat image), use **WorkManager Expedited Work** (`setExpedited()`). On Android 12+, expedited work runs via platform JobScheduler quotas without launching an FGS or requiring background start exemptions.\n\n"
            "Reserve Foreground Services strictly for active, ongoing, user-perceived multimedia, navigation, and live call sessions."
        ),
        "follow_ups": [
            {
                "question": "What is the timeout limit for `dataSync` Foreground Services in Android 14?",
                "answer": "Android 14 enforces a cumulative runtime cap of approximately 6 hours within a 24-hour window for `dataSync` services, after which the OS terminates the service."
            },
            {
                "question": "What exception is thrown if `startForeground()` is not called within 5 seconds of `startForegroundService()`?",
                "answer": "`ForegroundServiceDidNotStartInTimeException` (a specialized fatal ANR exception)."
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

    for item in BG_07_12:
        by_id[item["id"]] = item

    output = [by_id[k] for k in sorted(by_id.keys())]
    DATA_FILE.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {DATA_FILE} with questions BG-07 to BG-12. Total questions: {len(output)}")

if __name__ == "__main__":
    main()
