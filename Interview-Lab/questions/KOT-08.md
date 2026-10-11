---
id: "KOT-08"
question: "Explain let, run, with, apply, and also with appropriate use cases."
topic: "Kotlin Core & Advanced"
code: "KOT"
group: "A"
phase: 1
priority: "P1"
order: 8
editorial_status: "reviewed"
---

# KOT-08

## Original interview question

Explain let, run, with, apply, and also with appropriate use cases.

## What the interviewer evaluates

Choose scope functions by receiver versus argument and return value, and avoid nesting that hides ownership.

## Explanation in Arabic

الخمس scope functions اختلافهم الأساسي: `let` و`also` بيستخدموا `it`، بينما `run` و`apply` و`with` بيستخدموا `this`. `let`/`run`/`with` بيرجعوا نتيجة الـlambda؛ `also`/`apply` بيرجعوا الـobject نفسه. `with(x)` function عادية بتاخد receiver argument، والباقي extensions. اختار بناءً على النية: `?.let` للتعامل مع non-null، `apply` لتهيئة object، `also` side effect محدود، `run` حساب نتيجة بسياق object. التداخل العميق يخفي أي `this` أو `it` مستخدم.

## Why it matters and how it works

These functions shorten local transformations but do not create a new scope, transaction, or thread. Receiver style reads like members of one object; argument style makes the target explicit. Return type determines whether the chain carries a computed result or the original object.

## Worked example

JVM example: configuration returns the builder object, then `run` computes a separate result.
```kotlin
class Request(var path: String = "", var retries: Int = 0)
fun main() {
    val request = Request().apply { path = "/users"; retries = 2 }
    val label = request.run { "$path (retries=$retries)" }
    println(label)
}
```

## Trade-offs and decision criteria

An ordinary `if`, local variable, or named helper is better when a chain gets ambiguous. `also` suits logging or validation side effects, but avoid secretly mutating global state in it. `let` can clarify null handling; `run` with multiple receivers can obscure names.

## Failure modes

Nested `apply` blocks both expose `this`, causing configuration to land on the wrong object. Use qualified names or split into named statements. Also, `?.let { ... } ?: ...` executes the Elvis branch if the lambda returns null, even when the receiver was non-null; do not mistake it for a pure null check.

## Production perspective

A networking module uses `apply` to configure a request builder, then passes the built immutable request to the client. It uses `let` at a nullable response boundary and a named mapping function if multiple validation steps are needed.

## Interview answer — short

I pick a scope function by how it refers to the object and what it returns. `let` and `also` use `it`; `run`, `with`, and `apply` use `this`. `let`, `run`, and `with` return the lambda result; `also` and `apply` return the receiver.

## Interview answer — structured

`?.let` is useful for a non-null branch, `apply` for configuring and returning an object, `also` for a small side effect, and `run` or `with` when I want a computed result in an object context. The key is not memorizing names alone: I check whether the receiver is `this` or `it`, and whether the chain returns the original object or the lambda result. Deep nesting usually deserves named locals. If several receivers appear, I write named locals rather than forcing a nested chain. This lets a reviewer follow both the target object and the final type. One common trap is `?.let { nullableResult } ?: fallback`: the fallback may run because the lambda returned null even though the original object existed. I would split that logic when the distinction matters.

## Interview answer — deep senior

Scope functions are syntax for organizing calls, not an ownership or threading primitive. I review a chain by evaluating its actual type after each step. A subtle case is `?.let { nullableResult } ?: fallback`: fallback may run because the lambda returned null, not because the original receiver was null. I keep mutation and logging visible, avoid multiple implicit receivers, and prefer explicit statements when invariants or error handling need attention. The scope-function matrix has two independent dimensions. `let` and `also` expose the object as an argument, normally `it`; `run`, `with`, and `apply` use an implicit receiver, `this`. That means a chain may silently switch from a builder to a Boolean or nullable value. Nested receiver blocks can also set a property on the wrong object. In production mapping code I prefer a few clear statements and explicit validation when business meaning matters. These functions organize expressions; they do not create concurrency, ownership, or transactions. A scope-function chain can also hide side effects, especially with `also`. I keep logging or mutation small and visible, and I do not mistake `run` for a transaction or a coroutine scope. Those names are expression helpers; lifecycle, cancellation, and resource ownership still need explicit design.

## Deep-dive talking points

Describe receiver/argument and result/receiver matrix, `with` call form, null-safe chains, and lambda-returned null behavior.

## Follow-up questions

- [KOT-20](../kot-20/): Why is `this` risky in nested scopes? **Answer:** implicit receivers can shadow one another; `it` or named locals show the target.
- [KOT-09](../kot-09/): Are scope functions special syntax? **Answer:** they are standard-library functions using lambdas and extensions.

## Self-check rubric

Classify all five by receiver and return value; explain a legitimate use of three; spot a nested-scope ambiguity.

## References and reviewed-on date

- [Kotlin scope functions](https://kotlinlang.org/docs/scope-functions.html) — receiver and return distinctions.

Technically reviewed against the linked primary documentation on 2026-10-11. Examples are illustrative JVM snippets; no Android device claim is made.
