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

الـcoroutine شغل ممكن يقف عند suspension point ويرجع يكمل من غير ما يفضل حاجز thread وهو مستني. الـthread مورد من نظام التشغيل بينفّذ التعليمات فعلًا؛ الـcoroutine نفسها مش thread جديد. ممكن آلاف coroutines تتشارك عدد أقل من threads، لكن ده مش وعد إن كل شغل هيبقى سريع: لو ناديت blocking API على Main هتجمّد الـUI. الـdispatcher بيحدد مكان التنفيذ، والـscope بيحدد عمر الشغل وإلغاؤه.

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

“A coroutine is a suspendable unit of work, whereas a thread is the execution resource that runs it. Coroutines can share threads because a true suspension releases the thread while waiting. A dispatcher controls execution context and a scope controls lifetime. I still have to move blocking work appropriately and handle cancellation.”

## Interview answer — structured

“In Kotlin, a coroutine is a computation that can pause and resume at suspension points. On Android it still executes on a thread, but it is not permanently bound to one. That lets many waiting operations use relatively few threads. For example, `delay` suspends; calling a blocking SDK method inside a coroutine still blocks whichever thread runs it. I choose a lifecycle-owned scope for UI requests, make blocking repository boundaries main-safe, and use durable scheduling for work that must outlive the screen. Coroutines simplify concurrency, but do not by themselves provide thread safety or persistence.”

## Interview answer — deep senior

“A coroutine is a logical computation represented by a continuation and a Job, while a thread is an execution resource. The coroutine runs instructions on a thread until it suspends or completes; a truly suspending operation can release that thread, and later continuation may resume on a dispatcher-selected thread. This makes waiting work scalable, but a blocking call or CPU loop still occupies its worker and may freeze Main. I choose a scope based on ownership, such as a ViewModel for screen work, and ensure cancellation reaches downstream APIs. Shared state still needs synchronization, and operations that must survive process death need durable records and scheduling rather than merely a longer-lived coroutine.”

## Deep-dive talking points

Explain continuations and dispatcher inheritance; compare cooperative cancellation with interrupting a blocking API; discuss structured concurrency and why `GlobalScope` is a poor default for screen work. Distinguish concurrency from parallel execution.

## Follow-up questions

- [COR-02](../cor-02/): Does `suspend` imply background execution? **Answer:** no; the caller's context applies until a dispatcher is changed explicitly.
- [COR-04](../cor-04/): Who waits for child jobs? **Answer:** a structured parent scope waits for its children before completing and propagates failure according to its Job hierarchy.
- [COR-07](../cor-07/): Which dispatcher fits CPU work versus a blocking driver? **Answer:** CPU work normally fits `Default`; a blocking driver needs an appropriately bounded IO context, while a main-safe suspending API may need no switch.

## Self-check rubric

Score one point each (0–5): define coroutine and thread separately; explain suspension without blocking; identify dispatcher and scope roles; diagnose a blocking call on Main; choose an Android owner and justify lifetime. Missing any point shows what to rehearse next; this is self-scoring.

## References and reviewed-on date

- [Kotlin coroutines basics](https://kotlinlang.org/docs/coroutines-basics.html) — suspension, dispatchers, and threads.
- [Android coroutines guidance](https://developer.android.com/kotlin/coroutines) — Android integration and lifecycle guidance.

Technically reviewed against the linked primary documentation on 2026-10-11. The sample is a JVM illustration; Android device behavior was not tested here.
