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

## Concept and technical explanation

The critical distinction between launch and async in Kotlin coroutines lies in their return abstractions and exception propagation timelines. The launch builder is a fire-and-forget orchestrator that returns a Job. Exceptions thrown inside launch propagate eagerly and immediately up the job hierarchy to the parent and thread-level uncaught exception handlers. Conversely, async returns a Deferred handle representing a future computation result. In a root coroutine, async encapsulates exceptions inside the Deferred instance, remaining dormant until the consumer explicitly invokes await, at which point the stored exception is rethrown directly into the caller's call stack. However, when async is invoked as a child inside a standard coroutineScope, its unhandled exception immediately propagates upward to cancel the parent scope, regardless of whether await was ever called.

## Practical walkthrough (English)

Comparing exception timing in launch versus root async and child async:
```kotlin
// 1. launch: Eager and immediate propagation
scope.launch {
    throw IllegalStateException("Fails immediately!") // Crashes process or hits CEH immediately
}

// 2. Root async: Exception is encapsulated until await() is called
val deferred = scope.async {
    throw IllegalStateException("Deferred failure")
}
delay(1000) // Exception remains completely silent here!
try {
    deferred.await() // The exception is rethrown right here!
} catch (e: IllegalStateException) {
    println("Caught during await: ${e.message}")
}

// 3. Child async trap: Inside coroutineScope, child async cancels parent immediately!
coroutineScope {
    val task = async { throw RuntimeException("Child async failed") }
    // Even if we NEVER call task.await(), the parent scope is cancelled right now!
}
```

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

launch exceptions propagate eagerly and immediately up the job hierarchy, triggering cancellation and uncaught exception handlers. Root async exceptions are encapsulated inside the Deferred handle and are only rethrown when await() is called. However, a child async inside coroutineScope still cancels its parent immediately even before await() is invoked.

## Interview answer — structured

The fundamental divergence between launch and async centers on exception delivery timing and result representation.

Launch is designed for fire-and-forget side effects and returns a Job. When an uncaught exception occurs inside launch, it propagates eagerly and immediately up the job hierarchy. If unhandled, it cancels the parent scope and dispatches to the CoroutineExceptionHandler or crashes the application thread.

In production, async is designed for computations that return values, producing a Deferred instance. When async operates as a root coroutine, it encapsulates unhandled exceptions inside the Deferred container. The exception remains completely dormant and unobserved until a consumer invokes await, which unpacks the result and rethrows the original exception directly at the await call site where standard try-catch blocks can recover it.

Engineers must be aware of the child async trap. When async is invoked as a child inside a standard coroutineScope, structured concurrency still applies upward failure propagation immediately, cancelling the parent and sibling coroutines even if await is never invoked.


## Interview answer — deep senior

At the lower runtime tier, launch and async instantiate StandaloneCoroutine and DeferredCoroutine respectively. Both extend AbstractCoroutine, but override exception handling hooks differently. In StandaloneCoroutine, when an unhandled exception triggers completion, handleJobException invokes handleCoroutineException immediately, escalating the failure to the context hierarchy.
DeferredCoroutine alters this contract by overriding handleJobException to return false. Instead of escalating the error, it transitions its internal state machine to CompletedExceptionally, packaging the Throwable into an internal CompletedExceptionally wrapper. When a caller subsequently invokes await, the continuation checks the state machine; if exceptionally completed, it unpacks the throwable and throws it into the caller's stack frame via recoverStackTrace, preserving both the asynchronous dispatch trace and the current suspension point.
However, this encapsulation is frequently misunderstood in the context of child hierarchies. When async is called within a standard coroutineScope, the child still notifies its parent via parentHandle.childCancelled(cause). Unless the parent is a supervisorScope or backed by a SupervisorJob, the parent Job immediately enters the Cancelling state, tearing down all sibling coroutines before the consumer ever reaches the await statement.
Staff engineers enforce strict patterns: use launch with structured exception handlers for terminal background actions; use async wrapped inside supervisorScope with local try-catch blocks around await calls when parallel tasks must be isolated; and never leave a Deferred handle un-awaited in long-lived scopes.

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
