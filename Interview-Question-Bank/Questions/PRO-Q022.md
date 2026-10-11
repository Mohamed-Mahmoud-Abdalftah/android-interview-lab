---
id: PRO-Q022
lesson_id: PRO-005
topic: Startup modes
difficulty: intermediate
style: code-review
expected_minutes: 4
status: reviewed
---
# PRO-Q022 — Startup modes

## Interview question

> **Interviewer:** Compare cold, warm, and hot startup. Which process and Activity state exists in each, and why does mixing them make benchmark results meaningless?

<p dir="rtl" lang="ar"><strong>السياق:</strong> debug profile تقيلة اتاخدت مرة واتعممت على release، أو average startup خبت tail regression.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/PRO-Q022.md) · [Lesson](../../06-Production-Engineering/pro-005-profiling-startup-and-incident-evidence.md)
