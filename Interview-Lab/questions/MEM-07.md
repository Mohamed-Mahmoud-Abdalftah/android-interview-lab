---
id: "MEM-07"
question: "Explain int versus Integer in Java interoperability."
topic: "Memory Management, ANR & Performance"
code: "MEM"
group: "A"
phase: 1
priority: "P1"
order: 62
editorial_status: "reviewed"
---

# MEM-07

## Original interview question

Explain int versus Integer in Java interoperability.

## What the interviewer evaluates

- Distinguish Java primitive `int` from nullable reference `java.lang.Integer`.
- Explain Kotlin mapping and platform-type uncertainty at Java boundaries.
- Identify `Integer` identity/caching and null-unboxing pitfalls.

## Explanation in Arabic

Java `int` قيمة primitive لا تقبل null، بينما `Integer` object wrapper يقبل null ويُستخدم حيث مطلوب reference مثل generics. Kotlin تعرض Java `int` كـ`Int`، و`Integer` غالبًا كـ`Int?` حسب annotations والسياق، لكن generic Java collection ممكن عناصرها تظهر platform types بسبب نقص معلومات nullability. لذلك ما تفترضش إن `List<Integer>` سليمة من null. في المقارنة استخدم `==` للقيمة، مش `===` للهوية؛ cached wrappers تجعل الهوية متغيرة مع القيمة. لو `Integer` null واتعمل له unboxing لحساب رقم سيحدث crash.

## Why it matters and how it works

Java primitives store numeric values; wrappers are objects with identity and nullable references. Autoboxing converts between them where Java expects a wrapper or primitive. Kotlin maps both into its numeric API but generates primitive or boxed JVM representations according to nullable/generic usage. Java nullability annotations can improve compiler checks, yet unannotated platform types require explicit boundary validation.

## Worked example

A Java SDK method `Integer getRetryCount()` may return null. At the Kotlin boundary use `val retries: Int = sdk.retryCount ?: 0` if zero is a valid product default, or reject null explicitly if it signals a protocol error. Do not compare two returned wrappers with reference identity. The snippet assumes the SDK's nullability contract is confirmed; it is not a full integration example.

## Trade-offs and decision criteria

Primitive `int` avoids null and wrapper overhead; `Integer` is necessary for nullable values and generic APIs. Kotlin `Int?` accurately represents optional counts, but a sentinel or result type may communicate an error more clearly. Preserve null as “unknown” when zero would be misleading. Optimize boxed collections only where profiling shows a cost.

## Failure modes

Auto-unboxing null throws. `===` tests happen to pass for cached small values and fail elsewhere. Platform types let null slip into a non-null Kotlin assignment, leading to runtime assertions or NPE. Treat Java SDK output as an external boundary and test null and out-of-range values.

## Production perspective

Wrap Java-facing SDK responses in a Kotlin adapter that validates nullability and domain range once. Unit test null, zero, maximum, and ordinary values. Keep the rest of the Android app on a domain type such as `RetryPolicy` instead of propagating platform types through UI logic.

## Interview answer — short

“Java `int` is a non-null primitive; `Integer` is a nullable object wrapper. Kotlin maps them to numeric types but Java platform nullability and auto-unboxing need explicit care.”

## Interview answer — structured

“A Java `int` stores a primitive value, while `Integer` is a reference object, which supports null and generic collections. Boxing and unboxing bridge them. In Kotlin, primitive int maps to `Int`; a boxed `Integer` can surface as nullable or as a platform type when annotations are missing. I validate null at the Java boundary rather than relying on optimistic Kotlin types. I compare numbers by value, because wrapper identity and caching are not a correctness rule.”

## Interview answer — deep senior

“The distinction matters at API boundaries. A Java method returning `int` promises a value; one returning `Integer` can represent absence and can be null unless its contract says otherwise. Kotlin's mapping makes both pleasant to use, but an unannotated Java value may be a platform type that bypasses strict null checking. I convert it into an explicit domain value in one adapter, deciding whether null means unknown, default, or error. This prevents auto-unboxing crashes and avoids spreading platform uncertainty. I never use wrapper identity for equality, since caching is an implementation behavior. If large numeric collections are on a measured hot path, I consider primitive arrays to reduce boxing; normal UI code favors clarity.”

## Deep-dive talking points

Discuss primitive versus reference, nullable wrapper, platform types, auto-unboxing, identity caching, and domain-boundary conversion.

## Follow-up questions

- Can Java `Integer` hold null? **Answer:** yes; it is a reference type, unlike primitive `int`.
- What is a Kotlin platform type? **Answer:** a Java-derived type with incomplete nullability information that can permit unsafe use unless validated.
- Why can wrapper `===` appear to work for small values? **Answer:** JVM boxed-value caching may reuse instances; identity is still the wrong numeric comparison.

## Self-check rubric

Describe both Java types, map them to Kotlin, handle a null wrapper, and explain identity versus value equality.

## References and reviewed-on date

- [Kotlin Java interoperability](https://kotlinlang.org/docs/java-interop.html) — primitive and boxed type mapping.
- [Kotlin numbers](https://kotlinlang.org/docs/numbers.html) — boxed number caching.
- [Java autoboxing tutorial](https://docs.oracle.com/javase/tutorial/java/data/autoboxing.html) — conversion mechanics.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. The SDK example is illustrative.
