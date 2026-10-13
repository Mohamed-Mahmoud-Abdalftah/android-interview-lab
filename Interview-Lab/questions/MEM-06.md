---
id: "MEM-06"
question: "What causes boxing/unboxing, and when does it matter?"
topic: "Memory Management, ANR & Performance"
code: "MEM"
group: "A"
phase: 1
priority: "P1"
order: 61
editorial_status: "reviewed"
---

# MEM-06

## Original interview question

What causes boxing/unboxing, and when does it matter?

## What the interviewer evaluates

- Identify primitive-to-wrapper conversion at nullable and generic JVM boundaries.
- Explain allocation, null-unboxing, equality, and profile-driven optimization.
- Choose primitive arrays for large numerical workloads without over-optimizing ordinary UI code.

## Explanation in Arabic

في JVM، `Int` غير nullable غالبًا يتمثل كـprimitive `int`، لكن `Int?` أو `List<Int>` يحتاجوا boxed `Integer` لأن generic collection تخزن references. التحويل من primitive إلى wrapper هو boxing والعكس unboxing. ده مهم في loop رقمية كبيرة لأن wrappers قد تزود allocations وGC، ومهم في Java interop لأن `Integer` ممكن يكون null وunboxing له يعمل `NullPointerException`. المقارنة بالقيمة `==` آمنة للمعنى المعتاد؛ لا تعتمد على `===` للـboxed numbers لأن caching يغير referential equality.

## Practical walkthrough

في sensor stream فيه ملايين العينات، `MutableList<Int>` قد تعمل wrappers كتير، بينما `IntArray` يخزن قيم كثيفة. لكن في شاشة فيها عشر أسعار، فرق الأداء غالبًا مش ملموس. اعمل allocation recording للـhot path وشوف count وbytes وGC pauses، ثم بدّل representation فقط لو الفرق واضح. عند Java boundary، `Integer` nullable؛ unboxing بدون check ممكن يوقع التطبيق حتى لو benchmark سريع.

## Why it matters and how it works

Java collections and nullable values require object representations, whereas primitive arrays such as Kotlin `IntArray` store primitive elements on the JVM. Autoboxing is often invisible in source code. The compiler/runtime may optimize some allocations, so measure the hot path rather than assuming each expression creates an object. Unboxing a null wrapper is a correctness failure independent of performance.

## Worked example

For a sensor histogram with millions of integer samples, `IntArray(sampleCount)` avoids the per-element wrappers of `MutableList<Int>`. For ordinary screen labels, `List<Int>` is usually clearer and performance may be irrelevant. If Java returns `Integer?`, check for null before arithmetic: `val count = javaCounter ?: 0`. This Kotlin snippet assumes an appropriately nullable interop boundary.

For a high-volume numeric path, this is a standalone Kotlin sketch. `samples` and `binCount` come from a validated sensor pipeline; measure allocation rate before adopting it.

```kotlin
fun histogram(samples: IntArray, binCount: Int): IntArray {
    require(binCount > 0)
    val counts = IntArray(binCount)
    for (sample in samples) {
        if (sample in 0 until binCount) counts[sample]++
    }
    return counts
}
```

The array avoids one boxed object per stored count; it does not solve unbounded input size.

## Trade-offs and decision criteria

Primitive arrays reduce memory and boxing in dense numeric loops but have a less flexible API and fixed size. Generic collections support easier transformations and mixed ownership. Optimize only after allocation profiling and a representative workload. Never use identity equality as a shortcut for numeric value equality.

## Failure modes

Unboxing null crashes. Repeated boxing in a frame-time loop can produce GC pressure. Relying on small-integer caching makes `===` appear to work in tests but fail for other values. A premature switch to arrays can complicate code with no measurable gain.

## Production perspective

Profile a high-frequency telemetry aggregation on target devices. Compare allocation count, CPU, and frame behavior using `List<Int>` and `IntArray`; keep the simpler version if there is no material improvement. At Java boundaries, make nullability explicit and test a null result.

## Interview answer — short

“Boxing wraps a primitive as an object, often at nullable or generic collection boundaries; unboxing extracts it. It matters in large hot loops and when a Java wrapper may be null.”

## Interview answer — structured

“On the JVM a non-null Kotlin `Int` can usually use primitive `int`, but `Int?` and generic `List<Int>` need boxed values. That creates potential allocation and GC pressure in large numerical workloads. `IntArray` avoids per-element boxing when a dense primitive array fits. Java `Integer` can also be null, so unboxing without a check may crash. I use value equality and profile before optimizing a normal UI collection.”

## Interview answer — deep senior

“I look for boxing at representation boundaries rather than treating it as a property of every Kotlin integer. JVM generics and nullable numeric values commonly require wrapper objects; primitive arrays keep dense values unboxed. In a high-frequency computation, many wrappers can increase memory traffic and GC work, but compiler optimizations mean I verify with allocation profiling. Correctness is just as important: a platform or nullable `Integer` from Java must be checked before unboxing, and boxed referential equality can vary because of caching. I prefer `IntArray` for a measured numeric hot path, retain collections where clarity matters, and benchmark with realistic input sizes and device constraints. For a sensor histogram, I compare `MutableList<Int>` with `IntArray` using production-sized samples and allocated bytes per update, not an abstract microbenchmark. The primitive array may improve memory density but requires explicit indexing and conversion at API boundaries. I would keep a clear collection in a low-volume screen.”

## How to answer in the interview

- **Why:** Explain representation at generic and nullable boundaries.
- **How:** Profile allocated bytes in the actual hot loop.
- **Trade-off:** Primitive arrays save memory with less ergonomic APIs.
- **Failure case:** Null `Integer` can crash during unboxing.
- **Production solution:** Use dense primitives only where measured volume warrants it.

## Deep-dive talking points

Discuss JVM representation, generic erasure, `IntArray`, null unboxing, numeric equality, and allocation profiling.

## Follow-up questions

- Why can `List<Int>` allocate wrappers? **Answer:** JVM generic collections hold object references, while `IntArray` has primitive elements.
- What happens when Java returns null for `Integer` and Kotlin unboxes it? **Answer:** arithmetic or assignment to a non-null primitive path can fail with a null-related exception.
- Is `===` reliable for boxed numeric equality? **Answer:** no; caching can make some values share an instance while others do not.

## Self-check rubric

Identify two boxing boundaries, a null failure, a primitive-array alternative, and a measurement that justifies optimization.

## References and reviewed-on date

- [Kotlin numbers](https://kotlinlang.org/docs/numbers.html) — JVM boxing and caching.
- [Kotlin arrays](https://kotlinlang.org/docs/arrays.html) — primitive arrays.
- [Java interoperability](https://kotlinlang.org/docs/java-interop.html) — primitive and wrapper mapping.

Technically reviewed against these primary sources on 2026-10-13 by automated editorial review. The performance comparison is proposed, not measured.
