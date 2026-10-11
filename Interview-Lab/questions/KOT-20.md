---
id: "KOT-20"
question: "Explain scope-function receiver versus argument semantics."
topic: "Kotlin Core & Advanced"
code: "KOT"
group: "B"
phase: 1
priority: "P1"
order: 20
editorial_status: "reviewed"
---

# KOT-20

## Original interview question

Explain scope-function receiver versus argument semantics.

## What the interviewer evaluates

Distinguish `this` from `it`, receiver shadows, and the return-value axis of scope functions.

## Explanation in Arabic

في lambda with receiver زي `run`, `apply`, `with`، الـobject بيبقى `this` وتقدر تنادي members من غير اسم. في `let` و`also` الـobject بييجي argument اسمه الافتراضي `it` أو اسم تختاره. الـreceiver مريح في builder DSL، بس nested receivers ممكن يخبّوا بعض وتكتب property على object غلط. `it` أو اسم صريح مفيد لما في أكتر من object. ده غير محور return value: `apply/also` بيرجعوا الأصل، والباقي يرجعوا نتيجة lambda.

## Why it matters and how it works

Receiver versus argument semantics affect name resolution and readability, while return semantics affect chaining and types. Treating all scope functions as interchangeable can introduce mutation or null-handling bugs.

## Worked example

Runnable JVM example uses explicit argument names to avoid a nested `it` ambiguity.
```kotlin
data class User(val name: String)
fun names(users: List<User>): List<String> = users.map { user ->
    user.name.let { rawName -> rawName.trim() }
}
fun main() = println(names(listOf(User(" Ada "))))
```

## Trade-offs and decision criteria

Use receiver style when configuring one object and member access dominates. Use argument style when the value participates alongside other values or nested scopes. Explicit names or ordinary statements beat clever chains when several receivers are active.

## Failure modes

A nested `apply` initializes an inner object but an unqualified assignment lands on an outer receiver of the same property name. Compiler accepts it. Name objects explicitly or split the configuration. Do not mistake `let` for a lifecycle scope or asynchronous boundary.

## Production perspective

A request builder uses a short `apply` block to set fields. Mapping a response with multiple nullable pieces uses named locals and validation, so reviewers can see exactly which object supplies each field.

## Interview answer — short

Receiver lambdas expose the object as `this`; argument lambdas expose it as `it` or a named parameter. I choose receiver style for focused configuration and argument style when explicit naming helps. I also check whether the function returns the object or the lambda result.

## Interview answer — structured

`apply`, `run`, and `with` use a lambda receiver, so members are available through `this`. `let` and `also` pass the object as an argument, normally `it`. That affects how names resolve in nested code. Separately, `apply` and `also` return the original object, while `let`, `run`, and `with` return the lambda result. In review I trace both axes and avoid nested implicit receivers when they make mutation ambiguous. If I am comparing two values or nesting operations, an explicit argument name is safer. I also trace what each function returns: after `apply` I still have the request, while after `run` I have the computed result. That prevents a chain from subtly changing type or applying a fallback for the wrong reason.

## Interview answer — deep senior

These are ordinary higher-order functions with different function signatures. A receiver lambda creates an implicit receiver in the lexical context; nesting it inside another receiver can make unqualified member access surprising. An argument lambda is often easier to name explicitly, especially in mapping code with several values. Return semantics determine the type of a chain and can change null behavior: Elvis after `?.let` may trigger because the lambda returned null. I prefer local variables when the chain hides validation, ownership, or side effects. `this` in `apply`, `run`, or `with` is an implicit receiver, so member names can be concise but can also collide with outer receivers. The second axis is return value: `apply` and `also` preserve the receiver; `let`, `run`, and `with` return the lambda result. None of these constructs changes thread or lifecycle semantics. The same reasoning applies to nested DSLs. If two receivers expose `name`, unqualified access may bind to the wrong one, so I introduce names or use qualified receivers. I prefer one clear transformation over a compact chain that a reviewer must mentally execute.

## Deep-dive talking points

Map all five functions on receiver/argument and result/receiver axes; explain shadowing and nullable lambda results.

## Follow-up questions

- [KOT-08](../kot-08/): Which scope functions return their receiver? **Answer:** `apply` and `also`.
- [KOT-09](../kot-09/): Is a lambda receiver dynamically dispatched? **Answer:** no; extension-style resolution remains governed by declared types.

## Self-check rubric

Name the receiver functions and argument functions, trace a chain return type, and spot an implicit-receiver collision.

## References and reviewed-on date

- [Kotlin scope functions](https://kotlinlang.org/docs/scope-functions.html) — receiver and return semantics.

Technically reviewed against the linked primary documentation on 2026-10-11. Examples are illustrative JVM snippets; no Android device claim is made.
