---
id: ARC-Q021
lesson_id: ARC-005
topic: Module boundary
difficulty: foundational
style: conceptual
expected_minutes: 4
status: reviewed
---
# ARC-Q021 — Module boundary

## Interview question

> **Interviewer:** A team wants a Gradle module for every screen. Decide where module boundaries should actually go using ownership, change frequency, public API size, and build cost.

<p dir="rtl" lang="ar"><strong>السياق:</strong> feature modules متشابكة bidirectional، وكل تعديل يبني التطبيق كله، والـADR تقول استخدمنا Clean Architecture من غير context أو بدائل.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/ARC-Q021.md) · [Lesson](../../04-Architecture-DI/arc-005-modules-contracts-and-adrs.md)
