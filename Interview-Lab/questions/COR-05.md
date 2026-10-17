---
id: "COR-05"
question: "Compare launch and async/await."
topic: "Kotlin Coroutines & Concurrency"
code: "COR"
group: "A"
phase: 1
priority: "P1"
order: 86
editorial_status: "reviewed"
---

# COR-05

## Original interview question

Compare launch and async/await.

## What the interviewer evaluates

Whether the candidate chooses a result-bearing `async` versus side-effect `launch`, and understands failure observation.

## Concept and technical explanation

`launch` and `async` both start child coroutines in a scope. `launch` returns a `Job` for work whose caller does not need a result value; `async` returns a `Deferred<T>` whose value is obtained with `await()`. Both inherit the scope context by default and start immediately unless configured otherwise. A `Deferred` stores a failure for `await()`, but a child `async` in an ordinary job hierarchy can also cancel its parent as soon as it fails. Choosing the builder does not replace a decision about ownership, error handling, or whether concurrent calls are actually independent.

## Practical walkthrough (English)

A dashboard needs two independent values before it can show one combined state:

```kotlin
fun refreshDashboard() {
    viewModelScope.launch {
        try {
            val result = coroutineScope {
                val balance = async { accountApi.fetchBalance() }
                val alerts = async { alertApi.fetchAlerts() }
                DashboardUiState.Ready(balance.await(), alerts.await())
            }
            _uiState.value = result
        } catch (e: CancellationException) {
            throw e
        } catch (e: Exception) {
            _uiState.value = DashboardUiState.Error(e)
        }
    }
}
```

The outer `launch` is owned by the ViewModel. The two `async` children overlap while their values are needed together. The example assumes main-safe suspending APIs; `async` does not itself switch to IO. If either required request fails, the ordinary parent fails and the sibling is cancelled. If partial widget success is acceptable, give each result an explicit success/error representation under supervision.

## Explanation in Arabic

`launch` و`async` الاتنين بيبدأوا Coroutines فرعية داخل Scope. `launch` بترجع `Job` للشغل اللي المستدعي مش محتاج منه قيمة، و`async` بترجع `Deferred<T>` آخذ نتيجتها بـ `await()`. الاتنين بيورثوا السياق ويبدأوا فوراً بشكل افتراضي؛ ولا واحد فيهم بينقل الكود تلقائياً للخلفية.

لو `async` فرعية فشلت داخل Job hierarchy عادية، فشلها ممكن يلغي الأب فوراً حتى قبل `await()`. عشان كده بحدد من الأول هل كل النتائج مطلوبة، ولا محتاج نجاح جزئي مع supervision ومعالجة واضحة لكل خطأ.

## Practical walkthrough

في Dashboard محتاجة رصيد وتنبيهات معاً، أبدأ `viewModelScope.launch`، وداخلها `async` لكل API معلّقة وآمنة على Main، ثم أستنى القيمتين وأبني الـ UI state. `async` لا تعني Background Thread؛ لو API حظرية أنقلها عند الحد اللي يملكها. لو واحد من الطلبين فشل، أعرض خطأ وأترك `CancellationException` تمر من غير تحويلها لفشل عادي. لو كل كارت مستقل، أمثل نجاح وخطأ كل كارت تحت supervision بدل ما ألغي الكل.

## Why it matters and how it works

Both builders start immediately by default and inherit the scope context. `join` waits for termination but does not return a value; `await` waits and retrieves the value, throwing its failure. In a normal parent scope, child failure can cancel the parent even if the `Deferred` is never awaited. Concurrent `async` calls only help when independent latency can overlap.

## Worked example

JVM example assumes `kotlinx-coroutines-core` and two main-safe suspend API functions supplied by the caller.

```kotlin
import kotlinx.coroutines.async
import kotlinx.coroutines.coroutineScope

suspend fun dashboard(
    account: suspend () -> String,
    alerts: suspend () -> Int,
): Pair<String, Int> = coroutineScope {
    val a = async { account() }
    val n = async { alerts() }
    a.await() to n.await()
}
```

## Trade-offs and decision criteria

Use `async` for concurrent values, `launch` for owned work where only completion matters, and a direct suspend call for sequential work. Excess parallelism can overload an API; set limits when fan-out grows. Do not use `async` just to rename a sequential operation.

## Failure modes

`try/catch` around a later `await` may be too late to prevent a normal parent from being cancelled by an earlier child failure. Use a supervised boundary for independent failures, or catch inside the child to produce a typed result; always rethrow cancellation.

## Production perspective

A home screen fetches account and notification count concurrently because the APIs are independent and both are needed for the complete header. The ViewModel owns the call and cancellation; the repository returns a pair or a typed failure, while telemetry records which dependency failed.

## Interview answer — short

`launch` starts work and returns a `Job` to cancel or wait for it. `async` starts work that will produce a value and returns a `Deferred` whose result I get with `await()`. I use `async` when concurrent results help the caller, and I keep both inside a scope that owns their cancellation and failures.

## Interview answer — structured

I choose based on whether the caller needs a result. `launch` returns a `Job`, so it fits a screen event that updates state but does not return a value to the launching code. `async` returns a `Deferred<T>` and `await()` gives me the value. If a screen needs a profile and permissions and those requests are independent, I can start both with `async` inside `coroutineScope`, then await both before building the screen state.

I would not use `async` just to make every suspend call look more advanced. If one request depends on the other, sequential calls are clearer and do not add useful concurrency. Both builders inherit the owner's context and produce child jobs, so neither is a free-floating background task by default.

The failure behavior is the part people miss. A child `async` failure inside a regular scope can cancel the parent and siblings before I reach `await()`. Catching only around `await()` may be too late to keep the scope alive. If partial success is required, I would use supervision and model each result or error explicitly.

## Interview answer — deep senior

`launch` and `async` both create child coroutines in the supplied scope. `launch` exposes completion and cancellation through `Job`; `async` adds a result through `Deferred<T>`. `await()` suspends until the result is ready and rethrows a failure stored by the deferred.

A root `async` keeps its exception for `await()`, but a child `async` in an ordinary scope still reports failure to its parent immediately. That parent can already be cancelling when the caller catches an exception from `await()`. I therefore choose the failure boundary before starting work: `coroutineScope` when all results are required; `supervisorScope` plus explicit per-task handling when partial results are valid. A `launch` child under supervision also needs its own error handling because no caller awaits a value from it.

I would also avoid a detached `async` whose `Deferred` escapes its owner's lifetime. It becomes easy to lose cancellation or forget to observe the failure. For truly sequential work, plain suspend calls give a simpler failure path. If I use `CoroutineStart.LAZY`, I remember that awaiting lazy deferreds one by one can remove the intended concurrency unless I start them before waiting.

If the values feed a single UI state, I return them from a local `coroutineScope` to the outer ViewModel operation and catch the aggregate failure outside that boundary. That avoids publishing one half of a required pair. For independent widgets I model each outcome separately so one error does not silently become a successful empty value.

## How to answer in the interview

- **Why:** choose a builder by whether the caller needs a value.
- **How:** launch returns Job; async returns Deferred and await rethrows its stored failure.
- **Trade-off:** parallel reads may reduce latency but consume capacity.
- **Failure case:** unawaited Deferred or a late catch after parent cancellation.
- **Production solution:** use direct suspend calls for sequential work and explicit supervised outcomes for optional results.

## Deep-dive talking points

Explain eager start, `join` versus `await`, ordinary parent failure, lazy start caveats, and when parallel latency really helps.

## Follow-up questions

- **Interviewer:** "I caught the error from `await()`. Why did the sibling still get cancelled?"
  **Answer:** "The failing `async` was a child of an ordinary scope. It reported failure to its parent as soon as it failed, before my catch around `await()` could change the parent's state. If partial success is the contract, I would choose supervision and handle each result."

- **Interviewer:** "Would you use `async` for one network request?"
  **Answer:** "Usually no. A plain suspend call is simpler if there is nothing useful to run concurrently. `async` helps when I really need overlapping results."

- **Interviewer:** "What happens if you create two lazy deferreds and await the first before the second?"
  **Answer:** "The first `await()` starts the first task and waits for it. The second has not started yet, so I lose the overlap. I would start both first or use the default eager start if concurrency is intended."

## Self-check rubric

Can I choose the right builder, predict result and exception behavior, justify concurrency, and describe an Android owner?

## References and reviewed-on date

- [Kotlin coroutines basics](https://kotlinlang.org/docs/coroutines-basics.html) — `launch`, `async`, Job and Deferred.
- [Coroutine exceptions](https://kotlinlang.org/docs/exception-handling.html) — failure observation and propagation.

Technically reviewed against primary documentation on 2026-10-17.
