---
id: POS-Q009
lesson_id: EXT-POS-01
topic: Hardware disconnect
difficulty: senior
style: architecture
expected_minutes: 6
status: reviewed
---
# POS-Q009 — Hardware disconnect

## Interview question

> **Interviewer:** The card reader disconnects after card read but before the app sees the outcome. Model the state, user message, reconnection, and reconciliation flow.

<p dir="rtl" lang="ar"><strong>السياق:</strong> network يقطع بعد authorization فيتعمل retry بعملية جديدة، أو SDK callback قديمة تكمل attempt مختلفة</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/POS-Q009.md) · [Lesson](../../10-Optional-POS-Specialist/ext-pos-01.md)
