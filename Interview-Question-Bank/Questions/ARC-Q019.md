---
id: ARC-Q019
lesson_id: ARC-004
topic: DI replacement tests
difficulty: senior
style: architecture
expected_minutes: 5
status: reviewed
---
# ARC-Q019 — DI replacement tests

## Interview question

> **Interviewer:** You need an integration test that replaces the real payments gateway while keeping the production database graph. Show the Hilt test replacement you would use, the scope it must preserve, and what the test still cannot prove.

<p dir="rtl" lang="ar"><strong>السياق:</strong> Singleton ماسكة session/user object فتسرّب بيانات حساب قديم بعد logout، أو binding غلط توصل production endpoint في test.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/ARC-Q019.md) · [Lesson](../../04-Architecture-DI/arc-004-hilt-scopes-qualifiers-and-di-tests.md)
