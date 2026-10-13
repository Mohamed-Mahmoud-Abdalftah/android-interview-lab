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

## Practical walkthrough

`inline fun around(block: () -> Unit)` يسمح `return` من caller لو lambda اتنفذت مباشرة في موقع الاستدعاء. لو هتخزنها في object أو تمررها لfunction عادية، `noinline` يبقيها function object ويمنع non-local return. `crossinline` يمنع return ده لكن يسمح نقل جسمها لموضع زي `Runnable { action() }`؛ لازم تنفيذ callback في السياق المسموح حسب التصميم. `reified` يديك type token على call site، لكن generic arguments المتداخلة لسه تخضع لـtype erasure؛ `value is List<String>` مش فحص آمن لكل عنصر. خلي كل modifier مربوط بعقد API واضح بدل إضافته لإسكات compiler.

## Trade-offs and decision criteria

Use `noinline` only when a lambda must be a first-class stored value; use `crossinline` when invoking from a different execution context forbids caller return. Prefer ordinary explicit type tokens for non-inline public APIs or Java callers. Reified helpers can improve ergonomics but may enlarge bytecode.

## Failure modes

An API accepts a callback to run later yet tries to allow a non-local return; this cannot have coherent control flow. Mark the parameter appropriately and make asynchronous lifetime explicit. `value is List<String>` is still constrained by erased element types; reified `T` does not validate every nested generic element.

## Production perspective

A navigation registry stores callbacks, so its registration function uses ordinary or `noinline` function values and returns a cancellable handle. A small parse convenience wrapper may use `reified T`, but the serializer still validates payload shape and errors.

## Interview answer — short

`noinline` keeps a lambda as a function value, so it can be stored or passed on. `crossinline` disallows a non-local return when the lambda runs from another execution context. `reified` exposes an inline type parameter at a call site, within JVM erasure limits.

## Interview answer — structured

I start with the callback’s lifetime. A normal inlined lambda can use a non-local return to leave the caller because it is expanded at that call site. If I must store or pass that lambda as a value, I mark it `noinline`. If I invoke it from another context such as a `Runnable`, `crossinline` prevents a return that cannot safely jump out of the caller. `reified` applies to an inline type parameter and allows checks such as `value is T`, but it does not fully reify nested generic arguments. I choose these modifiers to express execution behavior, not to silence a compiler error.

## Interview answer — deep senior

I would inspect callback lifetime before selecting these modifiers. A delayed callback cannot jump back into a stack frame that has returned, so `noinline` or `crossinline` blocks that control flow. `noinline` preserves the lambda object; `crossinline` can still be substituted but prevents non-local return. Reification substitutes type information at each call site, which is convenient for serializers and class lookup, but type erasure remains relevant to nested generic contents. I keep wrappers small and document whether callbacks are immediate or deferred. A normal inlined lambda may use an unqualified `return` to exit the enclosing caller because its instructions are placed there. Once a callback can be stored or called later, that return has no valid stack frame to target.

Imagine an API that returns a `Runnable` to invoke a callback later. Allowing an unqualified `return` from the caller inside that callback would be nonsensical after the caller has returned, so `crossinline` communicates the restriction. If the callback itself must be stored as a value, `noinline` is the right contract. For a small JSON convenience API, `reified T` can supply a top-level class token, but it cannot prove that every element of a `List<T>` has type T after erasure. I would keep the wrapper small and let the serializer validate nested shape and report errors.

## How to answer in the interview

- **Why:** Fine-tune lambda inlining behavior and bypass JVM type erasure.
- **How:** Use `noinline` to pass lambdas as objects, `crossinline` to forbid non-local returns in deferred/async contexts, and `reified` to retain generic type parameters at runtime.
- **Trade-offs:** `reified` is only usable on `inline` functions and increases compiled bytecode size.
- **Failure cases:** Attempting a non-local `return` inside a lambda passed to an asynchronous runner, causing compiler errors or unexpected early termination of the outer function.
- **Production solution:** Use `crossinline` for callbacks executed inside coroutines or handlers, and `reified` for clean, type-safe JSON deserialization or Android `Intent`/`Bundle` extras.

## Deep-dive talking points

Show legal non-local return from an inline lambda, contrast labeled local return, and explain why delayed execution forbids it.

## Follow-up questions

- [KOT-12](../kot-12/): What is the code-size price of these features? **Answer:** inline body duplication at call sites.
- [KOT-14](../kot-14/): Does `reified` replace variance? **Answer:** no; variance controls subtype relationships in generic APIs.

## Self-check rubric

Explain each modifier, describe one prohibited non-local return, and state a limit of reified type checks.

## References and reviewed-on date

- [Kotlin inline functions](https://kotlinlang.org/docs/inline-functions.html) — `noinline`, `crossinline`, non-local returns, and reified.

Technically reviewed against the linked primary documentation on 2026-10-13. Examples are illustrative JVM snippets; no Android device claim is made.
