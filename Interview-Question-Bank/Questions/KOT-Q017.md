---
id: KOT-Q017
lesson_id: KOT-004
topic: Closure capture and snapshot
difficulty: intermediate
style: code-review
expected_minutes: 3
status: reviewed
---
# KOT-Q017 — Which ID does the lambda read?

Trace fixed and live after current changes from "old" to "new": val snapshot = current; val fixed = { snapshot }; val live = { current }. Which callback should a reload-current-profile button use, and when would fixed be correct?

[Open complete model answer](../Model-Answers/KOT-Q017.md) · [Lesson](../../01-Kotlin-JVM-ART/kot-004-functions-lambdas-and-closures.md)
