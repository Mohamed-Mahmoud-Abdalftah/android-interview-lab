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

Design for extreme constraints using compact binary payloads (Protobuf), WebP image compression, and local-first delta sync. Guard against sudden power loss using SQLite Write-Ahead Logging in atomic transactions, and defer heavy synchronization to Wi-Fi and healthy battery states via WorkManager constraints.

## Interview answer — structured

Designing for poor connectivity and sudden power loss treats resource scarcity as the default operating environment.

First, **Bandwidth Thrift & Binary Encoding**. Next, replace verbose JSON payloads with Protocol Buffers (gRPC/Protobuf) or enforce HTTP GZIP/Brotli compression, reducing network payload size by up to 70%.
Downsample media server-side to match the exact physical display density. Serve modern image formats (WebP or AVIF), deferring high-resolution asset downloads until unmetered Wi-Fi is detected. **Resilience Against Sudden Power Loss**.
Budget devices frequently experience sudden shutdowns due to degraded batteries under load. Prevent SQLite database corruption by enabling **Write-Ahead Logging (WAL)** mode in Room. Execute multi-table writes strictly inside atomic `database.withTransaction { }` blocks. If power drops mid-write, SQLite rolls back to the last consistent checkpoint on reboot without corrupting database pages.
**Battery-Aware Scheduling via WorkManager**. Finally, schedule background data syncs with explicit hardware constraints: `.setRequiresBatteryNotLow(true)` and `.setRequiredNetworkType(NetworkType.CONNECTED)`. This prevents the application from waking up the CPU when battery levels drop below 15%.


## Interview answer — deep senior

From a low-level platform architecture perspective, intermittent connectivity requires intelligent connection management.

First, with Adaptive Network Quality Telemetry, monitor cellular connection quality using Android's `ConnectivityManager.NetworkCallback` and bandwidth meters. When throughput drops below 50 kbps (2G/Edge), switch the app dynamically into 'Data Saver Mode': disable auto-playing videos, suppress decorative graphics, and request low-bandwidth text payloads from the backend. Next, with Atomic Disk File Operations, when saving downloaded files or JSON caches to disk, never write directly to the target file path. Write data to a temporary file (`temp_file.tmp`) and atomically rename it using `File.renameTo()` or `AtomicFile`. If power cuts out mid-write, the original file remains uncorrupted.
Finally, with Aggressive Offline Queuing (The Outbox Pattern), queue all user actions in persistent SQLite tables. Users in the field can continue creating invoices, taking notes, or logging deliveries offline with 100% responsiveness, confident that the synchronization engine will replay records deterministically when cellular coverage returns.


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
