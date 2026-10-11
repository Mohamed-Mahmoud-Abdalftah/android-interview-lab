---
id: PRO-Q027
lesson_id: PRO-006
topic: Staged rollout
difficulty: intermediate
style: code-review
expected_minutes: 4
status: reviewed
---
# PRO-Q027 — Staged rollout

## Interview question

> **Interviewer:** Design a staged rollout with cohort size, observation window, dashboards, owners, and automatic stop conditions. What bias appears if only early adopters receive the release?

<p dir="rtl" lang="ar"><strong>السياق:</strong> tests خضراء لكن migration path ناقصة أو security blocker مفتوحة، والفريق يكمل عشان deadline.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/PRO-Q027.md) · [Lesson](../../06-Production-Engineering/pro-006-revision-release-health-and-dsa.md)
