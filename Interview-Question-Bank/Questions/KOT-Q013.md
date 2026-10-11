---
id: KOT-Q013
lesson_id: KOT-003
topic: Secondary constructor delegation
difficulty: intermediate
style: code-review
expected_minutes: 3
status: reviewed
---
# KOT-Q013 — Can a secondary constructor skip validation?

A primary constructor has an init block that rejects blank names. A secondary constructor delegates to it and then logs an event. Can its body run before validation, or run when validation fails? When would a factory or default argument be clearer than a secondary constructor?

[Open complete model answer](../Model-Answers/KOT-Q013.md) · [Lesson](../../01-Kotlin-JVM-ART/kot-003-classes-constructors-initialization-order.md)
