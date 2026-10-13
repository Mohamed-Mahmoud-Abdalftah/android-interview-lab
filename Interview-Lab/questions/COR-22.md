---
id: "COR-22"
question: "When should you use ensureActive or yield during CPU-bound work?"
topic: "Kotlin Coroutines & Concurrency"
code: "COR"
group: "B"
phase: 1
priority: "P1"
order: 103
editorial_status: "reviewed"
---

# COR-22

## Original interview question

When should you use ensureActive or yield during CPU-bound work?

## What the interviewer evaluates

Explain cancellation responsiveness in CPU loops and the scheduling distinction between ensureActive and yield.

## Explanation in Arabic

استخدام `ensureActive()` و `yield()` أثناء العمليات المكثفة على المعالج (CPU-Bound Work) ضروري لضمان التعاونية وعدم تجويع العمليات الأخرى:

1. المشكلة في الـ CPU-Bound Loops:
   - لما coroutine تنفذ كود حسابي مكثف (زي تشفير، معالجة صور، أو فحص مصفوفات ضخمة)، الكود لا يحتوي على أي دالة تعليق (`suspend`).
   - لو تم استدعاء `job.cancel()`، الـ Coroutine **لن تتوقف أبداً** وهتفضل شغالة وتستهلك البطارية!
   - وأيضاً لو الـ Dispatcher Pool فيه عدد threads محدود، الـ Loop دي هتحجز الـ Thread بالكامل وتمنع باقي الـ Coroutines من التنفيذ (Starvation).

2. دور دالة `ensureActive()`:
   - بتفحص: هل الـ Job الحالي تم إلغاؤه؟
   - لو تم إلغاؤه: ترمي `CancellationException` فوراً وتنهي التنفيذ.
   - لو لم يتم إلغاؤه: تكمل التنفيذ بدون أي تبديل خيوط وبدون أي تأخير (Zero overhead).

3. دور دالة `yield()`:
   - بتفحص الإلغاء وترمي `CancellationException` تماماً مثل `ensureActive()`.
   - **الإضافة الجوهرية في `yield()`:** تقوم بتعليق الـ Coroutine مؤقتاً وتضعها في نهاية طابور الـ Dispatcher، وتمنح فرصة للـ Coroutines الأخرى في نفس الـ Pool أن تتنفس وتتنفذ (Fair Scheduling)!

4. متى نستخدم كل واحدة منهما؟
   - استخدم `ensureActive()` لو الـ Loop سريعة والمطلوب فقط فحص الإلغاء بأعلى سرعة.
   - استخدم `yield()` لو الـ Loop ثقيلة جداً وتريد إعطاء فرصة لباقي المهام في الـ Thread Pool حتى لا تتجمد.

## Practical walkthrough

في دالة توليد صورة مصغرة (Thumbnail Processing Loop):
```kotlin
suspend fun processLargeDataSet(records: List<RawRecord>) = withContext(Dispatchers.Default) {
    val results = mutableListOf<ProcessedRecord>()
    for ((index, record) in records.withIndex()) {
        // 1. فحص الإلغاء في كل لفة:
        ensureActive()
        
        // 2. كل 100 لفة نمنح فرصة للمهام الأخرى عبر yield:
        if (index % 100 == 0) {
            yield()
        }
        
        results.add(transformRecord(record))
    }
    results
}
```

## Why it matters and how it works

Ordinary CPU code does not hit cancellable suspension automatically. `ensureActive` is a cheap explicit check; `yield` adds a scheduling point and fairness opportunity. Neither makes non-cooperative native calls cancellable. Avoid running the loop on Main; use an appropriate CPU dispatcher and bounded work.

## Worked example

JVM illustration assumes `kotlinx-coroutines-core`; chunk size is an example to tune by profiling.

```kotlin
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.currentCoroutineContext
import kotlinx.coroutines.ensureActive
import kotlinx.coroutines.withContext

suspend fun score(rows: List<Int>): Long = withContext(Dispatchers.Default) {
    var total = 0L
    rows.forEachIndexed { index, value ->
        if (index % 512 == 0) currentCoroutineContext().ensureActive()
        total += value.toLong() * value
    }
    total
}
```

## Trade-offs and decision criteria

`ensureActive` suits cancellation-only checks; `yield` may improve fairness when many tasks share a dispatcher but adds scheduling overhead. Offload CPU work from Main, but cap large parallel searches so they do not saturate every core and starve rendering-adjacent work.

## Failure modes

A tight image-processing loop on Main causes jank and ignores screen cancellation. Checking only after the whole batch is too late. Using `yield` every iteration can spend disproportionate time rescheduling.

## Production perspective

A gallery indexer processes images in chunks on Default and checks cancellation at chunk boundaries. When the user changes filters, old indexing stops promptly. Benchmarks track throughput and worst-case cancellation latency.

## Interview answer — short

Use ensureActive() to verify cancellation and throw CancellationException immediately with zero scheduling overhead. Use yield() to both check for cancellation and yield the current thread to other waiting coroutines in the dispatcher queue, ensuring fair scheduling during heavy CPU tasks.

## Interview answer — structured

During intensive CPU-bound calculations, coroutines do not hit natural suspension points like network calls or delays. This causes two production problems: they ignore cancellation, and they monopolize worker threads in the dispatcher pool.

I use `ensureActive()` when I strictly want cancellation responsiveness with maximum performance. It checks the Job's active state and immediately throws `CancellationException` if the job was cancelled. If the job is active, it does nothing and has zero dispatching or scheduling overhead.

I use `yield()` when a CPU-bound task is heavy and I want fair scheduling. `yield()` checks for cancellation just like `ensureActive()`, but if active, it suspends the coroutine and dispatches it to the back of the dispatcher's work queue. This temporarily releases the OS thread so other waiting coroutines on the same dispatcher can execute, preventing thread starvation.

## Interview answer — deep senior

Under the hood, `ensureActive()` is an inline extension function on `CoroutineScope` and `Job` that executes:

```kotlin
if (!isActive) throw getCancellationException()
```

Because it is inlined, it compiles directly to a simple conditional jump in bytecode without creating any continuation frames or dispatch objects.

`yield()`, by contrast, is a true suspending function. It captures the current `Continuation` and dispatches it via `dispatcher.dispatchYield()`. If the dispatcher's event queue is empty, the runtime immediately reschedules and resumes the coroutine on the same thread with minimal latency. If other tasks are enqueued, they execute first.

In high-frequency loops (e.g., iterating 100,000 times), calling `yield()` on every single iteration causes excessive scheduling overhead and degrades throughput. The senior engineering pattern is batching: call `ensureActive()` on every iteration, and throttle `yield()` to once every 100 or 500 iterations.

## How to answer in the interview

- **Why:** CPU loops may have no natural suspension point.
- **How:** check current Job with ensureActive periodically, or yield when peers need scheduling.
- **Trade-off:** tighter checks improve cancellation latency but add overhead.
- **Failure case:** a tight loop ignores cancel and monopolizes a worker.
- **Production solution:** process chunks on Default and profile cancellation latency.

## Deep-dive talking points

Contrast checks, fairness, dispatcher choice and uncooperative library calls.

## Follow-up questions

- **Interviewer:** "Can `yield()` be called on `Dispatchers.Unconfined`?"
  **Answer:** "Calling `yield()` on `Dispatchers.Unconfined` still yields execution, but because Unconfined has no thread queue, it might resume on whichever thread triggered the yield, which can lead to unpredictable stack depths."

- **Interviewer:** "Why not just use `delay(1)` instead of `yield()`?"
  **Answer:** "`delay(1)` forces the coroutine to pause for at least 1 millisecond by scheduling a timer event. `yield()` introduces zero artificial sleep delay; if no other coroutines are waiting, it resumes immediately without waiting."

- **Interviewer:** "What is the difference between `Thread.yield()` and Coroutines `yield()`?"
  **Answer:** "`Thread.yield()` is an OS-level hint to the thread scheduler to yield the current CPU quantum. Coroutines `yield()` is a cooperative user-space suspension that yields the worker thread to other coroutines in the Kotlin dispatcher queue."

## Self-check rubric

Can I place a check, justify frequency, choose Default, and state the limitation for blocking native code?

## References and reviewed-on date

- [Kotlin cancellation guidance](https://kotlinlang.org/docs/cancellation-and-timeouts.html) — cooperative checks.
- [Kotlin coroutines basics](https://kotlinlang.org/docs/coroutines-basics.html) — dispatchers.

Technically reviewed against primary documentation on 2026-10-13.
