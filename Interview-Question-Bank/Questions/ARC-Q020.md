---
id: ARC-Q020
lesson_id: ARC-004
topic: Service locator trade-off
difficulty: senior
style: system-design
expected_minutes: 6
status: reviewed
---
# ARC-Q020 — Service locator trade-off

## Interview question

> **Interviewer:** A legacy app obtains dependencies from a global object in every screen. You cannot rewrite the app at once. How would you migrate toward constructor injection while keeping releases safe, and where is a small service locator still defensible?

<p dir="rtl" lang="ar"><strong>السياق:</strong> Singleton ماسكة session/user object فتسرّب بيانات حساب قديم بعد logout، أو binding غلط توصل production endpoint في test.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/ARC-Q020.md) · [Lesson](../../04-Architecture-DI/arc-004-hilt-scopes-qualifiers-and-di-tests.md)
