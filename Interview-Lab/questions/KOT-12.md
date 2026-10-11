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

## Trade-offs and decision criteria

Inline a small function when semantic features or measured overhead justify it. Use `noinline` for a lambda that must be stored, and avoid inlining a large body called widely. An ordinary function is easier on code size and binary evolution.

## Failure modes

A large parsing function is marked inline across dozens of modules because “inline is faster”; APK size and compile work rise without measured runtime gain. Another mistake is inlining a public API whose body exposes non-public implementation details; Kotlin restricts such access.

## Production perspective

A library exposes a tiny reified JSON adapter helper, but the actual parsing implementation remains ordinary code. Release builds are profiled for startup and DEX size before any performance conclusion.

## Interview answer — short

`inline` substitutes a function and eligible lambdas at call sites. It can remove lambda-call overhead and enable reified types, but duplicates bytecode. I reserve it for small APIs or measured hot paths.

## Interview answer — structured

Kotlin inlining can eliminate some higher-order function overhead because the compiler inserts the body at the call site. It also enables non-local returns and reified type parameters. The cost is code duplication, which can increase DEX size, compile time, and potentially hurt instruction-cache behavior. I would inspect generated code and profile release builds rather than assume every inline declaration improves Android performance. It can also enable reified type checks or a caller-level return. For a large function, the duplicated body can outweigh those gains across many call sites. A public inline API also deserves compatibility review because its body is copied into other modules. I keep those wrappers small and avoid exposing private implementation details through them.

## Interview answer — deep senior

I distinguish semantic reasons from optimization reasons. Reified generics require inline because the call site supplies a concrete type. Small collection-like higher-order functions can avoid function-object and invocation overhead. But large or frequently called inline bodies expand at every call site; JVM optimizers already inline some ordinary calls at runtime, and Android behavior depends on the runtime and build optimizer. I compare APK/DEX size and representative benchmarks, while ensuring public inline APIs obey visibility and ABI constraints. I split inline decisions into semantics and optimization. For performance, the compiler can substitute eligible lambdas and sometimes avoid closure allocations and virtual calls. The cost is duplicated bytecode, which can increase DEX size, build work, and pressure on code locality. A public inline function also exposes its body to downstream binaries, so visibility and compatibility become concerns. I keep the inline layer small and put heavy parsing or I/O work in an ordinary function. Android runtime and optimizer behavior can differ by build mode and device, so I compare minified release artifacts for size and real latency. The annotation is a trade, not a blanket optimization. A valid optimization review compares a control build with an inline build using representative calls and minification. I would measure latency, allocation, and artifact size, and check that the improved case is actually a user-visible bottleneck. Otherwise an ordinary function is simpler to evolve.

## Deep-dive talking points

Discuss noinline/crossinline, reified, non-local return, bytecode duplication, DEX size, and release profiling.

## Follow-up questions

- [KOT-13](../kot-13/): Why does `reified` need inline? **Answer:** the concrete type is substituted from each call site.
- [KOT-27](../kot-27/): When does inline lose? **Answer:** a large body duplicated across many sites can cost more than a call.

## Self-check rubric

Name two benefits and two costs, explain why benchmarking is needed, and identify a poor large-body candidate.

## References and reviewed-on date

- [Kotlin inline functions](https://kotlinlang.org/docs/inline-functions.html) — inlining, reified parameters, and lambda modifiers.

Technically reviewed against the linked primary documentation on 2026-10-11. Examples are illustrative JVM snippets; no Android device claim is made.
