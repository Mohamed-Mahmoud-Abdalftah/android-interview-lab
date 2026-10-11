---
id: SYS-Q017
lesson_id: SYS-004
topic: Durable outbox
difficulty: intermediate
style: code-review
expected_minutes: 4
status: reviewed
---
# SYS-Q017 — Durable outbox

## Interview question

> **Interviewer:** A user edits a note offline. Show the database transaction that updates the local row and enqueues a mutation atomically, then trace retry, acknowledgement, and process death.

<p dir="rtl" lang="ar"><strong>السياق:</strong> network response قديمة تكتب فوق local edit، أو delete يختفي ويرجع بعد sync.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/SYS-Q017.md) · [Lesson](../../08-Mobile-System-Design/sys-004-offline-notes-sync-design.md)
