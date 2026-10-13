---
id: "COR-07"
question: "What do Dispatchers.Main, IO, Default, and Unconfined do?"
topic: "Kotlin Coroutines & Concurrency"
code: "COR"
group: "A"
phase: 1
priority: "P1"
order: 88
editorial_status: "reviewed"
---

# COR-07

## Original interview question

What do Dispatchers.Main, IO, Default, and Unconfined do?

## What the interviewer evaluates

Whether the candidate maps dispatchers to execution resources while rejecting `suspend` as automatic backgrounding.

## Explanation in Arabic

`Dispatchers.Main` للتعامل مع UI على Android، و`IO` معمول للـblocking I/O، و`Default` مناسب CPU-intensive work. `Unconfined` بيبدأ في thread المستدعي لحد أول suspension وبعدها ممكن يكمل حسب suspending function؛ مش اختيار آمن كـdefault لواجهة Android. اختيار dispatcher لازم يبقى بحسب طبيعة الـAPI والـscope، مش لمجرد إن الدالة `suspend`.

## Practical walkthrough

لو repository بيقرأ ملف ثم يفك ضغطه، قراءة الملف synchronous تتعمل على `IO`، وفك الضغط CPU-heavy على `Default`، وبعدها UI تتحدّث على `Main`. كل نقلة لها سبب واضح. `Unconfined` ممكن يكمل على thread مختلف بعد أول suspension، فمش مكان مناسب لكود view. وخلي بالك: لو network API suspend ومكتوب main-safe، إطلاقها من Main ممكن يكون صحيح.

## Why it matters and how it works

Dispatcher is a context element that decides where continuation executes. Main targets the Android UI dispatcher, Default uses a shared CPU-oriented pool, and IO is elastic for blocking calls. `Unconfined` does not confine execution to one thread. Suspending operations may free a thread; synchronous calls still occupy their selected thread.

## Worked example

Android repository illustration; `blockingDecoder` is a synchronous CPU operation and `readFile` is synchronous disk I/O.

```kotlin
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

suspend fun readAndDecode(
    readFile: () -> ByteArray,
    blockingDecoder: (ByteArray) -> String,
): String {
    val bytes = withContext(Dispatchers.IO) { readFile() }
    return withContext(Dispatchers.Default) { blockingDecoder(bytes) }
}
```

## Trade-offs and decision criteria

Keep UI mutations on Main; put true blocking disk/network calls behind an IO boundary; use Default for CPU work. Some suspending clients are already main-safe, so an extra IO hop is unnecessary. Avoid hard-coded dispatchers in hard-to-test code; inject when tests need control.

## Failure modes

Using Default for hundreds of long blocking calls can starve CPU tasks; using Main for synchronous decoding causes jank or ANR. Assuming `Unconfined` always resumes on Main can produce a thread-confinement bug. `withContext(IO)` does not make a blocking driver promptly cancellable.

## Production perspective

A photo repository reads bytes from a legacy file API on IO, decodes thumbnail data on Default and exposes a main-safe suspend function. The ViewModel launches from Main and observes a result. Benchmark decode cost, bound parallel operations, and test UI responsiveness.

## Interview answer — short

“Main is the Android UI dispatcher, IO is intended for blocking I/O, Default for CPU work, and Unconfined has no stable thread confinement. `suspend` does not choose any of them; I switch context at the operation that owns blocking or CPU work.”

## Interview answer — structured

“Dispatchers answer where instructions run, not how long work lives. Main is where I update Android UI. IO provides capacity for blocking I/O; Default is a shared CPU pool. Unconfined starts in the caller thread and may resume elsewhere after suspension, so it is rarely appropriate for Android UI code. I expose main-safe repository methods and switch only around a synchronous blocking or heavy CPU boundary. I also verify the API contract, because a non-blocking suspend client may need no dispatcher switch.”

## Interview answer — deep senior

“For dispatcher selection I examine whether an operation blocks a thread, burns CPU, or mutates UI. A suspending network client can release the caller thread and be main-safe; a synchronous SDK call inside a `suspend` function still blocks the current dispatcher. I move that SDK boundary to IO, CPU decoding to Default, and render only on Main. I avoid Unconfined because its resume thread follows the suspending function and does not establish UI confinement. IO has capacity for blocking tasks, but unlimited fan-out can still strain memory, connections or the server, so I bound concurrency separately. Tests inject dispatchers and verify main safety; cancellation requires cooperation from the underlying operation. I would inspect the hot path rather than applying IO everywhere. For a file-and-decode flow, synchronous read occupies an IO worker, CPU decode belongs on Default, and rendering returns to Main. IO's elastic views can increase concurrent blocking operations, so an external API may still need a semaphore or rate limit. An `Unconfined` continuation has no stable UI-thread contract, which makes it a poor production default for view state.”

## How to answer in the interview

- **Why:** the dispatcher must fit the work, not the function name.
- **How:** Main renders, IO accommodates blocking I/O, Default runs CPU work, Unconfined has no stable thread guarantee.
- **Trade-off:** switches cost complexity and IO is not backpressure.
- **Failure case:** CPU decoding on Main or blocking on Default at scale.
- **Production solution:** place switches at repository boundaries and limit fan-out separately.

## Deep-dive talking points

Trace a coroutine across dispatcher switches and suspension; distinguish thread capacity, concurrency limits and cancellation of a blocking driver.

## Follow-up questions

- [COR-02](../cor-02/): Does `suspend` select IO? **Answer:** no; caller context remains until an explicit context switch.
- [COR-21](../cor-21/): How limit load? **Answer:** a semaphore or constrained parallelism limits active operations beyond dispatcher selection.

## Self-check rubric

Can I map each dispatcher, reject `Unconfined` for UI confinement, identify a blocking boundary, and explain that cancellation remains cooperative?

## References and reviewed-on date

- [Kotlin coroutines basics](https://kotlinlang.org/docs/coroutines-basics.html) — dispatcher and context.
- [Android coroutines guidance](https://developer.android.com/kotlin/coroutines) — main safety and repository boundaries.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-13; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
