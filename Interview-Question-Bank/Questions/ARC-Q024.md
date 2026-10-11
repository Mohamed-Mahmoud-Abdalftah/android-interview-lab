---
id: ARC-Q024
lesson_id: ARC-005
topic: ADR quality
difficulty: senior
style: architecture
expected_minutes: 5
status: reviewed
---
# ARC-Q024 — ADR quality

## Interview question

> **Interviewer:** Your team chose a single-activity architecture. What belongs in the ADR so a future team can understand and revisit the decision instead of treating it as permanent law?

<p dir="rtl" lang="ar"><strong>السياق:</strong> feature modules متشابكة bidirectional، وكل تعديل يبني التطبيق كله، والـADR تقول استخدمنا Clean Architecture من غير context أو بدائل.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/ARC-Q024.md) · [Lesson](../../04-Architecture-DI/arc-005-modules-contracts-and-adrs.md)
