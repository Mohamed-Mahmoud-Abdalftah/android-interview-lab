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

## Concept and technical explanation

A coroutine is a computation that can suspend and resume. On Android it still runs on a thread whenever it executes code, but a genuinely suspending operation can leave that thread free while waiting. A thread is an OS-managed execution resource with its own stack; creating large numbers of threads can exhaust native resources and cause `pthread_create` to fail. Coroutines are cheaper to keep waiting, but each one still consumes memory and can block a thread if it calls a synchronous API. `Dispatchers.IO` is designed for blocking I/O; its default parallelism and its `limitedParallelism` views do not amount to one fixed thread limit for an entire app. Scope ownership, cancellation, and bounded requests matter as much as the syntax.

## Practical walkthrough (English)

Consider a catalog that displays prices for a large list. Creating one thread per item is an unsafe way to fetch them:
```kotlin
repeat(1000) {
    Thread {
        fetchPrice(it)
    }.start()
}
```
The exact failure point depends on the device and process, but unmanaged thread creation can fail with `pthread_create` errors. Replacing each thread with one coroutine is still not a complete design. If the API supports a batch request, use it:
```kotlin
viewModelScope.launch {
    val prices = repository.fetchPrices(productIds) // main-safe suspending API
    render(prices)
}
```
The repository owns whether the call suspends without blocking and how the request is made. If the server has no bulk endpoint, use a concurrency limit for per-item calls. If `fetchPrice` is a blocking SDK call, isolate it on an appropriate dispatcher; adding `suspend` to its signature does not make it non-blocking.

## Explanation in Arabic

الـ Thread مورد تنفيذ بيديره نظام التشغيل وله Stack خاص. لو التطبيق أنشأ Threads كتير من غير حدود، ممكن يستهلك موارد Native ويفشل إنشاء Thread جديد. الـ Coroutine مهمة بتتنفذ على Thread حقيقي، لكن لما تستدعي عملية معلّقة فعلاً تقدر تحفظ حالتها وتسيب الـ Thread لشغل تاني لحد ما النتيجة تجهز. مش كل `suspend` عملية غير Blockingة؛ استدعاء SDK متزامن أو `Thread.sleep` هيحجز الـ Thread عادي. والكوروتينات نفسها بتستهلك Heap وموارد أخرى، فلازم نحدد عدد الطلبات ونختار Scope وDispatcher مناسبين.

## Practical walkthrough

في شاشة قائمة منتجات كبيرة، إنشاء Thread لكل سعر مش حل مناسب؛ عدد الـ Threads ومواردها ممكن يخرج عن السيطرة. استخدام Coroutine لكل سعر أوفر أثناء الانتظار لو الـ API معلّق فعلاً، لكنه برضه ممكن يطلق عدد طلبات أكبر من قدرة الشبكة أو السيرفر. الأفضل أشوف هل فيه Bulk API، أو أحدد عدد الطلبات المتزامنة، وأربط الشغل بعمر الشاشة. لو الـ SDK نفسه Blocking، أنقل الجزء الBlocking لسياق مناسب بدل ما أفترض إن `suspend` أو `launch` حلّ المشكلة.

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

**Wrong:** “`launch` creates a background thread, so the UI cannot freeze.” **Right:** inspect the inherited dispatcher and every call inside the coroutine. `Thread.sleep`, a synchronous Binder call, or blocking database driver on Main can stall frames. At 60 Hz the frame budget is about 16.7 ms; an input dispatch ANR has a default timeout of about five seconds. These are different failure thresholds, and the InputDispatcher timeout is not a promise that shorter stalls are acceptable. Another mistake is a detached application scope for a search request: results can return after the screen is gone. Tie the job to the correct owner and verify cancellation behavior.

## Production perspective

A search ViewModel launches request handling in `viewModelScope`; new input cancels obsolete search work and the repository documents whether its network API suspends without blocking. This keeps UI work owned by the screen. A payment reversal that must survive process death belongs in durable persisted state plus scheduled recovery, not a screen coroutine.

## Interview answer — short

A thread runs code; a coroutine is a task that runs on a thread and can pause without holding that thread while it waits. That makes coroutines useful for concurrent Android work, such as loading screen data. The distinction matters because launching a coroutine does not move blocking code off Main. I still choose the right scope and execution context for the work.

## Interview answer — structured

A thread is what actually executes the code. A coroutine is a task that can suspend and later resume, possibly on a different thread, without keeping a thread blocked during a genuine asynchronous wait.

For example, a ViewModel can call a suspending network API while the UI thread stays free to draw and handle input. I would launch that work in `viewModelScope` so it is cancelled when the ViewModel is cleared. I also check what the API really does: a `suspend` label alone does not make a blocking SDK call safe on Main.

The practical choice is about both lifetime and execution. UI work belongs to a screen-owned scope; blocking I/O belongs behind a main-safe repository method, often using `withContext` on an appropriate dispatcher. If I am loading many items, I limit requests rather than launching one job per item without a bound. Coroutines make waiting cheaper, but they do not remove thread limits, cancellation work, or the need to control concurrency.

## Interview answer — deep senior

If we go deeper, suspension saves the computation's state in a continuation so the current thread can do other work. When the operation completes, a dispatcher schedules the continuation. The coroutine is still executing on a real thread whenever it runs; it is not a replacement for the operating system scheduler. It may resume on another pool thread, while a Main-confined coroutine resumes on Main unless its context changes.

That distinction explains several production bugs. `delay` suspends, but `Thread.sleep` blocks. A synchronous SDK call inside `viewModelScope.launch` can freeze the UI because that scope normally starts on Main. I would put that blocking boundary in the repository, choose an appropriate dispatcher, and check whether cancelling the coroutine actually stops the underlying SDK operation. If it cannot, I would prevent its late callback from publishing into a dead screen.

I would also ask how much work we are starting. `Dispatchers.IO` is intended for blocking I/O, but it is not a universal fixed 64-thread ceiling, and launching a thousand requests can still overload the server, sockets, memory, or rate limit. A semaphore, batching, or an API designed for bulk requests may be the right answer. For CPU-heavy work I would use `Dispatchers.Default` and explicit cancellation checks in long loops. Tests should cover cancellation and late results with a test dispatcher and a controllable fake, rather than assuming that a coroutine's syntax guarantees safe behavior.

## How to answer in the interview

- **Why:** waiting requests need cheap ownership.
- **How:** distinguish the coroutine's continuation, its dispatcher thread, and its parent Job.
- **Trade-off:** cheap waiting does not make CPU or shared state free.
- **Failure case:** a blocking call on Main or a late response after navigation.
- **Production solution:** use a screen-owned scope, a main-safe client, and cancellation-aware result publication.

## Deep-dive talking points

Explain continuations and dispatcher inheritance; compare cooperative cancellation with interrupting a blocking API; discuss structured concurrency and why `GlobalScope` is a poor default for screen work. Distinguish concurrency from parallel execution.

## Follow-up questions

- **Interviewer:** "Does `launch` mean the code runs on a background thread?"
  **Answer:** "No. It inherits its scope's context unless I change it. A `viewModelScope.launch` normally starts on Main, so a blocking call inside it can still freeze the screen."

- **Interviewer:** "What if the SDK only exposes a blocking call?"
  **Answer:** "I would isolate it behind a repository method on an appropriate I/O dispatcher, then test its cancellation behavior. If the SDK cannot stop an in-flight call, I would also guard against a late result reaching a screen that no longer owns it."

- **Interviewer:** "Could you launch a coroutine for every product in a thousand-item list?"
  **Answer:** "Technically I could, but that does not mean I should send a thousand requests at once. I would look for a bulk endpoint or bound concurrency to protect the client and service."

## Self-check rubric

Score one point each (0–5): define coroutine and thread separately; explain suspension without blocking; identify dispatcher and scope roles; diagnose a blocking call on Main; choose an Android owner and justify lifetime. Missing any point shows what to rehearse next; this is self-scoring.

## References and reviewed-on date

- [Kotlin coroutines basics](https://kotlinlang.org/docs/coroutines-basics.html) — suspension, dispatchers, and threads.
- [Android coroutines guidance](https://developer.android.com/kotlin/coroutines) — Android integration and lifecycle guidance.
- [Coroutine IO dispatcher](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-i-o.html) — default parallelism and elastic views.
- [Android ANR diagnosis](https://developer.android.com/topic/performance/anrs/diagnose-and-fix-anrs) — input dispatch timeout.

Technically reviewed against the cited primary documentation on 2026-10-19; agent editorial review, not human verification.
