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

الـ Boxing والـ Unboxing في Kotlin ومتى يؤثر بشكل ملحوظ على أداء الذاكرة (Allocation Performance):

1. ما هو الـ Boxing والـ Unboxing؟
   - **الـ Boxing (التغليف):** هو تحويل نوع أولي خفيف يعيش على الـ Stack (مثل `int` أو `long` البدائي) إلى كائن كلاس ثقيل في الـ Heap (مثل `java.lang.Integer` أو `java.lang.Long`).
   - **الـ Unboxing (فك التغليف):** هو استخراج القيمة الأولية من كائن الـ Wrapper.

2. ما هي تكلفة الـ Boxing في الذاكرة؟
   - الـ `int` البدائي يستغرق **4 Bytes** فقط على الـ Stack.
   - كائن الـ `Integer` المغلف يستغرق **16 إلى 24 Bytes** على الـ Heap (Object header + primitive value + memory padding) بالإضافة لمؤشر العنوان (4-8 bytes)!
   - زيادة استهلاك الذاكرة بأكثر من 400% لكل رقم، بالإضافة لضغط الـ GC عند حذفه!

3. متى يحدث الـ Boxing في Kotlin؟
   - **مع الـ Nullable Types (`Int?`):** الأنواع الأولية في الـ JVM لا تقبل `null`؛ لذلك `Int?` تُجبر المترجم على استخدام `java.lang.Integer` المغلف في الـ Heap.
   - **مع الـ Generic Collections (`List<Int>`, `Map<Int, String>`):** لأن الـ Java Generics تدعم الكائنات فقط، كل رقم داخل `List<Int>` هو كائن مغلف في الـ Heap!
   - **مع الـ Value Classes:** عندما تستخدم `@JvmInline value class` كـ Generic أو كـ Nullable.

4. متى يشكل ذلك خطراً على الأداء؟
   - في الـ Hot Loops، معالجة الصوت، الرسوميات، وقوائم البيانات الضخمة التي تحتوي على مئات الآلاف من الأرقام.

## Practical walkthrough

مقارنة عملية في استهلاك الذاكرة بين Boxing وبدائل الأداء:
```kotlin
// ❌ كود يسبب Boxing لملايين الكائنات في الـ Heap:
val numbers = ArrayList<Int>() // كل رقم هو Integer كائن في الـ Heap!
for (i in 0 until 1_000_000) {
    numbers.add(i) // 1,000,000 كائن في الـ Heap -> يستهلك حوالي 24MB!
}

// ✅ كود محسّن بدون أي Boxing (Primitives):
val primitiveNumbers = IntArray(1_000_000) // مصفوفة أرقام أولية contiguous memory
for (i in 0 until 1_000_000) {
    primitiveNumbers[i] = i // 0 objects allocated -> يستهلك 4MB فقط!
}
```
في أندرويد، نستخدم أيضاً مجموعات أولية مخصصة مثل `SparseIntArray` لتجنب الـ Boxing في الخرائط.

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

Boxing converts stack-allocated primitives (int) into heap-allocated wrapper objects (Integer), increasing memory consumption by 400% per value. It occurs when using nullable primitives (Int?), generic collections (List<Int>), or boxed value classes, degrading performance in hot loops and high-throughput data processing.

## Interview answer — structured

Boxing is the conversion of an unboxed primitive (like `int`, `long`, `boolean`) into its corresponding object wrapper (`java.lang.Integer`, `java.lang.Long`, `java.lang.Boolean`) on the heap. Unboxing is the inverse.

**Memory Cost**:
A bare `int` occupies strictly 4 bytes on the stack. An `Integer` wrapper on 64-bit Android requires an 8-12 byte object header, 4 bytes for the int value, and 4 bytes of memory alignment padding, consuming **16 to 24 bytes on the heap**, plus an object reference pointer. That represents a 4x to 6x memory overhead.

**When Boxing Occurs in Kotlin**:

1. **Nullable Primitives (`Int?`)**: The JVM primitives cannot represent `null`. Declaring `var age: Int? = null` forces ART to box the value as `java.lang.Integer` whenever non-null.
2. **Generic Collections (`List<Int>`, `Map<K, V>`)**: Because Java/Kotlin generics erase to `Object`, collections cannot store primitives directly, boxing every single element.
3. **Value Classes**: Using `@JvmInline value class` in generic or nullable positions.

**When It Matters**: For everyday business logic, boxing overhead is negligible. However, in hot execution loops (audio signal processing, game loops, image filtering, or processing collections with 100,000+ items), boxing allocates millions of short-lived objects, triggering severe GC churn and frame drops.

## Interview answer — deep senior

To eliminate boxing in performance-critical Android systems, we employ specialized primitive architectures:

1. **Primitive Arrays**: Use `IntArray`, `LongArray`, and `FloatArray` instead of `Array<Int>` or `List<Int>`. In bytecode, `IntArray` compiles to `int[]`, a single contiguous native memory block with zero object overhead per element.

2. **Android Sparse Arrays**: In collections mapping integer keys, replace `HashMap<Int, T>` with Android's **`SparseArray<T>`**, **`SparseIntArray`**, or **`SparseLongArray`**. These are binary-search backed array collections that avoid boxing both the integer keys and values, reducing memory consumption by over 50%.

3. **Fast Primitive Collections**: For high-throughput graphics or math, libraries like HPPC (High Performance Primitive Collections) provide primitive-specialized sets and maps.

## How to answer in the interview

- **Why:** Explain representation at generic and nullable boundaries.
- **How:** Profile allocated bytes in the actual hot loop.
- **Trade-off:** Primitive arrays save memory with less ergonomic APIs.
- **Failure case:** Null `Integer` can crash during unboxing.
- **Production solution:** Use dense primitives only where measured volume warrants it.

## Deep-dive talking points

Discuss JVM representation, generic erasure, `IntArray`, null unboxing, numeric equality, and allocation profiling.

## Follow-up questions

- **Interviewer:** "Why does Kotlin cache small Integer boxes?"
  **Answer:** "Like Java, ART caches boxed `Integer` instances in an `IntegerCache` between -128 and 127. Values in this range reuse cached singleton objects without allocating new heap instances."

- **Interviewer:** "What is the difference between `Array<Int>` and `IntArray` in Kotlin?"
  **Answer:** "`Array<Int>` compiles to `java.lang.Integer[]` (an array of object pointers, boxing every integer). `IntArray` compiles to `int[]` (a flat array of raw 32-bit primitives with zero boxing)."

- **Interviewer:** "Does using `var x: Int = 10` ever box if not nullable?"
  **Answer:** "No. When declared as a non-null local variable or non-generic property, the Kotlin compiler compiles `Int` strictly to the primitive `int` bytecode instruction."

## Self-check rubric

Identify two boxing boundaries, a null failure, a primitive-array alternative, and a measurement that justifies optimization.

## References and reviewed-on date

- [Kotlin numbers](https://kotlinlang.org/docs/numbers.html) — JVM boxing and caching.
- [Kotlin arrays](https://kotlinlang.org/docs/arrays.html) — primitive arrays.
- [Java interoperability](https://kotlinlang.org/docs/java-interop.html) — primitive and wrapper mapping.

Technically reviewed against primary documentation on 2026-10-13.
