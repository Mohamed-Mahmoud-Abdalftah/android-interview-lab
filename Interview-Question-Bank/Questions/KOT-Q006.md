---
id: KOT-Q006
lesson_id: KOT-002
topic: val and var versus object mutability
difficulty: foundational
style: product-android
expected_minutes: 2
status: reviewed
---
# KOT-Q006 — Read-only binding, mutable object

Consider:

```kotlin
val labels = mutableListOf("Ada")
val alias = labels
labels.add("Mona")
```

What does `val` prevent here, what does `alias` observe, and how would changing `labels` to `var` alter the guarantees? Explain how you would expose this data if callers must not mutate it.

[Open complete model answer](../Model-Answers/KOT-Q006.md) · [Lesson](../../01-Kotlin-JVM-ART/kot-002-val-var-types-equality-and-identity.md)
