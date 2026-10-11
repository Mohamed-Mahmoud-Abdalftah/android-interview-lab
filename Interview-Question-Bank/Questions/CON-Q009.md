---
id: CON-Q009
lesson_id: EXT-CON-01
topic: Stress testing
difficulty: senior
style: live-coding
expected_minutes: 6
status: reviewed
---
# CON-Q009 — Stress testing

## Interview question

> **Interviewer:** Why can a concurrency stress test pass while a race still exists? Design controlled interleavings and explain what stress adds beyond them.

<p dir="rtl" lang="ar"><strong>السياق:</strong> counter read-modify-write تضيع updates، أو Mutex ماسكة أثناء network، أو atomic fields منفصلة تكسر invariant مشتركة</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/CON-Q009.md) · [Lesson](../../08-Mobile-System-Design/ext-con-01.md)
