---
id: INT-Q020
lesson_id: INT-003
topic: Trade-off communication
difficulty: senior
style: system-design
expected_minutes: 6
status: reviewed
---
# INT-Q020 — Trade-off communication

## Interview question

> **Interviewer:** Give a 90-second recommendation between two architectures: state the invariant, constraints, chosen option, cost, rejected alternative, and revisit signal.

<p dir="rtl" lang="ar"><strong>السياق:</strong> الفريق يسرّع startup بإزالة auth check، أو يشفر token بمفتاح ثابت داخل APK.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/INT-Q020.md) · [Lesson](../../09-Leadership-English/int-003-performance-and-security-review.md)
