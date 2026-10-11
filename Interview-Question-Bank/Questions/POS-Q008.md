---
id: POS-Q008
lesson_id: EXT-POS-01
topic: Terminal operation identity
difficulty: intermediate
style: debugging
expected_minutes: 6
status: reviewed
---
# POS-Q008 — Terminal operation identity

## Interview question

> **Interviewer:** Design a payment attempt ID that survives process death, duplicate callbacks, reconnects, and retries across app, terminal SDK, backend, and provider.

<p dir="rtl" lang="ar"><strong>السياق:</strong> network يقطع بعد authorization فيتعمل retry بعملية جديدة، أو SDK callback قديمة تكمل attempt مختلفة</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/POS-Q008.md) · [Lesson](../../10-Optional-POS-Specialist/ext-pos-01.md)
