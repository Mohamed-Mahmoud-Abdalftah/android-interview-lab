---
id: "KOT-22"
question: "What is Reflection, and when is it expensive or risky?"
topic: "Kotlin Core & Advanced"
code: "KOT"
group: "B"
phase: 1
priority: "P1"
order: 22
editorial_status: "reviewed"
---

# KOT-22

## Original interview question

What is Reflection, and when is it expensive or risky?

## What the interviewer evaluates

Describe runtime type/member inspection, its setup and invocation cost, and shrinker/security implications.

## Explanation in Arabic

Reflection معناها تفحص أو تنادي types وmembers وقت التشغيل بدل direct call معروف للـcompiler. Kotlin reflection API (`KClass`, `KProperty`) ممكن تحتاج `kotlin-reflect` على JVM؛ Java reflection بديل لمواقف مختلفة. التكلفة تشمل metadata، lookup، accessibility، allocation، وقلة فرص optimization، خصوصًا في startup أو hot loop. R8 ممكن يغيّر أسماء members أو يزيلها لو الاعتماد على reflection مش واضح له، فلازم keep rules ضيقة وتختبر release build. Reflection مش طريقة آمنة لاستخراج secrets أو تجاوز API contracts.

## Why it matters and how it works

Reflection supports frameworks such as dependency injection, serialization, or plugin discovery when types are only known at runtime. Its dynamic nature reduces compiler checking and can complicate Android shrinking and startup performance.

## Worked example

JVM illustration using class literal and declared member names; the `members` access requires the `kotlin-reflect` dependency matching the Kotlin toolchain.
```kotlin
import kotlin.reflect.full.memberProperties

data class Product(val id: String)
fun main() {
    val names = Product::class.memberProperties.map { it.name }
    println(names)
}
```
This is inspection, not a benchmark or Android integration test.

## Trade-offs and decision criteria

Use direct calls or generated adapters when schemas are known and startup matters. Reflection can reduce manual wiring for dynamic integrations, but carries dependency size, runtime failure, and shrinker configuration cost. Cache discovered metadata if repeated lookup is necessary; measure end-to-end.

## Failure modes

A serializer reflects on property names in debug but R8 renames or removes them in release, corrupting JSON. Prefer explicit serializers or narrowly scoped keep rules and release tests. Avoid `isAccessible = true` as a routine way around encapsulation.

## Production perspective

An Android analytics SDK uses generated event serializers for known models. A rare plugin loader uses reflection at initialization, caches metadata, validates names, and has a minified release test to catch missing classes.

## Interview answer — short

Reflection inspects or invokes program structure at runtime. It is useful for dynamic frameworks but can cost startup time, size, and runtime safety, and it needs careful R8 rules. I prefer generated or direct calls for known schemas.

## Interview answer — structured

Kotlin reflection exposes types and properties through APIs such as `KClass` and `KProperty`, often with the `kotlin-reflect` artifact on JVM. It enables runtime discovery, but lookup and invocation are less optimizable than direct calls and may fail after shrinking if names or members are changed. In Android I inspect whether the framework already uses code generation, keep rules, or cached metadata, then test a minified release build. An ORM or serializer may use reflection to discover members dynamically, but a known schema can often use generated adapters. I would ask whether discovery happens once at startup or repeatedly in a hot loop, whether `kotlin-reflect` adds size, and whether R8 knows which members must remain.

## Interview answer — deep senior

I distinguish discovery cost from invocation cost and dependency size. Reflection is reasonable when the set of types is genuinely dynamic; it is less attractive for every row of a hot serialization loop. Kotlin and Java reflection have different APIs, and the library/toolchain version must align. R8 can remove or rename members invisible to static analysis, so the production contract must include explicit rules or generated code. A release-mode test and startup trace provide evidence; speculative micro-optimizations do not. Reflection moves decisions from compile time to runtime. I would cache discovery if it is needed repeatedly, but I would not assume caching fixes every cost. I also avoid accessing private members as a routine shortcut because it makes behavior fragile. Startup tracing and representative workload profiling decide whether reflection is material for this app. A dependency-injection library may generate factories at build time precisely to avoid runtime discovery. If a plugin mechanism truly needs dynamic lookup, I keep it off the render hot path, cache validated metadata, and test it under shrinking. The review weighs flexibility against startup and failure cost.

## Deep-dive talking points

Discuss `kotlin-reflect`, Java reflection bridges, annotation processors/codegen, R8 keep rules and startup profiling.

## Follow-up questions

- [KOT-23](../kot-23/): Can Kotlin access Java reflection? **Answer:** yes, JVM interop bridges Kotlin and Java reflection APIs.
- [KOT-30](../kot-30/): How should reflection cost be evaluated? **Answer:** measure startup/hot-path behavior in minified release conditions.

## Self-check rubric

Name one justified use, two costs, and a release-only failure mode.

## References and reviewed-on date

- [Kotlin reflection](https://kotlinlang.org/docs/reflection.html) — reflection APIs and dependency.
- [Android R8 keep rules](https://developer.android.com/topic/performance/app-optimization/keep-rules-overview) — reflection and shrinking.

Technically reviewed against the linked primary documentation on 2026-10-11. Examples are illustrative JVM snippets unless explicitly labeled conceptual; no Android device claim is made.
