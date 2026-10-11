---
id: "AND-07"
question: "What is process death? How is it different from configuration change?"
topic: "Android Fundamentals, Lifecycle & Context"
code: "AND"
group: "A"
phase: 1
priority: "P1"
order: 37
editorial_status: "reviewed"
---

# AND-07

## Original interview question

What is process death? How is it different from configuration change?

## What the interviewer evaluates

- Recognize that process death removes all in-memory objects, including ViewModels and singletons.
- Explain how Android can later recreate a previously stopped screen without having called its old `onDestroy()`.
- Recover UI state and external operations from durable identity instead of replaying side effects blindly.

## Explanation in Arabic

الـprocess death يعني نظام Android أنهى الـprocess بتاع التطبيق، غالبًا وهو في الخلفية عشان يوفّر memory. كل الـheap راح: Activity وViewModel وsingleton وcoroutine كلهم انتهوا، ومش لازم يوصلك callback ينظّفهم قبل الإنهاء. لما المستخدم يرجع، النظام ممكن ينشئ process وActivity جديدين ويحاول يرجّع saved state صغير. ده مختلف عن configuration change: وقتها عادة الـActivity بتتعمل من جديد لكن الـprocess عايش وViewModel ممكن يفضل. لذلك خزّن ID أو draft صغير للرجوع، وخزّن العمليات المهمة بصورة durable، وبعد restart اسأل مصدر الحقيقة عن النتيجة بدل ما تعيد الطلب تلقائيًا.

## Why it matters and how it works

Android may kill a stopped application's process to reclaim resources. No in-process scope or static field is a recovery mechanism; even a process-level singleton will be reconstructed. The system can provide a previously saved Bundle when it later recreates a task, subject to the saved-state lifecycle and exit path. Persisted app data remains on disk, while server-owned transactions must be reconciled with the server. A configuration change, by contrast, normally recreates the UI within the still-running process and retains a correctly scoped ViewModel.

## Worked example

For a receipt screen, write the server's `paymentAttemptId` to a durable local record before leaving the initiation flow. The restored ViewModel reads that ID and calls a read-only status endpoint. Only the backend decides whether the attempt succeeded. Illustrative flow: `Persist attempt ID → submit with idempotency key → process is killed → reopen → read ID → fetch server status → render receipt/pending/failure`. A small `SavedStateHandle` key may restore which receipt page was open, but is not the transaction ledger.

## Trade-offs and decision criteria

Saved state is fast and convenient for small UI reconstruction keys; it is constrained by serialization cost, size, and save timing. Room or another durable store survives process death and supports richer data, but requires schema and I/O design. WorkManager can schedule deferrable recovery work under system constraints, while opening the screen can also trigger a foreground reconciliation. Neither makes an uncertain payment outcome safe to repeat without a server idempotency and status contract.

## Failure modes

Assuming `onDestroy()` will run before process termination loses unsaved data and cleanup actions. Keeping an upload cursor or payment state only in a ViewModel makes it disappear. Reissuing a POST on screen restoration can duplicate a non-idempotent operation. Test with a real background process kill and task return; simple rotation exercises a different path. Also test when no saved Bundle is available and when the server status request times out.

## Production perspective

An offline note editor persists drafts incrementally, saves only the note ID and cursor position as lightweight UI state, and reloads the note after restart. A payment screen persists attempt identity and uses an authenticated status API. Metrics distinguish restoration failures, stale pending attempts, and duplicate-request prevention. Treat logs as potentially sensitive; do not log tokens or payment credentials while diagnosing recreation.

## Interview answer — short

“Process death is termination of the app process, typically while it is backgrounded. It removes all in-memory state, including ViewModels. A configuration change usually recreates an Activity within the same process, so a scoped ViewModel can survive. For process death I restore small UI keys from saved state and durable data from storage or the server.”

## Interview answer — structured

“Rotation commonly replaces the Activity but leaves the process alive, allowing its ViewModelStore to retain the ViewModel. Process death removes the whole process; callbacks are not a reliable opportunity to save last-minute work. I persist business data before it matters, keep a compact reconstruction key in SavedStateHandle or rememberSaveable, and reload from disk or the server. For an external operation I restore its identity and query status instead of blindly retrying. A process may be killed without `onDestroy()`, so no final callback can be the durability plan. On return, the system may provide saved UI state, but I use it as a reconstruction hint and reload durable data. The exact restoration path differs after normal task return, force-stop or a fresh launch.”
## Interview answer — deep senior

“I design restoration as a fresh process bootstrap. The UI may receive a saved Bundle for a previously stopped task, but I do not make that Bundle the source of truth or assume every exit provides it. ViewModel and dependency graph are recreated, so repositories must rebuild from durable records. For a transaction, I persist an attempt ID and idempotency key before submission, model an unknown outcome if the response is lost, and reconcile against the server on restart. I exercise a background process kill, force-stop/new launch, and rotation separately because their restoration guarantees differ. I model return as a new process bootstrap: dependency graph, ViewModels and singleton caches are new objects. A saved Bundle may recover a receipt ID or cursor position for a previously stopped task, but it may be absent after other exit paths and should not contain large business data. Before sending a payment, I persist an operation ID and immutable parameters; after restart I query the backend for status and represent a lost response as unknown. I never repeat a non-idempotent POST merely because the screen reappeared. Tests must actually kill a background process and also cover a clean launch without saved state.”
## Deep-dive talking points

Explain process importance, Bundle save timing, why `onDestroy()` is not a durability hook, ViewModel retention only across ordinary configuration recreation, and safe handling of unknown network outcomes after a restart.

## Follow-up questions

- [AND-06](../and-06/): What survives ordinary rotation? **Answer:** a properly scoped ViewModel can survive; old Activity/view instances do not.
- [AND-09](../and-09/): Can `rememberSaveable` store a payment ledger? **Answer:** no; it is for compact UI state, while durable storage and backend reconciliation own transactions.
- [PAY-02](../pay-02/): What if the client loses the payment response? **Answer:** keep the attempt identity, represent the outcome as unknown, and query the server before any safe retry.

## Self-check rubric

State exactly what process death destroys; contrast it with a configuration change; choose restoration stores for a draft, screen ID, and payment attempt; explain why `onDestroy()` is insufficient; and describe a real process-kill test.

## References and reviewed-on date

- [Activity lifecycle and process state](https://developer.android.com/guide/components/activities/activity-lifecycle) — process termination and recreation.
- [Save UI states](https://developer.android.com/topic/libraries/architecture/saving-states) — scope and limitations of saved state.
- [ViewModel overview](https://developer.android.com/topic/libraries/architecture/viewmodel) — in-memory retention boundary.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. The payment recovery flow is an architectural illustration; no server implementation was tested.
