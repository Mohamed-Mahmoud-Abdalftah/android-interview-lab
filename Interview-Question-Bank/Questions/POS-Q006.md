---
id: POS-Q006
lesson_id: EXT-POS-01
topic: Reversal boundary
difficulty: foundational
style: conceptual
expected_minutes: 6
status: reviewed
---
# POS-Q006 — Reversal boundary

## Interview question

> **Interviewer:** A terminal approves a payment but the host response is lost. Explain when reversal is valid, who authorizes it, and why starting a new sale is dangerous.

<p dir="rtl" lang="ar"><strong>السياق:</strong> network يقطع بعد authorization فيتعمل retry بعملية جديدة، أو SDK callback قديمة تكمل attempt مختلفة</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/POS-Q006.md) · [Lesson](../../10-Optional-POS-Specialist/ext-pos-01.md)
