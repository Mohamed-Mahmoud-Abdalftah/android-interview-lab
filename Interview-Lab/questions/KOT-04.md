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

`==` في Kotlin بيقارن structural equality عبر `equals` بشكل null-safe؛ `===` بيتأكد إن الاتنين نفس object reference. `data class` بتولّد `equals` من properties في الـprimary constructor، فنسختين بنفس القيم ممكن يكونوا `==` true و`===` false. للـUI state غالبًا يهمنا تساوي المحتوى. للـidentity-sensitive caching أحيانًا يهم reference، لكن لازم سبب صريح. Arrays لها خصوصية: `==` لا يقارن العناصر عنصر بعنصر؛ استخدم `contentEquals` أو `contentDeepEquals` حسب البنية.

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

## Practical walkthrough

لما تقارن `UserId("42")` من cache مع نسخة جاية من network، `==` بتسأل هل القيمة متساوية حسب `equals`؛ الـdata class بيولّدها من constructor properties. `===` بتسأل هل الاتنين نفس object في الذاكرة. في deduplication وstate comparison غالبًا المطلوب value equality، لكن راجع `equals`: regular class افتراضيًا reference equality، وarray جوه data class مساواتها مش content equality تلقائيًا. ما تبنيش business rule على identity إلا لو هي نفسها المطلوب زي tracking لنفس instance.

## Trade-offs and decision criteria

Value comparison is correct for domain values and immutable UI snapshots. Identity checks can be useful for a specific cache or lifecycle object but should not stand in for business equality. Deep array comparisons are explicit and may cost proportional time.

## Failure modes

Putting a mutable data-class key into `HashMap` then changing an equality field can make lookup fail. Use immutable keys. Do not use `===` to decide whether two server responses are semantically identical; deserialization creates fresh instances.

## Production perspective

An offline cache keys records by immutable `UserId(value)`, so equivalent IDs match across deserialization. A ViewModel publishes immutable state; equality-based suppression is meaningful only when its `equals` contract describes the displayed data.

## Interview answer — short

`==` checks structural equality through `equals`, with null-safe behavior. `===` checks reference identity. For domain IDs I want value equality, so I check the type’s `equals` contract rather than assuming two equal-looking objects compare equal.

## Interview answer — structured

In Kotlin, `a == b` is the null-safe way to call the equality contract; `a === b` asks whether the references identify the same object. A data class generates equality from its primary constructor properties, while a regular class inherits identity-based equality unless it overrides `equals`. In a cache I compare stable IDs by value, not by whether network and database returned the same instance. I also review nested arrays or mutable fields, because their equality and mutation can surprise state diffing. I use `===` only when instance identity itself is the requirement.

## Interview answer — deep senior

I would inspect the type’s equality contract before choosing an operator. A regular class inherits reference-based `equals` unless overridden; a data class generates value equality for primary-constructor properties. A mutable property participating in equality is risky for hash collections. `===` bypasses that semantic contract and can be appropriate for a specific singleton or cache identity check. On Android, equality in state streams can suppress updates, so mutable nested models and array properties need special care. I usually start by asking what the domain considers the same value. Kotlin's `==` calls `equals` safely around nulls, so it reflects that type's semantic equality.

A concrete failure is using a data class containing a mutable array as a key in a hash map. The generated equality delegates to the property equality contract, and mutation or array reference equality may surprise the caller. In UI state, equality can also determine whether an update is emitted or rendered; mutating a nested model in place may leave an apparently equal state. I would define stable value objects, avoid mutable equality fields, and test two independently loaded instances. I use identity checks when I truly need to know whether a cache returned the exact same object, never as a substitute for domain equality.

## How to answer in the interview

- **Why:** Differentiate structural equality (`equals()`) from referential identity (`===`).
- **How:** Use `==` for comparing data contents (which compiles to `equals()` with null safety) and `===` to check whether references point to the exact same memory address.
- **Trade-offs:** Overriding `equals()` requires implementing `hashCode()` consistently; neglecting this breaks hash-based collections like `HashSet` and `HashMap`.
- **Failure cases:** Using `===` on boxed primitives or value objects where instances differ in memory, causing identity checks to fail unexpectedly.
- **Production solution:** Rely on data classes for automatic `equals`/`hashCode` generation, and restrict `===` to performance caches or singleton identity checks.

## Deep-dive talking points

Discuss generated data-class equality, `hashCode` consistency, arrays, mutable keys, and equality-based conflation in `StateFlow`.

## Follow-up questions

- [KOT-05](../kot-05/): Which data-class fields contribute to generated equality? **Answer:** primary-constructor properties, not body-only properties.
- [FLO-06](../flo-06/): Why can equality suppress a state emission? **Answer:** `StateFlow` conflates updates using `equals`.

## Self-check rubric

Predict both operators for two equal data-class instances, explain array comparison, and name a mutable-key failure.

## References and reviewed-on date

- [Kotlin equality](https://kotlinlang.org/docs/equality.html) — structural and referential equality.
- [Kotlin data classes](https://kotlinlang.org/docs/data-classes.html) — generated equality.

Technically reviewed against the linked primary documentation on 2026-10-13. Examples are illustrative JVM snippets; no Android device claim is made.
