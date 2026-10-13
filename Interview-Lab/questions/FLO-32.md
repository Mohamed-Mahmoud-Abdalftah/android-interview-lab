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

runCatching catches all Throwables including CancellationException. This swallows coroutines' cooperative cancellation signals, converting cancellations into regular failures, breaking structured concurrency, leaking background tasks, and causing operators like withTimeout and flatMapLatest to malfunction.

## Interview answer — structured

Using `kotlin.runCatching` around cancellable coroutine or flow work is a well-documented antipattern because it fundamentally breaks structured concurrency.

`runCatching` is implemented with an indiscriminate `catch (e: Throwable)`. In Kotlin Coroutines, cooperative cancellation is driven by throwing `CancellationException`. Because `CancellationException` inherits from `Throwable`, `runCatching` intercepts the cancellation signal and encapsulates it as a `Result.failure(cancellationException)`.

This causes catastrophic side effects:

1. The coroutine refuses to terminate, continuing to execute subsequent statements when it was supposed to stop.
2. Operators that rely on cancellation—such as `withTimeout`, `collectLatest`, and `debounce`—fail to work properly.

In production, we strictly forbid `runCatching` on suspend functions, replacing it with a custom `runSuspendCatching` helper or standard `try-catch` blocks that explicitly rethrow `CancellationException`.

## Interview answer — deep senior

Under the hood, why was `runCatching` designed this way in the Kotlin standard library?

Because `kotlin.Result` was introduced as a general JVM feature, independent of the coroutines library. When coroutines adopted `CancellationException` as a control-flow unwinding mechanism, the two APIs came into conflict.

Consider what happens inside a Flow pipeline:

```kotlin
flow.map {
    runCatching { api.call(it) } // CATCHES CANCELLATION!
}
```

If the collector cancels, `api.call(it)` throws `CancellationException`. `runCatching` catches it, treats it as an error, and downstream receives `Result.failure`. The downstream collector then attempts to process this 'failure', triggering secondary bugs like showing an error snackbar for a screen that the user voluntarily closed!

In enterprise codebases, we enforce a Detekt static analysis rule: flagging any invocation of `kotlin.runCatching` containing a suspending call.

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
