---
id: KOT-Q018
lesson_id: KOT-004
topic: Deferred callback timing and failure
difficulty: intermediate
style: debugging
expected_minutes: 4
status: reviewed
---
# KOT-Q018 — A reload button sends a stale profile

A callback captures the selected ID while a screen is created; the user selects another profile before tapping reload. Diagnose the stale request, propose a callback boundary, and state what a Boolean return from the local delegate can and cannot prove.

[Open complete model answer](../Model-Answers/KOT-Q018.md) · [Lesson](../../01-Kotlin-JVM-ART/kot-004-functions-lambdas-and-closures.md)
