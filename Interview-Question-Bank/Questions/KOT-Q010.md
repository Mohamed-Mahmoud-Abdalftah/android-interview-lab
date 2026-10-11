---
id: KOT-Q010
lesson_id: KOT-002
topic: Aliasing at a Java collection boundary
difficulty: senior
style: architecture
expected_minutes: 4
status: reviewed
---
# KOT-Q010 — A Java list exposed as Kotlin List

A Java SDK returns a live, mutable `java.util.List<String>` and may change it later. Kotlin stores that object in a `val` and exposes it to callers through a `List<String>` property. Assume the SDK returned a non-null list.

What do `val` and Kotlin's read-only `List` interface guarantee, and what can still change? Design a boundary that provides a stable snapshot. State one limit of a shallow copy and one concurrency concern.

[Open complete model answer](../Model-Answers/KOT-Q010.md) · [Lesson](../../01-Kotlin-JVM-ART/kot-002-val-var-types-equality-and-identity.md)
