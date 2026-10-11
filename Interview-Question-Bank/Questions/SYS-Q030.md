---
id: SYS-Q030
lesson_id: SYS-006
topic: Design verification
difficulty: senior
style: system-design
expected_minutes: 6
status: reviewed
---
# SYS-Q030 — Design verification

## Interview question

> **Interviewer:** Turn a mobile sync design into a verification plan with failure injection for process death, offline edits, duplicates, gaps, conflicts, and account switching.

<p dir="rtl" lang="ar"><strong>السياق:</strong> مرشح يرسم boxes من غير offline/auth/failure، أو يضيف lock حول network call فيعمل convoy.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/SYS-Q030.md) · [Lesson](../../08-Mobile-System-Design/sys-006-revision-design-review-and-concurrency.md)
