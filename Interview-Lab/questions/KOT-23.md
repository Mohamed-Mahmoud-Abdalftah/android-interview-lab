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

## Practical walkthrough

Java SDK فيها `String getAccountId()` بدون annotations بتظهر في Kotlin كـplatform type، فcompiler يسمح استخدام خطر. خذ `val id: String? = sdk.accountId` وvalidate بدل ما تمررها مباشرة لدومين non-null. `Runnable { ... }` مثال SAM conversion مع Java interface، لكن التنفيذ والتوقيت يفضلوا تابعين للـAPI؛ SAM مش معناها async. لو Java callers بيستخدموا Kotlin API، راجع default arguments، checked exceptions، overloads واسم الـJVM؛ annotations زي `@JvmOverloads` تستخدم عند الحاجة فقط. اختبر الاتجاهين من ملف Java حقيقي في module مش بالتخمين.

## Trade-offs and decision criteria

Keep Java libraries where stable; annotate or wrap ambiguous contracts rather than rewriting all code. SAM adapters are concise but can capture lifecycle objects. Expose explicit Java-friendly APIs when the module has Java consumers; annotations should be chosen intentionally, not sprayed everywhere.

## Failure modes

A Java getter returns null at runtime but Kotlin stores its platform type as `String` and dereferences it, causing NPE. Another failure is passing a lambda that captures Activity to a long-lived Java listener without unregistering it.

## Production perspective

A mixed-language banking app wraps legacy Java account APIs in a Kotlin boundary that checks nulls and converts failures to typed domain outcomes. Java UI callers use tested overloads/adapters, and listener registrations are removed on lifecycle end.

## Interview answer — short

Kotlin and Java interoperate on the JVM, but the boundary needs explicit contracts. Unannotated Java references become platform types, so I validate them before using non-null Kotlin APIs. Java SAM interfaces accept Kotlin lambdas; that says nothing about threading.

## Interview answer — structured

I treat Java interop as an external boundary rather than an automatic safety guarantee. An unannotated Java return is a platform type, so Kotlin may allow a call that fails at runtime. I convert it to a nullable local, validate it, and expose a clear Kotlin domain type. SAM conversion makes a lambda convenient for a Java single-abstract-method interface, but the Java API still defines when and where it runs. In the other direction I test Java callers for generated names, overloads, nullability annotations, and exceptions. In a mixed codebase I add boundary tests before relying on a Kotlin-only usage example.

## Interview answer — deep senior

I treat Java/Kotlin interop as an external contract even though both languages run on the JVM. Kotlin platform types mean the Java nullability promise is missing or incomplete; an optimistic non-null assignment can still throw later. Java collections can expose mutation through another alias even if Kotlin presents a read-only interface. I normalize uncertain data at the boundary, ideally with Java annotations plus explicit validation, and return domain types whose invariants callers can trust. SAM conversion replaces adapter syntax, not callback ownership: a long-lived Java listener capturing an Activity needs an unregister path. In the opposite direction, Kotlin properties, default arguments, suspend functions, value classes, and checked-exception differences can produce awkward or surprising Java APIs.

As a concrete boundary, an unannotated Java `getAccountId()` may return null while Kotlin allows direct use. I assign it to `String?`, validate it, and expose `AccountId` only after the invariant holds. For a Java listener, Kotlin’s SAM lambda removes boilerplate but does not specify the thread or registration lifetime, so I still unregister it when the owner stops. In the reverse direction, I compile a small Java consumer test for default arguments, overload names, value classes, and checked exceptions. That catches surprising generated APIs before a mixed-language team depends on them.

## How to answer in the interview

- **Why:** Enable smooth coexistence and migration between Kotlin and existing Java codebases.
- **How:** Handle unannotated Java types as platform types (`T!`), use `@JvmStatic`, `@JvmOverloads`, and `@file:JvmName` to craft idiomatic Java APIs.
- **Trade-offs:** Platform types bypass Kotlin null safety; treating them as non-null without validation risks runtime crashes.
- **Failure cases:** Directly assigning an unannotated Java getter returning `null` to a non-null Kotlin variable, triggering an immediate or delayed `NullPointerException`.
- **Production solution:** Immediately assign platform types to explicit nullable types (`String?`) at the boundary, validate them, and expose clean Kotlin models to the rest of the app.

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

Technically reviewed against the linked primary documentation on 2026-10-13. Examples are illustrative JVM snippets unless explicitly labeled conceptual; no Android device claim is made.
