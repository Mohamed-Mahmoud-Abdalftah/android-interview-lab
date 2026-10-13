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

## Practical walkthrough

في `users.map { user -> user.name.let { raw -> raw.trim() } }`، `map` و`let` بيمرّروا argument فالأسماء الصريحة بتمنع اختلاط `it`. `run` و`apply` بيخلّوا object هو implicit receiver `this`؛ ده لطيف في config قصيرة لكن nested receivers تخلي `name` تبع مين مش واضح. كمان return type مهم: `apply` يرجع original object و`run` يرجع lambda result. لما chain فيها mutation أو logging، فكها لمتغيرات محلية؛ readability أهم من عدد السطور. Scope functions ما بتغيّرش thread ولا lifecycle ولا ownership.

## Trade-offs and decision criteria

Use receiver style when configuring one object and member access dominates. Use argument style when the value participates alongside other values or nested scopes. Explicit names or ordinary statements beat clever chains when several receivers are active.

## Failure modes

A nested `apply` initializes an inner object but an unqualified assignment lands on an outer receiver of the same property name. Compiler accepts it. Name objects explicitly or split the configuration. Do not mistake `let` for a lifecycle scope or asynchronous boundary.

## Production perspective

A request builder uses a short `apply` block to set fields. Mapping a response with multiple nullable pieces uses named locals and validation, so reviewers can see exactly which object supplies each field.

## Interview answer — short

Receiver lambdas use implicit `this`; argument lambdas pass the value as `it` or a named parameter. I choose based on clarity in the surrounding scope, especially when lambdas are nested. Return value is a separate choice: `apply` returns the receiver, while `run` returns the computed result.

## Interview answer — structured

I look at a scope function’s function signature, not its fashionable name. `let` and `also` give the lambda an argument, which I name explicitly in nested code. `run`, `apply`, and `with` give an implicit receiver, which is concise for a short configuration block but ambiguous with nested receivers. I separately check whether the function returns the original object or the lambda result. In a code review, if a chain hides which `name` or `this` is used, I split it into named locals. These functions organize expression scope; they do not change concurrency or lifecycle behavior.

## Interview answer — deep senior

These are ordinary higher-order functions with different function signatures. A receiver lambda creates an implicit receiver in the lexical context; nesting it inside another receiver can make unqualified member access surprising. An argument lambda is often easier to name explicitly, especially in mapping code with several values. Return semantics determine the type of a chain and can change null behavior: Elvis after `?.let` may trigger because the lambda returned null. I prefer local variables when the chain hides validation, ownership, or side effects. `this` in `apply`, `run`, or `with` is an implicit receiver, so member names can be concise but can also collide with outer receivers. The second axis is return value: `apply` and `also` preserve the receiver; `let`, `run`, and `with` return the lambda result.

A nested builder block illustrates the ambiguity: inside `apply`, an unqualified `name` might belong to the builder; inside another receiver block it might refer to a different object. I name the argument in `let` or split the operations into locals when that matters. I also check null behavior: `source?.let { parse(it) } ?: fallback` uses fallback if either source or parse result is null. If those are distinct failures, I write explicit branches. These functions execute synchronously in their caller’s context; they neither dispatch work nor attach it to a lifecycle, so hidden I/O or mutation deserves ordinary statements.

## How to answer in the interview

- **Why:** Choose the appropriate scope function based on whether the context is accessible via `this` (receiver) or `it` (parameter).
- **How:** Use `apply`/`run` for receiver context (`this`), and `let`/`also` for argument context (`it`).
- **Trade-offs:** Accessing properties via `this` can shadow outer class members when nested; `it` requires explicit naming when disambiguation is needed.
- **Failure cases:** Writing multi-line transformations inside `apply` and expecting the return value to be the transformation result; `apply` always returns the original receiver.
- **Production solution:** Use `apply` strictly for object initialization/configuration, `let` for null-safe mapping and scope restriction, and always name nested parameters explicitly.

## Deep-dive talking points

Map all five functions on receiver/argument and result/receiver axes; explain shadowing and nullable lambda results.

## Follow-up questions

- [KOT-08](../kot-08/): Which scope functions return their receiver? **Answer:** `apply` and `also`.
- [KOT-09](../kot-09/): Is a lambda receiver dynamically dispatched? **Answer:** no; extension-style resolution remains governed by declared types.

## Self-check rubric

Name the receiver functions and argument functions, trace a chain return type, and spot an implicit-receiver collision.

## References and reviewed-on date

- [Kotlin scope functions](https://kotlinlang.org/docs/scope-functions.html) — receiver and return semantics.

Technically reviewed against the linked primary documentation on 2026-10-13. Examples are illustrative JVM snippets; no Android device claim is made.
