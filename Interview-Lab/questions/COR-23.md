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

Use suspendCancellableCoroutine to convert callbacks into suspending functions. Resume with continuation.resume() on success, continuation.resumeWithException() on error, and crucially register continuation.invokeOnCancellation to unregister listeners and abort external tasks when cancelled.

## Interview answer — structured

To adapt asynchronous callback APIs into idiomatic suspending functions, I always use `suspendCancellableCoroutine`.

It suspends the coroutine and provides a `CancellableContinuation<T>` handle. Inside the callback listener: on success, I call `continuation.resume(data)`; on failure, I call `continuation.resumeWithException(throwable)`.

The critical architectural step that separates senior engineers from juniors is handling cancellation: you must invoke `continuation.invokeOnCancellation { ... }` to detach the callback listener or signal cancellation to the underlying SDK. Without this, if the calling coroutine is cancelled, the underlying third-party listener remains registered, leaking memory and leaving network or location hardware active.

Never use the older `suspendCoroutine` builder because it cannot respond to coroutine cancellation.


## Interview answer — deep senior

Under the hood, `suspendCancellableCoroutine` provides strict safety guarantees regarding resume calls. A continuation can only be resumed once. If a third-party SDK accidentally triggers both a success and an error callback, or triggers a callback after cancellation, `CancellableContinuation` guards against illegal multi-resumes by ignoring or throwing an IllegalStateException.

For streaming callback APIs that deliver multiple events over time (such as GPS location updates or WebSocket messages), adapting them to a single suspending function is an anti-pattern. Instead, stream APIs must be adapted to Kotlin Flow using `callbackFlow { }`:

```kotlin
fun observeLocation(): Flow<Location> = callbackFlow {
    val listener = LocationListener { location -> trySend(location) }
    client.register(listener)
    awaitClose { client.unregister(listener) }
}
```

`callbackFlow` uses `awaitClose` to guarantee listener cleanup when flow collection halts.


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
