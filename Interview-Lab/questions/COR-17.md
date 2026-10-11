---
id: "COR-17"
question: "How do timeout, withTimeout, and withTimeoutOrNull work?"
topic: "Kotlin Coroutines & Concurrency"
code: "COR"
group: "B"
phase: 1
priority: "P1"
order: 98
editorial_status: "reviewed"
---

# COR-17

## Original interview question

How do timeout, withTimeout, and withTimeoutOrNull work?

## What the interviewer evaluates

Can the candidate distinguish a coroutine deadline from network commit certainty and handle timeout nullability?

## Explanation in Arabic

`withTimeout` بيعمل deadline للـblock ويلغيه بـ`TimeoutCancellationException` لما الوقت يخلص؛ `withTimeoutOrNull` يرجع `null` بدل رمي الاستثناء عند timeout. الإلغاء تعاوني: لو جوا block SDK blocking وما بيسمعش cancel، مش هيتوقف فورًا. وفي network/payment timeout ما نقدرش نستنتج إن السيرفر ما نفذش الطلب.

## Why it matters and how it works

Timeout is a structured child boundary and can race with a successful return. Use a positive duration and handle nullable domain values separately if `withTimeoutOrNull` is ambiguous. To convert timeout into a domain failure, map it at the correct boundary without swallowing unrelated parent cancellation. Transport timeouts and application deadlines are separate layers.

## Worked example

JVM illustration uses `kotlinx-coroutines-core`; `lookup` is a cancellable, side-effect-free suspend API, so `null` is a safe fallback meaning timeout here.

```kotlin
import kotlinx.coroutines.withTimeoutOrNull

suspend fun cachedLookup(
    lookup: suspend () -> String,
): String = withTimeoutOrNull(2_000) { lookup() } ?: "cached"
```

## Trade-offs and decision criteria

Use `withTimeout` when timeout is exceptional and `withTimeoutOrNull` when a fallback is natural. Do not use `null` to encode timeout if null is also a legitimate result. Set transport deadlines too, and make external writes idempotent/reconcilable rather than assuming cancellation undoes them.

## Failure modes

A `Thread.sleep` inside the block ignores coroutine cancellation and can exceed the deadline. A payment request may reach the server before timeout, so immediately retrying with a new key can charge twice. Closing a returned resource must account for cancellation racing with return.

## Production perspective

An address suggestion API uses a short timeout and cached suggestions as fallback. A checkout payment uses an operation ID, persists pending state, queries server status after ambiguous timeout and retries only with the same idempotency key according to the server contract.

## Interview answer — short

“`withTimeout` cancels a block and throws a timeout cancellation exception; `withTimeoutOrNull` returns null. Both depend on cooperative cancellation. A timeout tells me the client stopped waiting, not whether an external side effect committed.”

## Interview answer — structured

“I use coroutine timeouts to bound how long a caller waits for cancellable work. `withTimeout` throws `TimeoutCancellationException`; `withTimeoutOrNull` gives a nullable fallback path. The operation has to observe cancellation, so a blocking SDK may continue. I also separate this from HTTP client timeouts. For a read-only suggestion request, cached data can be a safe fallback. For a payment write, the timeout is an uncertain outcome: I persist an operation key and reconcile server status rather than assuming failure or creating a fresh retry. Use `withTimeout` when timeout is exceptional and `withTimeoutOrNull` when a fallback is natural. Do not use `null` to encode timeout if null is also a legitimate result. Set transport deadlines too, and make external writes idempotent/reconcilable rather than assuming cancellation undoes them.”

## Interview answer — deep senior

“A timeout is a local deadline in the coroutine tree. The deadline can fire before the caller receives a result, even if the block’s external work already happened. `withTimeout` cancels its child with `TimeoutCancellationException`; `withTimeoutOrNull` maps that timeout to null, which is unsuitable if null also means a valid response. Neither can forcibly interrupt arbitrary blocking Java code. In production I set compatible transport deadlines, make reads cancellable, and design writes with idempotency keys and status reconciliation. I catch and map a timeout at the narrow operation boundary, while letting unrelated parent cancellation propagate. Tests advance virtual time for the coroutine layer and use fake transport outcomes for commit uncertainty. Timeout is a structured child boundary and can race with a successful return. Use a positive duration and handle nullable domain values separately if `withTimeoutOrNull` is ambiguous. To convert timeout into a domain failure, map it at the correct boundary without swallowing unrelated parent cancellation. Transport timeouts and application deadlines are separate layers. A `Thread.sleep` inside the block ignores coroutine cancellation and can exceed the deadline. A payment request may reach the server before timeout, so immediately retrying with a new key can charge twice. Closing a returned resource must account for cancellation racing with return.”

## Deep-dive talking points

Discuss races with return, resource cleanup, blocking code and the difference between client deadline and server transaction status.

## Follow-up questions

- [COR-27](../cor-27/): Can payment timeout justify a fresh retry? **Answer:** no; reconcile using the same operation/idempotency key.
- [COR-29](../cor-29/): Does timeout interrupt a blocking SDK? **Answer:** only if the call cooperates or an appropriate interrupt/cancel mechanism is used.

## Self-check rubric

Can I choose an API, interpret null safely, name cooperative-cancellation limits, and explain ambiguous server outcome?

## References and reviewed-on date

- [Kotlin withTimeout API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/with-timeout.html) — deadline and race semantics.
- [Kotlin withTimeoutOrNull API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/with-timeout-or-null.html) — nullable timeout result.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
