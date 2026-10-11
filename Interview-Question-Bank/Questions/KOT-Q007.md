---
id: KOT-Q007
lesson_id: KOT-002
topic: Type inference and collection API boundaries
difficulty: foundational
style: code-review
expected_minutes: 3
status: reviewed
---
# KOT-Q007 — Inferred type versus declared view

Review this code:

```kotlin
val inferred = mutableListOf("Ada")
val view: List<String> = inferred
```

What are the static types of `inferred` and `view`? Which of `inferred.add("Mona")` and `view.add("Mona")` compiles? Does `view` provide a snapshot, and when would you declare an explicit type at an API boundary?

[Open complete model answer](../Model-Answers/KOT-Q007.md) · [Lesson](../../01-Kotlin-JVM-ART/kot-002-val-var-types-equality-and-identity.md)
