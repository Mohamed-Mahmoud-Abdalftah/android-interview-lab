---
id: PRO-Q024
lesson_id: PRO-005
topic: Memory evidence
difficulty: senior
style: architecture
expected_minutes: 5
status: reviewed
---
# PRO-Q024 — Memory evidence

## Interview question

> **Interviewer:** Memory grows after opening and closing a screen ten times. Design an investigation that separates a retained Activity from allocation churn, bitmap or native memory, and normal heap growth.

<p dir="rtl" lang="ar"><strong>السياق:</strong> debug profile تقيلة اتاخدت مرة واتعممت على release، أو average startup خبت tail regression.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/PRO-Q024.md) · [Lesson](../../06-Production-Engineering/pro-005-profiling-startup-and-incident-evidence.md)
