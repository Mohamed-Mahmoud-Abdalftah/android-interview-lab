---
id: "KOT-23"
question: "What is Java/Kotlin interoperability (platform types, SAM interfaces, nullability)?"
topic: "Kotlin Core & Advanced"
code: "KOT"
group: "B"
phase: 1
priority: "P1"
order: 23
editorial_status: "reviewed"
---

# KOT-23

## Original interview question

What is Java/Kotlin interoperability (platform types, SAM interfaces, nullability)?

## What the interviewer evaluates

Handle Java platform types, nullability annotations, SAM conversion, checked exceptions, and collection mutability boundaries.

## Explanation in Arabic

Kotlin وJava بيتبادلوا JVM types، لكن Java API من غير nullability annotations بتوصل Kotlin كـplatform type `T!`: compiler يسمح تتعامل معاها nullable أو non-null، والمخاطرة عليك. Java `List` كمان ممكن يتشاف mutable/read-only platform view، فلا تفترض snapshot. SAM conversion تخليك تمرر lambda لواجهة Java فيها abstract method واحدة، لكن راجع lifetime وthreading. Java callers لـKotlin APIs قد يحتاجوا `@JvmStatic`, `@JvmOverloads`, أو adapters حسب التصميم، وKotlin ما بتفرضش checked exceptions بنفس طريقة Java. الحد الفاصل لازم يبقى متعاقد ومختبَر.

## Why it matters and how it works

Interop lets Android apps migrate incrementally, but source-language guarantees do not cross ambiguous Java APIs automatically. Nullability annotations and explicit adapters reduce uncertainty at the boundary.

## Worked example

Illustrative Kotlin/JVM code using Java `Runnable`; the lambda is converted to the SAM interface and runs synchronously when `run()` is called.
```kotlin
fun main() {
    val action: Runnable = Runnable { println("work") }
    action.run()
}
```
For an unannotated Java return, assign to `String?` and validate before domain use.

## Trade-offs and decision criteria

Keep Java libraries where stable; annotate or wrap ambiguous contracts rather than rewriting all code. SAM adapters are concise but can capture lifecycle objects. Expose explicit Java-friendly APIs when the module has Java consumers; annotations should be chosen intentionally, not sprayed everywhere.

## Failure modes

A Java getter returns null at runtime but Kotlin stores its platform type as `String` and dereferences it, causing NPE. Another failure is passing a lambda that captures Activity to a long-lived Java listener without unregistering it.

## Production perspective

A mixed-language banking app wraps legacy Java account APIs in a Kotlin boundary that checks nulls and converts failures to typed domain outcomes. Java UI callers use tested overloads/adapters, and listener registrations are removed on lifecycle end.

## Interview answer — short

Kotlin interoperates directly with Java, but unannotated Java values become platform types with uncertain nullability. SAM interfaces accept lambdas. I validate null and mutability contracts at the boundary and test both language callers.

## Interview answer — structured

Java interop lets a Kotlin Android app retain stable Java libraries while new features migrate incrementally. The main type hazard is an unannotated Java return: Kotlin sees a platform type such as `String!`, and treating it as non-null does not make the runtime value safe. I prefer nullability annotations in the Java API or one Kotlin adapter that validates a nullable local and constructs a sound domain model. SAM conversion makes a Java listener easy to supply as a lambda, but I still check whether the listener is retained and unregister it with the screen. When Java calls new Kotlin code, I inspect generated JVM signatures, overloads, and exception documentation rather than assuming the Kotlin source syntax is the public API. Cross-language tests protect these boundaries.

## Interview answer — deep senior

I treat Java/Kotlin interop as an external contract even though both languages run on the JVM. Kotlin platform types mean the Java nullability promise is missing or incomplete; an optimistic non-null assignment can still throw later. Java collections can expose mutation through another alias even if Kotlin presents a read-only interface. I normalize uncertain data at the boundary, ideally with Java annotations plus explicit validation, and return domain types whose invariants callers can trust. SAM conversion replaces adapter syntax, not callback ownership: a long-lived Java listener capturing an Activity needs an unregister path. In the opposite direction, Kotlin properties, default arguments, suspend functions, value classes, and checked-exception differences can produce awkward or surprising Java APIs. I inspect compiled signatures and provide adapters or annotations where needed. I test realistic callers from both languages, including null returns and listener cleanup. The migration goal is a clearer contract at each touched boundary, not just a new source language. For example, when a Java SDK returns an unannotated customer ID, I assign it to a nullable local, reject a missing value, and record a typed adapter error; I do not let `!!` spread into UI code. If a Java client needs a Kotlin suspend operation, I offer a deliberate Java-facing adapter instead of exposing coroutine machinery as an accidental API.

## Deep-dive talking points

Explain platform types, nullability annotations, SAM conversion, Java collection mapping, generated JVM signatures and listener lifecycle.

## Follow-up questions

- [KOT-03](../kot-03/): Why can platform types throw? **Answer:** Kotlin permits a non-null view of an unannotated Java result that may actually be null.
- [KOT-21](../kot-21/): What about value classes from Java? **Answer:** default generated representation and names may need deliberate boxed exposure/adapters.

## Self-check rubric

Explain `T!`, demonstrate a SAM use, and identify a Java collection or listener hazard.

## References and reviewed-on date

- [Calling Java from Kotlin](https://kotlinlang.org/docs/java-interop.html) — platform types and SAM.
- [Calling Kotlin from Java](https://kotlinlang.org/docs/java-to-kotlin-interop.html) — JVM API design.

Technically reviewed against the linked primary documentation on 2026-10-11. Examples are illustrative JVM snippets unless explicitly labeled conceptual; no Android device claim is made.
