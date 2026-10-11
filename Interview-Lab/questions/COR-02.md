---
id: "COR-02"
question: "What does suspend mean? Does a suspend function imply background execution?"
topic: "Kotlin Coroutines & Concurrency"
code: "COR"
group: "A"
phase: 1
priority: "P1"
order: 83
editorial_status: "reviewed"
---

# COR-02

## Original interview question

What does suspend mean? Does a suspend function imply background execution?

## What the interviewer evaluates

- Precise meaning of a suspending declaration and a suspension point.
- Recognition that `suspend` alone does not choose a dispatcher or make blocking calls safe.
- Placement of the main-safety decision at the API boundary that owns the blocking operation.

## Explanation in Arabic

`suspend` معناها إن الدالة تقدر تنادي suspending functions وتتوقف بشكل تعاوني عند نقطة انتظار. مش معناها إنها بتشتغل تلقائي على background thread. لو استدعيتها من coroutine على Main ونفذت جواها `Thread.sleep` أو driver synchronous، الـMain هيتحجز. النقل لـdispatcher مناسب قرار صريح عند الجزء اللي فعلاً blocking؛ أما API أصلًا non-blocking ومكتوب إنها main-safe فمش لازم نحط حوالينها `withContext(IO)` لمجرد إن اسمها `suspend`.

## Why it matters and how it works

The `suspend` modifier changes how a function participates in coroutine continuations; it does not launch a new coroutine or select a thread. Execution initially follows the caller's context. A real suspending call can release the current thread. `withContext(dispatcher)` changes context for its block and returns to the caller context afterward. It cannot magically cancel an uncooperative blocking driver in mid-call; cancellation may wait until that call returns.

## Worked example

This JVM illustration assumes `kotlinx-coroutines-core` and a legacy blocking API. The repository owns the dispatcher because it knows the driver contract; callers can use it safely from Main. Production code should inject the dispatcher for deterministic tests.

```kotlin
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

interface BlockingProfileDriver {
    fun readProfile(id: String): String
}

class ProfileRepository(
    private val driver: BlockingProfileDriver,
    private val io: CoroutineDispatcher = Dispatchers.IO,
) {
    suspend fun readProfile(id: String): String = withContext(io) {
        driver.readProfile(id) // synchronous I/O runs on the chosen dispatcher
    }
}
```

## Trade-offs and decision criteria

Move blocking I/O off Main, but do not scatter dispatcher switches across every caller. `Dispatchers.IO` is meant for blocking I/O; `Default` fits CPU work. A non-blocking suspending client may already be main-safe, so an extra IO hop can add complexity without benefit. Verify the library contract instead of using a blanket rule.

## Failure modes

**Wrong:** changing `fun read()` to `suspend fun read()` and leaving a synchronous disk read on Main. The UI still freezes. **Fix:** identify the blocking boundary and wrap it in `withContext` or use a truly asynchronous API. Also avoid `runBlocking` on an Android UI callback: it blocks Main while waiting and defeats the purpose.

## Production perspective

A screen ViewModel calls a repository with a documented main-safe suspend contract. Inside that repository, a legacy SDK read is dispatched away from Main. If the user leaves the screen, the call's result must not update stale UI. The SDK may ignore cancellation; design timeouts and stale-result handling accordingly rather than promising immediate interruption.

## Interview answer — short

“`suspend` means a function can suspend and call other suspending functions. It does not start a coroutine or move execution to a background thread. The caller's context applies until code explicitly changes it. I make blocking operations main-safe at the data boundary, usually with an appropriate dispatcher.”

## Interview answer — structured

“A suspend function is compiled so a coroutine can pause and resume at suspension points. The modifier itself says nothing about the executing thread. If a ViewModel coroutine on Main calls a suspend function that invokes a synchronous driver, Main can still block. I put that driver call inside `withContext` with an injected IO dispatcher in the repository, while a genuinely non-blocking suspending API may need no switch. I also test cancellation and timeouts against the real driver, because a blocking operation may not stop just because its coroutine was cancelled.”

## Interview answer — deep senior

“The `suspend` modifier changes the call contract so a coroutine can pause at suspension points; it neither creates a new coroutine nor selects a thread. The executing dispatcher is inherited from the caller unless a block explicitly changes context. On Main, a suspending Retrofit API can await network I/O without blocking, but a synchronous database driver called inside a suspend function still blocks Main. I make each repository API main-safe at its implementation boundary, injecting a dispatcher for genuinely blocking work, and test cancellation with the real driver because cancellation of a coroutine cannot forcibly make a blocking API cooperative. That distinction matters when diagnosing an ANR despite apparently asynchronous code.”

## Deep-dive talking points

Discuss continuation passing, dispatcher inheritance, main-safe API contracts, testing with an injected dispatcher, and how uncooperative blocking work interacts with cancellation.

## Follow-up questions

- [COR-01](../cor-01/): How is a coroutine different from a thread? **Answer:** the coroutine is suspendable work; the thread executes its instructions until suspension or completion.
- [COR-09](../cor-09/): What does `withContext` change? **Answer:** it executes a block in another coroutine context and returns its result; it cannot by itself make an uncooperative driver cancellable.
- [COR-16](../cor-16/): How should cancellation propagate? **Answer:** let `CancellationException` escape ordinary error handling so the parent hierarchy can stop obsolete work.

## Self-check rubric

Score 0–5, one point each: define `suspend`; state that it does not select a thread; trace caller context; show an appropriate main-safe repository boundary; mention blocking/cancellation caveats. Use missing points as rehearsal targets.

## References and reviewed-on date

- [Kotlin coroutines basics](https://kotlinlang.org/docs/coroutines-basics.html) — suspending functions and dispatchers.
- [Android coroutines guidance](https://developer.android.com/kotlin/coroutines) — main safety and Android scope use.

Technically reviewed against the linked primary documentation on 2026-10-11. The code is a JVM illustration, not an instrumented Android test.
