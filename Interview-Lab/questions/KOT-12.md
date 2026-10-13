---
id: "KOT-12"
question: "What does inline do? What are its costs and benefits?"
topic: "Kotlin Core & Advanced"
code: "KOT"
group: "B"
phase: 1
priority: "P1"
order: 12
editorial_status: "reviewed"
---

# KOT-12

## Original interview question

What does inline do? What are its costs and benefits?

## What the interviewer evaluates

Explain inlining at call sites, lambda allocation/call overhead, bytecode growth, and measurement.

## Explanation in Arabic

`inline` يطلب من compiler نسخ body الـfunction والـlambda المناسبة في call site. ده ممكن يقلل function-object allocation وvirtual call في higher-order functions، ويسمح `reified` وnon-local return. المقابل إن الـbytecode يتكرر، خصوصًا لو body كبير أو call sites كتير؛ ده يزوّد حجم APK وقد يؤثر على instruction cache وbuild time. JVM/JIT أحيانًا يعمل optimization مشابه، فاختيار `inline` لازم يرتبط بـAPI semantics أو قياس، مش شعار إن كل function أسرع.

## Why it matters and how it works

Inlining is most useful for small higher-order functions with frequent lambda calls or language features such as reified types. It changes emitted code and some control-flow rules. Android cost includes DEX size and startup-sensitive code layout.

## Worked example

JVM example: a small higher-order wrapper; `measure` is only an illustration, not a benchmark.
```kotlin
inline fun <T> use(block: () -> T): T = block()
fun main() {
    val result = use { 2 + 3 }
    println(result)
}
```
For performance claims, inspect release bytecode/DEX and profile a representative workload.

## Practical walkthrough

لما `inline fun <T> trace(block: () -> T)` صغيرة واتنادت آلاف المرات، compiler ينسخ body في call sites ويقدر يتجنب بعض lambda object/call overhead. لكن ده trade-off مع bytecode/DEX size؛ و`inline` مش بديل عن benchmark. في Android ابدأ بprofile لrelease build لأن R8/JIT/AOT ممكن يغيّروا النتيجة. كمان public inline function body يبان للـcallers وقت compilation وله قيود على وصوله لـprivate internals؛ تغيير implementation في library قد يحتاج recompilation للمستهلكين. استخدم `inline` لما تحتاج reified أو non-local return، أو عندك قياس لhot-path صغير.

## Trade-offs and decision criteria

Inline a small function when semantic features or measured overhead justify it. Use `noinline` for a lambda that must be stored, and avoid inlining a large body called widely. An ordinary function is easier on code size and binary evolution.

## Failure modes

A large parsing function is marked inline across dozens of modules because “inline is faster”; APK size and compile work rise without measured runtime gain. Another mistake is inlining a public API whose body exposes non-public implementation details; Kotlin restricts such access.

## Production perspective

A library exposes a tiny reified JSON adapter helper, but the actual parsing implementation remains ordinary code. Release builds are profiled for startup and DEX size before any performance conclusion.

## Interview answer — short

`inline` copies a function and eligible lambdas into call sites, which can remove some call and allocation overhead and enables reified type parameters. It increases generated code and is not a blanket performance fix. I profile the release build before applying it broadly.

## Interview answer — structured

Inlining is a compile-time transformation: the body, and eligible lambda arguments, are placed at the call site. That can remove lambda allocation or virtual calls in a small hot path, and it makes `reified T` possible because the concrete type is known there. The cost is repeated bytecode, potential DEX growth, and a public inline API whose body affects downstream compilation. I use it when semantics require reification or when measurements justify it, then compare release size and latency. I would not inline a large parser merely because it is called often; modern runtime optimizers and R8 also matter.

## Interview answer — deep senior

I distinguish semantic reasons from optimization reasons. Reified generics require inline because the call site supplies a concrete type. Small collection-like higher-order functions can avoid function-object and invocation overhead. But large or frequently called inline bodies expand at every call site; JVM optimizers already inline some ordinary calls at runtime, and Android behavior depends on the runtime and build optimizer. I compare APK/DEX size and representative benchmarks, while ensuring public inline APIs obey visibility and ABI constraints.

For an Android release build, I would compare DEX size and representative latency before and after inlining a frequently used helper. A tiny inline wrapper around a lambda may remove an allocation, but a large body copied across many call sites can enlarge the artifact and pressure instruction cache. If I need reified type access, I keep that wrapper small and delegate parsing or I/O to an ordinary function. Public inline implementation is visible to compiling callers, so I also review binary and source compatibility when publishing a library. The failure is equating compiler substitution with guaranteed runtime improvement.

## How to answer in the interview

- **Why:** Eliminate object allocation and virtual call overhead for higher-order functions.
- **How:** Mark functions accepting lambdas with `inline` so the compiler substitutes the bytecode directly at the call site.
- **Trade-offs:** Inlining large function bodies across many call sites leads to APK/DEX code bloat and cache invalidation.
- **Failure cases:** Inlining functions that do not take lambdas; the compiler issues a warning because no allocation savings occur while code duplication increases.
- **Production solution:** Reserve `inline` for small, frequently called higher-order utility functions (like collection operations or reified type helpers), measuring DEX size in release builds.

## Deep-dive talking points

Discuss noinline/crossinline, reified, non-local return, bytecode duplication, DEX size, and release profiling.

## Follow-up questions

- [KOT-13](../kot-13/): Why does `reified` need inline? **Answer:** the concrete type is substituted from each call site.
- [KOT-27](../kot-27/): When does inline lose? **Answer:** a large body duplicated across many sites can cost more than a call.

## Self-check rubric

Name two benefits and two costs, explain why benchmarking is needed, and identify a poor large-body candidate.

## References and reviewed-on date

- [Kotlin inline functions](https://kotlinlang.org/docs/inline-functions.html) — inlining, reified parameters, and lambda modifiers.

Technically reviewed against the linked primary documentation on 2026-10-13. Examples are illustrative JVM snippets; no Android device claim is made.
