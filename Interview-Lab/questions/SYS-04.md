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

## Explanation in Arabic

في تصميم نظام Offline-First، القاعدة الذهبية إن قاعدة البيانات المحلية (Room) هي الـSingle Source of Truth الوحيد للـUI. شاشات التطبيق بتعمل observe لـ `Flow<List<T>>` جاية من Room مباشرة، ومفيش أي شاشة بتستنى رد الـNetwork عشان تعرض بيانات للمستخدم. لما المستخدم يعدل أو ينشئ عنصر جديد وهو أوفلاين، التعديل بيتكتب في جدول البيانات المحلي، وفي نفس الـDatabase Transaction بالظبط بنكتب سجل في جدول الـOutbox (`OutboxRecord`) بيحتوي على معرف عملية فريد ثابت (Idempotency Key)، الـpayload كـJSON، ورقم الـbase version. كتابة الـentity والـoutbox داخل atomic transaction بتضمن إن مستحيل يحصل تعديل محلي يضيع أو يتنسى لو التطبيق اتقفل أو النظام طفى فورًا بعد الحفظ.

## Practical walkthrough

بعد ما المعاملة تنجح محليًا، بنشغل WorkManager من خلال `ExistingWorkPolicy.KEEP` أو `APPEND_OR_REPLACE`. لما تتوفر شبكة مناسبة، الـ `SyncOutboxWorker` بيسحب العمليات المعلقة من جدول الـOutbox ويرسلها للسيرفر مصحوبة بـIdempotency-Key في الـheaders ورقم الإصدار. السيرفر لو استلم نفس الطلب مرتين بسبب ضعف الشبكة أو retry، مش هيكرر العملية لأنه مخزن الـkey. لو السيرفر اكتشف إن السجل اتعدل من جهاز تاني (Version Mismatch / HTTP 409 Conflict)، بيتم تطبيق سياسة فض النزاع المحددة للـdomain ده: إما دمج الحقول (3-way merge)، أو اعتبار السيرفر هو الفائز مع تنبيه المستخدم، أو حفظ نسخة conflicting copy. الـUI بتعرض بادج واضح "Pending Sync" أو "Conflict" عشان المستخدم يكون فاهم حالة بياناته بكل شفافية.

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

“I establish Room as the Single Source of Truth that UI observes via Flows. When the user makes an edit offline, I write the entity and an outbox mutation record containing a stable idempotency key within a single Room `@Transaction`. WorkManager then executes the sync with network constraints and exponential backoff. The backend reconciles versions to detect conflicts, and the UI displays pending or conflict states explicitly.”

## Interview answer — structured

“To build a robust offline-first architecture:
1. **Unidirectional Read Pipeline:** The UI strictly observes Room database entities mapped to UI models via Kotlin `StateFlow`. UI rendering never waits on network responses.
2. **Transactional Outbox Writes:** Offline actions write to both the target entity and a dedicated `sync_outbox` table inside a single SQLite transaction. This guarantees that crash during save cannot orphan an edit.
3. **Resilient Background Sync:** WorkManager schedules a `CoroutineWorker` requiring `NetworkType.CONNECTED`. It processes outbox records sequentially, applying exponential backoff on transient transport errors.
4. **Idempotency & Versioning:** Every mutation carries a UUID `operationId` and a `baseServerVersion`. The server uses the idempotency key to prevent double application of retries and returns HTTP 409 if another client changed the record first.
5. **Conflict Resolution & UX:** On conflict, the app either runs a deterministic field-merge or marks the record as `CONFLICT`, rendering an explicit resolution banner in the UI.”

## Interview answer — deep senior

“A senior architecture for offline-first systems solves three hard problems: write atomicity, duplicate prevention, and conflict semantics.

First, I guarantee local durability using the Outbox pattern. If a user creates or edits a note while disconnected, writing only the note entity leaves the background engine with no reliable mutation log. In my design, Room executes a single `@Transaction` that updates the entity with `localSyncState = PENDING_SYNC` and inserts an `OutboxRecord` containing the entity ID, payload JSON, timestamp, base server version, and a client-generated UUID `operationId`. If the process is killed at that exact millisecond, SQLite either rolls back both or commits both.

Second, for synchronization, I schedule WorkManager with `ExistingWorkPolicy.KEEP` and network constraints. When connectivity returns, the `SyncOutboxWorker` drains the outbox. Crucially, every HTTP request includes `Idempotency-Key: operationId`. In unreliable mobile networks, dropped connections often occur on the response path after the server has already executed the SQL write. When WorkManager retries, the backend detects the duplicate operation ID in Redis or PostgreSQL, skips re-executing business logic, and re-emits the original HTTP 200 result with the new server version.

Third, for concurrency, the server enforces optimistic locking via the `baseServerVersion`. If another client updated the record while this device was offline, the server returns HTTP 409 Conflict. In my architecture, conflict policy is domain-specific: for simple field updates, I apply a 3-way merge algorithm comparing base, remote, and local values; for irreconcilable documents, I fork the document locally, retain the user's draft, and surface an actionable resolution screen.

Finally, the UI models state explicitly: `NoteUiModel` exposes whether the item is `Synced`, `Syncing`, or `Conflicted`. This creates total user trust because the interface never misrepresents unacknowledged local state as confirmed remote truth.”

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

- [DAT-07](../dat-07/): What distinguishes offline-first from simple caching? **Answer:** Offline-first treats local storage as the primary read/write source of truth and syncs asynchronously; caching reads from network first and merely buffers responses.
- [SYS-06](../sys-06/): How do you combine Room with pagination and remote sync? **Answer:** Use Room `PagingSource` backed by `RemoteMediator` to coordinate remote page loading with local SQLite paging.

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

Technically reviewed against the cited primary documentation on 2026-10-13; this is an automated editorial and technical review, not a human review.
