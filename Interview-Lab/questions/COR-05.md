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

Use 'launch' for fire-and-forget tasks that do not return a result, which yields a Job and throws unhandled exceptions immediately. Use 'async' when an asynchronous computation produces a result, which yields a Deferred<T> whose value is retrieved by calling await(), exposing errors at the await call site.

## Interview answer — structured

The distinction between `launch` and `async` comes down to return values and error dispatching.

I use `launch` for 'fire-and-forget' side-effect operations where the caller does not need a computed result—such as updating a database, triggering a sync, or mutating UI state. `launch` returns a `Job`, which allows me to monitor its lifecycle, await completion with `join()`, or cancel it. If an unhandled exception occurs inside `launch`, it propagates immediately up the hierarchy tree.

I use `async` when I need to compute a value asynchronously, especially when running multiple concurrent operations in parallel. `async` returns a `Deferred<T>`, which is a promise of a future value. Calling `await()` suspends until the value is ready and returns it.

A critical pitfall to avoid is calling `await()` immediately on the same line as `async`. That forces sequential execution. To get true concurrency, you must start all `async` deferreds first, and only then await their results.

## Interview answer — deep senior

Under the hood, `launch` creates a `StandaloneCoroutine`, whereas `async` creates a `DeferredCoroutine<T>`. This architectural difference heavily impacts exception behavior. In a root coroutine created with `async` outside of structured supervision, uncaught exceptions are encapsulated inside the `Deferred` object and will not be thrown until `await()` is invoked. If the caller never calls `await()`, the exception could be silently dropped.

However, within structured concurrency (like inside `coroutineScope { }`), `async` failures behave differently: the moment an `async` child fails, its uncaught exception cancels its parent and all sibling coroutines immediately, regardless of whether `await()` was called.

From a performance perspective, `async` allocates both a `DeferredCoroutine` and a result completion object in the heap. Therefore, using `async` purely to trigger a side effect without needing a return value wastes memory; `launch` is always the leaner and more idiomatic choice for non-returning tasks.

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
