---
id: "PAY-13"
question: "A timeout handler exits the UI before enqueueing a reversal. How do you redesign ownership and ordering?"
topic: "Bonus: Payment/POS & Security Scenarios"
code: "PAY"
group: "C"
phase: 5
priority: "P2"
order: 483
editorial_status: "reviewed"
---

# PAY-13

## Original interview question

A timeout handler exits the UI before enqueueing a reversal. How do you redesign ownership and ordering?

## What the interviewer evaluates

- Ownership of timeout/reversal beyond an Activity lifecycle.
- Ordering of durable intent before UI exit.

## Explanation in Arabic

معالج نفاد الوقت (Timeout Handler) يغلق شاشة الواجهة (UI) قبل إدراج طلب العكس (Reversal) في الطابور، مما يفقد العملية. كيف تعيد هندسة الملكية والترتيب المعماري لحل المشكلة؟

1. تشريح العطل المعماري (Architectural Root Cause):
   - **خلل الملكية (Ownership Flaw)**: تم ربط منطق الدفع والعكس بدورة حياة واجهة المستخدم (Activity / Fragment / `viewModelScope`).
   - **خلل الترتيب (Ordering Flaw)**: عند نفاد مهلة الـ 30 ثانية، يستدعي كود الـ UI دالة `activity.finish()` أو يتنقل لشاشة الخطأ **قبل** اكتمال كتابة الـ Reversal في قاعدة البيانات!
   - عندما تنتهي الـ Activity، يقوم نظام أندرويد بإلغاء كل الـ Coroutines المرتبطة بـ `lifecycleScope`؛ فيتوقف كود إدراج الـ Reversal في منتصفه ويضيع للأبد!

2. إعادة الهندسة المعمارية الجذرية (Architectural Redesign):
   - **1. فصل ملكية المعاملات عن الواجهة (Inversion of Ownership)**:
     * لا تجعل الـ UI تملك تدفق الدفع! اجعل تدفق الدفع مملوكاً لـ **Application-Scoped Service** أو **WorkManager** يعمل بمعزل تام عن بقاء الشاشة مفتوحة أو مغلقة.
   - **2. عكس ترتيب العمليات (Durable Enqueue BEFORE UI Notification)**:
     * عند انتهاء المهلة، يقوم الكود أولاً بحفظ نية الـ Reversal ذرياً على القرص في Room (`markInDoubtAndEnqueueReversal`).
     * **بعد اكتمال الحفظ على القرص بنجاح فقط**، يتم إرسال إشعار للواجهة عبر `StateFlow` لعرض شاشة الخطأ أو إغلاق الشاشة.
   - **3. الواجهة مجرد مراقب سلبي (Passive UI Observer)**:
     * الشاشة تراقب فقط حالة المعاملة (`collectAsState()`)؛ وإذا أُغلقت الشاشة، تستمر المعاملة والـ Reversal في الخلفية دون أي تأثر.

## Practical walkthrough

إعادة هيكلة الملكية والترتيب لمنع فقدان الـ Reversals نهائياً:
```kotlin
// 1. خدمة ذات نطاق عام (Application Scope) تملك دورة حياة المعاملة وتصمد أمام إغلاق الشاشات:
@Singleton
class PaymentEngine @Inject constructor(
    @ApplicationScope private val externalScope: CoroutineScope,
    private val paymentDao: PaymentDao,
    private val paymentApi: PaymentApi,
    private val workScheduler: ReversalWorkScheduler
) {
    private val _txState = MutableSharedFlow<PaymentState>(replay = 1)
    val txState: SharedFlow<PaymentState> = _txState.asSharedFlow()

    fun executePaymentWithGuaranteedReversal(txId: String, request: PaymentRequest) {
        // يتم الإطلاق في ApplicationScope: حتى لو ماتت الـ Activity بالكامل، الكود يكمل تنفيذه!
        externalScope.launch {
            try {
                withTimeout(30_000L) {
                    val response = paymentApi.authorize(request)
                    paymentDao.markApproved(txId, response.authCode)
                    _txState.emit(PaymentState.Approved(response.authCode))
                }
            } catch (e: TimeoutCancellationException) {
                // ✅ الترتيب الحاسم: الحفظ الدائم على القرص أولاً وقبل إبلاغ الواجهة!
                paymentDao.markInDoubtAndEnqueueReversal(txId, request.toReversalPayload())
                workScheduler.triggerReversalWork()
                
                // الآن فقط نخبر الواجهة بأن العملية انتهت بمهلة وعكست بأمان:
                _txState.emit(PaymentState.TimedOutAndReversed(txId))
            }
        }
    }
}
```

## Why it matters and how it works

Activity lifecycle is too short for financial obligations. A repository transaction establishes durable state and outbox identity before emitting navigation. WorkManager or a terminal service resumes processing after process death, while backend/provider deduplicates repeated sends.

## Worked example

Timeout event enters `resolveTimeout(operationId)`. The use case first records Unknown and, if protocol rules require it, a reversal intent atomically. Only after transaction success does StateFlow expose “pending reversal” and allow navigation. A startup scan repairs missed worker scheduling.

### Kotlin/Android sketch

```kotlin
// Inside repository; returns only after local obligation commits.
suspend fun onTimeout(operationId: String): PaymentState = db.withTransaction {
    val attempt = attempts.get(operationId)
    if (attempt.state.isFinal) return@withTransaction attempt.state
    attempts.markUnknown(operationId)
    if (protocol.requiresReversal(attempt)) {
        reversals.insertIfAbsent(attempt.stableReversalIntent())
    }
    PaymentState.Unknown
}
// Imports: androidx.room.withTransaction. Network send happens after commit.
// isFinal/stableReversalIntent and DAOs are app-defined.
// UI can navigate after this suspend function completes.
```

## Trade-offs and decision criteria

Waiting for a durable DB commit slightly delays navigation, which is acceptable for preserving obligation. Enqueueing only a WorkManager request without domain state may not capture original references or guarantee consistent status.

## Failure modes

Coroutine launched in `lifecycleScope` is canceled when the Activity exits before enqueue. Moving it to `viewModelScope` still fails on process death. Persist state before UI completion and test kill between every line.

## Production perspective

Tests assert no navigation completion before DB commit, that reboot resumes the outbox, and that duplicate timeout callbacks create one reversal row. Metrics alert on aging pending reversals.

## Interview answer — short

Redesign ownership and ordering by decoupling payment execution from the UI lifecycle into an Application-scoped coroutine or WorkManager, and inverting operation order so the reversal intent is durably committed to SQLite before the UI is notified or dismissed.

## Interview answer — structured

Coupling financial reversal persistence to ephemeral Android UI component lifecycles represents a catastrophic anti-pattern:

1. **Root-Cause Flaws**:
   - **Fragile Ownership**: Launching payment coroutines within `lifecycleScope` or UI ViewModels binds business logic to the screen. When a timeout occurs and the user or handler executes `finish()`, the lifecycle cancels all active coroutine jobs, silently aborting incomplete database inserts.
   - **Inverted Sequencing**: Notifying the UI before completing disk persistence creates a race condition where the screen tears down the process while the disk write is in-flight.

2. **Architectural Redesign Blueprint**:
   - **Inversion of Ownership**: Transfer transaction ownership to a singleton `PaymentEngine` backed by an uncancelled `ApplicationScope` or persistent WorkManager. Transaction execution continues unhindered regardless of UI navigation, orientation changes, or screen dismissals.
   - **Strict Persistence-First Sequencing**: Upon timeout detection, the engine must atomically commit the in-doubt state and reversal payload to SQLite *first* (`paymentDao.markInDoubtAndEnqueueReversal()`). Only after disk confirmation does it emit state updates to UI observers.
   - **Passive State-Driven UI**: The UI becomes a purely passive observer of `StateFlow<PaymentState>`. If the user closes the screen, the reversal worker still dispatches reliably in the background.

## Interview answer — deep senior

From an Android process lifecycle and Coroutines concurrency standpoint, execution boundaries must be hardened:

1. **`NonCancellable` Context Protection**: In Kotlin Coroutines, when a timeout block cancels (`TimeoutCancellationException`), standard coroutine blocks immediately terminate. Enqueuing the reversal must be wrapped in `withContext(NonCancellable)` to prevent the active cancellation exception from aborting the emergency database commit.

2. **Handling Low-Memory Process Termination (LMK)**: Even an `ApplicationScope` will not survive if Android's Low Memory Killer terminates the OS process due to RAM pressure. Pairing `ApplicationScope` with an immediate WorkManager job registration (`ExistingWorkPolicy.REPLACE`) guarantees that if the process is killed mid-write, the Android OS will reschedule and execute the reversal upon system recovery.

3. **UI Event Back-Pressure**: If the UI exits during timeout, prevent the user from immediately re-entering the checkout flow until the background engine confirms the reversal intent has been durably secured.

## How to answer in the interview

- **Why:** Activity lifetime is shorter than a financial obligation.
- **How:** commit state and outbox before emitting a navigation-ready state.
- **Trade-off:** the UI may wait for a small local commit before exiting.
- **Failure case:** handler navigates away before queue insertion.
- **Production solution:** repository ownership, worker from durable rows, and crash-window tests.

## Deep-dive talking points

Prompt for Activity lifecycle limit, DB-before-navigation ordering, outbox scan and duplicate timeout race.

## Follow-up questions

- **Interviewer:** "Why must reversal enqueueing logic be wrapped in `withContext(NonCancellable)` inside a timeout catch block?"
  **Answer:** "Because a timeout cancellation exception cancels the coroutine context, which would abort regular database writes unless protected by `NonCancellable`."

- **Interviewer:** "What is the danger of binding transaction execution to `viewModelScope`?"
  **Answer:** "If the user navigates away or the ViewModel is cleared, the scope is cancelled, dropping in-flight transaction and reversal operations."

## Self-check rubric

Can I identify the race and reassign ownership to durable domain state?

## References and reviewed-on date

- [Android lifecycle-aware coroutines](https://developer.android.com/topic/libraries/architecture/coroutines) — scope lifetimes.
- [Android WorkManager overview](https://developer.android.com/topic/libraries/architecture/workmanager) — persistent work.

Technically reviewed against primary documentation on 2026-10-13.
