---
id: "KOT-04"
question: "What is the difference between == and ===?"
topic: "Kotlin Core & Advanced"
code: "KOT"
group: "A"
phase: 1
priority: "P1"
order: 4
editorial_status: "reviewed"
---

# KOT-04

## Original interview question

What is the difference between == and ===?

## What the interviewer evaluates

Distinguish structural equality from referential identity and know how equality contracts affect state and collections.

## Concept and technical explanation

In Kotlin, equality evaluation is explicitly split between structural equality, expressed via the double-equals operator (==), and referential identity, expressed via the triple-equals operator (===).

Structural equality evaluates whether two separate objects possess equivalent state or content according to their implementation of equals(). When kotlinc compiles the == operator, it transforms the expression into a null-safe equals invocation: a?.equals(b) ?: (b === null). This protects developers from NullPointerExceptions if the left-hand operand is null. In contrast, referential identity (===) evaluates whether two reference variables point to the exact same physical memory address on the JVM heap. For primitive types mapped to JVM primitives (such as Int or Long), both == and === compare raw numeric values, whereas for boxed primitives or objects, === strictly compares heap references.

## Practical walkthrough (English)

Consider implementing list diffing in an Android RecyclerView using DiffUtil:

Failure Scenario — Misusing Referential Identity in Content Comparisons:
```kotlin
data class TransactionItem(val id: String, val amount: Double)

class TransactionDiffCallback : DiffUtil.ItemCallback<TransactionItem>() {
    override fun areItemsTheSame(oldItem: TransactionItem, newItem: TransactionItem): Boolean {
        return oldItem.id == newItem.id // Correct identity comparison
    }

    override fun areContentsTheSame(oldItem: TransactionItem, newItem: TransactionItem): Boolean {
        // Bug: Misusing referential equality!
        return oldItem === newItem 
    }
}
```
Because the repository produces fresh immutable data class instances whenever an update arrives, oldItem === newItem always evaluates to false, even when properties are identical. This forces redundant item animations and breaks UI diffing optimizations.

Production Architecture — Correct Equality Separation:
Use structural equality for content verification, ensuring efficient re-rendering:
```kotlin
class TransactionDiffCallback : DiffUtil.ItemCallback<TransactionItem>() {
    override fun areItemsTheSame(oldItem: TransactionItem, newItem: TransactionItem): Boolean {
        return oldItem.id == newItem.id
    }

    override fun areContentsTheSame(oldItem: TransactionItem, newItem: TransactionItem): Boolean {
        return oldItem == newItem // Correctly invokes generated data class equals()
    }
}
```

Bytecode Decompilation Verification:
Decompiling a == b reveals the synthetic null-safe expansion emitted by kotlinc:
```java
Intrinsics.areEqual(a, b);
```
Where Intrinsics.areEqual executes:
```java
public static boolean areEqual(Object first, Object second) {
    return first == null ? second == null : first.equals(second);
}
```
Meanwhile, a === b compiles directly to Java's reference equality bytecode instruction: if_acmpeq.

## Explanation in Arabic

الفرق بين == و === في Kotlin هو الفرق بين المحتوى (Structural Equality) و الهوية في الذاكرة (Referential Identity).

المساواة الهيكلية (==) بتتحول مباشرة لاستدعاء دالة equals() مع فحص null آمن تحت الغطاء (a?.equals(b) ?: (b === null)). ده معناه إنه مستحيل يضرب NullPointerException لو الطرف الشمال null. في data class، الـ equals() بتتولد تلقائياً لتقارن كل القيم الموجودة في الـ Primary Constructor.

المساواة المرجعية (===) بتقارن هل المتغيرين بيشاوروا على نفس الـ Address تماماً في الـ Heap، وده بيترجم لـ acmp instruction في الـ JVM bytecode.

انتبه لفخ الـ Integer Caching: الأرقام من -128 لـ 127 بتتعمل لها Cache في الـ JVM، فلو قارنت 100 مع 100 بـ === هترجع true، لكن لو قارنت 1000 مع 1000 بـ === هترجع false لأن كل واحد اتعمل له Box في كائن مستقل في الـ Heap!

## Practical walkthrough

في DiffUtil في RecyclerView:
- areItemsTheSame بتستخدم == لمقارنة الـ unique ID (oldItem.id == newItem.id) لتحديد هوية العنصر.
- areContentsTheSame بتستخدم == لمقارنة محتويات الـ data class بالكامل (oldItem == newItem).
- لو استخدمت === بالغلط في areContentsTheSame، كل ما الـ Repository يرجع New Immutable Instance لنفس البيانات، DiffUtil هيفتكر إن البيانات اتغيرت وهيعيد رسم العنصر بالكامل بدون داعي.

## Why it matters and how it works

Choosing the wrong equality changes map keys, deduplication, and UI state emissions. `==` expands to a null-safe equals check; `===` is identity comparison. `equals` must remain stable for objects used as hash keys, so mutable equality fields are dangerous.

## Worked example

Runnable JVM example with two equal but distinct values.
```kotlin
data class UserId(val value: String)
fun main() {
    val a = UserId("42")
    val b = UserId("42")
    println(a == b)  // true: equals
    println(a === b) // false: distinct instances
}
```

## Trade-offs and decision criteria

Value comparison is correct for domain values and immutable UI snapshots. Identity checks can be useful for a specific cache or lifecycle object but should not stand in for business equality. Deep array comparisons are explicit and may cost proportional time.

## Failure modes

Putting a mutable data-class key into `HashMap` then changing an equality field can make lookup fail. Use immutable keys. Do not use `===` to decide whether two server responses are semantically identical; deserialization creates fresh instances.

## Production perspective

An offline cache keys records by immutable `UserId(value)`, so equivalent IDs match across deserialization. A ViewModel publishes immutable state; equality-based suppression is meaningful only when its `equals` contract describes the displayed data.

## Interview answer — short

In Kotlin, the double-equals operator (==) checks structural equality by invoking equals() in a null-safe manner, comparing object content. The triple-equals operator (===) checks referential equality, evaluating whether two references point to the identical heap address. For primitive types, both operators compare values. In Android architectures like DiffUtil or Compose state, structural equality determines whether UI components must re-render.

## Interview answer — structured

Kotlin makes a clear syntactic distinction between object content comparison and physical memory identity. The double-equals operator checks structural equality, translating under the hood to a null-safe invocation of the equals method. In contrast, the triple-equals operator evaluates referential equality, checking whether two pointers address the exact same instance on the heap.

This separation prevents unexpected crashes. In Java, writing double equals on objects checks reference identity and comparing with null can easily cause bugs. Kotlin guarantees that double equals safely handles null operands on either side, making content comparison the default and natural choice for domain entities and data classes.

In production, selecting the wrong operator distorts UI diffing algorithms and caching contracts. In RecyclerView DiffUtil or Jetpack Compose state comparisons, using triple equals causes unnecessary re-renders because immutable state updaters produce fresh instances with identical contents.

Senior engineers use double equals for domain and UI state comparisons, reserving triple equals for specialized object pooling, singleton identity checks, or performance-sensitive reference guards.


## Interview answer — deep senior

At the bytecode level, kotlinc translates the structural equality operator (==) into an invokestatic call to Intrinsics.areEqual(Object a, Object b). This utility method checks if the first reference is null; if so, it evaluates whether the second reference is null, and otherwise invokes invokevirtual on Object.equals(). This eliminates any possibility of a NullPointerException when the left-hand operand is null. When comparing custom classes, structural equality relies completely on a well-behaved equals and hashCode implementation, which Kotlin data classes synthesize automatically.

Conversely, the referential equality operator (===) maps directly to the JVM bytecode instruction if_acmpeq (or if_acmpne for inequality). This instruction pops two object references from the operand stack and compares their raw memory pointers directly, without calling any methods.

A critical nuance occurs when dealing with JVM primitive wrapping and autoboxing. When using primitive types like Int, the Kotlin compiler optimizes them to JVM primitive int, where both == and === emit integer comparison instructions like if_icmpeq. However, when an Int is cast to Any or declared as a nullable Int?, the compiler forces autoboxing via java.lang.Integer.valueOf(). In this boxed scenario, the JVM Integer cache applies to values between -128 and 127. Consequently, two boxed integers with value 100 evaluate to true for both == and ===, whereas two boxed integers with value 1000 evaluate to true for == but false for === due to distinct heap allocations.

In large-scale Android development, understanding this distinction is crucial for reactive performance. Jetpack Compose and StateFlow distinctUntilChanged operators rely heavily on structural equality (==) to suppress redundant UI recompositions. If an engineer breaks the equals contract or inadvertently relies on reference identity, the UI pipeline will suffer from frame drops and spurious layout recalculations.

## How to answer in the interview

- **Why:** Differentiate structural equality (`equals()`) from referential identity (`===`).
- **How:** Use `==` for comparing data contents (which compiles to `equals()` with null safety) and `===` to check whether references point to the exact same memory address.
- **Trade-offs:** Overriding `equals()` requires implementing `hashCode()` consistently; neglecting this breaks hash-based collections like `HashSet` and `HashMap`.
- **Failure cases:** Using `===` on boxed primitives or value objects where instances differ in memory, causing identity checks to fail unexpectedly.
- **Production solution:** Rely on data classes for automatic `equals`/`hashCode` generation, and restrict `===` to performance caches or singleton identity checks.

## Deep-dive talking points

Discuss generated data-class equality, `hashCode` consistency, arrays, mutable keys, and equality-based conflation in `StateFlow`.

## Follow-up questions

- **Interviewer:** "How does Kotlin's == prevent a NullPointerException if the left-hand variable is null?"
  **Answer:** "The compiler translates a == b into a?.equals(b) ?: (b === null). If a is null, it checks whether b is also null. If both are null, it evaluates to true; if only one is null, it evaluates to false. Neither path can trigger a NullPointerException."

- [KOT-05](../kot-05/): **Interviewer:** "If two data class instances have different values in properties declared in the class body, does == evaluate to true?"
  **Answer:** "Yes! Kotlin only generates equals(), hashCode(), and toString() using properties declared in the primary constructor. Properties declared in the class body are completely ignored by generated equality. If two instances have identical constructor fields but different body fields, == will still return true."

- **Interviewer:** "Why is Float.NaN == Float.NaN false, but in a Set<Float> it's treated as equal?"
  **Answer:** "When evaluated directly as primitive floats, Kotlin follows IEEE 754 specifications where NaN is not equal to anything, including itself. But when floats are boxed into a collection like a Set or compared through equals(), Kotlin applies total ordering so that hash tables and sets work deterministically. Under total ordering, NaN equals NaN."

## Self-check rubric

Predict both operators for two equal data-class instances, explain array comparison, and name a mutable-key failure.

## References and reviewed-on date

- [Kotlin equality](https://kotlinlang.org/docs/equality.html) — structural and referential equality.
- [Kotlin data classes](https://kotlinlang.org/docs/data-classes.html) — generated equality.

Technically reviewed against primary documentation on 2026-10-13.
