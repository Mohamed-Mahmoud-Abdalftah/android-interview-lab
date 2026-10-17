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

Designing an enterprise mobile system for hostile deployment environments—characterized by intermittent cellular connectivity, severe bandwidth throttling, sudden airplane mode switches, and abrupt power loss—requires an offline-first architecture. In such environments, the local persistent database must serve as the single source of truth, and network operations must be modeled as asynchronous synchronization events rather than prerequisites for user interaction. SQLite persistence via Room must enable Write-Ahead Logging (WAL) mode to protect database files from physical corruption during abrupt battery depletion or unexpected process termination. User actions must follow the local outbox pattern: every mutation is written to a durable pending operations table within an atomic SQLite transaction before updating the user interface. Background synchronization is delegated to WorkManager with battery-aware constraints, utilizing delta sync payloads and compact binary formats to minimize cellular overhead.

## Practical walkthrough (English)

Implementing an atomic mutation outbox with battery-conscious background synchronization:
```kotlin
// 1. Room database configured with Write-Ahead Logging for power-loss corruption resistance
@Database(entities = [OrderEntity::class, OutboxMutationEntity::class], version = 1)
abstract class ResilientAppDatabase : RoomDatabase() {
    abstract fun outboxDao(): OutboxDao
    abstract fun orderDao(): OrderDao

    companion object {
        fun buildDatabase(context: Context): ResilientAppDatabase {
            return Room.databaseBuilder(context, ResilientAppDatabase::class.java, "resilient.db")
                .setJournalMode(JournalMode.WRITE_AHEAD_LOGGING) // High durability against sudden battery shutoff
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
            .setRequiresBatteryNotLow(true)
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

كيف تصمم تطبيقاً يعمل بكفاءة تحت ظروف الاتصال الضعيف جداً (Poor Connectivity) والانقطاع المفاجئ للطاقة والبطارية (Intermittent Power Loss)؟

1. تحديات البيئات القاسية (Harsh Constraints / Emerging Markets):
   - شبكات 2G/3G متقطعة، زمن استجابة عالي (Latency > 2000ms)، باقات بيانات مكلفة ومحدودة.
   - بطاريات هواتف رديئة، وإمكانية إغلاق الهاتف فجأة في أي ثانية بسبب نفاد الشحن.

2. تقليص استهلاك الشبكة (Data Thrift & Bandwidth Optimization):
   - **ضغط البيانات بصيغ حديثة**: استخدام **Protocol Buffers (Protobuf)** أو GZIP JSON لتقليص حجم البايتات بنسبة 60-80% مقارنة بالنصوص العادية.
   - **تحسين الصور**: استخدام صيغ WebP أو AVIF، وجلب صور مصغرة جداً (Thumbnails) تناسب أبعاد الشاشة فقط، ومنع تحميل الصور عالية الدقة إلا على شبكات Wi-Fi.
   - **Delta Sync**: جلب البيانات المعدلة فقط منذ آخر فحص بدلاً من إعادة تنزيل القوائم كاملة.

3. الحماية ضد انقطاع الطاقة المفاجئ (Power Loss & Crash Resilience):
   - **المعاملات الذرية في SQLite (Atomic Transactions & WAL Mode)**: استخدام Room داخل `database.withTransaction { ... }` وتفعيل وضع Write-Ahead Logging (WAL). هذا يضمن أنه لو انطفأ الهاتف أثناء الكتابة، لن يتلف ملف قاعدة البيانات أبداً.
   - **جدولة المهام الموفرة للطاقة عبر WorkManager**:
     * وضع قيود صارمة على مهام الخلفية: `setRequiresBatteryNotLow(true)` و `setRequiresCharging(true)` لضمان عدم استنزاف طاقة المستخدم عند قرب نفاد البطارية.

## Practical walkthrough

تطبيق إعدادات توفير البيانات وحماية قاعدة البيانات من الانقطاع المفاجئ للطاقة:
```kotlin
// 1. إعدادات Room Database محمية بـ WAL Mode لمنع تلف الملفات عند انطفاء الهاتف:
@Database(entities = [TransactionEntity::class], version = 1)
abstract class ResilientDatabase : RoomDatabase() {
    companion object {
        fun create(context: Context): ResilientDatabase {
            return Room.databaseBuilder(context, ResilientDatabase::class.java, "resilient.db")
                .setJournalMode(JournalMode.WRITE_AHEAD_LOGGING) // حماية فائقة ضد انقطاع الطاقة المفاجئ
                .build()
        }
    }
}

// 2. جدولة مزامنة البيانات الكبيرة مع مراعاة حالة البطارية والشبكة:
fun scheduleBatteryAwareSync(workManager: WorkManager) {
    val constraints = Constraints.Builder()
        .setRequiredNetworkType(NetworkType.UNMETERED) // مزامنة البيانات الضخمة فقط على Wi-Fi
        .setRequiresBatteryNotLow(true)               // منع التشغيل إذا كانت البطارية منخفضة (< 15%)
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

We design for poor connectivity and power loss using an offline-first architecture with Room Write-Ahead Logging to prevent database corruption. We store mutations in a local outbox table before updating the UI, delegating background uploads to WorkManager with battery and network constraints, and streaming delta updates.

## Interview answer — structured

Designing for extreme network volatility and sudden power loss requires treating local persistence as the primary source of truth.
I configure Room with SQLite Write-Ahead Logging (WAL) mode. This guarantees atomic transaction durability and prevents physical database corruption if the device shuts down mid-write.
Every user mutation follows the transactional outbox pattern. When an action occurs, the app saves the intent to an outbox table in an atomic database transaction before updating the UI optimistically.
The UI never spins with blocking network loaders; actions feel instantaneous because they commit to disk locally.
Background uploads are handed off to WorkManager configured with constraints like connected network and battery not low.
WorkManager handles exponential backoff and retries safely across device reboots.
To preserve cellular data on slow networks, synchronization requests exchange compressed delta payloads using server revision tokens rather than re-transmitting entire entities.

## Interview answer — deep senior

From a staff mobile architecture perspective, designing for extreme environments requires managing data synchronization conflicts, radio power states, and honest user interface state indicators.
The primary risk in offline-first systems is conflict resolution. When multiple offline mutations accumulate on the client while other edits occur on the server, blind last-write-wins policies cause silent data loss. We resolve this by associating records with server revision vectors or timestamps. When the client syncs, the backend detects version divergence and executes deterministic three-way merges or flags conflicts for manual user resolution.
To survive intermittent cellular conditions, network serialization must minimize packet size. We replace verbose JSON payloads with Protocol Buffers or GZIP-compressed binary streams, significantly reducing transmission time over flaky 2G or 3G connections and lowering socket timeout rates.
Radio management is critical for devices with degraded batteries. Firing frequent small network requests keeps the cellular baseband processor energized in high-power states. Our sync engine batches pending outbox mutations, flushing up to fifty operations in a single persistent HTTP connection to allow the cellular radio to return to low-power sleep immediately.
Finally, the user experience must maintain transparent honesty. We provide visual pending indicators on un-synced items, reassuring users that their data is safely persisted on their phone and will synchronize automatically when power and signal restore.

## How to answer in the interview

- **Why:** power loss can interrupt any in-memory step.
- **How:** durably commit intent, schedule repeat-safe sync, and reconcile unknown remote results.
- **Trade-off:** offline support adds storage, conflict, and UX costs.
- **Failure case:** acknowledging success before local commit or retrying a write with a new ID.
- **Production solution:** Room transaction, WorkManager, backend idempotency, and crash-injection tests.

## Deep-dive talking points

Trace power loss before/after local commit, remote commit and acknowledgement.

## Follow-up questions

- **Interviewer:** "What is the benefit of using Android's AtomicFile helper class?"
  **Answer:** "AtomicFile writes data to a temporary file and performs an atomic rename, ensuring that sudden process death or power loss never leaves a corrupted, half-written file on disk."

- **Interviewer:** "Why is Write-Ahead Logging (WAL) mode safer during sudden power loss?"
  **Answer:** "WAL appends modifications to a separate log file without modifying original database pages directly, making recovery trivial if power cuts before a checkpoint."

## Self-check rubric

Can I preserve accepted intent, reconcile unknown outcome and test power-loss windows?

## References and reviewed-on date

- [Android offline-first guidance](https://developer.android.com/topic/architecture/data-layer/offline-first) — local source and sync.
- [Android task scheduling](https://developer.android.com/develop/background-work/background-tasks/persistent) — restartable work.

Technically reviewed against primary documentation on 2026-10-13.
