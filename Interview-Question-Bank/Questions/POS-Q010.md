---
id: POS-Q010
lesson_id: EXT-POS-01
topic: PCI-safe diagnostics
difficulty: senior
style: live-coding
expected_minutes: 6
status: reviewed
---
# POS-Q010 — PCI-safe diagnostics

## Interview question

> **Interviewer:** Support needs enough logs to investigate terminal failures. Define what may be logged, what must be masked or excluded, access controls, retention, and correlation IDs.

<p dir="rtl" lang="ar"><strong>السياق:</strong> network يقطع بعد authorization فيتعمل retry بعملية جديدة، أو SDK callback قديمة تكمل attempt مختلفة</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/POS-Q010.md) · [Lesson](../../10-Optional-POS-Specialist/ext-pos-01.md)
