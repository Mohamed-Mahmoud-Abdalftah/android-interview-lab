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

## Practical walkthrough

`firstMatching(items) { it.price < budget }` بتاخد behavior كparameter بدل ما تعمل method لكل filter. راجع العقد: الـpredicate بيتنادى كام مرة؟ synchronous ولا محفوظ لاستخدام لاحق؟ هل ممكن يرمي exception؟ لو بتسجل callback في listener، إمسك handle للإلغاء عشان ما تسرّبش Activity. والـlambda اللي تلتقط `budget` أو View reference بتحتفظ بيها طول عمر callback. في hot loop، allocation أو inlining قرار قياس، مش سبب لاستخدام lambda مبهمة.

## Trade-offs and decision criteria

A lambda is concise for one behavior; an interface or named class is clearer when there are multiple operations, identity, or long-lived lifecycle. Function references can be readable but still require checking capture and dispatch semantics. Inlining may remove call overhead but duplicates body bytecode.

## Failure modes

A repository retains a screen callback that captures an Activity; the Activity remains reachable after rotation. Prefer lifecycle-owned collection or remove the listener. Another failure is assuming a callback runs once when an API may retry or invoke it concurrently; document invocation rules.

## Production perspective

A validation pipeline accepts small predicates and applies them synchronously. For asynchronous search, a ViewModel collects a Flow in `viewModelScope` rather than registering an unowned callback that can outlive the screen.

## Interview answer — short

A higher-order function accepts or returns a function. A lambda supplies behavior at the call site, which is useful for filters, callbacks, and policies. I document when the lambda runs and whether it can escape, throw, or capture long-lived references.

## Interview answer — structured

I use higher-order functions to pass a small policy without creating a subclass, such as filtering products with a caller-supplied predicate. The function type shows the input and return value, but a useful API must also state whether it invokes the lambda immediately, stores it, or calls it on another thread. Those details affect captured state, exceptions, and lifecycle cleanup. For an Android listener I return an unregister handle and avoid capturing an Activity in a longer-lived owner. I choose a named interface if the behavior has several operations or needs a richer contract.

## Interview answer — deep senior

I treat higher-order functions as behavioral dependencies. A caller should know whether the lambda can return non-locally, whether it is invoked under a lock, and whether it can escape the call. Captures may retain resources and complicate lifecycle management. In a tight loop, generated allocation and call overhead may matter, but JVM optimization is contextual; profiling beats blanket inlining. For long-lived asynchronous subscriptions I give them an explicit owner and cancellation path. I see lambdas as a way to pass behavior with an explicit type, not merely shorter syntax.

Suppose a repository accepts a callback for live updates. The function type tells me the values it receives, but not whether it runs immediately, on Main, or after the screen is gone. I would document invocation timing and return a cancellation handle, then verify that an Activity or View captured by the lambda is released on stop. If the callback performs several operations or needs structured state, a named interface may communicate the contract better. I would only discuss inline or allocation cost after profiling a genuine hot path rather than assuming every lambda allocates in the same way.

## How to answer in the interview

- **Why:** Enable clean functional composition, event handling, and customizable algorithms.
- **How:** Pass lambdas and function references (`(T) -> R`) as parameters, inlining execution where appropriate to eliminate allocation overhead.
- **Trade-offs:** Non-inlined higher-order functions allocate `Function` object instances and closure capture contexts on the heap.
- **Failure cases:** Storing a lambda that captures an `Activity` reference inside a long-lived singleton, leaking the entire UI context.
- **Production solution:** Inline short utility functions, clear stored callbacks in lifecycle teardown (`onDestroy`), or prefer lifecycle-aware listeners and Flow streams.

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

Technically reviewed against the linked primary documentation on 2026-10-13. Examples are illustrative JVM snippets; no Android device claim is made.
