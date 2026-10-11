---
id: SYS-Q029
lesson_id: SYS-006
topic: Alternative comparison
difficulty: senior
style: architecture
expected_minutes: 5
status: reviewed
---
# SYS-Q029 — Alternative comparison

## Interview question

> **Interviewer:** Compare polling, push-triggered fetch, and a persistent socket for a messaging inbox using latency, battery, infrastructure cost, reliability, and recovery.

<p dir="rtl" lang="ar"><strong>السياق:</strong> مرشح يرسم boxes من غير offline/auth/failure، أو يضيف lock حول network call فيعمل convoy.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/SYS-Q029.md) · [Lesson](../../08-Mobile-System-Design/sys-006-revision-design-review-and-concurrency.md)
