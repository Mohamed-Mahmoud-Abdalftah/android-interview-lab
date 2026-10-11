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

## Explanation in Arabic

`launch` بيبدأ شغل ويرجع `Job` علشان تستنى نهايته أو تلغيه، من غير قيمة مرجعة. `async` بيرجع `Deferred<T>` يمثل نتيجة مستقبلية و`await` بيرجعها أو يرمي الخطأ. الاتنين بياخدوا scope وبيفضلوا جزء من شجرة الـJob؛ استخدام `async` من غير `await` مش طريقة آمنة لإخفاء exception.

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

“`launch` returns a Job for work without a result; `async` returns a Deferred whose `await` yields a value or throws. Both inherit scope ownership. I use `async` for independent values I will actually await and a direct suspend call for sequential work.”

## Interview answer — structured

“The choice starts with the API contract. `launch` is appropriate for an owned side task and gives cancellation and completion through Job. `async` represents a value-producing concurrent computation; `await` suspends and returns or throws. Neither is fire-and-forget when launched in a structured scope. If I need account and alerts independently, I start both with `async` and then await them inside `coroutineScope`. If one failure should not cancel the other, I change the failure boundary deliberately and return separate outcomes. Use `async` for concurrent values, `launch` for owned work where only completion matters, and a direct suspend call for sequential work. Excess parallelism can overload an API; set limits when fan-out grows. Do not use `async` just to rename a sequential operation.”

## Interview answer — deep senior

“Builders do not replace reasoning about dependency and failure. Both `launch` and `async` inherit the parent Job unless a new one is supplied, and both start eagerly by default. `Deferred` stores a result or exception for `await`, but child failure in a normal scope still cancels its parent. For an all-or-nothing header I use a structured `coroutineScope` and let a failed child cancel siblings. For independent cards I use supervision with explicit per-child results, and I distinguish user cancellation from an API error. I also cap fan-out, measure actual latency, and avoid extra coroutines for sequential calls that gain nothing from concurrency. Both builders start immediately by default and inherit the scope context. `join` waits for termination but does not return a value; `await` waits and retrieves the value, throwing its failure. In a normal parent scope, child failure can cancel the parent even if the `Deferred` is never awaited. Concurrent `async` calls only help when independent latency can overlap. `try/catch` around a later `await` may be too late to prevent a normal parent from being cancelled by an earlier child failure. Use a supervised boundary for independent failures, or catch inside the child to produce a typed result; always rethrow cancellation. A home screen fetches account and notification count concurrently because the APIs are independent and both are needed for the complete header.”

## Deep-dive talking points

Explain eager start, `join` versus `await`, ordinary parent failure, lazy start caveats, and when parallel latency really helps.

## Follow-up questions

- [COR-13](../cor-13/): Does an unawaited failed child matter? **Answer:** in an ordinary parent, yes; failure can cancel the parent tree.
- [COR-26](../cor-26/): How preserve partial success? **Answer:** supervise independent children and capture each failure without swallowing cancellation.

## Self-check rubric

Can I choose the right builder, predict result and exception behavior, justify concurrency, and describe an Android owner?

## References and reviewed-on date

- [Kotlin coroutines basics](https://kotlinlang.org/docs/coroutines-basics.html) — `launch`, `async`, Job and Deferred.
- [Coroutine exceptions](https://kotlinlang.org/docs/exception-handling.html) — failure observation and propagation.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
