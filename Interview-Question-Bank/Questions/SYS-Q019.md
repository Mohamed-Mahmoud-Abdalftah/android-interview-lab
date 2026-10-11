---
id: SYS-Q019
lesson_id: SYS-004
topic: Deletion tombstones
difficulty: senior
style: architecture
expected_minutes: 5
status: reviewed
---
# SYS-Q019 — Deletion tombstones

## Interview question

> **Interviewer:** Why can deleting a row locally cause it to reappear after sync? Design tombstone identity, retention, acknowledgement, and compaction.

<p dir="rtl" lang="ar"><strong>السياق:</strong> network response قديمة تكتب فوق local edit، أو delete يختفي ويرجع بعد sync.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/SYS-Q019.md) · [Lesson](../../08-Mobile-System-Design/sys-004-offline-notes-sync-design.md)
