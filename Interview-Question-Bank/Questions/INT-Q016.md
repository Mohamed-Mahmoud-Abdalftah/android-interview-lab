---
id: INT-Q016
lesson_id: INT-003
topic: Risk prioritization
difficulty: foundational
style: conceptual
expected_minutes: 4
status: reviewed
---
# INT-Q016 — Risk prioritization

## Interview question

> **Interviewer:** Rank a possible auth bypass, a reproducible data loss, a 200ms startup regression, and a cosmetic RTL bug. State the evidence and product context that could change the order.

<p dir="rtl" lang="ar"><strong>السياق:</strong> الفريق يسرّع startup بإزالة auth check، أو يشفر token بمفتاح ثابت داخل APK.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/INT-Q016.md) · [Lesson](../../09-Leadership-English/int-003-performance-and-security-review.md)
