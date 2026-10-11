---
id: KOT-Q003
lesson_id: KOT-001
topic: Smart casts and mutable state
difficulty: intermediate
style: code-review
expected_minutes: 3
status: reviewed
---
# KOT-Q003 — Repeated property reads

Review `if (holder.name != null) println(holder.name.length)` when `name` is mutable. What is the concern, and what does a local snapshot solve?

[Open complete model answer](../Model-Answers/KOT-Q003.md) · [Lesson](../../01-Kotlin-JVM-ART/KOT-001-nullability-java-boundary.md)
