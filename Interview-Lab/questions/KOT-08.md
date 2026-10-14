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

Scope functions differ by context access and return value. apply and run access the object via this, while let and also access it via it (with takes the receiver as an argument). apply and also return the context object itself, making them ideal for configuration and side-effects, while let, run, and with return the lambda result.

## Interview answer — structured

I categorize scope functions along two axes: how they access the context object, and what they return.

For access, apply and run use this, allowing direct property access, whereas let and also use it, which is safer when passing the object to external functions.

For return values, apply and also return the context object itself. I use apply for configuring objects like Intents or Views, and also for non-mutating side effects like logging.

Conversely, let and run return the lambda's result. I use let primarily for safe null checks and mapping, while run is great for computing a result from an object's properties.

In production, my team bans deeply nested scope functions because they obscure variable ownership and make debugging stack traces difficult.


## Interview answer — deep senior

Scope functions are inline extension functions (except with, which is a regular function taking a receiver). Because they are inlined, they introduce zero runtime allocation or method call overhead on the JVM.

However, the architectural trade-off is cognitive load and code review readability. When using receiver-based functions (run, with, apply), implicit this scoping can accidentally shadow properties of an outer enclosing class, especially inside Android Activities or Fragments. For example, calling finish() inside a WebView.apply block might invoke the Activity's finish() method if WebView lacks a matching signature.

When using argument-based functions (let, also), the default it identifier can create confusion if nested. In production guidelines, we require renaming it to explicit parameter names if let blocks exceed two lines. We also restrict scope chains to a maximum of two operations (e.g. Parse().apply { ... }.also { log(it) }), preferring explicit local variables for complex flows.


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
