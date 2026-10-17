---
id: "SYS-24"
question: "How would you design for poor connectivity and intermittent power loss?"
topic: "Android System Design & Architecture Decisions"
code: "SYS"
group: "C"
phase: 4
priority: "P1"
order: 353
editorial_status: "reviewed"
---

# SYS-24

## Original interview question

How would you design for poor connectivity and intermittent power loss?

## What the interviewer evaluates

Design for poor connectivity and intermittent power loss with durable state and honest UX.

## Concept and technical explanation

Poor connectivity calls for explicit local and remote state. For operations that can be accepted locally, save the visible change and an outbox row together, then show whether the server has confirmed it. Use stable operation IDs so the backend can deduplicate retries, and define a conflict rule for edits made on multiple devices. WorkManager can schedule persistent background sync under selected constraints, but it cannot make a disconnected server reachable or promise immediate execution. SQLite transactions protect local consistency; WAL mode is a journaling choice, not a universal guarantee that every commit survives sudden power loss. Durability depends on sync settings and storage behavior. Test process death, device restart, duplicate sends, and ambiguous server outcomes separately.

## Practical walkthrough (English)

Implementing an atomic mutation outbox with battery-conscious background synchronization:
```kotlin
// 1. Room database journaling mode; verify durability settings for critical data
@Database(entities = [OrderEntity::class, OutboxMutationEntity::class], version = 1)
abstract class ResilientAppDatabase : RoomDatabase() {
    abstract fun outboxDao(): OutboxDao
    abstract fun orderDao(): OrderDao

    companion object {
        fun buildDatabase(context: Context): ResilientAppDatabase {
            return Room.databaseBuilder(context, ResilientAppDatabase::class.java, "resilient.db")
                .setJournalMode(JournalMode.WRITE_AHEAD_LOGGING) // journaling choice, not a power-loss guarantee
                .build()
        }
    }
}

// 2. Atomic outbox mutation record storing user intent locally before network dispatch
@Entity(tableName = "outbox_mutations")
data class OutboxMutationEntity(
    @PrimaryKey val mutationId: String = UUID.randomUUID().toString(),
    val actionType: String,
    val payloadJson: String,
    val timestampMs: Long = System.currentTimeMillis(),
    val retryCount: Int = 0
)

// 3. Scheduling battery-conscious, network-constrained synchronization via WorkManager
class ResilientSyncScheduler @Inject constructor(
    private val workManager: WorkManager
) {
    fun scheduleOutboxSync() {
        val constraints = Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .setRequiresBatteryNotLow(true) // only if this work can wait for charge
            .build()

        val syncRequest = OneTimeWorkRequestBuilder<OutboxSyncWorker>()
            .setConstraints(constraints)
            .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 15, TimeUnit.SECONDS)
            .build()

        workManager.enqueueUniqueWork("outbox_sync", ExistingWorkPolicy.KEEP, syncRequest)
    }
}
```

## Explanation in Arabic

الاتصال الضعيف يحتاج تمييزاً واضحاً بين الحالة المحلية وما أكده السيرفر. للعمليات التي يمكن قبولها محلياً، أحفظ التغيير الظاهر وسجل Outbox في Transaction واحدة، ثم أعرض هل تم تأكيده من السيرفر أم لا. معرف عملية ثابت يساعد الـ Backend يمنع تكرار إعادة المحاولة، وRevision أو قاعدة تعارض تحمي تعديلات الأجهزة المختلفة. WorkManager يجدول المزامنة المستمرة تحت قيود مناسبة لكنه لا يجعل السيرفر غير المتاح متاحاً ولا يضمن وقت تنفيذ فوري. SQLite Transaction تحمي الاتساق المحلي؛ WAL طريقة Journaling وليست ضماناً عاماً لنجاة كل Commit من انقطاع الطاقة. المتانة تعتمد على إعدادات `synchronous` والتخزين. أختبر Process Death وإعادة تشغيل الجهاز وإعادة الإرسال والنتائج الملتبسة كل حالة لوحدها.

## Practical walkthrough

تطبيق إعدادات توفير البيانات وحماية قاعدة البيانات من الانقطاع المفاجئ للطاقة:
```kotlin
// 1. مثال Journaling في Room؛ راجع إعدادات المتانة للبيانات الحرجة:
@Database(entities = [TransactionEntity::class], version = 1)
abstract class ResilientDatabase : RoomDatabase() {
    companion object {
        fun create(context: Context): ResilientDatabase {
            return Room.databaseBuilder(context, ResilientDatabase::class.java, "resilient.db")
                .setJournalMode(JournalMode.WRITE_AHEAD_LOGGING) // ليس ضماناً لكل انقطاع طاقة
                .build()
        }
    }
}

// 2. جدولة مزامنة البيانات الكبيرة مع مراعاة حالة البطارية والشبكة:
fun scheduleBatteryAwareSync(workManager: WorkManager) {
    val constraints = Constraints.Builder()
        .setRequiredNetworkType(NetworkType.UNMETERED) // مزامنة البيانات الضخمة فقط على Wi-Fi
        .setRequiresBatteryNotLow(true) // only if this work can wait for charge               // منع التشغيل إذا كانت البطارية منخفضة (< 15%)
        .setRequiresCharging(false)
        .build()

    val syncWork = PeriodicWorkRequestBuilder<HeavySyncWorker>(6, TimeUnit.HOURS)
        .setConstraints(constraints)
        .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 15, TimeUnit.MINUTES)
        .build()

    workManager.enqueueUniquePeriodicWork("heavy_sync", ExistingPeriodicWorkPolicy.KEEP, syncWork)
}
```

## Why it matters and how it works

Use bounded local storage and cleanup that never deletes unacknowledged operations. Network timeouts create ambiguous remote outcomes; reconcile by stable ID. A battery/power loss can interrupt file/database migration or upload, so use transactional writes, checksums and resumable protocols. Cache TTL is domain-specific.

## Worked example

Conceptual persistent state model; implementation spans Room, WorkManager and server.

```kotlin
sealed interface SyncState {
    data object LocalPending : SyncState
    data object Sending : SyncState
    data object UnknownRemote : SyncState
    data class Confirmed(val version: String) : SyncState
    data class Conflict(val serverVersion: String) : SyncState
}
```

## Trade-offs and decision criteria

Offline-first adds storage and conflict complexity but preserves usefulness. A network-only app is simpler where offline action is not required. Background scheduling saves battery but may delay completion; product promises should describe Pending rather than exact time.

## Failure modes

A request can reach server before power loss; resending with new key duplicates write. Deleting cached rows before refresh creates blank offline UI. A partial file move can corrupt data without journal/verification. Unbounded retry can drain battery.

## Production perspective

A field inspection app saves forms/attachments locally, resumes uploads by acknowledged chunk, reconciles server status after restart and shows stale/pending badges. Support sees operation IDs; tests simulate airplane mode, force-stop, reboot, low battery and disk full.

## Interview answer — short

I would save user actions locally before relying on the network, show which ones are still pending, and sync them later with stable operation IDs. Room transactions help keep the local record and outbox consistent; WorkManager can schedule deferred uploads across app restarts. Neither WAL nor WorkManager guarantees that data survives every power failure or reaches a server that stays offline. The backend needs idempotency and conflict rules, and the UI needs an honest unresolved state.

## Interview answer — structured

I would design the feature so a weak connection does not decide whether the user can make progress. A local database can hold the screen state and an outbox of actions waiting to sync. When the user edits something, I save the new state and its pending operation in one local transaction, then show that it is saved locally but not yet confirmed by the server.

For delivery I would schedule background sync with WorkManager and use stable operation IDs so a retry cannot create a duplicate server action. I would choose network and battery constraints based on urgency; for a payment or safety action, “battery not low” may delay work that should be escalated. When the app restarts, it reads the outbox and resumes. If the server changed the same record, the API needs a version or conflict response rather than silently overwriting one side.

I would not promise that WAL alone protects every acknowledged write from a sudden power loss; durability depends on database and storage settings. Nor can the phone guarantee delivery while the network is unavailable indefinitely. I would test shutdown at each boundary, duplicate retries, stale server versions, and the user message when an action remains unresolved.

## Interview answer — deep senior

The first design choice is which data can be trusted locally. For a notes feature, local state may be the immediate source for the UI. For a bank balance, the server is authoritative and the local copy is explicitly stale until confirmed. I would define that per operation rather than declare the whole app “offline-first.” The outbox row should include an immutable operation ID, payload version, state, and last known server revision. Saving the visible local change and the outbox entry in one database transaction prevents the UI from showing a submitted action that the sync engine cannot find.

On restart, a worker scans pending entries. It may run more than once, be stopped when constraints change, or receive a timeout after the server committed the action. That is why the server must deduplicate the operation ID and expose enough status to reconcile unknown outcomes. Retries need bounded backoff, and permanent validation errors need a visible path for correction. For conflicting edits, I would use a revision check and a domain-specific resolution rule; last-write-wins is acceptable only where losing an older edit is explicitly okay.

Power loss needs careful language. SQLite transactions help preserve local consistency, but WAL mode is not a blanket guarantee of durable commits under every sync setting or storage failure. I would test process kill and device restart separately, then inspect the actual storage settings for the data's risk level. Compression and batching can help slow networks, but I would measure them rather than assume they improve every payload. The user should always see whether data is local, pending, confirmed, or needs action.

## How to answer in the interview

- **Why:** power loss can interrupt any in-memory step.
- **How:** durably commit intent, schedule repeat-safe sync, and reconcile unknown remote results.
- **Trade-off:** offline support adds storage, conflict, and UX costs.
- **Failure case:** acknowledging success before local commit or retrying a write with a new ID.
- **Production solution:** Room transaction, WorkManager, backend idempotency, and crash-injection tests.

## Deep-dive talking points

Trace power loss before/after local commit, remote commit and acknowledgement.

## Follow-up questions

- **Interviewer:** "Does WAL guarantee an action survives a sudden battery removal?"
  **Answer:** "No blanket guarantee. Transactions protect consistency, but power-loss durability depends on the SQLite sync mode and storage behavior. I would verify the configuration and test the failure window for this data's risk level."

- **Interviewer:** "What if the server applied the action but the response was lost?"
  **Answer:** "I keep the same operation ID, query or retry under an idempotent server contract, and leave the UI pending until the outcome is known. I would not create a new action ID."

- **Interviewer:** "Would you require battery-not-low for every sync?"
  **Answer:** "No. I would choose constraints from urgency. A routine catalog update can wait; a critical pending operation may need a different policy and an escalation path."

## Self-check rubric

Can I preserve accepted intent, reconcile unknown outcome and test power-loss windows?

## References and reviewed-on date

- [Android offline-first guidance](https://developer.android.com/topic/architecture/data-layer/offline-first) — local source and sync.
- [Android task scheduling](https://developer.android.com/develop/background-work/background-tasks/persistent) — restartable work.

Technically reviewed against primary documentation on 2026-10-13.
