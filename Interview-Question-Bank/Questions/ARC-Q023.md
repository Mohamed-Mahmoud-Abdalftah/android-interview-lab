---
id: ARC-Q023
lesson_id: ARC-005
topic: Public API control
difficulty: senior
style: debugging
expected_minutes: 5
status: reviewed
---
# ARC-Q023 — Public API control

## Interview question

> **Interviewer:** A library module exposes DAO entities, Retrofit DTOs, and implementation classes because making everything public was faster. What failures does this create for consumers, and how would you shrink the API safely?

<p dir="rtl" lang="ar"><strong>السياق:</strong> feature modules متشابكة bidirectional، وكل تعديل يبني التطبيق كله، والـADR تقول استخدمنا Clean Architecture من غير context أو بدائل.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/ARC-Q023.md) · [Lesson](../../04-Architecture-DI/arc-005-modules-contracts-and-adrs.md)
