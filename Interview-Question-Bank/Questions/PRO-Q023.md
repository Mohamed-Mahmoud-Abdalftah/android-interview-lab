---
id: PRO-Q023
lesson_id: PRO-005
topic: Perfetto trace reading
difficulty: senior
style: debugging
expected_minutes: 5
status: reviewed
---
# PRO-Q023 — Perfetto trace reading

## Interview question

> **Interviewer:** A screen janks while loading. In a Perfetto trace, how do you distinguish main-thread CPU work, lock wait, Binder wait, I/O, GC, and GPU pressure before proposing a fix?

<p dir="rtl" lang="ar"><strong>السياق:</strong> debug profile تقيلة اتاخدت مرة واتعممت على release، أو average startup خبت tail regression.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/PRO-Q023.md) · [Lesson](../../06-Production-Engineering/pro-005-profiling-startup-and-incident-evidence.md)
