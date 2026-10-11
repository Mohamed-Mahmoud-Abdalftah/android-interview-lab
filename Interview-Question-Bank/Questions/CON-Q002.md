---
id: CON-Q002
lesson_id: EXT-CON-01
topic: Atomicity versus visibility
difficulty: intermediate
style: code-review
expected_minutes: 6
status: reviewed
---
# CON-Q002 — Atomicity versus visibility

## Interview question

> **Interviewer:** A field is @Volatile and multiple threads execute balance = balance - amount. Explain why visibility is not atomicity and show a safe state transition.

<p dir="rtl" lang="ar"><strong>السياق:</strong> counter read-modify-write تضيع updates، أو Mutex ماسكة أثناء network، أو atomic fields منفصلة تكسر invariant مشتركة</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/CON-Q002.md) · [Lesson](../../08-Mobile-System-Design/ext-con-01.md)
