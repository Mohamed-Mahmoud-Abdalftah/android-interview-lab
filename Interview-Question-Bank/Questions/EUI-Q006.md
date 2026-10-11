---
id: EUI-Q006
lesson_id: EXT-UI-01
topic: Nested scroll
difficulty: senior
style: performance
expected_minutes: 6
status: reviewed
---
# EUI-Q006 — Nested scroll

## Interview question

> **Interviewer:** A collapsing toolbar and inner list both consume drag deltas. Trace pre-scroll, child consumption, and post-scroll, including fling ownership.

<p dir="rtl" lang="ar"><strong>السياق:</strong> custom component سريعة بصريًا لكن semantics مفقودة، أو state تضيع لما layout تتحول list-detail</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/EUI-Q006.md) · [Lesson](../../08-Mobile-System-Design/ext-ui-01.md)
