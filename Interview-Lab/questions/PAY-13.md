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

## Concept and technical explanation

Allowing a UI presentation timeout handler to dismiss the screen or cancel coroutines before a financial reversal is durably enqueued creates an orphaned hold vulnerability:
- The Flawed Architecture (UI-Owned Financial Lifecycle):
  - In flawed architectures, the financial transaction and reversal logic reside inside an Activity or ViewModel `viewModelScope`.
  - When a timeout occurs, the UI layer catches the timeout, immediately pops the backstack or navigates away, terminating the coroutine scope before the background network reversal request can be scheduled or dispatched.
  - Consequence: The customer's funds remain held at the issuing bank indefinitely; the app never retries because the task was bound to the dead UI component.
- The Redesigned Architecture (Application-Owned Coordination):
  1. Separation of Concerns & Ownership Inversion:
     - The financial state machine and reversal queue belong to a singleton Application-scoped Coordinator (`applicationScope` / persistent `PaymentRepository`), completely independent of Android Activity or ViewModel lifecycles.
     - The ViewModel acts purely as an observer, collecting state from a domain `StateFlow`.
  2. Inverted Transactional Ordering (Write Intent First):
     - Order of Operations:
       1. Timeout detected at the domain repository layer.
       2. The repository updates the transaction to `IN_DOUBT` and commits the reversal record into the persistent SQLite `reversal_queue` table inside a single atomic database transaction.
       3. Only *after* the local database confirms durable disk persistence does the repository emit the `Timeout` state to the UI.
     - Even if the user destroys the Activity, powers off the screen, or Android kills the UI process, the reversal intent is already safely burned into flash memory, ready for background dispatch.

## Practical walkthrough (English)

Redesigning ownership and transactional ordering for payment timeouts in Kotlin:
```kotlin
// 1. Domain Coordinator owned by Application Scope, NOT ViewModel
class PaymentCoordinator(
    private val appScope: CoroutineScope, // Injected ApplicationScope (SupervisorJob + Dispatchers.Default)
    private val appDatabase: AppDatabase,
    private val journalDao: PaymentJournalDao,
    private val reversalDao: ReversalDao,
    private val paymentGatewayApi: PaymentGatewayApi
) {
    private val _paymentState = MutableStateFlow<PaymentState>(PaymentState.Idle)
    val paymentState: StateFlow<PaymentState> = _paymentState.asStateFlow()

    fun executeTransaction(orderId: String, amount: Long) {
        // Launch in ApplicationScope: Outlives UI teardown and screen navigation
        appScope.launch {
            _paymentState.value = PaymentState.Processing

            try {
                withTimeout(20_000L) {
                    val auth = paymentGatewayApi.authorize(orderId, amount)
                    _paymentState.value = PaymentState.Approved(auth.code)
                }
            } catch (e: TimeoutCancellationException) {
                // CRITICAL ORDERING: Commit to disk FIRST before notifying UI
                appDatabase.withTransaction {
                    journalDao.markInDoubt(orderId)
                    reversalDao.insert(ReversalEntity(orderId, amount, System.currentTimeMillis()))
                }

                // Safe to notify UI now: Reversal intent is already durably persisted
                _paymentState.value = PaymentState.InDoubtTimeout
            }
        }
    }
}
```

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

Redesign ownership and ordering by decoupling the payment lifecycle from the UI, moving coordination into an Application-scoped repository. Invert the operational sequence: when a timeout occurs, durably persist the in-doubt state and reversal queue entry inside an atomic SQLite transaction first, and only notify the UI after disk commit succeeds.

## Interview answer — structured

Allowing a UI timeout to dismiss a screen before enqueueing a reversal causes catastrophic orphaned holds.
This flaw occurs when financial logic is coupled to UI lifecycles like ViewModel scopes. If a timeout timer cancels the scope or the user navigates away, execution terminates prematurely, leaving the customer's funds locked at the bank without a reversal.
To correct this, we execute an ownership redesign and an ordering inversion.
First, we transfer ownership of the payment state machine from the UI to an application-scoped domain coordinator. The coordinator runs in a persistent application coroutine scope or background service that survives Activity destruction. The UI simply observes state updates.
Second, we invert the execution ordering. When a network timeout occurs, the coordinator never notifies the UI immediately. Instead, it executes an atomic SQLite transaction that updates the transaction status to in-doubt and inserts a reversal task into the persistent queue table.
Only after the database write is confirmed does the coordinator emit the timeout state to the UI, guaranteeing that user navigation can never abort reversal dispatch.

## Interview answer — deep senior

From a software architecture, reactive state boundaries, and financial mission-critical resilience perspective, coupling payment execution to Android UI lifecycles is an architectural anti-pattern that directly causes ledger desynchronization.
Activities and Fragments in Android are inherently ephemeral: they are destroyed and recreated during screen rotations, configuration changes, user back-presses, and system memory pressure. If a payment flow is launched inside viewModelScope and the timeout handler immediately triggers a navigation event like findNavController().popBackStack(), Android cancels the active coroutine job. Any subsequent code intended to enqueue a reversal task in Room or dispatch an ISO 8583 0400 cancellation is dropped mid-execution. The cardholder's account remains charged with an orphaned authorization hold, and the system loses all automated recovery momentum.
The senior architectural solution enforces two uncompromising principles: Application Scope Ownership and Inverted Transactional Ordering.
We decouple the transaction coordinator entirely from the UI layer, injecting an ApplicationScope backed by a SupervisorJob. The ViewModel becomes a passive presentation observer that exposes a StateFlow to Compose or XML views.
Furthermore, we enforce strict ordering invariants. When a timeout occurs, the domain engine catches the exception and immediately enters an atomic SQLite transaction using Room withTransaction. It updates the payment journal record to IN_DOUBT and inserts a persistent reversal task into the reversal_queue table.
Only after the Linux kernel flushes the SQLite Write-Ahead Log to physical NAND storage does the coordinator emit the Timeout UI state.
Even if the user vigorously mashes the home button, swipes away the app, or unplugs the POS device, the reversal intent has already been durably anchored to disk, ensuring that background workers will reliably dispatch the reversal to the bank switch.

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
