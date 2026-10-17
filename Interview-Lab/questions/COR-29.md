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

## Concept and technical explanation

Integrating legacy third-party SDKs or native C/C++ libraries that execute blocking I/O calls without coroutine suspension points or cancellation checks poses a severe concurrency hazard in Android. When a coroutine calls a blocking method—such as a legacy synchronous socket read, blocking Bluetooth stream, or heavy JNI computation—the thread remains physically blocked. If the calling coroutine scope cancels, the coroutine cannot cancel cooperatively because no suspension point is reached. To handle unresponsive blocking code, engineers must apply three strategic countermeasures based on the nature of the blocking call. First, if the SDK executes standard Java blocking I/O or sleep calls, wrapping the invocation in runInterruptible(Dispatchers.IO) monitors coroutine cancellation and automatically invokes Thread.interrupt() on the worker thread. Second, if the SDK ignores thread interruption (such as legacy java.net.Socket calls or native JNI code), the application must implement resource closure: registering continuation.invokeOnCancellation to explicitly close the underlying socket, stream, or file descriptor, forcibly triggering an IOException that unblocks the thread. Third, if the blocking call is completely un-interruptible, it must be isolated in a dedicated single-thread dispatcher to prevent starvation of the shared Dispatchers.IO pool.

## Practical walkthrough (English)

Consider handling a legacy blocking Bluetooth socket read that ignores coroutine cancellation:
```kotlin
// Erroneous implementation: thread remains permanently blocked on cancellation
suspend fun readLegacyDataUnsafe(): ByteArray = withContext(Dispatchers.IO) {
    // If cancelled, the worker thread remains permanently stuck in read()!
    legacyBluetoothSocket.inputStream.readBytes() 
}

// Strategy 1: Using runInterruptible for interruptible blocking calls
suspend fun readInterruptibleData(): String = runInterruptible(Dispatchers.IO) {
    // If the underlying SDK checks Thread.currentThread().isInterrupted,
    // cancellation immediately interrupts the worker thread:
    legacySdk.blockingQuery()
}

// Strategy 2: Forcible resource closure for non-interruptible sockets
suspend fun readNonInterruptibleSocket(socket: Socket): ByteArray = suspendCancellableCoroutine { continuation ->
    val thread = thread {
        try {
            val bytes = socket.inputStream.readBytes()
            continuation.resume(bytes)
        } catch (e: Exception) {
            continuation.resumeWithException(e)
        }
    }
    
    // Forcibly unblock the stuck thread by closing the socket descriptor on cancellation:
    continuation.invokeOnCancellation {
        try {
            socket.close() // Throws SocketException inside readBytes(), unblocking thread!
        } catch (ignored: IOException) {}
    }
}
```

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

When a blocking SDK ignores coroutine cancellation, standard suspension cannot unblock it. Use runInterruptible(Dispatchers.IO) if the SDK responds to Thread.interrupt(). For non-interruptible network or file operations, forcibly close the underlying socket or stream via invokeOnCancellation to trigger an IOException that unblocks the thread. If completely uninterruptible, isolate the call in a dedicated custom dispatcher to prevent starving Dispatchers.IO.

## Interview answer — structured

Handling legacy third-party SDKs that execute blocking operations without coroutine cancellation awareness is a classic interoperability challenge in Android engineering. When a blocking method is invoked, it locks the physical operating system thread and ignores Job.cancel() signals because it lacks cooperative suspension points.

Engineers must evaluate whether the blocking operation is interruptible at the JVM thread level. If the underlying code checks thread interruption flags or blocks on interruptible channels, wrapping the call in runInterruptible with Dispatchers.IO ensures that coroutine cancellation immediately invokes Thread.interrupt() on the executing worker thread, aborting the call cleanly.

In production, involving non-interruptible blocking calls—such as legacy java.net.Socket reads or native JNI calls—thread interruption is completely ignored. In these situations, the only effective countermeasure is resource closure.

We register an invokeOnCancellation callback that forcibly closes the underlying socket or input stream, causing the blocking read to throw a SocketException or IOException that immediately frees the thread. If the library provides zero closure hooks, we isolate the call within a dedicated, bounded single-thread dispatcher to quarantine the thread and protect the shared Dispatchers.IO pool from resource exhaustion.


## Interview answer — deep senior

Under the hood, coroutine cancellation relies strictly on cooperative suspension points. When a coroutine invokes a blocking JNI function or a legacy synchronous method, the thread counter executes native or JVM opcodes continuously; the Kotlin coroutine runtime has zero mechanism to forcibly preempt that thread without external operating system signals. The Kotlin standard library provides runInterruptible to bridge this gap. Inside runInterruptible, a completion handler is registered on the coroutine's Job. If cancellation occurs while the blocking block is running, the handler retrieves the physical Java Thread reference executing the block and invokes Thread.interrupt(). This works reliably for any Java API that responds to InterruptedException or implements InterruptibleChannel (like java.nio.channels.FileChannel). However, classic blocking sockets (java.net.Socket) and native C++ shared libraries (.so files loaded via JNI) are completely immune to Thread.interrupt(); they block inside Linux kernel read() syscalls. In this scenario, invoking Thread.interrupt() simply sets the interrupt status flag without waking the thread from the kernel sleep state. To solve this in staff-level Android architectures, we employ the Asynchronous Close pattern. Using suspendCancellableCoroutine, we expose a cancellation boundary: when the coroutine cancels, invokeOnCancellation executes socket.close() or closes the native file descriptor (/dev/null or file handle). The Linux kernel intercepts the closed descriptor and immediately wakes the blocked thread with an EBADF or ECONNRESET error, which translates to a Java SocketException, unwinding the call stack cleanly. Finally, in extreme legacy situations where an SDK neither supports interruption nor exposes its underlying resources, the thread is effectively leaked until the external operation times out. To prevent this leaked thread from starving the global Dispatchers.IO pool (which has a default limit of 64 threads), we isolate such toxic calls in a dedicated, bounded dispatcher created via Executors.newSingleThreadExecutor().asCoroutineDispatcher(), ensuring that main application traffic remains fully isolated and performant.

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
