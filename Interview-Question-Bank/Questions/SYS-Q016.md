---
id: SYS-Q016
lesson_id: SYS-004
topic: Source of truth
difficulty: foundational
style: conceptual
expected_minutes: 4
status: reviewed
---
# SYS-Q016 — Source of truth

## Interview question

> **Interviewer:** Design an offline-first screen where Room is the observable source of truth and network refresh updates it. Trace loading, success, stale cache, and failure without creating two UI authorities.

<p dir="rtl" lang="ar"><strong>السياق:</strong> network response قديمة تكتب فوق local edit، أو delete يختفي ويرجع بعد sync.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/SYS-Q016.md) · [Lesson](../../08-Mobile-System-Design/sys-004-offline-notes-sync-design.md)
