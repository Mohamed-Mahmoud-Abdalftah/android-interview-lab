---
id: CON-Q005
lesson_id: EXT-CON-01
topic: Confinement
difficulty: senior
style: live-coding
expected_minutes: 6
status: reviewed
---
# CON-Q005 — Confinement

## Interview question

> **Interviewer:** Design a serialized owner for mutable session state using one dispatcher, actor, or event loop. What operations are allowed across the boundary?

<p dir="rtl" lang="ar"><strong>السياق:</strong> counter read-modify-write تضيع updates، أو Mutex ماسكة أثناء network، أو atomic fields منفصلة تكسر invariant مشتركة</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/CON-Q005.md) · [Lesson](../../08-Mobile-System-Design/ext-con-01.md)
