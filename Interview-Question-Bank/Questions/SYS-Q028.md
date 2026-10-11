---
id: SYS-Q028
lesson_id: SYS-006
topic: Concurrency boundary
difficulty: senior
style: debugging
expected_minutes: 5
status: reviewed
---
# SYS-Q028 — Concurrency boundary

## Interview question

> **Interviewer:** Two sends, a reconnect, and an account switch can happen together. Choose the serialized boundaries and operation identities that keep the chat state machine valid.

<p dir="rtl" lang="ar"><strong>السياق:</strong> مرشح يرسم boxes من غير offline/auth/failure، أو يضيف lock حول network call فيعمل convoy.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/SYS-Q028.md) · [Lesson](../../08-Mobile-System-Design/sys-006-revision-design-review-and-concurrency.md)
