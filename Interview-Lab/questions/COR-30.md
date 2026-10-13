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

لو ViewModel اتشال، `viewModelScope` هيتلغي؛ مينفعش نعتمد عليه يكمل كتابة مهمة لا يجوز ضياعها. أول خطوة نحفظ intent/operation في storage durable بtransaction قبل ما نسيب الشاشة، وبعدها WorkManager أو mechanism مناسب يعيد المحاولة بعد process death حسب قيود Android. application scope ممكن يكمل جوه نفس process فقط، مش بديل للاستمرار بعد قتله.

## Practical walkthrough

لو المستخدم ضغط حفظ ثم قفل الشاشة، `viewModelScope` ممكن يتلغي قبل اكتمال الكتابة. لو المطلوب ضمان بعد موت التطبيق، سجّل intent في Room transaction قبل ما تعلن قبول العملية، وبعدها WorkManager يكمّلها أو retry. لو crash حصل بين التخزين وenqueue، recovery scan يلاقي Pending ويعيد الجدولة. ولو worker اتكرر، backend لازم يستخدم operation ID ثابت.

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

“Critical work needs durable ownership. I persist the operation and enqueue restartable work, usually with WorkManager, before the ViewModel disappears. An application scope lasts only while the process does. The worker must handle retries and duplicate execution safely.”

## Interview answer — structured

“A ViewModel is the wrong owner if cancellation on navigation would lose the operation. I first commit a pending record with a stable ID to local storage, then schedule a Worker that can resume after process death and obey Android constraints. The ViewModel observes the durable status and can safely disappear. WorkManager is not a guarantee of instant or exactly-once remote execution, so I make the worker idempotent and reconcile ambiguous outcomes. I also handle the gap between local insert and enqueue with a recovery scan.”

## Interview answer — deep senior

“I split acceptance of the user action from execution. On tap, the repository transactionally stores the operation and enough input to retry; the UI can acknowledge that local acceptance. A worker then performs the remote or disk task under appropriate constraints. Worker invocations can repeat, process death can happen at every step, and a network timeout can leave uncertain server state, so I use a stable operation key, query authoritative status and advance local state only after confirmation. The ViewModel merely initiates and observes this workflow; its cancellation does not erase the persisted operation. An application scope is only useful for in-process coordination. Tests crash or cancel at each transition and assert recovery without duplicate business effects. I would separate acknowledgement from execution. Before leaving the screen, the app commits the user's intent and retry inputs to durable storage; a worker later performs the remote step under OS constraints. A crash can happen between local commit and enqueue, so startup reconciliation must discover pending records. Worker execution can repeat, so backend idempotency is essential. An application scope is sufficient only when finishing within the current process is acceptable; it cannot promise recovery after process death.”

## How to answer in the interview

- **Why:** the ViewModel only owns work while its screen owner exists.
- **How:** persist retryable intent, schedule a worker, and reconcile pending rows at startup.
- **Trade-off:** WorkManager is durable scheduling, not immediate or exactly-once execution.
- **Failure case:** process death between local commit and enqueue.
- **Production solution:** idempotent backend operation and persistent state transitions.

## Deep-dive talking points

Draw crash windows before/after persistence, enqueue, send and acknowledgement; distinguish scheduling from exactly-once effects.

## Follow-up questions

- [COR-06](../cor-06/): Does application scope survive process death? **Answer:** no.
- [COR-27](../cor-27/): How handle uncertain payment status? **Answer:** reconcile by stable operation ID.

## Self-check rubric

Can I persist intent first, recover enqueue gaps, make workers repeat-safe and explain timing constraints?

## References and reviewed-on date

- [Android persistent work](https://developer.android.com/develop/background-work/background-tasks/persistent) — durable scheduling.
- [Android offline-first guidance](https://developer.android.com/topic/architecture/data-layer/offline-first) — pending writes and sync.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-13; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
