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

## Practical walkthrough

في code review، اقرأ نتيجة كل خطوة: `apply` و`also` يرجعوا نفس object، فمناسبين للتهيئة أو side effect محدود؛ `run` و`let` و`with` يرجعوا نتيجة الـlambda. `let/also` بيستخدموا `it`، و`run/apply/with` بيستخدموا `this`. مثلًا `response?.let { parse(it) } ?: return Missing` واضح عند nullable boundary. لكن chain فيها nested `it` و`this` تخلي ownership مبهمة؛ سمي المتغير أو فكها لسطور. ولا تستخدم `also` لإخفاء network call أو mutation مهمة.

## Trade-offs and decision criteria

An ordinary `if`, local variable, or named helper is better when a chain gets ambiguous. `also` suits logging or validation side effects, but avoid secretly mutating global state in it. `let` can clarify null handling; `run` with multiple receivers can obscure names.

## Failure modes

Nested `apply` blocks both expose `this`, causing configuration to land on the wrong object. Use qualified names or split into named statements. Also, `?.let { ... } ?: ...` executes the Elvis branch if the lambda returns null, even when the receiver was non-null; do not mistake it for a pure null check.

## Production perspective

A networking module uses `apply` to configure a request builder, then passes the built immutable request to the client. It uses `let` at a nullable response boundary and a named mapping function if multiple validation steps are needed.

## Interview answer — short

I choose scope functions by two questions: is the object named `it` or implicit as `this`, and does the expression return the object or the lambda result? `apply` configures an object; `let` transforms a nullable value. I avoid long nested chains.

## Interview answer — structured

The five functions mainly differ in receiver syntax and return value. `let` and `also` pass the object as an argument; `run`, `apply`, and `with` expose it as a receiver. `also` and `apply` return the original object, while `let`, `run`, and `with` return the lambda result. That makes `apply` a good fit for request construction and `response?.let { parse(it) }` a good fit for nullable conversion. I do not treat these functions as lifecycle or threading tools. If nesting makes `this` or `it` ambiguous, I use explicit names and ordinary statements.

## Interview answer — deep senior

Scope functions are syntax for organizing calls, not an ownership or threading primitive. I review a chain by evaluating its actual type after each step. A subtle case is `?.let { nullableResult } ?: fallback`: fallback may run because the lambda returned null, not because the original receiver was null. I keep mutation and logging visible, avoid multiple implicit receivers, and prefer explicit statements when invariants or error handling need attention. The scope-function matrix has two independent dimensions. `let` and `also` expose the object as an argument, normally `it`; `run`, `with`, and `apply` use an implicit receiver, `this`.

For a nullable network response, `response?.let { parse(it) } ?: fallback` runs the fallback when either the response is null or `parse` returns null. If those represent different failures, the chain hides a bug; I would split it into explicit checks. Similarly, `Request().apply { ... }.also { log(it) }` returns the Request, whereas `run { validate() }` returns the validation result, so a later call may target a different type. My production rule is to use short scope blocks for local transformations and named statements when side effects or error categories matter.

## How to answer in the interview

- **Why:** Provide concise contextual scoping for object configuration, transformation, and side-effects.
- **How:** Use `apply`/`also` when returning the original object, and `let`/`run`/`with` when transforming or computing a new value.
- **Trade-offs:** Deeply nested or chained scope functions severely degrade readability, obscure `this` receivers, and complicate debugging.
- **Failure cases:** Shadowing the implicit `this` inside nested `apply` or `with` blocks, mutating outer properties by mistake.
- **Production solution:** Limit scope chains to 1–2 operations, use explicit parameter names (`it -> item`) when nesting `let`, and favor descriptive local variables for complex logic.

## Deep-dive talking points

Describe receiver/argument and result/receiver matrix, `with` call form, null-safe chains, and lambda-returned null behavior.

## Follow-up questions

- [KOT-20](../kot-20/): Why is `this` risky in nested scopes? **Answer:** implicit receivers can shadow one another; `it` or named locals show the target.
- [KOT-09](../kot-09/): Are scope functions special syntax? **Answer:** they are standard-library functions using lambdas and extensions.

## Self-check rubric

Classify all five by receiver and return value; explain a legitimate use of three; spot a nested-scope ambiguity.

## References and reviewed-on date

- [Kotlin scope functions](https://kotlinlang.org/docs/scope-functions.html) — receiver and return distinctions.

Technically reviewed against the linked primary documentation on 2026-10-13. Examples are illustrative JVM snippets; no Android device claim is made.
