---
id: "COR-05"
question: "Compare launch and async/await."
topic: "Kotlin Coroutines & Concurrency"
code: "COR"
group: "A"
phase: 1
priority: "P1"
order: 86
editorial_status: "reviewed"
---

# COR-05

## Original interview question

Compare launch and async/await.

## What the interviewer evaluates

Whether the candidate chooses a result-bearing `async` versus side-effect `launch`, and understands failure observation.

## Concept and technical explanation

The launch and async coroutine builders are the two primary mechanisms for creating new coroutines in Kotlin, differing fundamentally in their intent, return types, and exception propagation semantics. The launch builder is designed for fire-and-forget asynchronous tasks where the caller does not require a computed result value; it returns a Job instance that allows the caller to monitor lifecycle state, join completion, or cancel execution. Exceptions thrown inside a launch coroutine are considered uncaught failures and are immediately propagated up the Job hierarchy to the enclosing parent scope, triggering sibling cancellation and delegating to any configured CoroutineExceptionHandler or terminating the process. Conversely, the async builder is designed for concurrent computations that yield an eventual result; it returns a Deferred<T> instance, which is a lightweight future subclassing Job. The caller retrieves the computed result by calling the suspending await method. In terms of exception propagation, while an async root coroutine encapsulates exceptions within the Deferred until await is called, an async coroutine launched inside a standard coroutineScope will still propagate its failure up to the parent Job immediately upon crashing, cancelling the entire scope even before await is invoked.

## Practical walkthrough (English)

Consider a dashboard screen that triggers an analytics event while concurrently loading two independent data widgets.

Illustrating the distinct usage of launch versus async:
```kotlin
fun refreshDashboard() {
    // 1. launch: Fire-and-forget side effect, returns Job
    viewModelScope.launch {
        analyticsTracker.logEvent("dashboard_refreshed")
    }

    // 2. async: Concurrent value computations, returns Deferred<T>
    viewModelScope.launch {
        val balanceDeferred: Deferred<AccountBalance> = async(Dispatchers.IO) {
            accountApi.fetchBalance()
        }
        val notificationsDeferred: Deferred<List<Notification>> = async(Dispatchers.IO) {
            notificationApi.fetchNotifications()
        }

        // Await concurrent values in parallel
        val balance = balanceDeferred.await()
        val notifications = notificationsDeferred.await()
        _uiState.value = DashboardUiState.Ready(balance, notifications)
    }
}
```
If fetchBalance throws an exception, the async child fails. Even if await has not yet been called on notificationsDeferred, the failure propagates up the parent Job, immediately cancelling notificationsDeferred and the parent coroutine, preventing wasted network operations.

## Explanation in Arabic

المقارنة بين `launch` و `async` بتكشف فهمك لطرق استدعاء الـ Coroutines والتعامل مع النتائج والاستثناءات:

1. دالة `launch` (Fire-and-Forget):
   - بتستخدم لما تكون عايز تبدأ عملية ومش مستني منها قيمة مرجعة (No return value).
   - بترجع كائن `Job` يُستخدم للتحكم في دورة الحياة (زي الإلغاء بـ `job.cancel()` أو الانتظار بـ `job.join()`).
   - **التعامل مع الاستثناءات (Exception Handling):** أي Uncaught Exception بيحدث داخل `launch` بيتم رميه وتصعيده فوراً للـ Parent Job والـ Uncaught Exception Handler؛ لا ينتظر أن تنادي أي دالة.

2. دالة `async` (Compute-and-Return):
   - بتستخدم لما تكون بتشغل عملية غير متزامنة وعايز ترجع منها نتيجة (Returns a computed value).
   - بترجع كائن `Deferred<T>` (وهو نوع من أنواع الـ Job).
   - للحصول على النتيجة، بتنادي الدالة المعلقة `await(): T`.
   - **التعامل مع الاستثناءات:** الاستثناء بيتم تغليفه داخل الـ `Deferred`، وبيترمي لما المتصل ينادي `await()`. لكن انتبه: في الـ Standard `coroutineScope`، حتى لو منادتش `await()`، فشل `async` هيصعد الاستثناء للأب ويلغي باقي الإخوة!

3. خطأ شائع جداً (Anti-pattern):
   - استخدام `async` لما مفيش قيمة مرجعة، أو استخدام `async` متتالي في سطرين وراء بعض بدون توازي حقيقي: `val a = async { ... }.await()` ده بيمشي تسلسلي مش متوازي!

## Practical walkthrough

في شاشة الحساب: جلب الملف الشخصي وقائمة الإشعارات بالتوازي:
- **النهج الخاطئ (Sequential async):**
  val profile = async { api.getProfile() }.await() // انتظر حتى ينتهي بالكامل أولاً!
  val notifications = async { api.getNotifications() }.await() // بدأ بعد ما الأول خلص!
  كده مفيش أي توازي؛ الكود اشتغل تسلسلي وخسرنا ميزة الـ async.
- **النهج الصحيح (True Parallelism):**
  val profileDeferred = async { api.getProfile() } // بدأ فوراً في الخلفية
  val notificationsDeferred = async { api.getNotifications() } // بدأ في نفس اللحظة بالتوازي
  // الآن ننتظر النتيجتين معاً:
  val state = UiState(profileDeferred.await(), notificationsDeferred.await())
- **متى نستخدم launch؟**
  `viewModelScope.launch { repo.logAnalyticsEvent(event) }` // عملية إرسال لا تحتاج انتظار نتيجة.

## Why it matters and how it works

Both builders start immediately by default and inherit the scope context. `join` waits for termination but does not return a value; `await` waits and retrieves the value, throwing its failure. In a normal parent scope, child failure can cancel the parent even if the `Deferred` is never awaited. Concurrent `async` calls only help when independent latency can overlap.

## Worked example

JVM example assumes `kotlinx-coroutines-core` and two main-safe suspend API functions supplied by the caller.

```kotlin
import kotlinx.coroutines.async
import kotlinx.coroutines.coroutineScope

suspend fun dashboard(
    account: suspend () -> String,
    alerts: suspend () -> Int,
): Pair<String, Int> = coroutineScope {
    val a = async { account() }
    val n = async { alerts() }
    a.await() to n.await()
}
```

## Trade-offs and decision criteria

Use `async` for concurrent values, `launch` for owned work where only completion matters, and a direct suspend call for sequential work. Excess parallelism can overload an API; set limits when fan-out grows. Do not use `async` just to rename a sequential operation.

## Failure modes

`try/catch` around a later `await` may be too late to prevent a normal parent from being cancelled by an earlier child failure. Use a supervised boundary for independent failures, or catch inside the child to produce a typed result; always rethrow cancellation.

## Production perspective

A home screen fetches account and notification count concurrently because the APIs are independent and both are needed for the complete header. The ViewModel owns the call and cancellation; the repository returns a pair or a typed failure, while telemetry records which dependency failed.

## Interview answer — short

launch is a fire-and-forget coroutine builder returning a Job for operations where no value is returned, propagating uncaught exceptions immediately up the Job hierarchy. async is for concurrent computations returning a Deferred<T>, allowing callers to retrieve the result via await. Within a standard scope, async exceptions still cancel the parent hierarchy immediately.

## Interview answer — structured

The core distinction between launch and async centers on whether the asynchronous operation produces a computational result or performs a fire-and-forget action.

Launch returns a Job that represents the running task, making it ideal for background operations such as logging analytics, caching database entries, or firing UI notifications where the caller only cares about completion status.

In production, async returns a Deferred instance, which represents a promise of an eventual value retrieved through the suspending await method. We use async primarily when decomposing a complex screen into parallel network calls that need to be aggregated together.

Exception handling differs significantly. Uncaught exceptions in launch immediately propagate up the parent Job hierarchy. With async, while exceptions are thrown when calling await, an unhandled failure in an async child inside a standard scope still cancels the parent Job and all siblings immediately, unless wrapped in a supervisorScope.


## Interview answer — deep senior

Under the hood, launch creates a StandaloneCoroutine instance, whereas async creates a DeferredCoroutine instance. Both inherit the CoroutineScope context and instantiate a child Job linked to the parent. However, their internal completion and exception reporting logic diverges markedly in the handleJobException method.

In a StandaloneCoroutine created by launch, an unhandled exception thrown in the coroutine body causes the coroutine to cancel itself and call parentContext.handleCoroutineException(exception). The failure traverses directly up to the root Job. If no supervisor boundary exists, the root coroutine either delegates the exception to an installed CoroutineExceptionHandler or passes it to the thread default uncaught exception handler, crashing the Android runtime.

In contrast, a DeferredCoroutine created by async stores the resulting outcome—whether a value or an exception—inside its internal state. When await is called, the state is evaluated: if the computation completed normally, the value is returned; if it completed exceptionally, await unpacks and re-throws the original exception. However, a critical pitfall in Kotlin coroutines is assuming that wrapping await in a try-catch block protects the scope from cancellation. Inside a regular coroutineScope, the Deferred child notifies its parent of failure immediately upon crashing. By the time await throws the exception in the caller, the parent Job is already in the Cancelling state, and all siblings have been cancelled.

To achieve true resilience when using async for parallel operations where one failure should not cancel the others, senior engineers wrap the parallel operations in supervisorScope or invoke supervisorScope with individual try-catch blocks around each await call.

## How to answer in the interview

- **Why:** choose a builder by whether the caller needs a value.
- **How:** launch returns Job; async returns Deferred and await rethrows its stored failure.
- **Trade-off:** parallel reads may reduce latency but consume capacity.
- **Failure case:** unawaited Deferred or a late catch after parent cancellation.
- **Production solution:** use direct suspend calls for sequential work and explicit supervised outcomes for optional results.

## Deep-dive talking points

Explain eager start, `join` versus `await`, ordinary parent failure, lazy start caveats, and when parallel latency really helps.

## Follow-up questions

- **Interviewer:** "What happens if an `async` coroutine fails and you wrap `deferred.await()` in a `try-catch`?"
  **Answer:** "If you are inside a standard `coroutineScope`, wrapping `deferred.await()` in `try-catch` catches the exception locally at the call site, but the parent `coroutineScope` has already been cancelled by the failure of the child! To catch child exceptions locally without cancelling siblings, you must use `supervisorScope`."

- **Interviewer:** "Can you await multiple Deferred instances concurrently?"
  **Answer:** "Yes, using the `awaitAll()` extension function on a collection of Deferreds (e.g., `listOf(task1, task2).awaitAll()`). It awaits all results concurrently and returns a `List<T>`, failing fast if any of the tasks throw an exception."

- **Interviewer:** "What is `CoroutineStart.LAZY` and how does it affect `async`?"
  **Answer:** "By default, `async` starts executing immediately. When started with `CoroutineStart.LAZY`, the coroutine does not start executing until you either explicitly call `deferred.start()` or call `deferred.await()`. Calling `await()` on two lazy async blocks sequentially will run them sequentially rather than in parallel."

## Self-check rubric

Can I choose the right builder, predict result and exception behavior, justify concurrency, and describe an Android owner?

## References and reviewed-on date

- [Kotlin coroutines basics](https://kotlinlang.org/docs/coroutines-basics.html) — `launch`, `async`, Job and Deferred.
- [Coroutine exceptions](https://kotlinlang.org/docs/exception-handling.html) — failure observation and propagation.

Technically reviewed against primary documentation on 2026-10-13.
