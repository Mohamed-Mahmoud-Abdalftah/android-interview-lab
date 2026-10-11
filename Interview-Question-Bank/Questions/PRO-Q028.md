---
id: PRO-Q028
lesson_id: PRO-006
topic: Rollback criteria
difficulty: senior
style: debugging
expected_minutes: 5
status: reviewed
---
# PRO-Q028 — Rollback criteria

## Interview question

> **Interviewer:** A release improves startup but increases checkout failures by 0.3%. Set rollback criteria before launch and explain who has authority to trigger them during an incident.

<p dir="rtl" lang="ar"><strong>السياق:</strong> tests خضراء لكن migration path ناقصة أو security blocker مفتوحة، والفريق يكمل عشان deadline.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/PRO-Q028.md) · [Lesson](../../06-Production-Engineering/pro-006-revision-release-health-and-dsa.md)
