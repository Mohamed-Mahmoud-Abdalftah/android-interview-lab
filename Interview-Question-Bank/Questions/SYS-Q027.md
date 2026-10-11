---
id: SYS-Q027
lesson_id: SYS-006
topic: State ownership
difficulty: intermediate
style: code-review
expected_minutes: 4
status: reviewed
---
# SYS-Q027 — State ownership

## Interview question

> **Interviewer:** In a mobile system design interview, map draft text, message history, send status, unread count, and auth state to their authoritative owners and persistence levels.

<p dir="rtl" lang="ar"><strong>السياق:</strong> مرشح يرسم boxes من غير offline/auth/failure، أو يضيف lock حول network call فيعمل convoy.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/SYS-Q027.md) · [Lesson](../../08-Mobile-System-Design/sys-006-revision-design-review-and-concurrency.md)
