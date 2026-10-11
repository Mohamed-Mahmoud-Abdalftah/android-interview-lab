---
id: KOT-Q020
lesson_id: KOT-004
topic: Inline functions and callback safety
difficulty: senior
style: code-review
expected_minutes: 4
status: reviewed
---
# KOT-Q020 — Should every callback wrapper be inline?

A review suggests adding inline to every higher-order function to “make callbacks fast and thread-safe.” Evaluate the claim. Discuss measurement, code size, non-local return rules, and why inlining does not provide lifecycle ownership or synchronization.

[Open complete model answer](../Model-Answers/KOT-Q020.md) · [Lesson](../../01-Kotlin-JVM-ART/kot-004-functions-lambdas-and-closures.md)
