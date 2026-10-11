---
id: KOT-Q014
lesson_id: KOT-003
topic: Open dispatch during initialization
difficulty: senior
style: debugging
expected_minutes: 4
status: reviewed
---
# KOT-Q014 — Derived state read too early

A base-class init block calls an open method. The derived override reads a property initialized in the derived class body. Explain the construction-order hazard, evidence to collect, and a safe redesign. Do not assume a universal exception type across targets or compiler versions.

[Open complete model answer](../Model-Answers/KOT-Q014.md) · [Lesson](../../01-Kotlin-JVM-ART/kot-003-classes-constructors-initialization-order.md)
