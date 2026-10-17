---
id: "DAT-15"
question: "How do you sync local writes after offline edits?"
topic: "Networking, Room, DataStore & Offline-First"
code: "DAT"
group: "B"
phase: 3
priority: "P1"
order: 272
editorial_status: "reviewed"
---

# DAT-15

## Original interview question

How do you sync local writes after offline edits?

## What the interviewer evaluates

Persist offline edits and synchronize them safely after reconnect/process death.

## Concept and technical explanation

Synchronizing local offline mutations with remote backends requires implementing a durable, transactional outbox architecture:
- The Outbox Pattern (Local Mutation Queue):
  * Mutation Entity: Offline writes (create, update, delete) are committed immediately to the local database for instant UI feedback (optimistic updates), while a corresponding record is written atomically into a SyncMutationEntity table.
  * Schema Attributes: Stored mutations contain a unique client mutationId (UUID), entityType, entityId, operation (INSERT/UPDATE/DELETE), payload JSON, creation timestamp, and syncStatus (PENDING, IN_FLIGHT, FAILED).
- Durable Background Dispatch via WorkManager:
  * Constraints & Resilience: Synchronization is orchestrated by Jetpack WorkManager configured with NetworkType.CONNECTED. Because WorkManager schedules tasks in an internal SQLite database, pending edits survive app process termination, background OS memory reclaim, and full device reboots.
  * Causal Ordering (FIFO Execution): Mutations targeting the same entity must execute sequentially in strict chronological order to prevent out-of-order race conditions (e.g., executing a DELETE before an UPDATE completes).
- Two-Phase Reconciliation & Error Handling:
  * Upon successful backend ingestion, the server returns the canonical entity version or updated timestamp. The local client updates the domain entity and purges the mutation from the outbox in a single Room transaction.
  * If the server rejects the edit due to validation or schema conflicts, the client marks the mutation as FAILED and triggers conflict resolution policies.

## Practical walkthrough (English)

Transactional outbox pattern for offline writes and WorkManager synchronization:
```kotlin
// 1. Mutation Entity tracking pending offline operations
@Entity(tableName = "sync_mutations")
data class SyncMutationEntity(
    @PrimaryKey val mutationId: String = UUID.randomUUID().toString(),
    val entityType: String,
    val entityId: String,
    val action: String, // CREATE, UPDATE, DELETE
    val payloadJson: String,
    val createdAt: Long = System.currentTimeMillis()
)

// 2. Repository coordinates optimistic write and durable queueing atomically
class NoteRepositoryImpl(
    private val db: AppDatabase,
    private val workManager: WorkManager
) : NoteRepository {
    override suspend fun updateNote(id: String, newContent: String) = db.withTransaction {
        // Optimistic UI update
        db.noteDao().updateContent(id, newContent)

        // Queue durable mutation into outbox
        val mutation = SyncMutationEntity(
            entityType = "NOTE",
            entityId = id,
            action = "UPDATE",
            payloadJson = Json.encodeToString(NoteUpdatePayload(newContent))
        )
        db.syncDao().insertMutation(mutation)

        // Trigger guaranteed background sync
        val syncRequest = OneTimeWorkRequestBuilder<SyncWorker>()
            .setConstraints(Constraints.Builder().setRequiredNetworkType(NetworkType.CONNECTED).build())
            .build()
        workManager.enqueueUniqueWork("sync_outbox", ExistingWorkPolicy.KEEP, syncRequest)
    }
}
```

## Explanation in Arabic

كيف تزامن التعديلات المحلية (Local Writes) بعد انقطاع الاتصال في تطبيق Offline-First؟

1. دورة حياة العملية غير المتصلة (Offline Mutation Lifecycle):
   - **الخطوة 1: التسجيل المحلي الفوري في Room (Atomic Commit)**:
     * عند ضغط المستخدم على 'إرسال تعليق' أو 'تعديل ملف' وهو غير متصل، يتم حفظ التعديل في جدول البيانات الأساسي مع حالة `SYNC_PENDING`، ويتم إضافة سجل إلى جدول طابور المزامنة `sync_queue` يحتوي على: `operationId: UUID`, `actionType: EDIT`, `entityId`, `payloadJson`, `timestamp`.
     * يتم هذا داخل `database.withTransaction` لضمان عدم وجود تعديل بدون سجل في الطابور.
     * الـ UI تُحدّث فوراً ليشاهد المستخدم تعديله في 5ms.
   - **الخطوة 2: جدولة المزامنة المضمونة عبر WorkManager**:
     * يتم إطلاق `OneTimeWorkRequestBuilder<SyncWorker>()` مع شرط توفر الإنترنت `Constraints(NetworkType.CONNECTED)`.
     * يتميز WorkManager بأنه يضمن التنفيذ حتى لو أغلقت الشاشة، أو مات الـ Process، أو أعيد تشغيل الهاتف.
   - **الخطوة 3: التنفيذ المتسلسل والمعالجة (Execution & Acknowledgment)**:
     * يقرأ `SyncWorker` العمليات بالترتيب الزمني (FIFO).
     * يرسل العملية إلى السيرفر مرفقة بـ `idempotencyKey = operationId`.
     * عند استلام `200 OK`، يتم حذف السجل من طابور `sync_queue` وتحديث حالة الكيان في Room إلى `SYNCED`.

## Practical walkthrough

هيكل طابور المزامنة و SyncWorker لمعالجة التعديلات غير المتصلة:
```kotlin
// 1. كيان طابور المزامنة المحلي في Room:
@Entity(tableName = "sync_mutations_queue")
data class SyncMutationEntity(
    @PrimaryKey val operationId: String = UUID.randomUUID().toString(),
    val entityType: String,
    val entityId: String,
    val action: String, // CREATE, UPDATE, DELETE
    val payloadJson: String,
    val createdAt: Long = System.currentTimeMillis()
)

// 2. معالج المزامنة في WorkManager:
@HiltWorker
class OutboxSyncWorker @AssistedInject constructor(
    @Assisted appContext: Context,
    @Assisted workerParams: WorkerParameters,
    private val database: AppDatabase,
    private val syncApi: RemoteSyncApi
) : CoroutineWorker(appContext, workerParams) {

    override suspend fun doWork(): Result {
        val pendingMutations = database.syncDao().getOldestPendingMutations(limit = 20)
        
        for (mutation in pendingMutations) {
            try {
                // إرسال العملية مع Idempotency Key:
                syncApi.pushMutation(mutation.operationId, mutation.toRequest())
                // عند التأكيد، نحذفها من الطابور ونثبت الحالة:
                database.withTransaction {
                    database.syncDao().deleteMutation(mutation.operationId)
                    database.itemsDao().markSynced(mutation.entityId)
                }
            } catch (e: IOException) {
                // خطأ شبكة عابر: نطلب من WorkManager إعادة المحاولة بـ Exponential Backoff:
                return Result.retry()
            } catch (e: HttpException) {
                if (e.code() == 409) handleConflict(mutation) // معالجة النزاع
                else database.syncDao().markFailed(mutation.operationId, e.message)
            }
        }
        return Result.success()
    }
}
```

## Why it matters and how it works

Use an outbox table for durable operations. Distinguish local accepted, sending, acknowledged, conflicted and failed states. Server may apply writes out of order or reject stale versions; conflict resolution must preserve user intent. Work can be retried, so backend idempotency is required for side effects.

## Worked example

Conceptual DAO/repository; Room transaction annotation applies to local edit plus outbox row.

```kotlin
import androidx.room.Dao
import androidx.room.Insert
import androidx.room.Transaction

@Dao interface DraftDao {
    @Insert suspend fun saveDraft(draft: DraftEntity)
    @Insert suspend fun enqueue(op: PendingEditEntity)
    @Transaction suspend fun accept(draft: DraftEntity, op: PendingEditEntity) {
        saveDraft(draft); enqueue(op)
    }
}
```

## Trade-offs and decision criteria

Optimistic local UI feels immediate but can later conflict. Waiting for server avoids conflict UX but fails offline. Outbox adds schema/worker complexity and requires a visible pending state. Ordering rules depend on domain.

## Failure modes

Writing draft without outbox row loses sync intent after crash. Removing outbox row before server acknowledgement loses edits after timeout. Reusing an operation ID with different payload violates many idempotency contracts. Blind last-write-wins can erase another device’s change.

## Production perspective

A field inspection form commits edits locally, shows Pending badge, and syncs with WorkManager when connected. Server compares base version; conflict opens user review for text/attachments. Stuck pending age is monitored, and support can inspect operation IDs.

## Interview answer — short

Syncing offline writes requires the outbox pattern where mutations are saved in Room alongside optimistic UI updates in a single transaction. WorkManager monitors network availability to dispatch queued mutations sequentially in FIFO order, updating local database entities and pruning the outbox upon successful server confirmation.

## Interview answer — structured

Implementing offline write synchronization requires a resilient outbox architecture combined with durable background scheduling.
First, when a user edits data offline, we perform an optimistic write: the entity is updated immediately in Room for instant UI feedback, while an immutable mutation record is saved atomically in a local SyncMutation outbox table.
Second, we trigger background synchronization via Jetpack WorkManager with a CONNECTED network constraint. Because WorkManager persists work in SQLite, queued sync tasks survive process death and system reboots.
Third, the sync worker executes mutations in strict FIFO causal order. Once the server acknowledges the payload, Room updates the local entity with server timestamps and purges the mutation from the outbox in an atomic transaction.

## Interview answer — deep senior

In enterprise offline-first engineering, ensuring that user edits made in flight mode or underground subways sync durably without data loss is a core architectural requirement.
A common failure mode is firing coroutines directly inside the repository without local durability.
If the user edits three notes and immediately swipes the app away from recent tasks, in-memory coroutines are killed instantly by the Android runtime, permanently losing those edits.
To guarantee durability, we enforce the transactional Outbox Pattern.
When the user modifies an entity, we open a Room db.withTransaction block.
Within this single atomic transaction, we apply the optimistic write to our main entity table and simultaneously append a SyncMutation record into our persistent outbox table.
We then enqueue a unique WorkManager task with NetworkType.CONNECTED and exponential backoff policies.
Because WorkManager leverages an internal SQLite store, the task is immune to process termination and device reboots.
When network connectivity is established, our SyncWorker drains the outbox queue in strict First-In, First-Out (FIFO) chronological sequence.
Executing mutations sequentially per entity is critical: if an edit is followed by a delete, running them concurrently across threads could cause the delete to execute first, resulting in the edit reviving a deleted entity.
Upon successful HTTP 200 confirmation from the server, we remove the mutation from the outbox table and mark the local record as fully synchronized.

## How to answer in the interview

- **Why:** Offline edits need durable intent and cross-device consistency.
- **How:** Transactionally write note plus outbox, then worker sends by stable ID.
- **Trade-offs:** Optimistic UI requires pending/conflict visibility.
- **Failure cases:** Lost outbox row, duplicate send, old-account queue leak.
- **Production solution:** Version checks, reconciliation and crash-window tests.

## Deep-dive talking points

Draw outbox state transitions, crash windows and conflict resolution.

## Follow-up questions

- **Interviewer:** "Why shouldn't you run offline sync in a standard ViewModel coroutine?"
  **Answer:** "If the user closes the app or navigates away, the ViewModelScope is cancelled immediately, aborting the sync and leaving operations stranded until the screen is reopened."

- **Interviewer:** "What is 'Mutation Coalescing'?"
  **Answer:** "Combining multiple pending edits on the same record into a single network payload before uploading, saving cellular bandwidth and reducing API requests."

## Self-check rubric

Can I commit edit/outbox atomically, recover each crash window and reconcile duplicate sends?

## References and reviewed-on date

- [Android offline-first guidance](https://developer.android.com/topic/architecture/data-layer/offline-first) — queued writes and sync.
- [Android persistent work](https://developer.android.com/develop/background-work/background-tasks/persistent) — restartable scheduling.

Technically reviewed against primary documentation on 2026-10-13.
