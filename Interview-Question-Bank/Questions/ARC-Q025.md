---
id: ARC-Q025
lesson_id: ARC-005
topic: Build and ownership trade-offs
difficulty: senior
style: system-design
expected_minutes: 6
status: reviewed
---
# ARC-Q025 — Build and ownership trade-offs

## Interview question

> **Interviewer:** Two teams share a large core module. Changes trigger broad rebuilds and no one owns regressions. Propose an incremental split and define the measurements that would tell you whether it helped.

<p dir="rtl" lang="ar"><strong>السياق:</strong> feature modules متشابكة bidirectional، وكل تعديل يبني التطبيق كله، والـADR تقول استخدمنا Clean Architecture من غير context أو بدائل.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/ARC-Q025.md) · [Lesson](../../04-Architecture-DI/arc-005-modules-contracts-and-adrs.md)
