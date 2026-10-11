---
id: EUI-Q002
lesson_id: EXT-UI-01
topic: Snapshot state
difficulty: intermediate
style: code-review
expected_minutes: 6
status: reviewed
---
# EUI-Q002 — Snapshot state

## Interview question

> **Interviewer:** Two coroutines update Compose snapshot state from different contexts. Explain snapshot consistency, mutation policy, and how conflicting writes become visible.

<p dir="rtl" lang="ar"><strong>السياق:</strong> custom component سريعة بصريًا لكن semantics مفقودة، أو state تضيع لما layout تتحول list-detail</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/EUI-Q002.md) · [Lesson](../../08-Mobile-System-Design/ext-ui-01.md)
