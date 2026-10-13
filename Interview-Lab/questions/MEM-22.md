---
id: "MEM-22"
question: "Your main thread is blocked even though you launched a coroutine. Why?"
topic: "Memory Management, ANR & Performance"
code: "MEM"
group: "C"
phase: 1
priority: "P1"
order: 77
editorial_status: "reviewed"
---

# MEM-22

## Original interview question

Your main thread is blocked even though you launched a coroutine. Why?

## What the interviewer evaluates

- Explain dispatcher inheritance and distinguish suspension from blocking.
- Diagnose the actual Main-thread operation with a trace instead of assuming `launch` moved it.
- Make the blocking boundary main-safe while respecting cancellation and resource limits.

## Explanation in Arabic

`launch` بيبدأ coroutine، لكنه مش أمر “انقل الشغل لخلفية”. لو استدعيت `viewModelScope.launch` فغالبًا البداية على Main؛ `Thread.sleep` أو SDK synchronous أو loop CPU جواه هيحجز Main ويعمل jank أو ANR. الـsuspend function كمان مش ضمان إنها non-blocking: ممكن حد كتبها وبتنادي driver blocking. الحل إنك تحدد السطر اللي واقف عليه Main من trace، وتخلي طبقة البيانات main-safe بـ`withContext` على dispatcher مناسب للشغل blocking، أو تستخدم API asynchronous فعلًا. وخلي بالك إن إلغاء coroutine مش هيوقف driver blocking غصبًا عنه.

## Practical walkthrough

في `viewModelScope.launch` استدعاء `client.blockingLoad()` هيشتغل على Main لو مفيش context switch حقيقي. في ANR trace شوف هل Main بتنفذ SDK، ولا مستنية lock أو Binder. `withContext(ioDispatcher)` يحمي Main من blocking I/O لكن driver ممكن يفضل شغال بعد cancellation، ومئات طلبات متزامنة تستهلك threads. اعمل limit للconcurrency، timeout حقيقي حسب client، واختبر خروج المستخدم بسرعة من الشاشة.

## Why it matters and how it works

Coroutines execute on threads selected by their context. A coroutine launched from `viewModelScope` uses Main by default; it only releases that thread at a genuine suspension point. A plain synchronous call or CPU loop runs until it completes, yields cooperatively, or changes context. `withContext(ioDispatcher)` can move a blocking I/O boundary off Main; CPU-heavy work fits a CPU-oriented dispatcher. A non-blocking suspend API that already uses appropriate internal threads need not be wrapped blindly. Main-safety is a contract of the called layer, not the `suspend` keyword.

## Worked example

Illustrative Android repository with an injected dispatcher and a blocking legacy client. The surrounding app supplies `LegacyClient` and `Receipt`, and tests can inject a test dispatcher. The driver itself may not respond promptly to coroutine cancellation.

```kotlin
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.withContext

class ReceiptRepository(
    private val client: LegacyClient,
    private val ioDispatcher: CoroutineDispatcher
) {
    suspend fun load(id: String): Receipt = withContext(ioDispatcher) {
        client.blockingLoad(id)
    }
}
```

The ViewModel may call `repository.load(id)` from Main. Add timeout/driver cancellation behavior based on the real client contract, not by assuming `withContext` can interrupt it.

## Trade-offs and decision criteria

Moving a blocking call protects Main but still consumes a worker thread and can exhaust an unbounded pool under load. Prefer truly asynchronous APIs when available. For CPU work, use a CPU-limited dispatcher and measure; for I/O, bound concurrency where the driver or server has limits. Avoid wrapping every suspend function in `Dispatchers.IO`, which can add unnecessary hops and obscure ownership.

## Failure modes

A developer catches all `Exception`, including `CancellationException`, and continues a stale request after the screen leaves. A repository switches to IO around a driver but permits hundreds of concurrent blocking requests, causing starvation elsewhere. A slow Binder call on Main may not be obvious from app code. Inspect ANR clusters and Perfetto thread state, add StrictMode in development where appropriate, and test cancellation with the actual driver.

## Production perspective

For a receipt screen with rare ANRs, correlate ANR traces with network and database operations. If Main waits on a synchronous SDK call, move that boundary into a repository using an injected bounded dispatcher or migrate to an asynchronous API. Instrument queue depth and latency, and test rapid navigation away so stale work cannot update the new screen. Keep the payment attempt ID durable; moving its network call off Main does not make it safe to repeat after a timeout.

## Interview answer — short

“A coroutine still runs on a thread. `viewModelScope.launch` starts on Main by default, and a blocking call inside it blocks Main until it returns. I inspect the trace, make the blocking repository boundary main-safe with an appropriate dispatcher or async API, and verify cancellation behavior.”

## Interview answer — structured

“`launch` creates a coroutine, not a background thread. A real suspension such as an asynchronous wait frees Main, but `Thread.sleep`, a synchronous SDK, CPU loop, or lock wait does not. I inspect the ANR main-thread stack and its blockers, then move the blocking call to an injected dispatcher at the data boundary or replace it with a non-blocking API. I choose IO versus CPU execution deliberately and test cancellation, because a blocking driver may keep running after its coroutine is cancelled.”

## Interview answer — deep senior

“I separate execution context, suspension, and driver behavior. A ViewModel coroutine inherits Main, and `suspend` does not imply a thread switch. If the main thread is blocked I first gather ANR traces and, ideally, Perfetto scheduling evidence to identify whether it is CPU work, synchronous I/O, Binder, or lock contention. I make the responsible layer main-safe: an injected IO context for unavoidable blocking I/O, a CPU-limited context for computation, or a genuinely async API. I bound concurrency, preserve `CancellationException`, and verify how the driver handles cancellation. If the call is a payment operation, dispatcher choice solves responsiveness only; idempotent recovery and durable identity remain separate requirements. In a concrete failure, `viewModelScope.launch` invokes a synchronous legacy client and blocks Main until the call returns. I move that boundary behind an injected dispatcher or async API, then cap parallel requests so a worker pool cannot be exhausted. A driver that ignores cancellation needs its own timeout and ownership policy; `withContext` alone cannot interrupt it.”

## How to answer in the interview

- **Why:** Separate coroutine context from true suspension.
- **How:** Trace Main and switch at the responsible repository boundary.
- **Trade-off:** Worker dispatch consumes threads and needs concurrency limits.
- **Failure case:** A blocking driver can ignore coroutine cancellation.
- **Production solution:** Test rapid navigation and durable operation identity.

## Deep-dive talking points

Explain dispatcher inheritance, real suspension, noncooperative blocking APIs, Main-thread lock/Binder waits, bounded worker pools, cancellation propagation, and why responsiveness does not equal transaction safety.

## Follow-up questions

- [COR-02](../cor-02/): Does `suspend` mean background execution? **Answer:** no; caller context applies until code explicitly changes it.
- [COR-16](../cor-16/): Why rethrow `CancellationException`? **Answer:** swallowing it breaks cooperative cancellation and can let obsolete work continue.
- [MEM-25](../mem-25/): What if Main waits for a database lock? **Answer:** inspect the lock holder and transaction scope, then remove long contention rather than just changing the caller's dispatcher.

## Self-check rubric

State the default ViewModel coroutine context; name three blocking operations; use a trace to classify the stall; choose a bounded dispatcher or async replacement; and describe a cancellation limitation.

## References and reviewed-on date

- [Kotlin coroutines on Android](https://developer.android.com/kotlin/coroutines) — main-safety and dispatcher examples.
- [Coroutines best practices](https://developer.android.com/kotlin/coroutines/coroutines-best-practices) — repository responsibility for blocking calls.
- [Diagnose and fix ANRs](https://developer.android.com/topic/performance/anrs/diagnose-and-fix-anrs) — trace-led diagnosis.

Technically reviewed against these primary sources on 2026-10-13 by automated editorial review. The snippet is illustrative; the legacy client and Android integration were not compiled here.
