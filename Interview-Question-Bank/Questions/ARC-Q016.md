---
id: ARC-Q016
lesson_id: ARC-004
topic: Hilt component lifetimes
difficulty: foundational
style: conceptual
expected_minutes: 4
status: reviewed
---
# ARC-Q016 — Hilt component lifetimes

## Interview question

> **Interviewer:** A repository is scoped to SingletonComponent and caches the signed-in user. The user logs out and signs in with another account without the process dying. Explain the bug, choose the correct owner for account state, and describe what Hilt does and does not reset.

<p dir="rtl" lang="ar"><strong>السياق:</strong> Singleton ماسكة session/user object فتسرّب بيانات حساب قديم بعد logout، أو binding غلط توصل production endpoint في test.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/ARC-Q016.md) · [Lesson](../../04-Architecture-DI/arc-004-hilt-scopes-qualifiers-and-di-tests.md)
