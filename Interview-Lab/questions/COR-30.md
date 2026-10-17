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

## Concept and technical explanation

When an Android user triggers a critical persistence operation—such as tapping "Submit Order", saving an encrypted draft, or posting a financial payment—and immediately dismisses the screen or navigates back, the hosting Activity is finished and the ViewModel invokes onCleared(). Any coroutine launched inside viewModelScope is cooperatively cancelled immediately, causing in-flight persistence operations to abort mid-execution. Deciding who owns this critical work is a fundamental architectural boundary question. In modern Android architecture, ownership is bifurcated based on execution durability requirements. If the persistence operation is an immediate local database transaction (Room/SQLite) that must complete as long as the application process remains alive in memory, it must be owned by an application-level CoroutineScope (such as an injected @ApplicationScope CoroutineScope(SupervisorJob() + Dispatchers.IO)) living in the Repository. However, if the operation involves remote network synchronization or must be guaranteed to survive operating system process death (via the Low Memory Killer) or device reboots, in-memory scopes are fundamentally insufficient; the operation MUST be delegated to Android Jetpack WorkManager.

## Practical walkthrough (English)

Consider saving an offline customer order when the user immediately exits the checkout screen:
```kotlin
// Erroneous implementation: bound to dying ViewModel scope
class CheckoutViewModel(private val repository: OrderRepository) : ViewModel() {
    fun submitOrder(order: Order) {
        viewModelScope.launch {
            // BUG: If user presses Back, viewModelScope cancels immediately!
            // Order write is aborted mid-flight or never reaches database!
            repository.saveAndSyncOrder(order)
        }
    }
}

// Production-grade architectural solution:
// 1. Fast local persistence via injected ApplicationScope:
@Singleton
class OrderRepository @Inject constructor(
    private val orderDao: OrderDao,
    private val workManager: WorkManager,
    @ApplicationScope private val appScope: CoroutineScope
) {
    suspend fun submitOrder(order: Order) {
        // Fast in-process write: completes even if ViewModel is cleared
        appScope.launch {
            orderDao.insertOrder(order.copy(status = SyncStatus.PENDING))
            
            // 2. Guaranteed durable remote delivery via WorkManager:
            val syncWork = OneTimeWorkRequestBuilder<OrderSyncWorker>()
                .setConstraints(Constraints.Builder().setRequiredNetworkType(NetworkType.CONNECTED).build())
                .setInputData(workDataOf("order_id" to order.id))
                .build()
            workManager.enqueueUniqueWork("sync_${order.id}", ExistingWorkPolicy.KEEP, syncWork)
        }.join()
    }
}
```

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

viewModelScope cancels immediately when the user exits the screen. For critical persistence, immediate local database writes must be owned by an Application-level CoroutineScope injected into the repository. For guaranteed remote delivery that must survive process death by the OS or device reboots, the work MUST be delegated to Jetpack WorkManager, which persists tasks durably in SQLite.

## Interview answer — structured

Relying on viewModelScope for critical persistence is a dangerous architectural mistake because viewModelScope is strictly bound to the screen's interactive lifespan. When the user taps save and exits, the ViewModel is cleared, cancelling viewModelScope and aborting any in-flight database or network operations.

Ownership of critical operations must be decoupled from the presentation layer.

In production, we divide persistence ownership into two distinct tiers based on durability guarantees. Tier one handles fast, in-process local database writes: this work is owned by an application-scoped CoroutineScope injected into the repository layer. Because this scope is anchored to the Application lifecycle with a SupervisorJob, it completes writing the record to the local SQLite database even after the ViewModel has been destroyed. Tier two handles durable, asynchronous remote synchronization: because in-memory application scopes are terminated if the OS Low Memory Killer kills the process in the background, guaranteed delivery must be owned by Android Jetpack WorkManager.

WorkManager persists task constraints in an internal database and uses platform job schedulers to guarantee execution across process death and device restarts.


## Interview answer — deep senior

At the Android framework and process lifecycle level, there is a fundamental distinction between an in-memory CoroutineScope and a durable OS-managed task. When an Activity finishes, the ViewModelStore invokes ViewModel.clear(), which calls cancel() on the Job stored inside viewModelScope's CoroutineContext. Any active continuation running inside that scope receives a CancellationException, unwinding the call stack and aborting incomplete database writes. To ensure that an in-process operation survives screen teardown, we construct an application-level scope: CoroutineScope(SupervisorJob() + Dispatchers.IO), provisioned as a Singleton via Dagger/Hilt. When the repository launches work in this scope, the operation is completely immune to UI lifecycle destruction, running to completion as long as the Linux process remains alive. However, senior engineers must recognize the limits of application scopes: once the user navigates away, the Android ActivityManagerService reduces the process's oom_adj score, placing it in the CACHED_APP pool. If the device experiences memory pressure, the Linux kernel Low Memory Killer (lmkd) terminates the entire process via a SIGKILL signal without invoking any callbacks or coroutine cancellation handlers. Any in-memory coroutine running network synchronization is destroyed instantly. Therefore, for business-critical operations—such as financial transactions, message delivery, or background photo uploads—the repository must immediately commit the payload to local storage and hand off the task to Jetpack WorkManager. WorkManager stores execution metadata and network constraints inside its own internal SQLite database and integrates with system daemons like JobScheduler. If the app process is killed or the device is rebooted, the operating system resurrects the process when constraints are met and executes the Worker, guaranteeing at-least-once execution and rock-solid architectural reliability.

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
