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

Sync offline writes by committing the optimistic edit and an outbox queue record atomically to Room. Enqueue a WorkManager worker with a connected network constraint. When online, the worker processes outbox operations sequentially using idempotency keys, deleting queue records only upon verified server acknowledgment.

## Interview answer — structured

Synchronizing offline writes requires the **Outbox Pattern** backed by WorkManager to guarantee eventual consistency:

1. **Atomic Local Outbox Commit**:
   - When a user performs an offline edit, we do not simply mutate the UI state. We open a `roomDatabase.withTransaction { }`.
   - Inside the transaction, we write the optimistic entity state to Room (`status = PENDING_SYNC`) AND insert a mutation command record into an internal `sync_outbox` table (`operationId = UUID`, `payload`, `timestamp`). Both succeed or fail together.
   - The UI reflects the change in 5ms.

2. **Durable Sync Dispatcher (`WorkManager`)**:
   - Enqueue a unique WorkManager job (`ExistingWorkPolicy.APPEND_OR_REPLACE`) requiring `NetworkType.CONNECTED`.
   - WorkManager guarantees execution across app process death, phone reboots, and background constraints.

3. **Idempotent Sequential Processing**:
   - The worker drains the outbox in chronological order. Each HTTP call transmits `Idempotency-Key: <operationId>`.
   - Only upon receiving an explicit HTTP 200/201 response does the worker remove the mutation from the outbox and flip the entity status to `SYNCED` in SQLite.

## Interview answer — deep senior

Two severe failure modes occur in production offline sync engines:

1. **Out-of-Order Execution (The Chronological Bug)**:
   If a user edits an item offline and then deletes it 5 seconds later, firing two independent parallel network requests risks the Delete arriving *before* the Edit. The server executes Delete, then executes Edit, resurrecting the deleted item! To prevent this, the outbox processor must process mutations for the same `entityId` strictly sequentially (FIFO) or collapse intermediate states before syncing.

2. **The Zombie Pending Mutation (Process Kill during Sync)**:
   If the worker sends the mutation, the server commits it, but the cellular radio drops before the client receives the acknowledgment, the mutation remains in `sync_outbox`. When connectivity restores, the worker re-submits the mutation. Because the request carries the exact same `operationId` as its Idempotency Key, the backend recognizes it as a duplicate and acknowledges success without repeating side effects.

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
