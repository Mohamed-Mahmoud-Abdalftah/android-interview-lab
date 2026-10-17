---
id: "COR-10"
question: "What is cooperative cancellation? What are cancellation points?"
topic: "Kotlin Coroutines & Concurrency"
code: "COR"
group: "A"
phase: 1
priority: "P1"
order: 91
editorial_status: "reviewed"
---

# COR-10

## Original interview question

What is cooperative cancellation? What are cancellation points?

## What the interviewer evaluates

Whether the candidate can locate cancellation checks and explain that cancellation is cooperative, not forced thread interruption.

## Concept and technical explanation

In Kotlin coroutines, cancellation is cooperative, meaning that a running coroutine cannot be preemptively or forcefully aborted from the outside by an operating system thread interruption. When a coroutine or its parent Job is cancelled, its state transitions to Cancelling, and it must cooperatively inspect its cancellation status to terminate execution. Cancellation points are specific locations during coroutine execution where cancellation is checked; if the coroutine has been cancelled, a CancellationException is thrown to unwind the call stack cleanly. All suspending functions provided by kotlinx.coroutines (such as delay, yield, withContext, await, and receive) are built-in cancellation points. However, if a coroutine executes a long-running CPU computation or a synchronous blocking Java I/O stream without invoking suspending functions, it will continue running unabated unless the developer explicitly inserts cancellation checks, such as calling ensureActive(), querying isActive, or invoking yield(). Furthermore, swallowing CancellationException in a generic try-catch block without re-throwing it violates cooperative cancellation, causing cancelled coroutines to silently resurrect and run indefinitely.

## Practical walkthrough (English)

Consider a background file encryption routine executing a tight loop over thousands of byte chunks.

Uncooperative implementation that ignores cancellation:
```kotlin
// Defective: Ignores cancellation signals
suspend fun encryptFile(data: ByteArray): ByteArray = withContext(Dispatchers.Default) {
    val result = ByteArray(data.size)
    for (i in data.indices) {
        result[i] = computeByteHash(data[i]) // Tight CPU loop, no suspension point!
    }
    result
}
```
If the user cancels this operation, the loop continues running to completion, burning CPU cycles and draining the battery.

The correct cooperative implementation:
```kotlin
suspend fun encryptFile(data: ByteArray): ByteArray = withContext(Dispatchers.Default) {
    val result = ByteArray(data.size)
    for (i in data.indices) {
        // Check cancellation every 1,000 iterations
        if (i % 1000 == 0) ensureActive()
        result[i] = computeByteHash(data[i])
    }
    result
}
```
Calling ensureActive() immediately throws CancellationException if the coroutine is cancelled, terminating execution gracefully.

## Explanation in Arabic

الإلغاء في Kotlin Coroutines هو **Cooperative (تعاوني)**، وهذا المفهوم هو السبب رقم واحد لحدوث أخطاء عدم توقف العمليات في الخلفية:

1. ما معنى أن الإلغاء 'تعاوني' (Cooperative Cancellation)؟
   - الكود لا يتم إيقافه بالقوة الجبرية من نظام التشغيل أو الـ JVM.
   - استدعاء `job.cancel()` لا يعني قتل الـ Coroutine فوراً؛ هو فقط بيغير حالة الـ Job إلى `isCancelled = true`.
   - **الـ Coroutine نفسها هي المسؤولة عن التعاون:** لازم الكود يفحص حالة الإلغاء بنفسه ويتوقف طواعية!

2. ما هي نقاط الإلغاء (Cancellation Points)؟
   - هي الأماكن التي تقوم تلقائياً بفحص الإلغاء ورمي `CancellationException` إذا كان الـ Job ملغياً.
   - جميع الدوال المعلقة القياسية في مكتبة Kotlin (Standard Suspending Functions) هي نقاط إلغاء تلقائية، مثل:
     * `delay()`
     * `yield()`
     * `withContext()`
     * `await()`

3. متى يفشل الإلغاء ويستمر الكود في العمل؟
   - لو عندك Loop بتعمل عمليات CPU مكثفة أو Blocking I/O بدون أي دالة suspend:
     `while (i < 1_000_000) { compute() }`
     الكود ده هيفضل شغال حتى لو ناديت `job.cancel()` 100 مرة!
   - **الحل:** لازم تفحص الإلغاء يدوياً داخل الـ Loop باستخدام `isActive` أو تنادي `ensureActive()` أو `yield()` في كل لفة.

## Practical walkthrough

في دالة ضغط وتحويل ملف فيديو كبير (Video Transcoding):
- **الكود غير المتعاون (Non-cooperative Loop):**
  val job = scope.launch(Dispatchers.Default) {
      for (frame in allFrames) {
          compressFrame(frame) // لا توجد دالة تعليق هنا!
      }
  }
  // المستخدم ضغط 'إلغاء' ومشي من الشاشة:
  job.cancel() // الكود هيفضل شغال ويستهلك البطارية والمعالج حتى ينتهي كل الفيديو!
- **الكود المتعاون الصحيح (Cooperative Loop):**
  val job = scope.launch(Dispatchers.Default) {
      for (frame in allFrames) {
          ensureActive() // تفحص الإلغاء وترمي CancellationException فوراً لو تم الإلغاء
          compressFrame(frame)
      }
  }
- النتيجة: بمجرد استدعاء `job.cancel()`، العملية تتوقف فوراً في اللفة التالية ويتم تحرير موارد الجهاز.

## Why it matters and how it works

A cancelled Job makes cancellable suspension throw `CancellationException`. `ensureActive()` explicitly checks and throws; `yield()` checks and gives other coroutines a scheduling opportunity. `finally` runs for cleanup, but suspending cleanup needs `withContext(NonCancellable)` only for a small bounded critical cleanup when required.

## Worked example

JVM example uses `kotlinx-coroutines-core`; `items` is in-memory and `inspect` is CPU work, so the loop checks cancellation periodically.

```kotlin
import kotlinx.coroutines.currentCoroutineContext
import kotlinx.coroutines.ensureActive

suspend fun scan(items: List<String>, inspect: (String) -> Unit) {
    for ((index, item) in items.withIndex()) {
        if (index % 256 == 0) currentCoroutineContext().ensureActive()
        inspect(item)
    }
}
```

## Trade-offs and decision criteria

Checking every iteration may add cost; choose a frequency that keeps response time acceptable. `yield` also offers fairness, while `ensureActive` only checks. For blocking libraries use their explicit cancel/close API or isolate and bound them; coroutine cancellation alone cannot guarantee prompt interruption.

## Failure modes

`runCatching { suspendingCall() }` catches `CancellationException` because it catches Throwable, potentially converting cancellation to a normal failure result. A broad `catch (Exception)` that logs and continues has the same risk. Rethrow cancellation before handling domain errors.

## Production perspective

A ViewModel starts a large local search over cached products. New query input cancels the previous Job; the scan checks `ensureActive` to stop quickly. Telemetry distinguishes user cancellation from genuine error, and tests measure cancellation latency under a large dataset.

## Interview answer — short

Cancellation in Kotlin coroutines is cooperative and never preemptive. A coroutine must check its cancellation status or reach a cancellation point—such as delay(), yield(), or ensureActive()—which throws CancellationException to terminate. Swallowing CancellationException in try-catch prevents cancellation from taking effect.

## Interview answer — structured

Cancellation in Kotlin coroutines is strictly cooperative. An external scope cannot forcibly terminate a running coroutine; instead, it signals cancellation, requiring the coroutine to check its active state.

Cancellation points are checkpoints where the coroutine checks its Job status. All standard suspending functions in kotlinx.coroutines act as cancellation points by throwing CancellationException when cancelled.

In production, long CPU-bound loops or blocking stream reads lack automatic cancellation points. Engineers must explicitly include ensureActive(), check isActive, or invoke yield() periodically to allow cancellation signals to take effect.

Resource cleanup should occur within finally blocks. If an unmanaged catch block intercepts CancellationException without re-throwing it, cancellation is silently broken, leaving orphaned background tasks running indefinitely.


## Interview answer — deep senior

Under the hood, coroutine cancellation operates through the Job state machine and the throwing of CancellationException. When job.cancel() is invoked, the Job transitions from Active to Cancelling. It notifies all registered children to cancel and dispatches cancellation to any currently suspended continuation.

If the coroutine is currently suspended at a cancellation point—such as delay(1000)—the underlying cancellable continuation (CancellableContinuationImpl) immediately resumes the coroutine by throwing CancellationException. This unwinds the continuation stack frame by frame, triggering finally blocks along the way to release resources such as file handles or database locks.

However, if the coroutine is currently executing active CPU instructions inside a non-suspending loop, it remains oblivious to the Job state until it explicitly calls a cancellation point. The standard library provides three mechanisms for non-suspending code: isActive returns a boolean check of the Job state; ensureActive() throws CancellationException immediately if the Job is no longer active; and yield() checks cancellation while also cooperatively giving up the thread to other pending coroutines on the dispatcher.

A critical pitfall in production is catching Exception or Throwable. If a developer writes try { ... } catch (e: Exception) { log(e) }, the catch block intercepts CancellationException, treating it as an ordinary error and allowing execution to continue. To handle errors safely, engineers must either catch specific domain exceptions (like IOException) or explicitly re-throw CancellationException: if (e is CancellationException) throw e.

Finally, if cleanup logic inside a finally block requires invoking another suspending function (such as sending a network abort signal), it must be wrapped in withContext(NonCancellable) { ... }; otherwise, the already-cancelled coroutine will immediately throw CancellationException and abort the cleanup routine.

## How to answer in the interview

- **Why:** cancellation latency affects stale work and resource use.
- **How:** suspend points and explicit ensureActive checks observe a cancelled Job; yield also gives peers a turn.
- **Trade-off:** checking every item adds overhead, so tune the chunk.
- **Failure case:** runCatching turns cancellation into a Result failure or a blocking driver ignores it.
- **Production solution:** rethrow cancellation and test cleanup.

## Deep-dive talking points

Discuss cancellation at `delay`, a CPU loop and a blocking call; distinguish `ensureActive`, `yield` and `NonCancellable` cleanup.

## Follow-up questions

- **Interviewer:** "What is the difference between `ensureActive()` and checking `isActive`?"
  **Answer:** "`isActive` returns a boolean flag, requiring you to manually write `if (!isActive) return`. `ensureActive()` is an inline function that checks `isActive` and throws `CancellationException` immediately if false, guaranteeing standard coroutine unwinding."

- **Interviewer:** "What does `yield()` do, and how does it differ from `ensureActive()`?"
  **Answer:** "`ensureActive()` only checks for cancellation. `yield()` checks for cancellation AND yields the current thread to other coroutines in the dispatcher queue, allowing pending tasks to execute before resuming. It is ideal for compute loops to maintain fairness."

- **Interviewer:** "How do you run critical cleanup code after a coroutine is cancelled?"
  **Answer:** "By using a `try-finally` block. The `finally` block is guaranteed to execute upon cancellation. If the cleanup itself requires suspending functions (like closing a database), wrap that suspending call in `withContext(NonCancellable)` so it isn't aborted."

## Self-check rubric

Can I identify a cancellation point, fix a tight loop, explain a blocking limitation, and preserve cancellation through error handling?

## References and reviewed-on date

- [Kotlin coroutines basics](https://kotlinlang.org/docs/coroutines-basics.html) — Job and cancellation.
- [Coroutine exceptions](https://kotlinlang.org/docs/exception-handling.html) — cancellation exception semantics.

Technically reviewed against primary documentation on 2026-10-13.
