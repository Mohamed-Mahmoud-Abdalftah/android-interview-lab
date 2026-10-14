---
id: "COR-01"
question: "What is a coroutine, and how is it different from a thread?"
topic: "Kotlin Coroutines & Concurrency"
code: "COR"
group: "A"
phase: 1
priority: "P1"
order: 82
editorial_status: "reviewed"
---

# COR-01

## Original interview question

What is a coroutine, and how is it different from a thread?

## What the interviewer evaluates

- Whether you separate a suspendable computation from the OS thread that executes its instructions.
- Whether you understand dispatchers, suspension, blocking calls, and cancellation as different concerns.
- Whether you can choose an owner for Android work instead of launching unbounded jobs.

## Explanation in Arabic

الفرق بين الـ Coroutine والـ Thread هو حجر الأساس لفهم التزامن (Concurrency) في Kotlin و Android:

1. الـ Thread (خيط المعالجة في الـ OS):
   - هو كيان ثقيل يديره نظام التشغيل (OS-managed Kernel Thread).
   - كل Thread بيحجز مساحة ثابتة في الذاكرة للـ Stack بتاعه (عادة 1 ميجابايت على JVM وحوالي 512-1024KB على Android ART).
   - التبديل بين الـ Threads (Context Switching) مكلف جداً في الـ CPU؛ لأنه بيتطلب الانتقال بين User Mode و Kernel Mode وتفريغ سجلات المعالج.
   - لو حاولت تشغل 10,000 Thread في نفس الوقت على جهاز أندرويد، التطبيق هيعمل Crash بـ `OutOfMemoryError: unable to create new native thread` فوراً!

2. الـ Coroutine (خيط المعالجة الخفيف في User-space):
   - هي **Lightweight Thread** يتم إدارتها بالكامل في User Space بواسطة مكتبة Kotlin (`kotlinx.coroutines`) بدون تدخل الـ OS Kernel.
   - مش مربوطة بـ Thread معين؛ الـ Coroutine عبارة عن State Machine وكائن صغير في الـ Heap لا يتعدى حجمه بضع مئات من الـ Bytes.
   - عند التعليق (Suspension)، الـ Coroutine بتسيب الـ Thread بتاعها لكي ينفذ مهام تانية، ولما ترجع تشتغل، ممكن تكمل على نفس الـ Thread أو Thread تاني خالص من الـ Dispatcher Pool بدون أي Context Switch للـ OS!
   - تقدر تشغل 100,000 Coroutine في نفس الوقت على جهاز موبايل عادي بدون أي مشكلة في الذاكرة.

## Practical walkthrough

في شاشة قائمة المنتجات (Product Catalog):
- محتاجين نعمل 1,000 طلب خفيف لجلب أسعار المنتجات في الخلفية.
- **النهج الكارثي مع Threads:**
  `repeat(1000) { Thread { fetchPrice(it) }.start() }`
  هذا الكود سينشئ 1,000 OS Thread، يستهلك حوالي 1 جيجابايت RAM، ويسبب OOM Crash وتهنيج للجهاز بالكامل.
- **النهج الصحيح مع Coroutines:**
  `repeat(1000) { viewModelScope.launch(Dispatchers.IO) { fetchPrice(it) } }`
  الـ 1,000 Coroutine هيتشاركوا في Thread Pool مكون من عدد محدود من الـ Threads (عادة 64 thread كحد أقصى في Dispatchers.IO)، ويتم تعليقهم بدون حجز أي موارد إضافية أثناء انتظار استجابة السيرفر.

## Why it matters and how it works

On the JVM, a coroutine executes on a thread. A suspending operation can save its continuation and release that thread until the result is ready. Its dispatcher determines the execution context and it may resume on a different thread. A plain CPU loop or blocking SDK call does not become cooperative simply because it sits inside `launch`. Cancellation is cooperative: suspending functions usually check it, while custom long loops need explicit checks. Structured scope ownership lets an Activity or ViewModel stop obsolete UI work.

## Worked example

The following is a JVM example using `kotlinx-coroutines-core`; it is intentionally small enough to run in a coroutines-enabled Kotlin module. `delay` suspends, while `Thread.sleep` would block the executing thread.

```kotlin
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking

fun main() = runBlocking {
    val job = launch(Dispatchers.Default) {
        delay(100) // releases the worker while waiting
        println("Resumed on ${Thread.currentThread().name}")
    }
    job.join()
}
```

In Android, launch UI-bound work in `viewModelScope`; put a genuinely blocking repository operation behind `withContext` with an injected appropriate dispatcher. Do not add an IO switch to an API that is already documented main-safe without a reason.

## Trade-offs and decision criteria

Coroutines make asynchronous control flow and cancellation easier to express than callback chains. They do not make shared mutable state safe or eliminate the need for backpressure, thread pools, or durable work. Choose a ViewModel or lifecycle scope for UI lifetime; choose WorkManager for work that must survive the UI lifecycle and meet OS scheduling constraints. A single coroutine can still block or consume CPU for too long.

## Failure modes

**Wrong:** “`launch` creates a background thread, so the UI cannot freeze.” **Right:** inspect the inherited dispatcher and every call inside the coroutine. `Thread.sleep`, a synchronous Binder call, or blocking database driver on Main can still stall frames. Another mistake is a detached application scope for a search request: results can return after the screen is gone. Tie the job to the correct owner and verify cancellation behavior.

## Production perspective

A search ViewModel launches request handling in `viewModelScope`; new input cancels obsolete search work and the repository documents whether its network API suspends without blocking. This keeps UI work owned by the screen. A payment reversal that must survive process death belongs in durable persisted state plus scheduled recovery, not a screen coroutine.

## Interview answer — short

A coroutine is a lightweight, cooperative concurrency primitive managed entirely in user space by the Kotlin runtime, whereas a thread is an expensive operating-system resource with its own dedicated memory stack. Coroutines can suspend without blocking their underlying thread, allowing millions of concurrent tasks on a handful of OS threads.

## Interview answer — structured

The fundamental difference is that a thread is an operating system kernel resource, while a coroutine is a user-space abstraction managed by the Kotlin runtime.

An OS thread is heavy: each thread allocates its own 1MB call stack in memory, and switching between threads requires expensive OS kernel context switches. Spawning thousands of threads will quickly crash an Android app with an OutOfMemoryError.

A coroutine, by contrast, is completely lightweight—it is essentially an object instance in the heap representing a state machine, weighing only a few hundred bytes. When a coroutine executes a suspending operation like an API call or delay, it does not block the underlying OS thread; it unbinds itself and frees that thread to do other work, such as rendering UI frames. Once the asynchronous work completes, the coroutine resumes on an available thread in its dispatcher pool.


## Interview answer — deep senior

Under the hood, the Kotlin compiler transforms every suspending function into a state machine implementing the `Continuation<T>` interface, passing a continuation parameter under the continuation-passing style (CPS) transformation. When a suspension point is reached, the function stores its local frame state onto the heap and returns a special marker value `COROUTINE_SUSPENDED`. The underlying thread is immediately released back to its thread pool executor.

In contrast to preemptive multithreading where the OS scheduler forcibly interrupts threads at arbitrary time slices, coroutines are cooperative: a coroutine runs until it explicitly yields or reaches a suspension point. In Android architecture, this distinction is vital for UI fluidity. Blocking the main thread with a 500ms network call triggers an ANR dialog. Suspending on the main thread simply returns control to the Android Choreographer loop, keeping UI touch events and 120Hz frame rendering completely smooth.


## How to answer in the interview

- **Why:** waiting requests need cheap ownership.
- **How:** distinguish the coroutine's continuation, its dispatcher thread, and its parent Job.
- **Trade-off:** cheap waiting does not make CPU or shared state free.
- **Failure case:** a blocking call on Main or a late response after navigation.
- **Production solution:** use a screen-owned scope, a main-safe client, and cancellation-aware result publication.

## Deep-dive talking points

Explain continuations and dispatcher inheritance; compare cooperative cancellation with interrupting a blocking API; discuss structured concurrency and why `GlobalScope` is a poor default for screen work. Distinguish concurrency from parallel execution.

## Follow-up questions

- **Interviewer:** "Can a coroutine resume on a different thread than the one it started on?"
  **Answer:** "Yes. Unless confined to a single-threaded dispatcher like Dispatchers.Main, a coroutine running on a thread pool (like Dispatchers.Default or Dispatchers.IO) may suspend on thread A and resume execution on thread B once its asynchronous task finishes."

- **Interviewer:** "What happens if a coroutine executes a heavy blocking call like Thread.sleep() instead of delay()?"
  **Answer:** "Thread.sleep() blocks the underlying OS thread. If that coroutine is running on Dispatchers.Main, it freezes the Android UI and triggers an ANR. If running on a worker pool, it starves that pool's worker thread, depriving other coroutines of execution time."

- **Interviewer:** "How does memory allocation compare between 1,000 threads and 1,000 coroutines?"
  **Answer:** "1,000 threads require approximately 500MB to 1GB of dedicated stack memory allocated from native RAM, typically crashing mobile processes. 1,000 coroutines require only a few megabytes on the JVM heap for their Continuation instances."

## Self-check rubric

Score one point each (0–5): define coroutine and thread separately; explain suspension without blocking; identify dispatcher and scope roles; diagnose a blocking call on Main; choose an Android owner and justify lifetime. Missing any point shows what to rehearse next; this is self-scoring.

## References and reviewed-on date

- [Kotlin coroutines basics](https://kotlinlang.org/docs/coroutines-basics.html) — suspension, dispatchers, and threads.
- [Android coroutines guidance](https://developer.android.com/kotlin/coroutines) — Android integration and lifecycle guidance.

Technically reviewed against primary documentation on 2026-10-13.
