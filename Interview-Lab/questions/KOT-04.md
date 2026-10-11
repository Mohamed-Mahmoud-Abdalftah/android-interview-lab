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

## Trade-offs and decision criteria

Value comparison is correct for domain values and immutable UI snapshots. Identity checks can be useful for a specific cache or lifecycle object but should not stand in for business equality. Deep array comparisons are explicit and may cost proportional time.

## Failure modes

Putting a mutable data-class key into `HashMap` then changing an equality field can make lookup fail. Use immutable keys. Do not use `===` to decide whether two server responses are semantically identical; deserialization creates fresh instances.

## Production perspective

An offline cache keys records by immutable `UserId(value)`, so equivalent IDs match across deserialization. A ViewModel publishes immutable state; equality-based suppression is meaningful only when its `equals` contract describes the displayed data.

## Interview answer — short

`==` is null-safe structural equality through `equals`; `===` asks whether two references point to the same object. For domain values I normally use `==`. For arrays I use content comparison when I mean element equality.

## Interview answer — structured

Two separate data-class instances can compare equal with `==` because their primary-constructor values match, while `===` remains false. This distinction matters for map keys, deduplication, and state observation. I keep equality fields immutable. I use reference identity only when object ownership itself is the question, and I handle arrays explicitly with content comparison. For instance, two separately parsed `UserId("42")` values should match as domain keys even though they are different instances. A data class gives that value equality, while a regular class may use inherited identity equality unless I override it. I also call out arrays explicitly because ordinary `==` does not compare element contents. For hash-based collections I also require equal objects to have matching hash codes, and I avoid changing equality fields after insertion. Those are correctness constraints, not style preferences.

## Interview answer — deep senior

I would inspect the type’s equality contract before choosing an operator. A regular class inherits reference-based `equals` unless overridden; a data class generates value equality for primary-constructor properties. A mutable property participating in equality is risky for hash collections. `===` bypasses that semantic contract and can be appropriate for a specific singleton or cache identity check. On Android, equality in state streams can suppress updates, so mutable nested models and array properties need special care. I usually start by asking what the domain considers the same value. Kotlin's `==` calls `equals` safely around nulls, so it reflects that type's semantic equality. `===` compares reference identity and answers a different question: are these literally the same object instance? Equality affects hash maps, deduplication, and `StateFlow` emission suppression. Identity can be relevant for a cache or lifecycle object, but it is rarely a replacement for domain equality. I test both comparisons with separately created equal values, and I explicitly use content comparison for arrays. In a state stream, equality can suppress an emission, so a data model with a mutable nested object may fail to represent a new snapshot. I would publish immutable values and verify that the equality contract includes the fields the screen actually displays.

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

Technically reviewed against the linked primary documentation on 2026-10-11. Examples are illustrative JVM snippets; no Android device claim is made.
