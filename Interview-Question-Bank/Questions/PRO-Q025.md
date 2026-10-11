---
id: PRO-Q025
lesson_id: PRO-005
topic: Incident rollout
difficulty: senior
style: system-design
expected_minutes: 6
status: reviewed
---
# PRO-Q025 — Incident rollout

## Interview question

> **Interviewer:** Crash rate rises only in one device cohort during a 10% rollout. Decide whether to pause, roll back, or continue, and list the evidence you need before expanding exposure.

<p dir="rtl" lang="ar"><strong>السياق:</strong> debug profile تقيلة اتاخدت مرة واتعممت على release، أو average startup خبت tail regression.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/PRO-Q025.md) · [Lesson](../../06-Production-Engineering/pro-005-profiling-startup-and-incident-evidence.md)
