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

## Practical walkthrough

`@JvmInline value class UserId(val value: String)` يمنع تبديل `UserId` بـ`OrderId` وقت compile ويديك validation في `init`. لكن ما تقولش zero allocation: القيمة ممكن تتعمل لها boxing لما تستخدمها كـnullable، generic، أو interface، والتمثيل يتأثر بالسياق. الـJVM signature/name mangling ممكن يغيّر Java-facing API؛ جرّب الاستدعاء من Java فعلًا، خصوصًا library عامة أو serialization framework. كمان value class مش object identity: ما تستخدمش `===` عليها. لو ID بيدخل database وJSON، اعمل adapters صريحة واختبر round trip بدل افتراض إن frameworks تفهم wrapper تلقائيًا.

## Trade-offs and decision criteria

Prefer value class for one-field identifiers or units with clear invariants. Use data class for multiple fields or when stable object identity/interop simplicity matters. A typealias is cheaper syntactically but provides no distinct type. Avoid promising performance without profiling boxed generic and nullable paths.

## Failure modes

An API returns `List<UserId>` and assumes every element is unboxed because the class is “inline”; generic storage can box. Another risk is Java callers unable to access default mangled/unboxed signatures. Design and test the Java surface deliberately.

## Production perspective

A commerce app models `ProductId` and `OrderId` as separate value classes, validates them at the network boundary, and uses explicit serializers. Benchmark hot paths using release builds; database and Java adapter tests cover representation boundaries.

## Interview answer — short

A value class creates a distinct domain type around one value, often without a separate wrapper at a suitable call site. It can box in nullable, generic, or interface contexts, and Java interop needs testing. I use it to prevent ID mix-ups, not as a guaranteed allocation optimization.

## Interview answer — structured

A JVM value class lets me express `UserId` as a distinct type from a plain `String`, so the compiler rejects an accidental `OrderId` at the API boundary. The representation may use the underlying value at some call sites, but boxing can occur with generics, nullability, or interfaces; I never promise zero allocations. It also has no identity semantics. For a public Android library I test Java callers, serialization, and reflection against the Kotlin compiler version, since generated JVM signatures differ from a regular wrapper class. I choose it primarily for domain correctness and confirm performance only with measurement.

## Interview answer — deep senior

A value class has no object identity in its source-level contract. Its key benefit is a domain-specific type with a single stored property, potentially represented as the underlying value. The compiler may box it where a generic or interface representation is needed, so the cost model is use-site dependent. Public Java APIs require deliberate boxed exposure or adapters, and serialization libraries need explicit rules. I review validation, ABI, data persistence, and benchmarks on release builds rather than treating `@JvmInline` as a universal optimization.

For domain IDs, `UserId("u-7")` prevents passing an order ID to a user lookup, and an `init` check can reject blank values at construction. But a value class can be boxed when nullable, stored in a generic collection, or viewed through an interface, so I would not promise zero allocations. Java callers may see mangled or inaccessible signatures unless the API provides a deliberate adapter or boxed exposure supported by the toolchain. Serialization must also explicitly encode the underlying value and validate it on decode. I choose this feature for a type-level invariant first, then measure performance and test JVM interop.

## How to answer in the interview

- **Why:** Create domain-specific, strongly-typed wrappers around primitive values without heap allocation overhead.
- **How:** Define `@JvmInline value class UserId(val raw: String)` so the compiler replaces instances with the underlying type in bytecode.
- **Trade-offs:** Value classes box into heap objects when used in generic contexts, nullable types, or collections (`List<UserId>`).
- **Failure cases:** Name-mangled value class methods called from Java code, resulting in cryptic compiler errors or missing symbols on the Java side.
- **Production solution:** Use value classes to enforce domain type safety for IDs, currencies, and tokens, adding `@JvmName` when Java interoperability is required.

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

Technically reviewed against the linked primary documentation on 2026-10-13. Examples are illustrative JVM snippets unless explicitly labeled conceptual; no Android device claim is made.
