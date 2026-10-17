---
id: "SYS-04"
question: "Design an offline-first system with a local source of truth."
topic: "Android System Design & Architecture Decisions"
code: "SYS"
group: "A"
phase: 4
priority: "P1"
order: 333
editorial_status: "reviewed"
---

# SYS-04

## Original interview question

Design an offline-first system with a local source of truth.

## What the interviewer evaluates

- Single Source of Truth (SSOT) architecture using Room database and reactive Flows.
- Outbox pattern for durable, crash-resilient mutations without data loss.
- Guaranteed background synchronization using WorkManager with network constraints and exponential backoff.
- Server idempotency keys and version-based conflict resolution strategies (e.g., ETags, vector clocks, or domain-specific merging).
- Clear UI state modeling distinguishing between locally saved, syncing, confirmed, and conflicted states.

## Concept and technical explanation

An offline-first mobile architecture treats local persistence (typically a Room SQLite database) as the single source of truth (SSOT) and the remote network as an asynchronous synchronization mechanism. The UI layer never observes network responses directly; instead, it observes reactive database queries via Kotlin Flow or PagingData, ensuring immediate rendering and zero offline latency. When a user creates or modifies content, changes are applied optimistically to local tables alongside an atomic insertion into a durable Outbox table containing mutation payloads and client-generated idempotency keys. Background synchronization engines, implemented with WorkManager and exponential backoff, drain the Outbox table when connectivity is restored, transmitting payloads to the backend and reconciling state seamlessly.

## Practical walkthrough (English)

Implementing an offline-first repository with Room Single Source of Truth and the Outbox Pattern:
```kotlin
// 1. Database entities: Main content and durable mutation Outbox
@Entity(tableName = "notes")
data class NoteEntity(
    @PrimaryKey val id: String,
    val title: String,
    val content: String,
    val syncStatus: SyncStatus,
    val updatedAtMs: Long
)

enum class SyncStatus { SYNCED, PENDING_SYNC, FAILED }

@Entity(tableName = "sync_outbox")
data class OutboxEntity(
    @PrimaryKey val mutationId: String, // Client-generated UUID idempotency key
    val entityId: String,
    val payloadJson: String,
    val mutationType: String, // INSERT, UPDATE, DELETE
    val createdAtMs: Long
)

// 2. Offline-First Repository executing optimistic updates inside an atomic transaction
class NoteRepositoryImpl @Inject constructor(
    private val database: AppDatabase,
    private val noteDao: NoteDao,
    private val outboxDao: OutboxDao,
    private val workManager: WorkManager
) : NoteRepository {

    // Single source of truth streaming from Room to UI
    override fun getNotesStream(): Flow<List<Note>> =
        noteDao.getAllNotesFlow().map { list -> list.map { it.toDomain() } }

    override suspend fun updateNote(id: String, newContent: String): Result<Unit> = runCatching {
        val now = System.currentTimeMillis()
        val mutationId = UUID.randomUUID().toString()

        database.withTransaction {
            // Optimistic update of local entity
            noteDao.updateContent(id = id, content = newContent, status = SyncStatus.PENDING_SYNC, timestamp = now)
            
            // Durable record in outbox table
            outboxDao.insert(
                OutboxEntity(
                    mutationId = mutationId,
                    entityId = id,
                    payloadJson = "{"content":"$newContent"}",
                    mutationType = "UPDATE",
                    createdAtMs = now
                )
            )
        }

        // Trigger WorkManager synchronization with network constraints
        val syncRequest = OneTimeWorkRequestBuilder<SyncOutboxWorker>()
            .setConstraints(Constraints.Builder().setRequiredNetworkType(NetworkType.CONNECTED).build())
            .build()
        workManager.enqueueUniqueWork("SYNC_OUTBOX", ExistingWorkPolicy.KEEP, syncRequest)
    }
}
```

## Explanation in Arabic

كيف تصمم نظام Offline-First مع مصدر حقيقة محلي (Single Source of Truth) يضمن تجربة مستخدم سلسة بدون فقدان للبيانات؟

1. المبدأ المعماري لـ Offline-First:
   - **قاعدة البيانات المحلية (Local Room DB) هي مصدر الحقيقة الوحيد (Single Source of Truth - SSOT)**.
   - واجهة المستخدم (UI) لا تطلب البيانات من الشبكة مباشرة أبداً؛ بل تستمع (Observe) لـ `Flow<List<Item>>` صادر من قاعدة البيانات المحلية دائماً.
   - عمليات التحديث والإنشاء تُكتب أولاً في قاعدة البيانات المحلية، مما يجعل استجابة الـ UI فورية (Optimistic Updates).

2. محرك المزامنة (Synchronization Engine & Outbox Pattern):
   - **Outbox Pattern للعمليات المعلقة**: عند قيام المستخدم بإجراء (مثل كتابة تعليق أو إرسال رسالة) أثناء انقطاع الإنترنت:
     * يُحفظ الكائن في جدول الـ DB المحلي مع حالة مزامنة: `SYNC_STATUS = PENDING` ومُعرّف محلي مؤقت (`client_id = UUID()`).
     * يُعرض العنصر فوراً في الـ UI مع أيقونة ساعة صغيرة (Pending).
     * تضاف المهمة إلى جدول طابور المزامنة `sync_actions_queue`.
   - **المزامنة في الخلفية عبر WorkManager**: يقوم `WorkManager` بمراقبة اتصال الشبكة (`NetworkType.CONNECTED`) وتنفيذ المهام المعلقة بالترتيب، وإرسالها للسيرفر، ثم تحديث الـ ID المحلي بمعرف السيرفر وتغيير الحالة إلى `SYNC_STATUS = SYNCED`.

3. فض النزاعات (Conflict Resolution Strategies):
   - **Last-Write-Wins (LWW) عبر Timestamps**: الحل الأبسط ولكن قد يفقد بيانات إذا لم تكن الساعات متزامنة.
   - **Vector Clocks / Version Numbers**: السيرفر يرفض التعديل إذا كان رقم الإصدار قديماً ويطلب من العميل دمج البيانات (Merge).
   - **CRDTs (Conflict-free Replicated Data Types)**: للبيانات التشاركية المعقدة (مثل المستندات النصية المشتركة).

## Practical walkthrough

تنفيذ نمط الـ Outbox المحلي مع Room وتحديثات الواجهة الفورية (Optimistic UI) وإعادة المحاولة:
```kotlin
// 1. كيان قاعدة البيانات يمثل مصدر الحقيقة مع حالة المزامنة:
@Entity(tableName = "notes")
data class NoteEntity(
@PrimaryKey val localId: String = UUID.randomUUID().toString(),
    val remoteId: String? = null,
    val content: String,
    val syncStatus: SyncStatus = SyncStatus.PENDING,
    val updatedAt: Long = System.currentTimeMillis()
)

enum class SyncStatus { SYNCED, PENDING, FAILED }

// 2. مستودع يضمن التحديث الفوري المحلي وتفويض المزامنة للـ WorkManager:
class OfflineFirstNoteRepository @Inject constructor(
    private val noteDao: NoteDao,
    private val workManager: WorkManager
) {
    // الـ UI يستمع لقاعدة البيانات فقط
    val allNotes: Flow<List<Note>> = noteDao.observeNotes().map { entities -> entities.map { it.toDomain() } }

    suspend fun saveNote(content: String) {
        // 1. حفظ فوري في قاعدة البيانات المحلية (Optimistic Write)
        val newNote = NoteEntity(content = content, syncStatus = SyncStatus.PENDING)
        noteDao.insert(newNote)

        // 2. جدولة مزامنة عبر WorkManager بشرط توفر شبكة إنترنت
        val constraints = Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .build()

        val syncRequest = OneTimeWorkRequestBuilder<SyncNotesWorker>()
            .setConstraints(constraints)
            .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 10, TimeUnit.SECONDS)
            .build()

        workManager.enqueueUniqueWork("sync_notes_work", ExistingWorkPolicy.APPEND_OR_REPLACE, syncRequest)
    }
}
```

## Why it matters and how it works

In an offline-first architecture, network is treated as an asynchronous synchronization mechanism rather than an availability dependency. The architecture establishes strict operational boundaries:
1. **Read Path:** The UI layer strictly observes Room database queries through Kotlin `Flow`. The UI remains instantaneous and fully functional in airplane mode.
2. **Write Path (Transactional Outbox):** When a user triggers an action (create, update, delete), the repository writes both the updated local domain entity and a corresponding `OutboxRecord` within a single Room `@Transaction`. This guarantees atomicity: neither write can exist without the other.
3. **Execution Path (WorkManager):** An exponential-backoff, constraint-gated `CoroutineWorker` queries pending outbox records and dispatches them to the remote API.
4. **Idempotency & Reconciliation:** Every outbox record maintains an immutable `clientOperationId`. If the network drops after the server processes the write but before the client receives the HTTP 200 ACK, the subsequent retry carries the same idempotency key, preventing duplicate mutations.

## Worked example

Here is a complete, production-ready implementation of the offline-first Outbox pattern combining Room transactions and WorkManager:

```kotlin
import androidx.room.*
import kotlinx.coroutines.flow.Flow
import java.util.UUID

enum class SyncState { SYNCED, PENDING_SYNC, CONFLICT }
enum class OutboxAction { UPSERT, DELETE }

@Entity(tableName = "notes")
data class NoteEntity(
    @PrimaryKey val id: String,
    val title: String,
    val content: String,
    val serverVersion: Long,
    val localSyncState: SyncState = SyncState.SYNCED,
    val updatedAtMillis: Long = System.currentTimeMillis()
)

@Entity(tableName = "sync_outbox")
data class OutboxRecord(
    @PrimaryKey val operationId: String = UUID.randomUUID().toString(),
    val entityId: String,
    val action: OutboxAction,
    val payloadJson: String,
    val baseServerVersion: Long,
    val createdAtMillis: Long = System.currentTimeMillis(),
    val retryCount: Int = 0
)

@Dao
interface OfflineFirstNotesDao {
    @Query("SELECT * FROM notes ORDER BY updatedAtMillis DESC")
    fun observeNotes(): Flow<List<NoteEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsertNote(note: NoteEntity)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertOutbox(record: OutboxRecord)

    @Query("SELECT * FROM sync_outbox ORDER BY createdAtMillis ASC")
    suspend fun getPendingOutbox(): List<OutboxRecord>

    @Query("DELETE FROM sync_outbox WHERE operationId = :operationId")
    suspend fun deleteOutbox(operationId: String)

    @Transaction
    suspend fun saveNoteOffline(note: NoteEntity, outbox: OutboxRecord) {
        upsertNote(note.copy(localSyncState = SyncState.PENDING_SYNC))
        insertOutbox(outbox)
    }

    @Transaction
    suspend fun applyServerSyncSuccess(noteId: String, newVersion: Long, operationId: String) {
        deleteOutbox(operationId)
        // Mark note as cleanly synced with authoritative server version
        val current = getNoteById(noteId)
        if (current != null && current.localSyncState == SyncState.PENDING_SYNC) {
            upsertNote(current.copy(serverVersion = newVersion, localSyncState = SyncState.SYNCED))
        }
    }

    @Query("SELECT * FROM notes WHERE id = :id")
    suspend fun getNoteById(id: String): NoteEntity?
}
```

```kotlin
import android.content.Context
import androidx.work.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class SyncOutboxWorker(
    appContext: Context,
    workerParams: WorkerParameters,
    private val dao: OfflineFirstNotesDao,
    private val api: NotesRemoteApi
) : CoroutineWorker(appContext, workerParams) {

    override suspend fun doWork(): Result = withContext(Dispatchers.IO) {
        val pending = dao.getPendingOutbox()
        if (pending.isEmpty()) return@withContext Result.success()

        for (record in pending) {
            try {
                val response = api.syncMutation(
                    idempotencyKey = record.operationId,
                    entityId = record.entityId,
                    action = record.action.name,
                    baseVersion = record.baseServerVersion,
                    payload = record.payloadJson
                )

                when {
                    response.isSuccess -> {
                        dao.applyServerSyncSuccess(
                            noteId = record.entityId,
                            newVersion = response.committedVersion,
                            operationId = record.operationId
                        )
                    }
                    response.isConflict -> {
                        // Mark entity as conflicted for manual or algorithmic resolution
                        val current = dao.getNoteById(record.entityId)
                        if (current != null) {
                            dao.upsertNote(current.copy(localSyncState = SyncState.CONFLICT))
                        }
                        dao.deleteOutbox(record.operationId)
                    }
                    response.isRetryable -> return@withContext Result.retry()
                }
            } catch (e: Exception) {
                return@withContext Result.retry()
            }
        }
        Result.success()
    }
}
```

## Trade-offs and decision criteria

1. **Local Outbox vs Direct In-Flight Network Retries:**
   - In-flight retries inside a ViewModel or repository coroutine are lost as soon as the user exits the app or process death occurs.
   - The Outbox pattern persists mutations in SQLite, surviving app process death, OS reboots, and multi-day offline periods. The trade-off is database schema overhead and JSON serialization cost.

2. **Conflict Resolution Strategy:**
   - **Last-Write-Wins (LWW):** Simplest to implement, but causes silent data loss if two devices update the same note offline.
   - **Field-level 3-way Merge:** Merges non-conflicting fields automatically using base version, server version, and local version. Suitable for structured forms and profile data.
   - **User-Facing Conflict Prompt:** Preserves both copies (e.g., creates "My Note (Conflicted Copy)") and lets the user resolve discrepancies. Mandatory for sensitive documents or financial notes.

3. **Background Scheduling Constraints:**
   - WorkManager guarantees eventual execution with `NetworkType.CONNECTED`. For high-priority changes, attempt an immediate coroutine network dispatch; if it fails or the app is killed, WorkManager serves as the durable safety net.

## Failure modes

- **Non-Atomic Local Mutation:** Inserting the updated entity without writing the outbox in the same Room transaction creates a state where the local database displays the edit, but the sync engine never transmits it. Always wrap in `@Transaction`.
- **Missing Idempotency Key:** If an HTTP request times out after the backend commits the record, a naive retry generates duplicate server records. The `operationId` generated on the client must be preserved across retries and passed in the `Idempotency-Key` HTTP header.
- **Overwriting New Remote Changes on Refresh:** A background sync pulling server changes must never blindly overwrite rows where `localSyncState == PENDING_SYNC`. Remote delta merges must inspect dirty local flags or maintain separate sync shadow tables.
- **Unbounded Outbox Growth:** If a server-side validation error (e.g. HTTP 422 Unprocessable Entity) causes infinite retries, the worker will be stuck forever. Records must have a maximum retry threshold or explicit dead-letter queue.

## Production perspective

In high-scale production apps (e.g., Salesforce, Notion, or field logistics apps):
- Enforce periodic compaction: prune acknowledged outbox records and vacuum the SQLite database.
- Use `ExpeditedWorkRequest` or foreground notifications when syncing critical data that the user expects to finish immediately before app backgrounding.
- Implement exponential backoff with jitter on `Result.retry()` to prevent the thundering herd problem when connectivity is restored to thousands of devices simultaneously.
- Surface explicit sync status in the top bar (e.g. green checkmark for Synced, rotating indicator for Syncing, warning banner for Offline with pending count).

## Interview answer — short

We build offline-first systems by making a local Room database the single source of truth that UI components observe via reactive Flows. When users create or edit data, we write optimistically to the database and record mutations in a durable Outbox table inside an atomic transaction. WorkManager processes queued outbox records with exponential backoff and network constraints, guaranteeing eventual consistency and complete offline usability.

## Interview answer — structured

In an offline-first architecture, local persistence is the authoritative source of truth for the presentation layer, while the network functions as an asynchronous data pipeline.
When the UI loads, it subscribes to reactive database streams using Kotlin Flow.
All reads come directly from disk, delivering instantaneous screen rendering with zero network latency.
When a user creates or modifies content offline, we execute an optimistic local update.
Within a single atomic SQLite transaction, we update the local entity state and insert an entry into a durable Sync Outbox table with a unique idempotency key and pending status.
This guarantees that user intent is never lost, even if the application process dies immediately.
A dedicated background synchronization engine managed by WorkManager monitors network connectivity.
When a connection is established, the sync worker transmits pending outbox payloads in sequence.
Upon server acknowledgment, the outbox record is purged, and the local entity is marked as synchronized.
If conflicts arise, version timestamps or server-authoritative reconciliation strategies resolve differences, streaming the merged state directly to the UI.

## Interview answer — deep senior

The engineering complexity of offline-first architectures centers on conflict resolution, mutation ordering, and database transaction boundaries.
A naive approach performs network calls first and updates the database upon success; under flaky connectivity, this creates dropped mutations and inconsistent UI state.
By adopting the Outbox pattern with atomic transactions, we decouple user interaction from network availability.
When persisting local mutations, we generate a client-side UUID and an idempotency token.
If the device experiences intermittent connectivity or sudden process termination, WorkManager automatically resumes the sync worker with exponential backoff.
Because the server enforces idempotency via the client token, duplicate deliveries caused by lost HTTP response packets do not create duplicate records on the backend.
For conflict resolution, we choose between Last-Write-Wins based on synchronized server timestamps, field-level merging, or three-way merge vectors depending on domain criticality.
In financial or collaborative domains, server-authoritative rejection is handled by rolling back the optimistic entity in Room and surfacing a non-blocking resolution banner to the user.
Furthermore, Room's InvalidationTracker detects table changes and pushes fresh queries through Flow pipelines to Compose UI without manual refresh logic, achieving seamless consistency across online and offline states.
Underneath SQLite, we enable Write-Ahead Logging to decouple background outbox writes from foreground UI queries, preventing database lock contention.
Additionally, we handle device storage limits by catching SQLiteFullException and applying automated pruning to non-essential cached media, ensuring core mutation records always persist.

## How to answer in the interview

- **Why:** Mobile devices experience unpredictable network drops; users require responsive local writes that survive process death.
- **How:** Room as SSOT observed via Flows; atomic Room transactions writing entity + outbox; WorkManager background synchronization; server idempotency keys.
- **Trade-off:** High complexity in conflict resolution, database migrations, and sync state management versus naive direct-network calls.
- **Failure case:** Writing local edits without an outbox table causes mutations to be forgotten after OS termination; retries without idempotency cause duplicate remote operations.
- **Production solution:** Enforce SQLite `@Transaction`, attach client UUIDs as idempotency headers, implement optimistic locking, and expose sync status to UI.

## Deep-dive talking points

- **Room Reactive Queries:** How Room registers SQLite table invalidation trackers to re-emit new lists on `Flow` whenever tables are modified.
- **WorkManager ExistingWorkPolicy:** Preventing redundant duplicate worker executions when multiple offline edits occur in rapid succession.
- **Optimistic Locking:** Using version numbers or ETags to detect concurrent multi-client updates.
- **Idempotency Window:** How servers cache idempotency keys (e.g. in Redis with 24h TTL) to de-duplicate network retries.

## Follow-up questions

- **Interviewer:** "What is a tombstone in database synchronization?"
  **Answer:** "A record marked with a deletion flag rather than being physically dropped, allowing synchronization engines to propagate the delete operation to remote servers."

- **Interviewer:** "Why should local database IDs be client-generated UUIDs rather than auto-incrementing integers?"
  **Answer:** "Client-generated UUIDs prevent ID collisions across distributed offline devices before entities are assigned authoritative server IDs."

## Self-check rubric

- Can I explain why Room must be the Single Source of Truth for the UI?
- Can I write a Room `@Transaction` combining entity update and outbox insertion?
- Can I explain the role of client-generated idempotency keys during WorkManager retries?
- Can I contrast Last-Write-Wins against 3-way merging and user-prompted conflict resolution?
- Can I describe how the UI distinguishes between locally saved and server-acknowledged state?

## References and reviewed-on date

- [Android offline-first architecture guidance](https://developer.android.com/topic/architecture/data-layer/offline-first) — official data layer patterns.
- [WorkManager background processing](https://developer.android.com/develop/background-work/background-tasks/persistent) — scheduled persistent jobs.
- [Room database transactions](https://developer.android.com/training/data-storage/room) — data access objects and transactions.

Technically reviewed against primary documentation on 2026-10-13.
