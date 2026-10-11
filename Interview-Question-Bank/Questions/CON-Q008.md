---
id: CON-Q008
lesson_id: EXT-CON-01
topic: Backpressure
difficulty: senior
style: system-design
expected_minutes: 6
status: reviewed
---
# CON-Q008 — Backpressure

## Interview question

> **Interviewer:** A producer emits 10,000 updates per second and the UI can render 60. Choose between buffering, conflation, dropping, batching, and slowing the producer based on value semantics.

<p dir="rtl" lang="ar"><strong>السياق:</strong> counter read-modify-write تضيع updates، أو Mutex ماسكة أثناء network، أو atomic fields منفصلة تكسر invariant مشتركة</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/CON-Q008.md) · [Lesson](../../08-Mobile-System-Design/ext-con-01.md)
