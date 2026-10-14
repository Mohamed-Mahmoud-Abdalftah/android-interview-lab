---
id: "COR-29"
question: "A blocking SDK call does not respond to coroutine cancellation. What can you do?"
topic: "Kotlin Coroutines & Concurrency"
code: "COR"
group: "C"
phase: 1
priority: "P1"
order: 110
editorial_status: "reviewed"
---

# COR-29

## Original interview question

A blocking SDK call does not respond to coroutine cancellation. What can you do?

## What the interviewer evaluates

Reason about blocking SDK cancellation, interruption, resource closure and uncertain external effects.

## Explanation in Arabic

التعامل مع مكتبة أو SDK خارجي يعمل بطريقة Blocking ولا يستجيب لإلغاء الـ Coroutines هو أحد أصعب التحديات في بيئة Android:

1. المشكلة:
   - مكتبة C++ قديمة أو SDK بلوتوث أو قراءة ديسك قديمة تنفذ استدعاء يحظر الخيط بالكامل (Blocking Call زي `socket.read()` أو `legacySdk.process()`).
   - بما أن الكود Blocking ولا يحتوي على Suspension Points، استدعاء `job.cancel()` لن يوقفه حتى ينتهي الاستدعاء بمفرده!

2. الحلول الهندسية المتاحة (Engineering Solutions):
   - **الحل 1 (عزل الـ Blocking على Dispatchers.IO):** تشغيل الكود دائماً على `Dispatchers.IO` لضمان عدم تجميد الـ UI Thread إطلاقاً، واستخدام `runInterruptible`.
   - **الحل 2 (`runInterruptible`):** مكتبة كوتلن توفر `runInterruptible(Dispatchers.IO) { blockingCall() }`. هذه الدالة تقوم بعمل `Thread.interrupt()` للـ OS Thread عند إلغاء الـ Coroutine. لو الـ SDK يستجيب للـ Thread Interruption (زي معظم Java I/O)، سيتوقف ويرمي `InterruptedException` فوراً!
   - **الحل 3 (إغلاق الـ Underlying Resource بالقوة):** لو الـ SDK لا يستجيب حتى للـ Interruption، الحل الوحيد هو إغلاق الـ Resource الذي ينتظره من الخارج (زي `socket.close()` أو `stream.close()`) عبر `continuation.invokeOnCancellation { socket.close() }`.

## Practical walkthrough

تطبيق عملي باستخدام `runInterruptible` وإغلاق المورد:
```kotlin
suspend fun downloadLargeFile(url: URL, destination: File) = withContext(Dispatchers.IO) {
    // runInterruptible ترسل Thread.interrupt() للـ thread الحابس عند إلغاء الـ coroutine:
    runInterruptible {
        url.openStream().use { input ->
            destination.outputStream().use { output ->
                input.copyTo(output) // Blocking Java I/O استدعاء
            }
        }
    }
}

// في حالة Socket خارجي لا يدعم interruption:
suspend fun readFromRawSocket(socket: Socket): ByteArray = suspendCancellableCoroutine { continuation ->
    continuation.invokeOnCancellation {
        try { socket.close() } catch (ignored: Exception) {} // إغلاق المقبس يكسر الـ Blocking read فوراً
    }
    // تنفيذ القراءة في الخلفية...
}
```

## Why it matters and how it works

Cancellation is cooperative at coroutine suspension points. For blocking JVM code, `runInterruptible(Dispatchers.IO)` couples Job cancellation to thread interruption, subject to the call responding correctly. Otherwise isolate the driver, cap concurrent calls, set native/client timeouts, and discard stale results. External writes need idempotency/reconciliation.

## Worked example

JVM illustration assumes `BlockingSdk.read` is documented interruptible; if it is not, do not claim prompt cancellation.

```kotlin
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.runInterruptible

interface BlockingSdk { fun read(id: String): ByteArray }

suspend fun readSdk(sdk: BlockingSdk, id: String): ByteArray =
    runInterruptible(Dispatchers.IO) { sdk.read(id) }
```

## Trade-offs and decision criteria

Use `runInterruptible` only with a library whose blocking behavior responds safely to interruption. A dedicated SDK cancel method may be better. A thread pool cap protects the app when calls are uninterruptible, but latency remains. Prefer an async maintained API when possible.

## Failure modes

Wrapping an uninterruptible call in `withTimeout` does not stop the thread promptly. Calling `Thread.stop` is unsafe. Retrying a timed-out write can duplicate side effects. A cancelled caller must not publish a late result to obsolete UI state.

## Production perspective

A document scanner SDK blocks during OCR. The repository runs it off Main, calls its cancel API on screen exit, limits concurrent scans and verifies no late result is shown. If the SDK cannot cancel, product UX shows a bounded wait and telemetry captures slow calls; payment-like side effects are reconciled separately.

## Interview answer — short

Wrap the blocking call in 'runInterruptible(Dispatchers.IO)', which issues a thread interrupt (Thread.interrupt()) to the underlying worker thread upon coroutine cancellation. If the SDK ignores thread interruption, close the underlying socket or resource via invokeOnCancellation to forcibly abort the blocking read.

## Interview answer — structured

When integrating a third-party SDK with blocking Java or native calls that do not cooperate with coroutine cancellation, we apply a multi-tier containment strategy:

First, isolate the call onto `Dispatchers.IO` so it never blocks the main thread or compute worker pools.

Second, wrap the execution inside **`runInterruptible(Dispatchers.IO) { ... }`**. When the coroutine is cancelled, `runInterruptible` issues a standard Java `Thread.interrupt()` to the executing worker thread. If the legacy SDK is blocked on standard Java I/O or sleep, it immediately throws an `InterruptedException` or closes the channel, cleanly aborting execution.

Third, if the SDK uses uninterruptible I/O (like legacy blocking sockets or native C++ loops), we close the underlying resource from the outside: register an `invokeOnCancellation { socket.close() }` hook. Closing the socket or file descriptor forcibly breaks the blocking read and releases the thread.


## Interview answer — deep senior

Under the hood, `runInterruptible` tracks the executing JVM `Thread` reference. When cancellation occurs, it calls `thread.interrupt()`. However, developers must understand that some blocking operations are completely uninterruptible at the OS level (e.g., waiting on un-interruptible locks or native JNI system calls that do not check POSIX signals).

If an external C++ or legacy Java library is completely unresponsive to both interruption and resource closing, that worker thread is effectively 'zombie-locked' until the operation completes or times out. In this worst-case scenario: 1. We run the operation on a dedicated, isolated thread pool created via `Executors.newSingleThreadExecutor().asCoroutineDispatcher()`, preventing it from polluting and exhausting the shared `Dispatchers.IO` pool. 2. We use `withTimeoutOrNull` around the caller continuation to allow our application to proceed and ignore the leaked thread until it eventually terminates.


## How to answer in the interview

- **Why:** cancelling a Job does not forcibly terminate arbitrary blocking code.
- **How:** use the SDK's cancel API, or runInterruptible for truly interruptible JVM calls.
- **Trade-off:** isolation and worker caps protect the app while a stuck call may still consume a thread.
- **Failure case:** timeout mistaken for server rollback.
- **Production solution:** bounded execution and reconciliation for side effects.

## Deep-dive talking points

Trace cancellation signal, thread interruption, SDK cancel API, late callback and server-side effect.

## Follow-up questions

- **Interviewer:** "Why does `Thread.interrupt()` work with `runInterruptible` but not standard `launch`?"
  **Answer:** "Standard `launch` only sets internal Job cancellation flags; it never touches the underlying OS thread. `runInterruptible` explicitly links the coroutine cancellation signal to Java's `Thread.interrupt()` mechanism."

- **Interviewer:** "What happens to the thread if an uninterruptible blocking call never finishes?"
  **Answer:** "The OS worker thread remains blocked and leaked. If this happens repeatedly on `Dispatchers.IO`, you will eventually exhaust the 64-thread pool limit, starving all other I/O operations in the application."

- **Interviewer:** "Can you kill a thread running a blocking call in Android?"
  **Answer:** "No. The JVM deprecated `Thread.stop()` decades ago because it causes memory corruption and leaves monitors unlocked. You cannot forcibly kill a thread; you can only interrupt it or close its underlying file/socket handles."

## Self-check rubric

Can I identify SDK capability, protect Main, bound resources and handle late/uncertain results?

## References and reviewed-on date

- [Kotlin withTimeout API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/with-timeout.html) — cooperative timeout and runInterruptible note.
- [Android coroutines guidance](https://developer.android.com/kotlin/coroutines) — main safety.

Technically reviewed against primary documentation on 2026-10-13.
