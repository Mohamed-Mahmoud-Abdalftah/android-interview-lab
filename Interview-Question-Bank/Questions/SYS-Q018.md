---
id: SYS-Q018
lesson_id: SYS-004
topic: Conflict policy
difficulty: senior
style: debugging
expected_minutes: 5
status: reviewed
---
# SYS-Q018 — Conflict policy

## Interview question

> **Interviewer:** Two devices edit the same record offline. Compare last-write-wins, field merge, version rejection, and user-assisted resolution using a concrete product requirement.

<p dir="rtl" lang="ar"><strong>السياق:</strong> network response قديمة تكتب فوق local edit، أو delete يختفي ويرجع بعد sync.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/SYS-Q018.md) · [Lesson](../../08-Mobile-System-Design/sys-004-offline-notes-sync-design.md)
