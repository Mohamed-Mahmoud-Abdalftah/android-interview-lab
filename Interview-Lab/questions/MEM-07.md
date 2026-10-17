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

## Concept and technical explanation

The distinction between int and java.lang.Integer is a foundational aspect of Java and Kotlin interoperability. In Java, int is a primitive value type that represents a 32-bit signed integer stored by value directly on thread stack frames or embedded within class memory layouts. It has zero object overhead and can never hold a null reference. In contrast, java.lang.Integer is a full reference type that wraps an int inside an object allocated on the heap, allowing it to represent null and participate in generic collections. In Kotlin, this duality is abstracted into the unified Int type. Non-nullable Int compiles directly to primitive int in bytecode, whereas nullable Int? or generic T compiles to java.lang.Integer. When interoperating with Java APIs that lack nullability annotations, Kotlin treats types as platform types (Int!), creating potential unboxing crashes if null is received.

## Practical walkthrough (English)

Java interoperability pitfalls with primitives and wrappers:
```kotlin
// Java API signature:
// public class LegacyAnalytics {
//     public static Integer getScoreOrNull();
//     public static void trackMetric(int count);
// }

// Kotlin caller:
fun processAnalytics() {
    // Platform type pitfall: getScoreOrNull() returns Integer!
    val score: Int = LegacyAnalytics.getScoreOrNull() // If null, throws NullPointerException at runtime during unboxing!

    // Safe handling:
    val safeScore: Int? = LegacyAnalytics.getScoreOrNull()
    if (safeScore != null) {
        LegacyAnalytics.trackMetric(safeScore) // Automatic safe unboxing to primitive int
    }
}
```
By explicitly typing the returned platform type as Int?, the Kotlin compiler enforces null-safety checks before unboxing to primitive int, preventing unexpected application crashes.

## Explanation in Arabic

الفرق بين النوعين الأوليين `int` و `Integer` والتعامل بين Kotlin و Java على مستوى الذاكرة والأداء:

1. كيف يترجم كود Kotlin إلى بايت كود JVM؟
   - في Kotlin، النوع `Int` غير القابل للعدم (`Int`) يترجم دائماً في البايت كود إلى `int` بدائي (primitive) على الـ JVM، ولا يستهلك سوى 4 بايت مباشرة في الـ Stack أو كـ field داخل الكائن.
   - أما إذا كان نوعه يقبل العدم `Int?`، فيجب على المترجم تمثيل القيمة كـ Reference Object وهو `java.lang.Integer` (Boxed)، لأنه لا يمكن وضع `null` داخل `int` بدائي.

2. كلفة الـ Object Overhead في `Integer`:
   - الـ `int` البدائي: 4 بايت فقط.
   - الـ `Integer` المُغلّف (Boxed Object): يحتوي على Object Header (عادة 12 بايت) + الـ value (4 بايت) + Padding للمحاذاة على 8 بايت = 16 إلى 24 بايت على الـ Heap، بالإضافة إلى 4-8 بايت لعنوان الإشارة (Pointer Reference) إليه!
   - هذا يعني زيادة في الذاكرة بنسبة 400% إلى 600% لكل رقم، بالإضافة إلى Memory Churn وضغط على الـ Garbage Collector.

3. الـ Autoboxing في الحلقات والمجموعات (Collections):
   - استخدام `List<Int>` في Kotlin يترجم إلى `java.util.List<Integer>`، مما يجبر كل عنصر على أن يكون مغلفاً في كائن `Integer` على الـ Heap.
   - في المعالجات الحسابية الثقيلة أو قوائم الإحداثيات والرسوم، يُفضل دائماً استخدام المصفوفات البدائية: `IntArray` بدلاً من `Array<Int>` أو `List<Int>`.

## Practical walkthrough

مقارنة عملية تظهر تأثير التغليف (Boxing) على الذاكرة وسرعة المعالجة:
```kotlin
// ❌ كود سيء: يسبب Autoboxing مستمر لكل عنصر في القائمة، مهدراً الذاكرة ومسبباً GC Churn:
fun calculateSum(numbers: List<Int>): Long { // List<Int> تخزن كائنات java.lang.Integer
    var total: Long = 0L
    for (num in numbers) { // Unboxing من Integer إلى int في كل دورة
        total += num
    }
    return total
}

// ✅ كود احترافي: استخدام Primitive Array بدون أي Heap Allocation لكل رقم:
fun calculateSumFast(numbers: IntArray): Long { // يترجم مباشرة إلى int[] في الـ JVM
    var total: Long = 0L
    for (num in numbers) { // قراءة مباشرة من الذاكرة المتتالية بدون فك تغليف
        total += num
    }
    return total
}
```

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

In Java, primitive int is a 4-byte non-nullable value type, while Integer is a nullable heap object wrapper. Kotlin unifies both under Int, mapping non-nullable Int to primitive int and nullable Int? or generics to Integer. When calling unannotated Java APIs, Kotlin creates platform types (Int!), which cause fatal NullPointerExceptions if unboxed without explicit null checks.

## Interview answer — structured

The difference between int and Integer stems from Java's split type system between primitives and reference objects. A primitive int stores a raw 32-bit value directly in memory without object headers, offering maximum CPU execution speed and zero heap overhead, but cannot represent the absence of a value. Conversely, java.lang.Integer is a heap-allocated wrapper object that supports nullability and generic typing.

Kotlin eliminates this syntactical duality by exposing a single Int type. Under the hood, the Kotlin compiler maps non-nullable Int to primitive int, while mapping nullable Int? and generic parameters to java.lang.Integer.

In production, interoperability issues arise when interfacing with legacy Java code lacking JSR-305 nullability annotations. In these cases, Kotlin infers platform types, and attempting to treat a null Integer as a non-nullable primitive triggers an immediate NullPointerException during implicit unboxing.

Senior engineers always specify explicit nullability on Java integration boundaries to prevent unboxing crashes.


## Interview answer — deep senior

Delving into ART bytecode compilation and JNI bridge mechanics, the translation between Kotlin and Java reveals critical architectural trade-offs. When decompiling Kotlin bytecode, a non-nullable Int declaration compiles directly to JVM opcode instructions such as ILOAD, ISTORE, and IADD. However, as soon as nullability is introduced with Int?, the compiler synthesizes method calls to Integer.valueOf(int) for boxing and Integer.intValue() for unboxing. In addition to the memory inflation—where a 64-bit ART runtime incurs 16 bytes for each Integer instance compared to 4 bytes for primitive int—reference identity comparison presents subtle correctness traps. Java caches Integer instances within the range of -128 to 127 via IntegerCache. Comparing two Integer references with the referential equality operator inside this range evaluates to true due to cached identity, but identical values outside this range evaluate to false unless using structural equals().

At the JNI and native boundary, this distinction dictates performance. Passing a primitive int array across the JNI bridge allows the native runtime to use GetPrimitiveArrayCritical to pin the underlying memory buffer, enabling zero-copy pointer access in C++ without garbage collector interference. In contrast, passing an array of Integer objects requires traversing individual object pointers, creating immense JNI crossing overhead and preventing vectorization. In large-scale Android applications, staff engineers enforce NonNull and Nullable annotations across all Java libraries and utilize primitive arrays for high-throughput data models to ensure safe, zero-overhead Java-Kotlin interoperability.

## How to answer in the interview

- **Why:** Distinguish primitive value from nullable wrapper.
- **How:** Normalize the Java SDK result in one adapter.
- **Trade-off:** Defaulting null is convenient but may hide protocol errors.
- **Failure case:** Unboxing a null platform type causes a crash.
- **Production solution:** Test absence explicitly and document the chosen domain meaning.

## Deep-dive talking points

Discuss primitive versus reference, nullable wrapper, platform types, auto-unboxing, identity caching, and domain-boundary conversion.

## Follow-up questions

- **Interviewer:** "What happens if a Java method returns `Integer` and is assigned to a non-nullable Kotlin `Int`?"
  **Answer:** "The compiler accepts it as a platform type `Int!`. If the Java method returns null, unboxing it into Kotlin's primitive `int` invokes `intValue()`, which instantly throws a `NullPointerException`. We always annotate Java boundaries with `@NonNull` or type it explicitly as `Int?` in Kotlin."

- **Interviewer:** "Why does `IntArray` not box elements while `Array<Int>` does?"
  **Answer:** "`IntArray` compiles directly to JVM bytecode primitive array `int[]`, storing contiguous 4-byte values. In contrast, `Array<Int>` compiles to `Integer[]`, which is an array of object pointers pointing to separate `Integer` instances on the heap."

## Self-check rubric

Describe both Java types, map them to Kotlin, handle a null wrapper, and explain identity versus value equality.

## References and reviewed-on date

- [Kotlin Java interoperability](https://kotlinlang.org/docs/java-interop.html) — primitive and boxed type mapping.
- [Kotlin numbers](https://kotlinlang.org/docs/numbers.html) — boxed number caching.
- [Java autoboxing tutorial](https://docs.oracle.com/javase/tutorial/java/data/autoboxing.html) — conversion mechanics.

Technically reviewed against primary documentation on 2026-10-13.
