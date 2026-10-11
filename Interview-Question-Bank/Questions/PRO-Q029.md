---
id: PRO-Q029
lesson_id: PRO-006
topic: Migration coverage
difficulty: senior
style: architecture
expected_minutes: 5
status: reviewed
---
# PRO-Q029 — Migration coverage

## Interview question

> **Interviewer:** Your Room database supports versions 4 through 9. Which migration paths must CI execute, what data assertions belong after opening version 9, and why is a clean install irrelevant?

<p dir="rtl" lang="ar"><strong>السياق:</strong> tests خضراء لكن migration path ناقصة أو security blocker مفتوحة، والفريق يكمل عشان deadline.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/PRO-Q029.md) · [Lesson](../../06-Production-Engineering/pro-006-revision-release-health-and-dsa.md)
