#!/usr/bin/env python3
"""Elevate BG-10 through BG-18 for bilingual parity and senior spoken answers."""
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
# BG-10: Persist progress and communicate to UI
# ==========================================
DATA["BG-10"] = {
    "concept_en": """Communicating background work progress in WorkManager requires distinguishing between transient in-flight progress and durable state persistence. For active operations, CoroutineWorker invokes setProgress with a Data object, which serializes key-value pairs into WorkManager's internal SQLite database and dispatches updates through reactive WorkInfo streams via getWorkInfoByIdFlow or getWorkInfosByTagFlow. However, WorkManager progress is strictly ephemeral and tied to the RUNNING state; once a worker transitions to SUCCEEDED, FAILED, or CANCELLED, its progress payload is discarded. For multi-step, restartable operations—such as multi-part file uploads or paginated synchronizations—durable progress must be committed directly to a local Room database as an authoritative checkpoint, allowing retried workers to resume rather than restart from scratch.""",
    "walkthrough_en": """Communicating and persisting progress in practice:
```kotlin
// 1. Worker emitting progress during execution
class FileDownloadWorker(
    appContext: Context,
    params: WorkerParameters
) : CoroutineWorker(appContext, params) {
    override suspend fun doWork(): Result = withContext(Dispatchers.IO) {
        val totalBytes = inputData.getLong("TOTAL_BYTES", 1000L)
        var downloaded = 0L

        while (downloaded < totalBytes) {
            downloaded += 100L
            val progressPercent = ((downloaded * 100) / totalBytes).toInt()
            
            // Updates transient progress observed via WorkInfo
            setProgress(workDataOf("PROGRESS" to progressPercent))
            delay(100)
        }
        Result.success(workDataOf("DOWNLOADED_BYTES" to downloaded))
    }
}

// 2. UI observing progress reactively in ViewModel
class DownloadViewModel(private val workManager: WorkManager) : ViewModel() {
    val progressFlow: Flow<Int> = workManager.getWorkInfoByIdFlow(workerId)
        .filterNotNull()
        .map { workInfo ->
            if (workInfo.state == WorkInfo.State.RUNNING) {
                workInfo.progress.getInt("PROGRESS", 0)
            } else 0
        }
}
```""",
    "short_en": """Communicate in-flight worker progress to the UI using setProgress with a Data object in CoroutineWorker, and observe it reactively through WorkManager getWorkInfoByIdFlow or LiveData. Because setProgress data is ephemeral and discarded once the worker exits the RUNNING state, multi-step operations that need to survive retries or app reboots must persist their progress checkpoints directly in a local Room database.""",
    "structured_en": """Communicating background progress effectively involves choosing the right mechanism based on whether progress is transient or durable.
When presenting live feedback for an active worker, CoroutineWorker provides the suspending setProgress method. Calling this function serializes a Data map into WorkManager internal Room database and notifies registered observers. Presentation layers observe this stream by querying getWorkInfoByIdFlow or getWorkInfosByTagFlow on WorkManager, extracting the integer or percentage from WorkInfo progress payload.
The critical architectural limitation is that setProgress is available exclusively while the worker remains in the RUNNING state. As soon as the worker terminates with success or failure, the progress payload is cleared, leaving only terminal outputData.
If an operation requires durable progress tracking across retries, crashes, or device reboots, such as a multi-part file upload, developers should write checkpoint offsets to a Room entity. The UI observes the Room database as the single source of truth, while the worker updates both Room for persistence and setProgress for high-frequency UI updates.""",
    "deep_senior_en": """Under the hood, setProgress performs an asynchronous write into WorkManager internal Room database table and triggers a notification dispatch through the internal LiveData and Flow bus. Because database disk writes carry non-trivial I/O overhead, high-frequency progress reporting can easily saturate SQLite write locks and degrade application responsiveness.
Senior engineers throttle progress emissions inside worker loops, updating setProgress only when progress milestones change significantly, such as every full percentage point or megabyte chunk, rather than after every individual network byte received.
Furthermore, the lifecycle divergence between setProgress and terminal outputData represents a common source of state synchronization bugs. If a presentation screen connects after a worker has completed, observing WorkInfo progress returns an empty Data object. Presentation logic must therefore inspect WorkInfo state: if the state is SUCCEEDED, the UI should read the final outputData or the underlying domain database rather than relying on progress.
For mission-critical multi-step background pipelines, staff engineers combine WorkManager with an Outbox pattern in Room. The worker writes step completions and chunk byte offsets directly to the domain database inside atomic transactions. If the operating system terminates the process midway through execution, the rescheduled worker queries Room for the latest committed checkpoint, seamlessly resuming transmission without re-uploading completed segments or corrupting backend state.""",
    "meta_ar": {
        "id": "BG-10",
        "questionAr": "كيف تحفظ تقدم المهمة (Progress) وتبلغه لواجهة المستخدم في WorkManager؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على التمييز بين التقدم اللحظي العابر والتقدم الدائم في WorkManager، واستخدام setProgress ومراقبة WorkInfo، وتصميم آليات الحفظ الدائم في Room للعمليات الطويلة.",
        "why_it_matters_ar": "الاعتماد على setProgress لتخزين بيانات حيوية يتسبب في فقدانها بمجرد انتهاء المهمة، وإرسال التقدم بمعدل مرتفع جداً يستهلك رامات الجهاز ويغرق قاعدة بيانات SQLite الداخلية.",
        "worked_example_ar": "إرسال التقدم من الـ Worker واستقباله في الـ ViewModel:\n```kotlin\n// داخل CoroutineWorker\nsetProgress(workDataOf(\"PERCENT\" to 75))\n// في الـ ViewModel\nval progress = workManager.getWorkInfoByIdFlow(id)\n    .map { it?.progress?.getInt(\"PERCENT\", 0) ?: 0 }\n```",
        "trade_offs_ar": "دالة setProgress ممتازة لتحديث الواجهة الحية بسرعة لكنها تموت مع انتهاء الـ Worker، بينما الحفظ في Room يضمن الاستمرارية بعد الانهيار لكنه يتطلب كوداً إضافياً ومعاملات قاعدة بيانات.",
        "failure_modes_ar": "محاولة قراءة التقدم بعد اكتمال المهمة والوصول لحالة SUCCEEDED فيظهر صفر للواجهة، أو استدعاء setProgress مع كل بايت مما يسبب بطء شديد وتجميد لقاعدة البيانات الداخلية.",
        "production_perspective_ar": "في المشروعات الإنتاجية كرفع الفيديوهات، نحدد معدل إرسال setProgress بنسبة 1% فقط، ونسجل الأجزاء المكتملة في Room Database كـ Checkpoints لاستئناف الرفع عند انقطاع الشبكة.",
        "how_to_answer_ar": "ابدأ بتوضيح آلية setProgress ومراقبة WorkInfo Flow، ثم بين نقطة الضعف القاتلة وهي أنها مؤقتة ومرتبطة بحالة RUNNING فقط، واشرح كيف تدمج Room للحفظ الدائم والاستئناف.",
        "talking_points_ar": "استخدام setProgress في CoroutineWorker، وتدفقات WorkInfo التفاعلية، ومحدودية بقاء التقدم بحالة RUNNING، والتخزين الدائم في Room للعمليات المقسمة لأجزاء (Chunking).",
        "follow_ups_ar": "- **المحاور:** \"ماذا يحدث للـ Progress Data بمجرد أن يرجع الـ Worker نتيجة Result.success()؟\"\n  **المرشح:** \"الـ Progress بيتمسح تماماً وبيرجع فاضي، وأي نتيجة نهائية لازم تتبعت في كائن outputData مش في progress.\"\n\n- **المحاور:** \"لو عندنا رفع ملف 2 جيجابايت والـ Process ماتت، هل setProgress هيساعدنا نستأنف الرفع؟\"\n  **المرشح:** \"لا نهائياً؛ لأن setProgress عابر، والحل الصحيح هو تسجيل الـ Byte Offset في جدول Room محلي والاعتماد على سيرفر بيدعم Resumable Uploads.\"",
        "self_check_ar": "هل فرقت بين التقدم العابر والدائم؟ هل وضحت اختفاء progress بعد حالة RUNNING؟ وهل شرحت ترشيد معدل استدعاء setProgress؟",
        "references_ar": f"- [WorkManager Progress](https://developer.android.com/topic/libraries/architecture/workmanager/how-to/intermediate-progress) — الدليل الرسمي لمتابعة التقدم المرحلي للمهام.\n- [Observing Work](https://developer.android.com/topic/libraries/architecture/workmanager/how-to/observe-work) — مراقبة كائنات WorkInfo عبر Flow و LiveData.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "بنبلغ واجهة المستخدم بالتقدم اللحظي للمهمة باستخدام دالة setProgress داخل الـ CoroutineWorker، والواجهة بتستقبله من خلال تدفق getWorkInfoByIdFlow. لكن لازم ناخد بالنا إن بيانات setProgress مؤقتة وبترتبط فقط بحالة RUNNING وبتتمسح بمجرد اكتمال المهمة، فلو محتاجين حفظ دائم لنقاط التقدم يستمر بعد الريستارت أو إعادة المحاولة، بنسجل التقدم في قاعدة بيانات Room المحلية.",
        "best_answer_ar": "إبلاغ وحفظ تقدم المهام في WorkManager بيتطلب فهم الفارق بين التقدم اللحظي والتقدم الدائم عبر دورة حياة المهمة.\n\nلتحديث واجهة المستخدم أثناء تشغيل المهمة، CoroutineWorker بيوفر دالة التعليق `setProgress()` اللي بتمرر كائن Data بيحتوي على نسبة التقدم. والـ ViewModel بيقدر يراقب التقدم ده بشكل تفاعلي ومباشر من خلال دالة `getWorkInfoByIdFlow()` على كائن WorkManager واستخراج القيمة من `workInfo.progress`.\n\nلكن النقطة المعمارية الأهم هي إن بيانات `setProgress` تعتبر عابرة؛ يعني متاحة فقط طالما الـ Worker في حالة `RUNNING`. أول ما الـ Worker يخلص ويرجع `Result.success()`، كائن الـ progress بيتفرغ تماماً، والبيانات النهائية بتتنقل في كائن `outputData`.\n\nعلشان كده، لو بنفذ عملية طويلة ومقسمة زي رفع ملفات كبيرة ومحتاجين استئنافها بعد الانهيار أو إعادة المحاولة، الحل المعتمد هو حفظ نقاط التقدم (Checkpoints) داخل جدول في Room Database. الواجهة بتراقب Room كمصدر وحيد للحقيقة، والـ Worker بيسجل فيها كل خطوة بتكتمل لضمان الاستمرارية التامة.",
        "deep_answer_ar": "تحت الكابوت، استدعاء `setProgress` بيترجم لعملية كتابة غير متزامنة في قاعدة بيانات Room SQLite الداخلية الخاصة بمكتبة WorkManager، ومنها بيتبعت إشعار لتدفقات Flow و LiveData. ولأن عمليات الكتابة على القرص بتستهلك موارد، استدعاء `setProgress` مع كل بايت بيوصل من الشبكة هيؤدي لتجميد قاعدة البيانات وإبطاء التطبيق بالكامل.\n\nالمهندسون الكبار بيعملوا Throttling لبيانات التقدم؛ بحيث يتم إرسال التحديث فقط لما النسبة تتغير بقيمة ملحوظة كزيادة 1% أو انتهاء مرحلة كاملة، وده بيحافظ على سلاسة المعالجة واستقرار الـ SQLite Write Locks.\n\nبالإضافة لده، مشكلة شائعة بتحصل لما شاشة المستخدم تفتح بعد ما الـ Worker يكون خلص بالفعل؛ لو الـ ViewModel قرأ من `workInfo.progress` هيلاقيه فاضي ويعرض صفر للمستخدم! التصميم الصحيح بيفحص حالة `workInfo.state` أولاً: لو كانت انتهت بنجاح، الواجهة بتعتمد على `outputData` أو الداتا المسجلة محلياً في التطبيق.\n\nوفي سيناريوهات رفع الملفات الضخمة، بنربط WorkManager ببروتوكول رفع يدعم الاستئناف زي Tus أو Chunked Upload. الـ Worker بيكتب رقم آخر Byte تم رفعه وتأكيده في Room داخل Transaction محلي. لو النظام قتل الـ Process أو انقطعت الشبكة، الـ Worker لما يتعاد تشغيله بيقرأ الـ Offset من Room ويكمل رفع من غير ما يعيد من الصفر أو يستنزف باقة العميل، مما يحافظ على استقرار النظام وموثوقية المعالجة بالكامل."
    }
}

# ==========================================
# BG-11: Avoid duplicate processing on retry
# ==========================================
DATA["BG-11"] = {
    "concept_en": """WorkManager enforces an at-least-once execution guarantee, meaning that transient interruptions, unhandled exceptions, constraint breaks, or process termination before a successful result is committed will cause the system to reschedule and re-execute the worker. To prevent duplicate processing—such as double billing, redundant database writes, or duplicate network mutations—background tasks must be architected with strict idempotency across both client and server boundaries. This entails three core engineering strategies: attaching unique, deterministic client-generated idempotency keys (such as UUIDs) to network requests so the backend can recognize and de-duplicate repeated operations; maintaining transactional local state machines in Room to verify whether an action was already completed prior to invoking remote services; and recording resumable progress checkpoints so retried workers resume from the last committed step rather than restarting from the beginning.""",
    "walkthrough_en": """Enforcing idempotency under worker retries:
```kotlin
// 1. Worker implementing idempotency via local state and remote idempotency keys
class SubmitPaymentWorker(
    appContext: Context,
    params: WorkerParameters,
    private val paymentDao: PaymentDao,
    private val paymentApi: PaymentApi
) : CoroutineWorker(appContext, params) {

    override suspend fun doWork(): Result = withContext(Dispatchers.IO) {
        val paymentId = inputData.getString("PAYMENT_ID") ?: return@withContext Result.failure()
        val localRecord = paymentDao.getPayment(paymentId) ?: return@withContext Result.failure()

        // Local idempotency guard: skip if already executed prior to interruption
        if (localRecord.status == PaymentStatus.COMPLETED) {
            return@withContext Result.success()
        }

        try {
            // Pass deterministic idempotency key to remote server
            val response = paymentApi.chargeCard(
                idempotencyKey = localRecord.clientRequestId,
                amount = localRecord.amount
            )

            // Commit completed state atomically in Room
            paymentDao.updateStatus(paymentId, PaymentStatus.COMPLETED, response.transactionId)
            Result.success()
        } catch (e: IOException) {
            Result.retry() // Rescheduled with exponential backoff; safe because server de-duplicates key
        } catch (e: Exception) {
            Result.failure()
        }
    }
}
```""",
    "short_en": """Avoid duplicate processing under Worker retries by treating WorkManager as an at-least-once execution engine and enforcing strict idempotency. Generate a deterministic client-side UUID or idempotency key and pass it with mutating network calls, allowing the backend to de-duplicate repeated requests. Simultaneously, maintain a local state machine in Room to verify completion before dispatching network calls and resume multi-step workflows from saved checkpoints.""",
    "structured_en": """Preventing duplicate processing during Worker retries requires recognizing that WorkManager provides at-least-once execution rather than exactly-once execution. If a process crash, network timeout, or constraint violation interrupts a worker before it records success, WorkManager automatically reschedules the job.
The primary defense is client-driven idempotency tokens. Before enqueuing work, generate a unique deterministic UUID representing the transaction and store it locally. When the worker invokes backend mutation endpoints, it passes this token in the request headers. If the worker crashes after the server processes the charge but before receiving the acknowledgment, the subsequent retry submits the identical token. The backend detects the existing token and returns the cached success response without repeating the charge.
Locally, the worker must inspect its Room database entity state before making network calls. If a previous attempt succeeded in updating local status or if the transaction identifier is already populated, the worker immediately returns Result.success without executing remote side effects.
For multi-step batch operations, saving incremental progress checkpoints enables retried workers to skip completed units and process only pending items.""",
    "deep_senior_en": """Under the hood, the root cause of duplicate background processing is the distributed commit problem between remote servers and local persistence engines. When a Worker issues an HTTP POST request to submit a payment or place an order, the server may process the database transaction and commit the record. However, if the cellular connection drops before the TCP response arrives, or if the Android low-memory killer terminates the app process at that exact millisecond, WorkManager never receives Result.success.
Because WorkManager relies on JobScheduler to reschedule unacknowledged tasks, the worker executes again upon device reboot or network restoration. Without idempotency safeguards, the worker will submit a second charge.
Senior engineers address this vulnerability by designing atomic local-remote state machines. In Room, the business entity starts in a PENDING state with a persistent client-generated UUID. When the worker retries, it first queries the local database: if the status is already marked COMMITTED, it exits immediately.
If the status remains PENDING, the worker issues an idempotent request containing the UUID. The server enforces a unique database index on the idempotency key, transforming potential duplicate inserts into safe read-only queries returning the original transaction payload.
Furthermore, for long-running batch synchronization, staff engineers avoid coarse all-or-nothing retry loops. By persisting granular item-level statuses, the worker queries only items where status equals UNPROCESSED, preventing redundant network payloads and guaranteeing system-wide consistency across arbitrary process interruptions.""",
    "meta_ar": {
        "id": "BG-11",
        "questionAr": "كيف تتجنب التكرار والمعالجة المزدوجة عند إعادة محاولة تشغيل الـ Worker؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "استيعاب طبيعة At-least-once في WorkManager، وتصميم عمليات Idempotent في التطبيق والسيرفر، وتطبيق Idempotency Keys، وحماية قواعد البيانات المحلية من المعالجة المكررة.",
        "why_it_matters_ar": "إعادة محاولة تنفيذ Worker بدون تصميم Idempotent قد يتسبب في خصم أموال العميل مرتين أو تكرار إنشاء الطلبات عند انقطاع الشبكة المفاجئ.",
        "worked_example_ar": "فحص الحالة المحلية وتمرير مفتاح Idempotency للسيرفر:\n```kotlin\nval order = dao.getOrder(id)\nif (order.status == Status.SYNCED) return Result.success()\nval res = api.submitOrder(order.idempotencyKey, order.payload)\ndao.markSynced(id, res.txId)\nreturn Result.success()\n```",
        "trade_offs_ar": "بناء نظام Idempotent يتطلب تنسيقاً وتطويراً في الـ Backend وقاعدة البيانات المحلية، لكنه الضمان الوحيد لمنع الكوارث المالية ومشاكل اتساق البيانات.",
        "failure_modes_ar": "إعادة إرسال طلب الدفع بمفتاح UUID عشوائي جديد مع كل محاولة، مما يجعل السيرفر يعتبرها معاملة جديدة ويخصم المبلغ مرة أخرى.",
        "production_perspective_ar": "في تطبيقات البنوك والدفع، نولد Idempotency Key مرة واحدة عند نقر المستخدم ونحفظه في Room، والسيرفر يسجله بـ Unique Constraint في قاعدة بياناته لمنع التكرار قطيعاً.",
        "how_to_answer_ar": "ابدأ بتوضيح حقيقة أن WorkManager ينفذ العمليات لمرة واحدة على الأقل (At-least-once)، ثم بين سيناريو موت الـ Process بعد نجاح السيرفر، واشرح الحل عبر مفاتيح الـ Idempotency وفحص Room.",
        "talking_points_ar": "مفهوم At-least-once Execution، وتوليد Client-side Idempotency Keys، واستخدام Room State Machine، ونقاط الاستئناف للمهام المجمعة.",
        "follow_ups_ar": "- **المحاور:** \"لماذا لا يوفر WorkManager ضمانة Exactly-once بدلاً من إجهاد المطور؟\"\n  **المرشح:** \"لأن ضمان Exactly-once مستحيل عملياً في الأنظمة الموزعة بسبب Two Generals Problem واحتمالية انهيار التطبيق في اللحظة الفاصلة بين استجابة السيرفر وتحديث SQLite الداخلي.\"\n\n- **المحاور:** \"ماذا تفعل لو انقطع الاتصال والـ Worker بيعمل رفع لـ 50 صورة دفعة واحدة؟\"\n  **المرشح:** \"بنسجل حالة كل صورة في Room على حدة (Uploaded/Pending)، ولما الـ Worker يعيد المحاولة، بيجلب فقط الصور التي لم ترفع بعد ويتخطى الصور المكتملة.\"",
        "self_check_ar": "هل وضحت سبب إعادة المحاولة وطبيعة At-least-once؟ هل شرحت دور Idempotency Key في السيرفر؟ وهل بينت فحص الحالة المحلية في Room؟",
        "references_ar": f"- [WorkManager at-least-once execution](https://developer.android.com/topic/libraries/architecture/workmanager/how-to/define-work) — شرح ضمانات التنفيذ وإعادة المحاولة في WorkManager.\n- [Designing Idempotent APIs](https://stripe.com/docs/api/idempotent_requests) — أفضل الممارسات الهندسية لتصميم واجهات برمجة التطبيقات المتكررة بأمان.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "بنتجنب المعالجة المكررة بتطبيق مبدأ الـ Idempotency في كل خطوة، لأن WorkManager بيضمن التنفيذ لمرة واحدة على الأقل مش بالضبط مرة واحدة. بنولد كود فريد Idempotency Key لكل معاملة وبنمرره في الهيدر للسيرفر علشان يتجاهل الطلب لو اتكرر، وبنفحص حالة العملية في Room قبل أي استدعاء شبكة، وبنحفظ نقاط إنجاز لكل خطوة علشان نستأنف منها مباشرة.",
        "best_answer_ar": "تجنب التكرار أثناء إعادة محاولة الـ Worker بيتطلب التعامل مع حقيقة إن WorkManager بيدي ضمانة At-least-once Execution. يعني لو حصل انقطاع في الشبكة أو النظام قفل التطبيق قبل ما الـ Worker يسجل نجاحه، النظام هيعيد تشغيله حتماً.\n\nلمنع تكرار العمليات الحساسة زي الدفع، بنعتمد على محورين أساسيين. المحور الأول هو توليد مفتاح فريد Idempotency Token في جانب الموبايل وتخزينه في Room، وتمريره في ترويسة الطلب للسيرفر. فلو السيرفر نفذ العملية فعلياً والرد تاه في الطريق بسبب انقطاع النت، المحاولة الجديدة هتوصل بنفس المفتاح، فالسيرفر هيكتشف تكراره ويرجع النتيجة المحفوظة بدون ما يخصم فلوس العميل مرة تانية.\n\nالمحور التاني هو فحص الحالة المحلية داخل الـ Worker قبل إجراء أي اتصال خارجي. بنفتح كائن المعاملة من قاعدة بيانات Room؛ لو لقينا حالتها بالفعل مكتملة أو فيه رقم إيصال مسجل، بنرجع فوراً `Result.success()` بدون أي طلب شبكة مكرر.\n\nوفي المهام المجمعة، بنسجل حالة كل عنصر على حدة علشان الـ Worker لما يعيد المحاولة، يعالج فقط العناصر المعلقة ويتخطى الأجزاء المكتملة بنجاح.",
        "deep_answer_ar": "تحت الكابوت، السبب الجذري لتكرار العمليات هو مشكلة الالتزام الموزع (Distributed Commit) بين السيرفر الخارجي والتخزين المحلي. لما الـ Worker يبعت طلب إنشائي POST للسيرفر، السيرفر ممكن ينفذ المعاملة بنجاح، لكن اتصال الداتا ينقطع قبل ما الـ Response يوصل للموبايل، أو نظام أندرويد يقتل الـ Process في اللحظة دي بالظبط. في الحالة دي، WorkManager بيعتبر المهمة فشلت ويعيد جدولتها.\n\nلو الـ Worker مش مصمم على مبدأ الـ Idempotency، هيعيد إرسال الطلب للسيرفر وكأنه معاملة جديدة تماماً، وده بيتسبب في تكرار الخصم أو تكرار إرسال الشحنات.\n\nالمهندسون الكبار بيحلوا المعضلة دي بتصميم State Machine محكمة. المعاملة بتبدأ في Room بحالة PENDING وبتحمل UUID فريد وثابت بيتولد لحظة إنشاء الطلب. لما الـ Worker يشتغل أو يتعاد تشغيله، بيفحص أولاً هل الحالة في Room اتحولت لـ COMPLETED؟ لو اتحولت، بينهي المهمة فوراً بنجاح.\n\nلو لسه PENDING، بيبعت الطلب بنفس الـ UUID، والسيرفر بيحتوي على قيد فريد Unique Constraint على المفتاح ده، فلو لقاه مسجل عنده مش بينفذ العملية من جديد، بل بيرجع كود 200 مع بيانات المعاملة السابقة.\n\nبالإضافة لده، بنستخدم استعلامات فحص سريعة GET للتحقق من حالة الطلب على السيرفر قبل إعادة المحاولة لو كنا في بيئات تداول حساسة، وبنضمن تجزئة المهام الكبيرة بحيث لا يعاد رفع بايت واحد تم تأكيده سابقاً، مع الحفاظ الكامل على سلامة سجلات الدفع وحسابات العملاء."
    }
}

# ==========================================
# BG-12: Foreground-service restrictions & notification requirements
# ==========================================
DATA["BG-12"] = {
    "concept_en": """Android has progressively restricted Foreground Services to curb battery drain, memory monopolization, and background privilege abuse. Starting in Android 12 (API 31), applications cannot launch foreground services while operating in the background, throwing a runtime ForegroundServiceStartNotAllowedException unless fulfilling specific exemptions such as high-priority push messages, exact alarms, or user-driven interactions. Android 14 (API 34) mandates that every foreground service declare an explicit foregroundServiceType attribute in the manifest (e.g., location, mediaPlayback, camera, dataSync), request a matching runtime type permission (e.g., FOREGROUND_SERVICE_LOCATION), and pass appropriate system permission checks. In Android 14, the generic dataSync type is heavily discouraged and throttled with a 6-hour cumulative execution limit. System notification rules require calling startForeground within a strict system timeout (typically within 10 seconds), presenting a non-dismissible notification that clearly communicates ongoing activity, while Android 13 (API 33) introduced runtime notification permission requirements and task manager visibility.""",
    "walkthrough_en": """Configuring and starting foreground services in modern Android:
```kotlin
// 1. AndroidManifest.xml configuration for Android 14+
// <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
// <uses-permission android:name="android.permission.FOREGROUND_SERVICE_LOCATION" />
// <service
//     android:name=".LocationTrackingService"
//     android:foregroundServiceType="location"
//     android:exported="false" />

// 2. Service implementation calling startForeground within system timeout
class LocationTrackingService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val notification = NotificationCompat.Builder(this, "tracking_channel")
            .setContentTitle("Active Workout Tracking")
            .setContentText("Recording GPS coordinates in real-time...")
            .setSmallIcon(R.drawable.ic_gps)
            .setOngoing(true)
            .build()

        // Android 14 mandates passing service type flags matching manifest declaration
        ServiceCompat.startForeground(
            this,
            NOTIFICATION_ID,
            notification,
            ServiceInfo.FOREGROUND_SERVICE_TYPE_LOCATION
        )
        return START_STICKY
    }
    override fun onBind(intent: Intent?): IBinder? = null
}
```""",
    "short_en": """Android 12+ restricts starting Foreground Services from the background, throwing ForegroundServiceStartNotAllowedException except under narrow exemptions like high-priority FCM. Android 14+ mandates declaring explicit foregroundServiceType attributes in the manifest and acquiring corresponding type-specific permissions. Developers must post an ongoing system notification via startForeground within seconds of launch, and generic background syncing should use WorkManager instead of foreground services.""",
    "structured_en": """Foreground service restrictions in modern Android represent a paradigm shift toward battery conservation and user privacy.
Beginning with Android 12, the platform prohibits apps from starting foreground services while in the background. Attempting to invoke startForegroundService from background threads or workers throws ForegroundServiceStartNotAllowedException. Exceptions are strictly limited to direct user actions, high-priority Firebase push messages, companion device triggers, or exact alarms.
Android 14 intensifies these rules by requiring developers to declare specific foregroundServiceType values in AndroidManifest, such as location, mediaPlayback, microphone, or health. Apps must declare corresponding runtime permissions, such as FOREGROUND_SERVICE_LOCATION, and ensure prerequisite runtime permissions are granted prior to starting the service. Furthermore, Android 14 introduces a cumulative 6-hour daily execution cap on the dataSync service type, pushing developers toward WorkManager.
Regarding notifications, the service must invoke startForeground with an active notification within a strict platform window. Failing to post the notification triggers an immediate crash. Android 13 also requires the POST_NOTIFICATIONS permission and displays running foreground services inside the system Quick Settings Task Manager.""",
    "deep_senior_en": """Under the hood, Android background execution restrictions are enforced by the system ActivityManagerService and PowerManagerService. In previous platform releases, developers abused foreground services as an escape hatch to evade background execution limits, spinning up dummy notifications to maintain persistent background processes.
Starting with Android 12, ActivityManagerService tracks application process state UID records. If an app attempts to transition into a foreground service while its UID state is lower than the required foreground threshold, the platform intercepts the binder transaction and throws ForegroundServiceStartNotAllowedException.
In Android 14, Google eliminated generic background services entirely. Each declared foregroundServiceType undergoes rigorous manifest verification and runtime privilege validation. For instance, declaring foregroundServiceType="location" without first securing ACCESS_FINE_LOCATION or ACCESS_COARSE_LOCATION triggers a SecurityException upon calling startForeground.
Additionally, the dataSync type is now subject to platform timeout policies: Android 14 terminates dataSync services that run continuously for more than 6 hours within a 24-hour window, logging an ApplicationExitInfo reason of REASON_OTHER.
Senior engineers architect systems so that foreground services are reserved strictly for genuine continuous user-interactive activities—like real-time navigation or audio playback. For general data synchronization, file uploads, and background cache updates, staff engineers exclusively use WorkManager Expedited Work requests. Expedited work grants immediate high-priority execution quotas without triggering background launch exceptions or requiring invasive foreground service declarations, maintaining full compliance with modern Google Play quality guidelines.""",
    "meta_ar": {
        "id": "BG-12",
        "questionAr": "ما هي قيود الخدمات الأمامية (Foreground Services) ومتطلبات الإشعارات في أندرويد الحديث؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "معرفة قيود تشغيل Foreground Services من الخلفية في أندرويد 12+، ومتطلبات أنواع الخدمات والتصاريح في أندرويد 14+، وقواعد الإشعارات المستمرة، وبدائل Expedited Work.",
        "why_it_matters_ar": "تشغيل Foreground Service من الخلفية في أندرويد 12+ يسبب انهيار التطبيق بـ ForegroundServiceStartNotAllowedException، وإهمال نوع الخدمة في أندرويد 14+ يسبب رفض التطبيق في جوجل بلاي.",
        "worked_example_ar": "تعريف نوع الخدمة في المانيفست وتشغيلها بإشعار مستمر:\n```xml\n<service android:name=\".GpsService\"\n    android:foregroundServiceType=\"location\" />\n```\n```kotlin\nServiceCompat.startForeground(this, ID, notification, FOREGROUND_SERVICE_TYPE_LOCATION)\n```",
        "trade_offs_ar": "الـ Foreground Service تمنع قتل الـ Process أثناء الاستخدام الفعلي، لكنها تتطلب إشعاراً دائماً وقيوداً صارمة جداً في النظام، والبديل الأفضل لمزامنة البيانات هو WorkManager.",
        "failure_modes_ar": "محاولة تشغيل Foreground Service من كود شغال في الخلفية بدون تفاعل مباشر من المستخدم، أو استخدام نوع dataSync لمزامنة طويلة تتجاوز 6 ساعات في أندرويد 14.",
        "production_perspective_ar": "في المشروعات الحديثة، نمنع استخدام Foreground Service تماماً لأي مزامنة داتا ونستبدلها بـ Expedited Work في WorkManager، ونقصرها فقط على تشغيل الصوت والملاحة المباشرة.",
        "how_to_answer_ar": "ابدأ بالقيود الصارمة في أندرويد 12 على التشغيل من الخلفية، ثم اشرح إلزامية تحديد foregroundServiceType في أندرويد 14، ومتطلبات الإشعار خلال ثوانٍ، وانصح بـ WorkManager كبديل رسمي للمزامنة.",
        "talking_points_ar": "استثناء ForegroundServiceStartNotAllowedException في أندرويد 12، وتحديد نوع الخدمة وصلاحياتها في أندرويد 14، وحد الـ 6 ساعات لـ dataSync، ونافذة startForeground، وبديل Expedited Work.",
        "follow_ups_ar": "- **المحاور:** \"ماذا يحدث لو التطبيق تأخر في استدعاء startForeground() بعد startForegroundService()؟\"\n  **المرشح:** \"النظام بينهي التطبيق فوراً ويرمي ANR أو استثناء صريح لأن النظام بيدي مهلة قصيرة بحد أقصى بضع ثوانٍ لإظهار الإشعار للمستخدم.\"\n\n- **المحاور:** \"هل ما زال مسموحاً استخدام Foreground Service لرفع ملفات أو مزامنة بيانات دورية؟\"\n  **المرشح:** \"غير مفضل نهائياً؛ أندرويد 14 فرض حداً أقصى 6 ساعات يومياً لنوع dataSync، وجوجل بتوصي رسمياً باستخدام WorkManager و Expedited Work للرفع والمزامنة.\"",
        "self_check_ar": "هل وضحت استثناء أندرويد 12؟ هل شرحت إلزامية أنواع الخدمات في أندرويد 14؟ وهل بينت قيود الإشعارات والبديل الأفضل للمزامنة؟",
        "references_ar": f"- [Foreground service restrictions](https://developer.android.com/about/versions/12/behavior-changes-12#foreground-service-launch-restrictions) — قيود تشغيل الخدمات الأمامية في أندرويد 12+.\n- [Foreground service types in Android 14](https://developer.android.com/about/versions/14/changes/fgs-types-required) — إلزامية تحديد نوع الخدمة والتصاريح في أندرويد 14.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "أندرويد 12+ منع نهائياً تشغيل الـ Foreground Services أثناء تواجد التطبيق في الخلفية وبيرمي استثناء صريح إلا في حالات ضيقة جداً زي رسائل FCM العاجلة. وأندرويد 14+ ألزم بتحديد نوع الخدمة foregroundServiceType في المانيفست وطلب صلاحية خاصة مطابقة له مع تقييد خدمة مزامنة البيانات بـ 6 ساعات فقط، مع ضرورة إظهار إشعار دائم عبر startForeground فور التشغيل، واستبدال المزامنة بـ WorkManager.",
        "best_answer_ar": "الخدمات الأمامية (Foreground Services) شهدت تغييرات جذرية في إصدارات أندرويد الحديثة لحماية خصوصية المستخدم والبطارية.\n\nمن أول أندرويد 12، النظام حظر تماماً إمكانية بدء Foreground Service لو التطبيق شغال في الخلفية، ومحاولة تشغيلها بترمي استثناء `ForegroundServiceStartNotAllowedException`، ومفيش استثناءات غير في حالات نادرة زي نقر المستخدم على إشعار أو استقبال FCM High Priority أو تفعيل منبه دقيق.\n\nومع أندرويد 14، جوجل فرضت تحديد نوع صريح للخدمة `foregroundServiceType` في ملف المانيفست زي location أو mediaPlayback أو microphone، ولازم تطلب صلاحية نوع الخدمة في الـ Manifest وتتأكد من موافقة المستخدم عليها في الـ Runtime قبل التشغيل، وإلا الكود هيرمي `SecurityException`. كمان تم تقييد نوع `dataSync` بحد أقصى 6 ساعات تراكمية خلال 24 ساعة.\n\nوبالنسبة للإشعارات، المطور ملزم باستدعاء `startForeground()` لعرض إشعار مستمر يوضح للمستخدم النشاط القائم خلال ثوانٍ معدودة من بدء الخدمة لتفادي الانهيار، ومع أندرويد 13 أصبح ظهور الإشعارات يتطلب صلاحية `POST_NOTIFICATIONS` ومراقبة نشاطها في الـ Task Manager.",
        "deep_answer_ar": "تحت الكابوت، القيود دي اتفرضت لأن المطورين زمان كانوا بيستغلوا الـ Foreground Service كمهرب للالتفاف على قيود الذاكرة والخلفية، فكانوا بيعملوا إشعار وهمي علشان يخلوا التطبيق شغال دايماً في الرام. نظام تشغيل أندرويد من خلال `ActivityManagerService` بقى بيتتبع الـ Process State بدقة؛ فلو الـ UID بتاع التطبيق مش في حالة Foreground حقيقية وحاول يشغل خدمة أمامية، النظام بيعترض المعاملة فوراً على مستوى الـ Binder ويرمي خطأ.\n\nفي أندرويد 14، التحقق بقى صارم ومزدوج؛ النظام بيفحص المانيفست في وقت التثبيت ووقت التشغيل. فلو حددت مثلاً `foregroundServiceType=\"location\"` وناديت `startForeground` بدون ما يكون معاك صلاحية `ACCESS_FINE_LOCATION`، التطبيق هينهار في اللحظة نفسها.\n\nكمان قيد الـ 6 ساعات لنوع `dataSync` بيوضح رسالة جوجل القاطعة: الخدمات الأمامية مخصصة فقط للأنشطة المستمرة اللي المستخدم واعي بيها وبيشوفها بنشاط زي الملاحة أو تشغيل المزيكا. أما مزامنة البيانات ورفع الملفات فالأداة المعتمدة ليها هي WorkManager.\n\nالمهندسون الكبار بيستخدموا Expedited Work في WorkManager كبديل رسمي؛ الميزة دي بتمنح المهمة حصة تنفيذ عاجلة بدون الحاجة لإشعار دائم على أندرويد 12+، وبتحمي التطبيق تماماً من استثناءات التشغيل الخلفي مع الامتثال الصارم لسياسات متجر Google Play وتأمين تجربة استخدام موثوقة وعالية الاستقرار، مع الحفاظ الكامل على عمر شحن البطارية وحماية موارد الهاتف الذكي من الاستنزاف العشوائي."
    }
}

# ==========================================
# BG-13: Exact alarm vs periodic work
# ==========================================
DATA["BG-13"] = {
    "concept_en": """Choosing between AlarmManager exact alarms and WorkManager periodic work requires understanding the architectural trade-off between clock precision and battery conservation. Exact alarms via AlarmManager setExactAndAllowWhileIdle are reserved exclusively for clock-precise, user-facing events where failure to trigger at the precise designated minute or second causes direct real-world harm or invalidates the core functionality—such as a personal alarm clock, a calendar appointment alert, or a scheduled medication reminder. Exact alarms require the SCHEDULE_EXACT_ALARM or USE_EXACT_ALARM permission, both subject to strict Google Play review policies and automatic platform revocation on Android 13+. In contrast, WorkManager PeriodicWorkRequest is the mandatory platform standard for deferrable background execution, enforcing an API-level minimum interval of 15 minutes, flexible execution windows, and full harmonization with Doze mode and App Standby buckets to optimize battery life.""",
    "walkthrough_en": """Contrasting exact alarms with periodic work:
```kotlin
// 1. Clock-exact user alarm: Wakes CPU at precise second for user-facing event
fun scheduleClockExactAlarm(context: Context, triggerEpochMs: Long, pendingIntent: PendingIntent) {
    val alarmManager = context.getSystemService(AlarmManager::class.java)

    // Check if app has permission on Android 12+ (SCHEDULE_EXACT_ALARM)
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S && !alarmManager.canScheduleExactAlarms()) {
        // Guide user to system settings to grant permission
        return
    }

    alarmManager.setExactAndAllowWhileIdle(
        AlarmManager.RTC_WAKEUP,
        triggerEpochMs,
        pendingIntent
    )
}

// 2. Periodic background maintenance: Battery-friendly, deferrable, persists across reboots
fun schedulePeriodicDataSync(context: Context) {
    val syncRequest = PeriodicWorkRequestBuilder<SyncWorker>(
        repeatInterval = 1, repeatIntervalTimeUnit = TimeUnit.HOURS,
        flexTimeInterval = 15, flexTimeIntervalUnit = TimeUnit.MINUTES
    ).setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.UNMETERED)
            .setRequiresBatteryNotLow(true)
            .build()
    ).build()

    WorkManager.getInstance(context).enqueueUniquePeriodicWork(
        "periodic_data_sync",
        ExistingPeriodicWorkPolicy.KEEP,
        syncRequest
    )
}
```""",
    "short_en": """Use exact alarms with AlarmManager setExactAndAllowWhileIdle strictly for clock-precise, user-facing events where triggering at the exact minute is mandatory, such as alarm clocks, calendar reminders, and medical alerts. Use WorkManager PeriodicWorkRequest for all background data syncing, cleanup, and maintenance, which enforces a 15-minute minimum interval and aligns with Doze mode to preserve device battery.""",
    "structured_en": """The decision between an exact alarm and periodic work centers on clock precision versus power efficiency.
Exact alarms via AlarmManager are built for time-critical, user-perceived events. If a user sets an alarm to wake up at 07:00 AM or a medical reminder to take medication at noon, triggering even five minutes late represents a product failure. In these scenarios, developers use setExactAndAllowWhileIdle, which wakes the CPU from low-power states to trigger a PendingIntent. However, this precision comes with significant regulatory overhead: starting in Android 12, apps must secure SCHEDULE_EXACT_ALARM, and Google Play rejects applications using exact alarms for routine background operations.
WorkManager PeriodicWorkRequest is designed for deferrable, recurring operations like syncing catalog data, uploading analytics, or pruning database caches. The platform enforces a hardcoded minimum interval of 15 minutes. WorkManager intentionally defers execution until environmental constraints like network availability and charging status are met, batching work into Doze mode maintenance windows.
Under no circumstances should AlarmManager be used as a polling mechanism for background data synchronization.""",
    "deep_senior_en": """Under the hood, AlarmManager and WorkManager interact with Android power management infrastructure in fundamentally divergent ways. When an exact alarm fires via setExactAndAllowWhileIdle, the system PowerManagerService acquires a transient kernel wake lock, spinning up CPU cores and piercing through Doze mode restrictions to deliver the broadcast or start a foreground activity.
Because frequent CPU wakeups severely impact battery longevity, Android restricts exact alarms aggressively. On Android 13+ (API 33+), the SCHEDULE_EXACT_ALARM permission is revoked by default for newly installed applications unless the app is classified as an alarm, timer, or calendar app. If an app attempts to call setExact without permission, the system throws a SecurityException.
Furthermore, repeating exact alarms do not exist natively on modern Android: the platform converts repeating alarms into inexact alarms. To simulate repetition with exact alarms, an app must manually calculate the next target timestamp and reschedule a new one-shot exact alarm inside its broadcast receiver upon every trigger.
In contrast, WorkManager delegates periodic tasks to JobScheduler. JobScheduler batches jobs from multiple applications into synchronized execution windows, minimizing radio activations and maximizing CPU deep sleep states. It also dynamically manages App Standby Buckets, adjusting execution quotas based on how frequently the user interacts with the app.
Staff engineers establish architectural boundaries: AlarmManager is quarantined within specialized reminder modules with explicit user settings fallbacks, while all background data retrieval, cache invalidation, and server synchronization are strictly assigned to WorkManager.""",
    "meta_ar": {
        "id": "BG-13",
        "questionAr": "متى يجب استخدام المنبه الدقيق (Exact Alarm) بدلاً من العمل الدوري (Periodic Work)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم الفارق بين التوقيت الدقيق بالثانية والمهام القابلة للتأجيل، والتعامل مع قيود وصلاحيات SCHEDULE_EXACT_ALARM في أندرويد 12/13، ومعرفة الحد الأدنى لـ PeriodicWorkRequest وتأثير Doze Mode.",
        "why_it_matters_ar": "استخدام AlarmManager للمزامنة الدورية يستنزف البطارية ويسبب رفض التطبيق في Google Play، واستخدام PeriodicWorkRequest لمنبه الاستيقاظ يتسبب في تأخر الرنين لساعات.",
        "worked_example_ar": "التمييز بين المنبه الدقيق والعمل الدوري برمجياً:\n```kotlin\n// للمنبه الدقيق: منبه استيقاظ بالثانية\nalarmManager.setExactAndAllowWhileIdle(RTC_WAKEUP, time, pi)\n// للمزامنة الدورية: كل ساعتين مع شاحن وواي فاي\nPeriodicWorkRequestBuilder<SyncWorker>(2, TimeUnit.HOURS).build()\n```",
        "trade_offs_ar": "الـ Exact Alarm دقيق بالثانية ويخترق Doze Mode لكنه مكلف جداً في البطارية ويتطلب صلاحيات معقدة، بينما Periodic Work موفر للبطارية لكنه يفرض حداً أدنى 15 دقيقة ويقبل التأجيل.",
        "failure_modes_ar": "استدعاء `setExactAndAllowWhileIdle` بدون فحص `canScheduleExactAlarms()` في أندرويد 12+ مما يسبب SecurityException فوري وانهيار التطبيق.",
        "production_perspective_ar": "نحظر استخدام AlarmManager تماماً في طبقات البيانات والمزامنة، ونحصره فقط في موديول الإشعارات والمواعيد الحرجة للمستخدم مع توجيهه للإعدادات لمنح الصلاحية.",
        "how_to_answer_ar": "وضح معيار القرار: هل التأخير يفسد وظيفة التطبيق في نظر المستخدم؟ ثم قارن بين دقة AlarmManager بالثانية وبين Periodic Work ومحدداته، واشرح موقف أندرويد الحديث وجوجل بلاي.",
        "talking_points_ar": "دقة التوقيت في AlarmManager، ومفهوم التراجع في Doze Mode، وصلاحيات SCHEDULE_EXACT_ALARM، والحد الأدنى 15 دقيقة في PeriodicWorkRequest، وسياسات متجر Google Play.",
        "follow_ups_ar": "- **المحاور:** \"هل يمكن استخدام AlarmManager لتشغيل مزامنة مع السيرفر كل دقيقة في الخلفية؟\"\n  **المرشح:** \"ممنوع تماماً؛ لأن أندرويد بيبطئ تكرار المنبهات في وضع Doze لتشتغل كل 9 إلى 15 دقيقة، وجوجل بلاي هتحذف التطبيق لمخالفته إرشادات استهلاك البطارية.\"\n\n- **المحاور:** \"لماذا لا ينفذ PeriodicWorkRequest المهام كل 5 دقائق؟\"\n  **المرشح:** \"لأن نظام أندرويد بيفرض حداً أدنى إجبارياً قدره 15 دقيقة (MIN_PERIODIC_INTERVAL_MILLIS) لحماية بطارية الهاتف من الاستنزاف بواسطة المهام المتكررة.\"",
        "self_check_ar": "هل حددت الحالات الحصرية للمنبه الدقيق؟ هل ذكرت قيود وصلاحيات أندرويد 12+؟ وهل شرحت سبب منع استخدام AlarmManager للمزامنة؟",
        "references_ar": f"- [Schedule exact alarms](https://developer.android.com/training/scheduling/alarms) — الدليل الرسمي لجدولة المنبهات الدقيقة والصلاحيات المطلوبة.\n- [Periodic Work](https://developer.android.com/topic/libraries/architecture/workmanager/how-to/define-work#periodic-work) — توثيق جدولة المهام الدورية في WorkManager.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "بنستخدم المنبه الدقيق AlarmManager عبر setExactAndAllowWhileIdle فقط في الأحداث الزمنية الصارمة اللي المستخدم بيعتمد عليها شخصياً زي منبه الاستيقاظ ومواعيد الأدوية وتقويم المواعيد، لأن تأخير دقيقة واحدة يعتبر فشلاً للتطبيق. أما أي مزامنة بيانات أو تحديث للكاش فممنوع نستخدم منبه دقيق ولازم نعتمد على PeriodicWorkRequest في WorkManager اللي بيوفر البطارية ويخضع لـ Doze Mode.",
        "best_answer_ar": "المفاضلة بين الـ Exact Alarm والـ Periodic Work بتعتمد على معيار هندسي حاسم: هل التوقيت مطلوب بالثانية كحدث مباشر للمستخدم، أم أنه عملية خلفية تقبل التأجيل.\n\nالمنبه الدقيق من خلال `AlarmManager.setExactAndAllowWhileIdle()` محجوز حصرياً للأحداث الحساسة للوقت اللي بيشعر بيها المستخدم بشكل مباشر؛ زي منبه الصحيان الصبح أو تنبيه موعد أخذ الدواء. في الحالات دي، لو التنبيه اتأخر 5 دقائق التطبيق بيكون فقد قيمته الأساسية. المنبه الدقيق بيقدر يصحي المعالج ويخترق وضع Doze Mode لتنبيه المستخدم، لكن ده بيتطلب صلاحيات خاصة زي `SCHEDULE_EXACT_ALARM`، وجوجل بتدقق عليها بشدة وممكن ترفض التطبيق لو استخدمتها لمزامنة عادية.\n\nعلى الجانب التاني، المهام الدورية بنستخدم لها دائماً `PeriodicWorkRequest` في WorkManager؛ لأنها مخصصة لمزامنة الكتالوج أو رفع التحليلات أو تنظيف الـ Cache. المكتبة بتفرض حداً أدنى 15 دقيقة للتكرار، وبتجمع المهام مع قيود الشاحن والواي فاي في نوافذ صيانة Doze لتوفير البطارية.\n\nالقاعدة الذهبية في أندرويد: لا تستخدم AlarmManager نهائياً لعمل Polling أو مزامنة داتا مع السيرفر.",
        "deep_answer_ar": "تحت الكابوت، المنبه الدقيق والعمل الدوري بيتعاملوا مع دوائر إدارة الطاقة في المعالج ونواة لينكس بطرق متناقضة تماماً. لما تستدعي `setExactAndAllowWhileIdle`، النظام بيحصل على Kernel WakeLock مؤقت وبيشغل أنوية المعالج بأقصى طاقتها في الثانية المحددة بالظبط حتى لو الموبايل كان في أعمق درجات الـ Deep Doze.\n\nالاستيقاظ المفاجئ ده بيكلف البطارية طاقة هائلة، علشان كده جوجل قيدت العملية دي بشدة؛ ففي أندرويد 13 فما فوق، صلاحية `SCHEDULE_EXACT_ALARM` بقت ملغية افتراضياً للتطبيقات الجديدة، ولو التطبيق نادى دالة المنبه بدون فحص الصلاحية، النظام هيرمي `SecurityException` فوري.\n\nكمان المنبهات الدورية الحقيقية المتكررة بالثانية تم إلغاؤها من النظام من زمان؛ فلو عايز تكرر منبه دقيق، بتضطر برمجياً تعيد جدولة منبه أحادي جديد بعد كل رنة داخل الـ Broadcast Receiver.\n\nفي المقابل، WorkManager بيسلم المهام الدورية لمحرك `JobScheduler`. المحرك ده بيعمل Batching للمهام من مختلف تطبيقات الهاتف ويشغلها في نافذة زمنية موحدة لما الشاشة تكون مطفية أو الموبايل على الشاحن، وده بيقلل استهلاك مودم الشبكة والمعالج.\n\nالمهندسون الكبار بيقفلوا تماماً استخدام AlarmManager في طبقة الـ Data Layer، وبيخلوه محصوراً في طبقة الـ UI للتذكيرات الحقيقية فقط، مع توفير واجهة بديلة ترشد المستخدم لتفعيل الصلاحية لو كانت معطلة في إعدادات النظام لضمان تجربة مستقرة وخالية من الانهيارات."
    }
}

# ==========================================
# BG-14: Coordinate WorkManager with repository & DB transactions
# ==========================================
DATA["BG-14"] = {
    "concept_en": """Coordinating WorkManager with repository layers and database transactions requires enforcing the Single Source of Truth principle and implementing transactional messaging patterns such as the Transactional Outbox pattern. A frequent architectural defect in mobile applications occurs when presentation or repository code launches network requests and writes to local storage concurrently, resulting in race conditions, partial writes, and orphaned background tasks. Instead, repository business mutations must execute inside an atomic Room database transaction that persists both the domain entity and an Outbox queue record (e.g., status PENDING_SYNC). WorkManager requests are enqueued only after the database transaction successfully commits. The background worker queries Room for pending outbox items, performs remote synchronization, and updates entity states within a subsequent atomic transaction, while the UI observes database state reactively via Flow.""",
    "walkthrough_en": """Implementing the Transactional Outbox pattern with WorkManager and Room:
```kotlin
// 1. Repository: Atomic Outbox transaction + WorkManager enqueue
class OrderRepository(
    private val db: AppDatabase,
    private val orderDao: OrderDao,
    private val workManager: WorkManager
) {
    suspend fun createOrder(order: Order) = withContext(Dispatchers.IO) {
        // Step A: Atomic local commit (Domain Entity + Outbox Record)
        db.withTransaction {
            orderDao.insertOrder(order.copy(status = OrderStatus.PENDING))
            orderDao.insertOutbox(OutboxItem(orderId = order.id, type = "CREATE_ORDER"))
        }

        // Step B: Enqueue durable WorkManager task after transaction commit
        val request = OneTimeWorkRequestBuilder<SyncOutboxWorker>()
            .setConstraints(Constraints.Builder().setRequiredNetworkType(NetworkType.CONNECTED).build())
            .build()
        workManager.enqueueUniqueWork("sync_outbox", ExistingWorkPolicy.KEEP, request)
    }

    // UI observes local database as Single Source of Truth
    fun observeOrder(orderId: String): Flow<Order> = orderDao.observeOrder(orderId)
}

// 2. Worker: Pulls pending items, executes network sync, commits completion atomically
class SyncOutboxWorker(
    appContext: Context,
    params: WorkerParameters,
    private val db: AppDatabase,
    private val api: OrderApi
) : CoroutineWorker(appContext, params) {
    override suspend fun doWork(): Result = withContext(Dispatchers.IO) {
        val pendingItems = db.orderDao().getPendingOutboxItems()
        for (item in pendingItems) {
            val response = api.submitOrder(item.payload)
            db.withTransaction {
                db.orderDao().updateOrderStatus(item.orderId, OrderStatus.SYNCED)
                db.orderDao().deleteOutboxItem(item.id)
            }
        }
        Result.success()
    }
}
```""",
    "short_en": """Coordinate WorkManager with Room by establishing the local database as the single source of truth using an Outbox pattern. Inside an atomic Room transaction, commit the domain data and an outbox queue entry together. Enqueue the WorkManager task only after the transaction succeeds. The worker reads pending outbox entries, performs network synchronization, and updates entity states in another atomic transaction, while UI observes Room reactively.""",
    "structured_en": """Coordinating WorkManager with repositories and database transactions requires decoupling network synchronization from immediate UI state transitions through the Transactional Outbox pattern.
When a user performs an action—such as placing an order or editing a profile—the repository initiates an atomic database transaction using Room withTransaction. Inside this atomic block, it writes both the updated domain entity with a status of PENDING and an outbox task entry. Committing these operations together guarantees that an intent to sync cannot exist without the corresponding domain record, eliminating orphaned state.
Only after the database transaction successfully commits does the repository enqueue a OneTimeWorkRequest with ExistingWorkPolicy.KEEP or APPEND. If the process terminates before WorkManager is enqueued, the pending outbox entry remains safely persisted on disk and will be detected during the next application launch or periodic reconciliation worker.
When the worker executes, it queries pending outbox records from Room, invokes backend endpoints, and commits the resulting remote identifiers and COMPLETED status atomically. The presentation layer observes database state reactively through Kotlin Flow, ensuring seamless UI updates without direct coupling to background workers.""",
    "deep_senior_en": """Under the hood, failing to isolate transaction boundaries between WorkManager and local SQLite storage results in classic dual-write hazards and database lock contention. A naive anti-pattern is enqueuing a WorkManager request inside an open Room transaction block. Because WorkManager immediately serializes request metadata into its own internal Room SQLite database, opening nested or concurrent transactions across distinct database instances can cause thread starvation and SQLite database lock timeouts.
Senior engineers always separate database commit phases from WorkManager queuing. The repository commits domain state and outbox intents to the application database first. Once the transaction completes, WorkManager is enqueued asynchronously.
Furthermore, relying solely on immediate WorkManager queuing introduces an edge-case failure mode: if the application process crashes in the precise microsecond after the database commits but before enqueueUniqueWork returns, the work request is lost. Staff engineers solve this by implementing dual-trigger reconciliation.
In addition to the immediate WorkManager enqueue call, the application schedules a low-priority PeriodicWorkRequest that runs during Doze maintenance windows. When the periodic worker wakes up, it queries the outbox table for records stuck in PENDING status for longer than a designated threshold, enqueuing synchronization tasks automatically.
Additionally, all database operations performed by the background worker use optimistic concurrency control or dedicated transaction blocks with Dispatchers.IO, preventing background write locks from blocking main-thread database reads and guaranteeing high-throughput offline-first reliability.""",
    "meta_ar": {
        "id": "BG-14",
        "questionAr": "كيف تنسق بين WorkManager وطبقة الـ Repository ومعاملات قاعدة البيانات (Database Transactions)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على تصميم معمارية Offline-first متينة، وتطبيق نمط Transactional Outbox Pattern، وفصل حدود الـ Transactions لمنع قفل قاعدة البيانات، وتأمين المزامنة ضد انهيار الـ Process.",
        "why_it_matters_ar": "جدولة WorkManager داخل Room Transaction أو إجراء طلبات شبكة بالتوازي مع الحفظ يسبب سباق بيانات (Race Conditions) وتجميد قاعدة البيانات أو فقدان العمليات.",
        "worked_example_ar": "تطبيق نمط Outbox في الـ Repository:\n```kotlin\ndb.withTransaction {\n    dao.insertOrder(order.copy(status = PENDING))\n    dao.insertOutbox(OutboxItem(order.id))\n}\nworkManager.enqueueUniqueWork(\"sync\", ExistingWorkPolicy.KEEP, syncRequest)\n```",
        "trade_offs_ar": "نمط Outbox يتطلب جداول إضافية في Room وإدارة حالات المزامنة، لكنه يضمن عدم ضياع أي طلب ويحقق مبدأ Single Source of Truth بكفاءة مطلقة.",
        "failure_modes_ar": "استدعاء `workManager.enqueue` داخل بلوك `db.withTransaction` قبل عمل Commit، مما يسبب Deadlocks أو جدولة مهمة لبيانات لم يتم حفظها فعلياً لو فشل الـ Transaction.",
        "production_perspective_ar": "في التطبيقات المالية الكبرى، نعتمد Room كمصدر وحيد للحقيقة ونربطها بـ Flow للواجهة، ونشغل Worker دوري يفحص جدول Outbox كل فترة لإنعاش أي عمليات معلقة.",
        "how_to_answer_ar": "اشرح نمط Transactional Outbox: حفظ بيانات العمل مع سجل Outbox داخل Room Transaction ذري، ثم جدولة WorkManager بعد نجاح الحفظ، ومراقبة الواجهة للـ Database فقط.",
        "talking_points_ar": "نمط Transactional Outbox، ومبدأ Single Source of Truth (SSOT)، وفصل حدود المعاملات الذرية، وتفادي الـ Dual-write Hazards، والمصالحة الدورية (Periodic Reconciliation).",
        "follow_ups_ar": "- **المحاور:** \"ماذا يحدث لو التطبيق انهار بعد حفظ الداتابيز وقبل سطر workManager.enqueue()؟\"\n  **المرشح:** \"البيانات وسجل الـ Outbox محفوظين بأمان في Room، وأول ما التطبيق يفتح تاني أو يشتغل Worker المزامنة الدوري، بيكتشف العمليات المعلقة ويجدولها تلقائياً بدون ضياع أي معاملة.\"\n\n- **المحاور:** \"هل الـ ViewModel يتواصل مباشرة مع الـ Worker لمعرفة النتيجة؟\"\n  **المرشح:** \"لا نهائياً؛ الـ ViewModel بيراقب الـ Repository وقاعدة بيانات Room عبر Flow، والـ Worker بيحدث الـ Database لما يخلص، وده بيحافظ على المعمارية النظيفة.\"",
        "self_check_ar": "هل شرحت نمط Transactional Outbox؟ هل أكدت على جدولة WorkManager بعد الـ Commit؟ وهل وضحت مبدأ Single Source of Truth؟",
        "references_ar": f"- [Room Transactions](https://developer.android.com/training/data-storage/room/defining-data#transactions) — التوثيق الرسمي لتنفيذ المعاملات الذرية في Room.\n- [Transactional Outbox Pattern](https://microservices.io/patterns/data/transactional-outbox.html) — النمط المعماري لضمان موثوقية العمليات الموزعة.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "بنسق بينهم بتطبيق نمط Transactional Outbox واعتبار قاعدة بيانات Room هي المصدر الوحيد للحقيقة (SSOT). بنحفظ بيانات العملية وسجل المزامنة في جدول Outbox معاً داخل Room Transaction ذري واحد، وبعد نجاح الـ Commit بنجدول مهمة WorkManager. الـ Worker بيقرأ السجلات المعلقة وينفذ المزامنة مع السيرفر ويحدث الداتابيز في transaction جديد، بينما الواجهة بتراقب Room عبر Flow.",
        "best_answer_ar": "التنسيق الصحيح بين WorkManager وطبقة الـ Repository وقاعدة البيانات بيعتمد على فصل حدود الـ Transactions وتطبيق نمط الـ Transactional Outbox.\n\nأول خطوة لما المستخدم ينفذ عملية زي إنشاء طلب، الـ Repository بيفتح معاملة ذرية في Room باستخدام `db.withTransaction`. داخل المعاملة دي، بنسجل كائن الطلب بحالة PENDING، وفي نفس اللحظة بنسجل سجل في جدول الـ Outbox بيعبر عن العملية المطلوبة. دمج العمليتين في Transaction واحد بيضمن استحالة وجود نية مزامنة بدون وجود البيانات الفعلية على القرص.\n\nثاني خطوة بعد نجاح الـ Commit تماماً، الـ Repository بيستدعي `workManager.enqueueUniqueWork` بسياسة KEEP أو APPEND. وممنوع تماماً استدعاء WorkManager داخل بلوك الـ Transaction لتفادي مشاكل الـ Lock في SQLite.\n\nثالث خطوة، لما الـ Worker يشتغل في الخلفية، بيقرأ عناصر الـ Outbox المعلقة من Room، ويبعت البيانات للسيرفر، وبعد استلام الرد بنجاح، بيفتح Transaction جديد يغير حالة الطلب لـ SYNCED ويمسح سجل الـ Outbox. والـ ViewModel بيكون معزول تماماً وبيراقب جدول الطلبات في Room كتدفق Flow تفاعلي.",
        "deep_answer_ar": "تحت الكابوت، وقوع أخطاء في التنسيق بين قواعد البيانات و WorkManager بيسبب كوارث الـ Dual-write Hazards وتجميد خيوط المعالجة (Thread Starvation). الغلطة الشهيرة اللي بيقع فيها مهندسون كتير هي استدعاء `workManager.enqueue` داخل `db.withTransaction`؛ ده غلط لأن مكتبة WorkManager عندها قاعدة بيانات Room SQLite داخلية خاصة بيها، وفتح معاملات متداخلة على قواعد بيانات مختلفة في نفس الوقت بيعمل تنافس على الـ Locks وبيرمي استثناءات قفل.\n\nكمان فيه ثغرة دقيقة جداً: ماذا لو الهاتف مات فجأة في الميكروثانية الفاصلة بين نجاح Commit قاعدة البيانات وقبل استدعاء WorkManager؟ هنا المهمة مش هتتجدول!\n\nالمهندسون الكبار بيحلوا المعضلة دي بآلية المصالحة المزدوجة (Dual-Trigger Reconciliation). بجانب الاستدعاء الفوري للـ WorkManager بعد المعاملة، بنسجل `PeriodicWorkRequest` خفيف بيشتغل كل فترة؛ أول ما يصحى بيفحص جدول الـ Outbox في Room، ولو لقى أي عملية بقالها فترة بحالة PENDING بدون جدولة، بيعيد جدولتها فوراً.\n\nبالإضافة لده، كل العمليات اللي بينفذها الـ Worker بتستخدم `Dispatchers.IO` ومعاملات ذرية منفصلة مع استخدام Optimistic Concurrency Control لمنع تعارض الكتابة مع القراءة اللحظية اللي بتعملها الواجهة، مما يحقق استقراراً فائقاً للنظام وتجربة أوفلاين لا تنكسر أبداً تحت أي ظرف، مع ضمان وصول كافة التحديثات المعلقة إلى السيرفرات البعيدة فور عودة الاتصال بالإنترنت."
    }
}

# ==========================================
# BG-15: Resilient Upload Lifecycle
# ==========================================
DATA["BG-15"] = {
    "concept_en": """Architecting an upload pipeline that survives operating system process death, arbitrary network disruptions, and device reboots requires an offline-first resilient architecture combining chunked resumable upload protocols with WorkManager durable execution and Room local persistence. Relying on transient coroutine scopes or standard streaming uploads fails under mobile conditions because low-memory process kills force uploads to restart from byte zero. A production-grade design divides the lifecycle into five synchronized phases: local metadata commit in Room (generating upload UUID, total file length, and zero-offset state), durable work scheduling via WorkManager with network constraints and exponential backoff, remote session initiation or offset reconciliation via resumable protocols (such as Tus or HTTP Content-Range), iterative binary chunk transmission with incremental checkpointing in Room, and transactional terminal completion notifying the presentation layer reactively.""",
    "walkthrough_en": """Implementing a resilient resumable upload pipeline:
```kotlin
// 1. Resumable Chunked Upload Worker
class ResumableUploadWorker(
    appContext: Context,
    params: WorkerParameters,
    private val uploadDao: UploadDao,
    private val uploadApi: ResumableUploadApi
) : CoroutineWorker(appContext, params) {

    override suspend fun doWork(): Result = withContext(Dispatchers.IO) {
        val uploadId = inputData.getString("UPLOAD_ID") ?: return@withContext Result.failure()
        val uploadRecord = uploadDao.getUpload(uploadId) ?: return@withContext Result.failure()
        val file = File(uploadRecord.filePath)

        // Step A: Reconcile current byte offset with remote server
        var currentOffset = uploadApi.getServerOffset(uploadRecord.remoteUploadUrl)
        val chunkSize = 1024 * 1024 * 2 // 2MB chunks

        // Step B: Stream chunks sequentially with cooperative cancellation checks
        while (currentOffset < file.length()) {
            if (isStopped) return@withContext Result.retry()

            val endOffset = minOf(currentOffset + chunkSize, file.length())
            val chunkBytes = file.readBytesRange(currentOffset, endOffset)

            val success = uploadApi.uploadChunk(
                url = uploadRecord.remoteUploadUrl,
                chunk = chunkBytes,
                rangeHeader = "bytes $currentOffset-${endOffset - 1}/${file.length()}"
            )

            if (!success) return@withContext Result.retry()

            currentOffset = endOffset
            // Step C: Persist local checkpoint and update UI progress
            uploadDao.updateOffset(uploadId, currentOffset)
            val percent = ((currentOffset * 100) / file.length()).toInt()
            setProgress(workDataOf("PERCENT" to percent))
        }

        uploadDao.markCompleted(uploadId)
        Result.success()
    }
}
```""",
    "short_en": """Design a resilient upload pipeline by combining chunked resumable upload protocols with Room database checkpoints and WorkManager. Persist the file metadata, remote session URL, and byte offset in Room before enqueuing a OneTimeWorkRequest with connected network constraints. The worker queries the server for the current byte offset, streams chunks sequentially, updates Room checkpoints after each chunk, and resumes seamlessly after crashes or network drops.""",
    "structured_en": """Designing an upload system that survives process termination and connectivity loss requires decoupling data transmission from in-memory presentation scopes.
The lifecycle begins by recording the upload intent inside a local Room database. The repository generates a unique upload session UUID, saves the file URI and byte length, and sets the initial state to QUEUED with an offset of zero.
Next, the repository enqueues a OneTimeWorkRequest configured with NetworkType.CONNECTED and Exponential backoff criteria. WorkManager persists this request in its internal SQLite database, ensuring execution resumes after device reboots or process termination.
When the worker executes, it connects to the backend using a resumable upload protocol like Tus or Content-Range. Before transmitting payload data, it queries the backend to determine how many bytes were already received.
The worker then streams the file in fixed-size chunks. After each chunk acknowledgment, the worker commits the new byte offset to Room and reports transient progress via setProgress. If connectivity drops or the system kills the process, the rescheduled worker queries the latest offset and resumes transmission without restarting from byte zero.""",
    "deep_senior_en": """Under the hood, mobile network interfaces undergo frequent radio state transitions and radio link interruptions (RRC state changes from DCH to FACH to PCH/Idle). If an application attempts to upload large video or document payloads using a single monolithic HTTP POST, any momentary signal drop or system process reclamation aborts the TCP connection, forcing the client to retransmit the entire payload from the beginning and rapidly depleting user cellular quotas.
Senior engineers solve this by implementing chunked resumable architectures backed by durable storage. In this architecture, the local Room database acts as the state arbiter. When WorkManager initiates ResumableUploadWorker, the worker reads the local record and issues a HEAD or status request to the server upload URL. The server responds with the exact byte count already committed to cloud storage.
This handshake resolves the distributed state discrepancy: if the client previously transmitted a 4MB chunk but crashed before committing the local Room offset, the server authoritative response updates the client, preventing duplicate chunk transmission.
Additionally, file I/O within the worker utilizes random-access byte channel streams (FileChannel) rather than loading entire multi-gigabyte files into memory, eliminating OutOfMemoryError risks.
When constraints break or the user enters airplane mode, WorkManager triggers cooperative cancellation on CoroutineWorker. The worker finishes writing the current chunk status, releases file descriptors, and returns Result.retry(), allowing WorkManager exponential backoff to handle network recovery gracefully while presentation screens observe the Room entity reactively throughout.""",
    "meta_ar": {
        "id": "BG-15",
        "questionAr": "عملية رفع ملفات يجب أن تصمد أمام موت الـ Process وانقطاع الشبكة. صمّم دورة حياتها الهندسية.",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على تصميم نظام رفع ملفات متين (Resumable Chunked Upload)، واستخدام WorkManager مع Room Checkpointing، والتعامل مع بروتوكولات الاستئناف (Tus/Content-Range)، وحماية الذاكرة والبطارية.",
        "why_it_matters_ar": "رفع الملفات الضخمة في طلب HTTP واحد يؤدي لفقدان كل ما تم رفعه عند أدنى انقطاع في الشبكة أو قتل الـ Process، مما يستنزف باقة العميل ويفسد تجربة المستخدم.",
        "worked_example_ar": "تصميم الـ Worker للرفع المجزأ واستئناف الـ Byte Offset:\n```kotlin\nval offset = api.getRemoteOffset(uploadUrl)\nfile.openChannel().use { ch ->\n    ch.position(offset)\n    val chunk = ch.readChunk(2 * 1024 * 1024)\n    api.uploadChunk(chunk, offset)\n    dao.updateOffset(id, offset + chunk.size)\n}\n```",
        "trade_offs_ar": "الرفع المجزأ يتطلب دعماً خاصاً في الـ Backend وقاعدة بيانات محلية لحفظ الـ Checkpoints، لكنه الحل الوحيد المقبول هندسياً لرفع الملفات الكبيرة في بيئة الموبايل غير المستقرة.",
        "failure_modes_ar": "قراءة كامل الملف في الذاكرة `file.readBytes()` دفعة واحدة مما يسبب OutOfMemoryError فوري، أو إعادة رفع الملف من بايت صفر عند كل انقطاع للشبكة.",
        "production_perspective_ar": "في تطبيقات مشاركة الفيديو، نقسم الملفات لقطع بحجم 2MB ونرفعها ببروتوكول Tus، ونسجل حالة كل قطعة في Room مع إتاحة خيار الإيقاف المؤقت والاستئناف للمستخدم.",
        "how_to_answer_ar": "قسم دورة الحياة لمراحل: الحفظ الأولي في Room، والجدولة الدائمة بـ WorkManager، والتفاوض مع السيرفر لمعرفة نقطة الاستئناف، والرفع المجزأ وتحديث الـ Checkpoints، ثم الإكمال النهائي.",
        "talking_points_ar": "بروتوكولات الرفع القابل للاستئناف (Resumable Uploads)، ونقاط التفتيش (Checkpoints) في Room، واستخدام FileChannel لمنع OOM، وسياسات التراجع الأسي في WorkManager.",
        "follow_ups_ar": "- **المحاور:** \"كيف نمنع استهلاك الذاكرة (OOM) لو الملف حجمه 4 جيجابايت؟\"\n  **المرشح:** \"ممنوع نحمل الملف في مصفوفة Byte Array؛ بنستخدم FileChannel أو InputStream ونقرأ قطعة محددة فقط بحجم 2 إلى 4 ميجابايت في كل مرة.\"\n\n- **المحاور:** \"ماذا لو السيرفر استلم قطعة ورجع OK لكن الموبايل فصل شحن قبل ما يحدث Room؟\"\n  **المرشح:** \"الـ Worker لما يصحى بيبعت طلب استعلام (HEAD/Probe) للسيرفر يسأله عن آخر بايت مسجل عنده، فالسيرفر بيرجع الـ Offset الحقيقي ويبدأ من عنده بدون تكرار.\"",
        "self_check_ar": "هل صممت دورة حياة كاملة بمراحلها الخمس؟ هل شرحت الرفع المجزأ؟ وهل بينت كيفية الاستئناف من آخر بايت مسجل؟"
        ,
        "references_ar": f"- [WorkManager durable work](https://developer.android.com/topic/libraries/architecture/workmanager) — دليل إدارة المهام الدائمة التي تصمد أمام إغلاق التطبيق.\n- [Tus Resumable Upload Protocol](https://tus.io/protocols/resumable-upload.html) — المعيار المفتوح لبروتوكول رفع الملفات القابل للاستئناف.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "بنصمم نظام رفع مرن بيعتمد على الرفع المجزأ القابل للاستئناف (Chunked Resumable Upload) بالدمج بين Room و WorkManager. بنسجل بيانات الملف ومسار التخزين في Room بحالة مبدئية، وبنجدول OneTimeWorkRequest بمحددات توفر الإنترنت وتراجع أسي. الـ Worker بيبعت استعلام للسيرفر لمعرفة عدد البايتات المستلمة، ويرفع الملف في قطع صغيرة بحجم 2MB مع تحديث نقطة الإنجاز في Room بعد كل قطعة.",
        "best_answer_ar": "تصميم نظام رفع ملفات يصمد أمام موت الـ Process وانقطاع الشبكة بيتطلب دورة حياة معمارية محكمة بتفصل بين اتصال الشبكة والتخزين الدائم.\n\nالمرحلة الأولى هي التسجيل المحلي؛ قبل ما نبدأ أي رفع، الـ Repository بيسجل بيانات الملف في جدول Room: مسار الملف، وحجمه الكلي، ورابط الرفع، ورقم البايت الحالي وقيمته صفر، وحالة QUEUED. ده بيضمن إن نية الرفع محفوظة على القرص ولا يمكن تضيع لو التطبيق اتقفل فوراً.\n\nالمرحلة الثانية هي الجدولة الدائمة؛ بنطلق `OneTimeWorkRequest` بمحددات اتصال الإنترنت وسياسة `BackoffPolicy.EXPONENTIAL`. مكتبة WorkManager بتحفظ المهمة في SQLite الداخلي، فلو الجهاز عمل ريستارت، المهمة هتستأنف تلقائياً.\n\nالمرحلة الثالثة هي التفاوض مع السيرفر؛ الـ Worker بيبعت طلب استعلام للسيرفر (باستخدام بروتوكول زي Tus أو Content-Range) يسأله: كم بايت وصلك حتى الآن؟ الإجابة دي هي الحقيقة المطلقة وتمنع أي تعارض.\n\nالمرحلة الرابعة هي الرفع المجزأ؛ الـ Worker بيفتح الملف عبر `FileChannel` ويقرأ قطع بحجم 2MB ويرفعها بالتتابع، وبعد تأكيد كل قطعة، بيحدث الـ Offset في Room ويبعت التقدم للواجهة عبر `setProgress`، ويكرر لحد ما يكتمل الملف بنجاح.",
        "deep_answer_ar": "تحت الكابوت، شبكات الموبايل بطبيعتها غير مستقرة وبتتنقل بين أبراج التغطية وتتعرض لانقطاعات لحظية في الـ Radio Link. لو اعتمدت على طلب HTTP عادي بحجم الملف كله، أي انقطاع هيقطع اتصال الـ TCP ويضيع كل اللي ارفع ويبدأ من الصفر، وده كارثي لباقة العميل والبطارية.\n\nالمهندسون الكبار بيصمموا الـ Worker بحيث يتعامل مع كل سيناريوهات الانهيار كجزء طبيعي من دورة الحياة. أولاً، لمنع أخطاء OutOfMemoryError في الملفات الكبيرة (زي فيديو 2 جيجابايت)، ممنوع نهائياً استدعاء `readBytes()` كاملة؛ بل بنستخدم Streaming عبر `FileChannel` لقراءة الشريحة المطلوبة فقط في الذاكرة.\n\nثانياً، حل معضلة انقطاع الرد: لو الـ Worker رفع القطعة رقم 5 والسيرفر استلمها، لكن الموبايل مات قبل ما الـ Worker يستلم رد السيرفر ويسجل في Room، هيحصل عدم اتساق. الـ Worker لما يصحى مش بيعتمد على رقم Room القديم، بل بيبعت طلب HEAD للسيرفر يسأله عن آخر بايت مسجل عنده، ويحدث الـ Offset ويبدأ من القطعة رقم 6 مباشرة.\n\nثالثاً، عند انقطاع الشبكة، الـ WorkManager بيلغي الـ CoroutineScope تعاونياً، فالـ Worker بيلحق يقفل الـ File Descriptors ويرجع `Result.retry()`، ونظام الـ Exponential Backoff بيأخر المحاولة القادمة تدريجياً لحد ما الشبكة تستقر، والواجهة بتفضل تتابع الحالة من Room بدون أي تهنيج أو فقدان بيانات، مما يضمن تجربة رفع سلسة واحترافية تلبي أعلى معايير الجودة."
    }
}

# ==========================================
# BG-16: Job ran twice after crash - enforce idempotency
# ==========================================
DATA["BG-16"] = {
    "concept_en": """Enforcing idempotency when a background job executes twice following an application crash requires addressing the foundational reality of WorkManager: it is an at-least-once task execution engine, not an exactly-once system. If an operating system crash, low-memory process kill, or unhandled exception occurs after a worker completes its side effect (such as charging a customer or mutating remote state) but before it returns Result.success() to WorkManager's internal database, the platform reschedules the job. Enforcing idempotency requires establishing a resilient two-tier safeguard: client-side deterministic tokenization and server-side duplicate suppression. At the client tier, every discrete domain intent generates a persistent, unique idempotency key (UUID) recorded in a local Room database with a state machine; upon retry, the worker verifies whether local completion was already reached. At the server tier, the remote API requires this idempotency key in an HTTP header, verifying it against an atomic database ledger to return previously cached responses without re-executing transactions.""",
    "walkthrough_en": """Implementing two-tier idempotency guards across app crashes:
```kotlin
// 1. Enforcing idempotency via client state and remote idempotency keys
class ChargeSubscriptionWorker(
    appContext: Context,
    params: WorkerParameters,
    private val billingDao: BillingDao,
    private val billingApi: BillingApi
) : CoroutineWorker(appContext, params) {

    override suspend fun doWork(): Result = withContext(Dispatchers.IO) {
        val invoiceId = inputData.getString("INVOICE_ID") ?: return@withContext Result.failure()
        val invoice = billingDao.getInvoice(invoiceId) ?: return@withContext Result.failure()

        // 1. Local Precondition Check: Skip if already succeeded before the crash
        if (invoice.status == InvoiceStatus.PAID) {
            return@withContext Result.success()
        }

        try {
            // 2. Server Contract: Pass deterministic idempotency key generated at creation
            val response = billingApi.chargeInvoice(
                idempotencyKey = invoice.idempotencyKey, // UUID generated once when invoice was created
                invoiceId = invoice.id,
                amount = invoice.amountCents
            )

            // 3. Atomic local state transition
            billingDao.markAsPaid(invoiceId, response.transactionReceiptId)
            Result.success()
        } catch (e: IOException) {
            // Network failure or timeout: safe to retry because server caches the idempotencyKey
            Result.retry()
        } catch (e: Exception) {
            Result.failure()
        }
    }
}
```""",
    "short_en": """Enforce idempotency by separating the WorkManager retry mechanism from the logical domain mutation. Generate a persistent, deterministic UUID when creating the intent and store it in Room. Pass this UUID as an idempotency key in the remote API header so the backend can detect duplicates and return cached results. Inside the worker, verify local entity state before issuing network requests, returning success immediately if already completed.""",
    "structured_en": """Enforcing idempotency requires recognizing why jobs execute twice and addressing the vulnerability across both client and server layers.
When an app crashes or the system kills a process immediately after a remote mutation succeeds but before the worker commits Result.success, WorkManager interprets the interruption as a task failure and reschedules execution.
To prevent duplicate side effects during the subsequent retry, the architecture must implement a two-step defense.
First, maintain an explicit state machine in the local Room database. The domain entity is created with an initial PENDING status and a persistent, client-generated UUID. When the worker resumes, its first action is querying Room: if the entity is already marked COMPLETED or contains a valid transaction receipt, the worker immediately returns Result.success without making network calls.
Second, establish an idempotent server contract. The worker passes the persisted UUID in the request headers (such as Idempotency-Key). The backend stores this key within a unique constraint table. If the server receives a repeated request with an identical key, it returns the cached result without repeating the business transaction.""",
    "deep_senior_en": """Under the hood, the post-crash double execution anomaly illustrates the classic fallacies of distributed computing: network latency, partial failures, and lack of atomic distributed transactions across mobile clients and cloud backends. When a client sends a network request, there are three failure domains: the request was lost before reaching the server, the server crashed during execution, or the response was lost after execution.
Because mobile clients cannot differentiate between these three cases upon a sudden crash, WorkManager's at-least-once model guarantees that the request will be re-attempted.
Senior engineers eliminate double processing risks through rigorous distributed coordination patterns. On the client side, Room transactions ensure that the domain entity and its unique idempotency token are committed before any background worker is enqueued.
On the server side, the backend implements an Idempotency Ledger using Redis or a relational database with a short time-to-live or permanent unique constraint. When the worker retries after an app crash, the server intercepts the incoming Idempotency-Key. If an operation with that key is currently processing, the server returns HTTP 409 (Conflict) or an in-flight status, prompting the worker to retry with backoff. If the operation previously succeeded, the server replays the serialized original response payload with HTTP 200 OK.
Additionally, for operations that cannot easily implement server-side idempotency keys, staff engineers implement distributed status probe queries to verify remote status before attempting a re-execution, ensuring zero duplicate operations occur across arbitrary crashes.""",
    "meta_ar": {
        "id": "BG-16",
        "questionAr": "مهمة خلفية اشتغلت مرتين بعد انهيار التطبيق (Crash). كيف تفرض مبدأ الـ Idempotency؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم أسباب تكرار تشغيل المهام بعد الانهيار، ومعرفة طبيعة At-least-once في WorkManager، وتصميم Idempotency Keys على مستوى التطبيق والسيرفر، والتعامل مع حالات الـ Edge Cases في المعاملات المالية.",
        "why_it_matters_ar": "عدم فرض الـ Idempotency بعد الانهيار قد يؤدي لخصم أموال العميل مرتين أو تكرار حجز التذاكر، مما يتسبب في خسائر مالية وفقدان ثقة المستخدمين.",
        "worked_example_ar": "فحص الـ State المحلي وتمرير Idempotency-Key في الهيدر:\n```kotlin\nval order = dao.getOrder(id)\nif (order.isPaid) return Result.success()\nval res = api.charge(order.idempotencyKey, order.amount)\ndao.markPaid(id, res.receiptId)\nreturn Result.success()\n```",
        "trade_offs_ar": "تطبيق الـ Idempotency يتطلب بناء جدول لدفتر المعاملات (Ledger) في السيرفر وتخزين مفاتيح فريدة في Room، لكنه الصمام الأمان الوحيد في التطبيقات الموزعة.",
        "failure_modes_ar": "توليد UUID جديد داخل دالة doWork() مع كل إعادة تشغيل، مما يجعل السيرفر يعامل كل محاولة كطلب جديد تماماً ويخصم المبلغ مرتين.",
        "production_perspective_ar": "في أنظمة الدفع العالمية كـ Stripe، يتم إرسال `Idempotency-Key` في هيدر الطلب، ولو السيرفر استلم نفس المفتاح بيرجع الرد المخزن سابقاً بدون تكرار الخصم.",
        "how_to_answer_ar": "اشرح سبب تكرار المهمة: السيرفر نفذ الطلب لكن التطبيق انهار قبل وصول الرد أو تسجيل النجاح، ثم اشرح الحل المزدوج: فحص الحالة في Room ومفاتيح الـ Idempotency في السيرفر.",
        "talking_points_ar": "سبب تكرار المهام بعد الانهيار، وطبيعة At-least-once في WorkManager، وتوليد مفاتيح الـ Idempotency وتخزينها، وعقد السيرفر (Server Contract) وإرجاع الرد المخزن.",
        "follow_ups_ar": "- **المحاور:** \"لو السيرفر لا يدعم Idempotency-Key، كيف تحمي التطبيق من المعالجة المكررة؟\"\n  **المرشح:** \"بنعمل استعلام استكشافي (Status Probe) زي GET /orders/{client_tx_id} قبل ما ننفذ الـ POST؛ لو لقينا العملية اتنفذت فعلاً بنسجل نجاح ونتفادى إرسال الـ POST مرة تانية.\"\n\n- **المحاور:** \"أين يتم توليد الـ Idempotency Key بالضبط؟ في الـ Worker أم في الـ ViewModel؟\"\n  **المرشح:** \"يتم توليده مرة واحدة في الـ Repository لحظة إنشاء المعاملة ويحفظ في Room، وممنوع نهائياً توليده داخل doWork لأن doWork بتتكرر مع كل محاولة.\"",
        "self_check_ar": "هل بينت سبب تكرار المهمة بعد الانهيار؟ هل وضحت موقع توليد مفتاح الـ Idempotency؟ وهل شرحت التنسيق بين فحص Room وعقد السيرفر؟",
        "references_ar": f"- [WorkManager Idempotency](https://developer.android.com/topic/libraries/architecture/workmanager/how-to/define-work) — التعامل مع إعادة محاولة المهام وضمانات التنفيذ.\n- [IETF Idempotency-Key HTTP Header Field](https://datatracker.ietf.org/doc/html/draft-ietf-httpapi-idempotency-key-header-04) — المعيار الرسمي لهيدر مفاتيح التحصين من التكرار.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "المهمة اشتغلت مرتين لأن التطبيق انهار بعد ما السيرفر نفذ العملية لكن قبل ما WorkManager يسجل نجاحها في الداتابيز الداخلية. بنفرض الـ Idempotency بحل مزدوج: بنولد كود UUID فريد في الـ Repository لحظة إنشاء الطلب ونحفظه في Room، والـ Worker بيمرره في هيدر السيرفر علشان السيرفر يكتشف التكرار ويرجع نفس الرد، مع فحص حالة الداتابيز المحلية أول ما الـ Worker يصحى.",
        "best_answer_ar": "تكرار تشغيل المهمة بعد الانهيار (Crash) هو سلوك طبيعي ومتوقع في WorkManager؛ لأن ضمانة التشغيل هي At-least-once. السيناريو الكلاسيكي اللي بيحصل هو إن الـ Worker بيبعت طلب الدفع أو الحجز، والسيرفر بينفذه بنجاح، لكن التطبيق بينهار أو النظام بيقتل الـ Process في اللحظة اللي الرد راجع فيها في السلك وقبل ما يتنفذ سطر `Result.success()`. نظام أندرويد لما يفتح بيعتبر المهمة ماتت ويعيد تشغيلها.\n\nلفرض مبدأ الـ Idempotency ومنع تكرار العملية، بنطبق حماية هندسية ثنائية:\n\nأولاً، في جانب الموبايل: بنولد مفتاح فريد `Idempotency-Key` (كود UUID) مرة واحدة لحظة إنشاء الطلب في الـ Repository ونحفظه في Room بحالة PENDING. أول ما الـ Worker يشتغل بعد الانهيار، بيفحص جدول Room؛ لو لقى المعاملة اتسجلت بالفعل كـ COMPLETED أو فيها رقم إيصال، بينهي الـ Worker فوراً بنجاح بدون استدعاء الشبكة.\n\nثانياً، في جانب السيرفر: الـ Worker بيمرر نفس المفتاح ده في ترويسة الطلب. السيرفر بيسجل المفتاح في جدول بقيد فريد Unique Constraint؛ لو استلم نفس المفتاح تاني، مش بيخصم الفلوس من جديد، بل بيرجع الاستجابة المحفوظة عنده مع كود 200 OK.",
        "deep_answer_ar": "تحت الكابوت، المشكلة دي بتجسد معضلات الحوسبة الموزعة (Distributed Systems Fallacies) حيث يستحيل للموبايل التفرقة بين انقطاع الـ Response بعد نجاح السيرفر وبين فشل وصول الـ Request من الأساس عند حدوث انهيار مفاجئ. ولأن WorkManager بيحمي النظام من فقدان المهام، فإنه بيلجأ لإعادة الجدولة حتماً.\n\nالمهندسون الكبار بيتعاملوا مع المعضلة دي بنمط التصميم الشامل. الخطأ الأكبر هو توليد UUID عشوائي داخل دالة `doWork()`؛ لأن الـ Worker لما يتعاد تشغيله هيولد كود جديد خالص، فالسيرفر هيعتبره طلباً جديداً ويخصم من العميل مرتين!\n\nالتصميم المعتمد بيتطلب توليد الـ Idempotency Key في طبقة الـ Domain عند نقر المستخدم وتثبيته في قاعدة بيانات Room كجزء من الكيان نفسه. ولما الـ Worker يتعاد تشغيله، بيبعت نفس الـ UUID المحفوظ في الهيدر `Idempotency-Key` وفق معايير IETF.\n\nفي الـ Backend، بيتم استخدام مخزن سريع زي Redis مع Lock مؤقت؛ لو لقى الطلب شغال حالياً بيرجع 409 Conflict فالـ Worker يتراجع بـ Exponential Backoff، ولو لقاه خلص بيرجع النتيجة المخزنة فوراً.\n\nوفي الحالات اللي السيرفر مبيكونش مجهز فيها بـ Idempotency Keys، المهندس المحترف بيخلي الـ Worker يعمل استعلام استكشافي (Status Probe عبر دالة GET) برقم الطلب الداخلي ليتأكد من حالته في الباك إند قبل ما يجازف بإرسال طلب POST مكرر، وبكده بنضمن سلامة المعاملات بنسبة 100% بدون أي تكرار غير مقصود."
    }
}

# ==========================================
# BG-17: Second-perfect periodic execution limitations
# ==========================================
DATA["BG-17"] = {
    "concept_en": """Addressing a business requirement demanding second-perfect periodic background execution on modern Android requires establishing that the operating system intentionally and fundamentally prohibits such execution. Android's core architectural evolution—from Doze mode and App Standby Buckets in API 23 to background execution limits in API 26, AlarmManager throttling in API 31, and foreground service restrictions in API 34—is explicitly engineered to eradicate periodic background wakeups that deplete battery life, consume cellular radios, and compromise thermal stability. WorkManager enforces a platform minimum periodic interval of 15 minutes (PeriodicWorkRequest.MIN_PERIODIC_INTERVAL_MILLIS) with indeterminate flex windows. AlarmManager repeating alarms were converted into inexact alarms in API 19, and exact alarms are aggressively throttled during Doze sleep cycles. Furthermore, background services are terminated within minutes, and foreground dataSync services face hard 6-hour timeouts in Android 14.""",
    "walkthrough_en": """Demonstrating platform-enforced minimum limits and alternative push architecture:
```kotlin
// 1. Demonstrating platform-enforced minimum limits in WorkManager
// PeriodicWorkRequest.MIN_PERIODIC_INTERVAL_MILLIS is hardcoded to 15 minutes (900,000 ms)
val syncWork = PeriodicWorkRequestBuilder<SyncWorker>(
    repeatInterval = 5, repeatIntervalTimeUnit = TimeUnit.MINUTES // Clamped automatically to 15 minutes!
).build()

// 2. High-precision execution while device is active vs Doze throttling
fun scheduleNextPeriodicExecution(context: Context, targetEpochMs: Long, pendingIntent: PendingIntent) {
    val am = context.getSystemService(AlarmManager::class.java)

    // Exact alarms wake device from idle, but the OS throttles them in Deep Doze to once every 9-15 minutes!
    am.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, targetEpochMs, pendingIntent)
}

// 3. Recommended Architectural Alternative: Server-driven push via high-priority FCM
// Backend determines timing and wakes the device via high-priority data message
class PushNotificationService : FirebaseMessagingService() {
    override fun onMessageReceived(remoteMessage: RemoteMessage) {
        // App is granted a brief high-priority window to process data and update UI/notify user
    }
}
```""",
    "short_en": """Android strictly prohibits second-perfect periodic background execution to protect battery life and thermal stability. WorkManager enforces a hard 15-minute minimum interval and flex windows. AlarmManager repeating alarms are inexact, and exact alarms are throttled in Doze mode to once every 9 to 15 minutes. Background services are killed, and foreground services face strict type limits and execution caps in Android 14.""",
    "structured_en": """When business stakeholders request second-perfect periodic background execution, a senior engineer must educate them on Android platform realities and constraints.
The Android operating system is architected to eliminate background timers to preserve battery life and prevent thermal throttling.
WorkManager enforces a hard platform floor of 15 minutes for PeriodicWorkRequest; specifying intervals below 15 minutes is automatically clamped to 15 minutes, with additional delays imposed by Doze mode maintenance windows and App Standby Buckets.
AlarmManager cannot deliver periodic second-level precision either. Platform updates made repeating alarms inexact. While developers can reschedule individual exact alarms using setExactAndAllowWhileIdle, the platform limits idle wakeups to once every 9 to 15 minutes when the device enters Doze mode. Attempting to misuse exact alarms for periodic polling risks immediate rejection under Google Play policies.
Finally, Foreground Services cannot run indefinitely for general polling: Android 14 limits dataSync services to 6 hours within a 24-hour window.
The proper engineering resolution is pushing back on the requirement, proposing server-driven FCM push notifications, or capturing data in foreground sessions.""",
    "deep_senior_en": """Under the hood, Android power management is governed by Linux kernel low-power states, hardware wake locks, and system services including PowerManagerService and BatteryStatsService. When the device screen turns off and remains undisturbed, the platform transitions into Deep Doze. In this state, the application processor enters deep sleep (suspend-to-RAM), clock frequencies drop, the cellular modem enters low-power discontinuous reception (DRX) states, and iptables firewall rules block application socket connections.
Attempting to maintain a second-perfect periodic loop in the background fundamentally conflicts with this hardware and OS architecture. If an application attempts to hold a continuous Partial WakeLock to keep CPU cores active, modern Android releases detect excessive wake lock holding and flag the app via Android Vitals for bad behavior, penalizing its Google Play store visibility.
Furthermore, Android 14 introduced strict foreground service timeout policies, where any dataSync service running longer than 6 hours is forcibly killed.
Senior engineers address this business requirement by re-framing the problem. If the use case involves real-time telemetry, the application should maintain a persistent WebSocket connection only while the app is in the foreground, dropping to server-sent high-priority FCM notifications when backgrounded.
If the requirement involves medical or critical tracking, the app must be registered as a specialized foreground service (e.g., location or connectedDevice) with explicit hardware device pairing. For all standard use cases, the engineer negotiates an acceptable deferrable threshold aligned with WorkManager's 15-minute batched cadence.""",
    "meta_ar": {
        "id": "BG-17",
        "questionAr": "متطلب عمل يطلب تنفيذاً دورياً في الخلفية بدقة بالثانية. ما هي قيود أندرويد التي يجب مراعاتها؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على مواجهة متطلبات العمل غير الواقعية في أندرويد، ومعرفة قيود Doze Mode و App Standby، والحد الأدنى لـ WorkManager، وقيود AlarmManager، وحد الـ 6 ساعات للخدمات الأمامية في أندرويد 14.",
        "why_it_matters_ar": "محاولة تحقيق تنفيذ دوري بالثانية في الخلفية يؤدي لاستنزاف البطارية، وتصنيف التطبيق كسيء في Android Vitals، ورفض التطبيق أو حذفه من متجر Google Play.",
        "worked_example_ar": "الحد الأدنى لـ PeriodicWorkRequest وتخنيق المنبهات في Doze:\n```kotlin\n// لو كتبت 5 دقائق، أندرويد هيكبرها تلقائياً لـ 15 دقيقة إجبارياً!\nval req = PeriodicWorkRequestBuilder<MyWorker>(5, TimeUnit.MINUTES).build()\n// المنبهات الدقيقة في Doze بتتخنق لتعمل كل 9 إلى 15 دقيقة كحد أقصى\nalarmManager.setExactAndAllowWhileIdle(RTC_WAKEUP, time, pi)\n```",
        "trade_offs_ar": "المفاضلة مستحيلة تقنياً في أندرويد الحديث؛ لا يمكن الجمع بين العمل بالثانية في الخلفية والحفاظ على بطارية الهاتف، ويجب إعادة التفاوض على متطلب البزنس هندسياً.",
        "failure_modes_ar": "استخدام Partial WakeLock مستمر لإبقاء المعالج شغالاً طوال الليل، مما يستنزف البطارية تماماً ويطلق تحذيرات Bad Behavior في متجر التطبيقات.",
        "production_perspective_ar": "في المشروعات الكبرى، نرفض هذا المتطلب ونوضح للإدارة أن سياسات أندرويد تمنعه، ونستبدله بـ Push Notifications عبر FCM من السيرفر عند حدوث التغيير فعلياً.",
        "how_to_answer_ar": "ابدأ بحزم ووضوح: أندرويد يمنع هذا المتطلب عمداً لحماية البطارية، واستعرض القيود بالأرقام (15 دقيقة في WorkManager، وتخنيق Doze لـ 15 دقيقة في Alarms، وحد 6 ساعات في أندرويد 14)، واقترح البدائل.",
        "talking_points_ar": "استحالة التنفيذ الدوري بالثانية في أندرويد، والحد الأدنى 15 دقيقة في WorkManager، وتخنيق AlarmManager في Doze Mode، وحد 6 ساعات لـ dataSync في أندرويد 14، والبدائل المعتمدة (FCM).",
        "follow_ups_ar": "- **المحاور:** \"ماذا لو صمم العميل على تنفيذ المهمة كل دقيقة في الخلفية؟\"\n  **المرشح:** \"أوضح له أن النظام هيخنق المنبهات وهيقفل الـ Process، ولو حاولنا التحايل بالـ WakeLocks، التطبيق هيتسجل في Google Play كـ Bad Behavior وهيتم خفض ظهوره ورفضه في المراجعات.\"\n\n- **المحاور:** \"ما هو الحل الهندسي الأمثل لو السيرفر بيحتاج يبعث تحديثات حرجة للموبايل بانتظام؟\"\n  **المرشح:** \"الحل هو Server-Driven Architecture عبر رسائل High-Priority FCM Data Messages؛ السيرفر هو اللي يحدد توقيت التحديث ويصحي الموبايل لحظياً عند الحاجة فقط.\"",
        "self_check_ar": "هل أوضحت الرفض الهندسي الصريح للمتطلب؟ هل ذكرت القيود بالأرقام والنسخ؟ وهل اقترحت البدائل الاحترافية كـ FCM و WebSockets؟",
        "references_ar": f"- [Android background execution limits](https://developer.android.com/about/versions/oreo/background) — القيود الصارمة على تنفيذ المهام في الخلفية.\n- [Android Vitals - Excessive wake locks](https://developer.android.com/topic/performance/vitals/wakelock) — معايير جوجل بلاي لمراقبة الاستهلاك السيئ للبطارية.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "نظام أندرويد الحديث مصمم عمداً لمنع أي تنفيذ دوري بالثانية في الخلفية لحماية البطارية وحرارة الجهاز. مكتبة WorkManager بتفرض حداً أدنى إجبارياً قدره 15 دقيقة لأي مهمة دورية، والـ AlarmManager المتكرر بقى تقريبي، وحتى المنبهات الدقيقة بتتخنق في وضع Doze لتشتغل مرة كل ربع ساعة تقريباً، والخدمات الأمامية في أندرويد 14 مقيدة بـ 6 ساعات؛ والحل الهندسي هو الرفض والاعتماد على FCM Push من السيرفر.",
        "best_answer_ar": "لما يطلب متطلب بزنس تنفيذاً دورياً بالثانية في الخلفية، دور المهندس الكبير هو توضيح حقيقة قيود منصة أندرويد ومخاطر انتهاكها.\n\nنظام أندرويد اتطور عبر إصداراته بهدف أساسي هو القضاء التام على الاستيقاظ الدوري للتطبيقات في الخلفية لتوفير البطارية.\n\nأولاً، مكتبة WorkManager بتفرض حداً أدنى إجبارياً قدره 15 دقيقة لأي `PeriodicWorkRequest`؛ ولو حاولت تبرمجها على 5 دقائق، النظام هيكبرها تلقائياً لـ 15 دقيقة، ده غير التأخيرات الإضافية اللي بتفرضها نوافذ Doze Mode وتصنيفات App Standby Buckets.\n\nثانياً، الـ AlarmManager لا يوفر حلاً أيضاً؛ لأن المنبهات المتكررة أصبحت غير دقيقة (Inexact)، وحتى لو برمجت منبهات دقيقة متتالية عبر `setExactAndAllowWhileIdle`، نظام أندرويد بيخنق تكرارها أثناء سكون الهاتف لتصحى مرة واحدة كل 9 إلى 15 دقيقة فقط لمنع استنزاف الشحن.\n\nثالثاً، الـ Foreground Services لم تعد مهرباً مفتوحاً؛ فأندرويد 14 حدد مدة خدمة مزامنة البيانات بـ 6 ساعات كحد أقصى خلال 24 ساعة.\n\nالحل الهندسي هو مواجهة المتطلب واقتراح بديل واقعي: لو البيانات حرجة، السيرفر هو اللي يبعت إشعار FCM فائق الأهمية لحظة حدوث الحدث، أو تتم المزامنة عبر WebSocket فقط طالما الشاشة مفتوحة أمام المستخدم.",
        "deep_answer_ar": "تحت الكابوت، القيود دي متجذرة في معمارية نواة لينكس (Kernel) وإدارة حالات توفير الطاقة بالمعالج. لما شاشة الموبايل تقفل ويفضل ثابت، الهاتف بيدخل في Deep Doze، والمعالج بيدخل في Suspend-to-RAM، وترددات الأنوية بتنزل لأدنى مستوى، ومودم الشبكة بيقفل استقبال البيانات، وجدار الحماية iptables بيمنع أي تطبيق من فتح Sockets.\n\nمحاولة إجبار النظام على التنفيذ الدوري بالثانية بيتطلب حجز مستمر لـ Partial WakeLock، وده تصرف تصنفه جوجل كـ Bad Behavior في تقارير Android Vitals، وهيؤدي لخفض ترتيب التطبيق في متجر Google Play أو حذفه.\n\nبالإضافة لده، أندرويد 14 قفل آخر الثغرات بفرض Timeout صارم على خدمات `dataSync` بمجرد وصولها لـ 6 ساعات تشغيل تراكمية في اليوم، وبيقفل الـ Process بكود `REASON_OTHER`.\n\nالمهندسون الكبار بيحلوا المعضلة دي بإعادة صياغة المشكلة هندسياً مع فريق المنتج. لو الهدف هو مراقبة أجهزة أو أسعار حية، بنفتح الاتصال اللحظي عبر WebSocket فقط طالما التطبيق في الواجهة الأمامية، وأول ما التطبيق ينزل في الخلفية بنقفل الاتصال ونتحول لرسائل FCM High-Priority Data Messages اللي بتصحي التطبيق في ثوانٍ عند حدوث تغيير حقيقي في السيرفر فقط، وبكده بنلبي احتياج البزنس بدون ما نحرق بطارية الجهاز أو نخالف معايير أندرويد وتوفير استقرار تام للتطبيق في بيئة الإنتاج."
    }
}

# ==========================================
# BG-18: Payment reversal reaching backend after app exits
# ==========================================
DATA["BG-18"] = {
    "concept_en": """Executing a mission-critical payment reversal that must survive application termination, process reclamation, and network failure requires combining an offline-first transactional durable mechanism with an idempotent, auditable backend server contract. Relying on transient coroutines in viewModelScope or lifecycleScope is unacceptable because the host process may be destroyed before network delivery. The client-side mechanism relies on the Transactional Outbox pattern: within an atomic Room database transaction, the application records a persistent reversal intent (with unique client-generated reversal UUID, parent payment reference, timestamp, and payload) before enqueuing a durable WorkManager OneTimeWorkRequest configured with network constraints and exponential backoff. The server contract mandates an idempotent endpoint (accepting an Idempotency-Key header with strict deduplication), a state-query reconciliation probe endpoint, and strict HTTP status semantics distinguishing retryable server/transport errors (HTTP 5xx, network drops) from non-retryable domain rejections (HTTP 4xx).""",
    "walkthrough_en": """Implementing durable payment reversal and server contract:
```kotlin
// 1. Transactional Outbox commit in Room + WorkManager durable enqueue
class PaymentRepository(
    private val db: AppDatabase,
    private val paymentDao: PaymentDao,
    private val workManager: WorkManager
) {
    suspend fun schedulePaymentReversal(paymentId: String, reason: String) = withContext(Dispatchers.IO) {
        val reversalId = UUID.randomUUID().toString()
        val reversalEntity = PaymentReversalEntity(
            reversalId = reversalId,
            paymentId = paymentId,
            reason = reason,
            status = ReversalStatus.PENDING,
            createdAtEpoch = System.currentTimeMillis()
        )

        // Step A: Atomic local commit to Room (Survives immediate app kill)
        db.withTransaction {
            paymentDao.insertReversal(reversalEntity)
        }

        // Step B: Enqueue durable WorkManager task with Exponential Backoff
        val request = OneTimeWorkRequestBuilder<PaymentReversalWorker>()
            .setInputData(workDataOf("REVERSAL_ID" to reversalId))
            .setConstraints(Constraints.Builder().setRequiredNetworkType(NetworkType.CONNECTED).build())
            .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 15, TimeUnit.SECONDS)
            .build()

        workManager.enqueueUniqueWork("reversal_$reversalId", ExistingWorkPolicy.KEEP, request)
    }
}

// 2. Durable Worker executing with server contract
class PaymentReversalWorker(
    appContext: Context,
    params: WorkerParameters,
    private val paymentDao: PaymentDao,
    private val paymentApi: PaymentApi
) : CoroutineWorker(appContext, params) {

    override suspend fun doWork(): Result = withContext(Dispatchers.IO) {
        val reversalId = inputData.getString("REVERSAL_ID") ?: return@withContext Result.failure()
        val reversal = paymentDao.getReversal(reversalId) ?: return@withContext Result.failure()

        if (reversal.status == ReversalStatus.COMPLETED) return@withContext Result.success()

        try {
            // Idempotent Server Contract: Idempotency-Key header guarantees single execution
            val response = paymentApi.reversePayment(
                idempotencyKey = reversal.reversalId,
                paymentId = reversal.paymentId,
                reason = reversal.reason
            )
            paymentDao.updateReversalStatus(reversalId, ReversalStatus.COMPLETED, response.reversalReceiptId)
            Result.success()
        } catch (e: HttpException) {
            when (e.code()) {
                in 500..599 -> Result.retry() // Server transient outage: retry with exponential backoff
                else -> {
                    paymentDao.updateReversalStatus(reversalId, ReversalStatus.FAILED, null)
                    Result.failure() // 4xx: unrecoverable domain failure, stop retry loop
                }
            }
        } catch (e: IOException) {
            Result.retry() // Network drop: retry when connectivity returns
        }
    }
}
```""",
    "short_en": """Execute a durable payment reversal by committing the reversal intent with a unique UUID to a Room database in an atomic transaction before enqueuing a WorkManager OneTimeWorkRequest with connected network constraints. Pair this with an idempotent backend contract that enforces an Idempotency-Key header, supports status reconciliation queries, and returns clear HTTP status codes distinguishing transient 5xx retries from non-retryable 4xx client errors.""",
    "structured_en": """Guaranteeing that a payment reversal reaches the backend after application exit requires coupling a resilient local persistence mechanism with an idempotent server contract.
The client mechanism relies on the Transactional Outbox pattern implemented through Room and WorkManager. When a reversal is triggered, the repository generates a persistent UUID and commits the reversal record into the Room database with a PENDING status inside an atomic transaction. Only after this commit succeeds does the repository enqueue a OneTimeWorkRequest with connected network constraints and exponential backoff. Because WorkManager serializes the job to disk, execution is guaranteed even if the user swipes away the application or the device reboots.
The server contract requires an idempotent API endpoint that accepts the client-generated UUID via an Idempotency-Key header. The backend logs this key in a transactional database ledger; repeated calls with the same key return the original cached receipt without executing duplicate reversals.
The contract must also provide a query endpoint to verify reversal state if network timeouts occur, and enforce strict status semantics where transient 5xx errors trigger retries while permanent 4xx failures terminate cleanly.""",
    "deep_senior_en": """Under the hood, financial reversals in mobile systems present the most acute distributed consensus challenges due to asynchronous network partitions and process teardowns. If a reversal is dispatched through standard in-memory scopes, the user pressing the home button followed by the OS reclaiming memory halts the network socket midway, leaving the transaction in an ambiguous state where money may remain deducted or improperly credited.
Senior engineers construct a fault-tolerant multi-layered safety net. In the client layer, the Room database guarantees durable local write-ahead logging before network dispatch.
In the WorkManager layer, exponential backoff (e.g., 15s, 30s, 60s, up to platform caps) ensures that temporary payment gateway outages do not create a denial-of-service avalanche.
The server contract must support distributed two-phase reconciliation. When the backend receives the reversal request, it validates the Idempotency-Key against an atomic database table with a unique constraint. If the worker encounters a network timeout after the server committed the reversal, the retried worker resends the identical key; the backend detects the prior commit and returns HTTP 200 with the original reversal receipt.
Furthermore, staff engineers establish a dead-letter queue and dual-trigger reconciliation: if a reversal encounters repeated 5xx errors exceeding a max retry threshold, the record transitions to REQUIRES_MANUAL_AUDIT in Room, alerting internal analytics.
Simultaneously, a low-frequency periodic reconciliation worker scans the outbox table for unconfirmed reversals, ensuring that every financial transaction reaches eventual consistency regardless of edge-case operating system crashes.""",
    "meta_ar": {
        "id": "BG-18",
        "questionAr": "عملية رد مدفوعات (Payment Reversal) يجب أن تصل للسيرفر حتى بعد خروج المستخدم. ما الآلية الدائمة وعقد السيرفر المطلوبان؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "تصميم المعاملات المالية الحساسة في بيئة الموبايل، والدمج بين نمط Transactional Outbox في Room ومكتبة WorkManager، وتصميم عقود السيرفر الـ Idempotent، والتفرقة بين أخطاء 4xx و 5xx.",
        "why_it_matters_ar": "الاعتماد على الكوروتينات العادية لرد الأموال يتسبب في ضياع العملية عند خروج العميل، مما يؤدي لمشاكل قانونية ومالية جسيمة وفقدان أموال العملاء.",
        "worked_example_ar": "حفظ المعاملة في Room وجدولتها في WorkManager مع هيدر Idempotency:\n```kotlin\ndb.withTransaction { dao.insertReversal(reversal.copy(status = PENDING)) }\nval req = OneTimeWorkRequestBuilder<ReversalWorker>()\n    .setConstraints(Constraints.Builder().setRequiredNetworkType(NetworkType.CONNECTED).build())\n    .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 15, TimeUnit.SECONDS).build()\nworkManager.enqueueUniqueWork(\"rev_$id\", ExistingWorkPolicy.KEEP, req)\n```",
        "trade_offs_ar": "تصميم نظام Outbox وعقد Idempotent في السيرفر يتطلب جهداً معمارياً إضافياً وتنسيقاً بين فريقي الموبايل والباك إند، لكنه ضرورة حتمية لا غنى عنها في أي تطبيق مالي.",
        "failure_modes_ar": "إعادة محاولة تنفيذ العملية عند استلام كود خطأ من نوع 4xx (Client Error) مثل 400 أو 404، مما يدخل التطبيق في حلقة إعادة محاولة لا نهائية تستنزف الموارد.",
        "production_perspective_ar": "في بوابات الدفع والتطبيقات البنكية، نعتبر كل عملية Reversal بمثابة كائن لا يموت؛ يسجل في Room بـ UUID فوري، ويتكفل WorkManager بتسليمه مع التحقق من 200 OK.",
        "how_to_answer_ar": "قسم الإجابة لمحورين: الآلية الدائمة في الموبايل (Room Outbox + WorkManager بمحددات وتراجع أسي)، وعقد السيرفر (Idempotency-Key ونقطة استعلام والتفرقة بين أخطاء 4xx و 5xx).",
        "talking_points_ar": "نمط Transactional Outbox، والجدولة الدائمة بـ WorkManager، وعقد السيرفر الـ Idempotent، وهيدر Idempotency-Key، والتفرقة بين أخطاء الشبكة 5xx وأخطاء العمل 4xx.",
        "follow_ups_ar": "- **المحاور:** \"كيف يتعامل الـ Worker مع أخطاء HTTP 400 مقابل أخطاء HTTP 500؟\"\n  **المرشح:** \"أخطاء 5xx وأخطاء انقطاع الشبكة بنرجع معها Result.retry() لإعادة المحاولة بـ Backoff؛ بينما أخطاء 4xx بنعتبرها أخطاء منطقية غير قابلة للإصلاح ونرجع Result.failure() فوراً.\"\n\n- **المحاور:** \"ماذا يحدث لو قفل المستخدم التطبيق من شاشة المهام (Swiped away) في اللحظة التي بدأ فيها الرد؟\"\n  **المرشح:** \"الـ WorkManager بيسجل الطلب في SQLite داخلي ويضمن استئناف تشغيله عبر JobScheduler في الخلفية حتى بعد خروج المستخدم التام.\"",
        "self_check_ar": "هل شرحت نمط Outbox في Room؟ هل وضحت مواصفات عقد السيرفر وهيدر Idempotency-Key؟ وهل بينت التعامل مع أكواد أخطاء HTTP المختلفة؟",
        "references_ar": f"- [WorkManager for critical tasks](https://developer.android.com/topic/libraries/architecture/workmanager) — استخدام WorkManager للمهام الحساسة والمالية.\n- [Financial Transaction Idempotency](https://stripe.com/docs/api/idempotent_requests) — المعايير الدولية لتأمين المعاملات المالية الموزعة.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "بنضمن وصول عملية رد المدفوعات بحفظ نية العملية أولاً برقم UUID فريد في قاعدة بيانات Room داخل Transaction ذري بحالة PENDING، وبعدها بنجدول OneTimeWorkRequest في WorkManager بمحددات اتصال الإنترنت وتراجع أسي لضمان الصمود أمام إغلاق التطبيق. وفي جانب السيرفر، بنحتاج عقد Idempotent صريح بيستلم هيدر Idempotency-Key ويمنع تكرار العملية مع توفير نقطة استعلام ونظام تمييز بين أخطاء 5xx المؤقتة و 4xx الدائمة.",
        "best_answer_ar": "ضمان وصول عملية رد المدفوعات بعد إغلاق التطبيق بيتطلب تكاملاً وثيقاً بين آلية تخزين دائمة في الموبايل وعقد برمجي صارم مع السيرفر.\n\nالآلية الدائمة في الموبايل بتعتمد على نمط Transactional Outbox مع WorkManager. لما المستخدم يطلب رد العملية، الـ Repository بيولد كود فريد `reversal_id` (كود UUID) ويسجل بيانات العملية في Room بحالة PENDING داخل معاملة ذرية `db.withTransaction`. بعد نجاح الحفظ، بنجدول `OneTimeWorkRequest` بمحددات توفر الإنترنت وسياسة `BackoffPolicy.EXPONENTIAL`. لأن WorkManager بيحفظ الطلب في قاعدة بيانات SQLite داخلية، المهمة هتتنفذ حتماً حتى لو المستخدم عمل Swipe للتطبيق أو عمل ريستارت للهاتف.\n\nأما عقد السيرفر (Server Contract)، فيتطلب ثلاثة شروط أساسية:\nأولاً، نقطة نهاية تدعم الـ Idempotency وتستقبل كود الـ UUID في هيدر `Idempotency-Key` لمنع تكرار رد المبلغ لو أُعيد إرسال الطلب.\nثانياً، توفير نقطة استعلام (Status Query Endpoint) تتيح للـ Worker فحص حالة العملية لو انقطع الاتصال في المنتصف.\nثالثاً، دلالات واضحة لأكواد الـ HTTP: أخطاء 5xx وانقطاع الشبكة يرجع معها `Result.retry()` لإعادة المحاولة لاحقاً، بينما أخطاء 4xx (زي عملية غير صالحة) يرجع معها `Result.failure()` لإيقاف المحاولات وتفادي الحلقات اللانهائية.",
        "deep_answer_ar": "تحت الكابوت، المعاملات المالية في تطبيقات الموبايل هي أكثر العمليات عرضة لمشاكل عدم الاتساق (Distributed Consensus Failures). لو اعتمدت على كوروتين في `viewModelScope`، خروج المستخدم من التطبيق هيقتل الكوروتين في أجزاء من الثانية ويضيع طلب الرد في الذاكرة، مما يعرض الشركة لمساءلات قانونية.\n\nالمهندسون الكبار بيصمموا شبكة أمان ثلاثية الطبقات. أولاً، طبقة الـ Write-Ahead Logging في Room بتضمن إن نية الرد مسجلة على القرص الصلب قبل ما نلمس أي كود شبكة. ثانياً، محرك WorkManager بيجدول المهمة عبر `JobScheduler`، ولما ترجع خطأ شبكة، سياسة الـ Exponential Backoff بتضاعف فترات الانتظار (15 ثم 30 ثم 60 ثانية) لحماية بوابات الدفع من الانهيار.\n\nثالثاً، في جانب السيرفر، التحقق من الـ `Idempotency-Key` بيتم داخل Transaction ذري في قاعدة بيانات الباك إند؛ لو السيرفر لقى المفتاح مسجل عنده، بيرجع كود 200 OK مع بيانات الإيصال السابق فوراً بدون ما يلمس حساب العميل.\n\nعلاوة على ذلك، في الحالات القصوى لو استمر فشل السيرفر لأكثر من الحد المسموح، الـ Worker بيحول حالة السجل في Room لـ `MANUAL_AUDIT_REQUIRED` لإخطار فريق العمليات، مع تشغيل مهمة مصالحة دورية في الخلفية تضمن الوصول للاتساق النهائي (Eventual Consistency) التام بدون أي تدخل يدوي من العميل وبأعلى درجات الأمان المالي الممكنة."
    }
}


def main():
    print(f"Elevating {len(DATA)} questions in BG (BG-10 to BG-18)...")
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
    ee.save_topic_metadata("bg_10_18", {qid: d["meta_ar"] for qid, d in DATA.items()})

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
        print("\nAll 9 BG questions (BG-10 to BG-18) successfully elevated and passed validation!")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
