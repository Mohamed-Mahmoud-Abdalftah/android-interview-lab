---
id: SYS-Q020
lesson_id: SYS-004
topic: Sync observability
difficulty: senior
style: system-design
expected_minutes: 6
status: reviewed
---
# SYS-Q020 — Sync observability

## Interview question

> **Interviewer:** Define metrics and logs for an offline sync engine: queue age, attempts, conflicts, freshness, terminal failures, and redaction. Which signal pages an on-call engineer?

<p dir="rtl" lang="ar"><strong>السياق:</strong> network response قديمة تكتب فوق local edit، أو delete يختفي ويرجع بعد sync.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/SYS-Q020.md) · [Lesson](../../08-Mobile-System-Design/sys-004-offline-notes-sync-design.md)
