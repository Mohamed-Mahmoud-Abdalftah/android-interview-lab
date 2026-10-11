---
id: "KOT-27"
question: "When does inline cause code bloat rather than a performance win?"
topic: "Kotlin Core & Advanced"
code: "KOT"
group: "C"
phase: 1
priority: "P1"
order: 27
editorial_status: "reviewed"
---

# KOT-27

## Original interview question

When does inline cause code bloat rather than a performance win?

## What the interviewer evaluates

Explain code-size trade-off with call-site count, body size, and runtime optimizer behavior.

## Explanation in Arabic

لو `inline` function body كبير واتنادت من مواقع كتير، compiler ينسخ body في كل موقع. المكسب من إزالة call أو lambda object ممكن يبقى أصغر من تكلفة DEX/APK size، instruction cache، ووقت build. ده واضح في functions فيها parsing أو logging أو branching كتير ومش hot أصلًا. JVM/JIT وR8 ممكن يعملوا optimizations تانية، لذلك لازم تقيس release artifact على أجهزة ممثلة بدل ما تحكم من source. خلي wrapper صغير inline لو محتاج `reified`، وسيب العمل الثقيل في function عادية.

## Why it matters and how it works

Inlining trades one implementation body for duplicated code at call sites. It is not a free speed switch; small hot higher-order functions have a different profile from large cold functions.

## Worked example

Illustrative split: only the type-token wrapper is inline; heavy work stays ordinary.
```kotlin
inline fun <reified T : Any> typeName(): String = T::class.java.name
fun parsePayload(bytes: ByteArray): Int = bytes.sumOf { it.toInt() and 0xff }
```
This is not a benchmark; compare release bytecode size and measured latency before changing a real parser.

## Trade-offs and decision criteria

Use inline for semantic needs (`reified`, non-local return) or measured hot small lambdas. Ordinary functions keep bytecode compact and can still be optimized at runtime. Public inline APIs also constrain binary evolution and visibility of referenced declarations.

## Failure modes

A large inline function is called in hundreds of Compose rendering paths, increasing DEX size and startup pressure while doing no measurable hot work. Remove inline from the heavy body, profile again, and keep only a small inline adapter if needed.

## Production perspective

A media app profiles frame-time hot paths with a release build, checks DEX/APK delta, and compares representative devices. A tiny inlined iterator helper survives review; a large decoding function remains ordinary.

## Interview answer — short

Inline loses when duplicated body size across many call sites outweighs call or lambda overhead saved. Large cold functions are especially poor candidates. I inspect generated code and measure release performance and size.

## Interview answer — structured

An inline declaration copies its body into each call site. That can help a tiny higher-order hot path, but a large function used widely can bloat DEX, increase compile work, and hurt code locality. JVM optimizers may inline ordinary calls themselves. I use inline when language semantics require it or benchmarks show benefit, and keep heavy work behind a normal function. For example, a parser with branching, logging, and error mapping called from many modules is likely to grow the DEX if marked inline. A tiny reified wrapper around that parser might still be justified. If there is no meaningful gain, the ordinary function keeps the API simpler. I would keep a tiny inline wrapper only if it genuinely needs reified type access or measured lambda savings. The expensive parser stays as an ordinary call.

## Interview answer — deep senior

I evaluate body size, call-site count, frequency, lambda allocation, and runtime optimizer behavior. The relevant metric is not one microbenchmark alone: on Android, DEX size and startup/layout may matter as much as nanoseconds per call. Public inline bodies can also expose ABI/visibility constraints to downstream callers. A common pattern is a tiny reified wrapper delegating to a non-inline implementation. I compare minified release builds and device traces, then keep the simpler implementation unless the gain is material. Inlining substitutes code at each call site. That can avoid a function-object allocation or virtual call in a small hot higher-order function, but duplicated bodies accumulate as call sites grow. Runtime JIT and build optimizers can also inline ordinary functions, so source-level intuition is unreliable. I would keep a semantic inline function when I need `reified` or non-local return, but move heavy work behind a normal function. My review would compare release size, compiler output where useful, and real hot-path traces, and would include a correctness check around changed control flow. A microbenchmark should not be the only evidence because it may miss DEX growth and startup effects. I would include package size and frame or startup traces for the actual workload, and inspect whether R8 or the runtime already optimizes the ordinary function.

## Deep-dive talking points

Discuss call-site expansion, DEX size, instruction cache, JIT/R8 optimization, ABI concerns, and benchmark pitfalls.

## Follow-up questions

- [KOT-12](../kot-12/): What does inline save? **Answer:** eligible function/lambda call overhead and some allocations.
- [KOT-13](../kot-13/): Why keep a small wrapper inline? **Answer:** it can provide reified type information while delegating heavy work.

## Self-check rubric

Name a bloat scenario, a valid inline scenario, and two release measurements.

## References and reviewed-on date

- [Kotlin inline functions](https://kotlinlang.org/docs/inline-functions.html) — benefits and code growth.

Technically reviewed against the linked primary documentation on 2026-10-11. Examples are illustrative JVM snippets unless explicitly labeled conceptual; no Android device claim is made.
