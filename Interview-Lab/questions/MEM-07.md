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

In Kotlin, a non-nullable `Int` compiles to JVM primitive `int` (4 bytes on the stack), whereas nullable `Int?` or generic collections like `List<Int>` compile to boxed `java.lang.Integer` (16-24 bytes on the heap). Boxed integers multiply memory footprint and cause GC churn, so high-performance paths should use `IntArray` or primitive-specialized collections.

## Interview answer — structured

Under the hood, Kotlin does not expose primitives directly in syntax, but its compiler maps them intelligently based on nullability and generics.

A standard non-nullable `Int` compiles directly to a primitive `int` on JVM bytecode, occupying just 4 bytes of contiguous memory with zero object overhead. However, when an `Int` is marked nullable (`Int?`) or used as a type argument in standard generics like `List<Int>`, the runtime must represent it as a boxed reference: `java.lang.Integer`.

The memory impact is drastic: while a primitive `int` requires 4 bytes, a `java.lang.Integer` requires a 12-byte object header, 4 bytes of value payload, and 8-byte alignment padding, consuming 16 to 24 bytes on the heap, plus 4 to 8 bytes for the reference pointer. In high-frequency loops or graphics/sensor processing, this creates massive memory bloat and garbage collection churn. In production, we mitigate this by using primitive arrays like `IntArray` instead of `Array<Int>`, or specialized Android collections like `SparseIntArray` to avoid boxing entirely.


## Interview answer — deep senior

Java interoperability introduces subtle boxing pitfalls. If a Kotlin function expects `Int` and calls a Java method returning `Integer`, or vice-versa with platform types (`Integer!`), implicit boxing and unboxing occur at bytecode boundaries (`Integer.valueOf()` and `intValue()`). Furthermore, unboxing a null `Integer` returned from Java produces a fatal `NullPointerException` at runtime in Kotlin.

Another critical JVM optimization to understand is the **Integer Cache** (`java.lang.IntegerCache`), which caches boxed values between -128 and 127 by default. Comparing boxed integers inside this range with reference equality (`===`) might deceptively evaluate to `true`, but comparing values outside this range fails because distinct instances are allocated on the heap.

When profiling memory in Android Studio, collections of boxed primitives appear as massive retained sizes dominated by millions of tiny `java.lang.Integer` instances. Replacing `Map<Int, CustomObject>` with Android's `SparseArray<CustomObject>` eliminates the `Integer` key boxing completely, saving megabytes of heap in large list adapters or cache layers.


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
