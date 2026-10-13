#!/usr/bin/env python3
"""Generator for DAT-15 through DAT-22 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "dat.json"

DAT_15_22 = [
    {
        "id": "DAT-15",
        "arabic_explanation": (
            "كيف تزامن التعديلات المحلية (Local Writes) بعد انقطاع الاتصال في تطبيق Offline-First؟\n\n"
            "1. دورة حياة العملية غير المتصلة (Offline Mutation Lifecycle):\n   - **الخطوة 1: التسجيل المحلي الفوري في Room (Atomic Commit)**:\n     * عند ضغط المستخدم على 'إرسال تعليق' أو 'تعديل ملف' وهو غير متصل، يتم حفظ التعديل في جدول البيانات الأساسي مع حالة `SYNC_PENDING`، ويتم إضافة سجل إلى جدول طابور المزامنة `sync_queue` يحتوي على: `operationId: UUID`, `actionType: EDIT`, `entityId`, `payloadJson`, `timestamp`.\n     * يتم هذا داخل `database.withTransaction` لضمان عدم وجود تعديل بدون سجل في الطابور.\n     * الـ UI تُحدّث فوراً ليشاهد المستخدم تعديله في 5ms.\n   - **الخطوة 2: جدولة المزامنة المضمونة عبر WorkManager**:\n     * يتم إطلاق `OneTimeWorkRequestBuilder<SyncWorker>()` مع شرط توفر الإنترنت `Constraints(NetworkType.CONNECTED)`.\n     * يتميز WorkManager بأنه يضمن التنفيذ حتى لو أغلقت الشاشة، أو مات الـ Process، أو أعيد تشغيل الهاتف.\n   - **الخطوة 3: التنفيذ المتسلسل والمعالجة (Execution & Acknowledgment)**:\n     * يقرأ `SyncWorker` العمليات بالترتيب الزمني (FIFO).\n     * يرسل العملية إلى السيرفر مرفقة بـ `idempotencyKey = operationId`.\n     * عند استلام `200 OK`، يتم حذف السجل من طابور `sync_queue` وتحديث حالة الكيان في Room إلى `SYNCED`."
        ),
        "practical_walkthrough": (
            "هيكل طابور المزامنة و SyncWorker لمعالجة التعديلات غير المتصلة:\n"
            "```kotlin\n"
            "// 1. كيان طابور المزامنة المحلي في Room:\n"
            "@Entity(tableName = \"sync_mutations_queue\")\n"
            "data class SyncMutationEntity(\n"
            "    @PrimaryKey val operationId: String = UUID.randomUUID().toString(),\n"
            "    val entityType: String,\n"
            "    val entityId: String,\n"
            "    val action: String, // CREATE, UPDATE, DELETE\n"
            "    val payloadJson: String,\n"
            "    val createdAt: Long = System.currentTimeMillis()\n"
            ")\n"
            "\n"
            "// 2. معالج المزامنة في WorkManager:\n"
            "@HiltWorker\n"
            "class OutboxSyncWorker @AssistedInject constructor(\n"
            "    @Assisted appContext: Context,\n"
            "    @Assisted workerParams: WorkerParameters,\n"
            "    private val database: AppDatabase,\n"
            "    private val syncApi: RemoteSyncApi\n"
            ") : CoroutineWorker(appContext, workerParams) {\n"
            "\n"
            "    override suspend fun doWork(): Result {\n"
            "        val pendingMutations = database.syncDao().getOldestPendingMutations(limit = 20)\n"
            "        \n"
            "        for (mutation in pendingMutations) {\n"
            "            try {\n"
            "                // إرسال العملية مع Idempotency Key:\n"
            "                syncApi.pushMutation(mutation.operationId, mutation.toRequest())\n"
            "                // عند التأكيد، نحذفها من الطابور ونثبت الحالة:\n"
            "                database.withTransaction {\n"
            "                    database.syncDao().deleteMutation(mutation.operationId)\n"
            "                    database.itemsDao().markSynced(mutation.entityId)\n"
            "                }\n"
            "            } catch (e: IOException) {\n"
            "                // خطأ شبكة عابر: نطلب من WorkManager إعادة المحاولة بـ Exponential Backoff:\n"
            "                return Result.retry()\n"
            "            } catch (e: HttpException) {\n"
            "                if (e.code() == 409) handleConflict(mutation) // معالجة النزاع\n"
            "                else database.syncDao().markFailed(mutation.operationId, e.message)\n"
            "            }\n"
            "        }\n"
            "        return Result.success()\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Sync offline writes by committing the optimistic edit and an outbox queue record atomically to Room. Enqueue a WorkManager worker with a connected network constraint. When online, the worker processes outbox operations sequentially using idempotency keys, deleting queue records only upon verified server acknowledgment.",
        "best_answer": (
            "Synchronizing offline writes requires the **Outbox Pattern** backed by WorkManager to guarantee eventual consistency:\n\n"
            "1. **Atomic Local Outbox Commit**:\n   - When a user performs an offline edit, we do not simply mutate the UI state. We open a `roomDatabase.withTransaction { }`.\n   - Inside the transaction, we write the optimistic entity state to Room (`status = PENDING_SYNC`) AND insert a mutation command record into an internal `sync_outbox` table (`operationId = UUID`, `payload`, `timestamp`). Both succeed or fail together.\n   - The UI reflects the change in 5ms.\n\n"
            "2. **Durable Sync Dispatcher (`WorkManager`)**:\n   - Enqueue a unique WorkManager job (`ExistingWorkPolicy.APPEND_OR_REPLACE`) requiring `NetworkType.CONNECTED`.\n   - WorkManager guarantees execution across app process death, phone reboots, and background constraints.\n\n"
            "3. **Idempotent Sequential Processing**:\n   - The worker drains the outbox in chronological order. Each HTTP call transmits `Idempotency-Key: <operationId>`.\n   - Only upon receiving an explicit HTTP 200/201 response does the worker remove the mutation from the outbox and flip the entity status to `SYNCED` in SQLite."
        ),
        "deep_answer": (
            "Two severe failure modes occur in production offline sync engines:\n\n"
            "1. **Out-of-Order Execution (The Chronological Bug)**:\n   If a user edits an item offline and then deletes it 5 seconds later, firing two independent parallel network requests risks the Delete arriving *before* the Edit. The server executes Delete, then executes Edit, resurrecting the deleted item! "
            "To prevent this, the outbox processor must process mutations for the same `entityId` strictly sequentially (FIFO) or collapse intermediate states before syncing.\n\n"
            "2. **The Zombie Pending Mutation (Process Kill during Sync)**:\n   If the worker sends the mutation, the server commits it, but the cellular radio drops before the client receives the acknowledgment, the mutation remains in `sync_outbox`. "
            "When connectivity restores, the worker re-submits the mutation. Because the request carries the exact same `operationId` as its Idempotency Key, the backend recognizes it as a duplicate and acknowledges success without repeating side effects."
        ),
        "follow_ups": [
            {
                "question": "Why shouldn't you run offline sync in a standard ViewModel coroutine?",
                "answer": "If the user closes the app or navigates away, the ViewModelScope is cancelled immediately, aborting the sync and leaving operations stranded until the screen is reopened."
            },
            {
                "question": "What is 'Mutation Coalescing'?",
                "answer": "Combining multiple pending edits on the same record into a single network payload before uploading, saving cellular bandwidth and reducing API requests."
            }
        ]
    },
    {
        "id": "DAT-16",
        "arabic_explanation": (
            "كيف يتم حل النزاعات وتعارض البيانات (Conflict Resolution) عندما تختلف الحالة المحلية (Local State) عن حالة السيرفر (Server State)؟\n\n"
            "1. أسباب النزاع في بيئة الـ Offline-First:\n   - قام المستخدم بتعديل ملف أو مهمة على الهاتف وهو في الطائرة.\n   - في نفس الوقت، قام زميله في العمل بتعديل نفس الملف من متصفح الويب على السيرفر.\n   - عندما يعود هاتف المستخدم للإنترنت، تصبح هناك نسختان متعارضتان من الحقيقة لنفس المعرف (`EntityId`).\n\n"
            "2. الاستراتيجيات المعمارية لحل النزاعات (Conflict Resolution Strategies):\n   - **Last-Write-Wins (LWW - التعديل الأحدث يفوز)**:\n     * اعتماد النسخة ذات الـ Timestamp الأحدث.\n     * **تحذير**: كارثي في كثير من الحالات لأن ساعات الهواتف غير مضبوطة (Clock Drift)، مما قد يمسح بيانات مهمة دون علم المستخدم.\n   - **Server-Wins (السيرفر هو الحاكم الأخير)**:\n     * مناسب للبيانات السلطوية (الأسعار، المخزون، الحالات البنكية). السيرفر يرفض التعديل بـ `409 Conflict`، ويجبر العميل على تحديث نسخته المحلية.\n   - **Client-Wins (العميل يفوز)**:\n     * للمسودات الشخصية والملاحظات الخاصة التي لا يتشاركها عدة مستخدمين.\n   - **3-Way Merging (الدمج الذكي للحقول)**:\n     * مقارنة النسخة المشتركة القديمة (Base Version) والنسخة المحلية والنسخة البعيدة. إذا عدل العميل رقم الهاتف وعدل السيرفر العنوان، يتم دمج الحقلين معاً بنجاح.\n   - **Manual User Resolution (تدخل المستخدم)**:\n     * عرض شاشة للمستخدم بمقارنة جنباً إلى جنب (Side-by-Side Diff) ليختار النسخة التي يريد الاحتفاظ بها (مثل Google Keep أو Git Merge Conflict)."
        ),
        "practical_walkthrough": (
            "تنفيذ معالجة النزاع عبر Optimistic Locking باستخدام Version Vectors / ETag:\n"
            "```kotlin\n"
            "data class NoteSyncDto(\n"
            "    val id: String,\n"
            "    val content: String,\n"
            "    val baseVersion: Long // رقم الإصدار الذي كان لدى العميل عند بدء التعديل\n"
            ")\n"
            "\n"
            "class NoteRepositoryImpl @Inject constructor(\n"
            "    private val noteDao: NoteDao,\n"
            "    private val noteApi: NoteApiService\n"
            ") : NoteRepository {\n"
            "\n"
            "    suspend fun syncNote(noteId: String) {\n"
            "        val localNote = noteDao.getNoteById(noteId) ?: return\n"
            "        \n"
            "        try {\n"
            "            val response = noteApi.updateNote(\n"
            "                id = noteId,\n"
            "                dto = NoteSyncDto(localNote.id, localNote.content, localNote.version)\n"
            "            )\n"
            "            // نجاح: تحديث الإصدار الجديد من السيرفر:\n"
            "            noteDao.update(localNote.copy(version = response.newVersion, syncStatus = SYNCED))\n"
            "        } catch (e: HttpException) {\n"
            "            if (e.code() == 409) {\n"
            "                // تعارض حقيقي: السيرفر يحمل إصداراً أحدث!\n"
            "                val serverNote = noteApi.fetchLatestNote(noteId)\n"
            "                \n"
            "                // حفظ النزاع في Room وعرض إشعار للمستخدم:\n"
            "                noteDao.recordConflict(\n"
            "                    noteId = noteId,\n"
            "                    localContent = localNote.content,\n"
            "                    serverContent = serverNote.content\n"
            "                )\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Resolve conflicts between local and server state using Optimistic Concurrency Control with version numbers or ETags. When divergent states collide (HTTP 409), choose a domain-appropriate strategy: Server-Wins for authoritative data, field-level 3-way merging for non-overlapping attributes, or manual user review for documents and text.",
        "best_answer": (
            "When offline edits diverge from remote updates, naive Last-Write-Wins (LWW) based on device timestamps causes silent data loss due to client clock drift. Robust architectures implement **Optimistic Concurrency Control (OCC)**:\n\n"
            "1. **Version Tracking / ETags**: Every entity carries a `version: Long` or an HTTP `ETag` hash. When mutating data, the client submits `{ entityId, payload, baseVersion }`.\n\n"
            "2. **Server-Side Compare-and-Set**: If the server's current version matches `baseVersion`, the update commits and increments the version. If another client updated the record in the interim, the server rejects the write with **`409 Conflict`** and returns the latest server state.\n\n"
            "3. **Resolution Strategies by Business Domain**:\n   - **Authoritative Data (Inventory, Financial Balance)**: **Server-Wins**. The client discards local changes and updates Room with server ground truth.\n   - **Granular Attribute Merging**: If the server changed `status` and the client changed `notes`, apply 3-way merging to combine non-overlapping fields.\n   - **Collaborative Text (Notes, Documents)**: Present a visual conflict dialog allowing the user to select the preferred version or fork into two separate documents."
        ),
        "deep_answer": (
            "In advanced distributed mobile architectures (such as collaborative canvases or offline Google Docs), teams implement **CRDTs (Conflict-free Replicated Data Types)**.\n\n"
            "CRDTs (such as State-based or Operation-based PN-Counters, LWW-Element-Sets, or Yjs/Automerge trees) are mathematically proven to converge to the identical state on all nodes without central locking or conflict dialogs, regardless of network arrival order or message duplication.\n\n"
            "However, for standard enterprise Android applications, Optimistic Concurrency Control with a conflict resolution table in Room provides 99% of the reliability with a fraction of the algorithmic complexity."
        ),
        "follow_ups": [
            {
                "question": "Why is client device time dangerous for timestamp-based conflict resolution?",
                "answer": "Users can alter their device clock manually, or time zones and NTP sync failures can make client timestamps hours ahead or behind real UTC time."
            },
            {
                "question": "What is a 3-way merge in data synchronization?",
                "answer": "Comparing the base ancestor version, the local branch, and the remote branch to determine which specific fields changed on each side."
            }
        ]
    },
    {
        "id": "DAT-17",
        "arabic_explanation": (
            "كيف تدير انتهاء صلاحية الكاش (Caching Expiration) وإبطاله (Invalidation) في تطبيقات Android؟\n\n"
            "1. الفرق بين انتهاء الصلاحية والإبطال (Expiration vs. Invalidation):\n   - **Expiration (انتهاء الصلاحية الزمني - Time-based TTL)**: تحديد مدة بقاء البيانات صالحة في الكاش (Time-To-Live). بعد مرور 10 دقائق مثلاً، تعتبر البيانات Stale وتتطلب إعادة طلبها من السيرفر.\n   - **Invalidation (الإبطال الفوري المبني على الأحداث - Event-driven Invalidation)**: مسح أو تفريغ الكاش فوراً نتيجة لحدث معين (مثل قيام المستخدم بتسجيل الخروج Logout، أو تعديل الملف الشخصي، أو استلام Push Notification من السيرفر تفيد بتغير البيانات).\n\n"
            "2. استراتيجيات إدارة الصلاحية حسب طبيعة البيانات:\n   - **بيانات ثابتة (Static Assets / Lookup tables)**: TTL طويل جداً (أيام أو أسابيع).\n   - **بيانات متغيرة متوسطة (News / Products Feed)**: TTL يتراوح بين 5 إلى 15 دقيقة مع دعم Stale-While-Revalidate.\n   - **بيانات مالية وحساسة (Account Balance / Rights Entitlements)**: TTL صفر (No-Cache)، تتطلب دائماً فحص السيرفر أو استخدام ETag `If-None-Match`.\n\n"
            "3. آليات الإبطال الصارمة (Strict Invalidation Rules):\n   - **عند تسجيل الخروج (Logout / Account Switch)**: يجب إفراغ جميع جداول الـ Room والـ DataStore المرتبطة بالمستخدم لمنع تسريب بياناته للمستخدم التالي.\n   - **عند العمليات المحلية (Local Mutations)**: إذا قام المستخدم بحذف عنصر من السلة، يتم إبطال وحذف العنصر من Room فوراً دون انتظار استجابة السيرفر."
        ),
        "practical_walkthrough": (
            "إدارة انتهاء صلاحية الكاش عبر TTL زمني وترويسات ETag في الـ Repository:\n"
            "```kotlin\n"
            "class CachedFeedRepository @Inject constructor(\n"
            "    private val feedDao: FeedDao,\n"
            "    private val feedApi: FeedApiService,\n"
            "    private val metaStore: CacheMetadataStore\n"
            ") {\n"
            "    private val CACHE_TTL_MS = TimeUnit.MINUTES.toMillis(15) // صلاحية 15 دقيقة\n"
            "\n"
            "    fun observeFeed(): Flow<List<FeedItem>> = feedDao.observePosts()\n"
            "\n"
            "    suspend fun refreshFeedIfExpired(forceRefresh: Boolean = false) {\n"
            "        val lastFetchTime = metaStore.getLastFetchTime()\n"
            "        val isExpired = System.currentTimeMillis() - lastFetchTime > CACHE_TTL_MS\n"
            "\n"
            "        if (isExpired || forceRefresh) {\n"
            "            val savedETag = metaStore.getFeedETag()\n"
            "            // إرسال ETag للتحقق مما إذا كان السيرفر قد غير البيانات:\n"
            "            val response = feedApi.fetchFeed(ifNoneMatch = savedETag)\n"
            "            \n"
            "            if (response.code() == 304) {\n"
            "                // 304 Not Modified: البيانات لم تتغير على السيرفر! نجدد الـ TTL فقط ونوفر الباندويث:\n"
            "                metaStore.saveLastFetchTime(System.currentTimeMillis())\n"
            "            } else if (response.isSuccessful && response.body() != null) {\n"
            "                // 200 OK: بيانات جديدة، نحفظها في Room ونحدث الـ ETag:\n"
            "                feedDao.replaceFeed(response.body()!!.items)\n"
            "                metaStore.saveFeedETag(response.headers()[\"ETag\"])\n"
            "                metaStore.saveLastFetchTime(System.currentTimeMillis())\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Manage cache expiration using domain-specific TTLs paired with HTTP conditional validation (ETags / If-None-Match returning 304 Not Modified). Invalidate caches proactively upon user mutations, FCM push invalidations, and enforce immediate database purges on logout or user switching.",
        "best_answer": (
            "A comprehensive caching strategy separates time-based expiration from event-driven invalidation:\n\n"
            "1. **Time-To-Live (TTL) Expiration**:\n   - Different domains demand different freshness thresholds: user avatars (7 days), catalog feed (15 minutes), account balances (0 seconds / always revalidate).\n   - Leverage **HTTP Conditional Requests**: Store server `ETag` or `Last-Modified` headers. When the TTL expires, issue a lightweight `If-None-Match` request. If unchanged, the server returns **`304 Not Modified`** with an empty body, saving mobile bandwidth while refreshing the TTL.\n\n"
            "2. **Event-Driven Invalidation**:\n   - **Local Write Invalidation**: When a user updates their profile, the repository immediately mutates Room, ensuring UI screens observe fresh state without waiting for a TTL cycle.\n   - **Remote Server Invalidation**: Use high-priority FCM Silent Push notifications to instruct clients to invalidate specific cache keys when backend data updates.\n   - **Session Purges**: On `Logout` or account switching, execute an atomic SQLite wipe (`database.clearAllTables()`) to prevent data leaking between users."
        ),
        "deep_answer": (
            "A subtle pitfall in Android caching is **Clock Skew with Device Time**.\n\n"
            "If a developer calculates expiration using `System.currentTimeMillis()` (`now - lastFetched > TTL`), and the user manually alters device time or travels across time zones, the cache may appear permanently expired or permanently fresh.\n\n"
            "To prevent clock skew bugs:\n"
            "- Use **`SystemClock.elapsedRealtime()`** for in-session relative cache calculations (which counts milliseconds since device boot, immune to user time adjustments).\n"
            "- For persistent multi-day caches, rely on the server's HTTP `Date` header to calculate relative age rather than trusting the Android hardware clock."
        ),
        "follow_ups": [
            {
                "question": "What is the advantage of HTTP 304 Not Modified?",
                "answer": "It informs the client that the cached data is still valid without re-transmitting the HTTP response payload, saving battery and cellular data."
            },
            {
                "question": "Why shouldn't you delete cached data immediately when a TTL expires?",
                "answer": "Keep the stale data to support offline viewing; mark it as stale and attempt a revalidation, falling back to stale content if the network fails."
            }
        ]
    },
    {
        "id": "DAT-18",
        "arabic_explanation": (
            "المعاملة تُحفظ في قاعدة البيانات وتعمل بنجاح في Debug، لكنها تختفي تماماً بعد إعادة تشغيل التطبيق في Release Builds فقط! كيف تشخص وتصلح هذه المشكلة الغامضة؟\n\n"
            "1. تشريح أسباب الاختلاف بين Debug و Release (Root Cause Analysis):\n   - المشكلة لا تحدث في Debug ولكنها تحدث في Release دائماً ترتبط بأحد العوامل التالية:\n     * **قواعد R8/ProGuard وتحسينات الـ Bytecode**: قام R8 بحذف الـ No-Arg Constructor أو تغيير أسماء الحقول عبر الـ Obfuscation، مما جعل Room أو مكتبة التشفير تعجز عن قراءة البيانات بعد إعادة التشغيل.\n     * **ميزة النسخ الاحتياطي التلقائي (Android Auto Backup & GMS Restore)**: في ملف `AndroidManifest.xml`، إعداد `android:allowBackup=\"true\"` يقوم باستعادة قاعدة بيانات قديمة فارغة من Google Cloud عند إعادة تثبيت نسخة Release!\n     * **فقدان مفاتيح التشفير في Android Keystore (SQLCipher / EncryptedSharedPreferences)**: يتم توليد مفتاح التشفير في الذاكرة ولكن يفشل حفظه أو استعادته من الـ Keystore بسبب عدم توفر قواعد حماية R8 للكلاسات المشفرة.\n     * **استدعاء `fallbackToDestructiveMigration()` بالخطأ في Release**: اختلاف في رقم الإصدار بين ملفات الـ Schema أدى لمسح قاعدة البيانات بهدوء عند الإقلاع.\n\n"
            "2. خطة التحقيق التشخيصية المنظمة:\n   - فحص هل البيانات كُتبت فعلياً في ملف SQLite أم كانت معروضة كـ Optimistic UI State فقط في الـ ViewModel.\n   - فحص سجلات Logcat في نسخة Release موقّعة (`release` build مع `debuggable = true` مؤقتاً لتتبع الـ Crash).\n   - مراجعة ملف `proguard-rules.pro` وإضافة قواعد الحماية لكلاسات الـ Entity والـ Room."
        ),
        "practical_walkthrough": (
            "خطوات إصلاح وتأمين كلاسات Room ونظام التخزين ضد مشاكل R8 والـ Backup:\n"
            "```kotlin\n"
            "// 1. تأمين كلاسات Entity ضد R8 Obfuscation في proguard-rules.pro:\n"
            "// لو قام R8 بتغيير أسماء الحقول، تعجز SQLite عن مطابقة الأعمدة:\n"
            "-keepclassmembers class * extends androidx.room.RoomDatabase {\n"
            "    public void clearAllTables();\n"
            "}\n"
            "-keep class * extends androidx.room.RoomDatabase\n"
            "-keep @androidx.room.Entity class * { *; }\n"
            "-keep class * implements androidx.room.migration.Migration { *; }\n"
            "\n"
            "// 2. منع استعادة النسخ الاحتياطية القديمة من السحابة في AndroidManifest.xml:\n"
            "// <application\n"
            "//     android:allowBackup=\"false\"\n"
            "//     android:fullBackupContent=\"false\" ... />\n"
            "\n"
            "// 3. التحقق البرمجي من أن fallbackToDestructiveMigration غير مفعل:\n"
            "Room.databaseBuilder(context, AppDatabase::class.java, \"app.db\")\n"
            "    .addMigrations(MIGRATION_1_2, MIGRATION_2_3)\n"
            "    // ❌ احذر تماماً من كتابة هذا السطر في Release:\n"
            "    // .fallbackToDestructiveMigration() // هذا يمسح قاعدة البيانات إذا لم يجد مسار ترحيل!\n"
            "    .build()\n"
            "```"
        ),
        "quick_answer": "Investigate R8 obfuscation stripping Entity properties or default constructors, unexpected Auto Backup restoring stale databases from Google Cloud, fallbackToDestructiveMigration wiping data on version mismatches, or Android Keystore master keys becoming invalidated between app launches in release builds.",
        "best_answer": (
            "A release-only database disappearance that succeeds in debug points to production compilation transforms or platform backup mechanisms:\n\n"
            "1. **R8 / ProGuard Obfuscation**: R8 processes release builds aggressively. If Entity classes or TypeConverters lack keep rules (`@Keep` or `-keep @androidx.room.Entity class * { *; }`), R8 renames fields or strips reflective no-arg constructors. Room may fail to deserialize existing rows on subsequent launches, failing silently or catching an internal reflection error and returning empty datasets.\n\n"
            "2. **Android Auto Backup Collision**: If `android:allowBackup=\"true\"` is enabled in `AndroidManifest.xml`, the OS can restore an older cloud backup over the SQLite database file during installation or app restoration, replacing the newly written database with a stale snapshot.\n\n"
            "3. **Silent Destructive Migration**: If the release build has an unversioned migration gap and `fallbackToDestructiveMigration()` is active, Room wipes the entire SQLite file on startup rather than crashing with an `IllegalStateException`.\n\n"
            "4. **Keystore Invalidation (SQLCipher / Encrypted DBs)**: If the database is encrypted, ensure the master key in Android Keystore wasn't flagged with `setUserAuthenticationRequired(true)` or invalidated by device lockscreen configuration changes."
        ),
        "deep_answer": (
            "To diagnose this systematically in production:\n\n"
            "1. **Inspect the Physical SQLite File**: Using Android Studio Device File Explorer or an internal debug menu on a signed release build, inspect `/data/data/<package>/databases/app.db`. Check file size and dump table contents via the `sqlite3` CLI tool to verify if rows were committed to disk.\n\n"
            "2. **Verify WAL (Write-Ahead Logging) Checkpoints**: SQLite WAL mode writes transactions into a separate `app.db-wal` file. If the process is killed abruptly before a WAL checkpoint completes and the app configuration disables WAL on restart, uncheckpointed transactions can disappear.\n\n"
            "3. **Rule Out Optimistic UI Illusions**: Ensure the repository actually committed the transaction to SQLite rather than only updating a MutableStateFlow in memory."
        ),
        "follow_ups": [
            {
                "question": "How do you verify whether R8 caused the bug?",
                "answer": "Enable R8 mapping tracing or build a release APK with `minifyEnabled false` and test whether the bug disappears."
            },
            {
                "question": "How do you disable automatic cloud backup of your SQLite database specifically?",
                "answer": "Specify an XML backup rules file (`android:fullBackupContent=\"@xml/backup_rules\"`) and add `<exclude domain=\"database\" path=\"app.db\"/>`."
            }
        ]
    },
    {
        "id": "DAT-19",
        "arabic_explanation": (
            "طلبان متزامنان لتجديد التوكن (Refresh Token) أديا معاً إلى إبطال جلسة المستخدم وتسجيل خروجه بالخطأ. كيف تضبط تسلسل التجديد وتمنع هذا الخطأ؟\n\n"
            "1. تشريح المشكلة (Why Concurrent Requests Invalidate the Session):\n   - معظم خوادم الـ OAuth 2.0 الحديثة تطبق حماية **Refresh Token Rotation (RTR)**: عند استخدام Refresh Token، يُصدر السيرفر توكن جديد ويحرق (Revoke) التوكن القديم فوراً.\n   - إذا أرسل التطبيق طلبين متزامنين بـ Access Token منتهي، يستقبل الاثنان `401 Unauthorized`.\n   - إذا قام كلا الطلبين باستدعاء endpoint التجديد باستخدام نفس الـ Refresh Token القديم:\n     * الطلب الأول يصل السيرفر وينجح ويحرق الـ Refresh Token القديم.\n     * الطلب الثاني يصل بعده بـ 10 ميلي ثانية حاملاً نفس الـ Refresh Token القديم المحروق!\n     * يكتشف السيرفر محاولة استخدام توكن ملغى، ويعتبر ذلك هجوماً واختراقاً (Breach Detection)، فيقوم فوراً بإبطال جميع توكنز المستخدم وحظر الجلسة!\n\n"
            "2. المعمارية الصحيحة لتسلسل التجديد (Serialized Single-Flight Protocol):\n   - **قفل تسلسلي إجباري (Serialized Mutex)**: لا يجوز لأكثر من خيط واحد التحدث إلى endpoint التجديد في نفس الوقت.\n   - **فحص التوكن المزدوج (Double-Check under Lock)**: عند حصول أي خيط على القفل، يقارن التوكن الذي سبب الـ 401 بالتوكن المخزن حالياً. إذا كان التوكن قد تم تحديثه بالفعل بواسطة خيط سابق، يتخطى طلب التجديد ويعيد المحاولة بالتوكن الجديد فوراً.\n   - **جيل الجلسة (Session Generation Counter)**: عداد يمنع أي استجابة تجديد متأخرة من إعادة تنشيط جلسة تم تسجيل خروجها عمداً بواسطة المستخدم."
        ),
        "practical_walkthrough": (
            "التنفيذ البرمجي المانع لسباق تجديد التوكن في OkHttp Authenticator:\n"
            "```kotlin\n"
            "class ThreadSafeAuthenticator @Inject constructor(\n"
            "    private val sessionStore: SessionStore,\n"
            "    private val refreshApi: DedicatedRefreshClient\n"
            ") : Authenticator {\n"
            "\n"
            "    private val lock = Any()\n"
            "\n"
            "    override fun authenticate(route: Route?, response: Response): Request? {\n"
            "        // 1. استخراج التوكن الذي فشل في هذا الطلب المحدد:\n"
            "        val failedToken = response.request.header(\"Authorization\")?.removePrefix(\"Bearer \")\n"
            "\n"
            "        synchronized(lock) {\n"
            "            val currentToken = sessionStore.getAccessToken()\n"
            "\n"
            "            // 2. الفحص المزدوج الحاسم:\n"
            "            // إذا كان التوكن الحالي يختلف عن التوكن الذي فشل، فهذا يعني أن خيطاً آخر\n"
            "            // قد أكمل التجديد بنجاح أثناء انتظار هذا الخيط في الطابور!\n"
            "            if (currentToken != null && currentToken != failedToken) {\n"
            "                // أعد المحاولة مباشرة بالتوكن الجديد بدون استدعاء السيرفر:\n"
            "                return response.request.newBuilder()\n"
            "                    .header(\"Authorization\", \"Bearer $currentToken\")\n"
            "                    .build()\n"
            "            }\n"
            "\n"
            "            // 3. إذا كنا الخيط الأول: استدعاء التجديد مرة واحدة فقط:\n"
            "            val refreshToken = sessionStore.getRefreshToken() ?: return null\n"
            "            val refreshResult = refreshApi.executeRefreshToken(refreshToken)\n"
            "\n"
            "            return if (refreshResult.isSuccessful && refreshResult.tokens != null) {\n"
            "                // حفظ التوكن الجديد و Refresh Token الجديد ذرياً:\n"
            "                sessionStore.updateTokens(refreshResult.tokens.access, refreshResult.tokens.refresh)\n"
            "                \n"
            "                response.request.newBuilder()\n"
            "                    .header(\"Authorization\", \"Bearer ${refreshResult.tokens.access}\")\n"
            "                    .build()\n"
            "            } else {\n"
            "                // فشل حقيقي في التجديد -> مسح الجلسة وإلغاء المحاولات:\n"
            "                sessionStore.clearSession()\n"
            "                null\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Prevent dual refresh invalidation by strictly serializing refresh calls behind a Mutex or synchronized lock with double-checked token validation. When a thread acquires the lock, it checks if the active token was already updated by a preceding thread. If updated, it replays immediately without calling the refresh endpoint.",
        "best_answer": (
            "Under modern OAuth 2.0 Refresh Token Rotation (RTR), using an expired refresh token triggers backend breach detection, instantly revoking all active client sessions. When two concurrent requests receive 401s, both attempting to refresh using the same stale token inevitably invalidates the session.\n\n"
            "To serialize refresh correctly and prevent false logouts:\n\n"
            "1. **Lock Funneling**: Wrap the refresh block inside a thread-safe lock (`synchronized(lock)` in OkHttp Authenticator or a coroutine `Mutex`).\n\n"
            "2. **The Double-Check Token Protocol**: Before making any network call, extract the `failedToken` from the triggering request header and compare it to `sessionStore.getAccessToken()`:\n   - If `currentToken != failedToken`, another thread already executed the refresh while this thread was waiting on the lock. **Skip the refresh call entirely** and retry the request using `currentToken`.\n   - If `currentToken == failedToken`, this thread is the first to arrive. Execute exactly one refresh network request.\n\n"
            "3. **Atomic Session Mutation**: Save both the new access token and the rotated refresh token atomically before releasing the lock."
        ),
        "deep_answer": (
            "A critical edge case is the **Stale Response Race Across Logout**:\n\n"
            "Consider this sequence:\n"
            "1. Thread A fires a token refresh request.\n"
            "2. While the refresh is in flight on the network, the user explicitly taps 'Log Out'. The app clears credentials from storage.\n"
            "3. Thread A's refresh network request succeeds 1 second later and writes fresh tokens back into storage, accidentally resurrecting a logged-out session!\n\n"
            "To prevent this, implement a **Session Generation Counter**:\n"
            "- Maintain an atomic `sessionGeneration: Long` that increments on every explicit logout or login.\n"
            "- Capture the generation ID before initiating the refresh.\n"
            "- Before committing new tokens to storage, verify that `currentGeneration == capturedGeneration`. If mismatched, discard the newly fetched tokens."
        ),
        "follow_ups": [
            {
                "question": "What is Refresh Token Rotation (RTR)?",
                "answer": "An OAuth 2.0 security mechanism where the server issues a new refresh token and revokes the old one on every single refresh, preventing replay attacks."
            },
            {
                "question": "Why must the refresh HTTP client be independent of the primary OkHttpClient?",
                "answer": "If the refresh client shares the primary client's Authenticator, an unexpected 401 on the refresh endpoint triggers recursive authentication calls, causing a deadlock."
            }
        ]
    },
    {
        "id": "DAT-20",
        "arabic_explanation": (
            "قبل السيرفر عملية دفع مالي (Payment Accepted) لكن الاستجابة ضاعت في شبكة الهاتف (Lost Network Response). كيف تتعافى بأمان تام دون خصم العميل مرتين؟\n\n"
            "1. فهم طبيعة الفشل (The Distributed Systems Dilemma):\n   - أرسل العميل طلب `POST /orders/123/pay`.\n   - قام السيرفر بالخصم من بطاقة الائتمان وأصدر إيصالاً بنجاح.\n   - في نفس اللحظة، دخل الهاتف في نفق وانقطعت الشبكة، فاستقبل التطبيق `SocketTimeoutException`.\n   - **من منظور الهاتف**: النتيجة مجهولة (Unknown Outcome)، وليست فشلاً! السيرفر قد يكون خصم المبلغ بنجاح.\n   - **الخطأ الكارثي**: أن يعرض التطبيق رسالة 'فشلت العملية' ويطلب من المستخدم الضغط على زر 'ادفع الآن' مرة أخرى بمفتاح جديد، مما يؤدي إلى خصم المبلغ مرتين!\n\n"
            "2. بروتوكول التعافي الآمن (Safe Recovery Protocol):\n   - **المرحلة 1: توليد وحفظ Idempotency Key مسبقاً في Room**:\n     * قبل إرسال أول طلب للسيرفر، يتم حفظ المعاملة محلياً في Room بحالة `PAYMENT_PENDING` مع معرف فريد ثابت (UUID) ومفتاح تكرار محدد: `idempotencyKey = \"pay_ord_123\"`.\n   - **المرحلة 2: إظهار حالة غير مؤكدة للـ UI (Pending Reconciliation)**:\n     * عند وقوع مهلة الاتصال، لا تعرض 'فشل' ولا تعرض 'نجاح'؛ اعرض: 'جارِ التحقق من حالة الدفع مع البنك'.\n   - **المرحلة 3: استعلام استقصائي (Reconciliation Query)**:\n     * يتم إرسال طلب استعلام آمن `GET /orders/123/payment-status` مستخدماً نفس المفتاح.\n     * إذا وجد السيرفر المعاملة قد تمت، يعيد الإيصال ويتم تحديث الـ UI إلى `SUCCESS`.\n     * إذا لم يجد السيرفر أي أثر، يتم إلغاء المعاملة بأمان."
        ),
        "practical_walkthrough": (
            "تنفيذ بروتوكول استرداد الدفع المفقود باستخدام Idempotency Key والاستعلام الاستقصائي:\n"
            "```kotlin\n"
            "class PaymentRecoveryRepositoryImpl @Inject constructor(\n"
            "    private val paymentApi: PaymentApiService,\n"
            "    private val paymentDao: PaymentDao\n"
            ") : PaymentRepository {\n"
            "\n"
            "    override suspend fun executePayment(orderId: String, amountCents: Long): PaymentResult {\n"
            "        // 1. توليد وتثبيت مفتاح التكرار محلياً قبل أي اتصال شبكي:\n"
            "        val idempotencyKey = \"idemp_${orderId}_$amountCents\"\n"
            "        paymentDao.recordIntent(orderId, idempotencyKey, PaymentStatus.PENDING)\n"
            "\n"
            "        return try {\n"
            "            // 2. إرسال الطلب:\n"
            "            val receipt = paymentApi.chargeOrder(idempotencyKey, ChargeRequest(orderId, amountCents))\n"
            "            paymentDao.updateStatus(orderId, PaymentStatus.CONFIRMED, receipt.receiptUrl)\n"
            "            PaymentResult.Success(receipt)\n"
            "        } catch (e: IOException) {\n"
            "            // 3. انقطعت الشبكة بعد الإرسال! النتيجة غير مؤكدة:\n"
            "            reconcileLostPayment(orderId, idempotencyKey)\n"
            "        }\n"
            "    }\n"
            "\n"
            "    private suspend fun reconcileLostPayment(orderId: String, idempotencyKey: String): PaymentResult {\n"
            "        // استعلام استقصائي باستخدام نفس المفتاح:\n"
            "        return try {\n"
            "            val statusResponse = paymentApi.getPaymentStatus(orderId, idempotencyKey)\n"
            "            if (statusResponse.isPaid) {\n"
            "                paymentDao.updateStatus(orderId, PaymentStatus.CONFIRMED, statusResponse.receiptUrl)\n"
            "                PaymentResult.Success(statusResponse.toReceipt())\n"
            "            } else {\n"
            "                paymentDao.updateStatus(orderId, PaymentStatus.FAILED, null)\n"
            "                PaymentResult.Failed(\"Payment was not processed by server. Please try again.\")\n"
            "            }\n"
            "        } catch (e: Exception) {\n"
            "            // لا زالت الشبكة مقطوعة: نعرض حالة انتظار التحقق للـ UI:\n"
            "            PaymentResult.PendingVerification(orderId)\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Recover safely from lost payment responses by treating network drops on mutating requests as uncertain outcomes, never outright failures. Persist an Idempotency Key in Room prior to network dispatch. Upon timeout, query a dedicated status reconciliation endpoint using that key rather than issuing a fresh charge with a new ID.",
        "best_answer": (
            "In distributed mobile networking, a lost response after a mutating payment request represents an **Uncertain Outcome (the Two Generals' Problem)**. The server may have already committed the card charge. Retrying blindly or showing a failure screen causes double charges and furious customers.\n\n"
            "A production recovery architecture operates in three phases:\n\n"
            "1. **Pre-Flight Idempotency Persistence**: Prior to making the network call, persist the transaction intention in Room: `orderId`, `amount`, `status = PENDING`, and a deterministic `Idempotency-Key` (e.g. `UUID`).\n\n"
            "2. **State Transition to Uncertain UI**: If the call fails with `SocketTimeoutException` or `IOException`, do **NOT** show a 'Payment Failed - Tap to Retry' button. Update local state to `PaymentStatus.PENDING_VERIFICATION` and inform the user: 'Verifying payment with your bank...'.\n\n"
            "3. **Authoritative Reconciliation**: Query a dedicated reconciliation endpoint (`GET /orders/{id}/payment-status` or re-issue the `POST` with the *identical* Idempotency-Key). A compliant backend recognizes the key and returns the existing transaction status without charging again. If the server confirms payment, update local state to `SUCCESS`."
        ),
        "deep_answer": (
            "From an engineering telemetry and edge-case standpoint:\n\n"
            "1. **Background Polling via WorkManager**: If the user closes the app while in `PENDING_VERIFICATION`, schedule a constrained `PaymentReconciliationWorker` in WorkManager. When connectivity returns, the worker polls the backend, resolves the payment receipt, and triggers a local notification: 'Your order #123 is confirmed!'.\n\n"
            "2. **Backend Webhooks as Secondary Confirmation**: In robust payment flows (Stripe, Adyen, Apple Pay), mobile apps do not rely solely on client polling. The payment provider delivers an asynchronous server-to-server webhook directly to your backend. The backend updates the order status in the cloud database, which your app observes via WebSocket or a silent push notification upon relaunch."
        ),
        "follow_ups": [
            {
                "question": "What is the danger of generating a new Idempotency Key on retry?",
                "answer": "Generating a new key treats the retry as an entirely new transaction, causing the server to process a second independent charge."
            },
            {
                "question": "What HTTP status code should the server return on duplicate idempotent requests?",
                "answer": "HTTP 200 OK or 201 Created returning the original saved receipt, often accompanied by an `Idempotent-Replayed: true` header."
            }
        ]
    },
    {
        "id": "DAT-21",
        "arabic_explanation": (
            "تصميم نظام تغذية إخبارية مقسمة لصفحات (Paginated News Feed) تفتح فوراً في 5ms دون اتصال وتتزامن عند الاتصال بالإنترنت:\n\n"
            "1. المخطط المعماري الكامل (Architecture Blueprint):\n   - **قاعدة البيانات المحلية (Room) هي المصدر الوحيد للحقيقة (Single Source of Truth)**.\n   - **UI Layer (Jetpack Compose / LazyColumn)**: تجمع `Flow<PagingData<Article>>` من الـ ViewModel باستخدام `collectAsLazyPagingItems()`.\n   - **Presentation Model**: تعرض البيانات المخزنة فوراً من الـ SQLite Cache دون أي مؤشر انتظار أولي (Zero Initial Loading Spinner).\n   - **Data Layer (Paging 3 + RemoteMediator)**: يتولى `RemoteMediator` جلب الصفحات من السيرفر في الخلفية وكتابتها في Room.\n   - **مفاتيح التصفح (RemoteKeys Table)**: جدول في Room يخزن الصفحة التالية والسابقة لكل مقال لضمان عدم تكرار المقالات.\n\n"
            "2. تجربة المستخدم في وضع عدم الاتصال (Offline UX):\n   - عندما يفتح المستخدم التطبيق بدون إنترنت، تعرض الشاشة المقالات المخزنة فوراً، مع شريط علوي خفيف يفيد بأن التطبيق في وضع عدم الاتصال.\n   - عند عودة الإنترنت، يقوم `RemoteMediator` بجلب أحدث المقالات ودمجها بسلاسة دون التسبب في قفز الشاشة (No Scroll Jumping)."
        ),
        "practical_walkthrough": (
            "التطبيق البرمجي لنظام الأخبار الفوري باستخدام Room و Paging 3 و RemoteMediator:\n"
            "```kotlin\n"
            "// 1. إعداد الـ Repository لربط Room مع RemoteMediator:\n"
            "class NewsRepositoryImpl @Inject constructor(\n"
            "    private val database: AppDatabase,\n"
            "    private val newsApi: NewsApiService\n"
            ") : NewsRepository {\n"
            "\n"
            "    @OptIn(ExperimentalPagingApi::class)\n"
            "    override fun getNewsFeedStream(): Flow<PagingData<ArticleEntity>> {\n"
            "        return Pager(\n"
            "            config = PagingConfig(\n"
            "                pageSize = 20,\n"
            "                enablePlaceholders = false,\n"
            "                initialLoadSize = 20 // تحميل 20 عنصراً فقط لسرعة فائقة\n"
            "            ),\n"
            "            remoteMediator = NewsRemoteMediator(newsApi, database),\n"
            "            // القراءة تتم حصرياً من Room PagingSource:\n"
            "            pagingSourceFactory = { database.newsDao().observePagedArticles() }\n"
            "        ).flow\n"
            "    }\n"
            "}\n"
            "\n"
            "// 2. الـ ViewModel يعرض التدفق مباشرة مع التخزين المؤقت في viewModelScope:\n"
            "@HiltViewModel\n"
            "class NewsFeedViewModel @Inject constructor(\n"
            "    repository: NewsRepository\n"
            ") : ViewModel() {\n"
            "    val feedPagingData = repository.getNewsFeedStream().cachedIn(viewModelScope)\n"
            "}\n"
            "\n"
            "// 3. في Compose: فتح فوري في 5 ميلي ثانية من الكاش المحلي:\n"
            "@Composable\n"
            "fun NewsFeedScreen(viewModel: NewsFeedViewModel = hiltViewModel()) {\n"
            "    val articles = viewModel.feedPagingData.collectAsLazyPagingItems()\n"
            "\n"
            "    LazyColumn {\n"
            "        items(\n"
            "            count = articles.itemCount,\n"
            "            key = articles.itemKey { it.id } // مفاتيح ثابتة لمنع قفز الشاشة عند التحديث!\n"
            "        ) { index ->\n"
            "            articles[index]?.let { article -> ArticleCard(article) }\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Design an instant offline-first paginated feed by configuring Paging 3 with Room as the local source of truth via pagingSourceFactory and RemoteMediator as the network coordinator. UI renders local Room data instantly in 5ms, while RemoteMediator fetches remote pages in the background, updating Room transactionally without scroll jumps using stable item keys.",
        "best_answer": (
            "Designing an instant-opening, paginated feed that works seamlessly offline requires four integrated architectural pillars:\n\n"
            "1. **Room as the Single Source of Truth**: The UI collects `Flow<PagingData<T>>` served exclusively by Room's generated `PagingSource`. When the app launches, local SQLite records render onto the screen in under 5ms without displaying full-screen loading spinners.\n\n"
            "2. **Background Pagination Coordination (`RemoteMediator`)**: `RemoteMediator` intercepts scroll boundaries. When the user nears the bottom, it requests the next page from the API and writes the items and page cursors (`RemoteKeys`) into SQLite within a single `roomDatabase.withTransaction { }`.\n\n"
            "3. **Zero Scroll-Jumping UX**: In Jetpack Compose, pass stable item keys (`key = articles.itemKey { it.id }`). When fresh items are inserted into SQLite, Compose calculates precise diffs, maintaining the user's scroll position rather than snapping to the top.\n\n"
            "4. **Graceful Offline Degradation**: Network errors during background fetches are routed to `LoadState.Error`. The existing cached list remains fully interactive, and a subtle inline snackbar offers a 'Retry' action without blanking the screen."
        ),
        "deep_answer": (
            "To achieve true enterprise-grade performance with large feeds:\n\n"
            "1. **`InitializeAction.SKIP_INITIAL_REFRESH`**: In `RemoteMediator.initialize()`, inspect the timestamp of the last successful sync. If local data is less than 15 minutes old, return `SKIP_INITIAL_REFRESH`. This eliminates redundant API calls on frequent app launches, saving battery and server costs.\n\n"
            "2. **Cache Pruning and Database Compaction**: If an infinite feed appends hundreds of articles daily, the SQLite database will bloat over time. Implement an automated cleanup task in `RemoteMediator` on `REFRESH`: retain the most recent 200 articles and delete older items (`DELETE FROM articles WHERE id NOT IN (SELECT id FROM articles ORDER BY publishedAt DESC LIMIT 200)`)."
        ),
        "follow_ups": [
            {
                "question": "Why is `cachedIn(viewModelScope)` mandatory in Paging 3?",
                "answer": "It caches the PagingData stream across configuration changes (screen rotations), preventing the entire paging flow from resetting and reloading from scratch."
            },
            {
                "question": "What is the role of `enablePlaceholders = false` in PagingConfig?",
                "answer": "It prevents Room from projecting thousands of null placeholder items in the list before they are actually loaded from SQLite."
            }
        ]
    },
    {
        "id": "DAT-22",
        "arabic_explanation": (
            "كيف تهاجر قاعدة بيانات محلية غير مشفرة (Plaintext Database) إلى قاعدة بيانات مشفرة بالكامل (SQLCipher / Encrypted DB) دون فقدان أي بيانات؟\n\n"
            "1. مخاطر الهجرة الأمنية لقواعد البيانات:\n   - تحويل قاعدة بيانات SQLite العادية إلى مشفرة بـ SQLCipher ليس مجرد تغيير في كود الـ Schema؛ بل هو تشفير ثنائي كامل لجميع صفحات الـ SQLite على القرص.\n   - **المخاطر الكبرى**: نفاد مساحة الذاكرة على الهاتف (Disk Full)، انقطاع الكهرباء أو قتل الـ Process في منتصف التشفير، أو فقدان مفتاح التشفير من Android Keystore.\n\n"
            "2. البروتوكول الآمن خطوة بخطوة (Zero Data-Loss Encryption Protocol):\n   - **المرحلة 1: توليد وحفظ مفتاح التشفير بأمان**:\n     * توليد مفتاح عشوائي 256-bit وحفظه في الـ **Android Keystore System** لضمان عدم استخراجه.\n   - **المرحلة 2: إنشاء قاعدة بيانات مشفرة جديدة كملف منفصل (Safe Staging)**:\n     * لا تشفر الملف الأصلي في مكانه مباشرة!\n     * افتح قاعدة بيانات مشفرة جديدة باسم مؤقت (`app_encrypted.db`) باستخدام مكتبة SQLCipher ومفتاح الـ Keystore.\n   - **المرحلة 3: نسخ البيانات عبر أمر التشفير الأصلي في SQLCipher (`sqlcipher_export`)**:\n     * تنفيذ أمر `ATTACH DATABASE 'app_encrypted.db' AS encrypted KEY 'passphrase';` ثم `SELECT sqlcipher_export('encrypted');` ثم `DETACH DATABASE encrypted;`.\n     * هذا الأمر يقوم بنسخ جميع الجداول والبيانات والـ Indexes وتشفيرها بشكل ذري.\n   - **المرحلة 4: التحقق الصارم قبل حذف الملف الأصلي**:\n     * فتح قاعدة البيانات المشفرة والتأكد من تطابق عدد الصفوف (Row Counts).\n     * بعد التحقق بنسبة 100% فقط: حذف قاعدة البيانات القديمة غير المشفرة، وإعادة تسمية الملف المشفر إلى الاسم الرسمي."
        ),
        "practical_walkthrough": (
            "خطة ترحيل قاعدة بيانات غير مشفرة إلى مشفرة بأمان عبر SQLCipher:\n"
            "```kotlin\n"
            "class DatabaseEncryptionMigrator(private val context: Context) {\n"
            "\n"
            "    fun migratePlaintextToEncrypted(plaintextDbName: String, encryptedDbName: String, passphrase: ByteArray) {\n"
            "        val plaintextFile = context.getDatabasePath(plaintextDbName)\n"
            "        val encryptedFile = context.getDatabasePath(encryptedDbName)\n"
            "\n"
            "        // 1. إذا كان الملف الأصلي غير موجود، أو المشفر موجود ومكتمل -> لا داعي للهجرة:\n"
            "        if (!plaintextFile.exists() || encryptedFile.exists()) return\n"
            "\n"
            "        // 2. فتح قاعدة البيانات القديمة واستخدام sqlcipher_export لتصديرها مشفرة:\n"
            "        net.sqlcipher.database.SQLiteDatabase.loadLibs(context)\n"
            "        val rawDb = net.sqlcipher.database.SQLiteDatabase.openOrCreateDatabase(plaintextFile, \"\", null)\n"
            "\n"
            "        try {\n"
            "            // ربط القاعدة المشفرة الجديدة وتصدير البيانات بالكامل:\n"
            "            rawDb.rawExecSQL(\"ATTACH DATABASE '${encryptedFile.absolutePath}' AS encrypted KEY x'${passphrase.toHex()}';\")\n"
            "            rawDb.rawExecSQL(\"SELECT sqlcipher_export('encrypted');\")\n"
            "            rawDb.rawExecSQL(\"DETACH DATABASE encrypted;\")\n"
            "        } finally {\n"
            "            rawDb.close()\n"
            "        }\n"
            "\n"
            "        // 3. التحقق الحاسم من صحة التشفير قبل حذف القديم:\n"
            "        val testEncryptedDb = net.sqlcipher.database.SQLiteDatabase.openOrCreateDatabase(encryptedFile, passphrase, null)\n"
            "        val isVerified = testEncryptedDb.isOpen && testEncryptedDb.version >= 1\n"
            "        testEncryptedDb.close()\n"
            "\n"
            "        // 4. الحذف فقط بعد نجاح التحقق 100%:\n"
            "        if (isVerified) {\n"
            "            context.deleteDatabase(plaintextDbName)\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Migrate plaintext SQLite databases to SQLCipher encryption without data loss using staged export: generate a 256-bit master key in Android Keystore, attach a new encrypted database file, execute sqlcipher_export to copy all tables, verify row count integrity on the encrypted target, and delete the plaintext source only after verification succeeds.",
        "best_answer": (
            "Migrating an unencrypted database to SQLCipher encryption carries severe corruption risks if interrupted by crashes or power loss. A resilient enterprise migration follows a **Staged Export & Verify Protocol**:\n\n"
            "1. **Keystore Key Generation**: Generate a cryptographically secure 256-bit AES master key inside the hardware-backed **Android Keystore System** to protect the SQLCipher passphrase.\n\n"
            "2. **Staged Out-of-Place Export**: Never attempt in-place encryption. Open the existing plaintext SQLite database using SQLCipher and attach a fresh, separate destination file: `ATTACH DATABASE 'app_encrypted.db' AS encrypted KEY '<passphrase>'`.\n\n"
            "3. **Atomic SQLCipher Export**: Execute `SELECT sqlcipher_export('encrypted')` followed by `DETACH DATABASE encrypted`. This native SQLCipher engine routine copies all schemas, tables, triggers, and indices into the encrypted container with hardware-accelerated AES-256.\n\n"
            "4. **Integrity Verification**: Open the new encrypted database, execute `PRAGMA integrity_check`, and assert row count equivalence across critical tables.\n\n"
            "5. **Atomic Swap & Cleanup**: Only after verification passes, delete the plaintext database file (`context.deleteDatabase(plainDb)`). If anything fails prior to verification, abort and retain the unencrypted file."
        ),
        "deep_answer": (
            "Two catastrophic edge cases must be handled in production:\n\n"
            "1. **Insufficient Disk Space (`ENOSPC`)**: The `sqlcipher_export` operation duplicates the entire database on disk during export. If a user's database is 200MB and their device has only 100MB of free flash storage, the export fails midway with SQLite disk corruption. "
            "Pre-flight check: query `StatFs(context.filesDir.path).availableBytes`. Ensure free disk space is at least **$2.5 \\times$** the size of the unencrypted database before attempting the migration.\n\n"
            "2. **Process Death / Battery Loss Mid-Export**: If Android OS terminates the process halfway through export, `app_encrypted.db` exists in a corrupted, half-written state. "
            "On the next launch, the migrator must detect the partial file, delete the corrupted staging file, and re-run the migration safely from the pristine unencrypted original."
        ),
        "follow_ups": [
            {
                "question": "What does `PRAGMA integrity_check` do in SQLite?",
                "answer": "It scans the entire database file for out-of-order index records, missing B-tree pages, and malformed binary pointers, returning 'ok' if healthy."
            },
            {
                "question": "Can Room work directly with SQLCipher?",
                "answer": "Yes, by passing a `SupportFactory(passphrase)` from the SQLCipher library into Room's database builder via `openHelperFactory()`."
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

    for item in DAT_15_22:
        by_id[item["id"]] = item

    output = [by_id[k] for k in sorted(by_id.keys())]
    DATA_FILE.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {DATA_FILE} with questions DAT-15 to DAT-22. Total questions: {len(output)}")

if __name__ == "__main__":
    main()
