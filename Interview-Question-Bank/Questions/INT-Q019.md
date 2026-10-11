---
id: INT-Q019
lesson_id: INT-003
topic: Security regression tests
difficulty: senior
style: architecture
expected_minutes: 5
status: reviewed
---
# INT-Q019 — Security regression tests

## Interview question

> **Interviewer:** After fixing an exported-component vulnerability, design regression tests for hostile intents, authorization, replay, oversized input, and logging redaction.

<p dir="rtl" lang="ar"><strong>السياق:</strong> الفريق يسرّع startup بإزالة auth check، أو يشفر token بمفتاح ثابت داخل APK.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/INT-Q019.md) · [Lesson](../../09-Leadership-English/int-003-performance-and-security-review.md)
