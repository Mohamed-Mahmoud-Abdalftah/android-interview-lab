---
id: KOT-Q015
lesson_id: KOT-003
topic: Construction invariants and factories
difficulty: senior
style: architecture
expected_minutes: 4
status: reviewed
---
# KOT-Q015 — Parse or throw?

An untrusted config record may have a blank host or port outside 1..65535. Compare init validation, a private constructor plus nullable parsing factory, and a typed result. How would you keep the invariant intact when a serializer or generated copy enters the design?

[Open complete model answer](../Model-Answers/KOT-Q015.md) · [Lesson](../../01-Kotlin-JVM-ART/kot-003-classes-constructors-initialization-order.md)
