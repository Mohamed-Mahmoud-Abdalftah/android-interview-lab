---
id: "KOT-21"
question: "What are value classes, and what performance/interop caveats do they have?"
topic: "Kotlin Core & Advanced"
code: "KOT"
group: "B"
phase: 1
priority: "P1"
order: 21
editorial_status: "reviewed"
---

# KOT-21

## Original interview question

What are value classes, and what performance/interop caveats do they have?

## What the interviewer evaluates

Explain distinct domain type identity, conditional unboxed representation, boxing sites, and Java/serialization boundaries.

## Explanation in Arabic

`@JvmInline value class` بتلف قيمة واحدة في type مستقل عن النوع الداخلي، فـ`UserId` ما يتخلطش بسهولة مع `OrderId` حتى لو الاتنين `String`. الـcompiler يقدر يمثّلها unboxed في حالات كتير، لكن nullable، generic، interface، وبعض Java boundaries ممكن تعمل boxing. ما تقولش “zero allocations دائمًا”. هي كمان مش object identity ومينفعش تعتمد عليها كـsecret wrapper؛ القيمة لسه موجودة في الذاكرة والـserialization يحتاج contract واضح. validation في `init` يحمي construction المعتاد، لكن لازم تراجع deserialization والinterop.

## Why it matters and how it works

Value classes encode domain distinctions without always paying a wrapper allocation. The representation changes by use site, so performance and Java ABI require inspection. Type safety is the primary benefit; allocation reduction is conditional.

## Worked example

JVM illustration with a validated identifier.
```kotlin
@JvmInline value class UserId(val value: String) {
    init { require(value.isNotBlank()) }
}
fun loadUser(id: UserId): String = id.value
fun main() = println(loadUser(UserId("u-7")))
```
A Java-facing or serialization API needs explicit interop tests for the compiler version in use.

## Trade-offs and decision criteria

Prefer value class for one-field identifiers or units with clear invariants. Use data class for multiple fields or when stable object identity/interop simplicity matters. A typealias is cheaper syntactically but provides no distinct type. Avoid promising performance without profiling boxed generic and nullable paths.

## Failure modes

An API returns `List<UserId>` and assumes every element is unboxed because the class is “inline”; generic storage can box. Another risk is Java callers unable to access default mangled/unboxed signatures. Design and test the Java surface deliberately.

## Production perspective

A commerce app models `ProductId` and `OrderId` as separate value classes, validates them at the network boundary, and uses explicit serializers. Benchmark hot paths using release builds; database and Java adapter tests cover representation boundaries.

## Interview answer — short

A value class creates a distinct type around one value and may avoid a wrapper allocation in many cases. Boxing can occur with nullable, generic, interface, and Java interop use. I choose it mainly for type-safe domain identifiers, then measure costs.

## Interview answer — structured

`@JvmInline value class UserId(val value: String)` prevents accidental mixing with a plain `String` or a different ID class. On the JVM it often uses the underlying representation, but not in every context: nullable and generic positions can box, and generated methods can be awkward for Java. I validate construction, define serialization explicitly, and profile before claiming an allocation win. If the model has multiple fields or rich identity, a regular or data class is clearer. I would use a `UserId` value class to prevent passing an `OrderId` to a user lookup, which a type alias cannot do. I would also avoid selling it as allocation-free: nullable, generic, and interface paths can box the value. If Java callers or a serializer use the type, I test the generated API and wire format for the Kotlin/compiler version in the project.

## Interview answer — deep senior

A value class has no object identity in its source-level contract. Its key benefit is a domain-specific type with a single stored property, potentially represented as the underlying value. The compiler may box it where a generic or interface representation is needed, so the cost model is use-site dependent. Public Java APIs require deliberate boxed exposure or adapters, and serialization libraries need explicit rules. I review validation, ABI, data persistence, and benchmarks on release builds rather than treating `@JvmInline` as a universal optimization. It lets the compiler reject accidental mixing of identifiers or units while often representing the value without a separate wrapper. The word often is important: boxing can occur for nullable use, generic containers, interfaces, and other interop positions. Validation in `init` helps ordinary construction but should be verified at external-data boundaries. I compare it with a typealias, which adds no type distinction, and a data class, which handles multiple fields and simpler object interop. For performance claims I inspect generated code and benchmark release builds instead of assuming every value-class use removes allocations.

## Deep-dive talking points

Compare typealias and value class, identity, method mangling, boxed generics, nullability, Java exposure, and serializer tests.

## Follow-up questions

- [KOT-18](../kot-18/): Why not use a typealias for IDs? **Answer:** aliases remain assignment-compatible with their underlying type.
- [KOT-30](../kot-30/): How would you assess allocation cost? **Answer:** inspect generated code and profile representative release workloads.

## Self-check rubric

State the single-field rule, identify two boxing situations, and explain one Java interop risk.

## References and reviewed-on date

- [Kotlin inline value classes](https://kotlinlang.org/docs/inline-classes.html) — representation and boxing.
- [Calling Kotlin from Java](https://kotlinlang.org/docs/java-to-kotlin-interop.html) — Java exposure.

Technically reviewed against the linked primary documentation on 2026-10-11. Examples are illustrative JVM snippets unless explicitly labeled conceptual; no Android device claim is made.
