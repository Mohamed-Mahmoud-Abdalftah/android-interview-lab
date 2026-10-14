---
id: "COR-30"
question: "A ViewModel disappears but critical persistence must finish. Who should own that work?"
topic: "Kotlin Coroutines & Concurrency"
code: "COR"
group: "C"
phase: 1
priority: "P1"
order: 111
editorial_status: "reviewed"
---

# COR-30

## Original interview question

A ViewModel disappears but critical persistence must finish. Who should own that work?

## What the interviewer evaluates

Choose ownership for critical persistence after ViewModel removal and distinguish durability from in-process scope.

## Explanation in Arabic

السؤال عن اختفاء الـ ViewModel مع ضرورة إتمام عملية حفظ حرجة (Critical Persistence) هو اختبار مباشر للـ Architecture Ownership في Android:

1. المشكلة:
   - المستخدم كتب بيانات مهمة وضغط 'حفظ ومغادرة'. الشاشة قفلت فوراً والـ ViewModel تم تدميره واستدعى `onCleared()`.
   - لو عملية الحفظ كانت شغالة في `viewModelScope.launch`، **ستُلغى العملية فوراً**، وتضيع بيانات المستخدم ويتلف مسار العمل!

2. من الذي يجب أن يمتلك هذه العملية (Who should own this work)?
   - **الـ ViewModel لا يمتلكها!** الـ ViewModel يمتلك فقط العمليات المرتبطة بعرض الشاشة الحالية.
   - **الخيار الأول (عمليات سريعة في الذاكرة / Room Database):** يمتلكها **Application-Level CoroutineScope** محقون في الـ Repository. التطبيق حي، والـ Repository يكمل حفظ البيانات في Room حتى بعد موت الشاشة.
   - **الخيار الثاني (عمليات حيوية يجب أن تكتمل حتى لو قفل التطبيق أو مات الـ Process):** يمتلكها **WorkManager**. WorkManager يضمن إرسال البيانات للسيرفر حتى لو النظام قتل التطبيق لتوفير الذاكرة أو أعاد تشغيل الهاتف.

## Practical walkthrough

التصميم المعماري الاحترافي المعتمد من Google:
```kotlin
@Singleton
class UserRepository @Inject constructor(
    private val userDao: UserDao,
    private val api: UserApi,
    @ApplicationScope private val externalScope: CoroutineScope // Scope حي مع التطبيق
) {
    
    suspend fun saveUserProfile(profile: UserProfile) {
        // نطلق الحفظ داخل externalScope حتى لا يلغى بموت الـ ViewModel:
        externalScope.launch {
            userDao.insert(profile.toEntity()) // يكتمل 100% حتى لو المستخدم خرج من الشاشة
        }.join() // نعلق الـ ViewModel الحالي ليرى النتيجة لو كان ما زال حياً
    }
}
```

## Why it matters and how it works

Durable work has two parts: persist enough input/state to restart, then schedule execution. A worker must be idempotent or reconcile duplicates because work can be retried. A ViewModel can await the local durable enqueue acknowledgement, then observe persisted status. For immediate, user-visible tasks requiring special execution constraints, select Android’s supported foreground/background mechanism deliberately.

## Worked example

Conceptual Android snippet assumes Room-backed `OperationDao` and a configured WorkManager `SyncWorker`; the enqueue occurs after saving input.

```kotlin
import androidx.work.OneTimeWorkRequestBuilder
import androidx.work.WorkManager

suspend fun queueSync(
    id: String,
    dao: OperationDao,
    workManager: WorkManager,
) {
    dao.insertPending(id) // durable transaction in real implementation
    val request = OneTimeWorkRequestBuilder<SyncWorker>().build()
    workManager.enqueue(request)
}
// OperationDao and SyncWorker are application types.
```

## Trade-offs and decision criteria

WorkManager provides persistent scheduling under OS constraints but does not guarantee immediate execution or exactly-once side effects. An application scope can finish a short in-process operation after a screen leaves but is lost on process death. Design recovery and server idempotency for critical writes.

## Failure modes

If the ViewModel launches a file write and navigation immediately clears it, the write can be cancelled halfway. If the app crashes after storing a Pending row but before enqueue, a startup reconciliation pass should find and schedule it. If a worker repeats, the server must deduplicate logical operations.

## Production perspective

An offline form saves a pending submission locally before navigation. WorkManager sends it when constraints allow, marks acknowledged only after server confirmation, and uses a stable operation ID. UI observes Room status; telemetry detects stuck Pending rows and startup recovery re-enqueues them.

## Interview answer — short

The ViewModel must NOT own critical persistence because viewModelScope cancels on onCleared(). Quick local persistence should be owned by an application-level CoroutineScope injected into the Repository layer, while critical remote uploads that must survive process death must be delegated to WorkManager.

## Interview answer — structured

Critical persistence must never be owned by the ViewModel. When a user navigates away or presses the back button, the ViewModel is destroyed and its `viewModelScope` cancels immediately, aborting any active database transactions or network dispatches.

The ownership belongs in the Data/Repository layer using one of two mechanisms based on durability requirements.

First, **In-Process Operations (Local Room DB writes or analytics):** An **Application-Level CoroutineScope** injected into the Repository. By configuring this scope with `SupervisorJob() + Dispatchers.IO` as an application-level singleton in Dagger/Hilt, the coroutine continues executing to completion even after the calling ViewModel is garbage collected. Finally, **Guaranteed Operations (Surviving process death & reboots):** If the work involves syncing an order or uploading photos that must complete even if the user swipes the app away from recents or the OS kills the process under low memory, it must be delegated to **WorkManager**. WorkManager persists the job in SQLite and guarantees execution with constraints.


## Interview answer — deep senior

Architecturally, this adheres to the principle of scoping work to the lifecycle of the data, not the lifecycle of the UI. In Hilt, we provide the application scope as follows:

```kotlin
@Provides
@Singleton
@ApplicationScope
fun provideAppCoroutineScope(): CoroutineScope =
    CoroutineScope(SupervisorJob() + Dispatchers.Default)
```

Inside the repository, we use the pattern of starting the work on the `externalScope` and awaiting it with `join()`:

```kotlin
suspend fun saveOrder(order: Order) {
    externalScope.launch(Dispatchers.IO) {
        database.orderDao().insert(order)
    }.join()
}
```

This pattern has a major architectural advantage: if the ViewModel remains alive, `join()` suspends so the UI can show a loading spinner and transition upon completion. But if the ViewModel is destroyed, only the caller continuation is cancelled; the launched job on `externalScope` continues running independently until completion.


## How to answer in the interview

- **Why:** the ViewModel only owns work while its screen owner exists.
- **How:** persist retryable intent, schedule a worker, and reconcile pending rows at startup.
- **Trade-off:** WorkManager is durable scheduling, not immediate or exactly-once execution.
- **Failure case:** process death between local commit and enqueue.
- **Production solution:** idempotent backend operation and persistent state transitions.

## Deep-dive talking points

Draw crash windows before/after persistence, enqueue, send and acknowledgement; distinguish scheduling from exactly-once effects.

## Follow-up questions

- **Interviewer:** "Why not use `NonCancellable` context inside `viewModelScope` instead of an ApplicationScope?"
  **Answer:** "Writing `withContext(NonCancellable)` inside `viewModelScope` delays cancellation for that specific block, but it keeps the ViewModel in memory until completion and is fragile. If the entire process is cleared or multiple operations queue up, relying on a dead ViewModel's scope is an architectural anti-pattern."

- **Interviewer:** "How does WorkManager handle network constraints compared to coroutines?"
  **Answer:** "WorkManager leverages the Android JobScheduler system daemon to defer task execution until exact device constraints are met (e.g., unmetered Wi-Fi connection, battery not low, device idle), which coroutines in an active process cannot do."

- **Interviewer:** "How do you test a repository that uses an injected application CoroutineScope?"
  **Answer:** "In your unit test, inject a `TestScope` as the `@ApplicationScope`. Call `testScope.advanceUntilIdle()` to deterministically assert that background persistence completed."

## Self-check rubric

Can I persist intent first, recover enqueue gaps, make workers repeat-safe and explain timing constraints?

## References and reviewed-on date

- [Android persistent work](https://developer.android.com/develop/background-work/background-tasks/persistent) — durable scheduling.
- [Android offline-first guidance](https://developer.android.com/topic/architecture/data-layer/offline-first) — pending writes and sync.

Technically reviewed against primary documentation on 2026-10-13.
