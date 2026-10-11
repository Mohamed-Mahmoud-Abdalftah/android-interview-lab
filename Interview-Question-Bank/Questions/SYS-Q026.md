---
id: SYS-Q026
lesson_id: SYS-006
topic: Requirement discovery
difficulty: foundational
style: conceptual
expected_minutes: 4
status: reviewed
---
# SYS-Q026 — Requirement discovery

## Interview question

> **Interviewer:** Before designing chat sync, ask the questions that determine ordering, delivery guarantees, offline behavior, history size, latency, privacy, and multi-device consistency.

<p dir="rtl" lang="ar"><strong>السياق:</strong> مرشح يرسم boxes من غير offline/auth/failure، أو يضيف lock حول network call فيعمل convoy.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/SYS-Q026.md) · [Lesson](../../08-Mobile-System-Design/sys-006-revision-design-review-and-concurrency.md)
