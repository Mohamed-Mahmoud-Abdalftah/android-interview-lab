---
id: EUI-Q008
lesson_id: EXT-UI-01
topic: Focus restoration
difficulty: senior
style: system-design
expected_minutes: 6
status: reviewed
---
# EUI-Q008 — Focus restoration

## Interview question

> **Interviewer:** A TV or keyboard-driven screen navigates away and back after the list changes. Design stable focus identity and restoration without pointing to a removed item.

<p dir="rtl" lang="ar"><strong>السياق:</strong> custom component سريعة بصريًا لكن semantics مفقودة، أو state تضيع لما layout تتحول list-detail</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/EUI-Q008.md) · [Lesson](../../08-Mobile-System-Design/ext-ui-01.md)
