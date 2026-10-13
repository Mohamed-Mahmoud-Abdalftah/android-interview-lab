---
id: "COR-31"
question: "A coroutine starts on Main, calls blocking library code, and causes ANR. Explain the exact failure and fix."
topic: "Kotlin Coroutines & Concurrency"
code: "COR"
group: "C"
phase: 1
priority: "P1"
order: 112
editorial_status: "reviewed"
---

# COR-31

## Original interview question

A coroutine starts on Main, calls blocking library code, and causes ANR. Explain the exact failure and fix.

## What the interviewer evaluates

Diagnose why a coroutine on Main can still produce jank/ANR and provide a verifiable fix.

## Explanation in Arabic

`launch` على `Dispatchers.Main` بيشتغل على UI thread. لو جوه `suspend fun` نادينا blocking library بتمسك thread، الـLooper مش هيعالج input أو draw لحد ما النداء يرجع؛ كلمة `suspend` لا تجعلها non-blocking. نحدد stack من ANR traces أو profiler، ننقل boundary إلى IO أو API async، ونختبر responsiveness مع driver الحقيقي.

## Practical walkthrough

في ANR trace هتلاقي main Looper دخل `fetchBlocking()` ولم يرجع؛ مفيش suspension حقيقية أثناء النداء حتى لو الدالة الخارجية `suspend`. التشخيص يبدأ من stack trace والـprofiler عشان تحدد blocking boundary. خلي repository يعمل `withContext(IO)` حول النداء أو بدّله بـasync client؛ حدّ parallel calls واختبر library الحقيقي، لأن cancel قد لا يوقفه.

## Why it matters and how it works

A coroutine only releases Main at genuine suspension. `Thread.sleep`, synchronous disk/network or a blocking Binder/SDK call inside Main continues to occupy it. `withContext(IO)` protects Main for known blocking I/O, while heavy CPU belongs on Default. The chosen library may not respond promptly to cancellation; set native timeouts and bound concurrent calls.

## Worked example

Android/JVM repository example assumes `LegacyClient.fetchBlocking` is synchronous. ViewModel calls the main-safe suspending repository method.

```kotlin
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

interface LegacyClient { fun fetchBlocking(id: String): String }
class LegacyRepository(private val client: LegacyClient) {
    suspend fun fetch(id: String): String =
        withContext(Dispatchers.IO) { client.fetchBlocking(id) }
}
```

## Trade-offs and decision criteria

Prefer a true async client if maintained and cancellable; IO dispatch is a pragmatic wrapper for legacy blocking I/O. More IO threads do not fix a saturated server or unbounded work. Avoid using `runBlocking` from UI callbacks, which intentionally blocks Main.

## Failure modes

Calling `client.fetchBlocking()` directly inside `viewModelScope.launch` can freeze frames and trigger ANR. A superficial fix of declaring it `suspend` changes no execution behavior. If the SDK ignores cancellation, late results must be discarded and requests bounded.

## Production perspective

An ANR report shows Main parked in a third-party synchronous SDK. The team reproduces it with a slow fake and UI frame monitoring, moves the boundary to an injected IO dispatcher, configures SDK timeout and checks release traces. It also limits concurrent calls and replaces the SDK when feasible.

## Interview answer — short

“A coroutine on Main still executes on the UI thread until it suspends. A blocking library call prevents the Looper from drawing or handling input and can cause ANR. I confirm the blocking stack in traces, move that boundary off Main or use an async API, then test responsiveness and cancellation.”

## Interview answer — structured

“I would not assume `viewModelScope.launch` means background execution. It usually starts on Main. If a suspend wrapper calls a synchronous SDK, the SDK occupies Main until it returns, delaying frames and input. I inspect the ANR trace and profiler to identify the actual blocking method, then make the repository main-safe by switching that call to IO or replacing it with a non-blocking API. CPU-heavy work goes to Default. I test the slow path, set driver timeouts and handle late results if the SDK ignores cancellation.”

## Interview answer — deep senior

“The precise failure chain is dispatcher inheritance, synchronous call and blocked Looper. The coroutine starts in Main; the call has no suspension point, so no continuation is parked and the same UI thread remains inside the SDK. The system sees input or lifecycle work unserved long enough to report an ANR. I use production traces to confirm this path, because the apparent coroutine frame alone is not proof of the blocker. The repository owns the fix: a documented main-safe suspend contract, `withContext(IO)` for legacy blocking I/O or a genuine asynchronous SDK, plus concurrency limits and timeouts. I regression-test under artificial slow I/O and monitor ANR rates. Cancellation is separate; moving threads does not make an uncooperative call stoppable. To diagnose an ANR I would inspect the main thread trace and follow the call into the synchronous SDK; merely seeing `launch` or `suspend` in the source proves nothing about blocking. A main-safe repository can switch that specific call to an IO dispatcher, or preferably use an async client with a cancellation contract. I would cap outstanding requests, measure latency and test navigation cancellation, because an uncooperative SDK may still return after the ViewModel is gone.”

## How to answer in the interview

- **Why:** the UI Looper cannot render or handle input while a synchronous call occupies Main.
- **How:** trace dispatcher inheritance and the blocking stack frame.
- **Trade-off:** IO offload restores responsiveness but costs a worker; an async client is preferable when available.
- **Failure case:** merely adding suspend or unbounded IO fan-out.
- **Production solution:** main-safe repository boundary, limits, and trace-based verification.

## Deep-dive talking points

Trace Looper starvation, identify blocking stack evidence and verify the fix under slow-library conditions.

## Follow-up questions

- [COR-02](../cor-02/): Does `suspend` imply background work? **Answer:** no.
- [COR-29](../cor-29/): Will IO fix cancellation? **Answer:** it protects Main but may not interrupt the SDK.

## Self-check rubric

Can I explain the exact UI-thread blockage, collect trace evidence, choose IO versus Default, and test a slow driver?

## References and reviewed-on date

- [Android coroutines guidance](https://developer.android.com/kotlin/coroutines) — main safety.
- [Android ANR guidance](https://developer.android.com/topic/performance/vitals/anr) — diagnosis and traces.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-13; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
