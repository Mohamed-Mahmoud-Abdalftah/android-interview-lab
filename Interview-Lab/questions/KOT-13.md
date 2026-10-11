---
id: "KOT-13"
question: "Explain noinline, crossinline, non-local return, and reified type parameters."
topic: "Kotlin Core & Advanced"
code: "KOT"
group: "B"
phase: 1
priority: "P1"
order: 13
editorial_status: "reviewed"
---

# KOT-13

## Original interview question

Explain noinline, crossinline, non-local return, and reified type parameters.

## What the interviewer evaluates

Distinguish stored versus inlined lambdas, forbidden non-local returns, and runtime type access.

## Explanation in Arabic

داخل `inline` function، lambda العادية ممكن تتنسخ في call site وتعمل `return` من function اللي نادتها (non-local return) لو control flow يسمح. `noinline` يمنع نسخ lambda معينة ويخليها function value ينفع تتخزن أو تتبعت؛ وبالتالي non-local return منها غير مسموح. `crossinline` تمنع non-local return مع بقاء إمكانية inlining، وده مهم لما lambda تتنفذ في سياق تاني زي object method. `reified T` يتيح `T::class` و`is T` داخل inline لأن النوع الفعلي معروف في call site؛ مش معناه إن generic collection elements اتعمل لها runtime validation.

## Why it matters and how it works

These modifiers encode control-flow and storage contracts. The compiler cannot permit a return from the caller when a callback may run later. Reification addresses type erasure for a specific inline call site, not every generic type use.

## Worked example

Runnable JVM example: `crossinline` is needed because the callback runs from an object method.
```kotlin
inline fun <reified T : Any> matches(value: Any): Boolean = value is T
inline fun task(crossinline action: () -> Unit): Runnable =
    Runnable { action() }
fun main() {
    println(matches<String>("ok"))
    task { println("later") }.run()
}
```

## Trade-offs and decision criteria

Use `noinline` only when a lambda must be a first-class stored value; use `crossinline` when invoking from a different execution context forbids caller return. Prefer ordinary explicit type tokens for non-inline public APIs or Java callers. Reified helpers can improve ergonomics but may enlarge bytecode.

## Failure modes

An API accepts a callback to run later yet tries to allow a non-local return; this cannot have coherent control flow. Mark the parameter appropriately and make asynchronous lifetime explicit. `value is List<String>` is still constrained by erased element types; reified `T` does not validate every nested generic element.

## Production perspective

A navigation registry stores callbacks, so its registration function uses ordinary or `noinline` function values and returns a cancellable handle. A small parse convenience wrapper may use `reified T`, but the serializer still validates payload shape and errors.

## Interview answer — short

`noinline` keeps a lambda as a value; `crossinline` allows inlining but forbids non-local return; eligible inlined lambdas may return from the caller. `reified` makes a type parameter available at an inline call site.

## Interview answer — structured

The key is whether the lambda stays inside the call. An eligible inline lambda can perform a non-local return because its code is inserted into the caller. If I need to store or pass a lambda as a value, I mark it `noinline`. If I invoke it from another context where returning from the caller is invalid, I use `crossinline`. A reified type parameter is also tied to inlining; it permits checks such as `value is T`, but does not erase the need to validate generic payloads. The three modifiers answer different questions. If the callback is stored, it must remain a function value, so `noinline` fits. If I need `T::class` or `is T` in a small wrapper, `reified` makes the concrete type available at each inline call. None of this validates arbitrary nested generic data for me.

## Interview answer — deep senior

I would inspect callback lifetime before selecting these modifiers. A delayed callback cannot jump back into a stack frame that has returned, so `noinline` or `crossinline` blocks that control flow. `noinline` preserves the lambda object; `crossinline` can still be substituted but prevents non-local return. Reification substitutes type information at each call site, which is convenient for serializers and class lookup, but type erasure remains relevant to nested generic contents. I keep wrappers small and document whether callbacks are immediate or deferred. A normal inlined lambda may use an unqualified `return` to exit the enclosing caller because its instructions are placed there. Once a callback can be stored or called later, that return has no valid stack frame to target. Reified parameters similarly exploit substitution of a concrete type at the call site. That allows a type check or class token without explicitly passing `Class<T>`, but Java type erasure still limits checks of nested generic elements. I would make callback lifetime explicit and avoid a public inline wrapper so large that it bloats each caller. These modifiers are control-flow contracts as much as performance details.

## Deep-dive talking points

Show legal non-local return from an inline lambda, contrast labeled local return, and explain why delayed execution forbids it.

## Follow-up questions

- [KOT-12](../kot-12/): What is the code-size price of these features? **Answer:** inline body duplication at call sites.
- [KOT-14](../kot-14/): Does `reified` replace variance? **Answer:** no; variance controls subtype relationships in generic APIs.

## Self-check rubric

Explain each modifier, describe one prohibited non-local return, and state a limit of reified type checks.

## References and reviewed-on date

- [Kotlin inline functions](https://kotlinlang.org/docs/inline-functions.html) — `noinline`, `crossinline`, non-local returns, and reified.

Technically reviewed against the linked primary documentation on 2026-10-11. Examples are illustrative JVM snippets; no Android device claim is made.
