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

In a standard Job, failure propagates bidirectionally: if one child fails, it cancels the parent and all sibling coroutines. In a SupervisorJob, failure propagates only downwards: a child's failure does not cancel the parent or affect sibling coroutines.

## Interview answer — structured

The difference between a standard `Job` and a `SupervisorJob` lies entirely in how failure propagates through the coroutine hierarchy.

With a standard `Job`, failure is bidirectional. If any child coroutine fails with an unhandled exception, it immediately notifies its parent. The parent cancels itself, which cascades down to cancel all other active siblings. This 'all-or-nothing' semantic is ideal for atomic transactions—for example, calling an order API and an inventory API where both must succeed together.

With a `SupervisorJob`, failure propagates only downwards. If a child coroutine fails, the `SupervisorJob` does not cancel itself, and sibling coroutines continue executing undisturbed. Only if the `SupervisorJob` itself is explicitly cancelled will all its children be cancelled.

In Android architecture, `viewModelScope` internally uses a `SupervisorJob`. This ensures that if one user action—like refreshing an avatar—throws an exception, it doesn't tear down the entire ViewModel and abort unrelated ongoing operations.

## Interview answer — deep senior

A critical interview pitfall is how developers misuse `SupervisorJob` with coroutine builders. Consider this common mistake:

```kotlin
// ❌ WRONG:
viewModelScope.launch(SupervisorJob()) {
    val deferred1 = async { fetchA() }
    val deferred2 = async { fetchB() }
}
```

Passing `SupervisorJob()` as an argument to `launch` creates a new parent job that severs structured concurrency from `viewModelScope`. Furthermore, inside the `launch` block, `launch` itself creates a regular `Job` as the parent for `deferred1` and `deferred2`. If `fetchA` fails, it still cancels `fetchB`!

To correctly supervise siblings within a suspend function, you must use the `supervisorScope { }` builder. `supervisorScope` installs a `SupervisorJob` as the parent for all coroutines launched directly within its block, isolating child failures without breaking structured concurrency.

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
