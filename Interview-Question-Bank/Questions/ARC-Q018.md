---
id: ARC-Q018
lesson_id: ARC-004
topic: Accidental singleton session
difficulty: senior
style: debugging
expected_minutes: 5
status: reviewed
---
# ARC-Q018 — Accidental singleton session

## Interview question

> **Interviewer:** After logout, one screen briefly renders data from the previous account. The cache is held by a @Singleton repository. Trace the lifetime mismatch and redesign the session boundary without restarting the process.

<p dir="rtl" lang="ar"><strong>السياق:</strong> Singleton ماسكة session/user object فتسرّب بيانات حساب قديم بعد logout، أو binding غلط توصل production endpoint في test.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/ARC-Q018.md) · [Lesson](../../04-Architecture-DI/arc-004-hilt-scopes-qualifiers-and-di-tests.md)
