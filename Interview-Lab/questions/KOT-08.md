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

## Concept and technical explanation

Kotlin provides five standard library scope functions designed to execute a block of code within the context of an object: let, run, with, apply, and also. These functions differ along two architectural dimensions:
1. Context Object Reference: Inside the lambda, the context object is available either as a lambda receiver (this) or as a lambda argument (it).
   - Receiver (this): apply, run, and with. Best suited for operating on the object's public members without repeating the instance name.
   - Argument (it): let and also. Best suited when the context object is passed to other functions as an argument or when disambiguating outer references.
2. Return Value: The scope function expression evaluates either to the context object itself or to the result of the lambda block.
   - Returns Context Object: apply and also. Ideal for fluent builder patterns, configuration chains, and logging side-effects.
   - Returns Lambda Result: let, run, and with. Ideal for transformations, mapping operations, and computing dependent results.

## Practical walkthrough (English)

Consider preparing, configuring, and sending an HTTP network request in an Android service:

Failure Scenario — Nested Scope Anti-Pattern with Ambiguous Receivers:
```kotlin
fun sendPayload(client: HttpClient, config: RequestConfig?) {
    config?.let { // 'it' is RequestConfig
        client.run { // 'this' is HttpClient
            apply { // Ambiguity: is 'this' HttpClient or RequestConfig?
                setTimeout(it.timeout) // Hard to read and maintain
            }
        }
    }
}
```
Nesting multiple scope functions using `this` obscures lexical ownership, increases cognitive complexity, and easily leads to invoking methods on the wrong receiver.

Production Architecture — Intentional, Clear Scope Selection:
```kotlin
// 1. apply: Initialize and configure the builder (returns the builder)
val request = NetworkRequest.Builder().apply {
    setUrl("https://api.example.com/v1/orders")
    setTimeoutMs(5000)
    addHeader("Authorization", "Bearer token_xyz")
}.build()

// 2. also: Perform an isolated side-effect (logging) without mutating the request
val verifiedRequest = request.also {
    Timber.d("Outgoing request prepared for: ${it.url}")
}

// 3. let: Safe transformation of nullable response
fun handleResponse(rawPayload: String?): OrderUiModel? {
    return rawPayload?.let { json ->
        jsonParser.parse<OrderDto>(json).toDomainModel()
    }
}
```

Bytecode Decompilation Verification:
Decompiling any of the five scope functions reveals that all five are declared as `inline`:
```java
// Kotlin: val result = obj.let { it.compute() }
// Decompiled bytecode:
Object var1 = obj;
// inlined body executes directly without method call:
Object result = compute(var1);
```
Because they are fully inlined at the call site, scope functions introduce zero object allocation overhead, zero interface calls, and compile directly to linear Java bytecodes.

## Explanation in Arabic

الـ Scope Functions الخمسة (let, run, with, apply, also) هدفها تنفيذ كود داخل سياق Object معين (Context Object) بطريقة مقتضبة، والفرق بينهم بيتلخص في بعدين رئيسيين:

1. كيف تصل للـ Object داخل الـ Lambda؟
   - عبر this (Receiver): في run و with و apply. مناسب لو بتنادي دوال الـ Object مباشرة بدون تكرار اسمه.
   - عبر it (Argument): في let و also. مناسب لو عايز تمرر الـ Object لدوّال تانية أو تديله اسم معبر.

2. ماذا ترجع الدالة (Return Value)؟
   - ترجع الـ Context Object نفسه: في apply و also. مناسب للـ Object Configuration والـ Side-effects (Chaining).
   - ترجع نتيجة الـ Lambda (آخر سطر): في let و run و with. مناسب للـ Transformation والحسابات.

قاعدة ذهبية: تجنب الـ Nesting والـ Chaining الطويل (Scope Function Puzzles). لو الكود محتاج 3 Scope Functions ورا بعض، استبدله بـ كود عادي واضح بمتغيرات صريحة.

## Practical walkthrough

في شاشة أندرويد:
- apply: لتهيئة كائن View أو Intent: Intent(context, DetailActivity::class.java).apply { putExtra("id", 123); flags = FLAG_ACTIVITY_NEW_TASK }.
- let: لفحص null وتحويل القيمة بأمان: user?.let { sendNotification(it.email) }.
- also: لعمل Side-effect جانبي زي تسجيل Log دون تغيير الكائن: createOrder().also { Log.d("Order", "Created ${it.id}") }.
- run: لتهيئة كائن وحساب نتيجة نهائية: val label = TextView(context).run { text = "Hello"; width }.
- with: لما يكون عندك كائن مش null وعايز تنادي عليه دوال كتير: with(binding) { nameText.text = "..."; emailText.text = "..." }.

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

Kotlin's five scope functions execute code within an object's context. They differ by context access (receiver this versus argument it) and return value (the context object versus the lambda result). Use apply to configure objects and also for side-effects like logging; both return the object. Use let for null checks and transformations, run for object-scoped computation, and with for non-null configuration; all three return the lambda result.

## Interview answer — structured

Kotlin's scope functions provide idiomatic ways to execute operations within the context of an object. The key to mastering them is recognizing their two distinguishing dimensions: whether they access the object via this or it, and whether they return the object itself or the lambda result.

Apply and also return the context object, making them perfect for chained pipelines. Specifically, apply exposes this and is the industry standard for object configuration, such as setting up View properties or Intent flags. On the other hand, also exposes it and is designated for non-mutating side effects like logging or diagnostic validation.

In production, when the operation computes a new value or transforms data, let and run are the correct choices because they return the lambda result. The let function exposes it, serving as the standard mechanism for null-safe chaining. Meanwhile, run exposes this, combining configuration with result computation.

Senior engineers forbid deeply nested scope functions to prevent receiver shadowing and retain readable codebases.


## Interview answer — deep senior

From a compiler and bytecode perspective, all five standard library scope functions—let, run, with, apply, and also—are declared with the inline modifier and contract definitions. This means they do not exist as method calls in compiled JVM bytecode. Instead, kotlinc inlines the lambda instructions directly at the call site, eliminating all functional interface allocations, function call frames, and indirection overhead.

When examining decompiled bytecode for apply, such as obj.apply { doSomething() }, the compiler assigns obj to a local stack variable, inlines doSomething() directly against that variable, and leaves the original reference at the top of the stack frame to satisfy the return contract. For let, the compiler stores the receiver in a temporary register, passes it into the inlined transformation block, and leaves the evaluated expression on the operand stack. Consequently, performance differences among scope functions are completely non-existent at runtime; the choice between them is purely semantic and architectural.

However, improper nesting of receiver-based scope functions (apply, run, with) introduces severe scoping bugs. Because these functions bring the context object into lexical scope as an implicit this, nesting them creates multiple implicit receivers. If an inner call invokes a method shared by both receivers, the inner receiver silently shadows the outer one, causing unexpected state mutations.

Another critical pitfall involves pairing safe-call let with the Elvis operator: target?.let { it.transform() } ?: fallback(). If the transform() method evaluates to null, the entire let expression evaluates to null, triggering the Elvis fallback even though target was completely non-null. In high-stakes Android production code, senior engineers establish strict linting rules: limit scope functions to single-level expressions, use also strictly for observational side-effects, and replace ambiguous let-Elvis cascades with clear if-else branching.

## How to answer in the interview

- **Why:** Provide concise contextual scoping for object configuration, transformation, and side-effects.
- **How:** Use `apply`/`also` when returning the original object, and `let`/`run`/`with` when transforming or computing a new value.
- **Trade-offs:** Deeply nested or chained scope functions severely degrade readability, obscure `this` receivers, and complicate debugging.
- **Failure cases:** Shadowing the implicit `this` inside nested `apply` or `with` blocks, mutating outer properties by mistake.
- **Production solution:** Limit scope chains to 1–2 operations, use explicit parameter names (`it -> item`) when nesting `let`, and favor descriptive local variables for complex logic.

## Deep-dive talking points

Describe receiver/argument and result/receiver matrix, `with` call form, null-safe chains, and lambda-returned null behavior.

## Follow-up questions

- **Interviewer:** "How does `apply` differ from `also` if both return the context object?"
  **Answer:** "The difference is how they reference the object inside the lambda. `apply` provides the object as a receiver (`this`), making it ideal for mutating object properties directly. `also` provides the object as an argument (`it`), which is ideal for inspecting the object, logging, or passing it to external functions without shadowing `this`."

- **Interviewer:** "Why is `with` a regular function rather than an extension function?"
  **Answer:** "`with` was designed before Kotlin standard library conventions favored extension syntax. It takes the receiver as its first parameter: `with(receiver) { ... }`. Functionally, it is identical to `receiver.run { ... }`, and most modern codebases prefer `run` for consistency."

- **Interviewer:** "What is the danger of using `?.let { ... }` as an `if-else` replacement with `?: run { ... }`?"
  **Answer:** "If the code inside the `let` block evaluates to `null` (for instance, the last expression returns null), the Elvis operator `?: run` will unexpectedly trigger even though the original object was NOT null! It creates subtle logic bugs. When an explicit else branch is required, standard `if (x != null) ... else ...` is always safer."

## Self-check rubric

Classify all five by receiver and return value; explain a legitimate use of three; spot a nested-scope ambiguity.

## References and reviewed-on date

- [Kotlin scope functions](https://kotlinlang.org/docs/scope-functions.html) — receiver and return distinctions.

Technically reviewed against primary documentation on 2026-10-13.
