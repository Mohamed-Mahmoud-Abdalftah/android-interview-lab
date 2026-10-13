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

## Practical walkthrough

لو serializer أو DI framework بيكتشف properties وقت runtime، reflection ممكن يكون مناسب لو types مش معروفة وقت compile. لكن `kotlin-reflect` dependency تزود حجم وتكلفة init، والبحث المتكرر عن members أو invocation في hot path أغلى من direct call غالبًا. في Android release build، R8 ممكن يغيّر أسماء أو يحذف metadata حسب rules؛ اتبع تعليمات framework وجرّب minified build، مش debug بس. لو set الأنواع معلوم، generated adapter أو explicit map أبسط وأكثر قابلية للتحقق. اعمل cache لmetadata لو reflection ضرورية، لكن راجع memory/lifecycle.

## Trade-offs and decision criteria

Use direct calls or generated adapters when schemas are known and startup matters. Reflection can reduce manual wiring for dynamic integrations, but carries dependency size, runtime failure, and shrinker configuration cost. Cache discovered metadata if repeated lookup is necessary; measure end-to-end.

## Failure modes

A serializer reflects on property names in debug but R8 renames or removes them in release, corrupting JSON. Prefer explicit serializers or narrowly scoped keep rules and release tests. Avoid `isAccessible = true` as a routine way around encapsulation.

## Production perspective

An Android analytics SDK uses generated event serializers for known models. A rare plugin loader uses reflection at initialization, caches metadata, validates names, and has a minified release test to catch missing classes.

## Interview answer — short

Reflection inspects types or members at runtime. It is useful when the type set is genuinely dynamic, but it can add dependency size and lookup cost and can break under shrinking if metadata assumptions are wrong. I prefer generated or explicit code for known schemas.

## Interview answer — structured

I distinguish discovery from ordinary invocation. Reflection lets a framework inspect types or members at runtime, which can support plugins or schema-driven tools. On Android, that flexibility has costs: `kotlin-reflect` can increase artifact size, repeated member lookup can be expensive, and R8 may rename or remove information that a reflective framework expects. I would inspect the framework’s documented keep rules and run release, minified tests. If the schema is known at compile time, generated adapters or explicit mapping are easier to reason about. If reflection is required, I cache stable metadata and measure the actual workload.

## Interview answer — deep senior

I distinguish discovery cost from invocation cost and dependency size. Reflection is reasonable when the set of types is genuinely dynamic; it is less attractive for every row of a hot serialization loop. Kotlin and Java reflection have different APIs, and the library/toolchain version must align. R8 can remove or rename members invisible to static analysis, so the production contract must include explicit rules or generated code. A release-mode test and startup trace provide evidence; speculative micro-optimizations do not.

A dynamic plugin registry is a reasonable reflection use case because the concrete types may not be known at compile time. A known JSON schema or Room entity set is different: generated adapters are easier to verify and avoid repeated discovery. On Android I would run the minified release variant because R8 cannot infer every reflective member access from static call sites; the framework’s documented consumer rules and a targeted keep rule may be needed. I would cache stable metadata if lookup dominates, but inspect startup time and memory before broad caching. A debug-only passing test cannot establish that reflective names survive shrinking.

## How to answer in the interview

- **Why:** Dynamically inspect and invoke classes, methods, and properties at runtime for serialization or DI frameworks.
- **How:** Use Kotlin reflection (`KClass`, `::class`) or Java reflection (`Class.forName()`, `getMethod()`).
- **Trade-offs:** Reflection is significantly slower than direct calls, bypasses compile-time verification, and requires bundling the heavy `kotlin-reflect` library (~2.5MB).
- **Failure cases:** R8/Proguard obfuscating or shrinking reflected class names or field members in release builds, causing runtime `NoSuchMethodException`.
- **Production solution:** Prefer compile-time annotation processing and code generation (KSP, Moshi, Kotlinx.serialization) over runtime reflection in Android production apps.

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

Technically reviewed against the linked primary documentation on 2026-10-13. Examples are illustrative JVM snippets unless explicitly labeled conceptual; no Android device claim is made.
