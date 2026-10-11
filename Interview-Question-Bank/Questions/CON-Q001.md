---
id: CON-Q001
lesson_id: EXT-CON-01
topic: Race definition
difficulty: foundational
style: conceptual
expected_minutes: 6
status: reviewed
---
# CON-Q001 — Race definition

## Interview question

> **Interviewer:** Two coroutines increment a shared counter using read-modify-write. Write a harmful interleaving and distinguish a race condition from a merely nondeterministic execution order.

<p dir="rtl" lang="ar"><strong>السياق:</strong> counter read-modify-write تضيع updates، أو Mutex ماسكة أثناء network، أو atomic fields منفصلة تكسر invariant مشتركة</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/CON-Q001.md) · [Lesson](../../08-Mobile-System-Design/ext-con-01.md)
