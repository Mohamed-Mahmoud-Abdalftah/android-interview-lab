---
id: "COR-12"
question: "Compare Job and SupervisorJob."
topic: "Kotlin Coroutines & Concurrency"
code: "COR"
group: "B"
phase: 1
priority: "P1"
order: 93
editorial_status: "reviewed"
---

# COR-12

## Original interview question

Compare Job and SupervisorJob.

## What the interviewer evaluates

Whether the candidate can distinguish a Job hierarchy element from the `supervisorScope` builder and reason about child failure.

## Concept and technical explanation

In Kotlin's structured concurrency model, Job and SupervisorJob are the core implementations of the Job interface governing lifecycle, state management, and cancellation propagation. A standard Job enforces bidirectional cancellation propagation: if any child coroutine fails with an unhandled exception, that failure cancels the parent Job, which subsequently cancels all remaining child coroutines attached to it. This guarantees that operations operate as unified transactions where partial work is discarded upon error. A SupervisorJob alters this contract by enforcing unidirectional cancellation propagation: cancellation cascades downwards from the supervisor to its children, but failures within child coroutines do not propagate upwards to cancel the SupervisorJob or sibling jobs. This fault-isolation mechanism allows long-lived controllers, such as Android ViewModels and Application services, to execute independent concurrent tasks without allowing one failing routine to destroy the entire lifecycle scope.

## Practical walkthrough (English)

Demonstrating cancellation differences and the common parent-context trap:
```kotlin
// 1. Pitfall: Passing SupervisorJob directly as a context argument to a child builder
val scope = CoroutineScope(Dispatchers.Default)
scope.launch(SupervisorJob()) { // Ineffective: this creates a detached supervisor that is immediately overwritten!
    launch { throw RuntimeException("Child A died") }
    launch { delay(1000); println("Child B survived") } // Cancelled anyway because the parent launch is a standard Job!
}

// 2. Production Pattern: SupervisorJob at the scope root
class OrderManager : CoroutineScope {
    private val supervisor = SupervisorJob()
    override val coroutineContext = Dispatchers.Default + supervisor

    fun processOrders() {
        launch { syncInventory() } // Failure here does NOT cancel payment logging
        launch { logPaymentTelemetry() }
    }

    fun shutdown() {
        supervisor.cancel() // Downward cancellation terminates all active children cleanly
    }
}
```

## Explanation in Arabic

المقارنة بين `Job` و `SupervisorJob` هي أهم قاعدة في إدارة الأخطاء في شجرة الـ Coroutines (Structured Concurrency Tree):

1. الـ `Job` العادي (Standard Job - Two-way Failure Propagation):
   - العلاقة بين الأبناء والأب **ثنائية الاتجاه (Bidirectional)**.
   - لو عندك أب (Job) أطلق طفلين A و B:
     * لو الطفل A فشل برمي Exception (غير CancellationException):
     * الفشل يصعد للأب فوراً.
     * الأب يلغي نفسه.
     * الأب يقوم بإلغاء الطفل B وجميع الأطفال الآخرين!
   - الفلسفة هنا هي: **All-or-Nothing Transaction**. لو جزء من العملية فشل، كل العملية تلغى لتجنب حالة بيانات غير مكتملة.

2. الـ `SupervisorJob` (One-way Failure Propagation):
   - العلاقة بين الأبناء **أحادية الاتجاه للأسفل فقط (Downwards only)**.
   - لو الطفل A فشل ورمى Exception:
     * الفشل **لا ينتقل للأب**.
     * الأب يظل حياً ونشطاً (`isActive = true`).
     * الطفل B يستمر في العمل بدون أن يتأثر إطلاقاً!
   - الإلغاء الوحيد هو من أعلى لأسفل: لو ألغيت الأب نفسه يدوياً، كل الأطفال يلغون.

3. الفخ الشائع جداً في الـ SupervisorJob (Common Trap):
   - كتابة: `launch(SupervisorJob()) { ... }` داخل `viewModelScope`.
   - تمرير `SupervisorJob()` كـ parameter في دالة `launch` يقطع علاقة الـ Parent-Child ويجعل هذا الـ Job منفصلاً، ولا يجعل الأطفال المشتقين منه تحت إشراف supervisor كما يظن المطور!

## Practical walkthrough

في شاشة لوحة تحكم الأخبار (Dashboard Activity):
- الشاشة بتعرض: 1. حالة الطقس (Weather Widget)، 2. أسعار العملات (Stock Widget)، 3. قائمة الأخبار.
- **النهج الخاطئ باستخدام Job عادي:**
  لو خدمة أسعار العملات فشلت ورمت NetworkException، الـ Job العادي سيلغي شاشة الأخبار بالكامل وشاشة الطقس! المستخدم يرى شاشة بيضاء خالية لمجرد أن widget فرعي فشل.
- **النهج الصحيح باستخدام SupervisorJob / supervisorScope:**
  في الـ ViewModel، أو باستخدام `supervisorScope`:
  ```kotlin
  supervisorScope {
      launch { fetchWeather() } // لو فشل هنا، لن يؤثر على الأخبار
      launch { fetchStocks() }  // فشل هذا Widget يعرض Retry button فقط
      launch { fetchNews() }    // يستمر في التحميل والعرض بنجاح
  }
  ```

## Why it matters and how it works

A root `CoroutineScope(SupervisorJob() + dispatcher)` is useful for an owner with independent long-lived tasks. Each launched child still needs a failure policy; `SupervisorJob` does not catch exceptions. A parent Job passed to `SupervisorJob(parent)` retains downward cancellation from the parent. An ordinary Job is appropriate for fail-together groups.

## Worked example

Android/JVM conceptual owner; `handler` logs uncaught `launch` errors, but production should also surface task-specific failures and cancel the scope at shutdown.

```kotlin
import kotlinx.coroutines.CoroutineExceptionHandler
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.launch

class AppTaskOwner {
    private val handler = CoroutineExceptionHandler { _, error ->
        report(error)
    }
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Default + handler)
    fun start(task: suspend () -> Unit) { scope.launch { task() } }
    fun close() = scope.cancel()
    private fun report(error: Throwable) { /* log to app telemetry */ }
}
```

## Trade-offs and decision criteria

Use an ordinary Job for operations whose children form one consistent outcome; use SupervisorJob when independent tasks should not cancel one another. The latter can keep the owner running after one failure, but may conceal a persistent outage unless errors are observed and surfaced.

## Failure modes

A supervisor only prevents propagation to siblings. If `launch` fails without local handling or a suitable handler, the exception can still be reported as uncaught. If the owner forgets `close`, the scope can retain resources for the process lifetime.

## Production perspective

An application task owner runs independent cache warmers. Each job reports its failure; other warmers continue. On logout the owner cancels all tasks and creates a new session-owned scope. Critical work still goes through persistent scheduling rather than relying on this scope.

## Interview answer — short

A standard Job propagates failure bidirectionally: if any child fails, it cancels its parent and all sibling coroutines. A SupervisorJob propagates cancellation only downwards: child failures do not cancel the parent or siblings. SupervisorJob is used at scope roots to isolate independent tasks, but cancelling the supervisor itself still terminates all children.

## Interview answer — structured

The distinction between Job and SupervisorJob represents the foundation of lifecycle control and error containment in Kotlin coroutines.

A standard Job enforces bidirectional cancellation. When a child coroutine encounters an uncaught exception, it marks the parent Job as failed, causing the parent to immediately cancel all other active siblings. This fail-fast transactional design guarantees that tightly coupled subtasks do not waste device resources when a critical dependency fails.

In production, SupervisorJob implements fault isolation through unidirectional cancellation. Direct children manage their own failures independently; an uncaught exception in one child does not cancel the supervisor parent and does not interrupt sibling coroutines. This pattern forms the architectural backbone of framework scopes like Android's viewModelScope, where independent user interactions like fetching account details and tracking analytics must not interfere with each other.

Engineers must be cautious when passing SupervisorJob into builder parameters. Passing a SupervisorJob as an argument to launch creates a new job node that acts as a parent for that child's internal hierarchy, but does not convert an existing standard parent into a supervisor, often leading to surprising cancellation cascades if misconfigured.


## Interview answer — deep senior

At the runtime implementation layer, both Job and SupervisorJob rely on JobSupport, which orchestrates a strict internal state machine comprising New, Active, Completing, Cancelling, and Cancelled states. The fundamental mechanical divergence lies in how child failure callbacks are processed. In a standard Job, when a child throws a non-cancellation exception, it notifies its parent via parentHandle.childCancelled(cause). JobSupport verifies the exception, transitions its state to Cancelling, and dispatches cancellation tokens to its internal NodeList, invoking cancel on every attached child continuation before transitioning to Cancelled.
SupervisorJob alters this pipeline through its SupervisorJobImpl specialization. It overrides the childCancelled method to return false unconditionally. When an uncaught exception occurs in a child, the supervisor acknowledges the completion but does not transition into the Cancelling state, leaving its other child nodes completely untouched in their Active state.
A critical nuance often tested in staff-level interviews involves the scope of supervision. Supervision is strictly one-level deep. If a SupervisorJob has a child launched with launch, that child is by default a standard Job. If that child subsequently launches its own subroutines, any uncaught exception among those subroutines will cancel that child and all its siblings at that lower tier, because supervision does not automatically inherit down arbitrary levels of the hierarchy unless explicitly constructed with supervisorScope.
Finally, lifecycle destruction requires explicit supervision management. In custom architectural components, engineers must retain a handle to the root SupervisorJob. Invoking supervisor.cancel() cascades downward through the entire tree, ensuring complete garbage collection and socket teardown when the component is destroyed.

## How to answer in the interview

- **Why:** parent Job policy controls sibling fate.
- **How:** Job propagates ordinary child failure upward; SupervisorJob isolates direct children but still propagates parent cancellation downward.
- **Trade-off:** isolation increases responsibility to observe errors.
- **Failure case:** a supervised launch crashes through an unhandled exception.
- **Production solution:** own the scope, report task failure, and cancel it at shutdown or logout.

## Deep-dive talking points

Draw the Job tree and mark where failure propagation stops; compare root ownership, child `async` observation and parent cancellation.

## Follow-up questions

- **Interviewer:** "Who handles the exception when a child fails inside a SupervisorJob?"
  **Answer:** "Because the failure is not swallowed or propagated to the parent SupervisorJob, each child coroutine is directly responsible for its own exception. In `launch`, it must either be caught with try-catch or handled by a `CoroutineExceptionHandler` attached to that child. Otherwise, it reaches the uncaught exception handler."

- **Interviewer:** "Why does `coroutineScope` cancel siblings while `supervisorScope` does not?"
  **Answer:** "`coroutineScope` uses a standard Job to enforce atomic, all-or-nothing semantics where partial failures invalidate the whole scope. `supervisorScope` uses a SupervisorJob specifically designed for independent, concurrent sub-tasks."

- **Interviewer:** "Does `SupervisorJob` affect how cancellation propagates down when `cancel()` is called?"
  **Answer:** "No. When you call `cancel()` on a `SupervisorJob`, downward cancellation works identically to a standard Job: the supervisor and all of its active children are cancelled immediately."

## Self-check rubric

Can I distinguish element and builder, predict sibling fate, name error observation, and define scope shutdown?

## References and reviewed-on date

- [Coroutine exceptions](https://kotlinlang.org/docs/exception-handling.html) — Job and supervision.
- [Kotlin coroutines basics](https://kotlinlang.org/docs/coroutines-basics.html) — Job hierarchy.

Technically reviewed against primary documentation on 2026-10-13.
