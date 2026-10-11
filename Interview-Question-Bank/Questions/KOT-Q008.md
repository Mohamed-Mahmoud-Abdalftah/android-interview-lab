---
id: KOT-Q008
lesson_id: KOT-002
topic: Structural and referential equality
difficulty: intermediate
style: code-review
expected_minutes: 3
status: reviewed
---
# KOT-Q008 — Equality or same instance?

Predict the three comparisons and explain the rule behind each:

```kotlin
data class Candidate(val id: String)
val first = Candidate("7")
val second = Candidate("7")
val alias = first

first == second
first === second
first === alias
```

How does `==` behave if one operand is null? Why is `===` a poor substitute for a value comparison?

[Open complete model answer](../Model-Answers/KOT-Q008.md) · [Lesson](../../01-Kotlin-JVM-ART/kot-002-val-var-types-equality-and-identity.md)
