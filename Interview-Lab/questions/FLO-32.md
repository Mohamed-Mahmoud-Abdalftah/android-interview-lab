---
id: "FLO-32"
question: "What is the danger of using runCatching around cancellable flow/coroutine work?"
topic: "Flow, StateFlow, SharedFlow & Channels"
code: "FLO"
group: "C"
phase: 1
priority: "P1"
order: 145
editorial_status: "reviewed"
---

# FLO-32

## Original interview question

What is the danger of using runCatching around cancellable flow/coroutine work?

## What the interviewer evaluates

Explain runCatching swallowing cancellation and how to preserve structured shutdown.

## Concept and technical explanation

Using Kotlin's standard library runCatching { } block around suspending coroutine invocations or flow operations represents a catastrophic anti-pattern that sabotages structured concurrency and leaks background processes.
Under structured concurrency, coroutine cancellation operates cooperatively by throwing a specialized CancellationException through the coroutine hierarchy. When a coroutine scope (such as viewModelScope or lifecycleScope) is cancelled, all child jobs receive cancellation signals via this exception.
The standard runCatching function catches Throwable—the root of the exception hierarchy—which unconditionally intercepts and swallows CancellationException. Consequently, the exception is encapsulated inside a Result.failure instead of propagating upward to the coroutine dispatcher.
Swallowing CancellationException prevents the coroutine runtime from transitioning the Job into the CANCELLED state, causing background loops to continue executing undead, leaking CPU threads, network sockets, and hardware sensors, and causing subtle state corruption bugs.

## Practical walkthrough (English)

Mitigating runCatching cancellation swallowing with runCatchingCancellable:
```kotlin
// ❌ CATASTROPHIC ANTI-PATTERN: Swallowing CancellationException
suspend fun fetchUserDataCatastrophic(): Result<UserData> = runCatching {
    // If the screen closes, delay or api throws CancellationException:
    delay(2000L) // Or networkApi.getUser()
    networkApi.getUser()
    // runCatching catches CancellationException! The coroutine never cancels!
}

// ✅ SAFE PRODUCTION PATTERN: Explicitly rethrowing CancellationException
suspend fun fetchUserDataSafe(): Result<UserData> = runCatching {
    networkApi.getUser()
}.onFailure { throwable ->
    if (throwable is CancellationException) throw throwable // Propagate cancellation!
}

// ✅ IDIOMATIC EXTENSION: Custom runCatchingCancellable
inline fun <R> runCatchingCancellable(block: () -> R): Result<R> {
    return try {
        Result.success(block())
    } catch (e: CancellationException) {
        throw e // Re-throw to honor structured concurrency!
    } catch (e: Throwable) {
        Result.failure(e)
    }
}
```

## Explanation in Arabic

خطر استخدام `runCatching` حول كود الـ Coroutines والـ Flows هو أحد أكثر الأخطاء الخفية والمكلفة في Kotlin:

1. ما هو أصل المشكلة في `runCatching`؟
   - دالة `kotlin.runCatching { ... }` تم تصميمها لـ Standard Kotlin القديمة، وتقوم بالتقاط **`Throwable` بالكامل** (`catch (e: Throwable)`).
   - في Kotlin Coroutines، آلية الإلغاء (Cancellation Mechanism) تعتمد بالكامل على رمي **`CancellationException`**.
   - بما أن `CancellationException` تورث من `Throwable`، فإن `runCatching` **تلتقط إشارة الإلغاء وتبتلعها وتغلفها كـ `Result.failure`**!

2. النتائج الكارثية في الـ Production:
   - **كسر الـ Structured Concurrency:** الكوروتين ترفض التوقف! لو تم إلغاء الـ ViewModel أو الـ Scope، الكود يستمر في التنفيذ ويضيع الموارد.
   - **كسر المشغلات المعلقة (Operators Failure):** المشغلات التي تعتمد على الإلغاء (مثل `withTimeout`, `collectLatest`, `flatMapLatest`) تتوقف عن العمل بشكل سليم لأن الإلغاء يتم ابتلاعه!

3. الحل السليم:
   - عدم استخدام `runCatching` مع الدوال المعلقة، أو استخدام دالة مخصصة `runSuspendCatching` تعيد رمي `CancellationException` فوراً:
     `if (e is CancellationException) throw e`

## Practical walkthrough

المقارنة بين الكود المعطوب والكود المصحح:
```kotlin
// ❌ الكود الكارثي باستخدام runCatching:
suspend fun syncData() {
    runCatching {
        api.fetchUpdates() // لو تم إلغاء الـ coroutine، سيتم رمي CancellationException
    }.onFailure {
        // ابتلاع الإلغاء! الكود يظن أن السيرفر فشل، والـ coroutine لا تتوقف!
        showErrorDialog()
    }
}

// ✅ الكود المصحح والآمن مع Coroutines:
inline fun <T> runSuspendCatching(block: () -> T): Result<T> {
    return try {
        Result.success(block())
    } catch (e: CancellationException) {
        throw e // إعادة الرمي فوراً لضمان الإلغاء السليم!
    } catch (e: Throwable) {
        Result.failure(e)
    }
}
```

## Why it matters and how it works

CancellationException is control flow for a cancelled Job. `runCatching` is not coroutine-aware and catches it. A Flow `catch` operator has upstream placement rules and is transparent to downstream; custom wrappers still must avoid swallowing cancellation. Timeouts that use cancellation require narrow handling at their own boundary.

## Worked example

JVM/Android-compatible suspend wrapper; caller cancellation remains visible to its parent.

```kotlin
import kotlinx.coroutines.CancellationException

suspend fun <T> safeResult(call: suspend () -> T): Result<T> =
    try { Result.success(call()) }
    catch (e: CancellationException) { throw e }
    catch (e: Exception) { Result.failure(e) }
```

## Trade-offs and decision criteria

Typed Result can simplify expected error handling but should not absorb lifecycle cancellation or fatal errors. A narrow domain exception catch is preferable to a broad Throwable catch. For timeouts, choose whether a specific inner timeout becomes a domain result without catching outer cancellation.

## Failure modes

A flow search wrapped in bare `runCatching` may emit Error after a new query cancelled it. A retryWhen predicate that treats cancellation as transient may resubscribe an obsolete source. A catch block that logs and continues can retain work after logout.

## Production perspective

A search ViewModel cancels stale requests via flatMapLatest. Repository wrapper rethrows cancellation, so old request produces no Error state or retry. Unit tests cancel during delay and verify no further API calls or UI emissions.

## Interview answer — short

runCatching catches all Throwables including CancellationException, swallowing cancellation signals and breaking structured concurrency. This prevents cancelled coroutines from terminating, keeping undead background work, network calls, and hardware sensors running indefinitely while leaking memory and system resources.

## Interview answer — structured

RunCatching is a dangerous utility when applied to coroutines because it blindly swallows cancellation signals.

Kotlin coroutine cancellation relies on throwing CancellationException up the job hierarchy. When an Activity closes or a ViewModel clears, its CoroutineScope cancels child jobs cooperatively via this specific exception type.

In production, runCatching catches java.lang.Throwable. Because CancellationException is a subclass of Throwable, runCatching intercepts it and wraps it inside a Result.failure, treating normal cooperative cancellation as an ordinary business failure.
As for runtime consequences, the coroutine fails to recognize that it was cancelled, continuing to execute subsequent statements or infinite background loops. To maintain structured concurrency, developers must either rethrow CancellationException explicitly, use declarative Flow catch operators, or implement a custom runCatchingCancellable helper that preserves cancellation mechanics.


## Interview answer — deep senior

Under the hood in kotlinx.coroutines, cancellation is cooperative and driven by the CancellationException class, which extends java.lang.IllegalStateException (and ultimately Throwable). When a coroutine suspends at a suspension point—such as delay(), withContext(), or FlowCollector.emit()—and its parent Job has been cancelled, the suspension machinery un-suspends the continuation abnormally by throwing a CancellationException.
If this suspension point is wrapped inside runCatching { ... }, the try-catch block inside runCatching catches the CancellationException and wraps it in a Result.failure(exception). The coroutine continues running past the block instead of unwinding its call stack and terminating. If this happens inside a while(isActive) or while(true) loop, the coroutine transforms into an undead zombie process that permanently consumes CPU cycles, ignores scope disposal, and prevents the enclosing class from being garbage collected.
Furthermore, flow operators like catch { } explicitly check for CancellationException and rethrow it immediately: if (e is CancellationException) throw e. This is why standard Flow operators honor structured concurrency natively, whereas standard library runCatching destroys it.
Staff engineers create custom extension utilities like runCatchingCancellable or enforce custom Lint rules that forbid standard runCatching across all suspending functions and repository classes. By strictly isolating business error handling from coroutine infrastructure cancellation, applications guarantee that lifecycle events—such as Fragment destruction or user back-press navigation—instantly and deterministically terminate active background I/O operations.

## How to answer in the interview

- **Why:** cancellation controls structured shutdown.
- **How:** show runCatching catching Throwable and rethrow cancellation.
- **Trade-off:** typed Result must not absorb lifecycle control.
- **Failure case:** stale error or retry after query cancellation.
- **Production solution:** deterministic cancel-during-delay test.

## Deep-dive talking points

Trace CancellationException through runCatching, retryWhen, catch and inner timeout mapping.

## Follow-up questions

- **Interviewer:** "How does Kotlin Flow's `.catch { }` operator handle `CancellationException`?"
  **Answer:** "Flow's `.catch { }` operator is coroutine-aware: it explicitly rethrows `CancellationException` internally, guaranteeing that downstream cancellation unwinds properly while only intercepting real application exceptions."

- **Interviewer:** "Can you use `runCatching` if you check the exception in `onFailure`?"
  **Answer:** "You could write `.onFailure { if (it is CancellationException) throw it }`, but it is error-prone and easy for junior engineers to forget. Using a dedicated `runSuspendCatching` is much safer."

- **Interviewer:** "Does `withContext` swallow `CancellationException`?"
  **Answer:** "No. `withContext` properly rethrows `CancellationException` upon entry and exit, adhering to structured concurrency."

## Self-check rubric

Can I identify the caught Throwable, preserve parent cancellation and test no stale emission?

## References and reviewed-on date

- [Coroutine exceptions](https://kotlinlang.org/docs/exception-handling.html) — cancellation control flow.
- [Kotlin Result.runCatching API](https://kotlinlang.org/api/core/kotlin-stdlib/kotlin/run-catching.html) — catches Throwable.

Technically reviewed against primary documentation on 2026-10-13.
