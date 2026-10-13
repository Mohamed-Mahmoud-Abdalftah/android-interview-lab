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

وقت offline edit، نحفظ التعديل والـpending operation في Room transaction واحدة قبل ما نقول للمستخدم Saved. كل عملية لها stable ID وbase version. WorkManager يقرأ الطابور عند توفر network، يرسل بالترتيب المطلوب، ويعلّم acknowledged فقط بعد server response موثوقة. لو timeout، نستعلم عن status بنفس ID بدل إنشاء تعديل جديد.

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

## Practical walkthrough

offline edit لحظة الحفظ اعمل transaction تضم note الجديدة وoutbox command بنفس operation ID؛ لو crash بعد commit، worker يلاقي pending. worker يبعت command لما network تسمح، ويعدّل status/remote version بعد ack. لو ack ضاع، replay بنفس ID لا يخلق edit جديدة لو server idempotency contract موجود. conflict لو base version قديمة: لا تسكت وتكتب فوق تعديل جهاز تاني؛ اعرض conflict أو merge حسب field. اجعل queue مرتبطة بـuser/account، لا ترسل rows من user قديم بعد logout. اختبر crash قبل/بعد commit، أثناء send، وبعد server ack وقبل local ack.

## Trade-offs and decision criteria

Optimistic local UI feels immediate but can later conflict. Waiting for server avoids conflict UX but fails offline. Outbox adds schema/worker complexity and requires a visible pending state. Ordering rules depend on domain.

## Failure modes

Writing draft without outbox row loses sync intent after crash. Removing outbox row before server acknowledgement loses edits after timeout. Reusing an operation ID with different payload violates many idempotency contracts. Blind last-write-wins can erase another device’s change.

## Production perspective

A field inspection form commits edits locally, shows Pending badge, and syncs with WorkManager when connected. Server compares base version; conflict opens user review for text/attachments. Stuck pending age is monitored, and support can inspect operation IDs.

## Interview answer — short

“I use a transactional local outbox: save the edit and pending operation together, then a durable worker sends it with a stable ID and version. I acknowledge only after server confirmation and handle conflicts explicitly.”

## Interview answer — structured

“Offline edits need a durable workflow, not an in-memory retry coroutine. I commit the edited row and an outbox operation in one Room transaction, with a stable operation ID and base server version. A Worker sends pending entries when constraints permit. The UI shows local data as Pending. If the response is lost, the worker queries status or retries under the server’s idempotency contract; it does not create a new logical operation. Version conflicts go through a domain-specific merge or user resolution path. Ordering rules depend on domain.”

## Interview answer — deep senior

I design every crash point. Before local commit, the UI cannot claim save; after commit but before enqueue, a startup scan must schedule pending rows; after server acceptance but before local acknowledgement, the next worker run must reconcile by operation ID. Room gives atomic local edit/outbox persistence, and the server provides idempotency and version checks across devices. I keep an explicit state machine: pending, sending, acknowledged, conflicted, failed with retry metadata. The worker is repeat-safe, and cancellation does not discard the row. I test airplane mode, multiple offline edits, process death at each transition, conflict with another device and expired credentials.

I make the offline write atomic locally: the edited note and its outbox command commit in the same Room transaction. That guarantees a restarted worker can find every local edit that the UI claims was saved. The worker sends with a stable operation ID and expected server version, then records acknowledgement and new version locally. A lost acknowledgement may cause another HTTP request, so server idempotency or status reconciliation is required for one logical edit. If another device changed the note, the conflict policy must preserve user intent instead of silently overwriting it. I scope queues by account and test crash windows around commit, send, and acknowledgement.

## How to answer in the interview

- **Why:** Offline edits need durable intent and cross-device consistency.
- **How:** Transactionally write note plus outbox, then worker sends by stable ID.
- **Trade-offs:** Optimistic UI requires pending/conflict visibility.
- **Failure cases:** Lost outbox row, duplicate send, old-account queue leak.
- **Production solution:** Version checks, reconciliation and crash-window tests.

## Deep-dive talking points

Draw outbox state transitions, crash windows and conflict resolution.

## Follow-up questions

- [DAT-16](../dat-16/): What if base version is stale? **Answer:** apply domain merge or surface a conflict, never silently overwrite.
- [BG-08](../bg-08/): Who retries after process death? **Answer:** WorkManager reads durable outbox rows.

## Self-check rubric

Can I commit edit/outbox atomically, recover each crash window and reconcile duplicate sends?

## References and reviewed-on date

- [Android offline-first guidance](https://developer.android.com/topic/architecture/data-layer/offline-first) — queued writes and sync.
- [Android persistent work](https://developer.android.com/develop/background-work/background-tasks/persistent) — restartable scheduling.

Technically reviewed against linked primary documentation on 2026-10-13. Examples are conceptual unless explicitly stated otherwise; no Android device execution is claimed.
