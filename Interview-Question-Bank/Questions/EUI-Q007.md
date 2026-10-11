---
id: EUI-Q007
lesson_id: EXT-UI-01
topic: Semantics merging
difficulty: senior
style: debugging
expected_minutes: 6
status: reviewed
---
# EUI-Q007 — Semantics merging

## Interview question

> **Interviewer:** A clickable card contains an icon, title, and status. Decide whether to merge descendants and show how the choice changes TalkBack output and test selectors.

<p dir="rtl" lang="ar"><strong>السياق:</strong> custom component سريعة بصريًا لكن semantics مفقودة، أو state تضيع لما layout تتحول list-detail</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/EUI-Q007.md) · [Lesson](../../08-Mobile-System-Design/ext-ui-01.md)
