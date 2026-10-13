---
id: "COR-15"
question: "How do launch exceptions differ from async exceptions?"
topic: "Kotlin Coroutines & Concurrency"
code: "COR"
group: "B"
phase: 1
priority: "P1"
order: 96
editorial_status: "reviewed"
---

# COR-15

## Original interview question

How do launch exceptions differ from async exceptions?

## What the interviewer evaluates

Can the candidate compare the observation of `launch` and `async` exceptions while preserving structured failure propagation?

## Explanation in Arabic

الفارق الجوهري في معالجة الاستثناءات بين `launch` و `async` هو من أهم الأسئلة التي تميز الفهم العميق لـ Kotlin Coroutines:

1. استثناءات دالة `launch` (Eager Exception Propagation):
   - `launch` مصممة كـ Fire-and-Forget.
   - أي Uncaught Exception بيحدث داخلها **يتم رميه فوراً للأعلى (Eagerly Thrown)**.
   - يصعد للـ Parent Job، يلغي الـ Scope، ويصل للـ `CoroutineExceptionHandler` أو يوقع التطبيق بـ Crash لو لم يتم التقاطه داخل الـ Coroutine نفسه عبر `try-catch`.

2. استثناءات دالة `async` (Deferred / Encapsulated Exception Propagation):
   - `async` مصممة لحساب نتيجة وإرجاعها في المستقبل كائن `Deferred<T>`.
   - **في Root Coroutines:** لو أطلقت `val deferred = scope.async { throw Exception() }`، الاستثناء بيتم كتمه وتغليفه داخل كائن `Deferred`. لن يتم رمي الاستثناء إلا عندما ينادي المستدعي `deferred.await()`! إذا لم تنادِ `await()`، الاستثناء لن يُرمى أبداً!
   - **داخل `coroutineScope` (الفخ الأكبر):** لو استدعيت `async` كـ Child داخل `coroutineScope`، حتى لو لم تنادِ `await()`، الاستثناء سيلغي الـ `coroutineScope` ويلغي باقي الإخوة فوراً بمجرد حدوثه!

## Practical walkthrough

مقارنة عملية توضح الفرق في الكود:
```kotlin
// 1. سلوك launch:
viewModelScope.launch {
    throw IllegalStateException("Error A") // يرمى فوراً ويلغي viewModelScope لو لم يكن supervisor!
}

// 2. سلوك async كـ Root (خارج structured scope عادي):
val deferred = scope.async {
    throw IllegalStateException("Error B") // يتم تخزينه داخل deferred بهدوء
}
// لن تشعر بأي استثناء حتى تكتب:
try {
    deferred.await() // هنا فقط يتم رمي IllegalStateException("Error B")!
} catch (e: Exception) {
    println("Caught from await: $e")
}
```

## Why it matters and how it works

Root `launch` reports an uncaught exception through a handler/default handling. Root `async` stores exception until awaited. Inside a normal structured parent, child failure cancels the parent regardless of builder. A supervisor isolates sibling cancellation, but callers must still await or otherwise account for `Deferred` outcomes.

## Worked example

JVM illustration with injected suspending operation; local result mapping is inside the child so partial success is explicit.

```kotlin
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.async
import kotlinx.coroutines.supervisorScope

suspend fun <T> attempt(operation: suspend () -> T): Result<T> =
    supervisorScope {
        async {
            try { Result.success(operation()) }
            catch (e: CancellationException) { throw e }
            catch (e: Exception) { Result.failure(e) }
        }.await()
    }
```

## Trade-offs and decision criteria

Use `launch` for an owned task with no return value and an error route; use `async` for a value that will be awaited. A direct suspend call is simpler when no parallelism is needed. Supervision is appropriate only when independent failures are meaningful.

## Failure modes

Wrapping only `await` in try/catch under `coroutineScope` may not preserve siblings: the failed child can cancel the parent first. A `launch` that throws in a supervised scope without handling can still produce an uncaught exception and leave its UI card unresolved.

## Production perspective

A dashboard requests independent badges using supervised `async` and captures each `Result` inside each child. A payment confirmation uses a direct suspend call with a typed server response, avoiding a detached launch whose failure nobody observes.

## Interview answer — short

Exceptions in 'launch' propagate eagerly and immediately up the job hierarchy to the parent and uncaught exception handlers. Exceptions in root 'async' coroutines are encapsulated inside the Deferred object and are only rethrown when await() is called.

## Interview answer — structured

The key difference lies in timing and delivery: exceptions in `launch` are treated as immediate unhandled failures, whereas exceptions in `async` are encapsulated into the return value until observed.

When a coroutine launched with `launch` encounters an unhandled exception, it treats it like an uncaught exception in a thread: it immediately propagates up to its parent, cancels its scope, and delegates to a `CoroutineExceptionHandler` or crashes the process.

When a root coroutine launched with `async` throws an exception, the exception is stored inside the resulting `Deferred<T>` instance. It remains dormant and unthrown until the caller invokes `deferred.await()`, at which point `await()` rethrows the original exception. This allows the caller to handle failures locally using a standard `try-catch` block around `await()`.

## Interview answer — deep senior

There is a crucial architectural nuance that trips up many engineers: **the context of `async` determines whether it behaves quietly or eagerly**.

If `async` is launched as a child inside a standard `coroutineScope { }`:

```kotlin
coroutineScope {
    val task = async { throw NetworkException() }
}
```

Even if you never call `task.await()`, the moment the child `async` fails, it signals failure to its parent `coroutineScope`. The parent immediately cancels all other siblings and rethrows the `NetworkException`. Wrapping `task.await()` in a `try-catch` will catch the exception locally, but the parent `coroutineScope` has already been destroyed!

To catch an `async` exception locally with `try-catch` around `await()` without cancelling sibling operations, you must run the operations inside a `supervisorScope { }`.

## How to answer in the interview

- **Why:** builders expose different observation APIs.
- **How:** launch exposes completion through Job; async exposes value and failure through Deferred.await.
- **Trade-off:** async is right for a needed value, not a universal error shield.
- **Failure case:** an unawaited async child still cancels a normal parent.
- **Production solution:** catch expected errors inside optional children and preserve CancellationException.

## Deep-dive talking points

Compare root and child cases, then draw failure propagation for `async` under a normal parent and under supervision.

## Follow-up questions

- **Interviewer:** "What happens if you never call `await()` on a failing root `async` coroutine?"
  **Answer:** "If it is a root coroutine (e.g., launched on an independent scope with SupervisorJob), the exception is completely swallowed and never thrown, leading to silent failures that are difficult to debug."

- **Interviewer:** "How do you handle multiple `async` tasks where one might fail?"
  **Answer:** "Run them inside `supervisorScope`, wrap each `deferred.await()` in individual `try-catch` blocks or use `runCatching { deferred.await() }`, allowing you to handle partial failures gracefully."

- **Interviewer:** "Does `CoroutineExceptionHandler` catch exceptions from `async`?"
  **Answer:** "No, never. CEH only handles unhandled exceptions from `launch`. Because `async` stores its exception in the Deferred object, it is considered handled by design until await is called."

## Self-check rubric

Can I state both result handles, predict parent cancellation, and design explicit observation for either builder?

## References and reviewed-on date

- [Coroutine exceptions](https://kotlinlang.org/docs/exception-handling.html) — root builders and child propagation.
- [Kotlin coroutines basics](https://kotlinlang.org/docs/coroutines-basics.html) — Job versus Deferred.

Technically reviewed against primary documentation on 2026-10-13.
