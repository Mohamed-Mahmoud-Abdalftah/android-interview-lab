---
id: "COR-23"
question: "How do you safely adapt a callback API to suspending code?"
topic: "Kotlin Coroutines & Concurrency"
code: "COR"
group: "B"
phase: 1
priority: "P1"
order: 104
editorial_status: "reviewed"
---

# COR-23

## Original interview question

How do you safely adapt a callback API to suspending code?

## What the interviewer evaluates

Explain one-shot callback adaptation with prompt cancellation and exact-once continuation completion.

## Concept and technical explanation

Adapting legacy asynchronous callback-based APIs into idiomatic Kotlin suspending functions is a core responsibility when modernizing Android codebases. The standard, robust foundation for this transformation is suspendCancellableCoroutine. Unlike the lower-level and discouraged suspendCoroutine, suspendCancellableCoroutine provides active cancellation integration through its CancellableContinuation handle. When adapting a callback API, staff engineers must satisfy three non-negotiable correctness guarantees. First, the continuation must be resumed exactly once—either via resume(value) for successful outcomes or resumeWithException(throwable) for terminal failures. Calling resume multiple times crashes the runtime with an IllegalStateException: Already resumed. Second, the adapter must register an invokeOnCancellation handler to cleanly unregister the underlying SDK listener, close hardware handles, or abort the external call when the calling coroutine scope is cancelled. Third, race conditions between callback completion and cancellation must be handled safely, ensuring that late callbacks delivered after cancellation are ignored gracefully without throwing uncaught exceptions.

## Practical walkthrough (English)

Consider adapting a legacy third-party location SDK that delivers a single GPS fix through a listener:
```kotlin
// Erroneous implementation: leaks listener and ignores coroutine cancellation
suspend fun fetchLocationUnsafe(): Location = suspendCoroutine { continuation ->
    val listener = object : LegacyLocationListener {
        override fun onLocation(loc: Location) = continuation.resume(loc)
        override fun onError(e: Exception) = continuation.resumeWithException(e)
    }
    // BUG: Never unregisters listener if coroutine is cancelled!
    locationClient.requestLocation(listener) 
}

// Production-grade implementation using suspendCancellableCoroutine:
suspend fun fetchLocationSafe(): Location = suspendCancellableCoroutine { continuation ->
    val listener = object : LegacyLocationListener {
        override fun onLocation(loc: Location) {
            // Guard against resume races if cancelled:
            if (continuation.isActive) {
                continuation.resume(loc)
            }
        }
        override fun onError(e: Exception) {
            if (continuation.isActive) {
                continuation.resumeWithException(e)
            }
        }
    }
    locationClient.requestLocation(listener)
    
    // Automatically unregisters listener if coroutine cancels:
    continuation.invokeOnCancellation {
        locationClient.removeLocationListener(listener)
    }
}
```
If the caller's scope is cancelled while waiting for GPS satellite acquisition, invokeOnCancellation unregisters the listener immediately, shutting down the hardware GPS radio and preventing battery drain.

## Explanation in Arabic

تحويل الـ Callback APIs القديمة في Android إلى Suspending Functions هو أحد أهم الاختبارات العملية في المقابلات:

1. الأداة المعيارية: `suspendCancellableCoroutine`:
   - تُعلق الـ Coroutine وتوفر كائن `CancellableContinuation<T>`.
   - لما الـ Callback ينجح: ننادي `continuation.resume(result)`.
   - لما الـ Callback يفشل: ننادي `continuation.resumeWithException(error)`.

2. أهمية التعامل مع الإلغاء (`invokeOnCancellation`):
   - لو المتصل لغى الـ Coroutine قبل ما الـ Callback يرجع، لازم نلغي الـ Listener أو الطلب في الـ SDK الخارجي عبر `continuation.invokeOnCancellation { ... }` لمنع تسريب الذاكرة (Memory Leak) واستمرار العمليات في الخلفية.

3. تحذير خطير: تجنب `suspendCoroutine` العادية:
   - دالة `suspendCoroutine` (بدون Cancellable) لا تدعم الإلغاء! لو تم إلغاء الـ Coroutine، ستظل معلقة حتى ينتهي الـ Callback، مما يكسر مبدأ الـ Structured Concurrency.

## Practical walkthrough

تحويل Firebase أو Location Manager Callback لـ Suspend Function:
```kotlin
suspend fun FusedLocationProviderClient.awaitCurrentLocation(): Location =
    suspendCancellableCoroutine { continuation ->
        val cancellationSource = CancellationTokenSource()
        
        // 1. طلب الموقع من Google Play Services:
        getCurrentLocation(Priority.PRIORITY_HIGH_ACCURACY, cancellationSource.token)
            .addOnSuccessListener { location ->
                continuation.resume(location)
            }
            .addOnFailureListener { exception ->
                continuation.resumeWithException(exception)
            }
            
        // 2. الربط مع إلغاء الـ Coroutine لمنع تسريب الـ GPS:
        continuation.invokeOnCancellation {
            cancellationSource.cancel()
        }
    }
```

## Why it matters and how it works

The continuation can be resumed with a value or exception; cancellation can race with callback delivery. The adapter should unregister a listener or cancel the underlying call on cancellation. If callback returns a closeable resource, arrange cleanup for cancellation after delivery. For multi-shot APIs use `callbackFlow` with `awaitClose`, not a one-shot continuation.

## Worked example

Conceptual Kotlin/JVM adapter for value results that need no closing; `LegacyCall` specifies one terminal callback and cancellation, and must document whether callbacks can arrive after `cancel`. For a closeable result, use the continuation's `resume(value) { _, lostValue, _ -> lostValue.close() }` overload so prompt cancellation cannot leak the value before the caller receives it.

```kotlin
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException
import java.util.concurrent.atomic.AtomicBoolean

interface LegacyCall<T> {
    fun start(done: (Result<T>) -> Unit)
    fun cancel()
}

suspend fun <T> LegacyCall<T>.await(): T = suspendCancellableCoroutine { cont ->
    val terminal = AtomicBoolean(false)
    cont.invokeOnCancellation { terminal.set(true); cancel() }
    start { result ->
        if (terminal.compareAndSet(false, true)) {
            result.fold(
                onSuccess = { cont.resume(it) },
                onFailure = { cont.resumeWithException(it) },
            )
        }
    }
}
```

## Trade-offs and decision criteria

One-shot adapters are concise but the legacy API’s callback contract matters: duplicate callbacks need a stronger single-completion guard than `isActive` alone. Multi-shot listeners belong in Flow. Prefer an existing maintained suspending library adapter when available.

## Failure modes

Two callbacks can both observe `isActive` before either resumes and race to resume twice. Cancellation may not stop server side effects. A callback invoked synchronously during registration can make cleanup ordering tricky; test immediate success, failure, cancel and late callback.

## Production perspective

A location SDK adapter unregisters its one-time listener on ViewModel cancellation. The repository exposes a suspending result and tests immediate and delayed callback races with a fake SDK. Permission loss is mapped to a domain error, not cancellation.

## Interview answer — short

suspendCancellableCoroutine bridges callback APIs to suspending functions with full cancellation support. It provides a CancellableContinuation that must be resumed exactly once via resume or resumeWithException. It allows registering invokeOnCancellation to unregister SDK listeners or close hardware resources when cancelled. Unlike suspendCoroutine, it prevents memory leaks and guarantees prompt cancellation.

## Interview answer — structured

Adapting asynchronous callback interfaces into suspending functions is the standard approach for integrating legacy SDKs into modern Kotlin coroutine architectures. The primary API for this task is suspendCancellableCoroutine, which suspends the calling coroutine and exposes a CancellableContinuation handle.

The implementation must guarantee exact-once completion. The callback must invoke either continuation.resume or continuation.resumeWithException precisely once, because calling resume multiple times violates runtime invariants and throws an IllegalStateException.

In production, cancellation management is paramount. By invoking continuation.invokeOnCancellation, we install a teardown hook that unregisters the callback listener, cancels the underlying SDK request, or releases system hardware when the calling scope is cancelled.

Engineers must avoid legacy suspendCoroutine, which lacks cancellation awareness. If a coroutine wrapping suspendCoroutine is cancelled, it hangs in the background awaiting the callback, leaking listeners, Context references, and device battery.


## Interview answer — deep senior

At the compiler and runtime execution level, suspendCancellableCoroutine instantiates a CancellableContinuationImpl, transitioning its state into Suspended and intercepting parent job cancellation signals. When the parent scope cancels, the continuation transitions atomically to the Cancelled state and immediately dispatches its invokeOnCancellation handlers. A subtle concurrency bug in naive callback adapters is the completion-cancellation race. Because the external callback might fire on an arbitrary binder or SDK worker thread at the exact moment the coroutine scope is cancelled on the Main thread, calling continuation.resume directly can result in an IllegalStateException if the continuation has already transitioned to Cancelled. To handle this reliably, check continuation.isActive before resuming, or wrap the callback in an atomic one-shot flag (AtomicBoolean) to guarantee that resumption logic runs exactly once. Furthermore, if the legacy callback yields multiple continuous values over time (such as continuous location streams, sensor events, or WebSocket messages) rather than a single terminal value, adapting it as a suspend function is an architectural mistake. Single-shot results belong in suspendCancellableCoroutine, whereas multi-shot streaming callbacks must be adapted into a cold Flow using callbackFlow. In callbackFlow, awaitClose serves as the teardown boundary, ensuring that channel consumers receive stream values safely while guaranteeing that listeners are unregistered when the Flow collection terminates.

## How to answer in the interview

- **Why:** callback-to-coroutine adaptation is a race at the ownership boundary.
- **How:** register one-shot callback, atomically guard completion, and invoke SDK cancel/unregister on cancellation.
- **Trade-off:** a maintained library adapter is safer when available.
- **Failure case:** duplicate or late callback, synchronous completion, or leaked closeable result.
- **Production solution:** test each race and use Flow for multishot events.

## Deep-dive talking points

Analyze duplicate callbacks, synchronous callback, cancellation race, resource cleanup and one-shot versus multi-shot.

## Follow-up questions

- **Interviewer:** "What happens if a callback is invoked after the coroutine has already been cancelled?"
  **Answer:** "If the coroutine is cancelled, `CancellableContinuation` discards any subsequent `resume()` calls. If `resume()` provides an allocated resource that must be closed, you can use `continuation.resume(value) { value.close() }` to ensure resources are cleaned up if cancelled concurrently."

- **Interviewer:** "Why is `callbackFlow` preferred over `suspendCancellableCoroutine` for multiple values?"
  **Answer:** "A suspending function can only return a single value once. For streams emitting multiple values over time, `callbackFlow` provides an asynchronous cold stream backed by a Channel that buffers emissions and manages cleanup via `awaitClose`."

- **Interviewer:** "Can you call `continuation.resume()` from any thread?"
  **Answer:** "Yes. `CancellableContinuation.resume()` is thread-safe. When invoked, it automatically dispatches the resumption back to the coroutine's designated CoroutineDispatcher."

## Self-check rubric

Can I implement registration/cleanup, guard exactly one completion, and test late callback and cancellation?

## References and reviewed-on date

- [Kotlin suspendCancellableCoroutine API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/suspend-cancellable-coroutine.html) — prompt cancellation and cleanup.

Technically reviewed against primary documentation on 2026-10-13.
