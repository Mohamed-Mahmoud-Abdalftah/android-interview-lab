---
id: "DAT-16"
question: "How should conflicts be resolved when local and server state diverge?"
topic: "Networking, Room, DataStore & Offline-First"
code: "DAT"
group: "B"
phase: 3
priority: "P1"
order: 273
editorial_status: "reviewed"
---

# DAT-16

## Original interview question

How should conflicts be resolved when local and server state diverge?

## What the interviewer evaluates

Resolve divergent local/server state using versions, domain merge and conflict UX.

## Concept and technical explanation

Resolving data divergence between local offline storage and remote servers requires structured conflict resolution models:
- Last-Write-Wins (LWW): Resolves conflicts based on mutation timestamps. Simple to implement, but vulnerable to mobile clock drift, timezone shifts, and network latency anomalies, often silently overwriting newer legitimate user changes.
- Server-Wins vs Client-Wins: Strict authoritative boundaries. Server-Wins prioritizes enterprise state consistency, discarding local offline edits upon conflicts. Client-Wins prioritizes user autonomy, allowing local device changes to overwrite remote state unconditionally (common in personal note-taking or local settings).
- Field-Level Three-Way Merging: Compares the base ancestor snapshot, the local mutation, and the server payload. Non-intersecting property edits merge automatically without conflict.
- Conflict-Free Replicated Data Types (CRDTs): Mathematical data structures (such as Observed-Remove Sets or State-based LWW-Element-Sets) that guarantee deterministic mathematical convergence across concurrent distributed edits without requiring centralized coordination locks.
- Interactive User Resolution: Presents a conflict resolution modal when critical irreversible collisions occur, empowering the user to inspect differences and select the winning version.

## Practical walkthrough (English)

Offline sync engine with optimistic updates and revision-based conflict handling:
```kotlin
data class SyncEntity(
    val id: String,
    val title: String,
    val revision: Long,
    val isPendingSync: Boolean = false
)

class SyncRepository(
    private val dao: SyncDao,
    private val api: SyncApi
) {
    // 1. Optimistic local update
    suspend fun updateTitleLocally(id: String, newTitle: String) {
        dao.updateOptimistically(id = id, title = newTitle, isPending = true)
    }

    // 2. Sync with server revision validation
    suspend fun syncItem(id: String): Result<Unit> = runCatching {
        val local = dao.getItem(id) ?: return@runCatching
        try {
            val updated = api.pushUpdate(local.id, local.title, local.revision)
            dao.saveSynced(updated.copy(isPendingSync = false))
        } catch (e: HttpException) {
            if (e.code() == 409) {
                // Conflict detected: fetch remote and perform field-level merge
                val remote = api.fetchItem(id)
                val resolved = resolveConflict(base = local, remote = remote)
                dao.saveSynced(resolved)
            } else throw e
        }
    }

    private fun resolveConflict(base: SyncEntity, remote: SyncEntity): SyncEntity {
        // Business rule: Keep local edits if marked pending, update revision counter
        return remote.copy(title = base.title, isPendingSync = true)
    }
}
```

## Explanation in Arabic

كيف يتم حل النزاعات وتعارض البيانات (Conflict Resolution) عندما تختلف الحالة المحلية (Local State) عن حالة السيرفر (Server State)؟

1. أسباب النزاع في بيئة الـ Offline-First:
   - قام المستخدم بتعديل ملف أو مهمة على الهاتف وهو في الطائرة.
   - في نفس الوقت، قام زميله في العمل بتعديل نفس الملف من متصفح الويب على السيرفر.
   - عندما يعود هاتف المستخدم للإنترنت، تصبح هناك نسختان متعارضتان من الحقيقة لنفس المعرف (`EntityId`).

2. الاستراتيجيات المعمارية لحل النزاعات (Conflict Resolution Strategies):
   - **Last-Write-Wins (LWW - التعديل الأحدث يفوز)**:
     * اعتماد النسخة ذات الـ Timestamp الأحدث.
     * **تحذير**: كارثي في كثير من الحالات لأن ساعات الهواتف غير مضبوطة (Clock Drift)، مما قد يمسح بيانات مهمة دون علم المستخدم.
   - **Server-Wins (السيرفر هو الحاكم الأخير)**:
     * مناسب للبيانات السلطوية (الأسعار، المخزون، الحالات البنكية). السيرفر يرفض التعديل بـ `409 Conflict`، ويجبر العميل على تحديث نسخته المحلية.
   - **Client-Wins (العميل يفوز)**:
     * للمسودات الشخصية والملاحظات الخاصة التي لا يتشاركها عدة مستخدمين.
   - **3-Way Merging (الدمج الذكي للحقول)**:
     * مقارنة النسخة المشتركة القديمة (Base Version) والنسخة المحلية والنسخة البعيدة. إذا عدل العميل رقم الهاتف وعدل السيرفر العنوان، يتم دمج الحقلين معاً بنجاح.
   - **Manual User Resolution (تدخل المستخدم)**:
     * عرض شاشة للمستخدم بمقارنة جنباً إلى جنب (Side-by-Side Diff) ليختار النسخة التي يريد الاحتفاظ بها (مثل Google Keep أو Git Merge Conflict).

## Practical walkthrough

تنفيذ معالجة النزاع عبر Optimistic Locking باستخدام Version Vectors / ETag:
```kotlin
data class NoteSyncDto(
    val id: String,
    val content: String,
    val baseVersion: Long // رقم الإصدار الذي كان لدى العميل عند بدء التعديل
)

class NoteRepositoryImpl @Inject constructor(
    private val noteDao: NoteDao,
    private val noteApi: NoteApiService
) : NoteRepository {

    suspend fun syncNote(noteId: String) {
        val localNote = noteDao.getNoteById(noteId) ?: return
        
        try {
            val response = noteApi.updateNote(
                id = noteId,
                dto = NoteSyncDto(localNote.id, localNote.content, localNote.version)
            )
            // نجاح: تحديث الإصدار الجديد من السيرفر:
            noteDao.update(localNote.copy(version = response.newVersion, syncStatus = SYNCED))
        } catch (e: HttpException) {
            if (e.code() == 409) {
                // تعارض حقيقي: السيرفر يحمل إصداراً أحدث!
                val serverNote = noteApi.fetchLatestNote(noteId)
                
                // حفظ النزاع في Room وعرض إشعار للمستخدم:
                noteDao.recordConflict(
                    noteId = noteId,
                    localContent = localNote.content,
                    serverContent = serverNote.content
                )
            }
        }
    }
}
```

## Why it matters and how it works

Conflict detection requires a common base or version vector/ETag; timestamps from device clocks are unreliable as sole authority. A three-way merge compares base, local and remote changes. Preserve both versions until resolution to avoid data loss. Server remains final arbiter for shared invariants.

## Worked example

Conceptual Kotlin conflict model; merge implementation is domain-specific and should not silently discard either side.

```kotlin
data class VersionedNote(val text: String, val version: String)
sealed interface MergeDecision {
    data class Merged(val text: String) : MergeDecision
    data class NeedsUser(val local: String, val remote: String) : MergeDecision
}
fun decide(base: VersionedNote, local: String, remote: VersionedNote): MergeDecision =
    if (remote.version == base.version) MergeDecision.Merged(local)
    else MergeDecision.NeedsUser(local, remote.text)
```

## Trade-offs and decision criteria

Server-wins is simple but can lose offline user work; client-wins can overwrite others. Field-level merge is useful only when fields are independent; CRDTs add complexity and suit specific collaborative domains. User review preserves intent but costs UX.

## Failure modes

Using wall-clock last-write-wins across devices can choose the wrong update due to skew. Retrying stale write without version precondition can erase remote changes. Deleting local pending data on 409 destroys recovery context.

## Production perspective

A notes app stores base/local/remote versions and offers merge review when both edited text. A bank balance never client-merges; it refreshes authoritative server ledger and reconciles pending operations.

## Interview answer — short

Resolving conflicts when local and server state diverge depends on data criticalness. Systems employ Last-Write-Wins based on synchronized server timestamps, field-level three-way merging for independent attributes, or Conflict-Free Replicated Data Types for collaborative items. The client uses an outbox queue with optimistic local updates and presents interactive resolution modals for irreversible collisions.

## Interview answer — structured

Resolving divergence between local and server state requires establishing clear architectural ownership and deterministic merge rules.
First, Last-Write-Wins resolves conflicts by comparing update timestamps. While simple, it risks data loss if client device clocks drift, making server-assigned timestamps or monotonic revision counters preferable.
Second, field-level three-way merging compares the base snapshot, the local mutation, and the remote update. Non-overlapping field edits merge automatically, whereas conflicting changes on identical fields fall back to business rules or user selection modals.
Third, collaborative data structures leverage Conflict-Free Replicated Data Types to converge concurrently without central synchronization locks.
In Android offline architectures, we enforce an Outbox pattern where mutations are saved locally with pending sync flags, processed sequentially via WorkManager, and reconciled against server responses.

## Interview answer — deep senior

In enterprise offline-first Android systems, conflict resolution cannot be treated as an afterthought; naive approaches like blindly overwriting server data with local state lead to severe data corruption and lost user work.
When designing sync engines, we classify data into distinct consistency tiers.
For basic settings or ephemeral preferences, Client-Wins or Last-Write-Wins with server-assigned monotonic sequence numbers is acceptable.
However, for collaborative documents, shopping carts, or enterprise task lists, Last-Write-Wins silently destroys data because mobile device clocks frequently skew across timezones and hardware differences.
To solve this, we implement a robust Outbox pattern backed by Room.
When a user edits an item offline, we immediately apply an optimistic update to the local database to preserve instantaneous UI feedback, while inserting a pending mutation task into our sync queue.
Each entity carries a revision hash or version vector.
When connectivity returns, WorkManager dispatches the mutation to the backend.
If the server's current revision does not match the client's base revision, the server rejects the write with HTTP 409 Conflict and provides the latest remote payload.
Our repository then initiates a field-level three-way merge: if user A updated the title while user B updated the tags, both changes commit cleanly.
If both users edited the identical text field, we avoid silent data loss by surfacing an interactive conflict resolution sheet, empowering the user to choose which draft to retain while saving both versions in history.

## How to answer in the interview

- **Why:** Reconnect can reveal two valid but divergent user edits.
- **How:** Use base version/ETag and classify non-overlapping versus overlapping changes.
- **Trade-offs:** Explain data loss in client-wins and server-wins policies.
- **Failure cases:** Silent overwrite or merging authoritative financial state on device.
- **Production solution:** Preserve candidates, show conflict UI and server-check versions.

## Deep-dive talking points

Trace base/local/remote values, domain invariants and conflict persistence.

## Follow-up questions

- **Interviewer:** "Why is client device time dangerous for timestamp-based conflict resolution?"
  **Answer:** "Users can alter their device clock manually, or time zones and NTP sync failures can make client timestamps hours ahead or behind real UTC time."

- **Interviewer:** "What is a 3-way merge in data synchronization?"
  **Answer:** "Comparing the base ancestor version, the local branch, and the remote branch to determine which specific fields changed on each side."

## Self-check rubric

Can I detect conflict, choose policy by domain, preserve user edit and test skew/deletion?

## References and reviewed-on date

- [Android offline-first guidance](https://developer.android.com/topic/architecture/data-layer/offline-first) — conflict resolution.

Technically reviewed against primary documentation on 2026-10-13.
