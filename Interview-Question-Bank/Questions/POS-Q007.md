---
id: POS-Q007
lesson_id: EXT-POS-01
topic: Settlement and reconciliation
difficulty: intermediate
style: code-review
expected_minutes: 6
status: reviewed
---
# POS-Q007 — Settlement and reconciliation

## Interview question

> **Interviewer:** Differentiate authorization, capture, settlement, reversal, and refund. Which identifiers let operations reconcile terminal and provider records?

<p dir="rtl" lang="ar"><strong>السياق:</strong> network يقطع بعد authorization فيتعمل retry بعملية جديدة، أو SDK callback قديمة تكمل attempt مختلفة</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/POS-Q007.md) · [Lesson](../../10-Optional-POS-Specialist/ext-pos-01.md)
