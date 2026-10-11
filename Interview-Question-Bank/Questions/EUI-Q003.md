---
id: EUI-Q003
lesson_id: EXT-UI-01
topic: Stability contract
difficulty: intermediate
style: debugging
expected_minutes: 6
status: reviewed
---
# EUI-Q003 — Stability contract

## Interview question

> **Interviewer:** What does Compose stability allow the runtime to skip, and why does stable never mean immutable, thread-safe, or cheap to render?

<p dir="rtl" lang="ar"><strong>السياق:</strong> custom component سريعة بصريًا لكن semantics مفقودة، أو state تضيع لما layout تتحول list-detail</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/EUI-Q003.md) · [Lesson](../../08-Mobile-System-Design/ext-ui-01.md)
