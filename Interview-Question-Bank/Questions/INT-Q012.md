---
id: INT-Q012
lesson_id: INT-002
topic: Mitigation before certainty
difficulty: intermediate
style: code-review
expected_minutes: 4
status: reviewed
---
# INT-Q012 — Mitigation before certainty

## Interview question

> **Interviewer:** Users are losing work but the root cause is unclear. Choose a reversible mitigation now, preserve evidence, and explain which actions must wait for stronger confidence.

<p dir="rtl" lang="ar"><strong>السياق:</strong> الفريق يقضي ساعات في root cause بينما crash rate بتزيد وعنده rollback آمن.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/INT-Q012.md) · [Lesson](../../09-Leadership-English/int-002-production-incident-response.md)
