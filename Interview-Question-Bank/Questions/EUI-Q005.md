---
id: EUI-Q005
lesson_id: EXT-UI-01
topic: Lazy list identity
difficulty: senior
style: live-coding
expected_minutes: 6
status: reviewed
---
# EUI-Q005 — Lazy list identity

## Interview question

> **Interviewer:** A LazyColumn uses list indices as keys and items are inserted at the top. Explain the state and animation bugs, then choose stable keys and content types.

<p dir="rtl" lang="ar"><strong>السياق:</strong> custom component سريعة بصريًا لكن semantics مفقودة، أو state تضيع لما layout تتحول list-detail</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/EUI-Q005.md) · [Lesson](../../08-Mobile-System-Design/ext-ui-01.md)
