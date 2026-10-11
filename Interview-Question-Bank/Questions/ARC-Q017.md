---
id: ARC-Q017
lesson_id: ARC-004
topic: Qualifier design
difficulty: intermediate
style: code-review
expected_minutes: 4
status: reviewed
---
# ARC-Q017 — Qualifier design

## Interview question

> **Interviewer:** This module provides two Retrofit instances, but both are distinguished only by @Named strings copied across several files. Review the design. When would you introduce semantic qualifiers, and how would you prove the production binding is correct?

<p dir="rtl" lang="ar"><strong>السياق:</strong> Singleton ماسكة session/user object فتسرّب بيانات حساب قديم بعد logout، أو binding غلط توصل production endpoint في test.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/ARC-Q017.md) · [Lesson](../../04-Architecture-DI/arc-004-hilt-scopes-qualifiers-and-di-tests.md)
