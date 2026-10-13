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

Coroutine cancellation is cooperative: calling cancel() merely sets the job's state to cancelled. The coroutine itself must actively cooperate by reaching a cancellation point—such as delay(), yield(), or ensureActive()—which checks that state and throws a CancellationException to terminate execution.

## Interview answer — structured

Coroutine cancellation is strictly cooperative. Calling `job.cancel()` does not preemptively kill the thread or forcibly terminate execution like a deprecated Thread.stop() would. Instead, it transitions the coroutine's internal Job state to 'cancelling'.

The coroutine code must cooperate to actually stop. Standard library suspending functions—such as `delay()`, `withContext()`, `yield()`, and `await()`—act as built-in **cancellation points**. Before executing and immediately upon resuming, they check if their Job is cancelled. If it is, they throw a `CancellationException`, which unwinds the coroutine call stack cleanly.

The failure case occurs during tight, non-suspending CPU loops or blocking Java I/O. If a coroutine executes a mathematical loop for 10 seconds without calling any suspending functions, it will completely ignore `cancel()` until the loop finishes. To make CPU-bound code cancellable, we explicitly insert `ensureActive()` or `yield()` inside the loop body.

## Interview answer — deep senior

At the runtime level, cancellation uses `CancellationException` as its unwinding vehicle. Crucially, `CancellationException` is treated specially by the coroutine machinery: it is considered normal completion of a cancelled task rather than an error. It does not cancel parent scopes or trigger uncaught exception handlers.

However, this introduces a classic production trap: swallowing `CancellationException`. If a developer writes a broad catch block:

```kotlin
try {
    doWork()
} catch (e: Exception) { // Swallows CancellationException!
    logError(e)
}
```

This catches `CancellationException` and ignores it, completely breaking cancellation. The coroutine will refuse to stop! The golden rule is to either catch specific exceptions (like `IOException`) or immediately rethrow `CancellationException`:

```kotlin
} catch (e: Exception) {
    if (e is CancellationException) throw e
    handleError(e)
}
```

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
