---
id: "KOT-07"
question: "What are higher-order functions and lambdas?"
topic: "Kotlin Core & Advanced"
code: "KOT"
group: "A"
phase: 1
priority: "P1"
order: 7
editorial_status: "reviewed"
---

# KOT-07

## Original interview question

What are higher-order functions and lambdas?

## What the interviewer evaluates

Define function values and higher-order functions, including capture and cost implications.

## Explanation in Arabic

Higher-order function يعني function بتاخد function كـparameter أو بترجّع function. Lambda طريقة مختصرة لكتابة function value، وممكن تقفل على variables من scope الخارجي. ده مفيد في collection transformations، callbacks، وواجهات APIs زي transactions. لكن callback مخزّن مدة طويلة ممكن يمسك Activity reference ويسبب leak، وlambda متكررة على hot path ممكن تعمل allocations حسب compilation والسياق؛ قِس قبل ما تستخدم `inline` تلقائيًا.

## Why it matters and how it works

Functions as values allow behavior to be composed without subclass boilerplate. Captures preserve access to surrounding state, which is powerful but changes lifetime and sometimes allocation. A higher-order API should say whether it calls the callback immediately, stores it, or invokes it multiple times.

## Worked example

Runnable JVM example; the predicate is called synchronously for each candidate.
```kotlin
fun <T> firstMatching(items: List<T>, accept: (T) -> Boolean): T? =
    items.firstOrNull(accept)

fun main() {
    val limit = 10
    println(firstMatching(listOf(3, 12, 8)) { it > limit })
}
```

## Trade-offs and decision criteria

A lambda is concise for one behavior; an interface or named class is clearer when there are multiple operations, identity, or long-lived lifecycle. Function references can be readable but still require checking capture and dispatch semantics. Inlining may remove call overhead but duplicates body bytecode.

## Failure modes

A repository retains a screen callback that captures an Activity; the Activity remains reachable after rotation. Prefer lifecycle-owned collection or remove the listener. Another failure is assuming a callback runs once when an API may retry or invoke it concurrently; document invocation rules.

## Production perspective

A validation pipeline accepts small predicates and applies them synchronously. For asynchronous search, a ViewModel collects a Flow in `viewModelScope` rather than registering an unowned callback that can outlive the screen.

## Interview answer — short

A higher-order function takes or returns a function; a lambda is a compact function value. It helps compose behavior, but I check whether it captures state and whether the API stores or repeatedly invokes it.

## Interview answer — structured

Kotlin lets a function accept another function, for example a predicate passed to `firstOrNull`. The lambda can capture local values, which keeps the code concise. The important API contract is invocation: synchronous or deferred, once or many times, and on which thread. A deferred callback capturing an Activity can leak it. For performance-sensitive code I measure allocations and only consider inline where its trade-offs are justified. Suppose I pass a predicate to find a matching product: the function decides when and how often that predicate runs. If the predicate closes over a screen reference and is stored in a long-lived registry, I can leak the screen. I therefore review whether a higher-order API invokes immediately, retains the callback, or calls concurrently. A named interface can be preferable when the behavior has several methods or a lifecycle.

## Interview answer — deep senior

I treat higher-order functions as behavioral dependencies. A caller should know whether the lambda can return non-locally, whether it is invoked under a lock, and whether it can escape the call. Captures may retain resources and complicate lifecycle management. In a tight loop, generated allocation and call overhead may matter, but JVM optimization is contextual; profiling beats blanket inlining. For long-lived asynchronous subscriptions I give them an explicit owner and cancellation path. I see lambdas as a way to pass behavior with an explicit type, not merely shorter syntax. A higher-order function can compose validation or iteration cleanly, and closures can capture useful context such as a limit. That capture also extends the lifetime of referenced objects if the callback escapes. In Android, a retained lambda that captures an Activity is a classic leak; registration should return a removable handle or be tied to a lifecycle scope. I document invocation frequency and thread, especially for retries. I would profile before using `inline`, because inlining can enlarge bytecode. A readable named helper is often better than a chain of anonymous callbacks.

## Deep-dive talking points

Explain function types, closure capture, stored callbacks, invocation contracts, inline and escape analysis.

## Follow-up questions

- [KOT-12](../kot-12/): What can `inline` change? **Answer:** it substitutes the function and eligible lambdas at call sites, trading call overhead for code size.
- [KOT-13](../kot-13/): When can a lambda return from its caller? **Answer:** an eligible inlined lambda can perform a non-local return.

## Self-check rubric

Write a higher-order predicate function, explain capture, and identify a lifecycle leak from a stored callback.

## References and reviewed-on date

- [Kotlin lambdas](https://kotlinlang.org/docs/lambdas.html) — function types, higher-order functions, and closures.
- [Kotlin inline functions](https://kotlinlang.org/docs/inline-functions.html) — inline behavior.

Technically reviewed against the linked primary documentation on 2026-10-11. Examples are illustrative JVM snippets; no Android device claim is made.
