---
id: ARC-Q022
lesson_id: ARC-005
topic: Dependency direction
difficulty: intermediate
style: code-review
expected_minutes: 4
status: reviewed
---
# ARC-Q022 — Dependency direction

## Interview question

> **Interviewer:** feature-checkout currently depends directly on feature-cart to reuse one mapper. Review the dependency direction and propose a boundary that avoids a feature-to-feature cycle without creating a generic commons dump.

<p dir="rtl" lang="ar"><strong>السياق:</strong> feature modules متشابكة bidirectional، وكل تعديل يبني التطبيق كله، والـADR تقول استخدمنا Clean Architecture من غير context أو بدائل.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/ARC-Q022.md) · [Lesson](../../04-Architecture-DI/arc-005-modules-contracts-and-adrs.md)
