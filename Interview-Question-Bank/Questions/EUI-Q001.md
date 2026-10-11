---
id: EUI-Q001
lesson_id: EXT-UI-01
topic: Frame pipeline
difficulty: foundational
style: conceptual
expected_minutes: 6
status: reviewed
---
# EUI-Q001 — Frame pipeline

## Interview question

> **Interviewer:** Trace a user input through state mutation, composition, measure, layout, draw, RenderThread, and GPU presentation. Where can a missed frame originate?

<p dir="rtl" lang="ar"><strong>السياق:</strong> custom component سريعة بصريًا لكن semantics مفقودة، أو state تضيع لما layout تتحول list-detail</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/EUI-Q001.md) · [Lesson](../../08-Mobile-System-Design/ext-ui-01.md)
