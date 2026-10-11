---
id: CON-Q003
lesson_id: EXT-CON-01
topic: Mutex contract
difficulty: intermediate
style: debugging
expected_minutes: 6
status: reviewed
---
# CON-Q003 — Mutex contract

## Interview question

> **Interviewer:** A coroutine Mutex protects a map, but the critical section performs network I/O and calls user code. Review cancellation, reentrancy, latency, and the invariant that should actually be locked.

<p dir="rtl" lang="ar"><strong>السياق:</strong> counter read-modify-write تضيع updates، أو Mutex ماسكة أثناء network، أو atomic fields منفصلة تكسر invariant مشتركة</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/CON-Q003.md) · [Lesson](../../08-Mobile-System-Design/ext-con-01.md)
