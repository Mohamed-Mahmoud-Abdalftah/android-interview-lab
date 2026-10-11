---
id: PRO-Q026
lesson_id: PRO-006
topic: Release gate
difficulty: foundational
style: conceptual
expected_minutes: 4
status: reviewed
---
# PRO-Q026 — Release gate

## Interview question

> **Interviewer:** Define hard release gates for crash, ANR, data loss, security, and migration risk. Why should one healthy aggregate metric never cancel a blocking signal?

<p dir="rtl" lang="ar"><strong>السياق:</strong> tests خضراء لكن migration path ناقصة أو security blocker مفتوحة، والفريق يكمل عشان deadline.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/PRO-Q026.md) · [Lesson](../../06-Production-Engineering/pro-006-revision-release-health-and-dsa.md)
