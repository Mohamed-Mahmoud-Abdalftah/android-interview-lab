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

Resolve conflicts between local and server state using Optimistic Concurrency Control with version numbers or ETags. When divergent states collide (HTTP 409), choose a domain-appropriate strategy: Server-Wins for authoritative data, field-level 3-way merging for non-overlapping attributes, or manual user review for documents and text.

## Interview answer — structured

When offline edits diverge from remote updates, naive Last-Write-Wins (LWW) based on device timestamps causes silent data loss due to client clock drift. Robust architectures implement **Optimistic Concurrency Control (OCC)**:

1. **Version Tracking / ETags**: Every entity carries a `version: Long` or an HTTP `ETag` hash. When mutating data, the client submits `{ entityId, payload, baseVersion }`.

2. **Server-Side Compare-and-Set**: If the server's current version matches `baseVersion`, the update commits and increments the version. If another client updated the record in the interim, the server rejects the write with **`409 Conflict`** and returns the latest server state.

3. **Resolution Strategies by Business Domain**:
   - **Authoritative Data (Inventory, Financial Balance)**: **Server-Wins**. The client discards local changes and updates Room with server ground truth.
   - **Granular Attribute Merging**: If the server changed `status` and the client changed `notes`, apply 3-way merging to combine non-overlapping fields.
   - **Collaborative Text (Notes, Documents)**: Present a visual conflict dialog allowing the user to select the preferred version or fork into two separate documents.

## Interview answer — deep senior

In advanced distributed mobile architectures (such as collaborative canvases or offline Google Docs), teams implement **CRDTs (Conflict-free Replicated Data Types)**.

CRDTs (such as State-based or Operation-based PN-Counters, LWW-Element-Sets, or Yjs/Automerge trees) are mathematically proven to converge to the identical state on all nodes without central locking or conflict dialogs, regardless of network arrival order or message duplication.

However, for standard enterprise Android applications, Optimistic Concurrency Control with a conflict resolution table in Room provides 99% of the reliability with a fraction of the algorithmic complexity.

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
