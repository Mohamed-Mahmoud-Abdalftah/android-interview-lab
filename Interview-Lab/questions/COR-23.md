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

لتحويل callback بيرجع نتيجة واحدة إلى suspend API بنستخدم `suspendCancellableCoroutine`، ونسجّل callback ثم `invokeOnCancellation` لإلغاء/فصل التسجيل إن الـSDK يسمح. لازم نعالج السباق بين callback وcancel، وما نعملش `resume` مرتين، وما نفترضش إن إلغاء coroutine يعني إلغاء العملية الخارجية تلقائيًا.

## Why it matters and how it works

The continuation can be resumed with a value or exception; cancellation can race with callback delivery. The adapter should unregister a listener or cancel the underlying call on cancellation. If callback returns a closeable resource, arrange cleanup for cancellation after delivery. For multi-shot APIs use `callbackFlow` with `awaitClose`, not a one-shot continuation.

## Worked example

Conceptual Kotlin/JVM adapter; `LegacyCall` specifies one terminal callback and cancellation, and must document whether callbacks can arrive after `cancel`.

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

“I use `suspendCancellableCoroutine` for a one-shot callback, resume exactly once, and unregister or cancel the underlying call when the coroutine is cancelled. I test callback/cancellation races. For a stream of callbacks I use `callbackFlow`.”

## Interview answer — structured

“A callback wrapper must preserve both result and lifetime. I register the callback inside `suspendCancellableCoroutine`, resume the continuation on success or failure, and use `invokeOnCancellation` to detach the listener or cancel the call. I inspect whether the SDK may invoke the callback twice or after cancellation, because `isActive` checks alone are not a complete duplicate guard. A multi-event listener should be adapted as `callbackFlow` with `awaitClose`. The wrapper’s test cases include synchronous callback, delayed callback, error, cancellation and late delivery.”

## Interview answer — deep senior

“The hard part is the race at the boundary. Cancellation can happen after registration, during callback delivery or after a resource has been produced but before the caller receives it. I use the library’s prompt-cancellation support, implement an atomic single-terminal-event guard if the SDK does not guarantee exactly one callback, and release closeable results on cancellation where needed. `invokeOnCancellation` should call the SDK’s cancel/unregister method, but that only expresses local intent; a remote operation may already have committed. I keep the adapter in the data layer with a main-safe contract and test each interleaving with a controlled fake callback source. If the source emits repeatedly, `callbackFlow` is the correct abstraction.”

## Deep-dive talking points

Analyze duplicate callbacks, synchronous callback, cancellation race, resource cleanup and one-shot versus multi-shot.

## Follow-up questions

- [FLO-21](../flo-21/): How adapt repeated callbacks? **Answer:** `callbackFlow` with `awaitClose` for listener cleanup.
- [COR-10](../cor-10/): What does cancellation mean for SDK work? **Answer:** the adapter must invoke the SDK’s cancellation mechanism if available.

## Self-check rubric

Can I implement registration/cleanup, guard exactly one completion, and test late callback and cancellation?

## References and reviewed-on date

- [Kotlin suspendCancellableCoroutine API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/suspend-cancellable-coroutine.html) — prompt cancellation and cleanup.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
