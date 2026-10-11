---
id: INT-Q017
lesson_id: INT-003
topic: Trust boundaries
difficulty: intermediate
style: code-review
expected_minutes: 4
status: reviewed
---
# INT-Q017 — Trust boundaries

## Interview question

> **Interviewer:** Threat-model a mobile payment flow across app, OS intent, terminal SDK, backend, and provider. What input is untrusted at each boundary?

<p dir="rtl" lang="ar"><strong>السياق:</strong> الفريق يسرّع startup بإزالة auth check، أو يشفر token بمفتاح ثابت داخل APK.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/INT-Q017.md) · [Lesson](../../09-Leadership-English/int-003-performance-and-security-review.md)
