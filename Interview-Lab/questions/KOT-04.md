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

In Kotlin, == checks structural equality by calling equals() with safe null checks under the hood, whereas === checks referential identity, determining whether two references point to the exact same object in heap memory. For data classes, == compares primary constructor properties, while === compares memory addresses.

## Interview answer — structured

In Kotlin, == represents structural equality, while === represents referential identity.

When you write a == b, the compiler translates this into a safe call to equals(): it checks if either operand is null first, preventing NullPointerExceptions automatically. In data classes, equals() is generated for you to compare all primary constructor properties.

On the other hand, === checks whether two references point to the exact same instance in heap memory, compiling down to an acmp bytecode instruction on the JVM.

In Android, we rely on this distinction heavily in places like DiffUtil or Compose recomposition. For example, in DiffUtil, areItemsTheSame checks if unique IDs match, while areContentsTheSame uses == to check if property values changed. Using === for content comparison would trigger unnecessary UI redraws whenever new immutable instances are emitted from a repository.

## Interview answer — deep senior

Structural equality (==) and referential identity (===) differ in both intent and bytecode compilation. When compiling ==, Kotlin emits a call to Intrinsics.areEqual(a, b), which handles null checks before invoking equals(). For primitives, == maps directly to JVM primitive comparison instructions unless they are boxed into nullable types or generics.

A subtle pitfall arises with boxed primitives due to JVM Integer caching. Integers between -128 and 127 are cached by the JVM runtime. Comparing two boxed Int? values like 100 with === returns true because they share the cached instance. But comparing two boxed Int? values of 1000 with === evaluates to false because they are distinct heap allocations. This is why you must never rely on === for value types.

Another nuance is floating-point equality. IEEE 754 states that Float.NaN == Float.NaN is false. However, Kotlin adheres to total order equality when floats are statically typed as Any, boxed in collections, or compared in equals(): in that context, NaN equals NaN, and -0.0 is considered less than 0.0. In production, we override equals() and hashCode() carefully in custom classes, ensure consistency with data classes, and avoid === outside of performance caches or identity maps.

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
